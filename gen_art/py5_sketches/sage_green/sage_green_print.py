import os
import py5
import numpy as np

W, H = 7200, 7200

# -------------------------
# OUTPUT FILENAMES
# -------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_FILE = os.path.join(SCRIPT_DIR, "sage_green_full.png")

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
    np.random.seed(BG_SEED)
    py5.noise_seed(NOISE_SEED_BG)
    
    ox, oy = np.random.uniform(0, 9999), np.random.uniform(0, 9999)
    
    h_base, s_base, b_base = SAGE_BASE
    grid_spacing = 8
    line_thickness = 0.8
    
    # Draw directly to canvas, no offscreen buffer needed
    py5.background(h_base, s_base, b_base)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.no_stroke()
    
    print(f"Rendering background ({W}x{H} pixels)...")
    
    # Process in horizontal strips to avoid memory issues
    strip_height = 200
    total_strips = (H + strip_height - 1) // strip_height
    
    for strip in range(total_strips):
        pct = (strip / total_strips) * 100
        print(f"  Background: {pct:.0f}%")
        
        y_start = strip * strip_height
        y_end = min(y_start + strip_height, H)
        
        for y in range(y_start, y_end):
            for x in range(W):
                X, Y = x + ox, y + oy

                # Horizontal lines
                line_y_pos = (y // grid_spacing) * grid_spacing + grid_spacing // 2
                wiggle_y = np.sin(X / 40.0) * 0.3
                dist_from_h_line = abs(y - (line_y_pos + wiggle_y))
                
                # Vertical lines
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
                    # Stronger paper grain for visibility at high res
                    h = h_base + (grain - 0.5) * 4
                    s = np.clip(s_base + (grain - 0.5) * 6, 0, 100)
                    b = np.clip(b_base + (grain - 0.5) * 10, 0, 100)

                py5.stroke(h, s, b, 100)
                py5.point(x, y)
    
    print("  Background: 100% - done!")


def draw_irregular_speckles():
    """Draw irregular, noisy speckles that blend with background."""
    np.random.seed(SPECKLE_SEED)
    
    py5.no_stroke()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    
    # Large speckles
    n_clusters = 6000  # much more speckles for large canvas
    print(f"Rendering {n_clusters} large speckle clusters...")
    
    for _ in range(n_clusters):
        cx = np.random.uniform(0, W)
        cy = np.random.uniform(0, H)
        
        base_size = np.random.uniform(4, 18)  # larger speckles for visibility
        color = SPECKLE_COLORS[np.random.randint(0, len(SPECKLE_COLORS))]
        alpha = np.random.uniform(15, 40)  # more visible alpha
        
        # Draw irregular blob with more overlapping circles for softness
        n_blobs = np.random.randint(12, 25)  # denser blobs per cluster
        for i in range(n_blobs):
            angle = np.random.uniform(0, np.pi * 2)
            dist = np.random.uniform(0, base_size * 0.7)
            bx = cx + np.cos(angle) * dist
            by = cy + np.sin(angle) * dist
            bsize = base_size * np.random.uniform(0.5, 1.1)
            balpha = alpha * np.random.uniform(0.6, 1.0)  # stronger alpha
            
            py5.fill(color[0], color[1], color[2], balpha)
            py5.circle(bx, by, bsize)
        
        # Core of the speckle - slightly brighter for depth
        if np.random.random() > 0.3:
            py5.fill(color[0], color[1], min(color[2] + 3, 100), alpha * 0.6)
            py5.circle(cx, cy, base_size * 0.5)
        
        # More satellite speckles for blending
        if np.random.random() > 0.4:
            n_satellites = np.random.randint(8, 18)
            for _ in range(n_satellites):
                sx = cx + np.random.uniform(-base_size * 2.5, base_size * 2.5)
                sy = cy + np.random.uniform(-base_size * 2.5, base_size * 2.5)
                py5.fill(color[0], color[1], color[2], alpha * np.random.uniform(0.2, 0.5))
                py5.circle(sx, sy, np.random.uniform(1, 5))
    
    # Fine speckles layer - smaller, more numerous
    n_fine = 15000
    print(f"Rendering {n_fine} fine speckles...")
    for _ in range(n_fine):
        fx = np.random.uniform(0, W)
        fy = np.random.uniform(0, H)
        fsize = np.random.uniform(0.5, 3)
        color = SPECKLE_COLORS[np.random.randint(0, len(SPECKLE_COLORS))]
        py5.fill(color[0], color[1], color[2], np.random.uniform(5, 20))
        py5.circle(fx, fy, fsize)


def draw_triangle_outline(cx, cy, size, stroke_weight=1.5):
    """Draw an equilateral triangle outline centered at cx, cy."""
    py5.stroke(EYE_OUTLINE_COLOR[0], EYE_OUTLINE_COLOR[1], EYE_OUTLINE_COLOR[2])
    py5.stroke_weight(stroke_weight)
    py5.no_fill()
    
    # Calculate triangle points (pointing up)
    h = size * np.sqrt(3) / 2
    p1 = (cx, cy - h * 2/3)  # top
    p2 = (cx - size/2, cy + h/3)  # bottom left
    p3 = (cx + size/2, cy + h/3)  # bottom right
    
    py5.triangle(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])


