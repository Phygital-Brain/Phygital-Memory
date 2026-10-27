"""Cloud only: a memory that lives in a WebDAV cloud, with nothing on this Mac. A stand-in cloud (rclone's own
WebDAV server on 127.0.0.1) plays Nextcloud, so no real cloud or account is needed. Two Macs are played by two
separate app states.

Run: uv run python test_cloud.py
"""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-cloud-"))
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "mac1")
os.environ["PHYGITAL_MEMORY_CLOUD_KEYCHAIN"] = "Phygital Memory cloud TEST"
from phygital_memory import cloud, folders as F   # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


def mac(name):   # another Mac: its own app state (folder list, hidden drives)
    F.STATE = tmp / name
    F.REGISTRY = F.STATE / "folders.json"
    F.CLOUDS = F.STATE / "clouds"
    return F.Folders(None)


store = tmp / "cloud"
(store / "Notes").mkdir(parents=True)
(store / "Notes" / "plain.txt").write_text("not a memory")
port = 8797
server = subprocess.Popen(["rclone", "serve", "webdav", str(store), "--addr", f"127.0.0.1:{port}", "--user", "ana",
                           "--pass", "cloud-pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
conn = None
try:
    nc = cloud.make_conn("nextcloud", "cloud.example.com/", "ana")
    check(nc["url"] == "https://cloud.example.com/remote.php/dav/files/ana", "Nextcloud: address plus user is enough", nc)
    try:
        cloud.make_conn("webdav", "http://cloud.example.com", "ana")
        check(False, "a cloud without https is refused")
    except cloud.CloudError:
        check(True, "a cloud without https is refused")

    conn = cloud.make_conn("webdav", f"http://127.0.0.1:{port}", "ana")
    try:
        cloud.connect(conn, "wrong")
        check(False, "a wrong cloud password is caught")
    except cloud.CloudError as e:
        check("wrong" in str(e), "a wrong cloud password is caught, in plain words", str(e))
    cloud.connect(conn, "cloud-pass")
    check(cloud.has_password(conn), "the cloud password is kept in the Keychain")

    fs = mac("mac1")
    info = fs.create_in_cloud(conn, "Notes", "Work", "memory-pass-1")
    check((store / "Notes/Work/masterkey.cryptomator").is_file() and (store / "Notes/Work/AGENTS.md").is_file(),
          "a new memory is made in the cloud")
    f = fs.get(info["id"])
    check(not cloud.is_mounted(f.path), "nothing stays connected after making it")
    check(info["cloudOnly"] == "WebDAV" and "Notes/Work" in info["path"], "the list says where in the cloud it is", info)
    try:
        fs.create_in_cloud(conn, "Notes", "Work", "memory-pass-1")
        check(False, "a second memory with the same name is refused")
    except cloud.CloudError:
        check(True, "a second memory with the same name is refused")

    found = cloud.find_memories(conn)
    check(found == [{"path": "Notes/Work", "name": "Work"}], "the app finds the memories in the cloud", found)

    f.ready()
    f.memory.unlock("memory-pass-1")
    check(cloud.is_mounted(f.path), "unlocking connects the cloud (as a hidden drive)")
    check("nobrowse" in subprocess.run(["mount"], capture_output=True, text=True).stdout.split(str(f.path))[1].split("\n")[0],
          "the drive is hidden from Finder and the Desktop")
    f.memory.save("Plan.md", "# Plan\nsecret plan words\n", new=True)
    f.lock()
    check(not cloud.is_mounted(f.path), "locking disconnects it")
    blobs = [p for p in (store / "Notes/Work/d").rglob("*.c9r") if p.is_file()]
    check(blobs and not any(b"secret plan words" in p.read_bytes() for p in blobs),
          "the note reached the cloud, encrypted", len(blobs))
    cache = F.CLOUDS / f"{f.id}.cache"
    check(not any(b"secret plan words" in p.read_bytes() for p in cache.rglob("*") if p.is_file()),
          "nothing readable in the Mac's cache")

    fs2 = mac("mac2")
    g = fs2.get(fs2.from_cloud(conn, "Notes/Work")["id"])
    g.ready()
    g.memory.unlock("memory-pass-1")
    check(g.memory.read("Plan.md") == "# Plan\nsecret plan words\n", "another Mac opens it straight from the cloud")

    fs = mac("mac1")
    f = fs.get(info["id"])
    check(f.cloud_at and f.info()["cloudOnly"] == "WebDAV", "after a restart it's still a cloud memory")
    f.ready()
    f.memory.unlock("memory-pass-1")
    before = f.memory.gen()
    g.memory.save("Plan.md", "# Plan\nchanged on the other Mac\n")
    end = time.time() + 60
    while time.time() < end and f.memory.gen() == before:
        time.sleep(2)
    check(f.memory.read("Plan.md") == "# Plan\nchanged on the other Mac\n",
          "a change from the other Mac shows up here", f"{time.time() - end + 60:.0f}s")
    print(f"     (took {time.time() - end + 60:.0f} s)")
    g.lock()

    for fn, what in ((lambda: fs.relocate(f.id, str(tmp)), "moving"), (lambda: fs.to_github(f.id), "GitHub")):
        try:
            fn()
            check(False, f"{what} is refused for a cloud memory")
        except ValueError:
            check(True, f"{what} is refused for a cloud memory")

    fs2 = mac("mac2")   # (both "Macs" share this Mac's Keychain, so Mac 2 leaves first)
    fs2.forget(g.id)
    f.lock()
    cloud.connect(conn, "cloud-pass")
    fs = mac("mac1")
    home = fs.create_in_cloud(conn, "", "Home", "memory-pass-2")
    fs.forget(f.id)
    check(not cloud.is_mounted(f.path) and not (F.CLOUDS / f"{f.id}.cache").exists(), "removing it clears the Mac's cache")
    check(cloud.has_password(conn), "the cloud password stays while another memory uses that cloud")
    fs.forget(home["id"])
    check(not cloud.has_password(conn), "removing the last cloud memory forgets the cloud password")
    check((store / "Notes/Work/masterkey.cryptomator").is_file(), "removing never deletes anything in the cloud")
finally:
    for d in (tmp / "mac1/clouds", tmp / "mac2/clouds"):
        for p in d.iterdir() if d.is_dir() else []:
            cloud.unmount(p)
    if conn:
        cloud.forget_password(conn)
    server.terminate()
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
