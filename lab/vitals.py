#!/usr/bin/env python3
"""Take the lab's vital signs from the GitHub API and draw them.

Needs a token in GITHUB_TOKEN (the workflow's own token is enough: everything
read here is public). Writes:
  assets/vitals-{theme}.svg     bedside monitor: weekly contributions as a heartbeat, plus readouts
  assets/helix.stl              the last year wound into a double helix, one base pair per week
  assets/karyotype-{theme}.svg  one chromosome per language; bands are the repos that carry it
  assets/phylogeny-{theme}.svg  UPGMA tree of the repos, from their language composition
and the VITALS and PHYLOGENY blocks of README.md.

    GITHUB_TOKEN=... python lab/vitals.py
    python lab/vitals.py --from-json snapshot.json    # redraw from a saved API response
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request

import numpy as np

from notebook import (ASSETS, BRAND, LAB, SHEET, STAT_H, STAT_W, THEMES, USER, Typesetter, card, esc, fade, footnote,
                      now_manila, picture, readout, replace_block, stamp, strip, strip_tag, svg_doc, text_width, themed)

PROFILE_REPO = USER                 # the profile repo itself: lab code, not your work
DRAWER = {"Protein-Structure-Viewer-Lite-": "Helix threejsensis", "dexterslab": "Pixel laboratory",
          "viscal": "Turingia lissajousii", "Olatz-Tol-": "Grando collatzii"}
QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name stargazerCount forkCount pushedAt
        primaryLanguage { name color }
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ------------------------------------------------------------------ data

def fetch(token):
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "specimen-lab"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]["user"]


def analyse(user):
    cc = user["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cc["contributionCalendar"]["weeks"]]
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    for c in reversed(counts[:-1] if counts and counts[-1] == 0 else counts):   # today may still be young
        if not c:
            break
        current += 1
    by_wd = [0] * 7
    for d in days:
        by_wd[dt.date.fromisoformat(d["date"]).weekday()] += d["contributionCount"]
    busiest = max(days, key=lambda d: d["contributionCount"]) if days else None
    repos = [r for r in user["repositories"]["nodes"] if r["name"] != PROFILE_REPO]
    return {
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"], "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"], "private": cc["restrictedContributionsCount"],
        "weeks": weeks, "days": counts, "dates": [d["date"] for d in days], "current": current, "longest": longest,
        "last7": sum(counts[-7:]),
        "busiest": busiest, "weekday": WEEKDAYS[by_wd.index(max(by_wd))] if any(by_wd) else None,
        "repos": repos, "repo_count": len(repos),
        "stars": sum(r["stargazerCount"] for r in repos), "followers": user["followers"]["totalCount"],
    }


def languages(repos):
    """{language: {"bytes": n, "color": c, "repos": [(repo, bytes), ...]}} sorted by bytes."""
    out = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            lang = out.setdefault(e["node"]["name"], {"bytes": 0, "color": e["node"]["color"] or "#8b949e", "repos": []})
            lang["bytes"] += e["size"]
            lang["repos"].append((r["name"], e["size"]))
    for v in out.values():
        v["repos"].sort(key=lambda x: -x[1])
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["bytes"]))


# ------------------------------------------------------------------ monitor

def beat(x, w, amp, base):
    """One P-QRS-T complex across width w, as points."""
    if amp <= 0:
        return [(x, base), (x + w, base)]
    q = [(0.00, 0), (0.18, 0), (0.24, -0.12), (0.30, 0), (0.40, 0), (0.44, 0.10), (0.48, -1.0), (0.53, 0.32),
         (0.57, 0), (0.70, 0), (0.78, -0.22), (0.86, 0), (1.00, 0)]
    return [(x + fx * w, base + fy * amp) for fx, fy in q]


def pleth(x, w, amp, base):
    """One plethysmograph pulse: fast upstroke, dicrotic notch, slow fall."""
    if amp <= 0:
        return [(x, base), (x + w, base)]
    q = [(0, 0), (0.12, -0.15), (0.28, -1.0), (0.42, -0.62), (0.50, -0.68), (0.62, -0.42), (0.85, -0.08), (1, 0)]
    return [(x + fx * w, base + fy * amp) for fx, fy in q]


def breath(x, w, amp, base, n=10):
    return [(x + w * k / n, base - amp * math.sin(math.pi * k / n)) for k in range(n + 1)]


def monitor(v, theme):
    """A bedside monitor wired to the GitHub account. Every number is real:
    II (ECG)  one beat per week, height = contributions that week
    PLETH     one pulse per day for the last 90 days
    RESP      one breath per month for the last 12 months
    """
    t = THEMES[theme]
    ts = Typesetter("m")
    W, H = 840, 400
    scr = "#05070a"
    green, cyan, yellow, white, red, dim, grid = "#3dff8f", "#4ad6ff", "#ffd43b", "#e8f0ee", "#ff1f3d", "#5f7370", "#0e1714"
    sx0, sy0, sw, sh = 18, 54, 548, 300
    rows = [("II", "ACTIVITY · 1 BEAT / WEEK", green), ("PLETH", "DAILY · LAST 90 DAYS", cyan), ("RESP", "MONTHLY · LAST 12 MONTHS", yellow)]
    rh = sh / 3
    weeks, days = v["weeks"], v.get("days") or []
    last90 = days[-90:]
    months = {}
    for date, c in zip(v.get("dates") or [], days):
        months[date[:7]] = months.get(date[:7], 0) + c
    mvals = list(months.values())[-12:]

    def wave(kind, y0):
        base = y0 + rh * 0.68
        x, pts = sx0 + 14, []
        if kind == 0:
            peak, bw = max(weeks) or 1, (sw - 28) / max(len(weeks), 1)
            for c in weeks:
                pts += beat(x, bw, math.sqrt(c / peak) * rh * 0.62 if c else 0, base)
                x += bw
        elif kind == 1:
            peak, bw = max(last90 or [1]) or 1, (sw - 28) / max(len(last90), 1)
            for c in last90:
                pts += pleth(x, bw, math.sqrt(c / peak) * rh * 0.55 if c else 0, base)
                x += bw
        else:
            peak, bw = max(mvals or [1]) or 1, (sw - 28) / max(len(mvals), 1)
            for c in mvals:
                pts += breath(x, bw, (0.08 + 0.92 * math.sqrt(c / peak)) * rh * 0.5 if c else rh * 0.04, base)
                x += bw
        return pts

    body = [f'''<defs>
  <filter id="ph" x="-5%" y="-30%" width="110%" height="160%"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="scr"><rect x="{sx0}" y="{sy0}" width="{sw}" height="{sh}"/></clipPath>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{t['panel']}" stroke="{t['edge']}" stroke-width="1.5"/>
<rect x="10" y="10" width="{W - 20}" height="{H - 20}" rx="9" fill="{scr}"/>''']
    # alarm banner
    alarm = not v["last7"]
    banner = "!! NO SIGNAL · 7 DAYS · CHECK SPECIMEN" if alarm else "RHYTHM STABLE"
    bc = red if alarm else green
    body.append(f'<rect x="18" y="18" width="{W - 36}" height="26" rx="4" fill="{bc}" opacity="{0.9 if alarm else 0.18}">'
                + ('<animate attributeName="opacity" values="0.95;0.25;0.95" dur="1s" repeatCount="indefinite"/>' if alarm else "") + '</rect>')
    g, _ = ts.text(banner, "label", 13, 32, 36, "#ffffff" if alarm else green, tracking=2)
    body.append(g)
    g, _ = ts.text(f"BED 000 · @{USER.upper()}", "label", 12, W - 30, 36, "#ffffff" if alarm else dim, anchor="end", tracking=1.6)
    body.append(g)
    for gx in range(sx0, sx0 + sw + 1, 25):
        body.append(f'<line x1="{gx}" y1="{sy0}" x2="{gx}" y2="{sy0 + sh}" stroke="{grid}"/>')
    for gy in range(int(sy0), int(sy0 + sh) + 1, 25):
        body.append(f'<line x1="{sx0}" y1="{gy}" x2="{sx0 + sw}" y2="{gy}" stroke="{grid}"/>')
    sweep = 10
    for k, (code, desc, col) in enumerate(rows):
        y0 = sy0 + k * rh
        pts = wave(k, y0)
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) + 1
        body.append(f'<g clip-path="url(#scr)"><path d="{d}" fill="none" stroke="{col}" stroke-width="1" opacity="0.16"/>'
                    f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.9" stroke-linejoin="round" filter="url(#ph)" '
                    f'stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}"><animate attributeName="stroke-dashoffset" '
                    f'values="{L:.0f};0;0" keyTimes="0;0.88;1" dur="{sweep}s" begin="{0.2 * k:.1f}s" repeatCount="indefinite"/></path>'
                    f'<circle r="3.6" fill="#ffffff" filter="url(#ph)"><animateMotion path="{d}" keyPoints="0;1;1" keyTimes="0;0.88;1" '
                    f'calcMode="linear" dur="{sweep}s" begin="{0.2 * k:.1f}s" repeatCount="indefinite"/></circle></g>')
        g, _ = ts.text(code, "label", 12, sx0 + 8, y0 + 16, col, tracking=1)
        body.append(g)
        g, _ = ts.text(desc, "text", 10.5, sx0 + 8 + text_width(code, "label", 12, 1) + 10, y0 + 16, dim)
        body.append(g)
        if k:
            body.append(f'<line x1="{sx0}" y1="{y0:.1f}" x2="{sx0 + sw}" y2="{y0:.1f}" stroke="#1d2a26" stroke-width="1"/>')
    g, _ = ts.text("12 MO AGO", "text", 9.5, sx0 + 10, sy0 + sh - 6, dim)
    body.append(g)
    g, _ = ts.text("NOW", "text", 9.5, sx0 + sw - 10, sy0 + sh - 6, dim, anchor="end")
    body.append(g)

    # numerics, hospital style: label, big value, unit, small alarm limits
    nx = sx0 + sw + 22
    active = sum(1 for c in weeks if c)
    spo2 = round(100 * active / max(len(weeks), 1))

    def tile(y, label, value, unit, col, note, big=44):
        out = [ts.text(label, "label", 11, nx, y, col, tracking=1.4)[0],
               ts.text(str(value), "wordmark", big, nx, y + big * 0.98, col)[0]]
        vw = text_width(str(value), "wordmark", big)
        out.append(ts.text(unit, "text", 12, nx + vw + 8, y + big * 0.95, col, opacity=0.8)[0])
        out.append(ts.text(note, "text", 10.5, W - 28, y, col, anchor="end", opacity=0.7)[0])
        return "".join(out)
    body.append(tile(70, "HR · LAST 7 DAYS", v["last7"], "contrib", green, f"{v['total']} / yr"))
    body.append(tile(146, "SpO₂ · ACTIVE WEEKS", spo2, "%", cyan, f"{active} of {len(weeks)} wk"))
    body.append(tile(222, "RESP · STREAK", v["current"], "days", yellow, f"best {v['longest']}"))
    body.append(tile(298, "NIBP · COMMITS / PRS", f"{v['commits']}/{v['prs']}", "", white, f"{v['issues']} issues", big=34))
    busy = v["busiest"]
    foot = (f"peak {busy['date']} ({busy['contributionCount']})" if busy and busy["contributionCount"] else "no peaks yet")
    if v["weekday"]:
        foot += f" · most active on {v['weekday']}s"
    foot += f" · {v['repo_count']} repos · ★ {v['stars']} · {v['followers']} followers"
    g, _ = ts.text(foot, "text", 11, 22, H - 18, dim)
    body.append(g)
    if alarm:
        body.append(f'<circle cx="{W - 32}" cy="{H - 22}" r="5" fill="{red}"><animate attributeName="opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite"/></circle>')
    return svg_doc(W, H, ts.defs_svg() + "\n".join(body),
                   f"Vital signs: {v['last7']} contributions in the last 7 days, {v['total']} in the last year, active in "
                   f"{active} of {len(weeks)} weeks, streak {v['current']} days (best {v['longest']}), "
                   f"{v['commits']} commits and {v['prs']} pull requests")


# ------------------------------------------------------------------ contribution calendar

def calendar(v, theme):
    """Contributions card: the year's total, then the last 26 weeks as a heatmap that fills left to right."""
    s = SHEET[theme]
    ts = Typesetter("cal")
    head, typed = strip(ts, STAT_W, 0, [("github", BRAND["lavender"]), (" > ", BRAND["neon"]),
                                        ("contributions", BRAND["paper"])], start=0.1, top=True)
    body = [card(theme, STAT_W, STAT_H), head, strip_tag(ts, STAT_W, "live", live=True),
            readout(ts, theme, v["total"], "in 12 months", typed + 0.1)]
    dates = [dt.date.fromisoformat(d) for d in v["dates"]]
    if dates:
        first = dates[-1] - dt.timedelta(days=(dates[-1].weekday() + 1) % 7 + 25 * 7)   # Sunday, 26 weeks back
        pitch, size = 8.6, 7
        active = sorted(c for c in v["days"] if c)        # quartiles of active days, as GitHub shades them
        cuts = [active[len(active) * q // 4] for q in (1, 2, 3)] if active else []
        cells = []
        for date, count in zip(dates, v["days"]):
            if date < first:
                continue
            col, row = (date - first).days // 7, (date.weekday() + 1) % 7
            level = 1 + sum(count > c for c in cuts) if count else 0
            x, y = 14 + col * pitch, 102 + row * pitch
            anim = fade(typed + 0.25 + col * 0.03, 0.2) if count else ""
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" rx="1" '
                         f'fill="{s["heat"][level]}">{anim}</rect>')
        body.append(f'<g>{"".join(cells)}</g>')
    days = "day" if v["current"] == 1 else "days"
    body.append(footnote(ts, theme, f"{v['last7']} this week · streak {v['current']} {days}", typed + 1.1))
    label = (f"GitHub contributions for @{USER}: {v['total']} in the last 12 months, {v['last7']} in the last 7 days, "
             f"current streak {v['current']} {days}, best {v['longest']}.")
    return svg_doc(STAT_W, STAT_H, ts.defs_svg() + "".join(body), label), label


def write_contributions(v):
    """Draw the contributions card and fill the CONTRIBUTIONS block. True if the README changed."""
    svgs = {theme: calendar(v, theme) for theme in THEMES}
    for theme, (svg, _) in svgs.items():
        (ASSETS / f"contributions-{theme}.svg").write_text(svg, encoding="utf-8")
    pic = themed("contributions", svgs["light"][1], STAT_W, STAT_H, query="v=" + stamp(svgs["light"][0]))
    return replace_block("CONTRIBUTIONS", f'<a href="https://github.com/{USER}">{pic}</a>')


# ------------------------------------------------------------------ 3D helix

def helix_stl(weeks, turns=5, R=9.0):
    """Plasmid pLLX for GitHub's 3D viewer, the same shape as the colour render:
    a supercoiled ring of double-stranded DNA, one base pair per week, with a
    protein bound in the groove for every week that had contributions.
    """
    from stl import Mesh
    from turntable import plasmid_frame
    m = Mesh()
    n = len(weeks)
    peak = max(weeks) or 1
    groove = math.radians(150)

    def strand(u, ph):
        p, nr, bi = plasmid_frame(u, n)
        th = ph + 2 * math.pi * turns * u / n
        return tuple(p + R * (math.cos(th) * nr + math.sin(th) * bi))
    for ph in (0.0, groove):
        pts = [strand(k, ph) for k in range(n + 1)]
        m.tube(pts, 1.15, sides=3, caps=False)
    for u, c in enumerate(weeks):
        a, b = strand(u, 0.0), strand(u, groove)
        mid = tuple((x + y) / 2 for x, y in zip(a, b))
        p, nr, bi = plasmid_frame(u, n)
        m.slab(a, b, width=1.3, thick=0.9, up=tuple(nr))
        if c:
            size = 2.2 + 3.8 * math.sqrt(c / peak)
            core = np.array(mid) + nr * (R + size * 0.9)
            m.octahedron(tuple(core), size)
            if c >= 0.5 * peak:                      # the busiest weeks bind a second subunit
                m.octahedron(tuple(core + size * 0.85 * (math.cos(u) * bi + 0.4 * nr)), size * 0.6)
    return m.ascii("plasmid_pLLX"), len(m.tris)


# ------------------------------------------------------------------ spindle (3D karyotype)

def spindle_stl(langs):
    """Metaphase in 3D: one chromosome per language, lined up on the metaphase plate.

    Each chromosome is two sister chromatids joined at a pinched centromere,
    length proportional to sqrt(bytes), with grooves at the boundaries between
    the repositories that carry it. Sisters face opposite poles, and spindle
    fibres run from each pole to its kinetochore. Astral rays fan out behind
    the poles. Rotate it to see the plate edge-on.
    """
    from stl import Mesh
    m = Mesh()
    items = list(langs.items())[:10]
    if not items:
        return m.ascii("spindle"), 0
    biggest = items[0][1]["bytes"] or 1
    n = len(items)
    RP, POLE, LMAX = 26.0, 46.0, 34.0
    rng = random.Random(7)
    for i, (name, v) in enumerate(items):
        L = 12 + (LMAX - 12) * math.sqrt(v["bytes"] / biggest)
        phi = 2 * math.pi * i / n
        ur = (math.cos(phi), math.sin(phi), 0.0)
        tilt = rng.uniform(-0.35, 0.35)
        up = (0.0, 0.0, 1.0)
        c = (RP * ur[0], RP * ur[1], 0.0)
        p_len, q_len = 0.38 * L, 0.62 * L
        # repo boundaries along the q arm, as fractions of the chromatid
        cuts, acc = [], 0
        for _, b in v["repos"][:-1]:
            acc += b / v["bytes"]
            cuts.append(-p_len + acc * L)
        segs = max(6, int(5 + 8 * L / LMAX))
        for side in (-1, 1):
            pts, radii = [], []
            for k in range(segs + 1):
                s_ = -p_len + L * k / segs
                arm = p_len if s_ < 0 else q_len
                f = min(1.0, abs(s_) / arm)
                z = side * (1.0 + 1.6 * f)                     # sisters splay toward their poles
                d = (ur[0] * math.cos(tilt) - 0, ur[1] * math.cos(tilt), math.sin(tilt))
                pts.append((c[0] + d[0] * s_, c[1] + d[1] * s_, c[2] + d[2] * s_ + z))
                r = 1.55 * math.sqrt(max(0.0, 1 - f ** 6))      # rounded telomeres
                r *= 1 - 0.5 * math.exp(-(s_ / 1.6) ** 2)       # centromere pinch
                if any(abs(s_ - cut) < L / segs * 0.6 for cut in cuts):
                    r *= 0.72                                    # band boundary groove
                radii.append(max(r, 0.25))
            m.tube(pts, radii, sides=3)
            # kinetochore fibre to this sister's pole
            pole = (0.0, 0.0, side * POLE)
            kin = (c[0], c[1], side * 1.0)
            m.tube([pole, kin], 0.22, sides=3, caps=False)
    for side in (-1, 1):
        pole = (0.0, 0.0, side * POLE)
        m.octahedron(pole, 2.6)
        for k in range(6):
            a = 2 * math.pi * k / 6 + 0.3
            tip = (11 * math.cos(a), 11 * math.sin(a), side * (POLE + 9))
            m.tube([pole, tip], 0.2, sides=3, caps=False)
    return m.ascii("metaphase_spindle"), len(m.tris)


# ------------------------------------------------------------------ karyotype

def _mix(hex_a, hex_b, f):
    a = [int(hex_a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(hex_b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * f):02x}" for x, y in zip(a, b))


def karyotype(langs, theme):
    """Karyotype on a lab floor: one X-shaped chromosome per language, standing on a
    perspective grid with reflections, no frame. Length follows sqrt(bytes); bands
    are the repositories carrying that language. Each chromosome sways and twists,
    a gleam runs down it, and a red scan line crosses the floor.
    """
    from notebook import ambient
    t = THEMES[theme]
    ts = Typesetter("k")
    items = list(langs.items())[:10]
    total = sum(v["bytes"] for _, v in items) or 1
    W = 840
    slot = (W - 80) / max(len(items), 1)
    maxlen, floor = 220, 300
    H = floor + 120
    biggest = items[0][1]["bytes"] if items else 1
    red = t["red"]
    adefs, abody = ambient("ka", W, H, theme, seed=3, cells=8, bits=10)
    vx, vy = W / 2, floor - 170           # vanishing point, behind the chromosomes
    defs = [adefs,
            f'<linearGradient id="gleam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="0.5" stop-color="#fff" stop-opacity="0.6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
            f'<linearGradient id="refl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.5"/>'
            f'<stop offset="0.5" stop-color="#fff" stop-opacity="0"/></linearGradient>',
            f'<mask id="reflm" maskUnits="userSpaceOnUse" x="0" y="{floor}" width="{W}" height="{H - floor}">'
            f'<rect x="0" y="{floor}" width="{W}" height="{H - floor}" fill="url(#refl)"/></mask>',
            f'<radialGradient id="floorfade" cx="0.5" cy="0" r="0.75"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>',
            f'<mask id="floorm" maskUnits="userSpaceOnUse" x="0" y="{floor - 30}" width="{W}" height="{H - floor + 30}">'
            f'<rect x="0" y="{floor - 30}" width="{W}" height="{H - floor + 30}" fill="url(#floorfade)"/></mask>',
            f'<linearGradient id="scanf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{red}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{red}" stop-opacity="0.5"/></linearGradient>',
            f'<filter id="ksoft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>']
    body = [abody]
    # perspective floor: rays to the vanishing point, rows compressing toward the horizon
    grid = []
    for k in range(-14, 15):
        bx = W / 2 + k * 70
        grid.append(f"M{bx:.0f},{H} L{vx + (bx - vx) * 0.18:.0f},{floor - 6}")
    for j in range(1, 9):
        y = floor - 6 + (H - floor + 6) * (j / 8) ** 1.7
        grid.append(f"M0,{y:.1f} H{W}")
    body.append(f'<g mask="url(#floorm)"><path d="{" ".join(grid)}" fill="none" stroke="{red}" stroke-opacity="0.35" stroke-width="1"/>'
                f'<rect x="0" y="{floor - 6}" width="{W}" height="18" fill="url(#scanf)">'
                f'<animate attributeName="y" values="{floor - 6};{H};{H}" keyTimes="0;0.7;1" dur="4.5s" repeatCount="indefinite"/>'
                f'<animate attributeName="height" values="6;40;40" keyTimes="0;0.7;1" dur="4.5s" repeatCount="indefinite"/></rect></g>')
    g, _ = ts.text(f"KARYOTYPE · {len(items)} LANGUAGE{'S' if len(items) != 1 else ''} · 2n = {2 * len(items)}",
                   "label", 12, 24, 30, red, tracking=1.6)
    body.append(g)
    g, _ = ts.text("height ∝ √bytes · bands = repositories · rotate the spindle below in 3D", "text", 12, 24, 48, t["muted"])
    body.append(g)
    for i, (name, v) in enumerate(items):
        cx = 40 + slot * i + slot / 2
        L = 70 + (maxlen - 70) * math.sqrt(v["bytes"] / biggest)
        w = 16
        c = v["color"]
        top = floor - L - 4
        cen = top + L * 0.4
        gid = f"cg{i}"
        defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
                    f'<stop offset="0" stop-color="{_mix(c, "#000000", 0.65)}"/><stop offset="0.22" stop-color="{_mix(c, "#ffffff", 0.5)}"/>'
                    f'<stop offset="0.5" stop-color="{c}"/><stop offset="0.85" stop-color="{_mix(c, "#000000", 0.45)}"/>'
                    f'<stop offset="1" stop-color="{_mix(c, "#000000", 0.72)}"/></linearGradient>')
        chromatids = []
        for side in (-1, 1):
            cid = f"cc{i}{'a' if side < 0 else 'b'}"
            x0 = cx - w / 2
            capsule = f'<rect x="{x0:.1f}" y="{top:.1f}" width="{w}" height="{L:.1f}" rx="{w / 2}"/>'
            defs.append(f'<clipPath id="{cid}">{capsule}</clipPath>')
            bands, y = [], top
            for j, (repo, b) in enumerate(v["repos"]):
                h = L * b / v["bytes"]
                if j % 2 == 1:
                    bands.append(f'<path d="M{x0 - 2:.1f},{y:.1f} Q{cx:.1f},{y + 4:.1f} {x0 + w + 2:.1f},{y:.1f} V{y + h:.1f} '
                                 f'Q{cx:.1f},{y + h + 4:.1f} {x0 - 2:.1f},{y + h:.1f} Z" fill="#000" opacity="0.32"/>')
                elif j:
                    bands.append(f'<path d="M{x0:.1f},{y:.1f} Q{cx:.1f},{y + 4:.1f} {x0 + w:.1f},{y:.1f}" fill="none" stroke="#000" stroke-opacity="0.35"/>')
                y += h
            dur = 4.6 + 0.37 * i
            chromatids.append(
                f'<g transform="rotate({side * 8} {cx:.1f} {cen:.1f})"><g transform="translate({side * (w / 2 - 1.5):.1f} 0)">'
                f'<g fill="url(#{gid})">{capsule}</g><g clip-path="url(#{cid})">{"".join(bands)}'
                f'<rect x="{x0 - 2:.1f}" y="{top - 40:.1f}" width="{w + 4}" height="34" fill="url(#gleam)">'
                f'<animate attributeName="y" values="{top - 40:.1f};{top + L + 10:.1f}" dur="{dur:.1f}s" begin="{0.6 + 0.25 * i:.2f}s" repeatCount="indefinite"/></rect></g>'
                f'<rect x="{x0:.1f}" y="{top:.1f}" width="{w}" height="{L:.1f}" rx="{w / 2}" fill="none" stroke="#000" stroke-opacity="0.35"/>'
                f'</g></g>')
        sway = 2 + (i % 3)
        twist = 0.6 + 0.08 * (i % 4)
        fig = (f'<g id="chr{i}"><g transform="translate({cx:.1f} {floor})"><g>'
               f'<animateTransform attributeName="transform" type="rotate" values="{-sway};{sway};{-sway}" dur="{6 + i * 0.7:.1f}s" repeatCount="indefinite"/>'
               f'<g><animateTransform attributeName="transform" type="scale" values="1 1;{twist} 1;1 1" dur="{5 + i * 0.5:.1f}s" repeatCount="indefinite"/>'
               f'<g transform="translate({-cx:.1f} {-floor})">{"".join(chromatids)}'
               f'<circle cx="{cx:.1f}" cy="{cen:.1f}" r="4.5" fill="{_mix(c, "#000000", 0.5)}" stroke="#000" stroke-opacity="0.4"/></g>'
               f'</g></g></g></g>')
        body.append(f'<ellipse cx="{cx:.1f}" cy="{floor + 2}" rx="{w * 1.8:.1f}" ry="5" fill="{c}" opacity="0.35" filter="url(#ksoft)"/>')
        body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{0.15 * i:.2f}s" fill="freeze"/>'
                    f'<animateTransform attributeName="transform" type="translate" values="0 -60;0 6;0 0" keyTimes="0;0.75;1" '
                    f'begin="{0.15 * i:.2f}s" dur="0.8s" fill="freeze"/>{fig}'
                    f'<g mask="url(#reflm)" opacity="0.55"><use href="#chr{i}" xlink:href="#chr{i}" transform="translate(0 {2 * floor}) scale(1 -1)"/></g></g>')
        g, _ = ts.text(str(i + 1), "wordmark", 20, cx, floor + 44, t["ink"], anchor="middle")
        body.append(g)
        label = name if len(name) <= 11 else name[:10] + "."
        g, _ = ts.text(label, "label", 11, cx, floor + 62, t["ink"], anchor="middle")
        body.append(g)
        g, _ = ts.text(f"{100 * v['bytes'] / total:.1f}%", "text", 11, cx, floor + 78, t["muted"], anchor="middle")
        body.append(g)
    return svg_doc(W, H, "<defs>" + "".join(defs) + "</defs>" + ts.defs_svg() + "\n".join(body),
                   "Language karyotype: " + ", ".join(f"{n} {100 * v['bytes'] / total:.0f}%" for n, v in items))


