"""Import files and folders from the Mac (encrypted on the way in), and export readable copies out.

Run: uv run python test_import_export.py
"""
import shutil
import tempfile
from pathlib import Path

from phygital_memory.memory import Memory

PW = "test-import-export"
results = []


def check(cond, what, info=""):
    results.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


tmp = Path(tempfile.mkdtemp(prefix="pm-imex-"))
try:
    folder = tmp / "notes"
    Memory.create(folder, PW)
    m = Memory(folder)
    m.unlock(PW)
    m.make_folder("Projects")

    src = tmp / "from-mac"
    (src / "Trip" / "photos").mkdir(parents=True)
    (src / "Trip" / "Plan.md").write_text("# Plan\n\nwombat itinerary\n")
    (src / "Trip" / "photos" / "a.jpg").write_bytes(b"\xff\xd8 fake jpeg")
    (src / "Trip" / ".DS_Store").write_bytes(b"junk")
    (src / "Trip" / ".hidden").mkdir()
    (src / "Trip" / ".hidden" / "x.md").write_text("hidden\n")
    (src / "note.md").write_text("loose note\n")
    (src / "big.bin").write_bytes(b"0" * (25_000_000 + 1))

    j = m.import_paths("Projects", [str(src / "note.md"), str(src / "big.bin")])
    check(j["imported"] == ["Projects/note.md"] and j["skipped"] == 1, "files: the note comes in, the 25 MB+ file is skipped", j)
    j = m.import_paths("Projects", [str(src / "note.md")])
    check(j["imported"] == ["Projects/note 2.md"] and m.read("Projects/note.md") == "loose note\n",
          "a taken name gets ' 2', nothing replaced", j)

    j = m.import_paths("Projects", [str(src / "Trip")])
    paths = {f["path"] for f in m.list_files()}
    check({"Projects/Trip/Plan.md", "Projects/Trip/photos/a.jpg"} <= set(j["imported"]) and j["skipped"] == 2,
          "folder: notes and subfolders come in, hidden files don't", j)
    check(not any(".hidden" in p or "DS_Store" in p for p in paths), "nothing hidden came in")
    check(m.read_bytes("Projects/Trip/photos/a.jpg") == b"\xff\xd8 fake jpeg", "an imported file reads back the same")
    check(any(r["path"] == "Projects/Trip/Plan.md" for r in m.search("wombat itinerary")), "an imported note is searchable right away")
    check(b"wombat" not in b"".join(p.read_bytes() for p in folder.rglob("*") if p.is_file()), "imported text is encrypted on disk")
    j = m.import_paths("Projects", [str(src / "Trip")])
    check(any(p.startswith("Projects/Trip 2/") for p in j["imported"]), "the same folder again goes in as 'Trip 2'", j)

    out = tmp / "out"
    out.mkdir()
    check(m.export("Projects/Trip/Plan.md", str(out / "Plan.md")) == 1 and (out / "Plan.md").read_text() == "# Plan\n\nwombat itinerary\n",
          "export a note: a readable copy")
    n = m.export("Projects/Trip", str(out))
    check(n == 2 and (out / "Trip" / "photos" / "a.jpg").read_bytes() == b"\xff\xd8 fake jpeg", "export a folder: everything in it", n)
    m.export("Projects/Trip", str(out))
    check((out / "Trip 2" / "Plan.md").exists() and (out / "Trip" / "Plan.md").exists(), "exporting again never replaces: 'Trip 2'")
    m.make_folder("Empty")
    m.export("Empty", str(out))
    check((out / "Empty").is_dir(), "an empty folder exports as a folder")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
