"""Hand-drawn block letters for the gold gauntlets: D, E, X, T, R (enough for DEX, TER and,
turned over, XED). Drawn on a 100-unit-tall grid as polygons with holes, then extruded in
true 3D: every edge that faces the depth direction gets its own side face, shaded by which
way it points, under one ink outline. No font involved, so nothing about them can be
installed and copied.

Two cuts:
  "slab"   chamfered steel-plate letters, square and heavy (stamped lab hardware)
  "toon"   the same skeletons puffed and rounded, each letter bouncing off the baseline
           and leaning a few degrees (a 90s cartoon title card)
"""
import math
import random

from toon import INK, PHOENIX as C, clipped, f, fold, rpoly

# outer ring first, then holes; x from 0, y from 0 (top) to 100 (baseline)
GLYPHS = {
    "D": (80, [[(0, 0), (50, 0), (80, 26), (80, 74), (50, 100), (0, 100)],
               [(27, 25), (42, 25), (53, 35), (53, 65), (42, 75), (27, 75)]]),
    "E": (68, [[(0, 0), (68, 0), (68, 25), (28, 25), (28, 38), (60, 38), (60, 62), (28, 62), (28, 75), (68, 75), (68, 100), (0, 100)]]),
    "X": (86, [[(0, 0), (29, 0), (43, 26), (57, 0), (86, 0), (59, 50), (86, 100), (57, 100), (43, 74), (29, 100), (0, 100), (27, 50)]]),
    "T": (76, [[(0, 0), (76, 0), (76, 27), (51, 27), (51, 100), (25, 100), (25, 27), (0, 27)]]),
    "R": (80, [[(0, 0), (56, 0), (78, 18), (78, 44), (64, 57), (82, 100), (53, 100), (40, 63), (28, 63), (28, 100), (0, 100)],
               [(28, 22), (46, 22), (51, 27), (51, 37), (46, 42), (28, 42)]]),
}
GAP = 7


def _inside(pt, rings):
    x, y = pt
    c = False
    for ring in rings:
        n = len(ring)
        for i in range(n):
            (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c


def _ring_path(ring, r):
    return rpoly(ring, r) if r else "M" + " L".join(f"{f(x)},{f(y)}" for x, y in ring) + "Z"


def _place(rings, sc, ox, oy, rot, cx, cy):
    a = math.radians(rot)
    out = []
    for ring in rings:
        pts = []
        for x, y in ring:
            px, py = ox + x * sc, oy + y * sc
            dx, dy = px - cx, py - cy
            pts.append((cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)))
        out.append(pts)
    return out


def word(text, cx, cy, height, depth_vec, cut="slab", seed=1, face=None, side=None, under=None, uid="w"):
    """Draw `text` centred on (cx, cy), `height` px tall, extruded along depth_vec (px)."""
    face = face or C["glint"]
    side = side or C["gold_sh"]
    under = under or C["gold_dk"]
    tone_hi, tone_mid, tone_low = (("#FFFFFF", C["glint"], C["gold_sh"]) if face == C["glint"]
                                   else ("#FF8A98", "#C8193A", "#6E0E1E"))
    rnd = random.Random(seed)
    sc = height / 100
    total = sum(GLYPHS[ch][0] for ch in text) + GAP * (len(text) - 1)
    x = cx - total * sc / 2
    toon = cut == "toon"
    r = 9 * sc if toon else 2.5 * sc
    letters = []
    for ch in text:
        w, rings = GLYPHS[ch]
        bounce = rnd.uniform(-6, 6) * sc if toon else 0
        rot = rnd.uniform(-5, 5) if toon else 0
        placed = _place(rings, sc, x, cy - height / 2 + bounce, rot, x + w * sc / 2, cy)
        letters.append(placed)
        x += (w + GAP) * sc
    vx, vy = depth_vec
    sides, fronts = [], []
    for li, rings in enumerate(letters):
        for ring in rings:
            n = len(ring)
            for i in range(n):
                p, q = ring[i], ring[(i + 1) % n]
                ex, ey = q[0] - p[0], q[1] - p[1]
                ln = math.hypot(ex, ey) or 1
                nx, ny = ey / ln, -ex / ln
                mid = ((p[0] + q[0]) / 2 + nx * .6, (p[1] + q[1]) / 2 + ny * .6)
                if _inside(mid, rings):
                    nx, ny = -nx, -ny
                if nx * vx + ny * vy <= 0:
                    continue
                quad = [p, q, (q[0] + vx, q[1] + vy), (p[0] + vx, p[1] + vy)]
                # faces pointing up catch the light, faces pointing sideways sit in half shade
                col = C["glint"] if ny < -.5 else (side if abs(nx) > .5 else under)
                depth_key = -((p[0] + q[0]) / 2 * vx + (p[1] + q[1]) / 2 * vy)
                sides.append((depth_key, quad, col))
        d = " ".join(_ring_path(rg, r) for rg in rings)
        fronts.append(d)
    out = []
    # back plate: the whole extrusion silhouette in ink, so the side faces read as one solid
    for li, rings in enumerate(letters):
        for k in range(1, 7):
            t = k / 6
            out.append(f'<path d="{" ".join(_ring_path(rg, r) for rg in rings)}" transform="translate({f(vx * t)} {f(vy * t)})" '
                       f'fill="{INK}" fill-rule="evenodd" stroke="{INK}" stroke-width="{f(3.2 * sc * 2.2)}" stroke-linejoin="round"/>')
    for _, quad, col in sorted(sides, key=lambda s: s[0]):
        out.append(f'<path d="M{" L".join(f"{f(a)},{f(b)}" for a, b in quad)}Z" fill="{col}" stroke="{INK}" stroke-width="{f(1.6)}" stroke-linejoin="round"/>')
    sh, hl = 9 * sc, 4.4 * sc   # depth of the cel shadow (bottom-right) and the rim light (top-left)
    for i, d in enumerate(fronts):
        cid = f"lf{uid}{i}"
        letter = lambda dx, dy, col: f'<path d="{d}" transform="translate({f(dx)} {f(dy)})" fill="{col}" fill-rule="evenodd"/>'
        bevel = (f'<rect x="{f(cx - 400)}" y="{f(cy - height)}" width="800" height="{f(height * 2)}" fill="{tone_low}"/>'
                 + letter(-sh, -sh, tone_mid)               # the lit body, leaving a hard shadow along bottom-right edges
                 + letter(-sh, -sh, tone_hi)                # the rim light...
                 + letter(-sh + hl, -sh + hl, tone_mid))     # ...trimmed to a crescent along top-left edges
        out.append(f'<clipPath id="{cid}"><path d="{d}" clip-rule="evenodd"/></clipPath>'
                   f'<g clip-path="url(#{cid})"><g filter="url(#grain)">{bevel}</g></g>')
        out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{f(max(2.2, 4.2 * sc))}" stroke-linejoin="round"/>')
    # one shine on the first letter, where the light hits
    if letters:
        (x0, y0), = [min(letters[0][0], key=lambda p: p[0] + p[1])]
        out.append(fold([(x0 + 9 * sc, y0 + 22 * sc), (x0 + 9 * sc, y0 + 11 * sc), (x0 + 19 * sc, y0 + 8 * sc)], 4.6 * sc, "#FFFFFF", .85))
    return "".join(out)
