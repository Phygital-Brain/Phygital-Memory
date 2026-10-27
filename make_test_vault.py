"""Make the locked test folder from ../sample-notes. Test only: the password goes in .test-password (0600)."""
import os
import secrets
import shutil
import sys
from pathlib import Path

from phygital_memory.memory import Memory

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "sample-notes"
VAULT = HERE.parent / "locked-notes"
PASSWORD_FILE = HERE / ".test-password"

if VAULT.exists():
    if "--fresh" not in sys.argv:
        sys.exit(f"{VAULT} exists. Run with --fresh to make it again.")
    shutil.rmtree(VAULT)

password = "12345678"   # test only; the person asked for this simple one
PASSWORD_FILE.write_text(password)
os.chmod(PASSWORD_FILE, 0o600)

Memory.create(VAULT, password)
m = Memory(VAULT)
m.unlock(password)
for f in sorted(SAMPLES.rglob("*.md")):
    m.save(str(f.relative_to(SAMPLES)), f.read_text())
# images and other files
import zlib, struct
w, h = 320, 180
raw = b"".join(b"\x00" + bytes(v for x in range(w) for v in (int(127 + 128 * x / w) % 256, 80, int(255 * y / h))) for y in range(h))
chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
m.save_bytes("attachments/test-image.png", b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
             + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
for f in sorted((HERE.parent / "sample-files").rglob("*")):
    if f.is_file() and not f.name.startswith("."):   # skip Finder's .DS_Store and other hidden files
        m.save_bytes(str(f.relative_to(HERE.parent / "sample-files")), f.read_bytes())
print(m.status())
m.lock()
