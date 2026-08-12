#!/usr/bin/env python3
"""Genererer strekpiktogrammer (SVG + PNG) til den bildebaserte
monteringsanvisningen for loftsengen HANNA.

To familier med tegninger:

* Beslagglyfer  - én silhuett per festemiddel i docs/generated/beslagliste.md.
  Alle tegnes i samme mm-skala, slik at en 6x120 skrue faktisk er tre ganger
  så lang som en 5x40, og en 6 mm skrue er tykkere enn en 5 mm.
* Piktogrammer  - "før du starter"-symbolene på side 2. De settes sammen av
  ferdige 24x24-ikoner i docs/icons/ (Lucide + egne).

Ingen tredjepartsavhengigheter: SVG-en skrives som tekst. PNG-ene lages med
rsvg-convert hvis den finnes; hvis ikke hoppes de over med en advarsel.

    python3 tools/gen_glyphs.py

Standard utkatalog: docs/img/beslag/ og docs/img/ikon/.
"""

from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import unicodedata

# --------------------------------------------------------------------------
# Felles tegneparametre
# --------------------------------------------------------------------------

INK = "#111"

# Beslagglyfene tegnes i millimeter og skaleres til brukerenheter.
SCALE = 4.0                 # brukerenheter per millimeter
# Glyfene vises i manualen med ca. 0,25 px per brukerenhet (en skrue er rundt
# 30 px høy). Streken må derfor være tung nok til å bli svart, ikke grå.
STROKE_UNITS = 5.5          # hovedkontur, brukerenheter
DETAIL_UNITS = 3.5          # innvendig detalj, brukerenheter
STROKE_MM = STROKE_UNITS / SCALE
DETAIL_MM = DETAIL_UNITS / SCALE
MARGIN_MM = 3.0             # luft rundt motivet
BASE_H_MM = 30.0            # minste lerretshøyde -> skruer får lik høyde

# PNG-rastrering
PNG_PX_PER_UNIT = 0.75      # 3 px per mm for beslagglyfene
PICTO_PX_PER_UNIT = 13.333  # 24-rutenettet -> 320 px per ikon

# Isometrisk dybderetning (x, y) per mm dybde. y peker nedover i SVG.
ISO_DX = 0.52
ISO_DY = -0.29

# Piktogrammene ligger på Lucides rutenett: 24x24 brukerenheter. Lucide tegner
# for skjerm og setter streken til 2 enheter — 8,3 % av ikonhøyden. Trykt i
# 19 mm blir det 1,6 mm, og da klumper motivet seg: to-personer og veggfeste-ja
# gikk nesten igjen i seg selv. 1,25 enheter er ca. 1,0 mm på siden — i slekt
# med den svarte streken i steg­tegningene ved siden av, og fortsatt 0,5 mm om
# et ikon settes så lite som 10 mm.
#
# Streken settes HER, på gruppen ikonkroppen legges i, og ikke i ikonfilene:
# de vendorte Lucide-filene skal ligge som de kom, og hele settet — Lucide og
# hanna — skal ha nøyaktig samme vekt.
PICTO_SIZE = 24
PICTO_STROKE = 1.25

_STOPWORDS = {
    "forsenket", "torx", "varmforsinket", "elforsinket", "etter", "av",
    "bøyd", "boyd", "i", "eller", "og", "med", "for", "til", "pk", "stk",
}


# --------------------------------------------------------------------------
# Navn -> slug
# --------------------------------------------------------------------------

def _ascii_fold(text: str) -> str:
    """Norsk/typografisk tekst -> ren ascii i småbokstaver."""
    repl = {
        "æ": "ae", "ø": "o", "å": "a",
        "Æ": "ae", "Ø": "o", "Å": "a",
        "×": "x", "⌀": "d",
        "–": "-", "—": "-", "’": "", "'": "",
    }
    out = []
    for ch in text:
        if ch in repl:
            out.append(repl[ch])
            continue
        dec = unicodedata.normalize("NFKD", ch)
        dec = "".join(c for c in dec if not unicodedata.combining(c))
        out.append(dec)
    return "".join(out).lower()


_SIZE_RE = re.compile(r"^(?:m|d)?\d+(?:[.,]\d+)?(?:x\d+(?:[.,]\d+)?)*$")


def _tokens(name: str) -> list[str]:
    folded = _ascii_fold(name)
    folded = folded.replace("/", " ").replace("(", " ").replace(")", " ")
    folded = folded.replace("+", " ")
    raw = re.split(r"[\s,;]+", folded)
    return [t.strip(".:-") if t.strip(".:-") else t for t in raw if t.strip(".:-")]


def _size_token(tokens: list[str]) -> str | None:
    for tok in tokens:
        if any(c.isdigit() for c in tok) and _SIZE_RE.match(tok):
            return tok
    return None


def _trim_size(size: str) -> str:
    """Beholder maks tre talledd og fjerner desimaler: 90x90x65x2,5 -> 90x90x65."""
    prefix = ""
    body = size
    if body and body[0] in "md":
        prefix, body = body[0], body[1:]
    groups = body.split("x")
    keep = groups[:3]
    if len(keep) > 1:
        keep = [g for g in keep if "," not in g and "." not in g] or keep[:1]
    cleaned = [g.replace(",", "-").replace(".", "-") for g in keep]
    return prefix + "x".join(cleaned)


def slug(name: str) -> str:
    """Stabil, filsystemtrygg ascii-slug for et handelsnavn.

    "Treskrue 6x90 forsenket Torx" -> "treskrue-6x90"
    """
    toks = _tokens(name)
    if not toks:
        return "ukjent"
    kind = toks[0]
    size = _size_token(toks[1:] if len(toks) > 1 else [])
    parts = [kind]
    if size:
        parts.append(_trim_size(size))
    else:
        for tok in toks[1:]:
            if tok in _STOPWORDS or any(c.isdigit() for c in tok):
                continue
            parts.append(tok)
            break
    out = "-".join(parts)
    out = re.sub(r"[^a-z0-9]+", "-", out).strip("-")
    return out or "ukjent"


# --------------------------------------------------------------------------
# SVG-hjelpere
# --------------------------------------------------------------------------

def _f(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def _pts(points) -> str:
    return " ".join(f"{_f(x)},{_f(y)}" for x, y in points)


def path(d: str, **kw) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<path d="{d}"{extra}/>'


def poly(points, close: bool = False, **kw) -> str:
    d = "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in points)
    if close:
        d += " Z"
    return path(d, **kw)


def line(x1, y1, x2, y2, **kw) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return (f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" '
            f'y2="{_f(y2)}"{extra}/>')


def circle(cx, cy, r, **kw) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}"{extra}/>'


def ellipse(cx, cy, rx, ry, **kw) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return (f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" '
            f'ry="{_f(ry)}"{extra}/>')


def rect(x, y, w, h, rx=0.0, **kw) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    r = f' rx="{_f(rx)}"' if rx else ""
    return (f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" '
            f'height="{_f(h)}"{r}{extra}/>')


def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def svg_document(title: str, vb_w: float, vb_h: float, body: str,
                 stroke_w: float) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '
        f'{_f(vb_w)} {_f(vb_h)}" preserveAspectRatio="xMinYMid meet">\n'
        f'  <title>{_esc(title)}</title>\n'
        f'  <g fill="none" stroke="{INK}" stroke-width="{_f(stroke_w)}" '
        'stroke-linecap="round" stroke-linejoin="round">\n'
        f'{body}\n'
        '  </g>\n'
        '</svg>\n'
    )


# --------------------------------------------------------------------------
# Geometrihjelpere
# --------------------------------------------------------------------------

def _bbox(points) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


