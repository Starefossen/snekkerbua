#!/usr/bin/env python3
"""Bygger den trykkeklare PDF-en av HANNA-manualen.

  mise run pdf

Setter sammen EN print-HTML av
  1. docs/MONTERING.md   - selve manualen: forside, forberedelser, beslag,
                           deler og de nummererte stegsidene med strektegning,
  2. docs/ASSEMBLY.md    - referansedelen med begrunnelser og vedlegg,
  3. docs/generated/*.md - de genererte tabellene,
  4. docs/schematics/*.svg - tegningene,
og skriver den ut til docs/hanna.pdf med headless Chrome.

Ingenting i docs/ endres. Bildene refereres som absolutte file://-URL-er, slik
at Chrome laster dem fra disk uten nettverk.

Sidetallene i innholdsfortegnelsen finnes ved a rendre PDF-en to ganger: forste
runde plasserer usynlige merkelapper, pdftotext forteller hvilken side hver
merkelapp havnet pa, andre runde setter tallet inn.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    import markdown
except ImportError:  # pragma: no cover
    sys.exit(
        "python-markdown mangler. Kjor `mise run install` "
        "(eller `pip install markdown`) og prov igjen."
    )

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PDF_OUT = DOCS / "hanna.pdf"
PREVIEW_DIR = DOCS / "preview"

MD_EXTENSIONS = ["tables", "attr_list", "md_in_html", "sane_lists"]

# Kandidater for utskriftsmotoren, i prioritert rekkefolge. Chrome/Chromium
# printer print-CSS-en var som den er; alt annet er en nodlosning.
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]
CHROME_GLOBS = [
    (Path.home() / "Library/Caches/ms-playwright", "chromium-*/chrome-mac-arm64/*.app/Contents/MacOS/*"),
    (Path.home() / "Library/Caches/ms-playwright", "chromium-*/chrome-mac/*.app/Contents/MacOS/*"),
    (Path.home() / ".cache/puppeteer", "chrome/*/chrome-mac*/*.app/Contents/MacOS/*"),
]

# Interne lenkemal: filnavn (uten mappe og suffiks) -> anker i PDF-en.
ANCHORS = {
    "MONTERING": "montering",
    "ASSEMBLY": "ref-assembly",
    "kappliste": "doc-kappliste",
    "innkjopsliste": "doc-innkjopsliste",
    "nokkelmal": "doc-nokkelmal",
    "beslagliste": "doc-beslagliste",
    "skrueretninger": "doc-skrueretninger",
    "byggesteg": "doc-byggesteg",
    "byggerekkefolge": "sch-byggerekkefolge",
    "end-elevation": "sch-end-elevation",
    "ladder-detail": "sch-ladder-detail",
    "bench-detail": "sch-bench-detail",
    "panel-detail": "sch-panel-detail",
    "setedetalj": "sch-setedetalj",
    "bruk-sengestilling": "sch-bruk-sengestilling",
    "bruk-bordstilling": "sch-bruk-bordstilling",
    "schematics/": "tegninger",
}

PX_TO_MM = 25.4 / 96.0


# --------------------------------------------------------------------------
# markdown -> html
# --------------------------------------------------------------------------

def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html5")


def strip_generated_comment(text: str) -> str:
    return re.sub(r"^\s*<!--.*?-->\s*", "", text, count=1, flags=re.S)


def fix_images(chunk: str, base: Path, scale: float = 1.0) -> str:
    """Absolutte file://-URL-er, og valgfri skalering av ikonhoydene.

    Ikonene i MONTERING.md har hoyden sin i piksler rett i taggen. Vi regner
    den om til mm slik at den betyr det samme pa papir, og ganger med `scale`
    der en side ellers ikke gar opp.
    """

    def repl_src(m: re.Match[str]) -> str:
        src = m.group(1)
        if src.startswith(("http:", "https:", "data:", "file:")):
            return m.group(0)
        path = (base / src).resolve()
        if not path.exists():
            print(f"  ADVARSEL: fant ikke bildet {src} (fra {base})", file=sys.stderr)
        return f'src="{path.as_uri()}"'

    chunk = re.sub(r'src="([^"]+)"', repl_src, chunk)

    def repl_height(m: re.Match[str]) -> str:
        px = int(m.group(1))
        return f'style="height:{px * PX_TO_MM * scale:.2f}mm"'

    return re.sub(r'height="(\d+)"', repl_height, chunk)


def fix_links(chunk: str) -> str:
    """Doc-lenker blir interne PDF-anker; alt er i samme fil na."""

    def repl(m: re.Match[str]) -> str:
        href = m.group(1)
        if href.startswith(("http:", "https:", "#")):
            return m.group(0)
        target = href.split("#", 1)[0]
        key = Path(target).stem if target else ""
        anchor = ANCHORS.get(key) or ANCHORS.get(target)
        if anchor:
            return f'href="#{anchor}" class="xref"'
        return 'class="deadlink" href="#"'

    return re.sub(r'href="([^"]+)"', repl, chunk)


def render(text: str, base: Path, scale: float = 1.0) -> str:
    return fix_links(fix_images(md_to_html(text), base, scale))


def svg_aspect(path: Path) -> float:
    m = re.search(r'viewBox="\s*([-\d.]+)[\s,]+([-\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)',
                  path.read_text(encoding="utf-8")[:2000])
    if not m:
        return 1.0
    return float(m.group(3)) / float(m.group(4))


# --------------------------------------------------------------------------
# Sidemerker for innholdsfortegnelsen
# --------------------------------------------------------------------------

class PageMarks:
    """Usynlige merkelapper som pdftotext kan finne igjen i den ferdige PDF-en."""

    def __init__(self) -> None:
        self.tokens: list[str] = []

    def mark(self, key: str) -> str:
        token = f"@@{key}@@"
        self.tokens.append(token)
        return f'<span class="pagemark">{token}</span>'

    def slot(self, key: str) -> str:
        return f'<span class="pnum" data-key="{key}">&#160;</span>'


# --------------------------------------------------------------------------
# MONTERING.md -> sidene i manualen
# --------------------------------------------------------------------------

def split_sections(text: str) -> list[str]:
    return [c.strip() for c in re.split(r"^---\s*$", text, flags=re.M) if c.strip()]


def split_blocks(text: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


def build_manual(marks: PageMarks) -> tuple[list[str], list[tuple[str, str]]]:
    """Returnerer (sider, innholdsfortegnelse) for bildemanualen."""
    src = strip_generated_comment((DOCS / "MONTERING.md").read_text(encoding="utf-8"))
    pages: list[str] = []
    toc: list[tuple[str, str]] = []

    for section in split_sections(src):
        lines = section.split("\n")
        head = lines[0].strip()

        if head == "# HANNA":
            pages.append(cover_page(section, marks))
        elif head == "# Før du begynner":
            key = "prep"
            toc.append((key, "Før du begynner"))
            pages.append(simple_page(section, marks, key, css="prep"))
        elif head == "# Beslag":
            key = "beslag"
            toc.append((key, "Beslag"))
            # Den smale notasjonsforklaringen over tabellen koster ca. 20 mm,
            # og 14 rader beslag fyller allerede siden. Glyfene tas derfor ned
            # fra 0,78 til 0,70 - hele oversikten skal sta pa EN side.
            pages.append(simple_page(section, marks, key, css="beslag", scale=0.70))
        elif head == "# Delene":
            key = "delene"
            toc.append((key, "Delene"))
            pages.append(simple_page(section, marks, key, css="delene"))
        elif re.fullmatch(r"# \d+", head):
            num = head[2:]
            # Tittelen er den forste ##-linja i bolken; mellom den og
            # nummeret star det en blank linje.
            t_idx = next(i for i, l in enumerate(lines) if l.startswith("## "))
            title = lines[t_idx][3:].strip()
            key = f"steg-{num}"
            toc.append((key, f"Steg {num} — {title}"))
            pages.append(step_page(num, title, "\n".join(lines[t_idx + 1:]), marks, key))
        # Den siste bolken i MONTERING.md er en merknad om git og
        # `mise run montering`. Den horer ikke hjemme i en trykt manual.

    return pages, toc


def cover_page(section: str, marks: PageMarks) -> str:
    blocks = split_blocks(section)
    title = sub = hero = dims = ""
    rest: list[str] = []
    for b in blocks:
        if b.startswith("# "):
            title = b[2:].strip()
        elif b.startswith("## "):
            sub = b[3:].strip()
        elif b.startswith("!["):
            hero = render(b, DOCS)
        elif b.startswith("|"):
            dims = render(b, DOCS)
        else:
            rest.append(b)
    body = render("\n\n".join(rest), DOCS)
    return f"""<section class="page cover" id="montering">
  {marks.mark('forside')}
  <div class="cover-top">
    <h1>{html.escape(title)}</h1>
    <p class="cover-sub">{html.escape(sub)}</p>
  </div>
  <div class="cover-hero">{hero}</div>
  <div class="cover-dims">{dims}</div>
  <div class="cover-note">{body}</div>
