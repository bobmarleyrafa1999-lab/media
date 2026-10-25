#!/usr/bin/env python3
"""Moodius analytics engine: one SQLite file, one dashboard, one weekly note.

Reads what we already have, with no account connection:
  * Instagram's own "posts" CSV export (Professional dashboard > export)
  * strategy/post-log.csv (reel metrics copied from Instagram / Metricool)
  * strategy/22-90-day-plan/tracker.csv (the 90-day plan's log: metrics plus
    pillar, series, opener tone, experiment and arm in one row)
  * a tags CSV that gives older posts a pillar (Mind, Body, People) and hook type

Later the same tables take rows from the Instagram Graph API pull (official
API, same token as the comment agent) once Surafel approves that connection.

Rates are per 1,000 accounts reached, using summed numerators over summed
denominators, and only over posts that report both. Instagram's API gives
'follows' and 'profile_visits' for feed posts and stories, not reels, so reel
follow rates are shown as "n/a" rather than guessed.

Usage:
  python3 analytics.py --ig-export EXPORT.csv [--post-log post-log.csv] \
      --tags tags.csv --out OUT_DIR [--week-ending 2026-10-25]
Writes OUT_DIR/moodius.sqlite, OUT_DIR/dashboard.html, OUT_DIR/weekly.md.
"""
import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import sqlite3
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PILLARS_PATH = os.path.join(HERE, "..", "pillars.json")
METRICS = ["views", "reach", "likes", "comments", "saves", "shares", "follows", "profile_visits"]
MIN_N = 5          # below this a group result is a lead, not a finding
MIN_REACH = 50     # posts under this reach are too small to rank
MIN_AGE_DAYS = 3   # younger posts are still collecting reach

with open(PILLARS_PATH, encoding="utf-8") as _f:
    CFG = json.load(_f)


def num(value):
    value = (value or "").strip().replace(",", "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def hook_key(date, text):
    """Match the same post across sources: date + first 24 letters of the hook."""
    letters = re.sub(r"[^a-z]", "", (text or "").lower())[:24]
    return f"{date}:{letters}"


def kind_of(raw):
    raw = (raw or "").upper()
    if "REEL" in raw or "VIDEO" in raw:
        return "reel"
    if "CAROUSEL" in raw:
        return "carousel"
    if "STORY" in raw:
        return "story"
    return "image"


def read_ig_export(path):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            date = (r.get("Timestamp") or r.get("Publish time") or "")[:10]
            text = (r.get("Content") or r.get("Description") or "").strip()
            first = text.splitlines()[0] if text else ""
            rows.append({
                "key": hook_key(date, first), "source": "ig_export", "url": r.get("URL") or r.get("Permalink"),
                "date": date, "kind": kind_of(r.get("type") or r.get("Post type")), "hook": first,
                "views": num(r.get("Views")), "reach": num(r.get("Reach (Organic)") or r.get("Reach")),
                "likes": num(r.get("Likes")), "comments": num(r.get("Comments")),
                "saves": num(r.get("Saved") or r.get("Saves")), "shares": num(r.get("Shares")),
                "follows": num(r.get("Follows")), "profile_visits": num(r.get("Profile visits")),
            })
    # Instagram leaves a metric blank when it is zero; treat blanks as 0 for the
    # counts it always reports, but keep follows/profile visits blank when the
    # whole export lacks them.
    has = {m: any(r[m] is not None for r in rows) for m in METRICS}
    for r in rows:
        for m in ("likes", "comments", "saves", "shares"):
            r[m] = r[m] or 0.0
        for m in ("follows", "profile_visits"):
            if has[m] and r["kind"] != "reel":
                r[m] = r[m] or 0.0
    return rows


def read_post_log(path):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("brand") or "moodius") != "moodius":
                continue
            rows.append({
                "key": hook_key(r["date"], r.get("hook_text")), "source": "post_log", "url": None,
                "date": r["date"], "kind": kind_of(r.get("type")), "hook": r.get("hook_text", ""),
                **{m: num(r.get(m)) for m in METRICS},
                "hold_3s_pct": num(r.get("hold_3s_pct")), "avg_watch_s": num(r.get("avg_watch_s")),
            })
    return rows


