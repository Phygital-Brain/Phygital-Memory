"""Working together on a memory, with no server: the memory's files sit in a place everyone can reach (a shared cloud
folder, WebDAV, a GitHub repo, a bucket), and each person opens it with their own personal key, never a shared
password.

- Your personal key: an X25519 key pair, made once per Mac. The private half stays in the Keychain; the public half
  goes into join requests.
- In the memory's top folder (next to masterkey.cryptomator, outside the encrypted notes), in ".phygital-share":
  - keys/ID.key: the memory's key, locked to that person's public key (X25519, HKDF-SHA256, AES-GCM). Only they can
    open it.
  - members.enc: who's in, their roles, and open invites, encrypted with the memory's own key.
  - requests/ID.json: someone asking to join: their name, public key, and proof that they have the invite link
    (an HMAC with the link's one-time code). The owner says yes or no in the app.
- Roles: "edit" or "view". View is kept by the app (it opens the memory view only); anyone holding the key could
  write in theory, so a truly read-only share should also use the cloud's own read-only sharing.
- Removing someone deletes their key file and takes them off the list. A copy they already opened stays with them;
  changing the memory's key to shut them out of later changes is a separate step (not built yet)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import time
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from . import keychain
from .vault import keys as vkeys

SHARE = ".phygital-share"
ME_FILE = Path(os.environ.get("PHYGITAL_MEMORY_STATE", "~/Library/Application Support/Phygital Memory")).expanduser() / "me.json"
IDENTITY = os.environ.get("PHYGITAL_MEMORY_IDENTITY_KEYCHAIN", "Phygital Memory identity")
INVITE_DAYS = 7
ROLES = ("edit", "view")


# ---------- your personal key ----------

def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _identity() -> X25519PrivateKey:
    raw = keychain.read(IDENTITY, "x25519")
    if raw:
        return X25519PrivateKey.from_private_bytes(_unb64(raw.strip()))
    key = X25519PrivateKey.generate()
    keychain.save(IDENTITY, "x25519", _b64(key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                                              serialization.NoEncryption())))
    return key


def my_public() -> bytes:
    return _identity().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def my_id() -> str:
    return member_id(my_public())


def member_id(pub: bytes) -> str:
    return hashlib.sha256(pub).hexdigest()[:16]


def my_name() -> str:
    """The name others see: the one set in Settings, or else this Mac user's full name."""
    try:
        name = json.loads((ME_FILE).read_text()).get("name", "").strip()
    except (OSError, ValueError):
        name = ""
    if name:
        return name[:60]
    r = subprocess.run(["id", "-F"], capture_output=True, text=True)
    return (r.stdout.strip() or os.environ.get("USER", "Someone"))[:60]


def saved_name() -> str:
    """The name set in the app. Sharing needs one: others must know who's asking or inviting."""
    try:
        return json.loads(ME_FILE.read_text()).get("name", "").strip()[:60]
    except (OSError, ValueError):
        return ""


def set_my_name(name: str) -> str:
    name = " ".join(str(name).split())[:60]
    if not name:
        raise ValueError("Your name can't be empty.")
    ME_FILE.parent.mkdir(parents=True, exist_ok=True)
    ME_FILE.write_text(json.dumps({"name": name}))
    return my_name()


def safety_code(pub: bytes, vault_id: str) -> str:
    """Four words both people see when someone asks to join. If they match, it really is them (nobody swapped keys)."""
    from .vault.manage import WORDS
    n = int.from_bytes(hashlib.sha256(pub + vault_id.encode()).digest()[:6], "big")
    return " ".join(WORDS[(n >> (12 * i)) & 0xFFF] for i in range(4))


def my_safety_code(folder: Path) -> str:
    return safety_code(my_public(), _vault_id(folder))


# ---------- locking the memory's key to one person ----------

def _box_key(shared: bytes, eph: bytes, pub: bytes) -> bytes:
    return HKDF(hashes.SHA256(), 32, None, b"phygital-memory share v1" + eph + pub).derive(shared)


