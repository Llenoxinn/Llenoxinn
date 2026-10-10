//! render3d: a tiny, dependency-free ray tracer for the Specimen Lab.
//!
//! Reads a scene of spheres and capsules, spins a camera around it and writes
//! one PPM frame per step for each theme (dark and light) from a single set of
//! intersections. Shading: studio key/fill/rim lights, hard shadows, ambient
//! occlusion, emission with bloom, depth fog, drifting background cells, and
//! a vignette that fades exactly into the page colour so the render has no edge.
//!
//!   render3d scene.txt out_dir
//!
//! Scene format, one directive per line (# starts a comment):
//!   size W H | frames N | ss S | fov DEG | elev DEG | dist D | spin TURNS
//!   page dark R G B | page light R G B      (page background, sRGB 0..1)
//!   accent dark R G B | accent light R G B  (rim light and cells)
//!   s x y z r  R G B emit                   (sphere)
//!   c x1 y1 z1 x2 y2 z2 r  R G B emit       (capsule)

use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::ops::{Add, Mul, Neg, Sub};

#[derive(Clone, Copy, Debug, Default)]
struct V3 {
    x: f32,
    y: f32,
    z: f32,
}
fn v3(x: f32, y: f32, z: f32) -> V3 {
    V3 { x, y, z }
}
impl Add for V3 {
    type Output = V3;
    fn add(self, o: V3) -> V3 {
        v3(self.x + o.x, self.y + o.y, self.z + o.z)
    }
}
impl Sub for V3 {
    type Output = V3;
    fn sub(self, o: V3) -> V3 {
        v3(self.x - o.x, self.y - o.y, self.z - o.z)
    }
}
impl Mul<f32> for V3 {
    type Output = V3;
    fn mul(self, s: f32) -> V3 {
        v3(self.x * s, self.y * s, self.z * s)
    }
}
impl Neg for V3 {
    type Output = V3;
    fn neg(self) -> V3 {
        v3(-self.x, -self.y, -self.z)
    }
}
impl V3 {
    fn dot(self, o: V3) -> f32 {
        self.x * o.x + self.y * o.y + self.z * o.z
    }
    fn cross(self, o: V3) -> V3 {
        v3(self.y * o.z - self.z * o.y, self.z * o.x - self.x * o.z, self.x * o.y - self.y * o.x)
    }
    fn len(self) -> f32 {
        self.dot(self).sqrt()
    }
    fn norm(self) -> V3 {
        let l = self.len();
        if l > 0.0 { self * (1.0 / l) } else { self }
    }
    fn mulv(self, o: V3) -> V3 {
        v3(self.x * o.x, self.y * o.y, self.z * o.z)
    }
    fn min(self, o: V3) -> V3 {
        v3(self.x.min(o.x), self.y.min(o.y), self.z.min(o.z))
    }
    fn max(self, o: V3) -> V3 {
        v3(self.x.max(o.x), self.y.max(o.y), self.z.max(o.z))
    }
    fn axis(self, i: usize) -> f32 {
        match i {
            0 => self.x,
            1 => self.y,
            _ => self.z,
        }
    }
}

fn srgb_to_lin(c: f32) -> f32 {
    c.max(0.0).powf(2.2)
}
fn lin_to_srgb(c: f32) -> f32 {
    c.max(0.0).powf(1.0 / 2.2)
}
fn smoothstep(a: f32, b: f32, x: f32) -> f32 {
    let t = ((x - a) / (b - a)).clamp(0.0, 1.0);
    t * t * (3.0 - 2.0 * t)
}
fn aces(x: f32) -> f32 {
    ((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)).clamp(0.0, 1.0)
}
fn hash(mut x: u32) -> u32 {
    x ^= x >> 16;
    x = x.wrapping_mul(0x7feb352d);
    x ^= x >> 15;
    x = x.wrapping_mul(0x846ca68b);
    x ^= x >> 16;
    x
}

// ------------------------------------------------------------------ scene

