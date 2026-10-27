"""Sharing one folder, or one file, not the whole memory: Max shares "Projects" (can edit) and "People/Tom-Becker.md"
(can view) with Ana. Nothing comes over before his yes; then she gets only that part, in its own locked memory with
its own key. Edits go both ways for the folder; the view-only file only follows Max. The rest of his memory never
reaches her.

Run: uv run python test_share_parts.py   (needs a fresh test folder: make_test_vault.py --fresh)
"""
import time

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

    sf, ff, pf = join("People/Tom-Becker.md", "view", "Tom-Becker.md")
    check(wait(lambda: files(B, ff, pf) == {"Tom-Becker.md"}, 60), "one file shared: only that file reaches Ana")
    check(api(B, "save", {"path": "Tom-Becker.md", "text": "# Ana tries\n", "folder": ff}, pf).get("status") in (400, 403, 500),
          "view only: Ana can't change it")
    api(A, "save", {"path": "People/Tom-Becker.md", "text": "# Tom\nnew phone\n", "folder": fa}, pa)
    check(wait(lambda: "new phone" in api(B, "read", {"path": "Tom-Becker.md", "folder": ff}, pf)["text"], 60),
          "Max's change to the file reaches Ana")

    parts = api(A, "shareinfo", {"folder": fa}, pa).get("parts", [])
    check({p["path"] for p in parts} == {"Work", "People/Tom-Becker.md"} and all(p["people"] == ["Ana"] for p in parts),
          "the memory's Share window lists what's shared and with whom", parts)
    api(A, "sharestop", {"share": sf, "folder": fa}, pa)
    time.sleep(3)
    api(A, "save", {"path": "People/Tom-Becker.md", "text": "# Tom\nafter stop\n", "folder": fa}, pa)
    time.sleep(10)
    check("after stop" not in api(B, "read", {"path": "Tom-Becker.md", "folder": ff}, pf)["text"],
          "after Stop sharing, Ana gets no more changes")
finally:
    cleanup(procs)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