# ------------------------------------------------------------------ phylogeny

def upgma(names, vecs):
    """UPGMA on cosine distance. Returns nested (left, right, height) tuples with str leaves."""
    def cos_d(a, b):
        keys = set(a) | set(b)
        dotp = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
        na = math.sqrt(sum(x * x for x in a.values())) or 1
        nb = math.sqrt(sum(x * x for x in b.values())) or 1
        return max(0.0, 1 - dotp / (na * nb))
    clusters = {i: (names[i], 1, 0.0) for i in range(len(names))}
    dist = {(i, j): cos_d(vecs[i], vecs[j]) for i in clusters for j in clusters if i < j}
    nxt = len(names)
    while len(clusters) > 1:
        (i, j), d = min(dist.items(), key=lambda kv: (kv[1], kv[0]))
        ti, si, _ = clusters.pop(i)
        tj, sj, _ = clusters.pop(j)
        node = (ti, tj, d / 2)
        new = {}
        for k in clusters:
            dik = dist[(min(i, k), max(i, k))]
            djk = dist[(min(j, k), max(j, k))]
            new[(k, nxt)] = (dik * si + djk * sj) / (si + sj)
        dist = {key: v for key, v in dist.items() if i not in key and j not in key}
        dist.update(new)
        clusters[nxt] = (node, si + sj, d / 2)
        nxt += 1
    return next(iter(clusters.values()))[0]


