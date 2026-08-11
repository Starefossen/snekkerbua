"""V3 proof sheets: the two guide battens seated, and the three lock options.

Three pages, all drawn off the model through the same hidden-line machinery
every manual page uses - so nothing here can show a part the bed does not
have, or show it anywhere but where the model puts it:

  docs/preview/mekanisme-v2-bed.png     the two corners in BED mode
  docs/preview/mekanisme-v2-table.png   the same two corners in TABLE mode
  docs/preview/laasvalg.png             the three bed-mode lock options, all
                                        drawn at the corner each would live in
  docs/preview/stigefot-valg.png        the three answers to avvik 2 at the
                                        ladder foot  (`--stigefot`, made alone)

WHAT CHANGED IN V3, AND WHY THESE SHEETS STILL EXIST. They were drawn to prove
a claim about four angle brackets: one bracket geometry, two seats. There are
no brackets now. The claim they prove instead is stronger and it is made of
wood: the two long battens run down the 48 x 37 mm free shafts beside the rung
ends with 2 mm of clearance, and because rung 1 and rung 2 end at exactly the
same X, the SAME two battens find the SAME two end faces at both heights. So
the two mechanism sheets are still one page per corner and still the same two
crops 223 mm apart - the left crop is the rear seat (wood on wood, nothing
between the panel and the rail), the right crop is the guide in its shaft with
the measured clearance written on it.

The lock sheet is HISTORY, not a shopping list. V4 took the decision and the
answer is NO LOCK - an accepted deviation, docs/ASSEMBLY.md vedlegg B avvik 4 -
so none of the three is wired into the model and none of them is on the
beslagliste. The sheet is kept because the WOOD it is drawn on is unchanged and
asserted: V3 moved the point all three act at onto the front cross batten's end
face against the front bench rail's end face, across the side gap, and that pair
of faces only exists in bed mode. Anyone who later wants a lock can fit any of
the three without touching a single piece of timber, and this is the page that
says so. It is not in the build gate; it is made by hand with
`mise run mekanisme`.
"""

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

OUT = os.path.join(ROOT, "docs", "preview")

CROP = 145.0          # model mm around the crop centre, half-width
CAM = (318.0, 26.0)   # azimuth, elevation - the manual's own three-quarter


# ---------------------------------------------------------------------------
# THE TWO CORNERS EACH SHEET SHOWS
# ---------------------------------------------------------------------------
# Each one is a point in the model, per mode, and a title. They are computed
# off the parts, not typed: the rear crop is centred on the panel's rear left
# corner where it sits on the support, the front crop on the left rung end -
# the one place in this bed where 2 mm decides whether the panel goes in.
def corners(G, mode):
    panel = G.MODES[mode]
    batts = G.PANEL_BATTENS[id(panel)]
    guide = min((b for b in batts
                 if abs((b.extents[1][1] - b.extents[1][0]) - G.BATTEN_LEN)
                 < G.TOL), key=lambda b: b.extents[0][0])
    seat_z = panel.extents[2][0]
    return [
        ("BAKRE HJØRNE — platen ligger rett på tre",
         (G.PANEL_X0, (G.LEDGER_BACK_Y0 + G.BACK_RAIL_Y1) / 2, seat_z)),
        ("TRINNENDEN — styrelekta 2 mm klar av endeveden",
         (G.LADDER_INNER_L, (G.RUNG_Y0 + guide.extents[1][1]) / 2,
          seat_z - G.RUNG_T / 2)),
    ]


def near_parts(G, panel, centre, reach):
    """Every wooden part with a corner inside the crop sphere."""
    out = []
    for p in list(G.parts) + [panel] + G.PANEL_BATTENS[id(panel)]:
        if p is G.mattress:
            continue
        d = 0.0
        for j in range(3):
            lo, hi = p.extents[j]
            d += max(lo - centre[j], 0.0, centre[j] - hi) ** 2
        if math.sqrt(d) <= reach:
            out.append(p)
    return out


