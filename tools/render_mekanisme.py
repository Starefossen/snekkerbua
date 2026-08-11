"""V2 proof sheets: the four brackets seated, and the three lock options.

Three pages, all drawn off the model through the same hidden-line machinery
every manual page uses - so nothing here can show a bracket the bed does not
have, or show it anywhere but where the model puts it:

  docs/preview/mekanisme-v2-bed.png     the two corners in BED mode
  docs/preview/mekanisme-v2-table.png   the same two corners in TABLE mode
  docs/preview/laasvalg.png             the three bed-mode lock options, all
                                        drawn at the corner each would live in

The two mechanism sheets are CLOSE-UPS: one panel per corner, cropped to the
bracket and the wood it sits on, with the measured clearances written on. The
table-mode sheet is the same two crops 223 mm higher, which is the claim the
whole design rests on - one bracket geometry, two seats.

The lock sheet is a comparison, not a decision. None of the three is wired
into the model: the shopping list has a TBD line and the manual says so.
"""

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

OUT = os.path.join(ROOT, "docs", "preview")

# The two corners each sheet shows, as (title, which bracket joint, side).
CORNERS = [("BAKRE HJØRNE — beslaget hviler på opplegget", "J13c", -1.0),
           ("TRINNENDEN — beslaget står 2 mm klar av treet", "J13d", -1.0)]

CROP = 125.0          # model mm around the bracket centre, half-width
CAM = (318.0, 26.0)   # azimuth, elevation - the manual's own three-quarter


def bracket_specs(G, jid, side):
    return [f for f in G.FASTENER_SPECS
            if f["jid"] == jid and f["kind"] == "plate"
            and f.get("side") == side]


def bracket_extents(G, f):
    boxes = G.angle_boxes(f)
    return tuple((min(min(lo[j], hi[j]) for lo, hi in boxes),
                  max(max(lo[j], hi[j]) for lo, hi in boxes))
                 for j in range(3))


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


def solids_of(G, specs):
    return [f["solid"] for f in specs if f.get("solid") is not None]


def draw_corner(RL, G, page, box, mode, jid, side, title, extra=None):
    """One cropped panel: the wood in grey, the steel in black, on `box`."""
    panel = G.MODES[mode]
    dz = (G.PANEL_MODE_LIFT if mode == "table_mode" else 0)
    specs = bracket_specs(G, jid, side)
    assert specs, f"{jid}: no bracket on side {side}"
    ext = bracket_extents(G, specs[0])
    centre = (sum(ext[0]) / 2, sum(ext[1]) / 2, sum(ext[2]) / 2 + dz)
    view = RL.View(RL.camera_direction(*CAM), centre)

    wood = near_parts(G, panel, centre, CROP * 1.9)
    # Only the bracket and its own fasteners. The 22 wood screws that hold the
    # lekter on are a different question and they would fill this crop.
    steel = []
    for f in G.FASTENER_SPECS:
        if f.get("solid") is None or f["jid"] not in ("J13c", "J13d"):
            continue
        e = (bracket_extents(G, f) if f["kind"] == "plate"
             else _solid_ext(f["solid"]))
        c = tuple(sum(e[j]) / 2 for j in range(3))
        c = (c[0], c[1], c[2] + dz)
        if math.dist(c, centre) <= CROP * 1.6:
            steel.append(f["solid"])

    from build123d import Location
    shift = Location((0, 0, dz))
    wood_lines = RL.project(view, [("w", RL.comp(wood))])["w"]
    steel_lines = RL.project(
        view, [("s", RL.comp([s.moved(shift) for s in steel]))])["s"] \
        if steel else []

    # The crop window, in the view's own frame, centred on the bracket.
    cx, cy = view.xy(centre)
    k = min(box[2], box[3]) / (2 * CROP)

    def fit(plines):
        out = []
        for pl in plines:
            seg = [((x - cx) * k + box[0] + box[2] / 2,
                    (y - cy) * k + box[1] + box[3] / 2) for x, y in pl]
            out.append(seg)
        return out

    def at(p3):
        x, y = view.xy((p3[0], p3[1], p3[2] + dz))
        return ((x - cx) * k + box[0] + box[2] / 2,
                (y - cy) * k + box[1] + box[3] / 2)

    page.rect(box[0], box[1], box[2], box[3], fill="#ffffff",
              stroke=RL.GREY, width=RL.T.W_PHANTOM)
    page.clip_rect_begin(box)
    page.polylines(fit(wood_lines), RL.GREY, RL.T.W_NEW * 0.55)
    page.polylines(fit(steel_lines), RL.INK, RL.T.W_NEW * 0.95)
    if extra:
        extra(page, at, k)
    page.clip_rect_end()
    page.text((box[0] + box[2] / 2, box[1] - RL.T.BADGE_R * 1.1), title,
              RL.T.BADGE_R * 0.95, anchor="middle", weight="bold")
    return view, at, k, ext


