#!/usr/bin/env python3
"""Hodet på konturfiguren, REGNET: docs/icons/hanna/*.svg og tabellene i
PRAKSIS §4.

Menneskefiguren i piktogrammene er én lukket kontur — «beltet» rundt en kjede
av sirkler, med ytre tangentlinjer mellom nabosirkler, en bue på hver sirkel og
en konkav fals der hals og armhule snører seg inn. KROPPEN er tegnet én gang og
ligger i ikonfilene; HODET er regnet, og det er dette verktøyet som regner det:

    isse + hake      hodet er to ledd, ikke ett - hjerneskallen bak og over,
                     haken lav og skjøvet fram i ansiktsretningen
    nese             et ledd i kjeden som alle de andre, med neseryggen som en
                     ytre tangentlinje opp til issen (ikke en konkav fals - det
                     er den ene skjøten som skiller et ansikt fra et nebb)
    munnfals         konkav, kort, mellom nese og hake
    halsfalsene      den fremre ender på HAKEN, den bakre på ISSEN
    ansiktet         øyeprikken og smilekurven, polart om hodesenteret

HVOR TALLENE KOMMER FRA
-----------------------
Herfra, og bare herfra. Landemerketabellen nedenfor er kilden: den tegner
hodet inn i de fire figurikonene, og den skriver tabellene i PRAKSIS §4. To
filer som må være enige om et tall er ett tall for mye, så PRAKSIS har ingen
egen kopi - den har et generert avsnitt mellom to merker.

Kroppsleddene (bryst, midje, hofte, fald, armhule) står i den samme tabellen
fordi det er DEN tabellen, men de tegnes ikke herfra: de ligger i konturen i
ikonfilene. Verktøyet rører bare halsfalsene og alt over dem.

Usage:
    python tools/gen_figurhode.py            # skriv hodet inn i ikonene + PRAKSIS
    python tools/gen_figurhode.py --check    # skriv ingenting, fell hvis de avviker
    python tools/gen_figurhode.py --maal     # skriv lesbarhetsportens mål

Deterministisk: ingen klokke, ingen id(), ingen mengdeiterasjon ut i fila. To
kjøringer gir byte-identiske filer, og `mise run check` sier fra hvis ikke.
"""

from __future__ import annotations

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICON_DIR = os.path.join(ROOT, "docs", "icons", "hanna")
PRAKSIS = os.path.join(ROOT, "docs", "PRAKSIS.md")

# --------------------------------------------------------------------------
# LANDEMERKENE, i 24-rutenettets enheter
#
# `dx` er ut fra figurens midtlinje og `y` nedover i figurens egne
# koordinater. Hodebåndet er 1,5 øverst og 7,1 nederst - 5,6 av figurens 20,95,
# altså 26,7 %, som er IKEA-mannens hodeandel. `dx` er symmetrisk om
# midtlinjen for alle ledd unntatt HAKEN: den ligger bare på den ene siden, i
# ansiktsretningen, og det er det ene stedet figuren vet hvilken vei den ser.
# --------------------------------------------------------------------------

HEAD_TOP = 1.50             # issens topp
HEAD_BOT = 7.10             # hakens bunn
HEAD_C_Y = 4.30             # hodesenteret - ansiktet regnes polart om dette

CROWN_R = 2.52              # issen: hjerneskallen, stor og rund, bak og over
CHIN_DX = 1.30              # haken: eget lite ledd, lavt og skjøvet fram
CHIN_R = 1.45
NECK_F = 1.40               # halsens konkave fals, foran på haken, bak på issen

SHOULDER_DX = 1.15          # skulderen - halsfalsens andre ende
SHOULDER_Y = 9.40
SHOULDER_R = 1.35

# Kroppen. Tegnet i ikonfilene, ikke herfra; står her fordi dette er tabellen.
BODY = [
    ("bryst", 1.10, 11.60, 1.40),
    ("midje", 1.05, 14.20, 1.40),
    ("hofte", 1.30, 17.50, 1.45),
    ("fald, hjørne", 1.80, 20.40, 1.65),
    ("fald, midt", 0.00, 20.70, 1.70),
]
ARMPIT_F = 0.80             # armhulen, konkav