def draw_corner(RL, G, page, box, mode, centre, title, extra=None):
    """One cropped panel: the fixed bed in grey, the panel unit in black."""
    panel = G.MODES[mode]
    view = RL.View(RL.camera_direction(*CAM), centre)

    wood = near_parts(G, panel, centre, CROP * 1.9)
    unit = set(id(p) for p in [panel] + list(G.PANEL_BATTENS[id(panel)]))
    fixed = [p for p in wood if id(p) not in unit]
    moving = [p for p in wood if id(p) in unit]

    fixed_lines = RL.project(view, [("w", RL.comp(fixed))])["w"] if fixed \
        else []
    move_lines = RL.project(view, [("m", RL.comp(moving))])["m"] if moving \
        else []

    # The crop window, in the view's own frame, centred on the corner.
    cx, cy = view.xy(centre)
    k = min(box[2], box[3]) / (2 * CROP)

    def fit(plines):
        return [[((x - cx) * k + box[0] + box[2] / 2,
                  (y - cy) * k + box[1] + box[3] / 2) for x, y in pl]
                for pl in plines]

    def at(p3):
        x, y = view.xy(p3)
        return ((x - cx) * k + box[0] + box[2] / 2,
                (y - cy) * k + box[1] + box[3] / 2)

    page.rect(box[0], box[1], box[2], box[3], fill="#ffffff",
              stroke=RL.GREY, width=RL.T.W_PHANTOM)
    page.clip_rect_begin(box)
    page.polylines(fit(fixed_lines), RL.GREY, RL.T.W_NEW * 0.55)
    page.polylines(fit(move_lines), RL.INK, RL.T.W_NEW * 0.95)
    if extra:
        extra(page, at, k)
    page.clip_rect_end()
    page.text((box[0] + box[2] / 2, box[1] - RL.T.BADGE_R * 1.1), title,
              RL.T.BADGE_R * 0.8, anchor="middle", weight="bold")
    return view, at, k


def sheet(RL, G, mode, path):
    """One mechanism proof sheet: two cropped corners side by side."""
    pad = 60.0
    cell = 520.0
    w = pad * 3 + cell * 2
    h = pad * 3.9 + cell
    page = RL.Page(0, 0, w, h)
    lift = G.PANEL_MODE_LIFT if mode == "table_mode" else 0
    seat = G.PANEL_UNDER_BED + lift
    head = ("SENGESTILLING" if mode == "bed_mode" else "BORDSTILLING")
    page.text((pad, h - pad * 0.9),
              f"{head} — platens underside Z {seat:.0f}", RL.T.BADGE_R * 1.4,
              weight="bold")
    page.text((pad, h - pad * 1.45),
              "Grått = fast del av sengen, svart = plateenheten.",
              RL.T.BADGE_R * 0.8)
    page.text((pad, h - pad * 1.9),
              f"Ikke ett beslag: styringen er de to lange lektene mot "
              f"trinnendene, {G.PANEL_FIT} mm hver vei, "
              f"{G.BATTEN_GUIDE_ENGAGE_Z}×{G.BATTEN_GUIDE_ENGAGE_Y} mm tre "
              f"mot endeved.", RL.T.BADGE_R * 0.8)
    for i, (title, centre) in enumerate(corners(G, mode)):
        box = (pad + i * (cell + pad), pad * 1.6, cell, cell)
        draw_corner(RL, G, page, box, mode, centre, title)
    page.write(path + ".svg", 1600)
    RL.to_png(path + ".svg", path + ".png", 1600)
    return path + ".png"


