import vsketch

PX_PER_IN = 96.0
MM_PER_IN = 25.4
PX_TO_MM = MM_PER_IN / PX_PER_IN
offset = 75

class OffsetCurvesSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

        # make everything based on the center of the page
        # Convert the pixel page size to mm (to match the drawing units)
        w_mm = vsk.width * PX_TO_MM
        h_mm = vsk.height * PX_TO_MM

        # Now this translate is in mm, consistent with vsk.scale("mm")
        vsk.rect(0+offset, 0+offset, w_mm-offset, h_mm-offset)     # page border

        print("width px, height px:", vsk.width, vsk.height)
        print("width mm, height mm:", vsk.width * PX_TO_MM, vsk.height * PX_TO_MM)
        # vsk.translate(w_mm/2, h_mm/2)
        # vsk.line(-5, 0, 5, 0)                      # crosshair at new origin
        # vsk.line(0, -5, 0, 5)
        # vsk.circle(-50, -50, 10)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    OffsetCurvesSketch.display()
