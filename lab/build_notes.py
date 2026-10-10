#!/usr/bin/env python3
"""Typeset the lab-note equations as SVG: assets/eq-*-{dark,light}.svg.

GitHub's own LaTeX renderer is unreliable on profile pages, so the equations
are drawn here as vector paths and shipped as plain images.

    python lab/build_notes.py
"""
import io
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from notebook import ROOT  # noqa: E402

plt.rcParams.update({"mathtext.fontset": "stix", "svg.fonttype": "path"})

EQUATIONS = {
    "gray-scott-u": r"$\dfrac{\partial u}{\partial t} = D_u\,\nabla^2 u \;-\; u v^2 \;+\; F\,(1 - u)$",
    "gray-scott-v": r"$\dfrac{\partial v}{\partial t} = D_v\,\nabla^2 v \;+\; u v^2 \;-\; (F + k)\,v$",
    "needleman-wunsch": r"$F(i,j) = \max\,\{\; F(i-1,\,j-1) + s(a_i, b_j),\;\; F(i-1,\,j) + d,\;\; F(i,\,j-1) + d \;\}$",
}
from notebook import THEMES  # noqa: E402
INK = {theme: THEMES[theme]["ink"] for theme in THEMES}


def typeset(tex, colour, size=22):
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, tex, fontsize=size, color=colour)
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    svg = buf.getvalue()
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)   # drop generator noise
    return svg


if __name__ == "__main__":
    for name, tex in EQUATIONS.items():
        for theme, colour in INK.items():
            out = ROOT / "assets" / f"eq-{name}-{theme}.svg"
            out.write_text(typeset(tex, colour), encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)}")
