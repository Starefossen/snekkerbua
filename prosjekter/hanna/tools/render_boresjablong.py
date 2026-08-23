#!/usr/bin/env python3
"""BORESJABLONGENE, 1:1: docs/schematics/boresjablong-ramme.svg og
docs/schematics/boresjablong-skraaskrue.svg.

To A4-ark som skrives ut i FULL STØRRELSE, klippes fra hverandre og legges på
treet. Byggherren - som har bygget senga - ba om dem: et hull som skal stå
19 mm fra en kant når kravet er 18 er ikke et blyantmål, det er en sjablong.

HVA SOM ER PÅ DEM, OG REGELEN SOM VALGTE DET
--------------------------------------------
Sjablong bare der hullene står i et FAST, TRANGT innbyrdes forhold - to eller
tre hull som må komme ut riktig i forhold til hverandre OG til en kant. Alt
annet måles, og hvorfor det måles står trykt på ark 1:

    ark 1  RAMMELEDDENE   J1 J2 J2-B J3 J7 J8 J17
    ark 2  SKRÅSKRUENE    J8-B og J10 - munningene, som er ellipser og ikke
                          hull, og som er det eneste på hele senga der et
                          blyantkryss ikke sier hva du skal treffe

Ikke ett mål i denne fila er skrevet inn. Hvert hullsenter, hver c/c, hver
forboringsdiameter og hver kant- og endeavstand er lest ut av
generate_loftbed.py - FASTENER_PLACEMENTS for hullene, JOINTS for borene,
TOE_JIG_ELLIPSE for munningene. Det eneste denne fila eier er hvor på papiret
et mønster ligger, og teksten rundt det.

DEN ANDRE ENDEN AV DELEN
------------------------
De fleste av disse delene har hull i BEGGE ender, og den andre enden er et
speilbilde. Det finnes to lovlige svar på det, og «snu arket» er ingen av
dem - da ligger ringene ned mot treet og sylen har ingenting å sikte på:

  * Står hullene like langt fra begge langkanter, er mønsteret snudd 180°
    det samme mønsteret, brettet over den andre langkanten. J2, J3 og J7.
  * Gjør de ikke det, får mønsteret en klippekant til, i den avstanden som
    gir de samme målene lest baklengs. J1, J2-B, J17 og J8-B.

Hvilket av dem hver del får er REGNET UT av hullbildet, ikke bestemt her, og
assert_mirrors() krever at hver del med hull i to ender har fått ett av dem.

HVORFOR ALT STÅR I ÉN SVG
-------------------------
En CSS-boks (div, border, img) snappes til hele devicepiksler når Chrome
skriver PDF - opptil 0,265 mm feil på en kant. Én <svg width="210mm"
height="297mm" viewBox="0 0 210 297"> gjør derimot 1 brukerenhet = 1 mm av
papiret, og geometrien inni den skaleres ikke om: målt på Chromes egen
PDF-strøm står blekket der det skal innenfor 0,002 mm. Derfor er HELE arket -
linjaler, mønstre, tekst - ett eneste SVG-element, og build_pdf legger det
inline på en side med `@page jig { size: A4; margin: 0 }`.

Chrome sin MediaBox er 594,96 x 841,92 pt (209,888 x 297,011 mm): de siste
0,11 mm av bredden klippes bort. Derfor står ingenting forbi x = 209,8, og
den trygge sonen er 10 mm fra alle kanter.

DE TO LINJALENE
---------------
En skriver bommer ikke likt i begge retninger - matretningen er den som
strekker seg. Derfor to kontrollinjaler, en vannrett og en loddrett, og
begge måles med stålmål FØR arket klippes. Den vannrette er den lengste et
A4 kan bære (190 mm = 210 - 2 x 10); den loddrette er 250 mm, som er lang
nok til at 0,4 % matretningsfeil - det dokumenterte verste tilfellet - viser
seg som en hel millimeter.

Bruk:
    python tools/render_boresjablong.py [--out-dir docs/schematics]

Deterministisk: ingen klokke, ingen id(), ingen dict-iterasjon ut i fila.
To kjøringer gir byte-identiske filer, og `mise run check` sier så.
"""

import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "tools"))

from schematic import Sheet, esc, f, nb                  # noqa: E402

OUT_DIR = os.path.join(ROOT, "docs", "schematics")
STEMS = ("boresjablong-ramme", "boresjablong-skraaskrue")
PNG_WIDTH = 1600


# ---------------------------------------------------------------------------
# ARKET
# ---------------------------------------------------------------------------
# A4 nøyaktig, og en trygg sone 10 mm fra alle kanter. Chrome klipper de
# siste 0,11 mm av bredden, så INK_X1 er godt innenfor det.
SHEET_W, SHEET_H = 210.0, 297.0
SAFE = 10.0
INK_X0, INK_X1 = SAFE, SHEET_W - SAFE          # 10 .. 200
INK_Y0, INK_Y1 = SAFE, SHEET_H - SAFE          # 10 .. 287
CHROME_CLIP_X = 209.8                          # ingen blekk forbi denne

# STYLE_K = 0.1 gir familiens typeskala i millimeter: brødtekst 2,2 mm,
# overskrift 2,7, arktittel 5,0. Strektykkelsene under er sjablongens egne -
# de er ikke en tegnings streker, de er et måls streker - og de står i
# extra_css, etter familiens blokk, så de delte navnene beholder sin
# betydning.
STYLE_K = 0.1

W_RULE = 0.30           # linjalens grunnstrek
W_TICK = 0.25           # merkene på den
W_RING = 0.25           # hullringen
W_FOLD = 0.30           # brettelinjen
W_KNIFE = 0.60          # klippekanten
W_EDGE = 0.25           # tegnet delkant som ikke er anlegg

W_ENDMARK = 0.45        # linjalens to ytterste merker, som er de som maales

# Den bredeste HALVE streken paa arket. Sonen er trukket paa senterlinjene -
# linjalens ytterste merke staar paa 190 fordi det er der 190,0 mm er - og
# dette er all slakken assert_ink() gir for at en strek ogsaa har bredde.
PEN = max(W_RULE, W_TICK, W_RING, W_FOLD, W_KNIFE, W_EDGE, W_ENDMARK) / 2.0

# TYPEN, I MILLIMETER AV PAPIR. Ett bord og ikke to: CSS-en under er skrevet
# ut av det, saa en typestoerrelse som endres endres ETT sted. Blokken som
# maaler om en tekst faar plass (`_wrap`, `Ink.text`) leser det samme bordet,
# og det er hele grunnen til at den maalingen kan stemme.
TYPE_MM = {"fig": 2.2, "figb": 2.2, "nm": 2.6, "nm2": 2.1, "body": 2.4,
           "head": 5.0, "sect": 2.9, "note": 2.1}
BOLD = ("figb", "nm", "head", "sect")
HALOED = ("fig", "figb")            # hvite figurer over linjework
HALO = 0.7


def _type_css():
    rows = []
    for cls, mm in TYPE_MM.items():
        rule = f"font-size:{f(mm)}px;"
        if cls in BOLD:
            rule += " font-weight:bold;"
        if cls in HALOED:
            rule += (f" paint-order:stroke; stroke:#fff;"
                     f" stroke-width:{f(HALO)}px;")
        rows.append(f"    .{cls} {{ {rule} }}")
    return "\n".join(rows) + "\n"


EXTRA_CSS = f"""    .rul {{ fill:none; stroke:#000; stroke-width:{f(W_RULE)};
           stroke-linecap:butt; }}
    .tk  {{ fill:none; stroke:#000; stroke-width:{f(W_TICK)};
           stroke-linecap:butt; }}
    .tkb {{ fill:none; stroke:#000; stroke-width:{f(W_ENDMARK)};
           stroke-linecap:butt; }}
    .ring{{ fill:none; stroke:#000; stroke-width:{f(W_RING)}; }}
    .fold{{ fill:none; stroke:#000; stroke-width:{f(W_FOLD)};
           stroke-dasharray:3 2; }}
    .knife{{ fill:none; stroke:#000; stroke-width:{f(W_KNIFE)};
           stroke-linecap:butt; }}
    .edge{{ fill:none; stroke:#000; stroke-width:{f(W_EDGE)}; }}
""" + _type_css()