def read_tracker(path):
    """The 90-day plan's tracker.csv: metrics and tags in one row per post. Story rows are skipped."""
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if not r.get("date") or (r.get("format") or "").lower().startswith("story"):
                continue
            rows.append({
                "key": hook_key(r["date"], r.get("hook")), "source": "tracker", "url": None,
                "date": r["date"], "kind": kind_of(r.get("format")), "hook": r.get("hook", ""),
                **{m: num(r.get(m)) for m in METRICS},
                "hold_3s_pct": num(r.get("hold_3s_pct")), "avg_watch_s": num(r.get("avg_watch_s")),
                "tags": {k: r.get(k, "") for k in ("pillar", "series", "opener_tone", "experiment", "arm")},
            })
    return rows


def read_tags(path):
    tags = {}
    if not path:
        return tags
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            tags[hook_key(r["date"], r["hook"])] = r
    return tags


def pillar_key(value):
    """Accept a pillar key ('mind') or its name ('Mind'); anything else is 'untagged'."""
    v = (value or "").strip().lower()
    for key, p in CFG["pillars"].items():
        if v in (key, p["name"].lower()):
            return key
    return "untagged"


def merge(sources, tags):
    """Instagram's export wins over the hand log; the log fills gaps (hold, watch)."""
    posts = {}
    for rows in sources:
        for r in rows:
            cur = posts.get(r["key"])
            if cur is None:
                posts[r["key"]] = dict(r)
                continue
            for k, v in r.items():
                if cur.get(k) is None and v is not None:
                    cur[k] = v
    for key, p in posts.items():
        t = dict(p.pop("tags", {}) or {})
        t.update({k: v for k, v in tags.get(key, {}).items() if v})
        p["pillar"] = pillar_key(t.get("pillar"))
        p["series"] = t.get("series") or ""
        p["opener_tone"] = (t.get("opener_tone") or "").lower()
        p["hook_type"] = t.get("hook_type") or ""
        p["experiment"] = t.get("experiment") or ""
        p["arm"] = t.get("arm") or ""
        p["hurt_conflict"] = (t.get("hurt_conflict") or "").lower() in ("1", "yes", "true", "y") \
            or p["opener_tone"] == "hurt"
        p.setdefault("hold_3s_pct", None)
        p.setdefault("avg_watch_s", None)
    return sorted(posts.values(), key=lambda p: (p["date"], p["hook"]))


def write_db(posts, path):
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    cols = ["key", "source", "url", "date", "kind", "pillar", "series", "opener_tone", "hook_type", "hurt_conflict",
            "experiment", "arm", "hook",
            *METRICS, "hold_3s_pct", "avg_watch_s"]
    con.execute(f"CREATE TABLE posts ({', '.join(cols)}, PRIMARY KEY (key))")
    con.executemany(f"INSERT INTO posts VALUES ({', '.join('?' * len(cols))})",
                    [[p.get(c) for c in cols] for p in posts])
    con.commit()
    con.close()


def rate(posts, metric):
    """Per 1,000 reached, over posts that report both the metric and reach."""
    pairs = [(p[metric], p["reach"]) for p in posts if p.get(metric) is not None and p.get("reach")]
    if not pairs:
        return None, 0
    return 1000 * sum(a for a, _ in pairs) / sum(b for _, b in pairs), len(pairs)


def engagement(p):
    parts = [p.get(m) for m in ("likes", "comments", "saves", "shares")]
    return sum(x or 0 for x in parts)


def group(posts, field):
    out = []
    for value in sorted({p[field] for p in posts}):
        g = [p for p in posts if p[field] == value]
        reach = [p["reach"] for p in g if p.get("reach")]
        row = {"group": value, "n": len(g), "median_reach": statistics.median(reach) if reach else None}
        for m in ("comments", "saves", "shares", "follows"):
            row[m + "_per_1k"], row[m + "_n"] = rate(g, m)
        eng = [(engagement(p), p["reach"]) for p in g if p.get("reach")]
        row["engagement_per_1k"] = 1000 * sum(a for a, _ in eng) / sum(b for _, b in eng) if eng else None
        row["confidence"] = "finding" if len(reach) >= MIN_N else "lead only"
        out.append(row)
    return out


