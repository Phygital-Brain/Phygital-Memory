"""Mac + WebDAV, against a stand-in WebDAV server (rclone serve on 127.0.0.1): a Mac memory goes up and stays in
step both ways, a second Mac's change comes down, a clash keeps both versions, it survives a restart, it can stop
(the WebDAV copy stays), turn into WebDAV only without uploading again, and a WebDAV-only memory can come down to
Mac + WebDAV.

Run: uv run python test_webdav_sync.py
"""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

tmp = Path(tempfile.mkdtemp(prefix="pm-webdavsync-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"   # never touch the real GitHub account
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
server = subprocess.Popen(["rclone", "serve", "webdav", str(store), "--addr", "127.0.0.1:8797", "--user", "ana",
                           "--pass", "cloud-pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
conn = cloud.make_conn("webdav", "http://127.0.0.1:8797", "ana")
fast = [mock.patch.object(cloud, "MIRROR_AFTER", 0.5), mock.patch.object(cloud, "MIRROR_EVERY", 2)]
for p in fast:
    p.start()
try:
    cloud.connect(conn, "cloud-pass")
    mac = tmp / "Mac"
    mac.mkdir()
    fs = F.Folders(None)
    f = fs.get(fs.create(str(mac), "Work", "password-1")["id"])
    f.memory.unlock("password-1")
    f.memory.save("Plan.md", "# Plan\nfirst\n", new=True)

    info = fs.to_webdav(f.id, conn, "")
    check(info["webdav"] and not info["cloudOnly"] and (store / "Work" / "vault.cryptomator").exists(), "Mac + WebDAV: it went up", info)
    check(f.path.exists() and f.memory.is_open, "and it stays on this Mac, open")
    count = lambda: sum(1 for _ in (store / "Work").rglob("*.c9r"))
    before = count()
    f.memory.save("Second.md", "# Second\n", new=True)
    check(wait(lambda: count() > before), "a change here goes up by itself")

    # a second Mac (another copy of the same WebDAV folder) changes a note: it comes down here
    other = tmp / "Mac2" / "Work"
    other.parent.mkdir()
    subprocess.run(["cp", "-R", str(store / "Work"), str(other)], check=True)
    o = F.Memory(other)
    o.unlock("password-1")
    o.save("FromOther.md", "# From the other Mac\n", new=True)
    o.lock()
    cloud._run(conn, "copy", str(other), cloud._remote("Work"))   # through the server, like a real second device
    came = wait(lambda: "FromOther.md" in {x["path"] for x in f.memory.list_files()})
    check(came, "a change made elsewhere comes down", f"{f.mirror.status()} local={sum(1 for _ in f.path.rglob('*.c9r'))} remote={count()}")

    # the same note changed here and on the other Mac before a sync: both versions are kept
    f.mirror.stop()
    f.memory.save("Plan.md", "# Plan\nchanged here\n")
    subprocess.run(["rm", "-rf", str(other)], check=True)
    cloud._run(conn, "copy", cloud._remote("Work"), str(other))
    o = F.Memory(other)
    o.unlock("password-1")
    o.save("Plan.md", "# Plan\nchanged on the other Mac\n")
    o.lock()
    cloud._run(conn, "copy", str(other), cloud._remote("Work"))
    f.mirror.sync_once()
    f.memory.lock()
    f.memory.unlock("password-1")   # an unlock sorts out clash copies
    texts = [f.memory.read(x["path"]) for x in f.memory.list_files() if x["path"].startswith("Plan")]
    check(any("changed here" in t for t in texts) and any("other Mac" in t for t in texts), "a clash keeps both versions",
          [x["path"] for x in f.memory.list_files()])

    # restart: the sync picks up again on its own
    f.mirror.stop()
    fs = F.Folders(None)
    f = fs.get(f.id)
    check(f.mirror is not None and f.info()["webdav"], "after a restart it keeps syncing")
    f.memory.unlock("password-1")

    # stop: Mac only, the WebDAV copy stays
    where = fs.stop_webdav(f.id)
    check(not fs.get(f.id).mirror_at and (store / "Work" / "vault.cryptomator").exists() and "Work" in where,
          "stop: this Mac only, the WebDAV copy stays", where)

    # on again into a new folder, then WebDAV only without uploading again
    fs.to_webdav(f.id, conn, "Again")
    f = fs.get(f.id)
    f.memory.unlock("password-1")
    f.memory.save("Last.md", "# Last before going cloud only\n", new=True)
    with mock.patch.object(cloud, "upload", side_effect=AssertionError("uploaded again")):
        info = fs.to_cloud(f.id, {}, "")
    check(info["cloudOnly"] and not info["webdav"], "WebDAV only from Mac + WebDAV, no second upload", info)
    check(any("moved to" in p.name for p in (tmp / "Trash").iterdir()), "the Mac copy went to the Trash")
    g = fs.get(f.id)
    g.ready()
    g.memory.unlock("password-1")
    check(g.memory.read("Last.md").startswith("# Last"), "the last change made it up first")
    g.lock()

    # and back down as Mac + WebDAV
    info = fs.to_mac(g.id, str(tmp / "Mac3"), keep_sync=True)
    h = fs.get(g.id)
    check(info["webdav"] and h.mirror is not None and not info["cloudCopy"], "WebDAV only to Mac + WebDAV", info)
    h.memory.unlock("password-1")
    h.memory.save("Back.md", "# Back on the Mac\n", new=True)
    n0 = sum(1 for _ in (store / "Again" / "Work").rglob("*.c9r"))
    h.memory.save("Back2.md", "# Back again\n", new=True)
    check(wait(lambda: sum(1 for _ in (store / "Again" / "Work").rglob("*.c9r")) > n0), "and syncs from there", h.mirror.status())
    h.mirror.stop()
finally:
    for p in fast:
        p.stop()
    server.terminate()
    cloud.forget_password(conn)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
