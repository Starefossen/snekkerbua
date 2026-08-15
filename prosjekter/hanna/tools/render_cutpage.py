"""The cutting page - steg 0 of the HANNA manual, drawn rather than tabulated.

Every other page in tools/render_lineart.py is a projection of the bed. This
one is not: nothing is standing yet. Steg 0 is the morning on the trestles -
kapping, forboring og forsenking - and what the builder needs in front of him
there is not a view of the finished bed but a KAPPEPLAN: which boards to open,
in which order to cut them, and what is left over when he is done.

WHERE THE NUMBERS COME FROM
---------------------------
All of them from tools/gen_doc_tables.py's buy_table(), which is the same
first-fit packing that docs/generated/innkjopsliste.md prints - which in turn
is packed out of the model's own CUT_LIST. Not one millimetre on this page is
typed by hand: the sale lengths, the piece lengths, the saw kerf between two
cuts and the leftover at the end of every board are all read off that table,
and the plywood line takes its size from G.PANEL_W / G.PANEL_LEN / G.PANEL_T.
Change the model and this page changes with it.

THE SHEET IS LANDSCAPE
----------------------
Steg 0 is the one page of the manual that is turned on its side. A kappeplan
is fourteen long thin things stacked up, and on a portrait sheet the bars can
only be as wide as a portrait sheet is - which left the type at about six
point. So the page shapes itself to a LANDSCAPE A4 content area instead:
the vertical metrics below are fixed, the content height falls out of them,
and the page WIDTH is then set to height x ASPECT (267 / 180 mm usable). The
drawing is therefore always exactly as wide as the paper allows, and every
type size on it is a fixed fraction of that width - roughly 9-10 pt on the
printed page. Widening the sheet does not shrink the type, it widens the bars.

THE PAGE
--------
One horizontal BAR per board bought, and every bar on ONE shared scale: a
4,8 m board is drawn exactly twice the length of a 2,4 m one, so the pile in
the drawing is the pile in the shop. The bars run the full usable width. To
the left of each bar is its sale length, and against the first bar of each
profile stands the profile itself with how many boards of it to carry home
and what fraction of them is thrown away - no separate heading band, because
a heading band per profile is six lines of page height this sheet does not
have.

Inside a bar the pieces stand in the order the packer put them - longest
first, the order you would actually cut them in - separated by CUT MARKS that
run past the bar top and bottom. EVERY PIECE CARRIES ITS OWN LENGTH: five
800 mm slats off one board are five segments each reading "800", not one
segment reading "5 x 800", because the number the builder sets the saw stop
to is the one he wants under his eye. The part NAME is written once per run,
in the band above the bar; where a name will not fit over its own run it steps
below the bar and points back at it with a leader.

THE ZOOM BAND
-------------
One board defeats the per-piece rule outright: the 36x48 carries 2 x 1700 and
then sixteen small pieces - 8 x 73 and 8 x 48 - in its last metre. Printed,
those are 3,4 and 2,3 mm wide and read as a row of screw holes. So a board
with pieces too narrow to write on gets a MAGNIFIED SUB-STRIP: the dense
region of the parent bar is tinted, and directly beneath it the same region is
redrawn across the full bar width - 4,7 times life size here - with every cut
mark, every length and every name separately legible. A pale trapezoid joins
the two, so it is obvious that the sub-strip is not another board but the same
one, opened out, and the magnification is printed beside it. A run only ever
falls back to a grouped "n x len" label where even the zoom strip cannot give
its pieces three digits' worth of width - or where the small pieces are spread
so far along the board that there is nothing left to magnify into.

The tail of every board is the REST - what the packer could not place. It is
hatched and greyed so it can never be mistaken for a piece to cut, and it
carries its length, because that is the offcut that goes on the rack.

Two pictograms sit above the bars, in the same flat 24-grid line style as
docs/img/ikon: the saw (drawn here - there is no saw glyph in the icon set)
and docs/img/ikon/forbor.svg for the pre-drilling. They are the two things
this step is: cut everything, then drill everything, before anything is
raised. A third card is the key to the hatching.

The page is written twice, SVG and PNG, exactly as the step pages are.

Entry point:
    render(G, out_dir, width, glyph_dir) -> path of the PNG
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ICON_DIR = os.path.join(ROOT, "docs", "img", "ikon")

# ---------------------------------------------------------------------------
# THE SHEET
# ---------------------------------------------------------------------------
# Everything below is in the page's own unit, and the page's own unit is what
# fixes the printed type size: the height is the sum of the vertical metrics,
# and the width is that height times ASPECT, so one unit is always
# 180 mm / height. A size of 27 units on a 1440-unit page prints at 3,4 mm.
ASPECT = 267.0 / 180.0   # the usable area of a landscape A4, w : h

MARGIN = 24.0
BUY_COL = 280.0          # profile + sale length, to the left of every bar

TOP_H = 104.0            # the pictogram strip
GROUP_GAP = 16.0         # air (and a rule) above a new profile
NAME_H = 22.0            # the band over a bar that carries the part names
BAR_H = 42.0             # the board itself
BAR_GAP = 6.0            # air under a bar
LBL_H = 30.0             # a band of leader callouts, when a name will not fit
ZOOM_LEAD = 30.0         # the trapezoid tying a zoom strip to its bar
ZOOM_H = 42.0            # the magnified sub-strip
ZOOM_NAME = 30.0         # the names under it, clear of its ticks
SHEET_H = 48.0           # the plywood line
FOOT_H = 48.0

S_SECTION = 28.0         # "36x98"
S_SUB = 19.0             # "7 bord . 6 % svinn"
S_BUY = 25.0             # the sale length beside the bar
S_NAME = 22.0            # a part name over a run
S_LEN = 27.0             # the length inside a piece - the page's main number
S_LEN_SM = 21.0          # ...where the piece is too tight for the main size
S_REST = 21.0            # the leftover length
S_CAP = 22.0             # a pictogram caption
S_FOOT = 24.0

ICON = 78.0              # the pictogram box, 24-grid
TICK = 9.0               # how far a cut mark runs past the bar
HATCH_STEP = 18.0        # the rest hatching
PAD = 12.0               # white the knockout keeps around a label

TINT = "#ececec"         # the region of a bar a zoom strip expands


# ---------------------------------------------------------------------------
# TYPE METRICS
# ---------------------------------------------------------------------------
# Nothing here can ask the renderer how wide a string came out, so widths are
# estimated - deliberately a little generously, because the failure that shows
# is text running out of its segment, and the failure that does not is a name
# that could have fitted moving outside the bar.
_NARROW = set(" .,:;!|'ijltf()[]-")
_WIDE = set("mwMW")


def _tw(s, size, weight="normal"):
    """Roughly how wide `s` renders at `size`, in the page's own units."""
    u = 0.0
    for ch in s:
        if ch in _NARROW:
            u += 0.30
        elif ch in _WIDE:
            u += 0.86
        elif ch == "—":
            u += 0.92
        elif ch == "×":
            u += 0.62
        elif ch.isdigit() or ch.isupper():
            u += 0.62
        else:
            u += 0.53
    return u * size * (1.07 if weight == "bold" else 1.0)


