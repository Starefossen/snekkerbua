"""PLASSERINGSMÅLENE PÅ STEGARKENE - hvor langt fra et kjent punkt.

X15. The step drawings showed what goes where and which screw holds it, and
they showed it without a single number on the page. A builder standing with
the back bench rail in one hand and a drill in the other does not need to be
told again that it is a 48x68 - he needs to know how far down from the post
top it goes. That is the one question this module answers, and it answers it
for every step at once.

THE IDIOM IS SELECTION, NOT FLOOD
---------------------------------
A dimension on every edge is the cutting list with a picture behind it, and
this bed already has a cutting list. So a step gets the FEW measurements that
place the wood it adds, and every one of them is the distance from something
the reader can already see on that same page - a post top, the end of a rail,
the wall - to an edge of the piece going on.

WHAT IS OWED, AS ONE RULE
-------------------------
For every cut-list family a step adds, and for each of the three axes:

  * THE ROOM MAY HAVE PLACED IT ALREADY. A piece whose length is fine-cut to
    the niche is placed along that axis by the SAW, not by a tape, and the
    same goes for a standing piece trimmed in vater at the foot. `ROOM_FIT`
    says which, and nothing is owed on that axis.
  * OTHERWISE THE NEAREST KNOWN FACE IS THE DATUM, AND «KNOWN» IS NOT «ANY
    FACE ON THE PAGE». A distance is a thing a tape is stretched between, so
    the far end of it has to be something the new piece MEETS: a piece it is
    fastened to in this bed's own joint table, another member of its own
    cut-list family already laid (which is what turns a field of slats into
    one distance and one gap rather than fourteen distances), or one of the
    three planes the room itself presents. The nearest of those wins.
  * A FLUSH IS ASKED OF EVERYTHING, because it is a claim about a PLANE and a
    plane can be sighted right across the bed: the front bench rail lands at
    the same height as the back one two feet behind it, and «i flukt» says
    that better than any number measured up a post.
  * ZERO IS A MEASUREMENT TOO, AND IT IS A WORD. A piece that lands edge to
    edge gets «I FLUKT» rather than an arrow with 0 mm on it - and only when
    the face it flushes with belongs to a piece from an EARLIER step, because
    that is the case where lining up is an instruction. Two pieces of the same
    step are cut to each other and the drawing shows it.
  * A PIECE CAUGHT BETWEEN TWO FACES IS NOT MEASURED AT ALL. Both edges flush
    means the piece is cut to fill, and a filled gap has no free play to
    dimension.

TWO THINGS THE RULE REFUSES TO MEASURE FROM
-------------------------------------------
  1. A FOOT. X6 rule 2: the foot of a standing part is still `ROOM_OVER_FLOOR`
     of waste when the frame goes up, so neither an edge measured to it nor a
     datum taken from it exists yet.
  2. THE FLOOR. It is not level - that is WHY the feet are trimmed - so it is
     not a datum in this bed either. Heights above the floor live in
     nokkelmal.md, where a table can say what a tape cannot.
And the consequence of both is one rule with no exception: A HEIGHT ON A STEP
SHEET IS MEASURED DOWNWARDS. The datum face lies at or above the edge it
measures to, every time, and assert_datums() reads that off the finished
records rather than trusting the loop that made them.

AND A LOOSE SUB-ASSEMBLY MEASURES OFF ITSELF. X14 refuses to let a screw cross
out of the panel unit or the footstool; a measurement may not cross either.
A stool that stands where it is put has no distance to the wall worth
printing, so its parts are placed against each other and nothing else.

THE SYMMETRY IS COLLAPSED BY THE NUMBERS THEMSELVES. Left and right give the
same distance because the bed is mirrored, so two members that measure the
same are ONE dimension with two places it could be drawn, and the sheet draws
whichever one it can see. The X6 mirror assert is what guarantees the two
halves agree in the first place.

Entry points:
    owed(G, steps)         -> {step number: [record, ...]}
    assert_datums(G, recs)  the foot rule, on the derived records
    assert_ink(G, steps, read)  the finished SVGs against the owed list
"""

import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Half a millimetre: finer than a tape can read, and the same hair PLACE_TOL
# uses in the model. Two faces nearer than this are one face.
TOL = 0.5

FLUSH_WORD = "I FLUKT"
UNIT = "mm"

# The three axes, named the way X6 names them, and the order they are asked
# in. It is the order the words come out in a report, nothing more.
AXIS_NO = ("langs", "dybde", "høyde")

