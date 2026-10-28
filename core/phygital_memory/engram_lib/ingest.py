"""Incremental indexer. Reads the notes folder, never writes to it.

- A file is re-indexed only when its modified time or size changed.
- Notes that disappeared are removed, unless so many vanish at once that the folder looks half-synced.
- Secrets are redacted before anything is stored.
"""
import fnmatch, hashlib, json, os, re, time
from pathlib import Path

from .db import connect, remove_file, schema_ok, card_text, fts_put, set_card, TABLES


# ---------- helpers ----------

def read_ignore(vault):
    f = vault / ".claudeignore"
    if not f.exists():
        return []
    return [l.strip() for l in f.read_text().splitlines() if l.strip() and not l.startswith("#")]


def is_ignored(rel, pats):
    for p in pats:
        if p.endswith("/"):
            if rel.startswith(p) or ("/" + p) in ("/" + rel):
                return True
        elif fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p):
            return True
        elif not any(ch in p for ch in "*?[") and rel.startswith(p.rstrip("/") + "/"):
            return True  # 'finances' without a slash still covers the whole folder
    return False


def is_private(rel, cfg):
    """Private folders never go in the main index, whatever .claudeignore says."""
    low = rel.lower()  # "Finances/" counts too
    return any(low.startswith(p.rstrip("/").lower() + "/") for p in cfg.get("private", {}).get("paths", []))


def matches_any(rel, globs):
    """Folder rules ignore capital letters, so 'archive' and 'Archive' are the same."""
    return any(fnmatch.fnmatchcase(rel.lower(), g.lower()) for g in globs)


def path_weight(rel, cfg):
    for rule in cfg["path_weights"]:
        if matches_any(rel, [rule["match"]]):
            return rule["weight"]
    return 1.0


def make_redactor(cfg):
    rx = [re.compile(p) for p in cfg["redact_patterns"]]

    def redact(text):
        for r in rx:
            text = r.sub("[REDACTED]", text)
        return text

    return redact


def parse_frontmatter(text):
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line and not line.startswith(" "):
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip().strip("[]\"'")
            body = text[end + 4:]
    return meta, body


def to_ts(v):
    v = (v or "")[:10]
    if re.match(r"\d{4}-\d{2}-\d{2}$", v):
        try:
            return time.mktime(time.strptime(v, "%Y-%m-%d"))
        except ValueError:
            pass
    return None


def date_of(meta, name, mtime):
    """Frontmatter updated > date > date in the filename > file time (cloud sync apps can touch the file time)."""
    for key in ("updated", "date"):
        ts = to_ts(meta.get(key))
        if ts:
            return ts
    m = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return (to_ts(m.group(1)) if m else None) or mtime


def split_chunks(body, title, cfg):
    """Split on headings, keeping the full heading path ("Note > H2 > H3").
    Tiny sections are merged into the next one; long ones are split with a small overlap."""
    max_c, min_c, overlap = cfg["chunk_max_chars"], cfg["chunk_min_chars"], cfg["chunk_overlap_chars"]
    parts, stack, buf, in_code = [], [], [], False  # stack holds (level, heading)
    path = lambda: " > ".join([title] + [h for _, h in stack])
    current = path()
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        m = None if in_code else re.match(r"^(#{1,4}) (\S.*)", line)
        if m:
            if "\n".join(buf).strip():
                parts.append([current, "\n".join(buf).strip()])
            level = len(m.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, m.group(2).strip()))
            current, buf = path(), []
        else:
            buf.append(line)
    if "\n".join(buf).strip():
        parts.append([current, "\n".join(buf).strip()])

    merged = []  # tiny sections ride along with the next section, heading text kept inline
    carry = ""
    for head, text in parts:
        if carry:
            text = carry + "\n\n" + text
            carry = ""
        if len(text) < min_c:
            carry = f"{head.split(' > ')[-1]}: {text}"
            continue
        merged.append([head, text])
    if carry:
        if merged:
            merged[-1][1] += "\n\n" + carry
        elif len(carry) >= 20:
            merged.append([path() if not parts else parts[-1][0], carry])

    out = []
    for head, t in merged:
        while len(t) > max_c:
            cut = t.rfind("\n\n", 0, max_c)
            cut = cut if cut > max_c // 3 else t.rfind("\n", 0, max_c)
            cut = cut if cut > max_c // 3 else max_c
            out.append((head, t[:cut].strip()))
            t = t[cut - overlap if cut - overlap > 0 else cut:].strip()  # always moves forward
        if len(t) >= 20:
            out.append((head, t))
    return out


