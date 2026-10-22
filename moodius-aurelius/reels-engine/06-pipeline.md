# 6. Production pipeline: batch reels with minimal AI, cost and manual work

**Cost:** €0 on top of what's already paid (Metricool Starter + Claude). Python, Pillow, NumPy and FFmpeg only. One render takes ~20s; a week of 7 reels takes under 3 minutes.

## The weekly loop
| Step | What happens | Who | AI used |
|---|---|---|---|
| 1 Pull results | Metricool reel metrics for last week appended to `reels-log.csv` | Claude (Friday routine, Metricool connector) | none (API call) |
| 2 Decide | `07-testing.md` rules applied to the log: test status, format weights | Claude | small: reads only new rows |
| 3 Write | 7 scripts written into `scripts/batch-NN.json` from unused library rows and pillar ideas, using `prompts/weekly-batch.md` | Claude | **one** writing pass per week |
| 4 Gate | `python3 tools/engine.py check scripts/batch-NN.json` | Claude | none (code) |
| 5 Render | `python3 tools/engine.py render scripts/batch-NN.json` (unchanged scripts are skipped by the cache) | Claude | none |
| 6 Sheet | `python3 tools/export_md.py …` makes the readable script sheet | Claude | none |
| 7 Schedule | MP4 + caption + first comment handed to the account thread, which schedules in Metricool (Instagram) | Claude | none |
| 8 Spot-check | Watch 2 of the 7 on your phone; reply to comments | **the owner** | none |

## Why it's cheap on tokens
- **Facts live in files, not in prompts.** The library (`03-research-library.csv`) holds every insight with its source and a `used_in` column, so a session reads 50 short rows, not books.
- **The citation registry is computed, not remembered.** `engine.py registry` scans every manifest and calendar in the project for book + section, so Claude never has to re-read old weeks to avoid repeats.
- **Only new things are processed.** The render cache (`renders/.cache.json`) skips any script that hasn't changed; the log only adds new rows.
- **Media is never opened by Claude** except one contact-sheet frame per batch for a visual check.
- **One reusable prompt** (`prompts/weekly-batch.md`) carries the voice, rules and schema so nothing is re-explained.

