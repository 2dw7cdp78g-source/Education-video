"""Original background music, generated from scratch (no copyright issues).

A calm ambient bed: soft pad chords plus a gentle piano-like arpeggio, with echo for space.
It is mixed under the narration and automatically ducks (gets quieter) while the voice speaks.
"""
import subprocess

import numpy as np

SR = 32000
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(name):
    n, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE[n] + 12 * (octave + 1) - 69) / 12)


# A calm minor progression (Am - Fmaj7 - C - G), each chord 8 seconds
PROGRESSION = [
    ["A2", "E3", "A3", "C4", "E4"],
    ["F2", "C3", "A3", "E4", "A4"],
    ["C3", "G3", "C4", "E4", "G4"],
    ["G2", "D3", "G3", "B3", "D4"],
]
CHORD_SEC = 8.0


def _pad(freqs, dur):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for f in freqs:
        for det in (-0.0018, 0.0, 0.0021):  # three slightly detuned voices = warm chorus
            out += np.sin(2 * np.pi * f * (1 + det) * t + np.random.uniform(0, 6.28))
            out += 0.25 * np.sin(2 * np.pi * 2 * f * (1 + det) * t)
    env = np.minimum(1, t / 2.5) * np.minimum(1, (dur - t) / 2.5)  # slow swell in and out
    return out * env / (len(freqs) * 4)


def _pluck(f, dur=3.0):
    t = np.arange(int(dur * SR)) / SR
    tone = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    return tone * np.exp(-t * 2.2) * np.minimum(1, t / 0.01)


def compose(seconds, seed=11):
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    n = int((seconds + 4) * SR)
    mix = np.zeros(n + int(12 * SR))
    step = int(CHORD_SEC * SR)
    overlap = int(2.5 * SR)
    i = 0
    while i * step < n:
        chord = PROGRESSION[i % len(PROGRESSION)]
        freqs = [hz(c) for c in chord]
        pad = _pad(freqs, CHORD_SEC + 2.5)
        s = i * step
        mix[s:s + len(pad)] += pad * 0.55
        # gentle arpeggio: 8 notes per chord, upper chord tones, slightly random velocity
        for k in range(8):
            f = hz(chord[1 + (k % 4)]) * 2
            pl = _pluck(f) * rng.uniform(.10, .18)
            p0 = s + int(k * CHORD_SEC / 8 * SR)
            mix[p0:p0 + len(pl)] += pl[: len(mix) - p0]
        i += 1
    mix = mix[:n]
    mix /= np.max(np.abs(mix)) + 1e-9
    return mix * 0.8, overlap


def make_bed(seconds, out_wav, level_lufs=-30):
    """Write a stereo 48 kHz music bed of the given length, with echo and loudness normalised."""
    mono, _ = compose(seconds)
    raw = str(out_wav) + ".raw.f32"
    mono.astype(np.float32).tofile(raw)
    af = (f"aecho=0.8:0.6:90|230|470:0.28|0.18|0.12,lowpass=f=5200,highpass=f=60,"
          f"afade=t=in:d=3,afade=t=out:st={max(0, seconds - 4):.2f}:d=4,loudnorm=I={level_lufs}:TP=-3:LRA=7")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", raw,
                    "-af", af, "-ar", "48000", "-ac", "2", "-t", f"{seconds:.3f}", str(out_wav)], check=True)
    import os
    os.remove(raw)


def mix_under(voice_wav, music_wav, out_wav):
    """Voice on top; music ducks automatically while the voice is speaking."""
    fc = ("[1:a]anull[m];[0:a]asplit=2[v][sc];"
          "[m][sc]sidechaincompress=threshold=0.02:ratio=5:attack=120:release=900[duck];"
          "[v][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(voice_wav), "-i", str(music_wav),
                    "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-ac", "2", str(out_wav)], check=True)