def chunk_hash(path, head, body):
    """Content only (heading path and text): a renamed note keeps its paid Haiku cards."""
    return hashlib.sha1(f"{head}\n{body}".encode()).hexdigest()


def add_file(con, path, source, mtime, size, weight, hidden, title, chunks, keep=0, linked=0, fhash=None,
             shelf="main", until=None):
    remove_file(con, path)
    con.execute("INSERT INTO files(path,source,mtime,size,weight,hidden,indexed_at,keep,linked,fhash,shelf,until) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (path, source, mtime, size, weight, hidden, time.time(), keep, linked, fhash, shelf, until))
    for i, c in enumerate(chunks):
        h = chunk_hash(path, c["heading"], c["body"])
        cur = con.execute(
            "INSERT INTO chunks(file_path,ordinal,heading,date,evergreen,type,project,status,tags,weight,hash,body) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (path, i, c["heading"], c["date"], c["evergreen"], c["type"], c["project"], c["status"], c["tags"],
             c["weight"], h, c["body"]),
        )
        card = con.execute("SELECT context, summary, questions, atoms FROM cards WHERE hash=?", (h,)).fetchone()
        fts_put(con, cur.lastrowid, shelf, title, c["heading"], c["tags"], c["body"], card_text(card))


def callout_text(body, cfg):
    """Text inside Obsidian callouts like > [!important] Decision. With callouts.enabled it is also put in the
    tags field, which counts twice as much as normal text."""
    c = cfg.get("callouts", {})
    if not c.get("enabled"):
        return ""
    types = set(c.get("types", ["important", "warning", "tip", "todo", "note", "info", "success", "failure", "question"]))
    out, inside = [], False
    for line in body.splitlines():
        m = re.match(r"^>\s*\[!(\w+)\]\s*(.*)", line)
        if m:
            inside = m.group(1).lower() in types
            if inside and m.group(2):
                out.append(m.group(2))
        elif inside and line.startswith(">"):
            out.append(line.lstrip("> ").strip())
        else:
            inside = False
    return " ".join(out)[:2000]


def count_backlinks(con, cfg):
    """How many other notes link to each note with [[links]] (main shelf only: copied code does not vote)."""
    names = {}
    for (path,) in con.execute("SELECT path FROM files WHERE source='vault' AND shelf='main'"):
        names.setdefault(Path(path).stem.lower(), []).append(path)
    counts = {}
    for path, body in con.execute("SELECT c.file_path, group_concat(c.body, ' ') FROM chunks c JOIN files f "
                                  "ON f.path=c.file_path WHERE f.source='vault' AND f.shelf='main' GROUP BY c.file_path"):
        seen = set()
        here = os.path.dirname(path)
        for name in re.findall(r"\[\[([^\]|#]+)", body or ""):
            name = name.strip()
            options = names.get(Path(name).stem.lower(), [])
            if "/" in name:  # a link with a path picks the note whose path ends with it
                options = [t for t in options if t.lower().endswith(name.lower().removesuffix(".md") + ".md")]
            if len(options) > 1:  # like Obsidian: an unclear link means the one in the same folder, else nothing
                options = [t for t in options if os.path.dirname(t) == here]
            for target in options[:1]:
                if target != path and target not in seen:
                    seen.add(target)
                    counts[target] = counts.get(target, 0) + 1
    con.execute("DELETE FROM backlinks")
    con.executemany("INSERT INTO backlinks VALUES(?,?)", counts.items())


