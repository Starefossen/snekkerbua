"""Line-art assembly drawings for the HANNA manual.

One composed black-and-white page per build step, plus a hero drawing of the
finished bed for the cover. This is the picture side of docs/MONTERING.md; the
shaded USD renders that tools/render_steps.py makes are the solid-model view
of the same steps, kept for reference.

THE PROJECTION
--------------
The model is the source of truth, so this imports generate_loftbed.py (the
same import tools/gen_doc_tables.py does) and works on the real B-rep solids
rather than on meshes. For every step it forms two sub-compounds:

    prior   everything placed in an earlier step and not touched now
    new     exactly the parts this step is about

Both go into ONE OpenCascade hidden-line-removal run, and HLRBRep_HLRToShape
is then asked for the visible edges of each input shape SEPARATELY. That
per-shape extraction is the only reason this does not simply call build123d's
Shape.project_to_viewport(): that helper projects one shape and gives no way
to tell the groups apart afterwards. Everything else - the projector setup,
the edge harvesting, the BuildCurves3d fix-up - is the same code path.

    prior   thin, light grey
    new     heavy, black, drawn last

The grey layer comes out of the combined run, so a part already standing is
correctly hidden where this step's parts pass in front of it. The black layer
is a SECOND run on the new parts alone, so the piece you are about to fit is
always drawn whole even where the frame would cover it. That is the assembly-
manual convention rather than the photographic one, and it is what makes a
small part - the loose panel down between the benches, say - readable at all.

THE PAGE
--------
The projected edges come back lying in the viewport plane, so the SVG is
written here rather than by build123d's ExportSVG: once the line work is a
list of 2-D polylines, the rest of the page can be composed in the SAME
coordinate system. plane_xy() projects any 3-D point of the model into it, and
that is what anchors every annotation to real geometry:

  * fastening points are the CONTACT PATCHES between the parts - two boxes
    that meet on a face, computed from the parts' own extents. The marker
    arrow at each one points along the contact normal, i.e. the way the screw
    goes in.
  * the corner inset carries the step's fasteners at large scale with their
    counts, and a section through the step's biggest joint drawn from the two
    members' real dimensions.
  * leader lines run from the inset to the fastening points; a step with only
    one or two of them gets a circular magnifier of the real line work there
    instead.
  * the step that stands the back frame up gets before/after thumbnails, the
    second being the same parts drawn again from a laid-flat placement. That
    placement is a drawing transform - it moves nothing in the model.
  * the mattress step gets an information panel whose numbers (platform top,
    mattress thickness, guard-band underside, and the opening between them)
    are read off the model.

Every drawing is written twice: an SVG (the real thing, and what to print) and
a PNG made from it with rsvg-convert, because that is what docs/MONTERING.md
embeds. Both are committed, so the manual reads on a machine with none of
this installed.

Usage:
    python tools/render_lineart.py [--width 1600] [--out docs/img]
                                   [--step N] [--hero-only] [--steps-only]
"""

import json
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

STEP_JSON = os.path.join(ROOT, "docs", "generated", "byggesteg.json")

# ---------------------------------------------------------------------------
# PEN
# ---------------------------------------------------------------------------
# All widths are in model millimetres, which is what the SVG user unit is, so
# they scale with the drawing and not with the output resolution.
W_PRIOR = 2.2          # parts already standing
W_NEW = 7.0            # the parts this step is about
W_HERO = 5.6           # the cover drawing
W_RULE = 2.6           # inset borders, section outlines
W_LEAD = 2.4           # leader lines
W_MARK = 3.4           # fastening-point markers
GREY = "#9a9a9a"
INK = "#111111"

FONT = "Helvetica, Arial, sans-serif"
PAD = 70               # white margin around the bed, model mm
TOL = 0.51             # two faces this close count as touching, mm
MIN_CONTACT = 900.0    # ignore contact patches smaller than this, mm2


def _f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# PROJECTION
# ---------------------------------------------------------------------------
def camera_direction(azimuth, elevation):
    """The step camera, expressed in the model's own Z-up millimetre space.

    byggesteg.json stores the camera the way the USD renders take it: an
    azimuth measured from +Z towards +X and an elevation, both in the Y-up
    export space. generate_loftbed.py's Y_UP location is a -90 deg turn about
    X followed by 180 deg about Y, which maps (x, y, z) -> (-x, z, y), so the
    inverse of that on the Y-up view vector gives the direction to stand in
    here. Azimuth 0 ends up looking straight at the ladder side.
    """
    a, e = math.radians(azimuth), math.radians(elevation)
    return (-math.sin(a) * math.cos(e),
            math.cos(a) * math.cos(e),
            math.sin(e))


class View:
    """A camera: the projector the HLR runs in, and the 2-D frame it lands in.

    The hidden-line result comes back as edges lying in the z = 0 plane of the
    projector's own coordinate system. `right` and `up` are that system's axes
    in model space, so plane_xy() puts any 3-D point of the model into exactly
    the same 2-D frame as the line work - which is what lets an annotation be
    anchored to a joint instead of to a guessed pixel.
    """

    def __init__(self, direction, look_at):
        from build123d import Vector
        from OCP.gp import gp_Ax1, gp_Ax2
        from OCP.HLRAlgo import HLRAlgo_Projector

        self.look_at = Vector(look_at)
        # Parallel projection: the eye position only fixes the plane's origin,
        # so any comfortable stand-off does.
        self.origin = self.look_at + Vector(direction) * 10000.0
        proj_dir = (self.origin - self.look_at).normalized()
        frame = gp_Ax2()
        frame.SetAxis(gp_Ax1(self.origin.to_pnt(), proj_dir.to_dir()))
        frame.SetYDirection(Vector(0, 0, 1).to_dir())
        self.frame = frame
        self.projector = HLRAlgo_Projector(frame)
        x, y = frame.XDirection(), frame.YDirection()
        self.right = Vector(x.X(), x.Y(), x.Z())
        self.up = Vector(y.X(), y.Y(), y.Z())

    def xy(self, p):
        """A model point -> the drawing's 2-D frame."""
        from build123d import Vector
        v = Vector(*p) - self.look_at
        return (v.dot(self.right), v.dot(self.up))

    def dir_xy(self, v3):
        """A model direction -> the drawing's 2-D frame (not normalised)."""
        from build123d import Vector
        v = Vector(*v3)
        return (v.dot(self.right), v.dot(self.up))


