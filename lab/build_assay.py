#!/usr/bin/env python3
"""CTF assay: picoGym progress as a 96-well plate. assets/assay-{dark,light}.svg

Each solved challenge is one well, coloured by category; the wells fill once, in
order, when the image loads. Data comes from lab/data/picoctf.json (picoCTF has no
public API, so you update that file after solving).

    python lab/build_assay.py
"""
import json

from notebook import (ASSETS, PAPER, ROOT, SHADE, STAT_H, STAT_W, THEMES, Typesetter, box, esc, foot, printed,
                      reading, replace_block, scene, sparkle, stamp, step_in, svg_doc)

DATA = ROOT / "lab" / "data" / "picoctf.json"
# category -> (dark, light); the light set keeps 3:1 against the paper sheet
CATS = {"General Skills": ("#8b949e", "#57606a"), "Reverse Engineering": ("#ffb02e", "#b45309"),
        "Cryptography": ("#bc8cff", "#8250df"), "Web Exploitation": ("#58a6ff", "#0969da"),
        "Artificial Intelligence": ("#2ee6d6", "#0e7c74"), "Forensics": ("#3fb950", "#1a7f37"),
        "Binary Exploitation": ("#ff4d5e", "#cf222e"), "Blockchain": ("#ff7a45", "#c2410c")}
DIFF = ("easy", "medium", "hard")
ROWS, COLS = 8, 12
SHORT = {"General Skills": "General", "Reverse Engineering": "Reversing", "Cryptography": "Crypto",
         "Web Exploitation": "Web", "Artificial Intelligence": "AI", "Forensics": "Forensics",
         "Binary Exploitation": "Pwn", "Blockchain": "Blockchain"}


def counts(v):
    """Accept either an int (old format) or {easy, medium, hard, total}."""
    if isinstance(v, dict):
        return {k: int(v.get(k) or 0) for k in DIFF}, v.get("total")
    return {"easy": int(v or 0), "medium": 0, "hard": 0}, None


def tally(d):
    cats = {c: counts(d["solved"].get(c, 0))[0] for c in CATS}
    order = sorted((c for c in CATS if sum(cats[c].values())), key=lambda c: -sum(cats[c].values()))
    by_diff = {k: sum(v[k] for v in cats.values()) for k in DIFF}
    return cats, order, by_diff, sum(by_diff.values())


def plate(d, theme, animate=True):
    """picoGym card: flags captured ticks up, then a 96-well plate fills in order inside a recessed
    assay tray, scanned top-to-bottom by a microplate reader bar that highlights the newest flag."""
    s = PAPER[theme]
    ts = Typesetter("a")
    tone = 0 if theme == "dark" else 1
    cats, order, by_diff, total = tally(d)
    wells = [c for c in order for _ in range(sum(cats[c].values()))]
    extra = max(0, len(wells) - ROWS * COLS)
    wells = wells[:ROWS * COLS]
    body = reading(ts, theme, "pico", "PICOGYM", f"@{d.get('username')}", total, "flags", animate)
    body.append(box(11, 82, 108, 71, s["recess"], 2, s["line"]))
    px0, py0, dx, dy, wsize, hsize = 16.5, 88.0, 8.2, 7.6, 6.8, 6.2
    cells = []
    for i in range(ROWS * COLS):
        row, col = divmod(i, COLS)
        x, y = px0 + dx * col, py0 + dy * row
        filled = i < len(wells)
        motion = step_in(0.38 + i * 0.006) if animate and filled else ""
        cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{wsize}" height="{hsize}" '
                     f'fill="{CATS[wells[i]][tone] if filled else s["well"]}">{motion}</rect>')
    if animate and wells:
        # Microplate reader bar sweeps top-to-bottom across the 8 rows every 6s (staggered 3rd card)
        plate_w = (COLS - 1) * dx + wsize
        ys = [f"{py0 + r * dy:.1f}" for r in range(ROWS)]
        travel = 0.24
        kt = [f"{travel * r / ROWS:.4f}" for r in range(ROWS)] + [f"{travel:.4f}", "1"]
        kt_s = ";".join(kt)
        op_s = ";".join(["0.30"] * ROWS + ["0", "0"])
        cells.append(
            f'<rect x="{px0:.1f}" y="{ys[0]}" width="{plate_w:.1f}" height="{hsize}" fill="{s["text"]}" opacity="0">'
            f'<animate attributeName="y" values="{";".join(ys)};{ys[-1]};{ys[0]}" keyTimes="{kt_s}" '
            f'calcMode="discrete" dur="6.0s" begin="4.2s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{op_s}" keyTimes="{kt_s}" calcMode="discrete" '
            f'dur="6.0s" begin="4.2s" repeatCount="indefinite"/></rect>'
        )
        # Newest captured flag well flashes + sparkles right as the reader row crosses it
        lr, lc = divmod(len(wells) - 1, COLS)
        wx, wy = px0 + dx * lc, py0 + dy * lr
        hit = travel * lr / ROWS
        cells.append(
            f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{wsize}" height="{hsize}" fill="{s["text"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.85;0" keyTimes="0;{hit:.4f};{hit + 0.08:.4f}" '
            f'calcMode="discrete" dur="6.0s" begin="4.2s" repeatCount="indefinite"/></rect>'
            + sparkle(wx + 2, wy - 2, 2, s["text"], 6.0, 4.2 + hit * 6.0 - 0.25)
        )
    body.append(f'<g shape-rendering="crispEdges">{"".join(cells)}</g>')
    lx, right = 127, STAT_W - SHADE - 14
    for k, cat in enumerate(order[:3]):
        y = 96 + k * 19
        body.append(f'<g>{step_in(0.62 + k * 0.08 if animate else None)}'
                    f'<rect x="{lx}" y="{y - 8}" width="8" height="8" fill="{CATS[cat][tone]}"/>'
                    + ts.text(SHORT[cat], "body", 12, lx + 13, y, s["text"])[0]
                    + ts.text(str(sum(cats[cat].values())), "body-bold", 12, right, y, s["text"], anchor="end")[0]
                    + "</g>")
    if len(order) > 3:
        body.append(ts.text(f"+ {len(order) - 3} more", "body", 11.5, lx + 13, 152, s["muted"])[0])
    split = ", ".join(f"{by_diff[k]} {k}" for k in DIFF if by_diff[k]) or "no flags yet"
    body.append(foot(ts, theme, split + (f", {extra} more off the plate" if extra else "")))
    label = (f"picoGym progress for @{d.get('username')}: {total} flags captured ({split}). "
             + ", ".join(f"{c} {sum(cats[c].values())}" for c in order) + ".")
    return svg_doc(STAT_W, STAT_H, ts.defs_svg() + printed("pcp", STAT_W, STAT_H, body, animate), label), label


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    svgs = {theme: plate(d, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"assay-{theme}.svg").write_text(svg, encoding="utf-8")
        (ASSETS / f"assay-still-{theme}.svg").write_text(plate(d, theme, False)[0], encoding="utf-8")
    url = d.get("profile_url") or "https://play.picoctf.org"
    pic = scene("assay", svgs["light"][1], STAT_W, STAT_H, query="v=" + stamp(svgs["light"][0]))
    changed = replace_block("ASSAY", f'<a href="{esc(url)}">{pic}</a>')
    print(f"assay: {tally(d)[3]} solves, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
