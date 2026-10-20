# 8. Seven-day reels launch: Mon 26 Oct – Sun 1 Nov 2026

Base cadence 7 reels a week, one a day at **18:00 Madrid (Fri 17:00)**, which is the reel slot in `strategy/calendar-30-day-tracker.csv` (days 6–12). The 12:00 carousel and the 09:00 / 21:00 stories stay exactly as the strategy calendar has them. These are now in `strategy/calendar-30-day-tracker.csv` (days 6–12). Clocks change on 25 Oct, so every time is +01:00.

**Only the A files post this week.** Phase 1 runs one experiment at a time, and the carousel-cover test X1 runs 26 Oct to about 15 Nov. The hook test T1 is queued as **X5** in `strategy/experiments.csv`, next after X1; the B files are ready for it.

| Day | Reel (file in `renders/`) | Pillar · format | Source | CTA |
|---|---|---|---|---|
| Mon 26 | **R001** You'd never let a stranger decide what you're worth. | Daily · R2 | Meditations 12.4 | send |
| Tue 27 | **R003** Solitude: your phone is off. | Journal · R1 | Gallup 2025 | save |
| Wed 28 | **R002** Kafka wrote the most accurate book about work. | Daily · R4 | Kafka (idea) | send |
| Thu 29 | **R004** The first year of getting better looks embarrassing. | Identity · R2 | Enchiridion 13 | save |
| Fri 30 (17:00) | **R006** Angry men are usually something else first. | Journal · R3 | bell hooks (idea) | save |
| Sat 31 | **R005** You want to be chosen. You don't choose anyone. | Journal · R2 | Letters 9.6 | send |
| Sun 1 | **R007** Try sitting alone for five minutes. No phone. | Discipline · R2 | Pensées 139 | save |

R008–R010 are rendered and ready as substitutes if any of the seven fails a last check.

## Daily execution
| When | Claude (automatic) | Surafel (by hand) |
|---|---|---|
| By Fri 23 Oct | Account thread schedules the 7 A files in Metricool with caption + first comment (it owns scheduling); I log rows in `reels-log.csv` | — |
| Every day 18:00 | Reel publishes; 20:40 publish check flags failures | Reply to comments for 10 min (playbook); add the day's stories to highlights |
| Every day, 1 min | — | Open the reel in the Instagram app after ~24h, note skip rate in the log if you can (optional) |
| Sun 1 Nov | — | Watch 2 reels on your phone; tell me anything that felt off |
| Mon 2 Nov | Pull 72h metrics, write batch-02 (7 scripts) from the pillar pool | — |

## Before launch (one-off, Surafel)
1. Add 5 competitors in Metricool (2 min).
2. Optional: shoot the footage list in `footage/README.md` (20 min). Without it, every reel renders in flat Slate, which is the default look anyway.

TikTok/YouTube cross-posting and a second daily reel are outside the approved Phase 1 cadence, so they wait for the 19 Nov review.
