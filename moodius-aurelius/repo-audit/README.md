# Repo audit

A weekly check that keeps this repo tidy without ever deleting anything on its own.

**Weekly (Mondays 06:00 UTC, free on GitHub Actions):** `.github/workflows/moodius-repo-audit.yml` runs
`audit.py scan` on `main` and opens an issue labelled `repo-audit`. The issue is a checklist in seven parts:

1. **Already published**: upload packs, week folders and reels-engine renders whose posting slot ended more
   than 7 days ago (from the tracker, `published-ledger.csv` and `rules.json` → `retired_folders`).
   Offered for the archive. Metricool keeps its own copy, so the live post is not affected.
2. **Duplicate files**: byte-identical copies. The copy that docs or scripts mention is kept; copies inside
   upload packs and fix folders are left alone (they go when their pack is archived).
3. **Files nothing mentions**: images, video, audio and PDFs whose name (or content ID such as R004 or AD05)
   appears in no doc, script, tracker or ledger.
4. **Large files** (report only): everything over 5 MB and size by folder.
5. **Branches merged into main**: offered for deletion. Branches with an open PR, or that any file links to by
   URL (Metricool media served from `raw.githubusercontent.com`), or that are listed in `rules.json` →
   `keep_branches` (branches the account routines still serve media from or commit to), are always kept.
6. **Possible secrets** (report only, values never printed). Revoke at the provider first.
7. **Files naming the owner personally**: offered for a scrub (personal terms become "the owner", private
   emails become "[email removed]"). The names are read from the `AUDIT_PERSONAL_TERMS` repository secret,
   never written in this public repo, and never printed in the report.

**When you want changes:** tick lines in the issue, then comment `/apply` (only the repo owner can). The apply
workflow re-checks each ticked line, makes the file changes on a new branch and opens a pull request for you to
merge. Ticked merged branches are deleted straight away and the issue comment gives the command to restore each one.
Archived files keep their sub-path under `moodius-aurelius/_archive/` and are logged in `_archive/MOVED.csv`.
Ticks left on an unapplied issue carry over to next week's issue.

**Never touched:** the tracker, `experiments.csv`, reel script batches, grid ledgers, `.github/`, this folder
and the archive itself (`rules.json` → `never_touch`).

## One-time setup (owner)

1. Settings > Secrets and variables > Actions > New repository secret: name `AUDIT_PERSONAL_TERMS`, value the
   names to flag, separated by commas (full name, first name, surname, old handles). Optional but recommended.
2. Settings > Actions > General > Workflow permissions: tick "Allow GitHub Actions to create and approve pull
   requests", so `/apply` can open its pull request. Without it the branch is still pushed and the issue comment
   links to it.
3. Actions tab > "Moodius repo audit" > Run workflow, to get the first issue now instead of on Monday.

## For Claude threads and the account thread

- When a post goes live, append `path,published_at,metricool_id,note` to `published-ledger.csv` (repo path of
  the render or pack, ISO date). The audit offers it for the archive 7 days later.
- Only renders whose Metricool post is PUBLISHED may go in the ledger; anything PENDING stays where it is.
- When a branch stops serving media (its posts are all published), remove it from `keep_branches`.
- When a week folder or pack is finished, add it to `retired_folders` in `rules.json`.
- Run locally: `python3 moodius-aurelius/repo-audit/audit.py scan` (report to stdout), and
  `python3 moodius-aurelius/repo-audit/audit.py apply --body issue.md --dry-run`.
- Tests: `python3 -m unittest discover -s moodius-aurelius/repo-audit/tests` (also run before every weekly scan).
