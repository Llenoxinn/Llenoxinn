"""The rest of the DEXTER / XED README, drawn in the same painted-lab language as the hero and
the featured project: project drawers, the trophy wall, the chemical cabinet (stack), the
live instruments (contributions, picoGym) and the contact intercoms.

Every object stands on, hangs from, is screwed to or plugs into something. Light theme is
DEXTER (tidy), dark theme is XED (scorched, cracked, spilling).
"""
import json
import math
import random
import re

import kid
from notebook import ROOT, Typesetter, svg_doc, text_width, wrap
from panels import (THEME, bottles, desk, lab_wall, monitor, scorch, shelf, stepped_count)
from toon import INK, PHOENIX as C, clipped, defs as toon_defs, f, fold, inked, rpoly, smooth

STEEL, STEEL_DK, STEEL_LT = "#5B6478", "#3A4152", "#9AA3B8"


def doc(w, h, body, ts, label):
    return svg_doc(w, h, f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + body, label)


def tooth(w, h):
    return f'<rect width="{w}" height="{h}" filter="url(#paper)" opacity=".45"/>'


def bolt(x, y, r=3.2):
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{STEEL_LT}" stroke="{INK}" stroke-width="1.8"/><circle cx="{f(x - .8)}" cy="{f(y - .8)}" r="1" fill="#FFFFFF" opacity=".7"/>'


def brass_plate(ts, x, y, w, h, lines, uid):
    """An engraved brass plate screwed on at both ends. lines: [(text, size, bold)]"""
    d = rpoly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 3)
    out = [f'<path d="{d}" fill="{INK}" transform="translate(3 3)"/>',
           inked(d, C["gold"], 2.2, extra=f'<rect x="{f(x)}" y="{f(y + h * .58)}" width="{f(w)}" height="{f(h)}" fill="{C["gold_sh"]}" opacity=".6"/>'
                 + f'<path d="M{f(x + w * .6)},{f(y)} h10 l-16,{h} h-10z" fill="#FFFFFF" opacity=".25"/>'),
           bolt(x + 6, y + h / 2, 2.2), bolt(x + w - 6, y + h / 2, 2.2)]
    yy = y + 3
    for text, size, bold in lines:
        yy += size + 3
        out.append(ts.text(text, "body-bold" if bold else "body", size, x + w / 2, yy, "#4A2E0A", anchor="middle")[0])
    return "".join(out)


# ------------------------------------------------------------------ section header copy

LINES = {
    "projects": ("Web apps, 3D visualizers, a CTF platform and a tower defense game.",
                 "Web apps, 3D toys, a CTF arena and a tower defense game. Most survived."),
    "wins": ("Wins and placements from hackathons and CTFs.", "Things I broke well enough to win."),
    "stack": ("Languages, frameworks and tools I build and ship with.", "What I mix, and what I set on fire."),
    "live": ("Live from GitHub, LeetCode and picoGym, every hour.", "Still breathing. Readings every hour."),
    "contact": ("Open to projects, internships and CTF or hackathon teams.", "Ping me. Hackathons, CTFs, internships."),
}


# ------------------------------------------------------------------ project drawers

PROJECTS = [
    dict(name="dfCTF", repo="Llenoxinn/dfCTF", prop="flag",
         line="Capture flags and climb the weekly leaderboard.", where="public"),
    dict(name="BELaude", repo="Llenoxinn/BELaude", prop="cap",
         line="Track the GWA you need for UP Latin honors.", where="public"),
    dict(name="Sylvi", repo="Llenoxinn/Sylvi", prop="photos",
         line="Print-ready ID photo sheets, true to size.", where="public"),
    dict(name="Olatz-Tol", repo="Llenoxinn/Olatz-tol", prop="collatz",
         line="Watch any 3n + 1 path fall to 1.", where="public"),
    dict(name="Protein Viewer Lite", repo="Llenoxinn/Protein-Structure-Viewer-Lite-", prop="helix",
         line="3D protein structures on raw Three.js.", where="public"),
    dict(name="viscal", repo="Llenoxinn/Viscal", prop="scope",
         line="Generative art from pure math.", where="public"),
    dict(name="Perk the Star", repo="GeoCeff/perk-the-star", prop="orbit",
         line="Defend the Sun with orbital towers.", where="with GeoCeff"),
    dict(name="PhyTree", repo=None, prop="tree",
         line="Build and trace phylogenetic trees.", where="private"),
]


