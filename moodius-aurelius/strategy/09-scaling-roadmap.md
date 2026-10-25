# 9. Scaling roadmap: from one brand to 10–20

Rule (Phase 1 Summary): **gated on Moodius thresholds, not dates.** A phase starts only when the previous gate is met; dates below are rough expectations only.

## Phase 0 · Make Moodius work (from 21 Oct 2026)
**Do:** run the 30-day calendar (1 carousel + 1 reel a day), experiments X1–X4, the community layer (11), the free guide and email list.
**Gate to Phase 1 (all of them):**
| Gate | Target | Baseline |
|---|---|---|
| Publishing reliability | ≥ 95% of planned posts live, 4 weeks in a row | Week 2 lost Thu–Sun to the cap |
| QC | ≥ 95% pass first time | not measured |
| Reach | median reel views ≥ 400 (3× baseline) for 3 weeks | ~130 |
| Sends and saves | median sends/reach and saves/reach on carousels both up on the first 10 carousels | measured from 21 Oct |
| Hold | median 3s hold ≥ 40% | ≈ 41% on F1, 25% on lists |
| Learning | ≥ 1 experiment called "winner", ≥ 3 "directional" | 0 |
| Funnel | email capture live, ≥ 50 subscribers | not live |
| Community | ≥ 20 comments or story replies a week answered by you | not measured |
| Your time | ≤ 20 min/day | ~15 |

## Phase 1 · Productise the engine (Dec 2026 – Jan 2027)
- **Brand config:** one file per brand drives every tool.
```yaml
# brands/moodius/brand.yaml
slug: moodius
handle: "@moodiusaurelius"
positioning: "Stoicism for people who feel things"
promise: "Regulate, decide and act when emotions are loud"
voice: "calm, direct, warm; short sentences; names the feeling, then the move"
sources: [Marcus Aurelius, Seneca, Epictetus, Plato, Aristotle, Frankl]
citation_rule: "author, book, section, public-domain translation; else 'Moodius paraphrase'"
banned_visuals: [statues, gold, marble, gradients]
palette: {slate: "#1B1F24", graphite: "#2A2F36", charcoal: "#3A4049", bone: "#F3EFE7", ash: "#B8B3A9", ember: "#C9742E"}
fonts: {display: "Playfair Display", quote: "Playfair Display Italic", ui: "Inter"}
cadence: {carousel: "12:00", reel: "18:00", stories: ["09:00", "21:00"]}
carousel_rotation: {Mon: F1, Tue: F3, Wed: F2, Thu: F8, Fri: F10, Sat: F9, Sun: F7}
primary_metrics: [sends_per_reach, saves_per_reach]
timezone: Europe/Madrid
metricool_brand_id: 7224060
highlights: [Manifesto, Daily, Tools, Discipline, Truths, Journal, Identity]
banned_phrases: ["studies show", "science proves"]
```
- **Repo layout:** `engine/` (renderers, qc, scheduler, analytics) shared; `brands/<slug>/` (config, quote/claim bank, weekly manifests).
- **One weekly routine per brand,** same prompt template filled from `brand.yaml`.
- **SOP docs:** launch checklist, weekly review, incident (failed publish, account warning).
- **Gate:** a new brand goes from config to first scheduled week in ≤ 1 day; cost per post known.

## Phase 2 · Brands 2–3 (Jan – Mar 2027)
Pick niches that reuse the research → script → text/voice reel → carousel engine and have a clear way to make money.

| Niche | Fit with engine | Money | Risk | Verdict |
|---|---|---|---|---|
| Ancient history stories ("Histoics" style) | High: same sources, F7 story reels, YouTube long-form | YouTube RPM (historical sample $8–15), books, affiliates | Needs voice | **Brand 2 candidate** |
| Psychology of everyday behaviour | High: F4 evidence carousels | Courses, journals, apps | Health-claim discipline; overlaps Moodius audience | Brand 3 candidate |
| Stoic money / financial literacy | Medium | Highest affiliate value | Financial-promotion rules (EU/UK): education only, no product picks | Brand 3 candidate, with legal check |
| Productivity / deep work | Medium | Templates, apps | Crowded | Later |
| Philosophy beyond the Stoics (existentialism) | High | Same as Moodius | 20th-century texts in copyright: short quotes only | Later |
| Fitness / discipline | Low (needs footage) | Strong | Health claims, needs bodies on camera | Not faceless-friendly |

**Gate:** each new brand hits its own Phase 0 gate within 10 weeks, and Moodius keeps growing.

## Phase 3 · 5–10 brands (Apr – Jun 2027)
- Move to Metricool Advanced (25 brands, €69 ✓) or direct APIs.
- Assets on object storage, not GitHub.
- One part-time human: community replies + weekly QC across brands (≈ 2 h/day at 10 brands, estimate).
- Portfolio dashboard: one scorecard row per brand per week.
- **Kill rule:** a brand below gate after 12 weeks pauses; its slot goes to the next niche.

## Phase 4 · 10–20 brands (H2 2027)
- Shared research layer: one weekly trend scan feeds all brands' banks.
- Each brand still has its own niche, voice, audience, account, Page and schedule.
- Monetisation stack per brand: lead magnet → email → digital product; affiliates; YouTube/Facebook payouts where eligible.

## Phone farm: assessment
| Possible use | Legitimate? | Better alternative |
|---|---|---|
| Publishing to many accounts | Yes, but pointless | Official APIs and Metricool publish without devices |
| In-app-only actions (trending audio, stickers, highlights, comment replies) | Yes, when a person does them | 1–2 real phones. The Instagram app lets one person switch between several accounts |
| Checking how posts look on real screens | Yes | One iPhone + one Android |
| Scripted taps, auto-likes, auto-follows, view loops, cross-engagement between our accounts | **No.** This is the inauthentic behaviour Meta's Community Standards prohibit (artificially boosting distribution or engagement, coordinated use of multiple accounts), and automated access breaks Instagram's Terms | none; don't do it |

**Verdict:** no phone farm. It adds cost and ban risk and does nothing the APIs don't do better. Budget for 2 phones and one human.

## Compliance rules for every brand
1. Each account is a real, clearly described brand. No fake personas claiming to be real people.
2. Owned accounts never like, comment on or share each other to boost. Open cross-promotion ("our sister page @…") is fine.
3. Original content only. No reposted clips (not recommended by Instagram since 30 Apr 2026).
4. Quotes verified; claims cited; AI-generated media labelled where platforms require it.
5. No bought followers, engagement pods or giveaways for follows.

## Claude does (automatic)
- Tracks every Phase 0 gate in the Friday report and says when one is met.
- When a gate is met: writes `brand.yaml`, splits the tools into `engine/` + `brands/`, drafts the next niche's positioning, format library and first 30 days for your yes or no.

## You do (by hand)
- Say yes or no before each new brand starts (each one means a new account, and possibly spend).
- Create the new Instagram account and connect it to Metricool. Claude can't create accounts, and shouldn't.
