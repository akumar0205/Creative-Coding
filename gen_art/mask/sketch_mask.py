import vsketch
import numpy as np
import math

class MaskSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

        # Create 10 points in each dimension
        x = np.linspace(50, 150, 100)  # 10 points from 0 to 1
        y = np.linspace(50, 150, 100)  # 10 points from 0 to 1

        # Create the grid
        X, Y = np.meshgrid(x, y)

        # Plot the points with vsketch  

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MaskSketch.display()
