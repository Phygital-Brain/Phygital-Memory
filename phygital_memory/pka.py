"""Signed yeses for sharing, in Phygital Key's own approval format (pka.1, see the Phygital Key spec).

Letting someone in, adding, removing or forgetting a person, changing what they can do and stopping a share are each
approved by the person with their own key, for that one exact request, and checked before anything happens. The
signed approvals are kept, so any Phygital Key checker can verify them later, offline.

Two kinds of key, both P-256 (ES256), both shaped like a passkey's signature so Phygital Key's checkers accept them:
- chip: made inside this Mac's security chip (Secure Enclave). It never leaves the chip, and signs only after Touch
  ID or the Mac password. Its sealed handle sits in the Keychain; it's useless on any other Mac.
- password: for Macs without the chip or people who prefer it. The key is locked with a long password (scrypt, then
  AES-GCM), and wrong tries slow down.

The key card (public part) is in STATE/approver.json; the signed approvals in STATE/approvals-signed.jsonl."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import time
import unicodedata

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from . import keychain, touchid
from .folders import STATE

CARD = STATE / "approver.json"
SIGNED = STATE / "approvals-signed.jsonl"
CHIP_KEYCHAIN = os.environ.get("PHYGITAL_MEMORY_APPROVER_KEYCHAIN", "Phygital Memory approver")
RP_ID = "phygital-memory.app"
ORIGIN = "phygital-memory://app"
LIFE = 60
MIN_PASSWORD = 12
_seen: dict[str, int] = {}
_fails = {"n": 0, "until": 0.0}
_lock = threading.Lock()


class NotSetUp(Exception):
    pass


class NeedPassword(Exception):
    pass


class Refused(Exception):
    pass


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def canonical(v) -> bytes:
    """RFC 8785 for the plain values used here: sorted keys, no spaces, no floats, text already in NFC."""
    def check(x):
        if isinstance(x, float):
            raise ValueError("no floats in a signed request")
        if isinstance(x, int) and not isinstance(x, bool) and abs(x) > 2 ** 53 - 1:
            raise ValueError("number too big")
        if isinstance(x, str) and unicodedata.normalize("NFC", x) != x:
            raise ValueError("text must be NFC")
        if isinstance(x, dict):
            for k, y in x.items():
                check(k)
                check(y)
        if isinstance(x, list):
            for y in x:
                check(y)
    check(v)
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def challenge(claims: dict) -> bytes:
    return hashlib.sha256(b"phygital-key/approval/v1\x00" + canonical(claims)).digest()


# ---------- the person's key ----------

def card() -> dict | None:
    try:
        return json.loads(CARD.read_text())
    except (OSError, ValueError):
        return None


def chip_available() -> bool:
    return touchid.available() and touchid._helper() is not None


def _save_card(c: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    CARD.write_text(json.dumps(c))
    os.chmod(CARD, 0o600)


def _new_card(kind: str, public_der: bytes, extra: dict) -> dict:
    return {"credential_id": _b64(secrets.token_bytes(16)), "public_key": _b64(public_der), "rp_id": RP_ID,
            "name": "This Mac's security chip" if kind == "chip" else "Password", "created": time.strftime("%Y-%m-%d"),
            "kind": kind, **extra}


def set_up_chip() -> dict:
    r = touchid._run("signer-new", timeout=30)
    if not r or r.returncode != 0:
        raise Refused("This Mac couldn't make a key in its security chip.")
    out = json.loads(r.stdout)
    keychain.save(CHIP_KEYCHAIN, "chip", out["blob"])
    c = _new_card("chip", base64.b64decode(out["public"]), {})
    _save_card(c)
    return public(c)


def _pw_key(password: str, salt: bytes) -> bytes:
    return Scrypt(salt=salt, length=32, n=2 ** 15, r=8, p=1).derive(password.encode())


def set_up_password(password: str) -> dict:
    if len(password) < MIN_PASSWORD:
        raise ValueError(f"Use at least {MIN_PASSWORD} characters. A short sentence works well.")
    key = ec.generate_private_key(ec.SECP256R1())
    raw = key.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    salt, nonce = os.urandom(16), os.urandom(12)
    box = AESGCM(_pw_key(password, salt)).encrypt(nonce, raw, b"phygital-memory approver")
    pub = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    c = _new_card("password", pub, {"salt": _b64(salt), "box": _b64(nonce + box)})
    _save_card(c)
    return public(c)


def public(c: dict | None) -> dict | None:
    """The key card as Phygital Key knows it (nothing secret)."""
    return {k: c[k] for k in ("credential_id", "public_key", "rp_id", "name", "created")} if c else None


def keyring() -> dict:
    return {"keys": [public(card())] if card() else []}


def _sign(c: dict, msg: bytes, words: str, password: str | None) -> bytes:
    if c["kind"] == "chip":
        blob = (keychain.read(CHIP_KEYCHAIN, "chip") or "").strip()
        if not blob:
            raise NotSetUp()
        r = touchid._run("signer-sign", words, secret=(blob + "\n" + base64.b64encode(msg).decode()).encode())
        if not r or r.returncode != 0:
            raise Refused("Not approved.")
        return base64.b64decode(r.stdout.strip())
    if password is None:
        raise NeedPassword()
    with _lock:
        if time.time() < _fails["until"]:
            raise Refused(f"Too many wrong tries. Wait {int(_fails['until'] - time.time()) + 1} seconds.")
    try:
        box = _unb64(c["box"])
        raw = AESGCM(_pw_key(password, _unb64(c["salt"]))).decrypt(box[:12], box[12:], b"phygital-memory approver")
    except Exception:
        with _lock:
            _fails["n"] += 1
            _fails["until"] = time.time() + min(2 ** _fails["n"], 300)   # 2 s, 4 s, 8 s... up to 5 minutes
        raise Refused("That's not your approval password.")
    with _lock:
        _fails["n"] = 0
    return serialization.load_der_private_key(raw, None).sign(msg, ec.ECDSA(hashes.SHA256()))


# ---------- approving one exact request, and checking it ----------

def aud() -> str:
    from . import sharing
    return f"phygital-memory:{sharing.my_id()}"


def approve(request: dict, words: str, password: str | None = None) -> str:
    """The person's signed yes for this request (Touch ID prompt, or their password), checked before it's returned."""
    c = card()
    if not c:
        raise NotSetUp()
    req_hash = _b64(hashlib.sha256(canonical(request)).digest())
    now = int(time.time())
    claims = {"v": "pka.1", "id": _b64(secrets.token_bytes(16)), "aud": aud(), "request": request,
              "request_hash": req_hash, "level": "high", "iat": now, "exp": now + LIFE}
    client = json.dumps({"type": "webauthn.get", "challenge": _b64(challenge(claims)), "origin": ORIGIN,
                         "crossOrigin": False}, separators=(",", ":")).encode()
    auth = hashlib.sha256(RP_ID.encode()).digest() + bytes([0x05]) + (0).to_bytes(4, "big")   # present + verified
    sig = _sign(c, auth + hashlib.sha256(client).digest(), words, password)
    approval = _b64(json.dumps({"claims": claims, "signatures": [{
        "credential_id": c["credential_id"], "authenticator_data": _b64(auth), "client_data_json": _b64(client),
        "signature": _b64(sig)}]}, separators=(",", ":")).encode())
    verify(approval, request)
    with _lock:
        STATE.mkdir(parents=True, exist_ok=True)
        with SIGNED.open("a") as fh:
            fh.write(json.dumps({"t": now, "what": words, "approval": approval}) + "\n")
    return approval


def verify(approval: str, request: dict, now: int | None = None) -> dict:
    """Phygital Key's checks, in order, failing closed. Returns the claims when it's a valid, unused yes."""
    now = int(time.time()) if now is None else now
    try:
        obj = json.loads(_unb64(approval))
        claims, (sig,) = obj["claims"], obj["signatures"]
        assert set(obj) == {"claims", "signatures"} and claims["v"] == "pka.1"
    except Exception:
        raise Refused("MALFORMED")
    if claims["aud"] != aud():
        raise Refused("WRONG_AUDIENCE")
    if not (claims["iat"] <= now + 30 and now < claims["exp"] and claims["exp"] - claims["iat"] <= 300):
        raise Refused("EXPIRED")
    if _b64(hashlib.sha256(canonical(request)).digest()) != claims["request_hash"] or claims["request"] != request:
        raise Refused("REQUEST_MISMATCH")
    if claims["level"] != "high":
        raise Refused("ASSURANCE_TOO_LOW")
    c = public(card())
    if not c or sig["credential_id"] != c["credential_id"] or c["rp_id"] != RP_ID:
        raise Refused("UNTRUSTED_KEY")
    client, auth = _unb64(sig["client_data_json"]), _unb64(sig["authenticator_data"])
    cd = json.loads(client)
    if cd.get("type") != "webauthn.get" or cd.get("challenge") != _b64(challenge(claims)) or cd.get("origin") != ORIGIN \
            or cd.get("crossOrigin") is True or "topOrigin" in cd or auth[:32] != hashlib.sha256(RP_ID.encode()).digest():
        raise Refused("BAD_SIGNATURE")
    try:
        serialization.load_der_public_key(_unb64(c["public_key"])).verify(
            _unb64(sig["signature"]), auth + hashlib.sha256(client).digest(), ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        raise Refused("BAD_SIGNATURE")
    if not (auth[32] & 0x01 and auth[32] & 0x04):
        raise Refused("ASSURANCE_TOO_LOW")
    with _lock:
        for k in [k for k, exp in _seen.items() if exp <= now]:
            del _seen[k]
        if claims["id"] in _seen:
            raise Refused("REPLAYED")
        _seen[claims["id"]] = claims["exp"]
    return claims


def signed(n: int = 50) -> list[dict]:
    try:
        return [json.loads(x) for x in SIGNED.read_text().splitlines()[-n:]][::-1]
    except (OSError, ValueError):
        return []