#[derive(Clone, Copy)]
enum Shape {
    Sphere { c: V3, r: f32 },
    Capsule { a: V3, b: V3, r: f32 },
}

#[derive(Clone, Copy)]
struct Prim {
    shape: Shape,
    col: V3, // linear
    emit: f32,
}

impl Prim {
    fn bounds(&self) -> (V3, V3) {
        match self.shape {
            Shape::Sphere { c, r } => (c - v3(r, r, r), c + v3(r, r, r)),
            Shape::Capsule { a, b, r } => (a.min(b) - v3(r, r, r), a.max(b) + v3(r, r, r)),
        }
    }
    fn centre(&self) -> V3 {
        let (lo, hi) = self.bounds();
        (lo + hi) * 0.5
    }
    /// Distance along the ray to the first hit in front of the origin, or -1.
    fn hit(&self, ro: V3, rd: V3) -> f32 {
        match self.shape {
            Shape::Sphere { c, r } => {
                let oc = ro - c;
                let b = oc.dot(rd);
                let cc = oc.dot(oc) - r * r;
                let h = b * b - cc;
                if h < 0.0 {
                    return -1.0;
                }
                let h = h.sqrt();
                let t = -b - h;
                if t > 0.0 { t } else if -b + h > 0.0 { -b + h } else { -1.0 }
            }
            Shape::Capsule { a, b: pb, r } => {
                // after Inigo Quilez, "capsule - ray intersection"
                let ba = pb - a;
                let oa = ro - a;
                let baba = ba.dot(ba);
                let bard = ba.dot(rd);
                let baoa = ba.dot(oa);
                let rdoa = rd.dot(oa);
                let oaoa = oa.dot(oa);
                let qa = baba - bard * bard;
                let qb = baba * rdoa - baoa * bard;
                let qc = baba * oaoa - baoa * baoa - r * r * baba;
                let h = qb * qb - qa * qc;
                if h >= 0.0 && qa > 1e-9 {
                    let t = (-qb - h.sqrt()) / qa;
                    let y = baoa + t * bard;
                    if y > 0.0 && y < baba && t > 0.0 {
                        return t;
                    }
                }
                // caps
                let mut best = -1.0f32;
                for cen in [a, pb] {
                    let oc = ro - cen;
                    let b2 = rd.dot(oc);
                    let c2 = oc.dot(oc) - r * r;
                    let h2 = b2 * b2 - c2;
                    if h2 > 0.0 {
                        let t = -b2 - h2.sqrt();
                        if t > 0.0 && (best < 0.0 || t < best) {
                            best = t;
                        }
                    }
                }
                best
            }
        }
    }
    fn normal(&self, p: V3) -> V3 {
        match self.shape {
            Shape::Sphere { c, .. } => (p - c).norm(),
            Shape::Capsule { a, b, .. } => {
                let ba = b - a;
                let pa = p - a;
                let h = (pa.dot(ba) / ba.dot(ba).max(1e-12)).clamp(0.0, 1.0);
                (pa - ba * h).norm()
            }
        }
    }
}

// ------------------------------------------------------------------ BVH

/// Flat bounding volume hierarchy: median split on the longest axis, leaves of up to 4.
struct Flat {
    lo: Vec<V3>,
    hi: Vec<V3>,
    a: Vec<u32>, // left child or first prim
    b: Vec<u32>, // right child or prim count (when leaf flag set)
    leaf: Vec<bool>,
    prims: Vec<Prim>,
}

