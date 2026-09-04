import os
import math
import time

import numpy as np
import py5_tools

import py5

# -------------------------
# CANVAS (A4 landscape @ 300 dpi)
# -------------------------
W, H = 3508, 2480

# Per-plate layers render at full resolution so upscaling never softens or
# blotches them. The wash layer has been dropped: it rendered at a low
# resolution and upscaling created visible dark blur spots, and it had no
# counterpart in the vector SVG. Speed comes from fewer stroke segments.
STROKE_SCALE = 1.0

# -------------------------
# OUTPUT FILENAMES
# -------------------------
PNG_FILE = "halo_full.png"
SVG_FILE = "halo.svg"

# -------------------------
# PALETTE (HSB: Hue, Saturation, Brightness)
# 5 paint colors, banded across the ellipse.
# -------------------------
PAINT_PALETTE = [
    (66, 42, 35),   # #555934 olive green
    (32, 11, 95),   # #F2E6D8 cream
    (29, 36, 75),   # #BF9B7A tan
    (22, 56, 55),   # #8C5B3E brown
    (22, 48, 35),   # #593E2E dark brown
]
PAPER_HSB = (35, 8, 92)   # soft warm cream background

# -------------------------
# ELLIPSE GEOMETRY — a symmetric row of plates around the vertical center
# -------------------------
# Each: (ex, ey, a, b, tilt, stroke_angle, drip_side, seed_offset)
# Center plate + mirrored pairs. Left plates lean left, right plates lean
# right, so the whole composition is symmetric about x = W/2.
NUM_PLATES = 5
GAP = 40  # minimum horizontal gap between adjacent plates

def _plate_layouts():
    # sizes, tilts, stroke angles, drip sides, vertical positions
    sizes = [(260, 115), (360, 160), (460, 200), (360, 160), (260, 115)]
    tilts = [math.radians(-22), math.radians(-22), 0.0,
             math.radians(22), math.radians(22)]
    stroke_angles = [math.radians(-25), math.radians(-25), math.radians(90),
                     math.radians(25), math.radians(25)]
    drip_sides = ["left", "left", "both", "right", "right"]
    eys = [H * 0.60, H * 0.55, H * 0.50, H * 0.55, H * 0.60]

    def half_extent(a, b, tilt):
        return math.sqrt((a * math.cos(tilt)) ** 2 + (b * math.sin(tilt)) ** 2)

    hx = [half_extent(a, b, tilt) for (a, b), tilt in zip(sizes, tilts)]
    cx = W / 2
    # place from the center outward so no two plates overlap
    xs = [cx] * NUM_PLATES
    xs[1] = cx - (hx[2] + hx[1] + GAP)
    xs[3] = cx + (hx[2] + hx[3] + GAP)
    xs[0] = xs[1] - (hx[1] + hx[0] + GAP)
    xs[4] = xs[3] + (hx[3] + hx[4] + GAP)

    layout = []
    for i in range(NUM_PLATES):
        ex = xs[i]
        # clamp so nothing is cut off (positions above already fit)
        if ex - hx[i] < 20:
            ex = hx[i] + 20
        if ex + hx[i] > W - 20:
            ex = W - hx[i] - 20
        layout.append((ex, eys[i], sizes[i][0], sizes[i][1], tilts[i],
                       stroke_angles[i], drip_sides[i], i * 100))
    return layout

PLATES = _plate_layouts()

# Defaults from the front plate (used as function default args)
EX, EY, A, B, TILT = PLATES[0][0], PLATES[0][1], PLATES[0][2], PLATES[0][3], PLATES[0][4]

# -------------------------
# GRAVITY (pulls to the right edge)
# -------------------------
GRAVITY_POWER = 2.0           # density contrast: sparse left, thick right

# -------------------------
# BRUSH STROKES (long parallel diagonal sweeps)
# -------------------------
N_STROKES = 700
SEG_PER_STROKE = 45
WOBBLE_AMP = 4.0
GAP_CHANCE = 0.015
STROKE_ANGLE = math.radians(25)
ANGLE_JITTER = math.radians(4)
STROKE_WIDTH_START_MIN = 30
STROKE_WIDTH_START_MAX = 50
STROKE_WIDTH_END_MIN = 8
STROKE_WIDTH_END_MAX = 18
CONVERGE_POINT_OFFSET = 1.0
STROKE_ALPHA_MIN = 40
STROKE_ALPHA_MAX = 65

