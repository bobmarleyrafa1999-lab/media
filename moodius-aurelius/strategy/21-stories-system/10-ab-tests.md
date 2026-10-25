# A/B testing plan for Stories

Starts 8 Nov with the calendar. Numbered after the growth-system experiments (X7-X10), so these are X11-X15. Status: proposed.

## Honest limits first

Stories are seen mostly by followers (59 today). If 30-60 people see a story, one extra reply moves the reply rate by 2-3 points. So:
- run **one test at a time**, alternate arms by night, never two changes in the same story;
- decide only on a **big, consistent** gap: the rule below, set before we see results;
- treat every call as "keep for now", re-checked when the audience doubles.

Primary score for stories: **replies (or sticker taps) per 100 reached on the first frame.** Secondary: completion (last-frame reach ÷ first-frame reach) and exit rate. Growth score, logged but not tested on: follows per 1,000 reached.

## The tests, in order

| # | Question | Arm A | Arm B | Where | Min. nights per arm | Call rule |
|---|---|---|---|---|---|---|
| X11 | Is the hand-posted sticker worth the minute? | `_auto` only (reply prompt) | `_auto` + `_hand` with real sticker 5 min later | Hand-sticker nights in the calendar vs the rest, 8-21 Nov | 6 | B wins if its (sticker taps + replies) per 100 reached is ≥1.5× A on at least 4 of 6 pairs. If not, drop hand-posting and save the minute. |
| X12 | Opening frame: question or fact first? | Hook frame ends in a question ("How many noticed?") | Hook frame states a surprising fact, question on frame 2 | Evening sets, 22 Nov-5 Dec | 6 | Winner = higher frame-2 reach ÷ frame-1 reach (completion of the first tap). Needs ≥10 points gap on 4 of 6 pairs. |
| X13 | Posting window | Evening set at 21:00 | Evening set at 13:00 (lunch) | Weekdays, after X12 | 5 | Winner = replies per 100 reached ≥1.3× on 4 of 5 pairs. Morning payoff stays at 09:00 either way. |
| X14 | Call to action | "Reply with one word" | "Send this to the friend who…" | Morning Moodius-take frames | 8 | Two scores: replies vs shares. Keep both if each wins its own metric (likely); pick the one that matches the night's job. |
| X15 | Moodius answers first? | Question only | Moodius's own one-line answer shown on the same frame | Monday "about you" nights | 4 | Winner = replies per 100 reached ≥1.3× on 3 of 4 pairs. |
| X16 | Sequence length | 3 frames | 5 frames | Any sequence night, after X13 | 6 | Pick 5 only if completion stays ≥70% and total replies rise. |

## What the tracker needs, per story

reach · taps forward · taps back · exits · next story · replies (count in DMs) · sticker taps · shares · profile visits · follows. Fill from the app on Sunday. See the "How to fill" sheet in 09-tracker.xlsx.

## What I'll do with it

At the 19 Nov review I read the tracker, call X11, and change the calendar and the Friday routine to match. Results go into strategy/experiments.csv like the feed tests.
