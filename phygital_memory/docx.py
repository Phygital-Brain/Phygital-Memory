"""Word files (.docx): read the text paragraph by paragraph, and change words without touching anything else.

A .docx is a zip; the text lives in word/document.xml. We never parse and re-serialise that XML (that would rename
namespace prefixes and Word would call the file damaged). Instead we find the <w:p> paragraphs and their <w:t> text
pieces by position and replace only the characters inside <w:t>. Fonts, styles, tables, pictures, headers and every
other part of the zip stay byte for byte the same. An edited word takes the formatting of the run where the change
starts; untouched words keep theirs.
"""
from __future__ import annotations

import io
import re
import zipfile
from html import unescape

DOC = "word/document.xml"
TOKEN = re.compile(r"<w:p[\s>/]|</w:p>|<w:t(?:\s[^>]*)?/>|<w:t(?:\s[^>]*)?>(.*?)</w:t>|<w:tbl[\s>]|</w:tbl>|<w:pStyle\s[^>]*?w:val=\"([^\"]*)\"|<w:numPr[\s>]",
                   re.S)
MAX_PARAGRAPHS = 20_000


class DocxError(ValueError):
    pass


def _xml(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            return z.read(DOC).decode("utf-8")
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError):
        raise DocxError("This isn't a Word file the app can read (only .docx works, not the old .doc).") from None


def _scan(xml: str) -> list[dict]:
    """Paragraphs in order: {open, close, texts: [(start, end, text)], style, table}. start/end are the positions
    of a <w:t>'s inner text. Paragraphs inside text boxes nest, so a stack keeps each <w:t> with its own paragraph."""
    paras, stack, tables = [], [], 0
    for m in TOKEN.finditer(xml):
        tok = m.group(0)
        if tok.startswith("<w:tbl"):
            tables += 1
        elif tok == "</w:tbl>":
            tables = max(0, tables - 1)
        elif tok.startswith("<w:p") and not tok.startswith("<w:pS"):
            # a self-closing <w:p/> is an empty paragraph
            end = xml.find(">", m.start())
            p = {"open": m.start(), "close": None, "texts": [], "style": "", "table": tables > 0, "list": False}
            paras.append(p)
            if xml[end - 1] == "/":
                p["close"] = end + 1
                p["selfclosing"] = True
            else:
                stack.append(p)
        elif tok == "</w:p>":
            if stack:
                stack.pop()["close"] = m.start()
        elif tok.startswith("<w:numPr"):
            if stack:
                stack[-1]["list"] = True
        elif tok.startswith("<w:pStyle"):
            if stack and not stack[-1]["style"]:
                stack[-1]["style"] = m.group(2)
        elif tok.startswith("<w:t"):
            if stack and m.group(1) is not None:
                stack[-1]["texts"].append((m.start(1), m.end(1), unescape(m.group(1))))
            elif stack:   # <w:t/>: empty text piece, nowhere to put characters
                pass
        if len(paras) > MAX_PARAGRAPHS:
            raise DocxError("This Word file is too long to edit here. Open it in Word.")
    return paras


def paragraphs(data: bytes) -> list[dict]:
    """[{i, text, style, table, list}] for every paragraph, in document order."""
    return [{"i": i, "text": "".join(t[2] for t in p["texts"]), "style": p["style"], "table": p["table"], "list": p["list"]}
            for i, p in enumerate(_scan(_xml(data)))]


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _clean(s: str) -> str:
    # XML 1.0 can't hold most control characters; a line break inside a paragraph isn't a <w:t> character either
    return re.sub(r"[\x00-\x08\x0b-\x1f]", "", s.replace("\r", "").replace("\n", " "))


def edit(data: bytes, changes: dict[int, str]) -> bytes:
    """A copy of the .docx with the given paragraphs' text replaced and everything else untouched."""
    xml = _xml(data)
    paras = _scan(xml)
    patches = []   # (start, end, replacement) on the XML string
    for i, new in changes.items():
        if not 0 <= i < len(paras):
            raise DocxError("The Word file changed shape. Reload it.")
        p, new = paras[i], _clean(str(new))
        old = "".join(t[2] for t in p["texts"])
        if new == old:
            continue
        if not p["texts"]:   # an empty paragraph: add one plain run at its end
            if p.get("selfclosing"):
                tag = xml[p["open"]:p["close"]]
                patches.append((p["open"], p["close"], tag[:-2].rstrip() + ">"
                                + f'<w:r><w:t xml:space="preserve">{_esc(new)}</w:t></w:r></w:p>'))
            else:
                patches.append((p["close"], p["close"], f'<w:r><w:t xml:space="preserve">{_esc(new)}</w:t></w:r>'))
            continue
        # Keep what didn't change: common start and end. The changed middle goes into the piece where it starts.
        pre = 0
        while pre < min(len(old), len(new)) and old[pre] == new[pre]:
            pre += 1
        suf = 0
        while suf < min(len(old), len(new)) - pre and old[-1 - suf] == new[-1 - suf]:
            suf += 1
        cut_from, cut_to, middle = pre, len(old) - suf, new[pre:len(new) - suf]
        pos, placed = 0, False
        for start, end, text in p["texts"]:
            a, b = pos, pos + len(text)
            pos = b
            keep_left = text[:max(0, min(len(text), cut_from - a))]
            keep_right = text[max(0, min(len(text), cut_to - a)):]
            ins = ""
            if not placed and (cut_from < b or (cut_from == b and b == len(old))):
                ins, placed = middle, True
            out = keep_left + ins + keep_right if (a < cut_to and b > cut_from) or ins else text
            if out != text:
                patches.append((start, end, _esc(out)))
                _keep_spaces(xml, start, out, patches)
        if not placed:   # nothing to anchor on (shouldn't happen): append to the last piece
            start, end, text = p["texts"][-1]
            patches.append((start, end, _esc(text + middle)))
            _keep_spaces(xml, start, text + middle, patches)
    if not patches:
        return data
    for start, end, rep in sorted(patches, reverse=True):
        xml = xml[:start] + rep + xml[end:]
    return _rezip(data, xml.encode("utf-8"))


def _keep_spaces(xml: str, start: int, text: str, patches: list) -> None:
    """Word drops a <w:t>'s leading or trailing spaces unless it says xml:space="preserve": add it when needed."""
    tag_start = xml.rfind("<w:t", 0, start)
    tag = xml[tag_start:start]
    if text != text.strip() and "xml:space" not in tag:
        patches.append((tag_start, start, tag[:-1].rstrip() + ' xml:space="preserve">'))


def _rezip(data: bytes, doc: bytes) -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as zin, zipfile.ZipFile(out, "w") as zout:
        for info in zin.infolist():
            body = doc if info.filename == DOC else zin.read(info.filename)
            zout.writestr(info, body, compress_type=info.compress_type)
    return out.getvalue()
