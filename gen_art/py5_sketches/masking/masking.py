import py5
import numpy as np

W, H = 900, 900

# -------------------------
# OUTPUT FILENAMES
# -------------------------
PNG_FILE = "blue_circle_lines_full.png"
SVG_FILE = "blue_circle_lines_only.svg"

# -------------------------
# PALETTES
# -------------------------

# Darker blue watercolor paper palette (HSB)
PAPER_PALETTE = [
    (208, 28, 72),  # darker blue paper base
    (204, 34, 66),  # soft darker blue
    (200, 24, 62),  # steel blue
    (197, 46, 54),  # medium blue accent
    (192, 58, 46),  # deep blue accent
]

BASE = PAPER_PALETTE[0]
ACCENTS = PAPER_PALETTE[1:]

# Neutral brown line palette
LINE_PALETTE = [
    (28, 26, 95),
    (22, 48, 75),
    (22, 26, 85),
    (16, 73, 55),
    (16, 44, 45),
]

# -------------------------
# CIRCLE MASK
# -------------------------
CX, CY = W / 2, H / 2
R = 75

# -------------------------
# SEEDS
# -------------------------
# These make the on-screen lines and exported SVG match exactly.
BG_SEED = 12345
LINE_SEED = 54321
NOISE_SEED_BG = 11111
NOISE_SEED_LINES = 22222

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_hue(h1, h2, t):
    d = ((h2 - h1 + 180) % 360) - 180
    return (h1 + d * t) % 360

def fbm(x, y, octaves=5, lacunarity=2.0, gain=0.5):
    amp, freq, s, norm = 0.5, 1.0, 0.0, 0.0
    for _ in range(octaves):
        s += amp * py5.noise(x * freq, y * freq)
        norm += amp
        freq *= lacunarity
        amp *= gain
    return s / norm

def random_point_in_circle(cx, cy, r):
    a = np.random.uniform(0, np.pi * 2)
    rr = r * np.sqrt(np.random.uniform())
    return cx + np.cos(a) * rr, cy + np.sin(a) * rr

def inside_circle(x, y, cx, cy, r):
    dx = x - cx
    dy = y - cy
    return dx * dx + dy * dy <= r * r

def draw_walk_lines():
    n_walkers = 400
    steps_per = (30, 80)
    step_len = (2.0, 4.5)

    turn_amt = 0.6
    field_scale = 0.010
    wobble_scale = 0.020
    wobble_amt = 0.50

    w_base = (0.35, 1.6)
    w_amp = (0.15, 0.9)

    py5.push_style()
    py5.no_fill()
    py5.stroke_cap(py5.ROUND)

    for _ in range(n_walkers):
        x, y = random_point_in_circle(CX, CY, R)
        ang = np.random.uniform(0, np.pi * 2)

        steps = np.random.randint(steps_per[0], steps_per[1] + 1)
        sl = np.random.uniform(step_len[0], step_len[1])

        base_w = np.random.uniform(w_base[0], w_base[1])
        amp_w = np.random.uniform(w_amp[0], w_amp[1])

        phase = np.random.uniform(0, np.pi * 2)
        w_freq = np.random.uniform(0.02, 0.07)

        # Bias toward darker/more neutral browns
        ih, isat, ibri = LINE_PALETTE[np.random.randint(1, len(LINE_PALETTE))]
        py5.stroke(ih, isat, ibri, 20)

        px, py = x, y

        for i in range(steps):
            if not inside_circle(px, py, CX, CY, R):
                break

            u = px * field_scale
            v = py * field_scale

            flow = (
                np.sin(u * 6.0) +
                np.cos(v * 6.0) +
                (py5.noise(u * 2.0, v * 2.0) - 0.5)
            )

            wob = (
                np.sin(px * wobble_scale + phase) +
                np.cos(py * wobble_scale - phase)
            )

            ang += flow * turn_amt * 0.08 + wob * wobble_amt * 0.05

            nx = px + np.cos(ang) * sl
            ny = py + np.sin(ang) * sl

            if not inside_circle(nx, ny, CX, CY, R):
                break

            w = base_w + amp_w * (0.5 + 0.5 * np.sin(i * w_freq + phase))
            py5.stroke_weight(max(0.1, w))
            py5.line(px, py, nx, ny)

            px, py = nx, ny

    py5.pop_style()

def draw_background():
    S = 2
    rw, rh = W // S, H // S
    pg = py5.create_graphics(rw, rh)

    np.random.seed(BG_SEED)
    py5.noise_seed(NOISE_SEED_BG)

    ox, oy = np.random.uniform(0, 9999), np.random.uniform(0, 9999)

    pg.begin_draw()
    pg.color_mode(py5.HSB, 360, 100, 100, 100)
    pg.no_stroke()

    for y in range(rh):
        for x in range(rw):
            X, Y = x + ox, y + oy

            big = fbm(X / 520.0, Y / 520.0, octaves=4)
            mid = fbm(X / 150.0, Y / 150.0, octaves=5)
            fine = fbm(X / 45.0, Y / 45.0, octaves=3)

            f = 0.15 * big + 0.55 * mid + 0.30 * fine

            h, s, b = BASE
            b = np.clip(b + (f - 0.5) * 42, 0, 100)
            s = np.clip(s + (fine - 0.5) * 5, 0, 100)

            bloom = fbm((X + 2000) / 320.0, (Y + 4000) / 320.0, octaves=4)
            if bloom > 0.80:
                idx = int(fbm((X + 8000) / 120.0, (Y + 9000) / 120.0, octaves=3) * 999) % len(ACCENTS)
                ah, aS, aB = ACCENTS[idx]
                t = np.clip((bloom - 0.80) / 0.20, 0, 1)

                h = lerp_hue(h, ah, t * 0.18)
                s = lerp(s, aS, t * 0.28)
                b = lerp(b, aB, t * 0.18)

            pg.fill(h, s, b, 100)
            pg.rect(x, y, 1, 1)

    pg.end_draw()

    pg.begin_draw()
    pg.apply_filter(py5.BLUR, 1)
    pg.end_draw()

    py5.background(BASE[0], BASE[1], BASE[2])
    py5.image(pg, 0, 0, W, H)

def draw_lines_with_fixed_seed():
    np.random.seed(LINE_SEED)
    py5.noise_seed(NOISE_SEED_LINES)
    draw_walk_lines()

def export_svg():
    # begin_record() records subsequent drawing commands to the SVG file
    py5.begin_record(py5.SVG, SVG_FILE)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.no_fill()

    # No background here — export linework only as vector
    draw_lines_with_fixed_seed()

    py5.end_record()

def setup():
    py5.size(W, H)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.no_loop()
    py5.no_stroke()

    # Draw full artwork to screen
    draw_background()
    draw_lines_with_fixed_seed()

    # Save full raster artwork
    py5.save(PNG_FILE)

    # Save vector linework
    export_svg()

    print(f"Saved PNG: {PNG_FILE}")
    print(f"Saved SVG: {SVG_FILE}")

py5.run_sketch()