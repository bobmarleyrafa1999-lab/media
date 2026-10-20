# 10. Reconciling the strategy pack with the "Phase 1 Summary" (20 Oct 2026)

Compares this folder's pack (files 01–09) with the uploaded "Moodius Aurelius: Phase 1 Summary". Nothing has been deleted or re-rendered. Each conflict has a recommendation, and Surafel decides.

## Where they agree (adopt as settled)
| Topic | Both say |
|---|---|
| Name | Keep Moodius Aurelius. It fits emotional-regulation content. |
| Pillars | Keep all seven, and give relationships / emotional maturity more weight. |
| Citations | Book + section on every quote, public-domain translations (Long, Gummere). **Adopt the Phase 1 label:** paraphrases are marked "Moodius paraphrase". |
| Carousels | Carousels lead on saves; single images are the weakest format. |
| Formats | Quiet Truth + long caption, myth vs text, narrated reel, two-column comparison / framework, journal prompts, text-led short reel. The two libraries cover the same ground under different codes (mapping below). |
| Competitors | Quote aggregators plateau. Copy the practical, framework-led anonymous model (@stoicismideas). |
| Stack | Claude for copy, Canva brand templates with autofill, Metricool for scheduling and analytics, Sheets as the system of record. |
| Phone farm | No legitimate benefit over official APIs. |
| Scaling | Gate it on Moodius results, not dates. |
| Testing | Sends per reach and saves per reach are the primary metrics. |

## Conflicts and recommendations
| # | Topic | Strategy pack (01–09) | Phase 1 Summary | Recommendation |
|---|---|---|---|---|
| 1 | Positioning | Young men (the mission you set on 13 Oct) | "Stoicism for people who feel things": emotionally literate, broader audience | **Use the Phase 1 line as the tagline. Keep young men as the main reader in captions.** The line is the better hook and counters the aggressive Stoic content young men already see. The audience claim behind it (Everyday Stoic "over 75% female") is unverified; I couldn't find a source. |
| 2 | Cadence | 3 feed posts a day (16 reels, 3 carousels, 1 meme, 1 Quiet Truth a week), the cadence you asked for on 12 Oct | 1 carousel + 1 reel a day for 30 days | **2 reels + 1 carousel a day.** It keeps the 3 a day you asked for and adds a daily carousel as the Phase 1 plan wants. Reels are proven here (115–143 views vs 1–11 for images); carousels are not tested yet. After 30 days, cut whichever loses on sends + saves per reach. |
| 3 | Highlights | Hybrid seven: Manifesto, Purpose, Suffering, Amor fati, Virtue, Utilities, Feel Logs | Your seven, relabelled: Manifesto, Daily, Tools, Discipline, Truths, Journal, Identity | **Phase 1 set.** It keeps the seven you called established and uses plain one-word labels, which read better on a profile. Old stories map like this: Start → Manifesto, Purpose → Identity, Virtue → Discipline, Suffering and Amor fati → Truths, Beauty → Journal. The mission themes stay as story topics. **This replaces my earlier hybrid recommendation.** |
| 4 | Visual system | Current renderer: stone + marble veins, Cream text, Gold accent, Cormorant + Inter | Slate / Graphite / Charcoal / Bone / Ash, **Ember #C9742E** as the single accent; no statues, gold, marble or gradients; Playfair or Cormorant + Inter | **Adopt the Phase 1 palette and the no-marble/no-gold rule. Keep Cormorant Garamond rather than Playfair.** My own audit scored the visuals 3/5 for looking like every quote page, and marble and gold are the reason. Contrast checks out: Bone on Slate 14.4:1, Ash 7.9:1, Ember 4.7:1. Use Ember only at 24px or larger or for rules and icons, since it's 3.0:1 on Bone. Cost: change the tokens in `tools/stills.py` and `render_reels.py` (about an hour). The new look starts on the first week after you approve. |
| 5 | First five posts | Rendered: be-one reel (Med 10.16), weep reel (Letters 63.1), "who to let close" carousel, "3 habits psychology tested" carousel, story-views meme | Written, not designed: self-trust carousel, rude-person post, 2am-replay explainer, evening-review protocol, regulating-not-suppressing reel | **Ship the rendered five first, and re-source the Phase 1 five for the next batch.** The Phase 1 posts have strong hooks, but every source they name is already used on the account (table below), which breaks the no-repeat rule. |
| 6 | Research claims | Benchmarks with dated sources (Socialinsider 2026: carousels 0.05% save rate vs reels 0.04%) | "Carousel ER 0.55%", "~80% of carousel engagement comes from the cover", "Instagram signalled a preference for human-feeling content in 2026" | **Treat these three as unverified** until a source is attached. None was in the summary, and I couldn't confirm them. They don't change any decision above. |
| 7 | Testing cadence | Up to 2 experiments at once (different slots), call a winner at 9 of 10 matched pairs | 1 experiment at a time, 2 variants, at least 10 posts per variant | **Take the Phase 1 floor of 10 posts per variant**, and allow a second experiment only when it runs in a different format (reels vs carousels). |

## Why the Phase 1 five need new sources
| Phase 1 post | Sources named | Already on the account |
|---|---|---|
| 1 "You don't have a discipline problem. You have a self-trust problem." | Discourses 2.18 | Week 2/3 manifests |
| 2 "When someone is rude to you today…" | Meditations 2.1, 4.7 | reel-4 (2.1), reel-18 (4.7) |
| 3 "Why you replay the argument at 2am" | Letters 13.4, Enchiridion 5 | reel-6 (13.4), Week 3 meme (Ench. 5) |
| 4 "The 5-minute evening review" | On Anger 3.36 | strategy post 4, slide 2 |
| 5 "Three signs you are regulating, not suppressing" | Meditations 8.47 | strategy post 4, slide 1 |

Suggested new sources (all unused): 1 → Epictetus, Enchiridion 48 (signs of progress). 2 → Enchiridion 20 (it is your opinion that insults you). 3 → Seneca, Letters 98.8 ("He who suffers before it is necessary, suffers more than is necessary"). 4 → keep the protocol and swap the strategy post-4 slide to a different line. 5 → Marcus, Meditations 7.8 (the future, met with the same reason). Same hooks, same formats.

## Format code mapping
| Phase 1 | Strategy pack |
|---|---|
| F1 Reframe carousel | F3/F8 carousels |
| F2 Ancient line, modern situation | F1 confrontational reel / F5 meme |
| F3 Mechanism explainer | F4 ancient ↔ modern evidence |
| F4 Quiet Truth + long caption | F9 |
| F5 Text-led reel 12–20s | F1 / F6 |
| F6 Narrated reel 25–40s | F7 |
| F7 The Protocol (10 slides) | F8 (adds a 10-slide protocol variant) |
| F8 Two-column comparison | F8 framework |
| F9 Journal prompt set | F10 Feel Log (as a carousel too) |
| F10 Myth vs text | F2 |
Once the conflicts are decided, I'll merge both libraries under one set of codes.

## What changes once Surafel decides
- Positioning: bio and the weekly routine prompt's mission line.
- Cadence: rebuild `calendar-days-8-30.csv` with 2 reels + 1 carousel a day.
- Highlights: 7 new covers in the new palette, plus the story label mapping above.
- Visual: update renderer tokens, re-render the five posts in the new look before scheduling (content unchanged).
- First five: schedule them in Week 4, then make the re-sourced Phase 1 five.
