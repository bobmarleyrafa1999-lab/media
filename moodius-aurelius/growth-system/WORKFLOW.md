# Weekly workflow

This is the repeatable loop the scripts in `tools/` support. It reuses the
existing Friday routine and the Metricool queue. Steps marked **Surafel**
are the only ones that need him.

## Every day: comments (Stage 5)

1. The comment agent already emails new comments. The digest goes out at 20:30.
2. `comments.py` sorts them into `queue.csv`, highest priority first. For each
   comment it records the intent, the pillar and the question the commenter
   actually asked, plus the best-matching tidbit from the library. Every row
   starts as `awaiting_approval`. Nothing is ever posted.
3. **Surafel** reads the queue and approves, edits or skips each draft. Some
   rows never get a draft because they always need him personally:
   - crisis: reply the same day and point to UK Samaritans 116 123
   - sensitive comments
   - sponsorship and commercial questions
   - criticism: check the source first
4. Reading requests leave a gap for a book he has read himself. The checker
   never lets Claude recommend a book he hasn't read.
5. Questions asked twice or more go into `ideas.md`, and each one gets a brief
   skeleton in `idea-briefs/`. A skeleton fails the checker until a sourced
   tidbit is added. That's deliberate: comments suggest topics, but they are
   never a source.

## Friday: build the week (Stage 6)

1. Claude writes up to 20 briefs for the coming week. They draw on the
   library, the idea briefs and the series in progress.
2. `brief_lint.py` checks each one. Failures are fixed or dropped, never
   waved through.
3. `calendar_build.py --week-start <Monday>` fills the 14 feed slots against
   the pillar targets and the hurt/conflict cap. It writes `week-*.md` for the
   check and `handoff-*.json` for the account thread.
4. The account thread renders the posts with the reels engine and queues them
   in Metricool, the same way as now. **Surafel** only sees exceptions:
   empty slots, a pillar short of target, or a tidbit still marked `manual`
   that needs a hand-read.

## Friday: read last week (Stages 7 and 8)

1. Data comes in two ways:
   - Today: Surafel downloads Instagram's export by hand (Professional dashboard > Export).
   - Once he approves: a weekly job pulls the same numbers through the official API.
2. Run `analytics.py --experiments experiments-proposed.csv`. It produces the
   dashboard and `weekly.md`, which list:
   - follow-up candidates
   - posts that produced follows
   - underperformers
   - pillar balance
   - one readout line per experiment
3. Each experiment is called only by the rule written down in
   `experiments-proposed.csv` before it started: posts per arm, total events
   and minimum gap. Until all three are met, the readout says "keep running".
4. The next Friday's briefs follow from it: more of the follow-up
   candidates, fewer of the underperformers.

## What never happens without a yes from Surafel

- Publishing anywhere other than Instagram
- Sending a reply or a DM
- Any spend
- Connecting a new account or token
- Changing the five-pillar mix
- Making the repo private or public
