#!/usr/bin/env python3
"""MÅL ROMMET FØRST, drawn: docs/img/maal-rommet.svg.

The one figure in the manual with no bed in it. The pre-step tells the reader
to strike a height line round the niche, stand a plumb line down the middle of
it and read each end wall on a grid of so many heights by so many depths; this
draws exactly that, and nothing else.

THREE VIEWS, AND WHAT EACH OF THEM IS FOR
-----------------------------------------
    the ROOM - the niche as a room you can stand in, left. It answers "what
        am I looking at", and it is the only view where the height line is a
        RING: it runs up one end wall, across the back and down the other, and
        meets itself. That is the whole reason this view exists, and it is why
        it carries almost no numbers - one 1000, one 1990, one example arrow,
        and the two counts. Fifteen arrows in a room view was tried and it was
        unreadable.
    the ELEVATION - the niche from the room, top right. THIS is the
        instrument: the height line runs level right across it and out past
        both end walls, the plumb line stands down the middle, and the arrows
        go out to the left end wall at each HEIGHT.
    the PLAN - the same niche from above, under the elevation and on the same
        verticals, the way a drawing office stacks them, so the two 1990s are
        visibly the same 1990. Same plumb line, same left end wall, and the
        arrows go out to it at each DEPTH.

The room view stands alone in the left column against two views stacked in the
right, so it is drawn LARGER than they are - exactly as tall as the two of them
together, top to bottom, which is a scale solved rather than chosen (see
ROOM_S in render()). It is a perspective and has no true scale to lose; the
flat views keep theirs and keep it between them.

WHY THE ROOM VIEW IS A PERSPECTIVE AND NOT AN AXONOMETRIC
--------------------------------------------------------
It was meant to be an axonometric - cheaper, and the house draws in flat
projections everywhere else. It cannot be. Whether you see the INSIDE of an
end wall in a parallel projection depends only on the sign of the projection
direction's X component, and the two end walls face opposite ways: whichever
way you turn the room, one of them is seen from inside and the other from
outside. Turn it to zero and both go edge-on. So no axonometric, isometric or
oblique can show the height line running down BOTH end walls - and that ring
closing on itself is the one thing this view is here to say.

A perspective can, because the two walls converge. So the room view is a
one-point perspective with the picture plane in the OPENING: at the mouth of
the niche the projection is the identity, so everything there is drawn in the
elevation's own coordinates - the hatched wall and floor frame round it is the
elevation's own three rectangles, at the room view's scale - and everything
behind it shrinks towards one vanishing point. Verticals stay vertical, the
back wall stays square, and the whole thing is three lines of arithmetic in
eye() with no solid modeller in it, so it is as deterministic as the flat views
beside it - and it inverts in closed form, which is what lets assert_ring()
read the finished path back into millimetres.

The eye's three numbers are fractions of the model's own, at the top of the
file. It stands above the top of the walls, so their cut tops show; it stands
off centre, so the far end wall - the one the readings are taken on - opens up
wider than the near one; and it does NOT stand at 1000, because an eye on the
height line would flatten the ring into a single straight line.

WHAT IS DRAWN AS CUT
--------------------
The drawing cuts the room in the plane of the opening, and the cut is hatched
- the two end walls and the floor, seen full face, exactly as in the elevation.
The tops of the walls are the second cut (the model has no ceiling); they are
seen at a glancing angle and are too thin to hatch, so they are drawn as plain
bands and the hatch at the mouth carries the thickness.

THE NUMBERS
-----------
WALL_SPAN, MEASURE_DATUM_Z, MEASURE_GRID, OVERALL_DEPTH and POST_HEIGHT out of
generate_loftbed.py. The niche is drawn as high as the bed is - the model has
no ceiling and this figure does not invent one - and the grid spans the bed's
own height and depth, because that is the part of the wall the bed touches.

The numbers the model has no opinion about are named at the top of the file:
how thick the surrounding building is drawn, how far apart the views stand,
how far the height line runs past the niche, and where the eye stands. The PEN
is this figure's own as well - see the block in render() and the reason it is
not the bed's.

There are no words in the figure. The words are on the page it sits on: the
only type on it is the millimetre readings and the two grid counts.

THE ASSERTS READ THE INK
------------------------
Three of them, and all three read what was emitted rather than what was meant:

    assert_ring() takes the height line back out of the emitted path. It has
        to be ONE polyline of three segments that meet, level across the back,
        riding higher there than at its ends and turning in at both back
        corners - and each of its four vertices, put back through the camera,
        has to land on a corner of the niche at MEASURE_DATUM_Z.
    assert_grid_on_wall() counts the emitted dots against MEASURE_GRID and
        demands that every one of them fall inside the polygon that was
        emitted for the end wall.
    assert_fits_column() holds the drawing and gen_doc_tables.ROOM_FIG_PX
        together: at the height the manual sets the figure in, the figure's
        own proportions have to come out the width of the text column. Change
        the composition and this one tells you the new number.

Entry point:
    render(G, out_dir, width) -> path of the PNG
"""

