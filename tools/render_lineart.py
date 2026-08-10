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
  * nothing runs from the inset to the fastening points. The badge letter is
    already the tie between a mark and its row in the panel, and it ties ALL
    of them rather than the four that happened to be nearest. A step with only
    one or two locations to point at gets a circular magnifier of the real
    line work there instead - that one carries information, so it keeps its
    short leader.
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
if os.path.join(ROOT, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "tools"))

import layout                                              # noqa: E402

STEP_JSON = os.path.join(ROOT, "docs", "generated", "byggesteg.json")

# ---------------------------------------------------------------------------
# PEN
# ---------------------------------------------------------------------------
# All sizes are in model millimetres, which is what the SVG user unit is, so
# they scale with the drawing and not with the output resolution - and they
# are not typed in one at a time any more. `T` is the theme from
# tools/layout.py: every width, radius, margin and point size on a page is a
# multiple of ONE pen, and the pen is the SUBJECT's own bounding-box diagonal
# over 400. Draw a bed twice the size and the whole page follows it.
#
# It is deliberately empty until use_model() hands it the subject, so a size
# read before the model is known fails loudly instead of quietly.
T = layout.THEME


def use_model(G):
    """Fix the pen from the subject: the finished bed's own diagonal.

    Called by every entry point into this file - render_all(), render_hero()
    and tools/render_cutpage.py's own __main__ - because the pen is a property
    of the thing being drawn, not of whoever asked for a drawing.
    """
    if T.pen is None:
        T.set_subject(layout.subject_diag(full_bed(G)))
    return T


GREY = "#9a9a9a"
INK = "#111111"

# Arrows are for WOOD now - the before/after thumbnails, the dimension marks
# on the mattress panel, the screwdriver stub in a section, and the exploded
# panel page. A fastener is drawn as itself; see DRAWING A FASTENER below.
# Above this many marks on one page the exploded style stops helping - the
# slat fields drive one screw per slat end and there are twenty-eight of them,
# and twenty-eight screws hanging in the air over a bed is a hedge, not an
# instruction. Those pages get the in-situ phantom instead.
EXPLODE_MAX = 18

FONT = "Helvetica, Arial, sans-serif"


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
        out.append(dict(p3=p3, p2=view.xy(p3), a2=view.xy(f["anchor"]),
                        dir3=d3, per=1, jid=f["jid"],
                        name=f["name"], letter=letters.get(f["name"]),
                        area=area, spec=f,
                        # The body as the page would draw it sitting in its
                        # hole - what R2 asks its question of.
                        body=body_capsule(view, f)))
    return out


def mark_owner(mark):
    """A stable name for the thing a mark is about.

    It has to survive being written down in an occupancy field and compared
    later, and it has to be the SAME from run to run - so it is built out of
    the joint, the fastener's name and where on the page it landed, not out of
    an id() that a rerun would hand out differently.
    """
    return (mark["jid"], mark["name"],
            round(mark["p2"][0], 3), round(mark["p2"][1], 3))


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
DASH_PHANTOM = "15 11"
DASH_INSERT = "4 13"           # dotted: fasteners only
# How much fatter than life a drawn fastener is. ONE knob, and it lives with
# the rest of the pen set in tools/layout.py - see the note there for why it
# is 3.0 and not the 2.2 the first drawings were made with.
SCREW_FATTEN = layout.SCREW_FATTEN
# No fastener is drawn shorter than this fraction of its true length. Straight
# foreshortening is information - a screw driven into the page SHOULD look
# short - but past a point it stops being a screw and becomes a dot, and the
# reader loses the one number the drawing has to get right.
FORESHORTEN_FLOOR = 0.72
# Below this much of its true length on the page a screw has no axis left to
# draw and becomes a ringed dot. One number, used by the shape function and by
# the explosion alike: a fastener that is a dot is not backed out of anything,
# because a dot cannot show which way it came.
AXIS_ON_PAGE = FORESHORTEN_FLOOR * 0.5
# HOW FAR OUT AN EXPLODED FASTENER SITS - and it is not one rule, because a
# screw and a bracket are not the same kind of object.
#
# A SCREW comes out STRICTLY ALONG ITS OWN DRIVE AXIS. Its drawn body, the
# dotted insertion line and the hole are one straight line: the line is a pure
# extension of the screw, and the screw is a pure extension of the line. That
# is the whole claim the picture makes - "this one goes in HERE, this way" -
# and nothing is allowed to break it. Not a sideways lift to find white paper,
# not a stack offset: the moment the body steps off its own line, the reader
# stops reading a joint and starts matching a drawing to a dotted stub, which
# is exactly the work the drawing exists to save. Where an exploded screw
# collides with line work, the answer is a longer hop back down the same axis,
# or letting it lie over GHOST line work - never a sidestep.
#
#   EXPLODE_FRAC       the air between point and hole, on top of the screw's
#                      own drawn length. Just enough to read as "not in yet".
#
# Two screws whose tips land on the same page point - the camera looking down
# their shared axis - are separated by QUEUEING them, each one a body further
# back along that same axis. Both of them stay on the line.
#
# A BRACKET has no drive axis of its own, but it is not free either: it comes
# off BACKWARDS ALONG THE SCREWS THAT HOLD IT, and that direction is a fact
# about the joint rather than about the paper. See R1 under WHICH WAY A
# BRACKET COMES OFF: the float is the negated resultant of its own screws'
# drive vectors, and the only thing left free is how FAR out. Its own screws
# then explode along their axes from where the BRACKET ended up, and two
# screws entering from each side reads straight off the main drawing - which
# is why those brackets no longer need a magnifier to be understood.
#
# Both are fractions of the page's short side, so a cropped page gets the same
# picture at its own scale.
EXPLODE_FRAC = 0.038
EXPLODE_PLATE_FRAC = 0.055
STACK_STEP = 0.6               # coaxial screws, as a fraction of the head


def fill_code(letter):
    """The fill a badge letter carries, or None where the page has no letters.

    THE CODE IS THE LETTER, one more time, in a form the reader does not have
    to read. It is defined in tools/gen_glyphs.py - the file that draws the
    badge and the table glyph - so the drawing, the panel and the table cannot
    end up coding the same letter three different ways (PRAKSIS section 1).
    """
    import gen_glyphs
    return gen_glyphs.fill_code(letter)