def _harvest(hlr_to_shape, wrapped):
    """Visible edges belonging to one of the shapes fed to the HLR run."""
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_ShapeEnum
    from OCP.BRepLib import BRepLib
    from build123d.topology import Edge
    from build123d.topology.utils import downcast

    found = []
    for getter in (hlr_to_shape.VCompound,
                   hlr_to_shape.Rg1LineVCompound,
                   hlr_to_shape.OutLineVCompound):
        try:
            comp = getter(wrapped)
        except Exception:
            continue
        if comp is None or comp.IsNull():
            continue
        exp = TopExp_Explorer(comp, TopAbs_ShapeEnum.TopAbs_EDGE)
        while exp.More():
            found.append(downcast(exp.Current()))
            exp.Next()
    out = []
    for e in found:
        # Without this the 2-D result carries no 3-D curve and later use of
        # the edge segfaults; build123d's own projector does the same.
        BRepLib.BuildCurves3d_s(e, 1e-6)
        out.append(Edge(e))
    return out


def project(view, groups):
    """Hidden-line projection of several shapes in one run.

    `groups` is [(key, Shape), ...]; the return is {key: [polyline, ...]} in
    the view's 2-D frame, where a polyline is a list of (x, y).
    """
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape

    algo = HLRBRep_Algo()
    for _key, shape in groups:
        algo.Add(shape.wrapped)
    algo.Projector(view.projector)
    algo.Update()
    algo.Hide()
    to_shape = HLRBRep_HLRToShape(algo)
    return {key: [_polyline(e) for e in _harvest(to_shape, shape.wrapped)]
            for key, shape in groups}


def _polyline(edge):
    """A projected edge as a list of (x, y).

    Everything in this bed is a box, so almost every edge is a straight line
    and two points are exact; anything else is sampled.
    """
    from build123d import GeomType
    try:
        straight = edge.geom_type == GeomType.LINE
    except Exception:
        straight = False
    n = 2 if straight else 24
    pts = []
    for i in range(n):
        p = edge @ (i / (n - 1))
        pts.append((p.X, p.Y))
    return pts


def bounds(polylines):
    xs = [p[0] for pl in polylines for p in pl]
    ys = [p[1] for pl in polylines for p in pl]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------------------
# WHERE THE FASTENERS GO
# ---------------------------------------------------------------------------
# Every part in this bed is an axis-aligned box and carries its own extents,
# so the places where fasteners are driven can be READ OFF the model instead
# of listed by hand: two boxes that share a face, with area behind it, are a
# joint. The centre of that shared face is the fastening point and its normal
# is the direction the screw travels.
def contacts(new_parts, other_parts):
    """[(point3, axis, sign, area, part_a, part_b), ...], biggest first."""
    out = []
    pairs = [(a, b) for i, a in enumerate(new_parts)
             for b in new_parts[i + 1:]]
    pairs += [(a, b) for a in new_parts for b in other_parts]
    for a, b in pairs:
        ea, eb = a.extents, b.extents
        for k in range(3):
            for sign, touch in ((1, abs(ea[k][1] - eb[k][0])),
                                (-1, abs(ea[k][0] - eb[k][1]))):
                if touch > TOL:
                    continue
                span = []
                for j in range(3):
                    if j == k:
                        continue
                    lo = max(ea[j][0], eb[j][0])
                    hi = min(ea[j][1], eb[j][1])
                    span.append((j, lo, hi))
                if any(hi - lo <= TOL for _j, lo, hi in span):
                    continue
                area = 1.0
                for _j, lo, hi in span:
                    area *= hi - lo
                if area < MIN_CONTACT:
                    continue
                p = [0.0, 0.0, 0.0]
                p[k] = ea[k][1] if sign > 0 else ea[k][0]
                for j, lo, hi in span:
                    p[j] = (lo + hi) / 2
                out.append((tuple(p), k, sign, area, a, b))
    out.sort(key=lambda c: -c[3])
    return out


def wall_fix_contacts(new_parts, count):
    """Fixing points into the wall, spread along the longest part's back face.

    Same shape of record as contacts(), so the marker and inset code does not
    have to know the difference: the normal is -Y, straight into the wall.
    """
    if not new_parts:
        return []
    rail = max(new_parts, key=lambda p: p.extents[0][1] - p.extents[0][0])
    x0, x1 = rail.extents[0]
    y0 = rail.extents[1][0]
    z = (rail.extents[2][0] + rail.extents[2][1]) / 2
    n = max(int(count), 2)
    out = []
    for i in range(n):
        t = (i + 0.5) / n
        out.append(((x0 + (x1 - x0) * t, y0, z), 1, -1, 1e9, rail, rail))
    return out


# ---------------------------------------------------------------------------
# WHICH FASTENER GOES IN WHICH CONTACT PATCH
# ---------------------------------------------------------------------------
# contacts() finds the patches; the JOINTS table in tools/gen_doc_tables.py
# says what is driven through each joint. The bridge between the two is the
# pair of PART NAMES that meet, plus the axis they meet across - which is
# enough, because no two joints in this bed join the same pair of parts across
# the same axis. J4 is the reason the axis is needed at all: the same joint
# drives a 6x120 sideways through the ladder upright into the rung end AND a
# 5x60 straight down through the rung into the block under it, and the reader
# has to be told which is which.
#
# A patch that matches nothing here carries no fastener - two parts that
# simply bear on one another. On a step that badges its arrows those are left
# undrawn, because a lettered page has no way to say "this one is not a screw".
_PART = {
    "post":        r"Corner Post (?:Back|Front) (?:Left|Right)",
    "post_back":   r"Corner Post Back (?:Left|Right)",
    "post_front":  r"Corner Post Front (?:Left|Right)",
    "rail_back":   r"Upper Side Rail Back",
    "rail_front":  r"Upper Side Rail Front",
    "bench_back":  r"Bench Rail Back \(continuous\)",
    "bench_front": r"Bench Rail Front (?:Left|Right) \(segment\)",
    "bench_blk_b": r"Bench Rail Bearing Block Back (?:Left|Right)",
    "bench_blk_f": r"Bench Rail Bearing Block Front (?:Left|Right)",
    "ledger":      r"Table Ledger Back",
    "beam":        r"End Beam (?:Left|Right)",
    "beam_blk":    r"End Beam Bearing Block (?:Left|Right) (?:Back|Front)",
    "stub":        r"Bench Stub Leg (?:Back|Front) (?:Left|Right)",
    "upright":     r"Ladder Upright (?:Left|Right)",
    "rung":        r"Ladder Rung_\d+",
    "rung_blk":    r"Rung Block (?:Left|Right)_\d+",
    "panel":       r"Movable Panel \(bed mode\)",
    "batten":      r"Panel Stiffener Batten (?:Left|Right) \(bed mode\)",
}

