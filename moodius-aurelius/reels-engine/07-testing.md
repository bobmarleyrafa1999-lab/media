# 7. Reel testing: what we test, how we read it, what we do next

Runs inside the strategy experiment queue (`strategy/experiments.csv`) and follows the approved Phase 1 rule: **one experiment at a time, 2 variants, at least 10 reels per variant.** At 7 reels a week a test takes about 3 weeks; at 14 a week, about 10 days.

## Metrics (pulled 72h after posting, logged in `reels-log.csv`)
| Metric | Formula | Primary for |
|---|---|---|
| 3s hold | 3-second views ÷ plays (Metricool) | hooks, opening frame |
| Skip rate | from the Instagram app (Surafel copies it weekly) | hooks |
| Watch % | avg watch time ÷ length | length, pacing |
| Completion | read off the retention curve in the app, if shown | length |
| Sends/reach | shares ÷ reach | R1, R4, overall |
| Saves/reach | saves ÷ reach | R2, R5 |
| Profile visits, follows | per 1,000 reach | growth |

## Test queue
| ID | Question | Arm A | Arm B | Primary metric | How it's produced |
|---|---|---|---|---|---|
| **T1** | Situation hook vs curiosity hook | `hook` (specific "you" moment) | `hook_b` (curiosity: "Marcus noticed a habit. You have it.") | 3s hold | `--variant b`, alternate days |
| T2 | Length | 15–20s | 30–40s (same idea + one more beat) | views at 72h, then watch % | separate script field `long_cards` (batch-02) |
| T3 | Philosophical vs conversational wording | quote-led R2 | same idea as R1, no quote | sends/reach | paired scripts |
| T4 | Text placement | upper third (default) | centre | 3s hold | `--layout centre` |
| T5 | Visual | V1 flat Slate | V2 footage | 3s hold, reach | needs footage |
| T6 | Emotional vs humorous | R1/R2 | R4 on the same theme | sends/reach | paired scripts |
| T7 | Music | ambient bed | score.py cue | watch % | `audio.engine` |

T1 starts in the launch week (it needs no new assets). T2 is next, because the 2026 Socialinsider data (30–60s reels got about twice the median views of sub-30s) is the biggest open question. It's brand data and correlational, so we test rather than switch.

## Reading results (no invented significance)
- Compare **pairs** (same weekday, same slot), never one reel against one reel.
- **Directional:** one arm wins 8 of 10 pairs. Lean that way, keep testing.
- **Winner:** 9 of 10 pairs (sign test p ≈ 0.02) *and* the gap holds in the second half. Adopt it as the default.
- **No call** otherwise. Log it as "no difference" and move on; that's a result too.
- Note anything that could explain a gap (a collab share, a holiday, a slot change). Correlation isn't cause.

## Retire / promote
- A format that's in the bottom third on its primary metric for **two 10-reel windows in a row** is retired for a month.
- A pillar whose reels win sends/reach for two windows gets one extra slot a week.
- Any reel at 2× the 4-week median on sends gets a sequel within 10 days (same structure, new source).

## Files
- `reels-log.csv`: one row per published reel (columns match `strategy/post-log.csv` plus `script_id`, `arm`, `skip_rate`, `completion_pct`).
- `reels-tests.csv`: one row per test with status and pair counts.
