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


# ---------------------------------------------------------------- an arm reaching across the border
def reach():
    style = f"""
    @keyframes grab {{ 0%,100% {{ transform: translateX(-150px); }} 45%,60% {{ transform: translateX(0); }} }}
    @keyframes flee {{ 0%,35% {{ transform: translateX(0); }} 50%,62% {{ transform: translateX(26px); }} 100% {{ transform: translateX(0); }} }}
    @keyframes dash {{ to {{ stroke-dashoffset: -40; }} }}
    @keyframes glow {{ 0%,100% {{ opacity: .3; }} 50% {{ opacity: .9; }} }}
    .arm {{ {A('grab', 4)} }} .run {{ {A('flee', 4)} }} .bd {{ {A('dash', 1, timing='linear')} }} .gl {{ {A('glow', 2)} }}
    """
    sides = (f"<text x='150' y='110' font-size='30' font-weight='800' fill='{MUTED}' text-anchor='middle' letter-spacing='3'>MYANMAR</text>"
             f"<text x='450' y='110' font-size='30' font-weight='800' fill='{MUTED}' text-anchor='middle' letter-spacing='3'>THAILAND</text>"
             f"<line class='bd' x1='300' y1='140' x2='300' y2='560' stroke='{GOLD}' stroke-width='6' stroke-dasharray='22 18'/>")
    arm = (f"<g class='arm'><rect x='-120' y='300' width='420' height='46' rx='23' fill='#4a2a30'/>"
           f"<rect x='-140' y='290' width='70' height='66' rx='10' fill='#3a1f25'/>"
           f"<path d='M300,292 q40,-10 56,14 q-24,4 -30,18 q30,4 40,22 q-30,6 -66,0 Z' fill='#4a2a30'/>"
           f"<circle class='gl' cx='356' cy='324' r='40' fill='none' stroke='{RED}' stroke-width='4'/></g>")
    person = f"<g class='run'>{_person(440, 360, 1.1, LAND)}</g>"
    return _svg(sides + person + arm, style)


# ---------------------------------------------------------------- globe with arrows crossing a border
def globe():
    style = f"""
    @keyframes spin {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-120px); }} }}
    @keyframes arc {{ from {{ stroke-dashoffset: 520; }} 60%,100% {{ stroke-dashoffset: 0; }} }}
    @keyframes hit {{ 0%,55% {{ transform: scale(0); }} 65% {{ transform: scale(1.3); }} 75%,100% {{ transform: scale(1); }} }}
    .mer {{ {A('spin', 4, timing='linear')} }}
    .a1 {{ {A('arc', 3.2, 0, timing='ease-out')} }} .a2 {{ {A('arc', 3.2, 1.6, timing='ease-out')} }}
    .t1 {{ {A('hit', 3.2, 0, extra='transform-origin:455px 210px;')} }} .t2 {{ {A('hit', 3.2, 1.6, extra='transform-origin:470px 400px;')} }}
    """
    mer = "".join(f"<ellipse cx='{x}' cy='300' rx='60' ry='200' fill='none' stroke='{LINE}' stroke-width='3'/>" for x in range(120, 600, 120))
    lat = "".join(f"<line x1='100' y1='{y}' x2='500' y2='{y}' stroke='{LINE}' stroke-width='3'/>" for y in (200, 300, 400))
    globe = (f"<defs><clipPath id='gc'><circle cx='300' cy='300' r='200'/></clipPath></defs>"
             f"<circle cx='300' cy='300' r='200' fill='{PANEL}' stroke='{GOLD}' stroke-width='5'/>"
             f"<g clip-path='url(#gc)'>{lat}<g class='mer'>{mer}</g>"
             f"<path d='M190,240 q30,-40 70,-10 q20,40 -10,80 q-50,20 -60,-70 Z' fill='{LAND}'/></g>")
    arcs = (f"<path class='a1' d='M230,280 Q330,80 455,210' fill='none' stroke='{RED}' stroke-width='6' stroke-dasharray='520' stroke-linecap='round'/>"
            f"<path class='a2' d='M240,300 Q380,470 470,400' fill='none' stroke='{RED}' stroke-width='6' stroke-dasharray='520' stroke-linecap='round'/>"
            f"<g class='t1'><circle cx='455' cy='210' r='20' fill='{RED}'/>{_person(455, 220, .3, '#fff')}</g>"
            f"<g class='t2'><circle cx='470' cy='400' r='20' fill='{RED}'/>{_person(470, 410, .3, '#fff')}</g>")
    return _svg(globe + arcs, style)


