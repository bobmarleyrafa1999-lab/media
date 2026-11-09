import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mirror


class MirrorTest(unittest.TestCase):
    def test_selection(self):
        paths = ["moodius-aurelius/reels-engine/renders/R001-x.mp4", "moodius-aurelius/reels-engine/tools/engine.py",
                 "moodius-aurelius/week3/v2/story-1.jpg", "moodius-aurelius/hook-intel/data/raw/c/thumbs/a.jpg",
                 "moodius-aurelius/business/journal/out/personal/o/x.png", "moodius-aurelius/strategy/00-README.md",
                 "moodius-aurelius/strategy/upload-pack/_build/a.png", "moodius-aurelius/business/website/public/a.png"]
        self.assertEqual(list(mirror.selected(paths)),
                         ["moodius-aurelius/reels-engine/renders/R001-x.mp4", "moodius-aurelius/week3/v2/story-1.jpg"])

    def test_repoint(self):
        t = ("https://raw.githubusercontent.com/bobmarleyrafa1999-lab/media/claude/project-thread-bxasif/moodius-aurelius/week3/a.mp4 "
             "https://raw.githubusercontent.com/bobmarleyrafa1999-lab/media/main/moodius-aurelius/b.jpg "
             "https://raw.githubusercontent.com/GITenberg/x/master/1.txt")
        self.assertEqual(mirror.repoint(t),
                         "https://raw.githubusercontent.com/bobmarleyrafa1999-lab/moodius-media/main/moodius-aurelius/week3/a.mp4 "
                         "https://raw.githubusercontent.com/bobmarleyrafa1999-lab/moodius-media/main/moodius-aurelius/b.jpg "
                         "https://raw.githubusercontent.com/GITenberg/x/master/1.txt")


if __name__ == "__main__":
    unittest.main()
