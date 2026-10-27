"""Show the unlocked notes as a normal folder in Finder (the person's own choice, from the app).

The WebDAV mount itself is finder_mount.py (from Encryptor MCP). This file adapts it to Memory: every change
made in Finder goes through Memory, so a saved note keeps its old version and stays searchable, and a deleted
file goes to the trash inside the lock. The volume is removed when the notes lock.

While it is shown, any program of this Mac user can read the files through Finder, AI tools with a shell
included. The app says so; that's why it is only ever opened by hand and closes itself on lock.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from . import finder_mount
from .memory import Memory
from .vault.keys import VaultError

BASE = Path(os.environ.get("PHYGITAL_MEMORY_MOUNTS", "~/Library/Application Support/Phygital Memory/Finder")).expanduser()
DESKTOP = Path(os.environ.get("PHYGITAL_MEMORY_DESKTOP", "~/Desktop")).expanduser()   # where the shortcut goes
NAME = "Phygital Memory"


class _Vault:
    def __init__(self, name):
        self.name = name


class _Session:
    """What finder_mount expects of an open vault."""
    def __init__(self, memory: Memory, name: str = NAME):
        self.memory, self.vault, self.read_only = memory, _Vault(name), False
        self.status_code = secrets.token_hex(8)

    @property
    def tree(self):
        return self.memory._tree


class _Manager:
    def __init__(self, memory: Memory, session: _Session):
        self.memory, self.session, self.on_lock = memory, session, []

    def by_status_code(self, code):
        return self.session if self.memory.is_open and code == self.session.status_code else None

    def use(self, _name):
        self.memory._touch()

    def _event(self, *_):
        pass


class _Journal:
    """The change log finder_mount writes through, done with Memory's own methods."""
    def __init__(self, memory: Memory):
        self.m = memory

    @staticmethod
    def _p(path: str) -> str:
        return path.strip("/")

    def _wrap(self, fn, *args):
        try:
            return fn(*args)
        except (ValueError, LookupError, OSError) as e:
            raise VaultError(str(e)) from None

    def write(self, path, data, _etag, *_):
        self._wrap(self.m.write_bytes, self._p(path), data)
        return {"action": "saved", "path": path}

    def mkdir(self, path, *_):
        self._wrap(self.m.make_folder, self._p(path))
        return {"action": "made folder", "path": path}

    def move(self, src, dest, *_):
        self._wrap(self.m.move, self._p(src), self._p(dest))
        return {"action": "moved", "path": dest}

    def move_over(self, src, dest, *_):
        self._wrap(self.m.trash, self._p(dest))
        return self.move(src, dest)

    def trash(self, path, *_):
        self._wrap(self.m.trash, self._p(path))
        return {"action": "trashed", "path": path}

    def copy(self, src, dest, *_):
        self._wrap(self.m.write_bytes, self._p(dest), self.m.read_bytes(self._p(src)))
        return {"action": "copied", "path": dest}

    @staticmethod
    def etag(_entry):
        return ""


class Finder:
    def __init__(self, memory: Memory, volume: str = NAME):
        self.memory, self.volume = memory, volume
        self.session = None
        self.mounts = None
        self.link = None   # the Desktop shortcut while shown
        memory.on_lock.append(self.hide)

    def available(self) -> bool:
        return finder_mount.Mounts.available(self)   # macOS with mount_webdav

    def where(self) -> str:
        return self.mounts.where(self.session.vault.name) if self.mounts else ""   # the name it was mounted under

    def show(self, open_window: bool = True) -> str:
        """Mount the Finder view and put its icon on the Desktop. open_window=False: just the icon, no window."""
        if not self.memory.is_open:
            raise ValueError("Unlock first.")
        if self.mounts is None:
            self.session = _Session(self.memory, self.volume)
            manager = _Manager(self.memory, self.session)
            journal = _Journal(self.memory)
            BASE.mkdir(parents=True, exist_ok=True)
            self.mounts = finder_mount.Mounts(manager, lambda _s: journal, BASE)
        where = self.mounts.mount(self.session, open_window)
        self.link = _add_desktop_link(self.volume, where)
        return where

    def renamed(self, name: str) -> None:
        """The memory got a new name: so does its Desktop icon."""
        self.volume = name
        if self.link is not None and self.mounts is not None:
            _remove_desktop_link(self.link)
            self.link = _add_desktop_link(name, self.where())

    def hide(self) -> None:
        _remove_desktop_link(self.link)
        self.link = None
        if self.mounts is not None:
            mounts, self.mounts, self.session = self.mounts, None, None
            mounts.unmount_all()


# ---------- a shortcut on the Desktop while the folder is open in Finder ----------
# Only ever our own shortcut: a link into the Finder view's place. Something else with that name is never touched.

def _plain(path) -> Path:
    """One spelling of a path: the system's own (macOS may report /System/Volumes/Data/Users/...)."""
    return Path(os.path.realpath(str(path)).removeprefix("/System/Volumes/Data"))


def _ours(link: Path) -> bool:
    try:
        return link.is_symlink() and _plain(os.readlink(link)).is_relative_to(_plain(BASE))
    except (OSError, ValueError):
        return False


def _add_desktop_link(name: str, where: str) -> Path | None:
    if not where or not DESKTOP.is_dir():
        return None
    for label in (name, f"{name} (Phygital Memory)"):
        link = DESKTOP / label.replace("/", "-")
        if _ours(link):
            link.unlink()
        if not os.path.lexists(link):
            try:
                link.symlink_to(where)
                return link
            except OSError:
                return None
    return None


def _remove_desktop_link(link: Path | None) -> None:
    if link is not None and _ours(link):
        link.unlink(missing_ok=True)


def clear_desktop_links() -> None:
    """At start: remove shortcuts left from a run that ended without locking (a crash, a forced quit)."""
    try:
        for link in DESKTOP.iterdir():
            if _ours(link):
                link.unlink(missing_ok=True)
    except OSError:
        pass