</section>"""


def toc_page(marks: PageMarks, manual_toc, ref_toc) -> str:
    def rows(items) -> str:
        out = []
        for key, label in items:
            out.append(
                f'<li><span class="toc-label">{html.escape(label)}</span>'
                f'<span class="toc-dots"></span>{marks.slot(key)}</li>'
            )
        return "\n".join(out)

    return f"""<section class="page toc">
  <h1>Innhold</h1>
  <div class="toc-cols">
    <div>
      <h2>Monter sengen</h2>
      <ol class="toc-list">{rows(manual_toc)}</ol>
    </div>
    <div>
      <h2>Referanse</h2>
      <ol class="toc-list">{rows(ref_toc)}</ol>
    </div>
  </div>
  <p class="toc-foot">Bildedelen er nok til å bygge sengen. Referansedelen
  forklarer hvorfor, og eier alle tallene.</p>
</section>"""


def simple_page(section: str, marks: PageMarks, key: str, css: str, scale: float = 1.0) -> str:
    body = render(strip_first_heading(section), DOCS, scale)
    title = section.split("\n", 1)[0].lstrip("# ").strip()
    return f"""<section class="page {css}" id="{key}">
  {marks.mark(key)}
  <h1>{html.escape(title)}</h1>
  <div class="body">{body}</div>
