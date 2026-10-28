"""Keep a memory in a private GitHub repo: an Encrypted one's scrambled files, or an Open one's readable files.

The folder stays where it is on this Mac and the app works on it as always (instant reads and edits). This keeps a
git repo in it in step with GitHub: a few seconds after a change it commits and pushes, and every so often it pulls
what other devices pushed. Only the scrambled files ever leave the Mac, like any cloud.

- Always private: the repo is made private, and before every push GitHub is asked again. If it ever turns public,
  syncing stops and the app says why.
- Two devices changed the same scrambled file: git can't merge those. Theirs stays in place and ours is kept next
  to it as "NAME (1).c9r", which the app already turns into a readable conflict copy (and an AI task).
- GitHub refuses files over 100 MB: those stay on this Mac only, and the app lists them.
- Signing in: the app's own "Sign in with GitHub" (github_auth.py, key in the Keychain). Without it, the GitHub CLI
  (gh) on this Mac is used if it's signed in.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

from . import github_auth

PUSH_AFTER = 5      # seconds after a change before it goes up
PULL_EVERY = 30     # seconds between looks for other devices' changes
MAX_UP = 95 * 1024 * 1024
IGNORE = ".DS_Store\n._*\n.encryptor-*\n*.tmp\n"
# Every file is scrambled: git must never merge inside one (a small one can look like text to it and get spliced).
ATTRIBUTES = "* binary\n"
LOST = "phygital-lost-folders.json"   # in .git: folder IDs that lost a clash, for the app to fold back in
README_MARK = "<!-- phygital-memory-readme 8 -->"   # the app updates its own README when this goes up
README = README_MARK + """
<p><img src="phygital-memory-mark.svg" width="56" alt="Phygital Memory"></p>

# {name}

This private repo is the GitHub backup of **{name}**, a memory in Phygital Memory. Your Mac encrypts every note
before it comes here. Only the memory's password or its recovery key can open it.

> [!IMPORTANT]
> Keep this repo private. The app checks before every upload and stops the backup if the repo becomes public.

## How it's saved

- A few seconds after you change a note, the app encrypts the change and uploads it here.
- Every 30 seconds it checks for changes from your other Macs and brings them down.
- Each upload is a new commit, so GitHub keeps every past state of the encrypted files.
- Earlier versions of each note are inside the memory too. In the app, open the note and press Version history.
- Files over 95 MB stay on your Mac, because GitHub doesn't take files that big. The app lists them.

## Use the backup

**On a new Mac, or after losing this one**

1. Install Phygital Memory.
2. Click the memory name at the top of the sidebar, then **Add memory › From GitHub**.
3. Sign in to GitHub if the app asks, type `{repo}` and choose where to keep it.
4. Unlock it with the password. If you forget it, use the recovery key on the lock screen.

To check or stop the backup, open **Storage and backup › Backup** in the app. It shows when the last upload
happened and any problem. **Stop backup** keeps your notes on your Mac and sends nothing more here. The app never
deletes this repo.

## What's in the repo

| What | What it is |
|---|---|
| `d/` | Your notes, files and folders, encrypted. Names and contents can't be read without the password. |
| `masterkey.cryptomator` | The memory's key, locked with your password. |
| `vault.cryptomator` | Settings for the encryption. |
| `AGENTS.md`, `CLAUDE.md` | Short notes for AI apps: use Phygital Memory, don't open these files directly. |
| `Open in Phygital Memory.phygitalmemory` | Double-click it on a Mac to open the memory in the app. |
| `.github/`, `.gitignore`, `.gitattributes` | This page, its logo, and two small files that tell git how to treat encrypted files. Finder hides them. |

## What GitHub can see

GitHub can't read your note names or what you wrote. It can see how many files there are, their sizes, how the
folders nest and when things change.

> [!WARNING]
> Don't edit, move, rename or delete files here by hand. A change made outside the app can break notes.

## If something goes wrong

- **The same note changed on two Macs:** both versions are kept. The second shows next to the note as
  "name (conflict date)", and your AI apps get a task to merge them.
- **The backup stopped:** open Storage and backup in the app. It says why.
- **You want this repo gone:** first make sure your Mac still has the memory. Then on GitHub, open Settings and
  press Delete this repository.

