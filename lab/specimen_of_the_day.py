#!/usr/bin/env python3
"""Tonight's Specimen of the Day, drawn from the RCSB Protein Data Bank.

Picks a structure at random (seeded by the Manila date, so re-runs on the same
day pick the same one), downloads its coordinates, traces the backbone (Cα for
protein, P for nucleic acid) and writes an animated accession card:
the molecule draws itself in and turns, while the label types itself out.

Writes assets/specimen-{dark,light}.svg and the SPECIMEN block of README.md.

    python lab/specimen_of_the_day.py
    python lab/specimen_of_the_day.py --date 2026-01-01   # replay a past day
    python lab/specimen_of_the_day.py --id 4HHB           # a specific entry
"""
import argparse
import gzip
import json
import math
import random
import re
import sys
import time
import urllib.error
import urllib.request

import numpy as np

from notebook import ASSETS, LAB, THEMES, esc, glyphs, now_manila, picture, replace_block, svg_doc, svg_text

DATA_API = "https://data.rcsb.org/rest/v1"
FILES = "https://files.rcsb.org/download"
HEADERS = {"User-Agent": "specimen-lab (github.com/Llenoxinn; profile README bot)"}
CANDIDATES = 15
MAX_ATOMS = 30000          # skip giant assemblies: the download would be huge
MAX_POINTS = 300           # backbone points kept for the drawing
FRAMES = 24                # rotation keyframes

ACRONYMS = {"dna", "rna", "mrna", "trna", "rrna", "atp", "adp", "gtp", "gdp", "nad", "nadh", "nadp",
            "nadph", "fad", "fmn", "hiv", "sars", "mers", "mhc", "tcr", "gpcr", "abc", "ii", "iii", "iv",
            "vi", "vii", "viii", "ix", "xi", "xii", "nmr", "em", "cryo-em", "pdz", "sh2", "sh3", "ph",
            "rnase", "dnase", "crispr", "cas9", "jak", "kras", "egfr", "her2", "bcl-2"}
METHODS = {"X-RAY DIFFRACTION": "X-ray diffraction", "ELECTRON MICROSCOPY": "Cryo-EM",
           "SOLUTION NMR": "Solution NMR", "SOLID-STATE NMR": "Solid-state NMR",
           "NEUTRON DIFFRACTION": "Neutron diffraction", "ELECTRON CRYSTALLOGRAPHY": "Electron crystallography",
           "FIBER DIFFRACTION": "Fiber diffraction"}


# ------------------------------------------------------------------ network

def fetch(url, retries=3, raw=False):
    err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=90) as r:
                data = r.read()
                return data if raw else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = e
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            err = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"could not fetch {url}: {err}")


def coordinates(pdb_id):
    gz = fetch(f"{FILES}/{pdb_id}.cif.gz", raw=True)
    if gz:
        return gzip.decompress(gz).decode("utf-8", "replace")
    plain = fetch(f"{FILES}/{pdb_id}.cif", raw=True)
    return plain.decode("utf-8", "replace") if plain else None


# ------------------------------------------------------------------ structure

TOKEN = re.compile(r"'(?:[^']|'(?=\S))*'|\"[^\"]*\"|\S+")


def backbone(cif):
    """{chain: [(x, y, z), ...]} of Cα / P atoms from model 1, in sequence order."""
    lines = cif.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "loop_" and i + 1 < len(lines) and lines[i + 1].startswith("_atom_site."):
            break
        i += 1
    else:
        return {}
    i += 1
    cols = []
    while i < len(lines) and lines[i].startswith("_atom_site."):
        cols.append(lines[i].strip().split(".", 1)[1])
        i += 1
    col = {c: k for k, c in enumerate(cols)}
    need = ["group_PDB", "label_atom_id", "label_alt_id", "label_asym_id", "label_seq_id",
            "Cartn_x", "Cartn_y", "Cartn_z"]
    if any(c not in col for c in need):
        return {}
    model_col = col.get("pdbx_PDB_model_num")
    chains, first_model = {}, None
    for line in lines[i:]:
        if not line or line.startswith(("#", "loop_", "_")):
            if chains:
                break
            continue
        f = TOKEN.findall(line)
        if len(f) < len(cols):
            continue
        if f[col["group_PDB"]] != "ATOM" or f[col["label_atom_id"]].strip('"') not in ("CA", "P"):
            continue
        if f[col["label_alt_id"]] not in (".", "A", "?"):
            continue
        if model_col is not None:
            first_model = first_model or f[model_col]
            if f[model_col] != first_model:
                break
        try:
            seq = int(f[col["label_seq_id"]])
            xyz = tuple(float(f[col[c]]) for c in ("Cartn_x", "Cartn_y", "Cartn_z"))
        except ValueError:
            continue
        chains.setdefault(f[col["label_asym_id"]], []).append((seq, xyz))
    return {c: [p for _, p in sorted(v)] for c, v in chains.items() if len(v) >= 8}


