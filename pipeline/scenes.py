"""HTML templates for every scene type, in landscape (16:9) and vertical (9:16), with animation.

Animation model: render.js freezes all CSS animations and steps them frame by frame.
- Entrance animations play when a scene starts (body.enter).
- A newly revealed item (bullet, bubble, box) pops in (.newi).
- Scene-long motion (photo Ken Burns, map zoom, particles) uses --t0 / --sd so it continues
  smoothly across the several segments a scene is split into.
"""
import html
import json
import math
import random
import re
from pathlib import Path

from art import ART

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"

COLORS = {
    "bg": "#0e141b",
    "panel": "#16202b",
    "land": "#26384a",
    "land_line": "#0e141b",
    "neighbour": "#1a242f",
    "neighbour_line": "#2b3947",
    "text": "#f3efe6",
    "muted": "#a9b4bf",
    "gold": "#e8b04b",
    "red": "#d1495b",
    "green": "#3fa87a",
    "blue": "#4a8fd6",
}

e = lambda s: html.escape(str(s or ""))
BRAND = "Myanmar <b>Stories</b>"
CTX = {}  # set by render_scene: enter, new, t0, sd, hook_enter


def css(orient):
    v = orient == "v"
    scene_long = "animation-delay: calc(var(--t0) * -1s); animation-duration: calc(var(--sd) * 1s); animation-timing-function: linear; animation-fill-mode: both;"
    return f"""
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-Regular.otf'); font-weight: 400; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-SemiBold.otf'); font-weight: 600; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-Bold.otf'); font-weight: 700; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-ExtraBold.otf'); font-weight: 800; }}
@font-face {{ font-family: MM; src: url('file://{FONTS}/NotoSansMyanmar-Regular.ttf'); font-weight: 400; }}
@font-face {{ font-family: MM; src: url('file://{FONTS}/NotoSansMyanmar-Bold.ttf'); font-weight: 700; }}
@property --n {{ syntax: '<integer>'; inherits: false; initial-value: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; height: 100%; overflow: hidden; }}
body {{ background: {COLORS['bg']}; color: {COLORS['text']}; font-family: Inter, MM, sans-serif; position: relative; }}

/* ---------- backgrounds ---------- */
.amb {{ position: absolute; inset: -20%; background:
    radial-gradient(circle at 30% 40%, rgba(232,176,75,.10), transparent 35%),
    radial-gradient(circle at 75% 65%, rgba(209,73,91,.10), transparent 40%),
    radial-gradient(ellipse at 60% 30%, #17222e 0%, {COLORS['bg']} 65%);
  animation-name: ambmove; {scene_long} }}
@keyframes ambmove {{ from {{ transform: translate(-3%, -2%) rotate(0deg); }} to {{ transform: translate(3%, 2%) rotate(4deg); }} }}
.bgimg {{ position: absolute; inset: 0; background-size: cover; filter: saturate(.92) contrast(1.08) brightness(.95);
  animation-name: kb; {scene_long} }}
@keyframes kb {{ from {{ transform: scale(1.16) translate(var(--kx), var(--ky)); }} to {{ transform: scale(1.02) translate(0, 0); }} }}
.shade {{ position: absolute; inset: 0; }}
.vignette {{ position: absolute; inset: 0; background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,.55) 100%); }}
.grain {{ position: absolute; inset: 0; background-image: radial-gradient(rgba(255,255,255,.03) 1px, transparent 1px);
  background-size: 5px 5px; pointer-events: none; }}
.p {{ position: absolute; border-radius: 50%; background: rgba(255,236,200,.55); filter: blur(1px);
  animation-name: drift; {scene_long} }}
@keyframes drift {{ from {{ transform: translate(0, 0); opacity: 0; }} 15% {{ opacity: var(--o); }} 85% {{ opacity: var(--o); }} to {{ transform: translate(var(--dx), var(--dy)); opacity: 0; }} }}
.credit {{ position: absolute; {'top: 262px; right: 40px;' if v else 'bottom: 14px; right: 24px;'} font-size: {18 if v else 15}px; color: rgba(255,255,255,.55); }}
.fade {{ position: absolute; inset: 0; background: #000; pointer-events: none; opacity: 0; }}
body.enter .fade {{ animation: fadeout .5s ease-out both; }}
@keyframes fadeout {{ from {{ opacity: 1; }} to {{ opacity: 0; }} }}

/* ---------- text & layout ---------- */
.brand {{ position: absolute; {'top: 60px; left: 0; right: 0; text-align: center;' if v else 'top: 44px; left: 64px;'}
  font-size: {26 if v else 20}px; letter-spacing: .14em; text-transform: uppercase; color: {COLORS['muted']}; font-weight: 600; }}
.brand b {{ color: {COLORS['gold']}; }}
.source {{ position: absolute; {'top: 262px; left: 40px; right: 560px; text-align: left; font-size: 18px !important;' if v else 'top: 44px; right: 64px; text-align: right; max-width: 700px;'}
  font-size: {24 if v else 19}px; color: {COLORS['muted']}; }}
.hook {{ position: absolute; top: 100px; left: 50px; right: 50px; text-align: center; font-weight: 800;
  font-size: 62px; line-height: 1.08; color: {COLORS['text']}; text-shadow: 0 4px 24px rgba(0,0,0,.6); }}
.hook span {{ color: #111; background: {COLORS['gold']}; padding: 0 12px; border-radius: 8px; box-decoration-break: clone; -webkit-box-decoration-break: clone; }}
body.hookenter .hook {{ animation: pop .6s cubic-bezier(.2,.9,.3,1.3) both; }}
.mapbox {{ -webkit-mask-image: radial-gradient(ellipse 72% 72% at 50% 50%, #000 72%, transparent 100%); }}
.mapbox svg {{ animation-name: mapzoom; {scene_long} transform-origin: 50% 50%; }}
@keyframes mapzoom {{ from {{ transform: scale(1); }} to {{ transform: scale(1.08); }} }}
.kicker {{ color: {COLORS['gold']}; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; font-size: {32 if v else 26}px; }}
h1 {{ font-weight: 800; letter-spacing: -.02em; line-height: 1.05; text-shadow: 0 6px 30px rgba(0,0,0,.45); }}
h2 {{ font-weight: 800; letter-spacing: -.015em; line-height: 1.1; font-size: {66 if v else 64}px; text-shadow: 0 4px 24px rgba(0,0,0,.45); }}
.muted {{ color: {COLORS['muted']}; }}
.stage {{ position: absolute; {'top: 300px; bottom: 830px; left: 70px; right: 70px;' if v else 'top: 120px; bottom: 210px; left: 110px; right: 110px;'} }}

/* ---------- motion ---------- */
@keyframes rise {{ from {{ opacity: 0; transform: translateY(46px); filter: blur(12px); }} }}
@keyframes pop {{ 0% {{ opacity: 0; transform: scale(.82) translateY(24px); }} 60% {{ opacity: 1; transform: scale(1.04); }} }}
@keyframes flash {{ 0% {{ box-shadow: 0 0 0 0 rgba(232,176,75,.7); }} 100% {{ box-shadow: 0 0 0 26px rgba(232,176,75,0); }} }}
@keyframes grow {{ from {{ transform: scaleX(0); }} }}
@keyframes count {{ from {{ --n: var(--from); }} to {{ --n: var(--to); }} }}
@keyframes pulse {{ 0% {{ transform: scale(.6); opacity: .9; }} 100% {{ transform: scale(3.4); opacity: 0; }} }}
@keyframes shake {{ 0%, 24%, 100% {{ transform: rotate(0); }} 3% {{ transform: rotate(-3deg); }} 6% {{ transform: rotate(3deg); }}
  9% {{ transform: rotate(-3deg); }} 12% {{ transform: rotate(3deg); }} 15% {{ transform: rotate(-2deg); }} 18% {{ transform: rotate(2deg); }} }}
@keyframes wave {{ 0% {{ transform: scale(1); opacity: .7; }} 100% {{ transform: scale(2.4); opacity: 0; }} }}
@keyframes typing {{ 0% {{ opacity: 0; }} 12% {{ opacity: 1; }} 88% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
@keyframes dot {{ 0%, 100% {{ transform: translateY(0); opacity: .4; }} 50% {{ transform: translateY(-8px); opacity: 1; }} }}
@keyframes ghost {{ from {{ transform: translate(-50%, -50%) scale(1.15); opacity: 0; }} to {{ transform: translate(-50%, -50%) scale(1); opacity: .06; }} }}
@keyframes dash {{ to {{ stroke-dashoffset: -26; }} }}
@keyframes travel {{ 0% {{ stroke-dashoffset: 0; opacity: 0; }} 10% {{ opacity: 1; }} 90% {{ opacity: 1; }} 100% {{ stroke-dashoffset: calc(var(--L) * -1px); opacity: 0; }} }}
@keyframes hlin {{ from {{ fill: {COLORS['land']}; }} }}
body.enter .stage > *, body.enter .col > * {{ animation: rise .9s cubic-bezier(.2,.8,.2,1) both; }}
body.enter .stage > *:nth-child(2), body.enter .col > *:nth-child(2) {{ animation-delay: .12s; }}
body.enter .stage > *:nth-child(3), body.enter .col > *:nth-child(3) {{ animation-delay: .24s; }}
body.enter .stage > *:nth-child(4), body.enter .col > *:nth-child(4) {{ animation-delay: .36s; }}
body.enter .stage > *:nth-child(5), body.enter .col > *:nth-child(5) {{ animation-delay: .48s; }}
body.enter .stage > *:nth-child(6), body.enter .col > *:nth-child(6) {{ animation-delay: .60s; }}
body.enter .stage > *:nth-child(n+7) {{ animation-delay: .72s; }}
.newi {{ animation: pop .6s cubic-bezier(.2,.9,.3,1.2) both; }}
.newi .badge {{ animation: flash .9s .2s ease-out both; }}
body.enter .line {{ animation: grow .8s .3s cubic-bezier(.2,.8,.2,1) both; transform-origin: left; }}
body.enter .artwrap {{ animation: pop 1s .25s cubic-bezier(.2,.9,.3,1.1) both; }}
body.enter .phonewrap {{ animation: pop .8s cubic-bezier(.2,.9,.3,1.1) both; }}
.count {{ counter-reset: n var(--n); }}
.count::after {{ content: counter(n); }}
body.enter .count {{ animation: count 1.6s .2s cubic-bezier(.15,.8,.25,1) both; }}
.ring {{ transform-box: fill-box; transform-origin: center; animation: pulse 1.8s ease-out infinite; }}
body.enter .hl {{ animation: hlin 1.4s .3s ease-out both; }}
.shaking {{ animation: shake 1.6s infinite; transform-origin: 50% 60%; }}
.answer {{ position: relative; }}
.answer::before, .answer::after {{ content: ''; position: absolute; inset: 0; border-radius: 50%; border: 4px solid {COLORS['green']}; animation: wave 1.6s ease-out infinite; }}
.answer::after {{ animation-delay: .8s; }}
.typing {{ position: absolute; left: 0; top: 22px; padding: 26px 30px; border-radius: 26px; background: #2a3542; display: flex; gap: 10px; animation: typing .75s both; }}
.typing i {{ width: 14px; height: 14px; border-radius: 50%; background: #c6d0da; animation: dot .5s infinite; }}
.typing i:nth-child(2) {{ animation-delay: .12s; }} .typing i:nth-child(3) {{ animation-delay: .24s; }}
.newb {{ animation: pop .45s .75s cubic-bezier(.2,.9,.3,1.2) both; }}
.ghostnum {{ position: absolute; left: 50%; top: 50%; font-size: {700 if v else 760}px; font-weight: 800; color: #fff; opacity: .06; transform: translate(-50%, -50%);
  letter-spacing: -.06em; }}
body.enter .ghostnum {{ animation: ghost 1.4s cubic-bezier(.2,.8,.2,1) both; }}
"""


