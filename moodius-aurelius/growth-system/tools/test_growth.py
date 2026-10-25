#!/usr/bin/env python3
"""Tests for brief_lint.py and analytics.py, on synthetic fixtures only.

Run: python3 -m unittest discover -s moodius-aurelius/growth-system/tools
"""
import datetime as dt
import json
import os
import sqlite3
import tempfile
import unittest

import analytics
import brief_lint

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FIX = os.path.join(ROOT, "fixtures")
EXAMPLES = os.path.join(ROOT, "briefs", "examples")


def load(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
        return json.load(f)


class BriefLintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = brief_lint.load_config()
        cls.lib = brief_lint.load_library([os.path.join(FIX, "tidbits-sample.csv")])

    def test_good_examples_pass(self):
        for name in ("B001-ge-hong-to-tu-youyou.json", "B002-walking-and-mood.json"):
            errors, warnings = brief_lint.lint(load(name), self.cfg, self.lib)
            self.assertEqual(errors, [], name)
            self.assertTrue(any("hand-read" in w for w in warnings), name)

    def test_bad_example_catches_every_rule(self):
        errors, _ = brief_lint.lint(load("B003-bad-example.json"), self.cfg, self.lib)
        text = " | ".join(errors)
        for expected in ("1-3", "end on the question", "HM999", "Historical interest only",
                         "young men", "ancient secret", "faces"):
            self.assertIn(expected, text)

    def test_disclaimer_required_for_health(self):
        brief = load("B002-walking-and-mood.json")
        brief["caption"] = brief["caption"].replace(self.cfg["pillars"]["living_body"]["disclaimer"], "")
        errors, _ = brief_lint.lint(brief, self.cfg, self.lib)
        self.assertTrue(any("needs the line" in e for e in errors))

    def test_book_review_needs_his_reading(self):
        brief = load("B002-walking-and-mood.json")
        brief.update(pillar="reading_room", format="book_review")
        errors, _ = brief_lint.lint(brief, self.cfg, self.lib)
        self.assertTrue(any("read_by_surafel" in e for e in errors))
        brief["read_by_surafel"] = True
        errors, _ = brief_lint.lint(brief, self.cfg, self.lib)
        self.assertEqual(errors, [])

    def test_hashtags_may_follow_question(self):
        brief = load("B001-ge-hong-to-tu-youyou.json")
        self.assertTrue(brief["caption"].rstrip().endswith("#tuyouyou"))
        errors, _ = brief_lint.lint(brief, self.cfg, self.lib)
        self.assertEqual(errors, [])

    def test_faces_allowed_only_by_hand(self):
        brief = load("B002-walking-and-mood.json")
        brief["visual"]["faces"] = True
        self.assertTrue(any("faces" in e for e in brief_lint.lint(brief, self.cfg, self.lib)[0]))
        brief["made_by_hand"] = True
        self.assertEqual(brief_lint.lint(brief, self.cfg, self.lib)[0], [])


class AnalyticsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.posts, self.by_pillar, self.by_kind, self.recs = analytics.run(
            os.path.join(FIX, "ig-export-sample.csv"), None, os.path.join(FIX, "tags-sample.csv"),
            self.tmp, dt.date(2026, 10, 25))

    def test_outputs_written(self):
        for name in ("moodius.sqlite", "dashboard.html", "weekly.md"):
            self.assertTrue(os.path.exists(os.path.join(self.tmp, name)), name)
        con = sqlite3.connect(os.path.join(self.tmp, "moodius.sqlite"))
        self.assertEqual(con.execute("select count(*) from posts").fetchone()[0], 6)

    def test_rates_use_summed_denominators(self):
        rp = {r["group"]: r for r in self.by_pillar}["reading_room"]
        # saves 0 + 6 over reach 8 + 380
        self.assertAlmostEqual(rp["saves_per_1k"], 1000 * 6 / 388)
        self.assertEqual(rp["confidence"], "lead only")

    def test_reel_follows_are_not_guessed(self):
        reels = [p for p in self.posts if p["kind"] == "reel"]
        self.assertTrue(reels)
        self.assertTrue(all(p["follows"] is None for p in reels))
        rk = {r["group"]: r for r in self.by_kind}["reel"]
        self.assertIsNone(rk["follows_per_1k"])

    def test_recommendations_flag_small_sample_and_balance(self):
        self.assertIn("Sample is small", self.recs)
        self.assertIn("The Good Life: 1 of 3", self.recs)
        self.assertIn("first-aid book", self.recs.split("follow-up")[1].splitlines()[1])

    def test_post_log_fills_gaps_but_export_wins(self):
        log = os.path.join(self.tmp, "log.csv")
        with open(log, "w", encoding="utf-8") as f:
            f.write("post_id,brand,date,slot,type,hook_text,views,reach,hold_3s_pct,avg_watch_s\n"
                    "x,moodius,2026-10-21,18:00,REEL,SYNTHETIC: Your brain treats giving like getting.,1,999,41,5.2\n")
        posts, *_ = analytics.run(os.path.join(FIX, "ig-export-sample.csv"), log,
                                  os.path.join(FIX, "tags-sample.csv"), self.tmp, dt.date(2026, 10, 25))
        p = next(p for p in posts if p["hook"].startswith("SYNTHETIC: Your brain"))
        self.assertEqual(p["reach"], 300)
        self.assertEqual(p["hold_3s_pct"], 41)
        self.assertEqual(len(posts), 6)


if __name__ == "__main__":
    unittest.main()
