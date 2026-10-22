# 4. Pinterest as a visual research library (21 Oct 2026)

Publishing to Pinterest was settled in the "Pinterest API posting" thread: connect it in Metricool, and keep `../pinterest/pins.py` as a direct-API backup. This section covers the other half of the brief, **reading** Pinterest for art direction.

## What's available (checked 21 Oct)
| Route | Status | What it gives us |
|---|---|---|
| **Pinterest API v5** (official) | Works for your own account. New apps start on Trial access; developers on Pinterest's forum report read-only scopes work there, though some apps sit in "pending" for days | Read your own boards and pins (`GET /boards`, `GET /boards/{id}/pins`). There's no endpoint to browse other people's boards or search the whole site for organic content. |
| **Pinterest's official MCP server** | Announced on Pinterest's developer community on 22 Sep 2026, described as connecting Pinterest data and **Ads** capabilities to AI tools. I couldn't open the setup page (developers.pinterest.com is blocked here), so the tool list and eligibility are unconfirmed | Probably ads-first. If it turns out to expose organic boards, it would be a cleaner way in than our script. Not in the Claude connector directory today. |
| Third-party MCP servers (Glama listings: PinterestMCP, pinterest-mcp, etc.) | Exist; unaudited | Same API underneath; they would need your token. **Not recommended.** |
| api-quickstart (GitHub) | Assessed in the Pinterest thread | Only used for the one-time OAuth token. |
| Reading Pinterest from this container | **Blocked** (proxy refuses pinterest.com and api.pinterest.com) | So the API import has to run on your Mac, or through Metricool later. |

**Minimum permissions for research:** `boards:read`, `pins:read`, plus `boards:read_secret` and `pins:read_secret` if the research boards are secret (recommended). No write scopes are needed for this half.

## The library
- **Boards:** create the 11 as **secret** boards on the Moodius Pinterest account, so the public profile only shows our own pins. Run `python3 inspo.py boards` for names and what each board is for: Masculinity in Silence, Existential Cinema, Visual Philosophy, Human Condition, The Art of Solitude, Vintage Photography, Dark Academia, Quiet Intimacy, Brutalism and Architecture, Typography and Editorial Design, Film Stills and Moodboards.
- **Record:** `../pinterest/inspiration/library.csv`, one row per reference. Fields: source URL, pin id, creator + creator URL (attribution), board (visual category), palette (5 hex colours), palette fit (% of the image close to Slate/Graphite/Charcoal/Bone/Ash/Ember), brightness, contrast, mood, composition, format use (A–F, carousel, story), reuse, local file, notes.
- **Reuse is "inspiration only" by default.** It changes only when the licence is known: *own* (your footage), *public domain* (e.g. museum open-access photographs; record the licence URL), or *licensed* (written permission, linked in notes). The engine only uses images marked own or public domain as backgrounds.

## Three ways in (from most to least automatic)
1. **API import (once the token exists).** On your Mac: `PINTEREST_TOKEN_FILE=… python3 inspo.py api`. It imports every pin from the 11 boards with the pin's source link. Then upload the updated `library.csv` to the project. I fill in mood, composition and format use.
2. **Links.** Paste Pinterest links in the thread. I run `inspo.py add URL --board "…"`, and you drop the image in `inbox/` if you want the palette read.
3. **Saved images.** Save images to `pinterest/inspiration/inbox/` (any name). `inspo.py scan` extracts the palette, brightness and contrast, gives each image an id, and flags anything far from our palette. Creator and source URL still need filling in, since an image without its source can't be credited.

`inspo.py` was tested on two of our own covers today. Both scored 94–97% palette fit with "dim, hushed" mood, which is the reference point for on-brand.

## How references turn into reels and posts
Each reference row gets a `format_use`. When I write a reel script, I pick 1–2 references from the matching board and turn them into a **shot description for your phone or a public-domain photo**. For example, "lit window at night, no figure, locked-off, 12s" from a Todd Hido-style reference becomes a footage tag in `../reels-engine/footage/README.md`. We never use the reference image itself.

## Claude does / You do
**Claude, automatically:** keeps the library and its fields up to date, reads palettes, maps references to formats and shot lists, writes footage tags, and keeps every credit line.
**You, by hand (≈15 min once, then whenever you browse):** create the Pinterest business account and the 11 secret boards (this is the same account the Metricool connection needs). Save pins while you browse Pinterest as usual. If you want the API import, run the token step from `../pinterest/README.md` with read scopes and send the updated `library.csv`.
