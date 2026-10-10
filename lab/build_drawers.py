#!/usr/bin/env python3
"""Draw the specimen cabinet: assets/drawers/front-N-{theme}.svg and tray-N-{theme}.svg.

Each drawer front is the <summary> of a <details> block in the README, so
clicking it pulls the drawer open and shows the tray. The cards are typed,
the binomials are written in by hand, and the trays hold a small live drawing
of each project.

    python lab/build_drawers.py
"""
import math

from notebook import ASSETS, THEMES, svg_doc, svg_text

OUT = ASSETS / "drawers"

SPECIMENS = [
    ("L-001", "Helix threejsensis", "JAVASCRIPT · THREE.JS", "protein structure viewer"),
    ("L-002", "Arbor alignans", "TYPESCRIPT", "phylogenetic tree builder"),
    ("L-003", "Turingia lissajousii", "REACT · VITE · TAILWIND", "generative art playground"),
    ("L-004", "Solaris turrifera", "GODOT 4.6 · C++", "orbital tower defense"),
]
BRASS = {"dark": ("#c9a46a", "#8a6a3a"), "light": ("#b8935a", "#7d6034")}


# ------------------------------------------------------------------ fronts

def front(n, code, binomial, habitat, common, theme):
    t = THEMES[theme]
    b1, b2 = BRASS[theme]
    W, H = 840, 92
    hx = 690
    body = f'''<defs>
  <linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['panel2']}"/><stop offset="1" stop-color="{t['panel']}"/></linearGradient>
  <linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{b1}"/><stop offset="1" stop-color="{b2}"/></linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="6" fill="url(#f)" stroke="{t['edge']}" stroke-width="1.5"/>
<rect x="9" y="9" width="{W - 18}" height="{H - 18}" rx="3" fill="none" stroke="{t['edge']}" stroke-width="1" opacity="0.7"/>
<rect x="26" y="16" width="480" height="60" rx="3" fill="url(#b)"/>
<rect x="31" y="21" width="470" height="50" rx="1.5" fill="{t['paper']}"/>
<line x1="40" y1="44" x2="492" y2="44" stroke="{t['paper_ink']}" stroke-width="0.6" opacity="0.25"/>
{''.join(f'<circle cx="{x}" cy="{y}" r="1.7" fill="{b2}"/>' for x in (29, 503) for y in (19, 73))}
{svg_text(f"{code}  {habitat}", "type-bold", 12.5, 42, 38, t['paper_ink'], jitter=0.45, opacity=0.85)}
{svg_text(binomial, "hand", 23, 44, 66, "#1d3f8f")}
{svg_text(common, "type", 11.5, 492, 64, t['paper_ink'], anchor="end", opacity=0.6, jitter=0.4)}
<path d="M{hx - 58},50 q0,-16 16,-16 h84 q16,0 16,16" fill="none" stroke="url(#b)" stroke-width="6.5" stroke-linecap="round"/>
<rect x="{hx - 67}" y="45" width="18" height="11" rx="2" fill="url(#b)"/>
<rect x="{hx + 49}" y="45" width="18" height="11" rx="2" fill="url(#b)"/>
{svg_text(f"{n:02d}", "wordmark", 22, W - 30, 55, t['red'], anchor="end")}'''
    return svg_doc(W, H, body, f"Drawer {code}: {binomial}, {common}. Click to open.")


# ------------------------------------------------------------------ trays

NOTES = [
    ["A lightweight, portfolio-grade 3D protein", "structure viewer, built with raw Three.js.", "No framework between it and the GPU."],
    ["Feed it DNA or protein sequences. It aligns", "them pairwise, builds the tree, and replays", "the algorithm step by step."],
    ["A generative art playground run on math:", "Lissajous curves, L-systems and Gray-Scott", "reaction-diffusion, all in the browser."],
    ["Orbital tower defense in Godot 4.6. Rotating", "towers defend the Sun: campaign, endless,", "a No-Flare Challenge and a Tech XP tree."],
]