# ---------------------------------------------------------------------------
# THE THREE LOCK OPTIONS
# ---------------------------------------------------------------------------
# All three act at the SAME place, and after V3 that place is wood: the front
# cross batten's outboard END FACE against the front bench rail's END FACE,
# across the side gap (24 mm up to v12, 63 after K2). The two faces are side
# by side, in one Z band and
# one Y band, in BED mode - and 223 mm apart in table mode, where the lock
# therefore has nothing to take hold of. A lock that cannot be left on in the
# wrong position is a property of the geometry, not of the instructions.
# How far the strap has to lap onto each of the two end faces to have
# something to screw into. The strap's LENGTH is therefore the side gap plus
# two of these - it is not a stock number to be quoted, which is exactly the
# mistake K2 caught: the sheet said "flattstål 60x24x3" over a 24 mm gap, and
# the gap is 63 mm now, so a 60 mm strap would not reach across it at all.
LOCK_STRAP_LAP = 18.0


def locks(G):
    """The three options, with every dimension that depends on the side gap
    taken off the model."""
    strap = G.LOCK_GAP + 2 * LOCK_STRAP_LAP        # 99 mm after K2 (was 60)
    return [
        ("i   SKRUE — verktøy kreves",
         f"Flattstål {strap:g}×24×3 lagt over spalten, to treskruer 5×40 i "
         f"hver ende — én ned i tverrlekta, én ned i vangeenden. EN 747 "
         f"4.1.1: en omstilling som krever verktøy er den konforme "
         f"grunnlinjen. Koster en skrutrekker hver gang platen skal flyttes."),
        ("ii  FINGERSKRUE — verktøyfri",
         "Samme flattstål, men festet med en riflet fingerskrue M6 i en "
         "gjengeinnsats i vangeenden. Lifetime-sengene gjør nettopp dette. "
         "Verktøyfritt betyr at et barn òg kan gjøre det: EN-messig et "
         "grensetilfelle, ikke en konform løsning."),
        ("iii OVERSENTERLÅS — trekker platen ned",
         "Spennlås (Jula 012270-klassen) med huset på vangeenden og bøylen i "
         "tverrlekta. Den TREKKER platen ned mot opplegget, så klapringen "
         "forsvinner — men den er også verktøyfri, og huset står ut i "
         "sideklaringen."),
    ]


def lock_centre(G):
    """The point all three lock options act at, read off the model."""
    rail = next(p for p in G.parts
                if p.label.startswith("Bench Rail Front")
                and p.extents[0][1] <= G.PANEL_X0)
    nose = next(b for b in G.PANEL_BATTENS[id(G.panel_bed)]
                if abs(b.extents[0][0] - G.PANEL_X0) < G.TOL)
    return ((rail.extents[0][1] + nose.extents[0][0]) / 2,
            (max(rail.extents[1][0], nose.extents[1][0])
             + min(rail.extents[1][1], nose.extents[1][1])) / 2,
            nose.extents[2][1])


def lock_sheet(RL, G, path):
    pad = 60.0
    cell = 470.0
    # The caption block under each crop is what sets the page height: six
    # lines of prose plus the title, measured in the theme's own badge unit,
    # so a longer argument makes a taller page instead of running off it.
    cap_h = RL.T.BADGE_R * (2.4 + 6 * 1.05)
    box_y = pad + cap_h
    w = pad * 4 + cell * 3
    h = box_y + cell + pad * 3.4
    page = RL.Page(0, 0, w, h)
    centre = lock_centre(G)
    page.text((pad, h - pad * 0.9), "LÅS I SENGESTILLING — TRE VALG",
              RL.T.BADGE_R * 1.4, weight="bold")
    page.text((pad, h - pad * 1.4),
              f"Alle tre virker på det samme stedet: tverrlektas endeved mot "
              f"enden av den fremre benkevangen, tvers over de {G.LOCK_GAP} "
              f"mm i sideklaringen.", RL.T.BADGE_R * 0.8)
    page.text((pad, h - pad * 1.8),
              f"I BORDSTILLING står tverrlekta {G.PANEL_MODE_LIFT} mm høyere "
              f"og vangen er ikke der, så låsen kan ikke stå på i feil "
              f"stilling — det følger av geometrien.", RL.T.BADGE_R * 0.8)
    page.text((pad, h - pad * 2.2),
              "INGEN av dem monteres. Låsen er valgt bort (akseptert avvik "
              "4); dette arket er ettermonteringsgrunnlaget, ikke en "
              "bestilling.", RL.T.BADGE_R * 0.8)
    for i, (title, body) in enumerate(locks(G)):
        box = (pad + i * (cell + pad), box_y, cell, cell)

        def extra(page, at, k, i=i):
            _lock_art(page, RL, G, at, k, i, centre)

        draw_corner(RL, G, page, box, "bed_mode", centre, title, extra=extra)
        y = box[1] - RL.T.BADGE_R * 2.4
        for line in _wrap(body, 52):
            page.text((box[0], y), line, RL.T.BADGE_R * 0.72)
            y -= RL.T.BADGE_R * 1.05
    page.write(path + ".svg", 1800)
    RL.to_png(path + ".svg", path + ".png", 1800)
    return path + ".png"


