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
                                   by tools/render_lineart.py and
                                   tools/render_steps.py

Nothing here is hand-maintained: rerun `mise run build` and it is all rebuilt.
"""

import json
import math
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
# ...except where the trade does not actually stock the whole ladder. Butikk-
# runden: 36x98 C24 is sold as a fixed length ONLY at 4800 mm (Montér). 4200 is
# not listed by any retailer and 3600 does not exist in 36 mm C24 at all -
# Moelven mills 4200/4800/5100/5400 and the counter carries 4800. Planning on
# 4200/3600 boards would send the reader home with lengths he cannot buy, so
# the main board is packed into 4800s only. Costs a little more offcut; the cut
# list itself is untouched, this is purchasing.
# V6 butikkrunde: dette er lengdene virket FAKTISK ble kjøpt i. 36x98 finnes
# bare i 4,8 m (se over), og de tre andre lektedimensjonene ble tatt i 4,8 m
# fordi det er den lengden butikken hadde dem i. Kappeplanen skal beskrive det
# virket som ligger på planet, ikke en optimal pakking av en annen lengdeliste.
SALE_LENGTHS_BY_SECTION = {
    "23×98": [4800],
    "36×48": [4800],
    "36×98": [4800],
    "48×68": [4800],
}
KERF = 4                 # saw kerf allowance between two cuts, mm

# Butikkrunden: treskruer selges i faste pakkestørrelser. «1 pk. (24 stk.)» er
# ikke en vare - kolonnen «Kjøp» skal navngi en pakke som finnes, og «Behov»
# blir stående som det tallet sengen faktisk trenger.
SCREW_PACK_SIZES = [8, 20, 25, 50, 100, 200]

# The joint table, the trade names, the counts and the EC5 row geometry all
# live in generate_loftbed.py now - the model places the fasteners, so the
# model is where they are defined. This file only prints them.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import generate_loftbed as _MODEL          # noqa: E402

JOINTS = _MODEL.JOINTS
JOINT = _MODEL.JOINT
PART_NO = _MODEL.PART_NO
SCREW_D = _MODEL.SCREW_D
MIN_EDGE = _MODEL.MIN_EDGE
MIN_SPACING_GRAIN = _MODEL.MIN_SPACING_GRAIN
MIN_SPACING_CROSS = _MODEL.MIN_SPACING_CROSS


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


def step_fastener_rows(st):
    """[(handelsnavn, antall), ...] for one step, summed from its joints."""
    total = {}
    for jid, cnt in st["joints"].items():
        for name, per in JOINT[jid]["fast"]:
            total[name] = total.get(name, 0) + per * cnt
    return sorted(total.items())


def _badge_alphabet():
    """The letters a step's fastener kinds are badged with.

    Defined once, in tools/gen_glyphs.py - the file that DRAWS them. Imported
    late because gen_glyphs pulls in the SVG machinery this module does not
    otherwise need.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_glyphs
    return gen_glyphs.BADGE_ALPHABET


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
    alphabet = _badge_alphabet()
    return {name: alphabet[i] for i, (name, _q) in enumerate(order)}