def prop_art(kind, cx, base, xed, animate, uid):
    """The project's object, standing on the drawer's little shelf at `base`."""
    o = []
    if kind == "flag":   # a flag on a pole planted in a sandbag
        o.append(inked(rpoly([(cx - 20, base - 12), (cx + 20, base - 12), (cx + 22, base + 2), (cx - 22, base + 2)], 6), "#C9A66B", 2.4))
        o.append(f'<path d="M{f(cx - 4)},{f(base - 10)} V{f(base - 64)}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
                 f'<path d="M{f(cx - 4)},{f(base - 10)} V{f(base - 64)}" stroke="{STEEL_LT}" stroke-width="2.4" stroke-linecap="round"/>')
        flag_a = f'<path d="M{f(cx - 2)},{f(base - 62)} q14,-6 28,0 q-4,10 0,20 q-14,-6 -28,0z" fill="{C["crimson"]}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
        flag_b = f'<path d="M{f(cx - 2)},{f(base - 62)} q14,6 28,0 q4,10 0,20 q-14,6 -28,0z" fill="{C["crimson"]}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
        o.append(two_frame(flag_a, flag_b, animate, 1.0))
    elif kind == "cap":  # a graduation cap on a stack of two books
        for i, col in enumerate((C["prussian"], C["crimson"])):
            y = base - 10 - i * 11
            o.append(inked(rpoly([(cx - 24 + i * 3, y), (cx + 24 - i * 3, y), (cx + 24 - i * 3, y + 11), (cx - 24 + i * 3, y + 11)], 2), col, 2.2,
                           extra=f'<rect x="{f(cx + 10)}" y="{f(y)}" width="20" height="12" fill="{C["bone"]}"/>'))
        y = base - 32
        o.append(inked(f"M{f(cx - 12)},{f(y - 2)} v-8 h24 v8 q-12,6 -24,0z", INK, 1.6))
        o.append(f'<path d="M{f(cx - 28)},{f(y - 12)} L{f(cx)},{f(y - 22)} L{f(cx + 28)},{f(y - 12)} L{f(cx)},{f(y - 2)}Z" fill="#1E2230" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>')
        o.append(f'<path d="M{f(cx)},{f(y - 12)} Q{f(cx + 18)},{f(y - 10)} {f(cx + 20)},{f(y + 4)}" fill="none" stroke="{C["gold"]}" stroke-width="2.4"/><circle cx="{f(cx + 20)}" cy="{f(y + 6)}" r="3" fill="{C["gold"]}" stroke="{INK}" stroke-width="1.4"/>')
    elif kind == "photos":  # an ID photo sheet clipped to a little easel
        o.append(f'<path d="M{f(cx - 18)},{f(base + 1)} L{f(cx - 6)},{f(base - 60)} M{f(cx + 18)},{f(base + 1)} L{f(cx + 6)},{f(base - 60)}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M{f(cx - 18)},{f(base + 1)} L{f(cx - 6)},{f(base - 60)} M{f(cx + 18)},{f(base + 1)} L{f(cx + 6)},{f(base - 60)}" stroke="#A8693E" stroke-width="2" stroke-linecap="round"/>')
        sheet = rpoly([(cx - 22, base - 58), (cx + 22, base - 58), (cx + 22, base - 14), (cx - 22, base - 14)], 2)
        o.append(inked(sheet, "#FFFFFF", 2.2))
        for i in range(2):
            for j in range(2):
                px, py = cx - 17 + i * 18, base - 53 + j * 20
                o.append(f'<rect x="{f(px)}" y="{f(py)}" width="15" height="17" fill="#8FD3FF" stroke="{INK}" stroke-width="1.2"/>'
                         f'<circle cx="{f(px + 7.5)}" cy="{f(py + 7)}" r="3.4" fill="#E3AD84"/><path d="M{f(px + 2)},{f(py + 17)} q5.5,-7 11,0z" fill="{C["prussian"]}"/>')
        o.append(f'<rect x="{f(cx - 6)}" y="{f(base - 63)}" width="12" height="8" rx="2" fill="{STEEL_LT}" stroke="{INK}" stroke-width="1.8"/>')
    elif kind == "collatz":  # a stepped ladder of number tiles falling to 1
        seq = [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
        pts = [(cx - 34 + i * 4.2, base - 8 - math.log(v + 1) * 13) for i, v in enumerate(seq)]
        o.append(f'<rect x="{f(cx - 40)}" y="{f(base - 70)}" width="80" height="66" rx="4" fill="#1E2436" stroke="{INK}" stroke-width="2.6"/>')
        o.append(f'<path d="M{f(cx - 38)},{f(base - 4)} V{f(base + 2)} M{f(cx + 38)},{f(base - 4)} V{f(base + 2)}" stroke="{INK}" stroke-width="4"/>')
        d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
        line = f'<path d="{d}" fill="none" stroke="{C["gold"]}" stroke-width="2.4" stroke-linejoin="round"/>'
        o.append(reveal_path(line, cx - 40, base - 70, 80, 66, animate, uid))
        o.append(f'<circle cx="{f(pts[-1][0])}" cy="{f(pts[-1][1])}" r="3.4" fill="{C["spill"]}" stroke="{INK}" stroke-width="1.6"/>')
    elif kind == "helix":  # a double helix model in a specimen jar
        jar = rpoly([(cx - 20, base - 62), (cx + 20, base - 62), (cx + 22, base + 2), (cx - 22, base + 2)], 8)
        o.append(inked(jar, "#CFE6EA", 2.4, extra=f'<rect x="{f(cx - 30)}" y="{f(base - 40)}" width="60" height="50" fill="#BDE6C8" opacity=".6"/>'))
        for k in range(9):
            y = base - 54 + k * 6
            dx = math.sin(k * .8) * 12
            o.append(f'<path d="M{f(cx - dx)},{f(y)} L{f(cx + dx)},{f(y)}" stroke="{INK}" stroke-width="1.4"/>'
                     f'<circle cx="{f(cx - dx)}" cy="{f(y)}" r="2.8" fill="{C["crimson"]}" stroke="{INK}" stroke-width="1.2"/>'
                     f'<circle cx="{f(cx + dx)}" cy="{f(y)}" r="2.8" fill="{C["gold"]}" stroke="{INK}" stroke-width="1.2"/>')
        o.append(f'<rect x="{f(cx - 22)}" y="{f(base - 70)}" width="44" height="9" rx="3" fill="{STEEL}" stroke="{INK}" stroke-width="2.2"/>')
        o.append(fold([(cx - 14, base - 56), (cx - 15, base - 18)], 2.6, "#FFFFFF"))
    elif kind == "scope":  # an oscilloscope drawing a Lissajous curve
        o.append(inked(rpoly([(cx - 34, base - 58), (cx + 34, base - 58), (cx + 34, base + 1), (cx - 34, base + 1)], 5), "#C9C2AE" if not xed else "#4A4F63", 2.6))
        o.append(f'<rect x="{f(cx - 28)}" y="{f(base - 52)}" width="40" height="40" rx="5" fill="#071019" stroke="{INK}" stroke-width="2"/>')
        liss = "M" + " L".join(f"{f(cx - 8 + math.sin(3 * a + .6) * 15)},{f(base - 32 + math.sin(2 * a) * 15)}" for a in [k / 60 * math.tau for k in range(61)])
        o.append(f'<path d="{liss}" fill="none" stroke="{C["spill"]}" stroke-width="1.8"/>')
        for i in range(3):
            o.append(f'<circle cx="{f(cx + 24)}" cy="{f(base - 46 + i * 14)}" r="3.6" fill="{STEEL_LT}" stroke="{INK}" stroke-width="1.6"/>')
    elif kind == "orbit":  # a sun on a stand with a tower riding its ring
        o.append(f'<path d="M{f(cx)},{f(base + 1)} V{f(base - 18)}" stroke="{INK}" stroke-width="5"/>'
                 f'<rect x="{f(cx - 16)}" y="{f(base - 4)}" width="32" height="6" rx="2" fill="{STEEL}" stroke="{INK}" stroke-width="2"/>')
        o.append(f'<ellipse cx="{f(cx)}" cy="{f(base - 42)}" rx="32" ry="11" fill="none" stroke="{INK}" stroke-width="4"/>'
                 f'<ellipse cx="{f(cx)}" cy="{f(base - 42)}" rx="32" ry="11" fill="none" stroke="{STEEL_LT}" stroke-width="1.4"/>')
        o.append(f'<circle cx="{f(cx)}" cy="{f(base - 42)}" r="15" fill="{C["gold"]}" stroke="{INK}" stroke-width="2.6"/>'
                 f'<path d="M{f(cx - 15)},{f(base - 42)} A15,15 0 0 0 {f(cx + 15)},{f(base - 42)}Z" fill="{C["phoenix"]}"/>'
                 f'<circle cx="{f(cx)}" cy="{f(base - 42)}" r="15" fill="none" stroke="{INK}" stroke-width="2.6"/>')
        tower = f'<rect x="-4" y="-9" width="8" height="10" fill="{C["crimson"]}" stroke="{INK}" stroke-width="1.8"/><path d="M-6,-9 h12 l-6,-6z" fill="{C["gold"]}" stroke="{INK}" stroke-width="1.6"/>'
        if animate:
            steps = [(cx + math.cos(a) * 32, base - 42 + math.sin(a) * 11) for a in [k * math.tau / 8 for k in range(8)]]
            vals = ";".join(f"{f(x)} {f(y)}" for x, y in steps)
            o.append(f'<g transform="translate({f(steps[1][0])} {f(steps[1][1])})"><animateTransform attributeName="transform" type="translate" values="{vals}" '
                     f'calcMode="discrete" dur="4s" repeatCount="indefinite"/>{tower}</g>')
        else:
            o.append(f'<g transform="translate({f(cx + 22)} {f(base - 34)})">{tower}</g>')
    elif kind == "tree":  # a branching tree in a lab pot
        pot = rpoly([(cx - 18, base - 22), (cx + 18, base - 22), (cx + 14, base + 1), (cx - 14, base + 1)], 3)
        o.append(inked(pot, C["phoenix"], 2.4))
        o.append(f'<rect x="{f(cx - 21)}" y="{f(base - 27)}" width="42" height="7" rx="2" fill="{C["ember"]}" stroke="{INK}" stroke-width="2"/>')
        segs = [((cx, base - 26), (cx, base - 44)), ((cx, base - 44), (cx - 16, base - 56)), ((cx, base - 44), (cx + 14, base - 58)),
                ((cx - 16, base - 56), (cx - 24, base - 66)), ((cx - 16, base - 56), (cx - 8, base - 68)), ((cx + 14, base - 58), (cx + 22, base - 68))]
        for (x0, y0), (x1, y1) in segs:
            o.append(f'<path d="M{f(x0)},{f(y0)} V{f(y1)} H{f(x1)}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
                     f'<path d="M{f(x0)},{f(y0)} V{f(y1)} H{f(x1)}" fill="none" stroke="#7A4524" stroke-width="2"/>')
        for x, y in ((cx - 24, base - 66), (cx - 8, base - 68), (cx + 22, base - 68)):
            o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="5" fill="{C["spill"] if xed else "#4EA54A"}" stroke="{INK}" stroke-width="2"/>')
    return "".join(o)


def two_frame(a, b, animate, period):
    if not animate:
        return a
    an = lambda v: f'<animate attributeName="opacity" values="{v}" calcMode="discrete" dur="{period}s" repeatCount="indefinite"/>'
    return f'<g>{an("1;0")}{a}</g><g opacity="0">{an("0;1")}{b}</g>'


def reveal_path(svg, x, y, w, h, animate, uid):
    if not animate:
        return svg
    vals = ";".join(f"{f(w * k / 6)}" for k in range(1, 7)) + f";{f(w)};{f(w * .1)}"
    return (f'<clipPath id="rv{uid}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}">'
            f'<animate attributeName="width" values="{vals}" keyTimes="0;.08;.16;.24;.32;.4;.9;1" calcMode="discrete" dur="5s" repeatCount="indefinite"/></rect></clipPath>'
            f'<g clip-path="url(#rv{uid})">{svg}</g>')


STACKS = {  # same lists as lab/build_projects.py
    "dfCTF": ["TypeScript", "Next.js", "React", "PostgreSQL", "Drizzle", "Docker"],
    "BELaude": ["React", "TypeScript", "Vite", "Tailwind CSS", "Vitest", "Python"],
    "Sylvi": ["TypeScript", "JavaScript", "React", "Vite", "PL/pgSQL", "HTML", "CSS"],
    "Olatz-Tol": ["React", "Vite", "Tailwind CSS", "Zustand", "Lucide"],
    "Protein Viewer Lite": ["React", "Vite", "Three.js", "React Three Fiber", "Drei", "Tailwind CSS"],
    "viscal": ["React", "Vite", "Tailwind CSS"],
    "Perk the Star": ["Godot", "C++", "GDScript"],
    "PhyTree": ["TypeScript", "React", "Vite", "Tailwind CSS", "D3.js", "Zustand"],
}


def tags(ts, names, x, y, room, xed, rows=2):
    """The stack as small enamel tags, text only, wrapping onto a second row; anything past
    that folds into +N."""
    out, fs, x0, row = [], 9, x, 0
    for k, n in enumerate(names):
        w = text_width(n, "body-bold", fs) + 11
        rest = len(names) - k - 1
        if x + w > room and row + 1 < rows:
            row, x, y = row + 1, x0, y + 17
        if x + w + (30 if rest and row + 1 == rows else 0) > room:
            more = f"+{len(names) - k}"
            w = text_width(more, "body-bold", fs) + 12
            out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="14" rx="3" fill="#C9C2AE" stroke="{INK}" stroke-width="1.6"/>'
                       + ts.text(more, "body-bold", fs, x + 5.5, y + 10.4, INK)[0])
            break
        out.append(f'<rect x="{f(x + 1.4)}" y="{f(y + 1.4)}" width="{f(w)}" height="14" rx="3" fill="{INK}"/>'
                   f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="14" rx="3" fill="{C["prussian"] if not xed else C["oxblood"]}" stroke="{INK}" stroke-width="1.6"/>'
                   + ts.text(n, "body-bold", fs, x + 5.5, y + 10.4, C["bone"])[0])
        x += w + 4
    return "".join(out)