# (joint, part a, part b, contact axis, the trade names driven there). The
# names are prefixes of the ones in JOINTS - enough to pick the row out of the
# step's own fastener list, which is where the count and the letter come from.
JOINT_CONTACTS = [
    ("J1",    "post",        "beam",       0, ["Treskrue 6×90"]),
    ("J1-B",  "beam_blk",    "post",       0, ["Treskrue 6×90"]),
    ("J2",    "post_front",  "rail_front", 1, ["Treskrue 6×80"]),
    ("J2-B",  "post_back",   "rail_back",  2, ["Treskrue 6×120"]),
    ("J3",    "upright",     "rail_front", 1, ["Treskrue 6×80"]),
    ("J4",    "rung",        "rung_blk",   2, ["Treskrue 5×60"]),
    ("J4",    "rung",        "upright",    0, ["Treskrue 6×120"]),
    ("J5",    "upright",     "rung_blk",   0, ["Treskrue 5×60"]),
    ("J8",    "bench_front", "post_front", 1, ["Treskrue 6×80"]),
    ("J8-B",  "bench_back",  "post_back",  0, ["Treskrue 6×90"]),
    ("J9-B",  "bench_blk_b", "post_back",  0, ["Treskrue 6×90"]),
    ("J9-F",  "bench_blk_f", "post_front", 1, ["Treskrue 6×70"]),
    ("J10",   "bench_front", "stub",       2, ["Vinkelbeslag 90",
                                               "Treskrue 5×40",
                                               "Treskrue 5×70"]),
    ("J10",   "stub",        "bench_back", 2, ["Vinkelbeslag 90",
                                               "Treskrue 5×40",
                                               "Treskrue 5×70"]),
    ("J12",   "post_back",   "ledger",     0, ["Vinkelbeslag 40",
                                               "Treskrue 5×40"]),
    ("J13a",  "panel",       "batten",     2, ["Treskrue 5×60"]),
    ("J13b",  "panel",       "rung",       2, ["U-brakett", "Senkhodeskrue"]),
    ("J13c",  "panel",       "bench_back", 2, ["Krokplate", "Senkhodeskrue"]),
]


def _is_part(kind, label):
    return re.fullmatch(_PART[kind], label) is not None


def contact_fasteners(contact):
    """The trade-name prefixes driven at this patch, or () if none are."""
    a, b, axis = contact[4].label, contact[5].label, contact[1]
    for _jid, pa, pb, ax, names in JOINT_CONTACTS:
        if ax != axis:
            continue
        if ((_is_part(pa, a) and _is_part(pb, b))
                or (_is_part(pa, b) and _is_part(pb, a))):
            return tuple(names)
    return ()


def contact_badges(contact, letters):
    """The badge letters this patch should carry, in table order."""
    out = set()
    for want in contact_fasteners(contact):
        for name, letter in letters.items():
            if name.startswith(want):
                out.add(letter)
    return tuple(sorted(out))


def _apart(a, b, gap):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 > gap * gap


def _in_rect(p, rect, grow=0.0):
    x, y, w, h = rect
    return (x - grow <= p[0] <= x + w + grow
            and y - grow <= p[1] <= y + h + grow)


def choose_markers(pts, letters, inset=None):
    """Which fastening points get an arrow. -> [(xy, contact, badges), ...]

    Without letters this is the old rule and nothing else: walk the patches
    biggest first and keep the ones that do not crowd a marker already placed.

    With letters there is one more duty. A step that drives three kinds of
    screw has to SHOW all three, and the odd one out is regularly the one that
    loses the crowding test - the 6x120 into the ladder rung ends sits 36 mm
    from the 5x60 that goes down into the block below it, so the plain rule
    would drop every last one of them and leave badge B with nowhere to point.
    So after the ordinary pass, any letter with fewer than two markers is given
    them, at a tighter spacing. The letters keep the arrows apart where the
    geometry cannot.
    """
    tagged = [(p2, c, contact_badges(c, letters)) for p2, c in pts]
    if letters:
        tagged = [t for t in tagged if t[2]]
    if inset is not None:
        # A point under the inset panel has nothing to point at: the panel is
        # opaque and covers the very line work the arrow is about.
        tagged = [t for t in tagged if not _in_rect(t[0], inset, 8.0)]

    keep = []
    for item in tagged:
        if all(_apart(item[0], q[0], 52.0) for q in keep):
            keep.append(item)
        if len(keep) >= 34:
            break
    if not letters:
        return keep

    for letter in sorted({l for _p, _c, tags in tagged for l in tags}):
        seen = sum(1 for _p, _c, tags in keep if letter in tags)
        for item in tagged:
            if seen >= 2:
                break
            if letter not in item[2] or item in keep:
                continue
            if seen and not all(_apart(item[0], q[0], 20.0) for q in keep):
                continue
            keep.append(item)
            seen += 1
    return keep


def thin_out(points, limit, min_gap):
    """Keep markers legible: drop points that crowd one already kept."""
    kept = []
    for p in points:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > min_gap ** 2
               for q in kept):
            kept.append(p)
        if len(kept) >= limit:
            break
    return kept


