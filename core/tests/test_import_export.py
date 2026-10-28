"""Import files and folders from the Mac (encrypted on the way in), and export readable copies out.

Run: uv run python test_import_export.py
"""
import os
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
    big = os.urandom(1 << 20) * 40 + b"tail"   # about 42 MB, over the old 25 MB limit
    (src / "big.bin").write_bytes(big)
    for n in (0, 1, 32 * 1024, 32 * 1024 + 1, 3 * 32 * 1024):   # sizes around the 32 KiB parts
        (src / f"edge-{n}.bin").write_bytes(os.urandom(n))

    j = m.import_paths("Projects", [str(src / "note.md"), str(src / "big.bin")])
    check(j["imported"] == ["Projects/note.md", "Projects/big.bin"] and j["skipped"] == 0, "files: the note and a 42 MB file come in", j)
    check(m._tree.file_size(m._tree.resolve("Projects/big.bin")) == len(big), "the big file has the right size inside")
    try:
        m.read_bytes("Projects/big.bin")
        check(False, "a file over 25 MB isn't pulled into the app whole")
    except ValueError:
        check(True, "a file over 25 MB isn't pulled into the app whole")
    edges = [str(src / f"edge-{n}.bin") for n in (0, 1, 32 * 1024, 32 * 1024 + 1, 3 * 32 * 1024)]
    j = m.import_paths("", edges)
    check(all(m.read_bytes(f"edge-{n}.bin") == (src / f"edge-{n}.bin").read_bytes() for n in (0, 1, 32 * 1024, 32 * 1024 + 1, 3 * 32 * 1024)),
          "files of every size around the 32 KiB parts read back exactly")
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
    m.export("Projects/big.bin", str(out / "big.bin"))
    check((out / "big.bin").read_bytes() == big, "export the 42 MB file: exactly the same bytes")
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