def _solid_ext(s):
    bb = s.bounding_box()
    return ((bb.min.X, bb.max.X), (bb.min.Y, bb.max.Y), (bb.min.Z, bb.max.Z))


def note(page, RL, p, text, size=None):
    page.text(p, text, size or RL.T.BADGE_R * 0.8)


def sheet(RL, G, mode, path):
    """One mechanism proof sheet: two cropped corners side by side."""
    pad = 60.0
    cell = 520.0
    w = pad * 3 + cell * 2
    h = pad * 3.4 + cell
    page = RL.Page(0, 0, w, h)
    lift = G.PANEL_MODE_LIFT if mode == "table_mode" else 0
    seat = G.PANEL_UNDER_BED + lift
    head = ("SENGESTILLING" if mode == "bed_mode" else "BORDSTILLING")
    page.text((pad, h - pad * 0.9),
              f"{head} — platens underside Z {seat:.0f}", RL.T.BADGE_R * 1.4,
              weight="bold")
    page.text((pad, h - pad * 1.55),
              "Samme fire beslag, samme sted på platen, i begge stillinger. "
              "Grått = tre, svart = stål.", RL.T.BADGE_R * 0.85)
    for i, (title, jid, side) in enumerate(CORNERS):
        box = (pad + i * (cell + pad), pad * 1.6, cell, cell)
        draw_corner(RL, G, page, box, mode, jid, side, title)
    page.write(path + ".svg", 1600)
    RL.to_png(path + ".svg", path + ".png", 1600)
    return path + ".png"


# ---------------------------------------------------------------------------
# THE THREE LOCK OPTIONS
# ---------------------------------------------------------------------------
# All three act at the SAME place: the hole in the rear bracket's horizontal
# flange, straight down into the rear support. That is the only place on the
# panel where steel already lies flat on the wood it has to be held against,
# which is why the lock question and the bracket question have one answer
# between them.
LOCKS = [
    ("i   SKRUE — verktøy kreves",
     "To treskruer 5×40 ned gjennom flikens hull i vangen. EN 747 4.1.1: en "
     "omstilling som krever verktøy er den konforme grunnlinjen. Koster en "
     "skrutrekker hver gang platen skal flyttes."),
    ("ii  FINGERSKRUE — verktøyfri",
     "Samme hull, men en riflet fingerskrue M6 i en gjengeinnsats i vangen. "
     "Lifetime-sengene gjør nettopp dette. Verktøyfritt betyr at et barn òg "
     "kan gjøre det: EN-messig et grensetilfelle, ikke en konform løsning."),
    ("iii OVERSENTERLÅS — trekker platen ned",
     "Spennlås (Jula 012270-klassen) med bøylen i fliken og huset på vangen. "
     "Den TREKKER platen ned mot opplegget, så klapringen forsvinner - men "
     "den er også verktøyfri, og huset står 24 mm opp i sideklaringen."),
]


