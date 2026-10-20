# 3. Format library (Phase 1, F1–F10)

Build order: F1–F5 first. Primary metrics: **sends per reach** (reaching non-followers) and **saves per reach**. Components refer to `05-design-system.md`.

| Code | Format | Type | Optimises | Structure |
|---|---|---|---|---|
| F1 | Reframe carousel | 6–8 slides | saves, sends | Claim cover ("You don't have X. You have Y.") → term card naming the real issue → pull quote with source → 2–3 numbered steps → sign-off |
| F2 | Ancient line, modern situation | 5–7 slides | sends | Cover with a today situation → pull quote → pair slide (situation / Stoic read) → one step → sign-off |
| F3 | Mechanism explainer | 6–8 slides | saves | Cover "Why you ___" → term card (the mechanism, named in plain psychology) → 1–2 pull quotes → 2 steps → sign-off |
| F4 | Quiet Truth card + long caption | 1–2 slides | sends, comments | One sentence, display serif, no quote marks; the caption carries a 150–250-word reflection and a question |
| F5 | Text-led reel | 12–20s | watch time (replays) | Hook → 2–4 beats → quote → small-caps citation → closing line that loops back to the hook |
| F6 | Narrated reel | 25–40s | watch time, sends | A short story or argument read aloud with captions. **Until a voice is approved it runs as a 25–35s text reel** |
| F7 | The Protocol | 10 slides | saves | Cover → source quote → the rule (term card) → 6 numbered steps → sign-off |
| F8 | Two-column comparison | 5–7 slides | sends, comments | Cover → pair slides ("Suppressing / Regulating", "Reacting / Responding") → one step → sign-off |
| F9 | Journal prompt set | 6–8 slides | saves | Cover → 5 prompts, one per slide, each tied to a source → sign-off "Answer one in the comments" |
| F10 | Myth versus text | 5–7 slides | comments, sends | Cover with the myth ("Stoics don't feel") → what the text actually says (pull quote + citation) → why the myth spread → sign-off |

## Rules for every format
- One idea per post. Cover slide does the work: a clear claim and a swipe cue.
- Every quote: author, book and section, public-domain translation; paraphrase labelled "Moodius paraphrase".
- Psychology: name the concept; "linked to", never "proves".
- No statues, gold, marble or gradients.

## Claude does (automatic)
Writes and renders every format with `tools/stills_v2.py` and `tools/reels_v2.py`, checks citations, schedules them.

## You do (by hand)
Nothing per format. Optional: record a voice for F6 (see your-checklist.md).