def _mm(v):
    """A length the way a tape measure reads it."""
    return f"{int(round(v))}"


def _label(page, p, s, size, anchor="middle", weight="normal", colour=None,
           knockout=True):
    """Text with the drawing wiped out behind it.

    A run of eight identical blocks puts a cut mark every few units, and the
    label that names the run sits right across them. The marks matter more
    than tidiness, so they are drawn in full and the type is knocked out of
    them rather than dodging them.
    """
    import render_lineart as RL
    w = _tw(s, size, weight)
    x = p[0] - w / 2 if anchor == "middle" else (p[0] - w if anchor == "end"
                                                 else p[0])
    if knockout:
        page.rect(x - PAD / 2, p[1] - size * 0.24, w + PAD, size * 1.04,
                  fill="#ffffff", stroke="none", width=0)
    page.text(p, s, size, anchor=anchor, weight=weight,
              colour=RL.INK if colour is None else colour)


def _metres(v):
    return f"{v / 1000:.1f}".replace(".", ",") + " m"


# ---------------------------------------------------------------------------
# THE CUT DATA, SHAPED FOR A DRAWING
# ---------------------------------------------------------------------------
def _runs(pieces):
    """[(name, length, count)] - a board's pieces, identical neighbours joined.

    The packer hands out pieces longest first, so equal pieces are already
    adjacent; joining them is what lets one name stand over "8 x 73" while
    every one of the eight lengths is still written on its own piece.
    """
    out = []
    for name, length in pieces:
        if out and out[-1][0] == name and out[-1][1] == length:
            out[-1][2] += 1
        else:
            out.append([name, length, 1])
    return [tuple(r) for r in out]


