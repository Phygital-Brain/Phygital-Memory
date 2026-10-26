"""The locked folders the app knows about, like Obsidian's and Baalda's vault switcher.

Each folder is its own Cryptomator-format vault with its own password, its own search index (in memory, while
open), its own Finder view and its own app passes. The list of folders (names and paths only, never a password or
key) is kept in folders.json in the app's support folder.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import threading
from pathlib import Path

from .finder import Finder
from .memory import Memory

STATE = Path(os.environ.get("PHYGITAL_MEMORY_STATE", "~/Library/Application Support/Phygital Memory")).expanduser()
REGISTRY = STATE / "folders.json"


def is_vault(path: Path) -> bool:
    return (path / "masterkey.cryptomator").is_file() and (path / "vault.cryptomator").is_file()


class Folder:
    def __init__(self, fid: str, name: str, path: Path):
        self.id, self.name, self.path = fid, name, Path(path)
        self.memory = Memory(self.path)
        self.finder = Finder(self.memory, volume=name)
        self.passes: set[str] = set()
        self.fails = {"n": 0, "until": 0.0}

    def info(self) -> dict:
        return {"id": self.id, "name": self.name, "path": str(self.path), "open": self.memory.is_open,
                "exists": is_vault(self.path), "finder": bool(self.finder.where())}

    def lock(self) -> None:
        self.finder.hide()          # close the Finder view first, and wait for it (locking would also close it, later)
        self.memory.lock()
        self.passes.clear()


class Folders:
    def __init__(self, default: Path | None):
        self._lock = threading.RLock()
        self.items: dict[str, Folder] = {}
        entries = []
        try:
            entries = json.loads(REGISTRY.read_text()).get("folders", [])
        except (OSError, ValueError):
            pass
        for e in entries:
            if isinstance(e, dict) and e.get("id") and e.get("path"):
                self.items[e["id"]] = Folder(e["id"], e.get("name") or Path(e["path"]).name, Path(e["path"]))
        if default and is_vault(default) and not any(f.path == default for f in self.items.values()):
            self._add(default, default.name, first=True)

    # ---------- the list ----------

    def _save(self) -> None:
        STATE.mkdir(parents=True, exist_ok=True)
        data = {"folders": [{"id": f.id, "name": f.name, "path": str(f.path)} for f in self.items.values()]}
        tmp = REGISTRY.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1))
        os.replace(tmp, REGISTRY)

    def _add(self, path: Path, name: str, first: bool = False) -> Folder:
        f = Folder(secrets.token_hex(4), name, path)
        self.items = ({f.id: f} | self.items) if first else (self.items | {f.id: f})
        self._save()
        return f

    def list(self) -> list[dict]:
        with self._lock:
            return [f.info() for f in self.items.values()]

    def get(self, fid: str | None) -> Folder:
        with self._lock:
            if fid and fid in self.items:
                return self.items[fid]
            if not fid and self.items:
                return next(iter(self.items.values()))
        raise LookupError("Unknown folder.")

    def open(self) -> list[Folder]:
        with self._lock:
            return [f for f in self.items.values() if f.memory.is_open]

    def add_existing(self, path: str) -> dict:
        p = Path(path).expanduser().resolve()
        if not is_vault(p):
            raise ValueError("That folder isn't a locked Phygital Memory (or Cryptomator) folder.")
        with self._lock:
            for f in self.items.values():
                if f.path == p:
                    return f.info()
            return self._add(p, p.name).info()

    def create(self, parent: str, name: str, password: str) -> dict:
        name = name.strip()
        if not name or re.search(r'[/\\:*?"<>|]', name) or name.startswith("."):
            raise ValueError("Pick a simple name for the folder.")
        base = Path(parent).expanduser().resolve()
        if not base.is_dir():
            raise ValueError("The place for the new folder doesn't exist.")
        target = base / name
        Memory.create(target, password)
        with self._lock:
            return self._add(target, name).info()

    def rename(self, fid: str, name: str) -> dict:
        name = name.strip()
        if not name:
            raise ValueError("The name can't be empty.")
        with self._lock:
            f = self.get(fid)
            f.name = name
            self._save()
            return f.info()

    def forget(self, fid: str) -> None:
        """Take a folder off the list (it is locked first; nothing on disk is touched)."""
        with self._lock:
            f = self.get(fid)
            f.lock()
            self.items.pop(fid, None)
            self._save()

    def lock_all(self) -> None:
        for f in list(self.items.values()):
            f.lock()


def pick_folder(prompt: str) -> str | None:
    """The Mac's own folder picker (the person chooses; nothing is read from the page)."""
    script = f'POSIX path of (choose folder with prompt "{prompt.replace(chr(34), "")}")'
    out = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=600)
    return out.stdout.strip() or None if out.returncode == 0 else None
