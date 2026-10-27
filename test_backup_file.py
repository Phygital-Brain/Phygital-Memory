"""Backup file and recovery key: a memory saved as one zip of encrypted files, opened again (from the zip, or from a
masterkey.cryptomator file), refused when it's already here, and a forgotten password reset with the 44-word
recovery key.

Run: uv run python test_backup_file.py
"""
import os
import tempfile
import zipfile
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-backupfile-"))
os.environ["PHYGITAL_MEMORY_OFFLINE"] = "1"
os.environ["PHYGITAL_MEMORY_STATE"] = str(tmp / "state")
from phygital_memory import folders as F   # noqa: E402
from phygital_memory.vault import manage   # noqa: E402
from phygital_memory.vault.keys import VaultError, WrongPassword   # noqa: E402

ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


(tmp / "Mac").mkdir()
fs = F.Folders(None)
f = fs.get(fs.create(str(tmp / "Mac"), "Work", "password-1")["id"])
f.memory.unlock("password-1")
f.memory.save("Plan.md", "# Plan\nsecret plan text\n", new=True)
f.memory.save_bytes("Photos/a.jpg", b"\xff\xd8" + os.urandom(5000))

size = fs.save_backup(f.id, str(tmp / "Work backup"))
z = tmp / "Work backup.zip"
check(z.exists() and size == z.stat().st_size, "a backup zip is saved (.zip added to the name)")
with zipfile.ZipFile(z) as zz:
    names = zz.namelist()
    blob = b"".join(zz.read(n) for n in names)
check(all(n.startswith("Work/") for n in names) and "Work/vault.cryptomator" in names and "Work/masterkey.cryptomator" in names,
      "it holds one memory folder", names[:4])
check(b"secret plan text" not in blob and not any("Plan" in n for n in names), "everything in it is encrypted")

try:
    fs.open_backup(str(z), str(tmp / "Elsewhere"))
    check(False, "the same memory already here is refused")
except ValueError as e:
    check("already here" in str(e), "the same memory already here is refused", e)

fs.items.pop(f.id)   # like another Mac, without this memory
info = fs.open_backup(str(z), str(tmp / "Restored"))
r = fs.get(info["id"])
r.memory.unlock("password-1")
check(r.memory.read("Plan.md").startswith("# Plan") and r.path == tmp / "Restored" / "Work", "the zip opens as a memory with every note")
check(r.memory.read_bytes("Photos/a.jpg")[:2] == b"\xff\xd8", "files come back too")
r.memory.lock()

try:
    fs.open_backup(str(z), str(tmp / "Restored"))
    check(False, "opening it twice is refused")
except ValueError:
    check(True, "opening it twice is refused")

bad = tmp / "bad.zip"
with zipfile.ZipFile(bad, "w") as zz:
    zz.writestr("../evil.txt", "x")
try:
    fs.open_backup(str(bad), str(tmp / "Restored"))
    check(False, "a zip that isn't a backup is refused")
except ValueError:
    check(not (tmp / "evil.txt").exists(), "a zip that isn't a backup is refused, nothing written outside")

# a memory's own key file: its folder is opened where it is
fs.items.pop(r.id)
info = fs.open_backup(str(tmp / "Restored" / "Work" / "masterkey.cryptomator"), None)
check(Path(fs.get(info["id"]).path) == tmp / "Restored" / "Work", "a masterkey.cryptomator file opens its folder where it is")

# the recovery key
m = fs.get(info["id"]).memory
m.unlock("password-1")
try:
    m.recovery_words("wrong-password")
    check(False, "showing the recovery key needs the password")
except WrongPassword:
    check(True, "showing the recovery key needs the password")
words = m.recovery_words("password-1")
check(len(words.split()) == 44, "the recovery key is 44 words")
m.lock()
try:
    manage.reset_password(m.folder, " ".join(words.split()[:-1] + ["able"]), "new-password-2")
    check(False, "a wrong word is caught")
except VaultError:
    check(True, "a wrong word is caught")
manage.reset_password(m.folder, words.upper(), "new-password-2")
try:
    m.unlock("password-1")
    check(False, "after a reset the old password no longer works")
except WrongPassword:
    check(True, "after a reset the old password no longer works")
m.unlock("new-password-2")
check(m.read("Plan.md").startswith("# Plan"), "the new password opens it, every note still there")
m.lock()

print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
