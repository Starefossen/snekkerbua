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


# THE THREE VISIBLE-EDGE COMPOUNDS ARE TAKEN TOGETHER, AND FOR THE REFERENCE
# BODIES THAT WAS MEASURED, NOT ASSUMED. A body is a fusion of spheres and
# cylinders, so the worry was that the sharp (VCompound) and smooth
# (Rg1LineVCompound) sets would arrive as the SEAMS - circles of solder where
# one limb was welded to the next - and that a body would have to be harvested
# from OutLineVCompound alone to read as a person. It is the other way round:
# in a true elevation the outline compound holds ONLY the curved silhouettes
# and drops every straight generatrix, so a child comes out as eleven
# disconnected arcs. All three together is 64 edges on a seated child, 70 on a
# lying one, and it draws a person. The seams that survive are the shoulder
# and the hip, which is where a drawing wants a line anyway.
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
def step_marks(G, st, letters, codes, view):
    """One mark per fastener the step drives, in the drawing's own frame.

    The mark carries both keys the page hangs on a fastener: the badge LETTER,
    which every lettered page has, and the fill CODE, which only a page the
    rule fired on has. They are looked up here, once, off the two dicts the
    page was handed - so the body, the section and the panel row all draw the
    same fastener the same way, and a bare page is bare everywhere.
    """
    specs = [f for f in G.FASTENER_SPECS if f["jid"] in st["joints"]]
    # The ring a head-on fastener is drawn with is a property of the PAGE, not
    # of the screw: it shrinks where its neighbours crowd it (A ROW OF HEADS).
    # It has to be known here, because mark["body"] is what R2 merges on.
    rings = ring_radii(view, specs)
    out = []
    for f, ring in zip(specs, rings):
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
                        code=codes.get(f["name"]),
                        area=area, spec=f, ring=ring,
                        # The body as the page would draw it sitting in its
                        # hole - what R2 asks its question of.
                        body=body_capsule(view, f, ring=ring)))
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
# SHOULD THE FLOOR BE HIGHER FOR A SHORT SCREW? It is the obvious worry - a
# fraction treats a 5x40 and a 6x120 alike, and what makes a silhouette read as
# a SCREW is not its length in millimetres but how much longer it is than the
# head is WIDE, and the head does not shrink when the length does. So the pages
# were measured, every drawn body against its own drawn head:
#
#   1.81 heads   5x40, J10 (step 5) and J12 (step 1) - the shortest in the book
#   1.85         6x60, J9-F (step 3) - the shortest the FLOOR itself makes
#   2.2 - 3.3    everything else
#
# The answer is no, and the measurement is why. The stubbiest bodies in the
# manual are NOT floored at all: a 5x40 seen at this angle projects to 35.6 of
# its 40 mm all by itself, well clear of 28.8, so the floor never touches it
# and raising the floor cannot reach it. And it could not reach far if it did:
# a floor may never draw a screw LONGER than it is, so the whole of what a
# short screw could gain is the 12 % up to its true 40 mm - 1.81 heads becoming
# 2.05, which is not a difference anyone can see. What actually sets how stubby
# a 40 mm screw looks is the head, i.e. SCREW_FATTEN, and that number was
# settled on its own proof (docs/preview/formkontrast.png).
#
# What the worry deserves is not a second knob but a TRIPWIRE, and 1.75 is the
# value that was landed: no drawn body may come out under STUB_ASPECT of its
# own drawn head. It sits just under what the pages measure today, so the day a
# new camera, a shorter screw or a wider head makes a real dart of one, the
# build stops and a human looks at it - instead of the manual quietly acquiring
# an arrowhead where a fastener should be. assert_no_stubs() is the rule, and
# it measures the ink.
STUB_ASPECT = 1.75
# Below this much of its true length on the page a screw has no axis left to
# draw and becomes a ringed dot. One number, used by the shape function and by
# the explosion alike: a fastener that is a dot is not backed out of anything,
# because a dot cannot show which way it came.
AXIS_ON_PAGE = FORESHORTEN_FLOOR * 0.5


def foreshorten_floor(length):
    """The shortest a screw may be DRAWN, in model mm.

    One function, because the floor is asked for in four places - the
    silhouette, the explosion's hop back, a group's beat and the capsule every
    distance rule measures against - and a floor that four callers work out for
    themselves is four floors.
    """
    return length * FORESHORTEN_FLOOR


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
# HOW MUCH AIR IS ENOUGH. The first drawings were made at 0.038 of the short
# side - 42 mm on a 1114 mm page, more than a whole 5x40 - and the answer was
# measured on the paper rather than argued: at that gap the eye has to TRAVEL
# from a drawn point to a hole across empty white, and on a page with six of
# them it does that six times. The gap only has to be big enough that the point
# is visibly not in the hole yet; every millimetre past that is distance the
# reader crosses for nothing. 0.024 is 27 mm, about two thirds of the screw's
# own drawn body, which reads as "just short of home" at a glance and still
# leaves the dotted line three or four dashes long. The floor is the receiving
# edge: the gap may not shrink so far that the point touches the timber it is
# about to enter, and clear_back() is what keeps it off - it samples the body
# in the occupancy field and hops further out along the SAME axis where the
# close-in position is taken.
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
EXPLODE_FRAC = 0.024
EXPLODE_PLATE_FRAC = 0.024
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


def page_fill_codes(st, letters):
    """{handelsnavn: fyllkode} for one page - EMPTY where the page draws bare.

    Whether a page codes its fasteners is not this file's decision and not a
    number in this file either. It is a property of the STEP, derived from the
    fasteners the step drives and written into byggesteg.json as `fill_code`
    (tools/gen_doc_tables.step_fill_code), on the same terms as `half_view`
    and the rest: the code is bought to separate two screws the silhouette
    cannot separate, so it is paid for on the pages that have such a pair and
    nowhere else. An empty dict here means every fastener on the page comes
    out as a bare outline - badges, leaders and counts unchanged, because
    those answer a different question.
    """
    if not st.get("fill_code"):
        return {}
    return {name: fill_code(letter) for name, letter in letters.items()}


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


def thread_cues(code):
    """Does THIS fastener's silhouette carry its thread? R8.

    ONE TEXTURE PER SILHOUETTE. A drawn screw is a body about ten millimetres
    wide on a page a metre and a half across, and there is room in it for one
    pattern. The thread is the default, because the thread is most of what
    makes a shape read as a SCREW rather than as a dart; where a page has
    bought the fill code, the code is a second pattern of the same order of
    size and the two together are neither - the reader gets grey.

    So the code takes the body from the thread, and only where the code is
    actually a PATTERN. `open` is the absence of one, and it is deliberately
    handed to the letter the page has most of (gen_glyphs.FILL_CODES), so the
    commonest screw on a coded page - sixteen of the twenty on step 5 - keeps
    its thread and looks like the same object it is on every other page.
    Nothing competes with it there, so nothing is bought by taking it away.
    """
    return code in (None, "open")


def drawn_head_r(d):
    """Half the widest part of a drawn fastener: its countersunk head.

    The capsule every distance rule measures against is as wide as the widest
    thing on the silhouette, and on a countersunk screw that is the head. One
    definition, off the same ratio gen_glyphs draws the head with, so a change
    to the shape cannot leave the geometry that reasons about it behind.
    """
    import gen_glyphs
    return d * SCREW_FATTEN * gen_glyphs.HEAD_DIA_RATIO / 2.0


# ---------------------------------------------------------------------------
# A ROW OF HEADS - HOW BIG THE RINGED DOT IS
# ---------------------------------------------------------------------------
# A screw driven straight at the camera has no silhouette left, and the page
# draws the ringed dot instead. That ring is the one mark on the page whose
# size comes from NOTHING in the model: T.RING_R is a page constant, the same
# circle for a 5x40 and a 6x120, chosen so a single head-on screw reads at
# arm's length. It is a symbol, not a projection.
#
# And a symbol that is bigger than the spacing of the things it stands for
# stops being able to count them. J3 drives three 6x80 up the ladder upright
# 24 mm apart, dead-on to the step-6 camera; three rings of T.RING_R = 15 mm
# at 23 mm centres are a chain of overlapping circles, so R2 - which asks
# whether the DRAWN bodies share paper, and is right to - merged the middle
# one away and the page showed four screws where the table said six.
#
# The screws are not the problem. The symbol is, so the symbol gives way: in a
# row of head-on rings each one shrinks to half the gap to its nearest
# neighbour, which is the largest circle that still leaves every screw its own
# ring, and the row reads as the row of holes it is. Nothing else changes -
# same centre dot, same ink, same place - and the ring is never drawn LARGER
# than T.RING_R, so a lone head-on screw is untouched on every page.
#
# The floor is legibility: below RING_MIN_RATIO times its own centre dot there
# is no annulus left to see, only a blob, and at that point the two really are
# one place on the paper. Then the ring keeps its full size, the two bodies
# overlap, and R2 merges them into one mark carrying the count - which is the
# honest answer for two screws the camera has genuinely put on top of each
# other. assert_joint_marks_drawn() is where such a pair has to be written
# down by name before the build will pass.
RING_MIN_RATIO = 1.9
# The rings may touch, but a hairline of white between two circles is what
# makes them two circles, and capsules_overlap() is a strict "<" - so a row
# sized to exactly half the gap would sit on the boundary of every rule that
# measures it. This is that hairline, as a fraction of the half-gap.
RING_ROW_SLACK = 0.98


def head_on_point(view, f):
    """Where a fastener with no axis left on the page puts its ring, or None.

    The same test body_capsule() and draw_fastener() make - a projected axis
    shorter than AXIS_ON_PAGE of the screw's true length - asked once, in one
    place, so the ring rule and the ink cannot disagree about which fasteners
    are head-on.
    """
    if f["kind"] == "plate":
        return None
    p0 = view.xy(f["anchor"])
    p1 = view.xy(tuple(a + d * f["length"]
                       for a, d in zip(f["anchor"], f["direction"])))
    if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) >= f["length"] * AXIS_ON_PAGE:
        return None
    return p0


def ring_radii(view, specs):
    """The ring each head-on fastener on ONE page is drawn with.

    A list parallel to `specs`, None where the fastener has an axis to draw
    and therefore no ring. Every radius is at most T.RING_R and at least
    RING_MIN_RATIO centre dots, and the pairwise guarantee follows from taking
    half the NEAREST neighbour's gap: if r_a is half a's nearest gap and r_b
    half b's, then r_a + r_b <= d(a, b) for every pair that is not already
    inside the floor. So no two rings that could be separated are drawn on top
    of each other, and no ring is drawn too small to be a ring.
    """
    floor = T.RING_DOT_R * RING_MIN_RATIO
    pts = [head_on_point(view, f) for f in specs]
    out = []
    for i, p in enumerate(pts):
        if p is None:
            out.append(None)
            continue
        gaps = [math.hypot(q[0] - p[0], q[1] - p[1]) * 0.5 * RING_ROW_SLACK
                for j, q in enumerate(pts) if q is not None and j != i]
        gaps = [g for g in gaps if g >= floor]
        out.append(min([T.RING_R] + gaps))
    return out


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


def body_capsule(view, f, shift=(0.0, 0.0, 0.0), page_off=(0.0, 0.0),
                 ring=None):
    """The drawn body as (end, end, half-width) on the page.

    For a screw that is what the silhouette IS. For a bracket - which has no
    axis - it is the disc round its projected corners, which is close enough
    for a question no bracket has ever had to answer: a merge only ever
    considers two fasteners with the SAME NAME, and no bracket shares a name
    with a screw.

    `ring` is the head-on ring this fastener is DRAWN with on this page - see
    A ROW OF HEADS. It is passed in rather than read off T because a row of
    them shrinks together, and a capsule that assumed the full symbol would
    keep merging away screws the page has just made room for.
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
    r = drawn_head_r(f["d"])
    n = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if n < f["length"] * AXIS_ON_PAGE:
        # Head on: the page draws a ringed dot, so that is the body.
        return (p0, p0, T.RING_R if ring is None else ring)
    # The capsule is the body the page DRAWS, floor and all - not the raw
    # projection. A foreshortened screw is stretched back to the floor when it
    # is drawn, and a capsule that stopped short of it would let a badge park
    # on ink the rule believes is white.
    floor = foreshorten_floor(f["length"])
    if n < floor:
        p1 = (p0[0] + (p1[0] - p0[0]) * floor / n,
              p0[1] + (p1[1] - p0[1]) * floor / n)
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


# ---------------------------------------------------------------------------
# R9 - A BRACKET AND ITS SCREWS COME OFF AS ONE GROUP
# ---------------------------------------------------------------------------
# R1 says which way a bracket leaves. It says nothing about how far, and it
# says nothing at all about the screws that go THROUGH the bracket - and those
# two silences were what made the J12 corner unreadable. The bracket floated
# as far off its seat as the paper allowed; its two screws then backed out of
# it by their own drawn length plus a hop that had nothing to do with the
# bracket's; and the three dotted lines that resulted crossed each other in the
# middle of a corner the reader is trying to take in as one piece of work.
#
# A corner like that is ONE disassembly, not three, and an exploded view is a
# picture of taking things apart in order:
#
#     seat  --d-->  bracket  --d-->  each of its screws
#
# ONE RHYTHM, d, for the whole group. The bracket sits d off its seat along its
# disassembly direction (R1); every screw that rides on it then continues from
# WHERE THE BRACKET ENDED UP, along its own drive axis (which is the screws'
# own rule and is never bent), until the gap between its drawn point and its
# hole in the floated bracket is d as well. Two equal steps, and the eye reads
# them as one movement outward rather than as three unrelated escapes.
#
# The tethers follow from it and become a nested chain: seat -> bracket, and
# bracket -> each screw's own hole ON the bracket. Two asserts hold it, and
# both measure the ink: assert_chain_rhythm(), the steps are equal, and
# assert_chain_untangled(), the nesting is not cut - no screw's line crosses
# the leash it hangs off and none runs through a body in its own group. What is
# NOT assertable is two sibling lines meeting near the bracket; see the note
# there for the measurement that says why.
#
# What is still free is d itself: the group as a whole moves further out if
# there is no room close in, which is the same single degree of freedom R1
# already left the bracket. It moves as ONE - and that is also how the group
# gets its screws apart from each other. A lone screw that lands on another
# body queues one body further back along its own axis, which is a move only IT
# makes; a screw in a group may not, because a queued screw is a screw a beat
# out of time. What the group does instead is take a LONGER beat, all of it at
# once, until every one of its screws has its own paper. Four 5x40 and an angle
# in the stub-foot corner of step 5 need the second beat; J12's two need the
# first.
#
# HOW LONG THE BEAT IS. EXPLODE_PLATE_FRAC, and it came down from 0.055 of the
# page's short side to 0.024 - 61 mm to 27 mm on the step-1 page - because a
# group whose every step is longer than the parts in it has stopped being one
# unit. At 61 mm the J12 corner spread a leash, a bracket and two screw hops
# over more than 200 mm of paper, and the reader met four objects scattered
# round a corner instead of one corner coming apart. The beat is now shorter
# than the 40 mm screws it spaces: the bracket sits just clear of its seat,
# each screw just clear of the bracket, and seat, bracket and points are inside
# one glance. Nothing else about the rule moved - the steps are still equal,
# still measured off the ink, and a group that needs room still buys it by
# taking a LONGER beat rather than by breaking the rhythm.
#
# The LADDER grew two rungs when the base shrank, and it had to: every rung is
# a multiple of the base, so a base cut to 44 % cuts the reach of all of them
# to 44 %. The stub-foot corner on step 5 - four 5x40 and an angle - needs
# about 86 mm before its own screws are clear of each other, and 86 mm was the
# second rung of a 61 mm beat where it is the fifth of a 27 mm one. Same
# ratios, same rule, two more places to go; what a group may never do is take
# a beat that is not one of these.
BRACKET_HOPS = (1.0, 1.4, 1.9, 2.5, 3.2, 4.0)


def group_shift(view, f, d):
    """Where a screw in a bracket group sits, in MODEL space, at rhythm `d`.

    One function, because the answer is needed twice - once to pick the beat
    that gets the group's screws off each other, and again when the screw is
    actually drawn - and two versions of it would be two explosions.
    """
    dx, dy = view.dir_xy(f["direction"])
    nrm = math.hypot(dx, dy)
    if nrm < AXIS_ON_PAGE:
        # Head on: a ringed dot has no axis to travel down and does not move.
        return (0.0, 0.0, 0.0)
    blen = max(f["length"] * nrm, foreshorten_floor(f["length"]))
    return tuple(-c * ((blen + d) / nrm) for c in f["direction"])


def float_plate(occ, view, plate, screws, riders, hop):
    """The group's whole explosion: (page offset, rhythm d). R1 and R9.

    The DIRECTION is given - the caller does not get a vote and neither does
    the paper - so the only thing left to choose is the distance, and that is a
    single run of layout.place() over candidates strung out along that one
    line. A bracket that finds no room simply goes further out; it never leans,
    for the same reason a screw never does.

    The distance comes back with the offset because it is not the bracket's
    private business any more: it is the group's rhythm, and the screws that
    ride on this bracket are spaced by the same number (R9). `riders` is the
    set of them the page is actually going to draw, and a beat that would land
    two of those on top of each other is struck off the list before the paper
    is consulted at all: R2 is not negotiable, and the group has a way of
    obeying it that does not break the rhythm.
    """
    ux, uy = disassembly_dir(view, plate, screws)
    pts = plate_page_points(view, plate)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    home = _centroid(pts)
    foot = (max(xs) - min(xs), max(ys) - min(ys))

    def clashes(d):
        poff = (ux * d, uy * d)
        caps = [body_capsule(view, f, group_shift(view, f, d), poff)
                for f in riders]
        return any(capsules_overlap(caps[i], caps[j])
                   for i in range(len(caps)) for j in range(i + 1, len(caps)))

    beats = [k for k in BRACKET_HOPS if not clashes(hop * k)] or [
        BRACKET_HOPS[-1]]
    cands = [(home[0] + ux * hop * k, home[1] + uy * hop * k) for k in beats]
    at = layout.place(cands, foot, occ, tether=home, pull=1.0 / (hop * 6.0))
    # Off the multiplier rather than off the winning point, so the rhythm is
    # exactly the number both halves of the chain are built from.
    k = beats[min(range(len(cands)),
                  key=lambda i: (cands[i][0] - at[0]) ** 2
                  + (cands[i][1] - at[1]) ** 2)]
    return ((ux * hop * k, uy * hop * k), hop * k)


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


# A LONGER HOP HAS TO BUY SOMETHING. clear_back() returns the shortest hop
# that clears `want`; the question this answers is what it should do when NO
# hop on the axis clears it, which is the normal case rather than the odd one.
# A screw driven along a rail travels inside that rail's own silhouette for the
# whole of its journey, and on a page where every line is black - step 1 has no
# ghosted layer at all - there is no white anywhere on that axis to find.
#
# The old answer was "then take the roomiest", with no floor under how much
# roomier. Measured on step 1: the four candidates for a 6x90 into the post
# offered 0.78, 0.12, 1.03 and 1.06 mm of paper, so the screw went 80 mm
# further out than it had to in exchange for a quarter of a millimetre nobody
# can see - and it landed in the slot the NEXT screw into the same corner
# wanted, which then queued a whole body length past both of them. Two screws
# 25 mm apart in the model ended up 107 and 240 mm out.
#
# A hop the reader can see has to buy clearance the reader can see. A candidate
# only displaces the incumbent by beating it by a quarter of what was asked
# for; short of that the screw stays at the beat it started on and the drawing
# keeps its point next to its hole.
ROOM_GAIN = 0.25


def clear_back(occ, hole, u, body, base, step, want, tries=4):
    """How far back along its own axis an exploded screw has to sit.

    The one degree of freedom a screw is allowed - the same freedom, and the
    same only freedom, that float_plate() leaves a bracket. Its body is
    sampled at each candidate distance in the occupancy field and the SHORTEST
    hop that finds white paper for the whole of it wins; if none does, the
    shortest one that is meaningfully roomier than the first does, and where
    nothing is - see ROOM_GAIN - the first one stands. Only the BLACK line work
    counts: a screw is welcome to lie across the ghosted frame that is already
    standing, and on a page where everything is new there is nothing to be
    precious about anyway.

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
        if best is None or room > best + want * ROOM_GAIN:
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


