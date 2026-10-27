"""Run: python3 -m unittest discover -s tests   (from the growth-tracker folder)"""
import csv
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

TMP = tempfile.mkdtemp()
os.environ["MOODIUS_DATA_DIR"] = TMP

from moodius_growth import db, forecast as fc, importers, metrics as mx  # noqa: E402


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


class Core(unittest.TestCase):
    def setUp(self):
        self.con = db.connect(os.path.join(TMP, f"t{id(self)}.sqlite"))

    def test_missing_is_not_zero_and_duplicates_skipped(self):
        p = os.path.join(TMP, "acc.csv")
        write_csv(p, [{"date": "2026-10-01", "followers_total": "10", "reach": "", "profile_visits": "n/a"},
                      {"date": "2026-10-02", "followers_total": "12", "reach": "100", "profile_visits": ""}])
        importers.import_account_csv(self.con, p)
        self.assertEqual(importers.import_account_csv(self.con, p)["status"], "skipped")
        acc, _ = mx.load_account(self.con)
        self.assertTrue(np.isnan(acc.loc["2026-10-01", "reach"]))
        self.assertTrue(acc["profile_visits"].isna().all())
        d = mx.daily_changes(acc)
        s = mx.period_summary(d, "2026-10-02", "2026-10-02")
        self.assertEqual(s["net_change"], 2)
        self.assertAlmostEqual(s["growth_pct"], 20.0)      # 2 / 10 * 100

    def test_post_rates_and_reel_follows(self):
        p = os.path.join(TMP, "posts.csv")
        write_csv(p, [
            {"media_id": "a", "format": "carousel", "published_at": "2026-10-01 12:00", "reach": "1000", "likes": "10",
             "comments": "2", "saves": "5", "shares": "3", "follows": "4", "collected_at_utc": "2026-10-08T12:00:00+00:00"},
            {"media_id": "b", "format": "reel", "published_at": "2026-10-01 18:00", "reach": "500", "likes": "5",
             "comments": "", "saves": "1", "shares": "1", "follows": "", "collected_at_utc": "2026-10-08T12:00:00+00:00"}])
        importers.import_content_csv(self.con, p)
        posts = mx.load_posts(self.con).set_index("media_id")
        self.assertAlmostEqual(posts.loc["a", "eng_by_reach_pct"], 2.0)   # (10+2+5+3)/1000*100
        self.assertAlmostEqual(posts.loc["a", "shares_per_1k"], 3.0)
        self.assertTrue(np.isnan(posts.loc["b", "eng_by_reach_pct"]))    # comments missing -> n/a
        self.assertTrue(np.isnan(posts.loc["b", "follows_per_1k"]))      # reels: no attributed follows
        self.assertEqual(str(posts.loc["a", "published_at_london"].tz), "Europe/London")

    def test_metricool_time_is_utc(self):
        t = importers.parse_time("20261026170355", "UTC")
        self.assertEqual(t.isoformat(), "2026-10-26T17:03:55+00:00")

    def test_backtest_has_no_future_leakage(self):
        idx = pd.date_range("2026-01-01", periods=120)
        s = pd.Series(np.arange(120, dtype=float) * 3 + 100, index=idx)
        bt1, _ = fc.backtest(s, "drift_7", 14)
        s2 = s.copy()
        s2.iloc[-14:] += 10_000                              # change only the last 14 days
        bt2, _ = fc.backtest(s2, "drift_7", 14)
        early = bt1["target"] < idx[-14].date()
        self.assertTrue((bt1.loc[early, "pred"].values == bt2.loc[early, "pred"].values).all())

    def test_short_history_is_not_forecast(self):
        idx = pd.date_range("2026-10-01", periods=25)
        daily = pd.DataFrame({"followers_total": np.linspace(3, 146, 25)}, index=idx)
        res = fc.forecast(daily)
        self.assertFalse(res["horizons"][30]["supported"])

    def test_milestones(self):
        path = np.linspace(150, 900, 180)
        ms = fc.milestones("2026-10-26", path, start_total=146)
        self.assertEqual(ms[1000], "Not reached within the modelled horizon")
        ms2 = fc.milestones("2026-10-26", np.linspace(1500, 6000, 180), start_total=1200)
        self.assertEqual(ms2[1000], "already reached")


if __name__ == "__main__":
    unittest.main()


class MetaStore(unittest.TestCase):
    def test_meta_response_is_normalised(self):
        from moodius_growth import meta_api
        con = db.connect(os.path.join(TMP, "meta.sqlite"))
        raw = {"collected_at_utc": "2026-10-27T07:30:00+00:00", "account": {"followers_count": 150, "follows_count": 70},
               "days": {"2026-10-26": {"metrics": {"data": [{"name": "reach", "total_value": {"value": 1301}}]}}},
               "media": [{"id": "m1", "media_product_type": "REELS", "timestamp": "2026-10-26T17:03:55+0000",
                          "insights": {"data": [{"name": "ig_reels_avg_watch_time", "values": [{"value": 3843}]}]}}],
               "stories": []}
        meta_api.store(con, meta_api._save_raw(raw), raw)
        acc, _ = mx.load_account(con)
        self.assertEqual(acc.loc["2026-10-27", "followers_total"], 150)
        self.assertEqual(acc.loc["2026-10-26", "reach"], 1301)
        self.assertNotIn("profile_visits", acc.columns)          # never reported -> absent, not 0
        posts = mx.load_posts(con)
        self.assertAlmostEqual(posts.loc[0, "avg_watch_s"], 3.843)
