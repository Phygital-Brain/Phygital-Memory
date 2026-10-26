"""Every /api action the app uses, against a running test server (PM_TEST_PORT), on a fresh test folder.
Run make_test_vault.py --fresh first. Prints PASS/FAIL per check."""
import json
import os
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:" + os.environ.get("PM_TEST_PORT", "8796")
results = []


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


def check(name, ok, info=""):
    ok = bool(ok)
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  ({info})" if info and not ok else ""))


code, j = call("folders")
check("folders list", code == 200 and j["folders"], j)
fid = j["folders"][0]["id"]
code, j = call("unlock", {"password": "12345678"}, folder=fid)
check("unlock", code == 200 and j.get("pass"), j)
P = j["pass"]
c = lambda a, b=None: call(a, b, P, fid)

code, j = c("status"); check("status", j.get("open") is True, j)
code, j = c("bar"); check("status bar data", code == 200 and j.get("lockMinutes") is not None and "ai" in j, j)
code, j = c("notes"); check("notes", len(j.get("notes", [])) >= 10, j)
code, j = c("files"); check("files with dates", any(f.get("mtime") for f in j.get("files", [])), j)
code, j = c("read", {"path": "People/Tom-Becker.md"}); check("read", "Berlin" in j.get("text", ""), j)
code, j = c("save", {"path": "Tests/new.md", "text": "# New\nhello from the api test", "new": True}); check("save new", code == 200, j)
code, j = c("save", {"path": "Tests/new.md", "text": "x", "new": True}); check("save new refuses duplicate", code == 400, j)
code, j = c("save", {"path": "Tests/new.md", "text": "# New\nedited [[Tom-Becker]] #apitest"}); check("save edit", code == 200, j)
code, j = c("search", {"q": "hello api test"}); check("search", code == 200, j)
code, j = c("search", {"q": "sound", "within": "People"}); check("search within folder", all(r["path"].startswith("People/") for r in j.get("results", [])) and j.get("results"), j)
rid = (j.get("results") or [{}])[0].get("id")
code, j = c("result", {"id": rid}); check("result preview", code == 200 and j.get("text"), j)
code, j = c("savefile", {"path": "Tests/data.csv", "base64": "YSxiCjEsMgo="}); check("save file", code == 200, j)
code, j = c("readfile", {"path": "Tests/data.csv"}); check("read file", j.get("base64") == "YSxiCjEsMgo=", j)
code, j = c("mkdir", {"path": "Tests/Sub"}); check("make subfolder", code == 200, j)
code, j = c("move", {"from": "Tests/new.md", "to": "Tests/Sub/renamed"}); check("move/rename", j.get("path") == "Tests/Sub/renamed.md", j)
code, j = c("versions", {"path": "Tests/Sub/renamed.md"}); check("versions list", code == 200, j)
code, j = c("links"); check("links + tags", code == 200 and "edges" in j and any(t[0] == "apitest" for t in j.get("tags", [])), j)
code, j = c("backlinks", {"path": "People/Tom-Becker.md"}); check("backlinks", any(b["path"] == "Tests/Sub/renamed.md" for b in j.get("backlinks", [])), j)
code, j = c("prefs"); check("prefs read", code == 200, j)
code, j = c("saveprefs", {"prefs": {"home": "CLAUDE.md"}}); check("prefs save", j.get("prefs", {}).get("home") == "CLAUDE.md", j)
code, j = c("prefs"); check("prefs persisted", j.get("prefs", {}).get("home") == "CLAUDE.md", j)
code, j = c("handtoai", {"path": "People/Tom-Becker.md", "ask": "Fix typos"}); check("give to AI with a request", code == 200 and j.get("item", {}).get("ask") == "Fix typos", j)
hid = j.get("item", {}).get("id")
code, j = c("handtoai", {"path": "People/Tom-Becker.md", "ask": "Shorter"}); check("giving again replaces the open item", [i["ask"] for i in j.get("todo", [])] == ["Shorter"], j)
hid = j["todo"][0]["id"]
code, j = c("aitodoset", {"id": hid, "done": True}); check("tick off by hand", j.get("todo", [{}])[0].get("done") is True, j)
c("move", {"from": "People/Tom-Becker.md", "to": "People/Tom-B.md"})
code, j = c("aitodo"); check("to-do item follows a rename", j.get("todo", [{}])[0].get("path") == "People/Tom-B.md", j)
c("move", {"from": "People/Tom-B.md", "to": "People/Tom-Becker.md"})
code, j = c("aitodoremove", {"id": hid}); check("remove from AI list", j.get("todo") == [], j)
import base64 as _b
b64 = lambda t: _b.b64encode(t.encode()).decode()
code, j = c("writefile", {"path": "Tests/table.csv", "base64": b64("a,b\n1,2\n")}); check("write a new CSV", j.get("path") == "Tests/table.csv", j)
code, j = c("writefile", {"path": "Tests/table.csv", "base64": b64("a,b\n1,3\n"), "base": b64("a,b\n1,2\n")}); check("edit CSV on top of what we saw", j.get("path") == "Tests/table.csv" and "conflict" not in j, j)
code, j = c("writefile", {"path": "Tests/table.csv", "base64": b64("a,b\n9,9\n"), "base": b64("a,b\n1,2\n")})
check("stale CSV edit keeps both", "(conflict " in j.get("conflict", "") and _b.b64decode(j.get("base64", "")) == b"a,b\n1,3\n", j)
code, j = c("readfile", {"path": j.get("conflict", "x")}); check("conflict copy holds our edit", _b.b64decode(j.get("base64", "")) == b"a,b\n9,9\n", j)
import subprocess, tempfile
_d = __import__("pathlib").Path(tempfile.mkdtemp())
(_d / "w.md").write_text("# Plan\n\nShip on **Monday**.\n")
subprocess.run(["pandoc", str(_d / "w.md"), "-o", str(_d / "w.docx")], check=True)
_w = (_d / "w.docx").read_bytes()
c("writefile", {"path": "Tests/plan.docx", "base64": _b.b64encode(_w).decode()})
code, j = c("docxread", {"path": "Tests/plan.docx"}); check("read a Word file", [p["text"] for p in j.get("paragraphs", [])][:2] == ["Plan", "Ship on Monday."], j)
_base, _i = j.get("base"), 1
code, j = c("docxsave", {"path": "Tests/plan.docx", "changes": {"1": "Ship on Friday."}, "base": _base}); check("edit a Word file", "base" in j and "conflict" not in j, j)
code, j = c("docxread", {"path": "Tests/plan.docx"}); check("Word edit saved", j.get("paragraphs", [{}, {}])[1].get("text") == "Ship on Friday.", j)
code, j = c("docxsave", {"path": "Tests/plan.docx", "changes": {"1": "Ship never."}, "base": _base}); check("stale Word edit keeps both", "(conflict " in j.get("conflict", ""), j)
code, j = c("docxread", {"path": "Tests/plan.docx"}); check("theirs stays in the file", j.get("paragraphs", [{}, {}])[1].get("text") == "Ship on Friday.", j)
code, j = c("aiactivity"); check("AI activity", code == 200 and "activity" in j, j)
code, j = c("storage"); check("storage info", code == 200 and "places" in j, j)
code, j = c("finder", {"do": "status"}); check("finder status", code == 200 and "available" in j, j)
code, j = c("trash", {"path": "Tests"}); check("trash folder", code == 200, j)
code, j = c("files"); check("trashed folder hidden", not any(f["path"].startswith("Tests") for f in j.get("files", [])), j)
code, j = c("renamefolder", {"name": "Test notes"}); check("rename folder", j.get("folder", {}).get("name") == "Test notes", j)
code, j = c("renamefolder", {"name": "locked-notes"})
code, j = call("unlock", {"password": "wrong-password"}, folder=fid); check("wrong password refused", code == 400, j)
code, j = c("lock"); check("lock", j.get("open") is False, j)
code, j = c("notes"); check("old pass dead after lock", code == 423, j)
print(f"\n{sum(results)}/{len(results)} passed")
