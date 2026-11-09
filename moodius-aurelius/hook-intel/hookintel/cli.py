"""Command line: the five commands from the brief plus helpers.

    python3 -m hookintel discover-hooks   [--fetch requests/x.json] [--full]   # ingest raw data (+ fetch if reachable)
    python3 -m hookintel analyse-hooks    [--cycle NAME] [--top 5]              # classify, score, rank, patterns
    python3 -m hookintel generate-reels   briefs | build data/scripts/x.json [--no-engine]
    python3 -m hookintel review-performance [--import data/imports/x.json]
    python3 -m hookintel weekly-content-plan [--week 2026-11-30]
    python3 -m hookintel search "loneliness"        python3 -m hookintel export        python3 -m hookintel dashboard
"""
import argparse, glob, json, os, shutil, sys

from . import config, db, hooks, ingest, patterns, performance, reels, report


def cmd_discover(a, con):
    if a.fetch:
        if not shutil.which("yt-dlp"):
            sys.exit("yt-dlp is not installed here (pip install yt-dlp). Or commit the request file and let the "
                     "GitHub Actions fetcher run it.")
        sys.path.insert(0, os.path.join(config.ROOT, "remote"))
        import fetch  # noqa: E402
        fetch.run(a.fetch, config.RAW, a.full)
    n = ingest.ingest_all(con)
    for path in glob.glob(os.path.join(config.IMPORTS, "metricool-*.json")):
        ingest.ingest_metricool(con, path)
    acc = report.access_summary()
    print(f"ingested {n} records")
    for src, s in acc.items():
        print(f"  {src:20s} ok {s['ok']:3d}  failed {s['failed']:3d}  {'; '.join(sorted(s['errors']))[:140]}")
    cycles = [r["cycle"] for r in db.rows(con, "SELECT DISTINCT cycle FROM videos WHERE cycle IS NOT NULL")]
    os.makedirs(config.REPORTS, exist_ok=True)
    for c in cycles:
        hooks.analyse(con, c)
        p = os.path.join(config.REPORTS, f"discover-{c}.md")
        open(p, "w").write(report.discover_md(con, c))
        print("wrote", p)


def cmd_analyse(a, con):
    n = hooks.analyse(con, a.cycle)
    top, allp = patterns.build(con, a.cycle, a.top)
    print(f"analysed {n} videos, {len(allp)} patterns")
    for p in top:
        print(f"  #{p['rank']} {p['name']}  n={p['n']}  median outlier={p['median_outlier']}  score={p['score']}")


def cmd_generate(a, con):
    if a.action == "briefs":
        out = reels.briefs(con, a.n)
        path = os.path.join(config.SCRIPTS, "briefs.json")
        os.makedirs(config.SCRIPTS, exist_ok=True)
        json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
        print("wrote", path)
        return
    summary, note, out_dir = reels.build(con, a.path, run_engine=not a.no_engine)
    for s in summary:
        print(f"  {s['id']} {s['title']}: {'OK' if not s['errors'] else 'REJECTED ' + '; '.join(s['errors'])}"
              + (f"  (warn: {'; '.join(s['warnings'])})" if s["warnings"] else ""))
    print("reels-engine:", note)
    print("wrote", out_dir)


def cmd_review(a, con):
    for path in a.imports or glob.glob(os.path.join(config.IMPORTS, "metricool-*.json")):
        print(f"imported {ingest.ingest_metricool(con, path)} reels from {path}")
    md, _ = report.performance_md(con)
    p = os.path.join(config.REPORTS, "performance.md")
    os.makedirs(config.REPORTS, exist_ok=True)
    open(p, "w").write(md)
    print(md)


def cmd_weekly(a, con):
    path, plan = report.weekly_plan(con, a.week)
    print(f"wrote {path} ({len(plan)} slots, proposal only)")


def cmd_search(a, con):
    for r in db.search(con, a.query, a.limit):
        print(f"{r['platform']:8s} {str(r.get('outlier_ratio') or '-'):>6} {r.get('category') or '-':26s} "
              f"{(r.get('hook_text') or r.get('title') or '')[:70]}  {r['url']}")


def cmd_export(a, con):
    for p in report.export(con):
        print("wrote", p)


def cmd_dashboard(a, con):
    from . import dashboard
    if a.static:
        print("wrote", dashboard.write_static(con, a.static))
    else:
        dashboard.serve(a.port)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="hookintel", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=None, help="database path (default data/hookintel.db)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("discover-hooks"); s.add_argument("--fetch"); s.add_argument("--full", action="store_true")
    s.set_defaults(fn=cmd_discover)
    s = sub.add_parser("analyse-hooks"); s.add_argument("--cycle"); s.add_argument("--top", type=int, default=5)
    s.set_defaults(fn=cmd_analyse)
    s = sub.add_parser("generate-reels"); s.add_argument("action", choices=["briefs", "build"])
    s.add_argument("path", nargs="?"); s.add_argument("-n", type=int, default=5); s.add_argument("--no-engine", action="store_true")
    s.set_defaults(fn=cmd_generate)
    s = sub.add_parser("review-performance"); s.add_argument("--import", dest="imports", action="append")
    s.set_defaults(fn=cmd_review)
    s = sub.add_parser("weekly-content-plan"); s.add_argument("--week"); s.set_defaults(fn=cmd_weekly)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=25)
    s.set_defaults(fn=cmd_search)
    s = sub.add_parser("export"); s.set_defaults(fn=cmd_export)
    s = sub.add_parser("dashboard"); s.add_argument("--port", type=int, default=8765); s.add_argument("--static")
    s.set_defaults(fn=cmd_dashboard)
    a = ap.parse_args(argv)
    if a.cmd == "generate-reels" and a.action == "build" and not a.path:
        ap.error("generate-reels build needs a script batch path")
    con = db.connect(a.db)
    a.fn(a, con)
    con.close()


if __name__ == "__main__":
    main()
