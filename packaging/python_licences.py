"""The licences of what the packaged server carries: Python itself, the PyInstaller bootloader that starts it, and every
library it runs with (the project's dependencies, not the build tools). Writes one text file.

Run: uv run python packaging/python_licences.py OUT.txt
"""
import importlib.metadata as md
import platform
import re
import subprocess
import sys
from pathlib import Path

out = Path(sys.argv[1])
names = []
for line in subprocess.run(["uv", "export", "--no-dev", "--no-hashes", "--format", "requirements-txt"],
                           capture_output=True, text=True, check=True).stdout.splitlines():
    m = re.match(r"^([A-Za-z0-9_.-]+)==", line)
    if m:
        names.append(m.group(1))


def texts(dist) -> str:
    files = [f for f in dist.files or [] if re.search(r"(licen[cs]e|copying|notice)", str(f), re.I)
             and not str(f).endswith((".py", ".pyc"))]
    return "\n\n".join(Path(dist.locate_file(f)).read_text(errors="replace").strip() for f in files)


def licence(dist) -> str:
    meta = dist.metadata
    first = ((meta.get("License") or "").strip().splitlines() or [""])[0][:80]
    return meta.get("License-Expression") or first or next(
        (c.split("::")[-1].strip() for c in meta.get_all("Classifier") or [] if c.startswith("License ::")), "see below")


parts = []
py = Path(sys.base_prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "LICENSE.txt"
parts.append(f"Python {platform.python_version()}, PSF-2.0\n\n{py.read_text(errors='replace').strip()}")
pi = md.distribution("pyinstaller")   # only its bootloader ships: it starts the server
parts.append(f"PyInstaller bootloader {pi.version}, GPL-2.0 with the bootloader exception (it may ship in any program)\n\n{texts(pi)}")
missing = []
for n in sorted(set(names), key=str.lower):
    try:
        d = md.distribution(n)
    except md.PackageNotFoundError:
        missing.append(n)   # a library for another system (like pywin32 on Windows): not in the Mac app
        continue
    body = texts(d)
    parts.append(f"{d.metadata['Name']} {d.version}, {licence(d)}\n\n{body or '(no licence file in the package; see its project page)'}")

out.write_text("ENGINE: PYTHON AND ITS LIBRARIES\n================================\n\n" + "\n\n---\n\n".join(parts) + "\n")
print(f"{len(parts)} parts" + (f", not on this system: {', '.join(missing)}" if missing else ""))
