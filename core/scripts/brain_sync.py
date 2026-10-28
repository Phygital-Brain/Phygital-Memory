"""Bring the Phygital Brain files the app builds a brain from into phygital_memory/brain/. Run from core/ whenever
Phygital Brain changes (the app ships what's here; nothing is fetched at run time).

    python3 scripts/brain_sync.py /path/to/phygital-brain

Copies: the English templates and Brain Keeper files, the bundled no-ai-slop skill, and for every built language
its templates, keeper files and strings.json (folder names). Phygital Brain is Apache-2.0; its LICENSE comes along.
"""
import json
import shutil
import sys
from pathlib import Path

src = Path(sys.argv[1]).expanduser()
setup, keeper = src / "skills" / "brain-setup", src / "skills" / "brain-keeper"
out = Path(__file__).resolve().parent.parent / "phygital_memory" / "brain"
if not (setup / "templates").is_dir():
    sys.exit(f"No Phygital Brain at {src}")
shutil.rmtree(out, ignore_errors=True)
shutil.copytree(setup / "templates", out / "en" / "templates")
shutil.copytree(keeper / "templates", out / "en" / "keeper")
shutil.copytree(setup / "bundled", out / "bundled")
shutil.copy2(src / "LICENSE", out / "LICENSE")
langs = [["en", "English"]]
for d in sorted((setup / "i18n").iterdir()):
    if not (d / "strings.json").is_file():
        continue
    for part in ("templates", "keeper"):
        if (d / part).is_dir():
            shutil.copytree(d / part, out / d.name / part)
    shutil.copy2(d / "strings.json", out / d.name / "strings.json")
    langs.append([d.name, json.loads((d / "strings.json").read_text())["language"]["name"]])
(out / "languages.json").write_text(json.dumps(langs, ensure_ascii=False, indent=1) + "\n")
print(f"{len(langs)} languages in {out}")
