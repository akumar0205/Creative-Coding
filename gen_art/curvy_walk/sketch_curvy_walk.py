import vsketch
import numpy as np

class CurvyWalkSketch(vsketch.SketchClass):
    grid_size = vsketch.Param(8)   # size of grid in mm
    num_points = vsketch.Param(20)  # number of points per side
    runs = vsketch.Param(10)  # number of runs

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        x = np.linspace(0, self.grid_size * (self.num_points - 1), self.num_points)
        y = np.linspace(0, self.grid_size * (self.num_points - 1), self.num_points)
        tension = 6.0

        for run in range(self.runs):
            # Set layer for this run (simulates "color" change via layers)
            vsk.stroke(run + 1)

            # Parameters for noise (horizontal offset for vertical waves)
            noise_amplitude = self.grid_size / 2
            noise_frequency = np.random.uniform(0.1, .2)

            # Vertical shift by run (1 mm per run)
            y_offset = run * 1

            # Group points by vertical lines (columns) with exact original x as key
            v_lines = {}
            for ix in range(self.num_points):
                original_x = x[ix]
                v_lines[original_x] = []
                for iy in range(self.num_points):
                    py = y[iy] + y_offset
                    px = original_x + noise_amplitude * np.sin(noise_frequency * py)
                    v_lines[original_x].append([px, py])

            # Draw smooth vertical lines using Bezier curves
            for key, line_points in v_lines.items():
                if len(line_points) < 2:
                    continue
                for i in range(len(line_points) - 1):
                    p0 = line_points[i]
                    p1 = line_points[i + 1]
                    if i == 0:
                        p_prev = line_points[0]
                        p_next = line_points[2] if len(line_points) > 2 else line_points[1]
                    else:
                        p_prev = line_points[i - 1]
                        p_next = line_points[i + 2] if i + 2 < len(line_points) else line_points[i + 1]
                    c1x = p0[0] + (p1[0] - p_prev[0]) / tension
                    c1y = p0[1] + (p1[1] - p_prev[1]) / tension
                    c2x = p1[0] - (p_next[0] - p0[0]) / tension
                    c2y = p1[1] - (p_next[1] - p0[1]) / tension
                    vsk.bezier(p0[0], p0[1], c1x, c1y, c2x, c2y, p1[0], p1[1])

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CurvyWalkSketch.save("curvy_walk.svg")
    CurvyWalkSketch.display()