</section>"""


def strip_first_heading(section: str) -> str:
    return section.split("\n", 1)[1] if "\n" in section else ""


def _png_shape(src: str) -> tuple[int, int] | None:
    """(bredde, hoyde) fra PNG-headeren, eller None.

    `src` er allerede gjort om til en file://-URL av fix_images().
    """
    path = Path(unquote(urlparse(src).path)) if src.startswith("file:") \
        else DOCS / src
    try:
        with open(path, "rb") as fh:
            head = fh.read(24)
    except OSError:
        return None
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return (int.from_bytes(head[16:20], "big"),
            int.from_bytes(head[20:24], "big"))


def step_page(num: str, title: str, rest: str, marks: PageMarks, key: str) -> str:
    figure = ""
    tables: list[str] = []
    notes: list[str] = []
    for b in split_blocks(rest):
        if b.startswith("!["):
            figure = render(b, DOCS)
        elif b.startswith("|"):
            tables.append(render(b, DOCS))
        elif b.startswith("⚠"):
            notes.append(f'<p class="warn">{render(b, DOCS)[3:-4]}</p>')
        else:
            notes.append(render(b, DOCS))

    fig_html = f'<figure class="step-figure">{figure}</figure>' if figure else ""
    tab_html = f'<div class="step-tables">{"".join(tables)}</div>' if tables else ""
    # Stegtegningene er liggende - unntatt kappesiden, som er 14 bord stablet
    # oppa hverandre og star pa hoykant. Med den liggende hoydegrensen ville
    # den krympet til en tredjedels sidebredde, sa formatet leses av bildet
    # selv i stedet for a antas.
    shape = _png_shape(re.search(r'src="([^"]+)"', figure).group(1)) if figure \
        else None
    kind = " tall" if shape and shape[1] > shape[0] else ""
    # Kappesiden er ikke et bilde av sengen, men en kappeplan over 14 bord i
    # full lengde. Den vil ha bredden, og far derfor en liggende A4 for seg.
    if num == "0":
        kind += " cut"
    return f"""<section class="page step{kind}" id="{key}">
  {marks.mark(key)}
  <header class="step-head">
    <span class="step-num">{html.escape(num)}</span>
    <h1>{html.escape(title)}</h1>
  </header>
  {fig_html}
  {tab_html}
  <div class="step-notes">{"".join(notes)}</div>