def _particles(n, w, h, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        s = rnd.uniform(2, 6)
        out.append(f"<div class='p' style='left:{rnd.uniform(0, w):.0f}px;top:{rnd.uniform(0, h):.0f}px;width:{s:.1f}px;height:{s:.1f}px;"
                   f"--dx:{rnd.uniform(-120, 120):.0f}px;--dy:{rnd.uniform(-220, -60):.0f}px;--o:{rnd.uniform(.25, .7):.2f}'></div>")
    return "".join(out)


def page(orient, body, source="", hook="", brand=True, bg=None, seed=0, shade=None):
    v = orient == "v"
    W, H = (1080, 1920) if v else (1920, 1080)
    t0, sd = CTX.get("t0", 0), max(CTX.get("sd", 6), 0.1)
    cls = " ".join(c for c, on in (("enter", CTX.get("enter")), ("hookenter", CTX.get("hook_enter"))) if on)
    parts = [f"<!doctype html><html><head><meta charset='utf-8'><style>{css(orient)}</style></head>"
             f"<body class='{cls}' style='--t0:{t0:.3f};--sd:{sd:.3f}'>"]
    if bg:
        rnd = random.Random(seed)
        kx, ky = rnd.choice([-1, 1]) * rnd.uniform(1.5, 3.5), rnd.choice([-1, 1]) * rnd.uniform(1, 2.5)
        parts.append(f"<div class='bgimg' style=\"background-image:url('file://{bg['src']}');background-position:{bg.get('pos', 'center')};--kx:{kx:.1f}%;--ky:{ky:.1f}%\"></div>")
        dark = bg.get("dim", 0.5)
        if v:
            grad = (f"linear-gradient(180deg, rgba(14,20,27,{min(1, dark + .25)}) 0%, rgba(14,20,27,{dark - .2}) 22%, "
                    f"rgba(14,20,27,{dark - .15}) 45%, rgba(14,20,27,{min(1, dark + .3)}) 70%, rgba(14,20,27,.95) 100%)")
        else:
            grad = (shade or f"linear-gradient(90deg, rgba(14,20,27,{min(1, dark + .3)}) 0%, rgba(14,20,27,{dark}) 50%, rgba(14,20,27,{max(0, dark - .25)}) 100%)")
            grad += ", linear-gradient(0deg, rgba(14,20,27,.85) 0%, rgba(14,20,27,0) 30%)"
        parts.append(f"<div class='shade' style='background:{grad}'></div><div class='vignette'></div>")
    else:
        parts.append("<div class='amb'></div><div class='vignette'></div>")
    parts.append("<div class='grain'></div>")
    parts.append(_particles(26 if not v else 22, W, H, seed))
    if brand and not hook:
        parts.append(f"<div class='brand'>{BRAND}</div>")
    if hook:
        parts.append(f"<div class='hook'>{hook}</div>")
    parts.append(body)
    if source:
        parts.append(f"<div class='source'>Source: {e(source)}</div>")
    if bg and bg.get("credit"):
        parts.append(f"<div class='credit'>Photo: {e(bg['credit'])}</div>")
    parts.append("<div class='fade'></div></body></html>")
    return "".join(parts)


# ---------------------------------------------------------------- map
_GEO = None


def _geo():
    global _GEO
    if _GEO is None:
        regions = json.load(open(HERE / "data" / "myanmar_regions.geojson"))
        neighbours = json.load(open(HERE / "data" / "neighbours.geojson"))
        _GEO = (regions, neighbours)
    return _GEO


def _polys(geom):
    return geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]