def is_conflict(name):
    """Sync duplicates: 'note (conflicted copy 2026-10-20 101112).md' (cloud drives), 'note.sync-conflict-...' (Syncthing)."""
    return bool(re.search(r"\(conflicted copy|\.sync-conflict-", name, re.I))


def shelf_of(rel, cfg):
    """Background shelf: archives and copied code. Main shelf: everything else."""
    sh = cfg.get("shelves", {})
    if sh.get("enabled") and matches_any(rel, sh.get("background_paths", [])):
        return "back"
    return "main"


def has_skip_marker(text, cfg):
    """The marker counts only on a line of its own near the top (or as a frontmatter line), so a note that
    merely talks about the marker is still indexed."""
    marks = [m.lower() for m in cfg["skip_markers"]]
    lines = [l.strip().lower() for l in text[:2000].splitlines() if l.strip()][:12]
    return any(l in marks for l in lines)


# ---------- vault ----------

def ingest_vault(con, cfg, redact, stats):
    vault, pats, seen = cfg["vault"], read_ignore(cfg["vault"]), set()
    known = {r[0]: (r[1], r[2]) for r in con.execute(
        "SELECT path,mtime,size FROM files WHERE source IN ('vault','chat')")}
    today = time.time()
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in cfg["skip_dirs"]]
        for name in files:
            if not name.lower().endswith(".md"):
                continue
            if is_conflict(name):  # a cloud drive or Syncthing duplicate of another note
                stats["conflicts"] += 1
                continue
            full = Path(root) / name
            rel = str(full.relative_to(vault))
            if is_ignored(rel, pats) or matches_any(rel, cfg["exclude_paths"]) or is_private(rel, cfg):
                stats["ignored"] += 1
                continue
            seen.add(rel)  # before reading: a short read error (a cloud placeholder file) must not drop the note
            try:
                st = full.stat()
                if st.st_size > cfg["max_file_bytes"]:
                    stats["too_big"] += 1
                    seen.discard(rel)
                    continue
                if known.get(rel) == (st.st_mtime, st.st_size):
                    stats["unchanged"] += 1
                    continue
                text = full.read_text(errors="ignore")
            except OSError as e:
                stats["errors"].append(f"{rel}: {e}")
                continue
            if "\x00" in text[:4000]:  # not a real note (binary or damaged file): skip it, report it in health
                stats["unreadable"] += 1
                seen.discard(rel)
                continue
            if has_skip_marker(text, cfg):
                stats["skipped_marker"] += 1
                seen.discard(rel)
                continue
            meta, body = parse_frontmatter(redact(text))
            status = meta.get("status", "").lower()
            until = to_ts(meta.get("valid_until"))
            hidden = int(status in cfg["hide_status"] or (until is not None and until < today))
            # the folder's own guide (CLAUDE.md, README.md) is a rule file, not a chat
            is_chat = rel.startswith(cfg["conversations"]["path"]) and name not in ("CLAUDE.md", "README.md")
            # chats: weight, age steps and fading are worked out at search time (they change as days pass)
            fw = 1.0 if is_chat else (path_weight(rel, cfg) * cfg["status_weights"].get(status, 1.0)
                                      * cfg.get("type_weights", {}).get(meta.get("type", "").lower(), 1.0))
            evergreen = int(not is_chat and matches_any(rel, cfg["evergreen_paths"])
                            and not matches_any(rel, cfg.get("evergreen_exclude", [])))
            when = date_of(meta, name, st.st_mtime)
            title = Path(rel).stem.replace("-", " ").replace("_", " ")
            chunks = [
                dict(heading=h, body=b, date=when, evergreen=evergreen, type=meta.get("type", ""),
                     project=meta.get("project", ""), status=status,
                     tags=(meta.get("tags", "") + " " + meta.get("topic", "") + " " + callout_text(b, cfg)).strip(),
                     weight=fw)
                for h, b in split_chunks(body, Path(rel).stem, cfg)
            ]
            keep = int(meta.get("keep", "").lower() in ("true", "yes", "1"))
            linked = int(bool(re.search(r"\[\[[^\]]+\]\]", body))) if is_chat else 0
            fhash = hashlib.sha1(body.encode()).hexdigest() if is_chat else None
            add_file(con, rel, "chat" if is_chat else "vault", st.st_mtime, st.st_size, fw, hidden, title, chunks,
                     keep=keep, linked=linked, fhash=fhash, shelf="main" if is_chat else shelf_of(rel, cfg),
                     until=until)
            if is_chat:
                card = con.execute("SELECT summary, atoms FROM chat_cards WHERE path=? AND fhash=?",
                                   (rel, fhash)).fetchone()
                if card:  # the chat's card text rides on its first section
                    first = con.execute("SELECT id FROM chunks WHERE file_path=? ORDER BY ordinal LIMIT 1",
                                        (rel,)).fetchone()
                    if first:
                        set_card(con, first[0], card_text(card))
            stats["indexed"] += 1
            stats["hidden"] += hidden
    gone = set(known) - seen
    # Safety: if the cloud drive is offline or half-synced, the walk sees few files.
    # Never let that wipe the index. Big removals need --rebuild.
    if known and len(gone) > max(20, len(known) * 0.2) and not cfg.get("_rebuild"):
        stats["errors"].append(f"refused to remove {len(gone)} of {len(known)} notes (vault looks incomplete); "
                               "run 'ingest --rebuild' if this is intended")
        return
    for path in gone:
        remove_file(con, path)
        stats["removed"] += 1


