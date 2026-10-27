"""Working together, two people on one Mac: Max and Ana, each with their own personal key, one memory in a folder
both can reach (stands in for a shared cloud folder). Checks: invite, ask to join, approve, Ana opens it with her own
key (no password), both edit, view only, a wrong or used invite, remove.

Run: uv run python test_sharing.py
"""
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-share-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
from phygital_memory import keychain, sharing   # noqa: E402
from phygital_memory.memory import Memory      # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


class Person:
    """Switches whose personal key and name the sharing code uses."""
    def __init__(self, name):
        self.name, self.service = name, f"Phygital Memory identity TEST {name}"

    def __enter__(self):
        self.p = [mock.patch.object(sharing, "IDENTITY", self.service), mock.patch.object(sharing, "my_name", lambda: self.name)]
        for p in self.p:
            p.start()

    def __exit__(self, *a):
        for p in self.p:
            p.stop()


max, ana, bo = Person("Max"), Person("Ana"), Person("Bo")
shared = tmp / "Shared" / "Work"
(tmp / "Shared").mkdir()
Memory.create(shared, "maxs-password-1")
try:
    m = Memory(shared)
    m.unlock("maxs-password-1")
    m.save("Plan.md", "# Plan\nfrom Max\n", new=True)
    with max:
        link = sharing.invite(shared, m.key_raw, "edit", "Work")
        check(link.startswith("phygitalmemory://join?") and "maxs-password" not in link, "an invite link, no key or password in it")
        check([x["role"] for x in sharing.members(shared, m.key_raw)] == ["owner"], "Max is on the list as owner")
    names = [p.name for p in (shared / sharing.SHARE).rglob("*")]
    check("members.enc" in names and not any("Max" in (shared / sharing.SHARE / "members.enc").read_bytes().decode("latin1") for _ in [0]),
          "the list is encrypted (no names in the clear)")

    with ana:
        check(sharing.my_key(shared) is None, "Ana can't open it before asking")
        sharing.ask_to_join(shared, link)
    with bo:   # Bo found the folder, but has no invite
        (shared / sharing.SHARE / "requests").mkdir(exist_ok=True)
        pub = sharing.my_public()
        (shared / sharing.SHARE / "requests" / f"{sharing.member_id(pub)}.json").write_text(
            json.dumps({"pub": sharing._b64(pub), "name": "Bo", "proof": "guess"}))
    with max:
        reqs = sharing.requests(shared, m.key_raw)
        check([r["name"] for r in reqs] == ["Ana"], "Max sees Ana's request, not Bo's (no valid invite)", reqs)
        sharing.answer(shared, m.key_raw, reqs[0]["id"], True)
        check(sorted(x["name"] for x in sharing.members(shared, m.key_raw)) == ["Max", "Ana"], "Ana is in")

    with ana:
        raw = sharing.my_key(shared)
        check(raw is not None, "Ana's own key file opens for her")
        a = Memory(shared)
        a.unlock_with_key(sharing.masterkey(raw))
        check(a.read("Plan.md").startswith("# Plan"), "Ana opens the memory with her own key, no password")
        check(sharing.my_role(shared, a.key_raw) == "edit", "as an editor")
        a.save("FromAna.md", "# From Ana\n", new=True)
        a.lock()
    with bo:
        check(sharing.my_key(shared) is None, "Bo still can't open it")
    m.lock()
    m.unlock("maxs-password-1")
    check(m.read("FromAna.md").startswith("# From Ana"), "Max sees Ana's note")

    with ana:   # the same invite can't be used twice
        try:
            sharing.ask_to_join(shared, link)
            reqs = sharing.requests(shared, m.key_raw)
            check(not reqs, "a used invite doesn't work again", reqs)
        except ValueError:
            check(True, "a used invite doesn't work again")

    # view only
    with max:
        link2 = sharing.invite(shared, m.key_raw, "view", "Work")
    with bo:
        sharing.ask_to_join(shared, link2)
    with max:
        r = sharing.requests(shared, m.key_raw)
        check([x["name"] for x in r] == ["Bo"] and r[0]["role"] == "view", "Bo asks with the view invite", r)
        sharing.answer(shared, m.key_raw, r[0]["id"], True)
    with bo:
        b = Memory(shared)
        raw = sharing.my_key(shared)
        role = None
        b.unlock_with_key(sharing.masterkey(raw), read_only=True)
        role = sharing.my_role(shared, b.key_raw)
        check(role == "view" and b.read("Plan.md").startswith("# Plan"), "Bo can read")
        try:
            b.save("Bo.md", "x", new=True)
            check(False, "Bo can't change anything")
        except ValueError as e:
            check("view" in str(e), "Bo can't change anything", e)
        b.lock()

    # a no
    with max:
        link3 = sharing.invite(shared, m.key_raw, "edit", "Work")
    stranger = Person("Cy")
    with stranger:
        sharing.ask_to_join(shared, link3)
    with max:
        r = sharing.requests(shared, m.key_raw)
        sharing.answer(shared, m.key_raw, r[0]["id"], False)
        check(not sharing.requests(shared, m.key_raw) and "Cy" not in [x["name"] for x in sharing.members(shared, m.key_raw)], "a no removes the request")
    with stranger:
        check(sharing.my_key(shared) is None, "and they get nothing")

    # remove
    with max:
        ana_id = next(x["id"] for x in sharing.members(shared, m.key_raw) if x["name"] == "Ana")
        sharing.remove(shared, m.key_raw, ana_id)
        check("Ana" not in [x["name"] for x in sharing.members(shared, m.key_raw)], "Max removes Ana")
    with ana:
        check(sharing.my_key(shared) is None, "Ana can't open it any more")
    try:
        with max:
            sharing.remove(shared, m.key_raw, sharing.my_id())
        check(False, "the owner can't be removed")
    except ValueError:
        check(True, "the owner can't be removed")
    m.lock()
finally:
    for who in ("Max", "Ana", "Bo", "Cy"):
        keychain.delete(f"Phygital Memory identity TEST {who}", "x25519")

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
