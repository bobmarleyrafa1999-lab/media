# 27 · Grid refresh (27 Oct 2026)

Goal: make the profile grid look more interesting while staying professional, and change it
gradually so followers see an evolution, not a rebrand.

## What changes on every post (format v2, all options)

| Today | v2 |
|---|---|
| Headline about 78 px, small in the grid | Headline 104 px, fills the tile so it reads at grid size |
| "MOODIUS" wordmark on every tile | Pillar label: MIND / BODY / PEOPLE + post number (e.g. MIND · NO. 41) |
| Short Ember line under the text | One key word underlined with a hand-drawn Ember brush stroke |
| Flat colour | Fine paper grain (hand-made texture, never a gradient) |
| No frame | Thin inset frame, so the grid reads as one set of cards |

Fonts stay Playfair (headlines) + Inter (labels). Ember stays the only accent.

## The three colour options

Colour follows the order posts go out (post n gets `cycle[n % len]`), so the pattern survives
every new post and every archive of an older one.

| Option | Colours, in order | What the grid does |
|---|---|---|
| A · Paper and ink | Bone, Slate | Checkerboard. Calmest; closest to today. |
| B · Ember thread | Bone, Slate, Ember, Slate | Checkerboard with an Ember diagonal. Boldest. |
| C · Three columns | Sand, Slate, Olive | Three steady vertical stripes. New colours, still warm and muted. |

New colours (option C only): Olive `#4A4C37`, Sand `#E4D9C4`. Both sit next to the approved
Slate/Bone/Ember and avoid the banned looks (no gold, marble, statues, gradients, AI stock).

## The gradual change (3 steps)

| Step | Posts | What changes |
|---|---|---|
| 0 | Everything already in Metricool (to 4 Nov carousels, 7 Nov reel) | Nothing. Live and queued posts stay as they are. |
| 1 | 5 to 8 Nov | Format v2 only, still all Slate. Same colour, sharper type. |
| 2 | 9 to 15 Nov | Every other carousel uses the option's light colour; reels stay Slate. |
| 3 | From 16 Nov | Full pattern. Locked in before the 20 Nov cadence switch and the 23 Nov meme test, so the test doesn't measure a look change. |

`mocks/option-X-transition.png` shows what the top 12 look like during the change (bottom row
today, top row 16 Nov). `mocks/option-X-end-state.png` shows the finished grid.

## Files

- `build/grid_v2.py`: renderer. `mocks`, `samples`, or `cover` for one tile.
- `mocks/`: 12-tile grid previews, end state + transition per option.
- `renders/option-X/`: a full 5-slide carousel and reel covers per option (1080x1350, 1080x1920).
- `canva/CANVA-GUIDE.md`: brand colours, fonts and click-by-click steps to make the same posts in Canva.
- `fonts/`: Playfair Display and Inter (SIL Open Font License).

## Hooking it into the engine (after the pick)

- Carousel slide 1: `grid_v2.tile(hook, ground, "carousel", label, no)`; inner slides: `grid_v2.inner(...)`.
- Reel cover (Metricool `videoThumbnailUrl`): `grid_v2.tile(hook, ground, "reel", label, no)`.
  The reel video itself is unchanged; only the cover in the grid follows the pattern.
- Ground: step 1 = `slate`; step 2 = `ground_for(option, n, 2, kind)`; step 3 = `cycle[n % len]`,
  n counted from the first step-3 post (16 Nov 12:00).