# ---------------------------------------------------------------- testimony waveform + microphone
def waveform():
    import random as _r
    rnd = _r.Random(7)
    style = f"""
    @keyframes bar {{ 0%,100% {{ transform: scaleY(.25); }} 50% {{ transform: scaleY(1); }} }}
    @keyframes ring {{ from {{ transform: scale(.8); opacity: .8; }} to {{ transform: scale(1.5); opacity: 0; }} }}
    .rg {{ {A('ring', 2, timing='ease-out', extra='transform-origin:300px 170px;')} }}
    """
    bars = ""
    for i in range(17):
        x = 60 + i * 30
        h = 60 + 220 * abs(math.sin(i * .55)) * rnd.uniform(.5, 1)
        d = rnd.uniform(0, 1.2)
        dur = rnd.uniform(.7, 1.3)
        bars += (f"<rect x='{x}' y='{440 - h / 2:.0f}' width='16' height='{h:.0f}' rx='8' fill='{GOLD if i % 4 else RED}' "
                 f"style='animation:bar {dur:.2f}s ease-in-out infinite both;animation-delay:calc(var(--t0)*-1s + {d:.2f}s);"
                 f"transform-box:fill-box;transform-origin:center'/>")
    mic = (f"<circle class='rg' cx='300' cy='170' r='80' fill='none' stroke='{GOLD}' stroke-width='4'/>"
           f"<rect x='262' y='90' width='76' height='130' rx='38' fill='{PANEL}' stroke='{TEXT}' stroke-width='6'/>"
           + "".join(f"<line x1='276' y1='{y}' x2='324' y2='{y}' stroke='{LINE}' stroke-width='4'/>" for y in (120, 140, 160, 180))
           + f"<path d='M240,180 q0,70 60,70 q60,0 60,-70' fill='none' stroke='{TEXT}' stroke-width='6'/><line x1='300' y1='250' x2='300' y2='285' stroke='{TEXT}' stroke-width='6'/>")
    return _svg(mic + bars, style)


# ---------------------------------------------------------------- phone flashing a warning
def alert():
    style = f"""
    @keyframes buzz {{ 0%,40%,100% {{ transform: rotate(0); }} 5%,15%,25%,35% {{ transform: rotate(-6deg); }} 10%,20%,30% {{ transform: rotate(6deg); }} }}
    @keyframes flash {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: 1; }} }}
    @keyframes wave {{ from {{ transform: scale(.7); opacity: .8; }} to {{ transform: scale(1.6); opacity: 0; }} }}
    .ph {{ {A('buzz', 1.8, extra='transform-origin:300px 300px;')} }} .fl {{ {A('flash', .9)} }}
    .w1 {{ {A('wave', 1.8, 0, timing='ease-out', extra='transform-origin:300px 300px;')} }} .w2 {{ {A('wave', 1.8, .9, timing='ease-out', extra='transform-origin:300px 300px;')} }}
    """
    body = (f"<circle class='w1' cx='300' cy='300' r='170' fill='none' stroke='{RED}' stroke-width='6'/>"
            f"<circle class='w2' cx='300' cy='300' r='170' fill='none' stroke='{RED}' stroke-width='6'/>"
            f"<g class='ph'><rect x='210' y='130' width='180' height='340' rx='30' fill='{PANEL}' stroke='{TEXT}' stroke-width='8'/>"
            f"<path class='fl' d='M300,200 L380,350 L220,350 Z' fill='{RED}'/><rect x='292' y='240' width='16' height='60' rx='8' fill='#fff'/>"
            f"<circle cx='300' cy='322' r='10' fill='#fff'/><rect x='260' y='400' width='80' height='16' rx='8' fill='{LINE}'/></g>")
    return _svg(body, style)


