"""Ink comic panels for the DEXTER / XED README: section headers, the featured project and
the live stat panels.

Every card is a hand-inked comic panel: wobbly heavy border, slightly off-square corners,
a hard ink drop shadow and grained fills. The lab's mess lives on the borders, not over
the content: tape and a wrench on DEXTER's tidy panels; spill running off the corners,
scorch marks and a tilt on XED's.

Light theme is DEXTER, dark theme is XED. XED renames the sections.
"""
import math
import random

import kid
from notebook import Typesetter, svg_doc, text_width, wrap
from toon import INK, PHOENIX as C, clipped, defs as toon_defs, f, fold, inked, limb, rpoly, smooth

TITLES = {  # key: (DEXTER, XED)
    "projects": ("Projects", "Experiments"),
    "wins": ("Trophies", "Loot"),
    "stack": ("Stack", "Chemicals"),
    "live": ("Readings", "Vitals"),
    "contact": ("Contact", "Signal"),
}
LINES = {  # one short line per header, per persona
    "projects": ("Web apps, 3D visualizers, a CTF platform and a tower defense game.",
                 "Web apps, 3D toys, a CTF arena and a tower defense game. Most survived."),
}
THEME = {
    "light": dict(paper=C["bone"], panel=C["bone"], text=INK, muted="#3A4152", page="#FFFFFF",
                  easy="#1a7f37", medium="#b45309", hard="#cf222e", screen="#16285C", screen_text=C["bone"]),
    "dark": dict(paper="#1B2136", panel="#1B2136", text=C["bone"], muted="#AEB6CC", page="#0D1117",
                 easy="#3fb950", medium="#ffb02e", hard="#ff5c6c", screen="#071019", screen_text=C["spill"]),
}


# ------------------------------------------------------------------ panel kit

def wobble_rect(x, y, w, h, seed, amp=1.6):
    """A rectangle inked by hand: each corner nudged a little, corners barely rounded."""
    rnd = random.Random(seed)
    j = lambda: rnd.uniform(-amp, amp)
    return rpoly([(x + j(), y + j()), (x + w + j(), y + j()), (x + w + j(), y + h + j()), (x + j(), y + h + j())], 4)


