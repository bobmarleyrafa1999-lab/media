#!/usr/bin/env python3
"""Original Gladiator-style cues for @moodiusaurelius reels.

    python3 score.py <style> <dur> <seed> <out.wav>

styles:
  battle  3/4 low-string ostinato, taiko, horn theme, vocal wail
  elegy   harp arpeggios, duduk lead, female vocalise, heartbeat frame drum
  dawn    6/8 harp, solo cello, vocalise, D dorian
  march   slow 4/4 taiko, horn theme, low choir

Rules from the user: no snare, no big ending. Percussion is low taiko/frame
drum only, and every cue fades out instead of resolving on a hit. Sound starts
at t=0 so the hook lands immediately. The seed picks key, tempo and humanising.
"""
import numpy as np, wave, sys
from scipy.signal import butter, sosfilt

SR = 44100
_F = {}


def _sos(kind, fc, o):
    k = (kind, fc if np.isscalar(fc) else tuple(fc), o)
    if k not in _F:
        _F[k] = butter(o, fc, kind, fs=SR, output="sos")
    return _F[k]


def lp(x, fc, o=2): return sosfilt(_sos("low", fc, o), x)
def hp(x, fc, o=2): return sosfilt(_sos("high", fc, o), x)
def bp(x, lo, hi, o=2): return sosfilt(_sos("band", [lo, hi], o), x)
def hz(m): return 440.0 * 2 ** ((np.asarray(m, float) - 69) / 12)


def smooth(x, sec):
    k = max(1, int(sec * SR))
    if k == 1:
        return x
    pad = np.concatenate([np.full(k, x[0]), x, np.full(k, x[-1])])
    return np.convolve(pad, np.ones(k) / k, mode="same")[k:-k]


def additive(f, weights, rng):
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros_like(f)
    fmax = float(np.max(f))
    for k, w in enumerate(weights, 1):
        if k * fmax > 15000:
            break
        out += w * np.sin(k * ph + rng.uniform(0, 2 * np.pi))
    return out


def env_hold(n, a, hold, r):
    """Attack a sec, hold until `hold` sec, release r sec (n samples total)."""
    t = np.arange(n) / SR
    e = np.clip(t / max(a, 1e-3), 0, 1)
    e *= np.where(t > hold, np.exp(-(t - hold) / max(r / 4, 1e-3)), 1.0)
    return e


def drift(n, rng, rate=0.7, depth=1.0):
    """Slow random wobble, unit scale."""
    k = max(2, int(n / SR * rate) + 2)
    pts = rng.standard_normal(k)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts) * depth


SAW = [1 / k for k in range(1, 40)]
REED = [1, .38, .62, .22, .42, .16, .27, .1, .16, .07, .1, .05, .06, .03]
VOICE = [1 / k ** 1.1 for k in range(1, 40)]
BRASS = [1 / k ** 1.5 for k in range(1, 30)]