# ---------------------------------------------------------------- three-finger salute
def salute():
    style = f"""
    @keyframes rise {{ 0%,100% {{ transform: translateY(14px); }} 50% {{ transform: translateY(-14px); }} }}
    @keyframes rays {{ to {{ transform: rotate(360deg); }} }}
    .hand {{ {A('rise', 3)} }} .rays {{ {A('rays', 18, timing='linear', extra='transform-origin:300px 300px;')} }}
    """
    rays = "<g class='rays'>" + "".join(
        f"<path d='M300,300 L{300 + 320 * math.cos(a):.0f},{300 + 320 * math.sin(a):.0f} L{300 + 320 * math.cos(a + .14):.0f},{300 + 320 * math.sin(a + .14):.0f} Z' fill='{GOLD}' opacity='.12'/>"
        for a in [i * math.pi / 8 for i in range(16)]) + "</g>"
    hand = (f"<g class='hand'><rect x='225' y='290' width='150' height='170' rx='40' fill='{GOLD}'/>"
            + "".join(f"<rect x='{x}' y='{y}' width='40' height='{h}' rx='20' fill='{GOLD}'/>" for x, y, h in ((228, 140, 190), (280, 115, 215), (332, 140, 190)))
            + f"<rect x='370' y='300' width='40' height='70' rx='20' fill='#c48f2f'/>"
            f"<path d='M215,330 q-20,40 30,70' fill='none' stroke='#c48f2f' stroke-width='34' stroke-linecap='round'/>"
            f"<rect x='250' y='460' width='100' height='120' fill='{GOLD}'/></g>")
    return _svg(rays + hand, style)


# ---------------------------------------------------------------- four tools (icons in tiles)
def tools():
    style = f"""
    @keyframes hl {{ 0%,20%,100% {{ stroke: {LINE}; transform: scale(1); }} 6%,14% {{ stroke: {GOLD}; transform: scale(1.08); }} }}
    """
    icons = [
        f"<rect x='-26' y='-46' width='52' height='92' rx='10' fill='none' stroke='{TEXT}' stroke-width='6'/><path d='M0,-20 L20,16 L-20,16 Z' fill='{RED}'/>",
        f"<path d='M-50,0 L0,-40 L50,0 Z' fill='{TEXT}'/><rect x='-38' y='0' width='76' height='46' fill='{TEXT}'/><rect x='-10' y='16' width='20' height='30' fill='{PANEL}'/>",
        f"<rect x='-48' y='-32' width='96' height='64' rx='8' fill='#e9e3d4'/><rect x='-38' y='-20' width='26' height='34' rx='4' fill='#bdb4a0'/><rect x='-4' y='-16' width='40' height='8' rx='4' fill='#bdb4a0'/><rect x='-4' y='0' width='30' height='8' rx='4' fill='#bdb4a0'/>",
        f"<path d='M-50,0 Q0,-44 50,0 Q0,44 -50,0 Z' fill='none' stroke='{TEXT}' stroke-width='6'/><circle r='16' fill='{GOLD}'/>",
    ]
    tiles = ""
    for i, (x, y) in enumerate(((165, 165), (435, 165), (165, 435), (435, 435))):
        tiles += (f"<g style='animation:hl 4s ease-in-out infinite both;animation-delay:calc(var(--t0)*-1s + {i}s);transform-box:fill-box;transform-origin:center'"
                  f" stroke='{LINE}'><rect x='{x - 115}' y='{y - 115}' width='230' height='230' rx='34' fill='{PANEL}' stroke-width='6'/></g>"
                  f"<g transform='translate({x} {y}) scale(1.3)'>{icons[i]}</g>")
    return _svg(tiles, style)


# ---------------------------------------------------------------- protective shield
def shield():
    style = f"""
    @keyframes pulse {{ from {{ transform: scale(.85); opacity: .7; }} to {{ transform: scale(1.35); opacity: 0; }} }}
    @keyframes draw {{ from {{ stroke-dashoffset: 200; }} 40%,100% {{ stroke-dashoffset: 0; }} }}
    .p1 {{ {A('pulse', 2.4, 0, timing='ease-out', extra='transform-origin:300px 300px;')} }} .p2 {{ {A('pulse', 2.4, 1.2, timing='ease-out', extra='transform-origin:300px 300px;')} }}
    .ck {{ {A('draw', 3, timing='ease-out')} }}
    """
    sh = "M300,100 L470,160 Q470,400 300,500 Q130,400 130,160 Z"
    body = (f"<path class='p1' d='{sh}' fill='none' stroke='{GOLD}' stroke-width='5'/><path class='p2' d='{sh}' fill='none' stroke='{GOLD}' stroke-width='5'/>"
            f"<path d='{sh}' fill='{PANEL}' stroke='{GOLD}' stroke-width='10'/>"
            f"{_person(300, 300, 1.1, LAND)}"
            f"<path class='ck' d='M360,380 l30,30 l60,-70' fill='none' stroke='{GREEN}' stroke-width='18' stroke-linecap='round' stroke-linejoin='round' stroke-dasharray='200'/>")
    return _svg(body, style)


