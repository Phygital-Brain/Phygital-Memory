"""The AI door's lock, against a running test server (PM_TEST_PORT) on a fresh test folder: no key no entry, keys
from Settings (read only, read and edit, some memories, "AI can't see this", removed), MCP sign-in with Allow in the
app, and the new tools. Run make_test_vault.py --fresh first.

Run: PM_TEST_PORT=8796 uv run python test_ai_gate.py
"""
import asyncio
import base64
import hashlib
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

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


async def ai(token, steps):
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"} if token else {}) as client:
        async with streamable_http_client(f"{BASE}/mcp", http_client=client) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                out = {"tools": sorted(t.name for t in (await s.list_tools()).tools)}
                for name, args in steps:
                    res = await s.call_tool(name, args)
                    out[name] = ("ERROR " if res.is_error else "") + "\n".join(c.text for c in res.content if hasattr(c, "text"))
                return out


def run(token, *steps):
    return asyncio.run(ai(token, list(steps)))


code, j = api("folders")
fid = j["folders"][0]["id"]
code, j = api("unlock", {"password": "12345678"}, folder=fid)
P = j["pass"]

# ---- no key, wrong key ----
code, hdrs, _ = http("POST", "/mcp", {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                     {"Accept": "application/json, text/event-stream"})
check(code == 401 and "resource_metadata" in (hdrs.get("WWW-Authenticate") or ""), "no key: refused, and told where to sign in", code)
code, _, _ = http("POST", "/mcp", {}, {"Authorization": "Bearer pm_wrong", "Accept": "application/json, text/event-stream"})
check(code == 401, "a wrong key is refused")
code, j = api("aiappadd", {"name": "Sneaky", "kind": "other"})
check(code == 423, "making a key needs a page that unlocked a memory (no other program can)")

# ---- a read-only key from Settings ----
code, j = api("aiappadd", {"name": "Reader", "kind": "claude-code", "folders": "all", "write": False}, P, fid)
key = j["key"]
check(code == 200 and key.startswith("pm_") and j["app"]["name"] == "Reader", "Settings makes a key (shown once)")
state = open(os.path.join(os.environ.get("PM_TEST_STATE", ""), "ai-apps.json")).read() if os.environ.get("PM_TEST_STATE") else ""
check(not state or key not in state, "the key itself is never stored, only its fingerprint")
out = run(key, ("status", {}), ("search_notes", {"question": "lighthouse"}), ("list_notes", {}),
          ("recent_changes", {"limit": 3}), ("append_to_note", {"id": "h-x", "text": "x"}),
          ("trash_note", {"path": "Ideas/Pocket-Library.md"}))
check({"list_notes", "recent_changes", "read_file_text", "links_to", "move_note", "make_folder", "trash_note"} <= set(out["tools"]),
      "the new tools are there", out["tools"])
check("unlocked, " in out["status"] and "only read" in out["status"], "status works, and says it may only read", out["status"])
check("Lighthouse" in out["search_notes"], "a read-only key can search")
check("Projects/" in out["list_notes"] and ".phygital" not in out["list_notes"], "list_notes lists notes, never the hidden folder")
check(out["recent_changes"].count("\n") >= 2, "recent_changes lists the newest", out["recent_changes"])
check(out["append_to_note"].startswith("ERROR") and "only read" in out["append_to_note"], "a read-only key can't edit")
check(out["trash_note"].startswith("ERROR"), "…or trash")
code, j = api("aiactivity", {}, P, fid)
check(any(a["app"] == "Reader" for a in j["activity"]), "the activity list shows the name given in Settings")

# ---- edit allowed ----
aid = [a for a in api("aiapps", {}, P, fid)[1]["apps"] if a["name"] == "Reader"][0]["id"]
api("aiappupdate", {"id": aid, "write": True}, P, fid)
out = run(key, ("make_folder", {"path": "AI Made"}), ("move_note", {"path": "Ideas/Pocket-Library.md", "new_path": "AI Made/Pocket.md"}),
          ("links_to", {"path": "Projects/Lighthouse-App.md"}), ("read_file_text", {"path": "AI Made/Pocket.md"}),
          ("trash_note", {"path": "AI Made/Pocket.md"}), ("read_file_text", {"path": "attachments/Garden-plan.docx"}))
check(not out["make_folder"].startswith("ERROR") and not out["move_note"].startswith("ERROR"), "after allowing edits: folder and move work", out)
check("tomatoes" in out["read_file_text"], "read_file_text reads a Word file", out["read_file_text"][:200])
check(not out["links_to"].startswith("ERROR"), "links_to works", out["links_to"][:200])
code, j = api("trashlist", {}, P, fid)
check(not out["trash_note"].startswith("ERROR") and any("Pocket" in (t.get("path") or t.get("name") or "") for t in j.get("items", [])),
      "trash_note puts it in the app's trash (not erased)", j)

# ---- "AI can't see this", then only some memories ----
api("aihide", {"hidden": True}, P, fid)
out = run(key, ("search_notes", {"question": "lighthouse"}))
check(out["search_notes"].startswith("ERROR"), "a memory marked AI can't see this is closed to every app")
api("aihide", {"hidden": False}, P, fid)
api("aiappupdate", {"id": aid, "folders": ["someotherid"]}, P, fid)
out = run(key, ("search_notes", {"question": "lighthouse"}), ("status", {}))
check(out["search_notes"].startswith("ERROR") and "locked-notes" not in out["status"], "an app limited to other memories can't see this one")
api("aiappupdate", {"id": aid, "folders": "all"}, P, fid)

# ---- remove ----
api("aiappremove", {"id": aid}, P, fid)
code, _, _ = http("POST", "/mcp", {}, {"Authorization": f"Bearer {key}", "Accept": "application/json, text/event-stream"})
check(code == 401, "a removed app is cut off at once")

# ---- MCP sign-in: the AI app registers, the person presses Allow in the app ----
code, _, raw = http("POST", "/register", {"redirect_uris": ["http://127.0.0.1:9/cb"], "client_name": "Test AI",
                                          "token_endpoint_auth_method": "none",
                                          "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"]})
