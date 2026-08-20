#!/usr/bin/env python3
"""SENGEN I MÅL, drawn: docs/img/hanna-maal.svg.

ONE picture of the whole bed with a HANDFUL of dimensions on it - the sheet a
flat-pack catalogue puts on the page before the exploded views start, and the
one drawing in this folder whose job is to answer "how big is it and what fits
under it" without being read.

The idiom is borrowed, the strokes are not. Nothing here is traced, lifted or
measured off anybody's artwork; what was taken is a set of RULES about how a
dimension is drawn, and they are written down in Page.dimension() in
tools/render_lineart.py so the rest of the house can draw one the same way.
Same licence the outline figures took when they were drawn in that hand.

WHAT IS ON IT, AND WHY IT IS ONLY SIX THINGS
--------------------------------------------
The whole point of the idiom is SELECTION. A dimension drawing with every
number on it is the cutting list with a picture behind it, and this bed
already has a cutting list. Six survive, and they are the six a person asks
before they own one:

    1990   how wide - and it is the room's number, not the bed's: the bed is
           made to the niche (WALL_SPAN), so this is the one dimension the
           reader may have to change.
     836   how deep.
    2037   how tall.
    1500   WHAT FITS UNDER IT. The number the whole v14 round was about, and
           the reason the thing is a loft bed rather than a bunk.
     700   the DESK. Drawn where it stands, in table mode, because a desk at
           700 is a claim about a mode and not about a bed.
     800   the sleeping surface across. Its length is the 1990 above it, so
           printing it twice would be printing it twice.

Everything else - the five rungs, the 420 seat, the 807 over the upper
mattress, the 3 mm to each wall - is in nokkelmal.md, which is where a table
belongs.

THE BED IS IN TABLE MODE. The panel is the only part of this bed that has two
places to be, and the sheet shows it in the one the reader cannot work out
from the other drawings: up at 700 as a desk, with the two bearers under it.
That is also what the manual's cover shows, so the two front pages agree.

NOTHING ON THE SHEET IS POSITIONED BY HAND
------------------------------------------
Every dimension line stands off the drawing by dim_offset() - as far as it has
to to clear the line work IN THE STRETCH IT SPANS, plus one margin - and every
dimension already drawn goes back into the line work before the next one asks.
So the sheet composes itself, and it re-composes when the bed changes.

THE ASSERTS READ THE INK
------------------------
    assert_dimensions() takes each arrow back OUT of the emitted <path>,
        measures it on the paper, divides by the length one model millimetre
        has along that axis IN THIS CAMERA, and demands that the answer be the
        number printed on it - which in turn has to be the model's own. A
        figure typed by hand, an arrow drawn to the wrong corner or a camera
        that stopped agreeing with itself all die here. It also asks that the
        arrow LIE ALONG ITS AXIS: a height that is not parallel to the
        projected Z is not a height.
    assert_figures_written() re-reads the finished FILE and demands that the
        millimetre figures in it be exactly the six that were asked for -
        no seventh number crept in, none silently lost.

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

# The camera is the cover drawing's, on purpose: the reader meets this picture
# one page after the hero and should not have to re-learn the bed.
AZ, ELEV = 330, 22

# Sizes, all in pens (tools/layout.py). The figure is set BIG - this sheet is
# read at arm's length off a printed page, and a dimension nobody can read is
# a dimension nobody drew.
FIG_SIZE = 1.40         # x S_DIM
MARGIN = 1.55           # x the figure size: air between a dimension and what
#                         it measures, and between one dimension and the next
PAD = 0.90              # x the figure size: white round the whole sheet

# The page the figure is printed on: A4 less 15 mm each side, same as the
# room figure's. See assert_fits_column().
TEXT_MM = 180.0
PX_MM = 25.4 / 96.0


def part(G, label):
    """One part of the bed, by the name the model gave it.

    A dimension is anchored to a PART - the post that is 2037 tall, the
    uprights the ladder gap is between - and never to a coordinate typed in
    here, so a part that moves takes its dimension with it.
    """
    for p in G.parts:
        if p.label == label:
            return p
    raise AssertionError(f"modellen har ingen del som heter «{label}»")


def spec(G):
    """The six dimensions, in the order they are drawn.

    Order is not decoration: each one clears everything already on the sheet,
    so the ones that hug the bed go first and the ones that stand furthest out
    go last. Every number is read off the model - not one is typed.

        p0, p1   the two ends, in model millimetres
        along    the model axis the arrow runs along
        axis     the model axis the witness lines run out along; None for a
                 local dimension drawn on the part itself
        mm       what the model says the span is
    """
    W, D, H = G.WALL_SPAN, G.OVERALL_DEPTH, G.POST_HEIGHT
    y_front, y_back = G.DEPTH_Y1, G.DEPTH_Y0
    # The two front corner posts, on their own centre lines: a height is
    # measured on the thing that is that tall.
    near = part(G, "Corner Post Front Right")
    far = part(G, "Corner Post Front Left")
    x_near = (near.extents[0][0] + near.extents[0][1]) / 2.0
    x_far = (far.extents[0][0] + far.extents[0][1]) / 2.0
    y_post = (near.extents[1][0] + near.extents[1][1]) / 2.0
    panel = G.panel_table.extents
    # The ladder opening: the one stretch of the front with no guard rail in
    # it, so the witness line that carries the platform's front edge up out of
    # the drawing rises through clear air rather than through two boards.
    x_gap = (part(G, "Ladder Upright Left").extents[0][1]
             + part(G, "Ladder Upright Right").extents[0][0]) / 2.0
    return [
        # -- the sleeping surface across. It was drawn ON the platform once,
        #    and a diagonal arrow lying in a field of fourteen parallel slats
        #    is an arrow nobody can see: it goes UP, out over the bed, where
        #    the paper is empty. Same rule as the rest - the witness lines
        #    follow an axis, and here the axis is Z.
        dict(name="soveflate", mm=G.SLAT_LEN, along=(0, 1, 0), axis=(0, 0, 1),
             p0=(x_gap, G.SLAT_Y0, G.SLAT_Z1),
             p1=(x_gap, G.SLAT_Y1, G.SLAT_Z1)),
        # -- how wide, along the floor at the front -------------------------
        dict(name="bredde", mm=W, along=(1, 0, 0), axis=(0, 0, -1),
             p0=(0.0, y_front, 0.0), p1=(float(W), y_front, 0.0)),
        # -- how deep, along the floor at the near end ----------------------
        dict(name="dybde", mm=D, along=(0, 1, 0), axis=(1, 0, 0),
             p0=(float(W), float(y_back), 0.0),
             p1=(float(W), float(y_front), 0.0)),
        # -- how tall, up the near front post -------------------------------
        dict(name="hoyde", mm=H, along=(0, 0, 1), axis=(1, 0, 0),
             p0=(x_near, y_post, 0.0), p1=(x_near, y_post, float(H))),
        # -- the desk. Its witness lines run the length of the bed and out of
        #    the far end, so the figure stands in a column with 1500 and
        #    still points at the plate it belongs to. It goes FIRST of the
        #    two because it is the shorter: the small dimension nests inside
        #    the big one, the way a drawing office stacks them.
        dict(name="pult", mm=G.PANEL_TOP_TABLE, along=(0, 0, 1),
             axis=(-1, 0, 0),
             p0=(panel[0][1], panel[1][1], 0.0),
             p1=(panel[0][1], panel[1][1], float(G.PANEL_TOP_TABLE))),
        # -- what fits under it, up the far front post ----------------------
        dict(name="fri", mm=G.SLAT_Z0, along=(0, 0, 1), axis=(-1, 0, 0),
             p0=(x_far, y_post, 0.0), p1=(x_far, y_post, float(G.SLAT_Z0))),
    ]


# ---------------------------------------------------------------------------
# THE ASSERTS THAT READ THE INK
# ---------------------------------------------------------------------------
def assert_dimensions(page, view, records, size):
    """Every arrow, measured on the paper and put back through the camera."""
    import render_lineart as RL
    eps = size * 0.02
    seen = []
    for rec, sp in records:
        pts = RL.dim_ink(page, rec)
        # Two points if the arrow is drawn whole, four if it was cut for the
        # figure - and nothing else: the ends are pts[0] and pts[-1] either
        # way, and a third shape means the primitive changed under us.
        assert len(pts) in (2, 4), \
            (f"målpila for {sp['name']} kom ut som {len(pts)} punkter, "
             f"ikke 2 eller 4")
        dx = pts[-1][0] - pts[0][0]
        dy = pts[-1][1] - pts[0][1]
        drawn = math.hypot(dx, dy)
        ax, ay = view.dir_xy(sp["along"])
        k = math.hypot(ax, ay)
        assert k > 1e-6, \
            (f"aksen til {sp['name']} står rett inn i kameraet - "
             f"målet har ingen lengde på papiret")
        # ...and it has to LIE along that axis: a height that is not parallel
        # to the projected Z is not a height, however long it is.
        assert abs(dx * ay - dy * ax) / k < size * 0.002, \
            f"målpila for {sp['name']} ligger ikke langs sin egen akse"
        mm = drawn / k
        figure = RL.dim_figure(page, rec)
        m = re.fullmatch(r"(\d+) mm", figure)
        assert m, f"måltallet for {sp['name']} står som «{figure}»"
        printed = float(m.group(1))
        assert abs(printed - sp["mm"]) < 0.5, \
            (f"{sp['name']}: det står {printed:.0f} mm på arket, men "
             f"modellen sier {sp['mm']:.0f}")
        assert abs(mm - printed) < eps / k, \
            (f"{sp['name']}: pila er {mm:.1f} mm lang gjennom kameraet, "
             f"men det står {printed:.0f} mm på den")
        seen.append(figure)
    return seen


def assert_fits_column(page, fig_px):
    """The figure, at the height the manual sets it in, has to come out the
    width of the text column - not wider (the browser would squeeze it) and
    not much narrower (the drawing would be smaller than it needs to be).

    The same contract render_maalfigur keeps with ROOM_FIG_PX, and it is the
    only thing holding the type size on this sheet to a readable number of
    millimetres on paper: the figure is set 180 mm wide, so 48 drawing units
    of type is about 3,5 mm - big enough to read at arm's length, which is
    the whole point of the idiom.
    """
    mm = page.w / page.h * fig_px * PX_MM
    assert TEXT_MM - 1.0 < mm <= TEXT_MM, \
        (f"figuren blir {mm:.2f} mm bred ved MAAL_FIG_PX={fig_px}, men "
         f"satsbredden er {TEXT_MM:.0f} mm - sett MAAL_FIG_PX til "
         f"{int(TEXT_MM / (page.w / page.h) / PX_MM)}")
    return mm


def assert_figures_written(path, wanted):
    """...and the finished FILE carries those figures and no others."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    got = sorted(re.findall(r">(\d+ mm)</text>", raw))
    assert got == sorted(wanted), \
        (f"arket har måltallene {got}, men det ble tegnet {sorted(wanted)}")
    return got


