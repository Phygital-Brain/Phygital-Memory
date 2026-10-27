"""Sync conflicts: a stale save, cloud-drive conflict copies, and changes made by another device.

Run: uv run python test_conflicts.py
"""
import shutil
import tempfile
import time
from pathlib import Path

from phygital_memory.memory import Memory

PW = "test-conflicts"
ok = 0


def check(cond, what):
    global ok
    assert cond, what
    ok += 1
    print("ok  ", what)


def stored(m, rel):
    return m._tree.contents_path(m._tree.resolve(rel))


tmp = Path(tempfile.mkdtemp(prefix="pm-conflicts-"))
try:
    folder = tmp / "notes"
    Memory.create(folder, PW)
    a, b = Memory(folder), Memory(folder)   # two devices on the same synced folder
    a.unlock(PW)
    b.unlock(PW)

    a.save("Ideas.md", "first\n")
    check(a.save("Ideas.md", "second\n", base="first\n") == "Ideas.md", "a save on top of what we saw goes through")
    copy = a.save("Ideas.md", "mine\n", base="first\n")
    check("(conflict " in copy and a.read("Ideas.md") == "second\n" and a.read(copy) == "mine\n",
          "a save on top of an unseen change keeps both")
    check(a.save("Ideas.md", "second\n", base="old\n") == "Ideas.md", "saving the same text as on disk is no conflict")
    check(a.search("mine") and any(r["path"] == copy for r in a.search("mine")), "the conflict copy is searchable")

    # Another device changes a note: this side picks it up without relocking.
    b.save("Ideas.md", "changed on the phone zebra\n", base="second\n")
    a._synced = 0
    check(any(r["path"] == "Ideas.md" for r in a.search("zebra")), "a change from another device shows up in search")

    # A cloud drive keeps both sides as "ABC (1).c9r". Make one: other text, under Plan.md's scrambled name.
    a.save("Plan.md", "plan from this mac\n")
    a.save("tmp-other.md", "plan from the phone\n")
    main, other = stored(a, "Plan.md"), stored(a, "tmp-other.md")
    other.rename(main.with_name(main.stem + " (1).c9r"))
    a._synced = 0
    files = [f["path"] for f in a.list_files()]
    copies = [p for p in files if p.startswith("Plan (conflict ")]
    check(len(copies) == 1 and a.read(copies[0]) == "plan from the phone\n" and a.read("Plan.md") == "plan from this mac\n",
          "a cloud conflict copy becomes a readable note next to it")
    check(not list(main.parent.glob("* (1).c9r")), "the scrambled copy is gone")
    check(any(c["copy"] == copies[0] for c in a.clashes), "the app is told about it")

    # An exact duplicate is just removed.
    shutil.copy(main, main.with_name(main.stem + " (conflicted copy 2026-10-26).c9r"))
    a._synced = 0
    before = len(a.list_files())
    check(not list(main.parent.glob("*conflicted copy*")) and before == len(files),
          "an identical copy is removed, nothing new appears")

    # A copy whose original is gone comes back under the original name.
    a.save("Gone.md", "came back\n")
    g = stored(a, "Gone.md")
    g.rename(g.with_name(g.stem + " 2.c9r"))
    a._synced = 0
    check("Gone.md" in [f["path"] for f in a.list_files()] and a.read("Gone.md") == "came back\n",
          "a copy without its original takes the original's name")
    print(f"\n{ok} passed")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