def _unit2(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return (dx / n, dy / n, n) if n > 1e-9 else (0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# R2 - WHAT COUNTS AS TWO BODIES IN ONE PLACE
# ---------------------------------------------------------------------------
# The old rule was a distance: two marks of the same kind within `gap` of each
# other became one mark carrying "2x". That is a guess about legibility, and
# it merged things that are simply NEAR - on step 1 the two A screws it left
# behind are 50 mm apart and never touch.
#
# The honest question is not how far apart two fasteners are, it is whether
# the two BODIES the page draws end up on top of each other. Two silhouettes
# drawn over one another are a lie whatever the table says, and two that do
# not touch are two things the reader can count. So:
#
#   OVERLAPPING drawn bodies  ->  one mark, carrying the count
#   bodies that do not touch  ->  two marks, and if the drawing crowds them
#                                 they separate ALONG THEIR OWN AXES, which is
#                                 the one move an exploded fastener is allowed
#
# A drawn screw is a capsule - that is exactly what the silhouette is, a
# rectangle with a point on one end - so "do these two overlap" is the
# distance between their two axis segments against the sum of their half
# widths. It is measured on the page, in the projection, which is where the
# overlap either happens or does not.
#
# Merging never crosses a JOINT. PRAKSIS section 4 gives the case: on step 3
# the end beam's two 6x90 and the bearing block's one land in the same corner,
# and "3x" there would send the builder to the wrong holes. The flag is here
# so that the rule is a line to turn rather than an assumption to find, but it
# is OFF and the drawings are drawn with it off.
MERGE_ACROSS_JOINTS = False
# How many body-lengths back an exploded fastener will queue before it accepts
# the overlap. Four is already a long way out on a page this size.
QUEUE_MAX = 4


def _seg_seg_dist(a0, a1, b0, b1):
    """Distance between two segments on the page, 0 where they cross."""
    def cross(o, p, q):
        return ((p[0] - o[0]) * (q[1] - o[1])
                - (p[1] - o[1]) * (q[0] - o[0]))

    d1, d2 = cross(b0, b1, a0), cross(b0, b1, a1)
    d3, d4 = cross(a0, a1, b0), cross(a0, a1, b1)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(layout._seg_dist(a0, b0, b1), layout._seg_dist(a1, b0, b1),
               layout._seg_dist(b0, a0, a1), layout._seg_dist(b1, a0, a1))


def body_capsule(view, f, shift=(0.0, 0.0, 0.0), page_off=(0.0, 0.0)):
    """The drawn body as (end, end, half-width) on the page.

    For a screw that is what the silhouette IS. For a bracket - which has no
    axis - it is the disc round its projected corners, which is close enough
    for a question no bracket has ever had to answer: a merge only ever
    considers two fasteners with the SAME NAME, and no bracket shares a name
    with a screw.
    """
    anchor = tuple(a + s for a, s in zip(f["anchor"], shift))
    ox, oy = page_off
    if f["kind"] == "plate":
        pts = plate_page_points(view, dict(f, anchor=anchor), page_off)
        c = _centroid(pts)
        r = max(math.hypot(p[0] - c[0], p[1] - c[1]) for p in pts)
        return (c, c, r)
    tip = tuple(a + d * f["length"]
                for a, d in zip(anchor, f["direction"]))
    p0 = (view.xy(anchor)[0] + ox, view.xy(anchor)[1] + oy)
    p1 = (view.xy(tip)[0] + ox, view.xy(tip)[1] + oy)
    r = f["d"] * SCREW_FATTEN * 0.95
    if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < f["length"] * AXIS_ON_PAGE:
        # Head on: the page draws a ringed dot, so that is the body.
        return (p0, p0, T.RING_R)
    return (p0, p1, r)


def capsules_overlap(a, b, slack=0.0):
    """Do two drawn bodies actually share paper?"""
    return _seg_seg_dist(a[0], a[1], b[0], b[1]) < a[2] + b[2] + slack


def mark_clusters(marks, slack):
    """How many PLACES a set of marks is at, not how many marks it is.

    Two screws 30 mm apart are two marks now - R2 only merges bodies that
    actually overlap - but they are still one place on the page, and some
    decisions are about places: whether a step has few enough locations to
    point at that a magnifier of one of them is worth the paper. `slack` is
    how far apart two bodies have to be to count as two places.
    """
    groups = []
    for m in marks:
        hit = [g for g in groups
               if any(capsules_overlap(m["body"], q["body"], slack)
                      for q in g)]
        if not hit:
            groups.append([m])
            continue
        first = hit[0]
        first.append(m)
        for g in hit[1:]:
            first += g
            groups.remove(g)
    return groups


# ---------------------------------------------------------------------------
# R1 - WHICH WAY A BRACKET COMES OFF
# ---------------------------------------------------------------------------
# A screw explodes along its own drive axis; that direction is given and this
# file never chooses it. A BRACKET has no drive axis of its own, and the way
# it used to be floated - try all four diagonals, keep the one with the most
# white paper under it - was a guess about the PAPER dressed up as a drawing
# convention. It got J12 exactly backwards: the angle bracket under the table
# ledger floated up and to the left, which is INTO the ledger it is screwed to
# the underside of.
#
# The direction is not a matter of taste, and the model already knows it. A
# bracket is held by its screws, so the only way it comes off is BACKWARDS
# ALONG THEM: negate the resultant of the drive vectors of every fastener
# that passes through it, project that, and float it that way. J12's two
# screws go (-1,0,0) into the post and (0,0,+1) up into the ledger, so the
# bracket leaves at (+1,0,-1)/root 2 - out from the post and DOWN, away from
# everything it touches. That is disassembly, and it is what an exploded view
# is a picture of.
def plate_screws(G, plate):
    """Every fastener that passes THROUGH one bracket, straight off the model.

    Taken from the model rather than from the page's surviving marks on
    purpose: a bracket comes off the way it is held, and that is true whether
    or not this page happens to have merged two of its screws into one badge
    or cropped the far end of the bed away.
    """
    return [f for f in G.FASTENER_SPECS
            if f["kind"] != "plate" and f["jid"] == plate["jid"]
            and screw_on_plate(plate, f)]


def disassembly_dir(view, plate, screws):
    """The unit direction a bracket floats in, in the drawing's own frame.

    Three sources, in order, and the second and third are only ever reached by
    a camera that has flattened the first:

      1. minus the resultant of the screws' drive vectors - the disassembly
         direction proper;
      2. failing that (no screws, or drives that cancel exactly), out along
         the bracket's own normal, i.e. off the face it lies against;
      3. failing even that - the direction points straight at the reader and
         has no length on the page - straight down the page, which is the one
         direction that cannot be mistaken for a member of this bed.
    """
    v = tuple(-sum(f["direction"][j] for f in screws) for j in range(3))
    if math.hypot(*v) < 1e-9:
        v = tuple(-c for c in plate["direction"])
    for cand in (v, tuple(-c for c in plate["direction"])):
        dx, dy = view.dir_xy(cand)
        n = math.hypot(dx, dy)
        if n > 1e-6:
            return (dx / n, dy / n)
    return (0.0, -1.0)


def plate_page_points(view, plate, off=(0.0, 0.0)):
    """The bracket's drawn corners on the page - what the ink actually is."""
    return [(view.xy(p)[0] + off[0], view.xy(p)[1] + off[1])
            for q in plate_quads(plate) for p in q]


def _centroid(pts):
    return (sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts))


def float_plate(occ, view, plate, screws, hop):
    """Where an exploded bracket goes: R1 for the direction, the field for how
    far. The DIRECTION is given - the caller does not get a vote and neither
    does the paper - so the only thing left to choose is the distance, and
    that is a single run of layout.place() over candidates strung out along
    that one line. A bracket that finds no room simply goes further out; it
    never leans, for the same reason a screw never does.
    """
    ux, uy = disassembly_dir(view, plate, screws)
    pts = plate_page_points(view, plate)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    home = _centroid(pts)
    foot = (max(xs) - min(xs), max(ys) - min(ys))
    cands = [(home[0] + ux * hop * k, home[1] + uy * hop * k)
             for k in (1.0, 1.4, 1.9, 2.5)]
    at = layout.place(cands, foot, occ, tether=home, pull=1.0 / (hop * 6.0))
    return (at[0] - home[0], at[1] - home[1])


def assert_float_direction(page, view, plate, want, jid):
    """The float is checked against the rule, measured off the INK.

    The drawn bracket's centroid is taken out of the page's own record of what
    it emitted - not out of the offset that was computed - and compared with
    the centroid the same bracket would have had sitting on its seat. A
    drawing that floats a bracket into the timber it hangs under does not get
    written.
    """
    drawn = [r for r in page.record
             if r["kind"] == "plate" and r["owner"] == id(plate)]
    assert len(drawn) == 1, (
        f"{jid}: beslaget ble tegnet {len(drawn)} ganger - regelen kan bare "
        f"sjekkes mot ett blekkspor")
    home = _centroid(plate_page_points(view, plate))
    moved = _centroid(drawn[0]["points"])
    step = (moved[0] - home[0], moved[1] - home[1])
    assert math.hypot(*step) > 1e-6, (
        f"{jid}: beslaget er tegnet oppa setet sitt - en eksplodert del som "
        f"ikke har flyttet seg forteller ingenting om hvordan den tas av")
    dev = _angle_between(step, want)
    assert dev is not None and dev < AXIS_TOL_DEG, (
        f"{jid}: beslaget flyter {dev:.2f} grader av demonteringsretningen "
        f"(minus resultanten av skruene som holder det) - se "
        f"disassembly_dir()")


def clear_back(occ, hole, u, body, base, step, want, tries=4):
    """How far back along its own axis an exploded screw has to sit.

    The one degree of freedom a screw is allowed - the same freedom, and the
    same only freedom, that float_plate() leaves a bracket. Its body is
    sampled at each candidate distance in the occupancy field and the SHORTEST
    hop that finds white paper for the whole of it wins; if none does, the
    roomiest one does. Only the BLACK line work counts - a screw is welcome to
    lie across the ghosted frame that is already standing, and on a page where
    everything is new there is nothing to be precious about anyway.

    What it never does is lean. A screw that cannot find room on its axis
    comes further out along it, and if there is still no room it stays where
    it is and overlaps: an exploded screw's whole job is to point at its hole,
    and a screw beside its own dotted line has stopped doing it.
    """
    best, best_d = None, base
    for k in range(tries):
        d = base + k * step
        room = min(occ.clearance((hole[0] - u[0] * (d - body * t),
                                  hole[1] - u[1] * (d - body * t)),
                                 want, tags=("dark",))
                   for t in (0.0, 0.35, 0.7, 1.0))
        if room >= want - 1e-9:
            return d
        if best is None or room > best + 1e-9:
            best, best_d = room, d
    return best_d


def screw_on_plate(plate, f):
    """Is this screw one of the ones that go THROUGH that bracket?

    The two flanges are the test, taken off the model's own record: the screw
    belongs to the bracket when its head sits on one of them. It matters
    because a bracket's screws travel with the bracket when it floats, and a
    screw that merely passes nearby does not - J10 drives four through the
    90x90x40 and one 5x70 toe screw past its edge into the same joint, and
    dragging that one along would put it in mid air.
    """
    C, n, r = plate["anchor"], plate["direction"], plate["run"]
    reach, w = plate["reach"], plate["width"]
    cross = [j for j in range(3) if abs(n[j]) < 0.5 and abs(r[j]) < 0.5]
    if not cross:
        return False
    d = [a - c for a, c in zip(f["anchor"], C)]
    if abs(d[cross[0]]) > w / 2 + 2.0:
        return False
    a_run = sum(d[j] * r[j] for j in range(3))
    a_n = -sum(d[j] * n[j] for j in range(3))
    tol = 3.0
    return ((-tol <= a_run <= reach + tol and abs(a_n) <= tol)
            or (-tol <= a_n <= reach + tol and abs(a_run) <= tol))


def screw_shape(view, anchor, direction, length, d, fatten=SCREW_FATTEN):
    """(outline, head-end, tip-end, unit) for one screw, on the page.

    `outline` is the silhouette in page coordinates: head, countersink,
    shank, point - laid out along the PROJECTED DRIVE AXIS and nowhere else.
    There is no upright screw glyph in this function and there must never be
    one: a 6x90 driven at 65 deg into a corner is drawn at 65 deg, because
    the angle is the instruction. The only licence taken is the diameter.

    `None` when the screw points straight at the reader and has no length on
    the page at all - the caller draws a ringed dot instead, which is the
    head-on convention and, being a circle, cannot point the wrong way.
    """
    tip3 = tuple(a + c * length for a, c in zip(anchor, direction))
    p0, p1 = view.xy(anchor), view.xy(tip3)
    ux, uy, L = _unit2(p0, p1)
    if L < length * AXIS_ON_PAGE:
        return None, p0, p1, (0.0, 0.0)
    L = max(L, length * FORESHORTEN_FLOOR)
    return (screw_outline(p0, (ux, uy), L, d, fatten), p0, p1, (ux, uy))


def screw_outline(p0, u, L, d, fatten=None):
    """The silhouette itself: head, countersink, shank, point.

    Split out of screw_shape() so that everything which draws a fastener draws
    the SAME seven points - the step page, and the fill-code contrast proof
    that has to show the reader exactly what the step page will show them.
    """
    fatten = SCREW_FATTEN if fatten is None else fatten
    ux, uy = u
    w = d * fatten
    hw, head_l, tip_l = w * 0.95, w * 0.30, w * 0.85

    def P(t, q):
        return (p0[0] + ux * t - uy * q, p0[1] + uy * t + ux * q)

    prof = [(0, hw), (head_l, w / 2), (L - tip_l, w / 2), (L, 0),
            (L - tip_l, -w / 2), (head_l, -w / 2), (0, -hw)]
    return [P(t, q) for t, q in prof]


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


def draw_fastener(page, view, m, style, shift=(0.0, 0.0, 0.0), stack=0,
                  page_off=(0.0, 0.0)):
    """One fastener on the page.

    Returns (head, tip, body). `body` is the axis of the silhouette that was
    ACTUALLY put on the paper - (head centre, point) off the drawn polygon,
    not off the numbers that went in - or None when nothing with an axis was
    drawn. assert_on_axis() checks the drawing against the model with it, so
    the check cannot be satisfied by the intention instead of the ink.

    `shift` moves it in MODEL space - that is the hop back down its own drive
    axis, and it has to be done in the model so the fastener stays on the line
    it really travels. It is the ONLY thing that moves an exploded screw.

    `page_off` moves the finished drawing bodily on the PAPER. It belongs to
    BRACKETS: a bracket has no axis to come out along, so it floats a little
    way off its seat instead, and the screws that go through it are handed the
    same offset so they explode from where the bracket ended up rather than
    from a seat it has left. A screw is never given a page offset of its own.

    `stack` pushes coaxial fasteners apart sideways, and it is for the IN SITU
    style only: two screws driven at the same page point are one screw as far
    as the reader can tell. The exploded style separates the same pair by
    queueing them along their shared axis, which the caller does in `shift`.
    """
    f = m["spec"]
    anchor = tuple(a + s for a, s in zip(f["anchor"], shift))
    ox, oy = page_off
    solid = style == "eksplodert"
    if f["kind"] == "plate":
        polys = []
        for q in plate_quads(dict(f, anchor=anchor)):
            pl = [view.xy(p) for p in q]
            polys.append([(x + ox, y + oy) for x, y in pl + [pl[0]]])
        if solid:
            for pl in polys:
                page.poly(pl, fill=INK, stroke=INK, width=T.W_RULE * 0.6)
        else:
            for pl in polys:
                page.poly(pl, fill="#ffffff", stroke=INK, width=T.W_RULE)
        page.record.append(dict(kind="plate", owner=id(f), jid=f["jid"],
                                name=f["name"],
                                cap=body_capsule(view, f, shift, page_off),
                                # without each ring's repeated closing point,
                                # so the recorded centroid is the polygon's
                                # and not a corner counted twice
                                points=[q for pl in polys for q in pl[:-1]]))
        seat = view.xy(anchor)
        run_end = view.xy(tuple(a + r * f["reach"]
                                for a, r in zip(anchor, f["run"])))
        return ((run_end[0] + ox, run_end[1] + oy),
                (seat[0] + ox, seat[1] + oy), None)

    outline, p0, p1, u = screw_shape(view, anchor, f["direction"],
                                     f["length"], f["d"])
    off = f["d"] * SCREW_FATTEN * STACK_STEP * stack if stack else 0.0
    nx, ny = (-u[1], u[0]) if u != (0.0, 0.0) else (1.0, 0.0)
    ox, oy = ox + nx * off, oy + ny * off
    if ox or oy:
        p0 = (p0[0] + ox, p0[1] + oy)
        p1 = (p1[0] + ox, p1[1] + oy)
        if outline:
            outline = [(x + ox, y + oy) for x, y in outline]
    # The fill code: the letter again, as a pattern in the silhouette itself,
    # so a reader looking at a corner with four fasteners in it can see WHICH
    # of the four a given screw is without finding and reading a 5 mm letter.
    paint = page.fill_paint(fill_code(m.get("letter")))
    if outline is None:
        # Straight at the reader: the drawing convention for an axis with no
        # length on the page is a ringed dot, and it is the same mark whether
        # the screw is in or out.
        page.circle(p0, T.RING_R, fill=paint, width=T.W_SCREW)
        page.dot(p0, T.RING_DOT_R)
        return p0, p0, None
    if solid:
        page.poly(outline, fill=paint, stroke=INK, width=T.W_SCREW)
    else:
        # In situ: the head is the only part anybody can see, so it is the
        # only part drawn solid. The rest is a phantom line.
        # The head is the only part anybody can see, so it is the only part
        # drawn solid. The rest is a phantom line - same ink, dashed, a shade
        # lighter in weight, which is the drawing convention for "this is
        # really there and it is inside the wood". The fill code goes UNDER the
        # phantom line, in the body it belongs to: the buried screw still has
        # to say which of the step's screws it is, and on a page like the
        # ladder's it is the only fastener drawing there is.
        if paint != "#ffffff":
            page.poly(outline, fill=paint, stroke="none", width=0)
        page.polylines([outline[1:len(outline) - 1] + [outline[1]]],
                       INK, T.W_SCREW * 0.62, dash=DASH_PHANTOM)
        page.poly(outline[:2] + outline[-2:], fill=INK, stroke=INK,
                  width=T.W_SCREW * 0.8)
    # Straight off the polygon: the two head corners are prof[0] and prof[-1],
    # so their midpoint is the head centre, and prof[3] is the point.
    body = (((outline[0][0] + outline[-1][0]) / 2,
             (outline[0][1] + outline[-1][1]) / 2), outline[3])
    page.record.append(dict(kind="screw", owner=id(f), jid=f["jid"],
                            name=f["name"], points=list(outline), axis=body,
                            cap=body_capsule(view, f, shift, page_off)))
    return p0, p1, body


AXIS_TOL_DEG = 1.0


def _angle_between(a, b):
    """Degrees between two page-space directions, or None if either is nil."""
    na, nb = math.hypot(*a), math.hypot(*b)
    if na < 1e-9 or nb < 1e-9:
        return None
    c = (a[0] * b[0] + a[1] * b[1]) / (na * nb)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def assert_on_axis(view, f, body, tip, entry, poff, jid):
    """The drawing is checked against the model, not against the intention.

    Three things have to be true of every exploded screw, and none of them is
    a matter of taste:

      1. the silhouette that was drawn points along the PROJECTED DRIVE AXIS.
         A 6x90 driven at 65 deg into a corner post is drawn at 65 deg. There
         is no upright glyph anywhere on a step drawing - the legend keeps
         canonical pictures, the drawing keeps the real projected solid.
      2. the dotted insertion line is COLLINEAR with it, not merely attached
         to it. Body and line are one straight run or the reader is matching
         shapes to stubs.
      3. that line ends exactly at the hole the model put there - offset with
         the bracket, when the screw goes through a bracket that has floated,
         because that is where the screw really enters.

    Measured off the ink: `body` comes back from the polygon draw_fastener
    actually emitted. A drawing that fails this does not get written.
    """
    want = view.dir_xy(f["direction"])
    seat = view.xy(f["anchor"])
    expect = (seat[0] + poff[0], seat[1] + poff[1])
    off = math.hypot(entry[0] - expect[0], entry[1] - expect[1])
    assert off < 1e-6, (
        f"{jid} {f['name']}: innstikkslinjen ender {off:.3f} mm fra hullet")
    if body is None:
        # No axis on the page, so nothing may have moved it off one: a ringed
        # dot sits ON its hole and says only "into the paper, here".
        gap = math.hypot(tip[0] - entry[0], tip[1] - entry[1])
        assert gap < 1e-6, (
            f"{jid} {f['name']}: rettvendt feste er flyttet {gap:.1f} mm "
            f"fra hullet uten en akse a flyttes langs")
        return
    axis = (body[1][0] - body[0][0], body[1][1] - body[0][1])
    dev = _angle_between(axis, want)
    assert dev is not None and dev < AXIS_TOL_DEG, (
        f"{jid} {f['name']}: tegnet kropp ligger {dev:.2f} grader av sin "
        f"egen drivakse")
    lead = (entry[0] - body[1][0], entry[1] - body[1][1])
    dev = _angle_between(lead, want)
    assert dev is None or dev < AXIS_TOL_DEG, (
        f"{jid} {f['name']}: innstikkslinjen ligger {dev:.2f} grader av "
        f"skruens akse")


def _apart(a, b, gap):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 > gap * gap


def choose_marks(marks, inset=None):
    """One mark per DRAWN ELEMENT, without losing a single screw. R2 and R4.

    Two fasteners of the same kind whose bodies land on top of each other are
    one mark, and it carries the count: the page can only draw one of the two
    silhouettes, so pretending there are two badges' worth of separate things
    there is a lie. Two whose bodies do NOT touch are two marks - even 40 mm
    apart, even in the same corner - because the reader can see two screws and
    has to be able to count them. Where that crowds the page the answer is not
    a merge, it is the move an exploded fastener is allowed anyway: further
    out along its own axis.

    It never merges across JOINTS (see MERGE_ACROSS_JOINTS). On step 3 the two
    6x90 into the end beam and the one into the bearing block under it land in
    the same corner, and "3x" there would tell the builder to put three screws
    in one place. Two joints, two marks, 2x and 1x.

    A mark that is crowded out does not disappear: its count is handed to the
    mark that crowded it, and that mark says "4x" instead of "2x". The same
    happens to a mark that lands under the inset panel, which is opaque and
    would hide the very line work the mark is about. render_step() then checks
    the totals against the step's own fastener table, so nothing can go
    missing silently.
    """
    kept = []
    deferred = []
    for m in sorted(marks, key=lambda q: (-q["area"], q["p2"])):
        if inset is not None and layout._in_rect(m["p2"], inset, 10.0):
            deferred.append(m)
            continue
        same = [q for q in kept
                if q["letter"] == m["letter"] and q["name"] == m["name"]
                and (MERGE_ACROSS_JOINTS or q["jid"] == m["jid"])
                and capsules_overlap(q["body"], m["body"])]
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
        # The fill-code patterns this page has actually used. Written into the
        # SVG's <defs> only if something asked for one, so a page with a single
        # kind of fastener - which has no letters and therefore no code - comes
        # out exactly as it did before.
        self.fills = set()
        # WHAT ACTUALLY WENT ON THE PAPER. Every drawn body, badge and label
        # registers itself here with its geometry and its owner, and the
        # asserts read THIS rather than the numbers that went in. It is the
        # same discipline assert_on_axis() has always kept - it takes the axis
        # out of the polygon that was emitted, not out of the intention - and
        # it is the only kind of check that cannot be satisfied by meaning
        # well. A rule the drawing breaks silently is not a rule.
        self.record = []

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

    def line(self, a, b, colour=INK, width=None, dash=None):
        width = T.W_LEAD if width is None else width
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(
            f'<path d="M{self._p(a)} L{self._p(b)}" fill="none" '
            f'stroke="{colour}" stroke-width="{_f(width)}" '
            f'stroke-linecap="round"{da}/>')

    def rect(self, x, y, w, h, fill="#ffffff", stroke=INK, width=None,
             rx=0):
        width = T.W_RULE if width is None else width
        self.body.append(
            f'<rect x="{_f(x)}" y="{_f(-(y + h))}" width="{_f(w)}" '
            f'height="{_f(h)}" rx="{_f(rx)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{_f(width)}"/>')

    def poly(self, pts, fill="#ffffff", stroke=INK, width=None):
        width = T.W_RULE if width is None else width
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

    def hatch(self, x, y, w, h, step, colour=INK, width=None):
        """45 deg lines inside a rectangle - the drawing convention for a
        piece of timber that has been cut through."""
        width = T.W_HATCH if width is None else width
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

    def circle(self, c, r, fill="none", stroke=INK, width=None):
        width = T.W_RULE if width is None else width
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

    def arrow(self, tail, head, colour=INK, width=None, head_len=None):
        """A plain open arrowhead - no markers, so it survives any renderer."""
        width = T.W_MARK if width is None else width
        head_len = T.BADGE_R * 1.05 if head_len is None else head_len
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

    def fill_paint(self, code):
        """The paint for one fill code, and the pattern registered with it.

        The page carries the <defs> because the pattern is in the PAGE's
        coordinate system: the code has to look the same on a screw driven
        left as on one driven down, so it is the paper that is hatched and not
        the screw.
        """
        if code is None:
            return "#ffffff"
        import gen_glyphs
        self.fills.add(code)
        return gen_glyphs.fill_paint(code)

    def _defs(self):
        if not self.fills - {"solid", "open"}:
            return ""
        import gen_glyphs
        return gen_glyphs.fill_defs(T.FILL_PERIOD, T.W_FILL) + "\n"

    def write(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="{_f(self.x0)} {_f(-self.y1)} {_f(self.w)} '
                f'{_f(self.h)}">')
        bg = (self._defs()
              + f'<rect x="{_f(self.x0)}" y="{_f(-self.y1)}" '
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
                         length=f["length"] * n, d=f["d"],
                         code=fill_code(letters.get(f["name"]))))

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
        page.rect(x0, y0, pw, ph, fill="#ffffff", width=T.W_RULE)
        page.hatch(x0, y0, pw, ph, max(min(pw, ph) / 4.2, T.HATCH_MIN))

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
                          fill=INK, stroke=INK, width=T.W_RULE * 0.6)
            continue
        # The screw itself, drawn along its own vector.
        vx, vy = sdr["v"]
        dx, dy = pt((sdr["a"][0] + vx, sdr["a"][1] + vy))
        ux, uy = dx - o[0], dy - o[1]
        n = math.hypot(ux, uy) or 1.0
        ux, uy = ux / n, uy / n
        L = sdr["length"] * scale
        d = max(sdr["d"] * scale, T.SEC_SCREW_MIN)
        head_d, head_l, tip_l = d * 1.9, d * 0.55, d * 1.7

        def P(t_, q, o=o, ux=ux, uy=uy):
            return (o[0] + ux * t_ - uy * q, o[1] + uy * t_ + ux * q)

        prof = [(0, head_d / 2), (head_l, d / 2), (L - tip_l, d / 2),
                (L, 0), (L - tip_l, -d / 2), (head_l, -d / 2),
                (0, -head_d / 2)]
        page.poly([P(t_, q) for t_, q in prof],
                  fill=page.fill_paint(sdr["code"]), stroke=INK,
                  width=T.W_RULE * 0.8)
        # A short arrow behind the head: the way the screwdriver goes.
        page.arrow(P(-L * 0.42, 0), P(-head_d * 0.55, 0), INK, T.W_MARK * 0.7,
                   head_d * 0.7)

    for i, ch in enumerate(letter_label):
        badge(page, (x + T.BADGE_R * 0.9 + i * T.BADGE_R * 1.7,
                     y + h - T.BADGE_R * 0.9), ch, T.BADGE_R * 0.82)


