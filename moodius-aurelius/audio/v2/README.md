# Reel audio v2 (25 Oct 2026)

Surafel: "the audio on my reels is shocking… I want them better, professional."

## What was wrong (measured, not guessed)

Every reel published so far (R001-R007) and every reel scheduled 27 Oct-7 Nov (RB01-RB03) got its
music from `reels-engine/tools/ambient.py`. That script makes sound out of pure sine waves in NumPy.
The more polished `audio/tools/compose.py` + `mix.py` library was never actually used for posts.

| Check | R001 (published) | RB01 (scheduled) | What it means |
|---|---|---|---|
| Loudness | -13.6 LUFS, peak -2.5 dBFS | -14.1 LUFS, peak -3.4 | Fine. Loudness was never the problem. |
| Clipping | none | none | Fine. |
| Where the energy sits | 75% in 250 Hz-2 kHz, 25% below | 99% in 250 Hz-2 kHz | One narrow hum band, no top, no attack. |
| Above 2 kHz | 0.1% | 1.2% | Nothing for a phone speaker to articulate. |
| Note onsets | 1.5 per 10 s | 2.8 per 10 s | A held drone with a few beeps: nothing moves. |
| Short-term level spread | 4.0 dB | 3.3 dB | Flat, static; sounds like a fridge, not music. |
| Stereo correlation | 0.36 | 0.31 | Wide and phasey from detuned sines; thins out on one speaker. |

In plain words: the bed is a sine-wave organ chord with test-tone "piano" notes on top. Pure sines
have no hammer, no felt, no bow noise and no room, so the ear hears it as a synth demo, and on a
phone speaker (which plays almost nothing under ~200 Hz) it collapses into a hum. Mastering cannot
fix that: `samples/R001-mastering-only.mp3` is the old audio through the new EQ and loudness chain,
and it is still a hum.

## The fix (built, £0, owned outright, no credit needed)

`reels-engine/tools/sampled.py` composes the same six moods note by note, then plays them on real
recorded instruments through FluidSynth and the MuseScore General soundfont:
- Mellow Grand Piano: recorded, public domain (Splendid Grand, AKAI S5000).
- String sections (strings, violins, celli, basses): Versilian VSCO 2 Community Edition, CC0.
- The soundfont as a whole is MIT. Music rendered with it is ours; nothing goes in the caption.

What changed musically: real chord progressions (one chord per bar), pedalled broken chords,
strings that breathe with expression, the low octave entering on the reel's turn card
(quote / reveal), and the D-A-F motif under the CTA. Mastering: hall reverb by convolution,
high-pass 55 Hz, -3 dB below 120 Hz, -2 dB at 300 Hz, +2.5 dB at 3 kHz, +2 dB from 8 kHz,
2:1 glue compression, a -62 dBFS room floor, two-pass linear loudness to -14 LUFS / -1.5 dBTP.

`engine.py` now uses it automatically for every mood script when the soundfont is installed
(`sudo apt install fluidsynth musescore-general-soundfont-lossless`), skips the old single-pass
loudnorm for these beds (they arrive mastered), and falls back to the sine version with a warning.
`"audio": {"engine": "ambient-legacy"}` forces the old sound. Engine tests pass (9/9).

Nothing already scheduled has been swapped. Re-rendering is cached by script, so old renders
only change with `--force` and only after Surafel says yes.

## Samples
`samples/` (MP3, listen on headphones and on the phone speaker):
- R001-before / R001-mastering-only / R001-after
- RB01-before / RB01-after, RB02-before / RB02-after
- mood-night, dawn, warm, low, dry, room (20 s each)

`videos/` has the three re-rendered reels with the new audio (same picture).

## The other routes, honestly
- **Recorded library tracks (Scott Buckley, Chris Zabriskie, Musopen)**: produced by real composers,
  so the best ones beat anything generated. CC BY 4.0 needs the credit line in the caption (mix.py
  adds it). Risk: some CC tracks have been registered with rights systems by third parties, and a
  Meta Rights Manager match can mute a reel even when the licence is valid; Kevin MacLeod's are
  the most often hit. The container can't reach music sites, so they have to be downloaded on his
  Mac (15 min, steps in `../README.md`), or by a GitHub Actions job once he OKs it.
- **Instagram's own trending audio**: only possible when he posts by hand in the app. Metricool's
  API uploads the file's own audio and cannot attach an Instagram library sound. If the account is
  set to Business, the in-app library is limited to Meta's commercial-cleared collection; Creator
  accounts see more.
- **AI music services (Suno, Udio, etc.)**: paid for commercial use and murky on rights. Not used.

## Loudness norm
Meta publishes no official loudness target for reels. -14 LUFS integrated with peaks under
-1 dBTP is the common working standard across social platforms, and every new bed hits it.

The `engine.py` change lives on the reels-engine branch; `engine-sampled.patch` here is the exact diff (already applied to the project-files copy).
