"""Tallene i den håndskrevne prosaen, målt av porten.

Run by `mise run check`. Reads nothing it is allowed to write and writes
nothing at all: it imports the model, captures what the model PRINTS while it
builds, reads the generated fragments, and then holds the two hand-written
documents to what all of that adds up to.

TWO JOBS, ONE IMPORT.

1. THE COUNTED NUMBERS IN README.md. The README's whole claim is that nothing
   in this project is transcribed - and until this file existed, its own
   numbers were. «475 asserter», «136 artefakter», «94 sider», «72 deler»,
   «181 festemidler i 22 ledd»: every one of them was counted once by hand and
   then retold, round after round, by whoever remembered to. A retold number
   is a number that has already started drifting. So each of them is a CLAIM
   here, with the regex that finds it in the README and the measurement that
   settles it, in Norwegian and in English alike. Add an assert and this file
   stops the build until the README says the new total.

   Quotations get a stronger test than equality. Where the README prints a
   line of the model's own output in backticks - `181 festemidler plassert i
   22 ledd` - the claim is not that a number matches: it is that the model
   SAYS THAT. So it is checked as a substring of the captured log, and a
   quotation the model no longer makes fails whether or not its digits are
   right.

2. THE NUMBER SWEEP OVER THE HAND-WRITTEN PROSE. docs/ASSEMBLY.md is the one
   file allowed to be written by a person, and the rule it lives under is that
   it may name parts and cite joints but must never restate a measurement a
   generated fragment already carries. The consistency reviewer checked that
   by hand: every «NNN mm/MPa/kg/kN/%» in the file, against what the model can
   actually produce. This is that sweep, run every build.

   WHAT «CAN PRODUCE» MEANS, and it is deliberately not «any arithmetic on any
   two numbers». That was tried and thrown out: differences between any two
   module globals cover 93 % of every integer up to 2500, and even differences
   between two coordinates on the SAME AXIS take the pool from 17 % of that
   range to 36 %. A pool that can reach any number passes any number. So the
   pool is four kinds of value the model actually HOLDS or SAYS:

     * every scalar at module level, however deep in a list or a dict;
     * every part's box - the two bounds and the span - on all three axes,
       read off the solids;
     * every number the model PRINTS while it builds: the worked utilisations,
       the head rooms, the weights, the spans;
     * every number in the generated fragments, which is the same model
       speaking through the emitters.

   Everything else is either a finding or a whitelist line with the reason
   written beside it, and the whitelist is exact: an entry that stops
   occurring fails too, so it cannot rot in place.

   HOW COARSE IT IS, SAID OUT LOUD. The pool covers about a sixth of the
   millimetre range, and the sweep asserts that too (COVER_MAX), so widening
   it later is a decision and not a drift. But the density is not even: this
   bed has several hundred distinct numbers under 300 mm, so down there the
   net is wide and a wrong small integer will usually pass. Where it bites is
   the decimals, the stresses and the loads - the values nobody can hit by
   accident - and on the numbers a round moved: a paragraph still quoting the
   116 mm wing after it became 77 is exactly the shape of finding this exists
   for.
"""

import ast
import contextlib
import glob
import io
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

README = os.path.join(ROOT, "README.md")
MODEL = os.path.join(ROOT, "generate_loftbed.py")
TOOLS = os.path.join(ROOT, "tools")

# The paths `snap()` in mise.toml hashes, in the same order. The artefact
# count is `git ls-files` over exactly these - see the check task.
SNAP_PATHS = ["docs/generated", "docs/MONTERING.md", "docs/img", "parts.tsv",
              "docs/schematics/setedetalj.svg",
              "docs/schematics/end-elevation.svg",
              "docs/schematics/spikerslag.svg",
              "docs/schematics/boresjablong-*",
              "docs/icons/hanna", "docs/PRAKSIS.md"]