impl Flat {
    fn build(mut prims: Vec<Prim>) -> Flat {
        let mut f = Flat { lo: vec![], hi: vec![], a: vec![], b: vec![], leaf: vec![], prims: vec![] };
        let n = prims.len();
        f.node(&mut prims, 0, n);
        f.prims = prims;
        f
    }
    fn node(&mut self, prims: &mut [Prim], start: usize, end: usize) -> u32 {
        let mut lo = v3(f32::MAX, f32::MAX, f32::MAX);
        let mut hi = -lo;
        let mut clo = lo;
        let mut chi = hi;
        for p in &prims[start..end] {
            let (a, b) = p.bounds();
            lo = lo.min(a);
            hi = hi.max(b);
            let c = p.centre();
            clo = clo.min(c);
            chi = chi.max(c);
        }
        let idx = self.lo.len();
        self.lo.push(lo);
        self.hi.push(hi);
        self.a.push(0);
        self.b.push(0);
        self.leaf.push(false);
        let n = end - start;
        if n <= 4 {
            self.a[idx] = start as u32;
            self.b[idx] = n as u32;
            self.leaf[idx] = true;
            return idx as u32;
        }
        let ext = chi - clo;
        let axis = if ext.x > ext.y && ext.x > ext.z { 0 } else if ext.y > ext.z { 1 } else { 2 };
        prims[start..end].sort_by(|p, q| p.centre().axis(axis).partial_cmp(&q.centre().axis(axis)).unwrap());
        let mid = start + n / 2;
        let l = self.node(prims, start, mid);
        let r = self.node(prims, mid, end);
        self.a[idx] = l;
        self.b[idx] = r;
        idx as u32
    }
    fn slab(&self, i: usize, ro: V3, inv: V3, tmax: f32) -> f32 {
        let t1 = (self.lo[i] - ro).mulv(inv);
        let t2 = (self.hi[i] - ro).mulv(inv);
        let tmin = t1.min(t2);
        let tmx = t1.max(t2);
        let near = tmin.x.max(tmin.y).max(tmin.z).max(0.0);
        let far = tmx.x.min(tmx.y).min(tmx.z).min(tmax);
        if near <= far { near } else { f32::MAX }
    }
    fn closest(&self, ro: V3, rd: V3) -> Option<(f32, usize)> {
        if self.prims.is_empty() {
            return None;
        }
        let inv = v3(1.0 / rd.x, 1.0 / rd.y, 1.0 / rd.z);
        let mut best = f32::MAX;
        let mut hit = usize::MAX;
        let mut stack = [0u32; 64];
        let mut sp = 1;
        while sp > 0 {
            sp -= 1;
            let i = stack[sp] as usize;
            if self.slab(i, ro, inv, best) == f32::MAX {
                continue;
            }
            if self.leaf[i] {
                let s = self.a[i] as usize;
                for k in s..s + self.b[i] as usize {
                    let t = self.prims[k].hit(ro, rd);
                    if t > 0.0 && t < best {
                        best = t;
                        hit = k;
                    }
                }
            } else {
                let (l, r) = (self.a[i] as usize, self.b[i] as usize);
                let dl = self.slab(l, ro, inv, best);
                let dr = self.slab(r, ro, inv, best);
                // push the farther child first so the nearer one is popped first
                if dl < dr {
                    if dr != f32::MAX { stack[sp] = r as u32; sp += 1; }
                    if dl != f32::MAX { stack[sp] = l as u32; sp += 1; }
                } else {
                    if dl != f32::MAX { stack[sp] = l as u32; sp += 1; }
                    if dr != f32::MAX { stack[sp] = r as u32; sp += 1; }
                }
            }
        }
        if hit == usize::MAX { None } else { Some((best, hit)) }
    }
    fn occluded(&self, ro: V3, rd: V3, tmax: f32) -> bool {
        let inv = v3(1.0 / rd.x, 1.0 / rd.y, 1.0 / rd.z);
        let mut stack = [0u32; 64];
        let mut sp = 1;
        while sp > 0 {
            sp -= 1;
            let i = stack[sp] as usize;
            if self.slab(i, ro, inv, tmax) == f32::MAX {
                continue;
            }
            if self.leaf[i] {
                let s = self.a[i] as usize;
                for k in s..s + self.b[i] as usize {
                    let t = self.prims[k].hit(ro, rd);
                    if t > 0.0 && t < tmax {
                        return true;
                    }
                }
            } else {
                stack[sp] = self.a[i];
                sp += 1;
                stack[sp] = self.b[i];
                sp += 1;
            }
        }
        false
    }
}