def _name_forms(name):
    """A name, shortened step by step, longest first.

    The cut list is written for a table, where "Bearing block, bench rail
    (J9-B)" has all the room it wants; a 48 mm segment has none. Rather than a
    hand-kept abbreviation table - which would be one more place to forget the
    model changed - the forms are derived: drop the parenthetical, keep the
    clause before the comma, and put the parenthetical back on if that is the
    only thing telling two pieces apart.
    """
    tag = re.search(r"\(([^)]*)\)", name)
    bare = re.sub(r"\s*\([^)]*\)", "", name).strip().rstrip(",")
    head = bare.split(",")[0].strip()
    forms = [name, bare]
    if tag:
        forms.append(f"{head} ({tag.group(1)})")
    forms.append(head)
    seen, out = set(), []
    for f in forms:
        if f and f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _qty_text(count, length):
    return f"{count} × {_mm(length)}" if count > 1 else _mm(length)


def _fit_size(text, room, weight="bold"):
    """The largest of the two label sizes `text` fits in `room`, or None."""
    for size in (S_LEN, S_LEN_SM):
        if _tw(text, size, weight) + PAD <= room:
            return size
    return None


def _label_run(s, sc):
    """Decide how one run states its lengths on a strip drawn at scale `sc`.

    A length on every piece if the piece is wide enough; otherwise one grouped
    "n x len" over the run; and if even that will not go, the grouped label at
    the small size anyway - by then the run is inside a zoom strip and there is
    nothing further to fall back on.
    """
    size = _fit_size(s["txt"], s["length"] * sc)
    if size:
        s["mode"], s["size"] = "each", size
        return
    s["mode"] = "group"
    s["size"] = _fit_size(s["qty"], (s["mm1"] - s["mm0"]) * sc) or S_LEN_SM