# ---------------------------------------------------------------------------
# MEASURING
# ---------------------------------------------------------------------------
def n_asserts(path):
    """`ast.Assert` nodes - the count the README says is the method."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    return sum(isinstance(n, ast.Assert) for n in ast.walk(tree))


def n_grepped(path):
    """...and the count a grep on «assert» gives, which is the other one."""
    with open(path, encoding="utf-8") as fh:
        return sum(1 for line in fh if line.lstrip().startswith("assert"))


def n_artefacts():
    """The tracked files `mise run check` hashes twice and compares."""
    out = subprocess.run(["git", "ls-files", "-z", "--"] + SNAP_PATHS,
                         cwd=ROOT, capture_output=True, text=True, check=True)
    return len([p for p in out.stdout.split("\0") if p])


# THE TWO PRINTED BOOKLETS. `mise run pdf` writes both, and they are counted
# separately because they are two separately paginated documents: the build
# booklet is what goes to the bench, the reference is what stays on the shelf,
# and a sentence about one of them may not be checked against the other.
#   hefte -> (filnavn, forhandsvisningsmonster)
PDFS = {
    "bygg": ("hanna.pdf", "page-*.png"),
    "ref": ("hanna-referanse.pdf", "ref-*.png"),
}


def n_pages():
    """{hefte: (sider, hvor)} for de trykte heftene, sider=None nar utellelig.

    De to PDF-ene er bevisst utenfor git og `mise run pdf` trenger en headless
    Chrome, sa pa en maskin som aldri har bygget dem er det ingenting a telle.
    Det sies hoyt i stedet for a ga stille: et umalt tall er ikke et sjekket
    tall, og porten skal ikke late som noe annet.
    """
    out = {}
    for book, (name, pattern) in PDFS.items():
        pdf = os.path.join(ROOT, "docs", name)
        pages = None
        where = (f"docs/{name} finnes ikke og docs/preview har ingen "
                 f"{pattern} - kjør `mise run pdf` for å måle sidetallet")
        if os.path.exists(pdf):
            try:
                info = subprocess.run(["pdfinfo", pdf], capture_output=True,
                                      text=True).stdout
                m = re.search(r"^Pages:\s+(\d+)", info, flags=re.M)
                if m:
                    pages, where = int(m.group(1)), f"pdfinfo docs/{name}"
            except FileNotFoundError:
                pass
        if pages is None:
            pngs = glob.glob(os.path.join(ROOT, "docs", "preview", pattern))
            if pngs:
                pages, where = len(pngs), f"docs/preview/{pattern}"
        out[book] = (pages, where)
    return out


# ---------------------------------------------------------------------------
# BORESJABLONGENE, MÅLT PÅ DEN FERDIGE PDF-EN
# ---------------------------------------------------------------------------
# Arkene er 1:1, og et 1:1-ark har to påstander som bare den FERDIGE fila kan
# bekrefte: at siden er hele A4 (Chromes MediaBox, 594,96 × 841,92 pt) og at
# dokumentet ber leseren om «Faktisk størrelse». Begge leses her, av den
# trykte fila, og ingen av dem kan leses av tegneprogrammet.
JIG_MEDIABOX = (594.96, 841.92)     # pt - Chromes A4, malt pa dens egen strom
JIG_MEDIABOX_TOL = 0.2


def jig_pages(pdf, tokens):
    """{merkelapp: sidetall} for sjablongsidene i en ferdig PDF."""
    total = subprocess.run(["pdfinfo", pdf], capture_output=True,
                           text=True).stdout
    m = re.search(r"^Pages:\s+(\d+)", total, flags=re.M)
    if not m:
        return {}
    found = {}
    for page in range(1, int(m.group(1)) + 1):
        text = subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), pdf, "-"],
            capture_output=True, text=True).stdout
        for tok in tokens:
            if tok in text:
                found[tok] = page
    return found


def assert_print_scaling(data, what="byggeheftet"):
    """Dokumentet ber leseren om «Faktisk størrelse».

    Egen funksjon fordi den tar BYTES og ikke en filsti: tools/falsifiser.py
    river nøkkelen ut av en kopi i minnet og krever at denne feller.
    """
    sys.path.insert(0, TOOLS)
    import build_pdf as BP
    assert BP.has_print_scaling(data), (
        f"{what}s katalog mangler /ViewerPreferences /PrintScaling /None - "
        f"da åpner Acrobat sjablongene på «Tilpass til side», og et ark som "
        f"er skalert er ikke et mål")
    return True


def check_jig_pdf():
    """Assert 8: MediaBox-en og /PrintScaling, lest ut av den trykte fila."""
    sys.path.insert(0, TOOLS)
    import build_pdf as BP
    pdf = os.path.join(ROOT, "docs", PDFS["bygg"][0])
    if not os.path.exists(pdf) or not shutil.which("pdfinfo"):
        print(f"  ! boresjablongene ikke målt: {os.path.basename(pdf)} eller "
              f"pdfinfo mangler - kjør `mise run pdf`")
        return None
    with open(pdf, "rb") as fh:
        data = fh.read()
    assert_print_scaling(data)
    tokens = [f"@@jig-{stem}@@" for stem, _label in BP.JIGS]
    found = jig_pages(pdf, tokens)
    missing = [t for t in tokens if t not in found]
    assert not missing, f"fant ikke {missing} i {os.path.basename(pdf)}"
    for tok in tokens:
        page = found[tok]
        info = subprocess.run(["pdfinfo", "-f", str(page), "-l", str(page),
                               pdf], capture_output=True, text=True).stdout
        m = re.search(rf"^Page\s+{page} size:\s+([\d.]+) x ([\d.]+) pts",
                      info, flags=re.M)
        assert m, f"pdfinfo sier ingenting om størrelsen på side {page}"
        got = (float(m.group(1)), float(m.group(2)))
        assert all(abs(a - b) <= JIG_MEDIABOX_TOL
                   for a, b in zip(got, JIG_MEDIABOX)), (
            f"sjablongsiden {page} er {got[0]} × {got[1]} pt, ikke "
            f"{JIG_MEDIABOX[0]} × {JIG_MEDIABOX[1]} - arket er ikke A4 og "
            f"1:1 er ikke 1:1")
    print(f"  boresjablongene: {len(found)} sider på "
          f"{JIG_MEDIABOX[0]:g} × {JIG_MEDIABOX[1]:g} pt, og katalogen ber om "
          f"«Faktisk størrelse» (/PrintScaling /None)")
    return sorted(found.values())


def run_model():
    """Import the model with its output captured. One build, two jobs."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        import generate_loftbed as M            # noqa: E402
    return M, buf.getvalue()


