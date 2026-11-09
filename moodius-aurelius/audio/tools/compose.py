#!/usr/bin/env python3
"""Moodius score: original, owned background music in the Moodius sound (no samples, no AI model).

    python3 compose.py track  <category> <variant 1-4> <seconds> <out.wav> [--cue 9.2 --cue 16.0] [--motif-at 21]
    python3 compose.py library [--seconds 48]          # renders the 28 library originals to ../library/originals/
    python3 compose.py sting  <out.wav>                # the 2.4 s sound logo (D, A, F on felt piano)

Instruments are synthesised from scratch (felt piano, bowed low strings, tine piano, glass, sub,
room tone, tape hiss) and placed in one synthetic room, so every track shares a sonic signature.
`--cue` times are where the harmony moves and a new voice enters: the mixer passes the reel's
statement cards here, so the music turns exactly when the idea turns. Deterministic per seed.
Needs NumPy + SciPy (pip install scipy).
"""
import argparse, json, os, sys, wave
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(os.path.dirname(HERE), "library", "originals")
NOTES = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}

# chord = semitone offsets from the key root; progressions are lists of (root offset, chord tones)
m7, M7, m9, M9, sus2, m, add9 = [0, 3, 7, 10], [0, 4, 7, 11], [0, 3, 7, 10, 14], [0, 4, 7, 11, 14], [0, 2, 7], [0, 3, 7], [0, 4, 7, 14]
PRESETS = {
    # category: key, octave of root, bpm, voices, brightness 0-1, density (piano notes per beat), reverb s, progressions
    "stoicism": dict(key="D", bpm=64, voices=["piano", "strings", "room"], bright=.45, density=.5, verb=2.6,
                     progs=[[(0, m), (-4, M7), (-7, M7), (-2, sus2)], [(0, m7), (5, m7), (3, M7), (-2, add9)],
                            [(0, sus2), (-2, M7), (-4, M7), (-5, m7)], [(0, m), (3, M7), (-2, add9), (-7, sus2)]]),
    "psychology": dict(key="A", bpm=72, voices=["piano", "glass", "room"], bright=.6, density=.6, verb=2.2,
                       progs=[[(0, m9), (-4, M9), (-9, M7), (-2, add9)], [(0, m7), (3, M9), (8, M7), (5, m9)],
                              [(-4, M9), (0, m9), (-2, add9), (-7, M7)], [(0, sus2), (5, m7), (-4, M9), (-2, sus2)]]),
    "masculinity": dict(key="C", bpm=58, voices=["strings", "sub", "piano_low", "room"], bright=.3, density=.3, verb=3.0,
                        progs=[[(0, m), (-4, M7), (-2, sus2), (-5, m)], [(0, m7), (-5, m7), (-4, M7), (-2, add9)],
                               [(0, sus2), (3, M7), (-2, sus2), (0, m)], [(0, m), (5, m7), (-4, M7), (-7, sus2)]]),
    "existentialism": dict(key="Bb", bpm=52, voices=["drone", "piano_far", "glass", "room"], bright=.35, density=.25, verb=4.2,
                           progs=[[(0, sus2), (2, sus2), (-2, M7), (0, m)], [(0, m), (1, M7), (0, sus2), (-2, add9)],
                                  [(0, m9), (-3, M9), (-5, sus2), (0, sus2)], [(0, sus2), (6, sus2), (0, m), (-1, M7)]]),
    "relationships": dict(key="Eb", bpm=66, voices=["piano", "pad", "room"], bright=.55, density=.55, verb=2.4,
                          progs=[[(0, M9), (-3, m9), (5, M7), (-5, add9)], [(0, add9), (-5, M7), (-3, m7), (5, M9)],
                                 [(5, M7), (0, add9), (-3, m9), (-5, sus2)], [(0, M7), (2, m7), (-3, m9), (5, add9)]]),
    "discipline": dict(key="G", bpm=76, voices=["pulse", "strings", "piano", "room"], bright=.5, density=.45, verb=2.0,
                       progs=[[(0, m), (-4, M7), (-7, M7), (-2, sus2)], [(0, m7), (-2, add9), (3, M7), (-5, m7)],
                              [(0, sus2), (-4, M7), (-2, add9), (-7, sus2)], [(0, m), (3, M7), (5, m7), (-2, sus2)]]),
    "refined": dict(key="Db", bpm=80, voices=["tine", "pad", "brush", "room"], bright=.6, density=.55, verb=1.8,
                    progs=[[(0, M9), (-3, m9), (2, m9), (-5, add9)], [(0, M7), (5, M9), (-3, m9), (-5, M7)],
                           [(2, m9), (-5, add9), (0, M9), (-3, m7)], [(0, M9), (-2, M7), (-4, M9), (-5, add9)]]),
}
MOOD = {"stoicism": "steady, austere", "psychology": "curious, glassy", "masculinity": "low, warm, heavy",
        "existentialism": "vast, unresolved", "relationships": "tender, warm", "discipline": "quietly driving",
        "refined": "unhurried, luxe"}