def step_fill_code(st):
    """Does this step's page code its fasteners with a fill pattern?

    A DERIVED PROPERTY OF THE STEP, exactly like `half_view` or `info_panel`,
    and it travels with the step into byggesteg.json so that the drawing looks
    it up instead of deciding it. What it is derived FROM is the step's own
    fastener set: the code is bought to separate two screws the SILHOUETTE
    cannot separate, so it is switched on where such a pair exists on the page
    and nowhere else. The threshold is one definition, in tools/gen_glyphs.py
    beside the codes themselves - see `ambiguous_pairs()` there.

    Two consequences worth saying out loud. It is the PAGE that is coded, not
    the pair: fire the rule and every fastener on the page carries its own
    fill, because a page with coded and uncoded screws on it would be telling
    the reader something a third time in a language nobody taught them. And a
    step with a single kind of fastener can never fire it - it has no letters
    either, and a code with one value codes nothing.
    """
    rows = step_fastener_rows(st)
    if len(rows) < 2:
        return False
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_glyphs
    return gen_glyphs.shape_ambiguous([name for name, _q in rows])


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
#
# WHAT KIND OF PAGE A STEP GETS is declared here too, because it is a property
# of the STEP and not of its number. tools/render_lineart.py used to carry it
# as a handful of `if n == 0`, `if n == 2`, `if n == 10`, a HALF_VIEW_STEPS
# set and one label prefix match, which meant the answer to "why is this page
# different" lived in a file that is not allowed to know anything the model
# does not. All of these default to false/absent, so an ordinary step says
# nothing at all:
#
# `page`             "cutpage" or "panel": a page that is not a projection of
#                    the bed and has a module of its own.
# `half_view`        the step builds the SAME CORNER TWICE, once at each end,
#                    and nothing in between - so the drawing is cropped to one
#                    end and a mirror pictogram carries the other. The counts
#                    stay whole-step counts.
# `thumbnails`       before/after pair: the one step that changes the
#                    workpiece's orientation.
# `crop_to_subject`  the step's parts are a narrow thing in a wide bed and get
#                    a page cut round them instead of the shared bed page.
# `no_fasteners`     nothing is fastened: no marks, no inset, no coverage
#                    check.
# `info_panel`       the corner panel is an information panel rather than a
#                    fastener list.
# `avoid_top_left`   the top left corner is what the drawing is ABOUT, so no
#                    panel may be parked there.
def build_steps(G):
    # The batten profile and a Norwegian decimal, both wanted in several of
    # the strings below and neither worth repeating.
    _SEC = G.sec(G.BATTEN_W, G.BATTEN_H).replace("x", "×")

    def _mm(x):
        return f"{x:.1f}".rstrip("0").rstrip(".").replace(".", ",")

    return [
        dict(
            n=0,
            title="Kapping, forboring og forsenking",
            # There IS a drawing for step 0, it is just not a view of the bed:
            # tools/render_cutpage.py lays every purchase length out as a bar
            # with its cuts marked. So `image` is true and `camera` is None.
            image=True,
            page="cutpage",
            parts=[],
            highlight=[],
            camera=None,
            intro="Gjør alt sagarbeid og all boring på bukk, før noe reises. "
                  "Etterpå kommer du ikke til med drillen på de flatene som "
                  "vender mot vegg.",
            do=[
                "Kapp etter kapplista. **Verksteddelene kappes ferdig; "
                  "romdelene kappes med overmål** — kapplista sier hvilke og "
                  "hvor mye, og de finkappes i rommet. Alle kutt er 90°, "
                  "ingen gjæring — med to navngitte unntak, og begge står i "
                  "kapplista: de to kilelektene under platens forkant, og de "
                  "to vinkelklossene.",
                f"Skråkapp de to kilelektene. De er {_SEC} × {G.NOSE_LEN} mm "
                  "og skal "
                  "sages ned i ett rett snitt fra full høyde i den ene enden "
                  f"til {G.NOSE_TIP_H} mm i den andre ("
                  + f"{G.NOSE_TAPER_DEG:.1f}".replace(".", ",")
                  + "°). Håndsag eller båndsag; "
                  "overkanten — den som skal limes mot plata — skal stå "
                  "urørt og plan.",
                "Lag de to vinkelklossene, borjiggene til skråskruene — én "
                  "til J8-B og én til J10. Hver kloss er "
                  f"{G.TOE_JIG_PLIES} biter {_SEC} × {G.TOE_JIG_LEN} mm av "
                  "restene, skrudd FLATE MOT FLATE. Bor "
                  f"⌀{G.TOE_SEAT_D:g} VINKELRETT gjennom begge mens klossen "
                  "ennå er firkantet — det er hullet som styrer boret siden, "
                  "ikke en rampe. Kapp så sålen av under hullet på kappsag "
                  f"med bladet vippet {G.TOE_JIG_ANGLES['J8-B']:g}° (J8-B) "
                  f"hhv. {G.TOE_JIG_ANGLES['J10']:g}° (J10).",
                "**Vippen og flaten er komplementvinkler.** "
                  f"{G.TOE_JIG_ANGLES['J8-B']:g}° vipp gir en såle som står "
                  f"{90 - G.TOE_JIG_ANGLES['J8-B']:g}° på den borede flaten "
                  f"— og dermed {G.TOE_JIG_ANGLES['J8-B']:g}° på hullaksen, "
                  "som er det leddet er regnet på. Kontroller med "
                  "tommestokken før klossen får røre sengen: hullets munning "
                  "i sålen skal måle "
                  + _mm(G.TOE_JIG_ELLIPSE['J8-B'][0]) + " × "
                  + _mm(G.TOE_JIG_ELLIPSE['J8-B'][1])
                  + f" mm på {G.TOE_JIG_ANGLES['J8-B']:g}°-klossen og "
                  + _mm(G.TOE_JIG_ELLIPSE['J10'][0]) + " × "
                  + _mm(G.TOE_JIG_ELLIPSE['J10'][1])
                  + f" mm på {G.TOE_JIG_ANGLES['J10']:g}°-klossen. Er "
                  "ellipsen for kort, ble vippen satt på feil vinkel. "
                  "Klossene bygges ikke inn i sengen — de er verktøy.",
                "Merk hver del med blyant på en flate som blir skjult.",
                "**Bryt alle kanter et barn kan nå, nå — mens delene er "
                  "løse.** Kravet er brutt kant, ikke en bestemt metode: "
                  "45° fas eller avrunding, du velger. Fres med V-spor eller "
                  "avrundingsfres om du har fres; ellers gjør en blokkhøvel "
                  "eller en pussekloss med 120-korn nøyaktig samme nytte. "
                  "Viktigst: plateenhetens underside — begge styrelektenes "
                  "nedre kanter og begge kilene — for det er der et kne "
                  "møter treet når noen sitter ved bordet. Deretter platens "
                  "fire egne kanter, og så stolper, rekkverksbord, trinn og "
                  "stigevangenes kanter. Modellen tegner alle deler skarpe; "
                  "kantbrytningen er en instruks og flytter ingen mål.",
                "Bor alle gjennomgående hull i stolper, vanger, endebjelker "
                  "og benkevanger — diameter etter forboringskolonnen i "
                  "beslaglista. Bor gjennom begge deler samtidig, med delene "
                  "tvunget sammen.",
                "Forsenk hodene på alle festemidler som ender i en veggvendt "
                  "flate. Beslaglista sier hvilke ledd det gjelder.",
                "Forbor alle treskruer etter beslaglista. I bordene og i "
                  "all endeved er forboring et krav, ikke et råd.",
                "**Bor setene til de åtte skråskruene nå** — mens delene er "
                  "løse og ligger flatt på benken. Fire i den bakre "
                  "benkevangens forside (J8-B) og fire i stubbeføttenes "
                  "innersider (J10). Reist seng kommer du ikke til med "
                  "hverken kloss eller tvinger. Alt om setene og klossene er "
                  "tegnet opp på "
                  "[setedetalj.svg](../schematics/setedetalj.svg).",
                "Slik bores et sete: klem vinkelklossen mot flaten med TO "
                  "tvinger, hullet rett over merket, og legg en offerkloss "
                  "mot endeveden. Drillen i **gir 1 og slag AV** — et "
                  "forstnerbor i slagmodus brenner og vandrer. Trekk boret "
                  "helt ut 2–3 ganger per lomme og børst sponet ut; et fullt "
                  "forstnerbor skjærer ikke, det gnisser. Dybden er merket "
                  "du satte på boret da du lagde klossen: "
                  f"{G.TOE_JIG_SEATS['J8-B']:g} mm langs aksen på J8-B, "
                  f"{G.TOE_JIG_SEATS['J10']:g} mm på J10.",
                "På den bakre benkevangen står to lommer ved siden av "
                  "hverandre i hver ende, "
                  f"{G.TOE_SEAT_D + G.TOE_SEAT_MIN_WEB:g} mm fra senter til "
                  "senter. **Bor den som ligger nærmest kanten først** — da "
                  "har klossen hel flate å stå på. Når den andre skal bores, "
                  "hviler klossen delvis over den ferdige lomma; legg en "
                  "tynn list under den enden så den ikke vipper.",
                "Forbor for skruen med det samme, mens delen ligger som den "
                  "ligger: **lommebunnen er forborets egen jigg.** Bunnen "
                  "står vinkelrett på skrueaksen, så et brad-point-bor satt "
                  "i senter av den flate bunnen (⌀6 på J8-B, ⌀3,5 på J10) "
                  "retter seg selv inn i riktig vinkel. Ikke prøv å sikte "
                  "den på frihånd.",
                "Slå filtknotter under alle fire hjørnestolper og alle fire "
                  "stubbeføtter.",
            ],
            check=[
                "Romdelene skal IKKE kappes ferdig nå. Kapplista sier hvilke "
                  "— de kappes med overmål og finkappes i rommet.",
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
                   "Bench Rail Back (continuous)", "Table Ledger Back"],
            camera=(330, 24, 3.4),
            half_view=True,
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
                "Legg den bakre benkevangen ned mellom stolpene og fest den "
                  "etter J8-B. Det står ingen kloss under vangeenden — "
                  "**hullene du boret i steg 0 er jiggen**: vangen har "
                  "nøyaktig én høyde der hullene i vangen og hullene i "
                  "stolpen står over hverandre. Legg en list eller en tvinge "
                  "under vangen mens du skrur hvis du er alene. Vangen er "
                  "kappet nøyaktig så den fyller mellom de to stolpene — den "
                  "kan ikke tres inn senere.",
                "J8-B er skråskruer, og setene deres er boret i steg 0 — "
                  f"⌀{G.TOE_SEAT_D:g} flatbunnet lomme "
                  f"{G.TOE_JIG_SEATS['J8-B']:g} mm ned langs skruens egen "
                  f"akse, {G.TOE_JIG_ANGLES['J8-B']:g}° på flaten. Her skal "
                  "du bare skru. Skruen finner lomma selv gjennom forboret; "
                  "kjenn etter at hodet lander flatt på bunnen og ikke "
                  "stopper høyt. Stopper det høyt, står konusen på kanten av "
                  "forboret — skru ut, rens lomma for spon og ta den om "
                  "igjen.",
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
            joints={'J2-B': 2, 'J8-B': 2, 'J12': 2},
        ),
        dict(
            n=2,
            title="Reis bakrammen og skru den fast i veggen",
            parts=[],
            highlight=["Upper Side Rail Back"],
            camera=(330, 24, 3.4),
            thumbnails=True,
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
            parts=["Corner Post Front *", "End Beam Left", "End Beam Right"],
            camera=(325, 22, 3.4),
            half_view=True,
            intro="Nå bygges de to endene ut fra bakrammen. Endebjelken går "
                  "fra den bakre stolpen til den fremre og bærer begge "
                  "sidevanger.",
            do=[
                "Reis den fremre stolpen på plass mot sideveggen.",
                "Legg endebjelken opp mellom de to stolpene og fest den til "
                  "begge etter J1. **Det er ingen bærekloss under "
                  "bjelkeenden, og hullene fra steg 0 er jiggen:** bjelken "
                  "har nøyaktig én høyde der hullene i bjelken og hullene i "
                  "stolpen møtes, så du kan ikke sette den skjevt. Klem en "
                  "list på stolpens innside i høyde med bjelkens underkant "
                  "hvis du bygger alene — den listen tas av igjen.",
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
            joints={'J1': 4},
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
                "Fest den til begge fremre stolper etter J2. **Skruene "
                  "drives innenfra:** du står inne i sengerammen — den er "
                  "tom, spilene kommer først i steg 8 — og skrur gjennom "
                  "vangens innside og inn i stolpen. Da blir stolpens "
                  "forside, som er den flaten rommet ser, helt uten "
                  "skruehoder.",
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
            title="Fremre benkevanger, stubbeføtter og endelister",
            parts=["Bench Rail Front *", "Bench Stub Leg *",
                   "Bench End Cleat *"],
            camera=(330, 20, 3.4),
            half_view=True,
            intro="Den fremre benkevangen er delt i to. Midtpartiet er med "
                  "vilje åpent, slik at gulvet foran stigen er helt fritt. "
                  "Endelisten hører hjemme i dette steget og ikke blant "
                  "spilene: den er bæreverk som vangene, den står i samme "
                  "høyde som dem, og den skal stå ferdig før noe legges oppå.",
            do=[
                "Fest hver vangebit til sin fremre hjørnestolpe etter J8. "
                  "**Skruene drives innenfra**, fra vangens innside og inn i "
                  "stolpen, så stolpens forside blir stående uten "
                  "skruehoder. Du kommer til ovenfra: benken er åpen til "
                  "spilene går på i steg 7. Ingen kloss under enden — "
                  "hullene fra steg 0 holder vangen i riktig høyde.",
                "Sett en stubbefot under den innerste enden av hver "
                  "vangebit. Vangebiten skal slutte akkurat der foten står — "
                  "ingen utstikk forbi foten.",
                "Sett de to bakre stubbeføttene under den bakre benkevangen, "
                  "rett under de samme punktene.",
                "Fest alle fire føtter etter J10. Den ene 5×60 per fot er "
                  "en skråskrue nedenfra og opp i vangen, og setet er boret "
                  f"i steg 0 — ⌀{G.TOE_SEAT_D:g} flatbunnet lomme "
                  f"{G.TOE_JIG_SEATS['J10']:g} mm ned langs aksen, "
                  f"{G.TOE_JIG_ANGLES['J10']:g}° på fotens innerside. Skru "
                  "beslaget først, skråskruen sist.",
                f"ENDELISTEN, én i hver ende: skru den flatt på FORSIDEN av "
                  f"den bakre hjørnestolpen, med overkanten i flukt med "
                  f"benkevangens overkant ({G.END_CLEAT_Z1} mm over gulvet). "
                  f"To 5×60 ved siden av hverandre (J17) — {G.END_CLEAT_T} mm "
                  f"gjennom listen og {G.END_CLEAT_BITE} mm inn i stolpen, så "
                  f"det står {G.POST_T - G.END_CLEAT_BITE} mm igjen til "
                  f"veggflaten bak. Ikke bruk lengre skrue.",
            ],
            check=[
                "Ingenting skal krysse gulvet mellom de to benkene.",
                "Vater langs begge vangebiter, og samme høyde som den bakre "
                  "benkevangen.",
                "Alle fire føtter skal stå med hele endeflaten mot gulvet og "
                  "hele toppflaten mot vangen. Er det luft under en fot, kil "
                  "den ikke opp — juster den.",
                "Legg en rett list fra endelisten og bort på begge "
                  "benkevanger. Alle tre overkanter skal ta borti listen — "
                  "det er flaten spilene legges på i steg 7.",
                "Ingen skruespiss skal være synlig eller følbar på baksiden "
                  "av den bakre stolpen. Det er veggflaten.",
            ],
            joints={'J8': 2, 'J10': 4, 'J17': 2},
        ),
        dict(
            n=6,
            title="Stigen",
            parts=["Ladder Upright *", "Rung Block *", "Ladder Rung_*"],
            camera=(0, 16, 3.6),
            crop_to_subject=True,
            intro="Bygg hele stigen ferdig liggende på gulvet, og skru den så "
                  "på den fremre sidevangen.",
            do=[
                f"Skru stigeklossene på innsiden av hver stigevange (J5). "
                  f"Klossen er {G.RUNG_BLOCK_LEN} mm lang — nøyaktig så dyp "
                  f"som stigevangen — og skal ligge i flukt med vangens "
                  f"for- og bakkant, ikke stikke bakover slik trinnet gjør. "
                  f"Klosshøyden er trinnhøyden — mål to ganger.",
                "Legg trinnene på klossene og fest dem (J4).",
                "Reis stigen mot den fremre sidevangen. Trinnenes forkant "
                  "skal ligge i flukt med stigevangenes forkant — trinnene "
                  "stikker BAKOVER, ikke framover. Det som stikker bakover er "
                  "hylla den løse platen skal hvile på.",
                "Skru stigen fast til vangen etter J3 — **innenfra**, "
                  "gjennom sidevangen og inn i stigevangen, så stigevangens "
                  "forside blir uten skruehoder. Klem stigen fast mot vangen "
                  "først; du står på den andre siden når du skrur. "
                  "Gjennomgangshullene er boret i steg 0.",
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
            title="Benkespiler og endespiler",
            parts=["Bench Slat *", "Bench End Slat *"],
            camera=(330, 30, 3.4),
            intro=f"Fem spiler per benk, lagt oppå benkevangene — og helt ute "
                  f"ved hver vegg en {G.END_SLAT_LEN} mm ENDESPILE på "
                  f"endelisten fra steg 5. De to endespilene er det som gjør "
                  f"underetasjen til en seng i full lengde: uten dem stopper "
                  f"spilefeltet "
                  f"{G.BENCH_SLAT_W} mm fra veggen i hver ende, og putekanten "
                  f"har ingenting under seg.",
            do=[
                "Legg ut alle fem spilene på én benk før du skrur, og sjekk "
                  "delingen mot kapplista.",
                "Skru hver spile ned i den bakre og den fremre benkevangen, "
                  "én skrue per ende (J11). Forsenk hodene — dette er en "
                  "sitteflate.",
                "Gjenta speilvendt på den andre benken.",
                f"ENDESPILEN er kortere enn de andre, {G.END_SLAT_LEN} mm: "
                  f"den starter på stolpens forside, ikke på veggen — "
                  f"stolpen står i soveflaten her. Endelisten den skal hvile "
                  f"på sitter ferdig på stolpen fra steg 5; her legges bare "
                  f"spilen. Legg den mot veggen, tett inntil naboen, og skru "
                  f"én skrue ned i endelisten (J16) og én ned i den fremre "
                  f"benkevangen (J11-E).",
            ],
            check=[
                "Kjenn over hele benken med håndflaten: ingen skruehoder skal "
                  "stikke opp.",
                "Sett deg på begge benker.",
                "Endespilen skal ligge i nøyaktig samme plan som de andre — "
                  "legg en rett list på tvers over hele benken og se etter "
                  "lys under.",
            ],
            joints={'J11': 20, 'J11-E': 2, 'J16': 2},
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
            title="Løs plate med fire lekter — og ingen beslag",
            parts=["Movable Panel (bed mode)", "Panel Stiffener Batten *",
                   "Panel Front Batten *"],
            camera=(325, 30, 3.6),
            page="panel",
            intro="Platen er ikke et løst bord. Den er en liten enhet som "
                  "løftes ut i ett stykke og senkes rett ned igjen — i begge "
                  "stillinger. Lektene under den gjør to jobber: de gjør "
                  "platen stiv, OG de er styringen. De to lange går ned på "
                  "hver side av trinnenden med 2 mm klaring, så de finner "
                  "plassen selv. Det er ikke ett beslag i denne mekanismen, "
                  "og det skal ikke være én skrue synlig oppå platen.",
            do=[
                "Bor hullene i lektene FØR noe limes. Regelen er den samme "
                  "for alle fire delene, og den er lettest å huske slik: "
                  f"bor ⌀12 opp i undersiden TIL DET STÅR "
                  f"{G.PANEL_UPSCREW_PASS} mm igjen opp til plata, og ⌀3,5 "
                  "videre gjennom de siste "
                  f"{G.PANEL_UPSCREW_PASS} mm. På de to lange "
                  f"styrelektene, som er {G.BATTEN_H} mm hele veien, blir "
                  f"det {G.PANEL_UPSCREW_CBORE} mm kontrabor. På de to "
                  "skråkappede kilene blir det dypest ved roten og null ved "
                  "tuppen — tuppen ER "
                  f"{G.PANEL_UPSCREW_PASS} mm, så der ligger hodet i flukt "
                  "med kilens egen underside. Skruen tar "
                  f"{G.PANEL_UPSCREW_BITE} mm i den {G.PANEL_T} mm tykke "
                  f"platen uansett, med {G.PANEL_UPSCREW_COVER} mm plate "
                  "igjen over spissen.",
                "Legg platen med undersiden opp. Merk av de to lange "
                  f"avstivningslektene {G.NOSE_LEN} mm inn fra hver sidekant — det er "
                  "målet som gjør at de treffer utsiden av trinnenden.",
                "Lim (D3) hele lektas overkant, legg den på plass og skru "
                  "opp fra undersiden (J13a). Skruene er tvinger: de "
                  "trekker limfugen sammen og blir sittende.",
                "Samme sak for de to kilelektene, i flukt med platens "
                  "forkant og med den HØYE enden mot den lange lekta "
                  "(J13b) — den skråkappede tuppen peker ut mot platekanten. "
                  "De bærer hjørnet trinnet ikke rekker fram til.",
                "Ingenting går gjennom platens overside. Har du et hull "
                  "der, har du boret feil vei.",
                "Legg platen i sengestilling: senk den rett ned mellom "
                  "benkene, bakkanten på den bakre benkevangen, forkanten på "
                  "trinn 1. De to lange lektene skal gli ned på hver side av "
                  "trinnenden uten å tvinges.",
                "Prøv bordstilling: samme plate, samme lekter, rett ned på "
                  "bordbærelekta og trinn 2. Trinn 1 og trinn 2 ender på "
                  "samme sted i lengderetningen, så lektene finner "
                  "trinnenden i begge stillinger.",
            ],
            check=[
                "Skyv platen sidelengs. Den skal bevege seg et par "
                  "millimeter og så stoppe mot trinnenden — begge veier, i "
                  "begge stillinger.",
                "Vri på platen. Den skal kile seg med én gang: en vridning "
                  "drar begge lektene samme vei, og den ene tar imot.",
                "Platen skal ligge stødig på begge opplegg i begge "
                  "stillinger, uten å vippe. Den ligger på tre i hele "
                  "bredden bak og på trinnet foran.",
                "Se over platens overside i motlys. Ingen skruehoder, ingen "
                  "propper, ingen hull.",
                "Platen kan løftes rett opp. Det skal den kunne — låsen i "
                  "sengestilling er en egen avgjørelse, ikke en del av dette "
                  "steget.",
            ],
            joints={'J13a': 2, 'J13b': 2},
        ),
        dict(
            n=11,
            title="Madrass og puter",
            parts=["Mattress *", "Seat Cushion *",
                   "Back Cushion Left (bed mode)",
                   "Back Cushion Right (bed mode)"],
            camera=(330, 26, 3.4),
            no_fasteners=True,
            info_panel=True,
            avoid_top_left=True,
            intro="Sengen er dimensjonert rundt en STANDARD madrass på "
                  "80 × 200 cm — den er ikke spesialmål og skal ikke "
                  "spesialbestilles. Det eneste målet du må velge selv er "
                  "TYKKELSEN, og der er det bare ett riktig svar: "
                  f"{G.MATTRESS_H} mm. Vinduet er {G.MATTRESS_H_MIN}–"
                  f"{G.MATTRESS_H_MAX} mm, og en helt vanlig 160 mm madrass "
                  "er ULOVLIG i denne sengen — den legger spalten opp til "
                  "rekkverket midt i klemvinduet.",
            do=[
                "Legg madrassen på plass. En 80 × 200 presses de siste "
                  "millimeterne inn mellom veggene, og den skal fylle hele "
                  "dybden fra veggen til de fremre stolpene.",
                f"UNDERETASJEN: fire puter, alle "
                  f"{G.CUSHION_T} mm tykke og {G.LOWER_SLEEP_DEPTH} mm dype. "
                  f"To benkeputer på {G.SEAT_CUSHION_LEN} mm og to ryggputer "
                  f"på {G.BACK_CUSHION_LEN} mm — lagt etter hverandre dekker "
                  f"de nedre soveflate nøyaktig, "
                  f"{G.SEAT_CUSHION_LEN} + {G.BACK_CUSHION_LEN} + "
                  f"{G.BACK_CUSHION_LEN} + {G.SEAT_CUSHION_LEN} = "
                  f"{G.LOWER_SLEEP_LEN} mm.",
                f"Skjær et {G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} mm "
                  f"hakk i veggkanten på hver av de to benkeputene, der den "
                  f"bakre hjørnestolpen står. Brødkniv.",
                "SOFASTILLING: benkeputene ligger der de ligger — de flyttes "
                  "aldri. Ryggputene reises på høykant ytterst på hver benk, "
                  "med ryggen mot bordbærelekta.",
                f"MERK MAKSMÅLET PERMANENT. EN 747 krever det, og det er "
                  f"ikke en tusjstrek som skal kunne tørkes bort: skriv "
                  f"«MAKS MADRASS {G.MATTRESS_H_MAX} MM» på innsiden av en "
                  f"fremre stolpe, i høyden {G.SLAT_Z1 + G.MATTRESS_H_MAX} "
                  f"mm over gulvet. Den som bytter madrass om ti år skal "
                  f"kunne lese grensen av sengen selv.",
                f"Skriv nedre grense, {G.MATTRESS_H_MIN} mm, ved siden av. "
                  f"For tynn madrass åpner spalten under nederste "
                  f"rekkverksbord; for tykk lukker den seg ned i "
                  f"klemvinduet.",
            ],
            check=[
                "Ettertrekk alle festemidler som kan ettertrekkes.",
                "Madrassen skal ligge stramt mot veggen og mot de fremre "
                  "stolpene, uten spalte langs noen av de to lange kantene.",
                "Rist i sengen i begge retninger. Ingen bevegelse mot "
                  "bakveggen.",
                f"Mål spalten fra madrassens overside opp til undersiden "
                  f"av det nederste rekkverksbordet. Den skal være "
                  f"{G.EN_LIMB_BAND[0]:.0f}–{G.MAX_GUARD_OPENING} mm. Er "
                  f"den mindre, er madrassen for tykk.",
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
                + [G.mattress] + list(G.CUSHIONS_BED))
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


def SOFT_BUY(G, label):
    """The shopping line for a part that is foam: the reference mattress and
    the four cushions. They have no cut-list key because nothing is sawn."""
    if label.startswith("Mattress"):
        return (f"Madrass 80 × 200 cm, **{G.MATTRESS_H} mm tykk** "
                f"(vindu {G.MATTRESS_H_MIN:.0f}–{G.MATTRESS_H_MAX:.0f} mm)",
                "", "")
    if label.startswith("Seat Cushion"):
        return (f"Benkepute, skum **{G.CUSHION_T} mm** "
                f"({G.SEAT_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} mm, hakk "
                f"{G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} i veggkanten)",
                "", "")
    return (f"Ryggpute, skum **{G.CUSHION_T} mm** "
            f"({G.BACK_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} mm)", "", "")


def step_part_rows(G, st, cut_index):
    """[(antall, navn, dimensjon, lengde), ...] for the labels this step adds.

    `dimensjon` and `lengde` are empty strings for the reference mattress,
    which is bought rather than cut.
    """
    counts = {}
    for lbl in st["labels"]:
        key = cut_index.get(lbl)
        if key is None:                       # bought as foam, not cut as wood
            key = SOFT_BUY(G, lbl)
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
    "Bench rail, back (C5)": "Benkevange, bak (gjennomgående)",
    "Bench rail, front segment (D13)": "Benkevange, front (bit)",
    "Bench stub leg (W3)": "Stubbefot",
    "Bench slat (C3)": "Benkespile",
    "Bench end slat (V13)": "Endespile",
    "Bench end cleat (V13)": "Endelist",
    "Upper bed slat, short (D5/W4)": "Køyespile, kort (mot bakre stolpe)",
    "Upper bed slat, to the wall (W4)": "Køyespile, lang (inn til veggen)",
    "Upper bed slat": "Køyespile",
    "Upper bed slat (D5)": "Køyespile",
    "Guard rail, front segment (D2/D7/D13)": "Rekkverksbord, front",
    "Table ledger, back": "Bordbærelekt, bak",
    "Movable panel": "Løs plate",
    "Panel stiffener batten (M4)": "Avstivningslekt under plate",
    "Panel front cross batten (M5)": "Kilelekt under platens forkant (skråkappet)",
}


# The model gives every piece a cut-list line but does not record which part
# belongs to which line. This is that mapping, by label prefix, longest first.
# It is checked against CUT_LIST below: if the model ever grows, loses or
# renames a part, the assert in `part_cut_keys` fires.
LABEL_TO_CUT = [
    ("Upper Side Rail", "Upper side rail"),
    ("End Beam", "End beam"),
    ("Corner Post Back", "Corner post, back (W2, wall side)"),
    ("Corner Post Front", "Corner post, front"),
    ("Ladder Upright", "Ladder upright (D13)"),
    ("Rung Block", "Ladder rung block"),
    ("Ladder Rung_", "Ladder rung (tread)"),
    ("Bench Rail Back", "Bench rail, back (C5)"),
    ("Bench Rail Front", "Bench rail, front segment (D13)"),
    ("Bench Stub Leg", "Bench stub leg (W3)"),
    ("Bench Slat", "Bench slat (C3)"),
    ("Bench End Slat", "Bench end slat (V13)"),
    ("Bench End Cleat", "Bench end cleat (V13)"),
    ("Guard Rail Front", "Guard rail, front segment (D2/D7/D13)"),
    ("Table Ledger Back", "Table ledger, back"),
    ("Movable Panel", "Movable panel"),
    ("Panel Stiffener Batten", "Panel stiffener batten (M4)"),
    ("Panel Front Batten", "Panel front cross batten (M5)"),
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
        # The model now writes the line onto the piece as it makes it, so the
        # prefix table above has something to be checked AGAINST rather than
        # merely asserted for completeness.
        assert p.cut == out[p.label], \
            f"LABEL_TO_CUT puts '{p.label}' in {out[p.label]}, the model put " \
            f"it in {p.cut}"

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
    """[(no_name, section, length, qty, (xr, yr, zr), en, fit), ...].

    `fit` is the model's room-fit verdict for the whole line - None for a
    piece the workshop finishes, otherwise ("gulv"|"gulv+side"|"vegg"|
    "meddrag", overmål).
    The verdict is a rule in generate_loftbed.py; nothing here decides it.
    """
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
                     spans[(name, section, length)], name,
                     G.ROOM_LINES.get((name, section, length))))
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
# A piece is (name, finished length, OVERLENGTH). The third number is what
# the ROOM adds to the piece and the shop still has to saw off the board: a
# post that stands on the floor is cut 15 mm long and trimmed on site, and
# those 15 mm are wood, kerf and floor sweepings, not a rounding error. The
# packer therefore packs `fin + over` and reports `used` the same way - what
# comes off the board is what the board loses.
def _sawn(p):
    """What a piece actually takes out of a board."""
    return p[1] + p[2]


def pack(pieces, lengths=None):
    """First-fit-decreasing bin packing into the sale lengths of one profile.

    Boards are opened at the longest sale length and shrunk afterwards to the
    shortest one that still holds what they were given, which is what you
    would do at the counter - unless the profile only comes in one length, in
    which case there is nothing to shrink to.

    Every length in here is the SAWN length, finished plus the room's
    overlength. A cutting plan drawn on nominal lengths promises board that
    the saw has already eaten.
    """
    lengths = lengths or SALE_LENGTHS
    boards = []
    for piece in sorted(pieces, key=lambda p: -_sawn(p)):
        for b in boards:
            used = sum(_sawn(x) for x in b) + KERF * len(b)
            if used + _sawn(piece) <= max(lengths):
                b.append(piece)
                break
        else:
            assert _sawn(piece) <= max(lengths), \
                f"'{piece[0]}' is {_sawn(piece)} mm sawn - longer than any " \
                f"sale length"
            boards.append([piece])
    out = []
    for b in boards:
        need = sum(_sawn(x) for x in b) + KERF * (len(b) - 1)
        buy = min(s for s in lengths if s >= need)
        out.append(dict(buy=buy, pieces=b, used=sum(_sawn(x) for x in b),
                        rest=buy - need))
    out.sort(key=lambda b: (-b["buy"], -len(b["pieces"])))
    return out


def buy_table(G):
    rows = cut_table(G)
    by_section = {}
    for no_name, section, length, qty, _spans, _en, fit in rows:
        # fit[1] is the model's own total allowance for the line - one foot
        # trimmed, or one or two wall ends fine-cut. Nothing is decided here.
        over = fit[1] if fit else 0
        by_section.setdefault(section, []).extend(
            [(no_name, length, over)] * qty)
    out = []
    for section, pieces in sorted(by_section.items()):
        if "plate" in section or "panel" in section:   # sheet, not a stick
            out.append(dict(section=section, sheet=True, pieces=pieces))
            continue
        sale = SALE_LENGTHS_BY_SECTION.get(section)
        boards = pack(pieces, sale)
        # THE CLAIM THE LIST MAKES OUT LOUD - "du trenger ikke kjøpe mer
        # virke for det" - measured instead of hoped for: pack the same
        # pieces at their nominal lengths and demand the same shopping.
        nominal = pack([(n, ln, 0) for n, ln, _o in pieces], sale)
        assert sorted(b["buy"] for b in boards) == \
            sorted(b["buy"] for b in nominal), (
                f"{section}: med overmålet pakket blir handlelista "
                f"{sorted(b['buy'] for b in boards)} mot "
                f"{sorted(b['buy'] for b in nominal)} uten - "
                "innkjøpslista kan ikke lenger si at overmålet er gratis")
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


# WHAT THE ROOM FINISHES, IN WORDS. The kind and the millimetres come out of
# generate_loftbed.py; this only puts them in Norwegian. Nothing here decides
# how much - `over` is the model's own allowance for that line.
def _fit_text(G, fit):
    kind, over, ends = fit
    if kind == "gulv":
        return f"**+{over}** — trimmes i bunn"
    if kind == "gulv+side":
        return (f"**+{over}** — trimmes i bunn · siden mot veggen strekes "
                "opp ved bul")
    if kind == "vegg":
        hvor = "i hver ende" if ends == 2 else "i veggenden"
        return f"**+{over // ends}** {hvor} — finkappes"
    return "nominell — bredden strekes opp"


def _cut_rows(L, rows):
    """One position table. Returns the number of pieces it printed."""
    L.append("| Del | Dim. | Lengde | Ant. | X | Y | Z |\n")
    L.append("|---|---|---:|---:|---|---|---|\n")
    n = 0
    for no_name, section, length, qty, sp, _en, _fit in rows:
        n += qty
        L.append(f"| {no_name} | {section} | **{_fmt(length)}** | {qty} | "
                 f"{_axis(sp[0])} | {_axis(sp[1])} | {_axis(sp[2])} |\n")
    return n


def _room_rows(G, L, rows):
    L.append("| Del | Dim. | Lengde | Ant. | Kapp på stedet | X | Y | Z |\n")
    L.append("|---|---|---:|---:|---|---|---|---|\n")
    n = 0
    for no_name, section, length, qty, sp, _en, fit in rows:
        n += qty
        L.append(f"| {no_name} | {section} | **{_fmt(length)}** | {qty} | "
                 f"{_fit_text(G, fit)} | "
                 f"{_axis(sp[0])} | {_axis(sp[1])} | {_axis(sp[2])} |\n")
    return n


# THE ASSERT THAT READS THE INK. The split into two tables is a rule in the
# model, and a rule can be printed wrong. So the finished file is read back
# and every row is checked against the POSITION PRINTED IN THE SAME ROW: a
# part under «kapp på stedet» has to show an X that reaches a wall or a Z
# that starts on the floor, and a part under «kapp nå» has to show neither.
# The side-scribing sentence is checked the same way: only a row whose own Z
# says it stands on the floor over its whole sawn length, AND whose own X
# reaches an end wall, may carry it - because that combination is the one
# that meets the wall with a side. Nothing here repeats a length or a name.
def _assert_kappliste_ink(G, text):
    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]

    def span(cell):
        lo, hi = cell.replace(" (fordelt)", "").split("..")
        return float(lo.replace(",", ".")), float(hi.replace(",", "."))

    tables = {}
    head = None
    for line in text.split("\n"):
        if line.startswith("## "):
            head = line[3:].strip()
            tables.setdefault(head, [])
        elif line.startswith("| ") and head in tables:
            c = cells(line)
            if c[0] in ("Del", "---") or set(c[0]) <= set("-:"):
                continue
            tables[head].append(c)

    shop = next(v for k, v in tables.items() if k.startswith("Kapp nå —"))
    room = next(v for k, v in tables.items() if k.startswith("Kapp når rommet"))
    assert shop and room, "one of the two cut tables came out empty"

    n_side = 0
    for c in shop + room:
        is_room = len(c) == 8
        x0, x1 = span(c[-3])
        z0, z1 = span(c[-1])
        at_wall = x0 <= G.ROOM_TOL or x1 >= G.WALL_SPAN - G.ROOM_TOL
        touches = at_wall or z0 == 0
        assert touches == is_room, (
            f"«{c[0]}» står under «{'kapp på stedet' if is_room else 'kapp nå'}»"
            f", men posisjonen i samme rad sier X {c[-3]}, Z {c[-1]}")
        if is_room:
            allowed = {f"+{G.ROOM_OVER_FLOOR}", f"+{G.ROOM_OVER_WALL}"}
            assert (any(a in c[4] for a in allowed)
                    or "nominell" in c[4]), \
                f"«{c[0]}» har overmålet «{c[4]}», som ikke er en av " \
                f"modellens: {sorted(allowed)} eller nominell lengde"
            length = float(c[2].strip("*").replace(",", "."))
            stands = z0 == 0 and abs(z1 - z0 - length) < 0.5
            side = "siden mot veggen" in c[4]
            assert side == (stands and at_wall), (
                f"«{c[0]}» {'sier' if side else 'sier ikke'} at siden mot "
                f"veggen strekes opp, men raden selv sier lengde {c[2]}, "
                f"X {c[-3]}, Z {c[-1]}")
            n_side += int(side)

    want_side = sum(1 for f in G.ROOM_LINES.values() if f[0] == "gulv+side")
    assert n_side == want_side, \
        f"{n_side} rader streker opp siden mot veggen, mot {want_side} " \
        f"«gulv+side»-linjer i modellen"

    assert len(shop) + len(room) == len(G.CUT_LIST), \
        f"{len(shop)} + {len(room)} rader mot {len(G.CUT_LIST)} linjer i " \
        "modellens kappliste"
    assert len(room) == len(G.ROOM_LINES), \
        f"{len(room)} romdel-rader mot {len(G.ROOM_LINES)} romdel-linjer i " \
        "modellen"


def emit_kappliste(G, out_dir):
    rows = cut_table(G)
    shop = [r for r in rows if r[6] is None]
    room = [r for r in rows if r[6] is not None]
    L = [HEAD, "# Kappliste\n\n",
         "Alle mål i mm. Alle kutt er 90° på to nær — se merknaden "
         "under tabellene. Posisjonen er delens plass i "
         f"modellen: X langs veggen (0 = venstre vegg, {G.WALL_SPAN} = høyre "
         f"vegg), Y i dybden ({_fmt(G.WALL_Y)} = bakveggen), Z opp fra "
         "gulvet.\n\n",
         "Lista står i to bolker, og skillet er en regel: **en del som "
         f"kommer nærmere enn {_fmt(G.ROOM_TOL)} mm fra en endevegg, eller "
         "som står på gulvet, får sluttmålet sitt av rommet — ikke av "
         "modellen.** Rommet er hverken i vinkel eller i vater. Resten "
         "kappes ferdig på bukken.\n\n",
         "Mål rommet før du kapper romdelene: se "
         "[byggesteg](byggesteg.md#før-steg-0--mål-rommet).\n\n"]

    L.append("## Kapp nå — verksteddeler\n\n")
    n_shop = _cut_rows(L, shop)
    L.append(f"\n**{n_shop} deler.** Rommet bestemmer ingen mål på disse. "
             "Kapp dem ferdig med én gang.\n\n")

    L.append("## Kapp når rommet er ferdig — romdeler\n\n")
    n_room = _room_rows(G, L, room)
    L.append(f"\n**{n_room} deler.** Kapp dem med overmålet i kolonnen "
             "«Kapp på stedet», og finkapp på stedet:\n\n")
    L.append(f"* **Står på gulvet:** kapp {G.ROOM_OVER_FLOOR} mm for lang. "
             "Gulvet legges først. Så trimmes foten til rammen står i "
             "vater. Strek opp med avstandskloss — meddrag.\n")
    L.append("* **Står på gulvet inntil endevegg — hjørnestolpene:** samme "
             "trimming i bunn, og i tillegg strekes siden. Stolpen står "
             "helt inntil veggen uten klaring, så en bul i veggen må tas i "
             "treet: hold stolpen i lodd på plass, strek opp veggsiden med "
             "avstandskloss og høvle av til den står i lodd inntil veggen. "
             "Ikke legg på noe i bredden — den nominelle dimensjonen står, "
             "det er bare bulen som går av.\n")
    L.append(f"* **Går fra vegg til vegg:** kapp {G.ROOM_OVER_WALL} mm for "
             "lang i hver ende som møter vegg. Finkapp etter målt "
             "nisjebredde.\n")
    L.append("* **Bredden mot veggen:** kappes på nominell lengde. Det er "
             "BREDDEN som tilpasses, ikke lengden — ytterkanten strekes opp "
             "etter veggen så fugen blir jevn.\n\n")
    L.append("Kapp kanter som møter vegg eller gulv med lite bakfall. Da er "
             "det bare den synlige kanten som bestemmer fugen.\n\n")

    total = n_shop + n_room
    L.append(f"**{total} deler i alt.**\n\n")
    L.append("«(fordelt)» betyr at delene i den raden står på flere "
             "posisjoner langs den aksen; kolonnen viser da hele området de "
             "dekker. Nøyaktige posisjoner står i "
             "[nøkkelmål](nokkelmal.md).\n\n")
    # V4: THE TWO CUTS THAT ARE NOT 90 DEGREES, named where the "alle kutt er
    # 90°" line is, so the two do not have to be reconciled by the reader.
    L.append("**Ett unntak fra «alle kutt er 90°»:** de to kilelektene under "
             "platens forkant. De sages i ett rett snitt fra full "
             f"{G.NOSE_ROOT_H} mm ved roten — enden som støter mot "
             f"styrelekta — ned til {G.NOSE_TIP_H} mm ved tuppen på platens "
             "ytterkant, altså "
             + f"{G.NOSE_TAPER_DEG:.1f}".replace(".", ",")
             + "° på langs. Overkanten, "
             "den som limes mot plata, blir stående urørt i hele lengden. "
             "Håndsag eller båndsag; se steg 0 og J13b.\n\n")

    # SHOP AIDS: cut, but not built in. They are not parts, so they are not in
    # the count above and not in parts.tsv - and they are here rather than in
    # a note somewhere because a jig you were never told to make is a jig you
    # do not have when you need it.
    L.append("## Hjelpedeler — kappes, men bygges ikke inn\n\n")
    L.append("| Del | Dim. | Lengde | Ant. | Kapp | Brukes til |\n")
    L.append("|---|---|---:|---:|---|---|\n")
    for aid in G.SHOP_AIDS:
        L.append(f"| {aid['name']} | "
                 f"{aid['section'].replace('x', '×')} | "
                 f"**{_fmt(aid['length'])}** | {aid['qty']} | "
                 f"{aid['cut']} | {aid['use']} |\n")
    L.append("\nDisse er ikke med i de "
             f"{total} delene over og ikke i innkjøpslista — de kappes av "
             "restene i steg 0.\n\n")

    by_section = {}
    for no_name, section, length, qty, _sp, _en, _fit in rows:
        by_section[section] = by_section.get(section, 0) + qty
    L.append("Fordelt på dimensjon: "
             + " · ".join(f"**{s}** {n} stk."
                          for s, n in sorted(by_section.items(),
                                             key=lambda kv: -kv[1]))
             + "\n\n")
    board = G.sec(G.BOARD36_T, G.BOARD36_W).replace("x", "×")
    lens = {}
    for no_name, section, length, qty, _sp, _en, _fit in rows:
        if section == board:
            lens[length] = lens.get(length, 0) + qty
    L.append("Sagstopp for hovedbordet " + board + ": "
             + " · ".join(f"**{qty} stk. à {_fmt(ln)}**"
                          for ln, qty in sorted(lens.items(), reverse=True))
             + f" — {len(lens)} innstilling"
             + ("er" if len(lens) != 1 else "")
             + " på sagen, ikke én per del.\n")
    text = "".join(L)
    _assert_kappliste_ink(G, text)
    write(os.path.join(out_dir, "kappliste.md"), text)


def emit_innkjopsliste(G, out_dir):
    tab = buy_table(G)
    # ROMDELENE KAPPES FOR LANGE, og kappeplanen under er PAKKET med
    # overmålet: en romdel spiser lengde + overmål av bordet sitt, fordi det
    # er det sagen gjør. Resten i tabellen er derfor allerede resten ETTER at
    # overmålet er tatt, og at det likevel ikke koster ett bord mer er
    # asserten i buy_table().

    L = [HEAD, "# Innkjøpsliste — trevirke\n\n",
         "Høvlet konstruksjonsvirke C24 der ikke annet er nevnt. "
         f"Kappingen under er regnet med {KERF} mm sagsnitt mellom hvert "
         "kutt, og hvert bord er valgt som den korteste salgslengden som "
         "rommer det som skal kappes av det — blant de lengdene dimensjonen "
         "faktisk selges i. Se merknadene nederst.\n\n",
         "Romdelene kappes for lange og finkappes i rommet — se "
         "[kapplista](kappliste.md). Overmålet er regnet inn i kappeplanen "
         "under, og står som **+ tall** etter lengden: det er tre som går av "
         "bordet. Det koster likevel ikke ett bord mer — det går av resten, "
         "og det er en assert.\n\n"]

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
            for name, ln, ov in b["pieces"]:
                per[(name, ln, ov)] = per.get((name, ln, ov), 0) + 1
            txt = " + ".join(
                f"{q} × {_fmt(ln)}" + (f" + {_fmt(ov)}" if ov else "")
                + f" ({name})"
                for (name, ln, ov), q in sorted(per.items()))
            # THE ASSERT THAT READS THE PACKED INK: the row's own numbers have
            # to add up on the row. Everything sawn off this board, kerf
            # between each cut, plus the rest printed beside it, is the board
            # that was bought - overlength included, because the overlength is
            # in the pieces now.
            sawn = sum(ln + ov for _n, ln, ov in b["pieces"])
            cuts = KERF * (len(b["pieces"]) - 1)
            assert abs(sawn + cuts + b["rest"] - b["buy"]) < 0.5, (
                f"bord {i} av {e['section']}: {_fmt(sawn)} kappet + "
                f"{_fmt(cuts)} sagsnitt + {_fmt(b['rest'])} rest er ikke "
                f"{_fmt(b['buy'])} kjøpt")
            L.append(f"| {i} | {_fmt(b['buy'])} | {txt} | "
                     f"{_fmt(b['rest'])} |\n")
        L.append("\n")
        # SHOP AIDS COME OFF THE OFFCUT PILE, and the manual says so in two
        # places (kappliste, steg 0). That claim is only true if a board of
        # the right profile actually has the rest to give, so it is checked
        # here rather than hoped for.
        # K5 made the jig two blocks of two plies each, so this is no longer
        # "does one offcut hold one piece" but "does one offcut hold the whole
        # pile, kerf between each" - the pieces are all the same length, so
        # they come off the same rest in one row.
        mine = [a for a in G.SHOP_AIDS
                if a["section"] == e["section"].replace("×", "x")]
        if mine:
            # Resten er allerede resten etter romdelenes overmål - den er
            # pakket inn. Jiggene spiser av det som da er igjen.
            best = max(bb["rest"] for bb in e["boards"])
            pieces = [(a["name"], a["length"])
                      for a in mine for _ in range(a["qty"])]
            need = sum(ln for _n, ln in pieces) + KERF * (len(pieces) - 1)
            assert best >= need, (
                f"the shop aids on {e['section']} come to {need} mm with "
                f"{KERF} mm of kerf between them and the longest offcut on "
                f"that profile is {best} mm - the manual says they come off "
                f"the rest pile and they do not")
            L.append("Hjelpedelene på denne dimensjonen — "
                     + " + ".join(
                         f"{a['qty']} × {_fmt(a['length'])} mm "
                         f"({a['name'].split(' —')[0]})" for a in mine)
                     + f", til sammen {_fmt(need)} mm med sagsnitt — kappes "
                     f"av resten over. Den lengste er {_fmt(best)} mm, så det "
                     f"går av rest og du trenger ikke kjøpe bord til dem. "
                     f"Se [kapplista](kappliste.md).\n\n")

    # MYKT. The mattress and the four cushions are the only things on the
    # shopping list that are not timber, and they were the only things not on
    # it at all - the reader had to find them in ASSEMBLY §5. They belong here,
    # in their own section, so that one list is the whole trip.
    L.append("## Mykt — kjøpes, ikke kappes\n\n")
    L.append("Ikke trelast, men det står på samme handletur. Skum kjøpes som "
             "plate eller som ferdig skummadrass og kappes med brødkniv eller "
             "elektrisk kniv.\n\n")
    L.append("| Hva | Mål | Ant. | Merknad |\n|---|---|---:|---|\n")
    L.append(f"| Madrass, overkøye | 80 × 200 cm, **{G.MATTRESS_H} mm tykk** "
             f"| 1 | Vindu {G.MATTRESS_H_MIN:.0f}–{G.MATTRESS_H_MAX:.0f} mm. "
             f"En vanlig 160 mm er ULOVLIG her — se nøkkelmål |\n")
    L.append(f"| **Benkepute**, underetasjen | "
             f"**{G.SEAT_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} × "
             f"{G.CUSHION_T} mm** | 2 | Hakk {G.CUSHION_NOTCH[0]} × "
             f"{G.CUSHION_NOTCH[1]} mm i veggkanten, der den bakre "
             f"hjørnestolpen står |\n")
    L.append(f"| **Ryggpute**, underetasjen | "
             f"**{G.BACK_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} × "
             f"{G.CUSHION_T} mm** | 2 | Rene rektangler |\n")
    L.append(f"| Trekk | — | 5 | Skum uten trekk smuldrer. Regn det som en "
             f"egen post |\n\n")
    L.append(f"**De fire putene er én skumplate.** "
             f"{G.SEAT_CUSHION_LEN} + {G.BACK_CUSHION_LEN} + "
             f"{G.BACK_CUSHION_LEN} + {G.SEAT_CUSHION_LEN} = "
             f"{G.LOWER_SLEEP_LEN} mm, og dybden er {G.LOWER_SLEEP_DEPTH} mm "
             f"— altså nøyaktig en 80 × 200 skumplate med "
             f"{G.CUSHION_SHEET_WASTE} mm til overs på lengden. Kjøp én "
             f"plate, kapp fire ganger. Samme regnestykke gjelder om du "
             f"heller kjøper en billig skummadrass 80 × 200 og deler den.\n\n")
    L.append("## Merknader fra butikken\n\n")
    board = G.sec(G.BOARD36_T, G.BOARD36_W).replace("x", "×")
    slat = G.sec(G.BOARD23_T, G.BOARD36_W).replace("x", "×")
    L.append(f"* **{slat}** er det største bordet i denne sengen i antall og "
             f"lengde — de 24 spilene er kappet av det, og ingenting annet er. "
             f"**{board}** tar resten av det flate virket: stolper, "
             f"rekkverksbord og endebjelker. Ring og bestill før du drar; "
             f"butikken har sjelden nok av én dimensjon på lager. Får du ikke "
             f"akkurat disse målene, kan modellen kjøres om på en "
             f"nabodimensjon — det er én konstant i `generate_loftbed.py` — "
             f"men da må hele kapplista og alle nøkkelmål regnes på nytt. Ikke "
             f"improviser på sagbenken.\n")
    L.append(f"* **Kjøp ett bord {slat} ekstra.** Planen over bruker fem, og "
             f"fem er nok. Spilene er den ene delen det er 24 like av, og et "
             f"reservebord koster mindre enn en ny tur.\n")
    only = ", ".join(
        f"**{s}** finnes bare i "
        + " / ".join(f"{ln / 1000:.1f}".replace(".", ",") + " m"
                     for ln in sorted(lns))
        for s, lns in sorted(SALE_LENGTHS_BY_SECTION.items()))
    L.append(f"* Salgslengder: {only}. Kappeplanen over er derfor lagt på den "
             f"lengden alene — de kortere salgslengdene finnes ikke i denne "
             f"dimensjonen, og et bord du ikke kan kjøpe er ingen plan.\n")
    # U5: the two lekt dimensions are named off the model, not typed in, so a
    # profile that leaves the bed leaves this sentence too. 48×48 used to be a
    # third one here, with an "unless you can only get klasse 1" escape for the
    # four stub legs; the legs are cut from the 48×73 bench-rail board now, and
    # that board also holds the load-bearing rungs, so there is no escape left
    # and none is needed.
    lekt = " og ".join(x.replace("x", "×") for x in (
        G.sec(G.BLOCK_T, G.BLOCK_H), G.sec(G.BENCH_RAIL_T, G.BENCH_RAIL_H)))
    L.append(f"* **Alt konstruksjonsvirke kjøpes som C24** (styrkesortert), "
             f"også lektdimensjonene {lekt}. Står de i hylla bare som "
             f"«klasse 1 lekt/rekke — ikke-bærende», så spør i skranken: "
             f"stigevangene, rungetrinnene og stubbeføttene er alle bærende, "
             f"og lasttabellen regner C24.\n")
    L.append(f"* Platen er **{G.PANEL_W} mm bred** og kappes av **18 mm "
             f"kryssfiner**. "
             + (f"Merk at *begrunnelsen* er en annen enn før: fram til K2 var "
                f"platen 652 mm bred, altså bredere enn de "
                f"{G.LIMTRE_SHELF_W} mm limtre furu stopper på i hylla, og "
                f"kryssfiner var det eneste som fantes i den bredden. "
                f"{G.PANEL_W} går inn i en {G.LIMTRE_SHELF_W} mm limtreplate. "
                f"Materialet står likevel — lasttabellen, uttrekket for "
                f"oppskruene og propp-argumentet i J13 er alle regnet på "
                f"kryssfiner — men det er et **valg** nå og ikke en tvang. "
                f"Ført opp som åpent punkt, ikke stilltiende endret.\n"
                if G.PANEL_FITS_LIMTRE else
                f"Limtre furu i butikkhylla stopper på "
                f"{G.LIMTRE_SHELF_W} mm.\n"))
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
        (G.BENCH_TOP, "benkeoverflate (sittehøyde uten pute)"),
        (G.CUSHION_TOP_BENCH, "**puteoverflate — nedre soveflate og "
                              "sittehøyde med pute** (V13)"),
        (G.LEDGER_BACK_Z0, "bordbærelektas underkant"),
        (G.RUNG_TOPS[1], "bordbærelektas overkant = trinn 2 = platens "
                         "underside i bordstilling"),
        (G.PANEL_TOP_TABLE, "bordplate"),
        (G.BACKREST_Z1, "ryggputens topp i sofastilling (V13)"),
        (G.RUNG_TOPS[2], "trinn 3"),
        (G.RUNG_TOPS[3], "trinn 4"),
        (G.END_BEAM_Z0, "endebjelkens underkant"),
        (G.RAIL_BOTTOM, "endebjelkens overkant = sidevangens underkant "
                        "(fri høyde under sengen)"),
        (G.RAIL_TOP, "sidevangens overkant"),
        (G.SLAT_Z1, "spilebunn / madrassens underside / bakre stolpetopp"),
        (G.MATTRESS_Z1, "madrassens overside (ved "
                        f"{G.MATTRESS_H} mm madrass; lovlig band "
                        f"{G.MATTRESS_H_MIN}–{G.MATTRESS_H_MAX})"),
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
                   "endebjelkeender og bakre stubbeføtter ligger i dette "
                   "planet. Ingenting får stikke bak det."),
        (G.BACK_RAIL_Y0, "bakre sidevange, benkevange, bordbærelekt og "
                         "spilebunn — bakkant; bakre stolpes forside"),
        # Bordbærelekta er 48 dyp som benkevangen, ikke en 21 mm bordkant:
        # forsiden ligger i BACK_RAIL_Y1 og har ingen egen rad. (Den hadde en
        # rad regnet med BOARD_T her, og den ga et Y-plan som ikke finnes.)
        (G.BACK_RAIL_Y1, "bakre sidevanges, benkevanges og bordbærelektas "
                         "forside; avstivningslektenes bakkant"),
        (G.RUNG_Y0, "trinnenes bakkant (hylla platen hviler på)"),
        (G.BATTEN_Y1, "platens forkant; avstivningslektenes og kilelektenes "
                      "forkant"),
        (G.FRONT_RAIL_Y0, "fremre sidevange og benkevange — bakkant"),
        (G.FRONT_RAIL_Y1, "fremre sidevanges forside = fremre stolpers og "
                          "stigevangers bakside = spilebunnens forkant"),
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
    L.append(f"| Avstivningslekter (styrer platen) | "
             f"{_rng(G.BATTEN_X[0], G.BATTEN_X[0] + G.BATTEN_W)}"
             f" og {_rng(G.BATTEN_X[1], G.BATTEN_X[1] + G.BATTEN_W)} |\n")
    L.append(f"| Kilelekter under forkanten | "
             f"{_rng(*G.NOSE_X[0])} og {_rng(*G.NOSE_X[1])} |\n")
    L.append(f"| Klaring lekt → trinnende | {G.PANEL_FIT} mm hver vei "
             f"(trinnendene står på X {G.LADDER_INNER_L} og "
             f"{G.LADDER_INNER_R} i begge stillinger) |\n\n")

    # K2: the width windows. This is the one number in the bed that looks like
    # a free choice and is not, so the table is emitted from the same lists the
    # assert uses - it cannot say something the build would let through.
    L.append("### Platebredden er kvantisert — lovlige vinduer\n\n")
    L.append(f"Åpningen mellom benkene er fast, **{G.PANEL_OPENING} mm**, så "
             f"sideklaringen er `({G.PANEL_OPENING} − bredde) / 2` på hver "
             f"side. EN 747 gjør bare tre klaringsbånd lovlige — under "
             f"{_fmt(G.EN_FINGER_FREE)} mm kommer ikke fingeren inn, "
             f"{_fmt(G.EN_GAP_BAND[0])}–{_fmt(G.EN_GAP_BAND[1])} mm går den "
             f"fritt gjennom, {_fmt(G.EN_LIMB_BAND[0])}–"
             f"{_fmt(G.EN_LIMB_BAND[1])} mm går hele lemmet fritt og "
             f"åpningen er fortsatt under EN 747s egen 75 mm-grense — og "
             f"mellom båndene kiler fingeren seg. Bredden er derfor ikke en "
             f"skrue man vrir på: den lander i ett av tre vinduer, eller så "
             f"er den ulovlig.\n\n")
    L.append("| Klaringsbånd | Lovlig platebredde | |\n|---|---|---|\n")
    _rowsw = sorted(zip(G.PANEL_WIDTH_WINDOWS,
                        sorted(G.EN_LEGAL_GAP_BANDS, reverse=True)))
    for (wlo, whi), (glo, ghi) in _rowsw:
        if wlo <= G.PANEL_W <= whi:
            note = f"**valgt — {G.PANEL_W} mm, {G.PANEL_SIDE_GAP} mm klaring**"
        elif wlo <= 652 <= whi:
            note = "tidligere vindu (652 mm)"
        elif glo == 0:
            note = f"upraktisk — spiser opp de {G.PANEL_FIT} mm innsettingsklaring"
        else:
            note = ""
        L.append(f"| {_fmt(glo)}–{_fmt(ghi)} mm | "
                 f"{_fmt(wlo)}–{_fmt(whi)} mm | {note} |\n")
    for flo, fhi in G.PANEL_WIDTH_FORBIDDEN:
        L.append(f"| — | **{_fmt(flo)}–{_fmt(fhi)} mm** | **forbudt** — "
                 f"klaringer {_fmt((G.PANEL_OPENING - fhi) / 2)}–"
                 f"{_fmt((G.PANEL_OPENING - flo) / 2)} mm, midt i klembåndet |\n")
    L.append(f"\nBredden deltar **ikke** i begrensningene på stillingsbyttet — "
             f"det er høyden og dybden på plateenheten som møter "
             f"overføringssjakten ({G.TRANSFER_SLOT} mm fri høyde mot en "
             f"{G.PANEL_UNIT_H} mm høy enhet). Å smalne platen gir mer slingring "
             f"ved innsettingen og mindre bordflate, ingenting annet. "
             f"Modellen asserter vinduene: en «bare litt smalere»-endring "
             f"stopper byggeporten med akkurat denne tabellen.\n\n")

    slat_pitch = (G.SLAT_X_END - G.SLAT_X_START - G.BED_SLAT_W) / (G.SLAT_COUNT - 1)
    L.append(f"**Køyespiler:** {G.SLAT_COUNT} stk., første spile starter på "
             f"X {G.SLAT_X_START}, deling {_fmt(slat_pitch)} mm, siste spile "
             f"slutter på X {G.SLAT_X_END}. Åpning mellom spilene "
             f"{_fmt(slat_pitch - G.BED_SLAT_W)} mm.\n\n")
    L.append(f"**Benkespiler:** {G.BENCH_SLAT_COUNT} per benk, deling "
             f"{_fmt(G.BENCH_SLAT_PITCH)} mm, felt X {G.BENCH_SLAT_X_START}.."
             f"{G.BENCH_LEN} (speilvendt på den andre benken).\n\n")
    L.append(f"**Endespiler (V13):** 1 per benk, {G.END_SLAT_LEN} mm lang, X "
             f"{G.END_SLAT_X[0]}..{G.END_SLAT_X[0] + G.BENCH_SLAT_W} og "
             f"{G.END_SLAT_X[1]}..{G.WALL_SPAN}, Y {G.END_SLAT_Y0}.."
             f"{G.END_SLAT_Y1}. Den er kortere fordi den starter på den bakre "
             f"hjørnestolpens forside, og den lukker feltet helt ut til "
             f"veggen — spalten inn til første benkespile er "
             f"{G.END_SLAT_GAP} mm. Uten den stopper soveflaten nede "
             f"{G.BENCH_SLAT_W} mm fra veggen i hver ende. Endelisten under "
             f"den er {G.END_CLEAT_T}×{G.END_CLEAT_H} × {G.END_CLEAT_LEN} mm, "
             f"skrudd på stolpens forside (J17).\n\n")

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
    L.append(f"| Madrass, overkøye | **standard 80 × 200 cm.** Sengen er "
             f"dimensjonert rundt den; liggeflaten er {G.WALL_SPAN} × "
             f"{G.MATTRESS_W} mm, så madrassen presses de siste "
             f"{2000 - G.WALL_SPAN} mm inn mellom veggene og fyller bredden "
             f"nøyaktig |\n")
    L.append(f"| **Madrasstykkelse** | **{G.MATTRESS_H_MIN}–"
             f"{G.MATTRESS_H_MAX} mm — kjøp {G.MATTRESS_H} mm.** Åpningen fra "
             f"madrassens overside opp til nedre rekkverksbånd skal ligge i "
             f"EN 747-båndet {G.EN_LIMB_BAND[0]:.0f}–"
             f"{G.MAX_GUARD_OPENING} mm. Tynnere enn {G.MATTRESS_H_MIN} og "
             f"åpningen blir større enn {G.MAX_GUARD_OPENING}; **tykkere enn "
             f"{G.MATTRESS_H_MAX} og den faller ned i klemvinduet under "
             f"{G.EN_LIMB_BAND[0]:.0f} mm**. En vanlig 160 mm madrass er "
             f"altså ULOVLIG her. Modellen tegner {G.MATTRESS_H} mm, som gir "
             f"{G.GUARD_BAND_Z0[0] - G.MATTRESS_Z1} mm — midt i båndet |\n")
    L.append(f"| **Maks madrasstykkelse merkes på sengen** | "
             f"{G.MATTRESS_H_MAX} mm. EN 747 krever at maksmålet står "
             f"permanent på sengen. Merk linja "
             f"{G.SLAT_Z1 + G.MATTRESS_H_MAX} mm over gulvet — "
             f"{G.MATTRESS_H_MAX} mm over spilene — på innsiden av en fremre "
             f"stolpe (steg 11) |\n")
    wander = getattr(G, "MATTRESS_WANDER", 0)
    if wander:
        L.append(f"| Madrassens sideveis vandring | {wander} mm mellom "
                 f"veggen og de fremre stolpene |\n")
    else:
        L.append("| Madrassens sideveis vandring | ingen — madrassen fyller "
                 "hele bredden mellom veggen og de fremre stolpene |\n")
    L.append(f"| **Soveflate, underetasjen** | **{G.LOWER_SLEEP_LEN} × "
             f"{G.LOWER_SLEEP_DEPTH} mm** — samme lengde som overkøyen. De to "
             f"bakre hjørnestolpene står i flaten og tar et "
             f"{G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} mm hjørne i hver "
             f"ende; ellers er den hel |\n")
    L.append(f"| **Puter, tykkelse** | **{G.CUSHION_T} mm, alle fire.** Lik "
             f"tykkelse er hele poenget: fire like tykke puter er én seng. "
             f"Sittehøyden blir {G.BENCH_TOP} + {G.CUSHION_T} = "
             f"**{G.CUSHION_TOP_BENCH} mm** |\n")
    L.append(f"| Puter, dybde | {G.LOWER_SLEEP_DEPTH} mm — hele flatens dybde, "
             f"vegg til fremre stolpeplan |\n")
    L.append(f"| **Benkepute (2 stk.)** | **{G.SEAT_CUSHION_LEN} × "
             f"{G.LOWER_SLEEP_DEPTH} × {G.CUSHION_T} mm** — 1/3 av lengden. "
             f"Skjær et {G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} mm hakk i "
             f"veggkanten, der stolpen står |\n")
    L.append(f"| **Ryggpute (2 stk.)** | **{G.BACK_CUSHION_LEN} × "
             f"{G.LOWER_SLEEP_DEPTH} × {G.CUSHION_T} mm** — 1/6 av lengden. "
             f"Rene rektangler |\n")
    L.append(f"| Regnestykket | {G.SEAT_CUSHION_LEN} + {G.BACK_CUSHION_LEN} + "
             f"{G.BACK_CUSHION_LEN} + {G.SEAT_CUSHION_LEN} = "
             f"**{G.LOWER_SLEEP_LEN} mm**. {G.LOWER_SLEEP_LEN} deler seg ikke "
             f"på 6, så tredelen er rundet ned og sjettedelen opp — summen er "
             f"eksakt, og det er summen som må stemme |\n")
    L.append(f"| Alle fire av én skumplate | 80 × 200 cm dekker dem: "
             f"{G.CUSHION_SHEET[0]} mm er nøyaktig dybden og "
             f"{G.CUSHION_SHEET[1]} mm er {G.CUSHION_SHEET_WASTE} mm mer enn "
             f"lengden. Fire tverrkapp |\n")
    L.append(f"| Midtsonen ligger | {G.PANEL_BENCH_DIP} mm lavere enn "
             f"benkene ({G.CUSHION_TOP_PANEL} mot {G.CUSHION_TOP_BENCH} mm). "
             f"Putene er like tykke likevel — skummet tar de "
             f"{G.PANEL_BENCH_DIP} millimeterne, og ingen puteskjøt ligger på "
             f"en sonegrense |\n")
    L.append(f"| Hodehøyde over nedre soveflate | {G.LOWER_HEADROOM} mm til "
             f"køyespilene ({G.LOWER_HEADROOM_RAIL} mm under sidevangene) "
             f"|\n")
    L.append(f"| Ryggpute i sofastilling | står på høykant ytterst på hver "
             f"benk: {G.CUSHION_T} mm tykk, {G.LOWER_SLEEP_DEPTH} mm dyp, "
             f"{G.BACK_CUSHION_LEN} mm høy, topp {G.BACKREST_Z1} mm. Ryggen "
             f"mot bordbærelekta |\n\n")

    # REFERANSEKROPPEN. Tallene under er de eneste i nøkkelmål som er målt på
    # noe annet enn tre: fire barnekropper i modellen, hver bygget av 14
    # primitiver etter AnthroKids og posert i den stillingen raden handler om.
    # Ingen av dem er skrevet inn her - alle kommer ut av modellens egen
    # måleblokk, akkurat som resten av tabellen.
    L.append(f"\n## Referansekroppen — hva sengen er til for\n\n"
             f"Modellen har fire *referansekropper*: et barn på "
             f"**{G.FIGURE_H:.0f} mm** (EN 747 åpner overkøya fra 6 år), "
             f"bygget som én solid av {14} kuler, sylindre og bokser med "
             f"segmentene som brøkdeler av ståhøyden etter **AnthroKids** "
             f"(de digitaliserte Snyder-studiene 1975/1977, "
             f"math.nist.gov/~SRessler/anthrokids/, fri bruk). To ligger i "
             f"sengestilling, to sitter i bordstilling. En kropp er ikke en "
             f"del: den kappes ikke, bærer ingenting, står i ingen liste og "
             f"er tatt ut av alle kontaktsjekker — men den er i parts.tsv og "
             f"i eksportene, og målene under er målt på den.\n\n"
             f"| | Mål |\n|---|---:|\n")
    L.append(f"| **Fri høyde over hodet, sittende** | **{G.SIT_HEADROOM:.0f} "
             f"mm** — kronen står i Z {G.SIT_CROWN_Z:.0f} og "
             f"«{G.SIT_HEAD_OVER}» er det første over. Man sitter helt "
             f"rett opp i sofaen |\n")
    L.append(f"| Sittehøyde | {G.FIG_SITTING_H:.0f} mm (0,545 × H) over "
             f"seteflaten på {G.SEAT_FACE:.0f} mm |\n")
    L.append(f"| **Bordplaten over setet** | **{G.TABLE_OVER_SEAT:.0f} mm**, "
             f"og bare {G.TABLE_UNDER_SEAT:.0f} mm under seg — ett lår er "
             f"{2 * G.FIG_THIGH_R:.0f} mm. **Ingen knær går under denne "
             f"platen.** Den er en lekeflate i fanghøyde mellom to sofahalvdeler, "
             f"og man sitter i skredderstilling ved den |\n")
    L.append(f"| Foldet kne til platekant | {G.LEG_TO_TABLE:.0f} mm |\n")
    L.append(f"| Håndleddet over platen | {G.WRIST_OVER_TABLE:.0f} mm — "
             f"armen rekker fram når overkroppen lener seg |\n")
    L.append(f"| **Fri høyde over ansiktet, nede** | "
             f"**{G.LIE_LOWER_FACE:.0f} mm** til køyespilene |\n")
    L.append(f"| Over den som ligger i køya | ingenting — køya er åpen "
             f"oppover. Rekkverket står {G.GUARD_OVER_BODY:.0f} mm over "
             f"kroppens høyeste punkt og {G.GUARD_OVER_FACE:.0f} mm over "
             f"ansiktet |\n")
    L.append(f"| Madrass igjen bak føttene | "
             f"{G.WALL_SPAN - G.figure_lying_upper.extents[0][1]:.0f} mm av "
             f"{G.WALL_SPAN} — plassen å vokse i |\n\n")

    L.append("## Sikkerhetsmål (EN 747)\n\n| | Mål | Krav |\n|---|---:|---:|\n")
    band = f"≤ 5 eller {G.EN_LIMB_BAND[0]:.0f}–{G.MAX_GUARD_OPENING}"
    L.append(f"| Madrassoverside → nedre rekkverksbånd | "
             f"{G.GUARD_BAND_Z0[0] - G.MATTRESS_Z1} | {band} |\n")
    L.append(f"| Mellom de to rekkverksbåndene | "
             f"{G.GUARD_BAND_Z0[1] - (G.GUARD_BAND_Z0[0] + G.GUARD_W)} | "
             f"{band} |\n")
    L.append(f"| Klatreåpningens bredde | {G.LADDER_CLEAR} | "
             f"{G.MIN_LADDER_CLEAR}–{G.MAX_LADDER_CLEAR} |\n")
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