# ---------------------------------------------------------------------------
# THE POOL - WHAT THE MODEL CAN PRODUCE
# ---------------------------------------------------------------------------
NUM_RE = re.compile(r"(?<![\w.,])(\d[\d ]*(?:[.,]\d+)?)(?![\w])")


def _finite(x):
    return isinstance(x, float) and math.isfinite(x) and abs(x) < 1e7


def _scalars(v, depth=0):
    if depth > 3 or isinstance(v, bool):
        return
    if isinstance(v, (int, float)):
        yield float(v)
    elif isinstance(v, (list, tuple, set, frozenset)):
        for x in v:
            yield from _scalars(x, depth + 1)
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from _scalars(k, depth + 1)
            yield from _scalars(x, depth + 1)


def numbers_in(text):
    out = set()
    for m in NUM_RE.finditer(text):
        try:
            out.add(float(m.group(1).replace(" ", "").replace(",", ".")))
        except ValueError:
            pass
    return out


def achievable(M, log):
    """Every value this model can honestly be quoted as saying.

    WHAT IS NOT IN HERE, AND WHY. The obvious fifth source is the difference
    between any two numbers, and it was tried: differences between two
    coordinates on the same axis alone take the pool from 17 % of the
    millimetre range to 36 % of it, and differences between any two globals
    take it to 93 %, at which point every number in the file passes and the
    sweep is a rubber stamp with a docstring. A hand-worked difference is
    therefore a whitelist line with the arithmetic written next to it, not a
    hole the size of the pool.
    """
    pool = set()
    for name, v in vars(M).items():
        if name.startswith("__"):
            continue
        for s in _scalars(v):
            if _finite(s):
                pool.add(round(s, 3))
    solids = (list(M.parts) + [M.panel_bed, M.panel_table, M.mattress]
              + list(M.CUSHIONS_ALL) + list(M.battens_bed)
              + list(M.battens_table) + list(M.FIGURES_ALL))
    for p in solids:
        for j in range(3):
            lo, hi = p.extents[j]
            pool |= {round(lo, 3), round(hi, 3), round(hi - lo, 3)}
    pool |= numbers_in(log)
    for frag in sorted(glob.glob(os.path.join(ROOT, "docs", "generated",
                                              "*.md"))):
        with open(frag, encoding="utf-8") as fh:
            pool |= numbers_in(fh.read())
    with open(os.path.join(ROOT, "docs", "MONTERING.md"), encoding="utf-8") as fh:
        pool |= numbers_in(fh.read())
    return {x for x in pool if _finite(float(x))}