ENERGY = {"stoicism": 2, "psychology": 2, "masculinity": 2, "existentialism": 1, "relationships": 2, "discipline": 3, "refined": 2}


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR / 2 - 100) / (SR / 2), "low", output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc / (SR / 2), "high", output="sos"), x)


def pink(n, rng):
    w = rng.standard_normal(n)
    f = np.fft.rfft(w)
    f /= np.sqrt(np.maximum(np.arange(len(f)), 1))
    p = np.fft.irfft(f, n)
    return p / (np.abs(p).max() + 1e-9)


# ---------- instruments (mono, return array of length n) ----------
def felt_piano(f, dur, vel, bright, rng):
    n = int(SR * (dur + 2.5))
    t = np.arange(n) / SR
    out = np.zeros(n)
    B = 0.00018                                  # string inharmonicity
    for k in range(1, 13):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 9000:
            break
        amp = vel / k ** (1.35 - 0.5 * bright)
        decay = (1.6 + 2.5 * (f < 200)) / (1 + 0.35 * (k - 1)) * (0.7 + 0.6 * (f < 400))
        out += amp * np.exp(-t / decay) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    att = np.minimum(1, t / 0.006)
    rel = np.where(t > dur, np.exp(-(t - dur) / 0.35), 1)       # damper
    hammer = lp(rng.standard_normal(n) * np.exp(-t / 0.012), 1800) * 0.08 * vel
    return lp((out * att * rel + hammer), 1400 + 3200 * bright * vel)


def tine(f, dur, vel, bright, rng):                 # electric-piano-like FM tine
    n = int(SR * (dur + 2.0))
    t = np.arange(n) / SR
    idx = 1.6 * vel * np.exp(-t / 0.25)
    mod = idx * np.sin(2 * np.pi * f * t)
    body = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 2.2)
    bell = 0.12 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.08)
    env = np.minimum(1, t / 0.004) * np.where(t > dur, np.exp(-(t - dur) / 0.5), 1)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.2 * t)
    return lp(vel * (body + bell) * env * trem, 3000 + 2500 * bright)


def glass(f, dur, vel, bright, rng):
    n = int(SR * (dur + 3.0))
    t = np.arange(n) / SR
    tone = sum(a * np.sin(2 * np.pi * f * r * t) for r, a in ((1, 1), (2.76, .35), (5.4, .12)))
    return 0.35 * vel * tone * np.exp(-t / 2.8) * np.minimum(1, t / 0.003)


def bowed(f, dur, vel, bright, rng, attack=1.4):
    n = int(SR * (dur + 1.5))
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-0.06, 0.0, 0.07):                # three players
        vib = 1 + 0.0035 * np.sin(2 * np.pi * (4.8 + det) * t + rng.uniform(0, 6))
        ph = 2 * np.pi * np.cumsum(f * (1 + det / 100) * vib) / SR
        out += sum(np.sin(k * ph) / k for k in range(1, 10) if f * k < 6000)
    env = np.minimum(1, t / attack) * np.where(t > dur, np.exp(-(t - dur) / 0.9), 1)
    bow = 1 + 0.15 * lp(rng.standard_normal(n), 3)     # bow pressure drift
    return lp(out * env * bow * vel * 0.18, 700 + 900 * bright)


def pad(f, dur, vel, bright, rng):
    n = int(SR * (dur + 2.5))
    t = np.arange(n) / SR
    out = sum(np.sin(2 * np.pi * f * (1 + d) * t * k) / k for d in (-.004, 0, .005) for k in (1, 2, 3))
    env = np.minimum(1, t / 2.2) * np.where(t > dur, np.exp(-(t - dur) / 1.6), 1)
    return lp(out * env * vel * 0.12, 900 + 1200 * bright)


def sub(f, dur, vel, bright, rng):
    n = int(SR * (dur + 1.5))
    t = np.arange(n) / SR
    env = np.minimum(1, t / 1.5) * np.where(t > dur, np.exp(-(t - dur) / 1.0), 1)
    return np.sin(2 * np.pi * f * t) * env * vel * 0.5


# ---------- room ----------
def impulse(seconds, rng, bright):
    n = int(SR * seconds)
    t = np.arange(n) / SR
    ir = []
    for _ in range(2):
        x = rng.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        x = lp(x, 2600 + 2600 * bright)
        x[:int(SR * 0.012)] *= np.linspace(0, 1, int(SR * 0.012))   # pre-delay feel
        ir.append(x / np.sqrt((x ** 2).sum()))
    return ir


