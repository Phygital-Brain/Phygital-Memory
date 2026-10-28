"""S3 / R2 backup, offline: rclone's own S3 server on 127.0.0.1 plays Amazon S3. Checks: wrong keys and a missing
bucket are caught, the first copy goes up encrypted, changes follow by themselves, a replaced file is kept in
history, a big file (over GitHub's 95 MB) goes up, it survives a restart, a memory comes back from it (and is
refused when it's already here), and stopping leaves the bucket alone.

Run: uv run python test_s3_backup.py
"""
import io
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-s3-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
os.environ["PHYGITAL_MEMORY_CLOUD_KEYCHAIN"] = "Phygital Memory cloud TEST"
from phygital_memory import cloud, folders as F   # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def wait(cond, secs=40):
    end = time.time() + secs
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.5)
    return False


store = tmp / "s3"
(store / "notes-backup").mkdir(parents=True)   # the bucket (the app never makes buckets)
server = subprocess.Popen(["rclone", "serve", "s3", str(store), "--addr", "127.0.0.1:8798", "--auth-key", "AKIATEST,secret-test"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
conn = cloud.make_s3_conn("s3", "AKIATEST", "us-east-1", "http://127.0.0.1:8798")
fast = [mock.patch.object(cloud, "MIRROR_AFTER", 0.5), mock.patch.object(cloud, "MIRROR_EVERY", 2)]
for p in fast:
    p.start()
try:
    check(cloud.make_s3_conn("r2", "KEY", "0123456789abcdef0123456789abcdef")["url"].endswith(".r2.cloudflarestorage.com"),
          "a Cloudflare R2 address is built from the account ID")
    for bad, what in ((lambda: cloud.check_bucket(conn, "notes-backup", "wrong-secret"), "wrong keys are caught"),
                      (lambda: cloud.check_bucket(conn, "no-such-bucket", "secret-test"), "a missing bucket is caught")):
        try:
            bad()
            check(False, what)
        except cloud.CloudError:
            check(True, what)
    cloud.check_bucket(conn, "notes-backup", "secret-test")
    cloud.save_password(conn, "secret-test")

    (tmp / "Mac").mkdir()
    fs = F.Folders(None)
    f = fs.get(fs.create(str(tmp / "Mac"), "Work", "password-1")["id"])
    f.memory.unlock("password-1")
    f.memory.save("Plan.md", "# Plan\nsecret plan text\n", new=True)
    info = fs.to_s3(f.id, conn, "notes-backup")
    cur = store / "notes-backup" / "Work" / "current"
    check(info["s3"] == "Amazon S3 · notes-backup/Work" and (cur / "vault.cryptomator").exists(), "the first copy goes up", info)
    blob = b"".join(p.read_bytes() for p in cur.rglob("*") if p.is_file())
    check(b"secret plan text" not in blob, "everything in the bucket is encrypted")

    count = lambda: sum(1 for _ in cur.rglob("*.c9r"))
    n = count()
    f.memory.save("Second.md", "# Second\n", new=True)
    check(wait(lambda: count() > n), "a change goes up by itself")
    f.memory.save("Plan.md", "# Plan\nchanged\n")
    check(wait(lambda: (store / "notes-backup" / "Work" / "history").exists() and any((store / "notes-backup" / "Work" / "history").rglob("*.c9r"))),
          "the file it replaced is kept in history")

    f.memory.import_stream("Video/big.bin", io.BytesIO(os.urandom(120 * 1024 * 1024)))
    check(wait(lambda: any(p.stat().st_size > 100_000_000 for p in cur.rglob("*") if p.is_file()), 90),
          "a 120 MB file goes up (too big for GitHub)")

    f.s3.stop()
    fs = F.Folders(None)
    f = fs.get(f.id)
    check(f.s3 is not None and f.info()["s3"], "after a restart it keeps backing up")

    try:
        fs.from_s3(conn, "notes-backup/Work/current", str(tmp / "Mac2"))
        check(False, "the same memory already here is refused")
    except ValueError as e:
        check("already here" in str(e) and not (tmp / "Mac2" / "Work").exists(), "the same memory already here is refused", e)

    found = cloud.find_memories(conn, 4, "notes-backup")
    check([m["path"] for m in found if m["path"].endswith("/current")] == ["notes-backup/Work/current"], "the backup is found in the bucket", found)
    f.s3.sync_once()
    f.s3.stop()
    gone = fs.items.pop(f.id)   # like another Mac
    r = fs.get(fs.from_s3(conn, "notes-backup/Work/current", str(tmp / "Mac2"))["id"])
    r.memory.unlock("password-1")
    check(r.memory.read("Plan.md").startswith("# Plan\nchanged") and r.memory.read("Second.md").startswith("# Second"),
          "a memory comes back from the bucket with every note")
    size = next(x["size"] for x in r.memory.list_files() if x["path"] == "Video/big.bin")
    check(size == 120 * 1024 * 1024, "and the big file", size)
    r.memory.lock()

    fs.items[gone.id] = gone
    fs.items.pop(r.id)
    where = fs.stop_s3(gone.id)
    check(not fs.get(gone.id).s3_at and (cur / "vault.cryptomator").exists(), "stop: the bucket keeps what's there", where)
finally:
    for p in fast:
        p.stop()
    server.terminate()
    cloud.forget_password(conn)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
