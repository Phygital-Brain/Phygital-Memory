"""Cloud only: a memory that lives in the person's cloud (Nextcloud, or any WebDAV server, for now), not on this Mac.
(An Open memory works the same way, with its readable files: nothing is encrypted for it.)

rclone (MIT) talks to the cloud. While the memory is unlocked it shows the cloud folder to the app as a hidden drive
(macOS's own NFS, so nothing to install; "nobrowse" keeps it out of Finder and off the Desktop). The app then reads
and writes the encrypted files there exactly as it does on disk. Only encrypted files ever leave the Mac; rclone
keeps a small cache of them (also encrypted) while saving.

- Nothing talks to the cloud until the person presses a button: connecting, or unlocking a cloud memory.
- The cloud password lives in the Keychain (in rclone's own "obscured" form, so its cache keeps the same name
  every time). rclone gets the connection in its environment (seen only by this Mac user), never in a file.
- Locking waits until every saved file has reached the cloud, then removes the drive. If the cloud refuses (full),
  the saves wait in the cache and go up the next time the memory is unlocked.
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
import threading
import time
import urllib.request
from base64 import b64encode
from pathlib import Path
from urllib.parse import quote, urlparse

from . import keychain

KEYCHAIN = os.environ.get("PHYGITAL_MEMORY_CLOUD_KEYCHAIN", "Phygital Memory cloud")   # tests use their own
REMOTE = "PMCLOUD"
KINDS = {"nextcloud": "Nextcloud", "webdav": "WebDAV", "s3": "Amazon S3", "r2": "Cloudflare R2"}
S3_KINDS = ("s3", "r2")   # backups only: {kind, url (endpoint), user (access key ID), region}; the secret in the Keychain


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


def make_s3_conn(kind: str, key_id: str, where_: str, endpoint: str = "") -> dict:
    """Amazon S3: the access key ID and the region (like eu-west-1). Cloudflare R2: the access key ID and the
    account ID. endpoint: any other S3-compatible address (tests use a stand-in on this Mac)."""
    key_id, where_ = key_id.strip(), where_.strip().lower()
    if kind not in S3_KINDS:
        raise CloudError("That storage isn't supported yet.")
    if not key_id:
        raise CloudError("Type the access key ID.")
    if endpoint:
        u = urlparse(endpoint)
        if u.scheme not in ("https", "http") or (u.scheme == "http" and u.hostname not in ("127.0.0.1", "localhost")):
            raise CloudError("The address must use https.")
        return {"kind": kind, "url": endpoint.rstrip("/"), "user": key_id, "region": where_ or "auto"}
    if kind == "r2":
        # Cloudflare shows the endpoint ("https://ACCOUNT.r2.cloudflarestorage.com", or with .eu. for EU buckets);
        # the account ID alone works too
        m = re.search(r"([0-9a-f]{32})(\.(eu|fedramp))?\.r2\.cloudflarestorage\.com", where_)
        if m:
            return {"kind": "r2", "url": f"https://{m.group(0)}", "user": key_id, "region": "auto"}
        if not re.fullmatch(r"[0-9a-f]{32}", where_):
            raise CloudError("Paste the S3 endpoint Cloudflare shows, like https://ID.r2.cloudflarestorage.com.")
        return {"kind": "r2", "url": f"https://{where_}.r2.cloudflarestorage.com", "user": key_id, "region": "auto"}
    if not re.fullmatch(r"[a-z]{2}(-[a-z]+)+-\d", where_):
        raise CloudError("Type the region, like eu-west-1.")
    return {"kind": "s3", "url": f"https://s3.{where_}.amazonaws.com", "user": key_id, "region": where_}


def check_bucket(conn: dict, bucket: str, secret: str | None = None) -> None:
    """The keys work and the bucket is there (the app never makes or deletes buckets)."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", bucket.strip()):
        raise CloudError("Type the bucket name, like my-notes-backup.")
    _run(conn, "lsf", "--max-depth", "1", _remote(bucket.strip()), password=secret, timeout=60)


