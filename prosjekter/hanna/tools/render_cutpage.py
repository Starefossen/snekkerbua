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
is packed out of the model's own CUT_LIST, at SAWN lengths (see the
overlength section below). Not one millimetre on this page is typed by hand:
the sale lengths, the piece lengths, the room's allowances, the saw kerf
between two cuts and the leftover at the end of every board are read off that
table,
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
One board defeats the per-piece rule outright: the 36x48 carries 2 x 2037 and
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

THE OVERLENGTH ON A ROOM PART
-----------------------------
Half the cut list is not finished on the trestles. A part that stands on the
floor is cut LONG and trimmed at the foot until the frame is level; a part that
runs into an end wall is cut LONG at that end and fine-cut once the niche has
been measured. The bars used to show those pieces at their nominal length like
everything else, which is the one thing on this page a reader could act on and
be wrong.

So a room part carries its allowance in the drawing: a DASHED CAP off the end
of the piece, the width of the allowance at the page's own scale, in the same
weight as the bar it grows out of. One cap per end the room finishes - one on
a piece that stands on the floor, one or two on a piece that runs into a wall,
none at all on a piece that is only scribed across its width. A piece long at
BOTH ends has its finished length in the middle of what is sawn, which is why
a segment knows its `lead` as well as its `over`.

AND THE CAP EATS BOARD. The packer packs `fin + over`, so the bar behind a cap
is really that much longer, everything after it is pushed along and the rest
at the tail is that much shorter. A cutting plan that drew the caps for free
would be promising board the saw has already taken - the sheet cannot say one
thing and the trestles do another. "Brukt" in the footer counts the allowance
too: it is wood, it becomes floor sweepings, and it does not come back.

How much each cap is worth is not written on it: at this scale fifteen
millimetres is five units of page and a "+15" beside it would be four times
the width of the thing it labels. The rule stands in the legend instead, in
the model's own numbers, and the millimetre per line is in the cut list.

Which pieces those are, and how much they get, is the model's ROOM_LINES
verdict - nothing here decides it, and the assert at the end of render() counts
the dashed caps in the finished SVG back against it.

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

# The dashed cap on a room part's end. It is the only dash on this sheet, and
# that is what lets the assert count the caps by reading the file back.
OVER_DASH = "7 5"
# ...and the same dash under another name for the LEGEND swatch, which is a
# picture OF a cap and not a cap. It must not answer the assert's question -
# it would answer it wrong. Same numbers, so it looks identical on paper.
OVER_DASH_KEY = "7 5.0"


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
    for name, length, over in pieces:
        if (out and out[-1][0] == name and out[-1][1] == length
                and out[-1][2] == over):
            out[-1][3] += 1
        else:
            out.append([name, length, over, 1])
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


def _room_over(fit):
    """(millimetres per end, how many ends) - what the ROOM adds to a line.

    `fit` is the model's own verdict, ("gulv"|"gulv+side"|"vegg"|"meddrag",
    total allowance, ends touched). The total is what the model worked out;
    the only thing decided here is how it is SPREAD, and that follows the
    kind: a piece standing on the floor is trimmed at its one foot, a piece
    running into walls is fine-cut at each of them, and a piece that is only
    scribed across its width gets no length at all. No millimetre is typed.
    """
    if not fit:
        return (0.0, 0)
    kind, over, ends = fit
    if not over:
        return (0.0, 0)
    n = 1 if kind.startswith("gulv") else ends
    return (over / n, n)


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


def _plan_board(board, scale, kerf, sec, fits):
    """Where every piece, cut mark and label of ONE board lands.

    Returns a dict: the segments (one per RUN of identical pieces, but each
    knowing whether its pieces carry their lengths one by one, and how much
    overlength the room adds to how many of its ends), the cut marks, the
    rest, the region a zoom strip has to expand, and whether a band of outside
    leader callouts is needed under the bar.
    """
    runs = _runs(board["pieces"])
    segs, marks = [], []
    pos = 0.0
    for i, (name, length, over_total, count) in enumerate(runs):
        # What one piece TAKES OUT of the board is the finished length plus
        # the room's allowance - that is where the saw goes. `lead` is the
        # part of the allowance that sits in front of the finished length: a
        # piece fine-cut at both wall ends is long at both ends, so the
        # finished length stands in the middle of what is sawn.
        per_end, nend = _room_over(fits.get((sec, name, length)))
        sawn = length + over_total
        lead = per_end if nend == 2 else 0.0
        start, end = pos, pos + sawn * count + kerf * (count - 1)
        # One mark per cut, including the ones inside a run - those are the
        # repeats, drawn a shade lighter so the eye still finds the joints
        # between one KIND of piece and the next.
        for k in range(1, count):
            marks.append((start + (sawn + kerf) * k - kerf / 2, False))
        pos = end + kerf
        if i < len(runs) - 1:
            marks.append((end + kerf / 2, True))
        segs.append(dict(mm0=start, mm1=end, name=name, count=count,
                         length=length, sawn=sawn, lead=lead,
                         x0=start * scale, x1=end * scale,
                         qty=_qty_text(count, length), txt=_mm(length),
                         over=per_end, nend=nend))
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


