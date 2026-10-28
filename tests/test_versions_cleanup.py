"""Version history follows a note that moves, stays while the note is in the trash (alone or in a trashed folder),
and is removed once the note leaves the trash for good. No server, no Keychain: a throwaway memory in a temp folder.

Run: uv run python test_versions_cleanup.py
"""
import shutil
import tempfile
from pathlib import Path

from phygital_memory import memory
from phygital_memory.memory import Memory

ok = []


def check(cond, what):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what)


memory.VERSION_EVERY = 0   # keep a version on every save, so the test needn't wait
tmp = Path(tempfile.mkdtemp(prefix="pm-versions-"))
try:
    folder = tmp / "memory"
    Memory.create(folder, "test password 1")
    m = Memory(folder)
    m.unlock("test password 1")
    for rel in ("a.md", "keep.md", "F/inside.md"):
        for i in range(3):
            m.save(rel, f"{rel} version {i}")
    check(m.versions("a.md") and m.versions("keep.md") and m.versions("F/inside.md"), "edits keep versions")

    m.move("a.md", "b.md")
    check(m.versions("b.md") and not m.versions("a.md"), "a moved note takes its history along")

    m.trash("b.md")
    m.trash("F")
    m.lock(); m.unlock("test password 1")
    check(m.versions("b.md") and m.versions("F/inside.md"), "history stays while the note or its folder is in the trash")

    memory.TRASH_DAYS = -1   # everything in the trash is now old enough to go
    m.lock(); m.unlock("test password 1")
    check(not m.trash_list(), "the trash empties")
    check(not m.versions("b.md") and not m.versions("F/inside.md"), "history of notes gone for good is removed")
    check(m.versions("keep.md"), "history of a note that's still here stays")
    left = [e.name for e in m._tree.list_dir(m._tree.resolve(memory.VERSIONS).dir_id)]
    check(left == ["keep.md"], f"no empty history folders are left ({left})")
    m.lock()
finally:
    shutil.rmtree(tmp)

print(f"\n{sum(ok)}/{len(ok)} passed")
