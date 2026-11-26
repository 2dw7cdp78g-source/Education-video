"""Animated 2D illustrations (inline SVG + CSS), drawn for the stories on this channel.

Each function returns an <svg> in a 600x600 box. Loops use the scene clock (--t0), so the
motion continues smoothly when a scene is split into several rendered segments.
"""

NAVY, PANEL, LAND, LINE = "#0e141b", "#16202b", "#26384a", "#2b3947"
TEXT, MUTED, GOLD, RED, GREEN = "#f3efe6", "#8796a5", "#e8b04b", "#d1495b", "#3fa87a"


def A(name, dur, delay=0.0, timing="ease-in-out", it="infinite", extra=""):
    """CSS animation declaration tied to the scene clock."""
    return (f"animation:{name} {dur}s {timing} {it} both;animation-delay:calc(var(--t0)*-1s + {delay}s);"
            f"transform-box:view-box;{extra}")


def _svg(body, style):
    return f"<svg viewBox='0 0 600 600' width='100%' height='100%' xmlns='http://www.w3.org/2000/svg'><style>{style}</style>{body}</svg>"


def _person(x, y, s=1.0, color=LAND, cap=False):
    """Simple silhouette: head + rounded shoulders."""
    cap_svg = f"<rect x='{x-24*s}' y='{y-62*s}' width='{48*s}' height='{14*s}' rx='{4*s}' fill='{color}'/><rect x='{x-30*s}' y='{y-52*s}' width='{60*s}' height='{7*s}' rx='3' fill='{color}'/>" if cap else ""
    return (f"<circle cx='{x}' cy='{y-30*s}' r='{22*s}' fill='{color}'/>{cap_svg}"
            f"<path d='M{x-42*s},{y+60*s} Q{x-42*s},{y+2*s} {x},{y+2*s} Q{x+42*s},{y+2*s} {x+42*s},{y+60*s} Z' fill='{color}'/>")


# ---------------------------------------------------------------- surveillance eye
def eye():
    style = f"""
    @keyframes sweep {{ to {{ transform: rotate(360deg); }} }}
    @keyframes look {{ 0%,100% {{ transform: translateX(-34px); }} 45%,55% {{ transform: translateX(34px); }} }}
    @keyframes blink {{ 0%,90%,100% {{ transform: scaleY(1); }} 94% {{ transform: scaleY(.08); }} }}
    @keyframes ping {{ from {{ transform: scale(.4); opacity: .9; }} to {{ transform: scale(1.5); opacity: 0; }} }}
    @keyframes orbit {{ to {{ transform: rotate(-360deg); }} }}
    @keyframes floatup {{ 0% {{ transform: translateY(40px); opacity: 0; }} 20%,70% {{ opacity: 1; }} 100% {{ transform: translateY(-120px); opacity: 0; }} }}
    .sweep {{ {A('sweep', 4, timing='linear', extra='transform-origin:300px 300px;')} }}
    .look {{ {A('look', 5)} }}
    .lid {{ {A('blink', 4.5, extra='transform-origin:300px 300px;')} }}
    .ping {{ {A('ping', 2.4, timing='ease-out', extra='transform-origin:300px 300px;')} }}
    .ping2 {{ {A('ping', 2.4, 1.2, timing='ease-out', extra='transform-origin:300px 300px;')} }}
    .orb {{ {A('orbit', 9, timing='linear', extra='transform-origin:300px 300px;')} }}
    .f1 {{ {A('floatup', 3.6, 0)} }} .f2 {{ {A('floatup', 3.6, 1.2)} }} .f3 {{ {A('floatup', 3.6, 2.4)} }}
    """
    rings = "".join(f"<circle cx='300' cy='300' r='{r}' fill='none' stroke='{LINE}' stroke-width='2'/>" for r in (140, 200, 260))
    sweep = (f"<defs><linearGradient id='sw' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='{GOLD}' stop-opacity='0'/>"
             f"<stop offset='1' stop-color='{GOLD}' stop-opacity='.35'/></linearGradient></defs>"
             f"<g class='sweep'><path d='M300,300 L560,300 A260,260 0 0,0 525,170 Z' fill='url(#sw)'/></g>")
    dots = "".join(f"<circle cx='{300 + r}' cy='300' r='6' fill='{c}'/>" for r, c in ((200, GOLD), (-260, RED)))
    tags = (f"<g class='f1'><rect x='60' y='430' width='110' height='44' rx='12' fill='{PANEL}' stroke='{LINE}'/><text x='115' y='459' font-size='22' fill='{GOLD}' text-anchor='middle' font-weight='700'>@you</text></g>"
            f"<g class='f2'><rect x='440' y='420' width='110' height='44' rx='12' fill='{PANEL}' stroke='{LINE}'/><text x='495' y='449' font-size='22' fill='{RED}' text-anchor='middle' font-weight='700'>REC ●</text></g>"
            f"<g class='f3'><rect x='250' y='470' width='100' height='44' rx='12' fill='{PANEL}' stroke='{LINE}'/><text x='300' y='499' font-size='22' fill='{TEXT}' text-anchor='middle' font-weight='700'>IP</text></g>")
    eyeball = (f"<g class='lid'><path d='M110,300 Q300,130 490,300 Q300,470 110,300 Z' fill='{NAVY}' stroke='{GOLD}' stroke-width='7'/>"
               f"<g class='look'><circle cx='300' cy='300' r='78' fill='{PANEL}' stroke='{GOLD}' stroke-width='5'/>"
               f"<circle cx='300' cy='300' r='36' fill='{GOLD}'/><circle cx='318' cy='282' r='11' fill='#fff'/></g></g>")
    body = (rings + f"<circle class='ping' cx='300' cy='300' r='200' fill='none' stroke='{GOLD}' stroke-width='3'/>"
            f"<circle class='ping2' cx='300' cy='300' r='200' fill='none' stroke='{RED}' stroke-width='3'/>"
            + sweep + f"<g class='orb'>{dots}</g>" + eyeball + tags)
    return _svg(body, style)