def thin(chains, budget=MAX_POINTS):
    total = sum(len(v) for v in chains.values())
    step = max(1, math.ceil(total / budget))
    out = {}
    for c, pts in chains.items():
        keep = pts[::step]
        if keep[-1] is not pts[-1]:
            keep.append(pts[-1])
        if len(keep) >= 4:
            out[c] = np.array(keep)
    return out


# ------------------------------------------------------------------ metadata

def sentence_case(text):
    text = " ".join(str(text).split())
    if not text or text != text.upper():
        return text
    def fix(w):
        if any(c.isdigit() for c in w):
            return w.upper()
        return "-".join(p.upper() if p.strip("()[],;:.") in ACRONYMS or len(p.strip("()[],;:.")) == 1 and "-" in w else p
                        for p in w.split("-"))
    words = [fix(w) for w in text.lower().split(" ")]
    s = " ".join(words)
    return s[0].upper() + s[1:]


TITLE_PREFIX = re.compile(r"^(?:pandda analysis group deposition|group deposition|crystal structure of( the)?|"
                          r"x-ray structure of( the)?|cryo-?em structure of( the)?|solution (?:nmr )?structure of( the)?|"
                          r"structure of( the)?|the (?:crystal )?structure of)\s*[-:–—]*\s*", re.I)
TITLE_NOISE = [re.compile(p, re.I) for p in (
    r"\(dataset \d+\)", r"\bfrom the .*(?:campaign|screen(?:ing)?|library)\b", r",? data used for .*$",
    r"\bin complex with\b.*$", r"\bat \d+(?:\.\d+)? ?(?:a|å|angstroms?)( resolution)?\b", r"\bbound to\b.*$")]


def short_title(title, limit=58):
    """Readable headline from a PDB title: no deposition boilerplate, no dataset noise."""
    t = " ".join(str(title).split())
    if " -- " in t:
        head, tail = t.split(" -- ", 1)
        t = tail if re.search(r"deposition|pandda|group", head, re.I) else head
    for _ in range(2):
        t = TITLE_PREFIX.sub("", t)
    for rx in TITLE_NOISE:
        t = rx.sub("", t)
    t = re.split(r"[;,:]", t)[0].strip(" -–—:.")
    t = re.sub(r"^(?:a|an|the)\s+", "", " ".join(t.split()), flags=re.I)
    if len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-") + "…"
    return (t[0].upper() + t[1:]) if t else str(title)[:limit]


def describe(pdb_id):
    entry = fetch(f"{DATA_API}/core/entry/{pdb_id}")
    if not entry or not (entry.get("struct") or {}).get("title"):
        return None
    info = entry.get("rcsb_entry_info") or {}
    atoms = info.get("deposited_atom_count") or 0
    if atoms > MAX_ATOMS:
        return None
    method = ((entry.get("exptl") or [{}])[0].get("method") or "").upper()
    organism = None
    for eid in (entry.get("rcsb_entry_container_identifiers") or {}).get("polymer_entity_ids") or []:
        src = ((fetch(f"{DATA_API}/core/polymer_entity/{pdb_id}/{eid}") or {})
               .get("rcsb_entity_source_organism") or [{}])[0]
        organism = src.get("ncbi_scientific_name") or src.get("scientific_name")
        if organism:
            break
    return {
        "id": pdb_id.upper(),
        "title": sentence_case(entry["struct"]["title"]),
        "short": short_title(sentence_case(entry["struct"]["title"])),
        "method": METHODS.get(method, method.capitalize()) if method else None,
        "resolution": (info.get("resolution_combined") or [None])[0],
        "deposited": ((entry.get("rcsb_accession_info") or {}).get("deposit_date") or "")[:10] or None,
        "class": sentence_case((entry.get("struct_keywords") or {}).get("pdbx_keywords") or "") or None,
        "organism": organism,
    }


