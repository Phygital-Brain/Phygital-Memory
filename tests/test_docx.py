"""Word files: change words, keep everything else. Makes test .docx files with pandoc and LibreOffice, edits them,
and checks LibreOffice still opens the result. Run: uv run python test_docx.py"""
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from phygital_memory import docx

ok = 0


def check(cond, what):
    global ok
    assert cond, what
    ok += 1
    print("ok  ", what)


tmp = Path(tempfile.mkdtemp(prefix="pm-docx-"))
try:
    md = tmp / "src.md"
    md.write_text("# Garden plan\n\nPlant **tomatoes** in May and basil in June.\n\n"
                  "| Plant | Month |\n|---|---|\n| Tomato | May |\n| Basil | June |\n\nLast line.\n")
    subprocess.run(["pandoc", str(md), "-o", str(tmp / "pandoc.docx")], check=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "docx", "--outdir", str(tmp / "lo"), str(tmp / "pandoc.docx")],
                   check=True, capture_output=True, timeout=120)

    for name, path in (("pandoc", tmp / "pandoc.docx"), ("LibreOffice", tmp / "lo" / "pandoc.docx")):
        data = path.read_bytes()
        paras = docx.paragraphs(data)
        texts = [p["text"] for p in paras]
        check("Garden plan" in texts and "Plant tomatoes in May and basil in June." in texts, f"{name}: reads the paragraphs")
        check(any(p["table"] and p["text"] == "Tomato" for p in paras), f"{name}: knows table cells")
        i = texts.index("Plant tomatoes in May and basil in June.")
        j = next(p["i"] for p in paras if p["text"] == "May")
        out = docx.edit(data, {i: "Plant tomatoes in April and basil in July.", j: "April"})
        after = [p["text"] for p in docx.paragraphs(out)]
        check(after[i] == "Plant tomatoes in April and basil in July." and after[j] == "April", f"{name}: edits land")
        xml = zipfile.ZipFile(__import__("io").BytesIO(out)).read(docx.DOC).decode()
        bold_run = xml[:xml.find(">tomatoes<")]
        check(">tomatoes<" in xml and "<w:b" in bold_run[bold_run.rfind("<w:r>") if "<w:r>" in bold_run else bold_run.rfind("<w:r "):],
              f"{name}: the bold word stays bold")
        zin, zout = zipfile.ZipFile(path), zipfile.ZipFile(__import__("io").BytesIO(out))
        same = all(zin.read(n) == zout.read(n) for n in zin.namelist() if n != docx.DOC)
        check(same and zin.namelist() == zout.namelist(), f"{name}: every other part of the file is unchanged")
        check(docx.edit(data, {i: texts[i]}) == data, f"{name}: no change, same bytes")
        res = tmp / f"{name}-out.docx"
        res.write_bytes(out)
        subprocess.run(["soffice", "--headless", "--convert-to", "txt:Text", "--outdir", str(tmp / "txt"), str(res)],
                       check=True, capture_output=True, timeout=120)
        txt = (tmp / "txt" / f"{name}-out.txt").read_text(encoding="utf-8-sig")
        check("in April and basil in July" in txt and "April" in txt, f"{name}: LibreOffice opens the edited file")

    # spaces and special characters survive
    data = (tmp / "pandoc.docx").read_bytes()
    k = [p["text"] for p in docx.paragraphs(data)].index("Last line.")
    out = docx.edit(data, {k: "  Fish & chips <cheap>  "})
    check([p["text"] for p in docx.paragraphs(out)][k] == "  Fish & chips <cheap>  ", "spaces, & and < survive")
    try:
        docx.paragraphs(b"not a zip")
        check(False, "")
    except docx.DocxError:
        check(True, "a non-Word file is refused politely")
    print(f"\n{ok} passed")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
