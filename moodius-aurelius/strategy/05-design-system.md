# 5. Design system (Phase 1, approved 20 Oct 2026)

Implemented in `tools/design.py` (tokens), `tools/stills_v2.py` (carousels, stories) and `tools/reels_v2.py` (reels). Canva templates (below) are optional and would mirror the same tokens.

## Canvas and grid
- Carousels 1080 × 1350; reels and stories 1080 × 1920.
- 96 px safe margins, 12-column grid, text left-aligned on the margin.
- Stories keep the bottom 260 px clear for Instagram's reply bar.

## Palette (single accent)
| Token | Hex | Use |
|---|---|---|
| Slate | `#1B1F24` | Background (flat, no gradients) |
| Graphite | `#2A2F36` | Panels, highlight-cover discs |
| Charcoal | `#3A4049` | Rules, dividers |
| Bone | `#F3EFE7` | Main text (14.4:1 on Slate) |
| Ash | `#B8B3A9` | Secondary text, citations (7.9:1) |
| Ember | `#C9742E` | The only accent: kickers, numerals, rules, swipe cue (4.7:1 on Slate) |

## Type
| Role | Face | Size @1080 |
|---|---|---|
| Covers, claims | Playfair Display SemiBold | 84–92 |
| Pull quotes | Playfair Display Medium Italic | 62 |
| Big numerals | Playfair Display ExtraBold, Ember | 170 |
| Body | Inter Regular | 38–44 |
| Kickers, labels | Inter SemiBold caps, tracked | 26–30 |
| Citations | Inter Medium small caps, tracked, **bottom left**, Ash | 24 |
Fonts are in `tools/fonts/` (OFL / system Inter).

## Six components
| Component | Renderer kind | Contents |
|---|---|---|
| Claim cover | `cover` | Ember kicker, claim, optional sub-line, "Swipe →" |
| Pull quote | `quote` | Ember quote mark, quote, short Ember rule, note, citation |
| Term card | `term` | Ember tag, term, Charcoal rule, plain-language definition |
| Numbered step | `step` | Ember numeral, step title, body |
| Pair slide | `pair` | Two column heads (Ash / Ember), rows, Charcoal dividers |
| Sign-off | `signoff` | Closing line, Ember rule, CTA, "Follow @moodiusaurelius" |
Every slide carries the MOODIUS wordmark with an Ember square top-left, page count top-right, citation bottom-left, handle bottom-right.

## Two Canva templates (optional, not built yet)
Not needed to run the plan: every post is rendered by the tools above. If you want to hand-edit in Canva, these are the two templates to build:
1. **Carousel template** (1080 × 1350): six pages, one per component, text boxes named `{{kicker}}`, `{{claim}}`, `{{quote}}`, `{{cite}}`, `{{term}}`, `{{definition}}`, `{{n}}`, `{{title}}`, `{{body}}`, `{{left}}`, `{{right}}`, `{{line}}`, `{{action}}`.
2. **Reel/story template** (1080 × 1920): one text page and one story page with the same tokens.

## Rules
No statues, gold, marble or gradients. One accent. Nothing smaller than 24 px.

## Claude does (automatic)
- Renders every post with these components (done for the first five, this week's re-renders and the 7 highlight covers).
- Canva templates: not built. The Canva connector can't turn our own rendered files into editable designs, so building them needs a person in Canva or a Canva plan with brand templates. Nothing in the 30 days depends on them.

## You do (by hand)
- Nothing required. Only if you want Canva hand-edits: say so, and I'll write the step-by-step build (about 30 min for you in Canva). Canva autofill later needs Pro or Teams, which is a spend, so I'll ask first.
