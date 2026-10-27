"""Closing the app: the question, Keep open (remembered 72 hours), and Lock all.

Needs a test server started with PHYGITAL_MEMORY_SHELL_TOKEN=tok-test and ST=<its PHYGITAL_MEMORY_STATE folder>.
Run: ST=<state> PM_TEST_PORT=8796 uv run python test_close.py
"""
import json, os, urllib.request, urllib.error
B = "http://127.0.0.1:" + os.environ.get("PM_TEST_PORT", "8796"); T = "tok-test"
def post(path, body=None, h=None):
    r = urllib.request.Request(B + path, json.dumps(body or {}).encode(), method="POST", headers={"Content-Type": "application/json", **(h or {})})
    try:
        with urllib.request.urlopen(r) as x: return json.loads(x.read())
    except urllib.error.HTTPError as e: return json.loads(e.read() or b"{}")
sh = lambda a: post("/shell/" + a, h={"x-shell-token": T})
fid = post("/api/folders")["folders"][0]["id"]
pw = post("/api/unlock", {"password": "12345678", "folder": fid})["pass"]
api = lambda a, b=None: post("/api/" + a, {**(b or {}), "folder": fid}, {"X-App-Pass": pw})
ok = []
def check(c, what): ok.append(c); print(("PASS " if c else "FAIL ") + what)
r = sh("close"); check(r.get("ask") is True, "closing with a folder open asks")
check(api("closestate").get("asked") is True, "the page sees the question")
api("closeanswer", {"keep": 1}); check(sh("answer").get("answer") == {"keep": 1}, "Keep open is the answer")
check(api("status").get("open") is True, "Keep open: the folder stays unlocked")
state = os.environ["ST"]
check(os.path.exists(state + "/close.json"), "Keep open is saved")
sh("reopen"); r = sh("close"); check(r.get("ask") is False and r.get("keep") is True, "closing again within 72 h doesn't ask")
os.remove(state + "/close.json"); sh("reopen")
r = sh("close"); check(r.get("ask") is True, "after 72 h (file gone) it asks again")
api("closeanswer", {"keep": 0}); check(sh("should-exit").get("exit") is True, "Lock all: the app may quit")
check(post("/api/status", {"folder": fid}, {"X-App-Pass": pw}).get("open") is not True, "Lock all: the folder is locked")
print(f"{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
