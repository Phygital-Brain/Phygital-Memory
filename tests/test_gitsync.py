"""Private GitHub sync, for real: two Macs (two folders) on one private repo.

Uses the GitHub CLI's account and a test repo (default phygital-memory-sync-test), with a fresh branch per run so
runs don't mix. Only scrambled test notes go up.
Run: uv run python test_gitsync.py
"""
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from unittest import mock

from phygital_memory import gitsync
from phygital_memory.gitsync import GitSync
from phygital_memory.memory import Memory

PW = "test-gitsync-pass"
REPO = os.environ.get("PM_TEST_REPO", "phygital-memory-sync-test")
BRANCH = "test-" + time.strftime("%Y%m%d-%H%M%S")
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


me = gitsync.signed_in()
check(me, "signed in to GitHub", me)
tmp = Path(tempfile.mkdtemp(prefix="pm-git-"))
try:
    a_dir = tmp / "mac-a" / "Notes"
    a_dir.parent.mkdir()
    Memory.create(a_dir, PW)
    a = Memory(a_dir)
    a.unlock(PW)
    a.save("Plan.md", "# Plan\n\nkoala launch notes\n")
    a.save("Shared.md", "line one\nline two\nline three\n")

    # 1. The first Mac makes the private repo (once) and sends everything up.
    full = f"{me}/{REPO}"
    exists = subprocess.run([gitsync.gh(), "api", f"repos/{full}"], capture_output=True).returncode == 0
    sa = GitSync(a_dir, REPO if not exists else full, BRANCH)
    if exists:
        sa.prepare("Notes")
        sa.git("init", "-b", BRANCH)
        sa.git("remote", "add", "origin", f"https://github.com/{full}.git")
        sa.sync_once()
    else:
        check(sa.create() == full, "the private repo was made")
    check(gitsync.is_private(full), "the repo is private")
    tree = subprocess.run([gitsync.gh(), "api", f"repos/{full}/git/trees/{BRANCH}?recursive=1", "--jq", "[.tree[].path]"],
                          capture_output=True, text=True).stdout
    check("vault.cryptomator" in tree and "Plan" not in tree and "koala" not in tree,
          "GitHub only has scrambled names", tree[:200])
    check('".github/README.md"' in tree and '"README.md"' not in tree and ".gitattributes" in tree,
          "the repo has the README (in .github) and the binary-only rule", tree[:300])
    shown = subprocess.run([gitsync.gh(), "api", f"repos/{full}/readme?ref={BRANCH}", "--jq", ".path"],
                           capture_output=True, text=True).stdout.strip()
    check(shown == ".github/README.md", "GitHub shows that README on the repo's page", shown)
    check(not (a_dir / "README.md").exists() and (a_dir / ".github" / "README.md").exists(),
          "the folder itself has no README in Finder (.github is hidden)")
    check(gitsync.repo_name("My Notes") == "My-Notes-Phygital-Memory", "repo name: FOLDER-Phygital-Memory",
          gitsync.repo_name("My Notes"))

    # 2. The second Mac brings it down and reads it.
    b_dir = tmp / "mac-b" / "Notes"
    b_dir.parent.mkdir()
    sb = GitSync.clone(full, b_dir, BRANCH)
    b = Memory(b_dir)
    b.unlock(PW)
    check(b.read("Plan.md") == "# Plan\n\nkoala launch notes\n", "the second Mac reads the note")

    # 3. A change on the first Mac reaches the second.
    a.save("Plan.md", "# Plan\n\nkoala launch notes\nadded on mac A\n")
    sa.sync_once()
    sb.sync_once()
    b._synced = 0
    check(b.read("Plan.md").endswith("added on mac A\n"), "a change on one Mac reaches the other")
    check(any(r["path"] == "Plan.md" for r in b.search("added on mac A")), "and is searchable there")

    # 4. Both change the same note: nothing is lost, the other side's version becomes a copy and an AI task.
    a.save("Shared.md", "line one\nline two (mac A)\nline three\n")
    b.save("Shared.md", "line one\nline two (mac B)\nline three\n")
    sa.sync_once()
    sb.sync_once()
    b._synced = 0
    files = [f["path"] for f in b.list_files()]
    copies = [p for p in files if p.startswith("Shared (conflict ")]
    texts = {b.read("Shared.md")} | {b.read(c) for c in copies}
    check(len(copies) == 1 and any("(mac A)" in t for t in texts) and any("(mac B)" in t for t in texts),
          "a clash keeps both versions (one becomes a copy)", files)
    check(any(t.get("copy") in copies for t in b.todo()), "the copy is an AI task to merge")
    check(len(b.versions("Shared.md")) >= 1 and not (b_dir / ".git" / gitsync.LOST).exists(),
          "the version history survives the folder clash", b.versions("Shared.md"))

    # 4b. Both Macs make the same new folder, each with its own note: both notes survive.
    a.save("Trips/lisbon.md", "lisbon from mac A\n")
    b.save("Trips/porto.md", "porto from mac B\n")
    sa.sync_once()
    sb.sync_once()
    b._synced = 0
    trips = sorted(f["path"] for f in b.list_files() if f["path"].startswith("Trips/"))
    check(trips == ["Trips/lisbon.md", "Trips/porto.md"], "same new folder on both Macs: both notes kept", trips)
    sb.sync_once()
    sa.sync_once()
    a._synced = 0
    trips_a = sorted(f["path"] for f in a.list_files() if f["path"].startswith("Trips/"))
    check(trips_a == ["Trips/lisbon.md", "Trips/porto.md"] and a.read("Trips/porto.md") == "porto from mac B\n",
          "and the first Mac ends up with both too", trips_a)
    check(not list(b_dir.rglob("* (1).c9r")), "no stray scrambled copies left")
    sa.sync_once()
    a._synced = 0
    check(any(p.startswith("Shared (conflict ") for p in (f["path"] for f in a.list_files())),
          "the first Mac gets the copy too")

    # 5. Too big for GitHub: kept on this Mac only, everything else still goes up.
    (b_dir / "d" / "big.c9r").write_bytes(b"0" * (gitsync.MAX_UP + 1))
    b.save("After.md", "after the big file\n")
    sb.sync_once()
    check(sb.state["too_big"] == ["d/big.c9r"], "a file over 95 MB stays on this Mac", sb.state)
    sa.sync_once()
    a._synced = 0
    check(a.read("After.md") == "after the big file\n", "the rest still syncs")

    # 6. If the repo ever turns public, nothing more is sent.
    a.save("Plan.md", "secret change\n")
    with mock.patch.object(gitsync, "is_private", lambda repo: False):
        try:
            sa.sync_once()
            check(False, "a public repo stops syncing")
        except RuntimeError as e:
            check("isn't private" in str(e) and sa.state["stopped"], "a public repo stops syncing", e)
    ahead = sa.git("rev-list", "--count", f"origin/{BRANCH}..HEAD").stdout.strip()
    check(ahead != "0", "and the change was not pushed", ahead)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(ok)}/{len(ok)} passed  (test branch {BRANCH} on {REPO})")
raise SystemExit(0 if all(ok) else 1)
