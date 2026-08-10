"""The drawing's rule engine: one pen, one occupancy field, one placer.

Nothing here knows about beds, screws or steps. It is the layer under
tools/render_lineart.py that answers the two questions every annotation on a
page asks - HOW BIG is a line, a badge, a margin, and WHERE is there room -
so that the answer is a consequence of rules rather than of a number somebody
liked the look of.

THE PEN
-------
Every width, radius, margin and point size on a step page used to be an
absolute number of model millimetres, tuned against one bed at one scale. That
works exactly as long as the subject never changes size. Here they are all
multiples of ONE length:

    pen = subject_diag / PEN_DIVISOR

`subject_diag` is the diagonal of the DRAWING SUBJECT's own bounding box - the
bed's, a number the model owns - so the whole pen set scales with the thing
being drawn and not with the paper it lands on. Page-relative sizes (the inset
panel's width, the explosion hop, the white margin round the art) stay
fractions of the PAGE, because that is what they really are; the ratios below
are the ones that belong to the subject.

THE FIELD
---------
`Occupancy` is where everything already on the paper is written down: the
black line work, the ghosted line work, the panels, and the individual marks
that have landed. It answers two questions and nothing else - `cost(rect)`,
"how much is in the way of a box here", and `clearance(p, cap)`, "how much
white paper is round this point" - and it can name the OWNER of the nearest
mark, which is what lets a caption refuse to park closer to somebody else's
screw than to its own.

THE PLACER
----------
`place()` is the single scoring loop. It takes a fixed, ORDERED list of
candidate positions, the footprint that is going there, the field it has to
live in and the thing it is tethered to, and returns the cheapest candidate -
ties broken by the order the caller listed them, so the same page always comes
out the same way. Direction is never a free variable in it: where a rule says
which way something goes, the caller passes candidates along that direction
only, and the placer chooses the DISTANCE.
"""

import math

PEN_DIVISOR = 400.0

# Every subject-relative size on a drawing, in pens. The comment is what the
# hand-tuned absolute used to be at this bed's scale (pen = 6.87 mm), so the
# table can be read against the drawings it replaces.
RATIOS = {
    # --- line weights ------------------------------------------------------
    "W_PRIOR": 0.32,        # 2.2   parts already standing
    "W_NEW": 1.00,          # 7.0   the parts this step is about
    "W_HERO": 0.80,         # 5.6   the cover drawing
    "W_RULE": 0.38,         # 2.6   inset borders, section outlines
    "W_LEAD": 0.35,         # 2.4   leader lines
    "W_MARK": 0.75,         # 5.2   fastening-point markers
    "W_HATCH": 0.22,        # 1.5   the 45 deg hatching on a cut face
    "W_SCREW": 0.60,        # 4.2   a drawn fastener's own outline
    "W_PHANTOM": 0.44,      # 3.0   the buried part of one
    # --- marks and margins -------------------------------------------------
    "BADGE_R": 3.60,        # 25.0  the circled letters
    "PAD": 10.00,           # 70    white margin round the subject
    "INSET_PAD": 2.30,      # 16.0  inside the inset panel's border
    # --- type --------------------------------------------------------------
    "S_ICON": 6.70,         # 46    the "i" in the information panel
    "S_TITLE": 6.40,        # 44    a panel heading
    "S_BODY": 5.80,         # 40    a line of panel text
    "S_DIM": 4.65,          # 32    a dimension figure
    "S_NOTE": 3.80,         # 26    a label inside a section
    "S_LIMIT": 3.50,        # 24    the standard's limit under one
    # --- floors that used to be loose numbers ------------------------------
    "RING_R": 2.04,         # 14.0  the head-on ring for a screw with no axis
    "RING_DOT_R": 0.73,     # 5.0   its centre
    "ENTRY_R": 0.87,        # 6.0   the dot on the hole a fastener enters
    "HATCH_MIN": 1.31,      # 9.0   smallest hatch pitch in a section
    "SEC_SCREW_MIN": 0.73,  # 5.0   smallest drawn screw diameter in one
    "THUMB_PRIOR_MIN": 0.20,  # 1.4 grey weight floor in a thumbnail
    "THUMB_NEW_MIN": 0.44,  # 3.0   black weight floor in one
}


