"""SQLite schema.

files       what was indexed (one row per note), and which shelf it sits on
chunks      the sections, with heading path, date, weights and the text itself (stored here only)
cards       Haiku note cards, keyed by the section's content hash (survive re-indexing)
chat_cards  one Haiku card per AI conversation: summary, atoms, topic, lasting value, has a decision
fts         search index for the main shelf: title, heading path, tags, body, card text
fts_bg      search index for the background shelf (archives, copied code), same columns

With "store_text_once" the search indexes keep only the word index, not a second copy of the text
(the text lives once, in chunks). That halves the disk and changes nothing in the results.
"""
import sqlite3
from pathlib import Path

SCHEMA_VERSION = "6"
FTS_COLS = "title, heading, tags, body, card"
TABLES = {"main": "fts", "back": "fts_bg"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS files(
    path TEXT PRIMARY KEY, source TEXT NOT NULL, mtime REAL, size INTEGER,
    weight REAL DEFAULT 1.0, hidden INTEGER DEFAULT 0, indexed_at REAL,
    keep INTEGER DEFAULT 0, linked INTEGER DEFAULT 0, fhash TEXT, shelf TEXT DEFAULT 'main', until REAL
);
CREATE TABLE IF NOT EXISTS chat_cards(
    path TEXT PRIMARY KEY, fhash TEXT, summary TEXT, atoms TEXT, topic TEXT, value TEXT,
    has_decision INTEGER DEFAULT 0, model TEXT, created_at REAL
);
CREATE TABLE IF NOT EXISTS chunks(
    id INTEGER PRIMARY KEY, file_path TEXT NOT NULL REFERENCES files(path) ON DELETE CASCADE,
    ordinal INTEGER, heading TEXT, date REAL, evergreen INTEGER DEFAULT 0,
    type TEXT, project TEXT, status TEXT, tags TEXT, weight REAL DEFAULT 1.0,
    hash TEXT, body TEXT
);
CREATE INDEX IF NOT EXISTS chunks_file ON chunks(file_path);
CREATE INDEX IF NOT EXISTS files_source ON files(source);
CREATE TABLE IF NOT EXISTS backlinks(path TEXT PRIMARY KEY, n INTEGER);
CREATE TABLE IF NOT EXISTS usage(
    path TEXT PRIMARY KEY, shown REAL DEFAULT 0, opened REAL DEFAULT 0, last_ts REAL
);
CREATE INDEX IF NOT EXISTS chunks_hash ON chunks(hash);
CREATE TABLE IF NOT EXISTS cards(
    hash TEXT PRIMARY KEY, context TEXT, summary TEXT, questions TEXT, atoms TEXT,
    model TEXT, created_at REAL
);
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
"""


def _fts_sql(name, text_once):
    opts = ", content='', contentless_delete=1" if text_once else ""
    return (f"CREATE VIRTUAL TABLE IF NOT EXISTS {name} USING fts5({FTS_COLS}{opts}, "
            f"tokenize='porter unicode61 remove_diacritics 2');")


def connect(path, text_once=None):
    """Open (or create) an index. text_once is only used when the index is new; after that the
    index remembers how it was built."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SCHEMA)
    row = con.execute("SELECT v FROM meta WHERE k='text_once'").fetchone()
    if row is None:
        mode = "1" if text_once else "0"
        con.execute("INSERT OR REPLACE INTO meta VALUES('text_once',?)", (mode,))
    else:
        mode = row[0]
    for name in TABLES.values():
        con.execute(_fts_sql(name, mode == "1"))
    if con.execute("SELECT v FROM meta WHERE k='schema_version'").fetchone() is None:
        con.execute("INSERT INTO meta VALUES('schema_version',?)", (SCHEMA_VERSION,))
    con.commit()
    return con


def text_once(con):
    row = con.execute("SELECT v FROM meta WHERE k='text_once'").fetchone()
    return bool(row) and row[0] == "1"


def schema_ok(path, want_text_once=None):
    path = Path(path)
    if not path.exists():
        return True
    con = sqlite3.connect(path)
    try:
        row = con.execute("SELECT v FROM meta WHERE k='schema_version'").fetchone()
        if not row or row[0] != SCHEMA_VERSION:
            return False
        if want_text_once is not None:
            m = con.execute("SELECT v FROM meta WHERE k='text_once'").fetchone()
            if not m or (m[0] == "1") != bool(want_text_once):
                return False  # the setting changed: rebuild
        return True
    except sqlite3.Error:
        return False
    finally:
        con.close()


def card_text(row):
    """Flatten a cards row (context, summary, questions, atoms) into searchable text."""
    if not row:
        return ""
    return "\n".join(x for x in row if x)


def title_of(path):
    return Path(path).stem.replace("-", " ").replace("_", " ")


def fts_put(con, rowid, shelf, title, heading, tags, body, card):
    con.execute(f"INSERT OR REPLACE INTO {TABLES[shelf]}(rowid, {FTS_COLS}) VALUES(?,?,?,?,?,?)",
                (rowid, title, heading, tags, body, card))


def set_card(con, rowid, card):
    """Put new card text on one section. Works for both storage modes (re-writes the whole row)."""
    r = con.execute("SELECT c.file_path, c.heading, c.tags, c.body, f.shelf, f.source FROM chunks c "
                    "JOIN files f ON f.path = c.file_path WHERE c.id=?", (rowid,)).fetchone()
    if not r:
        return
    path, heading, tags, body, shelf, source = r
    title = f"session {source}" if source == "session" else title_of(path)
    fts_put(con, rowid, shelf or "main", title, heading, tags, body, card)


def remove_file(con, path):
    row = con.execute("SELECT shelf FROM files WHERE path=?", (path,)).fetchone()
    table = TABLES.get(row[0] if row else "main", "fts")
    ids = [r[0] for r in con.execute("SELECT id FROM chunks WHERE file_path=?", (path,))]
    con.executemany(f"DELETE FROM {table} WHERE rowid=?", [(i,) for i in ids])
    con.execute("DELETE FROM files WHERE path=?", (path,))  # cascades to chunks; cards are kept by hash
