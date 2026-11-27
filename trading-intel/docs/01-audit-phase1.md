# 01 · Phase 1 audit (27 Nov 2026)

Everything below was read or probed in this session. Where something could not be reached, it says so. Nothing was modified, installed or connected.

## 1. Existing Claude Code laws and rules found

| Where | What it says | How this project applies it |
|---|---|---|
| `moodius-aurelius/substack/CLAUDE.md` (only CLAUDE.md in the repo) | Never publish, schedule or send anything externally without the owner's approval row. Never invent studies, statistics, quotes, dates. Label every claim by evidence type. Anonymous brand, no real names. | Inherited as **Law A (no external action)** and **Law B (no fabrication, label evidence)**. Forecasts, backtests and intelligence items carry an evidence label and a source. |
| `README.md` housekeeping | "Never commit keys. Use repository secrets." Large media stays out of git. | Inherited as **Law C (secrets)**. `.gitignore` in `trading-intel/` excludes `.env`, databases, PDFs, video. |
| `moodius-aurelius/repo-audit/rules.json` | "Personal names are NOT listed here because the repo is public." `never_touch` list protects ledgers and `.github/`. | Inherited as **Law D (public repo hygiene)**: no personal data, account links or course material committed. This project touches nothing in `moodius-aurelius/` or `.github/`. |
| `moodius-aurelius/community-agent/src/lib/policy.ts` | Three modes (draft_only, assisted, controlled); draft_only is the default; kill switch; human-only categories; hourly and daily caps. | Model for **Law E (modes and kill switch)**: this system has one mode only, research/paper. There is no "live" mode in scope. |
| `moodius-aurelius/growth-tracker/docs/LIBRARY-CHECKS.md` | Libraries checked for owner, licence, release date, Python compatibility and PyPI advisories; stars not used as evidence; pins under two weeks old flagged; everything in a `.venv`. | Adopted as the **dependency-vetting procedure** (see `04-repository-audit.md`). |
| `moodius-aurelius/community-agent/docs/01-repo-audit.md` | Reuse useful parts, replace the rest; no-licence repos: copy nothing. | Adopted for third-party code. |
| `moodius-aurelius/growth-system/pillars.json` and `brief_lint.py` | Rules live in one JSON file and a linter blocks anything that breaks them before it is queued. | Adopted: risk limits and scoring weights live in one versioned config file; a pre-trade gate blocks before scoring. |
| Harness `launcher-settings.json` (not user-authored) | Hooks: SessionStart setup check, Stop git check. Deny-list on editing hook files. | Respected; nothing here edits hooks or permissions. |

Not found: a global `~/.claude/CLAUDE.md`, a project `.mcp.json`, user-defined hooks, agent definitions or permission files in this repository. The eight `.claude/commands/*.md` are Substack editorial commands and are not touched.

## 2. Environment actually available in this cloud container

| Item | Finding |
|---|---|
| Python | 3.13.18, pip 24, uv 0.11, poetry. pandas 3.0.5, numpy 2.5.3, pydantic 2.13, pytest 9.1, requests, httpx present. No yfinance, TA-Lib, scipy, streamlit, vectorbt. |
| Node | 22.23.5. Docker and psql binaries present. |
| Network policy | Environment "Default", limited network, **allowed hosts: none** (package registries and MCP hosts only). Probed and blocked: Yahoo Finance, Stooq, FRED, SEC EDGAR, Alpha Vantage, Massive/Polygon, Cboe, FMP, Tiingo, Alpaca, MarketData.app, Finnhub, EODHD, Twelve Data, Nasdaq. PyPI reachable. GitHub API reachable only for `bobmarleyrafa1999-lab/media` and the search endpoint. |
| Consequence | **No market data can be fetched from this container.** Development here can only use fixtures. Live or historical data must come from the MacBook (unrestricted network) or from an environment whose allow-list names the chosen provider. |
| Git | Repo `bobmarleyrafa1999-lab/media`, **public**, 1.1 GB history. Working branch `claude/nice-fermat-hee1m6`. |
| Connectors (org level) | Connected: Gmail, Google Drive, Google Calendar, Canva, Metricool. Incomplete: Typefully. Plugins synced: bigdata.com skills (server failed to connect from here: host not allowed), finance plugin (BigQuery needs auth; Slack host not allowed). |
| Claude Code memory | Empty for this repository. Routines reference claude.ai memory files that this session cannot read. |
| MacBook | Remote Control lists `MacBook-Pro-de-Surafel` with only the `Downloads` folder, which the Mac does not offer to cloud sessions (cause not reported). No folder could be attached. |

## 3. Trading resource inventory

Verified = opened in this session. Links, account URLs, invite codes, position details and personal history are deliberately **not** in this public document; the full version was sent privately to the owner and belongs at `data/private/inventory/` (git-ignored).