class Theme:
    """The pen set, derived from the subject and fixed once per run.

    Created unconfigured on import - a drawing module has no model yet at that
    point - and filled in by `set_subject()` as soon as the subject is known.
    Reading a size before then is a programming error and says so, rather than
    quietly handing out a None that turns into a NaN three calls later.
    """

    def __init__(self, subject_diag=None):
        self.subject_diag = None
        self.pen = None
        if subject_diag is not None:
            self.set_subject(subject_diag)

    def set_subject(self, subject_diag):
        assert subject_diag > 0.0, (
            f"tegningsobjektet har diagonal {subject_diag} - en penn kan ikke "
            f"utledes av ingenting")
        self.subject_diag = float(subject_diag)
        self.pen = self.subject_diag / PEN_DIVISOR
        for name, ratio in RATIOS.items():
            setattr(self, name, ratio * self.pen)
        return self

    def __getattr__(self, name):
        if name in RATIOS:
            raise RuntimeError(
                f"Theme.{name} er lest før skalaen er satt - kall "
                f"Theme.set_subject(diagonalen til det som tegnes) først")
        raise AttributeError(name)

    def __repr__(self):
        if self.pen is None:
            return "Theme(usatt)"
        return f"Theme(subject_diag={self.subject_diag:.2f}, pen={self.pen:.4f})"


# ONE theme per process, and it lives here rather than in the drawing module
# on purpose: tools/render_lineart.py is both a script and a module, so when
# it is run directly and tools/render_cutpage.py imports it back, there are
# TWO copies of it - and a pen set on one of them is not the pen the other
# draws with. layout is only ever imported, so this object is the same object
# for everybody.
THEME = Theme()


def subject_diag(shape):
    """The pen's root: the diagonal of the subject's own bounding box."""
    return shape.bounding_box().diagonal


# ---------------------------------------------------------------------------
# THE OCCUPANCY FIELD
# ---------------------------------------------------------------------------
def _seg_dist(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    ll = vx * vx + vy * vy
    if ll < 1e-12:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / ll
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return math.hypot(p[0] - (a[0] + vx * t), p[1] - (a[1] + vy * t))


def _in_rect(p, rect, grow=0.0):
    x, y, w, h = rect
    return (x - grow <= p[0] <= x + w + grow
            and y - grow <= p[1] <= y + h + grow)


def _overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
            * max(0.0, min(ay + ah, by + bh) - max(ay, by)))


