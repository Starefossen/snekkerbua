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

  * the fasteners are DRAWN, not pointed at. generate_loftbed.py models every
    screw, bolt and bracket in the bed as a solid with an anchor on the face
    it is driven from and a unit drive vector, and this file projects those
    records: on most pages backed out along their own axis with a dotted
    insertion line into the hole, on the pages that drive twenty-eight of the
    same screw drawn where they end up with the buried part dashed. There is
    no second copy of the joint table here and no direction derived here -
    the picture and docs/generated/skrueretninger.md are the same numbers.
  * the corner inset carries the step's fasteners at large scale with their
    counts, and one SECTION per joint family in the step: the two members at
    their true cross-section sizes and true relative positions, hatched the way
    a cut piece of timber is hatched, with every fastener of that joint drawn
    at its true length crossing the interface - head on the entry side, tip
    inside the receiving member.
  * a marker is allowed to stand for more than one screw (two screws 30 mm
    apart are one mark on a page this size), and then it carries the count:
    "2x" beside the badge. It never merges across JOINTS, though, because
    "4x" in a corner that takes two screws in one joint and two in another
    would send the builder to the wrong holes. Nothing is thinned away - a
    mark dropped for crowding hands its count to the mark that crowded it,
    and the page is checked at build time to show every fastener the step's
    table lists.
  * leader lines run from the inset to the fastening points; a step with only
    one or two of them gets a circular magnifier of the real line work there
    instead.
  * the step that stands the back frame up gets before/after thumbnails, the
    second being the same parts drawn again from a laid-flat placement. That
    placement is a drawing transform - it moves nothing in the model.
  * the mattress step gets an information panel whose numbers (platform top,
    mattress thickness, guard-band underside, and the opening between them)
    are read off the model.

TWO PAGES ARE NOT PROJECTIONS OF THE BED
----------------------------------------
Steg 0 is the morning on the trestles - there is nothing standing to draw - and
steg 10 is a 680 mm sub-assembly that disappears inside a 2 m frame. They get
their own modules, called from render_all() with the same arguments as any
other step so the driver does not have to know they are special:

    tools/render_cutpage.py   every board bought, to scale, with its cuts
    tools/render_panel.py     the loose panel, exploded, on its own

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
W_MARK = 5.2           # fastening-point markers - the page's loudest line
W_HATCH = 1.5          # the 45 deg hatching on a cut face
GREY = "#9a9a9a"
INK = "#111111"

# Arrows are for WOOD now - the before/after thumbnails, the dimension marks
# on the mattress panel, the screwdriver stub in a section, and the exploded
# panel page. A fastener is drawn as itself; see DRAWING A FASTENER below.
HEAD_FRAC = 0.22       # arrowhead length, as a fraction of the arrow
# Above this many marks on one page the exploded style stops helping - the
# slat fields drive one screw per slat end and there are twenty-eight of them,
# and twenty-eight screws hanging in the air over a bed is a hedge, not an
# instruction. Those pages get the in-situ phantom instead.
EXPLODE_MAX = 18

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
# Nowhere, as far as this file is concerned. generate_loftbed.py places every
# fastener in the bed as a record with an anchor, a unit drive vector, a
# length and the two members it ties - the same records it builds the solids
# from - and a drawing is just those records seen from a camera. The contact
# patches, the joint table, the fit rule and the EC5 row geometry all live
# there now; what used to be a second copy of them in this file is gone.
def step_marks(G, st, letters, view):
    """One mark per fastener the step drives, in the drawing's own frame."""
    out = []
    for f in G.FASTENER_SPECS:
        if f["jid"] not in st["joints"]:
            continue
        if f["kind"] == "plate":
            p3 = tuple(a + r * f["reach"] * 0.5
                       for a, r in zip(f["anchor"], f["run"]))
            d3 = f["direction"]
        else:
            # The head is on the entry face; the mark sits at the TIP, which
            # is inside the member the fastener grips. That is the end of it
            # the reader has to believe in.
            p3 = tuple(a + d * f["length"]
                       for a, d in zip(f["anchor"], f["direction"]))
            d3 = f["direction"]
        area = f["contact"][3] if f["contact"] is not None else 1e9
        out.append(dict(p3=p3, p2=view.xy(p3), dir3=d3, per=1, jid=f["jid"],
                        name=f["name"], letter=letters.get(f["name"]),
                        area=area, spec=f))
    return out


def mark_parts(mark):
    """The wooden parts a mark is about - for the coverage check.

    tools/render_panel.py composes its own marks (its page is an exploded
    sub-assembly, not a projection of the bed), so a mark is allowed to name
    its parts directly instead of carrying a fastener record.
    """
    if "spec" not in mark:
        return list(mark["parts"])
    f = mark["spec"]
    return [p for p in (f.get("pa"), f.get("pb"), f.get("through"),
                        f.get("into")) if p is not None]


# ---------------------------------------------------------------------------
# DRAWING A FASTENER
# ---------------------------------------------------------------------------
# The arrows are gone. What used to be a stroke pointing at a joint is now the
# fastener itself, at its own length, along its own axis, in the place the
# model put it - and the two conventions Agrawala's assembly-instruction work
# settles on are what tell the two states apart:
#
#   IN SITU   the fastener where it ends up. The head is solid, because that
#             is the part you can see; everything buried in wood is DASHED.
#             A phantom line is how a drawing says "this is really there and
#             you cannot see it", and it is the only honest way to show a
#             screw that is entirely inside two pieces of timber.
#   EKSPLODERT the fastener backed straight out along its own axis, solid,
#             with a DOTTED insertion line running from it through the hole
#             it goes into. Dotted for fasteners; arrows are reserved for
#             WOOD parts being brought together, which is Agrawala's rule and
#             the reason the two never get confused on one page.
#
# One licence is taken, and it is the same one every hardware drawing takes:
# the DIAMETER is exaggerated. A 6 mm screw on a 2 m page is thinner than the
# line the bed itself is drawn with, so it is fattened until head, shank and
# point read as three different things. The LENGTH is true - it is the number
# the reader has to get right.
W_SCREW = 4.2
W_PHANTOM = 3.0
DASH_PHANTOM = "15 11"
DASH_INSERT = "4 13"           # dotted: fasteners only
SCREW_FATTEN = 2.2
# No fastener is drawn shorter than this fraction of its true length. Straight
# foreshortening is information - a screw driven into the page SHOULD look
# short - but past a point it stops being a screw and becomes a dot, and the
# reader loses the one number the drawing has to get right.
FORESHORTEN_FLOOR = 0.72
EXPLODE_FRAC = 0.10            # of the page's short side
STACK_STEP = 0.6               # coaxial screws, as a fraction of the head


