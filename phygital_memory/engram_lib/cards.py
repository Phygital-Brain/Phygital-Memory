"""Haiku note cards (Nick's "summaries + atoms", Anthropic's contextual retrieval, doc2query).

For each section without a card, Haiku writes:
  context    one line on where this section sits in its note
  summary    one or two short summaries in different words
  questions  questions someone would type to find it (kept only if grounded in the section)
  atoms      exact facts: errors, fixes, commands, versions, names, the reason behind a decision

Cards are stored by the section's content hash, so unchanged sections never cost twice,
and they go into their own search column. Hidden notes and .claudeignore paths never reach Haiku
(they are never indexed). Secrets were already redacted at ingest.
"""
import json, re, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

from .config import api_key
from .db import connect, card_text, set_card
from .search import words

PROMPT = """You write a search card for one section of a personal Obsidian note. The card helps a keyword search find this section later, including when someone uses different words.

Note: {title}
Section path: {heading}
Note type: {type}

<note_start>
{note_start}
</note_start>

<section>
{body}
</section>

Reply with JSON only, no other text:
{{"context": "one sentence on where this section sits in the note and what it is for",
  "summary": "one or two short sentences saying what the section says, in plain words that differ from the original",
  "questions": ["3 to 5 questions a person would type to find this section, in everyday words"],
  "atoms": ["0 to 6 exact facts copied from the section: error messages, fixes, commands, versions, names, numbers, dates, and the reason behind any decision"]}}

Use only facts that are in the section or the note start. Never invent anything. Never use em dashes."""


CHAT_PROMPT = """You write a search card for one saved conversation between a person and an AI assistant. The card decides how findable the chat stays over time.

File: {title}

<chat>
{body}
</chat>

Reply with JSON only, no other text:
{{"summary": "two or three short sentences on what the chat was about and what came out of it, in plain words",
  "atoms": ["0 to 8 exact facts from the chat: decisions and their reason, fixes, commands, versions, names, numbers"],
  "topic": "two to four lowercase words naming the main topic, the same words another chat on this topic would get",
  "value": "high if it holds a lasting decision, fix, rule or reference; medium if useful for a while; low if small talk, a one-off or already outdated",
  "has_decision": true or false}}

Use only what is in the chat. Never invent anything. Never use em dashes."""


def pending_chats(con, limit=None):
    q = ("SELECT f.path, f.fhash FROM files f LEFT JOIN chat_cards k ON k.path = f.path AND k.fhash = f.fhash "
         "WHERE f.source = 'chat' AND f.hidden = 0 AND k.path IS NULL ORDER BY f.mtime DESC")
    if limit:
        q += f" LIMIT {int(limit)}"
    return con.execute(q).fetchall()


def fake_chat_card(path):
    """Offline stand-in: topic from the file name without its date, medium value."""
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-?", "", path.rsplit("/", 1)[-1].rsplit(".", 1)[0])
    return {"summary": f"Conversation about {stem.replace('-', ' ')}.", "atoms": [],
            "topic": stem.replace("-", " ").lower(), "value": "medium", "has_decision": False}


