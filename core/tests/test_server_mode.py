"""Server mode (docs/server.md), from the outside: the first visit chooses the passphrase (with the setup code from
the log), then the page needs it, other sites and other addresses are
refused, a new memory goes in the server's memories folder, and an AI app with a key searches it through Engram,
reads, and can't write until edits are allowed. Then the AI sign-in page asks for the login before it shows Allow.
Throwaway folders, its own port, secrets in the server's own file (never the Keychain).

Run: uv run python tests/test_server_mode.py
"""
import asyncio
import http.cookiejar
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

PORT = int(os.environ.get("PM_SERVER_TEST_PORT", "8812"))
BASE = f"http://localhost:{PORT}"
PASSPHRASE = "server test passphrase"
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


jar = http.cookiejar.CookieJar()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), NoRedirect)


def http(method, path, body=None, headers=None, signed_in=True):
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(BASE + path, None if body is None else json.dumps(body).encode(), method=method, headers=h)
    o = opener if signed_in else urllib.request.build_opener(NoRedirect)
    try:
        with o.open(req, timeout=60) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()


def api(action, body=None, pw=None, **kw):
    code, _, raw = http("POST", f"/api/{action}", body or {}, {"X-App-Pass": pw} if pw else None, **kw)
    try:
        return code, json.loads(raw or b"{}")
    except ValueError:
        return code, {}


async def ai(token, steps):
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as client:
        async with streamable_http_client(f"{BASE}/mcp", http_client=client) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                out = {"tools": sorted(t.name for t in (await s.list_tools()).tools)}
                for name, args in steps:
                    res = await s.call_tool(name, args)
                    out[name] = ("ERROR " if res.is_error else "") + "\n".join(c.text for c in res.content if hasattr(c, "text"))
                return out


tmp = Path(tempfile.mkdtemp(prefix="pm-server-"))
env = {**os.environ, "PHYGITAL_MEMORY_SERVER": "1", "PHYGITAL_MEMORY_URL": BASE,
       "PHYGITAL_MEMORY_DATA": str(tmp / "data"), "PHYGITAL_MEMORY_STATE": str(tmp / "state"),
       "PHYGITAL_MEMORY_PORT": str(PORT), "PHYGITAL_MEMORY_OFFLINE": "1", "PHYGITAL_MEMORY_SYNCTHING_LOCAL": "1",
       "PHYGITAL_MEMORY_TRASH": str(tmp / "trash"), "PHYGITAL_MEMORY_VERSION": "0.0.0-test"}
