# media

Everything for the Moodius Aurelius page lives in `moodius-aurelius/`. `main` is the single source;
per-thread `claude/project-thread-*` branches are working branches that get merged here.

| Folder | What it holds |
|---|---|
| `strategy/` | Strategy docs 00-16, the 30-day tracker and experiments (read by the weekly routine), reel-first plan, upload packs, grid patterns, n8n automation, ads and reach plans |
| `reels-engine/` | Reel formats, scripts (`scripts/batch-01.json`), renderer `tools/engine.py`, renders, Remotion prototype |
| `engine-v2/` | Research library, account study, reel formats A-F |
| `hook-intel/` | Hook research system and its fetcher (GitHub Actions) |
| `liberation/` | Free Minds pillar: sources, roster, verified quotes, archive image fetcher |
| `substack/` | Essays, packages, vault, scripts (QC, exports) for the Substack publication |
| `audio/` | Sonic identity, original tracks list, licence log, mixing tools |
| `brand/`, `profile/`, `lead-magnet/` | Logos, highlight covers, profile pack, free guide |
| `threads/`, `pinterest/` | Threads posts and avatar, Pinterest pins |
| `research/` | Adaptations from followed accounts, page studies |
| `business/` | Storefront (Cloudflare Pages), journal product, finance model, funnel reels |
| `community-agent/` | Comment and revenue agent (free GitHub Actions mode) |
| `week1/`-`week3/`, `reels/`, `fixes-*` | Early posting weeks and one-off fixes |
| `repo-audit/` | Weekly self-cleaning audit (see its README) |
| `_archive/` | Created by the audit when ticked items are archived; `MOVED.csv` maps old paths to new |

## Housekeeping

- A weekly audit (Mondays) opens an issue labelled `repo-audit` with a checklist. Nothing changes until the
  owner ticks lines and comments `/apply`. Details: `moodius-aurelius/repo-audit/README.md`.
- Large video and audio: git keeps every version forever, and this repo is already about 0.9 GB. New mp4,
  wav and m4a renders are better kept in the project folder or Git LFS. Existing paths stay, because posts
  were scheduled from `raw.githubusercontent.com` links to some branches.
- Never commit keys. Use repository secrets (Settings > Secrets and variables > Actions).
