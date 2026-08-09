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
    that meet on a face, computed from the parts' own extents. WHICH WAY the
    arrow at one of them points is NOT read off the geometry: the contact
    normal is a property of the joint, not of the screwdriver, and for a good
    half of the joints in this bed the two disagree. It is DATA. Every row of
    JOINT_CONTACTS names, per fastener kind, the member the screw ENTERS FROM
    (`frm`), or - where the screw does not cross the patch at all, as with the
    bracket screws that go sideways into a stub leg - the member it is driven
    INTO and along which axis (`into` + `axis`). The arrow's tail sits on the
    entry side and its head points into the receiving member, along the screw.
    Each row is the same fact docs/generated/beslagliste.md prints in its
    "Drives fra" column, which is JOINTS[...]["side"] in tools/gen_doc_tables.py.
  * the corner inset carries the step's fasteners at large scale with their
    counts, and one SECTION per joint family in the step: the two members at
    their true cross-section sizes and true relative positions, hatched the way
    a cut piece of timber is hatched, with every fastener of that joint drawn
    at its true length crossing the interface - head on the entry side, tip
    inside the receiving member.
  * a marker is allowed to stand for more than one screw (two screws 30 mm
    apart are one mark on a page this size), and then it carries the count:
    "2x" beside the badge. Nothing is thinned away - a mark that is dropped
    for crowding hands its count to the mark that crowded it, and the page is
    checked at build time to show every fastener the step's table lists.
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

# The marker arrow, as a fraction of the page's longer side. IKEA's arrows are
# long: the eye has to catch the DIRECTION from across the page, and a stub
# reads as a dot. This is about three times what the first version used.
ARROW_FRAC = 0.078
HEAD_FRAC = 0.22       # arrowhead length, as a fraction of the arrow

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
    "rail":        r"Upper Side Rail (?:Back|Front)",
    "rail_back":   r"Upper Side Rail Back",
    "rail_front":  r"Upper Side Rail Front",
    "bench_rail":  r"Bench Rail (?:Back \(continuous\)"
                   r"|Front (?:Left|Right) \(segment\))",
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
    "guard":       r"Guard Rail Front (?:Left|Right)_\d+",
    "guard_host":  r"(?:Corner Post Front|Ladder Upright) (?:Left|Right)",
    "bed_slat":    r"Bed Slat_\d+",
    "bench_slat":  r"Bench Slat (?:Left|Right)_\d+",
    "panel":       r"Movable Panel \(bed mode\)",
    "batten":      r"Panel Stiffener Batten (?:Left|Right) \(bed mode\)",
}


def drive(name, per, frm=None, into=None, axis=None, sign=None, depth=0.0,
          off=None, plate=None, exempt=None):
    """One kind of fastener driven at one contact patch.

    `name`  a prefix of the trade name in JOINTS - enough to find the row in
            the step's own fastener list, which is where the count and the
            badge letter come from.
    `per`   how many of them this ONE patch takes.
    `frm`   the member the screw enters from. The arrow then runs along the
            patch normal, out of that member and into the other one. This is
            the ordinary case and covers every joint where the screw does
            what the joint does.
    `into`  + `axis`: for a fastener that does NOT cross the patch - the
            bracket screws that go sideways into a stub leg, say. The arrow
            runs along `axis` into the named member, entering it on the face
            that looks back towards the middle of the bed, which is the side
            a screwdriver can reach. Give `sign` as well where that rule is
            not the right one (a screw driven UP into a ledger from the
            bracket flange underneath it).
    `depth` mm from the contact patch INTO the member this one grips, along
            the patch normal. Relative on purpose: the same row serves a joint
            and its mirror image at the far end of the bed, and an absolute
            offset would put the mark inside the wrong member on one of them.
    `off`   {axis: mm} - the same thing across the patch, where there is no
            mirror to worry about (Z is Z at both ends of the bed).
    `plate` steel thickness, mm: this "fastener" is a bracket, and the section
            draws it as a plate lying on the face it is screwed to.
    `exempt` a Norwegian reason why the fit rule below does NOT decide this
            one: a toe screw driven at an angle, or a bolt that goes right
            through and takes a nut. Anything without a reason has to obey.
    """
    return dict(name=name, per=per, frm=frm, into=into, axis=axis, sign=sign,
                depth=depth, off=off or {}, plate=plate, exempt=exempt)


