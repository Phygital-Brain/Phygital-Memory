"""Linking over the internet, with no local network discovery between the two sides: the link itself carries the
addresses and the relay (syncthing.address), so the side that pastes it dials at once. Needs internet.
 - computers: one test computer sends (Send to a computer), another receives (Receive from a computer)
 - server: a test computer sends, the Docker test server (pm-test2 on port 8814, docs/server.md) receives
Each ends with the Encrypted memory's files on the other side. Test keychain names only, removed at the end.

Run: uv run python tests/test_link_internet.py "$PWD" [computers] [server]   (from core/; default: computers)"""
import json, os, subprocess, sys, tempfile, time, urllib.request, urllib.error
from pathlib import Path
CORE = sys.argv[1]
which = sys.argv[2:] or ["computers"]
def engine(name, port):
    tmp = Path(tempfile.mkdtemp(prefix=f"pm-{name}-"))
    env = {**os.environ, "PHYGITAL_MEMORY_STATE": str(tmp / "state"), "PHYGITAL_MEMORY_PORT": str(port),
           "PHYGITAL_MEMORY_FOLDER": str(tmp / "none"), "PHYGITAL_MEMORY_OFFLINE": "1", "PHYGITAL_MEMORY_TRASH": str(tmp / "trash"),
           "PHYGITAL_MEMORY_TOUCHID": str(tmp / "no"), "PHYGITAL_MEMORY_MAC_NAME": f"Test {name}", "PHYGITAL_MEMORY_SYNCTHING_NO_LAN": "1",
           "PHYGITAL_MEMORY_SHARED_COPIES": str(tmp / "shared"), "PHYGITAL_MEMORY_SYNCTHING_HOME": str(tmp / "st")}
    for k in ("SEAL", "CLOUD", "IDENTITY", "APPROVER", "TOUCHID"):
        env[f"PHYGITAL_MEMORY_{k}_KEYCHAIN"] = f"Phygital Memory {k.lower()} PATHTEST {name}"
    for k in ("PHYGITAL_MEMORY_SHELL_TOKEN", "PHYGITAL_MEMORY_SERVER", "PHYGITAL_MEMORY_SYNCTHING_LOCAL"): env.pop(k, None)
    proc = subprocess.Popen([sys.executable, "-m", "phygital_memory.server"], env=env, cwd=CORE, stdout=open(tmp / "log", "wb"), stderr=subprocess.STDOUT)
    base = f"http://127.0.0.1:{port}"
    def api(a, b=None, pw=None):
        req = urllib.request.Request(f"{base}/api/{a}", json.dumps(b or {}).encode(), method="POST",
                                     headers={"Content-Type": "application/json", **({"X-App-Pass": pw} if pw else {})})
        try:
            with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e: return {"status": e.code, **json.loads(e.read() or b"{}")}
    for _ in range(60):
        try: urllib.request.urlopen(base + "/", timeout=1); break
        except Exception: time.sleep(0.5)
    api.proc, api.tmp = proc, tmp
    return api
def server_api():   # the Docker test server, signed in like its own page
    import http.cookiejar
    jar = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    B = "http://localhost:8814"
    def post(path, body):
        req = urllib.request.Request(B + path, json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"})
        try:
            with op.open(req, timeout=60) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e: return {"status": e.code, **json.loads(e.read() or b"{}")}
    post("/login", {"passphrase": "link test passphrase"})
    return lambda a, b=None, pw=None: post(f"/api/{a}", b or {})
def first(api):
    (api.tmp / "places").mkdir()
    f = api("createfolder", {"parent": str(api.tmp / "places"), "name": "Laptop Notes", "kind": "encrypted", "password": "laptop memory pw 1"})["folder"]
    p = api("unlock", {"folder": f["id"], "password": "laptop memory pw 1"})["pass"]
    api("save", {"folder": f["id"], "path": "Ideas/Kite.md", "text": "# Kite\n"}, p)
    api("approversetup", {"kind": "password", "password": "approver test pw 1"})
def link(a, b, label, arrived):
    t0 = time.time()
    s = a("linkstart"); print(label, "link made:", bool(s.get("link")))
    j = b("linkjoin", {"link": s["link"]}); print(label, "joined:", j.get("words") or j)
    st = {}
    while time.time() - t0 < 240:
        st = a("linkstatus")
        if st.get("state") == "asking": break
        time.sleep(3)
    print(label, f"request arrived after {int(time.time()-t0)}s:", st.get("state"), "| words match:", st.get("words") == j.get("words"))
    if st.get("state") != "asking": a("linkcancel"); b("linkcancel"); return False
    r = a("linkanswer", {"memories": [m["id"] for m in st["memories"]], "seen": st["seen"], "approverPassword": "approver test pw 1"})
    print(label, "Link pressed:", r)
    w = {}
    while time.time() - t0 < 360:
        w = b("linkwait")
        if w.get("state") in ("done", "none") or w.get("error"): break
        time.sleep(3)
    print(label, f"other side done after {int(time.time()-t0)}s:", w)
    while time.time() - t0 < 480:
        if arrived(): break
        time.sleep(5)
    ok = arrived(); print(label, f"memory files there after {int(time.time()-t0)}s:", ok); return ok
results = {}
procs = []
try:
    if "server" in which:
        a = engine("A", 8801); procs.append(a); first(a)
        srv = server_api()
        results["computer -> server (paste on server)"] = link(a, srv, "[server]",
            lambda: "masterkey" in subprocess.run(["docker", "exec", "pm-test2", "sh", "-c", "ls /data/memories/*/ 2>/dev/null"], capture_output=True, text=True).stdout)
    if "computers" in which:
        a2 = engine("C", 8802); procs.append(a2); first(a2)
        b2 = engine("D", 8803); procs.append(b2); b2("approversetup", {"kind": "password", "password": "approver test pw 2"})
        results["computer -> computer"] = link(a2, b2, "[computers]",
            lambda: any(p.name == "masterkey.cryptomator" for p in Path.home().glob("Laptop Notes*/masterkey.cryptomator")) or
                    any((x["path"] and Path(x["path"], "masterkey.cryptomator").exists()) for x in b2("folders").get("folders", [])))
finally:
    for p in procs: p.proc.terminate()
    for p in procs:
        try: p.proc.wait(timeout=15)
        except Exception: p.proc.kill()
    for name in ("A", "C", "D"):
        for k in ("seal", "cloud", "identity", "approver", "touchid"):
            while subprocess.run(["security", "delete-generic-password", "-s", f"Phygital Memory {k} PATHTEST {name}"], capture_output=True).returncode == 0: pass
print("\nRESULTS:", json.dumps(results, indent=1))
raise SystemExit(0 if results and all(results.values()) else 1)
