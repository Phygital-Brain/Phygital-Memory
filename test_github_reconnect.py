"""Connect, stop, connect again: the app sees the memory's old repo and uses it again, keeping both sides. A name
taken by a different memory gets "-2" instead. For real on GitHub, on the test repo (fresh branch, no new repos).

Run: uv run python test_github_reconnect.py
"""
import os
import shutil
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-recon-"))
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
os.environ["PHYGITAL_MEMORY_TRASH"] = str(tmp / "Trash")
(tmp / "Trash").mkdir()
from phygital_memory import folders as F, gitsync   # noqa: E402
from phygital_memory.gitsync import GitSync, SameMemoryRepo   # noqa: E402
from phygital_memory.memory import Memory               # noqa: E402

PW = "test-recon-pass"
ME = gitsync.signed_in()
TEST = os.environ.get("PM_TEST_REPO", "phygital-memory-sync-test")
FULL = f"{ME}/{TEST}"
BRANCH = "recon-" + time.strftime("%Y%m%d-%H%M%S")
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


class TestSync(GitSync):   # the app's GitSync, on the test repo and branch
    def __init__(self, folder, repo, branch="main", watch=None):
        super().__init__(folder, TEST, BRANCH, watch)


try:
    with mock.patch.object(F, "GitSync", TestSync), mock.patch.object(TestSync, "_make_repo", lambda self: FULL):
        mac = tmp / "mac" / "Notes"
        mac.parent.mkdir()
        Memory.create(mac, PW)
        fs = F.Folders(None)
        f = fs.get(fs.add_existing(str(mac))["id"])
        f.memory.unlock(PW)
        f.memory.save("Shared.md", "line one\nline two\n")
        f.memory.save("Plan.md", "plan v1\n")
        with mock.patch.object(gitsync, "_exists", lambda repo: False):   # the first time: the repo is "new"
            check(fs.to_github(f.id)["github"] == FULL, "connected the first time")
        f.sync.stop()
        fs.stop_github(f.id)
        check(f.github is None, "stopped: Mac only")

        # Meanwhile: this Mac edits a note, and another Mac (a clone) changes the same note and adds one.
        f.memory.save("Plan.md", "plan v2 from this mac\n")
        f.memory.save("Shared.md", "line one\nline two\nline three (this mac)\n")
        other = GitSync.clone(FULL, tmp / "other" / "Notes", BRANCH)
        o = Memory(other.folder)
        o.unlock(PW)
        o.save("Shared.md", "line one\nline two (other mac)\n")
        o.save("FromOther.md", "made on the other mac\n")
        other.sync_once()

        try:
            fs.to_github(f.id)
            check(False, "connecting again sees the memory's old repo")
        except SameMemoryRepo as e:
            check(e.repo == FULL, "connecting again sees the memory's old repo", e.repo)
        info = fs.to_github(f.id, reuse=FULL)
        f.sync.stop()
        check(info["github"] == FULL, "and uses it again when asked")
        f.memory._synced = 0
        files = {x["path"] for x in f.memory.list_files()}
        check("FromOther.md" in files and f.memory.read("FromOther.md") == "made on the other mac\n",
              "the other Mac's new note came down", sorted(files))
        check(f.memory.read("Plan.md") == "plan v2 from this mac\n", "this Mac's edit is kept")
        texts = [f.memory.read(p) for p in files if p.startswith("Shared")]
        check(any("(this mac)" in t for t in texts) and any("(other mac)" in t for t in texts),
              "a note changed on both sides keeps both versions", sorted(p for p in files if p.startswith("Shared")))
        other.sync_once()
        o._synced = 0
        check(o.read("Plan.md") == "plan v2 from this mac\n", "and everything went up for the other Mac")

        # A different memory whose name gives the same repo name: it never touches that repo, it gets "-2".
        second = tmp / "mac2" / "Notes"
        second.parent.mkdir()
        Memory.create(second, PW)
        tried = []
        with mock.patch.object(GitSync, "_make_repo", lambda self: tried.append(self.repo) or (_ for _ in ()).throw(RuntimeError("stop"))), \
             mock.patch.object(gitsync, "_exists", lambda repo: repo == FULL):
            try:
                GitSync(second, TEST, BRANCH).create()
            except RuntimeError:
                pass
        check(tried == [f"{TEST}-2"], "another memory with the same name gets a new repo name", tried)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)}/{len(ok)} passed  (branch {BRANCH})")
raise SystemExit(0 if all(ok) else 1)
