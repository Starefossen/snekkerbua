"""Steg 10 of the HANNA manual: the loose panel, drawn on its own.

Every other step page is a view of the BED with the step's parts picked out in
black. Steg 10 cannot be that page. What is built here - platen and the four
lektene under it - is a 652 x 798 sub-assembly inside a bed that is 2 m
across, and drawn inside the frame it is a postage stamp with the badges
crowded onto it. The reader gets no answer to the only questions the step
asks: which way up do the lekter go, how far in from the plate's edges do they
sit, and which way do the screws go.

So this page throws the bed away and draws the panel assembly ALONE, EXPLODED:

  * platen stays where the model has it, drawn heavy and filled white so it is
    a solid plate and not a wireframe;
  * all four lektene drop straight down out of it, so the reader sees they
    stand ON EDGE (48 x 73, the tall way) and how far in from the plate edges
    they sit - which after V3 is the dimension the whole mechanism turns on,
    because the two long ones are what find the trinnenden.

There is no steel on this page any more. V3 took all four vinkelbeslag out of
the mechanism; what used to be drawn as glyphs falling away past the plate's
edges is now two lekter with 2 mm of clearance on the trinnenden, and the only
hardware left is eighteen wood screws.

Each loose piece keeps a DASHED INSERTION LINE back to the spot it seats on,
so the explosion is a movement and not a scatter. The lines are drawn first
and the plate is filled white on top of them, which is what makes the plate
read as opaque: a dashed line dives under the plate exactly where the piece
it belongs to disappears under the plate.

Platen and lektene are the model's own solids, projected through the same
hidden-line machinery as every other page - the explosion is p.moved(), a
displaced COPY, so nothing in the model is touched.

THE SCREWS GO UP. That is the point of the step and it is why the drilling
pattern is drawn on the lekt's UNDERSIDE, in its exploded place, and not on
the plate: the counterbores are read straight off the model's own fastener
anchors, and every dotted line rises out of a hole towards the plate. No
FASTENER is drawn on the plate's top face, because after V3 there is nothing
there.

What IS on the plate's top face is the only two things a reader with the four
lekter in one hand and the plate in the other still has to be told. FOUR
FOOTPRINTS, each a dashed grey ring on the faintest of tints, say where the
lekter go and how far in from the plate's edges they sit; they are pulled a
few millimetres in off any plate edge they run out to, because a footprint
drawn underneath the plate's own heavy outline is a footprint the reader never
sees - which is exactly how two of the four used to be lost. And TWO WORDS,
VEGG and FORAN, say which way round the plate goes, because the assembly is
asymmetric in Y and the drawing of it is a rectangle.

Two thumbnails at the top say where the finished unit ends up: SENGESTILLING
(back edge on the bakre benkevange, front edge on trinn 1) and BORDSTILLING
(back edge on bordbærelekta, front edge on trinn 2).

Called from render_lineart.render_all() with exactly the arguments
render_step() takes, so the driver does not have to know this page is special.
"""

import math
import os

# ---------------------------------------------------------------------------
# THE EXPLOSION, IN MODEL MILLIMETRES
# ---------------------------------------------------------------------------
# One vector, along the axis every loose piece comes off: DOWN, because
# everything in this assembly hangs under the plate.
# The distance is not free: at this camera the plate's own silhouette is
# already ~380 mm tall on the page, so anything that drops less than that
# lands ON the plate and reads as lying on top of it.
DROP_BATTEN = (0.0, 0.0, -1150.0)

PAGE_PAD = 90.0        # white around the exploded assembly, model mm
COL_EXTRA = 130.0      # the left column is the inset panel plus this margin
THUMB_FRAC = 0.62      # thumbnail width, of the left column - they are
                       # CONTEXT, so they stay smaller than the fastener panel

# The footprints on the plate, in model millimetres. GHOST_EDGE is how far a
# ghost is pulled in off a plate edge it would otherwise be drawn ON; GHOST_GAP
# is the hair it is pulled in off everything else, so that two lekter which
# butt each other still read as two rectangles. See _ring().
GHOST_EDGE = 15.0
GHOST_GAP = 5.0
# A whisper of grey inside the dashed ring. A footprint is an AREA - this much
# of the plate is covered by wood you cannot see - and an area is what the
# reader has to be able to count four of. It is deliberately far too light to
# compete with any line on the page: the ring is still what carries the shape.
GHOST_TINT = "#e0e0e0"


