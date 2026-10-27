"""Sharing one folder or one file instead of the whole memory.

The shared part goes into its own small locked memory (a "share") with its own key, and only that travels to the
people let in, so the rest of the memory is out of their reach, not just hidden by the app.

- Shares live in the app's folder: STATE/shares/ID, each a normal memory, synced over the app's Syncthing.
- Its key is locked to the owner's personal key and to each person let in (sharing.py). Its password is random
  and thrown away: nobody ever types it.
- shares.json (on the owner's Mac only): {id: {memory: vault id, path, kind, name}}.
- The owner's app keeps the two in step while the memory is open on the owner's Mac (every few seconds). A change
  on one side is copied to the other. When both sides changed the same file, the owner's stays and theirs is kept
  next to it as "name (shared copy).ext". If nobody may edit, the owner's side always wins.
- What was last copied (each file's hash) is kept in STATE/shares/ID.sync, encrypted with the share's key, so a
  change made while the owner's memory was locked is still seen as a change, not a clash.
- If the shared folder or file is moved or renamed in the app, the share follows it. If it's gone (trashed), the
  copying stops and nothing is deleted on the other side."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import threading
import time
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from . import sharing
from .folders import STATE
from .memory import Memory
from .vault.manage import create_vault

HOME = STATE / "shares"
LIST = HOME / "shares.json"
_lock = threading.RLock()
_open: dict[str, Memory] = {}      # shares opened on the owner's side, while their memory is open
_seen: dict[str, dict] = {}        # per share: {path: (A sig, A hash, B sig, B hash)}, so unchanged files aren't read


def _all() -> dict:
    try:
        return json.loads(LIST.read_text())
    except (OSError, ValueError):
        return {}


def _save_all(d: dict) -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    tmp = HOME / f".shares-{secrets.token_hex(4)}.tmp"
    tmp.write_text(json.dumps(d))
    os.chmod(tmp, 0o600)
    os.replace(tmp, LIST)


def path_of(sid: str) -> Path:
    return HOME / sid


def get(sid: str) -> dict | None:
    s = _all().get(sid)
    return {**s, "id": sid} if s else None


def of_all() -> list[dict]:
    return [{**s, "id": k} for k, s in _all().items()]


def of_memory(vault_id: str) -> list[dict]:
    return [{**s, "id": k} for k, s in _all().items() if s["memory"] == vault_id]


def find(vault_id: str, rel: str) -> dict | None:
    return next((s for s in of_memory(vault_id) if s["path"] == rel), None)


def create(vault_id: str, rel: str, kind: str) -> dict:
    """A new share for one folder or file of a memory: an empty locked memory with the owner's key box in it."""
    with _lock:
        if s := find(vault_id, rel):
            return s
        sid = secrets.token_hex(8)
        HOME.mkdir(parents=True, exist_ok=True)
        key = create_vault(path_of(sid), secrets.token_urlsafe(32))   # the password is never used again
        try:
            sharing.start(path_of(sid), bytes(key.raw))
        finally:
            key.wipe()
        d = _all()
        d[sid] = {"memory": vault_id, "path": rel, "kind": kind, "name": rel.rsplit("/", 1)[-1], "made": time.time()}
        _save_all(d)
        return {**d[sid], "id": sid}


def key_of(sid: str) -> bytes:
    raw = sharing.my_key(path_of(sid))
    if raw is None:
        raise ValueError("This share's key is missing on this Mac.")
    return raw


def moved(vault_id: str, old: str, new: str) -> None:
    """The memory's folder or file was moved or renamed: shares of it (or inside it) follow."""
    with _lock:
        d = _all()
        for s in d.values():
            if s["memory"] == vault_id and (s["path"] == old or s["path"].startswith(old + "/")):
                s["path"] = new + s["path"][len(old):]
        _save_all(d)


def forget(sid: str) -> None:
    """Stop sharing this part: the share and its copy on this Mac go (copies others already have stay with them)."""
    with _lock:
        m = _open.pop(sid, None)
        if m:
            m.lock()
        d = _all()
        d.pop(sid, None)
        _save_all(d)
        shutil.rmtree(path_of(sid), ignore_errors=True)
        (HOME / f"{sid}.sync").unlink(missing_ok=True)
        _seen.pop(sid, None)


# ---------- keeping a share in step with its memory ----------

def _base_key(raw: bytes) -> bytes:
    return HKDF(hashes.SHA256(), 32, None, b"phygital-memory share sync v1").derive(raw)


