#!/usr/bin/env python3
import math
import re
import inkex
from inkex import PathElement, Group
from inkex.paths import Path, Move, Line

SVG_NS = "http://www.w3.org/2000/svg"
TAG_PATH = f"{{{SVG_NS}}}path"
TAG_POLYGON = f"{{{SVG_NS}}}polygon"
TAG_POLYLINE = f"{{{SVG_NS}}}polyline"
TAG_LINE = f"{{{SVG_NS}}}line"
TAG_G = f"{{{SVG_NS}}}g"

def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])

def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def parse_points(points_str):
    """
    Parse SVG points string for polygon/polyline: "x,y x,y ..." or "x y, x y ..."
    Returns list of (x,y) floats.
    """
    if not points_str:
        return []
    # Split by comma/space while preserving numeric tokens
    tokens = re.split(r"[,\s]+", points_str.strip())
    tokens = [t for t in tokens if t != ""]
    if len(tokens) < 4:
        return []
    pts = []
    for i in range(0, len(tokens) - 1, 2):
        try:
            x = float(tokens[i])
            y = float(tokens[i + 1])
            pts.append((x, y))
        except Exception:
            continue
    return pts

def path_from_points(points, close=False):
    p = Path()
    p.append(Move(points[0][0], points[0][1]))
    for pt in points[1:]:
        p.append(Line(pt[0], pt[1]))
    if close and len(points) >= 2:
        p.append(Line(points[0][0], points[0][1]))
    return p

def convert_shape_to_path_if_needed(el):
    """
    If el is polygon/polyline/line, convert it to an actual PathElement and return it.
    If el is already a path, return it.
    Otherwise return None.
    """
    if el.tag == TAG_PATH and isinstance(el, PathElement):
        return el

    parent = el.getparent()
    if parent is None:
        return None

    style = el.get("style")
    transform = el.get("transform")

    # polygon / polyline
    if el.tag in (TAG_POLYGON, TAG_POLYLINE):
        pts = parse_points(el.get("points"))
        if len(pts) < 2:
            return None
        close = (el.tag == TAG_POLYGON)
        pe = PathElement()
        pe.path = path_from_points(pts, close=close)
        if style:
            pe.set("style", style)
        if transform:
            pe.set("transform", transform)
        parent.add(pe)
        # remove original shape
        el.delete()
        return pe

    # line
    if el.tag == TAG_LINE:
        try:
            x1 = float(el.get("x1", "0"))
            y1 = float(el.get("y1", "0"))
            x2 = float(el.get("x2", "0"))
            y2 = float(el.get("y2", "0"))
        except Exception:
            return None
        pe = PathElement()
        pe.path = path_from_points([(x1, y1), (x2, y2)], close=False)
        if style:
            pe.set("style", style)
        if transform:
            pe.set("transform", transform)
        parent.add(pe)
        el.delete()
        return pe

    return None

def collect_drawable_elements(selection_values):
    """
    From the current selection, collect:
      - PathElements
      - polygons/polylines/lines (and convert them to paths)
      - any of the above inside selected groups/layers
    Returns a deduplicated list of PathElements.
    """
    candidates = []

    def add_candidate(node):
        # direct path
        if isinstance(node, PathElement) and node.tag == TAG_PATH:
            candidates.append(node)
            return
        # convert supported shapes
        if node.tag in (TAG_POLYGON, TAG_POLYLINE, TAG_LINE):
            converted = convert_shape_to_path_if_needed(node)
            if converted is not None:
                candidates.append(converted)
            return

    for el in selection_values:
        add_candidate(el)
        # Recurse descendants (for groups/layers)
        if hasattr(el, "iterdescendants"):
            for d in el.iterdescendants():
                add_candidate(d)

    # Deduplicate by element id (or object identity fallback)
    seen = set()
    uniq = []
    for p in candidates:
        pid = p.get_id() or str(id(p))
        if pid not in seen:
            seen.add(pid)
            uniq.append(p)
    return uniq

def make_dab_polyline(cx, cy, radius, segments, loops):
    pts = []
    if radius <= 0 or segments < 4 or loops < 1:
        return pts
    for _ in range(loops):
        for i in range(segments + 1):
            ang = 2.0 * math.pi * (i / segments)
            pts.append((cx + radius * math.cos(ang), cy + radius * math.sin(ang)))
    return pts

