"""Cloud only: a memory that lives in the person's cloud (Nextcloud, or any WebDAV server, for now), not on this Mac.

rclone (MIT) talks to the cloud. While the memory is unlocked it shows the cloud folder to the app as a hidden drive
(macOS's own NFS, so nothing to install; "nobrowse" keeps it out of Finder and off the Desktop). The app then reads
and writes the encrypted files there exactly as it does on disk. Only encrypted files ever leave the Mac; rclone
keeps a small cache of them (also encrypted) while saving.

- Nothing talks to the cloud until the person presses a button: connecting, or unlocking a cloud memory.
- The cloud password lives in the Keychain. rclone gets the connection in its environment (seen only by this Mac
  user), never in a file.
- Locking waits until every saved file has reached the cloud, then removes the drive.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from base64 import b64encode
from pathlib import Path
from urllib.parse import quote, urlparse

KEYCHAIN = os.environ.get("PHYGITAL_MEMORY_CLOUD_KEYCHAIN", "Phygital Memory cloud")   # tests use their own
REMOTE = "PMCLOUD"
KINDS = {"nextcloud": "Nextcloud", "webdav": "WebDAV"}


class CloudError(Exception):
    pass


def rclone() -> str:
    """rclone sits next to the server inside the app; in the test setup it's the one on this Mac."""
    for p in (os.environ.get("PHYGITAL_MEMORY_RCLONE"), str(Path(sys.executable).parent / "rclone"), shutil.which("rclone")):
        if p and Path(p).is_file():
            return p
    raise CloudError("The cloud helper (rclone) is missing from this copy of the app.")


# ---------- the connection: {kind, url, user}; the password only in the Keychain ----------

def make_conn(kind: str, server: str, user: str) -> dict:
    """Nextcloud: the server address and user name are enough (its WebDAV address is always the same shape).
    WebDAV: the full address."""
    if kind not in KINDS:
        raise CloudError("That cloud isn't supported yet.")
    server, user = server.strip().rstrip("/"), user.strip()
    if not user:
        raise CloudError("Type your user name.")
    if not re.match(r"^[a-z]+://", server):
        server = "https://" + server
    u = urlparse(server)
    local = u.hostname in ("127.0.0.1", "localhost", "::1")
    if not u.hostname or u.scheme not in ("https", "http") or (u.scheme == "http" and not local):
        raise CloudError("Type the server's address, like cloud.example.com (it must use https).")
    url = server
    if kind == "nextcloud" and "/remote.php/" not in server:
        url = f"{server}/remote.php/dav/files/{quote(user)}"
    return {"kind": kind, "url": url, "user": user}


def label(conn: dict) -> str:
    return KINDS.get(conn.get("kind"), "Cloud")


def where(conn: dict, path: str) -> str:
    """What the person sees for the place: "Nextcloud · cloud.example.com / Notes/Work"."""
    return f"{label(conn)} · {urlparse(conn['url']).hostname} / {path}"


def _account(conn: dict) -> str:
    return f"{conn['user']}@{conn['url']}"


def save_password(conn: dict, password: str) -> None:
    # shortcut: the password is passed to `security` as an argument (seen only by this Mac user, for a moment), as
    # with the GitHub key. A small Keychain helper in the Mac app would avoid even that; worth doing before release.
    subprocess.run(["security", "add-generic-password", "-U", "-a", _account(conn), "-s", KEYCHAIN, "-w", password],
                   capture_output=True, check=True)


def has_password(conn: dict) -> bool:
    return _password(conn) is not None


def forget_password(conn: dict) -> None:
    subprocess.run(["security", "delete-generic-password", "-a", _account(conn), "-s", KEYCHAIN], capture_output=True)


def _password(conn: dict) -> str | None:
    r = subprocess.run(["security", "find-generic-password", "-a", _account(conn), "-s", KEYCHAIN, "-w"],
                       capture_output=True, text=True)
    return r.stdout.rstrip("\n") or None if r.returncode == 0 else None


def _env(conn: dict, password: str | None = None) -> dict:
    password = password if password is not None else _password(conn)
    if password is None:
        raise CloudError(f"Connect to {label(conn)} again: its password isn't on this Mac any more.")
    obscured = subprocess.run([rclone(), "obscure", "-"], input=password, capture_output=True, text=True,
                              check=True).stdout.strip()
    p = f"RCLONE_CONFIG_{REMOTE}_"
    return {**os.environ, p + "TYPE": "webdav", p + "URL": conn["url"], p + "USER": conn["user"], p + "PASS": obscured,
            p + "VENDOR": "nextcloud" if conn["kind"] == "nextcloud" else "other",
            "RCLONE_CONFIG": "/dev/null"}   # never read or write a config file


def _remote(path: str) -> str:
    return f"{REMOTE}:{path.strip('/')}"


