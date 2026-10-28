"""The second audit's fixes, tried for real on a throwaway memory (no server, no Keychain):
a forged name like "../x" (only someone holding the key can plant one, for example through a share) is never shown and
never written outside an export; two versions in the same second are both kept; AI reads never push an Undo out.

Run: uv run python test_audit2.py
"""
import shutil
import tempfile
import time
from pathlib import Path

from phygital_memory import activity, memory
from phygital_memory.memory import Memory

ok = []


def check(cond, what):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what)


tmp = Path(tempfile.mkdtemp(prefix="pm-audit2-"))
try:
    folder = tmp / "memory"
    Memory.create(folder, "test password 1")
    m = Memory(folder)
    m.unlock("test password 1")
    m.save("Shared/ok.md", "fine")
    shared = m._tree.resolve("Shared")
    import base64
    for i, bad in enumerate(("../../escaped.txt", "a/b.txt", "..")):   # what a forged share could hold: the app's own
        good = m._writer.write_file(shared, f"plant{i}.txt", b"planted")  # writer refuses these names, so the test
        names = m._tree.names                                               # forges one like an attacker would
        forged = base64.urlsafe_b64encode(names._siv.encrypt(bad.encode(), [shared.dir_id])).decode() + ".c9r"
        good.stored.rename(good.stored.with_name(forged))
    m.lock(); m.unlock("test password 1")
    names = [e.name for e in m._tree.list_dir(m._tree.resolve("Shared").dir_id)]
    check(names == ["ok.md"], f"forged names are left out of the folder ({names})")
    out = tmp / "export" / "deep"
    out.mkdir(parents=True)
    m.export("Shared", str(out))
    check(not (tmp / "escaped.txt").exists() and not (tmp / "export" / "escaped.txt").exists(),
          "an export never writes outside the chosen place")
    check((out / "Shared" / "ok.md").read_text() == "fine", "the real file still exports")

    memory.VERSION_EVERY = 0
    m.save("v.md", "one")
    m.save("v.md", "two")
    m.save("v.md", "three")   # all in the same second
    check(len(m.versions("v.md")) == 2, "two changes in one second keep both old versions")

    activity.log.clear(); activity.undo.clear()
    activity.undo["u1"] = {"folder": "f", "path": "v.md", "before": "one", "after": ""}
    activity.add("AI", "f", "changed", path="v.md", undo_id="u1")
    for _ in range(400):
        activity.add("AI", "f", "checked status")
    check("u1" in activity.undo and any(a.get("undo") == "u1" for a in activity.log), "400 reads later, the change can still be undone")
    m.lock()
finally:
    shutil.rmtree(tmp)

print(f"\n{sum(ok)}/{len(ok)} passed")
