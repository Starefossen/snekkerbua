"""Steg 10 of the HANNA manual: the loose panel, drawn on its own.

Every other step page is a view of the BED with the step's parts picked out in
black. Steg 10 cannot be that page. What is built here - platen, the two
avstivningslekter under it, the two krokplater and the two U-brakettene - is a
680 x 800 sub-assembly inside a bed that is 2 m across, and drawn inside the
frame it is a postage stamp with four badges crowded onto it. The reader gets
no answer to the only questions the step asks: which way up do the lekter go,
where along the plate do the beslag sit, and what holds what.

So this page throws the bed away and draws the panel assembly ALONE, EXPLODED:

  * platen stays where the model has it, drawn heavy and filled white so it is
    a solid plate and not a wireframe;
  * the two lektene drop straight down out of it, so the reader sees they
    stand ON EDGE (48 x 73, the tall way) and how far in from the plate edges
    they sit;
  * krokplatene fall away backwards-and-down, out past the plate's back edge -
    the edge they hang in front of;
  * U-brakettene fall away forwards-and-down, past the front edge - the edge
    that grips the trinnet.

Each loose piece keeps a DASHED INSERTION LINE back to the spot it seats on,
so the explosion is a movement and not a scatter. The lines are drawn first
and the plate is filled white on top of them, which is what makes the plate
read as opaque: a dashed line dives under the plate exactly where the piece
it belongs to disappears under the plate.

Platen and lektene are the model's own solids, projected through the same
hidden-line machinery as every other page - the explosion is p.moved(), a
displaced COPY, so nothing in the model is touched. The steel beslag have no
solid in the model; they are the glyphs from docs/img/beslag, dropped in at
the exploded positions at a size that keeps them reading as hardware.

The fasteners are drawn where they are driven and pointing the way they are
driven - straight down through the plate, in every case in this step - each
with the step's own badge letter and, where one arrow stands for several
screws, its count. Two thumbnails at the top say where the finished unit ends
up: SENGESTILLING (back edge on the bakre benkevange, front edge on trinn 1)
and BORDSTILLING (back edge on bordbærelekta, front edge on trinn 2).

Called from render_lineart.render_all() with exactly the arguments
render_step() takes, so the driver does not have to know this page is special.
"""

import math
import os

# ---------------------------------------------------------------------------
# THE EXPLOSION, IN MODEL MILLIMETRES
# ---------------------------------------------------------------------------
# One vector per loose piece, along the axis it comes off. Everything moves
# DOWN, because everything in this assembly hangs under the plate; the beslag
# also move out past the edge they grip so their dashed line does not have to
# run through the lektene.
# The distances are not free: at this camera the plate's own silhouette is
# already ~380 mm tall on the page, so anything that drops less than that
# lands ON the plate and reads as lying on top of it. The lekter therefore go
# well past it, and the beslag past THEM, sideways along Y as well so they
# come out beyond the very edge each one grips.
DROP_BATTEN = (0.0, 0.0, -1150.0)
DROP_HOOK = (0.0, -900.0, -1500.0)
DROP_U = (0.0, 700.0, -1150.0)

GLYPH_H = 165.0        # drawn height of a beslag glyph, model mm
BRACKET_W = 30.0       # flattstål 30x4, the beslag's width across the plate

# Where the beslag sit along the plate, as X centres. Krokplatene go clear of
# the avstivningslektene (J13c's own note says so); U-brakettene have to land
# within the trinnet's own X span, 835..1155, and equally clear of the lekter.
HOOK_X = (760.0, 1230.0)
U_X = (858.0, 1132.0)
HOOK_HOLE_Y = (12.0, 34.0)     # the two M6 through the krokplate's flange
U_HOLE_Y = (726.0, 746.0)      # the two M6 through the U-brakett's flanges