def find_conn(server: str, user: str, password: str) -> dict:
    """One form for every WebDAV server: a full WebDAV address is used as given; a plain address (like
    cloud.example.com) is tried the Nextcloud way first, then as it is. Returns the one that logs in."""
    tries = [make_conn("webdav", server, user)]
    if not urlparse(tries[0]["url"]).path.strip("/"):
        tries.insert(0, make_conn("nextcloud", server, user))
    err = None
    for conn in tries:
        try:
            _run(conn, "lsf", "--max-depth", "1", _remote(""), password=password, timeout=60)
            return conn
        except CloudError as e:
            err = err or e
    raise err


def label(conn: dict) -> str:
    return KINDS.get(conn.get("kind"), "Cloud")


def where(conn: dict, path: str) -> str:
    """What the person sees for the place: "Nextcloud · cloud.example.com / Notes/Work", "Amazon S3 · bucket/Work"."""
    if conn.get("kind") in S3_KINDS:
        return f"{label(conn)} · {path}"
    return f"{label(conn)} · {urlparse(conn['url']).hostname} / {path}"


def _account(conn: dict) -> str:
    return f"{conn['user']}@{conn['url']}"


def _obscure(password: str) -> str:
    return subprocess.run([rclone(), "obscure", "-"], input=password, capture_output=True, text=True,
                          check=True).stdout.strip()


def save_password(conn: dict, password: str) -> None:
    if conn.get("kind") not in S3_KINDS:   # S3 wants its secret as it is; WebDAV's is kept obscured
        password = _obscure(password)   # once: rclone names its cache after the connection, password included
    keychain.save(KEYCHAIN, _account(conn), password)


def has_password(conn: dict) -> bool:
    return _password(conn) is not None


def forget_password(conn: dict) -> None:
    keychain.delete(KEYCHAIN, _account(conn))


def _password(conn: dict) -> str | None:
    try:
        return keychain.read(KEYCHAIN, _account(conn))
    except keychain.Refused:
        return None


def _env(conn: dict, password: str | None = None) -> dict:
    p = f"RCLONE_CONFIG_{REMOTE}_"
    if conn.get("kind") in S3_KINDS:
        secret = password if password is not None else _password(conn)
        if secret is None:
            raise CloudError(f"Connect to {label(conn)} again: its secret key isn't on this Mac any more.")
        provider = "Cloudflare" if conn["kind"] == "r2" else "AWS" if conn["url"].endswith(".amazonaws.com") else "Other"
        return {**os.environ, p + "TYPE": "s3", p + "PROVIDER": provider, p + "ACCESS_KEY_ID": conn["user"],
                p + "SECRET_ACCESS_KEY": secret, p + "ENDPOINT": conn["url"], p + "REGION": conn.get("region") or "auto",
                p + "NO_CHECK_BUCKET": "true", p + "FORCE_PATH_STYLE": "true", "RCLONE_CONFIG": "/dev/null"}
    obscured = _obscure(password) if password is not None else _password(conn)
    if obscured is None:
        raise CloudError(f"Connect to {label(conn)} again: its password isn't on this Mac any more.")
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
    if "signaturedoesnotmatch" in e or "invalidaccesskeyid" in e or "accessdenied" in e:
        return "The keys don't work. Check the access key ID and the secret access key."
    if "nosuchbucket" in e or "bucket does not exist" in e or "directory not found" in e and conn.get("kind") in S3_KINDS:
        return "That bucket isn't there. Check its name (the app never makes buckets)."
    if "507" in e or "insufficient storage" in e or "quota" in e:
        return f"Your {label(conn)} is full."
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


def find_memories(conn: dict, depth: int = 4, base: str = "") -> list[dict]:
    """The memories in this cloud: folders holding a masterkey.cryptomator and a vault.cryptomator (Encrypted), or a
    .phygital/id (Open), a few levels down at most. [{path, name, kind}], by name. base: look only inside it (an S3 /
    R2 bucket)."""
    out = _run(conn, "lsf", "-R", "--files-only", "--max-depth", str(depth + 1), "--include", "masterkey.cryptomator",
               "--include", "vault.cryptomator", "--include", ".phygital/id", _remote(base), timeout=180)
    seen: dict[str, set] = {}
    for line in out.splitlines():
        parent, _, name = line.rpartition("/")
        if parent.endswith(".phygital") and name == "id":   # an Open memory's own ID, in its hidden folder
            parent, name = parent[:-len(".phygital")].rstrip("/"), ".phygital/id"
        elif parent.count("/") >= depth:
            continue
        parent = f"{base.strip('/')}/{parent}".strip("/") if base else parent
        seen.setdefault(parent, set()).add(name)
    return sorted(({"path": p, "name": p.rsplit("/", 1)[-1] or label(conn),
                    "kind": "encrypted" if {"masterkey.cryptomator", "vault.cryptomator"} <= names else "open"}
                   for p, names in seen.items() if p and (names >= {"masterkey.cryptomator", "vault.cryptomator"}
                                                          or ".phygital/id" in names)), key=lambda m: m["name"].lower())