# ---------------------------------------------------------------- instruments
def string_note(m, d, rng, bright=3200, att=0.4, rel=0.9, voices=5):
    n = int((d + rel) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for _ in range(voices):
        det = 2 ** (rng.uniform(-8, 8) / 1200)
        rate = rng.uniform(4.8, 6.0)
        vib = 2 ** (rng.uniform(5, 11) / 1200 * np.sin(2 * np.pi * rate * t + rng.uniform(0, 6))
                    * np.clip((t - 0.25) / 0.5, 0, 1))
        out += additive(hz(m) * det * vib, SAW, rng)
    out = lp(out / voices, bright) * env_hold(n, att, d, rel)
    bow = bp(rng.standard_normal(n), 2500, 5000) * env_hold(n, att * 0.6, d, rel) * 0.015
    return out + bow


def spiccato(m, rng, d=0.16, bright=1900):
    n = int((d + 0.25) * SR)
    t = np.arange(n) / SR
    out = sum(additive(np.full(n, hz(m) * 2 ** (rng.uniform(-6, 6) / 1200)), SAW, rng)
              for _ in range(3)) / 3
    e = np.clip(t / 0.006, 0, 1) * np.exp(-t / (d * 0.8))
    bite = bp(rng.standard_normal(n), 1500, 4000) * np.exp(-t / 0.012) * 0.12
    return lp(out, bright) * e + bite


def pluck(m, d, rng, decay=0.9965):
    P = int(round(SR / float(hz(m))))
    n = int(d * SR)
    out = np.zeros(n + P + 1)
    out[1:P + 1] = smooth(rng.uniform(-1, 1, P), 0.00005)
    k = P + 1
    while k < len(out):
        e = min(k + P, len(out))
        blk = decay * 0.5 * (out[k - P:e - P] + out[k - P - 1:e - P - 1])
        out[k:e] = blk
        k = e
    y = out[1:n + 1]
    return lp(y, 5000) * np.clip(np.arange(n) / SR / 0.002, 0, 1)


def taiko(rng, size=1.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f0 = 52 / size ** 0.3
    f = f0 * (1 + 0.9 * np.exp(-t * 24))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.0)
    skin = lp(rng.standard_normal(n), 320, 4) * np.exp(-t * 26) * 2.5
    return np.tanh(1.6 * (body + skin))


def frame_drum(rng):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 82 * (1 + 0.5 * np.exp(-t * 30))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    skin = lp(rng.standard_normal(n), 650, 4) * np.exp(-t * 40) * 0.8
    return body + skin


def line_curves(notes, port, rng):
    """notes: (start_sec, midi, dur_sec[, grace_semitones]). Returns t0, pitch, amp, age."""
    notes = sorted(notes)
    t0 = notes[0][0]
    t1 = max(s + d for s, _, d, *g in notes) + 0.8
    n = int((t1 - t0) * SR)
    step = np.full(n, np.nan)
    amp = np.zeros(n)
    age = np.full(n, 10.0)
    off = np.zeros(n)
    idx = [(int((s - t0) * SR), min(n, int((s - t0 + d) * SR))) for s, _, d, *g in notes]
    for k, (s, m, d, *g) in enumerate(notes):
        i, j = idx[k]
        seg = j - i
        if seg <= 0:
            continue
        tt = np.arange(seg) / SR
        step[i:j] = m
        a = np.ones(seg) * (1 + 0.12 * np.clip(tt / max(d, 0.1), 0, 1))
        ai = min(int(0.06 * SR), seg)
        a[:ai] = np.linspace(0.4, a[ai - 1], ai)
        amp[i:j] = a
        age[i:j] = tt
        if g and g[0]:
            gi = min(seg, int(0.075 * SR))
            off[i:i + gi] = g[0]
        nxt = idx[k + 1][0] if k + 1 < len(idx) else n
        gap = nxt - j
        if gap <= 0:
            continue
        if gap < int(0.14 * SR):
            amp[j:nxt] = amp[j - 1]
            step[j:nxt] = m
            age[j:nxt] = tt[-1] + np.arange(gap) / SR
        else:
            r = min(gap, int(0.45 * SR))
            amp[j:j + r] = amp[j - 1] * np.exp(-np.arange(r) / SR / 0.09)
            step[j:j + r] = m
            age[j:j + r] = tt[-1] + np.arange(r) / SR
    good = ~np.isnan(step)
    ii = np.arange(n)
    step = np.interp(ii, ii[good], step[good])
    pitch = smooth(step, port) + smooth(off, 0.006)
    return t0, pitch, smooth(amp, 0.012), age


def vibrato(age, rng, rate, cents, delay):
    n = len(age)
    t = np.arange(n) / SR
    r = rate * (1 + drift(n, rng, 0.5, 0.04))
    ph = 2 * np.pi * np.cumsum(r) / SR
    depth = cents * np.clip((age - delay) / 0.45, 0, 1) * (1 + drift(n, rng, 0.4, 0.2))
    return depth * np.sin(ph) / 100.0  # in semitones


def duduk(notes, rng):
    t0, p, a, age = line_curves(notes, 0.035, rng)
    n = len(p)
    tt = np.arange(n) / SR
    scoop = np.zeros(n)
    for s, m, d, *g in notes:
        i = int((s - t0) * SR)
        k = min(n - i, int(0.18 * SR))
        if k > 0:
            scoop[i:i + k] = -0.55 * np.exp(-np.arange(k) / SR / 0.045)
    pitch = p + smooth(scoop, 0.004) + vibrato(age, rng, 5.1, 16, 0.35) + drift(n, rng, 3, 0.03)
    src = additive(hz(pitch), REED, rng)
    tone = 0.45 * lp(src, 3200) + 1.3 * bp(src, 950, 1450) + 0.45 * bp(src, 2200, 2900)
    breath = bp(rng.standard_normal(n), 900, 3500) * 0.035
    return t0, (tone + breath) * a


def vocalise(notes, rng, vowel="ah"):
    t0, p, a, age = line_curves(notes, 0.11, rng)
    n = len(p)
    pitch = p + vibrato(age, rng, 5.6, 34, 0.22) + drift(n, rng, 4, 0.04)
    src = additive(hz(pitch), VOICE, rng)
    if vowel == "ah":
        F = [(700, 900, 1.0), (1050, 1260, .55), (2750, 3050, .28), (3700, 4100, .1)]
    else:  # "oh"
        F = [(400, 560, 1.0), (750, 900, .5), (2350, 2650, .18), (3300, 3600, .06)]
    tone = 0.25 * lp(src, 450) + sum(g * bp(src, lo, hi) for lo, hi, g in F)
    breath = bp(rng.standard_normal(n), 2500, 7000) * 0.012
    return t0, (tone + breath) * a


def cello(notes, rng):
    t0, p, a, age = line_curves(notes, 0.07, rng)
    n = len(p)
    pitch = p + vibrato(age, rng, 5.4, 17, 0.15)
    src = additive(hz(pitch), SAW, rng)
    tone = 0.7 * lp(src, 2300) + 0.5 * bp(src, 220, 380) + 0.25 * bp(src, 600, 950)
    bow = bp(rng.standard_normal(n), 2000, 5000) * 0.01
    return t0, (tone + bow) * a


def horns(notes, rng, voices=3):
    outs = []
    for v in range(voices):
        jit = [(s + rng.uniform(-0.015, 0.015), m, d) for s, m, d, *g in notes]
        t0, p, a, age = line_curves(jit, 0.05, rng)
        pitch = p + vibrato(age, rng, 4.8, 6, 0.4) + rng.uniform(-0.06, 0.06)
        src = additive(hz(pitch), BRASS, rng)
        dyn = np.clip(a, 0, 1.2) ** 2
        outs.append((t0, (lp(src, 900) * (1 - 0.5 * dyn) + lp(src, 3800) * 0.8 * dyn) * a))
    t0 = min(o[0] for o in outs)
    n = max(int((o[0] - t0) * SR) + len(o[1]) for o in outs)
    y = np.zeros(n)
    for o0, s in outs:
        i = int((o0 - t0) * SR)
        y[i:i + len(s)] += s / voices
    return t0, y


def choir(ch, d, rng, att=0.9):
    """Low male 'oh' pad on chord tones."""
    out = None
    for m in ch:
        for _ in range(3):
            t0, s = vocalise([(0, m + rng.uniform(-0.08, 0.08), d)], rng, "oh")
            out = s if out is None else out[:len(s)] + s[:len(out)]
    n = len(out)
    return out * np.clip(np.arange(n) / SR / att, 0, 1) / (3 * len(ch))


# ---------------------------------------------------------------- mixing
class Mix:
    def __init__(s, dur, rng):
        s.L = int(dur * SR)
        s.dry = np.zeros((2, s.L))
        s.send = np.zeros((2, s.L))
        s.rng = rng

    def add(s, sig, t, gain=1.0, pan=0.0, rev=0.3):
        t += s.rng.uniform(-0.006, 0.006)
        i = max(0, int(t * SR))
        if i >= s.L or len(sig) == 0:
            return
        j = min(s.L, i + len(sig))
        seg = sig[:j - i] * gain
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        s.dry[0, i:j] += seg * l
        s.dry[1, i:j] += seg * r
        s.send[0, i:j] += seg * l * rev
        s.send[1, i:j] += seg * r * rev

    def render(s):
        rng = s.rng
        irn = int(3.4 * SR)
        t = np.arange(irn) / SR
        wet = np.zeros_like(s.dry)
        nfft = 1 << int(np.ceil(np.log2(s.L + irn)))
        for c in range(2):
            nz = rng.standard_normal(irn)
            ir = 0.35 * nz * np.exp(-t * 5) + lp(nz, 2200) * np.exp(-t * 1.7)
            pre = int(0.024 * SR)
            ir = np.concatenate([np.zeros(pre), ir])[:irn]
            for d, g in ((0.011, .5), (0.019, .35), (0.031, .3), (0.043, .2)):
                ir[int((d + c * 0.004) * SR)] += g
            ir /= np.sqrt(np.sum(ir ** 2))
            wet[c] = np.fft.irfft(np.fft.rfft(s.send[c], nfft) * np.fft.rfft(ir, nfft), nfft)[:s.L]
        mix = s.dry + wet * 0.55
        mix = np.stack([hp(mix[0], 32), hp(mix[1], 32)])
        mix /= np.max(np.abs(mix)) + 1e-9
        mix = np.tanh(mix * 1.6) / np.tanh(1.6)  # gentle glue
        tt = np.arange(s.L) / SR
        fade = np.clip(tt / 0.03, 0, 1) * np.clip((s.L / SR - tt) / 2.0, 0, 1) ** 1.5
        mix *= fade
        mix /= np.max(np.abs(mix)) / 0.93
        return mix


# ---------------------------------------------------------------- harmony
def chord_tones(root, quality):
    iv = {"m": (0, 3, 7), "M": (0, 4, 7)}[quality]
    return [root + i for i in iv]


def spread(root, quality, lo, hi):
    out = []
    for o in range(-3, 4):
        for i in chord_tones(root, quality):
            m = i + 12 * o
            if lo <= m <= hi:
                out.append(m)
    return sorted(out)


def extend(notes, unit, dur, period):
    """Repeat a phrase (times in beats) every `period` beats until it covers dur seconds."""
    out = []
    rep = 0
    while True:
        chunk = [(x[0] + rep * period, *x[1:]) for x in notes if (x[0] + rep * period) * unit < dur - 0.6]
        if not chunk:
            break
        out += chunk
        rep += 1
    return out


# ---------------------------------------------------------------- styles
def style_elegy(mx, K, bpm, dur, rng):
    b = 60 / bpm
    bar = 4 * b
    prog = [(50, "m"), (46, "M"), (41, "M"), (45, "M"), (50, "m"), (46, "M"), (48, "M"), (45, "M")]
    nb = int(dur / bar) + 2
    mx.add(string_note(38 + K, dur + 1, rng, bright=900, att=0.05, voices=4), 0, 0.30, 0, 0.2)
    mx.add(string_note(45 + K, dur + 1, rng, bright=900, att=1.5, voices=4), 0, 0.16, 0, 0.2)
    for i in range(nb):
        r, q = prog[i % len(prog)]
        tones = spread(r + K, q, 55 + K, 79 + K)
        pat = [0, 1, 2, 3, 4, 3, 2, 1]
        for e, k in enumerate(pat):
            m = tones[min(k, len(tones) - 1)]
            mx.add(pluck(m, 2.2, rng), i * bar + e * b / 2, 0.20 * (1.0 if e % 4 == 0 else 0.75),
                   0.45, 0.35)
        if i >= 1:
            for m in spread(r + K, q, 50 + K, 69 + K)[:4]:
                mx.add(string_note(m, bar, rng, bright=2600, att=1.2), i * bar,
                       0.07 * min(1, i / 3), rng.uniform(-0.7, 0.7), 0.5)
        if i >= 2:
            mx.add(choir(spread(r + K, q, 45 + K, 62 + K)[:3], bar, rng), i * bar, 0.5, -0.2, 0.6)
            mx.add(frame_drum(rng), i * bar, 0.35, 0, 0.2)
            mx.add(frame_drum(rng), i * bar + 0.42 * b, 0.18, 0, 0.2)
            mx.add(frame_drum(rng), i * bar + 2 * b, 0.22, 0, 0.2)
    D = [(0.5, 69, 1.5), (2, 70, .5), (2.5, 69, .5), (3, 67, 1), (4, 65, 1.5, 2), (5.5, 67, .5),
         (6, 69, 2), (8, 74, 1.5), (9.5, 72, .5), (10, 70, 1), (11, 69, 1), (12, 69, 1, 1),
         (13, 70, .5), (13.5, 69, .5), (14, 73, 2), (16, 62, 1.5), (17.5, 64, .5), (18, 65, 1),
         (19, 64, 1), (20, 62, 2, 2), (22, 65, 1), (23, 67, 1), (24, 64, 2), (26, 60, 2),
         (28, 61, 2), (30, 64, 2)]
    t0, s = duduk([(x[0] * b, x[1] + K, x[2] * b, *x[3:]) for x in extend(D, b, dur, 32)], rng)
    mx.add(s, t0, 0.42, -0.15, 0.4)
    V = [(8, 77, 4), (12, 76, 4), (16, 74, 3), (19, 77, 1), (20, 74, 4), (24, 72, 4), (28, 73, 4)]
    t0, s = vocalise([(x[0] * b, x[1] + K, x[2] * b) for x in extend(V, b, dur, 32)], rng)
    mx.add(s, t0, 0.17, 0.25, 0.7)


def style_battle(mx, K, bpm, dur, rng):
    b = 60 / bpm
    bar = 3 * b
    prog = [(50, "m"), (50, "m"), (46, "M"), (48, "M"), (50, "m"), (50, "m"), (43, "m"), (45, "M"),
            (50, "m"), (50, "m"), (46, "M"), (48, "M")]
    nb = int(dur / bar) + 2
    pat = [(0, 1.0), (0, .6), (7, .8), (0, .9), (12, .6), (7, .7)]
    for i in range(nb):
        r, q = prog[i % len(prog)]
        st = i * bar
        lo = r + K - 12 if r + K > 45 else r + K
        for e, (iv, v) in enumerate(pat):
            mx.add(spiccato(lo + iv, rng, bright=3400), st + e * b / 2, 0.26 * v, -0.3 + 0.6 * (e % 2), 0.2)
            mx.add(spiccato(lo + iv + 12, rng, bright=4200), st + e * b / 2, 0.12 * v, 0.3 - 0.6 * (e % 2), 0.25)
            mx.add(spiccato(lo + iv - 12, rng, bright=700), st + e * b / 2, 0.08 * v, 0, 0.1)
        if st < dur - 2.2:
            mx.add(taiko(rng), st, 0.5, 0, 0.25)
            if i >= 2:
                mx.add(taiko(rng, 1.4), st + 2 * b, 0.25, 0.2, 0.25)
                mx.add(taiko(rng, 1.4), st + 2.5 * b, 0.3, -0.2, 0.25)
            if i >= 5 and i % 2 == 1:
                mx.add(taiko(rng, 0.8), st + 1.5 * b, 0.4, 0, 0.3)
        if i >= 1:
            for m in spread(r + K, q, 57 + K, 76 + K)[:4]:
                mx.add(string_note(m, bar, rng, bright=4500, att=0.5), st,
                       0.1 * min(1.4, 0.5 + i / 5), rng.uniform(-0.8, 0.8), 0.45)
    H = [(6, 62, 1.5), (7.5, 64, .5), (8, 65, 1), (9, 65, 1.5), (10.5, 67, .5), (11, 62, 1),
         (12, 64, 3), (15, 69, 2), (17, 67, .5), (17.5, 65, .5), (18, 64, 1), (19, 65, 1),
         (20, 62, 1), (21, 67, 3), (24, 69, 1.5), (25.5, 70, .5), (26, 73, 1), (27, 74, 3),
         (30, 74, 3)]
    HH = extend(H, b, dur, 33)
    t0, s = horns([(x[0] * b, x[1] + K, x[2] * b) for x in HH], rng)
    mx.add(s, t0, 0.8, -0.1, 0.45)
    t0, s = horns([(x[0] * b, x[1] + K - 12, x[2] * b) for x in HH], rng, 2)
    mx.add(s, t0, 0.3, 0.1, 0.4)
    V = [(24, 81, 2.5), (26.5, 79, .5), (27, 74, 6)]
    t0, s = vocalise([(x[0] * b, x[1] + K, x[2] * b) for x in extend(V, b, dur, 33)], rng)
    mx.add(s, t0, 0.2, 0.3, 0.75)


def style_dawn(mx, K, bpm, dur, rng):
    e8 = 60 / bpm / 3  # bpm is the dotted-quarter pulse
    bar = 6 * e8
    prog = [(50, "m"), (43, "M"), (50, "m"), (48, "M"), (46, "M"), (48, "M"), (50, "m"), (50, "m")]
    nb = int(dur / bar) + 2
    mx.add(string_note(38 + K, dur + 1, rng, bright=800, att=0.05, voices=4), 0, 0.25, 0, 0.2)
    for i in range(nb):
        r, q = prog[i % len(prog)]
        tones = spread(r + K, q, 57 + K, 81 + K)
        for e, k in enumerate([0, 2, 4, 3, 4, 2]):
            mx.add(pluck(tones[min(k, len(tones) - 1)], 2.0, rng), i * bar + e * e8,
                   0.2 * (1 if e in (0, 3) else 0.7), 0.5, 0.35)
        if i >= 2:
            for m in spread(r + K, q, 53 + K, 72 + K)[:4]:
                mx.add(string_note(m, bar, rng, bright=2400, att=1.4), i * bar, 0.06,
                       rng.uniform(-0.7, 0.7), 0.5)
        if i >= 4:
            mx.add(frame_drum(rng), i * bar, 0.28, 0, 0.25)
            mx.add(frame_drum(rng), i * bar + 3 * e8, 0.16, 0, 0.25)
    C = [(1, 57, 2), (3, 62, 3), (6, 59, 2), (8, 62, 1), (9, 64, 3), (12, 65, 3), (15, 64, 2),
         (17, 62, 1), (18, 64, 3), (21, 60, 3), (24, 62, 4), (28, 65, 2), (30, 67, 3), (33, 64, 3),
         (36, 62, 6)]
    t0, s = cello([(x[0] * e8, x[1] + K, x[2] * e8) for x in extend(C, e8, dur, 42)], rng)
    mx.add(s, t0, 0.5, -0.2, 0.4)
    V = [(24, 74, 6), (30, 76, 3), (33, 72, 3), (36, 74, 9)]
    t0, s = vocalise([(x[0] * e8, x[1] + K, x[2] * e8) for x in extend(V, e8, dur, 42)], rng)
    mx.add(s, t0, 0.16, 0.3, 0.7)


def style_march(mx, K, bpm, dur, rng):
    b = 60 / bpm
    bar = 4 * b
    prog = [(50, "m"), (50, "m"), (46, "M"), (46, "M"), (43, "m"), (45, "M"), (50, "m"), (50, "m")]
    nb = int(dur / bar) + 2
    for i in range(nb):
        r, q = prog[i % len(prog)]
        st = i * bar
        if st < dur - 2.2:
            mx.add(taiko(rng), st, 0.55, 0, 0.3)
            mx.add(taiko(rng, 1.3), st + 2 * b, 0.32, 0, 0.3)
            if i >= 2:
                mx.add(taiko(rng, 1.6), st + 3.5 * b, 0.3, 0.25, 0.3)
        lo = r + K - 12 if r + K > 45 else r + K
        mx.add(string_note(lo, bar, rng, bright=1600, att=0.08, voices=4), st, 0.2, 0, 0.3)
        mx.add(string_note(lo + 7, bar, rng, bright=1600, att=0.3, voices=4), st, 0.12, 0, 0.3)
        if i >= 1:
            for m in spread(r + K, q, 60 + K, 79 + K)[:4]:
                mx.add(string_note(m, bar, rng, bright=4200, att=0.8), st, 0.07, rng.uniform(-0.8, 0.8), 0.5)
        if i >= 2:
            mx.add(choir(spread(r + K, q, 45 + K, 62 + K)[:3], bar, rng), st, 0.6, 0, 0.6)
    H = [(4, 62, 3), (7, 65, 1), (8, 69, 4), (12, 70, 2), (14, 69, 1), (15, 67, 1), (16, 65, 4),
         (20, 67, 2), (22, 70, 2), (24, 69, 3), (27, 73, 1), (28, 74, 4), (32, 74, 4)]
    t0, s = horns([(x[0] * b, x[1] + K, x[2] * b) for x in extend(H, b, dur, 36)], rng)
    mx.add(s, t0, 0.7, 0, 0.45)


STYLES = {"battle": (style_battle, 100), "elegy": (style_elegy, 68),
          "dawn": (style_dawn, 50), "march": (style_march, 70)}


def make(style, dur, seed):
    rng = np.random.default_rng(seed)
    fn, bpm = STYLES[style]
    K = int(rng.choice([0, 0, -2, 2, -1]))
    bpm *= rng.uniform(0.96, 1.04)
    mx = Mix(dur, rng)
    fn(mx, K, bpm, dur, rng)
    return mx.render()


if __name__ == "__main__":
    style, dur, seed, path = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    st = make(style, dur, seed)
    w = wave.open(path, "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st.T * 32767).astype(np.int16).tobytes())
    w.close()
    print(path, style, dur)
