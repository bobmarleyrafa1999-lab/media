# Faceless toolchain

The formal, dated check of MoviePy, Whisper and Remotion lives in the 90-day plan (`strategy/22-90-day-plan/plan.md`, section 6, PR #17). Its verdict: install nothing new.

What that means for the Mino formats:
- **All six formulas render on the current engine** (`reels-engine/tools/engine.py`, ffmpeg + Pillow). The five mino-01 reels already did, at €0.
- **F4 split screen** uses the engine's fallback (the two labelled cards in sequence) rather than Remotion.
- **Whisper** is not needed here: these reels are scripted, so captions already exist. Transcribing Mino's own videos would only be possible from the owner's Mac.