# ---------------------------------------------------------------------------
# GEOMETRY HELPERS
# ---------------------------------------------------------------------------
def _hull(pts):
    """Convex hull (monotone chain) of a set of projected points."""
    pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in pts))
    if len(pts) <= 2:
        return pts

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by) = out[-2], out[-1]
                if (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax) <= 0:
                    out.pop()
                else:
                    break
            out.append(p)
        return out

    return half(pts)[:-1] + half(reversed(pts))[:-1]


def _silhouette(plines):
    """The outline to knock white, taken from the piece's OWN LINE WORK.

    It used to be the hull of the eight projected corners of the piece's
    `extents`, and for a box that is exactly right, because the box IS the
    piece. V4 put the first non-box in the model: the two front wings are
    planed away underneath, 73 mm at the root down to 27 at the tip, and their
    `extents` is deliberately still the box they were sawn out of - every
    clearance assert in the model reads it and is meant to stay conservative.
    Filled from that box, a wing knocks out half again its own area: it eats
    the dashed lines running past under it, and on the page it reads as the
    block it is not.

    Every piece on this page is CONVEX and the hidden-line run hands back all
    of a convex body's visible edges, so the hull of the projected line work
    IS the silhouette. For a box that is the same answer as before; for a
    wedge it is the triangle.
    """
    return _hull([p for pl in plines for p in pl])


def _moved(part, off):
    from build123d import Location
    return part.moved(Location(off))


# ---------------------------------------------------------------------------
# THE EXPLODED ASSEMBLY
# ---------------------------------------------------------------------------
def _draw_solid(page, RL, plines, width):
    """One projected piece: white silhouette first, then its own line work.

    The fill is what makes the drawing read as an assembly of SOLIDS - a
    dashed insertion line stops at the piece it runs into instead of crossing
    it, and a lekt below the plate does not show through the plate.
    """
    page.poly(_silhouette(plines), fill="#ffffff", stroke="none", width=0)
    page.polylines(plines, RL.INK, width)


def _insertion(page, RL, view, extents, off, ends=2, steel=False):
    """Insertion lines from a displaced piece back to where it seats.

    DASHED for a wooden piece, DOTTED for a piece of steel - the same split
    the step pages use, so a reader who has learnt it on one page has learnt
    it on all of them.

    Drawn from the TOP corners of the piece in its exploded place to the same
    corners in its home place, i.e. along the explosion vector, so the reader
    reads a movement. `ends` picks how many corners carry a line.

    Returns the segments it drew, as polylines, so the page can tell a later
    annotation what paper is already spoken for.
    """
    (x0, x1), (y0, y1), (_z0, z1) = extents
    if ends >= 2:
        # Diagonally opposite corners: two lines say "this piece travels" as
        # well as four do, and this page already has twelve of them.
        tops = [(x0, y0, z1), (x1, y1, z1)]
    else:
        tops = [((x0 + x1) / 2, (y0 + y1) / 2, z1)]
    drawn = []
    for p in tops:
        a = view.xy((p[0] + off[0], p[1] + off[1], p[2] + off[2]))
        b = view.xy(p)
        page.line(a, b, RL.GREY,
                  RL.T.W_PHANTOM if steel else RL.T.W_LEAD,
                  dash=RL.DASH_INSERT if steel else "20 16")
        drawn.append([a, b])
    return drawn