# ---------------------------------------------------------------------------
# THE PAGE
# ---------------------------------------------------------------------------
class Page:
    """An SVG in the projection's own units, with y flipped for the screen."""

    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.body = []
        # Where the badge letters have already landed, so the next row can
        # step out of their way instead of on top of them.
        self.badge_spots = []

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def h(self):
        return self.y1 - self.y0

    def _p(self, pt):
        return f"{_f(pt[0])},{_f(-pt[1])}"

    def polylines(self, plines, colour, width, opacity=None):
        if not plines:
            return
        d = " ".join("M" + " L".join(self._p(p) for p in pl)
                     for pl in plines if len(pl) > 1)
        if not d:
            return
        extra = f' opacity="{opacity}"' if opacity else ""
        self.body.append(
            f'<path d="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{_f(width)}" stroke-linecap="round" '
            f'stroke-linejoin="round"{extra}/>')

    def line(self, a, b, colour=INK, width=W_LEAD, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(
            f'<path d="M{self._p(a)} L{self._p(b)}" fill="none" '
            f'stroke="{colour}" stroke-width="{_f(width)}" '
            f'stroke-linecap="round"{da}/>')

    def rect(self, x, y, w, h, fill="#ffffff", stroke=INK, width=W_RULE,
             rx=0):
        self.body.append(
            f'<rect x="{_f(x)}" y="{_f(-(y + h))}" width="{_f(w)}" '
            f'height="{_f(h)}" rx="{_f(rx)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{_f(width)}"/>')

    def circle(self, c, r, fill="none", stroke=INK, width=W_RULE):
        self.body.append(
            f'<circle cx="{_f(c[0])}" cy="{_f(-c[1])}" r="{_f(r)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{_f(width)}"/>')

    def dot(self, c, r, colour=INK):
        self.body.append(
            f'<circle cx="{_f(c[0])}" cy="{_f(-c[1])}" r="{_f(r)}" '
            f'fill="{colour}"/>')

    def text(self, p, s, size, anchor="start", weight="normal", colour=INK):
        s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        self.body.append(
            f'<text x="{_f(p[0])}" y="{_f(-p[1])}" font-family="{FONT}" '
            f'font-size="{_f(size)}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{colour}">{s}</text>')

    def arrow(self, tail, head, colour=INK, width=W_MARK, head_len=26):
        """A plain open arrowhead - no markers, so it survives any renderer."""
        dx, dy = head[0] - tail[0], head[1] - tail[1]
        n = math.hypot(dx, dy) or 1.0
        ux, uy = dx / n, dy / n
        self.line(tail, head, colour, width)
        for turn in (2.6, -2.6):
            bx = math.cos(turn) * ux - math.sin(turn) * uy
            by = math.sin(turn) * ux + math.cos(turn) * uy
            self.line(head, (head[0] + bx * head_len, head[1] + by * head_len),
                      colour, width)

    def embed_svg(self, path, x, y, w, h):
        """Drop one of the fastener glyphs in, at its own aspect ratio."""
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        raw = re.sub(r"<\?xml[^>]*\?>", "", raw)
        m = re.search(r'viewBox="([^"]+)"', raw)
        if not m:
            return
        vb = m.group(1)
        inner = raw[raw.index(">", raw.index("<svg")) + 1: raw.rindex("</svg>")]
        self.body.append(
            f'<svg x="{_f(x)}" y="{_f(-(y + h))}" width="{_f(w)}" '
            f'height="{_f(h)}" viewBox="{vb}" '
            f'preserveAspectRatio="xMidYMid meet">{inner}</svg>')

    def write(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="{_f(self.x0)} {_f(-self.y1)} {_f(self.w)} '
                f'{_f(self.h)}">')
        bg = (f'<rect x="{_f(self.x0)}" y="{_f(-self.y1)}" '
              f'width="{_f(self.w)}" height="{_f(self.h)}" fill="#ffffff"/>')
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head + "\n" + bg + "\n" + "\n".join(self.body)
                     + "\n</svg>\n")


def glyph_dims(path):
    with open(path, encoding="utf-8") as fh:
        m = re.search(r'viewBox="[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)"',
                      fh.read(4000))
    return (float(m.group(1)), float(m.group(2))) if m else (240.0, 120.0)


def clip_to_circle(plines, centre, r):
    """The line work inside a circle, for the magnifier insets."""
    cx, cy = centre
    out = []
    for pl in plines:
        run = []
        for a, b in zip(pl, pl[1:]):
            ina = math.hypot(a[0] - cx, a[1] - cy) <= r
            inb = math.hypot(b[0] - cx, b[1] - cy) <= r
            if ina and inb:
                if not run:
                    run.append(a)
                run.append(b)
                continue
            if not ina and not inb:
                if run:
                    out.append(run)
                    run = []
                continue
            # One end outside: walk the segment to the boundary.
            lo, hi = (0.0, 1.0)
            for _ in range(24):
                mid = (lo + hi) / 2
                p = (a[0] + (b[0] - a[0]) * mid, a[1] + (b[1] - a[1]) * mid)
                if (math.hypot(p[0] - cx, p[1] - cy) <= r) == ina:
                    lo = mid
                else:
                    hi = mid
            cut = (a[0] + (b[0] - a[0]) * lo, a[1] + (b[1] - a[1]) * lo)
            if ina:
                if not run:
                    run.append(a)
                run.append(cut)
                out.append(run)
                run = []
            else:
                run = [cut, b]
        if run:
            out.append(run)
    return out


def remap(plines, src_c, src_r, dst_c, dst_r):
    k = dst_r / src_r
    return [[(dst_c[0] + (p[0] - src_c[0]) * k,
              dst_c[1] + (p[1] - src_c[1]) * k) for p in pl] for pl in plines]


# ---------------------------------------------------------------------------
# THE MODEL SIDE
# ---------------------------------------------------------------------------
def universe(G):
    return {p.label: p for p in
            list(G.parts) + [G.panel_bed] + list(G.battens_bed) + [G.mattress]}


def full_bed(G):
    """The finished bed in bed mode - frame and loose panel, no mattress.

    The mattress is left out on purpose: it is bought, not built, and drawing
    it would only hide the slat field it lies on.
    """
    from build123d import Compound
    return Compound(children=list(G.parts) + [G.panel_bed]
                    + list(G.battens_bed))


def comp(parts):
    from build123d import Compound
    return Compound(children=list(parts))


