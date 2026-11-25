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
from panels import THEME, lab_wall, scorch, shelf
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

LINES = {  # header lines: (DEXTER, XED)
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
    """The stack as small paper chips with an ink outline, text only, wrapping onto a second
    row; anything past that folds into +N."""
    out, fs, x0, row = [], 9, x, 0
    fill = "#FFFFFF" if not xed else "#EFE6CF"
    for k, n in enumerate(names):
        w = text_width(n, "body-bold", fs) + 11
        rest = len(names) - k - 1
        if x + w > room and row + 1 < rows:
            row, x, y = row + 1, x0, y + 17
        if x + w + (30 if rest and row + 1 == rows else 0) > room:
            more = f"+{len(names) - k}"
            w = text_width(more, "body-bold", fs) + 11
            out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="14" rx="7" fill="#D9CDB2" stroke="{INK}" stroke-width="1.3"/>'
                       + ts.text(more, "body-bold", fs, x + 5.5, y + 10.4, INK)[0])
            break
        out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="14" rx="7" fill="{fill}" stroke="{INK}" stroke-width="1.3"/>'
                   + ts.text(n, "body-bold", fs, x + 5.5, y + 10.4, "#2A2F44")[0])
        x += w + 4
    return "".join(out)


ACCENTS = (C["crimson"], C["prussian"], C["phoenix"], C["gold"], "#2E8B57", "#7A4CC2", "#1F8FA0", C["ember"])


def drawer_lamp(cx, cy, colour, animate, begin):
    """A round pilot lamp in a steel bezel on the drawer front. Animated: dark until the label
    lands, flickers on (on, off, on) and holds; every few seconds it blinks once. Lit is the base."""
    lit = (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5.4" fill="{colour}"/>'
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="9" fill="{colour}" opacity=".22"/>'
           f'<circle cx="{f(cx - 1.6)}" cy="{f(cy - 1.8)}" r="1.8" fill="#FFFFFF" opacity=".85"/>')
    out = [f'<circle cx="{f(cx)}" cy="{f(cy)}" r="8" fill="{STEEL}" stroke="{INK}" stroke-width="2.2"/>',
           f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5.4" fill="#1A1E2E" stroke="{INK}" stroke-width="1.4"/>']
    if animate:
        on = (f'<animate attributeName="opacity" values="0;1;0;1" keyTimes="0;.4;.6;.8" calcMode="discrete" dur=".5s" begin="{begin:.2f}s" fill="freeze"/>'
              f'<animate attributeName="opacity" values="1;0;1;1" keyTimes="0;.02;.05;1" calcMode="discrete" dur="6s" begin="{begin + 3:.2f}s" repeatCount="indefinite"/>')
        out.append(f'<g opacity="1">{on}{lit}</g>')
    else:
        out.append(lit)
    out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5.4" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    return "".join(out)


def xed_mess(kind, W, H, lx, ly, lw, lh, seed):
    """One kind of damage per XED drawer, so no two neighbours look the same."""
    if kind == "drip":
        return kid.splat(W - 22, 14, 6, seed, drips=1, run=1.2)
    if kind == "ring":   # a beaker was set down on the label: a stained ring
        cx, cy = lx + lw - 6, ly + lh - 4
        return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="12" fill="none" stroke="#6B8E23" stroke-width="3" opacity=".45"/>'
                f'<circle cx="{f(cx + 2)}" cy="{f(cy + 1)}" r="10" fill="none" stroke="#6B8E23" stroke-width="1.2" opacity=".35"/>')
    if kind == "crack":  # the drawer front took a hit
        return (f'<path d="M{W - 12},{H - 34} l-8,5 l3,6 l-7,4" fill="none" stroke="{INK}" stroke-width="2"/>'
                f'<path d="M{W - 11},{H - 33.4} l-8,5 l3,6 l-7,4" fill="none" stroke="#7C86A0" stroke-width=".9"/>')
    if kind == "tape":   # the label tore and got taped back
        return (f'<g transform="rotate(-28 {f(lx + lw - 16)} {f(ly + lh - 6)})"><rect x="{f(lx + lw - 34)}" y="{f(ly + lh - 13)}" width="36" height="12" '
                f'fill="#EADFC2" opacity=".92" stroke="{INK}" stroke-width="1.4"/></g>')
    if kind == "burn":   # a singed label corner
        x0, y0 = lx + lw, ly + lh
        return (f'<path d="M{f(x0 - 34)},{f(y0)} q8,-6 12,-14 q8,-2 22,0 V{f(y0)}Z" fill="#3A2412" opacity=".55"/>'
                f'<path d="M{f(x0 - 22)},{f(y0)} q4,-4 6,-9 q6,-2 16,0 V{f(y0)}Z" fill="{INK}" opacity=".6"/>')
    return ""


