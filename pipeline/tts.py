"""AI narration with Kokoro (open-source, Apache-2.0: free for commercial use, runs locally)."""
import subprocess
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

MODELS = Path(__file__).resolve().parent / "models"
URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]

VOICES = {  # friendly name -> (kokoro id, language)
    "michael": ("am_michael", "en-us"), "george": ("bm_george", "en-gb"),
    "emma": ("bf_emma", "en-gb"), "heart": ("af_heart", "en-us"),
}


def _model():
    MODELS.mkdir(exist_ok=True)
    for f in FILES:
        if not (MODELS / f).exists():
            print(f"Downloading voice model {f} ...")
            urllib.request.urlretrieve(URL + f, MODELS / f)
    from kokoro_onnx import Kokoro
    return Kokoro(str(MODELS / FILES[0]), str(MODELS / FILES[1]))


def narrate(lines, scene_of, chapter_scenes, cfg, out_wav):
    """Speak every line; return [(start, end)] per line and total length.

    Pauses: 0.45 s between sentences, 0.9 s between scenes, 1.3 s before a new part.
    """
    voice, lang = VOICES.get(cfg.get("voice", "george"), (cfg.get("voice"), cfg.get("lang", "en-us")))
    speed = cfg.get("speed", 0.95)
    k = _model()
    sr, chunks, times, t = 24000, [], [], 0.6
    chunks.append(np.zeros(int(sr * 0.6), dtype=np.float32))
    for i, l in enumerate(lines):
        audio, sr = k.create(l.get("say", l["en"]), voice=voice, speed=speed, lang=lang)
        audio = np.asarray(audio, dtype=np.float32)
        # trim leading/trailing near-silence so pauses are consistent
        idx = np.where(np.abs(audio) > 0.01)[0]
        if len(idx):
            audio = audio[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
        d = len(audio) / sr
        if i + 1 < len(lines):
            nxt = scene_of[i + 1]
            gap = 1.3 if (nxt != scene_of[i] and nxt in chapter_scenes) else 0.9 if nxt != scene_of[i] else 0.45
        else:
            gap = 1.2
        gap *= cfg.get("gap_scale", 1.0)
        times.append([t, t + d])
        chunks += [audio, np.zeros(int(sr * gap), dtype=np.float32)]
        t += d + gap
        print(f"  voice {i + 1}/{len(lines)}", end="\r", flush=True)
    print()
    raw = Path(out_wav).with_suffix(".raw.wav")
    sf.write(raw, np.concatenate(chunks), sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", str(out_wav)], check=True)
    raw.unlink()
    # subtitles: each line runs until the next line starts (no flicker during short pauses)
    for i in range(len(times) - 1):
        times[i][1] = times[i + 1][0]
    times[0][0] = 0.0
    return [tuple(x) for x in times], t
