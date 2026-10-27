"""Sharing one folder, or one file, not the whole memory: Max shares "Projects" (can edit) and "People/Tom-Becker.md"
(can view) with Ana. Nothing comes over before his yes; then she gets only that part, in its own locked memory with
its own key. Edits go both ways for the folder; the view-only file only follows Max. The rest of his memory never
reaches her.

Run: uv run python test_share_parts.py   (needs a fresh test folder: make_test_vault.py --fresh)
"""
import time
from pathlib import Path

from test_syncthing_share import A, B, ROOT, api, check, cleanup, ok, servers, tmp, wait

procs = servers()
try:
    fa = api(A, "folders")["folders"][0]["id"]
    pa = api(A, "unlock", {"password": "12345678", "folder": fa})["pass"]
    api(A, "myname", {"name": "Max"})
    api(B, "myname", {"name": "Ana"})
    (tmp / "AnaMac").mkdir()

    def join(path, role, folder_name):
        inv = api(A, "shareinvite", {"role": role, "path": path, "folder": fa}, pa)
        check(inv.get("share") and "&k=" in inv.get("link", ""), f"an invite for {path} alone", inv)
        j = api(B, "joinshared", {"link": inv["link"], "parent": str(tmp / "AnaMac")})
        fb = j.get("folder", {}).get("id")
        reqs = []
        check(wait(lambda: reqs.extend(r for r in api(A, "sharerequests", {"folder": fa}, pa)["requests"]
                                       if r.get("share") == inv["share"]) or reqs, 60), f"Max sees Ana asking for {path}")
        target = tmp / "AnaMac" / folder_name
        check(not (target / "vault.cryptomator").exists(), f"nothing of {path} reaches Ana before the yes")
        r = reqs[0] if reqs else {}
        check(r.get("what") == path, "the request says what it's for", r)
        api(A, "shareanswer", {"id": r.get("id"), "allow": True, "share": inv["share"], "folder": fa}, pa)
        got = {}
        check(wait(lambda: got.update(api(B, "keyunlock", {"folder": fb})) or got.get("pass"), 90), f"Ana opens {path}", got)
        return inv["share"], fb, got.get("pass")

    def files(port, folder, pw):
        return {x["path"] for x in api(port, "files", {"folder": folder}, pw)["files"] if x.get("kind") != "folder"}

    sp, fp, pp = join("Projects", "edit", "Projects")
    check(wait(lambda: files(B, fp, pp) >= {"Lighthouse-App.md", "Garden-Planner.md"}, 60), "the folder's notes reach Ana")
    check(files(B, fp, pp) == {"Lighthouse-App.md", "Garden-Planner.md"}, "and nothing else of Max's memory",
          files(B, fp, pp))
    api(B, "save", {"path": "From Ana.md", "text": "# From Ana\n", "new": True, "folder": fp}, pp)
    check(wait(lambda: "Projects/From Ana.md" in files(A, fa, pa), 60), "Ana's new note lands in Max's Projects folder")
    api(A, "save", {"path": "Projects/Garden-Planner.md", "text": "# Garden\nchanged by Max\n", "folder": fa}, pa)
    check(wait(lambda: "changed by Max" in api(B, "read", {"path": "Garden-Planner.md", "folder": fp}, pp)["text"], 60),
          "Max's edit reaches Ana")
    api(A, "move", {"from": "Projects", "to": "Work", "folder": fa}, pa)
    api(A, "save", {"path": "Work/After rename.md", "text": "# Still shared\n", "new": True, "folder": fa}, pa)
    check(wait(lambda: "After rename.md" in files(B, fp, pp), 60), "renaming the folder keeps it shared")

    hist = api(A, "sharehistory", {"share": sp, "folder": fa}, pa).get("history", [])
    check(any(h["who"] == "Ana" and h["path"] == "From Ana.md" and h["what"] == "added" for h in hist)
          and any(h["who"] == "Max" and h["path"] == "Garden-Planner.md" and h["what"] == "edited" for h in hist),
          "History says who changed what (Ana added, Max edited)", hist[:5])
    check(any(h["who"] == "Max" for h in api(B, "sharehistory", {"folder": fp}, pp).get("history", [])),
          "Ana sees the same history")

    people = api(A, "sharepeople", {"path": "Ideas", "folder": fa}, pa).get("people", [])
    check([p["name"] for p in people] == ["Ana"], "Ana is on Max's list of people he already shares with", people)
    add = api(A, "shareadd", {"path": "Ideas", "id": people[0]["id"] if people else "", "role": "edit", "folder": fa}, pa)
    check(add.get("share"), "Max adds Ana to Ideas with no invite", add)
    fi = {}
    check(wait(lambda: fi.update(next((x for x in api(B, "folders")["folders"] if x["name"] == "Ideas"), {})) or fi, 60),
          "Ideas shows up on Ana's side by itself (Shared with me)")
    gi = {}
    check(wait(lambda: gi.update(api(B, "keyunlock", {"folder": fi.get("id")})) or gi.get("pass"), 90), "Ana opens Ideas with her own key", gi)
    check(wait(lambda: "Pocket-Library.md" in files(B, fi.get("id"), gi.get("pass")), 60), "and its notes are there")
    check(not api(A, "sharepeople", {"path": "Ideas", "folder": fa}, pa).get("people"), "once in, she's off the pick list")
    ideas_dir = Path(fi.get("path", "/nonexistent"))
    api(A, "shareremove", {"share": add.get("share"), "id": people[0]["id"] if people else "", "folder": fa}, pa)
    check(wait(lambda: not any(x["name"] == "Ideas" for x in api(B, "folders")["folders"]), 60),
          "removed from Ideas: it leaves Ana's list")
    check(not ideas_dir.exists(), "and her copy is deleted from her Mac", ideas_dir)

    sf, ff, pf = join("People/Tom-Becker.md", "view", "Tom-Becker.md")
    check(wait(lambda: files(B, ff, pf) == {"Tom-Becker.md"}, 60), "one file shared: only that file reaches Ana")
    check(api(B, "save", {"path": "Tom-Becker.md", "text": "# Ana tries\n", "folder": ff}, pf).get("status") in (400, 403, 500),
          "view only: Ana can't change it")
    api(A, "save", {"path": "People/Tom-Becker.md", "text": "# Tom\nnew phone\n", "folder": fa}, pa)
    check(wait(lambda: "new phone" in api(B, "read", {"path": "Tom-Becker.md", "folder": ff}, pf)["text"], 60),
          "Max's change to the file reaches Ana")

    parts = api(A, "shareinfo", {"folder": fa}, pa).get("parts", [])
    parts = [p for p in parts if p["people"]]   # Ideas stays listed, with nobody in it after the removal
    check({p["path"] for p in parts} == {"Work", "People/Tom-Becker.md"} and all(p["people"] == ["Ana"] for p in parts),
          "the memory's Share window lists what's shared and with whom", parts)
    api(A, "sharestop", {"share": sf, "folder": fa}, pa)
    check(wait(lambda: not any(x["id"] == ff for x in api(B, "folders")["folders"]), 60),
          "after Stop sharing, the file leaves Ana's list and her copy is deleted")
    check(wait(lambda: not any(p["path"] == "People/Tom-Becker.md" for p in api(A, "shareinfo", {"folder": fa}, pa).get("parts", [])), 30),
          "and it's gone from Max's shared list")
finally:
    cleanup(procs)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