def run_chats(cfg, con, key, fake, stats, limit=None):
    for path, fhash in pending_chats(con, limit):
        body = "\n\n".join(b for (b,) in con.execute(
            "SELECT body FROM chunks WHERE file_path=? ORDER BY ordinal", (path,)))[:16000]
        try:
            if fake:
                card, ti, to = fake_chat_card(path), 0, 0
            else:
                text, ti, to = call_haiku(cfg, key, CHAT_PROMPT.format(title=path.rsplit("/", 1)[-1], body=body))
                card = parse_card(text)
            if not card:
                raise RuntimeError("reply was not JSON")
            value = str(card.get("value", "medium")).lower()
            value = value if value in ("high", "medium", "low") else "medium"
            atoms = grounded(card.get("atoms", []), body)[:8]
            vals = (str(card.get("summary", ""))[:800], "\n".join(atoms))
            con.execute("INSERT OR REPLACE INTO chat_cards VALUES(?,?,?,?,?,?,?,?,?)",
                        (path, fhash, vals[0], vals[1], str(card.get("topic", ""))[:60].lower(), value,
                         int(bool(card.get("has_decision"))), "fake" if fake else cfg["cards"]["model"], time.time()))
            first = con.execute("SELECT id FROM chunks WHERE file_path=? ORDER BY ordinal LIMIT 1", (path,)).fetchone()
            if first:
                set_card(con, first[0], card_text(vals))
            stats["chats"] += 1
            stats["input_tokens"] += ti
            stats["output_tokens"] += to
        except Exception as e:
            stats["failed"] += 1
            if len(stats["errors"]) < 5:
                stats["errors"].append(f"chat {path.rsplit('/', 1)[-1]}: {e}")
    con.commit()


def pending(con, cfg, limit=None):
    """Sections that still need a card, most important first."""
    srcs = cfg["cards"]["sources"]
    q = (f"SELECT c.id, c.hash, c.file_path, c.heading, c.type, c.body FROM chunks c "
         f"JOIN files f ON f.path = c.file_path LEFT JOIN cards k ON k.hash = c.hash "
         f"WHERE k.hash IS NULL AND f.hidden = 0 AND f.source IN ({','.join('?' * len(srcs))}) "
         f"GROUP BY c.hash ORDER BY c.weight DESC, c.date DESC")
    if limit:
        q += f" LIMIT {int(limit)}"
    return con.execute(q, srcs).fetchall()


def estimate(cfg):
    con = connect(cfg["db"])
    rows = pending(con, cfg)
    chats = pending_chats(con)
    chars = sum(len(r[5]) for r in rows)
    in_tok = int(chars / 4) + len(rows) * 900 + len(chats) * 4500  # section + prompt + note start; chats up to 16k chars
    out_tok = len(rows) * 250 + len(chats) * 350
    return dict(sections=len(rows), chats=len(chats), input_tokens=in_tok, output_tokens=out_tok)


def grounded(items, source_text):
    """Keep a question or atom only if it shares a real word with the section (filters made-up ones).
    Haiku sometimes sends a single string or nothing instead of a list; both are handled."""
    if isinstance(items, str):
        items = [items]
    elif not isinstance(items, list):
        items = []
    have = {w[:5] for w in words(source_text)}
    keep = []
    for it in items:
        if isinstance(it, str) and it.strip() and any(w[:5] in have for w in words(it)):
            keep.append(it.strip())
    return keep