def _over_swatch(page, RL, x, y, w, h):
    """A piece of bar with the dashed cap on it - the key to the overlength."""
    cap = w * 0.30
    page.rect(x, y, w - cap, h, fill="#ffffff", stroke=RL.INK,
              width=RL.T.W_NEW * 0.42)
    page.polylines([[(x + w - cap, y), (x + w, y), (x + w, y + h),
                     (x + w - cap, y + h)]], RL.INK, RL.T.W_NEW * 0.42,
                   dash=OVER_DASH_KEY)


# ---------------------------------------------------------------------------
# THE SHAPE OF THE SHEET
# ---------------------------------------------------------------------------
def _layout(timber, sheets, kerf, page_w, fits):
    """Plan every board at a trial width; say how tall the page came out."""
    bar_x = MARGIN + BUY_COL
    bar_w = page_w - MARGIN - bar_x
    longest = max(b["buy"] for e in timber for b in e["boards"])
    scale = bar_w / longest
    plans = [(e, [_plan_board(b, scale, kerf, e["section"], fits)
                  for b in e["boards"]])
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


def _shape(timber, sheets, kerf, fits):
    """Settle the landscape sheet: height from the metrics, width from ASPECT.

    The vertical metrics are fixed, so the content height is very nearly
    fixed too - it moves only if a wider sheet lets one more label inside its
    piece and saves a callout band. Three passes is far more than that ever
    needs.
    """
    lay = _layout(timber, sheets, kerf, 2100.0, fits)
    for _ in range(3):
        lay = _layout(timber, sheets, kerf, lay["h"] * ASPECT, fits)
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

    # The room's verdict on every cut-list line, keyed the way a board's
    # pieces are keyed. Straight out of the model via gen_doc_tables, so the
    # dashed caps below and the «kapp på stedet» column in the cut list are
    # the same rule read twice.
    fits = {(sec, no_name, length): fit
            for no_name, sec, length, _q, _sp, _en, fit in T.cut_table(G)}
    lay = _shape(timber, sheets, kerf, fits)
    PAGE_W, height = lay["page_w"], lay["h"]
    bar_x, bar_w, scale = lay["bar_x"], lay["bar_w"], lay["scale"]
    plans = lay["plans"]

    page = RL.Page(0.0, 0.0, PAGE_W, height)
    top = height - MARGIN

    # --- the two things this step IS, plus the key to the hatching ---------
    card_w = (PAGE_W - 2 * MARGIN) / 4
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
    # The fourth card is the key to the dashed caps, and its two numbers are
    # read out of the model's own verdicts - not out of this file. If the
    # allowances change, the legend changes with them.
    overs = {}
    for kind, over, ends in G.ROOM_LINES.values():
        mm, n = _room_over((kind, over, ends))
        if n:
            overs[kind] = mm
    foot = next((v for k, v in sorted(overs.items())
                 if k.startswith("gulv")), 0.0)
    wall = overs.get("vegg", 0.0)
    _pictogram(page, MARGIN + 3 * card_w, strip_y, strip_h,
               lambda x, y: _over_swatch(page, RL, x, y + (ICON - 46.0) / 2,
                                         ICON, 46.0),
               ["Stiplet = overmål på romdelene:",
                f"+{_mm(foot)} i bunn, +{_mm(wall)} per veggende"])
    top -= TOP_H

    # --- the boards -------------------------------------------------------
    sale_x = MARGIN + BUY_COL - 20.0

    def _strip(x, y, h, w, segs, mm0, sc, marks, label_size=None,
               zoomed=False):
        """One run of bar: outline, cut marks, and a length on every piece.

        `zoomed` says WHICH strip this is, and it is the whole of the rule
        about who draws what twice: a run that lives in the zoom strip is
        named, numbered and capped DOWN THERE, once, and left blank up on the
        bar. The flag that decides is `inzoom`, which is the same flag the
        names already used - it is set on every run inside the zoom window,
        not only on the tiny ones that opened it. Reading `mode == "zoom"`
        here instead was a bug you could only see when a full-size run
        happened to sit between two small ones: it got its dashed overlength
        cap drawn on both strips, and the cap count stopped matching the cut
        list."""
        page.rect(x, y, w, h, fill="none", stroke=RL.INK,
                  width=RL.T.W_NEW * 0.42)
        for m, boundary in marks:
            mx = x + (m - mm0) * sc
            page.line((mx, y - TICK), (mx, y + h + TICK), RL.INK,
                      RL.T.W_MARK * (0.34 if boundary else 0.24))
        for s in segs:
            # A run that is going to be spelled out in a zoom strip below is
            # left blank up here - there is no room for a number on it.
            if bool(s.get("inzoom")) != zoomed or s["mode"] == "zoom":
                continue
            size = label_size or s["size"]
            base = y + h / 2 - size * 0.36
            if s["mode"] == "group":
                cx = x + ((s["mm0"] + s["mm1"]) / 2 - mm0) * sc
                _label(page, (cx, base), s["qty"], size, weight="bold")
            else:
                for k in range(s["count"]):
                    # The number labels the FINISHED length, so it sits over
                    # the solid part of the piece and not over the allowance.
                    c = (s["mm0"] + (s["sawn"] + kerf) * k + s["lead"]
                         + s["length"] / 2)
                    _label(page, (x + (c - mm0) * sc, base), s["txt"], size,
                           weight="bold")
        # The room's overlength, dashed off the end of every piece that has
        # it. It is drawn where the piece's LENGTH is drawn - so a run that
        # has gone down to the zoom strip is capped down there, once, and not
        # up here where it would be a smudge three units wide.
        for s in segs:
            if bool(s.get("inzoom")) != zoomed or not s["nend"]:
                continue
            for k in range(s["count"]):
                p0 = s["mm0"] + (s["sawn"] + kerf) * k
                q0 = p0 + s["lead"]              # where the finished length
                q1 = q0 + s["length"]            # starts and stops
                caps = ([(q1, q1 + s["over"])] if s["nend"] == 1
                        else [(p0, q0), (q1, q1 + s["over"])])
                for a_mm, b_mm in caps:
                    xa = x + (a_mm - mm0) * sc
                    xb = x + (b_mm - mm0) * sc
                    page.polylines([[(xa, y), (xb, y), (xb, y + h),
                                     (xa, y + h)]], RL.INK,
                                   RL.T.W_NEW * 0.42, dash=OVER_DASH)

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
                       zmarks, zoomed=True)
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
    n_caps = _assert_over_ink(svg, timber, fits)
    RL.to_png(svg, png, width)
    print(f"  steg  0  {n_boards} bord / {n_pieces} deler, {n_caps} overmål "
          f"({PAGE_W:.0f} × {height:.0f}, {PAGE_W / height:.3f}) -> {png}")
    return png


