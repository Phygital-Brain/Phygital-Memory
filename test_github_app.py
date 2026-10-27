"""The GitHub option inside the app's folder list: keep a folder in GitHub, changes go up by themselves, syncing
comes back after a restart, and another Mac opens it from GitHub.

Reuses the private test repo (PM_TEST_REPO, default phygital-memory-sync-test) instead of making a new one.
Run: uv run python test_github_app.py
"""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-ghapp-"))
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
from phygital_memory import folders as F, gitsync   # noqa: E402  (reads the state place above when loaded)
from phygital_memory.gitsync import GitSync          # noqa: E402
from phygital_memory.memory import Memory            # noqa: E402

PW = "test-ghapp-pass"
REPO = f"{gitsync.signed_in()}/{os.environ.get('PM_TEST_REPO', 'phygital-memory-sync-test')}"
BRANCH = "app-" + time.strftime("%Y%m%d-%H%M%S")
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def use_test_repo(self):   # instead of making a new repo: the test repo, on a fresh branch
    self.repo = self.state["repo"] = REPO
    self.prepare(self.folder.name)
    self.git("init", "-b", self.branch)
    self.git("remote", "add", "origin", f"https://github.com/{REPO}.git")
    self.sync_once()
    return REPO


class TestSync(GitSync):   # the app's GitSync, on the test branch
    def __init__(self, folder, repo, branch="main", watch=None):
        super().__init__(folder, repo, BRANCH, watch)

    create = use_test_repo

    @staticmethod
    def clone(repo, dest, branch="main"):
        return GitSync.clone(repo, dest, BRANCH)


def remote_has(path_part):
    out = subprocess.run([gitsync.gh(), "api", f"repos/{REPO}/commits/{BRANCH}", "--jq", ".sha"], capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip()


try:
    with mock.patch.object(F, "GitSync", TestSync), mock.patch.object(gitsync, "PUSH_AFTER", 1):
        mac = tmp / "mac-a" / "Notes"
        mac.parent.mkdir()
        Memory.create(mac, PW)
        fs = F.Folders(None)
        info = fs.add_existing(str(mac))
        f = fs.get(info["id"])
        f.memory.unlock(PW)
        f.memory.save("Hello.md", "hello from the app\n")
        info = fs.to_github(f.id)
        check(info["github"] == REPO and f.sync, "the folder is kept in GitHub", info)
        first = remote_has("")
        check(first, "the scrambled files went up")

        f.memory.save("Hello.md", "hello from the app\nchanged later\n")
        sha = first
        for _ in range(40):
            time.sleep(1)
            sha = remote_has("")
            if sha and sha != first:
                break
        check(sha and sha != first, "a change goes up by itself, seconds later", f.sync.status())
        check(f.sync.status()["error"] == "" and f.sync.status()["ago"] is not None, "the status says synced", f.sync.status())

        f.sync.stop()
        fs2 = F.Folders(None)   # the app starts again
        f2 = fs2.get(f.id)
        check(f2.github == REPO and f2.sync is not None, "after a restart it keeps syncing", f2.info())
        f2.sync.stop()

        other = tmp / "mac-b"
        other.mkdir()
        got = fs2.from_github(REPO, other)
        g = fs2.get(got["id"])
        g.memory.unlock(PW)
        check(g.memory.read("Hello.md") == "hello from the app\nchanged later\n", "another Mac opens it from GitHub",
              got)
        check(got["github"] == REPO, "and keeps it in step too")
        g.sync.stop()
        try:
            fs2.to_github(g.id)
            check(False, "a folder already in GitHub can't be added twice")
        except ValueError:
            check(True, "a folder already in GitHub can't be added twice")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)}/{len(ok)} passed  (test branch {BRANCH})")
raise SystemExit(0 if all(ok) else 1)
