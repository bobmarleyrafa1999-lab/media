"""End-to-end tests for audit.py on a throwaway git repo. Run: python3 -m unittest discover -s moodius-aurelius/repo-audit/tests"""
import datetime as dt, json, os, re, shutil, subprocess, sys, tempfile, unittest

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def write(root, path, data):
    full = os.path.join(root, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb" if isinstance(data, bytes) else "w") as f:
        f.write(data)


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        tool = os.path.join(self.repo, "moodius-aurelius/repo-audit")
        os.makedirs(tool)
        for f in ("audit.py", "rules.json", "published-ledger.csv"):
            shutil.copy(os.path.join(SRC, f), tool)
        rules = json.load(open(os.path.join(tool, "rules.json")))
        rules["retired_folders"] = [{"path": "moodius-aurelius/week1", "last_day": "2026-01-01", "note": "week 1"}]
        json.dump(rules, open(os.path.join(tool, "rules.json"), "w"))
        old = (dt.date.today() - dt.timedelta(days=30)).isoformat()
        soon = (dt.date.today() + dt.timedelta(days=3)).isoformat()
        blob = os.urandom(4096)
        write(self.repo, "moodius-aurelius/week1/reels/reel-1.mp4", os.urandom(2048))
        write(self.repo, f"moodius-aurelius/strategy/upload-pack/{old}/cover.jpg", os.urandom(2048))
        write(self.repo, f"moodius-aurelius/strategy/upload-pack/{soon}/cover.jpg", os.urandom(2048))
        write(self.repo, "moodius-aurelius/brand/a.png", blob)
        write(self.repo, "moodius-aurelius/brand/copy-of-a.png", blob)
        write(self.repo, "moodius-aurelius/brand/orphan-image.png", os.urandom(2048))
        write(self.repo, "moodius-aurelius/docs.md", "Logo is brand/a.png. Ask Jane Roe or jane.roe@gmail.com. Jane Roe's call.\n"
                                                    "See https://raw.githubusercontent.com/o/r/keep-me/x.jpg\n")
        write(self.repo, "moodius-aurelius/strategy/calendar-30-day-tracker.csv", "date,hook_or_prompt\n")
        write(self.repo, "moodius-aurelius/notes.md", "Roe was here. Roebuck stays.\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        # a bare "origin" so branch checks have remote refs
        self.origin = os.path.join(self.tmp, "origin.git")
        git(self.tmp, "init", "-q", "--bare", self.origin)
        git(self.repo, "remote", "add", "origin", self.origin)
        git(self.repo, "push", "-q", "origin", "main")
        for b in ("merged-one", "keep-me"):
            git(self.repo, "push", "-q", "origin", f"main:refs/heads/{b}")
        git(self.repo, "fetch", "-q", "origin")
        self.env = dict(os.environ, AUDIT_PERSONAL_TERMS="Jane Roe,Roe")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_audit(self, *args):
        return subprocess.run([sys.executable, "moodius-aurelius/repo-audit/audit.py", *args], cwd=self.repo,
                              env=self.env, check=True, capture_output=True, text=True).stdout

    def test_scan_then_apply(self):
        report = self.run_audit("scan")
        self.assertIn("`moodius-aurelius/week1`: week 1", report)
        self.assertRegex(report, r"upload-pack/\d{4}-\d\d-\d\d`: pack dated")
        self.assertEqual(report.count("upload-pack/"), 1, "future pack must not be offered")
        self.assertIn("`moodius-aurelius/brand/copy-of-a.png`: identical to `moodius-aurelius/brand/a.png`", report)
        self.assertIn("`moodius-aurelius/brand/orphan-image.png`: not mentioned", report)
        self.assertIn("`merged-one`: fully merged", report)
        self.assertIn("`keep-me`: 1 file(s) link to it by URL", report)
        self.assertIn("`moodius-aurelius/docs.md`: 1 line(s): 1", report)
        self.assertNotIn("Jane", report, "the report must never print the personal terms")
        self.assertNotIn("jane.roe", report)

        body = re.sub(r"- \[ \]", "- [x]", report)
        body = body.replace("- [x] `moodius-aurelius/brand/orphan-image.png`", "- [ ] `moodius-aurelius/brand/orphan-image.png`")
        open(os.path.join(self.tmp, "issue.md"), "w").write(body)
        out = self.run_audit("apply", "--body", os.path.join(self.tmp, "issue.md"),
                             "--branches-out", os.path.join(self.tmp, "b.txt"))
        status = git(self.repo, "status", "--short")
        self.assertIn("moodius-aurelius/_archive/week1/reels/reel-1.mp4", status)
        self.assertIn("D  moodius-aurelius/brand/copy-of-a.png", status)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "moodius-aurelius/brand/a.png")))
        self.assertTrue(os.path.exists(os.path.join(self.repo, "moodius-aurelius/brand/orphan-image.png")), "unticked stays")
        docs = open(os.path.join(self.repo, "moodius-aurelius/docs.md")).read()
        self.assertNotIn("Roe", docs)
        self.assertIn("Ask the owner or [email removed]. The owner's call.", docs)
        self.assertEqual(open(os.path.join(self.repo, "moodius-aurelius/notes.md")).read(), "The owner was here. Roebuck stays.\n")
        self.assertIn("all 2 files below", report)
        moved = open(os.path.join(self.repo, "moodius-aurelius/_archive/MOVED.csv")).read()
        self.assertIn("moodius-aurelius/week1,moodius-aurelius/_archive/week1", moved)
        self.assertEqual(open(os.path.join(self.tmp, "b.txt")).read().split(), ["merged-one"])
        self.assertIn("Applied", out)

    def test_apply_rechecks(self):
        def marker(action, path):
            import base64
            return f"- [x] `{path}`: x <!-- audit:{action}:{base64.urlsafe_b64encode(path.encode()).decode()} -->"
        body = "\n".join([marker("delete", "moodius-aurelius/brand/orphan-image.png"),       # no twin
                          marker("archive", "moodius-aurelius/strategy/calendar-30-day-tracker.csv"),  # protected
                          marker("archive", "../outside.txt"),
                          marker("archive", "moodius-aurelius/gone.png")])
        open(os.path.join(self.tmp, "issue.md"), "w").write(body)
        out = self.run_audit("apply", "--body", os.path.join(self.tmp, "issue.md"))
        self.assertIn("no identical copy left", out)
        self.assertIn("protected path", out)
        self.assertIn("`../outside.txt`: no longer in the repo", out)
        self.assertIn("no longer in the repo", out)
        self.assertEqual(git(self.repo, "status", "--short"), "")


if __name__ == "__main__":
    unittest.main()
