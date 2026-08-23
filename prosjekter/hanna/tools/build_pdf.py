#!/usr/bin/env python3
"""Bygger de to trykkeklare PDF-ene av HANNA-manualen.

  mise run pdf

TO HEFTER, OG HVORFOR. Sengen er bygget (2026-08-23), og byggmesteren sa hva
han faktisk brukte: de nummererte stegsidene. Resten er oppslag. Et hefte som
skal ligge apent pa benken og bli sølt pa, og et hefte som skal sta i hylla,
er to forskjellige trykksaker - sa de trykkes hver for seg:

  docs/hanna.pdf            BYGGEHEFTET. Forside, innhold, sengen i mal, mal
                            rommet forst, for du begynner, beslag, deler,
                            steg 0-12, kappliste, innkjopsliste og
                            spikerslagarket. Dette er det som skrives ut.
  docs/hanna-referanse.pdf  REFERANSEHEFTET. Byggeveiledningen med vedlegg,
                            nokkelmal, beslagliste, skrueretninger, de ovrige
                            tegningene, bruksarkene og kolofonen.

Kildene er de samme som for: docs/MONTERING.md, docs/ASSEMBLY.md,
docs/generated/*.md og docs/schematics/*.svg. Hva som havner hvor star i
TARGETS, ett sted, fordi to ting leser det: sidebyggerne og lenkemaskineriet.

Ingenting i docs/ endres. Bildene refereres som absolutte file://-URL-er, slik
at Chrome laster dem fra disk uten nettverk.

Sidetallene i innholdsfortegnelsen finnes ved a rendre hvert hefte to ganger:
forste runde plasserer usynlige merkelapper, pdftotext forteller hvilken side
hver merkelapp havnet pa, andre runde setter tallet inn. Det virker BARE
innenfor ett hefte - en kryssreferanse mellom de to kan ikke bare et sidetall,
og bærer seksjonstittelen i stedet.
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
REF_OUT = DOCS / "hanna-referanse.pdf"
PREVIEW_DIR = DOCS / "preview"

# The two booklets, and what a cross-reference calls the other one.
BOOKS = {"bygg": "byggeheftet", "ref": "referanseheftet"}

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

# HVA SOM TRYKKES HVOR. Ett bord, fordi to ting leser det: sidebyggerne
# lenger nede, som legger seksjonen i det ene heftet eller det andre, og
# fix_links(), som ma vite om en doc-lenke blir staende inne i sitt eget hefte
# eller ma sende leseren til det andre.
#
# `None` som hefte betyr IKKE TRYKT I DET HELE TATT.
# docs/generated/byggesteg.md er den ene: den er stegsidene i ord, og
# stegsidene er det byggmesteren faktisk brukte. A trykke begge er a trykke
# manualen to ganger. Fragmentet lever videre - stegsidene og blekk-assertene
# leser det - det bindes bare ikke inn i noen av heftene.
#
#   filnavn (uten mappe og suffiks) -> (hefte, anker, seksjonstittel)
DOCS_IN = [                     # docs/generated/*.md, i trykkerekkefolge
    ("kappliste", "bygg", "Kappliste"),
    ("innkjopsliste", "bygg", "Innkjøpsliste"),
    ("nokkelmal", "ref", "Nøkkelmål"),
    ("beslagliste", "ref", "Beslagliste"),
    ("skrueretninger", "ref", "Skrueretninger"),
    ("byggesteg", None, "Byggesteg i ord"),
]
SCHEMATICS = [
    # Veggarket star i BYGGEHEFTET, og det er det eneste snittet som gjor det:
    # det skal leses for veggen lukkes, altsa for noe annet i boka er
    # aktuelt, og da ma det ligge i heftet som er med pa plassen.
    ("spikerslag", "bygg", "Bakveggen — spikerslagsoner"),
    ("byggerekkefolge", "ref", "Byggerekkefølgen"),
    ("end-elevation", "ref", "Kortside, snitt A–A"),
    ("ladder-detail", "ref", "Stigen"),
    ("bench-detail", "ref", "Benken"),
    ("panel-detail", "ref", "Den løse platen"),
    ("setedetalj", "ref", "Skråskruesetene"),
]
# BRUKSARKENE står sist blant tegningene og kommer fra docs/img, ikke fra
# docs/schematics: de er strektegninger fra samme skjulte-linje-maskineri som
# stegsidene, ikke skjemategninger. De to er de eneste sidene i boka der noen
# BRUKER sengen - to som sover, to som sitter - og hvert mål på dem er målt på
# referansekroppene i modellen.
USE_SHEETS = [
    ("bruk-sengestilling", "ref", "Sengestillingen, i bruk"),
    ("bruk-bordstilling", "ref", "Bordstillingen, i bruk"),
]

TARGETS = {
    "MONTERING": ("bygg", "montering", "Stegsidene"),
    "ASSEMBLY": ("ref", "ref-assembly", "Byggeveiledning — hvorfor"),
    # «schematics/» som helhet: den forste av tegningene i referanseheftet.
    "schematics/": ("ref", "sch-byggerekkefolge", "Tegninger"),
}
TARGETS.update({stem: (book, f"doc-{stem}", title)
                for stem, book, title in DOCS_IN})
TARGETS.update({stem: (book, f"sch-{stem}", title)
                for stem, book, title in SCHEMATICS + USE_SHEETS})

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


A_RE = re.compile(r'<a href="([^"]+)">(.*?)</a>', re.S)
# En paragraf som ikke er annet enn en henvisning til noe som ikke trykkes.
# Den skal ikke sta igjen som en setning uten mal: «Steg 5 i ord» nederst pa
# hver stegside pekte pa byggesteg.md, og byggesteg.md trykkes ikke lenger.
LONE_UNPRINTED = re.compile(r'<p>\s*<span class="unprinted">.*?</span>\s*</p>\s*',
                            re.S)


def fix_links(chunk: str, book: str) -> str:
    """Doc-lenker, sett fra heftet de star i.

    Tre utfall, og TARGETS avgjor hvilket: malet trykkes i DETTE heftet og
    blir et internt anker; det trykkes i DET ANDRE og blir en henvisning med
    seksjonstittel - aldri med sidetall, for de to heftene nummereres hver for
    seg og et tall pa tvers av dem kunne verken settes inn eller asserteres;
    eller det trykkes ikke, og da sier henvisningen hvilken fil den er.
    """

    def repl(m: re.Match[str]) -> str:
        href, text = m.group(1), m.group(2)
        if href.startswith(("http:", "https:")):
            return m.group(0)
        if href.startswith("#"):
            return f'<a href="{href}" class="xref">{text}</a>'
        target = href.split("#", 1)[0]
        key = Path(target).stem if target else ""
        hit = TARGETS.get(key) or TARGETS.get(target)
        if hit is None:
            return f'<span class="deadlink">{text}</span>'
        where, anchor, title = hit
        if where == book:
            return f'<a href="#{anchor}" class="xref">{text}</a>'
        if where is None:
            # Sier hvilken fil den er. Er lenketeksten allerede stien, sies
            # den én gang og ikke to.
            path = f'<code>docs/{html.escape(target)}</code>'
            if text.strip("` ") in (target, f"docs/{target}"):
                return f'<span class="unprinted">{path}</span>'
            return f'<span class="unprinted">{text} ({path})</span>'
        return (f'<span class="xbook">«{html.escape(title)}» i '
                f'{BOOKS[where]}</span>')

    return A_RE.sub(repl, chunk)


def render(text: str, base: Path, book: str, scale: float = 1.0) -> str:
    out = fix_links(fix_images(md_to_html(text), base, scale), book)
    return LONE_UNPRINTED.sub("", out)


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


def build_manual(marks: PageMarks) -> tuple[str, list[str], list[tuple[str, str]]]:
    """Returnerer (forside, sider, innholdsfortegnelse) for byggeheftet."""
    src = strip_generated_comment((DOCS / "MONTERING.md").read_text(encoding="utf-8"))
    cover = ""
    pages: list[str] = []
    toc: list[tuple[str, str]] = []

    for section in split_sections(src):
        lines = section.split("\n")
        head = lines[0].strip()

        if head == "# HANNA":
            cover = cover_page(section, marks)
        elif head == "# Før du begynner":
            key = "prep"
            toc.append((key, "Før du begynner"))
            pages.append(simple_page(section, marks, key, css="prep"))
        elif head == "# Sengen i mål":
            # Maltegningen: en tegning som fyller satsbredden og tre korte
            # avsnitt under den. Samme mal som forsteg-siden - figuren er
            # allerede nøyaktig 180 mm bred (render_maaltegning), sa den
            # trenger ingen egen CSS.
            key = "maal"
            toc.append((key, "Sengen i mål"))
            pages.append(simple_page(section, marks, key, css="prep"))
        elif head == "# Mål rommet først":
            # Forsteget: nisja males for noe kappes. Ren tekst og en liten
            # tabell, sa den gar pa prep-malen.
            key = "rommet"
            toc.append((key, "Mål rommet først"))
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

    return cover, pages, toc


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
            hero = render(b, DOCS, "bygg")
        elif b.startswith("|"):
            dims = render(b, DOCS, "bygg")
        else:
            rest.append(b)
    body = render("\n\n".join(rest), DOCS, "bygg")
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


def toc_page(marks: PageMarks, cols, foot: str) -> str:
    """Innholdsfortegnelsen for ETT hefte.

    `cols` er [(spaltetittel, [(nokkel, tekst), ...]), ...]. Sidetallene er
    tomme her og settes inn av andre runde - og de er heftets EGNE sidetall,
    som er hele grunnen til at det andre heftet ikke star i denne lista.
    """

    def rows(items) -> str:
        out = []
        for key, label in items:
            out.append(
                f'<li><span class="toc-label">{html.escape(label)}</span>'
                f'<span class="toc-dots"></span>{marks.slot(key)}</li>'
            )
        return "\n".join(out)

    body = "\n".join(
        f'<div><h2>{html.escape(head)}</h2>'
        f'<ol class="toc-list">{rows(items)}</ol></div>'
        for head, items in cols)
    return f"""<section class="page toc">
  <h1>Innhold</h1>
  <div class="toc-cols">{body}</div>
  <p class="toc-foot">{foot}</p>