# -------------------------
# DRIPS (waterfall-style: long, thin, mostly straight)
# -------------------------
N_DRIPS = 500
DRIP_BRISTLES = 2
DRIP_SPREAD = 2.0
DRIP_WOBBLE = 1.5
BEAD_CHANCE = 0.15
BEAD_MIN, BEAD_MAX = 4, 9
MID_BEAD_CHANCE = 0.05

# -------------------------
# SEEDS
# -------------------------
RNG_SEED = 7
NOISE_SEED = 11111


# -------------------------
# HELPER FUNCTIONS
# -------------------------
def to_screen(lx: float, ly: float, ex: float = EX, ey: float = EY,
              tilt: float = TILT) -> tuple:
    c, s = math.cos(tilt), math.sin(tilt)
    return ex + lx * c - ly * s, ey + lx * s + ly * c


def ellipse_local_point(u: float, a: float = A, b: float = B) -> tuple:
    return a * math.cos(u), b * math.sin(u)


def lerp_hsb(c0: tuple, c1: tuple, t: float) -> tuple:
    h0, s0, b0 = c0
    h1, s1, b1 = c1
    dh = h1 - h0
    if dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    h = (h0 + dh * t) % 360
    s = s0 + (s1 - s0) * t
    b = b0 + (b1 - b0) * t
    return (h, s, b)


def band_color(d: float, rng: np.random.Generator, bleed: float = 0.0,
               a: float = A) -> tuple:
    """Pick a palette color based on local-x position, but with randomness."""
    t = (d + bleed + a) / (2 * a)
    t = max(0.0, min(0.9999, t))
    n = len(PAINT_PALETTE)
    idx = int(t * n)
    if idx >= n:
        idx = n - 1
    if rng.random() < 0.30:
        shift = rng.choice([-2, -1, 1, 2])
        idx = max(0, min(n - 1, idx + shift))
    return PAINT_PALETTE[idx]


def jitter_color(base: tuple, rng: np.random.Generator) -> tuple:
    h = base[0] + rng.uniform(-5, 5)
    s = max(0.0, min(100.0, base[1] + rng.uniform(-9, 7)))
    b = max(0.0, min(100.0, base[2] + rng.uniform(-8, 8)))
    return (h, s, b)


def gravity_weight_x(lx: float, a: float = A) -> float:
    """Density weight for stroke placement at local-x position."""
    t = (lx + a) / (2 * a)
    return t ** GRAVITY_POWER


# -------------------------
# BRUSH STROKE (filled tapered polygon)
# -------------------------
def in_ellipse(lx: float, ly: float) -> bool:
    return (lx / A) ** 2 + (ly / B) ** 2 <= 1.0


def ray_ellipse_t(lx: float, ly: float, dx: float, dy: float,
                  a: float = A, b: float = B):
    """Find the entry/exit t values where a ray intersects the ellipse."""
    aa = (dx / a) ** 2 + (dy / b) ** 2
    bb = 2 * (lx * dx / a**2 + ly * dy / b**2)
    cc = (lx / a) ** 2 + (ly / b) ** 2 - 1.0
    disc = bb * bb - 4 * aa * cc
    if disc < 0 or aa == 0:
        return None
    sq = math.sqrt(disc)
    return ((-bb - sq) / (2 * aa), (-bb + sq) / (2 * aa))


