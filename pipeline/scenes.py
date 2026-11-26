"""HTML templates for every scene type, in landscape (16:9) and vertical (9:16)."""
import html
import json
import math
from pathlib import Path

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
    "muted": "#9aa7b4",
    "gold": "#e8b04b",
    "red": "#d1495b",
    "green": "#3fa87a",
    "blue": "#4a8fd6",
}

e = lambda s: html.escape(str(s or ""))


def css(orient):
    v = orient == "v"
    return f"""
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-Regular.otf'); font-weight: 400; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-SemiBold.otf'); font-weight: 600; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-Bold.otf'); font-weight: 700; }}
@font-face {{ font-family: Inter; src: url('file://{FONTS}/Inter-ExtraBold.otf'); font-weight: 800; }}
@font-face {{ font-family: MM; src: url('file://{FONTS}/NotoSansMyanmar-Regular.ttf'); font-weight: 400; }}
@font-face {{ font-family: MM; src: url('file://{FONTS}/NotoSansMyanmar-Bold.ttf'); font-weight: 700; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; height: 100%; overflow: hidden; }}
body {{ background: radial-gradient(ellipse at 70% 30%, #17222e 0%, {COLORS['bg']} 70%);
  color: {COLORS['text']}; font-family: Inter, MM, sans-serif; position: relative; }}
.grain {{ position: absolute; inset: 0; background-image: radial-gradient(rgba(255,255,255,.025) 1px, transparent 1px);
  background-size: 6px 6px; pointer-events: none; }}
.brand {{ position: absolute; {'top: 60px; left: 0; right: 0; text-align: center;' if v else 'top: 44px; left: 64px;'}
  font-size: {26 if v else 20}px; letter-spacing: .14em; text-transform: uppercase; color: {COLORS['muted']}; font-weight: 600; }}
.brand b {{ color: {COLORS['gold']}; }}
.source {{ position: absolute; {'top: 1100px; left: 60px; right: 60px; text-align: center;' if v else 'top: 44px; right: 64px; text-align: right; max-width: 700px;'}
  font-size: {24 if v else 19}px; color: {COLORS['muted']}; }}
.hook {{ position: absolute; top: 110px; left: 60px; right: 60px; text-align: center; font-weight: 800;
  font-size: 60px; line-height: 1.1; color: {COLORS['text']}; }}
.mapbox {{ -webkit-mask-image: radial-gradient(ellipse 72% 72% at 50% 50%, #000 72%, transparent 100%); }}
.hook span {{ color: {COLORS['gold']}; }}
.kicker {{ color: {COLORS['gold']}; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; font-size: {32 if v else 26}px; }}
h1 {{ font-weight: 800; letter-spacing: -.02em; line-height: 1.05; }}
h2 {{ font-weight: 800; letter-spacing: -.015em; line-height: 1.1; font-size: {66 if v else 64}px; }}
.muted {{ color: {COLORS['muted']}; }}
.stage {{ position: absolute; {'top: 300px; bottom: 830px; left: 70px; right: 70px;' if v else 'top: 120px; bottom: 210px; left: 110px; right: 110px;'} }}
"""


def page(orient, body, source="", hook="", brand=True):
    parts = [f"<!doctype html><html><head><meta charset='utf-8'><style>{css(orient)}</style></head><body><div class='grain'></div>"]
    if brand and not hook:
        parts.append(f"<div class='brand'>{BRAND}</div>")
    if hook:
        parts.append(f"<div class='hook'>{hook}</div>")
    parts.append(body)
    if source:
        parts.append(f"<div class='source'>Source: {e(source)}</div>")
    parts.append("</body></html>")
    return "".join(parts)


BRAND = "Myanmar <b>Stories</b>"


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
        out.append(f"<path d='{path(f['geometry'])}' fill='{fill}' fill-opacity='{0.55 if dim else 1}' stroke='{COLORS['land_line']}' stroke-width='2.2' stroke-linejoin='round'/>")
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
    for m in scene.get("markers", []):
        x, y = P(m["lon"], m["lat"])
        col = COLORS.get(m.get("color", "gold"), m.get("color"))
        out.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{min(13, max(9, s*0.14)):.0f}' fill='{col}' stroke='#0e141b' stroke-width='4'/>")
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
def render_scene(scene, orient, state=None, hook=""):
    """Return HTML for one scene. `state` = how many reveal items are visible."""
    v = orient == "v"
    t = scene["type"]
    src = scene.get("source", "")
    fn = globals()["scene_" + t]
    return page(orient, fn(scene, v, state), source=src, hook=hook, brand=scene.get("brand", True))


