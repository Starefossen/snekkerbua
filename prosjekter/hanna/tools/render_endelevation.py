#!/usr/bin/env python3
"""KORTSIDEN, drawn: docs/schematics/end-elevation.svg.

The bed seen from its end - one vertical section through the left end beam,
in the Y-Z plane, with the wall on the left and the room on the right. It is
the only sheet in the folder that shows the bed's DEPTH as a whole, and the
one thing it exists to say is that the bed is ASYMMETRIC: 1402 mm at the wall,
2037 mm towards the room, no guard boards at the back because the wall is the
barrier. Every storey the bed has - stub foot, bench, cushion, table ledger,
loft frame, slat bed, mattress, the two guard bands - stacks up in one column
on this sheet, and the climb up to the bunk is the same column read as steps.

WHAT IS IN THE SECTION AND WHAT IS NOT
--------------------------------------
The cut is at X = SECTION_X, through the left end beam, and it is viewed
towards the wall end (-X). That is a rule, not a choice per part:

    x0 < SECTION_X < x1     cut by the plane      - hatched or greyed
    x1 <= SECTION_X         beyond the plane      - light, thin outline
    x0 >= SECTION_X         in front of the plane - not drawn

The one deliberate exception is the LOOSE PANEL, which lives at X 708..1282
and is therefore in front of the plane in both its positions. It is drawn
dashed anyway, and labelled as being out of section, because the two heights
it rests at are the whole point of the bed and this is the sheet that has the
room to show them against the storeys around them.

WHERE THE NUMBERS COME FROM
---------------------------
generate_loftbed.py, and nothing else. Every rectangle is a part's own
bounding box, every level on the Z ladder is read off a named part, and every
screw drawn is a placed fastener with its own anchor and direction. The only
things typed here are the ones the model has no opinion about: how big the
paper is, where on it a note goes, and what the note says.

Counts included (X13): the slats and the cushions are COUNTED in the model,
never typed, and assert_counts_ink() reads every count back out of the finished
SVG and holds it up against that same tally - so a bed that gains a slat or a
cushion stops the build rather than quietly disagreeing with its own drawing.

Usage:
    python tools/render_endelevation.py [--out docs/schematics/end-elevation.svg]

Deterministic: no clock, no id(), no set iteration into the output. Two runs
give byte-identical files, and `mise run check` says so.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "tools"))

from schematic import Sheet, nb                       # noqa: E402

OUT = os.path.join(ROOT, "docs", "schematics", "end-elevation.svg")

# ---------------------------------------------------------------------------
# THE SHEET
# ---------------------------------------------------------------------------
# The hand-drawn sheets in this folder are 3450 units wide, and this one is
# too - so its type, strokes, arrows and hatch are the family's own numbers
# with no scaling at all (STYLE_K = 1). The old hand-drawn end elevation was
# 3110 wide and drew its own type sizes; that is exactly the drift this
# rewrite removes.
FAMILY_W = 3450.0
STYLE_K = 1.0
SHEET_W = FAMILY_W
SHEET_H = 2800.0
ORIGIN = (0.0, 150.0)

MARG = 120.0
VIEW_X0 = 340.0             # where Y = -48 (the wall face) lands
VIEW_Z0 = 2530.0            # where Z = 0 (the floor) lands
K = 1.25                    # sheet units per model millimetre

LAD_X = 1470.0              # the Z ladder's tick column
LAB_X = 1520.0              # ... and its text column
NOTE_X = 2400.0             # the notes column
NOTE_W = SHEET_W - MARG - NOTE_X

EXTRA_CSS = """    .behind{ fill:#e6e6e6; stroke:#000; stroke-width:1.7; }
    .soft { fill:#f4f4f4; stroke:#000; stroke-width:2.2;
           stroke-dasharray:17 9; }
    .pnl1 { fill:none; stroke:#000; stroke-width:3.4;
           stroke-dasharray:26 6 5 6; }
    .pnl2 { fill:none; stroke:#000; stroke-width:2.0;
           stroke-dasharray:13 8; }
    .wallf{ fill:none; stroke:#000; stroke-width:5; }
    .flr  { fill:none; stroke:#000; stroke-width:5; }
    .scrp { fill:#000; stroke:none; }
    .scro { fill:#fff; stroke:#000; stroke-width:2.2; }
"""


def why(y):
    """Model Y (depth, wall at -48) to sheet x."""
    return VIEW_X0 + K * (y + 48.0)


def zed(z):
    """Model Z (height) to sheet y - up on the page is up in the room."""
    return VIEW_Z0 - K * z


# ---------------------------------------------------------------------------
# WHAT THE MODEL KNOWS
# ---------------------------------------------------------------------------
class Model:
    """The parts this sheet draws, sorted into the three cases the cut plane
    makes - plus the lookups the annotation needs."""

    def __init__(self, G):
        self.G = G
        self.by_label = {}
        wood = [p for p in G.mode_parts(G.panel_bed)
                if getattr(p, "group", None) != "figures"]
        extra = ([G.panel_table] + G.PANEL_BATTENS[id(G.panel_table)]
                 + G.CUSHIONS[id(G.panel_table)])
        for p in wood + extra:
            self.by_label[p.label] = p
        # The section plane: through the left end beam, clear of its faces.
        (bx0, bx1), _, _ = self.by_label["End Beam Left"].extents
        self.section_x = round((bx0 + bx1) / 2.0, 3)
        self.cut = [p for p in wood if self._cut(p)]
        self.beyond = [p for p in wood if self._beyond(p)]
        self.table_extra = [p for p in extra
                            if self._cut(p) or self._beyond(p)]

    def _cut(self, p):
        (x0, x1), _, _ = p.extents
        return x0 < self.section_x < x1

    def _beyond(self, p):
        (_, x1), _, _ = p.extents
        return x1 <= self.section_x

    def box(self, label):
        return self.by_label[label].extents

    def z(self, label, end):
        return self.by_label[label].extents[2][0 if end == 0 else 1]

    def y(self, label, end):
        return self.by_label[label].extents[1][0 if end == 0 else 1]

    def screws(self, x_lo, x_hi):
        """Placed fasteners whose anchor sits in the end zone this section
        looks at, newest-to-oldest order removed: sorted, so the file is."""
        out = []
        for fs in self.G.FASTENER_SPECS:
            a = fs.get("anchor")
            if a is None or not (x_lo <= a[0] <= x_hi):
                continue
            out.append((round(a[0], 3), round(a[1], 3), round(a[2], 3),
                        tuple(round(v, 6) for v in fs["direction"]),
                        fs["jid"]))
        return sorted(set(out))

    def rows(self, jid, axis=2):
        """The screw ladder of one joint, along one axis."""
        return sorted({round(fs["anchor"][axis], 1)
                       for fs in self.G.FASTENER_SPECS
                       if fs["jid"] == jid and fs.get("anchor") is not None})

    def count(self, stem):
        """Hvor mange deler modellen faktisk bygde med denne navnestammen -
        «Bed Slat_1», «Bed Slat_2», … Telt, aldri skrevet inn."""
        return sum(1 for lab in self.by_label if lab.startswith(stem))

    def cushions(self):
        """De fysiske putene, i rekkefølge langs X slik de ligger i
        sengestilling.

        CUSHIONS_ALL bygger de to ryggputene TO ganger - én gang per stilling -
        så lengden av den lista er ikke antall skumklosser. Klossene er de
        DISTINKTE navnene med stillingen strøket, og hver av dem tas i sin
        sengestilling, for det er der alle fire ligger på rad i samme flate.
        Asserten under gjør at en pute som bare finnes i bordstilling feller
        arket i stedet for å forsvinne stille ut av tellingen."""
        run = []
        seen = []
        for c in self.G.CUSHIONS_ALL:
            stem = c.label.split(" (")[0]
            if "(table mode)" in c.label or stem in seen:
                continue
            seen.append(stem)
            run.append(c)
        stems = {c.label.split(" (")[0] for c in self.G.CUSHIONS_ALL}
        assert len(run) == len(stems), (
            f"modellen har {len(stems)} puter, men bare {len(run)} av dem har "
            f"en sengestilling å ligge i")
        return sorted(run, key=lambda c: c.extents[0][0])

    def dim(self, part, axis):
        """Én kant av en del, målt langs én akse."""
        lo, hi = part.extents[axis]
        return round(hi - lo, 1)


# ---------------------------------------------------------------------------
# THE VIEW
# ---------------------------------------------------------------------------
# Which pen a part is drawn with follows its colour GROUP in the model, so a
# new part lands on this sheet in the right weight without anyone touching a
# list here.
CUT_CLASS = {"rails": "wood", "posts": "wood", "boards": "brd",
             "mattress": "soft", "panel": "pnl1"}


def rect(sh, box, cls):
    (_, _), (y0, y1), (z0, z1) = box
    sh.rect(why(y0), zed(z1), K * (y1 - y0), K * (z1 - z0), cls)


def draw_view(sh, M):
    G = M.G
    # -- the room the bed stands in ----------------------------------------
    wall_y = M.y("Corner Post Back Left", 0)
    sh.line((why(wall_y), zed(1780)), (why(wall_y), zed(-60)), "wallf")
    for i in range(30):
        z = -40 + i * 62.0
        sh.line((why(wall_y), zed(z)), (why(wall_y) - 34.0, zed(z) - 34.0),
                "ext")
    sh.line((why(wall_y) - 60.0, zed(0)), (why(880), zed(0)), "flr")

    # -- beyond the plane, then the cut ------------------------------------
    for p in sorted(M.beyond, key=lambda q: q.label):
        rect(sh, p.extents, "behind")
    for p in sorted(M.cut, key=lambda q: q.label):
        if getattr(p, "group", None) == "mattress":
            continue
        rect(sh, p.extents, CUT_CLASS.get(p.group, "brd"))
    for p in sorted(M.cut, key=lambda q: q.label):
        if getattr(p, "group", None) == "mattress":
            rect(sh, p.extents, "soft")

    # -- the other position, dashed ----------------------------------------
    for p in sorted(M.table_extra, key=lambda q: q.label):
        rect(sh, p.extents, "pnl2" if p.group == "panel" else "soft")

    # -- the loose panel: out of section, drawn anyway ---------------------
    for label, cls in (("Movable Panel (bed mode)", "pnl1"),
                       ("Movable Panel (table mode)", "pnl2")):
        rect(sh, M.box(label), cls)

    # -- the fasteners this end has ----------------------------------------
    for x, y, z, d, jid in M.screws(0.0, 260.0):
        if abs(d[0]) > 0.5:                      # driven along the bed: out
            sh.circle((why(y), zed(z)), 9.0, "scro")   # of the drawing plane
            sh.circle((why(y), zed(z)), 3.4, "scrp")
        else:
            tail = 46.0
            sh.line((why(y), zed(z)),
                    (why(y) + d[1] * tail, zed(z) - d[2] * tail), "scrl")
            sh.circle((why(y), zed(z)), 6.0, "scrp")


# ---------------------------------------------------------------------------
# THE MEMBERS, NAMED
# ---------------------------------------------------------------------------
# The bed is hollow between the two long sides, and that hollow is where the
# member names go: haloed text right on the drawing, next to the piece it
# names. Nothing is typed but the name - the section and the length are the
# part's own bounding box.
NAMED = [
    # label,                            Y of the text, Z, Y of the member the
    #                                   leader runs out to (None = it is on it)
    ("Upper Side Rail Front", 60.0, 1114.0, None),
    ("End Beam Left", 60.0, 1016.0, None),
    ("Bed Slat_1", 60.0, 1222.0, ("z", 1174.0)),
    ("Mattress 200x80 (reference)", 60.0, 1300.0, None),
    ("Guard Rail Front Left_2", 60.0, 1623.0, ("y", 716.0)),
    ("Corner Post Front Left", 60.0, 1460.0, ("y", 752.0)),
    ("Corner Post Back Left", 60.0, 860.0, ("y", -12.0)),
    ("Table Ledger Back", 60.0, 648.0, None),
    ("Bench Rail Back (continuous)", 60.0, 225.0, None),
    ("Bench Slat Left_1", 60.0, 320.0, ("z", 272.0)),
    ("Seat Cushion Left", 60.0, 366.0, None),
    ("Back Cushion Left (table mode)", 200.0, 560.0, None),
]

# Norsk prosa skriver små antall med bokstaver, og modellen kjenner bare
# heltallet. Denne tabellen er den ærlige broen over det gapet: TALLET telles
# fortsatt i modellen, det er bare STAVEMÅTEN som står her. Et antall utenfor
# tabellen skrives med siffer - da er det uansett for stort til å skrives med
# bokstaver på et arbeidsark.
TALLORD = {1: "én", 2: "to", 3: "tre", 4: "fire", 5: "fem", 6: "seks",
           7: "sju", 8: "åtte", 9: "ni", 10: "ti", 11: "elleve", 12: "tolv"}


def tallord(n):
    return TALLORD.get(n, str(n))


def names(M):
    """Navnet hver del får på arket. Ordene er dette arkets egne; hvert ANTALL
    i dem telles i modellen, på samme måte som trinnstigen leser RUNG_TOPS -
    får sengen en spile til, følger teksten etter av seg selv."""
    return {
        "Upper Side Rail Front": "Sidevange, øvre — bak og front",
        "End Beam Left": "Endebjelke — henger i sine egne skruer",
        "Bed Slat_1":
            f"Køyespile — {M.count('Bed Slat_')} like, én lengde",
        "Mattress 200x80 (reference)": "Madrass (referanse, ikke en del)",
        "Guard Rail Front Left_2": "Rekkverksbord, front — to bånd",
        "Corner Post Front Left": "Hjørnestolpe, front",
        "Corner Post Back Left": "Hjørnestolpe, bak — i veggplanet",
        "Table Ledger Back": "Bordbærelekt, bak",
        "Bench Rail Back (continuous)":
            "Benkevange — bak gjennomgående, front i to biter",
        "Bench Slat Left_1":
            f"Benkespile — {M.count('Bench Slat Left_')} per benk",
        "Seat Cushion Left": "Benkepute",
        "Back Cushion Left (table mode)":
            "Ryggpute, på høykant i sofastilling",
    }


def spec(M, label):
    """A part's section and length, written the way the cut list writes it -
    the two small sides as the section, the long one as the length."""
    e = M.box(label)
    d = sorted(round(hi - lo, 1) for (lo, hi) in e)
    return f"{nb(d[0], 0)}×{nb(d[1], 0)} × {nb(d[2], 0)}"


def draw_names(sh, M):
    NAMES = names(M)
    for label, y, z, target in NAMED:
        txt = f"{NAMES[label]}   {spec(M, label)}"
        sh.text((why(y), zed(z)), txt, "smh")
        if target is None:
            continue
        # A name that does not sit ON its member gets a line to it, because a
        # label floating in the middle of a hollow bed names nothing. The line
        # leaves the END of the text it belongs to, never crosses it.
        wide = len(txt) * sh.sz["sml"] * 0.52
        mid = zed(z) - sh.sz["sml"] * 0.32
        kind, val = target
        if kind == "z":
            sh.line((why(y) - 14.0, mid), (why(y) - 14.0, zed(val)), "ext")
        elif val > y:
            sh.line((why(y) + wide + 16.0, mid), (why(val), mid), "ext")
        else:
            sh.line((why(y) - 16.0, mid), (why(val), mid), "ext")


# ---------------------------------------------------------------------------
# THE Z LADDER - every storey the bed has, in one column
# ---------------------------------------------------------------------------
def levels(M):
    """(z, text) read off named parts. The names are the model's own labels;
    the words are this sheet's."""
    G = M.G
    L = [
        (0.0, "gulv"),
        (M.z("Bench Rail Back (continuous)", 0), "uk benkevange"),
        (M.z("Bench Rail Back (continuous)", 1),
         "ok benkevange = trinn 1 = platen i sengestilling"),
        (M.z("Bench Slat Left_1", 1), "benkeflate uten pute"),
        (M.z("Seat Cushion Left", 1),
         "puteoverside = sittehøyde = nedre soveflate"),
        (M.z("Table Ledger Back", 0), "uk bordbærelekt"),
        (M.z("Table Ledger Back", 1),
         f"ok bordbærelekt = trinn {G.CLIMB_LANDING + 1} = platen i "
         f"bordstilling"),
        (M.z("Movable Panel (table mode)", 1), "bordplate — pulthøyde"),
        (M.z("Back Cushion Left (table mode)", 1),
         "ryggputas topp i sofastilling"),
        # Trinn 1 er ok benkevange og står allerede over (RUNG_TOPS[0] ER
        # BENCH_RAIL_TOP), så stigen leses fra indeks 1 og ut. Håndlista var
        # 2-3-4 og mistet det femte trinnet da even_climb ga fem  [was 4].
        # X16: og støttetrinnet står allerede over på bordbærelektas linje -
        # samme høyde, samme strek - så det hoppes over her av samme grunn.
        *[(M.z(f"Ladder Rung_{i + 1}", 1), f"trinn {i + 1}")
          for i in range(1, len(G.RUNG_TOPS)) if i != G.CLIMB_LANDING],
        (M.z("End Beam Left", 0), "uk endebjelke — står fritt"),
        (M.z("End Beam Left", 1),
         "ok endebjelke = uk sidevange = ok bakre stolpe"),
        (M.z("Upper Side Rail Front", 1), "ok sidevange"),
        (M.z("Bed Slat_1", 1), "spilebunn = uk madrass"),
        (M.z("Mattress 200x80 (reference)", 1),
         f"ok madrass ({nb(G.MATTRESS_H, 0)} mm)"),
        (M.z("Guard Rail Front Left_1", 0), "uk nedre rekkverksbånd"),
        (M.z("Guard Rail Front Left_1", 1), "ok nedre rekkverksbånd"),
        (M.z("Guard Rail Front Left_2", 0), "uk øvre rekkverksbånd"),
        (M.z("Guard Rail Front Left_2", 1), "ok øvre rekkverksbånd"),
        (M.z("Corner Post Front Left", 1), "ok fremre stolpe"),
    ]
    return sorted(L, key=lambda r: -r[0])


def draw_ladder(sh, M):
    """The levels, spread so no two labels sit on top of each other. A label
    that has been pushed keeps a leader back to the height it belongs to, so
    the spreading never turns into a wrong reading."""
    rows = levels(M)
    lead = sh.sz["sml"] * 1.42
    ys = []
    for z, _ in rows:
        y = zed(z) + sh.sz["sml"] * 0.36
        if ys and y - ys[-1] < lead:
            y = ys[-1] + lead
        ys.append(y)
    right = why(M.y("Corner Post Front Left", 1))
    for (z, txt), y in zip(rows, ys):
        sh.line((right + 24.0, zed(z)), (LAD_X, zed(z)), "ext")
        if abs(y - (zed(z) + sh.sz["sml"] * 0.36)) > 1.0:
            sh.pline([(LAD_X, zed(z)), (LAD_X + 26.0, zed(z)),
                      (LAD_X + 52.0, y - sh.sz["sml"] * 0.34)], "ext")
        sh.text((LAB_X, y), f"{nb(z, 0)}   {txt}", "sml")
    return right


# ---------------------------------------------------------------------------
# THE WIDTH DIMENSIONS
# ---------------------------------------------------------------------------
def draw_depth(sh, M):
    y_free0 = M.y("Upper Side Rail Back", 1)
    y_free1 = M.y("Upper Side Rail Front", 0)
    y_slat0 = M.y("Bed Slat_1", 0)
    y_slat1 = M.y("Bed Slat_1", 1)
    y_all0 = M.y("Corner Post Back Left", 0)
    y_all1 = M.y("Corner Post Front Left", 1)

    base = zed(0) + 96.0
    sh.dim((why(y_free0), base), (why(y_free1), base),
           f"{nb(y_free1 - y_free0, 0)}  fri bredde mellom sidevangene",
           0.0, 1, "dmh")
    sh.dim((why(y_slat0), base + 108.0), (why(y_slat1), base + 108.0),
           f"{nb(y_slat1 - y_slat0, 0)}  spilebunn = madrassbredden",
           0.0, 1, "dmh")
    sh.dim((why(y_all0), base + 216.0), (why(y_all1), base + 216.0),
           f"{nb(y_all1 - y_all0, 0)}  dybde over alt", 0.0, 1, "dmh")

    # The mattress window and the two guard openings - the EN 747 chain.
    mz = M.z("Mattress 200x80 (reference)", 1)
    g1 = M.z("Guard Rail Front Left_1", 0)
    g1t = M.z("Guard Rail Front Left_1", 1)
    g2 = M.z("Guard Rail Front Left_2", 0)
    xg = why(M.y("Guard Rail Front Left_1", 1)) + 150.0
    sh.dim((xg, zed(mz)), (xg, zed(g1)), nb(g1 - mz, 0), 0.0, 1, "dmh")
    sh.dim((xg, zed(g1t)), (xg, zed(g2)), nb(g2 - g1t, 0), 0.0, 1, "dmh")
    lo, hi = M.G.EN_LIMB_BAND
    sh.text((xg + 30.0, zed(g1) - 8.0), "EN 747: begge åpninger i båndet "
            f"{nb(lo, 0)}–{nb(hi, 0)}", "sml")


# ---------------------------------------------------------------------------
# THE WORDS
# ---------------------------------------------------------------------------
# The thicknesses a mattress is actually SOLD in. Not a model constant - the
# model only knows its own window - but it is the shelf the window has to be
# read against, and the note below names the thinnest shelf height that no
# longer fits rather than asserting one.
SHELF_MATTRESS_H = (80, 100, 110, 120, 130, 140, 150, 160, 180,
                    200)


def notes(M):
    G = M.G
    post_b = M.box("Corner Post Back Left")
    post_f = M.box("Corner Post Front Left")
    rail_b = M.box("Upper Side Rail Back")
    beam = M.box("End Beam Left")
    j1 = M.rows("J1")
    j2 = M.rows("J2")
    j8 = M.rows("J8")
    j1y = M.rows("J1", 1)
    j2x = M.rows("J2", 0)[0]
    mz = M.z("Mattress 200x80 (reference)", 1)
    g1 = M.z("Guard Rail Front Left_1", 0)
    seat = M.z("Seat Cushion Left", 1)
    bench = M.z("Bench Slat Left_1", 1)
    # Den frie dybden madrassen ligger i: veggplanet til de fremre stolpenes
    # innside. Er den lik madrassbredden, er vandringen null.
    depth_clear = (M.y("Corner Post Front Left", 0)
                   - M.y("Corner Post Back Left", 0))
    roam = depth_clear - G.MATTRESS_W
    too_thick = min(t for t in SHELF_MATTRESS_H if t > G.MATTRESS_H_MAX)
    # PUTENE, TELT OG MÅLT. Antallet er antall skumklosser i modellen, tykkelse
    # og dybde er de samme to kantene på hver av dem, og oppdelingen er de fire
    # lengdene lest i rekkefølge langs sengen. Ingen av tallene skrives her.
    cush = M.cushions()
    c_t = sorted({M.dim(c, 2) for c in cush})
    c_d = sorted({M.dim(c, 1) for c in cush})
    seats = [c for c in cush if c.label.startswith("Seat")]
    backs = [c for c in cush if c.label.startswith("Back")]
    seat_len = sorted({M.dim(c, 0) for c in seats})
    back_len = sorted({M.dim(c, 0) for c in backs})
    assert len(c_t) == len(c_d) == len(seat_len) == len(back_len) == 1, (
        f"putene er ikke lenger én tykkelse ({c_t}), én dybde ({c_d}) og to "
        f"lengder ({seat_len}, {back_len}) - da holder ikke setningen under")
    run = [M.dim(c, 0) for c in cush]

    def mm(v):
        return nb(v, 0)

    return [
        ("ASYMMETRISK — SENGEN ER IKKE VENDBAR", [
            f"Bakre langside står mot vegg, og VEGGEN er barrieren: det står "
            f"ingen rekkverksbord bak. De to bakre hjørnestolpene er kappet i "
            f"Z {mm(post_b[2][1])}, og den bakre sidevangen bærer rett ned på "
            f"stolpens endeved. Foran går stolpene helt til "
            f"{mm(post_f[2][1])}.",
            f"Bakre stolpe ligger i veggplanet Y {mm(post_b[1][0])} … "
            f"{mm(post_b[1][1])}; vangen står {mm(rail_b[1][1] - post_b[1][1])}"
            f" mm fram for den. Ingenting stikker bak veggplanet.",
        ]),
        ("SKRUERADER I RAMMELEDDENE", [
            "Ingen bolt går inn i en stolpe. En 36 mm stolpe gir en M8 bare "
            "18 mm kantavstand mot kravet 24 (3d); en forboret 6 mm treskrue "
            "trenger 18. Det finnes ikke et forsenket boltehode i denne sengen.",
            f"J1  endebjelke → stolpe:  Z {mm(j1[0])} og {mm(j1[-1])}, "
            f"i planene Y {mm(j1y[0])} og {mm(j1y[-1])}",
            f"J2  fremre sidevange → stolpe:  Z {mm(j2[0])} og {mm(j2[-1])}, "
            f"X {nb(j2x, 1)} fra enden",
            f"J8  fremre benkevange → stolpe:  Z {mm(j8[0])} og {mm(j8[-1])}",
            "J2 og J8 er SNUDD: hodet ligger på vangens innside og skruen går "
            "utover i +Y inn i stolpen. Ingen skruehoder står på noen flate "
            "framfor de fremre stolpene — det er en assert i modellen.",
        ]),
        ("INGEN BÆREKLOSS NOE STED I RAMMEN", [
            f"Endebjelkens underkant, Z {mm(beam[2][0])}, er fri. Bjelken "
            f"henger i sine egne to skruer i hver ende, og de tar hele "
            f"vertikallasten: 4,0 kN i skjær mot under 1 kN hjørnereaksjon. "
            f"Det samme gjelder benkevangene.",
        ]),
        ("J14 VEGGFESTE — OBLIGATORISK", [
            "6 treskruer rett gjennom den bakre sidevangen og inn i "
            "stenderne. Ingen brakett, ingen kloss: vangen ligger flatt mot "
            "veggen i hele sin lengde, så festet gir midtopplegg også.",
        ]),
        ("MADRASSVINDUET", [
            f"Madrassen er {mm(G.MATTRESS_W)} mm bred og fyller dybden mellom "
            f"veggen og de fremre stolpene nøyaktig — {mm(roam)} mm vandring, "
            f"{mm(roam / 2.0)} mm spalte i hver ende. Tykkelsen er et VINDU: "
            # [X10: sto som 140–155 / tegnet 150 i ren tekst her - V7-tall
            #  som U1/X1 hadde flyttet under føttene på arket. Historikken
            #  hører hjemme i kilden, ikke på et ark en snekker leser.]
            f"{mm(G.MATTRESS_H_MIN)}–{mm(G.MATTRESS_H_MAX)} mm. Tegnet er "
            f"{mm(G.MATTRESS_H)}, som gir {mm(g1 - mz)} mm opp til nedre "
            f"rekkverksbånd. Tynnere enn {mm(G.MATTRESS_H_MIN)} og åpningen "
            f"blir over {mm(G.MAX_GUARD_OPENING)}; tykkere enn "
            f"{mm(G.MATTRESS_H_MAX)} og den faller ned i klemvinduet under "
            f"{mm(G.EN_LIMB_BAND[0])}. Vinduet er trangt: allerede en vanlig "
            f"{mm(too_thick)} mm madrass er ulovlig her, og alt over den "
            f"også.",
            # X18: og dette arket tegner den BYGDE sengen, der rekkverket
            # står 65 mm høyere enn tegnet. Vinduet flyttet seg med bordet;
            # madrassen gjorde det ikke.
            f"SOM BYGGET: nederste rekkverksbord står "
            f"{mm(G.AS_BUILT_GUARD_RISE)} mm over madrasstoppen, ikke "
            f"{mm(G.MATTRESS_H_WINDOW_DRAWN[0] + G.MAX_GUARD_OPENING - G.MATTRESS_H)}"
            f", så åpningen er {mm(G.AS_BUILT_MATTRESS_GAP)} mm mot grensen "
            f"{mm(G.MAX_GUARD_OPENING)} — {mm(G.AS_BUILT_GAP_OVER)} mm for "
            f"mye, og ingen avstivere i det båndet. Madrassen på senga er "
            f"{mm(G.MATTRESS_H)} mm og vinduet over krever "
            f"{mm(G.MATTRESS_H_MIN)}. Se vedlegg B, avvik 6.",
        ]),
        ("BENKEN, PUTENE OG DEN LØSE PLATEN", [
            f"Benkeflaten ligger på Z {mm(bench)} og puteoversiden på "
            f"{mm(seat)}. Det er {tallord(len(cush)).upper()} puter, alle "
            f"{mm(c_t[0])} mm tykke og {mm(c_d[0])} mm dype: "
            f"{tallord(len(seats))} benkeputer på {mm(seat_len[0])} mm og "
            f"{tallord(len(backs))} ryggputer på {mm(back_len[0])} mm. "
            f"{' + '.join(mm(v) for v in run)} = {mm(sum(run))} — hele "
            f"lengden.",
            f"I sofastilling står ryggputa på høykant ytterst på hver benk, "
            f"med toppen på Z "
            f"{mm(M.z('Back Cushion Left (table mode)', 1))} og ryggen mot "
            f"bordbærelekta. Den er tegnet stiplet her.",
            f"Ytterst mot veggenden ligger endespilen, "
            f"{spec(M, 'Bench End Slat Left')}, på sin endelist, "
            f"{spec(M, 'Bench End Cleat Left')} (J17). Den starter på den "
            f"bakre stolpens forside og lukker feltet helt ut til veggen: "
            f"spalten inn til første benkespile er 0 mm. Begge ligger bak "
            f"snittplanet og er tegnet lyse.",
            f"Den løse platen ligger IKKE i dette snittet — den er "
            f"{mm(M.box('Movable Panel (bed mode)')[0][1] - M.box('Movable Panel (bed mode)')[0][0])}"
            f" mm bred og står midt i sengen, X "
            f"{mm(M.box('Movable Panel (bed mode)')[0][0])}–"
            f"{mm(M.box('Movable Panel (bed mode)')[0][1])}. Begge stillingene "
            f"er tegnet inn i høyde, fordi det er de to høydene resten av "
            f"snittet skal leses mot.",
        ]),
    ]


def draw_notes(sh, M):
    y = zed(1780)
    for head, rows in notes(M):
        sh.text((NOTE_X, y), head, "leg")
        y += sh.sz["leg"] * 1.5
        for row in rows:
            wrapped = sh.wrap(row, NOTE_W)
            y = sh.lines((NOTE_X, y), wrapped, "sml") + sh.sz["sml"] * 1.35
        y += sh.sz["sml"] * 0.9
    return y


LEGEND = [
    ("wood", "Vange, endebjelke, bordbærelekt og stolpe I SNITT"),
    ("brd", "Bord i snitt: køyespile, benkespile, rekkverksbord"),
    ("behind", "Del BAK snittplanet (mot veggenden)"),
    ("soft", "Madrass og puter — referanse, ikke en del"),
    ("pnl1", "Løs plate, sengestilling (utenfor snittet)"),
    ("pnl2", "Løs plate og sofastilling, bordstilling (utenfor snittet)"),
]


def draw_legend(sh, y):
    x = NOTE_X
    sh.text((x, y), "TEGNFORKLARING", "leg")
    y += sh.sz["leg"] * 1.6
    for cls, txt in LEGEND:
        sh.rect(x, y - sh.sz["sml"] * 0.85, 90.0, sh.sz["sml"] * 1.1, cls)
        sh.text((x + 112.0, y), txt, "sml")
        y += sh.sz["sml"] * 1.55
    sh.circle((x + 32.0, y - sh.sz["sml"] * 0.3), 9.0, "scro")
    sh.circle((x + 32.0, y - sh.sz["sml"] * 0.3), 3.4, "scrp")
    sh.text((x + 112.0, y), "Treskrue ut av tegningsplanet (langs X)", "sml")
    y += sh.sz["sml"] * 1.55
    sh.line((x + 32.0, y - sh.sz["sml"] * 0.3),
            (x + 78.0, y - sh.sz["sml"] * 0.3), "scrl")
    sh.circle((x + 32.0, y - sh.sz["sml"] * 0.3), 6.0, "scrp")
    sh.text((x + 112.0, y), "Treskrue i tegningsplanet — prikken er hodet",
            "sml")
    return y


# ---------------------------------------------------------------------------
# ASSERTEN SOM LESER BLEKKET
# ---------------------------------------------------------------------------
# X13: de to antallene på dette arket - spilene og putene - sto som tall i
# teksten, riktige den dagen de ble skrevet. Nå telles de i modellen, og denne
# asserten leser dem TILBAKE UT AV DEN FERDIGE SVG-EN og holder dem opp mot
# modellens egen telling. Får sengen én spile eller én pute til uten at arket
# følger med, stopper bygget her - som på spikerslagsarket, der de skraverte
# feltene leses tilbake ut av blekket på samme måte.
_TXT_RE = re.compile(r"<text\b[^>]*>(.*?)</text>")


def _ink(path):
    """All teksten arket faktisk skrev, som én streng. Notatene brytes over
    flere linjer, så setningene settes sammen igjen med mellomrom før de
    leses - ellers avhenger asserten av hvor linjeskiftet tilfeldigvis falt."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    words = [b.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
             for b in _TXT_RE.findall(text)]
    return " ".join(words)


def assert_counts_ink(path, M):
    """Hvert antall som STÅR på arket, mot det modellen har bygd."""
    ink = _ink(path)
    checked = 0
    for pattern, want, hva in (
            (r"Køyespile — (\d+) like", M.count("Bed Slat_"), "køyespiler"),
            (r"Benkespile — (\d+) per benk", M.count("Bench Slat Left_"),
             "benkespiler per benk")):
        found = re.findall(pattern, ink)
        assert len(found) == 1, \
            f"fant {len(found)} steder som teller {hva} på arket, venter ett"
        assert int(found[0]) == want, (
            f"arket sier {found[0]} {hva}, men modellen har bygd {want}")
        checked += 1

    cush = M.cushions()
    found = re.findall(r"Det er ([A-ZÆØÅ]+) puter", ink)
    assert len(found) == 1, \
        f"fant {len(found)} steder som teller putene på arket, venter ett"
    assert found[0] == tallord(len(cush)).upper(), (
        f"arket sier {found[0]} puter, men modellen har bygd "
        f"{len(cush)} ({tallord(len(cush)).upper()})")
    checked += 1

    # ... og oppdelingen, som er de samme putene en gang til: lengdene i
    # rekkefølge langs sengen, og summen som SKAL være hele soveflaten.
    found = re.findall(r"((?:\d+ \+ )+\d+) = (\d+) — hele lengden", ink)
    assert len(found) == 1, \
        f"fant {len(found)} pute-regnestykker på arket, venter ett"
    run = [int(v) for v in found[0][0].split(" + ")]
    want = [int(M.dim(c, 0)) for c in cush]
    assert run == want, (
        f"regnestykket på arket deler soveflaten i {run}, men putene i "
        f"modellen måler {want}")
    assert int(found[0][1]) == sum(want) == int(M.G.LOWER_SLEEP_LEN), (
        f"putene summerer til {sum(want)} mm, arket skriver {found[0][1]} og "
        f"soveflaten er {M.G.LOWER_SLEEP_LEN} mm")
    checked += 1
    return checked


# ---------------------------------------------------------------------------

def build(G, M=None):
    # Samme modell tegner arket og leser blekket etterpå - ellers kunne de to
    # i prinsippet svare på hvert sitt sengeutkast.
    M = Model(G) if M is None else M
    sh = Sheet(SHEET_W, SHEET_H, STYLE_K,
               "Loftseng - kortside, snitt A-A",
               width=2400, origin=ORIGIN, extra_css=EXTRA_CSS)
    sh.text((MARG, 250.0), "KORTSIDE — ENDRAMMEN, SNITT A–A (Y–Z)", "ttl")
    sh.text((MARG, 310.0),
            f"Snitt ved X = {nb(M.section_x, 0)} gjennom endebjelken i venstre "
            f"ende, sett mot veggenden · veggen (Y = "
            f"{nb(M.y('Corner Post Back Left', 0), 0)}) til venstre, romsiden "
            f"(Y = {nb(M.y('Corner Post Front Left', 1), 0)}) til høyre · "
            f"alle mål i mm", "sub")
    draw_view(sh, M)
    draw_names(sh, M)
    draw_ladder(sh, M)
    draw_depth(sh, M)
    y = draw_notes(sh, M)
    draw_legend(sh, y + 40.0)
    sh.text((MARG, SHEET_H + ORIGIN[1] - 40.0),
            "Alle mål er lest ut av generate_loftbed.py — ingen av dem er "
            "skrevet inn her. Generert av tools/render_endelevation.py; "
            "rediger ikke for hånd.", "tiny")
    return sh


def main(argv):
    out = OUT
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    import generate_loftbed as G
    M = Model(G)
    build(G, M).write(out)
    n = assert_counts_ink(out, M)
    print(f"wrote {out}  ({n} antall på arket lest tilbake ut av blekket og "
          f"målt mot modellen)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