def _ring(xs, ys, panel_xy):
    """The four corners a footprint is DRAWN as, in model X/Y.

    Not the footprint itself, and on purpose. All four lekter run right out to
    the plate's own front edge, and the two wings run out to its side edges as
    well - so a ring drawn on the true footprint lays its outer side down
    underneath the plate's heavy black outline, where for the reader it is
    simply not there. That is why this page showed two long footprints and, at
    best, a hint of a third: the two wings were 48 mm deep with their long
    side swallowed by the silhouette.

    Every side is therefore pulled in - GHOST_EDGE off a plate edge, which is
    enough to clear the black line running along it, and GHOST_GAP off
    everything else, so that a wing and the guide lekt it butts still read as
    two rectangles and not as one L. The footprint stops being dimensionally
    exact and starts being countable, which is the job it is on the page to
    do; the dimensions themselves are the cut list's and the spec's.
    """
    out = []
    for (lo, hi), (plo, phi) in zip((xs, ys), panel_xy):
        lo += GHOST_EDGE if abs(lo - plo) < 0.5 else GHOST_GAP
        hi -= GHOST_EDGE if abs(hi - phi) < 0.5 else GHOST_GAP
        out.append((lo, hi))
    (x0, x1), (y0, y1) = out
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _ghost(page, RL, view, xs, ys, z, panel_xy):
    """The outline of a piece that is UNDER the plate, drawn on the plate.

    Thin, grey, dashed on the faintest of tints: the drawing convention for
    something you cannot see, plus the one thing that convention was missing
    here. It is what turns a scatter of drilling marks into two rows on a
    lekt, and it is the only thing on the page that says how far in from the
    plate's edges the lekter actually sit.
    """
    pts = [view.xy((x, y, z)) for x, y in _ring(xs, ys, panel_xy)]
    page.poly(pts, fill=GHOST_TINT, stroke="none", width=0)
    for a, b in zip(pts, pts[1:] + pts[:1]):
        page.line(a, b, RL.GREY, RL.T.W_LEAD * 0.85, dash="16 12")


# ---------------------------------------------------------------------------
# WHICH WAY ROUND THE PLATE GOES
# ---------------------------------------------------------------------------
# Everything this step builds is asymmetric in Y: the two wings sit on the
# FRONT edge and nowhere else, and the guide lekter stop 48 mm short of the
# wall edge. Turn the plate end for end and none of it fits. But what the page
# draws is a rectangle with some ghosts on it, and a rectangle has no front -
# so up to now the reader had no way at all of telling one long edge from the
# other. Two words fix it, one per long edge, in the drawing's own type.
#
# (word, which end of the panel's Y extent, which way it faces)
EDGE_WORDS = (("VEGG", 0, -1.0), ("FORAN", 1, 1.0))


def _edge_word_plan(RL, view, panel):
    """Where the two orientation words MAY stand, before the page exists.

    A chicken and egg: the page rectangle has to be big enough to hold
    whichever position wins, so every candidate must be known before the page
    is cut - but the choice itself cannot be made until the rest of the
    drawing is down and there is something to dodge. So the plan is drawn up
    here, folded into the page bounds by the caller, and spent later.

    Each candidate carries the point on the plate edge it is a label FOR, so
    that a word which has stepped sideways to find white paper still leads
    back to the edge under itself rather than to the middle of it.
    """
    (px0, px1), ys, (_z0, z1) = panel.extents
    size = RL.T.S_DIM
    step = (px1 - px0) * 0.17
    plan = []
    for word, i, sign in EDGE_WORDS:
        dx, dy = view.dir_xy((0.0, sign, 0.0))
        n = math.hypot(dx, dy) or 1.0
        ux, uy = dx / n, dy / n
        w, h = size * 0.74 * len(word), size * 1.3
        # How far out the word's own box reaches along the direction it
        # stands off in. The candidates are measured from there rather than
        # from the edge, so that the leader is a LEADER at every one of them
        # and not a tick swallowed by the word it is supposed to lead to: the
        # word box is five characters wide and the direction is diagonal, so
        # measuring to the centre buys nothing at all at the near candidates.
        pad = RL.T.BADGE_R * 0.35
        reach = min((w / 2 + pad) / abs(ux) if abs(ux) > 1e-9 else 1e9,
                    (h / 2 + pad) / abs(uy) if abs(uy) > 1e-9 else 1e9)
        mid = view.xy(((px0 + px1) / 2, ys[i], z1))
        cands = []
        # Straight out from the middle of the edge first, and only then
        # sideways: the order is the placer's tie-break, so a page with room
        # everywhere always puts the word where it belongs.
        for side in (0.0, 1.0, -1.0):
            root = view.xy(((px0 + px1) / 2 + side * step, ys[i], z1))
            for k in (1.8, 2.7, 3.7, 1.0):
                d = reach + RL.T.BADGE_R * k
                cands.append(((root[0] + ux * d, root[1] + uy * d), root))
        plan.append(dict(word=word, mid=mid, u=(ux, uy), foot=(w, h),
                         size=size, reach=reach, cands=cands))
    return plan


