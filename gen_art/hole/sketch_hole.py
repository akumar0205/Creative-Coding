import vsketch
import random
import math


class HoleSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def generate_two_points(self, vsk:vsketch.Vsketch, r1, r2): 
        # generate two random points within two circles of radius r1 and r2
        angle1 = random.uniform(0, 2 * math.pi)
        angle2 = angle1 + (vsk.noise(angle1)*10)
        x1 = r1 * math.cos(angle1)
        y1 = r1 * math.sin(angle1)
        x2 = r2 * math.cos(angle2)
        y2 = r2 * math.sin(angle2)
        return (x1, y1), (x2, y2)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

        number_of_points = 2000

        radiuses = [(15, 40), (40, 65), (65, 90)]
        stroke = 1

        for radius1, radius2 in radiuses:
            vsk.stroke(stroke)
            for _ in range(number_of_points):
                (x1, y1), (x2, y2) = self.generate_two_points(vsk, radius1, radius2)
                vsk.point(x1, y1)
                vsk.point(x2, y2)
                vsk.line(x1, y1, x2, y2)
            stroke = stroke + 1
        

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    HoleSketch.display()