# ---------------------------------------------------------------------------
# THE README'S COUNTED NUMBERS
# ---------------------------------------------------------------------------
def readme_claims(M, log):
    """[(what, regex, [measured, ...]), ...] - one row per counted claim.

    A regex that finds nothing is a failure too: it means the sentence was
    rewritten and the number quietly walked out of range of the check.
    """
    tools = sorted(glob.glob(os.path.join(TOOLS, "*.py")))
    pieces = sum(M.CUT_LIST.values())
    metres = sum(q * ln for (_p, _s, ln), q in M.CUT_LIST.items()) / 1000
    by_sec = {}
    same_cut = {}
    for (_p, sec, ln), q in M.CUT_LIST.items():
        by_sec[sec] = by_sec.get(sec, 0) + q
        same_cut[(sec, ln)] = same_cut.get((sec, ln), 0) + q
    modelled = len([f for f in M.FASTENER_SPECS if not f.get("wall")])
    placed = len(M.FASTENER_SPECS)
    pages = n_pages()
    # The direction sheet counts itself, so they are read back off the sheet
    # rather than recomputed here - the number the reader sees is the number
    # the claim is about.
    with open(os.path.join(ROOT, "docs", "generated", "skrueretninger.md"),
              encoding="utf-8") as fh:
        retn = fh.read()
    rows = [ln for ln in retn.split("\n") if ln.startswith("| **J")]
    n_dirs = len({ln.split("|")[1].strip() + ln.split("|")[2].strip()
                  for ln in rows})
    n_derived = int(re.search(r"\*\*(\d+)\*\* av retningene er utledet",
                              retn).group(1))

    def sec(s):
        return by_sec[s.replace("×", "x")]

    claims = [
        ("asserter",
         r"\*\*(\d+) asserter i modellen\*\* og (\d+) til i verktøyene",
         [n_asserts(MODEL), sum(n_asserts(p) for p in tools)]),
        ("grep-tallet", r"gir (\d+) her", [n_grepped(MODEL)]),
        ("verktøyfiler", r"over `tools/\*\.py` \((\d+) filer\)", [len(tools)]),
        ("artefakter (NO)", r"krever \*\*(\d+) byte-identiske artefakter\*\*",
         [n_artefacts()]),
        ("artefakter, anslag", r"(\d+) er ikke et anslag", [n_artefacts()]),
        ("artefakter, oppgave", r"to fulle kjøringer, (\d+) artefakter",
         [n_artefacts()]),
        ("artefakter (EN)", r"demands (\d+) byte-identical artefacts",
         [n_artefacts()]),
        ("trevirke", r"\*\*(\d+) stykker\*\* i \*\*(\d+) dimensjoner\*\*",
         [pieces, len(M.TIMBER_PROFILES)]),
        ("løpemeter", r"— ([\d,]+) løpemeter", [round(metres, 2)]),
        ("fordeling",
         r"23×98 (\d+) stk\. · 48×68 (\d+) stk\. · 36×48 (\d+) stk\. · "
         r"36×98 (\d+) stk\. · 48×98 (\d+) stk\. · plata (\d+) stk\.",
         [sec("23×98"), sec("48×68"), sec("36×48"), sec("36×98"),
          sec("48×98"),
          sum(q for s, q in by_sec.items() if "panel" in s)]),
        ("den ene lengden",
         r"(\d+) av de (\d+) stykkene er ett og samme stykke: spilen, "
         r"(\d+)×(\d+) × (\d+) mm",
         [max(same_cut.values()), pieces]
         + [int(v) for v in max(same_cut, key=same_cut.get)[0].split("x")]
         + [max(same_cut, key=same_cut.get)[1]]),
        ("stål",
         r"\*\*(\d+) festemidler fordelt på (\d+) ledd\*\*, \*\*(\d+) av dem "
         r"modellert som solide kropper\*\*",
         [placed, len(M.JOINTS), modelled]),
        ("de umodellerte", r"De (\d+) som mangler", [placed - modelled]),
        ("plasseringslinjer",
         r"(\d+) linjer over (\d+) skrueretninger og alle (\d+) festemidlene",
         [len(M.FASTENER_PLACEMENTS), n_dirs, modelled]),
        ("utledede retninger", r"\((\d+) av de (\d+) radene",
         [n_derived, len(rows)]),
        ("nisje og rom",
         r"\*\*Ytre mål\*\* \| (\d+) × (\d+) × (\d+) mm",
         [M.WALL_SPAN, M.OVERALL_DEPTH, M.BUILT_TOP_Z]),
        ("gjennomgående kapp", r"Gjennomgående deler kappes (\d+) mm",
         [M.THROUGH_LEN]),
        ("takhøyde", r"i et rom med (\d+) mm takhøyde", [M.ROOM_H]),
        ("fri høyde", r"gir (\d+) mm fri høyde under køya", [M.SLAT_Z0]),
    ]
    # THE PAGE COUNTS, AND THE ONE HOLE IN THIS FILE. The two PDFs are outside
    # git and `mise run pdf` needs a headless Chrome, so on a machine that has
    # never printed them - CI, for one - there is nothing to count. The
    # sentences are then held to EACH OTHER instead, one group per booklet:
    # they may not be measured, but they may not disagree either, and the
    # print says which of the two happened. Two groups and not one, because
    # two booklets of the same length would otherwise be the only shape the
    # README could not get wrong.
    for what, rx, books in PAGE_CLAIMS:
        claims.append((what, rx,
                       [pages[b][0] if pages[b][0] is not None else f"same:{b}"
                        for b in books]))
    return claims, "; ".join(f"{b}: {w}" for b, (_p, w) in sorted(pages.items()))