def free_space(conn: dict) -> int | None:
    """Free bytes in the cloud, or None if the cloud doesn't say."""
    try:
        d = json.loads(_run(conn, "about", "--json", _remote(""), timeout=60))
    except (CloudError, ValueError):
        return None
    return d.get("free")


def upload(conn: dict, src: Path, path: str) -> None:
    """Copy a locked memory (encrypted files only) up to the cloud, then check every file arrived."""
    skip = ["--exclude", ".DS_Store", "--exclude", "._*"]
    _run(conn, "copy", str(src), _remote(path), *skip, "--transfers", "8", timeout=24 * 3600)
    try:
        _run(conn, "check", str(src), _remote(path), "--one-way", "--size-only", *skip, timeout=3600)
    except CloudError:
        raise CloudError("Not every file arrived in the cloud, so nothing was moved. Try again.")


def download(conn: dict, path: str, dest: Path) -> None:
    """Copy a memory (encrypted files only) down from the cloud into dest, then check every file arrived."""
    skip = ["--exclude", ".DS_Store", "--exclude", "._*"]
    _run(conn, "copy", _remote(path), str(dest), *skip, "--transfers", "8", timeout=24 * 3600)
    try:
        _run(conn, "check", _remote(path), str(dest), "--one-way", "--size-only", *skip, timeout=3600)
    except CloudError:
        raise CloudError("Not every file came down from the cloud, so nothing was moved. Try again.")


def remove_folder(conn: dict, path: str) -> None:
    try:
        _run(conn, "purge", _remote(path), timeout=3600)
    except CloudError:
        pass


def human(n: int) -> str:
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if n < 1000 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1000


