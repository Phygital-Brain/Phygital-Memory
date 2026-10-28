"""An Open memory on WebDAV, against a stand-in WebDAV server (rclone serve on 127.0.0.1:8798): Mac + WebDAV puts its
notes on the server as normal files and keeps both sides in step; the server lists it as an Open memory; WebDAV only
opens it from the server with no password; and it comes back down to the Mac as an Open memory.

Run: uv run python test_webdav_open.py
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-webdavopen-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
os.environ["PHYGITAL_MEMORY_TRASH"] = str(tmp / "Trash")
os.environ["PHYGITAL_MEMORY_CLOUD_KEYCHAIN"] = "Phygital Memory cloud TEST"
(tmp / "Trash").mkdir()
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


store = tmp / "webdav"
store.mkdir()
server = subprocess.Popen(["rclone", "serve", "webdav", str(store), "--addr", "127.0.0.1:8798", "--user", "ana",
                           "--pass", "cloud-pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
conn = cloud.make_conn("webdav", "http://127.0.0.1:8798", "ana")
fast = [mock.patch.object(cloud, "MIRROR_AFTER", 0.5), mock.patch.object(cloud, "MIRROR_EVERY", 2)]
for p in fast:
    p.start()
try:
    cloud.connect(conn, "cloud-pass")
    mac = tmp / "Mac"
    mac.mkdir()
    fs = F.Folders(None)
    f = fs.get(fs.create(str(mac), "Notes", None)["id"])
    f.memory.unlock("")
    f.memory.save("Plan.md", "# Plan\nfirst\n", new=True)
    F.memory_id(f)   # what lets the server list it as a memory

    info = fs.to_webdav(f.id, conn, "")
    check(info["webdav"] and info["kind"] == "open", "Mac + WebDAV is on for an Open memory", info)
    check((store / "Notes" / "Plan.md").read_text() == "# Plan\nfirst\n", "its notes are normal files on the server")
    f.memory.save("Second.md", "# Second\n", new=True)
    check(wait(lambda: (store / "Notes" / "Second.md").exists()), "a change here goes up by itself")
    (tmp / "FromPhone.md").write_text("# Written in the Nextcloud app\n")   # through the server, like the phone app
    cloud._run(conn, "copyto", str(tmp / "FromPhone.md"), cloud._remote("Notes/FromPhone.md"))
    check(wait(lambda: "FromPhone.md" in {x["path"] for x in f.memory.list_files()}), "a note made on the server comes down",
          f"{f.mirror.status()} on disk={(f.path / 'FromPhone.md').exists()}")

    found = cloud.find_memories(conn)
    check(any(m["path"] == "Notes" and m["kind"] == "open" for m in found), "the server lists it as an Open memory", found)

    info = fs.to_cloud(f.id, {}, "")
    check(info["cloudOnly"] and info["kind"] == "open", "WebDAV only, still an Open memory", info)
    g = fs.get(f.id)
    g.ready()
    g.memory.unlock("")
    check(g.memory.read("FromPhone.md").startswith("# Written"), "it opens from the server with no password")
    g.memory.save("Cloud.md", "# Saved while on WebDAV only\n", new=True)
    g.lock()
    check((store / "Notes" / "Cloud.md").exists(), "a note saved there is on the server as a normal file")

    info = fs.to_mac(g.id, str(tmp / "Mac2"))
    h = fs.get(g.id)
    check(info["kind"] == "open" and (tmp / "Mac2" / "Notes" / "Cloud.md").exists(), "and back down to this Mac as an Open memory", info)

    added = fs.from_cloud(conn, "Notes", True)
    check(added["kind"] == "open", "Add memory › From WebDAV brings in an Open memory", added)
finally:
    for p in fast:
        p.stop()
    for x in list(F.CLOUDS.iterdir()) if F.CLOUDS.is_dir() else []:
        cloud.unmount(x)
    server.terminate()
    cloud.forget_password(conn)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
