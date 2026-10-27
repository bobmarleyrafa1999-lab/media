#!/usr/bin/env python3
"""Moodius beds played on real recorded instruments (the replacement for ambient.py's sine tones).

    python3 sampled.py <mood> <dur> <seed> <out.wav> [--turn SECONDS]

Same moods and arguments as ambient.py, so engine.py can swap one for the other. The music is
still composed here, note by note (so it is owned outright), but it is played by FluidSynth on the
MuseScore General soundfont: a recorded public-domain grand piano and the VSCO 2 CE string
sections (CC0), MIT-licensed as a whole. Nothing needs crediting in the caption.

  night  D minor, mellow piano broken chords + slow strings
  dawn   D major add9, rising piano arpeggios, violins high and soft
  warm   E-flat major sevenths, piano + warm strings
  low    C minor, celli and basses carry it, piano only at the turn
  dry    B minor pizzicato + short piano (humour: stays out of the joke's way)
  room   one held G chord on strings, three piano notes

--turn: the statement card's time. A low octave and a strings swell enter there, which is
the moment the idea turns. Without it the turn falls at 40% of the reel.

Mastering (ffmpeg): stereo hall reverb by convolution, high-pass 55 Hz and -3 dB below 120 Hz (phones
can't play it; it only eats loudness), -2 dB at 300 Hz (mud), +2.5 dB at 3 kHz and +2 dB from 8 kHz (so the
piano reads on phone speakers), gentle 2:1 glue compression, a -62 dBFS
room-tone floor, then two-pass linear loudness to -14 LUFS / -1.5 dBTP. Sound starts at t=0 and
the tail fades, so the hook never lands in silence and the loop back to the start is soft.

Needs: fluidsynth and musescore-general-soundfont-lossless (apt), NumPy, FFmpeg.
"""
import argparse, json, os, re, struct, subprocess, sys, tempfile
import numpy as np

SR = 44100
SOUNDFONTS = ["/usr/share/sounds/sf2/MuseScore_General_Full.sf2",
              "/usr/share/sounds/sf3/MuseScore_General.sf3",
              os.path.expanduser("~/.moodius/MuseScore_General.sf3")]
PPQ = 480

# instrument (bank, program) in MuseScore General
PIANO = (8, 0)          # Mellow Grand Piano (recorded, public domain)
STRINGS = (17, 49)      # Strings Slow, expression-controlled (VSCO 2 CE, CC0)
VIOLINS = (21, 49)      # Violins Slow Expr.
CELLI = (41, 49)        # Celli Slow Expr.
BASSES = (51, 49)       # Basses Slow Expr.
PIZZ = (0, 45)          # Strings Pizzicato

# chords are semitone offsets from the key root; one chord per bar
MOODS = {
    #       root bpm  progression                                                      piano   strings  extra
    "night": (50, 64, [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]],               "broken", STRINGS, CELLI),
    "dawn":  (50, 72, [[0, 4, 7, 14], [-3, 0, 4, 11], [-5, -1, 2, 9], [0, 4, 7, 14]], "rising", VIOLINS, STRINGS),
    "warm":  (51, 66, [[0, 4, 7, 11], [5, 9, 12, 16], [-3, 0, 4, 7], [-5, 0, 2, 7]],  "broken", STRINGS, CELLI),
    "low":   (48, 56, [[0, 3, 7], [-4, 0, 3], [-7, -4, 0], [0, 3, 7]],               "turn",   CELLI,   BASSES),
    "dry":   (47, 84, [[0, 3, 7], [5, 8, 12], [-2, 2, 5], [3, 7, 10]],               "short",  PIZZ,    None),
    "room":  (43, 50, [[0, 7, 14, 16]],                                               "sparse", STRINGS, None),
}
MOTIF = [0, 7, 3]       # root, fifth, minor third above: the Moodius three-note figure


# ---------------------------------------------------------------- MIDI writing (no dependencies)
def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def write_midi(path, events, bpm):
    """events: (time_s, bytes) on any channel. One track, tempo fixed."""
    tick = lambda s: int(round(s * bpm / 60 * PPQ))
    tempo = int(60_000_000 / bpm)
    body, last = bytearray(b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big")), 0
    for t, msg in sorted(events, key=lambda e: (e[0], e[1][0] & 0xF0 != 0x80)):   # note-offs first
        k = max(tick(t), last)
        body += vlq(k - last) + msg
        last = k
    body += b"\x00\xff\x2f\x00"
    with open(path, "wb") as fh:
        fh.write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ) + b"MTrk" + struct.pack(">I", len(body)) + body)