MESS = ("drip", "ring", "crack", "tape", "burn", "drip", "ring", "crack")


def project_card(p, theme, animate=True, order=0):
    """A steel drawer front in the lab's specimen cabinet. A paper index label slides out of its
    slot between two brass rails: a colour strip down its edge (one per project), the name and
    where the code lives, one line about it and the stack as paper chips. A pilot lamp on the
    drawer front lights when the label lands."""
    xed = theme == "dark"
    W, H = 376, 104
    uid = f"pc{re.sub('[^a-z]', '', p['name'].lower())}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    accent = ACCENTS[order % len(ACCENTS)]
    s = []
    front = rpoly([(4, 6), (W - 8, 6), (W - 8, H - 8), (4, H - 8)], 7)
    s.append(f'<path d="{front}" fill="{INK}" transform="translate(4 4)"/>')
    s.append(inked(front, "#4B5370" if not xed else "#1E2438", 3, extra=(
        f'<path d="M4,10 H{W - 8}" stroke="#7C86A0" stroke-width="2.2" opacity=".8"/>'
        f'<rect x="4" y="{H - 22}" width="{W}" height="20" fill="{INK}" opacity=".14"/>')))
    lx, ly, lw, lh = 14, 13, W - 56, H - 27
    # the slot and its two brass rails
    s.append(f'<rect x="{lx - 2}" y="{ly - 2}" width="{lw + 4}" height="{lh + 4}" rx="2" fill="#141826"/>')
    rails = (f'<rect x="{lx - 4}" y="{ly - 5}" width="{lw + 8}" height="5" rx="2" fill="{C["gold"]}" stroke="{INK}" stroke-width="1.8"/>'
             f'<rect x="{lx - 4}" y="{ly + lh}" width="{lw + 8}" height="5" rx="2" fill="{C["gold_sh"]}" stroke="{INK}" stroke-width="1.8"/>'
             + bolt(lx - 1, ly - 2.5, 1.6) + bolt(lx + lw + 1, ly - 2.5, 1.6) + bolt(lx - 1, ly + lh + 2.5, 1.6) + bolt(lx + lw + 1, ly + lh + 2.5, 1.6))
    lab = [f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="{C["bone"]}"/>',
           f'<rect x="{lx}" y="{ly}" width="7" height="{lh}" fill="{accent}"/>',
           f'<path d="M{lx + 7},{ly} V{ly + lh}" stroke="{INK}" stroke-width="1.4"/>',
           f'<path d="M{lx + lw * .74},{ly} l-12,{lh}" stroke="#FFFFFF" stroke-width="6" opacity=".28"/>']
    tx = lx + 16
    lab.append(ts.text(p["name"], "body-bold", 17, tx, ly + 20, INK)[0])
    wtxt = p["where"].upper()
    ww = text_width(wtxt, "body-bold", 8.2, 1) + 18
    wx = lx + lw - 8 - ww
    lit = p["where"] != "private"
    lab.append(f'<rect x="{f(wx)}" y="{ly + 7}" width="{f(ww)}" height="14" rx="2" fill="#2A2F44" stroke="{INK}" stroke-width="1.4"/>'
               f'<circle cx="{f(wx + 7.5)}" cy="{ly + 14}" r="2.6" fill="{C["spill"] if lit else "#FF4A3A"}" stroke="{INK}" stroke-width="1"/>'
               + ts.text(wtxt, "body-bold", 8.2, wx + 14, ly + 17, C["bone"], tracking=1)[0])
    lab.append(ts.text(p["line"], "body", 11.4, tx, ly + 34, "#2A2F44")[0])
    lab.append(tags(ts, STACKS[p["name"]], tx, ly + 41, lx + lw - 8, xed))
    if xed:
        lab.append(xed_mess(MESS[order % len(MESS)], W, H, lx, ly, lw, lh, order + 40) if MESS[order % len(MESS)] in ("ring", "tape", "burn") else "")
    label = "".join(lab)
    slot = rpoly([(lx, ly), (lx + lw, ly), (lx + lw, ly + lh), (lx, ly + lh)], 1)
    begin = .3 + order * .12
    if animate:  # slides out of the drawer in snapped frames, overshoots, settles
        slide = (f'<animateTransform attributeName="transform" type="translate" values="-360 0;-360 0;-230 0;-90 0;10 0;0 0" '
                 f'keyTimes="0;{begin / (begin + .4):.3f};{(begin + .1) / (begin + .4):.3f};{(begin + .2) / (begin + .4):.3f};{(begin + .3) / (begin + .4):.3f};1" '
                 f'calcMode="discrete" dur="{begin + .4:.2f}s" fill="freeze"/>')
        s.append(clipped(f"sl{uid}", slot, f'<g>{slide}{label}</g>'))
    else:
        s.append(clipped(f"sl{uid}", slot, label))
    s.append(f'<path d="{slot}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    s.append(rails)
    lamp_col = C["spill"] if p["where"] != "private" else "#FF4A3A"
    s.append(drawer_lamp(W - 25, H / 2 - 9, lamp_col, animate, begin + .45))
    s.append(f'<rect x="{W - 31}" y="{H / 2 + 5}" width="12" height="22" rx="3" fill="{STEEL_LT}" stroke="{INK}" stroke-width="2"/>')
    if xed and MESS[order % len(MESS)] in ("drip", "crack"):
        s.append(xed_mess(MESS[order % len(MESS)], W, H, lx, ly, lw, lh, order + 40))
    s.append(tooth(W, H))
    label_txt = f'{p["name"]}, {p["where"]} repository: {p["line"]} Built with {", ".join(STACKS[p["name"]])}.'
    return doc(W, H, "".join(s), ts, label_txt)


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
    """A round-shouldered reagent jar standing on the plank (foot pressed 2 px in): glass body
    with the liquid clipped inside it, a neck and a coloured cap, and a paper label carrying
    the tool's logo (its name goes in the alt text)."""
    from icons import ICONS
    from notebook import mark
    w, h = 34, 40
    x, y = cx - w / 2, base - h + 2
    caps = (C["crimson"], C["gold"], C["phoenix"], C["prussian"])
    liq = (C["spill"], C["phoenix"], "#8FD3FF", C["gold"])[k % 4]
    body = rpoly([(x, y + 9), (x + w, y + 9), (x + w, y + h), (x, y + h)], [10, 10, 5, 5])
    neck = rpoly([(cx - 7, y + 2), (cx + 7, y + 2), (cx + 7, y + 11), (cx - 7, y + 11)], 2)
    cap = rpoly([(cx - 9, y - 4), (cx + 9, y - 4), (cx + 9, y + 4), (cx - 9, y + 4)], 3)
    inside = (f'<rect x="{f(x - 4)}" y="{f(y + h * .5)}" width="{w + 8}" height="{h}" fill="{liq}"/>'
              f'<path d="M{f(x - 4)},{f(y + h * .5)} H{f(x + w + 4)}" stroke="#FFFFFF" stroke-width="1.4" opacity=".6"/>')
    out = [inked([body, neck], "#D8EEF2", 2.4, extra=clipped(f"jr{uid}", body, inside)),
           inked(cap, caps[k % 4], 2.2),
           f'<rect x="{f(x + 5)}" y="{f(y + 15)}" width="{w - 10}" height="21" rx="2" fill="{C["bone"]}" stroke="{INK}" stroke-width="1.6"/>']
    if name.lower() in ICONS:
        out.append(mark(name, cx - 8, y + 17.5, 16, INK))
    out.append(fold([(x + 3.5, y + 14), (x + 3, y + 32)], 2.2, "#FFFFFF"))
    return "".join(out)


def cabinet(theme, layout="wide", animate=True):
    xed = theme == "dark"
    wide = layout == "wide"
    W = 760 if wide else 400
    per = 14 if wide else 8
    rows = []
    for g, names in SHELF:
        n_rows = -(-len(names) // per)
        size = -(-len(names) // n_rows)   # split evenly: 12 -> 6 + 6, 9 -> 5 + 4
        for i in range(0, len(names), size):
            rows.append((g if i == 0 else "", names[i:i + size]))
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
        pitch = 50 if wide else 44
        row_w = sum(len(n) * pitch for _, n in groups) + 36 * (len(groups) - 1)
        x = (W - row_w) / 2
        for gi, (g, names) in enumerate(groups):
            span = len(names) * pitch
            if gi:
                x += 36
            s.append(shelf(x - 6, x + span + 6, base, f"{uid}{r}{gi}", xed, brackets=(x + 18, x + span - 18), depth=11))
            for j, n in enumerate(names):
                s.append(jar(x + pitch / 2 + j * pitch, base + 1, n, k, xed, f"{uid}{k}"))
                labels.append(n)
                k += 1
            if g:
                gw = text_width(g.upper(), "body-bold", 8.6, 1) + 14
                s.append(f'<rect x="{x}" y="{base + 14}" width="{f(gw)}" height="13" rx="2" fill="{C["bone"]}" stroke="{INK}" stroke-width="1.4"/>'
                         + ts.text(g.upper(), "body-bold", 8.6, x + 7, base + 23.6, INK, tracking=1)[0])
            x += span
    if xed:
        s.append(kid.splat(W - 20, 16, 9, 91, drips=2, run=3))
        s.append(scorch(W - 30, H - 24, 16, 5))
    s.append(tooth(W, H))
    return doc(W, H, "".join(s), ts, "Stack: " + ", ".join(labels) + ".")


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
