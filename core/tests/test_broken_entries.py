"""A broken entry in a locked memory (an empty .c9r folder, a folder whose encrypted directory is gone) is skipped,
like Cryptomator does: the rest of the memory still lists, opens and searches.

Run: sh core/tests/run.sh test_broken_entries.py
"""
import shutil
import tempfile
from pathlib import Path

from phygital_memory.memory import Memory

PW = "test-broken-entries"
ok = 0


def check(cond, what):
    global ok
    assert cond, what
    ok += 1
    print("ok  ", what)


tmp = Path(tempfile.mkdtemp(prefix="pm-broken-"))
try:
    folder = tmp / "notes"
    Memory.create(folder, PW)
    m = Memory(folder)
    m.unlock(PW)
    m.save("Home.md", "home note kiwi\n")
    m.save("Projects/Plan.md", "plan note\n")
    m.save("Gone/Lost.md", "lost note\n")
    m.save("Broken/Inside.md", "inside note\n")
    t = m._tree
    gone = t.dir_location(t.resolve("Gone").dir_id)
    broken_entry = t.resolve("Broken").stored
    m.lock()

    (broken_entry / "dir.c9r").unlink()                     # an empty entry folder: no dir.c9r, no symlink.c9r
    shutil.rmtree(gone)                                     # a folder whose encrypted directory is missing

    m = Memory(folder)
    m.unlock(PW)
    notes = m.list_notes()
    check("Home.md" in notes and "Projects/Plan.md" in notes, "the good notes still list")
    files = [f["path"] for f in m.list_files()]
    check("Broken" not in files, "the empty entry folder is left out")
    check("Gone" in files and "Gone/Lost.md" not in files, "the folder with no directory shows as empty")
    check(m.read("Home.md") == "home note kiwi\n", "a good note still opens")
    check(any(r["path"] == "Home.md" for r in m.search("kiwi")), "search still works")
    check(len(m._tree.broken) == 2, "both broken entries are kept in tree.broken")
    check(m.status()["broken"] == 2, "status counts the broken entries")
    m.save("New.md", "written after\n")
    check(m.read("New.md") == "written after\n", "saving still works")
    m.lock()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{ok} checks passed")