# ---------------------------------------------------------------- family home + soldier knocking + phone ringing
def family():
    style = f"""
    @keyframes flicker {{ 0%,100% {{ opacity: .95; }} 40% {{ opacity: .75; }} 60% {{ opacity: 1; }} 80% {{ opacity: .8; }} }}
    @keyframes knock {{ 0%,40%,100% {{ transform: rotate(0deg); }} 10%,30% {{ transform: rotate(-28deg); }} 20% {{ transform: rotate(4deg); }} }}
    @keyframes hit {{ 0%,8%,40%,100% {{ opacity: 0; }} 12%,30% {{ opacity: 1; }} }}
    @keyframes wave {{ from {{ transform: scale(.5); opacity: .9; }} to {{ transform: scale(1.6); opacity: 0; }} }}
    @keyframes buzz {{ 0%,30%,100% {{ transform: rotate(0); }} 5%,15%,25% {{ transform: rotate(-8deg); }} 10%,20% {{ transform: rotate(8deg); }} }}
    @keyframes twinkle {{ 0%,100% {{ opacity: .2; }} 50% {{ opacity: 1; }} }}
    @keyframes shiver {{ 0%,100% {{ transform: translateX(0); }} 50% {{ transform: translateX(3px); }} }}
    .win {{ {A('flicker', 2.6)} }}
    .arm {{ {A('knock', 2, extra='transform-origin:118px 372px;')} }}
    .hit {{ {A('hit', 2)} }}
    .w1 {{ {A('wave', 1.6, timing='ease-out', extra='transform-origin:300px 92px;')} }}
    .w2 {{ {A('wave', 1.6, .8, timing='ease-out', extra='transform-origin:300px 92px;')} }}
    .phone {{ {A('buzz', 1.6, extra='transform-origin:300px 92px;')} }}
    .st {{ {A('twinkle', 2.2)} }} .st2 {{ {A('twinkle', 2.2, 1.1)} }}
    .fam {{ {A('shiver', .9)} }}
    """
    stars = "".join(f"<circle class='{c}' cx='{x}' cy='{y}' r='3' fill='#fff'/>" for x, y, c in ((70, 70, 'st'), (520, 60, 'st2'), (560, 160, 'st'), (40, 190, 'st2'), (460, 130, 'st')))
    house = (f"<rect x='40' y='520' width='520' height='6' rx='3' fill='{LINE}'/>"
             f"<path d='M180,300 L370,180 L560,300 Z' fill='{LAND}'/>"
             f"<rect x='205' y='300' width='330' height='220' fill='#1c2733' stroke='{LINE}' stroke-width='3'/>"
             f"<rect class='win' x='240' y='335' width='120' height='95' rx='6' fill='{GOLD}'/>"
             f"<g class='fam'>{_person(278, 395, .55, '#2a2218')}{_person(325, 400, .45, '#2a2218')}</g>"
             f"<rect x='240' y='335' width='120' height='95' rx='6' fill='none' stroke='#5b4a2a' stroke-width='4'/>"
             f"<rect x='405' y='395' width='80' height='125' rx='6' fill='#2b1d1d' stroke='{LINE}' stroke-width='3'/>"
             f"<circle cx='470' cy='460' r='5' fill='{GOLD}'/>")
    soldier = (f"<g>{_person(80, 430, .95, '#4a2a30', cap=True)}"
               f"<g class='arm'><rect x='105' y='364' width='78' height='18' rx='9' fill='#4a2a30'/></g></g>"
               f"<g class='hit' stroke='{RED}' stroke-width='5' stroke-linecap='round'><path d='M205,350 l22,-14'/><path d='M210,372 l26,0'/><path d='M205,394 l22,14'/></g>")
    phone = (f"<circle class='w1' cx='300' cy='92' r='50' fill='none' stroke='{RED}' stroke-width='4'/>"
             f"<circle class='w2' cx='300' cy='92' r='50' fill='none' stroke='{RED}' stroke-width='4'/>"
             f"<g class='phone'><rect x='276' y='48' width='48' height='88' rx='10' fill='{PANEL}' stroke='{TEXT}' stroke-width='4'/>"
             f"<circle cx='300' cy='92' r='10' fill='{RED}'/></g>")
    return _svg(stars + house + soldier + phone, style)