def screw_shape(view, anchor, direction, length, d, fatten=SCREW_FATTEN,
                name=None, px_per_unit=None, threads=True):
    """(outline, head-end, tip-end, unit, drawn length) for one screw.

    `outline` is the silhouette in page coordinates: head, countersink,
    shank, thread, point - laid out along the PROJECTED DRIVE AXIS and
    nowhere else. There is no upright screw glyph in this function and there
    must never be one: a 6x90 driven at 65 deg into a corner is drawn at
    65 deg, because the angle is the instruction. The only licence taken is
    the diameter.

    `None` when the screw points straight at the reader and has no length on
    the page at all - the caller draws a ringed dot instead, which is the
    head-on convention and, being a circle, cannot point the wrong way.
    """
    tip3 = tuple(a + c * length for a, c in zip(anchor, direction))
    p0, p1 = view.xy(anchor), view.xy(tip3)
    ux, uy, L = _unit2(p0, p1)
    if L < length * AXIS_ON_PAGE:
        return None, p0, p1, (0.0, 0.0), 0.0
    L = max(L, foreshorten_floor(length))
    return (screw_outline(p0, (ux, uy), L, d, fatten, name, px_per_unit,
                          threads), p0, p1, (ux, uy), L)


def screw_outline(p0, u, L, d, fatten=None, name=None, px_per_unit=None,
                  threads=True):
    """The silhouette itself, and it is not this file's drawing any more.

    ONE SCREW LANGUAGE. The shape comes from gen_glyphs.screw_profile() - the
    same description the catalogue glyph in the inset panel and in the step's
    own fastener table is drawn from - mapped onto the projected drive axis.
    What used to be here was a seven-point capsule with a flange at one end
    and a spike at the other, and at page size it read as an ARROW: the page
    said "dart" where the panel beside it said "screw", and the reader has
    only the shape to recognise the part by.

    The one licence is still the diameter: `d * fatten` is what the profile is
    built at, and it is the NOMINAL diameter, so the head comes out
    gen_glyphs.HEAD_DIA_RATIO times that exactly as it does in the glyph.

    `px_per_unit` is how many device pixels one millimetre of this page
    becomes, and it decides one thing only: whether the thread is drawn at
    all. See gen_glyphs.thread_pitch() - a tooth finer than a few pixels is
    not a thread, it is a furry edge, and the profile then falls back on its
    own envelope. Same head, same core, same point; no wave.
    """
    import gen_glyphs
    fatten = SCREW_FATTEN if fatten is None else fatten
    w = d * fatten
    frac, pointed = gen_glyphs.screw_style(name) if name else (0.70, True)
    pitch = 0.0
    if threads and px_per_unit:
        # The TRUE diameter, not the fattened one: the licence this drawing
        # takes is width, and a thread's pitch is a length along the axis.
        # See gen_glyphs.thread_pitch().
        pitch = gen_glyphs.thread_pitch(d, L * frac, px_per_unit)
    prof, _bb = gen_glyphs.screw_profile(w, L, frac, pointed, pitch)
    ux, uy = u

    def P(t, q):
        return (p0[0] + ux * t - uy * q, p0[1] + uy * t + ux * q)

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
                                name=f["name"], mark=mark_owner(m),
                                letter=m.get("letter"),
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

    outline, p0, p1, u, L_drawn = screw_shape(
        view, anchor, f["direction"], f["length"], f["d"],
        name=f["name"], px_per_unit=page.px_per_unit,
        threads=thread_cues(m.get("code")))
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
    # It comes off the MARK, which got it from the page, which got it from the
    # step - and it is None on a page whose screws separate by shape, where
    # this call paints white and the silhouette stands bare.
    paint = page.fill_paint(m.get("code"), f["d"] * SCREW_FATTEN)
    if outline is None:
        # Straight at the reader: the drawing convention for an axis with no
        # length on the page is a ringed dot, and it is the same mark whether
        # the screw is in or out.
        ring = m.get("ring") or T.RING_R
        page.circle(p0, ring, fill=paint, width=T.W_SCREW)
        page.dot(p0, T.RING_DOT_R)
        # The ring IS the drawn body on this page - there is no axis to draw -
        # so it goes into the record as one. A badge has to be able to touch
        # it, and R5 has to be able to measure against it.
        page.record.append(dict(kind="screw", owner=id(f), jid=f["jid"],
                                name=f["name"], mark=mark_owner(m),
                                letter=m.get("letter"),
                                points=[p0], axis=None,
                                head_r=drawn_head_r(f["d"]),
                                cap=(p0, p0, ring)))
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
    # Straight off the polygon: the profile's first and last points are the
    # two corners of the head face, so their midpoint is the head centre and
    # the point is that far along the drawn axis. Not an index into the
    # outline any more - the thread makes it a different length on every page.
    head_c = ((outline[0][0] + outline[-1][0]) / 2,
              (outline[0][1] + outline[-1][1]) / 2)
    body = (head_c, (head_c[0] + u[0] * L_drawn, head_c[1] + u[1] * L_drawn))
    page.record.append(dict(kind="screw", owner=id(f), jid=f["jid"],
                            name=f["name"], mark=mark_owner(m),
                            letter=m.get("letter"),
                            points=list(outline), axis=body,
                            # The width the body was drawn with, beside the
                            # length it was drawn at: the two together are what
                            # says whether this is still a screw (STUB_ASPECT).
                            head_r=drawn_head_r(f["d"]),
                            cap=body_capsule(view, f, shift, page_off,
                                             ring=m.get("ring"))))
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
        # The narrowest thing a fill code has been asked to cross on this
        # page, in model millimetres, and how many pixels one of those
        # millimetres becomes in the PNG. Together they are the two numbers
        # gen_glyphs.fill_metrics() needs, and they are collected as the page
        # is drawn rather than assumed, because the answer belongs to what was
        # actually put on the paper.
        self.fill_spans = []
        self.px_per_unit = None
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

    def clip_rect_begin(self, box):
        """Everything until clip_rect_end() is cut to a rectangle - the crop
        panels the V2 mechanism sheets are made of."""
        self._clips = getattr(self, "_clips", 0) + 1
        cid = f"crop{self._clips}"
        x, y, w, h = box
        self.body.append(
            f'<defs><clipPath id="{cid}"><rect x="{_f(x)}" '
            f'y="{_f(-(y + h))}" width="{_f(w)}" height="{_f(h)}"/>'
            f'</clipPath></defs><g clip-path="url(#{cid})">')

    def clip_rect_end(self):
        self.body.append("</g>")

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

    def circle(self, c, r, fill="none", stroke=INK, width=None, dash=None):
        width = T.W_RULE if width is None else width
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(
            f'<circle cx="{_f(c[0])}" cy="{_f(-c[1])}" r="{_f(r)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{_f(width)}"{d}/>')

    def dot(self, c, r, colour=INK):
        self.body.append(
            f'<circle cx="{_f(c[0])}" cy="{_f(-c[1])}" r="{_f(r)}" '
            f'fill="{colour}"/>')

    def text(self, p, s, size, anchor="start", weight="normal", colour=INK,
             rotate=None, halo=None):
        """One line of type. `rotate` turns it about its own anchor - degrees,
        clockwise on the page, so a dimension figure can lie along its axis in
        an axonometric - and `halo` knocks the line work out from under it
        with a white stroke of that width. Both are opt-in and neither changes
        a byte of the tag when it is not asked for."""
        s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        extra = ""
        if halo:
            extra += (f' paint-order="stroke" stroke="#ffffff" '
                      f'stroke-width="{_f(halo)}" stroke-linejoin="round"')
        if rotate is not None:
            extra += (f' transform="rotate({_f(rotate)} {_f(p[0])} '
                      f'{_f(-p[1])})"')
        self.body.append(
            f'<text x="{_f(p[0])}" y="{_f(-p[1])}" font-family="{FONT}" '
            f'font-size="{_f(size)}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{colour}"{extra}>{s}</text>')

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

    # -- TYPE THAT HAS TO FIT ----------------------------------------------
    # 0.52 em per character is the same average the schematics family measures
    # its notes with (tools/schematic.py). It is an average and it is meant to
    # be: a note that runs off the sheet is the one drawing fault a proof
    # render always shows and a code review never does, and the only way to
    # not have it is to ask how wide the column is before the line is written.
    CHAR_W = 0.52

    def wrap(self, text, width, size):
        """Greedy wrap to a column measured in PAGE UNITS, not characters."""
        cw = size * self.CHAR_W
        out, row = [], ""
        for word in text.split():
            cand = (row + " " + word).strip()
            if row and len(cand) * cw > width:
                out.append(row)
                row = word
            else:
                row = cand
        if row:
            out.append(row)
        return out

    # -- A DIMENSION, AND IT IS THE ONLY WAY THIS HOUSE DRAWS ONE ----------
    # The idiom is the one a flat-pack sheet uses, and it is four rules:
    #   * a DOUBLE arrow - a solid head at each end of one line, so the figure
    #     is a span and not a leader pointing at something;
    #   * THIN, DASHED witness lines that run out along an AXIS of the
    #     drawing, never square to the paper. In an axonometric the paper has
    #     no axes of its own, so a helper line that does not follow one of the
    #     model's three is a line the reader cannot place in space;
    #   * the figure BIG, BOLD, WITH ITS UNIT, sitting on the arrow itself
    #     with the line knocked out from under it; and
    #   * the figure LYING ALONG ITS OWN AXIS, so a width reads along the
    #     width and a height stands up.
    # `p0`/`p1` are the two ends of the thing being measured, in the page's
    # own frame; `axis` is the page-space direction the witness lines run out
    # along and `off` how far out along it the dimension line stands. off = 0
    # is the local detail dimension - no witness lines, the arrow drawn on the
    # part itself.
    #
    # It returns a RECORD, and the record is the point: it carries the indices
    # of the two elements that were emitted, so the assert that checks this
    # drawing reads the ink rather than the intention.
    def dimension(self, p0, p1, label, axis=None, off=0.0, size=None,
                  colour=INK, weight="bold", at=0.5):
        size = T.S_DIM if size is None else size
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        span = math.hypot(dx, dy)
        if span < 1e-9:
            return None
        ux, uy = dx / span, dy / span
        if axis is None:
            nx, ny = -uy, ux
        else:
            an = math.hypot(axis[0], axis[1]) or 1.0
            nx, ny = axis[0] / an, axis[1] / an
        a = (p0[0] + nx * off, p0[1] + ny * off)
        b = (p1[0] + nx * off, p1[1] + ny * off)
        w_dim = size * 0.085
        if abs(off) > 1e-9:
            s = 1.0 if off >= 0.0 else -1.0
            gap, over = size * 0.30, size * 0.60
            dash = f"{_f(size * 0.34)} {_f(size * 0.30)}"
            for tip, foot in ((p0, a), (p1, b)):
                self.line((tip[0] + nx * gap * s, tip[1] + ny * gap * s),
                          (foot[0] + nx * over * s, foot[1] + ny * over * s),
                          colour, w_dim * 0.60, dash=dash)
        head = size * 0.95
        # THE FIGURE SITS IN THE LINE, NOT ON IT. A white halo hides the
        # stroke under a glyph and cannot hide it in the SPACE between two
        # words - which is exactly where "1990 mm" has one - so the line is
        # cut instead, and the halo is left as a small courtesy to whatever
        # else the arrow happens to cross. One <path> either way: the assert
        # that measures this arrow reads its first and last point.
        half = len(label) * size * self.CHAR_W * 0.5
        # `at` is where along the arrow the figure sits, and it is a fraction
        # rather than the middle because the middle is sometimes where a post
        # is. dim_seat() picks it; the default is the middle.
        mid = (a[0] + ux * span * at, a[1] + uy * span * at)
        cut = half + size * 0.36
        i_line = len(self.body)
        room = min(at, 1.0 - at) * span > cut + head
        if room:
            self.polylines([[a, (mid[0] - ux * cut, mid[1] - uy * cut)],
                            [(mid[0] + ux * cut, mid[1] + uy * cut), b]],
                           colour, w_dim)
        else:
            self.line(a, b, colour, w_dim)
        # Point OUT: the head's tip sits on the witness line and its body lies
        # inside the span, so the pair reads |<--->| and not >--< .
        for tip, sgn in ((a, -1.0), (b, 1.0)):
            self._dim_head(tip, (ux * sgn, uy * sgn), head, colour)
        # The figure reads left to right whatever the axis does, so the
        # direction is folded into the right half-plane before it is used.
        rx, ry = (ux, uy) if ux >= 0.0 else (-ux, -uy)
        i_text = len(self.body)
        # A span too short to cut keeps its line whole and the figure steps
        # ASIDE - the drawing office's own answer, and the only one that
        # works: a white halo hides the stroke under a glyph and cannot hide
        # it in the space between two words.
        drop = size * (0.34 if room else 1.05)
        base = (mid[0] + ry * drop, mid[1] - rx * drop)
        self.text(base, label, size, anchor="middle", weight=weight,
                  colour=colour, rotate=-math.degrees(math.atan2(ry, rx)),
                  halo=size * 0.22)
        # WHAT THIS DIMENSION PUT ON THE PAPER, so the next one can be told to
        # keep off it: the arrow, and the four corners of the box the figure
        # occupies - round where the figure actually ENDED UP, which is not
        # the middle of the arrow when it had to step aside.
        step = drop - size * 0.34
        c = (mid[0] + ry * step, mid[1] - rx * step)
        return {"line": i_line, "text": i_text, "a": a, "b": b,
                "label": label, "u": (ux, uy),
                "ink": [[a, b],
                        [(c[0] - rx * half - ry * size,
                          c[1] - ry * half + rx * size),
                         (c[0] + rx * half - ry * size,
                          c[1] + ry * half + rx * size),
                         (c[0] + rx * half + ry * size,
                          c[1] + ry * half - rx * size),
                         (c[0] - rx * half + ry * size,
                          c[1] - ry * half - rx * size)]]}

    def _dim_head(self, tip, direction, length, colour):
        """A solid arrow head - the flat-pack kind, not the open one a wood
        part being brought together gets."""
        ux, uy = direction
        back = (tip[0] - ux * length, tip[1] - uy * length)
        wing = length * 0.30
        self.poly([tip,
                   (back[0] - uy * wing, back[1] + ux * wing),
                   (back[0] + uy * wing, back[1] - ux * wing)],
                  fill=colour, stroke=colour, width=length * 0.06)

    # -- AND THE OTHER KIND OF DIMENSION, WHICH IS A WORD -------------------
    # Zero is a measurement too, and an arrow with «0 mm» on it is a drawing
    # lying about what it knows: nobody sets a rail flush by measuring nothing.
    # Two edges that land in line are drawn as what they are - a SIGHT LINE
    # lying IN the plane the two share, a short bar across it where each edge
    # is, and the word between them. Same pen, same type size and the same
    # record as dimension(), so the assert that takes an arrow back off the
    # paper takes this one back too.
    def flush(self, p0, p1, label, size=None, colour=INK):
        size = T.S_DIM if size is None else size
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        span = math.hypot(dx, dy)
        if span < 1e-9:
            return None
        ux, uy = dx / span, dy / span
        nx, ny = -uy, ux
        w_dim = size * 0.085
        half = len(label) * size * self.CHAR_W * 0.5
        mid = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
        cut = half + size * 0.36
        i_line = len(self.body)
        room = span * 0.5 > cut + size * 0.4
        dash = f"{_f(size * 0.34)} {_f(size * 0.30)}"
        if room:
            self.polylines([[p0, (mid[0] - ux * cut, mid[1] - uy * cut)],
                            [(mid[0] + ux * cut, mid[1] + uy * cut), p1]],
                           colour, w_dim * 0.60, dash=dash)
        else:
            self.line(p0, p1, colour, w_dim * 0.60, dash=dash)
        bar = size * 0.55
        for tip in (p0, p1):
            self.line((tip[0] - nx * bar, tip[1] - ny * bar),
                      (tip[0] + nx * bar, tip[1] + ny * bar), colour, w_dim)
        rx, ry = (ux, uy) if ux >= 0.0 else (-ux, -uy)
        i_text = len(self.body)
        drop = size * (0.34 if room else 1.05)
        base = (mid[0] + ry * drop, mid[1] - rx * drop)
        self.text(base, label, size, anchor="middle", weight="bold",
                  colour=colour, rotate=-math.degrees(math.atan2(ry, rx)),
                  halo=size * 0.22)
        c = (mid[0] + ry * (drop - size * 0.34),
             mid[1] - rx * (drop - size * 0.34))
        return {"line": i_line, "text": i_text, "a": p0, "b": p1,
                "label": label, "u": (ux, uy),
                "ink": [[p0, p1],
                        [(c[0] - rx * half - ry * size,
                          c[1] - ry * half + rx * size),
                         (c[0] + rx * half - ry * size,
                          c[1] + ry * half + rx * size),
                         (c[0] + rx * half + ry * size,
                          c[1] + ry * half - rx * size),
                         (c[0] - rx * half + ry * size,
                          c[1] - ry * half - rx * size)]]}

    def embed_svg(self, path, x, y, w, h):
        """Drop one of the fastener glyphs in, at its own aspect ratio."""
        with open(path, encoding="utf-8") as fh:
            self.embed_svg_text(fh.read(), x, y, w, h)

    def embed_svg_text(self, raw, x, y, w, h):
        """The same, from SVG already in hand rather than off disk."""
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

    def fill_paint(self, code, span=None):
        """The paint for one fill code, and the pattern registered with it.

        The page carries the <defs> because the pattern is in the PAGE's
        coordinate system: the code has to look the same on a screw driven
        left as on one driven down, so it is the paper that is hatched and not
        the screw.

        `span` is how wide the thing being filled is - the drawn diameter of
        the fastener, in model millimetres. It is the shape half of
        gen_glyphs.fill_metrics(); the resolution half is the page's own
        px_per_unit. Nothing here picks a period, and nothing here may.
        """
        if code is None:
            return "#ffffff"
        import gen_glyphs
        self.fills.add(code)
        if span:
            self.fill_spans.append(float(span))
        return gen_glyphs.fill_paint(code)

    # The width a fill has to cross when the page never told us: the thinnest
    # screw the manual uses, at its drawn diameter. It is a floor on the
    # SHAPE term only - the resolution term still applies - and it exists so
    # that a page which fills something without declaring its width cannot end
    # up with a finer pattern than the page next to it.
    FILL_SPAN_FLOOR = 5.0 * SCREW_FATTEN

    def _defs(self):
        if not self.fills - {"solid", "open"}:
            return ""
        import gen_glyphs
        assert self.px_per_unit, (
            "siden fyller noe med en kode, men vet ikke hvor mange piksler "
            "per millimeter den rasterres i - sett Page.px_per_unit før "
            "write()")
        span = min(self.fill_spans) if self.fill_spans else self.FILL_SPAN_FLOOR
        base, t = gen_glyphs.fill_metrics(span, self.px_per_unit)
        return gen_glyphs.fill_defs(base, t) + "\n"

    def write(self, path, px_width=None):
        """The SVG. `px_width` is the width the PNG beside it is rastered at,
        and it is not decoration: the fill code's period has a floor in DEVICE
        PIXELS, so the page cannot choose its patterns without knowing what it
        is about to be reduced to."""
        if px_width:
            self.px_per_unit = px_width / self.w
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="{_f(self.x0)} {_f(-self.y1)} {_f(self.w)} '
                f'{_f(self.h)}">')
        bg = (self._defs()
              + f'<rect x="{_f(self.x0)}" y="{_f(-self.y1)}" '
              f'width="{_f(self.w)}" height="{_f(self.h)}" fill="#ffffff"/>')
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head + "\n" + bg + "\n" + "\n".join(self.body)
                     + "\n</svg>\n")


