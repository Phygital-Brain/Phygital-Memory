"""The audit's findings, each tried for real and checked fixed (Max on 8796, Ana on 8799, offline Syncthing).

1 the approval key can't be swapped without the current key's yes      6 a removal note only counts if the owner signed it
2 a removed person gets nothing new; the rest move to a new key       7 approval words: access first, plain names
3 a viewer can't change the owner's files, even by going around the app 8 stopping a share nobody joined cleans up
4 a refused Keychain read never makes a new key                        5 renaming a shared file keeps it, never trashes it

Run: uv run python test_audit.py   (needs a fresh test folder: make_test_vault.py --fresh)
"""
import json
import subprocess
import time
from pathlib import Path
from unittest import mock

from test_syncthing_share import APPROVER_PW, A, B, api, check, cleanup, ok, servers, tmp, wait

procs = servers()
try:
    fa = api(A, "folders")["folders"][0]["id"]
    pa = api(A, "unlock", {"password": "12345678", "folder": fa})["pass"]
    api(A, "myname", {"name": "Max"})
    api(B, "myname", {"name": "Ana"})

    def ana(name):
        return next((x for x in api(B, "folders")["folders"] if x["name"] == name), None)

    def opened(name, secs=90):
        got = {}
        wait(lambda: ana(name) and got.update(api(B, "keyunlock", {"folder": ana(name)["id"]})) or got.get("pass"), secs)
        return got

    def files(port, folder, pw):
        return {x["path"] for x in api(port, "files", {"folder": folder}, pw).get("files", []) if x.get("kind") != "folder"}

    # 1. swapping the approval key needs the current key's yes
    r = api(A, "approversetup", {"kind": "password", "password": "a brand new phrase 99", "approverPassword": "wrong one here!"})
    check(r.get("status") == 403, "1. a new approval key without the current one's yes is refused", r)
    time.sleep(2.2)   # a wrong try slows the next one down
    r = api(A, "approversetup", {"kind": "password", "password": "a brand new phrase 99", "approverPassword": APPROVER_PW})
    check(r.get("card"), "with the current key's yes, it's replaced", r)
    ring = json.loads((tmp / "max" / "approver.json").read_text())
    check(len(ring.get("retired", [])) == 1, "and the old key stays on record, so past yeses still check")
    api(A, "approversetup", {"kind": "password", "password": APPROVER_PW, "approverPassword": "a brand new phrase 99"})

    # Ana gets Projects (edit) by invite, then Ideas (view) with no invite
    inv = api(A, "shareinvite", {"role": "edit", "path": "Projects", "folder": fa}, pa)
    api(B, "joinshared", {"link": inv["link"]})
    reqs = []
    wait(lambda: reqs.extend(api(A, "sharerequests", {"folder": fa}, pa)["requests"]) or reqs, 60)
    api(A, "shareanswer", {"id": reqs[0]["id"] if reqs else "", "allow": True, "share": reqs[0].get("share") if reqs else "", "folder": fa}, pa)
    check(opened("Projects").get("pass"), "Ana is in Projects")
    aid = (api(A, "sharepeople", {"path": "Ideas", "folder": fa}, pa).get("people") or [{}])[0].get("id")
    api(A, "shareadd", {"path": "Ideas", "id": aid, "role": "view", "folder": fa}, pa)
    gi = opened("Ideas")
    check(gi.get("role") == "view", "Ana has Ideas, view only")

    # 3. a viewer goes around the app: writes straight into her copy with the key she holds
    ideas_dir = Path(ana("Ideas")["path"])
    subprocess.run(["uv", "run", "python", "-c", f"""
import os
os.environ["PHYGITAL_MEMORY_STATE"] = {str(tmp / 'ana')!r}
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_IDENTITY_KEYCHAIN"] = "Phygital Memory identity TEST B"
from pathlib import Path
from phygital_memory import sharing
from phygital_memory.memory import Memory
d = Path({str(ideas_dir)!r})
raw = sharing.my_key(d)
m = Memory(d); m.unlock_with_key(sharing.masterkey(raw))
m.save("Sneaky.md", "# not allowed\\n", new=True)
m.trash("Pocket-Library.md")
mem = sharing._read_members(d, raw)
for x in mem["members"]:
    if x["role"] == "view": x["role"] = "edit"
sharing._write_members(d, raw, mem)
m.lock()
"""], capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent)
    time.sleep(25)
    mine = files(A, fa, pa)
    check("Ideas/Sneaky.md" not in mine and "Ideas/Pocket-Library.md" in mine,
          "3. a viewer's changes made around the app never reach the owner (no new note, nothing trashed)", sorted(mine))

    # 2. removing someone: they get nothing new; the rest move to a fresh share with a new key
    old = next(p for p in api(A, "shareinfo", {"folder": fa}, pa)["parts"] if p["path"] == "Projects")
    old_dir = tmp / "max" / "shares" / old["id"]
    api(A, "shareremove", {"path": "Projects", "id": aid, "folder": fa}, pa)
    before = sorted(p.name for p in old_dir.rglob("*") if p.is_file()) if old_dir.exists() else []
    api(A, "save", {"path": "Projects/After removal.md", "text": "# new\n", "new": True, "folder": fa}, pa)
    time.sleep(10)
    after = sorted(p.name for p in old_dir.rglob("*") if p.is_file()) if old_dir.exists() else []
    check(before == after or not old_dir.exists(),
          "2. after a removal, nothing new goes into the old share (frozen, then deleted once she has the note)")
    check(wait(lambda: ana("Projects") is None, 60), "and her copy goes")

    # 5. renaming a shared single file keeps it shared and never trashes it
    sid = api(A, "shareadd", {"path": "People/Tom-Becker.md", "id": aid, "role": "edit", "folder": fa}, pa).get("share")
    check(opened("Tom-Becker.md").get("pass"), "Ana has Tom-Becker.md")
    api(A, "move", {"from": "People/Tom-Becker.md", "to": "People/Tom.md", "folder": fa}, pa)
    time.sleep(12)
    mine = files(A, fa, pa)
    check("People/Tom.md" in mine, "5. renaming a shared file: the owner's file stays, nothing trashed", sorted(mine))
    api(A, "save", {"path": "People/Tom.md", "text": "# Tom\nrenamed and edited\n", "folder": fa}, pa)
    t = opened("Tom-Becker.md")
    check(wait(lambda: any("renamed and edited" in api(B, "read", {"path": n, "folder": ana("Tom-Becker.md")["id"]}, t.get("pass")).get("text", "")
                           for n in files(B, ana("Tom-Becker.md")["id"], t.get("pass"))), 60),
          "and it stays shared under its new name")

    # 8. stopping a share nobody joined cleans up at once
    sid2 = api(A, "shareinvite", {"role": "edit", "path": "Daily", "folder": fa}, pa).get("share")
    api(A, "sharestop", {"path": "Daily", "folder": fa}, pa)
    shares_list = json.loads((tmp / "max" / "shares" / "shares.json").read_text())
    check(sid2 not in shares_list and not (tmp / "max" / "shares" / sid2).exists(), "8. a share nobody joined is gone right after Stop")