def _run(conn: dict, *args: str, password: str | None = None, timeout: int = 120) -> str:
    try:
        r = subprocess.run([rclone(), *args, "--low-level-retries", "2", "--retries", "1"], env=_env(conn, password),
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise CloudError(f"{label(conn)} didn't answer in time. Check the address and your internet.")
    if r.returncode != 0:
        raise CloudError(_plain(r.stderr, conn))
    return r.stdout


def _plain(err: str, conn: dict) -> str:
    e = err.lower()
    if "401" in e or "unauthorized" in e:
        return "The user name or password is wrong. On Nextcloud, use an app password (Settings › Security)."
    if "no such host" in e or "connection refused" in e or "dial tcp" in e or "timeout" in e:
        return f"Can't reach {urlparse(conn['url']).hostname}. Check the address and your internet."
    if "404" in e or "not found" in e:
        return "That folder isn't in the cloud."
    return "The cloud said no: " + (err.strip().splitlines() or ["unknown error"])[-1][-200:]


def connect(conn: dict, password: str) -> None:
    """Check the login works, then keep the password in the Keychain."""
    _run(conn, "lsf", "--max-depth", "1", _remote(""), password=password, timeout=60)
    save_password(conn, password)


def find_memories(conn: dict, depth: int = 4) -> list[dict]:
    """The memories in this cloud: folders holding a masterkey.cryptomator and a vault.cryptomator, a few levels
    down at most. [{path, name}], by name."""
    out = _run(conn, "lsf", "-R", "--files-only", "--max-depth", str(depth),
               "--include", "masterkey.cryptomator", "--include", "vault.cryptomator", _remote(""), timeout=180)
    seen: dict[str, set] = {}
    for line in out.splitlines():
        parent, _, name = line.rpartition("/")
        seen.setdefault(parent, set()).add(name)
    return sorted(({"path": p, "name": p.rsplit("/", 1)[-1] or label(conn)} for p, names in seen.items()
                   if names == {"masterkey.cryptomator", "vault.cryptomator"}), key=lambda m: m["name"].lower())


def make_folder(conn: dict, path: str) -> None:
    """A new, empty folder in the cloud for a new memory. Refuses if something is already there."""
    parent, _, name = path.strip("/").rpartition("/")
    try:
        names = _run(conn, "lsf", "--max-depth", "1", _remote(parent), timeout=60).splitlines()
    except CloudError:
        names = []   # the parent doesn't exist yet: mkdir makes it
    if name + "/" in names or name in names:
        raise CloudError(f'There is already a "{name}" in that place in the cloud.')
    _run(conn, "mkdir", _remote(path), timeout=60)


# ---------- the hidden drive while a memory is unlocked ----------

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def is_mounted(point: Path) -> bool:
    return os.path.ismount(point)


class Drive:
    """The cloud folder shown at `point` while a cloud memory is unlocked."""

    def __init__(self, conn: dict, path: str, point: Path, cache: Path):
        self.conn, self.path, self.point, self.cache = conn, path, Path(point), Path(cache)
        self.proc: subprocess.Popen | None = None
        self.rc: tuple[int, str] | None = None

    def start(self, timeout: float = 45) -> None:
        if self.proc and self.proc.poll() is None and is_mounted(self.point):
            return
        unmount(self.point)   # a leftover from a crash
        self.point.mkdir(parents=True, exist_ok=True)
        self.cache.mkdir(parents=True, exist_ok=True)
        port, secret = _free_port(), secrets.token_urlsafe(24)
        log = open(self.cache.parent / f"{self.cache.name}.log", "ab")
        self.proc = subprocess.Popen(
            [rclone(), "nfsmount", _remote(self.path), str(self.point), "-o", "nobrowse",
             "--vfs-cache-mode", "writes", "--vfs-write-back", "1s", "--dir-cache-time", "20s",
             "--cache-dir", str(self.cache), "--rc", "--rc-addr", f"127.0.0.1:{port}", "--rc-user", "app",
             "--rc-pass", secret],
            env=_env(self.conn), stdout=log, stderr=log, stdin=subprocess.DEVNULL)
        self.rc = (port, secret)
        end = time.time() + timeout
        while time.time() < end:
            if self.proc.poll() is not None:
                raise CloudError(f"Couldn't open the memory in {label(self.conn)}. Check your internet and try again.")
            if is_mounted(self.point):
                return
            time.sleep(0.2)
        self.stop()
        raise CloudError(f"{label(self.conn)} took too long to answer. Try again.")

    def pending(self) -> int:
        """How many saved files haven't reached the cloud yet (0 if the drive isn't running)."""
        if not self.rc or not self.proc or self.proc.poll() is not None:
            return 0
        port, secret = self.rc
        req = urllib.request.Request(f"http://127.0.0.1:{port}/vfs/stats", data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Basic " + b64encode(f"app:{secret}".encode()).decode()})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.load(r).get("diskCache", {})
        return int(d.get("uploadsInProgress", 0)) + int(d.get("uploadsQueued", 0))

    def stop(self, wait: float = 600) -> int:
        """Wait (up to `wait` seconds) for saved files to reach the cloud, then remove the drive. Returns how many
        files were still waiting when it gave up (they stay in the cache and go up next time it's unlocked)."""
        left = 0
        end = time.time() + wait
        while True:
            try:
                left = self.pending()
            except OSError:
                break
            if not left or time.time() > end:
                break
            time.sleep(0.5)
        unmount(self.point)
        if self.proc:
            try:
                self.proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
            self.proc = None
        self.rc = None
        return left


def unmount(point: Path) -> None:
    if is_mounted(point):
        r = subprocess.run(["umount", str(point)], capture_output=True, timeout=60)
        if r.returncode != 0:
            subprocess.run(["diskutil", "unmount", "force", str(point)], capture_output=True, timeout=60)


def make_key(conn: dict) -> str:
    """One cloud account: the same address and user name."""
    return _account(conn)
