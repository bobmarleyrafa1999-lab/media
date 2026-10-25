# 5. Creative templates: Canva-ready specs

Same tokens as `tools/stills.py` and `tools/render_reels.py`, so Canva output and automated output match. Build each template once in Canva, save it as a **Brand Template**, and name the text boxes exactly as the `{{field}}` names. Those names become autofill fields for the Canva Connect API later (needs a plan with brand templates: Pro, Teams or Enterprise, per canva.dev).

## Brand kit (Canva > Brand > Brand Kit)
| Token | Hex | Use |
|---|---|---|
| Stone | `#1B1D1F` | Background base |
| Abyss | `#08090A` | Vignette edges |
| Vein | `#2C2E30` | Marble veins, dividers |
| Cream | `#EDE6D6` | Main text |
| Gold | `#C9A86A` | Monogram, sources, CTA, rules |
| Ash | `#A0988A` | Labels, small text |
| Parchment | `#F5F1E8` | Meme background |
| Ink | `#141414` | Meme text |
| Bronze | `#8C6E3C` | Meme source line |

**Type** (free and in Canva; recommended upgrade from FreeSerif, then mirror it in the Python tools):
| Role | Font | Weight | Size @1080w | Tracking | Line height |
|---|---|---|---|---|---|
| Hook / headline | Cormorant Garamond | SemiBold | 84 | 0 | 1.15 |
| Quote | Cormorant Garamond | Italic | 64–70 | 0 | 1.25 |
| Body | Cormorant Garamond | Regular | 50–54 | 0 | 1.3 |
| Source | Cormorant Garamond | Medium | 40 | +20 | 1.3, Gold |
| Label | Inter | Medium, ALL CAPS | 28–30 | +300 | 1.0, Ash |
| Handle | Inter | Regular | 34 | 0 | Cream 75% |

**Logo set:** "M · A" monogram (Cormorant Bold 44, Gold) above a 200×2px Gold rule. Highlight covers: Gold circle 660px, 6px stroke, glyph inside.

**Background:** Stone fill + 10% noise texture + radial vignette to Abyss + 3–5 faint Vein diagonals at 2px. Save as one image "bg-stone" in Brand Kit so every template reuses it.

**Margins:** 90px left/right on everything. Text never wider than 900px.

---

## T1 Reel card (1080×1920, 9:16)
| Layer | Position | Spec |
|---|---|---|
| bg-stone | full bleed | slow 3% zoom/pan if animated |
| monogram | top 230px, centred | M · A + rule |
| `{{line}}` | vertically centred | Hook/quote: 84 SemiBold or 70 Italic; body: 54 Regular. Max 3 lines |
| `{{source}}` | below line +40px | Gold 40 |
| handle | bottom 280px | @moodiusaurelius |
**Safe zone:** keep text between y=300 and y=1500 (Instagram UI covers the bottom ~420px and the top ~250px).
**Timing:** 6 cards: 3.0 / 2.4 / 3.6–4.2 / 1.8 / 3.0 / 2.4s, cross-fade 0.25s. Music: score.py cue at −14 LUFS.

## T2 Carousel cover (1080×1350, 4:5)
| Layer | Spec |
|---|---|
| monogram | top 90px |
| `{{pillar_label}}` | under rule, Ash caps |
| `{{promise}}` | centre, 84 SemiBold, ≤ 8 words |
| "Swipe →" | Inter 34, Ash, 40px under promise |
| handle | bottom 90px |

## T3 Carousel quote slide (1080×1350)
`{{number}}` label · `{{quote}}` 70 Italic (≤ 30 words) · `{{source}}` Gold 42 · `{{takeaway}}` 54 Regular (≤ 14 words) · handle. Text block vertically centred.

## T4 Carousel evidence slide (1080×1350)
`{{step_label}}` ("1 · Name the judgment") · `{{quote}}` 64 Italic · `{{source}}` · thin Gold rule 120px · `{{modern_concept}}` 52 Regular, starts "Modern name:" · `{{study}}` Inter 30 Ash, "(Author, Year)".

## T5 Framework diagram slide (1080×1350)
Two 400px circles (2px Gold stroke) side by side, or a 2×2 grid of 420px squares (1px Vein lines). Headings Inter caps 30 Ash; contents Cormorant 44 Cream. One line per item, max 5 items per side.

## T6 CTA / "Your turn" slide (1080×1350)
`{{question}}` 84 SemiBold · `{{action}}` 54 Regular ("Save this. Send it to…") · Gold arrow glyph or bookmark icon 80px.

## T7 Meme (1080×1350, Parchment)
Left-aligned at x=80. `{{setup_1}}` Inter 46 Ink 80% · `{{punch_1}}` Cormorant Italic 60 Ink · gap 70 · `{{setup_2}}` "[Name], [N] years ago:" · `{{punch_2}}` quote · `{{source}}` Bronze 38 · handle Inter 32 grey bottom 110px. Max 2 panels.

## T8 Quiet Truth (1080×1350)
No quote marks. `{{truth}}` 84 SemiBold centred, ≤ 12 words. Label "QUIET TRUTHS". Nothing else.

## T9 Story: Daily Stoic (1080×1920)
monogram top 230 · `{{highlight}}` label · `{{quote}}` 70 Italic · `{{source}}` · `{{action}}` 54 · `{{footer}}` Gold 34, 120px above the handle. Leave y=1350–1650 empty for a sticker.

## T10 Story: Feel Log (1080×1920)
Label "FEEL LOG · {{day}}" · `{{prompt}}` 84 SemiBold ("What did you avoid today, and why?") · body "Answer in the box ↓" · empty 700×300 area at y=1300 for the question sticker.

## T11 Highlight covers (1080×1920, art inside the centre 660px circle)
| Highlight | Glyph | Word |
|---|---|---|
| Manifesto | compass rose (✦ or ⌖) | MANIFESTO |
| Purpose | Τ | PURPOSE |
| Suffering | Π | SUFFERING |
| Amor fati | ∞ | AMOR FATI |
| Virtue | Α | VIRTUE |
| Utilities | ⊞ | UTILITIES |
| Feel Logs | quill (✒) | FEEL LOGS |

## Platform resizes (Canva "Resize" or ffmpeg)
| Source | YouTube Shorts | TikTok | Facebook | Pinterest |
|---|---|---|---|---|
| T1 reel 9:16 | same file; title = hook | same; add sound in-app | same | Idea/video pin 9:16 |
| T2–T6 carousel 4:5 | Shorts slideshow (3s/slide) | Photo carousel 4:5 | multi-photo post | Each slide as a 2:3 pin (1000×1500, re-pad top/bottom with Stone) |
| T7 meme 4:5 | n/a | photo post | photo post | 2:3 pin |

## QA checklist (every asset)
1. Text inside safe zone, nothing under 34px.
2. Every quote has author + book + section, or says "paraphrase".
3. Quote not used before (check manifests).
4. Contrast: Cream on Stone 13.6:1, Gold 7.5:1, Ash 5.9:1 (all pass WCAG AA). Bronze on Parchment is 4.2:1, so keep it at 38px or larger.
5. Handle visible. One idea per asset.