# --------------------------------------------------------------------------
# Skruer - ÉN SILHUETT, ETT STED
# --------------------------------------------------------------------------
# Katalogglyfen i beslagtabellen og skruen som tegnes inn i en stegside er det
# samme objektet, og de er nå den samme KONTUREN. `screw_profile()` er den ene
# beskrivelsen av hvordan en forsenket treskrue ser ut fra siden - i skruens
# egne koordinater, hodeflaten i x = 0, drivaksen på y = 0, spissen i
# x = length - og begge kallerne legger den inn i sitt eget system.
#
# Det var to før: tools/render_lineart.py hadde sin egen sju-punkts kapsel med
# en flens i den ene enden og en pigg i den andre, og på en stegside leste den
# som en PIL, ikke som en skrue - mens panelet ved siden av viste den ekte
# silhuetten. To billedspråk for én ting er den ene feilen en
# monteringsanvisning ikke har råd til, for leseren bruker formen til å kjenne
# igjen delen. Nå finnes formen ett sted, og det som skiller sidene fra
# hverandre er BARE hva rasteret har plass til (se `thread_pitch`).
HEAD_DIA_RATIO = 1.95       # hodediameter, i nominelle diametre
CORE_DIA_RATIO = 0.72       # gjengens kjerne, samme
TIP_RATIO = 1.7             # spissens lengde, samme
HEAD_H_FRAC = 0.92          # forsenkningens høyde, av (hode - kjerne)/2


def _head_dia(d: float) -> float:
    return HEAD_DIA_RATIO * d


# HVOR FIN EN GJENGE FÅR TEGNES - samme regel som fyllkoden har, og av samme
# grunn (se FILL_MIN_PERIOD_PX). En gjenge er en tekstur, og en tekstur koder
# bare så lenge leseren ser de enkelte tennene. Under et par piksler per tann
# folder kantutjevningen tann og bunn sammen til en grå ullen kant, og da har
# siden ikke fått en skrue - den har fått støy langs en kontur.
#
# Perioden er derfor den GROVESTE av formkravet (1,15 x diameteren, som er den
# overtydelige stigningen glyfen alltid har tegnet) og oppløsningskravet
# (en TANN, altså en halv periode, aldri under THREAD_MIN_PX piksler der
# flaten faktisk vises). Og blir det da for få tenner igjen på den gjengede
# strekningen til at det leses som en gjenge, tegnes ingen: silhuetten faller
# tilbake på sin egen omhyllingskurve - samme hode, samme kjerne, samme spiss,
# bare uten bølgen. Det er én nedgradering, ikke et annet billedspråk.
THREAD_MIN_PX = 4.5         # én tann - en halv periode - der den vises minst
THREAD_MIN_PITCHES = 2.5    # færre hele omdreininger enn dette: ingen gjenge


def thread_pitch(d: float, threaded_len: float,
                 px_per_unit: float | None = None) -> float:
    """Gjengedelingen en tegnet skrue får, eller 0,0 der rasteret spiser den.

    `d`            SANN diameter, i kallerens egne enheter
    `threaded_len` hvor lang den gjengede strekningen er, samme enheter
    `px_per_unit`  piksler per enhet der skruen vises minst; None = spør ikke

    SANN diameter, ikke den tegnede. En stegside overdriver bredden på et
    festemiddel og lar LENGDEN stå - det er hele licensen (layout.SCREW_FATTEN)
    - og stigningen er et mål LANGS skruen. Regnes den av den feite bredden,
    dobles den sammen med bredden mens skruen beholder sin lengde, og en 5x40
    som i katalogglyfen har sju omdreininger får to på siden. Da er det ikke en
    gjenge lenger, det er tre hakk. Delingen er den samme 1,15 x d overalt, og
    det er derfor skruen i tegningen og skruen i tabellen ser like ut.
    """
    pitch = max(1.15 * d, 5.5)
    if px_per_unit:
        pitch = max(pitch, 2.0 * THREAD_MIN_PX / px_per_unit)
    if threaded_len < pitch * THREAD_MIN_PITCHES:
        return 0.0
    return pitch


def screw_style(name: str) -> tuple[float, bool]:
    """(gjengeandel, spiss) for ett handelsnavn - den samme oppdelingen
    build_fastener() gjør, slik at skruen på tegningen er den skruen glyfen
    viser og ikke en generisk pinne (PRAKSIS §1)."""
    key = _ascii_fold(name)
    if key.startswith("senkhodeskrue"):
        return (0.86, False)
    if key.startswith("veggfeste"):
        return (0.66, True)
    return (0.70, True)


def screw_profile(d: float, length: float, threaded_frac: float = 0.72,
                  pointed: bool = True, pitch: float | None = None):
    """Silhuetten som punktliste, lukket, i skruens egne koordinater.

    `pitch`  None = glyfens egen grove deling; 0 = ingen gjenge, bare
             omhyllingskurven; ellers den delingen kalleren har regnet ut med
             `thread_pitch()`.
    """
    D = _head_dia(d)                    # hodediameter
    ds = CORE_DIA_RATIO * d             # kjernediameter
    hh = (D - ds) / 2.0 * HEAD_H_FRAC   # hodehøyde, forsenket 90 grader
    tip = TIP_RATIO * d if pointed else 0.0
    smooth_end = hh + (length - hh) * (1.0 - threaded_frac)
    xs = min(smooth_end, length)
    # Grov gjengedeling: manualen viser glyfene rundt 1 px per mm, så en
    # naturtro stigning ville gå i grøt. Tennene tegnes derfor overtydelige.
    if pitch is None:
        pitch = max(1.15 * d, 5.5)
    x_taper = length - tip

    def env(x, radius):
        if not pointed or x <= x_taper:
            return radius
        f = max(0.0, (length - x) / max(tip, 1e-6))
        return radius * f

    top = [(0.0, -D / 2.0), (hh, -ds / 2.0), (xs, -ds / 2.0)]
    if pitch <= 0.0:
        # Ingen gjenge: skaftet går ut i krestdiameteren og spissen tar det
        # derfra. Samme omhyllingskurve som den gjengede har, uten bølgen.
        top.append((xs, -env(xs, d / 2.0)))
        if pointed:
            top.append((x_taper, -d / 2.0) if x_taper > xs
                       else (xs, -env(xs, d / 2.0)))
        else:
            top.append((length, -d / 2.0))
    else:
        k = 0
        x = xs
        while x < length - 1e-6:
            x = min(xs + k * pitch / 2.0, length)
            radius = ds / 2.0 if k % 2 == 0 else d / 2.0
            top.append((x, -env(x, radius)))
            k += 1
            if k > 4000:
                break
    if pointed:
        top.append((length, 0.0))
    else:
        top.append((length, -ds / 2.0))

    bottom = [(x, -y) for (x, y) in reversed(top)]
    if not pointed:
        outline = top + bottom
    else:
        outline = top + bottom[1:]
    return outline, (0.0, -D / 2.0, length, D / 2.0)


def _screw_body(d: float, length: float, threaded_frac: float = 0.72,
                pointed: bool = True):
    """Skrue liggende, hode til venstre, spiss til høyre. Origo i hodets
    ytterflate, aksen på y = 0. Returnerer (elementer, bbox)."""
    D = _head_dia(d)
    hh = (D - CORE_DIA_RATIO * d) / 2.0 * HEAD_H_FRAC
    outline, _bb = screw_profile(d, length, threaded_frac, pointed)

    elems = [poly(outline, close=True)]

    # Torx-merke på hodet: et sekslobet uttak. Ved liten gjengivelse ville
    # eikene gå i ett, så det som blir igjen er selve uttaksringen.
    r = 0.20 * D
    cx = max(hh * 0.5, r + 0.2)
    lobe = []
    for i in range(36):
        a = math.radians(i * 10)
        rr = r * (1.0 + 0.20 * math.cos(6 * a))
        lobe.append((cx + rr * math.cos(a), rr * math.sin(a)))
    elems.append(poly(lobe, close=True, stroke_width=_f(DETAIL_MM)))

    return elems, (0.0, -D / 2.0, length, D / 2.0)


