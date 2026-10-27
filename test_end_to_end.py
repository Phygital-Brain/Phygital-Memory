"""End to end, against the running server: an AI app over MCP, and the person's app over /api."""
import asyncio

import testkey
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
    async with streamable_http_client(f"{BASE}/mcp", http_client=testkey.client()) as (r, w):
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
    good &= check("AI tools: search, open, write, plus listing, recent changes, file text, links, move, folder, trash",
                  r["tools"] == ["append_to_note", "around_result", "create_note", "finish_handed_note", "handed_notes",
                                 "links_to", "list_notes", "make_folder", "move_note", "open_result", "read_file_text",
                                 "read_note", "recent_changes", "replace_in_note", "search_notes", "status", "trash_note"])
    good &= check("locked: search refused", "locked" in r['search_notes{"question": "storm"}'].lower())
    # 2. The app without the password gets nothing
    good &= check("app without pass refused", api("notes")[0] == 423)
    good &= check("other site name refused (DNS rebinding)", api("status", host="evil.example")[0] in (403, 421))
    good &= check("wrong password refused", api("unlock", {"password": "nope"})[0] == 400)
    # 3. The person unlocks in the app
    code, s = api("unlock", {"password": (Path(__file__).parent / ".test-password").read_text()})
    good &= check("unlock with password", code == 200 and s["open"] and s["notes"] == 11)
    app_pass = s["pass"]
    good &= check("app lists notes", len(api("notes", app_pass=app_pass)[1]["notes"]) == 11)
    # 4. The AI searches, opens, edits through Engram ids
    r = await ai([("search_notes", {"question": "tide data supplier"})])
    found = r['search_notes{"question": "tide data supplier"}']
    good &= check("AI search finds Lighthouse", "Projects/Lighthouse-App.md" in found)
    rid = found.split("[", 1)[1].split("]", 1)[0]
    r = await ai([("read_note", {"id": rid}),
                  ("replace_in_note", {"id": rid, "old_text": "still owe us an API key",
                                       "new_text": "sent the API key on 26 October"}),
                  ("create_note", {"path": "Ideas/From-AI.md", "text": "## Note\nWritten by the AI test."})])
    good &= check("AI reads exact note with info block", "status: active" in r['read_note{"id": "%s"}' % rid])
    good &= check("AI edit saved", "Saved" in r['replace_in_note{"id": "%s", "old_text": "still owe us an API key", '
                                               '"new_text": "sent the API key on 26 October"}' % rid])
    code, note = api("read", {"path": "Projects/Lighthouse-App.md"}, app_pass=app_pass)
    good &= check("edit kept the info block and changed the text",
                  note["text"].startswith("---\ntype: project") and "sent the API key on 26 October" in note["text"])
    r = await ai([("search_notes", {"question": "written by the AI test"})])
    good &= check("new note is searchable", "Ideas/From-AI.md" in r['search_notes{"question": "written by the AI test"}'])
    # 4b. The AI to-do list: the person gives a short note (no search id) with a request; the AI does it, ticks it off
    api("save", {"path": "Ideas/Tiny.md", "text": "hi"}, app_pass=app_pass)
    code, j = api("handtoai", {"path": "Ideas/Tiny.md", "ask": "Add the word kumquat at the end."}, app_pass=app_pass)
    hid = j["item"]["id"]
    r = await ai([("handed_notes", {})])
    listed = r["handed_notes{}"]
    good &= check("AI sees the handed note with the request", hid in listed and "kumquat" in listed and "Ideas/Tiny.md" in listed)
    r = await ai([("append_to_note", {"id": hid, "text": "kumquat"}),
                  ("finish_handed_note", {"id": hid, "what_you_did": "Added kumquat at the end."})])
    code, note = api("read", {"path": "Ideas/Tiny.md"}, app_pass=app_pass)
    good &= check("AI edited the handed note by its handed id", note["text"].rstrip().endswith("kumquat"))
    todo = api("aitodo", app_pass=app_pass)[1]["todo"]
    good &= check("ticked off, with what it did", todo[-1]["done"] and todo[-1]["result"] == "Added kumquat at the end.")
    good &= check("finished notes leave the AI's list", "No AI tasks waiting" in (await ai([("handed_notes", {})]))["handed_notes{}"])
    api("trash", {"path": "Ideas/Tiny.md"}, app_pass=app_pass)
    # 4c. Undo an AI change: works while the note is as the AI left it, refuses once the person changed it
    rel = "Projects/Lighthouse-App.md"
    before = api("read", {"path": rel}, app_pass=app_pass)[1]["text"]
    await ai([("search_notes", {"question": "tide data supplier"})])
    await ai([("append_to_note", {"id": rid, "text": "AI line one"})])
    acts = api("aiactivity", app_pass=app_pass)[1]["activity"]
    row = next(a for a in acts if a["what"] == "added to")
    good &= check("AI change can be undone", row["canUndo"])
    code, j = api("undoai", {"id": row["undo"]}, app_pass=app_pass)
    good &= check("undo puts the note back", code == 200 and api("read", {"path": rel}, app_pass=app_pass)[1]["text"] == before)
    found = (await ai([("search_notes", {"question": "tide data supplier"})]))['search_notes{"question": "tide data supplier"}']
    rid2 = found.split("[", 1)[1].split("]", 1)[0]   # ids change when a note changes: search again
    await ai([("append_to_note", {"id": rid2, "text": "AI line two"})])
    row = next(a for a in api("aiactivity", app_pass=app_pass)[1]["activity"] if a["what"] == "added to" and a["path"] == rel and a["canUndo"])
    now = api("read", {"path": rel}, app_pass=app_pass)[1]["text"]
    api("save", {"path": rel, "text": now + "\nmy own words\n"}, app_pass=app_pass)
    code, j = api("undoai", {"id": row["undo"]}, app_pass=app_pass)
    good &= check("undo refuses after the person changed the note", code == 409 and "my own words" in api("read", {"path": rel}, app_pass=app_pass)[1]["text"])
    # 5. Nothing readable on disk
    blob = b"".join(p.read_bytes() for p in VAULT.rglob("*") if p.is_file())
    good &= check("no plain text on disk", not any(w in blob for w in (b"paprika", b"Mira", b"Lighthouse", b"26 October", b"kumquat")))
    # 6. Lock
    api("lock", app_pass=app_pass)
    r = await ai([("search_notes", {"question": "storm"})])
    good &= check("locked again: AI refused", "locked" in r['search_notes{"question": "storm"}'].lower())
    good &= check("old app pass dead after lock", api("notes", app_pass=app_pass)[0] == 423)
    print("\nALL PASS" if good else "\nSOME FAILED")


asyncio.run(main())
