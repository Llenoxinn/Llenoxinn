"""Colour turntable renders for the lab's 3D specimens.

Python builds a scene of spheres and capsules from the data; the Rust ray
tracer in lab/render3d renders it from a camera that circles the specimen;
Pillow packs the frames into a looping animated WebP per theme.

    from turntable import render, specimen_scene, plasmid_scene, spindle_scene
    render("plasmid", plasmid_scene(weeks))      # -> assets/plasmid-{dark,light}.webp
"""
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from notebook import ASSETS, ROOT, THEMES

CRATE = ROOT / "lab" / "render3d"
BINARY = CRATE / "target" / "release" / "render3d"
BASE_COLOURS = {"A": "#3fb950", "C": "#58a6ff", "G": "#ffb02e", "T": "#ff1f3d"}
PAIR = {"A": "T", "T": "A", "C": "G", "G": "C"}
# Scenes are shared by both renders; their lights use each theme's own accent.
SCENE_ACCENT = THEMES["dark"]["glow"]
SCENE_HIGHLIGHT = THEMES["dark"]["pen"]


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _mix(a, b, f):
    return tuple(x + (y - x) * f for x, y in zip(a, b))


def sphere(c, r, colour, emit=0.0):
    return ("s", tuple(c), r, _rgb(colour) if isinstance(colour, str) else colour, emit)


def capsule(a, b, r, colour, emit=0.0):
    return ("c", tuple(a) + tuple(b), r, _rgb(colour) if isinstance(colour, str) else colour, emit)


# ------------------------------------------------------------------ rendering

def ensure_binary():
    if not BINARY.exists():
        subprocess.run(["cargo", "build", "--release", "--quiet", "--manifest-path", str(CRATE / "Cargo.toml")], check=True)
    return BINARY


def render(name, prims, frames=48, fps=12, size=(760, 440), ss=2, elev=18, dist=3.2, fov=30, quality=78):
    """Render prims to assets/{name}-{dark,light}.webp. Returns the output paths.

    The camera moves every frame, so file size follows the frame count: 48 frames at
    12 fps keeps the 4 s turn at about 60% of the weight of 72 at 18 (around 0.4-0.8 MB
    each). That is what every visitor downloads, and what every nightly commit adds.
    """
    binary = ensure_binary()
    work = Path(tempfile.mkdtemp(prefix=f"render-{name}-"))
    try:
        lines = [f"size {size[0]} {size[1]}", f"frames {frames}", f"ss {ss}", f"fov {fov}", f"elev {elev}", f"dist {dist}"]
        for theme, t in THEMES.items():
            lines.append(f"page {theme} " + " ".join(f"{v:.4f}" for v in _rgb(t['bg'])))
            lines.append(f"accent {theme} " + " ".join(f"{v:.4f}" for v in _rgb(t['red'])))
        for kind, geo, r, col, emit in prims:
            lines.append(f"{kind} " + " ".join(f"{v:.2f}" for v in geo) + f" {r:.3f} " +
                         " ".join(f"{v:.3f}" for v in col) + f" {emit:.2f}")
        scene = work / "scene.txt"
        scene.write_text("\n".join(lines) + "\n")
        subprocess.run([str(binary), str(scene), str(work)], check=True)
        outs = []
        for theme in THEMES:
            imgs = [Image.open(work / f"{theme}-{f:03d}.ppm").convert("RGB") for f in range(frames)]
            out = ASSETS / f"{name}-{theme}.webp"
            imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=round(1000 / fps), loop=0,
                         quality=quality, method=4)
            outs.append(out)
            print(f"  rendered {out.name} ({out.stat().st_size // 1024} KB, {frames} frames)")
        return outs
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ------------------------------------------------------------------ specimen: cartoon from a Cα trace

