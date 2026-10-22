#!/usr/bin/env python3
"""Tests for engine 1.3 (beat grammar, QC, quote check). No rendering, no network if .sources is cached.

    python3 -m unittest tools/test_engine.py
"""
import json, os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine, quotes  # noqa: E402


def script(**kw):
    s = {"id": "T001", "slug": "test", "grammar": "beat",
         "cards": [["You'd never let a stranger decide what you're worth.", 2.4, "hook"],
                   ["Then you post something and refresh it forty times.", 2.4, "body"],
                   ["Whose opinion of you do you check first?", 2.4, "quiz"],
                   ["Not your own.\nA stranger's.", 2.0, "reveal"],
                   ["Before a stranger decides, decide what you're worth.", 2.3, "body"],
                   ["Send this to the friend who refreshes.", 1.8, "cta"]],
         "source": {"type": "original"}, "caption": "What would you post?", "first_comment": "x",
         "hashtags": [], "doctor": {"score": 80, "issues": []}}
    s.update(kw)
    return s


class Beat(unittest.TestCase):
    def test_frame0_hook_has_no_fade_in(self):
        segs, total = engine.plan(script())
        hook = [s for s in segs if s["card"] == 0 and s["role"] == "text"]
        self.assertTrue(hook and all(s["t0"] == 0.0 and s["rise"] == "0" for s in hook))
        self.assertNotIn("lt(t-", hook[0]["alpha"])

    def test_loop_redraws_hook_at_the_end(self):
        segs, total = engine.plan(script())
        loop = [s for s in segs if s["card"] == -1 and s["role"] == "text"]
        self.assertEqual(len(loop), len([s for s in segs if s["card"] == 0 and s["role"] == "text"]))
        self.assertAlmostEqual(loop[0]["t0"], total - engine.LOOP_S)

    def test_classic_timing_unchanged(self):
        s = script()
        s.pop("grammar")
        self.assertEqual(engine.timing(s), (0.2, sum(d for _, d, _ in s["cards"]) + 0.4))

    def test_reveal_steps_appear_in_turn(self):
        segs, _ = engine.plan(script())
        starts = [s["t0"] for s in segs if s["card"] == 3 and s["role"] == "text"]
        self.assertEqual(len(starts), 2)
        self.assertLess(starts[0], starts[1])

    def test_good_script_passes(self):
        err, _ = engine.qc(script(), {})
        self.assertEqual(err, [])

    def test_quiz_rules(self):
        s = script()
        s["cards"][2] = ["Whose opinion do you check first", 1.2, "quiz"]
        err, _ = engine.qc(s, {})
        self.assertTrue(any("question" in e for e in err) and any("lasts" in e for e in err))

    def test_low_doctor_score_blocks(self):
        err, _ = engine.qc(script(doctor={"score": 55, "issues": ["weak hook"]}), {})
        self.assertTrue(any("Script Doctor" in e for e in err))


class Quotes(unittest.TestCase):
    def test_punctuation_blind_but_word_strict(self):
        ok = quotes.check("Meditations", "5.1", "George Long",
                          "In the morning when thou risest unwillingly, let this thought be present: I am rising to the work of a human being.")
        bad = quotes.check("Enchiridion", "11", "George Long", "Never say about anything, ‘I have lost it,’ but rather ‘I have restored it.’")
        if "manual" in (ok[0], bad[0]):
            self.skipTest("source text not reachable")
        self.assertEqual(ok[0], "ok")
        self.assertEqual(bad[0], "missing")

    def test_unknown_source_is_manual(self):
        self.assertEqual(quotes.check("Moral Letters to Lucilius", "7.8", "Gummere", "x")[0], "manual")


if __name__ == "__main__":
    unittest.main()
