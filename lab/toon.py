"""Cartoon ink kit for the DEXTER / XED README.

Shapes are flat fills ringed in near-black ink (union outlines: an ink copy stroked
at 2x under the fill), interior marks are tapered slivers (`fold`), one hard cel step
per form, and a fine gouache grain gathers at each fill's edges (the `grain` filter).
Light theme is DEXTER, dark theme is XED.
"""
import math

INK = "#0A0A12"

# Phoenix palette plus the lab spill. Gold is the shared mark of both themes.
PHOENIX = dict(
    bone="#F1E6D0", prussian="#16285C", navy="#0E1A3A", night="#0B1026", ink=INK,
    crimson="#B3122E", crimson_dk="#7A1020", oxblood="#5A0A18",
    phoenix="#FF5A1F", ember="#B8321A", gold="#FFC233", gold_sh="#E09A12", gold_dk="#A8650A", glint="#FFF1B8",
    spill="#A6FF2E", spill_dk="#4C9A0C", spill_hi="#E9FFB8",
)


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def P(pts):
    return " ".join(f"{f(x)},{f(y)}" for x, y in pts)


def catmull(pts, n=10, closed=False):
    out = []
    N = len(pts)
    rng = range(N) if closed else range(N - 1)
    for i in rng:
        p0 = pts[(i - 1) % N] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % N]
        p3 = pts[(i + 2) % N] if closed else pts[min(i + 2, N - 1)]
        for s in range(n):
            t = s / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)) + (i + t,))
    if not closed:
        out.append(tuple(pts[-1]) + (N - 1,))
    return out


def smooth(pts, n=10):
    """closed smooth curve through points"""
    s = catmull(pts, n, closed=True)
    return "M" + "L".join(f"{f(x)},{f(y)}" for x, y, _ in s) + "Z"


def rpoly(pts, r):
    """polygon with rounded corners; r may be a number or list"""
    N = len(pts)
    rs = r if isinstance(r, (list, tuple)) else [r] * N
    d = ""
    for i in range(N):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % N]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        rr = min(rs[i], l1 / 2, l2 / 2)
        a = (p1[0] + v1[0] / l1 * rr, p1[1] + v1[1] / l1 * rr)
        b = (p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr)
        d += ("M" if i == 0 else "L") + f"{f(a[0])},{f(a[1])}Q{f(p1[0])},{f(p1[1])} {f(b[0])},{f(b[1])}"
    return d + "Z"


def limb(pts, ws, cap0=True, cap1=True):
    """tapered tube along a smooth centre line"""
    s = catmull(pts, 12)
    L, R, nrm = [], [], []
    for i in range(len(s)):
        a, b = s[max(0, i - 1)], s[min(len(s) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        m = math.hypot(tx, ty) or 1
        tx, ty = tx / m, ty / m
        k = min(len(ws) - 2, int(s[i][2]))
        u = s[i][2] - k
        w = (ws[k] * (1 - u) + ws[k + 1] * u) / 2
        nrm.append((tx, ty, w))
        L.append((s[i][0] - ty * w, s[i][1] + tx * w))
        R.append((s[i][0] + ty * w, s[i][1] - tx * w))

    def cap(i, dr):
        tx, ty, w = nrm[i]
        c = s[i]
        o = []
        for j in range(1, 10):
            th = math.pi * j / 10
            nx, ny = -ty, tx
            o.append((c[0] + w * (nx * math.cos(th) + dr * tx * math.sin(th)), c[1] + w * (ny * math.cos(th) + dr * ty * math.sin(th))))
        return o
    c1 = cap(len(s) - 1, 1) if cap1 else []
    c0 = list(reversed(cap(0, -1))) if cap0 else []
    return "M" + "L".join(f"{f(x)},{f(y)}" for x, y in L + c1 + list(reversed(R)) + c0) + "Z"


def fold(pts, w, color=INK, op=1):
    """tapered sliver: swells to w mid-way, pointed ends"""
    s = catmull(pts, 12)
    n = len(s)
    L, R = [], []
    for i in range(n):
        a, b = s[max(0, i - 1)], s[min(n - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        m = math.hypot(tx, ty) or 1
        t = i / (n - 1)
        hw = max(0.2, w / 2 * math.sin(math.pi * t) ** 0.8)
        L.append((s[i][0] - ty / m * hw, s[i][1] + tx / m * hw))
        R.append((s[i][0] + ty / m * hw, s[i][1] - tx / m * hw))
    o = f' opacity="{op}"' if op != 1 else ""
    return f'<path d="M{P(L + list(reversed(R)))}Z" fill="{color}"{o}/>'


def inked(ds, fill, w, grain="grain", extra=""):
    """union outline: ink copies stroked at 2w under, fill on top (grained)"""
    if isinstance(ds, str):
        ds = [ds]
    under = "".join(f'<path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="{2*w}" stroke-linejoin="round"/>' for d in ds)
    top = "".join(f'<path d="{d}" fill="{fill}"/>' for d in ds)
    g = f' filter="url(#{grain})"' if grain else ""
    return f'{under}<g{g}>{top}{extra}</g>'


def clipped(cid, d, inner):
    return f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{inner}</g>'


def defs():
    return f'''
<filter id="grain" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="1" seed="5" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.05  0 0 0 0 0.04  0 0 0 0 0.12  0 -2.0 0 0 1.1" result="dk"/>
  <feGaussianBlur in="SourceAlpha" stdDeviation="5" result="b"/>
  <feComposite in="SourceAlpha" in2="b" operator="arithmetic" k1="0" k2="2.0" k3="-1.75" k4="0" result="w"/>
  <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.5 -1.0 -0.2 0 1.7" result="dw"/>
  <feComposite in="w" in2="dw" operator="arithmetic" k1="1.6" k2="0" k3="0.22" k4="0" result="wt"/>
  <feComposite in="wt" in2="SourceAlpha" operator="in" result="wm"/>
  <feComposite in="dk" in2="wm" operator="in" result="g"/>
  <feBlend in="g" in2="SourceGraphic" mode="multiply"/>
</filter>
<filter id="paper" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="9"/>
  <feColorMatrix values="0 0 0 0 .05  0 0 0 0 .04  0 0 0 0 .1  0 0 0 1.4 -.62"/>
</filter>
<filter id="chalk" x="-20%" y="-20%" width="140%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="2" seed="3" result="fine"/>
  <feDisplacementMap in="SourceGraphic" in2="fine" scale="7" xChannelSelector="R" yChannelSelector="G"/>
</filter>'''