def project_card(p, theme, animate=True):
    """A steel drawer front pulled from the lab wall, with one wide paper label slid into its
    brass holder: the project's name and where the code lives, one line about it, and its
    stack as small enamel tags. No pictures."""
    xed = theme == "dark"
    W, H = 376, 104
    uid = f"pc{re.sub('[^a-z]', '', p['name'].lower())}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    s = []
    front = rpoly([(4, 6), (W - 8, 6), (W - 8, H - 8), (4, H - 8)], 7)
    s.append(f'<path d="{front}" fill="{INK}" transform="translate(4 4)"/>')
    s.append(inked(front, "#4B5370" if not xed else "#1E2438", 3, extra=f'<path d="M4,10 H{W - 8}" stroke="#7C86A0" stroke-width="2.2" opacity=".8"/>'))
    # brass holder and the paper label in it
    lx, ly, lw, lh = 16, 15, W - 40, H - 31
    s.append(f'<rect x="{lx - 5}" y="{ly - 5}" width="{lw + 10}" height="{lh + 10}" rx="4" fill="{C["gold"]}" stroke="{INK}" stroke-width="2.4"/>'
             f'<rect x="{lx - 5}" y="{ly + lh - 1}" width="{lw + 10}" height="6" fill="{C["gold_sh"]}"/>'
             + bolt(lx, ly + lh / 2, 2) + bolt(lx + lw, ly + lh / 2, 2))
    s.append(f'<rect x="{lx + 5}" y="{ly}" width="{lw - 10}" height="{lh}" fill="{C["bone"]}" stroke="{INK}" stroke-width="1.8"/>')
    s.append(f'<path d="M{lx + lw * .7},{ly} l-14,{lh}" stroke="#FFFFFF" stroke-width="7" opacity=".3"/>')
    s.append(ts.text(p["name"], "body-bold", 16, lx + 13, ly + 19, INK)[0])
    # where the code lives: a lit plate on the label's top right
    wtxt = p["where"].upper()
    ww = text_width(wtxt, "body-bold", 8.4, 1) + 18
    wx = lx + lw - 10 - ww
    lit = p["where"] != "private"
    s.append(f'<rect x="{f(wx)}" y="{ly + 6}" width="{f(ww)}" height="14" rx="2" fill="#2A2F44" stroke="{INK}" stroke-width="1.6"/>'
             f'<circle cx="{f(wx + 7.5)}" cy="{ly + 13}" r="2.6" fill="{C["spill"] if lit else "#5A1A20"}" stroke="{INK}" stroke-width="1"/>'
             + ts.text(wtxt, "body-bold", 8.4, wx + 14, ly + 16.2, C["bone"], tracking=1)[0])
    s.append(ts.text(p["line"], "body", 11.4, lx + 13, ly + 33, "#3A4152")[0])
    s.append(tags(ts, STACKS[p["name"]], lx + 13, ly + 39, lx + lw - 10, xed))
    if xed:
        s.append(scorch(30, H - 12, 10, len(p["name"])))
        if len(p["name"]) % 2:
            s.append(kid.splat(W - 14, 12, 6, len(p["name"]) + 40, drips=1, run=1.4))
    s.append(tooth(W, H))
    label = f'{p["name"]}, {p["where"]} repository: {p["line"]} Built with {", ".join(STACKS[p["name"]])}.'
    return doc(W, H, "".join(s), ts, label)


