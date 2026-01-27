import vsketch
import numpy as np 
import math
import random

class RecursiveTriangleSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    segments = 18
    triangle_size = 35  # mm

    # Waviness down the page
    amp_top = 0.3       # mm at top
    amp_bottom = 2.5    # mm at bottom
    freq_top = 0.05
    freq_bottom = 0.12
    noise_offset = 1000.0

    # Rotation down the page (max random rotation in degrees)
    rot_top = 5         # degrees max at top
    rot_bottom = 140    # degrees max at bottom

    def wavy_edge(self, vsk, a, b, amp_mm, noise_freq, seed=0.0):
        x1, y1 = a
        x2, y2 = b

        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return

        # unit perpendicular
        nx = -dy / length
        ny = dx / length

        pts = []
        for i in range(self.segments + 1):
            t = i / self.segments
            x = x1 + dx * t
            y = y1 + dy * t

            n = vsk.noise(
                (x + self.noise_offset + seed) * noise_freq,
                (y + self.noise_offset + seed) * noise_freq,
            ) - 0.5

            # fade to 0 at endpoints so corners stay clean
            fade = math.sin(math.pi * t)

            off = n * amp_mm * 2.0 * fade
            pts.append((x + nx * off, y + ny * off))

        for p, q in zip(pts[:-1], pts[1:]):
            vsk.line(p[0], p[1], q[0], q[1])

    def draw_triangle_edges_wavy(self, vsk, p1, p2, p3, amp_mm, noise_freq):
        self.wavy_edge(vsk, p1, p2, amp_mm, noise_freq, seed=0.0)
        self.wavy_edge(vsk, p2, p3, amp_mm, noise_freq, seed=17.3)
        self.wavy_edge(vsk, p3, p1, amp_mm, noise_freq, seed=42.7)

    def draw_triangle(self, vsk, p1, p2, p3, depth, amp_mm, noise_freq, g):
        if depth == 0:
            self.draw_triangle_edges_wavy(vsk, p1, p2, p3, amp_mm, noise_freq)
            return

        # rotate on even depths
        if depth:
            cx = (p1[0] + p2[0] + p3[0]) / 3.0
            cy = (p1[1] + p2[1] + p3[1]) / 3.0

            vsk.pushMatrix()
            vsk.translate(cx, cy)

            max_deg = self.rot_top + (self.rot_bottom - self.rot_top) * g
            angle_deg = random.uniform(-max_deg, max_deg)
            vsk.rotate(np.deg2rad(angle_deg))

            vsk.translate(-cx, -cy)

            self._subdivide_and_recurse(vsk, p1, p2, p3, depth, amp_mm, noise_freq, g)
            vsk.popMatrix()
        else:
            self._subdivide_and_recurse(vsk, p1, p2, p3, depth, amp_mm, noise_freq, g)

    def _subdivide_and_recurse(self, vsk, p1, p2, p3, depth, amp_mm, noise_freq, g):
        mid12 = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
        mid23 = ((p2[0] + p3[0]) / 2.0, (p2[1] + p3[1]) / 2.0)
        mid31 = ((p3[0] + p1[0]) / 2.0, (p3[1] + p1[1]) / 2.0)

        self.draw_triangle(vsk, p1, mid12, mid31, depth - 1, amp_mm, noise_freq, g)
        self.draw_triangle(vsk, p2, mid23, mid12, depth - 1, amp_mm, noise_freq, g)
        self.draw_triangle(vsk, p3, mid31, mid23, depth - 1, amp_mm, noise_freq, g)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # Grid of triangle centers
        xs = np.linspace(20, 160, 5)
        ys = np.linspace(20, 200, 5)

        # For mapping y -> [0,1]
        y_min = float(np.min(ys))
        y_max = float(np.max(ys))
        y_span = max(1e-9, (y_max - y_min))

        depth = 4

        side = self.triangle_size
        h = math.sqrt(3) / 2.0 * side

        for row_idx, py in enumerate(ys):
            # different stroke per row
            vsk.stroke(row_idx + 1)

            # 0 at top, 1 at bottom (optionally ease: **1.7)
            g = (py - y_min) / y_span

            amp = self.amp_top + (self.amp_bottom - self.amp_top) * g
            freq = self.freq_top + (self.freq_bottom - self.freq_top) * g

            for px in xs:
                # Equilateral triangle with centroid at (px, py)
                p1 = (px, py + (2.0 / 3.0) * h)
                p2 = (px - side / 2.0, py - (1.0 / 3.0) * h)
                p3 = (px + side / 2.0, py - (1.0 / 3.0) * h)

                self.draw_triangle(vsk, p1, p2, p3, depth, amp, freq, g)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    RecursiveTriangleSketch.display()