# ------------------------------------------------------------------ drawing

RAINBOW = {"dark": ["#58a6ff", "#3fb950", "#e3b341", "#f0883e", "#f85149"],
           "light": ["#0969da", "#1a7f37", "#9a6700", "#bc4c00", "#cf222e"]}


def frames(chains, cx, cy, radius):
    """Per-frame 2D projections and depths of every point, after PCA alignment."""
    allp = np.vstack(list(chains.values()))
    centre = allp.mean(axis=0)
    _, _, vt = np.linalg.svd(allp - centre, full_matrices=False)
    aligned = {c: (p - centre) @ vt.T for c, p in chains.items()}   # x = longest axis
    extent = max(np.linalg.norm(np.vstack(list(aligned.values())), axis=1).max(), 1e-6)
    scale = radius / extent
    out = []
    for f in range(FRAMES):
        a = 2 * math.pi * f / FRAMES
        rot = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
        out.append({c: (p @ rot.T) for c, p in aligned.items()})
    return out, scale


def molecule(chains, theme, cx, cy, radius):
    pal = RAINBOW[theme]
    fr, scale = frames(chains, cx, cy, radius)
    parts, k = [], 0
    dur = 20
    for c in chains:
        n = len(chains[c])
        for s in range(0, n - 1, 6):
            idx = list(range(s, min(n, s + 7)))
            ds, ops = [], []
            for f in fr:
                p = f[c][idx]
                ds.append("M" + " L".join(f"{cx + x * scale:.1f},{cy - y * scale:.1f}" for x, y in p[:, :2]))
                depth = p[:, 2].mean() * scale / radius          # -1 far .. 1 near
                ops.append(f"{0.35 + 0.65 * (depth + 1) / 2:.2f}")
            colour = pal[min(len(pal) - 1, int(len(pal) * s / n))]
            begin = 0.25 + k * 0.035
            parts.append(
                f'<path d="{ds[0]}" fill="none" stroke="{colour}" stroke-width="2.4" stroke-linecap="round" '
                f'stroke-linejoin="round" stroke-dasharray="400" stroke-dashoffset="400" opacity="{ops[0]}">'
                f'<animate attributeName="stroke-dashoffset" from="400" to="0" begin="{begin:.2f}s" dur="0.5s" fill="freeze"/>'
                f'<animate attributeName="d" values="{";".join(ds + [ds[0]])}" dur="{dur}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{";".join(ops + [ops[0]])}" dur="{dur}s" repeatCount="indefinite"/>'
                f'</path>')
            k += 1
    return "".join(parts), k


def typed_line(text, face, size, x, y, fill, start, rate=0.012, anchor="start", tracking=0.0):
    """Glyphs that appear one at a time, like a typewriter. Returns (svg, end time)."""
    out, t = [], start
    for ch, tf, d in glyphs(text, face, size, x, y, anchor=anchor, tracking=tracking, jitter=0.45, seed=start):
        out.append(f'<path transform="{tf}" d="{d}" opacity="0"><set attributeName="opacity" to="1" '
                   f'begin="{t:.2f}s" fill="freeze"/></path>')
        t += rate
    return f'<g fill="{fill}">{"".join(out)}</g>', t + 0.12


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = lines[2][:width - 1].rstrip() + "…"
    return lines