def panel(x, y, w, h, fill, seed, uid, inner=""):
    """The comic panel: hard ink shadow, grained fill, heavy wobbly border."""
    d = wobble_rect(x, y, w, h, seed)
    return (f'<path d="{d}" fill="{INK}" transform="translate(7 7)"/>'
            f'<g filter="url(#grain)"><path d="{d}" fill="{fill}"/></g>'
            + clipped(f"pn{uid}", d, inner)
            + f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')


def tape(cx, cy, w, rot):
    """A strip of masking tape holding a corner down."""
    h = 18
    d = f"M{f(-w / 2)},{f(-h / 2)} l4,-2 l4,2 H{f(w / 2)} l-3,3 l3,3 l-3,3 l3,3 l-3,3 V{f(h / 2)} H{f(-w / 2)} l3,-3 l-3,-3 l3,-3 l-3,-3z"
    return (f'<g transform="translate({f(cx)} {f(cy)}) rotate({rot})"><path d="{d}" fill="#EADFC2" opacity=".93" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{f(-w / 2 + 6)},-4 H{f(w / 2 - 8)}" stroke="#FFFFFF" stroke-width="2" opacity=".6"/></g>')


def scorch(cx, cy, r, seed):
    rnd = random.Random(seed)
    pts = [(cx + math.cos(i / 12 * math.tau) * r * rnd.uniform(.6, 1.2), cy + math.sin(i / 12 * math.tau) * r * rnd.uniform(.5, .9)) for i in range(12)]
    return (f'<path d="{smooth(pts)}" fill="{INK}" opacity=".5"/>'
            f'<path d="{smooth([(x * .55 + cx * .45, y * .55 + cy * .45) for x, y in pts])}" fill="{INK}" opacity=".55"/>')


def corner_spill(x, y, seed, run=1.6, r=16):
    """Spill that landed on a panel corner and runs off it."""
    return kid.splat(x, y, r, seed, drips=2, run=run)


# ------------------------------------------------------------------ type helpers

def creep(ts, text, x, y, size, anchor="start", seed=5, xed=False, drips=False):
    """Creepster lettering, bouncing letters on a stepped extrusion (same as the hero sign)."""
    rnd = random.Random(seed)
    w = text_width(text, "creep", size, 0)
    cx = x - {"start": 0, "middle": w / 2, "end": w}[anchor]
    ext = C["oxblood"] if xed else C["crimson"]
    out, drip = [], []
    for ch in text:
        adv = text_width(ch, "creep", size, 0)
        dy, rot = rnd.uniform(-size * .06, size * .06), rnd.uniform(-5, 5)
        g = [ts.text(ch, "creep", size, cx + i * 1.4, y + dy + i * 1.4, ext, tracking=0,
                     attrs=f' stroke="{INK}" stroke-width="{f(size * .09)}" stroke-linejoin="round" paint-order="stroke"')[0] for i in range(4, 0, -1)]
        g.append(ts.text(ch, "creep", size, cx, y + dy, C["gold"], tracking=0,
                         attrs=f' stroke="{INK}" stroke-width="{f(size * .05)}" stroke-linejoin="round" paint-order="stroke"')[0])
        out.append(f'<g transform="rotate({f(rot)} {f(cx + adv / 2)} {f(y)})">{"".join(g)}</g>')
        if drips and rnd.random() < .45:
            dx, ln = cx + adv * rnd.uniform(.3, .7), rnd.uniform(.16, .36) * size
            drip.append(f'<path d="M{f(dx - 4)},{f(y - 3)} v{f(ln)} a4,4 0 0 0 8,0 v{f(-ln)}z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.6"/>')
        cx += adv
    return "".join(drip) + "".join(out), w


def stepped_count(ts, value, face, size, x, y, fill, anchor, animate, start=.5, frames=6, attrs=""):
    """A number that races up in snapped frames and holds on its value (the base frame)."""
    final = ts.text(str(value), face, size, x, y, fill, anchor=anchor, attrs=attrs)[0]
    if not animate or value == 0:
        return final
    vals = [round(value * (k / frames) ** .6) for k in range(1, frames)]
    step = .07
    out = []
    end = start + step * len(vals)
    for k, v in enumerate(vals):
        t0, t1 = start + k * step, start + (k + 1) * step
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;{t0 / end:.4f};{t1 / end:.4f}" '
                   f'calcMode="discrete" dur="{end:.2f}s" fill="freeze"/>{ts.text(str(v), face, size, x, y, fill, anchor=anchor, attrs=attrs)[0]}</g>')
    out.append(f'<g><animate attributeName="opacity" values="0;1" keyTimes="0;{(end - step) / end:.4f}" calcMode="discrete" dur="{end:.2f}s" fill="freeze"/>{final}</g>')
    return "".join(out)


# ------------------------------------------------------------------ props

def flask_icon(cx, cy, s, liquid, animate, boil=False):
    body = rpoly([(cx - 7 * s, cy - 26 * s), (cx + 7 * s, cy - 26 * s), (cx + 7 * s, cy - 12 * s), (cx + 26 * s, cy + 20 * s),
                  (cx - 26 * s, cy + 20 * s), (cx - 7 * s, cy - 12 * s)], [3, 3, 4, 8, 8, 4])
    liq = f'<rect x="{f(cx - 40 * s)}" y="{f(cy + 2 * s)}" width="{f(80 * s)}" height="{f(30 * s)}" fill="{liquid}"/>'
    out = [inked(body, "#D8EEF2", 3, extra=clipped(f"fk{f(cx)}{f(cy)}", body, liq)),
           fold([(cx - 2 * s, cy - 20 * s), (cx - 4 * s, cy - 6 * s)], 3, "#FFFFFF"),
           f'<rect x="{f(cx - 10 * s)}" y="{f(cy - 32 * s)}" width="{f(20 * s)}" height="{f(7 * s)}" rx="2" fill="#9AA3B8" stroke="{INK}" stroke-width="2.6"/>']
    for i, (bx, r) in enumerate(((-4, 4), (5, 3), (0, 5))):
        b = f'<circle cx="{f(cx + bx * s)}" cy="{f(cy - 38 * s)}" r="{f(r * s)}" fill="{liquid}" stroke="{INK}" stroke-width="2"/>'
        if animate:
            out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;1;0" keyTimes="0;.2;.45;.7;.9" calcMode="discrete" '
                       f'dur="1.8s" begin="{i * .6:.1f}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" '
                       f'values="0 0;0 {f(-6 * s)};0 {f(-12 * s)};0 {f(-18 * s)};0 0" keyTimes="0;.2;.45;.7;.9" calcMode="discrete" dur="1.8s" '
                       f'begin="{i * .6:.1f}s" repeatCount="indefinite"/>{b}</g>')
    if boil:  # XED: it boiled over and runs down the glass
        out.append(f'<path d="M{f(cx - 10 * s)},{f(cy - 30 * s)} q-8,4 -9,{f(16 * s)} v{f(16 * s)} a4,4 0 0 0 8,0 v-12 q2,-8 4,-12z" fill="{liquid}" stroke="{INK}" stroke-width="2.4"/>')
    return "".join(out)


