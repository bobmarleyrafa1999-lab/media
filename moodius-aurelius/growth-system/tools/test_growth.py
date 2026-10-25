#!/usr/bin/env python3
"""Tests for brief_lint.py and analytics.py, on synthetic fixtures only.

Run: python3 -m unittest discover -s moodius-aurelius/growth-system/tools
"""
import csv
import datetime as dt
import json
import os
import sqlite3
import tempfile
import unittest

import analytics
import brief_lint
import calendar_build
import comments

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
        con.close()

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


    def test_experiment_readout_follows_the_rule(self):
        tags = os.path.join(self.tmp, "tags-x.csv")
        with open(os.path.join(FIX, "tags-sample.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        rows[0].update(experiment="X7", arm="forgotten_knowledge")
        rows[5].update(experiment="X7", arm="human_mind")
        with open(tags, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))  # rows[0] now carries experiment, arm
            w.writeheader()
            w.writerows(rows)
        _, _, _, recs = analytics.run(os.path.join(FIX, "ig-export-sample.csv"), None, tags, self.tmp,
                                      dt.date(2026, 10, 25), os.path.join(ROOT, "experiments-proposed.csv"))
        line = next(l for l in recs.splitlines() if l.startswith("- X7"))
        self.assertIn("keep running (1 and 1 of 6 posts per arm)", line)
        self.assertIn("X8 (proposed): no posts logged yet", recs)


class CommentsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        rows, cls.ideas = comments.run(os.path.join(FIX, "comments-sample.csv"),
                                       [os.path.join(FIX, "tidbits-sample.csv")], cls.tmp)
        cls.by_id = {r["comment_id"]: r for r in rows}

    def test_intents(self):
        want = {"c01": "genuine_question", "c02": "reading_request", "c06": "personal_story",
                "c07": "philosophical_disagreement", "c10": "appreciation", "c11": "spam",
                "c12": "sponsorship", "c13": "crisis", "c14": "criticism"}
        for cid, intent in want.items():
            self.assertEqual(self.by_id[cid]["intent"], intent, cid)

    def test_human_only_gets_no_draft(self):
        for cid in ("c12", "c13", "c14"):
            r = self.by_id[cid]
            self.assertEqual(r["needs_surafel"], "yes")
            self.assertEqual(r["draft_reply"], "")
        self.assertIn("Samaritans 116 123", self.by_id["c13"]["note"])

    def test_nothing_is_sent(self):
        self.assertTrue(all(r["status"] in ("awaiting_approval", "skip") for r in self.by_id.values()))
        self.assertTrue(all(r["draft_reply"].startswith("DRAFT") or not r["draft_reply"] for r in self.by_id.values()))

    def test_research_retrieval_and_health_disclaimer(self):
        self.assertEqual(self.by_id["c01"]["tidbit"], "HM001")
        c05 = self.by_id["c05"]
        self.assertEqual(c05["tidbit"], "KH004")
        self.assertIn("not medical advice", c05["draft_reply"])

    def test_commenter_never_written(self):
        with open(os.path.join(self.tmp, "queue.csv"), encoding="utf-8") as f:
            header = f.readline()
        self.assertNotIn("commenter", header)

    def test_repeated_questions_become_failing_briefs(self):
        self.assertEqual(len(self.ideas), 2)
        cfg, lib = brief_lint.load_config(), {}
        with open(os.path.join(self.tmp, "idea-briefs", "IDEA01.json"), encoding="utf-8") as f:
            brief = json.load(f)
        self.assertEqual(len(brief["from_comments"]), 2)
        self.assertTrue(brief_lint.lint(brief, cfg, lib)[0])


class CalendarTest(unittest.TestCase):
    def make_briefs(self, folder):
        base = load("B002-walking-and-mood.json")
        pillars = ["human_mind"] * 6 + ["good_life"] * 4 + ["reading_room"] * 4 + ["living_body"] * 3 + \
                  ["forgotten_knowledge"] * 3
        cfg = brief_lint.load_config()
        for i, p in enumerate(pillars):
            b = json.loads(json.dumps(base))
            b.update(id=f"T{i:02d}", pillar=p, format="carousel" if i % 5 == 0 else "reel",
                     hurt_conflict=(p == "human_mind"))
            if cfg["pillars"][p].get("needs_disclaimer"):
                b["caption"] = b["caption"].replace(cfg["pillars"]["living_body"]["disclaimer"],
                                                    cfg["pillars"][p]["disclaimer"])
            else:
                b["caption"] = b["caption"].replace(cfg["pillars"]["living_body"]["disclaimer"], "")
            with open(os.path.join(folder, f"T{i:02d}.json"), "w", encoding="utf-8") as f:
                json.dump(b, f)
        with open(os.path.join(folder, "bad.json"), "w", encoding="utf-8") as f:
            json.dump(load("B003-bad-example.json"), f)

    def test_week_meets_mix_and_cap(self):
        tmp = tempfile.mkdtemp()
        briefs = os.path.join(tmp, "briefs")
        os.makedirs(briefs)
        self.make_briefs(briefs)
        plan, need, hurt, rejected, summary = calendar_build.run(
            briefs, [os.path.join(FIX, "tidbits-sample.csv")], dt.date(2026, 11, 9), os.path.join(tmp, "out"))
        self.assertEqual(len(plan), 14)
        self.assertEqual(sum(1 for s in plan if s["kind"] == "carousel"), 2)
        self.assertLessEqual(hurt, 3)
        self.assertEqual([r[0] for r in rejected], ["B003"])
        filled = [s for s in plan if s["brief"]]
        for s in filled:
            self.assertTrue(calendar_build.fits(s["brief"], s["kind"]))
        with open(os.path.join(tmp, "out", "handoff-2026-11-09.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["status"], "draft_not_scheduled")
        self.assertIn("Nothing is in Metricool", summary)

    def test_week_must_start_monday(self):
        with self.assertRaises(SystemExit):
            calendar_build.main(["--briefs", EXAMPLES, "--week-start", "2026-11-10", "--out", tempfile.mkdtemp()])


if __name__ == "__main__":
    unittest.main()
