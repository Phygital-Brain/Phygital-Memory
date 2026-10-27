"""Folders private for AI, against a running test server (PM_TEST_PORT) on a fresh test folder: AI search shows their
notes locked (place and section only, and only when every word matches), every AI tool needs private=true to go in,
the mark follows a renamed folder, and turning it off opens it again. Run make_test_vault.py --fresh first.

Run: PM_TEST_PORT=8796 uv run python test_private.py
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


fid = api("folders")[1]["folders"][0]["id"]
P = api("unlock", {"password": "12345678"}, folder=fid)[1]["pass"]
key = api("aiappadd", {"name": "Tester", "kind": "other", "folders": "all", "write": True}, P, fid)[1]["key"]

code, j = api("aiprivate", {"path": "People", "on": True})
check(code == 423, "only the person's own page can make a folder private")
code, j = api("aiprivate", {"path": "People", "on": True}, P, fid)
check(code == 200 and j["paths"] == ["People"], "People is private now", j)

search, nothing, status = run(("search_notes", {"question": "Tom Becker sound designer"}),
                              ("search_notes", {"question": "Tom Becker zebra"}), ("status", {}))
line = next((l for l in search.splitlines() if "People/Tom-Becker" in l), "")
check("🔒 private" in line, "search shows the private note locked", search)
check("Berlin" not in search and "freelance" not in search, "and none of its text")
check("Tom-Becker" not in nothing, "a question with a word not in it shows no private note", nothing)
check("Private, ask first: People" in status, "status names the private folders", status)
rid = re.search(r"\[([^\]]+)\]", line).group(1)

out = run(("open_result", {"id": rid}), ("open_result", {"id": rid, "private": True}),
          ("read_note", {"id": rid}), ("around_result", {"id": rid}),
          ("read_file_text", {"path": "People/Tom-Becker.md"}), ("read_file_text", {"path": "People/Tom-Becker.md", "private": True}),
          ("list_notes", {}), ("list_notes", {"inside": "People"}), ("list_notes", {"inside": "People", "private": True}),
          ("recent_changes", {"limit": 50}), ("links_to", {"path": "People/Tom-Becker.md"}))
check(out[0].startswith("ERROR") and "private=true" in out[0], "open_result refuses without private=true", out[0])
check("Berlin" in out[1], "and opens it with private=true")
check(out[2].startswith("ERROR") and out[3].startswith("ERROR"), "read_note and around_result refuse too")
check(out[4].startswith("ERROR") and "Berlin" in out[5], "read_file_text refuses, then opens with private=true")
check("People/  (private: ask first)" in out[6] and "Tom-Becker" not in out[6], "list_notes shows the folder, not what's in it", out[6])
check(out[7].startswith("ERROR") and "Tom-Becker" in out[8], "looking inside needs private=true")
check("People/" not in out[9], "recent changes leave private notes out", out[9])
check(out[10].startswith("ERROR"), "links_to refuses too")

out = run(("create_note", {"path": "People/New.md", "text": "x"}), ("append_to_note", {"id": rid, "text": "x"}),
          ("trash_note", {"path": "People/Mira-Santos.md"}), ("move_note", {"path": "People/Mira-Santos.md", "new_path": "Mira.md"}),
          ("move_note", {"path": "Ideas", "new_path": "People/Ideas"}), ("make_folder", {"path": "People/Sub"}))
check(all(o.startswith("ERROR") for o in out), "writing, trashing and moving in or out need private=true", out)
out = run(("append_to_note", {"id": rid, "text": "Asked for by the person."}))
check(out[0].startswith("ERROR"), "still refused")
out = run(("append_to_note", {"id": rid, "text": "Asked for by the person.", "private": True}))
check(not out[0].startswith("ERROR"), "and allowed with private=true", out[0])

# other spellings of the same private path: "\\" for "/", and the decomposed (NFD) form of a name
import unicodedata
out = run(("read_file_text", {"path": "People\\Tom-Becker.md"}), ("read_file_text", {"path": "/People//Tom-Becker.md"}),
          ("move_note", {"path": "People\\Tom-Becker.md", "new_path": "Tom.md"}))
check(all(o.startswith("ERROR") and "private" in o for o in out), "other spellings of a private path are caught too", out)
api("make_folder" if False else "mkdir", {"path": "Café"}, P, fid)
api("save", {"path": "Café/x.md", "text": "# x\nbrioche\n", "new": True}, P, fid)
api("aiprivate", {"path": "Café", "on": True}, P, fid)
out = run(("read_file_text", {"path": unicodedata.normalize("NFD", "Café") + "/x.md"}))
check(out[0].startswith("ERROR"), "a decomposed spelling of a private name is caught", out)
api("aiprivate", {"path": "Café", "on": False}, P, fid)

code, j = api("move", {"from": "People", "to": "Contacts"}, P, fid)
check(api("aiprivate", {}, P, fid)[1]["paths"] == ["Contacts"], "renamed, it stays private")
out = run(("list_notes", {}), ("read_file_text", {"path": "Contacts/Tom-Becker.md"}))
check("Contacts/  (private: ask first)" in out[0] and out[1].startswith("ERROR"), "under its new name")

api("aiprivate", {"path": "Contacts", "on": False}, P, fid)
out = run(("search_notes", {"question": "Tom Becker sound designer"}), ("read_file_text", {"path": "Contacts/Tom-Becker.md"}))
check("Berlin" in out[0] and "🔒" not in out[0] and "Berlin" in out[1], "open to AI again: back to normal", out[0])
whats = [r["what"] for r in api("approvals", {}, P, fid)[1]["approvals"]]
check("Private for AI: People" in whats and "Open to AI again: Contacts" in whats, "both show in Approvals", whats)

# one note on its own
code, j = api("aiprivate", {"path": "Ideas/Secret-Recipe.md", "on": True}, P, fid)
check(code == 200 and j["paths"] == ["Ideas/Secret-Recipe.md"], "a single note can be private", j)
out = run(("list_notes", {}), ("read_file_text", {"path": "Ideas/Secret-Recipe.md"}),
          ("read_file_text", {"path": "Ideas/Secret-Recipe.md", "private": True}), ("recent_changes", {"limit": 50}),
          ("list_notes", {"inside": "Ideas"}))
check("Ideas/Secret-Recipe.md  (private: ask first)" in out[0], "listed with its mark", out[0])
check(out[1].startswith("ERROR") and not out[2].startswith("ERROR"), "opens only with private=true")
check("Secret-Recipe" not in out[3], "left out of recent changes")
check("Ideas/Pocket-Library.md" in out[4] and "(private: ask first)" in out[4], "the notes next to it stay open", out[4])
q = api("files", {}, P, fid)[1]["files"]
words = run(("read_file_text", {"path": "Ideas/Secret-Recipe.md", "private": True}))[0].split("---8<---")[-1].split()
w = " ".join(x for x in words if x.isalpha() and len(x) > 4)[:40].rsplit(" ", 1)[0]
out = run(("search_notes", {"question": w}))
line = next((l for l in out[0].splitlines() if "Secret-Recipe" in l), "")
check("🔒 private" in line, "search shows it locked", out[0])
api("move", {"from": "Ideas/Secret-Recipe.md", "to": "Recipe.md"}, P, fid)
check(api("aiprivate", {}, P, fid)[1]["paths"] == ["Recipe.md"], "moved, it stays private")
code, j = api("aiprivate", {"path": "Nope.md", "on": True}, P, fid)
check(code != 200, "a path that isn't there is refused", j)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