# ---------------------------------------------------------------- subscribe bell
def bell():
    style = f"""
    @keyframes ring {{ 0%,50%,100% {{ transform: rotate(0); }} 5%,15%,25% {{ transform: rotate(-16deg); }} 10%,20%,30% {{ transform: rotate(16deg); }} }}
    @keyframes wave {{ from {{ transform: scale(.7); opacity: .8; }} to {{ transform: scale(1.5); opacity: 0; }} }}
    .bl {{ {A('ring', 2, extra='transform-origin:300px 130px;')} }} .w {{ {A('wave', 2, timing='ease-out', extra='transform-origin:300px 300px;')} }}
    """
    body = (f"<circle class='w' cx='300' cy='300' r='190' fill='none' stroke='{GOLD}' stroke-width='6'/>"
            f"<g class='bl'><path d='M300,130 q-110,0 -110,140 v80 l-40,50 h300 l-40,-50 v-80 q0,-140 -110,-140 Z' fill='{GOLD}'/>"
            f"<circle cx='300' cy='120' r='18' fill='{GOLD}'/><circle cx='300' cy='430' r='34' fill='#c48f2f'/></g>"
            f"<circle cx='400' cy='170' r='34' fill='{RED}'/><text x='400' y='183' font-size='38' font-weight='900' fill='#fff' text-anchor='middle'>1</text>")
    return _svg(body, style)


import math  # noqa: E402  (used by the illustrations above)

ART.update({"reach": reach, "globe": globe, "waveform": waveform, "alert": alert, "salute": salute,
            "tools": tools, "shield": shield, "bell": bell})


# ---------------------------------------------------------------- ballot box with "FRAUD?" claim
def ballot():
    style = f"""
    @keyframes drop {{ 0%,10% {{ transform: translateY(-200px); opacity: 0; }} 25% {{ opacity: 1; }} 45%,100% {{ transform: translateY(0); opacity: 1; }} }}
    @keyframes stamp {{ 0%,50% {{ transform: rotate(-12deg) scale(2.2); opacity: 0; }} 60% {{ transform: rotate(-12deg) scale(.95); opacity: 1; }} 65%,95% {{ transform: rotate(-12deg) scale(1); opacity: 1; }} 100% {{ opacity: 0; }} }}
    .v {{ {A('drop', 4.5, timing='ease-in')} }}
    .st {{ {A('stamp', 4.5, timing='ease-out', extra='transform-origin:300px 380px;')} }}
    """
    paper = (f"<g class='v'><rect x='250' y='150' width='100' height='130' rx='8' fill='#e9e3d4'/>"
             f"<rect x='266' y='172' width='24' height='24' rx='4' fill='none' stroke='{LAND}' stroke-width='4'/><path d='M270,184 l6,8 l12,-16' stroke='{GREEN}' stroke-width='5' fill='none'/>"
             f"<rect x='298' y='178' width='40' height='10' rx='5' fill='#bdb4a0'/><rect x='266' y='214' width='24' height='24' rx='4' fill='none' stroke='{LAND}' stroke-width='4'/>"
             f"<rect x='298' y='220' width='34' height='10' rx='5' fill='#bdb4a0'/></g>")
    box = (f"<rect x='150' y='290' width='300' height='240' rx='16' fill='{LAND}' stroke='{LINE}' stroke-width='4'/>"
           f"<rect x='130' y='270' width='340' height='40' rx='10' fill='#3a4f63'/><rect x='240' y='282' width='120' height='14' rx='7' fill='{NAVY}'/>"
           f"<text x='300' y='440' font-size='44' font-weight='900' fill='{TEXT}' text-anchor='middle' letter-spacing='6'>VOTE</text>")
    stamp = (f"<g class='st'><rect x='170' y='340' width='260' height='84' rx='10' fill='rgba(14,20,27,.6)' stroke='{RED}' stroke-width='8'/>"
             f"<text x='300' y='398' font-size='50' font-weight='900' fill='{RED}' text-anchor='middle' letter-spacing='4'>FRAUD?</text></g>")
    return _svg(paper + box + stamp, style)