# ---------------------------------------------------------------------------
# LINJALENE
# ---------------------------------------------------------------------------
# Skriverfeilen er anisotrop: den ene retningen kan treffe og den andre bomme.
# Derfor to linjaler på hvert ark, og godkjenningsgrensen er trykt på arket.
ANISO = 0.004           # dokumentert verste matretningsfeil, 0,4 %
RULER_LIMIT = 1.0       # mm avvik som gjør arket ubrukelig
RULER_H = dict(x=INK_X0, y=283.0, length=190.0, vertical=False)
RULER_V = dict(x=INK_X0, y=15.0, length=250.0, vertical=True)

TICK_MINOR = 3.5
TICK_MAJOR = 6.0
TICK_STEP = 10.0
MAJOR_STEP = 50.0


def draw_ruler(sh, spec, ink):
    """En kontrollinjal, og alt den trenger for å bli målt.

    Returnerer det asserten trenger: senter av FØRSTE og SISTE merke, og
    tallet som ble TRYKT ved enden. Avstanden mellom de to merkesentrene er
    linjalens egentlige lengde på papiret; tallet er det leseren holder
    stålmålet mot. At de to er det samme er en assert og ikke en antakelse.
    """
    x0, y0, L, vert = spec["x"], spec["y"], spec["length"], spec["vertical"]

    def at(v):
        return (x0, y0 + v) if vert else (x0 + v, y0)

    ink.line(at(0.0), at(L), "rul", W_RULE)
    marks = []
    v = 0.0
    while v <= L + 1e-9:
        major = abs(v / MAJOR_STEP - round(v / MAJOR_STEP)) < 1e-9
        end = v < 1e-9 or abs(v - L) < 1e-9
        h = TICK_MAJOR if (major or end) else TICK_MINOR
        cls = "tkb" if end else "tk"
        p = at(v)
        q = (p[0] + h, p[1]) if vert else (p[0], p[1] - h)
        ink.line(p, q, cls, W_ENDMARK if end else W_TICK)
        marks.append(v)
        if major or end:
            lab = nb(v, 0)
            if vert:
                # Tallene står på høykant tett inntil merkene: en loddrett
                # linjal med liggende tall spiser 5 mm av arkets bredde, og
                # den bredden er mønstrenes.
                tp = (x0 + TICK_MAJOR + 3.2, y0 + v)
                ink.rot_text(tp, lab, "fig", -90.0)
            else:
                anchor = ("start" if v < 1e-9 else
                          "end" if end else "middle")
                ink.text((p[0], y0 + 3.2), lab, "fig", anchor)
        v += TICK_STEP
    first, last = at(marks[0]), at(marks[-1])
    return dict(spec=spec, first=first, last=last,
                measured=L, printed=float(nb(marks[-1], 0).replace(",", ".")),
                n_marks=len(marks))


def ruler_note():
    """Setningen som sier hva de to linjalene KAN bevise, regnet ut av
    lengdene deres og den dokumenterte skriverfeilen - ikke skrevet inn."""
    return (f"Den loddrette er {nb(RULER_V['length'], 0)} mm: "
            f"{nb(ANISO * 100, 1)} % matretningsfeil viser seg der som "
            f"{nb(RULER_V['length'] * ANISO, 1)} mm. Den vannrette er "
            f"{nb(RULER_H['length'], 0)} mm — det lengste et A4 kan bære.")


# ---------------------------------------------------------------------------
# BLEKKREGNSKAPET
# ---------------------------------------------------------------------------
class Ink:
    """Tegner på et Sheet OG fører regnskap over hvor blekket havnet.

    Hele poenget med arket er at det er et MÅL, og et mål som er trykt
    utenfor papiret eller inn i skriverens klippsone er ikke et mål. Så hver
    strek, ring og bokstav går gjennom denne, som utvider en boks - med halve
    strektykkelsen på strekene og med typens egen kasse på teksten - og
    asserten leser boksen etterpå.
    """

    def __init__(self, sh):
        self.sh = sh
        self.x0 = self.y0 = 1e9
        self.x1 = self.y1 = -1e9
        self.rings = []          # (x, y, dia) - hvert hullsenter, i arkets mm

    def _box(self, x0, y0, x1, y1):
        self.x0, self.y0 = min(self.x0, x0), min(self.y0, y0)
        self.x1, self.y1 = max(self.x1, x1), max(self.y1, y1)

    def line(self, a, b, cls, w):
        self.sh.line(a, b, cls)
        self._box(min(a[0], b[0]) - w / 2, min(a[1], b[1]) - w / 2,
                  max(a[0], b[0]) + w / 2, max(a[1], b[1]) + w / 2)

    def pline(self, pts, cls, w):
        self.sh.pline(pts, cls)
        self._box(min(p[0] for p in pts) - w / 2,
                  min(p[1] for p in pts) - w / 2,
                  max(p[0] for p in pts) + w / 2,
                  max(p[1] for p in pts) + w / 2)

    def circle(self, c, r, cls, w):
        self.sh.circle(c, r, cls)
        self._box(c[0] - r - w / 2, c[1] - r - w / 2,
                  c[0] + r + w / 2, c[1] + r + w / 2)

    def ellipse(self, c, rx, ry, cls, w):
        self.sh.ellipse(c, rx, ry, cls)
        self._box(c[0] - rx - w / 2, c[1] - ry - w / 2,
                  c[0] + rx + w / 2, c[1] + ry + w / 2)

    def text(self, p, s, cls, anchor="start"):
        self.sh.text(p, s, cls, anchor)
        sz = TYPE_MM[cls]
        w = len(s) * sz * Sheet.CHAR_W
        back = {"start": 0.0, "middle": w / 2.0, "end": w}[anchor]
        self._box(p[0] - back, p[1] - sz * 0.75,
                  p[0] - back + w, p[1] + sz * 0.25)

    def rot_text(self, p, s, cls, deg):
        sz = TYPE_MM[cls]
        self.sh.add(f'<text x="{f(p[0])}" y="{f(p[1])}" class="{cls}" '
                    f'text-anchor="middle" transform="rotate({f(deg)} '
                    f'{f(p[0])} {f(p[1])})">{esc(s)}</text>')
        w = len(s) * sz * Sheet.CHAR_W
        self._box(p[0] - sz * 0.75, p[1] - w / 2,
                  p[0] + sz * 0.25, p[1] + w / 2)

    def lines(self, p, rows, cls, lead=None):
        lead = lead or TYPE_MM[cls] * 1.35
        for i, row in enumerate(rows):
            self.text((p[0], p[1] + i * lead), row, cls)
        return p[1] + len(rows) * lead

    # -- HULLMERKET ---------------------------------------------------------
    # Åpen ring i forboringsdiameteren, ingen blekk i senter, fire korte
    # radielle merker utenfor. Et kryss trekker sylen ut av senter fordi
    # sylen søker en strek; en ring gir den ingen strek å søke og lar den
    # falle ned i midten der den hører hjemme.
    def hole(self, c, dia, label=None):
        r = dia / 2.0
        self.circle(c, r, "ring", W_RING)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            self.line((c[0] + dx * (r + 0.8), c[1] + dy * (r + 0.8)),
                      (c[0] + dx * (r + 2.6), c[1] + dy * (r + 2.6)),
                      "tk", W_TICK)
        self.rings.append((c[0], c[1], dia))
        if label:
            self.text((c[0] + r + 3.2, c[1] - r - 0.9), label, "fig")

    def zigzag(self, a, b, amp=0.8, period=4.0):
        """Familiens bruddstrek: kanten er ikke der, delen fortsetter."""
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        steps = max(2, int(round(n / period)))
        pts = []
        for i in range(steps + 1):
            t = n * i / steps
            s = 0.0 if i in (0, steps) else (amp if i % 2 else -amp)
            pts.append((a[0] + ux * t - uy * s, a[1] + uy * t + ux * s))
        self.pline(pts, "edge", W_EDGE)

    def bbox(self):
        return (self.x0, self.y0, self.x1, self.y1)


# ---------------------------------------------------------------------------
# HVA MODELLEN VET - mønstrene, lest ut av FASTENER_PLACEMENTS
# ---------------------------------------------------------------------------
# Hvor langt inn fra en ende et hull kan stå og fortsatt ha enden sin på
# papiret. Over dette må mønsteret registreres på en oppmerket linje i
# stedet - J3 er den ene: hullene står 808 mm fra enden, og 808 mm papir er
# fire teipede A4.
MAX_END_REG = 100.0

