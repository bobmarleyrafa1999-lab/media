"""Command line: python3 -m moodius_growth <command> ...   (run from the growth-tracker folder)"""
import argparse
import os
import sys

from . import db, importers
from .config import DEMO_DB, REAL_DB, ROOT, SCENARIOS_PATH


def main(argv=None):
    p = argparse.ArgumentParser(prog="moodius_growth")
    p.add_argument("--demo", action="store_true", help="use the separate demo database")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("import-account", "import-content", "import-tags", "import-experiments", "import-metricool-json"):
        s = sub.add_parser(name)
        s.add_argument("file")
        if name in ("import-account", "import-content"):
            s.add_argument("--source", default="manual_csv",
                           help="manual_csv, ig_export or metricool_csv")
            s.add_argument("--scope", default="organic", help="organic, paid, organic+paid or unknown")
        if name == "import-account":
            s.add_argument("--tz", default="Europe/London", help="time zone the export's days use")
        if name == "import-content":
            s.add_argument("--format", default=None, help="reel, carousel, image or story if the file has no type column")
    r = sub.add_parser("report", help="write the weekly report")
    r.add_argument("--week-ending", default=None, help="YYYY-MM-DD (default: latest day with a follower total)")
    r.add_argument("--out", default=None)
    c = sub.add_parser("collect-meta", help="pull from Meta's Instagram API (needs setup, see docs)")
    c.add_argument("--ig-user-id", default=os.environ.get("MOODIUS_IG_USER_ID"))
    c.add_argument("--days-back", type=int, default=3)
    sub.add_parser("status", help="show data freshness and the last collection runs")
    sub.add_parser("demo", help="rebuild the synthetic demo database")
    a = p.parse_args(argv)

    if a.cmd == "demo":
        from demo.make_demo import build
        print(build())
        return
    con = db.connect(DEMO_DB if a.demo else REAL_DB)
    if a.cmd == "import-account":
        print(importers.import_account_csv(con, a.file, a.source, a.tz, a.scope))
    elif a.cmd == "import-content":
        print(importers.import_content_csv(con, a.file, a.source, a.scope, default_format=a.format))
    elif a.cmd == "import-tags":
        print(importers.import_tags_csv(con, a.file))
    elif a.cmd == "import-experiments":
        print(importers.import_experiments_csv(con, a.file))
    elif a.cmd == "import-metricool-json":
        print(importers.import_metricool_json(con, a.file))
    elif a.cmd == "report":
        from . import report
        from .forecast import load_scenarios
        text, _ = report.build(con, load_scenarios(SCENARIOS_PATH), a.week_ending, is_demo=a.demo)
        out = a.out or os.path.join(os.path.dirname(REAL_DB), "reports",
                                    ("DEMO-" if a.demo else "") + "weekly-latest.md")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Report written to {out}")
    elif a.cmd == "collect-meta":
        if not a.ig_user_id:
            sys.exit("Set MOODIUS_IG_USER_ID or pass --ig-user-id (docs/META-API-SETUP.md step 7).")
        from . import meta_api
        print(meta_api.collect(con, a.ig_user_id, a.days_back))
    elif a.cmd == "status":
        from . import metrics
        print(metrics.freshness(con).to_string(index=False))
        for row in con.execute("SELECT * FROM collection_log ORDER BY run_at_utc DESC LIMIT 5"):
            print(row)


if __name__ == "__main__":
    main()
