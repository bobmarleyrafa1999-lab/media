#!/usr/bin/env python3
"""Render text reels from a JSON spec, then mix a score.py cue under each.

    python3 render_reels.py spec.json out_dir

spec.json: {"reel-name": {"style": "battle", "seed": 17, "segments": [[text, seconds, big], ...]}, ...}
Output: out_dir/<name>.mp4 (1080x1920, 30fps, AAC) with the cue loudness-normalised to -14 LUFS.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SERIF = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
if not os.path.exists(SERIFB):
    SERIFB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def esc(s):
    return (s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
            .replace("%", "\\%").replace(",", "\\,"))


def render(name, spec, out_dir):
    segs = spec["segments"]
    total = sum(d for _, d, _ in segs) + 0.5
    filt = []
    bg = (f"color=c=0x1b1d1f:s=1080x1920:d={total},format=yuv420p,"
          f"noise=alls=28:allf=t,boxblur=6:1,eq=contrast=1.15:brightness=-0.02,"
          f"scale=1240:2204,crop=1080:1920:x='80+60*sin(t/9)':y='140+80*t/{total}',vignette=PI/4[bg]")
    filt.append(bg)
    t = 0.25
    chain = "[bg]"
    i = 0
    for text, d, big in segs:
        lines = text.split("\n")
        fs = 78 if big else 64
        font = SERIFB if big else SERIF
        lh = fs * 1.3
        y0 = 960 - lh * len(lines) / 2
        a = (f"if(lt(t-{t:.2f},0.35),(t-{t:.2f})/0.35,"
             f"if(gt(t-{t:.2f},{d-0.35:.2f}),({t+d:.2f}-t)/0.35,1))")
        for j, ln in enumerate(lines):
            nxt = f"[v{i}]"
            filt.append(f"{chain}drawtext=fontfile={font}:text='{esc(ln)}':fontsize={fs}:fontcolor=0xEDE6D6:"
                        f"x=(w-text_w)/2:y={y0 + j * lh:.0f}:alpha='{a}':enable='between(t,{t:.2f},{t + d:.2f})':"
                        f"shadowcolor=black@0.6:shadowx=2:shadowy=3{nxt}")
            chain = nxt
            i += 1
        t += d
    filt.append(f"{chain}drawtext=fontfile={SERIFB}:text='M · A':fontsize=44:fontcolor=0xC9A86A@0.85:x=(w-text_w)/2:y=230,"
                f"drawbox=x=440:y=300:w=200:h=2:color=0xC9A86A@0.7:t=fill,"
                f"drawtext=fontfile={SANS}:text='@moodiusaurelius':fontsize=38:fontcolor=0xEDE6D6@0.75:x=(w-text_w)/2:y=1640[vout]")
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