# Rekkefølgen datumene leses i, den samme som festeplasseringstabellen
# bruker: fra veggen ut, fra gulvet opp, fra sideveggen inn.
AXIS_ORDER = {0: ("ytre", "midt", "indre"), 1: ("bak", "midt", "fram"),
              2: ("ned", "midt", "opp")}
END_NO = {(0, "ytre"): "ytterenden", (0, "indre"): "innerenden",
          (1, "bak"): "veggenden", (1, "fram"): "romenden",
          (2, "ned"): "nedre ende", (2, "opp"): "toppen"}
EDGE_NO = {(0, "ytre"): "ytterkanten", (0, "indre"): "innerkanten",
           (1, "bak"): "bakkanten", (1, "fram"): "forkanten",
           (2, "ned"): "underkanten", (2, "opp"): "overkanten"}
# Flatenavnene står KORT på sjablongen - et mønster er 25 mm bredt og en
# bildetekst som ikke får plass er en bildetekst som havner oppå naboen. Hva
# de betyr står én gang, nederst på arket, i FACE_LEGEND.
FACE_NO = {(0, "ytre"): "yttersiden", (0, "indre"): "innersiden",
           (1, "bak"): "baksiden", (1, "fram"): "forsiden",
           (2, "ned"): "undersiden", (2, "opp"): "oversiden"}
FACE_LEGEND = ("Flatene: baksiden = mot veggen · forsiden = mot rommet · "
               "yttersiden = mot nærmeste endevegg · innersiden = mot sengas "
               "midte · over-/undersiden er delen slik den står ferdig.")
OPPOSITE = {"ytre": "indre", "indre": "ytre", "bak": "fram", "fram": "bak",
            "ned": "opp", "opp": "ned"}


def _rows_from(a, target):
    """Hullene på én akse, målt fra ETT navngitt datum.

    Et hull som modellen oppgir fra den andre enden er det samme hullet -
    delens egen bredde snur tallet - og «midt på» er halve bredden. Så mange
    som står i en jevn rekke fra datumet med modellens egen c/c blir med;
    resten hører til den andre enden av delen og har sin egen registrering.
    """
    w, cc = a["width"], a["cc"]
    vals = set()
    for r in a["refs"]:
        for v in r["at"]:
            if r["ref"] == target:
                vals.add(round(v, 6))
            elif r["ref"] == "midt":
                vals.add(round(w / 2.0, 6))
            else:
                vals.add(round(w - v, 6))
    vals = sorted(vals)
    if cc is None:
        return vals[:1]
    keep = [vals[0]]
    for v in vals[1:]:
        if abs(v - keep[-1] - cc) > 0.05:
            break
        keep.append(v)
    return keep


def _datums(a):
    """[(datum, [mm fra det])] - ett innslag per uavhengig anleggskant.

    To datumer som gir SAMME liste er den samme registreringen sett fra hver
    sin side (J17s endelist er 98 mm lang, og de to hullene står 22,5 fra
    hver ende - én rekke, ikke to). To som gir ULIKE lister er to
    registreringer (J7s rekkverksbord: 24 mm inn fra innerenden, 47,5 fra
    ytterenden - samme to hull, to forskjellige anlegg).
    """
    named = {r["ref"] for r in a["refs"]}
    order = [n for n in AXIS_ORDER[a["axis"]] if n in named and n != "midt"]
    if not order:
        # «Midt på» er senterlinjen, og en senterlinje er ikke et anlegg: et
        # ark kan ikke legges mot den. Men et papir brettet over EN av
        # langkantene gir den samme senterlinja så lenge delen er så bred som
        # den skal være - halve bredden - så det er kanten sjablongen legges
        # mot, og halve bredden den måler. Sjablongen sier det høyt i
        # bildeteksten, for det er en annen påstand enn modellens.
        return [(AXIS_ORDER[a["axis"]][0], [a["width"] / 2.0])]
    out = []
    for t in order:
        vals = _rows_from(a, t)
        if not any(vals == v for _t, v in out):
            out.append((t, vals))
    return out


def _pilot(joint):
    """Forboringsdiameteren i den delen merket settes på.

    Leddets egen boreanvisning sier den, og den sier den i den formen som
    betyr «i delen skruehodet står i»: «⌀6 gjennom bjelken». Regexen krever
    nettopp den formen, så en anvisning som blir skrevet om stopper arket i
    stedet for å gi det en diameter fra feil del.
    """
    m = re.match(r"⌀([\d,]+) gjennom ", joint["drill"])
    assert m, (f"{joint['id']}: boreanvisningen «{joint['drill'][:40]}...» "
               f"begynner ikke med «⌀N gjennom ...», og da vet ikke "
               f"sjablongen hvilken diameter ringen skal ha")
    return float(m.group(1).replace(",", "."))


def pattern(G, jid, name=None, member=None, pilot=None):
    """Ett mønster, i delens egne mål og med hver kilde navngitt.

    `pilot` overstyrer boret ringen tegnes i. Bare skråskruesetene bruker
    den: der er «hullet» en ⌀18 forstnerlomme langs en skrå akse, og
    leddets boreanvisning begynner med den og ikke med et gjennomgående
    hull.
    """
    lines = [pl for pl in G.FASTENER_PLACEMENTS
             if pl["jid"] == jid
             and (name is None or name in pl["name"])
             and (member is None or pl["member"] == member)]
    assert len(lines) == 1, (
        f"{jid}: {len(lines)} plasseringslinjer passer - sjablongen må peke "
        f"på nøyaktig én")
    pl = lines[0]
    joint = next(j for j in G.JOINTS if j["id"] == jid)
    spec = next(s for s in G.FASTENER_SPECS
                if s["jid"] == jid and s["name"] == pl["name"])
    end = next(a for a in pl["axes"] if a["role"] == "ende")
    kant = next(a for a in pl["axes"] if a["role"] == "kant")
    # Anleggskanten er den NÆRMESTE - samme regel som festeplasseringen
    # trykker etter, og for J1 er det den som gir 19 mm og ikke 35.
    fold = min(_datums(kant), key=lambda d: (d[1][0], d[0]))
    return dict(
        jid=jid, d=spec["d"], pilot=(_pilot(joint) if pilot is None
                                     else pilot),
        member=G.PART_NO[pl["member"]], section=pl["section"],
        piece_len=pl["piece_len"], face=FACE_NO[pl["face"]],
        # HVOR MANGE ENDER MØNSTERET TJENER. En del med hull i begge ender
        # trenger enten et symmetrisk hullbilde (da kan mønsteret snus 180°
        # og brettes over den andre langkanten) eller en speilvendt
        # klippekant. Regnet ut, ikke husket: antall fester per stykke delt
        # på antall hull ett mønster tegner.
        ends=round((pl["n"] / pl["pieces"])
                   / (len(fold[1]) * len(_datums(end)[0][1]))),
        symmetric=(sorted(fold[1])
                   == sorted(kant["width"] - v for v in fold[1])),
        fold=dict(ref=fold[0], at=fold[1], width=kant["width"],
                  cc=kant["cc"], axis=kant["axis"], raw=kant,
                  name=EDGE_NO[(kant["axis"], fold[0])],
                  into=EDGE_NO[(kant["axis"], OPPOSITE[fold[0]])]),
        cuts=[dict(ref=t, at=v, width=end["width"], cc=end["cc"],
                   axis=end["axis"], raw=end, name=END_NO[(end["axis"], t)])
              for t, v in _datums(end)],
    )


def toe_pattern(G, jid, name, member):
    """Samme, for et skråskruesete: hullet er en ELLIPSE og ikke et hull."""
    p = pattern(G, jid, name, member, pilot=G.TOE_SEAT_D)
    p["mouth"] = G.TOE_JIG_ELLIPSE[jid]
    p["angle"] = G.TOE_JIG_ANGLES[jid]
    p["seat"] = G.TOE_JIG_SEATS[jid]
    p["seat_d"] = G.TOE_SEAT_D
    return p