env.pop("PHYGITAL_MEMORY_SHELL_TOKEN", None)
env.pop("PHYGITAL_MEMORY_PASSPHRASE", None)
core = Path(__file__).resolve().parent.parent
log = open(tmp / "engine.log", "wb")
proc = subprocess.Popen([sys.executable, "-m", "phygital_memory.server"], env=env, cwd=core, stdout=log, stderr=subprocess.STDOUT)
said = lambda: (tmp / "engine.log").read_text(encoding="utf-8", errors="replace")[-3000:]
try:
    up = False
    for _ in range(120):
        try:
            code, _, _ = http("GET", "/login", signed_in=False)
            up = code == 200
            if up:
                break
        except Exception:
            pass
        if proc.poll() is not None:
            break
        time.sleep(0.5)
    check(up, "the server starts and shows its login page", said() if not up else "")
    if not up:
        raise SystemExit(1)

    # ---- the first visit: choose the passphrase ----
    code, _, raw = http("GET", "/login", signed_in=False)
    check(b"Setup code" in raw, "the first visit asks for the setup code and a new passphrase")
    keep = (tmp / "state" / "setup-code").read_text() if (tmp / "state" / "setup-code").exists() else ""
    check(len(keep) == 14, "the setup code is kept so a restart doesn't change it")
    import re
    found = re.search(r"Setup code: ([0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4})", said())
    check(bool(found), "the setup code is in the server's log", said()[-300:])
    code, _, raw = http("POST", "/setup", {"code": "0000-0000-0000", "passphrase": PASSPHRASE}, signed_in=False)
    check(code == 400 and b"setup code" in raw, "a wrong setup code is refused", raw)
    code, _, raw = http("POST", "/setup", {"code": found.group(1) if found else "", "passphrase": "short"}, signed_in=False)
    check(code == 400 and b"12 characters" in raw, "a short passphrase is refused", raw)
    typed = (found.group(1) if found else "").upper().replace("-", " ")   # as someone might type it
    code, _, raw = http("POST", "/setup", {"code": typed, "passphrase": PASSPHRASE}, signed_in=False)
    check(code == 200, "the right code sets the passphrase (capitals and spaces are fine)", raw)
    check(not (tmp / "state" / "setup-code").exists(), "the setup code is gone once used")
    saved = (tmp / "state" / "passphrase.json")
    check(saved.exists() and PASSPHRASE not in saved.read_text() and oct(saved.stat().st_mode)[-3:] == "600",
          "only its fingerprint is kept, readable by the server only")
    code, _, raw = http("POST", "/setup", {"code": found.group(1) if found else "", "passphrase": "another passphrase 2"}, signed_in=False)
    check(code == 400, "nobody can set it a second time", raw)
    code, _, raw = http("GET", "/login", signed_in=False)
    check(b"Setup code" not in raw and b"Passphrase" in raw, "from then on the page asks for the passphrase")

    # ---- the door ----
    code, hdrs, _ = http("GET", "/", signed_in=False)
    check(code == 303 and hdrs.get("Location", "").endswith("/login"), "the page sends you to the login first", code)
    code, _ = api("folders", signed_in=False)
    check(code == 403, "the app's calls are refused without a login", code)
    code, _, raw = http("POST", "/login", {"passphrase": "wrong one"})
    check(code == 403, "a wrong passphrase is refused", code)
    code, _, raw = http("POST", "/login", {"passphrase": PASSPHRASE}, {"Origin": "https://evil.example"})
    check(code == 403, "a login sent from another site is refused", code)
    code, _, raw = http("POST", "/login", {"passphrase": PASSPHRASE, "next": "//evil.example"})
    check(code == 200 and json.loads(raw)["next"] == "/", "the right passphrase signs in, and never sends you off-site", raw)
    cookie = next((c for c in jar if c.name == "pm_session"), None)
    check(cookie is not None and cookie.has_nonstandard_attr("HttpOnly"), "the login is an HttpOnly cookie")
    code, _, raw = http("GET", "/")
    check(code == 200 and b'data-server="1"' in raw, "signed in, the page opens and knows it's on a server", code)
    code, _, _ = http("POST", "/api/folders", {}, {"Origin": "https://evil.example"})
    check(code == 403, "a signed-in browser's calls from another site are refused", code)
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/", headers={})
    try:
        code = opener.open(req, timeout=10).status
    except urllib.error.HTTPError as e:
        code = e.code
    check(code == 421, "another address for the same server is refused", code)
    code, j = api("serverinfo")
    check(j.get("server") is True and j.get("version") == "0.0.0-test", "the page learns it's a server, and its version", j)

    # ---- a memory on the server ----
    code, j = api("places")
    home = j.get("home", "")
    check(j.get("places") == [] and home == str(tmp / "data" / "memories"), "new memories go in the server's memories folder", j)
    code, j = api("pickfolder", {})
    check(j.get("path") == home, "choosing a place gives that folder (no file chooser on a server)", j)
    code, j = api("createfolder", {"parent": home, "name": "Work", "kind": "encrypted", "password": "server memory pw 1"})
    f = j.get("folder", {})
    check(f.get("kind") == "encrypted" and Path(home, "Work", "masterkey.cryptomator").exists(), "an Encrypted memory is made there", j)
    code, j = api("unlock", {"folder": f.get("id"), "password": "server memory pw 1"})
    P = j.get("pass")
    check(bool(P), "it unlocks on the page", j)
    api("save", {"folder": f.get("id"), "path": "Projects/Lighthouse.md", "text": "# Lighthouse\nThe blue lighthouse repaint is due in May.\n"}, P)

    # ---- an AI app ----
    code, j = api("aiappadd", {"name": "Phone", "kind": "other", "folders": "all", "write": False}, P)
    key = j.get("key", "")
    check(key and j.get("door") == f"{BASE}/mcp", "a key for an AI app, with the server's own address", j)
    out = asyncio.run(ai(key, [("search_notes", {"question": "when is the lighthouse repaint"}),
                               ("create_note", {"path": "Daily/x.md", "text": "hi"})]))
    check(len(out["tools"]) >= 17, "the AI app sees the tools", out["tools"])
    check("Lighthouse" in out["search_notes"] and not out["search_notes"].startswith("ERROR"), "search finds the note (Engram)", out["search_notes"][:300])
    check(out["create_note"].startswith("ERROR"), "a read-only app can't write", out["create_note"][:200])

    # ---- secrets stay in the server's own file ----
    sec = tmp / "state" / "secrets.json"
    if sec.exists():
        check(oct(sec.stat().st_mode)[-3:] == "600", "the secrets file is readable by the server only", oct(sec.stat().st_mode))

    # ---- an AI app signing in (OAuth): the page asks for the login first ----
    code, _, raw = http("POST", "/register", {"client_name": "Test AI", "redirect_uris": ["http://localhost:9/cb"],
                                             "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"],
                                             "token_endpoint_auth_method": "none"})
    cid = json.loads(raw).get("client_id", "") if code in (200, 201) else ""
    check(bool(cid), "an AI app can register", raw[:200])
    q = urllib.parse.urlencode({"response_type": "code", "client_id": cid, "redirect_uri": "http://localhost:9/cb",
                                "code_challenge": "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM", "code_challenge_method": "S256",
                                "state": "s1", "scope": "notes:read"})
    code, hdrs, _ = http("GET", f"/authorize?{q}", signed_in=False)
    allow = hdrs.get("Location", "")
    check(code in (302, 307) and "/allow/" in allow, "sign-in sends the AI app's browser to the Allow page", (code, allow))
    path = allow.replace(BASE, "")
    code, hdrs, _ = http("GET", path, signed_in=False)
    check(code == 303 and "/login?next=" in hdrs.get("Location", ""), "the Allow page asks for the login first", code)
    code, _, raw = http("POST", path + "/answer", {"allow": True}, signed_in=False)
    check(code == 403, "nobody can answer it without the login", code)
    code, _, raw = http("GET", path)
    check(code == 200 and b"Test AI" in raw, "signed in, it shows which app asks", code)
    code, _, raw = http("POST", path + "/answer", {"allow": True})
    check(code == 200, "Allow works on the page", raw)
    code, _, raw = http("GET", path + "/state")
    check("code=" in json.loads(raw).get("next", ""), "and the AI app's browser goes back with a sign-in code", raw)

    code, _, _ = http("POST", "/logout", {})
    code2, _ = api("folders")
    check(code == 200 and code2 == 403, "signing out ends the login")
finally:
    proc.terminate()
    if not all(ok):
        print(said())
    try:
        proc.wait(timeout=15)
    except Exception:
        proc.kill()

print(f"\n{sum(ok)} of {len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