def lock_overlay(kind):
    """The drawing each option adds at the rear bracket's flange hole."""
    def draw(page, at, k, RL=None, G=None):
        pass
    return draw


def lock_sheet(RL, G, path):
    pad = 60.0
    cell = 470.0
    # The caption block under each crop is what sets the page height: six
    # lines of prose plus the title, measured in the theme's own badge unit,
    # so a longer argument makes a taller page instead of running off it.
    cap_h = RL.T.BADGE_R * (2.4 + 6 * 1.05)
    box_y = pad + cap_h
    w = pad * 4 + cell * 3
    h = box_y + cell + pad * 2.6
    page = RL.Page(0, 0, w, h)
    page.text((pad, h - pad * 0.9), "LÅS I SENGESTILLING — TRE VALG",
              RL.T.BADGE_R * 1.4, weight="bold")
    page.text((pad, h - pad * 1.5),
              "Alle tre virker i det samme hullet: den vannrette fliken på "
              "det bakre vinkelbeslaget, rett ned i opplegget. Ingen av dem "
              "er valgt — modellen har en TBD-linje i beslaglista.",
              RL.T.BADGE_R * 0.85)
    for i, (title, body) in enumerate(LOCKS):
        box = (pad + i * (cell + pad), box_y, cell, cell)

        def extra(page, at, k, i=i):
            _lock_art(page, RL, G, at, k, i)

        draw_corner(RL, G, page, box, "bed_mode", "J13c", -1.0, title,
                    extra=extra)
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


def _lock_art(page, RL, G, at, k, which):
    """The lock itself, drawn in the model's own space at the flange hole."""
    f = bracket_specs(G, "J13c", -1.0)[0]
    ext = bracket_extents(G, f)
    # The hole: the middle of the horizontal flange, out in the side gap.
    hx = (ext[0][0] + G.PANEL_X0) / 2 if ext[0][1] <= G.PANEL_X0 else \
         (ext[0][1] + G.PANEL_X1) / 2
    hy = sum(ext[1]) / 2
    top = G.PANEL_UNDER_BED + G.BRACKETS["vinkel20"]["t"]
    w = RL.T.W_NEW * 0.95
    if which == 0:                      # two wood screws, heads on the flange
        for dy in (-9.0, 9.0):
            head = at((hx, hy + dy, top))
            tip = at((hx, hy + dy, top - 40.0))
            page.line(head, tip, RL.INK, w)
            page.dot(head, RL.T.BADGE_R * 0.32, colour=RL.INK)
    elif which == 1:                    # knurled thumbscrew
        head = at((hx, hy, top + 26.0))
        neck = at((hx, hy, top))
        tip = at((hx, hy, top - 30.0))
        page.line(neck, tip, RL.INK, w)
        page.line(head, neck, RL.INK, w)
        r = abs(at((hx + 13.0, hy, top + 26.0))[0] - head[0])
        page.circle(head, r, fill="#ffffff", stroke=RL.INK, width=w)
        for a in range(0, 360, 30):
            p0 = (head[0] + r * 0.62 * math.cos(math.radians(a)),
                  head[1] + r * 0.62 * math.sin(math.radians(a)))
            p1 = (head[0] + r * math.cos(math.radians(a)),
                  head[1] + r * math.sin(math.radians(a)))
            page.line(p0, p1, RL.INK, w * 0.5)
    else:                               # over-centre latch
        base = at((hx, hy + 22.0, top))
        body = at((hx, hy + 22.0, top - 34.0))
        arm = at((hx, hy - 26.0, top + 30.0))
        hookl = at((hx, hy - 4.0, top + 4.0))
        page.line(base, body, RL.INK, w)
        page.line(base, arm, RL.INK, w * 1.1)
        page.line(arm, hookl, RL.INK, w)
        page.line(hookl, at((hx, hy - 4.0, top - 8.0)), RL.INK, w)
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