# The joints, as the drawing needs them: which two parts meet, across which
# axis, and what is driven there - each with the direction it is driven in.
# Every `frm` / `into` here is the "Drives fra" column of the beslagliste,
# which is JOINTS[...]["side"] in tools/gen_doc_tables.py, restated as
# geometry. If those two ever disagree the drawing is wrong, so this table is
# the one to check against docs/ASSEMBLY.md.
JOINT_CONTACTS = [
    # Endebjelke -> stolpe: "fra bjelkens utside, inn mot stolpen".
    dict(jid="J1", a="post", b="beam", axis=0,
         drives=[drive("Treskrue 6×90", 2, frm="beam")]),
    # Bæreklossen skrus fra sin frie ende inn i stolpen.
    dict(jid="J1-B", a="beam_blk", b="post", axis=0,
         drives=[drive("Treskrue 6×90", 2, frm="beam_blk")]),
    # "Fra stolpens forside, gjennom stolpen inn i vangen."
    dict(jid="J2", a="post_front", b="rail_front", axis=1,
         drives=[drive("Treskrue 6×80", 2, frm="post_front")]),
    # "Rett ned gjennom vangen i stolpetoppen" - vangen ligger PÅ stolpen.
    dict(jid="J2-B", a="post_back", b="rail_back", axis=2,
         drives=[drive("Treskrue 6×120", 2, frm="rail_back")]),
    # "Fra stigevangens forside, inn i vangen."
    dict(jid="J3", a="upright", b="rail_front", axis=1,
         drives=[drive("Treskrue 6×80", 4, frm="upright")]),
    # J4 er to skruer i samme ledd, og de går hver sin vei.
    dict(jid="J4", a="rung", b="rung_blk", axis=2,
         drives=[drive("Treskrue 5×60", 1, frm="rung")]),
    dict(jid="J4", a="rung", b="upright", axis=0,
         drives=[drive("Treskrue 6×120", 1, frm="upright")]),
    # "Fra stigeåpningen, inn i vangens innside" - gjennom klossen.
    dict(jid="J5", a="upright", b="rung_blk", axis=0,
         drives=[drive("Treskrue 5×60", 2, frm="rung_blk")]),
    # Køyespile og benkespile: ovenfra, ned i vangen.
    dict(jid="J6", a="bed_slat", b="rail", axis=2,
         drives=[drive("Treskrue 5×60", 1, frm="bed_slat")]),
    # Rekkverksbordet ligger på innsiden: "fra sengesiden, inn i stolpen".
    dict(jid="J7", a="guard", b="guard_host", axis=1,
         drives=[drive("Treskrue 5×60", 2, frm="guard")]),
    dict(jid="J8", a="bench_front", b="post_front", axis=1,
         drives=[drive("Treskrue 6×80", 2, frm="post_front")]),
    # "Skrått fra vangens forside inn i stolpen."
    dict(jid="J8-B", a="bench_back", b="post_back", axis=0,
         drives=[drive("Treskrue 6×90", 2, frm="bench_back",
                       exempt="skråskrue gjennom vangens forside nær enden")]),
    dict(jid="J9-B", a="bench_blk_b", b="post_back", axis=0,
         drives=[drive("Treskrue 6×90", 2, frm="bench_blk_b")]),
    # "Fra klossens bakside, inn i stolpen" - kortere skrue, 36 mm stolpe bak.
    dict(jid="J9-F", a="bench_blk_f", b="post_front", axis=1,
         drives=[drive("Treskrue 6×70", 2, frm="bench_blk_f")]),
    # Benkevange -> stubbefot. Beslaget ligger flatt mot de to sammenfallende
    # innerflatene og skrus vannrett inn i BEGGE; de to 5x70 er skråskruer
    # nedenfra og opp i vangen. Ingen av beslagskruene krysser opplegget, så
    # de er `into`, ikke `frm`.
    dict(jid="J10", a="bench_front", b="stub", axis=2,
         drives=[drive("Vinkelbeslag 90", 1, into="stub", axis=1, depth=20,
                       plate=2.5),
                 drive("Treskrue 5×40", 2, into="stub", axis=1, depth=62),
                 drive("Treskrue 5×40", 2, into="bench_front", axis=1,
                       depth=36),
                 drive("Treskrue 5×70", 2, frm="stub",
                       exempt="skråskrue nedenfra opp i vangen")]),
    dict(jid="J10", a="stub", b="bench_back", axis=2,
         drives=[drive("Vinkelbeslag 90", 1, into="stub", axis=1, depth=20,
                       plate=2.5),
                 drive("Treskrue 5×40", 2, into="stub", axis=1, depth=62),
                 drive("Treskrue 5×40", 2, into="bench_back", axis=1,
                       depth=36),
                 drive("Treskrue 5×70", 2, frm="stub",
                       exempt="skråskrue nedenfra opp i vangen")]),
    # Benkespile -> benkevange: ovenfra, ned i vangen.
    dict(jid="J11", a="bench_slat", b="bench_rail", axis=2,
         drives=[drive("Treskrue 5×60", 1, frm="bench_slat")]),
    # Bordbærelekta hviler på et beslag på stolpens innerflate: to skruer
    # vannrett inn i stolpen, to opp i lekta.
    dict(jid="J12", a="post_back", b="ledger", axis=0,
         drives=[drive("Vinkelbeslag 40", 1, into="post_back", axis=0,
                       off={2: -34}, plate=2.0),
                 drive("Treskrue 5×40", 2, into="post_back", axis=0,
                       off={2: -18}),
                 drive("Treskrue 5×40", 2, into="ledger", axis=2, sign=1,
                       depth=26)]),
    dict(jid="J13a", a="panel", b="batten", axis=2,
         drives=[drive("Treskrue 5×60", 6, frm="panel")]),
    dict(jid="J13b", a="panel", b="rung", axis=2,
         drives=[drive("U-brakett", 1, frm="panel", plate=4.0),
                 drive("Senkhodeskrue", 2, frm="panel",
                       exempt="gjennomgående bolt i platen, mutter under")]),
    dict(jid="J13c", a="panel", b="bench_back", axis=2,
         drives=[drive("Krokplate", 1, frm="panel", plate=4.0),
                 drive("Senkhodeskrue", 2, frm="panel",
                       exempt="gjennomgående bolt i platen, mutter under")]),
]