def glyph_wood_screw(d: float, length: float):
    return _screw_body(d, length, threaded_frac=0.70, pointed=True)


def glyph_machine_screw_set(d: float = 6.0, length: float = 30.0):
    """Senkhodeskrue + skive + låsemutter, tre motiver ved siden av hverandre."""
    elems, (x0, y0, x1, y1) = _screw_body(d, length, threaded_frac=0.86,
                                          pointed=False)
    gap = 5.0

    # Skive M6: ytre 12, indre 6,4. Sett rett på, med hullet.
    w_r = 6.4
    wx = x1 + gap + w_r
    elems.append(circle(wx, 0.0, w_r))
    elems.append(circle(wx, 0.0, 3.4, stroke_width=_f(DETAIL_MM)))

    # Sekskantmutter M6: nøkkelvidde 10 -> hjørneradius 5,8.
    nx = wx + w_r + gap + 6.4
    R = 6.4
    hexpts = [(nx + R * math.cos(math.radians(30 + i * 60)),
               R * math.sin(math.radians(30 + i * 60))) for i in range(6)]
    elems.append(poly(hexpts, close=True))
    elems.append(circle(nx, 0.0, 3.4, stroke_width=_f(DETAIL_MM)))

    return elems, (x0, min(y0, -R), nx + R, max(y1, R))


def glyph_wall_fixing(d: float = 8.0, length: float = 100.0):
    """Lang veggskrue pluss ribbet plugg."""
    elems, (x0, y0, x1, y1) = _screw_body(d, length, threaded_frac=0.66,
                                          pointed=True)
    px = x1 + 7.0
    plug_len = 50.0
    r0, r1 = 5.0, 4.2
    lip = 6.2
    body = [
        (px, -lip), (px + 2.0, -lip), (px + 2.0, -r0),
        (px + plug_len - 6.0, -r1), (px + plug_len - 1.5, -2.0),
        (px + plug_len, 0.0),
        (px + plug_len - 1.5, 2.0), (px + plug_len - 6.0, r1),
        (px + 2.0, r0), (px + 2.0, lip), (px, lip),
    ]
    elems.append(poly(body, close=True))
    # Ribber.
    for i in range(4):
        bx = px + 13.0 + i * 9.0
        f = (bx - px) / plug_len
        rr = r0 + (r1 - r0) * f
        elems.append(poly([(bx, -rr), (bx - 4.4, -rr - 3.2)]))
        elems.append(poly([(bx, rr), (bx - 4.4, rr + 3.2)]))
    # Splittspor.
    elems.append(line(px + 9.0, 0.0, px + plug_len - 5.0, 0.0,
                      stroke_width=_f(DETAIL_MM)))
    return elems, (x0, min(y0, -lip - 3.2), px + plug_len, max(y1, lip + 3.2))


# --------------------------------------------------------------------------
# Beslag
# --------------------------------------------------------------------------

def glyph_angle_bracket(a: float, c: float, b: float, t: float,
                        rib: bool = False):
    """Vinkelbeslag i isometri. a = stående ben, c = liggende ben,
    b = beslagets bredde, t = godstykkelse.

    Betrakteren står foran, til høyre og litt over: synlige flater er de som
    vender mot +y (front), +z (topp) og +x (høyre side). Flatene males bakfra
    og fram med hvit fyll, slik at skjulte kanter forsvinner av seg selv.
    """

    def P(x, y, z):
        return (x - y * ISO_DX, y * (-ISO_DY) - z)

    # Bakerst først, nærmest sist.
    quads = [
        [P(b, 0, 0), P(b, 0, a), P(b, t, a), P(b, t, 0)],      # stående, høyre
        [P(0, 0, a), P(b, 0, a), P(b, t, a), P(0, t, a)],      # stående, topp
        [P(0, t, 0), P(b, t, 0), P(b, t, a), P(0, t, a)],      # stående, front
        [P(b, t, 0), P(b, c, 0), P(b, c, t), P(b, t, t)],      # liggende, høyre
        [P(0, t, t), P(b, t, t), P(b, c, t), P(0, c, t)],      # liggende, topp
        [P(0, c, 0), P(b, c, 0), P(b, c, t), P(0, c, t)],      # liggende, front
    ]
    elems = [poly(q, close=True, fill="#fff") for q in quads]

    # Ribben først, ellers spiser den hvite fyllen hullene.
    if rib:
        elems.append(poly([P(b / 2.0, t, a * 0.50),
                           P(b / 2.0, t, t),
                           P(b / 2.0, c * 0.50, t)], close=True, fill="#fff"))

    rh = min(3.4, b * 0.10 + 1.8)
    det = _f(DETAIL_MM)
    if rib:
        # Tungt beslag: hullene står parvis på hver side av ribben.
        cols = (0.26, 0.74)
        for xf in cols:
            for zf in (0.42, 0.76):
                cx, cy = P(b * xf, t, a * zf)
                elems.append(circle(cx, cy, rh, stroke_width=det))
            cx, cy = P(b * xf, t + (c - t) * 0.62, t)
            elems.append(ellipse(cx, cy, rh * 1.05, rh * 0.5,
                                 stroke_width=det))
    else:
        for zf in (0.40, 0.74):
            cx, cy = P(b / 2.0, t, a * zf)
            elems.append(circle(cx, cy, rh, stroke_width=det))
        for yf in (0.42, 0.80):
            cx, cy = P(b / 2.0, t + (c - t) * yf, t)
            elems.append(ellipse(cx, cy, rh * 1.05, rh * 0.5,
                                 stroke_width=det))

    pts = [p for q in quads for p in q]
    return elems, _bbox(pts)


def glyph_felt_pad(dia: float = 40.0):
    """Filtknott / møbeltapp: lav skive i oppriss med senterpinne opp."""
    r = dia / 2.0
    h = 11.0
    k = 3.2
    elems = [
        path(f"M {_f(-r)} 0 L {_f(-r)} {_f(-h + k)} "
             f"Q {_f(-r)} {_f(-h)} {_f(-r + k)} {_f(-h)} "
             f"L {_f(r - k)} {_f(-h)} "
             f"Q {_f(r)} {_f(-h)} {_f(r)} {_f(-h + k)} "
             f"L {_f(r)} 0 Z"),
        line(-r + 2.0, -3.6, r - 2.0, -3.6, stroke_width=_f(DETAIL_MM)),
    ]
    pin_r, pin_h = 3.0, 10.0
    elems.append(path(
        f"M {_f(-pin_r)} {_f(-h)} L {_f(-pin_r)} {_f(-h - pin_h + 1.5)} "
        f"Q {_f(-pin_r)} {_f(-h - pin_h)} {_f(-pin_r + 1.2)} {_f(-h - pin_h)} "
        f"L {_f(pin_r - 1.2)} {_f(-h - pin_h)} "
        f"Q {_f(pin_r)} {_f(-h - pin_h)} {_f(pin_r)} {_f(-h - pin_h + 1.5)} "
        f"L {_f(pin_r)} {_f(-h)}"))
    return elems, (-r, -h - pin_h, r, 0.0)


# --------------------------------------------------------------------------
# Klassifisering: handelsnavn -> tegning
# --------------------------------------------------------------------------

def _dims(name: str) -> list[float]:
    folded = _ascii_fold(name)
    tok = _size_token(_tokens(name))
    if not tok:
        return []
    tok = tok.lstrip("md")
    out = []
    for part in tok.split("x"):
        try:
            out.append(float(part.replace(",", ".")))
        except ValueError:
            pass
    del folded
    return out