def _plan_board(board, scale, kerf):
    """Where every piece, cut mark and label of ONE board lands.

    Returns a dict: the segments (one per RUN of identical pieces, but each
    knowing whether its pieces carry their lengths one by one), the cut marks,
    the rest, the region a zoom strip has to expand, and whether a band of
    outside leader callouts is needed under the bar.
    """
    runs = _runs(board["pieces"])
    segs, marks = [], []
    pos = 0.0
    for i, (name, length, count) in enumerate(runs):
        start, end = pos, pos + length * count + kerf * (count - 1)
        # One mark per cut, including the ones inside a run - those are the
        # repeats, drawn a shade lighter so the eye still finds the joints
        # between one KIND of piece and the next.
        for k in range(1, count):
            marks.append((start + (length + kerf) * k - kerf / 2, False))
        pos = end + kerf
        if i < len(runs) - 1:
            marks.append((end + kerf / 2, True))
        segs.append(dict(mm0=start, mm1=end, name=name, count=count,
                         length=length, x0=start * scale, x1=end * scale,
                         qty=_qty_text(count, length), txt=_mm(length)))
    rest_at = pos - kerf if runs else 0.0
    rest = board["buy"] - rest_at
    if rest > 0.5 and runs:
        marks.append((rest_at, True))

    # Every piece carries its OWN length wherever the piece is wide enough to
    # hold three digits - that is the number the builder sets the saw stop to.
    # A run whose pieces are not that wide is not labelled up here at all: it
    # goes to the zoom strip below, where it will be.
    for s in segs:
        s["size"] = _fit_size(s["txt"], s["length"] * scale)
        s["mode"] = "each" if s["size"] else "zoom"

    zoom = None
    tiny = [s for s in segs if s["mode"] == "zoom"]
    if tiny:
        lo = min(s["mm0"] for s in tiny)
        hi = max(s["mm1"] for s in tiny)
        # A zoom strip is only worth its page height if it actually magnifies.
        # Small pieces spread over most of a board leave nothing to magnify
        # into, so those runs fall back to one grouped label each instead.
        if hi - lo <= 0.6 * board["buy"]:
            inside = [s for s in segs
                      if lo - 0.5 <= s["mm0"] and s["mm1"] <= hi + 0.5]
            for s in inside:
                s["inzoom"] = True
            zoom = dict(mm0=lo, mm1=hi, segs=inside)
        else:
            for s in tiny:
                _label_run(s, scale)

    # The name goes over the run, once, in the band above the bar. Runs that
    # live in the zoom strip are named down there instead.
    for s in segs:
        s["nm"] = None
        if s.get("inzoom"):
            continue
        room = (s["x1"] - s["x0"]) - PAD
        for form in _name_forms(s["name"]):
            if _tw(form, S_NAME) <= room:
                s["nm"] = form
                break
        if s["nm"] is None:
            s["outside"] = _name_forms(s["name"])[-1]

    return dict(segs=segs, marks=sorted(marks),
                rest=dict(at=rest_at * scale, mm=rest), zoom=zoom,
                outside=any(s.get("outside") for s in segs))


def _spread(items, lo, hi, gap=16.0):
    """Nudge label centres apart along one line, then back inside [lo, hi]."""
    items.sort(key=lambda it: it["x"])
    cur = lo
    for it in items:
        it["x"] = max(it["x"], cur + it["w"] / 2)
        cur = it["x"] + it["w"] / 2 + gap
    cur = hi
    for it in reversed(items):
        it["x"] = min(it["x"], cur - it["w"] / 2)
        cur = it["x"] - it["w"] / 2 - gap
    return items


# ---------------------------------------------------------------------------
# THE SAW
# ---------------------------------------------------------------------------
# docs/img/ikon has no saw, so here is one, drawn on the same 24 x 24 grid at
# the same single stroke weight as the icons that are on disk - handle, blade
# and a tooth line, nothing else.
def _saw_icon(page, RL, x, y, size):
    """A flat-line handsaw in a `size` box with its corner at (x, y)."""
    k = size / 24.0
    width = 1.25 * k                       # the icon set's own stroke

    def P(u, v):                           # 24-grid, v measured DOWNWARDS
        return (x + u * k, y + (24.0 - v) * k)

    # A D-grip at the left, a deep blade running right, teeth on its underside
    # - the three things that make a saw a saw and not a screw.
    handle = [P(7.4, 4.0), P(2.9, 4.0), P(0.9, 7.0), P(0.9, 15.2),
              P(2.9, 17.8), P(7.4, 17.8), P(7.4, 4.0)]
    grip = [P(6.6, 7.0), P(4.1, 8.0), P(2.8, 10.4), P(2.8, 12.2),
            P(4.1, 14.6), P(6.6, 15.6), P(6.6, 7.0)]
    blade = [P(7.4, 15.2), P(7.4, 5.8), P(22.4, 8.4), P(22.4, 12.4)]

    # Six big teeth read as a saw; twenty small ones read as a smudge.
    teeth = [P(22.4, 12.4)]
    n = 6
    step = (22.4 - 7.4) / n
    for i in range(n):
        u0, u1 = 22.4 - (i + 0.5) * step, 22.4 - (i + 1) * step
        teeth.append(P(u0, 12.4 + 2.8 * (i + 0.5) / n + 2.5))
        teeth.append(P(u1, 12.4 + 2.8 * (i + 1) / n))
    page.polylines([handle, grip, blade, teeth], RL.INK, width)