# ---------------------------------------------------------------------------
# THE INSET
# ---------------------------------------------------------------------------
def joint_section(page, box, contact, view):
    """A section through the step's biggest joint, from the real members.

    The screw runs along the contact normal, so the section is taken in the
    plane that holds that normal and the shorter of the two axes across it.
    Both members are boxes, so both sections are rectangles and every number
    in the little drawing is one the cut list already carries.
    """
    x, y, w, h = box
    cp, k, sign, _area, a, b = contact
    across = [j for j in range(3) if j != k]
    # The narrower of the two remaining axes keeps the detail compact.
    u = min(across, key=lambda j: min(a.extents[j][1] - a.extents[j][0],
                                      b.extents[j][1] - b.extents[j][0]))

    def rectangle(part):
        return ((part.extents[k][0], part.extents[k][1]),
                (part.extents[u][0], part.extents[u][1]))

    ra, rb = rectangle(a), rectangle(b)
    # Keep the window on the joint itself. Two members can run a long way
    # past each other across the contact - a 1794 mm rail meeting a 98 mm
    # post - and drawing their full length would shrink the detail to a line.
    face = ra[0][1] if sign > 0 else ra[0][0]
    reach = max(min(ra[0][1] - ra[0][0], rb[0][1] - rb[0][0]) * 1.8, 40.0)
    n0, n1 = face - reach, face + reach
    mid_u = cp[u]
    half = max(min(ra[1][1] - ra[1][0], rb[1][1] - rb[1][0]), 1.0) * 1.6
    u0, u1 = mid_u - half, mid_u + half
    ra = ((max(ra[0][0], n0), min(ra[0][1], n1)),
          (max(ra[1][0], u0), min(ra[1][1], u1)))
    rb = ((max(rb[0][0], n0), min(rb[0][1], n1)),
          (max(rb[1][0], u0), min(rb[1][1], u1)))
    n0 = min(ra[0][0], rb[0][0])
    n1 = max(ra[0][1], rb[0][1])
    u0 = min(ra[1][0], rb[1][0])
    u1 = max(ra[1][1], rb[1][1])
    # A joint that stacks (the normal is Z) is drawn stacked, so the screw
    # goes down the page the way it goes down into the timber; a joint made
    # sideways is drawn sideways.
    stacked = (k == 2)
    if stacked:
        span_x, span_y = (u1 - u0), (n1 - n0)
    else:
        span_x, span_y = (n1 - n0), (u1 - u0)
    scale = min(w * 0.80 / max(span_x, 1e-6), h * 0.72 / max(span_y, 1e-6))
    ox = x + w / 2
    oy = y + h * 0.54

    def place(rn, ru):
        """(n-range, u-range) -> the rectangle's page position."""
        if stacked:
            return (ox + (ru[0] - (u0 + u1) / 2) * scale,
                    oy + (rn[0] - (n0 + n1) / 2) * scale,
                    (ru[1] - ru[0]) * scale, (rn[1] - rn[0]) * scale)
        return (ox + (rn[0] - (n0 + n1) / 2) * scale,
                oy + (ru[0] - (u0 + u1) / 2) * scale,
                (rn[1] - rn[0]) * scale, (ru[1] - ru[0]) * scale)

    for r in (ra, rb):
        px, py, pw, ph = place(r[0], r[1])
        page.rect(px, py, pw, ph, fill="none", width=W_RULE)
    # The fastener crosses the shared face, driven the way the arrow points.
    face = (ra[0][1] if sign > 0 else ra[0][0])
    fn = (face - (n0 + n1) / 2) * scale
    reach = min((n1 - n0) * scale * 0.34, (h if stacked else w) * 0.30)
    if stacked:
        page.arrow((ox, oy + fn - sign * reach * 1.6),
                   (ox, oy + fn + sign * reach), INK, W_MARK, 16)
    else:
        page.arrow((ox + fn - sign * reach * 1.6, oy),
                   (ox + fn + sign * reach, oy), INK, W_MARK, 16)


BADGE_R = 25.0         # the circled letters, model mm


def badge(page, centre, letter):
    """One circled sans letter - the same mark the step table carries."""
    page.circle(centre, BADGE_R, fill="#ffffff", stroke=INK, width=W_RULE)
    page.text((centre[0], centre[1] - BADGE_R * 0.40), letter,
              BADGE_R * 1.20, anchor="middle", weight="bold")
    page.badge_spots.append(centre)


def badge_row(page, tail, direction, letters, inset=None):
    """The letters for one fastening point, parked at the arrow's tail.

    Always laid out left to right on the page, whichever way the arrow points,
    so a joint that takes a bracket and two screws reads "A B D" exactly as the
    inset lists them.

    The natural place is straight back along the tail, far enough that the
    row's own width can never reach the arrowhead. Three things can spoil it:
    the page edge, the inset panel, and another row. Two joints of different
    kinds can sit within a badge of each other - the 6x120 into a ladder rung
    end is 25 mm from the 5x60 driven down into the block below it - and two
    touching circles would read as one two-letter group. So a handful of
    positions are tried (further back, or out to either side of the tail) and
    the cleanest one wins.
    """
    n = len(letters)
    pitch = 2 * BADGE_R + 8
    half = (n * pitch - 8) / 2
    dx, dy = direction
    base = half * abs(dx) + BADGE_R * abs(dy) + 12
    aside = half * abs(dy) + BADGE_R * abs(dx) + 12

    def row_at(cx, cy):
        return [(cx + (i - (n - 1) / 2) * pitch, cy) for i in range(n)]

    tries = [row_at(tail[0] - dx * (base + k * pitch),
                    tail[1] - dy * (base + k * pitch)) for k in range(4)]
    tries += [row_at(tail[0] - dy * s * aside, tail[1] + dx * s * aside)
              for s in (1, -1)]

    def cost(row):
        out = 0
        for c in row:
            if not (page.x0 + BADGE_R + 8 <= c[0] <= page.x1 - BADGE_R - 8
                    and page.y0 + BADGE_R + 8 <= c[1] <= page.y1 - BADGE_R - 8):
                out += 6
            if inset is not None and _in_rect(c, inset, BADGE_R * 0.7):
                out += 3
            out += sum(1 for q in page.badge_spots
                       if not _apart(c, q, 2 * BADGE_R + 6))
        return out

    row = min(((cost(r), k, r) for k, r in enumerate(tries)))[2]
    for centre, ch in zip(row, letters):
        badge(page, centre, ch)


