"""Readings / Vitals: the instrument console in the painted lab. Three different machines stand
on one steel console, wired into a junction box: a GitHub activity scope (CRT heatmap and
LED readouts), a LeetCode Nixie counter with three analog dials, and the picoGym tube rack.
Each has a brass plate on the console front. XED's console sparks, cracks a tube and spills
between the machines; the readouts themselves stay clean.
"""
import json
import math
import random

from notebook import ROOT, Typesetter, svg_doc, text_width
from panels import lab_wall, scorch
from rooms import STEEL, STEEL_DK, STEEL_LT, bolt, brass_plate, tooth
from toon import INK, PHOENIX as C, clipped, defs as toon_defs, f, fold, inked, rpoly



def frames_text(ts, seq, face, size, x, y, fill, begin, step=.06, anchor="middle", attrs=""):
    """Show each string in `seq` for one step, holding on the last (the base frame)."""
    final = ts.text(seq[-1], face, size, x, y, fill, anchor=anchor, attrs=attrs)[0]
    if len(seq) == 1:
        return final
    end = begin + step * (len(seq) - 1)
    out = []
    for k, v in enumerate(seq[:-1]):
        t0, t1 = begin + k * step, begin + (k + 1) * step
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="0;{t0 / end:.4f};{t1 / end:.4f}" calcMode="discrete" '
                   f'dur="{end:.2f}s" fill="freeze"/>{ts.text(v, face, size, x, y, fill, anchor=anchor, attrs=attrs)[0]}</g>')
    out.append(f'<g><animate attributeName="opacity" values="0;1" keyTimes="0;{(end - step) / end:.4f}" calcMode="discrete" dur="{end:.2f}s" fill="freeze"/>{final}</g>')
    return "".join(out)


def count_seq(n, steps=7):
    return [str(round(n * (k / steps) ** .6)) for k in range(1, steps)] + [str(n)]


# ------------------------------------------------------------------ the machines