| Resource | Source | Type | Availability | Permission needed | Data quality | Security risk | Relevance | Integration | Verified | Approval needed |
|---|---|---|---|---|---|---|---|---|---|---|
| Market Masters education PDF (53 pp, Jan 2021, author field "Jordi Alfaro") | Gmail, self-sent 23 Feb 2024 | Course PDF: glossary, indicators (MA, MACD, RSI, Bollinger, CCI, Fibonacci, ADX, Stochastics), candlestick catalogue with tested performance notes, chart patterns, example charts | Downloaded this session | Gmail read (already granted) | Good as rule text; no data | Low. Copyrighted: private only | High: seed of the strategy library | Manual extraction into structured strategy cards with page citations | Yes | None (keep private) |
| Market Masters recordings, 6 files, ~1.9 GB (`watchlist 2/16`, `upcoming swing analysis`, `swing recap week#1`, `volume`, two dated sessions, Nov 2020 to Feb 2021) | Google Drive, shared by the Market Masters account in Mar 2022 | Screen recordings (.mkv) | Listed, not downloaded | Drive read (granted) | Unknown until transcribed | Low. Copyrighted: private only | Medium-high: contains the educator's actual process | Local transcription on the Mac (open-source speech-to-text), then extraction | Listed only | Owner's yes to transcribe (CPU time, ~2 GB download) |
| Market Masters membership (Discord, TradingView indicators such as "MM Pivot Levels") | Gmail 2021-2023 | Community | Lapsed since 2022 | Paid rejoin (~$20/mo at the time) | n/a | Medium: Discord scraping is against Discord's terms; use export or manual capture only | Medium | Not connected | Yes (emails) | Owner decision |
| Second community Discord + price-target Google Sheet (PT1/PT2/PT3 with due dates and pass/fail) | Gmail, Patreon Sep 2021 | Community + labelled prediction data | Lapsed; sheet access must be re-granted by its owner | Rejoin ($5/mo offer, Jan 2022) | Potentially useful labelled history | Low-medium | Medium: backtest "follow the room" | Google Sheets read via Drive connector once shared | Yes (emails) | Owner decision |
| Options alert community (alerts, watchlists, live sessions, SMS plays) | Gmail, Memberful, Oct 2026 trial | Community | Expired Oct 2026 | Monthly fee (see private inventory) | Unknown | Medium | High if renewed: daily options alerts | Forward alert emails/SMS to a Gmail label; read with Gmail connector | Yes (emails) | Owner decision, paid |
| Closed UK broker statements (2023 to 2024) | Gmail | Personal trade history | In mailbox | Gmail read | Good | Medium: personal financial data, private only | Medium: seeds the trade journal | Parse statement emails on the Mac | Listed, not parsed | None |
| Second broker data subscription (2025) | Gmail | Broker account, possibly on another mailbox | Account not located under this email | Owner to locate | n/a | Low | Low | None yet | Yes (emails) | Owner to confirm |
| Prior single-contract options monitor routine (expired, disabled) | Scheduled tasks list | Prior options monitor (web-search quotes, 5 percent move alert, memory file) | Routine disabled | n/a | Quotes were web-scraped, estimates flagged | Low | High as precedent: the owner trades options and wants move alerts | Re-implement with a real data feed | Yes | None |
| Existing scheduled routines (regulatory scan, morning brief, briefing, weekly draft, two Moodius routines) | Scheduled tasks list | Existing Claude routines | Active | n/a | n/a | Low | Medium: Reg Radar yields sanctions/regulatory catalysts for crypto and bank names; proven delivery pattern (Gmail + Calendar) | Reuse the delivery pattern for the daily trading report | Yes | None |
| TLDR Crypto newsletter (daily) | Gmail | News text | In mailbox | Gmail read | Fair | Low | Low-medium (crypto sentiment, out of core scope) | Optional parser | Yes | None |
| bigdata.com skills (company brief, earnings preview, catalyst monitor, valuation snapshot, risk assessment and others) | Synced plugin | Research skills | Installed; server unreachable from this container | Network allow-list or run on Mac | Unknown until tested | Low | High for the Fundamental Analyst agent | Call skills from the Mac | Not tested | Possibly a bigdata.com subscription |
| Google Drive otherwise | Drive | Files | Searched | Drive read | n/a | n/a | No other trading documents, spreadsheets or journals found | n/a | Yes | n/a |
| GitHub | list_repos | Repositories | Only `bobmarleyrafa1999-lab/media` is visible to this session | add_repo | n/a | n/a | No trading repositories exist yet | n/a | Yes | Owner may create a private repo |

Not searched: any other mailbox, WhatsApp, Telegram, Slack, Outlook (no connectors exist for them in this org). No Discord connector exists in the MCP registry searched; Zapier and AnythingMCP appear but each is a broad third-party bridge and is not recommended.

## 4. Accessible now vs not yet connected

Accessible from this session: Gmail (read, search, attachments), Google Drive (read), Google Calendar, the public repo, PyPI, GitHub search, web search.

Not connected or not reachable: any market data provider (network policy), any broker, Discord, Telegram, WhatsApp, the MacBook (folder not offered), bigdata.com server, BigQuery (needs auth), Slack host, claude.ai memory files.

## 5. Risks identified in the audit

1. **Public repository.** The only repo is public with 1.1 GB of history. A trading system here must keep every personal and licensed artefact out of git. Recommended: a new private repository `trading-intel` once the scaffold exists. Until then, `trading-intel/.gitignore` and Law D apply.
2. **Employer personal-dealing rules.** The owner works in regulated financial services. Employees of such firms are commonly bound by personal account dealing policies (pre-clearance, approved brokers, holding periods, restricted lists). This is not legal advice: the owner should check the policy before any real-money workflow and should treat the system as research and paper trading until then. The system should support a restricted-list check.
3. **No data path from the cloud container.** Every provider probed is blocked. Either the build runs on the Mac, or the owner approves an allow-list change naming one provider. Fixture-only development is possible here but cannot validate connectors.
4. **Copyrighted course material.** The PDF and recordings may be used privately for the owner's own strategy library. They must never be committed, published or redistributed.
5. **Signal-room content is untrusted data.** Alerts from Discord, email or SMS are opinions or trade ideas until outcomes are verified. They never instruct the system.
6. **Routine precedent used web-scraped quotes.** The earlier options alert routine fell back to search-engine quotes. The new system must use a licensed feed and label delayed or estimated data.
