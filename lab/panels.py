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


def shelf(x0, x1, y, uid, xed, brackets=None, depth=12, sag_right=False):
    """A steel wall shelf: a plank with a gold front edge, held up by brackets screwed under it.
    XED's right bracket has sheared off, so the plank sags toward that end."""
    brackets = brackets or (x0 + 40, x1 - 40)
    drop = 7 if (xed and sag_right) else 0
    top = f"M{f(x0)},{f(y)} L{f(x1)},{f(y + drop)} L{f(x1)},{f(y + drop + depth)} L{f(x0)},{f(y + depth)}Z"
    out = []
    for i, bx in enumerate(brackets):
        broken = xed and sag_right and i == len(brackets) - 1
        by = y + depth + (drop * (bx - x0) / (x1 - x0))
        if broken:  # the bracket snapped: a stub stays on the plank, the rest dangles from one screw
            out.append(f'<path d="M{f(bx - 4)},{f(by - 1)} h12 v6 l-6,5 h-6z" fill="#5B6478" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
            out.append(f'<g transform="rotate(38 {f(bx)} {f(by + 18)})"><path d="M{f(bx)},{f(by + 18)} h7 v22 l-22,-22z" fill="#5B6478" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/></g>')
            continue
        out.append(f'<path d="M{f(bx - 4)},{f(by - 1)} h10 v26 l-24,-26z" fill="#5B6478" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>'
                   f'<circle cx="{f(bx + 1)}" cy="{f(by + 6)}" r="1.8" fill="{INK}"/><circle cx="{f(bx + 1)}" cy="{f(by + 17)}" r="1.8" fill="{INK}"/>')
    out.append(f'<path d="{top}" fill="{INK}" transform="translate(4 4)"/>')
    out.append(f'<path d="{top}" fill="#7C86A0" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    out.append(f'<path d="M{f(x0)},{f(y + depth * .45)} L{f(x1)},{f(y + drop + depth * .45)} L{f(x1)},{f(y + drop + depth)} L{f(x0)},{f(y + depth)}Z" fill="{C["gold"]}" stroke="{INK}" stroke-width="2"/>')
    out.append(fold([(x0 + 8, y + 2.5), ((x0 + x1) / 2, y + 2.5 + drop / 2), (x1 - 8, y + 2.5 + drop)], 2.2, "#C9D0DE"))
    return "".join(out)


def bottle(ts, x, base, key, name, cap, liquid, xed=False, tipped=False, uid="b"):
    """A reagent bottle standing on a shelf (its foot pressed 2 px into the plank), its paper
    label carrying the tool's name. The bottle grows to fit the name. Returns svg and width."""
    fs = 7.6
    w, h = max(36, text_width(name, "body-bold", fs) + 14), 46
    y = base - h + 2
    body = rpoly([(x, y + 12), (x + w, y + 12), (x + w, y + h), (x, y + h)], [8, 8, 4, 4])
    nx = x + w / 2
    neck = rpoly([(nx - 7, y + 4), (nx + 7, y + 4), (nx + 7, y + 14), (nx - 7, y + 14)], 2)
    capd = rpoly([(nx - 9, y - 3), (nx + 9, y - 3), (nx + 9, y + 6), (nx - 9, y + 6)], 3)
    liq = f'<rect x="{x - 4}" y="{f(y + h * .46)}" width="{w + 8}" height="{h}" fill="{liquid}"/>'
    lab_x, lab_y, lab_w, lab_h = x + 4, y + 18, w - 8, 22
    label = ts.text(name, "body-bold", fs, x + w / 2, lab_y + 14.5, INK, anchor="middle", tracking=0)[0]
    g = [inked([body, neck], "#CFE6EA", 2.6, extra=clipped(f"bt{uid}", body, liq)),
         inked(capd, cap, 2.4),
         f'<rect x="{lab_x}" y="{lab_y}" width="{lab_w}" height="{lab_h}" rx="2" fill="{C["bone"]}" stroke="{INK}" stroke-width="1.8"/>',
         label,
         fold([(x + 6, y + 16), (x + 5, y + 30)], 2.4, "#FFFFFF")]
    if tipped:  # XED cracked this one: a split in the glass, leaking onto the plank
        g.append(f'<path d="M{x + w - 8},{y + 14} l-6,10 l5,6 l-7,12" fill="none" stroke="{INK}" stroke-width="2"/>')
        g.append(f'<path d="M{x + w - 14},{base - 2} q14,-3 30,1 v4 q-14,2 -30,1z" fill="{liquid}" stroke="{INK}" stroke-width="2"/>')
        g.append(f'<path d="M{x + w + 8},{base + 9} v12 a3.6,3.6 0 0 0 7.2,0 v-12z" fill="{liquid}" stroke="{INK}" stroke-width="2"/>')
    return "".join(g), w


def bottles(ts, stack, x, base, room, xed, uid, gap=10):
    caps = (C["crimson"], C["gold"], C["phoenix"], C["prussian"])
    liquids = (C["spill"], C["phoenix"], "#8FD3FF", C["gold"])
    out, i = [], 0
    for k, (key, name) in enumerate(stack):
        if x + max(36, text_width(name, "body-bold", 7.6) + 14) > room:
            break
        svg, w = bottle(ts, x, base, key, name, caps[k % 4], liquids[k % 4], xed, xed and k == 2, f"{uid}{k}")
        out.append(svg)
        x += w + gap
    return "".join(out)


def live_sign(ts, x, y, xed, uid, animate):
    """An ON AIR style box sign bolted to the wall: LIVE DEMO glows behind red glass and
    flickers on in steps when the page loads. A small brass plate screwed beside it
    reads PRIVATE REPO, with a padlock."""
    fs, tr = 13, 1.4
    word = "LIVE DEMO"
    tw = text_width(word, "body-bold", fs, tr)
    w, h = tw + 46, 30
    glass_on = "#FF4A3A" if not xed else C["phoenix"]
    glass_off = "#5A1A20"
    out = []
    # mounting bolts and short brackets into the wall
    for bx in (x + 14, x + w - 14):
        out.append(f'<rect x="{f(bx - 3)}" y="{f(y - 8)}" width="6" height="10" fill="#5B6478" stroke="{INK}" stroke-width="2"/>'
                   f'<circle cx="{f(bx)}" cy="{f(y - 9)}" r="3" fill="#9AA3B8" stroke="{INK}" stroke-width="1.8"/>')
    box = rpoly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 6)
    out.append(f'<path d="{box}" fill="{INK}" transform="translate(4 4)"/>')
    out.append(inked(box, "#2A2F44", 2.6))
    gx0, gy0, gw, gh = x + 6, y + 5, w - 12, h - 10
    glass = rpoly([(gx0, gy0), (gx0 + gw, gy0), (gx0 + gw, gy0 + gh), (gx0, gy0 + gh)], 3)
    lit = (f'<path d="{glass}" fill="{glass_on}"/>'
           f'<rect x="{f(gx0 - 14)}" y="{f(gy0 - 14)}" width="{f(gw + 28)}" height="{f(gh + 28)}" rx="14" fill="{glass_on}" opacity=".16"/>'
           f'<circle cx="{f(gx0 + 10)}" cy="{f(gy0 + gh / 2)}" r="3.6" fill="#FFF1B8"/>'
           + ts.text(word, "body-bold", fs, gx0 + 20 + tw / 2, gy0 + gh / 2 + 4.6, "#FFF6E0", anchor="middle", tracking=tr)[0]
           + f'<path d="M{f(gx0 + 3)},{f(gy0 + 3)} h{f(gw * .45)}" stroke="#FFFFFF" stroke-width="1.6" opacity=".55"/>')
    off = (f'<path d="{glass}" fill="{glass_off}"/>'
           + ts.text(word, "body-bold", fs, gx0 + 20 + tw / 2, gy0 + gh / 2 + 4.6, "#8A3A40", anchor="middle", tracking=tr)[0])
    if animate:  # flickers on: off, on, off, on and holds (lit is the base frame)
        anim = ('<animate attributeName="opacity" values="0;1;0;1;1" keyTimes="0;.3;.45;.7;1" calcMode="discrete" dur=".9s" begin=".3s" fill="freeze"/>')
        out.append(off + f'<g opacity="1">{anim}{lit}</g>')
    else:
        out.append(lit)
    out.append(f'<path d="{glass}" fill="none" stroke="{INK}" stroke-width="2"/>')
    # the brass plate beside it
    pt = "PRIVATE REPO"
    pw = text_width(pt, "body-bold", 9.5, 1.2) + 34
    px, py = x + w + 12, y + 6
    plate = rpoly([(px, py), (px + pw, py), (px + pw, py + 20), (px, py + 20)], 3)
    out.append(f'<path d="{plate}" fill="{INK}" transform="translate(3 3)"/>' + inked(plate, C["gold"], 2.2,
               extra=f'<rect x="{f(px)}" y="{f(py + 12)}" width="{f(pw)}" height="9" fill="{C["gold_sh"]}" opacity=".6"/>'))
    lx, ly = px + 11, py + 10
    out.append(f'<path d="M{f(lx - 3.4)},{f(ly - 1)} v-2.6 a3.4,3.4 0 0 1 6.8,0 v2.6" fill="none" stroke="#5A3A10" stroke-width="1.8"/>'
               f'<rect x="{f(lx - 5)}" y="{f(ly - 1)}" width="10" height="7.5" rx="1.5" fill="#5A3A10"/>')
    out.append(ts.text(pt, "body-bold", 9.5, px + 21, py + 13.8, "#5A3A10", tracking=1.2)[0])
    for sx_ in (px + 4, px + pw - 4):
        out.append(f'<circle cx="{f(sx_)}" cy="{f(py + 10)}" r="1.6" fill="{C["gold_dk"]}"/>')
    return "".join(out)


def pushpin(x, y):
    return (f'<ellipse cx="{f(x + 2)}" cy="{f(y + 3)}" rx="7" ry="3" fill="{INK}" opacity=".35"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="7" fill="{C["crimson"]}" stroke="{INK}" stroke-width="2.4"/>'
            f'<circle cx="{f(x - 2)}" cy="{f(y - 2)}" r="2.2" fill="#FFFFFF" opacity=".8"/>')


def headphones(cx, top, s, xed):
    """Studio headphones tossed onto the cabinet lid: one round cup resting on the top, the
    other propped against it, the band arched over and the cord dropping down the back."""
    out = []
    lx, rx = cx - 22 * s, cx + 26 * s
    band = f"M{f(lx)},{f(top - 20 * s)} C{f(lx - 6 * s)},{f(top - 66 * s)} {f(rx + 8 * s)},{f(top - 70 * s)} {f(rx)},{f(top - 26 * s)}"
    out.append(f'<path d="{band}" fill="none" stroke="{INK}" stroke-width="{f(12 * s)}" stroke-linecap="round"/>'
               f'<path d="{band}" fill="none" stroke="{C["crimson"] if not xed else C["oxblood"]}" stroke-width="{f(5.5 * s)}" stroke-linecap="round"/>')
    for x0, y0, r in ((lx, top - 15 * s, 16 * s), (rx, top - 20 * s, 15 * s)):
        out.append(f'<ellipse cx="{f(x0)}" cy="{f(y0)}" rx="{f(r * .8)}" ry="{f(r)}" fill="#2A2F44" stroke="{INK}" stroke-width="3"/>'
                   f'<ellipse cx="{f(x0)}" cy="{f(y0)}" rx="{f(r * .5)}" ry="{f(r * .66)}" fill="#3A4152" stroke="{INK}" stroke-width="2"/>'
                   + fold([(x0 - r * .5, y0 - r * .5), (x0 - r * .6, y0 + r * .1)], 2.4, "#9AA3B8"))
    out.append(f'<path d="M{f(rx + 10 * s)},{f(top - 10 * s)} q16,6 14,34 q-2,30 4,60" fill="none" stroke="{INK}" stroke-width="2.6"/>')
    return f'<g transform="rotate(-8 {f(cx)} {f(top)})">{"".join(out)}</g>'


def medal(cx, nail_y, xed, uid, animate):
    """A gold medal on a crimson-and-gold ribbon, hung from a nail. It sways on the nail now
    and then, in snapped frames."""
    ribbon = (f'<path d="M{f(cx)},{f(nail_y)} L{f(cx - 13)},{f(nail_y + 30)} L{f(cx - 3)},{f(nail_y + 30)} L{f(cx + 2)},{f(nail_y + 8)}Z" fill="{C["crimson"]}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
              f'<path d="M{f(cx)},{f(nail_y)} L{f(cx + 13)},{f(nail_y + 30)} L{f(cx + 3)},{f(nail_y + 30)} L{f(cx - 2)},{f(nail_y + 8)}Z" fill="{C["gold"]}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    my, r = nail_y + 46, 17
    star = " ".join(f"{f(cx + math.cos(-math.pi / 2 + k * math.pi / 5) * (r * .62 if k % 2 == 0 else r * .26))},"
                    f"{f(my + math.sin(-math.pi / 2 + k * math.pi / 5) * (r * .62 if k % 2 == 0 else r * .26))}" for k in range(10))
    disc = (f'<circle cx="{f(cx)}" cy="{f(my)}" r="{r + 3}" fill="{INK}"/>'
            f'<circle cx="{f(cx)}" cy="{f(my)}" r="{r}" fill="{C["gold"]}"/>'
            f'<path d="M{f(cx - r)},{f(my)} A{r},{r} 0 0 0 {f(cx + r)},{f(my)}Z" fill="{C["gold_sh"]}"/>'
            f'<circle cx="{f(cx)}" cy="{f(my)}" r="{f(r * .78)}" fill="none" stroke="{C["gold_dk"]}" stroke-width="1.8"/>'
            f'<polygon points="{star}" fill="{C["glint"]}" stroke="{C["gold_dk"]}" stroke-width="1.4" stroke-linejoin="round"/>'
            + fold([(cx - r * .7, my - r * .3), (cx - r * .4, my - r * .72), (cx + r * .05, my - r * .82)], 2.4, "#FFFFFF")
            + f'<rect x="{f(cx - 5)}" y="{f(nail_y + 27)}" width="10" height="5" rx="1.5" fill="{C["gold_dk"]}" stroke="{INK}" stroke-width="1.8"/>')
    body = ribbon + disc
    if animate:
        vals = ";".join(f"{a} {f(cx)} {f(nail_y)}" for a in (0, 0, 7, -5, 3, -1.5, 0))
        body = (f'<g><animateTransform attributeName="transform" type="rotate" values="{vals}" keyTimes="0;.7;.74;.78;.82;.86;.9" '
                f'calcMode="discrete" dur="6.5s" begin="1.2s" repeatCount="indefinite"/>{body}</g>')
    nail = (f'<circle cx="{f(cx)}" cy="{f(nail_y)}" r="3.6" fill="#C9D0DE" stroke="{INK}" stroke-width="2"/>')
    return body + nail


def award_wall(ts, x, y, room, award, xed, uid, animate):
    """The win, hung on the wall: a medal on a nail beside an engraved brass plaque in a wood
    frame, screwed on at the corners."""
    title, where = award
    px = x + 44
    tw = max(text_width(title, "body-bold", 14), text_width(where, "body-bold", 9.2)) + 44
    pw, ph = min(tw, room - 40), 66
    band = 24   # height of the darker engraved strip at the bottom of the brass
    wood = rpoly([(px, y + 4), (px + pw, y + 4), (px + pw, y + 4 + ph), (px, y + 4 + ph)], 5)
    brass = rpoly([(px + 7, y + 11), (px + pw - 7, y + 11), (px + pw - 7, y + ph - 3), (px + 7, y + ph - 3)], 2)
    engraved = "#5A3A10"
    out = [f'<path d="{wood}" fill="{INK}" transform="translate(4 4)"/>',
           inked(wood, "#7A4524" if not xed else "#4A2A18", 2.6, extra=fold([(px + 6, y + 8), (px + pw * .6, y + 8)], 2, "#A8693E")),
           f'<g filter="url(#grain)"><path d="{brass}" fill="{C["gold"]}"/></g>',
           clipped(f"br{uid}", brass, f'<path d="M{f(px + pw * .55)},{f(y)} h18 l-30,{ph + 10} h-18z" fill="#FFFFFF" opacity=".28"/>'
                                     f'<rect x="{f(px)}" y="{f(y + ph - 3 - band)}" width="{f(pw)}" height="{band}" fill="{C["gold_sh"]}" opacity=".75"/>'
                                     f'<path d="M{f(px)},{f(y + ph - 3 - band)} H{f(px + pw)}" stroke="{C["gold_dk"]}" stroke-width="1.4"/>'),
           f'<path d="{brass}" fill="none" stroke="{INK}" stroke-width="2"/>',
           ts.text(title, "body-bold", 14, px + pw / 2, y + 11 + (ph - 14 - band) / 2 + 5, engraved, anchor="middle")[0],
           ts.text(where, "body-bold", 9.6, px + pw / 2, y + ph - 3 - band / 2 + 3.4, engraved, anchor="middle")[0]]
    for sx_, sy_ in ((px + 12, y + 11 + (ph - 14 - band) / 2), (px + pw - 12, y + 11 + (ph - 14 - band) / 2)):
        out.append(f'<circle cx="{f(sx_)}" cy="{f(sy_)}" r="2.4" fill="{C["gold_dk"]}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(medal(x + 18, y + 6, xed, uid, animate))
    if xed:  # a scorch licks the plaque's corner
        out.append(f'<path d="M{f(px + pw - 4)},{f(y + 6)} q-24,4 -30,22 q14,-8 30,-4z" fill="{INK}" opacity=".45"/>')
    return "".join(out)


def lab_wall(x, y, w, h, xed):
    wall, seam = (C["prussian"], C["navy"]) if not xed else ("#0E1A3A", "#070C1E")
    out = [f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{wall}"/>']
    for i in range(1, 4):
        sx = x + i * w / 4
        out.append(f'<line x1="{f(sx)}" y1="{f(y)}" x2="{f(sx)}" y2="{f(y + h)}" stroke="{seam}" stroke-width="4"/>')
        for j in range(int(h / 34)):
            out.append(f'<circle cx="{f(sx - 9)}" cy="{f(y + 16 + j * 34)}" r="2.8" fill="{seam}"/>')
    return "".join(out)


def desk(x0, x1, y, bottom, xed):
    """A bench top (light lip) with a steel front."""
    top = "#7C86A0" if not xed else "#3A4058"
    front = "#5B6478" if not xed else "#2A2F44"
    return (f'<rect x="{f(x0)}" y="{f(y)}" width="{f(x1 - x0)}" height="{f(bottom - y)}" fill="{front}" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{f(x0)}" y="{f(y)}" width="{f(x1 - x0)}" height="8" fill="{top}" stroke="{INK}" stroke-width="3"/>')


def studio(cx, floor, s, xed, animate, uid):
    """PlacebAIStudio on a bench: a studio monitor whose woofer pumps, and the level meter it is
    wired to, which never moves. The plug in the monitor's input jack is a pill. Every effect
    works, except none of them touch your audio."""
    out = []
    ch = 150 * s
    cy = floor - ch / 2 + 2  # cabinet foot pressed into the bench
    cab = rpoly([(cx - 50 * s, cy - ch / 2), (cx + 50 * s, cy - ch / 2), (cx + 54 * s, cy + ch / 2), (cx - 54 * s, cy + ch / 2)], 10 * s)
    out.append(inked(cab, "#2A2F44" if not xed else "#1A1E2E", 3.4, extra=clipped(f"cab{uid}", cab,
               f'<rect x="{f(cx + 22 * s)}" y="{f(cy - ch)}" width="{f(60 * s)}" height="{f(ch * 2)}" fill="{INK}" opacity=".35"/>')))
    out.append(headphones(cx - 4 * s, cy - ch / 2 + 2, s * .9, xed))
    ty = cy - ch * .3
    out.append(f'<circle cx="{f(cx)}" cy="{f(ty)}" r="{f(15 * s)}" fill="#9AA3B8" stroke="{INK}" stroke-width="3"/>'
               f'<circle cx="{f(cx)}" cy="{f(ty)}" r="{f(6 * s)}" fill="{INK}"/>')
    wy = cy + ch * .16
    cone = (f'<circle cx="{f(cx)}" cy="{f(wy)}" r="{f(38 * s)}" fill="#5B6478" stroke="{INK}" stroke-width="3.4"/>'
            f'<circle cx="{f(cx)}" cy="{f(wy)}" r="{f(26 * s)}" fill="#3A4152" stroke="{INK}" stroke-width="2.6"/>'
            f'<circle cx="{f(cx)}" cy="{f(wy)}" r="{f(10 * s)}" fill="{C["gold"]}" stroke="{INK}" stroke-width="2.6"/>'
            + fold([(cx - 24 * s, wy - 14 * s), (cx - 12 * s, wy - 26 * s), (cx + 4 * s, wy - 30 * s)], 3, "#C9D0DE"))
    if animate:
        cone = (f'<g transform="translate({f(cx)} {f(wy)})"><g><animateTransform attributeName="transform" type="scale" values="1;1.1;1;1.06;1;1" '
                f'keyTimes="0;.12;.24;.36;.48;1" calcMode="discrete" dur="1.6s" repeatCount="indefinite"/>'
                f'<g transform="translate({f(-cx)} {f(-wy)})">{cone}</g></g></g>')
    out.append(cone)
    # input jack on the cabinet's left side, with the pill pushed into it
    jx, jy = cx - 40 * s, cy + ch * .36
    jack_r = 11 * s   # a round metal socket on the cabinet's side (drawn here, its front lip after the pill)
    out.append(f'<circle cx="{f(jx + 2)}" cy="{f(jy)}" r="{f(jack_r)}" fill="#9AA3B8" stroke="{INK}" stroke-width="2.6"/>'
               f'<circle cx="{f(jx + 2)}" cy="{f(jy)}" r="{f(jack_r * .55)}" fill="{INK}"/>')
    # meter rack standing on the bench to the left
    mw, mh = 36 * s, 128 * s
    mx = cx - 112 * s
    my = floor - mh + 2
    rack = rpoly([(mx - mw / 2, my), (mx + mw / 2, my), (mx + mw / 2, my + mh), (mx - mw / 2, my + mh)], 5 * s)
    out.append(inked(rack, "#1A1E2E", 2.8))
    for k in range(10):
        col = C["spill"] if k == 9 else "#2A3046"
        out.append(f'<rect x="{f(mx - 11 * s)}" y="{f(my + (8 + k * 11.4) * s)}" width="{f(22 * s)}" height="{f(7.6 * s)}" rx="1.5" fill="{col}"/>')
    out.append(f'<circle cx="{f(mx)}" cy="{f(my + mh - 8 * s)}" r="{f(3 * s)}" fill="#9AA3B8" stroke="{INK}" stroke-width="2"/>')
    # cable: meter's output socket, along the bench, up into the pill's tail
    cable = (f"M{f(mx + mw / 2)},{f(my + mh - 8 * s)} C{f(mx + mw / 2 + 20 * s)},{f(floor + 2)} {f(jx - 70 * s)},{f(floor + 2)} "
             f"{f(jx - 50 * s)},{f(jy)}")
    out.append(f'<path d="{cable}" fill="none" stroke="{INK}" stroke-width="{f(9 * s)}" stroke-linecap="round"/>'
               f'<path d="{cable}" fill="none" stroke="{C["crimson"]}" stroke-width="{f(3.6 * s)}" stroke-linecap="round"/>')
    # the pill: a two-tone capsule whose crimson end is pushed into the socket
    px0, px1 = jx - 50 * s, jx + 2
    mid = (px0 + px1) / 2
    pill = rpoly([(px0, jy - 10 * s), (px1, jy - 10 * s), (px1, jy + 10 * s), (px0, jy + 10 * s)], 10 * s)
    halves = (f'<rect x="{f(mid)}" y="{f(jy - 14 * s)}" width="{f(px1 - mid + 4)}" height="{f(28 * s)}" fill="{C["crimson"]}"/>'
              f'<rect x="{f(px0 - 4)}" y="{f(jy + 3 * s)}" width="{f(px1 - px0 + 8)}" height="{f(10 * s)}" fill="{INK}" opacity=".14"/>')
    out.append(inked(pill, C["bone"], 2.8, extra=clipped(f"pl{uid}", pill, halves)))
    out.append(f'<path d="M{f(mid)},{f(jy - 10 * s)} V{f(jy + 10 * s)}" stroke="{INK}" stroke-width="2.4"/>')
    out.append(fold([(px0 + 7 * s, jy - 5 * s), (mid - 5 * s, jy - 6 * s)], 2.6, "#FFFFFF"))
    out.append(fold([(mid + 5 * s, jy - 5 * s), (px1 - 9 * s, jy - 6 * s)], 2.2, "#FF8A9C"))
    # the socket's front lip closes over the capsule's tip
    out.append(f'<path d="M{f(jx + 2 - jack_r * .2)},{f(jy - jack_r)} A{f(jack_r)},{f(jack_r)} 0 0 1 {f(jx + 2 - jack_r * .2)},{f(jy + jack_r)}" '
               f'fill="#9AA3B8" stroke="{INK}" stroke-width="2.6"/>')
    if xed:
        out.append(scorch(cx + 18 * s, cy - ch * .38, 16 * s, 4))
        out.append(f'<path d="M{f(cx - 30 * s)},{f(cy - ch * .48)} l10,18 l-8,10 l12,16" fill="none" stroke="{C["bone"]}" stroke-width="2.2"/>')
    return "".join(out)


def monitor(cx, floor, w, h, P, xed, inner, uid):
    """A lab CRT on a stand, its foot pressed into the desk. XED's screen is cracked."""
    stand_h = 16
    cy = floor - stand_h - h / 2 + 2
    out = [inked(rpoly([(cx - 20, cy + h / 2 - 4), (cx + 20, cy + h / 2 - 4), (cx + 34, floor + 2), (cx - 34, floor + 2)], 3), "#5B6478", 2.6)]
    case = rpoly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], 12)
    out.append(inked(case, "#C9C2AE" if not xed else "#4A4F63", 3.4, extra=clipped(f"mc{uid}", case,
               f'<rect x="{f(cx + w * .28)}" y="{f(cy - h)}" width="{f(w)}" height="{f(h * 2)}" fill="{INK}" opacity=".18"/>')))
    sx, sy, sw, sh = cx - w / 2 + 12, cy - h / 2 + 10, w - 24, h - 20
    scr = rpoly([(sx, sy), (sx + sw, sy), (sx + sw, sy + sh), (sx, sy + sh)], 14)
    scan = "".join(f'<rect x="{f(sx)}" y="{f(sy + k * 4)}" width="{f(sw)}" height="1.4" fill="#FFFFFF" opacity=".05"/>' for k in range(int(sh / 4)))
    out.append(f'<path d="{scr}" fill="{P["screen"]}" stroke="{INK}" stroke-width="3"/>')
    out.append(clipped(f"ms{uid}", scr, inner(sx, sy, sw, sh) + scan))
    if xed:
        out.append(f'<path d="M{f(sx + sw * .74)},{f(sy)} l-8,20 l10,10 l-14,22 M{f(sx + sw * .74 - 8)},{f(sy + 20)} l-18,6" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity=".85"/>')
    return "".join(out)


def label_plate(ts, x, y, w, h, left, right, P):
    """A small riveted plate screwed to the desk front, carrying the panel's caption."""
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="3" fill="{C["bone"]}" stroke="{INK}" stroke-width="2.2"/>'
            f'<circle cx="{f(x + 6)}" cy="{f(y + h / 2)}" r="1.8" fill="{INK}"/><circle cx="{f(x + w - 6)}" cy="{f(y + h / 2)}" r="1.8" fill="{INK}"/>'
            + ts.text(left, "body-bold", 11.5, x + 13, y + h * .7, INK)[0]
            + ts.text(right, "body", 10.5, x + w - 13, y + h * .7, "#3A4152", anchor="end")[0])


# ------------------------------------------------------------------ the pieces

def header(key, theme, layout="wide", animate=True):
    """Section header: the flask and the title stand on a wall shelf. XED's shelf has lost a
    bracket and sags; the flask has boiled over and runs off the plank's edge."""
    xed = theme == "dark"
    P = THEME[theme]
    wide = layout == "wide"
    w, h = (760, 140) if wide else (400, 168)
    uid = f"h{key}{layout[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    title, line = TITLES[key][xed], LINES[key][xed]
    plank_y = 88
    s = []
    size = 60 if wide else 44
    x0, x1 = 16, (w - 16)
    s.append(shelf(x0, x1, plank_y, uid, xed, brackets=(x0 + 60, x1 - 60), sag_right=True))
    s.append(flask_icon(52, plank_y - 22, 1.1, C["spill"] if xed else C["crimson"], animate, boil=xed))
    word, ww = creep(ts, title, 92, plank_y - 3, size, seed=3 + len(title), xed=xed, drips=False)
    s.append(word)
    if xed:  # what boiled over pools on the plank and drips off its front edge
        s.append(f'<path d="M30,{plank_y + 1} q22,-5 48,-1 q8,2 4,4 q-24,2 -52,1z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.4"/>'
                 f'<path d="M64,{plank_y + 10} v14 a4,4 0 0 0 8,0 v-14z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.4"/>'
                 f'<path d="M68,{plank_y + 32} q5,7 0,10 q-5,-3 0,-10z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2"/>')
    ly = plank_y + 44
    if wide:
        s.append(ts.text(line, "body-bold", 15.5, 92, ly, P["text"])[0])
    else:
        for i, ln in enumerate(wrap(line, "body-bold", 14.5, w - 110)):
            s.append(ts.text(ln, "body-bold", 14.5, 92, ly + i * 19, P["text"])[0])
    body = f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + "".join(s)
    return svg_doc(w, h, body, f"{title}. {line}")


FEATURE = dict(name="PlacebAIStudio", line="Every effect works, except none of them touch your audio.",
               award=("Champion, Rage Quit Award", "MALFUNCTION Hackathon 2026, iDE.A iAcademy"),
               where="Private repo with a live demo",
               stack=[("react", "React"), ("ts", "TypeScript"), ("vite", "Vite"), ("vitest", "Vitest"),
                      ("matter", "Matter.js"), ("xstate", "XState"), ("claude", "Claude API")])


PAINT = {
    "light": dict(wall="#4B5370", seam="#3C4360", rivet="#5E6788", floor="#2E3350", floor_line="#3E4566",
                  machine="#23273B", rim=C["bone"], text=C["bone"], muted="#D5D9E6",
                  sky=["#F7EAD3", "#F6D3AE", "#F2A27A", "#E07A5A"], cloud="#FFF7E8"),
    "dark": dict(wall="#161C33", seam="#0E1328", rivet="#232B4A", floor="#0E1020", floor_line="#221430",
                 machine="#0A0D1C", rim="#F2B98A", text=C["bone"], muted="#BFC6D8",
                 sky=[C["gold"], C["phoenix"], C["crimson"], C["oxblood"]], cloud=None),
}


def arch(x0, x1, top, bottom):
    """The opening cut in the steel wall: a round-topped doorway, like MAIN TEXTURE's keyhole."""
    r = (x1 - x0) / 2
    return f"M{f(x0)},{f(bottom)} V{f(top + r)} A{f(r)},{f(r)} 0 0 1 {f(x1)},{f(top + r)} V{f(bottom)}Z"


def tank(cx, cy, r, P, seed):
    """A big dark machine silhouette framing the scene, picked out with thin warm rim lines
    (the dark shapes in MAIN TEXTURE are drawn this way, not in heavy ink)."""
    rim = P["rim"]
    return (f'<g filter="url(#grain)"><circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{P["machine"]}"/></g>'
            f'<path d="M{f(cx - r * .9)},{f(cy + r * .44)} A{f(r)},{f(r)} 0 0 0 {f(cx + r * .44)},{f(cy + r * .9)}" fill="none" stroke="{rim}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .7)}" fill="none" stroke="{rim}" stroke-width="1.6" stroke-dasharray="6 12" opacity=".6"/>'
            + "".join(f'<circle cx="{f(cx + math.cos(a) * r * .84)}" cy="{f(cy + math.sin(a) * r * .84)}" r="3.4" fill="{rim}" opacity=".75"/>'
                      for a in [k * math.tau / 10 + .2 for k in range(10)]))


def pipes(x, top, bottom, P, n=3):
    """Vertical pipes running down the right edge, with flanged joints."""
    out = []
    for i in range(n):
        px = x + i * 22
        out.append(f'<g filter="url(#grain)"><rect x="{f(px)}" y="{f(top)}" width="16" height="{f(bottom - top)}" fill="{P["machine"]}"/></g>')
        out.append(f'<path d="M{f(px + 3)},{f(top)} V{f(bottom)}" stroke="{P["rim"]}" stroke-width="1.6" opacity=".7"/>')
        for jy in range(int(top) + 40 + i * 17, int(bottom) - 10, 70):
            out.append(f'<rect x="{f(px - 3)}" y="{jy}" width="22" height="9" rx="2" fill="{P["machine"]}" stroke="{P["rim"]}" stroke-width="1.6"/>')
    return "".join(out)


def gas_cylinder(cx, floor, P, xed):
    """A tall gas cylinder standing on the floor, chained to the wall, valve on top."""
    w, h = 40, 128
    top = floor - h + 3
    body = rpoly([(cx - w / 2, top + 14), (cx + w / 2, top + 14), (cx + w / 2, floor + 3), (cx - w / 2, floor + 3)], [18, 18, 4, 4])
    band = C["crimson"] if not xed else C["spill"]
    out = [inked(body, "#5B6478" if not xed else "#2A2F44", 2.8, extra=clipped(f"gc{cx}{xed}", body,
               f'<rect x="{f(cx - w)}" y="{f(top + 30)}" width="{f(w * 2)}" height="14" fill="{band}"/>'
               f'<rect x="{f(cx + w * .2)}" y="{f(top)}" width="{f(w)}" height="{h + 10}" fill="{INK}" opacity=".28"/>')),
           fold([(cx - w * .3, top + 50), (cx - w * .32, floor - 16)], 3, "#C9D0DE"),
           f'<rect x="{f(cx - 7)}" y="{f(top + 2)}" width="14" height="14" rx="2" fill="#9AA3B8" stroke="{INK}" stroke-width="2.4"/>',
           f'<rect x="{f(cx - 14)}" y="{f(top - 4)}" width="28" height="7" rx="3" fill="{C["gold"]}" stroke="{INK}" stroke-width="2.2"/>',
           f'<path d="M{f(cx - w / 2)},{f(top + 70)} q-8,-2 -14,2 M{f(cx + w / 2)},{f(top + 70)} q8,-2 14,2" fill="none" stroke="{INK}" stroke-width="3.4" stroke-dasharray="5 3"/>',
           f'<ellipse cx="{f(cx)}" cy="{f(floor + 4)}" rx="{f(w * .7)}" ry="4" fill="{INK}" opacity=".35"/>']
    return "".join(out)


def sconce(x, y, P, xed):
    """A wall lamp on an arm bolted to the wall, its light falling on the words below."""
    glow = C["gold"] if not xed else C["phoenix"]
    return (f'<path d="M{f(x - 230)},{f(y + 30)} L{f(x - 12)},{f(y + 14)} L{f(x + 14)},{f(y + 14)} L{f(x + 40)},{f(y + 330)} L{f(x - 300)},{f(y + 330)}Z" fill="{glow}" opacity=".06"/>'
            f'<rect x="{f(x + 30)}" y="{f(y - 14)}" width="10" height="22" rx="2" fill="{P["machine"]}" stroke="{P["rim"]}" stroke-width="1.6"/>'
            f'<path d="M{f(x + 30)},{f(y - 3)} H{f(x + 2)} V{f(y)}" fill="none" stroke="{P["machine"]}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{f(x - 22)},{f(y + 20)} L{f(x - 8)},{f(y)} H{f(x + 12)} L{f(x + 24)},{f(y + 20)}Z" fill="{P["machine"]}" stroke="{P["rim"]}" stroke-width="1.8" stroke-linejoin="round"/>'
            f'<ellipse cx="{f(x + 1)}" cy="{f(y + 21)}" rx="10" ry="3.6" fill="{glow}"/>')


def hanging_lamp(x, y, P, xed):
    """A shop lamp on its cord from the ceiling, lighting the wall where the text sits."""
    shade = f"M{f(x - 30)},{f(y + 26)} L{f(x - 12)},{f(y)} H{f(x + 12)} L{f(x + 30)},{f(y + 26)}Z"
    glow = C["gold"] if not xed else C["phoenix"]
    return (f'<path d="M{f(x)},-4 V{f(y)}" stroke="{P["machine"]}" stroke-width="3"/>'
            f'<path d="M{f(x - 70)},{f(y + 26)} L{f(x + 70)},{f(y + 26)} L{f(x + 150)},{f(y + 210)} L{f(x - 150)},{f(y + 210)}Z" fill="{glow}" opacity=".07"/>'
            f'<path d="{shade}" fill="{P["machine"]}" stroke="{P["rim"]}" stroke-width="1.8" stroke-linejoin="round"/>'
            f'<ellipse cx="{f(x)}" cy="{f(y + 27)}" rx="11" ry="4" fill="{glow}"/>')


def feature(theme, layout="wide", animate=True):
    """The featured project as a painted lab scene (MAIN TEXTURE): no panel frame. Matte steel
    wall and floor, a big dark tank and pipes framing the shot, a round-topped opening in the
    wall glowing warm, the studio set up on a bench inside it, and the project's words on the
    wall beside it under a shop lamp. XED: the same room at night, fire through the opening,
    spill leaking down the tank."""
    xed = theme == "dark"
    P = PAINT[theme]
    p = FEATURE
    wide = layout == "wide"
    uid = f"f{layout[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    if wide:
        W, H = 760, 356
        floor = 306
        ax0, ax1, atop = 44, 304, 34
        tx, tw, ty = 352, 320, 30
        tank_c = (-40, -40, 150)
        pipe_x = W - 42
        lamp_x = 676
    else:
        W, H = 400, 720
        floor = 676
        ax0, ax1, atop = 36, 340, 30
        tx, tw, ty = 30, 310, 344
        tank_c = (-70, 240, 120)
        pipe_x = W - 34
        lamp_x = None
    bench_y = (floor - 36) if wide else 266
    s = []
    frame = f"M0,0 H{W} V{H} H0Z"
    sc = []
    # wall, seams, rivets
    sc.append(f'<g filter="url(#grain)"><rect width="{W}" height="{H}" fill="{P["wall"]}"/></g>')
    for x in range(96, W, 96):
        sc.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{floor}" stroke="{P["seam"]}" stroke-width="4"/>')
        for y in range(28, floor - 10, 52):
            sc.append(f'<circle cx="{x - 12}" cy="{y}" r="3.2" fill="{P["seam"]}"/><circle cx="{x - 13}" cy="{y - 1}" r="1.4" fill="{P["rivet"]}"/>')
    # floor
    sc.append(f'<g filter="url(#grain)"><rect x="0" y="{floor}" width="{W}" height="{H - floor}" fill="{P["floor"]}"/></g>')
    for i in range(-10, 12):
        sc.append(f'<line x1="{f(W / 2 + i * 60)}" y1="{floor}" x2="{f(W / 2 + i * 170)}" y2="{H}" stroke="{P["floor_line"]}" stroke-width="2.4"/>')
    # the opening and what is through it
    a_bottom = bench_y + (0 if wide else 0)
    ad = arch(ax0, ax1, atop, a_bottom + (40 if wide else 10))
    bands = "".join(f'<rect x="{ax0 - 10}" y="{f(atop + i * (a_bottom - atop) / 4)}" width="{ax1 - ax0 + 20}" height="{f((a_bottom - atop) / 4 + 2)}" fill="{c}"/>'
                    for i, c in enumerate(P["sky"]))
    if P["cloud"]:
        bands += "".join(f'<circle cx="{f(ax0 + (ax1 - ax0) * cx_)}" cy="{f(atop + (a_bottom - atop) * cy_)}" r="{r_}" fill="{P["cloud"]}"/>'
                         for cx_, cy_, r_ in ((.72, .36, 16), (.8, .33, 20), (.88, .37, 14), (.2, .52, 12), (.27, .5, 16)))
    else:
        bands += kid_flames(ax0 - 10, ax1 + 10, a_bottom + 2, 70)
    inside = bands + studio((ax0 + ax1) / 2 + 26, bench_y + 1, 1.0 if wide else 1.05, xed, animate, uid)
    sc.append(f'<path d="{ad}" fill="{P["sky"][0]}"/>' + clipped(f"op{uid}", ad, inside))
    sc.append(f'<path d="{ad}" fill="none" stroke="{INK}" stroke-width="6"/><path d="{ad}" fill="none" stroke="{P["rim"]}" stroke-width="2" transform="translate(-3 -2)"/>')
    # bench across the opening's sill, standing on the floor
    sc.append(desk(ax0 - 18, ax1 + 18, bench_y, bench_y + 22, xed))
    if wide:  # a bench on legs, standing on the floor
        for lx_ in (ax0 - 6, ax1 + 2):
            sc.append(f'<rect x="{lx_}" y="{bench_y + 22}" width="12" height="{floor - bench_y - 20}" fill="#3A4152" stroke="{INK}" stroke-width="2.6"/>')
        sc.append(tank(*tank_c, P, 3))
    else:  # on a phone the bench is the opening's sill, held to the wall by brackets
        for bx in (ax0 + 20, ax1 - 20):
            sc.append(f'<path d="M{f(bx - 6)},{f(bench_y + 21)} h12 v30 l-30,-30z" fill="#5B6478" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>'
                      f'<circle cx="{f(bx)}" cy="{f(bench_y + 30)}" r="2" fill="{INK}"/><circle cx="{f(bx)}" cy="{f(bench_y + 43)}" r="2" fill="{INK}"/>')
        sc.append(sconce(W - 80, bench_y + 70, P, xed))
        sc.append(gas_cylinder(W - 92, floor, P, xed))
    sc.append(pipes(pipe_x, 0, floor + 6, P, n=2))
    if lamp_x:
        sc.append(hanging_lamp(lamp_x, 8, P, xed))
    if xed and wide:  # spill leaks from the tank and runs down to a puddle on the floor
        lx_, ly_ = (tank_c[0] + tank_c[2] * .72, tank_c[1] + tank_c[2] * .72)
        sc.append(f'<path d="M{f(lx_)},{f(ly_)} q4,30 -2,60 v{f(floor - ly_ - 64)} a5,5 0 0 0 10,0 v{f(-(floor - ly_ - 66))} q4,-30 2,-58z" '
                  f'fill="{C["spill"]}" stroke="{INK}" stroke-width="2.6"/>')
        sc.append(f'<ellipse cx="{f(lx_ + 4)}" cy="{f(floor + 10)}" rx="34" ry="6" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.6"/>')
    # the words, painted onto the wall under the lamp
    sc.append(live_sign(ts, tx, ty - 6, xed, uid, animate))
    yy = ty + 72
    sc.append(ts.text(p["name"], "body-bold", 34 if wide else 31, tx, yy, P["text"],
                      attrs=f' stroke="{INK}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"')[0])
    yy += 28
    for ln in wrap(p["line"], "body-bold", 16, tw):
        sc.append(ts.text(ln, "body-bold", 16, tx, yy, P["muted"])[0])
        yy += 22
    ry = yy + 4
    sc.append(award_wall(ts, tx, ry, tw, p["award"], xed, uid, animate))
    # the stack: reagent bottles on a shelf bolted to the wall
    sy = ry + 136
    rows = [p["stack"]] if wide else [p["stack"][:4], p["stack"][4:]]
    gap, margin = 6, 16   # equal gaps; every bottle stands well inside the plank's ends
    for i, row in enumerate(rows):
        y_ = sy + i * 70
        widths = [max(36, text_width(n, "body-bold", 7.6) + 14) for _, n in row]
        run = sum(widths) + gap * (len(row) - 1)
        x0 = tx
        sc.append(bottles(ts, row, x0 + margin, y_, x0 + margin + run + 1, xed and i == 0, uid + str(i), gap=gap))
        x1 = x0 + run + 2 * margin
        sc.append(shelf(x0, x1, y_, uid + "s" + str(i), xed, brackets=(x0 + margin + 14, x1 - margin - 14), depth=11))
    sc.append(f'<rect width="{W}" height="{H}" filter="url(#paper)" opacity=".5"/>')
    s.append(clipped(f"fr{uid}", frame, "".join(sc)))
    body = f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + "".join(s)
    label = f'{p["name"]}, featured. {p["line"]} {p["award"][0]}, {p["award"][1]}. {p["where"]}.'
    return svg_doc(W, H, body, label)


def kid_flames(x0, x1, base, hmax, seed=5):
    rnd = random.Random(seed)
    out = []
    for k, col in enumerate((C["crimson"], C["phoenix"], C["gold"])):
        d, x = f"M{f(x0)},{f(base)} ", x0
        while x < x1:
            w = rnd.uniform(26, 50)
            hh = hmax * (1 - k * .3) * rnd.uniform(.55, 1)
            d += f"Q{f(x + w * .05)},{f(base - hh * .55)} {f(x + w * .5)},{f(base - hh)} Q{f(x + w * .62)},{f(base - hh * .5)} {f(x + w)},{f(base - hh * .12)} "
            x += w
        out.append(f'<path d="{d}L{f(x1)},{f(base)} Z" fill="{col}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    return "".join(out)


LEET = dict(handle="Acetylsphae", solved=dict(Easy=30, Medium=1, Hard=0), active=11)


def leet(theme, animate=True, v=LEET):
    """LeetCode on a lab CRT standing on a desk: total solved races up, three difficulty bars
    fill in steps. The caption is a plate screwed to the desk front."""
    xed = theme == "dark"
    P = THEME[theme]
    uid = f"lc{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    W, H = 252, 188
    total = sum(v["solved"].values())
    mx = max(v["solved"].values()) or 1

    def screen(sx, sy, sw, sh):
        g = [stepped_count(ts, total, "body-bold", 40, sx + 12, sy + 42, P["screen_text"], "start", animate),
             ts.text("solved", "body-bold", 12, sx + 16 + text_width(str(total), "body-bold", 40), sy + 40, P["screen_text"])[0]]
        for i, (k, col) in enumerate((("Easy", P["easy"]), ("Medium", P["medium"]), ("Hard", P["hard"]))):
            n = v["solved"][k]
            by = sy + 54 + i * 11
            bw = (sw - 66) * n / mx
            g.append(f'<rect x="{f(sx + 12)}" y="{f(by)}" width="{f(sw - 66)}" height="6" fill="#FFFFFF" opacity=".1"/>')
            bar = f'<rect x="{f(sx + 12)}" y="{f(by)}" width="{f(max(bw, 2))}" height="6" fill="{col}"'
            if animate and n:
                bar += (f'><animate attributeName="width" values="0;{f(bw * .33)};{f(bw * .66)};{f(bw)}" keyTimes="0;.3;.6;.9" '
                        f'calcMode="discrete" dur=".6s" begin="{.5 + i * .1:.1f}s" fill="freeze"/></rect>')
            else:
                bar += "/>"
            g.append(bar)
            g.append(ts.text(f"{k[0]} {n}", "body-bold", 9.5, sx + sw - 48, by + 6, P["screen_text"])[0])
        return "".join(g)

    desk_y = 140
    content = desk(0, W, desk_y, H, xed)
    content += monitor(126, desk_y + 1, 196, 112, P, xed, screen, uid)
    content += label_plate(ts, 22, desk_y + 14, 208, 20, f"@{v['handle']}", f"{v['active']} active days", P)
    if xed:
        content += f'<ellipse cx="200" cy="{desk_y + 4}" rx="22" ry="3.5" fill="{C["spill"]}" stroke="{INK}" stroke-width="2"/>'
        content += f'<path d="M212,{desk_y + 6} v10 a3.5,3.5 0 0 0 7,0 v-10z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2"/>'
    wall = lab_wall(0, 0, W, desk_y, xed)
    s = [panel(6, 6, 238, 172, P["panel"], 23, uid, wall + content)]
    if not xed:
        s.append(tape(30, 8, 46, -28))
    else:
        s.append(corner_spill(226, 8, 51, 1.4, 11))
    group = "".join(s)
    if xed:
        group = f'<g transform="rotate(.8 {W / 2} {H / 2})">{group}</g>'
    body = f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + group
    label = (f"LeetCode @{v['handle']}: {total} problems solved ({v['solved']['Easy']} easy, {v['solved']['Medium']} medium, "
             f"{v['solved']['Hard']} hard) over {v['active']} active days.")
    return svg_doc(W, H, body, label)


if __name__ == "__main__":
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
