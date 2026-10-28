"""Health check per source, doctor style: each line says OK, WARN or FAIL, what is wrong, and the fix."""
import os, time

from .config import api_key
from .db import connect, schema_ok, SCHEMA_VERSION
from .ingest import read_ignore, is_ignored, matches_any, is_conflict


def age(ts):
    if ts is None:
        return "never"
    h = (time.time() - ts) / 3600
    return f"{h * 60:.0f} min ago" if h < 1 else f"{h:.1f} h ago" if h < 48 else f"{h / 24:.0f} days ago"


def check(cfg):
    """Returns (checks, problems). checks = [{area, status, detail, fix}]."""
    out = []
    add = lambda area, status, detail, fix="": out.append(dict(area=area, status=status, detail=detail, fix=fix))

    if not cfg["db"].exists():
        add("Index", "FAIL", "not built yet", "Update index")
        return out, [c for c in out if c["status"] == "FAIL"]
    if not schema_ok(cfg["db"]):
        add("Index", "FAIL", f"old format (needs version {SCHEMA_VERSION})", "Update index (it rebuilds itself)")
        return out, [c for c in out if c["status"] == "FAIL"]
    con = connect(cfg["db"])
    q = lambda sql, *a: con.execute(sql, a).fetchone()[0]

    last = con.execute("SELECT v FROM meta WHERE k='last_ingest'").fetchone()
    last = float(last[0]) if last else None
    stale = last is None or time.time() - last > 24 * 3600
    add("Index", "WARN" if stale else "OK", f"last update {age(last)}, {q('SELECT COUNT(*) FROM chunks'):,} sections",
        "Update index" if stale else "")

    # speed: time a few real searches; warn when the index has grown slow
    from .search import search
    probes = ["what did we decide about the website", "server version", "client email rules",
              "how does the backup work", "notes from this week", "project paused",
              "writing rules", "price list", "sync settings", "weekly report"]
    times = []
    for pq in probes:
        t0 = time.perf_counter()
        search(cfg, pq, con=con, private=False)
        times.append((time.perf_counter() - t0) * 1000)
    times.sort()
    med, worst = times[len(times) // 2], times[-1]
    limit = cfg.get("speed_warn_ms", 300)
    try:  # best effort: never make the health check fail because an update is writing
        con.execute("INSERT OR REPLACE INTO meta VALUES('last_speed_ms',?)", (f"{med:.1f}",))
        con.commit()
    except Exception:
        pass
    add("Speed", "WARN" if med > limit else "OK", f"search takes {med:.0f} ms (slowest probe {worst:.0f} ms, "
        f"warning above {limit} ms)", "The vault has grown: check the big-vault switches in config.json"
        if med > limit else "")

    # vault
    vault = cfg["vault"]
    if not vault.is_dir() or not (vault / "CLAUDE.md").exists():
        add("Vault", "FAIL", "folder not found or not synced", "Check the folder path in ENGRAM_VAULT and that your sync app is running")
    else:
        pats, on_disk, newest = read_ignore(vault), 0, 0
        for root, dirs, files in os.walk(vault):
            dirs[:] = [d for d in dirs if d not in cfg["skip_dirs"]]
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, vault)
                if (f.lower().endswith(".md") and not is_conflict(f) and not is_ignored(rel, pats)
                        and not matches_any(rel, cfg["exclude_paths"])
                        and os.path.getsize(full) <= cfg["max_file_bytes"]):
                    on_disk += 1
                    newest = max(newest, os.path.getmtime(full))
        indexed = q("SELECT COUNT(*) FROM files WHERE source='vault'")
        drift = on_disk - indexed
        bad = abs(drift) > max(5, on_disk * 0.01)
        add("Vault", "WARN" if bad else "OK", f"{indexed:,} of {on_disk:,} notes indexed, newest edit {age(newest)}",
            "Update index" if bad else "")
        hidden = q("SELECT COUNT(*) FROM files WHERE hidden=1")
        add("Vault", "OK", f"{hidden} notes hidden (superseded or expired)")
        if newest and time.time() - newest > 3 * 86400:
            add("Vault", "WARN", "no note changed in 3 days", "Check that your sync app is on")

    # files left out on purpose, so anything odd is visible here and not in search
    sk = con.execute("SELECT v FROM meta WHERE k='last_skipped'").fetchone()
    if sk:
        import json as _json
        d = _json.loads(sk[0])
        parts = [f"{d[k]} {label}" for k, label in (("conflicts", "sync conflict copies"), ("too_big", "too big (over 2 MB)"),
                 ("unreadable", "unreadable (not text)"), ("marked_skip", "marked engram: skip")) if d.get(k)]
        add("Skipped", "OK", ("left out on purpose: " + ", ".join(parts)) if parts else "nothing odd left out")

    # privacy
    likes = " OR ".join("path LIKE ?" for _ in cfg["private"]["paths"]) or "0"
    leaked = q(f"SELECT COUNT(*) FROM files WHERE {likes} OR path LIKE '%.env%'",
               *[p.rstrip("/") + "/%" for p in cfg["private"]["paths"]])
    add("Privacy", "FAIL" if leaked else "OK", f"{leaked} private files in the index",
        "Delete data/engram.sqlite and update" if leaked else "")

    # private folders (finances)
    pcfg = cfg["private"]
    if pcfg["enabled"]:
        if not pcfg["db"].exists():
            add("Private", "WARN", "private index not built yet", "Update index")
        else:
            import re, sqlite3
            pcon = sqlite3.connect(pcfg["db"])
            n_files = pcon.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            rx = [re.compile(p) for p in pcfg["id_patterns"]]
            ids_left = sum(1 for (b,) in pcon.execute("SELECT body FROM chunks") if any(r.search(b) for r in rx))
            cards_left = pcon.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
            pcon.close()
            ok = ids_left == 0 and cards_left == 0
            add("Private", "OK" if ok else "FAIL",
                f"{n_files} private notes searchable (where only), {ids_left} sections with ID numbers, "
                f"{cards_left} sent to Haiku", "" if ok else "Delete data/private.sqlite and update")

    # AI conversations
    conv = cfg["conversations"]
    n_chats = q("SELECT COUNT(*) FROM files WHERE source='chat'")
    if not (vault / conv["path"]).is_dir():
        add("AI conversations", "OK", f"folder {conv['path']} not created yet (optional)")
    else:
        cutoff = time.time() - conv["expire_days"] * 86400
        old = q("SELECT COUNT(DISTINCT f.path) FROM files f JOIN chunks c ON c.file_path=f.path "
                "WHERE f.source='chat' AND f.keep=0 AND c.date < ?", cutoff)
        kept = q("SELECT COUNT(*) FROM files WHERE source='chat' AND keep=1")
        carded = q("SELECT COUNT(*) FROM files f JOIN chat_cards k ON k.path=f.path AND k.fhash=f.fhash "
                   "WHERE f.source='chat'")
        add("AI conversations", "OK", f"{n_chats} chats indexed, {kept} marked keep, about {old} past "
            f"{conv['expire_days'] // 30} months (out of search unless high value or a decision), "
            f"{carded} with a Haiku chat card")

    # cards
    eligible = q(f"SELECT COUNT(DISTINCT c.hash) FROM chunks c JOIN files f ON f.path=c.file_path "
                 f"WHERE f.hidden=0 AND f.source IN ({','.join(repr(s) for s in cfg['cards']['sources'])})")
    have = q("SELECT COUNT(DISTINCT c.hash) FROM chunks c JOIN cards k ON k.hash=c.hash")
    fake = q("SELECT COUNT(*) FROM cards WHERE model='fake'")
    pct = have / eligible * 100 if eligible else 0
    if have == 0:
        add("Haiku cards", "OK", "none yet (optional step)", "Make cards when ready")
    else:
        add("Haiku cards", "OK" if pct > 95 else "WARN", f"{have:,} of {eligible:,} sections have a card ({pct:.0f}%)"
            + (f", {fake} are fake test cards" if fake else ""), "" if pct > 95 else "Make cards for the rest")
        if os.environ.get("ENGRAM_DATA"):
            # On the server the web page runs WITHOUT the API key on purpose (see entrypoint.sh), so looking for
            # the key here would always fail. Judge the card maker by its work instead: when was the last real card?
            if fake < have and have < eligible:
                last_card = q("SELECT MAX(created_at) FROM cards WHERE model != 'fake'")
                quiet_h = cfg["cards"].get("quiet_warn_hours", 2)
                if last_card is None or time.time() - last_card > quiet_h * 3600:
                    add("Haiku cards", "WARN", f"no new card in the last {quiet_h} h (last one {age(last_card)})",
                        "Check ANTHROPIC_API_KEY in your settings")
                else:
                    add("Haiku cards", "OK", f"card maker working, last new card {age(last_card)}")
        elif not api_key() and fake < have:
            add("Haiku cards", "WARN", "no API key found for new cards", "Add ANTHROPIC_API_KEY to engram-test/.env")

    # learning from use
    from .usage import status as usage_status
    u = usage_status(cfg, con)
    add("Learning from use", "OK", f"{u['opens']} opens counted over {u['notes']} notes; "
        + ("on" if u["active"] else f"off until {u['needed']} opens (it needs real use first)"))

    problems = [c for c in out if c["status"] == "FAIL"]
    return out, problems


def lines(checks):
    return [f"{c['status']:<4}  {c['area']}: {c['detail']}" + (f"  (fix: {c['fix']})" if c["fix"] else "") for c in checks]
