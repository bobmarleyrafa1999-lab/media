"""Core tests: python3 -m unittest discover -s tests  (stdlib only, no network)."""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from hookintel import db, hooks, ingest, patterns, performance, reels, report  # noqa: E402

FIXTURE = {
    "fetched_at": "2026-10-22T12:00:00+00:00",
    "youtube_search": [
        {"id": "s1", "title": "Why you push away the people who love you #psychology", "duration": 41, "view_count": 90000,
         "channel_id": "UCa", "channel": "Chan A", "_route": "ytsearch", "_query": "attachment"},
        {"id": "long", "title": "A two hour lecture", "duration": 7200, "view_count": 5, "channel_id": "UCa", "channel": "Chan A"},
    ],
    "youtube_channels": [{
        "ref": "@a", "channel_id": "UCa", "channel": "Chan A", "handle": "@a", "followers": 50000,
        "shorts": [{"id": f"x{i}", "views": v} for i, v in enumerate([1000, 2000, 3000, 4000, 5000, 6000])],
        "rss": [
            {"id": "r1", "title": "Stop calling it discipline. It's self-respect.", "url": "https://www.youtube.com/shorts/r1",
             "is_short": True, "published": "2026-10-10T10:00:00+00:00", "views": 35000, "rating_count": 900},
            {"id": "r2", "title": "Long video", "url": "https://www.youtube.com/watch?v=r2", "is_short": False,
             "published": "2026-10-11T10:00:00+00:00", "views": 10},
            {"id": "r3", "title": "When you still check their profile at 2am", "url": "https://www.youtube.com/shorts/r3",
             "is_short": True, "published": "2026-05-01T10:00:00+00:00", "views": 1000, "rating_count": 20},
        ]}],
    "tiktok": {"someone": [{"id": f"t{i}", "title": "Never argue with a woman, do this instead", "timestamp": 1760000000,
                            "duration": 30, "view_count": v, "like_count": 10, "comment_count": 1,
                            "url": f"https://www.tiktok.com/@someone/video/t{i}"} for i, v in enumerate([10, 20, 30, 40, 50])]},
    "podcasts": {"stoicism": [{"trackName": "Ep 1", "collectionName": "Pod", "releaseDate": "2026-10-01T00:00:00Z",
                               "trackTimeMillis": 3600000, "trackViewUrl": "https://podcasts.apple.com/x"}]},
    "full": {},
}


def script(**over):
    s = {
        "id": "T01", "slug": "test", "title": "Test", "pattern_id": "contrarian:negation_reframe", "pillar": "Identity",
        "format": "R2", "hooks": ["You checked their profile again.", "Their profile. Again. At 2am.", "What were you hoping to find?"],
        "cards": [["You checked their profile again.", 2.2, "hook"], ["Not to see them. To see if they're fine without you.", 3.4, "body"],
                  ["That's the question you're really asking.", 2.6, "body"], ["BUT\nIt isn't about them.", 2.4, "labelled"],
                  ["It's whether you're allowed to be fine too.", 2.8, "body"],
                  ["Idea: Bowlby, attachment theory (1969) · Moodius words", 2.0, "cite"],
                  ["Send this to the one who still checks.", 2.4, "cta"]],
        "shots": [{"card": i + 1, "visual": "rain on a window, night", "rights": "own footage"} for i in range(7)],
        "broll_keywords": ["rain window night"], "first_frame": "dark window, phone glow", "sound": "low room tone",
        "caption": "What were you hoping to find?", "first_comment": "One word.", "hashtags": ["#a", "#b", "#c"],
        "intended_emotion": "recognition", "save_share_reason": "names a private habit",
        "source": {"type": "idea", "author": "John Bowlby", "work": "Attachment", "section": "1969", "translation": "n/a"},
        "rules": {str(i): True for i in range(1, 8)}}
    s.update(over)
    return s


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.con = db.connect(os.path.join(self.tmp, "t.db"))
        path = os.path.join(self.tmp, "cycle1", "fetch.json")
        os.makedirs(os.path.dirname(path))
        json.dump(FIXTURE, open(path, "w"))
        ingest.ingest_fetch(self.con, path)


