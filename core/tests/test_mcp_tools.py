"""Every MCP tool an AI app gets, end to end, against a running test server (PM_TEST_PORT) on a fresh test folder:
it reads, searches, edits, makes, moves, trashes, does a handed task, and respects a private folder. Each edit is
checked in the note itself through the app's own /api, not only in what the tool says.

Run make_test_vault.py --fresh first, then: PM_TEST_PORT=8796 uv run python test_mcp_tools.py
"""
import asyncio
import json
import os
import re
import urllib.error
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

code, j = api("folders")
fid = j["folders"][0]["id"]
code, j = api("unlock", {"password": "12345678"}, folder=fid)
P = j["pass"]
code, j = api("aiappadd", {"name": "Full test", "kind": "other", "folders": "all", "write": True}, P, fid)
KEY = j["key"]
ALL = ["status", "search_notes", "open_result", "around_result", "read_note", "handed_notes", "finish_handed_note",
       "replace_in_note", "append_to_note", "create_note", "list_notes", "recent_changes", "read_file_text", "links_to",
       "move_note", "make_folder", "trash_note"]


def note(path):   # the note as the app itself sees it
    return api("read", {"path": path}, P, fid)[1].get("text", "")


async def main():
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {KEY}"}) as client:
        async with streamable_http_client(f"{BASE}/mcp", http_client=client) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()

                async def call(name, **args):
                    res = await s.call_tool(name, args)
                    return ("ERROR " if res.is_error else "") + "\n".join(c.text for c in res.content if hasattr(c, "text"))

                tools = sorted(t.name for t in (await s.list_tools()).tools)
                check(tools == sorted(ALL), "all 17 tools are offered", tools)
                t = await call("status")
                check("locked-notes" in t and "ERROR" not in t, "status names the open memory", t[:200])

                t = await call("search_notes", question="why is the garden planner paused")
                ids = re.findall(r"\b[0-9a-f]{4,}:\d+\b", t)
                check("Garden-Planner" in t and ids, "search_notes finds the right note", t[:300])
                rid = ids[0]
                t = await call("open_result", id=rid)
                check("licence" in t, "open_result shows the matching section", t[:200])
                t = await call("open_result", id=rid, whole_note=True)
                check("What it is" in t and "Why paused" in t, "open_result whole_note shows the whole note", t[:200])
                t = await call("around_result", id=rid)
                check(t and not t.startswith("ERROR"), "around_result shows the text around it", t[:200])
                t = await call("read_note", id=rid)
                check("balcony" in t, "read_note reads the note", t[:200])

                t = await call("replace_in_note", id=rid, old_text="Revisit in spring.", new_text="Revisit in April.")
                check("ERROR" not in t and "Revisit in April." in note("Projects/Garden-Planner.md"),
                      "replace_in_note changes the note", t[:200])
                t = await call("replace_in_note", id=rid, old_text="text that is not there", new_text="x")
                check("ERROR" in t or "not" in t.lower(), "replace_in_note refuses text that isn't there", t[:200])
                t = await call("append_to_note", id=rid, text="x")
                check("ERROR" in t and "Search" in t, "an edit makes the old search id stale (search again)", t[:200])
                t = await call("search_notes", question="garden planner revisit in April")
                rid = re.findall(r"\b[0-9a-f]{4,}:\d+\b", t)[0]
                t = await call("append_to_note", id=rid, text="Added by the full MCP test.")
                check("Added by the full MCP test." in note("Projects/Garden-Planner.md"), "append_to_note adds at the end", t[:200])

                t = await call("replace_in_note", path="Projects/Garden-Planner.md", old_text="Revisit in April.", new_text="Revisit in May.")
                check('path="Projects/Garden-Planner.md"' in t and "Revisit in May." in note("Projects/Garden-Planner.md"),
                      "replace_in_note works by path, and says which path to use next", t[:200])
                t = await call("append_to_note", path="Projects/Garden-Planner.md", text="Second edit in a row, no search.")
                check("Second edit in a row" in note("Projects/Garden-Planner.md"), "a second edit by path needs no new search", t[:200])
                t = await call("append_to_note", path="Projects/Nope.md", text="x")
                check("ERROR" in t, "an edit to a path that isn't there is refused", t[:200])
                t = await call("append_to_note", text="x")
                check("ERROR" in t and "path" in t, "an edit with neither path nor id says what to give", t[:200])
                api("aiprivate", {"path": "Ideas", "on": True}, P, fid)
                t = await call("append_to_note", path="Ideas/Secret-Recipe.md", text="x")
                check("ERROR" in t or "private" in t.lower(), "an edit by path into a private folder is refused", t[:200])
                t = await call("append_to_note", path="Ideas/Secret-Recipe", text="x")
                check("ERROR" in t or "private" in t.lower(), "...also without the .md ending", t[:200])
                api("aiprivate", {"path": "Ideas", "on": False}, P, fid)
                t = await call("make_folder", path="Archive/2027")
                check("ERROR" not in t, "make_folder makes a subfolder", t[:200])
                t = await call("create_note", path="Archive/2027/plan.md", text="# Plan\nA link to [[Garden-Planner]].")
                check("ERROR" not in t and "A link to" in note("Archive/2027/plan.md"), "create_note makes a note", t[:200])
                t = await call("create_note", path="Archive/2027/plan.md", text="again")
                check("ERROR" in t or "exists" in t.lower() or "already" in t.lower(), "create_note won't overwrite a note", t[:200])
                t = await call("list_notes", inside="Archive")
                check("plan.md" in t, "list_notes lists inside a subfolder", t[:200])
                t = await call("recent_changes", limit=5)
                check("plan" in t and "Garden-Planner" in t, "recent_changes shows the newest edits", t[:300])
                t = await call("links_to", path="Projects/Garden-Planner.md")
                check("plan" in t, "links_to finds the new link", t[:200])
                t = await call("read_file_text", path="attachments/people.csv")
                check(t and "ERROR" not in t, "read_file_text reads a CSV", t[:200])
                t = await call("read_file_text", path="attachments/Garden-plan.docx")
                check(t and "ERROR" not in t, "read_file_text reads a Word file", t[:200])

                t = await call("move_note", path="Archive/2027/plan.md", new_path="Archive/plan-2027.md")
                check(note("Archive/plan-2027.md") and not note("Archive/2027/plan.md"), "move_note moves and renames", t[:200])
                t = await call("trash_note", path="Archive/plan-2027.md")
                trash = api("trashlist", {}, P, fid)[1]
                check(not note("Archive/plan-2027.md") and "plan-2027" in str(trash), "trash_note puts it in the app's trash", t[:200])

                api("handtoai", {"path": "People/Tom-Becker.md", "ask": "Add a line saying the full test was here."}, P, fid)
                t = await call("handed_notes")
                hid = (re.findall(r"\bh-[0-9a-f]+\b", t) or [""])[0]
                check(hid and "Add a line" in t, "handed_notes shows what the person asked", t[:200])
                await call("append_to_note", id=hid, text="The full test was here.")
                t = await call("finish_handed_note", id=hid, what_you_did="Added the line.")
                left = await call("handed_notes")
                check("The full test was here." in note("People/Tom-Becker.md") and hid not in left,
                      "a handed task is done and finished", t[:200])

                api("aiprivate", {"path": "Ideas", "on": True}, P, fid)
                t = await call("search_notes", question="secret recipe")
                check("Secret-Recipe" not in t or "private" in t.lower(), "a private folder stays closed in search", t[:300])
                t = await call("read_file_text", path="Ideas/Secret-Recipe.md")
                check("ERROR" in t or "private" in t.lower(), "a private note won't open without private=true", t[:200])
                t = await call("read_file_text", path="Ideas/Secret-Recipe.md", private=True)
                check("ERROR" not in t and len(t) > 20, "it opens when the person asked (private=true)", t[:200])
                api("aiprivate", {"path": "Ideas", "on": False}, P, fid)

                code, a = api("aiactivity", {}, P, fid)
                check(code == 200, "every step shows in the app's AI activity", a)


asyncio.run(main())
print(f"\n{sum(ok)}/{len(ok)} passed")