# ---------------------------------------------------------------------------
# BEFORE STEP 0 - the room
# ---------------------------------------------------------------------------
# The bed is cut to a niche this model draws as three perfect planes. The
# house it is going into is being rebuilt, so those planes are about to be
# rebuilt too - and that makes the order of work a fact about the BUILD, not
# advice. This is that order, and every number in it is read off the model:
# the zones off WALL_ZONES, the niche width off WALL_SPAN, the allowances off
# ROOM_OVER_*. The text lives here, once, and is rendered into both
# byggesteg.md and MONTERING.md the way the numbered steps are.
ROOM_TITLE = "Før steg 0 — mål rommet"


def spikerslag_rows(G, idx):
    """[(nr, "fra–til", vegg, del), ...] - the noggings the wall needs."""
    out = []
    for i, zo in enumerate(G.WALL_ZONES, 1):
        z0, z1 = zo["z"]
        name = idx[zo["labels"][0]][0]
        n = len(zo["labels"])
        out.append((i, f"{_fmt(z0)}–{_fmt(z1)}",
                    "Hjørnene, mot endeveggene" if zo["corner"]
                    else "Bakveggen",
                    f"{name}" + (f" ({n} stk.)" if n > 1 else "")))
    return out


def spikerslag_table(G, idx):
    L = ["| Sone | Fra ferdig gulv | Vegg | Del som skal ha feste |\n",
         "|---:|---|---|---|\n"]
    for nr, z, wall, part in spikerslag_rows(G, idx):
        L.append(f"| {nr} | **{z}** | {wall} | {part} |\n")
    return "".join(L)