def recommendations(posts, cfg, week_end):
    lines = []
    total_reach = sum(p["reach"] or 0 for p in posts)
    lines.append(f"Data: {len(posts)} posts, {int(total_reach):,} accounts reached in total "
                 f"(reach is per post, so people who saw two posts count twice).")
    if total_reach < 5000 or len(posts) < 20:
        lines.append("Sample is small. Treat every comparison below as a lead to test, not a result.")

    ranked = [p for p in posts if (p["reach"] or 0) >= MIN_REACH]
    ranked.sort(key=lambda p: -((p["saves"] or 0) + (p["shares"] or 0)) / p["reach"])
    if ranked:
        lines.append("\n**Deserve a follow-up post** (saves + shares per 1,000 reached, reach 50+):")
        for p in ranked[:3]:
            v = 1000 * ((p["saves"] or 0) + (p["shares"] or 0)) / p["reach"]
            lines.append(f"- {p['date']} {p['kind']} \"{p['hook'][:70]}\": {v:.1f} per 1k, reach {int(p['reach'])}")

    followed = [p for p in posts if (p.get("follows") or 0) > 0]
    lines.append("\n**Posts that produced follows** (Instagram reports this for feed posts, not reels):")
    if followed:
        for p in followed:
            lines.append(f"- {p['date']} \"{p['hook'][:70]}\": {int(p['follows'])} follow(s) from reach {int(p['reach'] or 0)}")
    else:
        lines.append("- none in this data")

    by_kind = {}
    for p in ranked:
        by_kind.setdefault(p["kind"], []).append(p["reach"])
    settled = (week_end - dt.timedelta(days=MIN_AGE_DAYS)).isoformat()
    weak = [p for p in posts if p.get("reach") is not None and p["kind"] in by_kind and p["date"] <= settled
            and len(by_kind[p["kind"]]) >= 3 and p["reach"] < 0.25 * statistics.median(by_kind[p["kind"]])]
    if weak:
        lines.append("\n**Underperformed their format** (reach under a quarter of the format median):")
        for p in weak:
            lines.append(f"- {p['date']} {p['kind']} \"{p['hook'][:70]}\": reach {int(p['reach'])}")

    start = (week_end - dt.timedelta(days=6)).isoformat()
    week = [p for p in posts if start <= p["date"] <= week_end.isoformat()]
    lines.append(f"\n**Pillar balance, {start} to {week_end.isoformat()}** ({len(week)} posts):")
    for key, pillar in cfg["pillars"].items():
        have = sum(1 for p in week if p["pillar"] == key)
        goal = round(pillar["share"] * len(week))
        flag = "on target" if have >= goal else f"{goal - have} short"
        lines.append(f"- {pillar['name']}: {have} of {goal} ({pillar['share']:.0%} share; {flag})")
    untagged = sum(1 for p in week if p["pillar"] not in cfg["pillars"])
    if untagged:
        lines.append(f"- untagged: {untagged}")
    hurt = sum(1 for p in week if p["hurt_conflict"])
    cap = cfg["tone"]["max_hurt_or_conflict_per_week"]
    lines.append(f"- hurt/conflict openers: {hurt} (cap {cap})" + ("  **over cap**" if hurt > cap else ""))
    tagged = [p for p in week if p["opener_tone"]]
    if tagged:
        light = sum(1 for p in tagged if p["opener_tone"] in ("curiosity", "appreciation"))
        below = light / len(tagged) < cfg["tone"]["min_curiosity_or_appreciation_share"] - 1e-9
        lines.append(f"- curiosity or appreciation openers: {light} of {len(tagged)} (rule 2 in 3)"
                     + ("  **below the rule**" if below else ""))
    return "\n".join(lines)


def per_post(p, metric):
    """A post's value for an experiment metric: '<x>_per_1k' or a raw column such as hold_3s_pct."""
    if metric.endswith("_per_1k"):
        base = metric[:-len("_per_1k")]
        if p.get(base) is None or not p.get("reach"):
            return None
        return 1000 * p[base] / p["reach"]
    return p.get(metric)


