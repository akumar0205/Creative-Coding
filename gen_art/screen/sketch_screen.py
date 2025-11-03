import vsketch


class ScreenSketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        # drawing area
        x_min, x_max = 75, 225
        y_min, y_max = 25, 225

        # noise parameters
        noise_scale = 0.02   # smaller -> smoother warp
        noise_amp = 15        # max bend in mm

        sample_step = .5      # how finely we sample along the line (mm)
                             # smaller = smoother curve, more segments

        #
        # VERTICAL WIGGLY LINES
        #
        vsk.stroke(1)
        for x in range(x_min, x_max, 2):  # spacing between columns
            # start at the top point
            prev_y = y_min
            n0 = vsk.noise(x * noise_scale, prev_y * noise_scale)
            prev_x = x + (n0 - 0.5) * 2 * noise_amp

            # walk downwards in small steps, drawing tiny segments
            y = y_min + sample_step
            while y <= y_max:
                n1 = vsk.noise(x * noise_scale, y * noise_scale)
                cur_x = x + (n1 - 0.5) * 2 * noise_amp
                cur_y = y

                # draw a short segment from previous point to current point
                vsk.line(prev_x, prev_y, cur_x, cur_y)

                prev_x, prev_y = cur_x, cur_y
                y += sample_step

        #
        # HORIZONTAL WIGGLY LINES
        #
        vsk.stroke(2)
        for y in range(y_min, y_max, 2):  # spacing between rows
            # start at the left point
            prev_x = x_min
            n0 = vsk.noise(prev_x * noise_scale, y * noise_scale + 1000)
            prev_y = y + (n0 - 0.5) * 2 * noise_amp

            # walk rightwards in small steps, drawing tiny segments
            x = x_min + sample_step
            while x <= x_max:
                n1 = vsk.noise(x * noise_scale, y * noise_scale + 1000)
                cur_x = x
                cur_y = y + (n1 - 0.5) * 2 * noise_amp

                vsk.line(prev_x, prev_y, cur_x, cur_y)

                prev_x, prev_y = cur_x, cur_y
                x += sample_step

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    ScreenSketch.display()
