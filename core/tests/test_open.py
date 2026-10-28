"""An Open memory (a plain folder, phygital_memory/vault/plain.py): opens with no password, notes are plain files any
app can read, and search, versions, trash, moves and AI tasks work as in an Encrypted one. Another program's
change shows up, and dot folders like .git and links are left alone. A throwaway folder, no server.

Run: uv run python test_open.py
"""
import os
import shutil
import tempfile
import time
from pathlib import Path

from phygital_memory import brain, memory
from phygital_memory.memory import Memory

ok = []


def check(cond, what):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what)


tmp = Path(tempfile.mkdtemp(prefix="pm-open-"))
try:
    root = tmp / "Notes"
    Memory.create_open(root)
    (root / ".git").mkdir()
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
    (root / "Old.md").write_text("# Old\n\nwritten before the app, about a lighthouse\n")
    (root / ".env").write_text("TOKEN=not-a-real-one\n")
    (root / ".obsidian").mkdir()
    (root / ".obsidian" / "app.json").write_text("{}")
    (root / ".DS_Store").write_bytes(b"mac clutter")
    os.symlink("/etc", root / "outside")
    m = Memory(root, plain=True)
    m.tasks_file = tmp / "tasks.bin"
    m.unlock("")
    check(m.is_open, "opens with no password")

    m.save("Projects/Plan.md", "# Plan\n\nthe kite festival in June\n")
    check((root / "Projects" / "Plan.md").read_text() == "# Plan\n\nthe kite festival in June\n", "a note is a plain file on disk")
    check(m.search("lighthouse") and m.search("kite festival"), "search finds old and new notes")
    files = {f["path"] for f in m.list_files()}
    check("Old.md" in files and "Projects/Plan.md" in files, "the sidebar lists the files")
    check(not any(p.startswith((".git", "outside", ".phygital", ".DS_Store")) for p in files), ".git, the app's own folders, Mac clutter and links are left out")
    check({".env", ".obsidian/app.json"} <= files, f"hidden files are listed, so Show hidden files works ({sorted(files)})")

    m.save("Projects/Plan.md", "# Plan\n\nthe kite festival moved to July\n", keep_version=True)
    check(len(m.versions("Projects/Plan.md")) == 1, "a change keeps the old version")
    check((root / ".versions").is_dir(), "versions live in a hidden folder in the memory")

    m.move("Projects/Plan.md", "Projects/Kites.md")
    check((root / "Projects" / "Kites.md").exists() and not (root / "Projects" / "Plan.md").exists(), "a move renames the file on disk")
    check(len(m.versions("Projects/Kites.md")) == 1, "versions follow the move")
    m.move("Projects", "Work")
    check((root / "Work" / "Kites.md").exists(), "a folder moves with what's in it")

    m.trash("Work/Kites.md")
    check(not (root / "Work" / "Kites.md").exists() and m.trash_list(), "trash moves it out of sight")
    m.trash_restore(m.trash_list()[0]["id"])
    check(m.read("Work/Kites.md").endswith("July\n"), "restore puts it back")

    (root / "Phone.md").write_text("added on the phone, about otters\n")
    m._synced = 0
    check(m.search("otters"), "another program's new note shows up in search")

    m.todo_add("Old.md", "tidy this note")
    check(m.todo() and "tidy this note" in (root / ".ai-tasks" / "AI tasks.md").read_text(), "AI tasks work, in the AI tasks note")

    m.write_bytes("pic.png", b"\x89PNG fake")
    check((root / "pic.png").read_bytes() == b"\x89PNG fake", "other files are plain too")
    for bad in ("../x.md", ".git/config", "outside/passwd"):
        try:
            m.save(bad, "x")
            check(False, f"refuses {bad}")
        except Exception:
            check(True, f"refuses {bad}")
    check((root / ".git" / "HEAD").read_text().startswith("ref:"), ".git is untouched")
    try:
        m.key_raw
        check(False, "no key to share")
    except ValueError:
        check(True, "no key to share")

    r = brain.build(m, {"work": True, "pages": {}}, "en", "Ana", "Europe/Lisbon")
    check((root / "CLAUDE.md").is_file() and (root / "About").is_dir(), "the brain skeleton builds as plain files")

    m.lock()
    check(not m.is_open and (root / "Old.md").exists(), "closing leaves the files as they are")
    m.unlock("")
    check(m.search("lighthouse"), "opens again")
    # The memory list: an Open memory made, zipped as a backup file, and that zip added back as an Open memory
    from phygital_memory.folders import Folders
    fs = Folders(None)
    made = fs.create(str(tmp), "Zip Me", None)
    f = fs.get(made["id"])
    f.memory.unlock("")
    f.memory.save("Hello.md", "zipped note")
    f.memory.save("Hello.md", "zipped note, changed", keep_version=True)
    zipped = tmp / "zip-me.zip"
    fs.save_backup(f.id, str(zipped))
    import zipfile
    names = zipfile.ZipFile(zipped).namelist()
    check("Zip Me/Hello.md" in names and not any("/.versions/" in n for n in names), "the backup file holds the notes, not the app's history")
    (tmp / "restore").mkdir()
    back = fs.open_backup(str(zipped), str(tmp / "restore"))
    check(back["kind"] == "open" and (tmp / "restore" / "Zip Me" / "Hello.md").read_text() == "zipped note, changed",
          "the backup file comes back as an Open memory")
    fs.lock_all()
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)} of {len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
