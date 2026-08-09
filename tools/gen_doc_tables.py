"""Emit the generated documentation fragments from the frozen model.

Run by `mise run build`, after the model itself. It does NOT define geometry
and it does NOT touch generate_loftbed.py: it IMPORTS that script (which
builds, validates and exports the model exactly as running it directly does),
then reads its module globals and writes markdown fragments into
docs/generated/, plus the machine-readable build-step description that both
the text guide and the pictorial guide (docs/MONTERING.md) are built from.

THE ANTI-DUPLICATION RULE
-------------------------
Every millimetre that appears in the documentation comes from here, and every
number here comes from generate_loftbed.py. docs/ASSEMBLY.md is allowed to
name parts and to cite J-numbers, but it must never restate a dimension that
one of these fragments already carries - it links to the fragment instead.

WHAT IS WRITTEN
---------------
  docs/generated/kappliste.md      cut list: part, section, length, count,
                                   position extents
  docs/generated/innkjopsliste.md  per profile: which sale lengths to buy,
                                   first-fit cut mapping, waste %
  docs/generated/nokkelmal.md      envelope, heights, depth planes, ladder /
                                   rung / guard coordinates, bolt rows
  docs/generated/byggesteg.md      the full step-by-step build guide
  docs/generated/byggesteg.json    the same steps, machine readable, consumed
                                   by tools/render_steps.py and
                                   tools/gen_montering.py

Nothing here is hand-maintained: rerun `mise run build` and it is all rebuilt.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# SHOP CONVENTIONS
# ---------------------------------------------------------------------------
# Sale lengths of planed Norwegian softwood, in mm. Everything is bought in
# these and cut down; the packer below opens 4800 mm boards and then shrinks
# each one to the shortest sale length that still holds what it was given.
SALE_LENGTHS = [2400, 3000, 3600, 4200, 4800]
KERF = 4                 # saw kerf allowance between two cuts, mm
# v11/U4 took M8 out of every post joint: a 36 mm post face gives an M8 only
# 18 mm of edge distance where EC5 wants 3d = 24. Every joint into a corner
# post is now the 6 mm pre-drilled screw pattern the ladder uprights have used
# all along, and for a 6 mm screw 3d IS 18 mm - exactly what a 36 mm face
# offers on its centre line. No bolt enters a post, and nothing anywhere is
# driven from a face that ends against a wall, so there are no counterbores.
SCREW_D = 6              # mm - the frame screw
MIN_EDGE = 3 * SCREW_D            # 18 mm, unloaded edge / unloaded end
MIN_SPACING_GRAIN = 5 * SCREW_D   # 30 mm, two screws stacked along the grain
MIN_SPACING_CROSS = 4 * SCREW_D   # 24 mm, two screws stacked across the grain


def _fmt(v):
    """Numbers the way a Norwegian tape measure reads them."""
    if isinstance(v, float) and abs(v - round(v)) < 1e-6:
        v = int(round(v))
    if isinstance(v, float):
        # one decimal normally, two when rounding to one would lose the value
        txt = f"{v:.1f}" if abs(v - round(v, 1)) < 1e-9 else f"{v:.2f}"
        return txt.replace(".", ",")
    return str(v)


def _rng(a, b):
    return f"{_fmt(a)}..{_fmt(b)}"


def _no_section(G, section):
    """The model names the panel stock in English; the docs are Norwegian."""
    if "panel" in section:
        return f"{G.PANEL_T} mm plate, {G.PANEL_W} bred"
    return section.replace("x", "×")


def _axis(ranges):
    """One position cell: the common range, or the span the group covers."""
    uniq = sorted(set(ranges))
    if len(uniq) == 1:
        return _rng(*uniq[0])
    return _rng(min(r[0] for r in uniq), max(r[1] for r in uniq)) + " (fordelt)"


# ---------------------------------------------------------------------------
# BOLT ROWS - derived from the frozen member positions, then checked
# ---------------------------------------------------------------------------
def screw_rows(G):
    """Where every M8 goes, computed off the members it passes through.

    Two bolts per joint are stacked symmetrically about the member's own
    centre line, MIN_SPACING_GRAIN apart - that spacing is what the corner
    post needs (the bolts are stacked along ITS grain). The edge distance
    that falls out of it is then checked against the member the bolts pass
    through crossways.
    """
    rows = {}

    def pair(name, z0, z1, member):
        mid = (z0 + z1) / 2
        # Spread the two screws apart, but keep a comfortable 1,5 x MIN_EDGE
        # at each edge rather than sitting on the bare minimum; never closer
        # together than MIN_SPACING_GRAIN.
        span = max(MIN_SPACING_GRAIN, (z1 - z0) - 3 * MIN_EDGE)
        lo, hi = mid - span / 2, mid + span / 2
        assert lo - z0 >= MIN_EDGE, f"{name}: {lo - z0} mm to the lower edge"
        assert z1 - hi >= MIN_EDGE, f"{name}: {z1 - hi} mm to the upper edge"
        assert hi - lo >= MIN_SPACING_GRAIN
        assert hi - lo >= MIN_SPACING_CROSS
        rows[name] = dict(z=[lo, hi], member=member, band=[z0, z1],
                          edge=[lo - z0, z1 - hi], spacing=hi - lo, count=2)

    def single(name, z0, z1, member):
        mid = (z0 + z1) / 2
        assert mid - z0 >= MIN_EDGE and z1 - mid >= MIN_EDGE
        rows[name] = dict(z=[mid], member=member, band=[z0, z1],
                          edge=[mid - z0, z1 - mid], spacing=None, count=1)

    sec = lambda a, b: G.sec(a, b).replace("x", "×")
    pair("J1", G.END_BEAM_Z0, G.END_BEAM_Z1, "endebjelke " + sec(G.RAIL_T, G.RAIL_H))
    pair("J2", G.RAIL_BOTTOM, G.RAIL_TOP, "sidevange " + sec(G.RAIL_T, G.RAIL_H))
    pair("J8", G.BENCH_RAIL_BOTTOM, G.BENCH_RAIL_TOP,
         "benkevange " + sec(G.BENCH_RAIL_T, G.BENCH_RAIL_H))

    # The in-plane position of the J2 / J8 bolts: the middle of the corner
    # post, which is also the middle of the post/rail lap.
    rows["J2"]["x"] = G.POST_W / 2
    rows["J8"]["x"] = G.POST_W / 2
    # ...and of the J1 bolts: the middle of the post depth, at both ends.
    rows["J1"]["y"] = [G.BACK_POST_Y0 + G.POST_T / 2,
                       G.FRONT_POST_Y0 + G.POST_T / 2]

    # The rail end distance the lap leaves us with. The bolt force is
    # perpendicular to the rail's grain, so this is an UNLOADED end and the
    # requirement is 3d; the lap is only POST_W wide, so it is tight.
    rail_end = rows["J2"]["x"] - G.THROUGH_X0
    rows["_rail_end_distance"] = rail_end
    rows["_rail_end_required"] = MIN_EDGE
    return rows




# ---------------------------------------------------------------------------
# LEDD (J-numbers) AND THE HARDWARE THEY EAT - defined ONCE, here
# ---------------------------------------------------------------------------
# `n`     how many of this joint the finished bed has.
# `fast`  [(handelsnavn, antall per ledd), ...]
# `drill` what to pre-drill for it.
# `side`  which side you drive it from - the reason the build order is what
#         it is.
# The prose that explains each joint lives in docs/ASSEMBLY.md; the numbers
# live here and nowhere else. The per-step fastener lines in byggesteg.md and
# MONTERING.md are summed from this table times the step's joint counts, and
# the totals in innkjopsliste / beslagliste are summed from the same place.
JOINTS = [
    dict(id="J1", title="Endebjelke → hjørnestolpe", n=4,
         fast=[("Treskrue 6×90 forsenket Torx", 2)],
         drill="⌀6 gjennom bjelken, ⌀4 i stolpen",
         side="Fra bjelkens utside, inn mot stolpen — helt inne i sengen, "
              "tilgjengelig hele veien"),
    dict(id="J1-B", title="Bærekloss under endebjelke → hjørnestolpe", n=4,
         fast=[("Treskrue 6×90 forsenket Torx", 2)],
         drill="⌀6 gjennom klossen, ⌀4 i stolpen",
         side="Fra klossens frie ende, inn i stolpen"),
    dict(id="J2", title="Fremre sidevange → fremre hjørnestolpe", n=2,
         fast=[("Treskrue 6×80 forsenket Torx", 2)],
         drill="⌀6 gjennom stolpen, ⌀4 i vangen",
         side="Fra stolpens forside, gjennom stolpen inn i vangen"),
    dict(id="J2-B", title="Bakre sidevange → bakre hjørnestolpe "
                          "(vangen hviler på stolpetoppen)", n=2,
         fast=[("Treskrue 6×120 forsenket Torx", 2)],
         drill="⌀6 gjennom vangen, ⌀4 i stolpens endeved; forsenk hodet godt "
               "under vangens overkant så køyespilene ligger flatt",
         side="Rett ned gjennom vangen i stolpetoppen, mens bakrammen ligger "
              "flatt på gulvet. Ingenting på veggsiden, og ingen kloss: "
              "vangen står 12 mm proud av den tynnere stolpen, så et rett "
              "beslag ville uansett ikke ligget an mot begge"),
    dict(id="J3", title="Stigevange → fremre sidevange", n=2,
         fast=[("Treskrue 6×80 forsenket Torx", 4)],
         drill="⌀6 gjennom stigevangen, ⌀4 i sidevangen",
         side="Fra stigevangens forside, inn i vangen"),
    dict(id="J4", title="Rungetrinn → stigekloss og stigevange "
                        "(per trinnende)", n=8,
         fast=[("Treskrue 6×120 forsenket Torx", 1),
               ("Treskrue 5×60 forsenket Torx", 1)],
         drill="⌀6 gjennom stigevangen inn i trinnenden; ⌀3,5 ned gjennom "
               "trinnet i klossen",
         side="6×120 fra utsiden av stigevangen; 5×60 ovenfra ned i klossen"),
    dict(id="J5", title="Stigekloss → stigevange", n=8,
         fast=[("Treskrue 5×60 forsenket Torx", 2)],
         drill="⌀3,5 gjennom klossen, ⌀3 i vangen",
         side="Fra stigeåpningen, inn i vangens innside"),
    dict(id="J6", title="Køyespile → sidevange (per spileende)", n=28,
         fast=[("Treskrue 5×60 forsenket Torx", 1)],
         drill="⌀3,5 gjennom spilen, forsenk hodet under flaten",
         side="Ovenfra, ned i vangen"),
    dict(id="J7", title="Rekkverksbord → hjørnestolpe / stigevange "
                        "(per omlegg)", n=8,
         fast=[("Treskrue 5×60 forsenket Torx", 2)],
         drill="⌀3,5 gjennom bordet, ⌀3 i stolpen",
         side="Fra sengesiden, inn i stolpens/stigevangens innside"),
    dict(id="J8", title="Fremre benkevange → fremre hjørnestolpe", n=2,
         fast=[("Treskrue 6×80 forsenket Torx", 2)],
         drill="⌀6 gjennom stolpen, ⌀4 i vangen",
         side="Fra stolpens forside, gjennom stolpen inn i vangen"),
    dict(id="J8-B", title="Bakre benkevange → bakre hjørnestolpe "
                          "(endeskjøt)", n=2,
         fast=[("Treskrue 6×90 forsenket Torx", 2)],
         drill="⌀6 skrått gjennom vangen, ⌀4 i stolpen — forbor hele veien, "
               "dette er en skråskrue nær en ende",
         side="Skrått fra vangens forside inn i stolpen. Vangen ligger fast "
              "mellom de to stolpene, så skruene er bånd, ikke opplegg"),
    dict(id="J9-B", title="Bærekloss under bakre benkevange → bakre stolpe",
         n=2,
         fast=[("Treskrue 6×90 forsenket Torx", 2)],
         drill="⌀6 gjennom klossen, ⌀4 i stolpen",
         side="Fra klossens frie ende, inn i stolpen"),
    dict(id="J9-F", title="Bærekloss under fremre benkevange → fremre stolpe",
         n=2,
         fast=[("Treskrue 6×70 forsenket Torx", 2)],
         drill="⌀6 gjennom klossen, ⌀4 i stolpen",
         side="Fra klossens bakside, inn i stolpen. Kortere skrue enn de "
              "andre klossene — her er det bare 36 mm stolpe bak klossen"),
    dict(id="J10", title="Benkevange → stubbefot", n=4,
         fast=[("Vinkelbeslag 90×90×65×2,5 varmforsinket", 1),
               ("Treskrue 5×40 forsenket Torx", 4),
               ("Treskrue 5×70 forsenket Torx", 2)],
         drill="⌀3 i foten og i vangen; skråskruene forbores ⌀3,5",
         side="Beslaget på innsiden av foten; de to 5×70 settes som "
              "skråskruer nedenfra og opp i vangen"),
    dict(id="J11", title="Benkespile → benkevange (per spileende)", n=20,
         fast=[("Treskrue 5×60 forsenket Torx", 1)],
         drill="⌀3,5 gjennom spilen, forsenk hodet under flaten",
         side="Ovenfra, ned i benkevangen"),
    dict(id="J12", title="Bordbærelekt → bakre hjørnestolpe (endeskjøt)",
         n=2,
         fast=[("Vinkelbeslag 40×40×40", 1),
               ("Treskrue 5×40 forsenket Torx", 4)],
         drill="⌀3 i stolpen og i lekta — forboring er et krav, lekta er tynn",
         side="Beslaget på stolpens innerflate, under lektas ende, så lekta "
              "har noe å hvile på og ikke bare henger i skruer"),
    dict(id="J13a", title="Avstivningslekt → løs plate", n=2,
         fast=[("Treskrue 5×60 forsenket Torx", 6)],
         drill="⌀3,5 gjennom platen, forsenk og propp",
         side="Ovenfra, ned i lektas overkant"),
    dict(id="J13b", title="U-brakett → løs plate (omslutter trinnet)", n=2,
         fast=[("U-brakett, bøyd av flattstål 30×4", 1),
               ("Senkhodeskrue M6×30 + skive M6 + låsemutter M6", 2)],
         drill="⌀6,5 gjennom platen, forsenk ⌀13 i oversiden",
         side="Ovenfra gjennom platen; mutteren under"),
    dict(id="J13c", title="Krokplate → løs plate (griper om benkevangens "
                          "forkant)", n=2,
         fast=[("Krokplate, bøyd av flattstål 30×4", 1),
               ("Senkhodeskrue M6×30 + skive M6 + låsemutter M6", 2)],
         drill="⌀6,5 gjennom platen, forsenk ⌀13 i oversiden",
         side="Ovenfra gjennom platen; kroken henger ned foran vangen og "
              "vender innover under den. Plasseres i X klar av "
              "avstivningslektene"),
    dict(id="J14", title="Veggfeste — gjennom den bakre sidevangen inn i "
                         "stenderne", n=1,
         fast=[("Veggfeste etter veggtype (treskrue 8×100 i stender, eller "
                "plugg + skrue i mur)", 6)],
         drill="⌀8 gjennom vangen, forsenk for hodet; veggen etter festetype",
         side="Rett gjennom vangen inn i veggen. Vangen ligger flatt mot "
              "veggen i hele sin lengde, så festet trenger ingen kloss og "
              "ingen brakett"),
    dict(id="J15", title="Filtknott under stolpe og stubbefot", n=8,
         fast=[("Filtknott / møbeltapp ⌀40", 1)],
         drill="—",
         side="Slås i endeveden før reisning"),
]
JOINT = {j["id"]: j for j in JOINTS}


def step_fastener_rows(st):
    """[(handelsnavn, antall), ...] for one step, summed from its joints."""
    total = {}
    for jid, cnt in st["joints"].items():
        for name, per in JOINT[jid]["fast"]:
            total[name] = total.get(name, 0) + per * cnt
    return sorted(total.items())


# The letters a step's fastener kinds are badged with. tools/gen_glyphs.py
# draws them and holds the same alphabet.
BADGE_ALPHABET = "ABCDEFGH"


def step_badges(st):
    """{handelsnavn: 'A'} for a step that drives more than one kind of fastener.

    A step with one kind needs no letters - the glyph in its table IS the
    answer, and a badge on every arrow would be noise. A step with several
    does: the letter is what ties an arrow in the drawing to a row in the
    table, so the reader can see which of the three screws goes where.

    The order is the order the inset and the table use: the commonest first,
    ties broken by name. tools/render_lineart.py derives the same letters from
    the same rows, so the drawing and the page can never disagree.
    """
    rows = step_fastener_rows(st)
    if len(rows) < 2:
        return {}
    order = sorted(rows, key=lambda r: (-r[1], r[0]))
    return {name: BADGE_ALPHABET[i] for i, (name, _q) in enumerate(order)}


def step_fastener_summary(st):
    """The fastener line for one step, summed from the joints it completes."""
    return [f"{qty}× {name}" for name, qty in step_fastener_rows(st)]


def hardware_total(steps):
    """Every fastener in the bed, and the check that the steps add up."""
    seen = {}
    for st in steps:
        for jid, cnt in st["joints"].items():
            assert jid in JOINT, f"step {st['n']} cites unknown joint {jid}"
            seen[jid] = seen.get(jid, 0) + cnt
    for j in JOINTS:
        assert seen.get(j["id"], 0) == j["n"], (
            f"{j['id']}: the build steps complete {seen.get(j['id'], 0)} of "
            f"them, the bed has {j['n']}")
    total = {}
    for j in JOINTS:
        for name, per in j["fast"]:
            total[name] = total.get(name, 0) + per * j["n"]
    return total


# ---------------------------------------------------------------------------
# BUILD STEPS - defined ONCE, here
# ---------------------------------------------------------------------------
# `parts`     labels added to the assembly in this step ("*" = prefix match).
#             Every wooden part of the model must appear in exactly one step.
# `highlight` what the step image paints in the highlight colour; defaults to
#             `parts`. A step that only moves or fixes what is already there
#             (raising the frames, bolting to the wall) re-highlights instead.
# `camera`    (azimuth, elevation, distance) for tools/render_steps.py.
#             Azimuth 0 looks the ladder straight in the face; 270 is the
#             X = 1990 end; the back wall is at 180.
def build_steps(G):
    return [
        dict(
            n=0,
            title="Kapping, forboring og forsenking",
            image=False,
            parts=[],
            highlight=[],
            camera=None,
            intro="Gjør alt sagarbeid og all boring på bukk, før noe reises. "
                  "Etterpå kommer du ikke til med drillen på de flatene som "
                  "vender mot vegg.",
            do=[
                "Kapp alt etter kapplista. Alle kutt er 90°, ingen gjæring.",
                "Merk hver del med blyant på en flate som blir skjult.",
                "Bor alle gjennomgående hull i stolper, vanger, endebjelker "
                  "og benkevanger — diameter etter forboringskolonnen i "
                  "beslaglista. Bor gjennom begge deler samtidig, med delene "
                  "tvunget sammen.",
                "Forsenk hodene på alle festemidler som ender i en veggvendt "
                  "flate. Beslaglista sier hvilke ledd det gjelder.",
                "Forbor alle treskruer etter beslaglista. I bordene, i den "
                  "tynne bordbærelekta og i all endeved er forboring et krav, "
                  "ikke et råd.",
                "Slå filtknotter under alle fire hjørnestolper og alle fire "
                  "stubbeføtter.",
            ],
            check=[
                "Legg de to lengste delene — sidevangene — inn i rommet nå og "
                  "sjekk at de går fritt forbi begge vegger. De er kappet "
                  "kortere enn veggavstanden nettopp for dette.",
                "Legg delene i fire hauger på gulvet, én per steg. Du kommer "
                  "til å lete mindre.",
            ],
            joints={'J15': 8},
        ),
        dict(
            n=1,
            title="Bakrammen — bygg den flatt på gulvet",
            parts=["Corner Post Back *", "Upper Side Rail Back",
                   "Bench Rail Back (continuous)", "Table Ledger Back",
                   "Bench Rail Bearing Block Back *"],
            camera=(330, 24, 3.4),
            intro="Hele baksiden av sengen er ett eneste flatt lag: to korte "
                  "stolper og tre vannrette deler i samme plan. Det laget er "
                  "monteringsflaten mot veggen. Og det MÅ bygges som én "
                  "ramme: den bakre benkevangen og bordbærelekta er kappet "
                  "til å fylle nøyaktig mellom de to stolpene, så de lar seg "
                  "ikke tre inn etterpå.",
            do=[
                "Legg de to bakre stolpene ut i riktig avstand. De er de "
                  "korte — de stopper under sidevangen.",
                "Legg den bakre sidevangen oppå stolpetoppene. Den skal "
                  "hvile på endeveden, ikke henge på siden av stolpen. Fest "
                  "etter J2-B.",
                "Skru bæreklossene J9-B på innsiden av begge stolper. "
                  "Klossene er det den bakre benkevangen skal hvile på.",
                "Legg den bakre benkevangen ned mellom stolpene, på "
                  "klossene, og fest den etter J8-B. Vangen er kappet "
                  "nøyaktig så den fyller mellom de to stolpene — den kan "
                  "ikke tres inn senere.",
                "Sett vinkelbeslagene til bordbærelekta på stolpenes "
                  "innsider, legg lekta på høykant mellom stolpene og fest "
                  "etter J12.",
            ],
            check=[
                "Mål diagonalene i rammen — de skal være like.",
                "Kjenn etter med håndflaten over hele baksiden: ingen "
                  "skruehoder, ingenting som stikker ut. Denne flaten skal "
                  "ligge helt flatt mot veggen.",
                "Legg vinkelhaken på begge hjørner.",
            ],
            joints={'J2-B': 2, 'J8-B': 2, 'J9-B': 2, 'J12': 2},
        ),
        dict(
            n=2,
            title="Reis bakrammen og skru den fast i veggen",
            parts=[],
            highlight=["Upper Side Rail Back"],
            camera=(330, 24, 3.4),
            intro="Sengen festes til veggen gjennom den bakre sidevangen. "
                  "Vangen ligger flatt mot veggen i hele sin lengde, så "
                  "skruene går rett gjennom den og inn i stenderne. De "
                  "skruene holder ikke bare sengen på plass — de støtter også "
                  "vangen på midten.",
            do=[
                "Reis bakrammen og skyv den inntil bakveggen og inntil begge "
                  "sidevegger.",
                "Finn stenderne i veggen. Merk av senterlinjene på "
                  "sidevangen.",
                "Loddsjekk begge stolper, og vater langs sidevangen.",
                "Skru rammen fast i veggen gjennom sidevangen (J14). Ta et "
                  "feste i hver stender du treffer — minst i endene og på "
                  "midten.",
                "Skru en midlertidig skråstiver fra rammen ned til gulvet "
                  "hvis rammen står alene en stund. Den er flat og velter "
                  "lett framover.",
            ],
            check=[
                "Vater langs sidevangen, og lodd på begge stolper.",
                "Ta tak i vangen og dra. Rammen skal ikke bevege seg fra "
                  "veggen i det hele tatt.",
                "Er veggen mur eller betong, bruk plugg eller betongskrue. "
                  "Er den bindingsverk, må du treffe stender. En plateplugg i "
                  "gips er ikke et veggfeste.",
            ],
            joints={'J14': 1},
        ),
        dict(
            n=3,
            title="Endebjelkene og de fremre stolpene",
            parts=["Corner Post Front *", "End Beam Left", "End Beam Right",
                   "End Beam Bearing Block *",
                   "Bench Rail Bearing Block Front *"],
            camera=(325, 22, 3.4),
            intro="Nå bygges de to endene ut fra bakrammen. Endebjelken går "
                  "fra den bakre stolpen til den fremre og bærer begge "
                  "sidevanger.",
            do=[
                "Skru bæreklossene J1-B fast på innsiden av begge stolper — "
                  "også på den bakre, som allerede står. De skrus fra "
                  "klossens frie ende, inne fra sengen, så du kommer til når "
                  "som helst.",
                "Skru bæreklossen J9-F på baksiden av den fremre stolpen "
                  "mens den ennå ligger på gulvet. Merk deg at denne "
                  "klossen tar en kortere skrue enn de andre — det er bare "
                  "36 mm stolpe bak den.",
                "Reis den fremre stolpen på plass mot sideveggen.",
                "Legg endebjelken opp på de to bæreklossene J1-B og fest den "
                  "til begge stolper etter J1. Bjelken hviler på klossene — "
                  "den henger ikke i festemidlene.",
                "Gjenta i den andre enden.",
            ],
            check=[
                "Vater på begge endebjelker, og kontroller at de ligger i "
                  "nøyaktig samme høyde.",
                "Lodd på begge fremre stolper, i begge retninger.",
                "Endebjelkens overkant skal ligge i flukt med den bakre "
                  "sidevangens underkant. Gjør den ikke det, får ikke den "
                  "fremre vangen samme høyde som den bakre.",
                "Kjenn etter at ingenting stikker ut mot sideveggene.",
            ],
            joints={'J1': 4, 'J1-B': 4, 'J9-F': 2},
        ),
        dict(
            n=4,
            title="Fremre sidevange",
            parts=["Upper Side Rail Front"],
            camera=(330, 24, 3.4),
            intro="Den fremre vangen lukker rammen i overetasjen. Den hviler "
                  "på begge endebjelker og festes til de fremre stolpene.",
            do=[
                "Løft vangen opp på endebjelkene, på utsiden av dem.",
                "Fest den til begge fremre stolper etter J2.",
            ],
            check=[
                "Mål avstanden mellom de to sidevangene i begge ender og på "
                  "midten. Den skal være lik overalt — det er madrassbredden, "
                  "og madrassen er kappet nøyaktig etter den.",
                "Vater langs vangen, og kontroller at den ligger i samme "
                  "høyde som den bakre.",
                "Mål diagonalene i sengeflaten sett ovenfra.",
            ],
            joints={'J2': 2},
        ),
        dict(
            n=5,
            title="Fremre benkevanger og alle fire stubbeføtter",
            parts=["Bench Rail Front *", "Bench Stub Leg *"],
            camera=(330, 20, 3.4),
            intro="Den fremre benkevangen er delt i to. Midtpartiet er med "
                  "vilje åpent, slik at gulvet foran stigen er helt fritt.",
            do=[
                "Fest hver vangebit til sin fremre hjørnestolpe etter J8, på "
                  "bæreklossen J9-B.",
                "Sett en stubbefot under den innerste enden av hver "
                  "vangebit. Vangebiten skal slutte akkurat der foten står — "
                  "ingen utstikk forbi foten.",
                "Sett de to bakre stubbeføttene under den bakre benkevangen, "
                  "rett under de samme punktene.",
                "Fest alle fire føtter etter J10.",
            ],
            check=[
                "Ingenting skal krysse gulvet mellom de to benkene.",
                "Vater langs begge vangebiter, og samme høyde som den bakre "
                  "benkevangen.",
                "Alle fire føtter skal stå med hele endeflaten mot gulvet og "
                  "hele toppflaten mot vangen. Er det luft under en fot, kil "
                  "den ikke opp — juster den.",
            ],
            joints={'J8': 2, 'J10': 4},
        ),
        dict(
            n=6,
            title="Stigen",
            parts=["Ladder Upright *", "Rung Block *", "Ladder Rung_*"],
            camera=(0, 16, 3.6),
            intro="Bygg hele stigen ferdig liggende på gulvet, og skru den så "
                  "på den fremre sidevangen.",
            do=[
                "Skru stigeklossene på innsiden av hver stigevange (J5). "
                  "Klosshøyden er trinnhøyden — mål to ganger.",
                "Legg trinnene på klossene og fest dem (J4).",
                "Reis stigen mot den fremre sidevangen. Trinnenes forkant "
                  "skal ligge i flukt med stigevangenes forkant — trinnene "
                  "stikker BAKOVER, ikke framover. Det som stikker bakover er "
                  "hylla den løse platen skal hvile på.",
                "Skru stigen fast til vangen etter J3. Forbor tvers gjennom "
                  "stigevangen.",
            ],
            check=[
                "Mål lysåpningen mellom stigevangene øverst og nederst — den "
                  "skal være lik.",
                "Alle fire trinn i vater.",
                "Stå på nederste trinn og kjenn etter. Sitter noe løst nå, "
                  "sitter det løst for alltid.",
            ],
            joints={'J3': 2, 'J4': 8, 'J5': 8},
        ),
        dict(
            n=7,
            title="Benkespiler",
            parts=["Bench Slat *"],
            camera=(330, 30, 3.4),
            intro="Fem spiler per benk, lagt oppå benkevangene.",
            do=[
                "Legg ut alle fem spilene på én benk før du skrur, og sjekk "
                  "delingen mot kapplista.",
                "Skru hver spile ned i den bakre og den fremre benkevangen, "
                  "én skrue per ende (J11). Forsenk hodene — dette er en "
                  "sitteflate.",
                "Gjenta speilvendt på den andre benken.",
            ],
            check=[
                "Kjenn over hele benken med håndflaten: ingen skruehoder skal "
                  "stikke opp.",
                "Sett deg på begge benker.",
            ],
            joints={'J11': 20},
        ),
        dict(
            n=8,
            title="Køyespiler",
            parts=["Bed Slat_*"],
            camera=(330, 40, 3.4),
            intro="Spilene ligger OPPÅ begge sidevanger — ikke i et spor og "
                  "ikke på en lekt. Alle er like lange.",
            do=[
                "Legg ut alle spilene løst først og fordel dem etter "
                  "kapplista, før du skrur noe.",
                "Skyv hver spile helt inn til veggen. Bakkanten på spilene er "
                  "det madrassen støter mot.",
                "Skru hver spile ned i begge vanger, én skrue per ende (J6).",
            ],
            check=[
                "Alle spiler skal dekke hele bredden av begge vanger. Ligger "
                  "en spile bare halvveis på vangen, flytt den.",
                "Ingen skruehoder over flaten — de ligger under madrassen.",
                "Gå over hele bunnen med håndflaten før madrassen legges på.",
            ],
            joints={'J6': 28},
        ),
        dict(
            n=9,
            title="Rekkverk foran",
            parts=["Guard Rail Front *"],
            camera=(330, 22, 3.4),
            intro="To bånd, hvert delt i to bord, med klatreåpningen i "
                  "midten. Man klatrer GJENNOM rekkverket, ikke over. Det er "
                  "ikke rekkverk på baksiden — der er veggen sperren. Bordene "
                  "ligger på INNSIDEN av stolpene, mot sengen, ikke utenpå.",
            do=[
                "Legg det nederste båndet an mot innsiden av hjørnestolpen og "
                  "stigevangen, i flukt med stolpenes innerplan.",
                "Skru fra sengesiden inn i stolpen og i stigevangen (J7). "
                  "Forbor — bordet sprekker lett nær enden.",
                "Gjenta for det øverste båndet.",
            ],
            check=[
                "Mål åpningene over madrassoverflaten mot tallene i "
                  "nøkkelmålene. De er sikkerhetskravet i denne sengen.",
                "Ta tak i toppbordet og dra. Det skal ikke gi seg.",
            ],
            joints={'J7': 8},
        ),
        dict(
            n=10,
            title="Løs plate med avstivningslekter og beslag",
            parts=["Movable Panel (bed mode)", "Panel Stiffener Batten *"],
            camera=(325, 30, 3.6),
            intro="Platen er ikke et løst bord. Den er en liten enhet som "
                  "løftes ut i ett stykke, og beslagene på den er "
                  "konstruksjon — de holder platen nede OG avstiver stigen.",
            do=[
                "Skru de to avstivningslektene under platen, på høykant, fra "
                  "platens overside (J13a). Forsenk og propp hullene.",
                "Bøy eller kjøp de to U-brakettene og monter dem i platens "
                  "forkant slik at de omslutter trinnet (J13b).",
                "Monter de to krokplatene under platen, like innenfor "
                  "bakkanten (J13c). De skal henge ned foran den "
                  "bakre benkevangen og gripe inn under den.",
                "Legg platen i sengestilling: bakkanten på den bakre "
                  "benkevangen, forkanten på trinn 1. Krokplatene skal falle "
                  "ned foran vangen og hake seg inn under den.",
                "Prøv bordstilling: bakkanten på bordbærelekta, forkanten på "
                  "trinn 2. Samme plate, samme beslag. I denne stillingen "
                  "henger krokplatene fritt like foran bordbærelekta og "
                  "virker som stopp framover.",
            ],
            check=[
                "Løft i platens forkant. Den skal ikke kunne vippes opp — "
                  "U-brakettene låser den til trinnet.",
                "Platen skal ligge stødig på begge opplegg i begge "
                  "stillinger, uten å vippe.",
                "Rist i stigen sidelengs med platen i. Platen er stigens "
                  "avstivning nedad — sitter den løst, gynger stigen.",
            ],
            joints={'J13a': 2, 'J13b': 2, 'J13c': 2},
        ),
        dict(
            n=11,
            title="Madrass og sluttsjekk",
            parts=["Mattress *"],
            camera=(330, 26, 3.4),
            intro="Sengen er ferdig. Det som gjenstår er det som avgjør om "
                  "den er trygg.",
            do=[
                "Legg madrassen på plass. Den skal presses de siste "
                  "millimeterne inn mellom veggene, og den skal fylle hele "
                  "dybden fra veggen til de fremre stolpene.",
                "Legg de tre putene i underetasjen på plass.",
                "Skriv MINSTE tillatte madrasstykkelse med tusj på innsiden "
                  "av en fremre stolpe. Det er en nedre grense, ikke en øvre "
                  "— se sikkerhetsavsnittet i ASSEMBLY.md.",
            ],
            check=[
                "Ettertrekk alle festemidler som kan ettertrekkes.",
                "Madrassen skal ligge stramt mot veggen og mot de fremre "
                  "stolpene, uten spalte langs noen av de to lange kantene.",
                "Rist i sengen i begge retninger. Ingen bevegelse mot "
                  "bakveggen.",
                "Sett datoen for første ettertrekk i kalenderen: om fire "
                  "uker, og deretter en gang i året.",
            ],
            joints={},
        ),
    ]


# ---------------------------------------------------------------------------
# PART MATCHING
# ---------------------------------------------------------------------------
def _match(spec, label):
    if spec.endswith("*"):
        return label.startswith(spec[:-1])
    return label == spec


def resolve_steps(G, steps):
    """Attach the concrete part labels to every step and check the cover."""
    universe = (list(G.parts) + [G.panel_bed] + list(G.battens_bed)
                + [G.mattress])
    by_label = {p.label: p for p in universe}
    taken = {}
    for st in steps:
        labels = []
        for spec in st["parts"]:
            hit = [lbl for lbl in by_label if _match(spec, lbl)]
            assert hit, f"step {st['n']}: '{spec}' matches no part"
            for lbl in hit:
                assert lbl not in taken, \
                    f"'{lbl}' is claimed by step {taken[lbl]} and {st['n']}"
                taken[lbl] = st["n"]
            labels += hit
        st["labels"] = sorted(labels)
        hl = st.get("highlight", st["parts"])
        hlabels = []
        for spec in hl:
            hlabels += [lbl for lbl in by_label if _match(spec, lbl)]
        st["highlight_labels"] = sorted(set(hlabels))
    missing = sorted(set(by_label) - set(taken))
    assert not missing, f"no build step places: {missing}"
    return steps


def step_part_rows(G, st, cut_index):
    """[(antall, navn, dimensjon, lengde), ...] for the labels this step adds.

    `dimensjon` and `lengde` are empty strings for the reference mattress,
    which is bought rather than cut.
    """
    counts = {}
    for lbl in st["labels"]:
        key = cut_index.get(lbl)
        if key is None:                       # the reference mattress
            key = ("Madrass (se nøkkelmål)", "", "")
        counts[key] = counts.get(key, 0) + 1
    return [(qty, name, section, _fmt(length) if section else "")
            for (name, section, length), qty in sorted(counts.items())]


def step_part_summary(G, st, cut_index):
    """['2x Endebjelke 48x98 x 896', ...] for the labels this step adds."""
    out = []
    for qty, name, section, length in step_part_rows(G, st, cut_index):
        out.append(f"{qty}× {name} {section} × {length}" if section
                   else f"{qty}× {name}")
    return out


# ---------------------------------------------------------------------------
# CUT LIST
# ---------------------------------------------------------------------------
# The English cut-list names live in generate_loftbed.py (they are part of the
# model's own output). The documentation is Norwegian, so the names are mapped
# here - one place, and asserted complete.
NO_NAMES = {
    "Upper side rail": "Sidevange, øvre",
    "End beam": "Endebjelke",
    "Corner post, back (W2, wall side)": "Hjørnestolpe, bak (veggside)",
    "Corner post, front": "Hjørnestolpe, front",
    "Ladder upright (D13)": "Stigevange",
    "Ladder rung (tread)": "Rungetrinn",
    "Ladder rung block": "Stigekloss",
    "Bearing block, end beam (C2)": "Bærekloss, endebjelke (J1-B)",
    "Bearing block, bench rail (C2)": "Bærekloss, benkevange (J9-B)",
    "Bench rail, back (C5)": "Benkevange, bak (gjennomgående)",
    "Bench rail, front segment (D13)": "Benkevange, front (bit)",
    "Bench stub leg (W3)": "Stubbefot",
    "Bench slat (C3)": "Benkespile",
    "Upper bed slat, short (D5/W4)": "Køyespile, kort (mot bakre stolpe)",
    "Upper bed slat, to the wall (W4)": "Køyespile, lang (inn til veggen)",
    "Upper bed slat": "Køyespile",
    "Upper bed slat (D5)": "Køyespile",
    "Guard rail, front segment (D2/D7/D13)": "Rekkverksbord, front",
    "Table ledger, back": "Bordbærelekt, bak",
    "Movable panel": "Løs plate",
    "Panel stiffener batten (M4)": "Avstivningslekt under plate",
}


# The model gives every piece a cut-list line but does not record which part
# belongs to which line. This is that mapping, by label prefix, longest first.
# It is checked against CUT_LIST below: if the model ever grows, loses or
# renames a part, the assert in `part_cut_keys` fires.
LABEL_TO_CUT = [
    ("Upper Side Rail", "Upper side rail"),
    ("End Beam Bearing Block", "Bearing block, end beam (C2)"),
    ("End Beam", "End beam"),
    ("Corner Post Back", "Corner post, back (W2, wall side)"),
    ("Corner Post Front", "Corner post, front"),
    ("Ladder Upright", "Ladder upright (D13)"),
    ("Rung Block", "Ladder rung block"),
    ("Ladder Rung_", "Ladder rung (tread)"),
    ("Bench Rail Bearing Block", "Bearing block, bench rail (C2)"),
    ("Bench Rail Back", "Bench rail, back (C5)"),
    ("Bench Rail Front", "Bench rail, front segment (D13)"),
    ("Bench Stub Leg", "Bench stub leg (W3)"),
    ("Bench Slat", "Bench slat (C3)"),
    ("Guard Rail Front", "Guard rail, front segment (D2/D7/D13)"),
    ("Table Ledger Back", "Table ledger, back"),
    ("Movable Panel", "Movable panel"),
    ("Panel Stiffener Batten", "Panel stiffener batten (M4)"),
]


def part_cut_keys(G):
    """label -> the CUT_LIST key that part was counted into.

    The upper slats are the one family with two lines, and which line a slat
    gets is decided by its own length - the same rule the model uses.
    """
    by_name = {}
    for key in G.CUT_LIST:
        by_name.setdefault(key[0], []).append(key)
    for name, keys in by_name.items():
        assert len(keys) == 1, f"cut-list name '{name}' has {len(keys)} lines"

    out = {}
    for p in list(G.parts) + [G.panel_bed] + list(G.battens_bed):
        if p.label.startswith("Bed Slat_"):
            # The upper slats are the one family the model has sometimes split
            # into two cut-list lines (different lengths). Pick by length if
            # there are two, and just take the one line if there is only one.
            slat_lines = sorted(n for n in by_name if "bed slat" in n.lower())
            assert slat_lines, "no upper-slat line in the cut list"
            if len(slat_lines) == 1:
                name = slat_lines[0]
            else:
                (_, _), (y0, y1), _ = p.extents
                length = round(y1 - y0)
                cand = [n for n in slat_lines if by_name[n][0][2] == length]
                assert len(cand) == 1, \
                    f"'{p.label}' is {length} mm and matches {cand}"
                name = cand[0]
        else:
            name = next((cut for pre, cut in LABEL_TO_CUT
                         if p.label.startswith(pre)), None)
            assert name is not None, f"no cut-list line known for '{p.label}'"
        out[p.label] = by_name[name][0]

    counted = {}
    for key in out.values():
        counted[key] = counted.get(key, 0) + 1
    assert counted == dict(G.CUT_LIST), (
        "the label -> cut-list mapping disagrees with the model's own cut "
        "list; the model changed and LABEL_TO_CUT has not:\n"
        f"  mapping: {sorted(counted.items())}\n"
        f"  model:   {sorted(G.CUT_LIST.items())}")
    return out


def cut_table(G):
    """[(no_name, section, length, qty, (xr, yr, zr)), ...] sorted for humans."""
    keys = part_cut_keys(G)
    spans = {}
    for p in list(G.parts) + [G.panel_bed] + list(G.battens_bed):
        key = keys[p.label]
        (x0, x1), (y0, y1), (z0, z1) = p.extents
        cur = spans.setdefault(key, [[], [], []])
        cur[0].append((x0, x1))
        cur[1].append((y0, y1))
        cur[2].append((z0, z1))
    rows = []
    for (name, section, length), qty in G.CUT_LIST.items():
        assert name in NO_NAMES, f"cut-list name '{name}' has no Norwegian name"
        rows.append((NO_NAMES[name], _no_section(G, section), length, qty,
                     spans[(name, section, length)], name))
    rows.sort(key=lambda r: (r[1], -r[2], r[0]))
    return rows


def cut_index(G):
    """label -> (norwegian name, section, length)."""
    idx = {}
    for label, (name, section, length) in part_cut_keys(G).items():
        idx[label] = (NO_NAMES[name], _no_section(G, section), length)
    return idx


# ---------------------------------------------------------------------------
# BUYING LIST - first-fit-decreasing into sale lengths
# ---------------------------------------------------------------------------
def pack(pieces):
    """First-fit-decreasing bin packing into SALE_LENGTHS.

    Boards are opened at the longest sale length and shrunk afterwards to the
    shortest one that still holds what they were given, which is what you
    would do at the counter.
    """
    boards = []
    for name, length in sorted(pieces, key=lambda p: -p[1]):
        for b in boards:
            used = sum(x[1] for x in b) + KERF * len(b)
            if used + length <= max(SALE_LENGTHS):
                b.append((name, length))
                break
        else:
            assert length <= max(SALE_LENGTHS), \
                f"'{name}' is {length} mm - longer than any sale length"
            boards.append([(name, length)])
    out = []
    for b in boards:
        need = sum(x[1] for x in b) + KERF * (len(b) - 1)
        buy = min(s for s in SALE_LENGTHS if s >= need)
        out.append(dict(buy=buy, pieces=b, used=sum(x[1] for x in b),
                        rest=buy - need))
    out.sort(key=lambda b: (-b["buy"], -len(b["pieces"])))
    return out


def buy_table(G):
    rows = cut_table(G)
    by_section = {}
    for no_name, section, length, qty, _spans, _en in rows:
        by_section.setdefault(section, []).extend([(no_name, length)] * qty)
    out = []
    for section, pieces in sorted(by_section.items()):
        if "plate" in section or "panel" in section:   # sheet, not a stick
            out.append(dict(section=section, sheet=True, pieces=pieces))
            continue
        boards = pack(pieces)
        bought = sum(b["buy"] for b in boards)
        used = sum(b["used"] for b in boards)
        out.append(dict(section=section, sheet=False, boards=boards,
                        bought=bought, used=used,
                        waste=100.0 * (bought - used) / bought))
    return out


# ---------------------------------------------------------------------------
# WRITERS
# ---------------------------------------------------------------------------
HEAD = ("<!-- GENERERT AV generate_loftbed.py / tools/gen_doc_tables.py.\n"
        "     IKKE REDIGER FOR HÅND - kjør `mise run build`. -->\n\n")


def write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"  wrote {path}")


def emit_kappliste(G, out_dir):
    rows = cut_table(G)
    L = [HEAD, "# Kappliste\n\n",
         "Alle mål i mm. Alle kutt er 90°. Posisjonen er delens plass i "
         "modellen: X langs veggen (0 = venstre vegg, 1990 = høyre vegg), "
         "Y i dybden (−96 = bakveggen), Z opp fra gulvet.\n\n",
         "| Del | Dim. | Lengde | Ant. | X | Y | Z |\n",
         "|---|---|---:|---:|---|---|---|\n"]
    total = 0
    for no_name, section, length, qty, sp, _en in rows:
        total += qty
        L.append(f"| {no_name} | {section} | **{_fmt(length)}** | {qty} | "
                 f"{_axis(sp[0])} | {_axis(sp[1])} | {_axis(sp[2])} |\n")
    L.append(f"\n**{total} deler i alt.**\n\n")
    L.append("«(fordelt)» betyr at delene i den raden står på flere "
             "posisjoner langs den aksen; kolonnen viser da hele området de "
             "dekker. Nøyaktige posisjoner står i "
             "[nøkkelmål](nokkelmal.md).\n\n")

    by_section = {}
    for no_name, section, length, qty, _sp, _en in rows:
        by_section[section] = by_section.get(section, 0) + qty
    L.append("Fordelt på dimensjon: "
             + " · ".join(f"**{s}** {n} stk."
                          for s, n in sorted(by_section.items(),
                                             key=lambda kv: -kv[1]))
             + "\n\n")
    board = G.sec(G.BOARD36_T, G.BOARD36_W).replace("x", "×")
    lens = {}
    for no_name, section, length, qty, _sp, _en in rows:
        if section == board:
            lens[length] = lens.get(length, 0) + qty
    L.append("Sagstopp for hovedbordet " + board + ": "
             + " · ".join(f"**{qty} stk. à {_fmt(ln)}**"
                          for ln, qty in sorted(lens.items(), reverse=True))
             + f" — {len(lens)} innstilling"
             + ("er" if len(lens) != 1 else "")
             + " på sagen, ikke én per del.\n")
    write(os.path.join(out_dir, "kappliste.md"), "".join(L))


def emit_innkjopsliste(G, out_dir):
    tab = buy_table(G)
    L = [HEAD, "# Innkjøpsliste — trevirke\n\n",
         "Høvlet konstruksjonsvirke C24 der ikke annet er nevnt. "
         f"Kappingen under er regnet med {KERF} mm sagsnitt mellom hvert "
         "kutt, og hvert bord er valgt som den korteste salgslengden som "
         "rommer det som skal kappes av det.\n\n"]

    L.append("## Kort handleliste\n\n| Dimensjon | Kjøp | Svinn |\n")
    L.append("|---|---|---:|\n")
    for e in tab:
        if e["sheet"]:
            L.append(f"| **{e['section']}** | 1 plate 18 mm kryssfiner furu, "
                     f"minst {G.PANEL_W} × {G.PANEL_LEN} mm | — |\n")
            continue
        counts = {}
        for b in e["boards"]:
            counts[b["buy"]] = counts.get(b["buy"], 0) + 1
        buy = " + ".join(
            "**{} stk. {} m**".format(n, f"{ln / 1000:.1f}".replace(".", ","))
            for ln, n in sorted(counts.items(), reverse=True))
        L.append(f"| **{e['section']}** | {buy} | {e['waste']:.0f} % |\n")
    L.append("\n")

    L.append("## Kappeplan, bord for bord\n\n")
    for e in tab:
        if e["sheet"]:
            L.append(f"### {e['section']}\n\nÉn plate. "
                     f"{len(e['pieces'])} del(er) kappes av den.\n\n")
            continue
        L.append(f"### {e['section']}\n\n")
        L.append("Kjøpt {} m, brukt {} m, svinn {:.0f} %.\n\n".format(
            f"{e['bought'] / 1000:.2f}".replace(".", ","),
            f"{e['used'] / 1000:.2f}".replace(".", ","), e["waste"]))
        L.append("| Bord | Kjøpelengde | Kappes til | Rest |\n")
        L.append("|---:|---:|---|---:|\n")
        for i, b in enumerate(e["boards"], 1):
            per = {}
            for name, ln in b["pieces"]:
                per[(name, ln)] = per.get((name, ln), 0) + 1
            txt = " + ".join(f"{q} × {_fmt(ln)} ({name})"
                             for (name, ln), q in sorted(per.items()))
            L.append(f"| {i} | {_fmt(b['buy'])} | {txt} | "
                     f"{_fmt(b['rest'])} |\n")
        L.append("\n")

    L.append("## Merknader fra butikken\n\n")
    board = G.sec(G.BOARD36_T, G.BOARD36_W).replace("x", "×")
    L.append(f"* **{board}** er hovedbordet i denne sengen — det aller meste "
             f"av delelista er kappet av det. Ring og bestill før du drar; "
             f"butikken har sjelden nok av én dimensjon på lager. Får du ikke "
             f"akkurat {board}, kan modellen kjøres om på en nabodimensjon — "
             f"det er én konstant i `generate_loftbed.py` — men da må hele "
             f"kapplista og alle nøkkelmål regnes på nytt. Ikke improviser på "
             f"sagbenken.\n")
    L.append(f"* Platen er **{G.PANEL_W} mm bred**. Limtre furu i "
             f"butikkhylla stopper på 600 mm, så platen skal kappes av "
             f"**18 mm kryssfiner**.\n")
    L.append(f"* Vil du kunne bygge om til frittstående seng senere, trengs "
             f"to rekkverksbord til i samme dimensjon som de fremre, og to "
             f"bakre stolper i full høyde ({G.POST_HEIGHT} mm, som de "
             f"fremre). Kjøp dem gjerne nå, og forbor de bakre stolpene for "
             f"rekkverket mens de ligger på bukken.\n")
    write(os.path.join(out_dir, "innkjopsliste.md"), "".join(L))


def emit_nokkelmal(G, out_dir, rows):
    L = [HEAD, "# Nøkkelmål\n\n",
         "Alle mål i mm. X går langs rommet mellom de to veggene, Y i "
         "dybden med bakveggen på "
         f"{_fmt(G.WALL_Y)}, Z opp fra gulvet.\n\n"]

    L.append("## Ytre mål\n\n| | Mål |\n|---|---:|\n")
    L.append(f"| Bredde, vegg til vegg | {G.WALL_SPAN} |\n")
    L.append(f"| Dybde over alt | {G.OVERALL_DEPTH} |\n")
    L.append(f"| Høyde foran (stolpetopp) | {G.POST_HEIGHT} |\n")
    L.append(f"| Høyde ved veggen (bakre stolpe) | {G.BACK_POST_HEIGHT} |\n")
    L.append(f"| Gjennomgående deler kappes til | {G.THROUGH_LEN} "
             f"(X {G.THROUGH_X0}..{G.THROUGH_X1}) |\n")
    L.append(f"| Klaring til hver vegg for disse | {G.THROUGH_X0} |\n\n")
    L.append(f"En {G.WALL_SPAN} mm lang del lar seg ikke svinge inn i en "
             f"{G.WALL_SPAN} mm åpning. Derfor er hver gjennomgående del "
             f"{G.THROUGH_LEN} mm.\n\n")

    L.append("## Høyder (Z)\n\n| Z | Hva |\n|---:|---|\n")
    heights = [
        (0, "gulv"),
        (G.BENCH_RAIL_BOTTOM, "benkevangens underkant / stubbefotens topp"),
        (G.BENCH_RAIL_TOP, "benkevangens overkant = trinn 1 = platens "
                           "underside i sengestilling"),
        (G.PANEL_TOP_BED, "platens overside i sengestilling"),
        (G.BENCH_TOP, "benkeoverflate (sittehøyde)"),
        (G.LEDGER_BACK_Z0, "bordbærelektas underkant"),
        (G.RUNG_TOPS[1], "bordbærelektas overkant = trinn 2 = platens "
                         "underside i bordstilling"),
        (G.PANEL_TOP_TABLE, "bordplate"),
        (G.RUNG_TOPS[2], "trinn 3"),
        (G.RUNG_TOPS[3], "trinn 4"),
        (G.BEAM_BLOCK_Z0, "bæreklossen J1-B, underkant"),
        (G.END_BEAM_Z0, "endebjelkens underkant"),
        (G.RAIL_BOTTOM, "endebjelkens overkant = sidevangens underkant "
                        "(fri høyde under sengen)"),
        (G.RAIL_TOP, "sidevangens overkant"),
        (G.SLAT_Z1, "spilebunn / madrassens underside / bakre stolpetopp"),
        (G.MATTRESS_Z1, "madrassens overside (ved "
                        f"{G.MATTRESS_H} mm madrass)"),
        (G.GUARD_BAND_Z0[0], "rekkverk, nedre bånd underkant"),
        (G.GUARD_BAND_Z0[0] + G.GUARD_W, "rekkverk, nedre bånd overkant"),
        (G.GUARD_BAND_Z0[1], "rekkverk, øvre bånd underkant"),
        (G.GUARD_BAND_Z0[1] + G.GUARD_W, "rekkverk, øvre bånd overkant"),
        (G.POST_HEIGHT, "fremre stolpetopp"),
    ]
    for z, what in sorted(heights):
        L.append(f"| **{_fmt(z)}** | {what} |\n")

    climb = [0] + list(G.RUNG_TOPS) + [G.SLAT_Z1]
    steps = [b - a for a, b in zip(climb, climb[1:])]
    L.append(f"\nStigningen fra gulv til spilebunn: "
             + " + ".join(_fmt(s) for s in steps)
             + f" mm. Første stigning er benkevangens høyde — det er en "
               f"avsats du trår opp på, ikke et klatretrinn. De fire "
               f"klatretrinnene er {_fmt(min(steps[1:]))}–"
               f"{_fmt(max(steps[1:]))} mm.\n\n")

    L.append("## Dybdeplan (Y)\n\n| Y | Hva |\n|---:|---|\n")
    planes = [
        (G.WALL_Y, "BAKVEGGEN — monteringsflaten. Bakre stolper, "
                   "endebjelkeender og bakre bæreklosser ligger i dette "
                   "planet. Ingenting får stikke bak det."),
        (G.BACK_RAIL_Y0, "bakre sidevange, benkevange, bordbærelekt og "
                         "spilebunn — bakkant; bakre stolpes forside"),
        (G.LEDGER_BACK_Y0 + G.BOARD_T, "bordbærelektas forside"),
        (G.BACK_RAIL_Y1, "bakre sidevanges og benkevanges forside; "
                         "avstivningslektenes bakkant"),
        (G.RUNG_Y0, "trinnenes bakkant (hylla platen hviler på); "
                    "avstivningslektenes forkant"),
        (G.FRONT_RAIL_Y0, "fremre sidevange og benkevange — bakkant"),
        (G.FRONT_RAIL_Y1, "fremre sidevanges forside = fremre stolpers og "
                          "stigevangers bakside = spilebunnens og platens "
                          "forkant"),
        (G.FRONT_POST_Y1, "fremre stolpers og stigevangers forside = "
                          "trinnenes forkant"),
        (G.FRONT_GUARD_Y0, "rekkverksbordenes bakkant"),
        (G.FRONT_GUARD_Y1, "rekkverksbordenes forkant"),
        (G.DEPTH_Y1, "sengens forkant — det ytterste planet"),
    ]
    ext = getattr(G, "SLAT_Y0_EXT", None)
    if ext is not None and ext != G.SLAT_Y0:
        planes.append((ext, "de lange køyespilenes bakkant"))
    merged = {}
    for y, what in planes:
        merged.setdefault(y, [])
        if what not in merged[y]:
            merged[y].append(what)
    for y in sorted(merged):
        L.append(f"| **{_fmt(y)}** | " + "; ".join(merged[y]) + " |\n")
    L.append(f"\nFri bredde mellom de to sidevangene: "
             f"**{G.INNER_CLEAR_WIDTH}**. Spilebunnen fra vange til vange: "
             f"**{G.PLATFORM_DEPTH}** — nøyaktig madrassbredden.\n\n")

    L.append("## Stige, trinn og rekkverk (X)\n\n| | X |\n|---|---|\n")
    L.append(f"| Stigens senterlinje | {G.LADDER_CENTER_X} |\n")
    L.append(f"| Stigevanger | {_rng(G.LADDER_LEFT_X, G.LADDER_LEFT_X + G.UPRIGHT_W)}"
             f" og {_rng(G.LADDER_RIGHT_X, G.LADDER_RIGHT_X + G.UPRIGHT_W)} |\n")
    L.append(f"| Fri åpning mellom stigevangene | **{G.LADDER_CLEAR}** |\n")
    L.append(f"| Trinn (4 stk.) | {_rng(G.LADDER_INNER_L, G.LADDER_INNER_R)}"
             f", {G.RUNG_LEN} mm lange |\n")
    L.append(f"| Stigeklosser | {_rng(G.RUNG_BLOCK_X[0], G.RUNG_BLOCK_X[0] + G.RUNG_BLOCK_T)}"
             f" og {_rng(G.RUNG_BLOCK_X[1], G.RUNG_BLOCK_X[1] + G.RUNG_BLOCK_T)} |\n")
    L.append(f"| Rekkverksbord | {_rng(*G.FRONT_GUARD_SEGMENTS[0])} og "
             f"{_rng(*G.FRONT_GUARD_SEGMENTS[1])} |\n")
    L.append(f"| Klatreåpning i begge rekkverksbånd | **{G.LADDER_CLEAR}** |\n")
    L.append(f"| Benkene | {_rng(G.BENCH_X[0], G.BENCH_X[0] + G.BENCH_LEN)} og "
             f"{_rng(G.BENCH_X[1], G.BENCH_X[1] + G.BENCH_LEN)} |\n")
    L.append(f"| Åpent gulv mellom benkene | {_rng(*G.OPEN_FLOOR_X)} "
             f"({G.OPEN_FLOOR_X[1] - G.OPEN_FLOOR_X[0]} mm) |\n")
    L.append(f"| Gangpassasje ved siden av stigen | "
             f"{_fmt(G.LADDER_LEFT_X - G.OPEN_FLOOR_X[0])} mm på hver side |\n")
    L.append(f"| Stubbeføtter | {_rng(G.STUB_LEG_X[0], G.STUB_LEG_X[0] + G.LEG_W)}"
             f" og {_rng(G.STUB_LEG_X[1], G.STUB_LEG_X[1] + G.LEG_W)} |\n")
    L.append(f"| Løs plate | {_rng(G.PANEL_X0, G.PANEL_X1)} "
             f"({G.PANEL_W} mm bred) |\n")
    L.append(f"| Avstivningslekter | {_rng(G.BATTEN_X[0], G.BATTEN_X[0] + G.BATTEN_W)}"
             f" og {_rng(G.BATTEN_X[1], G.BATTEN_X[1] + G.BATTEN_W)} |\n\n")

    slat_pitch = (G.SLAT_X_END - G.SLAT_X_START - G.BED_SLAT_W) / (G.SLAT_COUNT - 1)
    L.append(f"**Køyespiler:** {G.SLAT_COUNT} stk., første spile starter på "
             f"X {G.SLAT_X_START}, deling {_fmt(slat_pitch)} mm, siste spile "
             f"slutter på X {G.SLAT_X_END}. Åpning mellom spilene "
             f"{_fmt(slat_pitch - G.BED_SLAT_W)} mm.\n\n")
    L.append(f"**Benkespiler:** {G.BENCH_SLAT_COUNT} per benk, deling "
             f"{_fmt(G.BENCH_SLAT_PITCH)} mm fra ytterveggen og innover.\n\n")

    L.append("## Skruerader i rammeleddene\n\n")
    L.append(f"Ingen bolt går inn i en stolpe. Stolpen er {G.POST_T} mm tykk, "
             f"og på den tykkelsen har en M8 ikke nok kantavstand; en {SCREW_D} "
             f"mm treskrue har akkurat nok. To skruer i et ledd står alltid "
             f"symmetrisk om delens midtlinje. Skruetyper og antall står i "
             f"[beslaglista](beslagliste.md).\n\n")
    L.append("| Ledd | Skruer | Z | Kantavstand | Avstand mellom | I planet |\n")
    L.append("|---|---:|---|---|---:|---|\n")
    where = {"J1": "Y " + " og ".join(_fmt(v) for v in rows["J1"]["y"])
                   + " (midt i stolpedybden)",
             "J2": f"X {_fmt(rows['J2']['x'])} fra hver vegg",
             "J8": f"X {_fmt(rows['J8']['x'])} fra hver vegg"}
    for j in ("J1", "J2", "J8"):
        r = rows[j]
        L.append(f"| {j} — {r['member']} | {r['count']} per ledd | "
                 + " og ".join(f"**{_fmt(z)}**" for z in r["z"]) + " | "
                 + " / ".join(_fmt(e) for e in r["edge"]) + " | "
                 + (_fmt(r["spacing"]) if r["spacing"] else "—") + " | "
                 + where[j] + " |\n")
    L.append(f"\nMinstekrav for en forboret {SCREW_D} mm treskrue: "
             f"kantavstand {MIN_EDGE} mm (3d), avstand mellom to skruer langs "
             f"fiberretningen {MIN_SPACING_GRAIN} mm (5d). Alle radene over "
             f"holder kravet.\n\n")
    end_d = rows["_rail_end_distance"]
    if end_d < rows["_rail_end_required"]:
        L.append(f"**Ett avvik:** endeavstanden fra vangens ende inn til "
                 f"J2- og J8-skruen blir {_fmt(end_d)} mm, mot minstekravet "
                 f"{rows['_rail_end_required']} mm. Se avviksnotatet i "
                 f"ASSEMBLY.md.\n\n")
    else:
        L.append(f"Endeavstanden fra vangens ende inn til J2- og J8-skruen "
                 f"er {_fmt(end_d)} mm, godt over minstekravet "
                 f"{rows['_rail_end_required']} mm — den brede stolpen ga "
                 f"denne avstanden gratis.\n\n")
    L.append("**Ingen forsenkte boltehoder.** Ingen del av rammen festes "
             "lenger fra en flate som ender mot vegg, så det finnes ikke et "
             "eneste hode som må senkes ned under en monteringsflate. "
             "Skruehoder forsenkes som vanlig der de er i veien for hånda.\n\n")

    L.append("## Madrass og puter\n\n| | Mål |\n|---|---|\n")
    L.append(f"| Madrass, overkøye | {G.WALL_SPAN} × {G.MATTRESS_W} mm "
             f"(en 200 × 80 presses de siste "
             f"{2000 - G.WALL_SPAN} mm inn mellom veggene) |\n")
    L.append(f"| Madrasstykkelse, minimum | {G.MATTRESS_H} mm — tynnere "
             f"madrass gjør åpningen opp til nedre rekkverksbånd større enn "
             f"{G.MAX_GUARD_OPENING} mm |\n")
    wander = getattr(G, "MATTRESS_WANDER", 0)
    if wander:
        L.append(f"| Madrassens sideveis vandring | {wander} mm mellom "
                 f"veggen og de fremre stolpene |\n")
    else:
        L.append("| Madrassens sideveis vandring | ingen — madrassen fyller "
                 "hele bredden mellom veggen og de fremre stolpene |\n")
    L.append(f"| Puter i underetasjen, dybde | {G.PANEL_LEN} mm |\n")
    L.append(f"| Pute over venstre benk | {G.BENCH_LEN} mm bred |\n")
    L.append(f"| Pute over platen (midten) | "
             f"{G.OPEN_FLOOR_X[1] - G.OPEN_FLOOR_X[0]} mm bred |\n")
    L.append(f"| Pute over høyre benk | {G.BENCH_LEN} mm bred |\n")
    L.append(f"| Midtputen er tykkere enn benkeputene med | "
             f"{G.PANEL_BENCH_DIP} mm — platen ligger så mye lavere enn "
             f"benkeflaten, og det er nettopp plassen putene skal folde seg "
             f"ned i |\n\n")

    L.append("## Sikkerhetsmål (EN 747)\n\n| | Mål | Krav |\n|---|---:|---:|\n")
    L.append(f"| Madrassoverside → nedre rekkverksbånd | "
             f"{G.GUARD_BAND_Z0[0] - G.MATTRESS_Z1} | ≤ "
             f"{G.MAX_GUARD_OPENING} |\n")
    L.append(f"| Mellom de to rekkverksbåndene | "
             f"{G.GUARD_BAND_Z0[1] - (G.GUARD_BAND_Z0[0] + G.GUARD_W)} | ≤ "
             f"{G.MAX_GUARD_OPENING} |\n")
    L.append(f"| Øvre bånd → stolpetopp | "
             f"{G.POST_HEIGHT - (G.GUARD_BAND_Z0[1] + G.GUARD_W)} | ≤ "
             f"{G.MAX_GUARD_OPENING} |\n")
    L.append(f"| Rekkverkets høyde over madrassen | "
             f"{G.GUARD_BAND_Z0[1] + G.GUARD_W - G.MATTRESS_Z1} | ≥ "
             f"{G.MIN_GUARD_OVER_MATTRESS} |\n")
    gap = getattr(G, "MAX_MATTRESS_GAP", None)
    if gap is not None:
        L.append(f"| Åpning mellom madrass og vegg (verste stilling) | "
                 f"{gap} | ≤ {G.MAX_GUARD_OPENING} |\n")
    L.append(f"| Fri klatreåpning i stigen | {G.LADDER_CLEAR} | ≥ "
             f"{G.MIN_LADDER_CLEAR} |\n")
    L.append(f"| Største klatretrinn | {_fmt(max(steps[1:]))} | ≤ "
             f"{G.MAX_CLIMB_STEP} |\n")
    write(os.path.join(out_dir, "nokkelmal.md"), "".join(L))


def emit_byggesteg(G, out_dir, steps, idx):
    L = [HEAD, "# Steg for steg\n\n",
         "Rekkefølgen er ikke fri. Sengen står inntil bakveggen og inntil "
         "begge sidevegger, og den bygges på plass. Alt som skal skrus eller "
         "boltes fra en flate som ender mot vegg, må gjøres før den flaten "
         "kommer inntil veggen. Derfor bygges den bakfra og utover.\n\n",
         "Bildeversjonen av de samme stegene, med samme nummer, ligger i "
         "[MONTERING.md](../MONTERING.md). Mål slår du opp i "
         "[nøkkelmål](nokkelmal.md) og [kappliste](kappliste.md); "
         "leddene står i J-oversikten i "
         "[ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene), med antall og forboring "
         "i [beslaglista](beslagliste.md).\n\n"]
    for st in steps:
        L.append(f"## Steg {st['n']} — {st['title']}\n\n")
        L.append(st["intro"] + "\n\n")
        parts = step_part_summary(G, st, idx)
        if parts:
            L.append("**Deler:** " + " · ".join(parts) + "\n\n")
        fast = step_fastener_summary(st)
        if fast:
            L.append("**Festemidler:** " + " · ".join(fast) + "\n\n")
        if st["joints"]:
            order = [j["id"] for j in JOINTS]
            L.append("**Ledd:** " + ", ".join(
                sorted(st["joints"], key=order.index))
                     + " — se J-oversikten i "
                       "[ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og "
                       "[beslagliste](beslagliste.md)\n\n")
        L.append("**Slik gjør du:**\n\n")
        for d in st["do"]:
            L.append(f"1. {d}\n")
        L.append("\n**Sjekk før du går videre:**\n\n")
        for c in st["check"]:
            L.append(f"* {c}\n")
        L.append("\n")
    write(os.path.join(out_dir, "byggesteg.md"), "".join(L))


MONTERING_HEAD = (
    "<!-- GENERERT AV tools/gen_doc_tables.py under `mise run build`.\n"
    "     IKKE REDIGER FOR HÅND. Strektegningene lages av\n"
    "     `mise run montering` (tools/render_lineart.py). -->\n\n")

# The pictogram page. (do-key, dont-key or None, the one line beside them).
# The drawings themselves come out of tools/gen_glyphs.py; the pairs use the
# manual convention of showing the wrong way beside the right one.
PREP = [
    ("to-personer", "en-person-nei",
     "**To personer.** Bakrammen veier mye og skal reises loddrett."),
    ("underlag", "dra-nei",
     "**Mykt underlag.** Bygg rammene flatt på papp eller teppe. Ikke dra "
     "delene over gulvet."),
    ("sorter", None,
     "**Sorter delene** etter kapplista, og merk hver del på en flate som "
     "blir skjult."),
    ("les", None,
     "**Les steg 0 først.** All saging og all boring skjer før noe reises."),
    ("verktoy", None,
     "**Verktøy:** drill med bor, torxbits, fastnøkkel 10 mm, tommestokk, "
     "vater og vinkelhake."),
    ("forbor", None,
     "**Forbor.** I bord, i den tynne bordbærelekta og i all endeved er "
     "forboring et krav."),
    ("veggfeste-ja", "fritt-staaende-nei",
     "**Sengen skal skrus fast i veggen.** Den er ikke beregnet på å stå "
     "fritt — veggen er sperren på baksiden."),
]


# On a step page the size is what you need; the full trade name is on the
# hardware page. Nothing is dropped that you cannot look up two pages back.
def _fast_short(name):
    for tail in (" forsenket Torx", " varmforsinket"):
        name = name.replace(tail, "")
    name = name.replace(", bøyd av flattstål 30×4", "")
    if name.startswith("Veggfeste"):
        return "Veggfeste"
    if name.startswith("Senkhodeskrue"):
        return "Senkhodeskrue M6×30 + skive + mutter"
    if name.startswith("Filtknott"):
        return "Filtknott ⌀40"
    return name


def _img(src, height, alt=""):
    return f'<img src="{src}" alt="{alt}" height="{height}">'


# The glyphs are all drawn to ONE scale, and each carries that scale in the
# height of its viewBox - a wood screw is 120 units tall, the big angle
# bracket 386. Rendering every glyph to the same pixel height would throw
# that away and make a 90 mm bracket look like a 5 mm screw, so the height in
# the page is taken from the drawing instead. SCREW_UNITS is the reference.
SCREW_UNITS = 120.0


def _glyph_height(path, screw_px, cap=None):
    with open(path, encoding="utf-8") as fh:
        head = fh.read(4000)
    m = re.search(r'viewBox="[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+([\d.]+)"', head)
    units = float(m.group(1)) if m else SCREW_UNITS
    h = round(screw_px * units / SCREW_UNITS)
    return min(h, cap) if cap else max(h, 12)


def emit_montering(G, root, steps, idx):
    """docs/MONTERING.md - the pictorial manual. Same steps, same numbers.

    Page 1 is the cover, page 2 the preparation pictograms, page 3 the
    hardware inventory, page 4 the part inventory, then one page per step.
    Everything on those pages is derived: the drawings from the model, the
    counts from JOINTS and the cut list, the step order from build_steps().
    """
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import gen_glyphs

    img_dir = os.path.join(root, "docs", "img")
    total_fast = hardware_total(steps)          # also asserts the step counts
    glyph = gen_glyphs.emit_fastener_glyphs(sorted(total_fast),
                                            os.path.join(img_dir, "beslag"))
    legend = gen_glyphs.emit_notation_legend(os.path.join(img_dir, "beslag"))
    pikto = gen_glyphs.emit_pictograms(os.path.join(img_dir, "ikon"))
    # As many letters as the busiest step needs, and no more.
    widest = max((len(step_badges(st)) for st in steps), default=0)
    merke = gen_glyphs.emit_badges(os.path.join(img_dir, "ikon"), widest)

    def gimg(name, screw_px, cap=None):
        f = glyph[name]
        h = _glyph_height(os.path.join(img_dir, "beslag", f), screw_px, cap)
        return _img("img/beslag/" + f, h, name)

    # ----- page 1: cover ---------------------------------------------------
    parts_rows = cut_table(G)
    n_parts = sum(r[3] for r in parts_rows)
    n_steps = sum(1 for st in steps if st["n"] > 0)
    L = [MONTERING_HEAD,
         "# HANNA\n\n",
         "## Loftseng med sofa, bord og ekstraseng under\n\n",
         "![HANNA](img/hanna-hero.png)\n\n",
         "| Bredde | Dybde | Høyde |\n|---:|---:|---:|\n",
         f"| **{G.WALL_SPAN} mm** | **{G.OVERALL_DEPTH} mm** | "
         f"**{G.POST_HEIGHT} mm** |\n\n",
         f"{n_parts} deler · {n_steps} steg · 2 personer · "
         f"madrass {G.WALL_SPAN} × {G.MATTRESS_W} mm\n\n",
         "Sengen står inntil bakveggen og inntil begge sidevegger, og skrus "
         "fast i bakveggen. **Bygg bakfra og utover.**\n\n",
         "Ord og begrunnelser: [ASSEMBLY.md](ASSEMBLY.md). "
         "Full steg-for-steg-tekst: [byggesteg](generated/byggesteg.md).\n\n"]

    # ----- page 2: before you start ---------------------------------------
    L.append("---\n\n# Før du begynner\n\n")
    L.append("**Svart strek** er delen du setter opp nå. "
             "**Grå strek** er det som allerede står.\n\n")
    L.append("| Slik | Ikke slik | |\n|:---:|:---:|---|\n")
    for do, dont, line in PREP:
        yes = (_img("img/ikon/" + pikto[do], 72, do) + " "
               + _img("img/ikon/" + pikto["hake"], 26, "ja"))
        no = ("" if dont is None else
              _img("img/ikon/" + pikto[dont], 72, dont) + " "
              + _img("img/ikon/" + pikto["kryss"], 26, "nei"))
        L.append(f"| {yes} | {no} | {line} |\n")
    L.append("\n")

    # ----- page 3: hardware -----------------------------------------------
    # The legend first: nothing on this page says what the two numbers in
    # "5×60" are, or what the "100x" counts. One measured exemplar does.
    L.append("---\n\n# Beslag\n\n")
    L.append(_img("img/beslag/" + legend, 104,
                  "5 = tykkelse i mm, 60 = lengde i mm, 100x = antall")
             + "\n\n")
    L.append("| | |\n|:---:|---|\n")
    for name, qty in sorted(total_fast.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {gimg(name, 44)} **{qty}x** | {name} |\n")
    L.append("\nHvor hver enkelt går, og hva som forbores: "
             "[beslagliste](generated/beslagliste.md).\n\n")

    # ----- page 4: parts ---------------------------------------------------
    L.append("---\n\n# Delene\n\n")
    L.append("| Del | Dim. | Lengde | Ant. |\n|---|---|---:|---:|\n")
    for no_name, section, length, qty, _sp, _en in parts_rows:
        L.append(f"| {no_name} | {section} | {_fmt(length)} | **{qty}** |\n")
    L.append(f"\n**{n_parts} deler.** **Ant.** er antallet — det samme tallet "
             "som står som `4×` på stegsidene. **Dim.** og **Lengde** er i "
             "millimeter.\n\n")
    L.append("Posisjoner: [kappliste](generated/kappliste.md). Hva du skal "
             "kjøpe: [innkjøpsliste](generated/innkjopsliste.md).\n\n")

    # ----- the step pages --------------------------------------------------
    order = [j["id"] for j in JOINTS]
    for st in steps:
        L.append("---\n\n")
        L.append(f"# {st['n']}\n\n")
        L.append(f"## {st['title']}\n\n")
        if st.get("image", True) and st["camera"]:
            L.append(f"![Steg {st['n']}](img/steg-{st['n']:02d}.png)\n\n")

        rows = step_part_rows(G, st, idx)
        if rows:
            L.append("| Ant. | Del | Dim. | Lengde |\n|---:|---|---|---:|\n")
            for qty, name, section, length in rows:
                L.append(f"| **{qty}×** | {name} | {section} | {length} |\n")
            L.append("\n")

        fast = step_fastener_rows(st)
        badges = step_badges(st)
        if fast and badges:
            # More than one kind in this step: the letter column is the key to
            # the same letters on the drawing's fastening arrows. Listed in
            # letter order, which is the order the drawing's inset lists them
            # in too - commonest first.
            L.append("| | | |\n|:---:|:---:|---|\n")
            for name, qty in sorted(fast, key=lambda r: badges[r[0]]):
                L.append(f"| {_img('img/ikon/' + merke[badges[name]], 20, badges[name])}"
                         f" | {gimg(name, 30, cap=72)} **{qty}x** | "
                         f"{_fast_short(name)} |\n")
            L.append("\nBokstavene viser hvor på tegningen hver type går.\n\n")
        elif fast:
            L.append("| | |\n|:---:|---|\n")
            for name, qty in fast:
                L.append(f"| {gimg(name, 30, cap=72)} **{qty}x** | "
                         f"{_fast_short(name)} |\n")
            L.append("\n")

        if st["joints"]:
            L.append("Ledd " + ", ".join(
                f"**{j}**" for j in sorted(st["joints"], key=order.index))
                + " → [beslagliste](generated/beslagliste.md)\n\n")
        for c in st["check"][:1]:
            L.append(f"⚠️ {c}\n\n")
        L.append(f"[Steg {st['n']} i ord]"
                 f"(generated/byggesteg.md#steg-{st['n']}"
                 f"--{_anchor(st['title'])})\n\n")

    L.append("---\n\n")
    L.append("Tegningene i `docs/img/` er projisert ut av modellen og sjekket "
             "inn i git. De lages på nytt med `mise run montering`.\n")
    path = os.path.join(root, "docs", "MONTERING.md")
    write(path, "".join(L))


def _anchor(title):
    out = []
    for ch in title.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -":
            out.append("-")
    return "".join(out)


def emit_beslagliste(out_dir, steps):
    total = hardware_total(steps)
    L = [HEAD, "# Beslag og festemidler\n\n",
         "Alt er elforsinket eller varmforsinket. Handelsnavn som i norsk "
         "byggevarehandel.\n\n",
         "## Handleliste\n\n",
         "| Post | Behov | Kjøp |\n|---|---:|---|\n"]
    for name, qty in sorted(total.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {name} | {qty} | {_buy_hint(name, qty)} |\n")
    L.append("\n## Hvor det går — ledd for ledd\n\n")
    L.append("| Ledd | Hva | Antall ledd | Per ledd | Forboring | "
             "Drives fra |\n|---|---|---:|---|---|---|\n")
    for j in JOINTS:
        per = " + ".join(f"{q}× {n}" for n, q in j["fast"])
        L.append(f"| **{j['id']}** | {j['title']} | {j['n']} | {per} | "
                 f"{j['drill']} | {j['side']} |\n")
    L.append("\nForklaringen til hvert ledd står i "
             "[ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene).\n")
    write(os.path.join(out_dir, "beslagliste.md"), "".join(L))


def _buy_hint(name, qty):
    if "Låseskrue M8" in name:
        return f"{qty + 5} stk. (bolt, mutter og skive hver for seg)"
    if name.startswith("Treskrue"):
        return "1 eske 200" if qty > 40 else f"1 pk. ({qty + 10} stk.)"
    if "M6×30" in name:
        return f"{qty + 2} sett"
    if "Vinkelbeslag" in name:
        return f"{qty + 2} stk."
    if "flattstål" in name:
        return "kappes av flattstål 30×4 — én meter dekker alle stålbeslagene"
    if "Filtknott" in name:
        return "1 pk."
    return f"{qty} stk."


def emit_json(G, out_dir, steps, idx, rows):
    data = dict(
        steps=[dict(n=st["n"], title=st["title"], image=st.get("image", True),
                    labels=st["labels"], highlight=st["highlight_labels"],
                    camera=st["camera"], intro=st["intro"], do=st["do"],
                    check=st["check"],
                    fasteners=step_fastener_summary(st),
                    joints=st["joints"],
                    parts=step_part_summary(G, st, idx))
               for st in steps],
        bolt_rows={k: v for k, v in rows.items() if not k.startswith("_")},
    )
    path = os.path.join(out_dir, "byggesteg.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# STEP MESHES  (per-step .stl groups for tools/render_steps.py)
# ---------------------------------------------------------------------------
def emit_step_meshes(G, steps, group_dir):
    """Two Y-up STLs per step - everything placed before it, and this step's
    highlight - plus the `.groups` manifest tools/mesh_to_usda.swift eats."""
    from build123d import Compound, export_stl

    step_dir = os.path.join(group_dir, "steps")
    os.makedirs(step_dir, exist_ok=True)
    universe = {p.label: p for p in
                list(G.parts) + [G.panel_bed] + list(G.battens_bed)
                + [G.mattress]}
    PRIOR = (0.82, 0.82, 0.80, 1.0)
    NEW = (0.94, 0.42, 0.10, 1.0)

    placed = []
    manifests = []
    for st in steps:
        if st.get("image", True) and st["camera"]:
            groups = []
            # Everything already standing, minus whatever this step paints,
            # goes in the pale group; the highlight group is exactly what the
            # step is about (new parts, or - for a step that only moves or
            # fixes what is already there - the parts it acts on).
            prior = [universe[l] for l in placed
                     if l not in st["highlight_labels"]]
            new = [universe[l] for l in st["highlight_labels"]]
            for name, members, rgba in (("prior", prior, PRIOR),
                                        ("new", new, NEW)):
                if not members:
                    continue
                path = os.path.join(step_dir, f"steg_{st['n']:02d}_{name}.stl")
                export_stl(Compound(children=[p.moved(G.Y_UP)
                                              for p in members]), path)
                groups.append(f"{name}={','.join(f'{c:.4g}' for c in rgba)}"
                              f"={path}")
            mpath = os.path.join(step_dir, f"steg_{st['n']:02d}.groups")
            with open(mpath, "w", encoding="utf-8") as fh:
                fh.write("\n".join(groups) + "\n")
            manifests.append(mpath)
        placed += st["labels"]
    print(f"  wrote {len(manifests)} per-step mesh manifests in {step_dir}")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
def emit(ns):
    import types
    G = types.SimpleNamespace(**ns)
    out_dir = os.path.join(G.OUT_DIR, "docs", "generated")
    os.makedirs(out_dir, exist_ok=True)

    print("\n=== DOC FRAGMENTS ===")
    rows = screw_rows(G)
    steps = resolve_steps(G, build_steps(G))
    idx = cut_index(G)

    emit_kappliste(G, out_dir)
    emit_innkjopsliste(G, out_dir)
    emit_nokkelmal(G, out_dir, rows)
    emit_byggesteg(G, out_dir, steps, idx)
    emit_beslagliste(out_dir, steps)
    emit_montering(G, G.OUT_DIR, steps, idx)
    emit_json(G, out_dir, steps, idx, rows)
    emit_step_meshes(G, steps, G.GROUP_DIR)


def main():
    """`mise run build` runs this; importing the generator builds the model."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    import generate_loftbed
    emit(vars(generate_loftbed))


if __name__ == "__main__":
    main()
