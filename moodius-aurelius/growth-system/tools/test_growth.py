#!/usr/bin/env python3
"""Tests for the growth-system tools, on synthetic fixtures only.

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
LIB = [os.path.join(FIX, "tidbits-sample.csv")]


def load(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
        return json.load(f)


class BriefLintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = brief_lint.load_config()
        cls.lib = brief_lint.load_library(LIB)

    def errors(self, brief):
        return brief_lint.lint(brief, self.cfg, self.lib)[0]

    def test_three_pillars(self):
        self.assertEqual(sorted(self.cfg["pillars"]), ["body", "mind", "people"])
        self.assertAlmostEqual(sum(p["share"] for p in self.cfg["pillars"].values()), 1.0)

    def test_good_examples_pass(self):
        for name in ("B001-ge-hong-to-tu-youyou.json", "B002-walking-and-mood.json"):
            errors, warnings = brief_lint.lint(load(name), self.cfg, self.lib)
            self.assertEqual(errors, [], name)
            self.assertTrue(any("hand-read" in w for w in warnings), name)

    def test_bad_example_catches_every_rule(self):
        text = " | ".join(self.errors(load("B003-bad-example.json")))
        for expected in ("1-3", "end on the question", "HM999", "evidence_label", "Historical interest only",
                         "young men", "ancient secret", "faces"):
            self.assertIn(expected, text)

    def test_medical_history_needs_its_line(self):
        brief = load("B001-ge-hong-to-tu-youyou.json")
        brief["caption"] = brief["caption"].replace(self.cfg["medical_history_disclaimer"], "")
        self.assertTrue(any("medical history needs the line" in e for e in self.errors(brief)))

    def test_body_needs_evidence_label_and_no_doses(self):
        brief = load("B002-walking-and-mood.json")
        del brief["evidence_label"]
        self.assertTrue(any("evidence_label" in e for e in self.errors(brief)))
        brief = load("B002-walking-and-mood.json")
        brief["explanation"] += " Take 500 mg of turmeric daily."
        self.assertTrue(any("no doses" in e for e in self.errors(brief)))

    def test_series_must_fit_pillar_and_format(self):
        brief = load("B002-walking-and-mood.json")
        brief["pillar"] = "people"
        self.assertTrue(any("Claim Check runs in" in e for e in self.errors(brief)))

    def test_scene_needs_film_credit(self):
        brief = load("B002-walking-and-mood.json")
        brief.update(pillar="mind", series="S2")
        self.assertTrue(any("film.title" in e for e in self.errors(brief)))
        brief["film"] = {"title": "Groundhog Day", "year": 1993, "director": "Harold Ramis"}
        self.assertEqual(self.errors(brief), [])

    def test_book_review_needs_his_reading(self):
        brief = load("B002-walking-and-mood.json")
        brief.update(pillar="mind", series="S1", format="book_review", book_label="Moodius review (read it)")
        self.assertTrue(any("read_by_surafel" in e for e in self.errors(brief)))
        brief["read_by_surafel"] = True
        self.assertEqual(self.errors(brief), [])
        brief.update(format="carousel", book_label="Researched introduction", read_by_surafel=False)
        self.assertEqual(self.errors(brief), [])

    def test_hashtags_may_follow_question(self):
        brief = load("B001-ge-hong-to-tu-youyou.json")
        self.assertTrue(brief["caption"].rstrip().endswith("#tuyouyou"))
        self.assertEqual(self.errors(brief), [])

    def test_faces_allowed_only_by_hand(self):
        brief = load("B002-walking-and-mood.json")
        brief["visual"]["faces"] = True
        self.assertTrue(any("faces" in e for e in self.errors(brief)))
        brief["made_by_hand"] = True
        self.assertEqual(self.errors(brief), [])


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
        mind = {r["group"]: r for r in self.by_pillar}["mind"]
        # saves 1 + 0 + 6 over reach 500 + 8 + 380
        self.assertAlmostEqual(mind["saves_per_1k"], 1000 * 7 / 888)
        self.assertEqual(mind["confidence"], "lead only")

    def test_reel_follows_are_not_guessed(self):
        reels = [p for p in self.posts if p["kind"] == "reel"]
        self.assertTrue(reels)
        self.assertTrue(all(p["follows"] is None for p in reels))
        self.assertIsNone({r["group"]: r for r in self.by_kind}["reel"]["follows_per_1k"])

    def test_recommendations_flag_small_sample_and_balance(self):
        self.assertIn("Sample is small", self.recs)
        self.assertIn("- People: 1 of 2", self.recs)
        self.assertIn("- Mind: 3 of 2", self.recs)
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

    def test_tracker_carries_its_own_tags(self):
        tracker = os.path.join(self.tmp, "tracker.csv")
        with open(tracker, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "slot", "pillar", "series", "format", "hook", "opener_tone", "experiment", "arm",
                        "reach", "views", "likes", "comments", "saves", "shares", "follows"])
            w.writerow(["2026-11-02", "12:00", "People", "Small Good Thing", "carousel", "SYNTHETIC: thanks",
                        "appreciation", "E1", "curiosity", "400", "600", "9", "2", "3", "4", "1"])
            w.writerow(["2026-11-02", "21:00", "Mind", "", "story sequence", "SYNTHETIC: poll", "", "", "",
                        "50", "", "", "", "", "", ""])
        posts, *_ = analytics.run(None, None, None, self.tmp, dt.date(2026, 11, 8), tracker=tracker)
        self.assertEqual(len(posts), 1)
        self.assertEqual((posts[0]["pillar"], posts[0]["arm"], posts[0]["opener_tone"]),
                         ("people", "curiosity", "appreciation"))

    def test_experiment_rule(self):
        exp = os.path.join(ROOT, "experiments.csv")

        def posts(arm, shares, reach=400, n=8):
            return [{"experiment": "E1", "arm": arm, "shares": shares, "reach": reach} for _ in range(n)]

        out = analytics.experiment_readout(posts("tension", 2) + posts("curiosity", 4), exp)
        self.assertIn("lead for curiosity", out.splitlines()[0])
        out = analytics.experiment_readout(posts("tension", 4) + posts("curiosity", 4.8), exp)
        self.assertIn("no clear winner (needs a 30% higher median)", out.splitlines()[0])
        out = analytics.experiment_readout(posts("tension", 2) + posts("curiosity", 4, reach=200), exp)
        self.assertIn("reach median is over 30% lower", out.splitlines()[0])
        out = analytics.experiment_readout(posts("tension", 2, n=3) + posts("curiosity", 4), exp)
        self.assertIn("keep running (3 and 8 of 8 posts per arm)", out.splitlines()[0])
        self.assertIn("E3 (proposed 25 Nov-24 Dec): no posts logged yet", out)


class CommentsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        rows, cls.ideas = comments.run(os.path.join(FIX, "comments-sample.csv"), LIB, cls.tmp)
        cls.by_id = {r["comment_id"]: r for r in rows}

    def test_intents(self):
        want = {"c01": "genuine_question", "c02": "reading_request", "c06": "personal_story",
                "c07": "philosophical_disagreement", "c10": "appreciation", "c11": "spam",
                "c12": "sponsorship", "c13": "crisis", "c14": "criticism"}
        for cid, intent in want.items():
            self.assertEqual(self.by_id[cid]["intent"], intent, cid)

    def test_pillars_are_the_three(self):
        self.assertTrue({r["pillar"] for r in self.by_id.values()} <= {"mind", "body", "people", "unknown"})
        self.assertEqual(self.by_id["c05"]["pillar"], "body")

    def test_human_only_gets_no_draft(self):
        for cid in ("c12", "c13", "c14"):
            r = self.by_id[cid]
            self.assertEqual(r["needs_surafel"], "yes")
            self.assertEqual(r["draft_reply"], "")
        self.assertIn("Samaritans 116 123", self.by_id["c13"]["note"])

    def test_nothing_is_sent(self):
        self.assertTrue(all(r["status"] in ("awaiting_approval", "skip") for r in self.by_id.values()))
        self.assertTrue(all(r["draft_reply"].startswith("DRAFT") or not r["draft_reply"]
                            for r in self.by_id.values()))

    def test_research_retrieval(self):
        self.assertEqual(self.by_id["c01"]["tidbit"], "HM001")
        self.assertEqual(self.by_id["c05"]["tidbit"], "KH004")

    def test_commenter_never_written(self):
        with open(os.path.join(self.tmp, "queue.csv"), encoding="utf-8") as f:
            self.assertNotIn("commenter", f.readline())

    def test_repeated_questions_become_failing_briefs(self):
        self.assertEqual(len(self.ideas), 2)
        with open(os.path.join(self.tmp, "idea-briefs", "IDEA01.json"), encoding="utf-8") as f:
            brief = json.load(f)
        self.assertEqual(len(brief["from_comments"]), 2)
        self.assertTrue(brief_lint.lint(brief, brief_lint.load_config(), {})[0])


class CalendarTest(unittest.TestCase):
    SERIES = {"mind": ("S4", "carousel"), "people": ("S5", "reel"), "body": ("S3", "carousel")}

    def make_briefs(self, folder, n_per_pillar=6, hurt_mind=6):
        base = load("B002-walking-and-mood.json")
        i = 0
        for pillar, (series, fmt) in self.SERIES.items():
            for j in range(n_per_pillar):
                b = json.loads(json.dumps(base))
                b.update(id=f"T{i:02d}", pillar=pillar, series=series,
                         format=fmt if j % 2 == 0 else ("reel" if fmt == "carousel" else "carousel"),
                         opener_tone="hurt" if pillar == "mind" and j < hurt_mind else "curiosity",
                         tradition_source="Zhuangzi ch. 3, tr. Legge")
                with open(os.path.join(folder, f"T{i:02d}.json"), "w", encoding="utf-8") as f:
                    json.dump(b, f)
                i += 1
        with open(os.path.join(folder, "bad.json"), "w", encoding="utf-8") as f:
            json.dump(load("B003-bad-example.json"), f)

    def run_week(self, monday, layout="auto", **kw):
        tmp = tempfile.mkdtemp()
        briefs = os.path.join(tmp, "briefs")
        os.makedirs(briefs)
        self.make_briefs(briefs, **kw)
        return calendar_build.run(briefs, LIB, monday, os.path.join(tmp, "out"), layout) + (tmp,)

    def test_targets_follow_shares(self):
        cfg = brief_lint.load_config()
        self.assertEqual(calendar_build.targets(cfg, 8), {"mind": 3, "body": 2, "people": 3})
        self.assertEqual(calendar_build.targets(cfg, 14), {"mind": 6, "body": 3, "people": 5})

    def test_layouts(self):
        before = calendar_build.week_slots(dt.date(2026, 11, 9))
        self.assertEqual(len(before), 14)
        self.assertEqual([s[3] for s in before].count("carousel"), 7)
        after = calendar_build.week_slots(dt.date(2026, 11, 23))
        self.assertEqual([s[3] for s in after].count("carousel"), 5)
        self.assertEqual([(s[1], s[2]) for s in after if s[3] == "reel"],
                         [("Tue", "18:00"), ("Thu", "18:00"), ("Fri", "17:00")])

    def test_standard_week_meets_mix_and_caps(self):
        plan, need, hurt, rejected, summary, tmp = self.run_week(dt.date(2026, 11, 23), hurt_mind=3)
        self.assertEqual(len(plan), 8)
        filled = [s for s in plan if s["brief"]]
        self.assertEqual(len(filled), 8)
        counts = {k: sum(1 for s in filled if s["brief"]["pillar"] == k) for k in self.SERIES}
        self.assertEqual(counts, {"mind": 3, "body": 2, "people": 3})
        self.assertLessEqual(hurt, 4)
        light = sum(1 for s in filled if s["brief"]["opener_tone"] in ("curiosity", "appreciation"))
        self.assertGreaterEqual(light / len(filled), 2 / 3)
        self.assertEqual([r[0] for r in rejected], ["B003"])
        for s in filled:
            self.assertTrue(calendar_build.fits(s["brief"], s["kind"]))
        with open(os.path.join(tmp, "out", "handoff-2026-11-23.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["status"], "draft_not_scheduled")
        self.assertIn("Nothing is in Metricool", summary)

    def test_tone_shortfall_is_reported(self):
        *_, summary, _ = self.run_week(dt.date(2026, 11, 23), hurt_mind=6)
        self.assertIn("below the rule", summary)

    def test_hurt_cap_on_a_full_week(self):
        plan, need, hurt, *_ = self.run_week(dt.date(2026, 11, 9), n_per_pillar=8, hurt_mind=8)
        self.assertLessEqual(hurt, 4)

    def test_week_must_start_monday(self):
        with self.assertRaises(SystemExit):
            calendar_build.main(["--briefs", EXAMPLES, "--week-start", "2026-11-10", "--out", tempfile.mkdtemp()])


if __name__ == "__main__":
    unittest.main()
