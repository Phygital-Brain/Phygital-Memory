"""One locked notes folder, opened only in memory.

The folder on disk is always encrypted (Cryptomator format 8). Unlocking keeps the key and a search index in
memory only: nothing readable is written to disk, not even the index. Every AI read goes through Engram search
(search, then open a result by its id). Locking wipes the key and drops the index.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
from pathlib import Path

from .engram_lib import ingest
from .engram_lib.db import connect, remove_file
from .engram_lib import search as engram
from .vault import keys
from .vault.manage import create_vault
from .vault.tree import NotFound, Tree
from .vault.writer import Exists, Writer, parent_and_name

HERE = Path(__file__).resolve().parent
IDLE_LOCK_SECONDS = 30 * 60
MAX_NOTE_BYTES = 2_000_000


class Locked(Exception):
    pass


def _engram_config() -> dict:
    cfg = json.loads((HERE / "engram_config.json").read_text())
    cfg["vault"] = Path("/nonexistent-phygital-memory")   # Engram never walks a folder here: we feed it notes
    cfg["display_vault"] = "Phygital Memory"
    cfg["db"] = Path(":memory:")
    cfg["private"]["enabled"] = False                       # the whole folder is locked already
    cfg["usage"]["enabled"] = False                         # usage counters would open a file on disk
    cfg["store_text_once"] = sqlite3.sqlite_version_info >= (3, 43, 0)
    return cfg


class Memory:
    def __init__(self, folder: Path, idle_lock: int = IDLE_LOCK_SECONDS):
        self.folder = Path(folder).expanduser()
        self.idle_lock = idle_lock
        self.cfg = _engram_config()
        self._lock = threading.RLock()
        self._key = self._tree = self._writer = self._con = None
        self._last_use = 0.0

    # ---------- open and close ----------

    @staticmethod
    def create(folder: Path, password: str) -> None:
        create_vault(Path(folder), password).wipe()

    @property
    def is_open(self) -> bool:
        with self._lock:
            self._sweep()
            return self._con is not None

    def unlock(self, password: str) -> dict:
        with self._lock:
            if self._con is not None:
                return self.status()
            key = keys.unlock_masterkey((self.folder / "masterkey.cryptomator").read_bytes(), password)
            try:
                config = keys.verify_vault_config((self.folder / "vault.cryptomator").read_bytes(), key)
                tree = Tree(self.folder, key, config)
                con = connect(":memory:", text_once=self.cfg["store_text_once"])
                con.execute("PRAGMA temp_store=MEMORY")   # sorting never spills note text to a temp file
            except BaseException:
                key.wipe()
                raise
            self._key, self._tree, self._writer, self._con = key, tree, Writer(tree), con
            self._touch()
            self._index_all()
            return self.status()

    def lock(self) -> None:
        with self._lock:
            if self._con is not None:
                self._con.close()
            if self._key is not None:
                self._key.wipe()
            self._key = self._tree = self._writer = self._con = None

    def status(self) -> dict:
        with self._lock:
            self._sweep()
            if self._con is None:
                return {"open": False, "folder": str(self.folder)}
            notes = self._con.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            left = int(self.idle_lock - (time.time() - self._last_use))
            return {"open": True, "folder": str(self.folder), "notes": notes, "locks_in_minutes": max(0, left // 60)}

    def _sweep(self) -> None:
        if self._con is not None and time.time() - self._last_use > self.idle_lock:
            self.lock()

    def _touch(self) -> None:
        self._last_use = time.time()

    def _need_open(self) -> None:
        self._sweep()
        if self._con is None:
            raise Locked("Phygital Memory is locked. The person unlocks it in the app with their password.")
        self._touch()

    # ---------- index (in memory only) ----------

    def _index_all(self) -> None:
        redact = ingest.make_redactor(self.cfg)
        for path, entry in self._tree.walk():
            if entry.kind == "file" and path.lower().endswith(".md"):
                self._index_one(path.lstrip("/"), entry, redact)
        ingest.count_backlinks(self._con, self.cfg)
        self._con.commit()

    def _index_one(self, rel: str, entry, redact=None) -> None:
        cfg = self.cfg
        redact = redact or ingest.make_redactor(cfg)
        if ingest.is_conflict(Path(rel).name) or self._tree.file_size(entry) > MAX_NOTE_BYTES:
            return
        text = self._tree.read_file(entry).decode("utf-8", "replace")
        if "\x00" in text[:4000] or ingest.has_skip_marker(text, cfg):
            return
        mtime = self._tree.contents_path(entry).stat().st_mtime
        meta, body = ingest.parse_frontmatter(redact(text))
        status = meta.get("status", "").lower()
        until = ingest.to_ts(meta.get("valid_until"))
        hidden = int(status in cfg["hide_status"] or (until is not None and until < time.time()))
        fw = (ingest.path_weight(rel, cfg) * cfg["status_weights"].get(status, 1.0)
              * cfg.get("type_weights", {}).get(meta.get("type", "").lower(), 1.0))
        evergreen = int(ingest.matches_any(rel, cfg["evergreen_paths"]))
        when = ingest.date_of(meta, Path(rel).name, mtime)
        chunks = [dict(heading=h, body=b, date=when, evergreen=evergreen, type=meta.get("type", ""),
                       project=meta.get("project", ""), status=status,
                       tags=(meta.get("tags", "") + " " + ingest.callout_text(b, cfg)).strip(), weight=fw)
                  for h, b in ingest.split_chunks(body, Path(rel).stem, cfg)]
        title = Path(rel).stem.replace("-", " ").replace("_", " ")
        ingest.add_file(self._con, rel, "vault", mtime, len(text), fw, hidden, title, chunks,
                        shelf=ingest.shelf_of(rel, cfg), until=until)

    # ---------- what an AI app may do: search, open a result, write ----------

    def search(self, q: str, n: int = 8) -> list[dict]:
        with self._lock:
            self._need_open()
            return engram.search(self.cfg, q, n, con=self._con, private=False)

    def get(self, chunk_id: int, whole_note: bool = False) -> dict | None:
        with self._lock:
            self._need_open()
            return engram.get(self.cfg, int(chunk_id), whole_note, con=self._con)

    def around(self, chunk_id: int) -> dict | None:
        with self._lock:
            self._need_open()
            return engram.around(self.cfg, int(chunk_id), con=self._con)

    def path_of(self, chunk_id: int) -> str:
        with self._lock:
            self._need_open()
            row = self._con.execute("SELECT file_path FROM chunks WHERE id=?", (int(chunk_id),)).fetchone()
            if not row:
                raise NotFound("No result with that id. Search first, then use an id from the results.")
            return row[0]

    def raw_of(self, chunk_id: int) -> tuple[str, str]:
        """The real note text (frontmatter and all) behind a search result: what an edit starts from."""
        with self._lock:
            rel = self.path_of(chunk_id)
            return rel, self.read(rel)

    def save(self, rel: str, text: str, new: bool = False) -> str:
        """Write a note (encrypted) and update the index. new=True refuses to replace an existing note."""
        rel = _clean_path(rel)
        data = text.encode("utf-8")
        if len(data) > MAX_NOTE_BYTES:
            raise ValueError("That note is too big.")
        with self._lock:
            self._need_open()
            parent, name = self._make_parents(rel)
            existing = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
            if existing and new:
                raise Exists(f"'{rel}' already exists. Open it from a search result to change it.")
            entry = self._writer.write_file(parent, name, data, replace=existing)
            remove_file(self._con, rel)
            self._index_one(rel, entry)
            self._con.commit()
            return rel

    def _make_parents(self, rel: str):
        parts = rel.split("/")
        for i in range(1, len(parts)):
            folder = "/".join(parts[:i])
            try:
                self._tree.resolve(folder)
            except NotFound:
                parent, name = parent_and_name(self._tree, folder)
                self._writer.make_dir(parent, name)
        return parent_and_name(self._tree, rel)

    # ---------- what only the person's own app shows ----------

    def list_notes(self) -> list[str]:
        with self._lock:
            self._need_open()
            return [r[0] for r in self._con.execute("SELECT path FROM files ORDER BY path")]

    def read(self, rel: str) -> str:
        with self._lock:
            self._need_open()
            return self._tree.read_file(self._tree.resolve(_clean_path(rel))).decode("utf-8", "replace")


def _clean_path(rel: str) -> str:
    parts = [p for p in rel.replace("\\", "/").strip("/").split("/") if p]
    if not parts or any(p in (".", "..") or p.startswith(".") for p in parts):
        raise ValueError("Give a path inside the notes, like 'Projects/idea.md'.")
    if not parts[-1].lower().endswith(".md"):
        parts[-1] += ".md"
    if any(re.search(r'[<>:"|?*\x00-\x1f]', p) for p in parts):
        raise ValueError("That name has characters a note name can't use.")
    return "/".join(parts)