# One row per counted page claim: what it is called, the sentence it lives in,
# and WHICH BOOKLET each captured group is about.
PAGE_CLAIMS = [
    ("sider (NO)",
     r"alle (\d+) sidene i byggeheftet og alle (\d+) i referanseheftet",
     ["bygg", "ref"]),
    ("sider, PDF",
     r"et byggehefte på \*\*(\d+) sider\*\* og et referansehefte på \*\*(\d+)\*\*",
     ["bygg", "ref"]),
    ("sider, oppgave",
     r"docs/hanna\.pdf, (\d+) sider \+ docs/hanna-referanse\.pdf, (\d+) sider",
     ["bygg", "ref"]),
    ("sider, kart", r"Byggeheftet på (\d+) sider", ["bygg"]),
    ("sider, kart ref", r"Referanseheftet på (\d+) sider", ["ref"]),
    ("sider, kontaktark", r"De ni første av byggeheftets (\d+) sider",
     ["bygg"]),
    ("sider (EN)",
     r"all (\d+) pages of the printed build booklet and all (\d+) of its",
     ["bygg", "ref"]),
]


# Lines the README prints in backticks BECAUSE the model prints them. The
# claim is not that the digits agree - it is that this is what the build says.
# Compared with runs of whitespace collapsed, because the model's own line is
# laid out in columns and the README quotes it as a sentence.
README_QUOTES = [
    "TOTAL 76 pcs 53.25 m in 5 timber profiles + 1 sheet",
    "185 festemidler plassert i 22 ledd",
    "176 festemidler modellert som kropper",
]


