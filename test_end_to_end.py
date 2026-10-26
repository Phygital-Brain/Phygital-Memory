"""End to end, against the running server: an AI app over MCP, and the person's app over /api."""
import asyncio
import json
import urllib.error
import urllib.request
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

BASE = "http://127.0.0.1:" + __import__("os").environ.get("PM_TEST_PORT", "8790")
VAULT = Path(__file__).resolve().parent.parent / "locked-notes"


def api(action, body=None, app_pass=None, host=None):
    req = urllib.request.Request(f"{BASE}/api/{action}", json.dumps(body or {}).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-App-Pass": app_pass} if app_pass else {}),
                                          **({"Host": host} if host else {})})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def text(result):
    return "\n".join(c.text for c in result.content if hasattr(c, "text"))


async def ai(steps):
    async with streamable_http_client(f"{BASE}/mcp") as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = sorted(t.name for t in (await s.list_tools()).tools)
            out = {"tools": tools}
            for name, args in steps:
                out[name + json.dumps(args)] = text(await s.call_tool(name, args))
            return out


def check(label, ok):
    print(("PASS " if ok else "FAIL ") + label)
    return ok


async def main():
    good = True
    api("lock", app_pass="none")
    # 1. Locked: the AI gets nothing and is told to ask the person to unlock in the app
    r = await ai([("search_notes", {"question": "storm"})])
    good &= check("AI tools are only search/open/write, no folder listing or path reading",
                  r["tools"] == ["append_to_note", "around_result", "create_note", "open_result", "read_note",
                                 "replace_in_note", "search_notes", "status"])
    good &= check("locked: search refused", "locked" in r['search_notes{"question": "storm"}'].lower())
    # 2. The app without the password gets nothing
    good &= check("app without pass refused", api("notes")[0] == 423)
    good &= check("other site name refused (DNS rebinding)", api("status", host="evil.example")[0] in (403, 421))
    good &= check("wrong password refused", api("unlock", {"password": "nope"})[0] == 400)
    # 3. The person unlocks in the app
    code, s = api("unlock", {"password": (Path(__file__).parent / ".test-password").read_text()})
    good &= check("unlock with password", code == 200 and s["open"] and s["notes"] == 10)
    app_pass = s["pass"]
    good &= check("app lists notes", len(api("notes", app_pass=app_pass)[1]["notes"]) == 10)
    # 4. The AI searches, opens, edits through Engram ids
    r = await ai([("search_notes", {"question": "tide data supplier"})])
    found = r['search_notes{"question": "tide data supplier"}']
    good &= check("AI search finds Lighthouse", "Projects/Lighthouse-App.md" in found)
    rid = int(found.split("[", 1)[1].split("]", 1)[0])
    r = await ai([("read_note", {"id": rid}),
                  ("replace_in_note", {"id": rid, "old_text": "still owe us an API key",
                                       "new_text": "sent the API key on 26 October"}),
                  ("create_note", {"path": "Ideas/From-AI.md", "text": "## Note\nWritten by the AI test."})])
    good &= check("AI reads exact note with info block", "status: active" in r['read_note{"id": %d}' % rid])
    good &= check("AI edit saved", "Saved" in r['replace_in_note{"id": %d, "old_text": "still owe us an API key", '
                                               '"new_text": "sent the API key on 26 October"}' % rid])
    code, note = api("read", {"path": "Projects/Lighthouse-App.md"}, app_pass=app_pass)
    good &= check("edit kept the info block and changed the text",
                  note["text"].startswith("---\ntype: project") and "sent the API key on 26 October" in note["text"])
    r = await ai([("search_notes", {"question": "written by the AI test"})])
    good &= check("new note is searchable", "Ideas/From-AI.md" in r['search_notes{"question": "written by the AI test"}'])
    # 5. Nothing readable on disk
    blob = b"".join(p.read_bytes() for p in VAULT.rglob("*") if p.is_file())
    good &= check("no plain text on disk", not any(w in blob for w in (b"paprika", b"Mira", b"Lighthouse", b"26 October")))
    # 6. Lock
    api("lock", app_pass=app_pass)
    r = await ai([("search_notes", {"question": "storm"})])
    good &= check("locked again: AI refused", "locked" in r['search_notes{"question": "storm"}'].lower())
    good &= check("old app pass dead after lock", api("notes", app_pass=app_pass)[0] == 423)
    print("\nALL PASS" if good else "\nSOME FAILED")


asyncio.run(main())
