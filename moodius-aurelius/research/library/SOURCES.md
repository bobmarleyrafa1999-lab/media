# Sources and scraper repos

Checked 22 Oct 2026. Licences were read from each repo's own LICENSE file (git clone), not from memory.
🟢 use now · 🟠 use with a condition · 🔴 don't use. "Here" = reachable from Claude's container;
"Action" = run through the GitHub Action or on the Mac. Nothing here costs money.

## 1. Texts (where the words come from)

| | Source | What it gives us | Licence | Reach |
|---|---|---|---|---|
| 🟢 | **Standard Ebooks** (github.com/standardebooks) | Clean, proofread public-domain books: Epictetus, Marcus, Seneca, Douglass, Thoreau... | Texts CC0. Their `tools` repo is GPL-3 (we only read the texts) | Here (raw GitHub) — machine-checked |
| 🟢 | **Perseus Digital Library** (PerseusDL/canonical-greekLit, canonical-latinLit) | Greek/Latin originals and old Loeb translations: Gellius, Diogenes Laertius, Plutarch, Cicero | CC BY-SA 4.0 for the encoding; credit "Perseus Digital Library". Translations pre-1930 are public domain | Here — machine-checked (Gellius wired in) |
| 🟢 | **First1KGreek** (OpenGreekAndLatin/First1KGreek) | Greek texts Perseus lacks, incl. Simplicius and later commentators | CC BY-SA 4.0 | Here |
| 🟢 | **Project Gutenberg** via **Gutendex** (garethbjohnson/gutendex, MIT) | Tens of thousands of public-domain books, searchable JSON | Books public domain in the US; check UK (author dead 70+ years) | Action |
| 🟢 | **c-w/gutenberg** | Python: download and strip Gutenberg texts | Apache-2.0 | Action |
| 🟢 | **Wikisource** (MediaWiki API, pywikibot MIT) | Transcribed public-domain books incl. Gummere's Seneca letters, Hardy, Douglass speeches | Public-domain texts; page text CC BY-SA | Action |
| 🟢 | **Internet Archive** (`jjjake/internetarchive`) | Scans and OCR of old books, 19th-c. translations, newspapers | Tool AGPL-3 (fine to run, don't ship it in a product). Each book has its own rights | Action |
| 🟢 | **Open Library** (`internetarchive/openlibrary-client`) | Find editions, page counts, "borrow" copies of modern books to check a page | Catalogue CC0; client AGPL-3 | Action |
| 🟢 | **OpenITI** (OpenITI/RELEASE) | Arabic manuscript texts: useful for the Timbuktu deep dive | Mixed per text; releases on Zenodo | Here (GitHub) |
| 🟠 | **HathiTrust** full-text search | Find the exact page in a 19th/20th-c. book | Free search; full view only for public domain | Action, by hand |
| 🔴 | Anna's Archive, LibGen, Z-Library | Pirated copies | Copyright infringement | Never |
| 🔴 | quote sites (BrainyQuote, Goodreads quotes, stoic-quotes APIs) | Unsourced and often wrong attributions | — | Never as a source; only as a lead to check |

## 2. Psychology and science (for "the study says" posts)

| | Source | What it gives us | Licence | Reach |
|---|---|---|---|---|
| 🟢 | **OpenAlex** (pyalex, MIT) | Hundreds of millions of papers, citation counts, open-access links | Data CC0 | Action |
| 🟢 | **Semantic Scholar API** (`danielnsilva/semanticscholar`, MIT; allenai/s2-folks Apache-2.0) | Paper search with one-line summaries and citation counts | Free API, metadata only | Action |
| 🟢 | **Europe PMC / PubMed** | Medical and psychology abstracts | Abstracts free to read; quote briefly | Action |
| 🟢 | **FReD replication database** (forrtproject/FReD, MIT) | Did a famous psychology finding replicate? Check every "study says" post here first | MIT | Here (GitHub) |
| 🟠 | **Crossref + Retraction Watch** | DOI lookup and retraction check | Free; Crossref blocked from the container | Action |
| 🟠 | `paper-scraper` (blackadad, public domain) | Pulls PDFs from many sites | Respect each site's terms | Mac only |
| 🔴 | `scholarly` (Google Scholar scraper) | Google Scholar results | Breaks Google's terms, gets blocked | Don't |

## 3. Reference (to check facts, not to quote)

| | Source | Use | Licence |
|---|---|---|---|
| 🟢 | **Wikidata** (SPARQL) | Birth/death dates, places, for a quick cross-check | CC0 |
| 🟠 | **Wikipedia** (Wikipedia-API, MIT) | Leads and its footnotes. Never the final source: follow the footnote | CC BY-SA |
| 🟠 | **Stanford Encyclopedia of Philosophy**, **Internet Encyclopedia of Philosophy** | Expert summaries to check our reading | Copyright: paraphrase and cite, don't copy |
| 🟢 | **Library of Congress** (LibraryOfCongress/data-exploration, CC0), Chronicling America | Civil-rights era papers and newspapers for Septima Clark, Arthur Ashe | Mostly public domain, check per item |
| 🟢 | **Met Museum Open Access** (metmuseum/openaccess) and **Smithsonian Open Access** | Hokusai prints and other artworks, with dates and provenance | CC0 (no-faces rule still applies) |

## 4. Tools for keeping it organised

| | Tool | Use | Licence |
|---|---|---|---|
| 🟢 | **tools/library.py** (this folder) | Word-for-word check, locate, discover, index | ours |
| 🟢 | **Zotero** + translation-server | A personal reference manager if you want one on the Mac | AGPL; free app |
| 🟢 | **CLTK** (cltk/cltk, MIT) | Greek/Latin processing if we ever check originals | MIT |
| 🟠 | **papis** (GPL-3), **JabRef** (MIT) | Command-line / desktop bibliography managers | Only if Zotero isn't enough |

## 5. Where each deep dive will come from

| Arc | Best primary sources | Status |
|---|---|---|
| Epictetus (12-15 Nov) | Discourses, Enchiridion (Long, Standard Ebooks); Gellius (Perseus); Meditations 1.7 | 🟢 29 tidbits in `tidbits/epictetus.csv` |
| Hokusai | Met + Smithsonian open-access records; his own colophon to *Thirty-six Views* / *One Hundred Views of Mt Fuji* (translations needed) | 🔵 next if picked |
| Ramanujan | His 1913 letter to Hardy and papers (Wikisource), Hardy's obituary of him (1921) | 🔵 check the copyright of Hardy's 1940 *Apology* before quoting it |
| Septima Clark | LoC civil-rights collections, SNCC Digital Gateway, oral-history interviews (to locate) | 🟠 her books are copyrighted: short quotes only |
| Arthur Ashe | Newspaper archives, *Days of Grace* (1993, copyrighted) | 🟠 short quotes only |
| Timbuktu manuscripts | OpenITI, Mamma Haidara Library digitisation, Library of Congress *Ancient Manuscripts from the Desert Libraries of Timbuktu* exhibit | 🟢 strong primary material |

Already reviewed elsewhere (don't re-audit): the faceless-video repos in the project's creator-repos list.
