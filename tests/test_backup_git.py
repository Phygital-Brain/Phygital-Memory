"""GitHub backup with every place, offline: a local stand-in plays GitHub (git's insteadOf points github.com at a
folder of bare repos), so nothing leaves this Mac. Checks: git's own files stay outside the memory, the backup goes up
after changes, an older memory's .git moves out, the backup follows a move into a cloud folder and up into a
cloud-only memory, a second Mac restores from it, and a clash keeps both versions.

Run: uv run python test_backup_git.py
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-gitbackup-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"   # never touch the real GitHub account
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
os.environ["PHYGITAL_MEMORY_TRASH"] = str(tmp / "Trash")
os.environ["PHYGITAL_MEMORY_CLOUD_KEYCHAIN"] = "Phygital Memory cloud TEST"
(tmp / "Trash").mkdir()
remotes = tmp / "github"
remotes.mkdir()
# every https://github.com/OWNER/REPO.git goes to the folder of bare repos instead
os.environ.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0=f"url.file://{remotes}/.insteadOf",
                  GIT_CONFIG_VALUE_0="https://github.com/")

from phygital_memory import cloud, folders as F, gitsync   # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def make_repo(self):
    full = f"me/{self.repo}"
    (remotes / "me").mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remotes / f"{full}.git")], check=True)
    return full


def remote_files(full):
    r = subprocess.run(["git", "--git-dir", str(remotes / f"{full}.git"), "ls-tree", "-r", "--name-only", "main"],
                       capture_output=True, text=True)
    return r.stdout.split()


patches = [mock.patch.object(gitsync, "is_private", lambda repo: True),
           mock.patch.object(gitsync, "signed_in", lambda: "me"),
           mock.patch.object(gitsync, "_exists", lambda repo: (remotes / f"{repo}.git").exists()),
           mock.patch.object(gitsync.GitSync, "same_memory", lambda self, repo: False),
           mock.patch.object(gitsync.GitSync, "_make_repo", make_repo),
           mock.patch.object(gitsync, "PUSH_AFTER", 0.5)]
for p in patches:
    p.start()

mac = tmp / "Mac"
mac.mkdir()
fs = F.Folders(None)
f = fs.get(fs.create(str(mac), "Work", "password-1")["id"])
f.memory.unlock("password-1")
f.memory.save("Plan.md", "# Plan\nfirst\n", new=True)

info = fs.to_github(f.id)
full = info["github"]
check(full == "me/Work-Phygital-Memory", "a backup repo is made", info)
check(not (f.path / ".git").exists() and (f.gitdir / "HEAD").exists(), "git's own files are outside the memory")
check("vault.cryptomator" in remote_files(full) and any(n.endswith(".c9r") for n in remote_files(full)),
      "the encrypted files are on GitHub")
check(not any("Plan" in n for n in remote_files(full)), "no readable note names on GitHub")

before = len(remote_files(full))
f.memory.save("Second.md", "# Second\n", new=True)
end = time.time() + 30
while time.time() < end and len(remote_files(full)) <= before:
    time.sleep(0.5)
check(len(remote_files(full)) > before, "a change goes up by itself a few seconds later")

# an older memory with .git inside: it moves out on the next start
legacy = tmp / "Mac" / "Old"
F.Memory.create(legacy, "password-2")
g = gitsync.GitSync(legacy, "Old-Phygital-Memory")
g.create()
check((legacy / ".git").is_dir(), "an older-style backup has .git inside")
fs2 = F.Folders(None)
old = fs2._add(legacy, "Old")
old.github = "me/Old-Phygital-Memory"
fs2._save()
f.sync and f.sync.stop()
fs3 = F.Folders(None)
o = fs3.get(old.id)
check(not (legacy / ".git").exists() and (o.gitdir / "HEAD").exists() and o.sync, "on start it moves out and keeps backing up")
o.sync.stop()

# a move into a cloud app's folder keeps the backup
fs = F.Folders(None)
f = fs.get(f.id)
cloudapp = tmp / "Dropbox"
cloudapp.mkdir()
moved = fs.relocate(f.id, str(cloudapp))
f = fs.get(f.id)
check(f.github == full and f.sync and not (f.path / ".git").exists(), "moved into a cloud folder, the backup stays on", moved)
f.memory.unlock("password-1")
f.memory.save("Third.md", "# Third\n", new=True)
before = len(remote_files(full))
end = time.time() + 30
while time.time() < end and len(remote_files(full)) <= before:
    time.sleep(0.5)
check(len(remote_files(full)) > before, "and keeps sending changes from there")
f.lock()

# the same Mac already has it: retrieving it again is refused, so two copies never fight over one backup
try:
    fs.from_github(full, tmp / "Mac2")
    check(False, "retrieving a memory that's already here is refused")
except ValueError as e:
    check("already here" in str(e) and not (tmp / "Mac2" / "Work").exists(), "retrieving a memory that's already here is refused", e)
# a second Mac (this one, without the memory) restores from the backup
del fs.items[f.id]
restored = fs.from_github(full, tmp / "Mac2")
r = fs.get(restored["id"])
check(not (r.path / ".git").exists() and (r.gitdir / "HEAD").exists(), "a restore keeps git's files outside too")
r.memory.unlock("password-1")
check(r.memory.read("Third.md").startswith("# Third"), "and has every note")
r.memory.lock()
r.sync.stop()
fs.items.pop(r.id)
fs.items[f.id] = f
f2 = fs.get(f.id)
fs.items[f.id].github = None   # a copy with no backup of its own: still the same memory
try:
    fs.from_github(full, tmp / "Mac4")
    check(False, "the same memory under no backup is caught too")
except ValueError as e:
    check("same memory" in str(e) and not (tmp / "Mac4" / "Work").exists(), "the same memory under no backup is caught too", e)
fs.items[f.id].github = full

# up into a cloud-only memory: it backs up while unlocked
store = tmp / "webdav"
store.mkdir()
server = subprocess.Popen(["rclone", "serve", "webdav", str(store), "--addr", "127.0.0.1:8797", "--user", "ana",
                           "--pass", "cloud-pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
conn = cloud.make_conn("webdav", "http://127.0.0.1:8797", "ana")
try:
    cloud.connect(conn, "cloud-pass")
    fs.to_cloud(f.id, conn, "")
    f = fs.get(f.id)
    check(f.cloud_at and f.github == full and not f.sync, "moved to cloud only, the backup is kept (it runs while unlocked)")
    f.ready()
    f.memory.unlock("password-1")
    check(f.sync is not None, "unlocked: the backup runs")
    f.memory.save("Fourth.md", "# Fourth\n", new=True)
    before = len(remote_files(full))
    end = time.time() + 40
    while time.time() < end and len(remote_files(full)) <= before:
        time.sleep(0.5)
    check(len(remote_files(full)) > before, "a change in the cloud-only memory goes to GitHub")
    check(not (store / f.path.name / ".git").exists() and not any(p.name == ".git" for p in store.rglob(".git")),
          "nothing of git's own goes into the cloud")
    f.lock()
    check(f.sync is None, "locked: the backup stops with it")
finally:
    server.terminate()
    cloud.forget_password(conn)

# stop: git's files go to the Trash, the notes stay
fs.stop_github(f.id)
check(not fs.get(f.id).github and not f.gitdir.exists() and any(".git (GitHub backup" in p.name for p in (tmp / "Trash").iterdir()),
      "stopping puts the backup's git files in the Trash")

for p in patches:
    p.stop()
print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
