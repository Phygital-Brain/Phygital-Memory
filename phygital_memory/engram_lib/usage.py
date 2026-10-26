"""Learning from use. Off until there is enough real use to learn from.

Every real search (from the person or their AI app, never from tests) records which notes were shown, and every
"open the full section" records which note was opened. Only the note's path and a counter are kept, never text.
Counters fade (half every half_life_days), so a note that stopped being useful drops back on its own.

Once the total of real opens reaches min_total_opens:
- a note opened often counts up to open_boost more (1.3x by default),
- a note shown many times but never opened counts a little less (ignored_factor, 0.85x).
"""
import sqlite3, time

from .db import connect


def _decay(value, last, now, half):
    if not last:
        return value
    return value * 0.5 ** (max(0.0, now - last) / (half * 86400))


def _bump(con, cfg, path, col):
    u = cfg.get("usage", {})
    now, half = time.time(), u.get("half_life_days", 90)
    row = con.execute("SELECT shown, opened, last_ts FROM usage WHERE path=?", (path,)).fetchone()
    shown, opened, last = row if row else (0.0, 0.0, None)
    shown, opened = _decay(shown, last, now, half), _decay(opened, last, now, half)
    if col == "shown":
        shown += 1
    else:
        opened += 1
    con.execute("INSERT OR REPLACE INTO usage VALUES(?,?,?,?)", (path, shown, opened, now))


def _write(cfg, paths, col):
    """Best effort, on its own short-lived connection: if an index update is busy writing, this use is simply not
    counted, instead of making the search wait (or fail) behind the update."""
    if not cfg.get("usage", {}).get("enabled", True):
        return
    try:
        c = sqlite3.connect(cfg["db"], timeout=0.3)
        for p in set(paths):
            _bump(c, cfg, p, col)
        c.commit()
        c.close()
    except sqlite3.Error:
        pass


def record_shown(cfg, paths, con=None):
    _write(cfg, paths, "shown")


def record_open(cfg, path, con=None):
    _write(cfg, [path], "opened")


def factors(cfg, con):
    """path -> multiplier, or {} while there is not enough use yet (then nothing changes)."""
    u = cfg.get("usage", {})
    if not u.get("enabled", True):
        return {}
    now, half = time.time(), u.get("half_life_days", 90)
    rows = con.execute("SELECT path, shown, opened, last_ts FROM usage").fetchall()
    total = sum(_decay(o, t, now, half) for _, _, o, t in rows)
    if total < u.get("min_total_opens", 50):
        return {}
    out, boost, full_at = {}, u.get("open_boost", 0.3), u.get("opens_for_full_boost", 5)
    for path, shown, opened, last in rows:
        s, o = _decay(shown, last, now, half), _decay(opened, last, now, half)
        if o >= 0.5:
            out[path] = 1 + boost * min(1.0, o / full_at)
        elif s >= u.get("ignored_after_shown", 20):
            out[path] = u.get("ignored_factor", 0.85)
    return out


def status(cfg, con):
    u = cfg.get("usage", {})
    now, half = time.time(), u.get("half_life_days", 90)
    rows = con.execute("SELECT shown, opened, last_ts FROM usage").fetchall()
    total = sum(_decay(o, t, now, half) for _, o, t in rows)
    return dict(notes=len(rows), opens=round(total, 1), needed=u.get("min_total_opens", 50),
                active=bool(u.get("enabled", True)) and total >= u.get("min_total_opens", 50))
