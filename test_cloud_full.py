"""Cloud only, the hard cases: the cloud refuses saves (full), the saves wait on this Mac and go up at the next
unlock; and moving a memory from this Mac into the cloud (refused when it doesn't fit). A stand-in cloud (rclone's
WebDAV server on 127.0.0.1) plays Nextcloud; "full" is played by restarting it read-only.

Run: uv run python test_cloud_full.py
"""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-cloudfull-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"   # never touch the real GitHub account
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "mac1")
os.environ["PHYGITAL_MEMORY_TRASH"] = str(tmp / "Trash")
os.environ["PHYGITAL_MEMORY_CLOUD_KEYCHAIN"] = "Phygital Memory cloud TEST"
(tmp / "Trash").mkdir()
from phygital_memory import cloud, folders as F   # noqa: E402
from phygital_memory.memory import Memory        # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


store = tmp / "cloud"
store.mkdir()
server = None


def serve(read_only=False):
    global server
    if server:
        server.terminate()
        server.wait()
    server = subprocess.Popen(["rclone", "serve", "webdav", str(store), "--addr", "127.0.0.1:8797", "--user", "ana",
                               "--pass", "cloud-pass", *(["--read-only"] if read_only else [])],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)


serve()
conn = cloud.make_conn("webdav", "http://127.0.0.1:8797", "ana")
try:
    check(cloud._plain("Error 507: Insufficient Storage", conn) == "Your WebDAV is full.", "a full cloud is named in plain words")
    cloud.connect(conn, "cloud-pass")
    fs = F.Folders(None)
    f = fs.get(fs.create_in_cloud(conn, "", "Work", "memory-pass-1")["id"])
    f.ready()
    f.memory.unlock("memory-pass-1")
    check(f.drive.health() == {"waiting": 0, "problem": None}, "all fine while the cloud takes saves")

    serve(read_only=True)   # the cloud now refuses every save, like a full Nextcloud
    f.memory.save("Late.md", "# Late\nwritten while the cloud was full\n", new=True)
    end, h = time.time() + 30, {}
    while time.time() < end:
        h = f.drive.health()
        if h["problem"]:
            break
        time.sleep(1)
    check(h["waiting"] and h["problem"], "the app notices the cloud refusing saves", h)
    t = time.time()
    f.lock()
    check(f.drive.left > 0 and time.time() - t < 60, "locking doesn't hang: it says saves are still waiting",
          f"{f.drive.left} left, {time.time() - t:.0f}s")
    try:
        fs.forget(f.id)
        check(False, "removing it is refused while saves wait")
    except ValueError as e:
        check("haven't reached" in str(e), "removing it is refused while saves wait")

    serve()   # room again
    fs = F.Folders(None)   # (also: a restart in between)
    f = fs.get(f.id)
    f.ready()
    f.memory.unlock("memory-pass-1")
    f.lock()
    check(f.drive.left == 0, "the waiting saves went up at the next unlock")
    F.STATE, F.CLOUDS = tmp / "mac2", tmp / "mac2/clouds"
    F.REGISTRY = F.STATE / "folders.json"
    fs2 = F.Folders(None)
    g = fs2.get(fs2.from_cloud(conn, "Work")["id"])
    g.ready()
    g.memory.unlock("memory-pass-1")
    check(g.memory.read("Late.md") == "# Late\nwritten while the cloud was full\n", "another Mac sees the late note")
    g.lock()

    # moving a memory from this Mac into the cloud
    local = tmp / "Mac" / "Diary"
    local.parent.mkdir()
    Memory.create(local, "diary-pass-1")
    F.write_guides(local)
    m = fs2.get(fs2.add_existing(str(local))["id"])
    m.memory.unlock("diary-pass-1")
    m.memory.save("Day.md", "# Day\nlocal words\n", new=True)
    real_free = cloud.free_space
    cloud.free_space = lambda c: 1000
    try:
        fs2.to_cloud(m.id, conn, "Moved")
        check(False, "a memory too big for the cloud is refused")
    except ValueError as e:
        check("Not enough room" in str(e) and local.is_dir() and not (store / "Moved").exists(),
              "a memory too big for the cloud is refused, nothing moved", str(e))
    cloud.free_space = real_free
    info = fs2.to_cloud(m.id, conn, "Moved")
    check(info["cloudOnly"] and info["id"] == m.id, "moved: it's a cloud memory now, same place in the list")
    check(not local.exists() and any("Diary (moved to WebDAV" in p.name for p in (tmp / "Trash").iterdir()),
          "the Mac's copy went to the Trash (not erased)")
    m = fs2.get(m.id)
    m.ready()
    m.memory.unlock("diary-pass-1")
    check(m.memory.read("Day.md") == "# Day\nlocal words\n", "it opens from the cloud with the same password")
    m.lock()
    try:
        fs2.to_cloud(m.id, conn, "")
        check(False, "moving a cloud memory again is refused")
    except ValueError:
        check(True, "moving a cloud memory again is refused")
finally:
    for d in (tmp / "mac1/clouds", tmp / "mac2/clouds"):
        for p in d.iterdir() if d.is_dir() else []:
            cloud.unmount(p)
    cloud.forget_password(conn)
    server.terminate()
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
