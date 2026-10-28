"""Linking your other Mac: it becomes you too, with no cloud and no account.

- The first Mac shows a one-time link (its Syncthing ID, where to reach it, and a random code). The other Mac pastes
  it, makes a throwaway key pair, and sends a request (its Syncthing ID, its name, the throwaway public key, its own
  approval key card, and proof it has the code) through a small "pml-" folder that only these two Macs share.
- Both Macs show the same four safety words, made from the throwaway key and the code. If they match, nobody in
  between swapped keys. The person presses Link on the first Mac and signs it with their approval key.
- The answer, locked to the throwaway key, carries the personal key and the memories picked. The throwaway private
  key only ever lives in the other Mac's memory (RAM), so a restart there means starting again.
- The picked memories then sync between the two Macs as they are: still encrypted, opened with the same password.
- Each Mac keeps its own approval key (a security chip key can't be copied). The first Mac's signed yes names the
  other Mac's key, and both keep that record.
- Shares the person runs stay with the first Mac: it must be on for changes to reach other people."""
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

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from . import keychain, sharing
from .folders import STATE

MACS = STATE / "my-macs.json"   # this person's other Macs: {device: {name, linked, approver, approval}}
LINKS = STATE / "links"          # the small "pml-" folders, while a link is under way
LIFE = 15 * 60                   # a link code works for 15 minutes
SCHEME = "phygitalmemory://link?"


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def folder_id(code: str) -> str:
    return "pml-" + hashlib.sha256(b"link|" + code.encode()).hexdigest()[:16]


def computer_name() -> str:
    if os.environ.get("PHYGITAL_MEMORY_MAC_NAME"):
        return os.environ["PHYGITAL_MEMORY_MAC_NAME"][:40]
    try:   # the Mac's own name ("Max's MacBook"); elsewhere, the computer's network name
        r = subprocess.run(["scutil", "--get", "ComputerName"], capture_output=True, text=True, timeout=5)
        if r.stdout.strip():
            return r.stdout.strip()[:40]
    except (OSError, subprocess.TimeoutExpired):
        pass
    import platform
    return (platform.node().split(".")[0] or "Computer")[:40]


def words(pub: bytes, code: str) -> str:
    """The four safety words both Macs show for this link."""
    return sharing.safety_code(pub, "link|" + code)


def proof(code: str, req: dict) -> str:
    msg = "|".join(str(req.get(k, "")) for k in ("device", "pub", "name", "approver"))
    return hmac.new(code.encode(), msg.encode(), hashlib.sha256).hexdigest()


# ---------- the first Mac ----------

_open: dict = {}   # the link this Mac is offering: {code, expires}. One at a time; it dies with the app.


def _key_tag(pub: bytes) -> str:
    """A short fingerprint of a personal key, carried in the link: the other Mac takes only that key."""
    return hashlib.sha256(b"link key|" + pub).hexdigest()[:24]


def start(device: str, address: str) -> str:
    code = secrets.token_urlsafe(18)
    _open.clear()
    _open.update(code=code, expires=time.time() + LIFE)
    return f"{SCHEME}d={device}&a={address}&c={code}&k={_key_tag(sharing.my_public())}"


def offered() -> str | None:
    if _open and _open["expires"] > time.time():
        return _open["code"]
    _open.clear()
    return None


def cancel() -> None:
    _open.clear()


def request_in() -> dict | None:
    """The other Mac's request, once its folder brought it here and the proof checks."""
    code = offered()
    if not code:
        return None
    try:
        r = json.loads((LINKS / folder_id(code) / "request.json").read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(r, dict) or not hmac.compare_digest(str(r.get("proof", "")), proof(code, r)):
        return None
    try:
        pub = _unb64(str(r["pub"]))
        card = json.loads(r["approver"])
        if len(pub) != 32 or not card["credential_id"] or not card["public_key"]:
            return None
    except Exception:
        return None
    name = "".join(c for c in str(r.get("name", "")) if c.isprintable() and c not in "()[]{}<>")[:40] or "Mac"
    return {"device": str(r["device"]), "name": name, "pub": pub, "approver": card, "words": words(pub, code),
            "seen": hashlib.sha256(pub).hexdigest()[:24]}


def approval_request(r: dict, memories: list[dict]) -> dict:
    """What the person signs: this exact Mac, its approval key, and the memories it gets."""
    return {"type": "device.link", "params": {"device": r["device"], "name": r["name"], "words": r["words"],
            "approver": r["approver"]["credential_id"], "approver_key": r["approver"]["public_key"],
            "memories": sorted(m["vault"] for m in memories)}}


def answer(r: dict, memories: list[dict], approval: str, my_device: str, my_name: str) -> None:
    """Locked to the other Mac's throwaway key: the personal key and the memories. Then the code is used up."""
    code = offered()
    if not code:
        raise ValueError("This link ran out. Start again.")
    ident = sharing._identity().private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                              serialization.NoEncryption())
    body = json.dumps({"identity": _b64(ident), "memories": memories, "approval": approval,
                       "from": {"device": my_device, "name": my_name}}).encode()
    eph = X25519PrivateKey.generate()
    eph_pub = eph.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    k = _box_key(eph.exchange(X25519PublicKey.from_public_bytes(r["pub"])), eph_pub, r["pub"], code)
    nonce = os.urandom(12)
    box = b"PML1" + eph_pub + nonce + AESGCM(k).encrypt(nonce, body, b"phygital-memory link v1")
    tmp = LINKS / folder_id(code) / f".answer-{secrets.token_hex(4)}.tmp"
    tmp.write_bytes(box)
    os.replace(tmp, LINKS / folder_id(code) / "answer.bin")
    remember(r["device"], {"name": r["name"], "linked": time.time(), "approver": r["approver"], "approval": approval})
    cancel()


