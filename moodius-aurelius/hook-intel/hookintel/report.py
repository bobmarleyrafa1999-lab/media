"""Markdown reports, CSV/JSON exports and the weekly content plan."""
import csv, datetime as dt, json, os

from . import config, db, performance

EXPORT_SQL = {
    "videos": "SELECT * FROM videos ORDER BY cycle, platform, views DESC",
    "hooks": """SELECT v.url, v.platform, v.creator, v.published, v.views, v.outlier_ratio, h.*
                FROM hooks h JOIN videos v ON v.id = h.video_id ORDER BY h.priority DESC""",
    "patterns": "SELECT * FROM patterns ORDER BY rank",
    "concepts": "SELECT id, batch, pattern_id, title, pillar, status, qc FROM concepts ORDER BY id",
    "own_posts": "SELECT * FROM own_posts ORDER BY published",
}


def fmt(n, unit=""):
    if n is None:
        return "n/a"
    if isinstance(n, float) and not n.is_integer():
        return f"{n:,.2f}{unit}"
    return f"{int(n):,}{unit}"


def export(con, out=None):
    out = out or config.EXPORTS
    os.makedirs(out, exist_ok=True)
    paths = []
    for name, sql in EXPORT_SQL.items():
        data = db.rows(con, sql)
        jp, cp = os.path.join(out, f"{name}.json"), os.path.join(out, f"{name}.csv")
        json.dump(data, open(jp, "w"), indent=1, ensure_ascii=False)
        with open(cp, "w", newline="", encoding="utf-8") as f:
            if data:
                w = csv.DictWriter(f, fieldnames=list(data[0]))
                w.writeheader()
                w.writerows(data)
        paths += [jp, cp]
    return paths


def access_summary():
    import glob
    rows = []
    for path in sorted(glob.glob(os.path.join(config.RAW, "*", "access-log.json"))):
        for r in json.load(open(path)):
            rows.append(r)
    by = {}
    for r in rows:
        k = r["source"]
        by.setdefault(k, {"ok": 0, "failed": 0, "errors": set()})
        by[k]["ok" if r["ok"] else "failed"] += 1
        if not r["ok"]:
            by[k]["errors"].add(r["detail"][:120])
    return by


def discover_md(con, cycle, limit=100):
    vids = db.rows(con, """SELECT v.*, h.category, h.hook_text, h.hook_text_source, h.hook_score, h.priority
                           FROM videos v LEFT JOIN hooks h ON h.video_id = v.id
                           WHERE v.cycle = ? AND v.platform != 'podcast'
                           ORDER BY h.priority DESC NULLS LAST, v.views DESC LIMIT ?""", (cycle, limit))
    lines = [f"# Discover · {cycle}", "", f"{len(vids)} short-form videos. Sorted by priority (outlier first).", "",
             "| # | Platform | Creator | Published | Views | Outlier | Hook (source) | Link |", "|---|---|---|---|---|---|---|---|"]
    for i, v in enumerate(vids, 1):
        lines.append(f"| {i} | {v['platform']} | {v['creator'] or ''} | {v['published'] or 'n/a'} | {fmt(v['views'])} | "
                     f"{fmt(v['outlier_ratio'], 'x')} | {(v['hook_text'] or '').replace('|', '/')} ({v['hook_text_source'] or ''}) | "
                     f"[open]({v['url']}) |")
    return "\n".join(lines) + "\n"


