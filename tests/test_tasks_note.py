"""AI tasks as one note, "AI tasks", at the top of the memory (Open and Encrypted): giving a task writes a To do line,
the AI finishing it moves it to Done, a line ticked or typed by hand (on the phone) is read back, the older list on
this Mac moves in once, done ones leave after 7 days, and a share never carries the note.

Run: uv run python test_tasks_note.py
"""
import json
import shutil
import tempfile
import time
from pathlib import Path

from phygital_memory import memory as M, shares
from phygital_memory.memory import Memory

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


tmp = Path(tempfile.mkdtemp(prefix="pm-tasks-"))
try:
    for kind in ("open", "encrypted"):
        root = tmp / kind
        if kind == "open":
            Memory.create_open(root)
            m = Memory(root, plain=True)
            m.tasks_file = tmp / f"{kind}.bin"
            m.unlock("")
        else:
            Memory.create(root, "test password 1")
            m = Memory(root)
            m.tasks_file = tmp / f"{kind}.bin"
            m.unlock("test password 1")
        m.save("Projects/Plan.md", "# Plan\n")

        item = m.todo_add("Projects/Plan.md", "tidy this note")
        note = m.read(M.TASKS_NOTE)
        check("## To do" in note and "- [ ] [[Projects/Plan]] tidy this note" in note, f"{kind}: giving a task writes a To do line", note)
        if kind == "open":
            check((root / "AI tasks.md").is_file(), "open: it's a normal file anyone can open")

        m.todo_set(item["id"], True, "Claude Code", "split it in two")
        note = m.read(M.TASKS_NOTE)
        done = note.split("## Done", 1)[1]
        check("- [x] [[Projects/Plan]] tidy this note → split it in two (Claude Code)" in done, f"{kind}: finished, it moves to Done with what the AI did", note)

        # on the phone: a new line typed by hand, and the done one unticked again
        m.save(M.TASKS_NOTE, note.replace("## To do\n\n", "## To do\n\n- [ ] [[Projects/Plan]] add a budget\n- [ ] call the printer\n")
               .replace("- [x] [[Projects/Plan]] tidy", "- [ ] [[Projects/Plan]] tidy"))
        items = m.todo()
        typed = next((i for i in items if i["ask"] == "add a budget"), {})
        check(typed.get("id", "").startswith("h-") and typed.get("path") == "Projects/Plan.md" and not typed.get("done"),
              f"{kind}: a line typed by hand becomes a task for its note", items)
        check(any(i["ask"] == "call the printer" and i["path"] == "" for i in items), f"{kind}: a line with no note is a task too")
        check(any(i["id"] == item["id"] and not i.get("done") for i in items), f"{kind}: unticked on the phone, it's to do again")
        check("<!-- pm" in m.read(M.TASKS_NOTE).split("add a budget", 1)[1].split("\n", 1)[0], f"{kind}: and it gets its id in the note")

        # ticked on the phone: done, by you
        m.save(M.TASKS_NOTE, m.read(M.TASKS_NOTE).replace("- [ ] call the printer", "- [x] call the printer"))
        check(any(i["ask"] == "call the printer" and i.get("done") and i.get("by") == "you" for i in m.todo()), f"{kind}: ticked on the phone, it's done")

        # done ones leave after 7 days
        items = m.todo()
        for i in items:
            if i.get("done"):
                i["done_t"] = time.time() - 8 * 86400
        m._save_todo(items)
        check(not any(i.get("done") for i in m.todo()), f"{kind}: done ones leave after 7 days")
        m.lock()

    # the older list on this Mac moves into the note once
    root = tmp / "older"
    Memory.create_open(root)
    m = Memory(root, plain=True)
    m.tasks_file = tmp / "older.bin"
    m.unlock("")
    m.save("Old.md", "# Old\n")
    m.read_only = True   # writes the older way, on this Mac
    m._save_todo([{"id": "h-0ld0ld00", "path": "Old.md", "ask": "from before", "t": time.time(), "done": False}])
    m.read_only = False
    check(m.tasks_file.exists(), "a list kept the older way, on this Mac")
    check(any(i["id"] == "h-0ld0ld00" for i in m.todo()) and "from before" in m.read(M.TASKS_NOTE)
          and not m.tasks_file.exists(), "moves into the AI tasks note, once")

    # a share never carries it
    b = tmp / "share-side"
    Memory.create_open(b)
    mb = Memory(b, plain=True)
    mb.tasks_file = tmp / "b.bin"
    mb.unlock("")
    shares.mirror("t", m, mb, b"k" * 32, True)
    check((b / "Old.md").exists() and not (b / "AI tasks.md").exists(), "a share copies the notes, never the AI tasks note")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)} of {len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