# ---------------------------------------------------------------- fishing hook with money bait
def hook():
    style = f"""
    @keyframes swing {{ 0%,100% {{ transform: rotate(-7deg); }} 50% {{ transform: rotate(7deg); }} }}
    @keyframes spark {{ 0%,100% {{ transform: scale(.2); opacity: 0; }} 50% {{ transform: scale(1); opacity: 1; }} }}
    @keyframes bub {{ from {{ transform: translateY(0); opacity: .7; }} to {{ transform: translateY(-160px); opacity: 0; }} }}
    .sw {{ {A('swing', 3.2, extra='transform-origin:300px 0px;')} }}
    .s1 {{ {A('spark', 1.8, 0, extra='transform-origin:180px 330px;')} }}
    .s2 {{ {A('spark', 1.8, .6, extra='transform-origin:430px 300px;')} }}
    .s3 {{ {A('spark', 1.8, 1.2, extra='transform-origin:400px 450px;')} }}
    .b1 {{ {A('bub', 3, 0, timing='linear')} }} .b2 {{ {A('bub', 3, 1, timing='linear')} }} .b3 {{ {A('bub', 3, 2, timing='linear')} }}
    """
    bars = "".join(f"<rect x='{x}' y='360' width='12' height='220' rx='6' fill='{RED}' opacity='.28'/>" for x in range(110, 520, 52))
    star = lambda cls, x, y: f"<path class='{cls}' d='M{x},{y-18} L{x+5},{y-5} L{x+18},{y} L{x+5},{y+5} L{x},{y+18} L{x-5},{y+5} L{x-18},{y} L{x-5},{y-5} Z' fill='{GOLD}'/>"
    note = (f"<g transform='translate(300 360) rotate(-8)'><rect x='-140' y='-62' width='280' height='124' rx='12' fill='{GREEN}' stroke='#d8f0e3' stroke-width='4'/>"
            f"<circle cx='-80' cy='0' r='34' fill='none' stroke='#d8f0e3' stroke-width='4'/><text x='-80' y='12' font-size='36' font-weight='800' fill='#d8f0e3' text-anchor='middle'>K</text>"
            f"<text x='40' y='-6' font-size='26' font-weight='800' fill='#fff' text-anchor='middle'>SALARY</text>"
            f"<text x='40' y='30' font-size='34' font-weight='800' fill='{GOLD}' text-anchor='middle'>× 2</text></g>")
    line = (f"<g class='sw'><line x1='300' y1='0' x2='300' y2='236' stroke='#c6d0da' stroke-width='3'/>"
            f"<path d='M300,236 L300,290 Q300,330 268,330 Q240,330 240,300' fill='none' stroke='#c6d0da' stroke-width='9' stroke-linecap='round'/>"
            f"<path d='M240,300 l-12,14 M240,300 l14,10' stroke='#c6d0da' stroke-width='7' stroke-linecap='round'/>{note}</g>")
    bubbles = "".join(f"<circle class='{c}' cx='{x}' cy='560' r='{r}' fill='none' stroke='{MUTED}' stroke-width='2'/>" for x, r, c in ((150, 8, 'b1'), (470, 10, 'b2'), (380, 6, 'b3')))
    return _svg(bars + bubbles + line + star('s1', 180, 330) + star('s2', 430, 300) + star('s3', 400, 450), style)


