"""Stop GitHub sync: the folder becomes Mac only, notes untouched, the sync's files go to the Trash (not erased),
and the repo on GitHub is left for the person to delete. No GitHub needed for this test.

Run: uv run python test_stop_github.py
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-stopgh-"))
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
os.environ["PHYGITAL_MEMORY_TRASH"] = str(tmp / "Trash")
(tmp / "Trash").mkdir()
from phygital_memory import folders as F   # noqa: E402
from phygital_memory.gitsync import GitSync   # noqa: E402
from phygital_memory.memory import Memory      # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


try:
    notes = tmp / "Notes"
    Memory.create(notes, "test-stop-pass")
    fs = F.Folders(None)
    f = fs.get(fs.add_existing(str(notes))["id"])
    f.memory.unlock("test-stop-pass")
    f.memory.save("Keep.md", "stays on this Mac\n")
    GitSync(notes, "me/Notes-Phygital-Memory").prepare("Notes")
    subprocess.run(["git", "init", "-q"], cwd=notes, check=True)
    f.github = "me/Notes-Phygital-Memory"
    fs._save()

    repo = fs.stop_github(f.id)
    check(repo == "me/Notes-Phygital-Memory", "it says which repo is left on GitHub")
    check(f.github is None and f.info()["github"] is None, "the folder is Mac only now")
    check(not (notes / ".git").exists() and not (notes / ".github").exists() and not (notes / ".gitignore").exists(),
          "the sync's files are gone from the folder")
    trashed = sorted(p.name for p in (tmp / "Trash").iterdir())
    check(len(trashed) == 4 and any(".git (GitHub sync" in n for n in trashed), "they went to the Trash, not erased", trashed)
    check(f.memory.read("Keep.md") == "stays on this Mac\n", "the notes are untouched")
    check(F.Folders(None).get(f.id).github is None, "after a restart it stays Mac only")
    try:
        fs.stop_github(f.id)
        check(False, "stopping twice is refused")
    except ValueError:
        check(True, "stopping twice is refused")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