def _read_base(sid: str, raw: bytes) -> dict:
    try:
        data = (HOME / f"{sid}.sync").read_bytes()
        return json.loads(AESGCM(_base_key(raw)).decrypt(data[:12], data[12:], b"sync"))
    except (OSError, ValueError, Exception):
        return {}


def _write_base(sid: str, raw: bytes, base: dict) -> None:
    nonce = os.urandom(12)
    p = HOME / f"{sid}.sync"
    tmp = HOME / f".{sid}-{secrets.token_hex(4)}.tmp"
    tmp.write_bytes(nonce + AESGCM(_base_key(raw)).encrypt(nonce, json.dumps(base).encode(), b"sync"))
    os.replace(tmp, p)


def _copy_name(rel: str) -> str:
    stem, dot, ext = rel.rpartition(".") if "." in rel.rsplit("/", 1)[-1] else (rel, "", "")
    return f"{stem} (shared copy){dot}{ext}"


def sync(sid: str, a: Memory) -> int:
    """One pass: copy what changed between the memory (a) and its share. Returns how many files were copied."""
    s = get(sid)
    if not s or not a.is_open:
        return 0
    with _lock:
        b = _open.get(sid)
        if b is None or not b.is_open:
            raw = key_of(sid)
            b = Memory(path_of(sid))
            b.unlock_with_key(sharing.masterkey(raw))
            _open[sid] = b
    kind = a.kind_of(s["path"])
    if kind != s["kind"]:
        return 0   # gone or replaced: stop copying, delete nothing on their side
    raw = key_of(sid)
    two_way = any(x["role"] == "edit" for x in sharing.members(path_of(sid), raw))
    prefix = s["path"]
    to_b = (lambda r: r[len(prefix) + 1:]) if kind == "folder" else (lambda r: r.rsplit("/", 1)[-1])
    to_a = (lambda r: f"{prefix}/{r}") if kind == "folder" else (lambda r: prefix)
    asig = {to_b(r): v for r, v in a.file_sigs(prefix).items()}
    bsig = b.file_sigs("")
    if kind == "file":
        bsig = {r: v for r, v in bsig.items() if r == s["name"]}
    base = _read_base(sid, raw)
    seen = _seen.setdefault(sid, {})

    def h(side, r, sig):
        if sig is None:
            return None
        old = seen.get(r)
        i = 0 if side is a else 2
        if old and old[i] == list(sig):
            return old[i + 1]
        data = (a.get_file(to_a(r)) if side is a else b.get_file(r))
        return hashlib.sha256(data).hexdigest()

    copied, changed, fresh = 0, False, set()
    for r in sorted(set(asig) | set(bsig) | set(base)):
        ah, bh, was = h(a, r, asig.get(r)), h(b, r, bsig.get(r)), base.get(r)
        ah0, bh0 = ah, bh
        if ah == bh:
            pass
        elif not two_way or bh == was:          # only the owner's side changed (or nobody else may edit)
            if ah is None:
                b.trash(r)
            else:
                b.put_file(r, a.get_file(to_a(r)))
            if was != ah:   # the owner's own change: into the history, as theirs
                try:
                    sharing.log_change(path_of(sid), raw, "deleted" if ah is None else "added" if was is None else "edited", r)
                except Exception:
                    pass
            bh = ah
        elif ah == was:                          # only their side changed
            if bh is None:
                a.trash(to_a(r))
            else:
                a.put_file(to_a(r), b.get_file(r))
            ah = bh
        elif ah is None:                         # both changed, one side deleted it: the file stays
            a.put_file(to_a(r), b.get_file(r))
            ah = bh
        elif bh is None:
            b.put_file(r, a.get_file(to_a(r)))
            bh = ah
        else:                                    # both changed: the owner's stays in place, theirs goes next to it
            a.put_file(a.free_path(_copy_name(to_a(r))), b.get_file(r))
            b.put_file(r, a.get_file(to_a(r)))
            bh = ah
        if (ah, bh) != (ah0, bh0):
            copied += 1
            fresh.add(r)   # just written: read it again next time
        if ah != was:
            changed = True
            if ah is None:
                base.pop(r, None)
            else:
                base[r] = ah
        seen.pop(r, None)
    for r in (set(asig) & set(bsig)) - fresh:
        if r in base:
            seen[r] = (list(asig[r]), base[r], list(bsig[r]), base[r])
    if changed:
        _write_base(sid, raw, base)
    return copied


def close_for(vault_id: str) -> None:
    """The memory locked: its shares lock too on this Mac."""
    with _lock:
        for s in of_memory(vault_id):
            m = _open.pop(s["id"], None)
            if m:
                m.lock()
