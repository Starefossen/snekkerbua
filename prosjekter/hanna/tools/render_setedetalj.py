"""The toe-screw SEAT, drawn: docs/schematics/setedetalj.svg.

Four fields on one sheet, all of them about the same small piece of geometry -
the flat-bottomed pocket a skew screw's head lies in, and the block that lets
a hand drill cut it at the right angle:

    1  SECTION ALONG THE SCREW AXIS, 2:1, one per angle. The face, the wood
       under it, the axis at its angle TO THE FACE, the pocket bored ALONG the
       axis with a flat bottom PERPENDICULAR to it, and the countersunk head
       lying in that bottom with the cover over its highest point dimensioned.
    2  THE MOUTHS SEEN HEAD ON, 1:1. What the ellipse actually looks like on
       the timber, where it sits, and how little wood is left between the two
       of them and out to the end grain.
    3  THE ANGLE BLOCK, EXPLODED. Two 48x68x200 pieces screwed face to face,
       the 18 mm hole bored SQUARE through both while the block is still
       square, and only then the sole cut off under it - with BOTH numbers on
       the cut, the saw's bevel and the angle the sole makes with the bored
       face, because they are complements and that is the pair the old recipe
       got wrong.
    4  THE BLOCK IN USE. Two clamps, a sacrificial block against the end
       grain, the bit down the guide hole, and the direction the screw goes.

WHERE THE NUMBERS COME FROM
---------------------------
generate_loftbed.py, and nothing else. The angles, the seat depths, the seat
diameter, the mouth ellipses, the head diameters and the two cover cases are
module globals or are measured off the placed fastener records; the local
frame each section is drawn in - which way is "into the wood", which way is
"towards the free end", how far the mouth centre is from that end - is derived
from the fastener's own seat_face and direction, so a screw that moves in the
model moves on this sheet. The only things typed here are the ones the model
has no opinion about: how big the paper is and where on it a label goes.

THE UNIT SYSTEM
---------------
One SVG user unit is one millimetre of paper, so a view drawn at 2:1 really is
2 units per model millimetre and the scale printed on it is the truth. The
type sizes and stroke weights are the checked-in sheets' own (the hand-drawn
sheets in docs/schematics/ - bench-detail.svg and friends, all drawn 3450
units wide), multiplied by STYLE_K = this sheet's width over theirs - so
rendered at the same pixel width, a line here is the same line there.

Usage:
    python tools/render_setedetalj.py [--out docs/schematics/setedetalj.svg]

Deterministic: no clock, no id(), no set iteration into the output. Two runs
give byte-identical files, and `mise run check` says so.
"""

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "tools"))

OUT = os.path.join(ROOT, "docs", "schematics", "setedetalj.svg")

# ---------------------------------------------------------------------------
# THE SHEET
# ---------------------------------------------------------------------------
SHEET_W = 880.0
SHEET_H = 606.0
# The checked-in schematics are drawn in a 3450-unit sheet, and every type
# size and stroke weight below is one of THEIRS multiplied by this factor -
# so the two families of sheet share one look.
#
# The factor is not the width ratio, and that is the one place this sheet
# parts company with the others. A unit here is a millimetre of PAPER,
# because the scales printed on the views (2:1, 1:1) have to be true; and on
# a 1:1 view the figures are competing with a 68 mm piece of timber rather
# than with a 2 m bed. 0.175 puts the body text at 3,85 mm, which is the
# height a drawing office writes at - and it is what makes a "6" fit between
# two pockets that are 6 mm apart.
FAMILY_W = 3450.0
STYLE_K = 0.175

def f(v):
    """Fixed, locale-free, sign-stable number formatting - the whole reason
    two runs of this file agree byte for byte."""
    s = f"{v:.3f}"
    if s.startswith("-") and float(s) == 0.0:
        s = s[1:]
    s = s.rstrip("0").rstrip(".")
    return s or "0"


