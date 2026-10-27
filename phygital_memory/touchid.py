"""Touch ID (or the Mac password when there's no Touch ID), through the small helper in packaging/touchid. Used to
unlock a memory without typing its password, and to confirm an AI app's first connection."""
import os
import subprocess
import sys
from pathlib import Path

SERVICE = os.environ.get("PHYGITAL_MEMORY_TOUCHID_KEYCHAIN", "Phygital Memory Touch ID (app only)")


def bundled() -> Path | None:
    """The helper inside the built app (Resources/server/touchid/Phygital Memory), the only one it ever uses."""
    p = Path(sys.executable).parent / "touchid" / "Phygital Memory"
    return p if getattr(sys, "frozen", False) and p.is_file() else None


def _helper() -> Path | None:
    if getattr(sys, "frozen", False):   # the built app: never a helper named by the environment
        return bundled()
    here = Path(sys.executable).parent
    for p in (os.environ.get("PHYGITAL_MEMORY_TOUCHID"), here / "touchid" / "Phygital Memory",
              Path(__file__).parent.parent / "packaging" / "touchid" / "bin" / "Phygital Memory"):
        if p and Path(p).is_file():
            return Path(p)
    return None


def _run(*args, secret: bytes | None = None, timeout=120):
    h = _helper()
    if not h:
        return None
    try:
        return subprocess.run([str(h), *args], input=secret, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def available() -> bool:
    r = _run("can", timeout=10)
    return bool(r) and r.returncode == 0


def ask(kind: str) -> bool:
    """kind: "unlock" or "allow". The helper has its own fixed wording for each, so nobody can make it say anything else."""
    r = _run("ask", kind)
    return bool(r) and r.returncode == 0


def save(folder_id: str, password: str) -> None:
    r = _run("save", SERVICE, folder_id, secret=password.encode(), timeout=30)
    if not r or r.returncode != 0:
        raise RuntimeError("Couldn't keep it in the Keychain.")


def get(folder_id: str) -> str | None:
    """The memory's password after the person confirmed, or None (said no, or nothing kept)."""
    r = _run("get", SERVICE, folder_id)
    return r.stdout.decode() if r and r.returncode == 0 and r.stdout else None


def has(folder_id: str) -> bool:
    r = _run("has", SERVICE, folder_id, timeout=10)
    return bool(r) and r.returncode == 0


def forget(folder_id: str) -> None:
    _run("forget", SERVICE, folder_id, timeout=30)