# ---------------------------------------------------------------------------

def render(G, out_dir, width):
    import render_lineart as RL
    RL.use_model(G)

    bed = RL.table_bed(G)
    view = RL.View(RL.camera_direction(AZ, ELEV), bed.bounding_box().center())
    art = RL.project(view, [("all", bed)])["all"]

    size = RL.T.S_DIM * FIG_SIZE
    margin = size * MARGIN
    x0, y0, x1, y1 = RL.bounds(art)
    page = RL.Page(x0, y0, x1, y1)
    page.polylines(art, RL.INK, RL.T.W_HERO)

    # The line work every dimension has to clear, and it GROWS: each arrow,
    # its witness lines and the box its figure sits in go back in before the
    # next one asks how far out it has to stand.
    field = list(art)
    records = []
    for sp in spec(G):
        p0, p1 = view.xy(sp["p0"]), view.xy(sp["p1"])
        label = f"{sp['mm']:.0f} mm"
        axis, off, step = None, 0.0, (0.0, 0.0)
        if sp["axis"] is not None:
            axis = view.dir_xy(sp["axis"])
            off = RL.dim_offset(field, p0, p1, axis, margin, slack=margin)
            an = math.hypot(axis[0], axis[1])
            step = (axis[0] / an * off, axis[1] / an * off)
        # Where the figure sits along its own arrow is asked of the arrow
        # WHERE IT WILL BE, not of the feature it measures.
        a = (p0[0] + step[0], p0[1] + step[1])
        b = (p1[0] + step[0], p1[1] + step[1])
        at = RL.dim_seat(field, a, b, len(label) * size * page.CHAR_W,
                         size * 1.1)
        rec = page.dimension(p0, p1, label, axis=axis, off=off, size=size,
                             at=at)
        assert rec is not None, f"{sp['name']} kom ut med null lengde"
        field += rec["ink"]
        if off:
            field.append([p0, p1])
        records.append((rec, sp))

    figures = assert_dimensions(page, view, records, size)

    # The sheet is as big as what is on it - the art plus every arrow - and
    # not a rectangle chosen in advance.
    bx0, by0, bx1, by1 = RL.bounds(art + [pl for r, _ in records
                                          for pl in r["ink"]])
    pad = size * PAD
    page.x0, page.y0 = bx0 - pad, by0 - pad
    page.x1, page.y1 = bx1 + pad, by1 + pad

    import gen_doc_tables as T
    mm = assert_fits_column(page, T.MAAL_FIG_PX)

    svg = os.path.join(out_dir, "hanna-maal.svg")
    png = os.path.join(out_dir, "hanna-maal.png")
    page.write(svg, width)
    assert_figures_written(svg, figures)
    RL.to_png(svg, png, width)
    print(f"  mål     bordstilling, {len(art)} kanter + {len(records)} mål "
          f"({', '.join(figures)}), {mm:.0f} mm bred  -> {png}")
    return png


if __name__ == "__main__":
    import generate_loftbed as _G
    render(_G, os.path.join(ROOT, "docs", "img"), 1600)