# ANSIKTET: de samme tallene en gang til, bare polart om hodesenteret.
# Avstand og vinkel i ansiktsretningen, positiv vinkel = under vannrett.
NOSE_D, NOSE_ANG, NOSE_R = 3.05, 10.0, 0.68
LIP_F = 0.45                # munnfalsen, konkav, nese -> hake
EYE_D, EYE_ANG, EYE_R = 1.35, -38.0, 0.30
SMILE = ((1.80, 40.0), (0.95, 68.0), 1.30)   # fremre munnvik, bakre ende, buens r

# Sirkelsentrene, relativt hodesenteret (x peker i ansiktsretningen).
CROWN_C = (0.0, HEAD_TOP - HEAD_C_Y + CROWN_R)
CHIN_C = (CHIN_DX, HEAD_BOT - HEAD_C_Y - CHIN_R)
SHOULDER_C = (SHOULDER_DX, SHOULDER_Y - HEAD_C_Y)


def polar(d, deg):
    a = math.radians(deg)
    return (d * math.cos(a), d * math.sin(a))


NOSE_C = polar(NOSE_D, NOSE_ANG)


# --------------------------------------------------------------------------
# Beltegeometri
# --------------------------------------------------------------------------

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _mul(a, k):
    return (a[0] * k, a[1] * k)


def _norm(a):
    return math.hypot(a[0], a[1])


def _unit(a):
    n = _norm(a)
    return (a[0] / n, a[1] / n)


def _right(u):
    """Høyre side av gangretningen u, i skjermkoordinater (y nedover)."""
    return (-u[1], u[0])


def tangent_line(ca, ra, cb, rb):
    """Ytre tangentlinje A->B. Beltet går med utsiden til HØYRE."""
    d = _norm(_sub(cb, ca))
    u = _unit(_sub(cb, ca))
    w = _right(u)
    cos_t = (ra - rb) / d
    if abs(cos_t) > 1:
        raise ValueError("ingen ytre tangent")
    sin_t = math.sqrt(1 - cos_t * cos_t)
    v = (cos_t * u[0] + sin_t * w[0], cos_t * u[1] + sin_t * w[1])
    return _add(ca, _mul(v, ra)), _add(cb, _mul(v, rb))


def fillet(ca, ra, cb, rb, f):
    """Konkav fals med radius f mellom A og B. Falsens senter ligger på
    UTSIDEN, altså til høyre for gangretningen A->B."""
    d = _norm(_sub(cb, ca))
    u = _unit(_sub(cb, ca))
    w = _right(u)
    ta, tb = ra + f, rb + f
    a = (ta * ta - tb * tb + d * d) / (2 * d)
    h2 = ta * ta - a * a
    if h2 < 0:
        raise ValueError("falsen får ikke plass")
    h = math.sqrt(h2)
    fc = (ca[0] + u[0] * a + w[0] * h, ca[1] + u[1] * a + w[1] * h)
    pa = _add(ca, _mul(_unit(_sub(fc, ca)), ra))
    pb = _add(cb, _mul(_unit(_sub(fc, cb)), rb))
    return fc, pa, pb


def _ang(c, p):
    return math.atan2(p[1] - c[1], p[0] - c[0])


TAU = 2 * math.pi


def arc_convex(c, r, p1, p2):
    """Bue på et ledd: gås med SYNKENDE vinkel (sweep 0)."""
    delta = (_ang(c, p1) - _ang(c, p2)) % TAU
    return dict(r=r, large=1 if delta > math.pi else 0, sweep=0,
                start=p1, end=p2, _c=c)


def arc_concave(c, r, p1, p2):
    """Bue på en fals: gås med STIGENDE vinkel (sweep 1)."""
    delta = (_ang(c, p2) - _ang(c, p1)) % TAU
    return dict(r=r, large=1 if delta > math.pi else 0, sweep=1,
                start=p1, end=p2, _c=c)


def _dir(sg, at_start):
    """Gangretningen i enden av et segment."""
    p = sg["start"] if at_start else sg["end"]
    if sg.get("line"):
        return _unit(_sub(sg["end"], sg["start"]))
    c = sg["_c"]
    phi = _ang(c, p)
    if sg["sweep"] == 0:
        return (math.sin(phi), -math.cos(phi))
    return (-math.sin(phi), math.cos(phi))


def assert_g1(segs):
    """Konturen skal være GLATT: gangretningen ut av et ledd er gangretningen
    inn i det neste. Går en bue feil vei rundt, snur den, og da er hodet et
    knekk - ikke et hode."""
    for a, b in zip(segs, segs[1:]):
        da, db = _dir(a, False), _dir(b, True)
        if da[0] * db[0] + da[1] * db[1] < 0.999:
            raise ValueError("knekk i hodekonturen - et ledd gås feil vei")