> [!CAUTION]
> If both the password and the recovery key are lost, nobody can open these notes. There is no reset. Keep both in
> a safe place, like a password manager.
"""
# An Open memory's repo holds the notes as they are: readable on GitHub, and by AI apps that can reach GitHub.
README_PLAIN = README_MARK + """
<p><img src="phygital-memory-mark.svg" width="56" alt="Phygital Memory"></p>

# {name}

This private repo is the GitHub backup of **{name}**, an Open memory in Phygital Memory. The notes here are plain
files, the same as on the Mac: you can read them on GitHub, and so can AI apps you connect to GitHub.

> [!IMPORTANT]
> Keep this repo private. The app checks before every upload and stops the backup if the repo becomes public.

## How it's saved

- A few seconds after you change a note, the app uploads the change here.
- Every 30 seconds it checks for changes from your other devices and brings them down.
- Each upload is a new commit, so GitHub keeps every past state of every note.
- Files over 95 MB stay on your Mac, because GitHub doesn't take files that big. The app lists them.

## Use the backup

On a new Mac: install Phygital Memory, click the memory name at the top of the sidebar, then **Add memory › From
GitHub**, and type `{repo}`.

To check or stop the backup, open **Storage and backup › Backup** in the app. **Stop backup** keeps your notes on
your Mac and sends nothing more here. The app never deletes this repo.

## If something goes wrong

- **The same note changed in two places:** both versions are kept. The second shows next to the note as
  "name (1)".
- **You want this repo gone:** first make sure your Mac still has the memory. Then on GitHub, open Settings and
  press Delete this repository.
"""
IGNORE_PLAIN = IGNORE + ".versions/\n.trash/\n.phygital/\n"   # git keeps the history; the app's own folders stay home
# The Knot (brand/phygital-memory-mark.svg), shown at the top of the README.
LOGO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64"><circle cx="32" cy="32" r="30" '
        'fill="#C8F031"/><path d="M12 42 H19 C24 42 25 36 25 30 C25 18 43 16 45 28 C46 38 33 42 29 35 C26 29 32 23 39 26 '
        'C45 29 46 36 46 42 H52" fill="none" stroke="#0B0D12" stroke-width="3" stroke-linecap="round" '
        'stroke-linejoin="round"/><circle cx="12" cy="42" r="3.2" fill="#4D5BFF"/><circle cx="52" cy="42" r="3.2" '
        'fill="#4D5BFF"/></svg>\n')
EXTRA_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"   # an app from the Dock has a short PATH


def _env() -> dict:
    env = {**os.environ, "PATH": os.environ.get("PATH", "") + ":" + EXTRA_PATH, "GIT_TERMINAL_PROMPT": "0"}
    if _own():   # the GitHub key, only for git's own run (git's credential helper below reads it from here)
        env["PM_GITHUB_KEY"] = github_auth.saved_token() or ""
    return env


def gh() -> str | None:
    if os.environ.get("PHYGITAL_MEMORY_OFFLINE"):   # tests: never use the person's real GitHub sign-in
        return None
    return shutil.which("gh", path=_env()["PATH"])


def _run(args, cwd=None, ok=(0,), timeout=120) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=_env(), timeout=timeout)
    if r.returncode not in ok:
        raise RuntimeError((r.stderr or r.stdout or "git failed").strip().splitlines()[-1][:300])
    return r


def _own() -> bool:
    """Signed in with the app's own Sign in with GitHub (its key is in the Keychain)."""
    return bool(github_auth.saved_token())


def credential_helper() -> str:
    """How git gets GitHub's password for a push or pull, without it ever being written down or passed around."""
    if _own():
        return ("!f() { test \"$1\" = get || exit 0; echo username=x-access-token; "
                "echo \"password=$PM_GITHUB_KEY\"; }; f")
    return f"!{gh()} auth git-credential" if gh() else ""


def signed_in() -> str | None:
    """The GitHub account the app is signed into (or else the GitHub CLI's), or None. This asks GitHub."""
    if _own():
        return github_auth.account()
    if not gh():
        return None
    r = subprocess.run([gh(), "api", "user", "--jq", ".login"], capture_output=True, text=True, env=_env(), timeout=30)
    return r.stdout.strip() or None if r.returncode == 0 else None


def is_private(repo: str) -> bool:
    if _own():
        code, info = github_auth.api(f"/repos/{repo}")
        return code == 200 and info.get("private") is True
    r = subprocess.run([gh(), "api", f"repos/{repo}", "--jq", ".private"], capture_output=True, text=True,
                       env=_env(), timeout=30)
    return r.returncode == 0 and r.stdout.strip() == "true"


