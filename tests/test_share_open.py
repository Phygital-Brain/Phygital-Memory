"""Sharing an Open memory: Max's memory is a normal folder. He shares it with Ana (can edit) and one folder of it
with her (can view). It travels locked, like any share, and on Ana's Mac it becomes a normal folder in Documents ›
Shared with me that her AI can read. A file changed on disk on either side reaches the other; the view-only copy only
follows Max; when he removes her, her folder is deleted.

Run: uv run python test_share_open.py
"""
import os
import time
from pathlib import Path

from test_syncthing_share import tmp

os.environ["PHYGITAL_MEMORY_SHARED_COPIES"] = str(tmp / "AnaDocs" / "Shared with me")   # Ana's server inherits it
from test_syncthing_share import A, B, api, check, cleanup, ok, servers, wait  # noqa: E402

procs = servers()
try:
    api(A, "myname", {"name": "Max"})
    api(B, "myname", {"name": "Ana"})
    (tmp / "MaxMac").mkdir()
    fa = api(A, "createfolder", {"parent": str(tmp / "MaxMac"), "name": "Studio", "kind": "open"})["folder"]["id"]
    pa = api(A, "unlock", {"password": "", "folder": fa})["pass"]
    studio = tmp / "MaxMac" / "Studio"
    api(A, "save", {"path": "Projects/Kite.md", "text": "# Kite\nfirst draft\n", "folder": fa}, pa)
    api(A, "save", {"path": "Plan.md", "text": "# Plan\n", "folder": fa}, pa)

    def join(path, role):
        inv = api(A, "shareinvite", {"role": role, "folder": fa, **({"path": path} if path else {})}, pa)
        check(inv.get("share"), f"an invite for {path or 'the whole memory'}", inv)
        j = api(B, "joinshared", {"link": inv.get("link", "")})
        fb = j.get("folder", {}).get("id")
        reqs = []
        check(wait(lambda: reqs.extend(r for r in api(A, "sharerequests", {"folder": fa}, pa)["requests"]
                                       if r.get("share") == inv.get("share")) or reqs, 60), "Max sees Ana asking")
        api(A, "shareanswer", {"id": reqs[0]["id"] if reqs else "", "allow": True, "share": inv.get("share"), "folder": fa}, pa)
        got = {}
        check(wait(lambda: got.update(api(B, "keyunlock", {"folder": fb})) or got.get("pass"), 90), "Ana opens it with her own key", got)
        return fb, got.get("pass")

    fb, pb = join("", "edit")
    info = next((x for x in api(B, "folders")["folders"] if x["id"] == fb), {})
    copy = Path(info.get("path", "/nonexistent"))
    check(info.get("kind") == "open" and copy.parent == tmp / "AnaDocs" / "Shared with me",
          "on Ana's Mac it's an Open memory, in Documents › Shared with me", info)
    check(wait(lambda: (copy / "Projects" / "Kite.md").read_text().endswith("first draft\n"), 60),
          "Max's notes are normal files on Ana's Mac")
    check(not (copy / "vault.cryptomator").exists() and not (copy / "d").exists(), "no encrypted files in her folder")

    (copy / "From Ana.md").write_text("# From Ana\nher AI wrote this\n")   # her AI, straight into the folder
    check(wait(lambda: (studio / "From Ana.md").exists(), 60), "a file Ana's AI writes reaches Max's folder")
    (studio / "Plan.md").write_text("# Plan\nchanged on Max's disk\n")   # Max's AI, straight into his folder
    check(wait(lambda: "changed on Max's disk" in (copy / "Plan.md").read_text(), 60), "a file Max's AI changes reaches Ana")
    hist = api(A, "sharehistory", {"folder": fa}, pa).get("history", [])
    check(any(h["who"] == "Ana" for h in hist), "the history says what Ana changed", hist[:3])

    fv, pv = join("Projects", "view")
    vinfo = next((x for x in api(B, "folders")["folders"] if x["id"] == fv), {})
    vcopy = Path(vinfo.get("path", "/nonexistent"))
    check(wait(lambda: (vcopy / "Kite.md").exists(), 60) and not (vcopy / "Plan.md").exists(),
          "the view-only folder arrives alone, as normal files")
    (vcopy / "Kite.md").write_text("# Kite\nAna tries to change it\n")
    time.sleep(8)
    check("Ana tries" not in (studio / "Projects" / "Kite.md").read_text(), "view only: Ana's change doesn't reach Max")
    check(wait(lambda: "Ana tries" not in (vcopy / "Kite.md").read_text(), 30), "and her copy goes back to Max's version")

    people = api(A, "shareinfo", {"folder": fa}, pa).get("members", [])
    ana = next((m for m in people if m.get("name") == "Ana"), {})
    api(A, "shareremove", {"id": ana.get("id", ""), "folder": fa}, pa)
    check(wait(lambda: not any(x["id"] == fb for x in api(B, "folders")["folders"]), 60), "removed: the memory leaves Ana's list")
    check(wait(lambda: not copy.exists(), 30), "and her normal folder is deleted", copy)
finally:
    cleanup(procs)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
