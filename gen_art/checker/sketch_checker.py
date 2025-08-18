import vsketch
import numpy as np


class CheckerSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")
        x = np.linspace(0, 30, 150)
        translate = np.linspace(0, 5, 30)
        for trans in translate:
            for x_point in x:

                vsk.arc(x_point+(25*vsk.noise(x_point)),
                        x_point+(25*vsk.noise(x_point)),
                        4+vsk.noise(x_point), 6+vsk.noise(trans), np.pi/2, np.pi*.75)

            print(np.ceil((trans)%5))
            vsk.stroke(np.ceil((trans)%5)+1)
            vsk.translate(trans+vsk.noise(trans), 5)
            vsk.rotate(3+(3*vsk.noise(trans)), True)

        vsk.save("cascade.svg")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CheckerSketch.display()