def draw_brush_sweep(perp_offset: float, angle: float, rng: np.random.Generator,
                      color: tuple, alpha_boost: float = 0.0,
                      ex: float = EX, ey: float = EY, tilt: float = TILT,
                      a: float = A, b: float = B) -> None:
    """Draw a brush stroke as a filled tapered polygon crossing the ellipse."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    px, py = -sin_a, cos_a
    cx = px * perp_offset
    cy = py * perp_offset

    hits = ray_ellipse_t(cx, cy, cos_a, sin_a, a, b)
    if hits is None:
        return
    t_in, t_out = hits
    length = t_out - t_in
    if length < 30:
        return

    converge_t = t_in + (t_out - t_in) * CONVERGE_POINT_OFFSET
    w_start = rng.uniform(STROKE_WIDTH_START_MIN, STROKE_WIDTH_START_MAX)
    w_end = rng.uniform(STROKE_WIDTH_END_MIN, STROKE_WIDTH_END_MAX)
    n_seg = SEG_PER_STROKE
    noise_off = rng.uniform(0, 1000)

    top_edge = []
    bottom_edge = []
    for i in range(n_seg + 1):
        t = i / n_seg
        along = t_in + (converge_t - t_in) * t
        w = w_start + (w_end - w_start) * t
        pressure = math.sin(t * math.pi) ** 0.3
        w *= 0.7 + 0.3 * pressure
        wob = (py5.noise(noise_off + i * 0.25) - 0.5) * 2.0 * WOBBLE_AMP
        lx_c = cx + along * cos_a
        ly_c = cy + along * sin_a
        half_w = w / 2.0
        top_lx = lx_c + (half_w + wob) * px
        top_ly = ly_c + (half_w + wob) * py
        bot_lx = lx_c + (-half_w + wob) * px
        bot_ly = ly_c + (-half_w + wob) * py
        top_edge.append(to_screen(top_lx, top_ly, ex, ey, tilt))
        bottom_edge.append(to_screen(bot_lx, bot_ly, ex, ey, tilt))

    alpha = int(min(95, rng.uniform(STROKE_ALPHA_MIN, STROKE_ALPHA_MAX) + alpha_boost))
    py5.fill(*color, alpha)
    py5.no_stroke()
    py5.begin_shape()
    for sx, sy in top_edge:
        py5.vertex(sx, sy)
    for sx, sy in reversed(bottom_edge):
        py5.vertex(sx, sy)
    py5.end_shape(py5.CLOSE)


def draw_strokes(rng: np.random.Generator, ex: float = EX, ey: float = EY,
                  tilt: float = TILT, a: float = A, b: float = B,
                  stroke_angle: float = STROKE_ANGLE,
                  n_strokes: int = N_STROKES) -> None:
    """Fill the ellipse with long tapered brush strokes at the diagonal angle."""
    cos_a, sin_a = math.cos(stroke_angle), math.sin(stroke_angle)
    px, py = -sin_a, cos_a
    max_perp = 0
    for u_deg in range(0, 360, 5):
        u = math.radians(u_deg)
        lx, ly = a * math.cos(u), b * math.sin(u)
        perp = abs(lx * px + ly * py)
        if perp > max_perp:
            max_perp = perp
    max_perp *= 1.05

    placed = 0
    attempts = 0
    while placed < n_strokes and attempts < n_strokes * 20:
        attempts += 1
        perp = rng.uniform(-max_perp, max_perp)
        cx = px * perp
        if rng.random() > gravity_weight_x(cx, a):
            continue
        if rng.random() < GAP_CHANCE:
            continue
        angle = stroke_angle + rng.uniform(-ANGLE_JITTER, ANGLE_JITTER)
        col = jitter_color(band_color(cx, rng, bleed=rng.uniform(0, 30), a=a), rng)
        boost = gravity_weight_x(cx, a) * 15.0
        draw_brush_sweep(perp, angle, rng, col, alpha_boost=boost,
                         ex=ex, ey=ey, tilt=tilt, a=a, b=b)
        placed += 1


# -------------------------
# GRAVITY SLIDES (paint running toward the right edge)
# -------------------------
def ray_exit(x0: float, y0: float, dx: float, dy: float):
    """Find the screen point where a ray from (x0, y0) in direction (dx, dy)
    exits the tilted ellipse. Returns None if the point is outside."""
    c, s = math.cos(TILT), math.sin(TILT)
    rx = x0 - EX
    ry = y0 - EY
    lx = rx * c + ry * s
    ly = -rx * s + ry * c
    # direction in local frame
    d_lx = dx * c + dy * s
    d_ly = -dx * s + dy * c
    # ellipse: ((lx + t*d_lx)/A)^2 + ((ly + t*d_ly)/B)^2 = 1
    a = (d_lx / A) ** 2 + (d_ly / B) ** 2
    b = 2 * (lx * d_lx / A**2 + ly * d_ly / B**2)
    cc = (lx / A) ** 2 + (ly / B) ** 2 - 1.0
    disc = b * b - 4 * a * cc
    if disc < 0 or a == 0:
        return None
    t_exit = (-b + math.sqrt(disc)) / (2 * a)
    return x0 + t_exit * dx, y0 + t_exit * dy


def gen_slides(rng: np.random.Generator):
    """Diagonal streaks on the face: paint that slid from where it was
    applied toward the bottom-right edge. Each slide follows the stroke
    angle (top-left -> bottom-right) and ends at the ellipse boundary."""
    slides = []
    dir_angle = STROKE_ANGLE
    dx = math.cos(dir_angle)
    dy = math.sin(dir_angle)
    for _ in range(N_SLIDES):
        # origin: biased toward the upper-left (paint left from here)
        u = rng.uniform(0, 2 * math.pi)
        r = math.sqrt(rng.uniform(0.1, 0.8))
        lx = A * math.cos(u) * r
        ly = B * math.sin(u) * r
        # bias toward upper-left half
        if lx > 0 and rng.random() < 0.7:
            lx = -lx
        if ly > 0 and rng.random() < 0.6:
            ly = -ly
        x0, y0 = to_screen(lx, ly)

        exit_pt = ray_exit(x0, y0, dx, dy)
        if exit_pt is None:
            continue
        ex_x, ex_y = exit_pt
        length = math.hypot(ex_x - x0, ex_y - y0)
        if length < 40:
            continue
        # nudge start along the ray
        x0 += dx * rng.uniform(5, 20)
        y0 += dy * rng.uniform(5, 20)
        length = math.hypot(ex_x - x0, ex_y - y0)
        if length < 25:
            continue

        nseg = max(3, int(length / 26))
        noff = rng.uniform(0, 1000)
        centerline = []
        for i in range(nseg + 1):
            t = i / nseg
            x = x0 + (ex_x - x0) * t
            y = y0 + (ex_y - y0) * t
            wob = (py5.noise(noff + i * 0.4) - 0.5) * 2.0 * SLIDE_WOBBLE * (1.0 - t * 0.2)
            # perpendicular wobble
            centerline.append((x + (-dy) * wob, y + dx * wob))

        col = jitter_color(band_color(lx, rng, bleed=rng.uniform(20, 70)), rng)
        slides.append((centerline, col))
    return slides


def draw_slides(rng: np.random.Generator) -> None:
    slides = gen_slides(rng)
    py5.no_fill()
    py5.stroke_cap(py5.ROUND)
    py5.stroke_join(py5.ROUND)
    for centerline, col in slides:
        n = len(centerline)
        for b in range(DRIP_BRISTLES):
            offset = (b - (DRIP_BRISTLES - 1) / 2) * DRIP_SPREAD
            py5.stroke(*col, int(rng.uniform(60, 85)))
            py5.stroke_weight(rng.uniform(0.6, 1.2))
            py5.begin_shape()
            for i, (px, py) in enumerate(centerline):
                taper = 1.0 - (i / n) * 0.4
                py5.vertex(px, py + offset * taper)
            py5.end_shape()


# -------------------------
# DRIPS (off the right edge only)
# -------------------------
def gen_drips(rng: np.random.Generator, ex: float = EX, ey: float = EY,
               tilt: float = TILT, a: float = A, b: float = B,
               drip_side: str = "right", n_drips: int = N_DRIPS):
    """Drips fall straight down from the pooled edge of the ellipse.
    `drip_side` = "right" -> drips off the bottom-right (positive tilt)
    `drip_side` = "left"  -> drips off the bottom-left (negative tilt).
    Colors are picked randomly from the full palette (mixed pooled paint)."""
    drips = []
    for _ in range(n_drips):
        if drip_side == "both":
            # split drips evenly between the left and right lower arcs
            if rng.random() < 0.5:
                u = math.pi - rng.beta(2, 3) * (math.pi * 0.6)
            else:
                u = rng.beta(2, 3) * (math.pi * 0.6)
        elif drip_side == "left":
            # u near pi = leftmost; bias toward lower-left arc
            u = math.pi - rng.beta(2, 3) * (math.pi * 0.6)
        else:
            # u near 0 = rightmost; bias toward lower-right arc
            u = rng.beta(2, 3) * (math.pi * 0.6)
        lx, ly = ellipse_local_point(u, a, b)
        x0, y0 = to_screen(lx, ly, ex, ey, tilt)
        x0 += rng.uniform(-2.0, 8.0)
        y0 += rng.uniform(-2.0, 6.0)

        y_end = H - rng.uniform(0.0, 6.0)
        length = y_end - y0
        if length < 20:
            continue
        nseg = max(3, int(length / 34))
        noff = rng.uniform(0, 1000)
        centerline = []
        for i in range(nseg + 1):
            t = i / nseg
            y = y0 + length * t
            wob = (py5.noise(noff + i * 0.32) - 0.5) * 2.0 * DRIP_WOBBLE * (1.0 + 0.4 * t)
            centerline.append((x0 + wob, y))

        # color: pick randomly from full palette (pooled paint is mixed)
        idx = int(rng.integers(0, len(PAINT_PALETTE)))
        col = jitter_color(PAINT_PALETTE[idx], rng)

        beads = _beads_for(centerline, rng)
        drips.append((centerline, col, beads))
    return drips


def _beads_for(centerline, rng: np.random.Generator):
    beads = []
    if rng.random() < BEAD_CHANCE:
        br = rng.uniform(BEAD_MIN, BEAD_MAX)
        beads.append((centerline[-1][0], centerline[-1][1], br))
    if rng.random() < MID_BEAD_CHANCE:
        mi = int(rng.integers(1, len(centerline) - 1))
        br = rng.uniform(BEAD_MIN * 0.7, BEAD_MAX * 0.9)
        beads.append((centerline[mi][0], centerline[mi][1], br))
    return beads


def draw_drips(rng: np.random.Generator) -> None:
    drips = gen_drips(rng)
    py5.no_fill()
    py5.stroke_cap(py5.ROUND)
    py5.stroke_join(py5.ROUND)
    for centerline, col, beads in drips:
        for b in range(DRIP_BRISTLES):
            offset = (b - (DRIP_BRISTLES - 1) / 2) * DRIP_SPREAD
            py5.stroke(*col, int(rng.uniform(70, 95)))
            py5.stroke_weight(rng.uniform(0.7, 1.4))
            py5.begin_shape()
            for px, py in centerline:
                py5.vertex(px + offset, py)
            py5.end_shape()
        for bx, by, br in beads:
            py5.fill(*col, 100)
            py5.no_stroke()
            py5.circle(bx, by, br * 2)
            py5.no_fill()


# -------------------------
# COMPOSITE
# -------------------------
def draw_background() -> None:
    py5.background(*PAPER_HSB)


def draw_painting(rng: np.random.Generator) -> None:
    """Render all plates to separate buffers, blur each, then composite
    back-to-front (last plate = furthest back, drawn first)."""
    n = len(PLATES)
    for i, plate in enumerate(reversed(PLATES), 1):
        ex, ey, a, b, tilt, stroke_angle, drip_side, seed_off = plate
        t0 = time.time()
        print(f"[{time.time():7.1f}] rendering plate {i}/{n} "
              f"(a={a})...", flush=True)
        stroke_buf = _render_ellipse_to_buffer(
            np.random.default_rng(RNG_SEED + seed_off),
            ex, ey, tilt, a, b, drip_side=drip_side,
            stroke_angle=stroke_angle)
        t1 = time.time()
        print(f"[{t1:7.1f}] plate {i}/{n} rendered in {t1 - t0:.1f}s, "
              f"drawing...", flush=True)
        py5.image(stroke_buf, 0, 0, W, H)
        stroke_buf = None  # free memory between plates


def _pg_draw_strokes(pg, rng: np.random.Generator, ex: float, ey: float,
                      tilt: float, a: float, b: float,
                      stroke_angle: float = STROKE_ANGLE,
                      n_strokes: int = N_STROKES) -> None:
    """Draw brush strokes onto a graphics buffer for blending."""
    cos_a, sin_a = math.cos(stroke_angle), math.sin(stroke_angle)
    px, py_dir = -sin_a, cos_a
    max_perp = 0
    for u_deg in range(0, 360, 5):
        u = math.radians(u_deg)
        lx, ly = a * math.cos(u), b * math.sin(u)
        perp = abs(lx * px + ly * py_dir)
        if perp > max_perp:
            max_perp = perp
    max_perp *= 1.05

    placed = 0
    attempts = 0
    while placed < n_strokes and attempts < n_strokes * 20:
        attempts += 1
        perp = rng.uniform(-max_perp, max_perp)
        cx = px * perp
        if rng.random() > gravity_weight_x(cx, a):
            continue
        if rng.random() < GAP_CHANCE:
            continue
        angle = stroke_angle + rng.uniform(-ANGLE_JITTER, ANGLE_JITTER)
        col = jitter_color(band_color(cx, rng, bleed=rng.uniform(0, 30), a=a), rng)
        boost = gravity_weight_x(cx, a) * 15.0
        _pg_draw_brush_sweep(pg, perp, angle, rng, col, alpha_boost=boost,
                              ex=ex, ey=ey, tilt=tilt, a=a, b=b)
        placed += 1


def _pg_draw_brush_sweep(pg, perp_offset: float, angle: float, rng: np.random.Generator,
                          color: tuple, alpha_boost: float = 0.0,
                          ex: float = EX, ey: float = EY, tilt: float = TILT,
                          a: float = A, b: float = B) -> None:
    """Draw a filled tapered brush stroke onto a graphics buffer."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    px, py_dir = -sin_a, cos_a
    cx = px * perp_offset
    cy = py_dir * perp_offset

    hits = ray_ellipse_t(cx, cy, cos_a, sin_a, a, b)
    if hits is None:
        return
    t_in, t_out = hits
    length = t_out - t_in
    if length < 30:
        return

    converge_t = t_in + (t_out - t_in) * CONVERGE_POINT_OFFSET
    w_start = rng.uniform(STROKE_WIDTH_START_MIN, STROKE_WIDTH_START_MAX)
    w_end = rng.uniform(STROKE_WIDTH_END_MIN, STROKE_WIDTH_END_MAX)
    n_seg = SEG_PER_STROKE
    noise_off = rng.uniform(0, 1000)

    top_edge = []
    bottom_edge = []
    for i in range(n_seg + 1):
        t = i / n_seg
        along = t_in + (converge_t - t_in) * t
        w = w_start + (w_end - w_start) * t
        pressure = math.sin(t * math.pi) ** 0.3
        w *= 0.7 + 0.3 * pressure
        wob = (py5.noise(noise_off + i * 0.25) - 0.5) * 2.0 * WOBBLE_AMP
        lx_c = cx + along * cos_a
        ly_c = cy + along * sin_a
        half_w = w / 2.0
        top_lx = lx_c + (half_w + wob) * px
        top_ly = ly_c + (half_w + wob) * py_dir
        bot_lx = lx_c + (-half_w + wob) * px
        bot_ly = ly_c + (-half_w + wob) * py_dir
        top_edge.append(to_screen(top_lx, top_ly, ex, ey, tilt))
        bottom_edge.append(to_screen(bot_lx, bot_ly, ex, ey, tilt))

    alpha = int(min(95, rng.uniform(STROKE_ALPHA_MIN, STROKE_ALPHA_MAX) + alpha_boost))
    pg.fill(*color, alpha)
    pg.no_stroke()
    pg.begin_shape()
    for sx, sy in top_edge:
        pg.vertex(sx, sy)
    for sx, sy in reversed(bottom_edge):
        pg.vertex(sx, sy)
    pg.end_shape(py5.CLOSE)