import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The things the model has no opinion about: how thick the surrounding
# building is DRAWN, how far apart the views stand, and how far the height
# line runs past the niche it is struck round.
WALL_T = 120.0
GAP = 640.0
GAP_V = 3.0             # between elevation and plan, in type sizes
OVERRUN = 90.0

# WHERE THE EYE STANDS for the room view, as fractions of the model's own
# numbers - nothing here is a millimetre.
#   BACK  in front of the mouth of the niche, x WALL_SPAN. Sets how hard the
#         perspective bites; about one niche width is a normal room's worth.
#   UP    above the finished floor, x POST_HEIGHT. Above the top of the walls,
#         so the cut tops show - and deliberately NOT at MEASURE_DATUM_Z,
#         which would put the eye on the height line and flatten the ring
#         into one straight line.
#   OVER  along the wall from the left end, x WALL_SPAN. Off centre, so the
#         LEFT end wall - the one the elevation and the plan take their
#         readings on - is the one that opens up.
EYE_BACK = 1.20
EYE_UP = 1.40
EYE_OVER = 0.72

# The page the figure is printed on: A4 less 15 mm each side. The figure is
# drawn to fill it, and gen_doc_tables.ROOM_FIG_PX is the height in CSS pixels
# that does so - the assert at the bottom holds the two together.
TEXT_MM = 180.0
PX_MM = 25.4 / 96.0


# ---------------------------------------------------------------------------
# THE ASSERTS THAT READ THE INK
# ---------------------------------------------------------------------------
_PT = re.compile(r"(-?[\d.]+),(-?[\d.]+)")


def _points(element):
    """The points back out of an emitted <path>, in the figure's own
    coordinates - Page draws with y flipped, so flip it back."""
    i = element.index('d="') + 3
    d = element[i:element.index('"', i)]
    return [(float(a), -float(b)) for a, b in _PT.findall(d)]


def assert_ring(element, back, span, datum, eps):
    """The height line, taken back out of the ink.

    Two things are asked of it. In the PICTURE it has to be ONE polyline of
    three segments that MEET - three separate lines would look the same on
    paper and say nothing - its back run has to be level, ride higher than its
    two ends, and turn inwards at both back corners, which is what "the eye is
    above the line and the line goes round the back" looks like.

    And in the ROOM: each of the four vertices, taken back through the camera
    at the depth it was drawn at, has to land on a corner of the niche at
    exactly MEASURE_DATUM_Z. `back(point, at_back)` is that inverse. A ring
    that drifted off the walls, or a camera that stopped agreeing with itself,
    dies here rather than in print.
    """
    assert element.count("M") == 1, \
        "høyderisset er tegnet som flere streker - ringen må være én linje"
    p = _points(element)
    assert len(p) == 4, \
        f"høyderisset har {len(p) - 1} segmenter, ikke 3 (én per vegg)"
    assert abs(p[1][1] - p[2][1]) < eps, \
        "løpet langs bakveggen er ikke vannrett i bildet"
    assert p[1][1] > p[0][1] + eps, \
        "risset stiger ikke innover - øyet ser ikke ned på ringen"
    assert p[0][0] < p[1][0] < p[2][0] < p[3][0], \
        "ringen svinger ikke innover i begge bakhjørnene"
    want = ((0.0, 0), (0.0, 1), (span, 1), (span, 0))
    for q, (wx, deep) in zip(p, want):
        x, z = back(q, deep)
        assert abs(x - wx) < eps and abs(z - datum) < eps, \
            (f"et hjørne av ringen ligger på ({x:.1f}, {z:.1f}) i rommet, "
             f"ventet ({wx:.0f}, {datum:.0f})")
    return p


