# 1. Editorial strategy: Moodius Aurelius on Substack

*21 October 2026. Builds on the Phase 1 standing direction (`strategy/`) and engine v2 (`engine-v2/`). Replaces neither.*

## The one-line idea
**Moodius Aurelius is a research-led journal about the inner life of ambitious people: what we feel, why, and what the best evidence and the oldest philosophy say we can do about it.**

Instagram already runs on "Stoicism for people who feel things". The Substack is where that line gets room to breathe. Instagram is the shop window and Substack is the reading room.

## Who it is for
Intelligent, emotionally curious readers aged roughly 24–45, many of them professionals, founders and high achievers, more men than women but written so that nobody feels outside the room. They:
- read books and long articles, but are tired of self-help that sounds like a sales page;
- succeed on paper and feel a quiet gap they can't name (status without satisfaction, people around them without closeness, discipline without peace);
- distrust both "toxic positivity" and online toughness culture;
- want something they can **use** on a Tuesday evening, not only admire.

## What makes it different (the five promises)
Each promise is checked against what the 30 publications in `02-market-research.md` do.

1. **Every claim is labelled.** Each essay marks what is *peer-reviewed evidence*, what is *philosophy or interpretation*, and what is *Moodius opinion*. Almost no publication in the niche does this consistently (see research §4). It's the brand's moat and costs nothing.
2. **Evidence and philosophy in one essay, honestly separated.** Psychology newsletters rarely quote Seneca; Stoic newsletters rarely cite a meta-analysis. Moodius does both, and says which is which.
3. **Men's emotional lives without the grievance or the sermon.** The gap between toughness influencers and campaign-style charity content is large. Moodius writes to men as peers, with citations, and never at anyone else's expense.
4. **Something to do.** Every essay ends with a reflection exercise and three journaling questions. Journaling is the thread that ties all ten pillars together.
5. **Anonymous and calm.** No face, no personal myth, no invented anecdotes. The writing and the design system *are* the persona.

## Voice
A perceptive friend who reads too much: specific, slightly dry, warm without being soft. It names a situation before naming an idea. Sure about what it has evidence for, open about what is opinion.

**Never:** "In today's fast-paced world", "unlock", "level up", "game-changer", "journey" (as metaphor), "delve", "tapestry", "it's not X, it's Y" more than once per essay, rhetorical triple questions, invented "a client once told me" stories, alpha/sigma/high-value vocabulary, diagnosing readers. The QC script (`scripts/qc.py`) checks for these.

## The ten pillars and their weight
Weights decide how often a pillar comes round in the 90-day calendar. They come from audience relevance in the research and from what Instagram already shows works for us (blunt one-line hooks, emotional regulation, self-trust).

| # | Pillar | Weight | Flagship series |
|---|---|---|---|
| 1 | Journaling and reflective self-inquiry | ★★★ | *The Evening Review* (every essay's exercise feeds it) |
| 2 | Jung, the shadow, unconscious patterns | ★★ | *What We Disown* |
| 3 | Modern masculinity, male emotional development | ★★★ | *Masculinity, Reconsidered* |
| 4 | Stoicism, existentialism, practical philosophy | ★★★ | *Old Answers* |
| 5 | Attachment, relationships, loneliness | ★★★ | *The Distance Between Us* |
| 6 | Identity, ambition, discipline, burnout | ★★ | *After the Goal* |
| 7 | Attention, technology, the overstimulated mind | ★★ | *The Loud Room* |
| 8 | Grief, mortality, meaning, impermanence | ★ | *Memento* (handled carefully, see safety) |
| 9 | Self-worth, shame, approval, regulation | ★★★ | *What We Disown* / *Old Answers* |
| 10 | Money, status, success, fulfilment | ★★ | *After the Goal* |

## Formats on Substack
| Format | Length | Cadence | Purpose |
|---|---|---|---|
| **The Essay** | 1,200–1,800 words | weekly, Thursday 07:30 Madrid | Flagship. Research + philosophy + exercise. Free. |
| **The Evening Review** | 300–500 words | from week 5, every other Sunday | One question, one practice, one line from the archive. Builds the habit of opening. |
| **Notes** | 1–3 short paragraphs | 1 a day on weekdays | Discovery. Excerpts, single findings, questions. |
| **Field Notes** (later, paid) | 800–1,200 words | from month 4 if thresholds met | Deeper reading lists, guided 7-day journaling programmes, essay companions. |

**Paid tier:** not in the first 90 days. Substack's own guidance and every creator in the research build free trust first. The gate to switch on paid is in §Metrics below (decision at day 90, Surafel's call).