class BrushReloadAxiDrawVisible(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--max_len_mm", type=float, default=250.0)
        pars.add_argument("--paint_x_mm", type=float, default=10.0)
        pars.add_argument("--paint_y_mm", type=float, default=10.0)

        pars.add_argument("--do_dab", type=inkex.Boolean, default=True)
        pars.add_argument("--dab_radius_mm", type=float, default=2.0)
        pars.add_argument("--dab_segments", type=int, default=24)
        pars.add_argument("--dab_loops", type=int, default=2)

        pars.add_argument("--keep_original", type=inkex.Boolean, default=False)
        pars.add_argument("--group_outputs", type=inkex.Boolean, default=True)

    def effect(self):
        # Collect and convert polygons/polylines/lines into paths as needed
        selected_paths = collect_drawable_elements(self.svg.selection.values())

        if not selected_paths:
            inkex.errormsg(
                "Brush reload: No drawable strokes found.\n\n"
                "This extension supports: path, polygon, polyline, line.\n"
                "If your artwork uses clones/symbols, ungroup/convert first."
            )
            return

        max_len = self.svg.unittouu(f"{self.options.max_len_mm}mm")
        px = self.svg.unittouu(f"{self.options.paint_x_mm}mm")
        py = self.svg.unittouu(f"{self.options.paint_y_mm}mm")

        do_dab = bool(self.options.do_dab)
        dab_radius = self.svg.unittouu(f"{self.options.dab_radius_mm}mm")
        dab_segments = max(8, int(self.options.dab_segments))
        dab_loops = max(1, int(self.options.dab_loops))

        total_new_paths = 0
        total_refills = 0
        processed = 0

        for elem in selected_paths:
            parent = elem.getparent()
            style = elem.get("style")

            # Apply transform to geometry so distance math is correct
            path = elem.path
            if elem.get("transform"):
                path = path.transform(elem.composed_transform())
                elem.set("transform", None)

            p_abs = path.to_absolute()

            container = parent
            if self.options.group_outputs:
                g = Group()
                g.label = f"brush_reload_{elem.get_id()}"
                parent.add(g)
                container = g

            last = None
            traveled = 0.0
            current_chunk_pts = None

            def flush_chunk():
                nonlocal total_new_paths, current_chunk_pts
                if current_chunk_pts and len(current_chunk_pts) >= 2:
                    pe = PathElement()
                    pe.path = path_from_points(current_chunk_pts, close=False)
                    if style:
                        pe.set("style", style)
                    container.add(pe)
                    total_new_paths += 1
                current_chunk_pts = None

            def emit_dab():
                nonlocal total_new_paths, total_refills
                if do_dab and dab_radius > 0:
                    dab_pts = make_dab_polyline(px, py, dab_radius, dab_segments, dab_loops)
                    if dab_pts:
                        dab_el = PathElement()
                        dab_el.path = path_from_points(dab_pts, close=False)
                        if style:
                            dab_el.set("style", style)
                        container.add(dab_el)
                        total_new_paths += 1
                total_refills += 1

            # Core logic assumes M/L (which is true after our conversions for polygon/polyline/line)
            for cmd in p_abs:
                if isinstance(cmd, Move):
                    flush_chunk()
                    last = (cmd.x, cmd.y)
                    traveled = 0.0
                    current_chunk_pts = [last]

                elif isinstance(cmd, Line):
                    if last is None:
                        last = (cmd.x, cmd.y)
                        traveled = 0.0
                        current_chunk_pts = [last]
                        continue

                    nxt = (cmd.x, cmd.y)
                    seg_len = dist(last, nxt)
                    if seg_len <= 1e-9:
                        continue

                    a = last
                    b = nxt
                    remaining = seg_len

                    while traveled + remaining > max_len:
                        need = max_len - traveled
                        t = need / remaining if remaining > 0 else 0.0
                        split_pt = lerp(a, b, t)

                        if current_chunk_pts is None:
                            current_chunk_pts = [a]
                        current_chunk_pts.append(split_pt)
                        flush_chunk()

                        emit_dab()

                        traveled = 0.0
                        a = split_pt
                        remaining = dist(a, b)
                        current_chunk_pts = [split_pt]

                    if current_chunk_pts is None:
                        current_chunk_pts = [a]
                    current_chunk_pts.append(b)
                    traveled += remaining
                    last = b

                else:
                    # If you have real Beziers, convert/flatten first.
                    pass

            flush_chunk()

            if not self.options.keep_original:
                elem.delete()

            processed += 1

        inkex.errormsg(
            f"Brush reload: processed {processed} stroke(s), created {total_new_paths} new path(s), "
            f"inserted {total_refills} refill(s).\n"
            f"Reminder: In AxiDraw Control, set Plot Optimization to Strict/None to preserve order."
        )

if __name__ == "__main__":
    BrushReloadAxiDrawVisible().run()
