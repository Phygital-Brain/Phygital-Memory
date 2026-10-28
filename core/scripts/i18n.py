"""The app's languages. Run from core/.

    python3 scripts/i18n.py extract            every text the app shows -> languages/en.json (the source)
    python3 scripts/i18n.py check              what each language is missing, or has wrong
    python3 scripts/i18n.py translate [code]   fill what's missing in every language (or one), with Claude
                                               (needs ANTHROPIC_API_KEY; --model to choose; --dry to only count)

How it works:
- The English text is the key. The screens ask t("Move to trash"); a text with parts uses {0}, {1}.
- languages/languages.json lists the languages: [code, the language's own name]. English is always there.
- languages/{code}.json maps each English text to the language's text. A missing one shows in English.
- Only the app's own words: note, folder and file names are never translated (the person wrote them), and neither
  are the AI tools' words (AI apps read English best).
- The build copies each language next to the app's page (assets/lang-{code}.json).
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG = ROOT / "languages"
SRC = ROOT / "frontend" / "src"
ENGINE = ROOT / "phygital_memory"
CALL = re.compile(r'\b(?:t|tr)\(\s*"((?:[^"\\\n]|\\.)*)"')
# Errors the engine sends to the app's screens (the AI tools' words stay English)
ENGINE_TEXT = [re.compile(r'"error":\s*"((?:[^"\\\n]|\\.)*)"'),
               re.compile(r'raise (?:ValueError|LookupError|PermissionError|FileNotFoundError|RuntimeError|Exists|Locked|'
                          r'WrongPassword|CloudError|NotFound)\(\s*"((?:[^"\\\n]|\\.)*)"\)')]


def unescape(s: str) -> str:
    return json.loads(f'"{s}"')


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def languages() -> list[list[str]]:
    return load(LANG / "languages.json") or [["en", "English"]]


def extract() -> None:
    texts = set()
    for f in SRC.rglob("*.js"):
        texts |= {unescape(m) for m in CALL.findall(f.read_text())}
    for f in ENGINE.rglob("*.py"):
        s = f.read_text()
        for rx in ENGINE_TEXT:
            texts |= {unescape(m) for m in rx.findall(s)}
    texts = sorted(x for x in texts if x.strip())
    LANG.mkdir(exist_ok=True)
    (LANG / "en.json").write_text(json.dumps({x: x for x in texts}, ensure_ascii=False, indent=1) + "\n")
    if not (LANG / "languages.json").exists():
        (LANG / "languages.json").write_text(json.dumps([["en", "English"]], ensure_ascii=False, indent=1) + "\n")
    print(f"{len(texts)} texts in languages/en.json")


def parts(s: str) -> list[str]:
    return sorted(re.findall(r"\{\d+\}", s))


def check() -> bool:
    en = load(LANG / "en.json")
    good = bool(en)
    if not en:
        print("No languages/en.json yet: run extract.")
    for code, name in languages():
        if code == "en":
            continue
        tr = load(LANG / f"{code}.json")
        missing = [k for k in en if not tr.get(k)]
        extra = [k for k in tr if k not in en]
        broken = [k for k in en if tr.get(k) and parts(tr[k]) != parts(k)]   # {0} lost or added
        print(f"{code} ({name}): {len(en) - len(missing)}/{len(en)} done"
              + (f", {len(missing)} missing" if missing else "") + (f", {len(extra)} no longer used" if extra else "")
              + (f", {len(broken)} with wrong {{0}} parts" if broken else ""))
        good = good and not broken
    return good


def translate(only: str | None, model: str, dry: bool) -> None:
    en = load(LANG / "en.json")
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    for code, name in languages():
        if code == "en" or (only and code != only):
            continue
        path = LANG / f"{code}.json"
        tr = load(path)
        todo = [k for k in en if not tr.get(k)]
        print(f"{code}: {len(todo)} to translate")
        if dry or not todo:
            continue
        if not key:
            sys.exit("Set ANTHROPIC_API_KEY first (it's never stored).")
        for i in range(0, len(todo), 150):
            batch = todo[i:i + 150]
            ask = (f"Translate these texts from a Mac notes app called Phygital Memory into {name} ({code}). Plain, short, "
                   "friendly words, the way a careful native speaker would write app text. Keep every {0}, {1} as it is, "
                   "keep ⌘ ⇧ and keyboard keys, keep the names Phygital Memory, Phygital Key, Phygital Brain, GitHub, "
                   "iCloud, Finder, Touch ID, Claude. Answer with one JSON object mapping each English text to its "
                   "translation, nothing else.\n\n" + json.dumps(batch, ensure_ascii=False))
            req = urllib.request.Request("https://api.anthropic.com/v1/messages", method="POST", data=json.dumps({
                "model": model, "max_tokens": 16000, "messages": [{"role": "user", "content": ask}]}).encode(),
                headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                text = "".join(c.get("text", "") for c in json.loads(r.read())["content"])
            got = json.loads(text[text.index("{"):text.rindex("}") + 1])
            tr.update({k: v for k, v in got.items() if k in en and isinstance(v, str) and parts(v) == parts(k)})
            path.write_text(json.dumps(dict(sorted(tr.items())), ensure_ascii=False, indent=1) + "\n")
            print(f"  {min(i + 150, len(todo))}/{len(todo)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in ("extract", "check", "translate"):
        sys.exit(__doc__)
    if args[0] == "extract":
        extract()
    elif args[0] == "check":
        sys.exit(0 if check() else 1)
    else:
        model = args[args.index("--model") + 1] if "--model" in args else "claude-opus-5-5"
        rest = [a for a in args[1:] if not a.startswith("--") and a != model]
        translate(rest[0] if rest else None, model, "--dry" in args)