def ink_rule(x0, x1, y, uid, animate, xed, drip=True):
    """A brush stroke under the header, drawn in once in four snapped steps."""
    ln = x1 - x0
    d = f"M{f(x0)},{f(y)} C{f(x0 + ln * .3)},{f(y - 3)} {f(x0 + ln * .7)},{f(y + 3)} {f(x1)},{f(y - 1)}"
    stroke = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
    stroke += f'<path d="{d}" fill="none" stroke="{C["gold"]}" stroke-width="2.4" stroke-linecap="round" transform="translate(0 -1.4)"/>'
    if animate:
        cw = ";".join(f"{f(ln * k / 4 + 10)}" for k in (1, 2, 3, 4))
        stroke = (f'<clipPath id="ru{uid}"><rect x="{f(x0 - 6)}" y="{f(y - 12)}" width="{f(ln + 12)}" height="24">'
                  f'<animate attributeName="width" values="{f(ln * .25)};{cw}" keyTimes="0;.2;.45;.7;1" calcMode="discrete" dur=".5s" begin=".15s" fill="freeze"/></rect></clipPath>'
                  f'<g clip-path="url(#ru{uid})">{stroke}</g>')
    if xed and drip:
        stroke += f'<path d="M{f(x1 - 40)},{f(y + 2)} v16 a4.5,4.5 0 0 0 9,0 v-16z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.6"/>'
        stroke += f'<path d="M{f(x1 - 35.5)},{f(y + 30)} q5,7 0,10 q-5,-3 0,-10z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.2"/>'
    return stroke