def secondary_structure(ca):
    """Per-residue H (helix), E (strand) or C (coil), from Cα geometry alone."""
    n = len(ca)
    ss = ["C"] * n
    d = lambda i, j: float(np.linalg.norm(ca[i] - ca[j]))
    for i in range(n - 4):
        if 4.6 < d(i, i + 3) < 5.8 and 5.6 < d(i, i + 4) < 6.9:
            for k in range(i, i + 5):
                ss[k] = "H"
    for i in range(1, n - 2):
        if ss[i] == "C" and d(i - 1, i + 1) > 6.1 and d(i, i + 2) > 6.1:
            ss[i] = "E"
    # strands need a run of 3 to count
    i = 0
    while i < n:
        if ss[i] == "E":
            j = i
            while j < n and ss[j] == "E":
                j += 1
            if j - i < 3:
                for k in range(i, j):
                    ss[k] = "C"
            i = j
        else:
            i += 1
    return ss


def catmull(points, sub):
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for s in range(sub):
            t = s / sub
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(points[-1])
    return out


RAINBOW = ["#4f7dff", "#2ec5ff", "#2ee6a6", "#a6f04a", "#ffd23f", "#ff8a3d", "#ff1f3d"]


def rainbow(f):
    f = min(max(f, 0.0), 1.0) * (len(RAINBOW) - 1)
    i = min(int(f), len(RAINBOW) - 2)
    return _mix(_rgb(RAINBOW[i]), _rgb(RAINBOW[i + 1]), f - i)


