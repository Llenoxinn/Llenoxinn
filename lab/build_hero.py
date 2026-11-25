#!/usr/bin/env python3
"""Build the hero: Dexter behind two gold gauntlet blocks.

DEXTER (light): the blocks read DEX and TER and punch forward in three snapped
steps, then a gold glint crosses them now and then. The lab behind is prussian
steel with a keyhole doorway glowing warm behind his head.

XED (dark): the same shot at night. The DEX block is turned over so it reads XED;
every few seconds it turns back and snaps over again in stepped frames. The TER
fist hangs lower, scorched and smoking, flames lick the floor and spill drips
from the ceiling.

Ships wide and narrow (phones), each animated and still. Usage:
    python lab/build_hero.py            # writes assets/
    python lab/build_hero.py --preview  # writes lab/.runtime/preview/
"""
import math
import random
import sys
from pathlib import Path

import kid
from notebook import ASSETS, ROOT, Typesetter, frames, svg_doc
from toon import INK, PHOENIX as C, clipped, defs as toon_defs, f, fold, inked, limb, rpoly, smooth

NAME = "Dexter Juevesano"
HANDLE = "@Llenoxinn"
SIGN = "dexterslab"
LINE = {"light": "I build things that ship.", "dark": "I break things to see how they work."}

LAYOUTS = {
    "wide": dict(w=880, h=400, floor=330, k=0.64, tx=410, ty=8, block=(168, 96), blocks=((462, 300), (746, 300)),
                 reach=((-196, 456), (196, 456)), key=(602, 96, 122), counter=348,
                 leaks=((112, 150, 16, 3), (392, 210, 13, 5), (812, 120, 14, 8)), clouds=((300, 52, 40, 7), (840, 214, 50, 9)),
                 sign=(44, 116, 74, "start"), plate=(44, 154, 300, 70), line=(46, 262, 19, "start"), line_xed=8, shelf=True),
    "narrow": dict(w=400, h=580, floor=300, k=0.5, tx=50, ty=12, block=(124, 72), blocks=((92, 250), (308, 250)),
                   reach=((-196, 456), (196, 456)), key=(200, 84, 96), counter=290,
                   leaks=((30, 120, 12, 3), (372, 140, 12, 8)), clouds=((340, 236, 36, 9),),
                   sign=(200, 392, 56, "middle"), plate=(56, 428, 288, 66), line=(200, 534, 16.5, "middle"), line_xed=24, shelf=False),
}

LIGHT = dict(wall=C["prussian"], seam=C["navy"], rivet_hi="#2F4A94", shaft="#22397A", floor="#E6D6B6", floor_line="#C9B48C",
             key=[C["glint"], C["gold"], "#FF8A1E", C["phoenix"], C["crimson"]], text=C["bone"],
             plate=C["bone"], plate_text=INK, machine=C["navy"])
DARK = dict(wall="#0E1A3A", seam="#070C1E", rivet_hi="#1C2C5C", shaft=None, floor="#1A0A12", floor_line="#3A1020",
            key=[C["gold"], C["phoenix"], C["crimson"], C["oxblood"], "#2A0610"], text=C["bone"],
            plate=C["oxblood"], plate_text=C["bone"], machine="#070C1E")


# ------------------------------------------------------------------ set dressing

def cloud(cx, cy, r, n, fill, seed, sw=5):
    """MAIN-poster smoke: a union of puffs with spiral curls."""
    rnd = random.Random(seed)
    circles = []
    for i in range(n):
        a = i / n * math.tau
        circles.append((cx + math.cos(a) * r * .7, cy + math.sin(a) * r * .45, r * rnd.uniform(.45, .7)))
    circles.append((cx, cy, r * .75))
    s = [f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(c + sw / 2)}" fill="{INK}"/>' for a, b, c in circles]
    s += [f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(c)}" fill="{fill}"/>' for a, b, c in circles]
    for a, b, c in circles[:n:2]:
        s.append(f'<path d="M{f(a - c * .35)},{f(b)} a{f(c * .35)},{f(c * .35)} 0 1 1 {f(c * .35)},{f(c * .35)} '
                 f'a{f(c * .18)},{f(c * .18)} 0 1 1 {f(-c * .12)},{f(-c * .2)}" fill="none" stroke="{INK}" '
                 f'stroke-width="2.6" opacity=".6" stroke-linecap="round"/>')
    return "".join(s)


