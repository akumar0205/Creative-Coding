import vsketch
import numpy as np
import math

class ChaosSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    @staticmethod
    def very_chaotic_y(x, A, b, noise_scale):
        import math
        return A * x + b + noise_scale * (
                math.sin(3 * x + math.cos(5 * x)) +
                math.sin(7 * x ** 1.5) * math.cos(11 * x)
        )

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        for iter in range (10):
            vsk.pushMatrix()
            vsk.translate(0, iter * 1)
            vsk.rotate(5)
            x_vals = np.linspace(7, 15, 60)
            y_vals = np.linspace(7, 15, 60)
            x, y = np.meshgrid(x_vals, y_vals)

            # Loop over each row
            for row_idx in range(y.shape[0]):
                row_points = []

                for col_idx in range(x.shape[1]):
                    x_val = x[row_idx, col_idx]
                    y_base = y[row_idx, col_idx]
                    y_val = self.very_chaotic_y(x_val, A=1.0, b=y_base, noise_scale=.2)
                    row_points.append((x_val, y_val))

                vsk.polygon(row_points)

            vsk.popMatrix()

            vsk.save("grid_chaos.svg")


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    ChaosSketch.display()
