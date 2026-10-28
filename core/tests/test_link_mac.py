"""Linking your other Mac: two app copies on this Mac (first Mac on 8796, other Mac on 8799), each with its own
private Syncthing on 127.0.0.1. The other Mac pastes the link, both show the same safety words, nothing comes over
before the signed Link, then the other Mac has the same personal key and the picked memory, which opens with the same
password and stays in step both ways.

Run: uv run python test_link_mac.py   (needs a fresh test folder: make_test_vault.py --fresh)
"""
import json
import subprocess
import time

from test_syncthing_share import A, APPROVER_PW, B, api, check, cleanup, ok, servers, tmp, wait


def identity(who):
    r = subprocess.run(["security", "find-generic-password", "-s", f"Phygital Memory identity TEST {who}", "-a", "x25519", "-w"],
                       capture_output=True, text=True)
    return r.stdout.strip()


def main():
    procs = servers()
    try:
        fa = api(A, "folders")["folders"][0]["id"]
        pa = api(A, "unlock", {"password": "12345678", "folder": fa})["pass"]
        api(A, "myname", {"name": "Max"})
        api(A, "shareinvite", {"role": "edit", "folder": fa}, pa)   # makes the first Mac's personal key

        link = api(A, "linkstart").get("link", "")
        check(link.startswith("phygitalmemory://link?") and "&c=" in link, "the first Mac shows a link", link)
        check(api(B, "linkjoin", {"link": link}).get("needApprover"), "the other Mac sets up its own approval key first")
        api(B, "approversetup", {"kind": "password", "password": APPROVER_PW})
        check(api(B, "linkjoin", {"link": "phygitalmemory://join?m=x&c=y"}).get("status") == 400, "an invite isn't a link")
        j = api(B, "linkjoin", {"link": link})
        check(api(B, "linkjoin", {"link": link.split("&k=")[0]}).get("status") == 400, "a link without its key fingerprint is refused")
        check(len(j.get("words", "").split()) == 4, "the other Mac shows four safety words", j)
        s = {}
        check(wait(lambda: s.update(api(A, "linkstatus")) or s.get("state") == "asking", 60), "the first Mac sees the request", s)
        check(s.get("words") == j.get("words"), "both Macs show the same words", (s.get("words"), j.get("words")))
        check(any(m["id"] == fa for m in s.get("memories", [])), "the first Mac offers its memory")
        mac2 = tmp / "OtherMac"
        mac2.mkdir()
        check(api(B, "linkwait", {"parent": str(mac2)}).get("state") == "waiting", "nothing comes before Link is pressed")
        check(identity("A") != identity("B"), "the other Mac still has its own key before Link")

        bad = api(A, "linkanswer", {"memories": [fa], "seen": s.get("seen"), "approverPassword": "wrong password here"})
        check(bad.get("status") == 403, "Link with the wrong approval password is refused", bad)
        time.sleep(3)   # a wrong try slows the next one down
        swap = api(A, "linkanswer", {"memories": [fa], "seen": "not-what-was-shown", "approverPassword": APPROVER_PW})
        check(swap.get("status") == 409, "Link is refused if the request isn't the one whose words were shown", swap)
        r = api(A, "linkanswer", {"memories": [fa], "seen": s.get("seen"), "approverPassword": APPROVER_PW})
        check(r.get("ok") and r.get("memories") == 1, "Link, signed, goes through", r)
        signed = [json.loads(x) for x in (tmp / "max" / "approvals-signed.jsonl").read_text().splitlines()]
        check(any("as your own computer" in x["what"] and j.get("words", "?") in x["what"] for x in signed),
              "the signed yes names the computer and its safety words")
        check(api(A, "linkstatus").get("state") == "expired", "the link works only once")

        w = {}
        check(wait(lambda: w.update(api(B, "linkwait", {"parent": str(mac2)})) or w.get("state") == "done", 60), "the other Mac gets the answer", w)
        check(identity("A") == identity("B") and identity("A"), "both Macs now have the same personal key")
        check(api(B, "linkwait").get("state") == "none", "the other Mac stops waiting")
        mine = {}
        check(wait(lambda: mine.update(next((f for f in api(B, "folders")["folders"] if f["name"] == "locked-notes"), {})) or mine, 120),
              "the memory shows up on the other Mac once its files are there", api(B, "folders"))
        fb = mine.get("id")
        check(not mine.get("joined"), "it's the person's own memory there, not a shared one")
        got = api(B, "unlock", {"password": "12345678", "folder": fb})
        pb = got.get("pass")
        check(pb, "it opens with the same password", got)
        files = lambda port, f, p: {x["path"] for x in api(port, "files", {"folder": f}, p).get("files", [])}
        check(wait(lambda: files(A, fa, pa) == files(B, fb, pb), 60), "the same notes on both Macs")
        api(B, "save", {"path": "From my laptop.md", "text": "# From my laptop\n", "new": True, "folder": fb}, pb)
        check(wait(lambda: "From my laptop.md" in files(A, fa, pa), 60), "a note made on the other Mac reaches the first")
        api(A, "save", {"path": "From my desk.md", "text": "# From my desk\n", "new": True, "folder": fa}, pa)
        check(wait(lambda: "From my desk.md" in files(B, fb, pb), 60), "and one made on the first reaches the other")
        check(any(m["device"] for m in api(A, "mymacs")["macs"]) and any(m["device"] for m in api(B, "mymacs")["macs"]),
              "each Mac lists the other")
        check(wait(lambda: not list((tmp / "max" / "links").glob("pml-*")), 60), "the link's own folder is cleaned up")
    finally:
        cleanup(procs)
    print(f"\n{sum(ok)}/{len(ok)} passed")
    raise SystemExit(0 if all(ok) else 1)


if __name__ == "__main__":
    main()