def room_first(G):
    """The pre-step, step-shaped: title, intro, do, check."""
    return dict(
        title=ROOM_TITLE,
        intro="Nisja er hverken i vinkel eller i vater, og senga skal stå i "
              "begge deler. **Senga er referansen, ikke rommet — bygg i "
              "vater og lodd, og ta skjevheten i delene som møter vegg og "
              "gulv.**",
        do=[
            "Vent til vegger og gulv er ferdige. **Mens veggen er åpen: legg "
            "spikerslag i sonene under.** Etterpå kommer du ikke til.",
            f"Slå et vannrett høyderiss rundt hele nisja med linjelaser, "
            f"{G.MEASURE_DATUM_Z} mm over ferdig gulv. Alt måles fra risset, "
            "aldri fra gulvet.",
            f"Sett laseren som loddlinje midt i nisja. Mål ut til hver "
            f"endevegg i rutenett: {G.MEASURE_GRID[0]} høyder × "
            f"{G.MEASURE_GRID[1]} dybder på hver vegg. Legg sammen paret i "
            f"hvert punkt. **Minste sum er nisjas minste bredde.**",
            f"Er minste bredde et annet tall enn {G.WALL_SPAN}: sett den inn "
            "som `WALL_SPAN` i `generate_loftbed.py` og kjør `mise run "
            "build`. Kapplista regner seg om.",
            "Gulv: mål ned fra risset i sengas fire hjørner og på midten. "
            "Merk det høyeste punktet på gulvet. Senga bygges ned fra det.",
            "Kapp verksteddelene nå. Romdelene tilpasses på stedet: stolper "
            f"og føtter kappes {G.ROOM_OVER_FLOOR} mm for lange og trimmes i "
            "bunn til rammen står i vater — strek opp med avstandskloss, "
            f"meddrag. Sidevangene kappes {G.ROOM_OVER_WALL} mm for lange i "
            "hver veggende og finkappes etter målt bredde. Ytterste "
            "endespile strekes opp etter veggen med fast avstand, så fugen "
            "blir jevn.",
            "**De fire hjørnestolpene står helt inntil endeveggen — null "
            "klaring.** Derfor strekes veggsiden på hver av dem, hver gang: "
            "sett stolpen på plass, hold den i lodd, og strek opp veggsiden "
            "med avstandskloss der veggen buler. Høvle av til stolpen står i "
            "lodd inntil veggen. Ingen monn i bredden — det er tre som skal "
            "bort, ikke legges til. Buler veggen og du lar det stå, skyver "
            "bulen hele rammen ut av lodd.",
            "Kapp kanter som møter vegg eller gulv med lite bakfall. Da er "
            "det bare den synlige kanten som bestemmer fugen.",
        ],
        check=[
            "Høyderisset skal gå hele veien rundt nisja og møte seg selv. "
            "Gjør det ikke det, står laseren feil.",
            f"Er forskjellen mellom minste og største bredde større enn "
            f"{G.ROOM_OVER_WALL} mm, mål om. Kapp uansett etter den minste.",
            "Sjekk at spikerslagene ligger i sonene før veggen lukkes.",
            "Hver hjørnestolpe skal stå i lodd begge veier. Vipper den "
            "fordi veggen buler, høvles bulen av — lys i fugen der veggen "
            "viker er greit og skal stå.",
        ],
    )


