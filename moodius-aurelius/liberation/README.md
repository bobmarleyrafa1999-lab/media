# Liberation pillar ("Free Minds")

Civil liberties, history and decolonising the mind, added to "Stoicism for people who feel things" without replacing it. Draft only, nothing scheduled.

| File | What |
|---|---|
| `01-repos-and-sources.md` | 10 vetted repos/sources (licence, upkeep, commercial use, pipeline fit) + what was skipped and why |
| `02-roster.csv` | 23 voices, mostly 20th century: core / use with care / skip, why they fit, what to avoid, copyright and image route |
| `03-pillar.md` | How it fits the brand, 10 guardrails, 10 hooks, 5 reel concepts with sourced quotes and visuals |
| `quotes.csv` | 26 usable lines + 3 known fakes. Public-domain lines verified word for word; copyrighted lines flagged with their use rule |
| `tools/verify_quotes.py` | Checks the public-domain quotes against Standard Ebooks on GitHub (13/13 pass) |
| `tools/fetch_archive.py` | LoC / Wikimedia Commons / Openverse search that keeps only commercially safe images and writes credit lines |
| `tests/` | 9 unit tests for the licence rules, parsers and the no-faces filter |
| `../.github/workflows/fetch-archive.yml` | The fetch tool as a button in GitHub Actions (the project container can't reach the archives) |

```
python3 tools/verify_quotes.py
python3 -m unittest discover -s tests
python3 tools/fetch_archive.py --source loc --query "manuscript page" --tag pages --n 4
```
