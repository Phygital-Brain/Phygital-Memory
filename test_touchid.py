"""Touch ID unlock, Touch ID for an AI app's Allow, and the sealed approvals list, against a running test server
(PM_TEST_PORT) started with PHYGITAL_MEMORY_TOUCHID=testing/fake-touchid.sh, FAKE_TOUCHID_DIR and a test
PHYGITAL_MEMORY_SEAL_KEYCHAIN. Run make_test_vault.py --fresh first.

Run: PM_TEST_PORT=8796 FAKE_TOUCHID_DIR=... PM_TEST_STATE=... uv run python test_touchid.py
"""
import base64
import hashlib
import json
import os
import secrets
import urllib.parse
from pathlib import Path

D = Path(os.environ["FAKE_TOUCHID_DIR"])
(D / "answer").write_text("yes")
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:" + os.environ.get("PM_TEST_PORT", "8796")
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def http(method, path, body=None, headers=None, form=False):
    data = None
    h = dict(headers or {})
    if body is not None:
        data = urllib.parse.urlencode(body).encode() if form else json.dumps(body).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    req = urllib.request.Request(BASE + path, data, method=method, headers=h)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=60) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()


def api(action, body=None, pw=None, folder=None):
    b = dict(body or {}, **({"folder": folder} if folder else {}))
    code, _, raw = http("POST", f"/api/{action}", b, {"X-App-Pass": pw} if pw else None)
    return code, json.loads(raw or b"{}")



STATE = Path(os.environ["PM_TEST_STATE"])
finger = lambda yes: (D / "answer").write_text("yes" if yes else "no")
print("---- Touch ID ----")

code, j = api("folders")
fid = j["folders"][0]["id"]
code, j = api("unlock", {"password": "12345678"}, folder=fid)
P = j["pass"]

code, j = api("touchidinfo", folder=fid)
check(code == 200 and j == {"available": True, "on": False}, "Touch ID is there, not on yet", j)
code, j = api("touchid", {"on": True, "password": "wrong"}, P, fid)
check(code == 403 and not (D / f"kept-{fid}").exists(), "turning it on needs the right password", j)
code, j = api("touchid", {"on": True, "password": "12345678"})
check(code == 423, "turning it on needs a page that unlocked the memory")
code, j = api("touchid", {"on": True, "password": "12345678"}, P, fid)
check(code == 200 and j["on"] and (D / f"kept-{fid}").read_text() == "12345678", "on: the password is kept by the helper", j)

api("lock", {}, P, fid)
finger(False)
code, j = api("touchidunlock", folder=fid)
check(code == 403 and "pass" not in j, "no finger, no unlock", j)
finger(True)
code, j = api("touchidunlock", folder=fid)
check(code == 200 and j.get("pass") and j.get("open"), "a finger unlocks it", j)
P = j["pass"]
check((D / "asked").read_text().splitlines()[-1] == "unlock", "the ask uses the fixed unlock wording")

(D / f"kept-{fid}").write_text("old-password")   # the password changed since
api("lock", {}, P, fid)
code, j = api("touchidunlock", folder=fid)
check(code == 403 and not (D / f"kept-{fid}").exists(), "a kept password that no longer works is forgotten", j)
code, j = api("unlock", {"password": "12345678"}, folder=fid)
P = j["pass"]
api("touchid", {"on": True, "password": "12345678"}, P, fid)
code, j = api("touchid", {"on": False}, P, fid)
check(code == 200 and not j["on"] and not (D / f"kept-{fid}").exists(), "off: the kept password is gone")

# pressed Touch ID before it was set up: the next password unlock turns it on
api("lock", {}, P, fid)
code, j = api("unlock", {"password": "12345678", "touchid": True}, folder=fid)
P = j["pass"]
check(code == 200 and (D / f"kept-{fid}").read_text() == "12345678", "the first password after pressing Touch ID turns it on")
api("lock", {}, P, fid)
code, j = api("unlock", {"password": "wrong", "touchid": True}, folder=fid)
check(code != 200, "a wrong password turns nothing on")
code, j = api("unlock", {"password": "12345678"}, folder=fid)
P = j["pass"]
api("touchid", {"on": False}, P, fid)
code, j = api("unlock", {"password": "12345678"}, folder=fid)
check(not (D / f"kept-{fid}").exists(), "a plain password unlock doesn't turn it on")

# ---- an AI app's Allow needs the finger too ----
code, _, raw = http("POST", "/register", {"redirect_uris": ["http://127.0.0.1:9/cb"], "client_name": "Finger AI",
                                          "token_endpoint_auth_method": "none",
                                          "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"]})
client = json.loads(raw)["client_id"]
challenge = base64.urlsafe_b64encode(hashlib.sha256(secrets.token_urlsafe(48).encode()).digest()).rstrip(b"=").decode()
q = urllib.parse.urlencode({"response_type": "code", "client_id": client, "redirect_uri": "http://127.0.0.1:9/cb",
                            "code_challenge": challenge, "code_challenge_method": "S256", "state": "s"})
rid = http("GET", f"/authorize?{q}")[1].get("Location", "").rsplit("/", 1)[-1]
finger(False)
code, j = api("allowanswer", {"id": rid, "allow": True, "folders": "all"}, P, fid)
check(code == 403 and json.loads(http("GET", f"/allow/{rid}/state")[2])["next"] is None, "Allow without the finger lets nobody in", j)
check((D / "asked").read_text().splitlines()[-1] == "allow", "the ask uses the fixed allow wording (not a name the AI app picked)")
finger(True)
code, j = api("allowanswer", {"id": rid, "allow": True, "folders": "all"}, P, fid)
check(code == 200 and "code=" in (json.loads(http("GET", f"/allow/{rid}/state")[2])["next"] or ""), "Allow with the finger lets it in")

# ---- the sealed list ----
code, j = api("approvals", {}, P, fid)
rows = j["approvals"]
whats = [r["what"] for r in rows]
check(code == 200 and all(r["sealed"] for r in rows), "every approval is sealed", rows[:3])
check("Let Finger AI in" in whats and "Touch ID unlock on" in whats and "Unlocked" in whats, "unlocks, Touch ID and AI apps are listed", whats)
check(any(r["what"] == "Let Finger AI in" and r["how"] == "Touch ID" and "all memories" in r["detail"] for r in rows),
      "it says how it was confirmed and what the app may reach")
check(any(r["what"] == "Unlocked" and r["how"] == "Touch ID" for r in rows), "a Touch ID unlock says so")
code, j = api("approvals")
check(code == 423, "the list needs a page that unlocked a memory")

f = STATE / "approvals.jsonl"
lines = f.read_text().splitlines()
bad = json.loads(lines[1]); bad["detail"] = "someone else"
f.write_text("\n".join([lines[0], json.dumps(bad)] + lines[2:]) + "\n")
rows = api("approvals", {}, P, fid)[1]["approvals"][::-1]
check(not rows[1]["sealed"] and rows[0]["sealed"] and rows[2]["sealed"], "a changed line shows as broken, the others stay sealed")
f.write_text("\n".join([lines[0]] + lines[2:]) + "\n")
rows = api("approvals", {}, P, fid)[1]["approvals"][::-1]
check(rows[0]["sealed"] and not rows[1]["sealed"], "a removed line breaks the one after it")

(D / "none").write_text("")
code, j = api("touchidinfo", folder=fid)
check(j == {"available": False, "on": False}, "a Mac that can't ask: no Touch ID button", j)
(D / "none").unlink()

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