def card(s, chains, theme, day, holdings):
    """The accession label: types itself out under the turntable render."""
    from notebook import ambient
    t = THEMES[theme]
    W, H = 840, 236
    n_res = sum(len(v) for v in chains.values())
    amb_d, amb_b = ambient("sd", W, H, theme, seed=day, cells=6, bits=10)
    body = [f'<defs>{amb_d}</defs>', amb_b]
    px, py, pw, ph = 24, 18, 792, 196
    ink = t["paper_ink"]
    body.append(f'<g transform="rotate(-0.5 {px + pw / 2} {py + ph / 2})">'
                f'<rect x="{px + 3}" y="{py + 4}" width="{pw}" height="{ph}" rx="3" fill="#000" opacity="0.2"/>'
                f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="3" fill="{t["paper"]}"/>'
                f'<rect x="{px}" y="{py}" width="8" height="{ph}" fill="{t["red"]}"/>'
                f'<line x1="{px + 28}" y1="{py + 42}" x2="{px + pw - 22}" y2="{py + 42}" stroke="{t["red"]}" stroke-width="1" opacity="0.55"/>')
    clock = 0.2
    svg, clock = typed_line("SPECIMEN OF THE DAY", "label", 13, px + 28, py + 28, ink, clock, tracking=1.6)
    body.append(svg)
    body.append(svg_text(f"{day} · 1 of {holdings:,} in the PDB", "text", 12, px + pw - 22, py + 28, ink, anchor="end", opacity=0.65))
    svg, clock = typed_line(s["id"], "wordmark", 56, px + 28, py + 112, ink, clock, rate=0.09)
    body.append(svg)
    x2 = px + 228
    y = py + 74
    for line in wrap(s.get("short") or s["title"], 46)[:2]:
        svg, clock = typed_line(line, "text", 18, x2, y, ink, clock, rate=0.01)
        body.append(svg)
        y += 24
    def clip(text, n):
        return text if len(text) <= n else text[:n - 1].rstrip() + "…"
    rows = []
    if s["organism"]:
        rows.append([("ORGANISM", clip(s["organism"], 58))])
    pair = []
    if s["method"]:
        res = f" · {s['resolution']:.2f} Å" if isinstance(s["resolution"], (int, float)) else ""
        pair.append(("METHOD", clip(s["method"] + res, 27)))
    if s["class"]:
        pair.append(("CLASS", clip(s["class"], 24)))
    rows.append(pair)
    pair = []
    if s["deposited"]:
        pair.append(("DEPOSITED", s["deposited"]))
    pair.append(("TRACED", f"{n_res:,} residues · {len(chains)} chain{'s' if len(chains) > 1 else ''}"))
    rows.append(pair)
    y = y + 8
    for row in rows:
        for j, (label, value) in enumerate(row):
            cx = x2 + 290 * j
            body.append(svg_text(label, "label", 10.5, cx, y, ink, opacity=0.55, tracking=1.2))
            svg, clock = typed_line(value, "text", 13.5, cx + 88, y, ink, clock)
            body.append(svg)
        y += 22
    body.append(f'<g opacity="0">{svg_text("tonight’s catch", "hand", 22, px + 120, py + ph - 20, "#1d3f8f", anchor="middle")}'
                f'<set attributeName="opacity" to="1" begin="{clock + 0.2:.2f}s" fill="freeze"/></g>')
    body.append("</g>")
    return svg_doc(W, H, "\n".join(body), f"Specimen of the day {day}: {s['id']}, {s.get('short') or s['title']}")


# ------------------------------------------------------------------ main

README_LIMIT = 480_000   # GitHub truncates READMEs past 500 KiB; keep a margin


