#!/usr/bin/env python3
"""Build a finished episode: long 16:9 video, vertical shorts, subtitles, thumbnail, upload text.

Usage:
    python3 pipeline/build.py episodes/01-civil-war-explained [--only long|shorts|thumb] [--fast]

Inputs (in the episode folder):
    episode.json            script, scenes, Burmese lines, shorts, sources
    audio/narration.*       your recorded voice (wav/m4a/mp3). If missing, a silent
                            DRAFT is built with estimated timing so you can preview.
Outputs: output/<episode-id>/
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import scenes as S

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FPS = 25


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"Command failed: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-2000:]}")
    return r


# ---------------------------------------------------------------- audio & timing
def find_audio(ep_dir):
    """All narration* files in audio/, sorted by name (narration-1, narration-2, ... are joined in order)."""
    exts = {".wav", ".m4a", ".mp3", ".aac", ".flac", ".ogg", ".webm", ".mp4", ".mov"}
    d = ep_dir / "audio"
    return sorted(p for p in d.glob("narration*") if p.suffix.lower() in exts) if d.exists() else []


def join_audio(files, dst):
    """Join section recordings with a 1.2 s pause between them."""
    if len(files) == 1:
        return files[0]
    ins, parts = [], []
    for i, f in enumerate(files):
        ins += ["-i", str(f)]
        parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,apad=pad_dur=1.2[a{i}]")
    fc = ";".join(parts) + ";" + "".join(f"[a{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1[out]"
    run(["ffmpeg", "-y", *ins, "-filter_complex", fc, "-map", "[out]", str(dst)])
    return dst


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(r.stdout.strip())


def clean_audio(src, dst):
    """Voice cleanup: rumble filter, denoise, gentle compression, loudness -14 LUFS (YouTube standard)."""
    af = ("highpass=f=80,afftdn=nf=-25,"
          "acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
          "loudnorm=I=-14:TP=-1.5:LRA=11")
    run(["ffmpeg", "-y", "-i", str(src), "-af", af, "-ar", "48000", "-ac", "2", str(dst)])


def silences(path):
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af", "silencedetect=noise=-38dB:d=0.28", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(starts, ends))


def align(lines, audio):
    """Give each subtitle line a (start, end) by matching the script to pauses in the voice."""
    total = duration(audio)
    sil = silences(audio)
    sp_start = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    sp_end = sil[-1][0] if sil and sil[-1][1] > total - 0.05 else total
    inner = [(a, b) for a, b in sil if a > sp_start + 0.1 and b < sp_end - 0.1]
    # Dynamic programming: choose one pause after each line (except the last) so that
    # every line's spoken length best matches its expected length from its character count.
    n = len(lines)
    w = [len(l["en"]) + 8 for l in lines]
    speech = (sp_end - sp_start) - sum(b - a for a, b in inner)
    rate = speech / sum(w)  # seconds per character of actual speech
    # candidate cut points: pause starts/ends; index 0 = speech start, M+1 = speech end
    pts = [(sp_start, sp_start)] + inner + [(sp_end, sp_end)]
    M = len(pts)
    pre = [0.0] * M  # cumulative silence length before each point, to measure speech only
    for j in range(1, M):
        pre[j] = pre[j - 1] + (pts[j - 1][1] - pts[j - 1][0])

    def cost(i, j0, j1):  # line i spoken between end of pause j0 and start of pause j1
        spoken = (pts[j1][0] - pts[j0][1]) - (pre[j1] - pre[j0 + 1])
        exp = w[i] * rate
        bonus = 0.6 * min(pts[j1][1] - pts[j1][0], 1.5) if j1 < M - 1 else 0
        return (spoken - exp) ** 2 / exp - bonus

    INF = float("inf")
    if M - 2 < n - 1:  # not enough pauses: fall back to proportional split
        t, edges = sp_start, [0.0]
        for i in range(n - 1):
            t += (sp_end - sp_start) * w[i] / sum(w)
            edges.append(t)
        edges.append(total)
        return [(edges[i], edges[i + 1]) for i in range(n)], total
    best = [[INF] * M for _ in range(n + 1)]
    back = [[-1] * M for _ in range(n + 1)]
    best[0][0] = 0.0
    for i in range(n):
        for j0 in range(M):
            if best[i][j0] == INF:
                continue
            lo = j0 + 1
            hi = M - (n - i - 1) - 1 if i < n - 1 else M - 1
            rng = range(lo, hi + 1) if i < n - 1 else [M - 1]
            for j1 in rng:
                c = best[i][j0] + cost(i, j0, j1)
                if c < best[i + 1][j1]:
                    best[i + 1][j1], back[i + 1][j1] = c, j0
    chain, j = [], M - 1
    for i in range(n, 0, -1):
        chain.append(j)
        j = back[i][j]
    chain.reverse()  # chain[i] = pause index ending line i
    bounds = [min(pts[j][1], pts[j][0] + 0.25) for j in chain[:-1]]
    edges = [0.0] + bounds + [total]
    return [(edges[i], edges[i + 1]) for i in range(len(lines))], total


def estimate(lines):
    t, out = 0.4, []
    for l in lines:
        d = max(1.6, len(l["en"].split()) / 2.5) + 0.35
        out.append((t, t + d))
        t += d
    out[0] = (0.0, out[0][1])
    return out, t + 0.6


# ---------------------------------------------------------------- subtitles
def ts_srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ts_ass(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_srt(path, items, key):
    with open(path, "w", encoding="utf-8") as f:
        for n, (a, b, l) in enumerate(items, 1):
            f.write(f"{n}\n{ts_srt(a)} --> {ts_srt(b - 0.04)}\n{l[key]}\n\n")


def write_ass(path, items, vertical, english, burmese=True):
    if vertical:
        W, H = 1080, 1920
        st = [("EN", "Inter", 56, 1, 2, 600), ("MY", "Noto Sans Myanmar", 52, 0, 2, 430)]
    else:
        W, H = 1920, 1080
        st = [("EN", "Inter", 44, 1, 2, 150), ("MY", "Noto Sans Myanmar", 48, 0, 2, 48)]
    my_margin = st[1][5]
    en_margin = st[0][5] if vertical else (my_margin + 110 if burmese else 52)
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EN,{st[0][1]},{st[0][2]},&H00FFFFFF,&H00FFFFFF,&H00141B0E,&H96141B0E,{-1 if vertical else 0},0,0,0,100,100,0,0,{3 if not vertical else 1},{10 if not vertical else 5},0,2,{90 if vertical else 200},{90 if vertical else 200},{en_margin},1
Style: MY,{st[1][1]},{st[1][2]},&H0066E0FF,&H0066E0FF,&H00141B0E,&H96141B0E,0,0,0,0,100,100,0,0,3,10,0,2,{70 if vertical else 200},{70 if vertical else 200},{my_margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    esc = lambda s: s.replace("{", "(").replace("}", ")").replace("\n", "\\N")
    with open(path, "w", encoding="utf-8") as f:
        f.write(hdr)
        for a, b, l in items:
            if english:
                f.write(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b - 0.04)},EN,,0,0,0,,{esc(l['en'])}\n")
            if burmese and l.get("my"):
                f.write(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b - 0.04)},MY,,0,0,0,,{esc(l['my'])}\n")


# ---------------------------------------------------------------- visuals
def reveal_states(scene):
    """For each line in a scene, how many reveal items are visible (None = no reveal)."""
    m = len(scene["lines"])
    if not scene.get("reveal"):
        return [None] * m
    n = len(scene["items"])
    at = scene.get("reveal_at") or [min(i, m - 1) if m >= n else math.floor(i * m / n) for i in range(n)]
    return [sum(1 for x in at if x <= j) for j in range(m)]


def plan_segments(ep, times):
    """Split the timeline into visual segments: (scene_idx, state, start, end)."""
    segs, k = [], 0
    for si, sc in enumerate(ep["scenes"]):
        states = reveal_states(sc)
        for j, stt in enumerate(states):
            a, b = times[k]
            if segs and segs[-1][0] == si and segs[-1][1] == stt:
                segs[-1][3] = b
            else:
                segs.append([si, stt, a, b])
            k += 1
    return segs


def render_pngs(jobs, work):
    if not jobs:
        return
    jf = work / "jobs.json"
    jf.write_text(json.dumps(jobs))
    run(["node", str(HERE / "render.js"), str(jf)], cwd=str(HERE))


def encode_segment(png, out, frames, vertical, zoom, fast):
    W, H = (1080, 1920) if vertical else (1920, 1080)
    if zoom:
        vf = (f"scale={W * 2}:{H * 2},zoompan=z='1+0.045*on/{max(frames, 1)}':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},format=yuv420p")
    else:
        vf = f"scale={W}:{H},format=yuv420p"
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(png), "-frames:v", str(frames),
         "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast" if fast else "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])


def assemble(seg_files, audio, ass, out, fast, audio_filter=None):
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{p}'\n" for p in seg_files))
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(audio)]
    vf = f"ass={ass}:fontsdir={HERE / 'fonts'}"
    cmd += ["-vf", vf]
    if audio_filter:
        cmd += ["-af", audio_filter]
    cmd += ["-c:v", "libx264", "-preset", "veryfast" if fast else "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    run(cmd)
    lst.unlink()


def build_video(ep, segs, items, audio, total, out_dir, work, vertical, name, fast, hook="", endcard=None,
                audio_filter=None, english=None):
    tag = "v" if vertical else "h"
    W, H = (1080, 1920) if vertical else (1920, 1080)
    jobs, pngs = [], []
    for i, (si, stt, a, b) in enumerate(segs):
        sc = ep["scenes"][si] if si >= 0 else endcard
        key = f"{name}_{i:03d}"
        htmlp = work / f"{key}.html"
        htmlp.write_text(S.render_scene(sc, tag, stt, hook=hook if si >= 0 else ""), encoding="utf-8")
        png = work / f"{key}.png"
        jobs.append({"html": str(htmlp), "png": str(png), "w": W, "h": H, "scale": 2})
        pngs.append(png)
    render_pngs(jobs, work)
    files = []
    for i, (si, stt, a, b) in enumerate(segs):
        frames = round(b * FPS) - round(a * FPS)
        f = work / f"{name}_{i:03d}.mp4"
        sc = ep["scenes"][si] if si >= 0 else endcard
        zoom = stt is None and sc.get("zoom", True)
        encode_segment(pngs[i], f, frames, vertical, zoom, fast)
        files.append(f)
        print(f"  [{name}] segment {i + 1}/{len(segs)}", end="\r", flush=True)
    print()
    ass = work / f"{name}.ass"
    if english is None:
        english = vertical or ep.get("burn_english_long", False)
    write_ass(ass, items, vertical, english=english)
    out = out_dir / f"{name}.mp4"
    assemble(files, audio, ass, out, fast, audio_filter)
    return out


# ---------------------------------------------------------------- upload text
def fmt_clock(t):
    t = int(t)
    return f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def write_upload(ep, segs, total, out_dir, draft):
    chapters = [(0, ep["scenes"][0].get("chapter_label", "Intro"))]
    seen = set()
    for si, stt, a, b in segs:
        sc = ep["scenes"][si]
        if sc["type"] == "chapter" and si not in seen:
            seen.add(si)
            chapters.append((a, sc["title"]))
    up = ep.get("upload", {})
    lines = [f"# Upload kit: {ep['title']}", ""]
    if draft:
        lines += ["> **DRAFT**: built without narration audio. Timings are estimates. Do not upload.", ""]
    lines += ["## YouTube (long video: `long.mp4`)", "", "**Title options**", ""]
    lines += [f"- {t}" for t in up.get("titles", [ep["title"]])]
    lines += ["", "**Description** (copy everything in the box)", "", "```"]
    lines += [up.get("description", ""), ""]
    if len(chapters) >= 3:
        lines += ["Chapters"] + [f"{fmt_clock(t)} {n}" for t, n in chapters] + [""]
    if ep.get("sources"):
        lines += ["Sources"] + [f"- {s}" for s in ep["sources"]] + [""]
    lines += [up.get("footer", "")]
    lines += ["```", "", f"**Tags:** {', '.join(up.get('tags', []))}", "",
              "**Subtitles:** upload `en.srt` (English) and `my.srt` (Burmese) under Subtitles.", "",
              "**Altered or synthetic content:** answer *No* unless the video uses realistic AI images, video or voice.", ""]
    for sh in ep.get("shorts", []):
        lines += [f"## Short: `{sh['id']}.mp4`", "", f"**Caption:** {sh.get('caption', sh.get('hook', ''))}", "",
                  f"**Hashtags:** {' '.join(sh.get('hashtags', up.get('hashtags', [])))}", ""]
    (out_dir / "upload.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--only", choices=["long", "shorts", "thumb"])
    ap.add_argument("--fast", action="store_true", help="quicker, lower-quality encode for previews")
    args = ap.parse_args()

    ep_dir = Path(args.episode).resolve()
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    S.BRAND = ep.get("channel_html", S.BRAND)
    for sc in ep["scenes"]:  # image paths are relative to the episode folder
        if sc["type"] == "image":
            sc["src"] = str((ep_dir / sc["src"]).resolve())
    out_dir = ROOT / "output" / ep["id"]
    work = out_dir / "_work"
    work.mkdir(parents=True, exist_ok=True)

    lines = [dict(l, scene=si) for si, sc in enumerate(ep["scenes"]) for l in sc["lines"]]
    found = find_audio(ep_dir)
    draft = not found
    src = join_audio(found, work / "narration_joined.wav") if found else None
    if draft:
        print("No narration found in audio/: building a silent DRAFT with estimated timing.")
        times, total = estimate(lines)
        audio = work / "silence.wav"
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{total:.3f}", str(audio)])
    else:
        print(f"Cleaning narration: {src.name}")
        audio = out_dir / "narration_clean.wav"
        clean_audio(src, audio)
        times, total = align(lines, audio)
    times[-1] = (times[-1][0], total)
    items = [(a, b, l) for (a, b), l in zip(times, lines)]
    write_srt(out_dir / "en.srt", items, "en")
    write_srt(out_dir / "my.srt", items, "my")
    segs = plan_segments(ep, times)
    (out_dir / "timing.json").write_text(json.dumps(
        [{"start": round(a, 2), "end": round(b, 2), "en": l["en"]} for a, b, l in items], indent=1, ensure_ascii=False))
    print(f"Runtime {fmt_clock(total)}, {len(lines)} lines, {len(segs)} visual segments")

    if args.only in (None, "thumb") and ep.get("thumbnail"):
        th = work / "thumb.html"
        th.write_text(S.thumbnail(ep["thumbnail"]), encoding="utf-8")
        render_pngs([{"html": str(th), "png": str(out_dir / "thumbnail.png"), "w": 1920, "h": 1080, "scale": 1}], work)
        run(["ffmpeg", "-y", "-i", str(out_dir / "thumbnail.png"), "-vf", "scale=1280:720", "-q:v", "2", str(out_dir / "thumbnail.jpg")])
        print("Thumbnail done")

    if args.only in (None, "long"):
        p = build_video(ep, segs, items, audio, total, out_dir, work, False, "long", args.fast)
        print(f"Long video: {p}")

    if args.only in (None, "shorts"):
        for sh in ep.get("shorts", []):
            want = set(sh["scenes"])
            spans = []  # (orig_start, orig_end) for each kept scene
            for si in sh["scenes"]:
                ks = [k for k, l in enumerate(lines) if l["scene"] == si]
                spans.append((times[ks[0]][0] if ks[0] else 0.0, times[ks[-1]][1]))
            spans[0] = (max(spans[0][0], 0.0), spans[0][1])
            sh_segs, sh_items, off, parts = [], [], 0.0, []
            for (a0, b0), si in zip(spans, sh["scenes"]):
                for s_si, stt, a, b in segs:
                    if s_si == si:
                        sh_segs.append([si, stt, a - a0 + off, b - a0 + off])
                for a, b, l in items:
                    if l["scene"] == si:
                        sh_items.append((a - a0 + off, b - a0 + off, l))
                parts.append(f"atrim={a0:.3f}:{b0:.3f},asetpts=PTS-STARTPTS")
                off += b0 - a0
            end_len = 3.0
            endcard = {"type": "endcard", "title": ep.get("short_endcard_title", ep["title"]),
                       "cta": ep.get("short_cta", "Full video on YouTube")}
            sh_segs.append([-1, None, off, off + end_len])
            n = len(parts)
            af = ";".join(f"[0:a]{p}[a{i}]" for i, p in enumerate(parts))
            af += ";" + "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,apad=pad_dur={end_len}[aout]"
            sh_audio = work / f"{sh['id']}.wav"
            run(["ffmpeg", "-y", "-i", str(audio), "-filter_complex", af, "-map", "[aout]",
                 "-t", f"{off + end_len:.3f}", str(sh_audio)])
            if off + end_len > 180:
                print(f"  WARNING: {sh['id']} is {off + end_len:.0f}s. YouTube Shorts max is 180s.")
            hook = S.e(sh.get("hook", "")).replace("*", "<span>", 1).replace("*", "</span>", 1)
            p = build_video(ep, sh_segs, sh_items, sh_audio, off + end_len, out_dir, work, True, sh["id"],
                            args.fast, hook=hook, endcard=endcard)
            print(f"Short: {p} ({off + end_len:.0f}s)")

    write_upload(ep, segs, total, out_dir, draft)
    print(f"Upload kit: {out_dir / 'upload.md'}")


if __name__ == "__main__":
    main()