# ---------------------------------------------------------------------------
# WHERE A DIMENSION LINE STANDS, AND WHY IT IS NOT A NUMBER SOMEBODY LIKED
# ---------------------------------------------------------------------------
# A dimension stands off the drawing far enough to clear it and no further.
# That is a measurement, not a taste, and it is made here: how far out along
# the witness axis the far side of the line work reaches, WITHIN the stretch
# the dimension actually spans, plus one margin. Anything outside that stretch
# is not in the way - a post top two metres along the bed has nothing to say
# about where a floor dimension at the other end may sit - and leaving it out
# is the whole difference between a snug sheet and one with a hand's width of
# white round it.
#
# `art` grows as the sheet is drawn: every dimension already placed goes back
# in, so the next one clears its neighbour by the same rule that cleared it of
# the bed. Nothing on the sheet is positioned by hand.
def dim_offset(art, p0, p1, axis, margin, slack=0.0):
    ux, uy = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    an = math.hypot(axis[0], axis[1]) or 1.0
    nx, ny = axis[0] / an, axis[1] / an
    lo = min(ux * p0[0] + uy * p0[1], ux * p1[0] + uy * p1[1]) - slack
    hi = max(ux * p0[0] + uy * p0[1], ux * p1[0] + uy * p1[1]) + slack
    base = max(nx * p0[0] + ny * p0[1], nx * p1[0] + ny * p1[1])
    out = base
    # SEGMENTS, not vertices. Almost every edge in this bed is a straight line
    # and therefore two points, so a 1990 mm rail that runs clean through the
    # stretch a dimension spans has NEITHER END in it - ask the vertices and
    # the rail is not there, and the dimension line lands on top of it.
    for pl in art:
        for a, b in zip(pl, pl[1:]):
            ta, tb = ux * a[0] + uy * a[1], ux * b[0] + uy * b[1]
            va, vb = nx * a[0] + ny * a[1], nx * b[0] + ny * b[1]
            d = tb - ta
            if abs(d) < 1e-12:
                if not (lo <= ta <= hi):
                    continue
                cand = max(va, vb)
            else:
                s0, s1 = (lo - ta) / d, (hi - ta) / d
                if s0 > s1:
                    s0, s1 = s1, s0
                s0, s1 = max(0.0, s0), min(1.0, s1)
                if s1 < s0:
                    continue
                cand = max(va + (vb - va) * s0, va + (vb - va) * s1)
            if cand > out:
                out = cand
    return out - base + margin


# WHERE ALONG THE ARROW THE FIGURE SITS. The middle, unless a post is in the
# middle. This is the same scoring loop layout.place() is: a FIXED, ORDERED
# list of candidates, one cost each - how many edges of the drawing cross the
# box the figure would occupy - and `min` over (score, index), so the middle
# wins every tie and the sheet comes out the same way twice.
#
# It is here rather than in the caller because it is a rule about dimensions
# and not about beds: an outboard dimension standing in clear paper scores
# zero everywhere and keeps the middle, and a local one drawn across the work
# steps aside by exactly as much as it has to.
DIM_SEATS = (0.5, 0.62, 0.38, 0.74, 0.26)


def dim_seat(art, p0, p1, w, h, fracs=DIM_SEATS):
    ux, uy = p1[0] - p0[0], p1[1] - p0[1]
    span = math.hypot(ux, uy)
    if span < 1e-9:
        return 0.5
    ux, uy = ux / span, uy / span
    nx, ny = -uy, ux
    best = None
    for i, frac in enumerate(fracs):
        c = (p0[0] + ux * span * frac, p0[1] + uy * span * frac)
        t_c, v_c = ux * c[0] + uy * c[1], nx * c[0] + ny * c[1]
        t0, t1 = t_c - w / 2.0, t_c + w / 2.0
        v0, v1 = v_c - h / 2.0, v_c + h / 2.0
        score = 0
        for pl in art:
            for a, b in zip(pl, pl[1:]):
                ta, tb = ux * a[0] + uy * a[1], ux * b[0] + uy * b[1]
                va, vb = nx * a[0] + ny * a[1], nx * b[0] + ny * b[1]
                d = tb - ta
                if abs(d) < 1e-12:
                    if not (t0 <= ta <= t1):
                        continue
                    lo, hi = min(va, vb), max(va, vb)
                else:
                    s0, s1 = (t0 - ta) / d, (t1 - ta) / d
                    if s0 > s1:
                        s0, s1 = s1, s0
                    s0, s1 = max(0.0, s0), min(1.0, s1)
                    if s1 < s0:
                        continue
                    ea, eb = va + (vb - va) * s0, va + (vb - va) * s1
                    lo, hi = min(ea, eb), max(ea, eb)
                if hi >= v0 and lo <= v1:
                    score += 1
        if best is None or score < best[0]:
            best = (score, i, frac)
    return best[2]


_DIM_PT = re.compile(r"(-?[\d.]+),(-?[\d.]+)")


def dim_ink(page, rec):
    """The two ends of a dimension line, taken back OUT of the emitted tag.

    Page draws with y flipped, so it is flipped back: what comes out is the
    arrow as it will be on paper, in the drawing's own frame, and it is the
    only thing an assert about this sheet is allowed to measure."""
    el = page.body[rec["line"]]
    i = el.index('d="') + 3
    d = el[i:el.index('"', i)]
    return [(float(a), -float(b)) for a, b in _DIM_PT.findall(d)]


# ---------------------------------------------------------------------------
# X15 - THE PLACEMENT MEASURES ON A STEP SHEET
# ---------------------------------------------------------------------------
# WHICH numbers a step owes is not this file's business: tools/step_dims.py
# derives them off the model's own solids and joints, and a page that drew one
# more or one less than the list says would be a page disagreeing with the bed.
# What IS this file's business is where on the paper they go, and that is the
# same rule the measurement sheet composes itself by - every arrow stands off
# the line work as far as it has to to clear it IN THE STRETCH IT SPANS, plus
# one margin, and every arrow already placed goes back into the line work
# before the next one asks.
#
# A step page is a crowded page, though, and the sheet has two extra decisions
# to make that the measurement sheet does not.
#
#   WHICH WAY OUT. A height on an axonometric can leave the drawing along
#   either of the two axes that are not its own, in either direction, and the
#   four answers are not equally good on a page that already carries a
#   fastener list, a magnifier and a mirror note. So all four are measured and
#   the shortest way out wins - the same rule again, asked once per candidate
#   - and then every later measure on the same axis FOLLOWS it, so they come
#   out as one column and not as a fan.
#
#   HOW FAR OUT WHEN THEY SHARE A DATUM. Two heights off one post top are
#   COLLINEAR, and dim_offset() clears the line work rather than the
#   neighbour: translate both spans and they land on each other at the post.
#   So the sheet keeps a high-water mark per axis and each further measure
#   stands one margin outside every one already placed.
STEP_DIM_MARGIN = 1.15          # x the figure size: air round a placement mark


# An axis a camera looks straight down has no direction on the paper: its
# projection is a couple of thousandths of a millimetre pointing wherever the
# rounding went. Normalise that and a witness line sets off in a random
# direction, which is how four ladder heights ended up stacked on top of one
# another down the middle of a stile. A quarter of the model unit is the
# floor: below it the axis is not a way out of the drawing.
AXIS_ON_PAPER = 0.25
# How far off parallel a witness axis has to be from the arrow it carries
# before it counts as a way OUT of the drawing: the sine of the angle between
# them, so 0.35 is about 20 degrees.
ACROSS_THE_SPAN = 0.35
# How long a flush sight line is allowed to be, in figure heights.
FLUSH_REACH = 7.0


def _dim_axis_candidates(view, axis):
    """The ways a measurement on this model axis can leave the drawing.

    Two per axis - out along it and back along it - over the two axes that are
    not its own, minus any the camera has flattened.
    """
    out = []
    for j in range(3):
        if j == axis:
            continue
        for sgn in (1.0, -1.0):
            v = [0.0, 0.0, 0.0]
            v[j] = sgn
            d = view.dir_xy(tuple(v))
            if math.hypot(d[0], d[1]) > AXIS_ON_PAPER:
                out.append((j, sgn, d))
    return out


def _pick_alt_model(view, rec, box):
    """Which of a mirrored measure's places this page can actually see.

    Left and right measure the same, so the record carries every place it
    could be drawn; the sheet takes the one inside its own crop, and where
    several are inside, the nearest end of the page - which on a half view is
    the end drawn at full size.
    """
    best = None
    x0, y0, x1, y1 = box
    for p0, p1 in rec["alts"]:
        a, b = view.xy(p0), view.xy(p1)
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        inside = (x0 <= a[0] <= x1 and x0 <= b[0] <= x1
                  and y0 <= a[1] <= y1 and y0 <= b[1] <= y1)
        key = (0 if inside else 1, round(mid[0], 3), round(mid[1], 3))
        if best is None or key < best[0]:
            best = (key, p0, p1)
    return best[1], best[2]


def _pick_alt(view, rec, box):
    p0, p1 = _pick_alt_model(view, rec, box)
    return view.xy(p0), view.xy(p1)


def plan_step_dims(view, recs, art, size, box):
    """Where every placement measure this step owes goes on the paper.

    Returns the plans in drawing order, with the page rectangle they need.
    Nothing is drawn: the page has to be told how big it is before it exists,
    and a measurement standing off the bed is part of how big it is.
    """
    margin = size * STEP_DIM_MARGIN
    field = list(art)
    plans, ways, high = [], {}, {}
    # Short spans first: the ones that hug the drawing take the paper nearest
    # it, and the long ones stand outside them - the way a drawing office
    # stacks a dimension.
    order = sorted(recs, key=lambda r: (
        math.hypot(*[a - b for a, b in zip(*_pick_alt(view, r, box))]),
        r["axis"], r["figure"]))
    for rec in order:
        p0, p1 = _pick_alt(view, rec, box)
        # A measure the camera has flattened cannot be drawn, and the step
        # still owes it - so this is an assert and not a `continue`: a page
        # that quietly dropped one would look exactly like a step that never
        # owed one, which is the whole failure mode X15 exists to close.
        m0, m1 = _pick_alt_model(view, rec, box)
        span = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        assert span > math.dist(m0, m1) * AXIS_ON_PAPER, \
            (f"steg {rec['n']}: {rec['family']} skylder «{rec['figure']}», men "
             f"målet står rett inn i kameraet fra denne vinkelen - det har "
             f"ingen lengde på papiret og kan ikke tegnes")
        if rec["kind"] == "flukt":
            # A SIGHT LINE IS A DIRECTION, NOT A DISTANCE. It says «this edge
            # is in line with that one», and once it has left the new piece
            # pointing at the other, every further millimetre of it is line
            # work laid over the drawing for nothing. So it is cut back to a
            # few figure heights: the end that MATTERS - the one on the wood
            # this step adds - stays where it is, and the assert reads it.
            keep = min(1.0, size * FLUSH_REACH / span)
            p0 = (p1[0] + (p0[0] - p1[0]) * keep,
                  p1[1] + (p0[1] - p1[1]) * keep)
            plan = dict(rec=rec, p0=p0, p1=p1, axis=None, off=0.0, at=0.5,
                        label=rec["figure"], ink=None, m0=m0, m1=m1)
        else:
            # THE WAY OUT MUST BE ACROSS THE MEASUREMENT, NOT ALONG IT. An
            # axis that projects parallel to the span carries the dimension
            # line further up its own arrow and no distance at all off the
            # drawing - which is how four ladder heights came out stacked on
            # top of one another down the middle of a stile.
            ux = (p1[0] - p0[0]) / span
            uy = (p1[1] - p0[1]) / span
            # THE FIGURE IS WIDER THAN THE GAP IT MEASURES, and that is the
            # normal case here: «14 mm» is five characters over a 14 mm span.
            # So the stretch the offset has to clear is not the arrow, it is
            # the arrow plus the figure standing beside it - otherwise the
            # measure clears a gap nothing is in and lands on the wood either
            # side of it.
            slack = (margin
                     + len(rec["figure"]) * size * Page.CHAR_W * 0.5)
            # TWO MEASURES OF THE SAME KIND LEAVE THE DRAWING THE SAME WAY.
            # The first one on an axis picks the shortest way out; every one
            # after it follows, and they stack in one column the way a drawing
            # office stacks them. Letting each choose for itself is worse than
            # untidy: two axes can project to page directions 40 degrees apart,
            # and then the second arrow only half clears the first and the two
            # come out lying on top of one another.
            best = None
            for _j, _sgn, d in ([(None, None, ways[rec["axis"]])]
                                if rec["axis"] in ways
                                else _dim_axis_candidates(view, rec["axis"])):
                dn = math.hypot(d[0], d[1])
                if abs(ux * d[1] - uy * d[0]) / dn < ACROSS_THE_SPAN:
                    continue
                off = dim_offset(field, p0, p1, d, margin, slack=slack)
                if best is None or off < best[0] - 1e-9:
                    best = (off, d)
            assert best is not None, \
                (f"steg {rec['n']}: {rec['family']} skylder «{rec['figure']}», "
                 f"men ingen av modellens akser går på tvers av målet på "
                 f"papiret - pila har ingen vei ut av tegningen")
            off, d = best
            ways[rec["axis"]] = d
            # AND A MEASURE OFF A SHARED DATUM STANDS OUTSIDE THE ONE BEFORE
            # IT. dim_offset() clears the LINE WORK in the stretch it spans,
            # which is the right question for a sheet whose dimensions point
            # in all directions and the wrong one for a column of them off one
            # post top: those are COLLINEAR, so a translated copy of the span
            # lands on top of its neighbour at the datum end however far out
            # its far end goes. The drawing office answer is a high-water mark
            # - each further dimension one margin outside every one already
            # placed, measured on the witness axis - and that is this.
            dn = math.hypot(d[0], d[1])
            nx, ny = d[0] / dn, d[1] / dn
            reach = min(nx * p0[0] + ny * p0[1], nx * p1[0] + ny * p1[1]) + off
            mark = high.get(rec["axis"])
            if mark is not None and reach < mark + margin:
                off += mark + margin - reach
            high[rec["axis"]] = max(
                max(nx * p[0] + ny * p[1] for p in (p0, p1)) + off,
                mark if mark is not None else -1e18)
            an = math.hypot(d[0], d[1])
            a = (p0[0] + d[0] / an * off, p0[1] + d[1] / an * off)
            b = (p1[0] + d[0] / an * off, p1[1] + d[1] / an * off)
            at = dim_seat(field, a, b,
                          len(rec["figure"]) * size * Page.CHAR_W, size * 1.1)
            plan = dict(rec=rec, p0=p0, p1=p1, axis=d, off=off, at=at,
                        label=rec["figure"], ink=None, m0=m0, m1=m1)
        # The ink this one is about to make, so the next one keeps off it:
        # the arrow WHERE IT WILL BE, and the witness lines that carry it out
        # there. The figure's own box comes back off the page when it is
        # actually drawn; here a margin's worth of air round the arrow stands
        # in for it, which is what STEP_DIM_MARGIN is.
        sx = sy = 0.0
        if plan["axis"]:
            an = math.hypot(*plan["axis"])
            sx = plan["axis"][0] / an * plan["off"]
            sy = plan["axis"][1] / an * plan["off"]
        a = (p0[0] + sx, p0[1] + sy)
        b = (p1[0] + sx, p1[1] + sy)
        plan["ink"] = [[a, b], [p0, a], [p1, b]]
        field += plan["ink"]
        plans.append(plan)
    return plans


def step_dim_bounds(plans, size):
    """The rectangle every planned measure needs, figures included.

    The pad is the longest figure on the sheet standing on end, because that
    is what it is: the type sits ON the arrow and turns with it, so a
    dimension at the edge of the page needs half a figure's length of paper
    whichever way round it ended up.
    """
    pts = [p for plan in plans for pl in plan["ink"] for p in pl]
    if not pts:
        return None
    pad = size * 1.0 + max(len(plan["label"]) for plan in plans) \
        * size * Page.CHAR_W * 0.5
    return (min(p[0] for p in pts) - pad, min(p[1] for p in pts) - pad,
            max(p[0] for p in pts) + pad, max(p[1] for p in pts) + pad)


def draw_step_dims(page, view, plans, size):
    """Draw them, and take every one of them back off the paper.

    The assert is the measurement sheet's: the arrow is measured ON THE PAPER,
    divided by the length one model millimetre has along that axis IN THIS
    CAMERA, and has to come out the number printed on it - which in turn has to
    be the model's own. A figure typed by hand, an arrow drawn to the wrong
    corner or a camera that stopped agreeing with itself all die here.
    """
    ink = []
    for plan in plans:
        rec = plan["rec"]
        if rec["kind"] == "flukt":
            out = page.flush(plan["p0"], plan["p1"], plan["label"], size=size)
        else:
            out = page.dimension(plan["p0"], plan["p1"], plan["label"],
                                 axis=plan["axis"], off=plan["off"],
                                 size=size, at=plan["at"])
        assert out is not None, \
            f"steg {rec['n']}: «{plan['label']}» kom ut med null lengde"
        _assert_step_dim(page, view, plan, out, size)
        ink += out["ink"]
    return ink


def _assert_step_dim(page, view, plan, out, size):
    rec = plan["rec"]
    pts = dim_ink(page, out)
    assert len(pts) in (2, 4), \
        (f"steg {rec['n']}: målpila for {rec['family']} kom ut som "
         f"{len(pts)} punkter, ikke 2 eller 4")
    dx, dy = pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]
    drawn = math.hypot(dx, dy)
    figure = dim_figure(page, out)
    assert figure == rec["figure"], \
        (f"steg {rec['n']}: det står «{figure}» på arket, men modellen "
         f"sier «{rec['figure']}»")
    if rec["kind"] == "flukt":
        # A sight line has no length to check - what it claims is a DIRECTION,
        # and that is what is asked of the ink.
        # The end that matters is the one ON THE NEW WOOD - the other has
        # been cut back to keep the line short - so that end has to sit on the
        # model's own edge, and the line has to POINT at the piece the edge is
        # in line with. Both are read off the emitted path.
        a, b = view.xy(plan["m0"]), view.xy(plan["m1"])
        end = min((pts[0], pts[-1]),
                  key=lambda p: math.hypot(p[0] - b[0], p[1] - b[1]))
        other = pts[-1] if end is pts[0] else pts[0]
        assert math.hypot(end[0] - b[0], end[1] - b[1]) < size * 0.05, \
            (f"steg {rec['n']}: flukt-linja for {rec['family']} starter et "
             f"sted modellen ikke har noen kant")
        wx, wy = a[0] - b[0], a[1] - b[1]
        gx, gy = other[0] - end[0], other[1] - end[1]
        wn, gn = math.hypot(wx, wy), math.hypot(gx, gy)
        assert gn > size * 0.5 and wn > 1e-9, \
            f"steg {rec['n']}: flukt-linja for {rec['family']} har ingen retning"
        assert (wx * gx + wy * gy) / (wn * gn) > 0.999, \
            (f"steg {rec['n']}: flukt-linja for {rec['family']} peker ikke mot "
             f"{rec['datum']}")
        return
    v = [0.0, 0.0, 0.0]
    v[rec["axis"]] = 1.0
    ax, ay = view.dir_xy(tuple(v))
    k = math.hypot(ax, ay)
    assert k > 1e-6, \
        (f"steg {rec['n']}: aksen til {rec['family']} står rett inn i "
         f"kameraet - målet har ingen lengde på papiret")
    assert abs(dx * ay - dy * ax) / k < size * 0.05, \
        f"steg {rec['n']}: målpila for {rec['family']} ligger ikke langs sin akse"
    mm = drawn / k
    printed = float(re.fullmatch(r"(\d+) mm", figure).group(1))
    assert abs(printed - rec["mm"]) <= 0.51, \
        (f"steg {rec['n']}: det står {printed:.0f} mm på arket, men modellen "
         f"sier {rec['mm']:.1f}")
    assert abs(mm - rec["mm"]) < size * 0.02 / k, \
        (f"steg {rec['n']}: pila for {rec['family']} er {mm:.1f} mm lang "
         f"gjennom kameraet, men det står {printed:.0f} mm på den")