# ---------- private folders (finances) ----------

def make_id_blanker(cfg):
    rx = [re.compile(p) for p in cfg["private"]["id_patterns"]]

    def blank(text):
        for r in rx:
            text = r.sub("[ID]", text)
        return text

    return blank


def ingest_private(cfg, redact, stats):
    """Index the private folders into their own file (data/private.sqlite).
    Tax IDs, social security numbers, IBANs and card numbers are blanked before storing.
    Search may say WHERE a match is; it never shows the text (see search.py)."""
    pcfg = cfg["private"]
    if not pcfg["enabled"]:
        return
    con = connect(pcfg["db"], text_once=cfg.get("store_text_once"))
    vault = cfg["vault"]
    blank = make_id_blanker(cfg)
    private_roots = {p.rstrip("/") for p in pcfg["paths"]}
    pats = [p for p in read_ignore(vault) if p.rstrip("/") not in private_roots]  # keys, .env etc. stay excluded
    known = {r[0]: (r[1], r[2]) for r in con.execute("SELECT path,mtime,size FROM files")}
    seen = set()
    for folder in pcfg["paths"]:
        base = vault / folder
        if not base.is_dir():
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in cfg["skip_dirs"]]
            for name in files:
                if not name.lower().endswith(".md") or is_conflict(name):
                    continue
                full = Path(root) / name
                rel = str(full.relative_to(vault))
                if is_ignored(rel, pats):
                    continue
                try:
                    st = full.stat()
                    if st.st_size > cfg["max_file_bytes"]:
                        continue
                    seen.add(rel)
                    if known.get(rel) == (st.st_mtime, st.st_size):
                        stats["unchanged"] += 1
                        continue
                    text = full.read_text(errors="ignore")
                except OSError as e:
                    stats["errors"].append(f"private file: {e.__class__.__name__}")  # no private path in logs
                    continue
                if has_skip_marker(text, cfg):
                    seen.discard(rel)
                    continue
                meta, body = parse_frontmatter(blank(redact(text)))
                when = date_of(meta, name, st.st_mtime)
                title = Path(rel).stem.replace("-", " ").replace("_", " ")
                chunks = [dict(heading=h, body=b, date=when, evergreen=0, type=meta.get("type", ""),
                               project=meta.get("project", ""), status=meta.get("status", ""),
                               tags=meta.get("tags", ""), weight=1.0)
                          for h, b in split_chunks(body, Path(rel).stem, cfg)]
                add_file(con, rel, "private", st.st_mtime, st.st_size, 1.0, 0, title, chunks)
                stats["private"] += 1
    gone = set(known) - seen
    if known and len(gone) > max(20, len(known) * 0.2) and not cfg.get("_rebuild"):
        stats["errors"].append("refused to remove many private notes (vault looks incomplete)")
    else:
        for path in gone:
            remove_file(con, path)
    con.commit()
    con.close()