def rejected(G):
    """De avviste, med tallet som avviste dem lest ut av modellen.

    En sjablong som ikke finnes er en beslutning, og en beslutning uten
    begrunnelse på papiret blir omgjort av neste mann.
    """
    def line(jid):
        return next(pl for pl in G.FASTENER_PLACEMENTS if pl["jid"] == jid)
    j4 = line("J4")
    span = max(a["refs"][0]["at"][-1] - a["refs"][0]["at"][0]
               for a in j4["axes"] if len(a["refs"][0]["at"]) > 1)
    j13 = line("J13a")
    cc13 = next(a["cc"] for a in j13["axes"] if a["cc"] is not None)
    singles = sorted({pl["jid"] for pl in G.FASTENER_PLACEMENTS
                      if all(a["cc"] is None for a in pl["axes"])
                      and pl["jid"] not in ("J4", "J13a")})
    return [
        f"J4 stigevangen: {nb(span, 0)} mm mellom ytterhullene. Målestokk i "
        f"tre, ikke fire teipede A4.",
        f"J13a lektene: jevn c/c {nb(cc13, 0)} mm, toleranse i centimeter. "
        f"Blyant og målebånd.",
        f"Ledd med ett hull i raden ({len(singles)} av dem): ett hull har "
        f"ingen innbyrdes avstand.",
        "J14/J12-V veggfestene: stenderne finnes bare i rommet, og har "
        "ingen X-mål.",
    ]


# ---------------------------------------------------------------------------
# ET MØNSTER PÅ PAPIRET
# ---------------------------------------------------------------------------
FLAP = 9.0              # papir under brettelinjen, som hektes over kanten
FIG_X = 6.8             # kontrollmålet står klar av opp-pila ved klippekanten
TOP_PAD = 3.0           # papir over ytterste hull, før bruddstreken
MIN_CAP_W = 32.0        # smaleste spalte en bildetekst brytes i
SIDE_PAD = 3.0          # papir til høyre for ytterste hull
LABEL_LEAD = 3.0


def _up_arrow(ink, p, ox, oy):
    """«Hvilken vei er opp» - og den er ikke alltid opp: brettelinjen kan
    være en bakkant like gjerne som en underkant, så pila bærer navnet på
    kanten den peker MOT, hentet fra delens egen navngivning.

    Den står INNE på mønsteret, mellom klippekanten og første hull, av to
    grunner: den følger med når mønsteret klippes ut, og den koster ikke
    bredde på et ark der bredden er det knappeste som finnes.
    """
    x = ox + 2.0
    ink.line((x, oy - 2.0), (x, oy - 9.0), "tk", W_TICK)
    ink.pline([(x - 1.2, oy - 6.8), (x, oy - 9.4), (x + 1.2, oy - 6.8)],
              "tk", W_TICK)
    ink.rot_text((x + 2.4, oy - 5.5),
                 f"MOT {p['fold']['into'].upper()}", "fig", -90.0)


def mirror_x(ats):
    """Hvor den SPEILVENDTE klippekanten står, målt fra den første.

    Et hull som står `a` mm inn fra den ene enden av delen står `a` mm inn
    fra den andre også - men fra den andre siden. Legges det en klippekant
    på X = min(a) + max(a), gir den nøyaktig de samme avstandene lest
    baklengs, og ett mønster tjener begge ender uten at noen må snu papiret
    med blekket ned. J17s 22,5 og 75,5 gir X = 98, som er hele delen; J1s
    18 gir 36; J2-Bs 36 og 77 gir 113.
    """
    return min(ats) + max(ats)


def draw_pattern(ink, p, ox, oy, whole=False, align=None, mirror=False):
    """Ett mønster, tegnet med brettelinjen på `oy`.

    x vokser INN i delen fra venstre kant av mønsteret, y oppover fra
    brettelinjen INN i delen, så «opp på delen» ligger opp på papiret.

    Har leddet FLERE anlegg for de samme hullene - J7s rekkverksbord ligger
    24 mm inn fra innerenden og 47,5 fra ytterenden - er det ett mønster med
    to klippekanter, ikke to mønstre: hullene står i samme innbyrdes
    forhold, og det er det sjablongen leverer. Klipp én av dem.

    `mirror` delen har hull i BEGGE ender og hullrekka er ikke symmetrisk om
             delens midtbredde, så den andre enden er et speilbilde. Da får
             mønsteret en klippekant til, på mirror_x() - aldri en beskjed om
             å snu arket, for da vender blekket ned mot treet.
    `whole`  samme sak, men delen er så kort at hele omrisset får plass
             (J17s 98 mm endelist): den fjerne langkanten tegnes også.
    `align`  det finnes ingen ende å legge mot - hullene står 808 mm inne på
             en 1984 mm vange - så mønsteret registreres på en oppmerket
             linje `align` mm inn på papiret (J3).
    """
    fold, cuts = p["fold"], p["cuts"]
    # Den klippekanten som ligger LENGST fra hullene er mønsterets venstre
    # kant; de andre står inne på papiret, like langt fra hullene som
    # modellen sier.
    base = max(cuts, key=lambda c: max(c["at"]))
    # I oppleggsmodus finnes ikke enden på papiret: `align` er hvor langt
    # inn på mønsteret den oppmerkede streken står, og hullene står PÅ den.
    span = align if align is not None else max(base["at"])
    xs = [span] if align is not None else base["at"]
    twin = whole or mirror
    top = oy - (fold["width"] if whole
                else max(fold["at"]) + p["pilot"] / 2.0 + TOP_PAD)
    right = (ox + mirror_x(base["at"]) if twin
             else ox + max(xs) + p["pilot"] / 2.0 + SIDE_PAD)

    # -- anleggene ----------------------------------------------------------
    ink.line((ox - 0.6, oy), (right, oy), "fold", W_FOLD)
    ink.line((ox - 0.6, oy + FLAP), (right, oy + FLAP), "edge", W_EDGE)
    knives = []
    if align is None:
        for c in sorted(cuts, key=lambda c: -max(c["at"])):
            kx = ox + (span - max(c["at"]))
            ink.line((kx, top), (kx, oy + FLAP), "knife", W_KNIFE)
            knives.append(dict(x=kx, sign=1.0, ref=c["ref"], raw=c["raw"]))
            if len(cuts) > 1:
                # Navnet står INNE på mønsteret, til høyre for sin egen
                # kniv: to klippekanter uten navn er to måter å ta feil på.
                ink.rot_text((kx + 1.4, top + 9.0), c["name"].upper(),
                             "fig", -90.0)
        if twin:
            ink.line((right, top), (right, oy + FLAP), "knife", W_KNIFE)
            # Bærer de to endene SAMME navn i modellen - begge er «ytre» på
            # en del som går fra vegg til vegg - er speilkanten det samme
            # datumet lest baklengs. Har de hvert sitt navn, er det det
            # andre navnet.
            other = (OPPOSITE[base["ref"]] if len(base["raw"]["refs"]) > 1
                     else base["ref"])
            knives.append(dict(x=right, sign=-1.0, ref=other,
                               raw=base["raw"]))
            ink.rot_text((right - 1.4, top + 9.0), "ANDRE ENDEN", "fig",
                         -90.0)
    else:
        ink.line((ox + span, top), (ox + span, oy + 1.5), "fold", W_FOLD)
        ink.zigzag((ox, top), (ox, oy + FLAP))
        ink.rot_text((ox + span - 1.4, oy - 8.0), "LEGG PÅ MERKET",
                     "fig", -90.0)
    if whole:
        ink.line((ox, top), (right, top), "edge", W_EDGE)
    else:
        # Kanter som IKKE er anlegg tegnes som bruddstrek: delen fortsetter
        # der, og papiret gjør det ikke.
        ink.zigzag((ox, top), (right, top))
        if not mirror:
            ink.zigzag((right, top), (right, oy + FLAP))

    # -- hullene ------------------------------------------------------------
    holes = []
    for xv in xs:
        for yv in fold["at"]:
            cx, cy = ox + xv, oy - yv
            ink.hole((cx, cy), p["pilot"])
            holes.append((cx, cy))

    # -- KONTROLLMÅLENE: fra hver anleggskant til NÆRMESTE hullsenter, som er
    # det leseren etterprøver med stålmål før han prikker. De står fete, og de
    # står inne på mønsteret, så de følger med når det klippes ut.
    y_near = min(fold["at"])
    ink.text((ox + (FIG_X if align is None else span + 2.0),
              oy - y_near / 2.0 + 0.8), nb(y_near), "figb")
    for k in knives:
        # Ett kontrollmål per klippekant som måles FRAMOVER: J7s to kanter
        # gir 24 og 47,5, og et mønster med to anlegg og ett tall er et
        # mønster som kan brukes feil. Speilkanten gjentar tallet sitt fra
        # den andre siden og får det ikke trykt.
        if k["sign"] < 0:
            continue
        near = min(cx - k["x"] for cx, _cy in holes)
        ink.text((k["x"] + near / 2.0, oy - max(fold["at"]) - 1.6),
                 nb(near), "figb", "middle")
    if fold["cc"] is not None and len(fold["at"]) > 1:
        ink.text((right - 1.6, oy - (fold["at"][0] + fold["at"][1]) / 2.0),
                 f"c/c {nb(fold['cc'])}", "fig", "end")
    if base["cc"] is not None and len(xs) > 1:
        ink.text((ox + (xs[0] + xs[1]) / 2.0, top + 3.0),
                 f"c/c {nb(base['cc'])}", "fig", "middle")

    _up_arrow(ink, p, ox, oy)
    return dict(top=top, right=right, holes=holes, knives=knives,
                fold=fold, fold_y=oy, far_edge=(top if whole else None),
                twin=twin,
                align=None if align is None else (ox + span, base))