def dim_figure(page, rec):
    """...and the number, out of the emitted <text>."""
    el = page.body[rec["text"]]
    return el[el.index(">", el.index("<text")) + 1:el.index("</text>")]


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
            list(G.parts) + [G.panel_bed] + list(G.battens_bed)
            + list(G.FOOTREST_PARTS) + [G.mattress]
            + list(G.CUSHIONS_BED)}


def full_bed(G):
    """The finished bed in bed mode - frame and loose panel, no mattress.

    The mattress is left out on purpose: it is bought, not built, and drawing
    it would only hide the slat field it lies on.
    """
    from build123d import Compound
    return Compound(children=list(G.parts) + [G.panel_bed]
                    + list(G.battens_bed) + list(G.FOOTREST_PARTS))


def table_bed(G):
    """The same bed with the panel up at 700 - the desk standing.

    The bed is one bed in two positions and the frame does not move; the
    difference is the plate and its four battens. This is the position the
    front of the book shows, because it is the one a still picture of the
    other position cannot tell you about (X9).
    """
    from build123d import Compound
    return Compound(children=list(G.parts) + [G.panel_table]
                    + list(G.battens_table) + list(G.FOOTREST_PARTS))


def comp(parts):
    from build123d import Compound
    return Compound(children=list(parts))


def badge(page, centre, letter, r=None, owner=None, body=None, leader=None,
          family=None, family_owners=None, family_lens=None):
    """One circled sans letter - the same mark the step table carries.

    `body` is the capsule of the element the badge is DRAWN FROM and `leader`
    the line to it where the badge could not sit on it. `family` is every
    capsule the badge stands for under R7, and `family_owners` their marks.
    All four go into the record because that is what assert_badges_anchored()
    and assert_badges_cover() re-measure: a badge is only a label if the
    reader can see WHAT it labels, and only complete if nothing it stands for
    is left without one.
    """
    r = T.BADGE_R if r is None else r
    page.circle(centre, r, fill="#ffffff", stroke=INK, width=T.W_RULE)
    page.text((centre[0], centre[1] - r * 0.40), letter,
              r * 1.20, anchor="middle", weight="bold")
    page.record.append(dict(kind="badge", owner=owner, letter=letter,
                            at=centre, r=r, body=body, leader=leader,
                            family=list(family) if family else None,
                            family_owners=list(family_owners)
                            if family_owners else None,
                            # The drawn lengths of everything this badge stands
                            # for - what assert_badges_homogeneous()
                            # re-measures
                            # the R7 amendment on.
                            family_lens=list(family_lens)
                            if family_lens else None))


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
# R6: off its own body, so it needs a leader. Allowed - a crowded corner has
# to be allowed something - but dearer than any amount of crowding, so the
# badge only ever leaves its screw when there is nowhere on it to sit.
CAP_NOCONTACT = 90.0
# R5: nearer somebody else's body than its own. Not a preference at all.
CAP_FOREIGN = 400.0
CAP_TAGS = ("panel", "mark", "badge")


# ---------------------------------------------------------------------------
# R10 - THE CHAIN CORRIDOR IS NOT A PLACE FOR A LETTER
# ---------------------------------------------------------------------------
# R9 draws a bracket group as ONE movement outward - seat, bracket, each of its
# screws, all in one beat - and the dotted links between them are the only
# thing on the paper saying that those four objects are one disassembly. A
# badge dropped into the middle of that fan cuts it. On the J12 corner it did
# exactly that: the D badge landed between the floated bracket and the 5x40
# coming up underneath it, so a reader following the chain met a letter where
# the next link should have been - and the one screw whose direction the corner
# exists to show, the one driven from BELOW, was the link that got hidden.
#
# It is not a crowding problem and it does not get a crowding weight. The
# corridor is a place a label may not be, and it is measured off the ink:
#
#     the group's LINKS - the recorded tethers themselves, seat to bracket and
#     bracket to each of its screws - and no badge circle may touch one.
#
# THE CONVEX REGION WAS WRITTEN FIRST, and the fan is why it is not what gets
# measured. The obvious statement of this rule is "stay off the convex hull of
# seat, bracket and screw points", and it turns out to be unsatisfiable for the
# one badge it was written for. A bracket's links leave in every direction at
# once - the seat on one side, its own screws on the other two or three - so
# the bracket lies INSIDE its own hull, and a badge outside the hull can never
# touch the bracket it names. R6 would have to be broken to obey R10.
#
# It is worse than that, and the placer said so when the hull rule was run: on
# the stub-foot corner of step 5 every candidate that got the D badge out of
# the hull put one of the corner's own 5x40 nearer to it than the bracket was,
# which is R5, which outranks everything here and should. The badge was priced
# back into the fan it had just been evicted from. A rule with no legal move is
# not a rule.
#
# The links carry the whole of what the region was for. A 49 mm badge in a
# corner whose beat is 27 mm cannot stand anywhere in the fan without lying
# across a link, so keeping off the links empties the fan by itself; and where
# there really is room between two links - a wide corner, a long beat - a
# letter in that gap covers nothing and hides nothing, which is the case the
# hull would have refused for no gain.
#
# What is NOT covered is a LEADER from a badge that had to step out: it ends on
# the body it names, so it reaches the chain by definition. A hairline touching
# a link is not a letter sitting on it, and a rule that forbade it would forbid
# labelling a bracket at all.
CAP_CORRIDOR = 250.0


def chain_corridors(page):
    """R10: every link of every bracket group on the page, as a segment.

    Read off page.record once the page has drawn all its fasteners and before
    it has placed a single caption - the one moment when every chain is whole
    and nothing is standing in one. Every badge is then asked about every link
    on the page: a letter belonging to one corner has no more business lying
    on another corner's chain than on its own.
    """
    return [r["seg"] for r in page.record
            if r["kind"] == "tether" and r.get("group") is not None]


def corridor_gap(p, links):
    """How far a point is from the nearest chain link."""
    return min((layout._seg_dist(p, a, b) for a, b in links),
               default=float("inf"))


def badge_gap_dir(view, poff, riders):
    """Which way a BRACKET's badge leaves the plate. R10's other half.

    A rule that only forbids is a rule the page obeys by failing. The badge of
    a bracket used to set off straight outboard, along the float - which is
    the one direction the group's own screws also travel in, so it walked down
    the middle of the fan and had to be evicted from every candidate it was
    offered. R5 then sent it back: a bracket is 40 mm of steel with four of its
    own screws round it, so any badge that leaves the plate has one of THEM
    nearer than the plate, and the two rules between them left the letter
    nowhere to stand.

    So the badge is given the one direction that is not a link. Every link
    leaves the plate on a known bearing - the leash back to the seat, and each
    rider backwards along its own drive axis - and those bearings are known
    here, before anything is drawn, because they are the group's own rule and
    not a property of the paper. The badge sets off through the middle of the
    WIDEST gap between two consecutive bearings: touching its plate, so R6 and
    R5 are satisfied where they are easiest to satisfy, and as far from every
    link as that corner allows, which is what R10 asks. Ties go to the lowest
    bearing, so the same corner always sends its letter the same way.
    """
    bearings = []
    if math.hypot(*poff) > 1e-9:
        bearings.append(math.atan2(-poff[1], -poff[0]))
    for f in riders:
        dx, dy = view.dir_xy(f["direction"])
        if math.hypot(dx, dy) > 1e-9:
            bearings.append(math.atan2(-dy, -dx))
    if not bearings:
        return (0.0, -1.0)
    bearings = sorted(round(b, 9) for b in bearings)
    best, at = None, bearings[0]
    for i, a in enumerate(bearings):
        nxt = bearings[i + 1] if i + 1 < len(bearings) else bearings[0] + 2.0 * math.pi
        if best is None or nxt - a > best:
            best, at = nxt - a, a + (nxt - a) / 2.0
    return (math.cos(at), math.sin(at))


def drawn_length(rec):
    """How long a drawn fastener came out on the paper, off its own record.

    `None` where the question does not apply - nothing was drawn, or what was
    drawn is a bracket, which is a plate and not an axis. `0.0` for the ringed
    dot a head-on screw becomes: it has no length, and that is not a small
    length, it is a different picture.
    """
    if rec is None or rec["kind"] != "screw":
        return None
    ax = rec.get("axis")
    if ax is None:
        return 0.0
    return math.hypot(ax[1][0] - ax[0][0], ax[1][1] - ax[0][1])


def cap_dist(p, cap):
    """Distance from a point to a drawn body's own edge, negative inside."""
    return layout._seg_dist(p, cap[0], cap[1]) - cap[2]


def cap_point(p, cap):
    """The point on a drawn body's axis nearest `p` - where a leader lands."""
    a, b = cap[0], cap[1]
    vx, vy = b[0] - a[0], b[1] - a[1]
    ll = vx * vx + vy * vy
    if ll < 1e-12:
        return a
    t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / ll
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return (a[0] + vx * t, a[1] + vy * t)


def mark_label(page, tail, direction, letter, occ=None, owner=None, body=None,
               family=None, corridors=None):
    """One fastener's badge - ON its screw, or on a leader to it.

    `family` is every caption this badge now stands for: its own cluster's
    fasteners of its own type (R7). The badge is still tethered to ONE of
    them - the one it was drawn from - but MINE, in the ownership rule, is the
    whole family, so a badge sitting on the second 6x90 of a corner is not
    counted as having strayed onto somebody else's screw.

    R6 - CONTACT OR LEADER. A badge that floats near a cluster is not a label,
    it is a riddle: the reader has to guess which of the four fasteners in the
    corner it names, and on step 5 there were three of them guessing at once.
    So a badge now has exactly two legal positions:

      TOUCHING   the badge circle overlaps the drawn body it names, sitting on
                 the head like a flag on a pole. This is the first thing tried
                 and what almost every badge gets.
      LEADERED   where the paper round the head is taken, the badge steps back
                 and a thin solid line runs from its edge to the body. The line
                 is the label; the badge is only its head.

    There is no third case, and assert_badges_anchored() re-measures both off
    the ink. Everything else about the placement is the old rule set: the
    candidates run straight back along the fastener's own axis first, then to
    either side, and layout.place() picks the cheapest - with R5 still in it,
    so a badge may never land nearer a FOREIGN body than its own.

    The COUNT is gone from here. Every screw the step drives is drawn as its
    own body now, so a "2x" beside one of them says nothing the picture does
    not; the counts live in the inset panel and in the step's table, where a
    number is read rather than looked at.
    """
    if not letter:
        # One kind of fastener on the page: the glyph in its table is already
        # the whole answer, so there is nothing to park. Page.record is what
        # went on the paper, and this went nowhere.
        return None
    dx, dy = direction
    r = T.BADGE_R
    # Straight back along the axis, hugging the head first: the badge sits ON
    # the fastener before it sits anywhere else. Then out along the same line,
    # then to either side - the ORDER is the preference, and layout.place()
    # breaks ties on it.
    # The sideways ladder runs two rungs further than it used to, and R10 is
    # why: a badge that has to leave a bracket group's chain corridor has to be
    # able to get OUT of it, and the corridor of a five-fastener corner is
    # wider than three rungs. Nothing else changed - the new rungs are further
    # from the tether than every old one, so `pull` reaches them only when
    # everything nearer has been priced out.
    tries = [(tail[0] - dx * r * k, tail[1] - dy * r * k)
             for k in (0.95, 1.45, 2.05, 2.75, 3.6)]
    for s in (1, -1):
        for k in range(5):
            tries.append((tail[0] - dy * s * (r * 1.15 + k * r * 1.5)
                          - dx * k * r * 0.8,
                          tail[1] + dx * s * (r * 1.15 + k * r * 1.5)
                          - dy * k * r * 0.8))

    # R6 and R5 are priced INTO the placer rather than checked after it. The
    # asserts are still there and still measure the ink, but a rule that only
    # ever fires as a build failure is a rule the drawing has no way to obey:
    # the placer has to be able to see that touching its own screw is worth
    # more than any amount of white paper, and that landing nearer somebody
    # else's is worth nothing at all.
    kin = list(family) if family else [dict(owner=owner, body=body)]
    kin_owners = {q["owner"] for q in kin}
    kin_bodies = [q["body"] for q in kin if q["body"] is not None]
    kin_lens = [q.get("plen") for q in kin if q["body"] is not None]
    foreign = [q["cap"] for q in page.record
               if q["kind"] in ("screw", "plate") and q.get("cap")
               and q.get("mark") is not None and q.get("mark") not in
               kin_owners]

    def price(c):
        out = 0.0
        # R10 first, and it is asked even of a badge with no body to measure
        # against: a chain corridor is a place no letter may stand, whoever
        # the letter belongs to.
        if corridors and corridor_gap(c, corridors) < r:
            out += CAP_CORRIDOR
        if not kin_bodies:
            return out
        d_own = min(cap_dist(c, q) for q in kin_bodies)
        # Contact is asked of the body this badge is DRAWN from: a letter
        # standing on the far member of its own family, with its own screw
        # bare, is a letter the eye has to hunt for.
        if body is not None and cap_dist(c, body) > r:
            out += CAP_NOCONTACT
        if foreign and min(cap_dist(c, q) for q in foreign) < d_own:
            out += CAP_FOREIGN
        return out

    occ = layout.Occupancy() if occ is None else occ
    centre = layout.place(
        tries, (2 * r, 2 * r), occ,
        tether=tail,
        # Having stepped out of the way it steps no further than it had to: a
        # badge that has wandered is one the reader has to guess at.
        pull=1.0 / (r * 8.0),
        owner=owner, family=kin_owners, tags=CAP_TAGS,
        bounds=(page.x0, page.y0, page.x1, page.y1),
        edge=r + 8, edge_penalty=CAP_EDGE, extra=price)

    leader = None
    if kin_bodies and min(cap_dist(centre, q) for q in kin_bodies) > r:
        # Out of reach of every body it stands for: it gets a line instead.
        # Drawn from the badge's rim, not its centre, so the circle stays a
        # clean disc, and to the point on the nearest family axis.
        near_body = min(kin_bodies, key=lambda q: cap_dist(centre, q))
        far = cap_point(centre, near_body)
        ux, uy, n = _unit2(centre, far)
        near = (centre[0] + ux * r, centre[1] + uy * r) if n > 0 else centre
        page.line(near, far, INK, T.W_LEAD)
        leader = (near, far)
        body = near_body
    badge(page, centre, letter, owner=owner, body=body, leader=leader,
          family=kin_bodies, family_owners=sorted(kin_owners),
          family_lens=kin_lens)
    occ.add_point(centre, radius=r, weight=CAP_BADGE, owner=owner, tag="badge")
    page.record.append(dict(kind="label", owner=owner, letter=letter,
                            at=centre, tether=tail,
                            family_owners=sorted(kin_owners)))
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


# R9, measured off the ink. The rhythm is allowed this much slack, as a
# fraction of the step itself: the bracket's leash is the float vector exactly,
# while a screw's is read back off the drawn silhouette's own point, so the two
# are the same number arrived at two ways and the last digits are not going to
# agree. Anything a reader could SEE as unequal is orders of magnitude above
# this.
CHAIN_TOL_FRAC = 0.02


def _chain_groups(page):
    """The recorded tethers, grouped by the bracket group they belong to."""
    out = {}
    for r in page.record:
        if r["kind"] == "tether" and r.get("group") is not None:
            out.setdefault(r["group"], []).append(r)
    return out


