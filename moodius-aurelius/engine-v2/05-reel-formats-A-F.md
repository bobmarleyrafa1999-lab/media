# 5. Six reel formats, A–F (21 Oct 2026)

These are original formats built on the existing renderer (`../reels-engine/tools/engine.py`, now v1.2). Each one has a sample reel rendered today from `../reels-engine/scripts/formats-AF.json`, and all six pass the quality gate.

| Code | Format | Sample (in `../reels-engine/renders/`) | Length | Sits on R-format | Highlight | Judge it on |
|---|---|---|---|---|---|---|
| **A** | The Uncomfortable Question | `A01-said-it-out-loud.mp4` | 16.6s | new (R1 family) | Identity | sends/reach |
| **B** | Quiet Truths | `B01-busy-room.mp4` | 13.6s | = R1 | Truths | sends/reach |
| **C** | The Philosophical Contradiction | `C01-discipline-two-readings.mp4` | 18.0s | extends R3 | Discipline | comments/reach |
| **D** | The Human Condition | `D01-the-bench.mp4` | 23.4s | new (essay) | Journal | saves/reach, 3s hold |
| **E** | Masculinity, Reconsidered | `E01-call-for-no-reason.mp4` | 19.2s | new | Identity | sends/reach |
| **F** | A Thought Worth Keeping | `F01-friends-who-train-you.mp4` | 18.8s | = R2/R5 | Daily | saves/reach |

R4 (dry humour) stays as it is, at most 2 a week. R5 (one book, one idea) folds into F whenever the idea comes from a modern book.

## Common to all six
- **Canvas and export:** 1080×1920, 30 fps, H.264 High, CRF 20, yuv420p, AAC 160 kbps, loudness −14 LUFS (true peak −1.5), `+faststart`. Cover = a frame from the hook card. A caption file goes with every MP4.
- **Type:** Playfair SemiBold for hook/question cards (84/88 px), Playfair Medium Italic for quotes (64), Inter Medium for body (60), Inter SemiBold for the CTA (50), Inter SemiBold 30 in Ember for labels, and Inter 32 in Ash, uppercase, for cite cards. Left-aligned on a 96 px margin with the text block in the upper third, clear of Instagram's caption overlay.
- **Motion:** each card rises 14 px and fades in over 0.3 s. There are no other transitions. A still photo drifts about 5% across the whole reel. Film grain (`"texture": "grain"`) is optional.
- **Backgrounds, three looks:** **V1** flat Slate. **V2** your own phone clip. **V3** (new) a still photograph, either your own or public domain, never a third-party Pinterest image. V2 and V3 are desaturated and tinted 72% Slate. If no clip or still exists for a script's footage tag, it falls back to V1.
- **Audio:** an original ambient bed from `ambient.py` (night, dawn, warm, low, dry, room). No voice-over, no trending audio, no "epic" music.
- **Reading speed:** the gate refuses any card shown for less than 0.4 s + 1 s per 4.5 words.
- **Evidence line:** captions end with "Evidence: … / Reflection: Moodius / Source: …", following the four tiers in `01-brand-identity.md`. A study or survey must have a cite card with a year, and the gate enforces this.

## A. The Uncomfortable Question
A single, psychologically precise question that the viewer answers silently. The discomfort is the hook.
| Time | Card | Screen text (A01) |
|---|---|---|
| 0–3.0s | question (Playfair 88 + Ember rule) | When did you last say what you felt, out loud, to someone? |
| 3.0–5.2 | body | Not hinted. Not turned into a joke. |
| 5.2–6.6 | body | Actually said. |
| 6.6–9.6 | body: release the shame | If the answer is in months, that's not a flaw in you. |
| 9.6–12.0 | body: the reframe | Plenty of men were never handed the words. |
| 12.0–14.0 | cite | Idea: Levant, normative male alexithymia (1992) · Moodius words |
| 14.0–16.2 | CTA | Send this to the one you'd answer honestly. |
**Shots:** V3 rain on a window at night (tag `window-rain`), or V1 + grain. **Audio:** room. **Caption:** restate the question in everyday terms, take away the shame, then ask "what would you say?" **Rule:** the question must be about the viewer's own behaviour, never about someone else, and never answerable with a diagnosis.

