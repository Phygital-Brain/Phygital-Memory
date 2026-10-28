"""Signed yeses for sharing (pka.py): a password key signs one exact request; the app's own checks and Phygital Key's
independent JavaScript checker both accept it; a replay, a changed request, a changed signature and a wrong password
are refused. Run: uv run python test_pka.py   (Phygital Key's checker comes from the local copy of its repo)"""
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-pka-"))
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_TOUCHID"] = "/nonexistent"
os.environ["PHYGITAL_MEMORY_IDENTITY_KEYCHAIN"] = "Phygital Memory identity TEST pka"
from phygital_memory import pka   # noqa: E402

# Phygital Key's own checker (verifier-js/src/index.js in the Phygital Key repo). The cross-check runs only when it's set.
CHECKER = Path(os.environ["PHYGITAL_KEY_VERIFIER"]) if os.environ.get("PHYGITAL_KEY_VERIFIER") else None
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def refused(fn, code=None):
    try:
        fn()
        return False
    except pka.Refused as e:
        return code is None or str(e) == code


REQ = {"type": "share.let_in", "params": {"item": "Projects", "person": "Ana", "person_id": "0123456789abcdef",
                                          "role": "edit", "safety": "frog belong exile imminent"}}
try:
    try:
        pka.set_up_password("short")
        check(False, "a short approval password is refused")
    except ValueError:
        check(True, "a short approval password is refused")
    pka.set_up_password("a long test approval phrase")
    try:
        pka.approve(REQ, "let Ana in")
        check(False, "with a password key, approving asks for the password")
    except pka.NeedPassword:
        check(True, "with a password key, approving asks for the password")
    check(refused(lambda: pka.approve(REQ, "let Ana in", "wrong password!!")), "a wrong password is refused")
    check(refused(lambda: pka.approve(REQ, "let Ana in", "a long test approval phrase")), "and the next try waits (slowed down)")
    time.sleep(2.1)
    a = pka.approve(REQ, "let Ana in", "a long test approval phrase")
    check(a, "the right password signs this exact request")
    check(refused(lambda: pka.verify(a, REQ), "REPLAYED"), "the same yes can't be used twice")

    b = pka.approve(REQ, "let Ana in", "a long test approval phrase")
    other = {**REQ, "params": {**REQ["params"], "role": "view"}}
    check(refused(lambda: pka.verify(b, other), "REQUEST_MISMATCH"), "a yes for one request doesn't fit another")
    obj = json.loads(pka._unb64(b))
    sig = bytearray(pka._unb64(obj["signatures"][0]["signature"]))
    sig[-1] ^= 1
    obj["signatures"][0]["signature"] = pka._b64(bytes(sig))
    check(refused(lambda: pka.verify(pka._b64(json.dumps(obj).encode()), REQ)), "a changed signature is refused")

    if CHECKER is None or not CHECKER.exists():
        print("SKIP Phygital Key's own checker: set PHYGITAL_KEY_VERIFIER to its verifier-js/src/index.js")
    else:
        # Phygital Key's own checker (JavaScript, independent of this app) accepts the app's approvals as they are
        c = pka.approve(REQ, "let Ana in", "a long test approval phrase")
        pka._seen.clear()
        (tmp / "in.json").write_text(json.dumps({"approval": c, "request": REQ, "keyring": pka.keyring(), "aud": pka.aud(),
                                                 "origins": [pka.ORIGIN], "rp_ids": [pka.RP_ID]}))
        (tmp / "check.mjs").write_text(f"""
    import {{ verify, MemorySeenStore, keyringFrom }} from {json.dumps(CHECKER.as_uri())};
    import {{ readFileSync }} from "node:fs";
    const x = JSON.parse(readFileSync(process.argv[2], "utf8"));
    const now = Math.floor(Date.now() / 1000);
    const ring = keyringFrom(x.keyring);
    const cfg = {{ origins: x.origins, rp_ids: x.rp_ids }};
    const seen = new MemorySeenStore();
    const out = [];
    for (const [req, aud] of [[x.request, x.aud], [{{...x.request, params: {{...x.request.params, role: "view"}}}}, x.aud], [x.request, "someone-else"]]) {{
      const r = await verify(x.approval, {{ aud, request: req, level: "high" }}, ring, seen, cfg, now);
      out.push(r.ok ? "ok:" + r.verified.approver : r.error);
    }}
    console.log(JSON.stringify(out));
    """)
        r = subprocess.run(["node", str(tmp / "check.mjs"), str(tmp / "in.json")], capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout or "[]") if r.returncode == 0 else [r.stderr[-300:]]
        check(res[:1] == ["ok:Password"], "Phygital Key's own checker accepts the app's signed yes", res)
        check(res[1:] == ["REQUEST_MISMATCH", "WRONG_AUDIENCE"], "and refuses it for another request or audience", res)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run(["security", "delete-generic-password", "-s", "Phygital Memory identity TEST pka", "-a", "x25519"], capture_output=True)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