def badge(page, centre, letter, r=None):
    """One circled sans letter - the same mark the step table carries."""
    r = T.BADGE_R if r is None else r
    page.circle(centre, r, fill="#ffffff", stroke=INK, width=T.W_RULE)
    page.text((centre[0], centre[1] - r * 0.40), letter,
              r * 1.20, anchor="middle", weight="bold")
    page.record.append(dict(kind="badge", owner=None, letter=letter,
                            at=centre, r=r))


# R5 - A MARK BELONGS TO ITS OWN ELEMENT
# --------------------------------------
# What a caption costs, in the units layout.place() scores in. The numbers are
# the old hand-tuned cost function's, carried over so that the pages that were
# right stay right; what is NEW is the last one, and it is the rule that makes
# the whole thing more than a tidiness heuristic.
CAP_EDGE = 30.0        # hanging off the page
CAP_MARK = 18.0        # sitting on a fastener this caption does not name
CAP_BADGE = 3.0        # sitting on another caption
CAP_PANEL = 42.0       # sitting on the inset panel, which is opaque
CAP_TAGS = ("panel", "mark", "badge")


def mark_label(page, tail, direction, letter, count, occ=None, owner=None):
    """One fastener's caption, parked behind its tail.

    A mark carries at most one letter - each kind of fastener points at its
    own spot - and beside it the number of screws that mark stands for. "2x"
    is there because a marker is not always one screw: two 5x60 driven 30 mm
    apart into the same rekkverksbord end are one arrow at this scale, and the
    page has to say so.

    The natural place is straight back along the tail, and four things can
    spoil it: the page edge, the inset panel, another caption, and a fastener
    this caption does not name. The last is the worst of them by a distance,
    because a badge sitting on somebody else's screw does not merely crowd the
    page - it tells the builder to put the wrong screw there. Step 1 had
    exactly that: J9-B's screw points left, so "behind its head" is to the
    RIGHT, straight at J8-B's screw, and the page read
    "[skrue] A [skrue] A 2x" - two A marks with a foreign body between each
    badge and the screw it names.

    So the rule is not "avoid crowding". It is R5, and layout.place() enforces
    it: A CAPTION MAY NOT LAND NEARER A FOREIGN BODY THAN ITS OWN. Given that,
    the second A moves itself and nothing has to be merged, renamed or
    special-cased.
    """
    dx, dy = direction
    txt = f"{count}x" if count > 1 else ""
    w_txt = 0.0 if not txt else T.BADGE_R * (1.10 * len(txt))
    if letter:
        span = 2 * T.BADGE_R + (w_txt + 6 if txt else 0)
    else:
        span = w_txt
    base = span / 2 * abs(dx) + T.BADGE_R * abs(dy) + 14
    aside = span / 2 * abs(dy) + T.BADGE_R * abs(dx) + 14

    def spots(cx, cy):
        """Badge centre and text anchor for a caption centred on (cx, cy)."""
        left = cx - span / 2
        if letter:
            return (left + T.BADGE_R, cy), (left + 2 * T.BADGE_R + 6, cy)
        return None, (left, cy)

    # Straight back along the tail first, then progressively further; then to
    # either side. The ORDER is the preference, and layout.place() breaks ties
    # on it, so an uncrowded page still parks every caption behind its head.
    tries = [(tail[0] - dx * (base + k * T.BADGE_R * 1.7),
              tail[1] - dy * (base + k * T.BADGE_R * 1.7)) for k in range(5)]
    for s in (1, -1):
        for k in range(3):
            tries.append((tail[0] - dy * s * (aside + k * T.BADGE_R * 1.6)
                          - dx * k * T.BADGE_R * 0.8,
                          tail[1] + dx * s * (aside + k * T.BADGE_R * 1.6)
                          - dy * k * T.BADGE_R * 0.8))

    occ = layout.Occupancy() if occ is None else occ
    centre = layout.place(
        tries, (span, 2 * T.BADGE_R), occ,
        tether=tail,
        # Having stepped out of the way it steps no further than it had to: a
        # caption that has wandered is one the reader has to guess at.
        pull=1.0 / (T.BADGE_R * 8.0),
        owner=owner, tags=CAP_TAGS,
        bounds=(page.x0, page.y0, page.x1, page.y1),
        edge=T.BADGE_R + 8, edge_penalty=CAP_EDGE)
    b_at, t_at = spots(*centre)
    if b_at is None and not txt:
        # A single screw of the page's only kind carries neither a letter nor
        # a count, so there is nothing to park: the drawn body IS the whole
        # caption. Nothing is recorded either - Page.record is what went on
        # the paper, and this went nowhere.
        return None
    if b_at is not None:
        badge(page, b_at, letter)
        occ.add_point(b_at, radius=T.BADGE_R, weight=CAP_BADGE, owner=owner,
                      tag="badge")
    if txt:
        page.text((t_at[0], t_at[1] - T.BADGE_R * 0.42), txt, T.BADGE_R * 1.25,
                  weight="bold")
        at = (t_at[0] + w_txt / 2, t_at[1])
        occ.add_point(at, radius=T.BADGE_R, weight=CAP_BADGE, owner=owner,
                      tag="badge")
    page.record.append(dict(kind="label", owner=owner, letter=letter,
                            count=count, at=centre, tether=tail))
    return centre