def flames(x0, x1, base, hmax, seed):
    rnd = random.Random(seed)
    out = []
    for k, col in enumerate((C["crimson"], C["phoenix"], C["gold"])):
        d, x = f"M{f(x0)},{f(base)} ", x0
        while x < x1:
            w = rnd.uniform(30, 62)
            hh = hmax * (1 - k * .3) * rnd.uniform(.55, 1)
            lean = rnd.uniform(-12, 12)
            d += (f"Q{f(x + w * .05)},{f(base - hh * .55)} {f(x + w * .5 + lean)},{f(base - hh)} "
                  f"Q{f(x + w * .62)},{f(base - hh * .5)} {f(x + w)},{f(base - hh * .12)} ")
            x += w
        d += f"L{f(x1)},{f(base)} Z"
        out.append(f'<path d="{d}" fill="{col}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    return "".join(out)


def leak(x, y0, length, width, seed, floor):
    """Spill leaking from a cracked pipe joint onto the steel wall: it gathers in a lumpy
    splash under the joint, then runs down in uneven streams that thin out and end in
    hanging bulbs. Around it the acid has eaten the paint: a dark green-black stain with
    pitted specks. One union outline, like everything else in the drawing."""
    rnd = random.Random(seed)
    # the splash under the joint
    n = 10
    pts = [(x + math.cos(i / n * math.tau) * width * rnd.uniform(.9, 1.5), y0 + 10 + math.sin(i / n * math.tau) * width * rnd.uniform(.45, .8))
           for i in range(n)]
    shapes = [smooth(pts)]
    ends = []
    runs = [(0, 1.0, .62)] + [(rnd.uniform(-.9, .9) * width, rnd.uniform(.25, .55), rnd.uniform(.38, .5)) for _ in range(2)]
    for dx, frac, wk in runs:
        ln = length * frac
        cl = [(x + dx + math.sin(k * 1.7 + seed) * 2.4, y0 + 10 + ln * k / 5) for k in range(6)]
        ws = [width * wk * (1 - .45 * k / 5) * (1.35 if k == 3 else 1) for k in range(6)]
        shapes.append(limb(cl, ws))
        bx, by = cl[-1]
        br = ws[-1] * .9
        shapes.append(f"M{f(bx - br)},{f(by + br * .4)} a{f(br)},{f(br * 1.2)} 0 1 0 {f(2 * br)},0 a{f(br)},{f(br * 1.2)} 0 1 0 {f(-2 * br)},0")
        ends.append((bx, by + br * 1.6))
    stain = "".join(f'<path d="{d}" fill="#0B2620" stroke="#0B2620" stroke-width="{f(width * 1.1)}" stroke-linejoin="round"/>' for d in shapes)
    specks = "".join(f'<circle cx="{f(x + rnd.uniform(-1.6, 1.6) * width)}" cy="{f(y0 + 8 + rnd.uniform(0, length * .9))}" r="{f(rnd.uniform(.8, 2.2))}" fill="#06140F"/>'
                     for _ in range(14))
    s = [f'<g opacity=".8" filter="url(#chalk)">{stain}</g>', specks]
    s.append(inked(shapes, C["spill"], 1.6, grain=None, extra="".join(
        clipped(f"lk{seed}{i}", d, f'<rect x="{f(x + 1)}" y="{y0}" width="{f(width * 3)}" height="{f(length + 60)}" fill="{C["spill_dk"]}" opacity=".55"/>')
        for i, d in enumerate(shapes))))
    for dx, frac, wk in runs:
        ln = length * frac
        s.append(fold([(x + dx - width * wk * .22, y0 + 16), (x + dx - width * wk * .24, y0 + 10 + ln * .4), (x + dx - width * wk * .16, y0 + 10 + ln * .7)],
                      max(1.6, width * wk * .2), C["spill_hi"]))
    s.append(f'<path d="M{f(x - 8)},{y0 - 1} l5,-7 l4,5 l5,-8" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    main = ends[0]
    return "".join(s), main


def falling_drop(x, y, floor, begin, animate):
    """A drop lets go of the bulb and falls in four snapped frames, then splats on the floor."""
    d = f'<path d="M{f(x)},{f(y)} q6,9 0,13 q-6,-4 0,-13z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.6"/>'
    if not animate:
        return ""
    fall = floor - y
    vals = ";".join(f"0 {f(v)}" for v in (0, 0, fall * .2, fall * .5, fall * .95, fall * .95))
    return (f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;1;1;0" keyTimes="0;.5;.6;.7;.8;.9" calcMode="discrete" '
            f'dur="2.6s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="0;.5;.6;.7;.8;.9" '
            f'calcMode="discrete" dur="2.6s" begin="{begin}s" repeatCount="indefinite"/>{d}</g>')


def keyhole(cx, cy, r, bands, uid, xed):
    d = (f"M{f(cx - r)},{f(cy + r * .4)} a{f(r)},{f(r)} 0 1 1 {f(2 * r)},0 c0,{f(r * .4)} {f(-r * .24)},{f(r * .62)} {f(-r * .42)},{f(r * .8)} "
         f"l{f(r * .62)},{f(r * 2.3)} h{f(-r * 2.4)} l{f(r * .62)},{f(-r * 2.3)} c{f(-r * .18)},{f(-r * .18)} {f(-r * .42)},{f(-r * .4)} {f(-r * .42)},{f(-r * .8)}z")
    inner = "".join(f'<rect x="{f(cx - r * 1.6)}" y="{f(cy - r * 1.2 + i * r * .78)}" width="{f(r * 3.2)}" height="{f(r * .82)}" fill="{c}"/>'
                    for i, c in enumerate(bands))
    inner += f'<circle cx="{f(cx)}" cy="{f(cy + r * .2)}" r="{f(r * .42)}" fill="{C["glint"]}"/>'
    if not xed:  # a cloud and a bird out in the daylight, the MAIN TEXTURE keyhole
        inner += cloud(cx + r * .5, cy + r * 1.1, r * .32, 5, "#FFF6E0", 4, 3)
    return clipped(f"kh{uid}", d, inner) + f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'


def wall(L, P, xed, uid):
    w, h, fy = L["w"], L["h"], L["floor"]
    s = [f'<rect width="{w}" height="{h}" fill="{P["wall"]}"/>']
    if P["shaft"]:
        s.append(f'<polygon points="{f(w * .08)},0 {f(w * .3)},0 {f(w * .52)},{fy} {f(w * .22)},{fy}" fill="{P["shaft"]}" opacity=".75"/>')
    step = 110 if w > 500 else 100
    for i, x in enumerate(range(step, w, step)):
        s.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{fy}" stroke="{P["seam"]}" stroke-width="5"/>')
        for y in range(26, fy - 10, 56):
            s.append(f'<circle cx="{x - 13}" cy="{y}" r="4" fill="{P["seam"]}"/><circle cx="{x - 14}" cy="{y - 1}" r="1.8" fill="{P["rivet_hi"]}"/>')
    cx, cy, r = L["key"]
    s.append(keyhole(cx, cy, r, P["key"], uid, xed))
    # pipes along the ceiling and a tank on the right edge frame the shot
    s.append(inked(rpoly([(-10, 10), (w + 10, 10), (w + 10, 30), (-10, 30)], 4), P["machine"], 3))
    for x in range(60, w, 150):
        s.append(f'<rect x="{x}" y="6" width="16" height="28" rx="3" fill="{P["seam"]}" stroke="{INK}" stroke-width="3"/>')
    tx = w - 58
    s.append(inked(rpoly([(tx, 70), (w + 40, 70), (w + 40, fy + 6), (tx, fy + 6)], [26, 4, 4, 4]), P["machine"], 3.4))
    for y in range(100, fy - 20, 40):
        s.append(f'<line x1="{tx + 10}" y1="{y}" x2="{w}" y2="{y}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<circle cx="{tx + 26}" cy="{fy - 40}" r="13" fill="{C["spill"] if xed else C["gold"]}" stroke="{INK}" stroke-width="4"/>')
    # floor
    s.append(f'<rect x="-5" y="{fy}" width="{w + 10}" height="{h - fy + 5}" fill="{P["floor"]}" stroke="{INK}" stroke-width="5"/>')
    for i in range(-9, 11):
        s.append(f'<line x1="{f(w / 2 + i * 50)}" y1="{fy}" x2="{f(w / 2 + i * 140)}" y2="{h}" stroke="{P["floor_line"]}" stroke-width="3"/>')
    return "".join(s)


def flask(x, y, sc, liquid, uid, animate, bubbling):
    """A conical flask; bubbles climb out of it in steps when animated."""
    body = rpoly([(x - 6 * sc, y - 40 * sc), (x + 6 * sc, y - 40 * sc), (x + 6 * sc, y - 24 * sc), (x + 22 * sc, y),
                  (x - 22 * sc, y), (x - 6 * sc, y - 24 * sc)], [2, 2, 3, 6, 6, 3])
    liq = f'<rect x="{f(x - 30 * sc)}" y="{f(y - 14 * sc)}" width="{f(60 * sc)}" height="{f(20 * sc)}" fill="{liquid}"/>'
    s = [inked(body, "#D8EEF2", 2.6, extra=clipped(f"fl{uid}{x}", body, liq))]
    s.append(fold([(x - 2 * sc, y - 34 * sc), (x - 2 * sc, y - 26 * sc)], 2.2, "#FFFFFF"))
    if bubbling:
        for i, (bx, r) in enumerate(((-3, 4), (4, 3), (0, 5))):
            b = f'<circle cx="{f(x + bx * sc)}" cy="{f(y - 46 * sc)}" r="{f(r * sc)}" fill="{liquid}" stroke="{INK}" stroke-width="2"/>'
            if animate:
                b = (f'<g opacity="0">{b}<animate attributeName="opacity" values="0;1;1;1;0" keyTimes="0;.2;.45;.7;.9" calcMode="discrete" '
                     f'dur="1.8s" begin="{i * .6:.1f}s" repeatCount="indefinite"/>'
                     f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 -12;0 -18;0 -18" '
                     f'keyTimes="0;.2;.45;.7;.9" calcMode="discrete" dur="1.8s" begin="{i * .6:.1f}s" repeatCount="indefinite"/></g>')
            elif i:
                continue
            s.append(b)
    return "".join(s)


def shelf(L, xed, uid, animate):
    """Bottom-left bench clutter: the mess that keeps the text side from going empty."""
    fy = L["floor"]
    s = [inked(rpoly([(34, fy - 34), (352, fy - 34), (352, fy - 20), (34, fy - 20)], 3), "#5B6478" if not xed else "#2A2F44", 3)]
    s.append(f'<rect x="48" y="{fy - 20}" width="12" height="22" fill="{INK}"/><rect x="326" y="{fy - 20}" width="12" height="22" fill="{INK}"/>')
    s.append(flask(80, fy - 34, 1, C["spill"], uid, animate, True))
    s.append(flask(126, fy - 34, .8, C["crimson"] if not xed else C["phoenix"], uid, animate, False))
    # a wrench and a coil of cable on the bench
    s.append(f'<g transform="rotate(-12 200 {fy - 40})">' + inked(rpoly([(160, fy - 44), (232, fy - 44), (232, fy - 36), (160, fy - 36)], 3), "#9AA3B8", 2.4)
             + inked(f"M226,{fy - 52} a12,12 0 1 1 0,24 l-4,-8 l4,-4 l-4,-4z", "#9AA3B8", 2.4) + "</g>")
    s.append(f'<path d="M262,{fy - 36} q16,-26 34,-6 q18,20 -6,24 q-24,4 -10,-16" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
             f'<path d="M262,{fy - 36} q16,-26 34,-6 q18,20 -6,24 q-24,4 -10,-16" fill="none" stroke="{C["crimson"]}" stroke-width="4" stroke-linecap="round"/>')
    return "".join(s)


# ------------------------------------------------------------------ gold blocks

BLOCK_FACE = dict(face="block", size=.66, base=.36, track=0)


def letters(ts, word, cx, cy, w, h, toward, uid):
    """Raised cast-gold letters: an ink-rimmed stepped extrusion that recedes the same way
    as the block, a dark-gold body, a bright face and a hard glint on each letter's top edge."""
    from notebook import text_width
    F = BLOCK_FACE
    size = min(h * F["size"], w * .82 * 100 / text_width(word, F["face"], 100, F["track"] * 100))  # fit the face
    base = cy + size * F["base"]
    depth = max(3, int(size * .09))
    ex, ey = toward * .9, .9
    rim = f' stroke="{INK}" stroke-width="{f(size * .13)}" stroke-linejoin="round" paint-order="stroke"'
    out = [ts.text(word, F["face"], size, cx + ex * depth, base + ey * depth, INK, anchor="middle", tracking=F["track"], attrs=rim)[0]]
    for i in range(depth, 0, -1):
        out.append(ts.text(word, F["face"], size, cx + ex * i, base + ey * i, C["gold_dk"], anchor="middle", tracking=F["track"])[0])
    out.append(ts.text(word, F["face"], size, cx, base, C["glint"], anchor="middle", tracking=F["track"],
                       attrs=f' stroke="{INK}" stroke-width="{f(size * .05)}" stroke-linejoin="round" paint-order="stroke"')[0])
    # top-edge glint: the face again, clipped to its upper third, in white
    out.append(f'<g clip-path="url(#tg{uid})" opacity=".55">'
               f'{ts.text(word, F["face"], size, cx, base, "#FFFFFF", anchor="middle", tracking=F["track"])[0]}</g>')
    clip = f'<clipPath id="tg{uid}"><rect x="{f(cx - size * 3)}" y="{f(base - size * .78)}" width="{f(size * 6)}" height="{f(size * .2)}"/></clipPath>'
    return clip + "".join(out)


def block(ts, cx, cy, w, h, word, toward, uid):
    """A gold block worn as a gauntlet. `toward` is +1 when the depth recedes to the right."""
    dx, dy = toward * w * .13, -h * .2
    x, y = cx - w / 2, cy - h / 2
    s = []
    # crimson gauntlet cuff disappearing into the back of the block
    cuff = rpoly([(cx - w * .24 + dx, y + dy + 6), (cx + w * .24 + dx, y + dy + 6), (cx + w * .2 + dx * 1.6, y + dy - 14), (cx - w * .2 + dx * 1.6, y + dy - 14)], 6)
    s.append(inked(cuff, C["crimson"], 3))
    top = f"M{f(x)},{f(y)} L{f(x + dx)},{f(y + dy)} L{f(x + w + dx)},{f(y + dy)} L{f(x + w)},{f(y)}Z"
    side_x = x + w if toward > 0 else x
    side = f"M{f(side_x)},{f(y)} L{f(side_x + dx)},{f(y + dy)} L{f(side_x + dx)},{f(y + h + dy)} L{f(side_x)},{f(y + h)}Z"
    front = f"M{f(x)},{f(y)} H{f(x + w)} V{f(y + h)} H{f(x)}Z"
    s.append(f'<path d="{top}" fill="{C["glint"]}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    s.append(f'<path d="{side}" fill="{C["gold_dk"]}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    shine = (f'<path d="M{f(x + w * .55)},{f(y + h)} L{f(x + w)},{f(y + h * .3)} V{f(y + h)}Z" fill="{C["gold_sh"]}"/>'
             f'<path d="M{f(x + w * .12)},{f(y + h)} L{f(x + w * .3)},{f(y)} H{f(x + w * .4)} L{f(x + w * .22)},{f(y + h)}Z" fill="#FFFFFF" opacity=".3"/>'
             f'<path d="M{f(x + w * .46)},{f(y + h)} L{f(x + w * .64)},{f(y)} H{f(x + w * .68)} L{f(x + w * .5)},{f(y + h)}Z" fill="#FFFFFF" opacity=".22"/>')
    s.append(f'<g filter="url(#grain)"><path d="{front}" fill="{C["gold"]}"/>{clipped(f"bf{uid}", front, shine)}</g>')
    s.append(letters(ts, word, cx, cy, w, h, toward, uid))
    s.append(f'<path d="{front}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    return "".join(s), front


def glint(front, uid, x, w, h, cy, begin):
    """A white band that crosses the gold now and then: four snapped positions, then gone."""
    band = f'<path d="M{f(x)},{f(cy + h)} L{f(x + 30)},{f(cy - h)} H{f(x + 52)} L{f(x + 22)},{f(cy + h)}Z" fill="#FFFFFF" opacity=".75"/>'
    moves = f"{f(-80)} 0;{f(w * .25)} 0;{f(w * .55)} 0;{f(w * .85)} 0;{f(w + 80)} 0;{f(w + 80)} 0"
    anim = (f'<animateTransform attributeName="transform" type="translate" values="{moves}" keyTimes="0;.03;.06;.09;.12;1" '
            f'calcMode="discrete" dur="6s" begin="{begin}s" repeatCount="indefinite"/>')
    return clipped(f"gl{uid}", front, f'<g transform="translate({f(w + 80)} 0)">{anim}{band}</g>')


def punch(inner, cx, cy, animate):
    """Snap forward on twos: small, bigger, overshoot, settle. The settled frame is the base."""
    if not animate:
        return inner
    anim = ('<animateTransform attributeName="transform" type="scale" values="0.74;0.74;0.88;1.08;1" '
            'keyTimes="0;.35;.55;.75;1" calcMode="discrete" dur="0.62s" fill="freeze"/>')
    return f'<g transform="translate({f(cx)} {f(cy)})"><g>{anim}<g transform="translate({f(-cx)} {f(-cy)})">{inner}</g></g></g>'


def turnover(inner, cx, cy, animate):
    """XED: the DEX block rests turned over (reads XED). Every 6 s it turns back and
    snaps over again in stepped frames. Rotated 180 is the base value."""
    rest = f"180 {f(cx)} {f(cy)}"
    if not animate:
        return f'<g transform="rotate({rest})">{inner}</g>'
    vals = ";".join(f"{a} {f(cx)} {f(cy)}" for a in (180, 180, 270, 360, 360, 450, 540))
    anim = (f'<animateTransform attributeName="transform" type="rotate" values="{vals}" keyTimes="0;.7;.73;.76;.84;.87;.9" '
            f'calcMode="discrete" dur="6s" begin="0.8s" repeatCount="indefinite"/>')
    return f'<g transform="rotate({rest})">{anim}{inner}</g>'


def smoke_column(x, y, sc, animate, seed):
    puffs = []
    for i in range(3):
        p = cloud(x + (i % 2) * 8 * sc, y - i * 22 * sc, (11 + i * 4) * sc, 4, "#4A3A4E", seed + i, 3.5)
        if animate:
            p = (f'<g>{p}<animateTransform attributeName="transform" type="translate" values="0 0;2 -6;-2 -12;0 -18;0 0" '
                 f'keyTimes="0;.25;.5;.75;1" calcMode="discrete" dur="2.4s" begin="{i * .8:.1f}s" repeatCount="indefinite"/></g>')
        puffs.append(p)
    return "".join(reversed(puffs))


# ------------------------------------------------------------------ type

def lettering(ts, text, x, y, size, anchor, xed, seed, animate):
    """Creepster B-movie lettering: letters bounce off the baseline, crimson (or ember)
    stepped extrusion under an ink outline. XED drips spill from the letters."""
    from notebook import text_width
    rnd = random.Random(seed)
    w = text_width(text, "creep", size, 0)
    x0 = x - {"start": 0, "middle": w / 2, "end": w}[anchor]
    ext = C["crimson"] if not xed else C["oxblood"]
    out, drips = [], []
    cx = x0
    for ch in text:
        adv = text_width(ch, "creep", size, 0)
        dy, rot = rnd.uniform(-size * .07, size * .07), rnd.uniform(-6, 6)
        g = [ts.text(ch, "creep", size, cx + i * 1.6, y + dy + i * 1.6, ext, tracking=0,
                     attrs=f' stroke="{INK}" stroke-width="{f(size * .09)}" stroke-linejoin="round" paint-order="stroke"')[0]
             for i in range(5, 0, -1)]
        g.append(ts.text(ch, "creep", size, cx, y + dy, C["gold"], tracking=0,
                         attrs=f' stroke="{INK}" stroke-width="{f(size * .05)}" stroke-linejoin="round" paint-order="stroke"')[0])
        out.append(f'<g transform="rotate({f(rot)} {f(cx + adv / 2)} {f(y)})">{"".join(g)}</g>')
        if xed and rnd.random() < .5:
            dx = cx + adv * rnd.uniform(.3, .7)
            ln = rnd.uniform(.18, .42) * size
            drips.append(f'<path d="M{f(dx - 5)},{f(y - 4)} v{f(ln)} a5,5 0 0 0 10,0 v{f(-ln)}z" fill="{C["spill"]}" stroke="{INK}" stroke-width="3"/>')
        cx += adv
    return "".join(drips) + "".join(out)


def chain(x0, y0, x1, y1, n=None):
    """Oval links from a wall bolt down to a ring on the plate."""
    ln = math.hypot(x1 - x0, y1 - y0)
    n = n or max(2, int(ln / 9))
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    s = []
    for i in range(n):
        t = (i + .5) / n
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        flat = i % 2
        rx, ry = (ln / n * .62, 3.6) if not flat else (ln / n * .6, 1.6)
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" transform="rotate({f(ang)} {f(cx)} {f(cy)})" '
                 f'fill="{"none" if not flat else "#9AA3B8"}" stroke="{INK}" stroke-width="{2.6 if not flat else 2.2}"/>')
        if not flat:
            s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" transform="rotate({f(ang)} {f(cx)} {f(cy)})" '
                     f'fill="none" stroke="#C9D0DE" stroke-width="1"/>')
    return "".join(s)


def screw(x, y, r=4.2, angle=35):
    a = math.radians(angle)
    return (f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#C9D0DE" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{f(x - math.cos(a) * r * .7)},{f(y - math.sin(a) * r * .7)} L{f(x + math.cos(a) * r * .7)},{f(y + math.sin(a) * r * .7)}" '
            f'stroke="{INK}" stroke-width="1.8" stroke-linecap="round"/>')


def emblem(cx, cy, r, xed):
    """Round gold medallion with the phoenix flame: the coat patch, cast in metal."""
    flame = (f"M{f(cx)},{f(cy + r * .62)} C{f(cx - r * .62)},{f(cy + r * .3)} {f(cx - r * .5)},{f(cy - r * .2)} {f(cx - r * .18)},{f(cy - r * .66)} "
             f"C{f(cx - r * .12)},{f(cy - r * .2)} {f(cx + r * .04)},{f(cy - r * .1)} {f(cx + r * .12)},{f(cy - r * .36)} "
             f"C{f(cx + r * .5)},{f(cy - r * .08)} {f(cx + r * .6)},{f(cy + r * .3)} {f(cx)},{f(cy + r * .62)}Z")
    return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r + 3)}" fill="{INK}"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{C["gold"]}"/>'
            f'<path d="M{f(cx - r)},{f(cy)} A{f(r)},{f(r)} 0 0 0 {f(cx + r)},{f(cy)} Z" fill="{C["gold_sh"]}"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .76)}" fill="{C["oxblood"] if xed else C["crimson"]}" stroke="{INK}" stroke-width="2.4"/>'
            f'<path d="{flame}" fill="{C["phoenix"]}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            + fold([(cx - r * .62, cy - r * .5), (cx - r * .2, cy - r * .9), (cx + r * .3, cy - r * .86)], 2.4, C["glint"]))