client = json.loads(raw)["client_id"]
check(code == 201, "an AI app can register for sign-in", raw[:200])
verifier = secrets.token_urlsafe(48)
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
q = urllib.parse.urlencode({"response_type": "code", "client_id": client, "redirect_uri": "http://127.0.0.1:9/cb",
                            "code_challenge": challenge, "code_challenge_method": "S256", "state": "s1"})
code, hdrs, _ = http("GET", f"/authorize?{q}")
where = hdrs.get("Location", "")
check(code in (302, 303, 307) and "/allow/" in where, "sign-in sends the browser to the waiting page", where)
rid = where.rsplit("/", 1)[-1]
code, _, raw = http("GET", f"/allow/{rid}/state")
check(json.loads(raw)["next"] is None, "the page waits until the person answers")
code, j = api("allowanswer", {"id": rid, "allow": True})
check(code == 423, "nobody can press Allow without a page that unlocked a memory")
code, j = api("allowwaiting", {}, P, fid)
check([w["name"] for w in j["waiting"]] == ["Test AI"], "the app shows who is asking", j)
api("allowanswer", {"id": rid, "allow": True, "folders": "all", "write": False}, P, fid)
code, _, raw = http("GET", f"/allow/{rid}/state")
nxt = json.loads(raw)["next"] or ""
got = urllib.parse.parse_qs(urllib.parse.urlparse(nxt).query)
check(nxt.startswith("http://127.0.0.1:9/cb") and got.get("state") == ["s1"] and got.get("code"), "after Allow the page goes back to the AI app with a code", nxt)
code, _, raw = http("POST", "/token", {"grant_type": "authorization_code", "code": got["code"][0], "client_id": client,
                                       "redirect_uri": "http://127.0.0.1:9/cb", "code_verifier": verifier}, form=True)
tok = json.loads(raw)
check(code == 200 and tok.get("access_token", "").startswith("pm_"), "the code becomes a key", raw[:200])
out = run(tok["access_token"], ("status", {}), ("create_note", {"path": "x.md", "text": "x"}))
check("only read" in out["status"] and out["create_note"].startswith("ERROR"), "the signed-in app gets what was chosen (read only)")
code, _, raw = http("POST", "/token", {"grant_type": "authorization_code", "code": got["code"][0], "client_id": client,
                                       "redirect_uri": "http://127.0.0.1:9/cb", "code_verifier": verifier}, form=True)
check(code == 400, "a code works only once")
code, _, raw = http("POST", "/token", {"grant_type": "refresh_token", "refresh_token": tok["refresh_token"], "client_id": client}, form=True)
check(code == 200 and json.loads(raw).get("access_token"), "the app can renew its key")
code, _, raw = http("POST", "/token", {"grant_type": "refresh_token", "refresh_token": tok["refresh_token"], "client_id": client}, form=True)
check(code == 400, "each renewal key works once")
apps = api("aiapps", {}, P, fid)[1]["apps"]
check([a["name"] for a in apps if a["signin"]] == ["Test AI"], "the signed-in app is listed in Settings", apps)

# a "no" goes back to the AI app as a refusal
code, hdrs, _ = http("GET", f"/authorize?{q}")
rid = hdrs.get("Location", "").rsplit("/", 1)[-1]
api("allowanswer", {"id": rid, "allow": False}, P, fid)
nxt = json.loads(http("GET", f"/allow/{rid}/state")[2])["next"] or ""
check("error=access_denied" in nxt, "Deny tells the AI app no")
code, _, raw = http("GET", "/allow/not-a-request/state")
check(json.loads(raw)["gone"], "an unknown request says it ran out")

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