def _draw_edge_words(page, RL, layout, plan, field):
    """Place and draw the two words. Returns the paper they took.

    `field` is an occupancy holding the line work they have to stay off; the
    scoring is by CLEARANCE rather than by cost, because everything on this
    part of the page is a straight two-point polyline and a box that counts
    vertices would see nothing at all in the middle of a 700 mm edge.
    """
    boxes = []
    for pl in plan:
        w, h = pl["foot"]
        cap = h * 1.15
        centres = [c for c, _root in pl["cands"]]

        def clear(c, field=field, cap=cap):
            return (cap - field.clearance(c, cap)) * 0.30

        c = layout.place(centres, (w, h), field, tether=pl["mid"], pull=0.05,
                         extra=clear)
        root = next(r for q, r in pl["cands"] if q == c)
        ux, uy = pl["u"]
        # The leader stops on the near face of the word's own box, so the
        # word is never struck through by its own tether.
        reach = pl["reach"]
        page.line(root, (c[0] - ux * reach, c[1] - uy * reach), RL.GREY,
                  RL.T.W_LEAD)
        page.text((c[0], c[1] - pl["size"] * 0.36), pl["word"], pl["size"],
                  anchor="middle", weight="bold")
        boxes.append((c[0] - w / 2, c[1] - h / 2, w, h))
    return boxes


# ---------------------------------------------------------------------------
# THE THUMBNAILS
# ---------------------------------------------------------------------------
def _thumbnail(page, RL, G, view, box, panel, battens, title):
    """The finished bed with the panel in one of its two positions.

    Frame grey and thin, the panel unit heavy black, exactly the weight the
    step pages use. The frame goes through one hidden-line run of its own and
    the panel through another, so the panel is drawn whole even where the
    ladder passes in front of it - the assembly-manual convention.
    """
    x, y, w, h = box
    frame = RL.project(view, [("f", RL.comp(list(G.parts)))])["f"]
    unit = RL.project(view, [("p", RL.comp([panel] + list(battens)))])["p"]
    bx0, by0, bx1, by1 = RL.bounds(frame + unit)
    k = min(w / max(bx1 - bx0, 1e-6), h / max(by1 - by0, 1e-6))
    cx, cy = x + w / 2, y + h / 2

    def fit(plines):
        return [[(cx + (p[0] - (bx0 + bx1) / 2) * k,
                  cy + (p[1] - (by0 + by1) / 2) * k) for p in pl]
                for pl in plines]

    page.polylines(fit(frame), RL.GREY, RL.T.W_PRIOR / k * 1.15)
    page.polylines(fit(unit), RL.INK, RL.T.W_NEW / k * 0.85)
    page.text((cx, y - RL.T.BADGE_R * 1.5), title, RL.T.BADGE_R * 1.05,
              anchor="middle", weight="bold")