def _wrap(text, n):
    out, line = [], ""
    for word in text.split():
        if len(line) + len(word) + 1 > n:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return out


def _lock_art(page, RL, G, at, k, which, centre):
    """The lock itself, drawn in the model's own space across the side gap."""
    hx, hy, top = centre
    w = RL.T.W_NEW * 0.95
    half = G.LOCK_GAP / 2 + LOCK_STRAP_LAP   # the strap laps onto each end
    if which == 0:                        # flat strap, two screws per end
        page.line(at((hx - half, hy, top)), at((hx + half, hy, top)),
                  RL.INK, w * 1.3)
        for dx in (-half + 9.0, half - 9.0):
            head = at((hx + dx, hy, top))
            page.line(head, at((hx + dx, hy, top - 40.0)), RL.INK, w)
            page.dot(head, RL.T.BADGE_R * 0.3, colour=RL.INK)
    elif which == 1:                      # knurled thumbscrew, same strap
        page.line(at((hx - half, hy, top)), at((hx + half, hy, top)),
                  RL.INK, w * 1.3)
        page.line(at((hx - half + 9.0, hy, top)),
                  at((hx - half + 9.0, hy, top - 40.0)), RL.INK, w)
        head = at((hx + half - 9.0, hy, top + 26.0))
        neck = at((hx + half - 9.0, hy, top))
        page.line(neck, at((hx + half - 9.0, hy, top - 30.0)), RL.INK, w)
        page.line(head, neck, RL.INK, w)
        r = abs(at((hx + half - 9.0 + 13.0, hy, top + 26.0))[0] - head[0])
        page.circle(head, r, fill="#ffffff", stroke=RL.INK, width=w)
        for a in range(0, 360, 30):
            p0 = (head[0] + r * 0.62 * math.cos(math.radians(a)),
                  head[1] + r * 0.62 * math.sin(math.radians(a)))
            p1 = (head[0] + r * math.cos(math.radians(a)),
                  head[1] + r * math.sin(math.radians(a)))
            page.line(p0, p1, RL.INK, w * 0.5)
    else:                                 # over-centre latch
        base = at((hx - half, hy, top - 6.0))
        body = at((hx - half, hy, top - 40.0))
        arm = at((hx + half, hy, top + 30.0))
        hook = at((hx + half - 6.0, hy, top + 2.0))
        page.line(base, body, RL.INK, w)
        page.line(base, arm, RL.INK, w * 1.1)
        page.line(arm, hook, RL.INK, w)
        page.line(hook, at((hx + half - 6.0, hy, top - 12.0)), RL.INK, w)
        page.dot(base, RL.T.BADGE_R * 0.3, colour=RL.INK)
        page.dot(arm, RL.T.BADGE_R * 0.26, colour=RL.INK)


