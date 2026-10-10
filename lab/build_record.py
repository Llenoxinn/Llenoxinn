#!/usr/bin/env python3
"""Specimen 000's intake form: assets/record-{dark,light}.svg

A specimen intake card that types itself out field by field, then gets a red
CONTAINED stamp slammed onto it. Edit FIELDS to change what it says.

    python lab/build_record.py
"""
from notebook import ASSETS, THEMES, Typesetter, svg_doc, text_width

FIELDS = [
    ("BINOMIAL", "Homo sapiens var. llenoxinnensis"),
    ("COMMON NAME", "Dexter Juevesano (he/him)"),
    ("LIFE STAGE", "sophomore, computer science"),
    ("HABITAT", "bioinformatics · cybersecurity · AI/ML · network engineering"),
    ("RANGE", "Cebu City, Philippines"),
    ("BEHAVIOUR", "builds the weird stuff nobody built yet; captures flags at night"),
    ("HANDLING", "docile. responds to dsjuevesano@up.edu.ph"),
]


def card(theme):
    t = THEMES[theme]
    ts = Typesetter("r")
    W, H = 840, 356
    x0, y0, w, h = 20, 18, 800, 320
    paper, ink = t["paper"], t["paper_ink"]
    body = [f'<rect x="{x0 + 4}" y="{y0 + 5}" width="{w}" height="{h}" rx="4" fill="#000" opacity="0.25"/>',
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4" fill="{paper}"/>',
            f'<rect x="{x0}" y="{y0}" width="{w}" height="44" rx="4" fill="{t["red"]}"/>',
            f'<rect x="{x0}" y="{y0 + 30}" width="{w}" height="14" fill="{t["red"]}"/>']
    g, e = ts.text("SPECIMEN INTAKE · FORM 000", "label", 15, x0 + 22, y0 + 28, "#fff", tracking=2.2)
    body.append(g)
    g, _ = ts.text("ACCESSION LLX-0000-26", "mono-bold", 13, x0 + w - 22, y0 + 28, "#fff", anchor="end")
    body.append(g)
    y = y0 + 80
    clock = 0.4
    for label, value in FIELDS:
        g, _ = ts.text(label, "label", 11.5, x0 + 22, y, ink, tracking=1.4, opacity=0.6)
        body.append(g)
        body.append(f'<line x1="{x0 + 160}" y1="{y + 5}" x2="{x0 + w - 22}" y2="{y + 5}" stroke="{ink}" stroke-width="0.6" opacity="0.25"/>')
        face = "hand" if label == "BINOMIAL" else "text"
        size = 22 if face == "hand" else 15
        fill = "#1d3f8f" if face == "hand" else ink
        g, clock = ts.text(value, face, size, x0 + 164, y + (1 if face == "hand" else 0), fill,
                           reveal=(clock, 0.028 if face == "hand" else 0.014))
        body.append(g)
        clock += 0.12
        y += 31
    # the stamp
    sx, sy = x0 + w - 150, y0 + h - 36
    stamp = ts.text("CONTAINED", "tape", 40, 0, 14, t["red"], anchor="middle", tracking=4)[0]
    sw = text_width("CONTAINED", "tape", 40, 4) + 36
    body.append(f'''<defs><filter id="ink" x="-10%" y="-20%" width="120%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.8" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in"/></filter></defs>
<g transform="translate({sx} {sy}) rotate(-12)" opacity="0">
  <set attributeName="opacity" to="0.9" begin="{clock + 0.3:.2f}s" fill="freeze"/>
  <animateTransform attributeName="transform" type="scale" values="2.4;0.92;1" keyTimes="0;0.7;1" additive="sum" begin="{clock + 0.3:.2f}s" dur="0.28s" fill="freeze"/>
  <g filter="url(#ink)">
    <rect x="{-sw / 2:.1f}" y="-26" width="{sw:.1f}" height="54" rx="6" fill="none" stroke="{t['red']}" stroke-width="4"/>
    <rect x="{-sw / 2 + 6:.1f}" y="-20" width="{sw - 12:.1f}" height="42" rx="3" fill="none" stroke="{t['red']}" stroke-width="1.5"/>
    {stamp}
  </g>
</g>''')
    g, _ = ts.text("checked in by the night shift", "hand", 18, x0 + 22, y0 + h - 14, t["pen"] if theme == "light" else "#c1121f")
    body.append(f'<g opacity="0">{g}<set attributeName="opacity" to="1" begin="{clock + 0.8:.2f}s" fill="freeze"/></g>')
    return svg_doc(W, H, ts.defs_svg() + "\n".join(body),
                   "Specimen intake form: " + "; ".join(f"{a.title()}: {b}" for a, b in FIELDS))


if __name__ == "__main__":
    for theme in THEMES:
        (ASSETS / f"record-{theme}.svg").write_text(card(theme), encoding="utf-8")
    print("wrote assets/record-{dark,light}.svg")
