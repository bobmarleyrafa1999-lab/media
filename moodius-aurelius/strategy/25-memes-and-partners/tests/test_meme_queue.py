import os, sys, json, shutil, tempfile, unittest

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


HERE = os.path.dirname(os.path.abspath(__file__))
RENDERS = os.path.join(HERE, "..", "renders")
CONCEPTS = json.load(open(os.path.join(HERE, "..", "data", "concepts.json")))["concepts"]


class ImageDedupe(Base):
    def resaved(self, src):
        from PIL import Image
        im = Image.open(src).convert("RGB")
        w, h = im.size
        p = os.path.join(self.tmp, "resaved.jpg")
        im.crop((20, 20, w - 20, h - 20)).resize((w // 2, h // 2)).save(p, "JPEG", quality=60)
        return p

    def test_cropped_jpeg_resave_still_matches(self):
        src = os.path.join(RENDERS, "MB01.png")
        self.assertLessEqual(mq.hash_distance(mq.image_hash(src), mq.image_hash(self.resaved(src))), mq.IMAGE_DUP)

    def test_distinct_memes_never_match(self):
        hs = {f: mq.image_hash(os.path.join(RENDERS, f)) for f in sorted(os.listdir(RENDERS)) if f.endswith(".png") and "-rough" not in f}
        names = list(hs)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                self.assertGreater(mq.hash_distance(hs[a], hs[b]), mq.IMAGE_DUP, (a, b))

    def test_import_images_skips_repeat_and_reports_bad_file(self):
        rows = [{"id": "MB01", "status": "approved", "phash": mq.image_hash(os.path.join(RENDERS, "MB01.png"))}]
        folder = os.path.join(self.tmp, "shots")
        os.makedirs(folder)
        os.rename(self.resaved(os.path.join(RENDERS, "MB01.png")), os.path.join(folder, "a.jpg"))
        open(os.path.join(folder, "b.png"), "wb").write(open(os.path.join(RENDERS, "MP02.png"), "rb").read())
        open(os.path.join(folder, "c.png"), "w").write("not a picture")
        added, skipped = mq.import_images(folder, rows)
        self.assertEqual(added, 1)
        self.assertIn(("a.jpg", "same as MB01 (distance 0)"), [(n, w) for n, w in skipped])
        self.assertTrue(any(n == "c.png" and w.startswith("unreadable") for n, w in skipped))
        self.assertEqual(rows[-1]["kind"], "candidate")
        self.assertEqual(rows[-1].get("reuse_status", ""), "")   # reuse still has to be set by a person

    def test_same_picture_cannot_be_approved_twice(self):
        h = mq.image_hash(os.path.join(RENDERS, "MM02.png"))
        rows = [{"id": "MM02", "kind": "original", "status": "approved", "reuse_status": "original", "phash": h},
                {"id": "MM99", "kind": "original", "status": "drafted", "reuse_status": "original", "phash": h}]
        done, blocked = mq.decide(rows, "approve", {"MM99"})
        self.assertEqual(done, [])
        self.assertIn("looks the same as MM02", blocked["MM99"][0])
        rows[0]["status"] = "rejected"   # a rejected twin doesn't block
        done, _ = mq.decide(rows, "approve", {"MM99"})
        self.assertEqual(done, ["MM99"])


class Rough(Base):
    def test_path_parser_handles_rough_commands(self):
        lines = mq._path_points("M0 0 L10 0 C10 5, 20 5, 20 0 M5 5 L6 6", steps=4)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0][:2], [(0.0, 0.0), (10.0, 0.0)])
        self.assertEqual(lines[0][-1], (20.0, 0.0))

    def test_clean_renders_unchanged(self):
        from PIL import Image, ImageChops
        for c in CONCEPTS:
            if c["id"] in ("MM02", "MM08", "MP02", "MM06"):
                new = Image.open(mq.render(c, self.tmp)).convert("RGB")
                old = Image.open(os.path.join(RENDERS, c["id"] + ".png")).convert("RGB")
                self.assertIsNone(ImageChops.difference(new, old).getbbox(), c["id"])

    @unittest.skipUnless(shutil.which("node"), "Node.js not installed")
    def test_rough_is_hand_drawn_and_repeatable(self):
        c = next(x for x in CONCEPTS if x["id"] == "MP02")
        a = mq.render(c, os.path.join(self.tmp, "a"), style="rough")
        b = mq.render(c, os.path.join(self.tmp, "b"), style="rough")
        self.assertTrue(a.endswith("MP02-rough.png"))
        self.assertEqual(open(a, "rb").read(), open(b, "rb").read())
        clean = mq.image_hash(os.path.join(RENDERS, "MP02.png"))
        self.assertGreater(mq.hash_distance(mq.image_hash(a), clean), 0)


if __name__ == "__main__":
    unittest.main()