def _pg_draw_drips(pg, rng: np.random.Generator, ex: float, ey: float,
                    tilt: float, a: float, b: float, drip_side: str = "right",
                    n_drips: int = N_DRIPS) -> None:
    """Draw drips onto a graphics buffer."""
    drips = gen_drips(rng, ex, ey, tilt, a, b, drip_side=drip_side,
                     n_drips=n_drips)
    pg.no_fill()
    pg.stroke_cap(py5.ROUND)
    pg.stroke_join(py5.ROUND)
    for centerline, col, beads in drips:
        for br in range(DRIP_BRISTLES):
            offset = (br - (DRIP_BRISTLES - 1) / 2) * DRIP_SPREAD
            pg.stroke(*col, int(rng.uniform(70, 95)))
            pg.stroke_weight(rng.uniform(0.7, 1.4))
            pg.begin_shape()
            for px, py in centerline:
                pg.vertex(px + offset, py)
            pg.end_shape()
        for bx, by, br in beads:
            pg.fill(*col, 100)
            pg.no_stroke()
            pg.circle(bx, by, br * 2)
            pg.no_fill()


def _render_ellipse_to_buffer(rng: np.random.Generator, ex: float, ey: float,
                                tilt: float, a: float, b: float,
                                drip_side: str = "right",
                                stroke_angle: float = STROKE_ANGLE):
    """Render strokes + drips for one ellipse to a transparent graphics
    buffer. Stroke and drip counts scale with plate area so smaller back
    plates aren't over-rendered. Blurred lightly for softer edges."""
    scale = (a * b) / (A * B)
    n_strokes = max(150, int(N_STROKES * scale))
    n_drips = max(100, int(N_DRIPS * scale))

    sw, sh = max(1, int(W * STROKE_SCALE)), max(1, int(H * STROKE_SCALE))

    # strokes + drips, blurred lightly for softer edges
    pg = py5.create_graphics(sw, sh)
    pg.begin_draw()
    pg.color_mode(py5.HSB, 360, 100, 100, 100)
    pg.background(0, 0, 100, 0)  # transparent
    pg.scale(STROKE_SCALE)
    _pg_draw_strokes(pg, rng, ex, ey, tilt, a, b, stroke_angle=stroke_angle,
                     n_strokes=n_strokes)
    _pg_draw_drips(pg, rng, ex, ey, tilt, a, b, drip_side=drip_side,
                   n_drips=n_drips)
    pg.end_draw()
    pg.apply_filter(py5.BLUR, 2)
    return pg


