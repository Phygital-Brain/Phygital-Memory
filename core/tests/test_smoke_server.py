"""The built engine on this computer (Mac, Windows or Linux), from the outside: it starts, makes an Open memory and an
Encrypted one, writes, reads, searches, locks and unlocks (a wrong password is refused), builds the brain skeleton,
gives the AI a task, and its AI door (MCP) answers. Throwaway folders, its own port, test names everywhere.

Run: uv run python test_smoke_server.py [path to the built phygital-memory-server]
     (with no path it runs the engine from source)
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

PORT = 8796 if os.environ.get("PM_SMOKE_PORT") is None else int(os.environ["PM_SMOKE_PORT"])
BASE = f"http://127.0.0.1:{PORT}"
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def api(action, body=None, pw=None):
    req = urllib.request.Request(f"{BASE}/api/{action}", json.dumps(body or {}).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-App-Pass": pw} if pw else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"status": e.code, **json.loads(e.read() or b"{}")}


tmp = Path(tempfile.mkdtemp(prefix="pm-smoke-"))
env = {**os.environ, "PHYGITAL_MEMORY_STATE": str(tmp / "state"), "PHYGITAL_MEMORY_PORT": str(PORT),
       "PHYGITAL_MEMORY_FOLDER": str(tmp / "none"), "PHYGITAL_MEMORY_OFFLINE": "1", "OFFLINE": "1",
       "PHYGITAL_MEMORY_SYNCTHING_LOCAL": "1", "PHYGITAL_MEMORY_TOUCHID": str(tmp / "no-touchid"),
       "PHYGITAL_MEMORY_SHARED_COPIES": str(tmp / "shared"), "PHYGITAL_MEMORY_TRASH": str(tmp / "trash"),
       "PHYGITAL_MEMORY_SEAL_KEYCHAIN": "Phygital Memory seal SMOKE", "PHYGITAL_MEMORY_CLOUD_KEYCHAIN": "Phygital Memory cloud SMOKE",
       "PHYGITAL_MEMORY_IDENTITY_KEYCHAIN": "Phygital Memory identity SMOKE", "PHYGITAL_MEMORY_APPROVER_KEYCHAIN": "Phygital Memory approver SMOKE",
       "PHYGITAL_MEMORY_TOUCHID_KEYCHAIN": "Phygital Memory Touch ID SMOKE"}
env.pop("PHYGITAL_MEMORY_SHELL_TOKEN", None)
cmd = [str(Path(sys.argv[1]).resolve())] if len(sys.argv) > 1 else [sys.executable, "-m", "phygital_memory.server"]
core = Path(__file__).resolve().parent.parent
log = open(tmp / "engine.log", "wb")   # a file, not a pipe: a full pipe would stall the engine
proc = subprocess.Popen(cmd, env=env, cwd=core, stdout=log, stderr=subprocess.STDOUT)
said = lambda: (tmp / "engine.log").read_text(encoding="utf-8", errors="replace")[-3000:]
try:
    up = False
    for _ in range(120):
        try:
            urllib.request.urlopen(f"{BASE}/", timeout=1)
            up = True
            break
        except Exception:
            if proc.poll() is not None:
                break
            time.sleep(0.5)
    check(up, "the engine starts and its page answers", said() if not up else "")
    if not up:
        raise SystemExit(1)

    (tmp / "places").mkdir()
    o = api("createfolder", {"parent": str(tmp / "places"), "name": "Open Notes", "kind": "open"}).get("folder", {})
    check(o.get("kind") == "open", "an Open memory is made", o)
    r = api("unlock", {"folder": o.get("id"), "password": ""})
    po = r.get("pass")
    check(bool(po), "it opens with no password", r)
    if not po:
        raise SystemExit(1)
    api("save", {"folder": o.get("id"), "path": "Projects/Kite.md", "text": "# Kite\nthe orange kite festival\n"}, po)
    check((tmp / "places" / "Open Notes" / "Projects" / "Kite.md").read_text(encoding="utf-8").endswith("festival\n"),
          "a note is a normal file on disk")
    check(api("read", {"folder": o.get("id"), "path": "Projects/Kite.md"}, po).get("text", "").startswith("# Kite"), "it reads back")
    hits = api("search", {"folder": o.get("id"), "q": "orange kite"}, po)
    check(any("Kite" in json.dumps(r) for r in hits.get("results", hits.get("rows", []))), "search finds it", hits)
    built = api("brainbuild", {"folder": o.get("id"), "picks": {"work": True, "pages": {"me": {"desc": "Who Ana is.", "tags": ["working-style"], "body": "Ana\n"}}}, "lang": "en", "name": "Ana", "tz": "UTC"}, po)
    check(not built.get("error") and (tmp / "places" / "Open Notes" / "CLAUDE.md").is_file(), "the brain skeleton builds", built.get("error"))
    task = api("handtoai", {"folder": o.get("id"), "path": "Projects/Kite.md", "ask": "add a budget"}, po)
    check(any(i.get("ask") == "add a budget" for i in task.get("todo", [])), "an AI task is given", task)

    e = api("createfolder", {"parent": str(tmp / "places"), "name": "Locked Notes", "password": "smoke test password 1"}).get("folder", {})
    check(e.get("kind") == "encrypted", "an Encrypted memory is made", e)
    r = api("unlock", {"folder": e.get("id"), "password": "smoke test password 1"})
    pe = r.get("pass")
    check(bool(pe), "it unlocks with its password", r)
    if not pe:
        raise SystemExit(1)
    api("save", {"folder": e.get("id"), "path": "Secret.md", "text": "# Secret\nthe blue lighthouse\n"}, pe)
    raw = b"".join(p.read_bytes() for p in (tmp / "places" / "Locked Notes").rglob("*") if p.is_file())
    check(b"blue lighthouse" not in raw, "nothing readable on disk")
    api("lock", {"folder": e.get("id")}, pe)
    check(api("read", {"folder": e.get("id"), "path": "Secret.md"}, pe).get("status") == 423, "locked, it can't be read")
    check(api("unlock", {"folder": e.get("id"), "password": "wrong password here"}).get("status") in (400, 401, 403),
          "a wrong password is refused")
    pe = api("unlock", {"folder": e.get("id"), "password": "smoke test password 1"}).get("pass")
    check(api("read", {"folder": e.get("id"), "path": "Secret.md"}, pe).get("text", "").startswith("# Secret"), "unlocked again, it reads back")

    try:
        req = urllib.request.Request(f"{BASE}/mcp", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "smoke", "version": "1"}}}).encode(),
            method="POST", headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
        code = urllib.request.urlopen(req, timeout=20).status
    except urllib.error.HTTPError as x:
        code = x.code
    except Exception:
        code = 0
    check(code in (200, 401), "the AI door (MCP) answers", code)
finally:
    proc.terminate()
    if not all(ok):   # what the engine said, for the failure
        print(said())
    try:
        proc.wait(timeout=15)
    except Exception:
        proc.kill()

print(f"\n{sum(ok)} of {len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
