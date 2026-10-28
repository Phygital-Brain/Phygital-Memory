"""Folds the long licence files (editor libraries and fonts, Python, Rust) into one short one: each licence text once,
with every part that uses it listed above it, each with its own copyright lines. Nothing is dropped: a part whose text
differs keeps its own text.

Run: python3 packaging/compact_licences.py LICENCE_DIR in1.txt in2.txt ... out.txt   (the inputs are deleted)
"""
import re
import sys
from pathlib import Path

d = Path(sys.argv[1])
ins, out = [d / n for n in sys.argv[2:-1]], d / sys.argv[-1]
HEAD = re.compile(r"^(?P<name>\S+(?: bootloader)?) (?P<ver>v?\d[^\s,]*), (?P<lic>.+)$")
COPY = re.compile(r"^\s*(copyright\b|\(c\)|©)", re.I)

parts, notes = [], []
for f in ins:
    for chunk in re.split(r"\n\n---\n\n|\n\n\n(?=[A-Z0-9 :,.()'-]+\n=+\n)", f.read_text()):
        lines = chunk.strip().splitlines()
        while lines and (re.fullmatch(r"[A-Z0-9 :,.()'-]+", lines[0].strip()) or re.fullmatch(r"=+", lines[0].strip())
                         or not lines[0].strip()):
            lines.pop(0)   # a section title (NOTE EDITOR, ======)
        if lines and not HEAD.match(lines[0]):   # a note before the parts, like the MPL one: keep it as written
            first = next((i for i, l in enumerate(lines) if HEAD.match(l)), len(lines))
            notes.append("\n".join(lines[:first]).strip())
            lines = lines[first:]
        if not lines:
            continue
        m = HEAD.match(lines[0])
        for doc in "\n".join(lines[1:]).split("\n\n~~~\n\n"):   # a part may ship two licences (MIT and Apache)
            rights = [l.strip() for l in doc.splitlines() if COPY.match(l)]
            text = re.sub(r"\n{3,}", "\n\n", "\n".join(l for l in doc.splitlines() if not COPY.match(l))).strip()
            parts.append({"who": f"{m['name']} {m['ver']}", "lic": m["lic"].strip(), "rights": rights, "text": text})

groups = {}   # the same licence wording (copyright lines, title line, spacing and punctuation aside)
for p in parts:
    words = p["text"].splitlines()
    if words and len(words[0]) < 60 and re.search(r"licen[cs]e|^mit|^bsd|^isc", words[0], re.I):
        words = words[1:]   # "MIT License", "The MIT License (MIT)": the title line
    key = re.sub(r"[^a-z]", "", " ".join(words).lower())
    groups.setdefault(key, []).append(p)

NAMES = [("apache license", "Apache License 2.0"), ("mozilla public license", "Mozilla Public License 2.0"),
         ("sil open font", "SIL Open Font License 1.1"), ("python software foundation", "Python Software Foundation License"),
         ("gnu general public", "GNU GPL (PyInstaller bootloader, with its exception)"), ("unicode", "Unicode License"),
         ("free and unencumbered", "The Unlicense"), ("provided 'as-is'", "zlib License"), ("provided \"as-is\"", "zlib License"),
         ("permission to use, copy, modify, and/or distribute", "ISC License"),
         ("permission to use, copy, modify, and distribute", "ISC License"),
         ("permission is hereby granted, free of charge", "MIT License"),
         ("redistribution and use in source and binary forms", "BSD License"), ("cc0", "CC0 1.0")]


def named(text: str) -> str:
    t = re.sub(r"\s+", " ", text.lower())
    return next((n for k, n in NAMES if k in t), "Other licence text") if t else "Named licence, no text shipped"


blocks = []
for key, ps in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    seen_who = {}
    for p in ps:   # one line per part, its copyright lines joined
        seen_who.setdefault(p["who"], []).extend(x for x in p["rights"] if x not in seen_who.get(p["who"], []))
    who = "\n".join(f"  {w}" + (f". {' '.join(r)}" if r else "") for w, r in sorted(seen_who.items(), key=lambda kv: kv[0].lower()))
    n = len(seen_who)
    title = f"{named(ps[0]['text'])}: {n} part{'s' if n > 1 else ''}"
    blocks.append(f"{title}\n{'-' * len(title)}\n{who}\n\n{ps[0]['text'] or '(No licence text ships with these. Each names its licence above.)'}")

out.write_text("EVERY OTHER PART, BY LICENCE\n============================\n\n"
               "Each licence text is printed once, with the parts that use it and their copyright lines listed above it.\n\n"
               + "".join(n + "\n\n" for n in notes) + "\n\n\n".join(blocks) + "\n")
for f in ins:
    f.unlink()
print(f"{len({p['who'] for p in parts})} parts, {len(groups)} licence texts")