def short(name):
    """Display lines for a tip: drop trailing dashes and long subtitles, then break a long
    name at the hyphen nearest its middle rather than cutting it off."""
    n = name.split("---")[0].strip("-")
    if len(n) <= 20:
        return [n]
    cuts = [i for i, ch in enumerate(n) if ch in "-_" and 4 <= i < len(n) - 3]
    if not cuts:
        return [n if len(n) <= 24 else n[:23] + "…"]
    i = min(cuts, key=lambda i: abs(i - len(n) / 2))
    return [line if len(line) <= 24 else line[:23] + "…" for line in (n[:i + 1], n[i + 1:])]


def phylogeny(repos, theme):
    """A radial tree of life for the repositories.

    Topology and branch heights are UPGMA on cosine distance between language
    compositions. Branches grow out from the common ancestor, a signal pulse
    runs down every lineage, tips are sized by code volume, and a radar sweep
    circles behind it all.
    """
    t = THEMES[theme]
    ts = Typesetter("p")
    named = [r for r in repos if r["languages"]["edges"]]
    W, H = 840, 660
    cx, cy, R, r0 = 420, 340, 196, 22
    if len(named) < 2:
        body = ts.text("Not enough repositories with code to grow a tree yet.", "text", 15, 24, 40, t["muted"])[0]
        return svg_doc(W, 70, ts.defs_svg() + body, "Phylogeny: not enough data yet")
    names = [r["name"] for r in named]
    vecs = [{e["node"]["name"]: e["size"] for e in r["languages"]["edges"]} for r in named]
    size = {r["name"]: sum(e["size"] for e in r["languages"]["edges"]) for r in named}
    colour = {r["name"]: (r["primaryLanguage"] or {}).get("color") or t["muted"] for r in named}
    tree = upgma(names, vecs)
    order = []

    def leaves(n):
        if isinstance(n, str):
            order.append(n)
        else:
            leaves(n[0])
            leaves(n[1])
    leaves(tree)
    root_h = tree[2] if tree[2] > 0 else 1e-6
    ang = {n: -90 + 360 * i / len(order) for i, n in enumerate(order)}

    def polar(a, rad):
        return cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))

    def arc(a1, a2, rad):
        (x1, y1), (x2, y2) = polar(a1, rad), polar(a2, rad)
        large = 1 if abs(a2 - a1) > 180 else 0
        sweep = 1 if a2 > a1 else 0
        return f"M{x1:.1f},{y1:.1f} A{rad:.1f},{rad:.1f} 0 {large} {sweep} {x2:.1f},{y2:.1f}"

    segs, routes = [], {}

    def place(n, depth, route):
        if isinstance(n, str):
            routes[n] = route
            return ang[n], R
        a_l, r_l = place(n[0], depth + 1, None)
        a_r, r_r = place(n[1], depth + 1, None)
        a = (a_l + a_r) / 2
        rad = r0 + (R - r0) * (1 - n[2] / root_h)
        for ca, cr in ((a_l, r_l), (a_r, r_r)):
            x1, y1 = polar(ca, rad)
            x2, y2 = polar(ca, cr)
            segs.append((depth, arc(a, ca, rad) + f" L{x2:.1f},{y2:.1f}"))
        node_pos[id(n)] = (a, rad)
        return a, rad
    node_pos = {}
    ra, rr = place(tree, 0, None)

    # root-to-tip routes for the pulses
    def trace(n, path):
        a, rad = node_pos[id(n)]
        for child in (n[0], n[1]):
            ca, cr = (ang[child], R) if isinstance(child, str) else node_pos[id(child)]
            x2, y2 = polar(ca, cr)
            p = path + " " + arc(a, ca, rad).split(" ", 1)[1] + f" L{x2:.1f},{y2:.1f}"
            if isinstance(child, str):
                routes[child] = p
            else:
                trace(child, p)
    x0, y0 = polar(ra, rr)
    trace(tree, f"M{cx},{cy} L{x0:.1f},{y0:.1f}")
    segs.append((-1, f"M{cx},{cy} L{x0:.1f},{y0:.1f}"))

    red = t["red"]
    from notebook import ambient
    amb_d, amb_b = ambient("pa", W, H, theme, seed=5, cells=10, bits=12)
    body = [f'''<defs>{amb_d}
  <radialGradient id="dish" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{t['panel2']}"/><stop offset="1" stop-color="{t['panel2']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{red}" stop-opacity="0"/><stop offset="1" stop-color="{red}" stop-opacity="0.28"/></linearGradient>
  <filter id="pg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<circle cx="{cx}" cy="{cy}" r="{R + 120}" fill="url(#dish)" opacity="0.8"/>''', amb_b]
    for k in range(1, 5):
        rad = r0 + (R - r0) * k / 4
        body.append(f'<circle cx="{cx}" cy="{cy}" r="{rad:.1f}" fill="none" stroke="{t["edge"]}" stroke-width="1" stroke-dasharray="2 6"/>')
        dist = root_h * 2 * (1 - k / 4)
        lxp, lyp = polar(-90 + 180 / len(order), rad)
        g, _ = ts.text(f"{dist:.2f}", "label", 9.5, lxp + 3, lyp - 3, t["muted"], opacity=0.8)
        body.append(g)
    for a in range(0, 360, 30):
        x1, y1 = polar(a, r0)
        x2, y2 = polar(a, R + 4)
        body.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["edge"]}" stroke-width="0.6" opacity="0.5"/>')
    # radar sweep
    xa, ya = polar(-40, R + 30)
    body.append(f'<g><path d="M{cx},{cy} L{cx + R + 30},{cy} A{R + 30},{R + 30} 0 0 0 {xa:.1f},{ya:.1f} Z" fill="url(#sweep)"/>'
                f'<line x1="{cx}" y1="{cy}" x2="{cx + R + 30}" y2="{cy}" stroke="{red}" stroke-width="1.6" opacity="0.8" filter="url(#pg)"/>'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="7s" repeatCount="indefinite"/></g>')
    # branches grow outward by depth
    depth_max = max(d for d, _ in segs) + 1
    for depth, d in sorted(segs):
        begin = 0.2 + 0.35 * (depth + 1)
        body.append(f'<path d="{d}" fill="none" stroke="{t["ink"]}" stroke-width="2" stroke-linecap="round" '
                    f'stroke-dasharray="800" stroke-dashoffset="800"><animate attributeName="stroke-dashoffset" '
                    f'from="800" to="0" begin="{begin:.2f}s" dur="0.9s" fill="freeze"/></path>')
    grown = 0.2 + 0.35 * (depth_max + 1) + 0.6
    # lineage ring, tips, labels
    biggest = max(size.values()) or 1
    step = 360 / len(order)
    for i, n in enumerate(order):
        a = ang[n]
        body.append(f'<path d="{arc(a - step / 2 + 2, a + step / 2 - 2, R + 9)}" fill="none" stroke="{colour[n]}" '
                    f'stroke-width="4" stroke-linecap="round" opacity="0.9"/>')
        x, y = polar(a, R)
        rad = 4 + 7 * math.sqrt(size[n] / biggest)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{colour[n]}" stroke="{t["bg"]}" stroke-width="1.5" opacity="0">'
                    f'<set attributeName="opacity" to="1" begin="{grown - 0.3:.2f}s" fill="freeze"/></circle>')
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="none" stroke="{red}" stroke-width="2" opacity="0">'
                    f'<animate attributeName="r" values="{rad:.1f};{rad + 12:.1f}" dur="3s" begin="{grown + 1.2 + 0.4 * i:.2f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="0.9;0" dur="3s" begin="{grown + 1.2 + 0.4 * i:.2f}s" repeatCount="indefinite"/></circle>')
        ca = math.cos(math.radians(a))
        lx, ly = polar(a, R + 24)
        anchor = "start" if ca > 0.25 else ("end" if ca < -0.25 else "middle")
        sa = math.sin(math.radians(a))
        ly += 4 + (10 if sa > 0.6 else (-8 if sa < -0.6 else 0))
        lines = short(n)
        up = sa < -0.6                                   # tips at the top grow their labels upward
        lead = 14
        y1 = ly - lead * (len(lines) - 1) if up else ly
        name_g = "".join(ts.text(line, "label", 12.5, lx, y1 + lead * j, t["ink"], anchor=anchor)[0]
                         for j, line in enumerate(lines))
        extra = ""
        if n in DRAWER:
            hy = y1 - 17 if up else y1 + lead * (len(lines) - 1) + 17
            extra = ts.text(DRAWER[n], "hand", 17, lx, hy, t["pen"], anchor=anchor)[0]
        body.append(f'<g opacity="0">{name_g}{extra}<set attributeName="opacity" to="1" begin="{grown:.2f}s" fill="freeze"/></g>')
        # a pulse running from the ancestor down this lineage
        body.append(f'<circle r="3.4" fill="{red}" filter="url(#pg)" opacity="0">'
                    f'<set attributeName="opacity" to="1" begin="{grown + 0.4 * i:.2f}s" fill="freeze"/>'
                    f'<animateMotion path="{routes[n]}" dur="3s" begin="{grown + 0.4 * i:.2f}s" repeatCount="indefinite"/></circle>')
    # the common ancestor
    body.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{red}" filter="url(#pg)"><animate attributeName="r" values="8;11;8" dur="1.6s" repeatCount="indefinite"/></circle>'
                f'<circle cx="{cx}" cy="{cy}" r="4" fill="{t["bg"]}"/>')
    body.append(f'<circle cx="30" cy="{H - 25}" r="6" fill="{red}"/>')
    g, _ = ts.text("LUCA, the last common ancestor: curiosity", "hand", 19, 44, H - 19, t["pen"])
    body.append(g)
    g, _ = ts.text(f"RADIAL UPGMA · {len(order)} TAXA", "label", 12, 24, 34, t["red"], tracking=1.6)
    body.append(g)
    g, _ = ts.text("cosine distance on language bytes", "text", 12, 24, 52, t["muted"])
    body.append(g)
    g, _ = ts.text("tip size = code volume · ring = main language", "text", 12, W - 24, H - 20, t["muted"], anchor="end")
    body.append(g)
    return svg_doc(W, H, ts.defs_svg() + "\n".join(body), "Radial phylogeny of repositories: " + ", ".join(order))


