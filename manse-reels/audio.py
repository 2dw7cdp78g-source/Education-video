"""Original upbeat music and sound effects, generated from scratch (no copyright issues)."""
import subprocess

import numpy as np

SR = 44100
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(name, shift=0):
    n, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE[n] + shift + 12 * (octave + 1) - 69) / 12)


def _t(sec):
    return np.arange(int(sec * SR)) / SR


def _kick():
    t = _t(0.35)
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def _clap(rng):
    t = _t(0.22)
    n = rng.uniform(-1, 1, len(t))
    env = np.exp(-t * 22) + 0.6 * np.exp(-np.maximum(0, t - 0.012) * 30) * (t > 0.012)
    return np.convolve(n * env, np.ones(3) / 3, "same") * 0.55


def _hat(rng, open_=False):
    t = _t(0.18 if open_ else 0.05)
    n = rng.uniform(-1, 1, len(t))
    n = n - np.concatenate([[0], n[:-1]])  # crude high-pass
    return n * np.exp(-t * (18 if open_ else 70)) * 0.18


def _bass(f, dur):
    t = _t(dur)
    w = np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + np.sin(2 * np.pi * f * t)
    return w * np.minimum(1, t / 0.005) * np.exp(-t * 3.5) * 0.45


def _pluck(f, dur=0.5):
    t = _t(dur)
    w = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.3 for k in range(1, 6))
    return w * np.exp(-t * 7) * np.minimum(1, t / 0.003)


def _chord_stab(freqs, dur):
    t = _t(dur)
    out = np.zeros_like(t)
    for f in freqs:
        for det in (-0.004, 0.0, 0.004):
            ph = 2 * np.pi * f * (1 + det) * t
            out += 2 * (ph / (2 * np.pi) % 1) - 1  # saw
    out /= len(freqs) * 3
    return np.convolve(out, np.ones(6) / 6, "same") * np.exp(-t * 4) * np.minimum(1, t / 0.004)


# Bright, bouncy I-V-vi-IV in C (shifted per reel), K-pop-ish
PROG = [["C4", "E4", "G4"], ["G3", "B3", "D4"], ["A3", "C4", "E4"], ["F3", "A3", "C4"]]
ROOTS = ["C2", "G1", "A1", "F1"]


def compose(seconds, bpm=112, shift=0, seed=3):
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    n = int((seconds + 2) * SR)
    mix = np.zeros(n + SR)

    def add(sig, at, gain=1.0):
        s = int(at * SR)
        if s >= n:
            return
        e = min(len(mix), s + len(sig))
        mix[s:e] += sig[: e - s] * gain

    kick, claps = _kick(), [_clap(rng) for _ in range(4)]
    b = 0
    while b * beat < seconds + 1:
        t0 = b * beat
        bar, pos = divmod(b, 4)
        ci = bar % 4
        add(kick, t0, 0.9)
        if pos in (1, 3):
            add(claps[b % 4], t0, 0.8)
        for h in range(2):
            add(_hat(rng, open_=(h == 1 and pos == 3)), t0 + h * beat / 2, 0.9)
        root = hz(ROOTS[ci], shift)
        add(_bass(root, beat * 0.45), t0)
        add(_bass(root * 2, beat * 0.3), t0 + beat * 0.5, 0.6)
        if pos in (0, 2):
            add(_chord_stab([hz(x, shift) for x in PROG[ci]], beat * 0.9), t0 + beat * 0.5, 0.5)
        # melody: arpeggio of chord tones, an octave up, with a little randomness
        tones = [hz(x, shift) * 2 for x in PROG[ci]]
        for k in range(2):
            if rng.random() < 0.8:
                add(_pluck(tones[(b * 2 + k) % 3] * (2 if rng.random() < 0.2 else 1)),
                    t0 + k * beat / 2, 0.16)
        b += 1
    mix = mix[:n]
    return mix / (np.max(np.abs(mix)) + 1e-9) * 0.9


def make_music(seconds, out_wav, shift=0, seed=3, bpm=112, lufs=-24):
    mono = compose(seconds, bpm=bpm, shift=shift, seed=seed)
    raw = str(out_wav) + ".f32"
    mono.astype(np.float32).tofile(raw)
    af = (f"aecho=0.8:0.5:60|140:0.18|0.10,highpass=f=35,afade=t=in:d=0.3,"
          f"afade=t=out:st={max(0, seconds - 1.5):.2f}:d=1.5,loudnorm=I={lufs}:TP=-2:LRA=7")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", raw,
                    "-af", af, "-ar", "48000", "-ac", "2", "-t", f"{seconds:.3f}", str(out_wav)], check=True)
    import os
    os.remove(raw)


# ---------- sound effects ----------

def sfx_whoosh():
    rng = np.random.default_rng(1)
    t = _t(0.45)
    n = rng.uniform(-1, 1, len(t))
    env = np.sin(np.pi * np.clip(t / 0.45, 0, 1)) ** 2
    out, y, a = np.zeros_like(n), 0.0, 0.0
    for i in range(len(n)):  # sweeping one-pole low-pass
        a = 0.02 + 0.25 * (i / len(n))
        y += a * (n[i] - y)
        out[i] = y
    return out * env * 1.6


def sfx_pop():
    t = _t(0.12)
    f = 900 * np.exp(-t * 25) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35) * 0.7


def sfx_ding():
    t = _t(0.9)
    out = np.zeros_like(t)
    for f0, d in ((1318.5, 0.0), (1760.0, 0.09)):
        tt = np.clip(t - d, 0, None)
        out += (np.sin(2 * np.pi * f0 * tt) + 0.3 * np.sin(2 * np.pi * f0 * 2.7 * tt)) * np.exp(-tt * 5) * (t >= d)
    return out * 0.45


def sfx_boom():
    t = _t(0.6)
    f = 40 + 80 * np.exp(-t * 12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.9


SFX = {"whoosh": sfx_whoosh, "pop": sfx_pop, "ding": sfx_ding, "boom": sfx_boom}


def make_sfx_track(events, seconds, out_wav):
    """events: [(time, name, gain)]"""
    mix = np.zeros(int((seconds + 1) * SR))
    cache = {}
    for at, name, gain in events:
        sig = cache.setdefault(name, SFX[name]())
        s = int(at * SR)
        e = min(len(mix), s + len(sig))
        if s < len(mix):
            mix[s:e] += sig[: e - s] * gain
    mix = np.clip(mix, -1, 1)[: int(seconds * SR)]
    raw = str(out_wav) + ".f32"
    mix.astype(np.float32).tofile(raw)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", raw,
                    "-ar", "48000", "-ac", "2", str(out_wav)], check=True)
    import os
    os.remove(raw)