LABEL_POS = {  # hand-tuned label anchors (lon, lat)
    "Kachin": (97.4, 26.2), "Sagaing": (95.2, 23.6), "Chin": (93.5, 22.2), "Shan": (98.2, 21.4),
    "Mandalay": (95.9, 21.3), "Magway": (94.6, 20.4), "Rakhine": (93.6, 19.6), "Kayah": (97.25, 19.25),
    "Bago": (96.0, 18.3), "Ayeyarwady": (95.0, 16.9), "Yangon": (96.2, 16.95), "Kayin": (97.9, 17.3),
    "Mon": (97.6, 15.9), "Tanintharyi": (98.7, 12.6),
}
COUNTRY_POS = {"Thailand": (100.6, 16.0), "China": (100.5, 25.8), "India": (93.2, 26.6),
               "Bangladesh": (90.6, 23.4), "Laos": (102.2, 20.5)}


def _q(x1, y1, mx, my, x2, y2, t):
    return ((1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2, (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2)


def map_svg(scene, w, h, focus=None):
    """Myanmar map. focus=(lon_min, lat_min, lon_max, lat_max) zooms in."""
    regions, neighbours = _geo()
    lon0, lat0, lon1, lat1 = focus or scene.get("focus") or (91.6, 9.4, 101.9, 28.8)
    k = math.cos(math.radians((lat0 + lat1) / 2))
    gw, gh = (lon1 - lon0) * k, (lat1 - lat0)
    s = min(w / gw, h / gh)
    ox, oy = (w - gw * s) / 2, (h - gh * s) / 2
    P = lambda lon, lat: (ox + (lon - lon0) * k * s, oy + (lat1 - lat) * s)

    def path(geom):
        d = []
        for poly in _polys(geom):
            for ring in poly:
                pts = [P(*c) for c in ring]
                d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
        return "".join(d)

    hl = scene.get("highlight", {})
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"]
    for f in neighbours["features"]:
        if f["properties"]["iso"] == "MMR":
            continue
        out.append(f"<path d='{path(f['geometry'])}' fill='{COLORS['neighbour']}' stroke='{COLORS['neighbour_line']}' stroke-width='2'/>")
    if scene.get("countries", True):
        for name, (lo, la) in COUNTRY_POS.items():
            x, y = P(lo, la)
            if 0 < x < w and 0 < y < h:
                out.append(f"<text x='{x:.0f}' y='{y:.0f}' fill='#4d5d6d' font-size='{min(30, max(16, s*0.32)):.0f}' font-weight='700' letter-spacing='4' text-anchor='middle'>{name.upper()}</text>")
    for f in regions["features"]:
        name = f["properties"]["name"]
        c = hl.get(name)
        fill = COLORS.get(c, c) if c else COLORS["land"]
        dim = hl and not c and scene.get("dim_others", True)
        out.append(f"<path class='{'hl' if c else ''}' d='{path(f['geometry'])}' fill='{fill}' fill-opacity='{0.55 if dim else 1}' stroke='{COLORS['land_line']}' stroke-width='2.2' stroke-linejoin='round'/>")
    if scene.get("labels", True):
        fs = min(30, max(14, s * 0.27))
        for f in regions["features"]:
            name = f["properties"]["name"]
            if scene.get("labels") not in (True, None) and name not in scene["labels"]:
                continue
            lo, la = LABEL_POS.get(name, (None, None))
            if lo is None:
                continue
            x, y = P(lo, la)
            on = name in hl
            out.append(f"<text x='{x:.0f}' y='{y:.0f}' fill='{'#fff' if on else '#b7c2cc'}' font-size='{fs*(1.12 if on else 1):.0f}' font-weight='{700 if on else 600}' text-anchor='middle' paint-order='stroke' stroke='rgba(14,20,27,.7)' stroke-width='4'>{e(name)}</text>")
    for k, r in enumerate(scene.get("routes", [])):
        (x1, y1), (x2, y2) = P(*r["from"]), P(*r["to"])
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - abs(x2 - x1) * r.get("bend", .35)
        L = sum(math.dist(_q(x1, y1, mx, my, x2, y2, i / 40), _q(x1, y1, mx, my, x2, y2, (i + 1) / 40)) for i in range(40))
        d = f"M{x1:.0f},{y1:.0f} Q{mx:.0f},{my:.0f} {x2:.0f},{y2:.0f}"
        dl = r.get("delay", k * .6)
        out.append(f"<path d='{d}' fill='none' stroke='{COLORS["gold"]}' stroke-width='5' stroke-dasharray='14 12' stroke-linecap='round' opacity='.85' "
                   f"style='animation:dash 1s linear infinite;animation-delay:calc(var(--t0)*-1s)'/>")
        out.append(f"<path d='{d}' fill='none' stroke='#fff' stroke-width='16' stroke-linecap='round' stroke-dasharray='1 {L + 40:.0f}' "
                   f"style='--L:{L:.0f};animation:travel 3s cubic-bezier(.5,0,.5,1) infinite;animation-delay:calc(var(--t0)*-1s + {dl}s)'/>")
    for m in scene.get("markers", []):
        x, y = P(m["lon"], m["lat"])
        col = COLORS.get(m.get("color", "gold"), m.get("color"))
        r = min(13, max(9, s * 0.14))
        out.append(f"<circle class='ring' cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='none' stroke='{col}' stroke-width='3'/>")
        out.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r:.0f}' fill='{col}' stroke='#0e141b' stroke-width='4'/>")
        dx = m.get("dx", 1)
        out.append(f"<text x='{x + dx*min(24, max(18, s*0.25)):.0f}' y='{y + 9:.0f}' fill='#fff' font-size='{min(38, max(22, s*0.34)):.0f}' font-weight='800' text-anchor='{'start' if dx > 0 else 'end'}' paint-order='stroke' stroke='#0e141b' stroke-width='6'>{e(m['name'])}</text>")
    out.append("</svg>")
    return "".join(out)


def legend(items, v):
    rows = "".join(
        f"<div style='display:flex;align-items:center;gap:16px;margin-top:14px'><span style='width:30px;height:30px;border-radius:6px;background:{COLORS.get(i['color'], i['color'])}'></span><span style='font-size:{34 if v else 30}px'>{e(i['label'])}</span></div>"
        for i in items)
    return f"<div style='margin-top:30px'>{rows}</div>"


# ---------------------------------------------------------------- scene types
def render_scene(scene, orient, state=None, hook="", ctx=None, seed=0):
    """Return HTML for one scene. `state` = how many reveal items are visible."""
    CTX.clear()
    CTX.update(ctx or {})
    v = orient == "v"
    fn = globals()["scene_" + scene["type"]]
    body = fn(scene, v, state)
    art = scene.get("art")
    if art and scene["type"] != "flow":
        svg = ART[art["name"]]()
        mode = art.get("mode", "side")
        if mode == "side" and not v:
            body = (f"<style>.stage{{right:860px !important;padding:0 !important}}</style>{body}"
                    f"<div class='artwrap' style='position:absolute;right:90px;top:170px;width:700px;height:700px'>{svg}</div>")
        elif mode == "side" and v:
            body = f"<div class='artwrap' style='position:absolute;left:190px;top:290px;width:700px;height:700px;opacity:.22'>{svg}</div>{body}"
        elif mode == "top":
            sz = 330 if not v else 300
            disc = (f"background:radial-gradient(circle, rgba(14,20,27,.92) 0%, rgba(14,20,27,.85) 58%, rgba(14,20,27,0) 71%);"
                    f"border-radius:50%;box-shadow:inset 0 0 0 3px rgba(232,176,75,.35);padding:{sz * .13:.0f}px")
            body = (f"<div class='artwrap' style='position:absolute;left:50%;top:{'320' if v else '70'}px;width:{sz}px;height:{sz}px;"
                    f"margin-left:-{sz // 2}px;{disc}'>{svg}</div><style>.stage{{top:{'580' if v else '330'}px !important}}</style>{body}")
        else:  # back
            body = (f"<div class='artwrap' style='position:absolute;left:50%;top:{'640' if v else '540'}px;width:{900 if v else 980}px;height:{900 if v else 980}px;"
                    f"transform:translate(-50%,-50%);opacity:{art.get('opacity', .5)}'>{svg}</div>{body}")
    return page(orient, body, source=scene.get("source", ""), hook=hook,
                brand=scene.get("brand", True), bg=scene.get("bg"), seed=seed)


def _new(cur):
    return " newi" if cur and CTX.get("new") else ""


def scene_title(s, v, state):
    size = 120 if v else 132
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;{'align-items:center;text-align:center;' if v else ''}'>
      <div class='kicker'>{e(s.get('kicker', 'Myanmar Stories'))}</div>
      <h1 style='font-size:{size}px;margin-top:26px;max-width:{900 if v else 1150}px'>{e(s['title'])}</h1>
      <div class='line' style='width:200px;height:8px;background:{COLORS['gold']};margin-top:34px'></div>
      <div style='font-size:{40 if v else 40}px;margin-top:30px;max-width:1000px;line-height:1.35;color:#dfe6ec'>{e(s.get('subtitle', ''))}</div>
      <div style='margin-top:40px;font-size:{30 if v else 26}px;font-weight:600;color:{COLORS['gold']}'>{e(s.get('byline', ''))}</div>
    </div>""" + ("" if v or s.get("bg") else f"<div class='mapbox' style='position:absolute;right:40px;top:90px;bottom:90px;width:620px;opacity:.55'>{map_svg({'labels': False, 'countries': False, 'highlight': s.get('highlight', {})}, 620, 900)}</div>")


def scene_chapter(s, v, state):
    return f"""<div class='ghostnum'>{e(s.get('number', ''))}</div>
    <div class='stage' style='display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center'>
      <div class='kicker' style='font-size:{36 if v else 32}px'>Part {e(s.get('number', ''))}</div>
      <div class='line' style='width:140px;height:6px;background:{COLORS['gold']};margin:34px 0;transform-origin:center'></div>
      <h1 style='font-size:{110 if v else 124}px;max-width:1400px'>{e(s['title'])}</h1>
    </div>"""


def scene_map(s, v, state):
    if v:
        return f"""<div class='col' style='position:absolute;top:300px;left:0;right:0;text-align:center;padding:0 60px'><h2 style='font-size:54px'>{e(s.get('heading', ''))}</h2></div>
        <div class='mapbox' style='position:absolute;top:380px;left:90px;width:900px;height:650px'>{map_svg(s, 900, 650)}</div>"""
    return f"""<div class='col' style='position:absolute;left:110px;top:200px;width:700px'>
        <div class='kicker'>{e(s.get('kicker', ''))}</div>
        <h2 style='margin-top:18px'>{e(s.get('heading', ''))}</h2>
        <div class='muted' style='font-size:32px;line-height:1.4;margin-top:24px'>{e(s.get('caption', ''))}</div>
        {legend(s.get('legend', []), v)}
      </div>
      <div class='mapbox' style='position:absolute;right:60px;top:60px;width:960px;height:900px'>{map_svg(s, 960, 900)}</div>"""


def _visible(s, state):
    n = len(s["items"])
    return n if state is None else state


def scene_timeline(s, v, state):
    items = s["items"]
    shown = _visible(s, state)
    if v:
        rows = []
        for i, it in enumerate(items):
            on, cur = i < shown, i == shown - 1
            rows.append(f"""<div class='{_new(cur)}' style='display:flex;gap:30px;align-items:flex-start;opacity:{1 if on else .18};margin-bottom:24px'>
              <div style='min-width:200px;text-align:right;font-weight:800;font-size:42px;color:{COLORS['gold'] if cur else COLORS['text']}'>{e(it['date'])}</div>
              <div class='badge' style='width:18px;height:18px;border-radius:50%;margin-top:16px;background:{COLORS['gold'] if cur else COLORS['muted']}'></div>
              <div style='font-size:36px;line-height:1.25;font-weight:{700 if cur else 500}'>{e(it['text'])}</div></div>""")
        return f"<div class='stage' style='display:flex;flex-direction:column;justify-content:center'><h2 style='text-align:center;margin-bottom:40px;font-size:54px'>{e(s.get('heading', ''))}</h2>{''.join(rows)}</div>"
    n = len(items)
    cols = []
    for i, it in enumerate(items):
        on, cur = i < shown, i == shown - 1
        cols.append(f"""<div class='{_new(cur)}' style='flex:1;opacity:{1 if on else .16};position:relative;padding-top:70px'>
          <div class='badge' style='position:absolute;top:18px;left:0;width:28px;height:28px;border-radius:50%;background:{COLORS['gold'] if cur else COLORS['text']}'></div>
          <div style='font-weight:800;font-size:{52 if n <= 5 else 42}px;color:{COLORS['gold'] if cur else COLORS['text']}'>{e(it['date'])}</div>
          <div style='font-size:{32 if n <= 5 else 27}px;line-height:1.3;margin-top:14px;padding-right:30px;font-weight:{600 if cur else 400}'>{e(it['text'])}</div></div>""")
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'><div class='kicker'>{e(s.get('kicker', 'Timeline'))}</div><h2 style='margin-top:16px'>{e(s.get('heading', ''))}</h2>
      <div style='position:relative;margin-top:90px'><div class='line' style='position:absolute;top:31px;left:0;right:0;height:3px;background:#3a4856'></div>
      <div style='display:flex'>{''.join(cols)}</div></div></div>"""


def scene_points(s, v, state):
    shown = _visible(s, state)
    rows = []
    for i, it in enumerate(s["items"]):
        on, cur = i < shown, i == shown - 1
        rows.append(f"""<div class='{_new(cur)}' style='display:flex;gap:28px;align-items:flex-start;opacity:{1 if on else .14};margin-bottom:{26 if v else 34}px'>
          <div class='badge' style='min-width:62px;height:62px;border-radius:14px;background:{COLORS['gold'] if cur else 'rgba(42,56,70,.9)'};color:{COLORS['bg'] if cur else COLORS['text']};font-weight:800;font-size:32px;display:flex;align-items:center;justify-content:center'>{i + 1}</div>
          <div style='font-size:{38 if v else 46}px;line-height:1.3;font-weight:{700 if cur else 500};padding-top:6px;text-shadow:0 3px 18px rgba(0,0,0,.6)'>{e(it)}</div></div>""")
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'><div class='kicker'>{e(s.get('kicker', ''))}</div>
      <h2 style='margin:16px 0 {40 if v else 54}px'>{e(s.get('heading', ''))}</h2>{''.join(rows)}</div>"""


def scene_stat(s, v, state):
    val = str(s["value"])
    if re.fullmatch(r"\d{1,6}", val):
        to = int(val)
        frm = 0 if to <= 100 else int(to * 0.97)
        value = f"<span class='count' style='--from:{frm};--to:{to};--n:{to}'></span>"
    else:
        value = e(val)
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center'>
      <div class='kicker'>{e(s.get('kicker', ''))}</div>
      <div style='font-size:{170 if v else 240}px;font-weight:800;letter-spacing:-.04em;color:{COLORS.get(s.get('color', 'gold'), s.get('color'))};margin-top:20px;line-height:1;text-shadow:0 10px 60px rgba(0,0,0,.5)'>{value}</div>
      <div style='font-size:{46 if v else 56}px;font-weight:700;margin-top:30px;max-width:1300px;line-height:1.2'>{e(s.get('label', ''))}</div>
      <div style='font-size:{32 if v else 34}px;margin-top:20px;max-width:1200px;line-height:1.35;color:#d3dbe2'>{e(s.get('detail', ''))}</div></div>"""


def scene_quote(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;{'' if v else 'padding:0 120px;'}'>
      <div style='font-size:220px;line-height:.6;color:{COLORS['gold']};font-weight:800'>“</div>
      <div style='font-size:{48 if v else 62}px;line-height:1.3;font-weight:700;text-shadow:0 4px 30px rgba(0,0,0,.6)'>{e(s['text'])}</div>
      <div style='font-size:{34 if v else 32}px;margin-top:40px;color:{COLORS['gold']};font-weight:700'>— {e(s.get('who', ''))}</div></div>"""


def scene_text(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'>
      <div class='kicker'>{e(s.get('kicker', ''))}</div>
      <h2 style='margin-top:18px;font-size:{70 if v else 86}px;max-width:1400px'>{e(s.get('heading', ''))}</h2>
      <div class='line' style='width:160px;height:6px;background:{COLORS['gold']};margin-top:30px'></div>
      <div style='font-size:{40 if v else 42}px;line-height:1.45;margin-top:30px;max-width:1350px;color:#dfe6ec;text-shadow:0 3px 18px rgba(0,0,0,.6)'>{e(s.get('body', ''))}</div></div>"""


def scene_image(s, v, state):
    return f"""<div class='col' style='position:absolute;left:{70 if v else 110}px;right:{70 if v else 110}px;bottom:{860 if v else 220}px'>
        <h2 style='font-size:{58 if v else 62}px'>{e(s.get('caption', ''))}</h2></div>"""


def scene_endcard(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center'>
      <div class='kicker'>{e(s.get('kicker', 'Watch the full story'))}</div>
      <h1 style='font-size:{96 if v else 108}px;margin-top:30px;max-width:1300px'>{e(s.get('title', ''))}</h1>
      <div style='margin-top:50px;font-size:{40 if v else 38}px;font-weight:800;color:#111;background:{COLORS['gold']};padding:18px 40px;border-radius:60px'>{e(s.get('cta', 'Full video on YouTube'))}</div></div>"""


def scene_phone(s, v, state):
    """A phone screen showing an incoming call or threatening messages."""
    msgs = s.get("messages", [])
    shown = len(msgs) if state is None else state
    bubbles = []
    for i, m in enumerate(msgs):
        cur = i == shown - 1
        newb = cur and CTX.get("new") and not m.get("me")
        anim = " newb" if newb else (" newi" if cur and CTX.get("new") else "")
        b = (f"<div class='{anim}' style='align-self:{'flex-end' if m.get('me') else 'flex-start'};max-width:82%;margin-top:22px;padding:22px 28px;border-radius:26px;"
             f"background:{'#2f6fd6' if m.get('me') else '#2a3542'};font-size:30px;line-height:1.35;opacity:{1 if i < shown else 0}'>{e(m['text'])}</div>")
        if newb:
            b = f"<div style='position:relative;display:flex;flex-direction:column'><div class='typing'><i></i><i></i><i></i></div>{b}</div>"
        bubbles.append(b)
    call, ringing = "", s.get("caller") and not msgs
    if s.get("caller"):
        call = f"""<div style='text-align:center;margin-top:60px'><div style='font-size:26px;color:{COLORS['muted']}'>{e(s.get('call_label', 'Incoming call'))}</div>
          <div style='font-size:46px;font-weight:700;margin-top:14px'>{e(s['caller'])}</div>
          <div style='display:flex;justify-content:center;gap:120px;margin-top:{300 if not msgs else 40}px'>
            <div style='width:110px;height:110px;border-radius:50%;background:{COLORS['red']}'></div>
            <div class='{'answer' if ringing else ''}' style='width:110px;height:110px;border-radius:50%;background:{COLORS['green']}'></div></div></div>"""
    phone = f"""<div class='{'shaking' if ringing else ''}' style='width:560px;height:1000px;border-radius:70px;background:linear-gradient(180deg,#0f151c,#0a0e13);border:14px solid #2c3742;box-shadow:0 40px 140px rgba(0,0,0,.75), 0 0 80px rgba(232,176,75,.08);
        padding:70px 34px 40px;display:flex;flex-direction:column;overflow:hidden'>
        <div style='width:160px;height:34px;border-radius:20px;background:#000;align-self:center;margin-top:-50px'></div>
        {call}<div style='display:flex;flex-direction:column;margin-top:20px'>{''.join(bubbles)}</div></div>"""
    if v:
        return f"<div style='position:absolute;top:290px;left:0;right:0;display:flex;justify-content:center;transform:scale(.78);transform-origin:top center'><div class='phonewrap'>{phone}</div></div>"
    return f"""<div class='col' style='position:absolute;left:110px;top:0;bottom:0;width:760px;display:flex;flex-direction:column;justify-content:center'>
        <div class='kicker'>{e(s.get('kicker', ''))}</div><h2 style='margin-top:18px'>{e(s.get('heading', ''))}</h2>
        <div class='muted' style='font-size:32px;line-height:1.4;margin-top:24px'>{e(s.get('caption', ''))}</div></div>
      <div class='phonewrap' style='position:absolute;right:200px;top:40px'>{phone}</div>"""


def scene_flow(s, v, state):
    """Boxes connected by arrows, e.g. Junta -> Family -> Activist."""
    shown = len(s["items"]) if state is None else state
    boxes = []
    for i, it in enumerate(s["items"]):
        on, cur = i < shown, i == shown - 1
        col = COLORS.get(it.get("color", ""), it.get("color")) or ("#2a3846")
        boxes.append(f"""<div class='{_new(cur).strip()} badge' style='opacity:{1 if on else .12};flex:1;background:rgba(22,32,43,.92);border:3px solid {COLORS['gold'] if cur else col};border-radius:24px;
            padding:{(12 if s.get('art') else 20) if v else (26 if s.get('art') else 38)}px;text-align:center'>
            <div style='font-size:{36 if v else 46}px;font-weight:800'>{e(it['title'])}</div>
            <div class='muted' style='font-size:{28 if v else 29}px;margin-top:12px;line-height:1.3'>{e(it.get('text', ''))}</div></div>""")
        if i < len(s["items"]) - 1:
            arrow = "↓" if v else "→"
            na = _new(i + 2 == shown)
            boxes.append(f"<div class='{na}' style='opacity:{1 if i + 1 < shown else .12};font-size:{36 if v else 80}px;line-height:1.1;color:{COLORS['gold']};text-align:center;padding:{'0' if v else '0 22px'};align-self:center'>{arrow}</div>")
    direction = "column" if v else "row"
    art_html = ""
    if s.get("art"):
        hh = 250 if v else 400
        svg = ART[s["art"]["name"]]().replace("viewBox='0 0 600 600'", "viewBox='0 60 600 480' preserveAspectRatio='xMidYMid meet'")
        art_html = (f"<div class='artwrap' style='height:{hh}px;margin:{'0 0 10px' if v else '6px 0 10px'};display:flex;justify-content:center'>"
                    f"<div style='width:{hh * 1.25:.0f}px;height:{hh}px'>{svg}</div></div>")
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'>
      <div class='kicker' style='{'text-align:center' if v else ''}'>{e(s.get('kicker', ''))}</div>
      <h2 style='margin:16px 0 {30 if v else (30 if s.get('art') else 70)}px;{'text-align:center;font-size:54px' if v else ''}'>{e(s.get('heading', ''))}</h2>
      {art_html}
      <div style='display:flex;flex-direction:{direction};align-items:stretch'>{''.join(boxes)}</div></div>"""


def thumbnail(t):
    big = e(t["text"]).replace("|", "<br>")
    CTX.clear()
    if t.get("bg"):
        art = ""
    else:
        art = f"<div style='position:absolute;right:-40px;top:-30px;width:720px;height:1140px'>{map_svg({'labels': False, 'countries': False, 'highlight': t.get('highlight', {}), 'dim_others': False}, 720, 1140)}</div>"
    body = f"""{art}
      <div style='position:absolute;inset:0;background:linear-gradient(90deg,rgba(14,20,27,.95) 0%,rgba(14,20,27,.75) 45%,rgba(14,20,27,0) 80%)'></div>
      <div style='position:absolute;left:70px;top:0;bottom:0;width:1000px;display:flex;flex-direction:column;justify-content:center'>
        <div style='font-size:38px;font-weight:800;color:#111;background:{COLORS['gold']};align-self:flex-start;padding:8px 22px;border-radius:10px;letter-spacing:.06em;text-transform:uppercase'>{e(t.get('kicker', ''))}</div>
        <h1 style='font-size:{t.get('size', 128)}px;margin-top:26px;line-height:.95;text-transform:uppercase;text-shadow:0 8px 40px rgba(0,0,0,.8)'>{big}</h1></div>"""
    bg = dict(t["bg"], dim=0.05) if t.get("bg") else None
    return page("h", body, brand=False, bg=bg, shade="linear-gradient(90deg, rgba(14,20,27,.2) 0%, rgba(14,20,27,0) 100%)")