def _crosses(a, b):
    """Do two segments cross OTHER than at a shared end? R9's question.

    A chain is allowed to touch itself - every screw's tether starts at a hole
    in the bracket the bracket's own leash starts from - and is not allowed to
    cut across itself. So an intersection at either segment's endpoint is not a
    crossing; one in both interiors is.
    """
    (a0, a1), (b0, b1) = a, b
    d1 = (a1[0] - a0[0], a1[1] - a0[1])
    d2 = (b1[0] - b0[0], b1[1] - b0[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-12:
        return False                      # parallel: no proper crossing
    dx, dy = b0[0] - a0[0], b0[1] - a0[1]
    t = (dx * d2[1] - dy * d2[0]) / den
    s = (dx * d1[1] - dy * d1[0]) / den
    eps = 1e-6
    return eps < t < 1.0 - eps and eps < s < 1.0 - eps


def assert_chain_untangled(page):
    """R9, measured off the ink: the chain is nested, not tangled.

    Two things are asked of a bracket group's dotted lines, and both are about
    the NESTING - the claim the picture makes is "the bracket comes off the
    seat, and these screws come out of the bracket", so no line in it may reach
    back across the link it hangs off, and none may cut across a body in its
    own group:

      1. no screw's line crosses the bracket's own LEASH. A screw whose line
         cuts the leash is a screw the reader ties to the seat instead of to
         the bracket, which is the one relation the group exists to show.
      2. no line crosses a drawn BODY in the group. A dotted line that runs
         through a silhouette does not read as that silhouette's travel; it
         reads as somebody else's.

    What is NOT asserted, because it is not a placement decision, is two
    SIBLING lines crossing near the bracket. J12 drives one 5x40 into the post
    and one up into the ledger, at right angles, through two holes 17 mm apart
    on the page - and this camera puts the ledger screw's hole on the far side
    of the post screw's own axis. Their two lines therefore meet, and they meet
    at a point on that axis that no rhythm can move: shorten the hop and the
    crossing moves off the dotted line and onto the SOLID body, which is worse.
    It is a fact about where the joint is seen from, not a choice the drawing
    made, and the rules here only assert what the drawing can obey.
    """
    bodies = {}
    for r in page.record:
        if r["kind"] in ("screw", "plate") and r.get("cap"):
            bodies.setdefault(r["owner"], r["cap"])
    for _gid, ts in _chain_groups(page).items():
        leash = [r for r in ts if r["owner"] == _gid]
        for a in ts:
            for lead in leash:
                if a is lead:
                    continue
                assert not _crosses(a["seg"], lead["seg"]), (
                    f"{a['jid']}: innstikkslinjen for {a['name']} krysser "
                    f"beslagets egen lenke tilbake til setet - kjeden "
                    f"sete->beslag->skrue er nøstet, og en linje som skjærer "
                    f"leddet den henger i knytter skruen til feil ting (R9)")
            for r in ts:
                cap = bodies.get(r["owner"])
                if r is a or cap is None or cap[0] == cap[1]:
                    continue
                assert not _crosses(a["seg"], (cap[0], cap[1])), (
                    f"{a['jid']}: innstikkslinjen for {a['name']} går tvers "
                    f"gjennom kroppen til {r['name']} i samme beslagklynge - "
                    f"en prikket linje gjennom en silhuett leses som "
                    f"silhuettens egen vei (R9)")


def assert_chain_rhythm(page):
    """R9, measured off the ink: the chain's two steps are the same step.

    Every tether in a group is measured where it LANDED - the bracket's leash
    back to its seat, and each screw's from the point that was drawn to its
    hole in the floated bracket - and they all have to be one length. Two
    unequal steps do not read as one movement outward; they read as two
    accidents that happened to point the same way.
    """
    for _gid, ts in _chain_groups(page).items():
        legs = [(math.hypot(r["seg"][1][0] - r["seg"][0][0],
                            r["seg"][1][1] - r["seg"][0][1]), r) for r in ts]
        lo = min(legs, key=lambda q: q[0])
        hi = max(legs, key=lambda q: q[0])
        assert hi[0] - lo[0] <= CHAIN_TOL_FRAC * hi[0], (
            f"{hi[1]['jid']}: klyngen eksploderer i ulike sprang - "
            f"{hi[1]['name']} står {hi[0]:.1f} mm ut og {lo[1]['name']} "
            f"{lo[0]:.1f} mm. Sete->beslag og beslag->skrue skal være samme "
            f"sprang (R9)")


def assert_badges_anchored(page):
    """R6, measured off the ink: no badge floats.

    Three questions per badge, and all three are asked of what was WRITTEN -
    the circle's landing place, the body's drawn capsule, the leader's two
    ends - rather than of what was meant:

      1. does it touch the body it names, or
      2. does a recorded leader run from it to that body, landing ON it;
      3. and is its own body still the nearest one? A badge whose leader
         crosses somebody else's screw on the way is a badge pointing at the
         wrong hole, which is the failure this whole rule exists to stop.

    Badges without a body - the letters in an inset section, the panel rows -
    are not marks on the drawing and are not asked.
    """
    bodies = [r for r in page.record
              if r["kind"] in ("screw", "plate") and r.get("cap")
              and r.get("mark") is not None]
    for b in page.record:
        if b["kind"] != "badge" or b.get("body") is None:
            continue
        mine, r = b["body"], b["r"]
        if b["leader"] is None:
            # Touching ANY of the bodies it stands for is contact: they are
            # the same fastener in the same cluster, and the badge names all
            # of them (R7).
            gap = min(cap_dist(b["at"], q) for q in (b.get("family") or [mine]))
            assert gap <= r + 1e-6, (
                f"merket {b['letter']} står {gap:.0f} mm fra kroppen sitt "
                f"eget feste tegner, uten lederlinje - et merke skal enten "
                f"røre festet sitt eller peke på det (R6)")
        else:
            near, far = b["leader"]
            assert cap_dist(far, mine) <= 1e-6, (
                f"merket {b['letter']} har en lederlinje som ender "
                f"{cap_dist(far, mine):.0f} mm utenfor sitt eget feste (R6)")
            assert abs(math.hypot(near[0] - b["at"][0],
                                  near[1] - b["at"][1]) - r) < 1e-6, (
                f"merket {b['letter']} sin lederlinje starter ikke i "
                f"merkets egen rand (R6)")
        # R5, widened from one body to the FAMILY the badge stands for (R7):
        # nearer to some member of its own type's cluster than to anything
        # outside it. A badge that has landed nearer a foreign screw than to
        # every screw it names is not a crowded label, it is a wrong one.
        kin = b.get("family") or [mine]
        kin_owners = set(b.get("family_owners") or [b["owner"]])
        d_own = min(cap_dist(b["at"], q) for q in kin)
        # R7's own promise, measured: a badge is never further from a body it
        # stands for than the radius the cluster rule is written with. A
        # cluster is a ball round a seed, so two of its members can be twice
        # that apart - and a letter standing for a screw most of a page away is
        # a letter the reader cannot get back from.
        far = max(cap_dist(b["at"], q) for q in kin)
        assert far <= T.BADGE_R * CLUSTER_R_BADGES + b["r"] + 1e-6, (
            f"merket {b['letter']} står for en kropp {far:.0f} mm unna, "
            f"utenfor klyngeradien det er skrevet med - da er ikke merket å "
            f"finne fra kroppen (R7)")
        for other in bodies:
            if other["mark"] in kin_owners:
                continue
            d_foreign = cap_dist(b["at"], other["cap"])
            assert d_foreign >= d_own - 1e-6, (
                f"merket {b['letter']} ligger {d_foreign:.0f} mm fra "
                f"{other['jid']} {other['name']} og {d_own:.0f} mm fra det "
                f"nærmeste festet det står for - et merke skal aldri lande "
                f"nærmere en fremmed kropp enn sin egen familie (R5)")


def assert_badges_clear_chain(page):
    """R10, measured off the ink: no badge stands in a bracket group's chain.

    The corridor is rebuilt here from the recorded tethers rather than handed
    down from the placer, and the badge's landing place is read out of the
    record too, so what is checked is the picture that was written - not the
    candidate list it was chosen from.

    Badges with no body are the inset panel's and the fastener table's; they
    are not marks on the drawing and there is no chain where they live.
    """
    corridors = chain_corridors(page)
    if not corridors:
        return
    for b in page.record:
        if b["kind"] != "badge" or b.get("body") is None:
            continue
        gap = corridor_gap(b["at"], corridors)
        assert gap >= b["r"] - 1e-6, (
            f"merket {b['letter']} ligger {b['r'] - gap:.0f} mm inn over et "
            f"ledd i en beslagklynges kjede - kjeden sete->beslag->skruer er "
            f"det eneste som sier at hjørnet er én demontering, og en bokstav "
            f"oppå den bryter den (R10)")


def assert_badges_cover(page):
    """R7, measured off the ink: nothing on the page is left unnamed.

    One badge per type per cluster is only a saving if the badge that stays
    covers the ones that went. So every drawn fastener that carries a letter
    is asked for its letter's badge among the badges that stand for IT - not
    for one somewhere on the page, for one whose own family it is in. A screw
    that answers no is a screw the reader cannot find a table row for, and
    that is the failure this whole rule has to be paid for with.
    """
    fams = [(b["letter"], set(b["family_owners"])) for b in page.record
            if b["kind"] == "badge" and b.get("family_owners")]
    for r in page.record:
        if r["kind"] not in ("screw", "plate") or r.get("mark") is None:
            continue
        if not r.get("letter"):
            continue
        assert any(r["letter"] == lt and r["mark"] in own for lt, own in fams), (
            f"{r['jid']} {r['name']} er tegnet uten at merket "
            f"{r['letter']} står for det - ingen bokstav innenfor klyngen "
            f"sin, og da finner ikke leseren raden i tabellen (R7)")


def assert_no_stubs(page):
    """No drawn fastener has been foreshortened into a dart. See STUB_ASPECT.

    Measured off the ink, on the two numbers that decide whether a silhouette
    still reads as a screw: the axis the page drew, and the head it drew it
    with. A ringed dot is exempt - it has no axis at all, and it is a
    convention the reader has been taught rather than a screw that came out
    short.
    """
    for r in page.record:
        if r["kind"] != "screw" or r.get("axis") is None:
            continue
        head = 2.0 * r["head_r"]
        length = drawn_length(r)
        assert length >= STUB_ASPECT * head - 1e-9, (
            f"{r['jid']} {r['name']}: kroppen er tegnet {length:.1f} mm lang "
            f"over et {head:.1f} mm hode - {length / head:.2f} hoder, under "
            f"{STUB_ASPECT}, og da er silhuetten en pil og ikke en skrue. "
            f"Se FORESHORTEN_FLOOR og SCREW_FATTEN")


def assert_badges_homogeneous(page):
    """The R7 amendment, measured off the ink: a family LOOKS like one.

    Every badge that stands for more than one body is asked what those bodies
    came out looking like - the lengths are read back out of the page's own
    record of the silhouettes it drew - and the spread has to be inside
    HOMOGENEITY_SPREAD. A letter standing for a full-length screw and a stub is
    a letter that answers the reader's question about one of them and leaves
    the other one nameless.
    """
    for b in page.record:
        if b["kind"] != "badge":
            continue
        lens = [v for v in (b.get("family_lens") or []) if v is not None]
        if len(lens) < 2:
            continue
        lo, hi = min(lens), max(lens)
        assert hi - lo <= HOMOGENEITY_SPREAD * hi + 1e-9, (
            f"merket {b['letter']} står for kropper som er tegnet "
            f"{lo:.0f} og {hi:.0f} mm lange - over {_pct(HOMOGENEITY_SPREAD)} "
            f"spredning er de to slags ting på papiret, og da skal hver av "
            f"dem ha sitt eget merke (R7)")


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
        fam = r.get("family_owners") or [r["owner"]]
        mine, _who = occ.nearest(r["at"], owner=r["owner"], foreign=False,
                                 family=fam)
        theirs, who = occ.nearest(r["at"], owner=r["owner"], foreign=True,
                                  family=fam)
        if mine is None or theirs is None:
            continue
        assert mine <= theirs + 1e-6, (
            f"merket {r['letter'] or '(uten bokstav)'} for {r['owner'][0]} "
            f"ligger {mine:.0f} mm fra sitt eget feste og {theirs:.0f} mm fra "
            f"{who[0]} sitt - et merke skal aldri lande nærmere en fremmed "
            f"kropp enn sin egen (R5)")


# ---------------------------------------------------------------------------
# EVERY FASTENER, ONE FOR ONE - AND THE THREE PLACES IT IS NOT
# ---------------------------------------------------------------------------
# The front of the manual promises that the fasteners are DRAWN, one for one,
# and check_coverage() has never been able to check that promise: it adds up
# the `per` counts, and a mark that swallowed its neighbour hands its count on
# and keeps the sum right while the page draws one screw where the table says
# two. That is precisely how J3's middle screw went missing on step 6 - six
# screws in the beslag list, four silhouettes on the paper, every total
# correct.
#
# assert_joint_marks_drawn() asks the other question, of the ink: how many
# SYMBOLS did this page put down for this joint, against how many fasteners
# the joint has in this step. It is a joint-by-joint count and not a page
# total, because a page total can be right for the wrong reason.
#
# COINCIDENT_MARKS is the only way out, and it is a list of NAMES rather than
# a tolerance: a step, a joint, what the model has, what the page could draw,
# and why. Every entry here is the same picture, and it is a real one - two
# screws of one joint 24 mm apart, drawn with heads fattened to SCREW_FATTEN
# so a 6 mm screw is legible at all, i.e. 23.4 mm across. The two silhouettes
# overlap by 0.3 mm and the page can only draw one of them. The screws are
# right, the spacing is right, and the head is a legibility licence the whole
# manual is drawn with (docs/preview/formkontrast.png is where that number is
# proven), so this is the one case that is honestly a coincidence.
#
# It is NOT the escape hatch for a symbol that is merely too big for its row.
# The head-on ring is a page constant with nothing of the screw in it, so when
# a row of them crowds, the ring gives way instead - see A ROW OF HEADS. Only
# a fattening that the manual has already paid for elsewhere may cash in here.
#
#   (step, joint): (fasteners in the model, symbols the page draws, why)
COINCIDENT_MARKS = {
    (1, "J8-B"): (2, 1, "bakre benkevangeende → bakre stolpe: paret står "
                        "24 mm fra hverandre i Z og hodene er 23,4 mm"),
    (5, "J8"): (2, 1, "fremre benkevangeende → fremre stolpe: samme par, "
                      "samme 24 mm, sett omtrent rett forfra"),
    # X18: og det samme paret en tredje gang, en etasje opp. J12 mistet
    # vinkelbeslaget sitt og er nå den samme skråskrueenden som J8-B.
    (1, "J12"): (2, 1, "bordbærelektas ende → bakre stolpe: samme par, "
                       "samme 24 mm i Z, samme 23,4 mm hoder"),
}


def assert_joint_marks_drawn(page, st, marks):
    """One drawn symbol per fastener, joint by joint, measured off the ink.

    `marks` is what the step drives on THIS page - already cut down to the
    half a half view draws, because a half view's other end is not a missing
    screw, it is a screw on the other sheet. The count on the paper comes out
    of the page's own record, so it is the silhouettes that answer and not the
    intention that produced them.
    """
    want, got = {}, {}
    for m in marks:
        want[m["jid"]] = want.get(m["jid"], 0) + 1
    for r in page.record:
        if r["kind"] in ("screw", "plate") and r.get("mark") is not None:
            got[r["jid"]] = got.get(r["jid"], 0) + 1
    for jid in sorted(want):
        n_want, n_got = want[jid], got.get(jid, 0)
        known = COINCIDENT_MARKS.get((st["n"], jid))
        if known is None:
            assert n_got == n_want, (
                f"steg {st['n']}, ledd {jid}: leddet har {n_want} "
                f"festemidler i dette steget, men arket tegner {n_got} "
                f"symboler. Festemidlene skal stå ett for ett. Enten skal "
                f"symbolet vike (se A ROW OF HEADS og choose_marks (R2)), "
                f"eller så er sammenfallet ekte og skal skrives opp med navn "
                f"og grunn i COINCIDENT_MARKS.")
            continue
        listed, drawn, why = known
        assert (n_want, n_got) == (listed, drawn), (
            f"steg {st['n']}, ledd {jid}: COINCIDENT_MARKS sier {listed} "
            f"festemidler tegnet som {drawn} symboler ({why}), men arket "
            f"har {n_want} festemidler og tegner {n_got}. Sammenfallet er "
            f"ikke det samme lenger - rett opp raden eller stryk den.")


# ---------------------------------------------------------------------------
# R7 - ONE BADGE PER TYPE PER CLUSTER
# ---------------------------------------------------------------------------
# A ladder stile takes eight identical 5x60 in a column, and the page used to
# put eight identical letters down beside them. Eight badges is not eight
# pieces of information: it is one, repeated until it becomes wallpaper, and
# the wallpaper is what crowds the badge that DOES say something new.
#
# The first version of this rule merged a RUN - same letter, same joint,
# bodies in an unbroken chain with nothing foreign among them - and it was too
# timid to help where help was needed. On step 5 the stub-leg corner came out
# with eleven letters over two joints (A A A D on the upper rail, A A A D B C
# on the lower), because the two joints are two joints and because the D
# bracket sat inside every run and broke it. Eleven letters for FOUR kinds of
# fastener, in a corner the reader is looking at as one piece of work.
#
# So the unit is no longer the run, it is the PLACE. A cluster is what the
# reader takes in with one look: every drawn body within CLUSTER_R of a seed,
# whatever joint it belongs to and whatever type it is. Inside one cluster,
# each TYPE carries exactly one badge - the first in the page's own drawing
# order, so the choice is as reproducible as everything else here - and that
# badge stands for its whole family. The inset panel is still the full key:
# every type on the page has a row there with its count, and nothing about
# what the reader is told has been dropped, only how many times.
#
# Two things keep it honest, and both are asserts that measure the ink:
#
#   * COVERAGE (assert_badges_cover). Every drawn fastener that has a letter
#     must have that letter's badge inside its own cluster. A screw with no
#     badge within a look of it is a screw the table cannot be found for.
#   * OWNERSHIP (R5, in assert_badges_anchored). The badge must be nearer to
#     SOME member of its own family than to any foreign body. It is the same
#     rule as before with MINE widened from one body to the family - which is
#     exactly what the badge now names.
#
# The cluster is a BALL and not a chain on purpose. Chaining is transitive,
# and on a page like the slat field one chain would swallow the whole bed and
# leave a single letter in a corner standing for twenty-eight screws a metre
# away. A seed and a radius cannot do that: a badge is never further from the
# body it stands for than the radius the rule is written with.
CLUSTER_R_BADGES = 16.0        # cluster radius, in badge radii
FAMILY_R_BADGES = 11.0         # X18: how far one badge may STAND FOR, same
                               # unit - the cluster radius less the room the
                               # badge itself is allowed to step aside into


def caption_clusters(captions, radius):
    """The PLACES a page's drawn bodies are at, in drawing order.

    Greedy from the first unassigned caption: it seeds a cluster and takes in
    every other unassigned body whose own capsule is within `radius` of it.
    Deterministic, because the order it walks is the order the page drew in,
    and bounded, because the seed never moves.
    """
    left = [c for c in captions]
    out = []
    while left:
        seed = left.pop(0)
        group = [seed]
        if seed["body"] is not None:
            rest = []
            for c in left:
                if (c["body"] is not None
                        and _seg_seg_dist(seed["body"][0], seed["body"][1],
                                          c["body"][0], c["body"][1])
                        <= radius):
                    group.append(c)
                else:
                    rest.append(c)
            left = rest
        out.append(group)
    return out


# THE AMENDMENT: A FAMILY HAS TO LOOK LIKE ONE.
# ---------------------------------------------
# One badge for a type is a saving because the reader sees a row of the same
# thing and needs telling once. That argument is about the PICTURE, not about
# the parts list, and it fails the moment the picture stops repeating itself.
#
# The J12 corner is where it failed. Two 5x40 go into it, one into the post and
# one up into the ledger, and they are the same screw out of the same box - but
# the camera looks nearly down the first one's axis and across the second's, so
# the page drew a stub beside a full-length screw and put ONE letter on the
# full-length one. The stub was then a fastener with no badge that looked like
# no other fastener on the page, which is precisely the reader's question ("and
# what is that one?") left unanswered by a rule that exists to answer it.
#
# So a type may share a badge only where its members are VISUALLY HOMOGENEOUS:
# the spread of drawn lengths inside the family - (longest - shortest) over
# the longest - no more than HOMOGENEITY_SPREAD. It is the same 25 % the fill
# code's ambiguity test uses (gen_glyphs.ambiguous_pairs, PRAKSIS 4) and for
# the same reason - below a quarter two lengths are one length to the eye,
# above it they are two things.
#
# Where a type is not homogeneous it is not un-merged wholesale, it is CUT at
# the gaps: the members are split into runs that are alike within the tolerance
# and each run keeps a badge. A family of eight identical ladder screws and one
# foreshortened odd one out is nine bodies, two appearances and two badges -
# not nine badges, which would hand the wallpaper back, and not one, which is
# the failure above.
HOMOGENEITY_SPREAD = 0.25


def homogeneous_runs(fam, order):
    """One type's captions, split into runs that LOOK alike. R7 amendment.

    `order` is the page's own drawing order, and it does two jobs: it breaks
    ties between equal lengths so the split is reproducible, and it decides
    which member of each run carries the badge - the first one drawn, exactly
    as the unamended rule chose.
    """
    lens = [c.get("plen") for c in fam]
    if len(fam) < 2 or any(v is None for v in lens):
        # A bracket has no drawn length to compare (its silhouette is a plate,
        # not an axis), and two brackets of one type in one cluster are two
        # identical plates. Nothing to split.
        return [fam]
    runs = []
    for c in sorted(fam, key=lambda q: (q["plen"], order[id(q)])):
        if runs and c["plen"] - runs[-1][0]["plen"] <= (HOMOGENEITY_SPREAD
                                                        * c["plen"]):
            runs[-1].append(c)
        else:
            runs.append([c])
    return [sorted(r, key=lambda q: order[id(q)]) for r in runs]


def reach_runs(fam, radius):
    """One type's captions, split so a badge is never out of reach of one.

    A cluster is a ball of `radius` round a SEED, so two members of it can be
    twice that apart - and the promise R7 is written with is that a badge is
    never further from a body it stands for than the radius. The same greedy
    ball, applied inside the type, keeps the promise: the first member drawn
    takes in everything within reach of itself, and whatever is left seeds the
    next badge. Step 5's two stub-foot corners are the case - two identical
    brackets 437 mm apart, in one cluster because a screw between them seeded
    it, and one letter for both would have left the second corner's bracket
    bare with its badge most of a page away.
    """
    # X18 - AND THE RADIUS THE FAMILY IS GATHERED WITH IS NOT THE ONE THE
    # PROMISE IS MEASURED WITH. The promise is about the BADGE, and a badge
    # does not sit on its seed: it is placed clear of the line work, up to a
    # leader's length off it. Gather the family at the full cluster radius and
    # the badge starts outside its own guarantee the moment it steps aside -
    # which is exactly what step 5 did the day the bench grew a slat ledger and
    # ten identical 5x60 landed in one place. So the family is gathered at the
    # cluster radius LESS the room a badge is allowed to step, and the two
    # numbers are written down separately instead of being the same one twice.
    reach = radius * FAMILY_R_BADGES / CLUSTER_R_BADGES
    left = list(fam)
    out = []
    while left:
        seed = left.pop(0)
        grp, rest = [seed], []
        for c in left:
            if (seed["body"] is not None and c["body"] is not None
                    and _seg_seg_dist(seed["body"][0], seed["body"][1],
                                      c["body"][0], c["body"][1]) <= reach):
                grp.append(c)
            else:
                rest.append(c)
        left = rest
        out.append(grp)
    return out


def thin_clusters(captions):
    """One badge per fastener TYPE per cluster, each carrying its family. R7."""
    radius = T.BADGE_R * CLUSTER_R_BADGES
    order = {id(c): i for i, c in enumerate(captions)}
    keep = []
    for group in caption_clusters(captions, radius):
        families = {}
        for c in group:
            if c["body"] is None or not c["letter"]:
                # Nothing to stand for anybody else with: a bracket drawn
                # without a capsule, or a page with no letters at all.
                keep.append(dict(c, family=[c]))
                continue
            families.setdefault(c["letter"], []).append(c)
        # Two cuts through a type's family, and they ask two different
        # questions: is the badge WITHIN REACH of everything it stands for, and
        # does everything it stands for LOOK like one thing.
        for _letter, fam in families.items():
            for near in reach_runs(fam, radius):
                for run in homogeneous_runs(near, order):
                    keep.append(dict(run[0], family=run))
    return sorted(keep, key=lambda c: order[id(c["family"][0])])


# ---------------------------------------------------------------------------
# THE STEP PAGES
# ---------------------------------------------------------------------------
# What a panel costs where it lands, in the units layout.place() scores in.
# A panel is opaque, so these are not preferences in the way a caption's are:
# line work it covers is line work nobody can read, a fastening point it
# covers loses its own mark and has to hand its count to a joint somewhere
# else on the page, and a panel on a panel is simply one page short.
PANEL_INK = 1.0
# ...and what it costs on the step's OWN parts. layout.Occupancy has always
# known that the two layers are not the same thing - "a caption may lie over
# the grey ghost of a frame that is already standing, never over the black
# part the step is about" - and every annotation on the page but this one
# asked it that way. The panel did not, and it is the annotation with the
# least right to be careless: a badge crowds what is under it, an opaque
# white box HIDES it. On the ladder page that put the fastener list over the
# top of the right upright, which is one of the two parts the step is about.
# So the step's own line work is a wall to the panel and the ghost behind it
# is not: the panel is welcome in front of the standing frame, which is what
# ghosting is for, and nowhere near the piece being fitted.
PANEL_SUBJECT = 400.0
PANEL_MARK = 60.0
PANEL_PANEL = 4000.0
# occ.cost() counts the VERTICES that land inside the box, which is the right
# question for a scatter of short edges and the wrong one for a 2 m upright
# whose two ends are off the page: a panel could sit squarely across the
# middle of it and be charged nothing. So the subject's edges are walked at
# this pitch first, in model mm, and the box is charged for the paper it
# covers rather than for the corners it happens to catch.
SUBJECT_SAMPLE = 25.0
# The panel's own air: how far its edge stands off the page edge, and how much
# margin round it also counts as occupied. They were two loose numbers in the
# placer call; they are named because crop_to_subject() has to solve for them
# - a page cut so tight that no corner can hold the panel is a page where the
# placer's only choice is which part of the subject to hide.
PANEL_EDGE = 20.0
PANEL_GROW = 30.0
# The margin crop_to_subject() solves for is EXACT, and exact means tangent:
# the grown footprint's edge lands on the subject's outermost line, and a
# point on the boundary counts as inside. This is the hairline that makes
# "beside the subject" mean beside it.
PANEL_CLEAR = 8.0
# EVERY OPAQUE BLOCK A STEP PAGE CAN PARK IN A CORNER, as a fraction of the
# page width, in one place - because two things read this list: render_step(),
# which draws them, and crop_to_subject(), which has to cut a page wide enough
# to hold the widest of them. They were three loose numbers in three calls,
# and the day the panel came off the sheets the crop went on reserving room
# for it, which is exactly the sort of quiet disagreement a manual made of one
# source is not allowed to have.
#
# `lens` is a RADIUS fraction; the other two are widths. The mirror pictogram
# is the widest, because it carries a whole little drawing of the bed with the
# mirror line through it and an "x2" beside it.
LENS_R_FRAC = 0.10
CORNER_BLOCK_FRAC = {
    "half_view": 0.38,        # the mirror pictogram
    "info_panel": 0.32,       # the mattress page's three lines and a section
}


def _sampled(plines, pitch):
    """The same line work with a point at least every `pitch` along it."""
    out = []
    for pl in plines:
        pts = [pl[0]]
        for a, b in zip(pl, pl[1:]):
            n = int(math.hypot(b[0] - a[0], b[1] - a[1]) / pitch)
            for i in range(1, n + 1):
                t = i / (n + 1)
                pts.append((a[0] + (b[0] - a[0]) * t,
                            a[1] + (b[1] - a[1]) * t))
            pts.append(b)
        out.append(pts)
    return out


def emptiest_corner(plines, page, box_w, box_h, marks=(),
                    avoid_top_left=False, avoid=(), subject=()):
    """Put the inset where the drawing is not - and, above all, where the
    fastening points are not.

    Four candidates, in the order they are preferred, through the same placer
    every other annotation goes through. `avoid` is any panel already on the
    page. Two panels in one corner is not crowding, it is one panel hiding the
    other. `subject` is the step's own parts - see PANEL_SUBJECT: the panel
    may stand in front of the ghost and not in front of them."""
    occ = layout.Occupancy()
    occ.add_lines(plines, weight=PANEL_INK, tag="art")
    occ.add_lines(_sampled(subject, SUBJECT_SAMPLE), weight=PANEL_SUBJECT,
                  tag="art")
    # The mark's own radius on top of the box's margin: a panel edge 40 mm
    # from a fastening point is already on it.
    occ.add_points([m["p2"] for m in marks], radius=10.0, weight=PANEL_MARK,
                   tag="mark")
    for a in avoid:
        occ.add_box(a, weight=PANEL_PANEL)
    e = PANEL_EDGE
    corners = [(page.x1 - box_w - e, page.y1 - box_h - e),
               (page.x1 - box_w - e, page.y0 + e),
               (page.x0 + e, page.y0 + e)]
    if not avoid_top_left:
        corners.append((page.x0 + e, page.y1 - box_h - e))
    at = layout.place([(bx + box_w / 2, by + box_h / 2)
                       for bx, by in corners],
                      (box_w, box_h), occ, grow=PANEL_GROW)
    return (at[0] - box_w / 2, at[1] - box_h / 2)


# ---------------------------------------------------------------------------
# THE WALL THE BED IS SCREWED TO
# ---------------------------------------------------------------------------
# One step in this manual is not about a piece of the bed at all: it stands the
# back frame up and fastens it to the ROOM. Drawn without the room, that page
# was a frame floating in white with its wall screws coming out of the back of
# it and nothing on the other side - the one page in the book whose whole
# subject was the thing it did not draw.
#
# So it gets the wall, and it gets it in the pen the page already has for
# something that is there and is not what you are fitting now: the ghost.
# Grey, W_PRIOR, drawn before anything else and therefore behind it. No new
# stroke is invented and nothing is added that the eye has to climb over -
# the step is still about the frame.
#
#   THE FLOOR LINE   where the wall meets the floor, and the ONLY edge of the
#                    wall that is drawn: it is the only one that is real. A
#                    wall does not stop at the edge of the page, so it runs
#                    out of the viewBox at both ends and at the top, and a
#                    rectangle round it would have said it stops there.
#   THE STUDS        phantom - dashed, in DASH_PHANTOM, which is this page's
#                    own way of saying "this is really there and you cannot
#                    see it" (see DRAWING A FASTENER). That is exactly their
#                    state: behind the boarding, and the reader's job to find.
#
# WHAT THE DRAWING DOES NOT CLAIM. Where the studs in the reader's room stand
# is not in the model and cannot be - generate_loftbed.py says so itself in
# the joint note, "stenderne finnes bare i rommet", and the fastener row says
# "etter veggtype" for the same reason. So this draws A stud wall and not THIS
# wall: ordinary bindingsverk at c/c 600, phased on the bed's own centre line.
# Nothing on the page counts them and no assert measures them; they are the
# picture of a wall, in the lightest pen the page owns.
WALL_STUD_CC = 600.0
WALL_STUD_W = 36.0
# How far past the bed the wall runs before the viewBox cuts it off. A wall
# that ended where the frame ends would be a headboard.
WALL_MARGIN = 700.0


def wall_datum(G, marks):
    """(wall plane Y, the bed's box) for a step that fastens to the room.

    None for every other step, and the test is deliberately not a joint id or
    a count: which joints go into the wall is the model's business and has
    already changed once. What cannot change is the geometry - a wall fixing
    is a fastener whose POINT ends up behind the bed's own back face - and the
    plane it ends up behind is that same back face, read off the model rather
    than typed in here.
    """
    box = full_bed(G).bounding_box()
    for m in marks:
        f = m["spec"]
        if f["kind"] == "plate":
            continue
        tip_y = f["anchor"][1] + f["direction"][1] * f["length"]
        if tip_y < box.min.Y - 1e-6:
            return (box.min.Y, box)
    return None


def draw_wall(page, view, G, marks):
    """The room behind the frame. Returns how many studs went down."""
    datum = wall_datum(G, marks)
    if datum is None:
        return 0
    wall_y, box = datum
    x0, x1 = box.min.X - WALL_MARGIN, box.max.X + WALL_MARGIN
    z0, z1 = box.min.Z, box.max.Z + WALL_MARGIN
    page.polylines([[view.xy((x0, wall_y, z0)), view.xy((x1, wall_y, z0))]],
                   GREY, T.W_PRIOR)
    # The FLOOR line runs past the bed at both ends; the STUDS do not. Only
    # the ones the frame is actually fastened to are any of the drawing's
    # business, and a phantom line out in the empty half of the page is
    # wallpaper - it crosses the before/after thumbnails and says nothing the
    # three behind the frame have not said already.
    mid = (box.min.X + box.max.X) / 2.0
    lo = int(math.floor((box.min.X - mid) / WALL_STUD_CC))
    hi = int(math.ceil((box.max.X - mid) / WALL_STUD_CC))
    studs = []
    for k in range(lo, hi + 1):
        c = mid + k * WALL_STUD_CC
        edges = [x for x in (c - WALL_STUD_W / 2, c + WALL_STUD_W / 2)
                 if box.min.X <= x <= box.max.X]
        if len(edges) < 2:
            continue
        for x in edges:
            studs.append([view.xy((x, wall_y, z0)),
                          view.xy((x, wall_y, z1))])
    page.polylines(studs, GREY, T.W_PRIOR, dash=DASH_PHANTOM)
    return len(studs) // 2


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

    A flat-pack manual writes a single maximum here. This bed needs BOTH
    bounds, and they pull opposite ways off the same two fixed heights - the
    slat top the mattress lies on, and the guard above it:

        too THIN  and the gap under the lower guard band opens up into the
                  wedge band, where part of a limb goes in and does not come
                  out. The arrow is UNDER the mattress.
        too THICK and the mattress top passes the board's own underside - the
                  board stops capping the mattress edge and is buried in it.
                  X18: on the BUILT bed that is the bound that bites, and the
                  barrier bound above it (which the arrow still draws) is a
                  long way from being reached.

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
            f"{int(round(gap))}", f"maks {G.MAX_GUARD_INBOARD_CAPPED} lukket")
    between(sx + sw * 0.78, G.MATTRESS_Z1, G.GUARD_TOP,
            f"{int(round(barrier))}", f"min {G.MIN_GUARD_OVER_MATTRESS}")


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
                fasteners, families, centre, half=None, dims=()):
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
    codes = page_fill_codes(st, letters)
    marks = ([] if st.get("no_fasteners")
             else step_marks(G, st, letters, codes, view))

    if half:
        page_box, half = half_crop(combined.get("prior", []) + new_only,
                                   marks)
        # Only the end that is drawn. The other end's fasteners are not
        # dropped from the manual - they are still in every count on the page
        # - they are dropped from the PICTURE, which is the whole point of a
        # half view and is what the mirror pictogram says out loud.
        marks = [m for m in marks if m["p2"][0] <= half["cut"]]

    # X15: THE PLACEMENT MEASURES ARE PLANNED BEFORE THE PAGE EXISTS, because
    # an arrow standing off the bed is part of how big the page has to be.
    # Every one of them is derived in tools/step_dims.py off the model's own
    # solids; all this does is find them paper.
    # A measure stands off THE SUBJECT, not off the ghost. The frame already
    # standing is grey for exactly this reason - an annotation is welcome to
    # lie across it, the way an exploded fastener is - and a dimension that
    # had to clear a two-metre bed to measure a rung would take the page with
    # it. So the field is the wood this step adds and nothing else.
    dim_size = T.S_DIM
    dim_plans = plan_step_dims(view, dims, new_only, dim_size, page_box)
    want = step_dim_bounds(dim_plans, dim_size)
    x0, y0, x1, y1 = page_box
    if want is not None:
        x0, y0 = min(x0, want[0]), min(y0, want[1])
        x1, y1 = max(x1, want[2]), max(y1, want[3])
    page = Page(x0, y0, x1, y1)
    # THE RASTER, KNOWN BEFORE ANYTHING IS DRAWN. write() works this out at
    # the end for the fill code's sake, but the thread on a screw has to be
    # decided while the screw is being drawn, and it is the same question:
    # how many pixels is one millimetre of this page going to be. So the page
    # is told once, here, and both rules read the one number.
    page.px_per_unit = width / page.w
    # THE ROOM, on the one page whose subject is the room: before the ghost,
    # so it is behind everything, including everything already standing.
    studs = draw_wall(page, view, G, marks)
    page.polylines(combined.get("prior", []), GREY, T.W_PRIOR)
    # The new part is drawn whole - but the stretch of it that something
    # already standing hides is drawn DASHED, because that is the only thing
    # on the page that says which side of the frame it goes on. The front side
    # rail passes BEHIND the front posts, and a solid line across the post
    # says the opposite.
    page.polylines(new_only, INK, T.W_NEW * 0.45, dash="26 20")
    page.polylines(combined.get("new", []), INK, T.W_NEW)
    # ...and the measures go down with the line work, so that everything that
    # comes after - the panel, the fasteners, the badges - can be told to keep
    # off them by the same field it keeps off the bed by.
    dim_ink_lines = draw_step_dims(page, view, dim_plans, dim_size)

    # No step number in the drawing: the page header already carries it, and
    # two of them is one too many.

    # THE FASTENER LIST IS NOT ON THE DRAWING ANY MORE (erfaringsrunde 1).
    # It used to be here twice: an opaque white panel in the corner of the
    # figure - joint sections, then a row per type with its count - and the
    # very same rows again as the beslag legend under the figure on the step
    # page. The builder read the legend, because that is where the glyph is
    # printed at a size a hand can match against a screw and where the trade
    # name is spelled out; the panel was the copy that covered line work to
    # say it. So the legend is the one that stays, and the sheet gets its
    # corner back. Where the screws GO IN, which is what the joint sections
    # carried, is the reference booklet's question and is answered there by
    # «Skrueretninger» and by the beslagliste each step page links to.
    #
    # The only panel left on a sheet is the mattress page's information
    # panel, which is not a list of anything: it is three lines and a section
    # about how the mattress meets the wall, and it has no copy anywhere.
    box = None
    if st.get("info_panel"):
        inset_w = page.w * CORNER_BLOCK_FRAC["info_panel"]
        inset_h = page.h * 0.36
        # A step with no fastener marks has nothing to steer the panel away
        # from, and the mattress itself is only a handful of outline points -
        # so "emptiest" would pick the top left corner, which is exactly the
        # corner the panel is about: the mattress meeting the back wall. The
        # step says so itself with avoid_top_left.
        # The measures count as SUBJECT to the panel placer, not as line
        # work: a panel parked over a dimension hides a number, and an opaque
        # white box over a number is the one drawing fault that cannot be
        # read round.
        bx, by = emptiest_corner(combined.get("prior", []),
                                 page, inset_w, inset_h, marks,
                                 avoid_top_left=st.get("avoid_top_left"),
                                 subject=new_only + dim_ink_lines)
        box = (bx, by, inset_w, inset_h)
    # Both of these are measured on the SHORT side of the page, so a step
    # that gets a tall page of its own - the ladder - does not get arrows and
    # spacings scaled off a height it never uses across.
    keep = choose_marks(marks, inset=box)
    keep = restore_orphans(keep, families,
                           {families[l] for l in st["labels"]
                            if l in families})

    if box is not None:
        info_panel(page, box, G)
    if not st.get("no_fasteners"):
        check_coverage(st, keep, fasteners, families, share=2 if half else 1)

    # The mirror pictogram is PLACED here and DRAWN last: it has to be out of
    # the magnifiers' way before they go looking for paper, and on top of the
    # line work when it lands.
    note_box = None
    if half:
        note_w = page.w * CORNER_BLOCK_FRAC["half_view"]
        note_h = note_w * 0.42
        nx, ny = emptiest_corner(combined.get("prior", []),
                                 page, note_w, note_h, keep,
                                 avoid=() if box is None else (box,),
                                 subject=new_only + dim_ink_lines)
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
    occ.add_lines(dim_ink_lines, weight=1.0, tag="dark")
    if box is not None:
        occ.add_box(box, weight=40.0)
    stacks = {}
    captions = []
    # The brackets are placed BEFORE anything is drawn: a bracket's own screws
    # explode from where the bracket ended up, so they have to know its float
    # before their own hop back is worked out.
    floats = {}
    # Which way each bracket's own letter sets off - through the widest gap
    # between the group's links (R10). It is worked out here with the float
    # because it is made of the same two things: the leash's bearing and the
    # riders' drive axes.
    badge_out = {}
    plates = [m["spec"] for m in keep if m["spec"]["kind"] == "plate"]
    if style == "eksplodert":
        for p in plates:
            # The direction comes off the model's own screws (R1 - a bracket
            # comes off the way it is HELD, whether or not this page draws
            # every screw that holds it); the beat has to clear the screws the
            # page is actually going to draw (R9).
            riders = [m["spec"] for m in keep
                      if m["spec"]["kind"] != "plate"
                      and m["spec"]["jid"] == p["jid"]
                      and screw_on_plate(p, m["spec"])]
            floats[id(p)] = float_plate(occ, view, p, plate_screws(G, p),
                                        riders, float_d)
            badge_out[id(p)] = badge_gap_dir(view, floats[id(p)][0], riders)

    def rides_on(f):
        """The bracket this screw goes through, if it goes through one.

        Returns (the bracket, its page offset, the group's rhythm) - all three,
        because a screw in a bracket group needs all three: it explodes FROM
        where the bracket ended up, BY the same step the bracket took, and its
        tether belongs to that group's chain when R9 comes to measure it.
        """
        for p in plates:
            if p["jid"] == f["jid"] and screw_on_plate(p, f):
                poff, d = floats.get(id(p), ((0.0, 0.0), None))
                return (p, poff, d)
        return (None, (0.0, 0.0), None)

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
                poff, rhythm = floats[id(f)]
                group = id(f)
                shift = (0.0, 0.0, 0.0)
                # The caption sets off through the gap between the group's own
                # links, and `label_dir` is the direction a caption ladder
                # walks BACKWARDS along - see mark_label() - so it is that
                # bearing negated. Outboard along the float is what this used
                # to be, and outboard along the float is exactly where the
                # group's screws go too (R10).
                out_x, out_y = badge_out[id(f)]
                label_dir = (-out_x, -out_y)
            else:
                # Backed out along its own axis in MODEL space, so the pulled
                # screw stays on the line it travels no matter where the camera
                # stands. The hop is measured off the projection - the screw's
                # own drawn length plus the gap - so the point ends up exactly
                # that far short of its hole whatever the angle, and body,
                # dotted line and hole are one straight run. The GAP is the
                # group's rhythm where the screw rides on a bracket (R9), and
                # `hover` grown until it finds paper where it does not.
                host, poff, rhythm = rides_on(f)
                group = None if host is None else id(host)
                if nrm >= AXIS_ON_PAGE:
                    ux, uy = dx / nrm, dy / nrm
                    blen = max(f["length"] * nrm,
                               foreshorten_floor(f["length"]))
                    if rhythm is not None:
                        # R9: this screw is the second step of a chain whose
                        # first step the bracket has already taken. The gap is
                        # the group's rhythm exactly - not a hop this screw
                        # negotiates for itself - so seat, bracket and point
                        # come out evenly spaced along one movement outward.
                        # Nothing is looked up in the field and nothing queues:
                        # a group that needs more room takes a longer beat, and
                        # it takes it in float_plate(), for all of its screws
                        # at once.
                        shift = group_shift(view, f, rhythm)
                    else:
                        # The hop is the drawn body plus air, grown along the
                        # axis if that is what it takes to find paper.
                        out = clear_back(occ, (hole[0] + poff[0],
                                               hole[1] + poff[1]),
                                         (ux, uy), blen, blen + hover,
                                         hover, f["d"] * SCREW_FATTEN * 0.75)
                        # ...and then out again, one body at a time, until it
                        # is clear of every body already on the page. QUEUE_MAX
                        # is where it gives up and overlaps rather than ending
                        # up in the next county: at that point the two really
                        # are one place and the drawing says so by drawing them
                        # there. Coaxial screws queue up BEHIND one another on
                        # the shared axis - never beside it - so every one of
                        # them still points at the hole it belongs to.
                        for q in range(QUEUE_MAX):
                            back = (out + (blen + hover) * q) / nrm
                            shift = tuple(-c * back for c in f["direction"])
                            cap = body_capsule(view, f, shift, poff,
                                               ring=m.get("ring"))
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
            drawn_caps.append(body_capsule(view, f, shift, poff,
                                           ring=m.get("ring")))
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
                # Into the record with everything else that went on the paper:
                # R9's two asserts - equal steps, and no two lines in a group
                # crossing - are questions about these segments, and they are
                # asked of the ink rather than of the offsets that produced it.
                page.record.append(dict(kind="tether", owner=id(f),
                                        jid=m["jid"], name=f["name"],
                                        group=group, seg=(start, entry)))
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
        # The body as it was actually drawn, off the page's own record: R6
        # asks whether the badge touches THAT, so it is the ink that answers
        # and not the offset that was computed.
        drawn = [r for r in page.record
                 if r["kind"] in ("screw", "plate")
                 and r.get("mark") == mark_owner(m)]
        if f["kind"] == "plate" and drawn and style == "eksplodert":
            # A bracket is barely bigger than the badge that names it - a 40 mm
            # angle and a 49 mm circle - so a badge that satisfies R6 by
            # sitting ON it satisfies it by HIDING it, and the reader is left
            # with a letter where the part should be. The tail therefore sits
            # on the bracket's own RIM, on the bearing badge_gap_dir() picked -
            # the widest gap between the group's own links (R10) - so the first
            # candidate in the ladder is a badge tangent to the plate rather
            # than one centred on it: contact, the bracket still visible under
            # its own letter, and the chain not walked over to get there.
            c0, _c1, rad = drawn[-1]["cap"]
            label_at = (c0[0] - label_dir[0] * rad,
                        c0[1] - label_dir[1] * rad)
        captions.append(dict(at=label_at, dir=label_dir, letter=m["letter"],
                             owner=mark_owner(m), jid=m["jid"],
                             body=drawn[-1]["cap"] if drawn else None,
                             # HOW LONG THIS ONE CAME OUT, off the drawn
                             # silhouette's own axis: it is what the R7
                             # amendment asks, and a screw's appearance is not
                             # its catalogue length but the length the camera
                             # left it with. None for a bracket, which has no
                             # axis to compare; zero for a head-on ringed dot,
                             # which looks like nothing else on the page and
                             # should not be merged with anything.
                             plen=drawn_length(drawn[-1] if drawn else None)))

    # THE CAPTIONS, once every fastener is down. Placing each one as its own
    # fastener was drawn is what let the second badge on a crowded corner park
    # itself neatly on top of the ninth screw - which had not been drawn yet,
    # so nothing objected. A caption that sits on a fastener it does not name
    # is worse than no caption: it is a wrong one.
    # R10: the chain corridors, off the tethers that have just been written.
    # Every fastener is down and no caption is placed yet, which is the one
    # moment the whole of every chain exists and nothing is standing in it.
    corridors = chain_corridors(page)
    for c in thin_clusters(captions):
        mark_label(page, c["at"], c["dir"], c["letter"], occ, c["owner"],
                   c["body"], family=c["family"], corridors=corridors)
    if style == "eksplodert":
        assert_bodies_apart(page)
        assert_chain_rhythm(page)
        assert_chain_untangled(page)
        assert_badges_clear_chain(page)
    assert_no_stubs(page)
    assert_badges_anchored(page)
    assert_badges_cover(page)
    assert_badges_homogeneous(page)
    assert_marks_own_element(page, occ)
    if not st.get("no_fasteners"):
        assert_joint_marks_drawn(page, st, marks)

    # THE MAGNIFIER, on a page whose whole fastening is in one or two places.
    # It carries real line work and its short leader says which spot has been
    # blown up, which is why it stayed when the panel's leaders went (R3: the
    # panel used to trail four grey dashed lines to the nearest fastening
    # points, and the badge letters already said what they said).
    # It used to be parked under the fastener panel and sized off it. With the
    # panel gone it is placed the way every other block on this page is
    # placed - through emptiest_corner, on its own square footprint - so the
    # lens lands where the drawing is not instead of where the list used to
    # be, and it keeps clear of the mirror pictogram if the page has one.
    if keep and fasteners:
        if len(mark_clusters(keep, T.BADGE_R * 2)) <= 2:
            src = keep[0]["p2"]
            src_r = max(page.w, page.h) * 0.055
            dst_r = page.w * LENS_R_FRAC
            lx, ly = emptiest_corner(combined.get("prior", []),
                                     page, 2 * dst_r, 2 * dst_r, keep,
                                     avoid=tuple(b for b in (box, note_box)
                                                 if b is not None),
                                     subject=new_only + dim_ink_lines)
            dst_c = (lx + dst_r, ly + dst_r)
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
    page.write(svg, width)
    to_png(svg, png, width)
    for f_name, *_rest in fasteners:
        ALL_FASTENERS.setdefault(f_name, n)
    if letters:
        PAGE_SCALES[n] = width / page.w
        PAGE_FASTENERS[n] = list(fasteners)
        if page.fill_spans:
            PAGE_FILL_SCALES[n] = width / page.w
    print(f"  steg {n:2d}  {len(combined.get('prior', [])):4d} gra / "
          f"{len(new_only):4d} svarte / {len(keep):2d} festepunkt"
          + (f" / {len(dim_plans)} mål" if dim_plans else "")
          + (f" / vegg m/{studs} stendere" if studs else "")
          + f" -> {png}")
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
# a fill code appears on. The SHEET is rastered at the largest of them, so its
# own labels stay readable, and the row that matters is drawn at the smallest:
# the exploded panel page is 3458 mm wide against step 1's 1114, so a fastener
# there is drawn at a third of the size, and that ratio is the worst case the
# manual actually contains. It is written to docs/preview/, beside the page
# previews, because it is review material and not part of the manual.
# One home, in tools/layout.py, because tools/render_panel.py imports this
# module back and would otherwise fill in a second copy of these - see the
# note there.
PAGE_SCALES = layout.PAGE_SCALES
PAGE_FASTENERS = layout.PAGE_FASTENERS
PAGE_FILL_SCALES = layout.PAGE_FILL_SCALES
ALL_FASTENERS = layout.ALL_FASTENERS
# The set in letter order, plus the one candidate that did not make it: dots
# reads well enough at page size but is the first to go to grey at half, and
# four codes is all a step has ever needed. It stays in the proof so that the
# next person to want a fifth can see what they are buying.
PROOF_EXTRA = ("dots",)


