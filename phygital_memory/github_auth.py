"""Sign in with GitHub, the way TV apps do it (GitHub's "device flow").

The person presses Sign in with GitHub: the app gets a short code from GitHub and opens github.com/login/device in
their browser. They type the code there and approve. The app then receives its own key, kept in the Mac's Keychain
(never in a file or a note). Nothing here talks to GitHub until the person presses the button.

The app is registered on GitHub as an OAuth app. Its Client ID is public (it isn't a password); it goes in
CLIENT_ID below, or in the PHYGITAL_MEMORY_GITHUB_CLIENT_ID setting for testing.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from . import keychain

CLIENT_ID = "Ov23liiRpMQVPucCB73y"   # the "Phygital Memory" OAuth app on GitHub (public, not a password)
SCOPE = "repo"   # needed to make and sync a private repo
KEYCHAIN = "Phygital Memory GitHub"
GITHUB = "https://github.com"
API = "https://api.github.com"


def client_id() -> str:
    return os.environ.get("PHYGITAL_MEMORY_GITHUB_CLIENT_ID") or CLIENT_ID


def _post(url: str, fields: dict) -> dict:
    req = urllib.request.Request(url, urllib.parse.urlencode(fields).encode(), method="POST",
                                 headers={"Accept": "application/json", "User-Agent": "Phygital Memory"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def api(path: str, token: str | None = None, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    token = token or saved_token()
    req = urllib.request.Request(f"{API}{path}", json.dumps(body).encode() if body is not None else None, method=method,
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "Phygital Memory",
                                          **({"Authorization": f"Bearer {token}"} if token else {}),
                                          **({"Content-Type": "application/json"} if body is not None else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}


# ---------- the key, in the Keychain ----------

def saved_token() -> str | None:
    if os.environ.get("PHYGITAL_MEMORY_OFFLINE"):   # tests: never use the person's real GitHub sign-in
        return None
    return (keychain.read(KEYCHAIN, "github") or "").strip() or None


def _save_token(token: str) -> None:
    keychain.save(KEYCHAIN, "github", token)


def sign_out() -> None:
    keychain.delete(KEYCHAIN, "github")


# ---------- the sign-in itself ----------

def start() -> dict:
    """Step 1: a code for the person to type on github.com. Returns {code, url, device, interval, expires}."""
    if not client_id():
        raise RuntimeError("Sign in with GitHub isn't set up in this test version yet (no Client ID).")
    d = _post(f"{GITHUB}/login/device/code", {"client_id": client_id(), "scope": SCOPE})
    if "device_code" not in d:
        raise RuntimeError(d.get("error_description") or "GitHub didn't give a sign-in code. Try again.")
    return {"code": d["user_code"], "url": d.get("verification_uri", f"{GITHUB}/login/device"),
            "device": d["device_code"], "interval": int(d.get("interval", 5)), "expires": int(d.get("expires_in", 900))}


def finish(device: str) -> dict:
    """Step 2, asked every few seconds: {"state": "waiting" | "slow" | "done" | "denied" | "expired", account}."""
    d = _post(f"{GITHUB}/login/oauth/access_token",
              {"client_id": client_id(), "device_code": device,
               "grant_type": "urn:ietf:params:oauth:grant-type:device_code"})
    if d.get("access_token"):
        _save_token(d["access_token"])
        return {"state": "done", "account": account()}
    err = d.get("error", "")
    return {"state": {"authorization_pending": "waiting", "slow_down": "slow", "access_denied": "denied",
                      "expired_token": "expired"}.get(err, "waiting" if not err else "denied")}


def account() -> str | None:
    """The signed-in GitHub account (asks GitHub), or None."""
    token = saved_token()
    if not token:
        return None
    code, user = api("/user", token)
    return user.get("login") if code == 200 else None