ROOM_ZONE_NOTE = ("Målene er fra **ferdig gulv**. Legges gulvet etterpå, må "
                  "påforingshøyden legges til.")


# THE ASSERT THAT READS THE INK. Every height band printed in the nogging
# table has to be the real Z extent of the part named in the same row - not a
# number that once was.
def assert_spikerslag_ink(G, idx, text):
    seen = 0
    for line in text.split("\n"):
        if not line.startswith("| ") or "**" not in line:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) != 4:
            continue
        m = re.fullmatch(r"\*\*([\d,]+)–([\d,]+)\*\*", c[1])
        if not m:
            continue
        z0, z1 = (float(v.replace(",", ".")) for v in m.groups())
        part = re.sub(r" \(\d+ stk\.\)$", "", c[3])
        hits = [p for p in G.CUT_PARTS
                if idx[p.label][0] == part
                and abs(p.extents[2][0] - z0) < 0.05
                and abs(p.extents[2][1] - z1) < 0.05]
        assert hits, (f"spikerslagsone {c[0]} sier {c[1]} for «{part}», men "
                      "ingen del med det navnet står i den høyden")
        seen += 1
    assert seen == len(G.WALL_ZONES), \
        f"{seen} soner på trykk mot {len(G.WALL_ZONES)} i modellen"


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

    # Før steg 0: rommet. Steg 0 kapper, og halve kapplista kan ikke kappes
    # ferdig før nisja er målt - så dette står foran, ikke i en merknad.
    room = room_first(G)
    L.append(f"## {room['title']}\n\n")
    L.append(room["intro"] + "\n\n")
    L.append("**Slik gjør du:**\n\n")
    for d in room["do"]:
        L.append(f"1. {d}\n")
    L.append("\n**Spikerslag i veggen:**\n\n")
    L.append(spikerslag_table(G, idx) + "\n")
    L.append(ROOM_ZONE_NOTE + "\n\n")
    L.append("Hva som kappes nå og hva som kappes på stedet: "
             "[kapplista](kappliste.md).\n\n")
    L.append("**Sjekk før du går videre:**\n\n")
    for c in room["check"]:
        L.append(f"* {c}\n")
    L.append("\n")

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
    text = "".join(L)
    assert_spikerslag_ink(G, idx, text)
    write(os.path.join(out_dir, "byggesteg.md"), text)


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
    # Denne raden avløste "Les steg 0 først" med bokikonet. Budskapet var det
    # samme - alt kappes og bores før noe reises - men det stod bare i teksten;
    # nå står det i bildet, og paret har fått den IKKE SLIK-en boka aldri hadde.
    ("blyant-foerst", "skrutrekker-foerst-nei",
     "**Blyanten først.** Merk av hvert kapp og hvert hull før du skrur — "
     "all saging og all boring skjer i steg 0, før noe reises."),
    ("verktoy", None,
     "**Verktøy:** drill med bor, torxbits, tommestokk, vater og "
     "vinkelhake."),
    ("forbor", None,
     "**Forbor.** I bordene og i all endeved er forboring et krav."),
    ("veggfeste-ja", "fritt-staaende-nei",
     "**Sengen skal skrus fast i veggen.** Den er ikke beregnet på å stå "
     "fritt — veggen er sperren på baksiden."),
]


