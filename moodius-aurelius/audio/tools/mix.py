#!/usr/bin/env python3
"""Moodius mixer: put a library track under a rendered reel, cut to the picture, at Instagram loudness.

    python3 mix.py <batch.json> <script_id> --video ../../reels-engine/renders/D01-the-bench.mp4
                   [--track MO-EXI-2 | --candidates 3] [--vo voice.wav] [--out ../renders/]

What it does, in order:
  1. Reads the script's cards to find the cut points: the statement (first quote / labelled / study
     card, or the turn after the hook) and the CTA.
  2. Originals (MO-*) are re-composed at the reel's exact length with the harmony turning on the
     statement card and the Moodius motif under the CTA. External tracks are aligned instead: the
     start offset is chosen so the track's biggest rise lands on the statement card and the first
     second is quiet.
  3. Automation: 0.25 s fade-in (the hook never starts in silence), -3 dB dip while a quote is
     on screen (reading room), 1.8 s fade-out.
  4. Voice-over (optional): high-pass, levelled, and the music is ducked under it with a sidechain
     compressor (fast attack, 350 ms release, so it breathes back between phrases).
  5. Two-pass loudness normalisation to -14 LUFS integrated, -1.5 dBTP; the video stream is copied.
  6. Writes <reel>-mix-<track>.mp4, appends the attribution line to the caption file, logs usage.
"""
import argparse, csv, json, os, re, subprocess, sys, tempfile
from datetime import date
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import compose, library  # noqa: E402

SR = 44100


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    return r


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout)


def timeline(script):
    """Card start times (engine.py starts the first card at 0.2 s, or at 0 s for 1.3 beat-grammar scripts)."""
    t, out = (0.0 if script.get("grammar") == "beat" else 0.2), []
    for text, d, kind in script["cards"]:
        out.append((t, d, kind, text))
        t += d
    turn = script.get("audio", {}).get("turn_card")          # optional override: 1-based card index
    statement = out[turn - 1][0] if turn else next((s for s, d, k, _ in out if k in ("quote", "labelled")), None)
    if statement is None:                                   # the card before a study cite, else the turn after the hook
        cites = [i for i, (_, _, k, x) in enumerate(out) if k == "cite" and re.search(r"(19|20)\d\d", x)]
        statement = out[cites[0] - 1][0] if cites else out[min(2, len(out) - 1)][0]
    cta = next((s for s, d, k, _ in out if k == "cta"), out[-1][0])
    reading = [(s, s + d) for s, d, k, _ in out if k == "quote"]
    return round(statement, 2), round(cta, 2), reading


def envelope(path):
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "a.f32")
        run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ac", "1", "-ar", "8000", "-f", "f32le", raw])
        x = np.fromfile(raw, dtype="<f4")
    hop = 400                                               # 50 ms
    e = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "same")[::hop] + 1e-12)
    return 20 * np.log10(e)


def best_offset(path, reel_s, cue):
    e = envelope(path)
    n = len(e) * 0.05
    if n <= reel_s + 1:
        return 0.0
    rise = np.convolve(np.diff(e, prepend=e[0]), np.ones(10), "same")   # ~0.5 s of rising energy
    best, best_s = 0.0, -1e9
    for off in np.arange(0, n - reel_s, 0.25):
        i_cue, i0 = int((off + cue) / 0.05), int(off / 0.05)
        s = rise[max(0, i_cue - 4):i_cue + 4].max() - 0.15 * max(0, e[i0:i0 + 20].mean() - e.mean())
        if s > best_s:
            best, best_s = off, s
    return round(float(best), 2)


def volume_expr(total, reading):
    parts = [f"min(1,t/0.25)", f"min(1,({total:.2f}-t)/1.8)"]
    for a, b in reading:                                     # -3 dB (0.708) with 0.5 s ramps
        parts.append(f"(1-0.292*min(1,max(0,min((t-{a - 0.5:.2f})/0.5,({b + 0.5:.2f}-t)/0.5))))")
    return "*".join(parts)


def measure(path, filt):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-af", filt + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
             "-f", "null", "-"]).stderr
    return json.loads(r[r.rindex("{"):r.rindex("}") + 1])


