#!/usr/bin/env python3
"""Render text reels in the Phase 1 design system (flat Slate, Bone type, one Ember accent),
then mix a score.py cue under each.

    python3 reels_v2.py spec.json out_dir

spec.json: {"reel-name": {"style": "elegy", "seed": 17, "segments": [[text, seconds, kind], ...]}}
kind: true = display serif, false = body sans, "quote" = italic serif pull quote, "cite" = caps citation
(plain caps: the old letter-spaced version lost its word spaces in drawtext, fixed 20 Oct 2026). Left-aligned on the 96px margin.
"""
import json, os, subprocess, sys, tempfile
from design import *

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_W = 1080 - 2 * MARGIN


def esc(s):
    return (s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
            .replace("%", "\\%").replace(",", "\\,"))


def wrap(text, font, fs):
    """Greedy wrap; if the last line is a single word, balance the lines instead (no runts)."""
    from PIL import ImageFont
    width = ImageFont.truetype(font, fs).getlength

    def greedy(ln, max_w):
        out, cur = [], ""
        for word in ln.split(" "):
            cand = f"{cur} {word}".strip()
            if cur and width(cand) > max_w:
                out.append(cur)
                cur = word
            else:
                cur = cand
        return out + [cur]

    out = []
    for ln in text.split("\n"):
        lines = greedy(ln, MAX_W)
        if len(lines) > 1 and " " not in lines[-1]:
            lo, hi = MAX_W * 0.5, MAX_W
            for _ in range(14):
                mid = (lo + hi) / 2
                lo, hi = (lo, mid) if len(greedy(ln, mid)) == len(lines) else (mid, hi)
            lines = greedy(ln, hi)
        out += lines
    return out


def render(name, spec, out_dir):
    segs = spec["segments"]
    total = sum(d for _, d, _ in segs) + 0.4
    filt = [f"color=c={hexc(SLATE)}:s=1080x1920:d={total},format=yuv420p[bg]"]
    t = 0.2
    chain = "[bg]"
    i = 0
    for text, d, kind in segs:
        if kind == "cite":
            font, fs, col, text = BODY_M, 34, hexc(ASH), text.upper()
        elif kind == "quote":
            font, fs, col = QUOTE, 64, hexc(BONE)
        elif kind:
            font, fs, col = DISPLAY, 82, hexc(BONE)
        else:
            font, fs, col = BODY_M, 58, hexc(BONE)
        lines = wrap(text, font, fs)
        lh = fs * 1.28
        y0 = 880 - lh * len(lines) / 2
        a = (f"if(lt(t-{t:.2f},0.3),(t-{t:.2f})/0.3,"
             f"if(gt(t-{t:.2f},{d-0.3:.2f}),({t+d:.2f}-t)/0.3,1))")
        for j, ln in enumerate(lines):
            nxt = f"[v{i}]"
            filt.append(f"{chain}drawtext=fontfile={font}:text='{esc(ln)}':fontsize={fs}:fontcolor={col}:"
                        f"x={MARGIN}:y={y0 + j * lh:.0f}:alpha='{a}':enable='between(t,{t:.2f},{t + d:.2f})'{nxt}")
            chain = nxt
            i += 1
        t += d
    filt.append(f"{chain}drawbox=x={MARGIN}:y={MARGIN + 196}:w=14:h=14:color={hexc(EMBER)}:t=fill,"
                f"drawtext=fontfile={BODY_SB}:text='M O O D I U S':fontsize=28:fontcolor={hexc(BONE)}:x={MARGIN + 30}:y={MARGIN + 190},"
                f"drawtext=fontfile={BODY}:text='{HANDLE}':fontsize=32:fontcolor={hexc(ASH)}:x={MARGIN}:y=1560[vout]")
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "cue.wav")
        subprocess.run([sys.executable, os.path.join(HERE, "score.py"), spec["style"], f"{total:.2f}",
                        str(spec["seed"]), wav], check=True, capture_output=True)
        out = os.path.join(out_dir, f"{name}.mp4")
        filt.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-filter_complex", ";".join(filt),
               "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}",
               "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(name, spec["style"], round(total, 1), "ok" if r.returncode == 0 else r.stderr[-600:])


if __name__ == "__main__":
    spec_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    with open(spec_path) as f:
        spec = json.load(f)
    for name, s in spec.items():
        render(name, s, out_dir)