def build_fastener(name: str):
    """Velger og bygger riktig glyf. Ukjent navn -> generisk treskrue."""
    key = _ascii_fold(name)
    dims = _dims(name)

    if key.startswith("treskrue"):
        d = dims[0] if len(dims) > 0 else 5.0
        L = dims[1] if len(dims) > 1 else 50.0
        return glyph_wood_screw(d, L)

    if key.startswith("senkhodeskrue"):
        d = dims[0] if len(dims) > 0 else 6.0
        L = dims[1] if len(dims) > 1 else 30.0
        return glyph_machine_screw_set(d, L)

    if key.startswith("vinkelbeslag"):
        a = dims[0] if len(dims) > 0 else 40.0
        c = dims[1] if len(dims) > 1 else a
        b = dims[2] if len(dims) > 2 else a
        t = dims[3] if len(dims) > 3 else 2.0
        return glyph_angle_bracket(a, c, b, max(t, 2.0), rib=a >= 70.0)

    if key.startswith("veggfeste"):
        d = dims[0] if len(dims) > 0 else 8.0
        L = dims[1] if len(dims) > 1 else 100.0
        return glyph_wall_fixing(d, L)

    if key.startswith("filtknott") or "mobeltapp" in key:
        dia = dims[0] if dims else 40.0
        return glyph_felt_pad(dia)

    # Fallback.
    d = dims[0] if len(dims) > 0 else 5.0
    L = dims[1] if len(dims) > 1 else 50.0
    if not (2.0 <= d <= 12.0):
        d = 5.0
    if not (10.0 <= L <= 200.0):
        L = 50.0
    return glyph_wood_screw(d, L)


def is_screw_glyph(name: str) -> bool:
    """Bærer denne glyfen en skruesilhuett fyllkoden kan legges i?

    Beslagene gjør ikke. En vinkel er allerede tegnet som en heldekt plate i
    isometri, og et mønster oppå den ville lest som en tredje slags flate -
    de beholder platelooken sin, slik snittene i innsettpanelet også gjør.
    """
    key = _ascii_fold(name)
    return not (key.startswith("vinkelbeslag")
                or key.startswith("filtknott") or "mobeltapp" in key)


def _filled(elem: str, paint: str) -> str:
    """Samme element, men med fyll. Konturen står som den står."""
    return elem[:-2].rstrip() + f' fill="{paint}"/>'


def coded_slug(name: str, code: str | None) -> str:
    """Filnavnet en glyf med fyllkode får. Den åpne koden er glyfen selv."""
    base = slug(name)
    return base if code in (None, "open") else f"{base}-{code}"


def fastener_svg(name: str, code: str | None = None) -> str:
    elems, (x0, y0, x1, y1) = build_fastener(name)
    w_mm = (x1 - x0) + 2 * MARGIN_MM
    h_mm = max(BASE_H_MM, (y1 - y0) + 2 * MARGIN_MM)
    defs = ""
    if code not in (None, "open") and is_screw_glyph(name):
        dims = _dims(name)
        d = dims[0] if dims else 5.0
        # EGEN PREFIKS PER FIL. Glyfen blir lagt inn hel i stegsidens
        # innsettpanel, og den siden har sine egne mønstre med de samme
        # navnene. To elementer med samme id i ett dokument er ikke to
        # mønstre - det første vinner - så en delt prefiks lot sidens
        # periode gjelde i glyfen og glyfens i naboglyfen. Filnavnet er
        # unikt og deterministisk, så det er prefiksen.
        prefix = "fyll-" + coded_slug(name, code)
        # Mønsteret ligger inne i `scale(SCALE)`-gruppa, altså i
        # MILLIMETER, og lerretet er h_mm høyt. Settes glyfen så lite som
        # manualen noen gang setter den, blir det GLYPH_MIN_PX / h_mm
        # piksler per millimeter - og det er den skalaen perioden må tåle.
        base, t = fill_metrics(d, GLYPH_MIN_PX / h_mm)
        defs = "  " + fill_defs(base, t, prefix) + "\n"
        elems = [_filled(elems[0], fill_paint(code, prefix))] + list(elems[1:])
    tx = MARGIN_MM - x0
    ty = (h_mm - (y1 - y0)) / 2.0 - y0
    body = (f'    <g transform="scale({_f(SCALE)}) '
            f'translate({_f(tx)} {_f(ty)})" stroke-width="{_f(STROKE_MM)}">\n'
            + "\n".join("      " + e for e in elems)
            + "\n    </g>")
    return svg_document(name, w_mm * SCALE, h_mm * SCALE, defs + body,
                        STROKE_MM * SCALE)


# --------------------------------------------------------------------------
# Notasjonsforklaring og merkebokstaver
# --------------------------------------------------------------------------
#
# Beslagsiden skriver "5×60" og "100x" uten å si hva tallene er. Forklaringen
# under er ett eneste eksemplar tegnet stort, med målsetting på de tre
# størrelsene: lengden langs skaftet, tykkelsen tvers over gjengene, og
# antallet. Den står som et smalt bånd over beslagtabellen.
#
# Merkebokstavene (Ⓐ, Ⓑ, ...) settes på stegsidene der ett steg bruker mer
# enn én type festemiddel: samme bokstav på pila i tegningen som i tabellen.

FONT_STACK = "Helvetica, Arial, sans-serif"

LEGEND_SCALE = 9.0          # brukerenheter per millimeter i forklaringen
LEGEND_TEXT = 41.0          # tekststørrelse, brukerenheter
LEGEND_HAIR = 2.4           # målelinjer - tynnere enn motivet
LEGEND_STROKE = 8.0         # skruens hovedkontur, brukerenheter
LEGEND_DETAIL = 5.0         # skruens innvendige detalj

# The one home of the badge alphabet. tools/gen_doc_tables.py assigns the
# letters to a step's fastener rows and tools/render_lineart.py draws them on
# the page; both import this name rather than repeating the string, because two
# files that have to agree about a value are one file too many (PRAKSIS §1).
BADGE_ALPHABET = "ABCDEFGH"

# --------------------------------------------------------------------------
# FYLLKODEN - bokstaven, en gang til, som mønster
# --------------------------------------------------------------------------
# Merkebokstaven er den ene knytningen mellom en skrue på tegningen og en rad
# i tabellen, og den er et lite tegn i en ring. Leseren som holder to skruer i
# hånda og ser på et hjørne med fire festemidler i, skal slippe å lese den for
# å se HVILKEN AV DE FIRE en gitt skrue er. Derfor bærer skruen kodingen én
# gang til, i selve silhuetten: samme bokstav, samme fyll, overalt den
# opptrer - i stegtegningen, i innsettpanelet og i tabellen under bildet.
#
# Redundant koding er poenget. Formen alene (lengde, tykkelse) skiller 5x40
# fra 6x120, men ikke 6x80 fra 6x90; bokstaven alene krever at leseren finner
# og leser et 5 mm tegn; sammen holder de hverandre oppe, og ingen av dem
# trenger farge - dette er en svart-hvit manual, og et fyllmønster fungerer
# like godt for en fargeblind leser som for en kopimaskin.
#
# HVA SOM ER FYLT. Ikke hodet alene: et forsenket hode er en 5 mm lang flens
# på tegningen (7 px på siden), og der får ingen mønster plass. Hele
# silhuetten fylles - hode, skaft og spiss - for det er den flaten leseren
# ser.
#
# Settet er valgt etter kontrastprøven, ikke etter smak; se
# docs/preview/fyllkontrast.png og PRAKSIS §4. Prøven avgjorde to ting:
#
#   * hodet alene kan ikke bære koden. Et forsenket hode er en flens på 5 mm
#     langs skruen — 7 px på siden — og der er alle fem kandidatene like.
#     Hele silhuetten fylles.
#   * krysskraveringen må ha grovere rute enn skraveringen, ellers er de to
#     bare to gråtoner ved 19 px bredde.
#
# REKKEFØLGEN er heller ikke smak. Bokstavene deles ut etter antall, flest
# først, så Ⓐ er den skruen siden har flest av: den beholder den åpne, lyse
# silhuetten, for seksten heldekte skruer ville gjort siden svart og skjult
# nettopp den lengdeforskjellen fyllkoden skal støtte. Den heldekte er sist,
# der den er sjeldnest — og på to av de fire sidene med bokstaver er den siste
# raden et vinkelbeslag, som allerede tegnes som en heldekt plate. Koden
# lander altså der fyllet var fra før.
FILL_CODES = ("open", "hatch", "cross", "solid")

