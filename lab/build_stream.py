#!/usr/bin/env python3
"""The bloodstream between sections: assets/stream-N-{theme}.svg

Red cells and data packets flow down a vessel with no edges. Every cycle a
malicious packet slips in, and an immune cell (the IDS) engulfs it.

    python lab/build_stream.py
"""
import math
import random

from notebook import ASSETS, THEMES, Typesetter, ambient, svg_doc, text_width

W, H = 840, 96
VARIANTS = [  # (threat label, direction, seed)
    ("0xDEADBEEF", 1, 1),
    ("' OR 1=1 --", -1, 2),
    ("<script>", 1, 3),
    ("rm -rf /", -1, 4),
]


def lane(y, amp, phase, direction):
    xs = range(-60, W + 61, 30)
    pts = [(x, y + amp * math.sin(x / 70 + phase)) for x in xs]
    if direction < 0:
        pts = pts[::-1]
    return "M" + " L".join(f"{x:.0f},{y:.1f}" for x, y in pts)


def rbc(colour, dark):
    return (f'<ellipse rx="9" ry="6" fill="{colour}"/><ellipse rx="4.5" ry="2.6" fill="{dark}" opacity="0.55"/>')


def stream(theme, threat, direction, seed):
    t = THEMES[theme]
    rng = random.Random(seed)
    ts = Typesetter(f"s{seed}")
    uid = f"st{seed}"
    red, ink, muted = t["red"], t["ink"], t["muted"]
    dark_red = t["red_dim"] if theme == "dark" else "#8b0018"
    adefs, abody = ambient(f"{uid}a", W, H, theme, seed=seed, cells=3, bits=6, fade=120, opacity=0.8)
    body = [f'<defs>{adefs}'
            f'<linearGradient id="{uid}fx" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset="0.14" stop-color="#fff"/>'
            f'<stop offset="0.86" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
            f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#{uid}fx)"/></mask>'
            f'<filter id="{uid}g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>', abody,
            f'<g mask="url(#{uid}m)">']
    # vessel walls
    for y, ph in ((12, 0.0), (H - 12, 1.7)):
        body.append(f'<path d="{lane(y, 3, ph, 1)}" fill="none" stroke="{red}" stroke-opacity="0.35" stroke-width="1.4" stroke-dasharray="2 5"/>')
    lanes = [lane(30 + 18 * k, 5, rng.uniform(0, 6), direction) for k in range(3)]
    for k, d in enumerate(lanes):
        body.append(f'<path id="{uid}l{k}" d="{d}" fill="none"/>')
    # traffic: red cells and packets
    for i in range(16):
        k = i % 3
        dur = rng.uniform(7, 11)
        begin = -rng.uniform(0, dur)
        if i % 3 == 2:
            label = rng.choice(["4c 6c", "65 6e", "6f 78", "69 6e", "SYN", "ACK", "TLS"])
            wlab = text_width(label, "mono", 8.5) + 12
            g, _ = ts.text(label, "mono", 8.5, -wlab / 2 + 6, 3, ink)
            shape = (f'<rect x="{-wlab / 2:.1f}" y="-7" width="{wlab:.1f}" height="14" rx="3" fill="{t["panel2"]}" stroke="{ink}" stroke-opacity="0.5"/>{g}')
            rot = "0"
        else:
            shape = rbc(red, dark_red)
            rot = "auto"
        body.append(f'<g><animateMotion dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite" rotate="{rot}">'
                    f'<mpath href="#{uid}l{k}" xlink:href="#{uid}l{k}"/></animateMotion>{shape}</g>')
    # the threat and the immune cell
    D = 9.0
    gx = W * (0.68 if direction > 0 else 0.32)
    gy = 48
    start_x = -50 if direction > 0 else W + 50
    spikes = "".join(f'<line x1="0" y1="0" x2="{12 * math.cos(a):.1f}" y2="{12 * math.sin(a):.1f}" stroke="{red}" stroke-width="2" stroke-linecap="round"/>'
                     f'<circle cx="{12 * math.cos(a):.1f}" cy="{12 * math.sin(a):.1f}" r="2" fill="{red}"/>'
                     for a in (k * math.pi / 5 for k in range(10)))
    tlabel, _ = ts.text(threat, "mono-bold", 10, 0, -18, red, anchor="middle")
    body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.05;0.56;0.62;1" dur="{D}s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" values="{start_x} {gy};{gx - 18 * direction:.0f} {gy};{gx:.0f} {gy};{gx:.0f} {gy}" '
                f'keyTimes="0;0.55;0.62;1" dur="{D}s" repeatCount="indefinite"/>'
                f'<g><animateTransform attributeName="transform" type="scale" values="1;1;0.2;0.2" keyTimes="0;0.56;0.64;1" dur="{D}s" repeatCount="indefinite"/>'
                f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="3s" repeatCount="indefinite"/>{spikes}'
                f'<circle r="8" fill="{red}" opacity="0.85"/></g>{tlabel}</g></g>')
    lobes = "".join(f'<circle cx="{5 * math.cos(a):.1f}" cy="{5 * math.sin(a):.1f}" r="4.2" fill="{t["purple"]}" opacity="0.8"/>'
                    for a in (0.3, 2.4, 4.4))
    ids_label, _ = ts.text("IDS", "label", 9.5, 0, 34, muted, anchor="middle", tracking=1.5)
    blocked, _ = ts.text("BLOCKED", "label", 11, 0, -30, red, anchor="middle", tracking=2)
    body.append(f'<g transform="translate({gx:.0f} {gy})">'
                f'<circle r="20" fill="{ink}" fill-opacity="0.12" stroke="{ink}" stroke-opacity="0.7" stroke-width="1.6" filter="url(#{uid}g)">'
                f'<animate attributeName="r" values="20;20;26;17;20;20" keyTimes="0;0.55;0.6;0.66;0.72;1" dur="{D}s" repeatCount="indefinite"/></circle>'
                f'{lobes}{ids_label}'
                f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.6;0.64;0.86;0.9;1" dur="{D}s" repeatCount="indefinite"/>{blocked}</g></g>')
    body.append("</g>")
    return svg_doc(W, H, ts.defs_svg() + "\n".join(body),
                   f"A bloodstream of red cells and data packets; a malicious packet ({threat}) is engulfed by an immune cell labelled IDS")


if __name__ == "__main__":
    for n, (threat, direction, seed) in enumerate(VARIANTS, start=1):
        for theme in THEMES:
            (ASSETS / f"stream-{n}-{theme}.svg").write_text(stream(theme, threat, direction, seed), encoding="utf-8")
    print(f"wrote {len(VARIANTS)} bloodstream strips")