def _pictogram(page, x, y, h, draw, lines):
    """One icon with its short Norwegian caption beside it."""
    top = y + h
    draw(x, top - ICON)
    tx = x + ICON + 22.0
    ty = top - ICON / 2 + (len(lines) - 1) * S_CAP * 0.66 - S_CAP * 0.34
    for line in lines:
        page.text((tx, ty), line, S_CAP)
        ty -= S_CAP * 1.32


def _hatch_swatch(page, RL, x, y, w, h):
    page.rect(x, y, w, h, fill="#ffffff", stroke=RL.GREY, width=RL.T.W_RULE)
    page.hatch(x, y, w, h, HATCH_STEP, RL.GREY, RL.T.W_RULE * 0.65)


# ---------------------------------------------------------------------------
# THE SHAPE OF THE SHEET
# ---------------------------------------------------------------------------
def _layout(timber, sheets, kerf, page_w):
    """Plan every board at a trial width; say how tall the page came out."""
    bar_x = MARGIN + BUY_COL
    bar_w = page_w - MARGIN - bar_x
    longest = max(b["buy"] for e in timber for b in e["boards"])
    scale = bar_w / longest
    plans = [(e, [_plan_board(b, scale, kerf) for b in e["boards"]])
             for e in timber]

    h = 2 * MARGIN + TOP_H + FOOT_H
    for _e, rows in plans:
        h += GROUP_GAP
        for pl in rows:
            h += NAME_H + BAR_H + BAR_GAP
            if pl["zoom"]:
                h += ZOOM_LEAD + ZOOM_H + ZOOM_NAME
            if pl["outside"]:
                h += LBL_H
    h += len(sheets) * (GROUP_GAP + SHEET_H)
    return dict(plans=plans, bar_x=bar_x, bar_w=bar_w, scale=scale, h=h,
                page_w=page_w)


def _shape(timber, sheets, kerf):
    """Settle the landscape sheet: height from the metrics, width from ASPECT.

    The vertical metrics are fixed, so the content height is very nearly
    fixed too - it moves only if a wider sheet lets one more label inside its
    piece and saves a callout band. Three passes is far more than that ever
    needs.
    """
    lay = _layout(timber, sheets, kerf, 2100.0)
    for _ in range(3):
        lay = _layout(timber, sheets, kerf, lay["h"] * ASPECT)
    return lay


