"""Sosial forhåndsvisning av repoet - GitHubs og:image, 1280 x 640.

Dette er PDF-forsiden (tools/build_pdf.py, cover_page) lagt ned på siden:
samme hvite ark, samme tunge grotesk, samme strektegning, samme målstripe -
men i 2:1 og med plass til begge navnene. Verkstedet står øverst i det små
(«snekkerbua»), prosjektet dominerer (HANNA), for lenken som deles peker på
repoet og ikke bare på sengen.

Teksten hentes ut av docs/MONTERING.md - den samme forsidebolken build_pdf.py
setter - så tittel, undertittel, mål og faktalinja er de tallene modellen
skrev, ikke tall skrevet av på nytt her. Tegningen er docs/img/hanna-hero.svg,
brukt som vektor og ikke som PNG, så den er skarp i begge oppløsningene.

Én ting er tegnet tyngre enn originalen med vilje: streken i tegningen. Et
og:image vises like ofte som en 320 px tommelfingernegl som i full bredde, og
en strek som er riktig ved 1280 px er borte ved 320. HERO_STROKE_PX er derfor
satt etter tommelfingerneglen.

Skriver docs/img/hanna-poster.svg (kilden), hanna-poster.png (1280 x 640) og
hanna-poster@2x.png (2560 x 1280). PNG-ene lages med rsvg-convert.

Usage:
    python tools/render_poster.py [--out docs/img]
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTERING = os.path.join(ROOT, "docs", "MONTERING.md")
HERO_SVG = os.path.join(ROOT, "docs", "img", "hanna-hero.svg")

# --------------------------------------------------------------------------
# Lerret og typografi
# --------------------------------------------------------------------------

W, H = 1280.0, 640.0          # og:image, 2:1 - GitHubs eksakte format
MARGIN = 64.0
COL_W = 556.0                 # tekstspalten til venstre
INK = "#111"
MUTED = "#5a5a5a"
RULE = "#111"
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"

# Tegningen til høyre: en boks teksten aldri kommer inn i.
HERO_X, HERO_W = 648.0, 600.0
HERO_STROKE_PX = 2.7          # streken i lerretspiksler ved 1280 px bredde

WORDMARK_TRACK = 0.105        # sperring, i em - forsiden har 6pt på 62pt
WORDMARK_TARGET = 548.0       # bredden ordmerket skal fylle av spalten

# Helvetica-Bold, tegnbredder i 1/1000 em (AFM). Bare det ordmerket trenger:
# store bokstaver, så «HANNA» kan måles og settes så stort spalten tåler i
# stedet for å bli tastet inn som en punktstørrelse som stemmer for ett ord.
BOLD_CAPS = {
    "A": 722, "B": 722, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 556, "K": 722, "L": 611, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611, " ": 278, "Å": 722,
    "Ø": 778, "Æ": 1000,
}
CAP_HEIGHT = 0.717            # Helvetica versalhøyde, i em


def fit_size(text: str, target_w: float, track: float) -> float:
    """Punktstørrelsen som gjør `text` nøyaktig `target_w` bred."""
    ems = sum(BOLD_CAPS.get(c, 722) for c in text) / 1000.0
    ems += track * max(len(text) - 1, 0)
    return target_w / ems


# --------------------------------------------------------------------------
# Kilder
# --------------------------------------------------------------------------

def read_cover() -> dict:
    """Plukker forsidebolken ut av docs/MONTERING.md.

    Samme bolk som build_pdf.cover_page setter: `# tittel`, `## undertittel`,
    måltabellen og faktalinja under den.
    """
    src = open(MONTERING, encoding="utf-8").read()
    # Filen åpner med generert-av-merknaden. Den er ikke forsidetekst.
    src = re.sub(r"^\s*<!--.*?-->\s*", "", src, count=1, flags=re.S)
    section = src.split("\n---\n", 1)[0]
    blocks = [b.strip() for b in re.split(r"\n\s*\n", section.strip()) if b.strip()]

    cover = {"title": "", "sub": "", "dims": [], "meta": ""}
    rows = []
    for b in blocks:
        if b.startswith("# "):
            cover["title"] = b[2:].strip()
        elif b.startswith("## "):
            cover["sub"] = b[3:].strip()
        elif b.startswith("|"):
            for line in b.split("\n"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if any(set(c) <= set("-: ") and c for c in cells):
                    continue
                rows.append([c.replace("**", "").strip() for c in cells])
        elif not b.startswith("!") and not cover["meta"]:
            cover["meta"] = b

    if len(rows) >= 2:
        cover["dims"] = list(zip(rows[0], rows[1]))
    if not (cover["title"] and cover["sub"] and len(cover["dims"]) == 3):
        sys.exit(f"FEIL: fant ikke forsidebolken i {MONTERING}")
    return cover


def read_hero() -> tuple[str, tuple[float, float, float, float]]:
    """Strektegningen som ett path-d, med sin egen tette rammeboks.

    hanna-hero.svg har luft rundt motivet fordi den skal stå på en A4-side.
    Her er plassen målt opp på forhånd, så tegningen legges inn etter det den
    faktisk dekker og ikke etter lerretet den kom med.
    """
    svg = open(HERO_SVG, encoding="utf-8").read()
    ds = re.findall(r'<path d="([^"]+)"', svg)
    if not ds:
        sys.exit(f"FEIL: ingen strek i {HERO_SVG}")
    d = " ".join(ds)
    pts = [(float(m.group(1)), float(m.group(2)))
           for m in re.finditer(r"(-?[\d.]+),(-?[\d.]+)", d)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return d, (min(xs), min(ys), max(xs), max(ys))


# --------------------------------------------------------------------------
# SVG
# --------------------------------------------------------------------------

def _f(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def text(x, y, s, size, weight="normal", fill=INK, track=0.0, anchor="start"):
    ls = f' letter-spacing="{_f(track)}"' if track else ""
    return (f'<text x="{_f(x)}" y="{_f(y)}" font-family="{FONT}" '
            f'font-size="{_f(size)}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}"{ls}>{_esc(s)}</text>')


def compose(cover: dict, hero_d: str, hero_box) -> str:
    x0, y0, x1, y1 = hero_box
    scale = HERO_W / (x1 - x0)
    hero_h = (y1 - y0) * scale
    tx = HERO_X - x0 * scale
    ty = (H - hero_h) / 2.0 - y0 * scale

    size = fit_size(cover["title"], WORDMARK_TARGET, WORDMARK_TRACK)
    cap = size * CAP_HEIGHT

    # Grunnlinjene i spalten. Ordmerket er ankeret; alt annet henger av det.
    y_top = 66.0                       # verkstedets navn, øverst
    y_mark = 262.0                     # ordmerkets grunnlinje
    y_sub = y_mark + 46.0
    y_label = 452.0                    # målstripa: etikett, strek, verdi
    y_rule = y_label + 13.0
    y_value = y_rule + 40.0
    y_meta = 566.0

    if y_mark - cap < y_top + 24.0:
        sys.exit("FEIL: ordmerket kolliderer med topplinja")

    out = [f'<rect width="{_f(W)}" height="{_f(H)}" fill="#ffffff"/>']

    # Tegningen først, så teksten alltid ligger over den.
    out.append(f'<g transform="translate({_f(tx)},{_f(ty)}) scale({_f(scale)})" '
               f'fill="none" stroke="{INK}" '
               f'stroke-width="{_f(HERO_STROKE_PX / scale)}" '
               'stroke-linecap="round" stroke-linejoin="round">')
    out.append(f'  <path d="{hero_d}"/>')
    out.append('</g>')

    # Verkstedet: lite, øverst, med undertittelen sin på samme linje. Ett
    # tekstelement med to tspan-er, så navnet og slagordet settes etter
    # hverandre av tekstmotoren og ikke etter en avstand tastet inn her.
    out.append(
        f'<text x="{_f(MARGIN)}" y="{_f(y_top)}" font-family="{FONT}" '
        f'font-size="21" fill="{INK}">'
        f'<tspan font-weight="700">snekkerbua</tspan>'
        f'<tspan dx="11" font-size="16" fill="{MUTED}">'
        f'{_esc("— der Hans gjør ting han (ennå) ikke kan")}</tspan></text>')

    # Prosjektet: stort.
    out.append(text(MARGIN, y_mark, cover["title"], size, weight="700",
                    track=size * WORDMARK_TRACK))
    out.append(text(MARGIN, y_sub, cover["sub"], 22, fill=MUTED))

    # Målstripa, satt som på forsiden: etikett over streken, verdi under.
    cell = COL_W / 3.0
    for i, (label, value) in enumerate(cover["dims"]):
        cx = MARGIN + i * cell
        out.append(text(cx, y_label, label.upper(), 13, fill=MUTED, track=1.3))
        out.append(text(cx, y_value, value, 28, weight="700"))
    out.append(f'<line x1="{_f(MARGIN)}" y1="{_f(y_rule)}" '
               f'x2="{_f(MARGIN + COL_W)}" y2="{_f(y_rule)}" '
               f'stroke="{RULE}" stroke-width="1.6"/>')

    out.append(text(MARGIN, y_meta, cover["meta"], 16, fill=MUTED))

    body = "\n".join("  " + line for line in out)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{_f(W)}" '
            f'height="{_f(H)}" viewBox="0 0 {_f(W)} {_f(H)}">\n'
            f'  <title>{_esc(cover["title"])} — snekkerbua</title>\n'
            f'{body}\n</svg>\n')


def render(svg_path: str, png_path: str, width: int, height: int) -> None:
    cmd = ["rsvg-convert", "-w", str(width), "-h", str(height),
           svg_path, "-o", png_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{res.stdout}\n{res.stderr}")


def main(argv) -> None:
    out_dir = os.path.join(ROOT, "docs", "img")
    i = 1
    while i < len(argv):
        if argv[i] == "--out":
            out_dir = argv[i + 1]; i += 2
        else:
            sys.exit(f"ukjent argument: {argv[i]}")

    os.makedirs(out_dir, exist_ok=True)
    hero_d, hero_box = read_hero()
    svg = compose(read_cover(), hero_d, hero_box)

    svg_path = os.path.join(out_dir, "hanna-poster.svg")
    with open(svg_path, "w", encoding="utf-8") as fh:
        fh.write(svg)

    for name, w, h in (("hanna-poster.png", 1280, 640),
                       ("hanna-poster@2x.png", 2560, 1280)):
        png = os.path.join(out_dir, name)
        render(svg_path, png, w, h)
        print(f"  poster  {w}x{h}  -> {png}")


if __name__ == "__main__":
    main(sys.argv)