def assert_bodies_apart(page):
    """R2, measured off the ink: no two drawn SCREWS share paper.

    Two silhouettes on top of each other are one silhouette as far as the
    reader is concerned, and a page that draws two there is claiming a count
    it cannot show. Either the two overlap - and then they are one mark
    carrying "2x", which is what choose_marks() decides - or they do not, and
    then the page has to have got them apart along their own axes. There is
    no third case, so this is an assert and not a preference.
    """
    caps = [r for r in page.record if r["kind"] == "screw" and r.get("cap")]
    for i, a in enumerate(caps):
        for b in caps[i + 1:]:
            assert not capsules_overlap(a["cap"], b["cap"]), (
                f"{a['jid']} {a['name']} og {b['jid']} {b['name']} er tegnet "
                f"oppå hverandre - to kropper på samme papir er ett merke, "
                f"ikke to. Se choose_marks() (R2) og køen langs egen akse")


def assert_marks_own_element(page, occ):
    """R5, measured off the ink: no caption is nearer somebody else's body.

    The badges are read back out of the page's own record - where they LANDED,
    not where they were aimed - and each one is asked the only question that
    matters about it: is the nearest drawn fastener the one you name? A page
    where it is not does not get written, because a badge beside the wrong
    screw is not a crowded drawing, it is a wrong instruction.
    """
    for r in page.record:
        if r["kind"] != "label" or r["owner"] is None:
            continue
        mine, _who = occ.nearest(r["at"], owner=r["owner"], foreign=False)
        theirs, who = occ.nearest(r["at"], owner=r["owner"], foreign=True)
        if mine is None or theirs is None:
            continue
        assert mine <= theirs + 1e-6, (
            f"merket {r['letter'] or '(uten bokstav)'} for {r['owner'][0]} "
            f"ligger {mine:.0f} mm fra sitt eget feste og {theirs:.0f} mm fra "
            f"{who[0]} sitt - et merke skal aldri lande nærmere en fremmed "
            f"kropp enn sin egen (R5)")


