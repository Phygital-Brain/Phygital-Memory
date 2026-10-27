"""One locked notes folder, opened only in memory.

The folder on disk is always encrypted (Cryptomator format 8). Unlocking keeps the key and a search index in
memory only: nothing readable is written to disk, not even the index. Every AI read goes through Engram search
(search, then open a result by its id). Locking wipes the key and drops the index.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import shutil
import sqlite3
import threading
import time
from pathlib import Path

from . import docx
from .engram_lib import ingest
from .engram_lib.db import connect, remove_file
from .engram_lib import search as engram
from .vault import keys
from .vault.manage import create_vault
from .vault.tree import Entry, NotFound, Tree
from .vault.writer import Exists, Writer, parent_and_name

HERE = Path(__file__).resolve().parent
IDLE_LOCK_SECONDS = None   # no auto-lock: a folder stays open until the person locks it or closes the app
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
    def __init__(self, folder: Path, idle_lock: int | None = IDLE_LOCK_SECONDS):
        self.folder = Path(folder).expanduser()
        self.idle_lock = idle_lock
        self.cfg = _engram_config()
        self._lock = threading.RLock()
        self._key = self._tree = self._writer = self._con = None
        self._last_use = 0.0
        self._last_version: dict[str, float] = {}
        self.on_lock: list = []
        self._gen = 0              # goes up whenever a note changes; the links cache is only good for one value
        self._links_cache = None   # called after every lock (the Finder view closes itself here)
        self._synced = 0.0         # when notes changed by a cloud drive were last picked up
        self._skipped: dict[str, float] = {}
        self.clashes: list[dict] = []   # clash copies made since unlock, for the app to tell the person once

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
                # Already open: the password must still be right. (Otherwise anyone could ask for a fresh app pass
                # for an open folder and read every note directly, around Engram.)
                keys.unlock_masterkey((self.folder / "masterkey.cryptomator").read_bytes(), password).wipe()
                self._touch()
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
            self._fix_clash_copies()
            try:
                self._empty_old_trash()
            except Exception:
                pass   # never let trash upkeep stop an unlock
            self._index_all()
            self._synced = time.time()
            return self.status()

    def lock(self) -> None:
        with self._lock:
            if self._con is not None:
                self._con.close()
            was_open = self._key is not None
            if self._key is not None:
                self._key.wipe()
            self._key = self._tree = self._writer = self._con = None
            self._links_cache = None
            self.clashes = []
        if was_open:   # on its own thread: unmounting Finder talks to us, and we may still hold the lock here
            def run():
                for fn in list(self.on_lock):
                    try:
                        fn()
                    except Exception:
                        pass
            threading.Thread(target=run, name="on-lock", daemon=True).start()

    def status(self) -> dict:
        with self._lock:
            self._sweep()
            if self._con is None:
                return {"open": False, "folder": str(self.folder)}
            notes = self._con.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            return {"open": True, "folder": str(self.folder), "notes": notes}

    def _sweep(self) -> None:
        if self.idle_lock and self._con is not None and time.time() - self._last_use > self.idle_lock:
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
        self._gen += 1
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
            self._sync()
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

    def save(self, rel: str, text: str, new: bool = False, base: str | None = None, keep_version: bool = False) -> str:
        """Write a note (encrypted) and update the index. new=True refuses to replace an existing note. Returns where
        the text went: the note itself, or a clash copy (see save_merge)."""
        return self.save_merge(rel, text, new, base, keep_version)[0]

    def save_merge(self, rel: str, text: str, new: bool = False, base: str | None = None,
                   keep_version: bool = False) -> tuple[str, str | None]:
        """Like save, and also says when two edits were put together: (path, merged text or None).

        base is the note's text as the editor last saw it. If the note changed since (a cloud drive brought another
        device's edit, or an AI app changed it), nothing is written over that change. Like Baalda: when the two
        edits touch different lines both go into the note; when they touch the same lines, this text goes into a
        clash copy next to it instead, and the clash copy's path is returned."""
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
            merged = None
            if existing and base is not None:
                now = self._tree.read_file(existing)
                if now != base.encode("utf-8") and now != data:
                    merged = merge3(base, now.decode("utf-8", "replace"), text)
                    if merged is None:
                        return self._clash_copy(parent, rel, data), None
                    data, keep_version = merged.encode("utf-8"), True
            self._write_note(rel, parent, name, existing, data, keep_version)
            return rel, merged

    def update(self, rel: str, change, keep_version: bool = True) -> tuple[str, str]:
        """Read a note, change it with change(text) -> new text, and write it, with nothing else getting in between.
        For AI apps: two of them adding to a note at the same moment both land. Returns (before, after)."""
        rel = _clean_path(rel)
        with self._lock:
            self._need_open()
            before = self.read(rel)
            after = change(before)
            if len(after.encode("utf-8")) > MAX_NOTE_BYTES:
                raise ValueError("That note is too big.")
            if after != before:
                parent, name = parent_and_name(self._tree, rel)
                existing = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
                self._write_note(rel, parent, name, existing, after.encode("utf-8"), keep_version)
            return before, after

    def _write_note(self, rel, parent, name, existing, data: bytes, keep_version: bool) -> None:
        if existing:
            self._keep_version(rel, existing, data, force=keep_version)
        entry = self._writer.write_file(parent, name, data, replace=existing)
        remove_file(self._con, rel)
        self._index_one(rel, entry)
        self._con.commit()

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

    # ---------- sync clashes (two devices, or the app and an AI app, changed the same note) ----------
    # Same rule as Baalda: never write over a change this side hasn't seen. Both versions are kept, the other side's
    # under the note's own name and ours as "name (conflict YYYY-MM-DD).md", and the person is told once.

    def _clash_copy(self, parent, rel: str, data: bytes) -> str:
        stem, dot, ext = Path(rel).name.rpartition(".") if "." in Path(rel).name else (Path(rel).name, "", "")
        here = self._tree.list_dir(parent.dir_id)
        for e in here:   # the same text already kept from an earlier try: reuse it, never a second copy
            if e.kind == "file" and e.name.startswith(f"{stem} (conflict ") and self._tree.read_file(e) == data:
                return "/".join(rel.split("/")[:-1] + [e.name])
        taken = {e.name for e in here}
        name, n = f"{stem} (conflict {time.strftime('%Y-%m-%d')}){dot}{ext}", 1
        while name in taken:
            n += 1
            name = f"{stem} (conflict {time.strftime('%Y-%m-%d')} {n}){dot}{ext}"
        entry = self._writer.write_file(parent, name, data)
        copy = "/".join(rel.split("/")[:-1] + [name])
        if copy.lower().endswith(".md") and copy.split("/")[0] not in HIDDEN:
            remove_file(self._con, copy)
            self._index_one(copy, entry)
            self._con.commit()
        self.clashes.append({"path": rel, "copy": copy, "t": time.time()})
        del self.clashes[:-50]
        if rel.lower().endswith(".md") and rel.split("/")[0] not in HIDDEN:
            self._conflict_task(rel, copy)
        return copy

    def _conflict_task(self, rel: str, copy: str) -> None:
        """A clash copy becomes an AI task: the AI puts what's missing into the note, and finishing the task moves
        the copy to the trash (where it can still be restored)."""
        try:
            items = self.todo()
            if any(i.get("copy") == copy and not i.get("done") for i in items):
                return
            ask = (f'This note was changed in two places at once. The other version is kept as "{Path(copy).stem}". '
                   "Bring anything from it that's missing here into this note, keeping both sides' work, then finish "
                   "this task. The other version then goes to the trash.")
            self._save_todo(items + [{"id": "h-" + secrets.token_hex(4), "path": rel, "copy": copy, "ask": ask,
                                      "t": time.time(), "done": False}])
        except Exception:
            pass   # the copy itself is what matters; the task is a helper

    def _fix_clash_copies(self) -> int:
        """Cloud drives keep both sides of a clash as an extra encrypted file, like "ABC (1).c9r" or "ABC (conflicted
        copy ...).c9r". Its name no longer decrypts, so it would just vanish. Exact duplicates are removed; the rest
        get a readable clash name next to the note. Returns how many were sorted out."""
        self._tree.conflicts = []
        for _ in self._tree.walk():
            pass
        found, self._tree.conflicts = list(dict.fromkeys(self._tree.conflicts)), []
        fixed = 0
        for path, dir_id in found:
            m = re.match(r"[A-Za-z0-9_=-]+", path.name)
            if not path.is_file() or not m:
                continue   # a clashed folder is left as it is (rare; nothing in it is lost)
            try:
                clear = self._tree.names.decrypt(m.group(0), dir_id)
                data = self._tree.read_file(Entry(clear, "file", path))
            except Exception:
                continue   # not from this folder's key: leave it alone
            parent = Entry("", "dir", self._tree.dir_location(dir_id), dir_id)
            main = next((e for e in self._tree.list_dir(dir_id) if e.name == clear), None)
            if main is None:
                self._writer.write_file(parent, clear, data)
            elif self._tree.read_file(main) != data:
                rel = self._rel_in(dir_id, clear)
                if rel is None:
                    continue
                self._clash_copy(parent, rel, data)
            path.unlink()
            fixed += 1
        return fixed

    def _rel_in(self, dir_id: bytes, name: str) -> str | None:
        if dir_id == b"":
            return name
        for p, e in self._tree.walk():
            if e.kind == "dir" and e.dir_id == dir_id:
                return f"{p.lstrip('/')}/{name}"
        return None

    def _adopt_lost_folders(self) -> None:
        """GitHub sync: two Macs made the same folder, each with its own ID, and git kept one. What's inside the
        other one is moved into the kept folder, so nothing is lost (see gitsync.py)."""
        store = getattr(self, "lost_store", None) or self.folder / ".git" / "phygital-lost-folders.json"
        if not store.exists():
            return
        try:
            items = json.loads(store.read_text())
        except (OSError, ValueError):
            items = []
        for it in items:
            try:
                kept_id = (self.folder / it["dir"] / "dir.c9r").read_bytes()
                self._fold_in(it["id"].encode("ascii"), kept_id)
            except Exception:
                continue
        store.unlink(missing_ok=True)

    def _fold_in(self, lost_id: bytes, kept_id: bytes) -> None:
        lost_at = self._tree.dir_location(lost_id)
        if lost_id == kept_id or not lost_at.is_dir():
            return
        kept = Entry("", "dir", self._tree.dir_location(kept_id), kept_id)
        here = {e.name: e for e in self._tree.list_dir(kept_id)}
        for e in self._tree.list_dir(lost_id):
            other = here.get(e.name)
            if other is None:
                self._writer.move(e, kept, e.name)
            elif e.kind == "dir" and other.kind == "dir":
                self._fold_in(e.dir_id, other.dir_id)
            elif e.kind == "file" and other.kind == "file" and self._tree.read_file(e) == self._tree.read_file(other):
                self._writer.remove(e)
            else:   # same name, different content: keep both
                stem, dot, ext = e.name.rpartition(".") if "." in e.name else (e.name, "", "")
                taken, n = set(here), 1
                name = f"{stem} (conflict {time.strftime('%Y-%m-%d')}){dot}{ext}"
                while name in taken:
                    n += 1
                    name = f"{stem} (conflict {time.strftime('%Y-%m-%d')} {n}){dot}{ext}"
                self._writer.move(e, kept, name)
        if all(p.name == "dirid.c9r" for p in lost_at.iterdir()):
            shutil.rmtree(lost_at, ignore_errors=True)

    def _sync(self) -> None:
        """Pick up notes a cloud drive (or Finder) changed on disk: at most every few seconds, only what changed."""
        if time.time() - self._synced < SYNC_EVERY:
            return
        self._synced = time.time()
        self._adopt_lost_folders()
        self._tree.conflicts = []
        disk = {}
        for path, entry in self._tree.walk():
            rel = path.lstrip("/")
            if entry.kind == "file" and rel.lower().endswith(".md") and rel.split("/")[0] not in HIDDEN:
                disk[rel] = entry
        if self._tree.conflicts and self._fix_clash_copies():
            self._synced = 0
            return self._sync()
        known = dict(self._con.execute("SELECT path, mtime FROM files"))
        changed = False
        for rel in known.keys() - disk.keys():
            remove_file(self._con, rel)
            changed = True
        for rel, entry in disk.items():
            mtime = self._tree.contents_path(entry).stat().st_mtime
            if known.get(rel) != mtime and self._skipped.get(rel) != mtime:
                remove_file(self._con, rel)
                self._index_one(rel, entry)
                if not self._con.execute("SELECT 1 FROM files WHERE path=?", (rel,)).fetchone():
                    self._skipped[rel] = mtime   # too big, not text, or marked to skip: don't retry until it changes
                changed = True
        if changed:
            self._gen += 1
            ingest.count_backlinks(self._con, self.cfg)
            self._con.commit()

    # ---------- what only the person's own app shows ----------

    def gen(self) -> int | None:
        """A number that goes up whenever a note changes here or on disk (a cloud drive, another device). The app
        polls it to reload open notes; it doesn't count as use, so polling never keeps the folder unlocked."""
        with self._lock:
            if self._con is None:
                return None
            self._sync()
            return self._gen

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
            self._sync()
            out = []
            for path, entry in self._tree.walk():
                rel = path.lstrip("/")
                if rel.split("/")[0] in HIDDEN or entry.kind == "link" or entry.name == ".DS_Store" \
                        or entry.name.startswith("._"):
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
            entry = self._tree.resolve(_clean_path(rel, md=False))
            if self._tree.file_size(entry) > MAX_FILE_BYTES:
                raise ValueError("Too big to open in the app (over 25 MB). Use Show in Finder, or Export a copy.")
            return self._tree.read_file(entry)

    def write_bytes(self, rel: str, data: bytes, base: bytes | None = None) -> str:
        """Write any file at exactly this path (replacing it). Notes go through save(), so they keep versions
        and stay searchable. With base (the bytes the editor started from), a file that changed meanwhile is not
        written over: this version goes to a conflict copy, whose path is returned."""
        rel = _clean_path(rel, md=False)
        if rel.lower().endswith(".md"):
            return self.save(rel, data.decode("utf-8", "replace"),
                             base=None if base is None else base.decode("utf-8", "replace"))
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("That file is too big (25 MB at most).")
        with self._lock:
            self._need_open()
            parent, name = self._make_parents(rel)
            existing = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
            if existing and base is not None:
                now = self._tree.read_file(existing)
                if now != base and now != data:
                    return self._clash_copy(parent, rel, data)
            self._writer.write_file(parent, name, data, replace=existing)
            return rel

    # ---------- Word files: change words, keep the format (see docx.py) ----------

    def docx_read(self, rel: str) -> dict:
        data = self.read_bytes(rel)
        return {"paragraphs": docx.paragraphs(data), "base": hashlib.sha256(data).hexdigest()}

    def docx_save(self, rel: str, changes: dict, base: str) -> dict:
        """Apply paragraph changes. If the file changed since `base` (its hash when read), nothing is written."""
        rel = _clean_path(rel, md=False)
        with self._lock:
            self._need_open()
            entry = self._tree.resolve(rel)
            data = self._tree.read_file(entry)
            if hashlib.sha256(data).hexdigest() != base:
                # changed somewhere else meanwhile: theirs stays, ours goes into a conflict copy next to it
                try:
                    ours = docx.edit(data, {int(k): v for k, v in changes.items()})
                except docx.DocxError:
                    ours = None
                if ours is None or ours == data:
                    return {"conflict": "", "base": hashlib.sha256(data).hexdigest()}
                parent, _ = parent_and_name(self._tree, rel)
                return {"conflict": self._clash_copy(parent, rel, ours), "base": hashlib.sha256(data).hexdigest()}
            out = docx.edit(data, {int(k): v for k, v in changes.items()})
            if len(out) > MAX_FILE_BYTES:
                raise ValueError("That file is too big (25 MB at most).")
            if out != data:
                self._writer.write_file(None, entry.name, out, replace=entry)
            return {"base": hashlib.sha256(out).hexdigest()}

    def save_bytes(self, rel: str, data: bytes) -> str:
        """An image or other file, stored encrypted like the notes. Picks a free name if the path is taken."""
        rel = _clean_path(rel, md=False)
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("That file is too big (25 MB at most).")
        with self._lock:
            self._need_open()
            parent, name = self._free_name(rel)
            self._writer.write_file(parent, name, data)
            self._gen += 1   # the graph shows every file, so it needs a fresh look
            return "/".join(rel.split("/")[:-1] + [name])

    def _free_name(self, rel: str):
        """The folder for rel, and rel's name or "name 2.ext" (3, 4...) if that's taken."""
        parent, name = self._make_parents(rel)
        taken = {e.name for e in self._tree.list_dir(parent.dir_id)}
        stem, dot, ext = name.rpartition(".") if "." in name else (name, "", "")
        n = 1
        while name in taken:
            n += 1
            name = f"{stem} {n}{dot}{ext}"
        return parent, name

    def _import_file(self, rel: str, src: Path) -> str:
        """A file from the Mac, encrypted straight from disk a part at a time: any size."""
        parent, name = self._free_name(_clean_path(rel, md=False))
        self._writer.write_file_from(parent, name, src)
        self._gen += 1
        return "/".join(rel.split("/")[:-1] + [name])

    def import_paths(self, into: str, sources: list[str]) -> dict:
        """Copy files and folders from the Mac into this folder, encrypted. Never replaces anything: a name that is
        taken gets " 2". Any size works (big files are encrypted a part at a time). Hidden files and links are
        skipped. Returns what came in."""
        into = _clean_path(into, md=False) if into else ""
        done, skipped = [], 0
        with self._lock:
            self._need_open()
            for src in map(Path, sources):
                if src.name.startswith(".") or src.is_symlink():
                    skipped += 1
                    continue
                if src.is_dir():
                    top = self._free_folder(f"{into}/{src.name}".lstrip("/"))
                    for f in sorted(src.rglob("*")):
                        rel = f.relative_to(src)
                        if any(p.startswith(".") for p in rel.parts) or f.is_symlink():
                            skipped += f.is_file()
                            continue
                        if f.is_dir():
                            self.make_folder(f"{top}/{rel.as_posix()}")
                        elif len(done) >= MAX_IMPORT:
                            skipped += 1
                        else:
                            done.append(self._import_file(f"{top}/{rel.as_posix()}", f))
                elif src.is_file():
                    if len(done) >= MAX_IMPORT:
                        skipped += 1
                    else:
                        done.append(self._import_file(f"{into}/{src.name}".lstrip("/"), src))
            self._synced = 0   # index the new notes now
            self._sync()
        return {"imported": done, "skipped": skipped}

    def _free_folder(self, rel: str) -> str:
        rel = _clean_path(rel, md=False)
        parent, name = self._make_parents(rel)
        taken = {e.name for e in self._tree.list_dir(parent.dir_id)}
        base, n = name, 1
        while name in taken:
            n += 1
            name = f"{base} {n}"
        return self.make_folder("/".join(rel.split("/")[:-1] + [name]))

    def export(self, rel: str, dest: str) -> int:
        """Write a decrypted copy of a note, file or folder to a place the person chose on the Mac. A folder goes in
        as a new folder inside dest (" 2" if the name is taken). Returns how many files were written."""
        rel = _clean_path(rel, md=False)
        with self._lock:
            self._need_open()
            entry = self._tree.resolve(rel)
            if entry.kind == "file":
                with open(dest, "wb") as out_file:
                    self._tree.read_file_to(entry, out_file)
                return 1
            out, n = Path(dest) / entry.name, 1
            while out.exists():
                n += 1
                out = Path(dest) / f"{entry.name} {n}"
            count = 0
            for path, e in self._tree.walk():
                p = path.lstrip("/")
                if not p.startswith(rel + "/"):
                    continue
                target = out / p[len(rel) + 1:]
                if e.kind == "dir":
                    target.mkdir(parents=True, exist_ok=True)
                elif e.kind == "file":
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with open(target, "wb") as out_file:
                        self._tree.read_file_to(e, out_file)
                    count += 1
            out.mkdir(parents=True, exist_ok=True)   # an empty folder still comes out as a folder
            return count

    def make_folder(self, rel: str) -> str:
        rel = _clean_path(rel, md=False)
        with self._lock:
            self._need_open()
            parent, name = self._make_parents(rel)
            if not any(e.name == name for e in self._tree.list_dir(parent.dir_id)):
                self._writer.make_dir(parent, name)
                self._gen += 1
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
            self.todo_moved(old_entry_path, new)
            priv = self.ai_private()   # a private folder stays private when it moves or is renamed
            moved = [new + p[len(old_entry_path):] if p == old_entry_path or p.startswith(old_entry_path + "/") else p
                     for p in priv]
            if moved != priv:
                self._save_ai_private(moved)
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
            taken = {e.name for e in self._tree.list_dir(bin_.dir_id)}
            name, n = f"{time.strftime('%Y%m%d-%H%M%S')} {Path(rel).name}", 1
            while name in taken:
                n += 1
                name = f"{time.strftime('%Y%m%d-%H%M%S')}-{n} {Path(rel).name}"
            self._writer.move(entry, bin_, name)
            where = self._json(TRASH_INDEX, {})
            where[name] = rel   # so Restore can put it back where it was
            self._put_json(TRASH_INDEX, where)
            self._reindex()

    def _empty_old_trash(self) -> None:
        """Things in the trash longer than TRASH_DAYS are removed for good (checked on unlock)."""
        try:
            bin_ = self._tree.resolve(TRASH)
        except NotFound:
            return
        cutoff = time.time() - TRASH_DAYS * 86400
        where, gone = self._json(TRASH_INDEX, {}), False
        for e in self._tree.list_dir(bin_.dir_id):
            try:
                t = time.mktime(time.strptime(e.name.partition(" ")[0][:15], "%Y%m%d-%H%M%S"))
            except ValueError:
                continue
            if t < cutoff:
                self._writer.remove_tree(e)
                where.pop(e.name, None)
                gone = True
        if gone:
            self._put_json(TRASH_INDEX, where)

    def trash_list(self) -> list[dict]:
        """What is in the trash, newest first: {id, name, path (where it was), kind, t}."""
        with self._lock:
            self._need_open()
            try:
                bin_ = self._tree.resolve(TRASH)
            except NotFound:
                return []
            where = self._json(TRASH_INDEX, {})
            out = []
            for e in self._tree.list_dir(bin_.dir_id):
                stamp, _, name = e.name.partition(" ")
                try:
                    t = time.mktime(time.strptime(stamp[:15], "%Y%m%d-%H%M%S"))
                except ValueError:
                    t, name = 0, e.name
                out.append({"id": e.name, "name": name, "path": where.get(e.name, name),
                            "kind": "folder" if e.kind == "dir" else "file", "t": t})
            return sorted(out, key=lambda i: -i["t"])

    def trash_restore(self, tid: str) -> str:
        """Put a trashed note, file or folder back where it was. Never over something already there."""
        with self._lock:
            self._need_open()
            item = next((i for i in self.trash_list() if i["id"] == tid), None)
            if not item:
                raise LookupError("That item isn't in the trash any more.")
            target = _clean_path(item["path"], md=False)
            try:
                self._tree.resolve(target)
                raise Exists(f"'{target}' already exists. Rename or move that one first, then restore.")
            except NotFound:
                pass
            entry = self._tree.resolve(f"{TRASH}/{tid}")
            parent, name = self._make_parents(target)
            self._writer.move(entry, parent, name)
            where = self._json(TRASH_INDEX, {})
            where.pop(tid, None)
            self._put_json(TRASH_INDEX, where)
            self._reindex()
            return target

    def _json(self, rel: str, default):
        try:
            return json.loads(self._tree.read_file(self._tree.resolve(rel)))
        except (NotFound, ValueError):
            return default

    def _put_json(self, rel: str, value) -> None:
        parent, name = self._make_parents(rel)
        existing = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
        self._writer.write_file(parent, name, json.dumps(value, ensure_ascii=False).encode(), replace=existing)

    # ---------- version history (kept inside the lock, in a hidden folder) ----------

    def _keep_version(self, rel: str, entry, new_data: bytes, force: bool = False) -> None:
        """Before a note changes, keep its old text as a version: at most one every VERSION_EVERY seconds per note
        (autosave runs often), the newest VERSION_KEEP per note. AI changes are kept the same way, so they can be undone."""
        now = time.time()
        if not force and now - self._last_version.get(rel, 0) < VERSION_EVERY:
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
        kept = sorted((e for e in self._tree.list_dir(parent.dir_id) if e.kind == "file"), key=lambda e: e.name)
        for e in kept[:-VERSION_KEEP]:
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
        """Every [[link]] between notes, and from notes to other files: {"nodes": [note paths], "files": [other file
        paths], "folders": [folder paths], "edges": [[from, to], ...], "missing": {from: [names]}}."""
        with self._lock:
            self._need_open()
            if self._links_cache and self._links_cache[0] == self._gen:
                return self._links_cache[1]
            notes = [r[0] for r in self._con.execute("SELECT path FROM files ORDER BY path")]
            wanted = set(notes)
            texts, files, dirs = {}, [], []   # one walk: each folder's names are decrypted once, not once per note
            for path, entry in self._tree.walk():
                rel = path.lstrip("/")
                if rel.split("/")[0] in HIDDEN or any(part.startswith(".") for part in rel.split("/")):
                    continue
                if entry.kind == "file" and rel in wanted:
                    texts[rel] = self._tree.read_file(entry).decode("utf-8", "replace")
                elif entry.kind == "file" and not rel.lower().endswith(".md"):
                    files.append(rel)
                elif entry.kind == "dir":
                    dirs.append(rel)
            file_by_path = {f.lower(): f for f in files}
            file_by_name: dict[str, str] = {}
            for f in files:
                file_by_name.setdefault(Path(f).name.lower(), f)
            by_path = {p[:-3].lower(): p for p in notes}
            by_name: dict[str, str] = {}
            for p in notes:
                by_name.setdefault(Path(p).stem.lower(), p)
            edges, missing, tags = set(), {}, {}
            for p in notes:
                text = texts.get(p, "")
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
                for m in re.finditer(r"\]\((?!https?:|mailto:)([^)\s]+)\)", text):   # [text](file.pdf), ![](photo.png)
                    name = m.group(1).replace("%20", " ").lstrip("./").lower()
                    target = file_by_path.get(name) or file_by_name.get(name.split("/")[-1])
                    if target:
                        edges.add((p, target))
                for m in re.finditer(r"!?\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", text):
                    raw = m.group(1).strip().lower()
                    name = raw.removesuffix(".md")
                    target = (by_path.get(name) or by_name.get(name.split("/")[-1])
                              or file_by_path.get(raw) or file_by_name.get(raw.split("/")[-1]))
                    if target and target != p:
                        edges.add((p, target))
                    elif not target and not re.search(r"\.\w{2,5}$", name):
                        missing.setdefault(p, []).append(m.group(1).strip())
            out = {"nodes": notes, "files": sorted(files), "folders": sorted(dirs), "edges": sorted(edges), "missing": missing,
                   "tags": sorted(tags.items(), key=lambda kv: (-kv[1], kv[0]))}
            self._links_cache = (self._gen, out)
            return out

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

    # ---------- AI tasks: notes the person gave to their AI, each with what to do ----------
    # Kept inside the lock like the settings, so it survives locking and waits for the AI.

    def todo(self) -> list[dict]:
        with self._lock:
            self._need_open()
            try:
                items = json.loads(self._tree.read_file(self._tree.resolve(TODO)))
                return items if isinstance(items, list) else []
            except (NotFound, ValueError):
                return []

    def _save_todo(self, items: list[dict]) -> list[dict]:
        items = items[-TODO_KEEP:]
        parent, name = self._make_parents(TODO)
        existing = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
        self._writer.write_file(parent, name, json.dumps(items, ensure_ascii=False).encode(), replace=existing)
        return items

    def todo_add(self, rel: str, ask: str) -> dict:
        """Give a note to the AI, with what to do (may be empty). Giving the same note again replaces its open item."""
        rel = _clean_path(rel)
        ask = str(ask or "").strip()[:TODO_ASK_MAX]
        with self._lock:
            self._need_open()
            self._tree.resolve(rel)   # must exist
            items = [i for i in self.todo() if not (i["path"] == rel and not i.get("done"))]
            item = {"id": "h-" + secrets.token_hex(4), "path": rel, "ask": ask, "t": time.time(), "done": False}
            self._save_todo(items + [item])
            return item

    def todo_set(self, tid: str, done: bool, by: str = "", result: str = "") -> dict:
        with self._lock:
            self._need_open()
            items = self.todo()
            item = next((i for i in items if i["id"] == tid), None)
            if not item:
                raise LookupError("That task isn't on the AI tasks list any more.")
            item.update(done=bool(done), done_t=time.time() if done else None,
                        by=str(by)[:60] if done else "", result=str(result).strip()[:TODO_ASK_MAX] if done else "")
            self._save_todo(items)
            if done and item.get("copy"):   # a merged clash: the other version goes to the trash, not lost
                try:
                    self.trash(item["copy"])
                except Exception:
                    pass   # already gone
            return item

    def todo_remove(self, tid: str) -> None:
        with self._lock:
            self._need_open()
            self._save_todo([i for i in self.todo() if i["id"] != tid])

    # ---------- folders private for AI: AI search shows them locked, AI opens them only when asked ----------

    def ai_private(self) -> list[str]:
        with self._lock:
            self._need_open()
            try:
                return [str(p) for p in json.loads(self._tree.read_file(self._tree.resolve(AI_PRIVATE)))]
            except (NotFound, ValueError):
                return []

    def is_ai_private(self, rel: str) -> bool:
        rel = str(rel).strip("/").lower()
        if any(p.startswith(".") for p in rel.split("/")):   # hidden files (.env keys and the like) are private always
            return True
        return any(rel == p.lower() or rel.startswith(p.lower() + "/") for p in self.ai_private())

    def set_ai_private(self, rel: str, on: bool) -> list[str]:
        rel = _clean_path(rel, md=False)
        with self._lock:
            self._need_open()
            self._tree.resolve(rel)   # a folder, note or file that exists
            return self._save_ai_private([p for p in self.ai_private() if p != rel] + ([rel] if on else []))

    def _save_ai_private(self, paths: list[str]) -> list[str]:
        paths = sorted(set(paths))
        parent, name = self._make_parents(AI_PRIVATE)
        existing = next((e for e in self._tree.list_dir(parent.dir_id) if e.name == name), None)
        self._writer.write_file(parent, name, json.dumps(paths, ensure_ascii=False).encode(), replace=existing)
        return paths

    def todo_moved(self, old: str, new: str) -> None:
        """A note or folder was renamed or moved: its to-do items follow it."""
        items = self.todo()
        changed = False
        for i in items:
            if i["path"] == old or i["path"].startswith(old + "/"):
                i["path"] = new + i["path"][len(old):]
                changed = True
        if changed:
            self._save_todo(items)

    def _reindex(self) -> None:
        for (path,) in self._con.execute("SELECT path FROM files").fetchall():
            remove_file(self._con, path)
        self._index_all()