def _is_part(kind, label):
    return re.fullmatch(_PART[kind], label) is not None


# ---------------------------------------------------------------------------
# WHICH WAY A SCREW CAN POSSIBLY GO
# ---------------------------------------------------------------------------
# A wood screw through a joint has to do three things at once: pass CLEAR
# through the member it is driven from, END INSIDE the member it grips, and
# not come out the far side of it. In millimetres:
#
#     thickness(entry) < length < thickness(entry) + thickness(receiver)
#
# For most joints in this bed only ONE of the two directions can satisfy that
# - a 6x90 cannot be driven through a 98 mm post into a 48 mm beam, because it
# would not even reach the beam - and then the direction is not a matter of
# opinion at all. It is derived, and the table below is only checked against
# it. Where both directions fit (a 6x80 through 36 mm into 48 mm works either
# way round) the rule cannot help and the direction is what the joint's own
# `side` column in tools/gen_doc_tables.py says: reviewed, human data.
# Where NEITHER fits, the screw is not a straight through-screw at all - a toe
# screw, or a bolt with a nut - and the drive must say so with `exempt`.
def screw_fits(entry, receiver, axis, length):
    t_e = entry.extents[axis][1] - entry.extents[axis][0]
    t_r = receiver.extents[axis][1] - receiver.extents[axis][0]
    return t_e < length < t_e + t_r


def derived_entry(contact, row, pa, pb, dr):
    """(entry member or None, status) - the physics, before the table.

    status: 'utledet'      only one direction is possible; use it.
            'tvetydig'     both are; the table decides.
            'unntak'       neither, and the drive says why.
            'umulig'       neither, and the drive does NOT say why - a bug.
            'gjelder ikke' not a through-screw (a bracket, or driven along an
                           axis of its own).
    """
    if dr["plate"] or dr["into"] is not None or dr["frm"] is None:
        return None, "gjelder ikke"
    if dr["exempt"]:
        return None, "unntak"
    axis = contact[1]
    _d, length = fastener_size(dr["name"])
    ok = [p for p, q in ((pa, pb), (pb, pa))
          if screw_fits(p, q, axis, length)]
    if len(ok) == 1:
        return ok[0], "utledet"
    return None, ("tvetydig" if ok else "umulig")