def draw_inset(page, box, view, step_fasteners, glyph_dir, contact):
    """The corner panel: the joint in section, then glyph + count per row."""
    x, y, w, h = box
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=W_RULE)
    rows = step_fasteners[:4]
    row_h = min(h * 0.30, 150.0)
    detail_h = h - row_h * len(rows) - 26
    # A wall fixing has no second member to section, so it gets the fastener
    # rows alone.
    if contact is not None and contact[4] is contact[5]:
        contact = None
    if contact is not None and detail_h > row_h * 0.9:
        joint_section(page, (x + 14, y + h - detail_h - 8, w - 28,
                             detail_h), contact, view)
        page.line((x + 14, y + h - detail_h - 14),
                  (x + w - 14, y + h - detail_h - 14), GREY, W_LEAD)
    top = y + h - detail_h - 26 if detail_h > row_h * 0.9 else y + h - 12
    for name, qty, svg, letter in rows:
        left = x + 16
        if letter:
            badge(page, (left + BADGE_R, top - row_h / 2), letter)
            left += 2 * BADGE_R + 16
        gw, gh = glyph_dims(os.path.join(glyph_dir, svg))
        # Every glyph is drawn to one scale and carries it in its viewBox
        # height, so a long screw stays longer than a short one here too.
        eh = min(row_h * 0.72 * gh / 120.0, row_h * 0.92)
        ew = eh * gw / gh
        avail = x + w - 14 - row_h * 1.5 - left
        if ew > avail:
            eh *= avail / ew
            ew = avail
        page.embed_svg(os.path.join(glyph_dir, svg),
                       left, top - row_h / 2 - eh / 2, ew, eh)
        page.text((x + w - 16, top - row_h / 2 - row_h * 0.20),
                  f"{qty}x", row_h * 0.62, anchor="end", weight="bold")
        top -= row_h


# ---------------------------------------------------------------------------
# THE STEP PAGES
# ---------------------------------------------------------------------------
def _edge_of_box(centre, target, bx, by, bw, bh):
    """Where the line centre->target leaves the inset, so leaders start there."""
    dx, dy = target[0] - centre[0], target[1] - centre[1]
    t = 1.0
    if abs(dx) > 1e-9:
        t = min(t, abs((bw / 2) / dx))
    if abs(dy) > 1e-9:
        t = min(t, abs((bh / 2) / dy))
    return (centre[0] + dx * t, centre[1] + dy * t)


def emptiest_corner(plines, page, box_w, box_h, avoid_top_left=True):
    """Put the inset where the drawing is not."""
    best, best_ink = None, None
    corners = [("tr", page.x1 - box_w - 20, page.y1 - box_h - 20),
               ("br", page.x1 - box_w - 20, page.y0 + 20),
               ("bl", page.x0 + 20, page.y0 + 20)]
    if not avoid_top_left:
        corners.append(("tl", page.x0 + 20, page.y1 - box_h - 20))
    for _name, bx, by in corners:
        ink = sum(1 for pl in plines for p in pl
                  if bx - 30 <= p[0] <= bx + box_w + 30
                  and by - 30 <= p[1] <= by + box_h + 30)
        if best_ink is None or ink < best_ink:
            best, best_ink = (bx, by), ink
    return best


def flat_placement(G, parts):
    """The back frame lying on the floor, for the before/after thumbnails.

    A drawing transform only: it tips the frame about its own bottom edge so
    the reader sees the shape they built flat in the step before. Nothing in
    the model moves.
    """
    from build123d import Compound, Location
    zs = [p.extents[2][0] for p in parts]
    ys = [p.extents[1][0] for p in parts]
    bottom, back = min(zs), min(ys)
    tip = (Location((0, back, bottom))
           * Location((0, 0, 0), (1, 0, 0), -90)
           * Location((0, -back, -bottom)))
    return Compound(children=[p.moved(tip) for p in parts])


def thumbnails(page, view, G, before_parts, box):
    """before -> after, top-left, with an arrow between them."""
    x, y, w, h = box
    cell = (w - 60) / 2
    flat = project(view, [("f", flat_placement(G, before_parts))])["f"]
    up = project(view, [("u", comp(before_parts))])["u"]
    for i, plines in enumerate((flat, up)):
        bx0, by0, bx1, by1 = bounds(plines)
        k = min(cell / max(bx1 - bx0, 1e-6), h / max(by1 - by0, 1e-6)) * 0.86
        cx = x + cell / 2 + i * (cell + 60)
        cy = y + h / 2
        moved = [[(cx + (p[0] - (bx0 + bx1) / 2) * k,
                   cy + (p[1] - (by0 + by1) / 2) * k) for p in pl]
                 for pl in plines]
        page.polylines(moved, INK, W_NEW * 0.55)
    page.arrow((x + cell + 8, y + h / 2), (x + cell + 52, y + h / 2),
               INK, W_MARK, 20)


def info_panel(page, box, G):
    """The mattress panel. Every number is read off the model.

    IKEA writes a maximum here because a thick mattress lifts the sleeper
    towards the top of the guard. This bed is the other way round: the guard
    bands sit at fixed heights and the opening above the mattress is only
    inside EN 747 while the mattress is at least as thick as the model
    assumes. A THINNER mattress opens the gap. So it is a minimum, in bold.
    """
    x, y, w, h = box
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=W_RULE)
    page.circle((x + 40, y + h - 40), 22, width=W_RULE)
    page.text((x + 40, y + h - 50), "i", 46, anchor="middle", weight="bold")
    page.text((x + 78, y + h - 52), "MADRASS", 44, weight="bold")
    page.text((x + 22, y + h - 112),
              f"{G.WALL_SPAN} x {G.MATTRESS_W} mm", 40)
    page.text((x + 22, y + h - 166),
              f"TYKKELSE MIN {G.MATTRESS_H} mm", 44, weight="bold")

    # Section: slat top, mattress, the opening, the lower guard band.
    top = y + h - 200
    bot = y + 30
    z0, z1 = G.SLAT_Z1, G.GUARD_BAND_Z0[0] + G.GUARD_W
    k = (top - bot) / (z1 - z0)
    sx, sw = x + 26, w - 52

    def zy(z):
        return bot + (z - z0) * k

    page.line((sx, zy(G.SLAT_Z1)), (sx + sw, zy(G.SLAT_Z1)), INK, W_RULE)
    page.rect(sx, zy(G.MATTRESS_Z0), sw * 0.78,
              (G.MATTRESS_Z1 - G.MATTRESS_Z0) * k, fill="none", width=W_RULE)
    page.rect(sx, zy(G.GUARD_BAND_Z0[0]), sw * 0.78, G.GUARD_W * k,
              fill="none", width=W_RULE)
    page.text((sx + 18, zy(G.GUARD_BAND_Z0[0]) + G.GUARD_W * k / 2 - 11),
              "REKKVERK", 30)
    page.text((sx + 18, zy(G.MATTRESS_Z0)
               + (G.MATTRESS_Z1 - G.MATTRESS_Z0) * k / 2 - 11),
              "MADRASS", 30)
    gap = G.GUARD_BAND_Z0[0] - G.MATTRESS_Z1
    ax = sx + sw * 0.88
    page.arrow((ax, zy(G.MATTRESS_Z1) + 4), (ax, zy(G.GUARD_BAND_Z0[0])),
               INK, W_LEAD, 12)
    page.arrow((ax, zy(G.GUARD_BAND_Z0[0]) - 4), (ax, zy(G.MATTRESS_Z1)),
               INK, W_LEAD, 12)
    page.text((ax + 16, (zy(G.MATTRESS_Z1) + zy(G.GUARD_BAND_Z0[0])) / 2 - 12),
              f"{int(round(gap))}", 38, weight="bold")