# WHICH AXIS A ROOM FIT SPEAKS FOR. `room_fit` in the model returns the kind
# of finishing a piece needs; each kind is a statement about ONE axis (or two),
# and on that axis the piece is placed by the saw rather than by a tape.
ROOM_AXES = {"vegg": (0,), "gulv": (2,), "gulv+side": (0, 2), "meddrag": (0,)}


def _fmt(mm):
    """The figure as it is printed, rounded away from zero on a half.

    Python rounds a half to even, so 44,5 would print as «44» and then fail
    its own ink assert by exactly the tolerance. The drawing office rounds up.
    """
    return f"{int(mm + 0.5) if mm >= 0 else -int(-mm + 0.5)}"


def label_of(mm):
    return f"{_fmt(mm)} {UNIT}"


class Face:
    """One flat face a measurement may be taken from.

    Either a face of a piece that is already standing, or one of the three
    planes the ROOM itself presents: the two end walls and the wall plane the
    whole back of this bed lies in (W1).
    """

    def __init__(self, axis, value, name, part=None, step=None, foot=False,
                 family=None):
        self.axis = axis
        self.value = float(value)
        self.name = name
        self.part = part           # None for a room plane
        self.step = step
        self.foot = foot           # still ROOM_OVER_FLOOR of waste
        self.family = family

    def spans(self, part, axis):
        """Do this face's piece and `part` stand in the same place, seen along
        the two axes the measurement does NOT run along?

        A room plane runs the length of the room and answers yes to both. For
        a piece it is a real question: the end beam is 36 mm of wood at one end
        of a two-metre bed, and its underside is no datum for a ladder rung in
        the middle of it however close the two heights happen to be.
        """
        if self.part is None:
            return 2
        n = 0
        for j in range(3):
            if j == axis:
                continue
            a, b = part.extents[j], self.part.extents[j]
            if min(a[1], b[1]) - max(a[0], b[0]) >= -TOL:
                n += 1
        return n


def room_planes(G):
    """The three planes the room itself puts on the drawing."""
    return [Face(0, 0.0, "endeveggen"),
            Face(0, float(G.WALL_SPAN), "endeveggen"),
            Face(1, float(G.WALL_Y), "veggplanet")]


def _foot_faces(G, part):
    """The faces of this piece that are still waste when it is offered up."""
    fit = G.ROOM_FIT.get(part.label)
    if fit is not None and fit["kind"].startswith("gulv"):
        return {(2, part.extents[2][0])}
    return set()


FACE_NO = (("enden", "enden"), ("bakkanten", "forkanten"),
           ("underkanten", "overkanten"))


def part_faces(G, part, step, no_name):
    """Both faces of a piece on each axis, as datum candidates."""
    waste = _foot_faces(G, part)
    out = []
    for axis in range(3):
        for i, v in enumerate(part.extents[axis]):
            out.append(Face(axis, v, f"{no_name} ({FACE_NO[axis][i]})",
                            part, step, foot=(axis, v) in waste,
                            family=no_name))
    return out


# ---------------------------------------------------------------------------
# THE MEASUREMENT ITSELF
# ---------------------------------------------------------------------------
def joint_partners(G):
    """label -> the labels it is FASTENED to, off the placed fasteners.

    The joint table is where this bed says which two pieces meet, and a
    placement measure is taken to the piece being met. Read off the fastener
    solids rather than the prose, so a joint that moves takes its datum with
    it.
    """
    out = {}
    for f in G.FASTENER_SPECS:
        a, b = f.get("pa"), f.get("pb")
        if a is None or b is None:
            continue
        out.setdefault(a.label, set()).add(b.label)
        out.setdefault(b.label, set()).add(a.label)
    return out


