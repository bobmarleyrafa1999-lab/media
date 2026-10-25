# Viral Stories & engagement system (25 Oct 2026)

Overview page: https://claude.ai/artifact/WhpJ66aYTAKSnprGwpq8A5 (build/page.html + build/build_site.py make it).

Builds on the 22 quiz stories already scheduled 26 Oct-7 Nov (strategy/20-story-replies/). This system takes over from **Sun 8 Nov**.

## The one thing to know

Instagram lets no scheduler add a poll, quiz, slider, question or Add Yours sticker; that's Meta's API rule. So every interactive story comes in two versions: `_auto` asks for a typed reply and is scheduled automatically; `_hand` has space for the real sticker and takes about a minute to post from your phone. Hand-posting is optional; test X11 finds out whether it's worth the minute.

Second thing: Meta's API reports **0 story replies for accounts in Europe**, and Metricool's story analytics came back empty. Replies get counted in the app/DMs; the tracker is built for that.

## What's here

| # | File | What it is |
|---|---|---|
| 1 | 01-research.md | What's verified vs third-party vs assumption: platform rules, 7 behavioural studies, competitor reality check, data audit |
| 2 | 02-concepts.md / .csv | 50 story concepts (+3 recurring formats), each with hook, layout, sticker, reply version, discussion question, follow-up, CTA, source |
| 3 | 03-sequences.md + renders/ | The 15 strongest sequences, written frame by frame and rendered (92 images, `_auto` and `_hand`) |
| 4 | 04-conversation-system.md | The seven formats, how you add your own takes (5 min a week), 25 discussion starters, rules for sharing replies |
| 5 | 05-questions.md / .csv | 100 questions, 20 per pillar, with sticker type and depth |
| 6 | 06-response-bank.md | 60 replies for real follower messages, crisis lines (UK 116 123, Spain 024), bait and troll handling |
| 7 | 07-calendar.md / .csv | 30 days, 8 Nov-7 Dec: 15 sequences + 15 concept nights, Monday about-you, Friday you-pick, hand-sticker nights marked |
| 8 | 08-workflow.md | Weekly loop, tools and repositories audited (instagrapi and instaloader rejected: they need your password) |
| 9 | 09-tracker.xlsx / .csv | Per-story log, per-sequence summary (completion, replies per 100, follows per 1,000), weekly sheet, how-to-fill |
| 10 | 10-ab-tests.md | X11-X16: sticker vs reply, opening frame, time, CTA, answering first, length |
| 11 | 11-templates.md + templates/ | 12 templates in the brand palette and type |
| | build/ | Source: concepts.py, sequences.py, questions.py, templates.py (render), export.py (docs, tracker) |

## Rules respected

Anonymous (no faces, no personal details), no gendered framing (masculinity research reframed as emotional intelligence for everyone), every fact with its source on the card and caveats where studies are small or correlational, quotes as labelled paraphrases, no invented follower messages (frames needing real answers are marked [by hand]), no bots, £0.

"Moodius take" frames are drafts in the page's voice. Change anything that isn't your view.

## Yes/no for you

1. Use this calendar for stories from 8 Nov (the Friday routine builds and schedules the `_auto` versions)?
2. Free GitHub Actions job to save story insights automatically before they expire (needs the page token the comment agent is waiting for)?
EOF