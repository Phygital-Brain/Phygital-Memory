"""Server mode: the same engine on your own server, with no window around it (see docs/server.md).

Turned on by PHYGITAL_MEMORY_SERVER=1. Then:
- The page and the AI door answer at PHYGITAL_MEMORY_URL (https://memory.example.com) instead of 127.0.0.1.
- The page needs a login with the server's passphrase. The first visit chooses it, after typing the one-time setup
  code the server prints in its log (so whoever opens the address first can't claim the server). Only its scrypt
  fingerprint is kept (passphrase.json in the state folder). PHYGITAL_MEMORY_PASSPHRASE sets it instead, for hosts
  that prefer settings. A login gives a cookie that lasts 30 days or until the server restarts. Too many wrong tries
  close the door for 15 minutes.
- Memories live under PHYGITAL_MEMORY_DATA (/data in Docker). Encrypted ones are unlocked on the page and stay
  open in memory until locked or the server restarts; their passwords are never written down.
- Secrets the desktop app keeps in the Keychain (cloud passwords, the GitHub key, the sharing key) go in one file
  in the state folder that only the server can read.
- Desktop-only parts are off: Touch ID, Finder, the computer's own file choosers.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

ON = os.environ.get("PHYGITAL_MEMORY_SERVER") == "1"
URL = os.environ.get("PHYGITAL_MEMORY_URL", "").strip().rstrip("/")
HOST = urlparse(URL).netloc
PASSPHRASE = os.environ.get("PHYGITAL_MEMORY_PASSPHRASE", "")
DATA = Path(os.environ.get("PHYGITAL_MEMORY_DATA", "/data")).expanduser()
MEMORIES = DATA / "memories"
COOKIE = "pm_session"
SESSION_DAYS = 30
TRIES, WINDOW = 10, 15 * 60   # wrong passphrases allowed in WINDOW seconds, then the door closes for WINDOW

REPO = "Phygital-Brain/Phygital-Memory"
if ON:   # secrets go in the server's own file (FileKeyring below), never a desktop keyring
    os.environ.setdefault("PYTHON_KEYRING_BACKEND", "phygital_memory.hosted.FileKeyring")

_sessions: dict[str, float] = {}   # cookie value: when it ends (in memory only: a restart signs everyone out)
_fails: list[float] = []
_lock = threading.Lock()


def problems() -> list[str]:
    """What must be fixed before the server may start."""
    out = []
    u = urlparse(URL)
    if u.scheme not in ("https", "http") or not u.netloc or u.path not in ("", "/"):
        out.append("PHYGITAL_MEMORY_URL must be the server's address, like https://memory.example.com")
    elif u.scheme == "http" and u.hostname not in ("localhost", "127.0.0.1"):
        out.append("PHYGITAL_MEMORY_URL must start with https:// (http is only for trying it on this computer)")
    if PASSPHRASE and len(PASSPHRASE) < 12:
        out.append("PHYGITAL_MEMORY_PASSPHRASE must be at least 12 characters (or leave it out and choose one on the first visit)")
    return out


MIN = 12
SETUP_CODE = ""   # made at start while no passphrase is set; printed in the server's log


def _pass_file() -> Path:
    from .system import state_dir
    return state_dir() / "passphrase.json"


def _fingerprint(text: str, salt: bytes) -> bytes:
    return hashlib.scrypt(text.encode(), salt=salt, n=2 ** 15, r=8, p=1, maxmem=64 * 1024 * 1024, dklen=32)


def configured() -> bool:
    return bool(PASSPHRASE) or _pass_file().exists()


def _code_file() -> Path:
    from .system import state_dir
    return state_dir() / "setup-code"


def setup_code() -> str:
    """The one-time code for the first visit, while there's no passphrase. It stays the same across restarts (hosts
    restart a server on every deploy) and is deleted once the passphrase is chosen."""
    global SETUP_CODE
    if configured() or SETUP_CODE:
        return SETUP_CODE
    f = _code_file()
    try:
        SETUP_CODE = f.read_text().strip()
    except OSError:
        SETUP_CODE = ""
    if not re.fullmatch(r"[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}", SETUP_CODE):
        SETUP_CODE = "-".join(secrets.token_hex(2) for _ in range(3))
        f.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(f, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            fh.write(SETUP_CODE)
    return SETUP_CODE


def _plain(code: str) -> str:
    """The code as typed, with spaces, dashes and capitals left out."""
    return re.sub(r"[^0-9a-f]", "", code.lower())


def _new_session() -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = time.time() + SESSION_DAYS * 86400
    return token


def choose(code: str, new: str) -> str:
    """The first visit: the setup code, then the server's passphrase. Returns a session cookie, or raises with words
    for the page."""
    now = time.time()
    with _lock:
        _fails[:] = [t for t in _fails if now - t < WINDOW]
        if configured():
            raise ValueError("This server already has a passphrase. Sign in instead.")
        if len(_fails) >= TRIES:
            raise ValueError("Too many wrong tries. Wait 15 minutes, then try again.")
        if not SETUP_CODE or not secrets.compare_digest(_plain(code).encode(), _plain(SETUP_CODE).encode()):
            _fails.append(now)
            raise ValueError("That setup code isn't right. Check the line that starts with First visit in the server's log.")
        if len(new) < MIN:
            raise ValueError("Make it at least 12 characters.")
        salt = secrets.token_bytes(16)
        p = _pass_file()
        p.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump({"salt": salt.hex(), "fp": _fingerprint(new, salt).hex(), "kind": "scrypt-32768-8-1"}, fh)
        _code_file().unlink(missing_ok=True)
        return _new_session()


def _right(given: str) -> bool:
    if PASSPHRASE:
        return secrets.compare_digest(given.encode(), PASSPHRASE.encode())
    try:
        d = json.loads(_pass_file().read_text())
        return secrets.compare_digest(_fingerprint(given, bytes.fromhex(d["salt"])), bytes.fromhex(d["fp"]))
    except (OSError, ValueError, KeyError):
        return False


def secure() -> bool:
    return URL.startswith("https://")


def login(given: str) -> str | None:
    """A new session cookie for the right passphrase, or None. None also while the door is closed."""
    now = time.time()
    with _lock:
        _fails[:] = [t for t in _fails if now - t < WINDOW]
        if len(_fails) >= TRIES:
            return None
        if not _right(given):
            _fails.append(now)
            return None
        return _new_session()


def closed() -> bool:
    with _lock:
        return len([t for t in _fails if time.time() - t < WINDOW]) >= TRIES


def logout(token: str) -> None:
    with _lock:
        _sessions.pop(token, None)


def signed_in(request) -> bool:
    token = request.cookies.get(COOKIE, "")
    with _lock:
        end = _sessions.get(token)
        if end and end < time.time():
            _sessions.pop(token, None)
            end = None
    return bool(end)


def same_site(request) -> bool:
    """A change from this server's own page: browsers send Origin on every POST, and another site's page can't fake it."""
    origin = request.headers.get("origin")
    return origin is None or origin == URL


