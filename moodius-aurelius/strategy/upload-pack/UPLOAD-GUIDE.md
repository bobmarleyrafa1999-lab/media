# Upload guide: 20 Oct to 1 Nov 2026 (free route, no Metricool payment)

## Where things stand
- Metricool's free plan is used up for October. Today's 12:00, 15:00 and 18:00 posts failed with "You have reached your Metricool account limit", and everything still queued there will fail the same way until you upgrade.
- So until you pay, **posting is by hand**, from the folders in this pack. Every post is finished: media, caption, hashtags, first comment, alt text and exact time.
- To stop a double post, I set the one Metricool item that could have gone out on 1 Nov (the 18:00 reel) to **draft**. Nothing else in Metricool will publish while you're on the free plan.
- **On the day you upgrade, tell me.** I'll swap the Metricool queue to these improved versions and you stop uploading by hand from the next slot.

## The pack
One folder per day: `strategy/upload-pack/2026-10-21/` and so on. File names start with the posting time:

| File | What |
|---|---|
| `0900-story-daily.jpg` | 09:00 story |
| `1200-carousel-01.jpg` … | 12:00 carousel, upload in number order |
| `1800-reel.mp4` + `1800-reel-cover.jpg` | 18:00 reel and its cover (Fridays: `1700-…`) |
| `2100-story-journal.jpg` | 21:00 Journal story |
| `caption.txt` | Everything to paste for that day, in order |

`2026-10-20/` holds the 4 Manifesto stories that failed tonight. Post them whenever you can, in order, and put them in the Manifesto highlight.

## Way 1 (recommended): schedule the whole week once in Meta Business Suite, about 40 min a week
Free, on a computer, and it publishes for you at the right time.
1. Open business.facebook.com and pick the Moodius page. Your Instagram is already linked to it (Metricool uses the same link).
2. **Carousel:** Planner (or Content) > Create post. Tick Instagram only (untick Facebook unless you want it there too). Add photos > select `1200-carousel-01` to the last one **in number order**. Paste the caption from `caption.txt`. Click the arrow next to Publish > Schedule > set the date and 12:00.
3. **Reel:** Create reel > upload `1800-reel.mp4`. Paste the caption. Under thumbnail/cover, upload `1800-reel-cover.jpg`. Keep "share to feed" on. Schedule for 18:00 (Fridays 17:00).
4. **Stories:** Create story > upload the jpg > Schedule for 09:00 or 21:00.
5. Times are your computer's clock. If you're in Madrid nothing to change. Clocks go back on Sun 25 Oct; the times in the pack are already Madrid local time.
6. **First comment:** if Business Suite shows a first-comment box, paste it there. If not, post it from the app as soon as the post is live (you're in the comments in that first hour anyway).

## Way 2: post from the Instagram app each day, about 10 min a day
Save the day's folder to your phone (Files / Google Drive). At each time: + > Post / Reel / Story, pick the files, paste the caption from `caption.txt`. For reels: Edit cover > Add from camera roll > the cover jpg. Alt text is under Advanced settings > Accessibility. On the 21:00 Journal story you can add a Question sticker in the empty space under the text (the only thing the app can do that scheduling can't).

## Way 3 (optional, free, more setup): direct Instagram API
A 20-minute one-off setup in Meta for Developers gives me a token to publish straight to Instagram with no Metricool. Say the word and I'll send the click-by-click steps. Not needed for these two weeks.

## What I did (Claude)
- Checked the Metricool queue and what would actually publish (nothing until you upgrade); set the 1 Nov reel to draft so it can't double-post.
- Wrote and rendered what wasn't built yet: 7 carousels for 26 Oct to 1 Nov and all 24 Daily and Journal stories for 21 Oct to 1 Nov, from the 30-day tracker.
- QC'd every slide, story and reel frame, and fixed what was off:
  - **Centring:** content now sits on one optical centre on every slide (before, covers and quotes sat high and steps sat low, so text jumped as you swiped).
  - **Line breaks:** no more one-word last lines on slides or reels.
  - **Stories:** text moved below Instagram's name bar (the wordmark sat under it) and kept above the reply bar.
  - **Reel citation cards:** the old renderer dropped the spaces ("MARCUSAURELIUS,MEDITATIONS7.7"); fixed and re-rendered.
  - **Quotes:** a few lines were in modern copyrighted translations; swapped to public-domain ones (Long, Basore, Jowett, Ludovici) and cited, per the Phase 1 rule.
  - **Voice:** removed leftover "brother", "good man", "a girl" lines from the 22-25 Oct reels.
  - **Hashtags:** every caption now has 5. Instagram caps posts at 5 hashtags since December 2025, so the old 7 to 8 would have been rejected or cut.
  - Typographic quotes and apostrophes throughout.
- Tools updated so future weeks come out the same: `tools/stills_v3.py`, `tools/reels_v2.py`, `reels-engine/tools/engine.py` (v1.1). Rebuild the pack with `strategy/upload-pack/_build/build.py`.

## What you do (by hand)
- Upload each day's posts (Way 1 or Way 2).
- Post the first comment right after each feed post goes live.
- Add each story to the highlight printed on it (Daily, Manifesto, Tools, Discipline, Truths, Identity, Journal).
- Reply to comments in the first hour and to Journal story replies in DMs (see `11-community.md`).
- When you're ready to pay: upgrade in Metricool > Settings > Plan, then tell me.

## Day by day
| Day | 09:00 story | 12:00 carousel | Reel | 21:00 Journal |
|---|---|---|---|---|
| Tue 20 Oct | 4 Manifesto stories (tonight or any time) | | | |
| Wed 21 | Daily · Epictetus | Self-trust (7) | 18:00 Regulating, not suppressing | What did you avoid today? |
| Thu 22 | Daily · Marcus 2.1 | Rude people (6) | 18:00 Asking for help | What feeling did you name? |
| Fri 23 | Daily · Seneca 13.4 | Replaying the argument (7) | **17:00** They got away with it | Who were you kind to? |
| Sat 24 | Daily · Seneca, On Anger | Evening review (10) | 18:00 Your family | What hurt today? |
| Sun 25 | Daily · Marcus 7.59 | 5 ancient lines (7) | 18:00 Look within | What was beautiful? |
| Mon 26 | Daily · Marcus 2.4 | You're not lazy (7) | 18:00 R001 Opinion of others | Where did you lose your temper? |
| Tue 27 | Manifesto · Marcus 7.8 | Rehearsing disasters (6) | 18:00 R003 Solitude vs loneliness | What are you pretending not to know? |
| Wed 28 | Daily · Marcus 4.24 | Do less, better (5) | 18:00 R002 Kafka | Who do you miss? |
| Thu 29 | Tools · Enchiridion 20 | One comment (5) | 18:00 R004 First year | What are you quietly proud of? |
| Fri 30 | Discipline · Aristotle | Who you let close (5) | **17:00** R006 Under the anger | What did fear decide? |
| Sat 31 | Truths · Enchiridion 46 | Show your philosophy (7) | 18:00 R005 Go first | What did your body need? |
| Sun 1 Nov | Identity · Plato | Two horses (10) | 18:00 R007 Five minutes | Who made you better? |