# ---------- entry point ----------

def run(cfg, rebuild=False):
    if not cfg["vault"].is_dir() or not (cfg["vault"] / "CLAUDE.md").exists():
        raise SystemExit(f"Vault not found or not synced: {cfg['vault']}. Nothing changed.")
    cfg["db"].parent.mkdir(parents=True, exist_ok=True)
    with index_lock(cfg):
        want = cfg.get("store_text_once")
        return _run(cfg, rebuild or not schema_ok(cfg["db"], want) or not schema_ok(cfg["private"]["db"], want)
                    or _settings_changed(cfg))


class index_lock:
    """One writer at a time (updates and Haiku cards share it). A lock older than an hour is from a crash."""
    def __init__(self, cfg):
        self.path = Path(str(cfg["db"]) + ".lock")

    def __enter__(self):
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.time() - self.path.stat().st_mtime < 3600:
                raise SystemExit("Another update is running (data/engram.sqlite.lock). Nothing changed.")
            self.path.unlink()
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return self

    def __exit__(self, *a):
        self.path.unlink(missing_ok=True)


# Every setting that changes what goes into the index. When any of them changes, the next update rebuilds by itself.
INDEX_SETTINGS = ["skip_dirs", "exclude_paths", "max_file_bytes", "chunk_max_chars", "chunk_min_chars",
                  "chunk_overlap_chars", "evergreen_paths", "evergreen_exclude", "status_weights", "hide_status",
                  "skip_markers", "path_weights", "type_weights", "redact_patterns", "callouts", "shelves",
                  "store_text_once"]


def _settings_sig(cfg):
    sig = {k: cfg.get(k) for k in INDEX_SETTINGS}
    sig["conversations_path"] = cfg.get("conversations", {}).get("path")
    sig["private"] = {k: cfg.get("private", {}).get(k) for k in ("enabled", "paths", "id_patterns")}
    return json.dumps(sig, sort_keys=True, default=str)


def _settings_changed(cfg):
    if not cfg["db"].exists():
        return False
    import sqlite3
    c = sqlite3.connect(cfg["db"])
    try:
        row = c.execute("SELECT v FROM meta WHERE k='index_settings'").fetchone()
    except sqlite3.Error:
        row = None
    c.close()
    return (row[0] if row else None) != _settings_sig(cfg)


def tidy(con, cfg, stats):
    """Self-tidying: after changes, merge the search index's small pieces at most once a week,
    so it never slowly gets slower. Cheap at this size (a second or two)."""
    last = con.execute("SELECT v FROM meta WHERE k='last_tidy'").fetchone()
    every = cfg.get("tidy_every_days", 7) * 86400
    if (stats["indexed"] or stats["removed"]) and (not last or time.time() - float(last[0]) > every):
        for table in TABLES.values():
            con.execute(f"INSERT INTO {table}({table}) VALUES('optimize')")
        con.execute("PRAGMA optimize")
        con.execute("INSERT OR REPLACE INTO meta VALUES('last_tidy',?)", (str(time.time()),))
        stats["tidied"] = True


def common_terms(con, cfg, stats):
    """Automatic common-word list. Only once the index is big (common_words.min_sections): words found in
    more than common_words.doc_share of all main-shelf sections are skipped in searches, because at that size
    they cost a lot of time and say almost nothing. Below the size, the list stays empty."""
    cw = cfg.get("common_words", {})
    n = con.execute("SELECT COUNT(*) FROM chunks c JOIN files f ON f.path=c.file_path WHERE f.shelf='main'").fetchone()[0]
    terms = []
    if cw.get("enabled", True) and n >= cw.get("min_sections", 200000):
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_vocab USING fts5vocab(fts, 'row')")
        limit = n * cw.get("doc_share", 0.25)
        terms = [t for (t,) in con.execute("SELECT term FROM fts_vocab WHERE doc > ?", (limit,))]
    con.execute("INSERT OR REPLACE INTO meta VALUES('common_terms',?)", (json.dumps(terms),))
    stats["common_terms"] = len(terms)