def draw_eye_shape(cx, cy, width, height):
    """Draw the eye shape (almond/football shape) for the white of the eye."""
    py5.no_stroke()
    py5.fill(EYE_WHITE_COLOR[0], EYE_WHITE_COLOR[1], EYE_WHITE_COLOR[2])
    
    # Create smooth almond shape using parametric curve
    py5.begin_shape()
    n_points = 100
    for i in range(n_points):
        t = i / (n_points - 1)
        # Full circle
        angle = np.pi * 2 * t
        
        # Almond shape: use modified parametric equation
        # Start with ellipse and pinch the ends
        base_x = np.cos(angle)
        base_y = np.sin(angle)
        
        # Pinch factor: reduces width at left/right ends (where cos(angle) is near -1 or 1)
        # and keeps height in middle
        pinch = 1 - 0.15 * abs(base_x)  # Slight pinch at ends
        
        x = cx + (width/2) * base_x
        y = cy + (height/2) * base_y * pinch
        
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)


def draw_paint_brush_stroke(pg, cx, cy, length, width, angle, h, s, b, alpha=100):
    """Draw a single fully blended paint brush stroke - indistinguishable."""
    pg.push_matrix()
    pg.translate(cx, cy)
    pg.rotate(angle)
    
    # Very many steps with tiny ellipses for complete blending
    steps = int(length * 15)
    
    for i in range(steps):
        t = i / steps
        # Smooth taper
        taper = np.sin(np.pi * t) ** 0.7
        w = width * taper
        
        x = -length/2 + length * t
        # Minimal waviness for smoother appearance
        y = np.sin(t * np.pi * 2) * 0.05 + np.random.uniform(-0.05, 0.05)
        
        if w > 0.15:
            # Many overlapping soft circles for complete blending
            for j in range(10):
                offset_x = np.random.uniform(-w*0.3, w*0.3)
                offset_y = np.random.uniform(-w*0.3, w*0.3)
                h_var = h + np.random.uniform(-0.2, 0.2)
                s_var = s + np.random.uniform(-0.8, 0.8)
                b_var = b + np.random.uniform(-1, 1)
                a_var = alpha + np.random.uniform(-2, 2)
                pg.fill(h_var, s_var, b_var, max(a_var, 5))
                # Very small overlapping ellipses that merge together
                size = w * (0.35 + j * 0.08)
                pg.ellipse(x + offset_x, y + offset_y, size, size * 0.95)
    
    pg.pop_matrix()