def scene_title(s, v, state):
    size = 96 if v else 116
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;{'align-items:center;text-align:center;' if v else ''}'>
      <div class='kicker'>{e(s.get('kicker', 'Myanmar Stories'))}</div>
      <h1 style='font-size:{size}px;margin-top:26px;max-width:{900 if v else 1150}px'>{e(s['title'])}</h1>
      <div class='muted' style='font-size:{40 if v else 38}px;margin-top:30px;max-width:1000px;line-height:1.35'>{e(s.get('subtitle', ''))}</div>
      <div style='margin-top:46px;font-size:{30 if v else 26}px;font-weight:600'>{e(s.get('byline', ''))}</div>
    </div>""" + ("" if v else f"<div style='position:absolute;right:40px;top:90px;bottom:90px;width:620px;opacity:.55'>{map_svg({'labels': False, 'countries': False, 'highlight': s.get('highlight', {})}, 620, 900)}</div>")


def scene_chapter(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center'>
      <div class='kicker' style='font-size:{36 if v else 30}px'>Part {e(s.get('number', ''))}</div>
      <div style='width:120px;height:5px;background:{COLORS['gold']};margin:34px 0'></div>
      <h1 style='font-size:{104 if v else 110}px;max-width:1300px'>{e(s['title'])}</h1>
    </div>"""


def scene_map(s, v, state):
    if v:
        return f"""<div style='position:absolute;top:300px;left:0;right:0;text-align:center;padding:0 60px'><h2 style='font-size:54px'>{e(s.get('heading', ''))}</h2></div>
        <div class='mapbox' style='position:absolute;top:380px;left:90px;width:900px;height:650px'>{map_svg(s, 900, 650)}</div>"""
    return f"""<div style='position:absolute;left:110px;top:200px;width:700px'>
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
            rows.append(f"""<div style='display:flex;gap:30px;align-items:flex-start;opacity:{1 if on else .18};margin-bottom:24px'>
              <div style='min-width:200px;text-align:right;font-weight:800;font-size:42px;color:{COLORS['gold'] if cur else COLORS['text']}'>{e(it['date'])}</div>
              <div style='width:18px;height:18px;border-radius:50%;margin-top:16px;background:{COLORS['gold'] if cur else COLORS['muted']}'></div>
              <div style='font-size:36px;line-height:1.25;font-weight:{700 if cur else 500}'>{e(it['text'])}</div></div>""")
        return f"<div class='stage' style='display:flex;flex-direction:column;justify-content:center'><h2 style='text-align:center;margin-bottom:40px;font-size:54px'>{e(s.get('heading', ''))}</h2>{''.join(rows)}</div>"
    n = len(items)
    cols = []
    for i, it in enumerate(items):
        on, cur = i < shown, i == shown - 1
        cols.append(f"""<div style='flex:1;opacity:{1 if on else .16};position:relative;padding-top:70px'>
          <div style='position:absolute;top:18px;left:0;width:28px;height:28px;border-radius:50%;background:{COLORS['gold'] if cur else COLORS['text']};box-shadow:0 0 0 8px {COLORS['bg']}'></div>
          <div style='font-weight:800;font-size:{52 if n <= 5 else 42}px;color:{COLORS['gold'] if cur else COLORS['text']}'>{e(it['date'])}</div>
          <div style='font-size:{32 if n <= 5 else 27}px;line-height:1.3;margin-top:14px;padding-right:30px;font-weight:{600 if cur else 400}'>{e(it['text'])}</div></div>""")
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'><div class='kicker'>{e(s.get('kicker', 'Timeline'))}</div><h2 style='margin-top:16px'>{e(s.get('heading', ''))}</h2>
      <div style='position:relative;margin-top:90px'><div style='position:absolute;top:31px;left:0;right:0;height:3px;background:#3a4856'></div>
      <div style='display:flex'>{''.join(cols)}</div></div></div>"""