</section>"""


def simple_page(section: str, marks: PageMarks, key: str, css: str, scale: float = 1.0) -> str:
    body = render(strip_first_heading(section), DOCS, "bygg", scale)
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


# X17: stegsidens avstivingsnotat. Det staar sist i notatfeltet og er det
# ENESTE notatet som kan komme til uten aa vaere der - et steg baerer det bare
# saa lenge kroppen det bygger fortsatt henger i ett feste - saa siden maa
# kunne gi plass til det uten aa deles. Se `.step.braced` i stilarket.
BRACE_NOTE = "\N{COMPRESSION}"        # 🗜️, tvingen


def step_page(num: str, title: str, rest: str, marks: PageMarks, key: str) -> str:
    figure = ""
    tables: list[str] = []
    notes: list[str] = []
    for b in split_blocks(rest):
        if b.startswith("!["):
            figure = render(b, DOCS, "bygg")
        elif b.startswith("|"):
            tables.append(render(b, DOCS, "bygg"))
        elif b.startswith("⚠"):
            notes.append(f'<p class="warn">{render(b, DOCS, "bygg")[3:-4]}</p>')
        elif b.startswith(BRACE_NOTE):
            notes.append(f'<p class="brace">{render(b, DOCS, "bygg")[3:-4]}</p>')
        else:
            # En bolk som var en henvisning til noe utrykt - «Steg N i ord» -
            # kommer tilbake tom herfra, og en tom <p> er en tynn strek over
            # notatfeltet som ikke sier noe.
            block = render(b, DOCS, "bygg")
            if block.strip():
                notes.append(block)

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
    # Et steg med avstivingsnotat har to linjer mer under tegningen enn de
    # andre. Samme regningen som paa kappesiden under: tegningen gir fra seg
    # hoyden, for alternativet er en hel side med to linjer paa.
    if any('class="brace"' in n for n in notes):
        kind += " braced"
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
# De genererte tabellene og tegningene - hver til sitt hefte
# --------------------------------------------------------------------------

def doc_pages(marks: PageMarks, book: str) -> tuple[list[str], list[tuple[str, str]]]:
    """De genererte tabellene som horer hjemme i `book`, i DOCS_IN-rekkefolge."""
    pages: list[str] = []
    toc: list[tuple[str, str]] = []
    for stem, where, label in DOCS_IN:
        if where != book:
            continue
        text = strip_generated_comment(
            (DOCS / "generated" / f"{stem}.md").read_text(encoding="utf-8"))
        key = f"doc-{stem}"
        toc.append((key, label))
        pages.append(f"""<section class="page refdoc" id="{key}">
  {marks.mark(key)}
  {render(text, DOCS / "generated", book)}