# ---------------------------------------------------------------------------
# THE THREE STILE-FOOT OPTIONS  (docs/preview/stigefot-valg.png, --stigefot)
# ---------------------------------------------------------------------------
# Same job as the lock sheet, one level down: a decision the BUILDER takes, drawn
# once so it can be taken by looking instead of by reading. Vedlegg B avvik 2
# says the ladder foot is held forward by J3 alone, and the F1 block in
# generate_loftbed.py measured every direction out of the foot: all four are
# volumes some other rule requires empty. Two of them can be given up, and this
# sheet is those two side by side with the third - doing nothing.
#
# ILLUSTRATION ONLY. The two candidate blocks below are NOT parts. They are
# built here, in this file, out of G.block() with no cut-list entry, they never
# touch G.parts, no assert sees them and nothing exports them. They exist for
# the length of one drawing so the reader can see what the option would occupy.
# If one of them is ever chosen it has to be built in the model, with its own
# joints and its own asserts - not lifted out of here.
FOOT_CROP = 225.0            # model mm, half-width of the crop
FOOT_CAM = (28.0, 22.0)      # low three-quarter from the ROOM side, outboard


def foot_scene(G):
    """The left stile foot, its passage, and the two candidate blocks.

    Everything is read off the model: the passage is the gap between the front
    sofa end (the stub leg / rail end at X 645) and the stile's outer face, and
    both blocks span exactly that gap, so neither can be drawn wider or
    narrower than the hole it would fill.
    """
    stile = min((p for p in G.parts if p.label.startswith("Ladder Upright")),
                key=lambda p: p.extents[0][0])
    leg = min((p for p in G.parts
               if p.label.startswith("Bench Stub Leg Front")),
              key=lambda p: p.extents[0][0])
    x0, x1 = leg.extents[0][1], stile.extents[0][0]       # 645 .. 787
    gap = x1 - x0
    rail = next(p for p in G.parts
                if p.label.startswith("Bench Rail Front")
                and p.extents[0][1] <= x0)

    # (i) THRESHOLD: 48x73 laid flat on the floor across the walk-around. Its
    #     73 mm goes in Y, in the ladder's own front band (flush with the stile
    #     front face) so the block lands square on the stile's outer face and
    #     laps the stub leg it starts from.
    thr = G.block(x0, stile.extents[1][1] - G.BENCH_RAIL_H, 0,
                  gap, G.BENCH_RAIL_H, G.BENCH_RAIL_T,
                  "ILLUSTRASJON terskelkloss", "rails")
    # (ii) RAIL EXTENSION: the front bench rail's own section, in the rail's own
    #     plane and height band, carried the last 142 mm to the stile.
    ext = G.block(x0, rail.extents[1][0], G.BENCH_RAIL_BOTTOM,
                  gap, G.BENCH_RAIL_T, G.BENCH_RAIL_H,
                  "ILLUSTRASJON vangeforlenger", "rails")
    centre = ((x0 + x1) / 2, G.PASSAGE_Y[1] + 40.0, G.BENCH_RAIL_TOP * 0.62)
    return centre, gap, [thr], [ext], []


def foot_floor(page, RL, G, at, x0, x1):
    """The floor, and the piece of it D13 keeps clear, as flat tone.

    Neither is a part - the room's floor is not in the model - but both are in
    the argument: option (i) lies ON the floor, inside the tinted rectangle,
    and option (ii) passes over it without touching it. Drawn first, so all
    the line work lands on top.
    """
    wide = (x1 - x0) * 6.0
    page.poly([at((x0 - wide, G.WALL_Y, 0)), at((x1 + wide, G.WALL_Y, 0)),
               at((x1 + wide, G.PASSAGE_Y[1] + 700.0, 0)),
               at((x0 - wide, G.PASSAGE_Y[1] + 700.0, 0))],
              fill="#f7f7f7", stroke="none", width=0)
    page.poly([at((x0, G.PASSAGE_Y[0], 0)), at((x1, G.PASSAGE_Y[0], 0)),
               at((x1, G.PASSAGE_Y[1], 0)), at((x0, G.PASSAGE_Y[1], 0))],
              fill="#e9e9e9", stroke=RL.GREY, width=RL.T.W_PHANTOM)