SUFFIX = "-Phygital-Memory"


class SameMemoryRepo(RuntimeError):
    """The repo name is taken by this same memory's repo, from an earlier connection."""
    def __init__(self, repo: str):
        super().__init__(f"This memory already has a repo on GitHub: {repo}.")
        self.repo = repo


def _exists(repo: str) -> bool:
    if _own():
        return github_auth.api(f"/repos/{repo}")[0] == 200
    return subprocess.run([gh(), "api", f"repos/{repo}"], capture_output=True, env=_env(), timeout=30).returncode == 0


def repo_name(name: str) -> str:
    """"Notes - Phygital Memory" as GitHub allows it (no spaces): "Notes-Phygital-Memory". A memory already called
    "Phygital Memory" (or "NAME Phygital Memory") isn't doubled: "Phygital-Memory"."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.") or "Notes"
    if slug.lower() == "phygital-memory" or slug.lower().endswith(SUFFIX.lower()):
        return slug[:90]
    return f"{slug[:70]}{SUFFIX}"


def memory_repos() -> list[dict]:
    """The signed-in account's private repos made for Phygital Memory (name ending in -Phygital-Memory, or
    Phygital-Memory itself), newest first. This asks GitHub."""
    repos, page = [], 1
    while page <= 10:
        if _own():
            code, batch = github_auth.api(f"/user/repos?per_page=100&page={page}&affiliation=owner&sort=pushed")
            if code != 200:
                raise RuntimeError("GitHub didn't send the list of repos.")
        else:
            r = _run([gh(), "api", f"user/repos?per_page=100&page={page}&affiliation=owner&sort=pushed"], timeout=60)
            batch = json.loads(r.stdout or "[]")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    mine = [r for r in repos if r.get("private") and (r["name"].lower() == "phygital-memory"
                                                     or r["name"].lower().endswith(SUFFIX.lower()))]
    return [{"repo": r["full_name"], "name": r["name"], "pushed": r.get("pushed_at")} for r in mine]


def rename_repo(repo: str, new_name: str) -> str:
    """Rename a repo on GitHub (it forwards the old address). Returns the new 'owner/name'."""
    if _own():
        code, info = github_auth.api(f"/repos/{repo}", method="PATCH", body={"name": new_name})
        if code != 200:
            raise RuntimeError(info.get("message") or "GitHub didn't rename the repo.")
        return info["full_name"]
    r = _run([gh(), "api", "-X", "PATCH", f"repos/{repo}", "-f", f"name={new_name}", "--jq", ".full_name"], timeout=60)
    return r.stdout.strip()


class GitSync:
    def __init__(self, folder: Path, repo: str, branch: str = "main", watch=None, git_dir: Path | None = None,
                 plain: bool = False):
        """watch: returns a number that changes when a note changes here (Memory's gen), to send changes up soon.
        git_dir: where git keeps its own files. Outside the memory folder, so a cloud app syncing that folder (or a
        cloud-only memory's drive) never sees them. None: the older way, a .git inside the folder."""
        self.folder, self.repo, self.branch, self.watch = Path(folder), repo, branch, watch
        self.plain = plain   # an Open memory: readable files, its own README
        self.gitdir = Path(git_dir) if git_dir else self.folder / ".git"
        self._outside = git_dir is not None
        self.state = {"repo": repo, "last": None, "error": "", "too_big": [], "stopped": False}
        self._wake = threading.Event()
        self._lock = threading.Lock()
        self._thread = None

    # ---------- git with GitHub's sign-in, nothing stored by us ----------
    def _where(self) -> list[str]:
        return ["--git-dir", str(self.gitdir), "--work-tree", str(self.folder)] if self._outside else []

    def git(self, *args, ok=(0,), timeout=120):
        return _run(["git", *self._where(), "-c", "credential.helper=", "-c", f"credential.helper={credential_helper()}",
                     "-c", "user.name=Phygital Memory", "-c", "user.email=sync@phygital.memory", *args],
                    cwd=self.folder, ok=ok, timeout=timeout)

    # ---------- the first time: a private repo, and everything (scrambled) up ----------
    def create(self, reuse: str | None = None) -> str:
        """Make the private repo on GitHub and push the folder. Returns 'owner/name'.

        If the name is taken by this same memory's repo (connected before, then stopped), SameMemoryRepo is raised so
        the person can choose to use it again: then call create(reuse='owner/name'). A name taken by anything else
        gets "-2", "-3"."""
        if (self.gitdir / "HEAD").exists() or (self.folder / ".git").exists():
            raise RuntimeError("This folder is already a git repo.")
        me = signed_in()
        if me is None:
            raise RuntimeError("Sign in with GitHub first.")
        if reuse:
            if not is_private(reuse) or not self.same_memory(reuse):
                raise RuntimeError("That repo isn't this memory's, or isn't private, so it isn't used.")
            owner_repo = reuse
        else:
            base, n = self.repo, 1
            while _exists(f"{me}/{self.repo}"):
                if self.same_memory(f"{me}/{self.repo}"):
                    raise SameMemoryRepo(f"{me}/{self.repo}")
                n += 1
                self.repo = f"{base}-{n}"
            owner_repo = self._make_repo()
        self.repo = self.state["repo"] = owner_repo
        if not is_private(owner_repo):
            raise RuntimeError("GitHub didn't make the repo private, so nothing was sent.")
        self.prepare(self.folder.name)
        if self._outside:
            self.gitdir.parent.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q", "-b", self.branch)
        self.git("remote", "add", "origin", f"https://github.com/{owner_repo}.git")
        if reuse:
            self._start_from_where_we_left()
        self.sync_once()   # with a reused repo, this merges both sides and keeps both versions where they differ
        return owner_repo

    def _start_from_where_we_left(self) -> None:
        """Using a repo again after a stop: the history here was put away, so find the commit on GitHub that
        matches this Mac's files best (where the two sides went apart) and build on it. Then a note changed only
        here, or only on GitHub, just moves across; only one changed on both sides keeps two versions."""
        self.git("fetch", "-q", "origin")
        local = {}
        for p in self.folder.rglob("*"):
            rel = p.relative_to(self.folder).as_posix()
            if p.is_file() and not rel.startswith(".git/") and p.stat().st_size <= MAX_UP:
                local[rel] = None
        if not local:
            return
        hashes = self.git("hash-object", "--", *local.keys()).stdout.split()
        local = dict(zip(local.keys(), hashes))
        best, best_score = None, -1
        for sha in self.git("rev-list", "--max-count=60", f"origin/{self.branch}").stdout.split():
            tree = {}
            for line in self.git("ls-tree", "-r", sha).stdout.splitlines():
                meta, _, path = line.partition("\t")
                tree[path] = meta.split()[2]
            same = sum(1 for path, h in local.items() if tree.get(path) == h)
            score = same - (len(tree) - same)   # files there that this Mac doesn't have, or has different, count against
            if score > best_score:   # newest first, so a tie keeps the newer commit
                best, best_score = sha, score
        if best:
            self.git("update-ref", f"refs/heads/{self.branch}", best)
            self.git("read-tree", best)   # this Mac's changes since then get committed on top of it

    def _make_repo(self) -> str:
        about = "Phygital Memory: an Open notes folder." if self.plain else "Phygital Memory: an encrypted notes folder."
        if _own():
            code, made = github_auth.api("/user/repos", method="POST", body={
                "name": self.repo, "private": True, "has_issues": False, "has_wiki": False, "has_projects": False,
                "description": about})
            if code != 201:
                raise RuntimeError(made.get("message") or "GitHub didn't make the repo.")
            return made["full_name"]
        r = _run([gh(), "repo", "create", self.repo, "--private", "--disable-issues", "--disable-wiki",
                  "--description", about], timeout=60)
        url = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else f"https://github.com/{self.repo}"
        return "/".join(url.rstrip("/").split("/")[-2:])

    def same_memory(self, repo: str) -> bool:
        """Is that repo a copy of this very memory? Its vault.cryptomator (the memory's own ID, not secret) matches.
        An Open memory has no ID like that, so a taken name just gets "-2"."""
        if self.plain:
            return False
        path = f"/repos/{repo}/contents/vault.cryptomator?ref={self.branch}"
        if _own():
            code, info = github_auth.api(path)
            content = info.get("content", "") if code == 200 else ""
        else:
            r = subprocess.run([gh(), "api", path.lstrip("/"), "--jq", ".content"], capture_output=True, text=True,
                               env=_env(), timeout=30)
            content = r.stdout if r.returncode == 0 else ""
        try:
            return bool(content) and base64.b64decode(content) == (self.folder / "vault.cryptomator").read_bytes()
        except (ValueError, OSError):
            return False

    def prepare(self, name: str) -> None:
        """The plain files the repo needs next to the scrambled ones: what to leave out, binary only, a README."""
        (self.folder / ".gitignore").write_text(IGNORE_PLAIN if self.plain else IGNORE)
        (self.folder / ".gitattributes").write_text(ATTRIBUTES)
        self.update_readme(name)

    def renamed(self, name: str, new_repo: str) -> None:
        """The memory and its repo got a new name: point git at the new address and retitle the README."""
        with self._lock:
            self.repo = self.state["repo"] = new_repo
            self.git("remote", "set-url", "origin", f"https://github.com/{new_repo}.git")
            self.update_readme(name, force=True)
        self.poke()

    def update_readme(self, name: str, force: bool = False) -> None:
        """Write the README in the hidden .github folder: GitHub shows it on the repo's page, Finder doesn't show it in
        the folder. The app's own older README (at the top of the folder, or an older text) is replaced; a README
        someone wrote is left alone."""
        ours = lambda t: t.startswith("<!-- phygital-memory-readme") or (t.startswith("# ") and "Phygital Memory" in t[:200])
        top = self.folder / "README.md"
        if top.exists() and ours(top.read_text(errors="replace")):
            top.unlink()   # moved into .github (the next sync sends the move up)
        p = self.folder / ".github" / "README.md"
        old = p.read_text(errors="replace") if p.exists() else None
        if old is None or (ours(old) and (force or not old.startswith(README_MARK))):
            p.parent.mkdir(exist_ok=True)
            p.write_text((README_PLAIN if self.plain else README).format(name=name, repo=self.repo))
            (p.parent / "phygital-memory-mark.svg").write_text(LOGO)

    @staticmethod
    def clone(repo: str, dest: Path, branch: str = "main", git_dir: Path | None = None) -> "GitSync":
        """Another Mac: bring the private repo down into dest (a new folder), then keep it in step."""
        if not is_private(repo):
            raise RuntimeError("That repo isn't private, so it isn't used.")
        if git_dir is None:
            _run(["git", "-c", "credential.helper=", "-c", f"credential.helper={credential_helper()}", "clone", "-q", "-b", branch,
                  f"https://github.com/{repo}.git", str(dest)], timeout=600)
            return GitSync(dest, repo, branch)
        dest.mkdir(parents=True, exist_ok=True)
        Path(git_dir).parent.mkdir(parents=True, exist_ok=True)
        g = GitSync(dest, repo, branch, git_dir=git_dir)
        g.git("init", "-q", "-b", branch)
        g.git("remote", "add", "origin", f"https://github.com/{repo}.git")
        g.git("fetch", "-q", "origin", timeout=600)
        g.git("checkout", "-q", "-f", "-B", branch, f"origin/{branch}")
        return g

    # ---------- keeping in step ----------
    def _skip_big(self) -> None:
        big = []
        for p in self.folder.rglob("*"):
            if ".git" in p.relative_to(self.folder).parts or not p.is_file():
                continue
            try:
                if p.stat().st_size > MAX_UP:
                    big.append(str(p.relative_to(self.folder)))
            except OSError:
                pass
        exclude = self.gitdir / "info" / "exclude"
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
        r = self.git("merge", "--no-edit", "--allow-unrelated-histories", f"origin/{self.branch}", ok=(0, 1))
        if r.returncode == 0:
            return
        clashed = [p for p in self.git("diff", "--name-only", "--diff-filter=U").stdout.splitlines() if p]
        lost = []
        for rel in clashed:
            path = self.folder / rel
            ours = subprocess.run(["git", *self._where(), "show", f":2:{rel}"], cwd=self.folder, capture_output=True, env=_env())
            theirs = subprocess.run(["git", *self._where(), "show", f":3:{rel}"], cwd=self.folder, capture_output=True, env=_env())
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
            store = self.gitdir / LOST
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
        """Stop syncing, and wait for a sync that is halfway through to finish (so nothing writes here after)."""
        self.state["stopped"] = True
        self._wake.set()
        with self._lock:
            pass
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=30)

    def status(self) -> dict:
        return {**self.state, "ago": int(time.time() - self.state["last"]) if self.state["last"] else None}
