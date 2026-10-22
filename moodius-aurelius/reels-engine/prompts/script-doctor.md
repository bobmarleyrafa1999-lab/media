# Script Doctor (reels-engine 1.3)

A second pass on every beat-grammar script, after writing and before `engine.py check`. Adapted from Purffle Studios' purffle-shorts "Script Doctor" (MIT): score the draft, list what is weak, rewrite to fix exactly that. Moodius additions are marked (M). No AI voice, no faces, Phase 1 rules unchanged.

Run `python3 tools/engine.py doctor scripts/batch-NN.json` to print this rubric plus every draft with its card timings. Then, for each script:

1. **Score 0-100** for how well it holds a viewer to the end. Be strict: 85+ is rare.

| Points | What earns them |
|---|---|
| 25 | **Hook in the first 2 seconds.** Card 1 is on screen at frame 0 and names a specific person, scene or contradiction. Not a generic truth. Under 12 words. |
| 15 | **Curiosity gap.** The hook opens a question the viewer can't answer yet. The payoff is not given away before the second-last card. |
| 10 | **Card 2 part-pays by second 3** (strategy/16-lessons). Viewers drop between seconds 3 and 6. |
| 10 | **Pattern change at 5-10 s** (hook-system rule 6): a quiz card, an Ember label, a number, or a reveal. |
| 15 | **Specificity.** One concrete detail: a place, an object, a sentence people actually say. Nothing that could sit on any other Stoic page. |
| 10 | **Payoff in the hook's own words** (rule 7), so the loop back to card 1 reads as a sentence. |
| 15 | **Accuracy risk (M).** Quote word for word in a public-domain translation with book and section; empirical vs philosophical vs opinion labelled; no invented study, number or quote. Any doubt here costs all 15. |

2. **Vetoes (M)**, each caps the score at 50: red-pill or gendered framing; a quote that isn't verified; a CTA that begs ("like and follow", "comment below"); hurt as the only angle when the week's mix needs appreciation or curiosity (hook-system "Angle mix").

3. **Issues:** at most 5, short sentences, most important first.

4. **Rewrite** if the score is under 70. Don't just reword: if the payoff comes early, move it to the end; if a line is vague, make it concrete; if a claim may not be true, cut it; if the hook is weak, make frame 0 a specific, high-stakes scene. Keep the subject, format, source and roughly the same length. Re-score the rewrite.

5. **Store** the final result on the script, then run `engine.py check` (it fails any beat script scored under 70):

```json
"doctor": {"score": 78, "issues": ["Card 3 repeats card 2", "..."], "rewritten": true, "by": "Claude, 30 Oct 2026"}
```

## Beat grammar, for reference (engine 1.3, `"grammar": "beat"`)

HOOK (frame 0, fully composed) → SETUP (card 2 part-pays) → optional **QUIZ** (`"quiz"`, 2-3.5 s, a question the viewer answers in their head, a draining Ember timer) → **REVEAL** (`"reveal"`, 2-4 steps separated by `\n`, each appearing in turn) → PAYOFF in the hook's words → CTA (Phase 1 rule: "Send this to…" or "Answer below") → LOOP (the hook fades back in; the last frame is frame 0). Beat grammar adapted from Hasan Aboul Hasan's claude-faceless-shorts-creator (MIT).