def contact_row(contact):
    """(row, part matching row['a'], part matching row['b']) or three Nones."""
    a, b, axis = contact[4], contact[5], contact[1]
    for row in JOINT_CONTACTS:
        if row["axis"] != axis:
            continue
        if _is_part(row["a"], a.label) and _is_part(row["b"], b.label):
            return row, a, b
        if _is_part(row["a"], b.label) and _is_part(row["b"], a.label):
            return row, b, a
    return None, None, None


def _letter_of(prefix, letters):
    for name, letter in letters.items():
        if name.startswith(prefix):
            return letter
    return None


def _full_name(prefix, names):
    for name in names:
        if name.startswith(prefix):
            return name
    return None


def drive_axis_sign(contact, row, pa, pb, dr, centre):
    """Which way this fastener travels, in the model's own axes.

    -> (axis, sign, receiving part). `frm` reads the direction off the patch;
    `into` puts it along its own axis, entering the named member from the face
    that looks back into the room side of the bed.
    """
    if dr["into"] is not None:
        axis = dr["axis"]
        member = pa if row["a"] == dr["into"] else pb
        if dr["sign"] is not None:
            return axis, float(dr["sign"]), member
        mid = sum(member.extents[axis]) / 2
        return axis, (1.0 if mid > centre[axis] else -1.0), member
    axis = contact[1]
    entry = pa if row["a"] == dr["frm"] else pb
    # THE HARD CHECK. The fit rule is the primary source; the table is only
    # allowed to agree with it, or to decide where it genuinely cannot.
    guess, status = derived_entry(contact, row, pa, pb, dr)
    assert status != "umulig", (
        f"{row['jid']}: {dr['name']} passer ikke gjennom "
        f"{pa.label} eller {pb.label} langs akse {axis} — verken den ene "
        f"eller den andre veien. Er det en skråskrue eller en gjennomgående "
        f"bolt, må drive(...) si det med exempt=...")
    if status == "utledet":
        assert guess is entry, (
            f"{row['jid']}: tabellen skrur {dr['name']} fra "
            f"{entry.label}, men den eneste retningen skruen faktisk kan gå "
            f"er fra {guess.label}. Rett `frm` i JOINT_CONTACTS.")
        entry = guess
    sign = contact[2] if entry is contact[4] else -contact[2]
    return axis, sign, (pb if entry is pa else pa)


def into_patch_side(contact, member):
    """+1 or -1: the way from the contact patch into `member`."""
    k = contact[1]
    mid = sum(member.extents[k]) / 2
    return 1.0 if mid > contact[0][k] else -1.0


def marks_for(contact, letters, names, centre, view):
    """Every fastener driven at one patch, as marker records."""
    row, pa, pb = contact_row(contact)
    if row is None:
        return []
    out = []
    for dr in row["drives"]:
        axis, sign, target = drive_axis_sign(contact, row, pa, pb, dr, centre)
        p3 = list(contact[0])
        p3[contact[1]] += dr["depth"] * into_patch_side(contact, target)
        for k, v in dr["off"].items():
            p3[k] += v
        if axis != contact[1]:
            # The head belongs on the face the screw actually goes through,
            # not on the bearing surface the patch happens to be.
            p3[axis] = (target.extents[axis][0] if sign > 0
                        else target.extents[axis][1])
        # ...and then a little PAST it, into the member the screw grips. An
        # arrow that stops dead on the joint line reads as pointing AT the
        # seam - and where the screw runs along a rail, as at J8-B, the shaft
        # lies on the rail's own edges and only the head says anything at all.
        # Landing the head inside the receiving member is what makes "into the
        # post" unmistakable at page size.
        t_target = target.extents[axis][1] - target.extents[axis][0]
        p3[axis] += sign * min(0.30 * t_target, 26.0)
        full = _full_name(dr["name"], names)
        if full is None:
            continue
        out.append(dict(p3=tuple(p3), p2=view.xy(tuple(p3)), axis=axis,
                        sign=sign, per=dr["per"], jid=row["jid"], name=full,
                        letter=_letter_of(dr["name"], letters),
                        area=contact[3], contact=contact, row=row, drive=dr))
    return out


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
    happens to stack. A mark that is crowded out therefore does not disappear:
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
                and not _apart(q["p2"], m["p2"], gap)]
        if same:
            same[0]["per"] += m["per"]
            same[0]["absorbed"].append(m)
            continue
        kept.append(dict(m, absorbed=[]))
    for m in deferred:
        same = [q for q in kept if q["name"] == m["name"]]
        if same:
            same.sort(key=lambda q: (q["p2"][0] - m["p2"][0]) ** 2
                      + (q["p2"][1] - m["p2"][1]) ** 2)
            same[0]["per"] += m["per"]
            same[0]["absorbed"].append(m)
        else:
            kept.append(dict(m, absorbed=[]))
    return kept