def stl_budget(readme_text):
    """How many tube segments of today's model fit in the README alongside everything else."""
    import re as _re
    without = _re.sub(r"<!-- SPECIMEN:START -->.*?<!-- SPECIMEN:END -->", "", readme_text, flags=_re.S)
    room = README_LIMIT - len(without.encode()) - 5_000     # markup around the model
    return max(0, min(150, room // (8 * 108)))              # ~108 bytes a triangle, 8 a segment


def model(chains, budget=150):
    """Cartoon trace for GitHub's 3D viewer.

    Like a molecular-graphics cartoon: helices are smoothed onto their axis and
    drawn as fat cylinders, strands are straightened, loops stay thin. The trace
    is then downsampled and splined so the whole model fits `budget` segments.
    """
    from stl import Mesh
    from turntable import catmull, secondary_structure
    allp = np.vstack([np.asarray(v, float) for v in chains.values()])
    centre = allp.mean(axis=0)
    total = len(allp)
    sub = 2
    stride = max(1, math.ceil(total * sub / max(budget, 1)))
    radius = {"H": 2.3, "E": 1.5, "C": 0.75}
    m = Mesh()
    for pts in chains.values():
        ca = np.asarray(pts, float) - centre
        if len(ca) < 4:
            continue
        ss = secondary_structure(ca)
        smooth = ca.copy()
        for i in range(len(ca)):
            if ss[i] == "H":                      # the helix axis: mean of a 4-residue window
                lo, hi = max(0, i - 1), min(len(ca), i + 3)
                smooth[i] = ca[lo:hi].mean(axis=0)
            elif ss[i] == "E":                    # straighten the strand's zigzag
                lo, hi = max(0, i - 1), min(len(ca), i + 2)
                smooth[i] = ca[lo:hi].mean(axis=0)
        idx = list(range(0, len(ca), stride))
        if idx[-1] != len(ca) - 1:
            idx.append(len(ca) - 1)
        keep = smooth[idx]
        curve = catmull(keep, sub) if len(keep) > 2 else list(keep)
        rk = [radius[ss[i]] for i in idx]
        rads = [rk[min(k // sub, len(rk) - 1)] for k in range(len(curve))]
        rads = [(rads[max(k - 1, 0)] + 2 * rads[k] + rads[min(k + 1, len(rads) - 1)]) / 4 for k in range(len(rads))]
        m.tube([tuple(p) for p in curve], rads, sides=4)
    return m.ascii("specimen_cartoon")


def readme_block(s, day, holdings, stl, rendered):
    page = f"https://www.rcsb.org/structure/{s['id']}"
    alt = f"Specimen of the day: {esc(s['id'])}, {esc(s.get('short') or s['title'])}"
    hero = (f'<a href="{page}">{picture("specimen", alt + ", turning under the lights", width="100%", ext="webp", query="v=" + day)}</a>\n\n'
            if rendered else "")
    jar = (f'<sub>Grab it and turn it:</sub>\n\n```stl\n{stl}\n```\n') if stl else ""
    return (hero + f'<a href="{page}">{picture("specimen", alt, width="100%", query="v=" + day)}</a>\n\n' + jar)


def deliver(s, chains, day, holdings):
    for theme in THEMES:
        (ASSETS / f"specimen-{theme}.svg").write_text(card(s, chains, theme, day, holdings), encoding="utf-8")
    rendered = False
    try:
        from turntable import render, specimen_scene
        render("specimen", specimen_scene(chains), dist=4.2)
        rendered = True
    except Exception as e:  # noqa: BLE001 - the card still ships without the render
        print(f"::warning::turntable render failed, shipping the card only ({e})")
    from notebook import README
    budget = stl_budget(README.read_text(encoding="utf-8"))
    stl = model(chains, budget) if budget >= 40 else ""
    if stl:
        (ASSETS / "specimen.stl").write_text(stl + "\n", encoding="utf-8")
    else:
        print("::warning::README is near GitHub's size limit; skipping the 3D model tonight")
    return replace_block("SPECIMEN", readme_block(s, day, holdings, stl, rendered))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in Manila)")
    ap.add_argument("--id", help="use this PDB entry instead of a random one")
    args = ap.parse_args()
    day = args.date or now_manila().date().isoformat()

    try:
        ids = fetch(f"{DATA_API}/holdings/current/entry_ids")
    except RuntimeError as e:
        print(f"::warning::PDB unreachable, keeping yesterday's specimen ({e})")
        return
    picks = [args.id.upper()] if args.id else random.Random(f"specimen-{day}").sample(ids, min(CANDIDATES, len(ids)))
    for pdb_id in picks:
        try:
            s = describe(pdb_id)
            if not s:
                continue
            cif = coordinates(s["id"])
            chains = {c: np.array(v) for c, v in (backbone(cif) if cif else {}).items()}
        except RuntimeError as e:
            print(f"  skipped {pdb_id}: {e}")
            continue
        if not chains:
            print(f"  skipped {pdb_id}: no backbone to trace")
            continue
        changed = deliver(s, chains, day, len(ids))
        print(f"specimen {s['id']}: {s['short']} ({sum(len(v) for v in chains.values())} residues, "
              f"README {'updated' if changed else 'unchanged'})")
        return
    print("::warning::no usable specimen tonight, keeping yesterday's")


if __name__ == "__main__":
    sys.exit(main())
