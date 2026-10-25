# 9. Scaling roadmap: from one brand to 10–20

Rule: a phase starts only when the previous gate is met. Dates are targets, not promises.

## Phase 0 · Make Moodius work (now – mid-Dec 2026)
**Do:** run the 30-day calendar and experiments, host the lead magnet, build `qc.py` and the post log.
**Gate to Phase 1 (all of them):**
| Gate | Target | Baseline |
|---|---|---|
| Publishing reliability | ≥ 95% of planned posts live, 4 weeks in a row | Week 2 lost Thu–Sun to the cap |
| QC | ≥ 95% pass first time | not measured |
| Reach | median reel views ≥ 400 (3× baseline) for 3 weeks | ~130 |
| Hold | median 3s hold ≥ 40% | ≈ 41% on F1, 25% on lists |
| Learning | ≥ 1 experiment called "winner", ≥ 3 "directional" | 0 |
| Funnel | email capture live, ≥ 50 subscribers | not live |
| Your time | ≤ 20 min/day | ~15 |

## Phase 1 · Productise the engine (Dec 2026 – Jan 2027)
- **Brand config:** one file per brand drives every tool.
```yaml
# brands/moodius/brand.yaml
slug: moodius
handle: "@moodiusaurelius"
audience: "young men 18-30"
mission: "purpose, meaning in suffering, amor fati, virtue, beauty"
voice: "first-person older brother, short sentences, no clichés"
sources: [Marcus Aurelius, Seneca, Epictetus, Plato, Aristotle, Frankl]
palette: {bg: "#1B1D1F", text: "#EDE6D6", accent: "#C9A86A", muted: "#A0988A"}
fonts: {display: "Cormorant Garamond", ui: "Inter"}
formats: {F1: 0.35, F2: 0.12, F6: 0.15, F7: 0.05, F3: 0.05, F4: 0.05, F8: 0.05, F5: 0.05, F9: 0.05}  # share of feed
slots: ["12:00", "15:00", "18:00"]
timezone: Europe/Madrid
metricool_brand_id: 7224060
highlights: [Manifesto, Purpose, Suffering, Amor fati, Virtue, Utilities, Feel Logs]
banned: ["studies show", "science proves"]
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
| Stoic money / financial literacy for young men | Medium | Highest affiliate value | Financial-promotion rules (EU/UK): education only, no product picks | Brand 3 candidate, with legal check |
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