def speaker(cx, cy, s, xed, animate, uid):
    """PlacebAIStudio: a studio monitor whose woofer pumps, beside a level meter that never
    moves: every effect works, except none of them touch your audio. A pill is plugged in."""
    out = []
    cab = rpoly([(cx - 52 * s, cy - 78 * s), (cx + 52 * s, cy - 78 * s), (cx + 56 * s, cy + 78 * s), (cx - 56 * s, cy + 78 * s)], 10 * s)
    out.append(inked(cab, "#2A2F44" if not xed else "#1A1E2E", 3.4, extra=clipped(f"cab{uid}", cab,
               f'<rect x="{f(cx + 24 * s)}" y="{f(cy - 90 * s)}" width="{f(60 * s)}" height="{f(180 * s)}" fill="{INK}" opacity=".35"/>')))
    # tweeter
    out.append(f'<circle cx="{f(cx)}" cy="{f(cy - 46 * s)}" r="{f(16 * s)}" fill="#9AA3B8" stroke="{INK}" stroke-width="3"/>'
               f'<circle cx="{f(cx)}" cy="{f(cy - 46 * s)}" r="{f(7 * s)}" fill="{INK}"/>')
    # woofer: pumps on twos
    cone = (f'<circle cx="{f(cx)}" cy="{f(cy + 22 * s)}" r="{f(40 * s)}" fill="#5B6478" stroke="{INK}" stroke-width="3.4"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy + 22 * s)}" r="{f(28 * s)}" fill="#3A4152" stroke="{INK}" stroke-width="2.6"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy + 22 * s)}" r="{f(11 * s)}" fill="{C["gold"]}" stroke="{INK}" stroke-width="2.6"/>'
            + fold([(cx - 26 * s, cy + 6 * s), (cx - 14 * s, cy - 6 * s), (cx + 2 * s, cy - 10 * s)], 3, "#C9D0DE"))
    if animate:
        vals = ";".join(f"{v} {f(cx)} {f(cy + 22 * s)}" for v in ("1 1", "1.1 1.1", "1 1", "1.06 1.06", "1 1", "1 1"))
        vals = ";".join(f"{v}" for v in ("1", "1.1", "1", "1.06", "1", "1"))
        cone = (f'<g transform="translate({f(cx)} {f(cy + 22 * s)})"><g><animateTransform attributeName="transform" type="scale" values="{vals}" '
                f'keyTimes="0;.12;.24;.36;.48;1" calcMode="discrete" dur="1.6s" repeatCount="indefinite"/>'
                f'<g transform="translate({f(-cx)} {f(-cy - 22 * s)})">{cone}</g></g></g>')
    out.append(cone)
    # the pill, plugged in by a cable
    px, py = cx + 82 * s, cy + 52 * s
    out.append(f'<path d="M{f(cx + 50 * s)},{f(cy + 60 * s)} C{f(cx + 70 * s)},{f(cy + 90 * s)} {f(px - 20 * s)},{f(py + 30 * s)} {f(px - 10 * s)},{f(py + 6 * s)}" '
               f'fill="none" stroke="{INK}" stroke-width="{f(8 * s)}" stroke-linecap="round"/>'
               f'<path d="M{f(cx + 50 * s)},{f(cy + 60 * s)} C{f(cx + 70 * s)},{f(cy + 90 * s)} {f(px - 20 * s)},{f(py + 30 * s)} {f(px - 10 * s)},{f(py + 6 * s)}" '
               f'fill="none" stroke="{C["crimson"]}" stroke-width="{f(3.4 * s)}" stroke-linecap="round"/>')
    pill = f'<g transform="rotate(-35 {f(px)} {f(py)})">' + inked(rpoly([(px - 26 * s, py - 12 * s), (px + 26 * s, py - 12 * s), (px + 26 * s, py + 12 * s), (px - 26 * s, py + 12 * s)], 12 * s), C["bone"], 3,
                 extra=f'<rect x="{f(px)}" y="{f(py - 14 * s)}" width="{f(30 * s)}" height="{f(28 * s)}" fill="{C["crimson"]}"/>') \
        + fold([(px - 18 * s, py - 5 * s), (px - 4 * s, py - 7 * s)], 3, "#FFFFFF") + "</g>"
    out.append(pill)
    # the level meter: flat, always
    mx, my = cx - 104 * s, cy - 70 * s
    out.append(inked(rpoly([(mx - 18 * s, my), (mx + 18 * s, my), (mx + 18 * s, my + 140 * s), (mx - 18 * s, my + 140 * s)], 5 * s), INK, 2.6))
    for k in range(10):
        lit = k >= 9
        col = C["spill"] if lit else "#1E2436"
        out.append(f'<rect x="{f(mx - 11 * s)}" y="{f(my + (8 + k * 13) * s)}" width="{f(22 * s)}" height="{f(9 * s)}" rx="1.5" fill="{col}"/>')
    out.append(f'<path d="M{f(mx - 26 * s)},{f(my + 148 * s)} h{f(52 * s)}" stroke="{INK}" stroke-width="3"/>')
    if xed:
        out.append(scorch(cx + 20 * s, cy - 60 * s, 18 * s, 4))
        out.append(f'<path d="M{f(cx - 30 * s)},{f(cy - 76 * s)} l10,18 l-8,10 l12,16" fill="none" stroke="{C["bone"]}" stroke-width="2.2"/>')
    return "".join(out)


