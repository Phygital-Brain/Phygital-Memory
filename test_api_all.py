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
code, j = c("handtoai", {"path": "People/Tom-Becker.md"}); check("give to AI", code == 200 and j.get("handed"), j)
code, j = c("handed"); check("handed list", len(j.get("handed", [])) == 1, j)
code, j = c("unhand", {"path": "People/Tom-Becker.md"}); check("unhand", j.get("handed") == [], j)
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