</section>""")
    return pages, toc


def sheet_pages(marks: PageMarks, folder: str, wanted) -> tuple[list[str], list[tuple[str, str]]]:
    """En tegning per side, hver med sin egen merkelapp.

    Egen merkelapp per ark og ikke en felles «Tegninger»-rad: na som boka er
    to hefter er tegningene delt mellom dem, og en samlerad ville sendt
    leseren til den forste av dem uansett hvilken han slo opp.
    """
    pages: list[str] = []
    toc: list[tuple[str, str]] = []
    for stem, label in wanted:
        path = (DOCS / folder / f"{stem}.svg").resolve()
        # Tegningene er tegnet for skjerm og er tette. Den som blir storst
        # liggende, trykkes liggende.
        orient = "land" if svg_aspect(path) > 1.1 else "port"
        key = f"sch-{stem}"
        toc.append((key, label))
        pages.append(f"""<section class="page schematic {orient}" id="{key}">
  {marks.mark(key)}
  <h1>{html.escape(label)}</h1>
  <figure><img src="{path.as_uri()}" alt="{html.escape(label)}"></figure>
  <p class="cap">docs/{folder}/{stem}.svg</p>
</section>""")
    return pages, toc


def build_manual_book(marks: PageMarks) -> list[str]:
    """BYGGEHEFTET: forside, innhold, stegsidene og det de trenger ved benken."""
    cover, pages, toc = build_manual(marks)
    docs, doc_toc = doc_pages(marks, "bygg")

    sheets, sheet_toc = sheet_pages(
        marks, "schematics",
        [(stem, label) for stem, where, label in SCHEMATICS if where == "bygg"])

    toc_html = toc_page(
        marks,
        [("Monter sengen", toc), ("Lister og ark", doc_toc + sheet_toc)],
        "Dette heftet er nok til å bygge sengen. Referanseheftet "
        "(<code>docs/hanna-referanse.pdf</code>) forklarer hvorfor, og eier "
        "alle tallene.")
    return [cover, toc_html] + pages + docs + sheets


def build_reference_book(marks: PageMarks) -> list[str]:
    """REFERANSEHEFTET: begrunnelsene, tallene og de ovrige tegningene."""
    pages: list[str] = []

    # ASSEMBLY.md: apningen blir forsiden pa dette heftet, og hver ## etter
    # det begynner pa ny side.
    assembly = (DOCS / "ASSEMBLY.md").read_text(encoding="utf-8")
    a_lines = assembly.split("\n")
    a_title = a_lines[0].lstrip("# ").strip()
    a_body = insert_section_marks(
        render("\n".join(a_lines[1:]), DOCS, "ref"), marks, "as")
    cut = a_body.find("<h2>")
    a_head, a_rest = a_body[:cut], a_body[cut:]

    cover = f"""<section class="page divider" id="ref-assembly">
  <p class="eyebrow">HANNA — referanse</p>
  <h1>{html.escape(a_title)}</h1>
  {a_head}
  <p class="divider-sub">Byggeveiledningen, de genererte tabellene og
  tegningene. Alle tall er regnet ut av modellen. Selve byggingen står i
  byggeheftet, <code>docs/hanna.pdf</code>.</p>
