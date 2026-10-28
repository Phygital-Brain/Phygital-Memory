"""Build the engine into one program folder (packaging/dist/phygital-memory-server), on Mac, Windows or Linux.

Run from core/: uv run python packaging/build.py

A folder, not one file: one file unpacks itself on every start, which doubled the start time.
"""
import os
import subprocess
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent
P = "phygital_memory"
# What the engine needs next to its code: the pages, the brain templates, the word list for recovery keys
DATA = ["app.html", "closeask.html", "web", "engram_config.json", "claude_ext", "brain", "brain_memory.json",
        "vault/words_en.txt"]


def main() -> None:
    os.chdir(CORE)
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", "--noupx",
            "--name", "phygital-memory-server", "--distpath", "packaging/dist", "--workpath", "packaging/build",
            "--specpath", "packaging", "--paths", ".",
            "--collect-submodules", P, "--collect-all", "wsgidav", "--collect-submodules", "cheroot"]
    for item in DATA:
        src = CORE / P / item
        dest = f"{P}/{Path(item).parent}".rstrip("/.") if "/" in item else (f"{P}/{item}" if src.is_dir() else P)
        args += ["--add-data", f"{src}{os.pathsep}{dest}"]
    args.append("packaging/entry.py")
    subprocess.run(args, check=True)


if __name__ == "__main__":
    main()
