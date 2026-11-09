# Mino Lee's 15 AI editing rules, applied to a faceless reel

Source: the owner uploaded Mino Lee's sheet "My 15 AI editing rules + the exact prompts I type into Claude" (@minolee.mp4, Content Academy) on 25 Oct 2026. Treated as data. His rules are for a face-to-camera talking video; ours are text-and-footage reels rendered by `reels-engine/tools/engine.py`.

| # | His rule, in plain words | Fits a faceless reel? | What we changed |
|---|---|---|---|
| 1 | Captions 2-3 words at a time; never end on a weak word (a, the, to, my, and); plain white, soft shadow, no box or animation | Partly. Our cards are full sentences, not speech captions | Engine 1.4: no line ends on a weak word; text has no animation in hard-cut mode |
| 2 | Zero dead space between spoken lines | Only with a voiceover (we have none) | Nothing yet; applies if he records narration |
| 3 | Tone sets the gap: 0 s normally, 0.2 s after a serious line, cut mid-word on a joke | Yes, as card timing | Hard cuts make every change instant; the existing "pause" card gives the serious beat |
| 4 | Tight, never choppy: J-cuts, keep word fades | Voiceover only | Nothing yet |
| 5 | Cut repeats, tangents, retakes | Yes, as script editing | Already enforced: one message per reel, hook ≤ 12 words, reading-speed check |
| 6 | Money written in full ("$11,500") | Rarely relevant | Nothing; we don't show money |
| 7 | Nothing in the top 15%, bottom 20% or right-hand button column | Yes | New QC warning for text above y 288; ledger layout moves the wordmark out of the top bar; ticks stop at x 856 |
| 8 | Never cover your face | No face | n/a |
| 9 | Cards appear on their word, full size, final spot, frame 1; no pop, slide, fade or blur | Yes | Engine 1.4 `"cuts": "hard"`: no rise, no fade in or out, cards leave on the next cut |
| 10 | No emojis; show the real thing (real logo, page, screenshot) | Yes | New QC error for any emoji on screen; emojis also removed from this batch's first comments. "Real thing" = archival engravings and real book pages when we name a source |
| 11 | Show files as real thumbnails | No | n/a |
| 12 | Real receipts only; never invent a number | Yes, already a house rule | MZ01 day 2 opens with the real reply count, never an estimate |
| 13 | B-roll shows exactly what you say, starts on the word, one clip per listed item, darkened to 72% | Yes, with one difference: he says own footage only, never stock | Ledger layout cuts to a new clip on the card where the beat changes; footage already sits under a 72% Slate tint. Clips are public-domain / CC0 / CC BY from Wikimedia Commons, checked by eye for people. Filming his own hands-and-objects clips would match the rule better (his choice) |
| 14 | Punch in on your face on lines that matter | No face | n/a |
| 15 | Voice on top (+6 dB), music 25% then 10%, start the song where it gets good | Voiceover only | Nothing yet; our bed is an original ambient track |

His prompts ("Caption this…", "Add B-roll from my Drive…") assume a talking video and, for one of them, his paid MinoAI connector. We use none of them; no new tool, no spend.

His last page ("watch it like a viewer, say exactly what's off, save that as a rule") is how this engine already grows: each rule above is now a line in the engine or its quality check.