# ---------------------------------------------------------------- ID card stamped REVOKED, chained
def documents():
    style = f"""
    @keyframes stamp {{ 0%,15% {{ transform: rotate(-14deg) scale(2.4); opacity: 0; }} 25% {{ transform: rotate(-14deg) scale(.95); opacity: 1; }}
        30%,90% {{ transform: rotate(-14deg) scale(1); opacity: 1; }} 100% {{ transform: rotate(-14deg) scale(1); opacity: 0; }} }}
    @keyframes jolt {{ 0%,23%,32%,100% {{ transform: translateY(0); }} 26% {{ transform: translateY(6px); }} }}
    @keyframes lock {{ 0%,100% {{ transform: rotate(-10deg); }} 50% {{ transform: rotate(10deg); }} }}
    .stamp {{ {A('stamp', 5, timing='ease-out', extra='transform-origin:330px 300px;')} }}
    .card {{ {A('jolt', 5)} }}
    .lock {{ {A('lock', 2.4, extra='transform-origin:300px 430px;')} }}
    """
    card = (f"<g class='card'><rect x='90' y='170' width='420' height='260' rx='22' fill='#e9e3d4'/>"
            f"<rect x='90' y='170' width='420' height='56' rx='22' fill='{LAND}'/><rect x='90' y='204' width='420' height='22' fill='{LAND}'/>"
            f"<text x='300' y='207' font-size='24' font-weight='800' fill='{TEXT}' text-anchor='middle' letter-spacing='2'>CERTIFICATE OF IDENTITY</text>"
            f"<rect x='120' y='250' width='120' height='150' rx='10' fill='#c9c1ae'/>{_person(180, 330, .8, '#8f8672')}"
            + "".join(f"<rect x='265' y='{y}' width='{w}' height='14' rx='7' fill='#bdb4a0'/>" for y, w in ((262, 210), (292, 170), (322, 200), (352, 140)))
            + f"<text x='265' y='408' font-size='30' font-weight='800' fill='{LAND}'>CI</text></g>")
    stamp = (f"<g class='stamp'><rect x='190' y='255' width='280' height='90' rx='10' fill='none' stroke='{RED}' stroke-width='9'/>"
             f"<text x='330' y='318' font-size='52' font-weight='900' fill='{RED}' text-anchor='middle' letter-spacing='4'>REVOKED</text></g>")
    chain = "".join(f"<ellipse cx='{x}' cy='{430 + (x - 300) * 0.0}' rx='30' ry='16' fill='none' stroke='#9aa5b1' stroke-width='9'/>" for x in range(40, 600, 48))
    lock = (f"<g class='lock'><path d='M272,440 V418 Q272,388 300,388 Q328,388 328,418 V440' fill='none' stroke='#9aa5b1' stroke-width='12'/>"
            f"<rect x='250' y='436' width='100' height='84' rx='14' fill='{GOLD}'/><circle cx='300' cy='470' r='10' fill='{NAVY}'/><rect x='296' y='472' width='8' height='24' fill='{NAVY}'/></g>")
    return _svg(card + stamp + chain + lock, style)