class Occupancy:
    """What is already on the paper, and how much it minds company.

    Three kinds of tenant, because they are in the way in three different
    ways. LINE WORK is what the drawing is - a caption may lie over the grey
    ghost of a frame that is already standing, never over the black part the
    step is about, so the two go in under different tags. A BOX is opaque: the
    inset panel does not merely crowd what is under it, it hides it. A POINT
    is a thing that has landed and carries an OWNER, which is the whole reason
    a badge can tell its own screw from the neighbour's.
    """

    def __init__(self):
        self.lines = []     # (polylines, weight, tag)
        self.boxes = []     # (rect, weight, tag)
        self.points = []    # (p, radius, weight, owner)

    # -- filling it in ------------------------------------------------------
    def add_lines(self, plines, weight=1.0, tag="dark"):
        if plines:
            self.lines.append((plines, weight, tag))
        return self

    def add_box(self, rect, weight=1.0, tag="panel"):
        self.boxes.append((rect, weight, tag))
        return self

    def add_point(self, p, radius=0.0, weight=1.0, owner=None):
        self.points.append((p, radius, weight, owner))
        return self

    def add_points(self, ps, radius=0.0, weight=1.0, owner=None):
        for p in ps:
            self.add_point(p, radius, weight, owner)
        return self

    # -- asking it questions ------------------------------------------------
    def clearance(self, p, cap, tags=None):
        """How much white paper is round `p`, given up on once `cap` is hit.

        The distance to the nearest SEGMENT, not to the nearest projected
        vertex: a 1794 mm rail is two points, and a hundred millimetres of
        clearance from either end of it says nothing about the edge running
        between them.
        """
        best = cap
        for plines, _weight, tag in self.lines:
            if tags is not None and tag not in tags:
                continue
            for pl in plines:
                for a, b in zip(pl, pl[1:]):
                    if (min(a[0], b[0]) - p[0] > best
                            or p[0] - max(a[0], b[0]) > best
                            or min(a[1], b[1]) - p[1] > best
                            or p[1] - max(a[1], b[1]) > best):
                        continue
                    d = _seg_dist(p, a, b)
                    if d < best:
                        best = d
        return best

    def cost(self, rect, grow=0.0, tags=None):
        """How much is in the way of a box put here."""
        out = 0.0
        for plines, weight, tag in self.lines:
            if tags is not None and tag not in tags:
                continue
            out += weight * sum(1 for pl in plines for p in pl
                                if _in_rect(p, rect, grow))
        for box, weight, tag in self.boxes:
            if tags is not None and tag not in tags:
                continue
            if _overlap(rect, box) > 1.0:
                out += weight
        for p, radius, weight, _owner in self.points:
            if _in_rect(p, rect, grow + radius):
                out += weight
        return out

    def nearest(self, p, owner=None, foreign=False):
        """(distance, owner) of the closest recorded point.

        `owner=X, foreign=True` asks the question R5 is written in: how close
        is the nearest thing that is NOT mine. A caption that is nearer to
        somebody else's screw than to its own is not crowding the page, it is
        labelling the wrong hole.
        """
        best, who = None, None
        for q, radius, _weight, own in self.points:
            if foreign and own == owner:
                continue
            if not foreign and owner is not None and own != owner:
                continue
            d = math.hypot(p[0] - q[0], p[1] - q[1]) - radius
            if best is None or d < best:
                best, who = d, own
        return (best, who)


# ---------------------------------------------------------------------------
# THE PLACER
# ---------------------------------------------------------------------------
# One scoring loop for every free position on the page. What varies between an
# inset panel, a badge and a floated bracket is the list of candidates and the
# weights - never the loop, and never the tie-break: `min` over
# (score, index) keeps the drawing byte-identical from run to run.
FOREIGN_PENALTY = 40.0


def place(candidates, footprint, occ, tether=None, pull=0.0, owner=None,
          bounds=None, edge=0.0, edge_penalty=10.0, extra=None):
    """The cheapest of a fixed list of candidate CENTRES for one footprint.

    `candidates`  centres, in the order the caller prefers them
    `footprint`   (w, h) of what is being placed
    `occ`         the field it has to live in
    `tether`      the point it belongs to; `pull` is what a millimetre of
                  wandering away from it costs. A caption that has strayed is
                  one the reader has to guess at, so straying is never free.
    `owner`       whose footprint this is. Given one, a candidate that lands
                  nearer a FOREIGN recorded point than its own tether is
                  charged FOREIGN_PENALTY: that is R5, and it is the rule that
                  stops a badge parking on the neighbour's screw.
    `bounds`      (x0, y0, x1, y1) the footprint has to stay inside of, with
                  `edge` of air to spare.

    Returns the winning centre.
    """
    w, h = footprint
    best = None
    for i, c in enumerate(candidates):
        rect = (c[0] - w / 2, c[1] - h / 2, w, h)
        score = occ.cost(rect)
        if bounds is not None:
            x0, y0, x1, y1 = bounds
            if (rect[0] < x0 + edge or rect[1] < y0 + edge
                    or rect[0] + w > x1 - edge or rect[1] + h > y1 - edge):
                score += edge_penalty
        if tether is not None:
            d_own = math.hypot(c[0] - tether[0], c[1] - tether[1])
            score += pull * d_own
            if owner is not None:
                d_foreign, _who = occ.nearest(c, owner=owner, foreign=True)
                if d_foreign is not None and d_foreign < d_own:
                    score += FOREIGN_PENALTY
        if extra is not None:
            score += extra(c)
        if best is None or score < best[0]:
            best = (score, i, c)
    return None if best is None else best[2]
