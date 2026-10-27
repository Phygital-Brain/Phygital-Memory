"""Big files in a shared folder: a 120 MB file is copied into the share and back in parts, with little memory used,
and nothing readable written to disk. Run: uv run python test_big_share.py"""
import hashlib
import os
import resource
import shutil
import tempfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-big-"))
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_IDENTITY_KEYCHAIN"] = "Phygital Memory identity TEST big"
from phygital_memory import shares, sharing   # noqa: E402
from phygital_memory.memory import Memory      # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6   # macOS: bytes


def fhash(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while part := f.read(1 << 20):
            h.update(part)
    return h.hexdigest()


SIZE = 120_000_000
try:
    Memory.create(tmp / "mem", "test-password-123")
    a = Memory(tmp / "mem")
    a.unlock("test-password-123")
    big = tmp / "big.bin"
    with open(big, "wb") as f:   # made a part at a time, so making it doesn't count against the copy
        for i in range(SIZE // 1_000_000):
            f.write(hashlib.sha256(str(i).encode()).digest() * 31250)
    want = fhash(big)
    a.import_paths("Video", [str(big)])
    a.save("Video/notes.md", "# Cut list\n")
    big.unlink()
    vid = sharing._vault_id(a.folder)
    s = shares.create(vid, "Video", "folder")
    before = rss_mb()
    shares.sync(s["id"], a)
    grew = rss_mb() - before
    b = shares._open[s["id"]]
    check(b.file_hash("big.bin") == want, "the 120 MB file arrives in the share, whole")
    check(grew < 60, "copied in parts: memory grew far less than the file's size", f"{grew:.0f} MB")
    check(not any(p.suffix in (".bin", ".md") for p in shares.path_of(s["id"]).rglob("*")),
          "nothing readable on disk in the share")
    check(b.read("notes.md").startswith("# Cut list"), "the small note comes along too")

    with open(tmp / "edit.bin", "wb") as f:   # their side changes the big file
        for i in range(SIZE // 1_000_000):
            f.write(hashlib.sha256(f"x{i}".encode()).digest() * 31250)
    want2 = fhash(tmp / "edit.bin")
    # someone with Can edit is needed for changes to come back: add a stand-in member
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    pub = X25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    sharing.add_member(shares.path_of(s["id"]), shares.key_of(s["id"]),
                       {"id": sharing.member_id(pub), "name": "Ana", "pub": sharing._b64(pub)}, "edit")
    with open(tmp / "edit.bin", "rb") as f:
        b.put_stream("big.bin", f)
    (tmp / "edit.bin").unlink()
    shares.sync(s["id"], a)
    check(a.file_hash("Video/big.bin") == want2, "their change to the big file comes back, whole")
    check(shares.sync(s["id"], a) == 0, "next pass: nothing to copy (fingerprints remembered)")
    a.lock()
    shares.close_for(vid)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
    os.system('security delete-generic-password -s "Phygital Memory identity TEST big" -a x25519 >/dev/null 2>&1')

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
