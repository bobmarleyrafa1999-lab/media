"""Build data/demo.sqlite from SYNTHETIC numbers. Nothing here is real @moodiusaurelius data.

The demo exists so the dashboard and forecasts can be tried with 150 days of
history before the real account has that much. It lives in its own database
file and every row is flagged is_demo = 1.
"""
import csv
import datetime as dt
import os

import numpy as np

from moodius_growth import db, importers
from moodius_growth.config import DATA_DIR, DEMO_DB, LONDON

HERE = os.path.dirname(os.path.abspath(__file__))


def build(days=150, seed=11):
    rng = np.random.default_rng(seed)
    if os.path.exists(DEMO_DB):
        os.remove(DEMO_DB)
    con = db.connect(DEMO_DB)
    start = dt.date(2026, 5, 1)
    collected = "2026-09-28T07:00:00+00:00"
    acc_path = os.path.join(DATA_DIR, "demo-account.csv")
    con_path = os.path.join(DATA_DIR, "demo-content.csv")
    tag_path = os.path.join(DATA_DIR, "demo-tags.csv")
    os.makedirs(DATA_DIR, exist_ok=True)
    followers = 300.0
    acc_rows, posts, tags = [], [], []
    for i in range(days):
        d = start + dt.timedelta(days=i)
        weekday_boost = 1.15 if d.weekday() in (1, 3) else 1.0
        reach = rng.lognormal(np.log(600 + 6 * i), 0.35) * weekday_boost
        if i == 95:
            reach *= 9                                     # one viral day, kept as an outlier
        follows = rng.poisson(reach * 0.006)
        unfollows = rng.poisson(followers * 0.0007)
        followers += follows - unfollows
        row = {"date": d.isoformat(), "followers_total": int(followers), "following_total": 70,
               "follows": follows, "unfollows": unfollows, "reach": int(reach), "views": int(reach * 1.4),
               "accounts_engaged": int(reach * 0.03), "profile_visits": int(reach * 0.02),
               "link_taps": "" if i % 9 == 0 else rng.poisson(1.5), "collected_at_utc": collected}
        acc_rows.append(row)
        for fmt, hour in (("carousel", 12), ("reel", 18)):
            if fmt == "reel" and d.weekday() in (0, 2, 5):
                continue
            mid = f"DEMO-{d:%m%d}-{fmt[0]}"
            r = rng.lognormal(np.log(380 if fmt == "carousel" else 170), 0.5) * (6 if i == 95 and fmt == "carousel" else 1)
            hook = rng.choice(["conflict", "question", "list", "story"])
            topic = rng.choice(["Mind", "Body", "People"])
            pub = dt.datetime(d.year, d.month, d.day, hour, tzinfo=LONDON)
            posts.append({"media_id": mid, "format": fmt, "published_at": pub.strftime("%Y-%m-%d %H:%M"),
                          "first_line": f"DEMO {fmt} {d:%d %b}: {hook} hook about {topic}",
                          "reach": int(r), "views": int(r * 1.5), "likes": rng.poisson(r * 0.03),
                          "comments": rng.poisson(r * 0.004), "saves": rng.poisson(r * (0.012 if fmt == "carousel" else 0.004)),
                          "shares": rng.poisson(r * (0.008 if hook == "conflict" else 0.004)),
                          "follows": "" if fmt == "reel" else rng.poisson(r * 0.004),
                          "avg_watch_s": round(rng.uniform(3, 9), 1) if fmt == "reel" else "",
                          "view_rate_3s_pct": round(rng.uniform(20, 50), 1) if fmt == "reel" else "",
                          "collected_at_utc": collected})
            tags.append({"media_id": mid, "pillar": topic, "topic": topic.lower(), "hook_type": hook,
                         "cta": rng.choice(["send this", "save this", "question"]),
                         "duration_s": 32 if fmt == "reel" else "", "production_minutes": 45 if fmt == "reel" else 30,
                         "experiment_id": "D1" if i >= days - 28 and fmt == "carousel" else "",
                         "arm": ("A" if i % 2 else "B") if i >= days - 28 and fmt == "carousel" else ""})
    for path, rows in ((acc_path, acc_rows), (con_path, posts), (tag_path, tags)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    importers.import_account_csv(con, acc_path, "demo", "Europe/London", "organic", is_demo=True)
    importers.import_content_csv(con, con_path, "demo", "organic", is_demo=True)
    importers.import_tags_csv(con, tag_path, is_demo=True)
    con.execute("INSERT OR REPLACE INTO experiment VALUES ('D1','DEMO: conflict openers earn more shares than question openers',"
                "'carousel opener','shares per 1k reach',7,'Pick the arm whose median is >=30% higher after 8 posts each; else no winner',"
                "'2026-09-01','2026-09-28','running',NULL)")
    con.commit()
    return f"Demo database rebuilt: {DEMO_DB} ({days} synthetic days, {len(posts)} synthetic posts)"


if __name__ == "__main__":
    print(build())