def place(buf, sig, start, pan):
    i = int(start * SR)
    j = min(len(buf[0]), i + len(sig))
    if i >= len(buf[0]):
        return
    l, r = np.cos(pan * np.pi / 2), np.sin(pan * np.pi / 2)
    buf[0][i:j] += sig[:j - i] * l
    buf[1][i:j] += sig[:j - i] * r


# ---------- composition ----------
def compose(category, variant, seconds, cues=(), motif_at=None, seed=None):
    P = PRESETS[category]
    rng = np.random.default_rng(seed if seed is not None else hash((category, variant)) % 2 ** 32)
    root = NOTES[P["key"]] + 48
    beat = 60 / P["bpm"]
    prog = P["progs"][(variant - 1) % 4]
    n = int(SR * (seconds + 4))
    dry = {k: [np.zeros(n), np.zeros(n)] for k in ("near", "far")}
    bright = P["bright"]
    # chord boundaries: every 8 beats, plus every cue (a cue forces a change and an entry)
    bounds = list(np.arange(0, seconds, 8 * beat))
    for c in cues:
        bounds = [b for b in bounds if abs(b - c) > 2.5 * beat] + [c]
    bounds = sorted(set([0.0] + [b for b in bounds if 0 < b < seconds - 1.5])) + [seconds]
    first_cue = min(cues) if cues else bounds[min(2, len(bounds) - 2)]
    v = set(P["voices"])
    for ci in range(len(bounds) - 1):
        a, b = bounds[ci], bounds[ci + 1]
        off, tones = prog[ci % len(prog)]
        chord = [root + off + x for x in tones]
        lifted = a >= first_cue - 0.01
        # sustained voices
        if "strings" in v or "drone" in v:
            for i, m_ in enumerate([chord[0] - 12, chord[1] if len(chord) > 1 else chord[0], chord[2] if len(chord) > 2 else chord[0]]):
                if i > 0 and not lifted and "drone" not in v:
                    continue
                place(dry["near"], bowed(hz(m_), b - a + 0.6, 0.9 if i == 0 else 0.55, bright, rng,
                                          attack=2.5 if "drone" in v else 1.4), a, 0.35 + 0.15 * i)
        if "pad" in v:
            for i, m_ in enumerate(chord[:4]):
                place(dry["far"], pad(hz(m_ + 12), b - a + 0.5, 0.6, bright, rng), a, 0.25 + 0.17 * i)
        if "sub" in v or "drone" in v:
            place(dry["near"], sub(hz(chord[0] - 12), b - a + 0.5, 0.7, bright, rng), a, 0.5)
        # melodic voice
        lead = ("piano" if "piano" in v else "piano_low" if "piano_low" in v else "piano_far" if "piano_far" in v
                else "tine" if "tine" in v else None)
        if lead:
            reg = {"piano": 12, "piano_low": 0, "piano_far": 12, "tine": 12}[lead]
            dens = P["density"] * (1.5 if lifted else 0.7)
            t = a + (0 if ci else beat * 2)              # the first chord breathes before the piano speaks
            while t < b - beat * 0.5:
                if rng.random() < dens:
                    m_ = int(rng.choice(chord)) + reg + (12 if rng.random() < .25 else 0)
                    vel = float(rng.uniform(.45, .8)) * (1.1 if abs(t - a) < .05 else 1)
                    inst = tine if lead == "tine" else felt_piano
                    sig = inst(hz(m_), beat * rng.choice([1, 1.5, 2, 3]), vel, bright, rng)
                    place(dry["far" if lead == "piano_far" else "near"], sig * (0.55 if lead == "piano_far" else 1),
                          t + rng.uniform(-.012, .012), 0.42 + rng.uniform(-.15, .15))
                t += beat * rng.choice([1, 1, 2, 0.5]) if lead != "piano_low" else beat * 2
            if lifted and abs(a - first_cue) < .01:      # the turn: a low octave under the new chord
                place(dry["near"], felt_piano(hz(chord[0] + reg - 12), beat * 4, .7, bright, rng), a, .45)
        if "glass" in v and lifted and rng.random() < .8:
            place(dry["far"], glass(hz(chord[-1] + 24), beat * 2, .5, bright, rng), a + beat * rng.integers(1, 4), .7)
        if "pulse" in v:                                 # muted piano heartbeat, enters at the first cue
            t = a
            while t < b:
                if lifted or rng.random() < .3:
                    place(dry["near"], lp(felt_piano(hz(chord[0]), beat * .3, .35, 0, rng), 600), t, .5)
                t += beat
        if "brush" in v:
            t = a
            while t < b:
                nn = int(SR * .25)
                hit = hp(rng.standard_normal(nn), 4000) * np.exp(-np.arange(nn) / SR / .05) * .035
                place(dry["near"], hit, t + beat * .5, .65)
                t += beat
    if motif_at is not None:                             # the Moodius motif: root, fifth, minor third above
        for i, iv in enumerate((0, 7, 15)):
            place(dry["near"], felt_piano(hz(root + 12 + iv), beat * 3, .55, bright, rng), motif_at + i * beat * .75, .5)
    # room: near voices get a short send, far voices a long one
    irs = impulse(P["verb"], rng, bright)
    out = []
    for ch in range(2):
        near, far = dry["near"][ch], dry["far"][ch]
        wet = fftconvolve(near * .45 + far, irs[ch])[:n]
        out.append(near * .8 + far * .35 + wet * .9)
    out = np.array(out)
    # texture: room tone and tape hiss, constant (the Moodius floor)
    out += np.array([lp(pink(n, rng), 1200) * .004, lp(pink(n, rng), 1200) * .004])
    out += np.array([hp(rng.standard_normal(n), 6000) * .0012 for _ in range(2)])
    out = out[:, :int(SR * seconds)]
    out = hp(out, 32)
    out = np.tanh(out / (np.abs(out).max() + 1e-9) * 1.3) / np.tanh(1.3)      # gentle tape saturation
    fade_in, fade_out = int(SR * .12), int(SR * min(3.0, seconds * .12))
    out[:, :fade_in] *= np.linspace(0, 1, fade_in)
    out[:, -fade_out:] *= np.linspace(1, 0, fade_out) ** 1.5
    return out * 0.7


