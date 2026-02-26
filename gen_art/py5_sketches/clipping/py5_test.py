import numpy as np
import py5

def inside_circle(x, y, cx, cy, R):
    dx = x - cx
    dy = y - cy
    return (dx * dx + dy * dy) <= (R * R)

def draw_wavy_line_runs_clipped(xc, yc, R, k, segs, fx, fy, z, amp, n_lines):
    """
    Draw one noisy polyline across the circle bbox, but only emit vertex runs
    where points are inside the circle. Uses begin_shape/vertex/end_shape
    to reduce SVG primitives.
    """
    base_y = (yc - R) + (k / (n_lines - 1)) * (2 * R)

    in_run = False

    for s in range(segs + 1):
        u = s / segs
        x = (xc - R) + u * (2 * R)
        n = py5.noise(x * fx, k * fy, z)
        y = base_y + py5.remap(n, 0, 1, -amp, amp)

        inside = inside_circle(x, y, xc, yc, R)

        if inside and not in_run:
            py5.begin_shape()
            py5.vertex(x, y)
            in_run = True
        elif inside and in_run:
            py5.vertex(x, y)
        elif (not inside) and in_run:
            py5.end_shape()
            in_run = False

    if in_run:
        py5.end_shape()

def setup():
    # SVG export mode: no preview window, writes vector output
    py5.size(1500, 1500, py5.SVG, "circle_grid.svg")
    py5.pixel_density(1)
    py5.color_mode(py5.HSB, 360, 100, 100)
    py5.background(35, 12, 96)

    padding = 150
    x_circle = np.linspace(padding, py5.width - padding, 10)
    y_circle = np.linspace(padding, py5.height - padding, 10)

    terracotta = (28, 32, 72)   # (H, S, B)
    ink_hsb    = (205, 25, 85)

    r = 125
    R = r / 2

    py5.background(35, 10, 95)

    py5.stroke_cap(py5.ROUND)
    py5.stroke_join(py5.ROUND)

    # ---- speed / look knobs ----
    n_lines = 100
    segs = 90
    amp = 20
    fx = 0.02
    fy = 0.20
    darken_by = 35  # how much darker the bottom row gets vs top

    for i, xc in enumerate(x_circle):
        for j, yc in enumerate(y_circle):

            # --- vertical brightness gradient for circle fill ---
            h, s, base_b = terracotta
            b = py5.remap(j, 0, len(y_circle) - 1, base_b, base_b - darken_by)

            py5.no_stroke()
            py5.fill(h, s, b)
            py5.circle(xc, yc, r)

            # texture lines (vector)
            py5.no_fill()
            py5.stroke(*ink_hsb)
            py5.stroke_weight(0.5)

            z = i * 10 + j

            for k in range(n_lines):
                draw_wavy_line_runs_clipped(xc, yc, R, k, segs, fx, fy, z, amp, n_lines)

    # force flush/write
    py5.exit_sketch()

py5.run_sketch()