def pattern_caption(ink, p, ox, top, width):
    """Navnet over mønsteret - og det står OVER det, inne i det som klippes
    ut, for et mønster uten navn er et papirstykke.

    Bildeteksten brytes til mønsterets egen bredde: et 25 mm bredt mønster
    får tre korte linjer og et 98 mm bredt får to, og ingen av dem havner
    oppå naboen. Hvor bred den ble er det `assert_layout` måler.
    """
    head = f"{p['jid']} · {p['member'].upper()}"
    body = (f"{p['section']} × {nb(p['piece_len'], 0)} · {p['face']} · "
            f"⌀{nb(p['pilot'])}")
    col = max(width, MIN_CAP_W,
              len(head) * TYPE_MM["nm"] * Sheet.CHAR_W)
    rows = _wrap(body, col, TYPE_MM["nm2"])
    y = top - LABEL_LEAD * len(rows) - 2.4
    ink.text((ox, y), head, "nm")
    for i, row in enumerate(rows, 1):
        ink.text((ox, y + i * LABEL_LEAD - 0.2), row, "nm2")
    w = max([len(head) * TYPE_MM["nm"] * Sheet.CHAR_W]
            + [len(r) * TYPE_MM["nm2"] * Sheet.CHAR_W for r in rows])
    return y - TYPE_MM["nm"] * 0.8, ox + w


# ---------------------------------------------------------------------------
# TOPPEN OG BUNNEN - teksten som gjør arket til et mål
# ---------------------------------------------------------------------------
TEXT_X = 23.0                       # innenfor den loddrette linjalens tall
TEXT_W = INK_X1 - TEXT_X            # 177 mm satsbredde


def header(ink, sh, subtitle):
    """Toppen av arket: hva det er, og hva som må stemme før det brukes.

    Ett avsnitt og ikke fire, med vilje: fire avsnitt brytes hver for seg og
    koster fire halvtomme linjer, og linjene her er de mønstrene ikke får.
    """
    ink.text((TEXT_X, 15.5), "1:1 — DETTE ARKET ER ET MÅL", "head")
    ink.text((TEXT_X, 20.0), subtitle, "sect")
    para = (
        "Skriv ut på A4 i 100 % — i Acrobat «Faktisk størrelse»; slå AV "
        "«Tilpass» og «Krymp til utskriftsområde». ENKELTSIDIG: arket skal "
        "klippes opp. "
        f"MÅL BEGGE LINJALENE MED STÅLMÅL FØR DU KLIPPER — en skriver kan "
        f"treffe den ene retningen og bomme den andre. Avvik over "
        f"{nb(RULER_LIMIT)} mm på én av dem: kast arket. " + ruler_note())
    y = 24.8
    for line in _wrap(para, TEXT_W, TYPE_MM["body"]):
        ink.text((TEXT_X, y), line, "body")
        y += 3.2
    return y - 3.2 + TYPE_MM["body"] * 0.25


# Bunnstripa er to spalter, og notatblokken står i det papiret J2-B lar
# være igjen. Alle fire målene er arkets eget oppsett og ingenting annet.
COL_W = 82.0
COL2_X = 109.0
COL2_W = 91.0
FOOT_Y = 252.0
NOTE_X = 140.0
NOTE_Y = 209.0
NOTE_W = 60.0

HOWTO = [
    "1  Klipp langs den TYKKE linjen — kniv mot ståltlinjal, aldri saks.",
    "2  Brett langs den stiplede og hekt brettet over kanten på delen.",
    "3  Legg klippekanten mot delens ende. Teip over hvert hull.",
    "4  Kontrollér det fete kontrollmålet med stålmål før du prikker.",
    "5  Prikk med syl gjennom ringen — ringen sentrerer, et kryss ikke.",
    "6  TA AV PAPIRET, og bor på prikken. Papir under boret river seg.",
]


# Nederste linje blekk et tekstfelt får bruke: én millimeter over toppen av
# den vannrette linjalens merker. Alt under den er linjalens, og en tekst
# som gror ned i en kontrollinjal gjør linjalen uleselig.
TEXT_BOTTOM = RULER_H["y"] - TICK_MAJOR - 1.0


def block(ink, x, y, rows, width, limit, what, heading=None, gap=0.0):
    """Ett tekstfelt, brutt til sin egen spalte og MÅLT mot plassen sin.

    Et ark satt for hånd har ett feilmodus som ingen ser i koden: en setning
    vokser med to ord og skyver seg ned i naboen. Så hvert felt vet hvor det
    slutter, og sier fra i stedet for å skrive over.
    """
    yy = y
    if heading:
        ink.text((x, yy), heading, "sect")
        yy += 3.6
    for row in rows:
        for line in _wrap(row, width, TYPE_MM["note"]):
            ink.text((x, yy), line, "note")
            yy += 2.6
        yy += gap
    assert yy <= limit + 1e-6, (
        f"«{what}» slutter på y={yy:.1f} og har plass til {limit:.1f} - "
        f"teksten har vokst ut av feltet sitt")
    return yy


def howto(ink, y, width, limit):
    return block(ink, TEXT_X, y, HOWTO, width, limit,
                 "SLIK BRUKES ET MØNSTER", "SLIK BRUKES ET MØNSTER")


def why_not(ink, rows, x, y, width, limit):
    return block(ink, x, y, rows, width, limit,
                 "IKKE SJABLONG", "IKKE SJABLONG — OG HVORFOR")


def _wrap(text, width, sz):
    cw = sz * Sheet.CHAR_W
    out, row = [], ""
    for word in text.split():
        cand = (row + " " + word).strip()
        if row and len(cand) * cw > width:
            out.append(row)
            row = word
        else:
            row = cand
    if row:
        out.append(row)
    return out


def footer_source(ink, x, y, stem, width, limit):
    return block(ink, x, y, [
        f"Hvert mål på arket er lest ut av generate_loftbed.py "
        f"(FASTENER_PLACEMENTS). Tegnet av tools/render_boresjablong.py → "
        f"docs/schematics/{stem}.svg — rediger ikke for hånd."],
        width, limit, "kilden")


# ---------------------------------------------------------------------------
# ARK 1 - RAMMELEDDENE
# ---------------------------------------------------------------------------
# (x på klippekanten, y på brettelinjen). Håndsatt, fordi et ark er et ark -
# og kontrollert av assert_layout(), som krever at ingen to mønstre rører
# hverandre og at alt står i den trygge sonen.
SHEET1 = [
    ("J7", 23.0, 123.0, {}),
    ("J2", 79.5, 123.0, {}),
    ("J3", 137.0, 123.0, {"align": 10.0}),
    ("J1", 157.0, 123.0, {"mirror": True}),
    ("J8", 23.0, 196.0, {}),
    ("J17", 80.5, 196.0, {"whole": True}),
    ("J2-B", 23.0, 240.0, {"mirror": True}),
]
def sheet1_note(p):
    """Notatet et mønster trenger, med tallene lest ut av mønsteret selv."""
    jid, fold, cuts = p["jid"], p["fold"], p["cuts"]
    if jid == "J1":
        return (f"J1  {nb(fold['at'][0])} mm fra {fold['name']} mot kravet "
                f"{nb(3 * p['d'], 0)} for en ⌀{nb(p['d'], 0)} skrue. Den "
                f"millimeteren er grunnen til at arket finnes.")
    if jid == "J7":
        a, b = sorted(c["at"][0] for c in cuts)
        return f"J7  To klippekanter, {nb(a)} og {nb(b)} mm fra hullene."
    if jid == "J3":
        return (f"J3  Ingen ende å legge mot: hullene står "
                f"{nb(cuts[0]['at'][0])} mm inne. Riss en vinkelrett strek "
                f"og legg den stiplede linjen på den.")
    return None


