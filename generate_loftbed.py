"""
Freestanding loft bed with a convertible sofa / table / bed underneath
(Hoppekids-style), custom fitted between two walls 1990 mm apart.

COORDINATE SYSTEM (all units mm)
--------------------------------
  Z  up, floor at Z = 0
  X  along the length of the bed. The two walls are the planes X = 0 and
     X = WALL_SPAN (1990). HARD LIMIT: no geometry may cross those planes.
  Y  depth. Y = 0 is the inner face of the back rail, positive Y points
     towards the front (room side). Negative Y is "behind" the back rail
     (where the back guard boards sit).

DESIGN INTENT (v8 - "flush mattress + open front floor + slim 320 ladder")
--------------------------------------------------------------------------
D12 DEPTH SHRINK - THE MATTRESS IS FLUSH AT BOTH EDGES. The platform was
    906 mm deep and carried an 800 mm mattress, so 106 mm of bare slat was
    on show - 29 mm at the back, 77 mm at the front. The whole depth stack
    is pulled in by 106 mm ON THE FRONT SIDE ONLY; the back plane (back rail
    Y -48..0, back posts Y -96..-48, back guards Y -130..-96, back ledger,
    back bench rail) does not move at all. What that gives:
      * upper slats and bench slats become 800 mm long, Y -48..752 - still
        one and the same piece, still 34x98, still lying on top of the rails;
      * the front side rail moves 810..858 -> 704..752, so the clear width
        between the upper rails is 704 = 800 - 2 x 48: the mattress spans
        OVER both rails and its two edges land exactly on the slat ends;
      * the reference mattress is Y -48..752, i.e. EXACTLY the slat footprint.
        Sideways play is 0 by construction, which is the point - there is no
        bare slat strip left to fall into and no gap along either edge;
      * everything in the front plane follows -106: front corner posts
        752..800, ladder uprights 752..800, rung treads 727..800 (the 25 mm
        rest ledge behind the upright plane is preserved exactly), rung
        blocks, front guards 800..834, front bench rail 704..752, front stub
        legs, the front bench-rail bearing blocks;
      * the end beams shorten 1002 -> 896 (they still span the full post-to-
        post depth, Y -96..800);
      * the movable panel becomes 680 x 800, Y -48..752 - rear edge still
        flush with the bench slats and on the back bench rail / back ledger,
        front edge still butting the ladder uprights and resting on the rung.
    Overall depth over the guards drops 1070 -> 964 mm.
D13 FRONT FLOOR CLEARED + SLIM 320 LADDER. Two moves that belong together,
    both about the space you actually stand in.
      * The front bench rail no longer runs from the sofa to the ladder. Each
        segment now STOPS AT ITS SOFA END, X 3..645 and X 1345..1987 (642 mm
        each), landing its inner end square on the stub leg that was already
        there (X 572..645 / 1345..1418) - zero cantilever, the leg simply
        moves from mid-span to end-bearing. Nothing at bench-rail height
        crosses the whole 700 mm between the two benches any more, so the
        entire front floor in front of the ladder is clear.
      * The ladder narrows from 420 to 320 clear and slims from 48x48 to
        36x48 uprights, 36 along X / 48 along Y so the 48 face still lies
        flat on the front rail plane for through-bolting. Upright inner faces
        835 / 1155, outer faces 799 / 1191, symmetric about 995. The rungs
        become 320 mm treads, the front guard segments lengthen to 832 mm to
        meet the new inner faces, and the climb-through gap is 320 mm in both
        guard bands and at floor level. The rung blocks are unchanged 36x48
        x 73 offcuts - their 36 mm is stock thickness, not upright width, and
        the 48 x 48 face they present to the upright inner face is unaffected
        by the upright getting narrower in X.
    The pair of them opens a walk-around passage on each side of the ladder,
    between the sofa end and the upright outer face, 151 mm clear and empty
    from the floor to 482.
    STRUCTURAL CONSEQUENCE, flagged for the docs round: the ladder has LOST
    its low lateral restraint. See the LADDER section for the numbers.

DESIGN INTENT (v7 - "resting panel + even ladder + open ladder bay")
--------------------------------------------------------------------
D8  EVEN LADDER. The rungs were a mechanical 280/560/840/1120 grid that had
    nothing to do with the rest of the bed: a 280 mm first rise off the floor
    and then three 280 mm steps up to a platform that D5 had moved to 1197,
    leaving a 77 mm stub of a last step. The tops are now 259 / 482 / 720 /
    958. Rung 1 lands exactly on the BENCH RAIL TOP (259) and rung 2 exactly
    on the TABLE-MODE PANEL UNDERSIDE (482), so the two rungs that carry the
    movable panel (D10) are the same wood as the rest of that mode's support
    line; rungs 3 and 4 are then spaced to even out the climb. The rises are
      floor -> 259   259 mm   (the "first step" IS the bench seat rail line)
      259 -> 482     223 mm
      482 -> 720     238 mm
      720 -> 958     238 mm
      958 -> 1197    239 mm   (last rung to the platform surface)
    i.e. every step of the climb proper is 223..239 mm, a 16 mm spread, all
    under the 250 mm comfort limit. The 259 mm floor-to-rung-1 rise is not a
    climbing step in the same sense - it is a seat-height ledge you step onto,
    and it is fixed by the bench rail it shares its top with.
D9  BACK LEDGER UP. The back table ledger moves from Z 371..466 to 387..482,
    so its top is level with rung 2 (482) and the table-mode panel lies
    straight on both of them - no step, no bracket (D10).
D10 THE PANEL RESTS ON WOOD. The four steel U-hooks of D3 are DELETED, and
    with them the 16 mm hook step. The panel now simply LIES on wood:
      BED MODE   Z 259..277 - on the back bench rail (top 259), on rung 1
                 (top 259) and, because D11 only takes the MIDDLE out of the
                 front bench rail, on the two front rail segment ends as well.
      TABLE MODE Z 482..500 - on the back table ledger (top 482) and rung 2
                 (top 482).
    Two consequences fall out of that:
      * the panel grows to the full depth of a slat (v7: 906, Y -48..858;
        v8/D12: 800, Y -48..752) because it has to REACH the members it rests
        on - the back bench rail lives at Y -48..0 and the ledger at
        Y -48..-27, and the old Y 30 rear edge reached neither. Its rear edge
        is now flush with the bench slats' rear edge, so in bed mode benches
        and panel are one field.
      * the RUNGS slide 25 mm back, so the tread fronts are flush with the
        ladder-upright front faces instead of standing 25 mm proud of them
        (v7: Y 858..931 -> 833..906; v8/D12: Y 727..800). This is what gives
        the panel's front edge something to sit ON: the panel cannot cross
        the upright back plane (the uprights are floor-to-ceiling and the
        panel's X range 655..1335 straddles both of them), so the rung has to
        come back to meet it. The result is a RUNG_LEN x 25 mm bearing under
        the front edge - the same order as the 21 mm the back ledger offers -
        and the rung blocks keep their full 48 x 48 mm face contact on the
        upright inner faces.
      * v8/D13 ripple: with the front bench rail cut back to the sofa ends the
        bed-mode panel no longer picks up its two segment ends. Both modes are
        now the same clean two-line support - a back member (bench rail /
        ledger) and a rung - about 727 mm apart.
    The panel top in bed mode is 277, i.e. 16 mm BELOW the 293 bench tops.
    That dip is deliberate: the fold-out seat cushions are what bridge the
    three zones into one sleeping surface, and they need somewhere to fold
    into.
M4  PANEL STIFFENER BATTENS + THE REAL PANEL CONNECTIONS. An 18 mm sheet on
    the two-line support D13 left it with is at bending utilisation ~1.42 at
    the 2 kN dynamic design point - a fail. Two 48x73 battens ON EDGE, 727 mm
    long, are screwed under the panel and run bearing line to bearing line
    (Y 0..727, i.e. from the back rail face to the rung face). They sit at
    X 882..930 and 1060..1108, symmetric about the ladder centreline 995 and
    inset 11 mm inside the rung-block line, and they hang BELOW the panel:
    Z 186..259 in bed mode, 409..482 in table mode. They travel with the
    panel. Utilisation drops to ~0.27.
    The steel is not modelled but it is not decorative either. At the FRONT,
    load-bearing U-brackets wrap the rung (as on the Hoppekids original) and
    clamp the panel to the ladder: that is the panel's anti-tip restraint AND,
    through the panel, the brace that ties the ladder base back to the rear
    bearing line - this design's answer to the ladder-restraint finding F1.
    At the REAR, hook plates drop over the back bench rail (bed mode) or the
    back table ledger (table mode).
D11 OPEN LADDER BAY. The FRONT bench rail is cut into two segments so nothing
    crosses the floor of the ladder bay below the benches any more - you can
    stand at the foot of the ladder with your toes under it. Both front stub
    legs stay where they were, under their segment. The BACK bench rail is
    untouched and still runs the full 1984 mm.
    v7 made the segments X 3..785 / 1205..1987, each lapping its ladder
    upright over the full 48 mm face on the plane Y = 858. v8/D13 goes the
    whole way and stops them at the SOFA ends instead (X 3..645 / 1345..1987,
    642 mm each), so the open bay is the entire 700 mm between the benches,
    not just the 420 mm of the ladder. The lap onto the upright is gone with
    it; the inner end bears on the stub leg that was already under it.

DESIGN INTENT (v6 - "flush top + re-banded guards" final tweak)
---------------------------------------------------------------
D5  The upper mattress platform is no longer a sunken tray. The two 36x48
    slat cleats are DELETED and the slats now lie ON TOP of both side rails,
    exactly the way the bench slats lie on top of the bench rails. One
    consequence at a time:
      * the slats become the same piece as a bench slat - 34x98, spanning the
        full platform depth so each one covers the full 48 mm width of BOTH
        rails (v7: 906 mm, Y -48..858; v8/D12: 800 mm, Y -48..752) - and
        34x98 becomes the common board stock of the whole design;
      * the platform surface rises 1134 -> 1197 and the mattress with it,
        1197..1337;
      * the slat reaction now lands on the rail centreline instead of on a
        cleat screwed to one face, so the rails are loaded concentrically;
      * both guard bands move up (see D6). The rail underside, the head
        clearance under the platform and the whole lower storey are untouched.
D6  GUARD RE-BANDING. With the mattress top at 1337 the two guard bands go to
    Z 1412..1510 and 1585..1683, which makes every opening measured above the
    mattress surface 75 / 75 / 17 mm - all at or under the 75 mm EN 747
    entrapment limit, with the top band still 346 mm above the mattress.
D7  ONE GUARD PROFILE. The front guard segments follow the back boards from
    21x95 up to 34x98 (v7: Y 906..940; v8/D12: Y 800..834), so every guard
    and every slat in the bed is cut from the same board. 21x95 now survives
    only as the back table ledger.

DESIGN INTENT (v5 - "slim + 6 verticals" design round)
------------------------------------------------------
C9 is the rule that shapes everything horizontal: a 1990 mm long member
cannot be swung into a 1990 mm opening (the corners sweep ~997 mm from the
centre when the piece is rotated down to horizontal). Every through-running
horizontal member is therefore 1984 mm long and centred at X 3..1987.
Only the vertical posts still touch the walls at X 0..48 / 1942..1990.

WHAT CHANGED IN v5
  D1  The two intermediate BACK POSTS (v4 / C1) are GONE. The frame now has
      exactly SIX verticals: four corner posts and two ladder uprights.
      The back guard boards are upgraded from 21x95 to 34x98 to carry the
      resulting full 1894 mm span between the corner posts on their own.
  D2  The front guard boards are SEGMENTED. Each band is two boards lapped
      onto the ladder uprights, so the ladder opening continues straight up
      past the guard rails and you climb THROUGH instead of over. (v5: 21x95,
      X 3..785 / 1205..1987, 420 mm opening. v7/D7: 34x98. v8/D13: X 3..835 /
      1155..1987, 832 mm each, 320 mm opening.)
  D3  The front table ledger (v4 / C6) is DELETED - it crossed the front of
      both sofa benches at knee height. The panel is instead carried at its
      FRONT edge by a LADDER RUNG (rung 1 in bed mode, rung 2 in table mode)
      and at its REAR edge by the back bench rail (bed mode) / the back table
      ledger (table mode). (v7: the four steel U-hooks that used to make that
      connection are gone too - the panel lies straight on the wood now, see
      D8/D9/D10.)
  D4  SLIMMING. Side rails and end beams 48x123 -> 48x98 (rail underside
      stays at 1065, end-beam top stays flush with it). Corner posts and
      ladder uprights 48x73 -> 48x48. Everything else keeps its stock.

Upper level: a 1984 x 800 sleeping platform at 1065 mm underside height (the
slats bridge both rails flush on top, D5; D12 shrank the depth 906 -> 800 so
the 800 mm mattress is flush at both edges), carried by four corner posts. The
two ends are OPEN above the mattress -
there are no end boards at guard-rail height, because they cut into the
sleeping area. Instead each end has a single 48x98 END BEAM bolted to the
inner faces of the corner posts, its top flush with the underside of the
side rails so both rails bear on it. Under each end of each end beam sits a
36x48 BEARING BLOCK (C2, joint J1-B) screwed to the post, so the vertical
load is wood-on-wood bearing and the M8 bolts become pure ties.

The ladder is mounted directly on the front of the bed: its 36x48 uprights
share the Y 752..800 plane with the front corner posts, i.e. they lie flat
against the outer face of the front rail (bolted through it in reality).
The rungs are 48x73 treads, 320 mm long, carried on cleat blocks screwed to
the inner faces of the uprights.

Lower level: a convertible sofa / table / bed. The 48x73 bench rails sit at
Z 186..259, carried by the corner posts (via 36x48 J9-B bearing blocks, C2)
and by four stub legs. The BACK rail runs the whole 1984 mm (C5); the FRONT
one is two 642 mm segments that stop at the sofa ends on their stub legs,
leaving the whole front floor between the benches open (D11/D13). The two
benches are the slatted zones at each end: 34x98 slats (C3) laid on the
rails, so the bench top is at Z = 293. Between the benches an 18 mm pine
panel, stiffened by two 48x73 battens on edge underneath it (M4), RESTS on
wood (D10) - it is held down by steel U-brackets round the rung at the front
and hook plates at the back, but every gram of vertical load goes into wood:
  * TABLE MODE  - on the back table ledger (top Z 482) and on ladder rung 2
                  (top Z 482); panel top Z = 500.
  * BED MODE    - on the back bench rail (top Z 259) and on ladder rung 1
                  (top Z 259); panel top Z = 277, i.e. 16 mm below the bench
                  slats, the depth the fold-out cushions bridge.

Everything is modelled as plain axis-aligned Boxes moved into place.

EXPORTS
-------
Default (`mise run build`) - the fast validation loop only:
  .step  Z-up, mm, per-part names and colours (CAD truth).
  .stl   Y-up, baked into the vertex data, so the bed stands upright in
         Quick Look / Preview / Xcode without any extra rotation.
  per-colour-group .stl files in a scratch directory, consumed by
  tools/mesh_to_usda.swift to build a multi-material .usdz.

Opt-in (`mise run build-full`, i.e. LOFTBED_FULL=1) - the slow deliverables,
run once at the end of the project:
  .glb   Y-up (export_gltf writes the Z-up -> Y-up rotation on the root
         node itself), one node per part, per-part colours.
  .svg   hidden-line iso + front projections. These dominate the runtime.
"""

import math
import os
import tempfile