def experiment_readout(posts, experiments_path):
    """One line per experiment, called by the rule fixed before it started (the 90-day plan's 30% rule).

    Per arm: the median of the per-post metric. A lead is called only when both
    arms have min_per_arm posts, one arm's median is at least rule_ratio times
    the other's, and the leader's median reach is no more than 30% lower.
    Otherwise: 'keep running' or 'no clear winner'.
    """
    lines = []
    with open(experiments_path, encoding="utf-8-sig", newline="") as f:
        exps = list(csv.DictReader(f))
    for e in exps:
        metric, need, ratio = e["primary_metric"], int(e["min_per_arm"]), float(e["rule_ratio"])
        mine = [p for p in posts if p.get("experiment") == e["id"]]
        if not mine:
            lines.append(f"- {e['id']} ({e['status']}): no posts logged yet.")
            continue
        arms = {}
        for arm in (e["arm_a"], e["arm_b"]):
            vals = [v for v in (per_post(p, metric) for p in mine if p.get("arm") == arm) if v is not None]
            reach = [p["reach"] for p in mine if p.get("arm") == arm and p.get("reach")]
            arms[arm] = (statistics.median(vals) if vals else None, len(vals),
                         statistics.median(reach) if reach else None)
        (ma, na, ra), (mb, nb, rb) = arms[e["arm_a"]], arms[e["arm_b"]]
        if min(na, nb) < need:
            call = f"keep running ({na} and {nb} of {need} posts per arm)"
        else:
            lead, (ml, rl), (mo, ro) = ((e["arm_a"], (ma, ra), (mb, rb)) if ma >= mb
                                        else (e["arm_b"], (mb, rb), (ma, ra)))
            big_enough = ml >= ratio * mo if mo > 0 else ml > 0
            reach_ok = rl is None or ro is None or rl >= 0.7 * ro
            if big_enough and reach_ok:
                call = f"lead for {lead} (median {fmt(ml)} vs {fmt(mo)})"
            elif big_enough:
                call = f"no clear winner: {lead} is ahead but its reach median is over 30% lower"
            else:
                call = f"no clear winner (needs a {ratio - 1:.0%} higher median)"
        lines.append(f"- {e['id']} median {metric}: {e['arm_a']} {fmt(ma)} (n={na}) vs "
                     f"{e['arm_b']} {fmt(mb)} (n={nb}). {call}.")
    return "\n".join(lines)


def fmt(v, digits=1):
    return "n/a" if v is None else (f"{v:,.{digits}f}" if isinstance(v, float) else str(v))


def dashboard(posts, by_pillar, by_kind, recs, cfg):
    names = {k: v["name"] for k, v in cfg["pillars"].items()}

    def table(rows, label):
        top = max([r["engagement_per_1k"] or 0 for r in rows] + [1])
        body = []
        for r in rows:
            e = r["engagement_per_1k"]
            bar = f'<span class="bar" style="width:{0 if e is None else 100 * e / top:.0f}%"></span>'
            body.append(
                f"<tr><td>{html.escape(names.get(r['group'], r['group']))}</td><td>{r['n']}</td>"
                f"<td>{fmt(r['median_reach'], 0)}</td><td class='barcell'>{bar}<span>{fmt(e)}</span></td>"
                f"<td>{fmt(r['saves_per_1k'])}</td><td>{fmt(r['shares_per_1k'])}</td>"
                f"<td>{fmt(r['comments_per_1k'])}</td><td>{fmt(r['follows_per_1k'])}</td>"
                f"<td class='conf'>{r['confidence']}</td></tr>")
        return (f"<table><thead><tr><th>{label}</th><th>posts</th><th>median reach</th>"
                "<th>engagement /1k</th><th>saves /1k</th><th>shares /1k</th><th>comments /1k</th>"
                "<th>follows /1k</th><th></th></tr></thead><tbody>" + "".join(body) + "</tbody></table>")

    post_rows = "".join(
        f"<tr><td>{p['date']}</td><td>{p['kind']}</td><td>{html.escape(names.get(p['pillar'], p['pillar']))}</td>"
        f"<td class='hook'>{html.escape(p['hook'][:90])}</td><td>{fmt(p['reach'], 0)}</td>"
        f"<td>{fmt(p['saves'], 0)}</td><td>{fmt(p['shares'], 0)}</td><td>{fmt(p['comments'], 0)}</td>"
        f"<td>{fmt(p['follows'], 0)}</td></tr>" for p in sorted(posts, key=lambda p: p["date"], reverse=True))
    md = html.escape(recs)
    md = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", md).replace("\n", "<br>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Moodius dashboard</title>