# ---------------------------------------------------------------- deportation truck to border gate
def truck():
    style = f"""
    @keyframes road {{ to {{ stroke-dashoffset: -120; }} }}
    @keyframes drive {{ 0% {{ transform: translateX(-330px); }} 55%,100% {{ transform: translateX(0); }} }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    @keyframes gate {{ 0%,50% {{ transform: rotate(-75deg); }} 65%,92% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(-75deg); }} }}
    @keyframes blink {{ 0%,100% {{ opacity: .2; }} 50% {{ opacity: 1; }} }}
    .road {{ {A('road', 1, timing='linear')} }}
    .truck {{ {A('drive', 6, timing='cubic-bezier(.3,.6,.3,1)')} }}
    .wh1 {{ {A('spin', .6, timing='linear', extra='transform-origin:150px 470px;')} }}
    .wh2 {{ {A('spin', .6, timing='linear', extra='transform-origin:290px 470px;')} }}
    .bar {{ {A('gate', 6, extra='transform-origin:470px 400px;')} }}
    .light {{ {A('blink', .8)} }}
    """
    hills = f"<path d='M0,360 L90,270 L170,330 L260,240 L360,330 L440,260 L520,320 L600,280 L600,420 L0,420 Z' fill='#141d27'/>"
    road = (f"<rect x='0' y='420' width='600' height='110' fill='#1b242e'/>"
            f"<line class='road' x1='0' y1='478' x2='600' y2='478' stroke='{MUTED}' stroke-width='5' stroke-dasharray='40 20' opacity='.6'/>")
    gate = (f"<rect x='478' y='300' width='80' height='120' rx='8' fill='{LAND}' stroke='{LINE}' stroke-width='3'/>"
            f"<rect x='492' y='318' width='52' height='36' rx='4' fill='{GOLD}' opacity='.8'/>"
            f"<circle class='light' cx='518' cy='292' r='10' fill='{RED}'/>"
            f"<text x='518' y='394' font-size='18' font-weight='800' fill='{TEXT}' text-anchor='middle'>BORDER</text>"
            f"<g class='bar'><rect x='330' y='394' width='148' height='14' rx='7' fill='{RED}'/>"
            + "".join(f"<rect x='{x}' y='394' width='20' height='14' fill='#fff'/>" for x in (350, 390, 430)) + "</g>"
            f"<rect x='462' y='392' width='16' height='40' rx='4' fill='{MUTED}'/>")
    wheel = lambda cx, cls: (f"<g class='{cls}'><circle cx='{cx}' cy='470' r='26' fill='#0b0f14' stroke='{MUTED}' stroke-width='5'/>"
                             f"<path d='M{cx-18},470 H{cx+18} M{cx},452 V488' stroke='{MUTED}' stroke-width='4'/></g>")
    truck = (f"<g class='truck'><rect x='90' y='330' width='190' height='130' rx='10' fill='{LAND}' stroke='{LINE}' stroke-width='3'/>"
             + "".join(f"<rect x='{x}' y='352' width='8' height='60' rx='4' fill='{NAVY}'/>" for x in (120, 150, 180, 210, 240))
             + f"<path d='M280,370 H335 Q350,370 356,392 L364,430 V460 H280 Z' fill='#3a4f63' stroke='{LINE}' stroke-width='3'/>"
             f"<rect x='292' y='380' width='44' height='34' rx='5' fill='#9fc3e0' opacity='.7'/>"
             + wheel(150, 'wh1') + wheel(290, 'wh2') + "</g>")
    return _svg(hills + road + gate + truck, style)