# -------------------------
# EXPORT
# -------------------------
def export_svg(svg_path: str, rng: np.random.Generator) -> None:
    """Export vector strokes directly (no blur) for plotting."""
    py5.begin_record(py5.SVG, svg_path)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    # Draw plates back-to-front
    n = len(PLATES)
    for i, plate in enumerate(reversed(PLATES), 1):
        ex, ey, a, b, tilt, stroke_angle, drip_side, seed_off = plate
        t0 = time.time()
        scale = (a * b) / (A * B)
        n_s = max(150, int(N_STROKES * scale))
        n_d = max(100, int(N_DRIPS * scale))
        draw_strokes(np.random.default_rng(RNG_SEED + seed_off),
                     ex, ey, tilt, a, b, stroke_angle=stroke_angle,
                     n_strokes=n_s)
        drips = gen_drips(np.random.default_rng(RNG_SEED + seed_off),
                         ex, ey, tilt, a, b, drip_side=drip_side,
                         n_drips=n_d)
        _draw_drip_list(drips)
        print(f"[{time.time():7.1f}] svg: plate {i}/{n} done in "
              f"{time.time() - t0:.1f}s", flush=True)
    py5.end_record()


def _draw_drip_list(drips) -> None:
    py5.no_fill()
    py5.stroke_cap(py5.ROUND)
    py5.stroke_join(py5.ROUND)
    for centerline, col, beads in drips:
        for br in range(DRIP_BRISTLES):
            offset = (br - (DRIP_BRISTLES - 1) / 2) * DRIP_SPREAD
            py5.stroke(*col, 85)
            py5.stroke_weight(1.0)
            py5.begin_shape()
            for px, py in centerline:
                py5.vertex(px + offset, py)
            py5.end_shape()
        for bx, by, br in beads:
            py5.fill(*col, 100)
            py5.no_stroke()
            py5.circle(bx, by, br * 2)
            py5.no_fill()