# Hvert mønster som en tile: (elementer i en periode x periode-rute, rotasjon).
# `t` er strekbredden. Mønstrene tegnes i SIDENS koordinatsystem, ikke i
# skruens, så to skruer med samme kode ser like ut uansett hvilken vei de
# står - det er koden som skal leses, ikke retningen.
#
# Hvert mønster har sin egen periode, som et multiplum av grunnperioden.
# Krysskraveringen er den grove: to retninger på samme finhet som den enkle
# skraveringen blir en grå flate ved 19 px bredde, og da koder den ingenting.
# Grovere rute gir den en form leseren ser med én gang - ruter, ikke gråtone.
PATTERN_PERIOD = {"hatch": 1.0, "cross": 1.45, "dots": 1.15}

# HVOR FIN PERIODEN FÅR VÆRE - og dette er regelen, ikke et tall noen likte.
#
# Et mønster koder bare så lenge leseren ser de enkelte strekene. Under et par
# piksler per periode folder rasterets kantutjevning strek og mellomrom sammen
# til én gråtone, og da er Ⓑ og Ⓒ det samme festemiddelet. Det var nøyaktig det
# som skjedde: glyfen i stegets egen festetabell bandt perioden til skruens
# SANNE diameter (0,24 x d = 1,44 mm for en 6 mm skrue) mens manualen setter
# den samme glyfen 30 px høy på et lerret som er 30 mm - altså 1 px per mm.
# 1,44 px periode med 0,48 px strek er ingen skravering, det er 33 % grått.
#
# Perioden velges derfor aldri fritt. Den er den GROVESTE av to krav:
#
#   * FORMKRAVET   - flaten den skal dekke, delt på hvor mange striper vi vil
#                    ha over den. Det er dette kravet som binder på stegsiden,
#                    der skruen er tegnet feit og sitter på en stor side.
#   * OPPLØSNINGSKRAVET - én periode skal aldri bli mindre enn
#                    FILL_MIN_PERIOD_PX piksler DER FLATEN FAKTISK VISES. Det
#                    er dette kravet som binder i tabellglyfen og i
#                    forklaringen, der hele skruen er noen få piksler tykk.
#
# Kalleren oppgir begge tallene i sitt eget koordinatsystem: `span` er bredden
# mønsteret skal krysse, `px_per_unit` er hvor mange piksler én enhet blir når
# flaten settes SÅ LITE SOM MANUALEN NOEN GANG SETTER DEN. Da er svaret riktig
# på hver eneste flate uten at noen av dem kjenner de andres skala.
#
# Tallene under er lest av kontrastprøven (docs/preview/fyllkontrast.png),
# ikke gjettet: 2,8 striper er det stegsidens hånd-innstilte periode allerede
# svarte til (15 mm tegnet bredde / 5,36 mm periode), og 5 px er der prøven
# viser at skraveringen slutter å være grå og blir striper igjen.
FILL_STRIPES = 2.8          # perioder over flaten mønsteret skal dekke
FILL_LINE_FRAC = 0.384      # én strek, som andel av perioden
FILL_MIN_PERIOD_PX = 5.0    # én periode, i piksler, på det minste den vises
FILL_MIN_LINE_PX = 1.5      # én strek, samme sted

# Den minste manualen noen gang setter en festemiddelglyf: raden i stegets
# egen festetabell, `height="30"` i docs/MONTERING.md. Den står her fordi det
# er denne filen som må kjenne den for å velge perioden, og
# tools/gen_doc_tables.py henter den herfra i stedet for å skrive 30 en gang
# til (PRAKSIS §1).
GLYPH_MIN_PX = 30.0
# Og den største: fyllkodeforklaringen på beslagsiden, som er der koden læres.
FILL_LEGEND_PX = 96.0


def fill_metrics(span: float, px_per_unit: float) -> tuple[float, float]:
    """(grunnperiode, strekbredde) for én flate, i kallerens egne enheter.

    `span`         bredden mønsteret skal krysse
    `px_per_unit`  piksler per enhet der flaten vises minst
    """
    assert span > 0.0 and px_per_unit > 0.0, (
        f"fyllmønsteret kan ikke måles mot span={span} px_per_unit="
        f"{px_per_unit}")
    period = max(span / FILL_STRIPES, FILL_MIN_PERIOD_PX / px_per_unit)
    return period, max(period * FILL_LINE_FRAC,
                       FILL_MIN_LINE_PX / px_per_unit)


def _fill_tile(kind: str, period: float, t: float) -> tuple[str, str]:
    """(innholdet i mønsterruta, patternTransform) for én fyllkode."""
    if kind == "hatch":
        return (f'<path d="M {_f(period / 2)} 0 V {_f(period)}" '
                f'stroke="{INK}" stroke-width="{_f(t)}" fill="none"/>',
                "rotate(45)")
    if kind == "cross":
        return (f'<path d="M {_f(period / 2)} 0 V {_f(period)} '
                f'M 0 {_f(period / 2)} H {_f(period)}" '
                f'stroke="{INK}" stroke-width="{_f(t)}" fill="none"/>',
                "rotate(45)")
    if kind == "dots":
        return (f'<circle cx="{_f(period / 2)}" cy="{_f(period / 2)}" '
                f'r="{_f(t * 0.95)}" fill="{INK}" stroke="none"/>', "")
    raise KeyError(kind)


def fill_defs(base: float, t: float, prefix: str = "fyll") -> str:
    """<defs> med ett <pattern> per fyllkode som trenger ett."""
    out = []
    for kind in ("hatch", "cross", "dots"):
        period = base * PATTERN_PERIOD[kind]
        body, xform = _fill_tile(kind, period, t)
        tf = f' patternTransform="{xform}"' if xform else ""
        out.append(f'<pattern id="{prefix}-{kind}" width="{_f(period)}" '
                   f'height="{_f(period)}" patternUnits="userSpaceOnUse"'
                   f'{tf}>{body}</pattern>')
    return "<defs>" + "".join(out) + "</defs>"


def fill_paint(kind: str | None, prefix: str = "fyll") -> str:
    """Malingen en fyllkode gir: en farge for de to flate, en url for resten."""
    if kind is None or kind == "open":
        return "#ffffff"
    if kind == "solid":
        return INK
    return f"url(#{prefix}-{kind})"


def fill_code(letter: str | None) -> str | None:
    """Fyllkoden en merkebokstav bærer, eller None når siden ikke har
    bokstaver i det hele tatt - da er det bare én type på siden, og en kode
    som bare har én verdi koder ingenting."""
    if not letter or letter not in BADGE_ALPHABET:
        return None
    i = BADGE_ALPHABET.index(letter)
    return FILL_CODES[i] if i < len(FILL_CODES) else None