class TestIngest(Base):
    def test_short_form_only_and_baseline(self):
        ids = {r["id"] for r in db.rows(self.con, "SELECT id FROM videos WHERE platform='youtube'")}
        self.assertEqual(ids, {"youtube:r1", "youtube:r3", "youtube:s1"})       # long-form dropped
        r1 = db.rows(self.con, "SELECT * FROM videos WHERE id='youtube:r1'")[0]
        self.assertEqual(r1["creator_median_views"], 3500)                     # median of 6 Shorts
        self.assertEqual(r1["outlier_ratio"], 10.0)
        self.assertEqual(r1["in_window"], 1)
        r3 = db.rows(self.con, "SELECT * FROM videos WHERE id='youtube:r3'")[0]
        self.assertEqual(r3["in_window"], 0)                                   # older than 90 days

    def test_missing_metrics_are_null_not_invented(self):
        s1 = db.rows(self.con, "SELECT * FROM videos WHERE id='youtube:s1'")[0]
        self.assertIsNone(s1["published"])                                     # search route has no date
        self.assertIsNone(s1["comments"])
        self.assertIn("published", json.loads(s1["missing"]))

    def test_small_baseline_gives_no_outlier(self):
        con = db.connect(os.path.join(self.tmp, "u.db"))
        fx = json.loads(json.dumps(FIXTURE))
        fx["youtube_channels"][0]["shorts"] = fx["youtube_channels"][0]["shorts"][:3]
        p = os.path.join(self.tmp, "c2", "fetch.json"); os.makedirs(os.path.dirname(p)); json.dump(fx, open(p, "w"))
        ingest.ingest_fetch(con, p)
        self.assertIsNone(db.rows(con, "SELECT outlier_ratio FROM videos WHERE id='youtube:r1'")[0]["outlier_ratio"])

    def test_manual_csv(self):
        p = os.path.join(self.tmp, "m.csv")
        open(p, "w").write("url,platform,creator,views,first_onscreen\nhttps://www.instagram.com/reel/ABC/,instagram,x,1200,You never asked why\n")
        self.assertEqual(ingest.ingest_manual(self.con, p), 1)
        r = db.rows(self.con, "SELECT * FROM videos WHERE id='instagram:ABC'")[0]
        self.assertEqual(r["first_onscreen"], "You never asked why")


class TestHooks(Base):
    def test_classify(self):
        self.assertEqual(hooks.classify("Stop calling it discipline. It's self-respect.")["category"], "contrarian")
        self.assertEqual(hooks.classify("When you still check their profile at 2am")["category"], "emotional_recognition")
        self.assertEqual(hooks.classify("People who over-apologise usually learned it as children")["category"],
                         "psychological_revelation")
        self.assertEqual(hooks.classify("When did you last cry in front of someone?")["category"] in
                         ("unexpected_question", "emotional_recognition"), True)
        self.assertEqual(hooks.classify("The more you chase calm, the less calm you have")["category"], "philosophical_paradox")

    def test_structure(self):
        self.assertEqual(hooks.structure("3 Stoic rules for overthinkers"), "list_opener")
        self.assertEqual(hooks.structure("Someone disrespected you today?"), "question")

    def test_hook_text_prefers_spoken_and_labels_title_proxy(self):
        t, src = hooks.hook_text({"title": "A title #tag", "first_spoken": None})
        self.assertEqual((t, src), ("A title", "title (proxy: not the spoken hook)"))
        t, src = hooks.hook_text({"title": "x", "first_spoken": "I almost didn't post this."})
        self.assertEqual(src, "first spoken sentence")

    def test_scores_and_off_brand(self):
        good, total_good, *_ = hooks.score("You checked their profile again at 2am.")
        bad, total_bad, _, _, _, flags = hooks.score("Never argue with a woman, alpha mindset")
        self.assertEqual(bad["alignment"], 0)
        self.assertIn("off_brand", flags)
        self.assertGreater(total_good, total_bad)
        for v in good.values():
            self.assertTrue(0 <= v <= 5)

    def test_priority_prefers_outliers(self):
        self.assertGreater(hooks.priority(8, 50), hooks.priority(1, 80))
        self.assertEqual(hooks.priority(None, 50), hooks.priority(1, 50))

    def test_analyse_and_patterns(self):
        n = hooks.analyse(self.con)
        self.assertGreaterEqual(n, 3)
        h = db.rows(self.con, "SELECT * FROM hooks WHERE video_id='youtube:r1'")[0]
        self.assertEqual(h["strong"], 1)
        tk = db.rows(self.con, "SELECT * FROM hooks WHERE video_id LIKE 'tiktok:%'")[0]
        self.assertIn("off_brand", tk["flags"])
        top, allp = patterns.build(self.con)
        self.assertTrue(all("off_brand" not in json.dumps(p["examples"]) for p in allp))
        self.assertEqual(top[0]["rank"], 1)
        self.assertTrue(db.search(self.con, "profile"))