def neck_ends():
    """Halsfalsenes endepunkter på SKULDEREN: foran (på haken), bak (på issen).
    Kroppen ender her, og hodet begynner."""
    s_front = SHOULDER_C
    s_back = (-SHOULDER_C[0], SHOULDER_C[1])
    _, q_front, _ = fillet(s_front, SHOULDER_R, CHIN_C, CHIN_R, NECK_F)
    _, _, q_back = fillet(CROWN_C, CROWN_R, s_back, SHOULDER_R, NECK_F)
    return q_front, q_back


def head_segments():
    """Hodekonturen i gangretning, fra den fremre halsfalsens endepunkt på
    HAKEN til den bakre halsfalsens endepunkt på ISSEN. Ansiktet mot +x.

    Rekkefølgen nese, munn, hake, hals er hele forskjellen på et ansikt og et
    hode med nebb: felles nesen inn i HALSEN i stedet for i haken, leser falsen
    som strupe og hodet slutter der nesen slutter.
    """
    s_front = SHOULDER_C
    s_back = (-SHOULDER_C[0], SHOULDER_C[1])
    _, _, p_in = fillet(s_front, SHOULDER_R, CHIN_C, CHIN_R, NECK_F)
    _, p_out, _ = fillet(CROWN_C, CROWN_R, s_back, SHOULDER_R, NECK_F)

    fc_l, a_l, b_l = fillet(CHIN_C, CHIN_R, NOSE_C, NOSE_R, LIP_F)
    t1, t2 = tangent_line(NOSE_C, NOSE_R, CROWN_C, CROWN_R)
    segs = [arc_convex(CHIN_C, CHIN_R, p_in, a_l),
            arc_concave(fc_l, LIP_F, a_l, b_l),
            arc_convex(NOSE_C, NOSE_R, b_l, t1),
            dict(line=True, start=t1, end=t2),
            arc_convex(CROWN_C, CROWN_R, t2, p_out)]
    assert_g1(segs)
    return segs, p_in, p_out


# --------------------------------------------------------------------------
# Lesbarhetsporten: mellomrommene er det som setter grensen på 16 mm
# --------------------------------------------------------------------------

FIGURE_STROKE = 0.75        # 0,6 x PICTO_STROKE, se PRAKSIS §4


def contour_x(y):
    """Den fremre konturens x i høyden y (relativt hodesenteret)."""
    best = None
    for c, r in ((CROWN_C, CROWN_R), (CHIN_C, CHIN_R)):
        dy = y - c[1]
        if abs(dy) <= r:
            x = c[0] + math.sqrt(r * r - dy * dy)
            best = x if best is None else max(best, x)
    return best


def contour_points(n=720):
    """Hodekonturen som punkter. Å måle mot SIRKLENE er feil - et ledd bærer
    bare sin egen bue, og den nærmeste sirkelen er ofte ikke kontur der
    målingen tas."""
    segs, _, _ = head_segments()
    pts = []
    for sg in segs:
        if sg.get("line"):
            for i in range(n + 1):
                t = i / n
                pts.append((sg["start"][0] + t * (sg["end"][0] - sg["start"][0]),
                            sg["start"][1] + t * (sg["end"][1] - sg["start"][1])))
            continue
        c, r = sg["_c"], sg["r"]
        a0, a1 = _ang(c, sg["start"]), _ang(c, sg["end"])
        d = (a1 - a0) % TAU
        if sg["sweep"] == 0:
            d -= TAU
        for i in range(n + 1):
            a = a0 + d * i / n
            pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return pts


def _clearance(p, r):
    """Fri luft fra et fylt element ut til nærmeste hodekontur, med streken
    trukket fra på begge sider."""
    return min(_norm(_sub(p, q)) for q in contour_points()) - r - FIGURE_STROKE


