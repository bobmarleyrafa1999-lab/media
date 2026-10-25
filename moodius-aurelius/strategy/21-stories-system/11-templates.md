# Visual templates

Twelve story layouts, 1080 × 1920, built in code (build/templates.py, Pillow, free) so every story matches. Samples in templates/.

| ID | Name | Use | Background |
|---|---|---|---|
| T01 | Hook | First frame: one tense or curious line + a short second line | Slate |
| T02 | Two perspectives | Dilemma or poll: two cards, A and B | Slate |
| T03 | What psychology says | Claim, plain explanation, source with an Ember bar | Slate |
| T04 | Question box | One question; empty zone for the sticker | Slate |
| T05 | Book | Reading Room: book-spine motif | Bone (paper) |
| T06 | Kindness | Stranger's kindness: three Ember rings | Bone (paper) |
| T07 | Argument against | "My view" card over "Best case against" card | Slate |
| T08 | Quiz / answer | Options A-C; answer version highlights the right one in Ember, others fade | Slate |
| T09 | Slider | Emoji-slider zone; scheduled version draws a 1-10 scale | Slate |
| T10 | Add Yours | Prompt + zone for the Add Yours sticker | Slate |
| T11 | You pick | Friday vote, three options | Slate |
| T12 | Moodius take | Italic serif, Ember quote mark, CTA line | Graphite |

**Grid:** 96 px side margins; masthead (Ember square, MOODIUS, pillar · sequence · page) at the top below Instagram's progress bar; content from 330 px; the bottom 260 px stays clear for the reply bar; handle bottom right.
**Type:** Playfair Display SemiBold for headlines (70-96 px), Playfair Medium Italic for options and takes, Inter for body (42 px), Inter SemiBold caps tracked for kickers (28 px, Ember).
**Colour:** Slate #1B1F24, Graphite #2A2F36, Charcoal #3A4049, Bone #F3EFE7, Ash #B8B3A9, one accent Ember #C9742E. No gradients, statues, gold or stock photos.
**Two versions of every interactive frame:** `_hand` leaves the sticker zone empty (post from the app and drop the sticker there); `_auto` prints the reply prompt in a Graphite panel so it can be scheduled.

To make a new story: add a frame to build/sequences.py (or a concept to build/concepts.py) and run `python3 build/templates.py sequences`.