def plate(ts, x, y, w, h, P, xed, uid, animate):
    """The nameplate: a crimson enamel sign in a bevelled gold frame, slotted screws, a cast
    phoenix medallion, hung from two wall bolts by chains. DEXTER's swings once when it
    lands and sways now and then. XED's left chain has snapped: it hangs crooked off one
    corner, scorched, with spill running down its face, and keeps swinging."""
    hang = 20
    bl, br = (x + w * .2, y - hang), (x + w * .8, y - hang)
    face = (C["oxblood"] if xed else C["crimson"])
    s = []
    # the sign itself, drawn level; the group gets rotated about its hanging point
    g = [f'<rect x="{x + 6}" y="{y + 6}" width="{w}" height="{h}" rx="6" fill="{INK}"/>']
    outer = rpoly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 6)
    g.append(inked(outer, C["gold"], 2.6, extra=(
        f'<path d="M{x},{y + h} L{x + 8},{y + h - 8} H{x + w - 8} V{y + 8} L{x + w},{y} V{y + h}Z" fill="{C["gold_dk"]}"/>'
        f'<path d="M{x},{y} L{x + 8},{y + 8} H{x + w - 8} L{x + w},{y}Z" fill="{C["glint"]}"/>')))
    inner = rpoly([(x + 8, y + 8), (x + w - 8, y + 8), (x + w - 8, y + h - 8), (x + 8, y + h - 8)], 3)
    shine = f'<path d="M{x + w * .55},{y} L{x + w * .62},{y} L{x + w * .5},{y + h} L{x + w * .43},{y + h}Z" fill="#FFFFFF" opacity=".12"/>'
    g.append(f'<path d="{inner}" fill="{face}" stroke="{INK}" stroke-width="2.4"/>')
    g.append(clipped(f"pl{uid}", inner, shine + f'<rect x="{x}" y="{y + h * .62}" width="{w}" height="{h}" fill="{INK}" opacity=".16"/>'))
    er = h * .29
    g.append(emblem(x + 10 + er + 8, y + h / 2, er, xed))
    tx0 = x + 10 + er * 2 + 22
    tw = x + w - 16 - tx0
    from notebook import text_width
    ns = min(h * .32, tw / text_width(NAME, "body-bold", 100) * 100)
    g.append(ts.text(NAME, "body-bold", ns, tx0, y + h * .5, C["bone"], attrs=f' stroke="{INK}" stroke-width="{f(ns * .16)}" stroke-linejoin="round" paint-order="stroke"')[0])
    g.append(ts.text(HANDLE, "body-bold", ns * .72, tx0, y + h * .5 + ns * 1.02, C["gold"])[0])
    corners = [(x + 6, y + 6), (x + w - 6, y + 6), (x + 6, y + h - 6), (x + w - 6, y + h - 6)]
    for i, (cx, cy) in enumerate(corners):
        if xed and i == 0:  # the screw by the broken chain popped out
            g.append(f'<circle cx="{cx}" cy="{cy}" r="3.4" fill="{INK}"/>')
        else:
            g.append(screw(cx, cy, 3.6, 30 + i * 47))
    # hanging rings
    rl, rr = (x + w * .2, y + 2), (x + w * .8, y + 2)
    for rx, ry in (rl, rr):
        g.append(f'<circle cx="{f(rx)}" cy="{f(ry)}" r="5" fill="none" stroke="{INK}" stroke-width="4.4"/><circle cx="{f(rx)}" cy="{f(ry)}" r="5" fill="none" stroke="#C9D0DE" stroke-width="1.6"/>')
    if xed:
        g.append(f'<path d="M{x + w - 60},{y + h - 8} q16,-22 40,-14 q6,12 -4,22z" fill="{INK}" opacity=".55"/>')
        g.append(f'<path d="M{x + 14},{y + h - 8} l8,-10 l-6,-6 l10,-8" fill="none" stroke="{INK}" stroke-width="2"/>')
        g.append(splat_on(x + w - 9, y + 5, 7, 31))
    body = "".join(g)
    if not xed:
        g_all = chain(*bl, *rl) + chain(*br, *rr) + body
        pivot = ((bl[0] + br[0]) / 2, bl[1])
        rest = "0"
        sway = "0;-5;4;-2.5;1.2;0;0;-1.4;1;0"
        times = "0;.03;.06;.09;.12;.15;.8;.85;.9;.95"
        dur, begin = "7s", "0s"
    else:
        g_all = chain(*br, *rr) + body
        pivot = br
        rest = "-7"
        sway = "-7;-4.5;-9;-5.5;-8;-6.5;-7"
        times = "0;.15;.3;.45;.6;.8;1"
        dur, begin = "2.8s", "0s"
    anim = ""
    if animate:
        vals = ";".join(f"{v} {f(pivot[0])} {f(pivot[1])}" for v in sway.split(";"))
        anim = (f'<animateTransform attributeName="transform" type="rotate" values="{vals}" keyTimes="{times}" '
                f'calcMode="discrete" dur="{dur}" begin="{begin}" repeatCount="indefinite"/>')
    s.append(f'<g transform="rotate({rest} {f(pivot[0])} {f(pivot[1])})">{anim}{g_all}</g>')
    if xed:  # the snapped chain end dangles from its bolt
        s.append(chain(bl[0], bl[1], bl[0] - 3, bl[1] + 22, 3))
    for bx, by in (bl, br):
        s.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="5.4" fill="#5B6478" stroke="{INK}" stroke-width="2.6"/><circle cx="{f(bx - 1.4)}" cy="{f(by - 1.4)}" r="1.8" fill="#C9D0DE"/>')
    return "".join(s)