def monitor(cx, cy, w, h, P, xed, inner, uid):
    """A lab CRT on a stand. XED's screen is cracked and the case scorched."""
    out = [inked(rpoly([(cx - 22, cy + h / 2 - 4), (cx + 22, cy + h / 2 - 4), (cx + 34, cy + h / 2 + 16), (cx - 34, cy + h / 2 + 16)], 4), "#5B6478", 2.6)]
    case = rpoly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], 12)
    out.append(inked(case, "#C9C2AE" if not xed else "#4A4F63", 3.4, extra=clipped(f"mc{uid}", case,
               f'<rect x="{f(cx + w * .28)}" y="{f(cy - h)}" width="{f(w)}" height="{f(h * 2)}" fill="{INK}" opacity=".18"/>')))
    sx, sy, sw, sh = cx - w / 2 + 12, cy - h / 2 + 10, w - 24, h - 20
    scr = rpoly([(sx, sy), (sx + sw, sy), (sx + sw, sy + sh), (sx, sy + sh)], 14)
    scan = "".join(f'<rect x="{f(sx)}" y="{f(sy + k * 4)}" width="{f(sw)}" height="1.4" fill="#FFFFFF" opacity=".05"/>' for k in range(int(sh / 4)))
    out.append(f'<path d="{scr}" fill="{P["screen"]}" stroke="{INK}" stroke-width="3"/>')
    out.append(clipped(f"ms{uid}", scr, inner + scan + f'<path d="M{f(sx)},{f(sy)} h{f(sw * .5)} l{f(-sw * .3)},{f(sh)} h{f(-sw * .2)}z" fill="#FFFFFF" opacity=".06"/>'))
    if xed:
        out.append(f'<path d="M{f(sx + sw * .7)},{f(sy)} l-8,20 l10,10 l-14,22 M{f(sx + sw * .7 - 8)},{f(sy + 20)} l-18,6" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity=".85"/>')
    return "".join(out)


# ------------------------------------------------------------------ the pieces

def header(key, theme, layout="wide", animate=True):
    xed = theme == "dark"
    P = THEME[theme]
    w, h = (760, 118) if layout == "wide" else (400, 150)
    uid = f"h{key}{layout[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    title = TITLES[key][xed]
    line = LINES[key][xed]
    s = []
    icon_x = 50
    s.append(flask_icon(icon_x, 58, 1.15, C["spill"] if xed else C["crimson"], animate, boil=xed))
    size = 62 if layout == "wide" else 54
    word, ww = creep(ts, title, 96, 74, size, seed=3 + len(title), xed=xed, drips=xed)
    s.append(word)
    s.append(ink_rule(96, w - 24 if layout == "wide" else w - 16, 92, uid, animate, xed, drip=layout == "wide"))
    if layout == "wide":
        s.append(ts.text(line, "body-bold", 15.5, 98, 114, P["text"])[0])
    else:
        for i, ln in enumerate(wrap(line, "body-bold", 14.5, w - 110)):
            s.append(ts.text(ln, "body-bold", 14.5, 98, 116 + i * 18, P["text"])[0])
    body = f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + "".join(s)
    return svg_doc(w, h, body, f"{title}. {line}")


FEATURE = dict(name="PlacebAIStudio", line="Every effect works, except none of them touch your audio.",
               award=("Champion, Rage Quit Award", "MALFUNCTION Hackathon 2026, iDE.A iAcademy"),
               where="Private repo with a live demo",
               stack=[("react", "React"), ("ts", "TypeScript"), ("vite", "Vite"), ("vitest", "Vitest"),
                      ("matter", "Matter.js"), ("xstate", "XState"), ("claude", "Claude API")])


def chips(ts, stack, x, y, room, P, xed):
    from icons import ICONS
    from notebook import mark
    out = []
    for k, name in stack:
        has = k.lower() in ICONS or name.lower() in ICONS
        if has:
            cw = 34
            inner = mark(k if k.lower() in ICONS else name, x + 8, y + 7, 18, INK)
        else:
            cw = text_width(name, "body-bold", 12) + 18
            inner = ts.text(name, "body-bold", 12, x + 9, y + 21, INK)[0]
        if x + cw > room:
            break
        chip = rpoly([(x, y), (x + cw, y), (x + cw, y + 32), (x, y + 32)], 5)
        out.append(f'<path d="{chip}" fill="{INK}" transform="translate(3 3)"/>' + inked(chip, C["bone"] if not xed else "#D9D2BE", 2.2) + inner)
        x += cw + 7
    return "".join(out)