# --------------------------------------------------------------------------
# NÅR KODEN SLÅS PÅ - og at den ikke alltid gjør det
# --------------------------------------------------------------------------
# Fyllkoden er ikke gratis. Den legger et mønster i hver eneste skrue på siden,
# og et mønster er blekk som ikke er tegning: en side der silhuettene skiller
# seg fra hverandre helt av seg selv blir ikke tydeligere av å bli kodet, den
# blir travlere. Koden ble kjøpt for ett bestemt problem — to skruer på den
# samme siden som er så nær hverandre i størrelse at formen ikke skiller dem —
# og den skal derfor bare betales der det problemet finnes.
#
# TVETYDIG AV FORM er definert her, i tall, slik at spørsmålet «trenger denne
# siden koden?» har ett svar som kan regnes ut av leddataene og ikke et som
# avgjøres av hvem som ser på siden:
#
#   * lengdeforskjellen er under 25 % av den lengste, OG
#   * diameterne er i samme klasse (like) eller skiller seg med høyst 1 mm.
#
# Begge må holde. En 5x40 ved siden av en 6x120 er tre ganger lengden og det er
# ingen konkurranse; en 5x70 ved siden av en 6x80 er 12,5 % og ett
# diametertrinn, og det er nettopp den avlesningen fyllkoden ble kjøpt for.
# (Diameterleddet er skrevet som «samme klasse ELLER høyst 1 mm»; den første
# halvdelen er inneholdt i den andre, og den står der fordi det er den måten
# regelen leses på: skruer i samme grovhet, som bare skiller seg i lengde.)
#
# REGELEN GJELDER SIDEN, IKKE PARET. Slår den til, kodes HELE settet på siden.
# Å kode bare de to som ligner ville gitt siden to slags skruer — kodede og
# ukodede — og det er en tredje opplysning leseren ikke er fortalt, altså sin
# egen forvirring.
AMBIG_LEN_FRAC = 0.25       # lengdeforskjell, som andel av den lengste
AMBIG_DIAM_MM = 1.0         # diameterforskjell, i millimeter


def screw_dims(name: str) -> tuple[float, float] | None:
    """(diameter, lengde) for et festemiddel med akse, ellers None.

    Beslagene har ingen: en vinkel er en plate, ikke en silhuett med lengde,
    og den står utenfor både fyllkoden og regelen som slår den på.
    """
    if not is_screw_glyph(name):
        return None
    dims = _dims(name)
    if len(dims) < 2:
        return None
    return dims[0], dims[1]


def ambiguous_pairs(names) -> list[tuple[str, str, float, float]]:
    """Parene på én side som formen ikke skiller.

    -> [(navn_a, navn_b, lengdeandel, diameterforskjell), ...], sortert på
    navn slik at rapporten kommer ut likt hver gang.
    """
    sized = [(n, screw_dims(n)) for n in sorted(set(names))]
    sized = [(n, d) for n, d in sized if d]
    out = []
    for i, (na, (da, la)) in enumerate(sized):
        for nb, (db, lb) in sized[i + 1:]:
            longest = max(la, lb)
            if longest <= 0.0:
                continue
            frac = abs(la - lb) / longest
            ddiff = abs(da - db)
            if frac < AMBIG_LEN_FRAC and ddiff <= AMBIG_DIAM_MM:
                out.append((na, nb, frac, ddiff))
    return out


def shape_ambiguous(names) -> bool:
    """Trenger en side med disse festemidlene fyllkoden?"""
    return bool(ambiguous_pairs(names))


def _text(x, y, s, size, anchor="start", weight="normal") -> str:
    return (f'<text x="{_f(x)}" y="{_f(y)}" font-family="{FONT_STACK}" '
            f'font-size="{_f(size)}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{INK}" stroke="none">'
            f'{_esc(s)}</text>')


def _arrow_head(tip, direction, size=11.0, w=LEGEND_HAIR) -> str:
    """Åpen pilspiss med spissen i `tip`, pekende `direction`."""
    ux, uy = direction
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    legs = []
    for turn in (2.55, -2.55):
        bx = math.cos(turn) * ux - math.sin(turn) * uy
        by = math.sin(turn) * ux + math.cos(turn) * uy
        legs.append((tip[0] + bx * size, tip[1] + by * size))
    return poly([legs[0], tip, legs[1]], stroke_width=_f(w))