// ------------------------------------------------------------------ settings

struct Theme {
    page: V3,   // sRGB
    accent: V3, // sRGB
    dark: bool,
}

struct Settings {
    w: usize,
    h: usize,
    frames: usize,
    ss: usize,
    fov: f32,
    elev: f32,
    dist: f32,
    spin: f32,
    themes: [Theme; 2],
}

fn parse(text: &str) -> (Settings, Vec<Prim>) {
    let mut s = Settings {
        w: 760,
        h: 440,
        frames: 72,
        ss: 2,
        fov: 30.0,
        elev: 18.0,
        dist: 3.2,
        spin: 1.0,
        themes: [
            Theme { page: v3(0.051, 0.067, 0.090), accent: v3(1.0, 0.12, 0.24), dark: true },
            Theme { page: v3(1.0, 1.0, 1.0), accent: v3(0.88, 0.0, 0.16), dark: false },
        ],
    };
    let mut prims = Vec::new();
    for line in text.lines() {
        let line = line.split('#').next().unwrap_or("").trim();
        if line.is_empty() {
            continue;
        }
        let mut it = line.split_whitespace();
        let key = it.next().unwrap();
        let rest: Vec<&str> = it.collect();
        let nums: Vec<f32> = rest.iter().filter_map(|t| t.parse::<f32>().ok()).collect();
        match key {
            "size" => {
                s.w = nums[0] as usize;
                s.h = nums[1] as usize;
            }
            "frames" => s.frames = nums[0] as usize,
            "ss" => s.ss = (nums[0] as usize).max(1),
            "fov" => s.fov = nums[0],
            "elev" => s.elev = nums[0],
            "dist" => s.dist = nums[0],
            "spin" => s.spin = nums[0],
            "page" | "accent" => {
                let t = if rest[0] == "dark" { 0 } else { 1 };
                let c = v3(nums[0], nums[1], nums[2]);
                if key == "page" { s.themes[t].page = c } else { s.themes[t].accent = c }
            }
            "s" => prims.push(Prim {
                shape: Shape::Sphere { c: v3(nums[0], nums[1], nums[2]), r: nums[3] },
                col: v3(srgb_to_lin(nums[4]), srgb_to_lin(nums[5]), srgb_to_lin(nums[6])),
                emit: nums[7],
            }),
            "c" => prims.push(Prim {
                shape: Shape::Capsule { a: v3(nums[0], nums[1], nums[2]), b: v3(nums[3], nums[4], nums[5]), r: nums[6] },
                col: v3(srgb_to_lin(nums[7]), srgb_to_lin(nums[8]), srgb_to_lin(nums[9])),
                emit: nums[10],
            }),
            other => eprintln!("render3d: ignoring unknown directive {other}"),
        }
    }
    (s, prims)
}

/// Centre the scene on its bounding box and scale it to unit radius.
fn normalise(prims: &mut [Prim]) {
    let mut lo = v3(f32::MAX, f32::MAX, f32::MAX);
    let mut hi = -lo;
    for p in prims.iter() {
        let (a, b) = p.bounds();
        lo = lo.min(a);
        hi = hi.max(b);
    }
    let c = (lo + hi) * 0.5;
    let mut r: f32 = 1e-6;
    for p in prims.iter() {
        let (a, b) = p.bounds();
        for q in [a, b] {
            r = r.max(((q - c).len()) * 0.88);
        }
    }
    let k = 1.0 / r;
    for p in prims.iter_mut() {
        p.shape = match p.shape {
            Shape::Sphere { c: cc, r: rr } => Shape::Sphere { c: (cc - c) * k, r: rr * k },
            Shape::Capsule { a, b, r: rr } => Shape::Capsule { a: (a - c) * k, b: (b - c) * k, r: rr * k },
        };
    }
}

// ------------------------------------------------------------------ rendering

