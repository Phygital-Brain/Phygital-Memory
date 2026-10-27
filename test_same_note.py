"""The same note changed from several places at once: the app, AI apps over MCP, and another device.

Nothing may be lost, and no extra copies may appear when there is nothing to keep apart.
Part 1 needs no server. Part 2 runs against a running test server (PM_TEST_PORT, fresh test folder).

Run: uv run python test_same_note.py
"""
import asyncio
import json
import os
import shutil
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path

from phygital_memory.memory import Memory

PW = "test-same-note"
results = []


def check(cond, what, info=""):
    results.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def copies_of(m, stem):
    return [f["path"] for f in m.list_files() if f["path"].startswith(stem + " (conflict ")]


# ---------- part 1: the notes folder itself ----------

tmp = Path(tempfile.mkdtemp(prefix="pm-same-"))
try:
    folder = tmp / "notes"
    Memory.create(folder, PW)
    a, b = Memory(folder), Memory(folder)   # this Mac, and another device on the same synced folder
    a.unlock(PW)
    b.unlock(PW)

    # Many writers on one note at the same moment: every addition must land.
    a.save("Log.md", "# Log\n")
    errs = []

    def add(i):
        try:
            a.update("Log.md", lambda t: t + f"line {i}\n")
        except Exception as e:
            errs.append(e)
    ts = [threading.Thread(target=add, args=(i,)) for i in range(30)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    log = a.read("Log.md")
    check(not errs and all(f"line {i}\n" in log for i in range(30)), "30 additions at once: none lost", errs[:1])
    check(not copies_of(a, "Log"), "30 additions at once: no conflict copies")

    # Two edits in different places of a note: both kept in the note, no copy.
    base = "one\ntwo\nthree\nfour\nfive\n"
    a.save("Merge.md", base)
    a.update("Merge.md", lambda t: t + "six (from the AI)\n")
    out = a.save("Merge.md", base.replace("two", "TWO (from the app)"), base=base)
    text = a.read("Merge.md")
    check(out == "Merge.md" and "TWO (from the app)" in text and "six (from the AI)" in text,
          "edits in different places are put together", text)
    check(not copies_of(a, "Merge"), "edits in different places: no conflict copy")

    # Two edits to the same line: the note keeps the first, the second goes to ONE copy, however often it's retried.
    a.save("Same.md", base)
    a.save("Same.md", base.replace("three", "three by the phone"), base=base)
    first = a.save("Same.md", base.replace("three", "three by the app"), base=base)
    again = a.save("Same.md", base.replace("three", "three by the app"), base=base)
    check("(conflict " in first and first == again, "a retried clash reuses its copy", (first, again))
    check(len(copies_of(a, "Same")) == 1, "a retried clash: only one copy", copies_of(a, "Same"))
    check("three by the phone" in a.read("Same.md") and "three by the app" in a.read(first),
          "a real clash: both versions kept")

    # Same text saved from two places: no copy.
    a.save("Twin.md", base)
    b.save("Twin.md", base + "end\n", base=base)
    check(a.save("Twin.md", base + "end\n", base=base) == "Twin.md" and not copies_of(a, "Twin"),
          "the same change from two places: no copy")

    # Another device changed the note on disk (cloud sync): a stale save doesn't write over it.
    a.save("Phone.md", base)
    b.save("Phone.md", "written on the phone\n", base=base)
    out = a.save("Phone.md", "written on the mac\n", base=base)
    check(a.read("Phone.md") == "written on the phone\n" and a.read(out) == "written on the mac\n",
          "other device first: its text stays, ours goes to a copy")

    # An update that refuses (old text not there any more) changes nothing.
    a.save("Keep.md", base)
    try:
        a.update("Keep.md", lambda t: (_ for _ in ()).throw(ValueError("not there")))
    except ValueError:
        pass
    check(a.read("Keep.md") == base, "a refused change leaves the note alone")

    # AI edits a few seconds apart each keep a version (this used to crash from the second version on).
    import time
    a.save("Versions.md", "v0\n")
    for i in range(3):
        a.update("Versions.md", lambda t, i=i: t + f"v{i + 1}\n")
        time.sleep(1.1)
    check(a.read("Versions.md").count("\n") == 4 and len(a.versions("Versions.md")) >= 3,
          "AI edits seconds apart: all saved, each keeps a version")

    # Deleted on one side, edited on the other: the edit isn't lost.
    a.save("Gone.md", base)
    b.trash("Gone.md")
    out = a.save("Gone.md", base + "edited\n", base=base)
    check(a.read(out) == base + "edited\n", "edited after the other side deleted it: the edit is kept", out)
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# ---------- part 2: the app and AI apps through the running server ----------

BASE = "http://127.0.0.1:" + os.environ.get("PM_TEST_PORT", "8796")


def call(action, body=None, pw=None, folder=None):
    body = dict(body or {})
    if folder:
        body["folder"] = folder
    req = urllib.request.Request(f"{BASE}/api/{action}", json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-App-Pass": pw} if pw else {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


async def mcp(steps):
    from mcp.client.session import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    async with streamable_http_client(f"{BASE}/mcp") as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out = []
            for name, args in steps:
                res = await s.call_tool(name, args)
                out.append("\n".join(c.text for c in res.content if hasattr(c, "text")))
            return out


try:
    code, j = call("folders")
    server = code == 200
except Exception:
    server = False

if not server:
    print("SKIP part 2: no test server on", BASE)
else:
    fid = j["folders"][0]["id"]
    _, j = call("unlock", {"password": "12345678"}, folder=fid)
    P = j["pass"]
    c = lambda a, b=None: call(a, b, P, fid)

    seed = "# Busy note\n\nquokka marker\n\nfirst line\n"
    c("save", {"path": "Busy.md", "text": seed})

    found = asyncio.run(mcp([("search_notes", {"question": "quokka marker"})]))[0]
    import re
    m = re.search(r"\[([0-9a-f]+:\d+)\] Busy\.md", found)
    rid = m and m.group(1)
    check(rid, "the AI finds the note", found[:200])

    # Eight AI apps add to the note at once.
    async def many():
        return await asyncio.gather(*[mcp([("append_to_note", {"id": rid, "text": f"ai line {i}"})]) for i in range(8)])
    asyncio.run(many())
    _, j = c("read", {"path": "Busy.md"})
    now = j.get("text", "")
    check(all(f"ai line {i}" in now for i in range(8)), "8 AI additions at once: none lost",
          [i for i in range(8) if f"ai line {i}" not in now])

    # The app saves with the text it loaded before the AI wrote: the app's edit and the AI's both stay, no copy.
    app_text = seed.replace("first line", "first line, edited in the app")
    _, j = c("save", {"path": "Busy.md", "text": app_text, "base": seed})
    _, r = c("read", {"path": "Busy.md"})
    check(not j.get("conflict") and "edited in the app" in r["text"] and "ai line 3" in r["text"],
          "app save after AI additions: both kept, no copy", j)

    # The app and an AI change the same line: the first stays, the other is kept in one copy.
    base2 = r["text"]
    asyncio.run(mcp([("replace_in_note", {"id": rid, "old_text": "edited in the app", "new_text": "edited by the AI"})]))
    clash = base2.replace("edited in the app", "edited in the app again")
    _, j1 = c("save", {"path": "Busy.md", "text": clash, "base": base2})
    _, j2 = c("save", {"path": "Busy.md", "text": clash, "base": base2})
    _, files = c("files")
    cps = [f["path"] for f in files.get("files", []) if f["path"].startswith("Busy (conflict ")]
    check(j1.get("conflict") and j1.get("conflict") == j2.get("conflict") and len(cps) == 1,
          "same-line clash, saved twice: one copy", (j1, j2, cps))

    # An AI change can't be undone after the app edited the note on top of it.
    _, r = c("read", {"path": "Busy.md"})
    _, act = c("aiactivity")
    undo = next((x for x in act.get("activity", []) if x.get("canUndo") and x.get("path") == "Busy.md"), None)
    c("save", {"path": "Busy.md", "text": r["text"] + "app edit after the AI\n", "base": r["text"]})
    if undo:
        code, j = c("undoai", {"id": undo["undo"]})
        _, r2 = c("read", {"path": "Busy.md"})
        check(code == 409 and "app edit after the AI" in r2["text"], "undo AI refused after the app edited", (code, j))
    else:
        check(False, "undo AI refused after the app edited", act)

print(f"\n{sum(results)}/{len(results)} passed")
raise SystemExit(0 if all(results) else 1)
