import os
import py5
import numpy as np

W, H = 2048, 2048  # Perfect for Instagram/web

# -------------------------
# OUTPUT FILENAMES
# -------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_FILE = os.path.join(SCRIPT_DIR, "sage_green_web.png")

# -------------------------
# PALETTES
# -------------------------

# Sage green base tones (HSB)
SAGE_BASE = (95, 14, 70)      # soft sage green
SAGE_LINE = (95, 15, 68)      # line color almost same as base - very subtle

# Speckle colors - even closer to base for better blending
SPECKLE_COLORS = [
    (95, 14, 72),   # lighter than base
    (95, 13, 68),   # darker than base  
    (96, 12, 70),   # subtle variation
    (94, 14, 71),   # warm tint
    (96, 14, 69),   # cool tint
]

# -------------------------
# SEEDS
# -------------------------
BG_SEED = 77777
NOISE_SEED_BG = 33333
SPECKLE_SEED = 55555
EYE_SEED = 88888

# -------------------------
# EYE COLORS
# -------------------------
# Muted brick red for pupils - more subdued
PUPIL_COLOR = (8, 45, 40)  # HSB: more muted brick red
EYE_OUTLINE_COLOR = (95, 20, 45)  # darker sage for outline
EYE_WHITE_COLOR = (95, 8, 82)  # very light sage for eye white


def lerp(a, b, t):
    return a + (b - a) * t


def fbm(x, y, octaves=5, lacunarity=2.0, gain=0.5):
    """Fractal Brownian Motion for organic noise patterns."""
    amp, freq, s, norm = 0.5, 1.0, 0.0, 0.0
    for _ in range(octaves):
        s += amp * py5.noise(x * freq, y * freq)
        norm += amp
        freq *= lacunarity
        amp *= gain
    return s / norm


