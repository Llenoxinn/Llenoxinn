#!/usr/bin/env python3
"""Draw the animated profile banner: assets/banner-{dark,light}.svg.

The lab is on red alert. On load:
  1. a pen plotter draws the portrait, one signal line per row (amplitude and
     frequency follow the photo), then a biometric scan sweeps it for good;
  2. four of the portrait's lines carry packets into a Sanger chromatogram;
  3. the read is called base by base, grouped into bytes, and decoded in a
     terminal. The read is the handle "Llenoxinn" packed 2 bits per base
     (A=00 C=01 G=10 T=11), so anyone can check it by hand.

    python lab/build_banner.py                       # uses lab/data/portrait.png
    python lab/build_banner.py --source photo.png    # grayscale + alpha (subject mask) works best
"""
import argparse
import math
import random

import numpy as np
from PIL import Image, ImageFilter, ImageOps

import wordmark
from notebook import ASSETS, ROOT, THEMES, Typesetter, svg_doc, text_width

W, H = 1600, 560
HANDLE = "Llenoxinn"
BASES = "ACGT"
PROMPT = "root@specimen-lab:~$ "
COMMAND = "cat read01.seq | decode --2bit | xxd"


def encode(text):
    """Bytes to bases, 2 bits per base, most significant pair first."""
    return "".join(BASES[(b >> s) & 3] for b in text.encode() for s in (6, 4, 2, 0))


def pts_d(pts):
    """Compact path: absolute move, then relative line steps."""
    (x0, y0), out = pts[0], []
    px, py = x0, y0
    for x, y in pts[1:]:
        out.append(f"{x - px:.1f} {y - py:.1f}")
        px, py = x, y
    return f"M{x0:.1f} {y0:.1f}l" + " ".join(out)


def length(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# ------------------------------------------------------------------ portrait

def tone_map(path, box_w, box_h, theme):
    """Ink density 0..1: darkness on paper-white, lit-up brightness on the dark theme."""
    img = ImageOps.exif_transpose(Image.open(path))
    alpha = img.getchannel("A") if "A" in img.getbands() else Image.new("L", img.size, 255)
    g = img.convert("L").resize((box_w, box_h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.1))
    m = np.asarray(alpha.resize((box_w, box_h), Image.LANCZOS), np.float32) / 255
    a = np.asarray(g, np.float32) / 255
    inside = a[m > 0.5]
    lo, hi = np.percentile(inside, 2), np.percentile(inside, 99)
    a = np.clip((a - lo) / max(hi - lo, 1e-3), 0, 1)
    if theme == "light":
        tone = np.clip(1 - a, 0, 1) ** 0.95
    else:
        local = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(box_w / 12)),
                           np.float32) / 255
        flat = np.clip(0.5 + (a - local) * 1.6, 0, 1)
        tone = 0.12 + 0.88 * np.clip(0.55 * flat + 0.45 * a, 0, 1) ** 1.3
    fade = np.clip((box_h - np.arange(box_h)) / (box_h * 0.12), 0, 1)[:, None]   # scan fades at the bottom
    return tone * m * fade, m


def portrait_rows(tone, mask, x0, y0, rows, step=2):
    """Per row: (y, full point list, subject spans as point lists, background spans as (xa, xb))."""
    h, w = tone.shape
    spacing = h / rows
    for r in range(rows):
        yc = (r + 0.5) * spacing
        lo, hi = max(0, int(yc - spacing / 2)), min(h, int(yc + spacing / 2)) + 1
        band, mband = tone[lo:hi].mean(axis=0), mask[lo:hi].mean(axis=0)
        phase, pts, spans, flats, cur, flat_start = 0.0, [], [], [], [], None
        for x in range(0, w, step):
            v = band[x]
            phase += step * 2 * math.pi * (0.05 + 0.32 * v)
            p = (x0 + x, y0 + yc + spacing * 0.92 * v ** 0.8 * math.sin(phase))
            pts.append(p)
            if mband[x] > 0.25:
                cur.append(p)
                if flat_start is not None:
                    flats.append((flat_start, x0 + x))
                    flat_start = None
            else:
                if len(cur) > 1:
                    spans.append(cur)
                cur = []
                flat_start = x0 + x if flat_start is None else flat_start
        if len(cur) > 1:
            spans.append(cur)
        if flat_start is not None:
            flats.append((flat_start, x0 + w))
        yield y0 + yc, pts, spans, flats


# ------------------------------------------------------------------ chromatogram

