import vsketch
import numpy as np
import math

class MaskSketch(vsketch.SketchClass):

    def project(self, x, y, z, depth=300):
        scale = 1 / (1 + z / depth)
        return x * scale, y * scale

    def wavy_line(self, vsk, x1, y1, x2, y2, amp, freq, steps, seed):
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return

        nx = -dy / length
        ny = dx / length

        px, py = x1, y1

        for i in range(1, steps + 1):
            t = i / steps
            x = x1 + dx * t
            y = y1 + dy * t

            n = vsk.noise(x * freq, y * freq, seed)
            offset = (n - 0.5) * 2 * amp

            x += nx * offset
            y += ny * offset

            vsk.line(px, py, x, y)
            px, py = x, y

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        xs = np.linspace(25, 200, 25)
        ys = np.linspace(25, 200, 25)
        X, Y = np.meshgrid(xs, ys)

        grids = np.linspace(5, 6, 10)
        tilt = math.radians(20)
        stroke = 1 

        for grid in grids:
            vsk.pushMatrix()
            vsk.stroke(stroke)
            vsk.translate(0, 125 * grid)

            z_scale = grid
            amp = 1.5 + grid * 2.0      # wave grows with depth
            freq = 0.05
            steps = 10
            seed = grid * 10

            # ---- Horizontal lines ----
            for row_x, row_y in zip(X, Y):
                for (x1, y1), (x2, y2) in zip(
                    zip(row_x, row_y),
                    zip(row_x[1:], row_y[1:])
                ):
                    z1 = y1 * z_scale
                    z2 = y2 * z_scale

                    y1r = y1 * math.cos(tilt) - z1 * math.sin(tilt)
                    z1r = y1 * math.sin(tilt) + z1 * math.cos(tilt)

                    y2r = y2 * math.cos(tilt) - z2 * math.sin(tilt)
                    z2r = y2 * math.sin(tilt) + z2 * math.cos(tilt)

                    px1, py1 = self.project(x1, y1r, z1r)
                    px2, py2 = self.project(x2, y2r, z2r)

                    self.wavy_line(vsk, px1, py1, px2, py2, amp, freq, steps, seed)

            # ---- Vertical lines ----
            for col_x, col_y in zip(X.T, Y.T):
                for (x1, y1), (x2, y2) in zip(
                    zip(col_x, col_y),
                    zip(col_x[1:], col_y[1:])
                ):
                    z1 = y1 * z_scale
                    z2 = y2 * z_scale

                    y1r = y1 * math.cos(tilt) - z1 * math.sin(tilt)
                    z1r = y1 * math.sin(tilt) + z1 * math.cos(tilt)

                    y2r = y2 * math.cos(tilt) - z2 * math.sin(tilt)
                    z2r = y2 * math.sin(tilt) + z2 * math.cos(tilt)

                    px1, py1 = self.project(x1, y1r, z1r)
                    px2, py2 = self.project(x2, y2r, z2r)

                    self.wavy_line(vsk, px1, py1, px2, py2, amp, freq, steps, seed + 100)

            vsk.popMatrix()
            stroke += 1


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MaskSketch.display()
