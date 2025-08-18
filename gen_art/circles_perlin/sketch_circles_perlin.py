import vsketch
import numpy as np


class CirclesPerlinSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")
        for i in range(500):
            x_cords = np.linspace(0, 50, 100)
            # print (x_cords)
            y = 0
            y_cords = []
            for x in x_cords:
                y = y + vsk.noise(x*i)
                vsk.rotate(vsk.noise(y))
                # vsk.point(x, y)
                y_cords.append(y)

            points = list(zip(x_cords, y_cords))
            xs, ys = zip(*points)
            vsk.polygon(xs, ys)

        vsk.translate(-100.0, -100.0)

        for i in range(500):
            x_cords = np.linspace(0, 50, 100)
            # print (x_cords)
            y = 0
            y_cords = []
            for x in x_cords:
                y = y + vsk.noise(x*i)
                vsk.rotate(vsk.noise(y))
                # vsk.point(x, y)
                y_cords.append(y)

            points = list(zip(x_cords, y_cords))
            xs, ys = zip(*points)
            vsk.polygon(xs, ys)

        vsk.save("spore.svg")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CirclesPerlinSketch.display()