def scene_points(s, v, state):
    shown = _visible(s, state)
    rows = []
    for i, it in enumerate(s["items"]):
        on, cur = i < shown, i == shown - 1
        rows.append(f"""<div style='display:flex;gap:28px;align-items:flex-start;opacity:{1 if on else .14};margin-bottom:{26 if v else 34}px'>
          <div style='min-width:62px;height:62px;border-radius:14px;background:{COLORS['gold'] if cur else '#2a3846'};color:{COLORS['bg'] if cur else COLORS['text']};font-weight:800;font-size:32px;display:flex;align-items:center;justify-content:center'>{i + 1}</div>
          <div style='font-size:{38 if v else 44}px;line-height:1.3;font-weight:{700 if cur else 500};padding-top:6px'>{e(it)}</div></div>""")
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'><div class='kicker'>{e(s.get('kicker', ''))}</div>
      <h2 style='margin:16px 0 {40 if v else 54}px'>{e(s.get('heading', ''))}</h2>{''.join(rows)}</div>"""


def scene_stat(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center'>
      <div class='kicker'>{e(s.get('kicker', ''))}</div>
      <div style='font-size:{160 if v else 220}px;font-weight:800;letter-spacing:-.04em;color:{COLORS.get(s.get('color', 'gold'), s.get('color'))};margin-top:20px;line-height:1'>{e(s['value'])}</div>
      <div style='font-size:{46 if v else 54}px;font-weight:700;margin-top:30px;max-width:1300px;line-height:1.2'>{e(s.get('label', ''))}</div>
      <div class='muted' style='font-size:{32 if v else 34}px;margin-top:20px;max-width:1200px;line-height:1.35'>{e(s.get('detail', ''))}</div></div>"""