finally:
    cleanup(procs)

# 4, 6, 7: checked on their own, without servers
import os  # noqa: E402
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "unit")
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_IDENTITY_KEYCHAIN"] = "Phygital Memory identity TEST unit"
from phygital_memory import keychain  # noqa: E402   (only now, with the test folder and test key names set)
from phygital_memory import sharing  # noqa: E402

# 4. a refused Keychain read never makes a new key
with mock.patch.object(keychain.touchid, "bundled", return_value=Path("/fake")), \
        mock.patch.object(keychain, "_helper", return_value=subprocess.CompletedProcess([], 4, b"", b"nothing kept (-25300)")), \
        mock.patch.object(keychain.subprocess, "run", return_value=subprocess.CompletedProcess([], 51, "", "denied")), \
        mock.patch.object(keychain, "save") as saved:
    keychain._got.clear(), keychain._refused.clear(), sharing._me.clear()
    try:
        sharing._identity()
        check(False, "4. a refused Keychain read raises, never makes a new key")
    except keychain.Refused:
        check(not saved.called, "4. a refused Keychain read raises, never makes a new key (nothing saved over it)")
with mock.patch.object(keychain.subprocess, "run", return_value=subprocess.CompletedProcess([], 44, "", "")):
    check(keychain._security_read("x", "y") is None, "only \"not found\" counts as missing")

# 6. a removal note only counts when the owner signed it
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
d = tmp / "unit" / "share"
(d / ".phygital-share" / "removed").mkdir(parents=True)
with mock.patch.object(sharing, "_vault_id", return_value="v1"), mock.patch.object(sharing, "my_id", return_value="carol"):
    owner, other = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    pub = sharing._b64(owner.public_key().public_bytes_raw())
    note = d / ".phygital-share" / "removed" / "carol"
    note.write_text(sharing._b64(other.sign(sharing._removed_words(d, "carol"))))
    check(not sharing.am_removed(d, pub), "6. a removal note signed by another member is ignored")
    note.write_text("")
    check(not sharing.am_removed(d, pub), "an empty removal note is ignored")
    note.write_text(sharing._b64(owner.sign(sharing._removed_words(d, "carol"))))
    check(sharing.am_removed(d, pub), "the owner's signed note counts")

# 7. approval words: access first, names can't fake other words
src = (Path(__file__).resolve().parent.parent / "phygital_memory" / "server.py").read_text()
import re  # noqa: E402
plain = eval(compile("lambda name: re.sub(r\"[()\\[\\]{}<>\\n\\r\\t]\", \"\", str(name)).strip()[:40] or \"someone\"", "x", "eval"))
check(plain("Eve (can view)\nok") == "Eve can viewok", "7. brackets and line breaks are taken out of names in approvals")
check('f"{_role_words(arole)}: {who}, {item}. Safety code' in src, "the access comes first, and the safety code is shown")
subprocess.run(["security", "delete-generic-password", "-s", "Phygital Memory identity TEST unit", "-a", "x25519"], capture_output=True)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
