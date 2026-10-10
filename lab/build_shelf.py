#!/usr/bin/env python3
"""Materials & methods: the stack as a reagent shelf. assets/shelf-{dark,light}.svg

Every bottle is something actually used in a repository on this profile, and
its label says where. Liquid bubbles; the hazard bottle at the end blinks.
Add your security tools to SHELF when you want them on the shelf.

    python lab/build_shelf.py
"""
import random

from notebook import ASSETS, THEMES, Typesetter, svg_doc

# (name, used in, liquid colour, vessel)
SHELF = [
    ("JavaScript", "L-001 · L-003", "#f1e05a", "bottle"),
    ("TypeScript", "L-002", "#3178c6", "bottle"),
    ("C++", "L-004", "#f34b7d", "flask"),
    ("React", "L-003", "#61dafb", "vial"),
    ("Vite", "L-003", "#bd34fe", "vial"),
    ("Tailwind", "L-003", "#38bdf8", "vial"),
    ("Three.js", "L-001", "#e6edf3", "flask"),
    ("Godot 4.6", "L-004", "#478cbf", "bottle"),
    ("picoCTF", "the night shift", "#ff1f3d", "hazard"),
    # add tools you use, e.g. ("Ghidra", "REV", "#d42f2f", "vial"), ("Wireshark", "net", "#1679a7", "vial"),
]


def vessel(kind, x, base, liquid, t, rng, i):
    """Return (glass path, liquid clip path, top of liquid y) for a vessel standing on `base`."""
    if kind == "flask":
        w, h, neck = 56, 92, 16
        glass = (f"M{x - neck / 2},{base - h} v28 L{x - w / 2},{base - 8} q0,8 8,8 h{w - 16} q8,0 8,-8 "
                 f"L{x + neck / 2},{base - h + 28} v-28 Z")
        level = base - 40
    elif kind == "vial":
        w, h = 30, 84
        glass = f"M{x - w / 2},{base - h} h{w} v{h - 10} q0,10 -10,10 h{-(w - 20)} q-10,0 -10,-10 Z"
        level = base - 52
    else:  # bottle or hazard
        w, h, neck = 52, 96, 22
        glass = (f"M{x - neck / 2},{base - h} h{neck} v14 q{(w - neck) / 2},6 {(w - neck) / 2},20 V{base - 6} "
                 f"q0,6 -6,6 h{-(w - 12)} q-6,0 -6,-6 V{base - h + 34} q0,-14 {(w - neck) / 2},-20 Z")
        level = base - 58
    return glass, level, w