def scene_quote(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;{'' if v else 'padding:0 120px;'}'>
      <div style='font-size:200px;line-height:.6;color:{COLORS['gold']};font-weight:800'>“</div>
      <div style='font-size:{48 if v else 60}px;line-height:1.3;font-weight:600'>{e(s['text'])}</div>
      <div style='font-size:{34 if v else 32}px;margin-top:40px;color:{COLORS['gold']};font-weight:700'>— {e(s.get('who', ''))}</div></div>"""


def scene_text(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'>
      <div class='kicker'>{e(s.get('kicker', ''))}</div>
      <h2 style='margin-top:18px;font-size:{70 if v else 80}px;max-width:1400px'>{e(s.get('heading', ''))}</h2>
      <div class='muted' style='font-size:{40 if v else 40}px;line-height:1.45;margin-top:34px;max-width:1350px'>{e(s.get('body', ''))}</div></div>"""


def scene_image(s, v, state):
    src = Path(s["src"]).resolve()
    return f"""<div style='position:absolute;inset:0;background:url("file://{src}") center/cover'></div>
      <div style='position:absolute;inset:0;background:linear-gradient(180deg,rgba(14,20,27,.55) 0%,rgba(14,20,27,0) 30%,rgba(14,20,27,0) 55%,rgba(14,20,27,.92) 100%)'></div>
      <div style='position:absolute;left:{70 if v else 110}px;right:{70 if v else 110}px;bottom:{860 if v else 220}px'>
        <h2 style='font-size:{58 if v else 62}px'>{e(s.get('caption', ''))}</h2>
        <div class='muted' style='font-size:24px;margin-top:14px'>{e(s.get('credit', ''))}</div></div>"""


def scene_endcard(s, v, state):
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center'>
      <div class='kicker'>{e(s.get('kicker', 'Watch the full story'))}</div>
      <h1 style='font-size:{96 if v else 100}px;margin-top:30px;max-width:1300px'>{e(s.get('title', ''))}</h1>
      <div style='margin-top:50px;font-size:{40 if v else 36}px;font-weight:700;color:{COLORS['gold']}'>{e(s.get('cta', 'Full video on YouTube'))}</div></div>"""


def thumbnail(t):
    big = e(t["text"]).replace("|", "<br>")
    body = f"""<div style='position:absolute;right:-40px;top:-30px;width:720px;height:1140px'>{map_svg({'labels': False, 'countries': False, 'highlight': t.get('highlight', {}), 'dim_others': False}, 720, 1140)}</div>
      <div style='position:absolute;inset:0;background:linear-gradient(90deg,{COLORS['bg']} 0%,{COLORS['bg']} 45%,rgba(14,20,27,0) 75%)'></div>
      <div style='position:absolute;left:70px;top:0;bottom:0;width:820px;display:flex;flex-direction:column;justify-content:center'>
        <div class='kicker' style='font-size:34px'>{e(t.get('kicker', ''))}</div>
        <h1 style='font-size:{t.get('size', 128)}px;margin-top:20px;line-height:.98;text-transform:uppercase'>{big}</h1>
        <div style='width:160px;height:12px;background:{COLORS['gold']};margin-top:40px'></div></div>"""
    return page("h", body, brand=False)


def scene_phone(s, v, state):
    """A phone screen showing an incoming call or threatening messages."""
    shown = len(s.get("messages", [])) if state is None else state
    bubbles = "".join(
        f"<div style='align-self:{'flex-end' if m.get('me') else 'flex-start'};max-width:82%;margin-top:22px;padding:22px 28px;border-radius:26px;"
        f"background:{'#2f6fd6' if m.get('me') else '#2a3542'};font-size:30px;line-height:1.35;opacity:{1 if i < shown else 0}'>{e(m['text'])}</div>"
        for i, m in enumerate(s.get("messages", [])))
    call = ""
    if s.get("caller"):
        call = f"""<div style='text-align:center;margin-top:60px'><div style='font-size:26px;color:{COLORS['muted']}'>{e(s.get('call_label', 'Incoming call'))}</div>
          <div style='font-size:46px;font-weight:700;margin-top:14px'>{e(s['caller'])}</div>
          <div style='display:flex;justify-content:center;gap:120px;margin-top:{300 if not s.get('messages') else 40}px'>
            <div style='width:110px;height:110px;border-radius:50%;background:{COLORS['red']}'></div>
            <div style='width:110px;height:110px;border-radius:50%;background:{COLORS['green']}'></div></div></div>"""
    phone = f"""<div style='width:560px;height:1000px;border-radius:70px;background:#0b1016;border:14px solid #2c3742;box-shadow:0 40px 120px rgba(0,0,0,.6);
        padding:70px 34px 40px;display:flex;flex-direction:column;overflow:hidden'>
        <div style='width:160px;height:34px;border-radius:20px;background:#000;align-self:center;margin-top:-50px'></div>
        {call}<div style='display:flex;flex-direction:column;margin-top:20px'>{bubbles}</div></div>"""
    if v:
        return f"<div style='position:absolute;top:290px;left:0;right:0;display:flex;justify-content:center;transform:scale(.78);transform-origin:top center'>{phone}</div>"
    return f"""<div style='position:absolute;left:110px;top:0;bottom:0;width:760px;display:flex;flex-direction:column;justify-content:center'>
        <div class='kicker'>{e(s.get('kicker', ''))}</div><h2 style='margin-top:18px'>{e(s.get('heading', ''))}</h2>
        <div class='muted' style='font-size:32px;line-height:1.4;margin-top:24px'>{e(s.get('caption', ''))}</div></div>
      <div style='position:absolute;right:200px;top:40px'>{phone}</div>"""


def scene_flow(s, v, state):
    """Boxes connected by arrows, e.g. Junta -> Family -> Activist."""
    shown = len(s["items"]) if state is None else state
    boxes = []
    for i, it in enumerate(s["items"]):
        on, cur = i < shown, i == shown - 1
        col = COLORS.get(it.get("color", ""), it.get("color")) or ("#2a3846")
        box = f"""<div style='opacity:{1 if on else .12};flex:1;background:{COLORS['panel']};border:3px solid {COLORS['gold'] if cur else col};border-radius:24px;
            padding:{30 if v else 38}px;text-align:center'>
            <div style='font-size:{44 if v else 46}px;font-weight:800'>{e(it['title'])}</div>
            <div class='muted' style='font-size:{28 if v else 28}px;margin-top:12px;line-height:1.3'>{e(it.get('text', ''))}</div></div>"""
        boxes.append(box)
        if i < len(s["items"]) - 1:
            arrow = "↓" if v else "→"
            boxes.append(f"<div style='opacity:{1 if i + 1 < shown else .12};font-size:{60 if v else 80}px;color:{COLORS['gold']};text-align:center;padding:{'6px 0' if v else '0 22px'};align-self:center'>{arrow}</div>")
    direction = "column" if v else "row"
    return f"""<div class='stage' style='display:flex;flex-direction:column;justify-content:center'>
      <div class='kicker' style='{'text-align:center' if v else ''}'>{e(s.get('kicker', ''))}</div>
      <h2 style='margin:16px 0 {40 if v else 70}px;{'text-align:center;font-size:54px' if v else ''}'>{e(s.get('heading', ''))}</h2>
      <div style='display:flex;flex-direction:{direction};align-items:stretch'>{''.join(boxes)}</div></div>"""