def maal():
    """Tallene lesbarhetsporten hviler på, regnet - ikke gjettet."""
    eye = polar(EYE_D, EYE_ANG)
    (d1, a1), _, _ = SMILE
    mouth = polar(d1, a1)
    head_w = max(CROWN_C[0] + CROWN_R, CHIN_C[0] + CHIN_R) \
        - min(CROWN_C[0] - CROWN_R, CHIN_C[0] - CHIN_R)
    return {
        "hodehøyde": HEAD_BOT - HEAD_TOP,
        "hjerneskallens bredde": 2 * CROWN_R,
        "hodebredde med haken": head_w,
        "nesetippen forbi issekonturen": NOSE_C[0] + NOSE_R - contour_x(NOSE_C[1]),
        "øyeprikken -> nærmeste kontur": _clearance(eye, EYE_R),
        "munnviken -> nærmeste kontur": _clearance(mouth, 0.0),
    }


def gate():
    """Portens asserter. Grensene er de målte i PRAKSIS §4, ikke ambisjoner:
    ryker en av dem, er ansiktet borte i 72 px og det skal stoppe bygget."""
    m = maal()
    assert abs(m["hodehøyde"] - 5.6) < 1e-9, m
    # Nesen må BRYTE silhuetten: en nese som ikke gjør det, finnes ikke i 72 px.
    assert m["nesetippen forbi issekonturen"] > 1.0, m
    # Øyet og munnviken vokser fra begge sider når streken vokser.
    assert m["øyeprikken -> nærmeste kontur"] > 0.28, m
    assert m["munnviken -> nærmeste kontur"] > 0.60, m
    # Høyere enn bredt, med tyngden ned mot kjeven.
    assert m["hjerneskallens bredde"] < m["hodehøyde"], m
    assert m["hodebredde med haken"] < m["hodehøyde"], m


# --------------------------------------------------------------------------
# SVG
# --------------------------------------------------------------------------

