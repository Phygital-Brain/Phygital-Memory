"""The app's secrets (cloud passwords, the GitHub key, S3 keys, the approvals seal key) in the Keychain.

In the built app they're kept by the helper (packaging/touchid), trusted only to itself, so another program can't
read them silently the way it can read items made by the `security` tool; and the helper only answers this app's
own server. Items an older version made with `security` move over the first time they're read. Running from source
(tests, development) uses `security` as before."""
import subprocess

from . import touchid


def _helper(*args: str, secret: bytes | None = None) -> subprocess.CompletedProcess | None:
    h = touchid.bundled()
    if not h:
        return None
    try:
        return subprocess.run([str(h), *args], input=secret, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None


def _security_read(service: str, account: str | None) -> str | None:
    r = subprocess.run(["security", "find-generic-password", *(["-a", account] if account else []), "-s", service, "-w"],
                       capture_output=True, text=True)
    return r.stdout.rstrip("\n") or None if r.returncode == 0 else None


def _security_delete(service: str, account: str | None) -> None:
    subprocess.run(["security", "delete-generic-password", *(["-a", account] if account else []), "-s", service],
                   capture_output=True)


APP_ONLY = " (app only)"   # the helper's own items get their own name, so finding an older one never prompts


def save(service: str, account: str, secret: str) -> None:
    if touchid.bundled():
        r = _helper("keep", service + APP_ONLY, account, secret=secret.encode())
        if not r or r.returncode != 0:
            raise RuntimeError("Couldn't keep it in the Keychain.")
        _security_delete(service, account)   # an older copy made with `security`
        return
    # shortcut (source runs only): the secret is passed to `security` as an argument, seen by this Mac user for a moment
    subprocess.run(["security", "add-generic-password", "-U", "-a", account, "-s", service, "-w", secret],
                   capture_output=True, check=True)


def read(service: str, account: str) -> str | None:
    if touchid.bundled():
        r = _helper("read", service + APP_ONLY, account)
        if r and r.returncode == 0 and r.stdout:
            return r.stdout.decode()
        old = _security_read(service, account)   # made by an older version: move it behind the helper
        if old is not None:
            try:
                save(service, account, old)
            except RuntimeError:
                pass   # still works from the old place; it moves next time
        return old
    return _security_read(service, account)


def delete(service: str, account: str) -> None:
    if touchid.bundled():
        _helper("drop", service + APP_ONLY, account)
    _security_delete(service, account)