def feature(theme, layout="wide", animate=True):
    xed = theme == "dark"
    P = THEME[theme]
    p = FEATURE
    uid = f"f{layout[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    if layout == "wide":
        W, H = 760, 300
        px, py, pw, ph = 12, 14, 734, 270
        art = (150, 150, 1.0)
        tx, ty, tw = 300, 92, 420
    else:
        W, H = 400, 560
        px, py, pw, ph = 10, 14, 376, 530
        art = (200, 150, .9)
        tx, ty, tw = 34, 330, 330
    s = []
    # art window inside the panel
    ax, ay, asc = art
    win = rpoly([(ax - 118, ay - 112), (ax + 118, ay - 112), (ax + 118, ay + 112), (ax - 118, ay + 112)], 6) if layout == "wide" else \
        rpoly([(ax - 160, ay - 116), (ax + 160, ay - 116), (ax + 160, ay + 116), (ax - 160, ay + 116)], 6)
    win_bg = C["prussian"] if not xed else "#0B1026"
    rays = "".join(f'<path d="M{f(ax)},{f(ay)} L{f(ax + math.cos(a) * 400)},{f(ay + math.sin(a) * 400)} L{f(ax + math.cos(a + .16) * 400)},{f(ay + math.sin(a + .16) * 400)}Z" fill="{"#1E3570" if not xed else "#14193A"}"/>'
                   for a in [k * .42 for k in range(15)])
    inner = (f'<path d="{win}" fill="{win_bg}"/>' + clipped(f"wr{uid}", win, rays)
             + f'<path d="{win}" fill="none" stroke="{INK}" stroke-width="4"/>' + speaker(ax + 10, ay - 4, asc, xed, animate, uid))
    # text column
    t = [ts.text(p["name"], "body-bold", 34 if layout == "wide" else 30, tx, ty, P["text"],
                 attrs=f' stroke="{P["panel"]}" stroke-width="0"')[0]]
    yy = ty + 30
    for ln in wrap(p["line"], "body-bold", 17, tw):
        t.append(ts.text(ln, "body-bold", 17, tx, yy, P["muted"])[0])
        yy += 23
    # award ribbon
    ry = yy + 6
    rw = min(tw, text_width(p["award"][0], "body-bold", 16) + 70)
    rib = f"M{f(tx)},{f(ry)} H{f(tx + rw)} l-12,17 l12,17 H{f(tx)} l10,-17z"
    t.append(f'<path d="{rib}" fill="{INK}" transform="translate(4 4)"/>' + inked(rib, C["gold"], 2.6,
             extra=f'<path d="M{f(tx)},{f(ry + 22)} H{f(tx + rw)} V{f(ry + 40)} H{f(tx)}Z" fill="{C["gold_sh"]}"/>'))
    t.append(f'<circle cx="{f(tx + 26)}" cy="{f(ry + 17)}" r="9" fill="{C["crimson"]}" stroke="{INK}" stroke-width="2.4"/>'
             f'<path d="M{f(tx + 26)},{f(ry + 11)} l2,4 4,.5 -3,3 1,4.5 -4,-2 -4,2 1,-4.5 -3,-3 4,-.5z" fill="{C["gold"]}"/>')
    t.append(ts.text(p["award"][0], "body-bold", 16, tx + 42, ry + 23, INK)[0])
    t.append(ts.text(p["award"][1], "body", 13.5, tx, ry + 56, P["muted"])[0])
    t.append(chips(ts, p["stack"], tx, ry + 70, tx + tw + 30, P, xed))
    # where the code lives: a rubber stamp
    st = p["where"]
    sw_ = text_width(st, "body-bold", 12.5) + 20
    sx_, sy_ = (tx, ty - 58) if layout == "wide" else (tx, ty - 50)
    t.append(f'<g transform="rotate(-4 {f(sx_ + sw_ / 2)} {f(sy_ + 12)})" opacity=".9"><path d="{wobble_rect(sx_, sy_, sw_, 26, 9, .8)}" fill="none" stroke="{C["crimson"] if not xed else C["phoenix"]}" stroke-width="2.6"/>'
             + ts.text(st, "body-bold", 12.5, sx_ + 10, sy_ + 17.5, C["crimson"] if not xed else C["phoenix"])[0] + "</g>")
    content = inner + "".join(t)
    if xed:
        content += scorch(px + 30, py + ph - 20, 30, 7)
    s.append(panel(px, py, pw, ph, P["panel"], 11, uid, content))
    # mess on the borders
    if not xed:
        s.append(tape(px + 30, py + 2, 70, -24) + tape(px + pw - 24, py + ph - 2, 64, -20))
    else:
        s.append(corner_spill(px + pw - 40, py + 2, 41, 1.8, 18))
        s.append(corner_spill(px + 120, py + ph - 2, 42, 1.2, 11))
    group = "".join(s)
    if xed:
        group = f'<g transform="rotate(-.6 {W / 2} {H / 2})">{group}</g>'
    body = f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + group
    label = f'{p["name"]}, featured. {p["line"]} {p["award"][0]}, {p["award"][1]}. {p["where"]}.'
    return svg_doc(W, H, body, label)