# ------------------------------------------------------------------ trophy wall

WINS = [
    dict(kind="cup", title="Champion, Rage Quit Award", event="MALFUNCTION Hackathon 2026", org="iDE.A iAcademy"),
    dict(kind="medal", title="Top 2 Student Performer", event="HackforGov5 Region 7", org="DICT Region 7"),
    dict(kind="flagcup", title="Champion", event="Mission: CTF", org="UP Computer Science Guild"),
]


def trophy(kind, cx, base, xed, animate, uid):
    o = []
    if kind in ("cup", "flagcup"):
        o.append(inked(rpoly([(cx - 26, base - 18), (cx + 26, base - 18), (cx + 30, base + 2), (cx - 30, base + 2)], 3), "#3A2412" if not xed else "#2A1A10", 2.6))
        o.append(f'<rect x="{f(cx - 8)}" y="{f(base - 40)}" width="16" height="23" fill="{C["gold_sh"]}" stroke="{INK}" stroke-width="2.4"/>')
        cup = f"M{f(cx - 30)},{f(base - 100)} H{f(cx + 30)} C{f(cx + 30)},{f(base - 60)} {f(cx + 14)},{f(base - 44)} {f(cx)},{f(base - 42)} C{f(cx - 14)},{f(base - 44)} {f(cx - 30)},{f(base - 60)} {f(cx - 30)},{f(base - 100)}Z"
        for sx in (-1, 1):
            o.append(f'<path d="M{f(cx + sx * 28)},{f(base - 92)} q{sx * 22},2 {sx * 16},24 q-4,10 {-sx * 14},10" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
                     f'<path d="M{f(cx + sx * 28)},{f(base - 92)} q{sx * 22},2 {sx * 16},24 q-4,10 {-sx * 14},10" fill="none" stroke="{C["gold"]}" stroke-width="3.4" stroke-linecap="round"/>')
        o.append(inked(cup, C["gold"], 3, extra=clipped(f"cp{uid}", cup, f'<rect x="{f(cx + 8)}" y="{f(base - 110)}" width="30" height="80" fill="{C["gold_sh"]}"/>')))
        o.append(fold([(cx - 20, base - 94), (cx - 18, base - 70), (cx - 8, base - 54)], 4, C["glint"]))
        o.append(f'<path d="M{f(cx - 31)},{f(base - 100)} H{f(cx + 31)}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
        if kind == "flagcup":
            o.append(f'<path d="M{f(cx + 6)},{f(base - 100)} V{f(base - 136)}" stroke="{INK}" stroke-width="4"/>'
                     f'<path d="M{f(cx + 7)},{f(base - 136)} q12,-4 22,0 v14 q-10,-4 -22,0z" fill="{C["crimson"]}" stroke="{INK}" stroke-width="2.2"/>')
        else:
            star = " ".join(f"{f(cx + math.cos(-math.pi / 2 + k * math.pi / 5) * (11 if k % 2 == 0 else 4.6))},{f(base - 76 + math.sin(-math.pi / 2 + k * math.pi / 5) * (11 if k % 2 == 0 else 4.6))}" for k in range(10))
            o.append(f'<polygon points="{star}" fill="{C["glint"]}" stroke="{C["gold_dk"]}" stroke-width="1.6"/>')
    else:  # medal on a hook
        hy = base - 128
        o.append(f'<path d="M{f(cx - 8)},{f(hy)} h16 v6 h-16z" fill="{STEEL}" stroke="{INK}" stroke-width="2"/>'
                 f'<path d="M{f(cx)},{f(hy + 6)} v8 q0,6 6,6" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
        rib = (f'<path d="M{f(cx)},{f(hy + 18)} L{f(cx - 20)},{f(hy + 66)} L{f(cx - 6)},{f(hy + 66)} L{f(cx + 4)},{f(hy + 30)}Z" fill="{C["prussian"]}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
               f'<path d="M{f(cx)},{f(hy + 18)} L{f(cx + 20)},{f(hy + 66)} L{f(cx + 6)},{f(hy + 66)} L{f(cx - 4)},{f(hy + 30)}Z" fill="{C["crimson"]}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>')
        my, r = hy + 90, 26
        disc = (f'<circle cx="{f(cx)}" cy="{f(my)}" r="{r + 3}" fill="{INK}"/><circle cx="{f(cx)}" cy="{f(my)}" r="{r}" fill="#D6DCE6"/>'
                f'<path d="M{f(cx - r)},{f(my)} A{r},{r} 0 0 0 {f(cx + r)},{f(my)}Z" fill="#AEB6C6"/>'
                f'<circle cx="{f(cx)}" cy="{f(my)}" r="{r * .74}" fill="none" stroke="#7C86A0" stroke-width="2"/>')
        disc += f'<path d="M{f(cx - 7)},{f(my - 6)} q7,-8 14,0 q0,6 -14,14 h14" fill="none" stroke="#5B6478" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
        disc += fold([(cx - r * .7, my - r * .3), (cx - r * .3, my - r * .76), (cx + r * .1, my - r * .84)], 3, "#FFFFFF")
        body = rib + disc
        if animate:
            vals = ";".join(f"{a} {f(cx)} {f(hy + 18)}" for a in (0, 0, 6, -4, 2.5, -1, 0))
            body = f'<g><animateTransform attributeName="transform" type="rotate" values="{vals}" keyTimes="0;.6;.65;.7;.75;.8;.85" calcMode="discrete" dur="7s" begin="2s" repeatCount="indefinite"/>{body}</g>'
        o.append(body)
    return "".join(o)


def glint(cx, top, animate, begin):
    if not animate:
        return ""
    star = f'<path d="M0,-9 Q1,-1 9,0 Q1,1 0,9 Q-1,1 -9,0 Q-1,-1 0,-9Z" fill="#FFFFFF"/>'
    return (f'<g transform="translate({f(cx)} {f(top)})" opacity="0"><animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.04;.08;1" '
            f'calcMode="discrete" dur="6s" begin="{begin}s" repeatCount="indefinite"/>{star}</g>')


def trophy_wall(theme, layout="wide", animate=True):
    xed = theme == "dark"
    wide = layout == "wide"
    W = 760 if wide else 400
    H = 284 if wide else 780
    uid = f"tw{layout[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    s = [lab_wall(0, 0, W, H, xed)]
    slots = [(W * (i + .5) / 3, 196) for i in range(3)] if wide else [(W / 2, 196 + i * 246) for i in range(3)]
    for i, (w, (cx, base)) in enumerate(zip(WINS, slots)):
        x0, x1 = cx - (W / 3 if wide else W) / 2 + 18, cx + (W / 3 if wide else W) / 2 - 18
        sag = xed and i == 2
        s.append(shelf(x0, x1, base, f"{uid}{i}", xed, brackets=(x0 + 26, x1 - 26), depth=12, sag_right=sag))
        s.append(trophy(w["kind"], cx, base + (2 if not sag else 5), xed, animate, f"{uid}{i}"))
        s.append(glint(cx - 14, base - 92, animate, 1 + i * 2))
        pw = min(x1 - x0 + 4, max(text_width(w["title"], "body-bold", 12), text_width(w["event"], "body-bold", 10), text_width(w["org"], "body", 9.5)) + 34)
        s.append(brass_plate(ts, cx - pw / 2, base + 22, pw, 52, [(w["title"], 12, True), (w["event"], 10, True), (w["org"], 9.5, False)], f"{uid}{i}"))
    if xed:
        s.append(scorch(W * .5 + 60, 30, 26, 3))
        s.append(kid.splat(W - 40, 60, 9, 77, drips=2, run=2.4))
    s.append(tooth(W, H))
    label = "Trophy wall. " + " ".join(f'{w["title"]}, {w["event"]}, {w["org"]}.' for w in WINS)
    return doc(W, H, "".join(s), ts, label)


# ------------------------------------------------------------------ chemical cabinet (stack)

SHELF = [
    ("Languages", ["C", "C++", "C#", "Haskell", "Kotlin", "Prolog", "Python", "JavaScript", "TypeScript", "HTML", "CSS", "LaTeX"]),
    ("Web", ["React", "Next.js", "Svelte", "Vite", "Tailwind CSS", "Zustand", "D3.js", "Three.js", "Electron"]),
    ("Back end", ["Node.js", "Supabase", "PostgreSQL", "Drizzle"]),
    ("Test and ship", ["Docker", "Vercel", "GitHub Actions", "Vitest", "Playwright"]),
    ("Tools", ["Godot", "WSL", "UCSF ChimeraX", "Audacity"]),
    ("AI agents", ["Antigravity", "Codex", "Claude", "OpenCode"]),
    ("Design", ["Figma", "Adobe Photoshop", "Adobe InDesign", "Adobe Illustrator", "Canva"]),
]


def jar(cx, base, name, k, xed, uid):
    """A squat reagent jar carrying the tool's logo on its label (name in the alt text)."""
    from icons import ICONS
    from notebook import mark
    w, h = 40, 44
    x, y = cx - w / 2, base - h + 2
    caps = (C["crimson"], C["gold"], C["phoenix"], C["prussian"])
    liq = (C["spill"], C["phoenix"], "#8FD3FF", C["gold"])[k % 4]
    body = rpoly([(x, y + 10), (x + w, y + 10), (x + w, y + h), (x, y + h)], [9, 9, 4, 4])
    out = [inked(body, "#CFE6EA", 2.4, extra=f'<rect x="{x - 2}" y="{f(y + h * .55)}" width="{w + 4}" height="{h}" fill="{liq}"/>'),
           inked(rpoly([(cx - 11, y), (cx + 11, y), (cx + 11, y + 10), (cx - 11, y + 10)], 3), caps[k % 4], 2.2),
           f'<rect x="{x + 6}" y="{y + 15}" width="{w - 12}" height="24" rx="2" fill="{C["bone"]}" stroke="{INK}" stroke-width="1.6"/>']
    key = name.lower()
    if key in ICONS:
        out.append(mark(name, cx - 9, y + 18, 18, INK))
    else:
        out.append(f'<text x="{f(cx)}" y="{y + 31}" font-size="7" text-anchor="middle">?</text>')
    out.append(fold([(x + 4, y + 14), (x + 3, y + 30)], 2.2, "#FFFFFF"))
    return "".join(out)


def cabinet(theme, layout="wide", animate=True):
    xed = theme == "dark"
    wide = layout == "wide"
    W = 760 if wide else 400
    per = 16 if wide else 8
    rows = []
    for g, names in SHELF:
        for i in range(0, len(names), per):
            rows.append((g if i == 0 else "", names[i:i + per]))
    if wide:  # pack short groups side by side on one plank
        packed, cur = [], []
        for g, names in rows:
            if cur and sum(len(n) for _, n in cur) + len(names) + len(cur) <= per:
                cur.append((g, names))
            else:
                if cur:
                    packed.append(cur)
                cur = [(g, names)]
        packed.append(cur)
    else:
        packed = [[r] for r in rows]
    row_h = 86
    H = 30 + row_h * len(packed)
    uid = f"cb{layout[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    s = [lab_wall(0, 0, W, H, xed)]
    labels = []
    k = 0
    for r, groups in enumerate(packed):
        base = 22 + 56 + r * row_h
        x = 22
        for gi, (g, names) in enumerate(groups):
            span = len(names) * 44
            if gi:
                x += 30
            s.append(shelf(x - 8, x + span + 4, base, f"{uid}{r}{gi}", xed, brackets=(x + 16, x + span - 20), depth=11,
                           sag_right=xed and r == 1 and gi == 0))
            for j, n in enumerate(names):
                s.append(jar(x + 20 + j * 44, base + 1, n, k, xed, f"{uid}{k}"))
                labels.append(n)
                k += 1
            if g:
                gw = text_width(g.upper(), "body-bold", 8.6, 1) + 14
                s.append(f'<rect x="{x}" y="{base + 14}" width="{f(gw)}" height="13" rx="2" fill="{C["bone"]}" stroke="{INK}" stroke-width="1.4"/>'
                         + ts.text(g.upper(), "body-bold", 8.6, x + 7, base + 23.6, INK, tracking=1)[0])
            x += span
    if xed:
        s.append(kid.splat(W * .62, 16, 10, 91, drips=3, run=3))
        s.append(scorch(W * .2, H - 20, 20, 5))
    s.append(tooth(W, H))
    return doc(W, H, "".join(s), ts, "Stack: " + ", ".join(labels) + ".")


# ------------------------------------------------------------------ live instruments

def contributions_data():
    """Real numbers from the last lab round's card: totals from its label, the 26-week
    heatmap levels read back from its cells."""
    svg = (ROOT / "assets" / "contributions-still-light.svg").read_text(encoding="utf-8")
    lab = re.search(r'aria-label="([^"]*)"', svg).group(1)
    num = lambda pat: int(re.search(pat, lab).group(1))
    heat = ["#dedef4", "#a8a8f6", "#6666fd", "#1313ba", "#0a0a5d"]
    cells = []
    for x, y, fill in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="7" height="7" fill="(#[0-9a-f]+)"', svg):
        if fill in heat:
            cells.append((float(x), float(y), heat.index(fill)))
    xs = sorted({c[0] for c in cells})
    ys = sorted({c[1] for c in cells})
    grid = {(xs.index(x), ys.index(y)): lv for x, y, lv in cells}
    return dict(total=num(r"(\d+) in the last 12"), last7=num(r"(\d+) in the last 7"), streak=num(r"streak (\d+)"),
                best=num(r"best (\d+)"), grid=grid, weeks=len(xs))


def contrib(theme, animate=True):
    """GitHub on a lab CRT standing on the desk: the year's total races up, and the last 26 weeks
    glow on the screen as a phosphor grid that lands along diagonals."""
    v = contributions_data()
    xed = theme == "dark"
    P = THEME[theme]
    uid = f"gh{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    W, H = 252, 188
    phos = [("#1E2A4A", "#2F6BFF", "#5FA8FF", "#A8E0FF", "#FFFFFF"), ("#1A2A1E", "#2E7A3E", "#4FCB62", C["spill"], "#E9FFB8")][xed]

    def screen(sx, sy, sw, sh):
        g = [stepped_count(ts, v["total"], "body-bold", 26, sx + 10, sy + 26, P["screen_text"], "start", animate),
             ts.text("in 12 months", "body-bold", 9.5, sx + 14 + text_width(str(v["total"]), "body-bold", 26), sy + 25, P["screen_text"])[0]]
        cell, gap = 5.2, 1.2
        gx, gy = sx + 10, sy + 34
        for (c, r), lv in v["grid"].items():
            x, y = gx + c * (cell + gap), gy + r * (cell + gap)
            rect = f'<rect x="{f(x)}" y="{f(y)}" width="{cell}" height="{cell}" fill="{phos[lv]}"'
            if animate:
                d = .4 + (c + r) * .025
                rect += f' opacity="1"><animate attributeName="opacity" values="0;1" keyTimes="0;{d / (d + .01):.4f}" calcMode="discrete" dur="{d + .01:.2f}s" fill="freeze"/></rect>'
            else:
                rect += "/>"
            g.append(rect)
        return "".join(g)

    desk_y = 140
    content = lab_wall(0, 0, W, desk_y, xed) + desk(0, W, desk_y, H, xed)
    content += monitor(126, desk_y + 1, 196, 112, P, xed, screen, uid)
    from panels import label_plate
    content += label_plate(ts, 22, desk_y + 14, 208, 20, "@Llenoxinn", f"{v['streak']} day streak", P)
    from panels import panel, tape, corner_spill
    s = [panel(6, 6, 238, 172, P["panel"], 31, uid, content)]
    s.append(tape(30, 8, 46, -28) if not xed else corner_spill(30, 8, 61, 1.4, 11))
    group = "".join(s)
    if xed:
        group = f'<g transform="rotate(-.8 {W / 2} {H / 2})">{group}</g>'
    label = (f"GitHub contributions for @Llenoxinn: {v['total']} in the last 12 months, {v['last7']} in the last 7 days, "
             f"current streak {v['streak']} days, best {v['best']}.")
    return doc(W, H, group, ts, label)


def pico(theme, animate=True):
    """picoGym as a test-tube rack on the desk: one tube per category, each filled in proportion
    to its solves (the busiest category fills its tube), the count etched on the rack under it."""
    data = json.loads((ROOT / "lab" / "data" / "picoctf.json").read_text(encoding="utf-8"))
    cats = [(k, sum(v[d] for d in ("easy", "medium", "hard")), v.get("total")) for k, v in data["solved"].items()]
    total = sum(c[1] for c in cats)
    short = {"General Skills": "GEN", "Reverse Engineering": "REV", "Cryptography": "CRY", "Web Exploitation": "WEB",
             "Artificial Intelligence": "AI", "Forensics": "FOR", "Binary Exploitation": "BIN", "Blockchain": "BLK"}
    colors = {"GEN": "#8FD3FF", "REV": C["phoenix"], "CRY": C["gold"], "WEB": C["spill"], "AI": "#C9A0FF",
              "FOR": "#FF8A9C", "BIN": C["crimson"], "BLK": "#9AA3B8"}
    xed = theme == "dark"
    P = THEME[theme]
    uid = f"pg{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    W, H = 252, 188
    desk_y = 140
    content = lab_wall(0, 0, W, desk_y, xed) + desk(0, W, desk_y, H, xed)
    content += stepped_count(ts, total, "body-bold", 30, 18, 40, P["screen_text"] if xed else C["bone"], "start", animate,
                             attrs=f' stroke="{INK}" stroke-width="4" stroke-linejoin="round" paint-order="stroke"')
    content += ts.text("picoGym solves", "body-bold", 11, 22 + text_width(str(total), "body-bold", 30), 38, C["bone"])[0]
    # the rack
    rx0, rx1, ry = 16, W - 16, desk_y - 22
    n = len(cats)
    step = (rx1 - rx0 - 16) / n
    tubes = []
    for i, (name, solved, tot) in enumerate(cats):
        cx = rx0 + 8 + step * (i + .5)
        top, bot = 52, ry + 8          # the tube passes down into a hole in the rack
        tube = f"M{f(cx - 7)},{f(top)} V{f(bot - 7)} a7,7 0 0 0 14,0 V{f(top)}Z"
        frac = solved / (max(c[1] for c in cats) or 1)
        fill_h = 0 if not solved else (bot - ry) + (ry - top - 6) * max(.06, frac)
        col = colors[short[name]]
        liq = f'<rect x="{f(cx - 9)}" y="{f(bot - fill_h)}" width="18" height="{f(fill_h + 4)}" fill="{col}"'
        if animate and fill_h:
            liq += (f'><animate attributeName="y" values="{f(bot)};{f(bot - fill_h * .4)};{f(bot - fill_h * .8)};{f(bot - fill_h)}" keyTimes="0;.3;.6;.9" '
                    f'calcMode="discrete" dur=".7s" begin="{.4 + i * .08:.2f}s" fill="freeze"/></rect>')
        else:
            liq += "/>"
        tubes.append(inked(tube, "#CFE6EA", 2.2, grain=None, extra=clipped(f"tb{uid}{i}", tube, liq)))
        tubes.append(fold([(cx - 3.5, top + 6), (cx - 3.5, bot - 14)], 1.8, "#FFFFFF"))
        tubes.append(f'<rect x="{f(cx - 9)}" y="{f(top - 5)}" width="18" height="6" rx="2" fill="{STEEL_LT}" stroke="{INK}" stroke-width="1.8"/>')
    content += "".join(tubes)
    content += inked(rpoly([(rx0, ry), (rx1, ry), (rx1, ry + 16), (rx0, ry + 16)], 3), "#7A4524" if not xed else "#4A2A18", 2.6)
    for i, (name, solved, tot) in enumerate(cats):
        cx = rx0 + 8 + step * (i + .5)
        content += ts.text(short[name], "body-bold", 7.6, cx, ry + 7.6, C["bone"], anchor="middle", tracking=.4)[0]
        content += ts.text(str(solved), "body-bold", 7, cx, ry + 14.4, C["gold"], anchor="middle")[0]
    from panels import label_plate, panel, tape, corner_spill
    content += label_plate(ts, 22, desk_y + 14, 208, 20, f"@{data['username']}", f"{len([c for c in cats if c[1]])} of {n} categories", P)
    if xed:
        content += f'<ellipse cx="60" cy="{desk_y + 4}" rx="22" ry="3.5" fill="{C["spill"]}" stroke="{INK}" stroke-width="2"/>'
    s = [panel(6, 6, 238, 172, P["panel"], 41, uid, content)]
    s.append(tape(220, 8, 46, 24) if not xed else corner_spill(220, 8, 71, 1.4, 11))
    group = "".join(s)
    if xed:
        group = f'<g transform="rotate(.6 {W / 2} {H / 2})">{group}</g>'
    label = f"picoGym @{data['username']}: {total} challenges solved. " + ", ".join(f"{k} {s_}" for k, s_, _ in cats if s_) + "."
    return doc(W, H, group, ts, label)


# ------------------------------------------------------------------ contact intercoms

CONTACTS = [("linkedin", "LinkedIn", "linkedin.com/in/dsjuevesano"), ("github", "GitHub", "github.com/Llenoxinn")]


def intercom(key, label, url, theme, animate=True):
    """A wall intercom screwed to the steel: a speaker grille, a big brand-marked call button
    whose lamp pulses now and then, and the address on a paper strip under glass."""
    from notebook import mark
    xed = theme == "dark"
    W, H = 376, 92
    uid = f"ic{key}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    s = [lab_wall(0, 0, W, H, xed)]
    box = rpoly([(10, 8), (W - 12, 8), (W - 12, H - 10), (10, H - 10)], 10)
    s.append(f'<path d="{box}" fill="{INK}" transform="translate(4 4)"/>')
    s.append(inked(box, "#C9C2AE" if not xed else "#4A4F63", 3, extra=f'<rect x="0" y="{H - 34}" width="{W}" height="30" fill="{INK}" opacity=".14"/>'))
    for x, y in ((18, 16), (W - 20, 16), (18, H - 18), (W - 20, H - 18)):
        s.append(bolt(x, y, 2.6))
    # grille
    for r in range(4):
        for c in range(5):
            s.append(f'<circle cx="{34 + c * 9}" cy="{30 + r * 10}" r="2.6" fill="{INK}"/>')
    # call button
    bx, by, br = 112, H / 2 - 1, 24
    lamp = C["spill"] if xed else "#5FA8FF"
    s.append(f'<circle cx="{bx}" cy="{f(by)}" r="{br + 4}" fill="{STEEL}" stroke="{INK}" stroke-width="2.6"/>')
    btn = (f'<circle cx="{bx}" cy="{f(by)}" r="{br}" fill="{C["crimson"] if not xed else C["oxblood"]}" stroke="{INK}" stroke-width="2.6"/>'
           f'<path d="M{bx - br},{f(by)} A{br},{br} 0 0 0 {bx + br},{f(by)}Z" fill="{INK}" opacity=".25"/>'
           + mark(key, bx - 12, by - 12, 24, C["bone"])
           + fold([(bx - 15, by - 10), (bx - 6, by - 19)], 3, "#FFFFFF"))
    s.append(btn)
    halo = f'<circle cx="{bx}" cy="{f(by)}" r="{br + 4}" fill="none" stroke="{lamp}" stroke-width="3"/>'
    if animate:
        s.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0;1;0;0" keyTimes="0;.05;.1;.15;.2;1" calcMode="discrete" dur="5s" begin="{1.2 if key == "github" else 2.4}s" repeatCount="indefinite"/>{halo}</g>')
    # address under glass
    gx, gy, gw, gh = 152, 22, W - 182, 46
    s.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="4" fill="{C["bone"]}" stroke="{INK}" stroke-width="2.4"/>')
    s.append(ts.text(label, "body-bold", 17, gx + 12, gy + 21, INK)[0])
    s.append(ts.text(url, "body", 11.5, gx + 12, gy + 37, "#3A4152")[0])
    s.append(f'<path d="M{gx + gw - 50},{gy} l-30,{gh}" stroke="#FFFFFF" stroke-width="8" opacity=".35"/>')
    if xed:
        s.append(scorch(W - 50, H - 20, 12, 9 + len(key)))
        if key == "github":
            s.append(f'<path d="M{gx + 30},{gy} l8,14 l-6,8 l10,14" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    s.append(tooth(W, H))
    return doc(W, H, "".join(s), ts, f"{label}: {url}")


if __name__ == "__main__":
    import panels
    out = ROOT / "lab" / ".runtime" / "preview" / "readme"
    out.mkdir(parents=True, exist_ok=True)
    panels.LINES.update(LINES)
    for theme in ("light", "dark"):
        for key in LINES:
            for lay in ("wide", "narrow"):
                (out / f"h-{key}-{lay}-{theme}.svg").write_text(panels.header(key, theme, lay, True), encoding="utf-8")
        for lay in ("wide", "narrow"):
            (out / f"feature-{lay}-{theme}.svg").write_text(panels.feature(theme, lay, True), encoding="utf-8")
            (out / f"trophies-{lay}-{theme}.svg").write_text(trophy_wall(theme, lay, True), encoding="utf-8")
            (out / f"stack-{lay}-{theme}.svg").write_text(cabinet(theme, lay, True), encoding="utf-8")
        for p in PROJECTS:
            (out / f"p-{re.sub('[^a-z]', '', p['name'].lower())}-{theme}.svg").write_text(project_card(p, theme), encoding="utf-8")
        (out / f"live-gh-{theme}.svg").write_text(contrib(theme), encoding="utf-8")
        (out / f"live-lc-{theme}.svg").write_text(panels.leet(theme), encoding="utf-8")
        (out / f"live-pg-{theme}.svg").write_text(pico(theme), encoding="utf-8")
        for key, label, url in CONTACTS:
            (out / f"c-{key}-{theme}.svg").write_text(intercom(key, label, url, theme), encoding="utf-8")
    print("readme pieces written to", out)