</section>"""


# --------------------------------------------------------------------------
# Referansedelen
# --------------------------------------------------------------------------

REF_DOCS = [
    ("kappliste", "Kappliste"),
    ("innkjopsliste", "Innkjøpsliste"),
    ("nokkelmal", "Nøkkelmål"),
    ("beslagliste", "Beslagliste"),
    ("skrueretninger", "Skrueretninger"),
    ("byggesteg", "Byggesteg i ord"),
]

SCHEMATICS = [
    ("byggerekkefolge", "Byggerekkefølgen"),
    ("end-elevation", "Kortside, snitt A–A"),
    ("ladder-detail", "Stigen"),
    ("bench-detail", "Benken"),
    ("panel-detail", "Den løse platen"),
    ("setedetalj", "Skråskruesetene"),
]

# BRUKSARKENE står sist blant tegningene og kommer fra docs/img, ikke fra
# docs/schematics: de er strektegninger fra samme skjulte-linje-maskineri som
# stegsidene, ikke skjemategninger. De to er de eneste sidene i boka der noen
# BRUKER sengen - to som sover, to som sitter - og hvert mål på dem er målt på
# referansekroppene i modellen.
USE_SHEETS = [
    ("bruk-sengestilling", "Sengestillingen, i bruk"),
    ("bruk-bordstilling", "Bordstillingen, i bruk"),
]


def build_reference(marks: PageMarks) -> tuple[list[str], list[tuple[str, str]]]:
    pages: list[str] = []
    toc: list[tuple[str, str]] = []

    # ASSEMBLY.md: apningen blir skilleark for referansedelen, og hver ##
    # etter det begynner pa ny side.
    assembly = (DOCS / "ASSEMBLY.md").read_text(encoding="utf-8")
    a_lines = assembly.split("\n")
    a_title = a_lines[0].lstrip("# ").strip()
    a_body = insert_section_marks(render("\n".join(a_lines[1:]), DOCS), marks, "as")
    cut = a_body.find("<h2>")
    a_head, a_rest = a_body[:cut], a_body[cut:]

    pages.append(f"""<section class="page divider" id="ref-assembly">
  {marks.mark('assembly')}
  <p class="eyebrow">Referanse</p>
  <h1>{html.escape(a_title)}</h1>
  {a_head}
  <p class="divider-sub">Byggeveiledningen, de genererte tabellene og
  tegningene. Alle tall er regnet ut av modellen.</p>
</section>""")
    pages.append(f'<section class="page assembly">{a_rest}</section>')
    toc.append(("assembly", "Byggeveiledning — hvorfor"))
    toc.append(("as-vedlegg-a--lastbane", "Vedlegg A — lastbane"))
    toc.append(("as-vedlegg-b--aksepterte-avvik", "Vedlegg B — avvik"))

    for stem, label in REF_DOCS:
        text = strip_generated_comment((DOCS / "generated" / f"{stem}.md").read_text(encoding="utf-8"))
        key = f"doc-{stem}"
        toc.append((key, label))
        pages.append(f"""<section class="page refdoc" id="{key}">
  {marks.mark(key)}
  {render(text, DOCS / "generated")}
</section>""")

    toc.append(("tegninger", "Tegninger"))
    for i, (stem, label) in enumerate(SCHEMATICS):
        path = (DOCS / "schematics" / f"{stem}.svg").resolve()
        first = '<span id="tegninger"></span>' if i == 0 else ""
        # Tegningene er tegnet for skjerm og er tette. Den som blir storst
        # liggende, trykkes liggende.
        orient = "land" if svg_aspect(path) > 1.1 else "port"
        pages.append(f"""<section class="page schematic {orient}" id="sch-{stem}">
  {first}{marks.mark('tegninger') if i == 0 else ''}
  <h1>{html.escape(label)}</h1>
  <figure><img src="{path.as_uri()}" alt="{html.escape(label)}"></figure>
  <p class="cap">docs/schematics/{stem}.svg</p>