def tray(theme, inner, caption, n):
    """The drawer pulled out: a felt-lined box that slides out when shown."""
    from notebook import Typesetter
    t = THEMES[theme]
    ts = Typesetter(f"t{n}")
    b1, b2 = BRASS[theme]
    W, H = 840, 250
    code, binomial, habitat, common = SPECIMENS[n - 1]
    notes = []
    clock = 0.75
    for k, line in enumerate(NOTES[n - 1]):
        g, clock = ts.text(line, "text", 15, 340, 92 + k * 24, t["ink"], reveal=(clock, 0.012))
        notes.append(g)
    head, _ = ts.text(f"FIELD NOTES · {code}", "label", 12, 340, 60, t["red"], tracking=1.8)
    name, _ = ts.text(binomial, "hand", 26, 340, 196, t["pen"])
    body = f'''<g opacity="0">
  <set attributeName="opacity" to="1" begin="0s" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" values="0 -70;0 6;0 0" keyTimes="0;0.8;1" dur="0.7s" fill="freeze"/>
  <path d="M6,8 H{W - 6} L{W - 22},{H - 6} H22 Z" fill="{t['panel2']}" stroke="{t['edge']}" stroke-width="1.5"/>
  <path d="M22,22 H{W - 22} L{W - 34},{H - 18} H34 Z" fill="{t['panel']}"/>
  <g transform="translate(26 30)">{inner}{svg_text(caption, "hand", 17, 140, 186, t['pen'], anchor="middle")}</g>
  <line x1="318" y1="40" x2="318" y2="{H - 30}" stroke="{t['edge']}" stroke-width="1" stroke-dasharray="3 5"/>
  {head}{"".join(notes)}{name}
  <rect x="{W - 120}" y="{H - 52}" width="76" height="22" rx="3" fill="{t['paper']}" transform="rotate(-4 {W - 82} {H - 41})"/>
  {svg_text(f"{code} · OPEN", "label", 10, W - 82, H - 37, t['paper_ink'], anchor="middle")}
</g>'''
    return svg_doc(W, H, ts.defs_svg() + body, f"Drawer {code} pulled open: {binomial}, {common}. " + " ".join(NOTES[n - 1]))


def pin(x, y, t):
    return (f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 16}" stroke="{t["muted"]}" stroke-width="1.2"/>'
            f'<circle cx="{x}" cy="{y}" r="3.4" fill="{t["red"]}"/>')


def tray_protein(theme):
    t = THEMES[theme]
    front_runs, back_runs, cur, side = [], [], [], None
    for i in range(361):
        u = i / 360
        ang = u * 2 * math.pi * 4.2
        p = (40 + 200 * u, 92 + 36 * math.sin(ang))
        s = math.cos(ang) > 0
        if side is not None and s != side:
            (front_runs if side else back_runs).append(cur)
            cur = [cur[-1]]
        cur.append(p)
        side = s
    (front_runs if side else back_runs).append(cur)

    def poly(run, colour, w, op=1):
        return (f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in run)}" fill="none" '
                f'stroke="{colour}" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>')
    g = "".join(poly(r, t["blue"], 7, 0.35) for r in back_runs) + "".join(poly(r, t["glow"], 9) for r in front_runs)
    return (f'<g>{g}<animateTransform attributeName="transform" type="translate" values="0,0;0,-3;0,0" '
            f'dur="4s" repeatCount="indefinite"/></g>{pin(140, 24, t)}')