# ------------------------------------------------------------------ main

def write(v, langs):
    pulse = write_contributions(v)
    for theme in THEMES:
        (ASSETS / f"vitals-{theme}.svg").write_text(monitor(v, theme), encoding="utf-8")
        (ASSETS / f"karyotype-{theme}.svg").write_text(karyotype(langs, theme), encoding="utf-8")
        (ASSETS / f"phylogeny-{theme}.svg").write_text(phylogeny(v["repos"], theme), encoding="utf-8")
    stl, n = helix_stl(v["weeks"])
    (ASSETS / "helix.stl").write_text(stl + "\n", encoding="utf-8")
    spindle, ns = spindle_stl(langs)
    (ASSETS / "spindle.stl").write_text(spindle + "\n", encoding="utf-8")
    active = sum(1 for c in v["weeks"] if c)
    stamp = now_manila().date().isoformat()
    rendered = {}
    try:
        from turntable import plasmid_scene, render, spindle_scene
        for name, scene, opts in (("plasmid", plasmid_scene(v["weeks"]), dict(dist=3.5)),
                                  ("spindle", spindle_scene(langs), dict(dist=4.3, elev=12))):
            render(name, scene, **opts)
            rendered[name] = True
    except Exception as e:  # noqa: BLE001 - yesterday's renders stay up; these shapes change slowly
        print(f"::warning::turntable renders failed ({e})")

    # GitHub boots each ```stl viewer one after another and gives up on any not ready within
    # 10 s of the page asking, then prints the raw mesh instead. The specimen keeps the README's
    # one inline viewer; these two open full-page in the same viewer from their .stl files.
    def hero(name, alt, model):
        if not (rendered.get(name) or (ASSETS / f"{name}-dark.webp").exists()):
            return ""
        return f'<a href="{LAB}/assets/{model}">{picture(name, alt, width="100%", ext="webp", query="v=" + stamp)}</a>\n\n'
    vitals = (
        f'{picture("vitals", "Vital signs monitor", width="100%")}\n\n'
        f'<sub>{v["total"]} contributions this year · {v["commits"]} commits · {v["prs"]} pull requests</sub>\n\n'
        + hero("plasmid", "Plasmid pLLX turning under the lights. Open it in 3D", "helix.stl") +
        f'<sub><b>pLLX</b> · the year as a plasmid, a base pair a week; each glowing protein is a week with commits '
        f'({active} so far) · <a href="{LAB}/assets/helix.stl">turn it in 3D</a></sub>\n\n'
        f'{picture("karyotype", "Language karyotype", width="100%")}\n\n'
        f'<sub>One chromosome per language · height by bytes · bands by repo</sub>\n\n'
        + hero("spindle", "The language chromosomes at metaphase on a glowing spindle. Open it in 3D", "spindle.stl") +
        f'<sub><b>Metaphase</b> · the same chromosomes lined up on the spindle · '
        f'<a href="{LAB}/assets/spindle.stl">turn it in 3D</a></sub>')
    phylo = (
        f'{picture("phylogeny", "Phylogeny of repositories", width="100%")}\n\n'
        f'<sub>Re-grown every night from each repo\'s language mix.</sub>')
    a = replace_block("VITALS", vitals)
    b = replace_block("PHYLOGENY", phylo)
    print(f"vitals: {v['total']} contributions, streak {v['current']}/{v['longest']}, {len(langs)} languages, "
          f"{v['repo_count']} repos, helix {n} triangles, README {'updated' if a or b or pulse else 'unchanged'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-json", help="read a saved GraphQL `user` object instead of calling the API")
    ap.add_argument("--telemetry", action="store_true",
                    help="also draw the old lab telemetry (needs VITALS and PHYLOGENY markers in the README)")
    args = ap.parse_args()
    if args.from_json:
        user = json.load(open(args.from_json))
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("set GITHUB_TOKEN (the Actions token works)")
        try:
            user = fetch(token)
        except Exception as e:  # noqa: BLE001 - keep yesterday's readings rather than fail the run
            print(f"::warning::GitHub API unavailable, keeping yesterday's vitals ({e})")
            return
    v = analyse(user)
    if args.telemetry:
        write(v, languages(v["repos"]))
    else:
        changed = write_contributions(v)
        print(f"contributions: {v['total']} in 12 months, README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