# ---------------------------------------------------------------- banging pots and pans
def pots():
    style = f"""
    @keyframes hitL {{ 0%,100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(-38deg); }} }}
    @keyframes hitR {{ 0%,100% {{ transform: rotate(0deg); }} 50% {{ transform: rotate(38deg); }} }}
    @keyframes clang {{ 0%,40%,100% {{ opacity: 0; transform: scale(.6); }} 50% {{ opacity: 1; transform: scale(1.1); }} }}
    @keyframes note {{ from {{ transform: translate(0,0); opacity: 1; }} to {{ transform: translate(var(--x), -180px); opacity: 0; }} }}
    .sL {{ {A('hitL', .5, extra='transform-origin:190px 330px;')} }} .sR {{ {A('hitR', .5, .25, extra='transform-origin:410px 330px;')} }}
    .cl {{ {A('clang', .5, extra='transform-box:fill-box;transform-origin:center;')} }} .cl2 {{ {A('clang', .5, .25, extra='transform-box:fill-box;transform-origin:center;')} }}
    .n1 {{ {A('note', 2, 0, timing='linear')} --x:-80px; }} .n2 {{ {A('note', 2, .7, timing='linear')} --x:60px; }} .n3 {{ {A('note', 2, 1.4, timing='linear')} --x:-20px; }}
    """
    pot = lambda x: (f"<path d='M{x-90},360 h180 v60 q0,60 -60,60 h-60 q-60,0 -60,-60 Z' fill='#9aa5b1'/>"
                     f"<rect x='{x-100}' y='350' width='200' height='18' rx='9' fill='#c6d0da'/><rect x='{x+95}' y='372' width='60' height='14' rx='7' fill='#6d7884'/>")
    spoon = lambda cls, x: f"<g class='{cls}'><rect x='{x-6}' y='190' width='12' height='150' rx='6' fill='{GOLD}'/><ellipse cx='{x}' cy='190' rx='22' ry='30' fill='{GOLD}'/></g>"
    burst = lambda cls, x: f"<g class='{cls}'>" + "".join(f"<line x1='{x}' y1='330' x2='{x + dx}' y2='{330 + dy}' stroke='{GOLD}' stroke-width='6' stroke-linecap='round'/>" for dx, dy in ((-40, -30), (0, -50), (40, -30))) + "</g>"
    notes = "".join(f"<text class='{c}' x='{x}' y='300' font-size='54' fill='{TEXT}'>♪</text>" for x, c in ((150, 'n1'), (300, 'n2'), (430, 'n3')))
    return _svg(pot(190) + pot(410) + burst('cl', 190) + burst('cl2', 410) + spoon('sL', 190) + spoon('sR', 410) + notes, style)