# THE ASSERT THAT READS THE INK. Every dashed cap on the finished sheet is one
# end that the room finishes, so counting them in the file answers the only
# question that matters: does the drawing promise the same overlength the cut
# list does? The count on the other side is built from the packed pieces - the
# model's own cut list, one entry per piece that will actually be sawn - and
# not from the drawing code, so a piece that quietly lost its cap is a failed
# build. The dash is this sheet's only one, which is what makes it countable.
def _assert_over_ink(svg, timber, fits):
    with open(svg, encoding="utf-8") as fh:
        text = fh.read()
    drawn = text.count(f'stroke-dasharray="{OVER_DASH}"')
    want = 0
    for e in timber:
        for b in e["boards"]:
            for name, length, _over in b["pieces"]:
                want += _room_over(fits.get((e["section"], name, length)))[1]
    assert drawn == want, (
        f"kappeplanen tegnet {drawn} stiplede overmål, men modellens "
        f"ROOM_LINES gir {want} ender som rommet kapper")
    return drawn


if __name__ == "__main__":
    import generate_loftbed as _G
    import render_lineart as _RL
    # The pen is the SUBJECT's, so it has to be set before anything is drawn -
    # render_lineart.render_all() does it for the whole run, and this page has
    # to do it for itself when it is asked for on its own.
    _RL.use_model(_G)
    render(_G, os.path.join(ROOT, "docs", "img"), 1600,
           os.path.join(ROOT, "docs", "img", "beslag"))