def _box_key(shared: bytes, eph: bytes, pub: bytes, code: str) -> bytes:
    return HKDF(hashes.SHA256(), 32, None, b"phygital-memory link v1" + eph + pub + code.encode()).derive(shared)


# ---------- the other Mac ----------

_wait: dict = {}   # {code, owner, key (throwaway private key), words}: only in this run's memory


def parse(link: str) -> dict:
    from urllib.parse import parse_qs, urlparse
    link = link.strip()
    if not link.startswith(SCHEME):
        raise ValueError("Paste the whole link, starting with phygitalmemory://link")
    q = parse_qs(urlparse(link).query)
    if not q.get("d") or not q.get("c") or not q.get("k"):
        raise ValueError("That link is cut short. Copy it again.")
    return {"device": q["d"][0], "address": (q.get("a") or ["dynamic"])[0], "code": q["c"][0], "key": q["k"][0]}


def make_request(link: dict, my_device: str, approver: dict) -> dict:
    key = X25519PrivateKey.generate()
    pub = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    r = {"device": my_device, "pub": _b64(pub), "name": computer_name(), "approver": json.dumps(approver, sort_keys=True)}
    r["proof"] = proof(link["code"], r)
    _wait.clear()
    _wait.update(code=link["code"], owner=link["device"], key=key, words=words(pub, link["code"]), tag=link["key"])
    return r


def waiting() -> dict | None:
    return {"words": _wait["words"], "owner": _wait["owner"]} if _wait else None


def answer_in() -> dict | None:
    """The first Mac's answer, opened with the throwaway key. None until it has arrived."""
    if not _wait:
        return None
    p = LINKS / folder_id(_wait["code"]) / "answer.bin"
    try:
        box = p.read_bytes()
    except OSError:
        return None
    if box[:4] != b"PML1" or len(box) < 64:
        return None
    eph_pub, nonce, ct = box[4:36], box[36:48], box[48:]
    key = _wait["key"]
    pub = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    try:
        body = AESGCM(_box_key(key.exchange(X25519PublicKey.from_public_bytes(eph_pub)), eph_pub, pub, _wait["code"])) \
            .decrypt(nonce, ct, b"phygital-memory link v1")
        a = json.loads(body)
        ident = X25519PrivateKey.from_private_bytes(_unb64(a["identity"]))
        mine = ident.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        if not hmac.compare_digest(_key_tag(mine), _wait["tag"]):   # not the key the link named: refused
            return None
        if not isinstance(a.get("memories"), list) or not all(
                isinstance(m, dict) and isinstance(m.get("vault"), str) and isinstance(m.get("name"), str) for m in a["memories"]):
            return None
        if not all(c.isalnum() or c == "-" for m in a["memories"] for c in m["vault"]):
            return None
        a["from"] = {"device": str(a["from"]["device"]), "name": str(a["from"]["name"])[:40]}
        return a
    except Exception:
        return None


def take_identity(a: dict) -> None:
    """This Mac becomes you: your personal key goes into its Keychain. The one it had is kept next to it."""
    raw = _unb64(a["identity"])
    X25519PrivateKey.from_private_bytes(raw)   # a real key, or this fails before anything changes
    old = keychain.read(sharing.IDENTITY, "x25519")
    if old and old.strip() != _b64(raw):
        keychain.save(sharing.IDENTITY, "x25519 before linking", old.strip())
    keychain.save(sharing.IDENTITY, "x25519", _b64(raw))
    with sharing._me_lock:
        sharing._me.pop(sharing.IDENTITY, None)
    remember(a["from"]["device"], {"name": a["from"]["name"][:40], "linked": time.time(), "approval": a.get("approval", "")})


def done_waiting() -> None:
    _wait.clear()


# ---------- both ----------

def macs() -> dict:
    try:
        return json.loads(MACS.read_text())
    except (OSError, ValueError):
        return {}


def remember(device: str, info: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    tmp = STATE / f".my-macs-{secrets.token_hex(4)}.tmp"
    tmp.write_text(json.dumps({**macs(), device: info}))
    os.chmod(tmp, 0o600)
    os.replace(tmp, MACS)


def forget(device: str) -> None:
    d = macs()
    d.pop(device, None)
    MACS.write_text(json.dumps(d))