def mirror_notes(drawn):
    """De to veiene til den andre enden av en del, sagt én gang hver.

    Hvilke ledd som går hvilken vei er lest ut av mønstrene, ikke skrevet
    inn: flytter et hull seg i modellen så rekka slutter å være symmetrisk,
    flytter leddet seg i denne setningen også - og assert_mirrors krever da
    at det har fått en speilkant.
    """
    sym = [p["jid"] for p, g in drawn if p["ends"] >= 2 and not g["twin"]]
    twin = [p["jid"] for p, g in drawn if g["twin"]]
    out = []
    if sym:
        out.append(
            f"Symmetriske ({', '.join(sym)}): hullene står like langt fra "
            f"begge langkanter — snu mønsteret 180° for den andre enden.")
    if twin:
        out.append(
            f"To klippekanter ({', '.join(twin)}): speilkanten for den "
            f"andre enden er tegnet inn. Klipp ÉN. Snu ALDRI arket — da "
            f"vender ringene ned mot treet.")
    return out


def _ord(n):
    """Tallordet, så overskriften teller mønstrene og ikke husker dem."""
    return ("null", "ett", "to", "tre", "fire", "fem", "seks", "sju",
            "åtte", "ni", "ti")[n]


def build_ramme(G):
    sh = Sheet(SHEET_W, SHEET_H, STYLE_K,
               "Boresjablong 1:1 - rammeleddene", width="210mm",
               extra_css=EXTRA_CSS, height="297mm")
    ink = Ink(sh)
    head_y = header(ink, sh, f"ARK 1 · RAMMELEDDENE — {_ord(len(SHEET1))} "
                            f"mønstre å klippe ut og legge på treet")
    rulers = [draw_ruler(sh, RULER_H, ink), draw_ruler(sh, RULER_V, ink)]

    boxes, drawn = [], []
    for jid, ox, oy, opts in SHEET1:
        p = pattern(G, jid)
        g = draw_pattern(ink, p, ox, oy, **opts)
        cap_top, cap_right = pattern_caption(ink, p, ox, g["top"],
                                             g["right"] - ox)
        # To bokser per mønster, ikke én: bildeteksten står OVER geometrien
        # og kan gjerne skyte ut over en nabo som ennå ikke har begynt
        # der oppe. Geometrien kan ikke det.
        boxes.append((jid + " tekst", ox, cap_top, cap_right, g["top"]))
        boxes.append((jid, ox, g["top"], g["right"], oy + FLAP))
        drawn.append((p, g))

    # Notatene står i papiret J2-B lar være igjen. Tallene i dem er lest ut
    # av mønstrene, ikke skrevet inn - J3s 808 er modellens.
    rows = [n for n in (sheet1_note(p) for p, _g in drawn) if n]
    block(ink, NOTE_X, NOTE_Y, rows + mirror_notes(drawn), NOTE_W,
          FOOT_Y - 2.0, "MERK", "MERK", gap=0.7)

    howto(ink, FOOT_Y, COL_W, TEXT_BOTTOM)
    yy = why_not(ink, rejected(G), COL2_X, FOOT_Y, COL2_W, TEXT_BOTTOM - 8.0)
    footer_source(ink, COL2_X, yy + 1.2, STEMS[0], COL2_W, TEXT_BOTTOM)
    return sh, ink, rulers, drawn, boxes, head_y, FOOT_Y


# ---------------------------------------------------------------------------
# ARK 2 - SKRÅSKRUENE
# ---------------------------------------------------------------------------
def draw_mouth(ink, p, ox, oy, mirror=False):
    """Ett skråskruesete: munningen slik den ser ut på treet, 1:1.

    Et ⌀18 forstnerbor som kommer inn på skrå etterlater ikke et ⌀18 hull.
    Det etterlater en ellipse 18/sin(vinkelen) lang, og ellipsen er det
    eneste som sier hvor mye ved som blir igjen ut mot enden. Storaksen
    peker mot den frie enden, som er den veien skruen heller.

    Delen står i sin fulle bredde her - 68 mm - så begge langkanter er
    tegnet, og `mirror` gir den andre enden sin egen klippekant på samme
    måte som på ark 1.
    """
    fold, cut = p["fold"], p["cuts"][0]
    ml, mw = p["mouth"]
    top = oy - fold["width"]
    right = (ox + mirror_x(cut["at"]) if mirror
             else ox + max(cut["at"]) + ml / 2.0 + SIDE_PAD)

    ink.line((ox - 0.6, oy), (right, oy), "fold", W_FOLD)
    ink.line((ox - 0.6, oy + FLAP), (right, oy + FLAP), "edge", W_EDGE)
    ink.line((ox, top), (ox, oy + FLAP), "knife", W_KNIFE)
    ink.line((ox, top), (right, top), "edge", W_EDGE)
    knives = [dict(x=ox, sign=1.0, ref=cut["ref"], raw=cut["raw"])]
    if mirror:
        ink.line((right, top), (right, oy + FLAP), "knife", W_KNIFE)
        other = (OPPOSITE[cut["ref"]] if len(cut["raw"]["refs"]) > 1
                 else cut["ref"])
        knives.append(dict(x=right, sign=-1.0, ref=other, raw=cut["raw"]))
        ink.rot_text((right - 1.4, top + 9.0), "ANDRE ENDEN", "fig", -90.0)
    else:
        ink.zigzag((right, top), (right, oy))

    holes = []
    for xv in cut["at"]:
        for yv in fold["at"]:
            cx, cy = ox + xv, oy - yv
            ink.ellipse((cx, cy), ml / 2.0, mw / 2.0, "ring", W_RING)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                r = (ml / 2.0 if dx else mw / 2.0)
                ink.line((cx + dx * (r + 0.8), cy + dy * (r + 0.8)),
                         (cx + dx * (r + 2.6), cy + dy * (r + 2.6)),
                         "tk", W_TICK)
            ink.rings.append((cx, cy, p["seat_d"]))
            holes.append((cx, cy))

    y_near = min(fold["at"])
    ink.text((ox + FIG_X, oy - y_near / 2.0 + 0.8), nb(y_near), "figb")
    ink.text((ox + min(cut["at"]) / 2.0, top + 3.4),
             nb(min(cut["at"])), "figb", "middle")
    if fold["cc"] is not None and len(fold["at"]) > 1:
        ink.text((right - 1.6, oy - (fold["at"][0] + fold["at"][1]) / 2.0),
                 f"c/c {nb(fold['cc'])}", "fig", "end")
    ink.text((ox + max(cut["at"]), oy - max(fold["at"]) - mw / 2.0 - 2.4),
             f"{nb(ml)} × {nb(mw)}", "fig", "middle")
    _up_arrow(ink, p, ox, oy)
    return dict(top=top, right=right, holes=holes, fold=fold, fold_y=oy,
                knives=knives, far_edge=top, twin=mirror, align=None)


SHEET2 = [
    ("J8-B", "6×80", "bench_back", 23.0, 118.0, True),
    ("J10", "5×60", "stub", 105.0, 118.0, False),
]
FOOT2_Y = 196.0                 # ark 2 har to mønstre - bunnteksten står høyt