PAGE_PAD = 90.0        # white around the exploded assembly, model mm
COL_EXTRA = 130.0      # the left column is the inset panel plus this margin
THUMB_FRAC = 0.62      # thumbnail width, of the left column - they are
                       # CONTEXT, so they stay smaller than the fastener panel


# ---------------------------------------------------------------------------
# GEOMETRY HELPERS
# ---------------------------------------------------------------------------
def _hull(pts):
    """Convex hull (monotone chain) - the silhouette of a projected box."""
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


def _corners(extents, off=(0.0, 0.0, 0.0)):
    (x0, x1), (y0, y1), (z0, z1) = extents
    return [(x + off[0], y + off[1], z + off[2])
            for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def _silhouette(view, extents, off=(0.0, 0.0, 0.0)):
    return _hull([view.xy(p) for p in _corners(extents, off)])


def _moved(part, off):
    from build123d import Location
    return part.moved(Location(off))


def _shift(extents, off):
    return tuple((lo + off[k], hi + off[k])
                 for k, (lo, hi) in enumerate(extents))


# ---------------------------------------------------------------------------
# THE EXPLODED ASSEMBLY
# ---------------------------------------------------------------------------
def _draw_solid(page, RL, view, plines, extents, off, width):
    """One projected piece: white silhouette first, then its own line work.

    The fill is what makes the drawing read as an assembly of SOLIDS - a
    dashed insertion line stops at the piece it runs into instead of crossing
    it, and a lekt below the plate does not show through the plate.
    """
    page.poly(_silhouette(view, extents, off), fill="#ffffff", stroke="none",
              width=0)
    page.polylines(plines, RL.INK, width)


def _insertion(page, RL, view, extents, off, ends=2, steel=False):
    """Insertion lines from a displaced piece back to where it seats.

    DASHED for a wooden piece, DOTTED for a piece of steel - the same split
    the step pages use, so a reader who has learnt it on one page has learnt
    it on all of them.

    Drawn from the TOP corners of the piece in its exploded place to the same
    corners in its home place, i.e. along the explosion vector, so the reader
    reads a movement. `ends` picks how many corners carry a line: four for a
    long lekt, one for a small beslag.
    """
    (x0, x1), (y0, y1), (_z0, z1) = extents
    if ends >= 2:
        # Diagonally opposite corners: two lines say "this piece travels" as
        # well as four do, and this page already has twelve of them.
        tops = [(x0, y0, z1), (x1, y1, z1)]
    else:
        tops = [((x0 + x1) / 2, (y0 + y1) / 2, z1)]
    for p in tops:
        a = view.xy((p[0] + off[0], p[1] + off[1], p[2] + off[2]))
        b = view.xy(p)
        page.line(a, b, RL.GREY,
                  RL.T.W_PHANTOM if steel else RL.T.W_LEAD,
                  dash=RL.DASH_INSERT if steel else "20 16")


def _ghost(page, RL, view, xs, ys, z):
    """The outline of a piece that is UNDER the plate, drawn on the plate.

    Thin, grey, dashed: the drawing convention for something you cannot see.
    It is what turns a scatter of drilling marks into two rows on a lekt, and
    it is the only thing on the page that says how far in from the plate's
    edges the lekter and the beslag actually sit.
    """
    ring = [(xs[0], ys[0]), (xs[1], ys[0]), (xs[1], ys[1]), (xs[0], ys[1])]
    pts = [view.xy((x, y, z)) for x, y in ring]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        page.line(a, b, RL.GREY, RL.T.W_LEAD * 0.85, dash="16 12")


def _glyph_box(view, seat, off, gw, gh):
    """The rectangle a beslag glyph is drawn in, on its exploded seat."""
    cx, cy = view.xy((seat[0] + off[0], seat[1] + off[1], seat[2] + off[2]))
    w = GLYPH_H * gw / gh
    return (cx - w / 2, cy - GLYPH_H / 2, w, GLYPH_H)


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
    battens = [p for p in new if "Stiffener Batten" in p.label]

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

    letters = {name: letter for name, _q, _s, letter in fasteners if letter}
    names = [name for name, _q, _s, _l in fasteners]

    def by_prefix(prefix):
        for name in names:
            if name.startswith(prefix):
                return name
        return prefix

    n_wood = by_prefix("Treskrue 5×60")
    n_m6 = by_prefix("Senkhodeskrue M6×30")
    n_hook = by_prefix("Krokplate")
    n_u = by_prefix("U-brakett")

    # The beslag: no solid in the model, so a glyph at the exploded seat.
    # (glyph file, seat point on the plate's underside, explosion vector)
    beslag = []
    for x in HOOK_X:
        beslag.append(dict(name=n_hook, svg="krokplate-30x4.svg",
                           seat=(x, sum(HOOK_HOLE_Y) / 2, panel.extents[2][0]),
                           off=DROP_HOOK, holes=HOOK_HOLE_Y,
                           box3=((x - BRACKET_W / 2, x + BRACKET_W / 2),
                                 (HOOK_HOLE_Y[0] - 12, HOOK_HOLE_Y[1] + 14),
                                 (panel.extents[2][0] - 48,
                                  panel.extents[2][0]))))
    for x in U_X:
        beslag.append(dict(name=n_u, svg="u-brakett-30x4.svg",
                           seat=(x, sum(U_HOLE_Y) / 2, panel.extents[2][0]),
                           off=DROP_U, holes=U_HOLE_Y,
                           box3=((x - BRACKET_W / 2, x + BRACKET_W / 2),
                                 (U_HOLE_Y[0] - 14, panel.extents[1][1]),
                                 (panel.extents[2][0] - 48,
                                  panel.extents[2][0]))))

    # --- the page rectangle -----------------------------------------------
    # Worked out from the exploded assembly's own bounds: the bed is not in
    # this picture, so the shared page box for this camera would leave the
    # drawing adrift in a page-sized field of white.
    art = list(plate_lines)
    for pl in batten_lines:
        art += pl
    ax0, ay0, ax1, ay1 = RL.bounds(art)
    for b in beslag:
        gw, gh = RL.glyph_dims(os.path.join(glyph_dir, b["svg"]))
        gx, gy, gwd, ghd = _glyph_box(view, b["seat"], b["off"], gw, gh)
        ax0, ay0 = min(ax0, gx), min(ay0, gy)
        ax1, ay1 = max(ax1, gx + gwd), max(ay1, gy + ghd)

    # The arrows are sized to the DRAWING, not to the page: the page is wide
    # because it carries a column of panels beside the drawing, and an arrow
    # scaled to that would be longer than the plate is deep. They stand ON the
    # bounds worked out above, so the room they and their badges need has to
    # go back INTO those bounds before the page is cut - every arrow on this
    # page rises out of the plate's top face.
    arrow_len = max(ax1 - ax0, ay1 - ay0) * 0.115
    ay1 += arrow_len + 2.8 * RL.T.BADGE_R
    ay0 -= 2.6 * RL.T.BADGE_R
    ax0 -= 1.6 * RL.T.BADGE_R
    ax1 += 3.2 * RL.T.BADGE_R

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
    for ext in batten_ext:
        _insertion(page, RL, view, ext, DROP_BATTEN, ends=4)
    for b in beslag:
        _insertion(page, RL, view, b["box3"], b["off"], ends=1, steel=True)

    _draw_solid(page, RL, view, plate_lines, panel.extents, (0, 0, 0),
                RL.T.W_NEW)
    for ext, pl in zip(batten_ext, batten_lines):
        _draw_solid(page, RL, view, pl, _shift(ext, DROP_BATTEN), (0, 0, 0),
                    RL.T.W_NEW)
    for b in beslag:
        gw, gh = RL.glyph_dims(os.path.join(glyph_dir, b["svg"]))
        gx, gy, gwd, ghd = _glyph_box(view, b["seat"], b["off"], gw, gh)
        b["glyph_box"] = (gx, gy, gwd, ghd)
        page.embed_svg(os.path.join(glyph_dir, b["svg"]), gx, gy, gwd, ghd)

    # --- what is driven, where, and which way -----------------------------
    # Every fastener in this step goes STRAIGHT DOWN through the plate: the
    # 5x60 into the lekt's top edge, the M6 through the plate into the
    # beslag's flange with the nut underneath.
    top = panel.extents[2][1]
    marks = []
    for i, b_part in enumerate(battens):
        (bx0, bx1), (by0, by1), _bz = b_part.extents
        # The screw pattern itself, drawn on the plate's face: six holes
        # evenly along the lekt under it, which is the answer to "where do I
        # drill" that no arrow can give. The mark then points at ONE of them
        # and says 6x.
        holes = [(by0 + (by1 - by0) * (k + 0.5) / 6) for k in range(6)]
        _ghost(page, RL, view, (bx0, bx1), (by0, by1), top)
        for hy in holes:
            page.circle(view.xy(((bx0 + bx1) / 2, hy, top)), 9.0,
                        stroke=RL.INK, width=RL.T.W_LEAD)
        # The two lekter stand only 178 mm apart in X, which is next to
        # nothing across the page, so their marks are staggered ALONG the
        # lekt - the one axis that has room here - and towards opposite ends,
        # far enough that the two arrows do not stand on each other.
        pick = holes[0] if i == 1 else holes[-1]
        marks.append(dict(
            name=n_wood, per=6, letter=letters.get(n_wood),
            p3=((bx0 + bx1) / 2, pick, top),
            parts=(panel, b_part)))
    for b in beslag:
        _ghost(page, RL, view, b["box3"][0], b["box3"][1], top)
        for hy in b["holes"]:
            page.circle(view.xy((b["seat"][0], hy, top)), 6.5,
                        stroke=RL.INK, width=RL.T.W_LEAD)
        marks.append(dict(
            name=n_m6, per=2, letter=letters.get(n_m6),
            p3=(b["seat"][0], b["seat"][1], top),
            parts=(panel,)))

    dx, dy = view.dir_xy((0, 0, -1))
    nrm = math.hypot(dx, dy) or 1.0
    dx, dy = dx / nrm, dy / nrm
    bx = x0 + (col_w - inset_w) / 2
    box = (bx, y0 + gap, inset_w, inset_h)
    if rows:
        RL.draw_inset(page, box, [], rows, glyph_dir, letters)

    # Dotted, not an arrow: on this page as on every other, a dotted line is a
    # fastener going into its hole and an arrow is a wooden part being brought
    # into place. The captions go through the same placer and the same
    # occupancy field as every other page's - this page has its own geometry,
    # not its own rules - so R5 holds here too: a badge may not land nearer a
    # fastener it does not name than its own.
    import layout
    occ = layout.Occupancy()
    occ.add_box(box, weight=RL.CAP_PANEL)
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

    # The beslag themselves carry a badge each, beside the glyph: they ARE
    # items in the step's table, not just something screws go through.
    for b in beslag:
        gx, gy, gwd, ghd = b["glyph_box"]
        letter = letters.get(b["name"])
        at = (gx + gwd / 2, gy - RL.T.BADGE_R * 1.35)
        if letter:
            # Under the glyph and touching it: R6 holds for every badge on
            # this page too, and here the element is the beslag's own drawing.
            RL.badge(page, at, letter, owner=(b["name"], gx, gy),
                     body=((gx + gwd / 2, gy), (gx + gwd / 2, gy + ghd),
                           gwd / 2))
        marks.append(dict(name=b["name"], per=1, letter=letter,
                          p3=b["seat"], parts=(panel,)))

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
          f"{len(beslag)} beslag / {len(marks)} festepunkt -> {png}")
    return png