def lock_for(raw_key: bytes, pub: bytes) -> bytes:
    eph = X25519PrivateKey.generate()
    eph_pub = eph.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    k = _box_key(eph.exchange(X25519PublicKey.from_public_bytes(pub)), eph_pub, pub)
    nonce = os.urandom(12)
    return b"PMS1" + eph_pub + nonce + AESGCM(k).encrypt(nonce, raw_key, b"phygital-memory share v1")


def open_mine(box: bytes) -> bytes:
    if box[:4] != b"PMS1" or len(box) < 4 + 32 + 12 + 16:
        raise ValueError("That key file isn't one of ours.")
    eph_pub, nonce, ct = box[4:36], box[36:48], box[48:]
    me = _identity()
    pub = me.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    k = _box_key(me.exchange(X25519PublicKey.from_public_bytes(eph_pub)), eph_pub, pub)
    return AESGCM(k).decrypt(nonce, ct, b"phygital-memory share v1")


def masterkey(raw: bytes) -> vkeys.Masterkey:
    return vkeys.Masterkey(bytearray(raw[:32]), bytearray(raw[32:]))


# ---------- the members list (encrypted with the memory's key) ----------

def _list_key(raw_key: bytes) -> bytes:
    return HKDF(hashes.SHA256(), 32, None, b"phygital-memory members v1").derive(raw_key)


def _read_members(folder: Path, raw_key: bytes) -> dict:
    p = folder / SHARE / "members.enc"
    if not p.exists():
        return {"members": [], "invites": []}
    data = p.read_bytes()
    return json.loads(AESGCM(_list_key(raw_key)).decrypt(data[:12], data[12:], b"members"))


def _write_members(folder: Path, raw_key: bytes, m: dict) -> None:
    (folder / SHARE).mkdir(exist_ok=True)
    nonce = os.urandom(12)
    data = nonce + AESGCM(_list_key(raw_key)).encrypt(nonce, json.dumps(m).encode(), b"members")
    tmp = folder / SHARE / f".members-{secrets.token_hex(4)}.tmp"
    tmp.write_bytes(data)
    os.replace(tmp, folder / SHARE / "members.enc")


def _vault_id(folder: Path) -> str:
    return vkeys.read_vault_config_unverified((folder / "vault.cryptomator").read_bytes())[0].vault_id


# ---------- the owner's side (the memory is open, so its key is at hand) ----------

def members(folder: Path, raw_key: bytes) -> list[dict]:
    return _read_members(folder, raw_key)["members"]


def is_shared(folder: Path) -> bool:
    return (folder / SHARE / "members.enc").exists()


def start(folder: Path, raw_key: bytes) -> None:
    """Make this memory shareable: you go on the list as its owner, with your own key file too."""
    m = _read_members(folder, raw_key)
    pub = my_public()
    if not any(x["id"] == member_id(pub) for x in m["members"]):
        m["members"].append({"id": member_id(pub), "name": my_name(), "pub": _b64(pub), "role": "owner", "added": time.time()})
        (folder / SHARE / "keys").mkdir(parents=True, exist_ok=True)
        (folder / SHARE / "keys" / f"{member_id(pub)}.key").write_bytes(lock_for(raw_key, pub))
    _write_members(folder, raw_key, m)


def invite(folder: Path, raw_key: bytes, role: str, name: str) -> str:
    """A one-time invite link for someone. It carries a code (to prove they got it from you), never a key."""
    if role not in ROLES:
        raise ValueError("Choose edit or view.")
    start(folder, raw_key)
    code = secrets.token_urlsafe(18)
    m = _read_members(folder, raw_key)
    m["invites"] = [i for i in m["invites"] if i["expires"] > time.time() and not i.get("used")] + [
        {"code": code, "role": role, "expires": time.time() + INVITE_DAYS * 86400}]
    _write_members(folder, raw_key, m)
    return f"phygitalmemory://join?m={quote(_vault_id(folder))}&c={code}&n={quote(name)}"


def _proof(code: str, pub: bytes, name: str) -> str:
    return hmac.new(code.encode(), pub + name.encode(), hashlib.sha256).hexdigest()


