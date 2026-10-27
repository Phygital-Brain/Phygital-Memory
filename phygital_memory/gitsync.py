"""Keep a locked folder in a private GitHub repo.

The folder stays where it is on this Mac and the app works on it as always (instant reads and edits). This keeps a
git repo in it in step with GitHub: a few seconds after a change it commits and pushes, and every so often it pulls
what other devices pushed. Only the scrambled files ever leave the Mac, like any cloud.

- Always private: the repo is made private, and before every push GitHub is asked again. If it ever turns public,
  syncing stops and the app says why.
- Two devices changed the same scrambled file: git can't merge those. Theirs stays in place and ours is kept next
  to it as "NAME (1).c9r", which the app already turns into a readable conflict copy (and an AI task).
- GitHub refuses files over 100 MB: those stay on this Mac only, and the app lists them.
- Signing in: for now the GitHub CLI (gh) on this Mac does it; nothing is stored by the app.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

PUSH_AFTER = 5      # seconds after a change before it goes up
PULL_EVERY = 30     # seconds between looks for other devices' changes
MAX_UP = 95 * 1024 * 1024
IGNORE = ".DS_Store\n._*\n.encryptor-*\n*.tmp\n"
# Every file is scrambled: git must never merge inside one (a small one can look like text to it and get spliced).
ATTRIBUTES = "* binary\n"
LOST = "phygital-lost-folders.json"   # in .git: folder IDs that lost a clash, for the app to fold back in
README = """# {name} · Phygital Memory

This repo holds an encrypted Phygital Memory folder. Everything in it is scrambled: note names and contents can
only be read with the folder's password, in the Phygital Memory app.

**Please don't delete or change these files.** The app keeps them in step by itself. Editing, moving or deleting a
file here by hand can break notes.

**Keep this repo private.** Even scrambled, a public repo shows how many files there are, their sizes and when they
change, and anyone could copy them and try to guess the password. The app checks before every upload and stops
syncing if the repo ever becomes public.

To open the notes on another Mac: in Phygital Memory, open the folder menu and choose "Open from GitHub…".
"""
EXTRA_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"   # an app from the Dock has a short PATH


def _env() -> dict:
    return {**os.environ, "PATH": os.environ.get("PATH", "") + ":" + EXTRA_PATH, "GIT_TERMINAL_PROMPT": "0"}


def gh() -> str | None:
    return shutil.which("gh", path=_env()["PATH"])


def _run(args, cwd=None, ok=(0,), timeout=120) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=_env(), timeout=timeout)
    if r.returncode not in ok:
        raise RuntimeError((r.stderr or r.stdout or "git failed").strip().splitlines()[-1][:300])
    return r


def signed_in() -> str | None:
    """The GitHub account the CLI is signed into, or None."""
    if not gh():
        return None
    r = subprocess.run([gh(), "api", "user", "--jq", ".login"], capture_output=True, text=True, env=_env(), timeout=30)
    return r.stdout.strip() or None if r.returncode == 0 else None


def is_private(repo: str) -> bool:
    r = subprocess.run([gh(), "api", f"repos/{repo}", "--jq", ".private"], capture_output=True, text=True,
                       env=_env(), timeout=30)
    return r.returncode == 0 and r.stdout.strip() == "true"


def repo_name(name: str) -> str:
    """"Notes - Phygital Memory" as GitHub allows it (no spaces): "Notes-Phygital-Memory"."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.") or "Notes"
    return f"{slug[:70]}-Phygital-Memory"