<style>
:root{{--bg:#F3EFE7;--fg:#1B1F24;--muted:#6b6760;--line:#d9d3c7;--accent:#C9742E}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1B1F24;--fg:#F3EFE7;--muted:#B8B3A9;--line:#3A4049}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 Inter,system-ui,sans-serif;margin:0;padding:24px 16px;max-width:1100px;margin:auto}}
h1,h2{{font-family:"Playfair Display",Georgia,serif;font-weight:600}} .note{{color:var(--muted)}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;margin:8px 0 24px;font-size:14px}}
th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);white-space:nowrap}} td.hook{{white-space:normal;min-width:240px}}
.barcell{{position:relative;min-width:120px}} .bar{{position:absolute;left:0;top:30%;height:40%;background:var(--accent);opacity:.35}}
.barcell span:last-child{{position:relative}} .conf{{color:var(--muted)}} .recs{{background:rgba(201,116,46,.08);padding:12px 16px;border-left:3px solid var(--accent)}}
</style></head><body>
<h1>Moodius Aurelius: what is working</h1>
<p class="note">Rates are per 1,000 accounts reached, summed over posts that report both numbers. "Lead only" means fewer than {MIN_N} posts with reach: test it, don't act on it. Instagram does not report follows for reels.</p>
<h2>This week's notes</h2><div class="recs">{md}</div>
<h2>By pillar</h2><div class="wrap">{table(by_pillar, "pillar")}</div>
<h2>By format</h2><div class="wrap">{table(by_kind, "format")}</div>
<h2>Every post</h2><div class="wrap"><table><thead><tr><th>date</th><th>format</th><th>pillar</th><th>hook</th><th>reach</th><th>saves</th><th>shares</th><th>comments</th><th>follows</th></tr></thead><tbody>{post_rows}</tbody></table></div>
</body></html>"""


def run(ig_export, post_log, tags_path, out, week_end, experiments=None, tracker=None):
    cfg = CFG
    sources = []
    if ig_export:
        sources.append(read_ig_export(ig_export))
    if tracker:
        sources.append(read_tracker(tracker))
    if post_log:
        sources.append(read_post_log(post_log))
    posts = merge(sources, read_tags(tags_path))
    os.makedirs(out, exist_ok=True)
    write_db(posts, os.path.join(out, "moodius.sqlite"))
    by_pillar, by_kind = group(posts, "pillar"), group(posts, "kind")
    recs = recommendations(posts, cfg, week_end)
    if experiments:
        recs += "\n\n**Experiments**\n" + experiment_readout(posts, experiments)
    with open(os.path.join(out, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(dashboard(posts, by_pillar, by_kind, recs, cfg))
    with open(os.path.join(out, "weekly.md"), "w", encoding="utf-8") as f:
        f.write(f"# Weekly notes, week ending {week_end.isoformat()}\n\n{recs}\n")
    return posts, by_pillar, by_kind, recs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ig-export")
    ap.add_argument("--post-log")
    ap.add_argument("--tracker", help="strategy/22-90-day-plan/tracker.csv (metrics and tags in one file)")
    ap.add_argument("--tags")
    ap.add_argument("--out", required=True)
    ap.add_argument("--week-ending", default=dt.date.today().isoformat())
    ap.add_argument("--experiments", help="experiments CSV with decision rules (experiments.csv)")
    args = ap.parse_args(argv)
    if not (args.ig_export or args.post_log or args.tracker):
        ap.error("give --ig-export, --post-log and/or --tracker")
    _, _, _, recs = run(args.ig_export, args.post_log, args.tags, args.out,
                        dt.date.fromisoformat(args.week_ending), args.experiments, args.tracker)
    print(recs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