def requests(folder: Path, raw_key: bytes) -> list[dict]:
    """People asking to join with a valid, unused invite: [{id, name, role}]."""
    m = _read_members(folder, raw_key)
    out = []
    for p in sorted((folder / SHARE / "requests").glob("*.json")) if (folder / SHARE / "requests").is_dir() else []:
        try:
            r = json.loads(p.read_text())
            pub, name = _unb64(r["pub"]), str(r["name"])[:60]
        except (ValueError, KeyError, OSError):
            continue
        inv = next((i for i in m["invites"] if not i.get("used") and i["expires"] > time.time()
                    and hmac.compare_digest(_proof(i["code"], pub, name), str(r.get("proof", "")))), None)
        if inv and not any(x["id"] == member_id(pub) for x in m["members"]):
            out.append({"id": member_id(pub), "name": name, "role": inv["role"], "safety": safety_code(pub, _vault_id(folder))})
    return out


def answer(folder: Path, raw_key: bytes, rid: str, allow: bool, role: str | None = None) -> None:
    """Yes: their own key file is made and they're on the list (the invite is used up). No: the request goes."""
    m = _read_members(folder, raw_key)
    req = folder / SHARE / "requests" / f"{rid}.json"
    if not req.exists():
        raise ValueError("That request is gone.")
    r = json.loads(req.read_text())
    pub, name = _unb64(r["pub"]), str(r["name"])[:60]
    inv = next((i for i in m["invites"] if not i.get("used") and i["expires"] > time.time()
                and hmac.compare_digest(_proof(i["code"], pub, name), str(r.get("proof", "")))), None)
    if allow:
        if not inv:
            raise ValueError("That invite ran out or was used. Send a new one.")
        (folder / SHARE / "keys").mkdir(parents=True, exist_ok=True)
        (folder / SHARE / "keys" / f"{member_id(pub)}.key").write_bytes(lock_for(raw_key, pub))
        m["members"].append({"id": member_id(pub), "name": name, "pub": r["pub"], "role": role or inv["role"], "added": time.time(),
                             **({"device": str(r["device"])[:80]} if r.get("device") else {})})
        inv["used"] = True
        _write_members(folder, raw_key, m)
    req.unlink()


def add_member(folder: Path, raw_key: bytes, person: dict, role: str) -> None:
    """Someone already let in elsewhere (their public key checked then): their own key file, and on the list."""
    if role not in ROLES:
        raise ValueError("Choose edit or view.")
    start(folder, raw_key)
    m = _read_members(folder, raw_key)
    pub = _unb64(person["pub"])
    if member_id(pub) != person["id"]:
        raise ValueError("That person's key doesn't match.")
    (folder / SHARE / "keys" / f"{person['id']}.key").write_bytes(lock_for(raw_key, pub))
    m["members"] = [x for x in m["members"] if x["id"] != person["id"]] + [
        {"id": person["id"], "name": str(person["name"])[:60], "pub": person["pub"], "role": role, "added": time.time(),
         **({"device": str(person["device"])[:80]} if person.get("device") else {})}]
    _write_members(folder, raw_key, m)


# ---------- history: who changed what (each person writes only their own list, so lists never clash) ----------

LOG_KEEP = 500


def _log_key(raw_key: bytes) -> bytes:
    return HKDF(hashes.SHA256(), 32, None, b"phygital-memory history v1").derive(raw_key)


def _read_log(p: Path, raw_key: bytes) -> list:
    try:
        data = p.read_bytes()
        return json.loads(AESGCM(_log_key(raw_key)).decrypt(data[:12], data[12:], b"history"))
    except Exception:
        return []


def log_change(folder: Path, raw_key: bytes, what: str, path: str) -> None:
    """Add one line to my own history list in this shared memory: what I did, to which file, when."""
    d = folder / SHARE / "history"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{my_id()}.enc"
    items = _read_log(p, raw_key)
    if items and items[-1]["path"] == path and items[-1]["what"] == what and time.time() - items[-1]["t"] < 60:
        items[-1]["t"] = time.time()   # typing in one note: one line a minute, not one per save
    else:
        items.append({"what": what, "path": path, "t": time.time()})
    nonce = os.urandom(12)
    tmp = d / f".{my_id()}-{secrets.token_hex(4)}.tmp"
    tmp.write_bytes(nonce + AESGCM(_log_key(raw_key)).encrypt(nonce, json.dumps(items[-LOG_KEEP:]).encode(), b"history"))
    os.replace(tmp, p)


