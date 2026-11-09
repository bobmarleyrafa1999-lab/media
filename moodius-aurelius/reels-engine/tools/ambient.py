#!/usr/bin/env python3
"""Quiet original ambient beds for text reels (the "subtle ambient music" option).

    python3 ambient.py <mood> <dur> <seed> <out.wav>

moods:
  night  low minor pad, sparse felt-piano notes, faint room noise
  dawn   open fifths, brighter pad, slow rising notes
  warm   major-seventh pad, gentle mid notes
  low    sub-heavy drone, almost no melody (for heavy topics)
  dry    thin pad with a light pulse (for humour: stays out of the joke's way)
  room   mostly room tone and one sustained chord (for "sit in silence" reels)

Deterministic: the same mood + seed always gives the same file. Sound starts at t=0 so the
hook never lands in silence, and every bed fades out instead of resolving.
"""
import sys, wave
import numpy as np

SR = 44100
MOODS = {
    #        root  chord (semitones)     pad_cut  notes/10s  scale for notes            noise   pulse
    "night": (45, [0, 3, 7, 10],        900,     4,        [0, 3, 5, 7, 10, 12, 15],  0.010,  0),
    "dawn":  (50, [0, 7, 12, 14],       1500,    5,        [0, 2, 4, 7, 9, 12, 14],   0.006,  0),
    "warm":  (48, [0, 4, 7, 11],        1300,    4,        [0, 2, 4, 7, 9, 11, 12],   0.006,  0),
    "low":   (38, [0, 7, 12],           600,     1.5,      [0, 3, 7, 12],             0.008,  0),
    "dry":   (47, [0, 5, 10],           1000,    3,        [0, 2, 5, 7, 10, 12],      0.004,  1),
    "room":  (43, [0, 7, 15],           700,     1,        [0, 7, 12],                0.020,  0),
}


def hz(m):
    return 440.0 * 2 ** ((np.asarray(m, float) - 69) / 12)


def lp(x, fc, order=2):
    """Butterworth-shaped low-pass applied in the frequency domain (NumPy only, no SciPy needed)."""
    spec = np.fft.rfft(x, axis=-1)
    f = np.fft.rfftfreq(x.shape[-1], 1 / SR)
    return np.fft.irfft(spec / np.sqrt(1 + (f / fc) ** (2 * order)), n=x.shape[-1], axis=-1)


def pad(root, chord, cut, n, rng):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for semi in chord:
        f = hz(root + 12 + semi)
        for det in (-0.004, 0.0, 0.0045):
            ph = rng.uniform(0, 2 * np.pi)
            lfo = 0.75 + 0.25 * np.sin(2 * np.pi * rng.uniform(0.04, 0.11) * t + ph)
            out += lfo * (np.sin(2 * np.pi * f * (1 + det) * t + ph) + 0.25 * np.sin(4 * np.pi * f * (1 + det) * t))
    return lp(out / (len(chord) * 3), cut)


def felt_note(f, d, rng):
    n = int(d * SR)
    t = np.arange(n) / SR
    env = np.minimum(t / 0.012, 1) * np.exp(-t / rng.uniform(1.6, 2.6))
    tone = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)))
    return lp(env * tone, 2200)


def render(mood, dur, seed):
    root, chord, cut, density, scale, noise_amt, pulse = MOODS[mood]
    rng = np.random.default_rng(seed)
    root += int(rng.integers(-2, 3))
    n = int(dur * SR)
    left = pad(root, chord, cut, n, rng)
    right = pad(root, chord, cut * 1.1, n, rng)
    bed = np.stack([left, right]) * 0.5
    # felt-piano notes, never in the first 0.4s or the last 1.5s
    count = max(1, int(density * dur / 10))
    for _ in range(count):
        start = rng.uniform(0.4, max(0.5, dur - 3.5))
        m = root + 24 + int(rng.choice(scale))
        note = felt_note(hz(m), 3.5, rng) * rng.uniform(0.18, 0.28)
        i = int(start * SR)
        j = min(n, i + len(note))
        pan = rng.uniform(0.3, 0.7)
        bed[0, i:j] += note[: j - i] * (1 - pan)
        bed[1, i:j] += note[: j - i] * pan
    if pulse:
        t = np.arange(n) / SR
        beat = 60 / 84
        env = np.exp(-((t % beat) / 0.09))
        bed += 0.05 * env * np.sin(2 * np.pi * hz(root) * t)
    room = lp(rng.standard_normal((2, n)), 500) * noise_amt * 6
    bed += room
    # fast fade-in so the hook isn't silent, long fade-out, no ending hit
    fade = np.ones(n)
    k = int(0.35 * SR)
    fade[:k] = np.linspace(0.35, 1, k)
    k2 = int(min(1.6, dur / 4) * SR)
    fade[-k2:] = np.linspace(1, 0, k2) ** 1.5
    bed *= fade
    bed /= max(1e-9, np.abs(bed).max())
    return (bed * 0.6 * 32767).astype(np.int16)


def write(path, pcm):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.T.copy().tobytes())


if __name__ == "__main__":
    mood, dur, seed, out = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    write(out, render(mood, dur, seed))
