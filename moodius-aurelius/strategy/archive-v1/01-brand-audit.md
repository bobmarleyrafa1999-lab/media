# 1. Brand audit: @moodiusaurelius (20 Oct 2026)

Evidence tags: **[D]** our own Metricool data · **[V]** verified public source · **[A]** assumption or judgement.

## Where the account actually is
| Item | Status | Tag |
|---|---|---|
| Followers | 3 → 4 (12–16 Oct) | D |
| Reels at 12:00 / 18:00 | 115–143 views each | D |
| Reels at 10:00 | 12–26 views (slot dropped) | D |
| Best 3-second hold | Confrontational/relational hooks: 44–48% | D |
| Worst 3-second hold | Numbered-list reels: 25–28% | D |
| Image posts | meme 11 views, quote cards 1–7 | D |
| Output | 3 feed posts + 2 stories a day, fully automated | D |
| Publishing | Metricool Starter (upgraded 20 Oct). Week 3 scheduled 19–25 Oct | D |
| Lead magnet | PDF built, **not hosted**, so no email capture yet | D |
| Competitors in Metricool | **Not added**, so no live competitor data | D |

Read: the content engine works; distribution has barely started. Four followers means every result so far is a small sample. Treat the numbers as direction, not proof.

## Scorecard
| Dimension | Score /5 | Why | Fix |
|---|---|---|---|
| Name and concept | 4 | "Moodius" (moody + Marcus) is memorable and fits emotional-regulation content. | Lean into it: "Feel Logs" and "Quiet Truths" are natural series names. |
| Mission clarity | 4 | Since 13 Oct: young men, purpose, suffering, amor fati, virtue, beauty. | Keep. Add the master prompt's psychology and relationships pillars beneath it (table below). |
| Voice / "who" | 3 | First-person "Moodius" older-brother captions exist, but reels are anonymous text. | One recurring sign-off and a fixed caption shape (see templates). Voice recordings are still the biggest upgrade. |
| Visual identity | 3 | Dark stone, cream serif, gold "M · A" monogram is consistent but looks like every quote page (FreeSerif, marble). | Swap to a distinctive free font pair (Cormorant Garamond + Inter) and add one ownable device: the gold rule plus a pillar label on every asset. |
| Format range | 2 | Almost all text reels. No working carousel or story system yet. | Use the 10-format library: reels stay the majority, plus 3 carousels a week. |
| Accuracy | 4 | Book/chapter cited on screen. One weak claim: the Week 1 "Evening review" reel says "Marcus Aurelius did this every night". The documented nightly review is Seneca's (On Anger 3.36), so future versions credit Seneca. | Rule: every quote carries book + section, and translations are public-domain (Long, Gummere, Higginson, Ross) or labelled paraphrase. |
| Funnel | 1 | Bio promises a free guide that isn't hosted. | Host the PDF (Kit free plan or Stan Store), put the link in bio. This is the top non-content action. |
| Community | 2 | First-comment questions exist, but nobody replies to comments yet. | 10 min a day with the playbook. |
| Bio | 3 | "3 posts a day" is a promise about us, not the reader. | New bio below. |

## Conflict 1: highlights (needs your call)
Live on the page since 13 Oct: **Start · Purpose · Suffering · Amor fati · Virtue · Beauty** (covers in `week2/stills/cover-*.jpg`, 25 stories already labelled with these).
The master prompt lists: **Moodius Manifesto · Quiet Truths · Training Room · Becoming · Utilities · Feel Logs · Daily Stoic.**

The master prompt's names mix themes (Becoming, Training Room) with formats (Daily Stoic, Quiet Truths). The live set is themes only, and has no home for tools or journaling, which are the two most saveable things we make.

**Recommendation: a hybrid seven.**
| Highlight | Replaces / merges | Holds | Cover |
|---|---|---|---|
| Manifesto | Start + Moodius Manifesto | Who this is for, the 7 principles, free guide link | compass (new) |
| Purpose | Purpose + Becoming | Identity, ambition, transformation | Τ (existing) |
| Suffering | Suffering | Meaning in hardship | Π (existing) |
| Amor fati | Amor fati + Beauty | Loving fate, seeing the beauty in life | ∞ (existing) |
| Virtue | Virtue + Training Room | Discipline, habits, character | Α (existing) |
| Utilities | new | Frameworks, exercises, carousels re-shared | wrench/grid (new) |
| Feel Logs | new | Journaling prompts, emotional check-ins | quill (new) |

Quiet Truths and Daily Stoic become **content series** (a caption tag and a story label) rather than highlights, because they span every theme. Existing "Beauty" and "Start" stories move into Amor fati and Manifesto. This needs 3 new covers and the story labels in `tools/stills.py` specs changed from the next weekly run. I've put this on a decision card. Until you answer, the calendar uses the hybrid names, and they map 1:1 back to the live six.

## Conflict 2: content pillars vs the 13 Oct mission
No real conflict. The mission is the *outcome*; the pillars are the *topics*. Mapping:
| Master-prompt pillar | Mission theme it serves | Highlight | Share of feed |
|---|---|---|---|
| 1 Stoicism (Marcus, Seneca, Epictetus) | all | Daily Stoic series | runs through everything |
| 2 Mental fortitude, emotional regulation | Suffering | Suffering / Feel Logs | 20% |
| 3 Psychology, identity, behaviour | Purpose | Utilities | 15% |
| 4 Discipline, habits, delayed gratification | Virtue | Virtue | 20% |
| 5 Self-awareness, journaling | Suffering / Beauty | Feel Logs | 10% |
| 6 Relationships, attachment, maturity | Virtue | Virtue | 15% (new; nothing covered it) |
| 7 Purpose, ambition, solitude | Purpose / Amor fati | Purpose | 20% |

Two guard-rails come with the new pillars:
- **Psychology:** cite a named study or named concept, never "studies show". No diagnosis or therapy advice. Say "linked to", not "proves".
- **Audience:** the master prompt says a general audience; the 13 Oct mission says mostly young men. I kept **young men** as the primary audience, because all existing copy and the lead magnet are written for them.

## Conflict 3: the weekly routine favours list reels
`research/weekly-routine-prompt-3-a-day.md` step 4 says "favour list and contrast formats" for reels. Our own data says list reels hold worst (25–28%). Lists should go to carousels; reels should use the confrontational hook. The routine prompt can only be edited from its own thread, so the coordinator needs to pass this change on (wording in `07-automation-architecture.md`).

## Conflict 4: Canva vs the Python renderer
The master prompt asks for Canva templates. Production today is `tools/stills.py` + `tools/render_reels.py`: free, fully automated, already in the weekly loop. Recommendation: keep Python as the production engine and build the **same** templates in Canva (specs in `05-canva-template-specs.md`) for hand-made hero posts and future team members. Both use one set of design tokens, so output matches.

## Bio (replace when the guide link is live)
```
Moodius Aurelius | Stoic Wisdom
Ancient philosophy for young men who feel too much and want to become more.
Purpose · Suffering · Amor fati · Virtue
Free: 7 ancient rules ↓
```

## Top 5 actions, in order
1. Host the lead-magnet PDF and put the link in bio (you: 10 min).
2. Add competitors in Metricool: Analytics > Instagram > Competitors (you: 2 min). List in `02-competitor-intelligence.md`.
3. Answer the highlights card. I then make 3 new covers.
4. Pass the routine-prompt change (Conflict 3) to the weekly routine.
5. Reply to comments for 10 min a day.
