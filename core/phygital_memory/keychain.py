"""The app's secrets (cloud passwords, the GitHub key, S3 keys, the approvals seal key) in the Keychain.

In the built app they're kept by the helper (packaging/touchid), trusted only to itself, so another program can't
read them silently the way it can read items made by the `security` tool; and the helper only answers this app's
own server. Items an older version made with `security` move over the first time they're read. Running from source
(tests, development) uses `security` as before."""
import subprocess
import threading
import time

from . import touchid

# What was read, kept for this run: macOS may ask the person before the helper gets an item (after an update, say),
# so the app asks once, waits for the answer, and doesn't ask again every few seconds. A "no" is kept 10 minutes.
_got: dict = {}
_refused: dict = {}
_locks: dict = {}
_guard = threading.Lock()


MESSAGE = "Sharing needs your sharing key from the Keychain, and macOS hasn't allowed it yet. Quit and reopen the app; when macOS asks, type your Mac login password and choose Always Allow."


class Refused(Exception):
    """macOS didn't let the app read an item it keeps (the person said no, or didn't answer). Not the same as the
    item missing: callers must never make a new key in its place."""


def _helper(*args: str, secret: bytes | None = None, timeout: int = 30) -> subprocess.CompletedProcess | None:
    h = touchid.bundled()
    if not h:
        return None
    try:
        return subprocess.run([str(h), *args], input=secret, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def _security_read(service: str, account: str | None) -> str | None:
    """An item made by `security`. None only when it isn't there; any other trouble is a refusal, never "missing"."""
    try:
        r = subprocess.run(["security", "find-generic-password", *(["-a", account] if account else []), "-s", service, "-w"],
                           capture_output=True, text=True, timeout=20)
    except subprocess.TimeoutExpired:
        raise Refused(MESSAGE)
    if r.returncode == 44:   # errSecItemNotFound
        return None
    if r.returncode != 0:
        raise Refused(MESSAGE)
    return r.stdout.rstrip("\n") or None


def _security_delete(service: str, account: str | None) -> None:
    subprocess.run(["security", "delete-generic-password", *(["-a", account] if account else []), "-s", service],
                   capture_output=True)


APP_ONLY = " (app only)"   # the helper's own items get their own name, so finding an older one never prompts


def save(service: str, account: str, secret: str) -> None:
    _got.pop((service, account), None)
    _refused.pop((service, account), None)
    if touchid.bundled():
        r = _helper("keep", service + APP_ONLY, account, secret=secret.encode())
        if not r or r.returncode != 0:
            raise RuntimeError("Couldn't keep it in the Keychain.")
        back = _helper("read", service + APP_ONLY, account, timeout=20)
        if back and back.returncode == 0 and back.stdout.decode() == secret:   # the new copy reads back right:
            _security_delete(service, account)   # only now does an older copy made with `security` go
        return
    # shortcut (source runs only): the secret is passed to `security` as an argument, seen by this Mac user for a moment
    subprocess.run(["security", "add-generic-password", "-U", "-a", account, "-s", service, "-w", secret],
                   capture_output=True, check=True)


def read(service: str, account: str) -> str | None:
    if not touchid.bundled():
        return _security_read(service, account)
    k = (service, account)
    with _guard:
        lock = _locks.setdefault(k, threading.Lock())
    with lock:   # one question at a time per item; others wait for its answer
        if k in _got:
            return _got[k]
        if time.time() < _refused.get(k, 0):
            raise Refused(MESSAGE)
        got = _read(service, account)
        if got is not None:
            _got[k] = got
        return got


def _read(service: str, account: str) -> str | None:
    if touchid.bundled():
        r = _helper("read", service + APP_ONLY, account, timeout=20)   # never hold the app up for long
        if r and r.returncode == 0 and r.stdout:
            return r.stdout.decode()
        missing = r is not None and r.returncode == 4 and b"-25300" in r.stderr   # simply not kept there
        if not missing:   # no answer, or the person said no: don't ask again for a while
            _refused[(service, account)] = time.time() + 600
            raise Refused(MESSAGE)
        old = _security_read(service, account)   # made by an older version: move it behind the helper
        if old is not None:
            try:
                save(service, account, old)
            except RuntimeError:
                pass   # still works from the old place; it moves next time
        return old
    return _security_read(service, account)


def delete(service: str, account: str) -> None:
    _got.pop((service, account), None)
    if touchid.bundled():
        _helper("drop", service + APP_ONLY, account)
    _security_delete(service, account)
