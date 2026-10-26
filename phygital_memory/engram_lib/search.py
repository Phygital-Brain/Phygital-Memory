"""Search.

Ranked: BM25 over title, heading path, tags, body and Haiku card text,
        x folder weight x recency boost (evergreen notes never fade). Hidden notes are left out.
Exact:  quoted text and code-like terms (versions, IDs, paths, error codes) are also matched
        letter for letter, and those hits come first. Plain-search quality for exact things.
Results are short (path, heading, snippet). get() returns the full section or note on request.

Any question text is safe: it is reduced to plain words, so FTS5 syntax can never break the query.
"""
import json, math, re, time

from .db import connect, text_once
from . import usage

STOP = set("""a an the and or but if of to in on at by for with from as is are was were be been it its this that these
those i me my we our you your do does did how what which who whom when where why can could should would will shall
about into than then so not no yes any all some there here has have had get got am check show tell find please""".split())

COLS = "{title heading tags body}"  # every column except card
# Matching words in snippets are wrapped in these two invisible marks (not [ ], which Obsidian uses for [[links]]).
# The app turns them into highlights; the command line shows them as [ ].
HL_OPEN, HL_CLOSE = "\x02", "\x03"


def words(q):
    return [w for w in re.findall(r"\w+", q.lower()) if w not in STOP and len(w) > 1]


def stems(con, ws):
    """The index's own root form of each word ('dashes' -> 'dash'), using a tiny temporary index with the
    same rules, so the common-word list and the question always agree."""
    con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.qtok USING fts5(x, tokenize='porter unicode61 remove_diacritics 2')")
    con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.qtok_v USING fts5vocab(temp, qtok, 'instance')")
    con.execute("DELETE FROM temp.qtok")
    con.executemany("INSERT INTO temp.qtok(rowid, x) VALUES(?, ?)", list(enumerate(ws, 1)))
    out = {doc: term for term, doc in con.execute("SELECT term, doc FROM temp.qtok_v")}
    return [out.get(i, w) for i, w in enumerate(ws, 1)]


def folder_hints(cfg, q):
    """Folders the question points at ("check my decisions" -> the decisions folder, "what did I do with X" -> clients).
    Notes in those folders count more (a boost, not a filter, so a wrong guess never hides the right note).
    Rules live in config.json under folder_hints."""
    h = cfg.get("folder_hints") or {}
    low = q.lower()
    out = []
    for rule in h.get("rules", []):
        if re.search(rule["when"], low):
            out += rule["folders"]
    return out, h.get("boost", 1.0)


def build_query(q, use_cards=True, mode="or", common=None, con=None):
    """mode 'or': any word (best ranking). mode 'and': every word (fast and precise, used for the background
    shelf). Common words (only listed once the index is big) are left out, unless that would leave nothing."""
    ws = words(q)
    if not ws:
        return None
    if common and con is not None:
        kept = [w for w, s in zip(ws, stems(con, ws)) if s not in common]
        ws = kept or ws
    terms = [f'"{w}"' for w in ws]
    if mode == "and":
        expr = " AND ".join(terms)
    else:
        phrases = [f'"{a} {b}"' for a, b in zip(ws, ws[1:])]  # neighbouring words together score higher
        expr = " OR ".join(terms + phrases)
    return expr if use_cards else f"{COLS} : ({expr})"