## B. Quiet Truths
A thought in two or three parts that goes past the quote: claim, then turn, then something small to do.
| Time | Card | Screen text (B01) |
|---|---|---|
| 0–2.6 | hook | Being busy is the most respectable way to avoid yourself. |
| 2.6–4.6 | body (outside) | From outside it looks like ambition. |
| 4.6–7.2 | body (inside) | From inside it's a room you never sit down in. |
| 7.2–9.6 | body (act) | Tonight, sit in it for one song. No phone. |
| 9.6–11.0 | series mark | Quiet Truths · Moodius |
| 11.0–13.2 | CTA | Save it for the week you can't stop. |
**Shots:** V1 flat Slate. This is the control look for the series. **Audio:** night. **Rule:** part 2 has to add something part 1 didn't say. If it only rephrases part 1, cut it.

## C. The Philosophical Contradiction
Steelman two plausible readings of the same virtue, then show what tells them apart. It ends on a choice, not a verdict.
| Time | Card | Screen text (C01) |
|---|---|---|
| 0–2.4 | question | Is discipline self-respect or self-punishment? |
| 2.4–5.6 | labelled "ONE READING" | You keep your word to yourself because your word counts. |
| 5.6–8.8 | labelled "THE OTHER" | You grind because resting feels like proof you're worthless. |
| 8.8–11.0 | body | Same alarm. Same gym. Different engine. |
| 11.0–13.6 | body | Pressure gets you started. Wanting it is what lasts. |
| 13.6–15.6 | cite | Idea: Ryan & Deci, self-determination theory (2000) · Moodius words |
| 15.6–17.6 | CTA | Which one woke you up this morning? |
**Shots:** V1 + grain, or a brutalist stairwell still (V3, tag `stairs`). **Audio:** low. **Other topics to run it on:** identity (found vs made, Marcia vs Nietzsche), suffering (meaningful vs simply bad, Frankl vs Camus), solitude (restorative vs avoidant). **Rule:** both readings must sound reasonable to someone who holds them.

## D. The Human Condition
A cinematic miniature essay of up to about 100 words (the Tiny Love Stories limit) about a moment everyone recognises, with one dated finding at the turn. It runs 20–30 s and the gate allows up to 30 when `max_s` is set.
| Time | Card | Screen text (D01) |
|---|---|---|
| 0–3.0 | hook (the scene) | You drive past a place you used to be someone else in. |
| 3.0–6.0 | body (the detail) | The bench is still there. The person sitting on it isn't. |
| 6.0–9.2 | body (the feeling) | For a second you miss that version of you more than anyone. |
| 9.2–12.0 | body (the turn) | People who study nostalgia found it's mostly not sadness. |
| 12.0–16.0 | body (the finding) | It shows up when we're lonely, and pulls us back toward the people who made us. |
| 16.0–18.2 | cite | Wildschut, Sedikides, Arndt & Routledge · J. Pers. Soc. Psychol. (2006) |
| 18.2–20.8 | body (the line to keep) | Missing who you were is proof you became someone. |
| 20.8–23.0 | CTA | Send it to someone who was on that bench. |
**Shots:** V3 or V2 tagged `bench` (an empty bench or a lit window at dusk, locked off, no people). Allow 2–3 clips at most, each held for 5 s or more. **Audio:** warm. **Rule:** a concrete object in the first 6 seconds, and no advice in the essay. The only instruction allowed is the CTA.

