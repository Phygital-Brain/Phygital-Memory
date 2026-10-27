"""Sharing with no cloud: two app copies on this Mac (Max on 8796, Ana on 8799), each with its own private Syncthing,
talking only on 127.0.0.1 (no discovery, relays or internet). Max invites, Ana's app connects with the invite,
the encrypted files come over, Ana asks, both see the same safety code, Max lets her in, Ana opens with her own key,
edits go both ways, and once removed Ana's computer gets no more changes.

Run: uv run python test_syncthing_share.py   (needs a fresh test folder: make_test_vault.py --fresh)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-st-"))
ROOT = Path(__file__).parent
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def server(port, state, folder, who):
    env = {**os.environ, "PHYGITAL_MEMORY_STATE": str(state), "PHYGITAL_MEMORY_MOUNTS": str(state / "mounts"),
           "PHYGITAL_MEMORY_FOLDER": str(folder), "PHYGITAL_MEMORY_PORT": str(port), "PHYGITAL_MEMORY_OFFLINE": "1",
           "PHYGITAL_MEMORY_SYNCTHING_LOCAL": "1", "PHYGITAL_MEMORY_TOUCHID": "/nonexistent",
           "PHYGITAL_MEMORY_CLOUD_KEYCHAIN": "Phygital Memory cloud TEST",
           "PHYGITAL_MEMORY_SEAL_KEYCHAIN": f"Phygital Memory seal TEST {who}",
           "PHYGITAL_MEMORY_IDENTITY_KEYCHAIN": f"Phygital Memory identity TEST {who}"}
    return subprocess.Popen([sys.executable, "-m", "phygital_memory.server"], env=env, cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def api(port, action, body=None, pw=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/{action}", json.dumps(body or {}).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-App-Pass": pw} if pw else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"status": e.code, **json.loads(e.read() or b"{}")}


def wait(cond, secs=60):
    end = time.time() + secs
    while time.time() < end:
        try:
            if cond():
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


A, B = 8796, 8799
procs = [server(A, tmp / "max", ROOT.parent / "locked-notes", "A"), server(B, tmp / "ana", tmp / "none", "B")]
try:
    for port in (A, B):
        wait(lambda: urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1), 30)
    fa = api(A, "folders")["folders"][0]["id"]
    pa = api(A, "unlock", {"password": "12345678", "folder": fa})["pass"]
    api(A, "myname", {"name": "Max", "folder": fa})
    inv = api(A, "shareinvite", {"role": "edit", "folder": fa}, pa)
    link = inv.get("link", "")
    check("&d=" in link and "Syncthing" in inv.get("place", ""), "the invite carries Max's Syncthing ID, no cloud", inv)

    (tmp / "AnaMac").mkdir()
    j = api(B, "joinshared", {"link": link, "parent": str(tmp / "AnaMac")})
    fb = j.get("folder", {}).get("id")
    check(j.get("syncthing") and fb, "Ana's app joins over Syncthing", j)
    api(B, "myname", {"name": "Ana", "folder": fb})
    target = tmp / "AnaMac" / "locked-notes"
    check(wait(lambda: (target / "vault.cryptomator").exists(), 90), "the encrypted files arrive on Ana's side")
    check(not any(p.suffix == ".md" and p.name not in ("AGENTS.md", "CLAUDE.md") for p in target.rglob("*")), "only encrypted files came over (no readable notes)")

    w = api(B, "keyunlock", {"folder": fb})
    check(w.get("waiting") and w.get("safety"), "Ana waits for Max, and sees a safety code", w)
    reqs = []
    check(wait(lambda: reqs.extend(api(A, "sharerequests", {"folder": fa}, pa)["requests"]) or reqs, 60),
          "Max's app sees Ana asking")
    r = reqs[0] if reqs else {}
    check(r.get("safety") == w.get("safety"), "both see the same safety code", (r.get("safety"), w.get("safety")))
    api(A, "shareanswer", {"id": r.get("id"), "allow": True, "folder": fa}, pa)

    got = {}
    check(wait(lambda: got.update(api(B, "keyunlock", {"folder": fb})) or got.get("pass"), 60), "Ana opens it with her own key", got)
    pb = got.get("pass")
    api(B, "save", {"path": "From Ana.md", "text": "# From Ana\nover Syncthing\n", "new": True, "folder": fb}, pb)
    check(wait(lambda: any(x["path"] == "From Ana.md" for x in api(A, "files", {"folder": fa}, pa)["files"]), 60),
          "Ana's note reaches Max")
    api(A, "save", {"path": "From Max.md", "text": "# From Max\n", "new": True, "folder": fa}, pa)
    check(wait(lambda: any(x["path"] == "From Max.md" for x in api(B, "files", {"folder": fb}, pb)["files"]), 60),
          "and Max's reaches Ana")

    members = api(A, "shareinfo", {"folder": fa}, pa)["members"]
    ana = next(m for m in members if m["name"] == "Ana")
    check(ana.get("role") == "edit", "Ana is on Max's list by the name she chose", members)
    api(A, "shareremove", {"id": ana["id"], "folder": fa}, pa)
    time.sleep(3)
    api(A, "save", {"path": "After removing.md", "text": "# Not for Ana\n", "new": True, "folder": fa}, pa)
    time.sleep(10)
    check(not any("After removing" in p.name for p in target.rglob("*")) and
          not any(x["path"] == "After removing.md" for x in api(B, "files", {"folder": fb}, pb)["files"]),
          "once removed, Ana's computer gets no more changes")
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        try:
            p.wait(timeout=15)
        except Exception:
            p.kill()
    subprocess.run(["pkill", "-f", f"syncthing serve --home={tmp}"], capture_output=True)
    for who in ("A", "B"):
        for svc, acct in ((f"Phygital Memory identity TEST {who}", "x25519"), (f"Phygital Memory seal TEST {who}", "seal")):
            subprocess.run(["security", "delete-generic-password", "-s", svc, "-a", acct], capture_output=True)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
