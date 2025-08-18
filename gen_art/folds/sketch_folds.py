import vsketch
import numpy as np


class FoldsSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        x = np.linspace(25, 175, 75)
        print (x)

        fill = 1
        for y in range(-100, 100):
            for x_point in x:
                vsk.fill(1)
                vsk.circle(x_point, y + (35*vsk.noise(x_point+y)), 1)


        vsk.save("folds.svg")



    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    FoldsSketch.display()
    vsketch.Vsketch.save("folds.svg")