## E. Masculinity, Reconsidered
Men's emotional lives, without toughness theatre or blaming women. One cited fact, one reframe of a "masculine" virtue, and one small act.
| Time | Card | Screen text (E01) |
|---|---|---|
| 0–2.8 | hook | Nobody taught you how to call a friend for no reason. |
| 2.8–5.6 | body | So you wait for one. A birthday. A match. A wedding. |
| 5.6–7.8 | body | Months go by. You call it being busy. |
| 7.8–11.8 | body (the fact) | In 1990, 3% of US men said they had no close friend. In 2021: 15%. |
| 11.8–13.6 | cite | Survey Center on American Life (2021) |
| 13.6–16.6 | body (the reframe) | Self-reliance is a strength until it's the reason you never ask. |
| 16.6–18.8 | CTA (act) | Text one friend tonight. No reason needed. |
**Shots:** V2 `phone-table` (dark phone, lamp), or V1 + grain. **Audio:** night. **Guardrails (enforced by the gate):** no alpha/beta/sigma, SMV, hypergamy, simp, "female nature" or red-pill language. Women are never the cause, the prize or the punchline. Strength is never mocked. Sources lean on E13 (Wong et al.), E14 (Addis & Mahalik), E18 (Cox) and P14 (hooks).

## F. A Thought Worth Keeping
A carefully sourced classic line, read slowly, then one application to life in 2026.
| Time | Card | Screen text (F01) |
|---|---|---|
| 0–2.6 | hook (modern frame) | The friends you keep are training you for something. |
| 2.6–4.8 | body (who and when) | Seneca, writing to a friend, around 65 AD: |
| 4.8–11.8 | quote (Playfair italic) | "Associate with those who will make a better man of you. Welcome those whom you yourself can improve. The process is mutual; for men learn while they teach." |
| 11.8–13.4 | cite | Letters 7.8 · tr. Richard M. Gummere |
| 13.4–16.6 | body (application) | Not networking. One friend who makes you better, and you return it. |
| 16.6–18.4 | CTA | Send this to yours. |
**Shots:** V1 flat (quotes read best clean), or a dark-academia desk still (V3, tag `desk`). **Audio:** dawn. **Rule:** quotes only from public-domain translations, checked against the citation registry, with the section on screen. Modern thinkers (Camus, Frankl, Fromm, Kierkegaard in modern translation, hooks, Beauvoir) appear as "Idea: … · Moodius words" and are never quoted. *The F01 wording matches the Goodreads text and the Latin of Ep. 7.8. Check it against the Gummere print before it's scheduled.*

## Tools verdict (from the dedicated threads, plus this one)
| Tool | Verdict | Status |
|---|---|---|
| FFmpeg engine (`engine.py`) | **Default renderer.** v1.2 adds the question, labelled and pause cards, V3 stills with drift, grain, `max_s` and the data-cite rule. Its output for the 20 existing scripts is unchanged (filter graphs compared one by one) | installed, used today |
| Remotion | Licence free for us (≤3 people). Use it for kinetic text the FFmpeg engine can't do, e.g. word-by-word reveals in F and split screens in C. Test it as one experiment after the cover test (~mid-Nov) | prototype in `../reels-engine/remotion/` |
| instagram-transcript | Works, but only on your Mac (Instagram and the model download are blocked here). It captures speech, not on-screen text | waiting on reel links |
| n8n | Not a reel tool. Useful as glue for IG stats and comment DMs on a €4–6/month VPS, waiting on your spend OK and a Meta app setup. Not installed separately | proposed, gated on spend |
| Pinterest api-quickstart | Used only to get the OAuth token. Publishing goes through Metricool, reading through `inspo.py api` | waiting on the business account |

## Claude does / You do
**Claude, automatically:** writes scripts per format from the research library, runs the gate, renders, writes captions with evidence lines, and passes reels to the account thread for Metricool. A–F slot into the existing 18:00 reel and don't add to the cadence.
**You, by hand (optional, 20 min once):** shoot the new footage tags `window-rain`, `bench`, `stairs` and `desk` (`../reels-engine/footage/README.md`). Without them every format still renders on Slate + grain.
