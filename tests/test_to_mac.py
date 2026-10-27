"""Moving a cloud-only memory down to this Mac, and back up again: every file comes down and is checked, the memory
opens from the Mac after, the cloud copy stays, and a bad move leaves nothing behind. A stand-in cloud (rclone's WebDAV
server on 127.0.0.1) plays Nextcloud.

Run: uv run python test_to_mac.py
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-tomac-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"   # never touch the real GitHub account
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "mac1")
os.environ["PHYGITAL_MEMORY_TRASH"] = str(tmp / "Trash")
os.environ["PHYGITAL_MEMORY_CLOUD_KEYCHAIN"] = "Phygital Memory cloud TEST"
(tmp / "Trash").mkdir()
from phygital_memory import cloud, folders as F   # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


store = tmp / "cloud"
store.mkdir()
server = subprocess.Popen(["rclone", "serve", "webdav", str(store), "--addr", "127.0.0.1:8797", "--user", "ana",
                           "--pass", "cloud-pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
conn = cloud.make_conn("webdav", "http://127.0.0.1:8797", "ana")
try:
    cloud.connect(conn, "cloud-pass")
    fs = F.Folders(None)
    f = fs.get(fs.create_in_cloud(conn, "", "Work", "memory-pass-1")["id"])
    f.ready()
    f.memory.unlock("memory-pass-1")
    for i in range(5):
        f.memory.save(f"Note {i}.md", f"# Note {i}\nfrom the cloud\n", new=True)
    f.lock()

    mac = tmp / "Mac"
    mac.mkdir()
    (mac / "Work").mkdir()
    try:
        fs.to_mac(f.id, str(mac))
        check(False, "a name already taken on the Mac is refused")
    except ValueError as e:
        check("already" in str(e) and fs.get(f.id).cloud_at, "a name already taken on the Mac is refused, nothing moves")
    (mac / "Work").rmdir()

    info = fs.to_mac(f.id, str(mac))
    g = fs.get(f.id)
    check(not g.cloud_at and g.path == mac / "Work" and info["cloudOnly"] is None, "it's a Mac memory now", info)
    check(info["cloudCopy"] and (store / "Work" / "masterkey.cryptomator").exists(), "the cloud copy stays", info)
    g.memory.unlock("memory-pass-1")

    check(g.memory.status()["notes"] >= 5, "all notes open from the Mac", g.memory.status())
    check(g.memory.read("Note 3.md").startswith("# Note 3"), "a note reads back")
    g.lock()
    check(F.Folders(None).get(f.id).path == mac / "Work", "the move is remembered after a restart")

    try:
        fs.to_mac(f.id, str(mac))
        check(False, "moving a Mac memory to the Mac is refused")
    except ValueError:
        check(True, "moving a Mac memory to the Mac is refused")

    # back up again, then down into a place where the download fails: nothing half-copied stays
    fs.to_cloud(f.id, conn, "Again")
    check(fs.get(f.id).cloud_at and (store / "Again" / "Work").exists(), "and up to the cloud again")
    server.terminate(); server.wait()
    try:
        fs.to_mac(f.id, str(mac))
        check(False, "a cloud that can't be reached is refused")
    except Exception:
        check(not (mac / "Work").exists() and fs.get(f.id).cloud_at, "a failed move leaves nothing on the Mac, and the memory stays in the cloud")
finally:
    server.terminate()
    cloud.forget_password(conn)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
