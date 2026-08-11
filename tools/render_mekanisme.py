"""V3 proof sheets: the two guide battens seated, and the three lock options.

Three pages, all drawn off the model through the same hidden-line machinery
every manual page uses - so nothing here can show a part the bed does not
have, or show it anywhere but where the model puts it:

  docs/preview/mekanisme-v2-bed.png     the two corners in BED mode
  docs/preview/mekanisme-v2-table.png   the same two corners in TABLE mode
  docs/preview/laasvalg.png             the three bed-mode lock options, all
                                        drawn at the corner each would live in

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
# across the 24 mm side gap. The two faces are side by side, in one Z band and
# one Y band, in BED mode - and 223 mm apart in table mode, where the lock
# therefore has nothing to take hold of. A lock that cannot be left on in the
# wrong position is a property of the geometry, not of the instructions.
LOCKS = [
    ("i   SKRUE — verktøy kreves",
     "Flattstål 60×24×3 lagt over spalten, to treskruer 5×40 i hver ende — "
     "én ned i tverrlekta, én ned i vangeenden. EN 747 4.1.1: en omstilling "
     "som krever verktøy er den konforme grunnlinjen. Koster en skrutrekker "
     "hver gang platen skal flyttes."),
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
    for i, (title, body) in enumerate(LOCKS):
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
    half = G.LOCK_GAP / 2 + 18.0          # the strap laps 18 mm onto each end
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


def main():
    import generate_loftbed as G
    import render_lineart as RL
    RL.use_model(G)
    os.makedirs(OUT, exist_ok=True)
    made = [sheet(RL, G, "bed_mode", os.path.join(OUT, "mekanisme-v2-bed")),
            sheet(RL, G, "table_mode",
                  os.path.join(OUT, "mekanisme-v2-table")),
            lock_sheet(RL, G, os.path.join(OUT, "laasvalg"))]
    for p in made:
        print(f"  wrote {p}")


if __name__ == "__main__":
    main()