# The inset panel is the same shape on every page: the same fraction of the
# page's width, the same fastener-row height, the same glyph scale. A step
# with one fastener therefore gets a SHORTER panel, never a smaller one - the
# rows do not stretch to fill it and the glyphs do not shrink to fit it.
INSET_W_FRAC = 0.345          # of the page width
INSET_ROW_FRAC = 0.185        # row height, of the panel width
INSET_CELL_FRAC = 0.62        # section-cell height, of the cell width


def inset_layout(page, n_sections, n_rows):
    """(w, h, cols, cell_w, cell_h, row_h) - worked out before it is drawn,
    because the panel has to be placed before the markers are chosen."""
    w = page.w * INSET_W_FRAC
    row_h = w * INSET_ROW_FRAC
    cols = 1 if n_sections <= 1 else 2
    rows_of_cells = -(-n_sections // cols) if n_sections else 0
    cell_w = (w - 2 * T.INSET_PAD) / cols
    cell_h = cell_w * INSET_CELL_FRAC
    h = (2 * T.INSET_PAD + rows_of_cells * cell_h
         + (10 if n_sections else 0) + n_rows * row_h)
    return w, h, cols, cell_w, cell_h, row_h


def draw_inset(page, box, sections, step_fasteners, glyph_dir, letters):
    """The corner panel: one section per joint in the step, then the
    fasteners at large scale with their counts."""
    x, y, w, h = box
    rows = step_fasteners[:4]
    _w, _h, cols, cell_w, cell_h, row_h = inset_layout(page, len(sections),
                                                       len(rows))
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=T.W_RULE)

    top = y + h - T.INSET_PAD
    for i, (specs, label) in enumerate(sections):
        cx = x + T.INSET_PAD + (i % cols) * cell_w
        cy = top - (i // cols + 1) * cell_h
        joint_section(page, (cx, cy, cell_w, cell_h), specs, letters, label)
    if sections:
        top -= (-(-len(sections) // cols)) * cell_h + 10
        page.line((x + T.INSET_PAD, top + 4), (x + w - T.INSET_PAD, top + 4),
                  GREY, T.W_LEAD)

    for name, qty, svg, letter in rows:
        left = x + T.INSET_PAD
        if letter:
            badge(page, (left + T.BADGE_R, top - row_h / 2), letter)
            left += 2 * T.BADGE_R + 14
        gw, gh = glyph_dims(os.path.join(glyph_dir, svg))
        # Every glyph is drawn to one scale and carries it in its viewBox
        # height, so a long screw stays longer than a short one here too.
        eh = min(row_h * 0.70 * gh / 120.0, row_h * 0.90)
        ew = eh * gw / gh
        avail = x + w - T.INSET_PAD - row_h * 1.6 - left
        if ew > avail:
            eh *= avail / ew
            ew = avail
        page.embed_svg(os.path.join(glyph_dir, svg),
                       left, top - row_h / 2 - eh / 2, ew, eh)
        page.text((x + w - T.INSET_PAD, top - row_h / 2 - row_h * 0.20),
                  f"{qty}x", row_h * 0.60, anchor="end", weight="bold")
        top -= row_h


# ---------------------------------------------------------------------------
# THE STEP PAGES
# ---------------------------------------------------------------------------
# What a panel costs where it lands, in the units layout.place() scores in.
# A panel is opaque, so these are not preferences in the way a caption's are:
# line work it covers is line work nobody can read, a fastening point it
# covers loses its own mark and has to hand its count to a joint somewhere
# else on the page, and a panel on a panel is simply one page short.
PANEL_INK = 1.0
PANEL_MARK = 60.0
PANEL_PANEL = 4000.0


def emptiest_corner(plines, page, box_w, box_h, marks=(),
                    avoid_top_left=False, avoid=()):
    """Put the inset where the drawing is not - and, above all, where the
    fastening points are not.

    Four candidates, in the order they are preferred, through the same placer
    every other annotation goes through. `avoid` is any panel already on the
    page. Two panels in one corner is not crowding, it is one panel hiding the
    other."""
    occ = layout.Occupancy()
    occ.add_lines(plines, weight=PANEL_INK, tag="art")
    # The mark's own radius on top of the box's margin: a panel edge 40 mm
    # from a fastening point is already on it.
    occ.add_points([m["p2"] for m in marks], radius=10.0, weight=PANEL_MARK,
                   tag="mark")
    for a in avoid:
        occ.add_box(a, weight=PANEL_PANEL)
    corners = [(page.x1 - box_w - 20, page.y1 - box_h - 20),
               (page.x1 - box_w - 20, page.y0 + 20),
               (page.x0 + 20, page.y0 + 20)]
    if not avoid_top_left:
        corners.append((page.x0 + 20, page.y1 - box_h - 20))
    at = layout.place([(bx + box_w / 2, by + box_h / 2)
                       for bx, by in corners],
                      (box_w, box_h), occ, grow=30.0)
    return (at[0] - box_w / 2, at[1] - box_h / 2)


# ---------------------------------------------------------------------------
# THE HALF VIEW
# ---------------------------------------------------------------------------
# Three steps in this bed build the SAME CORNER TWICE, once at each end of a
# two-metre frame, and nothing at all in between: the back frame (1), the end
# beams and front posts (3), and the front bench rails on their stub legs (5).
# Drawn whole, the page spends four fifths of its width on a rail passing
# through, and the joint the step is actually about - four fasteners inside a
# 100 mm corner - lands at a scale where two screws are one smudge.
#
# So those pages take the furniture-manual half view: ONE end at better than
# twice the size, the frame running out of the crop the way it runs out of the
# reader's hand, and a small pictogram saying the other end is the same thing
# mirrored. The COUNTS do not halve with the picture - the inset table, the
# parts table and the step's own text stay whole-step totals, because a builder
# counting screws into a bag is not building half a bed - and the pictogram
# says that in words as well as showing it.
# WHICH steps those are is not this file's to know: `half_view` is a field on
# the step in docs/generated/byggesteg.json, declared in the one table that
# defines what a build step IS (tools/gen_doc_tables.build_steps).
# How much of the frame's length the crop keeps. Enough to hold the corner
# cluster and a clear run of every member leaving it; short enough that the
# reader can see it is a crop and not a shorter bed.
HALF_FRAC = 0.44


def half_crop(plines, marks=(), frac=HALF_FRAC):
    """(page box, the crop's own record) for the left end of a wide drawing.

    The cut is made on the PAPER, not in the model: keep the left `frac` of the
    projection and throw the rest over the edge. Which end of the bed that is
    depends on where the camera stands, and it does not matter - what matters
    is that the reader gets the near end of the page at full size and the
    members run out of the crop rather than stopping.

    The kept band sets the page's height as well as its width. Trimming the
    height to what is actually inside the crop is what keeps a half view from
    coming out as a ribbon: the far end of a two-metre frame seen in isometric
    sits a long way up or down the page, and none of that paper is wanted here.
    """
    bx0, by0, bx1, by1 = bounds(plines)
    cut = bx0 + (bx1 - bx0) * frac
    xs, hi = [bx0], [cut]
    ys = [p[1] for pl in plines for p in pl if p[0] <= cut]
    # The line work is not the whole page: every fastener this end drives is
    # about to be drawn hanging out of its hole with a badge behind it, and a
    # crop taken off the timber alone slices the heads off.
    for m in marks:
        if m["p2"][0] > cut:
            continue
        f = m["spec"]
        # From the HOLE, not from the tip: the drawn fastener stands off the
        # hole by its own length plus the hover, and its caption stands off
        # that again. Five badge radii is what the caption can wander.
        r = (f.get("length") or f.get("reach") or 40.0) + T.BADGE_R * 5.0
        for p in (m["a2"], m["p2"]):
            xs.append(p[0] - r)
            hi.append(p[0] + r)
            ys += [p[1] - r, p[1] + r]
    # The cut is where the FAR end is dropped, not a guillotine: a joint on the
    # near side of it keeps everything it needs, even where that reaches a
    # little past the line.
    return ((min(xs) - T.PAD, min(ys) - T.PAD,
             max(hi) + T.PAD, max(ys) + T.PAD),
            dict(cut=cut, x0=bx0, x1=bx1, frac=frac))


def mirror_note(page, prior_lines, new_lines, box, half):
    """The half view's own footnote, and it is a picture before it is a line.

    A reader who has just been handed one corner at twice the usual size will
    not go hunting for a sentence, so the note is the whole assembly at
    thumbnail scale with a ring round each end and the mirror axis drawn
    between them: build this, then build it again the other way round. The
    caption is there for the one thing a picture cannot say - that every number
    on this page is still counted for the whole frame.
    """
    x, y, w, h = box
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=T.W_RULE)
    pad = T.INSET_PAD
    cap_h = w * 0.075
    count_w = w * 0.17
    cell_w = w - 2 * pad - count_w
    cell_h = h - 2 * pad - cap_h

    allp = prior_lines + new_lines
    bx0, by0, bx1, by1 = bounds(allp)
    k = min(cell_w / max(bx1 - bx0, 1e-6), cell_h / max(by1 - by0, 1e-6))
    cx = x + pad + cell_w / 2
    cy = y + pad + cap_h + cell_h / 2

    def to_page(p):
        return (cx + (p[0] - (bx0 + bx1) / 2) * k,
                cy + (p[1] - (by0 + by1) / 2) * k)

    def moved(pls):
        return [[to_page(p) for p in pl] for pl in pls]

    page.polylines(moved(prior_lines), GREY,
                   max(T.W_PRIOR * k, T.THUMB_PRIOR_MIN))
    page.polylines(moved(new_lines), INK,
                   max(T.W_NEW * k * 0.7, T.THUMB_NEW_MIN))

    # A ring round each end - the same two corners, and the reason the page
    # only draws one of them. The bands are the crop's own width, taken off
    # either end, so the left ring is exactly what the big drawing shows.
    band = half["cut"] - half["x0"]
    ring_r = 0.0
    rings = []
    for a, b in ((half["x0"], half["cut"]), (half["x1"] - band, half["x1"])):
        pts = [to_page(p) for pl in allp for p in pl if a <= p[0] <= b]
        ex0, ey0 = min(q[0] for q in pts), min(q[1] for q in pts)
        ex1, ey1 = max(q[0] for q in pts), max(q[1] for q in pts)
        rings.append(((ex0 + ex1) / 2, (ey0 + ey1) / 2))
        ring_r = max(ring_r, math.hypot(ex1 - ex0, ey1 - ey0) * 0.34)
    ring_r = min(ring_r, cell_w * 0.30)
    for c in rings:
        page.circle(c, ring_r, width=T.W_RULE * 1.1)
    # The mirror axis between them, in the drawing convention for one: a
    # long-dash-short-dash centre line.
    mx = (rings[0][0] + rings[1][0]) / 2
    page.line((mx, cy - cell_h / 2), (mx, cy + cell_h / 2),
              INK, T.W_LEAD, dash="30 10 6 10")

    page.text((x + w - pad, cy - cap_h * 0.60), "×2", cap_h * 1.70,
              anchor="end", weight="bold")
    page.text((x + w / 2, y + pad * 0.7), "ANTALL GJELDER HELE RAMMEN",
              cap_h * 0.62, anchor="middle", weight="bold")


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
        page.polylines(moved, INK, T.W_NEW * 0.55)
    page.arrow((x + cell + 8, y + h / 2), (x + cell + 52, y + h / 2),
               INK, T.W_MARK, 20)


def magnifier(page, src, dst_c, dst_r, src_r, new_only, prior_lines):
    """The real line work around one point, blown up in a circle."""
    page.circle(src, src_r, width=T.W_LEAD)
    page.line(src, dst_c, GREY, T.W_LEAD, dash="18 14")
    page.circle(dst_c, dst_r, fill="#ffffff", width=T.W_RULE)
    page.polylines(remap(clip_to_circle(prior_lines, src, src_r),
                         src, src_r, dst_c, dst_r),
                   GREY, T.W_PRIOR * dst_r / src_r)
    page.polylines(remap(clip_to_circle(new_only, src, src_r),
                         src, src_r, dst_c, dst_r),
                   INK, T.W_NEW * dst_r / src_r)


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
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=T.W_RULE)
    page.circle((x + 40, y + h - 40), 22, width=T.W_RULE)
    page.text((x + 40, y + h - 50), "i", T.S_ICON, anchor="middle",
              weight="bold")
    page.text((x + 78, y + h - 52), "MADRASS", T.S_TITLE, weight="bold")
    page.text((x + 22, y + h - 112), "STANDARD 80 x 200 cm", T.S_BODY)
    page.text((x + 22, y + h - 166),
              f"TYKKELSE {G.MATTRESS_H_MIN}–{G.MATTRESS_H_MAX} mm",
              T.S_TITLE, weight="bold")

    # Section: slat top, mattress, the opening, both guard bands, post top.
    top = y + h - 208
    bot = y + 30
    z0, z1 = G.SLAT_Z1, G.GUARD_TOP
    k = (top - bot) / (z1 - z0)
    sx, sw = x + 26, w - 52

    def zy(z):
        return bot + (z - z0) * k

    page.line((sx, zy(G.SLAT_Z1)), (sx + sw, zy(G.SLAT_Z1)), INK, T.W_RULE)
    page.rect(sx, zy(G.MATTRESS_Z0), sw * 0.44,
              (G.MATTRESS_Z1 - G.MATTRESS_Z0) * k, fill="none", width=T.W_RULE)
    for zb in G.GUARD_BAND_Z0:
        page.rect(sx, zy(zb), sw * 0.44, G.GUARD_W * k, fill="none",
                  width=T.W_RULE)
    for i, zb in enumerate(G.GUARD_BAND_Z0):
        page.text((sx + 14, zy(zb) + G.GUARD_W * k / 2 - 10),
                  "REKKVERK" if i == 0 else "REKKVERK 2", T.S_NOTE)
    page.text((sx + 14, zy(G.MATTRESS_Z0)
               + (G.MATTRESS_Z1 - G.MATTRESS_Z0) * k / 2 - 10),
              "MADRASS", T.S_NOTE)

    def between(ax, za, zb, txt, limit):
        ya, yb = zy(za), zy(zb)
        page.arrow((ax, ya + 4), (ax, yb), INK, T.W_LEAD, 12)
        page.arrow((ax, yb - 4), (ax, ya), INK, T.W_LEAD, 12)
        page.text((ax + 12, (ya + yb) / 2 - 11), txt, T.S_DIM, weight="bold")
        page.text((ax + 12, (ya + yb) / 2 - 44), limit, T.S_LIMIT)

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


def check_coverage(st, kept, fasteners, families, share=1):
    """The hard check: everything the step's tables list is on the drawing.

    Two ways a page can lie, and both are build failures. It can show fewer
    screws than the step drives - the Baerekloss that was listed in the parts
    table and never once shown being fastened - and it can show fewer of a
    kind than the fastener table counts. So: every part family in the step's
    own parts table must carry at least one marker, and the marker counts must
    add up to the table's counts, kind for kind.

    `share` is what the HALF VIEW does to that sum and nothing else: a page
    that draws one of two identical ends must show exactly half of every kind,
    no more and no less. An odd count would mean the step is not the mirror
    pair the crop claims it is, and that is a build failure too.
    """
    shown = {}
    for m in kept:
        shown[m["name"]] = shown.get(m["name"], 0) + m["per"]
    for name, qty, _svg, _letter in fasteners:
        got = shown.get(name, 0)
        assert qty % share == 0, (
            f"steg {st['n']}: {qty} x '{name}' kan ikke deles på {share} "
            f"halvdeler - steget er ikke det speilparet halvsnittet påstår. "
            f"Sett half_view=False på steget i gen_doc_tables.build_steps().")
        assert got == qty // share, (
            f"steg {st['n']}: tegningen viser {got} x '{name}', "
            f"tabellen sier {qty}"
            + (f" ({qty // share} på den halvdelen som tegnes)"
               if share > 1 else "")
            + ". Festepunktene og beslaglista er ikke enige - se JOINTS i "
              "generate_loftbed.py.")
    covered = set()
    for m in kept:
        for part in mark_parts(m):
            covered.add(families.get(part.label))
    want = {families[l] for l in st["labels"] if l in families}
    missing = sorted(f for f in want - covered if f)
    assert not missing, (
        f"steg {st['n']}: {missing} står i deletabellen, men ingen "
        f"festing av dem er tegnet. Legg leddet inn i JOINTS i "
        f"generate_loftbed.py.")