def cookie_header(token: str, max_age: int) -> str:
    return (f"{COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"
            + ("; Secure" if secure() else ""))


def version() -> str:
    try:
        from importlib.metadata import version as v
        return v("phygital-memory")
    except Exception:
        return "dev"


_latest = {"v": "", "at": 0.0}


def latest() -> str:
    """The newest release on GitHub (checked at most every 6 hours), or "" when it can't be reached."""
    if time.time() - _latest["at"] < 6 * 3600:
        return _latest["v"]
    _latest["at"] = time.time()
    try:
        import urllib.request
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "phygital-memory"})
        with urllib.request.urlopen(req, timeout=10) as r:
            _latest["v"] = str(json.load(r).get("tag_name", "")).lstrip("v")[:40]
    except Exception:
        pass
    return _latest["v"]


# ---------- the secrets file, used instead of the Keychain (keyring backend) ----------

def _secrets_file() -> Path:
    from .system import state_dir
    return state_dir() / "secrets.json"


try:
    from keyring.backend import KeyringBackend
    from keyring.errors import PasswordDeleteError
except ImportError:   # the Mac build has no keyring: server mode never runs there
    KeyringBackend, PasswordDeleteError = object, Exception


class FileKeyring(KeyringBackend):
    """Secrets in one file only the server's user can read. Picked by keyring through PYTHON_KEYRING_BACKEND."""
    priority = 1
    _guard = threading.Lock()

    def _all(self) -> dict:
        try:
            return json.loads(_secrets_file().read_text())
        except (OSError, ValueError):
            return {}

    def _write(self, d: dict) -> None:
        p = _secrets_file()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(d, fh)
        os.replace(tmp, p)

    def get_password(self, service, username):
        return self._all().get(service, {}).get(username)

    def set_password(self, service, username, password):
        with self._guard:
            d = self._all()
            d.setdefault(service, {})[username] = password
            self._write(d)

    def delete_password(self, service, username):
        with self._guard:
            d = self._all()
            if username not in d.get(service, {}):
                raise PasswordDeleteError("Not found.")
            del d[service][username]
            self._write(d)
