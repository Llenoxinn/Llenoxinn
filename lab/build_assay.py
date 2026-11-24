#!/usr/bin/env python3
"""CTF assay: picoGym progress as a 96-well plate. assets/assay-{dark,light}.svg and stills

Each solved challenge is one well, coloured by category; the wells fill once, in
order, when the image loads. The plate sits on a screen, so the bright category
colours are used in both themes. Data comes from lab/data/picoctf.json (picoCTF has no
public API, so you update that file after solving).

    python lab/build_assay.py
"""
import json

from notebook import ASSETS, ROOT, THEMES, Typesetter, count_up, esc, replace_block, scene, stamp, svg_doc
from rts import HALF, INK, bar, defs, plaque, text

PANEL_H = 236

DATA = ROOT / "lab" / "data" / "picoctf.json"
# category -> colour on a screen
CATS = {"General Skills": "#8b949e", "Reverse Engineering": "#ffb02e", "Cryptography": "#bc8cff",
        "Web Exploitation": "#58a6ff", "Artificial Intelligence": "#2ee6d6", "Forensics": "#3fb950",
        "Binary Exploitation": "#ff4d5e", "Blockchain": "#ff7a45"}
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
    """picoGym production panel: flags captured, then the top categories as filling slots."""
    ts = Typesetter("a")
    cats, order, by_diff, total = tally(d)
    body = [defs(), plaque(0, 0, HALF, PANEL_H),
            text(ts, "PICOGYM", "head", 15, 16, 30, "url(#orange)", track=.1),
            text(ts, f"@{d.get('username')}", "semi", 14, HALF - 16, 30, INK["muted"], anchor="end"),
            count_up(lambda n: text(ts, f"{n:,}", "num", 52, 16, 86, INK["text"]), total, 0.3 if animate else None),
            text(ts, "FLAGS CAPTURED", "bold", 12, 80, 68, INK["muted"], track=.14)]
    split = ", ".join(f"{by_diff[k]} {k}" for k in DIFF if by_diff[k]) or "no flags yet"
    body.append(text(ts, split.upper(), "bold", 12, 80, 84, INK["gold"], track=.12))
    for k, cat in enumerate(order[:4]):
        got = sum(cats[cat].values())
        tot = counts(d["solved"][cat])[1]
        x, y = 16 + (k % 2) * 194, 118 + (k // 2) * 44
        body.append(bar(ts, x, y, 184, got / tot if tot else got / total, CATS[cat], SHORT[cat],
                        f"{got}" + ("\\" + str(tot) if tot else ""), 0.5 + k * .12 if animate else None))
    if len(order) > 4:
        body.append(text(ts, f"+ {len(order) - 4} MORE CATEGORIES", "bold", 10.5, 16, PANEL_H - 14, INK["dim"], track=.08))
    label = (f"picoGym progress for @{d.get('username')}: {total} flags captured ({split}). "
             + ", ".join(f"{c} {sum(cats[c].values())}" for c in order) + ".")
    return svg_doc(HALF, PANEL_H, ts.defs_svg() + "".join(body), label), label


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    svgs = {theme: plate(d, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"assay-{theme}.svg").write_text(svg, encoding="utf-8")
        (ASSETS / f"assay-still-{theme}.svg").write_text(plate(d, theme, False)[0], encoding="utf-8")
    url = d.get("profile_url") or "https://play.picoctf.org"
    pic = scene("assay", svgs["light"][1], HALF, PANEL_H, query="v=" + stamp(svgs["light"][0]))
    changed = replace_block("ASSAY", f'<a href="{esc(url)}">{pic}</a>')
    print(f"assay: {tally(d)[3]} solves, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
