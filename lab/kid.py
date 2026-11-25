"""Dexter as a cartoon: the approved character (Gate 1, Nov 25 2026).

His real features in the late-90s TV-cartoon construction: a black warrior cut
(spiky textured top, chunky fringe locks), thick half-rim browline glasses, crimson
welding gauntlets, a rolled-sleeve bone lab coat with a phoenix patch. Never the
show's character: no orange hair, no purple gloves, no pale-blue rectangle lenses.

DEXTER (light) scowls with half-lidded eyes and a smirk, lit from the top left.
XED (dark) cocks one brow, grins, cracks a lens, sets his fringe smoking, spills
acid on the coat, and is lit from below by fire.

Drawn in a 600 x 700 local box, head centred on x 300. `kid(xed, uid)` draws the
standing sheet pose; `head(xed, uid)` is reusable for other poses.
"""
import math
import random

from toon import INK, PHOENIX as C, clipped, f, fold, inked, limb, rpoly, smooth

SKIN, SKIN_D, SKIN_COOL = "#E3AD84", "#B97A55", "#9A6458"
HAIR, HAIR_HI = "#1A1620", "#4A5578"
COAT, COAT_SH = "#FBF6EA", "#D6CDBA"
NAVY, CRIM, CRIM_D = C["navy"], C["crimson"], C["crimson_dk"]
GOLD, ORANGE, SPILL = C["gold"], C["phoenix"], C["spill"]
GLASS = "#CFE6EA"

HEAD = [(198, 140), (402, 140), (438, 232), (420, 316), (354, 356), (246, 356), (180, 316), (162, 232)]
HEAD_D = rpoly(HEAD, 40)


def hair_back():
    pts = [(156, 236), (154, 168), (184, 112), (208, 70), (236, 90), (258, 52), (288, 80), (318, 44), (340, 76),
           (374, 54), (384, 92), (420, 104), (446, 168), (444, 236), (426, 240), (420, 186), (300, 168), (180, 186), (174, 240)]
    return rpoly(pts, [6, 30, 30, 4, 8, 4, 8, 4, 8, 4, 8, 30, 30, 6, 4, 20, 20, 20, 4])


def fringe(xed):
    pts = [(166, 180), (172, 212), (190, 186), (200, 220), (222, 186), (238, 224), (258, 184), (276, 214),
           (298, 180), (318, 222), (336, 184), (356, 210), (376, 180), (396, 200), (412, 176), (430, 190), (436, 164),
           (386, 128), (300, 116), (214, 128)]
    if xed:  # singed tuft: one lock burnt short and frizzed upward
        pts[8] = (302, 190)
        pts[9] = (314, 200)
    return rpoly(pts, [4, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 6, 2, 4, 30, 30, 30])


def lens_path(cx):
    return rpoly([(cx - 54, 222), (cx + 54, 222), (cx + 50, 266), (cx + 32, 284), (cx - 32, 284), (cx - 50, 266)], [4, 4, 16, 14, 14, 16])