def render_step(G, view, st, uni, placed, out_dir, width, page_box, glyph_dir,
                fasteners):
    from build123d import Compound

    n = st["n"]
    prior = [uni[l] for l in placed if l not in st["highlight"]]
    new = [uni[l] for l in st["highlight"]]
    groups = []
    if prior:
        groups.append(("prior", comp(prior)))
    if new:
        groups.append(("new", comp(new)))
    if not groups:
        return None

    # Grey layer: the combined run, so standing parts are cut where this
    # step's parts pass in front of them. Black layer: a second run on the
    # new parts alone, so the piece being fitted is drawn whole.
    combined = project(view, groups)
    new_only = project(view, [("new", comp(new))])["new"] if new else []

    x0, y0, x1, y1 = page_box
    page = Page(x0, y0, x1, y1)
    page.polylines(combined.get("prior", []), GREY, W_PRIOR)
    page.polylines(new_only, INK, W_NEW)

    # The step number, small, top left.
    page.text((x0 + 34, y1 - 76), str(n), 96, weight="bold")

    # Where the fasteners go, in the drawing's own frame.
    is_mattress = any(p.label.startswith("Mattress") for p in new)
    if "J14" in st["joints"]:
        # The wall fixings do not join two parts of the bed, so there is no
        # contact patch to find: they go through the back rail into the wall
        # behind it. Spread them along that rail's own back face, pointing the
        # way they are driven. The count is the one the joint table carries.
        # One marker per wall fixing, not per joint: the count that matters
        # to the builder is how many screws go into the wall.
        cts = wall_fix_contacts(
            new, max((q for _n, q, _s, _l in fasteners), default=2))
    elif is_mattress:
        cts = []
    else:
        cts = contacts(new, prior)
    # A step that drives only one kind of fastener needs no letters: the glyph
    # in its table is already the whole answer.
    letters = {name: letter for name, _q, _s, letter in fasteners if letter}
    pts = [(view.xy(c[0]), c) for c in cts]
    keep = choose_markers(pts, letters)

    if is_mattress:
        # The information panel carries a section as well as three lines of
        # text, so it needs more room than a fastener list does.
        inset_w, inset_h = page.w * 0.32, page.h * 0.36
    else:
        primary = keep[0][1] if keep else None
        has_section = primary is not None and primary[4] is not primary[5]
        inset_w = page.w * 0.34
        inset_h = min(page.h * 0.40, 30 + 150 * (len(fasteners[:4])
                                                 + (1.6 if has_section else 0.3)))
    bx, by = emptiest_corner(combined.get("prior", []) + new_only,
                             page, inset_w, inset_h)
    # Now that the panel has a place, pick the markers again without the ones
    # it would have swallowed. The first pass only had to be good enough to
    # size the panel, which is the number of fastener rows plus a section or
    # not - and that survives the second.
    box = (bx, by, inset_w, inset_h)
    keep = choose_markers(pts, letters, inset=box) or keep

    if is_mattress:
        info_panel(page, (bx, by, inset_w, inset_h), G)
    elif fasteners:
        draw_inset(page, (bx, by, inset_w, inset_h), view, fasteners,
                   glyph_dir, keep[0][1] if keep else None)

    # A marker at every fastening point: a short arrow along the contact
    # normal, i.e. the direction the screw travels, ending on the joint.
    for p2, c, tags in keep:
        # contacts() always lists the NEW part first, and `sign` is the way
        # from it into the part it lands on - which is the way the screw goes.
        axis = [0.0, 0.0, 0.0]
        axis[c[1]] = c[2]
        dx, dy = view.dir_xy(axis)
        nrm = math.hypot(dx, dy)
        if nrm < 1e-6:
            page.circle(p2, 13, width=W_MARK)
            page.dot(p2, 4)
            if tags:
                badge_row(page, (p2[0], p2[1] + 20), (0.0, -1.0), tags, box)
            continue
        dx, dy = dx / nrm, dy / nrm
        tail = (p2[0] - dx * 62, p2[1] - dy * 62)
        page.arrow(tail, p2, INK, W_MARK, 16)
        if tags:
            badge_row(page, tail, (dx, dy), tags, box)

    # Leaders from the inset to the joints, or one magnifier when there is
    # only a location or two to point at.
    if keep and not is_mattress and fasteners:
        anchor = (bx + inset_w / 2, by + inset_h / 2)
        if len(keep) <= 2:
            src = keep[0][0]
            src_r = max(page.w, page.h) * 0.055
            dst_r = inset_w * 0.30
            dst_c = (bx + inset_w / 2, by + inset_h + dst_r + 60)
            if dst_c[1] + dst_r > y1 - 20:
                dst_c = (bx + inset_w / 2, by - dst_r - 60)
            page.circle(src, src_r, width=W_LEAD)
            clipped = clip_to_circle(new_only, src, src_r)
            clipped_grey = clip_to_circle(combined.get("prior", []), src,
                                          src_r)
            page.circle(dst_c, dst_r, fill="#ffffff", width=W_RULE)
            page.polylines(remap(clipped_grey, src, src_r, dst_c, dst_r),
                           GREY, W_PRIOR * dst_r / src_r)
            page.polylines(remap(clipped, src, src_r, dst_c, dst_r),
                           INK, W_NEW * dst_r / src_r)
            page.line(src, dst_c, GREY, W_LEAD, dash="18 14")
        else:
            # One leader per joint would bury the drawing, so the inset points
            # at the nearest few and the markers carry the rest.
            near = sorted(keep, key=lambda kp: (kp[0][0] - anchor[0]) ** 2
                          + (kp[0][1] - anchor[1]) ** 2)[:4]
            for p2, _c, _tags in near:
                page.line(_edge_of_box(anchor, p2, bx, by, inset_w, inset_h),
                          p2, GREY, W_LEAD, dash="16 14")

    # Before / after: the frame is built flat and then stood up.
    if st.get("thumbnails"):
        tb_w = page.w * 0.30
        tb_h = page.h * 0.22
        thumbnails(page, view, G, st["thumbnails"],
                   (x0 + 30, y1 - tb_h - 130, tb_w, tb_h))

    svg = os.path.join(out_dir, f"steg-{n:02d}.svg")
    png = os.path.join(out_dir, f"steg-{n:02d}.png")
    page.write(svg)
    to_png(svg, png, width)
    print(f"  steg {n:2d}  {len(combined.get('prior', [])):4d} gra / "
          f"{len(new_only):4d} svarte / {len(keep):2d} festepunkt -> {png}")
    return png


