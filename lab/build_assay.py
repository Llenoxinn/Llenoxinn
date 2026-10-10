#!/usr/bin/env python3
"""CTF assay: picoCTF progress as a 96-well plate. assets/assay-{dark,light}.svg

Each solved challenge is one well, coloured by category. On load the wells fill
with reagent in order, a plate-reader laser sweeps the plate, and the readout
types itself out. Data comes from lab/data/picoctf.json (picoCTF has no public
API, so you update that file after solving).

    python lab/build_assay.py
"""
import json
import math
import random

from notebook import ASSETS, LAB, ROOT, THEMES, Typesetter, esc, picture, replace_block, svg_doc, text_width

DATA = ROOT / "lab" / "data" / "picoctf.json"
CATS = {"General Skills": "#8b949e", "Reverse Engineering": "#ffb02e", "Cryptography": "#bc8cff",
        "Web Exploitation": "#58a6ff", "Artificial Intelligence": "#2ee6d6", "Forensics": "#3fb950",
        "Binary Exploitation": "#ff1f3d", "Blockchain": "#ff7a45"}
SHORT = {"General Skills": "GEN", "Cryptography": "CRY", "Web Exploitation": "WEB", "Forensics": "FOR",
         "Reverse Engineering": "REV", "Binary Exploitation": "PWN", "Artificial Intelligence": "AI",
         "Blockchain": "BLK"}
DIFF = {"easy": "#3fb950", "medium": "#ffb02e", "hard": "#ff1f3d"}
ROWS, COLS = 8, 12


def counts(v):
    """Accept either an int (old format) or {easy, medium, hard, total}."""
    if isinstance(v, dict):
        return {k: int(v.get(k) or 0) for k in DIFF}, v.get("total")
    return {"easy": int(v or 0), "medium": 0, "hard": 0}, None


