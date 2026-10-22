# Research library ("the depository")

Every fact, story and quote that goes into a Moodius reel, carousel, caption or essay comes from here,
with its source attached. If it is not in this library, it does not go on the page.

- `tidbits/<figure>.csv` – one row per tidbit. Open in Numbers/Excel/Google Sheets.
- `LIBRARY.md` – readable version of every tidbit with its status. Rebuilt by `tools/library.py index`.
- `SOURCES.md` – the colour-coded list of repos, APIs and archives we draw from, with licences.
- `tools/library.py` – checks tidbits word for word against the source text, finds passages, and searches the open APIs.
- `discover/` – raw search results from the APIs (leads, not facts).
- `.sources/` – downloaded texts (cache, not committed).

## Tidbit format

| field | what goes in it |
|---|---|
| `id` | figure code + number, e.g. `EP014`. Never reuse an id. |
| `figure`, `topic` | e.g. Epictetus / Biography, Stories, Teaching, Legacy |
| `claim` | the fact in plain Moodius words, as it could appear in a post |
| `evidence` | the exact words in the source that back the claim (copy, don't retype). Use `...` to skip words. |
| `kind` | `text` = machine-checked against a registered text; `web` = a page or book we read by hand |
| `source`, `locator` | registered text key (`python3 tools/library.py sources`) and section, e.g. `discourses` `1.18`. For `web`, the full book/article title and page. |
| `author`, `translator` | who wrote it, and the public-domain translator if any |
| `link` | where anyone can read it |
| `licence` | what we're allowed to do with the wording |
| `tier` | primary (their own words) · ancient testimony (someone who knew them or wrote soon after) · scholarly · late testimony |
| `caveat` | what a careful historian would add; read this before you write the post |
| `verified_by`, `verified_at` | the tool or person that checked it, and the date |
| `status` | `verified` (machine check) · `manual` (read by hand) · `retired` |
| `use_in` | post idea or arc slot |

## Rules (same as the project's quote rule)

1. **Evidence or nothing.** No invented studies, numbers or quotes. A claim with no exact evidence line is not a tidbit.
2. **Quotes are word for word** from a public-domain translation (Long, Gummere, Stewart, Rolfe). Anything rewritten is labelled *Moodius*.
3. **Cite book and section** on the post: "Epictetus, Discourses 1.18 (tr. Long)".
4. **Copyrighted voices** (Beck, Stockdale, Baldwin...) get one short credited line, never next to the shop.
5. **Read the caveat.** Many "famous facts" are legends (the broken leg, EP005). Say "one story says" when the tier is not primary.
6. 🟠 manual rows get a second look before a Sunday deep-dive carousel.

## Commands

```bash
cd moodius-aurelius/research/library
python3 tools/library.py verify                    # check everything; exits 1 if anything fails
python3 tools/library.py locate discourses "iron lamp"
python3 tools/library.py section enchiridion 5
python3 tools/library.py sources
python3 tools/library.py index                     # rebuild LIBRARY.md
python3 tools/library.py discover "Septima Clark"  # needs open internet: Mac or the GitHub Action
python3 tools/test_library.py
```

Only GitHub-hosted texts (Standard Ebooks, Perseus) are reachable from Claude's container, so those
are the machine-checked ones. Gutenberg, Internet Archive, Open Library, OpenAlex, Semantic Scholar
and Wikisource are searched by the GitHub Action **Research discover** (Actions tab → Run workflow →
type a topic). It saves results to `discover/` on the branch; a Claude thread then turns the good
leads into tidbits.

## Adding a new figure

1. Run `discover` for the figure. Pick public-domain primary sources first.
2. If the text is on GitHub (Standard Ebooks, Perseus, OpenITI), add it to `SOURCES` in `library.py` so tidbits can be machine-checked.
3. Write rows in `tidbits/<figure>.csv`, run `verify`, then `index`.