def to_png(svg_path, png_path, width):
    rsvg = shutil.which("rsvg-convert")
    if rsvg is None:
        print(f"  ! rsvg-convert not found - {png_path} not written")
        return False
    subprocess.run([rsvg, "-w", str(width), "-b", "white",
                    svg_path, "-o", png_path], check=True)
    return True


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------
def step_fastener_glyphs(st, glyph_dir):
    """[(handelsnavn, antall, svg-filnavn, merkebokstav), ...] for one step.

    Commonest first, ties broken by name - the order the inset draws them in,
    which is also the order the letters run in. tools/gen_doc_tables.py's
    step_badges() derives the same letters from the same rows for the page, so
    the drawing and the table cannot drift apart.
    """
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import gen_glyphs
    rows = []
    for line in st["fasteners"]:
        # "8× Treskrue 5×40 forsenket Torx" - only the count is followed by a
        # space, so the first "× " is the one that separates it.
        qty, name = line.split("× ", 1)
        rows.append((name, int(qty.strip())))
    rows.sort(key=lambda r: (-r[1], r[0]))
    letters = gen_glyphs.BADGE_ALPHABET if len(rows) > 1 else [None] * len(rows)

    out = []
    for (name, qty), letter in zip(rows, letters):
        svg = gen_glyphs.slug(name) + ".svg"
        if os.path.exists(os.path.join(glyph_dir, svg)):
            out.append((name, qty, svg, letter))
    return out


def render_all(G, data, out_dir, width, only):
    uni = universe(G)
    look_at = full_bed(G).bounding_box().center()
    glyph_dir = os.path.join(ROOT, "docs", "img", "beslag")

    # One page rectangle per camera, taken from the FINISHED bed, so nothing
    # jumps between drawings. These are all worked out before a single step
    # is drawn, and each from a freshly built compound: putting a part into a
    # build123d Compound re-parents it, so a compound kept across steps would
    # quietly lose its members to the next one.
    views, pages = {}, {}
    for st in data["steps"]:
        if not st["image"] or not st["camera"]:
            continue
        az, elev, _d = st["camera"]
        key = (az, elev)
        if key in views:
            continue
        views[key] = View(camera_direction(az, elev), look_at)
        bx0, by0, bx1, by1 = bounds(
            project(views[key], [("all", full_bed(G))])["all"])
        pages[key] = (bx0 - PAD, by0 - PAD, bx1 + PAD, by1 + PAD)

    made, placed = [], []
    for st in data["steps"]:
        n = st["n"]
        if not st["image"] or not st["camera"]:
            placed += st["labels"]
            continue
        key = tuple(st["camera"][:2])
        if only is None or n == only:
            st = dict(st)
            if n == 2:
                # The one step that changes the workpiece's orientation.
                st["thumbnails"] = [uni[l] for l in placed]
            png = render_step(G, views[key], st, uni, placed, out_dir, width,
                              pages[key], glyph_dir,
                              step_fastener_glyphs(st, glyph_dir))
            if png:
                made.append(png)
        placed += st["labels"]
    return made


def render_hero(G, out_dir, width, az=330, elev=22):
    bed = full_bed(G)
    look_at = bed.bounding_box().center()
    view = View(camera_direction(az, elev), look_at)
    plines = project(view, [("all", bed)])["all"]
    x0, y0, x1, y1 = bounds(plines)
    page = Page(x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD)
    page.polylines(plines, INK, W_HERO)
    svg = os.path.join(out_dir, "hanna-hero.svg")
    png = os.path.join(out_dir, "hanna-hero.png")
    page.write(svg)
    to_png(svg, png, width)
    print(f"  hero    az {az} elev {elev}  {len(plines)} kanter  -> {png}")
    return png


def main(argv):
    width = 1600
    out_dir = os.path.join(ROOT, "docs", "img")
    only = None
    hero_only = steps_only = False
    i = 1
    while i < len(argv):
        if argv[i] == "--width":
            width = int(argv[i + 1]); i += 2
        elif argv[i] == "--out":
            out_dir = argv[i + 1]; i += 2
        elif argv[i] == "--step":
            only = int(argv[i + 1]); i += 2
        elif argv[i] == "--hero-only":
            hero_only = True; i += 1
        elif argv[i] == "--steps-only":
            steps_only = True; i += 1
        else:
            sys.exit(__doc__)

    with open(STEP_JSON, encoding="utf-8") as fh:
        data = json.load(fh)
    os.makedirs(out_dir, exist_ok=True)

    import generate_loftbed as G

    print("\n=== STREKTEGNINGER ===")
    made = []
    if not hero_only:
        made += render_all(G, data, out_dir, width, only)
    if not steps_only and only is None:
        made.append(render_hero(G, out_dir, width))
    print(f"\n{len(made)} tegninger i {out_dir}")


if __name__ == "__main__":
    main(sys.argv)