def plate(d, theme):
    t = THEMES[theme]
    ts = Typesetter("a")
    W, H = 840, 470
    px, py, pw, ph = 22, 40, 470, 360
    wx0, wy0, pitch, r = px + 48, py + 64, 34.5, 13.5
    cats = {c: counts(d["solved"].get(c, 0)) for c in CATS}
    order = sorted(CATS, key=lambda c: -sum(cats[c][0].values()))
    wells = [(c, k) for c in order for k in DIFF for _ in range(cats[c][0][k])]
    extra = max(0, len(wells) - ROWS * COLS)
    wells = wells[:ROWS * COLS]
    total = sum(sum(v[0].values()) for v in cats.values())
    by_diff = {k: sum(v[0][k] for v in cats.values()) for k in DIFF}

    from notebook import ambient
    amb_d, amb_b = ambient("aa", W, H, theme, seed=8, cells=9, bits=12)
    body = [f'''<defs>{amb_d}
  <linearGradient id="plastic" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['panel2']}"/><stop offset="1" stop-color="{t['panel']}"/></linearGradient>
  <linearGradient id="laser" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['red']}" stop-opacity="0"/>
    <stop offset="0.85" stop-color="{t['red']}" stop-opacity="0.3"/><stop offset="1" stop-color="{t['red']}" stop-opacity="1"/></linearGradient>
  <pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2.2" height="5" fill="#fff" opacity="0.55"/></pattern>
</defs>
{amb_b}
<path d="M{px + 16},{py} H{px + pw} V{py + ph} H{px} V{py + 16} Z" fill="url(#plastic)" stroke="{t['edge']}" stroke-width="1.5"/>''']
    g, _ = ts.text(f"PLATE 01 · {len(wells)} OF 96 WELLS LOADED", "label", 11, px + 22, py + 22, t["muted"], tracking=1.4)
    body.append(g)
    for c in range(COLS):
        g, _ = ts.text(str(c + 1), "label", 10.5, wx0 + c * pitch, wy0 - 22, t["muted"], anchor="middle")
        body.append(g)
    for rr in range(ROWS):
        g, _ = ts.text("ABCDEFGH"[rr], "label", 10.5, wx0 - 28, wy0 + rr * pitch + 4, t["muted"], anchor="middle")
        body.append(g)
    clips = []
    col_t = lambda c: 0.6 + 0.42 * c          # when the pipette head reaches column c
    for i in range(ROWS * COLS):
        c, rr = divmod(i, ROWS)               # filled column by column, like a multichannel pipette
        cx, cy = wx0 + c * pitch, wy0 + rr * pitch
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{t["bg"]}" stroke="{t["edge"]}" stroke-width="1.2"/>')
        if i < len(wells):
            cat, diff = wells[i]
            begin = col_t(c) + 0.18
            clips.append(f'<clipPath id="w{i}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r - 2}"/></clipPath>')
            mark = ""
            if diff == "medium":
                mark = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r - 2}" fill="url(#hatch)"/>'
            elif diff == "hard":
                mark = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="#fff"/>'
            glow_begin = col_t(COLS) + 0.6 + 0.03 * i
            body.append(f'<g clip-path="url(#w{i})"><rect x="{cx - r:.1f}" y="{cy + r:.1f}" width="{2 * r}" height="{2 * r}" fill="{CATS[cat]}">'
                        f'<animate attributeName="y" from="{cy + r:.1f}" to="{cy - r + 2:.1f}" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/></rect>'
                        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin + 0.35:.2f}s" fill="freeze"/>{mark}'
                        f'<circle cx="{cx - 4:.1f}" cy="{cy - 4:.1f}" r="3" fill="#fff" opacity="0.45"/></g></g>'
                        # plate-reader fluorescence: each loaded well breathes once the run is done
                        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 1}" fill="none" stroke="{CATS[cat]}" stroke-width="2" opacity="0" filter="url(#wg)">'
                        f'<animate attributeName="opacity" values="0;0.9;0" dur="2.4s" begin="{glow_begin:.2f}s" repeatCount="indefinite"/></circle>')
    body.insert(1, "<defs>" + "".join(clips) + '<filter id="wg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter></defs>')
    # the 8-channel pipette head: steps across the plate, dispensing a drop per tip at each column
    cols_needed = max(1, -(-len(wells) // ROWS))
    xs = [wx0 + c * pitch for c in range(cols_needed)]
    key = ";".join(f"{x - wx0:.1f} 0" for x in xs) + f";{px + pw + 30 - wx0:.1f} 0"
    times = [col_t(c) for c in range(cols_needed)] + [col_t(cols_needed) + 0.2]
    total_t = times[-1] + 0.5
    kt = ";".join(f"{tt / total_t:.3f}" for tt in [0] + times[1:]) + ";1"
    vals = f"{xs[0] - wx0 - 60:.1f} 0;" + key
    kts = "0;" + ";".join(f"{tt / total_t:.3f}" for tt in times) + ";1"
    vals = f"{-60:.1f} 0;" + ";".join(f"{x - wx0:.1f} 0" for x in xs) + f";{px + pw + 40 - wx0:.1f} 0"
    head = [f'<rect x="{wx0 - 11}" y="{wy0 - 30}" width="22" height="{ROWS * pitch + 26:.0f}" rx="6" fill="{t["panel2"]}" stroke="{t["ink"]}" stroke-opacity="0.6" stroke-width="1.4"/>',
            f'<rect x="{wx0 - 6}" y="{wy0 - 26}" width="12" height="10" rx="2" fill="{t["red"]}"><animate attributeName="opacity" values="1;0.3;1" dur="0.5s" repeatCount="indefinite"/></rect>']
    for rr in range(ROWS):
        ty = wy0 + rr * pitch
        head.append(f'<circle cx="{wx0}" cy="{ty:.1f}" r="5.5" fill="{t["bg"]}" stroke="{t["ink"]}" stroke-opacity="0.7" stroke-width="1.2"/>')
        head.append(f'<circle cx="{wx0}" cy="{ty:.1f}" r="2.4" fill="{t["red"]}"><animate attributeName="r" values="2.4;4.2;2.4" dur="0.42s" repeatCount="{cols_needed}" begin="{col_t(0):.2f}s"/></circle>')
    body.append(f'<g>{"".join(head)}<animateTransform attributeName="transform" type="translate" values="{vals}" '
                f'keyTimes="{kts}" calcMode="spline" keySplines="{";".join(["0.6 0 0.3 1"] * (cols_needed + 1))}" dur="{total_t:.2f}s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.92;1" dur="{total_t:.2f}s" fill="freeze"/></g>')
    g, _ = ts.text("8-CHANNEL HEAD · DISPENSING", "label", 10, px + pw - 16, py + ph - 14, t["red"], anchor="end", tracking=1.2)
    body.append(f'<g>{g}<animate attributeName="opacity" values="1;0.2;1" dur="0.8s" repeatCount="{max(1, int(total_t / 0.8))}"/>'
                f'<set attributeName="opacity" to="0" begin="{total_t:.2f}s" fill="freeze"/></g>')
    g, _ = ts.text("READ COMPLETE · FLUORESCENCE", "label", 10, px + pw - 16, py + ph - 14, t["muted"], anchor="end", tracking=1.2)
    body.append(f'<g opacity="0">{g}<set attributeName="opacity" to="1" begin="{total_t:.2f}s" fill="freeze"/></g>')
    body.append(f'<clipPath id="plate"><rect x="{px}" y="{py}" width="{pw}" height="{ph}"/></clipPath>')
    body.append(f'<rect clip-path="url(#plate)" x="{px - 70}" y="{py}" width="70" height="{ph}" fill="url(#laser)">'
                f'<animate attributeName="x" values="{px - 70};{px + pw}" dur="3.4s" begin="{total_t:.1f}s" repeatCount="indefinite"/></rect>')
    # legend under the plate
    lx = px + 22
    for label, kind in (("easy", "solid"), ("medium", "hatched"), ("hard", "dot")):
        body.append(f'<circle cx="{lx + 6}" cy="{py + ph - 18}" r="6" fill="{t["muted"]}"/>')
        if kind == "hatched":
            body.append(f'<circle cx="{lx + 6}" cy="{py + ph - 18}" r="6" fill="url(#hatch)"/>')
        if kind == "dot":
            body.append(f'<circle cx="{lx + 6}" cy="{py + ph - 18}" r="2.2" fill="#fff"/>')
        g, _ = ts.text(label, "text", 11.5, lx + 17, py + ph - 14, t["muted"])
        body.append(g)
        lx += 82
    if extra:
        g, _ = ts.text(f"+{extra} more", "label", 12, px + pw - 14, py + ph - 14, t["ink"], anchor="end")
        body.append(g)

    # readout
    rx, rw = 520, W - 26 - 520
    g, e = ts.text("CTF ASSAY · PICOGYM · CMU CYLAB", "label", 12, rx, 50, t["red"], tracking=1.6, reveal=(0.2, 0.015))
    body.append(g)
    g, e = ts.text(f"@{d.get('username') or 'unknown'}", "mono-bold", 14, rx, 74, t["ink"], reveal=(e, 0.04))
    body.append(g)
    g, _ = ts.text(str(total), "wordmark", 56, rx, 136, t["ink"])
    body.append(g)
    nw = text_width(str(total), "wordmark", 56)
    g, _ = ts.text("flags captured", "text", 14, rx + nw + 10, 134, t["muted"])
    body.append(g)
    extras = [f"{int(d['score']):,} pts" if d.get("score") else "", f"rank #{int(d['rank']):,}" if d.get("rank") else ""]
    if any(extras):
        g, _ = ts.text(" · ".join(x for x in extras if x), "text", 13, rx + nw + 10, 116, t["muted"])
        body.append(g)
    # difficulty split, like a stacked gel lane
    bx, by, bw, bh = rx, 152, rw, 10
    body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="5" fill="{t["faint"]}"/>')
    acc = 0
    for k, col in DIFF.items():
        n = by_diff[k]
        if not n:
            continue
        w = bw * n / max(total, 1)
        body.append(f'<rect x="{bx + acc:.1f}" y="{by}" width="0" height="{bh}" fill="{col}">'
                    f'<animate attributeName="width" from="0" to="{w:.1f}" begin="0.5s" dur="0.9s" fill="freeze"/></rect>')
        acc += w
    g, _ = ts.text(" · ".join(f"{by_diff[k]} {k}" for k in DIFF), "text", 12, rx, by + 28, t["muted"])
    body.append(g)
    y = 222
    for cat in order:
        (n, tot) = (sum(cats[cat][0].values()), cats[cat][1])
        col = CATS[cat]
        body.append(f'<circle cx="{rx + 5}" cy="{y - 4}" r="5" fill="{col}"/>')
        g, _ = ts.text(cat, "text", 13, rx + 17, y, t["ink"] if n else t["muted"])
        body.append(g)
        right = f"{n}/{tot}" if tot else f"{n}"
        g, _ = ts.text(right, "label", 12.5, W - 26, y, t["ink"] if n else t["muted"], anchor="end")
        body.append(g)
        track = rw - 17
        body.append(f'<rect x="{rx + 17}" y="{y + 5}" width="{track}" height="4" rx="2" fill="{t["faint"]}"/>')
        if tot:
            acc = 0
            for k in DIFF:
                m = cats[cat][0][k]
                if not m:
                    continue
                w = track * m / tot
                fill = col if k == "easy" else ("url(#hatch)" if False else col)
                op = {"easy": 1, "medium": 0.55, "hard": 0.3}[k]
                body.append(f'<rect x="{rx + 17 + acc:.1f}" y="{y + 5}" width="0" height="4" fill="{fill}" opacity="{op}">'
                            f'<animate attributeName="width" from="0" to="{w:.1f}" begin="0.8s" dur="1s" fill="freeze"/></rect>')
                acc += w
        else:
            for j in range(min(n, 30)):
                body.append(f'<rect x="{rx + 17 + j * 7}" y="{y + 4}" width="5" height="6" rx="1" fill="{col}"/>')
        y += 27
    note = "bars: easy solid, medium faded, out of every challenge in the category"
    g, _ = ts.text("still to culture: forensics, pwn, blockchain", "hand", 18, W - 26, H - 16, t["pen"], anchor="end") \
        if not any(sum(cats[c][0].values()) for c in ("Forensics", "Binary Exploitation")) else ("", 0)
    body.append(g)
    return svg_doc(W, H, ts.defs_svg() + "\n".join(body),
                   f"picoGym assay plate for @{d.get('username')}: {total} flags captured ({by_diff['easy']} easy, "
                   f"{by_diff['medium']} medium, {by_diff['hard']} hard). " +
                   ", ".join(f"{c} {sum(cats[c][0].values())}" for c in order))


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    for theme in THEMES:
        (ASSETS / f"assay-{theme}.svg").write_text(plate(d, theme), encoding="utf-8")
    url = d.get("profile_url") or "https://play.picoctf.org"
    total = sum(sum(counts(v)[0].values()) for v in d["solved"].values())
    block = (f'<a href="{esc(url)}">{picture("assay", "picoGym assay plate", width="100%", query="v=" + str(total))}</a>\n\n'
             f'<sub>One well per flag · {total} captured as <code>@{esc(d.get("username") or "")}</code> on picoGym</sub>')
    changed = replace_block("ASSAY", block)
    print(f"assay: {total} solves, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
