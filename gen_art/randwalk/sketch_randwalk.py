import vsketch
import numpy as np


class RandwalkSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")
        x0, y0 = 0, 0  # Start in the center

        for walk in range(1,10):
            #vsk.stroke(walk)
            x, y = x0, y0

            # Loop while inside the 600x600 box
            while -150 < x < 150 and -150 < y < 150:
                angle_deg = np.random.uniform(0, 360)
                length = np.random.uniform(1, 4)
                angle_rad = np.radians(angle_deg)

                x_new = x + length * np.cos(angle_rad)
                y_new = y + length * np.sin(angle_rad)

                vsk.line(x, y, x_new, y_new)

                x, y = x_new, y_new

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    RandwalkSketch.display()