struct Sample {
    hit: bool,
    t: f32,
    n: V3,
    v: V3,
    col: V3,
    emit: f32,
    ao: f32,
    shadow: f32,
}

const AO_DIRS: usize = 6;

fn trace(bvh: &Flat, ro: V3, rd: V3, key: V3, px_seed: u32) -> Sample {
    let mut s = Sample { hit: false, t: 0.0, n: v3(0.0, 0.0, 0.0), v: -rd, col: v3(0.0, 0.0, 0.0), emit: 0.0, ao: 1.0, shadow: 1.0 };
    if let Some((t, k)) = bvh.closest(ro, rd) {
        let p = ro + rd * t;
        let pr = &bvh.prims[k];
        let mut n = pr.normal(p);
        if n.dot(rd) > 0.0 {
            n = -n;
        }
        s.hit = true;
        s.t = t;
        s.n = n;
        s.col = pr.col;
        s.emit = pr.emit;
        let o = p + n * 0.002;
        if pr.emit < 0.5 {
            s.shadow = if bvh.occluded(o, key, 4.0) { 0.25 } else { 1.0 };
            // ambient occlusion: a fixed fan of directions, rotated per pixel
            let up = if n.y.abs() < 0.9 { v3(0.0, 1.0, 0.0) } else { v3(1.0, 0.0, 0.0) };
            let tu = up.cross(n).norm();
            let tv = n.cross(tu);
            let rot = (hash(px_seed) as f32 / u32::MAX as f32) * std::f32::consts::TAU;
            let mut occ = 0.0;
            for i in 0..AO_DIRS {
                let a = rot + i as f32 * std::f32::consts::TAU / AO_DIRS as f32;
                let el = 0.35 + 0.5 * ((i % 3) as f32 / 2.0);
                let d = (tu * (a.cos() * el.cos()) + tv * (a.sin() * el.cos()) + n * el.sin()).norm();
                if bvh.occluded(o, d, 0.16) {
                    occ += 1.0;
                }
            }
            s.ao = 1.0 - 0.75 * occ / AO_DIRS as f32;
        }
    }
    s
}

fn shade(s: &Sample, th: &Theme, key: V3, fill: V3, back: V3, cam_dist: f32) -> V3 {
    let acc = v3(srgb_to_lin(th.accent.x), srgb_to_lin(th.accent.y), srgb_to_lin(th.accent.z));
    let page = v3(srgb_to_lin(th.page.x), srgb_to_lin(th.page.y), srgb_to_lin(th.page.z));
    let n = s.n;
    let v = s.v;
    if s.emit >= 0.5 {
        let rim = (1.0 - n.dot(v).max(0.0)).powf(2.0);
        if !th.dark {
            // on white paper a glow reads as nothing: draw emitters as saturated accent ink
            let ink = s.col * 0.25 + acc * 0.75;
            return ink * (0.75 + 0.25 * rim);
        }
        return s.col * (1.6 * s.emit) + s.col * rim * 0.8;
    }
    let ndk = n.dot(key).max(0.0);
    let ndf = n.dot(fill).max(0.0);
    let h = (key + v).norm();
    let spec = n.dot(h).max(0.0).powf(56.0) * 0.55 * s.shadow;
    let fres = (1.0 - n.dot(v).max(0.0)).powf(3.0);
    let rim = fres * (n.dot(back) + 0.35).max(0.0);
    let (amb, rimk) = if th.dark { (0.16, 1.5) } else { (0.34, 0.55) };
    let mut c = s.col * (amb * s.ao + 0.95 * ndk * s.shadow + 0.28 * ndf * s.ao);
    c = c + v3(1.0, 1.0, 1.0) * spec + acc * (rim * rimk) + s.col * s.emit;
    // depth fog toward the page colour: far side of the model recedes
    let tn = ((s.t - (cam_dist - 1.0)) / 2.0).clamp(0.0, 1.0);
    let fog = smoothstep(0.3, 1.0, tn) * if th.dark { 0.7 } else { 0.3 };
    c * (1.0 - fog) + page * fog
}