def _pct(frac):
    return f"{frac * 100:.1f}".replace(".", ",") + " %"


def assert_fill_code_rule(data):
    """The fill code's SAFETY DIRECTION, measured on the ink that landed.

    The rule that switches the code on is derived data (see
    tools/gen_doc_tables.step_fill_code), and derived data can be wrong in two
    directions that are not worth the same. A page that PUTS the code on a set
    the silhouette already separates is only busier than it needed to be - it
    is reported and the build goes on. A page whose set contains a pair the
    silhouette does NOT separate, and which draws them bare anyway, has taken
    the reader's only remaining way of telling two screws apart away from
    them. That is the failure, and it is checked here rather than trusted,
    because it is checked against what was DRAWN: `PAGE_FILL_SCALES` is
    written by the pages themselves as they put a pattern on paper, so a
    plumbing mistake between the step data and the paint cannot pass.
    """
    import gen_glyphs
    declared = {st["n"]: bool(st.get("fill_code")) for st in data["steps"]}
    coded = []
    for n in sorted(PAGE_FASTENERS):
        names = [row[0] for row in PAGE_FASTENERS[n]]
        pairs = gen_glyphs.ambiguous_pairs(names)
        drawn = n in PAGE_FILL_SCALES
        detail = "; ".join(f"{a} / {b}: {_pct(frac)}, Ø{dd:g} mm"
                           for a, b, frac, dd in pairs)
        if pairs:
            assert declared.get(n), (
                f"steg {n}: {detail} — formen skiller dem ikke, men steget "
                f"er ikke merket med fyllkode i byggesteg.json")
            assert drawn, (
                f"steg {n}: {detail} — formen skiller dem ikke, og siden "
                f"tegner dem uten fyll. Da har leseren ingenting igjen å "
                f"skille dem på")
            coded.append(f"steg {n} ({detail})")
        elif drawn:
            print(f"  ! steg {n} bærer fyllkode, men ingen to festemidler på "
                  f"siden er nære nok i form til å trenge den")
    print("  fyllkode: " + ("; ".join(coded) if coded
                            else "ingen side trengte den"))