def snippet_multi(body, q, width=240):
    """Short piece of text around the first matching word, with the matching words in [brackets].
    Built in Python, so it works when the index keeps no copy of the text."""
    ws = [w for w in words(q) if len(w) > 2]
    low = body.lower()
    pos = [low.find(w[:5]) for w in ws]
    pos = [p for p in pos if p >= 0]
    start = max(0, min(pos) - width // 3) if pos else 0
    s = body[start:start + width]
    for w in sorted(set(ws), key=len, reverse=True):
        s = re.sub(r"(?i)\b(" + re.escape(w[:5]) + r"\w*)", HL_OPEN + r"\1" + HL_CLOSE, s)
    s = re.sub(HL_OPEN + "+", HL_OPEN, re.sub(HL_CLOSE + "+", HL_CLOSE, s))
    return ("... " if start else "") + s


def exact_terms(q):
    """Quoted phrases, plus tokens that look like versions, IDs, paths, hostnames or error codes."""
    quoted = [m.strip() for m in re.findall(r'"([^"]{2,})"', q)]
    rest = re.sub(r'"[^"]*"', " ", q)
    codes = [t.strip(".,;:!?()[]'") for t in rest.split()]
    codes = [t for t in codes if len(t) >= 3 and (re.search(r"\d", t) or re.search(r"[._/@:\-]\w", t))]
    seen, out = set(), []
    for t in quoted + codes:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def make_snippet(body, term, width=240):
    i = body.lower().find(term.lower())
    if i < 0:
        return body[:width]
    start = max(0, i - width // 3)
    s = body[start:start + width]
    j = s.lower().find(term.lower())
    s = s[:j] + HL_OPEN + s[j:j + len(term)] + HL_CLOSE + s[j + len(term):]
    return ("... " if start else "") + s


def _row(r, score, exact=False, snippet=None):
    cid, path, head, date, src, w, ev, keep, linked, s, snip, body = r
    return dict(id=cid, score=round(score, 3), path=path, heading=head, source=src, date=date,
                exact=exact, snippet=(snippet or snip or body[:240]).replace("\n", " ")[:300], body=body)


def chat_factors(cfg, con):
    """Per-chat info from the Haiku chat cards, plus which chats are the newest on their topic."""
    info = {}
    for path, topic, value, dec in con.execute("SELECT path, topic, value, has_decision FROM chat_cards"):
        info[path] = dict(topic=(topic or "").strip().lower(), value=(value or "medium").lower(), decision=bool(dec))
    newest = {}
    for path, date in con.execute("SELECT c.file_path, MAX(c.date) FROM chunks c JOIN files f ON f.path=c.file_path "
                                  "WHERE f.source='chat' GROUP BY c.file_path"):
        t = info.get(path, {}).get("topic")
        if t:
            newest[t] = max(newest.get(t, 0), date)
    return info, newest


def chat_weight(cfg, path, date, keep, linked, info, newest, now):
    """How much one AI conversation counts right now, or None if it has expired.
    Age steps (half, then a quarter, then out), keep: true never fades, high value ages slower,
    a decision or fix stays longer, a link to a vault note or a newer chat on the same topic counts less."""
    c = cfg["conversations"]
    if keep:
        return c["keep_weight"]
    meta = info.get(path, {})
    age = max(0.0, (now - date) / 86400)
    if meta.get("value") == "high":
        age *= c["high_value_ages_at"]
    expire = c["expire_days"] * (c["decision_expire_factor"] if meta.get("decision") else 1)
    if age > expire:
        return None
    steps = [wt for start, wt in sorted(c["age_steps"]) if age >= start]
    w = steps[-1] if steps else sorted(c["age_steps"])[0][1]
    w *= c["value_factor"].get(meta.get("value", "medium"), 1.0)
    if meta.get("decision"):
        w *= c["decision_factor"]
    if linked:
        w *= c["linked_note_factor"]
    t = meta.get("topic")
    if t and newest.get(t, 0) > date + 86400:
        w *= c["superseded_factor"]
    return w


PRIVATE_NOTE = "Private. Open only when the person asks about this."


def backlink_factors(cfg, con):
    """1 + boost x (how linked the note is, on a log scale, full at cap links). Empty when switched off."""
    b = cfg.get("backlinks", {})
    if not b.get("enabled"):
        return {}
    cap, boost = b.get("cap", 30), b.get("boost", 0.2)
    return {p: 1 + boost * min(1.0, math.log1p(n) / math.log1p(cap)) for p, n in con.execute("SELECT path, n FROM backlinks")}


def tail_slots(n, n_main, n_extra, cap):
    """How many places extras (background shelf, private notes, chats) get after the main notes:
    at most cap and never more than half the list, unless the main notes did not fill it."""
    return min(n_extra, max(n - n_main, min(cap, n // 2)))


def search(cfg, q, n=None, recency=True, weights=True, source=None, use_cards=True, exact=True,
           include_hidden=False, with_body=False, con=None, private=True, log=False):
    """The notes, plus the private index (finances). Private matches come back
    as WHERE only: path and heading, no snippet, no text, id prefixed with 'p'."""
    n = n or cfg["results_default"]
    con = con or connect(cfg["db"])
    has_chats = con.execute("SELECT 1 FROM files WHERE source='chat' LIMIT 1").fetchone() is not None
    chat_info = chat_factors(cfg, con) if has_chats else ({}, {})  # worked out once per search, not per query
    row = con.execute("SELECT v FROM meta WHERE k='common_terms'").fetchone()
    common = set(json.loads(row[0])) if row else set()  # stays empty until the index is big
    use_f = usage.factors(cfg, con) if weights else {}  # empty until there is enough real use
    back_f = backlink_factors(cfg, con) if weights else {}
    run = lambda src, k: _search(cfg, q, k, recency, weights, src, use_cards, exact, include_hidden, with_body, con,
                                 chat_info, common=common, use_f=use_f, back_f=back_f)
    if source == "private":
        rows = []
    elif source is None and has_chats:  # notes and chats fetched apart, so a few chats can always follow the notes
        rows = [r for r in run(None, n) if r["source"] != "chat"] + run("chat", cfg["conversations"]["max_in_results"])
    else:
        rows = run(source, n)
    chats_first = [r for r in rows if r["source"] == "chat"]  # kept apart so the back shelf cannot push them out
    rows = _add_background(cfg, q, n, [r for r in rows if r["source"] != "chat"], recency, weights, source, use_cards,
                           exact, include_hidden, with_body, con, chat_info) + chats_first
    pcfg = cfg.get("private", {})
    if private and pcfg.get("enabled") and pcfg["db"].exists() and source in (None, "private"):
        # Private matches say WHERE only, and come after the normal notes (at most a few, one per file):
        # their scores come from a much smaller index and are not comparable with the main notes' scores.
        pcon = connect(pcfg["db"])
        priv, seen = [], set()
        # every word of the question must be in the private note, so unrelated questions show no finance notes
        for r in _search(cfg, q, n, recency, False, None, False, False, True, False, pcon, ({}, {}), qmode="and"):
            if r["path"] in seen:
                continue
            seen.add(r["path"])
            priv.append(dict(id=f"p{r['id']}", score=r["score"], path=r["path"], heading=r["heading"],
                             source="private", date=r["date"], exact=r["exact"], private=True,
                             snippet=PRIVATE_NOTE))
        pcon.close()
        if source == "private" or not rows:
            return priv[:n]
        k = tail_slots(n, len(rows), len(priv), pcfg.get("max_in_results", 2))
        chats_now = [r for r in rows if r["source"] == "chat"]
        notes_now = [r for r in rows if r["source"] != "chat"]
        rows = notes_now[:n - k] + priv[:k] + chats_now
    # AI conversations come after the vault notes, at most a few, unless nothing else matched
    chats = [r for r in rows if r["source"] == "chat"]
    others = [r for r in rows if r["source"] != "chat"]
    if source == "chat" or not others:
        final = chats[:n]
    else:
        k = tail_slots(n, len(others), len(chats), cfg["conversations"]["max_in_results"])
        final = others[:n - k] + chats[:k]
    if log:  # only real searches (app, command line, Claude's tool) are remembered, never tests
        usage.record_shown(cfg, [r["path"] for r in final if not r.get("private")], con)
    return final


FOLDER_LABELS = {"*CLAUDE.md": "rule file", "*AGENTS.md": "rule file", "Context/*": "Context",
                 "*/archive/*": "archive", "archive/*": "archive", "*/decisions/*": "decision", "Library/*": "library"}


def why(cfg, q, r, exact_hits, status, typ, table, use_f, back_f, info, newest):
    """A short plain line saying why a result came back, built from the same facts the ranking used."""
    from .ingest import matches_any
    path, date, src, ev, keep = r[1], r[3], r[4], r[6], r[7]
    out = []
    if exact_hits:
        out.append("exact match")
    ws = {w[:5] for w in words(q)}
    if ws and any(w[:5] in ws for w in words(r[2])):
        out.append("your words in the heading")
    if src == "chat":
        meta = info.get(path, {})
        out.append("AI conversation" + (f", {meta['value']} value" if meta.get("value") else "")
                   + (", kept" if keep else ""))
    else:
        rule = next((x for x in cfg["path_weights"] if matches_any(path, [x["match"]])), None)
        if rule:
            label = FOLDER_LABELS.get(rule["match"], rule["match"].rstrip("/*"))
            out.append(label if rule["weight"] == 1 else f"{label} ({rule['weight']:g}x)")
        sw = cfg["status_weights"].get((status or "").lower())
        if sw:
            out.append(f"status {status} ({sw:g}x)")
        tw = cfg.get("type_weights", {}).get((typ or "").lower())
        if tw:
            out.append(f"{typ} note ({tw:g}x)")
    if table == "fts_bg":
        out.append("back shelf")
    if ev:
        out.append("never fades")
    else:
        days = max(0, (time.time() - date) / 86400)
        out.append("from today" if days < 1 else f"{days:.0f} days old" if days < 60 else f"{days / 30:.0f} months old")
    n_links = back_f and back_f.get(path)
    if n_links and n_links > 1.0:
        out.append("linked from many notes" if n_links >= 1.05 else "linked from other notes")
    u = use_f and use_f.get(path)
    if u:
        out.append("you open it often" if u > 1 else "shown often, rarely opened")
    return " · ".join(out)


def _add_background(cfg, q, n, rows, recency, weights, source, use_cards, exact, include_hidden, with_body, con,
                    chat_info):
    """Two shelves. The background shelf (archives, copied code) is searched apart from the main notes.
    mode 'after': background results follow the main ones, at most max_in_results, more only if the main
    shelf found little. mode 'merge': everything is ranked together. The background is searched with
    'every word' by default, which stays fast even when that shelf is huge."""
    sh = cfg.get("shelves", {})
    if not sh.get("enabled") or source in ("private", "chat", "session"):
        return rows
    args = (recency, weights, source, use_cards, exact, include_hidden, with_body, con, chat_info)
    bg = _search(cfg, q, n, *args, table="fts_bg", qmode=sh.get("background_query", "and"))
    if not bg and sh.get("background_query", "and") == "and" and len(rows) < n:
        bg = _search(cfg, q, n, *args, table="fts_bg", qmode="or")  # nothing with every word: try any word
    if sh.get("mode", "after") == "merge":
        return sorted(rows + bg, key=lambda r: r["score"], reverse=True)[:n]
    k = tail_slots(n, len(rows), len(bg), sh.get("max_in_results", 3))
    return rows[:n - k] + bg[:k]


def _search(cfg, q, n, recency, weights, source, use_cards, exact, include_hidden, with_body, con, chat_info,
            table="fts", qmode="or", common=None, use_f=None, back_f=None):
    """Two steps, for speed: first rank on small facts only (id, scores, weights, dates), then build snippets
    and fetch text for the few results that are actually shown."""
    # expiry dates are checked at search time, so a note hides itself the day its valid_until passes
    where = "" if include_hidden else f" AND f.hidden = 0 AND (f.until IS NULL OR f.until > {time.time():.0f})"
    src = [source] if source else []
    if source:
        where += " AND f.source = ?"
    cols = "c.id, c.file_path, c.heading, c.date, f.source, c.weight, c.evergreen, f.keep, f.linked"
    frm = (f"FROM {table} JOIN chunks c ON c.id = {table}.rowid JOIN files f ON f.path = c.file_path "
           f"WHERE {table} MATCH ?")
    boost, now = cfg["recency"]["boost"], time.time()
    info, newest = chat_info
    hint_folders, hint_boost = folder_hints(cfg, q) if weights else ([], 1.0)
    if hint_folders:
        from .ingest import matches_any

    def mult(r):
        """Score multiplier for one row, or None if the row should not be shown (expired chat)."""
        path, date, src, w, ev, keep, linked = r[1], r[3], r[4], r[5], r[6], r[7], r[8]
        is_chat = src == "chat"
        half = cfg["conversations"]["half_life_days"] if is_chat and not keep else cfg["recency"]["half_life_days"]
        m = 1.0
        if is_chat:  # chats always follow their own rules, even in plain mode, so they never outrank notes by accident
            cw = chat_weight(cfg, path, date, keep, linked, info, newest, now)
            if cw is None and not include_hidden:
                return None
            m *= cw or 0.05
        if recency:
            age = 0.0 if ev else max(0.0, (now - date) / 86400)
            m *= 1 + boost * math.exp(-age * math.log(2) / half)
        if weights and not is_chat:
            m *= w
        if weights and use_f:  # learning from use (empty until there is enough real use)
            m *= use_f.get(path, 1.0)
        if weights and back_f:  # notes many other notes link to count a bit more
            m *= back_f.get(path, 1.0)
        if hint_folders and not is_chat and matches_any(path, hint_folders):
            m *= hint_boost
        return m

    cand = {}  # id -> [facts row, score, exact hits, exact term]

    # 1. ranked keyword search, on small facts only
    query = build_query(q, use_cards, qmode, common, con)
    if query:
        for r in con.execute(f"SELECT {cols}, bm25({table}, 4.0, 3.0, 2.0, 1.0, 2.0) {frm}{where} ORDER BY 10 LIMIT 300",
                             [query] + src):
            m = mult(r)
            if m is not None:
                cand[r[0]] = [r, -r[9] * m, 0, None]

    # 2. exact matches: found through the index (fast), then checked letter for letter.
    #    They get a strong boost instead of always jumping to the top (always-first scored worse in tests).
    terms = exact_terms(q) if exact else []
    if terms:
        top = max((c[1] for c in cand.values()), default=1.0)
        boost_x = cfg.get("exact_boost", 1.0)
        for t in terms:
            toks = re.findall(r"\w+", t.lower())
            if not toks:
                continue
            phrase = '"' + " ".join(toks) + '"'
            for r in con.execute(f"SELECT {cols}, 0, c.heading || ' ' || c.body {frm}{where} LIMIT 300", [phrase] + src):
                if t.lower() not in r[10].lower():
                    continue
                if r[0] in cand:
                    cand[r[0]][2] += 1
                    cand[r[0]][3] = cand[r[0]][3] or t
                else:
                    m = mult(r)
                    if m is not None:
                        cand[r[0]] = [r[:10], top * 0.5 * m, 1, t]
        for c in cand.values():
            if c[2]:
                c[1] *= 1 + boost_x * c[2]

    # 3. pick the shown results (at most 2 per note), then build snippets and fetch text only for those
    cap, per_file, chosen = cfg["max_chunks_per_file_in_results"], {}, []
    for c in sorted(cand.values(), key=lambda c: c[1], reverse=True):
        path = c[0][1]
        if per_file.get(path, 0) >= cap:
            continue
        per_file[path] = per_file.get(path, 0) + 1
        chosen.append(c)
        if len(chosen) == n:
            break
    if not chosen:
        return []
    ids = [c[0][0] for c in chosen]
    marks = ",".join("?" * len(ids))
    extra = {i: (b, st, ty) for i, b, st, ty in
             con.execute(f"SELECT id, body, status, type FROM chunks WHERE id IN ({marks})", ids)}
    bodies = {i: v[0] for i, v in extra.items()}
    snips = {}
    if query and not text_once(con):
        snips = dict(con.execute(f"SELECT rowid, snippet({table}, 3, char(2), char(3), ' ... ', 32) FROM {table} "
                                 f"WHERE {table} MATCH ? AND rowid IN ({marks})", [query] + ids))
    final = []
    for r, score, k, term in chosen:
        body = bodies.get(r[0], "")
        snip = make_snippet(body, term) if term else (snips.get(r[0]) or snippet_multi(body, q))
        row = _row(tuple(r[:9]) + (0, snip, body), score, bool(k))
        _, st, ty = extra.get(r[0], ("", "", ""))
        row["why"] = why(cfg, q, r, k, st, ty, table, use_f, back_f, info, newest)
        if not with_body:
            row.pop("body", None)
        final.append(row)
    return final


def get(cfg, chunk_id, whole_note=False, con=None, allow_private=False, log=False):
    """Full text of one section, or of the whole note (sections in order). Short notes come back whole.
    Private ids ('p...') stay locked unless allow_private is set, which an AI app does only when the person asked."""
    cid = str(chunk_id)
    if cid.startswith("p"):
        pdb = cfg["private"]["db"]
        if not pdb.exists():
            return None
        pcon = connect(pdb)
        head = pcon.execute("SELECT file_path, heading FROM chunks WHERE id=?", (int(cid[1:]),)).fetchone()
        if not head:
            return None
        if not allow_private:
            return dict(id=cid, path=head[0], heading=head[1], private=True, locked=True, text=None,
                        note=PRIVATE_NOTE)
        r = get(cfg, int(cid[1:]), whole_note, con=pcon)
        r.update(id=cid, private=True, locked=False)
        return r
    con = con or connect(cfg["db"])
    row = con.execute("SELECT file_path, heading, body FROM chunks WHERE id=?", (int(chunk_id),)).fetchone()
    if not row:
        return None
    path, head, body = row
    if log:  # a real open: learning from use counts it (tests never log)
        usage.record_open(cfg, path, con)
    parts = con.execute("SELECT heading, body FROM chunks WHERE file_path=? ORDER BY ordinal", (path,)).fetchall()
    total = sum(len(b) for _, b in parts)
    if whole_note or total <= 4000:
        text = "\n\n".join(f"## {h}\n{b}" for h, b in parts)
        return dict(id=chunk_id, path=path, heading=head, whole_note=True, text=text)
    return dict(id=chunk_id, path=path, heading=head, whole_note=False, text=f"## {head}\n{body}")


def around(cfg, chunk_id, con=None, same_day=5):
    """What's around a result: the sections just before and after it in the same note, and other notes
    from the same day (path and heading only). Private results have no surroundings."""
    if str(chunk_id).startswith("p"):
        return None
    con = con or connect(cfg["db"])
    row = con.execute("SELECT c.file_path, c.ordinal, c.heading, c.date, f.source FROM chunks c "
                      "JOIN files f ON f.path = c.file_path WHERE c.id=?", (int(chunk_id),)).fetchone()
    if not row:
        return None
    path, ordinal, head, date, source = row
    near = con.execute("SELECT id, ordinal, heading, body FROM chunks WHERE file_path=? AND ordinal IN (?, ?) "
                       "ORDER BY ordinal", (path, ordinal - 1, ordinal + 1)).fetchall()
    before = [dict(id=i, heading=h, text=b[:600]) for i, o, h, b in near if o < ordinal]
    after = [dict(id=i, heading=h, text=b[:600]) for i, o, h, b in near if o > ordinal]
    day = time.strftime("%Y-%m-%d", time.localtime(date))
    start = time.mktime(time.strptime(day, "%Y-%m-%d"))
    others = con.execute("SELECT c.file_path, MIN(c.id), MIN(c.heading) FROM chunks c JOIN files f ON f.path=c.file_path "
                         "WHERE c.date >= ? AND c.date < ? AND c.file_path != ? AND f.hidden = 0 AND f.source != 'chat' "
                         "GROUP BY c.file_path ORDER BY c.file_path LIMIT ?",
                         (start, start + 86400, path, same_day)).fetchall()
    return dict(id=chunk_id, path=path, heading=head, day=day, before=before, after=after,
                same_day=[dict(path=p, id=i, heading=h) for p, i, h in others])
