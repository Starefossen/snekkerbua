#!/usr/bin/env python3
"""BAKVEGGEN, drawn: docs/schematics/spikerslag.svg.

The wall the bed hangs on, seen as an elevation - X along the niche, Z up from
the finished floor - with the zones that have to have noggings in them marked
out. It is the one sheet in the folder that is not a drawing of the bed at
all: it is a drawing of the WALL, and it is drawn because the wall is closed
before the bed is built. What is not in the wall when the plasterboard goes up
is not going in later.

WHERE THE ZONES COME FROM
-------------------------
generate_loftbed.py's WALL_ZONES, and nothing else. A zone is a (height band,
cut-list line) the model worked out from the geometry: a part lying on the
wall face whose length runs along the wall presses on it over that whole
length, and a part on the wall face that is also flush with an end wall stands
in the corner. This sheet draws one hatched field per PART in those zones -
its own X extent, its own Z band - so the two corner columns come out 98 mm
wide because that is how wide the back posts are, and the long bands stop at
the post faces because that is where the members stop.

Every height on the sheet is measured from the FINISHED FLOOR, Z = 0 - and,
after X8b, ALSO from the height line, in brackets beside it. The line is
MEASURE_DATUM_Z, struck round the niche with a laser 1000 mm over the floor;
it is drawn here too, thin, and the model asserts that it falls on bare wall
between two zones - a line struck across a nogging is a line you cannot see
once the bed is up. The second notation exists because the floor is out of
level and the line is not: at the open wall you set a zone by pulling the tape
from the laser, not by finding the floor. Minus is below the line, plus above.

WHICH WAY ROUND X RUNS
----------------------
The same way the cut list says it does: X = 0 is the left end wall,
X = WALL_SPAN the right one. That is the convention every other document in
this folder measures in, and a sheet that flipped it to suit one eye position
would make every X in the cut list read backwards against it.

THE ASSERTS
-----------
The sheet is written, then READ BACK: every hatched field in the finished SVG
is converted from sheet units to model millimetres and has to be the X extent
and Z band of a part in WALL_ZONES. A zone the model grew and the drawing did
not is a failed build, not a drawing to be noticed later. The second height
notation is read back the same way: every height written in both is subtracted
on the finished sheet and has to differ by exactly MEASURE_DATUM_Z.

And so is the TYPE. Every <text> on the finished sheet is measured, and no two
of them may touch, and none of them may hang off the paper. That assert is the
reason the labels on the wall face are not written at typed coordinates any
more but PLACED, by tools/layout.py's occupancy field: a label whose position
is a number somebody nudged is a collision again the next time the model moves
a zone, and this sheet's zones move whenever the bed does.

Usage:
    python tools/render_spikerslag.py [--out docs/schematics/spikerslag.svg]

Deterministic: no clock, no id(), no set iteration into the output.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "tools"))

from layout import Occupancy, place                   # noqa: E402
from schematic import Sheet, nb                       # noqa: E402

OUT = os.path.join(ROOT, "docs", "schematics", "spikerslag.svg")

# ---------------------------------------------------------------------------
# THE SHEET
# ---------------------------------------------------------------------------
# 3450 units wide, like every other sheet in the folder, so the type, strokes,
# arrows and hatch are the family's own numbers unscaled (STYLE_K = 1).
FAMILY_W = 3450.0
STYLE_K = 1.0
SHEET_W = FAMILY_W
ORIGIN = (0.0, 150.0)

# THE HEIGHT IS NOT TYPED HERE ANY MORE. It used to be, and every time the
# sheet gained a line the number was raised by hand ("X8b: +140 for the second
# height notation"), which is the same fault as a hand-nudged label one axis
# over. `build()` writes the sheet top-down and stops the paper FOOT_GAP under
# the last word - so the sheet is as tall as its content and no taller.
#
# One thing does watch over it: tools/build_pdf.py prints a schematic
# landscape when its aspect is over LAND_LIMIT and portrait when it is not,
# and this sheet - 1990 mm of wall with a ladder of heights beside it - is a
# landscape drawing whatever the prose under it does. So the finished height
# is asserted against that ratio rather than trusted.
LAND_LIMIT = 1.1

MARG = 120.0
VIEW_X0 = 470.0             # where X = 0 (the left end wall) lands
K = 1.0                     # sheet units per model millimetre

# Where Z = 0 (the finished floor) lands - DERIVED, once, by set_view(), which
# is the first thing build() does after writing the title. It was a typed
# 1780 for a long time, and a typed one cannot know that the title block above
# it is 315 units deep: at 1780 this sheet drew 1650 mm of wall face straight
# over its own heading. See set_view().
VIEW_Z0 = 0.0

TTL_Y = 250.0               # the title block's two baselines
SUB_Y = 310.0
TITLE_CLEAR = 50.0          # white under the title block before ANY drawing
WALL_TICK = 40.0            # the end-wall hatch ticks rise this far over it

AIR_OVER = 150.0            # wall drawn this far above the topmost zone
LAD_X = 2560.0              # the height ladder's tick column
LAB_X = 2610.0              # ... and its text column
CHAIN_X = VIEW_X0 - 110.0   # the vertical dimension chain, left of the wall

NOTE_X = (MARG, 1800.0)     # the prose panel
NOTE_W = 1520.0
NOTE_GAP = 90.0             # white between the last dimension row and prose
FOOT_GAP = 100.0            # ... and between the last word and the footer

# What a label wants round itself, and how far it slides when it has to give
# way. LAB_STEP is one step, not one nudge: the placer tries the step, and
# then another, and the first free one wins - so the number decides the GRAIN
# of the search, never the answer.
TEXT_PAD = 8.0
LAB_STEP = 240.0

# What is in a label's way, and how much it minds. A label may sit on hatch if
# it must - the hatch is 45 deg grey and type reads over it - it may not sit on
# a screw, and it may never sit on another label.
W_ZONE, W_MARK, W_TEXT = 1.0, 3.0, 6.0
IN_THE_WAY = ("zone", "mark", "text")

# `.zonekey` is the same ink as `.zone` under another name, and the reason is
# the assert at the bottom of this file: it reads every `zone` rectangle back
# off the finished sheet and demands it be a part in WALL_ZONES. The swatch in
# the legend is a picture OF a zone, not a zone, so it must not answer that
# question - it would answer it wrong.
EXTRA_CSS = """    .zone, .zonekey { fill:url(#hatch); stroke:#000;
           stroke-width:2.6; }
    .wallf{ fill:none; stroke:#000; stroke-width:5; }
    .flr  { fill:none; stroke:#000; stroke-width:5; }
    .face { fill:none; stroke:#000; stroke-width:1.7; }
    .scrp { fill:#000; stroke:none; }
    .scro { fill:#fff; stroke:#000; stroke-width:2.2; }
"""


def ex(x):
    """Model X (along the wall, 0 = left end wall) to sheet x."""
    return VIEW_X0 + K * x


def zed(z):
    """Model Z (height over the finished floor) to sheet y."""
    return VIEW_Z0 - K * z


def un_ex(sx):
    return (sx - VIEW_X0) / K


def un_zed(sy):
    return (VIEW_Z0 - sy) / K


# ---------------------------------------------------------------------------
# HOW MUCH PAPER A WORD COVERS
# ---------------------------------------------------------------------------
# A sheet that places its own labels has to know what one COVERS, and it has
# no font to ask. So it estimates, and the estimate is written down here so
# that it can be argued with.
#
# Helvetica's advance widths - Arial's are the same to within a hair, and the
# sheet asks for both - fall into groups, not onto a line: 0.222 em for i, l
# and j, 0.278 for the space and the full stop, 0.556 for the digits and most
# lowercase, 0.667-0.778 for the capitals, 0.944 for W and 1.0 for the em
# dash. So the estimate is five CLASSES, each set a little over the true
# average of its members. It was checked the only way an estimate of ink can
# be: by drawing each of this sheet's real labels with a bar of its estimated
# width under it and looking. At the numbers below every bar overhangs its
# label by two or three per cent - fat enough that a pair the estimate calls
# clear really is clear, tight enough that a label is not sent wandering for
# a collision it never had.
#
# Which way the error has to point is the whole design: over-estimating moves
# a label that could have stayed, and the sheet is a little airier than it had
# to be. Under-estimating PRINTS the collision. The assert at the bottom of
# the file measures with the same numbers the placer places with.
NARROW = " .,;:!|'\"`()[]/\\-·iljtfrI"        # 0.222 - 0.333 in the metrics
MID = "0123456789+×–"                         # 0.556 - 0.584: digits, en dash
WIDE = "ABCDEFGHJKLMNOPQRSTUVXYZÆØÅmw"        # 0.667 - 0.944
EM_NARROW, EM_MID, EM_WIDE, EM_OTHER, EM_DASH = 0.31, 0.57, 0.72, 0.545, 1.02
BOLD_K = 1.05               # Helvetica-Bold over Helvetica, averaged

# A line of type covers this much over and under its baseline. Ø and Å reach
# higher than a cap, and the sheet is full of both.
ASC, DESC = 0.78, 0.20

# class -> (the family size it is set in, bold?). The haloed variants are the
# same type as their plain twins - the halo is ink round it, not a size.
CLS = {"ttl": ("ttl", True), "sub": ("sub", False), "pt": ("pt", True),
       "big": ("big", True), "sml": ("sml", False), "smh": ("sml", False),
       "tiny": ("tiny", False), "tinyh": ("tiny", False),
       "dm": ("dm", False), "dmh": ("dm", False), "leg": ("leg", True),
       "jl": ("jl", True)}


def text_w(s, sz, bold=False):
    """The estimated width of `s` set at `sz`, in sheet units."""
    em = 0.0
    for ch in s:
        if ch == "—":
            em += EM_DASH
        elif ch in NARROW:
            em += EM_NARROW
        elif ch in MID:
            em += EM_MID
        elif ch in WIDE:
            em += EM_WIDE
        else:
            em += EM_OTHER
    return em * sz * (BOLD_K if bold else 1.0)


def tbox(sh, p, s, cls, anchor="start"):
    """The rectangle a label written at `p` covers: (x, y, w, h)."""
    key, bold = CLS[cls]
    sz = sh.sz[key]
    w = text_w(s, sz, bold)
    x = p[0]
    if anchor == "middle":
        x -= w / 2.0
    elif anchor == "end":
        x -= w
    return (x, p[1] - ASC * sz, w, (ASC + DESC) * sz)


def put(sh, occ, p, s, cls, anchor="start"):
    """Write a label AND remember what it covers, so the next can see it."""
    sh.text(p, s, cls, anchor)
    box = tbox(sh, p, s, cls, anchor)
    occ.add_box(box, weight=W_TEXT, tag="text")
    return box


def put_free(sh, occ, cands, s, cls, anchor="start", bounds=None):
    """Write a label at the first free one of an ORDERED list of candidates.

    The list is the rule - "over the band, then a step to the side, then
    under it" - and tools/layout.py's placer only decides how far down the
    list to go: it charges each candidate for what is already there, and
    `min` breaks a tie on the earliest, so a run of empty candidates always
    ends at the first of them and the same model always comes out the same
    sheet.

    There is deliberately NO tether pulling the label towards the thing it
    names. One was tried, and what it did was override the order it was meant
    to break ties in - a wall fixing's label went UNDER its row rather than
    over it, because its own screws are nearer the underside of the band than
    the top of a line of type is to the upper side. Which side a label
    belongs on is a drawing rule, not a distance.
    """
    boxes = [tbox(sh, p, s, cls, anchor) for p in cands]
    cent = [(b[0] + b[2] / 2.0, b[1] + b[3] / 2.0) for b in boxes]
    # The footprint carries TEXT_PAD of white on every side - what is asked
    # of the field is not "does this fit" but "does this fit with air round
    # it". Two labels a hair apart pass the assert and still read as one.
    won = place(cent, (boxes[0][2] + 2 * TEXT_PAD, boxes[0][3] + 2 * TEXT_PAD),
                occ, bounds=bounds, edge=TEXT_PAD, tags=IN_THE_WAY,
                grow=TEXT_PAD)
    i = next(j for j, c in enumerate(cent) if c is won)
    put(sh, occ, cands[i], s, cls, anchor)
    return cands[i], boxes[i]


def wall_bounds(M):
    """The wall face. No label this sheet places may leave it: a name that has
    slid off the drawing is not a name of anything on it."""
    return (ex(0.0), zed(M.z_top), ex(M.G.WALL_SPAN), zed(0.0))


def band_rows(sh, z0, z1, n=3, cls="sml"):
    """Text baselines just over a band and just under it, n of each.

    A label belonging to a band reads best sitting on top of it, and the rule
    the whole sheet follows is: over first, and then further over, and only
    then under. Nothing is ever written INSIDE a band - zones 3 and 4 have the
    wall fixings in them, and a name across a screw is a name in the way.
    """
    lead = sh.sz[cls] * 1.42
    up = [zed(z1) - sh.sz[cls] * 0.55 - i * lead for i in range(n)]
    dn = [zed(z0) + sh.sz[cls] * 1.15 + i * lead for i in range(n)]
    return up + dn


def set_view(sh, M):
    """Where Z = 0 lands - derived from the top of the sheet downwards.

    The title block is the first ink on the paper. Under it there is
    TITLE_CLEAR of white, and only then may the drawing start. The drawing's
    topmost ink is not the wall face itself but the end-wall hatch ticks,
    which rise WALL_TICK over it; the face in turn is already AIR_OVER of bare
    wall over the highest zone (that is in M.z_top). Nothing is reserved up
    here for labels: every label this sheet writes about the wall is placed
    INSIDE the view, on bare wall, beside the thing it names.
    """
    global VIEW_Z0
    VIEW_Z0 = (SUB_Y + DESC * sh.sz["sub"] + TITLE_CLEAR + WALL_TICK
               + K * M.z_top)
    return VIEW_Z0


# ---------------------------------------------------------------------------
# WHAT THE MODEL KNOWS
# ---------------------------------------------------------------------------
class Model:
    """The wall zones, flattened into the fields this sheet draws."""

    def __init__(self, G, idx):
        self.G = G
        self.idx = idx
        by_label = {p.label: p for p in G.CUT_PARTS}
        self.fields = []            # one hatched field per part in a zone
        self.zones = []             # one entry per WALL_ZONES entry
        for n, zo in enumerate(G.WALL_ZONES, 1):
            z0, z1 = zo["z"]
            name = idx[zo["labels"][0]][0]
            spans = []
            for label in zo["labels"]:
                (x0, x1), _, _ = by_label[label].extents
                spans.append((round(x0, 3), round(x1, 3)))
                self.fields.append(dict(n=n, x0=x0, x1=x1, z0=z0, z1=z1,
                                        name=name, corner=zo["corner"]))
            self.zones.append(dict(n=n, z0=z0, z1=z1, name=name,
                                   corner=zo["corner"], spans=sorted(spans),
                                   count=len(zo["labels"]),
                                   labels=sorted(zo["labels"]),
                                   fix=sorted(zo["fix"]),
                                   riss=zo["riss"], riss_txt=zo["riss_txt"]))
        self.z_top = max(z["z1"] for z in self.zones) + AIR_OVER
        # The wall fixings: the screws that make the whole thing a rule rather
        # than a suggestion. Anchors are the model's own.
        #
        # X11: THERE ARE TWO ROWS ON THIS WALL NOW, at two heights - J14
        # through the back side rail at the top and J12-V through the table
        # ledger at desk height - so the sheet groups them by joint instead of
        # assuming one. Which joint, and how many, is not typed here: it is
        # read off the placed fasteners, and the zone each row belongs to is
        # the zone that owns the piece the screw goes THROUGH.
        rows = {}
        for fs in G.FASTENER_SPECS:
            if not fs.get("wall") or fs.get("anchor") is None:
                continue
            rows.setdefault(fs["jid"], set()).add(
                (round(fs["anchor"][0], 3), round(fs["anchor"][2], 3)))
        self.fixings = []
        for jid, pts in rows.items():
            pts = sorted(pts)
            zone = next(z for z in self.zones
                        if jid in [j for j, _n in z["fix"]])
            self.fixings.append(dict(jid=jid, xz=pts, z=pts[0][1],
                                     zone=zone["n"], name=zone["name"]))
        self.fixings.sort(key=lambda g: (-g["z"], g["jid"]))
        self.fix = sorted(p for g in self.fixings for p in g["xz"])

    def datum_gap(self):
        """The two bare-wall heights the height line is struck between."""
        bands = sorted((z["z0"], z["z1"]) for z in self.zones
                       if not z["corner"])
        d = self.G.MEASURE_DATUM_Z
        return (max(z1 for z0, z1 in bands if z1 <= d),
                min(z0 for z0, z1 in bands if z0 >= d))


# ---------------------------------------------------------------------------
# THE VIEW
# ---------------------------------------------------------------------------
def draw_wall(sh, M):
    """The niche itself: floor, two end walls, and the bare face between."""
    G = M.G
    x0, x1 = ex(0.0), ex(G.WALL_SPAN)
    top = zed(M.z_top)
    base = zed(0.0)
    sh.rect(x0, top, x1 - x0, base - top, "plain")
    # The two end walls and the floor are the three surfaces the model draws
    # as perfect planes and the room does not have. They get the heavy line
    # and the hatch ticks that say "this is building, not furniture".
    for sx, sgn in ((x0, -1.0), (x1, 1.0)):
        sh.line((sx, top - WALL_TICK), (sx, base), "wallf")
        n = int((base - (top - WALL_TICK)) // 62.0)
        for i in range(n + 1):
            y = top - WALL_TICK + i * 62.0
            sh.line((sx, y), (sx + sgn * 34.0, y - 34.0), "ext")
    sh.line((x0 - 60.0, base), (x1 + 60.0, base), "flr")
    for i in range(int((x1 + 60.0 - (x0 - 60.0)) // 62.0) + 1):
        x = x0 - 60.0 + i * 62.0
        sh.line((x, base), (x - 34.0, base + 34.0), "ext")


def draw_zones(sh, M, occ):
    """One hatched field per part, plus the badge that ties it to the table."""
    for fl in sorted(M.fields, key=lambda f: (f["n"], f["x0"])):
        x, y = ex(fl["x0"]), zed(fl["z1"])
        w, h = K * (fl["x1"] - fl["x0"]), K * (fl["z1"] - fl["z0"])
        sh.rect(x, y, w, h, "zone")
        occ.add_box((x, y, w, h), weight=W_ZONE, tag="zone")
    for fl in sorted(M.fields, key=lambda f: (f["n"], f["x0"])):
        cx = ex((fl["x0"] + fl["x1"]) / 2.0)
        cy = zed((fl["z0"] + fl["z1"]) / 2.0)
        if fl["corner"]:
            cy = zed(fl["z1"] - 150.0)
        r = 26.0
        sh.circle((cx, cy), r, "picf")
        sh.text((cx, cy + sh.sz["pt"] * 0.36), str(fl["n"]), "pt", "middle")
        occ.add_point((cx, cy), radius=r, weight=W_MARK, tag="mark")


def draw_zone_names(sh, M, occ):
    """The part each zone carries, written where there is still room for it.

    LAST of the three label passes on the wall face, and that is the rule the
    sheet resolves its collisions by: what has the least freedom is written
    first. The height line's caption cannot leave its line, a fixing row's
    label cannot leave its row - but a zone name has a whole band edge to
    slide along, so it is the one that gives way.
    """
    bd = wall_bounds(M)
    for z in M.zones:
        if z["corner"]:
            # A 98 mm column has no room for words, so the two corner fields
            # are named on the bare wall beside themselves, each label
            # pointing INTO its own column. Short, and side-specific: the
            # sheet knows which side each field is on (X = 0 is the left end
            # wall), and the full sentence - the band, the riss notation, the
            # two-fields-one-part of it - stands once, in the notes column
            # under HJØRNENE. Written out here twice, 300 mm apart, it read
            # as two different fields saying the same thing.
            for a, b in z["spans"]:
                left = (a + b) / 2.0 < M.G.WALL_SPAN / 2.0
                txt = (f"{z['name'].split(',')[0]}, "
                       f"{'venstre' if left else 'høyre'} — sone {z['n']}")
                anch = "start" if left else "end"
                x = ex(b) + 24.0 if left else ex(a) - 24.0
                lo, hi = M.datum_gap()
                # No tether: the rule for the bare band is the one gap_rows()
                # states - the highest free row - and a pull towards the
                # middle of the band would only ever pull a label towards the
                # height line, which is the one thing already written there.
                cands = [(x, y) for y in gap_rows(sh, lo, hi)]
                put_free(sh, occ, cands, txt, "smh", anch, bounds=bd)
            continue
        txt = (f"{z['name']} — {nb(z['z0'], 0)}–{nb(z['z1'], 0)} over gulv  ·  "
               f"{z['riss_txt']}")
        x0 = ex(min(s[0] for s in z["spans"])) + 20.0
        cands = [(x0 + i * LAB_STEP, y)
                 for y in band_rows(sh, z["z0"], z["z1"])
                 for i in range(4)]
        put_free(sh, occ, cands, txt, "smh", "start", bounds=bd)


def gap_rows(sh, z0, z1, cls="sml"):
    """Every text baseline that fits on the bare wall between two bands.

    The band of wall the height line is struck on is the one piece of this
    elevation with room for prose, so it is treated as a stack of rows and
    handed out top down. Whoever asks first gets the top one.
    """
    lead = sh.sz[cls] * 1.42
    top = zed(z1) + sh.sz[cls] * 1.15
    n = max(1, int((zed(z0) - sh.sz[cls] * 0.5 - top) // lead) + 1)
    return [top + i * lead for i in range(n)]


def draw_datum(sh, M, occ):
    """The height line the whole fitting job is measured from.

    Its caption is the first label placed on the wall face, because it is the
    one that cannot move away: it names a line, and the line is where the
    laser puts it. It may slide ALONG the line, and it would rather sit over
    the line than under it - that is the whole candidate list.
    """
    G = M.G
    d = G.MEASURE_DATUM_Z
    sh.line((ex(0.0) - 120.0, zed(d)), (ex(G.WALL_SPAN) + 120.0, zed(d)),
            "ctr")
    txt = (f"HØYDERISS {nb(d, 0)} OVER FERDIG GULV — 0 I RISS-NOTASJONEN "
           f"(MINUS ER UNDER, PLUSS ER OVER)")
    x0 = ex(0.0) + 150.0
    cands = [(x0 + i * LAB_STEP, y)
             for y in (zed(d) - sh.sz["sml"] * 0.5,
                       zed(d) + sh.sz["sml"] * 1.15)
             for i in range(5)]
    put_free(sh, occ, cands, txt, "smh", "start", bounds=wall_bounds(M))


def draw_fixings(sh, M, occ):
    """The screws through the bed and into the wall - one row per joint.

    X11 put a SECOND row on this wall, and the single tally that used to be
    written over the whole drawing had to become one label per row: two rows
    named in one sentence is a sentence that grows with the bed, and it grew
    off the top of the paper. Each row is now named beside its own screws, on
    bare wall over its own band, with a leader back to the nearest screw in
    it - and where "beside" is, is the placer's business, not a typed offset.
    """
    for g in M.fixings:
        for x, z in g["xz"]:
            sh.circle((ex(x), zed(z)), 12.0, "scro")
            sh.circle((ex(x), zed(z)), 4.5, "scrp")
            occ.add_point((ex(x), zed(z)), radius=26.0, weight=W_MARK,
                          tag="mark")
    zb = {z["n"]: z for z in M.zones}
    for g in M.fixings:
        z = zb[g["zone"]]
        txt = (f"{len(g['xz'])} × veggfeste ({g['jid']}) — Z "
               f"{nb(g['z'], 0)}, sone {g['zone']}")
        x1 = ex(M.G.WALL_SPAN) - 24.0
        cands = [(x1 - i * LAB_STEP, y)
                 for y in band_rows(sh, z["z0"], z["z1"])
                 for i in range(5)]
        p, box = put_free(sh, occ, cands, txt, "smh", "end",
                          bounds=wall_bounds(M))
        # The leader, out of the screw nearest the label. If the label stands
        # clear of its row it gets the height ladder's own knee - out of the
        # screw, then in to the near edge. If it stands OVER one of its own
        # screws it gets a plain tick instead: an elbow would have to cross
        # the words to reach their edge, and a line through a label is worse
        # than no leader at all.
        mid = box[0] + box[2] / 2.0
        near = min(g["xz"], key=lambda q: abs(ex(q[0]) - mid))
        nx, ny = ex(near[0]), zed(near[1])
        over = p[1] < ny
        if box[0] - 14.0 <= nx <= box[0] + box[2] + 14.0:
            sh.line((nx, ny), (nx, box[1] + box[3] + 6.0 if over
                               else box[1] - 6.0), "ext")
        else:
            ty = p[1] - sh.sz["sml"] * 0.34
            edge = (box[0] - 14.0 if nx < box[0] else box[0] + box[2] + 14.0)
            sh.pline([(nx, ny), (nx, ty), (edge, ty)], "ext")


# ---------------------------------------------------------------------------
# THE DIMENSIONS - every one of them from the finished floor
# ---------------------------------------------------------------------------
def draw_heights(sh, M):
    """The vertical chain: floor to zone edge to zone edge, all the way up."""
    stations = sorted({0.0} | {z["z0"] for z in M.zones}
                      | {z["z1"] for z in M.zones})
    x = CHAIN_X
    for a, b in zip(stations, stations[1:]):
        sh.dim((x, zed(a)), (x, zed(b)), nb(b - a, 0), 0.0, 1, "dmh")
        sh.line((ex(0.0), zed(b)), (x - 16.0, zed(b)), "ext")
    sh.line((ex(0.0), zed(stations[0])), (x - 16.0, zed(stations[0])), "ext")


def ladder(M):
    """(z, text) - every height on this wall, read off the model."""
    G = M.G
    L = [(0.0, "ferdig gulv — alle mål herfra")]
    for z in M.zones:
        low = f"uk {z['name'].lower()}"
        high = f"ok {z['name'].lower()}"
        if z["z0"] > 0.0:
            L.append((z["z0"], f"{low} — sone {z['n']} begynner"))
        L.append((z["z1"], f"{high} — sone {z['n']} slutter"))
    L.append((float(G.MEASURE_DATUM_Z), "høyderiss (laser rundt hele nisja)"))
    for g in M.fixings:
        L.append((g["z"], f"veggfeste {g['jid']}"))
    return sorted(L, key=lambda r: (-r[0], r[1]))


def draw_ladder(sh, M):
    """The heights, spread so no two labels sit on top of one another."""
    rows = ladder(M)
    lead = sh.sz["sml"] * 1.42
    ys = []
    for z, _ in rows:
        y = zed(z) + sh.sz["sml"] * 0.36
        if ys and y - ys[-1] < lead:
            y = ys[-1] + lead
        ys.append(y)
    right = ex(M.G.WALL_SPAN)
    for (z, txt), y in zip(rows, ys):
        sh.line((right + 24.0, zed(z)), (LAD_X, zed(z)), "ext")
        if abs(y - (zed(z) + sh.sz["sml"] * 0.36)) > 1.0:
            sh.pline([(LAD_X, zed(z)), (LAD_X + 26.0, zed(z)),
                      (LAD_X + 52.0, y - sh.sz["sml"] * 0.34)], "ext")
        sh.text((LAB_X, y),
                f"{nb(z, 0)}   ({M.G.riss_num(z)} fra risset)   {txt}", "sml")


def draw_widths(sh, M):
    """One dimension row per distinct field width, then the niche itself."""
    rows, order = {}, []
    for z in M.zones:
        key = tuple(z["spans"])
        if key not in rows:
            rows[key] = []
            order.append(key)
        rows[key].append(z["n"])
    base = zed(0.0) + 120.0
    for key in order:
        ns = rows[key]
        for a, b in key:
            sh.dim((ex(a), base), (ex(b), base), nb(b - a, 0), 0.0, 1, "dmh")
        word = "sone " + (" og ".join(str(n) for n in ns) if len(ns) < 3
                          else ", ".join(str(n) for n in ns))
        sh.text((LAD_X, base + sh.sz["dm"] * 0.36), word, "sml")
        base += 95.0
    sh.dim((ex(0.0), base), (ex(M.G.WALL_SPAN), base),
           f"{nb(M.G.WALL_SPAN, 0)}  nisjas bredde, vegg til vegg", 0.0, 1,
           "dmh")
    return base


# ---------------------------------------------------------------------------
# THE WORDS
# ---------------------------------------------------------------------------
def notes(M, T):
    G = M.G
    below, above = M.datum_gap()
    corner = [z for z in M.zones if z["corner"]]
    zone_lines = [
        f"Sone {z['n']}:  {nb(z['z0'], 0)}–{nb(z['z1'], 0)} over ferdig gulv  "
        f"=  {z['riss_txt']} — {z['name']}"
        + (f" ({z['count']} stk., ett felt i hvert hjørne)"
           if z["count"] > 1 else "")
        for z in M.zones
    ]
    return [
        ("LEGG SPIKERSLAG MENS VEGGEN ER ÅPEN", [
            f"Sengen presser på bakveggen i {len(M.zones)} bånd, ikke overalt. "
            f"Her er båndene. Legger du spikerslag i dem før veggen lukkes, "
            f"kan du feste sengen hvor som helst i sonen. Etterpå kommer du "
            f"ikke til.",
        ] + zone_lines),
        ("HØYDERISSET", [
            f"Slå et vannrett riss rundt hele nisja med linjelaser, "
            f"{nb(G.MEASURE_DATUM_Z, 0)} mm over ferdig gulv. Alle høyder på "
            f"dette arket er målt fra ferdig gulv, og på veggen måler du dem "
            f"ned eller opp fra risset — aldri fra gulvet.",
            f"Derfor står hver høyde to ganger: over ferdig gulv, og i "
            f"parentes det samme tallet minus {nb(G.MEASURE_DATUM_Z, 0)} — "
            f"minus er under laserlinja, pluss er over. Gulvet er skjevt og "
            f"risset er ikke, så det er parentesen du setter sonene etter.",
            f"Risset ligger på bar vegg mellom sone-toppen {nb(below, 0)} og "
            f"sone-bunnen {nb(above, 0)}, så det er synlig helt til sengen "
            f"står inntil. Det er en assert i modellen.",
            _plain(T.ROOM_ZONE_NOTE),
        ]),
        ("HJØRNENE", [
            f"De to feltene i hjørnene går fra gulvet og opp til "
            f"{nb(corner[0]['z1'], 0)}, og de er "
            f"{nb(corner[0]['spans'][0][1] - corner[0]['spans'][0][0], 0)} mm "
            f"brede — bredden på den bakre hjørnestolpen. Stolpen står i "
            f"veggplanet uten klaring, mot både endeveggen og bakveggen, så "
            f"det er i disse to smale feltene hele endekreftene tas.",
        ]),
        ("VEGGFESTENE", [
            f"{len(M.fix)} skruer i {len(M.fixings)} rader, gjennom sengen og "
            f"inn i veggen. Ingen brakett, ingen kloss: begge delene ligger "
            f"flatt mot veggen i hele sin lengde. Treffer en skrue verken "
            f"stender eller spikerslag, er festet verdiløst — det er derfor "
            f"sonen skal ligge der før platen skrus opp.",
        ] + [
            f"{g['jid']}:  {len(g['xz'])} stk. i Z {nb(g['z'], 0)} — gjennom "
            f"{g['name'].lower()}, sone {g['zone']}."
            for g in M.fixings
        ] + [
            f"De andre {sum(1 for z in M.zones if not z['fix'])} sonene får "
            f"ingen skrue. De er anleggsflater: sengen presser mot veggen "
            f"der, og spikerslaget skal likevel ligge der.",
        ]),
        ("HVA ARKET IKKE SIER", [
            "Hvor stenderne står. Det vet huset, ikke modellen. Sonene er "
            "høydene og breddene sengen trenger tre bak; hvordan du får tre "
            "dit — spikerslag mellom stendere, gjennomgående lekt eller en "
            "hel plate — er veggens sak.",
        ]),
    ]


def _plain(md):
    """A markdown line as the drawing writes it - no asterisks on a sheet."""
    return md.replace("**", "")


def note_h(sh, blocks):
    """How deep a run of prose sets - measured before it is set.

    Every number in it is one draw_notes() uses two lines further down, so
    the two cannot drift apart: head, one lead per WRAPPED line, and the
    half-line of air after the block.
    """
    h = 0.0
    for _head, rows in blocks:
        h += sh.sz["leg"] * 1.5
        for row in rows:
            h += len(sh.wrap(row, NOTE_W)) * sh.sz["sml"] * 1.35
        h += sh.sz["sml"] * 0.9
    return h


def note_split(sh, blocks):
    """Where the prose breaks over the two columns.

    It used to break at the halfway BLOCK, which is the halfway DEPTH only by
    luck - and depth is what the paper is bought by: the sheet is as tall as
    its deeper column, and it has to stay a landscape sheet (LAND_LIMIT). So
    the break is the one that leaves the two columns most nearly equal. Ties
    fall to the earliest, so the same prose always breaks in the same place.
    """
    best = None
    for cut in range(1, len(blocks)):
        deep = max(note_h(sh, blocks[:cut]), note_h(sh, blocks[cut:]))
        if best is None or deep < best[0]:
            best = (deep, cut)
    return best[1]


def draw_notes(sh, M, T, y0):
    """The prose, in two columns. Returns where each column ran out."""
    blocks = notes(M, T)
    cut = note_split(sh, blocks)
    ends = []
    for col, group in ((0, blocks[:cut]), (1, blocks[cut:])):
        x = NOTE_X[col]
        y = y0
        for head, rows in group:
            sh.text((x, y), head, "leg")
            y += sh.sz["leg"] * 1.5
            for row in rows:
                y = sh.lines((x, y), sh.wrap(row, NOTE_W), "sml") \
                    + sh.sz["sml"] * 1.35
            y += sh.sz["sml"] * 0.9
        ends.append(y - sh.sz["sml"] * (1.35 + 0.9))
    return ends


LEGEND = [
    ("zonekey",
     "Sone som skal ha spikerslag — hele feltet, ikke bare en linje"),
    ("plain", "Bar vegg — ingenting av sengen ligger inntil"),
]


def draw_legend(sh, M, x, y):
    """The key, in the top right corner - beside the title, over the height
    ladder's own column.

    It used to set under the right-hand prose column, and that cost the sheet
    218 units of PAPER: the sheet is as tall as its deeper column, and the
    legend was the bottom fifth of one of them. Up here it costs nothing - the
    band beside the title block is white all the way to the sheet edge,
    because the drawing under it starts at the wall face and the wall face
    starts below the title (set_view) - and it is nearer the drawing it
    explains than it was at the foot of the page.
    """
    sh.text((x, y), "TEGNFORKLARING", "leg")
    y += sh.sz["leg"] * 1.6
    for cls, txt in LEGEND:
        sh.rect(x, y - sh.sz["sml"] * 0.85, 90.0, sh.sz["sml"] * 1.1, cls)
        sh.text((x + 112.0, y), txt, "sml")
        y += sh.sz["sml"] * 1.55
    sh.line((x, y - sh.sz["sml"] * 0.3), (x + 90.0, y - sh.sz["sml"] * 0.3),
            "ctr")
    sh.text((x + 112.0, y), "Høyderiss over ferdig gulv", "sml")
    y += sh.sz["sml"] * 1.55
    sh.circle((x + 45.0, y - sh.sz["sml"] * 0.3), 12.0, "scro")
    sh.circle((x + 45.0, y - sh.sz["sml"] * 0.3), 4.5, "scrp")
    sh.text((x + 112.0, y),
            "Veggfeste (" + " / ".join(g["jid"] for g in M.fixings)
            + ") — skrue inn i veggen", "sml")
    return y


# ---------------------------------------------------------------------------
# THE ASSERT THAT READS THE INK
# ---------------------------------------------------------------------------
_ZONE_RE = re.compile(
    r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" '
    r'height="([\d.]+)" class="zone"/>')


def assert_zone_ink(path, M):
    """Every hatched field on the finished sheet, converted back to model
    millimetres, has to be a part in WALL_ZONES - and every part in WALL_ZONES
    has to have a field."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    drawn = []
    for sx, sy, sw, sh_ in _ZONE_RE.findall(text):
        x0 = un_ex(float(sx))
        x1 = un_ex(float(sx) + float(sw))
        z1 = un_zed(float(sy))
        z0 = un_zed(float(sy) + float(sh_))
        drawn.append(tuple(round(v, 2) for v in (x0, x1, z0, z1)))
    want = sorted(tuple(round(v, 2) for v in (f["x0"], f["x1"],
                                              f["z0"], f["z1"]))
                  for f in M.fields)
    assert sorted(drawn) == want, (
        f"de skraverte feltene på arket er ikke sonene i modellen:\n"
        f"  tegnet:  {sorted(drawn)}\n"
        f"  modell:  {want}")
    return len(drawn)


# X8b - AND THE SAME TREATMENT FOR THE SECOND NOTATION. Every height on the
# ladder is written twice on this sheet - over the finished floor, and from
# the height line - and the second one is only worth anything if it really is
# the first one minus the datum. So the finished SVG is read back and the
# subtraction is done on the INK: one line that disagrees, or a datum that
# moved and took only one of the two with it, stops the build.
_RISS_RE = re.compile(r">(\d+)   \(([-+]?\d+) fra risset\)")


def assert_riss_ink(path, M):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    found = _RISS_RE.findall(text)
    assert len(found) == len(ladder(M)), \
        (f"{len(found)} høyder på arket er skrevet i begge notasjoner, men "
         f"høydestigen har {len(ladder(M))} rader")
    for z, r in found:
        assert float(z) - float(r) == float(M.G.MEASURE_DATUM_Z), \
            (f"høyden {z} er skrevet som {r} fra risset: differansen er "
             f"{float(z) - float(r)}, og den SKAL være høyderisset selv, "
             f"{M.G.MEASURE_DATUM_Z}")
    return len(found)


# X12 - AND THE SAME TREATMENT FOR THE TYPE. The two asserts above read the
# drawing back; this one reads the WORDS back. Every <text> on the finished
# sheet is measured with the estimate at the top of this file and has to be
# alone where it stands, and to stand on the paper at all.
#
# It exists because this sheet had four printed collisions at once - a title
# under its own wall, a fixing tally over the top edge, the height line's
# caption through a zone name, and one zone name written out twice - and every
# one of them arrived the same way: a label at a coordinate that was right for
# the model on the day it was typed. The asserts on the fields and the heights
# would not have said a word about any of them. This one says all four.
#
# It is an estimate, so it is deliberately fat (see EM_* at the top) and it
# compares the estimates, not the glyphs. A pair that JUST touches on paper
# but not in the estimate is a drawing that reads; a pair that touches in the
# estimate is moved whether it would have read or not. That is the right way
# round for a proof.
_TXT_RE = re.compile(
    r'<text x="([-\d.]+)" y="([-\d.]+)" class="([a-z]+)" '
    r'text-anchor="([a-z]+)">(.*?)</text>')


def _unesc(s):
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def assert_text_ink(path, sh):
    """No two labels on the finished sheet touch, and none hangs off it."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    lab = []
    for sx, sy, cls, anchor, body in _TXT_RE.findall(text):
        s = _unesc(body)
        lab.append((tbox(sh, (float(sx), float(sy)), s, cls, anchor), s))
    x0, y0 = sh.origin
    x1, y1 = x0 + sh.w, y0 + sh.h
    for (bx, by, bw, bh), s in lab:
        assert (bx >= x0 and by >= y0 and bx + bw <= x1 and by + bh <= y1), (
            f"teksten «{s}» ligger utenfor arkflaten: den dekker "
            f"({bx:.0f}, {by:.0f}) til ({bx + bw:.0f}, {by + bh:.0f}), og "
            f"arket går fra ({x0:.0f}, {y0:.0f}) til ({x1:.0f}, {y1:.0f})")
    for i, (a, sa) in enumerate(lab):
        for b, sb in lab[i + 1:]:
            ow = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
            oh = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
            assert ow <= 0.0 or oh <= 0.0, (
                f"to tekster på arket ligger oppå hverandre "
                f"({ow:.0f} × {oh:.0f} enheter):\n"
                f"  «{sa}»  ved ({a[0]:.0f}, {a[1]:.0f})\n"
                f"  «{sb}»  ved ({b[0]:.0f}, {b[1]:.0f})")
    return len(lab)


# ---------------------------------------------------------------------------

def build(G, T):
    idx = T.cut_index(G)
    M = Model(G, idx)
    # The height is filled in at the bottom of this function, once the last
    # word is written: see LAND_LIMIT.
    sh = Sheet(SHEET_W, 0.0, STYLE_K,
               "Loftseng - bakveggen, spikerslagsoner",
               width=2400, origin=ORIGIN, extra_css=EXTRA_CSS)
    occ = Occupancy()
    # The title block first, and the drawing under it - not the other way
    # round, which is what a typed VIEW_Z0 amounted to.
    put(sh, occ, (MARG, TTL_Y), "BAKVEGGEN — SPIKERSLAGSONER, OPPRISS (X–Z)",
        "ttl")
    put(sh, occ, (MARG, SUB_Y),
        f"Veggen sengen skrus fast i, sett som oppriss · X langs veggen "
        f"(0 = venstre endevegg, {nb(G.WALL_SPAN, 0)} = høyre) · Z opp fra "
        f"FERDIG GULV · alle mål i mm · legg spikerslagene FØR veggen "
        f"lukkes", "sub")
    draw_legend(sh, M, LAD_X, TTL_Y)
    set_view(sh, M)
    draw_wall(sh, M)
    draw_zones(sh, M, occ)
    # The three label passes on the wall face, in order of how little freedom
    # each has - see draw_zone_names().
    draw_datum(sh, M, occ)
    draw_fixings(sh, M, occ)
    draw_zone_names(sh, M, occ)
    draw_heights(sh, M)
    draw_ladder(sh, M)
    base = draw_widths(sh, M)
    ends = draw_notes(sh, M, T, base + NOTE_GAP)
    sh.h = max(ends) + FOOT_GAP + 40.0 - ORIGIN[1]
    sh.text((MARG, ORIGIN[1] + sh.h - 40.0),
            "Alle soner, høyder og bredder er lest ut av generate_loftbed.py "
            "(WALL_ZONES) — ingen av dem er skrevet inn her. Generert av "
            "tools/render_spikerslag.py; rediger ikke for hånd.", "tiny")
    return sh, M


def main(argv):
    out = OUT
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    import generate_loftbed as G
    import gen_doc_tables as T
    sh, M = build(G, T)
    sh.write(out)
    n = assert_zone_ink(out, M)
    nr = assert_riss_ink(out, M)
    nt = assert_text_ink(out, sh)
    assert sh.w / sh.h > LAND_LIMIT, (
        f"arket er blitt {nb(sh.w, 0)} × {nb(sh.h, 0)} enheter, altså "
        f"{sh.w / sh.h:.3f} bredt over høyt, og under {LAND_LIMIT} trykker "
        f"tools/build_pdf.py det stående. Veggen er en liggende tegning: "
        f"enten må notatspalten kortes ned, eller så må de to spaltene "
        f"balanseres på nytt")
    print(f"wrote {out}  ({n} skraverte felt i "
          f"{len(M.zones)} soner, {nb(M.z_top, 0)} mm vegg tegnet, "
          f"{nr} høyder skrevet både over gulv og fra høyderisset, "
          f"{nt} tekster uten overlapp på et ark {nb(sh.w, 0)} × "
          f"{nb(sh.h, 0)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
