"""Score the test questions.

A question is answered at rank k if one of its expect_files (or, when it has none, a section
containing one of its expect phrases) is the k-th result. Reported: hit@1, hit@5, hit@10, MRR@10.

tests/questions.json is the tuning set. tests/holdout.json is never used for tuning: it is only
scored with the final setup, to check the tuning did not just fit the tuning set.
Notes only: saved chats can contain these very questions, which would be cheating.
"""
import json, time

from .config import ROOT
from .db import connect
from .search import search

MODES = {
    "plain": dict(recency=False, weights=False, exact=False, use_cards=False),
    "smart": dict(recency=True, weights=True, exact=True, use_cards=False),
    "smart + cards": dict(recency=True, weights=True, exact=True, use_cards=True),
}


def load(name):
    p = ROOT / "tests" / name
    if not p.exists():
        return []
    return [q for q in json.loads(p.read_text()) if not q["q"].startswith("REPLACE")]


def norm(s):
    return " ".join(s.lower().split())


def rank_of(item, rows):
    files = [f.lower() for f in item.get("expect_files", [])]
    phrases = [norm(e) for e in item.get("expect", [])]
    for i, r in enumerate(rows, 1):
        if files and r["path"].lower() in files:
            return i
        if not files and any(p in norm(r["body"]) for p in phrases):
            return i
    return None


def score(cfg, qs, opts, con):
    ranks, misses, kinds, t0 = [], [], {}, time.time()
    for item in qs:
        rows = search(cfg, item["q"], 10, con=con, source="vault", with_body=True, **opts)
        r = rank_of(item, rows)
        ranks.append(r)
        k = kinds.setdefault(item.get("kind", "fact"), [0, 0])
        k[1] += 1
        k[0] += bool(r and r <= 5)
        if not r or r > 5:
            misses.append(dict(q=item["q"], kind=item.get("kind", ""), want=(item.get("expect_files") or [""])[0],
                               got=rows[0]["path"] if rows else "(nothing)", rank=r))
    n = max(1, len(qs))
    hit = lambda k: sum(1 for r in ranks if r and r <= k)
    return dict(total=len(qs), hit1=hit(1), hit5=hit(5), hit10=hit(10),
                mrr=round(sum(1 / r for r in ranks if r) / n, 3), ms_per_q=round((time.time() - t0) * 1000 / n, 1),
                kinds={k: f"{v[0]}/{v[1]}" for k, v in sorted(kinds.items())}, misses=misses)


def run(cfg, verbose=True):
    con = connect(cfg["db"])
    main, hold = load("questions.json"), load("holdout.json")
    has_cards = con.execute("SELECT COUNT(*) FROM cards WHERE model != 'fake'").fetchone()[0] > 0
    modes = {k: v for k, v in MODES.items() if has_cards or not v["use_cards"]}
    result = {"main": {name: score(cfg, main, opts, con) for name, opts in modes.items()}}
    best = list(modes)[-1]
    if hold:
        result["holdout"] = {best: score(cfg, hold, modes[best], con)}
    result["best_mode"] = best
    if verbose:
        print(f"Tuning set: {len(main)} questions")
        print(f"  {'mode':<15} {'hit@1':>6} {'hit@5':>6} {'hit@10':>7} {'MRR':>6}  ms/q")
        for name, s in result["main"].items():
            print(f"  {name:<15} {s['hit1']:>6} {s['hit5']:>6} {s['hit10']:>7} {s['mrr']:>6}  {s['ms_per_q']}")
        b = result["main"][best]
        print(f"  by kind ({best}, hit@5): " + ", ".join(f"{k} {v}" for k, v in b["kinds"].items()))
        if hold:
            h = result["holdout"][best]
            print(f"Holdout ({len(hold)}, never tuned on): hit@1 {h['hit1']}, hit@5 {h['hit5']}, "
                  f"hit@10 {h['hit10']}, MRR {h['mrr']}")
        if b["misses"]:
            print(f"\nNot in top 5 ({best}):")
            for m in b["misses"]:
                print(f"  - [{m['kind']}] {m['q']}\n      want {m['want']}  |  got {m['got']}"
                      + (f"  (it was #{m['rank']})" if m["rank"] else ""))
    out = ROOT / "tests/results" / (time.strftime("%Y-%m-%d-%H%M%S") + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return result