def mix(batch, sid, video, track_id, vo, out_dir):
    spec = json.load(open(batch, encoding="utf-8"))
    script = next(s for s in spec["scripts"] if s["id"] == sid)
    script.setdefault("grammar", spec.get("grammar"))       # engine 1.3 batch-level grammar
    track = next(t for t in library.load() if t["id"] == track_id)
    if track["status"] != "in_library" or track["commercial_ok"] != "yes":
        sys.exit(f"{track_id} is not usable yet (status {track['status']}, commercial {track['commercial_ok']})")
    total = duration(video)
    statement, cta, reading = timeline(script)
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.splitext(os.path.basename(video))[0] + f"-mix-{track_id}"
    with tempfile.TemporaryDirectory() as tmp:
        music = os.path.join(tmp, "music.wav")
        if track_id.startswith("MO-"):
            cat = track["category"]
            var = int(track_id.rsplit("-", 1)[1])
            seed = 1000 + 10 * list(compose.PRESETS).index(cat) + var
            compose.write(music, compose.compose(cat, var, total, cues=[statement], motif_at=cta + 0.3, seed=seed))
            offset, how = 0.0, f"composed to picture: turn at {statement}s, motif at {cta + 0.3:.1f}s"
        else:
            src = os.path.join(library.LIB, track["file"])
            offset = best_offset(src, total, statement)
            run(["ffmpeg", "-v", "error", "-y", "-ss", str(offset), "-t", f"{total:.2f}", "-i", src, "-ar", str(SR), "-ac", "2", music])
            how = f"aligned: track offset {offset}s puts its biggest rise on the statement card ({statement}s)"
        mus = f"[m]volume='{volume_expr(total, reading)}':eval=frame"
        if vo:
            graph = (f"[1:a]{mus.split(']', 1)[1]}[mv];[2:a]highpass=f=80,acompressor=threshold=0.1:ratio=3:attack=10:release=200,"
                     f"loudnorm=I=-16:TP=-2,asplit[v1][v2];[mv][v2]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[duck];"
                     f"[duck][v1]amix=inputs=2:normalize=0:duration=first")
            inputs = ["-i", video, "-i", music, "-i", vo]
        else:
            graph = f"[1:a]{mus.split(']', 1)[1]}"
            inputs = ["-i", video, "-i", music]
        pre = os.path.join(tmp, "pre.wav")
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph + "[a]", "-map", "[a]", "-ar", str(SR), pre])
        m = measure(pre, "anull")
        ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        out = os.path.join(out_dir, name + ".mp4")
        run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", pre, "-map", "0:v", "-map", "1:a", "-af", ln, "-ar", "48000",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out])
    final = measure(out, "anull")
    cap = os.path.splitext(video)[0] + ".txt"
    credit = track["attribution"] if track["attribution"] != "none needed" else ""
    with open(os.path.join(out_dir, name + ".txt"), "w", encoding="utf-8") as fh:
        body = open(cap, encoding="utf-8").read() if os.path.exists(cap) else ""
        fh.write(body.replace("\n\n---", f"\n\n{credit}\n\n---", 1) if credit else body)
    new = not os.path.exists(library.USAGE)
    with open(library.USAGE, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["date", "reel", "track_id", "offset_s", "statement_s", "lufs", "file"])
        w.writerow([date.today().isoformat(), sid, track_id, offset, statement, final["input_i"], os.path.basename(out)])
    print(f"{name}.mp4  {total:.1f}s  {final['input_i']} LUFS / {final['input_tp']} dBTP  · {how}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch"); ap.add_argument("id"); ap.add_argument("--video", required=True)
    ap.add_argument("--track"); ap.add_argument("--candidates", type=int, default=0)
    ap.add_argument("--vo"); ap.add_argument("--out", default=os.path.join(AUDIO, "renders"))
    a = ap.parse_args()
    if a.track:
        mix(a.batch, a.id, a.video, a.track, a.vo, a.out)
        return
    picks = library.candidates(argparse.Namespace(batch=a.batch, only=a.id, json=None))[a.id]["candidates"]
    for p in [p for p in picks if p["status"] == "in_library"][:max(1, a.candidates)]:
        mix(a.batch, a.id, a.video, p["id"], a.vo, a.out)

if __name__ == "__main__":
    main()
