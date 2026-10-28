"""Every way of sharing with the same person, end to end (Max on 8796, Ana on 8799, offline Syncthing):
invite, add someone known (no invite), view then edit, a different item, remove (her copy goes), share the same
item again, stop sharing then share it again, removed from everything but still on the list, and forget.

Run: uv run python test_share_cases.py   (needs a fresh test folder: make_test_vault.py --fresh)
"""
import time

from test_syncthing_share import A, B, api, check, cleanup, ok, servers, tmp, wait

procs = servers()
try:
    fa = api(A, "folders")["folders"][0]["id"]
    pa = api(A, "unlock", {"password": "12345678", "folder": fa})["pass"]
    api(A, "myname", {"name": "Max"})
    api(B, "myname", {"name": "Ana"})

    def ana(name):
        return next((x for x in api(B, "folders")["folders"] if x["name"] == name), None)

    waited = []   # shares that waited on Ana's list until she said yes (nothing arrives by itself)

    def take(name):
        for o in api(B, "shareoffers").get("offers", []):
            if o["label"] == name:
                waited.append((name, ana(name) is None))
                api(B, "shareofferaccept", {"id": o["id"]})

    def opened(name, secs=90):
        got = {}
        wait(lambda: take(name) or ana(name) and got.update(api(B, "keyunlock", {"folder": ana(name)["id"]})) or got.get("pass"), secs)
        return got

    def files(port, folder, pw):
        return {x["path"] for x in api(port, "files", {"folder": folder}, pw).get("files", []) if x.get("kind") != "folder"}

    def gone(name, secs=60):
        return wait(lambda: ana(name) is None, secs)

    # 1. a new person: invite, she asks, Max lets her in
    inv = api(A, "shareinvite", {"role": "edit", "path": "Projects", "folder": fa}, pa)
    api(B, "joinshared", {"link": inv["link"]})
    reqs = []
    wait(lambda: reqs.extend(r for r in api(A, "sharerequests", {"folder": fa}, pa)["requests"]) or reqs, 60)
    api(A, "shareanswer", {"id": reqs[0]["id"] if reqs else "", "allow": True, "share": inv["share"], "folder": fa}, pa)
    check(opened("Projects").get("pass"), "1. invite: Ana opens Projects")
    aid = (api(A, "sharepeople", {"path": "Ideas", "folder": fa}, pa).get("people") or [{}])[0].get("id")
    check(aid, "Ana is now someone Max can pick")

    # 2. someone known, view only, then edit
    ideas = api(A, "shareadd", {"path": "Ideas", "id": aid, "role": "view", "folder": fa}, pa).get("share")
    g = opened("Ideas")
    check(g.get("role") == "view", "2. known person: Ideas arrives with no invite, view only", g)
    check(("Ideas", True) in waited, "it waited for Ana's yes before coming onto her Mac", waited)
    check(ana("Ideas") and ana("Ideas").get("aiHidden"), "and came in hidden from AI", ana("Ideas"))
    check(api(B, "save", {"path": "Ana.md", "text": "x", "new": True, "folder": ana("Ideas")["id"]}, g.get("pass")).get("status"),
          "view only: she can't add a note")
    api(A, "sharerole", {"share": ideas, "id": aid, "role": "edit", "folder": fa}, pa)
    time.sleep(8)
    api(B, "lock", {"folder": ana("Ideas")["id"]}, g.get("pass"))
    g = opened("Ideas")
    check(g.get("role") == "edit", "made Can edit: next time she opens it, she can edit", g)
    check(api(B, "save", {"path": "From Ana.md", "text": "# hi\n", "new": True, "folder": ana("Ideas")["id"]}, g.get("pass")).get("path"),
          "and her note saves")
    check(wait(lambda: "Ideas/From Ana.md" in files(A, fa, pa), 60), "and reaches Max's Ideas")

    # 3. something else: one file, to the same person
    day = api(A, "shareadd", {"path": "Daily/2026-10-20.md", "id": aid, "role": "edit", "folder": fa}, pa).get("share")
    check(opened("2026-10-20.md").get("pass"), "3. a different item (one file) arrives too")

    # 4. remove from one: only that copy goes
    api(A, "shareremove", {"path": "Ideas", "id": aid, "folder": fa}, pa)
    check(gone("Ideas"), "4. removed from Ideas: her copy goes")
    check(ana("Projects") and ana("2026-10-20.md"), "the others stay")

    # 5. the same item again, after removing her
    check(api(A, "shareadd", {"path": "Ideas", "id": aid, "role": "edit", "folder": fa}, pa).get("share"),
          "5. Max shares Ideas with her again")
    check(opened("Ideas", 120).get("pass"), "Ideas comes back and opens")
    check(wait(lambda: "From Ana.md" in files(B, ana("Ideas")["id"], opened("Ideas").get("pass")), 60), "with what's in it now")

    # 6. stop sharing an item, then share the same item again
    api(A, "sharestop", {"share": day, "folder": fa}, pa)
    check(gone("2026-10-20.md"), "6. Stop sharing the file: her copy goes")
    check(api(A, "shareadd", {"path": "Daily/2026-10-20.md", "id": aid, "role": "view", "folder": fa}, pa).get("share"),
          "Max shares that file again (a fresh share)")
    check(opened("2026-10-20.md", 120).get("pass"), "it comes back to her")

    # 7. removed from everything: still on Max's list, and can get something new
    for name, path in (("Projects", "Projects"), ("Ideas", "Ideas"), ("2026-10-20.md", "Daily/2026-10-20.md")):
        sid = next(p["id"] for p in api(A, "shareinfo", {"folder": fa}, pa)["parts"] if p["path"] == path)
        api(A, "shareremove", {"share": sid, "id": aid, "folder": fa}, pa)
    check(gone("Projects") and gone("Ideas") and gone("2026-10-20.md"), "7. removed from everything: all her copies go")
    check([p["name"] for p in api(A, "sharepeople", {"path": "People", "folder": fa}, pa)["people"]] == ["Ana"],
          "she's still on Max's list")
    api(A, "shareadd", {"path": "People", "id": aid, "role": "edit", "folder": fa}, pa)
    check(opened("People", 120).get("pass"), "and something new still reaches her with no invite")

    # 8. forget her
    check(api(A, "shareforget", {"id": aid, "folder": fa}, pa).get("ok"), "8. Max forgets Ana")
    check(gone("People"), "her copy of People goes")
    check(not api(A, "sharepeople", {"path": "Ideas", "folder": fa}, pa)["people"], "she's off Max's list")
    check(api(A, "shareadd", {"path": "Ideas", "id": aid, "folder": fa}, pa).get("status") == 404,
          "sharing with her again needs a new invite")
    check(not api(B, "folders")["folders"], "Ana's list is empty")
finally:
    cleanup(procs)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