def _saved(path):
    """Paid Haiku cards and months of usage counts, read from the current index so a rebuild keeps them."""
    import sqlite3
    out = {"cards": [], "chat_cards": [], "usage": []}
    if not Path(path).exists():
        return out
    old = sqlite3.connect(path)
    for key, sql in (("cards", "SELECT hash,context,summary,questions,atoms,model,created_at FROM cards"),
                     ("chat_cards", "SELECT path,fhash,summary,atoms,topic,value,has_decision,model,created_at FROM chat_cards"),
                     ("usage", "SELECT path, shown, opened, last_ts FROM usage")):
        try:
            out[key] = old.execute(sql).fetchall()
        except Exception:
            pass
    old.close()
    return out


def _swap(new, real):
    """Put a finished rebuild in place of the old index in one step. Until this moment the old index stays
    untouched and searchable, so a crash or Ctrl-C during a rebuild loses nothing."""
    import sqlite3
    c = sqlite3.connect(new)
    c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    c.close()
    for suffix in ("-wal", "-shm"):
        Path(str(real) + suffix).unlink(missing_ok=True)
    os.replace(new, real)
    for suffix in ("-wal", "-shm"):
        Path(str(new) + suffix).unlink(missing_ok=True)


def _run(cfg, rebuild):
    if not rebuild:
        return _build(cfg, False, None)
    real_db, real_priv = cfg["db"], cfg["private"]["db"]
    new_db, new_priv = Path(str(real_db) + ".new"), Path(str(real_priv) + ".new")
    for p in (new_db, new_priv):
        for suffix in ("", "-wal", "-shm"):
            Path(str(p) + suffix).unlink(missing_ok=True)
    work = dict(cfg, db=new_db)
    work["private"] = dict(cfg["private"], db=new_priv)
    stats = _build(work, True, _saved(real_db))
    _swap(new_db, real_db)
    if new_priv.exists():
        _swap(new_priv, real_priv)
    return stats


def _build(cfg, rebuild, saved):
    cfg["_rebuild"] = rebuild
    con = connect(cfg["db"], text_once=cfg.get("store_text_once"))
    con.execute("INSERT OR REPLACE INTO meta VALUES('index_settings',?)", (_settings_sig(cfg),))
    if saved:
        con.executemany("INSERT OR IGNORE INTO cards VALUES(?,?,?,?,?,?,?)", saved["cards"])
        con.executemany("INSERT OR IGNORE INTO chat_cards VALUES(?,?,?,?,?,?,?,?,?)", saved["chat_cards"])
        con.executemany("INSERT OR IGNORE INTO usage VALUES(?,?,?,?)", saved["usage"])
    redact = make_redactor(cfg)
    stats = dict(indexed=0, unchanged=0, removed=0, ignored=0, too_big=0, hidden=0,
                 skipped_marker=0, private=0, conflicts=0, unreadable=0, rebuilt=rebuild, errors=[])
    t = time.time()
    ingest_vault(con, cfg, redact, stats)
    ingest_private(cfg, redact, stats)
    con.execute("INSERT OR REPLACE INTO meta VALUES('last_ingest',?)", (str(time.time()),))
    con.execute("INSERT OR REPLACE INTO meta VALUES('last_skipped',?)", (json.dumps(dict(
        conflicts=stats["conflicts"], too_big=stats["too_big"], unreadable=stats["unreadable"],
        marked_skip=stats["skipped_marker"])),))
    count_backlinks(con, cfg)
    tidy(con, cfg, stats)
    common_terms(con, cfg, stats)
    con.commit()
    stats.update(files=con.execute("SELECT COUNT(*) FROM files").fetchone()[0],
                 chunks=con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0],
                 seconds=round(time.time() - t, 1))
    con.close()
    return stats
