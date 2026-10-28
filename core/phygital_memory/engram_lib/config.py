"""Load config.json and resolve paths. Refuses to put any data inside the notes folder."""
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path=None):
    """ENGRAM_VAULT points at the notes folder and ENGRAM_DATA at the folder for the index (outside the notes)."""
    cfg = json.loads((path or ROOT / "config.json").read_text())
    cfg["vault"] = Path(os.environ.get("ENGRAM_VAULT") or cfg["vault"]).expanduser()
    data = Path(os.environ["ENGRAM_DATA"]).expanduser() if os.environ.get("ENGRAM_DATA") else ROOT
    at = lambda rel: (data / (rel[len("data/"):] if os.environ.get("ENGRAM_DATA") and rel.startswith("data/") else rel)).resolve()
    cfg["db"] = at(cfg["db"])
    cfg["private"]["db"] = at(cfg["private"]["db"])
    # "Store text once" needs SQLite 3.43+ (contentless_delete). Older SQLite keeps the normal index.
    import sqlite3
    if sqlite3.sqlite_version_info < (3, 43, 0):
        cfg["store_text_once"] = False
    # The path to show people, when it differs from the folder this program reads (for example on a server).
    cfg["display_vault"] = os.environ.get("ENGRAM_DISPLAY_VAULT") or str(cfg["vault"])
    vault = cfg["vault"].resolve()
    for name, p in (("db", cfg["db"]), ("private db", cfg["private"]["db"])):
        if vault == p or vault in p.parents:
            raise SystemExit(f"Refusing to run: {name} path is inside the vault.")
    return cfg


def api_key():
    """ANTHROPIC_API_KEY from the environment or from .env in this folder (never synced, never printed)."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip().strip("\"'")
    return None
