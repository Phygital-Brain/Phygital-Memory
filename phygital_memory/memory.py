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
        self._last_version: dict[str, float] = {}

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
            if entry.kind == "file" and path.lower().endswith(".md") and path.split("/")[1] not in HIDDEN:
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
            if existing:
                self._keep_version(rel, existing, data)
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

    def list_files(self) -> list[dict]:
        """Every folder and file (notes, images, other files), for the person's own sidebar."""
        with self._lock:
            self._need_open()
            out = []
            for path, entry in self._tree.walk():
                rel = path.lstrip("/")
                if rel.split("/")[0] in HIDDEN or entry.kind == "link":
                    continue
                item = {"path": rel, "kind": "folder" if entry.kind == "dir" else "file"}
                if entry.kind == "file":
                    st = self._tree.contents_path(entry).stat()
                    item.update(mtime=st.st_mtime, size=self._tree.file_size(entry))
                out.append(item)
            return out

    def read_bytes(self, rel: str) -> bytes:
        with self._lock:
            self._need_open()
            return self._tree.read_file(self._tree.resolve(_clean_path(rel, md=False)))

    def save_bytes(self, rel: str, data: bytes) -> str:
        """An image or other file, stored encrypted like the notes. Picks a free name if the path is taken."""
        rel = _clean_path(rel, md=False)
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("That file is too big (25 MB at most).")
        with self._lock:
            self._need_open()
            parent, name = self._make_parents(rel)
            taken = {e.name for e in self._tree.list_dir(parent.dir_id)}
            stem, dot, ext = name.rpartition(".") if "." in name else (name, "", "")
            n = 1
            while name in taken:
                n += 1
                name = f"{stem} {n}{dot}{ext}"
            self._writer.write_file(parent, name, data)
            return "/".join(rel.split("/")[:-1] + [name])

    def make_folder(self, rel: str) -> str:
        rel = _clean_path(rel, md=False)
        with self._lock:
            self._need_open()
            parent, name = self._make_parents(rel)
            if not any(e.name == name for e in self._tree.list_dir(parent.dir_id)):
                self._writer.make_dir(parent, name)
            return rel

    def move(self, old: str, new: str) -> str:
        """Rename or move a note, file or folder. Notes keep their .md ending."""
        old_entry_path = _clean_path(old, md=False)
        with self._lock:
            self._need_open()
            entry = self._tree.resolve(old_entry_path)
            new = _clean_path(new, md=entry.kind == "file" and old_entry_path.lower().endswith(".md"))
            parent, name = self._make_parents(new)
            if any(e.name == name for e in self._tree.list_dir(parent.dir_id)):
                raise Exists(f"'{new}' already exists.")
            self._writer.move(entry, parent, name)
            self._reindex()
            return new

    def trash(self, rel: str) -> None:
        """Move a note, file or folder to the hidden trash folder inside the lock (nothing is erased)."""
        rel = _clean_path(rel, md=False)
        with self._lock:
            self._need_open()
            entry = self._tree.resolve(rel)
            try:
                bin_ = self._tree.resolve(TRASH)
            except NotFound:
                root = self._tree.resolve("")
                bin_ = self._writer.make_dir(root, TRASH)
            self._writer.move(entry, bin_, f"{time.strftime('%Y%m%d-%H%M%S')} {Path(rel).name}")
            self._reindex()

    # ---------- version history (kept inside the lock, in a hidden folder) ----------

    def _keep_version(self, rel: str, entry, new_data: bytes) -> None:
        """Before a note changes, keep its old text as a version: at most one every VERSION_EVERY seconds per note
        (autosave runs often), the newest VERSION_KEEP per note. AI changes are kept the same way, so they can be undone."""
        now = time.time()
        if now - self._last_version.get(rel, 0) < VERSION_EVERY:
            return
        old = self._tree.read_file(entry)
        if old == new_data:
            return
        self._last_version[rel] = now
        folder = f"{VERSIONS}/{rel}"
        parent, _ = self._make_parents(f"{folder}/x")
        name = f"{time.strftime('%Y%m%d-%H%M%S', time.localtime(now))}.md"
        same = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
        self._writer.write_file(parent, name, old, replace=same)
        kept = sorted(e for e in self._tree.list_dir(parent.dir_id) if e.kind == "file")
        for e in sorted(kept, key=lambda e: e.name)[:-VERSION_KEEP]:
            self._writer.remove(e)

    def versions(self, rel: str) -> list[dict]:
        rel = _clean_path(rel)
        with self._lock:
            self._need_open()
            try:
                folder = self._tree.resolve(f"{VERSIONS}/{rel}")
            except NotFound:
                return []
            out = [{"id": e.name[:-3], "size": self._tree.file_size(e)}
                   for e in self._tree.list_dir(folder.dir_id) if e.kind == "file"]
            return sorted(out, key=lambda v: v["id"], reverse=True)

    def version(self, rel: str, vid: str) -> str:
        rel = _clean_path(rel)
        if not re.fullmatch(r"\d{8}-\d{6}", vid):
            raise ValueError("Unknown version.")
        with self._lock:
            self._need_open()
            return self._tree.read_file(self._tree.resolve(f"{VERSIONS}/{rel}/{vid}.md")).decode("utf-8", "replace")

    # ---------- links between notes (for backlinks and the graph) ----------

    def links(self) -> dict:
        """Every [[link]] between notes: {"nodes": [paths], "edges": [[from, to], ...], "missing": {from: [names]}}."""
        with self._lock:
            self._need_open()
            notes = [r[0] for r in self._con.execute("SELECT path FROM files ORDER BY path")]
            by_path = {p[:-3].lower(): p for p in notes}
            by_name: dict[str, str] = {}
            for p in notes:
                by_name.setdefault(Path(p).stem.lower(), p)
            edges, missing, tags = set(), {}, {}
            for p in notes:
                text = self.read(p)
                for t in re.findall(r"(?:^|\s)#([\w][\w/-]*)", re.sub(r"```.*?```", "", text, flags=re.S)):
                    if not t.isdigit():
                        tags[t] = tags.get(t, 0) + 1
                fm = re.match(r"---\n(.*?)\n---", text, re.S)
                if fm:
                    tm = re.search(r"^tags:\s*\[(.*?)\]|^tags:\s*\n((?:\s*-\s*.+\n?)+)", fm.group(1), re.M)
                    if tm:
                        for t in re.split(r"[,\n]", tm.group(1) or tm.group(2)):
                            t = t.strip().lstrip("-").strip().strip("'\"").lstrip("#")
                            if t:
                                tags[t] = tags.get(t, 0) + 1
                for m in re.finditer(r"!?\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", text):
                    name = m.group(1).strip().lower().removesuffix(".md")
                    target = by_path.get(name) or by_name.get(name.split("/")[-1])
                    if target and target != p:
                        edges.add((p, target))
                    elif not target and not re.search(r"\.\w{2,5}$", name):
                        missing.setdefault(p, []).append(m.group(1).strip())
            return {"nodes": notes, "edges": sorted(edges), "missing": missing,
                    "tags": sorted(tags.items(), key=lambda kv: (-kv[1], kv[0]))}

    def backlinks(self, rel: str) -> list[dict]:
        rel = _clean_path(rel)
        graph = self.links()
        out = []
        for src, dst in graph["edges"]:
            if dst == rel:
                line = next((l.strip() for l in self.read(src).splitlines() if "[[" in l and Path(rel).stem.lower() in l.lower()), "")
                out.append({"path": src, "line": line[:240]})
        return out

    # ---------- the person's settings for this folder (kept inside the lock) ----------

    def prefs(self) -> dict:
        with self._lock:
            self._need_open()
            try:
                return json.loads(self._tree.read_file(self._tree.resolve(PREFS)))
            except (NotFound, ValueError):
                return {}

    def save_prefs(self, prefs: dict) -> dict:
        data = json.dumps(prefs, ensure_ascii=False).encode()
        if len(data) > 200_000:
            raise ValueError("Settings too big.")
        with self._lock:
            self._need_open()
            parent, name = self._make_parents(PREFS)
            existing = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
            self._writer.write_file(parent, name, data, replace=existing)
            return prefs

    def _reindex(self) -> None:
        for (path,) in self._con.execute("SELECT path FROM files").fetchall():
            remove_file(self._con, path)
        self._index_all()


TRASH = ".trash"
VERSIONS = ".versions"
PREFS = ".phygital/prefs.json"
HIDDEN = (TRASH, VERSIONS, ".phygital")
VERSION_EVERY = 5 * 60
VERSION_KEEP = 50
MAX_FILE_BYTES = 25_000_000


def _clean_path(rel: str, md: bool = True) -> str:
    parts = [p for p in rel.replace("\\", "/").strip("/").split("/") if p]
    if not parts or any(p in (".", "..") or p.startswith(".") for p in parts):
        raise ValueError("Give a path inside the notes, like 'Projects/idea.md'.")
    if md and not parts[-1].lower().endswith(".md"):
        parts[-1] += ".md"
    if any(re.search(r'[<>:"|?*\x00-\x1f]', p) for p in parts):
        raise ValueError("That name has characters a note name can't use.")
    return "/".join(parts)