def fill_contrast_strip(out_dir, px_per_mm, worst=None):
    """docs/preview/fyllkontrast.{svg,png} - every fill code at page size.

    `px_per_mm` is the sheet's own raster, i.e. the LARGEST scale a lettered
    page is drawn at; `worst` the smallest, which the stress row is drawn at.
    """
    import gen_glyphs
    k_worst = (worst / px_per_mm) if worst else 0.5
    patterns = tuple(gen_glyphs.FILL_CODES) + PROOF_EXTRA
    heads = [f"{gen_glyphs.BADGE_ALPHABET[i]}  {c.upper()}"
             if i < len(gen_glyphs.FILL_CODES) else f"({c.upper()})"
             for i, c in enumerate(patterns)]
    col = 118.0
    lab = 150.0
    rows = [
        ("5x40 EKSPLODERT", "screw", 5.0, 40.0, 1.0),
        ("6x90 EKSPLODERT", "screw", 6.0, 90.0, 1.0),
        ("5x60 I SITU (FANTOM)", "situ", 5.0, 60.0, 1.0),
        ("5x60 HODET ALENE", "head", 5.0, 0.30, 1.0),
        # The smallest a fastener is ever drawn in this manual: the same 5x40,
        # on the widest page there is. The pattern it carries is the sheet's,
        # which is the pattern a FULL-SIZE page gets, so this row is a shade
        # harsher than the real step 10 - that page derives a coarser period
        # off its own scale. A stress row is allowed to be pessimistic.
        (f"5x40 PA MINSTE SIDESKALA ({k_worst:.2f}x)", "screw",
         5.0, 40.0, k_worst),
        # And half of that again, which no page asks for - the margin the set
        # has left before it stops coding anything.
        ("5x40 PA HALVE DET IGJEN", "screw", 5.0, 40.0, k_worst * 0.5),
        # THE ROW THE PROOF WAS MISSING, and the one the bug lived in: the
        # glyph as the step's own fastener table sets it, at the pixel height
        # docs/MONTERING.md actually writes into the <img> tag. Everything
        # above is drawn by this file at page scale; this row is the OTHER
        # drawing of a fastener the manual has, rendered through the same
        # embedding the inset panel uses, so the two sit side by side and the
        # reader of the proof can see whether they say the same thing.
        ("TABELLGLYF 6x60 @30 px", "glyph", 6.0, 60.0, 1.0),
        ("TABELLGLYF 5x40 @30 px", "glyph", 5.0, 40.0, 1.0),
    ]
    row_h = 34.0
    w = lab + col * len(patterns) + 20.0
    h = 42.0 + row_h * len(rows) + 16.0
    page = Page(0.0, 0.0, w, h)
    # The proof has to be drawn at the raster it is proving, because the
    # thread on a silhouette is chosen by that raster exactly as the fill's
    # period is (gen_glyphs.thread_pitch).
    page.px_per_unit = px_per_mm
    top = h - 16.0
    page.text((10.0, top), "FYLLKODE - KONTRASTPROVE", 13.0, weight="bold")
    page.text((10.0, top - 15.0),
              f"tegnet i {px_per_mm:.2f} px per mm - den storste stegsidens "
              f"egen skala", 9.5)
    top -= 34.0
    for i, head in enumerate(heads):
        page.text((lab + col * i + col / 2, top), head, 10.0,
                  anchor="middle", weight="bold")
    top -= 6.0
    for label, kind, d, arg, k in rows:
        cy = top - row_h / 2
        page.text((lab - 12.0, cy - 3.5), label, 9.5, anchor="end")
        for i, code in enumerate(patterns):
            x = lab + col * i + 8.0
            if kind == "glyph":
                # The step table's own glyph, at the height docs/MONTERING.md
                # sets it: gen_glyphs picks the period off that height, so the
                # only honest way to prove it is to embed the real file at the
                # real size. GLYPH_MIN_PX device pixels is
                # GLYPH_MIN_PX / px_per_mm millimetres on this strip.
                name = f"Treskrue {d:g}×{arg:g} forsenket Torx"
                raw = gen_glyphs.fastener_svg(name, code)
                m = re.search(r'viewBox="[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+'
                              r'([\d.]+)"', raw)
                gw, gh = float(m.group(1)), float(m.group(2))
                eh = gen_glyphs.GLYPH_MIN_PX / px_per_mm
                page.embed_svg_text(raw, x, cy - eh / 2, eh * gw / gh, eh)
                continue
            # No span declared on purpose: the proof has to carry the pattern
            # a STEP PAGE would give it, not one fitted to the proof's own
            # rows, or the half-scale stress row would quietly make every row
            # above it finer and the proof would stop proving the manual.
            paint = page.fill_paint(code)
            # R8: the code takes the body from the thread, and only where the
            # code is a pattern. The proof shows exactly that, or it is
            # proving a drawing the manual does not make.
            thr = thread_cues(code)
            if kind == "screw":
                pts = screw_outline((x, cy), (1.0, 0.0), arg * k, d * k,
                                    px_per_unit=px_per_mm, threads=thr)
                page.poly(pts, fill=paint, stroke=INK, width=T.W_SCREW * k)
            elif kind == "situ":
                # Buried in wood: the outline is a phantom line and only the
                # head is solid, so the fill has the whole body to live in but
                # no continuous edge round it.
                pts = screw_outline((x, cy), (1.0, 0.0), arg * k, d * k,
                                    px_per_unit=px_per_mm, threads=thr)
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
        page.line((10.0, top - row_h), (w - 10.0, top - row_h), GREY,
                  T.W_LEAD * 0.5)
        top -= row_h
    page.fills |= set(patterns)
    os.makedirs(out_dir, exist_ok=True)
    svg = os.path.join(out_dir, "fyllkontrast.svg")
    png = os.path.join(out_dir, "fyllkontrast.png")
    page.write(svg, w * px_per_mm)
    to_png(svg, png, int(round(w * px_per_mm)))
    print(f"  fyllkontrast  {w:.0f} x {h:.0f} mm @ {px_per_mm:.2f} px/mm "
          f"-> {png}")
    return png


# ---------------------------------------------------------------------------
# THE SHAPE PROOF
# ---------------------------------------------------------------------------
# The fill code exists because SHAPE was judged not to be enough. This proof
# is that judgement put back on the table, drawn instead of asserted.
#
# It asks the question in the form the reader actually meets it. Not "can you
# tell eight screws apart" - nobody is ever shown eight at once - but "on THIS
# page, with THESE two to four types beside each other at the size the page
# draws them, does the silhouette separate them on its own". A 5x40 next to a
# 6x120 is three times the length and it is no contest; a 6x80 next to a 6x90
# is twelve per cent, and twelve per cent of a screw is what the fill code was
# bought for. The proof lays both cases out, bare and then filled, so the
# answer is looked at rather than argued.
def _screw_dims(name):
    """(d, length) for a fastener that has an axis, else None.

    One definition, in the file that draws the glyphs and owns the rule that
    reads these two numbers (PRAKSIS §1).
    """
    import gen_glyphs
    return gen_glyphs.screw_dims(name)


def form_contrast_strip(out_dir, px_per_mm):
    """docs/preview/formkontrast.{svg,png} - can the SILHOUETTE carry the code?

    Drawn in model millimetres and rastered at `px_per_mm`, the smallest scale
    any lettered step page is rendered at, so a screw drawn here at its page
    size comes out the pixel size the reader is given.
    """
    import gen_glyphs
    steps = sorted(PAGE_FASTENERS)
    # Every type the manual uses - off ALL_FASTENERS and not off the lettered
    # pages, because the wall fixing and the M6 set live on pages that carry
    # one kind of fastener and therefore no letters at all. Longest first.
    every = {name: _screw_dims(name) for name in ALL_FASTENERS}
    every = {k: v for k, v in every.items() if v}
    order = sorted(every, key=lambda k: (-every[k][1], -every[k][0], k))

    lab = 260.0
    row_h = 30.0
    head_h = 26.0
    gap = 14.0
    tab_h = gen_glyphs.GLYPH_MIN_PX / px_per_mm      # 30 px, in millimetres

    # Width: the longest screw anything on the sheet draws, plus the gutters.
    longest = max([L for _d, L in every.values()]
                  + [d_L[1] * PAGE_SCALES[n] / px_per_mm
                     for n in steps
                     for d_L in [_screw_dims(r[0]) for r in PAGE_FASTENERS[n]]
                     if d_L])
    w = max(lab + longest + 100.0, 620.0)
    n_rows = (len(order) * 2                      # section 1: scene + table
              + sum(len(PAGE_FASTENERS[n]) for n in steps) * 2)  # 2 and 3
    h = (44.0 + 4 * (head_h * 0.55 + 8.0) + len(steps) * 2 * (head_h * 0.8)
         + n_rows * row_h + len(steps) * 2 * 6.0 + 30.0)
    page = Page(0.0, 0.0, w, h)
    page.px_per_unit = px_per_mm
    top = h - 16.0
    page.text((10.0, top), "FORMKONTRAST - BAERER SILHUETTEN KODEN?", 13.0,
              weight="bold")
    top -= 15.0
    page.text((10.0, top),
              f"sann lengde og sann diameter, {SCREW_FATTEN:g}x fortykket som "
              f"paa sidene - tegnet i {px_per_mm:.2f} px per mm", 9.5)
    top -= 22.0

    def heading(text, size=11.0):
        nonlocal top
        page.text((10.0, top), text, size, weight="bold")
        top -= head_h * 0.55

    def rule():
        nonlocal top
        page.line((10.0, top), (w - 10.0, top), GREY, T.W_LEAD * 0.5)
        top -= 8.0

    def scene_row(label, d, L, tag, code=None, name=None):
        """One screw at the size a step page draws it."""
        nonlocal top
        cy = top - row_h / 2
        page.text((lab - 12.0, cy - 3.5), label, 9.0, anchor="end")
        paint = page.fill_paint(code) if code else "#ffffff"
        page.poly(screw_outline((lab, cy), (1.0, 0.0), L, d, name=name,
                                px_per_unit=px_per_mm,
                                threads=thread_cues(code)),
                  fill=paint, stroke=INK, width=T.W_SCREW)
        page.text((lab + L + 10.0, cy - 3.5), tag, 9.0)
        top -= row_h

    # ---- 1. every type, bare, at both sizes -------------------------------
    heading("1  ALLE TYPER, BAR SILHUETT - SCENESKALA (stegsiden)")
    for name in order:
        d, L = every[name]
        scene_row(_short(name), d, L, f"{d:g}x{L:g}", name=name)
    rule()
    heading(f"1b ALLE TYPER, BAR SILHUETT - TABELLSKALA "
            f"({gen_glyphs.GLYPH_MIN_PX:.0f} px, tabellen under bildet)")
    for name in order:
        d, L = every[name]
        cy = top - row_h / 2
        page.text((lab - 12.0, cy - 3.5), _short(name), 9.0, anchor="end")
        raw = gen_glyphs.fastener_svg(name)
        m = re.search(r'viewBox="[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)"',
                      raw)
        gw, gh = float(m.group(1)), float(m.group(2))
        page.embed_svg_text(raw, lab, cy - tab_h / 2, tab_h * gw / gh, tab_h)
        page.text((lab + tab_h * gw / gh + 10.0, cy - 3.5), f"{d:g}x{L:g}",
                  9.0)
        top -= row_h
    rule()

    # ---- 2 and 3. the pages' own sets, bare and then coded ----------------
    for coded in (False, True):
        heading("3  SAMME SETT MED FYLLKODE" if coded else
                "2  SETTET HVER SIDE FAKTISK VISER, BAR SILHUETT")
        for n in steps:
            k = PAGE_SCALES[n] / px_per_mm
            note = "" if n in PAGE_FILL_SCALES else \
                "  - siden tegner ingen skruekropper; tabellen er eneste sted"
            page.text((10.0, top - 10.0),
                      f"STEG {n}   ({PAGE_SCALES[n]:.2f} px/mm){note}", 9.5,
                      weight="bold")
            top -= head_h * 0.8
            for name, qty, _svg, letter in PAGE_FASTENERS[n]:
                dims = _screw_dims(name)
                if dims is None:
                    cy = top - row_h / 2
                    page.text((lab - 12.0, cy - 3.5),
                              f"{letter}  {_short(name)}", 9.0, anchor="end")
                    page.text((lab, cy - 3.5), "(beslag - ingen akse)", 9.0)
                    top -= row_h
                    continue
                d, L = dims
                scene_row(f"{letter}  {_short(name)}  {qty}x", d * k, L * k,
                          f"{d:g}x{L:g}",
                          gen_glyphs.fill_code(letter) if coded else None,
                          name=name)
            top -= 6.0
        rule()

    os.makedirs(out_dir, exist_ok=True)
    svg = os.path.join(out_dir, "formkontrast.svg")
    png = os.path.join(out_dir, "formkontrast.png")
    page.write(svg, w * px_per_mm)
    to_png(svg, png, int(round(w * px_per_mm)))
    print(f"  formkontrast  {w:.0f} x {h:.0f} mm @ {px_per_mm:.2f} px/mm "
          f"-> {png}")
    return png


