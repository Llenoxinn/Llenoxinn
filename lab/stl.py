"""A tiny mesh builder for the README's ```stl blocks (GitHub renders them in 3D).

Outward-facing triangles are guaranteed by orienting every face away from a
point known to be inside its solid. Coordinates are written with one decimal
to keep the README light.
"""
import math


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = math.sqrt(_dot(a, a)) or 1.0
    return _mul(a, 1 / n)


class Mesh:
    def __init__(self):
        self.tris = []

    def tri(self, a, b, c, inside):
        n = _cross(_sub(b, a), _sub(c, a))
        if _dot(n, _sub(_mul(_add(_add(a, b), c), 1 / 3), inside)) < 0:
            b, c, n = c, b, _mul(n, -1)
        self.tris.append((_unit(n), a, b, c))

    def quad(self, a, b, c, d, inside):
        self.tri(a, b, c, inside)
        self.tri(a, c, d, inside)

    def tube(self, pts, radius, sides=6, caps=True):
        """A tube along a polyline, with parallel-transported frames (no twisting).
        `radius` is a number or one radius per point."""
        if len(pts) < 2:
            return
        radii = list(radius) if hasattr(radius, "__iter__") else [radius] * len(pts)
        t0 = _unit(_sub(pts[1], pts[0]))
        ref = (0, 0, 1) if abs(t0[2]) < 0.9 else (1, 0, 0)
        nrm = _unit(_cross(t0, ref))
        rings = []
        for i, p in enumerate(pts):
            a = pts[max(0, i - 1)]
            b = pts[min(len(pts) - 1, i + 1)]
            t = _unit(_sub(b, a))
            nrm = _unit(_sub(nrm, _mul(t, _dot(nrm, t))))
            bi = _cross(t, nrm)
            rad = radii[i]
            rings.append([_add(p, _add(_mul(nrm, rad * math.cos(2 * math.pi * k / sides)),
                                       _mul(bi, rad * math.sin(2 * math.pi * k / sides)))) for k in range(sides)])
        for i in range(len(pts) - 1):
            mid = _mul(_add(pts[i], pts[i + 1]), 0.5)
            for k in range(sides):
                k2 = (k + 1) % sides
                self.quad(rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k], mid)
        if caps:
            for i, j in ((0, 1), (len(pts) - 1, len(pts) - 2)):
                inside = _add(pts[i], _mul(_sub(pts[j], pts[i]), 0.3))
                for k in range(1, sides - 1):
                    self.tri(rings[i][0], rings[i][k], rings[i][k + 1], inside)

    def octahedron(self, c, r):
        v = [_add(c, d) for d in ((r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0), (0, 0, r), (0, 0, -r))]
        for a in (0, 1):
            for b in (2, 3):
                for z in (4, 5):
                    self.tri(v[a], v[b], v[z], c)

    def bead(self, c, r):
        """Triangular bipyramid: 6 faces, reads as a bead at README scale."""
        eq = [_add(c, (r * math.cos(2 * math.pi * k / 3), r * math.sin(2 * math.pi * k / 3), 0)) for k in range(3)]
        for tip in (_add(c, (0, 0, r * 1.15)), _add(c, (0, 0, -r * 1.15))):
            for k in range(3):
                self.tri(eq[k], eq[(k + 1) % 3], tip, c)

    def slab(self, p, q, width, thick, up=(0, 0, 1)):
        along = _unit(_sub(q, p))
        up = _unit(_sub(up, _mul(along, _dot(up, along))))
        side = _cross(along, up)
        h, w = _mul(up, thick / 2), _mul(side, width / 2)
        cs = [_add(_add(o, _mul(h, a)), _mul(w, b)) for o in (p, q) for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        a0, a1, a2, a3, b0, b1, b2, b3 = cs
        mid = _mul(_add(p, q), 0.5)
        for f in ((a0, a1, a2, a3), (b0, b1, b2, b3), (a0, a1, b1, b0), (a1, a2, b2, b1), (a2, a3, b3, b2), (a3, a0, b0, b3)):
            self.quad(*f, mid)

    def ascii(self, name, scale=10, tilt=(32, 24)):
        """ASCII STL. Coordinates are scaled up and written as integers to keep the
        README light; GitHub's viewer fits the camera to the model, so scale is free.
        `tilt` pre-rotates the model (degrees about x, then z) so it already looks
        three-dimensional from the viewer's default camera, whichever axis that is."""
        ax, az = (math.radians(a) for a in tilt)

        def rot(v):
            x, y, z = v
            y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
            x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
            return (x, y, z)

        def f(v):
            return " ".join(str(int(round(x * scale))) for x in rot(v))

        def nf(x):
            return f"{x:.1f}".replace("-0.0", "0").replace(".0", "")
        out = [f"solid {name}"]
        for n, a, b, c in self.tris:
            n = rot(n)
            out.append(f"facet normal {nf(n[0])} {nf(n[1])} {nf(n[2])}\nouter loop\nvertex {f(a)}\nvertex {f(b)}\n"
                       f"vertex {f(c)}\nendloop\nendfacet")
        out.append(f"endsolid {name}")
        return "\n".join(out)
