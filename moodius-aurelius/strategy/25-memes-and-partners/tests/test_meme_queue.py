import os, sys, json, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import meme_queue as mq


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        mq.LEARNED = os.path.join(self.tmp, "learned.json")


class Dedupe(Base):
    def test_instagram_variants_match(self):
        a = mq.url_key("https://www.instagram.com/p/ABC123/?igsh=xyz")
        b = mq.url_key("https://instagram.com/someone/reel/ABC123")
        self.assertEqual(a, b)

    def test_tracking_params_dropped(self):
        self.assertEqual(mq.url_key("https://example.com/x/?utm_source=a&id=2"),
                         mq.url_key("https://example.com/x?id=2"))

    def test_import_skips_duplicates(self):
        p = os.path.join(self.tmp, "links.txt")
        open(p, "w").write("https://instagram.com/p/AAA/ | someone | joke one\n"
                           "https://www.instagram.com/p/AAA/?igsh=1 | someone | joke one\n"
                           "https://instagram.com/p/BBB/ | other | a different joke\n")
        rows = []
        added, dups = mq.import_file(p, rows)
        self.assertEqual((added, dups), (2, 1))


class Gates(Base):
    def row(self, **kw):
        r = {"id": "C001", "kind": "candidate", "image_context": "plain photo of a desk"}
        r.update(kw)
        return r

    def test_permission_needed_blocks(self):
        self.assertIn("no written permission yet", mq.gate(self.row(reuse_status="permission-needed")))

    def test_inspiration_only_cannot_be_reposted(self):
        self.assertTrue(mq.gate(self.row(reuse_status="inspiration-only")))

    def test_attribution_alone_is_not_permission(self):
        g = mq.gate(self.row(reuse_status="authorised", creator="someone"))
        self.assertTrue(any("commercial" in x for x in g))
        self.assertTrue(any("watermark" in x for x in g))

    def test_full_permission_passes(self):
        r = self.row(reuse_status="authorised", creator="someone", licence_commercial="yes",
                     licence_edits="yes", watermark_kept="yes", permission_ref="DM 27 Oct screenshot")
        self.assertEqual(mq.gate(r), [])

    def test_image_context_required_for_found_items(self):
        r = self.row(reuse_status="authorised", creator="x", licence_commercial="yes", licence_edits="yes",
                     watermark_kept="yes", permission_ref="email", image_context="")
        self.assertTrue(any("image" in x for x in mq.gate(r)))

    def test_high_score_does_not_override_gate(self):
        rows = [self.row(reuse_status="permission-needed", humour="5", relevance="5", thought="5")]
        done, blocked = mq.decide(rows, "approve", {"C001"})
        self.assertEqual(done, [])
        self.assertIn("C001", blocked)


class Flags(Base):
    def test_flags_need_review(self):
        self.assertIn("gender-war", mq.flags_for({"setup": "Women are", "punch": "..."}))
        self.assertIn("health-claim", mq.flags_for({"caption": "This cures anxiety"}))
        self.assertIn("body-shaming", mq.flags_for({"image_context": "fat man at the gym"}))

    def test_image_context_is_screened_too(self):
        self.assertTrue(mq.flags_for({"setup": "harmless", "image_context": "photo from a terror attack"}))

    def test_all_concepts_are_clean(self):
        rows = []
        mq.CONCEPTS = os.path.join(os.path.dirname(__file__), "..", "data", "concepts.json")
        self.assertEqual(mq.load_concepts(rows), 20)
        self.assertEqual([r["id"] for r in rows if r["flags"]], [])
        self.assertTrue(all(mq.gate(r) == [] for r in rows))


class Inspire(Base):
    def test_copying_a_caption_is_caught(self):
        rows = [{"id": "C001", "kind": "candidate", "caption": "buying another book to fix not reading my books"}]
        new, sim = mq.inspire(rows, "C001", "MX01", "Buying another book", "to fix not reading my books")
        self.assertGreaterEqual(sim, mq.TOO_CLOSE)
        self.assertIn("too-close", new["flags"])
        self.assertTrue(mq.gate(new))

    def test_genuinely_new_joke_passes(self):
        rows = [{"id": "C001", "kind": "candidate", "caption": "buying another book to fix not reading my books"}]
        new, sim = mq.inspire(rows, "C001", "MX01", "My to-read pile", "is now load-bearing.")
        self.assertLess(sim, mq.TOO_CLOSE)


class Learn(Base):
    def test_learning_changes_order_only(self):
        rows = [{"id": f"X{i}", "theme": "gym", "decision": "reject", "decision_note": "too cheesy"} for i in range(4)]
        out = mq.learn(rows)
        self.assertLess(out["theme_weight"]["gym"], 1.0)
        self.assertGreaterEqual(out["theme_weight"]["gym"], 0.7)
        self.assertIn("unchanged", out["standards"])
        # a gated item still cannot be approved after learning
        r = {"id": "C9", "kind": "candidate", "reuse_status": "permission-needed", "image_context": "x"}
        self.assertTrue(mq.gate(r))

    def test_few_decisions_learn_nothing(self):
        out = mq.learn([{"id": "X", "theme": "gym", "decision": "reject"}])
        self.assertEqual(out["theme_weight"], {})


class Render(Base):
    def test_renders_every_concept(self):
        data = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "concepts.json")))["concepts"]
        for c in data:
            p = mq.render(c, self.tmp)
            self.assertTrue(os.path.getsize(p) > 5000)


if __name__ == "__main__":
    unittest.main()
