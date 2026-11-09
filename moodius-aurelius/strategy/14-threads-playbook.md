# 14. Threads playbook: the Threads side of Moodius (21 Oct 2026)

Same principles as Instagram (Stoicism for people who feel things, cited sources, Moodius paraphrases labelled, no bait). Different engine: Threads is a conversation feed, so text and replies matter more than visuals.

## How Threads ranks (what's known, and how sure we are)
Meta doesn't publish the full ranking. What's reasonably established (Metricool's 2026 guide, other marketing guides, Meta's own product changes):
- **The For You feed predicts whether someone will like a post, open its replies, or follow the author.** Opening replies and following are the signals Instagram doesn't have, so posts that start conversations are favoured.
- **Followed accounts got more weight (Nov 2024 change), and engagement bait got less visibility.** "Comment YES if…" hurts us here too.
- **Topic tags** (one per post) file a post into a topic feed. There's no confirmation that they boost ranking, but they decide who can find the post.
- **Users steer their own feed** ("Dear Algo"), so being clearly about one subject helps people choose us.
- **Unconfirmed, used only as working rules:** that the first 30–60 minutes are a test window, and that replies outweigh likes (e.g. "10 replies beat 100 likes"). Our own data will confirm or kill these.

## What we post (Claude, via Metricool, once the Moodius Threads account is connected)
| Slot (Madrid) | Post | Source |
|---|---|---|
| 12:30 daily | **The carousel as text:** the claim, 3–5 short lines, the citation in plain words, the cover image attached. One topic tag (Stoicism, Psychology, Mental Health or Philosophy) | same day's Instagram carousel |
| 21:30 daily | **A Quiet Truth or a question** that's genuinely open (not "agree?"). Text only | research library + B/A formats |
| Twice a week | **A short thread (3–5 posts)**: one idea unfolded, e.g. the C format's two readings | C/D scripts |
| Never | Reposted reels with "link in bio", hashtag piles, engagement bait, anything from the old personal account | |

Instagram ↔ Threads, helping each other: every Threads post can link the matching reel or the free guide once a week (not every post). Instagram stories point to the best Threads conversation of the week ("this got 40 replies, read them").

## Analytics we track (all available from Metricool for Threads)
| Metric | Why it matters on Threads | Target to beat (set after 2 weeks of data) |
|---|---|---|
| **Replies per 1,000 views** | The conversation signal; our primary Threads KPI | baseline week 1 |
| **(Reposts + quotes + shares) per 1,000 views** | Distribution to non-followers | baseline |
| **Followers gained per post** (delta followers ÷ posts) | Whether posts convert | baseline |
| Profile views | Interest beyond the post | — |
| Likes | Reported, not optimised | — |

The Friday report gets a Threads section with these, and the best and worst post with the reason. Experiments follow the same rule as Instagram: one at a time, 2 variants, at least 10 posts each. First Threads test once there's a baseline: **text-only vs text + carousel cover image** (metric: replies per 1,000 views).

## You do (Surafel, by hand)
1. Profile setup for the account you choose on the decision card (name, bio, photo: same as Instagram).
2. **Reply to replies within the first hour** when you can, 10 minutes a day. On Threads this does more for reach than on Instagram.
3. Optional, 10 minutes a day: thoughtful replies on 5 posts from bigger accounts in philosophy and psychology. This is how small Threads accounts get discovered.
4. Add 3–5 Threads competitors in Metricool (Analytics › Threads › Competitors). Metricool supports Threads competitor tracking: followers, views, likes, replies, reposts, quotes.

## Claude does
Writes and schedules both daily posts and the weekly threads in Metricool (through the account thread's queue and the Friday routine), pulls Threads metrics weekly, runs the one active test, and drafts reply prompts for the posts that start conversations.
