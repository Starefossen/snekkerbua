"""The schematics family's pen, in one place.

Everything in docs/schematics/ is one family of sheets: the same type sizes,
the same stroke weights, the same arrow heads, the same hatch. The hand-drawn
sheets were drawn 3450 units wide and every size on them is a number in the
tables below; a generated sheet that wants to sit in the same folder has to be
drawn with the same pen, or it is a stranger on the shelf.

    style_k = this sheet's unit over the family's unit

so a sheet drawn 3450 units wide has style_k = 1 and gets the family's numbers
unchanged, while tools/render_setedetalj.py - which is drawn in millimetres of
PAPER, because the scales printed on it (2:1, 1:1) have to be true - passes
0.175 and gets the same look at its own size.

Nothing in here knows about beds, screws or steps. It knows about paper.

Deterministic by construction: `f()` is the only number formatter, it is
locale-free and sign-stable, and no dict is iterated into the output in an
order that is not written down here.
"""

from __future__ import annotations

import math


def f(v):
    """Fixed, locale-free, sign-stable number formatting - the whole reason
    two runs of a sheet agree byte for byte."""
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


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# THE FAMILY'S NUMBERS - type, stroke, halo
# ---------------------------------------------------------------------------
SZ_BASE = {
    "ttl": 50.0, "sub": 26.0, "pt": 31.0, "big": 27.0,
    "sml": 22.0, "dm": 23.0, "dmh": 23.0, "leg": 26.0, "jl": 27.0,
    "tiny": 19.0,
}

SW_BASE = {
    "dim": 1.4, "ext": 0.9, "ldr": 1.5, "cut": 2.6, "pst": 3.0,
    "brd": 2.6, "gho": 1.7, "scrl": 1.8, "legbox": 1.6,
    "brk": 2.0, "ctr": 1.1, "pic": 2.6, "pic2": 1.6,
}

HALO_BASE = 6.0             # the white halo under a figure on line work


def sizes(k):
    return {name: v * k for name, v in SZ_BASE.items()}


def strokes(k):
    return {name: v * k for name, v in SW_BASE.items()}


