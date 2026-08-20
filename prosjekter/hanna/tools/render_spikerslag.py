#!/usr/bin/env python3
"""BAKVEGGEN, drawn: docs/schematics/spikerslag.svg.

The wall the bed hangs on, seen as an elevation - X along the niche, Z up from
the finished floor - with the zones that have to have noggings in them marked
out. It is the one sheet in the folder that is not a drawing of the bed at
all: it is a drawing of the WALL, and it is drawn because the wall is closed
before the bed is built. What is not in the wall when the plasterboard goes up
is not going in later.

WHERE THE ZONES COME FROM
-------------------------
generate_loftbed.py's WALL_ZONES, and nothing else. A zone is a (height band,
cut-list line) the model worked out from the geometry: a part lying on the
wall face whose length runs along the wall presses on it over that whole
length, and a part on the wall face that is also flush with an end wall stands
in the corner. This sheet draws one hatched field per PART in those zones -
its own X extent, its own Z band - so the two corner columns come out 98 mm
wide because that is how wide the back posts are, and the long bands stop at
the post faces because that is where the members stop.

Every height on the sheet is measured from the FINISHED FLOOR, Z = 0 - and,
after X8b, ALSO from the height line, in brackets beside it. The line is
MEASURE_DATUM_Z, struck round the niche with a laser 1000 mm over the floor;
it is drawn here too, thin, and the model asserts that it falls on bare wall
between two zones - a line struck across a nogging is a line you cannot see
once the bed is up. The second notation exists because the floor is out of
level and the line is not: at the open wall you set a zone by pulling the tape
from the laser, not by finding the floor. Minus is below the line, plus above.

WHICH WAY ROUND X RUNS
----------------------
The same way the cut list says it does: X = 0 is the left end wall,
X = WALL_SPAN the right one. That is the convention every other document in
this folder measures in, and a sheet that flipped it to suit one eye position
would make every X in the cut list read backwards against it.

THE ASSERT
----------
The sheet is written, then READ BACK: every hatched field in the finished SVG
is converted from sheet units to model millimetres and has to be the X extent
and Z band of a part in WALL_ZONES. A zone the model grew and the drawing did
not is a failed build, not a drawing to be noticed later. The second height
notation is read back the same way: every height written in both is subtracted
on the finished sheet and has to differ by exactly MEASURE_DATUM_Z.

Usage:
    python tools/render_spikerslag.py [--out docs/schematics/spikerslag.svg]

Deterministic: no clock, no id(), no set iteration into the output.
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

OUT = os.path.join(ROOT, "docs", "schematics", "spikerslag.svg")

# ---------------------------------------------------------------------------
# THE SHEET
# ---------------------------------------------------------------------------
# 3450 units wide, like every other sheet in the folder, so the type, strokes,
# arrows and hatch are the family's own numbers unscaled (STYLE_K = 1).
FAMILY_W = 3450.0
STYLE_K = 1.0
SHEET_W = FAMILY_W
SHEET_H = 2900.0            # X8b: +140 for the second height notation in the
                            # notes column - the sheet grew, the type did not
ORIGIN = (0.0, 150.0)

MARG = 120.0
VIEW_X0 = 470.0             # where X = 0 (the left end wall) lands
VIEW_Z0 = 1780.0            # where Z = 0 (the finished floor) lands
K = 1.0                     # sheet units per model millimetre

AIR_OVER = 150.0            # wall drawn this far above the topmost zone
LAD_X = 2560.0              # the height ladder's tick column
LAB_X = 2610.0              # ... and its text column
CHAIN_X = VIEW_X0 - 110.0   # the vertical dimension chain, left of the wall

NOTE_Y = 2300.0             # the prose panel
NOTE_X = (MARG, 1800.0)
NOTE_W = 1520.0

# `.zonekey` is the same ink as `.zone` under another name, and the reason is
# the assert at the bottom of this file: it reads every `zone` rectangle back
# off the finished sheet and demands it be a part in WALL_ZONES. The swatch in
# the legend is a picture OF a zone, not a zone, so it must not answer that
# question - it would answer it wrong.
EXTRA_CSS = """    .zone, .zonekey { fill:url(#hatch); stroke:#000;
           stroke-width:2.6; }
    .wallf{ fill:none; stroke:#000; stroke-width:5; }
    .flr  { fill:none; stroke:#000; stroke-width:5; }
    .face { fill:none; stroke:#000; stroke-width:1.7; }
    .scrp { fill:#000; stroke:none; }
    .scro { fill:#fff; stroke:#000; stroke-width:2.2; }
"""


def ex(x):
    """Model X (along the wall, 0 = left end wall) to sheet x."""
    return VIEW_X0 + K * x


def zed(z):
    """Model Z (height over the finished floor) to sheet y."""
    return VIEW_Z0 - K * z


def un_ex(sx):
    return (sx - VIEW_X0) / K


def un_zed(sy):
    return (VIEW_Z0 - sy) / K


# ---------------------------------------------------------------------------
# WHAT THE MODEL KNOWS
# ---------------------------------------------------------------------------
class Model:
    """The wall zones, flattened into the fields this sheet draws."""

    def __init__(self, G, idx):
        self.G = G
        self.idx = idx
        by_label = {p.label: p for p in G.CUT_PARTS}
        self.fields = []            # one hatched field per part in a zone
        self.zones = []             # one entry per WALL_ZONES entry
        for n, zo in enumerate(G.WALL_ZONES, 1):
            z0, z1 = zo["z"]
            name = idx[zo["labels"][0]][0]
            spans = []
            for label in zo["labels"]:
                (x0, x1), _, _ = by_label[label].extents
                spans.append((round(x0, 3), round(x1, 3)))
                self.fields.append(dict(n=n, x0=x0, x1=x1, z0=z0, z1=z1,
                                        name=name, corner=zo["corner"]))
            self.zones.append(dict(n=n, z0=z0, z1=z1, name=name,
                                   corner=zo["corner"], spans=sorted(spans),
                                   count=len(zo["labels"]),
                                   riss=zo["riss"], riss_txt=zo["riss_txt"]))
        self.z_top = max(z["z1"] for z in self.zones) + AIR_OVER
        # The J14 wall fixing: the screws that make the whole thing a rule
        # rather than a suggestion. Anchors are the model's own.
        self.fix = sorted({(round(fs["anchor"][0], 3), round(fs["anchor"][2], 3))
                           for fs in G.FASTENER_SPECS
                           if fs["jid"] == "J14"
                           and fs.get("anchor") is not None})

    def datum_gap(self):
        """The two bare-wall heights the height line is struck between."""
        bands = sorted((z["z0"], z["z1"]) for z in self.zones
                       if not z["corner"])
        d = self.G.MEASURE_DATUM_Z
        return (max(z1 for z0, z1 in bands if z1 <= d),
                min(z0 for z0, z1 in bands if z0 >= d))


# ---------------------------------------------------------------------------
# THE VIEW
# ---------------------------------------------------------------------------
def draw_wall(sh, M):
    """The niche itself: floor, two end walls, and the bare face between."""
    G = M.G
    x0, x1 = ex(0.0), ex(G.WALL_SPAN)
    top = zed(M.z_top)
    base = zed(0.0)
    sh.rect(x0, top, x1 - x0, base - top, "plain")
    # The two end walls and the floor are the three surfaces the model draws
    # as perfect planes and the room does not have. They get the heavy line
    # and the hatch ticks that say "this is building, not furniture".
    for sx, sgn in ((x0, -1.0), (x1, 1.0)):
        sh.line((sx, top - 40.0), (sx, base), "wallf")
        n = int((base - (top - 40.0)) // 62.0)
        for i in range(n + 1):
            y = top - 40.0 + i * 62.0
            sh.line((sx, y), (sx + sgn * 34.0, y - 34.0), "ext")
    sh.line((x0 - 60.0, base), (x1 + 60.0, base), "flr")
    for i in range(int((x1 + 60.0 - (x0 - 60.0)) // 62.0) + 1):
        x = x0 - 60.0 + i * 62.0
        sh.line((x, base), (x - 34.0, base + 34.0), "ext")


def draw_zones(sh, M):
    """One hatched field per part, plus the badge that ties it to the table."""
    for fl in sorted(M.fields, key=lambda f: (f["n"], f["x0"])):
        sh.rect(ex(fl["x0"]), zed(fl["z1"]), K * (fl["x1"] - fl["x0"]),
                K * (fl["z1"] - fl["z0"]), "zone")
    for fl in sorted(M.fields, key=lambda f: (f["n"], f["x0"])):
        cx = ex((fl["x0"] + fl["x1"]) / 2.0)
        cy = zed((fl["z0"] + fl["z1"]) / 2.0)
        if fl["corner"]:
            cy = zed(fl["z1"] - 150.0)
        r = 26.0
        sh.circle((cx, cy), r, "picf")
        sh.text((cx, cy + sh.sz["pt"] * 0.36), str(fl["n"]), "pt", "middle")


def draw_zone_names(sh, M):
    """The part each zone carries, written where the field has room for it."""
    G = M.G
    for z in M.zones:
        txt = (f"{z['name']} — {nb(z['z0'], 0)}–{nb(z['z1'], 0)} over gulv  ·  "
               f"{z['riss_txt']}")
        if z["corner"]:
            # A 98 mm column has no room for words. The two corner fields are
            # named once, on the bare wall between the bands, each pointing at
            # its own side.
            mid = (M.datum_gap()[0] + M.datum_gap()[1]) / 2.0
            lo = min(s[0] for s in z["spans"])
            hi = max(s[1] for s in z["spans"])
            sh.text((ex(lo) + 90.0, zed(mid)), txt, "smh")
            sh.text((ex(hi) - 90.0, zed(mid) + sh.sz["sml"] * 1.5), txt,
                    "smh", "end")
            continue
        # OVER the band, not in it: zone 4 has the six wall fixings inside it,
        # and a name written across a screw is a name that has to be moved by
        # hand the next time the model moves a screw.
        x0 = min(s[0] for s in z["spans"])
        sh.text((ex(x0) + 20.0, zed(z["z1"]) - sh.sz["sml"] * 0.55), txt,
                "smh")


def draw_datum(sh, M):
    """The height line the whole fitting job is measured from."""
    G = M.G
    d = G.MEASURE_DATUM_Z
    sh.line((ex(0.0) - 120.0, zed(d)), (ex(G.WALL_SPAN) + 120.0, zed(d)),
            "ctr")
    sh.text((ex(0.0) + 150.0, zed(d) - sh.sz["sml"] * 0.5),
            f"HØYDERISS {nb(d, 0)} OVER FERDIG GULV — 0 I RISS-NOTASJONEN "
            f"(MINUS ER UNDER, PLUSS ER OVER)", "smh")


def draw_fixings(sh, M):
    """J14 - the screws through the back side rail into the wall."""
    if not M.fix:
        return
    for x, z in M.fix:
        sh.circle((ex(x), zed(z)), 12.0, "scro")
        sh.circle((ex(x), zed(z)), 4.5, "scrp")
    z = M.fix[0][1]
    sh.text((ex(M.fix[0][0]), zed(M.z_top) + 46.0),
            f"{len(M.fix)} × veggfeste (J14) i Z {nb(z, 0)} — "
            f"de skal treffe stender eller spikerslag", "smh")


# ---------------------------------------------------------------------------
# THE DIMENSIONS - every one of them from the finished floor
# ---------------------------------------------------------------------------
def draw_heights(sh, M):
    """The vertical chain: floor to zone edge to zone edge, all the way up."""
    stations = sorted({0.0} | {z["z0"] for z in M.zones}
                      | {z["z1"] for z in M.zones})
    x = CHAIN_X
    for a, b in zip(stations, stations[1:]):
        sh.dim((x, zed(a)), (x, zed(b)), nb(b - a, 0), 0.0, 1, "dmh")
        sh.line((ex(0.0), zed(b)), (x - 16.0, zed(b)), "ext")
    sh.line((ex(0.0), zed(stations[0])), (x - 16.0, zed(stations[0])), "ext")


def ladder(M):
    """(z, text) - every height on this wall, read off the model."""
    G = M.G
    L = [(0.0, "ferdig gulv — alle mål herfra")]
    for z in M.zones:
        low = f"uk {z['name'].lower()}"
        high = f"ok {z['name'].lower()}"
        if z["z0"] > 0.0:
            L.append((z["z0"], f"{low} — sone {z['n']} begynner"))
        L.append((z["z1"], f"{high} — sone {z['n']} slutter"))
    L.append((float(G.MEASURE_DATUM_Z), "høyderiss (laser rundt hele nisja)"))
    for _x, z in M.fix[:1]:
        L.append((z, "veggfeste J14"))
    return sorted(L, key=lambda r: (-r[0], r[1]))


def draw_ladder(sh, M):
    """The heights, spread so no two labels sit on top of one another."""
    rows = ladder(M)
    lead = sh.sz["sml"] * 1.42
    ys = []
    for z, _ in rows:
        y = zed(z) + sh.sz["sml"] * 0.36
        if ys and y - ys[-1] < lead:
            y = ys[-1] + lead
        ys.append(y)
    right = ex(M.G.WALL_SPAN)
    for (z, txt), y in zip(rows, ys):
        sh.line((right + 24.0, zed(z)), (LAD_X, zed(z)), "ext")
        if abs(y - (zed(z) + sh.sz["sml"] * 0.36)) > 1.0:
            sh.pline([(LAD_X, zed(z)), (LAD_X + 26.0, zed(z)),
                      (LAD_X + 52.0, y - sh.sz["sml"] * 0.34)], "ext")
        sh.text((LAB_X, y),
                f"{nb(z, 0)}   ({M.G.riss_num(z)} fra risset)   {txt}", "sml")


def draw_widths(sh, M):
    """One dimension row per distinct field width, then the niche itself."""
    rows, order = {}, []
    for z in M.zones:
        key = tuple(z["spans"])
        if key not in rows:
            rows[key] = []
            order.append(key)
        rows[key].append(z["n"])
    base = zed(0.0) + 120.0
    for key in order:
        ns = rows[key]
        for a, b in key:
            sh.dim((ex(a), base), (ex(b), base), nb(b - a, 0), 0.0, 1, "dmh")
        word = "sone " + (" og ".join(str(n) for n in ns) if len(ns) < 3
                          else ", ".join(str(n) for n in ns))
        sh.text((LAD_X, base + sh.sz["dm"] * 0.36), word, "sml")
        base += 95.0
    sh.dim((ex(0.0), base), (ex(M.G.WALL_SPAN), base),
           f"{nb(M.G.WALL_SPAN, 0)}  nisjas bredde, vegg til vegg", 0.0, 1,
           "dmh")
    return base


# ---------------------------------------------------------------------------
# THE WORDS
# ---------------------------------------------------------------------------
def notes(M, T):
    G = M.G
    below, above = M.datum_gap()
    corner = [z for z in M.zones if z["corner"]]
    bands = [z for z in M.zones if not z["corner"]]
    zone_lines = [
        f"Sone {z['n']}:  {nb(z['z0'], 0)}–{nb(z['z1'], 0)} over ferdig gulv  "
        f"=  {z['riss_txt']} — {z['name']}"
        + (f" ({z['count']} stk., ett felt i hvert hjørne)"
           if z["count"] > 1 else "")
        for z in M.zones
    ]
    return [
        ("LEGG SPIKERSLAG MENS VEGGEN ER ÅPEN", [
            f"Sengen presser på bakveggen i {len(M.zones)} bånd, ikke overalt. "
            f"Her er båndene. Legger du spikerslag i dem før veggen lukkes, "
            f"kan du feste sengen hvor som helst i sonen. Etterpå kommer du "
            f"ikke til.",
        ] + zone_lines),
        ("HØYDERISSET", [
            f"Slå et vannrett riss rundt hele nisja med linjelaser, "
            f"{nb(G.MEASURE_DATUM_Z, 0)} mm over ferdig gulv. Alle høyder på "
            f"dette arket er målt fra ferdig gulv, og på veggen måler du dem "
            f"ned eller opp fra risset — aldri fra gulvet.",
            f"Derfor står hver høyde to ganger: over ferdig gulv, og i "
            f"parentes det samme tallet minus {nb(G.MEASURE_DATUM_Z, 0)} — "
            f"minus er under laserlinja, pluss er over. Gulvet er skjevt og "
            f"risset er ikke, så det er parentesen du setter sonene etter.",
            f"Risset ligger på bar vegg mellom sone-toppen {nb(below, 0)} og "
            f"sone-bunnen {nb(above, 0)}, så det er synlig helt til sengen "
            f"står inntil. Det er en assert i modellen.",
            _plain(T.ROOM_ZONE_NOTE),
        ]),
        ("HJØRNENE", [
            f"De to feltene i hjørnene går fra gulvet og opp til "
            f"{nb(corner[0]['z1'], 0)}, og de er "
            f"{nb(corner[0]['spans'][0][1] - corner[0]['spans'][0][0], 0)} mm "
            f"brede — bredden på den bakre hjørnestolpen. Stolpen står i "
            f"veggplanet uten klaring, mot både endeveggen og bakveggen, så "
            f"det er i disse to smale feltene hele endekreftene tas.",
        ]),
        ("VEGGFESTET", [
            f"{len(M.fix)} skruer gjennom den bakre sidevangen og inn i "
            f"veggen, i Z {nb(M.fix[0][1], 0)} — inne i sone "
            f"{[z['n'] for z in bands if z['z0'] <= M.fix[0][1] <= z['z1']][0]}"
            f". Ingen brakett, ingen kloss: vangen ligger flatt mot veggen i "
            f"hele sin lengde. Treffer en skrue verken stender eller "
            f"spikerslag, er festet verdiløst — det er derfor sonen skal "
            f"ligge der før platen skrus opp.",
        ]),
        ("HVA ARKET IKKE SIER", [
            "Hvor stenderne står. Det vet huset, ikke modellen. Sonene er "
            "høydene og breddene sengen trenger tre bak; hvordan du får tre "
            "dit — spikerslag mellom stendere, gjennomgående lekt eller en "
            "hel plate — er veggens sak.",
        ]),
    ]


def _plain(md):
    """A markdown line as the drawing writes it - no asterisks on a sheet."""
    return md.replace("**", "")


def draw_notes(sh, M, T):
    blocks = notes(M, T)
    half = (len(blocks) + 1) // 2
    for col, group in ((0, blocks[:half]), (1, blocks[half:])):
        x = NOTE_X[col]
        y = NOTE_Y
        for head, rows in group:
            sh.text((x, y), head, "leg")
            y += sh.sz["leg"] * 1.5
            for row in rows:
                y = sh.lines((x, y), sh.wrap(row, NOTE_W), "sml") \
                    + sh.sz["sml"] * 1.35
            y += sh.sz["sml"] * 0.9
    return y


LEGEND = [
    ("zonekey",
     "Sone som skal ha spikerslag — hele feltet, ikke bare en linje"),
    ("plain", "Bar vegg — ingenting av sengen ligger inntil"),
]


def draw_legend(sh, x, y):
    sh.text((x, y), "TEGNFORKLARING", "leg")
    y += sh.sz["leg"] * 1.6
    for cls, txt in LEGEND:
        sh.rect(x, y - sh.sz["sml"] * 0.85, 90.0, sh.sz["sml"] * 1.1, cls)
        sh.text((x + 112.0, y), txt, "sml")
        y += sh.sz["sml"] * 1.55
    sh.line((x, y - sh.sz["sml"] * 0.3), (x + 90.0, y - sh.sz["sml"] * 0.3),
            "ctr")
    sh.text((x + 112.0, y), "Høyderiss over ferdig gulv", "sml")
    y += sh.sz["sml"] * 1.55
    sh.circle((x + 45.0, y - sh.sz["sml"] * 0.3), 12.0, "scro")
    sh.circle((x + 45.0, y - sh.sz["sml"] * 0.3), 4.5, "scrp")
    sh.text((x + 112.0, y), "Veggfeste (J14) — skrue inn i veggen", "sml")
    return y


# ---------------------------------------------------------------------------
# THE ASSERT THAT READS THE INK
# ---------------------------------------------------------------------------
_ZONE_RE = re.compile(
    r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" '
    r'height="([\d.]+)" class="zone"/>')


def assert_zone_ink(path, M):
    """Every hatched field on the finished sheet, converted back to model
    millimetres, has to be a part in WALL_ZONES - and every part in WALL_ZONES
    has to have a field."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    drawn = []
    for sx, sy, sw, sh_ in _ZONE_RE.findall(text):
        x0 = un_ex(float(sx))
        x1 = un_ex(float(sx) + float(sw))
        z1 = un_zed(float(sy))
        z0 = un_zed(float(sy) + float(sh_))
        drawn.append(tuple(round(v, 2) for v in (x0, x1, z0, z1)))
    want = sorted(tuple(round(v, 2) for v in (f["x0"], f["x1"],
                                              f["z0"], f["z1"]))
                  for f in M.fields)
    assert sorted(drawn) == want, (
        f"de skraverte feltene på arket er ikke sonene i modellen:\n"
        f"  tegnet:  {sorted(drawn)}\n"
        f"  modell:  {want}")
    return len(drawn)


# X8b - AND THE SAME TREATMENT FOR THE SECOND NOTATION. Every height on the
# ladder is written twice on this sheet - over the finished floor, and from
# the height line - and the second one is only worth anything if it really is
# the first one minus the datum. So the finished SVG is read back and the
# subtraction is done on the INK: one line that disagrees, or a datum that
# moved and took only one of the two with it, stops the build.
_RISS_RE = re.compile(r">(\d+)   \(([-+]?\d+) fra risset\)")


def assert_riss_ink(path, M):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    found = _RISS_RE.findall(text)
    assert len(found) == len(ladder(M)), \
        (f"{len(found)} høyder på arket er skrevet i begge notasjoner, men "
         f"høydestigen har {len(ladder(M))} rader")
    for z, r in found:
        assert float(z) - float(r) == float(M.G.MEASURE_DATUM_Z), \
            (f"høyden {z} er skrevet som {r} fra risset: differansen er "
             f"{float(z) - float(r)}, og den SKAL være høyderisset selv, "
             f"{M.G.MEASURE_DATUM_Z}")
    return len(found)


# ---------------------------------------------------------------------------

def build(G, T):
    idx = T.cut_index(G)
    M = Model(G, idx)
    sh = Sheet(SHEET_W, SHEET_H, STYLE_K,
               "Loftseng - bakveggen, spikerslagsoner",
               width=2400, origin=ORIGIN, extra_css=EXTRA_CSS)
    sh.text((MARG, 250.0), "BAKVEGGEN — SPIKERSLAGSONER, OPPRISS (X–Z)", "ttl")
    sh.text((MARG, 310.0),
            f"Veggen sengen skrus fast i, sett som oppriss · X langs veggen "
            f"(0 = venstre endevegg, {nb(G.WALL_SPAN, 0)} = høyre) · Z opp fra "
            f"FERDIG GULV · alle mål i mm · legg spikerslagene FØR veggen "
            f"lukkes", "sub")
    draw_wall(sh, M)
    draw_zones(sh, M)
    draw_zone_names(sh, M)
    draw_datum(sh, M)
    draw_fixings(sh, M)
    draw_heights(sh, M)
    draw_ladder(sh, M)
    draw_widths(sh, M)
    y = draw_notes(sh, M, T)
    draw_legend(sh, NOTE_X[1], y + 40.0)
    sh.text((MARG, SHEET_H + ORIGIN[1] - 40.0),
            "Alle soner, høyder og bredder er lest ut av generate_loftbed.py "
            "(WALL_ZONES) — ingen av dem er skrevet inn her. Generert av "
            "tools/render_spikerslag.py; rediger ikke for hånd.", "tiny")
    return sh, M


def main(argv):
    out = OUT
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    import generate_loftbed as G
    import gen_doc_tables as T
    sh, M = build(G, T)
    sh.write(out)
    n = assert_zone_ink(out, M)
    nr = assert_riss_ink(out, M)
    print(f"wrote {out}  ({n} skraverte felt i "
          f"{len(M.zones)} soner, {nb(M.z_top, 0)} mm vegg tegnet, "
          f"{nr} høyder skrevet både over gulv og fra høyderisset)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