def render_step(G, view, st, uni, placed, out_dir, width, page_box, glyph_dir,
                fasteners, families, centre, half=None):
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

    # A mirror-symmetric step is cropped to one of its two identical ends, and
    # the crop is taken off the finished projection - which is also where the
    # mirror pictogram gets the whole thing from.
    # Where the fasteners go, in the drawing's own frame. A step that drives
    # only one kind needs no letters: the glyph in its table is already the
    # whole answer. This has to be known before the page rectangle is fixed:
    # an exploded screw sticks out past the timber it goes into, and a crop
    # that only knows about the timber would cut its head off.
    # WHAT KIND OF PAGE THIS IS comes off the step, not out of a label match.
    # The mattress page used to be recognised by a part name beginning with
    # "Mattress", and that one match then steered six different behaviours -
    # no marks, a panel of its own size, a corner ruled out, an information
    # panel instead of a fastener list, no coverage check, no magnifier. Six
    # behaviours behind one string is five accidents waiting: the step now
    # says each of them out loud.
    letters = {name: letter for name, _q, _s, letter in fasteners if letter}
    marks = [] if st.get("no_fasteners") else step_marks(G, st, letters, view)

    if half:
        page_box, half = half_crop(combined.get("prior", []) + new_only,
                                   marks)
        # Only the end that is drawn. The other end's fasteners are not
        # dropped from the manual - they are still in every count on the page
        # - they are dropped from the PICTURE, which is the whole point of a
        # half view and is what the mirror pictogram says out loud.
        marks = [m for m in marks if m["p2"][0] <= half["cut"]]
    x0, y0, x1, y1 = page_box
    page = Page(x0, y0, x1, y1)
    page.polylines(combined.get("prior", []), GREY, T.W_PRIOR)
    # The new part is drawn whole - but the stretch of it that something
    # already standing hides is drawn DASHED, because that is the only thing
    # on the page that says which side of the frame it goes on. The front side
    # rail passes BEHIND the front posts, and a solid line across the post
    # says the opposite.
    page.polylines(new_only, INK, T.W_NEW * 0.45, dash="26 20")
    page.polylines(combined.get("new", []), INK, T.W_NEW)

    # No step number in the drawing: the page header already carries it, and
    # two of them is one too many.

    sections = step_sections(marks)
    if st.get("info_panel"):
        # The information panel carries a section as well as three lines of
        # text, so it needs more room than a fastener list does.
        inset_w, inset_h = page.w * 0.32, page.h * 0.36
    else:
        inset_w, inset_h = inset_layout(page, len(sections),
                                        len(fasteners[:4]))[:2]
    # A step with no fastener marks has nothing to steer the panel away from,
    # and the mattress itself is only a handful of outline points - so
    # "emptiest" would pick the top left corner, which is exactly the corner
    # the panel is about: the mattress meeting the back wall. The step says so
    # itself with avoid_top_left.
    bx, by = emptiest_corner(combined.get("prior", []) + new_only,
                             page, inset_w, inset_h, marks,
                             avoid_top_left=st.get("avoid_top_left"))
    box = (bx, by, inset_w, inset_h)
    # Both of these are measured on the SHORT side of the page, so a step
    # that gets a tall page of its own - the ladder - does not get arrows and
    # spacings scaled off a height it never uses across.
    keep = choose_marks(marks, inset=box)
    keep = restore_orphans(keep, families,
                           {families[l] for l in st["labels"]
                            if l in families})

    if st.get("info_panel"):
        info_panel(page, (bx, by, inset_w, inset_h), G)
    elif fasteners:
        draw_inset(page, box, sections, fasteners, glyph_dir, letters)
    if not st.get("no_fasteners"):
        check_coverage(st, keep, fasteners, families, share=2 if half else 1)

    # The mirror pictogram is PLACED here and DRAWN last: it has to be out of
    # the magnifiers' way before they go looking for paper, and on top of the
    # line work when it lands.
    note_box = None
    if half:
        note_w = page.w * 0.38
        note_h = note_w * 0.42
        nx, ny = emptiest_corner(combined.get("prior", []) + new_only,
                                 page, note_w, note_h, keep,
                                 avoid=(box,))
        note_box = (nx, ny, note_w, note_h)

    # THE FASTENERS THEMSELVES. Two styles, and which one a page gets is
    # decided by how many marks survive the merge: a step that drives eight
    # screws is clearer with all eight pulled out of their holes, and a step
    # that drives twenty-eight - the slat fields - would be a forest. Those
    # get the in-situ phantom instead, which says the same thing quietly.
    style = "eksplodert" if len(keep) <= EXPLODE_MAX else "in situ"
    short = min(page.w, page.h)
    hover = short * EXPLODE_FRAC
    float_d = short * EXPLODE_PLATE_FRAC
    # THE OCCUPANCY FIELD: everything already on the paper, in one place, so
    # every rule that has to ask "is there room here" asks the same object.
    # The two layers are not the same thing to a fastener - it is welcome to
    # lie across the ghosted frame that is already standing, that is what
    # ghosting is for, but not across the piece this step is about.
    occ = layout.Occupancy()
    occ.add_lines(combined.get("prior", []), weight=0.15, tag="grey")
    occ.add_lines(new_only + combined.get("new", []), weight=1.0, tag="dark")
    occ.add_box(box, weight=40.0)
    stacks = {}
    captions = []
    # The brackets are placed BEFORE anything is drawn: a bracket's own screws
    # explode from where the bracket ended up, so they have to know its float
    # before their own hop back is worked out.
    floats = {}
    if style == "eksplodert":
        for m in keep:
            if m["spec"]["kind"] == "plate":
                floats[id(m["spec"])] = float_plate(
                    occ, view, m["spec"], plate_screws(G, m["spec"]), float_d)
    plates = [m["spec"] for m in keep if m["spec"]["kind"] == "plate"]

    def rides_on(f):
        """The bracket this screw goes through, if it goes through one."""
        for p in plates:
            if p["jid"] == f["jid"] and screw_on_plate(p, f):
                return floats.get(id(p), (0.0, 0.0))
        return (0.0, 0.0)

    # R2's other half. Two bodies that do NOT overlap are two marks, so the
    # page has to be able to show them as two - and the only move an exploded
    # fastener has is further out along its OWN axis. Every body that has been
    # drawn is kept here as the capsule it is, and the next one queues up
    # behind its own hole until it is clear of all of them. Never sideways:
    # a screw beside its own dotted line has stopped saying where it goes.
    drawn_caps = []
    for m in sorted(keep, key=lambda q: (-q["p2"][1], q["p2"][0])):
        f = m["spec"]
        key = (round(m["p2"][0] / 6.0), round(m["p2"][1] / 6.0),
               tuple(round(c, 3) for c in f["direction"]))
        stack = stacks.get(key, 0)
        stacks[key] = stack + 1
        if style == "eksplodert":
            dx, dy = view.dir_xy(f["direction"])
            nrm = math.hypot(dx, dy)
            hole = view.xy(f["anchor"])
            if f["kind"] == "plate":
                # No axis, so no hop back: the float on the paper IS the whole
                # explosion, and the dotted line is the leash to its seat.
                poff = floats[id(f)]
                shift = (0.0, 0.0, 0.0)
                # The caption goes OUTBOARD of the float, away from the seat:
                # parked on the leash side it reads as a label for the hole.
                lead = math.hypot(*poff)
                label_dir = (-poff[0] / lead, -poff[1] / lead)
            else:
                # Backed out along its own axis in MODEL space, so the pulled
                # screw stays on the line it travels no matter where the camera
                # stands. The hop is measured off the projection - the screw's
                # own drawn length plus `hover` - so the point ends up exactly
                # that far short of its hole whatever the angle, and body,
                # dotted line and hole are one straight run.
                poff = rides_on(f)
                if nrm >= AXIS_ON_PAGE:
                    ux, uy = dx / nrm, dy / nrm
                    blen = max(f["length"] * nrm,
                               f["length"] * FORESHORTEN_FLOOR)
                    # The hop is the drawn body plus air, grown along the axis
                    # if that is what it takes to find paper. Room is looked
                    # for where the screw will actually BE - which for one
                    # through a floated bracket is the bracket's hole, not the
                    # seat it has left. Coaxial screws then queue up BEHIND one
                    # another on the shared axis - never beside it - so every
                    # one of them still points at the hole it belongs to.
                    out = clear_back(occ, (hole[0] + poff[0],
                                            hole[1] + poff[1]),
                                     (ux, uy), blen, blen + hover,
                                     hover, f["d"] * SCREW_FATTEN * 0.75)
                    # ...and then out again, one body at a time, until it is
                    # clear of every body already on the page. QUEUE_MAX is
                    # where it gives up and overlaps rather than ending up in
                    # the next county: at that point the two really are one
                    # place and the drawing says so by drawing them there.
                    for q in range(QUEUE_MAX):
                        back = (out + (blen + hover) * q) / nrm
                        shift = tuple(-c * back for c in f["direction"])
                        cap = body_capsule(view, f, shift, poff)
                        if not any(capsules_overlap(cap, c)
                                   for c in drawn_caps):
                            break
                    label_dir = (ux, uy)
                else:
                    # Driven straight into the paper. There is no axis on the
                    # page to come out along and no honest direction an
                    # explosion could take, so the ringed dot - which is the
                    # convention for exactly this - stays where the hole is.
                    back = 0.0
                    shift = (0.0, 0.0, 0.0)
                    label_dir = (0.0, -1.0)
            drawn_caps.append(body_capsule(view, f, shift, poff))
            head, tip, body = draw_fastener(page, view, m, style, shift, 0,
                                            poff)
            # Dotted, not dashed and not an arrow: this line is a fastener's
            # travel, and the page keeps that convention to itself. For a screw
            # it is a pure extension of the screw's own axis, and it leaves the
            # POINT that was drawn - not the point the unstretched projection
            # would have had, which is somewhere up inside the body. A
            # bracket's line is the leash back to its true seat; a screw's runs
            # to its hole in whatever it goes into, and if that is a floated
            # bracket the line follows the bracket - which is where the screw
            # actually goes in.
            entry = hole if f["kind"] == "plate" else (hole[0] + poff[0],
                                                       hole[1] + poff[1])
            start = body[1] if body is not None else tip
            if _apart(start, entry, 1.0):
                page.line(start, entry, GREY, T.W_PHANTOM, dash=DASH_INSERT)
            page.dot(entry, T.ENTRY_R, colour=INK)
            if f["kind"] == "plate":
                assert_float_direction(
                    page, view, f,
                    disassembly_dir(view, f, plate_screws(G, f)), m["jid"])
            else:
                assert_on_axis(view, f, body, tip, entry, poff, m["jid"])
            # The caption goes behind the HEAD, i.e. further from the hole -
            # the one direction that cannot land on the fastener itself.
            label_at = head
            mine = [head, tip, ((head[0] + tip[0]) / 2,
                                (head[1] + tip[1]) / 2), entry]
        else:
            draw_fastener(page, view, m, style, stack=stack)
            label_at = m["p2"]
            label_dir = (0.0, -1.0)
            mine = [m["p2"]]
        # Into the field, under this mark's OWN name: R5 is the question "is
        # there anything nearer than my own body", and it can only be asked of
        # a field that knows whose everything is.
        occ.add_points(mine, radius=T.BADGE_R + 10, weight=CAP_MARK,
                       owner=mark_owner(m), tag="mark")
        captions.append((label_at, label_dir, m["letter"], m["per"],
                         mark_owner(m)))

    # THE CAPTIONS, once every fastener is down. Placing each one as its own
    # fastener was drawn is what let the second badge on a crowded corner park
    # itself neatly on top of the ninth screw - which had not been drawn yet,
    # so nothing objected. A caption that sits on a fastener it does not name
    # is worse than no caption: it is a wrong one.
    for label_at, label_dir, letter, per, owner in captions:
        mark_label(page, label_at, label_dir, letter, per, occ, owner)
    if style == "eksplodert":
        assert_bodies_apart(page)
    assert_marks_own_element(page, occ)

    # R3 - NO LEADERS FROM THE INSET.
    # The panel used to trail up to four long grey dashed lines across the
    # drawing to the nearest fastening points. They said nothing: the badge
    # letter already ties every mark to its row in the panel, and it does it
    # for ALL the marks rather than for the four that happen to be closest.
    # What the lines did do was cross the line work at every angle, and on a
    # half view they ran straight through the corner the page exists to show.
    # A magnifier is different and stays: it carries real line work, and its
    # short leader says which spot has been blown up.
    if keep and fasteners:
        if len(mark_clusters(keep, T.BADGE_R * 2)) <= 2:
            src = keep[0]["p2"]
            src_r = max(page.w, page.h) * 0.055
            dst_r = inset_w * 0.30
            dst_c = (bx + inset_w / 2, by + inset_h + dst_r + 60)
            if dst_c[1] + dst_r > y1 - 20:
                dst_c = (bx + inset_w / 2, by - dst_r - 60)
            magnifier(page, src, dst_c, dst_r, src_r, new_only,
                      combined.get("prior", []))

    # The J12 bracket used to need a magnifier of its own here: at page scale
    # it was 40 mm of steel behind a 1794 mm ledger and nobody could place it.
    # It does not need one any more. The bracket now floats off its seat on a
    # short dotted leash with its two screws coming out along their own axes -
    # one into the post, one up into the ledger - and that says everything the
    # blown-up circle said, in the place it is actually about, without a lens
    # covering a quarter of the drawing to say it.

    # Before / after: the frame is built flat and then stood up.
    if st.get("thumbnail_parts"):
        tb_w = page.w * 0.30
        tb_h = page.h * 0.22
        thumbnails(page, view, G, st["thumbnail_parts"],
                   (x0 + 30, y1 - tb_h - 130, tb_w, tb_h))

    if note_box is not None:
        mirror_note(page, combined.get("prior", []), new_only, note_box, half)

    svg = os.path.join(out_dir, f"steg-{n:02d}.svg")
    png = os.path.join(out_dir, f"steg-{n:02d}.png")
    page.write(svg)
    to_png(svg, png, width)
    if letters:
        PAGE_SCALES[n] = width / page.w
    print(f"  steg {n:2d}  {len(combined.get('prior', [])):4d} gra / "
          f"{len(new_only):4d} svarte / {len(keep):2d} festepunkt -> {png}")
    return png