def _measure(G, part, axis, pool, reach):
    """(distance, every face it could be taken from, which edge) or None.

    EVERY face, not the first one: the back bench rail is ONE piece and it
    lands the same distance under BOTH post tops, so the measure has two
    places it could be drawn and the sheet picks whichever end it can see.
    Mirror symmetry falls out of this rather than being asked for - if the two
    halves ever stopped agreeing, the two would not tie and only one would be
    offered.

    The nearest legal face wins. A face INSIDE the piece is no datum - it is
    something passing through - a face that is still waste is no datum either,
    and on Z a face BELOW the edge is not a datum at all: heights are measured
    downwards in this bed (X6 rule 2).
    """
    lo, hi = part.extents[axis]
    waste = _foot_faces(G, part)
    found = []
    for f in pool:
        if f.axis != axis or f.foot:
            continue
        if lo + TOL < f.value < hi - TOL:
            continue
        edge = lo if abs(f.value - lo) <= abs(f.value - hi) else hi
        if (axis, edge) in waste:
            continue
        d = abs(f.value - edge)
        if axis == 2 and f.value < edge - TOL:
            continue                 # a height is measured downwards
        # A distance is only a distance between two things that MEET - a joint
        # partner, the next member of the same family, or the room. A FLUSH is
        # a claim about one plane, and a plane is visible right across the
        # drawing, so it is asked of everything that stands beside it.
        if d > TOL and not reach(f):
            continue
        if f.spans(part, axis) < (1 if d <= TOL else 2):
            continue
        # HOW FAR AWAY THE DATUM PIECE ITSELF IS, and it is a tie-break with a
        # reason: half a dozen edges of this bed line up on the same plane, and
        # the one worth sighting along is the piece STANDING NEXT TO the new
        # one - not a bench slat two courses down that happens to share a face.
        near = 0.0 if f.part is None else math.dist(
            [sum(part.extents[j]) / 2.0 for j in range(3)],
            [sum(f.part.extents[j]) / 2.0 for j in range(3)])
        found.append((round(d, 3), round(near, 3), f.name,
                      round(f.value, 3), f, edge))
    if not found:
        return None
    shortest = min(r[0] for r in found)
    # ...and they have to be ties on the SAME EDGE of the piece. A 48 mm rail
    # laid alongside another 48 mm rail at the same height has both its edges
    # in line, and one sight line can only be about one of them. It is the top
    # that gets it: a height is sighted along the surface a spirit level goes
    # on, not along the underside nobody can see.
    sgn = -1.0 if axis == 2 else 1.0
    tied = [r for r in found if r[0] == shortest]
    near = min(r[1] for r in tied)
    tied = sorted([r for r in tied if r[1] == near],
                  key=lambda r: (r[2], sgn * r[3]))
    edge = tied[0][5]
    tied = [r for r in tied if abs(r[5] - edge) < 1e-9]
    return tied[0][0], [r[4] for r in tied], edge


def _mid(a, b):
    return (max(a[0], b[0]) + min(a[1], b[1])) / 2.0


def _nearest(part, other, axis, value):
    """The point on this piece's face nearest the other piece.

    A flush is drawn as a SIGHT LINE between the two edges that are in line,
    and the line has to be short enough to read: from the middle of one piece
    to the middle of the other it crosses everything in between. Nearest point
    to nearest point runs it the short way, through the gap the two actually
    have between them.
    """
    p = []
    for j in range(3):
        lo, hi = part.extents[j]
        c = sum(other.extents[j]) / 2.0
        p.append(min(max(c, lo), hi))
    p[axis] = float(value)
    return tuple(p)


def _touching(a, b):
    """Do the two pieces meet? Then the flush needs no line: the drawing shows
    two edges running into each other, and a word about it is a word about
    what the reader is looking at."""
    return all(min(a.extents[j][1], b.extents[j][1])
               - max(a.extents[j][0], b.extents[j][0]) >= -TOL
               for j in range(3))


def _point(part, face, axis, value):
    """Where on the paper the arrow (or the tick) is drawn: on the axis it
    measures it sits at `value`, and on the other two in the middle of the
    stretch the two pieces have in common - which is where a tape would go."""
    p = [0.0, 0.0, 0.0]
    p[axis] = float(value)
    for j in range(3):
        if j == axis:
            continue
        p[j] = (_mid(part.extents[j], face.part.extents[j])
                if face.part is not None
                else sum(part.extents[j]) / 2.0)
    return tuple(p)


# ---------------------------------------------------------------------------
# WHAT ONE STEP OWES
# ---------------------------------------------------------------------------
def _families(G, labels, uni, fam):
    out = {}
    for lbl in labels:
        if lbl in uni:
            out.setdefault(fam[lbl], []).append(uni[lbl])
    for ps in out.values():
        ps.sort(key=lambda p: p.label)
    return out


def _room_axes(G, parts):
    fit = G.ROOM_FIT.get(parts[0].label)
    return () if fit is None else ROOM_AXES[fit["kind"]]


def _settled(G, parts, pool):
    """How many of a family's three axes are already spoken for - by the room's
    own saw, or by an edge landing flush on something standing.

    It is the order the families of one step go down in: the piece with the
    least left to say is the piece the others measure from.
    """
    room = _room_axes(G, parts)
    p = parts[0]
    n = len(room)
    for axis in range(3):
        if axis in room:
            continue
        for v in p.extents[axis]:
            if any(f.axis == axis and not f.foot and abs(f.value - v) <= TOL
                   and f.spans(p, axis) >= 1 for f in pool):
                n += 1
                break
    return n