# Forsteg-sidens eget SLIK / IKKE SLIK-par, i samme oppsett som «Før du
# begynner». Det er én ting på den siden som ikke lar seg si med tall, og det
# er HVORDAN en strek mot vegg blir til: klossen følger veggen, tommestokken
# gjør det ikke. Bakfallet fra punkt 8 fikk ikke sitt eget par - siden bærer
# allerede lista, målefiguren og spikerslagstabellen, og et par til ville
# skyve tabellen over på neste side for å illustrere en setning som står
# tydelig i lista.
ROOM_PREP = [
    ("meddrag-ja", "punktmaal-nei",
     "**Avstandskloss, ikke tommestokk.** Klossen følger veggen hele veien, "
     "og blyanten mot klossens ytterkant gir emnet veggens form. Ett "
     "punktmål gir en rett strek mot en vegg som ikke er rett."),
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


# Målefiguren på forsteg-siden er tre visninger: nisja som rom til venstre,
# oppriss og plan under hverandre til høyre. Høyden er i piksler som alle
# andre bildehøyder her; build_pdf regner den om til millimeter på papiret.
# 360 px er ca. 95 mm høyt og fyller satsbredden 180 mm - så bredt som siden
# tillater, og det er den bredden figurens egen typestørrelse er regnet for.
# Tallet er ikke fritt: render_maalfigur.assert_fits_column() leser det herfra
# og stopper tegningen hvis figurens egne proporsjoner ikke gir 180 mm ved
# akkurat denne høyden - endrer du komposisjonen der, sier asserten hva tallet
# skal være (se tools/render_maalfigur.py).
ROOM_FIG_PX = 360


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
    # THE FILL CODE. A badge letter carries a fill pattern as well as a
    # letter, and the pattern follows it everywhere the letter goes - so the
    # glyph in a step's own fastener table is the coded one, drawn with the
    # same pattern the drawing above it puts in that screw. Which (fastener,
    # code) pairs exist is decided by the STEPS, because that is where the
    # letters are handed out; a pair no page shows is a file nobody reads.
    #
    # And a page only hands out fills where the SHAPES need them - see
    # step_fill_code(). A step whose screws tell themselves apart draws them
    # bare, and its table draws them bare too: the table is the key to the
    # picture above it, so a coded row over an uncoded screw would be a key to
    # a lock that is not there.
    coded_pairs = set()
    for st in steps:
        if not step_fill_code(st):
            continue
        for name, letter in step_badges(st).items():
            code = gen_glyphs.fill_code(letter)
            if code and code != "open":
                coded_pairs.add((name, code))
    coded = gen_glyphs.emit_coded_glyphs(coded_pairs,
                                         os.path.join(img_dir, "beslag"))
    fill_legend = gen_glyphs.emit_fill_code_legend(
        os.path.join(img_dir, "beslag"))
    # FIGURHODET er REGNET, ikke tegnet. Landemerketabellen i
    # tools/gen_figurhode.py er kilden, og den skriver hodet inn i de fire
    # figurikonene FØR piktogramsiden settes av dem - og den samme tabellen
    # skriver PRAKSIS §4. Ikonfilene er dermed artefakter som resten: en hånd
    # som retter et tall i en av dem blir overskrevet ved neste bygg, og
    # `mise run check` hasher dem.
    import gen_figurhode
    gen_figurhode.regenerate()
    pikto = gen_glyphs.emit_pictograms(os.path.join(img_dir, "ikon"))
    # As many letters as the busiest step needs, and no more.
    widest = max((len(step_badges(st)) for st in steps), default=0)
    merke = gen_glyphs.emit_badges(os.path.join(img_dir, "ikon"), widest)

    def gimg(name, screw_px, cap=None, code=None):
        f = coded.get((name, code), glyph[name])
        h = _glyph_height(os.path.join(img_dir, "beslag", f), screw_px, cap)
        return _img("img/beslag/" + f, h, name)

    # ----- page 1: cover ---------------------------------------------------
    parts_rows = cut_table(G)
    n_parts = sum(r[3] for r in parts_rows)
    # Every numbered page is a step, and step 0 - the cutting, drilling and
    # countersinking that happens before anything is raised - is one of them.
    # The cover counts what the reader will actually turn: 12 steg (0-11), the
    # same count byggerekkefolge.svg prints. Counting only 1..11 said 11 and
    # left the two documents contradicting each other.
    n_steps = len(steps)
    step_lo = min(st["n"] for st in steps)
    step_hi = max(st["n"] for st in steps)
    assert n_steps == step_hi - step_lo + 1, "stegnumrene har hull"
    L = [MONTERING_HEAD,
         "# HANNA\n\n",
         "## Loftseng med sofa, bord og ekstraseng under\n\n",
         "![HANNA](img/hanna-hero.png)\n\n",
         "| Bredde | Dybde | Høyde |\n|---:|---:|---:|\n",
         f"| **{G.WALL_SPAN} mm** | **{G.OVERALL_DEPTH} mm** | "
         f"**{G.POST_HEIGHT} mm** |\n\n",
         f"{n_parts} deler · {n_steps} steg ({step_lo}–{step_hi}) · 2 personer · "
         f"passer standard madrass 80 × 200 cm\n\n",
         "Sengen står inntil bakveggen og inntil begge sidevegger, og skrus "
         "fast i bakveggen. **Bygg bakfra og utover.**\n\n",
         "Ord og begrunnelser: [ASSEMBLY.md](ASSEMBLY.md). "
         "Full steg-for-steg-tekst: [byggesteg](generated/byggesteg.md).\n\n"]

    # ----- page 2: the room ------------------------------------------------
    # Denne siden står før alt annet fordi arbeidet gjør det: nisja må være
    # ferdig og målt før halve kapplista kan kappes. Samme tekst som i
    # byggesteg.md - den står ett sted, i room_first().
    room = room_first(G)
    L.append("---\n\n# Mål rommet først\n\n")
    L.append(room["intro"] + "\n\n")
    for i, d in enumerate(room["do"], 1):
        L.append(f"{i}. {d}\n")
    # Figuren står ETTER lista og før spikerslagstabellen, fordi den er
    # bildet av punkt 2 og 3 og ikke av siden som helhet. Den tegnes av
    # tools/render_maalfigur.py under `mise run montering`, akkurat som
    # stegbildene lenger bak - denne fila skriver bare taggen.
    L.append("\n" + _img("img/maal-rommet.png", ROOM_FIG_PX,
                         f"Nisja som rom, med oppriss og plan ved siden av: "
                         f"høyderisset {G.MEASURE_DATUM_Z} mm over ferdig "
                         f"gulv går som en ring rundt alle tre veggene, "
                         f"loddplanet står midt i nisja, og hver endevegg "
                         f"måles i {G.MEASURE_GRID[0]} høyder × "
                         f"{G.MEASURE_GRID[1]} dybder")
             + "\n\n")
    L.append("\n**Slik strekes en del opp mot vegg og gulv:**\n\n")
    L.append("| Slik | Ikke slik | |\n|:---:|:---:|---|\n")
    for do, dont, line in ROOM_PREP:
        yes = (_img("img/ikon/" + pikto[do], 72, do) + " "
               + _img("img/ikon/" + pikto["hake"], 26, "ja"))
        no = (_img("img/ikon/" + pikto[dont], 72, dont) + " "
              + _img("img/ikon/" + pikto["kryss"], 26, "nei"))
        L.append(f"| {yes} | {no} | {line} |\n")
    L.append("\n**Spikerslag i veggen** — legg dem mens veggen er åpen:\n\n")
    L.append(spikerslag_table(G, idx) + "\n")
    L.append(ROOM_ZONE_NOTE + "\n\n")
    for c in room["check"][:1]:
        L.append(f"⚠️ {c}\n\n")

    # ----- page 3: before you start ---------------------------------------
    L.append("---\n\n# Før du begynner\n\n")
    L.append("**Svart strek** er delen du setter opp nå. "
             "**Grå strek** er det som allerede står.\n\n")
    # The drawings say four things with marks rather than words, and none of
    # them are obvious the first time you meet them. They are explained once,
    # here, and never repeated on a step page.
    L.append("**Festemidlene er tegnet, ikke antydet.** Hver skrue, bolt og "
             "hvert beslag på stegsidene er den samme kroppen som står i "
             "modellen, i sin egen lengde og langs sin egen akse — så en "
             "skrue som peker feil vei eller er for lang stopper byggingen "
             "av manualen, ikke først byggingen av sengen.\n\n")
    L.append("**Trukket ut av hullet:** på de fleste stegene er festemidlene "
             "tegnet et stykke ut langs sin egen akse, med en **prikket "
             "linje** ned i hullet de skal i og en **prikk** der hullet er. "
             "Den prikkede linjen betyr festemiddel og ingenting annet; "
             "**piler** brukes bare om tredeler som skal føres sammen. På de "
             "stegene som setter tjue-tretti like skruer — spilene — er de "
             "tegnet **der de havner** i stedet: hodet fylt, og den delen "
             "som ligger begravd i treet **stiplet**.\n\n")
    L.append("**Bokstaven i ringen** (Ⓐ, Ⓑ …) sier hvilken av stegets typer "
             "et festemiddel er, og går igjen i tabellen under bildet. Den "
             "sitter alltid **på** skruen den gjelder, eller har en tynn "
             "strek bort til den — den peker aldri i løse lufta. Der to "
             "skruer på samme side er nesten like lange, skilles de i tillegg "
             "med **fyll** i silhuetten — den samme bokstaven én gang til, så "
             "du ser hvilken av dem det er uten å lese: åpen, skravert, "
             "krysskravert, heldekt. Ellers står skruene i ren kontur, for da "
             "skiller lengden dem selv. Hele koden står på [beslagsiden]"
             "(#beslag).\n\n")
    L.append("**Antallet står ikke i bildet.** Festemidlene er tegnet ett for "
             "ett, der de går — bare to som havner nøyaktig oppå hverandre på "
             "papiret er tegnet én gang. Hvor mange det er i alt står i ruta i "
             "hjørnet og i tabellen under bildet. **Ruta i hjørnet** viser "
             "leddet i snitt, med "
             "delene i riktig innbyrdes størrelse, skravur på snittflatene og "
             "festemidlene i full lengde — hodet på skrusiden, spissen inne i "
             "mottakerdelen.\n\n")
    L.append("| Slik | Ikke slik | |\n|:---:|:---:|---|\n")
    for do, dont, line in PREP:
        yes = (_img("img/ikon/" + pikto[do], 72, do) + " "
               + _img("img/ikon/" + pikto["hake"], 26, "ja"))
        no = ("" if dont is None else
              _img("img/ikon/" + pikto[dont], 72, dont) + " "
              + _img("img/ikon/" + pikto["kryss"], 26, "nei"))
        L.append(f"| {yes} | {no} | {line} |\n")
    L.append("\n")

    # ----- page 4: hardware -----------------------------------------------
    # The legend first: nothing on this page says what the two numbers in
    # "5×60" are, or what the "100x" counts. One measured exemplar does.
    L.append("---\n\n# Beslag\n\n")
    L.append(_img("img/beslag/" + legend, 104,
                  "5 = tykkelse i mm, 60 = lengde i mm, 100x = antall")
             + "\n\n")
    # And the fill code, in the one place it is worth learning: full size,
    # all four at once. On a step page it is a reminder; here it is the
    # definition.
    L.append(_img("img/beslag/" + fill_legend,
                  int(gen_glyphs.FILL_LEGEND_PX),
                  "Fyllkoden: A åpen, B skravert, C krysskravert, D heldekt")
             + "\n\n")
    L.append("**Fyllkode.** Der to skruer på samme side er nesten like lange, "
             "skilles de med fyll — ellers står festemidlene i ren "
             "kontur.\n\n")
    L.append("| | |\n|:---:|---|\n")
    for name, qty in sorted(total_fast.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {gimg(name, 44)} **{qty}x** | {name} |\n")
    L.append("\nHvor hver enkelt går, og hva som forbores: "
             "[beslagliste](generated/beslagliste.md). Hvilken vei hver "
             "enkelt drives, og hvorfor: "
             "[skrueretninger](generated/skrueretninger.md).\n\n")

    # ----- page 5: parts ---------------------------------------------------
    L.append("---\n\n# Delene\n\n")
    L.append("| Del | Dim. | Lengde | Ant. | Kapp |\n|---|---|---:|---:|---|\n")
    for no_name, section, length, qty, _sp, _en, fit in parts_rows:
        L.append(f"| {no_name} | {section} | {_fmt(length)} | **{qty}** | "
                 + ("på stedet" if fit else "nå") + " |\n")
    L.append(f"\n**{n_parts} deler.** **Ant.** er antallet — det samme tallet "
             "som står som `4×` på stegsidene. **Dim.** og **Lengde** er i "
             "millimeter.\n\n")
    n_room = sum(r[3] for r in parts_rows if r[6])
    L.append(f"**Kapp:** «nå» er delene verkstedet gjør ferdig. «på stedet» "
             f"er de {n_room} delene som møter en endevegg eller gulvet — de "
             "kappes med overmål og finkappes i rommet. Overmålet står i "
             "[kapplista](generated/kappliste.md).\n\n")
    L.append("Posisjoner: [kappliste](generated/kappliste.md). Hva du skal "
             "kjøpe: [innkjøpsliste](generated/innkjopsliste.md).\n\n")

    # ----- the step pages --------------------------------------------------
    order = [j["id"] for j in JOINTS]
    for st in steps:
        L.append("---\n\n")
        L.append(f"# {st['n']}\n\n")
        L.append(f"## {st['title']}\n\n")
        if st.get("image", True):
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
            fills_on = step_fill_code(st)
            L.append("| | | |\n|:---:|:---:|---|\n")
            for name, qty in sorted(fast, key=lambda r: badges[r[0]]):
                code = gen_glyphs.fill_code(badges[name]) if fills_on else None
                L.append(f"| {_img('img/ikon/' + merke[badges[name]], 20, badges[name])}"
                         f" | {gimg(name, gen_glyphs.GLYPH_MIN_PX, cap=72, code=code)} "
                         f"**{qty}x** | {_fast_short(name)} |\n")
            if fills_on:
                L.append("\nBokstavene viser hvor på tegningen hver type går. "
                         "To av dem er nesten like lange, så de bærer fyll "
                         "også — den samme bokstaven om igjen — "
                         "se [fyllkoden på beslagsiden](#beslag).\n\n")
            else:
                L.append("\nBokstavene viser hvor på tegningen hver type "
                         "går.\n\n")
        elif fast:
            L.append("| | |\n|:---:|---|\n")
            for name, qty in fast:
                L.append(f"| {gimg(name, gen_glyphs.GLYPH_MIN_PX, cap=72)} "
                         f"**{qty}x** | "
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


# ---------------------------------------------------------------------------
# WHICH WAY EVERY SCREW GOES - the sheet a human reviews
# ---------------------------------------------------------------------------
# The direction a screw is driven is what the arrows in docs/MONTERING.md
# assert on every page, and it is the one thing in this documentation that
# cannot be read off the model: the geometry says two boxes meet, not which
# side the drill was on. So it is derived where it CAN be derived - a screw
# has to pass through the member it is driven from and stop inside the one it
# grips, and for most of these joints only one direction does that - and it is
# reviewed where it cannot. This page is that review: one line per screw, with
# the basis stated, so a builder can check the drawings against the joint.
BASIS = {
    "utledet": "utledet av tykkelsene",
    "tvetydig": "fastsatt — begge veier holder målene",
    "unntak": "fastsatt",
    "gjelder ikke": "fastsatt",
}

# The drawing's part KINDS in Norwegian live with the joint table in
# generate_loftbed.py, because that is where the joint table now is.
KIND_NO = PART_NO

# The model's own axes, said out loud. X runs along the wall, Y out of it
# towards the room, Z up.
AXIS_NO = {(0, 1): "mot høyre vegg", (0, -1): "mot venstre vegg",
           (1, 1): "utover mot rommet", (1, -1): "innover mot veggen",
           (2, 1): "rett opp", (2, -1): "rett ned"}


def _dir_no(vec):
    """The drive vector as a phrase. Skew screws get both components."""
    parts_ = [(j, v) for j, v in enumerate(vec) if abs(v) > 1e-6]
    parts_.sort(key=lambda jv: -abs(jv[1]))
    words = [AXIS_NO[(j, 1 if v > 0 else -1)] for j, v in parts_]
    if len(words) == 1:
        return words[0]
    ang = math.degrees(math.atan2(abs(parts_[1][1]), abs(parts_[0][1])))
    return f"{words[0]}, {ang:.0f}° skrått {words[1]}"


def emit_skrueretninger(G, out_dir, idx):
    """One line per kind of fastener per joint, printed off the placed solids.

    Nothing here is prose that somebody keeps in step with the drawings: the
    direction is the unit vector the model drove the screw along, and the
    members are the ones it actually passes through. The old «Drives fra»
    sentence in the joint table has become this caption.
    """
    def dims(part):
        return _no_section(G, idx[part.label][1])

    def kind_of(crow, part, pa, pb):
        return crow["a"] if part is pa else crow["b"]

    L = [HEAD, "# Skrueretninger\n\n",
         "Hvilken vei hver skrue drives, og hvorfor akkurat den veien. "
         "Hvert festemiddel i denne sengen er modellert som en kropp med "
         "egen retningsvektor; tabellen under er skrevet ut av de kroppene, "
         "ikke av en setning noen holder ved like. Tegningene i "
         "[MONTERING.md](../MONTERING.md) tegner de samme kroppene.\n\n",
         "**Utledet** betyr at bare én retning er fysisk mulig: skruen må gå "
         "klar gjennom delen den drives fra og ende inne i den andre, altså "
         "`tykkelse(fra) < lengde < tykkelse(fra) + tykkelse(inn i)`. "
         "**Fastsatt** betyr at begge retninger ville holdt målene, eller at "
         "skruen ikke er en rett gjennomskrue i det hele tatt (skråskrue, "
         "gjennomgående bolt, beslagflik) — da er retningen den som står i "
         "leddtabellen, og den er satt for hånd og kontrollert mot "
         "geometrien.\n\n",
         "**Der begge veier holder målene, avgjør fronten.** Sengens front "
         "— alt fra vangenes ytterflate og fram til stolpeplanet — er den "
         "eneste flaten noen ser på, og det skal ikke stå et skruehode i "
         "den. Ledd som griper i en del i det laget skrus derfor innenfra og "
         "ut, og linjene under sier det. Modellen asserter det: ingen "
         "festemiddelhoder på en romvendt flate.\n\n",
         "| Ledd | Festemiddel | Retning | Grunnlag |\n",
         "|---|---|---|---|\n"]

    # One line per KIND of fastener per joint: a joint and its mirror image
    # at the far end of the bed are one line, with a note that the direction
    # turns round with it.
    order = {j["id"]: i for i, j in enumerate(JOINTS)}
    groups, seq = {}, []
    for f in G.FASTENER_SPECS:
        if f["drive"] is None:              # the wall fixing, see the note
            continue
        crow = f["crow"]
        key = (f["jid"], f["name"],
               crow["a"] if f["through"] is f["pa"] or f["into"] is f["pa"]
               else crow["b"], f["kind"], id(f["drive"]))
        if key not in groups:
            groups[key] = []
            seq.append(key)
        groups[key].append(f)
    seq.sort(key=lambda k: (order[k[0]], k[1]))

    n_derived = n_set = 0
    for key in seq:
        fs = groups[key]
        f = fs[0]
        dr = f["drive"]
        mirrored = len({q["direction"] for q in fs}) > 1
        crow, c = f["crow"], f["contact"]
        pa, pb = f["pa"], f["pb"]
        _guess, status = G.derived_entry(c, crow, pa, pb, dr)
        way = _dir_no(f["direction"])
        if f["kind"] == "plate":
            seat = f["through"] or f["into"]
            grips = pb if seat is pa else pa
            host, other = (KIND_NO[kind_of(crow, seat, pa, pb)],
                           KIND_NO[kind_of(crow, grips, pa, pb)])
            if f["through"] is not None:
                what = (f"**{f['name']}** ligger under {host}, bøyer ned "
                        f"forbi kanten og griper om {other}")
            else:
                what = (f"**{f['name']}** ligger på {host} og bøyer om "
                        f"hjørnet til {other}; skruene i fliken går {way}")
        elif f["through"] is None:
            t_no = KIND_NO[kind_of(crow, f["into"], pa, pb)]
            what = (f"**{f['name']}** gjennom beslagfliken og {way} inn i "
                    f"{t_no} ({dims(f['into'])})")
        else:
            e_no = KIND_NO[kind_of(crow, f["through"], pa, pb)]
            t_no = KIND_NO[kind_of(crow, f["into"], pa, pb)]
            what = (f"**{f['name']}** gjennom {e_no} ({dims(f['through'])}) "
                    f"→ inn i {t_no} ({dims(f['into'])}), {way}")
            if dr["counterbore"]:
                _ax = max(range(3), key=lambda j: abs(f["direction"][j]))
                _t = (f["through"].extents[_ax][1]
                      - f["through"].extents[_ax][0])
                _bite = f["length"] - (_t - dr["counterbore"])
                if getattr(f["through"], "tapered", None):
                    # The wedge: one rule, a different depth at every hole.
                    what += (f" — hodet står {_t - dr['counterbore']:g} mm "
                             f"under plata i alle tre hullene, så "
                             f"kontraboret grunner ut mot den skråkappede "
                             f"tuppen (dypest ved roten, null ved tuppen) og "
                             f"skruen tar {_bite:g} mm i {t_no} uansett")
                else:
                    what += (f" — hodet står {dr['counterbore']:g} mm inne i "
                             f"{e_no}, i bunnen av kontraboret, så skruen "
                             f"tar {_bite:g} mm i {t_no} og ingenting går "
                             f"gjennom den andre siden")
            if f.get("seat"):
                what += (f" — skruen står i et flatbunnet sete, "
                         f"⌀{f['seat_d']:g} forstner {f['seat']:g} mm ned "
                         f"langs skruens egen akse (vinkelklossen), så hodet "
                         f"ligger helt under flaten")
        if mirrored:
            what += " (speilvendt i den andre enden)"
        basis = BASIS[status]
        if dr["exempt"]:
            basis += f" — {dr['exempt']}"
        # V5: where the fit rule cannot decide, the visible front does. Read
        # off the same geometry the model asserts on, not off a list of joint
        # ids: the screw runs OUT of the room-front (+Y) into a member that
        # reaches the visible layer, so the other direction would have put
        # its head on a face the room looks at.
        elif (status == "tvetydig" and f["kind"] == "screw"
              and f["through"] is not None and f["direction"][1] > 1e-9
              and f["into"].extents[1][1] >= G.VISIBLE_FRONT_Y - 1e-6):
            basis += (" — skrudd innenfra og ut, så hodet ikke havner på "
                      "den romvendte forflaten")
        if status == "utledet":
            n_derived += 1
        else:
            n_set += 1
        L.append(f"| **{f['jid']}** | {dr['per']}× {f['name']} | {what} | "
                 f"{basis} |\n")

    L.append(f"\n**{n_derived}** av retningene er utledet av målene alene, "
             f"**{n_set}** er fastsatt for hånd. Alle sammen kontrolleres ved "
             f"hver bygging: skruekroppen må ha hodet i plan med flaten den "
             f"drives fra, spissen inne i delen den tar tak i, og ingenting "
             f"av seg selv i noen annen del.\n\n")
    L.append("Veggfestet (J14) står ikke her — det går rett gjennom den bakre "
             "sidevangen og inn i veggen, og har ingen andre del å gå inn "
             "i.\n")
    write(os.path.join(out_dir, "skrueretninger.md"), "".join(L))


def emit_beslagliste(out_dir, steps):
    total = hardware_total(steps)
    L = [HEAD, "# Beslag og festemidler\n\n",
         "Alt er elforsinket eller varmforsinket. Handelsnavn som i norsk "
         "byggevarehandel.\n\n",
         "## Handleliste\n\n",
         "| Post | Behov | Kjøp |\n|---|---:|---|\n"]
    for name, qty in sorted(total.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {name} | {qty} | {_buy_hint(name, qty)} |\n")
    L.append("\n**Behov** er antallet sengen bruker; **Kjøp** er den minste "
             "pakken som finnes i butikk og dekker behovet. Treskruer selges "
             "i pakker à "
             + " / ".join(str(n) for n in SCREW_PACK_SIZES)
             + " stk. Står det samme tall i begge kolonnene, har du ingen "
               "reserve — ta en pakke opp. En skrue du mangler koster en "
               "kveld.\n")
    L.append("\nI tillegg trengs **D3 trelim**, én liten flaske. Den er ikke "
             "en post i tabellen fordi den ikke telles i stykk, men den er "
             "ikke valgfri: J13a og J13b er limte fuger, og skruene der er "
             "tvinger som blir sittende.\n")
    L.append("\n## Hvor det går — ledd for ledd\n\n")
    L.append("| Ledd | Hva | Antall ledd | Per ledd | Forboring | "
             "Drives fra |\n|---|---|---:|---|---|---|\n")
    for j in JOINTS:
        per = " + ".join(f"{q}× {n}" for n, q in j["fast"])
        L.append(f"| **{j['id']}** | {j['title']} | {j['n']} | {per} | "
                 f"{j['drill']} | {j['side']} |\n")
    L.append("\nForklaringen til hvert ledd står i "
             "[ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene).\n")
    # THE LINE THAT USED TO BE OPEN, AND IS NOT ANY MORE. The panel is a
    # drop-in unit and nothing holds it DOWN. Until this round that was the
    # one decision the manual left to the builder, and it sat here - in the
    # shopping list - as three costed options and a TBD. The decision is
    # taken now: NO LOCK, accepted deviation, and the reasoning is in
    # ASSEMBLY vedlegg B. So there is no unbought part left to list, and the
    # beslagliste says so instead of asking.
    L.append("\n## Lås i sengestilling — ingen, og det er et valg\n\n"
             "**Det står ingen lås i denne lista, og det er ikke en glipp.** "
             "Platen løftes rett opp i begge stillinger, og etter denne "
             "runden er det ingen ståldel igjen i platemekanismen i det hele "
             "tatt — verken beslag eller lås.\n\n"
             "Begrunnelsen står i sin helhet i "
             "[ASSEMBLY, vedlegg B, avvik 4](../ASSEMBLY.md#vedlegg-b--aksepterte-avvik). "
             "Kort: madrassen ligger *oppå* platen og må fjernes før platen "
             "kan løftes, dette er underetasjen med ~26 cm fallhøyde, og "
             "plateenheten veier "
             f"{_fmt(round(_MODEL.PANEL_UNIT_MASS, 1))} kg.\n\n"
             "Trevirket for en ettermontert lås står likevel der det sto: "
             "**kilelektas endeved mot enden av den fremre benkevangen**, "
             f"tvers over de {_MODEL.LOCK_GAP} mm i sideklaringen, i samme "
             "høydebånd i sengestilling og 223 mm fra hverandre i "
             "bordstilling. Geometrien er målt og asserted i modellen, så "
             "alle tre løsningene i "
             "[docs/preview/laasvalg.png](../preview/laasvalg.png) kan "
             "monteres senere uten at noe tre må endres. Det arket er "
             "historikk nå, ikke en bestilling.\n")
    write(os.path.join(out_dir, "beslagliste.md"), "".join(L))


def _buy_hint(name, qty):
    if "Låseskrue M8" in name:
        return f"{qty + 5} stk. (bolt, mutter og skive hver for seg)"
    if name.startswith("Treskrue"):
        # Treskruer selges i faste pakker, ikke i «behov + 10». Kjøp nærmeste
        # pakke opp.
        for size in SCREW_PACK_SIZES:
            if size >= qty:
                return f"1 pk. à {size} stk."
        n = -(-qty // SCREW_PACK_SIZES[-1])
        return f"{n} pk. à {SCREW_PACK_SIZES[-1]} stk."
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
    # The drawing flags travel with the step, so tools/render_lineart.py can
    # look up what kind of page this is instead of branching on its number.
    # They are written out even when false: a reader of byggesteg.json should
    # be able to see that a step is NOT a half view without knowing that the
    # key exists on other steps.
    #
    # `fill_code` is in the same list and is written the same way, but it is
    # not declared by hand in build_steps() - it is COMPUTED from the step's
    # own fastener set by step_fill_code(). That is the point: whether a page
    # needs the fill code is a fact about the screws it drives, so nobody has
    # to remember to switch it on the day a joint changes size.
    page_flags = ("half_view", "thumbnails", "crop_to_subject",
                  "no_fasteners", "info_panel", "avoid_top_left")
    data = dict(
        steps=[dict(n=st["n"], title=st["title"], image=st.get("image", True),
                    page=st.get("page", "step"),
                    labels=st["labels"], highlight=st["highlight_labels"],
                    camera=st["camera"], intro=st["intro"], do=st["do"],
                    check=st["check"],
                    fasteners=step_fastener_summary(st),
                    joints=st["joints"],
                    parts=step_part_summary(G, st, idx),
                    fill_code=step_fill_code(st),
                    **{k: bool(st.get(k, False)) for k in page_flags})
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
                + [G.mattress] + list(G.CUSHIONS_BED)}
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
    rows = G.SCREW_ROWS
    steps = resolve_steps(G, build_steps(G))
    idx = cut_index(G)

    emit_kappliste(G, out_dir)
    emit_innkjopsliste(G, out_dir)
    emit_nokkelmal(G, out_dir, rows)
    emit_byggesteg(G, out_dir, steps, idx)
    emit_beslagliste(out_dir, steps)
    emit_skrueretninger(G, out_dir, idx)
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
