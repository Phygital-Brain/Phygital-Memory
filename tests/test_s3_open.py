"""An Open memory backed up to S3 / R2, offline (rclone's own S3 server on 127.0.0.1:8798 plays Amazon S3): its notes
go up as normal files, changes follow, the bucket lists it, and it comes back as an Open memory.

Run: uv run python test_s3_open.py
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-s3open-"))
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
(store / "notes-backup").mkdir(parents=True)
server = subprocess.Popen(["rclone", "serve", "s3", str(store), "--addr", "127.0.0.1:8798", "--auth-key", "AKIATEST,secret-test"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
conn = cloud.make_s3_conn("s3", "AKIATEST", "us-east-1", "http://127.0.0.1:8798")
fast = [mock.patch.object(cloud, "MIRROR_AFTER", 0.5), mock.patch.object(cloud, "MIRROR_EVERY", 2)]
for p in fast:
    p.start()
try:
    cloud.check_bucket(conn, "notes-backup", "secret-test")
    cloud.save_password(conn, "secret-test")
    (tmp / "Mac").mkdir()
    fs = F.Folders(None)
    f = fs.get(fs.create(str(tmp / "Mac"), "Notes", None)["id"])
    f.memory.unlock("")
    f.memory.save("Plan.md", "# Plan\nreadable in the bucket\n", new=True)
    F.memory_id(f)
    info = fs.to_s3(f.id, conn, "notes-backup")
    check(info["s3"] and info["kind"] == "open", "S3 backup is on for an Open memory", info)
    blob = b"".join(p.read_bytes() for p in store.rglob("*") if p.is_file())
    check(b"readable in the bucket" in blob, "its notes are normal files in the bucket")
    f.memory.save("Second.md", "# Second\n", new=True)
    check(wait(lambda: any(p.name == "Second.md" for p in store.rglob("*"))), "a change follows by itself")
    found = cloud.find_memories(conn, 4, "notes-backup")
    check(any(m["path"] == "notes-backup/Notes/current" for m in found), "the bucket lists it", found)
    fs.stop_s3(f.id)
    back = fs.from_s3(conn, "notes-backup/Notes/current", str(tmp / "Mac2"))
    check(back["kind"] == "open" and (tmp / "Mac2" / "Notes" / "Plan.md").exists(), "it comes back as an Open memory", back)
finally:
    for p in fast:
        p.stop()
    server.terminate()
    cloud.forget_password(conn)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