# ---------------------------------------------------------------------------
# THE CONTRAST PROOF
# ---------------------------------------------------------------------------
# A fill code that cannot be told apart at the size it is printed is not a
# code, it is a texture. So the set is not chosen and then trusted: it is
# drawn, at the sizes the step pages actually give a fastener, and looked at.
#
# `PAGE_SCALES` is filled in as the pages are drawn - {step: px per model mm}
# for every page that carries badge letters, because those are the only pages
# a fill code appears on. The proof then renders at the SMALLEST of them, which
# is the worst case the manual contains, and at half that again as a stress
# test. It is written to docs/preview/, beside the page previews, because it is
# review material and not part of the manual.
PAGE_SCALES = {}
PROOF_PATTERNS = ("solid", "open", "hatch", "cross", "dots")


def fill_contrast_strip(out_dir, px_per_mm):
    """docs/preview/fyllkontrast.{svg,png} - every fill code at page size."""
    import gen_glyphs
    col = 118.0
    lab = 150.0
    rows = [
        ("5x40 EKSPLODERT", "screw", 5.0, 40.0, 1.0),
        ("6x90 EKSPLODERT", "screw", 6.0, 90.0, 1.0),
        ("5x60 I SITU (FANTOM)", "situ", 5.0, 60.0, 1.0),
        ("5x60 HODET ALENE", "head", 5.0, 0.30, 1.0),
        ("INNSETT (SNITT)", "sect", 5.0, 50.0, 1.0),
        ("5x40 PA HALV SIDE", "screw", 5.0, 40.0, 0.5),
    ]
    row_h = 34.0
    w = lab + col * len(PROOF_PATTERNS) + 20.0
    h = 42.0 + row_h * len(rows) + 16.0
    page = Page(0.0, 0.0, w, h)
    top = h - 16.0
    page.text((10.0, top), "FYLLKODE - KONTRASTPROVE", 13.0, weight="bold")
    page.text((10.0, top - 15.0),
              f"tegnet i {px_per_mm:.2f} px per mm - stegsidenes egen skala",
              9.5)
    top -= 34.0
    for i, code in enumerate(PROOF_PATTERNS):
        page.text((lab + col * i + col / 2, top), code.upper(), 10.0,
                  anchor="middle", weight="bold")
    top -= 6.0
    for label, kind, d, arg, k in rows:
        cy = top - row_h / 2
        page.text((lab - 12.0, cy - 3.5), label, 9.5, anchor="end")
        for i, code in enumerate(PROOF_PATTERNS):
            paint = page.fill_paint(code)
            x = lab + col * i + 8.0
            if kind == "screw":
                pts = screw_outline((x, cy), (1.0, 0.0), arg * k, d * k)
                page.poly(pts, fill=paint, stroke=INK, width=T.W_SCREW * k)
            elif kind == "situ":
                # Buried in wood: the outline is a phantom line and only the
                # head is solid, so the fill has the whole body to live in but
                # no continuous edge round it.
                pts = screw_outline((x, cy), (1.0, 0.0), arg * k, d * k)
                page.poly(pts, fill=paint, stroke="none", width=0)
                page.polylines([pts[1:len(pts) - 1] + [pts[1]]], INK,
                               T.W_SCREW * 0.62 * k, dash=DASH_PHANTOM)
                page.poly(pts[:2] + pts[-2:], fill=INK, stroke=INK,
                          width=T.W_SCREW * 0.8 * k)
            elif kind == "head":
                w_s = d * SCREW_FATTEN * k
                hl = w_s * arg
                page.poly([(x, cy + w_s * 0.95), (x + hl, cy + w_s / 2),
                           (x + hl, cy - w_s / 2), (x, cy - w_s * 0.95)],
                          fill=paint, stroke=INK, width=T.W_SCREW * 0.8 * k)
            else:
                # The inset's own section screw: floored at SEC_SCREW_MIN and
                # drawn with the section's lighter pen.
                w_s = max(d * 0.8, T.SEC_SCREW_MIN) * k
                hd, hl, tl = w_s * 1.9, w_s * 0.55, w_s * 1.7
                L = arg * k
                page.poly([(x, cy + hd / 2), (x + hl, cy + w_s / 2),
                           (x + L - tl, cy + w_s / 2), (x + L, cy),
                           (x + L - tl, cy - w_s / 2), (x + hl, cy - w_s / 2),
                           (x, cy - hd / 2)],
                          fill=paint, stroke=INK, width=T.W_RULE * 0.8 * k)
        page.line((10.0, top - row_h), (w - 10.0, top - row_h), GREY,
                  T.W_LEAD * 0.5)
        top -= row_h
    page.fills |= set(PROOF_PATTERNS)
    os.makedirs(out_dir, exist_ok=True)
    svg = os.path.join(out_dir, "fyllkontrast.svg")
    png = os.path.join(out_dir, "fyllkontrast.png")
    page.write(svg)
    to_png(svg, png, int(round(w * px_per_mm)))
    print(f"  fyllkontrast  {w:.0f} x {h:.0f} mm @ {px_per_mm:.2f} px/mm "
          f"-> {png}")
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
    - and that is right for the ten steps that build across the whole 1990 mm
    of it. The ladder is not one of them: it is 416 mm wide and 1700 tall, and
    on a bed-wide page it comes out as a sliver with four badges fighting for
    the 320 mm between its stiles. So that step asks for a page of its own,
    cut round its parts - the scale goes up, the badges stay the size they
    are, and the grey frame behind simply falls outside the viewBox.

    WHICH step is the step's own business (`crop_to_subject` in
    byggesteg.json), not a threshold guessed at here. The old test - "does the
    subject fill less than a third of the page" - answered the question
    correctly for exactly one step and would have answered it differently the
    day somebody re-aimed a camera.
    """
    if not new_parts:
        return page_box
    bx0, by0, bx1, by1 = bounds(project(view, [("s", comp(new_parts))])["s"])
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
    use_model(G)
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
        pages[key] = (bx0 - T.PAD, by0 - T.PAD, bx1 + T.PAD, by1 + T.PAD)

    made, placed = [], []
    for st in data["steps"]:
        n = st["n"]
        if not st["image"]:
            placed += st["labels"]
            continue
        if st.get("page") == "cutpage":
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
            half = st.get("half_view")
            box = pages[key]
            if st.get("crop_to_subject"):
                box = crop_to_subject(views[key], box,
                                      [uni[l] for l in st["highlight"]])
            if st.get("thumbnails"):
                # The one step that changes the workpiece's orientation shows
                # it before and after; "before" is everything already standing.
                st["thumbnail_parts"] = [uni[l] for l in placed]
            if st.get("page") == "panel":
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
                                  families, centre, half)
            if png:
                made.append(png)
        placed += st["labels"]
    return made


def render_hero(G, out_dir, width, az=330, elev=22):
    use_model(G)
    bed = full_bed(G)
    look_at = bed.bounding_box().center()
    view = View(camera_direction(az, elev), look_at)
    plines = project(view, [("all", bed)])["all"]
    x0, y0, x1, y1 = bounds(plines)
    page = Page(x0 - T.PAD, y0 - T.PAD, x1 + T.PAD, y1 + T.PAD)
    page.polylines(plines, INK, T.W_HERO)
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
    hero_only = steps_only = proof = False
    i = 1
    while i < len(argv):
        if argv[i] == "--fill-contrast":
            proof = True; i += 1; continue
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
    if proof:
        fill_contrast_strip(os.path.join(ROOT, "docs", "preview"),
                            min(PAGE_SCALES.values()))
    print(f"\n{len(made)} tegninger i {out_dir}")


if __name__ == "__main__":
    main(sys.argv)