def _flat(s):
    return re.sub(r"\s+", " ", s)


def check_readme(M, log, text=None):
    """`text` overrides the file on disk - that is how tools/falsifiser.py
    hands this check a README with one number perturbed and demands it fall."""
    claims, where = readme_claims(M, log)
    if text is None:
        with open(README, encoding="utf-8") as fh:
            text = fh.read()
    # Matched against the README with its line wrapping flattened away: a
    # claim that happens to straddle a line break is the same claim.
    flat = _flat(text)
    bad, agreed = [], {}
    for what, rx, want in claims:
        m = re.search(rx, flat)
        if m is None:
            bad.append(f"«{what}»: fant ingen setning som matcher {rx!r} - "
                       f"påstanden er skrevet om og har gått ut av syne")
            continue
        got = [g.replace(",", ".") for g in m.groups()]
        for g, w in zip(got, want):
            if isinstance(w, str) and w.startswith("same:"):
                # Unmeasurable here: hold the sentences about THIS booklet to
                # one another.
                w = agreed.setdefault(w, float(g))
            if abs(float(g) - float(w)) > 1e-9:
                bad.append(f"«{what}»: README sier {m.group(0)!r} - målt "
                           f"{w}, ikke {g}")
    flat_log = _flat(log)
    for q in README_QUOTES:
        assert f"`{q}`" in flat, \
            f"README siterer ikke lenger `{q}` - oppdater README_QUOTES"
        if q not in flat_log:
            bad.append(f"README siterer `{q}` som noe modellen skriver ut, "
                       f"og modellen skriver det ikke")
    assert not bad, "README-tallene stemmer ikke med det porten måler:\n  " \
        + "\n  ".join(bad)
    n_quotes = len(README_QUOTES)
    print(f"OK  README-tall: {len(claims)} talte påstander målt på nytt "
          f"({n_quotes} av dem som sitat av modellens egen utskrift), ingen "
          f"gjenfortalt. Sidetallet: {where}")


# ---------------------------------------------------------------------------
# THE SWEEP OVER THE HAND-WRITTEN PROSE
# ---------------------------------------------------------------------------
PROSE_UNITS = r"(?:mm|MPa|kg|kN|%)"
PROSE_RE = re.compile(r"(?<![\w.,])(\d[\d ]*(?:,\d+)?)\s?" + PROSE_UNITS
                      + r"(?![²³\w])")
# HISTORY IS NOT A CLAIM. A number written down because it USED to be true is
# the one number that must NOT be in the model any more, so the sweep has to
# be able to see the difference. Three markers, all of them already in use:
# «(før)» in the row label a table compares against, a parenthesis that opens
# with «var », and the file's own [was ...] bracket.
HIST_PAREN = re.compile(r"\((?:var|was|X\d+:)\b[^)]*\)|\[[^\]]*\]")
HIST_ROW = re.compile(r"\(før\)")

