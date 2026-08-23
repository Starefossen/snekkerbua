"""Kontaktark av byggeheftet - de første sidene i docs/hanna.pdf, side ved side.

README-en påstår at manualen er kompilert ut av modellen. Påstanden er lettere
å tro på når man ser sidene: forsiden, innholdet, kuttplanen og de første
byggestegene i ett bilde, i den rekkefølgen de kommer i heftet. Dette er det
bildet - et rutenett med sidene i leserekkefølge, radvis.

BYGGEHEFTET og ikke referanseheftet: manualen er to PDF-er, og det er
byggeheftet den som står ved sagen slår opp. Referanseheftet er oppslag, og et
kontaktark av oppslag sier ingenting. `--pdf` tar den andre om noen vil se
den.

Sidene rendres med poppler (`pdftoppm`) og settes sammen med Pillow. Ingenting
her vet noe om innholdet i manualen: verktøyet ber om N sider, får vite hvor
store de ble, og regner ut resten. Sidestørrelsen leses av rendringen, ikke av
et tall skrevet her, så et annet papirformat gir et annet - og riktig - bilde.

Rutenettet er satt som et kontaktark og ikke som en collage: hvit bakgrunn,
samme luft mellom sidene som rundt dem, og en hårfin grå kant per side så to
hvite ark ved siden av hverandre ikke flyter sammen. Ingen skygger, ingen
rammer, ingen sidetall - heftet har sine egne.

Trenger et ferdig docs/hanna.pdf (`mise run pdf`). Det bygges ikke her: PDF-en
koster en Chrome-runde, og dette verktøyet er en avlesning av den, ikke en ny
kilde.

Skriver docs/img/hanna-manual-sider.png. To kjøringer på samme PDF gir
byte-identisk fil.

Usage:
    python tools/render_pdf_matrix.py [--pages 9] [--cols 3] [--width 1800]
                                      [--pdf docs/hanna.pdf] [--out ...]
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "docs", "hanna.pdf")
OUT = os.path.join(ROOT, "docs", "img", "hanna-manual-sider.png")

# --------------------------------------------------------------------------
# Arket
# --------------------------------------------------------------------------

# Total bredde. Satt etter det bildet skal gjøre: vises i en README i om lag
# 900 px, og skal tåle å bli åpnet i full størrelse uten at brødteksten på
# sidene blir grøt. 1800 px over tre A4-sider er ~70 dpi per side - layouten er
# tydelig og teksten så vidt lesbar som tekst.
TOTAL_W = 1800

# Luften mellom sidene, som andel av sidebredden. Den samme luften brukes ute
# i kanten, så arket har én avstand og ikke to.
GUTTER_FRAC = 1.0 / 32.0

PAPER = (255, 255, 255)
EDGE = (216, 216, 216)      # hårfin grå kant, så hvitt ark på hvitt ark skilles


def render_pages(pdf: str, pages: int, width: int, work: str) -> list[Image.Image]:
    """Første `pages` sider av `pdf` som bilder, `width` px brede."""
    if not os.path.exists(pdf):
        sys.exit(f"FEIL: fant ikke {pdf} - kjør `mise run pdf` først.")
    if not shutil.which("pdftoppm"):
        sys.exit("FEIL: pdftoppm mangler (brew install poppler / "
                 "apt install poppler-utils).")

    stem = os.path.join(work, "side")
    # -scale-to-y -1 betyr «behold sideforholdet», så høyden er sidens egen.
    cmd = ["pdftoppm", "-png", "-f", "1", "-l", str(pages),
           "-scale-to-x", str(width), "-scale-to-y", "-1", pdf, stem]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{res.stdout}\n{res.stderr}")

    # pdftoppm nummererer filene selv, med like mange siffer som sidetallet
    # trenger. Sorter på tallet og ikke på navnet, så side 10 ikke havner
    # foran side 2 den dagen noen ber om flere enn ni.
    files = sorted(
        (f for f in os.listdir(work) if f.startswith("side-") and f.endswith(".png")),
        key=lambda f: int(f[len("side-"):-len(".png")]),
    )
    if len(files) != pages:
        sys.exit(f"FEIL: ba om {pages} sider, fikk {len(files)} fra {pdf}.")
    return [Image.open(os.path.join(work, f)).convert("RGB") for f in files]


def compose(pages: list[Image.Image], cols: int, page_w: int, gutter: int) -> Image.Image:
    """Sidene i et rutenett, radvis, med samme luft ute som inne."""
    rows = -(-len(pages) // cols)
    # Cellen er den største siden - så et hefte med både stående og liggende
    # sider fortsatt får rette rader og kolonner.
    cell_h = max(p.height for p in pages)
    W = cols * page_w + (cols + 1) * gutter
    H = rows * cell_h + (rows + 1) * gutter

    sheet = Image.new("RGB", (W, H), PAPER)
    for i, page in enumerate(pages):
        col, row = i % cols, i // cols
        x = gutter + col * (page_w + gutter) + (page_w - page.width) // 2
        y = gutter + row * (cell_h + gutter) + (cell_h - page.height) // 2
        # Kanten tegnes i luften rundt siden, ikke oppå den, så ingen strek på
        # arket blir spist av en ramme.
        for dx, dy, w, h in (
            (x - 1, y - 1, page.width + 2, 1),          # over
            (x - 1, y + page.height, page.width + 2, 1),  # under
            (x - 1, y - 1, 1, page.height + 2),         # venstre
            (x + page.width, y - 1, 1, page.height + 2),  # høyre
        ):
            sheet.paste(EDGE, (dx, dy, dx + w, dy + h))
        sheet.paste(page, (x, y))
    return sheet


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf", default=PDF)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--pages", type=int, default=9)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--width", type=int, default=TOTAL_W,
                    help=f"total bredde i px (standard {TOTAL_W})")
    args = ap.parse_args(argv[1:])

    # Sidebredden er det som blir igjen av bredden når luften er trukket fra,
    # og luften er en andel av sidebredden: W = cols*p + (cols+1)*p*frac.
    page_w = round(args.width / (args.cols + (args.cols + 1) * GUTTER_FRAC))
    gutter = round(page_w * GUTTER_FRAC)

    with tempfile.TemporaryDirectory() as work:
        pages = render_pages(args.pdf, args.pages, page_w, work)
        sheet = compose(pages, args.cols, page_w, gutter)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    # Ingen metadata: ingen dpi, ingen tekstbolker, ingen tidsstempel - filen
    # er sjekket inn, og da skal to like kjøringer gi de samme bytene.
    sheet.save(args.out, format="PNG", optimize=True)
    print(f"  manualsider  {args.pages} sider {args.cols}x{-(-args.pages // args.cols)}  "
          f"{sheet.width}x{sheet.height}  -> {args.out}")


if __name__ == "__main__":
    main(sys.argv)