from build123d import (
    Box,
    Color,
    Compound,
    ExportSVG,
    Location,
    export_gltf,
    export_step,
    export_stl,
)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Per-colour-group STL intermediates live outside the repo (they are only an
# input to the .usdz conversion). Override with LOFTBED_GROUP_DIR.
GROUP_DIR = os.environ.get(
    "LOFTBED_GROUP_DIR", os.path.join(tempfile.gettempdir(), "loftbed_groups")
)

# LOFTBED_FULL=1 turns on the slow deliverable exports (.glb and the hidden-line
# .svg projections). The default build writes only what the STEP/USDZ/render
# chain needs, which is what the design-validation loop runs over and over.
FULL_EXPORT = os.environ.get("LOFTBED_FULL", "").lower() in ("1", "true", "yes", "on")

# ---------------------------------------------------------------------------
# LUMBER CROSS SECTIONS (Norwegian standard planed dimensions)
# ---------------------------------------------------------------------------
# D4: the four corner posts and the two ladder uprights go 48x73 -> 48x48.
# Reasoning (see the report): all vertical load already rides on the C2 wood
# bearing blocks, so every post bolt is a pure TIE. A single central M8 in a
# 48 mm face has 24 mm edge distance = 3d, which is exactly the EC5 minimum
# for an unloaded edge - and a 48x73 post could not have taken two bolts
# side by side either (4d spacing + 2x3d edge = 80 mm > 73), so the wider
# section bought no extra bolting. Ties are stacked VERTICALLY instead
# (5d = 40 mm apart along the grain), which works in 48x48 just as well.
POST_T = 48          # corner posts, thin dim (Y)
POST_W = 48          # corner posts, wide dim (X)  [was 73]

# D13: the two ladder uprights slim further, 48x48 -> 36x48, oriented 36 along
# X and 48 along Y. The 48 mm face is the one that lies against the front rail
# plane, so the through-bolt into the side rail keeps its full 48 mm of glue
# line and its 24 mm edge distance; what shrinks is only the width you see
# from the front, which is what buys the extra 2 x 12 mm of walk-around.
UPRIGHT_W = 36       # ladder uprights, X
UPRIGHT_T = POST_T   # ladder uprights, Y - unchanged, it is the bolting face

LEG_T = 48           # bench stub legs, thin dim (Y)   - unchanged stock
LEG_W = 73           # bench stub legs, wide dim (X)   - unchanged stock

RAIL_T = 48          # upper bed side rails and end beams, thickness
RAIL_H = 98          # upper bed side rails and end beams, height  [was 123]

BENCH_RAIL_T = 48    # continuous bench rails, thickness (Y) - unchanged stock
BENCH_RAIL_H = 73    # continuous bench rails, height (Z)    - unchanged stock

TREAD_T = 48         # ladder rung (tread) thickness (Z) - unchanged stock
TREAD_D = 73         # ladder rung (tread) depth (Y)     - unchanged stock

BOARD_T = 21         # 21x95 board, thickness  - D7: the back table ledger ONLY
BOARD_W = 95         # 21x95 board, width      - D7: the back table ledger ONLY

# D5/D7: 34x98 is the COMMON BOARD STOCK of this design. Everything flat-laid
# or stood on edge as a board comes out of it: the 13 upper bed slats, the 10
# bench slats (identical pieces, 906 mm), the 2 back guard boards and the 4
# front guard segments. One profile, one pile of timber, one setup on the saw.
BOARD34_T = 34       # 34x98 board, thickness
BOARD34_W = 98       # 34x98 board, width

GUARD_T = BOARD34_T  # guard boards, thickness (Y) - back (D1) and front (D7)
GUARD_W = BOARD34_W  # guard boards, width (Z)
BED_SLAT_T = BOARD34_T   # D5: upper bed slats, thickness (Z)
BED_SLAT_W = BOARD34_W   # D5: upper bed slat width (X)
BENCH_SLAT_T = BOARD34_T # C3: bench slats upgraded 21x95 -> 34x98, thickness (Z)
BENCH_SLAT_W = BOARD34_W # C3: bench slat width (X)
BLOCK_T = 36         # 36x48 bearing/rung block stock, thin dim
BLOCK_H = 48         # 36x48 bearing/rung block stock, wide dim
PANEL_T = 18         # movable pine panel thickness

# ---------------------------------------------------------------------------
# COLOUR GROUPS
# ---------------------------------------------------------------------------
# One colour per structural family. These survive into the .step (XCAF
# colours), into the .glb (one material per node) and, via the per-group STL
# export below, into the .usdz as five named UsdPreviewSurface materials.
GROUP_COLORS = {
    "posts": Color(0.95, 0.94, 0.91),       # posts, ladder uprights, stub legs
    "rails": Color(0.85, 0.73, 0.54),       # side rails, end beams, bench rails
    "boards": Color(0.91, 0.84, 0.68),      # slats, rungs, blocks, guards, ledger
    "panel": Color(0.98, 0.98, 0.96),       # movable pine panel
    "mattress": Color(0.62, 0.72, 0.81, 0.45),   # translucent reference mattress
}
GROUP_ORDER = ["posts", "rails", "boards", "panel", "mattress"]

# ---------------------------------------------------------------------------
# ENVELOPE
# ---------------------------------------------------------------------------
WALL_SPAN = 1990                 # X = 0 .. 1990, hard limit
MATTRESS_W = 800                 # 200x80 mattress
MATTRESS_H = 140

# D12: the platform depth IS the mattress width. The slats run from the outer
# face of the back rail to the outer face of the front rail, so the platform is
# (clear width) + 2 x RAIL_T; setting that equal to 800 puts the mattress edges
# exactly on the slat ends. The clear width between the upper side rails falls
# out of it: 800 - 2 x 48 = 704 (was 810, a 906 mm platform under an 800 mm
# mattress with 106 mm of bare slat on show).
PLATFORM_DEPTH = MATTRESS_W                        # 800, D12
INNER_CLEAR_WIDTH = PLATFORM_DEPTH - 2 * RAIL_T    # 704
DEPTH_SHRINK = 906 - PLATFORM_DEPTH                # 106, taken off the FRONT

# C9: no horizontal 1990 mm member can be manoeuvred into a 1990 mm opening -
# swinging it down to horizontal sweeps sqrt(995^2 + 61.5^2) = 996.9 mm from the
# centre, ~2 mm too long at each end. Every through-running horizontal member is
# cut to 1984 and centred, leaving 3 mm clearance at each wall.
THROUGH_LEN = 1984               # every wall-to-wall horizontal member
THROUGH_X0 = (WALL_SPAN - THROUGH_LEN) // 2     # 3
THROUGH_X1 = THROUGH_X0 + THROUGH_LEN           # 1987

# ---------------------------------------------------------------------------
# UPPER BED
# ---------------------------------------------------------------------------
# D4: the rails are slimmed 123 -> 98 mm deep. The UNDERSIDE stays fixed at
# 1065 (head clearance below the platform is untouched); the top drops
# 1188 -> 1163.
#
# UTILISATION NOTE (D4, back side rail, worst case): with the intermediate
# back posts gone the back rail is a full 1894 mm single span. At the 2 kN
# dynamic design point the bending utilisation scales with (123/98)^2 = 1.575,
# i.e. 0.46 -> ~0.73, and the deflection with (123/98)^3 = 1.98, giving about
# 6 mm at midspan (~L/315). Both are acceptable; formal re-verification is a
# job for the docs round.
RAIL_BOTTOM = 1065               # underside of the upper side rails (FIXED)
RAIL_TOP = RAIL_BOTTOM + RAIL_H  # 1163

# D12: the BACK plane is the fixed datum - it does not move. Everything in
# front of it comes in by DEPTH_SHRINK = 106 mm.
BACK_RAIL_Y0 = -RAIL_T           # -48 .. 0   (FIXED)
BACK_RAIL_Y1 = 0
FRONT_RAIL_Y0 = INNER_CLEAR_WIDTH        # 704  [was 810]
FRONT_RAIL_Y1 = FRONT_RAIL_Y0 + RAIL_T   # 752  [was 858]

# D5: FLUSH TOP. The slat cleats are gone; the slats lie ON TOP of both side
# rails, exactly like the bench slats on the bench rails. Each slat therefore
# spans from the OUTER face of the back rail to the OUTER face of the front
# rail (D12: Y -48..752) and covers the full 48 mm width of both - which is
# what makes it the same 34x98 x 800 piece as a bench slat. One 5x60 screw per
# end down into the rail; no cleat, no rebate, no lip anywhere.
#
# UTILISATION NOTE (D5, upper bed slat): identical stock, identical span and
# identical load model to the bench slat (C3), so the numbers are the same.
# 34x98 flat-on gives W = 98*34^2/6 = 18 881 mm3. The bench-slat case - the
# 2 kN dynamic design point shared over three slats, then checked with the
# concentrated 1.0 kN that a single slat can see on its own at midspan of the
# span - gave, over the v7 906 mm span, M = 227 kNmm, sigma = 12.0 MPa against
# f_m,d = 16.6 MPa, so utilisation ~0.72 (deflection ~4.4 mm, L/206). D12
# shortens the span to 800 mm, i.e. M scales by 800/906 = 0.883 and the
# deflection by 0.883^3 = 0.69: sigma ~10.6 MPa, utilisation ~0.64, deflection
# ~3.0 mm (L/262). The depth shrink is a strict improvement here.
SLAT_Z0 = RAIL_TOP                       # 1163, slats bear on top of the rails
SLAT_Z1 = SLAT_Z0 + BED_SLAT_T           # 1197
SLAT_Y0 = BACK_RAIL_Y0                   # -48, outer face of the back rail
SLAT_Y1 = FRONT_RAIL_Y1                  # 752, outer face of the front rail
SLAT_LEN = SLAT_Y1 - SLAT_Y0             # 800  (the bench slat, same piece)
SLAT_COUNT = 13
SLAT_X_START = 20                        # first slat left edge
SLAT_X_END = 1970                        # last slat right edge
MAX_SLAT_GAP = 60

# The reference mattress sits proud on the flush platform, and after D12 it is
# EXACTLY the platform footprint: both its long edges land on the slat ends, so
# there is no bare slat strip at either side any more.
MATTRESS_Z0 = SLAT_Z1                    # 1197
MATTRESS_Y0 = SLAT_Y0                    # -48  [was 29]
MATTRESS_Y1 = MATTRESS_Y0 + MATTRESS_W   # 752  [was 829] == SLAT_Y1
MATTRESS_Z1 = MATTRESS_Z0 + MATTRESS_H   # 1337

# ---------------------------------------------------------------------------
# SHARED LOWER DATUM  (hoisted - the ladder needs it before it is "its" section)
# ---------------------------------------------------------------------------
# The bench rail top is THE lower datum of the whole convertible section: it is
# the seat-height ledge, it is rung 1's top (D8), it is the bed-mode panel
# underside (D10) and it is the top of the stiffener battens (M4). It used to be
# declared down in LOWER CONVERTIBLE SECTION, which forced RUNG_TOPS[0] to
# repeat the literal 259 and left two numbers to keep in step by hand. It is
# hoisted here so every consumer derives from the one declaration.
BENCH_RAIL_TOP = 259                                # fixed by the doc (J9, J13)
BENCH_RAIL_BOTTOM = BENCH_RAIL_TOP - BENCH_RAIL_H   # 186

# ---------------------------------------------------------------------------
# POSTS  (D1: SIX verticals in total - four corner posts, two ladder uprights)
# ---------------------------------------------------------------------------
POST_HEIGHT = 1700                       # floor to top of every post
BACK_POST_Y0 = BACK_RAIL_Y0 - POST_T     # -96 .. -48 (outer face of back rail)
BACK_POST_Y1 = BACK_RAIL_Y0              # -48
FRONT_POST_Y0 = FRONT_RAIL_Y1            # 752 .. 800 (outer face of front rail)
FRONT_POST_Y1 = FRONT_POST_Y0 + POST_T   # 800
CORNER_POST_X = [0, WALL_SPAN - POST_W]  # 0..48 and 1942..1990 (walls untouched)

# ---------------------------------------------------------------------------
# END BEAMS (48x98, rail stock)
# ---------------------------------------------------------------------------
# One per end, bolted to the inner faces of the two corner posts of that end.
# Its top is flush with the rail underside, so BOTH side rails land on it and
# it carries the platform across the end. Above the mattress the ends are
# completely open.
#
# UTILISATION NOTE (D4, end beam): a 1002 mm span carrying the two rail
# reactions. 48x123 -> 48x98 raises the bending utilisation by (123/98)^2 =
# 1.575 from ~0.24 to ~0.38 and roughly doubles the (tiny) deflection.
# Comfortable margin. D12 shortens the span 1002 -> 896 (-106), which takes
# the utilisation back down by roughly (896/1002)^2 = 0.80 to ~0.30.
END_BEAM_Y0 = BACK_POST_Y0                     # -96
END_BEAM_Y1 = FRONT_POST_Y1                    # 800  [was 906]
END_BEAM_LEN = END_BEAM_Y1 - END_BEAM_Y0       # 896  [was 1002]
END_BEAM_Z1 = RAIL_BOTTOM                      # 1065, flush with rail underside
END_BEAM_Z0 = END_BEAM_Z1 - RAIL_H             # 967
# D4 ripple: the posts are 48 wide now, so the beams slide out to the new post
# inner faces. The side rails (X 3..1987) still cover both beams completely.
END_BEAM_X = [POST_W, WALL_SPAN - POST_W - RAIL_T]   # 48..96 and 1894..1942

# C2 / joint J1-B: a 36x48 offcut under each end of each end beam, screwed to the
# inner face of the corner post with 2x 5x80. 48 mm in X (right under the beam),
# 48 mm in Y (the full post depth), 36 mm in Z, top flush with the beam underside.
# The end beam then BEARS on wood (48x48 = 2304 mm2, 5.3 kN) instead of hanging in
# bolt shear with only 24 mm end distance.
BEAM_BLOCK_DX = RAIL_T                         # 48 (X), matches the beam
BEAM_BLOCK_DY = POST_T                         # 48 (Y), matches the post depth
BEAM_BLOCK_DZ = BLOCK_T                        # 36 (Z)
BEAM_BLOCK_Z1 = END_BEAM_Z0                    # 967, flush with the beam underside
BEAM_BLOCK_Z0 = BEAM_BLOCK_Z1 - BEAM_BLOCK_DZ  # 931
BEAM_BLOCK_LEN = BEAM_BLOCK_DX                 # 48, cut length off 36x48 stock

# ---------------------------------------------------------------------------
# LADDER
# ---------------------------------------------------------------------------
# The uprights are in the SAME Y plane as the front corner posts, i.e. flat
# against the outer face of the front rail (through-bolted in reality).
#
# D13: the ladder narrows 420 -> 320 clear and the uprights slim 48x48 ->
# 36x48. The opening stays centred on X 995, so the INNER faces move out to
# 835 / 1155 and the OUTER faces to 799 / 1191 - i.e. the whole ladder is
# 100 mm narrower in the clear and 24 mm narrower over the uprights. 320 mm is
# still a comfortable climb-through (EN 747 asks for >= 300 between the ladder
# stiles for a child's bed ladder) and the 100 mm it gives back is what turns
# the two dead corners beside the ladder into a real walk-around passage.
#
# D13 / STRUCTURAL FLAG FOR THE DOCS ROUND - THE LADDER LOSES ITS LOW LATERAL
# RESTRAINT. Until v7 each upright was tied to the frame twice below the
# platform: the front bench rail segment lapped it face-to-face over 48 x 73 mm
# at Z 186..259, and the front side rail took it at Z 1065..1163. D13 cuts the
# bench rail back to the sofa ends, so the lap is gone and the ONLY connection
# to the frame below the guards is the through-bolted front side rail. The
# uprights remain bolted through that rail and they still carry the rungs (the
# rungs sit on 36x48 cleat blocks screwed to the upright inner faces, exactly as
# before), and the four rungs still triangulate the two uprights to each other
# in the ladder's own plane - what is gone is the out-of-plane (Y) hold at
# bench height.
#   BUCKLING, weak-plane check on the new 36x48 section:
#     A = 1728 mm2; I_y (bending in Y, the 48 mm depth) = 36*48^3/12 = 331 776
#     mm4, i_y = 13.86 mm; I_x (bending in X, the 36 mm width) = 48*36^3/12 =
#     186 624 mm4, i_x = 10.39 mm.
#   In the ladder plane (X) the rungs brace the upright at 259 / 482 / 720 /
#   958, so the worst unbraced length there is the 259 mm floor-to-rung-1 and
#   lambda_x = 25 - irrelevant.
#   OUT OF PLANE (Y) is the one that moved. v7: restrained at the bench rail
#   lap (top 259) and at the rail (1065), worst unbraced length 1065 - 259 =
#   806 mm, lambda_y = 58. v8/D13: the bench lap is gone, so the length runs
#   floor to rail, 1065 mm - a growth of 259 mm - and lambda_y = 1065/13.86 =
#   77. For C24 that is k_c ~ 0.5, i.e. N_c,Rd ~ 1728 * 0.5 * 13 = ~11 kN
#   against the ~1 kN a climber puts down an upright. Ample, but it is now a
#   slenderness-governed member instead of a stocky one, and the base is
#   unrestrained in Y: the docs round must run the real EC5 6.3.2 check and
#   decide whether to add a floor-level tie back to the front corner posts.
LADDER_Y0 = FRONT_RAIL_Y1                # 752, outer face of the front rail
LADDER_Y1 = LADDER_Y0 + UPRIGHT_T        # 800, same plane as the front posts
LADDER_CLEAR = 320                       # clear width between the uprights
LADDER_CENTER_X = 995
LADDER_INNER_L = LADDER_CENTER_X - LADDER_CLEAR // 2          # 835  (FIXED)
LADDER_INNER_R = LADDER_CENTER_X + LADDER_CLEAR // 2          # 1155 (FIXED)
LADDER_LEFT_X = LADDER_INNER_L - UPRIGHT_W                    # 799 .. 835
LADDER_RIGHT_X = LADDER_INNER_R                               # 1155 .. 1191
MIN_LADDER_CLEAR = 300                   # EN 747 clear width between stiles

# Rungs are proper treads out of 48x73 stock: 73 deep, 48 thick.
# D10: the treads sit BACK in the uprights - their front faces are flush with
# the upright front faces (D12: Y = 800) instead of standing 25 mm proud of
# them, so their back 25 mm reaches behind the plane Y = 752 and gives the
# movable panel's front edge a 320 x 25 mm ledge to rest on. The panel itself
# cannot come forward to meet the rung: the uprights occupy Y 752..800 right
# across its X range. Nothing else lives in Y 727..752 at any rung height -
# D11/D13 take the front bench rail out of the whole X band between the sofas.
RUNG_LEN = LADDER_CLEAR                  # 320, X 835 .. 1155  [was 420]
RUNG_T = TREAD_T                         # 48, tread thickness (Z)
RUNG_D = TREAD_D                         # 73, tread depth (Y)
RUNG_Y1 = LADDER_Y1                      # 800, flush with the upright front
RUNG_Y0 = RUNG_Y1 - RUNG_D               # 727
RUNG_REST_LEDGE = LADDER_Y0 - RUNG_Y0    # 25, the bit behind the upright plane
# D8: an even climb. See the design-intent note - rung 1 shares its top with
# the bench rails (259) and rung 2 with the table-mode panel underside (482);
# 720 and 958 even out the rest of the way to the 1197 platform.
RUNG_TOPS = [BENCH_RAIL_TOP, 482, 720, 958]
MAX_CLIMB_STEP = 250             # comfort limit, rung 1 upwards
MAX_CLIMB_SPREAD = 20            # how uneven the climb proper may be

# Cleat blocks under every rung end, screwed to the inner faces of the
# uprights; the rung sits on them and is screwed down from above.
#
# D13 CHECK - does the 36x48x73 block still work against a 36 mm wide upright?
# Yes, unchanged, because none of its three dimensions references the upright
# WIDTH: the 36 mm is the block's own stock thickness standing off the upright
# inner face (into the ladder opening), the 48 mm is its height in Z, and the
# 73 mm follows the tread depth in Y. What it presents to the upright is a
# 48 (Z) x 48 (Y) face - the upright is still 48 deep in Y - so the screwed
# contact area is exactly what it was. As before, the block's rear 25 mm
# (Y 727..752) overhangs the upright's back plane together with the tread it
# carries. No adjustment needed.
RUNG_BLOCK_T = BLOCK_T                   # 36 (X), stock thickness
RUNG_BLOCK_H = BLOCK_H                   # 48 (Z)
RUNG_BLOCK_LEN = RUNG_D                  # 73 (Y), same depth as the tread
RUNG_BLOCK_X = [LADDER_INNER_L,                          # 835 .. 871
                LADDER_INNER_R - RUNG_BLOCK_T]           # 1119 .. 1155

# ---------------------------------------------------------------------------
# GUARD RAILS
# ---------------------------------------------------------------------------
# Two bands per side, at the same Z front and back and - after D7 - out of the
# same 34x98 board front and back, so the two sides are now geometrically
# identical mirror images of each other.
#
# D6 RE-BANDING. The flush top (D5) lifted the mattress surface 1274 -> 1337,
# which would have left a 56 mm opening under the old lower band and a useless
# 426 mm one above the top band. The bands move to 1412..1510 and 1585..1683,
# which makes the three openings measured ABOVE THE MATTRESS SURFACE
#     1337 -> 1412   75 mm   (mattress top to the underside of band 1)
#     1510 -> 1585   75 mm   (between the bands)
#     1683 -> 1700   17 mm   (band 2 to the top of the posts)
# i.e. every one of them at or under the 75 mm EN 747 entrapment limit, and
# the top edge of the barrier 1683 - 1337 = 346 mm above the mattress (EN 747
# asks for 160). This is the item that closes the entrapment finding.
GUARD_BAND_Z0 = [1412, 1585]
MAX_GUARD_OPENING = 75           # EN 747 entrapment limit, above the mattress
MIN_GUARD_OVER_MATTRESS = 160    # EN 747 barrier height above the mattress

# D1: with the two intermediate back posts deleted the back boards span the
# full 1894 mm between the corner post inner faces. 21x95 flat-on (W = 95*21^2/6
# = 6983 mm3) was at utilisation 1.99 over 1844 mm - failure. 34x98 gives
# W = 98*34^2/6 = 18 883 mm3, so at the same 0.54 kN/m barrier line load the
# stress falls to ~12.9 MPa against f_m,d = 16.6 MPa -> utilisation ~0.78.
# (Deflection under the full barrier load is ~26 mm, which is large but is a
# short-term accidental-load figure for a guard, not a serviceability case.)
BACK_GUARD_Y1 = BACK_POST_Y0                       # -96, outer face of the posts
BACK_GUARD_Y0 = BACK_GUARD_Y1 - GUARD_T            # -130

# D2: the front boards are cut in two so the ladder opening carries on past
# the guard rails - you climb THROUGH, not over.
# NOTE (deviation from the sketch): the sketch had the segments STOP at the
# uprights' outer faces. That is only a line contact - the board end face meets
# the upright side face but the guard plane and the upright plane merely share
# an edge, so the board would be a long cantilever off one corner post and be
# fixed to nothing at its inner end. The segments therefore LAP the uprights'
# front faces and stop flush with the upright INNER faces, which (a) gives a
# full face-to-face screwed lap at the inner end, (b) leaves a clear opening
# exactly as wide as the ladder itself.
#
# D7: the segments go 21x95 -> 34x98, the same board as the back guards and
# every slat in the bed. The lap face is unchanged - the boards land flat on
# the front face of the corner posts and of the ladder uprights, they are just
# 13 mm prouder.
#
# D13: the uprights moved out to inner faces 835 / 1155, so each segment grows
# 782 -> 832 mm and the climb-through opening becomes 320 mm. The lap onto the
# upright shrinks with the upright, 48 -> 36 mm (still a full 36 x 98 = 3528
# mm2 screwed face, two 5x60 into 36 mm of end grain-free timber). Support
# centres go 737 -> 787 mm; the 34x98 board was at utilisation ~0.12 at 737 mm
# so at 787 it is ~0.14 - nothing.
# D12: the whole band comes forward-plane -106, Y 906..940 -> 800..834.
FRONT_GUARD_Y0 = FRONT_POST_Y1                 # 800  [was 906]
FRONT_GUARD_Y1 = FRONT_GUARD_Y0 + GUARD_T      # 834  [was 940]
FRONT_GUARD_SEGMENTS = [(THROUGH_X0, LADDER_INNER_L),      # 3 .. 835
                        (LADDER_INNER_R, THROUGH_X1)]      # 1155 .. 1987
FRONT_GUARD_SEG_LEN = LADDER_INNER_L - THROUGH_X0          # 832  [was 782]

# ---------------------------------------------------------------------------
# LOWER CONVERTIBLE SECTION
# ---------------------------------------------------------------------------
# C5: the bench rails are 48x73 members at Z 186..259, one per Y plane, instead
# of two 645 mm rails per plane. The loose panel had nothing to bear on in the
# gap X 655..1335 before; now there is an unbroken edge behind it. They also
# give the ladder uprights a low fixing point. Max span 700 mm (utilisation
# 0.14).
#
# D11: the BACK rail is still the continuous 1984 mm member. The FRONT one is
# cut, so the ladder bay is open right down to the floor - there is no longer a
# beam across your shins when you stand at the foot of the ladder.
#
# D13: the cut goes all the way back to the SOFA ENDS. v7 stopped the segments
# at the ladder uprights (X 3..785 / 1205..1987, 782 mm) with a face lap onto
# the upright; v8 stops them at X 645 / 1345 (X 3..645 / 1345..1987, 642 mm),
# which is where the sofa slats end and where the stub legs already stood. The
# consequences, in order:
#   * each segment's inner end now lands SQUARE ON ITS STUB LEG (X 572..645 /
#     1345..1418) instead of overhanging it by 140 mm to reach the upright, so
#     the leg goes from a mid-span prop to a clean end bearing and the segment
#     is a two-support member, X 3..48 on the corner post and 572..645 on the
#     leg: a 597 mm span with zero cantilever;
#   * NOTHING at bench-rail height crosses the 700 mm between the two benches
#     any more - the whole front floor in front of the ladder is clear;
#   * the ladder upright loses this lap, which was its low lateral restraint.
#     See the LADDER section for the buckling numbers and the docs-round flag.
# D12: the front rail plane comes in 106 mm, 810..858 -> 704..752.
# BENCH_RAIL_TOP / BENCH_RAIL_BOTTOM are declared up in SHARED LOWER DATUM -
# the ladder section needs the top for RUNG_TOPS[0].
BENCH_RAIL_Y = [BACK_RAIL_Y0, FRONT_RAIL_Y0]        # -48..0 and 704..752

# C3: bench slats 21x95 -> 34x98 (21x95 was at utilisation 1.96 with a point load
# on one slat). Consequence: the bench top rises 280 -> 293, and the bed-mode
# panel follows it (see PANEL_TOP_BED) so it stays flush.
BENCH_TOP = BENCH_RAIL_TOP + BENCH_SLAT_T      # 293, bench slat top / seat height
BENCH_LEN = 645                                # slatted zone / stub leg reference
BENCH_X = [0, WALL_SPAN - BENCH_LEN]           # 0..645 and 1345..1990
BENCH_SLAT_Y0 = BACK_POST_Y1                   # -48
BENCH_SLAT_Y1 = FRONT_RAIL_Y1                  # 752  [was 858]
BENCH_SLAT_LEN = BENCH_SLAT_Y1 - BENCH_SLAT_Y0 # 800  [was 906]
BENCH_SLAT_COUNT = 5
BENCH_SLAT_PITCH = 137.5                       # doc J11: 39.5 mm gap between slats
STUB_LEG_H = BENCH_RAIL_BOTTOM                 # 186, floor to bench rail underside
STUB_LEG_X = [BENCH_LEN - LEG_W,               # 572..645
              WALL_SPAN - BENCH_LEN]           # 1345..1418

# D13: the front bench rail segments end at the SOFA ends, on their stub legs.
FRONT_BENCH_RAIL_SEGMENTS = [(THROUGH_X0, BENCH_LEN),              # 3 .. 645
                             (WALL_SPAN - BENCH_LEN, THROUGH_X1)]  # 1345 .. 1987
FRONT_BENCH_RAIL_SEG_LEN = BENCH_LEN - THROUGH_X0                  # 642  [was 782]
# The clear front floor between the two benches: 645 .. 1345.
OPEN_FLOOR_X = (BENCH_LEN, WALL_SPAN - BENCH_LEN)                  # 645 .. 1345
# D13: the walk-around passages, one on each side of the ladder, between the
# sofa end and the upright outer face. Nominally 799 - 645 = 154 mm each.
MIN_PASSAGE = 140                # clear walk-around beside the ladder

# C2 / joint J9-B: a 36x48 offcut under each end of each bench rail, screwed to
# the inner face of the corner post with 3x 5x70. Its X length follows the post
# width (48 after D4), 36 mm in Y, 48 mm in Z, top flush with the rail underside
# at Z 186. Wood bearing over the rail footprint X 3..48 is 45 x 36 = 1620 mm2
# -> ~3.7 kN at f_c90,d with k_c90 = 1.5; the single M8 bolt stays a pure tie.
RAIL_BLOCK_DX = POST_W                         # 48 (X), cut length off 36x48
RAIL_BLOCK_DY = BLOCK_T                        # 36 (Y)
RAIL_BLOCK_DZ = BLOCK_H                        # 48 (Z)
RAIL_BLOCK_Z1 = BENCH_RAIL_BOTTOM              # 186
RAIL_BLOCK_Z0 = RAIL_BLOCK_Z1 - RAIL_BLOCK_DZ  # 138
# NOTE (deviation): the doc gives the front block as 24 mm deep - it also calls
# it "36 mm i Y". 36 mm off the post face is what is drawn here.
RAIL_BLOCK_Y0 = [BACK_POST_Y1,                          # -48 .. -12
                 FRONT_RAIL_Y1 - RAIL_BLOCK_DY]         # 716 .. 752  [was 822..858]

PANEL_X0 = 655                                 # 10 mm play against each bench
PANEL_X1 = 1335
PANEL_W = PANEL_X1 - PANEL_X0                  # 680
# D10: the panel is as deep as a slat (D12: Y -48..752) because it has to REACH
# the wood it rests on: the back bench rail lives at Y -48..0 and the back table
# ledger at Y -48..-27. Its rear edge is therefore flush with the rear edge of
# the bench slats (both -48), so in bed mode bench / panel / bench form one
# unbroken 800 mm deep field. Its front edge stops in the ladder-upright plane:
# the uprights stand at Y 752..800 and the panel's X range straddles both of
# them, so 752 is a hard limit - which is precisely why the rungs had to move
# back 25 mm to meet it.
PANEL_Y0 = BENCH_SLAT_Y0                       # -48, flush with the bench slats
PANEL_Y1 = LADDER_Y0                           # 752, against the ladder uprights
PANEL_LEN = PANEL_Y1 - PANEL_Y0                # 800, the slat dimension again

# D10: NO HOOKS. The panel is a loose board that LIES on wood, and the geometry
# below is what makes that true in both modes:
#
#   BED MODE    underside 259 = the bench rail tops = rung 1 top. It lands on
#               the back bench rail (680 x 48 = 32 640 mm2) and on rung 1
#               (320 x 25 = 8 000 mm2). Top 277 - see PANEL_BENCH_DIP.
#   TABLE MODE  underside 482 = the back ledger top = rung 2 top. It lands on
#               the ledger (680 x 21 = 14 280 mm2) and on rung 2 (320 x 25 =
#               8 000 mm2). Top 500.
#
# D13 changed the bed-mode case: the front bench rail used to reach into the
# panel's X range and offer 260 x 48 mm under the two front corners, but it now
# stops at the sofa ends (X 645 / 1345) well outside the panel (X 655..1335).
# Both modes are therefore the SAME two-line support now - one back member, one
# rung - with the bearing lines 727 mm apart (Y 0 and Y 727) instead of 858.
# For an 18 mm pine board 680 wide that is a 727 mm simple span, and BARE that
# is not good enough: at the 2 kN dynamic design point (someone sits or kneels
# on the panel, not the 0.55 kN static table load) W = 680*18^2/6 = 36 720 mm3
# puts the bending utilisation at ~1.42 - a fail. M4 answers it with the two
# stiffener battens below.
#
# THE PANEL CONNECTIONS (M4 / F1). The panel is not a loose board any more; it
# is a small assembly that lifts out as one piece, and it is fixed at both ends:
#
#   FRONT  load-bearing steel U-brackets that wrap the rung, exactly as on the
#          Hoppekids original. They are screwed up into the panel and close
#          around the tread, so the panel is clamped to the ladder. That does
#          two jobs at once: it is the panel's anti-tip restraint (you cannot
#          lever the front edge up off its 25 mm ledge), AND it braces the
#          ladder base through the panel - the panel ties the two uprights back
#          to the rear bearing line, which is this design's answer to the
#          ladder-restraint finding F1 (D13 cut the uprights' lap onto the front
#          bench rail and left the base unrestrained in Y).
#   REAR   hook plates that drop over the back bench rail (bed mode) / the back
#          table ledger (table mode) and hold the rear edge down on its ledge.
#
# Neither connection is drawn - they are sheet steel, not timber - but neither
# is a mere locator: the front pair is a structural tie and is sized as one in
# the docs round.
PANEL_UNDER_BED = BENCH_RAIL_TOP               # 259, rests on the rails/rung 1
PANEL_TOP_BED = PANEL_UNDER_BED + PANEL_T      # 277
PANEL_UNDER_TABLE = RUNG_TOPS[1]               # 482, rests on rung 2/the ledger
PANEL_TOP_TABLE = PANEL_UNDER_TABLE + PANEL_T  # 500

# ---------------------------------------------------------------------------
# M4: PANEL STIFFENER BATTENS
# ---------------------------------------------------------------------------
# Two 48x73 battens ON EDGE (48 wide in X, 73 deep in Z), screwed up into the
# underside of the panel and travelling with it. They run the full 727 mm
# between the two bearing lines, so the panel stops being an 18 mm board on a
# 727 mm span and becomes a pair of tee-sections with the panel as their flange.
#
# UTILISATION NOTE (M4, panel, 2 kN dynamic). Bare 18 mm panel, 680 wide over
# 727 mm: W = 36 720 mm3, utilisation ~1.42 - a fail. With two 48x73 battens on
# edge the load goes into the battens, not the sheet: each batten alone gives
# W = 48*73^2/6 = 42 632 mm3, the two together 85 264 mm3, and composite action
# with the 18 mm flange lifts that further. Sharing the 2 kN over the pair,
# utilisation drops to ~0.27. The deflection follows the same way - the thin
# panel over 727 mm was the item the docs round was asked to sign off on, and
# the battens remove the question rather than answer it.
#
# GEOMETRY - the constraints, in the order they bite:
#   Y  the battens must not foul EITHER bearing, in EITHER mode. Rear: the back
#      bench rail occupies Y -48..0 at Z 186..259, which is exactly the bed-mode
#      batten band, so Y0 = 0 (the back ledger at Y -48..-27 is further back
#      still, so table mode is slack). Front: the rungs occupy Y 727..800 at
#      both 259 and 482, so Y1 = 727. Both faces are a butt, not an overlap -
#      and they double as end stops that keep the panel from sliding.
#   X  the battens have to miss the rung-block line. The blocks stand at
#      X 835..871 and 1119..1155, so the usable window is 871..1119; the pair is
#      inset 11 mm inside it and comes out symmetric about the ladder / panel
#      centreline X 995 (centres 906 and 1084, i.e. +/- 89).
#   Z  the batten TOP is the panel underside, so the battens hang BELOW it:
#      186..259 in bed mode, 409..482 in table mode. 186 is the bench rail
#      underside, which is the floor of the ladder-bay walking zone - the
#      battens sit at its ceiling and never enter it. Asserted below.
BATTEN_W = BENCH_RAIL_T                        # 48, batten width (X)
BATTEN_H = BENCH_RAIL_H                        # 73, batten depth (Z), on edge
BATTEN_Y0 = BACK_RAIL_Y1                       # 0, clear of the back rail/ledger
BATTEN_Y1 = RUNG_Y0                            # 727, clear of the rung ledge
BATTEN_LEN = BATTEN_Y1 - BATTEN_Y0             # 727
BATTEN_CLEAR_X = 11                            # inset from the rung-block line
BATTEN_X = [RUNG_BLOCK_X[0] + RUNG_BLOCK_T + BATTEN_CLEAR_X,   # 882 .. 930
            RUNG_BLOCK_X[1] - BATTEN_CLEAR_X - BATTEN_W]       # 1060 .. 1108
BATTEN_Z0_BED = PANEL_UNDER_BED - BATTEN_H     # 186 == BENCH_RAIL_BOTTOM
BATTEN_Z0_TABLE = PANEL_UNDER_TABLE - BATTEN_H # 409
# The walking zone under the ladder bay: floor to the bench rail underside. The
# battens are not allowed into it in either mode.
WALK_ZONE_Z = (0, BENCH_RAIL_BOTTOM)           # 0 .. 186

# D10: the bed-mode panel top is deliberately 16 mm BELOW the bench tops. The
# fold-out seat cushions are what turn the three zones into one sleeping
# surface, and this is the recess they fold down into - a panel flush with the
# bench slats would leave the cushions standing proud of it instead.
PANEL_BENCH_DIP = BENCH_TOP - PANEL_TOP_BED    # 16

# BACK TABLE LEDGER (21x95), permanently mounted in both modes, screwed to the
# inner faces of the two back corner posts (Y -48..-27).
# NOTE (deviation, back ledger): the original spec placed it at Y 0..21, but
# nothing exists in that plane at this height, so the board would float.
# It now spans the full 1894 mm between corner posts. It only picks up the
# panel's rear edge (a 680 mm wide load band at midspan): at a 0.55 kN table
# load, half of it on the rear bearing, M = 89 kNmm against W = 21*95^2/6 =
# 31 587 mm3, so sigma ~ 2.8 MPa -> utilisation ~0.17, deflection ~2 mm. The
# long span is a non-issue because the board is on EDGE for this load.
#
# D9: the ledger moves up 16 mm, to Z 387..482, so its TOP is the table-mode
# panel underside itself - level with rung 2, no hook step in between. Its
# 21 mm width is the depth of the rear bearing.
LEDGER_BACK_Z1 = PANEL_UNDER_TABLE             # 482
LEDGER_BACK_Z0 = LEDGER_BACK_Z1 - BOARD_W      # 387
LEDGER_BACK_Y0 = BACK_POST_Y1                  # -48 .. -27, on the back posts

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
CUT_LIST = {}


def block(x0, y0, z0, dx, dy, dz, label, group, cut=None):
    """Axis aligned Box given by its minimum corner and its extents.

    `group` picks the colour group (see GROUP_COLORS) and drives the
    per-material STL export used by the .usdz pipeline.
    `cut` is (cut-list name, "section", length) and adds one piece to the cut
    list. Mirrored / repeated parts share a cut-list name so they merge.
    """
    b = Box(dx, dy, dz).moved(Location((x0 + dx / 2, y0 + dy / 2, z0 + dz / 2)))
    b.label = label
    b.color = GROUP_COLORS[group]
    b.group = group
    b.extents = ((x0, x0 + dx), (y0, y0 + dy), (z0, z0 + dz))
    if cut is not None:
        name, section, length = cut
        key = (name, section, round(length))
        CUT_LIST[key] = CUT_LIST.get(key, 0) + 1
    return b


def write_svg(comp, path, direction):
    """Hidden-line-removed projection of `comp` seen from `direction`."""
    bb = comp.bounding_box()
    center = bb.center()
    diag = bb.diagonal
    origin = (center.X + direction[0] * diag * 4,
              center.Y + direction[1] * diag * 4,
              center.Z + direction[2] * diag * 4)
    visible, _hidden = comp.project_to_viewport(
        viewport_origin=origin,
        viewport_up=(0, 0, 1),
        look_at=(center.X, center.Y, center.Z),
    )
    exporter = ExportSVG(scale=0.5, line_weight=0.15, margin=10)
    exporter.add_layer("visible")
    exporter.add_shape(visible, layer="visible")
    exporter.write(path)


def sec(a, b):
    return f"{int(a)}x{int(b)}"


# ---------------------------------------------------------------------------
# UPPER BED
# ---------------------------------------------------------------------------
parts = []

back_rail = block(THROUGH_X0, BACK_RAIL_Y0, RAIL_BOTTOM, THROUGH_LEN, RAIL_T,
                  RAIL_H, "Upper Side Rail Back", "rails",
                  ("Upper side rail", sec(RAIL_T, RAIL_H), THROUGH_LEN))
front_rail = block(THROUGH_X0, FRONT_RAIL_Y0, RAIL_BOTTOM, THROUGH_LEN, RAIL_T,
                   RAIL_H, "Upper Side Rail Front", "rails",
                   ("Upper side rail", sec(RAIL_T, RAIL_H), THROUGH_LEN))
parts += [back_rail, front_rail]

# D5: no slat cleats any more. The slats lie straight on top of both rails.

# Slats across Y, evenly spaced along X inside 20..1970. One 5x60 screw per
# end, down through the slat into the rail below it.
slat_pitch = (SLAT_X_END - SLAT_X_START - BED_SLAT_W) / (SLAT_COUNT - 1)
slat_gap = slat_pitch - BED_SLAT_W
slat_end_gap = min(SLAT_X_START, WALL_SPAN - SLAT_X_END)
assert slat_gap <= MAX_SLAT_GAP, f"slat gap {slat_gap:.1f} > {MAX_SLAT_GAP}"
assert slat_end_gap <= MAX_SLAT_GAP, f"slat end gap {slat_end_gap} > {MAX_SLAT_GAP}"

bed_slats = []
for i in range(SLAT_COUNT):
    x0 = SLAT_X_START + i * slat_pitch
    bed_slats.append(block(x0, SLAT_Y0, SLAT_Z0, BED_SLAT_W, SLAT_LEN, BED_SLAT_T,
                           f"Bed Slat_{i + 1}", "boards",
                           ("Upper bed slat (D5)",
                            sec(BED_SLAT_T, BED_SLAT_W), SLAT_LEN)))
parts += bed_slats

mattress = block(0, MATTRESS_Y0, MATTRESS_Z0, WALL_SPAN, MATTRESS_W, MATTRESS_H,
                 "Mattress 200x80 (reference)", "mattress")

# ---------------------------------------------------------------------------
# POSTS  (four corner posts - D1 deleted the two intermediate back posts)
# ---------------------------------------------------------------------------
for i, x0 in enumerate(CORNER_POST_X):
    side = "Left" if i == 0 else "Right"
    parts.append(block(x0, BACK_POST_Y0, 0, POST_W, POST_T, POST_HEIGHT,
                       f"Corner Post Back {side}", "posts",
                       ("Corner post", sec(POST_T, POST_W), POST_HEIGHT)))
    parts.append(block(x0, FRONT_POST_Y0, 0, POST_W, POST_T, POST_HEIGHT,
                       f"Corner Post Front {side}", "posts",
                       ("Corner post", sec(POST_T, POST_W), POST_HEIGHT)))

# ---------------------------------------------------------------------------
# END BEAMS
# ---------------------------------------------------------------------------
# One 48x98 beam per end. Bolted to the inner faces of the corner posts, top
# flush with the rail underside so both side rails bear on it.
for i, x0 in enumerate(END_BEAM_X):
    side = "Left" if i == 0 else "Right"
    parts.append(block(x0, END_BEAM_Y0, END_BEAM_Z0, RAIL_T, END_BEAM_LEN, RAIL_H,
                       f"End Beam {side}", "rails",
                       ("End beam", sec(RAIL_T, RAIL_H), END_BEAM_LEN)))
    # C2 / J1-B: bearing block under each end of the beam, on the post face.
    for name, by0 in (("Back", BACK_POST_Y0), ("Front", FRONT_POST_Y0)):
        parts.append(block(x0, by0, BEAM_BLOCK_Z0,
                           BEAM_BLOCK_DX, BEAM_BLOCK_DY, BEAM_BLOCK_DZ,
                           f"End Beam Bearing Block {side} {name}", "boards",
                           ("Bearing block, end beam (C2)",
                            sec(BLOCK_T, BLOCK_H), BEAM_BLOCK_LEN)))

# ---------------------------------------------------------------------------
# LADDER
# ---------------------------------------------------------------------------
for name, x0 in (("Left", LADDER_LEFT_X), ("Right", LADDER_RIGHT_X)):
    parts.append(block(x0, LADDER_Y0, 0, UPRIGHT_W, UPRIGHT_T, POST_HEIGHT,
                       f"Ladder Upright {name}", "posts",
                       ("Ladder upright (D13)", sec(UPRIGHT_W, UPRIGHT_T),
                        POST_HEIGHT)))

# Cleat blocks first: the rung rests on the blocks and is screwed down into
# them, and the blocks are screwed to the inner face of each upright.
for i, top in enumerate(RUNG_TOPS):
    for j, bx0 in enumerate(RUNG_BLOCK_X):
        parts.append(block(bx0, RUNG_Y0, top - RUNG_T - RUNG_BLOCK_H,
                           RUNG_BLOCK_T, RUNG_BLOCK_LEN, RUNG_BLOCK_H,
                           f"Rung Block {'Left' if j == 0 else 'Right'}_{i + 1}",
                           "boards",
                           ("Ladder rung block", sec(RUNG_BLOCK_T, RUNG_BLOCK_H),
                            RUNG_BLOCK_LEN)))
    parts.append(block(LADDER_INNER_L, RUNG_Y0, top - RUNG_T,
                       RUNG_LEN, RUNG_D, RUNG_T,
                       f"Ladder Rung_{i + 1}", "boards",
                       ("Ladder rung (tread)", sec(RUNG_T, RUNG_D), RUNG_LEN)))

# ---------------------------------------------------------------------------
# GUARD RAILS
# ---------------------------------------------------------------------------
# BACK  (D1): two full-length 34x98 boards on the outer faces of the back
#             corner posts - they now span 1894 mm unaided.
# FRONT (D2): four segments, two per band, lapped onto the ladder uprights and
#             stopping flush with the upright inner faces, so the 420 mm
#             climb-through opening runs all the way up.
# D7: front and back are now the same 34x98 board.
# D6: the two bands sit at 1412..1510 and 1585..1683 (see GUARD_BAND_Z0).
for i, z0 in enumerate(GUARD_BAND_Z0):
    parts.append(block(THROUGH_X0, BACK_GUARD_Y0, z0,
                       THROUGH_LEN, GUARD_T, GUARD_W,
                       f"Guard Rail Back_{i + 1}", "boards",
                       ("Guard rail, back (D1 upgrade)",
                        sec(GUARD_T, GUARD_W), THROUGH_LEN)))
    for j, (sx0, sx1) in enumerate(FRONT_GUARD_SEGMENTS):
        side = "Left" if j == 0 else "Right"
        parts.append(block(sx0, FRONT_GUARD_Y0, z0,
                           sx1 - sx0, GUARD_T, GUARD_W,
                           f"Guard Rail Front {side}_{i + 1}", "boards",
                           ("Guard rail, front segment (D2/D7/D13)",
                            sec(GUARD_T, GUARD_W), sx1 - sx0)))

# ---------------------------------------------------------------------------
# LOWER SECTION: BENCHES
# ---------------------------------------------------------------------------
# C5: 48x73 bench rails at Z 186..259, one per Y plane, each carried at its ends
# by a corner post (via the J9-B bearing block) and in between by two stub legs.
# They give the loose panel an edge to rest on in bed mode and give the ladder
# uprights a low fixing point.
# D11/D13: the BACK rail is the continuous 1984 mm member; the FRONT one is two
# 642 mm segments that stop at the sofa ends on their stub legs, so the whole
# front floor between the benches is open.
for i, ry0 in enumerate(BENCH_RAIL_Y):
    name = "Back" if i == 0 else "Front"
    if i == 0:
        parts.append(block(THROUGH_X0, ry0, BENCH_RAIL_BOTTOM, THROUGH_LEN,
                           BENCH_RAIL_T, BENCH_RAIL_H,
                           "Bench Rail Back (continuous)", "rails",
                           ("Bench rail, back (C5)",
                            sec(BENCH_RAIL_T, BENCH_RAIL_H), THROUGH_LEN)))
    else:
        for j, (sx0, sx1) in enumerate(FRONT_BENCH_RAIL_SEGMENTS):
            side = "Left" if j == 0 else "Right"
            parts.append(block(sx0, ry0, BENCH_RAIL_BOTTOM, sx1 - sx0,
                               BENCH_RAIL_T, BENCH_RAIL_H,
                               f"Bench Rail Front {side} (segment)", "rails",
                               ("Bench rail, front segment (D13)",
                                sec(BENCH_RAIL_T, BENCH_RAIL_H), sx1 - sx0)))
    # C2 / J9-B: bearing block under each rail end, on the corner post face.
    for j, px0 in enumerate(CORNER_POST_X):
        side = "Left" if j == 0 else "Right"
        parts.append(block(px0, RAIL_BLOCK_Y0[i], RAIL_BLOCK_Z0,
                           RAIL_BLOCK_DX, RAIL_BLOCK_DY, RAIL_BLOCK_DZ,
                           f"Bench Rail Bearing Block {name} {side}", "boards",
                           ("Bearing block, bench rail (C2)",
                            sec(BLOCK_T, BLOCK_H), RAIL_BLOCK_DX)))
    # Stub legs at the inner end of each bench (the outer ends sit on the posts).
    for j, lx0 in enumerate(STUB_LEG_X):
        side = "Left" if j == 0 else "Right"
        parts.append(block(lx0, ry0, 0, LEG_W, LEG_T, STUB_LEG_H,
                           f"Bench Stub Leg {name} {side}", "posts",
                           ("Bench stub leg", sec(LEG_T, LEG_W), STUB_LEG_H)))

# C3: 34x98 bench slats on top of the continuous rails, five per bench.
# The doc's J11 table lists the right-hand bench at X 1345..1993, which runs 3 mm
# past the wall; the positions here are the exact mirror of the left bench.
for i in range(len(BENCH_X)):
    side = "Left" if i == 0 else "Right"
    for j in range(BENCH_SLAT_COUNT):
        off = j * BENCH_SLAT_PITCH
        x0 = off if i == 0 else WALL_SPAN - BENCH_SLAT_W - off
        parts.append(block(x0, BENCH_SLAT_Y0, BENCH_RAIL_TOP,
                           BENCH_SLAT_W, BENCH_SLAT_LEN, BENCH_SLAT_T,
                           f"Bench Slat {side}_{j + 1}", "boards",
                           ("Bench slat (C3)", sec(BENCH_SLAT_T, BENCH_SLAT_W),
                            BENCH_SLAT_LEN)))

# D3: only the BACK table ledger survives. The front one used to cross the
# whole front of both sofa benches at shin height, right where you sit down,
# and it is replaced by resting the panel's front edge on a ladder rung (D10).
support_rail = block(THROUGH_X0, LEDGER_BACK_Y0, LEDGER_BACK_Z0, THROUGH_LEN,
                     BOARD_T, BOARD_W, "Table Ledger Back", "boards",
                     ("Table ledger, back", sec(BOARD_T, BOARD_W), THROUGH_LEN))
parts.append(support_rail)

# ---------------------------------------------------------------------------
# MOVABLE PANEL
# ---------------------------------------------------------------------------
# See the D10 note above for what it rests on. NOTE (deviation): the doc's cut
# list gives the panel as 680 x 860 at Y 30..890, inside the ladder uprights
# (floor to ceiling) which the panel X range 655..1335 straddles - a hard
# collision. The panel front edge is kept flush against the uprights' back
# plane; D10 then takes the rear edge back to Y -48 so that it reaches the back
# bench rail and the ledger. D12 makes that 680 x 800, Y -48..752.
panel_bed = block(PANEL_X0, PANEL_Y0, PANEL_UNDER_BED,
                  PANEL_W, PANEL_LEN, PANEL_T,
                  "Movable Panel (bed mode)", "panel",
                  ("Movable panel", f"{PANEL_T} panel, {PANEL_W} wide", PANEL_LEN))
panel_table = block(PANEL_X0, PANEL_Y0, PANEL_UNDER_TABLE,
                    PANEL_W, PANEL_LEN, PANEL_T,
                    "Movable Panel (table mode)", "panel")

# M4: the two stiffener battens. They are SCREWED TO THE PANEL, so they are not
# part of the fixed structure - they move with it and are built once per mode,
# alongside the panel they hang under. Only the bed-mode pair carries the cut
# entry; it is the same two pieces in both modes.
battens_bed = []
battens_table = []
for i, bx0 in enumerate(BATTEN_X):
    side = "Left" if i == 0 else "Right"
    battens_bed.append(block(bx0, BATTEN_Y0, BATTEN_Z0_BED,
                             BATTEN_W, BATTEN_LEN, BATTEN_H,
                             f"Panel Stiffener Batten {side} (bed mode)", "panel",
                             ("Panel stiffener batten (M4)",
                              sec(BATTEN_W, BATTEN_H), BATTEN_LEN)))
    battens_table.append(block(bx0, BATTEN_Y0, BATTEN_Z0_TABLE,
                               BATTEN_W, BATTEN_LEN, BATTEN_H,
                               f"Panel Stiffener Batten {side} (table mode)",
                               "panel"))

# ---------------------------------------------------------------------------
# ASSEMBLY
# ---------------------------------------------------------------------------
IDENTITY = Location((0, 0, 0))
# Z-up (CAD) -> Y-up (Quick Look / glTF / USD): a -90 deg turn about X.
Y_UP = Location((0, 0, 0), (1, 0, 0), -90)

MODES = {"bed_mode": panel_bed, "table_mode": panel_table}
# M4: the panel sub-assembly - the panel plus the battens screwed under it.
PANEL_BATTENS = {id(panel_bed): battens_bed, id(panel_table): battens_table}


def mode_parts(panel):
    return parts + [mattress, panel] + PANEL_BATTENS[id(panel)]


def make_compound(panel, xform=IDENTITY):
    return Compound(children=[p.moved(xform) for p in mode_parts(panel)])


bed_mode = make_compound(panel_bed)
table_mode = make_compound(panel_table)

# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------
TOL = 0.1
print("\n=== VALIDATION ===")

# D12: the depth envelope. The BACK face is the fixed datum - the back guard
# boards at Y -130 - and the front face is the front guard boards. The whole
# depth stack came in 106 mm on the front side only, so the overall depth over
# the guards drops 1070 -> 964 and the back plane must not have moved a micron.
DEPTH_Y0 = BACK_GUARD_Y0                       # -130, FIXED datum
DEPTH_Y1 = FRONT_GUARD_Y1                      # 834  [was 940]
OVERALL_DEPTH = DEPTH_Y1 - DEPTH_Y0            # 964  [was 1070]
for name, comp in (("bed mode", bed_mode), ("table mode", table_mode)):
    bb = comp.bounding_box()
    assert bb.min.X >= -TOL, f"{name}: geometry crosses wall at X=0 ({bb.min.X:.3f})"
    assert bb.max.X <= WALL_SPAN + TOL, \
        f"{name}: geometry crosses wall at X={WALL_SPAN} ({bb.max.X:.3f})"
    assert bb.max.Z <= POST_HEIGHT + TOL, \
        f"{name}: something is taller than the {POST_HEIGHT} mm posts ({bb.max.Z:.3f})"
    assert abs(bb.min.Y - DEPTH_Y0) < TOL, \
        f"{name}: the BACK plane moved - Y min is {bb.min.Y:.3f}, must stay " \
        f"{DEPTH_Y0} (D12 shrinks the FRONT only)"
    assert bb.max.Y <= DEPTH_Y1 + TOL, \
        f"{name}: something sticks out past the front guards ({bb.max.Y:.3f} > " \
        f"{DEPTH_Y1})"
    print(f"OK  {name}: X extent {bb.min.X:.2f} .. {bb.max.X:.2f} "
          f"(limit 0 .. {WALL_SPAN}), top Z {bb.max.Z:.0f} (limit {POST_HEIGHT}), "
          f"Y extent {bb.min.Y:.0f} .. {bb.max.Y:.0f} = {bb.max.Y - bb.min.Y:.0f} "
          f"mm deep (D12: was 1070, back plane {DEPTH_Y0} unmoved)")
assert OVERALL_DEPTH == 964 and DEPTH_SHRINK == 106

# C9: nothing horizontal may be longer than 1984, and every through-running
# member must sit at X 3..1987. A 1990 mm piece cannot be swung into a 1990 mm
# opening, so the envelope assert above is necessary but not sufficient.
long_members = []
for p in parts + [panel_bed, panel_table]:
    (x0, x1), _, _ = p.extents
    dx = x1 - x0
    assert dx <= THROUGH_LEN + TOL, \
        f"'{p.label}' is {dx:.1f} mm long in X - cannot be manoeuvred into the " \
        f"{WALL_SPAN} mm opening (max {THROUGH_LEN})"
    if dx > POST_HEIGHT / 2:                      # a through-running member
        assert abs(x0 - THROUGH_X0) < TOL and abs(x1 - THROUGH_X1) < TOL, \
            f"'{p.label}' spans {x0}..{x1}, expected {THROUGH_X0}..{THROUGH_X1}"
        long_members.append(p.label)
# D11 ripple: the front bench rail has LEFT this list - it is two 782 mm
# segments now, in the same class as the D2 front guard segments. The back bench
# rail, the two side rails, the two back guards and the table ledger are the six
# that remain.
assert not any("Bench Rail Front" in m for m in long_members), \
    "D11: the front bench rail must not be a through-running member any more"
assert "Bench Rail Back (continuous)" in long_members, \
    "C5: the back bench rail must still run wall to wall"
print(f"OK  no horizontal member exceeds {THROUGH_LEN} mm; all "
      f"{len(long_members)} through members centred at "
      f"X {THROUGH_X0}..{THROUGH_X1} (C9): "
      + ", ".join(sorted(long_members)))

# D1: exactly SIX floor-to-top verticals - 4 corner posts + 2 ladder uprights.
verticals = [p for p in parts
             if p.extents[2] == (0, POST_HEIGHT)]
corner_posts = [p for p in verticals if p.label.startswith("Corner Post")]
uprights = [p for p in verticals if p.label.startswith("Ladder Upright")]
assert len(verticals) == 6, \
    f"D1: expected 6 full-height verticals, found {len(verticals)}: " \
    f"{[p.label for p in verticals]}"
assert len(corner_posts) == 4 and len(uprights) == 2
assert not any(p.label.startswith("Back Post Mid") for p in parts), \
    "D1: the intermediate back posts are supposed to be gone"
# D13: the two families no longer share a section - corner posts are 48x48,
# ladder uprights 36x48 (36 in X, 48 in Y so the bolting face is unchanged).
for p in verticals:
    (x0, x1), (y0, y1), _ = p.extents
    want_w = UPRIGHT_W if p.label.startswith("Ladder Upright") else POST_W
    want_t = UPRIGHT_T if p.label.startswith("Ladder Upright") else POST_T
    assert x1 - x0 == want_w, f"'{p.label}' is {x1 - x0} wide in X, want {want_w}"
    assert y1 - y0 == want_t, f"'{p.label}' is {y1 - y0} deep in Y, want {want_t}"
    assert 0 <= x0 and x1 <= WALL_SPAN
for u in uprights:
    assert u.extents[1] == (LADDER_Y0, LADDER_Y1), \
        f"'{u.label}' is not in the front rail plane for bolting"
print(f"OK  D1: exactly 6 verticals x {POST_HEIGHT} mm - 4 corner posts "
      f"({sec(POST_T, POST_W)}) + 2 ladder uprights ({sec(UPRIGHT_W, UPRIGHT_T)}, "
      f"D13: {UPRIGHT_W} along X / {UPRIGHT_T} along Y, the {UPRIGHT_T} face on "
      f"the front rail plane Y={LADDER_Y0}), no intermediate back posts")

# D4: the post section is the slim one, but the wall faces and the ladder
# opening are exactly where they always were.
assert [p.extents[0] for p in sorted(corner_posts, key=lambda q: q.extents[0][0])][0] \
    == (0, POST_W)
assert sorted(corner_posts, key=lambda q: q.extents[0][0])[-1].extents[0] \
    == (WALL_SPAN - POST_W, WALL_SPAN)
up = sorted(uprights, key=lambda q: q.extents[0][0])
assert up[0].extents[0] == (LADDER_INNER_L - UPRIGHT_W, LADDER_INNER_L)
assert up[1].extents[0] == (LADDER_INNER_R, LADDER_INNER_R + UPRIGHT_W)
assert up[1].extents[0][0] - up[0].extents[0][1] == LADDER_CLEAR
# D13: still centred on 995 and still wide enough to climb through.
assert (up[0].extents[0][1] + up[1].extents[0][0]) / 2 == LADDER_CENTER_X, \
    "D13: the ladder opening is not symmetric about X 995"
assert LADDER_CLEAR >= MIN_LADDER_CLEAR, \
    f"D13: {LADDER_CLEAR} mm clear ladder is under the {MIN_LADDER_CLEAR} limit"
print(f"OK  D4: posts flush with the walls at X 0..{POST_W} / "
      f"{WALL_SPAN - POST_W}..{WALL_SPAN}; D13 ladder clear opening "
      f"{LADDER_CLEAR} mm (min {MIN_LADDER_CLEAR}) between X "
      f"{LADDER_INNER_L:.0f} and {LADDER_INNER_R:.0f}, upright outer faces "
      f"{up[0].extents[0][0]:.0f} / {up[1].extents[0][1]:.0f}, centred on "
      f"{LADDER_CENTER_X}")

# Fixed heights. Everything below the platform is untouched by D5/D6/D7; the
# platform stack itself is the thing that moved.
assert RAIL_BOTTOM == 1065 and RAIL_TOP == 1163
assert not any("Cleat" in p.label for p in parts), "D5: the slat cleats must be gone"
assert (SLAT_Z0, SLAT_Z1) == (1163, 1197), "D5: slats not flush on top of the rails"
assert (MATTRESS_Z0, MATTRESS_Z1) == (1197, 1337)
assert (BENCH_RAIL_BOTTOM, BENCH_RAIL_TOP) == (186, 259)
assert BENCH_TOP == 293 and PANEL_TOP_BED == 277 and PANEL_UNDER_BED == 259
assert PANEL_TOP_TABLE == 500 and PANEL_UNDER_TABLE == 482
assert RUNG_TOPS == [259, 482, 720, 958] and POST_HEIGHT == 1700
assert (LEDGER_BACK_Z0, LEDGER_BACK_Z1) == (387, 482)
print("OK  invariant heights held: rail underside 1065, rail top 1163, no "
      "cleats, slats 1163..1197 (flush on the rails), mattress 1197..1337, "
      "bench 186/259/293, ledger 387..482, rungs 259/482/720/958, panel "
      "259..277 (bed) / 482..500 (table), total 1700")

# D12: the depth planes. The back half is the FIXED datum and must be exactly
# where v7 left it; every front plane is exactly 106 mm in from where it was.
assert (BACK_GUARD_Y0, BACK_GUARD_Y1) == (-130, -96), "D12: the back guard plane moved"
assert (BACK_POST_Y0, BACK_POST_Y1) == (-96, -48), "D12: the back post plane moved"
assert (BACK_RAIL_Y0, BACK_RAIL_Y1) == (-48, 0), "D12: the back rail plane moved"
assert LEDGER_BACK_Y0 == -48, "D12: the back ledger plane moved"
FRONT_PLANES_V7 = {                      # v7 value -> v8 value, all -106
    "front side rail": ((810, 858), (FRONT_RAIL_Y0, FRONT_RAIL_Y1)),
    "front bench rail": ((810, 858), (BENCH_RAIL_Y[1], BENCH_RAIL_Y[1] + BENCH_RAIL_T)),
    "front posts": ((858, 906), (FRONT_POST_Y0, FRONT_POST_Y1)),
    "ladder uprights": ((858, 906), (LADDER_Y0, LADDER_Y1)),
    "rung treads": ((833, 906), (RUNG_Y0, RUNG_Y1)),
    "front guards": ((906, 940), (FRONT_GUARD_Y0, FRONT_GUARD_Y1)),
    "slats / bench slats / panel front": ((858, 858), (SLAT_Y1, PANEL_Y1)),
}
for what, ((o0, o1), (n0, n1)) in FRONT_PLANES_V7.items():
    assert (o0 - n0, o1 - n1) == (DEPTH_SHRINK, DEPTH_SHRINK), \
        f"D12: '{what}' moved {o0 - n0}/{o1 - n1}, not {DEPTH_SHRINK}/{DEPTH_SHRINK}"
assert (SLAT_Y0, SLAT_Y1) == (-48, 752) and SLAT_LEN == PLATFORM_DEPTH == 800
assert BENCH_SLAT_LEN == SLAT_LEN and PANEL_LEN == SLAT_LEN
assert END_BEAM_LEN == 896 and (END_BEAM_Y0, END_BEAM_Y1) == (-96, 800)
assert RUNG_REST_LEDGE == 25, \
    f"D12: the rung rest ledge is {RUNG_REST_LEDGE} mm, must stay 25"
print(f"OK  D12: back planes unmoved (guards {BACK_GUARD_Y0}, posts "
      f"{BACK_POST_Y0}, rail {BACK_RAIL_Y0}); every front plane in by exactly "
      f"{DEPTH_SHRINK} mm - rail {FRONT_RAIL_Y0}..{FRONT_RAIL_Y1}, posts/uprights "
      f"{FRONT_POST_Y0}..{FRONT_POST_Y1}, rungs {RUNG_Y0}..{RUNG_Y1} "
      f"({RUNG_REST_LEDGE} mm rest ledge kept), guards {FRONT_GUARD_Y0}.."
      f"{FRONT_GUARD_Y1}; platform/slats/bench slats/panel {PLATFORM_DEPTH} mm, "
      f"end beams {END_BEAM_LEN} mm, overall depth {OVERALL_DEPTH} mm")

# Inner clear width between the upper side rails
clear = FRONT_RAIL_Y0 - BACK_RAIL_Y1
assert abs(clear - INNER_CLEAR_WIDTH) < 1e-9, f"inner clear width is {clear}"
assert abs((front_rail.extents[1][0] - back_rail.extents[1][1]) - INNER_CLEAR_WIDTH) < 1e-9
print(f"OK  inner clear width between upper rails = {clear} mm")

# The ends must be completely open above the platform: no part above the slats
# may reach into the clear width between the two side rails.
for p in parts:
    (_, _), (y0, y1), (_, z1) = p.extents
    if z1 > SLAT_Z1:
        assert y1 <= BACK_RAIL_Y1 or y0 >= FRONT_RAIL_Y0, \
            f"'{p.label}' reaches into the sleeping area above the platform"
print("OK  both ends fully open above the platform (no upper end boards)")

# D4: both side rails must land on both end beams - including in X, which the
# post slimming (beams moved 73..121 -> 48..96) could have broken.
for beam in (p for p in parts if p.label.startswith("End Beam ")
             and "Block" not in p.label):
    assert beam.extents[2] == (END_BEAM_Z0, RAIL_BOTTOM), \
        "end beam top not flush with rail underside"
    for rail in (back_rail, front_rail):
        assert rail.extents[1][0] >= beam.extents[1][0] and \
            rail.extents[1][1] <= beam.extents[1][1], "rail not carried by the end beam"
        bear = min(rail.extents[0][1], beam.extents[0][1]) - \
            max(rail.extents[0][0], beam.extents[0][0])
        assert bear >= RAIL_T - TOL, \
            f"'{rail.label}' only bears {bear:.1f} mm on '{beam.label}' in X"
print(f"OK  end beams {sec(RAIL_T, RAIL_H)} x {END_BEAM_LEN} at Z "
      f"{END_BEAM_Z0}..{RAIL_BOTTOM} carry both side rails "
      f"(full {RAIL_T} mm bearing in X, beams at X {END_BEAM_X[0]} / {END_BEAM_X[1]})")

# C2: every end-beam end and every bench-rail end must sit on a bearing block,
# so the vertical load is wood-on-wood and the M8 bolts are pure ties.
beam_blocks = [p for p in parts if "End Beam Bearing Block" in p.label]
rail_blocks = [p for p in parts if "Bench Rail Bearing Block" in p.label]
assert len(beam_blocks) == 4 and len(rail_blocks) == 4, "missing C2 bearing blocks"
for b in beam_blocks:
    assert abs(b.extents[2][1] - END_BEAM_Z0) < TOL, "J1-B block top not at the beam underside"
rail_x_spans = [p.extents[0] for p in parts
                if "Bench Rail" in p.label and "Block" not in p.label]
rail_bearings = []
for b in rail_blocks:
    assert abs(b.extents[2][1] - BENCH_RAIL_BOTTOM) < TOL, \
        "J9-B block top not at the bench rail underside"
    # D13 ripple: the front rail is two SHORT segments now, so this can no
    # longer be checked against the through span - it has to be checked against
    # the actual rail piece that lands on this block.
    bear = max(min(rx1, b.extents[0][1]) - max(rx0, b.extents[0][0])
               for rx0, rx1 in rail_x_spans)
    assert bear >= 40, f"bench rail only bears {bear:.0f} mm on '{b.label}'"
    rail_bearings.append(bear)
print(f"OK  C2: 4 J1-B blocks under the end beams (top Z={END_BEAM_Z0}) and "
      f"4 J9-B blocks under the bench rails (top Z={BENCH_RAIL_BOTTOM}, "
      f"{min(rail_bearings):.0f}..{max(rail_bearings):.0f} mm bearing in X "
      f"against the real rail piece)")

# D1: the back guard boards are the upgraded 34x98 stock, full span, mounted on
# the outer faces of the back corner posts.
back_guards = [p for p in parts if p.label.startswith("Guard Rail Back")]
assert len(back_guards) == 2, "expected two back guard boards"
for g, z0 in zip(sorted(back_guards, key=lambda p: p.extents[2][0]), GUARD_BAND_Z0):
    assert g.extents[0] == (THROUGH_X0, THROUGH_X1)
    assert g.extents[1] == (BACK_GUARD_Y0, BACK_GUARD_Y1), "back guard not on the post faces"
    assert g.extents[2] == (z0, z0 + GUARD_W), "back guard Z band wrong"
back_span = CORNER_POST_X[1] - POST_W          # 1894, post inner face to inner face
print(f"OK  D1: back guards {sec(GUARD_T, GUARD_W)} x {THROUGH_LEN} at "
      f"Y {BACK_GUARD_Y0}..{BACK_GUARD_Y1}, Z {GUARD_BAND_Z0[0]}.."
      f"{GUARD_BAND_Z0[0] + GUARD_W} and {GUARD_BAND_Z0[1]}.."
      f"{GUARD_BAND_Z0[1] + GUARD_W}; single {back_span} mm span "
      f"(utilisation ~0.78, was 1.99 in 21x95)")

# D2: four front guard segments, leaving exactly the ladder opening, each one
# lapped onto a corner post at one end and a ladder upright at the other.
front_guards = [p for p in parts if p.label.startswith("Guard Rail Front")]
assert len(front_guards) == 4, f"expected 4 front guard segments, got {len(front_guards)}"
post_x_ranges = [p.extents[0] for p in parts if p.label.startswith("Corner Post Front")]
up_x_ranges = [p.extents[0] for p in up]
for g in front_guards:
    (x0, x1), y, z = g.extents
    # D7: same board as the back guards, still landing flat on the plane
    # Y = 906 (the front faces of the corner posts and the ladder uprights).
    assert y == (FRONT_GUARD_Y0, FRONT_GUARD_Y1)
    assert y[1] - y[0] == GUARD_T and z[1] - z[0] == GUARD_W, \
        f"'{g.label}' is not {sec(GUARD_T, GUARD_W)}"
    assert y[0] == FRONT_POST_Y1, \
        f"'{g.label}' does not lie on the post/upright front face plane Y={FRONT_POST_Y1}"
    assert x1 - x0 == FRONT_GUARD_SEG_LEN, f"'{g.label}' is {x1 - x0} long"
    lap_post = max(min(x1, a1) - max(x0, a0) for a0, a1 in post_x_ranges)
    lap_up = max(min(x1, a1) - max(x0, a0) for a0, a1 in up_x_ranges)
    assert lap_post >= POST_W - THROUGH_X0, f"'{g.label}' barely laps a corner post"
    # D13: the upright is 36 wide now, so the lap is 36 - still the FULL width
    # of the upright, which is what the detail asks for.
    assert lap_up >= UPRIGHT_W, \
        f"'{g.label}' does not fully lap a ladder upright ({lap_up})"
    # full FACE contact over the whole lap and the whole board width, not an
    # edge kiss: the lap area is (X overlap) x (board width in Z).
    assert lap_post * GUARD_W >= (POST_W - THROUGH_X0) * GUARD_W
    assert lap_up * GUARD_W >= UPRIGHT_W * GUARD_W
for z0 in GUARD_BAND_Z0:
    band = sorted((g for g in front_guards if g.extents[2][0] == z0),
                  key=lambda p: p.extents[0][0])
    assert len(band) == 2
    gap = band[1].extents[0][0] - band[0].extents[0][1]
    assert abs(gap - LADDER_CLEAR) < TOL, f"climb-through gap is {gap}, want {LADDER_CLEAR}"
    assert (band[0].extents[0][1], band[1].extents[0][0]) == (LADDER_INNER_L,
                                                              LADDER_INNER_R), \
        "D13: the guard segments must die on the upright inner faces"
print(f"OK  D2/D7/D13: 4 front guard segments {sec(GUARD_T, GUARD_W)} x "
      f"{FRONT_GUARD_SEG_LEN} at X {FRONT_GUARD_SEGMENTS[0][0]}.."
      f"{FRONT_GUARD_SEGMENTS[0][1]} / {FRONT_GUARD_SEGMENTS[1][0]}.."
      f"{FRONT_GUARD_SEGMENTS[1][1]}, Y {FRONT_GUARD_Y0}..{FRONT_GUARD_Y1}, "
      f"{UPRIGHT_W} x {GUARD_W} mm face lap on the uprights and "
      f"{POST_W - THROUGH_X0} x {GUARD_W} mm on the corner posts, clear "
      f"climb-through gap {LADDER_CLEAR} mm in both bands")

# D6: guard re-banding. Every opening measured ABOVE THE MATTRESS SURFACE has
# to be <= 75 mm (EN 747 entrapment), and the barrier has to stand at least
# 160 mm above the mattress.
guard_openings = [
    ("mattress top -> band 1", GUARD_BAND_Z0[0] - MATTRESS_Z1),
    ("band 1 -> band 2", GUARD_BAND_Z0[1] - (GUARD_BAND_Z0[0] + GUARD_W)),
    ("band 2 -> post tops", POST_HEIGHT - (GUARD_BAND_Z0[1] + GUARD_W)),
]
for what, o in guard_openings:
    assert o > 0, f"guard bands overlap or invert: {what} = {o}"
    assert o <= MAX_GUARD_OPENING + TOL, \
        f"EN 747 entrapment: opening '{what}' is {o} mm > {MAX_GUARD_OPENING}"
guard_over_mattress = GUARD_BAND_Z0[1] + GUARD_W - MATTRESS_Z1
assert guard_over_mattress >= MIN_GUARD_OVER_MATTRESS, \
    f"barrier only {guard_over_mattress} mm above the mattress"
# and both sides must actually be in those bands
for g in parts:
    if g.label.startswith("Guard Rail"):
        assert g.extents[2][0] in GUARD_BAND_Z0 and \
            g.extents[2][1] - g.extents[2][0] == GUARD_W, \
            f"'{g.label}' is not in one of the D6 guard bands"
print(f"OK  D6: guard bands Z {GUARD_BAND_Z0[0]}..{GUARD_BAND_Z0[0] + GUARD_W} "
      f"and {GUARD_BAND_Z0[1]}..{GUARD_BAND_Z0[1] + GUARD_W}; openings above "
      f"the mattress top ({MATTRESS_Z1}): "
      + " / ".join(f"{o:.0f}" for _, o in guard_openings)
      + f" mm (limit {MAX_GUARD_OPENING}), barrier {guard_over_mattress} mm "
      f"above the mattress (min {MIN_GUARD_OVER_MATTRESS})")

# C3/C5/D11: 34x98 bench slats on the bench rails - one continuous rail at the
# back, two lapped segments at the front - and the bed-mode panel sitting one
# cushion-thickness below the resulting bench top.
bench_rails = [p for p in parts if "Bench Rail" in p.label and "Block" not in p.label]
back_bench_rails = [p for p in bench_rails if p.label.startswith("Bench Rail Back")]
front_bench_rails = [p for p in bench_rails if p.label.startswith("Bench Rail Front")]
assert len(back_bench_rails) == 1, "C5: expected exactly one continuous back bench rail"
assert len(front_bench_rails) == 2, \
    f"D11: expected 2 front bench rail segments, got {len(front_bench_rails)}"
for r in bench_rails:
    assert r.extents[2] == (BENCH_RAIL_BOTTOM, BENCH_RAIL_TOP), \
        f"'{r.label}' is not at Z {BENCH_RAIL_BOTTOM}..{BENCH_RAIL_TOP}"
    assert r.extents[1][1] - r.extents[1][0] == BENCH_RAIL_T
assert back_bench_rails[0].extents[0] == (THROUGH_X0, THROUGH_X1), \
    "C5: the back bench rail must still run the full 1984 mm"
assert back_bench_rails[0].extents[1] == (BACK_RAIL_Y0, BACK_RAIL_Y1)
assert BENCH_TOP == BENCH_RAIL_TOP + BENCH_SLAT_T == 293
assert PANEL_BENCH_DIP == 16 and PANEL_TOP_BED == BENCH_TOP - PANEL_BENCH_DIP, \
    "D10: the bed-mode panel should sit 16 mm below the bench tops"
print(f"OK  C5: back bench rail {sec(BENCH_RAIL_T, BENCH_RAIL_H)} x "
      f"{THROUGH_LEN} at Z {BENCH_RAIL_BOTTOM}..{BENCH_RAIL_TOP}, on 2 posts + "
      f"2 stub legs")
print(f"OK  C3: bench slats {sec(BENCH_SLAT_T, BENCH_SLAT_W)}, bench top Z="
      f"{BENCH_TOP}, bed-mode panel {PANEL_UNDER_BED}..{PANEL_TOP_BED} "
      f"({PANEL_BENCH_DIP} mm below the bench tops - the cushion recess, D10)")

# D11/D13: the two front bench rail segments stop at the SOFA ends now. Each one
# must (a) still lap its corner post at the outer end, (b) land its inner end
# square on the stub leg that is already there, with the full leg width under it
# and no cantilever past it.
front_legs = [p for p in parts if p.label.startswith("Bench Stub Leg Front")]
assert len(front_legs) == 2
leg_x_ranges = [p.extents[0] for p in front_legs]
leg_bearings = []
for r in front_bench_rails:
    (x0, x1), (y0, y1), (z0, z1) = r.extents
    assert (y0, y1) == (FRONT_RAIL_Y0, FRONT_RAIL_Y1), \
        f"'{r.label}' is not in the front bench rail plane"
    assert x1 - x0 == FRONT_BENCH_RAIL_SEG_LEN, \
        f"'{r.label}' is {x1 - x0} long, expected {FRONT_BENCH_RAIL_SEG_LEN}"
    # D13: no more upright lap - the segment must not reach the ladder at all.
    for a0, a1 in (p.extents[0] for p in up):
        assert min(x1, a1) - max(x0, a0) <= TOL, \
            f"D13: '{r.label}' still touches a ladder upright"
    # the outer end must still land on its corner post
    lap_post = max(min(x1, a1) - max(x0, a0)
                   for a0, a1 in (p.extents[0] for p in corner_posts))
    assert lap_post >= POST_W - THROUGH_X0, f"'{r.label}' barely reaches a corner post"
    # the INNER end must be supported: a stub leg directly under it, full width,
    # and the segment must not overhang the leg's inner face.
    is_left = x0 == THROUGH_X0
    inner_end = x1 if is_left else x0
    leg = [(a0, a1) for a0, a1 in leg_x_ranges
           if abs((a1 if is_left else a0) - inner_end) < TOL]
    assert len(leg) == 1, \
        f"D13: '{r.label}' inner end at X {inner_end} is not on a stub leg"
    (a0, a1) = leg[0]
    bear = min(x1, a1) - max(x0, a0)
    assert abs(bear - LEG_W) < TOL, \
        f"D13: '{r.label}' only bears {bear} mm on its stub leg, want {LEG_W}"
    # cantilever measured at the INNER end only (the outer end runs on to its
    # corner post, which is the other support, not an overhang)
    overhang = max((x1 - a1) if is_left else (a0 - x0), 0.0)
    assert overhang <= TOL, \
        f"D13: '{r.label}' cantilevers {overhang} mm past its stub leg"
    leg_bearings.append(bear)
seg = sorted(front_bench_rails, key=lambda p: p.extents[0][0])
bay_gap = seg[1].extents[0][0] - seg[0].extents[0][1]
assert abs(bay_gap - (OPEN_FLOOR_X[1] - OPEN_FLOOR_X[0])) < TOL, \
    f"the open front floor is {bay_gap} mm wide, want " \
    f"{OPEN_FLOOR_X[1] - OPEN_FLOOR_X[0]}"
# D13: the empty region grows from "the ladder opening" to THE WHOLE FLOOR
# BETWEEN THE BENCHES - X 645..1345, from the front face of the back rail
# forward, floor to bench-rail top. The ladder's own members are excluded not by
# an X exclusion but by the Y bound: the uprights live at Y 752..800 and the
# rungs and rung blocks at Y 727..800, all at or beyond RUNG_Y0, so bounding the
# zone at RUNG_Y0 takes exactly "the ladder itself" out and nothing else.
# M4 NOTE: this loop runs over `parts` - the FIXED structure - and the stiffener
# battens are deliberately not in it, because they belong to the panel and lift
# out with it. They do occupy the top 73 mm of this box in bed mode (Z 186..259)
# by design: they hang under the panel, which is itself the ceiling of the bay
# at 259. What must stay empty for them is the WALKING zone, floor to Z 186 -
# checked separately in the M4 block above.
BAY = (OPEN_FLOOR_X, (BACK_RAIL_Y1, RUNG_Y0), (0, BENCH_RAIL_TOP))
for p in parts:
    inter = [min(a1, b1) - max(a0, b0) for (a0, a1), (b0, b1) in zip(p.extents, BAY)]
    assert min(inter) <= TOL, \
        f"D13: '{p.label}' crosses the open front floor between the benches"
# and the legs must still stand under their segment
for leg in front_legs:
    (lx0, lx1), _, _ = leg.extents
    assert any(sx0 <= lx0 and lx1 <= sx1 for sx0, sx1 in FRONT_BENCH_RAIL_SEGMENTS), \
        f"'{leg.label}' at X {lx0}..{lx1} no longer stands under a rail segment"
print(f"OK  D11/D13: front bench rail = 2 x {sec(BENCH_RAIL_T, BENCH_RAIL_H)} x "
      f"{FRONT_BENCH_RAIL_SEG_LEN} at X {FRONT_BENCH_RAIL_SEGMENTS[0][0]}.."
      f"{FRONT_BENCH_RAIL_SEGMENTS[0][1]} / {FRONT_BENCH_RAIL_SEGMENTS[1][0]}.."
      f"{FRONT_BENCH_RAIL_SEGMENTS[1][1]} (Y {FRONT_RAIL_Y0}..{FRONT_RAIL_Y1}), "
      f"inner ends end-bearing {min(leg_bearings):.0f} mm on their stub legs "
      f"with no cantilever, no contact with the ladder; front floor open "
      f"{bay_gap} mm (X {OPEN_FLOOR_X[0]}..{OPEN_FLOOR_X[1]}) from the floor to "
      f"the bench rail top, everywhere in front of the back rail")

# D13: WALK-AROUND. There must be a real passage on each side of the ladder,
# between the sofa end and the upright outer face, clear from the floor up to
# the table-mode panel line (482) across the whole front zone.
#
# The clear width is measured against FIXED STRUCTURE (`parts`). The loose panel
# is handled separately below: it is the seat / table surface, it lies at 259 in
# bed mode and 482 in table mode, and it does bridge the passage at that height
# by design - what matters is that it never touches the floor level you actually
# stand and put your feet in, which is checked explicitly afterwards.
PASSAGE_Y = (BACK_RAIL_Y1, FRONT_GUARD_Y1)           # 0 .. 834, front zone
PASSAGE_Z = (0, RUNG_TOPS[1])                        # 0 .. 482
PASSAGE_BANDS = [("left", OPEN_FLOOR_X[0], up[0].extents[0][0]),
                 ("right", up[1].extents[0][1], OPEN_FLOOR_X[1])]
passages = []
for side, bx0, bx1 in PASSAGE_BANDS:
    lo, hi = bx0, bx1
    for p in parts:
        (px0, px1), (py0, py1), (pz0, pz1) = p.extents
        if min(py1, PASSAGE_Y[1]) - max(py0, PASSAGE_Y[0]) <= TOL:
            continue
        if min(pz1, PASSAGE_Z[1]) - max(pz0, PASSAGE_Z[0]) <= TOL:
            continue
        if min(px1, bx1) - max(px0, bx0) <= TOL:
            continue
        # something pokes into the nominal band - pull the clear edge back
        if px1 - bx0 <= (bx1 - bx0) / 2:
            lo = max(lo, px1)
        elif bx1 - px0 <= (bx1 - bx0) / 2:
            hi = min(hi, px0)
        else:
            raise AssertionError(
                f"D13: '{p.label}' blocks the {side} walk-around passage")
    clear = hi - lo
    assert clear >= MIN_PASSAGE, \
        f"D13: the {side} walk-around is only {clear:.0f} mm, want >= {MIN_PASSAGE}"
    # and the resulting passage must be genuinely empty
    box = ((lo + TOL, hi - TOL), PASSAGE_Y, PASSAGE_Z)
    for p in parts:
        inter = [min(a1, b1) - max(a0, b0)
                 for (a0, a1), (b0, b1) in zip(p.extents, box)]
        assert min(inter) <= TOL, \
            f"D13: '{p.label}' stands in the {side} walk-around passage"
    # the movable panel must not reach down into the standing zone either, in
    # EITHER mode - floor to the bench-rail top, the height your feet occupy.
    foot_box = ((lo + TOL, hi - TOL), PASSAGE_Y, (0, BENCH_RAIL_TOP))
    for p in (panel_bed, panel_table):
        inter = [min(a1, b1) - max(a0, b0)
                 for (a0, a1), (b0, b1) in zip(p.extents, foot_box)]
        assert min(inter) <= TOL, \
            f"D13: '{p.label}' reaches into the {side} standing zone"
    passages.append((side, lo, hi, clear))
print("OK  D13: walk-around beside the ladder - "
      + " / ".join(f"{s} X {lo:.0f}..{hi:.0f} = {c:.0f} mm clear"
                   for s, lo, hi, c in passages)
      + f" (min {MIN_PASSAGE}), empty over Y {PASSAGE_Y[0]}..{PASSAGE_Y[1]} and "
        f"Z {PASSAGE_Z[0]}..{PASSAGE_Z[1]}")

# D8: an even ladder. Rung 1 shares its top with the bench rails and rung 2 with
# the table-mode panel underside; every step of the climb proper has to be under
# the comfort limit and the four of them within a few mm of each other.
rungs = sorted((p for p in parts if p.label.startswith("Ladder Rung_")),
               key=lambda p: p.extents[2][0])
assert len(rungs) == len(RUNG_TOPS)
for r, top in zip(rungs, RUNG_TOPS):
    assert r.extents[2] == (top - RUNG_T, top), f"'{r.label}' is not at top Z {top}"
    assert r.extents[1] == (RUNG_Y0, RUNG_Y1) and r.extents[0] == (LADDER_INNER_L,
                                                                   LADDER_INNER_R)
# every rung block sits directly under its rung, on the same 36x48 stock
rung_blocks = [p for p in parts if p.label.startswith("Rung Block")]
assert len(rung_blocks) == 2 * len(RUNG_TOPS)
for b in rung_blocks:
    top = b.extents[2][1] + RUNG_T
    assert top in RUNG_TOPS, f"'{b.label}' does not sit under a rung"
    assert b.extents[2] == (top - RUNG_T - RUNG_BLOCK_H, top - RUNG_T)
    assert b.extents[1] == (RUNG_Y0, RUNG_Y1)
climb = [0] + RUNG_TOPS + [SLAT_Z1]
steps = [b - a for a, b in zip(climb, climb[1:])]
first_rise, climb_steps = steps[0], steps[1:]
# The first rise is not a climbing step - it is the seat-height ledge you step
# onto, and it is fixed by the bench rail whose top rung 1 shares.
assert first_rise == BENCH_RAIL_TOP == RUNG_TOPS[0], \
    f"rung 1 (top {RUNG_TOPS[0]}) is not level with the bench rails ({BENCH_RAIL_TOP})"
assert max(climb_steps) <= MAX_CLIMB_STEP, \
    f"D8: biggest climbing step is {max(climb_steps)} > {MAX_CLIMB_STEP}"
assert max(climb_steps) - min(climb_steps) <= MAX_CLIMB_SPREAD, \
    f"D8: the climb is uneven - steps {climb_steps}"
assert climb[-1] == SLAT_Z1, "the climb must end on the platform surface"
print(f"OK  D8: rung tops {'/'.join(str(t) for t in RUNG_TOPS)}; rises "
      + " + ".join(str(s) for s in steps)
      + f" mm from the floor to the {SLAT_Z1} platform - first rise "
      f"{first_rise} = bench rail top, then {min(climb_steps)}..{max(climb_steps)} "
      f"(limit {MAX_CLIMB_STEP}, spread {max(climb_steps) - min(climb_steps)} <= "
      f"{MAX_CLIMB_SPREAD})")

# D9: the front table ledger must be GONE and the back one's TOP must BE the
# table-mode panel underside - no hook step, nothing in between.
ledgers = [p for p in parts if p.label.startswith("Table Ledger")]
assert len(ledgers) == 1 and ledgers[0].label == "Table Ledger Back", \
    "D3: the front table ledger must be deleted"
assert not any("Front" in p.label and "Ledger" in p.label for p in parts)
assert ledgers[0].extents[2] == (LEDGER_BACK_Z0, LEDGER_BACK_Z1)
assert LEDGER_BACK_Z1 == PANEL_UNDER_TABLE == RUNG_TOPS[1], \
    "D9: the ledger top, rung 2 and the table-mode panel underside must coincide"
assert BENCH_RAIL_TOP == PANEL_UNDER_BED == RUNG_TOPS[0], \
    "D10: the bench rail tops, rung 1 and the bed-mode panel underside must coincide"
assert "HOOK_STEP" not in globals(), "D10: the hook step is supposed to be gone"
assert PANEL_X0 >= LADDER_INNER_L - 200 and PANEL_X1 <= LADDER_INNER_R + 200
print(f"OK  D9: front table ledger deleted; back ledger {sec(BOARD_T, BOARD_W)} x "
      f"{THROUGH_LEN} at Z {LEDGER_BACK_Z0}..{LEDGER_BACK_Z1}, top level with "
      f"rung 2")

# D10: THE PANEL RESTS ON WOOD. No hooks, no exclusions: in each mode the panel
# must have real BEARING AREA - a shared horizontal face, not an edge kiss - on
# the members the design says carry it.
def bearing_area(upper, lower):
    """Horizontal bearing area of `upper` sitting on top of `lower`, in mm2."""
    (ax0, ax1), (ay0, ay1), (az0, _) = upper.extents
    (bx0, bx1), (by0, by1), (_, bz1) = lower.extents
    if abs(az0 - bz1) > TOL:
        return 0.0
    dx = min(ax1, bx1) - max(ax0, bx0)
    dy = min(ay1, by1) - max(ay0, by0)
    return max(dx, 0.0) * max(dy, 0.0)


# D13 recomputation. The rung bearing shrinks with the 420 -> 320 rung:
#   bed   rung 1   320 x 25 =  8 000 mm2   (was 420 x 25 = 10 500)
#         back bench rail 680 x 48 = 32 640 mm2   (unchanged)
#         the two front bench rail segment ends are GONE (they used to add
#         260 x 48 = 12 480 mm2) - the segments now stop at X 645 / 1345, well
#         clear of the panel's X 655..1335.
#   table rung 2   320 x 25 =  8 000 mm2   (was 10 500)
#         back ledger 680 x 21 = 14 280 mm2   (unchanged)
# Every named support is still far above the 5 000 mm2 floor.
MIN_BEARING = 5000               # mm2, per named support
PANEL_SUPPORTS = {
    "bed_mode": ("Ladder Rung_1", "Bench Rail Back (continuous)"),
    "table_mode": ("Ladder Rung_2", "Table Ledger Back"),
}
EXPECT_BEARING = {
    "bed_mode": {"Ladder Rung_1": RUNG_LEN * RUNG_REST_LEDGE,
                 "Bench Rail Back (continuous)": PANEL_W * BENCH_RAIL_T},
    "table_mode": {"Ladder Rung_2": RUNG_LEN * RUNG_REST_LEDGE,
                   "Table Ledger Back": PANEL_W * BOARD_T},
}
for mode_name, panel in MODES.items():
    found = {p.label: bearing_area(panel, p) for p in parts
             if bearing_area(panel, p) > 0}
    for want in PANEL_SUPPORTS[mode_name]:
        assert want in found, \
            f"D10: the {mode_name} panel does not rest on '{want}' - it only " \
            f"lands on {sorted(found)}"
        assert found[want] >= MIN_BEARING, \
            f"D10: only {found[want]:.0f} mm2 of bearing on '{want}' in {mode_name}"
    # the front edge and the rear edge must BOTH be carried, or it tips
    assert any(a > 0 for lbl, a in found.items() if "Rung" in lbl), \
        f"D10: nothing carries the {mode_name} panel's front edge"
    assert any(a > 0 for lbl, a in found.items()
               if "Back" in lbl or "Ledger" in lbl), \
        f"D10: nothing carries the {mode_name} panel's rear edge"
    # D13: exactly two supports now, and exactly the areas the note computes.
    assert set(found) == set(EXPECT_BEARING[mode_name]), \
        f"D13: the {mode_name} panel rests on {sorted(found)}, expected " \
        f"{sorted(EXPECT_BEARING[mode_name])}"
    for lbl, want in EXPECT_BEARING[mode_name].items():
        assert abs(found[lbl] - want) < TOL, \
            f"D13: bearing on '{lbl}' is {found[lbl]:.0f} mm2, expected {want}"
    assert not any("Bench Rail Front" in lbl for lbl in found), \
        "D13: the front bench rail segments must no longer carry the panel"
    print(f"OK  D10: {mode_name} panel {panel.extents[2][0]:.0f}.."
          f"{panel.extents[2][1]:.0f} rests on "
          + ", ".join(f"{lbl} ({a:.0f} mm2)" for lbl, a in sorted(found.items()))
          + f" = {sum(found.values()):.0f} mm2 total")
assert PANEL_LEN == BENCH_SLAT_LEN == PLATFORM_DEPTH == 800, \
    "D10: the panel has to be as deep as a slat to reach its rear bearings"
assert PANEL_Y0 == BENCH_SLAT_Y0 and PANEL_Y1 == LADDER_Y0
assert RUNG_Y1 == LADDER_Y1, "D10: the tread fronts must be flush with the uprights"
assert LADDER_Y0 - RUNG_Y0 == RUNG_D - UPRIGHT_T == RUNG_REST_LEDGE == 25, \
    "D10: the rungs must reach 25 mm behind the upright plane to catch the panel"
# D13: the panel still straddles BOTH uprights, which is what makes Y=752 a hard
# limit for its front edge and therefore what makes the rung ledge necessary.
assert PANEL_X0 < LADDER_LEFT_X and LADDER_RIGHT_X + UPRIGHT_W < PANEL_X1, \
    "D13: the panel no longer straddles both ladder uprights"
print(f"OK  D10: no hooks - panel {PANEL_T} x {PANEL_W} x {PANEL_LEN} at Y "
      f"{PANEL_Y0}..{PANEL_Y1}, rear edge flush with the bench slats, front edge "
      f"against the uprights; rungs at Y {RUNG_Y0}..{RUNG_Y1} reach "
      f"{LADDER_Y0 - RUNG_Y0} mm behind the upright plane; bed-mode top "
      f"{PANEL_TOP_BED} = {PANEL_BENCH_DIP} mm below the {BENCH_TOP} bench tops "
      f"(cushion recess); table-mode top {PANEL_TOP_TABLE}")

# ---------------------------------------------------------------------------
# M4: THE PANEL STIFFENER BATTENS
# ---------------------------------------------------------------------------
# Three things have to hold, in both modes: the battens are ATTACHED to the
# panel (a real face contact, not a near miss), they CLEAR every other part
# (they are inserted between two bearing lines and under a walking zone, so
# there is no slack), and they stay OUT OF the ladder-bay walking zone.
assert BATTEN_LEN == BATTEN_Y1 - BATTEN_Y0 == 727
assert BATTEN_Y0 == BACK_RAIL_Y1, \
    "M4: the battens must stop at the back rail face, not run past it"
assert BATTEN_Y1 == RUNG_Y0, \
    "M4: the battens must stop at the rung face, not run into the ledge"
assert LEDGER_BACK_Y0 + BOARD_T <= BATTEN_Y0, \
    "M4: the battens foul the back table ledger"
# X: clear of both rung-block lines, and symmetric about the ladder centreline.
assert RUNG_BLOCK_X[0] + RUNG_BLOCK_T <= BATTEN_X[0] and \
    BATTEN_X[1] + BATTEN_W <= RUNG_BLOCK_X[1], \
    "M4: a batten crosses the rung-block line"
batten_centres = [x + BATTEN_W / 2 for x in BATTEN_X]
assert abs((batten_centres[0] + batten_centres[1]) / 2 - LADDER_CENTER_X) < TOL, \
    f"M4: the battens are not symmetric about the ladder centreline: {batten_centres}"
for bx0 in BATTEN_X:
    assert PANEL_X0 <= bx0 and bx0 + BATTEN_W <= PANEL_X1, \
        "M4: a batten hangs off the edge of the panel"

WALK_ZONE = (OPEN_FLOOR_X, (BACK_RAIL_Y1, RUNG_Y0), WALK_ZONE_Z)
for mode_name, panel in MODES.items():
    batts = PANEL_BATTENS[id(panel)]
    assert len(batts) == 2
    for b in batts:
        # attached: the batten top IS the panel underside, over its whole face
        area = bearing_area(panel, b)
        assert abs(area - BATTEN_W * BATTEN_LEN) < TOL, \
            f"M4: '{b.label}' only meets the panel over {area:.0f} mm2, want " \
            f"{BATTEN_W * BATTEN_LEN}"
        assert abs(b.distance(panel)) < TOL, f"M4: '{b.label}' is not on the panel"
        # clear: zero overlap with every other member of this mode. (The general
        # no-two-parts-overlap check below sees the battens too; this one names
        # the batten and runs with a hard zero instead of the 1 mm3 threshold.)
        for q in mode_parts(panel):
            if q is b or q is mattress:
                continue
            inter = [min(a1, c1) - max(a0, c0)
                     for (a0, a1), (c0, c1) in zip(b.extents, q.extents)]
            assert min(inter) <= 0.0, \
                f"M4: '{b.label}' overlaps '{q.label}' in {mode_name} by " \
                f"{inter} mm"
        # out of the walking zone under the ladder bay
        inter = [min(a1, c1) - max(a0, c0)
                 for (a0, a1), (c0, c1) in zip(b.extents, WALK_ZONE)]
        assert min(inter) <= TOL, \
            f"M4: '{b.label}' hangs into the ladder-bay walking zone in {mode_name}"
        assert b.extents[2][0] >= BENCH_RAIL_BOTTOM - TOL, \
            f"M4: '{b.label}' reaches below Z {BENCH_RAIL_BOTTOM} in {mode_name}"
    print(f"OK  M4: {mode_name} - 2 x {sec(BATTEN_W, BATTEN_H)} x {BATTEN_LEN} "
          f"battens on edge at X {BATTEN_X[0]}..{BATTEN_X[0] + BATTEN_W} / "
          f"{BATTEN_X[1]}..{BATTEN_X[1] + BATTEN_W}, Y {BATTEN_Y0}..{BATTEN_Y1}, "
          f"Z {batts[0].extents[2][0]:.0f}..{batts[0].extents[2][1]:.0f}, "
          f"{BATTEN_W * BATTEN_LEN} mm2 screwed face each to the panel, "
          f"clear of every other part and of the walking zone below Z "
          f"{BENCH_RAIL_BOTTOM}")
print(f"OK  M4: panel utilisation at the 2 kN dynamic point 1.42 -> ~0.27 - the "
      f"battens turn an 18 mm sheet over a {BATTEN_LEN} mm span into two tee "
      f"sections (W = 2 x {BATTEN_W}*{BATTEN_H}^2/6 = "
      f"{2 * BATTEN_W * BATTEN_H ** 2 // 6} mm3 in the webs alone)")

# D5: FLUSH TOP. No cleats anywhere; every slat lies on top of the rails and
# must bear on the FULL 48 mm width of BOTH of them, exactly like a bench slat.
assert SLAT_Z0 == RAIL_TOP, "slats do not sit on top of the rails"
assert MATTRESS_Z0 == SLAT_Z1, "mattress does not sit on the slats"
assert (SLAT_Y0, SLAT_Y1) == (BACK_RAIL_Y0, FRONT_RAIL_Y1)
assert SLAT_LEN == BENCH_SLAT_LEN == 800, \
    "D5: an upper slat is supposed to be the same piece as a bench slat"
assert (BED_SLAT_T, BED_SLAT_W) == (BENCH_SLAT_T, BENCH_SLAT_W) == (GUARD_T, GUARD_W)
assert len(bed_slats) == SLAT_COUNT
rail_y = [(BACK_RAIL_Y0, BACK_RAIL_Y1), (FRONT_RAIL_Y0, FRONT_RAIL_Y1)]
for s in bed_slats:
    (sx0, sx1), (sy0, sy1), (sz0, sz1) = s.extents
    assert (sz0, sz1) == (RAIL_TOP, SLAT_Z1), f"'{s.label}' is not on the rail tops"
    for ry0, ry1 in rail_y:
        bear = min(sy1, ry1) - max(sy0, ry0)
        assert bear >= RAIL_T - TOL, \
            f"'{s.label}' only bears {bear:.1f} mm on the rail at Y {ry0}..{ry1}"
    assert 0 <= sx0 and sx1 <= WALL_SPAN
slat_xs = sorted(s.extents[0] for s in bed_slats)
slat_gaps = [slat_xs[i + 1][0] - slat_xs[i][1] for i in range(len(slat_xs) - 1)]
slat_gaps += [slat_xs[0][0] - 0, WALL_SPAN - slat_xs[-1][1]]
assert max(slat_gaps) <= MAX_SLAT_GAP + TOL, \
    f"largest slat gap is {max(slat_gaps):.1f} > {MAX_SLAT_GAP}"
print(f"OK  D5: {SLAT_COUNT} upper slats {sec(BED_SLAT_T, BED_SLAT_W)} x "
      f"{SLAT_LEN} flush on top of both rails, Z {SLAT_Z0}..{SLAT_Z1}, Y "
      f"{SLAT_Y0}..{SLAT_Y1} ({RAIL_T} mm full bearing on each rail), pitch "
      f"{slat_pitch:.1f}, gaps {min(slat_gaps):.0f}..{max(slat_gaps):.1f} mm "
      f"(limit {MAX_SLAT_GAP}); mattress {MATTRESS_Z0}..{MATTRESS_Z1} at Y "
      f"{MATTRESS_Y0}..{MATTRESS_Y1}; rail {RAIL_BOTTOM}..{RAIL_TOP}")

# The mattress must land entirely on the slat platform, and nothing but the
# mattress and the bed slats may intrude into the mattress volume. The slats
# are now BELOW that volume (they stop at 1197, where the mattress starts), so
# the exemption is only there to keep the check honest if the stack ever moves.
assert SLAT_Y0 <= MATTRESS_Y0 and MATTRESS_Y1 <= SLAT_Y1, \
    "the mattress overhangs the slat platform in Y"

# D12: THE MATTRESS IS FLUSH AT BOTH EDGES. Not "fits with play" - flush. Both
# long edges land exactly on the slat ends, so there is no bare slat strip left
# on either side, at the back or at the front.
assert MATTRESS_Y0 == SLAT_Y0, \
    f"D12: mattress rear edge {MATTRESS_Y0} is not flush with the slat ends {SLAT_Y0}"
assert MATTRESS_Y1 == SLAT_Y1, \
    f"D12: mattress front edge {MATTRESS_Y1} is not flush with the slat ends {SLAT_Y1}"
assert MATTRESS_W == SLAT_LEN == PLATFORM_DEPTH, \
    "D12: the mattress width and the platform depth must be the same number"
exposed = [("back", MATTRESS_Y0 - SLAT_Y0), ("front", SLAT_Y1 - MATTRESS_Y1)]
for where, e in exposed:
    assert abs(e) < TOL, f"D12: {e} mm of bare slat still shows at the {where}"
print(f"OK  D12: mattress {MATTRESS_W} x {WALL_SPAN} at Y {MATTRESS_Y0}.."
      f"{MATTRESS_Y1} is EXACTLY the {PLATFORM_DEPTH} mm slat footprint - "
      f"0 mm of bare slat at the back, 0 mm at the front (v7: 29 / 77)")

# D5 consequence worth stating: the sunken tray used to locate the mattress
# sideways (the rail tops overlapped its bottom 29 mm). The flush top cannot,
# and the guard boards cannot either - they start 75 mm ABOVE the mattress
# surface. The job passes to the six verticals, which all run past the mattress
# band: the back posts stop it at Y -48 and the front posts and ladder uprights
# at Y 752 - exactly the edges of the slat platform. After D12 that is no longer
# a loose fit with 106 mm of shuffle, it is a positive fit: the mattress is
# captured between the two lines of verticals with zero play, which is a much
# better answer to the same problem.
stops_back = [p for p in verticals
              if p.extents[1][1] == SLAT_Y0 and p.extents[2][0] <= MATTRESS_Z0
              and p.extents[2][1] >= MATTRESS_Z1]
stops_front = [p for p in verticals
               if p.extents[1][0] == SLAT_Y1 and p.extents[2][0] <= MATTRESS_Z0
               and p.extents[2][1] >= MATTRESS_Z1]
assert len(stops_back) == 2 and len(stops_front) == 4, \
    f"mattress not bracketed by the verticals ({len(stops_back)} back, " \
    f"{len(stops_front)} front)"
mattress_play = (SLAT_Y1 - SLAT_Y0) - MATTRESS_W
assert mattress_play == 0, \
    f"D12: the mattress should be a flush fit, not {mattress_play} mm of play"
print(f"OK  D5/D12: the mattress is bracketed at Y {SLAT_Y0}..{SLAT_Y1} by "
      f"{len(stops_back)} back posts and {len(stops_front)} front verticals "
      f"over its whole Z band - {mattress_play} mm of sideways play on the "
      f"{SLAT_Y1 - SLAT_Y0} mm platform (v7: 106), a positive fit")
mattress_vol = ((0, WALL_SPAN), (MATTRESS_Y0, MATTRESS_Y1), (MATTRESS_Z0, MATTRESS_Z1))


def overlap_volume(extents, other):
    v = 1.0
    for (a0, a1), (b0, b1) in zip(extents, other):
        d = min(a1, b1) - max(a0, b0)
        if d <= 0:
            return 0.0
        v *= d
    return v


allowed = {id(mattress)} | {id(s) for s in bed_slats}
clashes = []
checked = 0
for p in parts + [panel_bed, panel_table] + battens_bed + battens_table:
    if id(p) in allowed:
        continue
    checked += 1
    v = overlap_volume(p.extents, mattress_vol)
    if v >= 1e-6:
        clashes.append((p.label, v))
assert not clashes, "parts intruding into the mattress volume: " + str(clashes)
print(f"OK  no part intrudes into the mattress volume (checked {checked} parts)")

# --- no two parts may overlap each other -----------------------------------
for mode_name, panel in MODES.items():
    items = [p for p in mode_parts(panel) if p is not mattress]
    bad = []
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if overlap_volume(a.extents, b.extents) > 1.0:
                bad.append((a.label, b.label))
    assert not bad, f"{mode_name}: parts occupying the same space: {bad}"
print("OK  no two wooden parts overlap in either mode")

# --- CONNECTIVITY: every wooden part must touch at least one other part -----
# Regression guard: the v2 ladder floated 48 mm in front of the rail and was
# attached to nothing at all.
CONTACT_TOL = 0.5


def aabb_distance(a, b):
    """Exact distance between two axis-aligned boxes given by their extents."""
    d2 = 0.0
    for (a0, a1), (b0, b1) in zip(a, b):
        gap = max(b0 - a1, a0 - b1, 0.0)
        d2 += gap * gap
    return math.sqrt(d2)


print("--- connectivity (min distance to the rest of the assembly) ---")
for mode_name, panel in MODES.items():
    items = [p for p in mode_parts(panel) if p is not mattress]
    # No part is excluded, and after D10 the movable panel is not even a
    # borderline case any more: it is not hung on undrawn steel hardware, it
    # LIES on the wood this model draws. Its nearest neighbours are the members
    # it bears on - the back bench rail and rung 1 in bed mode, the back ledger
    # and rung 2 in table mode (D13 took the front bench rail segments out of
    # its X range) - all at zero distance with real contact area (see the D10
    # bearing check above), plus the two ladder uprights its front edge butts
    # against in both modes.
    # D13 also cut the ladder uprights loose from the front bench rail. They are
    # still in contact with the assembly on three counts: the front side rail
    # they are bolted through (Y 704..752 against their back face at 752), the
    # front guard segments lapped onto their front faces, and their own rung
    # blocks - so this check still passes with zero excluded parts.
    skip = set()
    worst = (None, -1.0)
    for p in items:
        if id(p) in skip:
            continue
        others = [q for q in items if q is not p]
        near = min(others, key=lambda q: aabb_distance(p.extents, q.extents))
        # confirm the analytic result with OCC's real solid-to-solid distance
        d = p.distance(near)
        assert d < CONTACT_TOL, (
            f"{mode_name}: '{p.label}' is floating - nearest part "
            f"'{near.label}' is {d:.2f} mm away")
        if d > worst[1]:
            worst = (p.label, d)
    n = len(items) - len(skip)
    print(f"OK  {mode_name}: all {n} wooden parts in contact "
          f"(worst gap {worst[1]:.3f} mm on '{worst[0]}')")

# ---------------------------------------------------------------------------
# EXPORT
# ---------------------------------------------------------------------------
print("\n=== EXPORT ===")
os.makedirs(GROUP_DIR, exist_ok=True)
exports = []
group_files = []

for name, panel in MODES.items():
    comp = bed_mode if name == "bed_mode" else table_mode

    # STEP stays in the CAD convention: mm, Z-up.
    step_path = os.path.join(OUT_DIR, f"loftbed_{name}.step")
    export_step(comp, step_path)
    exports.append(step_path)

    # Mesh exports are Y-up so the bed stands upright by default.
    # export_gltf() writes the Z-up -> Y-up rotation onto the root node of the
    # glTF scene itself, so the Z-up compound is handed to it unchanged (pre-
    # rotating would apply the turn twice). The GLB keeps one node per part,
    # so labels and per-part colours survive. Deliverable only (LOFTBED_FULL).
    if FULL_EXPORT:
        glb_path = os.path.join(OUT_DIR, f"loftbed_{name}.glb")
        export_gltf(comp, glb_path, binary=True)
        exports.append(glb_path)

    # STL has no transform node, so Y-up has to be baked into the vertices.
    y_up = make_compound(panel, Y_UP)
    stl_path = os.path.join(OUT_DIR, f"loftbed_{name}.stl")
    export_stl(y_up, stl_path)
    exports.append(stl_path)

    # One STL per colour group (same Y-up orientation), so the .usdz can carry
    # five separate UsdPreviewSurface materials. These are intermediates and
    # deliberately live outside the repo.
    manifest = []
    for group in GROUP_ORDER:
        members = [p.moved(Y_UP) for p in mode_parts(panel) if p.group == group]
        if not members:
            continue
        gpath = os.path.join(GROUP_DIR, f"loftbed_{name}_{group}.stl")
        export_stl(Compound(children=members), gpath)
        rgba = ",".join(f"{c:.4g}" for c in tuple(GROUP_COLORS[group]))
        manifest.append(f"{group}={rgba}={gpath}")
    mpath = os.path.join(GROUP_DIR, f"loftbed_{name}.groups")
    with open(mpath, "w", encoding="utf-8") as fh:
        fh.write("\n".join(manifest) + "\n")
    group_files.append(mpath)

    # Hidden-line projections are by far the slowest step in this script, so
    # they are deliverables only (LOFTBED_FULL / `mise run build-full`).
    if FULL_EXPORT:
        for view, direction in (("iso", (1, -1, 1)), ("front", (0, -1, 0))):
            svg_path = os.path.join(OUT_DIR, f"loftbed_{name}_{view}.svg")
            try:
                write_svg(comp, svg_path, direction)
                exports.append(svg_path)
            except Exception as e:  # pragma: no cover
                print(f"SVG export failed for {svg_path}: {e}")

for p in exports:
    print("  wrote", p)
print(f"  per-colour-group STL manifests in {GROUP_DIR}:")
for p in group_files:
    print("   ", p)
if not FULL_EXPORT:
    print("  (.glb and .svg skipped - run `mise run build-full` / LOFTBED_FULL=1 "
          "for the full deliverable set)")

# ---------------------------------------------------------------------------
# CUT LIST
# ---------------------------------------------------------------------------
print("\n=== CUT LIST ===")
# The name column is 40 wide so the longest entry - "Guard rail, front segment
# (D2/D7/D13)", 39 chars - fits without running into the section column.
NAME_COL = 40
RULE = NAME_COL + 18 + 12 + 6                  # 76
print(f"{'Part':<{NAME_COL}}{'Section':<18}{'Length (mm)':>12}{'Qty':>6}")
print("-" * RULE)
total = 0
for (part, section, length), qty in sorted(CUT_LIST.items()):
    assert len(part) < NAME_COL, \
        f"cut-list name '{part}' ({len(part)} chars) overflows the {NAME_COL} " \
        f"char column"
    print(f"{part:<{NAME_COL}}{section:<18}{length:>12}{qty:>6}")
    total += qty
print("-" * RULE)
print(f"{'TOTAL pieces':<{NAME_COL}}{'':<18}{'':>12}{total:>6}")
by_section = {}
for (part, section, length), qty in CUT_LIST.items():
    by_section[section] = by_section.get(section, 0) + qty
print("\nBy section: " + ", ".join(
    f"{s} x{n}" for s, n in sorted(by_section.items(), key=lambda kv: -kv[1])))
print("\nNote: the movable panel and its two battens are listed once; they are "
      "the same three parts in both modes.")
print(f"Note (D10/M4): the panel rests straight on wood in both modes and is "
      f"stiffened by 2 x {sec(BATTEN_W, BATTEN_H)} x {BATTEN_LEN} battens on "
      f"edge screwed to its underside (X {BATTEN_X[0]}/{BATTEN_X[1]}, Y "
      f"{BATTEN_Y0}..{BATTEN_Y1}), which take the 2 kN dynamic utilisation from "
      f"1.42 to ~0.27. The steel is not modelled: at the FRONT, load-bearing "
      f"U-brackets wrap the rung (as the Hoppekids original) and clamp the panel "
      f"to the ladder - panel anti-tip AND, through the panel, the brace that "
      f"restrains the ladder base (finding F1); at the REAR, hook plates over "
      f"the back bench rail / back table ledger. No bolts or screws are drawn.")
print(f"Note (D11/D13): the front bench rail is two {FRONT_BENCH_RAIL_SEG_LEN} mm "
      f"segments that stop at the sofa ends on their stub legs; only the back "
      f"one is a through-running {THROUGH_LEN} mm member. The ladder uprights "
      f"no longer lap it - flagged for the docs-round load check.")
print(f"Note (D12): the depth stack came in {DEPTH_SHRINK} mm on the FRONT side "
      f"only, so the {MATTRESS_W} mm mattress is flush with the slat ends at "
      f"both edges. Slats, bench slats and the panel are all {SLAT_LEN} mm long "
      f"now (was 906) and the end beams {END_BEAM_LEN} mm (was 1002); overall "
      f"depth {OVERALL_DEPTH} mm (was 1070).")
print(f"Note (D13): the ladder is {LADDER_CLEAR} mm clear (was 420) on "
      f"{sec(UPRIGHT_W, UPRIGHT_T)} uprights (was 48x48), so the rungs are "
      f"{RUNG_LEN} mm and the front guard segments {FRONT_GUARD_SEG_LEN} mm. "
      f"The 36x48x{RUNG_BLOCK_LEN} rung blocks are unchanged - their 36 mm is "
      f"stock thickness, not upright width.")
print(f"Note (D5/D7): 34x98 is the common board stock - {SLAT_COUNT} upper bed "
      f"slats + {BENCH_SLAT_COUNT * len(BENCH_X)} bench slats (all "
      f"{SLAT_LEN} mm, one and the same piece, so cut "
      f"{SLAT_COUNT + BENCH_SLAT_COUNT * len(BENCH_X)} of them in one go) + 2 "
      f"back guards + 4 front guard segments.")
print("Note (D7): 21x95 now appears exactly once in the whole bed - the back "
      "table ledger. Nothing else uses it.")
print("Note (D5): the slat cleats are gone; the upper slats are screwed "
      "straight down onto the side rails, one 5x60 per end.")

# ---------------------------------------------------------------------------
# PARTS SNAPSHOT
# ---------------------------------------------------------------------------
# parts.tsv is the tracked regression snapshot: every part's label, colour group
# and bounding box, sorted by label. Both panel positions are in it, told apart
# by the "(bed mode)" / "(table mode)" suffix on the label. It is the one
# generated file that IS committed - a diff on it is the diff on the model.
snapshot = parts + [mattress, panel_bed, panel_table] + battens_bed + battens_table
snap_path = os.path.join(OUT_DIR, "parts.tsv")
with open(snap_path, "w", encoding="utf-8") as fh:
    fh.write("label\tgroup\tx0\tx1\ty0\ty1\tz0\tz1\n")
    for p in sorted(snapshot, key=lambda q: q.label):
        (x0, x1), (y0, y1), (z0, z1) = p.extents
        fh.write(f"{p.label}\t{p.group}\t" + "\t".join(
            f"{v:g}" for v in (x0, x1, y0, y1, z0, z1)) + "\n")
print(f"\nwrote {snap_path} ({len(snapshot)} parts, both panel modes)")
