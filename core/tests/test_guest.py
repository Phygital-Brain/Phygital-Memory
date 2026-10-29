"""The AI app starts the engine itself (`phygital-memory-server mcp`, docs/connect-your-ai.md): with the app closed it
answers over stdin and stdout with the Open memories the key may reach, keeps to the key's rights (read only, edits,
"AI can't see this", a removed key), and never writes the app's own files. With the app open it passes every message
to the app's door. Throwaway folders, its own ports.

Run: uv run python tests/test_guest.py
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

tmp = Path(tempfile.mkdtemp(prefix="pm-guest-"))
os.environ.update({"PHYGITAL_MEMORY_STATE": str(tmp / "state"), "PHYGITAL_MEMORY_OFFLINE": "1"})

from mcp.client.session import ClientSession   # noqa: E402
from mcp.client.stdio import StdioServerParameters, stdio_client   # noqa: E402

from phygital_memory import gate as gate_mod   # noqa: E402  (reads the test state folder set above)

CLOSED, OPEN = int(os.environ.get("PM_GUEST_PORT", "8814")), int(os.environ.get("PM_GUEST_APP_PORT", "8815"))
core = Path(__file__).resolve().parent.parent
ok = []


def check(cond, what, info=""):
    ok.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + what + (f"  ({info})" if info and not cond else ""))


notes, hidden = tmp / "Notes", tmp / "Hidden"
(notes / "Animals").mkdir(parents=True)
(notes / "Animals" / "whale.md").write_text("# Whales\n\nThe blue whale is the largest animal.\n")
hidden.mkdir()
(hidden / "secret.md").write_text("# Secret\n\nThe orange lighthouse.\n")
state = tmp / "state"
state.mkdir()
(state / "folders.json").write_text(json.dumps({"folders": [
    {"id": "aa11", "name": "Notes", "path": str(notes), "open": True},
    {"id": "bb22", "name": "Hidden", "path": str(hidden), "open": True, "aiHidden": True}]}))
g = gate_mod.Gate()
_, read_key = g.add_key("Reader", "claude-code", "all", False)
writer, write_key = g.add_key("Writer", "codex", "all", True)
before = {n: (state / n).read_bytes() for n in ("folders.json", "ai-apps.json")}
env = {**os.environ, "PHYGITAL_MEMORY_VERSION": "0.0.0-test", "PHYGITAL_MEMORY_TRASH": str(tmp / "trash"),
       "PHYGITAL_MEMORY_FOLDER": str(tmp / "none"), "PYTHONPATH": str(core)}
env.pop("PHYGITAL_MEMORY_SHELL_TOKEN", None)
env.pop("PHYGITAL_MEMORY_SERVER", None)


async def ai(key, port, steps):
    p = StdioServerParameters(command=sys.executable, args=["-c", "from phygital_memory.server import main; main()", "mcp"],
                              env={**env, "PHYGITAL_MEMORY_KEY": key, "PHYGITAL_MEMORY_PORT": str(port)}, cwd=str(core))
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out = {"tools": sorted(t.name for t in (await s.list_tools()).tools)}
            for name, args in steps:
                res = await s.call_tool(name, args)
                out[name] = ("ERROR " if res.is_error else "") + "\n".join(c.text for c in res.content if hasattr(c, "text"))
            return out


# ---------- the app is closed: the engine answers by itself ----------
r = asyncio.run(ai(read_key, CLOSED, [("status", {}), ("search_notes", {"question": "largest animal"}),
                                      ("list_notes", {}),
                                      ("create_note", {"path": "new.md", "text": "no"})]))
check("search_notes" in r["tools"] and "create_note" in r["tools"], "the AI app sees the same tools", r["tools"])
check("Notes" in r["status"] and "Hidden" not in r["status"], "status shows the Open memory, not the hidden one", r["status"])
check("blue whale" in r["search_notes"].lower(), "search finds a note with the app closed", r["search_notes"][:300])
check("orange" not in r["search_notes"].lower(), "\"AI can't see this\" stays hidden")
check(r["create_note"].startswith("ERROR") and "only read" in r["create_note"], "a read-only key can't write", r["create_note"])
check(not (notes / "new.md").exists(), "nothing was written by the read-only key")

r = asyncio.run(ai(write_key, CLOSED, [("create_note", {"path": "Animals/otter.md", "text": "# Otters\n\nThey hold hands.\n"})]))
check(not r["create_note"].startswith("ERROR") and (notes / "Animals" / "otter.md").is_file(),
      "a key with Allow edits writes the note on disk", r["create_note"])

r = asyncio.run(ai(read_key, CLOSED, [("search_notes", {"question": "otters hold hands"})]))
check("otter" in r["search_notes"].lower(), "a new engine finds the note the other one wrote", r["search_notes"][:300])

after = {n: (state / n).read_bytes() for n in before}
check(after == before, "the app's own files (folders.json, ai-apps.json) are never written")

gate_mod.Gate().remove(writer["id"])
r = asyncio.run(ai(read_key, CLOSED, [("status", {})]))   # the reader still works
check("Notes" in r["status"], "another key keeps working after one is removed", r["status"])
try:
    r = asyncio.run(ai(write_key, CLOSED, [("status", {})]))
    check(False, "a removed key is refused", str(r)[:200])
except Exception as e:
    check(True, "a removed key is refused")

# ---------- the app is open: every message goes to the app's door ----------
log = open(tmp / "app.log", "wb")
app = subprocess.Popen([sys.executable, "-m", "phygital_memory.server"], cwd=core, stdout=log, stderr=subprocess.STDOUT,
                       env={**env, "PHYGITAL_MEMORY_PORT": str(OPEN)})
try:
    for _ in range(150):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{OPEN}/mcp-proof?n={'a' * 32}", timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    r = asyncio.run(ai(read_key, OPEN, [("status", {})]))
    check(r.get("status") and "Notes" in r["status"], "with the app open, the answer comes from the app", r)
    seen = urllib.request.urlopen(f"http://127.0.0.1:{OPEN}/mcp-proof?n={'b' * 32}", timeout=2).read()
    check(b"proofs" in seen, "the app's door is up")
finally:
    app.terminate()
    app.wait(10)

print(f"\n{sum(ok)}/{len(ok)} passed")
sys.exit(0 if all(ok) else 1)
