#!/usr/bin/env python3
"""Punch the section headers on label-maker tape: assets/labels/*.svg.

Embossed white letters on coloured tape, each strip stuck on slightly crooked.
The tape colours read on both GitHub themes, so one file serves both.

    python lab/build_headers.py
"""
import random

from notebook import ASSETS, glyphs, svg_doc, text_width

LABELS = [
    ("accession", "ACCESSION RECORD"),
    ("cabinet", "SPECIMEN CABINET"),
    ("specimen", "SPECIMEN OF THE DAY"),
    ("vitals", "VITAL SIGNS"),
    ("assay", "CTF ASSAY · PICOGYM"),
    ("phylogeny", "PHYLOGENY"),
    ("methods", "MATERIALS & METHODS"),
    ("notes", "LAB NOTES"),
]
TAPES = ["#e0002a", "#c4001f", "#ff1f3d", "#a8001a"]  # red alert: every tape is red
SIZE, TRACK, PAD, TAPE_H = 25, 3.2, 22, 42


def tape(slug, text, colour, seed):
    rng = random.Random(seed)
    tw = text_width(text, "tape", SIZE, TRACK)
    w = tw + 2 * PAD
    W, H = w + 24, TAPE_H + 22
    tilt = rng.uniform(-1.4, 1.4)
    x0, y0 = 12, 11
    # slightly uneven scissor cuts at both ends
    l1, l2, r1, r2 = (rng.uniform(-3, 3) for _ in range(4))
    outline = (f"M{x0 + l1:.1f},{y0} L{x0 + w + r1:.1f},{y0} L{x0 + w + r2:.1f},{y0 + TAPE_H} "
               f"L{x0 + l2:.1f},{y0 + TAPE_H} Z")
    letters = []
    base = y0 + TAPE_H / 2 + SIZE * 0.36
    for _, tf, d in glyphs(text, "tape", SIZE, x0 + PAD, base, tracking=TRACK, jitter=0.7, seed=seed):
        letters.append(f'<path transform="{tf}" d="{d}"/>')
    glyph_g = "".join(letters)
    body = f'''<defs>
  <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.16"/>
    <stop offset="0.45" stop-color="#ffffff" stop-opacity="0.03"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0.18"/>
  </linearGradient>
</defs>
<g transform="rotate({tilt:.2f} {W / 2:.0f} {H / 2:.0f})">
  <path d="{outline}" fill="#000000" opacity="0.18" transform="translate(1.5 2)"/>
  <path d="{outline}" fill="{colour}"/>
  <path d="{outline}" fill="url(#sheen)"/>
  <g fill="#000000" opacity="0.35" transform="translate(0.9 1.1)">{glyph_g}</g>
  <g fill="#f4f1ea">{glyph_g}</g>
</g>'''
    return svg_doc(round(W), H, body, text.title())


if __name__ == "__main__":
    out = ASSETS / "labels"
    out.mkdir(parents=True, exist_ok=True)
    for i, (slug, text) in enumerate(LABELS):
        (out / f"{slug}.svg").write_text(tape(slug, text, TAPES[i % len(TAPES)], i), encoding="utf-8")
    print(f"punched {len(LABELS)} labels into {out.relative_to(ASSETS.parent)}")
