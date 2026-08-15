#!/usr/bin/env python3
"""MÅL ROMMET FØRST, drawn: docs/img/maal-rommet.svg.

The one figure in the manual with no bed in it. The pre-step tells the reader
to strike a height line round the niche, stand a plumb line down the middle of
it and read each end wall on a grid of so many heights by so many depths; this
draws exactly that, and nothing else.

TWO VIEWS, BECAUSE A GRID IS TWO THINGS
---------------------------------------
The heights and the depths cannot both be shown in one flat view, and putting
the niche in perspective to get them both puts the fifteen readings on top of
one another. So the figure is the pair a drawing office would draw:

    the ELEVATION - the niche from the room. The height line runs level right
        across it and out past both end walls, the plumb line stands down the
        middle, and the arrows go out to the left end wall at each HEIGHT.
    the PLAN - the same niche from above, the back wall at the top. Same plumb
        line, same left end wall, and the arrows go out to it at each DEPTH.

Both are drawn at the same scale, so the two 1990s are the same 1990.

THE NUMBERS
-----------
WALL_SPAN, MEASURE_DATUM_Z, MEASURE_GRID, OVERALL_DEPTH and POST_HEIGHT out of
generate_loftbed.py. The niche is drawn as high as the bed is - the model has
no ceiling and this figure does not invent one - and the grid spans the bed's
own height and depth, because that is the part of the wall the bed touches.

The three numbers the model has no opinion about are named at the top of the
file: how thick the surrounding building is drawn, how far apart the two views
stand, and how far the height line runs past the niche. The PEN is this
figure's own as well - see the block in render() and the reason it is not the
bed's.

There are no words in the figure. The words are on the page it sits on: the
only type on it is the two millimetre readings and the two grid counts.

Entry point:
    render(G, out_dir, width) -> path of the PNG
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The three things the model has no opinion about: how thick the surrounding
# building is DRAWN, how far apart the two views stand, and how far the height
# line runs past the niche it is struck round.
WALL_T = 120.0
GAP = 640.0
OVERRUN = 90.0


def render(G, out_dir, width):
    import render_lineart as RL
    RL.use_model(G)

    W = float(G.WALL_SPAN)
    D = float(G.OVERALL_DEPTH)
    H = float(G.POST_HEIGHT)
    EYE = float(G.MEASURE_DATUM_Z)
    n_h, n_d = G.MEASURE_GRID

    heights = [H * (i + 0.5) / n_h for i in range(n_h)]
    depths = [D * (j + 0.5) / n_d for j in range(n_d)]

    ox = W + GAP                      # the plan's left end wall
    plan_top = EYE + D / 2.0          # ...and its back wall, centred on the
                                      # height line so the pair sits square

    # THE PEN IS THIS FIGURE'S OWN, not the bed's. render_lineart sets its
    # theme from the FINISHED BED's diagonal, which is right for a page that
    # draws the bed and wrong for one that draws a room twice as wide and
    # prints it at half the size - the numbers came out under a millimetre.
    # So every size here is a fixed fraction of the drawing's own width, the
    # way tools/render_cutpage.py does it: the figure is printed about 160 mm
    # wide, and SZ is the ~2,5 mm of type that has to be readable there.
    SPAN = ox + W + WALL_T
    SZ = SPAN * 0.0160
    W_BOX = SPAN * 0.0020
    W_RULE = SPAN * 0.0009
    W_HATCH = SPAN * 0.0007
    W_DATUM = SPAN * 0.0026     # the struck line - the one thing the page is
    W_PLUMB = SPAN * 0.0013     # about; the plumb line is only its partner
    W_DIM = SPAN * 0.0010
    TICK = SZ * 0.50
    HEAD = SZ * 0.70
    HATCH = SZ * 0.90

    pad = SZ * 1.1
    x0 = -WALL_T - SZ * 1.9 - pad
    x1 = ox + W + WALL_T + pad
    y0 = -WALL_T - SZ * 2.2 - pad
    y1 = H + pad
    page = RL.Page(x0, y0, x1, y1)

    def wall(x, y, w, h):
        """A piece of the building: hatched, with a light outline."""
        page.hatch(x, y, w, h, HATCH, RL.GREY, W_HATCH)
        page.rect(x, y, w, h, fill="none", stroke=RL.GREY, width=W_RULE)

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

    # -- ELEVATION ----------------------------------------------------------
    wall(-WALL_T, 0.0, WALL_T, H)
    wall(W, 0.0, WALL_T, H)
    wall(-WALL_T, -WALL_T, W + 2 * WALL_T, WALL_T)
    page.polylines([[(0.0, H), (0.0, 0.0), (W, 0.0), (W, H)]], RL.INK, W_BOX)

    page.line((-WALL_T - OVERRUN, EYE), (W + WALL_T + OVERRUN, EYE),
              RL.INK, W_DATUM)
    page.line((W / 2.0, H), (W / 2.0, 0.0), RL.INK, W_PLUMB,
              dash="30 10 6 10")
    for z in heights:
        measure((W / 2.0, z), (0.0, z))
    bracket(-WALL_T - TICK * 1.6, heights[0], heights[-1], f"{n_h}×")

    # The height line off the finished floor, on the clear right-hand half.
    dx = W * 0.84
    for z in (0.0, EYE):
        page.line((dx - TICK, z), (dx + TICK, z), RL.GREY, W_DIM)
    measure((dx, 0.0), (dx, EYE))
    page.text((dx + TICK * 1.5, EYE / 2.0 - SZ * 0.34), f"{EYE:.0f}", SZ)

    # ...and the width the whole exercise is looking for.
    base = -WALL_T - SZ * 1.2
    for x in (0.0, W):
        page.line((x, -WALL_T), (x, base), RL.GREY, W_DIM)
    measure((0.0, base), (W, base))
    page.text((W / 2.0, base + SZ * 0.5), f"{W:.0f}", SZ, anchor="middle")

    # -- PLAN ---------------------------------------------------------------
    wall(ox - WALL_T, plan_top, W + 2 * WALL_T, WALL_T)
    wall(ox - WALL_T, plan_top - D, WALL_T, D)
    wall(ox + W, plan_top - D, WALL_T, D)
    page.polylines([[(ox, plan_top - D), (ox, plan_top),
                     (ox + W, plan_top), (ox + W, plan_top - D)]],
                   RL.INK, W_BOX)

    page.line((ox + W / 2.0, plan_top),
              (ox + W / 2.0, plan_top - D - OVERRUN), RL.INK, W_PLUMB,
              dash="30 10 6 10")
    for d in depths:
        measure((ox + W / 2.0, plan_top - d), (ox, plan_top - d))
    bracket(ox - WALL_T - TICK * 1.6, plan_top - depths[-1],
            plan_top - depths[0], f"{n_d}×")

    svg = os.path.join(out_dir, "maal-rommet.svg")
    png = os.path.join(out_dir, "maal-rommet.png")
    page.write(svg, width)
    RL.to_png(svg, png, width)
    print(f"  rommet  oppriss + plan, {n_h} høyder × {n_d} dybder, høyderiss "
          f"{EYE:.0f}  -> {png}")
    return png


if __name__ == "__main__":
    import generate_loftbed as _G
    render(_G, os.path.join(ROOT, "docs", "img"), 1600)