</section>""")

    for stem, label in USE_SHEETS:
        path = (DOCS / "img" / f"{stem}.svg").resolve()
        orient = "land" if svg_aspect(path) > 1.1 else "port"
        pages.append(f"""<section class="page schematic {orient}" id="sch-{stem}">
  <h1>{html.escape(label)}</h1>
  <figure><img src="{path.as_uri()}" alt="{html.escape(label)}"></figure>
  <p class="cap">docs/img/{stem}.svg</p>
</section>""")

    pages.append(colophon())
    return pages, toc


def insert_section_marks(body: str, marks: PageMarks, prefix: str) -> str:
    """Merker vedleggene i ASSEMBLY slik at innholdsfortegnelsen finner dem."""
    wanted = {
        "Vedlegg A — lastbane": f"{prefix}-vedlegg-a--lastbane",
        "Vedlegg B — aksepterte avvik": f"{prefix}-vedlegg-b--aksepterte-avvik",
    }
    for title, key in wanted.items():
        body = body.replace(f"<h2>{title}</h2>", f"<h2>{title}{marks.mark(key)}</h2>", 1)
    return body


def colophon() -> str:
    return """<section class="page colophon">
  <h1>Kolofon</h1>
  <p><strong>HANNA</strong> — loftseng med sofa, bord og ekstraseng under.</p>
  <p>Hele sengen er én parametrisk modell. Alle mål i denne boka er regnet ut
  av <code>generate_loftbed.py</code> og skrevet ut av <code>mise run build</code>.
  Strektegningene er projisert ut av den samme modellen med
  <code>mise run montering</code>. Denne PDF-en settes sammen av
  <code>mise run pdf</code>.</p>
  <p class="credits">Piktogrammer basert på Lucide (ISC-lisens).<br>
  Øvrige piktogrammer tegnet for denne bruksanvisningen.</p>
  <p class="placeholder">Revisjon: <span class="rev">—</span></p>
</section>"""


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------

CSS = """
:root { --rule: #d5d5d5; --ink: #111; --muted: #666; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0; color: var(--ink); background: #fff;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10pt; line-height: 1.42;
}
@page { size: A4; margin: 16mm 15mm 15mm 15mm; }

section.page { break-before: page; }
body > section.page:first-child { break-before: auto; }

