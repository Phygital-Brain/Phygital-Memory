# SPDX-License-Identifier: AGPL-3.0-only
"""An Open memory: the same folder tree as a vault (tree.py, writer.py), over a plain folder of readable files.

Memory works the same over either one. Here a folder's ID is its path inside the memory ("" for the top), and a
file's contents are the file itself. Anything starting with "." is left out, except the memory's own hidden
folders (trash, versions, prefs, AI tasks), so .git, .obsidian and the like stay untouched. Links are left out
too: a link could point anywhere on the Mac.
"""

from __future__ import annotations

import os
import shutil
import unicodedata
import uuid
from pathlib import Path

from .keys import VaultError
from .tree import Entry, NotFound, _safe_name
from .writer import Exists, _write_atomic

OWN = (".trash", ".versions", ".phygital", ".ai-tasks")   # the memory's own hidden folders (memory.HIDDEN, and the AI tasks)
TEMP = ".phygital"                           # big files arrive here first, then move into place


def _id(rel: str) -> bytes:
    return rel.encode("utf-8")


class PlainNames:
    """Names aren't encrypted here: nothing to decrypt (tree.conflicts is always empty, so this isn't reached)."""
    def decrypt(self, name: str, dir_id: bytes) -> str:
        raise VaultError("An Open memory has no encrypted names.")


class PlainTree:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.names = PlainNames()
        self.conflicts: list = []   # a cloud drive's clash copy here is just another readable file

    def dir_location(self, dir_id: bytes) -> Path:
        return self.root / dir_id.decode("utf-8") if dir_id else self.root

    def list_dir(self, dir_id: bytes = b"") -> list[Entry]:
        location = self.dir_location(dir_id)
        if not location.is_dir():
            raise NotFound("That folder isn't there any more.")
        rel = dir_id.decode("utf-8")
        out = []
        for p in location.iterdir():
            name = unicodedata.normalize("NFC", p.name)
            if not _safe_name(name) or (name.startswith(".") and name not in OWN):   # the app's own at any depth:
                continue   # their versions and trashed copies sit inside one another
            if p.is_symlink():
                out.append(Entry(name, "link", p, None, dir_id))
            elif p.is_dir():
                out.append(Entry(name, "dir", p, _id(f"{rel}/{name}" if rel else name), dir_id))
            elif p.is_file():
                out.append(Entry(name, "file", p, None, dir_id))
        return sorted(out, key=lambda e: e.name)

    def resolve(self, clear_path: str) -> Entry:
        parts = [unicodedata.normalize("NFC", p) for p in clear_path.strip("/").split("/") if p]
        entry = Entry("", "dir", self.root, b"")
        for i, part in enumerate(parts):
            if part in (".", ".."):
                raise VaultError("Paths can't contain '.' or '..'.")
            if entry.kind != "dir":
                raise NotFound(f"'{'/'.join(parts[:i])}' isn't a folder.")
            match = next((e for e in self.list_dir(entry.dir_id) if e.name == part), None)
            if match is None:
                raise NotFound(f"No '{'/'.join(parts[:i + 1])}' in this memory.")
            entry = match
        return entry

    def read_file(self, entry: Entry) -> bytes:
        if entry.kind != "file":
            raise VaultError(f"'{entry.name}' isn't a file.")
        return entry.stored.read_bytes()

    def read_file_to(self, entry: Entry, dst) -> None:
        if entry.kind != "file":
            raise VaultError(f"'{entry.name}' isn't a file.")
        with open(entry.stored, "rb") as src:
            while chunk := src.read(1 << 20):
                dst.write(chunk)

    @staticmethod
    def contents_path(entry: Entry) -> Path:
        return entry.stored

    def file_size(self, entry: Entry) -> int:
        return entry.stored.stat().st_size

    def walk(self, dir_id: bytes = b"", prefix: str = ""):
        for entry in self.list_dir(dir_id):
            path = f"{prefix}/{entry.name}"
            yield path, entry
            if entry.kind == "dir":
                yield from self.walk(entry.dir_id, path)


