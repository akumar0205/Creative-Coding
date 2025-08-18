import vsketch
import numpy as np


class PointsSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)
    points = 5
    column_dict = {}

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        column = 0
        for x_column in (np.linspace(0, 75, 2000)):
            points = []
            for point in range(self.points):
                vsk.rotate(1*vsk.noise(point))
                if column % 20:
                    x_column = x_column + vsk.noise(point)
                y_point = (point + vsk.random(0, 3))
                points.append((x_column, y_point))
                vsk.point(x_column, y_point)
                # if column%3:
                #     x_column = x_column - vsk.noise(point)
            self.column_dict[column] = points
            column += 1

        # print (self.column_dict)

        vsk.save("junji.svg")




    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    PointsSketch.display()