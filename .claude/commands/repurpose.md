---
description: Build the cross-platform package for an approved or drafted essay (reels, carousel, cards, stories, pins, Notes)
argument-hint: publication/essays/NN-slug.md
---
Build the repurposing package for **$ARGUMENTS**. Follow `publication/CLAUDE.md`; copy the shape of `publication/packages/01.json`.

Produce `publication/packages/NN.json` with: 2 reel scripts in reels-engine schema (formats A–F from `engine-v2/05-reel-formats-A-F.md`; hook ≤12 words; a cite card with a year for any study; quotes only from public-domain translations not already in the engine registry), a 7-slide carousel (cover, 4–5 evidence/idea slides each with a small-caps citation, a practice slide, sign-off pointing to the essay), 5 quote/insight cards, 3 Story concepts (poll, question/slider, link), 5 Pinterest titles ≤100 chars + descriptions, 3 Substack Notes of ~250–300 characters, the A/B headline, and visuals/type/music (Slate/Graphite/Charcoal/Bone/Ash/Ember, Playfair + Inter, ambient mood or `audio/library/originals` ID).

Then run `python3 publication/scripts/render_packages.py` and `python3 <reels-engine>/tools/engine.py check publication/packages/reels-batch.json`; fix every FAIL. Render only if asked. Everything goes to the approval queue; nothing is scheduled.