def chromatogram(read, x0, x1, base_y, height, rng):
    n = len(read)
    step = (x1 - x0) / n
    xs = np.linspace(x0, x1, int(x1 - x0))
    traces = {b: np.full_like(xs, 0.012) for b in BASES}
    for i, base in enumerate(read):
        c = x0 + (i + 0.5) * step
        width = step * rng.uniform(0.20, 0.26)
        for b in BASES:
            hgt = rng.uniform(0.62, 1.0) if b == base else (rng.uniform(0, 0.11) if rng.random() < 0.45 else 0)
            traces[b] += hgt * np.exp(-0.5 * ((xs - c) / width) ** 2)
    return {b: [(x, base_y - v * height) for x, v in zip(xs, t)] for b, t in traces.items()}, step


# ------------------------------------------------------------------ banner

def render(theme, source, seed=7):
    t = THEMES[theme]
    dark = theme == "dark"
    rng = random.Random(seed)
    ts = Typesetter("g")
    body = []

    # stage: emergency lighting, pulsing alarm, hazard tape top and bottom
    stripe_b = "#111" if dark else "#ffffff"
    body.append(f'''<defs>
  <radialGradient id="room" cx="0.68" cy="0.45" r="0.85">
    <stop offset="0" stop-color="{'#3d0414' if dark else '#ffeef0'}"/><stop offset="0.6" stop-color="{'#160307' if dark else '#fff8f8'}"/><stop offset="1" stop-color="{t['bg']}"/>
  </radialGradient>
  <radialGradient id="alarm" cx="0.5" cy="0.5" r="0.75">
    <stop offset="0.55" stop-color="{t['red']}" stop-opacity="0"/><stop offset="1" stop-color="{t['red']}" stop-opacity="{0.55 if dark else 0.28}"/>
  </radialGradient>
  <pattern id="hazard" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="28" height="28" fill="{stripe_b}"/><rect width="14" height="28" fill="{t['red']}"/>
    <animateTransform attributeName="patternTransform" type="translate" additive="sum" from="0 0" to="28 0" dur="1.6s" repeatCount="indefinite"/>
  </pattern>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{t['red']}" stop-opacity="0"/><stop offset="0.85" stop-color="{t['red']}" stop-opacity="{0.22 if dark else 0.12}"/>
    <stop offset="1" stop-color="{t['red']}" stop-opacity="0.9"/>
  </linearGradient>
  <filter id="glow" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="2.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="12" fill="url(#room)"/>
<rect width="{W}" height="{H}" rx="12" fill="url(#alarm)" opacity="0.4">
  <animate attributeName="opacity" values="0.15;1;0.15" dur="2.4s" repeatCount="indefinite"/></rect>
<rect x="0" y="0" width="{W}" height="14" fill="url(#hazard)"/>
<rect x="0" y="{H - 14}" width="{W}" height="14" fill="url(#hazard)"/>''')

    # status plate, top right
    plate, _ = ts.text("CONTAINMENT ALERT · BSL-4", "label", 15, W - 70, 48, t["red"], anchor="end", tracking=1.6)
    body.append(f'<circle cx="{W - 50}" cy="43" r="7" fill="{t["red"]}" filter="url(#glow)">'
                f'<animate attributeName="opacity" values="1;0.15;1" dur="1s" repeatCount="indefinite"/></circle>{plate}')

    # portrait
    px0, py0, box_h = 62, 34, 492
    src = Image.open(source)
    box_w = int(box_h * src.width / src.height)
    tone, mask = tone_map(source, box_w, box_h, theme)
    rows = 74
    read = encode(HANDLE)
    cx0, cx1, base_y, peak_h = 560, 1546, 380, 118
    traces, step = chromatogram(read, cx0, cx1, base_y, peak_h, rng)
    row_ys = [py0 + (r + 0.5) * box_h / rows for r in range(rows)]
    feed_rows = sorted(sorted(range(rows), key=lambda r: abs(row_ys[r] - (base_y - 10)))[:4])
    feed_base = dict(zip(feed_rows, BASES))
    line_ink = t["ink"]
    xe = px0 + box_w
    rows_svg, flats_svg, routes = [], [], []
    for r, (yc, pts, spans, flats) in enumerate(portrait_rows(tone, mask, px0, py0, rows)):
        begin = 0.1 + r * 0.024
        if spans:
            d = "".join(pts_d(s) for s in spans)
            L = sum(length(s) for s in spans) + 1
            rows_svg.append(f'<path d="{d}" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}">'
                            f'<animate attributeName="stroke-dashoffset" from="{L:.0f}" to="0" begin="{begin:.2f}s" '
                            f'dur="1.1s" fill="freeze"/></path>')
        if flats:
            flats_svg.append("".join(f"M{a:.0f} {yc:.1f}H{b:.0f}" for a, b in flats))
        if r in feed_base:
            k = feed_rows.index(r)
            jog = xe + 26 + 15 * k
            ty = base_y + 6 + (k - 1.5) * 7
            routes.append((feed_base[r], [(xe, yc), (jog, yc), (jog + abs(ty - yc), ty), (cx0 - 14, ty)]))
    body.append(f'<path d="{"".join(flats_svg)}" fill="none" stroke="{line_ink}" stroke-width="1" '
                f'stroke-opacity="{0.16 if dark else 0.2}" opacity="0"><animate attributeName="opacity" from="0" to="1" '
                f'begin="0.1s" dur="1.6s" fill="freeze"/></path>')
    body.append(f'<g fill="none" stroke="{line_ink}" stroke-width="1.15" stroke-opacity="{0.94 if dark else 0.95}" '
                f'stroke-linejoin="round">{"".join(rows_svg)}</g>')

    # biometric scan: face box, then a sweeping scan line forever
    fx0, fy0 = px0 + box_w * 0.20, py0 + box_h * 0.14
    fx1, fy1 = px0 + box_w * 0.80, py0 + box_h * 0.66
    c = 18
    corners = (f"M{fx0},{fy0 + c} V{fy0} H{fx0 + c} M{fx1 - c},{fy0} H{fx1} V{fy0 + c} "
               f"M{fx1},{fy1 - c} V{fy1} H{fx1 - c} M{fx0 + c},{fy1} H{fx0} V{fy1 - c}")
    tag, _ = ts.text("SUBJECT 000 · IDENTIFIED", "label", 12, fx0, fy0 - 8, t["red"], tracking=1.2, reveal=(2.9, 0.02))
    body.append(f'<g opacity="0"><path d="{corners}" fill="none" stroke="{t["red"]}" stroke-width="2.2" filter="url(#glow)"/>'
                f'<set attributeName="opacity" to="1" begin="2.6s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="1;0.55;1" begin="3.2s" dur="1.8s" repeatCount="indefinite"/></g>{tag}')
    body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="2.4s" fill="freeze"/>'
                f'<rect x="{px0 - 10}" y="{py0 - 40}" width="{box_w + 20}" height="40" fill="url(#scan)">'
                f'<animate attributeName="y" values="{py0 - 40};{py0 + box_h - 40}" begin="2.4s" dur="3.2s" repeatCount="indefinite"/></rect>'
                f'<rect x="{px0 - 10}" y="{py0}" width="{box_w + 20}" height="2" fill="{t["red"]}" filter="url(#glow)">'
                f'<animate attributeName="y" values="{py0};{py0 + box_h}" begin="2.4s" dur="3.2s" repeatCount="indefinite"/></rect></g>')

    # feed lines with packets running into the sequencer
    for k, (base, route) in enumerate(routes):
        col = t[base]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in route)
        L = length(route)
        body.append(f'<path id="feed{k}" d="{d}" fill="none" stroke="{col}" stroke-width="1.6" '
                    f'stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}"><animate attributeName="stroke-dashoffset" '
                    f'from="{L:.0f}" to="0" begin="1.9s" dur="0.5s" fill="freeze"/></path>'
                    f'<circle cx="{cx0 - 14}" cy="{route[-1][1]:.1f}" r="3.5" fill="{col}"/>')
        for j in range(2):
            body.append(f'<circle r="3" fill="{col}" opacity="0" filter="url(#glow)">'
                        f'<set attributeName="opacity" to="1" begin="{2.5 + 0.4 * k + 0.8 * j:.1f}s" fill="freeze"/>'
                        f'<animateMotion dur="1.6s" begin="{2.5 + 0.4 * k + 0.8 * j:.1f}s" repeatCount="indefinite">'
                        f'<mpath href="#feed{k}" xlink:href="#feed{k}"/></animateMotion></circle>')

    # chromatogram: traces draw in, bases are called as the trace passes them
    t0, tdur = 2.3, 2.6
    body.append(f'<line x1="{cx0 - 8}" y1="{base_y}" x2="{cx1 + 6}" y2="{base_y}" stroke="{t["edge"]}" stroke-width="1"/>')
    for b in "GACT":
        L = length(traces[b])
        body.append(f'<path d="{pts_d(traces[b])}" fill="none" stroke="{t[b]}" stroke-width="2" stroke-linejoin="round" '
                    f'stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}"><animate attributeName="stroke-dashoffset" '
                    f'from="{L:.0f}" to="0" begin="{t0}s" dur="{tdur}s" fill="freeze"/></path>')
    head, _ = ts.text("READ 01 · 36 bp · Q40", "label", 14, cx0 - 8, base_y - peak_h - 52, t["muted"], reveal=(t0 - 0.4, 0.015))
    body.append(head)
    for i, base in enumerate(read):
        x = cx0 + (i + 0.5) * step
        when = t0 + tdur * (x - cx0) / (cx1 - cx0)
        g, _ = ts.text(base, "mono-bold", 18, x, base_y - peak_h - 18, t[base], anchor="middle", reveal=(when, 0))
        body.append(g)
    # group into bytes and decode
    tb = t0 + tdur + 0.2
    for gi in range(len(read) // 4):
        xa, xb = cx0 + gi * 4 * step + 3, cx0 + (gi + 1) * 4 * step - 3
        byte = HANDLE.encode()[gi]
        when = tb + 0.11 * gi
        body.append(f'<path d="M{xa:.1f},{base_y + 8} v6 H{xb:.1f} v-6" fill="none" stroke="{t["muted"]}" stroke-width="1.2" '
                    f'opacity="0"><set attributeName="opacity" to="1" begin="{when:.2f}s" fill="freeze"/></path>')
        g, _ = ts.text(f"{byte:02x}", "mono-bold", 15, (xa + xb) / 2, base_y + 34, t["ink"], anchor="middle", reveal=(when + 0.05, 0.04))
        body.append(g)

    # terminal
    tt = tb + 0.11 * 9 + 0.3
    y1, y2 = base_y + 84, base_y + 112
    g, tt = ts.text(PROMPT, "mono-bold", 15, cx0 - 8, y1, t["red"], reveal=(tt, 0.012))
    body.append(g)
    px = cx0 - 8 + text_width(PROMPT, "mono-bold", 15)
    g, tt = ts.text(COMMAND, "mono", 15, px, y1, t["ink"], reveal=(tt, 0.025))
    body.append(g)
    hexes = HANDLE.encode().hex()
    dump = f"00000000: {' '.join(hexes[i:i + 4] for i in range(0, len(hexes), 4)):<40} "
    g, tt = ts.text(dump, "mono", 15, cx0 - 8, y2, t["muted"], reveal=(tt + 0.25, 0.008))
    body.append(g)
    ax = cx0 - 8 + text_width(dump, "mono", 15)
    g, tt = ts.text(HANDLE, "mono-bold", 15, ax, y2, t["red"], reveal=(tt + 0.1, 0.06))
    body.append(g)
    cur_x = ax + text_width(HANDLE, "mono-bold", 15) + 6
    body.append(f'<rect x="{cur_x:.1f}" y="{y2 - 14}" width="9" height="17" fill="{t["red"]}" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{tt:.2f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" begin="{tt:.2f}s" dur="1s" repeatCount="indefinite"/></rect>')

    # name plate: the name grown as a cell colony (see wordmark.py)
    wm_defs, wm_body = wordmark.hive("nm", cx0 - 8, 104, 64, t["ink"], t["red"], start=0.25)
    body.append(f"<defs>{wm_defs}</defs>{wm_body}")
    g, e = ts.text("SPECIMEN 000 · HOMO SAPIENS VAR. LLENOXINNENSIS", "label", 16, cx0 - 6, 146, t["muted"],
                   tracking=1.4, reveal=(0.8, 0.012))
    body.append(g)
    g, _ = ts.text("bioinformatics / cybersecurity / AI·ML / networks · Cebu City, PH", "text", 16, cx0 - 6, 171,
                   t["muted"], reveal=(e, 0.01))
    body.append(g)

    # margin notes in red pen
    note, _ = ts.text("decode me", "hand", 28, 1300, 214, t["pen"])
    arrow = f'<path d="M1292,206 Q1250,206 1236,236 M1236,236 l-1,-12 M1236,236 l10,-7" fill="none" stroke="{t["pen"]}" stroke-width="2.2" stroke-linecap="round"/>'
    body.append(f'<g opacity="0">{note}{arrow}<set attributeName="opacity" to="1" begin="5.6s" fill="freeze"/></g>')
    note2, _ = ts.text("do not feed the specimen", "hand", 21, xe + 18, py0 + 236, t["pen"])
    arrow2 = f'<path d="M{xe + 26},{py0 + 214} Q{xe + 14},{py0 + 186} {xe - 20},{py0 + 176} M{xe - 20},{py0 + 176} l12,-3 M{xe - 20},{py0 + 176} l9,9" fill="none" stroke="{t["pen"]}" stroke-width="2" stroke-linecap="round"/>'
    body.append(f'<g opacity="0">{note2}{arrow2}<set attributeName="opacity" to="1" begin="3.4s" fill="freeze"/></g>')

    return svg_doc(W, H, ts.defs_svg() + "\n" + "\n".join(body),
                   "Dexter Juevesano, Llenoxinn: a plotter portrait under a biometric scan, wired into a DNA "
                   "chromatogram whose read decodes to the handle Llenoxinn")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", default=str(ROOT / "lab" / "data" / "portrait.png"))
    args = ap.parse_args()
    for theme in THEMES:
        out = ASSETS / f"banner-{theme}.svg"
        out.write_text(render(theme, args.source), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