def specimen_scene(chains):
    """Cartoon-style trace: fat tubes for helices, medium for strands, thin coil, N→C rainbow per chain."""
    allp = np.vstack([np.asarray(v, float) for v in chains.values()])
    centre = allp.mean(axis=0)
    _, _, vt = np.linalg.svd(allp - centre, full_matrices=False)
    prims = []
    radius = {"H": 2.2, "E": 1.5, "C": 0.7}
    for pts in chains.values():
        ca = (np.asarray(pts, float) - centre) @ vt.T            # longest axis horizontal
        ca = ca[:, [0, 2, 1]]                                     # y up = third axis
        if len(ca) < 4:
            continue
        ss = secondary_structure(ca)
        sub = 3
        curve = catmull(ca, sub)
        rad = np.array([radius[s] for s in ss], float)
        rad = np.convolve(np.pad(rad, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")   # soften ends
        n = len(curve)
        for k in range(n - 1):
            i = min(k // sub, len(ca) - 1)
            f = k / max(n - 2, 1)
            prims.append(capsule(curve[k], curve[k + 1], float(rad[i]), rainbow(f)))
    return prims


# ------------------------------------------------------------------ plasmid: the year as supercoiled DNA

def handle_bases():
    return "".join("ACGT"[(b >> s) & 3] for b in "Llenoxinn".encode() for s in (6, 4, 2, 0))


def plasmid_path(u, n, rc=46.0):
    """A ring with a saddle writhe, so it reads as 3D from every side."""
    phi = 2 * math.pi * u / n
    rr = rc * (1 + 0.08 * math.cos(3 * phi))
    return np.array([rr * math.cos(phi), 9.0 * math.sin(2 * phi), rr * math.sin(phi)])


def plasmid_frame(u, n):
    p = plasmid_path(u, n)
    t = plasmid_path(u + 0.01, n) - plasmid_path(u - 0.01, n)
    t /= np.linalg.norm(t)
    radial = np.array([p[0], 0.0, p[2]])
    radial /= np.linalg.norm(radial)
    nrm = radial - t * radial.dot(t)
    nrm /= np.linalg.norm(nrm)
    return p, nrm, np.cross(t, nrm)


def plasmid_scene(weeks, turns=5, R=9.0):
    n = len(weeks)
    peak = max(weeks) or 1
    bases = handle_bases()
    groove = math.radians(150)
    prims = []

    def strand_point(u, ph):
        p, nr, bi = plasmid_frame(u, n)
        th = ph + 2 * math.pi * turns * u / n
        return p + R * (math.cos(th) * nr + math.sin(th) * bi)
    for ph, col in ((0.0, "#e8eef5"), (groove, "#b9c7d6")):
        pts = [strand_point(k / 3, ph) for k in range(3 * n + 1)]
        for a, b in zip(pts, pts[1:]):
            prims.append(capsule(a, b, 1.25, col))
        for u in range(n):
            prims.append(sphere(strand_point(u, ph), 1.9, "#ffb02e"))
    for u, c in enumerate(weeks):
        a, b = strand_point(u, 0.0), strand_point(u, groove)
        mid = (a + b) / 2
        base = bases[u % len(bases)]
        da, db = (mid - a), (mid - b)
        prims.append(capsule(a + da * 0.12, mid - da * 0.06, 1.05, BASE_COLOURS[base]))
        prims.append(capsule(b + db * 0.12, mid - db * 0.06, 1.05, BASE_COLOURS[PAIR[base]]))
        if c:
            p, nr, bi = plasmid_frame(u, n)
            size = 2.4 + 4.2 * math.sqrt(c / peak)
            core = mid + nr * (R + size * 0.9)
            prims.append(sphere(core, size, SCENE_ACCENT, 0.9))
            for k in range(3):
                ang = 2 * math.pi * k / 3 + u
                prims.append(sphere(core + size * 0.75 * (math.cos(ang) * bi + math.sin(ang) * nr * 0.6 + 0.3 * nr),
                                    size * 0.62, SCENE_HIGHLIGHT, 0.6))
    return prims


# ------------------------------------------------------------------ spindle: metaphase in colour

def spindle_scene(langs, seed=7):
    import random
    rng = random.Random(seed)
    items = list(langs.items())[:10]
    if not items:
        return []
    biggest = items[0][1]["bytes"] or 1
    n = len(items)
    RP, POLE, LMAX = 26.0, 46.0, 34.0
    prims = []
    for i, (name, v) in enumerate(items):
        base = _rgb(v["color"] or "#8b949e")
        L = 12 + (LMAX - 12) * math.sqrt(v["bytes"] / biggest)
        phi = 2 * math.pi * i / n
        ur = np.array([math.cos(phi), 0.0, math.sin(phi)])
        tilt = rng.uniform(-0.35, 0.35)
        d = np.array([ur[0] * math.cos(tilt), math.sin(tilt), ur[2] * math.cos(tilt)])
        c = RP * ur
        p_len, q_len = 0.38 * L, 0.62 * L
        bounds, acc = [], 0
        for _, b in v["repos"]:
            acc += b / v["bytes"]
            bounds.append(-p_len + acc * L)
        segs = max(10, int(10 + 14 * L / LMAX))
        for side in (-1, 1):
            pts, rads, cols = [], [], []
            for k in range(segs + 1):
                s_ = -p_len + L * k / segs
                arm = p_len if s_ < 0 else q_len
                f = min(1.0, abs(s_) / arm)
                y = side * (1.0 + 1.6 * f)
                pts.append(c + d * s_ + np.array([0.0, y, 0.0]))
                r = 1.6 * math.sqrt(max(0.0, 1 - f ** 6)) * (1 - 0.5 * math.exp(-(s_ / 1.6) ** 2))
                rads.append(max(r, 0.35))
                band = next((j for j, bnd in enumerate(bounds) if s_ <= bnd), len(bounds) - 1)
                cols.append(_mix(base, (0.05, 0.05, 0.07), 0.45) if band % 2 else _mix(base, (1, 1, 1), 0.12))
            for k in range(segs):
                prims.append(capsule(pts[k], pts[k + 1], (rads[k] + rads[k + 1]) / 2, cols[k]))
            kin = c + np.array([0.0, side * 1.0, 0.0])
            prims.append(sphere(kin, 0.9, "#ffffff", 0.7))
            prims.append(capsule(np.array([0.0, side * POLE, 0.0]), kin, 0.16, SCENE_HIGHLIGHT, 0.75))
    for side in (-1, 1):
        pole = np.array([0.0, side * POLE, 0.0])
        prims.append(sphere(pole, 2.8, SCENE_ACCENT, 1.0))
        for k in range(10):
            a = 2 * math.pi * k / 10 + 0.3
            tip = pole + np.array([13 * math.cos(a), side * 10.0, 13 * math.sin(a)])
            prims.append(capsule(pole, tip, 0.12, SCENE_HIGHLIGHT, 0.7))
    return prims