# The numbers that are RIGHTLY not in the model, one line each with the reason.
# Exact: an entry that stops occurring in the file fails, so the list cannot
# quietly outlive what it was excusing.
#
# X13 TOOK TWENTY LINES OUT OF THIS LIST. Every one of them read «håndregnet i
# lastveis-tillegget» or «lagerkapasitet regnet av flate x f_c,90» - vedlegg A
# worked its own arithmetic and the model had no opinion. The model computes
# those rows now (search X13 in generate_loftbed.py), so the sweep is sharp on
# them instead of blind to them: change a stress in the prose and it fails.
#
# AND THREE PRAKSIS LINES WENT WITH THEM, WHICH IS A SMALL LOSS AND IS SAID
# OUT LOUD. «1,56 %», «5,8 %» and «21,6 %» were drawing-room measurements off
# IKEA's sheet, rightly absent from the model - but the pool is unit-blind, and
# X13 put 1,56 (the bare Johansen capacity), 5,8 (a slat deflection) and 21,6
# (f_m,d at k_h 1,3) into it. The whitelist has to be exact, so the lines had
# to go; those three percentages are now covered by numbers that have nothing
# to do with them. If the sweep ever grows units, they come back.
PROSE_ALLOW = {
    "ASSEMBLY.md": {
        # X16 STRØK «52,1 mm». Det var mellomregningen i bordklossens hylledybde
        # (5000 / (2 x 48), rundet opp til 53 i samme setning), og bordklossen
        # finnes ikke lenger - platens forkant står på et trinn. Setningen gikk
        # ut med J5-B-avsnittet, og da må linja her gå ut med den: en hviteliste
        # som overlever det den unnskyldte, skjuler neste feil.
        "2,9 mm": "mellomregning på vinkelklossens såle, ikke et mål på senga",
        "1,8 mm": "differansen mellom to hullkanter, regnet i teksten selv",
        "35,5 mm": "raden på den gamle 116 mm-vingen - samme historiske setning",
        # X14 STRØK TRE OPPFØRINGER, og det er verdt å skrive hvorfor, for to
        # av dem gikk ut ved et sammentreff og ikke fordi noen regnet dem:
        #   «12,7 mm» dekkes nå ekte - FIG_BUTTOCK_SINK er det tallet;
        #   «108 mm» og «116 mm» dekkes av potten uten at senga har noe
        #   108 eller 116 mm i seg: 116 kommer av at kantavstandsrapporten
        #   fikk 116 RADER da J18 la til åtte skruer, og 108 av en skalar
        #   dypt i J5s festeliste. Det er nøyaktig den grovheten sveipet
        #   selv oppgir (potten dekker ~17 % av heltallene opp til 2500), og
        #   regelen om at en hviteliste ikke får overleve det den unnskyldte
        #   er sterkere enn ønsket om å beholde dekningen. Notert her i
        #   stedet for å bli oppdaget på nytt neste runde.
        # X14: begge disse lå i potten ved et sammentreff og mistet dekningen
        # da fotbrettet re-poserte de to sittende figurene. Tallene er de
        # samme; det er potten som flyttet seg, og det er nøyaktig den
        # grovheten sveipet selv sier at den har.
        "175 mm": "øvre rad i madrasstabellens forbudte vindu - håndsatt så "
                  "radene flisleger 126..175 og 180+; modellen regner "
                  "vinduet 110..125 og ikke tabellens rader",
        "584 mm": "spennet vedlegg A regner den fremre benkevangebiten på, "
                  "håndregnet der; sto i potten til X14 fordi en "
                  "referansekropp tilfeldigvis målte 583,8 mm bred",
    },
    # HANNAs egen PRAKSIS måler for det meste PAPIRET og ikke sengen -
    # streker, ikoner, dekningsgrad, kilder. De tallene finnes med rette ikke
    # i modellen, og hver av dem sier her hvilket rom det er målt i.
    "PRAKSIS.md": {
        "888 mm": "dybden senga VILLE fått med veggskruene eksportert - "
                  "regnet nettopp for å forkastes",
        "23,4 mm": "skrueikonets hodediameter på papiret (HEAD_DIA_RATIO), tegnerom",
        "8,6 mm": "skrueikonets kjerne på papiret, tegnerom",
        "35,6 mm": "avstand målt på den ferdige stegsiden, ikke på senga",
        "0,71 mm": "strekbredde målt på IKEAs eget ark, kildemåling",
        "0,22 mm": "strekbredde som ble prøvd og forkastet - gråner i trykk",
        "0,001 mm": "OpenCascades toleranse for en krum kropp, ikke et mål",
        "15,6 %": "dekningsgrad målt på ikonet i 19 mm @ 300 dpi",
        "17,8 %": "dekningsgrad målt på ikonet i 19 mm @ 300 dpi",
        "20,1 %": "dekningsgrad målt på ikonet i 19 mm @ 300 dpi",
        "21,5 %": "dekningsgrad målt på ikonet i 19 mm @ 300 dpi",
        "22,4 %": "figurhøyde i ikonets egne enheter, tegnerom",
        "26,9 %": "hodeandel målt på IKEAs ark, kildemåling",
        "437 mm": "avstand mellom to merkeklynger på den ferdige stegsiden, tegnerom",
    },
}
PROSE_FILES = ["docs/ASSEMBLY.md", "docs/PRAKSIS.md"]
# The sweep polices itself: the pool may not cover more than this much
# of the millimetre range, or a wrong number has nowhere left to fail.
COVER_TOP = 2500
COVER_MAX = 0.30


