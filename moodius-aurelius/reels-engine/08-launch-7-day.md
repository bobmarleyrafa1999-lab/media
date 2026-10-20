# 8. Seven-day reels launch: Mon 26 Oct – Sun 1 Nov 2026

Base cadence 7 reels a week, one a day at **18:00 Madrid (Fri 17:00)**, which is the reel slot in `strategy/calendar-30-day-tracker.csv` (days 6–12). The 12:00 carousel and the 09:00 / 21:00 stories stay exactly as the strategy calendar has them. The tracker's planned reel hooks for those days are still unmade, so they move back a week rather than being lost (confirming with the strategy thread). Clocks change on 25 Oct, so every time is +01:00.

Test T1 runs all week: A = situation hook, B = curiosity hook, alternating.

| Day | Reel (file in `renders/`) | Pillar · format | Arm | Source | CTA |
|---|---|---|---|---|---|
| Mon 26 | **R001** You'd never let a stranger decide what you're worth. | Daily Stoic · R2 | A | Meditations 12.4 | send |
| Tue 27 | **R003** Solitude: your phone is off. | Feel Logs · R1 | B | Gallup 2025 | save |
| Wed 28 | **R002** Kafka wrote the most accurate book about work. | Daily Stoic · R4 | A | Kafka (idea) | send |
| Thu 29 | **R004** The first year of getting better looks embarrassing. | Becoming · R2 | B | Enchiridion 13 | save |
| Fri 30 (17:00) | **R006** Angry men are usually something else first. | Feel Logs · R3 | A | bell hooks (idea) | save |
| Sat 31 | **R005** You want to be chosen. You don't choose anyone. | Feel Logs · R2 | B | Letters 9.6 | send |
| Sun 1 | **R007** Try sitting alone for five minutes. No phone. | Training Room · R2 | A | Pensées 139 | save |

Arm B days use `renders/<id>-b.mp4` (rendered with `--variant b`). R008–R010 are rendered and ready as substitutes or for an optional second daily reel at 15:00 if you move to 14 a week.

## Daily execution
| When | Claude (automatic) | Surafel (by hand) |
|---|---|---|
| Fri 23 Oct, routine | Render arm-B files, schedule the 7 reels in Metricool with caption + first comment, log rows in `reels-log.csv` | — |
| Every day 18:00 | Reel publishes; 20:40 publish check flags failures | Reply to comments for 10 min (playbook); add the day's stories to highlights |
| Every day, 1 min | — | Open the reel in the Instagram app after ~24h, note skip rate in the log if you can (optional) |
| Sun 1 Nov | — | Watch 2 reels on your phone; tell me anything that felt off |
| Mon 2 Nov | Pull 72h metrics, update T1 pairs, write batch-02 (7 scripts) from the pillar pool | — |

## Before launch (one-off, Surafel)
1. Connect TikTok and YouTube to the Metricool brand so the same reels cross-post (5 min).
2. Add 5 competitors in Metricool (2 min).
3. Optional: shoot the footage list in `footage/README.md` (20 min). Without it, every reel renders in flat Slate, which is the default look anyway.
