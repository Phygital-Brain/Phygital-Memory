"""Put the engine, Syncthing, rclone and every licence into app/src-tauri/server (Resources/server inside the app).

Run from the top folder after packaging/build.py:
    python3 core/packaging/bundle_server.py            Syncthing and rclone from this computer (Homebrew on a Mac)
    python3 core/packaging/bundle_server.py --fetch    downloaded from their own releases, for this system (CI)

Syncthing (MPL-2.0) and rclone (MIT) go in unchanged, with their licences. The licences of everything else (the
editor's libraries and the fonts, Python and its libraries, Tauri and its Rust crates) are written next to them and
shown in Settings › Licences.
"""
import io
import json
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

TOP = Path(__file__).resolve().parents[2]
CORE = TOP / "core"
SERVER = TOP / "app" / "src-tauri" / "server"
LIC = SERVER / "licenses"
WINDOWS = sys.platform == "win32"
EXE = ".exe" if WINDOWS else ""
# The versions downloaded with --fetch. Change them here, together.
SYNCTHING = "2.1.7"
RCLONE = "1.75.2"

OVERVIEW = """PHYGITAL MEMORY: OPEN-SOURCE PARTS

These open-source parts are inside Phygital Memory. Each part keeps its own licence.

Inside the app
  Sharing between computers: Syncthing (MPL-2.0)
  Cloud storage: rclone (MIT)
  Note editor: CodeMirror and Lezer (MIT)
  Diagrams in notes: Mermaid and the libraries it uses (MIT, ISC, BSD-3-Clause, Unlicense)
  Graph view: Sigma, Graphology and d3 (MIT, ISC)
  Safe pasting: DOMPurify (MPL-2.0 or Apache-2.0)
  Fonts: Anybody, Hanken Grotesk and JetBrains Mono (SIL Open Font License 1.1)
  Engine: Python and its libraries (PSF-2.0, MIT, BSD, Apache-2.0)
  App window: Tauri and the Rust crates it uses (MIT, Apache-2.0, MPL-2.0 and others)

Thanks
  Baalda (github.com/naveedharri/baalda, Apache-2.0), for design and feature ideas. No Baalda code is included.
"""


def _arch() -> str:
    m = platform.machine().lower()
    return "arm64" if m in ("arm64", "aarch64") else "amd64"


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "phygital-memory-build"})   # some hosts refuse Python's own
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def _unpack(data: bytes, url: str, want: str) -> tuple[bytes, dict[str, bytes]]:
    """The program `want` and the licence files from a release archive."""
    files = {}
    if url.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for n in z.namelist():
                files[n] = z.read(n) if not n.endswith("/") else b""
    else:
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            for m in t.getmembers():
                if m.isfile():
                    files[m.name] = t.extractfile(m).read()
    prog = max((v for n, v in files.items() if Path(n).name == want), key=len)   # the program, not a same-named helper file
    lic = {Path(n).name: v for n, v in files.items() if Path(n).name.upper() in ("LICENSE", "LICENSE.TXT", "COPYING")}
    return prog, lic


def fetch_tools() -> dict[str, tuple[str, bytes, str]]:
    """Syncthing and rclone for this system, from their own GitHub and download pages."""
    osname = {"darwin": "macos", "win32": "windows"}.get(sys.platform, "linux")
    arch = _arch()
    st_os = {"macos": "macos", "windows": "windows", "linux": "linux"}[osname]
    st_ext = "zip" if osname in ("macos", "windows") else "tar.gz"
    st_url = (f"https://github.com/syncthing/syncthing/releases/download/v{SYNCTHING}/"
              f"syncthing-{st_os}-{'universal' if osname == 'macos' else arch}-v{SYNCTHING}.{st_ext}")
    rc_os = {"macos": "osx", "windows": "windows", "linux": "linux"}[osname]
    rc_url = f"https://downloads.rclone.org/v{RCLONE}/rclone-v{RCLONE}-{rc_os}-{arch}.zip"
    out = {}
    for name, url, ver in (("syncthing", st_url, SYNCTHING), ("rclone", rc_url, RCLONE)):
        prog, lic = _unpack(_get(url), url, name + EXE)
        text = b"\n".join(lic.values()).decode("utf-8", "replace")
        if not text and name == "rclone":   # rclone's zip has no licence file: take it from its source, same version
            text = _get(f"https://raw.githubusercontent.com/rclone/rclone/v{RCLONE}/COPYING").decode()
        out[name] = (ver, prog, text)
    return out


def local_tools() -> dict[str, tuple[str, bytes, str]]:
    """Syncthing and rclone as installed on this computer (Homebrew), with the licence each ships."""
    out = {}
    for name, lic_name in (("syncthing", "LICENSE"), ("rclone", "COPYING")):
        exe = Path(shutil.which(name) or "").resolve()
        if not exe.is_file():
            sys.exit(f"{name} isn't installed here. Install it, or run with --fetch.")
        ver = subprocess.run([str(exe), "--version" if name == "syncthing" else "version"], capture_output=True,
                             text=True).stdout.split()[1].lstrip("v")
        lic = exe.parent.parent / lic_name
        out[name] = (ver, exe.read_bytes(), lic.read_text() if lic.is_file() else "")
    return out


def main() -> None:
    dist = CORE / "packaging" / "dist" / "phygital-memory-server"
    if not dist.is_dir():
        sys.exit("Build the engine first: cd core && uv run python packaging/build.py")
    shutil.rmtree(SERVER, ignore_errors=True)
    shutil.copytree(dist, SERVER)
    tools = fetch_tools() if "--fetch" in sys.argv else local_tools()
    for name, (ver, prog, lic) in tools.items():
        p = SERVER / (name + EXE)
        p.write_bytes(prog)
        p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    LIC.mkdir(parents=True, exist_ok=True)
    st_ver, _, st_lic = tools["syncthing"]
    rc_ver, _, rc_lic = tools["rclone"]
    (LIC / "1-syncthing.txt").write_text(f"Syncthing {st_ver}\nCopyright the Syncthing contributors. Mozilla Public License 2.0. "
                                         f"Included unchanged.\nSource code: https://github.com/syncthing/syncthing\n\n{st_lic}")
    (LIC / "2-rclone.txt").write_text(f"rclone {rc_ver}\nMIT License. Included unchanged.\n"
                                      f"Source code: https://github.com/rclone/rclone\n\n{rc_lic}")
    shutil.copy(CORE / "phygital_memory" / "web" / "THIRD-PARTY-LICENSES.txt", LIC / "3-libraries-and-fonts.txt")
    py = shutil.which("uv")
    subprocess.run([py, "run", "python", "packaging/python_licences.py", str(LIC / "4-engine-python.txt")] if py
                   else [sys.executable, "packaging/python_licences.py", str(LIC / "4-engine-python.txt")],
                   cwd=CORE, check=True, capture_output=True)
    subprocess.run([sys.executable, str(CORE / "packaging" / "rust_licences.py"), str(TOP / "app" / "src-tauri"),
                    str(LIC / "5-app-window.txt")], check=True, capture_output=True)
    subprocess.run([sys.executable, str(CORE / "packaging" / "compact_licences.py"), str(LIC), "3-libraries-and-fonts.txt",
                    "4-engine-python.txt", "5-app-window.txt", "3-open-source-parts.txt"], check=True, capture_output=True)
    (LIC / "0-overview.txt").write_text(OVERVIEW)
    print(json.dumps({"server": str(SERVER), "syncthing": st_ver, "rclone": rc_ver}))


if __name__ == "__main__":
    main()