class PlainWriter:
    def __init__(self, tree: PlainTree):
        self.tree = tree

    def _free(self, parent: Entry, name: str) -> Path:
        if parent.kind != "dir":
            raise VaultError(f"'{parent.name}' isn't a folder.")
        if not _safe_name(name):
            raise VaultError("That name can't be used.")
        if any(e.name == name for e in self.tree.list_dir(parent.dir_id)) or (parent.stored / name).exists():
            raise Exists(f"'{name}' already exists there.")
        return parent.stored / name

    def _entry(self, parent: Entry, name: str, kind: str, stored: Path) -> Entry:
        rel = parent.dir_id.decode("utf-8")
        dir_id = _id(f"{rel}/{name}" if rel else name) if kind == "dir" else None
        return Entry(name, kind, stored, dir_id, parent.dir_id)

    def write_file(self, parent: Entry | None, name: str, data: bytes, replace: Entry | None = None) -> Entry:
        if replace is not None:
            if replace.kind != "file":
                raise VaultError(f"'{replace.name}' isn't a file.")
            _write_atomic(replace.stored, data)
            return replace
        stored = self._free(parent, name)
        _write_atomic(stored, data)
        return self._entry(parent, name, "file", stored)

    def write_file_from(self, parent: Entry, name: str, src) -> Entry:
        stored = self._free(parent, name)

        def fill(f):
            if hasattr(src, "read"):
                while chunk := src.read(1 << 20):
                    f.write(chunk)
                return
            with open(src, "rb") as s:
                shutil.copyfileobj(s, f, 1 << 20)
        _write_atomic(stored, fill)
        return self._entry(parent, name, "file", stored)

    def encrypt_to_temp(self, src) -> Path:
        """(Nothing to encrypt.) Copy a stream into a temporary file in the memory's hidden folder."""
        folder = self.tree.root / TEMP
        folder.mkdir(exist_ok=True)
        tmp = folder / f"incoming-{uuid.uuid4().hex}.tmp"
        try:
            with open(tmp, "xb") as f:
                while chunk := src.read(1 << 20):
                    f.write(chunk)
                f.flush()
                os.fsync(f.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        return tmp

    def place_temp(self, parent: Entry, name: str, tmp: Path) -> Entry:
        stored = self._free(parent, name)
        os.replace(tmp, stored)
        return self._entry(parent, name, "file", stored)

    def copy_file(self, entry: Entry, parent: Entry, name: str) -> Entry:
        if entry.kind != "file":
            raise VaultError(f"'{entry.name}' isn't a file. Only files can be copied.")
        stored = self._free(parent, name)
        shutil.copy2(entry.stored, stored)
        return self._entry(parent, name, "file", stored)

    def make_dir(self, parent: Entry, name: str) -> Entry:
        stored = self._free(parent, name)
        stored.mkdir()
        return self._entry(parent, name, "dir", stored)

    def move(self, entry: Entry, parent: Entry, name: str) -> Entry:
        if entry.parent_id is None:
            raise VaultError("The top folder can't be moved.")
        if entry.kind == "dir" and (parent.dir_id == entry.dir_id or parent.dir_id.startswith(entry.dir_id + b"/")):
            raise VaultError("A folder can't be moved into itself.")
        stored = self._free(parent, name)
        os.rename(entry.stored, stored)
        return self._entry(parent, name, entry.kind, stored)

    def put_ciphertext(self, entry: Entry, data: bytes) -> None:
        if entry.kind != "file":
            raise VaultError(f"'{entry.name}' isn't a file.")
        _write_atomic(entry.stored, data)

    def remove_tree(self, entry: Entry) -> None:
        if entry.parent_id is None:
            raise VaultError("The top folder can't be removed.")
        if entry.kind == "dir":
            shutil.rmtree(entry.stored)
        else:
            entry.stored.unlink()

    def remove(self, entry: Entry) -> None:
        if entry.parent_id is None:
            raise VaultError("The top folder can't be removed.")
        if entry.kind == "dir":
            if self.tree.list_dir(entry.dir_id):
                raise VaultError(f"The folder '{entry.name}' isn't empty.")
            if any(p.name not in (".DS_Store",) and not p.name.startswith("._") for p in entry.stored.iterdir()):
                raise VaultError(f"The folder '{entry.name}' has hidden files in it, so it stays.")
            shutil.rmtree(entry.stored)   # only Finder's own files are left in it
        else:
            entry.stored.unlink()
