"""The sealed list of the person's yeses: unlocks, AI apps let in, what each may reach. Each line is chained to the one
before and sealed with a key kept in the Keychain, so a line changed or taken out later shows up as broken.

shortcut: a program running as this Mac user could read the seal key and forge lines. This catches later edits to the
file, not a program that knows how; signed Phygital Key receipts (a key behind Touch ID) are the upgrade."""
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import threading
import time

from .folders import STATE

FILE = STATE / "approvals.jsonl"
KEYCHAIN = os.environ.get("PHYGITAL_MEMORY_SEAL_KEYCHAIN", "Phygital Memory seal")
_lock = threading.Lock()
_key: bytes | None = None


def _seal_key() -> bytes:
    global _key
    if _key is None:
        r = subprocess.run(["security", "find-generic-password", "-a", "seal", "-s", KEYCHAIN, "-w"],
                           capture_output=True, text=True)
        k = r.stdout.strip() if r.returncode == 0 else ""
        if not k:
            k = secrets.token_hex(32)
            subprocess.run(["security", "add-generic-password", "-U", "-a", "seal", "-s", KEYCHAIN, "-w", k],
                           capture_output=True, check=True)
        _key = bytes.fromhex(k)
    return _key


def _seal(prev: str, line: dict) -> str:
    body = json.dumps({k: v for k, v in line.items() if k != "seal"}, sort_keys=True, ensure_ascii=False)
    return hmac.new(_seal_key(), (prev + body).encode(), hashlib.sha256).hexdigest()


def _read() -> list[dict]:
    try:
        return [json.loads(x) for x in FILE.read_text().splitlines() if x.strip()]
    except FileNotFoundError:
        return []
    except ValueError:
        return [{"t": 0, "what": "This list was damaged.", "detail": "", "how": "", "prev": "", "seal": ""}]


def add(what: str, detail: str = "", how: str = "") -> None:
    """One yes: what was allowed, the detail (which memory, which app), and how it was confirmed."""
    with _lock:
        lines = _read()
        line = {"t": time.time(), "what": what[:120], "detail": detail[:200], "how": how,
                "prev": lines[-1]["seal"] if lines else ""}
        line["seal"] = _seal(line["prev"], line)
        STATE.mkdir(parents=True, exist_ok=True)
        with FILE.open("a") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def listing(limit: int = 200) -> list[dict]:
    """Newest first, each with sealed: True when it and its link to the line before are untouched."""
    with _lock:
        lines = _read()
    out, prev = [], ""
    for x in lines:
        ok = bool(x.get("seal")) and x.get("prev") == prev and hmac.compare_digest(_seal(prev, x), x["seal"])
        out.append({"t": x.get("t", 0), "what": x.get("what", ""), "detail": x.get("detail", ""),
                    "how": x.get("how", ""), "sealed": ok})
        prev = x.get("seal", "")
    return out[::-1][:limit]