# ---------------------------------------------------------------- propaganda megaphone + fake posts
def megaphone():
    style = f"""
    @keyframes wave {{ from {{ transform: scale(.6); opacity: .9; }} to {{ transform: scale(1.5); opacity: 0; }} }}
    @keyframes post {{ 0% {{ transform: translate(0, 120px); opacity: 0; }} 15%,75% {{ opacity: 1; }} 100% {{ transform: translate(60px, -260px); opacity: 0; }} }}
    @keyframes shout {{ 0%,100% {{ transform: rotate(0); }} 50% {{ transform: rotate(-4deg); }} }}
    .w1 {{ {A('wave', 1.4, 0, timing='ease-out', extra='transform-origin:250px 300px;')} }}
    .w2 {{ {A('wave', 1.4, .47, timing='ease-out', extra='transform-origin:250px 300px;')} }}
    .w3 {{ {A('wave', 1.4, .94, timing='ease-out', extra='transform-origin:250px 300px;')} }}
    .p1 {{ {A('post', 4.2, 0, timing='linear')} }} .p2 {{ {A('post', 4.2, 1.4, timing='linear')} }} .p3 {{ {A('post', 4.2, 2.8, timing='linear')} }}
    .meg {{ {A('shout', .7, extra='transform-origin:150px 330px;')} }}
    """
    waves = "".join(f"<path class='{c}' d='M300,190 Q380,300 300,410' fill='none' stroke='{GOLD}' stroke-width='8' stroke-linecap='round'/>" for c in ("w1", "w2", "w3"))
    meg = (f"<g class='meg'><path d='M110,260 L250,170 L250,430 L110,340 Z' fill='{GOLD}'/>"
           f"<rect x='60' y='255' width='60' height='90' rx='12' fill='#c48f2f'/>"
           f"<rect x='120' y='340' width='28' height='90' rx='10' fill='#c48f2f' transform='rotate(-12 134 340)'/></g>")

    def post(cls, x, y, badge, color):
        return (f"<g class='{cls}'><rect x='{x}' y='{y}' width='190' height='110' rx='16' fill='{PANEL}' stroke='{LINE}' stroke-width='3'/>"
                f"<circle cx='{x+30}' cy='{y+30}' r='14' fill='{LAND}'/><rect x='{x+54}' y='{y+22}' width='100' height='14' rx='7' fill='{LAND}'/>"
                f"<rect x='{x+20}' y='{y+58}' width='150' height='12' rx='6' fill='{LINE}'/><rect x='{x+20}' y='{y+80}' width='110' height='12' rx='6' fill='{LINE}'/>"
                f"<circle cx='{x+180}' cy='{y+6}' r='24' fill='{color}'/><text x='{x+180}' y='{y+16}' font-size='28' font-weight='900' fill='#fff' text-anchor='middle'>{badge}</text></g>")
    return _svg(waves + meg + post('p1', 370, 330, '!', RED) + post('p2', 340, 360, '♥', RED) + post('p3', 390, 380, '!', GOLD), style)