def draw_irregular_pupil(cx, cy, radius, seed_offset=0):
    """Draw pupil with smooth organic texture for large format printing."""
    np.random.seed(EYE_SEED + seed_offset)
    py5.noise_seed(EYE_SEED + seed_offset)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    
    # Buffer size - use 2x radius for full resolution
    S = 1  # Full resolution for crisp pupil
    buf_size = int(radius * 2 / S)
    print(f"    Pupil {seed_offset}: rendering {buf_size}x{buf_size}...")
    pg = py5.create_graphics(buf_size, buf_size)
    pg.begin_draw()
    pg.color_mode(py5.HSB, 360, 100, 100, 100)
    pg.no_stroke()
    
    offset = buf_size / 2
    
    # Scale for smooth texture
    scale = 0.02 * S
    
    # Draw base shape with smooth gradient
    for py in range(buf_size):
        for px in range(buf_size):
            dx = (px - offset) * S
            dy = (py - offset) * S
            dist = np.sqrt(dx*dx + dy*dy)
            
            if dist > radius * 1.2:
                continue
            
            edge_factor = dist / radius
            
            # Smooth multi-octave noise
            n1 = py5.noise(px * scale, py * scale)
            n2 = py5.noise(px * scale * 2 + 50, py * scale * 2 + 50)
            
            texture = n1 * 0.6 + n2 * 0.4
            
            # Soft organic edge
            edge_noise = py5.noise(px * 0.04 * S + 200, py * 0.04 * S + 200)
            soft_threshold = 0.92 + edge_noise * 0.2
            
            if edge_factor > soft_threshold:
                continue
            
            # Alpha fade
            alpha = 100
            if edge_factor > 0.65:
                alpha = 100 * (1 - (edge_factor - 0.65) / (soft_threshold - 0.65))
            
            # Subtle variation
            h_var = PUPIL_COLOR[0] + (n2 - 0.5) * 2
            s_var = PUPIL_COLOR[1] + (texture - 0.5) * 6
            b_var = PUPIL_COLOR[2] + (texture - 0.5) * 12
            
            pg.fill(h_var, max(s_var, 0), max(min(b_var, 100), 0), max(alpha, 0))
            pg.rect(px, py, 1, 1)
    
    # Large soft blobs for organic texture
    for _ in range(25):
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
    # Draw eye white
    draw_eye_shape(cx, cy, eye_width, eye_height)
    
    # Draw radiating lines from pupil to edge of eye
    max_line_radius = eye_height/2 - 50
    draw_radiating_lines(cx, cy, pupil_radius + 20, max_line_radius, n_lines=n_lines)
    
    # Draw irregular pupil with paint texture
    draw_irregular_pupil(cx, cy, pupil_radius, seed_offset)


def draw_seven_eyes():
    """Draw 7 eyes in a pattern (3 on left, 4 on right) like the reference image."""
    np.random.seed(EYE_SEED)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    
    print("Rendering 7 eyes...")
    center_x, center_y = W // 2, H // 2
    
    # Eye dimensions - scaled for large canvas print
    eye_width = 960
    eye_height = 600
    pupil_radius = 60  # scaled pupil size
    
    # Arrange 7 eyes: 3 on left column, 4 on right column
    # Vertical spacing between eyes - scaled for large canvas
    v_spacing = 840
    h_spacing = 1200  # horizontal spacing between columns
    
    # Left column has 3 eyes - positioned slightly left of center
    left_x = center_x - h_spacing/2
    # Right column has 4 eyes - positioned slightly right of center
    right_x = center_x + h_spacing/2
    
    # Left column: 3 eyes (vertically centered group)
    left_y_start = center_y - v_spacing
    for i in range(3):
        print(f"  Eye {i+1}/7 (left column)...")
        ey = left_y_start + i * v_spacing
        draw_single_eye(left_x, ey, eye_width, eye_height, pupil_radius, seed_offset=i)
    
    # Right column: 4 eyes (starts higher to accommodate 4 eyes)
    right_y_start = center_y - v_spacing * 1.5
    for i in range(4):
        print(f"  Eye {i+4}/7 (right column)...")
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

    print(f"Saved PNG: {PNG_FILE}")
    py5.exit_sketch()


py5.run_sketch()