def splat_on(cx, cy, r, seed):
    """Spill running down a surface (sign face): the character's splat, reused."""
    return kid.splat(cx, cy, r, seed, drips=2, run=2.4)


# ------------------------------------------------------------------ the shot

PLATES = ROOT / "lab" / "plates"


def painted_plate(layout, theme, w, h):
    """A Code Painter pass over the bare set (lab/plates/hero-<layout>-<theme>.webp|png), if one exists.
    It replaces the vector wall; everything that moves or carries meaning stays crisp vector on top."""
    import base64
    for ext, mime in (("webp", "image/webp"), ("png", "image/png"), ("jpg", "image/jpeg")):
        src = PLATES / f"hero-{layout}-{theme}.{ext}"
        if src.exists():
            data = base64.b64encode(src.read_bytes()).decode()
            return f'<image href="data:{mime};base64,{data}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>'
    return None


def hero(theme, animate, layout, plate_only=False):
    """plate_only draws just the bare set (wall, keyhole, pipes, tank, floor, smoke, drips): the
    picture handed to Code Painter."""
    L, xed = LAYOUTS[layout], theme == "dark"
    P = DARK if xed else LIGHT
    uid = f"{layout[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(f"h{uid}")
    w, h, fy = L["w"], L["h"], L["floor"]
    painted = None if plate_only else painted_plate(layout, theme, w, h)
    s = [painted or wall(L, P, xed, uid)]
    if xed and not painted:
        for i, (lx_, ln_, wd_, sd_) in enumerate(L["leaks"]):
            art, (ex_, ey_) = leak(lx_, 30, ln_, wd_, sd_, fy)
            s.append(art)
            s.append(f'<ellipse cx="{f(ex_)}" cy="{fy + 8}" rx="{f(wd_ * 2.2)}" ry="5" fill="{C["spill"]}" stroke="{INK}" stroke-width="3"/>')
            s.append(falling_drop(ex_, ey_ - 8, fy + 2, .4 + i * 1.1, animate))
        for (cx_, cy_, r_, sd_) in L["clouds"]:
            s.append(cloud(cx_, cy_, r_, 6, C["oxblood"], sd_))
    if plate_only:
        return svg_doc(w, h, f'<defs>{toon_defs()}</defs>' + "".join(s), f"{SIGN} backplate, {theme}")
    if L["shelf"]:
        s.append(shelf(L, xed, uid, animate))
    # the kid, upper body behind the blocks
    k, tx, ty = L["k"], L["tx"], L["ty"]
    s.append(f'<g transform="translate({tx} {ty}) scale({k})">{kid.hero_body(xed, uid, L["reach"])}{kid.head(xed, uid)}</g>')
    cy_ = L["counter"]
    top_c = "#5B6478" if not xed else "#2A2F44"
    bot = cy_ + (44 if layout == "narrow" else h)
    x0, x1 = tx + 20 * k, tx + 580 * k
    s.append(inked(rpoly([(x0, cy_), (x1, cy_), (x1, bot), (x0, bot)], [6, 6, 2, 2]), top_c, 3.4,
                   extra=f'<rect x="{f(x0)}" y="{cy_}" width="{f(x1 - x0)}" height="12" fill="{"#7C86A0" if not xed else "#3A4058"}"/>'))
    for dxk in (.2, .8):  # drawer pulls
        s.append(f'<rect x="{f(x0 + (x1 - x0) * dxk - 14)}" y="{cy_ + 24}" width="28" height="7" rx="3" fill="{INK}"/>')
    # blocks
    (lx, ly), (rx, ry) = L["blocks"]
    bw, bh = L["block"]
    dex, dex_front = block(ts, lx, ly, bw, bh, "DEX", 1, uid + "l")
    ter_y = ry + (bh * .22 if xed else 0)
    ter, ter_front = block(ts, rx, ter_y, bw, bh, "TER", -1, uid + "r")
    if not xed:
        if animate:
            dex += glint(dex_front, uid + "l", lx - bw / 2, bw, bh, ly, 1.4)
            ter += glint(ter_front, uid + "r", rx - bw / 2, bw, bh, ry, 1.55)
        s.append(punch(dex, lx, ly, animate))
        s.append(punch(ter, rx, ry, animate))
    else:
        ter_g = f'<g transform="rotate(-9 {f(rx)} {f(ter_y)})">{ter}</g>'
        s.append(ter_g)
        s.append(f'<path d="M{f(rx + bw * .5)},{f(ter_y - bh * .5)} l{f(-bw * .2)},{f(bh * .06)} l{f(bw * .06)},{f(bh * .14)} l{f(-bw * .08)},{f(bh * .16)} l{f(bw * .22)},{f(bh * .04)}z" fill="{INK}" opacity=".7" transform="rotate(-9 {f(rx)} {f(ter_y)})"/>')
        s.append(smoke_column(rx + bw * .3, ter_y - bh * .62, bw / 176, animate, 21))
        s.append(turnover(dex, lx, ly, animate))
        flame_a = flames(-10, w + 10, h + 4, 46, 3)
        flame_b = flames(-10, w + 10, h + 4, 46, 8)
        s.append(frames([flame_a, flame_b], period=0.5, order="01") if animate else flame_a)
        if L["shelf"]:
            s.append(f'<ellipse cx="{f(w * .26)}" cy="{f(fy + 34)}" rx="64" ry="10" fill="{C["spill"]}" stroke="{INK}" stroke-width="4"/>')
    # type
    sx, sy, ssize, sanchor = L["sign"]
    s.append(lettering(ts, SIGN, sx, sy, ssize, sanchor, xed, 5, animate))
    px, py, pw, ph = L["plate"]
    s.append(plate(ts, px, py, pw, ph, P, xed, uid, animate))
    lx_, ly_, lsize, lanchor = L["line"]
    ly_ += L["line_xed"] if xed else 0   # XED's sign hangs lower on its broken side
    s.append(ts.text(LINE[theme], "body-bold", lsize, lx_, ly_, P["text"], anchor=lanchor,
                     attrs=f' stroke="{INK}" stroke-width="{f(lsize * .22)}" stroke-linejoin="round" paint-order="stroke"')[0])
    # paper tooth over everything, then the frame
    s.append(f'<rect width="{w}" height="{h}" filter="url(#paper)" opacity=".45"/>')
    body = f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + "".join(s)
    label = f"{SIGN}: {NAME}, {HANDLE}. {LINE[theme]}"
    return svg_doc(w, h, body, label)


if __name__ == "__main__":
    out = ROOT / "lab" / ".runtime" / "preview" if "--preview" in sys.argv else ASSETS
    out.mkdir(parents=True, exist_ok=True)
    if "--plates" in sys.argv:  # bare sets to paint in Code Painter, saved as SVG; screenshot to PNG at 2x
        for theme in ("light", "dark"):
            for layout in LAYOUTS:
                (out / f"plate-{layout}-{theme}.svg").write_text(hero(theme, False, layout, plate_only=True), encoding="utf-8")
        print("plates written to", out)
        sys.exit()
    for theme in ("light", "dark"):
        for layout, stem in (("wide", "banner"), ("narrow", "banner-narrow")):
            (out / f"{stem}-{theme}.svg").write_text(hero(theme, True, layout), encoding="utf-8")
            (out / f"{stem}-still-{theme}.svg").write_text(hero(theme, False, layout), encoding="utf-8")
    print("hero written to", out)
