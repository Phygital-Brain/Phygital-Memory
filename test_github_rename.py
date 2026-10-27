"""Open from GitHub lists your memory repos, and renaming a memory renames its GitHub repo and README, for real.

Uses the private test repo (renamed for the test, then back) on a fresh branch.
Run: uv run python test_github_rename.py
"""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-ghren-"))
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
from phygital_memory import folders as F, gitsync   # noqa: E402
from phygital_memory.gitsync import GitSync, repo_name   # noqa: E402
from phygital_memory.memory import Memory              # noqa: E402

PW = "test-ghren-pass"
ME = gitsync.signed_in()
TEST = os.environ.get("PM_TEST_REPO", "phygital-memory-sync-test")
BRANCH = "rename-" + time.strftime("%Y%m%d-%H%M%S")
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


check(repo_name("Phygital Memory") == "Phygital-Memory", "a memory called Phygital Memory isn't doubled", repo_name("Phygital Memory"))
check(repo_name("Work Phygital Memory") == "Work-Phygital-Memory", "nor one ending in Phygital Memory")
check(repo_name("My Notes") == "My-Notes-Phygital-Memory", "other names get -Phygital-Memory")


def use_test_repo(self):
    self.repo = self.state["repo"] = f"{ME}/{TEST}"
    self.prepare(self.folder.name)
    self.git("init", "-b", self.branch)
    self.git("remote", "add", "origin", f"https://github.com/{ME}/{TEST}.git")
    self.sync_once()
    return self.repo


class TestSync(GitSync):
    def __init__(self, folder, repo, branch="main", watch=None):
        super().__init__(folder, repo, BRANCH, watch)

    create = use_test_repo

    @staticmethod
    def clone(repo, dest, branch="main"):
        return GitSync.clone(repo, dest, BRANCH)


current = f"{ME}/{TEST}"
try:
    with mock.patch.object(F, "GitSync", TestSync):
        mac = tmp / "mac-a" / "Notes"
        mac.parent.mkdir()
        Memory.create(mac, PW)
        fs = F.Folders(None)
        f = fs.get(fs.add_existing(str(mac))["id"])
        f.memory.unlock(PW)
        f.memory.save("Hello.md", "before the rename\n")
        fs.to_github(f.id)
        f.sync.stop()   # the test drives the syncing itself

        info = fs.rename(f.id, "Sync Test")
        current = info.get("github") or current
        check(info.get("github") == f"{ME}/Sync-Test-Phygital-Memory" and "warning" not in info,
              "renaming the memory renames the GitHub repo", info)
        url = f.sync.git("remote", "get-url", "origin").stdout.strip()
        check(url.endswith("/Sync-Test-Phygital-Memory.git"), "git now points at the new name", url)
        check((mac / "README.md").read_text().split("\n")[1].startswith("# Sync Test"), "the README has the new name")
        check(gitsync.is_private(current), "the renamed repo is still private")

        f.memory.save("Hello.md", "after the rename\n")
        f.sync.sync_once()
        tree = subprocess.run([gitsync.gh(), "api", f"repos/{current}/contents/README.md?ref={BRANCH}", "--jq", ".content"],
                              capture_output=True, text=True).stdout
        import base64
        check("# Sync Test" in base64.b64decode(tree or b"").decode(errors="replace"), "the new README went up to GitHub")

        repos = gitsync.memory_repos()
        check(any(r["repo"] == current for r in repos), "Open from GitHub lists it", [r["repo"] for r in repos])
        check(all(r["repo"].split("/")[1].lower().endswith("phygital-memory") for r in repos), "and lists only memory repos")

        other = tmp / "mac-b"
        other.mkdir()
        got = fs.from_github(current, other)
        g = fs.get(got["id"])
        g.memory.unlock(PW)
        check(got["name"] == "Sync Test" and g.memory.read("Hello.md") == "after the rename\n",
              "another Mac opens the renamed repo, with a readable name", got)
        g.sync.stop()
finally:
    if current != f"{ME}/{TEST}":
        gitsync.rename_repo(current, TEST)   # the test repo gets its name back
    shutil.rmtree(tmp, ignore_errors=True)
check(gitsync.is_private(f"{ME}/{TEST}"), "the test repo is back under its own name")

print(f"\n{sum(ok)}/{len(ok)} passed  (branch {BRANCH})")
raise SystemExit(0 if all(ok) else 1)