def _captive(G, part, axis, pool):
    """Both edges flush AGAINST SOMETHING THAT BOXES THE PIECE IN: it is cut
    to fill and has nowhere else to go.

    Both faces, and both of them square onto real wood - the weaker overlap a
    flush NOTE is allowed (one axis, so a plane can be sighted the length of
    the bed) would let a rail two feet away make a piece look captive when
    nothing at all is holding that end.
    """
    n = 0
    for v in part.extents[axis]:
        if any(f.axis == axis and not f.foot and abs(f.value - v) <= TOL
               and f.spans(part, axis) >= 2 for f in pool):
            n += 1
    return n >= 2


def step_owed(G, st, uni, fam, pool, partners):
    """The records one step owes."""
    labels = [l for l in st["labels"] if l in uni]
    if not labels:
        return []
    loose = {p.label for p in G.LOOSE_PARTS}
    if all(l in loose for l in labels):
        # X14: no screw crosses out of a loose sub-assembly, and no tape does
        # either. A stool that stands where it is put has no distance to the
        # wall worth printing.
        pool = []
    fams = _families(G, labels, uni, fam)
    # WHICH PIECE GOES DOWN FIRST, AND IT IS NOT ALPHABETICAL. A step is a
    # little sub-assembly, and the piece the others are SCREWED TO is the one
    # they are placed off: the two back posts before the three rails between
    # them, the ladder stiles before the rungs, the panel before its battens.
    # That is the joint table read inside one step - in-degree, and no list.
    kin = {}
    for name, parts in fams.items():
        mine = {p.label for p in parts}
        kin[name] = len({other for other, ps in fams.items()
                         if other != name
                         and any(q.label in partners.get(p.label, ())
                                 for p in parts for q in ps)})
    recs, todo = [], dict(fams)
    while todo:
        name = max(sorted(todo),
                   key=lambda k: (kin[k], _settled(G, todo[k], pool)))
        parts = todo.pop(name)
        recs += _family_owed(G, st, name, parts, pool, partners)
        for p in parts:
            pool = pool + part_faces(G, p, st["n"], name)
    return recs


def _family_owed(G, st, name, parts, pool, partners):
    """One cut-list family's placement facts, collapsed to distinct numbers."""
    room = _room_axes(G, parts)
    pool = list(pool)
    found = {}                       # (axis, kind, figure) -> record
    left = list(parts)
    while left:
        # The member nearest something already known goes first, and the next
        # one measures off it. That is what turns a field of slats into one
        # distance from the wall and one gap, instead of fourteen distances.
        scored = []
        for p in left:
            reach = _reach_for(p, name, partners)
            d = [x for x in (_measure(G, p, a, pool, reach)
                             for a in range(3) if a not in room)
                 if x is not None]
            # ...and where two members are equally near - fourteen slats all
            # sitting flush on the same rail - the tie is broken by WHERE THEY
            # ARE and not by what they are called. `Bed Slat_10` sorts between
            # 1 and 2 as a string, and a field laid in that order chains every
            # slat back to the first one across a metre of bed.
            scored.append((min([x[0] for x in d], default=1e9),
                           p.extents, p.label, p))
        scored.sort()
        part = scored[0][3]
        left.remove(part)
        reach = _reach_for(part, name, partners)
        for axis in range(3):
            if axis in room:
                continue
            got = _measure(G, part, axis, pool, reach)
            if got is None:
                continue
            d, faces, edge = got
            face = faces[0]
            if d <= TOL:
                if any(f.part is None for f in faces) \
                        or face.step == st["n"]:
                    continue         # the room, or the same step's own wood
                if _captive(G, part, axis, pool):
                    continue         # cut to fill
                faces = [f for f in faces if not _touching(part, f.part)]
                if not faces:
                    continue         # the two run into each other on the page
                face = faces[0]
                kind, fig = "flukt", FLUSH_WORD
            else:
                kind, fig = "mål", label_of(d)
            key = (axis, kind, fig)
            if kind == "flukt":
                # A flush is not a span, it is a SIGHT LINE: the two edges that
                # are in line, joined by a line lying IN the plane they share.
                # So the two ends sit on the middle of each piece rather than
                # on the middle of what they have in common - the line then
                # runs from the one piece to the other and shows the reader
                # exactly which two edges the word is about.
                pairs = [(_nearest(f.part, part, axis, f.value),
                          _nearest(part, f.part, axis, edge))
                         for f in faces]
            else:
                pairs = [(_point(part, f, axis, f.value),
                          _point(part, f, axis, edge)) for f in faces]
            rec = found.get(key)
            if rec is None:
                found[key] = dict(
                    n=st["n"], family=name, part=part.label, axis=axis,
                    kind=kind, mm=float(d), figure=fig,
                    datum=face.name, datum_step=face.step,
                    alts=list(pairs))
            else:
                rec["alts"] += pairs
        pool += part_faces(G, part, st["n"], name)
    return [found[k] for k in sorted(found)]