class Score:
    def __init__(self):
        self.ev = []

    def program(self, ch, inst):
        bank, prog = inst
        self.ev += [(0, bytes([0xB0 | ch, 0, bank])), (0, bytes([0xC0 | ch, prog]))]

    def cc(self, ch, t, num, val):
        self.ev.append((max(0, t), bytes([0xB0 | ch, num, int(np.clip(val, 0, 127))])))

    def note(self, ch, t, dur, pitch, vel):
        pitch, vel = int(pitch), int(np.clip(vel, 1, 127))
        self.ev += [(max(0, t), bytes([0x90 | ch, pitch, vel])), (max(0, t + dur), bytes([0x80 | ch, pitch, 0]))]

    def swell(self, ch, t0, t1, lo, hi, steps=24):
        """Expression (CC11) up and back down across [t0, t1]: strings breathe in, not swell out."""
        for i in range(steps + 1):
            x = i / steps
            self.cc(ch, t0 + (t1 - t0) * x, 11, lo + (hi - lo) * np.sin(np.pi * x) ** 1.5)


# ---------------------------------------------------------------- composition
def compose(mood, dur, seed, turn):
    root, bpm, prog, piano, pad, extra = MOODS[mood]
    rng = np.random.default_rng(seed)
    root += int(rng.integers(-1, 2))                       # small key shift per seed so beds don't repeat
    k = int(rng.integers(len(prog)))
    prog = prog[k:] + prog[:k]
    beat = 60 / bpm
    bar = 4 * beat
    nbars = int(np.ceil(dur / bar)) + 1
    jit = lambda: rng.normal(0, 0.012)                    # human timing
    sc = Score()
    sc.program(0, PIANO)
    sc.program(1, pad)
    if extra:
        sc.program(2, extra)
    for ch in (0, 1, 2):
        sc.cc(ch, 0, 91, 0)                               # reverb is added in mastering
        sc.cc(ch, 0, 93, 0)
        sc.cc(ch, 0, 7, 100)
    sc.cc(1, 0, 1, 50)
    motif_at = max(0.0, dur - bar * 1.6)                  # the motif sits under the CTA
    for b in range(nbars):
        t = b * bar
        if t >= dur:
            break
        ch_ = prog[b % len(prog)]
        bass = root - 12 + ch_[0]
        after_turn = t + bar > turn
        # sustain pedal: lift and re-press just after each chord change
        sc.cc(0, t - 0.03, 64, 0)
        sc.cc(0, t + 0.05, 64, 100)
        if piano == "broken":
            pat = [bass, root + ch_[1], root + ch_[2], root + 12 + ch_[0], root + ch_[2], root + ch_[1]]
            for i, p in enumerate(pat):
                if i * beat * 2 / 3 < bar:
                    sc.note(0, t + i * beat * 2 / 3 + jit(), beat * 2, p, rng.integers(34, 52) + (8 if i == 0 else 0))
        elif piano == "rising":
            for i, off in enumerate(ch_ + [ch_[0] + 12, ch_[1] + 12]):
                sc.note(0, t + i * beat / 2 + jit(), beat * 3, root + off, rng.integers(32, 48))
            sc.note(0, t + jit(), bar, bass, 44)
        elif piano == "short":
            for i in range(4):
                sc.note(0, t + i * beat + jit(), beat * 0.35, root + 12 + ch_[i % len(ch_)], rng.integers(30, 44))
        elif piano == "turn":
            if after_turn:
                sc.note(0, t + jit(), bar * 1.5, bass, 48)
                sc.note(0, t + beat * 2 + jit(), bar, root + ch_[2], 36)
        elif piano == "sparse":
            for k in range(3):
                if rng.random() < 0.5:
                    sc.note(0, t + k * beat * 1.3 + rng.uniform(0, beat), beat * 4, root + 24 + ch_[k % len(ch_)], rng.integers(28, 42))
        # melody: a few chord tones in the right hand, more after the turn; never during the CTA motif
        if piano in ("broken", "rising", "sparse") and t < motif_at and rng.random() < (0.75 if after_turn else 0.35):
            top = root + 24 + ch_[int(rng.integers(len(ch_)))]
            sc.note(0, t + beat * rng.choice([1, 2, 2.5]) + jit(), beat * 2.5, top, rng.integers(40, 54))
        # strings pad: whole chord held, breathing with expression
        lo, hi = (40, 72) if after_turn else (28, 52)
        pad_notes = [root + c for c in ch_] if pad != PIZZ else []
        if pad == PIZZ:
            for i in range(0, 4, 2):
                sc.note(1, t + i * beat + jit(), beat, root + ch_[i // 2 % len(ch_)], rng.integers(40, 60))
        else:
            for p in pad_notes:
                sc.note(1, t + 0.02, bar + 0.25, p + (12 if pad == VIOLINS else 0), 70)
            sc.swell(1, t, t + bar, lo, hi)
        # the turn: low octave enters and stays
        if extra and after_turn:
            sc.note(2, max(t, turn) + 0.02, bar + 0.25 - max(0, turn - t), bass, 72)
            sc.swell(2, max(t, turn), t + bar, 34, 80)
    # the motif (D-A-F shape) on piano under the CTA
    for i, off in enumerate(MOTIF):
        sc.note(0, motif_at + i * beat * 0.9, beat * 3, root + 24 + off, 50 - i * 4)
    # everything off at the end
    for ch in (0, 1, 2):
        sc.cc(ch, dur + 2, 64, 0)
        sc.cc(ch, dur + 2, 123, 0)
    return sc, bpm


# ---------------------------------------------------------------- render + master
def soundfont():
    for p in SOUNDFONTS:
        if os.path.exists(p):
            return p
    return None


def impulse(path, secs=2.6, seed=7):
    """Stereo hall impulse: 18 ms pre-delay, exponential decay, darker as it decays."""
    rng = np.random.default_rng(seed)
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((2, n)) * np.exp(-t / (secs / 6.9))
    spec = np.fft.rfft(ir, axis=-1)
    f = np.fft.rfftfreq(n, 1 / SR)
    spec /= np.sqrt(1 + (f / 4500) ** 2)
    ir = np.fft.irfft(spec, n=n, axis=-1)
    ir = np.concatenate([np.zeros((2, int(0.018 * SR))), ir], axis=1)
    ir /= np.abs(ir).max()
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((ir.T * 32000).astype(np.int16).tobytes())


MASTER = ("highpass=f=55,lowshelf=f=120:g=-3,equalizer=f=300:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1:g=2.5,"
          "highshelf=f=8000:g=2,"
          "acompressor=threshold=-24dB:ratio=2:attack=30:release=400:makeup=2")


def loudnorm(src, dst, extra_filter="", target=-14.0):
    """Two-pass linear loudness normalisation (no pumping on quiet material)."""
    pre = (extra_filter + "," if extra_filter else "")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-af",
                        pre + f"loudnorm=I={target}:TP=-1.5:LRA=20:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S).group(0))
    lf = (f"loudnorm=I={target}:TP=-1.5:LRA=20:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", pre + lf + ",aresample=44100",
                    "-c:a", "pcm_s16le", dst], check=True)


def render(mood, dur, seed, out, turn=None):
    sf = soundfont()
    if not sf:
        sys.exit("sampled.py: no soundfont. Install with: sudo apt install fluidsynth musescore-general-soundfont-lossless")
    turn = dur * 0.4 if turn is None else turn
    sc, bpm = compose(mood, dur, seed, turn)
    with tempfile.TemporaryDirectory() as tmp:
        mid, dry, ir, wet = (os.path.join(tmp, x) for x in ("s.mid", "dry.wav", "ir.wav", "wet.wav"))
        write_midi(mid, sc.ev, bpm)
        subprocess.run(["fluidsynth", "-ni", "-q", "-R", "0", "-C", "0", "-g", "0.5", "-r", str(SR),
                        "-F", dry, sf, mid], check=True, capture_output=True)
        impulse(ir, seed=seed)
        fade = min(1.8, dur / 4)
        # dry + hall (wet 30%), master chain, room floor, trim to length, fade the tail
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", dry, "-i", ir,
                        "-f", "lavfi", "-i", f"anoisesrc=c=pink:r={SR}:a=0.0012:d={dur + 3:.2f}",
                        "-filter_complex",
                        f"[0:a]aresample={SR},asplit[d][s];[s][1:a]afir[r];"
                        f"[d][r]amix=inputs=2:weights='0.72 0.38':normalize=0[m];"
                        f"[2:a]aformat=channel_layouts=stereo,lowpass=f=6000[n];"
                        f"[m][n]amix=inputs=2:weights='1 1':normalize=0,{MASTER},"
                        f"atrim=0:{dur:.3f},afade=t=out:st={dur - fade:.3f}:d={fade:.3f}",
                        "-c:a", "pcm_s16le", wet], check=True, capture_output=True)
        loudnorm(wet, out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mood", choices=MOODS)
    ap.add_argument("dur", type=float)
    ap.add_argument("seed", type=int)
    ap.add_argument("out")
    ap.add_argument("--turn", type=float)
    a = ap.parse_args()
    render(a.mood, a.dur, a.seed, a.out, a.turn)
