"""Build vertical Facebook Reels (1080x1920) for MANSE Korean Food.

Usage:  python3 build.py            # all reels
        python3 build.py 01 05      # only reels whose id starts with these
Output: reels/<id>.mp4, reels/<id>-cover.jpg, reels/CAPTIONS.md
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image

import audio

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
WORK = ROOT / "work"
OUT = ROOT / "reels"
W, H, FPS = 1080, 1920, 30
CFG = json.loads((ROOT / "reels.json").read_text())
CTA_TAIL = " Manse Korean food. Made with love!"


# ---------------------------------------------------------------- voice
_kokoro = None


def tts(text, out):
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        m = REPO / "pipeline" / "models"
        _kokoro = Kokoro(str(m / "kokoro-v1.0.onnx"), str(m / "voices-v1.0.bin"))
    for k, v in CFG["pronounce"].items():
        text = re.sub(rf"\b{re.escape(k)}\b", v, text)
    a, sr = _kokoro.create(text, voice=CFG["voice"], speed=CFG["speed"], lang="en-us")
    a = np.asarray(a, dtype=np.float32)
    idx = np.where(np.abs(a) > 0.01)[0]
    if len(idx):
        a = a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
    sf.write(out, a, sr)
    return a, sr


# ---------------------------------------------------------------- captions
def chunks(text, dur, start):
    words = text.split()
    groups, cur = [], []
    for w in words:
        if cur and (len(cur) >= 3 or len(" ".join(cur + [w])) > 20):
            groups.append(cur)
            cur = []
        cur.append(w)
        if w[-1] in ".?!,:" and len(cur) >= 2:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    total = sum(len(" ".join(g)) + 4 for g in groups)
    t, out = start, []
    for g in groups:
        d = dur * (len(" ".join(g)) + 4) / total
        out.append((t, d, " ".join(g)))
        t += d
    return out


def cap_html(s):
    s = html.escape(s)
    # numbers, prices and ALL-CAPS words pop in yellow
    return re.sub(r"(\d[\d,]*\s?(?:baht|฿)?|\b[A-Z]{3,}\b|“[^”]+”)", r'<em>\1</em>', s)


# ---------------------------------------------------------------- html
CSS = """
@font-face{font-family:Lucky;src:url(FONTS/LuckiestGuy.ttf)}
@font-face{font-family:Prompt;font-weight:500;src:url(FONTS/Prompt-Medium.ttf)}
@font-face{font-family:Prompt;font-weight:700;src:url(FONTS/Prompt-Bold.ttf)}
@font-face{font-family:Prompt;font-weight:800;src:url(FONTS/Prompt-ExtraBold.ttf)}
@font-face{font-family:Prompt;font-weight:900;src:url(FONTS/Prompt-Black.ttf)}
:root{--red:#8a0d0d;--deep:#4d0404;--yel:#ffe14d;--lime:#d9f47a;--cream:#fff7ea}
*{box-sizing:border-box}
body{margin:0;width:1080px;height:1920px;overflow:hidden;background:var(--deep);font-family:Prompt,'Noto Color Emoji';color:#fff}
.seg{position:absolute;inset:0;opacity:0;animation-name:vis;animation-timing-function:linear;animation-fill-mode:none}
@keyframes vis{from{opacity:1}to{opacity:1}}
.bg{position:absolute;inset:-2%;overflow:hidden}
.bg img{width:100%;height:100%;object-fit:cover;animation-name:kb;animation-timing-function:cubic-bezier(.3,.1,.4,1);animation-fill-mode:both}
@keyframes kb{from{transform:scale(var(--z0))}to{transform:scale(var(--z1))}}
.blur img{filter:blur(38px) brightness(.55) saturate(1.3);transform:scale(1.25)!important}
.card{position:absolute;left:70px;right:70px;top:330px;height:1000px;border-radius:44px;overflow:hidden;border:10px solid var(--cream);
 box-shadow:0 30px 80px rgba(0,0,0,.55);animation-name:cardin;animation-duration:.5s;animation-timing-function:cubic-bezier(.2,1.5,.4,1);animation-fill-mode:both}
@keyframes cardin{from{transform:translateY(240px) rotate(6deg) scale(.7);opacity:0}to{transform:rotate(-2deg);opacity:1}}
.card img{width:100%;height:100%;object-fit:cover;animation-name:kb;animation-timing-function:linear;animation-fill-mode:both}
.shade{position:absolute;inset:0;background:linear-gradient(rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 26%,rgba(0,0,0,0) 52%,rgba(0,0,0,.72) 100%)}
.shake{animation-name:shake;animation-duration:.5s;animation-fill-mode:both}
@keyframes shake{0%,100%{transform:none}15%{transform:translate(-18px,10px) rotate(-1deg)}30%{transform:translate(16px,-12px) rotate(1deg)}
 45%{transform:translate(-12px,-6px)}60%{transform:translate(10px,8px)}80%{transform:translate(-4px,2px)}}
.brand{position:absolute;left:56px;top:84px;display:flex;align-items:center;gap:18px;z-index:5}
.brand img{width:104px;height:104px;border-radius:50%;border:5px solid var(--cream);object-fit:cover;object-position:50% 30%;background:#fff}
.brand b{font-family:Lucky;font-size:58px;line-height:1;color:var(--cream);text-shadow:0 4px 0 var(--red),0 8px 18px rgba(0,0,0,.5);display:block}
.brand span{font-weight:700;font-size:28px;color:var(--lime);text-shadow:0 2px 8px rgba(0,0,0,.8)}
.dish{position:absolute;left:56px;top:226px;background:var(--red);color:var(--cream);font-weight:900;font-size:44px;padding:6px 26px 4px;
 border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,.4);animation:slide .45s cubic-bezier(.2,1.4,.4,1) both}
.dish small{font-weight:700;color:var(--lime);font-size:36px;margin-left:12px}
@keyframes slide{from{transform:translateX(-700px)}to{transform:none}}
.title{position:absolute;left:40px;right:120px;top:300px;text-align:center;font-family:Lucky,Prompt,'Noto Color Emoji';font-size:138px;line-height:1.02;
 color:var(--yel);-webkit-text-stroke:14px var(--deep);paint-order:stroke fill;text-shadow:0 14px 0 var(--deep),0 20px 40px rgba(0,0,0,.6);
 animation:slam .45s cubic-bezier(.2,1.6,.4,1) both;white-space:pre-line}
@keyframes slam{from{transform:scale(2.6) rotate(-6deg);opacity:0}to{transform:rotate(-2deg);opacity:1}}
.th{position:absolute;left:0;right:80px;top:660px;text-align:center;animation:up .4s cubic-bezier(.2,1.4,.4,1) both}
.th span{display:inline-block;background:var(--red);color:#fff;font-weight:800;font-size:56px;padding:10px 34px 6px;border-radius:999px;
 border:5px solid var(--cream);box-shadow:0 10px 30px rgba(0,0,0,.45)}
@keyframes up{from{transform:translateY(120px);opacity:0}to{transform:none;opacity:1}}
.chips{position:absolute;left:56px;top:330px;display:flex;flex-direction:column;align-items:flex-start;gap:22px}
.chip{background:var(--cream);color:#2a0505;font-weight:800;font-size:54px;padding:12px 34px 8px;border-radius:999px;
 box-shadow:0 12px 30px rgba(0,0,0,.45);border-left:16px solid var(--red);animation:pop .4s cubic-bezier(.2,1.7,.4,1) both}
.card ~ .chips{top:auto;bottom:640px;left:36px}
.card ~ .chips .chip{font-size:46px}
@keyframes pop{from{transform:scale(0) rotate(-8deg);opacity:0}to{transform:none;opacity:1}}
.opt-h{position:absolute;left:0;right:60px;top:320px;text-align:center;font-family:Lucky;font-size:96px;color:var(--yel);
 -webkit-text-stroke:12px var(--deep);paint-order:stroke fill;text-shadow:0 10px 0 var(--deep);animation:slam .4s cubic-bezier(.2,1.6,.4,1) both}
.opt-h small{display:block;font-family:Prompt;font-weight:800;font-size:48px;color:#fff;-webkit-text-stroke:0;text-shadow:0 3px 12px #000}
.opts{position:absolute;left:60px;right:120px;top:560px;display:flex;flex-wrap:wrap;justify-content:center;gap:24px}
.opt{background:var(--red);color:var(--yel);font-weight:900;font-size:60px;padding:14px 40px 10px;border-radius:26px;border:6px solid var(--yel);
 box-shadow:0 12px 30px rgba(0,0,0,.5);animation:pop .4s cubic-bezier(.2,1.7,.4,1) both}
.sticker{position:absolute;left:150px;top:420px;width:720px;height:720px;animation:spin .6s cubic-bezier(.2,1.5,.4,1) both}
.sticker svg{position:absolute;inset:0;filter:drop-shadow(0 24px 40px rgba(0,0,0,.6))}
.sticker .in{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--deep);transform:rotate(-8deg)}
.sticker .lab{font-family:Lucky;font-size:84px;line-height:1;margin-bottom:-10px}
.sticker .num{font-family:Lucky;font-size:300px;line-height:.9;display:flex;align-items:flex-start}
.sticker .num i{font-family:Prompt;font-style:normal;font-weight:900;font-size:130px;margin-top:20px;margin-left:6px}
@keyframes spin{from{transform:scale(0) rotate(-200deg)}to{transform:none}}
.pulse{animation:pulse 1s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
.pth{position:absolute;left:0;right:0;top:1150px;text-align:center;animation:up .4s cubic-bezier(.2,1.4,.4,1) both}
.pth span{display:inline-block;background:var(--cream);color:var(--red);font-weight:900;font-size:62px;padding:10px 40px 6px;border-radius:999px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
.caps{position:absolute;left:50px;right:110px;top:1330px;height:240px}
.cap{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;opacity:0;
 font-weight:900;font-size:78px;line-height:1.12;color:#fff;-webkit-text-stroke:12px #000;paint-order:stroke fill;
 text-shadow:0 6px 18px rgba(0,0,0,.6);animation-name:capv;animation-fill-mode:none;animation-timing-function:linear}
.cap em{font-style:normal;color:var(--yel)}
@keyframes capv{0%{opacity:1;transform:scale(.82)}10%{transform:scale(1.04)}18%,100%{opacity:1;transform:scale(1)}}
.flash{position:absolute;inset:0;background:#fff;opacity:0;animation:flash .22s ease-out forwards;z-index:20;pointer-events:none}
@keyframes flash{from{opacity:.75}to{opacity:0}}
.cta-bg{position:absolute;inset:0;background:radial-gradient(circle at 50% 30%,rgba(138,13,13,.55),rgba(40,0,0,.92))}
.mascot{position:absolute;left:230px;top:150px;width:620px;height:620px;border-radius:50%;overflow:hidden;border:12px solid var(--cream);
 box-shadow:0 30px 80px rgba(0,0,0,.6);animation:spin .6s cubic-bezier(.2,1.4,.4,1) both;background:#fff}
.mascot img{width:100%;height:100%;object-fit:cover}
.logo{position:absolute;left:0;right:0;top:790px;text-align:center;font-family:Lucky;font-size:190px;line-height:1;color:var(--cream);
 text-shadow:0 12px 0 var(--red),0 20px 40px rgba(0,0,0,.6);animation:slam .45s cubic-bezier(.2,1.6,.4,1) both}
.sub{position:absolute;left:0;right:0;top:990px;text-align:center;font-weight:800;font-size:52px;color:var(--lime);animation:up .4s both}
.thc{position:absolute;left:0;right:0;top:1080px;text-align:center;animation:up .4s cubic-bezier(.2,1.4,.4,1) both}
.thc span{display:inline-block;background:var(--yel);color:var(--deep);font-weight:900;font-size:62px;padding:10px 40px 6px;border-radius:999px}
.eng{position:absolute;left:60px;right:120px;top:1230px;text-align:center;font-weight:900;font-size:66px;line-height:1.15;color:#fff;
 -webkit-text-stroke:10px #000;paint-order:stroke fill;animation:pop .45s cubic-bezier(.2,1.6,.4,1) both}
.eng small{display:block;font-weight:700;font-size:46px;color:var(--lime);-webkit-text-stroke:0;margin-top:14px}
"""

STAR = ('<svg viewBox="-100 -100 200 200"><polygon fill="#ffe14d" stroke="#4d0404" stroke-width="5" points="{}"/>'
        '<circle r="70" fill="none" stroke="#8a0d0d" stroke-width="3" stroke-dasharray="6 5"/></svg>')


def star_points(n=18, r1=96, r2=82):
    pts = []
    for i in range(n * 2):
        a = np.pi * i / n
        r = r1 if i % 2 == 0 else r2
        pts.append(f"{r * np.sin(a):.1f},{-r * np.cos(a):.1f}")
    return " ".join(pts)


def A(name, start, dur=None, extra=""):
    """inline animation timing"""
    d = f"animation-delay:{start:.3f}s;"
    if dur is not None:
        d += f"animation-duration:{dur:.3f}s;"
    return d + extra


def build_html(reel, segs, img_url, mascot_url, sfx):
    b = CFG["brand"]
    parts = []
    for i, s in enumerate(segs):
        t0, d = s["t0"], s["dur"]
        z0, z1 = s.get("zoom", [1.2, 1.4])
        fx, fy = s.get("focus", [50, 50])
        kb = f"--z0:{z0};--z1:{z1};transform-origin:{fx}% {fy}%;object-position:{fx}% {fy}%;"
        inner = []
        typ = s["type"]
        if typ == "cta":
            inner.append(f'<div class="bg blur"><img src="{img_url}"></div><div class="cta-bg"></div>')
            inner.append(f'<div class="mascot" style="{A("", t0 + .05)}"><img src="{mascot_url}"></div>')
            inner.append(f'<div class="logo" style="{A("", t0 + .35)}">{b["name"]}</div>')
            inner.append(f'<div class="sub" style="{A("", t0 + .6)}">{html.escape(b["tag"])} 🇰🇷</div>')
            inner.append(f'<div class="thc" style="{A("", t0 + .8)}"><span>{b["th_cta"]}</span></div>')
            inner.append(f'<div class="eng" style="{A("", t0 + 1.1)}">{cap_html(s.get("cap", s["say"]))}'
                         f'<small>{b["th_tag"]}</small></div>')
            sfx += [(t0, "boom", .8), (t0 + .35, "pop", .6), (t0 + 1.1, "pop", .6)]
        else:
            if s.get("mode") == "card":
                inner.append(f'<div class="bg blur"><img src="{img_url}"></div>')
                inner.append(f'<div class="card" style="{A("", t0)}"><img src="{img_url}" style="{kb}{A("", t0, d)}"></div>')
            else:
                shake = ' shake' if s.get("shake") else ''
                inner.append(f'<div class="bg{shake}" style="{A("", t0 + .1) if shake else ""}">'
                             f'<img src="{img_url}" style="{kb}{A("", t0, d)}"></div>')
            inner.append('<div class="shade"></div>')
            inner.append(f'<div class="brand"><img src="{mascot_url}"><div><b>{b["name"]}</b><span>Korean Food</span></div></div>')
            if typ == "hook":
                inner.append(f'<div class="title" style="{A("", t0 + .05)}">{html.escape(s["title"])}</div>')
                inner.append(f'<div class="th" style="{A("", t0 + .5)}"><span>{s["th"]}</span></div>')
                sfx += [(t0 + .05, "boom", 1.0), (t0 + .5, "pop", .5)]
            else:
                inner.append(f'<div class="dish" style="{A("", t0)}">{reel["name"]}<small>{reel["th_name"]}</small></div>')
            if typ == "feature":
                cs = "".join(f'<div class="chip" style="{A("", t0 + .35 + k * .38)}">{html.escape(c)}</div>'
                             for k, c in enumerate(s["chips"]))
                inner.append(f'<div class="chips">{cs}</div>')
                sfx += [(t0 + .35 + k * .38, "pop", .55) for k in range(len(s["chips"]))]
            if typ == "options":
                inner.append(f'<div class="opt-h" style="{A("", t0 + .05)}">PICK YOURS<small>เลือกได้ตามใจ</small></div>')
                os_ = "".join(f'<div class="opt" style="{A("", t0 + .35 + k * .22)}">{html.escape(o)}</div>'
                              for k, o in enumerate(s["options"]))
                inner.append(f'<div class="opts">{os_}</div>')
                sfx += [(t0 + .35 + k * .22, "pop", .5) for k in range(len(s["options"]))]
            if typ == "price":
                lab = "FROM" if s.get("from") else "ONLY"
                th = ("เริ่มต้น " if s.get("from") else "เพียง ") + s["price"] + " บาท"
                inner.append(f'<div class="sticker" style="{A("", t0 + .1)}"><div class="pulse" style="position:absolute;inset:0;{A("", t0 + .7)}">'
                             f'{STAR.format(star_points())}<div class="in"><div class="lab">{lab}</div>'
                             f'<div class="num">{s["price"]}<i>฿</i></div></div></div></div>')
                inner.append(f'<div class="pth" style="{A("", t0 + .6)}"><span>{th}</span></div>')
                sfx += [(t0 + .1, "whoosh", .7), (t0 + .5, "ding", 1.0)]
            # spoken captions
            caps = "".join(f'<div class="cap" style="{A("", ct, cd)}"><span>{cap_html(txt)}</span></div>'
                           for ct, cd, txt in chunks(s.get("cap", s["say"]), s["vdur"], s["vt"]))
            inner.append(f'<div class="caps">{caps}</div>')
        parts.append(f'<div class="seg" style="{A("", t0, d)}">{"".join(inner)}</div>')
        if i > 0:
            parts.append(f'<div class="flash" style="{A("", t0)}"></div>')
            if typ not in ("cta",):
                sfx.append((t0 - .12, "whoosh", .45))
    css = CSS.replace("FONTS", (ROOT / "fonts").as_uri())
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(parts)}</body></html>'


# ---------------------------------------------------------------- build one reel
def build(reel):
    rid = reel["id"]
    wd = WORK / rid
    wd.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    print(f"== {rid}")

    src = Image.open(ROOT / "assets" / "menu" / f"{reel['img']}.jpg").convert("RGB")
    if reel.get("crop_top"):
        src = src.crop((0, int(src.height * reel["crop_top"]), src.width, src.height))
    img = wd / "dish.jpg"
    src.save(img, quality=95)

    # voice per segment
    segs, t, sr = [], 0.0, 24000
    voice_parts = []
    for i, s in enumerate(reel["segments"]):
        s = dict(s)
        if s["type"] == "price" and "cap" not in s:
            s["cap"] = ("From " if s.get("from") else "Only ") + s["price"] + " baht"
        say = s["say"] + (CTA_TAIL if s["type"] == "cta" else "")
        a, sr = tts(say, wd / f"v{i}.wav")
        vd = len(a) / sr
        lead = 0.15 if i == 0 else (0.45 if s["type"] in ("price", "cta") else 0.25)
        tail = {"hook": 0.35, "price": 0.7, "cta": 2.6}.get(s["type"], 0.3)
        dur = max(lead + vd + tail, {"hook": 2.4, "price": 2.4, "options": 2.6}.get(s["type"], 2.2))
        s.update(t0=t, dur=dur, vt=t + lead, vdur=vd)
        if s["type"] == "cta":
            s["vdur"] = len(tts(s["say"], wd / "cap.wav")[0]) / sr
        voice_parts.append((t + lead, a))
        segs.append(s)
        t += dur
    total = round(t, 3)

    vtrack = np.zeros(int((total + .5) * sr), dtype=np.float32)
    for at, a in voice_parts:
        p = int(at * sr)
        vtrack[p:p + len(a)] += a[: len(vtrack) - p]
    sf.write(wd / "voice.wav", vtrack[: int(total * sr)], sr)

    sfx = []
    page = build_html(reel, segs, img.as_uri(), (ROOT / "assets" / "menu" / "mascot.jpg").as_uri(), sfx)
    (wd / "reel.html").write_text(page)

    # audio: voice + ducked music + sfx
    audio.make_music(total, wd / "music.wav", shift=reel.get("shift", 0), seed=reel.get("seed", 3))
    audio.make_sfx_track(sfx, total, wd / "sfx.wav")
    fc = (f"[0:a]apad,atrim=0:{total},aresample=48000,loudnorm=I=-16:TP=-2,asplit=2[v][sc];"
          f"[1:a]apad,atrim=0:{total}[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=500[m];"
          "[2:a]volume=0.55[s];[v][m][s]amix=inputs=3:duration=longest:normalize=0,"
          f"loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.95,apad,atrim=0:{total}[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wd / "voice.wav"), "-i", str(wd / "music.wav"),
                    "-i", str(wd / "sfx.wav"), "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-ac", "2",
                    str(wd / "mix.wav")], check=True)

    # video
    jobs = [{"html": str(wd / "reel.html"), "mp4": str(wd / "video.mp4"), "w": W, "h": H, "dur": total, "fps": FPS,
             "preset": "medium"}]
    (wd / "jobs.json").write_text(json.dumps(jobs))
    subprocess.run(["node", str(REPO / "pipeline" / "render.js"), str(wd / "jobs.json")], check=True)
    print()

    out = OUT / f"{rid}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wd / "video.mp4"), "-i", str(wd / "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(out)], check=True)
    hook_t = segs[0]["t0"] + 1.3
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{hook_t:.2f}", "-i", str(wd / "video.mp4"), "-frames:v", "1",
                    "-q:v", "2", str(OUT / f"{rid}-cover.jpg")], check=True)
    print(f"   {out.name}  {total:.1f}s")
    return total


def captions(durs):
    lines = ["# MANSE Korean Food: Facebook Reels captions", "",
             "Copy the caption under each reel when you upload it. Replace `[your area]` with your neighbourhood or city.", ""]
    base = "#ManseKoreanFood #KoreanFood #อาหารเกาหลี #ร้านอาหารเกาหลี #KoreanFoodThailand #ของอร่อย #reels"
    for r in CFG["reels"]:
        if r["id"] not in durs:
            continue
        lines += [f"## {r['id']}.mp4  ({durs[r['id']]:.0f}s)", f"Angle: {r['angle']}", "", "```",
                  r["caption_en"], "", r["caption_th"], "",
                  "📍 MANSE Korean Food, [your area]", f"{r['tags']} {base}", "```", ""]
    (OUT / "CAPTIONS.md").write_text("\n".join(lines))


if __name__ == "__main__":
    want = sys.argv[1:]
    durs = {}
    for r in CFG["reels"]:
        if not want or any(r["id"].startswith(w) for w in want):
            durs[r["id"]] = build(r)
    if not want:
        captions(durs)