# ---------------------------------------------------------------- earthquake: seismograph + shaking buildings
def quake():
    style = f"""
    @keyframes scroll {{ to {{ transform: translateX(-300px); }} }}
    @keyframes shake {{ 0%,100% {{ transform: translate(0,0) rotate(0); }} 20% {{ transform: translate(-6px,2px) rotate(-1.5deg); }} 40% {{ transform: translate(6px,-2px) rotate(1.5deg); }}
        60% {{ transform: translate(-4px,1px) rotate(-1deg); }} 80% {{ transform: translate(4px,0) rotate(1deg); }} }}
    @keyframes fall {{ 0%,60% {{ transform: translateY(0); opacity: 1; }} 100% {{ transform: translateY(120px); opacity: 0; }} }}
    .wave {{ {A('scroll', 1.6, timing='linear')} }}
    .b1 {{ {A('shake', .35, extra='transform-origin:180px 520px;')} }} .b2 {{ {A('shake', .3, .1, extra='transform-origin:330px 520px;')} }} .b3 {{ {A('shake', .4, .2, extra='transform-origin:460px 520px;')} }}
    .d1 {{ {A('fall', 1.4, 0, timing='ease-in')} }} .d2 {{ {A('fall', 1.4, .5, timing='ease-in')} }}
    """
    import random as _r
    rnd = _r.Random(3)
    pts, x = [], 0
    while x <= 900:
        amp = 70 if 300 < x % 600 < 420 else 12
        pts.append(f"{x},{150 + rnd.uniform(-amp, amp):.0f}")
        x += 12
    seis = (f"<rect x='40' y='60' width='520' height='180' rx='16' fill='{PANEL}' stroke='{LINE}' stroke-width='3'/>"
            f"<defs><clipPath id='sc'><rect x='50' y='70' width='500' height='160'/></clipPath></defs>"
            f"<g clip-path='url(#sc)'><g class='wave'><polyline points='{' '.join(pts)}' fill='none' stroke='{RED}' stroke-width='4' transform='translate(50,0)'/></g></g>"
            f"<text x='520' y='100' font-size='30' font-weight='900' fill='{GOLD}' text-anchor='end'>7.7</text>")
    bld = lambda cls, x, w, h: (f"<g class='{cls}'><rect x='{x}' y='{520-h}' width='{w}' height='{h}' fill='{LAND}' stroke='{LINE}' stroke-width='3'/>"
                                + "".join(f"<rect x='{x+14+c*28}' y='{520-h+16+r*36}' width='16' height='20' fill='{GOLD}' opacity='.6'/>" for r in range(int(h // 36) - 1) for c in range(int((w - 14) // 28))) + "</g>")
    ground = f"<rect x='0' y='520' width='600' height='14' fill='{LINE}'/><path d='M260,520 l20,14 l-12,14 l18,14' stroke='{RED}' stroke-width='5' fill='none'/>"
    debris = f"<rect class='d1' x='300' y='300' width='18' height='14' fill='{MUTED}'/><rect class='d2' x='200' y='330' width='14' height='12' fill='{MUTED}'/>"
    return _svg(seis + bld('b1', 110, 140, 230) + bld('b2', 270, 120, 190) + bld('b3', 400, 120, 260) + ground + debris, style)


# ---------------------------------------------------------------- calendar flipping through the years
def calendar():
    years = ["1948", "1962", "1988", "2011", "2015", "2021"]
    n, cyc = len(years), 7.2
    style = f"""
    @keyframes yr {{ 0% {{ opacity: 0; transform: translateY(40px); }} 4%,{100/n - 3:.1f}% {{ opacity: 1; transform: translateY(0); }} {100/n:.1f}%,100% {{ opacity: 0; transform: translateY(-40px); }} }}
    @keyframes flip {{ 0%,80% {{ transform: rotateX(0deg); }} 100% {{ transform: rotateX(-90deg); }} }}
    @keyframes bar {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    .pg {{ {A('flip', cyc / n, timing='ease-in', extra='transform-origin:300px 200px;')} }}
    .prog {{ {A('bar', cyc, timing='linear', extra='transform-origin:150px 500px;')} }}
    """
    labels = "".join(f"<text x='300' y='365' font-size='120' font-weight='900' fill='{RED if y == '2021' else TEXT}' text-anchor='middle' "
                     f"style='animation:yr {cyc}s linear infinite both;animation-delay:calc(var(--t0)*-1s + {i * cyc / n:.2f}s)'>{y}</text>" for i, y in enumerate(years))
    cal = (f"<rect x='130' y='150' width='340' height='300' rx='24' fill='{PANEL}' stroke='{LINE}' stroke-width='4'/>"
           f"<rect x='130' y='150' width='340' height='70' rx='24' fill='{RED}'/><rect x='130' y='190' width='340' height='30' fill='{RED}'/>"
           f"<rect x='200' y='120' width='18' height='60' rx='9' fill='{TEXT}'/><rect x='382' y='120' width='18' height='60' rx='9' fill='{TEXT}'/>"
           f"<g class='pg'><rect x='150' y='230' width='300' height='14' rx='7' fill='{LINE}' opacity='.5'/></g>")
    prog = (f"<rect x='150' y='494' width='300' height='12' rx='6' fill='{LINE}'/>"
            f"<rect class='prog' x='150' y='494' width='300' height='12' rx='6' fill='{GOLD}'/>")
    return _svg(cal + labels + prog, style)


ART.update({"ballot": ballot, "pots": pots, "quake": quake, "calendar": calendar})