def fmt(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pt(p):
    return f"{fmt(p[0])} {fmt(p[1])}"


def place(p, H, s, d):
    """Fra hodesenterets koordinater til ikonets. d = -1 vender figuren."""
    return (H[0] + d * s * p[0], H[1] + s * p[1])


def segs_to_d(segs, H, s, d):
    items = []
    for sg in segs:
        st = place(sg["start"], H, s, d)
        en = place(sg["end"], H, s, d)
        if sg.get("line"):
            items.append(dict(line=True, start=st, end=en))
        else:
            items.append(dict(r=sg["r"] * s, large=sg["large"],
                              sweep=sg["sweep"], start=st, end=en))
    if d < 0:
        items = [dict(it, start=it["end"], end=it["start"])
                 for it in reversed(items)]
    parts = []
    for it in items:
        if it.get("line"):
            parts.append(f"L{pt(it['end'])}")
        else:
            parts.append(f"A{fmt(it['r'])} {fmt(it['r'])} 0 "
                         f"{it['large']} {it['sweep']} {pt(it['end'])}")
    return "".join(parts), items[0]["start"], items[-1]["end"]


def face_elems(H, s, dr):
    """Øyeprikken (fylt) og smilekurven (åpen)."""
    eye = place(polar(EYE_D, EYE_ANG), H, s, dr)
    (d1, a1), (d2, a2), rr = SMILE
    p1 = place(polar(d1, a1), H, s, dr)
    p2 = place(polar(d2, a2), H, s, dr)
    sweep = 1 if dr > 0 else 0
    return (f'<circle cx="{fmt(eye[0])}" cy="{fmt(eye[1])}" '
            f'r="{fmt(EYE_R * s)}" fill="#111" />',
            f'<path d="M{pt(p1)}A{fmt(rr * s)} {fmt(rr * s)} 0 0 {sweep} '
            f'{pt(p2)}" fill="none" />')


# --------------------------------------------------------------------------
# Kirurgi i ikonfilene
#
# Konturen er ÉN path, og kroppen i den er tegnet - ikke regnet. Verktøyet
# bytter derfor ut halen: halsfalsenes endepunkter og alt over dem. Hvor halen
# begynner er ikke gjettet ut av et tall, men telt: hodet er like mange
# segmenter hver gang, og segmentet foran dem er halsfalsen.
# --------------------------------------------------------------------------

TOKEN = re.compile(r"([MLAZ])([^MLAZ]*)")

# figurens hodesenter i ikonet -> (senter, skala, retning). 1 = ser mot høyre.
# to-personer er skalert 0,86 om ikonets midtlinje: to figurer på 12,9 enheter
# får ikke plass på 24, og skaleringen tar konturen og radiene, ikke streken.
PLACEMENT = {
    ("to-personer", 0): ((5.9005, 5.373), 0.86, +1),
    ("to-personer", 1): ((18.0995, 5.373), 0.86, -1),
    ("en-person-nei", 0): ((12.00, 4.30), 1.0, +1),
    ("blyant-foerst", 0): ((7.20, 4.30), 1.0, +1),
    ("skrutrekker-foerst-nei", 0): ((6.80, 4.30), 1.0, +1),
}

FIGURES = ["to-personer", "en-person-nei", "blyant-foerst",
           "skrutrekker-foerst-nei"]


def parse_d(d):
    toks = []
    for m in TOKEN.finditer(d):
        args = [float(x) for x in m.group(2).replace(",", " ").split()]
        toks.append((m.group(1), args, m.start(), m.end()))
    return toks


def endpoint(cmd, args):
    if cmd in ("M", "L"):
        return (args[0], args[1])
    if cmd == "A":
        return (args[5], args[6])
    return None


def rebuild_path(d, H, s, dr):
    segs, _, _ = head_segments()
    toks = parse_d(d)
    assert toks[0][0] == "M" and toks[-1][0] == "Z", d[:40]
    # Halen: M, halsfals bak, ..., halsfals foran, <hodet>, Z
    k = len(toks) - len(segs) - 2
    assert abs(toks[k][1][0] - NECK_F * s) < 0.02, (k, toks[k])
    assert abs(toks[1][1][0] - NECK_F * s) < 0.02, toks[1]

    head_d, head_start, head_end = segs_to_d(segs, H, s, dr)
    q_front, q_back = neck_ends()
    Q_front = place(q_front, H, s, dr)
    Q_back = place(q_back, H, s, dr)
    # Figuren går inn på hodet forfra (dr = -1) eller bakfra (dr = +1).
    q_first, q_last = (Q_back, Q_front) if dr > 0 else (Q_front, Q_back)

    def arc_str(tok, end):
        _, a, *_ = tok
        return f"A{fmt(a[0])} {fmt(a[1])} 0 {int(a[3])} {int(a[4])} {pt(end)}"

    out = [f"M{pt(head_end)}",
           arc_str(toks[1], q_first),
           arc_str(toks[2], endpoint(*toks[2][:2])),
           d[toks[3][2]:toks[k - 1][2]],          # kroppen, urørt
           arc_str(toks[k - 1], q_last),
           arc_str(toks[k], head_start),
           head_d,
           "Z"]
    return "".join(out)


BODY_G = re.compile(r'<g fill="#fff">(.*?)</g>', re.S)
FIG_PATH = re.compile(r'(<path d="M)([^"]*)(" />)')
EYE = re.compile(r'<circle cx="[-\d.]+" cy="[-\d.]+" r="[-\d.]+" fill="#111" />')
SMILE_RE = re.compile(r'<path d="M[^"]*" fill="none" />')


def transform(text, name):
    """Bytt hodet, øyet og smilekurven i ett ikon."""
    body = BODY_G.search(text)
    assert body, name
    inner = body.group(1)
    idx = [0]

    def do_path(m):
        i = idx[0]
        idx[0] += 1
        H, s, dr = PLACEMENT[(name, i)]
        return m.group(1) + rebuild_path("M" + m.group(2), H, s, dr)[1:] + m.group(3)

    new = FIG_PATH.sub(do_path, inner)

    eyes, smiles = [], []
    for i in range(idx[0]):
        H, s, dr = PLACEMENT[(name, i)]
        e, sm = face_elems(H, s, dr)
        eyes.append(e)
        smiles.append(sm)
    ei, si = [0], [0]

    def take(bag, cnt):
        def sub(_m):
            r = bag[cnt[0]]
            cnt[0] += 1
            return r
        return sub

    new = EYE.sub(take(eyes, ei), new)
    new = SMILE_RE.sub(take(smiles, si), new)
    assert ei[0] == si[0] == idx[0], (name, ei, si, idx)
    return text[:body.start(1)] + new + text[body.end(1):]


# --------------------------------------------------------------------------
# PRAKSIS §4: tabellene skrives herfra
# --------------------------------------------------------------------------

MARK_LEDD = "figur-landemerker"
MARK_ANSIKT = "figur-ansikt"


def no(x):
    """Landemerketall: to desimaler og komma. Null er null."""
    return "0" if x == 0 else f"{x:.2f}".replace(".", ",")


def noy(x):
    """Høyder i figurens egne koordinater: like mange desimaler som tallet har."""
    return f"{x:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def grad(x):
    return ("−" if x < 0 else "") + f"{abs(x):.0f}°"


def table_ledd():
    rows = [("isse", no(0.0), noy(HEAD_C_Y + CROWN_C[1]), no(CROWN_R)),
            ("hake", no(CHIN_DX), noy(HEAD_C_Y + CHIN_C[1]), no(CHIN_R)),
            ("hals (konkav)", "—", "—", no(NECK_F)),
            ("skulder", no(SHOULDER_DX), noy(SHOULDER_Y), no(SHOULDER_R))]
    rows += [(n, no(dx), noy(y), no(r)) for n, dx, y, r in BODY]
    rows += [("armhule (konkav)", "—", "—", no(ARMPIT_F))]
    out = ["| ledd | dx | y | r |", "|---|---:|---:|---:|"]
    out += [f"| {n} | {a} | {b} | {c} |" for n, a, b, c in rows]
    return "\n".join(out)


def table_ansikt():
    (d1, a1), (d2, a2), rr = SMILE
    rows = [("nese", no(NOSE_D), grad(NOSE_ANG), no(NOSE_R)),
            ("neserygg", "ytre tangentlinje nese → isse", "—", "—"),
            ("munnfals (konkav, nese → hake)", "—", "—", no(LIP_F)),
            ("øyeprikk", no(EYE_D), grad(EYE_ANG), no(EYE_R)),
            ("smilekurve, fremre munnvik", no(d1), grad(a1),
             f"bue r {no(rr)}"),
            ("smilekurve, bakre ende", no(d2), grad(a2), "—")]
    out = ["| landemerke | avstand | vinkel | r |", "|---|---:|---:|---:|"]
    out += [f"| {n} | {a} | {b} | {c} |" for n, a, b, c in rows]
    return "\n".join(out)


def splice(text, mark, block):
    """Bytt ut alt mellom de to merkene. Tabellen står inne i en punktliste, så
    den arver innrykket merket selv står med."""
    start = f"<!-- GENERERT AV tools/gen_figurhode.py: {mark} -->"
    end = f"<!-- SLUTT: {mark} -->"
    i, j = text.find(start), text.find(end)
    assert i >= 0 and j > i, f"mangler merkene for {mark} i PRAKSIS §4"
    bol = text.rfind("\n", 0, i) + 1
    pad = text[bol:i]
    assert pad.strip() == "", f"merket for {mark} står ikke først på linja"
    body = "\n".join((pad + ln if ln else "") for ln in block.split("\n"))
    return text[:i] + start + "\n\n" + body + "\n\n" + pad + text[j:]


def praksis(text):
    return splice(splice(text, MARK_LEDD, table_ledd()),
                  MARK_ANSIKT, table_ansikt())


# --------------------------------------------------------------------------

def targets():
    """(sti, ny tekst) for alt verktøyet eier."""
    out = []
    for name in FIGURES:
        p = os.path.join(ICON_DIR, name + ".svg")
        with open(p, encoding="utf-8") as fh:
            old = fh.read()
        out.append((p, transform(old, name)))
    with open(PRAKSIS, encoding="utf-8") as fh:
        out.append((PRAKSIS, praksis(fh.read())))
    return out


def regenerate(check=False):
    """Skriv hodet inn i ikonene og tabellene inn i PRAKSIS. Returnerer de
    filene som var uenige med landemerketabellen."""
    gate()
    changed = []
    for path, new in targets():
        with open(path, encoding="utf-8") as fh:
            old = fh.read()
        if old == new:
            continue
        changed.append(os.path.relpath(path, ROOT))
        if not check:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
    return changed


def main(argv):
    gate()
    if "--maal" in argv:
        for k, v in maal().items():
            print(f"{k:32s} {v:6.3f}")
        return 0
    check = "--check" in argv
    bad = regenerate(check)
    if bad and not check:
        for rel in bad:
            print(f"skrev {rel}")
        bad = []
    if bad:
        print("HODET OG FILA ER UENIGE - landemerketabellen i "
              "tools/gen_figurhode.py er kilden, kjør verktøyet uten --check:")
        for rel in bad:
            print(f"  {rel}")
        return 1
    print(f"OK  {len(FIGURES)} figurikoner og PRAKSIS §4 er regnet av "
          f"landemerketabellen")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