def assert_grid_on_wall(wall_element, dot_elements, n_h, n_d):
    """Every reading point is a dot, and every dot is ON the end wall.

    The count is MEASURE_GRID's own product, and the containment test is run
    against the polygon that was actually emitted for the wall - so a camera
    that drifts, or a grid that runs off the wall, stops the drawing.
    """
    assert len(dot_elements) == n_h * n_d, \
        (f"{len(dot_elements)} rutenettprikker tegnet, "
         f"men MEASURE_GRID er {n_h}×{n_d} = {n_h * n_d}")
    poly = _points(wall_element)
    for el in dot_elements:
        cx = float(re.search(r'cx="(-?[\d.]+)"', el).group(1))
        cy = -float(re.search(r'cy="(-?[\d.]+)"', el).group(1))
        inside = False
        j = len(poly) - 1
        for i, (xi, yi) in enumerate(poly):
            xj, yj = poly[j]
            if (yi > cy) != (yj > cy) and \
                    cx < (xj - xi) * (cy - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        assert inside, \
            f"rutenettprikk ({cx:.1f}, {cy:.1f}) ligger utenfor endeveggen"
    return len(dot_elements)


def assert_fits_column(page, fig_px):
    """The figure, at the height the manual sets it in, has to come out the
    width of the text column - not wider (the browser would squeeze it) and
    not much narrower (the drawing would be smaller than it needs to be)."""
    mm = page.w / page.h * fig_px * PX_MM
    assert TEXT_MM - 1.0 < mm <= TEXT_MM, \
        (f"figuren blir {mm:.2f} mm bred ved ROOM_FIG_PX={fig_px}, "
         f"men satsbredden er {TEXT_MM:.0f} mm - sett ROOM_FIG_PX til "
         f"{int(TEXT_MM / (page.w / page.h) / PX_MM)}")
    return mm


# ---------------------------------------------------------------------------

def render(G, out_dir, width):
    import render_lineart as RL
    RL.use_model(G)

    W = float(G.WALL_SPAN)
    D = float(G.OVERALL_DEPTH)
    H = float(G.POST_HEIGHT)
    EYE = float(G.MEASURE_DATUM_Z)
    n_h, n_d = G.MEASURE_GRID

    heights = [H * (i + 0.5) / n_h for i in range(n_h)]
    depths = [D * (j + 0.5) / n_d for j in range(n_d)]   # from the BACK wall

    # -- THE EYE, and the projection it makes -------------------------------
    # One point, picture plane in the mouth of the niche: at y = 0 this is the
    # identity, so the mouth is drawn in the elevation's own coordinates and
    # the hatched frame round it is the same three rectangles.
    e_back = W * EYE_BACK
    e_up = H * EYE_UP
    e_over = W * EYE_OVER

    def eye(x, y, z):
        k = e_back / (e_back + y)
        return (e_over + (x - e_over) * k, e_up + (z - e_up) * k)

    # ...how high the room view comes out at its own scale: the far top corner
    # of the walls, which is the highest thing in it.
    top3 = eye(0.0, D + WALL_T, H)[1]

    # -- HOW BIG THE ROOM VIEW IS DRAWN -------------------------------------
    # It stands alone in the left column against TWO views stacked in the
    # right, so at one to one it would leave a quarter of the figure white.
    # The scale is therefore not chosen, it is solved: the room view is drawn
    # exactly as tall as the elevation and the plan together, top to bottom,
    # and the width follows. It is a perspective and has no true scale to
    # lose, so this costs nothing that the flat views have to keep.
    #
    #   room block   = (top3 + WALL_T)*s + 2,2 SZ
    #   right column = H + 2 WALL_T + D + OVERRUN + (2,2 + GAP_V) SZ
    #   SZ           = 0,016 (u s + C)
    #   u = W + 2 WALL_T,  C = GAP + W + WALL_T
    #
    # ...which is linear in s, so it comes out in one line rather than in a
    # loop that would have to be argued for.
    u = W + 2 * WALL_T
    C = GAP + W + WALL_T
    ROOM_S = ((H + 2 * WALL_T + D + OVERRUN + 0.0160 * GAP_V * C)
              / ((top3 + WALL_T) - 0.0160 * GAP_V * u))

    # The room view's outer wall face lands at u*ROOM_S - WALL_T; then GAP of
    # clear paper, then the elevation's own outer face at ox - WALL_T.
    ox = (u * ROOM_S - WALL_T) + GAP + WALL_T

    # THE PEN IS THIS FIGURE'S OWN, not the bed's. render_lineart sets its
    # theme from the FINISHED BED's diagonal, which is right for a page that
    # draws the bed and wrong for one that draws a room three times and
    # prints it at half the size - the numbers came out under a millimetre.
    # So every size here is a fixed fraction of the drawing's own width, the
    # way tools/render_cutpage.py does it: the figure is printed about 180 mm
    # wide, and SZ is the ~2,6 mm of type that has to be readable there.
    SPAN = ox + W + WALL_T
    SZ = SPAN * 0.0160
    W_BOX = SPAN * 0.0020
    W_RULE = SPAN * 0.0009
    W_HATCH = SPAN * 0.0007
    W_DATUM = SPAN * 0.0026     # the struck line - the one thing the page is
    W_PLUMB = SPAN * 0.0013     # about; the plumb line is only its partner
    # Room edges that run AWAY from the eye, lighter than the mouth they
    # start at - so the one heavy line inside the room is the struck one.
    W_EDGE = SPAN * 0.0013
    W_DIM = SPAN * 0.0010
    TICK = SZ * 0.50
    HEAD = SZ * 0.70
    HATCH = SZ * 0.90
    DOT = SZ * 0.18
    DASH = "30 10 6 10"         # the plumb line's dash-dot, both views

    # Where the plan hangs under the elevation.
    elev_base = -WALL_T - SZ * 1.2                 # the 1990 dimension line
    elev_foot = -WALL_T - SZ * 2.2                 # ...and the type under it
    plan_top = elev_foot - SZ * GAP_V - WALL_T     # the plan's back wall

    # The room view sits in the page with its outer wall face on the same
    # left-hand line the elevation's bracket is measured from, and its top -
    # the far corner of the walls - level with the top of the elevation.
    r_tx = -WALL_T * (1.0 - ROOM_S)
    r_ty = H - top3 * ROOM_S

    def RX(x):
        return r_tx + x * ROOM_S

    def RY(y):
        return r_ty + y * ROOM_S

    def P(x, y, z):
        """A point in the room, on the page."""
        p = eye(x, y, z)
        return (RX(p[0]), RY(p[1]))

    def unP(q, at_back):
        """...and back again, for a point known to have been drawn in the
        mouth of the niche (at_back = 0) or against the back wall (1). This is
        what assert_ring reads the finished path with."""
        px = (q[0] - r_tx) / ROOM_S
        py = (q[1] - r_ty) / ROOM_S
        k = e_back / (e_back + (D if at_back else 0.0))
        return (e_over + (px - e_over) / k, e_up + (py - e_up) / k)

    pad = SZ * 1.1
    x0 = -WALL_T - SZ * 1.9 - pad
    # ...and on the right the height line runs OUT past the building, so the
    # margin has to clear the overrun or the one line the page is about ends
    # against the edge of the paper.
    x1 = ox + W + WALL_T + max(pad, OVERRUN + SZ * 0.5)
    y0 = plan_top - D - OVERRUN - pad
    y1 = H + pad
    page = RL.Page(x0, y0, x1, y1)

    def wall(x, y, w, h):
        """A piece of the building: hatched, with a light outline."""
        page.hatch(x, y, w, h, HATCH, RL.GREY, W_HATCH)
        page.rect(x, y, w, h, fill="none", stroke=RL.GREY, width=W_RULE)

    def wall3(x, y, w, h):
        """The same, in the room view's own scale - the cut in the mouth of
        the niche is the elevation's three rectangles, drawn there."""
        wall(RX(x), RY(y), w * ROOM_S, h * ROOM_S)

    def measure(a, b):
        """One reading: arrows out from the middle to both ends."""
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        page.arrow(mid, a, RL.INK, W_DIM, HEAD)
        page.arrow(mid, b, RL.INK, W_DIM, HEAD)

    def bracket(x, lo, hi, text):
        """A square bracket down a column of readings, with its count."""
        page.polylines([[(x + TICK, hi), (x, hi), (x, lo), (x + TICK, lo)]],
                       RL.GREY, W_DIM)
        page.text((x - TICK * 0.6, (lo + hi) / 2.0 - SZ * 0.34), text, SZ,
                  anchor="end")

    def bracket_along(a, b, text):
        """The same bracket laid along a run of readings that goes away from
        the eye, so it has to lean with them."""
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1.0
        nx, ny = dy / n, -dx / n              # out, away from the niche
        # Further out than the flat views' bracket stands, because the line it
        # is offset from and the line it must not touch - the foot of the wall
        # and the row of readings just above it - both run to the same
        # vanishing point and close on each other as they go.
        off, lip = TICK * 3.0, TICK * 0.55

        def at(p, d):
            return (p[0] + nx * d, p[1] + ny * d)
        page.polylines([[at(a, off - lip), at(a, off), at(b, off),
                         at(b, off - lip)]], RL.GREY, W_DIM)
        m = at(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0), off + SZ * 0.85)
        page.text((m[0], m[1] - SZ * 0.34), text, SZ, anchor="middle")

    # -- THE ROOM -----------------------------------------------------------
    # Painter's order, back to front. Nothing here overlaps anything else -
    # an open box seen from outside its mouth has no hidden line problem - so
    # the white fills are only there to keep the paper clean.
    def face(pts, stroke="none", w=0.0):
        page.poly([P(*p) for p in pts], fill="#ffffff", stroke=stroke, width=w)

    face([(0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0)])                # floor
    face([(0, D, 0), (W, D, 0), (W, D, H), (0, D, H)])                # back
    i_wall = len(page.body)
    face([(0, 0, 0), (0, D, 0), (0, D, H), (0, 0, H)])                # left
    face([(W, 0, 0), (W, D, 0), (W, D, H), (W, 0, H)])                # right

    # The tops of the walls: the second cut, seen almost edge on. Plain bands
    # - the hatch that carries the thickness is at the mouth, full face.
    for pts in ([(-WALL_T, 0, H), (0, 0, H), (0, D + WALL_T, H),
                 (-WALL_T, D + WALL_T, H)],
                [(W, 0, H), (W + WALL_T, 0, H), (W + WALL_T, D + WALL_T, H),
                 (W, D + WALL_T, H)],
                [(0, D, H), (W, D, H), (W, D + WALL_T, H),
                 (0, D + WALL_T, H)]):
        face(pts, RL.GREY, W_RULE)

    # The cut in the plane of the opening - the elevation's own three
    # rectangles, square on, because the picture plane IS that plane.
    wall3(-WALL_T, 0.0, WALL_T, H)
    wall3(W, 0.0, WALL_T, H)
    wall3(-WALL_T, -WALL_T, W + 2 * WALL_T, WALL_T)

    # The mouth of the niche, in the elevation's own weight - it is the same
    # three sides that view draws, at the same size, on the same floor line.
    page.polylines([[P(*p) for p in
                     ((0, 0, H), (0, 0, 0), (W, 0, 0), (W, 0, H))]],
                   RL.INK, W_BOX)
    # Everything that runs back from it, lighter. The tops of the walls are
    # lighter still: drawn heavy they make a second trapezoid the same shape
    # as the ring, and then the eye cannot tell which of the two is the line
    # it is meant to strike.
    page.polylines([[P(*p) for p in pl] for pl in (
        [(0, 0, 0), (0, D, 0), (W, D, 0), (W, 0, 0)],
        [(0, D, 0), (0, D, H)],
        [(W, D, 0), (W, D, H)])], RL.INK, W_EDGE)

    # The plumb PLANE: a sheet of light standing down the middle of the niche,
    # through the whole depth. Dash-dot, the same convention as the plumb line
    # in the two flat views.
    page.polylines([[P(W / 2.0, 0, 0), P(W / 2.0, 0, H), P(W / 2.0, D, H),
                     P(W / 2.0, D, 0), P(W / 2.0, 0, 0)]],
                   RL.INK, W_PLUMB, dash=DASH)

    # THE RING. Up one end wall, across the back, down the other, and it meets
    # itself - one polyline of three segments, which is what assert_ring reads.
    i_ring = len(page.body)
    page.polylines([[P(0, 0, EYE), P(0, D, EYE), P(W, D, EYE),
                     P(W, 0, EYE)]], RL.INK, W_DATUM)

    # The readings, as points rather than as arrows: fifteen on the left end
    # wall, and ONE arrow out to one of them to say what the fifteen are.
    ys = [D - d for d in depths]                      # back of the niche first
    i_dots = len(page.body)
    for z in heights:
        for y in ys:
            page.dot(P(0, y, z), DOT, RL.INK)
    dots = page.body[i_dots:]
    z_ex, y_ex = heights[n_h // 2], ys[n_d // 2]
    page.arrow(P(W / 2.0, y_ex, z_ex), P(0, y_ex, z_ex), RL.INK, W_DIM, HEAD)

    bracket(-WALL_T - TICK * 1.6, P(0, ys[-1], heights[0])[1],
            P(0, ys[-1], heights[-1])[1], f"{n_h}×")
    bracket_along(P(0, ys[-1], 0.0), P(0, ys[0], 0.0), f"{n_d}×")

    # The height line off the finished floor, read in the MOUTH of the niche -
    # the one plane of the room view that is not foreshortened, so the reading
    # is taken where it is honest, at the end of the ring itself.
    dx = W * 0.94
    for z in (0.0, EYE):
        page.line((RX(dx), RY(z)), (RX(W), RY(z)), RL.GREY, W_DIM)
    measure((RX(dx), RY(0.0)), (RX(dx), RY(EYE)))
    page.text((RX(dx) - TICK * 0.7, RY(EYE / 2.0) - SZ * 0.34), f"{EYE:.0f}",
              SZ, anchor="end")

    # ...and the width the whole exercise is looking for.
    room_base = RY(-WALL_T) - SZ * 1.2
    for x in (0.0, W):
        page.line((RX(x), RY(-WALL_T)), (RX(x), room_base), RL.GREY, W_DIM)
    measure((RX(0.0), room_base), (RX(W), room_base))
    page.text((RX(W / 2.0), room_base + SZ * 0.5), f"{W:.0f}", SZ,
              anchor="middle")

    # -- ELEVATION ----------------------------------------------------------
    wall(ox - WALL_T, 0.0, WALL_T, H)
    wall(ox + W, 0.0, WALL_T, H)
    wall(ox - WALL_T, -WALL_T, W + 2 * WALL_T, WALL_T)
    page.polylines([[(ox, H), (ox, 0.0), (ox + W, 0.0), (ox + W, H)]],
                   RL.INK, W_BOX)

    page.line((ox - WALL_T - OVERRUN, EYE), (ox + W + WALL_T + OVERRUN, EYE),
              RL.INK, W_DATUM)
    page.line((ox + W / 2.0, H), (ox + W / 2.0, 0.0), RL.INK, W_PLUMB,
              dash=DASH)
    for z in heights:
        measure((ox + W / 2.0, z), (ox, z))
    bracket(ox - WALL_T - TICK * 1.6, heights[0], heights[-1], f"{n_h}×")

    dx = ox + W * 0.84
    for z in (0.0, EYE):
        page.line((dx - TICK, z), (dx + TICK, z), RL.GREY, W_DIM)
    measure((dx, 0.0), (dx, EYE))
    page.text((dx + TICK * 1.5, EYE / 2.0 - SZ * 0.34), f"{EYE:.0f}", SZ)

    for x in (ox, ox + W):
        page.line((x, -WALL_T), (x, elev_base), RL.GREY, W_DIM)
    measure((ox, elev_base), (ox + W, elev_base))
    page.text((ox + W / 2.0, elev_base + SZ * 0.5), f"{W:.0f}", SZ,
              anchor="middle")

    # -- PLAN, straight under the elevation and on the same verticals -------
    wall(ox - WALL_T, plan_top, W + 2 * WALL_T, WALL_T)
    wall(ox - WALL_T, plan_top - D, WALL_T, D)
    wall(ox + W, plan_top - D, WALL_T, D)
    page.polylines([[(ox, plan_top - D), (ox, plan_top),
                     (ox + W, plan_top), (ox + W, plan_top - D)]],
                   RL.INK, W_BOX)

    page.line((ox + W / 2.0, plan_top),
              (ox + W / 2.0, plan_top - D - OVERRUN), RL.INK, W_PLUMB,
              dash=DASH)
    for d in depths:
        measure((ox + W / 2.0, plan_top - d), (ox, plan_top - d))
    bracket(ox - WALL_T - TICK * 1.6, plan_top - depths[-1],
            plan_top - depths[0], f"{n_d}×")

    # -- read the ink back --------------------------------------------------
    import gen_doc_tables as T
    assert_ring(page.body[i_ring], unP, W, EYE, SZ * 0.05)
    assert_grid_on_wall(page.body[i_wall], dots, n_h, n_d)
    mm = assert_fits_column(page, T.ROOM_FIG_PX)

    svg = os.path.join(out_dir, "maal-rommet.svg")
    png = os.path.join(out_dir, "maal-rommet.png")
    page.write(svg, width)
    RL.to_png(svg, png, width)
    print(f"  rommet  perspektiv + oppriss + plan, {n_h} høyder × {n_d} "
          f"dybder, høyderiss {EYE:.0f} rundt tre vegger, {mm:.0f} mm bred "
          f"-> {png}")
    return png


if __name__ == "__main__":
    import generate_loftbed as _G
    render(_G, os.path.join(ROOT, "docs", "img"), 1600)
