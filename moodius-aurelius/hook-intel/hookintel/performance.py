"""Own-account performance: baseline, per-post comparison, and the three-hook A/B framework.

Statistics are kept honest: a difference is called "evidence" only when a two-proportion test on
real counts gives p < 0.05 with at least MIN_VIEWS views per arm. Everything else is a hypothesis.
"""
import glob, json, math, os, statistics

from . import config, db

MIN_VIEWS = 100
METRICS = {  # name -> (function of a post row, unit)
    "reach": (lambda p: p["reach"], "people"),
    "view_rate_3s": (lambda p: p["view_rate_3s"], "% of views past 3 s"),
    "avg_watch_s": (lambda p: p["avg_watch_s"], "s"),
    "watch_ratio": (lambda p: p["avg_watch_s"] / p["duration_s"] if p.get("avg_watch_s") and p.get("duration_s") else None,
                    "share of the reel watched"),
    "shares_per_1k_reach": (lambda p: 1000 * p["shares"] / p["reach"] if p.get("reach") else None, "per 1,000 reached"),
    "saves_per_1k_reach": (lambda p: 1000 * p["saves"] / p["reach"] if p.get("reach") else None, "per 1,000 reached"),
    "follows_per_1k_reach": (lambda p: 1000 * p["follows"] / p["reach"] if p.get("reach") and p.get("follows") is not None
                             else None, "per 1,000 reached"),
}


def quantiles(vals):
    vals = sorted(vals)
    if len(vals) < 4:
        return None, statistics.median(vals) if vals else None, None
    q = statistics.quantiles(vals, n=4)
    return q[0], q[1], q[2]


def baseline(con):
    posts = db.rows(con, "SELECT * FROM own_posts WHERE kind = 'reel'")
    out = {"n": len(posts), "metrics": {}, "missing": []}
    for name, (fn, unit) in METRICS.items():
        vals = [v for v in (fn(p) for p in posts) if v is not None]
        if not vals:
            out["missing"].append(name)
            continue
        q1, med, q3 = quantiles(vals)
        out["metrics"][name] = {"n": len(vals), "q1": q1, "median": med, "q3": q3, "unit": unit}
    return out


def compare_post(p, base):
    """Each metric vs the account's interquartile range: above / within / below."""
    res = {}
    for name, (fn, _) in METRICS.items():
        v, b = fn(p), base["metrics"].get(name)
        if v is None or not b:
            continue
        if b["q1"] is None:
            res[name] = {"value": v, "vs_median": round(v / b["median"], 2) if b["median"] else None, "band": "n<4"}
            continue
        band = "above" if v > b["q3"] else "below" if v < b["q1"] else "within"
        res[name] = {"value": round(v, 2), "vs_median": round(v / b["median"], 2) if b["median"] else None, "band": band}
    return res


def two_prop(k1, n1, k2, n2):
    """Two-sided two-proportion z-test. Returns (difference, p-value)."""
    if min(n1, n2) == 0:
        return None, None
    p1, p2 = k1 / n1, k2 / n2
    pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return p1 - p2, 1.0
    z = (p1 - p2) / se
    return p1 - p2, math.erfc(abs(z) / math.sqrt(2))


def load_experiments(con):
    for path in sorted(glob.glob(os.path.join(config.DATA, "experiments", "*.json"))):
        e = json.load(open(path))
        db.upsert(con, "experiments", {k: e.get(k) for k in ("id", "concept_id", "hypothesis", "metric", "status",
                                                             "created", "notes")})
        for v, d in e.get("variants", {}).items():
            db.upsert(con, "variants", {"experiment_id": e["id"], "variant": v, "hook": d.get("hook"),
                                        "post_url": d.get("post_url"), "slot": d.get("slot"),
                                        "published": d.get("published")}, key=("experiment_id", "variant"))
    con.commit()


def review_experiment(con, exp_id, base):
    variants = db.rows(con, "SELECT * FROM variants WHERE experiment_id = ? ORDER BY variant", (exp_id,))
    arms = []
    for v in variants:
        post = None
        if v["post_url"]:
            key = v["post_url"].rstrip("/").split("/")[-1]
            post = (db.rows(con, "SELECT * FROM own_posts WHERE id = ?", (key,)) or [None])[0]
        arms.append({**v, "post": post, "vs_baseline": compare_post(post, base) if post else None})
    live = [a for a in arms if a["post"] and a["post"]["views"] and a["post"]["view_rate_3s"] is not None]
    tests = []
    for i in range(len(live)):
        for j in range(i + 1, len(live)):
            a, b = live[i]["post"], live[j]["post"]
            n1, n2 = int(a["views"]), int(b["views"])
            k1, k2 = round(n1 * a["view_rate_3s"] / 100), round(n2 * b["view_rate_3s"] / 100)
            diff, p = two_prop(k1, n1, k2, n2)
            enough = min(n1, n2) >= MIN_VIEWS
            label = ("evidence" if p is not None and p < 0.05 and enough else
                     "hypothesis (not significant)" if enough else f"hypothesis (fewer than {MIN_VIEWS} views per arm)")
            tests.append({"pair": f"{live[i]['variant']} vs {live[j]['variant']}", "metric": "3 s hold",
                          "diff_pts": round(100 * diff, 1), "p": round(p, 3) if p is not None else None, "label": label})
    status = "waiting for posts" if not live else "complete" if len(live) == len(arms) else "partial"
    return {"experiment": exp_id, "status": status, "arms": arms, "tests": tests}


def recommendations(con, base):
    from . import hooks
    own = hooks.classify_own(con)
    by = {}
    for o in own:
        for f in o["flags"] or ["other"]:
            by.setdefault(f, []).append(o)
    lines = []
    med_hold = base["metrics"].get("view_rate_3s", {}).get("median")
    for flag, posts in sorted(by.items()):
        holds = [p["view_rate_3s"] for p in posts if p["view_rate_3s"] is not None]
        if not holds or med_hold is None:
            continue
        m = statistics.median(holds)
        kind = "measured on this account" if len(holds) >= 3 else "single example: hypothesis"
        lines.append(f"{flag.replace('_', ' ')}: median 3 s hold {m:.0f}% vs account {med_hold:.0f}% "
                     f"(n={len(holds)}, {kind})")
    lines.append("Next experiment (X6, after X5 closes on 23 Nov): three hooks per hook-intel reel, grid post = A, "
                 "B and C as Instagram trial reels in matched slots; primary metric 3 s hold, secondary sends per reach.")
    if base["missing"]:
        lines.append("Not measurable yet: " + ", ".join(base["missing"]) +
                     " (Metricool's reels connector does not expose follows per reel or video duration for organic reels).")
    return lines