def write(path, st):
    st = np.clip(st, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st.T * 32767).astype("<i2").tobytes())


def main():
    ap = argparse.ArgumentParser()
    sub_ = ap.add_subparsers(dest="cmd", required=True)
    t = sub_.add_parser("track"); t.add_argument("category", choices=PRESETS); t.add_argument("variant", type=int)
    t.add_argument("seconds", type=float); t.add_argument("out"); t.add_argument("--cue", type=float, action="append", default=[])
    t.add_argument("--motif-at", type=float); t.add_argument("--seed", type=int)
    l = sub_.add_parser("library"); l.add_argument("--seconds", type=float, default=48); l.add_argument("--only")
    s = sub_.add_parser("sting"); s.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "track":
        write(a.out, compose(a.category, a.variant, a.seconds, a.cue, a.motif_at, a.seed))
    elif a.cmd == "sting":
        write(a.out, compose("stoicism", 1, 3.2, motif_at=0.15, seed=7) * 0 + compose_sting())
    else:
        os.makedirs(LIB, exist_ok=True)
        meta = []
        for cat in PRESETS:
            if a.only and cat not in a.only.split(","):
                continue
            for var in range(1, 5):
                name = f"MO-{cat[:3].upper()}-{var}"
                wav = os.path.join(LIB, name + ".wav")
                beat = 60 / PRESETS[cat]["bpm"]
                cue = round(beat * 16, 2)                 # the default lift: after 16 beats
                write(wav, compose(cat, var, a.seconds, cues=[cue], seed=1000 + 10 * list(PRESETS).index(cat) + var))
                os.system(f'ffmpeg -v error -y -i "{wav}" -af loudnorm=I=-18:TP=-2:LRA=11 -ar 44100 -c:a aac -b:a 256k '
                          f'"{os.path.join(LIB, name + ".m4a")}" && rm "{wav}"')
                meta.append(dict(id=name, category=cat, variant=var, bpm=PRESETS[cat]["bpm"], key=PRESETS[cat]["key"],
                                 mood=MOOD[cat], energy=ENERGY[cat], lift_s=cue, seconds=a.seconds,
                                 voices=" + ".join(PRESETS[cat]["voices"])))
                print(name, flush=True)
        json.dump(meta, open(os.path.join(LIB, "originals.json"), "w"), indent=1)


def compose_sting():
    rng = np.random.default_rng(7)
    n = int(SR * 3.2)
    buf = [np.zeros(n), np.zeros(n)]
    root = NOTES["D"] + 60
    for i, iv in enumerate((0, 7, 15)):
        place(buf, felt_piano(hz(root + iv), .9, .6, .45, rng), .1 + i * .42, .5)
    place(buf, bowed(hz(root - 24), 2.2, .5, .3, rng, attack=.6), .1, .5)
    ir = impulse(2.6, rng, .45)
    out = np.array([np.array(buf[c]) * .8 + fftconvolve(buf[c], ir[c])[:n] * .8 for c in range(2)])
    out = out / (np.abs(out).max() + 1e-9) * .7
    out[:, -int(SR * .8):] *= np.linspace(1, 0, int(SR * .8))
    return out


if __name__ == "__main__":
    main()