# ---------------------------------------------------------------- hiding at home
def hiding():
    style = f"""
    @keyframes hand {{ to {{ transform: rotate(360deg); }} }}
    @keyframes curtain {{ 0%,100% {{ transform: skewX(0deg); }} 50% {{ transform: skewX(3deg); }} }}
    @keyframes breathe {{ 0%,100% {{ transform: scaleY(1); }} 50% {{ transform: scaleY(1.03); }} }}
    @keyframes sweep {{ 0%,100% {{ transform: translateX(-60px); opacity: 0; }} 40%,60% {{ opacity: .5; }} 50% {{ transform: translateX(60px); }} }}
    @keyframes ping {{ 0%,70%,100% {{ transform: scale(1); }} 80% {{ transform: scale(1.25); }} }}
    .h1 {{ {A('hand', 2, timing='linear', extra='transform-origin:470px 150px;')} }}
    .h2 {{ {A('hand', 24, timing='linear', extra='transform-origin:470px 150px;')} }}
    .cur {{ {A('curtain', 3, extra='transform-origin:0px 80px;')} }}
    .me {{ {A('breathe', 2.4, extra='transform-origin:250px 520px;')} }}
    .torch {{ {A('sweep', 5)} }}
    .notif {{ {A('ping', 2.5, extra='transform-origin:150px 470px;')} }}
    """
    room = (f"<rect x='0' y='520' width='600' height='80' fill='#141d27'/>"
            f"<rect x='60' y='80' width='300' height='220' rx='8' fill='#0a1626' stroke='{LINE}' stroke-width='6'/>"
            f"<circle cx='290' cy='140' r='30' fill='#e9e3d4' opacity='.9'/><circle cx='304' cy='130' r='26' fill='#0a1626'/>"
            f"<g class='torch'><path d='M150,300 L210,80 L270,80 Z' fill='#fff8d6' opacity='.35'/></g>"
            f"<line x1='210' y1='80' x2='210' y2='300' stroke='{LINE}' stroke-width='5'/><line x1='60' y1='190' x2='360' y2='190' stroke='{LINE}' stroke-width='5'/>"
            f"<g class='cur'><path d='M60,70 H170 Q150,190 175,310 H60 Z' fill='#3a2a36'/></g>"
            f"<path d='M360,70 H250 Q270,190 245,310 H360 Z' fill='#3a2a36'/>")
    clock = (f"<circle cx='470' cy='150' r='62' fill='{PANEL}' stroke='{TEXT}' stroke-width='6'/>"
             f"<g class='h2'><rect x='466' y='108' width='8' height='46' rx='4' fill='{TEXT}'/></g>"
             f"<g class='h1'><rect x='468' y='98' width='4' height='56' rx='2' fill='{GOLD}'/></g><circle cx='470' cy='150' r='7' fill='{GOLD}'/>")
    person = (f"<g class='me'><circle cx='250' cy='400' r='34' fill='{LAND}'/>"
              f"<path d='M190,520 Q190,430 250,432 Q310,430 312,520 Z' fill='{LAND}'/>"
              f"<path d='M205,470 Q250,500 300,470' stroke='#34495e' stroke-width='16' fill='none' stroke-linecap='round'/></g>")
    bag = (f"<rect x='420' y='430' width='110' height='90' rx='10' fill='{GOLD}'/><path d='M445,430 Q475,395 505,430' fill='none' stroke='#c48f2f' stroke-width='8'/>"
           f"<g class='notif'><rect x='80' y='445' width='140' height='50' rx='25' fill='{PANEL}' stroke='{GOLD}' stroke-width='3'/>"
           f"<text x='150' y='478' font-size='22' font-weight='800' fill='{GOLD}' text-anchor='middle'>+ ฿ fee</text></g>")
    return _svg(room + clock + person + bag, style)


# ---------------------------------------------------------------- mutual-aid network
def network():
    import math
    style = f"""
    @keyframes flow {{ to {{ stroke-dashoffset: -60; }} }}
    @keyframes glow {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.12); }} }}
    .ln {{ {A('flow', 1.2, timing='linear')} }}
    .nd {{ {A('glow', 2.4, extra='transform-box:fill-box;transform-origin:center;')} }}
    """
    pts = [(300, 300)] + [(300 + 200 * math.cos(a), 300 + 200 * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]]
    lines = "".join(f"<line class='ln' x1='{pts[0][0]}' y1='{pts[0][1]}' x2='{x:.0f}' y2='{y:.0f}' stroke='{GOLD}' stroke-width='4' stroke-dasharray='14 16'/>" for x, y in pts[1:])
    lines += "".join(f"<line x1='{pts[i][0]:.0f}' y1='{pts[i][1]:.0f}' x2='{pts[i % 6 + 1][0]:.0f}' y2='{pts[i % 6 + 1][1]:.0f}' stroke='{LINE}' stroke-width='3'/>" for i in range(1, 7))
    nodes = "".join(f"<g class='nd'><circle cx='{x:.0f}' cy='{y:.0f}' r='44' fill='{PANEL}' stroke='{GOLD if i == 0 else LINE}' stroke-width='4'/>{_person(x, y + 6, .5, GOLD if i == 0 else LAND)}</g>" for i, (x, y) in enumerate(pts))
    return _svg(lines + nodes, style)


ART = {"eye": eye, "family": family, "hook": hook, "documents": documents, "truck": truck,
       "megaphone": megaphone, "hiding": hiding, "network": network}
