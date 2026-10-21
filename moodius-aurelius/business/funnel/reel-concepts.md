# Product reels P001-P006

Six reels that sell the journal (five) and the free guide (one). They're rendered and pass the reels engine's quality check. **None are scheduled.** They'd go into Metricool only once the shop is live on a real domain, because each one tells people to comment for a link.

Source: `reels/product-batch.json` (reels-engine schema). Renders: `reels/renders/<id>-<slug>.mp4`, with cover JPG and caption TXT alongside.
Re-render: `python3 /mnt/project-files/moodius-aurelius/reels-engine/tools/engine.py render reels/product-batch.json --out reels/renders`

| ID | Hook | Format | Sells | DM keyword | Link sent in the DM |
|----|------|--------|-------|-----------|------|
| P001 | Most people have never once looked at their defaults. | R1 cards | Journal | JOURNAL | `/r/journal?src=dm_reel_p001` |
| P002 | Stop asking yourself why. Ask what. | R2 | Journal (Day 3) | JOURNAL | `/r/journal?src=dm_reel_p002` |
| P003 | Here's what's inside the journal, page by page. | R4 pages | Journal | JOURNAL | `/r/journal?src=dm_reel_p003` |
| P004 | When someone you love goes quiet, what do you do? | R1 | Journal (Day 17) | JOURNAL | `/r/journal?src=dm_reel_p004` |
| P005 | Seven evenings. Ten minutes each. Free. | R1 | Free guide | GUIDE | `/r/guide?src=dm_reel_p005` |
| P006 | My journal won't fix you. Here's what it does. | R2 | Journal (honesty) | JOURNAL | `/r/journal?src=dm_reel_p006` |

Each script has an alternative hook (`hook_b`) for the hook test (T1) once the cover test finishes.

## Suggested order once the shop is live

1. P005 (free guide) first, to start the list without asking for money.
2. P002 and P004 (the strongest "idea" reels, which work even for people who never buy).
3. P001, P003, P006 as the direct offers, one per week, mixed into the normal schedule. Product reels should stay under one in five posts.

## DM keyword flow

Comment JOURNAL or GUIDE → a DM with the matching link above. Until the community agent's keyword DM is live, Surafel sends these by hand from saved replies in the Instagram app (one saved reply per keyword, with the `src` for that reel). The agent's keyword list includes both JOURNAL and GUIDE.

**Once the community agent sends the DMs**, its links use `src=dm_journal` or `src=dm_guide`, and the agent attributes each DM to its reel from the comment's media id (see the update section of `community-agent/INTEGRATION-CONTRACT.md`). The per-reel `dm_reel_<id>` links above are for saved replies sent by hand until then. The agent's `/r/newsletter` goes to its own consent page, not Substack.


## Rules they follow

The P-series uses the brand's rules: Marcus lines labelled as Moodius paraphrases, the Watkins (2008) and Fraley et al. (2015) findings stated with their evidence strength, no therapeutic claims, and P006 points to Samaritans 116 123.