# ---------------------------------------------------------------------------
# THE PAGE
# ---------------------------------------------------------------------------
def render(G, view, st, uni, placed, out_dir, width, page_box, glyph_dir,
           fasteners, families, centre):
    """Writes <out_dir>/steg-10.svg and steg-10.png. Returns the png path.

    Same signature as render_lineart.render_step(), so the driver does not
    have to special-case the call. Two of the arguments are deliberately not
    used: `placed`, because nothing standing from an earlier step is in this
    picture at all, and `page_box`, because the shared rectangle for this
    camera is the size of the whole BED - the page here is cut from the
    exploded assembly's own bounds instead. `view` is replaced for the same
    reason: it looks at the bed's centre, and this drawing wants the panel's.
    """
    import render_lineart as RL

    n = st["n"]
    # The step's own parts, out of the same universe every other page reads.
    new = [uni[label] for label in st["highlight"]]
    panel = next(p for p in new if p.label.startswith("Movable Panel"))
    # V2/V3: four lekter - two along Y that both stiffen the plate and guide
    # it past the trinnenden, two across X under the front corners - and all
    # four travel with the plate, so all four are in this picture and all four
    # get their screw pattern drawn.
    battens = [p for p in new if "Batten" in p.label]

    # A camera of this page's own: the step's angles, but looking at the
    # panel instead of at the bed, and lifted a little so the reader sees
    # DOWN onto the plate and along the lektene under it.
    az, elev = st["camera"][0], st["camera"][1]
    pc = tuple((lo + hi) / 2 for lo, hi in panel.extents)
    view = RL.View(RL.camera_direction(az, max(elev, 34)), pc)

    # --- the pieces, in their exploded places -----------------------------
    plate_lines = RL.project(view, [("p", RL.comp([panel]))])["p"]
    batten_lines, batten_ext = [], []
    for b in battens:
        moved = _moved(b, DROP_BATTEN)
        batten_lines.append(RL.project(view, [("b", RL.comp([moved]))])["b"])
        batten_ext.append(b.extents)
    word_plan = _edge_word_plan(RL, view, panel)

    letters = {name: letter for name, _q, _s, letter in fasteners if letter}
    # The panel page follows the same rule as every other page: it codes its
    # fasteners only where the step says the shapes need it. It draws no screw
    # bodies of its own - the drilling pattern and a dotted line into each
    # hole is what it draws - so in practice this decides its panel rows.
    codes = RL.page_fill_codes(st, letters)
    names = [name for name, _q, _s, _l in fasteners]

    def by_prefix(prefix):
        for name in names:
            if name.startswith(prefix):
                return name
        return prefix

    n_wood = by_prefix("Treskrue 5×40")

    # V3: THE HOLES ARE READ OFF THE MODEL, NOT OFF THIS FILE. Every screw in
    # this step is a solid with an anchor, and the anchor is the bottom of its
    # counterbore - so the pattern drawn on the lekt's underside is the
    # pattern the model drilled, and this page cannot invent one.
    holes_by_batten = {}
    for f in G.FASTENER_SPECS:
        if not f["jid"].startswith("J13") or f.get("solid") is None:
            continue
        holes_by_batten.setdefault(f["through"].label, []).append(
            (f["anchor"][0], f["anchor"][1]))
    for key in holes_by_batten:
        holes_by_batten[key].sort()
    # --- the page rectangle -----------------------------------------------
    # Worked out from the exploded assembly's own bounds: the bed is not in
    # this picture, so the shared page box for this camera would leave the
    # drawing adrift in a page-sized field of white.
    art = list(plate_lines)
    for pl in batten_lines:
        art += pl
    ax0, ay0, ax1, ay1 = RL.bounds(art)

    # The arrows are sized to the DRAWING, not to the page: the page is wide
    # because it carries a column of panels beside the drawing, and an arrow
    # scaled to that would be longer than the plate is deep. They stand ON the
    # bounds worked out above, so the room they and their badges need has to
    # go back INTO those bounds before the page is cut - and after V3 every
    # arrow on this page comes UP from under the lekt, so the room is at the
    # bottom.
    arrow_len = max(ax1 - ax0, ay1 - ay0) * 0.115
    ay0 -= arrow_len + 2.8 * RL.T.BADGE_R
    ay1 += 2.6 * RL.T.BADGE_R
    ax0 -= 1.6 * RL.T.BADGE_R
    ax1 += 3.2 * RL.T.BADGE_R

    # The two edge words stand OUTSIDE the plate, on the axis they name, so
    # every position one of them might take has to be inside the page before
    # the page is cut. All of them go in, not just the preferred one: which
    # candidate wins is not known until the drawing is down, and a page that
    # changed size with that choice would be a page whose scale depended on
    # how crowded it turned out to be.
    for wp in word_plan:
        w_w, w_h = wp["foot"]
        for c, _root in wp["cands"]:
            ax0 = min(ax0, c[0] - w_w / 2)
            ax1 = max(ax1, c[0] + w_w / 2)
            ay0 = min(ay0, c[1] - w_h / 2)
            ay1 = max(ay1, c[1] + w_h / 2)

    # The left column is exactly as wide as the inset panel, whose width is a
    # fixed fraction of the PAGE - so the page width is what falls out of
    # "the drawing, plus a column the inset fits in".
    art_w = ax1 - ax0 + 2 * PAGE_PAD
    page_w = (art_w + COL_EXTRA) / (1.0 - RL.INSET_W_FRAC)
    col_w = page_w - art_w
    x0 = ax0 - PAGE_PAD - col_w
    x1 = x0 + page_w

    rows = fasteners[:4]
    tmp = RL.Page(x0, 0.0, x1, 1.0)
    inset_w, inset_h = RL.inset_layout(tmp, 0, len(rows))[:2]
    cell_w = (col_w - COL_EXTRA) * THUMB_FRAC
    cell_h = cell_w / 1.25
    gap = 2.6 * RL.T.BADGE_R
    left_h = 2 * (cell_h + gap) + inset_h + 3 * gap
    page_h = max((ay1 - ay0) + 2 * PAGE_PAD, left_h)
    y0 = ay0 - PAGE_PAD - (page_h - ((ay1 - ay0) + 2 * PAGE_PAD)) * 0.5
    y1 = y0 + page_h
    page = RL.Page(x0, y0, x1, y1)

    # --- the exploded assembly --------------------------------------------
    # Dashed first, solids on top: the plate's white fill is what swallows the
    # line where the piece disappears under it.
    insert_lines = []
    for ext in batten_ext:
        insert_lines += _insertion(page, RL, view, ext, DROP_BATTEN, ends=4)

    _draw_solid(page, RL, plate_lines, RL.T.W_NEW)
    for pl in batten_lines:
        _draw_solid(page, RL, pl, RL.T.W_NEW)

    # --- what is driven, where, and which way -----------------------------
    # V3: every fastener in this step goes STRAIGHT UP, out of a counterbore
    # in the lekt's underside and 13 mm into the plate. So the drilling
    # pattern belongs on the LEKT, in its exploded place, and the plate's top
    # face stays empty - which is the whole point of the step.
    top = panel.extents[2][1]
    marks = []
    for i, b_part in enumerate(battens):
        (bx0, bx1), (by0, by1), (bz0, _bz1) = b_part.extents
        holes = holes_by_batten.get(b_part.label, [])
        under = bz0 + DROP_BATTEN[2]
        # The ghost outline stays on the PLATE - it is what says how far in
        # from the plate's edges the lekt sits, and after V3 that number
        # (116 mm to the side edge) is the mechanism.
        _ghost(page, RL, view, (bx0, bx1), (by0, by1), top,
               panel.extents[:2])
        for hx, hy in holes:
            # DASHED, because the face they are in is the one turned away from
            # this camera: the counterbores are drilled in the lekt's
            # UNDERSIDE, and this page keeps the convention that a line you
            # cannot see is dashed.
            page.circle(view.xy((hx, hy, under)), 9.0,
                        stroke=RL.INK, width=RL.T.W_LEAD, dash="9 7")
        # The two long lekter stand 372 mm apart in X, but at this camera that
        # is still little across the page, so their marks are staggered ALONG
        # the lekt - the one axis that has room here - and towards opposite
        # ends, far enough that the two arrows do not stand on each other.
        if not holes:
            continue
        pick = holes[0] if i % 2 else holes[-1]
        marks.append(dict(
            name=n_wood, per=len(holes), letter=letters.get(n_wood),
            p3=(pick[0], pick[1], under),
            parts=(panel, b_part)))

    dx, dy = view.dir_xy((0, 0, 1))
    nrm = math.hypot(dx, dy) or 1.0
    dx, dy = dx / nrm, dy / nrm
    bx = x0 + (col_w - inset_w) / 2
    box = (bx, y0 + gap, inset_w, inset_h)
    if rows:
        RL.draw_inset(page, box, [], rows, glyph_dir, codes)

    import layout

    # --- which edge is which ----------------------------------------------
    # Placed against a field of its own, holding the line work the words have
    # to keep off: the plate, the four lekter and the dashed insertion lines
    # that come down between them. It is not the badges' field - a word on the
    # plate's edge and a badge on a screw two feet below it are never in each
    # other's way - but the boxes the words end up taking do go into that
    # field afterwards, because R5's placer is entitled to know about every
    # last thing already on the paper.
    field = layout.Occupancy()
    field.add_lines(plate_lines)
    for pl in batten_lines:
        field.add_lines(pl)
    field.add_lines(insert_lines, weight=0.6, tag="ghost")
    field.add_box(box, weight=RL.CAP_PANEL)
    word_boxes = _draw_edge_words(page, RL, layout, word_plan, field)

    # Dotted, not an arrow: on this page as on every other, a dotted line is a
    # fastener going into its hole and an arrow is a wooden part being brought
    # into place. The captions go through the same placer and the same
    # occupancy field as every other page's - this page has its own geometry,
    # not its own rules - so R5 holds here too: a badge may not land nearer a
    # fastener it does not name than its own.
    occ = layout.Occupancy()
    occ.add_box(box, weight=RL.CAP_PANEL)
    for rect in word_boxes:
        occ.add_box(rect, weight=RL.CAP_PANEL)
    placed_marks = []
    for m in sorted(marks, key=lambda q: (-q["p3"][1], q["p3"][0])):
        p2 = view.xy(m["p3"])
        tail = (p2[0] - dx * arrow_len, p2[1] - dy * arrow_len)
        page.line(tail, p2, RL.GREY, RL.T.W_PHANTOM, dash=RL.DASH_INSERT)
        page.dot(p2, 6.5, colour=RL.INK)
        owner = (m["name"], round(p2[0], 3), round(p2[1], 3))
        m["p2"] = p2
        occ.add_points([p2, tail], radius=RL.T.BADGE_R + 10,
                       weight=RL.CAP_MARK, owner=owner, tag="mark")
        placed_marks.append((tail, m, owner))
    for tail, m, owner in placed_marks:
        # This page draws no screw bodies - it draws the drilling pattern on
        # the plate and a dotted line into each hole - so the element the
        # badge names is that LINE, from where the fastener comes in to the
        # hole it ends in. R6 is satisfied the flag way: the badge sits on the
        # line's near end, and the line is its own leader to the hole.
        RL.mark_label(page, tail, (dx, dy), m["letter"], occ, owner,
                      body=(tail, m["p2"], RL.T.ENTRY_R))
    RL.assert_badges_anchored(page)
    RL.assert_marks_own_element(page, occ)

    # --- where it lands ----------------------------------------------------
    thumb_view = RL.View(RL.camera_direction(az, elev), centre)
    tx = x0 + (col_w - cell_w) / 2
    ty = y1 - gap - cell_h
    _thumbnail(page, RL, G, thumb_view, (tx, ty, cell_w, cell_h),
               G.panel_bed, G.battens_bed, "SENGESTILLING")
    ty -= cell_h + 2.2 * gap
    _thumbnail(page, RL, G, thumb_view, (tx, ty, cell_w, cell_h),
               G.panel_table, G.battens_table, "BORDSTILLING")

    RL.check_coverage(st, marks, fasteners, families)

    svg = os.path.join(out_dir, f"steg-{n:02d}.svg")
    png = os.path.join(out_dir, f"steg-{n:02d}.png")
    page.write(svg, width)
    RL.to_png(svg, png, width)
    for f_name, *_rest in fasteners:
        RL.ALL_FASTENERS.setdefault(f_name, n)
    if letters:
        # The panel page carries badge letters like any other, so it belongs
        # in the two contrast proofs on the same terms.
        RL.PAGE_SCALES[n] = width / page.w
        RL.PAGE_FASTENERS[n] = list(fasteners)
        if page.fill_spans:
            RL.PAGE_FILL_SCALES[n] = width / page.w
    print(f"  steg {n:2d}  eksplodert plate: {len(plate_lines)} + "
          f"{sum(len(p) for p in batten_lines)} kanter / "
          f"{sum(len(v) for v in holes_by_batten.values())} kontraborhull / "
          f"{len(marks)} festepunkt -> {png}")
    return png
