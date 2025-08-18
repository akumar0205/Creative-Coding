import vsketch
import numpy as np


class CirclesSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

        # vsk.point(0, 0)
        # vsk.point(0, 4)
        # vsk.point(4, 0)
        # vsk.point(-4, 0)
        # vsk.point(0, -4)
        radius_array = np.linspace(0, 90, 33)
        for radius in radius_array:
            print(radius)
            i = 0
            # vsk.pushMatrix()
            while i < 5:
                vsk.arc(0, radius, radius, radius, 0, np.pi)
                vsk.arc(radius, 0, radius, radius, np.pi/2, -np.pi/2)
                vsk.arc(-radius, 0, radius, radius, -np.pi/2, np.pi/2)
                vsk.arc(0, -radius, radius, radius, np.pi, 0)
                vsk.rotate(30.0 * vsk.noise(radius))
                i = i + 1
            # vsk.popMatrix()

        vsk.save('eye.svg')

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CirclesSketch.display()