def make_folder(conn: dict, path: str) -> None:
    """A new, empty folder in the cloud for a new memory. Refuses if something is already there."""
    parent, _, name = path.strip("/").rpartition("/")
    try:
        names = _run(conn, "lsf", "--max-depth", "1", _remote(parent), timeout=60).splitlines()
    except CloudError as e:
        if "isn't in the cloud" not in str(e):
            raise   # couldn't look: never risk treating an existing folder as new (a failed upload removes it)
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

    @property
    def left(self) -> int:
        """Saves still waiting in the cache for the cloud (read from rclone's own notes, so it survives a restart)."""
        n = 0
        for meta in (self.cache / "vfsMeta").rglob("*"):
            try:
                n += meta.is_file() and json.loads(meta.read_text()).get("Dirty") is True
            except (OSError, ValueError):
                pass
        return n

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
             "--cache-dir", str(self.cache), "--rc", "--rc-addr", f"127.0.0.1:{port}", "--rc-user", "app"],
            env={**_env(self.conn), "RCLONE_RC_PASS": secret},   # not on the command line: ps shows that to everyone
            stdout=log, stderr=log, stdin=subprocess.DEVNULL)
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

    def _ask(self, what: str) -> dict:
        port, secret = self.rc
        req = urllib.request.Request(f"http://127.0.0.1:{port}/{what}", data=b"{}", method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Basic " + b64encode(f"app:{secret}".encode()).decode()})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r)

    def pending(self) -> int:
        """How many saved files haven't reached the cloud yet (0 if the drive isn't running)."""
        if not self.rc or not self.proc or self.proc.poll() is not None:
            return 0
        d = self._ask("vfs/stats").get("diskCache", {})
        return int(d.get("uploadsInProgress", 0)) + int(d.get("uploadsQueued", 0))

    def health(self) -> dict:
        """{waiting, problem}: saves not in the cloud yet, and why, in plain words, if the cloud refused them."""
        try:
            waiting = self.pending()
            err = self._ask("core/stats").get("lastError", "") if waiting else ""
        except (OSError, ValueError, TypeError):
            return {"waiting": 0, "problem": None}
        return {"waiting": waiting, "problem": _plain(err, self.conn) if err else None}

    def stop(self, wait: float = 600) -> int:
        """Wait (up to `wait` seconds, or 20 once the cloud refuses a save) for saved files to reach the cloud, then
        remove the drive. Returns how many were still waiting: they stay in the cache and go up the next time it's
        unlocked."""
        left = 0
        start = time.time()
        while True:
            h = self.health()
            left = h["waiting"]
            if not left or time.time() - start > (20 if h["problem"] else wait):
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


SKIP = ["--exclude", ".DS_Store", "--exclude", "._*", "--exclude", ".git/**", "--exclude", "*.tmp"]
MIRROR_AFTER = 5     # seconds after a change before it goes up
MIRROR_EVERY = 60    # seconds between looks for changes made on other devices


class Mirror:
    """Mac + WebDAV: the memory lives on this Mac (fast, works offline) and stays in step with a folder on the
    WebDAV server both ways (rclone bisync). Only encrypted files ever go. A note changed on two devices at once
    keeps both: the extra copy gets a clash name the app already knows how to show."""

    def __init__(self, conn: dict, path: str, folder: Path, workdir: Path, watch=None):
        self.conn, self.path, self.folder, self.workdir, self.watch = conn, path, Path(folder), Path(workdir), watch
        self.state = {"last": None, "error": "", "stopped": False}
        self._wake = threading.Event()
        self._lock = threading.Lock()
        self._thread = None

    def sync_once(self) -> None:
        with self._lock:
            first = not (self.workdir / "done").exists()
            self.workdir.mkdir(parents=True, exist_ok=True)
            _run(self.conn, "bisync", str(self.folder), _remote(self.path), "--workdir", str(self.workdir / "bisync"),
                 *(["--resync"] if first else []), "--resilient", "--recover", "--create-empty-src-dirs",
                 # a clash: the newer one keeps the name, the other becomes "NAME.conflict1.c9r", which the app
                 # turns into a readable clash copy next to the note (nothing is lost)
                 "--conflict-resolve", "newer", "--conflict-loser", "num", "--suffix-keep-extension", *SKIP, timeout=3600)
            (self.workdir / "done").touch()
            self.state.update(last=time.time(), error="")

    def poke(self) -> None:
        self._wake.set()

    def start(self) -> None:
        if self._thread:
            return

        def seen():
            try:
                return self.watch() if self.watch else None
            except Exception:
                return None

        def loop():
            last, waited = seen(), MIRROR_EVERY
            while not self.state["stopped"]:
                if waited < MIRROR_EVERY and not self._wake.is_set() and seen() == last:
                    self._wake.wait(MIRROR_AFTER)
                    waited += MIRROR_AFTER
                    continue
                if self._wake.is_set() or seen() != last:
                    time.sleep(MIRROR_AFTER)
                self._wake.clear()
                last, waited = seen(), 0
                try:
                    self.sync_once()
                except Exception as e:
                    self.state["error"] = str(e)[:300]
        self._thread = threading.Thread(target=loop, name=f"mirror {self.path}", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.state["stopped"] = True
        self._wake.set()
        with self._lock:
            pass
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=30)

    def status(self) -> dict:
        return {**self.state, "ago": int(time.time() - self.state["last"]) if self.state["last"] else None}


class S3Backup(Mirror):
    """A copy of a memory in an S3 or R2 bucket (an Encrypted one's encrypted files, an Open one's readable files), kept up to date a few seconds after each change. One way
    only (a backup): the copy is at BUCKET/NAME/current, and every file it replaces or removes is kept under
    BUCKET/NAME/history/DATE, so older versions can be brought back. Any file size works."""

    def __init__(self, conn: dict, path: str, folder: Path, watch=None):
        super().__init__(conn, path.strip("/"), folder, Path(), watch)

    def sync_once(self) -> None:
        with self._lock:
            _run(self.conn, "sync", str(self.folder), _remote(f"{self.path}/current"),
                 "--backup-dir", _remote(f"{self.path}/history/{time.strftime('%Y-%m-%d %H.%M.%S')}"),
                 *SKIP, "--exclude", ".github/**", "--exclude", ".gitignore", "--exclude", ".gitattributes",
                 "--exclude", ".encryptor-*", "--transfers", "4", timeout=24 * 3600)
            self.state.update(last=time.time(), error="")