def nb(v, dec=1):
    """A number the way it is written on a Norwegian drawing."""
    s = f"{v:.{dec}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def wrap(text, width, cls="sml"):
    """Greedy wrap to a column that is measured in PAPER millimetres, not in
    characters: a note that runs off the sheet is the one drawing fault a
    proof render always shows and a code review never does."""
    cw = SZ[cls] * 0.52
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


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Sheet:
    """A y-down SVG in paper millimetres, in the schematics family's idiom."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.body = []

    def add(self, raw):
        self.body.append("  " + raw)

    # -- primitives ---------------------------------------------------------
    def line(self, a, b, cls="dim", extra=""):
        self.add(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" '
                 f'y2="{f(b[1])}" class="{cls}"{extra}/>')

    def rect(self, x, y, w, h, cls):
        self.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" '
                 f'height="{f(h)}" class="{cls}"/>')

    def poly(self, pts, cls):
        d = " ".join(f"{f(p[0])},{f(p[1])}" for p in pts)
        self.add(f'<polygon points="{d}" class="{cls}"/>')

    def pline(self, pts, cls, extra=""):
        d = " ".join(f"{f(p[0])},{f(p[1])}" for p in pts)
        self.add(f'<polyline points="{d}" class="{cls}"{extra}/>')

    def path(self, d, cls, extra=""):
        self.add(f'<path d="{d}" class="{cls}"{extra}/>')

    def circle(self, c, r, cls):
        self.add(f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" '
                 f'class="{cls}"/>')

    def ellipse(self, c, rx, ry, cls, rot=0.0):
        tr = ""
        if abs(rot) > 1e-9:
            tr = (f' transform="rotate({f(rot)} {f(c[0])} {f(c[1])})"')
        self.add(f'<ellipse cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(rx)}" '
                 f'ry="{f(ry)}" class="{cls}"{tr}/>')

    def text(self, p, s, cls="sml", anchor="start"):
        self.add(f'<text x="{f(p[0])}" y="{f(p[1])}" class="{cls}" '
                 f'text-anchor="{anchor}">{esc(s)}</text>')

    def lines(self, p, rows, cls="sml", lead=None, anchor="start"):
        """A block of text, one row per line, top-left anchored."""
        lead = lead or SZ[cls] * 1.35
        for i, row in enumerate(rows):
            self.text((p[0], p[1] + i * lead), row, cls, anchor)
        return p[1] + (len(rows) - 1) * lead

    def arc(self, c, r, th0, th1, cls="dim", extra=""):
        """A circular arc, angles in sheet space (y down, so a growing angle
        turns clockwise on the page)."""
        a = (c[0] + r * math.cos(th0), c[1] + r * math.sin(th0))
        b = (c[0] + r * math.cos(th1), c[1] + r * math.sin(th1))
        large = 1 if abs(th1 - th0) > math.pi else 0
        sweep = 1 if th1 > th0 else 0
        self.path(f"M {f(a[0])},{f(a[1])} A {f(r)},{f(r)} 0 {large} "
                  f"{sweep} {f(b[0])},{f(b[1])}", cls, extra)

    # -- annotation ---------------------------------------------------------
    def dim(self, a, b, label, off=0.0, side=1, cls="dmh", gap=1.2,
            outside=None, txt_off=None, anchor="middle"):
        """One linear dimension: witness lines out to the dimension line,
        arrows on it, the figure over it. `off` is how far the dimension line
        stands off the two points, on the `side` given by the normal.

        Below a certain span the arrows have nowhere to sit, so they go on the
        OUTSIDE pointing in - the same thing a drawing office does, and the
        reason it is a rule here rather than a judgement is that the span is
        known: it is the distance between the two points.
        """
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        if n < 1e-9:
            return
        ux, uy = dx / n, dy / n
        nx, ny = -uy * side, ux * side
        a2 = (a[0] + nx * off, a[1] + ny * off)
        b2 = (b[0] + nx * off, b[1] + ny * off)
        if abs(off) > 1e-9:
            self.line((a[0] + nx * gap, a[1] + ny * gap),
                      (a2[0] + nx * gap * 2, a2[1] + ny * gap * 2), "ext")
            self.line((b[0] + nx * gap, b[1] + ny * gap),
                      (b2[0] + nx * gap * 2, b2[1] + ny * gap * 2), "ext")
        if outside is None:
            outside = n < SZ["dm"] * 2.2
        if outside:
            self.line(a2, b2, "dim")
            tail = SZ["dm"] * 1.6
            self.line((a2[0] - ux * tail, a2[1] - uy * tail), a2, "dim",
                      ' marker-end="url(#aE)"')
            self.line((b2[0] + ux * tail, b2[1] + uy * tail), b2, "dim",
                      ' marker-end="url(#aE)"')
        else:
            self.line(a2, b2, "dim",
                      ' marker-start="url(#aS)" marker-end="url(#aE)"')
        if txt_off is None:
            txt_off = (nx * SZ["dm"] * 0.55 - ux * 0,
                       ny * SZ["dm"] * 0.55 - uy * 0)
            if abs(uy) > abs(ux):          # a vertical dimension
                txt_off = (nx * SZ["dm"] * 0.55, ny * SZ["dm"] * 0.55
                           + SZ["dm"] * 0.35)
            else:
                txt_off = (0.0, -SZ["dm"] * 0.5 if side * ny < 0
                           else SZ["dm"] * 1.0)
        m = ((a2[0] + b2[0]) / 2 + txt_off[0],
             (a2[1] + b2[1]) / 2 + txt_off[1])
        self.text(m, label, cls, anchor)

    def leader(self, tip, elbow, txt_p, rows, cls="sml", anchor="start"):
        self.pline([tip, elbow, txt_p], "ldr", ' marker-start="url(#aE)"')
        return self.lines((txt_p[0] + (2.0 if anchor == "start" else -2.0),
                           txt_p[1] - SZ[cls] * 0.25), rows, cls,
                          anchor=anchor)

    # -- output -------------------------------------------------------------
    def write(self, path):
        head = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {f(self.w)} {f(self.h)}" width="2400">\n'
                f'  <title>Loftseng - skraaskruesetet og vinkelklossen'
                f'</title>\n')
        # An explicit ground, not a CSS `background`: rsvg-convert renders
        # the CSS one to transparency, and a transparent sheet is a black
        # sheet the moment anything composites it.
        bg = (f'  <rect x="0" y="0" width="{f(self.w)}" '
              f'height="{f(self.h)}" fill="#ffffff"/>\n')
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head + DEFS + bg + "\n".join(self.body) + "\n</svg>\n")


class Frame:
    """Model millimetres to sheet millimetres for one view."""

    def __init__(self, ox, oy, k, sx=1.0, sy=1.0):
        self.ox, self.oy, self.k, self.sx, self.sy = ox, oy, k, sx, sy

    def p(self, x, y):
        return (self.ox + self.k * self.sx * x, self.oy + self.k * self.sy * y)

    def d(self, x, y):
        return (self.k * self.sx * x, self.k * self.sy * y)

    def s(self, v):
        return self.k * v


# ---------------------------------------------------------------------------
# TYPE AND STROKE - the family's numbers, scaled to this sheet
# ---------------------------------------------------------------------------
SZ = {k: v * STYLE_K for k, v in {
    "ttl": 50.0, "sub": 26.0, "pt": 31.0, "big": 27.0,
    "sml": 22.0, "dm": 23.0, "dmh": 23.0, "leg": 26.0, "jl": 27.0,
    "tiny": 19.0,
}.items()}

_SW = {k: v * STYLE_K for k, v in {
    "dim": 1.4, "ext": 0.9, "ldr": 1.5, "cut": 2.6, "pst": 3.0,
    "brd": 2.6, "gho": 1.7, "scrl": 1.8, "legbox": 1.6,
    "brk": 2.0, "ctr": 1.1, "pic": 2.6, "pic2": 1.6,
}.items()}

_HAL = 6.0 * STYLE_K            # the white halo under a figure on line work


def _style():
    s = SZ
    w = _SW
    return f"""  <style>
    svg  {{ background:#fff; }}
    text {{ font-family:Helvetica,Arial,sans-serif; fill:#000;
           font-size:{f(s['sml'])}px; }}
    .ttl {{ font-size:{f(s['ttl'])}px; font-weight:bold; }}
    .sub {{ font-size:{f(s['sub'])}px; }}
    .pt  {{ font-size:{f(s['pt'])}px; font-weight:bold; }}
    .big {{ font-size:{f(s['big'])}px; font-weight:bold; }}
    .sml {{ font-size:{f(s['sml'])}px; }}
    .tiny{{ font-size:{f(s['tiny'])}px; }}
    .tinyh{{ font-size:{f(s['tiny'])}px; paint-order:stroke; stroke:#fff;
           stroke-width:{f(_HAL)}px; }}
    .smh {{ font-size:{f(s['sml'])}px; paint-order:stroke; stroke:#fff;
           stroke-width:{f(_HAL)}px; }}
    .dm  {{ font-size:{f(s['dm'])}px; }}
    .dmh {{ font-size:{f(s['dm'])}px; paint-order:stroke; stroke:#fff;
           stroke-width:{f(_HAL)}px; }}
    .leg {{ font-size:{f(s['leg'])}px; font-weight:bold; }}
    .jl  {{ font-size:{f(s['jl'])}px; font-weight:bold; paint-order:stroke;
           stroke:#fff; stroke-width:{f(_HAL)}px; }}
    .wood{{ fill:url(#hatch); stroke:#000; stroke-width:{f(w['brd'])}; }}
    .mate{{ fill:#c4c4c4; stroke:#000; stroke-width:{f(w['pst'])}; }}
    .brd {{ fill:#ececec; stroke:#000; stroke-width:{f(w['brd'])}; }}
    .plain{{ fill:#fff; stroke:#000; stroke-width:{f(w['brd'])}; }}
    .gho {{ fill:none; stroke:#000; stroke-width:{f(w['gho'])};
           stroke-dasharray:{f(10.9 * STYLE_K)} {f(6.8 * STYLE_K)}; }}
    .ctr {{ fill:none; stroke:#000; stroke-width:{f(w['ctr'])};
           stroke-dasharray:{f(9 * STYLE_K)} {f(3 * STYLE_K)}
           {f(1.5 * STYLE_K)} {f(3 * STYLE_K)}; }}
    .dot {{ fill:none; stroke:#000; stroke-width:{f(w['scrl'])};
           stroke-dasharray:{f(0.6 * STYLE_K)} {f(4.5 * STYLE_K)};
           stroke-linecap:round; }}
    .dim {{ fill:none; stroke:#000; stroke-width:{f(w['dim'])}; }}
    .ext {{ fill:none; stroke:#000; stroke-width:{f(w['ext'])}; }}
    .ldr {{ fill:none; stroke:#000; stroke-width:{f(w['ldr'])}; }}
    .brk {{ fill:none; stroke:#000; stroke-width:{f(w['brk'])}; }}
    .cut {{ fill:none; stroke:#000; stroke-width:{f(w['cut'])}; }}
    .scr {{ fill:#fff; stroke:#000; stroke-width:{f(w['scrl'])}; }}
    .scrd{{ fill:none; stroke:#000; stroke-width:{f(w['scrl'])};
           stroke-dasharray:{f(8.8 * STYLE_K)} {f(5.7 * STYLE_K)}; }}
    .pic {{ fill:none; stroke:#000; stroke-width:{f(w['pic'])};
           stroke-linecap:round; stroke-linejoin:round; }}
    .picf{{ fill:#fff; stroke:#000; stroke-width:{f(w['pic'])};
           stroke-linecap:round; stroke-linejoin:round; }}
    .pic2{{ fill:none; stroke:#000; stroke-width:{f(w['pic2'])};
           stroke-linecap:round; stroke-linejoin:round; }}
    .fld {{ fill:none; stroke:#000; stroke-width:{f(w['legbox'])}; }}
    .era {{ fill:none; stroke:#fff; stroke-width:{f(w['pic'])}; }}
  </style>
"""


DEFS = ""      # filled in by build()


def _defs():
    aw = 13.0 * STYLE_K * 2.2
    return f"""  <defs>
    <marker id="aE" markerWidth="13" markerHeight="10" refX="12" refY="4.5"
      orient="auto"><path d="M0,0 L12,4.5 L0,9 z" fill="#000"/></marker>
    <marker id="aS" markerWidth="13" markerHeight="10" refX="1" refY="4.5"
      orient="auto"><path d="M12,0 L0,4.5 L12,9 z" fill="#000"/></marker>
    <pattern id="hatch" width="{f(14 * STYLE_K)}" height="{f(14 * STYLE_K)}"
      patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="{f(14 * STYLE_K)}" height="{f(14 * STYLE_K)}"
        fill="#dcdcdc"/>
      <line x1="0" y1="0" x2="0" y2="{f(14 * STYLE_K)}" stroke="#000"
        stroke-width="{f(1.7 * STYLE_K)}"/></pattern>
  </defs>
""" + _style()


# ---------------------------------------------------------------------------
# WHAT THE MODEL KNOWS
# ---------------------------------------------------------------------------
def _dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _corners(part):
    e = part.extents
    return [(x, y, z) for x in e[0] for y in e[1] for z in e[2]]


def seat(G, jid):
    """Everything one toe-screw seat is, in ITS OWN local frame.

    The frame is derived, never typed: `n` is the outward normal of the face
    the screw is driven from (the model's own seat_face), `u` is the in-face
    part of the screw's direction - which is the way to the FREE END, because
    a toe screw always leans towards the joint it is crossing - and `w` is the
    third one. x is measured from that free end INTO the piece, y down from
    the face into the wood. Both sections on this sheet are drawn in it, which
    is what makes them comparable at a glance.
    """
    specs = [s for s in G.FASTENER_SPECS if s.get("toe") and s["jid"] == jid]
    assert specs, f"modellen har ingen skråskrue i {jid}"
    s0 = specs[0]
    sax, ssg, surf = s0["seat_face"]
    n = [0.0, 0.0, 0.0]
    n[sax] = ssg
    n = tuple(n)
    dirv = tuple(s0["direction"])
    dn = _dot(dirv, n)
    tang = tuple(c - dn * m for c, m in zip(dirv, n))
    ln = math.sqrt(_dot(tang, tang))
    u = tuple(c / ln for c in tang)
    w = _cross(n, u)
    alpha = math.degrees(math.asin(-dn))

    through, into = s0["through"], s0["into"]
    end_u = max(_dot(c, u) for c in _corners(through))

    def loc(p):
        return (end_u - _dot(p, u), ssg * (surf - p[sax]), _dot(p, w))

    def box(part):
        cs = [loc(c) for c in _corners(part)]
        return (min(c[0] for c in cs), max(c[0] for c in cs),
                min(c[1] for c in cs), max(c[1] for c in cs),
                min(c[2] for c in cs), max(c[2] for c in cs))

    dep = s0["seat"]
    mouths = []
    for s in specs:
        if s["through"] is not through:
            continue
        m = tuple(a - d * dep for a, d in zip(s["anchor"], s["direction"]))
        mouths.append(loc(m))
    back = mouths[0][0]
    assert abs(mouths[0][1]) < 1e-6, (
        f"{jid}: munningssenteret ligger {mouths[0][1]:+.3f} mm fra flaten - "
        f"setet er ikke boret fra flaten det påstår")
    want = (G.TOE_BENCH_POST if jid == "J8-B" else G.TOE_STUB_RAIL)["back"]
    assert abs(back - want) < 1e-6, (
        f"{jid}: målt kantavstand {back:.3f} mm, modellen sier {want:g}")

    cov = [c for c in G.TOE_SEAT_COVER if c[0].startswith(jid + " ")]
    assert cov, f"{jid}: ingen setedekning målt i modellen"
    d = s0["d"]
    head_d = G.SCREW_HEAD_D[int(round(d))]
    a_rad = math.radians(alpha)
    tb = box(through)
    return dict(
        jid=jid, alpha=alpha, a=a_rad, seat=dep, d=d, head_d=head_d,
        head_h=(head_d - d) / 2.0, length=s0["length"],
        seat_d=G.TOE_SEAT_D, back=back,
        mouth_len=G.TOE_JIG_ELLIPSE[jid][0], mouth_w=G.TOE_JIG_ELLIPSE[jid][1],
        cover=min(c[1] for c in cov), cover_rim=min(c[2] for c in cov),
        through=through.label, into=into.label,
        thick=tb[3] - tb[2], face_w=tb[5] - tb[4],
        seats_w=[m[2] - tb[4] for m in mouths],
        into_box=box(into), n_seats=len(mouths),
    )


# ---------------------------------------------------------------------------
# THE PAGE PLAN
# ---------------------------------------------------------------------------
MARG = 18.0
COL_A = 18.0
COL_B = 566.0
ROW_1 = 54.0
ROW_2 = 264.0
COL_4 = 470.0

# The window every section in field 1 is drawn in, in model millimetres of
# the local frame: x from the free end into the piece, y down from the face.
WIN = (-46.0, 74.0, -19.0, 42.0)
K1 = 2.0                                   # field 1: 2:1
K2 = 1.0                                   # fields 2 and 3: 1:1


def _v(a, t):
    return (a[0] * t, a[1] * t)


def _add(*ps):
    return (sum(p[0] for p in ps), sum(p[1] for p in ps))


def zigzag(sh, fr, p0, p1, amp=1.4, period=5.5, cls="brk"):
    """The family's break line: the edge is not really there, the piece runs
    on past it."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dy)
    if n < 1e-9:
        return
    ux, uy = dx / n, dy / n
    steps = max(2, int(round(n / period)))
    pts = []
    for i in range(steps + 1):
        t = n * i / steps
        s = amp if i % 2 else -amp
        if i in (0, steps):
            s = 0.0
        pts.append(fr.p(p0[0] + ux * t - uy * s, p0[1] + uy * t + ux * s))
    sh.pline(pts, cls)


def screw_outline(S, mouth, a, p, lift=0.0):
    """The countersunk screw as it lies in its seat: head disc on the pocket
    bottom (or `lift` back up the axis, which is the pilot-rim rest), cone
    down to the shank, shank to the point."""
    hd, d, hh = S["head_d"] / 2.0, S["d"] / 2.0, S["head_h"]
    top = _add(mouth, _v(a, S["seat"] - lift))
    bot = _add(top, _v(a, hh))
    tip = _add(mouth, _v(a, S["length"] - lift))
    shoulder = _add(mouth, _v(a, S["length"] - lift - 1.3 * S["d"]))
    return [_add(top, _v(p, -hd)), _add(top, _v(p, hd)),
            _add(bot, _v(p, d)), _add(shoulder, _v(p, d)), tip,
            _add(shoulder, _v(p, -d)), _add(bot, _v(p, -d))]


def section(sh, S, ox, oy, head, sub, mate_txt, end_txt, rows, dashed=False):
    """One field-1 section: the pocket along the screw's own axis, 2:1."""
    XL, XR, YT, YB = WIN
    fr = Frame(ox, oy, K1)
    P = fr.p
    al = S["a"]
    a = (-math.cos(al), math.sin(al))          # into the wood, towards the end
    p = (math.sin(al), math.cos(al))           # square to it, deeper
    back, dep, r = S["back"], S["seat"], S["seat_d"] / 2.0
    half = S["mouth_len"] / 2.0
    M = (back, 0.0)
    B = _add(M, _v(a, dep))
    Bn, Bf = _add(B, _v(p, -r)), _add(B, _v(p, r))

    sh.text((ox + fr.s(XL), oy + fr.s(YT) - SZ["big"] * 1.55), head, "big")
    sh.text((ox + fr.s(XL), oy + fr.s(YT) - SZ["big"] * 0.45), sub, "sml")

    # -- the member the screw goes INTO, and the one it is driven through ----
    ib = S["into_box"]
    mx0, mx1 = max(XL, ib[0]), min(0.0, ib[1])
    my0, my1 = max(YT, ib[2]), min(YB, ib[3])
    sh.poly([P(mx0, my0), P(mx1, my0), P(mx1, my1), P(mx0, my1)], "mate")
    if ib[0] < XL - 1e-6:
        zigzag(sh, fr, (mx0, my0), (mx0, my1))
    if ib[2] < YT - 1e-6:
        zigzag(sh, fr, (mx0, my0), (mx1, my0))
    if ib[3] > YB + 1e-6:
        zigzag(sh, fr, (mx0, my1), (mx1, my1))

    wood = [(0.0, 0.0), (back - half, 0.0), Bn, Bf, (back + half, 0.0),
            (XR, 0.0), (XR, YB), (0.0, YB)]
    sh.poly([P(*q) for q in wood], "wood")
    zigzag(sh, fr, (XR, 0.0), (XR, YB))
    zigzag(sh, fr, (XR, YB), (0.0, YB))

    # the face itself, and the free end - the two planes every number on this
    # section is measured from, so they carry the heavy line
    sh.line(P(0.0, 0.0), P(back - half, 0.0), "cut")
    sh.line(P(back + half, 0.0), P(XR, 0.0), "cut")
    sh.line(P(0.0, 0.0), P(0.0, YB), "cut")
    sh.line(P(*Bn), P(*Bf), "cut")

    # -- the axis, and the angle that is the whole point --------------------
    sh.line(P(*_add(M, _v(a, -20.0))), P(*_add(M, _v(a, S["length"] + 6.0))),
            "ctr")
    # The arc stands OUTSIDE the wood, between the face and the axis produced
    # back out of the mouth: that is the angle a builder can actually set, and
    # the only quadrant round the mouth with nothing else in it.
    ar = 12.0
    sh.arc(P(*M), fr.s(ar), 0.0, -al, "dim")
    sh.text(P(back + ar * 1.5 * math.cos(al / 2),
              -ar * 1.5 * math.sin(al / 2) + 1.2),
            f"{nb(S['alpha'], 0)}°", "dmh", "middle")

    # -- the screw, and the rest it cannot be relied on to find -------------
    if dashed:
        ring = screw_outline(S, M, a, p, S["head_h"])
        sh.pline([P(*q) for q in ring] + [P(*ring[0])], "scrd")
    sh.poly([P(*q) for q in screw_outline(S, M, a, p)], "scr")

    # -- dimensions ---------------------------------------------------------
    sh.dim(P(0.0, 0.0), P(back, 0.0), nb(back, 0), off=fr.s(15.0), side=-1)
    sh.line(P(back, 0.0), P(back, -16.0), "ext")
    sh.dim(P(*M), P(*B), nb(dep, 0), off=fr.s(8.0), side=1)

    cov = S["cover"]
    hx = _add(B, _v(p, -S["head_d"] / 2.0))
    sh.line(P(hx[0], hx[1]), P(XR - 12.0, hx[1]), "ext")
    sh.dim(P(XR - 16.0, 0.0), P(XR - 16.0, cov), nb(cov, 2),
           off=0.0, side=1, txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 1.35),
           anchor="start")
    sh.text(P(XR - 15.0, cov + 5.0), "under flaten", "tinyh", "start")

    # -- what the heavy lines are -------------------------------------------
    sh.text(P(XR - 2.0, -3.0), "flaten", "smh", "end")
    sh.text(P(1.5, YB - 2.5), end_txt, "smh", "start")
    sh.text(P(mx0 + 1.5, my1 - 2.5), mate_txt, "smh", "start")
    sh.text(P(30.0, 31.0), S["jid"], "jl", "middle")

    # the right angle at the bottom of the pocket - drawn, not asserted in
    # prose, because it is the one thing a builder gets wrong by eye
    sq = [_add(B, _v(a, 3.2)), _add(_add(B, _v(a, 3.2)), _v(p, 3.2)),
          _add(B, _v(p, 3.2))]
    sh.pline([P(*t) for t in sq], "ext")

    ty = oy + fr.s(YB) + SZ["sml"] * 2.2
    sh.lines((ox + fr.s(XL), ty), rows, "sml")
    return ty + len(rows) * SZ["sml"] * 1.35


def field1(sh, SB, SS):
    """FIELD 1 - the two sections, side by side, 2:1."""
    y = ROW_1
    sh.text((COL_A, y), "1 · SNITT LANGS SKRUEAKSEN — LOMMEN, BUNNEN OG "
            "HODET, 2:1", "pt")
    y += SZ["pt"] * 0.95
    sh.text((COL_A, y),
            "Vinkelen står MELLOM AKSEN OG FLATEN. Setet bores LANGS aksen, "
            "ikke ned i treet, og bunnen står 90° på aksen.", "sub")
    top = y + SZ["sub"] * 1.5
    ox = COL_A + K1 * (-WIN[0])
    oy = top + K1 * (-WIN[2]) + SZ["big"] * 2.2
    b = section(
        sh, SB, ox, oy, "J8-B · 25° · treskrue 6×80",
        "bakre benkevange → bakre hjørnestolpe",
        "hjørnestolpe", "bakre benkevange",
        [f"Lomme ⌀{nb(SB['seat_d'], 0)}, flat bunn, "
         f"{nb(SB['seat'], 0)} mm LANGS aksen. Hodet ⌀{nb(SB['head_d'])} "
         f"ligger i bunnen;",
         f"høyeste punkt {nb(SB['cover'], 2)} mm under flaten.",
         f"STIPLET: konusen hviler på ⌀{nb(SB['d'], 0)}-forborkanten i "
         f"stedet. Da står hodet",
         f"{nb(SB['head_h'])} mm høyere langs aksen og dekket er "
         f"{nb(SB['cover_rim'], 2)} mm.",
         f"Begge over kravet {nb(1.0)} mm."],
        dashed=True)
    s = section(
        sh, SS, ox + K1 * (WIN[1] - WIN[0]) + 46.0, oy,
        "J10 · 30° · treskrue 5×60",
        "stubbefot → bakre benkevange",
        "benkevange", "stubbefot",
        [f"Lomme ⌀{nb(SS['seat_d'], 0)}, flat bunn, "
         f"{nb(SS['seat'], 0)} mm LANGS aksen. Hodet ⌀{nb(SS['head_d'])} "
         f"ligger i bunnen;",
         f"høyeste punkt {nb(SS['cover'], 2)} mm under flaten, krav "
         f"{nb(1.0)} mm.",
         f"{nb(SS['back'], 0)} mm måles fra FOTENS TOPP, ikke fra en ende:",
         "skruen går opp i benkevangen som hviler på foten.",
         "Snittet ligger på siden — fotens topp er til venstre."])
    return max(b, s)


# ---------------------------------------------------------------------------
# FIELD 2 - THE MOUTH, HEAD ON, 1:1
# ---------------------------------------------------------------------------
# An 18 mm Forstner cutting along a leaning axis does not leave an 18 mm hole
# in the face. It leaves an ellipse D/sin(angle) long, and that ellipse is
# what the builder sets out and what eats the edge distance. Both views are
# 1:1, so a pencil mark can be held against the paper.
def mouth_ellipses(S):
    """The mouth, and the pocket bottom seen through it, in face coordinates.

    Semi-axes as (along, across): `along` runs the way the axis leans, which
    is towards the free end, and `across` is square to it in the face. The
    bottom is a full-diameter disc standing square to the axis, so seen
    through the mouth it is foreshortened to r*sin(angle) - and it reaches
    NEARER the free end than the mouth does, which is the edge distance that
    actually decides the joint.
    """
    r = S["seat_d"] / 2.0
    sa = math.sin(S["a"])
    floor_c = S["back"] - S["seat"] * math.cos(S["a"])
    return dict(mouth=(S["mouth_len"] / 2.0, S["mouth_w"] / 2.0),
                floor=(r * sa, r), floor_c=floor_c,
                near_mouth=S["back"] - S["mouth_len"] / 2.0,
                near_floor=floor_c - r * sa)


def field2(sh, SB, SS):
    """FIELD 2 - both mouths at 1:1, on the face they are actually bored in."""
    y = ROW_1
    sh.text((COL_B, y), "2 · MUNNINGEN SETT RETT PÅ, 1:1", "pt")
    y += SZ["pt"] * 0.95
    sh.text((COL_B, y), "Setet er ⌀18, men munningen er en ELLIPSE, "
            "18/sin(vinkelen) lang. Det er ellipsen du merker opp etter.",
            "sub")
    top = y + SZ["sub"] * 1.6 + SZ["big"] * 2.2

    # ---- J8-B: two mouths in the front face of the back bench rail --------
    E = mouth_ellipses(SB)
    fw, r = SB["face_w"], SB["seat_d"] / 2.0
    XR2, POST = 84.0, 22.0
    ox, oy = COL_B + POST + 12.0, top + fw + 30.0
    fr = Frame(ox, oy, K2, 1.0, -1.0)
    P = fr.p
    sh.text((COL_B, top - SZ["big"] * 1.5), "J8-B · vangens forside, to "
            "lommer", "big")
    sh.text((COL_B, top - SZ["big"] * 0.35),
            "bakre benkevange 48×68, sett mot enden", "sml")
    sh.poly([P(-POST, 0.0), P(0.0, 0.0), P(0.0, fw), P(-POST, fw)], "mate")
    zigzag(sh, fr, (-POST, 0.0), (-POST, fw))
    sh.poly([P(0.0, 0.0), P(XR2, 0.0), P(XR2, fw), P(0.0, fw)], "brd")
    zigzag(sh, fr, (XR2, 0.0), (XR2, fw))
    sh.line(P(0.0, 0.0), P(0.0, fw), "cut")
    sh.text(P(-POST + 1.5, fw * 0.5), "stolpen", "tinyh")
    sh.text(P(2.5, fw - 5.0), "bakre benkevange", "smh")
    sh.text(P(-1.5, fw + 4.0), "vangeenden", "tinyh", "end")
    for w in SB["seats_w"]:
        sh.ellipse(P(E["floor_c"], w), E["floor"][0], E["floor"][1], "gho")
        sh.ellipse(P(SB["back"], w), E["mouth"][0], E["mouth"][1], "plain")
        sh.line(P(SB["back"] - E["mouth"][0] - 4.0, w),
                P(SB["back"] + E["mouth"][0] + 4.0, w), "ctr")
        sh.ellipse(P(E["floor_c"], w), E["floor"][0], E["floor"][1], "gho")
    sh.line(P(SB["back"], -4.0), P(SB["back"], fw + 24.0), "ctr")

    lo, hi = SB["seats_w"][0], SB["seats_w"][-1]
    dia = f"⌀{nb(2 * r, 0)}"
    chain = [(0.0, lo - r, nb(lo - r, 0)), (lo - r, lo + r, dia),
             (lo + r, hi - r, nb(hi - lo - 2 * r, 0)),
             (hi - r, hi + r, dia), (hi + r, fw, nb(fw - hi - r, 0))]
    for w0, w1, lab in chain:
        sh.dim(P(XR2 - 3.0, w0), P(XR2 - 3.0, w1), lab, off=10.0, side=1,
               txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 0.35), anchor="start")
    sh.dim(P(XR2 - 3.0, 0.0), P(XR2 - 3.0, fw), nb(fw, 0), off=24.0, side=1,
           txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 0.35), anchor="start")
    mh = E["mouth"][0]
    sh.dim(P(SB["back"] - mh, fw), P(SB["back"] + mh, fw),
           nb(SB["mouth_len"]), off=9.0, side=-1)
    sh.dim(P(0.0, fw), P(SB["back"], fw), nb(SB["back"], 0), off=20.0, side=-1)
    sh.dim(P(0.0, 0.0), P(E["near_mouth"], 0.0), nb(E["near_mouth"]),
           off=11.0, side=1)
    sh.dim(P(0.0, 0.0), P(E["near_floor"], 0.0), nb(E["near_floor"]),
           off=22.0, side=1)
    sh.leader(P(E["floor_c"], lo - r), P(E["floor_c"] + 8.0, 7.0),
              P(E["floor_c"] + 10.0, 7.0), ["lommebunnen"], "tiny", "start")

    # ---- J10: one mouth in the inboard face of the stub leg ---------------
    F = mouth_ellipses(SS)
    sw, YB2, RAIL = SS["face_w"], 92.0, 20.0
    ox2 = COL_B + 190.0
    oy2 = top + RAIL
    fr2 = Frame(ox2, oy2, K2)
    Q = fr2.p
    sh.text((ox2 - 44.0, top - SZ["big"] * 1.5),
            "J10 · fotens innerside", "big")
    sh.text((ox2 - 44.0, top - SZ["big"] * 0.35),
            "stubbefot 48×68, sett fra sengens midte", "sml")
    sh.poly([Q(0.0, -RAIL), Q(sw, -RAIL), Q(sw, 0.0), Q(0.0, 0.0)], "mate")
    zigzag(sh, fr2, (0.0, -RAIL), (sw, -RAIL))
    sh.poly([Q(0.0, 0.0), Q(sw, 0.0), Q(sw, YB2), Q(0.0, YB2)], "brd")
    zigzag(sh, fr2, (0.0, YB2), (sw, YB2))
    sh.line(Q(0.0, 0.0), Q(sw, 0.0), "cut")
    sh.text(Q(2.5, -RAIL + 7.0), "benkevangen", "tinyh")
    sh.text(Q(2.5, YB2 - 4.0), "stubbefot", "smh")
    sh.text(Q(sw + 2.0, -2.5), "fotens topp", "tinyh")
    wc = SS["seats_w"][0]
    sh.ellipse(Q(wc, F["floor_c"]), F["floor"][1], F["floor"][0], "gho")
    sh.ellipse(Q(wc, SS["back"]), F["mouth"][1], F["mouth"][0], "plain")
    sh.line(Q(wc, -6.0), Q(wc, YB2 - 4.0), "ctr")
    sh.line(Q(wc - F["mouth"][1] - 4.0, SS["back"]),
            Q(wc + F["mouth"][1] + 4.0, SS["back"]), "ctr")
    sh.dim(Q(0.0, 0.0), Q(0.0, F["near_mouth"]), nb(F["near_mouth"], 0),
           off=10.0, side=1, txt_off=(-SZ["dm"] * 0.5, SZ["dm"] * 0.35),
           anchor="end")
    sh.dim(Q(0.0, 0.0), Q(0.0, F["near_floor"]), nb(F["near_floor"]),
           off=23.0, side=1, txt_off=(-SZ["dm"] * 0.5, SZ["dm"] * 0.35),
           anchor="end")
    sh.dim(Q(sw, 0.0), Q(sw, SS["back"]), nb(SS["back"], 0), off=11.0,
           side=-1, txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 0.35), anchor="start")
    fh_ = F["mouth"][0]
    sh.dim(Q(sw, SS["back"] - fh_), Q(sw, SS["back"] + fh_),
           nb(SS["mouth_len"], 0), off=24.0, side=-1,
           txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 0.35), anchor="start")
    for a0, a1, lab in [(0.0, wc - 9.0, nb(wc - 9.0, 0)),
                        (wc - 9.0, wc + 9.0, f"⌀{nb(SS['seat_d'], 0)}"),
                        (wc + 9.0, sw, nb(sw - wc - 9.0, 0))]:
        sh.dim(Q(a0, YB2 - 3.0), Q(a1, YB2 - 3.0), lab, off=10.0, side=1)
    sh.dim(Q(0.0, YB2 - 3.0), Q(sw, YB2 - 3.0), nb(sw, 0), off=22.0, side=1)

    rows = [
        f"J8-B: to munninger {nb(SB['mouth_len'])} × {nb(SB['mouth_w'], 0)} "
        f"mm, langaksen mot vangeenden. Senteravstand "
        f"{nb(hi - lo, 0)} mm gir {nb(hi - lo - 2 * r, 0)} mm tre mellom "
        f"lommene — kravet er én skruediameter.",
        f"Stiplet ellipse = lommebunnen sett gjennom munningen. Den ligger "
        f"{nb(E['near_floor'])} mm fra endeveden mot munningens "
        f"{nb(E['near_mouth'])} mm, så det er BUNNEN som styrer "
        f"kantavstanden.",
        f"J10: én munning {nb(SS['mouth_len'], 0)} × {nb(SS['mouth_w'], 0)} "
        f"mm i fotens innerside, {nb(SS['back'], 0)} mm ned fra fotens topp. "
        f"Foten er 48×68 og det er 48-flaten skruen går inn i.",
    ]
    wide = SHEET_W - MARG - COL_B
    out = []
    for row in rows:
        out += wrap(row, wide)
    ty = max(oy + 26.0, oy2 + YB2 + 34.0)
    sh.lines((COL_B, ty), out, "sml")
    return ty + len(out) * SZ["sml"] * 1.35


# ---------------------------------------------------------------------------
# FIELD 3 - THE ANGLE BLOCK, EXPLODED
# ---------------------------------------------------------------------------
# The block is the model's own shop aid: TOE_JIG_PLIES pieces of the batten
# section, TOE_JIG_LEN long, screwed face to face. Everything below follows
# from that and from the angle - except the ONE number the model has no
# opinion about, which is where along the block the hole is marked out.
JIG_HOLE_END = 40.0     # mm from the block's end to the hole axis. Free: it
#                         only has to leave the Forstner solid wood all round
#                         and leave the sole cut inside the length. 40 does
#                         both at both angles, and it is the same mark on both
#                         blocks, which is worth more than a tuned number.


def jig(G, S):
    """The block for one angle, in its own (u, w) side view.

    u runs through the bored faces - the two plies stack along it, so u is
    also the direction they come apart in - and w runs down the length from
    the intact end. The sole is the plane through the hole axis at mid
    thickness, tilted by the angle; both blocks' soles therefore turn about
    the SAME point, which is the drawing's way of saying that the two blocks
    are one block with one number changed.
    """
    u = G.TOE_JIG_PLIES * G.BATTEN_W
    return dict(u=u, ply=G.BATTEN_W, v=G.BATTEN_H, w=float(G.TOE_JIG_LEN),
                pivot=(u / 2.0, G.TOE_JIG_LEN - JIG_HOLE_END),
                slope=math.tan(S["a"]), sole_len=u / math.cos(S["a"]),
                guide=u / 2.0)


def field3(sh, G, SB, SS):
    """FIELD 3 - two 48x68x200 pieces, one hole, one bevel cut."""
    J, J2 = jig(G, SB), jig(G, SS)
    r = SB["seat_d"] / 2.0
    y = ROW_2
    sh.text((COL_A, y), "3 · VINKELKLOSSEN — BORJIGGEN, EKSPLODERT, 1:1", "pt")
    y += SZ["pt"] * 0.95
    sh.text((COL_A, y),
            "Én kloss per vinkel. Hullet bores VINKELRETT gjennom begge "
            "bitene mens klossen ennå er firkantet. Sålen kappes ETTERPÅ.",
            "sub")
    top = y + SZ["sub"] * 1.8

    GAP = 26.0
    ox = COL_A + 44.0
    oy = top + 10.0

    def A(u, w):                       # ply nearest the sole's shallow end
        return (ox + u, oy + w)

    def B(u, w):                       # the ply the drill enters through
        return (ox + u + GAP, oy + w)

    w0 = J["pivot"][1]
    sole = lambda u: w0 + (u - J["pivot"][0]) * J["slope"]
    sole2 = lambda u: w0 + (u - J2["pivot"][0]) * J2["slope"]

    # the square block the hole is bored in, before anything is cut off
    for M, u0, u1 in ((A, 0.0, J["ply"]), (B, J["ply"], J["u"])):
        sh.poly([M(u0, 0.0), M(u1, 0.0), M(u1, J["w"]), M(u0, J["w"])], "gho")
    # the finished piece
    sh.poly([A(0.0, 0.0), A(J["ply"], 0.0), A(J["ply"], sole(J["ply"])),
             A(0.0, sole(0.0))], "brd")
    sh.poly([B(J["ply"], 0.0), B(J["u"], 0.0), B(J["u"], sole(J["u"])),
             B(J["ply"], sole(J["ply"]))], "brd")
    sh.line(A(0.0, sole(0.0)), A(J["ply"], sole(J["ply"])), "cut")
    sh.line(B(J["ply"], sole(J["ply"])), B(J["u"], sole(J["u"])), "cut")
    # the same cut at the other angle, turning about the same point
    sh.line(A(-12.0, sole2(-12.0)), A(J["ply"], sole2(J["ply"])), "scrd")
    sh.line(B(J["ply"], sole2(J["ply"])), B(J["u"], sole2(J["u"])), "scrd")

    # the hole: bored square through both, so its walls run the whole width
    for d in (-r, r):
        sh.line(A(0.0, w0 + d), A(J["ply"], w0 + d), "scrd")
        sh.line(B(J["ply"], w0 + d), B(J["u"], w0 + d), "scrd")
    sh.line(A(-14.0, w0), A(J["ply"], w0), "ctr")
    sh.line(B(J["ply"], w0), B(J["u"] + 16.0, w0), "ctr")

    # the two pieces come apart along the hole's own axis, and what holds them
    # together is drawn the way every fastener on a HANNA page is: dotted
    for w in (34.0, 118.0):
        sh.line(A(0.0, w), B(J["ply"] + 22.0, w), "dot")
        sh.circle(A(0.0, w), 1.6, "scr")

    # -- the two angles, at one corner, so the complement is visible --------
    c = A(0.0, sole(0.0))
    sh.line(c, (c[0] + 34.0, c[1]), "ext")
    sh.arc(c, 13.0, 0.0, SB["a"], "dim")
    sh.arc(c, 21.0, SB["a"], -math.pi / 2, "dim")
    sh.text((c[0] + 19.0, c[1] + 5.5), f"{nb(SB['alpha'], 0)}°", "dmh")
    sh.text((c[0] + 15.0, c[1] - 12.0), f"{nb(90 - SB['alpha'], 0)}°", "dmh")
    sh.text(A(-14.0, sole2(-12.0) - 1.5), f"{nb(SS['alpha'], 0)}°", "dmh",
            "end")

    # -- dimensions ---------------------------------------------------------
    sh.dim(A(0.0, 0.0), A(J["ply"], 0.0), nb(J["ply"], 0), off=13.0, side=-1)
    sh.dim(B(J["ply"], 0.0), B(J["u"], 0.0), nb(J["ply"], 0), off=13.0,
           side=-1)
    sh.dim(B(J["u"], 0.0), B(J["u"], J["w"]), nb(J["w"], 0), off=26.0,
           side=-1, txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 0.35), anchor="start")
    sh.dim(B(J["u"], w0), B(J["u"], J["w"]), nb(JIG_HOLE_END, 0), off=13.0,
           side=-1, txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 0.35), anchor="start")
    sh.leader(B(J["ply"] + 10.0, w0 - r), B(J["ply"] + 16.0, w0 - 40.0),
              B(J["ply"] + 18.0, w0 - 40.0),
              [f"⌀{nb(2 * r, 0)} gjennom", "begge bitene"], "tiny")
    sh.text(A(-40.0, 12.0), "48×68×200", "smh")
    sh.text(A(-40.0, 12.0 + SZ["sml"] * 1.3), "to like biter", "smh")
    sh.text(B(J["u"] + 4.0, 12.0), "boret", "tinyh")
    sh.text(B(J["u"] + 4.0, 12.0 + SZ["tiny"] * 1.3), "går inn her", "tinyh")
    sh.text(A(2.0, J["w"] - 4.0), "kappes av", "tinyh")

    # -- the sole, seen square on: the one measurement that catches the ------
    # -- complement mistake -------------------------------------------------
    sx = ox + J["u"] + GAP + 74.0
    for i, (S, Jx) in enumerate(((SB, J), (SS, J2))):
        sy = oy + i * 108.0
        L, V = Jx["sole_len"], Jx["v"]
        sh.text((sx, sy - 7.0),
                f"SÅLEN, {nb(S['alpha'], 0)}°-KLOSSEN — kontrollmål", "big")
        sh.rect(sx, sy, L, V, "brd")
        sh.ellipse((sx + L / 2.0, sy + V / 2.0), S["mouth_len"] / 2.0,
                   S["mouth_w"] / 2.0, "plain")
        sh.line((sx + L / 2.0 - S["mouth_len"] / 2.0 - 5.0, sy + V / 2.0),
                (sx + L / 2.0 + S["mouth_len"] / 2.0 + 5.0, sy + V / 2.0),
                "ctr")
        sh.line((sx + L / 2.0, sy - 5.0), (sx + L / 2.0, sy + V + 5.0), "ctr")
        sh.dim((sx + L / 2.0 - S["mouth_len"] / 2.0, sy + V),
               (sx + L / 2.0 + S["mouth_len"] / 2.0, sy + V),
               nb(S["mouth_len"]), off=11.0, side=1)
        sh.dim((sx, sy + V / 2.0 - S["mouth_w"] / 2.0),
               (sx, sy + V / 2.0 + S["mouth_w"] / 2.0),
               nb(S["mouth_w"], 0), off=11.0, side=1,
               txt_off=(-SZ["dm"] * 0.5, SZ["dm"] * 0.35), anchor="end")
        sh.dim((sx, sy + V), (sx + L, sy + V), nb(L), off=23.0, side=1)
        sh.text((sx + 2.0, sy + V - 3.0), f"{nb(Jx['v'], 0)} bred", "tinyh")

    # -- the depth mark on the bit ------------------------------------------
    dx = sx + 162.0
    dy = oy + 6.0
    sh.text((dx - 16.0, dy - 13.0), "DYBDEMERKET", "big")
    shaft, headw, headh = 9.0, 18.0, 15.0
    tip = dy + 128.0
    sh.poly([(dx - shaft / 2, dy), (dx + shaft / 2, dy),
             (dx + shaft / 2, tip - headh), (dx - shaft / 2, tip - headh)],
            "plain")
    sh.poly([(dx - headw / 2, tip - headh), (dx + headw / 2, tip - headh),
             (dx + headw / 2, tip), (dx - headw / 2, tip)], "plain")
    sh.poly([(dx - 2.2, tip), (dx + 2.2, tip), (dx, tip + 7.0)], "plain")
    sh.line((dx - headw / 2, tip), (dx - headw / 2, tip + 3.5), "cut")
    sh.line((dx + headw / 2, tip), (dx + headw / 2, tip + 3.5), "cut")
    m1 = tip - headh - 26.0
    m2 = m1 - SB["seat"]
    for m in (m1, m2):
        sh.line((dx - shaft / 2 - 3.0, m), (dx + shaft / 2 + 3.0, m), "cut")
    sh.dim((dx + shaft / 2 + 3.0, m1), (dx + shaft / 2 + 3.0, m2),
           f"{nb(SB['seat'], 0)} / {nb(SS['seat'], 0)}", off=10.0, side=-1,
           txt_off=(SZ["dm"] * 0.5, SZ["dm"] * 0.2), anchor="start")
    sh.text((dx + shaft / 2 + 13.0, (m1 + m2) / 2 + SZ["dm"] * 1.3),
            "= setedybden", "tinyh")
    sh.text((dx - headw / 2 - 3.0, m1 + 2.0), "1 merk av", "tinyh", "end")
    sh.text((dx - headw / 2 - 3.0, m2 + 2.0), "2 bor hit", "tinyh", "end")
    sh.text((dx - headw / 2 - 3.0, tip + 3.0), "randen i", "tinyh", "end")
    sh.text((dx - headw / 2 - 3.0, tip + 3.0 + SZ["tiny"] * 1.2),
            "flukt med", "tinyh", "end")
    sh.text((dx - headw / 2 - 3.0, tip + 3.0 + SZ["tiny"] * 2.4),
            "sålen", "tinyh", "end")

    rows = [
        f"{G.TOE_JIG_PLIES} stk. {nb(J['ply'], 0)}×{nb(J['v'], 0)}×"
        f"{nb(J['w'], 0)} skrus FLATE MOT FLATE til én kloss "
        f"{nb(J['u'], 0)} mm tykk. Bor ⌀{nb(2 * r, 0)} VINKELRETT gjennom "
        f"begge, {nb(JIG_HOLE_END, 0)} mm fra enden og midt i bredden, MENS "
        f"KLOSSEN ER FIRKANTET.",
        f"Kapp så sålen av under hullet: kappsag med bladet vippet "
        f"{nb(SB['alpha'], 0)}° hhv. {nb(SS['alpha'], 0)}°. Da står sålen "
        f"{nb(90 - SB['alpha'], 0)}° hhv. {nb(90 - SS['alpha'], 0)}° på den "
        f"borede flaten — de to tallene er komplementer, og det er her den "
        f"gamle oppskriften tok feil.",
        f"KONTROLL: mål munningen i sålen. Den skal være "
        f"{nb(SB['mouth_len'])} × {nb(SB['mouth_w'], 0)} mm på "
        f"{nb(SB['alpha'], 0)}°-klossen og {nb(SS['mouth_len'], 0)} × "
        f"{nb(SS['mouth_w'], 0)} mm på {nb(SS['alpha'], 0)}°-klossen. "
        f"Er den for kort, ble vippen satt på komplementvinkelen.",
        f"DYBDEMERKE: hold boret i jiggen til randen flukter med sålen ved "
        f"hullaksen, merk av på skaftet der det kommer ut av klossen, og "
        f"flytt merket {nb(SB['seat'], 0)} mm (J8-B) / {nb(SS['seat'], 0)} mm "
        f"(J10) opp. Bor til det øverste merket.",
    ]
    ty = oy + J["w"] + 34.0
    out = []
    for row in rows:
        out += wrap(row, COL_4 - MARG - 40.0)
    sh.lines((COL_A, ty), out, "sml")
    return ty + len(out) * SZ["sml"] * 1.35


# ---------------------------------------------------------------------------
# FIELD 4 - THE BLOCK IN USE
# ---------------------------------------------------------------------------
# A picture, not a projection: the timber and the block are at 1:1 and come
# out of the same numbers as fields 1 and 3, the clamps and the drill are
# drawn the way the pictograms in docs/icons/hanna are - one stroke weight,
# round ends, no fill that is not there to hide a line behind it.
#
# One thing here is a RULE and not a taste. PRAKSIS says a dotted line is a
# fastener's way into its hole and an arrow is a piece of wood being moved,
# and the two are never mixed on one page. So the screw's direction is dotted,
# with the screw drawn on the line outside the wood - the same "exploded along
# its own axis" the step pages use - and there is no arrow anywhere near it.
CLAMP_UP = (34.0, 56.0)     # where on the block's two edges the clamps bite


def clamp(sh, at, work_bottom, out=1.0):
    """One F-clamp: a pad on the block, a pad under the timber, the bar down
    the outboard side, and the screw that closes it."""
    x, y = at
    pad, reach = 7.0, 13.0
    b = x + out * (pad + reach)
    sh.poly([(x - pad, y - 6.0), (x + pad, y - 6.0), (x + pad, y),
             (x - pad, y)], "picf")
    sh.pline([(x + out * pad, y - 6.0), (b, y - 6.0), (b, work_bottom + 15.0),
              (x + out * pad, work_bottom + 15.0)], "pic")
    sh.poly([(x - pad, work_bottom), (x + pad, work_bottom),
             (x + pad, work_bottom + 6.0), (x - pad, work_bottom + 6.0)],
            "picf")
    sh.line((x, work_bottom + 6.0), (x, work_bottom + 20.0), "pic")
    sh.line((x - 7.0, work_bottom + 20.0), (x + 7.0, work_bottom + 20.0),
            "pic")


def field4(sh, G, SB):
    """FIELD 4 - the block clamped down, the bit in the guide hole."""
    J = jig(G, SB)
    al = SB["a"]
    ca, sa = math.cos(al), math.sin(al)
    y = ROW_2
    sh.text((COL_4, y), "4 · KLOSSEN I BRUK", "pt")
    y += SZ["pt"] * 0.95
    sh.text((COL_4, y), "Klossen og virket 1:1, tvinger og drill skjematisk. "
            "Flaten ligger vannrett her; i sengen står den loddrett.", "sub")

    ox, oy = COL_4 + 108.0, y + 116.0
    T = 48.0                                   # the timber, seen on edge

    def L(q):
        return (ox + q[0], oy + q[1])

    ax, per = (ca, -sa), (sa, ca)              # up the hole; square to it
    e = (-sa, -ca)                             # up the block's bored faces
    sole_l = J["sole_len"]
    mid = sole_l / 2.0
    half = SB["mouth_len"] / 2.0
    m = (mid, 0.0)
    end_x = mid - SB["back"]                   # where the end grain falls
    cut = 84.0

    # -- the timber, and the block that saves its end grain -----------------
    sh.poly([L((end_x, 0.0)), L((sole_l + 92.0, 0.0)),
             L((sole_l + 92.0, T)), L((end_x, T))], "brd")
    sh.poly([L((end_x - 38.0, 0.0)), L((end_x, 0.0)), L((end_x, T)),
             L((end_x - 38.0, T))], "plain")
    sh.line(L((end_x, 0.0)), L((end_x, T)), "cut")

    # -- the block ----------------------------------------------------------
    top_l = _add((0.0, 0.0), _v(e, cut))
    top_r = _add((sole_l, 0.0), _v(e, cut))
    sh.poly([L((0.0, 0.0)), L((sole_l, 0.0)), L(top_r), L(top_l)], "picf")
    zigzag(sh, Frame(ox, oy, 1.0), top_l, top_r, amp=2.4, period=10.0,
           cls="pic2")
    # the mouth is OPEN - the sole line stops at it
    sh.line(L((mid - half, 0.0)), L((mid + half, 0.0)), "era")
    for k in (-1.0, 1.0):
        q = (mid + k * half, 0.0)
        reach = (sole_l - q[0]) * ca
        sh.line(L(q), L(_add(q, _v(ax, reach))), "pic2")

    # -- the bit: hidden in the guide hole, solid where it is in the open ---
    def seg(t0, t1, w):
        return [_add(_add(m, _v(ax, t0)), _v(per, -w)),
                _add(_add(m, _v(ax, t0)), _v(per, w)),
                _add(_add(m, _v(ax, t1)), _v(per, w)),
                _add(_add(m, _v(ax, t1)), _v(per, -w))]
    g = J["guide"]
    sh.pline([L(q) for q in seg(19.0, 33.0, 9.0)] +
             [L(seg(19.0, 33.0, 9.0)[0])], "gho")
    sh.pline([L(q) for q in seg(33.0, g, 4.5)][1:3], "gho")
    sh.pline([L(q) for q in seg(33.0, g, 4.5)][3:] +
             [L(seg(33.0, g, 4.5)[0])], "gho")
    sh.poly([L(q) for q in seg(g, 88.0, 4.5)], "picf")
    sh.poly([L(q) for q in
             [_add(_add(m, _v(ax, 88.0)), _v(per, -6.0)),
              _add(_add(m, _v(ax, 88.0)), _v(per, 6.0)),
              _add(_add(m, _v(ax, 100.0)), _v(per, 12.0)),
              _add(_add(m, _v(ax, 100.0)), _v(per, -12.0))]], "picf")
    sh.poly([L(q) for q in seg(100.0, 158.0, 15.0)], "picf")
    sh.poly([L(q) for q in
             [_add(_add(m, _v(ax, 112.0)), _v(per, 15.0)),
              _add(_add(m, _v(ax, 108.0)), _v(per, 44.0)),
              _add(_add(m, _v(ax, 130.0)), _v(per, 44.0)),
              _add(_add(m, _v(ax, 134.0)), _v(per, 15.0))]], "picf")
    sh.line(L(_add(_add(m, _v(ax, 122.0)), _v(per, -15.0))),
            L(_add(_add(m, _v(ax, 122.0)), _v(per, 15.0))), "pic2")

    # -- two clamps, both bars outboard -------------------------------------
    clamp(sh, L(_v(e, CLAMP_UP[0])), oy + T, out=-1.0)
    clamp(sh, L(_add((sole_l, 0.0), _v(e, CLAMP_UP[1]))), oy + T, out=1.0)

    # -- the screw's own way in: dotted, and it stops at the end grain ------
    run = (mid - end_x) / ca
    sh.line(L(m), L(_add(m, _v((-ca, sa), run))), "dot")
    sh.circle(L(_add(m, _v((-ca, sa), run))), 2.2, "scr")

    # -- labels -------------------------------------------------------------
    sh.line(L((end_x - 22.0, T + 20.0)), L((end_x - 22.0, T + 3.0)), "ldr")
    sh.text(L((end_x - 34.0, T + 27.0)), "offerkloss mot endeveden", "sml")
    sh.line(L((sole_l + 54.0, T + 20.0)), L((sole_l + 54.0, T + 3.0)), "ldr")
    sh.text(L((sole_l + 46.0, T + 27.0)), "virket", "sml")
    sh.text(L(_add(_add(m, _v(ax, 58.0)), _v(per, -12.0))),
            f"⌀{nb(SB['seat_d'], 0)} forstnerbor i føringshullet", "smh",
            "end")
    sh.text(L(_add(_add(m, _v((-ca, sa), run * 0.55)), (0.0, 9.0))),
            "skruens vei", "smh", "end")
    sh.text(L(_add(_v(e, cut * 0.62), (5.0, 0.0))), "vinkelklossen", "smh")
    sh.text(L(_add(_v(e, CLAMP_UP[0]), (-46.0, -16.0))), "to tvinger", "smh",
            "end")
    sh.line(L(_add(_v(e, CLAMP_UP[0]), (-44.0, -18.0))),
            L(_add(_v(e, CLAMP_UP[0]), (-24.0, -8.0))), "ldr")

    rows = [
        "Klem klossen mot flaten med TO tvinger, hullet rett over merket. "
        "Sålen henger utfor endeveden, så sett en offerkloss inntil — den "
        "bærer sålen og hindrer utrivning.",
        "Forstnerboret går NED I føringshullet før det tar treet, så det ikke "
        "kan vandre. Bor til det øverste merket på skaftet. Bytt så til "
        "forboret, i samme hull.",
    ]
    out = []
    for row in rows:
        out += wrap(row, SHEET_W - MARG - COL_4)
    ty = oy + T + 52.0
    sh.lines((COL_4, ty), out, "sml")
    return ty + len(out) * SZ["sml"] * 1.35


def build(G):
    global DEFS
    DEFS = _defs()
    sh = Sheet(SHEET_W, SHEET_H)
    SB, SS = seat(G, "J8-B"), seat(G, "J10")
    sh.text((MARG, 24.0), "SKRÅSKRUESETET OG VINKELKLOSSEN", "ttl")
    sh.text((MARG, 36.0),
            "Lommen skråskruen ligger i, munningen slik den ser ut på treet, "
            "borjiggen som gir vinkelen, og jiggen i bruk · alle mål i mm",
            "sub")
    bottom = max(field1(sh, SB, SS), field2(sh, SB, SS),
                 field3(sh, G, SB, SS), field4(sh, G, SB))
    legend(sh, bottom + 14.0)
    return sh


def legend(sh, y):
    """The key, and the one line that says where every number came from."""
    h = 30.0
    assert y + h <= SHEET_H - MARG + 1e-6, (
        f"tegneforklaringen havner på {y + h:.1f} mm og arket er "
        f"{SHEET_H:g} mm høyt - feltene over har vokst, sett opp SHEET_H "
        f"eller kort ned notatene")
    sh.rect(MARG, y, SHEET_W - 2 * MARG, h, "fld")
    sh.text((MARG + 5.0, y + 8.0), "TEGNFORKLARING", "leg")
    x = MARG + 5.0
    items = [
        ("wood", "Gjennomskåret tre"),
        ("mate", "Delen skruen går inn i"),
        ("brd", "Tre sett rett på"),
    ]
    for cls, txt in items:
        sh.rect(x, y + 13.0, 11.0, 6.0, cls)
        sh.text((x + 14.0, y + 18.0), txt, "sml")
        x += 20.0 + len(txt) * SZ["sml"] * 0.52
    sh.line((x, y + 16.0), (x + 12.0, y + 16.0), "gho")
    sh.text((x + 15.0, y + 18.0), "Skjult kant — lommebunn, hull, "
            "materiale som skal kappes bort", "sml")
    x += 15.0 + 63 * SZ["sml"] * 0.52 + 8.0
    sh.line((x, y + 16.0), (x + 12.0, y + 16.0), "dot")
    sh.text((x + 15.0, y + 18.0), "Festemiddelets vei (aldri en pil)", "sml")
    sh.text((MARG + 5.0, y + 26.5),
            "Alle mål i mm. Vinkler, setedybder, ⌀18, munningsellipsene, "
            "hodediametrene og de to dekningstallene er lest ut av "
            "generate_loftbed.py — ingen av dem er skrevet inn her. "
            "Generert av tools/render_setedetalj.py; rediger ikke for hånd.",
            "tiny")


def main(argv):
    out = OUT
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    import generate_loftbed as G
    sh = build(G)
    sh.write(out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
