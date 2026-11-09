#!/usr/bin/env python3
"""Tests for library.py. Needs raw.githubusercontent.com (reachable from the project container)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library as L

BASE = dict(id="T1", figure="Test", topic="t", claim="c", kind="text", source="discourses", locator="1.18",
            author="Epictetus", translator="Long", link="https://example.org", licence="CC0", tier="primary",
            caveat="", verified_by="", verified_at="", status="", use_in="")


class TestCheck(unittest.TestCase):
    def test_exact_words_pass(self):
        r = dict(BASE, evidence="for a man only loses that which he has")
        self.assertEqual(L.check_tidbit(r)[0], "ok")

    def test_reworded_quote_fails(self):
        r = dict(BASE, evidence="for a man only loses what he has")
        self.assertEqual(L.check_tidbit(r)[0], "fail")

    def test_wrong_section_fails_and_points_to_right_one(self):
        r = dict(BASE, locator="1.17", evidence="for a man only loses that which he has")
        status, detail = L.check_tidbit(r)
        self.assertEqual(status, "fail")
        self.assertIn("1.18", detail)

    def test_ellipsis_segments(self):
        r = dict(BASE, source="enchiridion", locator="5",
                 evidence="Men are disturbed not by the things which happen ... the opinion about death, that it is terrible, is the terrible thing")
        self.assertEqual(L.check_tidbit(r)[0], "ok")

    def test_web_needs_reader_and_date(self):
        r = dict(BASE, kind="web", source="Some book", locator="p. 1", evidence="x")
        self.assertEqual(L.check_tidbit(r)[0], "fail")
        r.update(verified_by="Claude", verified_at="2026-10-22")
        self.assertEqual(L.check_tidbit(r)[0], "manual")

    def test_gellius_keeps_text_after_footnotes(self):
        r = dict(BASE, source="attic-nights", locator="15.11",
                 evidence="Epictetus also withdrew from Rome to Nicopolis")
        self.assertEqual(L.check_tidbit(r)[0], "ok")

    def test_library_has_no_failures(self):
        self.assertEqual(L.cmd_verify([]), 0)


if __name__ == "__main__":
    unittest.main()
