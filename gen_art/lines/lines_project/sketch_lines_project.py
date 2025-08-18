import vsketch
import numpy as np


class LinesProjectSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)
    x_points = 20.0
    y_points = 25.0

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")
        points = []
        for x_point in (np.linspace(0, self.x_points, 50)):
            for y_point in (np.linspace(0, self.y_points, 200)):
                x = (x_point) * vsk.noise(x_point+vsk.random(2))
                y = (y_point) * vsk.noise(y_point+vsk.random(2))
                points.append((x,y))
                #print (points)
                vsk.point(x,y)

        # print(len(points))
        # for count, point in enumerate(points):
        #     if count < len(points) - 1:
        #         print (count)
        #         if count % 5:
        #             vsk.line(point[0], point[1], points[count + 1][0], points[count + 1][1])
        #         else:
        #             continue
                    # print(point[0], point[1], points[count][0], points[count][1])

        vsk.save("points.svg", color_mode="none")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    LinesProjectSketch.display()
