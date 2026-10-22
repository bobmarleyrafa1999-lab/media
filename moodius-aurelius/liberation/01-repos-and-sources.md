# Repos and sources for the Liberation pillar

Checked 22 Oct 2026. "Commercial reel?" means: can it sit under a Moodius reel on an account that also sells a journal. Licences were read on each project page; where a page did not state something, that is said.

**One thing to know first:** almost every famous 20th-century voice (Baldwin, Malcolm X, King, Lorde, Bukowski, hooks) is still in copyright. No GitHub repo makes their words free to use. What repos give you is (a) the public-domain texts and records, verifiable word for word, (b) image archives with machine-readable rights, and (c) tools to fetch, credit and check. For copyrighted voices the rule is one short attributed line (UK quotation exception, CDPA s.30(1ZA); US fair use), or a paraphrase labelled "Idea: … · Moodius words". See `02-roster.csv`.

## Shortlist (use these)

| # | Repo / source | What it gives | Licence | Upkeep | Commercial reel? | Fit with reels-engine / engine-v2 |
|---|---|---|---|---|---|---|
| 1 | [standardebooks](https://standardebooks.org) GitHub repos, e.g. `standardebooks/frederick-douglass_narrative-of-the-life-of-frederick-douglass`, `w-e-b-du-bois_the-souls-of-black-folk`, `john-stuart-mill_on-liberty`, `henry-david-thoreau_essays`, `marcus-aurelius_meditations_george-long`, `epictetus_discourses_george-long`, `seneca_moral-letters-to-lucilius_richard-m-gummere` | Proofread public-domain texts in clean XHTML, one file per chapter | Texts public domain (US); Standard Ebooks' own work CC0 | Active, one repo per book | Yes, quote freely with book + chapter | **Best fit.** Reachable from the project container, so `tools/verify_quotes.py` checks quotes word for word (11/11 pass). Same Long and Gummere translations the engine already allows |
| 2 | [LibraryOfCongress/data-exploration](https://github.com/LibraryOfCongress/data-exploration) | Jupyter notebooks for the loc.gov JSON and IIIF APIs | CC0 | 267 commits, 233 stars | n/a (code); the photos carry per-item rights | Recipe for `fetch_archive.py --source loc` |
| 3 | Library of Congress photos, especially the **U.S. News & World Report collection** (Warren K. Leffler, Marion S. Trikosko, 1950s-80s) | March on Washington, King, Malcolm X, Fannie Lou Hamer, 1960s protest | Per item. Many say "No known restrictions on publication" (checked: Leffler, March on Washington, 28 Aug 1963, item 2013648812) | Live API | Yes where the advisory says no known restrictions | `fetch_archive.py` keeps only those items and writes the credit line |
| 4 | [WordPress/openverse](https://github.com/wordpress/openverse) (the API at api.openverse.org) | One search across Commons, Smithsonian, Met, Flickr Commons and more, with licence filters and a ready attribution string | MIT (code); per-image CC licences | Very active (11.5k commits) | Yes with `license_type=commercial,modification` (the tool sets this) | `fetch_archive.py --source openverse` |
| 5 | Wikimedia Commons API (no repo needed; [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot) if you want one) | Largest pool of historical portraits; also the CC0 Dutch National Archive (Anefo) press photos 1945-89 | Per file: PD, CC0, CC BY, CC BY-SA | Live | PD, CC0, CC BY yes. **CC BY-SA no by default**: text over the photo is an adaptation, so the reel would have to be BY-SA too | `fetch_archive.py --source commons` reads the licence from file metadata |
| 6 | [Smithsonian/OpenAccess](https://github.com/Smithsonian/OpenAccess) + Open Access API (free key from api.data.gov) | Metadata for millions of objects incl. NMAAHC; images only for CC0 items | CC0 (metadata and released images) | Refreshed weekly | Yes for items that have a CC0 image; many NMAAHC items have no open image | Via Openverse, or add a key later |
| 7 | [NYPL-publicdomain/data-and-utilities](https://github.com/NYPL-publicdomain/data-and-utilities) | 187k public-domain items incl. Schomburg Center material | CC0 | Snapshot from Dec 2015 (317 stars); current data needs an NYPL API token | Yes, items are public domain | Search the CSV offline for leads, then download from NYPL |
| 8 | [metmuseum/openaccess](https://github.com/metmuseum/openaccess) | 470k-object CSV | CC0 | 1.4k stars, "updated on a regular basis" | Yes for public-domain objects | Little civil-rights material; useful for older art. Images not in the repo (Git LFS CSV only) |
| 9 | [owid/etl](https://github.com/owid/etl) + Our World in Data charts (V-Dem civil liberties index, 1789-2025) | Dated data for empirical cards ("civil liberties worldwide since 1789") | OWID charts CC BY; V-Dem's own terms apply to the underlying data (not stated on the OWID page, check before use) | Active | Yes with credit "Our World in Data / V-Dem (2026)" | Fits the engine's "data" source type, which already requires a dated cite card |
| 10 | [garethbjohnson/gutendex](https://github.com/garethbjohnson/gutendex) | JSON search over Project Gutenberg for texts Standard Ebooks hasn't done (Ida B. Wells, Harriet Jacobs, Equiano, Garvey-era pamphlets) | MIT (code); Gutenberg texts PD in US | 385 stars, small but stable | Yes for the PD texts | Gutenberg is blocked from the container; run on the Mac or the Action |

## Also useful, not GitHub
- **UN Universal Declaration of Human Rights.** The UN says the text "may be reproduced … without prior permission" when distributed free. Fine for reels; ask permissions@un.org before printing it in anything you sell. Remove the UN emblem.
- **Congressional Record (govinfo.gov).** Floor speeches by members of Congress (John Lewis, Barbara Jordan, Shirley Chisholm) are US government records and treated as public domain. The best route to modern civil-rights words with no copyright worry.
- **Europeana API** (free key). Filter `reusability=open` = CC0, CC BY, CC BY-SA only. Skip `restricted` (non-commercial).
- **Wikiquote** for discovery only. It separates "sourced" from "disputed" and "misattributed", which is the useful part. Never cite it as the source.

## Looked at and skipped
- **Quote APIs and datasets** (e.g. Quotable and Kaggle-style quote dumps): no primary sources, full of misattributions. Fails the "never invent quotes" rule.
- **Open Images (Google)**: modern Flickr photos with CC BY claims Google doesn't vouch for. Off-brand, and no archival material.
- **Unsplash / Pexels**: free for commercial use with no credit needed, but modern stock. Fine for neutral textures (paper, light, window); never for history or people.
- **AI captioning repos** (BLIP and similar): HuggingFace is blocked, and a model guessing who's in a 1963 photo is a misinformation risk. Use the archive's own caption and date.
- **Quote-over-image video repos** (MoviePy templates, Remotion templates): nothing they do that `engine.py` 1.2 doesn't already do (still background, slow drift, Slate tint, grain). Remotion also needs a paid company licence above 3 people.
- **Internet Archive uploads of 1960s speeches**: uploader rarely owns the rights. Don't use audio or video of King, Malcolm X or Baldwin speeches; the estates enforce.
- **Slave Voyages / colonial-history datasets**: heavy material, and terms are mostly academic or non-commercial. Not for a reel brand.

## How it plugs in (built on this branch)
- `tools/fetch_archive.py`: search LoC / Commons / Openverse, keep only commercially safe images, save as `<tag>-<n>.jpg` with `credits.csv`. Copy the images into `reels-engine/footage/`; engine 1.2 already uses a jpg named by tag as a drifting still. 8 unit tests pass.
- `.github/workflows/fetch-archive.yml`: the same tool as a button in GitHub Actions (Actions → Fetch archive images → Run). Needed because the project container can't reach any of these archives; GitHub's runners can. Results download as a zip.
- `tools/verify_quotes.py`: checks every public-domain quote in `quotes.csv` against Standard Ebooks on GitHub. Runs in the container.
- One engine change is needed before rendering: `PD_TRANSLATIONS` in `engine.py` only lists translators (Long, Gummere…), so a Douglass or Mill quote (English originals) fails the gate. Proposed: accept `"translation": "original (public domain)"`. Not changed here because another thread owns the engine.