def draw_foot(RL, G, page, box, centre, title, cand, gapx):
    """One cropped panel: the standing bed in grey, the candidate in black."""
    view = RL.View(RL.camera_direction(*FOOT_CAM), centre)
    reach = FOOT_CROP * 1.9
    wood = []
    for p in G.parts:
        d = 0.0
        for j in range(3):
            lo, hi = p.extents[j]
            d += max(lo - centre[j], 0.0, centre[j] - hi) ** 2
        if math.sqrt(d) <= reach:
            wood.append(p)

    groups = [("w", RL.comp(wood))]
    if cand:
        groups.append(("c", RL.comp(cand)))
    lines = RL.project(view, groups)

    cx, cy = view.xy(centre)
    k = min(box[2], box[3]) / (2 * FOOT_CROP)

    def fit(plines):
        return [[((x - cx) * k + box[0] + box[2] / 2,
                  (y - cy) * k + box[1] + box[3] / 2) for x, y in pl]
                for pl in plines]

    def at(p3):
        x, y = view.xy(p3)
        return ((x - cx) * k + box[0] + box[2] / 2,
                (y - cy) * k + box[1] + box[3] / 2)

    page.rect(box[0], box[1], box[2], box[3], fill="#ffffff",
              stroke=RL.GREY, width=RL.T.W_PHANTOM)
    page.clip_rect_begin(box)
    foot_floor(page, RL, G, at, *gapx)
    page.polylines(fit(lines["w"]), RL.GREY, RL.T.W_NEW * 0.55)
    if cand:
        page.polylines(fit(lines["c"]), RL.INK, RL.T.W_NEW * 1.15)
    foot_labels(page, RL, G, at, box, *gapx)
    page.clip_rect_end()
    page.text((box[0] + box[2] / 2, box[1] - RL.T.BADGE_R * 1.15), title,
              RL.T.BADGE_R * 0.8, anchor="middle", weight="bold")
    return at, k


def foot_labels(page, RL, G, at, box, x0, x1):
    """What the reader is looking at: the two faces, and the gap between them.

    The same four marks on all three panels, anchored to model points, so the
    only thing that changes across the sheet is the black part.
    """
    w = RL.T.W_NEW * 0.75
    s = RL.T.BADGE_R * 0.62
    dim_y = G.PASSAGE_Y[1] + 70.0                 # out in the room, in front
    a, b = at((x0, dim_y, 0)), at((x1, dim_y, 0))
    page.line(a, b, RL.GREY, w)
    for p in (a, b):
        page.line((p[0], p[1] - RL.T.BADGE_R * 0.45),
                  (p[0], p[1] + RL.T.BADGE_R * 0.45), RL.GREY, w)
    page.text(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - RL.T.BADGE_R * 0.95),
              f"{x1 - x0:.0f} mm", s, anchor="middle", colour=RL.GREY,
              weight="bold")
    # The two feet the gap is between, named in the two bottom corners of the
    # frame with a leader back to the front bottom corner the 142 mm is
    # measured from. Which name goes in which corner is decided by where the
    # camera actually puts the two members, not assumed.
    feet = [("STIGEVANGE", at((x1, G.LADDER_Y1, 0))),
            ("SOFAENDE", at((x0, G.FRONT_RAIL_Y1, 0)))]
    feet.sort(key=lambda f: f[1][0])
    for (lbl, foot), fx in zip(feet, (0.15, 0.85)):
        anchor = (box[0] + box[2] * fx, box[1] + RL.T.BADGE_R * 1.1)
        page.line((anchor[0], anchor[1] + RL.T.BADGE_R * 0.6), foot,
                  RL.GREY, w * 0.7)
        page.text(anchor, lbl, s, anchor="middle", colour=RL.GREY)


