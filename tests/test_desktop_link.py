"""The Desktop shortcut while a folder is open in Finder: made, never over someone else's file, removed, and
leftovers cleared at start.

Run: uv run python test_desktop_link.py
"""
import os
import tempfile
from pathlib import Path

t = Path(tempfile.mkdtemp(prefix="pm-link-"))
(t / "Desktop").mkdir()
(t / "mnt" / "abc").mkdir(parents=True)
os.environ["PHYGITAL_MEMORY_MOUNTS"] = str(t / "mnt")
os.environ["PHYGITAL_MEMORY_DESKTOP"] = str(t / "Desktop")
from phygital_memory import finder as F   # noqa: E402  (reads the two places above when loaded)

ok = []


def check(cond, what):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what)


link = F._add_desktop_link("Notes", str(t / "mnt" / "abc"))
check(link and link.is_symlink() and link.name == "Notes", "shortcut made on the Desktop")
(t / "Desktop" / "Other").write_text("mine")
other = F._add_desktop_link("Other", str(t / "mnt" / "abc"))
check(other.name == "Other (Phygital Memory)" and (t / "Desktop" / "Other").read_text() == "mine",
      "a file with that name is never touched")
F._remove_desktop_link(link)
check(not os.path.lexists(link), "shortcut removed")
(t / "Desktop" / "Elsewhere").symlink_to(t)
F.clear_desktop_links()
check(not os.path.lexists(other) and (t / "Desktop" / "Other").exists() and os.path.lexists(t / "Desktop" / "Elsewhere"),
      "leftovers cleared at start, nothing else")
print(f"\n{sum(ok)}/{len(ok)} passed")
raise SystemExit(0 if all(ok) else 1)