# ---------------------------------------------------------------------------
# THE PAGE
# ---------------------------------------------------------------------------
def render(G, out_dir, width, glyph_dir):
    """Write <out_dir>/steg-00.svg and .png. Returns the PNG path.

    `glyph_dir` is the fastener-glyph folder every other page renderer is
    handed; it is part of the shared signature render_lineart.render_all
    calls with. Nothing is fastened on this page - it is all saw and drill -
    so nothing is taken out of it, and the two pictograms come from
    docs/img/ikon instead.
    """
    import render_lineart as RL
    import gen_doc_tables as T

    kerf = T.KERF
    table = T.buy_table(G)
    timber = [e for e in table if not e["sheet"]]
    sheets = [e for e in table if e["sheet"]]

    lay = _shape(timber, sheets, kerf)
    PAGE_W, height = lay["page_w"], lay["h"]
    bar_x, bar_w, scale = lay["bar_x"], lay["bar_w"], lay["scale"]
    plans = lay["plans"]

    page = RL.Page(0.0, 0.0, PAGE_W, height)
    top = height - MARGIN

    # --- the two things this step IS, plus the key to the hatching ---------
    card_w = (PAGE_W - 2 * MARGIN) / 3
    strip_y, strip_h = top - TOP_H + 34.0, TOP_H - 48.0
    forbor = os.path.join(ICON_DIR, "forbor.svg")

    def _drill(x, y, path=forbor):
        gw, gh = RL.glyph_dims(path)
        page.embed_svg(path, x, y, ICON * gw / gh, ICON)

    _pictogram(page, MARGIN, strip_y, strip_h,
               lambda x, y: _saw_icon(page, RL, x, y, ICON),
               # «Kapp alt først» stod her til kapplista ble delt i to.
               # Romdelene kappes med overmål og finkappes i rommet, så
               # siden lover ikke lenger ferdige lengder på alle bar.
               ["Kapp på bukken først —",
                f"alle kutt 90°, {kerf} mm sagsnitt"])
    _pictogram(page, MARGIN + card_w, strip_y, strip_h, _drill,
               ["Forbor og forsenk alt",
                "før noe reises"])
    _pictogram(page, MARGIN + 2 * card_w, strip_y, strip_h,
               lambda x, y: _hatch_swatch(page, RL, x, y + (ICON - 46.0) / 2,
                                          ICON, 46.0),
               ["Skravert = rest,",
                "det du ikke skal kappe"])
    top -= TOP_H

    # --- the boards -------------------------------------------------------
    sale_x = MARGIN + BUY_COL - 20.0

    def _strip(x, y, h, w, segs, mm0, sc, marks, label_size=None):
        """One run of bar: outline, cut marks, and a length on every piece."""
        page.rect(x, y, w, h, fill="none", stroke=RL.INK,
                  width=RL.T.W_NEW * 0.42)
        for m, boundary in marks:
            mx = x + (m - mm0) * sc
            page.line((mx, y - TICK), (mx, y + h + TICK), RL.INK,
                      RL.T.W_MARK * (0.34 if boundary else 0.24))
        for s in segs:
            # A run that is going to be spelled out in a zoom strip below is
            # left blank up here - there is no room for a number on it.
            if s["mode"] == "zoom":
                continue
            size = label_size or s["size"]
            base = y + h / 2 - size * 0.36
            if s["mode"] == "group":
                cx = x + ((s["mm0"] + s["mm1"]) / 2 - mm0) * sc
                _label(page, (cx, base), s["qty"], size, weight="bold")
            else:
                for k in range(s["count"]):
                    c = s["mm0"] + (s["length"] + kerf) * k + s["length"] / 2
                    _label(page, (x + (c - mm0) * sc, base), s["txt"], size,
                           weight="bold")
        # The knockout under each label punched a hole in the cut marks, so
        # the parts of them that live outside the bar go back on top: the comb
        # over a run of eight blocks is never lost to a caption spanning it.
        for m, boundary in marks:
            mx = x + (m - mm0) * sc
            wgt = RL.T.W_MARK * (0.34 if boundary else 0.24)
            page.line((mx, y - TICK), (mx, y), RL.INK, wgt)
            page.line((mx, y + h), (mx, y + h + TICK), RL.INK, wgt)

    for e, rows in plans:
        top -= GROUP_GAP
        page.line((MARGIN, top + GROUP_GAP * 0.45),
                  (PAGE_W - MARGIN, top + GROUP_GAP * 0.45), RL.GREY,
                  RL.T.W_LEAD * 0.5)
        first = True

        for board, pl in zip(e["boards"], rows):
            segs, marks, rest, zoom = (pl["segs"], pl["marks"], pl["rest"],
                                       pl["zoom"])
            y = top - NAME_H - BAR_H
            w = board["buy"] * scale

            page.text((sale_x, y + BAR_H / 2 - S_BUY * 0.36),
                      _metres(board["buy"]), S_BUY, anchor="end",
                      weight="bold")
            if first:
                # The profile heading sits in the name band of its first bar
                # and its shopping line inside that bar's row, so a profile
                # costs this sheet no page height of its own at all.
                page.text((MARGIN, y + BAR_H + NAME_H * 0.20), e["section"],
                          S_SECTION, weight="bold")
                page.text((MARGIN, y + BAR_H / 2 - S_SUB * 0.36),
                          f"{len(e['boards'])} bord · "
                          f"{e['waste']:.0f} % svinn", S_SUB, colour=RL.GREY)
                first = False

            # The rest first, so the bar outline draws over its hatching.
            if rest["mm"] > 0.5:
                rw = w - rest["at"]
                page.hatch(bar_x + rest["at"], y, rw, BAR_H, HATCH_STEP,
                           RL.GREY, RL.T.W_RULE * 0.5)
                if _tw(_mm(rest["mm"]), S_REST, "bold") + PAD <= rw:
                    _label(page, (bar_x + rest["at"] + rw / 2,
                                  y + BAR_H / 2 - S_REST * 0.36),
                           _mm(rest["mm"]), S_REST, weight="bold",
                           colour=RL.GREY)
                page.rect(bar_x + rest["at"], y, rw, BAR_H, fill="none",
                          stroke=RL.GREY, width=RL.T.W_RULE * 0.7)

            # The region a zoom strip expands, tinted under the bar.
            if zoom:
                page.rect(bar_x + zoom["mm0"] * scale, y,
                          (zoom["mm1"] - zoom["mm0"]) * scale, BAR_H,
                          fill=TINT, stroke="none", width=0)

            _strip(bar_x, y, BAR_H, w, segs, 0.0, scale, marks)

            # Part names, once per run, in the band over the bar.
            for s in segs:
                if s["nm"] is not None:
                    page.text(((bar_x + (s["x0"] + s["x1"]) / 2),
                               y + BAR_H + NAME_H * 0.20), s["nm"], S_NAME,
                              anchor="middle")
            top -= NAME_H + BAR_H + BAR_GAP

            # A name that will not go over its own run steps below the bar.
            if pl["outside"]:
                out = [dict(x=bar_x + (s["x0"] + s["x1"]) / 2,
                            at=bar_x + (s["x0"] + s["x1"]) / 2,
                            s=s["outside"], w=_tw(s["outside"], S_NAME))
                       for s in segs if s.get("outside")]
                _spread(out, MARGIN, PAGE_W - MARGIN)
                base = top - LBL_H + S_NAME * 0.6
                for it in out:
                    page.line((it["at"], y - TICK - 2.0),
                              (it["x"], base + S_NAME * 1.1), RL.GREY,
                              RL.T.W_LEAD * 0.5)
                    _label(page, (it["x"], base), it["s"], S_NAME)
                top -= LBL_H

            # --- the magnified sub-strip ---------------------------------
            if zoom:
                zy = top - ZOOM_LEAD - ZOOM_H
                zs = bar_w / (zoom["mm1"] - zoom["mm0"])
                a0 = bar_x + zoom["mm0"] * scale
                a1 = bar_x + zoom["mm1"] * scale
                page.poly([(a0, y), (a1, y), (bar_x + bar_w, zy + ZOOM_H),
                           (bar_x, zy + ZOOM_H)], fill=TINT, stroke="none",
                          width=0)
                page.line((a0, y), (bar_x, zy + ZOOM_H), RL.GREY,
                          RL.T.W_LEAD * 0.6)
                page.line((a1, y), (bar_x + bar_w, zy + ZOOM_H), RL.GREY,
                          RL.T.W_LEAD * 0.6)
                zsegs = zoom["segs"]
                zmarks = [(m, b) for m, b in marks
                          if zoom["mm0"] - 0.5 <= m <= zoom["mm1"] + 0.5]
                for s in zsegs:
                    _label_run(s, zs)
                _strip(bar_x, zy, ZOOM_H, bar_w, zsegs, zoom["mm0"], zs,
                       zmarks)
                page.text((sale_x, zy + ZOOM_H / 2 - S_SUB * 0.36),
                          f"forstørret {zs / scale:.1f}×".replace(".", ","),
                          S_SUB, anchor="end", colour=RL.GREY)
                for s in zsegs:
                    cx = bar_x + ((s["mm0"] + s["mm1"]) / 2 - zoom["mm0"]) * zs
                    room = (s["mm1"] - s["mm0"]) * zs
                    form = next((f for f in _name_forms(s["name"])
                                 if _tw(f, S_NAME) <= room),
                                _name_forms(s["name"])[-1])
                    page.text((cx, zy - TICK - S_NAME * 0.74), form, S_NAME,
                              anchor="middle")
                top -= ZOOM_LEAD + ZOOM_H + ZOOM_NAME

    # --- the one thing that is not a stick --------------------------------
    for e in sheets:
        top -= GROUP_GAP
        page.line((MARGIN, top + GROUP_GAP * 0.45),
                  (PAGE_W - MARGIN, top + GROUP_GAP * 0.45), RL.GREY,
                  RL.T.W_LEAD * 0.5)
        # The one line on the page with no bar under it: the plywood heading is
        # wider than the profile column, so it simply runs on into the bar
        # column and the plate line starts after it.
        y = top - SHEET_H
        page.text((MARGIN, y + SHEET_H / 2 - S_SECTION * 0.34), e["section"],
                  S_SECTION, weight="bold")
        page.text((MARGIN + _tw(e["section"], S_SECTION, "bold") + 44.0,
                   y + SHEET_H / 2 - S_LEN * 0.36),
                  f"1 plate {G.PANEL_T} mm kryssfiner, minst "
                  f"{_mm(G.PANEL_W)} × {_mm(G.PANEL_LEN)} mm",
                  S_LEN, weight="bold")
        page.text((PAGE_W - MARGIN, y + SHEET_H / 2 - S_SUB * 0.36),
                  f"{len(e['pieces'])} del kappes av den", S_SUB,
                  anchor="end", colour=RL.GREY)
        top -= SHEET_H

    # --- what it all adds up to -------------------------------------------
    bought = sum(e["bought"] for e in timber)
    used = sum(e["used"] for e in timber)
    n_boards = sum(len(e["boards"]) for e in timber)
    n_pieces = sum(sum(len(b["pieces"]) for b in e["boards"]) for e in timber)
    n_pieces += sum(len(e["pieces"]) for e in sheets)
    page.line((MARGIN, top - 8.0), (PAGE_W - MARGIN, top - 8.0), RL.INK,
              RL.T.W_RULE * 0.7)
    page.text((MARGIN, top - 8.0 - S_FOOT * 1.10),
              f"{n_boards} bord + {len(sheets)} plate — "
              f"{n_pieces} deler å kappe", S_FOOT, weight="bold")
    page.text((PAGE_W - MARGIN, top - 8.0 - S_FOOT * 1.10),
              f"{_metres(bought)} kjøpt, {_metres(used)} brukt, "
              f"{100.0 * (bought - used) / bought:.0f} % svinn",
              S_FOOT, anchor="end", colour=RL.GREY)

    svg = os.path.join(out_dir, "steg-00.svg")
    png = os.path.join(out_dir, "steg-00.png")
    page.write(svg, width)
    RL.to_png(svg, png, width)
    print(f"  steg  0  {n_boards} bord / {n_pieces} deler "
          f"({PAGE_W:.0f} × {height:.0f}, {PAGE_W / height:.3f}) -> {png}")
    return png


if __name__ == "__main__":
    import generate_loftbed as _G
    import render_lineart as _RL
    # The pen is the SUBJECT's, so it has to be set before anything is drawn -
    # render_lineart.render_all() does it for the whole run, and this page has
    # to do it for itself when it is asked for on its own.
    _RL.use_model(_G)
    render(_G, os.path.join(ROOT, "docs", "img"), 1600,
           os.path.join(ROOT, "docs", "img", "beslag"))