def call_haiku(cfg, key, prompt):
    body = json.dumps({"model": cfg["cards"]["model"], "max_tokens": cfg["cards"]["max_tokens"],
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST", headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            usage = data.get("usage", {})
            return text, usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(2 ** attempt * 3)
                continue
            raise RuntimeError(f"API error {e.code}: {e.read()[:200].decode(errors='ignore')}")
    raise RuntimeError("API kept failing")


def parse_card(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def fake_card(title, heading, body):
    """Offline stand-in for testing the pipeline. Costs nothing, finds nothing new."""
    first = re.split(r"(?<=[.!?])\s", body.strip(), 1)[0][:200]
    return {"context": f"Part of the note {title}, section {heading.split(' > ')[-1]}.",
            "summary": first, "questions": [f"what does {heading.split(' > ')[-1]} say"], "atoms": []}


def run(cfg, limit=None, fake=False, log=print):
    """Make cards, holding the same lock as index updates so a rebuild and cards never write at once."""
    from .ingest import index_lock
    with index_lock(cfg):
        return _run_cards(cfg, limit, fake, log)


def _run_cards(cfg, limit=None, fake=False, log=print):
    con = connect(cfg["db"])
    key = None if fake else api_key()
    if not fake and not key:
        raise SystemExit("No API key. Put ANTHROPIC_API_KEY=... in engram-test/.env (this folder, never in the vault), "
                         "or run with --fake to test the pipeline for free.")
    stats = dict(done=0, chats=0, failed=0, input_tokens=0, output_tokens=0, errors=[])
    if "chat" in cfg["cards"]["sources"]:
        run_chats(cfg, con, key, fake, stats, limit)  # one card per AI conversation, newest first
    rows = pending(con, cfg, limit)
    starts = {}
    lock = threading.Lock()

    def note_start(path):
        if path not in starts:
            r = con.execute("SELECT body FROM chunks WHERE file_path=? ORDER BY ordinal LIMIT 1", (path,)).fetchone()
            starts[path] = (r[0] if r else "")[:1200]
        return starts[path]

    def work(row):
        cid, h, path, heading, typ, body = row
        title = heading.split(" > ")[0]
        try:
            if fake:
                card, ti, to = fake_card(title, heading, body), 0, 0
            else:
                with lock:
                    start = note_start(path)
                text, ti, to = call_haiku(cfg, key, PROMPT.format(
                    title=title, heading=heading, type=typ or "note", note_start=start, body=body))
                card = parse_card(text)
            if not card:
                raise RuntimeError("reply was not JSON")
            src = heading + "\n" + body
            summary = card.get("summary", "")
            summary = " ".join(summary) if isinstance(summary, list) else str(summary)
            vals = (str(card.get("context", ""))[:400], summary[:600],
                    "\n".join(grounded(card.get("questions", []), src)[:5]),
                    "\n".join(grounded(card.get("atoms", []), src)[:6]))
            with lock:
                con.execute("INSERT OR REPLACE INTO cards VALUES(?,?,?,?,?,?,?)",
                            (h, *vals, "fake" if fake else cfg["cards"]["model"], time.time()))
                for (rid,) in con.execute("SELECT id FROM chunks WHERE hash=?", (h,)).fetchall():
                    set_card(con, rid, card_text(vals))
                stats["done"] += 1
                stats["input_tokens"] += ti
                stats["output_tokens"] += to
                if stats["done"] % 50 == 0:
                    con.commit()
                    log(f"  {stats['done']}/{len(rows)} cards")
        except Exception as e:
            with lock:
                stats["failed"] += 1
                if len(stats["errors"]) < 5:
                    stats["errors"].append(f"{path} > {heading.split(' > ')[-1]}: {e}")

    workers = 1 if fake else cfg["cards"]["workers"]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, rows))
    con.commit()
    stats["remaining"] = len(pending(con, cfg))
    return stats


def export(cfg):
    """Every real Haiku card, for a local test copy. Finance notes never get cards, so none are in here."""
    from .ingest import _saved
    s = _saved(cfg["db"])
    return {"cards": [r for r in s["cards"] if r[5] != "fake"],
            "chat_cards": [r for r in s["chat_cards"] if r[7] != "fake"]}


def import_file(cfg, path):
    """Load cards downloaded from the server, then rebuild so every matching section picks its card up.
    Cards are keyed by content, so only sections that are the same here as on the server match."""
    from .ingest import run as ingest_run
    data = json.loads(open(path).read())
    con = connect(cfg["db"])
    con.executemany("INSERT OR IGNORE INTO cards VALUES(?,?,?,?,?,?,?)", data.get("cards", []))
    con.executemany("INSERT OR IGNORE INTO chat_cards VALUES(?,?,?,?,?,?,?,?,?)", data.get("chat_cards", []))
    con.commit()
    con.close()
    ingest_run(cfg, rebuild=True)
    con = connect(cfg["db"])
    used = con.execute("SELECT COUNT(*) FROM chunks c JOIN cards k ON k.hash = c.hash").fetchone()[0]
    return {"cards": len(data.get("cards", [])), "chat_cards": len(data.get("chat_cards", [])), "sections_with_card": used}
