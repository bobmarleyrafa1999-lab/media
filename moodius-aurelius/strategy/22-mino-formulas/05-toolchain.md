# Faceless toolchain: one line each (the 90-day-plan thread owns the full repo audit)

- **Current renderer (keep):** `reels-engine/tools/engine.py` already drives ffmpeg + Pillow directly; all five mino-01 reels rendered with it at €0.
- **MoviePy (Zulko/moviepy, MIT): skip.** It is a Python wrapper over ffmpeg that does what our engine already does, only slower; no gap it fills for these formats.
- **Whisper (openai/whisper, MIT): optional, Mac only.** Useful to transcribe Mino's two method videos ("the only 2 hooks…", "master storyteller") if wanted; it can't run usefully from GitHub Actions because YouTube asks for sign-in there. Our own reels are scripted, so we don't need it for captions.
- **Remotion (remotion-dev/remotion; prototyped 21 Oct in `reels-engine/remotion/`): switch on only for F4 split screens and word-by-word captions over b-roll.** Note its licence needs a paid company licence above 3 people; a one-person business is free. Everything else stays on ffmpeg.
