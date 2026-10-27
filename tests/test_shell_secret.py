"""When the Mac app runs the server (PHYGITAL_MEMORY_SHELL_TOKEN set), only its own windows may use /api and /upload,
and /shell/hello proves the server is the app's own. Starts its own server on port 8799 with a test state.

Run: uv run python test_shell_secret.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

tmp = tempfile.mkdtemp(prefix="pm-shell-")
env = {**os.environ, "PHYGITAL_MEMORY_STATE": tmp, "PHYGITAL_MEMORY_OFFLINE": "1", "PHYGITAL_MEMORY_PORT": "8799",
       "PHYGITAL_MEMORY_FOLDER": os.path.join(tmp, "none"), "PHYGITAL_MEMORY_SHELL_TOKEN": "page-secret-1",
       "PHYGITAL_MEMORY_SERVER_PROOF": "proof-2", "PHYGITAL_MEMORY_TOUCHID": "/nonexistent"}
server = subprocess.Popen([sys.executable, "-m", "phygital_memory.server"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def post(path, body=b"{}", headers=None, ctype="application/json"):
    req = urllib.request.Request("http://127.0.0.1:8799" + path, body, method="POST", headers={"Content-Type": ctype, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


try:
    for _ in range(100):
        try:
            urllib.request.urlopen("http://127.0.0.1:8799/", timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    check(post("/api/folders")[0] == 403, "without the page secret, /api is refused")
    check(post("/api/touchidunlock")[0] == 403, "so is a Touch ID unlock from another program")
    check(post("/upload?folder=x&path=a.txt", b"x", ctype="application/octet-stream")[0] == 403, "and /upload")
    code, raw = post("/api/folders", headers={"X-Shell-Token": "page-secret-1"})
    check(code == 200 and "folders" in json.loads(raw), "with it, /api works")
    check(post("/api/folders", headers={"X-Shell-Token": "wrong"})[0] == 403, "a wrong secret is refused")
    code, raw = post("/shell/hello", headers={"X-Shell-Token": "page-secret-1"})
    check(code == 200 and json.loads(raw)["proof"] == "proof-2", "the server proves it's the app's own")
    check(post("/shell/hello")[0] == 403, "and tells nobody else")
finally:
    server.terminate()
print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