def weekly_plan(con, week_start=None, out=None):
    """Proposal only: which hook-intel concepts go where, with A on the grid and B/C as trial reels.

    Slots follow the reel-first plan (12:00 and 18:00 Madrid, max 2 reels a day, 2 h apart). Nothing
    is scheduled: the account thread books slots in Metricool after the owner picks.
    """
    if week_start is None:
        week_start = dt.date(2026, 11, 30)   # first full week after X5 closes (23 Nov)
    elif isinstance(week_start, str):
        week_start = dt.date.fromisoformat(week_start)
    concepts = db.rows(con, "SELECT * FROM concepts WHERE status IN ('approved', 'draft') ORDER BY status, id")
    plan, day = [], 0
    for c in concepts[:5]:               # one hook-intel reel a day at 12:00: A, then B and C on the next days
        data = json.loads(c["data"])
        for j, v in enumerate("ABC"):
            plan.append({"date": (week_start + dt.timedelta(day)).isoformat(), "time": "12:00", "concept": c["id"],
                         "variant": v, "where": "grid (Metricool)" if v == "A" else "trial reel (Instagram app, by hand)",
                         "hook": data["hooks"][j], "status": c["status"]})
            day += 1
    plan.sort(key=lambda r: (r["date"], r["variant"]))
    end = week_start + dt.timedelta(max(6, day - 1))
    lines = [f"# Content plan from {week_start:%d %b %Y} to {end:%d %b %Y} (proposal)", "",
             "One hook-intel reel a day in the 12:00 slot; 18:00 stays with the existing queue, so it's never more than "
             "2 reels a day, 6 hours apart. Variant A goes on the grid through Metricool. B and C go out as Instagram "
             "trial reels (shown to non-followers only, so the grid doesn't repeat), posted by hand at 12:00 on the next "
             "two days. Five reels x three hooks fill about two weeks. One experiment at a time: this is X6 and starts "
             "only after X5 closes.", "",
             "| Date | Time | Reel | Variant | Where | Hook | Status |", "|---|---|---|---|---|---|---|"]
    for r in plan:
        lines.append(f"| {r['date']} | {r['time']} | {r['concept']} | {r['variant']} | {r['where']} | {r['hook']} | {r['status']} |")
    if not plan:
        lines.append("| | | no concepts built yet: run generate-reels build | | | | |")
    lines += ["", "Rules applied: max 2 reels a day, 12:00/18:00 only, no 10:00, no list openers as hook A, "
              "two-branch structure at least once a week (check the 18:00 queue).",
              "", "_Nothing here is scheduled. the owner picks; the account thread books the slots._"]
    md = "\n".join(lines) + "\n"
    out = out or os.path.join(config.REPORTS, f"weekly-plan-{week_start.isoformat()}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(md)
    with open(out.replace(".md", ".csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "time", "concept", "variant", "where", "hook", "status"])
        w.writeheader()
        w.writerows(plan)
    return out, plan


def performance_md(con):
    base = performance.baseline(con)
    performance.load_experiments(con)
    lines = ["# Performance · Moodius Aurelius reels", "",
             f"Baseline from {base['n']} reels imported from Metricool. Bands use the account's own interquartile range.", "",
             "| Metric | n | Q1 | Median | Q3 |", "|---|---|---|---|---|"]
    for k, m in base["metrics"].items():
        lines.append(f"| {k} | {m['n']} | {fmt(m['q1'])} | {fmt(m['median'])} | {fmt(m['q3'])} |")
    lines += ["", "Missing metrics: " + (", ".join(base["missing"]) or "none"), "", "## Per reel", "",
              "| Published | Hook | Reach | 3 s hold | Avg watch | Bands |", "|---|---|---|---|---|---|"]
    for p in db.rows(con, "SELECT * FROM own_posts ORDER BY published"):
        c = performance.compare_post(p, base)
        bands = ", ".join(f"{k} {v['band']}" for k, v in c.items() if v["band"] != "within") or "all within range"
        lines.append(f"| {(p['published'] or '')[:16]} | {p['hook']} | {fmt(p['reach'])} | {fmt(p['view_rate_3s'], '%')} | "
                     f"{fmt(p['avg_watch_s'], 's')} | {bands} |")
    lines += ["", "## Experiments", ""]
    exps = db.rows(con, "SELECT * FROM experiments")
    if not exps:
        lines.append("No hook-intel experiment has posted yet.")
    for e in exps:
        r = performance.review_experiment(con, e["id"], base)
        lines.append(f"- **{e['id']}** ({r['status']}): {e['hypothesis']}")
        for t in r["tests"]:
            lines.append(f"  - {t['pair']}: {t['diff_pts']:+} pts 3 s hold, p={t['p']} → {t['label']}")
    lines += ["", "## Recommendations", ""] + [f"- {x}" for x in performance.recommendations(con, base)]
    return "\n".join(lines) + "\n", base