def scope(ts, x, base, w, xed, animate, uid, v):
    """GitHub activity scope: a heavy CRT box standing on the console."""
    h = 222
    top = base - h + 2
    out = []
    case = rpoly([(x, top), (x + w, top), (x + w, base + 2), (x, base + 2)], 14)
    out.append(f'<path d="{case}" fill="{INK}" transform="translate(5 5)"/>')
    out.append(inked(case, "#C9C2AE" if not xed else "#4A4F63", 3.4, extra=clipped(f"sc{uid}", case,
               f'<rect x="{f(x + w * .78)}" y="{f(top)}" width="{f(w)}" height="{h + 10}" fill="{INK}" opacity=".16"/>'
               f'<rect x="{f(x)}" y="{f(base - 46)}" width="{f(w)}" height="60" fill="{INK}" opacity=".12"/>')))
    out.append(fold([(x + 14, top + 8), (x + w * .5, top + 6), (x + w - 30, top + 8)], 3, "#FFFFFF"))
    # the screen
    sx, sy, sw, sh = x + 16, top + 14, w - 32, h - 76
    scr = rpoly([(sx, sy), (sx + sw, sy), (sx + sw, sy + sh), (sx, sy + sh)], 18)
    phos = ("#132044", "#2C5FD8", "#5FA8FF", "#A8E0FF", "#FFFFFF") if not xed else ("#10261A", "#2E7A3E", "#4FCB62", C["spill"], "#E9FFB8")
    ink_on = "#DDEBFF" if not xed else C["spill"]
    g = [f'<rect x="{f(sx)}" y="{f(sy)}" width="{f(sw)}" height="{f(sh)}" fill="{"#071226" if not xed else "#061410"}"/>']
    g.append(frames_text(ts, count_seq(v["total"]), "body-bold", 34, sx + 16, sy + 40, ink_on, .5, anchor="start") if animate
             else ts.text(str(v["total"]), "body-bold", 34, sx + 16, sy + 40, ink_on)[0])
    g.append(ts.text("in 12 months", "body-bold", 12, sx + 22 + text_width(str(v["total"]), "body-bold", 34), sy + 38, ink_on, attrs=' opacity=".8"')[0])
    cols = v["weeks"]
    cell = min(9, (sw - 28) / cols - 2)
    gap = 2
    gx = sx + (sw - cols * (cell + gap) + gap) / 2
    gy = sy + 54
    for (c, r), lv in v["grid"].items():
        rx_, ry_ = gx + c * (cell + gap), gy + r * (cell + gap)
        rect = f'<rect x="{f(rx_)}" y="{f(ry_)}" width="{f(cell)}" height="{f(cell)}" rx="1.4" fill="{phos[lv]}"'
        if animate:
            d = .55 + (c + r) * .028
            rect += f'><animate attributeName="opacity" values="0;1" keyTimes="0;{d / (d + .01):.4f}" calcMode="discrete" dur="{d + .01:.2f}s" fill="freeze"/></rect>'
        else:
            rect += "/>"
        g.append(rect)
    # sweep line crossing the grid now and then
    if animate:
        g.append(f'<rect x="{f(sx)}" y="{f(sy)}" width="3" height="{f(sh)}" fill="{ink_on}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;.5;.5;.5;.5;0;0" keyTimes="0;.02;.04;.06;.08;.1;1" calcMode="discrete" dur="7s" begin="2s" repeatCount="indefinite"/>'
                 f'<animate attributeName="x" values="{f(sx)};{f(sx + sw * .25)};{f(sx + sw * .5)};{f(sx + sw * .75)};{f(sx + sw)};{f(sx + sw)}" keyTimes="0;.02;.04;.06;.08;1" '
                 f'calcMode="discrete" dur="7s" begin="2s" repeatCount="indefinite"/></rect>')
    g += [f'<rect x="{f(sx)}" y="{f(sy + k * 3.2)}" width="{f(sw)}" height="1.1" fill="#FFFFFF" opacity=".05"/>' for k in range(int(sh / 3.2))]
    g.append(f'<path d="M{f(sx)},{f(sy)} h{f(sw * .4)} l{f(-sw * .22)},{f(sh)} h{f(-sw * .18)}z" fill="#FFFFFF" opacity=".05"/>')
    out.append(f'<path d="{scr}" fill="#000" stroke="{INK}" stroke-width="3.4"/>' + clipped(f"ss{uid}", scr, "".join(g)))
    out.append(f'<path d="{scr}" fill="none" stroke="#2A2F44" stroke-width="2" transform="translate(1.5 1.5)" opacity=".6"/>')
    # LED readouts on the case
    led_y = sy + sh + 14
    for i, (val, lab) in enumerate(((str(v["last7"]), "this week"), (f'{v["streak"]}', "day streak"))):
        lx = x + 18 + i * (w - 36) / 2
        lw = (w - 36) / 2 - 10
        out.append(f'<rect x="{f(lx)}" y="{f(led_y)}" width="{f(lw)}" height="30" rx="4" fill="#1A1E2E" stroke="{INK}" stroke-width="2.4"/>')
        out.append(ts.text(val, "body-bold", 15, lx + 9, led_y + 20.5, "#FF4A3A" if not xed else C["phoenix"])[0])
        out.append(ts.text(lab, "body-bold", 8.6, lx + 12 + text_width(val, "body-bold", 15), led_y + 19.5, "#C9C2AE")[0])
    for kx in (x + 22, x + w - 22):
        out.append(f'<rect x="{f(kx - 10)}" y="{f(base - 2)}" width="20" height="6" rx="2" fill="{STEEL_DK}" stroke="{INK}" stroke-width="1.8"/>')
    return "".join(out), (x + w, top + 60)


