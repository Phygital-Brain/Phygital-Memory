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

password = secrets.token_urlsafe(18)
PASSWORD_FILE.write_text(password)
os.chmod(PASSWORD_FILE, 0o600)

Memory.create(VAULT, password)
m = Memory(VAULT)
m.unlock(password)
for f in sorted(SAMPLES.rglob("*.md")):
    m.save(str(f.relative_to(SAMPLES)), f.read_text())
print(m.status())
m.lock()