def spiderweb(ix, iy, seed):
    """Impact crack: kinked radial lines plus broken rings around the hit."""
    rnd = random.Random(seed)
    s = []
    for i in range(9):
        a = i / 9 * math.tau + rnd.uniform(-.2, .2)
        pts, r = [(ix, iy)], 0
        while r < 80:
            r += rnd.uniform(12, 22)
            a2 = a + rnd.uniform(-.18, .18)
            pts.append((ix + math.cos(a2) * r, iy + math.sin(a2) * r))
        s.append("M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts))
    for rr in (9, 19, 31):
        for i in range(6):
            if rnd.random() < .7:
                a0 = i / 6 * math.tau + rnd.uniform(0, .3)
                a1 = a0 + rnd.uniform(.5, .9)
                s.append(f"M{f(ix + math.cos(a0) * rr)},{f(iy + math.sin(a0) * rr)} L{f(ix + math.cos(a1) * rr)},{f(iy + math.sin(a1) * rr)}")
    d = " ".join(s)
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width=".9" opacity=".75" transform="translate(1.2 -.8)"/>')


def hole(cx, cy, r, seed):
    rnd = random.Random(seed)
    pts = []
    for i in range(16):
        a = i / 16 * math.tau
        rr = r * (rnd.uniform(.55, 1.0) if i % 2 else rnd.uniform(.95, 1.3))
        pts.append((cx + math.cos(a) * rr * 1.15, cy + math.sin(a) * rr))
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + "Z"


def shard(x, y, sc, rot):
    d = f"M{f(x)},{f(y)} l{f(10 * sc)},{f(-14 * sc)} l{f(8 * sc)},{f(16 * sc)} l{f(-12 * sc)},{f(6 * sc)}z"
    return (f'<g transform="rotate({rot} {f(x)} {f(y)})"><path d="{d}" fill="{GLASS}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
            + fold([(x + 4 * sc, y - 4 * sc), (x + 9 * sc, y - 10 * sc)], 2, "#FFFFFF") + "</g>")


def glasses(xed):
    s = []
    if not xed:
        for sx in (-1, 1):
            cx = 300 + sx * 58
            lens = lens_path(cx)
            s.append(f'<path d="{lens}" fill="{GLASS}" opacity=".28"/>')
            s.append(f'<path d="{lens}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
            s.append(fold([(cx + 26, 226), (cx + 36, 240), (cx + 40, 256)], 3.6, "#FFFFFF", .85))
        lb = rpoly([(182, 206), (296, 224), (296, 242), (184, 226)], 7)
        rb = rpoly([(304, 224), (418, 206), (416, 226), (304, 242)], 7)
        s.append(f'<path d="{lb}" fill="{INK}"/><path d="{rb}" fill="{INK}"/>')
        s.append(fold([(196, 204), (240, 210), (284, 218)], 2.4, HAIR_HI, .9))
        s.append(f'<path d="M292,222 Q300,216 308,222" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
        s.append(f'<path d="M186,210 L166,228" stroke="{INK}" stroke-width="6" stroke-linecap="round"/><path d="M414,210 L434,228" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
        return "".join(s)
    # XED: knocked crooked, one lens spider-webbed, the other blown out, bridge snapped and taped
    s.append('<g transform="rotate(-6 300 230)">')
    ll, rl = lens_path(242), lens_path(358)
    s.append(f'<path d="{ll}" fill="{GLASS}" opacity=".3"/>')
    s.append(clipped("webL", ll, spiderweb(222, 246, 3)))
    s.append(f'<path d="{ll}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
    # right lens: a jagged hole where the glass used to be, cracks running out from it
    hd = hole(362, 252, 24, 8)
    s.append(f'<path d="{rl} {hd}" fill="{GLASS}" fill-rule="evenodd" opacity=".34"/>')
    s.append(f'<clipPath id="webR"><path d="{rl} {hd}" clip-rule="evenodd"/></clipPath>'
             f'<g clip-path="url(#webR)">{spiderweb(362, 252, 11).replace(chr(34) + "2" + chr(34), chr(34) + "1.7" + chr(34), 1)}</g>')
    s.append(f'<path d="{hd}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
    s.append(f'<path d="{hd}" fill="none" stroke="#FFFFFF" stroke-width="1" opacity=".8" transform="translate(1.4 1.2)"/>')
    # the rim popped open at the bottom corner
    s.append(f'<path d="{rl}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round" stroke-dasharray="210 26 400"/>')
    # brow bars: left cocked up, right cracked through with a gap
    lb = rpoly([(182, 200), (296, 206), (296, 224), (184, 220)], 7)
    rb1 = rpoly([(304, 200), (352, 194), (348, 214), (304, 220)], 5)
    rb2 = rpoly([(360, 190), (418, 182), (416, 202), (356, 210)], 5)
    s.append(f'<path d="{lb}" fill="{INK}"/><path d="{rb1}" fill="{INK}"/><path d="{rb2}" fill="{INK}" transform="rotate(7 360 200)"/>')
    s.append(f'<path d="M350,192 l6,6 l-5,5 l6,7" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    # bridge snapped and wrapped in white tape
    s.append(f'<path d="M292,216 Q300,210 308,216" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    s.append(f'<g transform="rotate(-14 300 214)"><rect x="288" y="202" width="24" height="22" rx="3" fill="#F4EFE2" stroke="{INK}" stroke-width="3"/>'
             f'<path d="M294,204 v18 M300,203 v20 M306,204 v18" stroke="#C9BFA8" stroke-width="1.6"/></g>')
    # left arm fine, right arm snapped: a stub at the hinge, the rest dangling by the ear
    s.append(f'<path d="M186,206 L166,224" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    s.append(f'<path d="M414,192 L424,198" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    s.append("</g>")
    s.append(f'<path d="M438,236 L446,270" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    # shards falling past the cheek
    s.append(shard(392, 300, 1, 20) + shard(408, 336, .7, -30) + shard(376, 352, .55, 60))
    return "".join(s)


def eyes(xed, uid):
    s = []
    for sx in (-1, 1):
        cx, cy = 300 + sx * 58, 252
        if not xed:
            # half-lidded scowl: flat lid slanting down toward the nose
            top_out, top_in = (cx - sx * 28, cy - 13), (cx + sx * 26, cy + 1)
            d = f"M{f(top_out[0])},{f(top_out[1])} L{f(top_in[0])},{f(top_in[1])} Q{cx + sx * 24},{cy + 20} {cx},{cy + 20} Q{cx - sx * 28},{cy + 20} {f(top_out[0])},{f(top_out[1])}Z"
            pr, px, py = 10.5, cx + 7 - sx * 2, cy + 2
        else:
            big = sx > 0
            rx, ry = (30, 28) if big else (26, 23)
            d = f"M{cx - rx},{cy} a{rx},{ry} 0 1 0 {2 * rx},0 a{rx},{ry} 0 1 0 {-2 * rx},0Z"
            pr, px, py = (5.5 if big else 6.5), cx - sx * 6, cy + 2
        cid = f"eye{uid}{sx}"
        s.append(f'<path d="{d}" fill="#FFFFFF"/>')
        s.append(clipped(cid, d, f'<circle cx="{px}" cy="{py}" r="{pr}" fill="{INK}"/><circle cx="{px + 3}" cy="{py - 3}" r="2.6" fill="#FFFFFF"/>'
                         f'<path d="M{cx - 40},{cy + 14} Q{cx},{cy + 4} {cx + 40},{cy + 14} V{cy + 40} H{cx - 40}Z" fill="#D8E2EE"/>'))
        s.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linejoin="round"/>')
        if not xed:
            s.append(fold([top_out, ((top_out[0] + top_in[0]) / 2, (top_out[1] + top_in[1]) / 2 - 1.5), top_in], 6))
    return "".join(s)


def mouth(xed):
    if not xed:  # set jaw, one-sided smirk
        return (fold([(258, 318), (290, 322), (322, 318), (342, 306)], 5.2)
                + fold([(338, 300), (346, 306), (344, 314)], 2.6))
    m = "M246,304 Q300,312 356,298 Q350,336 302,342 Q258,340 246,304Z"
    return (f'<path d="{m}" fill="#5A0A18" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M252,308 Q300,316 350,303 L346,316 Q300,326 256,318Z" fill="#FFFFFF"/>'
            f'<path d="M274,334 Q300,322 326,332 Q312,342 300,342 Q284,341 274,334Z" fill="#E8556A"/>'
            f'<path d="{m}" fill="none" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            + fold([(240, 300), (246, 306), (244, 316)], 2.6) + fold([(358, 292), (356, 300), (362, 308)], 2.6))


def face_shade(xed, cid):
    if not xed:  # key light top-left: one hard cel step on the right side and under the fringe
        sh = smooth([(392, 150), (470, 150), (470, 380), (330, 380), (382, 320), (404, 250)])
        fr = rpoly([(160, 194), (180, 226), (198, 200), (212, 234), (230, 200), (246, 238), (266, 198), (284, 228),
                    (306, 194), (326, 236), (344, 198), (364, 224), (384, 194), (404, 214), (440, 190), (440, 150), (160, 150)], 4)
        inner = f'<path d="{sh}" fill="{SKIN_D}"/><path d="{fr}" fill="{SKIN_D}"/>'
    else:  # fire from below: cool shadow over the upper face, orange rim on the jaw
        cool = smooth([(140, 120), (460, 120), (460, 262), (404, 282), (340, 270), (300, 292), (250, 276), (196, 290), (140, 268)])
        inner = (f'<path d="{cool}" fill="#9A6458"/>'
                 + fold([(176, 306), (226, 344), (300, 356), (374, 344), (424, 306)], 9, ORANGE)
                 + fold([(176, 300), (168, 262)], 5, ORANGE))
    return clipped(cid, HEAD_D, inner)


def norm(v):
    m = math.hypot(*v)
    return (v[0] / m, v[1] / m)


def quad(a, b, n, wa, wb, r=8):
    return rpoly([(a[0] + n[0] * wa, a[1] + n[1] * wa), (b[0] + n[0] * wb, b[1] + n[1] * wb),
                  (b[0] - n[0] * wb, b[1] - n[1] * wb), (a[0] - n[0] * wa, a[1] - n[1] * wa)], r)


def arm(sx, xed, uid):
    """akimbo arm in front of the coat: sleeve to the elbow, rolled cuff, forearm, welding gauntlet, fist on hip"""
    s = []
    sh, el, wr = (300 + sx * 74, 392), (300 + sx * 158, 470), (300 + sx * 108, 532)
    d = norm((wr[0] - el[0], wr[1] - el[1]))
    n = (-d[1], d[0])
    fa = limb([el, wr], [32, 27])
    s.append(inked(fa, SKIN, 3, extra=clipped(f"fa{uid}{sx}", fa,
             f'<path d="{quad((el[0] + n[0] * sx * 10, el[1] + n[1] * sx * 10), (wr[0] + n[0] * sx * 8, wr[1] + n[1] * sx * 8), n, 9, 8, 1)}" fill="{SKIN_COOL if xed else SKIN_D}"/>')))
    # rolled cuff band around the elbow
    c0 = (el[0] - d[0] * 16, el[1] - d[1] * 16)
    c1 = (el[0] + d[0] * 8, el[1] + d[1] * 8)
    s.append(inked(quad(c0, c1, n, 30, 27, 9), COAT, 3))
    m = ((c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2)
    s.append(fold([(m[0] + n[0] * 22, m[1] + n[1] * 22), (m[0], m[1] + 2), (m[0] - n[0] * 22, m[1] - n[1] * 22)], 2.4, "#A89C84"))
    # welding gauntlet, flared toward the elbow
    g0 = (wr[0] - d[0] * 38, wr[1] - d[1] * 38)
    g1 = (wr[0] + d[0] * 4, wr[1] + d[1] * 4)
    gaunt = quad(g0, g1, n, 29, 19, 8)
    s.append(inked(gaunt, CRIM, 3.2, extra=clipped(f"ga{uid}{sx}", gaunt,
             f'<path d="{quad((g0[0] - n[0] * sx * 16, g0[1] - n[1] * sx * 16), (g1[0] - n[0] * sx * 12, g1[1] - n[1] * sx * 12), n, 14, 10, 1)}" fill="{CRIM_D}"/>')))
    s.append(fold([(g0[0] + n[0] * sx * 18 + d[0] * 8, g0[1] + n[1] * sx * 18 + d[1] * 8),
                   (g1[0] + n[0] * sx * 11 - d[0] * 4, g1[1] + n[1] * sx * 11 - d[1] * 4)], 3.4, "#FF7A8C", .9))
    s.append(fold([(g0[0] + n[0] * 27 + d[0] * 9, g0[1] + n[1] * 27 + d[1] * 9),
                   (g0[0] - n[0] * 27 + d[0] * 9, g0[1] - n[1] * 27 + d[1] * 9)], 2.6, CRIM_D))
    # fist planted on the hip
    fc = (wr[0] + d[0] * 16 - sx * 6, wr[1] + d[1] * 16)
    fist = rpoly([(fc[0] - 22, fc[1] - 18), (fc[0] + 22, fc[1] - 18), (fc[0] + 24, fc[1] + 16), (fc[0] - 24, fc[1] + 18)], 12)
    s.append(inked(fist, CRIM, 3.2, extra=clipped(f"fi{uid}{sx}", fist,
             f'<path d="M{fc[0] - 40},{fc[1] + 6} L{fc[0] + 40},{fc[1] + 2} V{fc[1] + 40} H{fc[0] - 40}Z" fill="{CRIM_D}"/>')))
    for k in range(3):
        y = fc[1] - 10 + k * 10
        s.append(fold([(fc[0] - sx * 22, y), (fc[0] - sx * 13, y + 1), (fc[0] - sx * 5, y)], 2.4))
    s.append(fold([(fc[0] + sx * 6, fc[1] - 12), (fc[0] + sx * 14, fc[1] - 2), (fc[0] + sx * 8, fc[1] + 8)], 2.6))
    return "".join(s)


SPILL_DK, SPILL_HI = C["spill_dk"], C["spill_hi"]


def splat(cx, cy, r, seed, drips=2, run=1.0):
    """Acid splash: a lumpy blob, runs that drip downward and end in a hanging drop,
    satellite droplets thrown outward, one hard shadow step and a wet highlight."""
    rnd = random.Random(seed)
    n = 11
    pts = [(cx + math.cos(i / n * math.tau) * r * rnd.uniform(.62, 1.15),
            cy + math.sin(i / n * math.tau) * r * rnd.uniform(.55, 1.0)) for i in range(n)]
    blob = smooth(pts)
    runs = []
    for k in range(drips):
        x = cx + rnd.uniform(-.6, .6) * r
        ln = rnd.uniform(.9, 2.0) * r * run
        wd = rnd.uniform(.18, .3) * r
        runs.append(f"M{f(x - wd)},{f(cy)} V{f(cy + ln)} a{f(wd)},{f(wd)} 0 0 0 {f(2 * wd)},0 V{f(cy)}Z")
        runs.append(f"M{f(x)},{f(cy + ln + wd * 1.6)} m{f(-wd * .8)},0 a{f(wd * .8)},{f(wd * .9)} 0 1 0 {f(wd * 1.6)},0 a{f(wd * .8)},{f(wd * .9)} 0 1 0 {f(-wd * 1.6)},0")
    dots = []
    for k in range(rnd.randint(3, 5)):
        a = rnd.uniform(0, math.tau)
        d = r * rnd.uniform(1.3, 1.9)
        rr = r * rnd.uniform(.08, .16)
        dots.append(f"M{f(cx + math.cos(a) * d - rr)},{f(cy + math.sin(a) * d * .8)} a{f(rr)},{f(rr)} 0 1 0 {f(2 * rr)},0 a{f(rr)},{f(rr)} 0 1 0 {f(-2 * rr)},0")
    shapes = [blob] + runs + dots
    under = "".join(f'<path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="5.6" stroke-linejoin="round"/>' for d in shapes)
    top = "".join(f'<path d="{d}" fill="{SPILL}"/>' for d in shapes)
    shade = f'<path d="M{f(cx - r * 1.4)},{f(cy + r * .25)} Q{f(cx)},{f(cy + r * .55)} {f(cx + r * 1.4)},{f(cy + r * .1)} V{f(cy + r * 3 * run)} H{f(cx - r * 1.4)}Z" fill="{SPILL_DK}" opacity=".55"/>'
    hi = fold([(cx - r * .55, cy - r * .3), (cx - r * .2, cy - r * .55), (cx + r * .2, cy - r * .5)], max(2.2, r * .16), SPILL_HI)
    return f'{under}<g filter="url(#grain)">{top}{clipped(f"sp{seed}", blob, shade)}</g>{hi}'


def body(xed, uid):
    s = []
    for sx in (-1, 1):
        lx = 300 + sx * 46
        s.append(inked(limb([(lx, 590), (lx + sx * 2, 640)], [34, 30]), "#121C3E", 3))
        ox = lx + sx * 10
        sh = rpoly([(ox - 44, 628), (ox + 44, 628), (ox + 58, 672), (ox - 58, 672)], [22, 22, 8, 8])
        s.append(inked(sh, CRIM, 3.2, extra=clipped(f"shoe{uid}{sx}", sh, f'<path d="M{ox - 60},652 H{ox + 60} V680 H{ox - 60}Z" fill="#FFFFFF"/>')))
        s.append(f'<path d="M{ox - 56},652 H{ox + 56}" stroke="{INK}" stroke-width="3"/>')
        s.append(fold([(ox - 24, 636), (ox - 6, 632), (ox + 12, 636)], 3, "#FF7A8C", .9))
    coat = rpoly([(226, 372), (374, 372), (396, 428), (440, 604), (160, 604), (204, 428)], [26, 26, 14, 8, 8, 14])
    if not xed:
        shade = f'<path d="M352,372 L420,372 L466,620 L350,620 Q382,520 352,372Z" fill="{COAT_SH}"/>'
    else:
        shade = (f'<path d="M140,360 L460,360 L460,440 Q380,424 300,446 Q220,424 140,440Z" fill="#9EA3BF"/>'
                 + fold([(170, 598), (300, 602), (430, 598)], 9, ORANGE))
    sleeves = [limb([(300 + sx * 60, 392), (300 + sx * 112, 418), (300 + sx * 158, 470)], [44, 40, 40]) for sx in (-1, 1)]
    s.append(inked([coat] + sleeves, COAT, 3.4, extra=clipped(f"coat{uid}", coat, shade)
                   + "".join(clipped(f"sl{uid}{i}", d, f'<path d="M{300 + sx * 96},{404} L{300 + sx * 200},{436} L{300 + sx * 200},{500} L{300 + sx * 130},{500}Z" fill="{COAT_SH}"/>')
                             for i, (sx, d) in enumerate(zip((-1, 1), sleeves)))))
    for sx in (-1, 1):
        s.append(fold([(300 + sx * 104, 404), (300 + sx * 116, 424), (300 + sx * 124, 446)], 2.6))
        s.append(fold([(300 + sx * 86, 402), (300 + sx * 84, 424), (300 + sx * 88, 440)], 2.4))
    s.append(f'<path d="M264,372 L300,446 L336,372Z" fill="{NAVY}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    s.append(f'<path d="M264,372 L300,446 L288,468 L244,386Z" fill="{COAT}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    s.append(f'<path d="M336,372 L300,446 L312,468 L356,386Z" fill="{COAT}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    s.append(f'<path d="M300,468 L300,604" stroke="{INK}" stroke-width="4"/>')
    s.append(fold([(256, 540), (252, 572), (256, 600)], 3))
    s.append(fold([(350, 524), (352, 562), (346, 600)], 3))
    for k in range(3):
        s.append(f'<circle cx="288" cy="{494 + k * 34}" r="4" fill="{INK}"/>')
    s.append(f'<path d="M226,474 H268 V510 Q247,516 226,510Z" fill="{COAT}" stroke="{INK}" stroke-width="3.4" stroke-linejoin="round"/>')
    s.append(f'<rect x="234" y="454" width="9" height="24" rx="3" fill="{CRIM}" stroke="{INK}" stroke-width="3"/><rect x="250" y="448" width="9" height="30" rx="3" fill="{GOLD}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M316,474 L356,474 L356,502 Q336,522 316,502Z" fill="{ORANGE}" stroke="{INK}" stroke-width="3.4" stroke-linejoin="round"/>')
    s.append(f'<path d="M336,510 C325,500 325,490 331,480 C333,490 337,492 339,486 C345,492 347,502 336,510Z" fill="{GOLD}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    if xed:
        s.append(f'<path d="M384,452 l8,-10 l6,8 l10,-4 l-2,12 l8,6 l-12,4 l-2,10 l-8,-6 l-10,4 l2,-10 l-8,-6z" fill="{INK}"/>')
        s.append(splat(258, 556, 30, 11, drips=3, run=1.3))     # big soak low on the coat, running off the hem
        s.append(splat(352, 540, 18, 12, drips=2, run=1.6))
        s.append(splat(276, 404, 16, 13, drips=2))              # splash on the lapel
        # the pocket overflows: ooze over the lip and down the coat
        s.append(splat(246, 478, 14, 14, drips=3, run=1.4))
    s.append(arm(-1, xed, uid))
    s.append(arm(1, xed, uid))
    if xed:
        s.append(splat(178, 436, 13, 15, drips=1))              # left sleeve
        s.append(splat(410, 548, 10, 16, drips=1, run=.8))      # right gauntlet
        s.append(splat(250, 650, 9, 17, drips=0))               # left sneaker
    return "".join(s)


def smoke():
    s = []
    puffs = [(306, 98, 15), (290, 76, 18), (316, 58, 20), (300, 30, 24), (330, 34, 17), (284, 44, 15)]
    s.append("".join(f'<circle cx="{x}" cy="{y}" r="{r + 3.5}" fill="{INK}"/>' for x, y, r in puffs))
    s.append("".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#4A3A4E"/>' for x, y, r in puffs))
    s.append("".join(f'<circle cx="{x - r * .25}" cy="{y - r * .25}" r="{r * .55}" fill="#6E6078"/>' for x, y, r in puffs))
    for x, y, r in puffs[1:4]:
        s.append(f'<path d="M{x - r * .4},{y + r * .1} a{r * .38},{r * .38} 0 1 1 {r * .38},{r * .38} a{r * .2},{r * .2} 0 1 1 {-r * .14},{-r * .22}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>')
    s.append(f'<path d="M294,130 L298,108 L306,122 L312,100 L318,120 L324,112 L324,132Z" fill="{ORANGE}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    s.append(f'<path d="M302,128 L306,116 L312,126 L316,118 L318,130Z" fill="{GOLD}"/>')
    return "".join(s)


def head(xed, uid):
    s = []
    s.append(inked(hair_back(), HAIR, 3.4))
    # ears
    for sx in (-1, 1):
        s.append(inked(f"M{300 + sx * 132},{226} a24,26 0 1 {1 if sx > 0 else 0} 0,52Z", SKIN, 3))
        s.append(fold([(300 + sx * 146, 240), (300 + sx * 152, 252), (300 + sx * 144, 264)], 3))
    # neck
    s.append(inked(rpoly([(272, 340), (328, 340), (324, 378), (276, 378)], 6), SKIN, 3,
                   extra=f'<path d="M272,340 H328 V362 Q300,352 272,362Z" fill="{SKIN_D}"/>'))
    s.append(inked(HEAD_D, SKIN, 3.6, extra=face_shade(xed, f"face{uid}")))
    # cheek warmth
    if not xed:
        s.append(f'<ellipse cx="226" cy="294" rx="16" ry="7" fill="#E88A74" opacity=".45"/>')
    s.append(eyes(xed, uid))
    s.append(fold([(296, 270), (308, 286), (294, 292)], 3.4))
    s.append(mouth(xed))
    if xed:
        for x, y, r in ((392, 286, 4.5), (402, 300, 3), (214, 318, 3.6)):
            s.append(f'<circle cx="{x}" cy="{y}" r="{r + 2.6}" fill="{INK}"/><circle cx="{x}" cy="{y}" r="{r}" fill="{SPILL}"/>')
    # fringe over the forehead
    fr = fringe(xed)
    s.append(inked(fr, HAIR, 3.4))
    for a, b, c in [((222, 140), (230, 160), (232, 182)), ((262, 132), (266, 152), (264, 172)), ((330, 132), (334, 150), (332, 168))]:
        s.append(fold([a, b, c], 4, HAIR_HI, .95))
    for a, b, c in [((210, 166), (214, 184), (204, 208)), ((248, 162), (252, 184), (244, 212)), ((292, 160), (292, 178), (288, 200)),
                    ((332, 162), (336, 184), (332, 210)), ((372, 160), (374, 174), (372, 190))]:
        s.append(fold([a, b, c], 2.4))
    # side fade
    for sx in (-1, 1):
        s.append(fold([(300 + sx * 140, 196), (300 + sx * 142, 214), (300 + sx * 138, 232)], 3, HAIR_HI, .8))
    s.append(glasses(xed))
    if xed:
        # singed tuft smoking
        s.append(smoke())
    return "".join(s)




def kid(xed, uid):
    return body(xed, uid) + head(xed, uid)


def hero_body(xed, uid, reach=((-176, 560), (176, 560))):
    """Upper body for the hero: shoulders and coat behind two raised fists.
    The fists themselves (gold blocks) are drawn by the hero, over the sleeve ends at `reach`."""
    s = []
    coat = rpoly([(222, 370), (378, 370), (404, 430), (420, 600), (180, 600), (196, 430)], [26, 26, 14, 8, 8, 14])
    sleeves = []
    for (dx, dy) in reach:
        sx = 1 if dx > 0 else -1
        sleeves.append(limb([(300 + sx * 62, 394), (300 + sx * 120, 440), (300 + dx, dy)], [46, 44, 42]))
    shade = (f'<path d="M350,370 L430,370 L460,620 L346,620 Q378,520 350,370Z" fill="{COAT_SH}"/>' if not xed else
             f'<path d="M140,360 L460,360 L460,440 Q380,424 300,446 Q220,424 140,440Z" fill="#9EA3BF"/>')
    sl_shade = "".join(clipped(f"hs{uid}{i}", d, f'<path d="M{300 + sx * 90},420 L{300 + sx * 260},470 L{300 + sx * 260},620 L{300 + sx * 150},620Z" fill="{COAT_SH if not xed else "#9EA3BF"}"/>')
                       for i, (sx, d) in enumerate(zip((-1, 1), sleeves)))
    s.append(inked([coat] + sleeves, COAT, 3.4, extra=clipped(f"hc{uid}", coat, shade) + sl_shade))
    for sx in (-1, 1):
        s.append(fold([(300 + sx * 104, 410), (300 + sx * 126, 440), (300 + sx * 140, 474)], 2.8))
    s.append(f'<path d="M264,372 L300,446 L336,372Z" fill="{NAVY}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    s.append(f'<path d="M264,372 L300,446 L288,468 L244,386Z" fill="{COAT}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    s.append(f'<path d="M336,372 L300,446 L312,468 L356,386Z" fill="{COAT}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    s.append(f'<path d="M300,468 L300,600" stroke="{INK}" stroke-width="4"/>')
    s.append(f'<path d="M316,474 L356,474 L356,502 Q336,522 316,502Z" fill="{ORANGE}" stroke="{INK}" stroke-width="3.4" stroke-linejoin="round"/>')
    s.append(f'<path d="M336,510 C325,500 325,490 331,480 C333,490 337,492 339,486 C345,492 347,502 336,510Z" fill="{GOLD}" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    if xed:
        s.append(splat(258, 512, 30, 21, drips=3, run=1.2))
        s.append(splat(276, 404, 16, 13, drips=2))
        s.append(splat(352, 520, 16, 22, drips=2, run=1.4))
        s.append(splat(178, 452, 13, 15, drips=1))
    return "".join(s)