def shelf(theme):
    t = THEMES[theme]
    ts = Typesetter("sv")
    rng = random.Random(9)
    W, H = 840, 236
    base = 160
    from notebook import ambient
    amb_d, amb_b = ambient("sa", W, H, theme, seed=2, cells=7, bits=10)
    body = [f'<defs>{amb_d}</defs>', amb_b,
            f'<rect x="16" y="{base}" width="{W - 32}" height="9" rx="2" fill="{t["edge"]}"/>',
            f'<rect x="28" y="{base + 9}" width="10" height="40" fill="{t["edge"]}" opacity="0.6"/>',
            f'<rect x="{W - 38}" y="{base + 9}" width="10" height="40" fill="{t["edge"]}" opacity="0.6"/>']
    step = (W - 60) / len(SHELF)
    clips = []
    for i, (name, used, colour, kind) in enumerate(SHELF):
        x = 30 + step * (i + 0.5)
        glass, level, w = vessel(kind, x, base, colour, t, rng, i)
        clips.append(f'<clipPath id="v{i}"><path d="{glass}"/></clipPath>')
        bubbles = []
        for b in range(4):
            bx = x + rng.uniform(-w / 4, w / 4)
            dur = rng.uniform(2.2, 3.8)
            beg = rng.uniform(0, 3)
            bubbles.append(f'<circle cx="{bx:.1f}" cy="{base - 6}" r="{rng.uniform(1.5, 3):.1f}" fill="#fff" opacity="0.55">'
                           f'<animate attributeName="cy" values="{base - 6};{level + 2}" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/>'
                           f'<animate attributeName="opacity" values="0;0.6;0" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/></circle>')
        # the shelf gets bumped: a wave of agitation runs bottle to bottle, and each liquid sloshes after it
        period, hit = 9.0, 0.6 + 0.32 * i
        slosh_vals = "0;-14;11;-8;5;-2;0;0"
        slosh_kt = "0;0.04;0.09;0.15;0.22;0.3;0.4;1"
        surf = (f'<g><animateTransform attributeName="transform" type="rotate" values="{";".join(f"{a} {x:.1f} {level:.1f}" for a in slosh_vals.split(";"))}" '
                f'keyTimes="{slosh_kt}" dur="{period}s" begin="{hit:.2f}s" repeatCount="indefinite"/>'
                f'<path d="M{x - 60},{level} q10,-5 20,0 t20,0 t20,0 t20,0 t20,0 t20,0 V{base + 30} H{x - 60} Z" fill="{colour}" opacity="0.88">'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;-20 0;0 0" dur="{rng.uniform(2.4, 3.6):.1f}s" repeatCount="indefinite"/></path>'
                f'<path d="M{x - 60},{level + 3} q10,-3 20,0 t20,0 t20,0 t20,0 t20,0 t20,0" fill="none" stroke="#fff" stroke-opacity="0.35" stroke-width="1.5">'
                f'<animateTransform attributeName="transform" type="translate" values="-20 0;0 0;-20 0" dur="{rng.uniform(2.0, 3.0):.1f}s" repeatCount="indefinite"/></path></g>')
        body.append(f'<g><animateTransform attributeName="transform" type="rotate" '
                    f'values="0 {x:.1f} {base};-5 {x:.1f} {base};4 {x:.1f} {base};-2 {x:.1f} {base};0 {x:.1f} {base};0 {x:.1f} {base}" '
                    f'keyTimes="0;0.03;0.07;0.11;0.16;1" dur="{period}s" begin="{hit - 0.05:.2f}s" repeatCount="indefinite"/>')
        body.append(f'<g clip-path="url(#v{i})">{surf}{"".join(bubbles)}</g>')
        body.append(f'<path d="{glass}" fill="{t["ink"]}" fill-opacity="0.05" stroke="{t["ink"]}" stroke-opacity="0.75" stroke-width="1.6"/>')
        body.append(f'<path d="M{x - w / 2 + 7},{base - 40} v-26" stroke="#fff" stroke-opacity="0.35" stroke-width="3" stroke-linecap="round"/>')
        # paper label on the glass
        lw = max(44, min(w + 18, 84))
        body.append(f'<g transform="rotate({rng.uniform(-3, 3):.1f} {x} {base - 22})">'
                    f'<rect x="{x - lw / 2:.1f}" y="{base - 34}" width="{lw:.1f}" height="22" rx="2" fill="{t["paper"]}"/>'
                    + ts.text(name if len(name) < 11 else name[:10], "label", 9.5 if len(name) > 7 else 10.5, x, base - 19,
                              t["paper_ink"], anchor="middle")[0] + '</g>')
        if kind == "hazard":
            body.append(f'<path d="M{x},{base - 70} l9,15 h-18 Z" fill="{t["red"]}" stroke="{t["paper"]}" stroke-width="1.2">'
                        f'<animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite"/></path>')
        body.append("</g>")
        g, _ = ts.text(used, "text", 11, x, base + 30, t["muted"], anchor="middle")
        body.append(g)
    g, _ = ts.text("every bottle is in a repo above. handle with care", "hand", 20, W - 28, H - 18, t["pen"], anchor="end")
    body.append(g)
    return svg_doc(W, H, "<defs>" + "".join(clips) + "</defs>" + ts.defs_svg() + "\n".join(body),
                   "Reagent shelf: " + ", ".join(f"{n} ({u})" for n, u, _, _ in SHELF))


if __name__ == "__main__":
    for theme in THEMES:
        (ASSETS / f"shelf-{theme}.svg").write_text(shelf(theme), encoding="utf-8")
    print("wrote assets/shelf-{dark,light}.svg")