def _short(name):
    """The trade name without the boilerplate, for a proof's label column."""
    if name.startswith("Veggfeste"):
        return "Veggfeste 8×100"
    if name.startswith("Senkhodeskrue"):
        return "Senkhodeskrue M6×30 + skive + mutter"
    for tail in (" forsenket Torx", " varmforsinket"):
        name = name.replace(tail, "")
    return name.replace(", bøyd av flattstål 30×4", "")


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
    # FOUR KINDS TO A PAGE, and the limit is the fill code's, not a panel's.
    # gen_glyphs.FILL_CODES has four patterns, one per badge letter, and a
    # fifth kind on a coded page would come out with `code=None` - a bare
    # silhouette among four patterned ones, which is exactly the thing the
    # code exists to prevent. No step has ever needed five; the day one does,
    # the SET has to grow (a fifth pattern, proven in the contrast strip) -
    # the fifth type may not quietly go uncoded.
    assert len(rows) <= len(gen_glyphs.FILL_CODES), (
        f"steg {st['n']} driver {len(rows)} slags festemidler, og fyllkoden "
        f"har {len(gen_glyphs.FILL_CODES)} mønstre. Den femte typen ville "
        f"blitt tegnet uten kode blant fire kodede. Utvid "
        f"gen_glyphs.FILL_CODES før steget får en femte type.")
    letters = gen_glyphs.BADGE_ALPHABET if len(rows) > 1 else [None] * len(rows)
    coded = bool(st.get("fill_code"))

    out = []
    for (name, qty), letter in zip(rows, letters):
        # The panel row shows the glyph with its own fill code in it, which is
        # the same file the step's table under the picture uses: the row is
        # where the reader meets the pattern and the letter side by side. On a
        # page the rule left bare, that file is the bare glyph - the row shows
        # what the drawing shows.
        code = gen_glyphs.fill_code(letter) if coded else None
        svg = gen_glyphs.coded_slug(name, code) + ".svg"
        if not os.path.exists(os.path.join(glyph_dir, svg)):
            svg = gen_glyphs.slug(name) + ".svg"
        # A missing glyph must STOP the build, not thin the page: this list is
        # also what check_coverage() counts against, so a silently dropped row
        # was a fastener kind exempted from the completeness check as well as
        # from the panel.
        assert os.path.exists(os.path.join(glyph_dir, svg)), (
            f"steg {st['n']}: ingen glyf for '{name}' ({svg} finnes ikke i "
            f"{glyph_dir}) - kjør `mise run build` så gen_doc_tables/"
            f"gen_glyphs skriver den, eller legg navnet inn i glyphmaskineriet")
        out.append((name, qty, svg, letter))
    return out


def crop_to_subject(view, page_box, st, new_parts):
    """A tighter page for a step whose subject is a narrow thing in a wide bed.

    Every page is cut from the FINISHED bed, so nothing jumps between drawings
    - and that is right for the ten steps that build across the whole 1990 mm
    of it. The ladder is not one of them: it is 416 mm wide and 2037 tall, and
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
    sw = bx1 - bx0
    mx = sw * 1.05                         # room for arrows and badges
    # ...AND ROOM FOR WHATEVER OPAQUE BLOCK THIS STEP PARKS IN A CORNER, which
    # is not an annotation the crop may leave out: every one of them is a
    # fraction of the FINISHED page width and every one of emptiest_corner()'s
    # candidates puts it in a side margin. Cut the page to 1.05 subject widths
    # and that margin comes out 437 mm against a 445 mm block, so all four
    # corners cover the ladder and the placer's only decision is which upright
    # to hide - which is how the fastener list used to end up lying over the
    # right stile's top.
    #
    # The margin that can hold a block of fraction f is the fixed point of
    #     mx = f * (sw + 2 mx) + PANEL_EDGE + PANEL_GROW + PANEL_CLEAR
    # and it is solved rather than guessed, so the day a block or the crop
    # changes width the page follows it instead of going quietly opaque.
    #
    # WHICH blocks - the step says, except for the lens, which any page can
    # earn by having all its fastening in one place, so it is always allowed
    # for. The fastener list is gone from the sheets (erfaringsrunde 1), so
    # the widest thing left is the mirror pictogram on a half view, then the
    # mattress page's information panel, then the lens - and a step that
    # carries only the lens, as the ladder does, keeps the rest of the margin
    # for its own drawing, which is what the crop is for.
    f = max([2 * LENS_R_FRAC]
            + [frac for key, frac in CORNER_BLOCK_FRAC.items() if st.get(key)])
    room = ((f * sw + PANEL_EDGE + PANEL_GROW + PANEL_CLEAR)
            / (1.0 - 2 * f))
    mx = max(mx, room)
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
    # X15: what every step owes in placement measures, derived once off the
    # model. The pages draw from this list and nothing else, and the ink
    # assert at the bottom of this function reads the finished files back
    # against the same list.
    import step_dims
    owed = step_dims.owed(G, data["steps"])

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
                box = crop_to_subject(views[key], box, st,
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
                                  families, centre, half,
                                  dims=owed.get(n, ()))
            if png:
                made.append(png)
        placed += st["labels"]
    if only is None:
        # Every page has been drawn, so the question can be asked of all of
        # them at once. On a single-step run there is nothing to ask it of.
        assert_fill_code_rule(data)
        # X15's bijection, and it is asked of the FILES. Every figure that
        # came out on a step sheet against every figure the model says that
        # step owes - so a measure that quietly stopped being drawn cannot
        # look like a step that never owed one.
        sheets = {}
        for st in data["steps"]:
            path = os.path.join(out_dir, f"steg-{st['n']:02d}.svg")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as fh:
                    sheets[st["n"]] = fh.read()
        drawn = step_dims.assert_ink(G, data["steps"], sheets)
        n_dim = sum(1 for r in sum(owed.values(), []) if r["kind"] == "mål")
        print(f"  X15 plasseringsmål: {drawn} tegnet over "
              f"{len([n for n in owed if owed[n]])} stegark - {n_dim} pil"
              f"er og {drawn - n_dim} «{step_dims.FLUSH_WORD}», hver enkelt "
              f"målt tilbake gjennom projeksjonen og mot modellen")
    return made


# THE COVER DRAWING IS IN TABLE MODE, and that is the builder's call: "the
# cover picture ought to be table mode". It is the right one. The frame is the
# same frame in both positions, so a cover in bed mode shows a loft bed with a
# board lying in the sofa - and hides the one thing that makes this bed worth
# building, which is that the board goes UP and becomes a desk at 700. The
# dimension sheet on the page after it stands in the same position, so the two
# front pages are the same bed and the reader never has to re-learn it.
def render_hero(G, out_dir, width, az=330, elev=22):
    use_model(G)
    bed = table_bed(G)
    look_at = bed.bounding_box().center()
    view = View(camera_direction(az, elev), look_at)
    plines = project(view, [("all", bed)])["all"]
    x0, y0, x1, y1 = bounds(plines)
    page = Page(x0 - T.PAD, y0 - T.PAD, x1 + T.PAD, y1 + T.PAD)
    page.polylines(plines, INK, T.W_HERO)
    svg = os.path.join(out_dir, "hanna-hero.svg")
    png = os.path.join(out_dir, "hanna-hero.png")
    page.write(svg, width)
    to_png(svg, png, width)
    print(f"  hero    az {az} elev {elev}  {len(plines)} kanter  -> {png}")
    return png


# ---------------------------------------------------------------------------
# BRUKSARKENE - the two positions with the people in them
# ---------------------------------------------------------------------------
# One page per position, and both of them are a TRUE ELEVATION: azimuth 0,
# elevation 0, so the page's vertical axis IS the model's Z and a dimension
# line between two heights is the difference between two numbers in
# generate_loftbed.py. Nothing on these two pages is typed - every figure is a
# solid, every clearance is measured off those solids in the model's own
# validation block, and the text below the arrow prints that measurement.
#
# THE BED IS GREY AND THE PEOPLE ARE BLACK, and they are two separate hidden-
# line runs on purpose, laid one over the other. A reference body is not part
# of the subject: it must never occlude a board (it would be drawing a child
# in front of a guard rail that is in front of the child), and it must never
# be occluded either, or the one thing the page is about disappears behind the
# ladder. Same layering the mechanism sheets use for the panel unit.
BRUK_SHEETS = {
    "bed_mode": ("bruk-sengestilling", "SENGESTILLING — TO SOM SOVER"),
    "table_mode": ("bruk-bordstilling", "BORDSTILLING — TO SOM SITTER"),
}


def _bruk_dims(G, mode):
    """[(kind, along, from, to, mm, words, where)] - the dimension lines.

    'v' is a vertical dimension standing at model X = `along`, 'h' a
    horizontal one at model Z = `along`. `where` puts the WORDS clear of the
    line work - "top", "bot" or "side" - and it is chosen per dimension
    because the page is a drawing, not a table. Every number comes out of the
    model's measured-clearance block; not one is typed here.

    THE NUMBER AND THE WORDS ARE TWO THINGS. They used to be one string with
    the figure glued to the front of it, drawn beside the arrow - which meant
    the one thing on the page that had to be read at a glance was set in the
    same weight as the sentence explaining it. The figure goes ON the arrow
    now, bold and with its unit, by the same Page.dimension() the measurement
    sheet uses; the sentence stays where it was and says what the figure
    means. Neither carries the other's job.
    """
    if mode == "bed_mode":
        up, lo = G.figure_lying_upper, G.figure_lying_lower
        return [
            ("v", up.pose["head"][0], up.pose["head"][2] + G.FIG_HEAD_R,
             G.GUARD_TOP, G.GUARD_OVER_FACE, "rekkverk over ansiktet", "top"),
            ("v", up.extents[0][1] - 60, up.extents[2][1], G.GUARD_TOP,
             G.GUARD_OVER_BODY, "over kroppen", "top"),
            ("h", G.GUARD_TOP + 55, up.extents[0][1], G.WALL_SPAN,
             G.WALL_SPAN - up.extents[0][1], "madrass igjen bak føttene",
             "top"),
            ("v", lo.pose["head"][0], lo.pose["head"][2] + G.FIG_HEAD_R,
             G.SLAT_Z1 - G.BED_SLAT_T,
             G.LIE_LOWER_FACE, "fri høyde over ansiktet nede", "side"),
        ]
    right = G.figure_seated_right
    return [
        ("v", right.pose["crown"][0], right.pose["crown"][2],
         G.SLAT_Z1 - G.BED_SLAT_T,
         G.SIT_HEADROOM, "over hodet — man sitter helt rett opp", "side"),
        ("v", right.pose["crown"][0] - 250, G.SEAT_FACE,
         right.pose["crown"][2],
         G.FIG_SITTING_H, "sittehøyde (0,545 H)", "top"),
        ("v", G.PANEL_X0 + G.PANEL_W / 2, G.SEAT_FACE, G.PANEL_TOP_TABLE,
         G.TABLE_OVER_SEAT, "plate over sete", "top"),
        # The knee gap is a short dimension in a narrow gap, so it carries the
        # number alone - what it means is one line down in the caption. X9:
        # the knees are UNDER the plate now, so what this measures is the
        # nearest approach of body to plate, not a folded leg stopping short.
        ("h", G.FIG_SIT_Z + 20, G.panel_table.extents[0][1],
         right.extents[0][0], G.LEG_TO_TABLE, "", "top"),
        # X14: and the floor the soles actually stand on. It is the one
        # dimension on this sheet that is a piece of wood rather than a gap.
        ("v", G.FOOTREST_DECK_X[1] + 40, 0, G.FOOTREST_TOP,
         G.FOOTREST_TOP, "fotbrett", "side"),
    ]


BRUK_NOTE = {
    "bed_mode":
        "Kroppene er tegnet i et eget lag OVER sengen, ikke bak den: en "
        "referansekropp skal verken skjule et bord eller skjules av et.",
    "table_mode":
        # X9: the pose is an ordinary sit now, so the note says what it
        # measures. The history - 140/122 and cross-legged until v15 - is in
        # nøkkelmål and in ASSEMBLY; this line has one page width to live in.
        "Alminnelig sitting, og det er et måleresultat: platen ligger "
        "{over:.0f} mm over seteflaten og har {under:.0f} mm under seg, så "
        "knærne går inn under den. Tallet i sjakten er {leg:.0f} mm — "
        "nærmeste kropp til platen. Sålene står på fotbrettet (X14) og "
        "henger ikke: {foot:.0f} mm over gulvet, leggen i lodd og foten "
        "flatt.",
}


def render_bruk(G, out_dir, width):
    """The two use sheets: bed mode with two sleepers, table mode with two
    sitting at the plate. Returns the PNG paths."""
    use_model(G)
    made = []
    for mode, (stem, head) in BRUK_SHEETS.items():
        panel = G.MODES[mode]
        bed = comp([p for p in G.mode_parts(panel)])
        people = comp(G.FIGURES[id(panel)])
        look_at = bed.bounding_box().center()
        view = View(camera_direction(0, 0), look_at)
        bed_lines = project(view, [("b", bed)])["b"]
        fig_lines = project(view, [("f", people)])["f"]

        x0, y0, x1, y1 = bounds(bed_lines + fig_lines)
        pad, lead = T.PAD * 1.6, T.BADGE_R * 4.2
        page = Page(x0 - pad - lead, y0 - pad - lead * 0.8,
                    x1 + pad + lead, y1 + pad + lead * 1.6)
        page.polylines(bed_lines, GREY, T.W_NEW * 0.5)
        page.polylines(fig_lines, INK, T.W_NEW * 0.5)

        tick, size = T.BADGE_R * 0.55, T.BADGE_R * 0.78
        dim_sz = T.BADGE_R * 0.95
        for kind, along, a, b, mm, words, where in _bruk_dims(G, mode):
            if kind == "v":
                p0, p1 = view.xy((along, 0, a)), view.xy((along, 0, b))
            else:
                p0, p1 = view.xy((a, 0, along)), view.xy((b, 0, along))
            mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            # The end marks stay: with no offset there are no witness lines,
            # and a dimension has to show WHERE it stopped.
            for end in (p0, p1):
                page.line((end[0] - tick, end[1]) if kind == "v"
                          else (end[0], end[1] - tick),
                          (end[0] + tick, end[1]) if kind == "v"
                          else (end[0], end[1] + tick), GREY, T.W_LEAD)
            page.dimension(p0, p1, f"{mm:.0f} mm", size=dim_sz)
            if not words:
                continue
            # A sentence written across a child is a sentence nobody reads, so
            # every one of them says for itself which way it steps out of the
            # way.
            hi = p0 if p0[1] >= p1[1] else p1
            lo = p0 if p0[1] < p1[1] else p1
            if where == "top":
                page.text((hi[0], hi[1] + size * 0.6), words, size,
                          anchor="middle")
            elif where == "bot":
                page.text((lo[0], lo[1] - size * 1.35), words, size,
                          anchor="middle")
            else:
                page.text((mid[0] + dim_sz * 0.9, mid[1] - size * 0.32),
                          words, size)

        top = page.y1 - T.BADGE_R * 1.4
        page.text((page.x0 + T.BADGE_R, top), head, T.BADGE_R * 1.5,
                  weight="bold")
        # THE NOTES ARE WRAPPED TO THE SHEET, not written and hoped for. The
        # first of them is 286 characters and ran a third of its length off
        # the right-hand edge for as long as it has existed - which is the one
        # drawing fault a proof render always shows and a code review never
        # does. Page.wrap() measures the column in the page's own units, so
        # the answer follows the sheet whatever size the bed is.
        note_sz = T.BADGE_R * 0.72
        col = page.w - T.BADGE_R * 2.0
        rows = page.wrap(
            f"Referansekroppen er et barn på {G.FIGURE_H:.0f} mm "
            f"(EN 747, alder 6+), bygget som én solid av 14 primitiver "
            f"etter AnthroKids (Snyder m.fl. 1977). Grått = sengen, "
            f"svart = kroppen. Kroppen er ikke en del: den kappes ikke, "
            f"bærer ingenting og står i ingen liste — men hvert mål på "
            f"arket er målt på den.", col, note_sz)
        rows += page.wrap(
            BRUK_NOTE[mode].format(
                over=G.TABLE_OVER_SEAT, under=G.TABLE_UNDER_SEAT,
                thigh=2 * G.FIG_THIGH_R, leg=G.LEG_TO_TABLE,
                foot=G.FOOTREST_TOP), col, note_sz)
        y = top - T.BADGE_R * 1.7
        for row in rows:
            page.text((page.x0 + T.BADGE_R, y), row, note_sz)
            y -= note_sz * 1.35
        assert y > page.y1 - T.PAD * 1.6 - T.BADGE_R * 4.2 * 1.6, \
            (f"bruksarkets {len(rows)} notatlinjer går ned i tegningen - "
             f"marginen over motivet må vokse")
        svg = os.path.join(out_dir, f"{stem}.svg")
        png = os.path.join(out_dir, f"{stem}.png")
        page.write(svg, width)
        to_png(svg, png, width)
        print(f"  bruk    {mode:11s} {len(bed_lines):4d} kanter seng + "
              f"{len(fig_lines)} silhuett  -> {png}")
        made += [png]
    return made


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
        made += render_bruk(G, out_dir, width)
        # The pre-step's figure. It is not a projection of anything - there is
        # no bed yet when it is read - but it is drawn with this file's pen and
        # lands in the same folder as the step pages, so it is made here with
        # them rather than in a chain of its own.
        import render_maalfigur
        made.append(render_maalfigur.render(G, out_dir, width))
        # ...and the bed's own dimensions, drawn with the same pen from the
        # cover's own camera. Same reason it is made here: it is a projection
        # of this model through this file's View, and it lands in the same
        # folder as the pages it stands in front of.
        import render_maaltegning
        made.append(render_maaltegning.render(G, out_dir, width))
    if proof:
        preview = os.path.join(ROOT, "docs", "preview")
        # The sheets are rastered at the LARGEST page scale so their own type
        # stays readable; every row inside them is then drawn at the size the
        # page it stands for gives it.
        fill_contrast_strip(preview, max(PAGE_FILL_SCALES.values()),
                            min(PAGE_FILL_SCALES.values()))
        form_contrast_strip(preview, max(PAGE_SCALES.values()))
    print(f"\n{len(made)} tegninger i {out_dir}")


if __name__ == "__main__":
    main(sys.argv)