# -------------------------
# SETUP AND RUN
# -------------------------
def settings():
    py5.size(W, H)


def setup():
    t_start = time.time()
    print(f"[{t_start:7.1f}] setup: initialized canvas ({W}x{H})", flush=True)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.no_loop()

    np.random.seed(RNG_SEED)
    py5.noise_seed(NOISE_SEED)
    rng = np.random.default_rng(RNG_SEED)

    draw_background()

    print(f"[{time.time():7.1f}] setup: drawing background done", flush=True)
    draw_painting(rng)
    print(f"[{time.time():7.1f}] setup: all plates drawn", flush=True)

    here = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(here, PNG_FILE)
    svg_path = os.path.join(here, SVG_FILE)

    print(f"[{time.time():7.1f}] saving PNG...", flush=True)
    py5.save(png_path)
    print(f"[{time.time():7.1f}] saved PNG ({os.path.getsize(png_path)} bytes)",
          flush=True)

    print(f"[{time.time():7.1f}] exporting SVG (vector linework)...", flush=True)
    export_svg(svg_path, np.random.default_rng(RNG_SEED))
    print(f"[{time.time():7.1f}] saved SVG ({os.path.getsize(svg_path)} bytes)",
          flush=True)

    print(f"[{time.time():7.1f}] DONE in {time.time() - t_start:.0f}s "
          f"- PNG: {png_path}", flush=True)
    print(f"                       SVG: {svg_path}", flush=True)


py5.run_sketch()