def tray_tree(theme):
    t = THEMES[theme]
    ys = [40, 58, 78, 102, 124]
    a, b = (ys[0] + ys[1]) / 2, (ys[3] + ys[4]) / 2
    root = (a + b) / 2
    paths = (f"M58,{ys[0]} V{ys[1]} M58,{ys[0]} H100 M58,{ys[1]} H100 "
             f"M38,{a} H58 M38,{a} V{ys[2]} M38,{ys[2]} H100 "
             f"M72,{ys[3]} V{ys[4]} M72,{ys[3]} H100 M72,{ys[4]} H100 "
             f"M38,{(a + ys[2]) / 2} H30 M30,{(a + ys[2]) / 2} V{b} M30,{b} H72 M22,{root} H30")
    cols = {"A": t["green"], "C": t["blue"], "G": t["amber"], "T": t["red"]}
    seqs = ["ACGTTGCA", "ACGATGCA", "ACCTTGGA", "TCGTAGCA", "TCGTAGCT"]
    cells = "".join(f'<rect x="{110 + c * 17}" y="{y - 7}" width="15" height="14" rx="2" fill="{cols[ch]}" opacity="0.85"/>'
                    for y, s in zip(ys, seqs) for c, ch in enumerate(s))
    sweep = (f'<rect x="108" y="26" width="19" height="112" rx="3" fill="none" stroke="{t["ink"]}" stroke-width="1.5">'
             f'<animate attributeName="x" values="108;227;108" dur="6s" repeatCount="indefinite"/></rect>')
    return f'<path d="{paths}" fill="none" stroke="{t["ink"]}" stroke-width="1.7"/>{cells}{sweep}{pin(140, 14, t)}'


def tray_lissajous(theme):
    t = THEMES[theme]
    pts = [(140 + 84 * math.sin(3 * s + math.pi / 2), 86 - 52 * math.sin(2 * s))
           for s in (2 * math.pi * i / 400 for i in range(401))]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    L = sum(math.dist(pts[i], pts[i + 1]) for i in range(400))
    return (f'<path d="{d}" fill="none" stroke="{t["muted"]}" stroke-width="1" opacity="0.4"/>'
            f'<path d="{d}" fill="none" stroke="{t["glow"]}" stroke-width="2.6" stroke-linecap="round" '
            f'stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}">'
            f'<animate attributeName="stroke-dashoffset" values="{L:.0f};0;0;{-L:.0f}" keyTimes="0;0.6;0.75;1" '
            f'dur="7s" repeatCount="indefinite"/></path>{pin(140, 14, t)}')


def tray_orbit(theme):
    t = THEMES[theme]
    cx, cy = 140, 86
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["muted"]}" stroke-width="1" '
                    f'stroke-dasharray="3 4" opacity="0.6"/>' for r in (40, 62))
    sun = (f'<circle cx="{cx}" cy="{cy}" r="17" fill="{t["amber"]}"/>'
           f'<circle cx="{cx}" cy="{cy}" r="24" fill="none" stroke="{t["amber"]}" stroke-width="2" opacity="0.35">'
           f'<animate attributeName="r" values="22;27;22" dur="3s" repeatCount="indefinite"/></circle>')

    def tower(angle, r):
        x, y = cx + r * math.cos(math.radians(angle)), cy + r * math.sin(math.radians(angle))
        return (f'<rect x="{x - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" rx="2" fill="{t["blue"]}" '
                f'transform="rotate({angle + 45:.0f} {x:.1f} {y:.1f})"/>')
    spin = '<animateTransform attributeName="transform" type="rotate" from="{a} {cx} {cy}" to="{b} {cx} {cy}" dur="{d}s" repeatCount="indefinite"/>'
    inner = f'<g>{tower(0, 40)}{tower(120, 40)}{tower(240, 40)}{spin.format(a=0, b=360, cx=cx, cy=cy, d=14)}</g>'
    outer = f'<g>{tower(60, 62)}{tower(200, 62)}{spin.format(a=360, b=0, cx=cx, cy=cy, d=22)}</g>'
    return rings + sun + inner + outer


TRAYS = [(tray_protein, "an α-helix, 3.6 residues a turn"),
         (tray_tree, "five taxa, eight columns aligned"),
         (tray_lissajous, "x = sin(3t + π/2), y = sin(2t)"),
         (tray_orbit, "towers in orbit around the Sun")]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for n, ((code, binomial, habitat, common), (draw, caption)) in enumerate(zip(SPECIMENS, TRAYS), start=1):
            (OUT / f"front-{n}-{theme}.svg").write_text(front(n, code, binomial, habitat, common, theme), encoding="utf-8")
            (OUT / f"tray-{n}-{theme}.svg").write_text(tray(theme, draw(theme), caption, n), encoding="utf-8")
    print(f"wrote {len(list(OUT.glob('*.svg')))} drawer drawings to {OUT.relative_to(ASSETS.parent)}")