img { max-width: 100%; }
figure { margin: 0; }
a { color: inherit; text-decoration: none; }
a.xref { border-bottom: 0.4pt dotted #999; }
a.deadlink { border: 0; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.88em; }
.pagemark { color: #fff; font-size: 2pt; }

h1 { font-size: 19pt; letter-spacing: -0.3pt; margin: 0 0 4mm; }
h2 { font-size: 13pt; margin: 0 0 3mm; }
h3 { font-size: 11pt; margin: 5mm 0 2mm; }
h1, h2, h3 { break-after: avoid; }
p { margin: 0 0 3mm; }

table { border-collapse: collapse; width: 100%; margin: 0 0 4mm; font-size: 9pt; }
th, td { border-bottom: 0.4pt solid var(--rule); padding: 1.1mm 2mm;
         text-align: left; vertical-align: middle; }
th { border-bottom: 0.8pt solid var(--ink); font-size: 8.5pt;
     text-transform: uppercase; letter-spacing: 0.4pt; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
td img { display: block; margin: 0 auto; }

/* ---------- forside ---------- */
.cover { text-align: center; padding-top: 6mm; }
.cover h1 { font-size: 62pt; letter-spacing: 6pt; margin: 0; font-weight: 700; }
.cover .cover-sub { font-size: 13pt; color: var(--muted); margin: 2mm 0 0; }
.cover-hero { margin: 6mm 0 4mm; }
.cover-hero img { width: 100%; max-height: 150mm; object-fit: contain; }
.cover-dims table { width: 120mm; margin: 0 auto 4mm; }
.cover-dims th, .cover-dims td { text-align: center; }
.cover-note { font-size: 9.5pt; color: var(--muted); }
.cover-note p { margin: 0 0 2mm; }

/* ---------- innhold ---------- */
.toc h1 { border-bottom: 1pt solid var(--ink); padding-bottom: 2mm; }
.toc-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 10mm; }
.toc h2 { font-size: 10pt; text-transform: uppercase; letter-spacing: 0.6pt;
          color: var(--muted); margin-bottom: 2mm; }
.toc-list { list-style: none; margin: 0; padding: 0; font-size: 9.5pt; }
.toc-list li { display: flex; align-items: baseline; gap: 1mm;
               padding: 1.1mm 0; border-bottom: 0.3pt dotted var(--rule); }
.toc-dots { flex: 1 1 auto; }
.pnum { font-variant-numeric: tabular-nums; color: var(--muted); }
.toc-foot { margin-top: 6mm; font-size: 9pt; color: var(--muted); }

/* ---------- forberedelse ---------- */
/* Kolonne 1 rommer verktoypanelet: tre ikoner i bredden, ca. 29 mm. */
.prep table td:nth-child(1) { width: 32mm; text-align: center; }
.prep table td:nth-child(2) { width: 26mm; text-align: center; }
.prep table td img { display: inline-block; margin: 0 1mm; vertical-align: middle; }

/* ---------- beslag ----------
   Skruglyfene er tegnet i riktig innbyrdes lengde, sa de er brede. Hele
   oversikten star derfor i en spalte, med ikonet og antallet i samme celle. */
.beslag table { font-size: 9.5pt; }
.beslag table td:first-child { width: 96mm; white-space: nowrap; }
.beslag table td:first-child img { display: inline-block; vertical-align: middle;
                                   margin-right: 2.5mm; }
.beslag table td:last-child { padding-left: 4mm; }

/* ---------- deler ---------- */
.delene table td:first-child { width: 62mm; }

/* ---------- stegside ---------- */
.step-head { display: flex; align-items: baseline; gap: 5mm;
             border-bottom: 1pt solid var(--ink); padding-bottom: 2mm; margin-bottom: 4mm; }
.step-num { font-size: 34pt; font-weight: 700; line-height: 1; letter-spacing: -1pt; }
.step-head h1 { font-size: 16pt; margin: 0; }
.step-figure { text-align: center; margin: 0 0 4mm; }
.step-figure img { max-height: 122mm; width: auto; max-width: 100%; }
/* En stegtegning som staar paa hoykant - stigen, halvsnittene, kappeplanen -
   faar all hoyden som blir til overs naar tittel, tabell og notat har sitt.
   Tabellene beholder TO spalter her: en hoy tegning legger beslag paa hoyden,
   og en enspaltet tabell under den skyver resten over pa en side som ellers
   er tom. */
.step.tall .step-figure img { max-height: 136mm; }
.step.tall .step-tables { column-count: 2; }
/* Kappesiden er 14 bord i full lengde og vil ha bredden: liggende A4. */
@page cutplan { size: A4 landscape; margin: 13mm 14mm; }
/* ...and it must NOT split. At 142mm the drawing pushed the joint line, the
   warning and the "in words" link onto a second landscape sheet with nothing
   else on it - a whole page of footnote. The figure gives up 18mm instead. */
.step.cut { page: cutplan; break-inside: avoid; }
.step.cut .step-figure img { width: 100%; max-height: 124mm;
                             object-fit: contain; }
/* Alt annet paa kappesiden holdes nede, sa tegningen far bredden. */
.step.cut .step-head { margin-bottom: 2mm; padding-bottom: 1.5mm; }
.step.cut .step-num { font-size: 26pt; }
.step.cut .step-head h1 { font-size: 13pt; }
.step.cut .step-figure { margin-bottom: 2mm; }
.step.cut .step-tables { column-count: 2; }
.step.cut .step-tables table { font-size: 8pt; margin-bottom: 1.5mm; }
.step.cut .step-notes { font-size: 8.5pt; padding-top: 1.5mm; }
.step-tables { column-count: 2; column-gap: 8mm; }
.step-tables table { break-inside: avoid; margin-bottom: 3mm; font-size: 8.5pt; }
.step-tables table td:first-child { white-space: nowrap; }
.step-notes { font-size: 9pt; border-top: 0.4pt solid var(--rule); padding-top: 2.5mm; }
.step-notes p { margin: 0 0 1.6mm; }
.warn { padding-left: 0; font-weight: 500; }

/* ---------- referanse ---------- */
.divider { padding-top: 42mm; }
.divider .eyebrow { font-size: 10pt; text-transform: uppercase;
                    letter-spacing: 2pt; color: var(--muted); margin-bottom: 2mm; }
.divider h1 { font-size: 27pt; letter-spacing: -0.4pt; margin-bottom: 6mm; }
.divider p, .divider blockquote { max-width: 130mm; }
.divider-sub { color: var(--muted); margin-top: 6mm; }
.divider hr { display: none; }
.assembly h2 { break-before: page; border-bottom: 0.8pt solid var(--ink);
               padding-bottom: 1.5mm; margin-top: 0; }
.assembly > h2:first-child { break-before: auto; }
.assembly hr { display: none; }
.assembly blockquote { margin: 0 0 4mm; padding: 2.5mm 4mm;
                       border-left: 2pt solid var(--ink); background: #f4f4f4; }
.assembly blockquote p:last-child { margin: 0; }
.assembly, .refdoc { font-size: 9.5pt; }
/* J-oversikten er lang og bygd av korte h3-avsnitt. Strammere luft rundt dem
   holder den pa tre sider i stedet for a la ett ledd henge alene pa en fjerde. */
.assembly h3 { margin: 3.4mm 0 1.4mm; }
.assembly p { margin-bottom: 2.4mm; }
.assembly table, .refdoc table { font-size: 8pt; }
.assembly ul, .assembly ol { margin: 0 0 3mm; padding-left: 5mm; }
.refdoc h2 { margin-top: 5mm; }
.refdoc h1 { border-bottom: 1pt solid var(--ink); padding-bottom: 2mm; }

/* ---------- tegninger ---------- */
@page land { size: A4 landscape; margin: 12mm; }
.schematic.land { page: land; }
.schematic h1 { font-size: 15pt; margin-bottom: 3mm; }
.schematic figure { text-align: center; }
.schematic.port img { width: 100%; max-height: 235mm; object-fit: contain; }
.schematic.land img { width: 100%; max-height: 163mm; object-fit: contain; }
.cap { font-size: 8pt; color: var(--muted); margin-top: 2mm; }

/* ---------- kolofon ---------- */
.colophon { padding-top: 60mm; }
.colophon p { max-width: 130mm; }
.placeholder { color: var(--muted); font-style: italic; }
.credits { font-size: 8.5pt; color: var(--muted); }
"""


def assemble_html(marks: PageMarks) -> str:
    manual_pages, manual_toc = build_manual(marks)
    ref_pages, ref_toc = build_reference(marks)
    pages = [manual_pages[0], toc_page(marks, manual_toc, ref_toc)] + manual_pages[1:] + ref_pages
    return f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<title>HANNA — loftseng, monteringsanvisning</title>
<style>{CSS}</style>
</head>
<body>
{chr(10).join(pages)}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Utskrift
# --------------------------------------------------------------------------

def find_chrome() -> str | None:
    env = os.environ.get("CHROME")
    if env and Path(env).exists():
        return env
    for cand in CHROME_CANDIDATES:
        if Path(cand).exists():
            return cand
    for base, pattern in CHROME_GLOBS:
        if not base.exists():
            continue
        hits = sorted(base.glob(pattern))
        hits = [h for h in hits if h.is_file() and os.access(h, os.X_OK)]
        if hits:
            return str(hits[-1])
    return None


def print_pdf(html_path: Path, pdf_path: Path, chrome: str) -> None:
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=20000",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if not pdf_path.exists():
        sys.stderr.write(res.stdout + res.stderr)
        sys.exit("Chrome klarte ikke a skrive PDF-en.")


def page_count(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    m = re.search(r"^Pages:\s+(\d+)", out, flags=re.M)
    return int(m.group(1)) if m else 0


def locate_marks(pdf: Path, tokens: list[str]) -> dict[str, int]:
    """Finner hvilken side hver merkelapp havnet pa."""
    total = page_count(pdf)
    found: dict[str, int] = {}
    for page in range(1, total + 1):
        text = subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
            capture_output=True, text=True,
        ).stdout
        squashed = re.sub(r"\s+", "", text)
        for tok in tokens:
            if tok not in found and re.sub(r"\s+", "", tok) in squashed:
                found[tok] = page
    return found


def apply_page_numbers(doc: str, found: dict[str, int]) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        page = found.get(f"@@{key}@@")
        return f'<span class="pnum">{page if page else "&#160;"}</span>'

    return re.sub(r'<span class="pnum" data-key="([^"]+)">&#160;</span>', repl, doc)


def make_previews(pdf: Path, width: int) -> list[Path]:
    # Only the page previews are this run's to throw away. docs/preview is the
    # review shelf, and other things live on it - the fill-code contrast proof
    # (`render_lineart.py --fill-contrast`) among them - which a PDF build has
    # no business deleting just because it is about to write beside them.
    for old in PREVIEW_DIR.glob("page-*.png"):
        old.unlink()
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    if shutil.which("pdftoppm"):
        subprocess.run(
            ["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1",
             str(pdf), str(PREVIEW_DIR / "page")],
            check=True,
        )
    else:  # pragma: no cover
        try:
            import fitz  # type: ignore
        except ImportError:
            sys.exit("Verken pdftoppm eller pymupdf finnes - ingen forhandsvisning.")
        doc = fitz.open(pdf)
        for i, page in enumerate(doc, 1):
            zoom = width / page.rect.width
            page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(
                PREVIEW_DIR / f"page-{i:02d}.png"
            )
    return sorted(PREVIEW_DIR.glob("page-*.png"))


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=PDF_OUT)
    ap.add_argument("--preview-width", type=int, default=1200)
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--keep-html", type=Path, default=None,
                    help="Skriv den sammensatte print-HTML-en hit ogsa")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        sys.exit(
            "Fant ingen Chrome/Chromium. Sett CHROME=/sti/til/binaer, eller "
            "installer Google Chrome."
        )
    print(f"Utskriftsmotor: {chrome}")

    # Innholdsfortegnelsen far sidetallene sine ved a LESE den ferdige PDF-en:
    # pdfinfo teller sidene og pdftotext sier hvilken side hver merkelapp
    # havnet pa. Uten poppler er det ingen andre runde, og det skal sies her -
    # ikke som en FileNotFoundError midt i kjoringen.
    poppler = [t for t in ("pdfinfo", "pdftotext") if not shutil.which(t)]
    if poppler:
        sys.exit(
            f"Fant ikke {' og '.join(poppler)} (poppler). Sidetallene i "
            "innholdsfortegnelsen leses ut av den ferdige PDF-en, sa den "
            "trengs: `brew install poppler` / `apt install poppler-utils`."
        )

    marks = PageMarks()
    doc = assemble_html(marks)

    work = args.out.parent / ".hanna-print"
    work.mkdir(parents=True, exist_ok=True)
    html_path = work / "hanna.html"

    # Runde 1: finn sidetallene til innholdsfortegnelsen.
    html_path.write_text(doc, encoding="utf-8")
    print_pdf(html_path, args.out, chrome)
    found = locate_marks(args.out, marks.tokens)
    missing = [t for t in marks.tokens if t not in found]
    if missing:
        print(f"  merkelapper uten side: {', '.join(missing)}", file=sys.stderr)

    # Runde 2: samme oppsett, med tallene satt inn.
    doc = apply_page_numbers(doc, found)
    html_path.write_text(doc, encoding="utf-8")
    print_pdf(html_path, args.out, chrome)

    if args.keep_html:
        args.keep_html.write_text(doc, encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)

    total = page_count(args.out)
    print(f"{args.out.relative_to(ROOT)} — {total} sider, "
          f"{args.out.stat().st_size / 1_000_000:.1f} MB")

    if not args.no_preview:
        pngs = make_previews(args.out, args.preview_width)
        print(f"{PREVIEW_DIR.relative_to(ROOT)}/ — {len(pngs)} forhandsvisninger "
              f"({args.preview_width} px)")


if __name__ == "__main__":
    main()
