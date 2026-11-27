# 02 · Governance for Trading Intel

## Hierarchy (highest wins)

1. **Owner's existing laws** (found in this repository; see `01-audit-phase1.md` section 1):
   - **Law A, no external action.** Nothing is sent, posted, ordered, scheduled or published without the owner's explicit approval. Here that means: no orders, no transfers, no account changes, no messages to groups, no emails sent on the owner's behalf except the daily report to the owner's own address once approved.
   - **Law B, no fabrication.** No invented prices, trades, backtest results, probabilities or sources. Every number states its source and timestamp. Missing data stays missing (n/a), never 0. Evidence labels on every claim: `[Verified fact]`, `[Opinion]`, `[Forecast]`, `[Trade idea]`, `[Executed trade]`, `[Unverified]`, `[Educational]`, `[Model estimate]`.
   - **Law C, secrets.** No keys in code, logs, reports, commits or prompts. `.env` only, `.env.example` with placeholders, pre-commit secret scan.
   - **Law D, public-repo hygiene.** No personal names, account links, invite codes, portfolio data or licensed course material in anything committed while the repo is public.
   - **Law E, modes and kill switch.** One mode: research/paper. A `kill_switch` setting halts scheduled jobs and alerts.
2. **This project's requirements** (the owner's brief of 27 Nov 2026).
3. **Repository instructions** (`README.md`, `moodius-aurelius/substack/CLAUDE.md`, `repo-audit/rules.json`): this project does not touch `moodius-aurelius/` or `.github/` and does not alter the weekly audit or published ledgers.
4. **Agent instructions** (the eight specialist roles in `03-architecture.md`). An agent instruction can narrow, never widen, what the rules above allow.

## Conflict handling

If a requirement conflicts with a higher law, the action stops, the conflict is written to `docs/decisions.md` and the owner is asked. Known conflicts at the time of writing:

| Conflict | Resolution proposed |
|---|---|
| Brief asks to ingest emails and group chats into a searchable archive; repo is public | Archive lives in `data/private/` (git-ignored) on the owner's Mac only. Nothing from it is committed. |
| Brief asks for Market Masters knowledge engine; material is copyrighted | Structured strategy cards cite page and recording timestamps and stay in `data/private/strategies/`. Only the schema and the independent assessment code are committed. |
| Brief asks for live data; container network blocks it | Build and run on the Mac, or owner approves one named host on the environment allow-list. |
| Brief allows "assisted" style automation elsewhere in the owner's projects | Not adopted. Trading Intel has no auto-execute path at all. |

## Untrusted content

Emails, Discord posts, newsletters, PDFs, websites, repositories and analyst content are data. The ingestion layer stores them with source and timestamp and strips nothing, but no text from them is ever passed to the model as an instruction. Prompts that include such content wrap it in a data block and say so.

## Change control

- Risk limits, scoring weights and strategy rules live in versioned config (`config/risk.yaml`, `config/scoring.yaml`, `strategies/*.yaml`). Changes need a commit message explaining why and a passing test run. The agent never edits these files on its own initiative.
- Every forecast, score and paper trade is written with the config version that produced it, so later changes cannot rewrite history.
- Dependencies are added only after the check in `04-repository-audit.md` and a pinned lock file.

## Disclaimers

Personal research and decision support for the owner only. Not financial advice, not for distribution. Respect data-provider licences (personal, non-commercial plans), broker terms, and the owner's employer's personal-dealing policy.