def style(k):
    s, w = sizes(k), strokes(k)
    hal = HALO_BASE * k
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
           stroke-width:{f(hal)}px; }}
    .smh {{ font-size:{f(s['sml'])}px; paint-order:stroke; stroke:#fff;
           stroke-width:{f(hal)}px; }}
    .dm  {{ font-size:{f(s['dm'])}px; }}
    .dmh {{ font-size:{f(s['dm'])}px; paint-order:stroke; stroke:#fff;
           stroke-width:{f(hal)}px; }}
    .leg {{ font-size:{f(s['leg'])}px; font-weight:bold; }}
    .jl  {{ font-size:{f(s['jl'])}px; font-weight:bold; paint-order:stroke;
           stroke:#fff; stroke-width:{f(hal)}px; }}
    .wood{{ fill:url(#hatch); stroke:#000; stroke-width:{f(w['brd'])}; }}
    .mate{{ fill:#c4c4c4; stroke:#000; stroke-width:{f(w['pst'])}; }}
    .brd {{ fill:#ececec; stroke:#000; stroke-width:{f(w['brd'])}; }}
    .plain{{ fill:#fff; stroke:#000; stroke-width:{f(w['brd'])}; }}
    .gho {{ fill:none; stroke:#000; stroke-width:{f(w['gho'])};
           stroke-dasharray:{f(10.9 * k)} {f(6.8 * k)}; }}
    .ctr {{ fill:none; stroke:#000; stroke-width:{f(w['ctr'])};
           stroke-dasharray:{f(9 * k)} {f(3 * k)}
           {f(1.5 * k)} {f(3 * k)}; }}
    .dot {{ fill:none; stroke:#000; stroke-width:{f(w['scrl'])};
           stroke-dasharray:{f(0.6 * k)} {f(4.5 * k)};
           stroke-linecap:round; }}
    .dim {{ fill:none; stroke:#000; stroke-width:{f(w['dim'])}; }}
    .ext {{ fill:none; stroke:#000; stroke-width:{f(w['ext'])}; }}
    .ldr {{ fill:none; stroke:#000; stroke-width:{f(w['ldr'])}; }}
    .brk {{ fill:none; stroke:#000; stroke-width:{f(w['brk'])}; }}
    .cut {{ fill:none; stroke:#000; stroke-width:{f(w['cut'])}; }}
    .scr {{ fill:#fff; stroke:#000; stroke-width:{f(w['scrl'])}; }}
    .scrd{{ fill:none; stroke:#000; stroke-width:{f(w['scrl'])};
           stroke-dasharray:{f(8.8 * k)} {f(5.7 * k)}; }}
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


def defs(k):
    return f"""  <defs>
    <marker id="aE" markerWidth="13" markerHeight="10" refX="12" refY="4.5"
      orient="auto"><path d="M0,0 L12,4.5 L0,9 z" fill="#000"/></marker>
    <marker id="aS" markerWidth="13" markerHeight="10" refX="1" refY="4.5"
      orient="auto"><path d="M12,0 L0,4.5 L12,9 z" fill="#000"/></marker>
    <pattern id="hatch" width="{f(14 * k)}" height="{f(14 * k)}"
      patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="{f(14 * k)}" height="{f(14 * k)}"
        fill="#dcdcdc"/>
      <line x1="0" y1="0" x2="0" y2="{f(14 * k)}" stroke="#000"
        stroke-width="{f(1.7 * k)}"/></pattern>
  </defs>
""" + style(k)


class Frame:
    """Model millimetres to sheet units for one view."""

    def __init__(self, ox, oy, k, sx=1.0, sy=1.0):
        self.ox, self.oy, self.k, self.sx, self.sy = ox, oy, k, sx, sy

    def p(self, x, y):
        return (self.ox + self.k * self.sx * x, self.oy + self.k * self.sy * y)

    def d(self, x, y):
        return (self.k * self.sx * x, self.k * self.sy * y)

    def s(self, v):
        return self.k * v


class Sheet:
    """A y-down SVG in the schematics family's idiom.

    `style_k` is this sheet's unit over the family's - see the module doc.
    """

    def __init__(self, w, h, style_k, title, width=2400, origin=(0.0, 0.0),
                 extra_css=""):
        self.w, self.h = w, h
        self.k = style_k
        self.title = title
        self.width = width
        self.origin = origin
        # A sheet may need a class the family does not have - a wall, a member
        # behind the cut plane. It gets it HERE, after the family's own block,
        # so the shared names keep their shared meaning.
        self.extra_css = extra_css
        self.sz = sizes(style_k)
        self.sw = strokes(style_k)
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
        lead = lead or self.sz[cls] * 1.35
        for i, row in enumerate(rows):
            self.text((p[0], p[1] + i * lead), row, cls, anchor)
        return p[1] + (len(rows) - 1) * lead

    def wrap(self, text, width, cls="sml"):
        """Greedy wrap to a column measured in SHEET UNITS, not in characters:
        a note that runs off the sheet is the one drawing fault a proof render
        always shows and a code review never does."""
        cw = self.sz[cls] * 0.52
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
        SZ = self.sz
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
                           txt_p[1] - self.sz[cls] * 0.25), rows, cls,
                          anchor=anchor)

    # -- output -------------------------------------------------------------
    def write(self, path):
        ox, oy = self.origin
        head = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="{f(ox)} {f(oy)} {f(self.w)} {f(self.h)}" '
                f'width="{self.width}">\n'
                f'  <title>{esc(self.title)}</title>\n')
        # An explicit ground, not a CSS `background`: rsvg-convert renders
        # the CSS one to transparency, and a transparent sheet is a black
        # sheet the moment anything composites it.
        bg = (f'  <rect x="{f(ox)}" y="{f(oy)}" width="{f(self.w)}" '
              f'height="{f(self.h)}" fill="#ffffff"/>\n')
        css = defs(self.k)
        if self.extra_css:
            css += f"  <style>\n{self.extra_css}  </style>\n"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head + css + bg + "\n".join(self.body) + "\n</svg>\n")