TRASH = ".trash"
VERSIONS = ".versions"
PREFS = ".phygital/prefs.json"
TODO = ".phygital/ai-todo.json"
AI_PRIVATE = ".phygital/ai-private.json"
TRASH_INDEX = ".phygital/trash.json"
TRASH_DAYS = 90
TODO_KEEP = 100
TODO_ASK_MAX = 2000
HIDDEN = (TRASH, VERSIONS, ".phygital")
VERSION_EVERY = 5 * 60
VERSION_KEEP = 50
SYNC_EVERY = 5
MAX_FILE_BYTES = 25_000_000
MAX_IMPORT = 5000   # files in one import


def merge3(base: str, mine: str, theirs: str) -> str | None:
    """Put two edits of the same note together, line by line. None when they change the same lines, or both add
    lines at the same spot, so nothing is guessed: the caller keeps both versions apart instead."""
    from difflib import SequenceMatcher
    b, m, t = (x.splitlines(keepends=True) for x in (base, mine, theirs))

    def changes(x):
        return [(i1, i2, x[j1:j2]) for op, i1, i2, j1, j2 in SequenceMatcher(None, b, x, autojunk=False).get_opcodes()
                if op != "equal"]
    out, at, end, last = [], 0, -1, None
    for i1, i2, lines in sorted(changes(m) + changes(t), key=lambda c: (c[0], c[1])):
        if (i1, i2, lines) == last:
            continue   # the same change on both sides
        if i1 < end or (last and i1 == i2 == last[0] == last[1]):
            return None
        out += b[at:i1] + lines
        at, end, last = i2, i2, (i1, i2, lines)
    return "".join(out + b[at:])


def _clean_path(rel: str, md: bool = True) -> str:
    parts = [p for p in rel.replace("\\", "/").strip("/").split("/") if p]
    # Dot files (.env, .gitignore) are fine; the app's own hidden folders and Mac clutter are not.
    if not parts or any(p in (".", "..") or p in HIDDEN or p == ".DS_Store" or p.startswith("._") for p in parts):
        raise ValueError("Give a path inside the notes, like 'Projects/idea.md'.")
    if md and not parts[-1].lower().endswith(".md"):
        parts[-1] += ".md"
    if any(re.search(r'[<>:"|?*\x00-\x1f]', p) for p in parts):
        raise ValueError("That name has characters a note name can't use.")
    return "/".join(parts)