def draw_grid_background():
    """Render sage green background with very subtle grid lines like fine paper."""
    S = 1
    rw, rh = W // S, H // S
    pg = py5.create_graphics(rw, rh)

    np.random.seed(BG_SEED)
    py5.noise_seed(NOISE_SEED_BG)

    ox, oy = np.random.uniform(0, 9999), np.random.uniform(0, 9999)

    pg.begin_draw()
    pg.color_mode(py5.HSB, 360, 100, 100, 100)
    pg.no_stroke()

    h_base, s_base, b_base = SAGE_BASE
    grid_spacing = 12
    line_thickness = 0.6
    
    print(f"Rendering web background ({rw}x{rh})...")
    
    for y in range(rh):
        for x in range(rw):
            X, Y = x + ox, y + oy

            line_y_pos = (y // grid_spacing) * grid_spacing + grid_spacing // 2
            wiggle_y = np.sin(X / 40.0) * 0.3
            dist_from_h_line = abs(y - (line_y_pos + wiggle_y))
            
            line_x_pos = (x // grid_spacing) * grid_spacing + grid_spacing // 2
            wiggle_x = np.sin(Y / 40.0) * 0.3
            dist_from_v_line = abs(x - (line_x_pos + wiggle_x))
            
            dist_from_line = min(dist_from_h_line, dist_from_v_line)
            grain = fbm(X / 20.0, Y / 20.0, octaves=3)
            
            h, s, b = h_base, s_base, b_base
            
            if dist_from_line < line_thickness:
                line_intensity = 1 - (dist_from_line / line_thickness)
                h = lerp(h_base, SAGE_LINE[0], line_intensity * 0.12)
                s = lerp(s_base, SAGE_LINE[1], line_intensity * 0.08)
                b = lerp(b_base, SAGE_LINE[2], line_intensity * 0.06)
            else:
                h = h_base + (grain - 0.5) * 3
                s = np.clip(s_base + (grain - 0.5) * 5, 0, 100)
                b = np.clip(b_base + (grain - 0.5) * 8, 0, 100)

            pg.fill(h, s, b, 100)
            pg.rect(x, y, 1, 1)

    pg.end_draw()
    print("  Background done!")

    py5.background(h_base, s_base, b_base)
    py5.image(pg, 0, 0, W, H)


def draw_irregular_speckles():
    """Draw irregular, noisy speckles that blend with background."""
    np.random.seed(SPECKLE_SEED)
    
    py5.no_stroke()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    
    # Reduced for web
    n_clusters = 400
    print(f"Rendering {n_clusters} speckle clusters...")
    
    for _ in range(n_clusters):
        cx = np.random.uniform(0, W)
        cy = np.random.uniform(0, H)
        
        base_size = np.random.uniform(3, 10)
        color = SPECKLE_COLORS[np.random.randint(0, len(SPECKLE_COLORS))]
        alpha = np.random.uniform(12, 30)
        
        n_blobs = np.random.randint(6, 12)
        for i in range(n_blobs):
            angle = np.random.uniform(0, np.pi * 2)
            dist = np.random.uniform(0, base_size * 0.7)
            bx = cx + np.cos(angle) * dist
            by = cy + np.sin(angle) * dist
            bsize = base_size * np.random.uniform(0.5, 1.1)
            balpha = alpha * np.random.uniform(0.5, 0.9)
            
            py5.fill(color[0], color[1], color[2], balpha)
            py5.circle(bx, by, bsize)
        
        if np.random.random() > 0.3:
            py5.fill(color[0], color[1], min(color[2] + 3, 100), alpha * 0.6)
            py5.circle(cx, cy, base_size * 0.5)
        
        if np.random.random() > 0.4:
            n_satellites = np.random.randint(3, 8)
            for _ in range(n_satellites):
                sx = cx + np.random.uniform(-base_size * 2.5, base_size * 2.5)
                sy = cy + np.random.uniform(-base_size * 2.5, base_size * 2.5)
                py5.fill(color[0], color[1], color[2], alpha * np.random.uniform(0.2, 0.5))
                py5.circle(sx, sy, np.random.uniform(0.5, 3))
    
    # Fine speckles layer - reduced
    n_fine = 800
    print(f"Rendering {n_fine} fine speckles...")
    for _ in range(n_fine):
        fx = np.random.uniform(0, W)
        fy = np.random.uniform(0, H)
        fsize = np.random.uniform(0.5, 2.5)
        color = SPECKLE_COLORS[np.random.randint(0, len(SPECKLE_COLORS))]
        py5.fill(color[0], color[1], color[2], np.random.uniform(5, 18))
        py5.circle(fx, fy, fsize)


def draw_eye_shape(cx, cy, width, height):
    """Draw the eye shape (almond/football shape) for the white of the eye."""
    py5.no_stroke()
    py5.fill(EYE_WHITE_COLOR[0], EYE_WHITE_COLOR[1], EYE_WHITE_COLOR[2])
    
    py5.begin_shape()
    n_points = 100
    for i in range(n_points):
        t = i / (n_points - 1)
        angle = np.pi * 2 * t
        base_x = np.cos(angle)
        base_y = np.sin(angle)
        pinch = 1 - 0.15 * abs(base_x)
        x = cx + (width/2) * base_x
        y = cy + (height/2) * base_y * pinch
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)


def draw_irregular_pupil(cx, cy, radius, seed_offset=0):
    """Draw pupil with smooth organic texture."""
    np.random.seed(EYE_SEED + seed_offset)
    py5.noise_seed(EYE_SEED + seed_offset)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    
    S = 2  # Slightly scaled for performance
    buf_size = int(radius * 2 / S)
    pg = py5.create_graphics(buf_size, buf_size)
    pg.begin_draw()
    pg.color_mode(py5.HSB, 360, 100, 100, 100)
    pg.no_stroke()
    
    offset = buf_size / 2
    scale = 0.02 * S
    
    for py in range(buf_size):
        for px in range(buf_size):
            dx = (px - offset) * S
            dy = (py - offset) * S
            dist = np.sqrt(dx*dx + dy*dy)
            
            if dist > radius * 1.2:
                continue
            
            edge_factor = dist / radius
            n1 = py5.noise(px * scale, py * scale)
            n2 = py5.noise(px * scale * 2 + 50, py * scale * 2 + 50)
            texture = n1 * 0.6 + n2 * 0.4
            
            edge_noise = py5.noise(px * 0.04 * S + 200, py * 0.04 * S + 200)
            soft_threshold = 0.92 + edge_noise * 0.2
            
            if edge_factor > soft_threshold:
                continue
            
            alpha = 100
            if edge_factor > 0.65:
                alpha = 100 * (1 - (edge_factor - 0.65) / (soft_threshold - 0.65))
            
            h_var = PUPIL_COLOR[0] + (n2 - 0.5) * 2
            s_var = PUPIL_COLOR[1] + (texture - 0.5) * 6
            b_var = PUPIL_COLOR[2] + (texture - 0.5) * 12
            
            pg.fill(h_var, max(s_var, 0), max(min(b_var, 100), 0), max(alpha, 0))
            pg.rect(px, py, 1, 1)
    
    for _ in range(20):
        angle = np.random.uniform(0, np.pi * 2)
        dist = np.random.uniform(0, radius * 0.6)
        bx = offset + np.cos(angle) * dist / S
        by = offset + np.sin(angle) * dist / S
        bsize = radius * np.random.uniform(0.3, 0.5) / S
        
        if np.random.random() > 0.5:
            pg.fill(PUPIL_COLOR[0], max(PUPIL_COLOR[1] - 6, 0), min(PUPIL_COLOR[2] + 10, 100), 18)
        else:
            pg.fill(PUPIL_COLOR[0], min(PUPIL_COLOR[1] + 4, 100), max(PUPIL_COLOR[2] - 6, 0), 18)
        
        pg.ellipse(bx, by, bsize, bsize)
    
    pg.end_draw()
    py5.image(pg, cx - radius, cy - radius, radius * 2, radius * 2)


def draw_radiating_lines(cx, cy, inner_radius, outer_radius, n_lines=12):
    """Draw lines radiating from pupil."""
    py5.stroke(EYE_OUTLINE_COLOR[0], EYE_OUTLINE_COLOR[1], EYE_OUTLINE_COLOR[2])
    py5.stroke_weight(0.7)
    
    for i in range(n_lines):
        angle = (np.pi * 2 * i / n_lines)
        x1 = cx + np.cos(angle) * inner_radius
        y1 = cy + np.sin(angle) * inner_radius
        x2 = cx + np.cos(angle) * (outer_radius - 2)
        y2 = cy + np.sin(angle) * (outer_radius - 2)
        py5.line(x1, y1, x2, y2)


def draw_single_eye(cx, cy, eye_width, eye_height, pupil_radius, n_lines=14, seed_offset=0):
    """Draw a single eye at the given position."""
    draw_eye_shape(cx, cy, eye_width, eye_height)
    max_line_radius = eye_height/2 - 15
    draw_radiating_lines(cx, cy, pupil_radius + 8, max_line_radius, n_lines=n_lines)
    draw_irregular_pupil(cx, cy, pupil_radius, seed_offset)


def draw_seven_eyes():
    """Draw 7 eyes in a pattern (3 on left, 4 on right)."""
    np.random.seed(EYE_SEED)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    
    print("Rendering 7 eyes...")
    center_x, center_y = W // 2, H // 2
    
    # Scaled for 2048x2048
    eye_width = 280
    eye_height = 175
    pupil_radius = 18
    
    v_spacing = 245
    h_spacing = 350
    
    left_x = center_x - h_spacing/2
    right_x = center_x + h_spacing/2
    
    left_y_start = center_y - v_spacing
    for i in range(3):
        print(f"  Eye {i+1}/7...")
        ey = left_y_start + i * v_spacing
        draw_single_eye(left_x, ey, eye_width, eye_height, pupil_radius, seed_offset=i)
    
    right_y_start = center_y - v_spacing * 1.5
    for i in range(4):
        print(f"  Eye {i+4}/7...")
        ey = right_y_start + i * v_spacing
        draw_single_eye(right_x, ey, eye_width, eye_height, pupil_radius, seed_offset=i+100)
    print("  Eyes done!")


def setup():
    py5.size(W, H)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.no_loop()
    py5.no_stroke()

    draw_grid_background()
    draw_irregular_speckles()
    draw_seven_eyes()
    
    py5.save(PNG_FILE)

    print(f"Saved web PNG: {PNG_FILE}")
    py5.exit_sketch()


py5.run_sketch()
