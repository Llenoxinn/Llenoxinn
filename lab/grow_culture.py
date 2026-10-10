#!/usr/bin/env python3
"""Grow this week's culture: assets/culture-{dark,light}.gif

A Gray-Scott reaction-diffusion culture filmed as it grows, seeded by the ISO
week in Manila, so the regime and pattern change every Monday.

    dA/dt = Da lap(A) - A B^2 + F (1 - A)
    dB/dt = Db lap(B) + A B^2 - (F + k) B

    python lab/grow_culture.py               # this week's culture
    python lab/grow_culture.py --seed hello  # any seed
"""
import argparse
import hashlib

import numpy as np
from PIL import Image

from notebook import ASSETS, LAB, now_manila, replace_block

GW, GH, SCALE = 220, 66, 3          # grid cells and pixels per cell -> 660 x 198
STEPS, HOLD = 5200, 14
SHOTS = sorted({int(30 * 1.105 ** i) for i in range(48)} | {STEPS - 1})   # dense early, sparse late
REGIMES = [("coral", 0.0545, 0.0620), ("mitosis", 0.0367, 0.0649), ("fingerprint", 0.0370, 0.0600),
           ("spots", 0.0300, 0.0620), ("maze", 0.0290, 0.0570)]
PALETTES = {"dark": ["#07020a", "#2a0410", "#8b0018", "#ff1f3d", "#ffd6dc"],
            "light": ["#ffffff", "#ffe3e7", "#ff5c72", "#c1001f", "#3d0010"]}


def lap(Z):
    v = np.roll(Z, 1, 0) + np.roll(Z, -1, 0)
    h = np.roll(Z, 1, 1) + np.roll(Z, -1, 1)
    col = v + Z
    return 0.05 * (col + np.roll(col, 1, 1) + np.roll(col, -1, 1)) + 0.15 * (v + h) - 1.05 * Z


def colour(v, stops):
    cols = np.array([[int(s[i:i + 2], 16) for i in (1, 3, 5)] for s in stops], np.float32)
    pos = np.linspace(0, 1, len(stops))
    return np.stack([np.interp(v, pos, cols[:, i]) for i in range(3)], -1).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed")
    args = ap.parse_args()
    if args.seed:
        seed = args.seed
    else:
        y, w, _ = now_manila().isocalendar()
        seed = f"{y}-W{w:02d}"
    digest = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    name, F, k = REGIMES[digest % len(REGIMES)]
    rng = np.random.default_rng(digest % 2 ** 63)
    A = np.ones((GH, GW), np.float32)
    B = np.zeros((GH, GW), np.float32)
    for _ in range(int(rng.integers(8, 16))):
        yy, xx, r = int(rng.integers(0, GH)), int(rng.integers(0, GW)), int(rng.integers(2, 5))
        A[max(0, yy - r):yy + r, max(0, xx - r):xx + r] = 0.5
        B[max(0, yy - r):yy + r, max(0, xx - r):xx + r] = 0.25
    B += (rng.random((GH, GW), dtype=np.float32)) * 0.01
    frames = []
    for s in range(STEPS):
        ab2 = A * B * B
        A += lap(A) - ab2 + F * (1 - A)
        B += 0.5 * lap(B) + ab2 - (k + F) * B
        if s in SHOTS:
            frames.append(np.clip(B / 0.40, 0, 1))
    frames += [frames[-1]] * HOLD
    for theme, stops in PALETTES.items():
        imgs = [Image.fromarray(colour(f, stops)).resize((GW * SCALE, GH * SCALE), Image.BICUBIC)
                .quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
        out = ASSETS / f"culture-{theme}.gif"
        imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=90, loop=0, optimize=True, disposal=1)
        print(f"wrote {out.name} ({out.stat().st_size // 1024} KB, {len(imgs)} frames)")
    from notebook import picture
    replace_block("CULTURE", (
        f'{picture("culture", f"Gray-Scott culture, {name} regime, growing", width="100%", ext="gif", query="v=" + seed)}\n\n'
        f'<sub><b>Fig. 2</b> This week\'s culture · Gray-Scott, <i>{name}</i> regime · re-plated every Monday</sub>'))


if __name__ == "__main__":
    main()
