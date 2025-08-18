import vsketch
import numpy as np


class BlobsSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")
        # Use smaller grid for clarity
        x = np.linspace(-50, 50, 40)
        y = np.linspace(-50, 50, 40)

        # Center of the page
        cx, cy = vsk.width / 2, vsk.height / 2
        #
        # # Grid 1: normal, centered
        # vsk.pushMatrix()
        # vsk.translate(cx, cy)
        # vsk.fill(4)
        # for x_cord in x:
        #     for y_cord in y:
        #         vsk.point(x_cord, y_cord)
        #         #vsk.circle(x_cord, y_cord, 5 * vsk.noise(x_cord * y_cord))
        # vsk.popMatrix()
        #
        # # Grid 2: rotated, centered
        # vsk.pushMatrix()
        # vsk.translate(cx, cy)  # move to center
        # vsk.rotate(np.radians(45))  # rotate around center
        # vsk.fill(3)
        # for x_cord in x:
        #     for y_cord in y:
        #         vsk.point(x_cord, y_cord)
        #         #vsk.circle(x_cord, y_cord, 4 * vsk.noise(x_cord * y_cord))
        # vsk.popMatrix()
        #
        # # Grid 3: rotated, centered
        # vsk.pushMatrix()
        # vsk.translate(cx, cy)  # move to center
        # vsk.rotate(np.radians(vsk.lerp(45, 90, .3)))  # rotate around center
        # vsk.fill(2)
        # for x_cord in x:
        #     for y_cord in y:
        #         vsk.point(x_cord, y_cord)
        #         #vsk.circle(x_cord, y_cord, 3 * vsk.noise(x_cord * y_cord))
        # vsk.popMatrix()
        #
        # # Grid 4: rotated, centered
        # vsk.pushMatrix()
        # vsk.translate(cx, cy)  # move to center
        # vsk.rotate(vsk.lerp(45, 90, .6))  # rotate around center
        # vsk.fill(5)
        # for x_cord in x:
        #     for y_cord in y:
        #         vsk.point(x_cord, y_cord)
        #         #vsk.circle(x_cord, y_cord, 2 * vsk.noise(x_cord * y_cord))
        # vsk.popMatrix()

        iterations = 10
        lerps = np.linspace(.1, .9, 6)
        for lerp in lerps:
            vsk.pushMatrix()
            vsk.translate(cx, cy)  # move to center
            vsk.rotate(vsk.lerp(10, 90, lerp))  # rotate around center
            vsk.stroke(lerp*10)
            for x_cord in x:
                for y_cord in y:
                    vsk.point(x_cord, y_cord)
                    # vsk.circle(x_cord, y_cord, 2 * vsk.noise(x_cord * y_cord))
                    # Add noise-based displacement
            vsk.popMatrix()

        vsk.save("blots.svg")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    BlobsSketch.display()