## Quality gate (automatic, blocks the render)
`engine.py check` fails a script if any of these is true:
1. First card isn't the hook, or the hook is over 12 words.
2. A card is too fast to read (~270 words a minute, plus 0.4s).
3. A quote card has no cite card after it, or the translation isn't on the public-domain list.
4. The book + section was already used anywhere in the project, or twice in the batch.
5. A modern-book idea has no "Idea: … · Moodius words" label.
6. Caption over 2,200 characters, more than 5 hashtags, or no first comment.
7. Banned words: alpha, high value, grindset, sigma, level up, unlock, journey, game-changer, hustle, king, "studies show", "science proves", cure, guaranteed, and similar.
8. (1.3) A quote card's words aren't in the public-domain text (Standard Ebooks: Long's Meditations, Discourses, Enchiridion; Stewart's Seneca Dialogues). Punctuation may differ, words may not.
9. (1.3, beat scripts only) A quiz card that isn't a question, isn't 2-3.5 s, or isn't answered by the next card; a reveal with fewer than 2 or more than 4 steps; a Script Doctor score under 70.
Warnings (don't block): length outside 7–20s, hook card over 2.6s, caption without a question, a quote that couldn't be machine-checked, a line under Instagram's buttons or caption, and for beat scripts no pattern change at 5-10 s, a payoff that doesn't reuse a hook word, no Script Doctor score yet.

## Beat grammar (engine 1.3, 22 Oct 2026)
Opt in with `"grammar": "beat"` on the batch (or one script). Scripts without it render exactly as in 1.2 (checked frame by frame on R001).
- **Frame 0:** the hook and its Ember rule are fully on screen at 0.0 s; no fade from a blank Slate. The cover JPG is frame 0.
- **Quiz** (`"quiz"`): a question held 2-3.5 s with an Ember timer draining right to left. It is the hook-system midpoint break.
- **Reveal** (`"reveal"`): 2-4 lines joined by `\n`; each appears in turn and stays.
- **Loop:** after the last card the hook fades back in over 0.6 s, so the last frame equals frame 0 and a replay reads as one sentence. Still photos drift there and back for the same reason.
- **QA sheet:** every render writes `-qa.png` (frame 0, each card, last frame at 1/3 size with Instagram's caption and button zones shaded) and `-qa.json` (text on frame 0; loop difference).
- **Script Doctor:** `engine.py doctor` + `prompts/script-doctor.md`, a scored second pass before QC.
Credits: beat grammar adapted from Hasan Aboul Hasan's claude-faceless-shorts-creator (MIT); Script Doctor from Purffle Studios' purffle-shorts (MIT). Demo: `renders/beat-demo/` (R001 before/after).

## Creative check (Claude, before the gate; rewrite on any "no")
1. Would a thoughtful 28-year-old actually say this out loud?
2. Would someone send it because it names something they feel?
3. Is there one concrete detail (a place, an object, a sentence people say)?
4. Is it smart without showing off?
5. Is the feeling earned by the detail, not by big words?
6. Could this appear on any other Stoic page? If yes, rewrite.

Rejected and rewritten in batch-01, for reference:
| First draft | Problem | Shipped |
|---|---|---|
| "Grief is love with nowhere to go." | someone else's line (Jamie Anderson), and widely used | "Nobody tells you grief comes back in the supermarket." |
| "Your brain isn't broken. It has 34 tabs open." | vague; and the source it needed is planned in the strategy calendar | Pascal "five minutes, no phone" (R007) |
| "Looking foolish is the entry fee. Pay it." | stock phrase | "Being laughed at for a year is cheaper than staying the same for ten." |
| "Most people last about 40 seconds." | made-up number | "Notice how fast your hand goes to your pocket." |
| "Seneca found the cure…" | banned word, over-claims | "Seneca found the answer…" |

## Footage (optional V2 look)
Drop original clips in `footage/` named by tag (`phone-table-1.mp4`, `aisle-1.mp4` …). The engine picks them up automatically, tints them 72% Slate and desaturates them; with no clip it renders flat Slate. Spec in `footage/README.md`.

## Commands
```
cd /mnt/project-files/moodius-aurelius/reels-engine
python3 tools/engine.py check  scripts/batch-01.json
python3 tools/engine.py render scripts/batch-01.json --only R001,R002
python3 tools/engine.py render scripts/batch-01.json --variant b      # hook B for test T1
python3 tools/engine.py render scripts/batch-01.json --layout centre  # text placement test T4
python3 tools/engine.py registry                                       # every citation already used
python3 tools/export_md.py scripts/batch-01.json 05-scripts-batch-01.md
```

## Can do now vs needs something extra
| Task | Status |
|---|---|
| Research from public pages, write, gate, render, schedule on Instagram via Metricool | **Can do now** (connected tools) |
| Read competitors' per-reel numbers | **Needs the owner:** add 5 competitors in Metricool (Analytics > Instagram > Competitors), 2 min |
| Post to TikTok and YouTube Shorts automatically | **Outside Phase 1** until the 19 Nov review; then the owner connects them in Metricool (Settings > Connections) |
| Retention curve and skip rate per reel | **Partly blocked:** Metricool gives 3s views and watch time; the full curve is only in the Instagram app (the owner reads it weekly, 2 min) |
| Footage look (V2) | **Needs the owner:** 8 phone clips, about 20 min once (spec in `footage/README.md`) |
| Licensed stock footage | **Needs the owner** to download from Pexels/Pixabay (free licence); this machine can't reach those sites |
| Voice-over / narrated reels | **Needs software or the owner's voice:** ElevenLabs (paid) or phone recordings. Not used in this plan |
| Comment replies, highlights, stickers | **the owner by hand** (APIs can't do these) |