def build_skraaskrue(G):
    sh = Sheet(SHEET_W, SHEET_H, STYLE_K,
               "Boresjablong 1:1 - skraaskruesetene", width="210mm",
               extra_css=EXTRA_CSS, height="297mm")
    ink = Ink(sh)
    head_y = header(ink, sh, "ARK 2 · SKRÅSKRUENE — munningene i full "
                             "størrelse")
    rulers = [draw_ruler(sh, RULER_H, ink), draw_ruler(sh, RULER_V, ink)]

    drawn, boxes = [], []
    for jid, name, member, ox, oy, mirror in SHEET2:
        p = toe_pattern(G, jid, name, member)
        g = draw_mouth(ink, p, ox, oy, mirror=mirror)
        cap, cap_right = pattern_caption(ink, p, ox, g["top"],
                                         g["right"] - ox)
        boxes.append((jid + " tekst", ox, cap, cap_right, g["top"]))
        boxes.append((jid, ox, g["top"], g["right"], oy + FLAP))
        drawn.append((p, g))

    pats = [p for p, _g in drawn]
    y = 136.0
    ink.text((TEXT_X, y), "PAPIRET GIR INNGANGSPUNKTET; VINKELEN GIR "
             "VINKELKLOSSEN.", "sect")
    rows = [
        f"{p['jid']}  {nb(p['angle'], 0)}° · sete ⌀{nb(p['seat_d'], 0)} "
        f"forstner {nb(p['seat'], 0)} mm NED LANGS SKRUENS AKSE — ikke ned i "
        f"treet. Munningen blir da en ellipse {nb(p['mouth'][0])} × "
        f"{nb(p['mouth'][1])} mm, som er {nb(p['seat_d'], 0)}/"
        f"sin({nb(p['angle'], 0)}°) lang, og det er ellipsen du merker opp "
        f"etter." for p in pats]
    rows += [
        "Prikk SENTERET i ellipsen med syl. Det er det punktet "
        "vinkelklossens ⌀18-hull skal stå rett over — papiret gir "
        "inngangspunktet, klossen gir vinkelen, og de to er to forskjellige "
        "verktøy.",
        "Ellipsen selv står der for at du skal se hvor lite ved som blir "
        "igjen ut mot enden: blir munningen på treet KORTERE enn den på "
        "papiret, sto vinkelklossen for bratt og skruen går for flatt.",
        "Klossen, snittet langs skrueaksen og de to dekningsmålene står på "
        "docs/schematics/setedetalj.svg i referanseheftet. Dette arket er "
        "bare inngangspunktet.",
        FACE_LEGEND,
    ]
    block(ink, TEXT_X, y + 3.8, rows, TEXT_W, FOOT2_Y - 3.0,
          "forklaringen på ark 2", gap=1.0)

    howto(ink, FOOT2_Y, COL_W, TEXT_BOTTOM)
    footer_source(ink, COL2_X, FOOT2_Y + 3.6, STEMS[1], COL2_W, TEXT_BOTTOM)
    return sh, ink, rulers, drawn, boxes, head_y, FOOT2_Y


# ---------------------------------------------------------------------------
# ASSERTENE
# ---------------------------------------------------------------------------
def assert_unit(path):
    """1) SVG-enheten. Ett brukerenhet skal være én millimeter av papiret,
    og det er ikke en stilart - det er hele grunnlaget for at arket er et
    mål. Lest ut av den FERDIGE fila."""
    with open(path, encoding="utf-8") as fh:
        head = fh.read(600)
    m = re.search(r'viewBox="([^"]+)"\s+width="([^"]+)"\s+height="([^"]+)"',
                  head)
    assert m, f"{os.path.basename(path)}: fant ingen <svg ...> med viewBox, "\
              f"width og height i den rekkefølgen"
    vb = [float(v) for v in m.group(1).split()]
    assert vb == [0.0, 0.0, SHEET_W, SHEET_H], \
        f"viewBox er {vb}, og da er ikke én enhet én millimeter"
    assert (m.group(2), m.group(3)) == (f"{SHEET_W:g}mm", f"{SHEET_H:g}mm"), \
        (f"arket er {m.group(2)} × {m.group(3)} og ikke "
         f"{SHEET_W:g}mm × {SHEET_H:g}mm")
    return f"{m.group(2)}×{m.group(3)} / viewBox {m.group(1)}"


def assert_rulers(rulers):
    """2) Linjalblekket. Avstanden mellom senter av første og siste merke ER
    linjalens lengde på papiret, og tallet som står trykt ved enden er det
    leseren holder stålmålet mot. At de to er det samme er en assert."""
    out = []
    for r in rulers:
        drawn = math.hypot(r["last"][0] - r["first"][0],
                           r["last"][1] - r["first"][1])
        assert abs(drawn - r["measured"]) < 0.001, (
            f"linjalen er tegnet {drawn:.4f} mm mellom ytterste merkesentre, "
            f"men skulle være {r['measured']:.3f}")
        assert abs(r["printed"] - drawn) < 0.001, (
            f"det står {r['printed']:g} ved enden av en linjal som er "
            f"{drawn:.4f} mm lang")
        out.append((r["spec"]["vertical"], drawn, r["printed"], r["n_marks"]))
    return out


def assert_resolution(rulers):
    """6) Oppløsning. Linjalen skal være lang nok til at den dokumenterte
    matretningsfeilen viser seg som noe et stålmål kan lese.

    Den LODDRETTE bærer kravet: 250 x 0,4 % = 1,0 mm, som er
    godkjenningsgrensen. Den vannrette KAN ikke: et A4 er 210 bredt, og med
    10 mm trygg sone er 190 det lengste som får plass - 190 x 0,4 % = 0,76.
    Så asserten sier begge deler: en av dem oppfyller kravet, og den andre
    er så lang som papiret tillater. Et ark som gjorde den vannrette
    kortere, ville gjort det uten grunn.
    """
    lens = {r["spec"]["vertical"]: r["measured"] for r in rulers}
    assert lens[True] * ANISO >= RULER_LIMIT - 1e-9, (
        f"den loddrette linjalen er {lens[True]:g} mm: {ANISO * 100:g} % av "
        f"den er {lens[True] * ANISO:.2f} mm, og da kan ikke "
        f"{RULER_LIMIT:g} mm være grensen")
    assert abs(lens[False] - (SHEET_W - 2 * SAFE)) < 1e-9, (
        f"den vannrette linjalen er {lens[False]:g} mm, men den trygge sonen "
        f"gir plass til {SHEET_W - 2 * SAFE:g} - kortere uten grunn")
    return lens


def _expect(axis, ref):
    """Modellens egne avstander fra ETT navngitt datum, regnet ut her.

    Egen vei fram til tallet, med vilje: `pattern()` plukker en rekke ut av
    de samme postene og arket tegner den, og en assert som spurte `pattern()`
    igjen ville bare bekreftet seg selv. Denne går rett i placement-postens
    `refs` og `width` og snur hver avstand som er oppgitt fra den andre
    enden.
    """
    w = axis["width"]
    out = set()
    for r in axis["refs"]:
        for v in r["at"]:
            if r["ref"] == ref:
                out.add(round(v, 6))
            elif r["ref"] == "midt":
                out.add(round(w / 2.0, 6))
            else:
                out.add(round(w - v, 6))
    return sorted(out)


def assert_holes(drawn):
    """3) og 4). Hvert tegnet hullsenter mot modellens eget mål, og hver
    tegnet c/c mot modellens.

    Målt på GEOMETRIEN som ble tegnet - senterkoordinatene som havnet i
    fila - mot avstander regnet ut på nytt av `_expect` rett fra
    placement-posten. En skrue som flytter seg 1 mm i modellen felles her.
    """
    n = 0
    for p, g in drawn:
        fold = g["fold"]
        want_edge = _expect(fold["raw"], fold["ref"])
        for cx, cy in g["holes"]:
            de = round(g["fold_y"] - cy, 6)
            assert any(abs(de - w) < 0.01 for w in want_edge), (
                f"{p['jid']}: et hull står {de:g} mm fra brettelinjen "
                f"({fold['name']}), men modellen sier {want_edge}")
            n += 1
        for k in g["knives"]:
            want_end = _expect(k["raw"], k["ref"])
            for cx, _cy in g["holes"]:
                dx = round(k["sign"] * (cx - k["x"]), 6)
                assert any(abs(dx - w) < 0.01 for w in want_end), (
                    f"{p['jid']}: et hull står {dx:g} mm fra klippekanten "
                    f"({k['ref']}), men modellen sier {want_end}")
        if g["align"] is not None:
            ax, base = g["align"]
            want = _expect(base["raw"], base["ref"])
            assert all(abs(cx - ax) < 1e-9 for cx, _cy in g["holes"]), \
                f"{p['jid']}: et hull ligger ikke på oppleggslinjen"
            assert len(want) == 1 and want[0] > MAX_END_REG, (
                f"{p['jid']}: {want} mm fra enden er nær nok til at "
                f"mønsteret skulle hatt en klippekant og ikke en linje")
        # ...og c/c mellom de tegnede hullene, mot modellens egen. Målt på
        # koordinatene, ikke på lista de ble tegnet fra.
        for axis, along in ((fold, 1), (p["cuts"][0], 0)):
            if axis["cc"] is None:
                continue
            vals = sorted({round(h[along], 6) for h in g["holes"]})
            if len(vals) < 2:
                continue
            steps = [round(abs(b - a), 6) for a, b in zip(vals, vals[1:])]
            assert all(abs(s - axis["cc"]) < 0.01 for s in steps), (
                f"{p['jid']}: tegnet c/c {steps} mot modellens "
                f"{axis['cc']:g}")
    return n


