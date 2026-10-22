# Media mirror (option A, prepared, not switched on)

If this repo (`media`) goes private, `raw.githubusercontent.com` links into it stop working, and Metricool
needs public links whenever a post is created, re-scheduled or updated. Option A keeps a second, **public,
renders-only** repo, `bobmarleyrafa1999-lab/moodius-media`, that holds only finished images and videos.

- `mirror.py list` shows exactly what would be public: about 494 files, 0.85 GB, only `.mp4/.jpg/.jpeg/.png`
  from the render and post folders in `ALLOW`. No scripts, docs, data, strategy, ledgers, hook-intel
  thumbnails or personal order files.
- `.github/workflows/moodius-media-mirror.yml` copies them on every push to `main`, at the **same paths**,
  and never deletes anything there (archived files stay reachable at their old public path too).
- `mirror.py repoint FILE... [--write]` swaps old links for new ones. Only the prefix changes:
  `raw.githubusercontent.com/bobmarleyrafa1999-lab/media/<branch>/moodius-aurelius/...` becomes
  `raw.githubusercontent.com/bobmarleyrafa1999-lab/moodius-media/main/moodius-aurelius/...`

## Switching it on (only after the owner picks option A)

1. Create the public repo `moodius-media` (empty, no README) on github.com.
2. Create a fine-grained token: Settings > Developer settings > Fine-grained tokens, repository access
   "Only select repositories" > moodius-media, permission Contents: Read and write. Save it in `media` as the
   repository secret `MOODIUS_MEDIA_TOKEN`.
3. In `media`: Settings > Secrets and variables > Actions > Variables: `MOODIUS_MEDIA_MIRROR` = `true`.
4. Actions > "Moodius media mirror" > Run workflow. Check a few links open in a private browser window.
5. Only then make `media` private.

## What needs repointing (account thread)

Posts already in the Metricool queue are safe: Metricool copied their files to static.metricool.com.
Links matter only for new posts, re-schedules and edits. These build or store `media` links:

| Where | What to change |
|---|---|
| Friday routine prompt (`trig_011adyEthea3vbBPNS2Dwnov`) | Build media links from `moodius-media/main/` instead of `media/claude/project-thread-*`, and commit new weeks to `main` of `media` (pushes to `bxasif` are not mirrored) |
| Daily publish check (`trig_01KuimLeNzzqrFNe6Tp4DMNq`) | Same prefix, if it re-posts or edits anything |
| `strategy/schedule-21-25-oct.json` | 52 links into `claude/project-thread-bxasif` (posts already queued; only for re-schedules) |
| `week3/posts.json` | 1 link into `claude/project-thread-o20fqk` |
| Any Metricool `updateScheduledPost` call on a PENDING post | Use the new prefix for its media |
| `community-agent/deploy/setup.sh` | Fetches a script from `claude/project-thread-ycspok`; works only while `media` is public. Clone with a token instead (server route only, not used by the free Actions mode) |

Run `python3 moodius-aurelius/media-mirror/mirror.py repoint <files>` for a count, then add `--write`.