def _reach_for(part, name, partners):
    """Which faces this piece may stretch a tape to: the pieces it is fastened
    to, its own family, and the room."""
    kin = partners.get(part.label, set())

    def reach(f):
        return (f.part is None or f.family == name or f.part.label in kin)
    return reach


def owed(G, steps):
    """{step number: [record, ...]} - every placement fact the sheets owe."""
    import gen_doc_tables as T
    uni = {p.label: p for p in G.CUT_PARTS}
    fam = {}
    for lbl, (nm, _sec, _len) in T.part_cut_keys(G).items():
        fam[lbl] = T.NO_NAMES.get(nm, nm)
    partners = joint_partners(G)
    pool = room_planes(G)
    out = {}
    for st in steps:
        out[st["n"]] = step_owed(G, st, uni, fam, pool, partners)
        for lbl in st["labels"]:
            if lbl in uni:
                pool = pool + part_faces(G, uni[lbl], st["n"], fam[lbl])
    return out


# ---------------------------------------------------------------------------
# THE DOM - X6 RULE 2, ON THE DRAWINGS THIS TIME
# ---------------------------------------------------------------------------
def assert_datums(G, all_recs):
    """No placement line on any step sheet measures from a foot or the floor.

    The same rule assert_datum_ink() holds the PLACEMENT TABLE to, asked of the
    drawings: a standing piece is marked from the top, because its other end is
    still `ROOM_OVER_FLOOR` of waste when the tape comes out - and the floor
    the waste is there for is no datum either.
    """
    bad, feet = [], []
    for n, recs in sorted(all_recs.items()):
        for r in recs:
            if r["axis"] != 2:
                continue
            for p0, p1 in r["alts"]:
                if abs(p0[2]) <= TOL or abs(p1[2]) <= TOL:
                    bad.append(f"steg {n}: {r['family']} måler til gulvet")
                if r["kind"] == "mål" and p1[2] > p0[2] + TOL:
                    feet.append(f"steg {n}: {r['family']} måler OPP fra "
                                f"{r['datum']} ({r['figure']})")
    assert not bad, (
        "X6/X15: gulvet er ikke i vater - det er derfor føttene kappes - og "
        "kan ikke være utgangspunkt for et plasseringsmål: " + "; ".join(bad))
    assert not feet, (
        "X6/X15: disse høydemålene på stegarkene måler OPPOVER, altså fra en "
        "ende som ennå er avfall når målet tas: " + "; ".join(feet))
    n_z = sum(1 for recs in all_recs.values() for r in recs if r["axis"] == 2)
    return n_z


# ---------------------------------------------------------------------------
# THE BIJECTION - WHAT THE SHEET DREW AGAINST WHAT THE STEP OWED
# ---------------------------------------------------------------------------
_FIG = re.compile(r">(\d+ mm|" + FLUSH_WORD + r")</text>")


def sheet_figures(raw):
    """The placement figures on one finished sheet, off the ink."""
    return sorted(_FIG.findall(raw))


def wanted_figures(recs):
    return sorted(r["figure"] for r in recs)


def assert_ink(G, steps, sheets):
    """Every step drew exactly the placement facts it owed - no more, no less.

    `sheets` is {step number: the finished SVG as text}. This is the assert
    that catches a SILENCE: a dimension that quietly stopped being drawn looks
    exactly like a step that never owed one, and only the model can tell the
    two apart.
    """
    all_recs = owed(G, steps)
    bad, drawn = [], 0
    for st in steps:
        n = st["n"]
        if n not in sheets:
            continue
        want = wanted_figures(all_recs.get(n, []))
        got = sheet_figures(sheets[n])
        drawn += len(got)
        if got != want:
            bad.append(f"steg {n}: arket har {got or '[]'}, "
                       f"men steget skylder {want or '[]'}")
    assert not bad, (
        "X15 plasseringsmål: stegarkene og modellen er uenige om hvilke mål "
        "stegene skylder:\n  " + "\n  ".join(bad))
    return drawn
