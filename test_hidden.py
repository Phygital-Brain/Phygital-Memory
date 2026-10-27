"""Hidden files (.env, .gitignore, .obsidian/): the app can show, open and save them; AI apps treat them as
private always; Mac clutter and the app's own folders stay out.

Run: PM_TEST_PORT=8796 uv run python test_hidden.py
"""
import asyncio
import json
import os
import re
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


def api(action, body=None, pw=None, folder=None):
    b = dict(body or {}, **({"folder": folder} if folder else {}))
    req = urllib.request.Request(f"{BASE}/api/{action}", json.dumps(b).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-App-Pass": pw} if pw else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


async def ai(token, steps):
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as client:
        async with streamable_http_client(f"{BASE}/mcp", http_client=client) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                out = []
                for name, args in steps:
                    res = await s.call_tool(name, args)
                    out.append(("ERROR " if res.is_error else "") + "\n".join(c.text for c in res.content if hasattr(c, "text")))
                return out


def run(*steps):
    return asyncio.run(ai(key, list(steps)))


import base64

fid = api("folders")[1]["folders"][0]["id"]
P = api("unlock", {"password": "12345678"}, folder=fid)[1]["pass"]
key = api("aiappadd", {"name": "Tester", "kind": "other", "folders": "all", "write": True}, P, fid)[1]["key"]
b64 = lambda t: base64.b64encode(t.encode()).decode()

code, j = api("savefile", {"path": ".env", "base64": b64("API_KEY=secret-123\n")}, P, fid)
check(code == 200 and j["path"] == ".env", "a .env file can be saved", j)
code, j = api("savefile", {"path": ".obsidian/app.json", "base64": b64("{}")}, P, fid)
check(code == 200, "and a file in a dot folder", j)
for bad in (".DS_Store", "._x", ".phygital/x.json", ".trash/x.md", "Projects/.versions/x"):
    code, j = api("savefile", {"path": bad, "base64": b64("x")}, P, fid)
    check(code != 200, f"{bad} is refused", j)
files = [f["path"] for f in api("files", {}, P, fid)[1]["files"]]
check(".env" in files and ".obsidian/app.json" in files, "hidden files are listed for the app", files)
check(not any(p.startswith((".phygital", ".trash", ".versions")) for p in files), "the app's own folders stay out")
code, j = api("readfile", {"path": ".env"}, P, fid)
check(code == 200 and base64.b64decode(j["base64"]).decode().startswith("API_KEY"), "a .env file opens", j)

out = run(("list_notes", {}), ("list_notes", {"private": True}), ("read_file_text", {"path": ".env"}),
          ("read_file_text", {"path": ".env", "private": True}), ("recent_changes", {"limit": 50}),
          ("create_note", {"path": ".secret/x.md", "text": "x"}), ("search_notes", {"question": "API_KEY secret"}))
check(".env" not in out[0] and ".obsidian" not in out[0], "AI lists don't show hidden files", out[0])
check(".env" in out[1], "unless the person asked (private=true)")
check(out[2].startswith("ERROR") and "secret-123" not in out[2], "AI can't read .env by itself", out[2])
check("secret-123" in out[3], "only with private=true")
check(".env" not in out[4], "hidden files stay out of recent changes")
check(out[5].startswith("ERROR"), "AI can't write a hidden file by itself")
check("secret-123" not in out[6], "search never shows a .env's text")

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