class GitSync:
    def __init__(self, folder: Path, repo: str, branch: str = "main", watch=None):
        """watch: returns a number that changes when a note changes here (Memory's gen), to send changes up soon."""
        self.folder, self.repo, self.branch, self.watch = Path(folder), repo, branch, watch
        self.state = {"repo": repo, "last": None, "error": "", "too_big": [], "stopped": False}
        self._wake = threading.Event()
        self._lock = threading.Lock()
        self._thread = None

    # ---------- git with GitHub's sign-in, nothing stored by us ----------
    def git(self, *args, ok=(0,), timeout=120):
        helper = f"!{gh()} auth git-credential" if gh() else ""
        return _run(["git", "-c", "credential.helper=", "-c", f"credential.helper={helper}",
                     "-c", "user.name=Phygital Memory", "-c", "user.email=sync@phygital.memory", *args],
                    cwd=self.folder, ok=ok, timeout=timeout)

    # ---------- the first time: a private repo, and everything (scrambled) up ----------
    def create(self) -> str:
        """Make the private repo on GitHub and push the folder. Returns 'owner/name'."""
        if (self.folder / ".git").exists():
            raise RuntimeError("This folder is already a git repo.")
        if gh() is None or signed_in() is None:
            raise RuntimeError("Sign in to GitHub first (GitHub CLI: gh auth login).")
        r = _run([gh(), "repo", "create", self.repo, "--private", "--disable-issues", "--disable-wiki",
                  "--description", "Phygital Memory: an encrypted notes folder (scrambled files only)."], timeout=60)
        url = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else f"https://github.com/{self.repo}"
        owner_repo = "/".join(url.rstrip("/").split("/")[-2:])
        self.repo = self.state["repo"] = owner_repo
        if not is_private(owner_repo):
            raise RuntimeError("GitHub didn't make the repo private, so nothing was sent.")
        self.prepare(self.folder.name)
        self.git("init", "-b", self.branch)
        self.git("remote", "add", "origin", f"https://github.com/{owner_repo}.git")
        self.sync_once()
        return owner_repo

    def prepare(self, name: str) -> None:
        """The plain files the repo needs next to the scrambled ones: what to leave out, binary only, a README."""
        (self.folder / ".gitignore").write_text(IGNORE)
        (self.folder / ".gitattributes").write_text(ATTRIBUTES)
        if not (self.folder / "README.md").exists():
            (self.folder / "README.md").write_text(README.format(name=name))

    @staticmethod
    def clone(repo: str, dest: Path, branch: str = "main") -> "GitSync":
        """Another Mac: bring the private repo down into dest (a new folder), then keep it in step."""
        if not is_private(repo):
            raise RuntimeError("That repo isn't private, so it isn't used.")
        helper = f"!{gh()} auth git-credential"
        _run(["git", "-c", "credential.helper=", "-c", f"credential.helper={helper}", "clone", "-q", "-b", branch,
              f"https://github.com/{repo}.git", str(dest)], timeout=600)
        return GitSync(dest, repo, branch)

    # ---------- keeping in step ----------
    def _skip_big(self) -> None:
        big = []
        for p in self.folder.rglob("*"):
            if ".git" in p.parts or not p.is_file():
                continue
            try:
                if p.stat().st_size > MAX_UP:
                    big.append(str(p.relative_to(self.folder)))
            except OSError:
                pass
        exclude = self.folder / ".git" / "info" / "exclude"
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text("# too big for GitHub: kept on this Mac only\n" + "\n".join("/" + b for b in big) + "\n")
        self.state["too_big"] = big

    def _commit(self) -> bool:
        self._skip_big()
        if not self.git("status", "--porcelain").stdout.strip():
            return False
        self.git("add", "-A")
        self.git("commit", "-q", "-m", f"Phygital Memory sync {time.strftime('%Y-%m-%d %H:%M')}")
        return True

    def _merge(self) -> None:
        """Bring in what other devices pushed. Same scrambled file changed on both sides: keep both."""
        r = self.git("merge", "--no-edit", f"origin/{self.branch}", ok=(0, 1))
        if r.returncode == 0:
            return
        clashed = [p for p in self.git("diff", "--name-only", "--diff-filter=U").stdout.splitlines() if p]
        lost = []
        for rel in clashed:
            path = self.folder / rel
            ours = subprocess.run(["git", "show", f":2:{rel}"], cwd=self.folder, capture_output=True, env=_env())
            theirs = subprocess.run(["git", "show", f":3:{rel}"], cwd=self.folder, capture_output=True, env=_env())
            if theirs.returncode == 0:
                path.write_bytes(theirs.stdout)
            if path.name == "dir.c9r":
                # Both Macs made the same folder, each with its own ID. Theirs is kept; the app moves what's in
                # ours over into it (it holds the key to do that), so nothing inside is lost.
                if ours.returncode == 0 and theirs.returncode == 0 and ours.stdout != theirs.stdout:
                    lost.append({"dir": str(Path(rel).parent), "id": ours.stdout.decode("ascii", "replace")})
                continue
            if ours.returncode == 0 and ours.stdout != theirs.stdout:
                n = 1
                while True:
                    copy = path.with_name(f"{path.stem} ({n}){path.suffix}")
                    if not copy.exists():
                        break
                    n += 1
                copy.write_bytes(ours.stdout)
        self.git("add", "-A")   # every clash is settled in the files above: mark them resolved
        if lost:
            store = self.folder / ".git" / LOST
            old = json.loads(store.read_text()) if store.exists() else []
            store.write_text(json.dumps(old + lost))
        self.git("commit", "-q", "--no-edit")

    def sync_once(self) -> None:
        with self._lock:
            self._commit()
            fetched = self.git("fetch", "-q", "origin", ok=(0, 128))
            remote_has = self.git("rev-parse", "--verify", "-q", f"origin/{self.branch}", ok=(0, 1)).returncode == 0
            if fetched.returncode == 0 and remote_has:
                self._merge()
            ahead = (not remote_has) or self.git("rev-list", "--count", f"origin/{self.branch}..HEAD").stdout.strip() != "0"
            if ahead:
                if not is_private(self.repo):   # asked again before every push
                    self.state.update(stopped=True, error="The GitHub repo isn't private, so syncing stopped. "
                                                          "Make it private again on GitHub.")
                    raise RuntimeError(self.state["error"])
                self.git("push", "-q", "-u", "origin", f"HEAD:{self.branch}")
            self.state.update(last=time.time(), error="")

    def poke(self) -> None:
        """Something changed here: send it up soon."""
        self._wake.set()

    def start(self) -> None:
        if self._thread:
            return

        def seen():
            try:
                return self.watch() if self.watch else None
            except Exception:
                return None

        def loop():
            last, waited = seen(), PULL_EVERY   # first look right away
            while not self.state["stopped"]:
                if waited < PULL_EVERY and not self._wake.is_set() and seen() == last:
                    self._wake.wait(PUSH_AFTER)
                    waited += PUSH_AFTER
                    continue
                if self._wake.is_set() or seen() != last:
                    time.sleep(PUSH_AFTER)   # let a burst of saves settle
                self._wake.clear()
                last, waited = seen(), 0
                try:
                    self.sync_once()
                except Exception as e:
                    self.state["error"] = str(e)[:300]
        self._thread = threading.Thread(target=loop, name=f"gitsync {self.repo}", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.state["stopped"] = True
        self._wake.set()

    def status(self) -> dict:
        return {**self.state, "ago": int(time.time() - self.state["last"]) if self.state["last"] else None}