def check_prose(pool, texts=None):
    """`texts` ({basename: text}) overrides the files on disk - see
    tools/falsifiser.py, which re-introduces a corrected error in memory and
    demands this sweep catch it again."""
    hits, misses, used = 0, [], {k: set() for k in PROSE_ALLOW}
    for rel in PROSE_FILES:
        name = os.path.basename(rel)
        allow = PROSE_ALLOW[name]
        if texts and name in texts:
            text = texts[name]
        else:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                text = fh.read()
        skip = [m.span() for m in HIST_PAREN.finditer(text)]
        rows = {}
        for line in text.split("\n"):
            if HIST_ROW.search(line):
                rows[line] = True
        for m in PROSE_RE.finditer(text):
            if any(a <= m.start() < b for a, b in skip):
                continue
            line = text[text.rfind("\n", 0, m.start()) + 1:
                        text.find("\n", m.start())]
            if line in rows:
                continue
            raw = m.group(1).replace(" ", "")
            v = float(raw.replace(",", "."))
            dp = len(raw.split(",")[1]) if "," in raw else 0
            tol = 0.5 * 10 ** -dp + 1e-9
            if any(abs(v - p) <= tol for p in pool):
                hits += 1
            elif m.group(0) in allow:
                used[name].add(m.group(0))
            else:
                misses.append(f"{name}: «{m.group(0)}» - modellen kan ikke "
                              f"produsere det tallet")
    assert not misses, (
        "TALLSVEIP: håndprosaen oppgir tall modellen ikke har:\n  "
        + "\n  ".join(sorted(set(misses)))
        + "\nEnten er tallet feil, eller så hører det hjemme i PROSE_ALLOW "
          "med en grunn skrevet ved siden av")
    stale = {n: sorted(set(PROSE_ALLOW[n]) - used[n]) for n in PROSE_ALLOW}
    stale = {n: v for n, v in stale.items() if v}
    assert not stale, (
        f"TALLSVEIP: disse står i PROSE_ALLOW og finnes ikke lenger i "
        f"teksten: {stale}. En hviteliste som overlever det den unnskyldte, "
        f"er en hviteliste som skjuler neste feil")
    n_allow = sum(len(v) for v in used.values())
    # HOW MUCH OF A CHECK THIS IS, MEASURED. A pool that can produce every
    # number passes every number, so the sweep prints its own density: how
    # much of the millimetre range a wrong integer could hide in. Kept honest
    # rather than claimed - widen the pool and this number says so.
    dense = len({round(x) for x in pool
                 if abs(x - round(x)) < 1e-6 and 0 < x <= COVER_TOP})
    assert dense <= COVER_MAX * COVER_TOP, (
        f"TALLSVEIP: potten dekker {dense / COVER_TOP:.0%} av heltallene opp "
        f"til {COVER_TOP} - over grensen på {COVER_MAX:.0%}, og et sveip som "
        f"godtar nesten hvilket som helst tall er ikke et sveip")
    print(f"OK  TALLSVEIP: {hits + n_allow} tall med enhet i "
          f"{len(PROSE_FILES)} håndskrevne filer. {hits} av dem er verdier "
          f"modellen faktisk kan produsere; potten er {len(pool)} verdier og "
          f"dekker {dense / COVER_TOP:.0%} av heltallene opp til "
          f"{COVER_TOP}, så et treff er et treff. {n_allow} står i "
          f"hvitelista med grunn; historikk i «(var …)», «[was …]» og "
          f"«(før)»-rader leses ikke")


def main():
    M, log = run_model()
    check_readme(M, log)
    check_prose(achievable(M, log))
    check_jig_pdf()


if __name__ == "__main__":
    main()
