"""For the tests that talk to the AI door: a key with read and edit, made the way the app makes one (a page that
unlocked a memory asks Settings › AI apps for it). The memory is left as it was found (locked or open)."""
import json
import os
import urllib.error
import urllib.request

import httpx2

BASE = "http://127.0.0.1:" + os.environ.get("PM_TEST_PORT", "8796")
_key = None


def _call(action, body, pw=None):
    req = urllib.request.Request(f"{BASE}/api/{action}", json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-App-Pass": pw} if pw else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


def key() -> str:
    global _key
    if _key is None:
        fid = _call("folders", {})["folders"][0]["id"]
        was_open = _call("folders", {})["folders"][0]["open"]
        pw = _call("unlock", {"password": "12345678", "folder": fid})["pass"]
        _key = _call("aiappadd", {"name": "Test AI", "kind": "other", "folders": "all", "write": True, "folder": fid}, pw)["key"]
        if not was_open:
            _call("lock", {"folder": fid}, pw)
    return _key


def client() -> httpx2.AsyncClient:
    return httpx2.AsyncClient(headers={"Authorization": f"Bearer {key()}"})
