# Remotion prototype (21 Oct 2026)

A second renderer for engine scripts, built to compare with `tools/engine.py` (FFmpeg).
One React composition (`src/Reel.tsx`) reads any script from `scripts/batch-01.json` format,
so Claude still only writes JSON. Same tokens, fonts, card kinds and timings as the FFmpeg engine.

What it adds over FFmpeg drawtext: word-by-word reveal on hook and quote cards, spring easing,
browser line balancing (`text-wrap: balance`), an Ember rule that draws in, a thin progress line.
Anything CSS can lay out (split screens, lists, captions over footage) becomes possible.

## Run
    npm ci
    python3 ../tools/ambient.py night 21 101 public/R001-bed.wav   # music bed (then loudnorm -14 LUFS)
    # put the script JSON in public/ as R001.json, then:
    npx remotion render src/index.ts Reel out/R001.mp4 --props='{"script":"R001.json"}' \
      --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell --crf=20

## Cost
- Money: free for individuals and companies of up to 3 people (Remotion licence); a company licence is needed above that.
- Compute: R001 took 50 s vs 18 s with FFmpeg in the cloud container; needs Node + Chromium, 455 MB node_modules.
- Claude tokens: same as now. The composition is written once; each reel is still one JSON script.

Comparison: `../renders/R001-side-by-side.mp4`, `../renders/R001-ffmpeg-vs-remotion-frames.png`.