def _dim_line(a, b, size=11.0, w=LEGEND_HAIR) -> list[str]:
    """Målelinje mellom to punkter, med pilspiss i begge ender."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    return [line(a[0], a[1], b[0], b[1], stroke_width=_f(w)),
            _arrow_head(a, (-dx, -dy), size, w),
            _arrow_head(b, (dx, dy), size, w)]


def notation_legend_svg(d: float = 5.0, length: float = 60.0,
                        count: int = 100) -> str:
    """Ett eksemplar med målsetting: lengde, tykkelse og antall.

    Skruen tegnes av den samme koden som beslagglyfene, bare i større målestokk
    og med litt finere strek, slik at den er den samme silhuetten leseren
    finner igjen i tabellen under.
    """
    global STROKE_MM, DETAIL_MM
    S = LEGEND_SCALE
    keep = (STROKE_MM, DETAIL_MM)
    STROKE_MM, DETAIL_MM = LEGEND_STROKE / S, LEGEND_DETAIL / S
    try:
        screw, (_x0, _y0, _x1, _y1) = glyph_wood_screw(d, length)
        stroke_mm = STROKE_MM
    finally:
        STROKE_MM, DETAIL_MM = keep

    ox, axis = 70.0, 118.0                      # hodets ytterflate, skruaksen
    tip_x = ox + length * S
    head_r = _head_dia(d) / 2.0 * S
    thread_r = d / 2.0 * S
    dim_x = ox + length * 0.72 * S              # midt i gjengene

    body = [f'    <g transform="translate({_f(ox)} {_f(axis)}) '
            f'scale({_f(S)})" stroke-width="{_f(stroke_mm)}">']
    body += ["      " + e for e in screw]
    body.append("    </g>")

    # LENGDE: målelinje under hele skruen, med hjelpelinjer i begge ender.
    y_dim = 192.0
    for x in (ox, tip_x):
        body.append("    " + line(x, axis + head_r + 8, x, y_dim + 14,
                                  stroke_width=_f(LEGEND_HAIR)))
    body += ["    " + e for e in _dim_line((ox, y_dim), (tip_x, y_dim))]
    body.append("    " + _text((ox + tip_x) / 2, 240,
                               f"{_fmt_dim(length)} = lengde (mm)",
                               LEGEND_TEXT, "middle"))

    # TYKKELSE: gjengediameteren er bare 5 mm, så pilene settes UTENFOR målet
    # og peker innover - ellers ville de to spissene gå i hverandre. Den øvre
    # pilas hale er samtidig henvisningen til teksten.
    hair = _f(LEGEND_HAIR)
    for y in (axis - thread_r, axis + thread_r):
        body.append("    " + line(dim_x - 15, y, dim_x + 15, y,
                                  stroke_width=hair))
    body.append("    " + poly([(374, 56), (dim_x, 56),
                               (dim_x, axis - thread_r)], stroke_width=hair))
    body.append("    " + _arrow_head((dim_x, axis - thread_r), (0, 1), 10.0))
    body.append("    " + line(dim_x, axis + thread_r + 46, dim_x,
                              axis + thread_r, stroke_width=hair))
    body.append("    " + _arrow_head((dim_x, axis + thread_r), (0, -1), 10.0))
    body.append("    " + _text(366, 68, f"{_fmt_dim(d)} = tykkelse (mm)",
                               LEGEND_TEXT, "end"))

    # ANTALL: tallet slik det står i tabellen, med sin egen henvisning.
    cnt_x = tip_x + 74
    body.append("    " + _text(cnt_x, axis + 24, f"{count}x", 66.0,
                               "start", "bold"))
    body.append("    " + line(cnt_x + 38, 64, cnt_x + 38, 88,
                              stroke_width=_f(LEGEND_HAIR)))
    body.append("    " + _arrow_head((cnt_x + 38, 92), (0, 1), 9.0))
    body.append("    " + _text(cnt_x + 38, 50, "antall", 34.0, "middle"))

    return svg_document("Slik leser du beslaglista", 910.0, 258.0,
                        "\n".join(body), LEGEND_HAIR)


def _fmt_dim(v: float) -> str:
    return f"{v:g}".replace(".", ",")


BADGE_STROKE = 1.6          # ringen, på 24-rutenettet


def badge_svg(letter: str) -> str:
    """Én ringet bokstav, på det samme 24x24-rutenettet som piktogrammene.

    Egen strekvekt, ikke piktogrammenes: merket settes bare 5 mm høyt i
    stegtabellen, og ringen må holde seg svart der.
    """
    c, r = PICTO_SIZE / 2.0, 10.4
    body = ("    " + circle(c, c, r) + "\n"
            + "    " + _text(c, c + r * 0.40, letter, r * 1.20, "middle",
                             "bold"))
    return svg_document(f"Merke {letter}", PICTO_SIZE, PICTO_SIZE, body,
                        BADGE_STROKE)


# --------------------------------------------------------------------------
# Piktogrammer
# --------------------------------------------------------------------------
#
# Piktogrammene tegnes ikke lenger i kode. De ligger som ferdige SVG-filer i
# docs/icons/, på Lucides spesifikasjon: 24x24 viewBox, fill="none",
# stroke="currentColor", stroke-width="2", runde hjørner og ender.
#
#   docs/icons/lucide/  vendorte Lucide-ikoner (ISC, LICENSE ligger ved siden)
#   docs/icons/hanna/   ikonene som er tegnet for denne bruksanvisningen
#
# Her settes de bare sammen: kroppen hentes ut av kildefila og legges inn i
# manualens eget lerret med svart strek i stedet for currentColor. Noen
# nøkler er rutenett av flere ikoner (verktøypanelet).

ICON_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "docs", "icons")

# nøkkel -> (tittel, kilde). Kilde er enten en enkelt ikonreferanse
# "<katalog>/<navn>", eller en liste som settes i rutenett.
PICTOGRAMS: dict[str, tuple[str, object]] = {
    "to-personer": ("To personer til løftet", "hanna/to-personer"),
    "en-person-nei": ("Ikke løft alene", "hanna/en-person-nei"),
    "underlag": ("Mykt underlag under delene", "hanna/underlag"),
    "dra-nei": ("Ikke dra delene over gulvet", "hanna/dra-nei"),
    "sorter": ("Sorter delene før du starter", "hanna/sorter"),
    # Steg 0-regelen tegnet: blyanten bak øret og delene merket, mot
    # skrutrekkeren i hånda og delene i en haug. Den avløste bokikonet
    # ("les steg 0 først"), som sa det samme uten å vise det - og lucide/
    # book-open fulgte med ut av katalogen, etter regelen over.
    "blyant-foerst": ("Merk av før du skrur", "hanna/blyant-foerst"),
    "skrutrekker-foerst-nei": ("Ikke start med skrutrekkeren",
                               "hanna/skrutrekker-foerst-nei"),
    # V5: the spanner is gone with the last threaded fastener - there is
    # nothing in this bed to put a 10 mm nut on, and a tool panel that shows
    # one is a tool panel that sends somebody looking for it.
    "verktoy": ("Verktøy: drill, torxbits, tommestokk, vater, vinkelhake",
                ["lucide/drill", "hanna/torx-driver",
                 "hanna/tape-measure", "hanna/spirit-level",
                 "hanna/try-square"]),
    "forbor": ("Forbor før du skrur", "hanna/forbor"),
    "veggfeste-ja": ("Sengen skal festes i veggen", "hanna/veggfeste-ja"),
    "fritt-staaende-nei": ("Sengen skal ikke stå fritt",
                           "hanna/fritt-staaende-nei"),
    "hake": ("Slik skal det gjøres", "lucide/check"),
    "kryss": ("Slik skal det ikke gjøres", "lucide/x"),
    "info": ("Merk", "lucide/info"),
}

# Verktøypanelet: tre ikoner i bredden gir 72x48 - samme høyde som de andre
# piktogrammene, og hvert verktøy trykkes i ca. 9,5 mm.
GRID_COLS = 3

_SVG_BODY_RE = re.compile(r"<svg\b[^>]*>(.*)</svg>", re.S)


def icon_path(ref: str) -> str:
    return os.path.join(ICON_ROOT, *ref.split("/")) + ".svg"


def icon_body(ref: str) -> str:
    """Kroppen i en 24x24-ikonfil, uten <svg>-kappen og uten tomme linjer."""
    path = icon_path(ref)
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    m = _SVG_BODY_RE.search(text)
    if not m:
        raise ValueError(f"{path} ser ikke ut som en SVG")
    vb = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', text)
    if not vb or (float(vb.group(1)), float(vb.group(2))) != (PICTO_SIZE,
                                                             PICTO_SIZE):
        raise ValueError(f"{path} er ikke på {PICTO_SIZE}x{PICTO_SIZE}-rutenettet")
    return "\n".join(ln.strip() for ln in m.group(1).strip().splitlines()
                     if ln.strip())


def pictogram_svg(key: str) -> str:
    title, src = PICTOGRAMS[key]
    if isinstance(src, str):
        body = "\n".join("    " + ln for ln in icon_body(src).splitlines())
        return svg_document(title, PICTO_SIZE, PICTO_SIZE, body, PICTO_STROKE)

    cols = min(GRID_COLS, len(src))
    rows = -(-len(src) // cols)
    cells = []
    for i, ref in enumerate(src):
        dx = (i % cols) * PICTO_SIZE
        dy = (i // cols) * PICTO_SIZE
        inner = "\n".join("        " + ln for ln in icon_body(ref).splitlines())
        cells.append(f'    <g transform="translate({_f(dx)} {_f(dy)})">\n'
                     f'{inner}\n    </g>')
    return svg_document(title, cols * PICTO_SIZE, rows * PICTO_SIZE,
                        "\n".join(cells), PICTO_STROKE)


# --------------------------------------------------------------------------
# Rastrering
# --------------------------------------------------------------------------

_RSVG_WARNED = False


def _rsvg() -> str | None:
    for cand in ("rsvg-convert", "/opt/homebrew/bin/rsvg-convert",
                 "/usr/local/bin/rsvg-convert"):
        found = shutil.which(cand) or (cand if os.path.exists(cand) else None)
        if found:
            return found
    return None


def _vb_width(svg_text: str) -> float:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
    return float(m.group(1)) if m else 400.0


def write_png(svg_path: str, px_per_unit: float) -> str | None:
    """Rastrerer en SVG ved siden av seg selv. Returnerer PNG-stien eller None."""
    global _RSVG_WARNED
    exe = _rsvg()
    if not exe:
        if not _RSVG_WARNED:
            print("ADVARSEL: rsvg-convert mangler - hopper over PNG-ene.",
                  file=sys.stderr)
            _RSVG_WARNED = True
        return None
    with open(svg_path, "r", encoding="utf-8") as fh:
        width = max(64, int(round(_vb_width(fh.read()) * px_per_unit)))
    png_path = os.path.splitext(svg_path)[0] + ".png"
    try:
        subprocess.run([exe, "-w", str(width), svg_path, "-o", png_path],
                       check=True, capture_output=True)
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"ADVARSEL: klarte ikke rastrere {svg_path}: {exc}",
              file=sys.stderr)
        return None
    return png_path


# --------------------------------------------------------------------------
# Utskriving
# --------------------------------------------------------------------------

def emit_fastener_glyphs(names: list[str], out_dir: str) -> dict[str, str]:
    """Skriver én SVG (og PNG) per unikt festemiddel. -> {navn: filnavn}."""
    os.makedirs(out_dir, exist_ok=True)
    result: dict[str, str] = {}
    seen: dict[str, str] = {}
    for name in names:
        if name in result:
            continue
        base = slug(name)
        if base in seen and seen[base] != name:
            n = 2
            while f"{base}-{n}" in seen:
                n += 1
            base = f"{base}-{n}"
        seen[base] = name
        fname = base + ".svg"
        target = os.path.join(out_dir, fname)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(fastener_svg(name))
        write_png(target, PNG_PX_PER_UNIT)
        result[name] = fname
    return result


def emit_coded_glyphs(pairs, out_dir: str) -> dict[tuple[str, str], str]:
    """Én glyf per (festemiddel, fyllkode) et steg faktisk bruker.

    Ikke én per kombinasjon som finnes: bokstavene deles ut per steg, så det
    er stegene som avgjør hvilke par som oppstår, og et par ingen side viser
    er en fil ingen leser."""
    os.makedirs(out_dir, exist_ok=True)
    result: dict[tuple[str, str], str] = {}
    for name, code in sorted(pairs):
        if not is_screw_glyph(name):
            # A bracket keeps its plate look, so a coded copy of it would be
            # the same drawing under a second name.
            continue
        fname = coded_slug(name, code) + ".svg"
        target = os.path.join(out_dir, fname)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(fastener_svg(name, code))
        write_png(target, PNG_PX_PER_UNIT)
        result[(name, code)] = fname
    return result


# Kodenavnene på norsk, i bokstavrekkefølge - forklaringen på beslagsiden.
FILL_CODE_NAMES = {"open": "åpen", "hatch": "skravert",
                   "cross": "krysskravert", "solid": "heldekt"}


def fill_code_legend_svg(d: float = 6.0, length: float = 45.0) -> str:
    """Fyllkoden i full størrelse: hver bokstav med sin egen silhuett.

    Beslagsiden er der leseren lærer notasjonen - hva de to tallene i «5×60»
    er, og hva «100x» teller. Fyllkoden hører hjemme samme sted, og den må
    læres én gang i en størrelse der ingen to mønstre kan forveksles. På
    stegsiden er den en påminnelse; her er den definisjonen.
    """
    global STROKE_MM, DETAIL_MM
    S = 4.0
    keep = (STROKE_MM, DETAIL_MM)
    STROKE_MM, DETAIL_MM = 5.0 / S, 3.2 / S
    try:
        screw, (x0, _y0, x1, _y1) = glyph_wood_screw(d, length)
        stroke_mm = STROKE_MM
    finally:
        STROKE_MM, DETAIL_MM = keep

    cell = 232.0
    axis = 86.0
    vb_h = 150.0
    # SAMME MØNSTER SOM TABELLGLYFEN, ikke et som er valgt for forklaringens
    # egen (større) størrelse. Dette er den samme skruen i den samme
    # millimeterskalaen, bare satt større på siden, og forklaringen er stedet
    # koden LÆRES: gir vi den en finere periode fordi den har plass, lærer
    # leseren et mønster som ikke er det tabellen viser. Perioden hentes
    # derfor med tabellglyfens egne to tall.
    base, t = fill_metrics(d, GLYPH_MIN_PX / BASE_H_MM)
    body = ["  " + fill_defs(base, t)]
    for i, code in enumerate(FILL_CODES):
        letter = BADGE_ALPHABET[i]
        ox = i * cell + 20.0
        r = 21.0
        body.append("    " + circle(ox + r, axis - 46.0, r,
                                    stroke_width=_f(2.6)))
        body.append("    " + _text(ox + r, axis - 46.0 + r * 0.40, letter,
                                   r * 1.20, "middle", "bold"))
        elems = [_filled(screw[0], fill_paint(code))] + list(screw[1:])
        body.append(f'    <g transform="translate({_f(ox)} {_f(axis)}) '
                    f'scale({_f(S)})" stroke-width="{_f(stroke_mm)}">')
        body += ["      " + e for e in elems]
        body.append("    </g>")
        body.append("    " + _text(ox, axis + 54.0, FILL_CODE_NAMES[code],
                                   30.0, "start"))
    w = cell * len(FILL_CODES) + 20.0
    return svg_document("Fyllkoden: bokstaven som mønster", w, vb_h,
                        "\n".join(body), 2.6)


def emit_fill_code_legend(out_dir: str) -> str:
    """Skriver fyllkodeforklaringen til beslagsiden. -> filnavn."""
    os.makedirs(out_dir, exist_ok=True)
    fname = "fyllkode.svg"
    target = os.path.join(out_dir, fname)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(fill_code_legend_svg())
    write_png(target, PNG_PX_PER_UNIT)
    return fname


def emit_notation_legend(out_dir: str) -> str:
    """Skriver notasjonsforklaringen til beslagsiden. -> filnavn."""
    os.makedirs(out_dir, exist_ok=True)
    fname = "notasjon.svg"
    target = os.path.join(out_dir, fname)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(notation_legend_svg())
    write_png(target, PNG_PX_PER_UNIT)
    return fname


def emit_badges(out_dir: str, n: int) -> dict[str, str]:
    """Skriver de `n` første merkebokstavene. -> {bokstav: filnavn}."""
    os.makedirs(out_dir, exist_ok=True)
    result: dict[str, str] = {}
    for letter in BADGE_ALPHABET[:n]:
        fname = f"merke-{letter.lower()}.svg"
        target = os.path.join(out_dir, fname)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(badge_svg(letter))
        write_png(target, PICTO_PX_PER_UNIT)
        result[letter] = fname
    return result


def emit_pictograms(out_dir: str) -> dict[str, str]:
    """Skriver "før du starter"-piktogrammene. -> {nøkkel: filnavn}."""
    os.makedirs(out_dir, exist_ok=True)
    result: dict[str, str] = {}
    for key in PICTOGRAMS:
        fname = key + ".svg"
        target = os.path.join(out_dir, fname)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(pictogram_svg(key))
        write_png(target, PICTO_PX_PER_UNIT)
        result[key] = fname
    return result


FASTENERS = [
    "Treskrue 5×40 forsenket Torx",
    "Treskrue 4×16 forsenket Torx",
    "Treskrue 5×60 forsenket Torx",
    "Treskrue 5×70 forsenket Torx",
    "Treskrue 6×60 forsenket Torx",
    "Treskrue 6×80 forsenket Torx",
    "Treskrue 6×90 forsenket Torx",
    "Treskrue 6×120 forsenket Torx",
    "Senkhodeskrue M6×30 + skive M6 + låsemutter M6",
    "Vinkelbeslag 20×20×40 varmforsinket",
    "Vinkelbeslag 40×40×20",
    "Vinkelbeslag 90×90×40×2,5 varmforsinket",
    "Veggfeste etter veggtype (treskrue 8×100 i stender, eller plugg + skrue i mur)",
    "Filtknott / møbeltapp ⌀40",
]


def read_fastener_names(path_md: str) -> list[str]:
    """Leser handelsnavnene ut av docs/generated/beslagliste.md.
    Faller tilbake på den innebygde listen."""
    try:
        with open(path_md, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return list(FASTENERS)
    names, seen = [], set()
    in_table = False
    for raw in text.splitlines():
        ln = raw.strip()
        if ln.startswith("| Post "):
            in_table = True
            continue
        if in_table:
            if not ln.startswith("|"):
                break
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if not cells or set(cells[0]) <= set("-: "):
                continue
            name = cells[0]
            if name and name not in seen:
                seen.add(name)
                names.append(name)
    return names or list(FASTENERS)


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv: list[str] | None = None) -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--beslag-dir",
                    default=os.path.join(root, "docs", "img", "beslag"))
    ap.add_argument("--ikon-dir",
                    default=os.path.join(root, "docs", "img", "ikon"))
    ap.add_argument("--beslagliste",
                    default=os.path.join(root, "docs", "generated",
                                         "beslagliste.md"))
    args = ap.parse_args(argv)

    names = read_fastener_names(args.beslagliste)
    fast = emit_fastener_glyphs(names, args.beslag_dir)
    legend = emit_notation_legend(args.beslag_dir)
    icons = emit_pictograms(args.ikon_dir)
    badges = emit_badges(args.ikon_dir, 4)

    print(f"{len(fast)} beslagglyfer -> {args.beslag_dir}")
    print(f"  {legend:<28} notasjonsforklaring")
    print(f"  {len(badges)} merkebokstaver -> {args.ikon_dir}")
    for name, fname in fast.items():
        print(f"  {fname:<28} {name}")
    print(f"{len(icons)} piktogrammer -> {args.ikon_dir}")
    for key, fname in icons.items():
        print(f"  {fname:<28} {key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