def assert_ink(ink, name):
    """5) Alt blekk i den trygge sonen, og ingenting i Chromes klippsone.

    Sonen er trukket på SENTERLINJENE - linjalens ytterste merke står på
    x = 190 fordi det er der 190,0 mm er - og en strek legger halve
    tykkelsen sin på utsiden av sin egen linje. PEN er den bredeste halve
    streken på arket, og det er hele slakken denne asserten gir.
    """
    x0, y0, x1, y1 = ink.bbox()
    assert x0 >= INK_X0 - PEN and x1 <= INK_X1 + PEN, (
        f"{name}: blekket går fra x={x0:.2f} til x={x1:.2f}, utenfor den "
        f"trygge sonen {INK_X0:g}..{INK_X1:g} (+{PEN:g} penn)")
    assert y0 >= INK_Y0 - PEN and y1 <= INK_Y1 + PEN, (
        f"{name}: blekket går fra y={y0:.2f} til y={y1:.2f}, utenfor den "
        f"trygge sonen {INK_Y0:g}..{INK_Y1:g} (+{PEN:g} penn)")
    assert x1 <= CHROME_CLIP_X, (
        f"{name}: blekk på x={x1:.2f} - Chrome klipper alt forbi "
        f"{CHROME_CLIP_X:g} mm")
    return (x0, y0, x1, y1)


def assert_edge_distance(drawn):
    """7) Ingen sjablong tegner et hull EC5 forbyr.

    Kant- og endeavstand minst 3d fra hver TEGNET delkant. Skråskruesetene
    er ikke med: der er hullet en ⌀18 lomme langs en skrå akse, og modellen
    har sine egne regler for den (K4, TOE_SEAT_COVER, setevegg).
    """
    worst = None
    for p, g in drawn:
        if "mouth" in p:
            continue
        need = 3.0 * p["d"]
        # Målt på det som faktisk ER tegnet: brettelinjen, hver klippekant,
        # og - der hele omrisset står - den fjerne langkanten. En kant som
        # ikke er tegnet er ikke et anlegg og har ingenting her å gjøre.
        got = [(min(g["fold_y"] - cy for _cx, cy in g["holes"]),
                "brettelinjen")]
        for k in g["knives"]:
            got.append((min(k["sign"] * (cx - k["x"])
                            for cx, _cy in g["holes"]),
                        f"klippekanten ({k['ref']})"))
        if g["far_edge"] is not None:
            got.append((min(cy - g["far_edge"] for _cx, cy in g["holes"]),
                        "den fjerne langkanten"))
        for mm, what in got:
            assert mm >= need - 1e-6, (
                f"{p['jid']}: sjablongen tegner et hull {mm:g} mm fra "
                f"{what}, og 3d for en ⌀{p['d']:g} skrue er {need:g}")
            r = mm / need
            if worst is None or r < worst[0]:
                worst = (r, p["jid"], mm, need, what)
    return worst


def assert_mirrors(drawn):
    """En del med hull i BEGGE ender må ha en vei til den andre enden.

    To lovlige veier, og bare de to. ENTEN er hullrekka symmetrisk om delens
    midtbredde - da er mønsteret snudd 180° det samme mønsteret, brettet
    over den andre langkanten, og blekket vender fortsatt opp. ELLER har
    mønsteret en speilvendt klippekant til. «Snu arket» er ingen av delene:
    da ligger ringene ned mot treet og sylen har ingenting å sikte på, og
    det er nettopp den beskjeden denne asserten finnes for å hindre.
    """
    out = []
    for p, g in drawn:
        if p["ends"] < 2:
            continue
        assert p["symmetric"] or g["twin"], (
            f"{p['jid']}: hullene står i {p['ends']} ender, rekka er ikke "
            f"symmetrisk om delens {p['fold']['width']:g} mm bredde "
            f"({p['fold']['at']}), og mønsteret har ingen speilvendt "
            f"klippekant - den andre enden kan ikke merkes opp fra dette "
            f"arket")
        out.append((p["jid"], "speilkant" if g["twin"] else "symmetrisk"))
    return out


def assert_layout(boxes, sheet, head_y, foot_y):
    """Ingen to mønstre rører hverandre, ingen står utenfor sonen, og ingen
    er kommet opp i toppteksten eller ned i bunnteksten.

    En sjablong som overlapper en annen kan ikke klippes ut, og det er
    akkurat den slags feil et hånd-satt oppsett gjør når et mønster vokser
    fordi et mål flyttet seg i modellen. Bildeteksten er MED i boksen: den
    hører til mønsteret og klippes ut sammen med det, så den kan like lite
    som hullene ligge oppå naboen.
    """
    for i, (jid, x0, y0, x1, y1) in enumerate(boxes):
        assert INK_X0 <= x0 and x1 <= INK_X1 and INK_Y0 <= y0 <= y1 <= INK_Y1,\
            f"{sheet}: {jid} står på ({x0:.1f},{y0:.1f})-({x1:.1f},{y1:.1f})"
        assert y0 >= head_y, (
            f"{sheet}: {jid} begynner på y={y0:.1f} og toppteksten slutter "
            f"på {head_y:.1f} - bildeteksten ligger i innledningen")
        assert y1 <= foot_y, (
            f"{sheet}: {jid} slutter på y={y1:.1f} og bunnteksten begynner "
            f"på {foot_y:.1f}")
        for jid2, a0, b0, a1, b1 in boxes[i + 1:]:
            if jid2.split()[0] == jid.split()[0]:
                continue        # bildeteksten og sitt eget mønster møtes
            assert x1 <= a0 or a1 <= x0 or y1 <= b0 or b1 <= y0, \
                f"{sheet}: {jid} og {jid2} overlapper hverandre"
    return len(boxes)


# ---------------------------------------------------------------------------
def to_png(svg_path, png_path, width):
    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        print(f"  ! rsvg-convert mangler - {os.path.basename(png_path)} "
              f"ikke skrevet")
        return None
    subprocess.run([rsvg, "-w", str(width), "-b", "white",
                    svg_path, "-o", png_path], check=True)
    return png_path


def render(G, out_dir=OUT_DIR):
    made = []
    for stem, build in zip(STEMS, (build_ramme, build_skraaskrue)):
        sh, ink, rulers, drawn, boxes, head_y, foot_y = build(G)
        svg = os.path.join(out_dir, f"{stem}.svg")
        sh.write(svg)
        unit = assert_unit(svg)
        rul = assert_rulers(rulers)
        assert_resolution(rulers)
        n_holes = assert_holes(drawn)
        box = assert_ink(ink, stem)
        worst = assert_edge_distance(drawn)
        n_box = assert_layout(boxes, stem, head_y, foot_y - 2.0)
        twins = assert_mirrors(drawn)
        png = to_png(svg, os.path.join(out_dir, f"{stem}.png"), PNG_WIDTH)
        made.append(svg)
        if png:
            made.append(png)
        print(f"  {stem}: {len(drawn)} mønstre i {n_box} bokser uten "
              f"overlapp, {n_holes} hull, {unit}")
        print(f"    andre enden: "
              + (" · ".join(f"{j} {how}" for j, how in twins)
                 or "ingen del har hull i to ender"))
        print("    linjaler "
              + " · ".join(f"{d:.3f} mm trykt {pr:g} ({n} merker)"
                           for _v, d, pr, n in rul))
        print(f"    blekk x {box[0]:.2f}..{box[2]:.2f}  y {box[1]:.2f}.."
              f"{box[3]:.2f} (sone {INK_X0:g}..{INK_X1:g} × "
              f"{INK_Y0:g}..{INK_Y1:g})")
        if worst:
            print(f"    trangeste kantavstand {worst[1]}: {worst[2]:g} mm mot "
                  f"kravet {worst[3]:g} ({worst[4]})")
    return made


def main(argv):
    out_dir = OUT_DIR
    if "--out-dir" in argv:
        out_dir = argv[argv.index("--out-dir") + 1]
    import generate_loftbed as G
    made = render(G, out_dir)
    for m in made:
        print(f"wrote {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