def mark_families(mark, families):
    return {families.get(p.label)
            for p in (mark["contact"][4], mark["contact"][5])} - {None}


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
_SIZE_RE = re.compile(r"(\d+)\s*[x×]\s*(\d+)")


def fastener_size(name):
    """(diameter, length) in mm, read off the trade name."""
    m = _SIZE_RE.search(name)
    if not m:
        return (5.0, 50.0)
    return (float(m.group(1)), float(m.group(2)))


def bracket_size(name):
    """How far a bracket reaches along the members it ties, mm."""
    m = _SIZE_RE.search(name)
    return float(m.group(1)) if m else 40.0


def _long_axis(part):
    sizes = [part.extents[j][1] - part.extents[j][0] for j in range(3)]
    return sizes.index(max(sizes))


def joint_section(page, box, contact, row, letters, names, centre,
                  letter_label=""):
    """ONE joint, cut through and drawn honestly.

    Both members keep their real cross-section: an axis is only trimmed where
    it is the member's own LENGTH, because a 1794 mm rail drawn whole beside a
    36 mm post would leave the joint a line. The cut faces are hatched the way
    a sawn piece of timber is hatched, and every fastener the joint takes is
    drawn at its true length, entering on the side it is driven from with its
    point buried in the member it grips. A bracket is the black plate lying on
    the face it is screwed to.
    """
    x, y, w, h = box
    cp, k, _sign, _area, pa0, pb0 = contact
    pa = pa0 if _is_part(row["a"], pa0.label) else pb0
    pb = pb0 if pa is pa0 else pa0

    # The second axis of the cut. A fastener that travels across the patch
    # decides it. Failing that, cut along Z whenever one of the two members
    # RUNS THROUGH the joint vertically - a post, a ladder stile - because
    # then the section is an elevation and the reader can see at a glance
    # which member is the continuous one: it carries on above and below while
    # the other stops. Only where neither is a standing member does the cut
    # fall back to the narrower axis, which keeps the detail compact.
    across = [j for j in range(3) if j != k]
    want = [dr["axis"] for dr in row["drives"]
            if dr["axis"] is not None and dr["axis"] in across]
    if want:
        u = max(set(want), key=want.count)
    elif 2 in across and 2 in (_long_axis(pa), _long_axis(pb)):
        u = 2
    else:
        u = min(across,
                key=lambda j: min(pa.extents[j][1] - pa.extents[j][0],
                                  pb.extents[j][1] - pb.extents[j][0]))

    # Where every fastener starts and ends, along its own axis.
    screws = []
    for dr in row["drives"]:
        axis, sign, target = drive_axis_sign(contact, row, pa, pb, dr, centre)
        if axis not in (k, u):
            continue
        d_, length_ = fastener_size(dr["name"])
        if dr["into"] is not None:
            head = (target.extents[axis][0] if sign > 0
                    else target.extents[axis][1])
        else:
            # How deep into the member it is driven from the head sits. A
            # screw driven through a member takes the member's whole
            # thickness (a 6x120 down through a 98 mm rail starts on the
            # rail's top face); a screw driven near the END of a long member
            # - the toe screw at J8-B - starts a bit back from the joint.
            entry = pa if row["a"] == dr["frm"] else pb
            thick = entry.extents[axis][1] - entry.extents[axis][0]
            back = thick if thick < 0.85 * length_ else 0.55 * length_
            head = cp[axis] - sign * back
        # Where along the OTHER section axis this fastener sits. Across the
        # patch that is a plain offset; along the patch normal it is a depth
        # into the member being gripped, so the mirrored joint at the far end
        # of the bed comes out right too.
        other = k if axis == u else u
        at = cp[other] + (dr["depth"] * into_patch_side(contact, target)
                          if other == k else dr["off"].get(other, 0.0))
        if dr["plate"]:
            screws.append(dict(kind="plate", axis=axis, sign=sign, head=head,
                               at=at, t=dr["plate"],
                               reach=bracket_size(dr["name"]), other=other))
            continue
        screws.append(dict(kind="screw", axis=axis, sign=sign, head=head,
                           at=at, d=d_, length=length_, other=other))

    # The window: whole cross-sections, trimmed lengths, and room for the
    # fasteners that stick out of them.
    win = {}
    for j in (k, u):
        lo, hi = None, None
        for part in (pa, pb):
            if _long_axis(part) == j:
                continue
            a0, a1 = part.extents[j]
            lo = a0 if lo is None else min(lo, a0)
            hi = a1 if hi is None else max(hi, a1)
        for s in screws:
            if s["axis"] != j:
                continue
            tip = s["head"] + s["sign"] * (s["t"] if s["kind"] == "plate"
                                           else s["length"])
            back = s["head"] - s["sign"] * (0 if s["kind"] == "plate" else 8)
            lo = min(lo, tip, back) if lo is not None else min(tip, back)
            hi = max(hi, tip, back) if hi is not None else max(tip, back)
        if lo is None:                     # both members run along this axis
            lo, hi = cp[j] - 60, cp[j] + 60
        # Where a member is being cut short because this is its LENGTH, the
        # window is opened wider, so the continuous member visibly carries on
        # past the one that stops.
        runs_through = any(_long_axis(part) == j for part in (pa, pb))
        pad = (max((hi - lo) * 0.34, 30.0) if runs_through
               else max((hi - lo) * 0.16, 14.0))
        win[j] = (lo - pad, hi + pad)

    def rect_of(part):
        out = {}
        for j in (k, u):
            a0, a1 = part.extents[j]
            out[j] = (max(a0, win[j][0]), min(a1, win[j][1]))
        return out

    # Z always goes up the page; the joint axis takes the other direction.
    v_ax = k if k == 2 else u
    h_ax = u if k == 2 else k
    span_x = win[h_ax][1] - win[h_ax][0]
    span_y = win[v_ax][1] - win[v_ax][0]
    scale = min(w * 0.92 / max(span_x, 1e-6), h * 0.80 / max(span_y, 1e-6))
    cx = x + w / 2
    cy = y + h * 0.44

    def px(v):
        return cx + (v - (win[h_ax][0] + win[h_ax][1]) / 2) * scale

    def py(v):
        return cy + (v - (win[v_ax][0] + win[v_ax][1]) / 2) * scale

    for part in (pa, pb):
        r = rect_of(part)
        if r[k][1] <= r[k][0] or r[u][1] <= r[u][0]:
            continue
        x0, y0 = px(r[h_ax][0]), py(r[v_ax][0])
        pw = (r[h_ax][1] - r[h_ax][0]) * scale
        ph = (r[v_ax][1] - r[v_ax][0]) * scale
        page.rect(x0, y0, pw, ph, fill="#ffffff", width=W_RULE)
        page.hatch(x0, y0, pw, ph, max(min(pw, ph) / 4.2, 9.0))

    for s in screws:
        along = (1.0, 0.0) if s["axis"] == h_ax else (0.0, 1.0)
        side = (0.0, 1.0) if s["axis"] == h_ax else (1.0, 0.0)
        o = (px(s["head"]), py(s["at"])) if s["axis"] == h_ax else \
            (px(s["at"]), py(s["head"]))
        sgn = s["sign"]

        def P(t, q, o=o, along=along, side=side, sgn=sgn):
            return (o[0] + along[0] * sgn * t + side[0] * q,
                    o[1] + along[1] * sgn * t + side[1] * q)

        if s["kind"] == "plate":
            t = s["t"] * scale
            reach = min(s["reach"] * scale, max(w, h) * 0.42)
            page.poly([P(0, -reach), P(0, reach), P(-t, reach), P(-t, -reach)],
                      fill=INK, stroke=INK, width=W_RULE * 0.6)
            continue
        L = s["length"] * scale
        d = max(s["d"] * scale, 5.0)
        head_d, head_l, tip_l = d * 1.9, d * 0.55, d * 1.7
        prof = [(0, head_d / 2), (head_l, d / 2), (L - tip_l, d / 2),
                (L, 0), (L - tip_l, -d / 2), (head_l, -d / 2),
                (0, -head_d / 2)]
        page.poly([P(t, q) for t, q in prof], fill="#ffffff", stroke=INK,
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


def draw_inset(page, box, sections, step_fasteners, glyph_dir, letters, names,
               centre):
    """The corner panel: one section per joint in the step, then the
    fasteners at large scale with their counts."""
    x, y, w, h = box
    rows = step_fasteners[:4]
    _w, _h, cols, cell_w, cell_h, row_h = inset_layout(page, len(sections),
                                                       len(rows))
    page.rect(x, y, w, h, fill="#ffffff", stroke=INK, width=W_RULE)

    top = y + h - INSET_PAD
    for i, (contact, row, label) in enumerate(sections):
        cx = x + INSET_PAD + (i % cols) * cell_w
        cy = top - (i // cols + 1) * cell_h
        joint_section(page, (cx, cy, cell_w, cell_h), contact, row, letters,
                      names, centre, label)
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
    c = mark["contact"]
    post = c[4] if _is_part("post_back", c[4].label) else c[5]
    ledger = c[5] if post is c[4] else c[4]
    # The mark's own arrow overshoots into the post, so the sign is the way
    # the screw travels; the bracket lies the other way, out under the ledger.
    e = 1.0 if ledger.extents[0][0] > post.extents[0][0] else -1.0
    xf = post.extents[0][1] if e > 0 else post.extents[0][0]
    zf = ledger.extents[2][0]
    y0, y1 = post.extents[1]
    ym = (y0 + y1) / 2
    leg = 40.0

    # Centred on the CORNER itself - post face meets ledger underside - so the
    # circle holds a piece of both members and not just the steel.
    src = view.xy((xf, ym, zf))
    src_r = max(page.w, page.h) * 0.072
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
    reach = leg * 4.2
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

    standing = [(xf, y0, zf), (xf, y1, zf), (xf, y1, zf + leg),
                (xf, y0, zf + leg)]
    lying = [(xf, y0, zf), (xf, y1, zf), (xf + e * leg, y1, zf),
             (xf + e * leg, y0, zf)]
    for quad in (lying, standing):
        page.poly([P(q) for q in quad], fill="#9a9a9a", stroke=INK,
                  width=W_RULE * 0.9)
    r = 3.2 * k
    for z in (zf + leg * 0.34, zf + leg * 0.72):
        page.dot(P((xf, ym, z)), r)
    for x in (xf + e * leg * 0.34, xf + e * leg * 0.72):
        page.dot(P((x, ym, zf)), r)
    # ...and which way they are driven: into the post, and up into the ledger.
    a_len = dst_r * 0.42
    for tip, dxy in ((P((xf, ym, zf + leg * 0.53)),
                      view.dir_xy((-e, 0, 0))),
                     (P((xf + e * leg * 0.53, ym, zf)),
                      view.dir_xy((0, 0, 1)))):
        n = math.hypot(*dxy) or 1.0
        u = (dxy[0] / n, dxy[1] / n)
        page.arrow((tip[0] - u[0] * a_len, tip[1] - u[1] * a_len), tip,
                   INK, W_MARK * 0.8, a_len * 0.30)
    page.clip_end()
    # The caption goes wherever there is paper: under the circle, over it, or
    # - if the circle sits in a corner - just inside its lower edge.
    if dst_c[1] - dst_r - 66 >= page.y0 + 12:
        ty = dst_c[1] - dst_r - 62
    elif dst_c[1] + dst_r + 62 <= page.y1 - 12:
        ty = dst_c[1] + dst_r + 24
    else:
        ty = dst_c[1] - dst_r + 34
    page.text((dst_c[0], ty), "VINKELBESLAG 40×40×40", 44,
              anchor="middle", weight="bold")


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


def step_sections(marks):
    """One section per joint family in the step, biggest joint first.

    A step with three families - the ladder has three - gets three little
    sections, each labelled with the badge letters of what is driven in it.
    """
    best = {}
    for m in marks:
        c = m["contact"]
        if c[4] is c[5] or m["row"] is None:   # a wall fixing: nothing to cut
            continue
        # One section per KIND of joint, not per instance: the two ends of a
        # bench rail are the same joint mirrored and want one drawing, but
        # J4's two rows - a 5x60 down into the block and a 6x120 sideways
        # into the rung end - are two different things and want two.
        row = m["row"]
        key = (m["jid"], tuple((d["name"], d["axis"], d["frm"] is not None)
                               for d in row["drives"]))
        cur = best.get(key)
        if cur is None or m["area"] > cur[0]:
            best[key] = (m["area"], c, row)
    out = []
    for _key, (area, c, row) in sorted(best.items(), key=lambda kv: -kv[1][0]):
        letters = []
        for d in row["drives"]:
            ch = next((m["letter"] for m in marks
                       if m["row"] is row and m["drive"] is d), None)
            if ch and ch not in letters:
                letters.append(ch)
        out.append((c, row, "".join(sorted(letters))))
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
        for part in (m["contact"][4], m["contact"][5]):
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

    if is_mattress:
        marks = []
    elif "J14" in st["joints"]:
        # The wall fixings do not join two parts of the bed, so there is no
        # contact patch to find: they go through the back rail into the wall
        # behind it. Spread them along that rail's own back face, pointing the
        # way they are driven - one marker per wall fixing, not per joint,
        # because what matters to the builder is how many go into the wall.
        wall = names[0] if names else ""
        marks = [dict(p3=c[0], p2=view.xy(c[0]), axis=1, sign=-1.0, per=1,
                      jid="J14", name=wall, letter=letters.get(wall),
                      area=c[3], contact=c, row=None, drive=None)
                 for c in wall_fix_contacts(
                     new, max((q for _n, q, _s, _l in fasteners), default=2))]
    else:
        marks = [m for c in contacts(new, prior)
                 for m in marks_for(c, letters, names, centre, view)]

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
        draw_inset(page, box, sections, fasteners, glyph_dir, letters, names,
                   centre)
    if not is_mattress:
        check_coverage(st, keep, fasteners, families)

    # A marker at every fastening point: an arrow along the DRIVING direction
    # the joint table gives, head in the member the screw grips.
    arrow_len = min(page.w, page.h) * ARROW_FRAC * 1.15
    for m in sorted(keep, key=lambda q: (-q["p2"][1], q["p2"][0])):
        p2 = m["p2"]
        axis = [0.0, 0.0, 0.0]
        axis[m["axis"]] = m["sign"]
        dx, dy = view.dir_xy(axis)
        nrm = math.hypot(dx, dy)
        if nrm < 1e-6:
            # Straight at the reader: a ringed dot, the drawing convention
            # for an axis that has no length on the page.
            page.circle(p2, 15, width=W_MARK)
            page.dot(p2, 5)
            mark_label(page, (p2[0], p2[1] + 24), (0.0, -1.0), m["letter"],
                       m["per"], box)
            continue
        # Foreshortened, like everything else in the projection: a screw
        # driven half into the page gets a shorter arrow than one driven
        # across it, so the length itself says which way the joint faces.
        length = arrow_len * (0.62 + 0.38 * min(nrm, 1.0))
        dx, dy = dx / nrm, dy / nrm
        tail = (p2[0] - dx * length, p2[1] - dy * length)
        page.arrow(tail, p2, INK, W_MARK, length * HEAD_FRAC)
        mark_label(page, tail, (dx, dy), m["letter"], m["per"], box)

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
