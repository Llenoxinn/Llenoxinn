#!/usr/bin/env python3
"""CTF assay: picoGym progress as a 96-well plate. assets/assay-{dark,light}.svg

Each solved challenge is one well, coloured by category; the wells fill once, in
order, when the image loads. Data comes from lab/data/picoctf.json (picoCTF has no
public API, so you update that file after solving).

    python lab/build_assay.py
"""
import datetime as dt
import json

from notebook import (ASSETS, BRAND, ROOT, SHEET, STAT_H, STAT_W, THEMES, Typesetter, card, esc, fade, footnote,
                      readout, replace_block, stamp, strip, strip_tag, svg_doc, themed)

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


def plate(d, theme):
    """picoGym card: flags captured, then a 96-well plate that fills in order with one well per flag."""
    s = SHEET[theme]
    ts = Typesetter("a")
    tone = 0 if theme == "dark" else 1
    cats, order, by_diff, total = tally(d)
    wells = [c for c in order for _ in range(sum(cats[c].values()))]
    extra = max(0, len(wells) - ROWS * COLS)
    wells = wells[:ROWS * COLS]
    head, typed = strip(ts, STAT_W, 0, [("picoctf", BRAND["lavender"]), (" > ", BRAND["neon"]),
                                        ("gym", BRAND["paper"])], start=0.1, top=True)
    body = [card(theme, STAT_W, STAT_H), head, readout(ts, theme, total, "flags", typed + 0.1)]
    if d.get("updated"):
        day = dt.date.fromisoformat(d["updated"])
        body.append(strip_tag(ts, STAT_W, f"logged {day.day} {day:%b}"))
    pitch, r = 8.4, 3.1
    for i in range(ROWS * COLS):
        row, col = divmod(i, COLS)
        cx, cy = 14 + pitch * (col + 0.5), 98 + pitch * (row + 0.5)
        fill = CATS[wells[i]][tone] if i < len(wells) else s["well"]
        anim = fade(typed + 0.25 + i * 0.01, 0.15) if i < len(wells) else ""
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}">{anim}</circle>')
    lx = 14 + pitch * COLS + 14
    for k, cat in enumerate(order[:3]):
        y = 107 + k * 20
        body.append(f'<g opacity="1">{fade(typed + 0.5 + k * 0.08)}'
                    f'<rect x="{lx}" y="{y - 8}" width="8" height="8" rx="1" fill="{CATS[cat][tone]}"/>'
                    + ts.text(SHORT[cat], "text", 13, lx + 14, y, s["text"])[0]
                    + ts.text(str(sum(cats[cat].values())), "code-bold", 12, STAT_W - 14, y, s["text"], anchor="end")[0]
                    + "</g>")
    if len(order) > 3:
        body.append(f'<g opacity="1">{fade(typed + 0.75)}'
                    + ts.text(f"+ {len(order) - 3} more", "text", 13, lx + 14, 167, s["muted"])[0] + "</g>")
    split = " · ".join(f"{by_diff[k]} {k}" for k in DIFF if by_diff[k]) or "no flags yet"
    body.append(footnote(ts, theme, split + (f" · +{extra} off-plate" if extra else ""), typed + 1.2))
    label = (f"picoGym progress for @{d.get('username')}: {total} flags captured ({split}). "
             + ", ".join(f"{c} {sum(cats[c].values())}" for c in order) + ".")
    return svg_doc(STAT_W, STAT_H, ts.defs_svg() + "".join(body), label), label


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    svgs = {theme: plate(d, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"assay-{theme}.svg").write_text(svg, encoding="utf-8")
    url = d.get("profile_url") or "https://play.picoctf.org"
    pic = themed("assay", svgs["light"][1], STAT_W, STAT_H, query="v=" + stamp(svgs["light"][0]))
    changed = replace_block("ASSAY", f'<a href="{esc(url)}">{pic}</a>')
    print(f"assay: {tally(d)[3]} solves, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