class TestReels(unittest.TestCase):
    def test_valid_script(self):
        err, warn = reels.validate(script())
        self.assertEqual(err, [])

    def test_rejections(self):
        self.assertTrue(any("3 hooks" in e for e in reels.validate(script(hooks=["a", "b"]))[0]))
        self.assertTrue(any("too fast" in e for e in reels.validate(script(cards=[["one two three four five six seven eight nine ten", 0.8, "hook"]] + script()["cards"][1:]))[0]))
        self.assertTrue(any("hold rules" in e for e in reels.validate(script(rules={"1": True, "2": True}))[0]))
        self.assertTrue(any("off-brand" in e for e in reels.validate(script(caption="be an alpha"))[0]))
        self.assertTrue(any("rights" in e for e in reels.validate(script(shots=[{"card": i + 1, "visual": "x"} for i in range(7)]))[0]))

    def test_timeline_and_srt_per_variant(self):
        s = script()
        tl = reels.timeline(s, 2)
        self.assertEqual(tl[0]["text"], s["hooks"][2])
        self.assertIn("00:00:00,000 -->", reels.srt(tl))
        e = reels.engine_script(s, "b")
        self.assertEqual(e["id"], "T01b")
        self.assertEqual(e["cards"][0][0], s["hooks"][1])

    def test_build_writes_outputs(self):
        tmp = tempfile.mkdtemp()
        con = db.connect(os.path.join(tmp, "t.db"))
        p = os.path.join(tmp, "b.json")
        json.dump({"batch": "test", "scripts": [script()]}, open(p, "w"))
        summary, note, out = reels.build(con, p, out_dir=os.path.join(tmp, "out"), run_engine=False)
        self.assertEqual(summary[0]["errors"], [])
        self.assertTrue(os.path.exists(os.path.join(out, "T01.md")))
        self.assertTrue(os.path.exists(os.path.join(out, "srt", "T01c.srt")))
        self.assertEqual(db.rows(con, "SELECT status FROM concepts")[0]["status"], "draft")


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.con = db.connect(os.path.join(self.tmp, "t.db"))
        rows = [[f"2026101{i}160000", f"Hook {i}\n\nbody", f"https://www.instagram.com/reel/P{i}/", "1", "4", str(100 + i * 10),
                 "1", "1", "140", str(4 + i), None, None, str(30 + i * 3), None] for i in range(6)]
        p = os.path.join(self.tmp, "m.json")
        json.dump({"fields": ["IGRE02", "IGRE03", "IGRE06", "IGRE07", "IGRE10", "IGRE11", "IGRE12", "IGRE21", "IGRE23",
                              "IGRE24", "IGRE26", "IGRE27", "IGRE28", "IGRE29"], "rows": rows}, open(p, "w"))
        ingest.ingest_metricool(self.con, p)

    def test_baseline_and_missing(self):
        b = performance.baseline(self.con)
        self.assertEqual(b["n"], 6)
        self.assertAlmostEqual(b["metrics"]["view_rate_3s"]["median"], 37.5)
        self.assertIn("follows_per_1k_reach", b["missing"])          # never invented

    def test_two_prop(self):
        d, p = performance.two_prop(450, 1000, 380, 1000)
        self.assertLess(p, 0.01)
        d, p = performance.two_prop(5, 10, 4, 10)
        self.assertGreater(p, 0.5)

    def test_experiment_labels(self):
        os.makedirs(os.path.join(self.tmp, "experiments"))
        db.upsert(self.con, "experiments", {"id": "X6-T", "hypothesis": "h"})
        db.upsert(self.con, "variants", {"experiment_id": "X6-T", "variant": "a", "post_url": "https://www.instagram.com/reel/P0/"},
                  key=("experiment_id", "variant"))
        db.upsert(self.con, "variants", {"experiment_id": "X6-T", "variant": "b", "post_url": "https://www.instagram.com/reel/P5/"},
                  key=("experiment_id", "variant"))
        r = performance.review_experiment(self.con, "X6-T", performance.baseline(self.con))
        self.assertEqual(r["status"], "complete")
        self.assertTrue(r["tests"][0]["label"].startswith(("hypothesis", "evidence")))

    def test_weekly_plan_is_proposal(self):
        con = self.con
        db.upsert(con, "concepts", {"id": "T01", "status": "draft", "data": script()})
        out, plan = report.weekly_plan(con, "2026-11-30", out=os.path.join(self.tmp, "plan.md"))
        self.assertEqual(len(plan), 3)
        self.assertEqual({p["variant"] for p in plan}, {"A", "B", "C"})
        self.assertEqual(len({p["date"] for p in plan}), 3)          # one hook-intel reel per day
        self.assertIn("Nothing here is scheduled", open(out).read())


class TestDashboard(Base):
    def test_static_dashboard(self):
        from hookintel import dashboard
        hooks.analyse(self.con)
        patterns.build(self.con)
        out = dashboard.write_static(self.con, os.path.join(self.tmp, "d.html"))
        html = open(out).read()
        self.assertNotIn("/*__DATA__*/null", html)
        for tab in ("Discover", "Analyse", "Create", "Library", "Performance"):
            self.assertIn(tab, html)


if __name__ == "__main__":
    unittest.main()