def _unit2(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return (dx / n, dy / n, n) if n > 1e-9 else (0.0, 0.0, 0.0)


def screw_shape(view, anchor, direction, length, d, fatten=SCREW_FATTEN):
    """(outline, head-end, tip-end, unit) for one screw, on the page.

    `outline` is the silhouette in page coordinates: head, countersink,
    shank, point. `None` when the screw points straight at the reader and has
    no length on the page at all - the caller draws a ringed dot instead.
    """
    tip3 = tuple(a + c * length for a, c in zip(anchor, direction))
    p0, p1 = view.xy(anchor), view.xy(tip3)
    ux, uy, L = _unit2(p0, p1)
    if L < length * FORESHORTEN_FLOOR * 0.5:
        return None, p0, p1, (0.0, 0.0)
    L = max(L, length * FORESHORTEN_FLOOR)
    w = d * fatten
    hw, head_l, tip_l = w * 0.95, w * 0.30, w * 0.85

    def P(t, q):
        return (p0[0] + ux * t - uy * q, p0[1] + uy * t + ux * q)

    prof = [(0, hw), (head_l, w / 2), (L - tip_l, w / 2), (L, 0),
            (L - tip_l, -w / 2), (head_l, -w / 2), (0, -hw)]
    return [P(t, q) for t, q in prof], p0, p1, (ux, uy)


def plate_quads(spec):
    """The two flanges of a bracket as 3-D quads, off the model's own record.

    A hook has three; the middle one is the leg that goes down past the edge.
    Every corner here is computed the same way generate_loftbed.py computes
    the solid, so the drawing cannot show a bracket the model does not have.
    """
    C = spec["anchor"]
    n = spec["direction"]
    r = spec["run"]
    w = spec["width"]
    reach = spec["reach"]
    cx = [j for j in range(3)
          if abs(n[j]) < 0.5 and abs(r[j]) < 0.5][0]

    def quad(o, along, dist):
        out = []
        for s_along, s_cross in ((0, -1), (dist, -1), (dist, 1), (0, 1)):
            p = list(o)
            for j in range(3):
                p[j] += along[j] * s_along
            p[cx] += s_cross * w / 2
            out.append(tuple(p))
        return out

    faces = [quad(C, r, reach), quad(C, tuple(-c for c in n), reach)]
    if spec.get("hook"):
        ax = max(range(3), key=lambda j: abs(n[j]))
        into = spec["into"]
        far = into.extents[ax][0] if n[ax] < 0 else into.extents[ax][1]
        drop = list(C)
        drop[ax] = far + n[ax] * 4.0
        faces = [quad(C, r, reach),
                 quad(C, n, abs(drop[ax] - C[ax])),
                 quad(tuple(drop), tuple(-c for c in r), spec["hook"])]
    return faces


def draw_fastener(page, view, m, style, shift=(0.0, 0.0, 0.0), stack=0):
    """One fastener on the page. Returns the point its insertion line ends at.

    `stack` pushes coaxial fasteners apart sideways: two screws driven into
    the same joint from the same face land on the same page point when the
    camera looks along their axis, and an exploded pile of them is one screw
    as far as the reader can tell.
    """
    f = m["spec"]
    anchor = tuple(a + s for a, s in zip(f["anchor"], shift))
    solid = style == "eksplodert"
    if f["kind"] == "plate":
        polys = []
        for q in plate_quads(dict(f, anchor=anchor)):
            polys.append([view.xy(p) for p in q] + [view.xy(q[0])])
        if solid:
            for pl in polys:
                page.poly(pl, fill=INK, stroke=INK, width=W_RULE * 0.6)
        else:
            for pl in polys:
                page.poly(pl, fill="#ffffff", stroke=INK, width=W_RULE)
        seat = view.xy(anchor)
        run_end = view.xy(tuple(a + r * f["reach"]
                                for a, r in zip(anchor, f["run"])))
        return run_end, seat

    outline, p0, p1, u = screw_shape(view, anchor, f["direction"],
                                     f["length"], f["d"])
    if stack:
        off = f["d"] * SCREW_FATTEN * STACK_STEP * stack
        nx, ny = (-u[1], u[0]) if u != (0.0, 0.0) else (1.0, 0.0)
        p0 = (p0[0] + nx * off, p0[1] + ny * off)
        p1 = (p1[0] + nx * off, p1[1] + ny * off)
        if outline:
            outline = [(x + nx * off, y + ny * off) for x, y in outline]
    if outline is None:
        _ = None
        # Straight at the reader: the drawing convention for an axis with no
        # length on the page is a ringed dot, and it is the same mark whether
        # the screw is in or out.
        page.circle(p0, 14, width=W_SCREW)
        page.dot(p0, 5)
        return p0, p0
    if solid:
        page.poly(outline, fill="#ffffff", stroke=INK, width=W_SCREW)
    else:
        # In situ: the head is the only part anybody can see, so it is the
        # only part drawn solid. The rest is a phantom line.
        # The head is the only part anybody can see, so it is the only part
        # drawn solid. The rest is a phantom line - same ink, dashed, a shade
        # lighter in weight, which is the drawing convention for "this is
        # really there and it is inside the wood".
        page.polylines([outline[1:len(outline) - 1] + [outline[1]]],
                       INK, W_SCREW * 0.62, dash=DASH_PHANTOM)
        page.poly(outline[:2] + outline[-2:], fill=INK, stroke=INK,
                  width=W_SCREW * 0.8)
    return p0, p1


def _apart(a, b, gap):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 > gap * gap


def _in_rect(p, rect, grow=0.0):
    x, y, w, h = rect
    return (x - grow <= p[0] <= x + w + grow
            and y - grow <= p[1] <= y + h + grow)


def choose_marks(marks, gap, inset=None):
    """Thin the marks to what a page can hold WITHOUT losing a single screw.

    Two fasteners of the same kind driven at the same joint 30 mm apart are
    one mark at this scale, and so are the two ends of a joint that the camera
    happens to stack. It never merges across JOINTS, though: on step 3 the two
    6x90 into the end beam and the one into the bearing block under it land in
    the same corner, and "3x" there would tell the builder to put three screws
    in one place. Two joints, two marks, 2x and 1x.
    A mark that is crowded out does not disappear:
    its count is handed to the mark that crowded it, and that mark says "4x"
    instead of "2x". The same happens to a mark that lands under the inset
    panel, which is opaque and would hide the very line work the arrow is
    about. render_step() then checks the totals against the step's own
    fastener table, so nothing can go missing silently.
    """
    kept = []
    deferred = []
    for m in sorted(marks, key=lambda q: (-q["area"], q["p2"])):
        if inset is not None and _in_rect(m["p2"], inset, 10.0):
            deferred.append(m)
            continue
        # Same fastener, same spot on the page: one mark, and it counts them
        # both. This crosses joint numbers on purpose - at the end of a ladder
        # rung the 5x60 driven down into the block and the two driven through
        # the block into the stile are three screws in one corner, and three
        # badges there say nothing the number does not say better.
        same = [q for q in kept
                if q["letter"] == m["letter"] and q["name"] == m["name"]
                and q["jid"] == m["jid"]
                and not _apart(q["p2"], m["p2"], gap)]
        if same:
            same[0]["per"] += m["per"]
            same[0]["absorbed"].append(m)
            continue
        kept.append(dict(m, absorbed=[]))
    for m in deferred:
        same = [q for q in kept
                if q["name"] == m["name"] and q["jid"] == m["jid"]]
        if same:
            same.sort(key=lambda q: (q["p2"][0] - m["p2"][0]) ** 2
                      + (q["p2"][1] - m["p2"][1]) ** 2)
            same[0]["per"] += m["per"]
            same[0]["absorbed"].append(m)
        else:
            kept.append(dict(m, absorbed=[]))
    return kept


def mark_families(mark, families):
    return {families.get(p.label) for p in mark_parts(mark)} - {None}


def restore_orphans(kept, families, want):
    """Give back any mark whose merge cost a part its only showing.

    Merging is a legibility trick and it is allowed to lose a joint NUMBER -
    three 5x60 in one ladder corner are one arrow - but it is never allowed to
    lose a PART. The bench-rail bearing block sits 54 mm under the rail end it
    carries, close enough on the page to be swallowed by the rail's own mark,
    and then the drawing is back to listing a block it never shows anyone
    fastening. So: whatever the merge covered up, hand it back its own arrow.
    """
    for _ in range(len(want) + 1):
        covered = set()
        for m in kept:
            covered |= mark_families(m, families)
        missing = want - covered
        if not missing:
            return kept
        for host in kept:
            hit = next((a for a in host["absorbed"]
                        if mark_families(a, families) & missing), None)
            if hit is None:
                continue
            host["absorbed"].remove(hit)
            host["per"] -= hit["per"]
            kept.append(dict(hit, absorbed=[]))
            break
        else:
            return kept
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

    def polylines(self, plines, colour, width, opacity=None, dash=None):
        if not plines:
            return
        d = " ".join("M" + " L".join(self._p(p) for p in pl)
                     for pl in plines if len(pl) > 1)
        if not d:
            return
        extra = f' opacity="{opacity}"' if opacity else ""
        if dash:
            extra += f' stroke-dasharray="{dash}"'
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

    def poly(self, pts, fill="#ffffff", stroke=INK, width=W_RULE):
        d = "M" + " L".join(self._p(p) for p in pts) + " Z"
        self.body.append(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{_f(width)}" stroke-linejoin="round"/>')

    def clip_begin(self, centre, r):
        """Everything until clip_end() is cut to a circle - the magnifiers."""
        self._clips = getattr(self, "_clips", 0) + 1
        cid = f"mag{self._clips}"
        self.body.append(
            f'<defs><clipPath id="{cid}"><circle cx="{_f(centre[0])}" '
            f'cy="{_f(-centre[1])}" r="{_f(r)}"/></clipPath></defs>'
            f'<g clip-path="url(#{cid})">')

    def clip_end(self):
        self.body.append("</g>")

    def hatch(self, x, y, w, h, step, colour=INK, width=W_HATCH):
        """45 deg lines inside a rectangle - the drawing convention for a
        piece of timber that has been cut through."""
        segs = []
        c = math.floor((x - (y + h)) / step) * step
        while c <= (x + w) - y:
            t0 = max(y, x - c)
            t1 = min(y + h, x + w - c)
            if t1 > t0:
                segs.append(((c + t0, t0), (c + t1, t1)))
            c += step
        if not segs:
            return
        d = " ".join(f"M{self._p(a)} L{self._p(b)}" for a, b in segs)
        self.body.append(
            f'<path d="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{_f(width)}"/>')

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
def _long_axis(part):
    sizes = [part.extents[j][1] - part.extents[j][0] for j in range(3)]
    return sizes.index(max(sizes))


def joint_section(page, box, specs, letters, letter_label=""):
    """ONE joint, cut through and drawn honestly.

    Both members keep their real cross-section: an axis is only trimmed where
    it is the member's own LENGTH, because a 1794 mm rail drawn whole beside a
    36 mm post would leave the joint a line. The cut faces are hatched the way
    a sawn piece of timber is hatched, and every fastener the joint takes is
    drawn AT ITS OWN ANCHOR, LENGTH AND DIRECTION - the record the model made
    the solid from - entering on the face it is driven from with its point
    buried in the member it grips. A bracket is the black bent plate lying on
    the faces it is screwed to.
    """
    x, y, w, h = box
    contact = specs[0]["contact"]
    k = contact[1]
    pa, pb = specs[0]["pa"], specs[0]["pb"]

    # The second axis of the cut: the one the fasteners actually travel along,
    # so a section always shows a screw at its length rather than end on.
    # Failing that, cut along Z whenever one of the two members RUNS THROUGH
    # the joint vertically - a post, a ladder stile - because then the section
    # is an elevation and the reader can see which member is the continuous
    # one. Only where neither applies does the cut fall back to the narrower
    # axis, which keeps the detail compact.
    across = [j for j in range(3) if j != k]
    weight = {j: sum(abs(f["direction"][j]) for f in specs) for j in across}
    if max(weight.values()) > 1e-6:
        u = max(across, key=lambda j: weight[j])
    elif 2 in across and 2 in (_long_axis(pa), _long_axis(pb)):
        u = 2
    else:
        u = min(across,
                key=lambda j: min(pa.extents[j][1] - pa.extents[j][0],
                                  pb.extents[j][1] - pb.extents[j][0]))

    # Every fastener as a 2-D run in the (k, u) plane: where it starts and
    # where it ends, straight off the record.
    draw = []
    for f in specs:
        a0 = (f["anchor"][k], f["anchor"][u])
        if f["kind"] == "plate":
            draw.append(dict(kind="plate", a=a0,
                             run=(f["run"][k], f["run"][u]),
                             nrm=(f["direction"][k], f["direction"][u]),
                             reach=f["reach"], t=f["t"]))
            continue
        v = (f["direction"][k], f["direction"][u])
        n = math.hypot(*v)
        if n < 1e-6:                       # straight out of the section
            continue
        draw.append(dict(kind="screw", a=a0, v=(v[0] / n, v[1] / n),
                         length=f["length"] * n, d=f["d"]))

    # The window: whole cross-sections, trimmed lengths, and room for the
    # fasteners that stick out of them.
    win = {}
    for i, j in ((0, k), (1, u)):
        lo, hi = None, None
        for part in (pa, pb):
            if _long_axis(part) == j:
                continue
            a0, a1 = part.extents[j]
            lo = a0 if lo is None else min(lo, a0)
            hi = a1 if hi is None else max(hi, a1)
        for sdr in draw:
            pts = [sdr["a"][i]]
            if sdr["kind"] == "plate":
                pts.append(sdr["a"][i] + sdr["run"][i] * sdr["reach"])
                pts.append(sdr["a"][i] - sdr["nrm"][i] * sdr["reach"])
            else:
                pts.append(sdr["a"][i] + sdr["v"][i] * sdr["length"])
                pts.append(sdr["a"][i] - sdr["v"][i] * 8)
            lo = min([lo] + pts) if lo is not None else min(pts)
            hi = max([hi] + pts) if hi is not None else max(pts)
        if lo is None:                     # both members run along this axis
            lo, hi = contact[0][j] - 60, contact[0][j] + 60
        runs_through = any(_long_axis(part) == j for part in (pa, pb))
        pad = (max((hi - lo) * 0.34, 30.0) if runs_through
               else max((hi - lo) * 0.16, 14.0))
        win[j] = (lo - pad, hi + pad)

    def rect_of(part):
        return {j: (max(part.extents[j][0], win[j][0]),
                    min(part.extents[j][1], win[j][1])) for j in (k, u)}

    # Z always goes up the page; the joint axis takes the other direction.
    v_ax = k if k == 2 else u
    h_ax = u if k == 2 else k
    span_x = win[h_ax][1] - win[h_ax][0]
    span_y = win[v_ax][1] - win[v_ax][0]
    scale = min(w * 0.92 / max(span_x, 1e-6), h * 0.80 / max(span_y, 1e-6))
    cx, cy = x + w / 2, y + h * 0.44

    def px(v):
        return cx + (v - (win[h_ax][0] + win[h_ax][1]) / 2) * scale

    def py(v):
        return cy + (v - (win[v_ax][0] + win[v_ax][1]) / 2) * scale

    def pt(a):
        """(k-value, u-value) -> the page."""
        return (px(a[0] if h_ax == k else a[1]),
                py(a[0] if v_ax == k else a[1]))

    for part in (pa, pb):
        r = rect_of(part)
        if r[k][1] <= r[k][0] or r[u][1] <= r[u][0]:
            continue
        x0, y0 = px(r[h_ax][0]), py(r[v_ax][0])
        pw = (r[h_ax][1] - r[h_ax][0]) * scale
        ph = (r[v_ax][1] - r[v_ax][0]) * scale
        page.rect(x0, y0, pw, ph, fill="#ffffff", width=W_RULE)
        page.hatch(x0, y0, pw, ph, max(min(pw, ph) / 4.2, 9.0))

    for sdr in draw:
        o = pt(sdr["a"])
        if sdr["kind"] == "plate":
            # Two flanges at right angles: one along `run` out of the corner,
            # one along the drive vector reversed. That IS the bracket.
            t = sdr["t"] * scale
            for along, side in ((sdr["run"], sdr["nrm"]),
                                (tuple(-c for c in sdr["nrm"]), sdr["run"])):
                al = pt((sdr["a"][0] + along[0] * sdr["reach"],
                         sdr["a"][1] + along[1] * sdr["reach"]))
                ux, uy = al[0] - o[0], al[1] - o[1]
                n = math.hypot(ux, uy) or 1.0
                nx, ny = -uy / n * t, ux / n * t
                page.poly([o, al, (al[0] - nx, al[1] - ny),
                           (o[0] - nx, o[1] - ny)],
                          fill=INK, stroke=INK, width=W_RULE * 0.6)
            continue
        # The screw itself, drawn along its own vector.
        vx, vy = sdr["v"]
        dx, dy = pt((sdr["a"][0] + vx, sdr["a"][1] + vy))
        ux, uy = dx - o[0], dy - o[1]
        n = math.hypot(ux, uy) or 1.0
        ux, uy = ux / n, uy / n
        L = sdr["length"] * scale
        d = max(sdr["d"] * scale, 5.0)
        head_d, head_l, tip_l = d * 1.9, d * 0.55, d * 1.7

        def P(t_, q, o=o, ux=ux, uy=uy):
            return (o[0] + ux * t_ - uy * q, o[1] + uy * t_ + ux * q)

        prof = [(0, head_d / 2), (head_l, d / 2), (L - tip_l, d / 2),
                (L, 0), (L - tip_l, -d / 2), (head_l, -d / 2),
                (0, -head_d / 2)]
        page.poly([P(t_, q) for t_, q in prof], fill="#ffffff", stroke=INK,
                  width=W_RULE * 0.8)
        # A short arrow behind the head: the way the screwdriver goes.
        page.arrow(P(-L * 0.42, 0), P(-head_d * 0.55, 0), INK, W_MARK * 0.7,
                   head_d * 0.7)

    for i, ch in enumerate(letter_label):
        badge(page, (x + BADGE_R * 0.9 + i * BADGE_R * 1.7,
                     y + h - BADGE_R * 0.9), ch, BADGE_R * 0.82)


BADGE_R = 25.0         # the circled letters, model mm


def badge(page, centre, letter, r=BADGE_R):
    """One circled sans letter - the same mark the step table carries."""
    page.circle(centre, r, fill="#ffffff", stroke=INK, width=W_RULE)
    page.text((centre[0], centre[1] - r * 0.40), letter,
              r * 1.20, anchor="middle", weight="bold")
    page.badge_spots.append(centre)


def mark_label(page, tail, direction, letter, count, inset=None):
    """One arrow's caption, parked behind its tail.

    A mark carries at most one letter now - each kind of fastener points at
    its own spot - and beside it the number of screws that mark stands for.
    "2x" is there because a marker is not always one screw: two 5x60 driven
    30 mm apart into the same rekkverksbord end are one arrow at this scale,
    and the page has to say so.

    The natural place is straight back along the tail. Three things can spoil
    it: the page edge, the inset panel, and another caption - so a handful of
    positions are tried and the cleanest one wins.
    """
    dx, dy = direction
    txt = f"{count}x" if count > 1 else ""
    w_txt = 0.0 if not txt else BADGE_R * (1.10 * len(txt))
    if letter:
        span = 2 * BADGE_R + (w_txt + 6 if txt else 0)
    else:
        span = w_txt
    base = span / 2 * abs(dx) + BADGE_R * abs(dy) + 14
    aside = span / 2 * abs(dy) + BADGE_R * abs(dx) + 14

    def spots(cx, cy):
        """Badge centre and text anchor for a caption centred on (cx, cy)."""
        left = cx - span / 2
        if letter:
            return (left + BADGE_R, cy), (left + 2 * BADGE_R + 6, cy)
        return None, (left, cy)

    tries = [(tail[0] - dx * (base + k * BADGE_R * 1.7),
              tail[1] - dy * (base + k * BADGE_R * 1.7)) for k in range(5)]
    for s in (1, -1):
        for k in range(3):
            tries.append((tail[0] - dy * s * (aside + k * BADGE_R * 1.6)
                          - dx * k * BADGE_R * 0.8,
                          tail[1] + dx * s * (aside + k * BADGE_R * 1.6)
                          - dy * k * BADGE_R * 0.8))

    def cost(c):
        out = 0
        for probe in (c, (c[0] - span / 2, c[1]), (c[0] + span / 2, c[1])):
            if not (page.x0 + BADGE_R + 8 <= probe[0] <= page.x1 - BADGE_R - 8
                    and page.y0 + BADGE_R + 8 <= probe[1]
                    <= page.y1 - BADGE_R - 8):
                out += 10
            if inset is not None and _in_rect(probe, inset, BADGE_R * 0.7):
                out += 14
            out += sum(1 for q in page.badge_spots
                       if not _apart(probe, q, 2 * BADGE_R + 4))
        return out

    centre = min(((cost(c), k, c) for k, c in enumerate(tries)))[2]
    b_at, t_at = spots(*centre)
    if b_at is not None:
        badge(page, b_at, letter)
    if txt:
        page.text((t_at[0], t_at[1] - BADGE_R * 0.42), txt, BADGE_R * 1.25,
                  weight="bold")
        page.badge_spots.append((t_at[0] + w_txt / 2, t_at[1]))


# The inset panel is the same shape on every page: the same fraction of the
# page's width, the same fastener-row height, the same glyph scale. A step
# with one fastener therefore gets a SHORTER panel, never a smaller one - the
# rows do not stretch to fill it and the glyphs do not shrink to fit it.
INSET_W_FRAC = 0.345          # of the page width
INSET_ROW_FRAC = 0.185        # row height, of the panel width
INSET_CELL_FRAC = 0.62        # section-cell height, of the cell width
INSET_PAD = 16.0              # model mm, inside the panel border


def inset_layout(page, n_sections, n_rows):
    """(w, h, cols, cell_w, cell_h, row_h) - worked out before it is drawn,
    because the panel has to be placed before the markers are chosen."""
    w = page.w * INSET_W_FRAC
    row_h = w * INSET_ROW_FRAC
    cols = 1 if n_sections <= 1 else 2
    rows_of_cells = -(-n_sections // cols) if n_sections else 0
    cell_w = (w - 2 * INSET_PAD) / cols
    cell_h = cell_w * INSET_CELL_FRAC
    h = (2 * INSET_PAD + rows_of_cells * cell_h
         + (10 if n_sections else 0) + n_rows * row_h)
    return w, h, cols, cell_w, cell_h, row_h


def draw_inset(page, box, sections, step_fasteners, glyph_dir, letters):
    """The corner panel: one section per joint in the step, then the
    fasteners at large scale with their counts."""
    x, y, w, h = box
    rows = step_fasteners[:4]
    _w, _h, cols, cell_w, cell_h, row_h = inset_layout(page, len(sections),
                                                       len(rows))
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=W_RULE)

    top = y + h - INSET_PAD
    for i, (specs, label) in enumerate(sections):
        cx = x + INSET_PAD + (i % cols) * cell_w
        cy = top - (i // cols + 1) * cell_h
        joint_section(page, (cx, cy, cell_w, cell_h), specs, letters, label)
    if sections:
        top -= (-(-len(sections) // cols)) * cell_h + 10
        page.line((x + INSET_PAD, top + 4), (x + w - INSET_PAD, top + 4),
                  GREY, W_LEAD)

    for name, qty, svg, letter in rows:
        left = x + INSET_PAD
        if letter:
            badge(page, (left + BADGE_R, top - row_h / 2), letter)
            left += 2 * BADGE_R + 14
        gw, gh = glyph_dims(os.path.join(glyph_dir, svg))
        # Every glyph is drawn to one scale and carries it in its viewBox
        # height, so a long screw stays longer than a short one here too.
        eh = min(row_h * 0.70 * gh / 120.0, row_h * 0.90)
        ew = eh * gw / gh
        avail = x + w - INSET_PAD - row_h * 1.6 - left
        if ew > avail:
            eh *= avail / ew
            ew = avail
        page.embed_svg(os.path.join(glyph_dir, svg),
                       left, top - row_h / 2 - eh / 2, ew, eh)
        page.text((x + w - INSET_PAD, top - row_h / 2 - row_h * 0.20),
                  f"{qty}x", row_h * 0.60, anchor="end", weight="bold")
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


def emptiest_corner(plines, page, box_w, box_h, marks=(),
                    avoid_top_left=False):
    """Put the inset where the drawing is not - and, above all, where the
    fastening points are not: a joint the panel covers loses its own arrow and
    has to hand its count to a joint somewhere else on the page."""
    best, best_cost = None, None
    corners = [("tr", page.x1 - box_w - 20, page.y1 - box_h - 20),
               ("br", page.x1 - box_w - 20, page.y0 + 20),
               ("bl", page.x0 + 20, page.y0 + 20)]
    if not avoid_top_left:
        corners.append(("tl", page.x0 + 20, page.y1 - box_h - 20))
    for _name, bx, by in corners:
        box = (bx, by, box_w, box_h)
        cost = sum(1 for pl in plines for p in pl if _in_rect(p, box, 30))
        cost += 60 * sum(1 for m in marks if _in_rect(m["p2"], box, 40))
        if best_cost is None or cost < best_cost:
            best, best_cost = (bx, by), cost
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


def magnifier(page, src, dst_c, dst_r, src_r, new_only, prior_lines):
    """The real line work around one point, blown up in a circle."""
    page.circle(src, src_r, width=W_LEAD)
    page.line(src, dst_c, GREY, W_LEAD, dash="18 14")
    page.circle(dst_c, dst_r, fill="#ffffff", width=W_RULE)
    page.polylines(remap(clip_to_circle(prior_lines, src, src_r),
                         src, src_r, dst_c, dst_r),
                   GREY, W_PRIOR * dst_r / src_r)
    page.polylines(remap(clip_to_circle(new_only, src, src_r),
                         src, src_r, dst_c, dst_r),
                   INK, W_NEW * dst_r / src_r)


def ledger_bracket_detail(page, view, keep, new_only, prior_lines, inset):
    """WHERE the 40x40x40 sits, and which way its four screws go.

    The bracket is the one piece of hardware in the bed that an overview
    drawing cannot place: it is 40 mm of steel behind a 1794 mm ledger, and at
    page scale it is a smudge. So it gets a magnifier - the real line work of
    the joint, blown up, with the bracket drawn on top in its true position:
    the standing leg flat on the post's inner face, the lying leg under the
    ledger's end, two screws into each.
    """
    # Either end of the ledger does; take the one whose locator circle is not
    # half off the paper - the corner posts sit on the page's own edge.
    room = max(page.w, page.h) * 0.072 + 10
    cands_m = [m for m in keep if m["jid"] == "J12"]
    inside = [m for m in cands_m
              if page.x0 + room <= m["p2"][0] <= page.x1 - room
              and page.y0 + room <= m["p2"][1] <= page.y1 - room]
    mark = (inside or cands_m or [None])[0]
    if mark is None:
        return
    f = mark["spec"]
    pa, pb = f["pa"], f["pb"]
    post = pa if pa.label.startswith("Corner Post Back") else pb
    ledger = pb if post is pa else pa
    # The mark's own arrow overshoots into the post, so the sign is the way
    # the screw travels; the bracket lies the other way, out under the ledger.
    e = 1.0 if ledger.extents[0][0] > post.extents[0][0] else -1.0
    xf = post.extents[0][1] if e > 0 else post.extents[0][0]
    zf = ledger.extents[2][0]
    y0, y1 = post.extents[1]
    ym = (y0 + y1) / 2
    leg = next((q["spec"]["reach"] for q in cands_m
                if q["spec"]["kind"] == "plate"), 40.0)

    # Centred on the CORNER itself - post face meets ledger underside - so the
    # circle holds a piece of both members and not just the steel.
    src = view.xy((xf, ym, zf))
    # Tight on the STEEL: a circle scaled to the page would put a 40 mm
    # bracket at a tenth of its diameter and the magnifier would magnify
    # nothing. Three flange lengths across is what makes the bend readable.
    src_r = leg * 3.0
    dst_r = page.w * 0.145
    edge = dst_r + 105                    # room for the caption under it
    # Away from the inset panel, in the emptiest of the two low corners.
    ix, iy, iw, ih = inset
    cands = [(page.x0 + edge, page.y0 + edge),
             (page.x1 - edge, page.y0 + edge),
             (page.x0 + edge, page.y1 - edge),
             (page.x1 - edge, page.y1 - edge)]
    def ink(c2):
        if _in_rect(c2, (ix - dst_r, iy - dst_r, iw + 2 * dst_r,
                         ih + 2 * dst_r)):
            return 10 ** 6
        return sum(1 for pl in new_only + prior_lines for p in pl
                   if math.hypot(p[0] - c2[0], p[1] - c2[1]) < dst_r * 1.15)
    dst_c = min(cands, key=ink)

    # The locator on the drawing itself, heavy enough to be found, and the
    # dashed leader out to the blown-up circle.
    page.circle(src, src_r, width=W_MARK * 0.7)
    page.line(src, dst_c, GREY, W_LEAD, dash="18 14")
    page.circle(dst_c, dst_r, fill="#ffffff", width=W_RULE)
    page.clip_begin(dst_c, dst_r)
    k = dst_r / src_r

    def P(p3):
        p = view.xy(p3)
        return (dst_c[0] + (p[0] - src[0]) * k, dst_c[1] + (p[1] - src[1]) * k)

    # The two members, as the faces the bracket is actually screwed to: the
    # post's inner face, and the ledger's underside and front. Filled light so
    # they read as timber, with the real projected edges drawn back on top.
    ly0, ly1 = ledger.extents[1]
    lz1 = ledger.extents[2][1]
    reach = leg * 2.4
    faces = [
        [(xf, y0, zf - reach * 0.5), (xf, y1, zf - reach * 0.5),
         (xf, y1, zf + reach), (xf, y0, zf + reach)],          # stolpens innerflate
        [(xf, ly0, zf), (xf, ly1, zf), (xf + e * reach, ly1, zf),
         (xf + e * reach, ly0, zf)],                            # lektas underside
        [(xf, ly1, zf), (xf + e * reach, ly1, zf),
         (xf + e * reach, ly1, lz1), (xf, ly1, lz1)],           # lektas forside
    ]
    for quad in faces:
        page.poly([P(q) for q in quad], fill="#efefef", stroke=GREY,
                  width=W_RULE * 0.8)
    page.polylines(remap(clip_to_circle(prior_lines, src, src_r),
                         src, src_r, dst_c, dst_r),
                   GREY, W_PRIOR * k)
    page.polylines(remap(clip_to_circle(new_only, src, src_r),
                         src, src_r, dst_c, dst_r), INK, W_NEW * k * 0.8)

    # THE BRACKET ITSELF, off the model's own record - the same corners
    # generate_loftbed.py built the solid from. Nothing here is a second
    # drawing of a bracket somebody once measured: if the model turns it over,
    # this turns over with it.
    plate = next((q["spec"] for q in cands_m
                  if q["spec"]["kind"] == "plate"
                  and q["spec"]["pa"] is pa and q["spec"]["pb"] is pb), None)
    if plate is None:
        plate = next(q["spec"] for q in cands_m if q["spec"]["kind"] == "plate")
    for quad in plate_quads(plate):
        page.poly([P(q) for q in quad], fill="#9a9a9a", stroke=INK,
                  width=W_RULE * 0.9)
    # ...and the screws through it, at their own length and their own angle.
    for q in cands_m:
        g = q["spec"]
        if g["kind"] != "screw":
            continue
        head3 = g["anchor"]
        tip3 = tuple(c + d * g["length"]
                     for c, d in zip(head3, g["direction"]))
        h2, t2 = P(head3), P(tip3)
        ux, uy, ln = _unit2(h2, t2)
        if ln < 1e-6:
            page.dot(h2, 4.0 * k)
            continue
        w2 = g["d"] * k * 0.5
        hd = w2 * 1.9
        page.poly([(h2[0] - uy * hd, h2[1] + ux * hd),
                   (h2[0] + ux * hd * 0.5 - uy * w2,
                    h2[1] + uy * hd * 0.5 + ux * w2),
                   (t2[0] - uy * w2 * 0.15, t2[1] + ux * w2 * 0.15),
                   (t2[0] + uy * w2 * 0.15, t2[1] - ux * w2 * 0.15),
                   (h2[0] + ux * hd * 0.5 + uy * w2,
                    h2[1] + uy * hd * 0.5 - ux * w2),
                   (h2[0] + uy * hd, h2[1] - ux * hd)],
                  fill="#ffffff", stroke=INK, width=W_RULE * 0.8)
        a_len = dst_r * 0.22
        page.arrow((h2[0] - ux * a_len, h2[1] - uy * a_len), h2,
                   INK, W_MARK * 0.55, a_len * 0.36)
    page.clip_end()
    # The caption goes wherever there is paper: under the circle, over it, or
    # - if the circle sits in a corner - just inside its lower edge.
    if dst_c[1] - dst_r - 66 >= page.y0 + 12:
        ty = dst_c[1] - dst_r - 62
    elif dst_c[1] + dst_r + 62 <= page.y1 - 12:
        ty = dst_c[1] + dst_r + 24
    else:
        ty = dst_c[1] - dst_r + 34
    page.text((dst_c[0], ty), plate["name"].split(" varmforsinket")[0].upper(),
              44, anchor="middle", weight="bold")


def info_panel(page, box, G):
    """The mattress panel. Every number is read off the model.

    IKEA writes a maximum here. This bed needs BOTH bounds, and they pull
    opposite ways off the same two fixed heights - the slat top the mattress
    lies on, and the guard above it:

        too THIN  and the gap under the lower guard band opens past the
                  EN 747 entrapment limit. The arrow is UNDER the mattress.
        too THICK and the barrier standing above the sleeper falls under the
                  EN 747 minimum. The arrow is ABOVE it.

    So the panel draws the mattress at its modelled thickness with a
    constraint arrow on each side, and prints the range rather than a number.
    """
    x, y, w, h = box
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=W_RULE)
    page.circle((x + 40, y + h - 40), 22, width=W_RULE)
    page.text((x + 40, y + h - 50), "i", 46, anchor="middle", weight="bold")
    page.text((x + 78, y + h - 52), "MADRASS", 44, weight="bold")
    page.text((x + 22, y + h - 112), "STANDARD 80 x 200 cm", 40)
    page.text((x + 22, y + h - 166),
              f"TYKKELSE {G.MATTRESS_H_MIN}-{G.MATTRESS_H_MAX} mm", 44,
              weight="bold")

    # Section: slat top, mattress, the opening, both guard bands, post top.
    top = y + h - 208
    bot = y + 30
    z0, z1 = G.SLAT_Z1, G.GUARD_TOP
    k = (top - bot) / (z1 - z0)
    sx, sw = x + 26, w - 52

    def zy(z):
        return bot + (z - z0) * k

    page.line((sx, zy(G.SLAT_Z1)), (sx + sw, zy(G.SLAT_Z1)), INK, W_RULE)
    page.rect(sx, zy(G.MATTRESS_Z0), sw * 0.44,
              (G.MATTRESS_Z1 - G.MATTRESS_Z0) * k, fill="none", width=W_RULE)
    for zb in G.GUARD_BAND_Z0:
        page.rect(sx, zy(zb), sw * 0.44, G.GUARD_W * k, fill="none",
                  width=W_RULE)
    for i, zb in enumerate(G.GUARD_BAND_Z0):
        page.text((sx + 14, zy(zb) + G.GUARD_W * k / 2 - 10),
                  "REKKVERK" if i == 0 else "REKKVERK 2", 26)
    page.text((sx + 14, zy(G.MATTRESS_Z0)
               + (G.MATTRESS_Z1 - G.MATTRESS_Z0) * k / 2 - 10),
              "MADRASS", 26)

    def between(ax, za, zb, txt, limit):
        ya, yb = zy(za), zy(zb)
        page.arrow((ax, ya + 4), (ax, yb), INK, W_LEAD, 12)
        page.arrow((ax, yb - 4), (ax, ya), INK, W_LEAD, 12)
        page.text((ax + 12, (ya + yb) / 2 - 11), txt, 32, weight="bold")
        page.text((ax + 12, (ya + yb) / 2 - 44), limit, 24)

    # MIN side: the gap under the lower band. MAX side: the barrier above the
    # mattress, measured to the top of the guard.
    gap = G.GUARD_BAND_Z0[0] - G.MATTRESS_Z1
    barrier = G.GUARD_TOP - G.MATTRESS_Z1
    between(sx + sw * 0.51, G.MATTRESS_Z1, G.GUARD_BAND_Z0[0],
            f"{int(round(gap))}", f"maks {G.MAX_GUARD_OPENING}")
    between(sx + sw * 0.78, G.MATTRESS_Z1, G.GUARD_TOP,
            f"{int(round(barrier))}", f"min {G.MIN_GUARD_OVER_MATTRESS}")


def step_sections(marks):
    """One section per joint family in the step, biggest joint first.

    A step with three families - the ladder has three - gets three little
    sections, each labelled with the badge letters of what is driven in it.
    One section per KIND of joint, not per instance: the two ends of a bench
    rail are the same joint mirrored and want one drawing, but J4's two rows -
    a 5x60 down into the block and a 6x120 sideways into the rung end - are
    two different things and want two.
    """
    best = {}
    for m in marks:
        f = m["spec"]
        if f["contact"] is None:              # a wall fixing: nothing to cut
            continue
        key = (f["jid"], id(f["crow"]), tuple(f["contact"][0]))
        best.setdefault(key, []).append(m)
    by_joint = {}
    for key, ms in best.items():
        jkey = (key[0], key[1])
        cur = by_joint.get(jkey)
        if cur is None or ms[0]["area"] > cur[0]["area"]:
            by_joint[jkey] = ms
    out = []
    for _jkey, ms in sorted(by_joint.items(), key=lambda kv: -kv[1][0]["area"]):
        letters = []
        for m in ms:
            if m["letter"] and m["letter"] not in letters:
                letters.append(m["letter"])
        out.append(([m["spec"] for m in ms], "".join(sorted(letters))))
    return out[:4]


def check_coverage(st, kept, fasteners, families):
    """The hard check: everything the step's tables list is on the drawing.

    Two ways a page can lie, and both are build failures. It can show fewer
    screws than the step drives - the Baerekloss that was listed in the parts
    table and never once shown being fastened - and it can show fewer of a
    kind than the fastener table counts. So: every part family in the step's
    own parts table must carry at least one marker, and the marker counts must
    add up to the table's counts, kind for kind.
    """
    shown = {}
    for m in kept:
        shown[m["name"]] = shown.get(m["name"], 0) + m["per"]
    for name, qty, _svg, _letter in fasteners:
        got = shown.get(name, 0)
        assert got == qty, (
            f"steg {st['n']}: tegningen viser {got} x '{name}', "
            f"tabellen sier {qty}. Festepunktene og beslaglista er ikke "
            f"enige - se JOINT_CONTACTS i tools/render_lineart.py.")
    covered = set()
    for m in kept:
        for part in mark_parts(m):
            covered.add(families.get(part.label))
    want = {families[l] for l in st["labels"] if l in families}
    missing = sorted(f for f in want - covered if f)
    assert not missing, (
        f"steg {st['n']}: {missing} står i deletabellen, men ingen "
        f"festing av dem er tegnet. Legg leddet inn i JOINT_CONTACTS.")


def render_step(G, view, st, uni, placed, out_dir, width, page_box, glyph_dir,
                fasteners, families, centre):
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
    # The new part is drawn whole - but the stretch of it that something
    # already standing hides is drawn DASHED, because that is the only thing
    # on the page that says which side of the frame it goes on. The front side
    # rail passes BEHIND the front posts, and a solid line across the post
    # says the opposite.
    page.polylines(new_only, INK, W_NEW * 0.45, dash="26 20")
    page.polylines(combined.get("new", []), INK, W_NEW)

    # No step number in the drawing: the page header already carries it, and
    # two of them is one too many.

    # Where the fasteners go, in the drawing's own frame. A step that drives
    # only one kind needs no letters: the glyph in its table is already the
    # whole answer.
    is_mattress = any(p.label.startswith("Mattress") for p in new)
    letters = {name: letter for name, _q, _s, letter in fasteners if letter}
    names = [name for name, _q, _s, _l in fasteners]

    marks = [] if is_mattress else step_marks(G, st, letters, view)

    sections = step_sections(marks)
    if is_mattress:
        # The information panel carries a section as well as three lines of
        # text, so it needs more room than a fastener list does.
        inset_w, inset_h = page.w * 0.32, page.h * 0.36
    else:
        inset_w, inset_h = inset_layout(page, len(sections),
                                        len(fasteners[:4]))[:2]
    bx, by = emptiest_corner(combined.get("prior", []) + new_only,
                             page, inset_w, inset_h, marks)
    box = (bx, by, inset_w, inset_h)
    # Both of these are measured on the SHORT side of the page, so a step
    # that gets a tall page of its own - the ladder - does not get arrows and
    # spacings scaled off a height it never uses across.
    gap = min(page.w, page.h) * 0.034
    keep = choose_marks(marks, gap, inset=box)
    keep = restore_orphans(keep, families,
                           {families[l] for l in st["labels"]
                            if l in families})

    if is_mattress:
        info_panel(page, (bx, by, inset_w, inset_h), G)
    elif fasteners:
        draw_inset(page, box, sections, fasteners, glyph_dir, letters)
    if not is_mattress:
        check_coverage(st, keep, fasteners, families)

    # THE FASTENERS THEMSELVES. Two styles, and which one a page gets is
    # decided by how many marks survive the merge: a step that drives eight
    # screws is clearer with all eight pulled out of their holes, and a step
    # that drives twenty-eight - the slat fields - would be a forest. Those
    # get the in-situ phantom instead, which says the same thing quietly.
    style = "eksplodert" if len(keep) <= EXPLODE_MAX else "in situ"
    pull = min(page.w, page.h) * EXPLODE_FRAC
    stacks = {}
    for m in sorted(keep, key=lambda q: (-q["p2"][1], q["p2"][0])):
        f = m["spec"]
        key = (round(m["p2"][0] / 6.0), round(m["p2"][1] / 6.0),
               tuple(round(c, 3) for c in f["direction"]))
        stack = stacks.get(key, 0)
        stacks[key] = stack + 1
        if style == "eksplodert":
            # Backed out along its own axis in MODEL space, so the pulled
            # fastener stays on the line it travels no matter where the
            # camera stands. The 3-D distance that lands `pull` page units
            # clear is worked out off the projection itself.
            dx, dy = view.dir_xy(f["direction"])
            nrm = math.hypot(dx, dy)
            back = pull / nrm if nrm > 0.12 else pull * 8
            shift = tuple(-c * back for c in f["direction"])
            hole = view.xy(f["anchor"])
            head, tip = draw_fastener(page, view, m, style, shift, stack)
            # Dotted, not dashed and not an arrow: this line is a fastener's
            # travel, and the page keeps that convention to itself.
            page.line(tip, hole, GREY, W_PHANTOM, dash=DASH_INSERT)
            page.dot(hole, 6.0, colour=INK)
            # The caption goes behind the HEAD, i.e. further from the hole -
            # the one direction that cannot land on the fastener itself.
            label_at, label_dir = head, (
                (dx / nrm, dy / nrm) if nrm > 1e-6 else (0.0, -1.0))
        else:
            draw_fastener(page, view, m, style, stack=stack)
            label_at = m["p2"]
            label_dir = (0.0, -1.0)
        mark_label(page, label_at, label_dir, m["letter"], m["per"], box)

    # Leaders from the inset to the joints, or one magnifier when there is
    # only a location or two to point at.
    if keep and not is_mattress and fasteners:
        anchor = (bx + inset_w / 2, by + inset_h / 2)
        if len({(round(m["p2"][0]), round(m["p2"][1])) for m in keep}) <= 2:
            src = keep[0]["p2"]
            src_r = max(page.w, page.h) * 0.055
            dst_r = inset_w * 0.30
            dst_c = (bx + inset_w / 2, by + inset_h + dst_r + 60)
            if dst_c[1] + dst_r > y1 - 20:
                dst_c = (bx + inset_w / 2, by - dst_r - 60)
            magnifier(page, src, dst_c, dst_r, src_r, new_only,
                      combined.get("prior", []))
        else:
            # One leader per joint would bury the drawing, so the inset points
            # at the nearest few and the markers carry the rest.
            near = sorted(keep, key=lambda kp: (kp["p2"][0] - anchor[0]) ** 2
                          + (kp["p2"][1] - anchor[1]) ** 2)[:4]
            for m in near:
                page.line(_edge_of_box(anchor, m["p2"], bx, by, inset_w,
                                       inset_h),
                          m["p2"], GREY, W_LEAD, dash="16 14")

    # A bracket nobody can place from the overview gets a magnifier of its
    # own: the 40x40x40 under the table ledger, drawn where it sits.
    if any(m["jid"] == "J12" for m in keep):
        ledger_bracket_detail(page, view, keep, new_only,
                              combined.get("prior", []), box)

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


def crop_to_subject(view, page_box, new_parts):
    """A tighter page for a step whose subject is a narrow thing in a wide bed.

    Every page is cut from the FINISHED bed, so nothing jumps between drawings
    - and that is right for the eleven steps that build across the whole 1990
    mm of it. The ladder is not one of them: it is 416 mm wide and 1700 tall,
    and on a bed-wide page it comes out as a sliver with four badges fighting
    for the 320 mm between its stiles. So a step whose new parts fill less
    than a third of the page gets a page of its own, cut round them - the
    scale goes up, the badges stay the size they are, and the grey frame
    behind simply falls outside the viewBox.
    """
    if not new_parts:
        return page_box
    x0, y0, x1, y1 = page_box
    bx0, by0, bx1, by1 = bounds(project(view, [("s", comp(new_parts))])["s"])
    if (bx1 - bx0) > (x1 - x0) * 0.34:
        return page_box
    mx = (bx1 - bx0) * 1.05                # room for arrows and badges
    my = (by1 - by0) * 0.06
    return (bx0 - mx, by0 - my, bx1 + mx, by1 + my)


def part_families(G):
    """label -> the cut-list line it is counted on, i.e. the row of the step's
    own parts table. Straight out of tools/gen_doc_tables.py, so the drawing
    and the table cannot disagree about what a part IS."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import gen_doc_tables
    return {label: name
            for label, (name, _sec, _len) in
            gen_doc_tables.part_cut_keys(G).items()}


def render_all(G, data, out_dir, width, only):
    uni = universe(G)
    box = full_bed(G).bounding_box()
    look_at = box.center()
    centre = (look_at.X, look_at.Y, look_at.Z)
    families = part_families(G)
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
        if not st["image"]:
            placed += st["labels"]
            continue
        if n == 0:
            # The cutting page is not a view of the bed at all.
            if only is None or n == only:
                import render_cutpage
                made.append(render_cutpage.render(G, out_dir, width,
                                                  glyph_dir))
            placed += st["labels"]
            continue
        key = tuple(st["camera"][:2])
        if only is None or n == only:
            st = dict(st)
            box = crop_to_subject(views[key], pages[key],
                                  [uni[l] for l in st["highlight"]])
            if n == 2:
                # The one step that changes the workpiece's orientation.
                st["thumbnails"] = [uni[l] for l in placed]
            if n == 10:
                import render_panel
                png = render_panel.render(G, views[key], st, uni, placed,
                                          out_dir, width, pages[key],
                                          glyph_dir,
                                          step_fastener_glyphs(st, glyph_dir),
                                          families, centre)
            else:
                png = render_step(G, views[key], st, uni, placed, out_dir,
                                  width, box, glyph_dir,
                                  step_fastener_glyphs(st, glyph_dir),
                                  families, centre)
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
