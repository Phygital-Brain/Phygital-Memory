"""A clash copy becomes an AI task: the AI sees both versions, merges, finishes, and the copy goes to the trash.

Run against a running test server: PM_TEST_PORT=8796 uv run python test_conflict_task.py
"""
import asyncio
import json
import os
import re
import urllib.error
import urllib.request

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

BASE = "http://127.0.0.1:" + os.environ.get("PM_TEST_PORT", "8796")
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def call(action, body=None, pw=None, folder=None):
    body = {**(body or {}), **({"folder": folder} if folder else {})}
    req = urllib.request.Request(f"{BASE}/api/{action}", json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-App-Pass": pw} if pw else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


async def ai(steps):
    async with streamable_http_client(f"{BASE}/mcp") as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            return [("\n".join(c.text for c in (await s.call_tool(n, a)).content if hasattr(c, "text"))) for n, a in steps]


fid = call("folders")["folders"][0]["id"]
P = call("unlock", {"password": "12345678"}, folder=fid)["pass"]
c = lambda a, b=None: call(a, b, P, fid)

base = "# Trip\n\nday one: beach\nday two: museum\n"
c("save", {"path": "Trip.md", "text": base})
c("save", {"path": "Trip.md", "text": base.replace("museum", "museum and market (phone)"), "base": base})
j = c("save", {"path": "Trip.md", "text": base.replace("museum", "museum and castle (mac)"), "base": base})
copy = j.get("conflict")
check(copy and "(conflict " in copy, "a same-line clash makes a copy", j)

todo = c("aitodo").get("todo", [])
task = next((t for t in todo if t.get("copy") == copy), None)
check(task and task["path"] == "Trip.md" and not task["done"], "the copy shows as an AI task on the note", todo)
c("save", {"path": "Trip.md", "text": base.replace("museum", "museum and castle (mac)"), "base": base})
check(sum(1 for t in c("aitodo")["todo"] if t.get("copy") == copy) == 1, "a retried save doesn't add a second task")

out = asyncio.run(ai([("handed_notes", {})]))[0]
check(task["id"] in out and "castle (mac)" in out and "market (phone)" in out, "the AI sees both versions", out[:300])

asyncio.run(ai([("replace_in_note", {"id": task["id"], "old_text": "museum and market (phone)",
                                     "new_text": "museum, market (phone) and castle (mac)"}),
                ("finish_handed_note", {"id": task["id"], "what_you_did": "Merged both versions."})]))
note = c("read", {"path": "Trip.md"})["text"]
check("market (phone) and castle (mac)" in note, "the merged note keeps both sides", note)
files = [f["path"] for f in c("files")["files"]]
check(copy not in files, "the copy is gone from the folder", files)
check(any(i["path"] == copy for i in c("trashlist")["items"]), "the copy is in the trash, so it can come back")
check(next(t for t in c("aitodo")["todo"] if t["id"] == task["id"])["done"], "the task is ticked off")

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