def history(folder: Path, raw_key: bytes, n: int = 100) -> list[dict]:
    """Everyone's lines together, newest first: [{who, what, path, t}]."""
    names = {x["id"]: x["name"] for x in members(folder, raw_key)}
    out = []
    for p in (folder / SHARE / "history").glob("*.enc") if (folder / SHARE / "history").is_dir() else []:
        out += [{**x, "who": names.get(p.stem, "Someone who left")} for x in _read_log(p, raw_key)]
    return sorted(out, key=lambda x: -x["t"])[:n]


def set_role(folder: Path, raw_key: bytes, mid: str, role: str) -> None:
    if role not in ROLES:
        raise ValueError("Choose edit or view.")
    m = _read_members(folder, raw_key)
    x = next((x for x in m["members"] if x["id"] == mid and x["role"] != "owner"), None)
    if not x:
        raise ValueError("They're not on the list.")
    x["role"] = role
    _write_members(folder, raw_key, m)


def remove(folder: Path, raw_key: bytes, mid: str) -> dict:
    """Takes them off the list and deletes their key file. Returns who it was (with their Syncthing device, if any)."""
    m = _read_members(folder, raw_key)
    gone = next((x for x in m["members"] if x["id"] == mid and x["role"] != "owner"), None)
    if not gone:
        raise ValueError("They're not on the list.")
    (folder / SHARE / "keys" / f"{mid}.key").unlink(missing_ok=True)
    m["members"] = [x for x in m["members"] if x["id"] != mid]
    _write_members(folder, raw_key, m)
    return gone


# ---------- the joining side ----------

def parse_link(link: str) -> dict:
    u = urlparse(link.strip())
    q = parse_qs(u.query)
    if u.scheme != "phygitalmemory" or u.netloc != "join" or not q.get("m") or not q.get("c"):
        raise ValueError("That isn't a Phygital Memory invite link.")
    return {"vault": q["m"][0], "code": q["c"][0], "name": (q.get("n") or ["Shared memory"])[0][:60]}


def request_for(link: str, device: str = "") -> dict:
    """What a request to join says: your name, your public key, and proof you have the invite."""
    inv = parse_link(link)
    pub, name = my_public(), my_name()
    return {"pub": _b64(pub), "name": name, "proof": _proof(inv["code"], pub, name), "at": time.time(),
            **({"device": device} if device else {})}


def put_request(folder: Path, r: dict) -> None:
    """Drop a request into the shared memory's folder, where the owner's app finds it."""
    (folder / SHARE / "requests").mkdir(parents=True, exist_ok=True)
    (folder / SHARE / "requests" / f"{member_id(_unb64(r['pub']))}.json").write_text(json.dumps(r))


def ask_to_join(folder: Path, link: str, device: str = "") -> dict:
    """Leave a request in the shared memory's folder. The owner sees it in their app and says yes or no."""
    inv = parse_link(link)
    if _vault_id(folder) != inv["vault"]:
        raise ValueError("That folder holds a different memory than the one in the invite.")
    put_request(folder, request_for(link, device))
    return inv


def request_of(folder: Path, rid: str) -> dict | None:
    try:
        return json.loads((folder / SHARE / "requests" / f"{rid}.json").read_text())
    except (OSError, ValueError):
        return None


def my_key(folder: Path) -> bytes | None:
    """The memory's key, if the owner said yes (your key file is there). None while waiting."""
    p = folder / SHARE / "keys" / f"{my_id()}.key"
    return open_mine(p.read_bytes()) if p.exists() else None


def my_role(folder: Path, raw_key: bytes) -> str | None:
    me = my_id()
    return next((x["role"] for x in members(folder, raw_key) if x["id"] == me), None)