## How one essay becomes a week of content
```
Essay (Thu)  ─┬─ 3 Substack Notes (Thu, Fri, Mon)
              ├─ 7-slide carousel (Instagram, the following Mon 12:00 slot)
              ├─ 2 text-led reels (Tue + Fri 18:00 slots, engine formats A–F)
              ├─ 5 quote/insight cards (stories, Threads, Pinterest)
              ├─ 3 Story concepts (poll, question box, link to essay)
              └─ 5 Pinterest pins (link to the essay, not to IG)
```
Every piece carries the same palette, type and evidence label, and every off-Substack piece points to the essay.

## Funnel and the Instagram link
- Instagram bio link moves from the Kit guide page to the **Substack subscribe page** once the first essay is live. The free guide (`lead-magnet/7-stoic-tools-for-loud-emotions.pdf`) becomes Substack's welcome-email gift.
- **Recommendation:** after launch, import the Kit list into Substack (Settings → Import subscribers, CSV) and keep one list. Running both costs attention and splits the numbers. *This is Surafel's decision; nothing moves until he says so.*
- Reel and carousel captions end with one line: "The full essay is on the Substack (link in bio)."

## Safety and editorial standards
- **Evidence labels** on every claim: `[Study]`, `[Review]`, `[Philosophy]`, `[Moodius]`. Tiers match `engine-v2/01-brand-identity.md`.
- **Quotes** only from public-domain translations with book and section (Long for Marcus/Epictetus, Gummere for Seneca's letters, Stewart for *On Anger*, Ross for Aristotle). Modern authors in copyright are paraphrased with attribution ("Idea: bell hooks, *The Will to Change*, 2004").
- **Jung and the shadow** are presented as an interpretive framework from analytical psychology, not as a validated treatment. Where related lab findings exist (defensive projection, thought suppression), they're cited separately and their limits stated.
- **No invented anecdotes.** Examples are explicitly hypothetical ("Picture a manager who…") or composites drawn from public research, and labelled.
- **Mental-health line:** essays on grief, shame and loneliness end with a short signpost to professional help. No diagnosis, no treatment claims.
- **Anonymity:** publication and byline are "Moodius". No real name, face, voice or location.

## Metrics that decide things (and the ones that don't)
| Decides | Source | Why |
|---|---|---|
| Free subscribers gained per essay | Substack dashboard | The core outcome |
| Open rate and **read-through** (time on post / % reaching end where shown) | Substack post stats | Quality of the essay itself |
| Subscribers per 1,000 post views | Substack | Whether the essay converts strangers |
| Restacks + shares + comments per 1,000 views | Substack | Whether it travels |
| IG → Substack: link clicks (bio + story link) and subscribers with source "instagram" | IG insights + Substack subscriber source | Whether distribution works |
| IG saves and sends per reach | Metricool | Same as Phase 1 |
| **Returning readers by topic**: share of subscribers who opened ≥3 of the last 4 essays, split by the pillar that brought them | Substack subscriber CSV export, joined in `data/metrics.csv` | Which pillars build loyalty, not just spikes |

**Ignored for decisions:** follower count, likes, impressions on their own.

**Rules:** one experiment at a time (headline A/B test via Substack's title test when available, otherwise alternate weeks), at least 6 essays per variant before calling it, and a written review at day 30, 60 and 90.

**Paid-tier gate (day 90, Surafel decides):** ≥1,000 free subscribers *and* average open rate ≥45% *and* at least 3 essays with ≥5% of views converting. If missed, stay free for another 90 days.

## Claude does / You do
**Claude, automatically:** keeps the editorial database and source library, finds and checks research, drafts essays and every repurposing piece, runs the QC script, exports Substack-ready HTML, puts everything in an approval queue, and writes the weekly metrics note.

**You, by hand:** approve each essay (or send edits), paste it into Substack and press publish, publish Notes, decide the Kit→Substack move and the paid-tier gate. Nothing goes out without your yes.