struct Cell {
    x: f32,
    y: f32,
    r: f32,
    ax: f32,
    ay: f32,
    ph: f32,
}

fn cells(n: usize) -> Vec<Cell> {
    (0..n)
        .map(|i| {
            let h = |k: u32| hash(i as u32 * 7919 + k) as f32 / u32::MAX as f32;
            Cell { x: h(1), y: h(2), r: 0.018 + 0.05 * h(3), ax: 0.03 + 0.06 * h(4), ay: 0.02 + 0.04 * h(5), ph: h(6) * 6.283 }
        })
        .collect()
}

/// Background (linear): page colour, a soft accent glow behind the model, drifting cells.
fn background(th: &Theme, u: f32, v: f32, aspect: f32, phase: f32, cl: &[Cell]) -> V3 {
    let page = v3(srgb_to_lin(th.page.x), srgb_to_lin(th.page.y), srgb_to_lin(th.page.z));
    let acc = v3(srgb_to_lin(th.accent.x), srgb_to_lin(th.accent.y), srgb_to_lin(th.accent.z));
    let dx = (u - 0.5) * aspect;
    let dy = v - 0.5;
    let d = (dx * dx + dy * dy).sqrt();
    let glow = (1.0 - smoothstep(0.0, 0.55, d)) * if th.dark { 0.10 } else { 0.05 };
    let mut c = page * (1.0 - glow) + acc * glow;
    for k in cl {
        let cx = (k.x + k.ax * (phase + k.ph).sin()) * aspect;
        let cy = k.y + k.ay * (phase * 1.0 + k.ph * 1.7).cos();
        let ddx = u * aspect - cx;
        let ddy = v - cy;
        let dd = (ddx * ddx + ddy * ddy).sqrt();
        let ring = (1.0 - smoothstep(0.0, 0.006, (dd - k.r).abs())) * 0.55;
        let fillc = (1.0 - smoothstep(k.r * 0.85, k.r, dd)) * 0.08;
        let nuc = (1.0 - smoothstep(k.r * 0.28, k.r * 0.36, dd)) * 0.35;
        let a = (ring + fillc + nuc).min(1.0) * if th.dark { 0.38 } else { 0.3 };
        c = c * (1.0 - a) + acc * a;
    }
    c
}