def dial(ts, cx, cy, r, val, vmax, label, colour, animate, begin, uid):
    face = (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{r + 4}" fill="{STEEL}" stroke="{INK}" stroke-width="2.4"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{r}" fill="{C["bone"]}" stroke="{INK}" stroke-width="1.8"/>')
    ticks = []
    for k in range(9):
        a = math.radians(-210 + k * 30)
        r0 = r * (.72 if k % 2 else .64)
        ticks.append(f'<path d="M{f(cx + math.cos(a) * r0)},{f(cy + math.sin(a) * r0)} L{f(cx + math.cos(a) * r * .88)},{f(cy + math.sin(a) * r * .88)}" stroke="{INK}" stroke-width="{1.8 if k % 2 == 0 else 1.1}"/>')
    arc_a0, arc_a1 = math.radians(-210 + 180), math.radians(30)
    band = (f'<path d="M{f(cx + math.cos(arc_a0) * r * .8)},{f(cy + math.sin(arc_a0) * r * .8)} A{f(r * .8)},{f(r * .8)} 0 0 1 {f(cx + math.cos(arc_a1) * r * .8)},{f(cy + math.sin(arc_a1) * r * .8)}" '
            f'fill="none" stroke="{colour}" stroke-width="3"/>')
    target = -120 + 240 * (val / vmax if vmax else 0)
    needle = (f'<path d="M{f(cx - 2.4)},{f(cy)} L{f(cx)},{f(cy - r * .82)} L{f(cx + 2.4)},{f(cy)}Z" fill="{C["crimson"]}" stroke="{INK}" stroke-width="1.2"/>')
    if animate:
        steps = [-120, -120 + (target + 120) * .5, target + 8 if val else target, target]
        vals = ";".join(f"{f(a)} {f(cx)} {f(cy)}" for a in steps)
        needle = (f'<g transform="rotate({f(target)} {f(cx)} {f(cy)})"><animateTransform attributeName="transform" type="rotate" values="{vals}" keyTimes="0;.4;.7;1" '
                  f'calcMode="discrete" dur=".5s" begin="{begin:.2f}s" fill="freeze"/>{needle}</g>')
    else:
        needle = f'<g transform="rotate({f(target)} {f(cx)} {f(cy)})">{needle}</g>'
    pin = f'<circle cx="{f(cx)}" cy="{f(cy)}" r="3.4" fill="{INK}"/>'
    lab = (ts.text(label, "body-bold", 9, cx, cy + r * .5, INK, anchor="middle")[0]
           + ts.text(str(val), "body-bold", 13, cx, cy + r + 18, colour, anchor="middle",
                     attrs=f' stroke="{INK}" stroke-width="3" stroke-linejoin="round" paint-order="stroke"')[0])
    return face + "".join(ticks) + band + lab + needle + pin


def nixie(ts, x, base, w, xed, animate, uid, v):
    """LeetCode Nixie counter: three glass tubes on a steel box roll to the total; three dials
    on the box front read Easy, Medium and Hard."""
    total = sum(v["solved"].values())
    digits = f"{total:03d}"
    box_top = base - 118
    out = []
    box = rpoly([(x, box_top), (x + w, box_top), (x + w, base + 2), (x, base + 2)], 8)
    out.append(f'<path d="{box}" fill="{INK}" transform="translate(5 5)"/>')
    out.append(inked(box, "#2A2F44" if not xed else "#1A1E2E", 3.2, extra=f'<rect x="{x}" y="{box_top}" width="{w}" height="10" fill="#4B5370"/>'))
    tw, th = 46, 82
    gap = (w - 3 * tw) / 4
    glow = "#FF9A3A"
    rnd = random.Random(7)
    for i, dch in enumerate(digits):
        tx = x + gap + i * (tw + gap)
        tube = f"M{f(tx)},{f(box_top + 2)} V{f(box_top - th + tw / 2)} A{f(tw / 2)},{f(tw / 2)} 0 0 1 {f(tx + tw)},{f(box_top - th + tw / 2)} V{f(box_top + 2)}Z"
        out.append(f'<rect x="{f(tx - 3)}" y="{f(box_top - 6)}" width="{tw + 6}" height="10" rx="2" fill="{STEEL}" stroke="{INK}" stroke-width="2"/>')
        inner = [f'<rect x="{f(tx)}" y="{f(box_top - th)}" width="{tw}" height="{th + 4}" fill="#1A0E0A"/>']
        inner += [f'<path d="M{f(tx + 4)},{f(box_top - th + 18 + k * 9)} H{f(tx + tw - 4)}" stroke="#3A2A20" stroke-width="1"/>' for k in range(6)]
        inner.append(f'<ellipse cx="{f(tx + tw / 2)}" cy="{f(box_top - th / 2 + 4)}" rx="{tw * .42}" ry="{th * .36}" fill="{glow}" opacity=".16"/>')
        seq = [str(rnd.randint(0, 9)) for _ in range(5 + i * 2)] + [dch] if animate else [dch]
        inner.append(frames_text(ts, seq, "body-bold", 44, tx + tw / 2, box_top - 18, "#FFC27A", .45, step=.07,
                                 attrs=f' stroke="{glow}" stroke-width="1.6" paint-order="stroke"'))
        out.append(clipped(f"nx{uid}{i}", tube, "".join(inner)))
        out.append(f'<path d="{tube}" fill="#CFE6EA" opacity=".12" stroke="{INK}" stroke-width="2.6"/>')
        out.append(fold([(tx + 8, box_top - th + 18), (tx + 7, box_top - 18)], 2.6, "#FFFFFF"))
        if xed and i == 2:
            out.append(f'<path d="M{f(tx + tw - 6)},{f(box_top - th + 26)} l-6,8 l4,5 l-5,7" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity=".85"/>')
    # dials on the box front
    vmax = max(v["solved"].values()) or 1
    cols = (("Easy", "#3fb950" if xed else "#1a9f47"), ("Medium", "#ffb02e" if xed else "#d97706"), ("Hard", "#ff5c6c" if xed else "#cf222e"))
    for i, (k, col) in enumerate(cols):
        cx = x + w * (i + .5) / 3
        out.append(dial(ts, cx, box_top + 44, 22, v["solved"][k], vmax, k[0], col, animate, 1.0 + i * .12, f"{uid}{i}"))
    for kx in (x + 18, x + w - 18):
        out.append(f'<rect x="{f(kx - 10)}" y="{f(base - 2)}" width="20" height="6" rx="2" fill="{STEEL_DK}" stroke="{INK}" stroke-width="1.8"/>')
    return "".join(out), (x, box_top + 20), (x + w, box_top + 20)


def rack(ts, x, base, w, xed, animate, uid):
    """picoGym: test tubes standing in a wooden rack, filled in proportion to solves."""
    data = json.loads((ROOT / "lab" / "data" / "picoctf.json").read_text(encoding="utf-8"))
    cats = [(k, sum(vv[d] for d in ("easy", "medium", "hard"))) for k, vv in data["solved"].items()]
    short = {"General Skills": "GEN", "Reverse Engineering": "REV", "Cryptography": "CRY", "Web Exploitation": "WEB",
             "Artificial Intelligence": "AI", "Forensics": "FOR", "Binary Exploitation": "BIN", "Blockchain": "BLK"}
    colors = {"GEN": "#8FD3FF", "REV": C["phoenix"], "CRY": C["gold"], "WEB": C["spill"], "AI": "#C9A0FF",
              "FOR": "#FF8A9C", "BIN": C["crimson"], "BLK": "#9AA3B8"}
    total = sum(c[1] for c in cats)
    top_hi = max(c[1] for c in cats) or 1
    out = []
    rack_top, rack_h = base - 44, 46
    # back rail the tubes lean on
    out.append(inked(rpoly([(x + 4, base - 170), (x + w - 4, base - 170), (x + w - 4, base - 160), (x + 4, base - 160)], 3), "#7A4524" if not xed else "#4A2A18", 2.4))
    for px_ in (x + 8, x + w - 16):
        out.append(f'<rect x="{f(px_)}" y="{f(base - 170)}" width="8" height="{170 - rack_h + 4}" fill="#7A4524" stroke="{INK}" stroke-width="2"/>')
    n = len(cats)
    step = (w - 30) / n
    for i, (name, solved) in enumerate(cats):
        cx = x + 15 + step * (i + .5)
        top, bot = base - 158, rack_top + 20
        tube = f"M{f(cx - 9)},{f(top)} V{f(bot - 9)} a9,9 0 0 0 18,0 V{f(top)}Z"
        frac = solved / top_hi
        fill_h = 0 if not solved else (bot - rack_top) + (rack_top - top - 8) * max(.06, frac)
        col = colors[short[name]]
        liq = (f'<rect x="{f(cx - 11)}" y="{f(bot - fill_h)}" width="22" height="{f(fill_h + 10)}" fill="{col}"'
               + (f'><animate attributeName="y" values="{f(bot)};{f(bot - fill_h * .35)};{f(bot - fill_h * .7)};{f(bot - fill_h)}" keyTimes="0;.3;.6;.9" '
                  f'calcMode="discrete" dur=".7s" begin="{.6 + i * .08:.2f}s" fill="freeze"/></rect>' if animate and fill_h else "/>")
               + (f'<rect x="{f(cx - 11)}" y="{f(bot - fill_h)}" width="22" height="2" fill="#FFFFFF" opacity=".55"/>' if fill_h and not animate else ""))
        out.append(inked(tube, "#DCEFF3", 2.4, grain=None, extra=clipped(f"rt{uid}{i}", tube, liq)))
        out.append(fold([(cx - 4.5, top + 8), (cx - 4.5, rack_top - 6)], 2.2, "#FFFFFF"))
        out.append(f'<rect x="{f(cx - 11)}" y="{f(top - 6)}" width="22" height="7" rx="2" fill="{STEEL_LT}" stroke="{INK}" stroke-width="1.8"/>')
        if xed and short[name] == "REV":
            out.append(f'<path d="M{f(cx + 7)},{f(top + 30)} l-5,7 l4,4 l-4,6" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    block = rpoly([(x, rack_top), (x + w, rack_top), (x + w, base + 2), (x, base + 2)], 4)
    out.append(f'<path d="{block}" fill="{INK}" transform="translate(5 5)"/>')
    out.append(inked(block, "#8A5230" if not xed else "#5A3420", 3, extra=(
        f'<rect x="{x}" y="{rack_top}" width="{w}" height="9" fill="#A8693E"/>'
        + fold([(x + 10, rack_top + 3), (x + w - 10, rack_top + 3)], 2, "#C98A5A"))))
    for i, (name, solved) in enumerate(cats):
        cx = x + 15 + step * (i + .5)
        out.append(f'<ellipse cx="{f(cx)}" cy="{rack_top + 4}" rx="11" ry="3.4" fill="#3A1E0E"/>')
        out.append(ts.text(short[name], "body-bold", 9, cx, rack_top + 24, C["bone"], anchor="middle", tracking=.3)[0])
        out.append(ts.text(str(solved), "body-bold", 12, cx, rack_top + 39, C["gold"], anchor="middle")[0])
    return "".join(out), total, data["username"], (x, base - 110)


# ------------------------------------------------------------------ the console

def cable(a, b, sag, colour):
    d = f"M{f(a[0])},{f(a[1])} C{f(a[0] + 10)},{f(a[1] + sag)} {f(b[0] - 10)},{f(b[1] + sag)} {f(b[0])},{f(b[1])}"
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="3.4" stroke-linecap="round"/>')


def spark(x, y, animate):
    s = (f'<path d="M{f(x)},{f(y)} l6,-10 l-2,7 l9,-5 l-5,9 l8,1 l-12,4z" fill="{C["gold"]}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    if not animate:
        return ""
    return (f'<g opacity="0"><animate attributeName="opacity" values="0;1;0;1;0;0" keyTimes="0;.04;.08;.12;.16;1" calcMode="discrete" '
            f'dur="3.2s" begin="1.6s" repeatCount="indefinite"/>{s}</g>')


TILE_W, TILE_H = 252, 300
DATA = ROOT / "lab" / "data"


def github_data():
    d = json.loads((DATA / "github.json").read_text(encoding="utf-8"))
    d["grid"] = {tuple(int(n) for n in k.split(",")): lv for k, lv in d["grid"].items()}
    return d


def leetcode_data():
    return json.loads((DATA / "leetcode.json").read_text(encoding="utf-8"))


def tile(kind, theme, animate=True):
    """One machine on its stretch of the lab console. The three tiles sit side by side in the
    README (one image per live source, each with its own link and generated block), and the
    wall, console top and plates line up across them so they read as one bench."""
    xed = theme == "dark"
    uid = f"t{kind[0]}{theme[0]}{int(animate)}"
    ts = Typesetter(uid)
    W, H, base = TILE_W, TILE_H, 240
    s = [lab_wall(-40, 0, W + 80, base, xed),
         f'<rect x="-4" y="{base}" width="{W + 8}" height="{H - base + 4}" fill="{"#4B5370" if not xed else "#232A40"}" stroke="{INK}" stroke-width="3.4"/>'
         f'<rect x="-4" y="{base}" width="{W + 8}" height="12" fill="{"#7C86A0" if not xed else "#3A4058"}" stroke="{INK}" stroke-width="3"/>'
         + fold([(8, base + 4), (W / 2, base + 4), (W - 8, base + 4)], 2.2, "#C9D0DE")]
    if kind == "github":
        v = github_data()
        art, _ = scope(ts, 12, base, W - 24, xed, animate, uid, v)
        plate = ("GitHub", f"@{v['user']}")
        label = (f"GitHub contributions for @{v['user']}: {v['total']} in the last 12 months, {v['last7']} in the last 7 days, "
                 f"current streak {v['streak']} days, best {v['best']}.")
    elif kind == "leetcode":
        v = leetcode_data()
        art, _, _ = nixie(ts, 28, base, W - 56, xed, animate, uid, v)
        plate = ("LeetCode", f"@{v['handle']}, {v['active']} active days")
        n = v["solved"]
        label = (f"LeetCode @{v['handle']}: {sum(n.values())} problems solved ({n['Easy']} easy, {n['Medium']} medium, "
                 f"{n['Hard']} hard) over {v['active']} active days.")
    else:
        art, total, user, _ = rack(ts, 14, base, W - 28, xed, animate, uid)
        plate = (f"picoGym, {total} solves", f"@{user}")
        d = json.loads((DATA / "picoctf.json").read_text(encoding="utf-8"))
        per = [(k, sum(c[x] for x in ("easy", "medium", "hard"))) for k, c in d["solved"].items()]
        label = f"picoGym @{user}: {total} challenges solved. " + ", ".join(f"{k} {n}" for k, n in per if n) + "."
    s.append(art)
    a, b = plate
    pw = max(text_width(a, "body-bold", 12.5), text_width(b, "body", 10.5)) + 40
    s.append(brass_plate(ts, W / 2 - pw / 2, base + 18, pw, 36, [(a, 12.5, True), (b, 10.5, False)], uid))
    if xed:
        if kind == "github":
            s.append(f'<ellipse cx="{W - 40}" cy="{base + 6}" rx="26" ry="4.5" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.4"/>'
                     f'<path d="M{W - 30},{base + 9} v14 a4,4 0 0 0 8,0 v-14z" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.2"/>')
        elif kind == "leetcode":
            s.append(spark(W - 30, base - 10, animate))
            s.append(scorch(40, 30, 18, 6))
        else:
            s.append(f'<ellipse cx="44" cy="{base + 6}" rx="22" ry="4" fill="{C["spill"]}" stroke="{INK}" stroke-width="2.4"/>')
    s.append(tooth(W, H))
    return svg_doc(W, H, f'<defs>{toon_defs()}</defs>{ts.defs_svg()}' + "".join(s), label), label


KINDS = ("github", "leetcode", "picogym")
BLOCKS = {"github": "CONTRIBUTIONS", "leetcode": "LEETCODE", "picogym": "ASSAY"}


def link(kind):
    if kind == "github":
        return f"https://github.com/{github_data()['user']}"
    if kind == "leetcode":
        return f"https://leetcode.com/u/{leetcode_data()['handle']}/"
    d = json.loads((DATA / "picoctf.json").read_text(encoding="utf-8"))
    return d.get("profile_url") or "https://play.picoctf.org"


def live_block(kind):
    """Draw one live tile (animated and still, light and dark) and return its README markup."""
    from notebook import ASSETS, esc, scene, stamp
    out = ASSETS / "live"
    out.mkdir(parents=True, exist_ok=True)
    parts, label = [], ""
    for theme in ("light", "dark"):
        for animate, tag in ((True, ""), (False, "-still")):
            svg, label = tile(kind, theme, animate)
            (out / f"{kind}{tag}-{theme}.svg").write_text(svg, encoding="utf-8")
            parts.append(svg)
    pic = scene(kind, label, TILE_W, TILE_H, folder="assets/live", query="v=" + stamp(*parts))
    return f'<a href="{esc(link(kind))}">{pic}</a>'


def write_live(kind):
    """Redraw one live tile and refill its README block. True if the README changed."""
    from notebook import replace_block
    return replace_block(BLOCKS[kind], live_block(kind))


if __name__ == "__main__":
    out = ROOT / "lab" / ".runtime" / "preview" / "readme"
    out.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        for kind in ("github", "leetcode", "picogym"):
            (out / f"live-{kind}-{theme}.svg").write_text(tile(kind, theme, True)[0], encoding="utf-8")
    print("tiles written")