LEET = dict(handle="Acetylsphae", solved=dict(Easy=30, Medium=1, Hard=0), active=11)


def leet(theme, animate=True, v=LEET):
    """LeetCode on a lab CRT: total solved races up, three difficulty bars fill in steps."""
    xed = theme == "dark"
    P = THEME[theme]
    uid = f"lc{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    W, H = 252, 188
    total = sum(v["solved"].values())
    inner = []
    cx, cy = 126, 76
    sx, sy = cx - 92, cy - 52
    inner.append(stepped_count(ts, total, "body-bold", 46, sx + 12, sy + 52, P["screen_text"], "start", animate,
                               attrs=f' stroke="{INK}" stroke-width="0"'))
    inner.append(ts.text("solved", "body-bold", 13, sx + 14 + text_width(str(total), "body-bold", 46) + 6, sy + 50, P["screen_text"])[0])
    mx = max(v["solved"].values()) or 1
    for i, (k, col) in enumerate((("Easy", P["easy"]), ("Medium", P["medium"]), ("Hard", P["hard"]))):
        n = v["solved"][k]
        by = sy + 66 + i * 12
        bw = 110 * n / mx
        inner.append(f'<rect x="{f(sx + 14)}" y="{f(by)}" width="110" height="7" fill="#FFFFFF" opacity=".1"/>')
        bar = f'<rect x="{f(sx + 14)}" y="{f(by)}" width="{f(max(bw, 2))}" height="7" fill="{col}"/>'
        if animate and n:
            bar = (f'<rect x="{f(sx + 14)}" y="{f(by)}" width="{f(max(bw, 2))}" height="7" fill="{col}">'
                   f'<animate attributeName="width" values="0;{f(bw * .33)};{f(bw * .66)};{f(bw)}" keyTimes="0;.3;.6;.9" calcMode="discrete" dur=".6s" begin="{.5 + i * .1:.1f}s" fill="freeze"/></rect>')
        inner.append(bar)
        inner.append(ts.text(f"{k[0]} {n}", "body-bold", 10, sx + 132, by + 7, P["screen_text"])[0])
    mon = monitor(cx, cy, 200, 124, P, xed, "".join(inner), uid)
    foot = (ts.text(f"@{v['handle']}", "body-bold", 13, 18, 166, P["text"])[0]
            + ts.text(f"{v['active']} active days", "body", 12, 232, 166, P["muted"], anchor="end")[0])
    content = mon + foot
    if xed:
        content += scorch(214, 30, 14, 3)
    s = [panel(6, 6, 238, 172, P["panel"], 23, uid, content)]
    if not xed:
        s.append(tape(30, 8, 46, -28))
    else:
        s.append(corner_spill(226, 8, 51, 1.4, 11))
    group = "".join(s)
    if xed:
        group = f'<g transform="rotate(.8 {W / 2} {H / 2})">{group}</g>'
    body = f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + group
    label = f"LeetCode @{v['handle']}: {total} problems solved ({v['solved']['Easy']} easy, {v['solved']['Medium']} medium, {v['solved']['Hard']} hard) over {v['active']} active days."
    return svg_doc(W, H, body, label)


if __name__ == "__main__":
    import sys
    from notebook import ROOT
    out = ROOT / "lab" / ".runtime" / "preview"
    out.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        for anim, tag in ((True, ""), (False, "-still")):
            (out / f"g3-header{tag}-{theme}.svg").write_text(header("projects", theme, "wide", anim), encoding="utf-8")
            (out / f"g3-header-narrow{tag}-{theme}.svg").write_text(header("projects", theme, "narrow", anim), encoding="utf-8")
            (out / f"g3-feature{tag}-{theme}.svg").write_text(feature(theme, "wide", anim), encoding="utf-8")
            (out / f"g3-feature-narrow{tag}-{theme}.svg").write_text(feature(theme, "narrow", anim), encoding="utf-8")
            (out / f"g3-leet{tag}-{theme}.svg").write_text(leet(theme, anim), encoding="utf-8")
    print("gate 3 written to", out)