fn blur(buf: &mut [V3], w: usize, h: usize, r: usize) {
    let mut tmp = vec![v3(0.0, 0.0, 0.0); w * h];
    for _ in 0..3 {
        for y in 0..h {
            let mut acc = v3(0.0, 0.0, 0.0);
            let row = &buf[y * w..(y + 1) * w];
            for x in 0..=r.min(w - 1) {
                acc = acc + row[x];
            }
            for x in 0..w {
                let n = (x.min(r) + 1 + r.min(w - 1 - x)) as f32;
                tmp[y * w + x] = acc * (1.0 / n);
                if x + r + 1 < w { acc = acc + row[x + r + 1]; }
                if x >= r { acc = acc - row[x - r]; }
            }
        }
        for x in 0..w {
            let mut acc = v3(0.0, 0.0, 0.0);
            for y in 0..=r.min(h - 1) {
                acc = acc + tmp[y * w + x];
            }
            for y in 0..h {
                let n = (y.min(r) + 1 + r.min(h - 1 - y)) as f32;
                buf[y * w + x] = acc * (1.0 / n);
                if y + r + 1 < h { acc = acc + tmp[(y + r + 1) * w + x]; }
                if y >= r { acc = acc - tmp[(y - r) * w + x]; }
            }
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        eprintln!("usage: render3d scene.txt out_dir");
        std::process::exit(2);
    }
    let text = fs::read_to_string(&args[1]).expect("read scene");
    let out = std::path::PathBuf::from(&args[2]);
    fs::create_dir_all(&out).expect("create out dir");
    let (st, mut prims) = parse(&text);
    if prims.is_empty() {
        eprintln!("render3d: empty scene");
        std::process::exit(1);
    }
    normalise(&mut prims);
    let nprims = prims.len();
    let bvh = Flat::build(prims);
    let (w, h, ss) = (st.w, st.h, st.ss);
    let aspect = w as f32 / h as f32;
    let threads = std::thread::available_parallelism().map(|n| n.get()).unwrap_or(2);
    let cl = cells(9);
    let tan = (st.fov.to_radians() * 0.5).tan();
    eprintln!("render3d: {nprims} primitives, {}x{} x{} frames, ss {ss}, {threads} threads", w, h, st.frames);

    for f in 0..st.frames {
        let phase = std::f32::consts::TAU * f as f32 / st.frames as f32;
        let az = phase * st.spin;
        let el = st.elev.to_radians();
        let cam = v3(el.cos() * az.sin(), el.sin(), el.cos() * az.cos()) * st.dist;
        let fwd = (-cam).norm();
        let right = fwd.cross(v3(0.0, 1.0, 0.0)).norm();
        let up = right.cross(fwd);
        // studio lights, fixed to the camera so the specimen turns under them
        let key = (right * -0.55 + up * 0.75 - fwd * 0.45).norm();
        let fill = (right * 0.8 - up * 0.1 - fwd * 0.35).norm();
        let back = (right * 0.15 + up * 0.35 + fwd * 0.9).norm();

        let mut img = [vec![v3(0.0, 0.0, 0.0); w * h], vec![v3(0.0, 0.0, 0.0); w * h]];
        let mut glow = [vec![v3(0.0, 0.0, 0.0); w * h], vec![v3(0.0, 0.0, 0.0); w * h]];
        {
            let rows_per = (h + threads - 1) / threads;
            let (i0, i1) = img.split_at_mut(1);
            let (g0, g1) = glow.split_at_mut(1);
            let (d0, d1, l0, l1) = (&mut i0[0], &mut i1[0], &mut g0[0], &mut g1[0]);
            let chunks: Vec<_> = d0
                .chunks_mut(rows_per * w)
                .zip(d1.chunks_mut(rows_per * w))
                .zip(l0.chunks_mut(rows_per * w).zip(l1.chunks_mut(rows_per * w)))
                .collect();
            std::thread::scope(|sc| {
                for (ci, ((a, b), (ga, gb))) in chunks.into_iter().enumerate() {
                    let bvh = &bvh;
                    let st = &st;
                    let cl = &cl;
                    sc.spawn(move || {
                        let y0 = ci * rows_per;
                        for (ly, (rowa, rowb)) in a.chunks_mut(w).zip(b.chunks_mut(w)).enumerate() {
                            let y = y0 + ly;
                            for x in 0..w {
                                let mut acc = [v3(0.0, 0.0, 0.0); 2];
                                let mut bgc = [v3(0.0, 0.0, 0.0); 2];
                                let mut hits = 0.0f32;
                                let mut em = [v3(0.0, 0.0, 0.0); 2];
                                for sy in 0..ss {
                                    for sx in 0..ss {
                                        let u = (x as f32 + (sx as f32 + 0.5) / ss as f32) / w as f32;
                                        let v = (y as f32 + (sy as f32 + 0.5) / ss as f32) / h as f32;
                                        let rd = (fwd + right * ((u * 2.0 - 1.0) * tan * aspect) + up * ((1.0 - v * 2.0) * tan)).norm();
                                        let seed = (y * w + x) as u32 * 4 + (sy * ss + sx) as u32;
                                        let smp = trace(bvh, cam, rd, key, seed);
                                        if smp.hit {
                                            hits += 1.0;
                                        }
                                        for t in 0..2 {
                                            let th = &st.themes[t];
                                            if smp.hit {
                                                let c = shade(&smp, th, key, fill, back, st.dist);
                                                acc[t] = acc[t] + c;
                                                if smp.emit > 0.0 && th.dark {
                                                    em[t] = em[t] + c * smp.emit.min(1.0);
                                                }
                                            } else {
                                                bgc[t] = bgc[t] + background(th, u, v, aspect, phase, cl);
                                            }
                                        }
                                    }
                                }
                                // pack: tone-mapped hit colour blended over the untouched background, in sRGB
                                let k = 1.0 / (ss * ss) as f32;
                                let alpha = hits * k;
                                for t in 0..2 {
                                    let hitc = if hits > 0.0 { acc[t] * (1.0 / hits) } else { v3(0.0, 0.0, 0.0) };
                                    let bg = if hits < (ss * ss) as f32 { bgc[t] * (1.0 / ((ss * ss) as f32 - hits)) } else { v3(0.0, 0.0, 0.0) };
                                    let lit = v3(lin_to_srgb(aces(hitc.x * 1.1)), lin_to_srgb(aces(hitc.y * 1.1)), lin_to_srgb(aces(hitc.z * 1.1)));
                                    let back_s = v3(lin_to_srgb(bg.x), lin_to_srgb(bg.y), lin_to_srgb(bg.z));
                                    let px = lit * alpha + back_s * (1.0 - alpha);
                                    if t == 0 { rowa[x] = px } else { rowb[x] = px }
                                }
                                ga[ly * w + x] = em[0] * k;
                                gb[ly * w + x] = em[1] * k;
                            }
                        }
                    });
                }
            });
        }
        for t in 0..2 {
            let th = &st.themes[t];
            // bloom from emissive surfaces and bright highlights
            if th.dark {
                for i in 0..w * h {
                    let c = img[t][i];
                    let lum = 0.2126 * c.x + 0.7152 * c.y + 0.0722 * c.z;
                    let extra = if lum > 0.85 { v3(srgb_to_lin(c.x), srgb_to_lin(c.y), srgb_to_lin(c.z)) * ((lum - 0.85) * 2.0) } else { v3(0.0, 0.0, 0.0) };
                    glow[t][i] = glow[t][i] + extra;
                }
            }
            blur(&mut glow[t], w, h, 7);
            let bk = if th.dark { 0.9 } else { 0.35 };
            let page = th.page;
            let path = out.join(format!("{}-{:03}.ppm", if th.dark { "dark" } else { "light" }, f));
            let mut wtr = BufWriter::new(File::create(&path).expect("create frame"));
            write!(wtr, "P6\n{} {}\n255\n", w, h).unwrap();
            let mut bytes = Vec::with_capacity(w * h * 3);
            for y in 0..h {
                for x in 0..w {
                    let i = y * w + x;
                    let s0 = img[t][i];
                    let g = glow[t][i] * bk;
                    let soft = |base: f32, add: f32| {
                        let l = srgb_to_lin(base) + add;
                        lin_to_srgb(l / (1.0 + (l - 1.0).max(0.0)))
                    };
                    let mut o = if th.dark { v3(soft(s0.x, g.x), soft(s0.y, g.y), soft(s0.z, g.z)) } else { s0 };
                    // vignette into the exact page colour: no edge, no frame
                    let nx = (x as f32 + 0.5) / w as f32 * 2.0 - 1.0;
                    let ny = (y as f32 + 0.5) / h as f32 * 2.0 - 1.0;
                    let e = (nx.abs().powi(4) + ny.abs().powi(4)).powf(0.25);
                    let fade = smoothstep(0.72, 0.985, e);
                    o = o * (1.0 - fade) + page * fade;
                    bytes.push((o.x.clamp(0.0, 1.0) * 255.0 + 0.5) as u8);
                    bytes.push((o.y.clamp(0.0, 1.0) * 255.0 + 0.5) as u8);
                    bytes.push((o.z.clamp(0.0, 1.0) * 255.0 + 0.5) as u8);
                }
            }
            wtr.write_all(&bytes).unwrap();
        }
        if f % 12 == 0 {
            eprintln!("render3d: frame {}/{}", f + 1, st.frames);
        }
    }
}