def foot_sheet(RL, G, path):
    centre, gap, thr, ext, asis = foot_scene(G)
    opts = [
        ("i   TERSKELKLOSS", thr,
         f"På gulvet, tåa kan treffe den; D13-passasjeregelen må endres. "
         f"{G.BENCH_RAIL_T}×{G.BENCH_RAIL_H} lagt flatt, {gap:.0f} mm fra "
         f"stubbefotens innerende til stigevangens utside. Gangpassasjen er "
         f"ikke lenger fri fra gulvet: du får en {G.BENCH_RAIL_T} mm terskel "
         f"å tråkke over."),
        ("ii  VANGEFORLENGER", ext,
         f"Kne-høyde, gulvet åpent; gulvåpningen inn i boden 700→"
         f"{G.LADDER_CLEAR} mm. Samme {G.BENCH_RAIL_T}×{G.BENCH_RAIL_H} som "
         f"benkevangen, i vangens eget plan og høydebånd (Z "
         f"{G.BENCH_RAIL_BOTTOM}..{G.BENCH_RAIL_TOP}). Tåspalten under er "
         f"urørt, og ingenting ligger tvers over gulvet."),
        ("iii SOM I DAG", asis,
         "Luken åpen; stigen holdes fremover kun av toppskruene (J3), "
         "dokumentert som Avvik 2. Platen er énveis stiver bakover, "
         "veggfestet (J14) holder resten av rammen. Ingen ny del, ingen "
         "regel gitt opp."),
    ]
    pad = 60.0
    cell = 470.0
    cap_h = RL.T.BADGE_R * (2.5 + 5 * 1.05)
    box_y = pad + cap_h
    w = pad * 4 + cell * 3
    h = box_y + cell + pad * 3.8
    page = RL.Page(0, 0, w, h)
    page.text((pad, h - pad * 0.9), "STIGEFOTENS FREMOVER-FESTE — TRE VALG",
              RL.T.BADGE_R * 1.4, weight="bold")
    y = h - pad * 1.4
    for line in _wrap(
            f"Alle tre svarer på det samme: stigevangens fot har ingenting å "
            f"ta i framover — den henger på skruene opp i den fremre "
            f"sidevangen (J3), og de tre fyller, eller lar stå, de "
            f"{gap:.0f} mm mellom sofaenden og stigevangen. Samme utsnitt og "
            f"samme kamera i alle tre: venstre stigefot lavt fra rommet. "
            f"Grått = sengen som den er i dag, svart = delen valget legger "
            f"til, og den lyse flaten på gulvet er D13-gangpassasjen, som "
            f"regelen krever fri. INGEN av dem er bygget: de svarte klossene "
            f"er tegnet for dette arket alene, og står ikke i modellen, i "
            f"kappelisten eller på beslaglisten.", 118):
        page.text((pad, y), line, RL.T.BADGE_R * 0.8)
        y -= RL.T.BADGE_R * 1.15
    for i, (title, cand, body) in enumerate(opts):
        box = (pad + i * (cell + pad), box_y, cell, cell)
        draw_foot(RL, G, page, box, centre, title, cand,
                  (centre[0] - gap / 2, centre[0] + gap / 2))
        y = box[1] - RL.T.BADGE_R * 2.5
        for line in _wrap(body, 52):
            page.text((box[0], y), line, RL.T.BADGE_R * 0.72)
            y -= RL.T.BADGE_R * 1.05
    page.write(path + ".svg", 1800)
    RL.to_png(path + ".svg", path + ".png", 1800)
    return path + ".png"


def main():
    import generate_loftbed as G
    import render_lineart as RL
    RL.use_model(G)
    os.makedirs(OUT, exist_ok=True)
    if "--stigefot" in sys.argv:
        made = [foot_sheet(RL, G, os.path.join(OUT, "stigefot-valg"))]
    else:
        made = [sheet(RL, G, "bed_mode", os.path.join(OUT, "mekanisme-v2-bed")),
                sheet(RL, G, "table_mode",
                      os.path.join(OUT, "mekanisme-v2-table")),
                lock_sheet(RL, G, os.path.join(OUT, "laasvalg"))]
    for p in made:
        print(f"  wrote {p}")


if __name__ == "__main__":
    main()