</section>"""
    # Merkelappen star pa den forste TEKSTsiden, ikke pa forsiden: raden i
    # innholdsfortegnelsen skal sende leseren dit veiledningen begynner. Den
    # legges INNE i den forste h2-en, ikke foran den, for `.assembly > h2
    # :first-child` er det som lar det forste kapitlet stå pa samme ark som
    # sitt eget oppslag - et span foran den koster et helt blankt ark.
    pages.append('<section class="page assembly">'
                 + a_rest.replace("<h2>", "<h2>" + marks.mark("assembly"), 1)
                 + '</section>')
    a_toc = [("assembly", "Byggeveiledning — hvorfor"),
             ("as-vedlegg-a--lastbane", "Vedlegg A — lastbane"),
             ("as-vedlegg-b--aksepterte-avvik", "Vedlegg B — avvik")]

    docs, doc_toc = doc_pages(marks, "ref")
    pages += docs

    sheets, sheet_toc = sheet_pages(
        marks, "schematics",
        [(stem, label) for stem, where, label in SCHEMATICS if where == "ref"])
    use, use_toc = sheet_pages(
        marks, "img", [(stem, label) for stem, _w, label in USE_SHEETS])
    sheets += use
    sheet_toc += use_toc
    pages += sheets
    pages.append(colophon())

    toc_html = toc_page(
        marks,
        [("Hvorfor", a_toc), ("Tall og tegninger", doc_toc + sheet_toc)],
        "Ingenting her trengs ved benken. Stegsidene står i byggeheftet, "
        "<code>docs/hanna.pdf</code>.")
    return [cover, toc_html] + pages


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
/* En henvisning til det ANDRE heftet. Ingen prikket understrek, for det er
   ingenting a folge her - den er satt i kursiv fordi den er en tittel, og
   det er tittelen som er adressen: to hefter nummereres hver for seg, sa et
   sidetall pa tvers av dem kunne verken settes inn eller sjekkes. */
.xbook { font-style: italic; }
.unprinted, .deadlink { border: 0; }
.unprinted code { font-style: normal; }
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
/* Malefiguren over piktogramtabellen tar det meste av det som er igjen av
   forstegssiden, og da havnet "Slik strekes en del opp mot vegg og gulv:"
   alene nederst mens tabellen den innleder gikk over pa neste side. En
   avsnittslinje som star igjen uten det den innleder er ikke en side, det er
   en feil - overskriften folger tabellen sin. */
#rommet p:has(+ table) { break-after: avoid; }

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
/* X17: avstivingsnotatet er to linjer til under tegningen, og paa den tetteste
   stegsiden var det nok til aa skyve dem alene over paa neste ark. Tegningen
   gir fra seg 12mm i stedet - samme avveining som kappesiden over. */
.step.braced .step-figure img { max-height: 110mm; }
.step.braced.tall .step-figure img { max-height: 124mm; }
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


BOOK_BUILDERS = {
    "bygg": (build_manual_book, PDF_OUT,
             "HANNA — loftseng, byggehefte"),
    "ref": (build_reference_book, REF_OUT,
            "HANNA — loftseng, referansehefte"),
}


def assemble_html(book: str, marks: PageMarks) -> str:
    build, _out, title = BOOK_BUILDERS[book]
    pages = build(marks)
    return f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
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


def make_previews(pdf: Path, width: int, stem: str) -> list[Path]:
    """docs/preview/<stem>-NN.png - en per side i heftet.

    `stem` skiller de to heftene fra hverandre pa hylla: byggeheftets sider
    heter fortsatt page-NN, som er det check_tall og kontaktarket leter etter,
    og referanseheftets heter ref-NN.
    """
    # Only this booklet's page previews are this run's to throw away.
    # docs/preview is the review shelf, and other things live on it - the
    # fill-code contrast proof (`render_lineart.py --fill-contrast`) among
    # them - which a PDF build has no business deleting just because it is
    # about to write beside them.
    for old in PREVIEW_DIR.glob(f"{stem}-*.png"):
        old.unlink()
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    if shutil.which("pdftoppm"):
        subprocess.run(
            ["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1",
             str(pdf), str(PREVIEW_DIR / stem)],
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
                PREVIEW_DIR / f"{stem}-{i:02d}.png"
            )
    return sorted(PREVIEW_DIR.glob(f"{stem}-*.png"))


def build_book(book: str, out: Path, chrome: str, work: Path,
               keep_html: Path | None) -> int:
    """Skriver ett hefte og returnerer sidetallet.

    To runder, som for: forste plasserer merkelappene, pdftotext sier hvilken
    side hver havnet pa, andre setter tallet inn. Hvert hefte har sitt eget
    sett merkelapper, for det er sine egne sider det teller.
    """
    marks = PageMarks()
    doc = assemble_html(book, marks)
    html_path = work / f"hanna-{book}.html"

    html_path.write_text(doc, encoding="utf-8")
    print_pdf(html_path, out, chrome)
    found = locate_marks(out, marks.tokens)
    missing = [t for t in marks.tokens if t not in found]
    if missing:
        print(f"  merkelapper uten side i {out.name}: {', '.join(missing)}",
              file=sys.stderr)

    doc = apply_page_numbers(doc, found)
    html_path.write_text(doc, encoding="utf-8")
    print_pdf(html_path, out, chrome)
    if keep_html:
        keep_html.write_text(doc, encoding="utf-8")
    return page_count(out)


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=PDF_OUT,
                    help="Byggeheftet. Referanseheftet legges ved siden av "
                         "det, som hanna-referanse.pdf")
    ap.add_argument("--preview-width", type=int, default=1200)
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--keep-html", type=Path, default=None,
                    help="Skriv byggeheftets print-HTML hit ogsa")
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

    work = args.out.parent / ".hanna-print"
    work.mkdir(parents=True, exist_ok=True)
    outs = {"bygg": args.out, "ref": args.out.with_name(REF_OUT.name)}
    stems = {"bygg": "page", "ref": "ref"}

    for book in ("bygg", "ref"):
        out = outs[book]
        total = build_book(book, out, chrome, work,
                           args.keep_html if book == "bygg" else None)
        print(f"{out.relative_to(ROOT)} — {total} sider, "
              f"{out.stat().st_size / 1_000_000:.1f} MB")
        if not args.no_preview:
            pngs = make_previews(out, args.preview_width, stems[book])
            print(f"{PREVIEW_DIR.relative_to(ROOT)}/{stems[book]}-*.png — "
                  f"{len(pngs)} forhandsvisninger ({args.preview_width} px)")

    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
