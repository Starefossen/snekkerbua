"""Emit the generated documentation fragments from the frozen model.

Run by `mise run build`, after the model itself. It does NOT define geometry
and it does NOT touch generate_loftbed.py: it IMPORTS that script (which
builds, validates and exports the model exactly as running it directly does),
then reads its module globals and writes markdown fragments into
docs/generated/, plus the machine-readable build-step description that both
the text guide and the pictorial guide (docs/MONTERING.md) are built from.

THE ANTI-DUPLICATION RULE
-------------------------
Every millimetre that appears in the documentation comes from here, and every
number here comes from generate_loftbed.py. docs/ASSEMBLY.md is allowed to
name parts and to cite J-numbers, but it must never restate a dimension that
one of these fragments already carries - it links to the fragment instead.

WHAT IS WRITTEN
---------------
  docs/generated/kappliste.md      cut list: part, section, length, count,
                                   position extents
  docs/generated/innkjopsliste.md  per profile: which sale lengths to buy,
                                   first-fit cut mapping, waste %
  docs/generated/nokkelmal.md      envelope, heights, depth planes, ladder /
                                   rung / guard coordinates, bolt rows
  docs/generated/byggesteg.md      the full step-by-step build guide
  docs/generated/byggesteg.json    the same steps, machine readable, consumed
                                   by tools/render_lineart.py and
                                   tools/render_steps.py

Nothing here is hand-maintained: rerun `mise run build` and it is all rebuilt.
"""

import json
import math
import os
import re
import sys

# ---------------------------------------------------------------------------
# SHOP CONVENTIONS
# ---------------------------------------------------------------------------
# Sale lengths of planed Norwegian softwood, in mm. Everything is bought in
# these and cut down; the packer below opens 4800 mm boards and then shrinks
# each one to the shortest sale length that still holds what it was given.
SALE_LENGTHS = [2400, 3000, 3600, 4200, 4800]
# ...except where the trade does not actually stock the whole ladder. Butikk-
# runden: 36x98 C24 is sold as a fixed length ONLY at 4800 mm (Montér). 4200 is
# not listed by any retailer and 3600 does not exist in 36 mm C24 at all -
# Moelven mills 4200/4800/5100/5400 and the counter carries 4800. Planning on
# 4200/3600 boards would send the reader home with lengths he cannot buy, so
# the main board is packed into 4800s only. Costs a little more offcut; the cut
# list itself is untouched, this is purchasing.
# V6 butikkrunde: dette er lengdene virket FAKTISK ble kjøpt i. 36x98 finnes
# bare i 4,8 m (se over), og de tre andre lektedimensjonene ble tatt i 4,8 m
# fordi det er den lengden butikken hadde dem i. Kappeplanen skal beskrive det
# virket som ligger på planet, ikke en optimal pakking av en annen lengdeliste.
SALE_LENGTHS_BY_SECTION = {
    "23×98": [4800],
    "36×48": [4800],
    "36×98": [4800],
    "48×68": [4800],
}
KERF = 4                 # saw kerf allowance between two cuts, mm

# Butikkrunden: treskruer selges i faste pakkestørrelser. «1 pk. (24 stk.)» er
# ikke en vare - kolonnen «Kjøp» skal navngi en pakke som finnes, og «Behov»
# blir stående som det tallet sengen faktisk trenger.
SCREW_PACK_SIZES = [8, 20, 25, 50, 100, 200]

# The joint table, the trade names, the counts and the EC5 row geometry all
# live in generate_loftbed.py now - the model places the fasteners, so the
# model is where they are defined. This file only prints them.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import generate_loftbed as _MODEL          # noqa: E402

JOINTS = _MODEL.JOINTS
JOINT = _MODEL.JOINT
PART_NO = _MODEL.PART_NO
SCREW_D = _MODEL.SCREW_D
MIN_EDGE = _MODEL.MIN_EDGE
MIN_SPACING_GRAIN = _MODEL.MIN_SPACING_GRAIN
MIN_SPACING_CROSS = _MODEL.MIN_SPACING_CROSS


def _fmt(v):
    """Numbers the way a Norwegian tape measure reads them."""
    if isinstance(v, float) and abs(v - round(v)) < 1e-6:
        v = int(round(v))
    if isinstance(v, float):
        # one decimal normally, two when rounding to one would lose the value
        txt = f"{v:.1f}" if abs(v - round(v, 1)) < 1e-9 else f"{v:.2f}"
        return txt.replace(".", ",")
    return str(v)


def _rng(a, b):
    return f"{_fmt(a)}..{_fmt(b)}"


def _no_section(G, section):
    """The model names the panel stock in English; the docs are Norwegian."""
    if "panel" in section:
        return f"{G.PANEL_T} mm plate, {G.PANEL_W} bred"
    return section.replace("x", "×")


def _axis(ranges):
    """One position cell: the common range, or the span the group covers."""
    uniq = sorted(set(ranges))
    if len(uniq) == 1:
        return _rng(*uniq[0])
    return _rng(min(r[0] for r in uniq), max(r[1] for r in uniq)) + " (fordelt)"


def step_fastener_rows(st):
    """[(handelsnavn, antall), ...] for one step, summed from its joints."""
    total = {}
    for jid, cnt in st["joints"].items():
        for name, per in JOINT[jid]["fast"]:
            total[name] = total.get(name, 0) + per * cnt
    return sorted(total.items())


def _badge_alphabet():
    """The letters a step's fastener kinds are badged with.

    Defined once, in tools/gen_glyphs.py - the file that DRAWS them. Imported
    late because gen_glyphs pulls in the SVG machinery this module does not
    otherwise need.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_glyphs
    return gen_glyphs.BADGE_ALPHABET


def step_badges(st):
    """{handelsnavn: 'A'} for a step that drives more than one kind of fastener.

    A step with one kind needs no letters - the glyph in its table IS the
    answer, and a badge on every arrow would be noise. A step with several
    does: the letter is what ties an arrow in the drawing to a row in the
    table, so the reader can see which of the three screws goes where.

    The order is the order the inset and the table use: the commonest first,
    ties broken by name. tools/render_lineart.py derives the same letters from
    the same rows, so the drawing and the page can never disagree.
    """
    rows = step_fastener_rows(st)
    if len(rows) < 2:
        return {}
    order = sorted(rows, key=lambda r: (-r[1], r[0]))
    alphabet = _badge_alphabet()
    return {name: alphabet[i] for i, (name, _q) in enumerate(order)}


def step_fill_code(st):
    """Does this step's page code its fasteners with a fill pattern?

    A DERIVED PROPERTY OF THE STEP, exactly like `half_view` or `info_panel`,
    and it travels with the step into byggesteg.json so that the drawing looks
    it up instead of deciding it. What it is derived FROM is the step's own
    fastener set: the code is bought to separate two screws the SILHOUETTE
    cannot separate, so it is switched on where such a pair exists on the page
    and nowhere else. The threshold is one definition, in tools/gen_glyphs.py
    beside the codes themselves - see `ambiguous_pairs()` there.

    Two consequences worth saying out loud. It is the PAGE that is coded, not
    the pair: fire the rule and every fastener on the page carries its own
    fill, because a page with coded and uncoded screws on it would be telling
    the reader something a third time in a language nobody taught them. And a
    step with a single kind of fastener can never fire it - it has no letters
    either, and a code with one value codes nothing.
    """
    rows = step_fastener_rows(st)
    if len(rows) < 2:
        return False
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_glyphs
    return gen_glyphs.shape_ambiguous([name for name, _q in rows])


def step_fastener_summary(st):
    """The fastener line for one step, summed from the joints it completes."""
    return [f"{qty}× {name}" for name, qty in step_fastener_rows(st)]


def hardware_total(steps):
    """Every fastener in the bed, and the check that the steps add up."""
    seen = {}
    for st in steps:
        for jid, cnt in st["joints"].items():
            assert jid in JOINT, f"step {st['n']} cites unknown joint {jid}"
            seen[jid] = seen.get(jid, 0) + cnt
    for j in JOINTS:
        assert seen.get(j["id"], 0) == j["n"], (
            f"{j['id']}: the build steps complete {seen.get(j['id'], 0)} of "
            f"them, the bed has {j['n']}")
    total = {}
    for j in JOINTS:
        for name, per in j["fast"]:
            total[name] = total.get(name, 0) + per * j["n"]
    return total


# ---------------------------------------------------------------------------
# WHAT THE ROOM FINISHES, AND WHAT IT COSTS THE STEPS
# ---------------------------------------------------------------------------
# Four facts the build steps have to say out loud, and every one of them is a
# property of the MODEL and not of the prose:
#
#   * which pieces the room saws to LENGTH. Their holes cannot be bored on a
#     bench, because the end every one of those holes is measured from does
#     not exist yet - see X6 rule 2 in generate_loftbed.py, which allows a
#     wall end as a datum on exactly one condition: that it is fine-cut off
#     the measured niche BEFORE the drill comes out.
#   * which pieces stand on the floor with a trim allowance under them.
#     Somebody has to be told to cut it off, and in which step.
#   * how big the BACK FRAME is lying down. Step 1 builds it flat and step 2
#     tips it up, and both of those cost room.
#   * where the WALL FIXINGS go. Which joints they are, how many screws each
#     drives and at what height is read out of the model, never typed, because
#     a fixing may be added or moved in the same breath as this is written.
#
# `_match` is the part matcher in the PART MATCHING section further down; it
# is only ever called from inside a function here, so the order is fine.
def room_cut(G, kind):
    """The pieces the room finishes the named way, and their cut-list lines."""
    ps = [p for p in G.CUT_PARTS
          if G.ROOM_FIT.get(p.label, {}).get("kind", "").startswith(kind)]
    assert ps, f"no piece in the model is finished '{kind}' by the room"
    return ps, sorted({p.cut for p in ps})


def wall_cut_joints(G):
    """Joints whose holes are measured off an end the ROOM has not cut yet.

    The one list that keeps X6 rule 2's promise honest. Note what it is NOT:
    it is not «every joint on a piece the room shortens». A hole in the front
    bench rail segment measured from the INNER end can be bored on a bench
    all day - that end is sawn in the shop. It is the datum that decides, so
    the datum is what is read: an `ytre` end on a piece the room cuts to
    length is an end that does not exist yet.
    """
    _ps, lines = room_cut(G, "vegg")
    keys = {(sec, ln) for _n, sec, ln in lines}
    order = {j["id"]: i for i, j in enumerate(JOINTS)}
    hit = set()
    for pl in G.FASTENER_PLACEMENTS:
        if (pl["section"].replace("×", "x"), pl["piece_len"]) not in keys:
            continue
        for a in pl["axes"]:
            if a["role"] == "ende" and any(r["ref"] == "ytre"
                                           for r in a["refs"]):
                hit.add(pl["jid"])
    assert hit, "no joint is measured off a wall end - X6 rule 2 has no owner"
    return sorted(hit, key=lambda j: order[j])


def floor_trim(G, *specs):
    """(count, allowance) for the standing pieces one step trims at the foot.

    Read off the model's own room-fit table, so a piece that stops standing on
    the floor stops being told to trim - and a step that names a piece the
    room does NOT trim stops the build instead of printing an instruction
    nobody can carry out.
    """
    ps = [p for p in G.CUT_PARTS if any(_match(s, p.label) for s in specs)]
    assert ps, f"{specs} matches no part"
    kinds = {G.ROOM_FIT.get(p.label, {}).get("kind", "") for p in ps}
    assert all(k.startswith("gulv") for k in kinds), \
        f"{specs} is not trimmed at the foot by the room: {sorted(kinds)}"
    overs = {G.ROOM_FIT[p.label]["over"] for p in ps}
    assert len(overs) == 1, f"{specs} carries {sorted(overs)} mm of allowance"
    return len(ps), next(iter(overs))


# The back frame: the members step 1 lays out flat and step 2 tips upright.
# Named ONCE - step 1's `parts` list is this list - so the frame the steps
# build and the frame the clearances are measured on cannot drift apart.
#
# X12: AND IT IS NO LONGER A CASE OF ITS OWN. `unit_envelope` below measures
# ANY body a step hands the builder, `step_units` derives what those bodies
# are from the joints the step drives, and `check_step_units` runs the
# manoeuvring rule over all of them. The back frame is what that rule finds
# when it looks at step 1 - the list here is the prose's handle on it, and
# the check asserts the two are the same five pieces.
BACK_FRAME_PARTS = ["Corner Post Back *", "Upper Side Rail Back",
                    "Bench Rail Back (continuous)", "Table Ledger Back"]


def unit_envelope(G, ps):
    """One BODY's box, and what getting it into place costs the room.

    A body is whatever the builder screws together and then lifts, tips or
    carries as one thing. Three spans off the solids and two consequences:

      w  along the wall (X). This is the C9 measurement, taken on an
         assembly instead of on a stick: a body wider than THROUGH_LEN
         cannot be swung in through the opening at all, however light it is.
      t  the thickness of the layer it was built in (Y).
      h  how tall it stands (Z).

    `sweep` is what its far corner traces when it is tipped upright about its
    bottom edge - the same idiom as TILT_SWEEP in the model
    (`math.hypot(BUILT_TOP_Z, OVERALL_DEPTH)` against ROOM_H) - and `need` is
    the niche depth it wants if it has to be built LYING DOWN in the niche:
    its own height, or the finished bed's depth, whichever is the deeper.
    Which of the two binds is a fact about this bed, not a given.
    """
    ext = [(min(p.extents[j][0] for p in ps),
            max(p.extents[j][1] for p in ps)) for j in range(3)]
    h = ext[2][1] - ext[2][0]
    t = ext[1][1] - ext[1][0]
    return dict(labels=sorted(p.label for p in ps), n=len(ps),
                w=ext[0][1] - ext[0][0], t=t, h=h,
                sweep=math.hypot(h, t), need=max(h, G.OVERALL_DEPTH))


def back_frame(G):
    """The back frame's own envelope, and what raising it needs.

    A DIFFERENT number from the bed's, because this is the back frame and not
    the bed: the frame is as tall as its own topmost member and only as thick
    as the one layer it is built in.
    """
    ps = [p for p in G.CUT_PARTS
          if any(_match(s, p.label) for s in BACK_FRAME_PARTS)]
    for spec in BACK_FRAME_PARTS:
        assert any(_match(spec, p.label) for p in ps), \
            f"the back frame names '{spec}' and the model has no such part"
    return unit_envelope(G, ps)


def rung_pitch(G):
    """(lower pitches, upper pitches, the rung the change happens above).

    X9 made the ladder two runs, so it has two pitches and the change is a
    DESIGN DECISION the reader is entitled to see named. Derived from the rung
    tops: the first place two neighbouring gaps stop matching is the joint.
    """
    tops = list(G.RUNG_TOPS)
    gaps = [b - a for a, b in zip(tops, tops[1:])]
    k = next((i for i in range(1, len(gaps)) if abs(gaps[i] - gaps[i - 1]) > 1.5),
             None)
    assert k is not None, "the ladder climbs on one pitch - there is no change"
    return gaps[:k], gaps[k:], k + 1


def wall_end_inset(G, jid):
    """How far from a piece's WALL end this joint's nearest hole stands."""
    for pl in G.FASTENER_PLACEMENTS:
        if pl["jid"] != jid:
            continue
        for a in pl["axes"]:
            for r in a["refs"]:
                if r["ref"] == "bak":
                    return min(r["at"])
    raise AssertionError(f"{jid} has no hole measured from a wall end")


def _member_no(G, part):
    """The Norwegian trade name of a part, off the joint table that names it.

    A part is named by every joint it is in, and the names are not all equally
    sharp: the slats know the back side rail only as «sidevange», the joint at
    its own end calls it «bakre sidevange». The sharpest one wins - and the
    assert says what «sharpest» means, so a genuinely ambiguous part stops the
    build instead of being printed under whichever name came first.
    """
    names = set()
    for f in G.FASTENER_SPECS:
        crow = f.get("crow")
        if crow is None:
            continue
        for who, key in (("pa", "a"), ("pb", "b")):
            if f.get(who) is part:
                names.add(PART_NO[crow[key]])
    assert names, f"no joint names '{part.label}'"
    best = max(sorted(names), key=len)
    assert all(best.endswith(n) for n in names), \
        f"'{part.label}' is called {sorted(names)} - no one of those is the " \
        f"same name with a qualifier on it"
    return best


def wall_fix_lines(G, jids=None):
    """One placement line per wall-fixing joint, measured off the model.

    WHICH joints hold the bed to the wall, how many fixings each drives,
    through which member, at what height and on what nominal spacing all come
    out of WALL_FIXINGS and the fastener solids themselves. Add a fixing, move
    it, take one away - the table follows without a word being edited here.
    """
    out = []
    for jid, part in G.WALL_FIXINGS:
        if jids is not None and jid not in jids:
            continue
        fs = [f for f in G.FASTENER_SPECS if f["jid"] == jid]
        assert fs, f"{jid} fixes the bed to the wall and places no fastener"
        assert all(f["through"] is part for f in fs), \
            f"{jid} does not pass through '{part.label}' all the way"
        zs = {f["anchor"][2] for f in fs}
        assert len(zs) == 1, \
            f"{jid}: the wall fixings stand at {sorted(zs)} - not one row"
        z = next(iter(zs))
        xs = sorted(f["anchor"][0] for f in fs)
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        assert gaps and max(gaps) - min(gaps) < 0.51, \
            f"{jid}: the fixings are not on one pitch ({gaps})"
        ds = {f["d"] for f in fs}
        assert len(ds) == 1, f"{jid}: {sorted(ds)} mm holes in one row"
        fast = JOINT[jid]["fast"]
        assert len(fast) == 1, f"{jid} drives {len(fast)} kinds of fixing"
        (x0, _x1), _y, (z0, z1) = part.extents
        out.append(dict(
            jid=jid, name=fast[0][0], per=fast[0][1], n=len(fs),
            member=_member_no(G, part), section=_no_section(G, part.cut[1]),
            piece_len=part.cut[2], d=next(iter(ds)),
            # The face the head is countersunk in is the face the screw is
            # driven FROM - the opposite one to where it points, read off the
            # solid exactly as the model's own _mark_face does.
            face=(1, "fram" if fs[0]["direction"][1] < 0 else "bak"),
            z=z, below=z - z0, above=z1 - z,
            inset=xs[0] - x0, cc=gaps[0], drill=JOINT[jid]["drill"]))
    return out


# The cut list's room half, named once so the steps can link to it and the
# heading and the anchor can never drift apart.
KAPP_ROOM_HEAD = "Kapp når rommet er ferdig — romdeler"


def kapp_room_link(text="kapplistas rombolk"):
    return f"[{text}](kappliste.md#{_anchor(KAPP_ROOM_HEAD)})"


def _per_joint(jid):
    """«2× Treskrue 6×80» for one joint - the count the model places, never
    a number typed into a sentence."""
    return " + ".join(f"{q}× {_fast_short(n)}" for n, q in JOINT[jid]["fast"])


def _upright_top(G):
    ps = [p for p in G.CUT_PARTS if _match("Ladder Upright *", p.label)]
    tops = {p.extents[2][1] for p in ps}
    assert len(tops) == 1, f"the ladder stiles top out at {sorted(tops)}"
    return next(iter(tops))


def _rung_pitch_do(G):
    """The one line that says the ladder changes pitch, and that it is meant."""
    low, high, at = rung_pitch(G)
    def band(gs):
        return " / ".join(_fmt(v) for v in sorted(set(gs)))
    return (f"**Stigningen skifter over trinn {at}, og det er tilsiktet.** "
            f"{band(low)} mm mellom de nederste trinnene, {band(high)} mm "
            f"mellom de øverste. Stigen er to løp (X9): det nederste er "
            f"trappa opp på benken, det øverste er klatringen opp i senga. "
            f"Måler du {band(low)} der det skal være {band(high)}, har du "
            f"satt en kloss feil — ikke rett opp stigningen, rett opp "
            f"klossen.")


def _room_drill_do(G):
    """Step 0's LAST instruction: the holes the bench is not allowed to bore.

    Every number in it is read out of the room-fit table and the placement
    lines, so the day a piece stops being cut by the room, this paragraph
    stops naming it.
    """
    ps, lines = room_cut(G, "vegg")
    jids = wall_cut_joints(G)
    return (f"**IKKE PÅ BUKKEN — {len(ps)} romdeler skal bores senere.** "
            f"Delene i {len(lines)} kapplinjer under "
            f"«{kapp_room_link(KAPP_ROOM_HEAD)}» har "
            f"{G.ROOM_OVER_WALL} mm overmål i hver ende som møter vegg, og "
            f"hullene deres er målt **fra ytterenden** — nettopp den enden. "
            f"**En ende som ikke er kappet, er ikke et utgangspunkt.** "
            f"Rekkefølgen er: mål nisja, finkapp veggendene etter målt "
            f"bredde, og bor først da. Det gjelder "
            f"{', '.join(jids)}. Legg delene på bukk i rommet når de er "
            f"finkappet; alt annet i dette steget gjøres ferdig i "
            f"verkstedet.")


# ---------------------------------------------------------------------------
# BUILD STEPS - defined ONCE, here
# ---------------------------------------------------------------------------
# `parts`     labels added to the assembly in this step ("*" = prefix match).
#             Every wooden part of the model must appear in exactly one step.
# `highlight` what the step image paints in the highlight colour; defaults to
#             `parts`. A step that only moves or fixes what is already there
#             (raising the frames, bolting to the wall) re-highlights instead.
# `camera`    (azimuth, elevation, distance) for tools/render_steps.py.
#             Azimuth 0 looks the ladder straight in the face; 270 is the
#             X = 1990 end; the back wall is at 180.
#
# WHAT KIND OF PAGE A STEP GETS is declared here too, because it is a property
# of the STEP and not of its number. tools/render_lineart.py used to carry it
# as a handful of `if n == 0`, `if n == 2`, `if n == 10`, a HALF_VIEW_STEPS
# set and one label prefix match, which meant the answer to "why is this page
# different" lived in a file that is not allowed to know anything the model
# does not. All of these default to false/absent, so an ordinary step says
# nothing at all:
#
# `page`             "cutpage" or "panel": a page that is not a projection of
#                    the bed and has a module of its own.
# `half_view`        the step builds the SAME CORNER TWICE, once at each end,
#                    and nothing in between - so the drawing is cropped to one
#                    end and a mirror pictogram carries the other. The counts
#                    stay whole-step counts.
# `thumbnails`       before/after pair: the one step that changes the
#                    workpiece's orientation.
# `crop_to_subject`  the step's parts are a narrow thing in a wide bed and get
#                    a page cut round them instead of the shared bed page.
# `no_fasteners`     nothing is fastened: no marks, no inset, no coverage
#                    check.
# `info_panel`       the corner panel is an information panel rather than a
#                    fastener list.
# `avoid_top_left`   the top left corner is what the drawing is ABOUT, so no
#                    panel may be parked there.
def build_steps(G):
    # The batten profile and a Norwegian decimal, both wanted in several of
    # the strings below and neither worth repeating.
    _SEC = G.sec(G.BATTEN_W, G.BATTEN_H).replace("x", "×")

    def _mm(x):
        return f"{x:.1f}".rstrip("0").rstrip(".").replace(".", ",")

    return [
        dict(
            n=0,
            title="Kapping, forboring og forsenking",
            # There IS a drawing for step 0, it is just not a view of the bed:
            # tools/render_cutpage.py lays every purchase length out as a bar
            # with its cuts marked. So `image` is true and `camera` is None.
            image=True,
            page="cutpage",
            parts=[],
            highlight=[],
            camera=None,
            intro="Gjør alt sagarbeid og all boring på bukk, før noe reises. "
                  "Etterpå kommer du ikke til med drillen på de flatene som "
                  "vender mot vegg.",
            do=[
                "Kapp etter kapplista. **Verksteddelene kappes ferdig; "
                  "romdelene kappes med overmål** — kapplista sier hvilke og "
                  "hvor mye, og de finkappes i rommet. Alle kutt er 90°, "
                  "ingen gjæring — med to navngitte unntak, og begge står i "
                  "kapplista: de to kilelektene under platens forkant, og de "
                  "to vinkelklossene.",
                f"Skråkapp de to kilelektene. De er {_SEC} × {G.NOSE_LEN} mm "
                  "og skal "
                  "sages ned i ett rett snitt fra full høyde i den ene enden "
                  f"til {G.NOSE_TIP_H} mm i den andre ("
                  + f"{G.NOSE_TAPER_DEG:.1f}".replace(".", ",")
                  + "°). Håndsag eller båndsag; "
                  "overkanten — den som skal limes mot plata — skal stå "
                  "urørt og plan.",
                "Lag de to vinkelklossene, borjiggene til skråskruene — én "
                  "til J8-B og én til J10. Hver kloss er "
                  f"{G.TOE_JIG_PLIES} biter {_SEC} × {G.TOE_JIG_LEN} mm av "
                  "restene, skrudd FLATE MOT FLATE. Bor "
                  f"⌀{G.TOE_SEAT_D:g} VINKELRETT gjennom begge mens klossen "
                  "ennå er firkantet — det er hullet som styrer boret siden, "
                  "ikke en rampe. Kapp så sålen av under hullet på kappsag "
                  f"med bladet vippet {G.TOE_JIG_ANGLES['J8-B']:g}° (J8-B) "
                  f"hhv. {G.TOE_JIG_ANGLES['J10']:g}° (J10).",
                "**Vippen og flaten er komplementvinkler.** "
                  f"{G.TOE_JIG_ANGLES['J8-B']:g}° vipp gir en såle som står "
                  f"{90 - G.TOE_JIG_ANGLES['J8-B']:g}° på den borede flaten "
                  f"— og dermed {G.TOE_JIG_ANGLES['J8-B']:g}° på hullaksen, "
                  "som er det leddet er regnet på. Kontroller med "
                  "tommestokken før klossen får røre sengen: hullets munning "
                  "i sålen skal måle "
                  + _mm(G.TOE_JIG_ELLIPSE['J8-B'][0]) + " × "
                  + _mm(G.TOE_JIG_ELLIPSE['J8-B'][1])
                  + f" mm på {G.TOE_JIG_ANGLES['J8-B']:g}°-klossen og "
                  + _mm(G.TOE_JIG_ELLIPSE['J10'][0]) + " × "
                  + _mm(G.TOE_JIG_ELLIPSE['J10'][1])
                  + f" mm på {G.TOE_JIG_ANGLES['J10']:g}°-klossen. Er "
                  "ellipsen for kort, ble vippen satt på feil vinkel. "
                  "Klossene bygges ikke inn i sengen — de er verktøy.",
                "Merk hver del med blyant på en flate som blir skjult.",
                "**Bryt alle kanter et barn kan nå, nå — mens delene er "
                  "løse.** Kravet er brutt kant, ikke en bestemt metode: "
                  "45° fas eller avrunding, du velger. Fres med V-spor eller "
                  "avrundingsfres om du har fres; ellers gjør en blokkhøvel "
                  "eller en pussekloss med 120-korn nøyaktig samme nytte. "
                  "Viktigst: plateenhetens underside — begge styrelektenes "
                  "nedre kanter og begge kilene — for det er der et kne "
                  "møter treet når noen sitter ved bordet. Deretter platens "
                  "fire egne kanter, og så stolper, rekkverksbord, trinn og "
                  "stigevangenes kanter. Modellen tegner alle deler skarpe; "
                  "kantbrytningen er en instruks og flytter ingen mål.",
                "Bor alle gjennomgående hull i **verksteddelene** — stolper, "
                  "endebjelker og de delene kapplista sier er ferdig kappet. "
                  "Diameter etter forboringskolonnen i beslaglista. Bor "
                  "gjennom begge deler samtidig, med delene tvunget sammen.",
                "Forsenk hodene på alle festemidler som ender i en veggvendt "
                  "flate. Beslaglista sier hvilke ledd det gjelder.",
                "Forbor alle treskruer etter beslaglista. I bordene og i "
                  "all endeved er forboring et krav, ikke et råd.",
                "**Bor setene til de åtte skråskruene nå** — mens delene er "
                  "løse og ligger flatt på benken. Fire i den bakre "
                  "benkevangens forside (J8-B) og fire i stubbeføttenes "
                  "innersider (J10). Reist seng kommer du ikke til med "
                  "hverken kloss eller tvinger. Alt om setene og klossene er "
                  "tegnet opp på "
                  "[setedetalj.svg](../schematics/setedetalj.svg).",
                "Slik bores et sete: klem vinkelklossen mot flaten med TO "
                  "tvinger, hullet rett over merket, og legg en offerkloss "
                  "mot endeveden. Drillen i **gir 1 og slag AV** — et "
                  "forstnerbor i slagmodus brenner og vandrer. Trekk boret "
                  "helt ut 2–3 ganger per lomme og børst sponet ut; et fullt "
                  "forstnerbor skjærer ikke, det gnisser. Dybden er merket "
                  "du satte på boret da du lagde klossen: "
                  f"{G.TOE_JIG_SEATS['J8-B']:g} mm langs aksen på J8-B, "
                  f"{G.TOE_JIG_SEATS['J10']:g} mm på J10.",
                "På den bakre benkevangen står to lommer ved siden av "
                  "hverandre i hver ende, "
                  f"{G.TOE_SEAT_D + G.TOE_SEAT_MIN_WEB:g} mm fra senter til "
                  "senter. **Bor den som ligger nærmest kanten først** — da "
                  "har klossen hel flate å stå på. Når den andre skal bores, "
                  "hviler klossen delvis over den ferdige lomma; legg en "
                  "tynn list under den enden så den ikke vipper.",
                "Forbor for skruen med det samme, mens delen ligger som den "
                  "ligger: **lommebunnen er forborets egen jigg.** Bunnen "
                  "står vinkelrett på skrueaksen, så et brad-point-bor satt "
                  "i senter av den flate bunnen (⌀6 på J8-B, ⌀3,5 på J10) "
                  "retter seg selv inn i riktig vinkel. Ikke prøv å sikte "
                  "den på frihånd.",
                "Slå filtknotter under alle fire hjørnestolper og alle fire "
                  "stubbeføtter.",
                _room_drill_do(G),
            ],
            check=[
                "Romdelene skal IKKE kappes ferdig nå, og hullene i dem skal "
                  "ikke bores nå. Kapplista sier hvilke — de kappes med "
                  "overmål, finkappes i rommet, og bores der.",
                "Legg de to lengste delene — sidevangene — inn i rommet nå og "
                  "sjekk at de går fritt forbi begge vegger. De er kappet "
                  "kortere enn veggavstanden nettopp for dette.",
                "Legg delene i fire hauger på gulvet, én per steg. Du kommer "
                  "til å lete mindre.",
            ],
            joints={'J15': 8},
        ),
        dict(
            n=1,
            title="Bakrammen — bygg den flatt på gulvet i nisja",
            parts=list(BACK_FRAME_PARTS),
            camera=(330, 24, 3.4),
            half_view=True,
            intro=f"Hele baksiden av sengen er ett eneste flatt lag: to korte "
                  f"stolper og tre vannrette deler i samme plan. Det laget er "
                  f"monteringsflaten mot veggen. Og det MÅ bygges som én "
                  f"ramme: den bakre benkevangen og bordbærelekta er kappet "
                  f"til å fylle nøyaktig mellom de to stolpene, så de lar seg "
                  f"ikke tre inn etterpå. **Rammen bygges liggende INNE i "
                  f"nisja**, med underkanten mot bakveggen — den er "
                  f"{G.WALL_SPAN} mm bred og lar seg ikke bære inn ferdig "
                  f"reist. Det er den samme rammen steg 2 tipper opp.",
            do=[
                f"Rydd gulvet i nisja og legg ut papp eller teppe. Rammen "
                  f"legges ned der den skal stå: underkanten inntil "
                  f"bakveggen, toppen ut mot rommet. Den tar "
                  f"{_fmt(back_frame(G)['h'])} mm av nisjedybden liggende — "
                  f"målet du kontrollerte i forsteget.",
                "Legg de to bakre stolpene ut i riktig avstand. De er de "
                  "korte — de stopper under sidevangen.",
                "Legg den bakre sidevangen oppå stolpetoppene. Den skal "
                  "hvile på endeveden, ikke henge på siden av stolpen. Fest "
                  "etter J2-B.",
                "Legg den bakre benkevangen ned mellom stolpene og fest den "
                  "etter J8-B. Det står ingen kloss under vangeenden — "
                  "**hullene du boret i steg 0 er jiggen**: vangen har "
                  "nøyaktig én høyde der hullene i vangen og hullene i "
                  "stolpen står over hverandre. Legg en list eller en tvinge "
                  "under vangen mens du skrur hvis du er alene. Vangen er "
                  "kappet nøyaktig så den fyller mellom de to stolpene — den "
                  "kan ikke tres inn senere.",
                "J8-B er skråskruer, og setene deres er boret i steg 0 — "
                  f"⌀{G.TOE_SEAT_D:g} flatbunnet lomme "
                  f"{G.TOE_JIG_SEATS['J8-B']:g} mm ned langs skruens egen "
                  f"akse, {G.TOE_JIG_ANGLES['J8-B']:g}° på flaten. Her skal "
                  "du bare skru. Skruen finner lomma selv gjennom forboret; "
                  "kjenn etter at hodet lander flatt på bunnen og ikke "
                  "stopper høyt. Stopper det høyt, står konusen på kanten av "
                  "forboret — skru ut, rens lomma for spon og ta den om "
                  "igjen.",
                "Sett vinkelbeslagene til bordbærelekta på stolpenes "
                  "innsider, legg lekta på høykant mellom stolpene og fest "
                  "etter J12.",
            ],
            check=[
                "Mål diagonalene i rammen — de skal være like.",
                "Kjenn etter med håndflaten over hele baksiden: ingen "
                  "skruehoder, ingenting som stikker ut. Denne flaten skal "
                  "ligge helt flatt mot veggen.",
                "Legg vinkelhaken på begge hjørner.",
            ],
            joints={'J2-B': 2, 'J8-B': 2, 'J12': 2},
        ),
        dict(
            n=2,
            title="Tipp bakrammen opp og skru den fast i veggen",
            two_person=True,
            parts=[],
            highlight=["Upper Side Rail Back", "Table Ledger Back"],
            camera=(330, 24, 3.4),
            thumbnails=True,
            intro="Sengen festes til veggen i to høyder: gjennom den bakre "
                  "sidevangen øverst og gjennom bordbærelekta nede ved "
                  "bordhøyde. Begge ligger flatt mot veggen i hele sin "
                  "lengde, så skruene går rett gjennom dem og inn i "
                  "stenderne. De skruene holder ikke bare sengen på plass — "
                  "de støtter også de to lange delene på midten.",
            do=[
                f"**Tipp rammen opp om sin egen underkant, der den ligger.** "
                  f"Den skal ikke bæres inn og ikke skyves sidelengs mot "
                  f"sideveggene: rammen er {G.WALL_SPAN} mm bred og nisja er "
                  f"{G.WALL_SPAN} mm — null klaring i begge ender, og en "
                  f"{G.WALL_SPAN} mm del lar seg ikke svinge inn i en "
                  f"{G.WALL_SPAN} mm åpning. Derfor ble den bygget liggende "
                  f"på plassen sin i steg 1. Underkanten er hengselet og blir "
                  f"liggende mot gulvet hele veien opp.",
                f"To personer, én på hver stolpe. Rammens øverste hjørne "
                  f"sveiper {back_frame(G)['sweep']:.0f} mm på vei opp — "
                  f"taket er på {G.ROOM_H} mm, så den går klar, men få "
                  f"lamper og lister ut av veien først.",
                "Skyv rammen inntil bakveggen. Bare bakover — sidelengs er "
                  "det ingen vei å gå.",
                f"**Trim de {floor_trim(G, 'Corner Post Back *')[0]} "
                  f"bakstolpene i bunn nå.** De er kappet "
                  f"{floor_trim(G, 'Corner Post Back *')[1]} mm for lange. "
                  f"Mål ned fra høyderisset i begge ender, strek opp foten "
                  f"med avstandskloss, legg rammen ned igjen og kapp. Tipp "
                  f"opp på nytt og vater langs sidevangen. Gjenta til vangen "
                  f"ligger vannrett — det er den høyden hele sengen arves "
                  f"fra.",
                "Finn stenderne i veggen. Merk av senterlinjene på "
                  "sidevangen og på bordbærelekta.",
                "Loddsjekk begge stolper, og vater langs sidevangen.",
                "Skru rammen fast i veggen gjennom sidevangen (J14). Ta et "
                  "feste i hver stender du treffer — minst i endene og på "
                  "midten.",
                "Skru bordbærelekta fast i veggen på samme måte (J12-V), midt "
                  "i lektas høyde. **Hullene bores nå, ikke i verkstedet** — "
                  "stenderne finnes bare i rommet, og lekta satt i rammen "
                  "allerede i steg 1. Forsenk hodene under lektas forside; "
                  "det er den ryggputa lener seg mot. Lekta bærer bordplatens "
                  "bakkant, og disse skruene tar den lange spennvidden ned "
                  "til tre korte.",
                "Skru en midlertidig skråstiver fra rammen ned til gulvet "
                  "hvis rammen står alene en stund. Den er flat og velter "
                  "lett framover.",
            ],
            check=[
                "Vater langs sidevangen, og lodd på begge stolper.",
                "Begge bakstolper skal stå med hele endeflaten mot gulvet "
                  "etter trimmingen. Er det luft under en av dem, er den ikke "
                  "trimmet nok — kil den ikke opp.",
                "Ta tak i vangen og dra. Rammen skal ikke bevege seg fra "
                  "veggen i det hele tatt.",
                "Kjenn etter langs bordbærelektas overkant: den skal ligge "
                  "vannrett og skruehodene skal stå under forsiden.",
                "Er veggen mur eller betong, bruk plugg eller betongskrue. "
                  "Er den bindingsverk, må du treffe stender. En plateplugg i "
                  "gips er ikke et veggfeste.",
            ],
            joints={'J14': 1, 'J12-V': 1},
        ),
        dict(
            n=3,
            title="Endebjelkene og de fremre stolpene",
            parts=["Corner Post Front *", "End Beam Left", "End Beam Right"],
            camera=(325, 22, 3.4),
            half_view=True,
            intro="Nå bygges de to endene ut fra bakrammen. Endebjelken går "
                  "fra den bakre stolpen til den fremre og bærer begge "
                  "sidevanger.",
            do=[
                f"**Trim de {floor_trim(G, 'Corner Post Front *')[0]} fremre "
                  f"stolpene i bunn før de reises.** De har samme "
                  f"{floor_trim(G, 'Corner Post Front *')[1]} mm overmål som "
                  f"bakstolpene: still stolpen opp mot sideveggen, mål ned "
                  f"fra høyderisset, strek opp foten med avstandskloss og "
                  f"kapp. Toppen er referansen — hvert hull i stolpen er "
                  f"målt derfra, og det er derfor foten er den enden som "
                  f"kappes.",
                "Reis den fremre stolpen på plass mot sideveggen.",
                "Legg endebjelken opp mellom de to stolpene og fest den til "
                  "begge etter J1. **Det er ingen bærekloss under "
                  "bjelkeenden, og hullene fra steg 0 er jiggen:** bjelken "
                  "har nøyaktig én høyde der hullene i bjelken og hullene i "
                  "stolpen møtes, så du kan ikke sette den skjevt. Klem en "
                  "list på stolpens innside i høyde med bjelkens underkant "
                  "hvis du bygger alene — den listen tas av igjen.",
                f"**De to bakerste J1-skruene står "
                  f"{_fmt(wall_end_inset(G, 'J1'))} "
                  f"mm fra bakveggen.** Der får du ikke inn en drill med "
                  f"vanlig bits. Ta lang bits eller vinkelbits, og prøv "
                  f"rekkevidden før bjelken ligger på plass — etterpå er det "
                  f"ingen vei rundt.",
                "Gjenta i den andre enden.",
            ],
            check=[
                "Vater på begge endebjelker, og kontroller at de ligger i "
                  "nøyaktig samme høyde.",
                "Lodd på begge fremre stolper, i begge retninger.",
                "Endebjelkens overkant skal ligge i flukt med den bakre "
                  "sidevangens underkant. Gjør den ikke det, får ikke den "
                  "fremre vangen samme høyde som den bakre.",
                "Kjenn etter at ingenting stikker ut mot sideveggene.",
            ],
            joints={'J1': 4},
        ),
        dict(
            n=4,
            title="Fremre sidevange",
            two_person=True,
            parts=["Upper Side Rail Front"],
            camera=(330, 24, 3.4),
            intro="Den fremre vangen lukker rammen i overetasjen. Den hviler "
                  "på begge endebjelker og festes til de fremre stolpene.",
            do=[
                f"Løft vangen opp på endebjelkene, på utsiden av dem. **To "
                  f"personer**, én i hver ende: vangen er {G.THROUGH_LEN} mm "
                  f"lang og skal treffe to opplegg i "
                  f"{G.RAIL_BOTTOM} mm høyde samtidig. Alene ender den ene "
                  f"enden på gulvet.",
                "Fest den til begge fremre stolper etter J2. **Skruene "
                  "drives innenfra:** du står inne i sengerammen — den er "
                  "tom, spilene kommer først i steg 8 — og skrur gjennom "
                  "vangens innside og inn i stolpen. Da blir stolpens "
                  "forside, som er den flaten rommet ser, helt uten "
                  "skruehoder.",
            ],
            check=[
                "Mål avstanden mellom de to sidevangene i begge ender og på "
                  "midten. Den skal være lik overalt — det er madrassbredden, "
                  "og madrassen er kappet nøyaktig etter den.",
                "Vater langs vangen, og kontroller at den ligger i samme "
                  "høyde som den bakre.",
                "Mål diagonalene i sengeflaten sett ovenfra.",
            ],
            joints={'J2': 2},
        ),
        dict(
            n=5,
            title="Fremre benkevanger, stubbeføtter og endelister",
            parts=["Bench Rail Front *", "Bench Stub Leg *",
                   "Bench End Cleat *"],
            camera=(330, 20, 3.4),
            half_view=True,
            intro="Den fremre benkevangen er delt i to. Midtpartiet er med "
                  "vilje åpent, slik at gulvet foran stigen er helt fritt. "
                  "Endelisten hører hjemme i dette steget og ikke blant "
                  "spilene: den er bæreverk som vangene, den står i samme "
                  "høyde som dem, og den skal stå ferdig før noe legges oppå.",
            do=[
                f"Fest hver vangebit til sin fremre hjørnestolpe etter J8. "
                  f"**Skruene drives innenfra**, fra vangens innside og inn i "
                  f"stolpen, så stolpens forside blir stående uten "
                  f"skruehoder. Du kommer til ovenfra: benken er åpen til "
                  f"spilene går på i steg 7. Ingen kloss under enden — "
                  f"hullene holder vangen i riktig høyde. Vangebiten er en "
                  f"romdel: hullene i den ble boret etter finkapp, se det "
                  f"siste punktet i steg 0 og {kapp_room_link()}.",
                f"**Trim de {floor_trim(G, 'Bench Stub Leg *')[0]} "
                  f"stubbeføttene i bunn.** De er kappet "
                  f"{floor_trim(G, 'Bench Stub Leg *')[1]} mm for lange. Hold "
                  f"foten opp under vangen der den skal stå, strek av mot "
                  f"gulvet med avstandskloss, og kapp. Én fot om gangen — "
                  f"gulvet er ikke i vater, og de fire blir ikke like lange.",
                "Sett en stubbefot under den innerste enden av hver "
                  "vangebit. Vangebiten skal slutte akkurat der foten står — "
                  "ingen utstikk forbi foten.",
                "Sett de to bakre stubbeføttene under den bakre benkevangen, "
                  "rett under de samme punktene.",
                "Fest alle fire føtter etter J10. Den ene 5×60 per fot er "
                  "en skråskrue nedenfra og opp i vangen, og setet er boret "
                  f"i steg 0 — ⌀{G.TOE_SEAT_D:g} flatbunnet lomme "
                  f"{G.TOE_JIG_SEATS['J10']:g} mm ned langs aksen, "
                  f"{G.TOE_JIG_ANGLES['J10']:g}° på fotens innerside. Skru "
                  "beslaget først, skråskruen sist.",
                f"ENDELISTEN, én i hver ende: skru den flatt på FORSIDEN av "
                  f"den bakre hjørnestolpen, med overkanten i flukt med "
                  f"benkevangens overkant ({G.END_CLEAT_Z1} mm over gulvet). "
                  f"To 5×60 ved siden av hverandre (J17) — {G.END_CLEAT_T} mm "
                  f"gjennom listen og {G.END_CLEAT_BITE} mm inn i stolpen, så "
                  f"det står {G.POST_T - G.END_CLEAT_BITE} mm igjen til "
                  f"veggflaten bak. Ikke bruk lengre skrue.",
            ],
            check=[
                "Ingenting skal krysse gulvet mellom de to benkene.",
                "Vater langs begge vangebiter, og samme høyde som den bakre "
                  "benkevangen.",
                "Alle fire føtter skal stå med hele endeflaten mot gulvet og "
                  "hele toppflaten mot vangen. Er det luft under en fot, kil "
                  "den ikke opp — juster den.",
                "Legg en rett list fra endelisten og bort på begge "
                  "benkevanger. Alle tre overkanter skal ta borti listen — "
                  "det er flaten spilene legges på i steg 7.",
                "Ingen skruespiss skal være synlig eller følbar på baksiden "
                  "av den bakre stolpen. Det er veggflaten.",
            ],
            joints={'J8': 2, 'J10': 4, 'J17': 2},
        ),
        dict(
            n=6,
            title="Stigen",
            parts=["Ladder Upright *", "Rung Block *", "Ladder Rung_*"],
            camera=(0, 16, 3.6),
            crop_to_subject=True,
            intro="Bygg hele stigen ferdig liggende på gulvet, og skru den så "
                  "på den fremre sidevangen.",
            do=[
                f"Skru stigeklossene på innsiden av hver stigevange (J5). "
                  f"Klossen er {G.RUNG_BLOCK_LEN} mm lang — nøyaktig så dyp "
                  f"som stigevangen — og skal ligge i flukt med vangens "
                  f"for- og bakkant, ikke stikke bakover slik trinnet gjør. "
                  f"Klosshøyden er trinnhøyden — mål to ganger.",
                "Legg trinnene på klossene og fest dem (J4).",
                _rung_pitch_do(G),
                f"**Trinn {G.CLIMB_LANDING + 1} er STØTTETRINNET — det er "
                  f"bordplatens forkant i bordstilling.** Ingen egen del og "
                  f"ingen ekstra skrue: det er det samme trinnet som de "
                  f"andre, satt med overkanten på {G.PANEL_UNDER_TABLE} mm "
                  f"over gulvet. Har du en eldre tegning med to "
                  f"BORDKLOSSER på vangenes innside her, er den utgått — "
                  f"klossene er strøket, og trinnet gjør jobben deres.",
                "Reis stigen mot den fremre sidevangen. Trinnenes forkant "
                  "skal ligge i flukt med stigevangenes forkant — trinnene "
                  "stikker BAKOVER, ikke framover. Det som stikker bakover er "
                  "hylla den løse platen skal hvile på.",
                f"**Trim de {floor_trim(G, 'Ladder Upright *')[0]} "
                  f"stigevangene i bunn — og gjør det nå, mens stigen står "
                  f"prøvd opp.** De er kappet "
                  f"{floor_trim(G, 'Ladder Upright *')[1]} mm for lange. "
                  f"Stigen ble bygget liggende, så trimmingen går i tre "
                  f"trekk: hold stigen i lodd med toppen der den skal sitte, "
                  f"strek av mot gulvet med avstandskloss, ta den ned og legg "
                  f"den flatt, og kapp begge vanger. Prøv opp igjen før du "
                  f"skrur.",
                f"Skru stigen fast til vangen etter J3 — **innenfra**, "
                  f"gjennom sidevangen og inn i stigevangen, så stigevangens "
                  f"forside blir uten skruehoder. Klem stigen fast mot vangen "
                  f"først; du står på den andre siden når du skrur. "
                  f"Gjennomgangshullene sitter i sidevangen, som er en "
                  f"romdel: de ble boret etter finkapp, se det siste punktet "
                  f"i steg 0.",
            ],
            check=[
                "Mål lysåpningen mellom stigevangene øverst og nederst — den "
                  "skal være lik.",
                f"Alle {len(G.RUNG_TOPS)} trinn i vater.",
                f"Mål ned fra STIGEVANGENS TOPP til STØTTETRINNETS overkant: "
                  f"{_fmt(_upright_top(G) - G.PANEL_UNDER_TABLE)} mm i begge "
                  f"ender, og trinnet i vater. Målt ovenfra, som alt annet "
                  f"på en stående del — foten er nettopp trimmet og er ikke "
                  f"et utgangspunkt. Bordplaten hviler på dette trinnet og "
                  f"på bordbærelekta samtidig; står de i ulik høyde, vipper "
                  f"platen.",
                "Stå på nederste trinn og kjenn etter. Sitter noe løst nå, "
                  "sitter det løst for alltid.",
            ],
            joints={'J3': 2, 'J4': 2 * len(G.RUNG_TOPS),
                    'J5': 2 * len(G.RUNG_TOPS)},
        ),
        dict(
            n=7,
            title="Benkespiler og endespiler",
            parts=["Bench Slat *", "Bench End Slat *"],
            camera=(330, 30, 3.4),
            intro=f"Fem spiler per benk, lagt oppå benkevangene — og helt ute "
                  f"ved hver vegg en {G.END_SLAT_LEN} mm ENDESPILE på "
                  f"endelisten fra steg 5. De to endespilene er det som gjør "
                  f"underetasjen til en seng i full lengde: uten dem stopper "
                  f"spilefeltet "
                  f"{G.BENCH_SLAT_W} mm fra veggen i hver ende, og putekanten "
                  f"har ingenting under seg.",
            do=[
                "Legg ut alle fem spilene på én benk før du skrur, og sjekk "
                  "delingen mot kapplista.",
                "Skru hver spile ned i den bakre og den fremre benkevangen, "
                  "én skrue per ende (J11). Forsenk hodene — dette er en "
                  "sitteflate.",
                "Gjenta speilvendt på den andre benken.",
                f"ENDESPILEN er kortere enn de andre, {G.END_SLAT_LEN} mm: "
                  f"den starter på stolpens forside, ikke på veggen — "
                  f"stolpen står i soveflaten her. Endelisten den skal hvile "
                  f"på sitter ferdig på stolpen fra steg 5; her legges bare "
                  f"spilen. Legg den mot veggen, tett inntil naboen, og skru "
                  f"én skrue ned i endelisten (J16) og én ned i den fremre "
                  f"benkevangen (J11-E).",
            ],
            check=[
                "Kjenn over hele benken med håndflaten: ingen skruehoder skal "
                  "stikke opp.",
                "Sett deg på begge benker.",
                "Endespilen skal ligge i nøyaktig samme plan som de andre — "
                  "legg en rett list på tvers over hele benken og se etter "
                  "lys under.",
            ],
            joints={'J11': 20, 'J11-E': 2, 'J16': 2},
        ),
        dict(
            n=8,
            title="Køyespiler",
            parts=["Bed Slat_*"],
            camera=(330, 40, 3.4),
            intro="Spilene ligger OPPÅ begge sidevanger — ikke i et spor og "
                  "ikke på en lekt. Alle er like lange.",
            do=[
                "Legg ut alle spilene løst først og fordel dem etter "
                  "kapplista, før du skrur noe.",
                "Skyv hver spile helt inn til veggen. Bakkanten på spilene er "
                  "det madrassen støter mot.",
                "Skru hver spile ned i begge vanger, én skrue per ende (J6).",
            ],
            check=[
                "Alle spiler skal dekke hele bredden av begge vanger. Ligger "
                  "en spile bare halvveis på vangen, flytt den.",
                "Ingen skruehoder over flaten — de ligger under madrassen.",
                "Gå over hele bunnen med håndflaten før madrassen legges på.",
            ],
            joints={'J6': 28},
        ),
        dict(
            n=9,
            title="Rekkverk foran",
            parts=["Guard Rail Front *"],
            camera=(330, 22, 3.4),
            intro="To bånd, hvert delt i to bord, med klatreåpningen i "
                  "midten. Man klatrer GJENNOM rekkverket, ikke over. Det er "
                  "ikke rekkverk på baksiden — der er veggen sperren. Bordene "
                  "ligger på INNSIDEN av stolpene, mot sengen, ikke utenpå.",
            do=[
                "Legg det nederste båndet an mot innsiden av hjørnestolpen og "
                  "stigevangen, i flukt med stolpenes innerplan.",
                "Skru fra sengesiden inn i stolpen og i stigevangen (J7). "
                  "Forbor — bordet sprekker lett nær enden.",
                "Gjenta for det øverste båndet.",
            ],
            check=[
                "Mål åpningene over madrassoverflaten mot tallene i "
                  "nøkkelmålene. De er sikkerhetskravet i denne sengen.",
                "Ta tak i toppbordet og dra. Det skal ikke gi seg.",
            ],
            joints={'J7': 8},
        ),
        dict(
            n=10,
            title="Løs plate med fire lekter — og ingen beslag",
            parts=["Movable Panel (bed mode)", "Panel Stiffener Batten *",
                   "Panel Front Batten *"],
            camera=(325, 30, 3.6),
            page="panel",
            intro="Platen er ikke et løst bord. Den er en liten enhet som "
                  "løftes ut i ett stykke og senkes rett ned igjen — i begge "
                  "stillinger. Lektene under den gjør to jobber: de gjør "
                  "platen stiv, OG de er styringen. De to lange går ned på "
                  "hver side av trinnenden med 2 mm klaring, så de finner "
                  "plassen selv. Det er ikke ett beslag i denne mekanismen, "
                  "og det skal ikke være én skrue synlig oppå platen.",
            do=[
                "Bor hullene i lektene FØR noe limes. Regelen er den samme "
                  "for alle fire delene, og den er lettest å huske slik: "
                  f"bor ⌀12 opp i undersiden TIL DET STÅR "
                  f"{G.PANEL_UPSCREW_PASS} mm igjen opp til plata, og ⌀3,5 "
                  "videre gjennom de siste "
                  f"{G.PANEL_UPSCREW_PASS} mm. På de to lange "
                  f"styrelektene, som er {G.BATTEN_H} mm hele veien, blir "
                  f"det {G.PANEL_UPSCREW_CBORE} mm kontrabor. På de to "
                  "skråkappede kilene blir det dypest ved roten og null ved "
                  "tuppen — tuppen ER "
                  f"{G.PANEL_UPSCREW_PASS} mm, så der ligger hodet i flukt "
                  "med kilens egen underside. Skruen tar "
                  f"{G.PANEL_UPSCREW_BITE} mm i den {G.PANEL_T} mm tykke "
                  f"platen uansett, med {G.PANEL_UPSCREW_COVER} mm plate "
                  "igjen over spissen.",
                "Legg platen med undersiden opp. Merk av de to lange "
                  f"avstivningslektene {G.NOSE_LEN} mm inn fra hver sidekant — det er "
                  "målet som gjør at de treffer utsiden av trinnenden.",
                "Lim (D3) hele lektas overkant, legg den på plass og skru "
                  "opp fra undersiden (J13a). Skruene er tvinger: de "
                  "trekker limfugen sammen og blir sittende.",
                "Samme sak for de to kilelektene, i flukt med platens "
                  "forkant og med den HØYE enden mot den lange lekta "
                  "(J13b) — den skråkappede tuppen peker ut mot platekanten. "
                  "De bærer hjørnet trinnet ikke rekker fram til.",
                "Ingenting går gjennom platens overside. Har du et hull "
                  "der, har du boret feil vei.",
                "Legg platen i sengestilling: senk den rett ned mellom "
                  "benkene, bakkanten på den bakre benkevangen, forkanten på "
                  "trinn 1. De to lange lektene skal gli ned på hver side av "
                  "trinnenden uten å tvinges.",
                "Prøv bordstilling: samme plate, samme lekter, rett ned på "
                  "bordbærelekta og STØTTETRINNET. Det er nøyaktig samme "
                  "grep som i sengestilling — samme trinnprofil, samme "
                  "trinnende, samme passing — bare fire trinn høyere oppe. "
                  "Lektene skal gli ned på hver side av trinnenden uten å "
                  "tvinges her også.",
            ],
            check=[
                "Skyv platen sidelengs. Den skal bevege seg et par "
                  "millimeter og så stoppe mot trinnenden — begge veier, i "
                  "begge stillinger.",
                "Vri på platen. Den skal kile seg med én gang: en vridning "
                  "drar begge lektene samme vei, og den ene tar imot.",
                "Platen skal ligge stødig på begge opplegg i begge "
                  "stillinger, uten å vippe. Den ligger på tre i hele "
                  "bredden bak og på trinnet foran.",
                "Se over platens overside i motlys. Ingen skruehoder, ingen "
                  "propper, ingen hull.",
                "Platen kan løftes rett opp. Det skal den kunne — låsen i "
                  "sengestilling er en egen avgjørelse, ikke en del av dette "
                  "steget.",
            ],
            joints={'J13a': 2, 'J13b': 2},
        ),
        dict(
            n=11,
            title="Madrass og puter",
            parts=["Mattress *", "Seat Cushion *",
                   "Back Cushion Left (bed mode)",
                   "Back Cushion Right (bed mode)"],
            camera=(330, 26, 3.4),
            no_fasteners=True,
            info_panel=True,
            avoid_top_left=True,
            intro="Sengen er dimensjonert rundt en STANDARD madrass på "
                  "80 × 200 cm — den er ikke spesialmål og skal ikke "
                  "spesialbestilles. Det eneste målet du må velge selv er "
                  "TYKKELSEN, og der er det bare ett riktig svar: "
                  f"{G.MATTRESS_H} mm. Vinduet er {G.MATTRESS_H_MIN}–"
                  f"{G.MATTRESS_H_MAX} mm, og en helt vanlig 160 mm madrass "
                  "er ULOVLIG i denne sengen — den legger spalten opp til "
                  "rekkverket midt i klemvinduet.",
            do=[
                "Legg madrassen på plass. En 80 × 200 presses de siste "
                  "millimeterne inn mellom veggene, og den skal fylle hele "
                  "dybden fra veggen til de fremre stolpene.",
                f"UNDERETASJEN: fire puter, alle "
                  f"{G.CUSHION_T} mm tykke og {G.LOWER_SLEEP_DEPTH} mm dype. "
                  f"To benkeputer på {G.SEAT_CUSHION_LEN} mm og to ryggputer "
                  f"på {G.BACK_CUSHION_LEN} mm — lagt etter hverandre dekker "
                  f"de nedre soveflate nøyaktig, "
                  f"{G.SEAT_CUSHION_LEN} + {G.BACK_CUSHION_LEN} + "
                  f"{G.BACK_CUSHION_LEN} + {G.SEAT_CUSHION_LEN} = "
                  f"{G.LOWER_SLEEP_LEN} mm.",
                f"Skjær et {G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} mm "
                  f"hakk i veggkanten på hver av de to benkeputene, der den "
                  f"bakre hjørnestolpen står. Brødkniv.",
                "SOFASTILLING: benkeputene ligger der de ligger — de flyttes "
                  "aldri. Ryggputene reises på høykant ytterst på hver benk, "
                  "med ryggen mot bordbærelekta.",
                f"MERK MAKSMÅLET PERMANENT. EN 747 krever det, og det er "
                  f"ikke en tusjstrek som skal kunne tørkes bort: skriv "
                  f"«MAKS MADRASS {G.MATTRESS_H_MAX} MM» på innsiden av en "
                  f"fremre stolpe, i høyden {G.SLAT_Z1 + G.MATTRESS_H_MAX} "
                  f"mm over gulvet. Den som bytter madrass om ti år skal "
                  f"kunne lese grensen av sengen selv.",
                f"Skriv nedre grense, {G.MATTRESS_H_MIN} mm, ved siden av. "
                  f"For tynn madrass åpner spalten under nederste "
                  f"rekkverksbord; for tykk lukker den seg ned i "
                  f"klemvinduet.",
            ],
            check=[
                "Ettertrekk alle festemidler som kan ettertrekkes.",
                "Madrassen skal ligge stramt mot veggen og mot de fremre "
                  "stolpene, uten spalte langs noen av de to lange kantene.",
                "Rist i sengen i begge retninger. Ingen bevegelse mot "
                  "bakveggen.",
                f"Mål spalten fra madrassens overside opp til undersiden "
                  f"av det nederste rekkverksbordet. Den skal være "
                  f"{G.EN_LIMB_BAND[0]:.0f}–{G.MAX_GUARD_OPENING} mm. Er "
                  f"den mindre, er madrassen for tykk.",
                "Sett datoen for første ettertrekk i kalenderen: om fire "
                  "uker, og deretter en gang i året.",
            ],
            joints={},
        ),
        dict(
            n=12,
            title="Fotbrettet",
            parts=["Footrest Cheek *", "Footrest Deck Board_*"],
            camera=(330, 26, 3.4),
            intro="Det siste stykket er ikke en del av sengen. Det er en "
                  "krakk som står under platen, og den er der fordi pulten "
                  "på "
                  f"{G.PANEL_TOP_TABLE} står {G.TABLE_OVER_SEAT} mm over et "
                  "sete som er laget for voksne — barnet får knærne inn "
                  "under platen, men føttene når ikke gulvet. Høyden er ikke "
                  "valgt: den er den eneste av de ni kurvene sengens egne "
                  "dimensjoner kan lage som lar puta bære låret uten at "
                  "putekanten skjærer inn i det. Se X14.",
            do=[
                f"Kapp to gavler "
                  f"{G.sec(G.FOOTREST_CHEEK_T, G.FOOTREST_CHEEK_H)} × "
                  f"{G.FOOTREST_DEPTH} mm og {G.FOOTREST_BOARDS} dekkbord "
                  f"{G.sec(G.FOOTREST_DECK_T, G.FOOTREST_DECK_W)} × "
                  f"{G.FOOTREST_LEN} mm. Alt sammen er rest fra bordene du "
                  "allerede har kjøpt.",
                f"Sett de to gavlene PÅ HØYKANT på et plant underlag, "
                  f"{G.FOOTREST_LEN} mm fra utside til utside — "
                  f"det er nøyaktig dekkbordenes lengde, så de flukter i "
                  "begge ender.",
                f"Legg dekkbordene tvers over, kant i kant, og la endene "
                  "flukte med gavlenes yttersider. Ingen overheng: hele "
                  "dekket skal stå over gavlene, ellers vipper krakken når "
                  "noen tråkker ytterst.",
                f"Forbor ⌀6 gjennom hvert bord og ⌀4 videre ned i gavlens "
                  f"overkant. Én "
                  f"{G.FOOTREST_SCREW.split(' forsenket')[0].lower()} per "
                  "landing, {n} i alt (J18), midt i bordet og midt i "
                  "gavlens tykkelse.".replace("{n}", str(8)),
                "Forsenk hodene UNDER flaten og pusse over. Dette er en "
                  "flate bare føtter står på, ofte uten sokker.",
                "Skyv brettet inn under platen, midt i bukta mellom benkene. "
                  "Det skal ikke skrus fast til noe: det er en løs krakk, og "
                  "gulvet foran stigen skal kunne feies.",
            ],
            check=[
                f"Mål dekkets overkant: {G.FOOTREST_TOP} mm over gulvet.",
                "Sett deg på benken med knærne under platen og sålene på "
                  "brettet. Låret skal ligge på puta hele veien ut til "
                  "putekanten, og leggen skal stå i lodd.",
                f"Sjekk at brettet ikke stikker ut i noen av de to "
                  f"gangpassasjene ved stigen — det skal stå mellom "
                  f"X {G.FOOTREST_X0} og {G.FOOTREST_X1}, altså i bredden "
                  "mellom stigevangenes yttersider.",
                "Vipp på brettet. Det skal ikke vippe: dekket er hele "
                  "fotavtrykket.",
            ],
            joints={'J18': 8},
        ),
    ]


# ---------------------------------------------------------------------------
# PART MATCHING
# ---------------------------------------------------------------------------
def _match(spec, label):
    if spec.endswith("*"):
        return label.startswith(spec[:-1])
    return label == spec


def resolve_steps(G, steps):
    """Attach the concrete part labels to every step and check the cover."""
    universe = (list(G.parts) + [G.panel_bed] + list(G.battens_bed)
                + list(G.FOOTREST_PARTS)
                + [G.mattress] + list(G.CUSHIONS_BED))
    by_label = {p.label: p for p in universe}
    taken = {}
    for st in steps:
        labels = []
        for spec in st["parts"]:
            hit = [lbl for lbl in by_label if _match(spec, lbl)]
            assert hit, f"step {st['n']}: '{spec}' matches no part"
            for lbl in hit:
                assert lbl not in taken, \
                    f"'{lbl}' is claimed by step {taken[lbl]} and {st['n']}"
                taken[lbl] = st["n"]
            labels += hit
        st["labels"] = sorted(labels)
        hl = st.get("highlight", st["parts"])
        hlabels = []
        for spec in hl:
            hlabels += [lbl for lbl in by_label if _match(spec, lbl)]
        st["highlight_labels"] = sorted(set(hlabels))
    missing = sorted(set(by_label) - set(taken))
    assert not missing, f"no build step places: {missing}"
    return steps


# ---------------------------------------------------------------------------
# X12 - C9 ON THE ASSEMBLIES, NOT JUST ON THE STICKS
# ---------------------------------------------------------------------------
# C9 in the model asks one question of every PIECE of wood: can a member this
# long be got into a WALL_SPAN opening? It is the right question and it was
# being asked of the wrong things. Nobody carries a stick into this niche and
# screws it to the wall on its own - the builder screws five pieces together
# on the floor and then has to get THAT into place, and until the review
# nothing measured it. The 1990 mm back frame passed every assert in the file
# while the prose told the reader to slide it in sideways through a 1990 mm
# gap.
#
# WHAT A BODY IS, DERIVED. A step lists the parts it adds and the joints it
# drives. Two of its parts are one body exactly when a joint OF THAT STEP
# fastens them to each other: screw them together and what you lift is the
# sum. So the bodies of a step are the connected components of that graph,
# and a part nothing in the step joins to is a body of one - which is C9 as it
# always was. Nothing here is a list of steps that happen to build frames:
# move a joint into another step and the bodies move with it.
#
# THE RULE, ON EVERY BODY:
#
#   1. It has to fit between the walls at all             w <= WALL_SPAN
#   2. Tipped upright about its bottom edge, its far
#      corner has to pass under the ceiling               sweep <= ROOM_H
#   3. If it is wider than a member may be long, it
#      cannot be swung in through the opening: it must
#      be BUILT WHERE IT STANDS and raised on the spot.   w > THROUGH_LEN
#      Then the steps have to say so - there has to be a
#      step that raises it and adds nothing - and the
#      niche has to be deep enough to hold it lying down.
#
# The back frame is not a case in that list. It is what rule 3 CATCHES, and
# the check below asserts that the body rule 3 finds is the same five pieces
# the prose calls the back frame. The day a second body goes over 1984, this
# stops the build and asks for the second raising step in words.
UNIT_TOL = 0.5


def step_units(G, steps):
    """{step number: [unit, ...]} - the bodies each step hands the builder."""
    by_label = {p.label: p for p in G.CUT_PARTS}
    out = {}
    for st in steps:
        labels = [l for l in st["labels"] if l in by_label]
        parent = {l: l for l in labels}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for f in G.FASTENER_SPECS:
            if f["jid"] not in st["joints"]:
                continue
            pa, pb = f.get("pa"), f.get("pb")
            if pa is None or pb is None:
                continue
            if pa.label in parent and pb.label in parent:
                ra, rb = find(pa.label), find(pb.label)
                if ra != rb:
                    parent[ra] = rb
        groups = {}
        for l in labels:
            groups.setdefault(find(l), []).append(l)
        out[st["n"]] = sorted(
            (unit_envelope(G, [by_label[l] for l in g]) for g in groups.values()),
            key=lambda u: u["labels"])
    return out


def raising_steps(G, steps, unit):
    """The steps that MOVE this body without adding anything to it.

    A step with no parts of its own re-highlights what it works on (the
    `highlight` field exists for exactly that), so the ink says which body it
    takes hold of. That is the declaration the rule needs: a body too wide to
    be carried in has to have one of these after the step that builds it.
    """
    return [st["n"] for st in steps
            if not st["labels"] and st["highlight_labels"]
            and set(st["highlight_labels"]) <= set(unit["labels"])]


def check_step_units(G, steps):
    """The manoeuvring rule, run on every body every step makes."""
    units = step_units(G, steps)
    in_place = []
    for st in steps:
        for u in units[st["n"]]:
            assert u["w"] <= G.WALL_SPAN + UNIT_TOL, (
                f"steg {st['n']}: enheten {u['labels']} er {_fmt(u['w'])} mm "
                f"bred og nisja er {G.WALL_SPAN} - den får ikke plass mellom "
                f"veggene i det hele tatt")
            assert u["sweep"] <= G.ROOM_H, (
                f"steg {st['n']}: enheten {u['labels']} er {_fmt(u['h'])} × "
                f"{_fmt(u['t'])} mm og sveiper {u['sweep']:.0f} mm når den "
                f"tippes opp om underkanten - taket er på {G.ROOM_H}")
            if u["w"] <= G.THROUGH_LEN + UNIT_TOL:
                continue
            # Rule 3: too wide to be swung in. It is built where it stands.
            raisers = raising_steps(G, steps, u)
            assert raisers, (
                f"steg {st['n']}: enheten {u['labels']} er {_fmt(u['w'])} mm "
                f"bred - mer enn {G.THROUGH_LEN}, så den lar seg ikke svinge "
                f"inn i en {G.WALL_SPAN} mm åpning. Den må bygges der den "
                f"skal stå og reises på stedet, og da må et senere steg gjøre "
                f"nettopp det: et steg uten egne deler som merker av denne "
                f"enheten. Det finnes ikke")
            in_place.append((st["n"], raisers, u))
    # THE BACK FRAME IS RULE 3'S OUTCOME, and this is where that is said out
    # loud rather than assumed. One body in this bed cannot be carried in; the
    # prose calls it the back frame and prints its numbers, so the two have to
    # be the same body measured once.
    assert len(in_place) == 1, (
        "X12: " + str(len(in_place)) + " enheter må bygges på plass - "
        + "; ".join(f"steg {n}: {u['labels']}" for n, _r, u in in_place)
        + ". Prosaen i «Før steg 0» og i steg 1/2 beskriver ÉN slik enhet. "
          "Blir det flere, må teksten si det - tallene kan ikke bare "
          "regnes om")
    _n, _raisers, u = in_place[0]
    bf = back_frame(G)
    assert u["labels"] == bf["labels"], (
        f"X12: enheten som må bygges på plass er {u['labels']}, og prosaen "
        f"kaller bakrammen {bf['labels']} - BACK_FRAME_PARTS og steg "
        f"{_n} har gått fra hverandre")
    assert u["need"] <= bf["need"] + UNIT_TOL, "X12: back frame need drifted"
    _all = [v for vs in units.values() for v in vs]
    _carried = max(v["w"] for v in _all if v["w"] <= G.THROUGH_LEN + UNIT_TOL)
    _sweep = max(v["sweep"] for v in _all)
    _built = len([s for s in steps if s["labels"]])
    _rz = ", ".join(str(r) for r in _raisers)
    print(f"  X12 manøvrerbarhet: {len(_all)} enheter i {_built} steg målt "
          f"som kropper, ikke som pinner. Bredeste som kan bæres inn: "
          f"{_fmt(_carried)} mm (grense {G.THROUGH_LEN}); høyeste sveip "
          f"{_sweep:.0f} mm (tak {G.ROOM_H}). Steg {_n} bygger den ene som "
          f"IKKE kan bæres inn - {_fmt(u['w'])} mm bred, {u['n']} deler - og "
          f"steg {_rz} reiser den: sveip {u['sweep']:.0f} mm, og den krever "
          f"{_fmt(u['need'])} mm nisjedybde liggende")
    return units


def SOFT_BUY(G, label):
    """The shopping line for a part that is foam: the reference mattress and
    the four cushions. They have no cut-list key because nothing is sawn."""
    if label.startswith("Mattress"):
        return (f"Madrass 80 × 200 cm, **{G.MATTRESS_H} mm tykk** "
                f"(vindu {G.MATTRESS_H_MIN:.0f}–{G.MATTRESS_H_MAX:.0f} mm)",
                "", "")
    if label.startswith("Seat Cushion"):
        return (f"Benkepute, skum **{G.CUSHION_T} mm** "
                f"({G.SEAT_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} mm, hakk "
                f"{G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} i veggkanten)",
                "", "")
    return (f"Ryggpute, skum **{G.CUSHION_T} mm** "
            f"({G.BACK_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} mm)", "", "")


def step_part_rows(G, st, cut_index):
    """[(antall, navn, dimensjon, lengde), ...] for the labels this step adds.

    `dimensjon` and `lengde` are empty strings for the reference mattress,
    which is bought rather than cut.
    """
    counts = {}
    for lbl in st["labels"]:
        key = cut_index.get(lbl)
        if key is None:                       # bought as foam, not cut as wood
            key = SOFT_BUY(G, lbl)
        counts[key] = counts.get(key, 0) + 1
    return [(qty, name, section, _fmt(length) if section else "")
            for (name, section, length), qty in sorted(counts.items())]


def step_part_summary(G, st, cut_index):
    """['2× Endebjelke 36×98 × 836', ...] for the labels this step adds."""
    out = []
    for qty, name, section, length in step_part_rows(G, st, cut_index):
        out.append(f"{qty}× {name} {section} × {length}" if section
                   else f"{qty}× {name}")
    return out


# ---------------------------------------------------------------------------
# CUT LIST
# ---------------------------------------------------------------------------
# The English cut-list names live in generate_loftbed.py (they are part of the
# model's own output). The documentation is Norwegian, so the names are mapped
# here - one place, and asserted complete.
NO_NAMES = {
    "Upper side rail": "Sidevange, øvre",
    "End beam": "Endebjelke",
    "Corner post, back (W2, wall side)": "Hjørnestolpe, bak (veggside)",
    "Corner post, front": "Hjørnestolpe, front",
    "Ladder upright (D13)": "Stigevange",
    "Ladder rung (tread)": "Rungetrinn",
    "Ladder rung block": "Stigekloss",
    "Bench rail, back (C5)": "Benkevange, bak (gjennomgående)",
    "Bench rail, front segment (D13)": "Benkevange, front (bit)",
    "Bench stub leg (W3)": "Stubbefot",
    "Bench slat (C3)": "Benkespile",
    "Bench end slat (V13)": "Endespile",
    "Bench end cleat (V13)": "Endelist",
    "Upper bed slat, short (D5/W4)": "Køyespile, kort (mot bakre stolpe)",
    "Upper bed slat, to the wall (W4)": "Køyespile, lang (inn til veggen)",
    "Upper bed slat": "Køyespile",
    "Upper bed slat (D5)": "Køyespile",
    "Guard rail, front segment (D2/D7/D13)": "Rekkverksbord, front",
    "Table ledger, back": "Bordbærelekt, bak",
    "Movable panel": "Løs plate",
    "Panel stiffener batten (M4)": "Avstivningslekt under plate",
    "Panel front cross batten (M5)": "Kilelekt under platens forkant (skråkappet)",
    "Footrest cheek (X14)": "Fotbrettgavl",
    "Footrest deck board (X14)": "Fotbrettbord",
}


# The model gives every piece a cut-list line but does not record which part
# belongs to which line. This is that mapping, by label prefix, longest first.
# It is checked against CUT_LIST below: if the model ever grows, loses or
# renames a part, the assert in `part_cut_keys` fires.
LABEL_TO_CUT = [
    ("Upper Side Rail", "Upper side rail"),
    ("End Beam", "End beam"),
    ("Corner Post Back", "Corner post, back (W2, wall side)"),
    ("Corner Post Front", "Corner post, front"),
    ("Ladder Upright", "Ladder upright (D13)"),
    ("Rung Block", "Ladder rung block"),
    ("Ladder Rung_", "Ladder rung (tread)"),
    ("Bench Rail Back", "Bench rail, back (C5)"),
    ("Bench Rail Front", "Bench rail, front segment (D13)"),
    ("Bench Stub Leg", "Bench stub leg (W3)"),
    ("Bench Slat", "Bench slat (C3)"),
    ("Bench End Slat", "Bench end slat (V13)"),
    ("Bench End Cleat", "Bench end cleat (V13)"),
    ("Guard Rail Front", "Guard rail, front segment (D2/D7/D13)"),
    ("Table Ledger Back", "Table ledger, back"),
    ("Movable Panel", "Movable panel"),
    ("Panel Stiffener Batten", "Panel stiffener batten (M4)"),
    ("Panel Front Batten", "Panel front cross batten (M5)"),
    ("Footrest Cheek", "Footrest cheek (X14)"),
    ("Footrest Deck Board", "Footrest deck board (X14)"),
]


def part_cut_keys(G):
    """label -> the CUT_LIST key that part was counted into.

    The upper slats are the one family with two lines, and which line a slat
    gets is decided by its own length - the same rule the model uses.
    """
    by_name = {}
    for key in G.CUT_LIST:
        by_name.setdefault(key[0], []).append(key)
    for name, keys in by_name.items():
        assert len(keys) == 1, f"cut-list name '{name}' has {len(keys)} lines"

    out = {}
    for p in (list(G.parts) + [G.panel_bed] + list(G.battens_bed)
              + list(G.FOOTREST_PARTS)):
        if p.label.startswith("Bed Slat_"):
            # The upper slats are the one family the model has sometimes split
            # into two cut-list lines (different lengths). Pick by length if
            # there are two, and just take the one line if there is only one.
            slat_lines = sorted(n for n in by_name if "bed slat" in n.lower())
            assert slat_lines, "no upper-slat line in the cut list"
            if len(slat_lines) == 1:
                name = slat_lines[0]
            else:
                (_, _), (y0, y1), _ = p.extents
                length = round(y1 - y0)
                cand = [n for n in slat_lines if by_name[n][0][2] == length]
                assert len(cand) == 1, \
                    f"'{p.label}' is {length} mm and matches {cand}"
                name = cand[0]
        else:
            name = next((cut for pre, cut in LABEL_TO_CUT
                         if p.label.startswith(pre)), None)
            assert name is not None, f"no cut-list line known for '{p.label}'"
        out[p.label] = by_name[name][0]
        # The model now writes the line onto the piece as it makes it, so the
        # prefix table above has something to be checked AGAINST rather than
        # merely asserted for completeness.
        assert p.cut == out[p.label], \
            f"LABEL_TO_CUT puts '{p.label}' in {out[p.label]}, the model put " \
            f"it in {p.cut}"

    counted = {}
    for key in out.values():
        counted[key] = counted.get(key, 0) + 1
    assert counted == dict(G.CUT_LIST), (
        "the label -> cut-list mapping disagrees with the model's own cut "
        "list; the model changed and LABEL_TO_CUT has not:\n"
        f"  mapping: {sorted(counted.items())}\n"
        f"  model:   {sorted(G.CUT_LIST.items())}")
    return out


def cut_table(G):
    """[(no_name, section, length, qty, (xr, yr, zr), en, fit), ...].

    `fit` is the model's room-fit verdict for the whole line - None for a
    piece the workshop finishes, otherwise ("gulv"|"gulv+side"|"vegg"|
    "meddrag", overmål).
    The verdict is a rule in generate_loftbed.py; nothing here decides it.
    """
    keys = part_cut_keys(G)
    spans = {}
    for p in (list(G.parts) + [G.panel_bed] + list(G.battens_bed)
              + list(G.FOOTREST_PARTS)):
        key = keys[p.label]
        (x0, x1), (y0, y1), (z0, z1) = p.extents
        cur = spans.setdefault(key, [[], [], []])
        cur[0].append((x0, x1))
        cur[1].append((y0, y1))
        cur[2].append((z0, z1))
    rows = []
    for (name, section, length), qty in G.CUT_LIST.items():
        assert name in NO_NAMES, f"cut-list name '{name}' has no Norwegian name"
        rows.append((NO_NAMES[name], _no_section(G, section), length, qty,
                     spans[(name, section, length)], name,
                     G.ROOM_LINES.get((name, section, length))))
    rows.sort(key=lambda r: (r[1], -r[2], r[0]))
    return rows


def cut_index(G):
    """label -> (norwegian name, section, length)."""
    idx = {}
    for label, (name, section, length) in part_cut_keys(G).items():
        idx[label] = (NO_NAMES[name], _no_section(G, section), length)
    return idx


# ---------------------------------------------------------------------------
# BUYING LIST - first-fit-decreasing into sale lengths
# ---------------------------------------------------------------------------
# A piece is (name, finished length, OVERLENGTH). The third number is what
# the ROOM adds to the piece and the shop still has to saw off the board: a
# post that stands on the floor is cut 15 mm long and trimmed on site, and
# those 15 mm are wood, kerf and floor sweepings, not a rounding error. The
# packer therefore packs `fin + over` and reports `used` the same way - what
# comes off the board is what the board loses.
def _sawn(p):
    """What a piece actually takes out of a board."""
    return p[1] + p[2]


def pack(pieces, lengths=None):
    """First-fit-decreasing bin packing into the sale lengths of one profile.

    Boards are opened at the longest sale length and shrunk afterwards to the
    shortest one that still holds what they were given, which is what you
    would do at the counter - unless the profile only comes in one length, in
    which case there is nothing to shrink to.

    Every length in here is the SAWN length, finished plus the room's
    overlength. A cutting plan drawn on nominal lengths promises board that
    the saw has already eaten.
    """
    lengths = lengths or SALE_LENGTHS
    boards = []
    for piece in sorted(pieces, key=lambda p: -_sawn(p)):
        for b in boards:
            used = sum(_sawn(x) for x in b) + KERF * len(b)
            if used + _sawn(piece) <= max(lengths):
                b.append(piece)
                break
        else:
            assert _sawn(piece) <= max(lengths), \
                f"'{piece[0]}' is {_sawn(piece)} mm sawn - longer than any " \
                f"sale length"
            boards.append([piece])
    out = []
    for b in boards:
        need = sum(_sawn(x) for x in b) + KERF * (len(b) - 1)
        buy = min(s for s in lengths if s >= need)
        out.append(dict(buy=buy, pieces=b, used=sum(_sawn(x) for x in b),
                        rest=buy - need))
    out.sort(key=lambda b: (-b["buy"], -len(b["pieces"])))
    return out


def buy_table(G):
    rows = cut_table(G)
    by_section = {}
    for no_name, section, length, qty, _spans, _en, fit in rows:
        # fit[1] is the model's own total allowance for the line - one foot
        # trimmed, or one or two wall ends fine-cut. Nothing is decided here.
        over = fit[1] if fit else 0
        by_section.setdefault(section, []).extend(
            [(no_name, length, over)] * qty)
    # X5: THE JIGS ARE PIECES THE BOARD HAS TO HOLD. A shop aid is not part of
    # the bed - not in `parts`, not in the cut list, not in the piece count -
    # but it IS wood you have to saw off a board of that profile, and the
    # shopping list is the one place where that distinction does not matter.
    # Until v14 they were left out of the packing and the list claimed
    # afterwards that they came off the offcut pile; that claim held only as
    # long as some board happened to have 812 mm of rest lying about, and X2's
    # fifth rung and X3's taller stub legs ate it. So they are packed with
    # everything else now and the plan shows them by name: one rule - anything
    # the saw has to cut is something the counter has to sell - instead of a
    # claim that has to come out true again every round.
    for _aid in G.SHOP_AIDS:
        _sect = _aid["section"].replace("x", "×")
        if _sect not in by_section:
            continue
        _nm = _aid["name"].split(" —")[0]
        by_section[_sect].extend([(_nm, _aid["length"], 0)] * _aid["qty"])
    out = []
    for section, pieces in sorted(by_section.items()):
        if "plate" in section or "panel" in section:   # sheet, not a stick
            out.append(dict(section=section, sheet=True, pieces=pieces))
            continue
        sale = SALE_LENGTHS_BY_SECTION.get(section)
        boards = pack(pieces, sale)
        # THE CLAIM THE LIST MAKES OUT LOUD - "du trenger ikke kjøpe mer
        # virke for det" - measured instead of hoped for: pack the same
        # pieces at their nominal lengths and demand the same shopping.
        nominal = pack([(n, ln, 0) for n, ln, _o in pieces], sale)
        assert sorted(b["buy"] for b in boards) == \
            sorted(b["buy"] for b in nominal), (
                f"{section}: med overmålet pakket blir handlelista "
                f"{sorted(b['buy'] for b in boards)} mot "
                f"{sorted(b['buy'] for b in nominal)} uten - "
                "innkjøpslista kan ikke lenger si at overmålet er gratis")
        bought = sum(b["buy"] for b in boards)
        used = sum(b["used"] for b in boards)
        out.append(dict(section=section, sheet=False, boards=boards,
                        bought=bought, used=used,
                        waste=100.0 * (bought - used) / bought))
    return out


# ---------------------------------------------------------------------------
# WRITERS
# ---------------------------------------------------------------------------
HEAD = ("<!-- GENERERT AV generate_loftbed.py / tools/gen_doc_tables.py.\n"
        "     IKKE REDIGER FOR HÅND - kjør `mise run build`. -->\n\n")


def write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"  wrote {path}")


# WHAT THE ROOM FINISHES, IN WORDS. The kind and the millimetres come out of
# generate_loftbed.py; this only puts them in Norwegian. Nothing here decides
# how much - `over` is the model's own allowance for that line.
def _fit_text(G, fit):
    kind, over, ends = fit
    if kind == "gulv":
        return f"**+{over}** — trimmes i bunn"
    if kind == "gulv+side":
        return (f"**+{over}** — trimmes i bunn · siden mot veggen strekes "
                "opp ved bul")
    if kind == "vegg":
        hvor = "i hver ende" if ends == 2 else "i veggenden"
        return f"**+{over // ends}** {hvor} — finkappes"
    return "nominell — bredden strekes opp"


LOOSE_MARK = "(løs del)"


def loose_lines(G):
    """The cut-list lines whose pieces are LOOSE - furniture inside the
    furniture. The model's own LOOSE_PARTS, and the reason a piece can stand
    on the floor and still be finished on the bench: nobody screws it down,
    so nothing has to be scribed to a floor that is out of level."""
    return {p.cut[0] for p in G.LOOSE_PARTS if p.cut is not None}


def _cut_rows(G, L, rows):
    """One position table. Returns the number of pieces it printed."""
    L.append("| Del | Dim. | Lengde | Ant. | X | Y | Z |\n")
    L.append("|---|---|---:|---:|---|---|---|\n")
    n = 0
    loose = loose_lines(G)
    for no_name, section, length, qty, sp, en, _fit in rows:
        n += qty
        # X14: a loose piece that STANDS ON THE FLOOR is the one row in this
        # table whose position contradicts the rule the table is split by, so
        # the row says why out loud - and the ink assert below reads the same
        # words rather than being told about the exception in code.
        touches = (min(a for a, _b in sp[0]) <= G.ROOM_TOL
                   or max(b for _a, b in sp[0]) >= G.WALL_SPAN - G.ROOM_TOL
                   or min(a for a, _b in sp[2]) == 0)
        mark = f" {LOOSE_MARK}" if en in loose and touches else ""
        L.append(f"| {no_name}{mark} | {section} | **{_fmt(length)}** | {qty} | "
                 f"{_axis(sp[0])} | {_axis(sp[1])} | {_axis(sp[2])} |\n")
    return n


def _room_rows(G, L, rows):
    L.append("| Del | Dim. | Lengde | Ant. | Kapp på stedet | X | Y | Z |\n")
    L.append("|---|---|---:|---:|---|---|---|---|\n")
    n = 0
    for no_name, section, length, qty, sp, _en, fit in rows:
        n += qty
        L.append(f"| {no_name} | {section} | **{_fmt(length)}** | {qty} | "
                 f"{_fit_text(G, fit)} | "
                 f"{_axis(sp[0])} | {_axis(sp[1])} | {_axis(sp[2])} |\n")
    return n


# THE ASSERT THAT READS THE INK. The split into two tables is a rule in the
# model, and a rule can be printed wrong. So the finished file is read back
# and every row is checked against the POSITION PRINTED IN THE SAME ROW: a
# part under «kapp på stedet» has to show an X that reaches a wall or a Z
# that starts on the floor, and a part under «kapp nå» has to show neither.
# The side-scribing sentence is checked the same way: only a row whose own Z
# says it stands on the floor over its whole sawn length, AND whose own X
# reaches an end wall, may carry it - because that combination is the one
# that meets the wall with a side. Nothing here repeats a length or a name.
def _assert_kappliste_ink(G, text):
    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]

    def span(cell):
        lo, hi = cell.replace(" (fordelt)", "").split("..")
        return float(lo.replace(",", ".")), float(hi.replace(",", "."))

    tables = {}
    head = None
    for line in text.split("\n"):
        if line.startswith("## "):
            head = line[3:].strip()
            tables.setdefault(head, [])
        elif line.startswith("| ") and head in tables:
            c = cells(line)
            if c[0] in ("Del", "---") or set(c[0]) <= set("-:"):
                continue
            tables[head].append(c)

    shop = next(v for k, v in tables.items() if k.startswith("Kapp nå —"))
    room = next(v for k, v in tables.items() if k.startswith("Kapp når rommet"))
    assert shop and room, "one of the two cut tables came out empty"

    n_side = 0
    for c in shop + room:
        is_room = len(c) == 8
        x0, x1 = span(c[-3])
        z0, z1 = span(c[-1])
        at_wall = x0 <= G.ROOM_TOL or x1 >= G.WALL_SPAN - G.ROOM_TOL
        touches = at_wall or z0 == 0
        # X14: unless the row itself says it is a loose piece - then it stands
        # on the floor and is still the workshop's, and the row has to say so.
        if LOOSE_MARK in c[0]:
            assert not is_room and z0 == 0 and not at_wall, (
                f"«{c[0]}» er merket {LOOSE_MARK}, men står ikke bare på "
                f"gulvet: X {c[-3]}, Z {c[-1]}")
            continue
        assert touches == is_room, (
            f"«{c[0]}» står under «{'kapp på stedet' if is_room else 'kapp nå'}»"
            f", men posisjonen i samme rad sier X {c[-3]}, Z {c[-1]}")
        if is_room:
            allowed = {f"+{G.ROOM_OVER_FLOOR}", f"+{G.ROOM_OVER_WALL}"}
            assert (any(a in c[4] for a in allowed)
                    or "nominell" in c[4]), \
                f"«{c[0]}» har overmålet «{c[4]}», som ikke er en av " \
                f"modellens: {sorted(allowed)} eller nominell lengde"
            length = float(c[2].strip("*").replace(",", "."))
            stands = z0 == 0 and abs(z1 - z0 - length) < 0.5
            side = "siden mot veggen" in c[4]
            assert side == (stands and at_wall), (
                f"«{c[0]}» {'sier' if side else 'sier ikke'} at siden mot "
                f"veggen strekes opp, men raden selv sier lengde {c[2]}, "
                f"X {c[-3]}, Z {c[-1]}")
            n_side += int(side)

    want_side = sum(1 for f in G.ROOM_LINES.values() if f[0] == "gulv+side")
    assert n_side == want_side, \
        f"{n_side} rader streker opp siden mot veggen, mot {want_side} " \
        f"«gulv+side»-linjer i modellen"

    assert len(shop) + len(room) == len(G.CUT_LIST), \
        f"{len(shop)} + {len(room)} rader mot {len(G.CUT_LIST)} linjer i " \
        "modellens kappliste"
    assert len(room) == len(G.ROOM_LINES), \
        f"{len(room)} romdel-rader mot {len(G.ROOM_LINES)} romdel-linjer i " \
        "modellen"


def emit_kappliste(G, out_dir):
    rows = cut_table(G)
    shop = [r for r in rows if r[6] is None]
    room = [r for r in rows if r[6] is not None]
    L = [HEAD, "# Kappliste\n\n",
         "Alle mål i mm. Alle kutt er 90° på to nær — se merknaden "
         "under tabellene. Posisjonen er delens plass i "
         f"modellen: X langs veggen (0 = venstre vegg, {G.WALL_SPAN} = høyre "
         f"vegg), Y i dybden ({_fmt(G.WALL_Y)} = bakveggen), Z opp fra "
         "gulvet.\n\n",
         "Lista står i to bolker, og skillet er en regel: **en del som "
         f"kommer nærmere enn {_fmt(G.ROOM_TOL)} mm fra en endevegg, eller "
         "som står på gulvet, får sluttmålet sitt av rommet — ikke av "
         "modellen.** Rommet er hverken i vinkel eller i vater. Resten "
         "kappes ferdig på bukken.\n\n",
         "Mål rommet før du kapper romdelene: se "
         "[byggesteg](byggesteg.md#før-steg-0--mål-rommet).\n\n"]

    L.append("## Kapp nå — verksteddeler\n\n")
    n_shop = _cut_rows(G, L, shop)
    L.append(f"\n**{n_shop} deler.** Rommet bestemmer ingen mål på disse. "
             "Kapp dem ferdig med én gang.\n\n")

    L.append(f"## {KAPP_ROOM_HEAD}\n\n")
    n_room = _room_rows(G, L, room)
    L.append(f"\n**{n_room} deler.** Kapp dem med overmålet i kolonnen "
             "«Kapp på stedet», og finkapp på stedet:\n\n")
    L.append(f"* **Står på gulvet:** kapp {G.ROOM_OVER_FLOOR} mm for lang. "
             "Gulvet legges først. Så trimmes foten til rammen står i "
             "vater. Strek opp med avstandskloss — meddrag.\n")
    L.append("* **Står på gulvet inntil endevegg — hjørnestolpene:** samme "
             "trimming i bunn, og i tillegg strekes siden. Stolpen står "
             "helt inntil veggen uten klaring, så en bul i veggen må tas i "
             "treet: hold stolpen i lodd på plass, strek opp veggsiden med "
             "avstandskloss og høvle av til den står i lodd inntil veggen. "
             "Ikke legg på noe i bredden — den nominelle dimensjonen står, "
             "det er bare bulen som går av.\n")
    L.append(f"* **Går fra vegg til vegg:** kapp {G.ROOM_OVER_WALL} mm for "
             "lang i hver ende som møter vegg. Finkapp etter målt "
             "nisjebredde.\n")
    L.append("* **Bredden mot veggen:** kappes på nominell lengde. Det er "
             "BREDDEN som tilpasses, ikke lengden — ytterkanten strekes opp "
             "etter veggen så fugen blir jevn.\n\n")
    L.append("Kapp kanter som møter vegg eller gulv med lite bakfall. Da er "
             "det bare den synlige kanten som bestemmer fugen.\n\n")

    total = n_shop + n_room
    L.append(f"**{total} deler i alt.**\n\n")
    L.append("«(fordelt)» betyr at delene i den raden står på flere "
             "posisjoner langs den aksen; kolonnen viser da hele området de "
             "dekker. Nøyaktige posisjoner står i "
             "[nøkkelmål](nokkelmal.md).\n\n")
    # V4: THE TWO CUTS THAT ARE NOT 90 DEGREES, named where the "alle kutt er
    # 90°" line is, so the two do not have to be reconciled by the reader.
    L.append("**Ett unntak fra «alle kutt er 90°»:** de to kilelektene under "
             "platens forkant. De sages i ett rett snitt fra full "
             f"{G.NOSE_ROOT_H} mm ved roten — enden som støter mot "
             f"styrelekta — ned til {G.NOSE_TIP_H} mm ved tuppen på platens "
             "ytterkant, altså "
             + f"{G.NOSE_TAPER_DEG:.1f}".replace(".", ",")
             + "° på langs. Overkanten, "
             "den som limes mot plata, blir stående urørt i hele lengden. "
             "Håndsag eller båndsag; se steg 0 og J13b.\n\n")

    # SHOP AIDS: cut, but not built in. They are not parts, so they are not in
    # the count above and not in parts.tsv - and they are here rather than in
    # a note somewhere because a jig you were never told to make is a jig you
    # do not have when you need it.
    L.append("## Hjelpedeler — kappes, men bygges ikke inn\n\n")
    L.append("| Del | Dim. | Lengde | Ant. | Kapp | Brukes til |\n")
    L.append("|---|---|---:|---:|---|---|\n")
    for aid in G.SHOP_AIDS:
        L.append(f"| {aid['name']} | "
                 f"{aid['section'].replace('x', '×')} | "
                 f"**{_fmt(aid['length'])}** | {aid['qty']} | "
                 f"{aid['cut']} | {aid['use']} |\n")
    # X5: they are not PARTS, but they are wood, and since v14 the buying list
    # packs them like everything else. Saying "de kappes av restene" was true
    # only while some board happened to have room; now the plan has a line for
    # each of them and the sentence says where to look.
    L.append("\nDisse er ikke med i de "
             f"{total} delene over — de er ikke deler i senga, de er verktøy "
             "du sager i steg 0. Virket til dem er likevel med i "
             "[innkjøpslista](innkjopsliste.md): de står i kappeplanen for "
             "sin egen dimensjon, som alt annet du må sage.\n\n")

    by_section = {}
    for no_name, section, length, qty, _sp, _en, _fit in rows:
        by_section[section] = by_section.get(section, 0) + qty
    L.append("Fordelt på dimensjon: "
             + " · ".join(f"**{s}** {n} stk."
                          for s, n in sorted(by_section.items(),
                                             key=lambda kv: -kv[1]))
             + "\n\n")
    board = G.sec(G.BOARD36_T, G.BOARD36_W).replace("x", "×")
    lens = {}
    for no_name, section, length, qty, _sp, _en, _fit in rows:
        if section == board:
            lens[length] = lens.get(length, 0) + qty
    L.append("Sagstopp for hovedbordet " + board + ": "
             + " · ".join(f"**{qty} stk. à {_fmt(ln)}**"
                          for ln, qty in sorted(lens.items(), reverse=True))
             + f" — {len(lens)} innstilling"
             + ("er" if len(lens) != 1 else "")
             + " på sagen, ikke én per del.\n")
    text = "".join(L)
    _assert_kappliste_ink(G, text)
    write(os.path.join(out_dir, "kappliste.md"), text)


def emit_innkjopsliste(G, out_dir):
    tab = buy_table(G)
    # ROMDELENE KAPPES FOR LANGE, og kappeplanen under er PAKKET med
    # overmålet: en romdel spiser lengde + overmål av bordet sitt, fordi det
    # er det sagen gjør. Resten i tabellen er derfor allerede resten ETTER at
    # overmålet er tatt, og at det likevel ikke koster ett bord mer er
    # asserten i buy_table().

    L = [HEAD, "# Innkjøpsliste — trevirke\n\n",
         "Høvlet konstruksjonsvirke C24 der ikke annet er nevnt. "
         f"Kappingen under er regnet med {KERF} mm sagsnitt mellom hvert "
         "kutt, og hvert bord er valgt som den korteste salgslengden som "
         "rommer det som skal kappes av det — blant de lengdene dimensjonen "
         "faktisk selges i. Se merknadene nederst.\n\n",
         "Romdelene kappes for lange og finkappes i rommet — se "
         "[kapplista](kappliste.md). Overmålet er regnet inn i kappeplanen "
         "under, og står som **+ tall** etter lengden: det er tre som går av "
         "bordet. Det koster likevel ikke ett bord mer — det går av resten, "
         "og det er en assert.\n\n"]

    L.append("## Kort handleliste\n\n| Dimensjon | Kjøp | Svinn |\n")
    L.append("|---|---|---:|\n")
    for e in tab:
        if e["sheet"]:
            L.append(f"| **{e['section']}** | 1 plate 18 mm kryssfiner furu, "
                     f"minst {G.PANEL_W} × {G.PANEL_LEN} mm. "
                     f"**Legg dekkfineren langs de {G.PANEL_W} mm** "
                     f"(sengens lengderetning): platas styrende arkrad "
                     f"spenner den veien. Det er en MARGIN og ikke lenger et "
                     f"krav — raden holder "
                     + f"{G.PANEL_EDGE_UTIL_CROSS:.2f}".replace(".", ",")
                     + f" også snudd — men det "
                     f"koster ingenting, så legg den riktig vei. Se X16 "
                     f"| — |\n")
            continue
        counts = {}
        for b in e["boards"]:
            counts[b["buy"]] = counts.get(b["buy"], 0) + 1
        buy = " + ".join(
            "**{} stk. {} m**".format(n, f"{ln / 1000:.1f}".replace(".", ","))
            for ln, n in sorted(counts.items(), reverse=True))
        L.append(f"| **{e['section']}** | {buy} | {e['waste']:.0f} % |\n")
    L.append("\n")

    L.append("## Kappeplan, bord for bord\n\n")
    for e in tab:
        if e["sheet"]:
            L.append(f"### {e['section']}\n\nÉn plate. "
                     f"{len(e['pieces'])} del(er) kappes av den.\n\n")
            continue
        L.append(f"### {e['section']}\n\n")
        L.append("Kjøpt {} m, brukt {} m, svinn {:.0f} %.\n\n".format(
            f"{e['bought'] / 1000:.2f}".replace(".", ","),
            f"{e['used'] / 1000:.2f}".replace(".", ","), e["waste"]))
        L.append("| Bord | Kjøpelengde | Kappes til | Rest |\n")
        L.append("|---:|---:|---|---:|\n")
        for i, b in enumerate(e["boards"], 1):
            per = {}
            for name, ln, ov in b["pieces"]:
                per[(name, ln, ov)] = per.get((name, ln, ov), 0) + 1
            txt = " + ".join(
                f"{q} × {_fmt(ln)}" + (f" + {_fmt(ov)}" if ov else "")
                + f" ({name})"
                for (name, ln, ov), q in sorted(per.items()))
            # THE ASSERT THAT READS THE PACKED INK: the row's own numbers have
            # to add up on the row. Everything sawn off this board, kerf
            # between each cut, plus the rest printed beside it, is the board
            # that was bought - overlength included, because the overlength is
            # in the pieces now.
            sawn = sum(ln + ov for _n, ln, ov in b["pieces"])
            cuts = KERF * (len(b["pieces"]) - 1)
            assert abs(sawn + cuts + b["rest"] - b["buy"]) < 0.5, (
                f"bord {i} av {e['section']}: {_fmt(sawn)} kappet + "
                f"{_fmt(cuts)} sagsnitt + {_fmt(b['rest'])} rest er ikke "
                f"{_fmt(b['buy'])} kjøpt")
            L.append(f"| {i} | {_fmt(b['buy'])} | {txt} | "
                     f"{_fmt(b['rest'])} |\n")
        L.append("\n")
        # SHOP AIDS ARE IN THE PLAN ABOVE (X5), not in a footnote hoping for a
        # rest to turn up. What is checked here is that they really are: every
        # jig piece of this profile has to appear on one of the boards, by
        # name and in the right number, or the paragraph below is describing a
        # cutting plan that does not contain it.
        mine = [a for a in G.SHOP_AIDS
                if a["section"] == e["section"].replace("×", "x")]
        if mine:
            planned = [nm for bb in e["boards"]
                       for nm, _ln, _ov in bb["pieces"]]
            need = sum(a["length"] * a["qty"] for a in mine) \
                + KERF * (sum(a["qty"] for a in mine) - 1)
            for a in mine:
                nm = a["name"].split(" —")[0]
                assert planned.count(nm) == a["qty"], (
                    f"the shop aids on {e['section']}: the cutting plan has "
                    f"{planned.count(nm)} x '{nm}' and the manual asks for "
                    f"{a['qty']} - a jig you were never given board for is a "
                    f"jig you do not have when you need it")
            L.append("Hjelpedelene på denne dimensjonen — "
                     + " + ".join(
                         f"{a['qty']} × {_fmt(a['length'])} mm "
                         f"({a['name'].split(' —')[0]})" for a in mine)
                     + f", til sammen {_fmt(need)} mm med sagsnitt — står i "
                     f"kappeplanen over. De er ikke deler i senga, men de er "
                     f"virke du må sage, og da er de kjøpt inn som alt annet. "
                     f"Se [kapplista](kappliste.md).\n\n")

    # MYKT. The mattress and the four cushions are the only things on the
    # shopping list that are not timber, and they were the only things not on
    # it at all - the reader had to find them in ASSEMBLY §5. They belong here,
    # in their own section, so that one list is the whole trip.
    L.append("## Mykt — kjøpes, ikke kappes\n\n")
    L.append("Ikke trelast, men det står på samme handletur. Skum kjøpes som "
             "plate eller som ferdig skummadrass og kappes med brødkniv eller "
             "elektrisk kniv.\n\n")
    L.append("| Hva | Mål | Ant. | Merknad |\n|---|---|---:|---|\n")
    L.append(f"| Madrass, overkøye | 80 × 200 cm, **{G.MATTRESS_H} mm tykk** "
             f"| 1 | Vindu {G.MATTRESS_H_MIN:.0f}–{G.MATTRESS_H_MAX:.0f} mm. "
             f"Hyllevarene over vinduet — "
             + ", ".join(f"{t}" for t in (140, 150, 160)
                         if t > G.MATTRESS_H_MAX)
             + f" mm — er ULOVLIGE her. Se nøkkelmål |\n")
    L.append(f"| **Benkepute**, underetasjen | "
             f"**{G.SEAT_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} × "
             f"{G.CUSHION_T} mm** | 2 | Hakk {G.CUSHION_NOTCH[0]} × "
             f"{G.CUSHION_NOTCH[1]} mm i veggkanten, der den bakre "
             f"hjørnestolpen står |\n")
    L.append(f"| **Ryggpute**, underetasjen | "
             f"**{G.BACK_CUSHION_LEN} × {G.LOWER_SLEEP_DEPTH} × "
             f"{G.CUSHION_T} mm** | 2 | Rene rektangler |\n")
    L.append(f"| Trekk | — | 5 | Skum uten trekk smuldrer. Regn det som en "
             f"egen post |\n\n")
    L.append(f"**De fire putene er én skumplate.** "
             f"{G.SEAT_CUSHION_LEN} + {G.BACK_CUSHION_LEN} + "
             f"{G.BACK_CUSHION_LEN} + {G.SEAT_CUSHION_LEN} = "
             f"{G.LOWER_SLEEP_LEN} mm, og dybden er {G.LOWER_SLEEP_DEPTH} mm "
             f"— altså nøyaktig en 80 × 200 skumplate med "
             f"{G.CUSHION_SHEET_WASTE} mm til overs på lengden. Kjøp én "
             f"plate, kapp fire ganger. Samme regnestykke gjelder om du "
             f"heller kjøper en billig skummadrass 80 × 200 og deler den.\n\n")
    L.append("## Merknader fra butikken\n\n")
    board = G.sec(G.BOARD36_T, G.BOARD36_W).replace("x", "×")
    slat = G.sec(G.BOARD23_T, G.BOARD36_W).replace("x", "×")
    # Antallet er utledet, ikke telt for hånd: 14 køyespiler + 2 x 5
    # benkespiler + 2 endespiler = 26 stykker  [var 24, før endespilene].
    # 24 av dem er den SAMME 800 mm biten; endespilene er kortere fordi den
    # bakre stolpen står i veien for dem.
    n_same = G.SLAT_COUNT + 2 * G.BENCH_SLAT_COUNT
    n_slat = n_same + len(G.END_SLAT_X)
    L.append(f"* **{slat}** er det største bordet i denne sengen i antall og "
             f"lengde — de {n_slat} spilene er kappet av det: {G.SLAT_COUNT} "
             f"køyespiler og {2 * G.BENCH_SLAT_COUNT} benkespiler à "
             f"{_fmt(G.SLAT_LEN)} mm, pluss {len(G.END_SLAT_X)} endespiler à "
             f"{_fmt(G.END_SLAT_LEN)} mm. "
             f"**{board}** tar resten av det flate virket: stolper, "
             f"rekkverksbord og endebjelker. Ring og bestill før du drar; "
             f"butikken har sjelden nok av én dimensjon på lager. Får du ikke "
             f"akkurat disse målene, kan modellen kjøres om på en "
             f"nabodimensjon — det er én konstant i `generate_loftbed.py` — "
             f"men da må hele kapplista og alle nøkkelmål regnes på nytt. Ikke "
             f"improviser på sagbenken.\n")
    L.append(f"* **Kjøp ett bord {slat} ekstra.** Planen over bruker fem, og "
             f"fem er nok. Spilene er den ene delen det er {n_same} HELT LIKE "
             f"av — {_fmt(G.SLAT_LEN)} mm, ett saganslag — og et "
             f"reservebord koster mindre enn en ny tur.\n")
    only = ", ".join(
        f"**{s}** finnes bare i "
        + " / ".join(f"{ln / 1000:.1f}".replace(".", ",") + " m"
                     for ln in sorted(lns))
        for s, lns in sorted(SALE_LENGTHS_BY_SECTION.items()))
    L.append(f"* Salgslengder: {only}. Kappeplanen over er derfor lagt på den "
             f"lengden alene — de kortere salgslengdene finnes ikke i denne "
             f"dimensjonen, og et bord du ikke kan kjøpe er ingen plan.\n")
    # U5: the two lekt dimensions are named off the model, not typed in, so a
    # profile that leaves the bed leaves this sentence too. 48×48 used to be a
    # third one here, with an "unless you can only get klasse 1" escape for the
    # four stub legs; the legs are cut from the 48×73 bench-rail board now, and
    # that board also holds the load-bearing rungs, so there is no escape left
    # and none is needed.
    lekt = " og ".join(x.replace("x", "×") for x in (
        G.sec(G.BLOCK_T, G.BLOCK_H), G.sec(G.BENCH_RAIL_T, G.BENCH_RAIL_H)))
    L.append(f"* **Alt konstruksjonsvirke kjøpes som C24** (styrkesortert), "
             f"også lektdimensjonene {lekt}. Står de i hylla bare som "
             f"«klasse 1 lekt/rekke — ikke-bærende», så spør i skranken: "
             f"stigevangene, rungetrinnene og stubbeføttene er alle bærende, "
             f"og lasttabellen regner C24.\n")
    L.append(f"* Platen er **{G.PANEL_W} mm bred** og kappes av **18 mm "
             f"kryssfiner**. "
             + (f"Merk at *begrunnelsen* er en annen enn før: fram til K2 var "
                f"platen 652 mm bred, altså bredere enn de "
                f"{G.LIMTRE_SHELF_W} mm limtre furu stopper på i hylla, og "
                f"kryssfiner var det eneste som fantes i den bredden. "
                f"{G.PANEL_W} går inn i en {G.LIMTRE_SHELF_W} mm limtreplate. "
                f"Materialet står likevel — lasttabellen, uttrekket for "
                f"oppskruene og propp-argumentet i J13 er alle regnet på "
                f"kryssfiner — men det er et **valg** nå og ikke en tvang. "
                f"Ført opp som åpent punkt, ikke stilltiende endret.\n"
                if G.PANEL_FITS_LIMTRE else
                f"Limtre furu i butikkhylla stopper på "
                f"{G.LIMTRE_SHELF_W} mm.\n"))
    L.append(f"* Vil du kunne bygge om til frittstående seng senere, trengs "
             f"to rekkverksbord til i samme dimensjon som de fremre, og to "
             f"bakre stolper i full høyde ({G.POST_HEIGHT} mm, som de "
             f"fremre). Kjøp dem gjerne nå, og forbor de bakre stolpene for "
             f"rekkverket mens de ligger på bukken.\n")
    write(os.path.join(out_dir, "innkjopsliste.md"), "".join(L))


def emit_nokkelmal(G, out_dir, rows):
    L = [HEAD, "# Nøkkelmål\n\n",
         "Alle mål i mm. X går langs rommet mellom de to veggene, Y i "
         "dybden med bakveggen på "
         f"{_fmt(G.WALL_Y)}, Z opp fra gulvet.\n\n"]

    L.append("## Ytre mål\n\n| | Mål |\n|---|---:|\n")
    L.append(f"| Bredde, vegg til vegg | {G.WALL_SPAN} |\n")
    L.append(f"| Dybde over alt | {G.OVERALL_DEPTH} |\n")
    L.append(f"| Høyde foran (stolpetopp) | {G.POST_HEIGHT} |\n")
    L.append(f"| Høyde ved veggen (bakre stolpe) | {G.BACK_POST_HEIGHT} |\n")
    # X1: the room is a parameter now, and the two head rooms are what the
    # whole round is about - they belong in the first table a reader meets.
    L.append(f"| **Takhøyde i rommet senga er regnet for** | "
             f"**{G.ROOM_H}** |\n")
    L.append(f"| Klaring over høyeste del | {G.CEILING_CLEAR} |\n")
    L.append(f"| **Fri høyde under senga (gulv til spilenes underside)** | "
             f"**{G.SLAT_Z0}** |\n")
    L.append(f"| Fri høyde over øvre madrass | {G.UPPER_SIT_HEADROOM} |\n")
    L.append(f"| Gjennomgående deler kappes til | {G.THROUGH_LEN} "
             f"(X {G.THROUGH_X0}..{G.THROUGH_X1}) |\n")
    L.append(f"| Klaring til hver vegg for disse | {G.THROUGH_X0} |\n\n")
    L.append(f"En {G.WALL_SPAN} mm lang del lar seg ikke svinge inn i en "
             f"{G.WALL_SPAN} mm åpning. Derfor er hver gjennomgående del "
             f"{G.THROUGH_LEN} mm.\n\n")

    L.append("## Høyder (Z)\n\n| Z | Hva |\n|---:|---|\n")
    heights = [
        (0, "gulv"),
        (G.BENCH_RAIL_BOTTOM, "benkevangens underkant / stubbefotens topp"),
        (G.BENCH_RAIL_TOP, "benkevangens overkant = trinn 1 = platens "
                           "underside i sengestilling"),
        (G.PANEL_TOP_BED, "platens overside i sengestilling"),
        (G.BENCH_TOP, "benkeoverflate (sittehøyde uten pute)"),
        (G.CUSHION_TOP_BENCH, "**puteoverflate — nedre soveflate og "
                              "sittehøyde med pute** (V13)"),
        (G.RUNG_TOPS[1], "trinn 2"),
        (G.LEDGER_BACK_Z0, "bordbærelektas underkant"),
        (G.PANEL_UNDER_TABLE - G.RUNG_T, "støttetrinnets underkant"),
        (G.PANEL_UNDER_TABLE, "bordbærelektas og STØTTETRINNETS overkant = "
                              "platens underside i bordstilling (X16: et "
                              "trinn igjen; X9 hadde to bordklosser her)"),
        (G.PANEL_TOP_TABLE, "**bordplate — pulthøyde** (X9)"),
        (G.BACKREST_Z1, "ryggputens topp i sofastilling (V13)"),
        # X2: the rung count is derived now (even_climb), so the landmark
        # rows are too - rungs 1 and 2 have their own lines above because they
        # share a top with something else, and the rest are just steps.
        *((z, f"trinn {i + 1}") for i, z in enumerate(G.RUNG_TOPS) if i >= 2),
        (G.END_BEAM_Z0, "endebjelkens underkant"),
        # X6: the BACK post stops under the back side rail, 635 mm below the
        # front one, and that top is a landmark in its own right - it is the
        # height the back frame is built to and the datum every hole in a back
        # post is measured down from. It used to be printed on the slat-bottom
        # row, which is a different height altogether.
        (G.BACK_POST_HEIGHT, "**bakre stolpetopp**"),
        (G.RAIL_BOTTOM, "endebjelkens overkant = sidevangens underkant "
                        "(fri høyde under sengen)"),
        (G.RAIL_TOP, "sidevangens overkant"),
        (G.SLAT_Z1, "spilebunn / madrassens underside"),
        (G.MATTRESS_Z1, "madrassens overside (ved "
                        f"{G.MATTRESS_H} mm madrass; lovlig band "
                        f"{G.MATTRESS_H_MIN}–{G.MATTRESS_H_MAX})"),
        (G.GUARD_BAND_Z0[0], "rekkverk, nedre bånd underkant"),
        (G.GUARD_BAND_Z0[0] + G.GUARD_W, "rekkverk, nedre bånd overkant"),
        (G.GUARD_BAND_Z0[1], "rekkverk, øvre bånd underkant"),
        (G.GUARD_BAND_Z0[1] + G.GUARD_W, "rekkverk, øvre bånd overkant"),
        (G.POST_HEIGHT, "fremre stolpetopp"),
    ]
    # TWO LANDMARKS AT ONE HEIGHT ARE ONE ROW. The back post top and the side
    # rail's underside are the same Z, and printing them as two rows with the
    # same number in the left column would ask the reader to decide which one
    # the height belongs to. They are merged in the order they are named
    # above, so the row reads as one fact seen from several parts.
    merged = {}
    for z, what in heights:
        merged.setdefault(round(z, 3), []).append(what)
    for z in sorted(merged):
        L.append(f"| **{_fmt(z)}** | {' = '.join(merged[z])} |\n")

    climb = [0] + list(G.RUNG_TOPS) + [G.SLAT_Z1]
    steps = [b - a for a, b in zip(climb, climb[1:])]
    L.append(f"\nStigningen fra gulv til spilebunn: "
             + " + ".join(_fmt(s) for s in steps)
             + f" mm. Første stigning er benkevangens høyde — det er en "
               f"avsats du trår opp på, ikke et klatretrinn. De "
               f"{len(steps) - 1} klatretrinnene er {_fmt(min(steps[1:]))}–"
               f"{_fmt(max(steps[1:]))} mm.\n\n")

    L.append("## Dybdeplan (Y)\n\n| Y | Hva |\n|---:|---|\n")
    planes = [
        (G.WALL_Y, "BAKVEGGEN — monteringsflaten. Bakre stolper, "
                   "endebjelkeender og bakre stubbeføtter ligger i dette "
                   "planet. Ingenting får stikke bak det."),
        (G.BACK_RAIL_Y0, "bakre sidevange, benkevange, bordbærelekt og "
                         "spilebunn — bakkant; bakre stolpes forside"),
        # Bordbærelekta er 48 dyp som benkevangen, ikke en 21 mm bordkant:
        # forsiden ligger i BACK_RAIL_Y1 og har ingen egen rad. (Den hadde en
        # rad regnet med BOARD_T her, og den ga et Y-plan som ikke finnes.)
        (G.BACK_RAIL_Y1, "bakre sidevanges, benkevanges og bordbærelektas "
                         "forside; avstivningslektenes bakkant"),
        (G.RUNG_Y0, "trinnenes bakkant (hylla platen hviler på)"),
        (G.BATTEN_Y1, "platens forkant; avstivningslektenes og kilelektenes "
                      "forkant"),
        (G.FRONT_RAIL_Y0, "fremre sidevange og benkevange — bakkant"),
        (G.FRONT_RAIL_Y1, "fremre sidevanges forside = fremre stolpers og "
                          "stigevangers bakside = spilebunnens forkant"),
        (G.FRONT_POST_Y1, "fremre stolpers og stigevangers forside = "
                          "trinnenes forkant"),
        (G.FRONT_GUARD_Y0, "rekkverksbordenes bakkant"),
        (G.FRONT_GUARD_Y1, "rekkverksbordenes forkant"),
        (G.DEPTH_Y1, "sengens forkant — det ytterste planet"),
    ]
    ext = getattr(G, "SLAT_Y0_EXT", None)
    if ext is not None and ext != G.SLAT_Y0:
        planes.append((ext, "de lange køyespilenes bakkant"))
    merged = {}
    for y, what in planes:
        merged.setdefault(y, [])
        if what not in merged[y]:
            merged[y].append(what)
    for y in sorted(merged):
        L.append(f"| **{_fmt(y)}** | " + "; ".join(merged[y]) + " |\n")
    L.append(f"\nFri bredde mellom de to sidevangene: "
             f"**{G.INNER_CLEAR_WIDTH}**. Spilebunnen fra vange til vange: "
             f"**{G.PLATFORM_DEPTH}** — nøyaktig madrassbredden.\n\n")

    L.append("## Stige, trinn og rekkverk (X)\n\n| | X |\n|---|---|\n")
    L.append(f"| Stigens senterlinje | {G.LADDER_CENTER_X} |\n")
    L.append(f"| Stigevanger | {_rng(G.LADDER_LEFT_X, G.LADDER_LEFT_X + G.UPRIGHT_W)}"
             f" og {_rng(G.LADDER_RIGHT_X, G.LADDER_RIGHT_X + G.UPRIGHT_W)} |\n")
    L.append(f"| Fri åpning mellom stigevangene | **{G.LADDER_CLEAR}** |\n")
    # X2 made the rung COUNT a derivation (even_climb), and this line was
    # still typing 4 - it went on saying four rungs for a whole round after
    # the model built five. Counted off RUNG_TOPS like everything else.
    L.append(f"| Trinn ({len(G.RUNG_TOPS)} stk.) | "
             f"{_rng(G.LADDER_INNER_L, G.LADDER_INNER_R)}"
             f", {G.RUNG_LEN} mm lange |\n")
    L.append(f"| Stigeklosser | {_rng(G.RUNG_BLOCK_X[0], G.RUNG_BLOCK_X[0] + G.RUNG_BLOCK_T)}"
             f" og {_rng(G.RUNG_BLOCK_X[1], G.RUNG_BLOCK_X[1] + G.RUNG_BLOCK_T)} |\n")
    L.append(f"| Rekkverksbord | {_rng(*G.FRONT_GUARD_SEGMENTS[0])} og "
             f"{_rng(*G.FRONT_GUARD_SEGMENTS[1])} |\n")
    L.append(f"| Klatreåpning i begge rekkverksbånd | **{G.LADDER_CLEAR}** |\n")
    L.append(f"| Benkene | {_rng(G.BENCH_X[0], G.BENCH_X[0] + G.BENCH_LEN)} og "
             f"{_rng(G.BENCH_X[1], G.BENCH_X[1] + G.BENCH_LEN)} |\n")
    L.append(f"| Åpent gulv mellom benkene | {_rng(*G.OPEN_FLOOR_X)} "
             f"({G.OPEN_FLOOR_X[1] - G.OPEN_FLOOR_X[0]} mm) |\n")
    L.append(f"| Gangpassasje ved siden av stigen | "
             f"{_fmt(G.LADDER_LEFT_X - G.OPEN_FLOOR_X[0])} mm på hver side |\n")
    L.append(f"| Stubbeføtter | {_rng(G.STUB_LEG_X[0], G.STUB_LEG_X[0] + G.LEG_W)}"
             f" og {_rng(G.STUB_LEG_X[1], G.STUB_LEG_X[1] + G.LEG_W)} |\n")
    L.append(f"| Løs plate | {_rng(G.PANEL_X0, G.PANEL_X1)} "
             f"({G.PANEL_W} mm bred) |\n")
    L.append(f"| Avstivningslekter (styrer platen) | "
             f"{_rng(G.BATTEN_X[0], G.BATTEN_X[0] + G.BATTEN_W)}"
             f" og {_rng(G.BATTEN_X[1], G.BATTEN_X[1] + G.BATTEN_W)} |\n")
    L.append(f"| Kilelekter under forkanten | "
             f"{_rng(*G.NOSE_X[0])} og {_rng(*G.NOSE_X[1])} |\n")
    L.append(f"| Klaring lekt → trinnende | {G.PANEL_FIT} mm hver vei "
             f"(trinnendene står på X {G.LADDER_INNER_L} og "
             f"{G.LADDER_INNER_R} i begge stillinger) |\n\n")

    # K2: the width windows. This is the one number in the bed that looks like
    # a free choice and is not, so the table is emitted from the same lists the
    # assert uses - it cannot say something the build would let through.
    L.append("### Platebredden er kvantisert — lovlige vinduer\n\n")
    L.append(f"Åpningen mellom benkene er fast, **{G.PANEL_OPENING} mm**, så "
             f"sideklaringen er `({G.PANEL_OPENING} − bredde) / 2` på hver "
             f"side. EN 747 gjør bare tre klaringsbånd lovlige — under "
             f"{_fmt(G.EN_FINGER_FREE)} mm kommer ikke fingeren inn, "
             f"{_fmt(G.EN_GAP_BAND[0])}–{_fmt(G.EN_GAP_BAND[1])} mm går den "
             f"fritt gjennom, {_fmt(G.EN_LIMB_BAND[0])}–"
             f"{_fmt(G.EN_LIMB_BAND[1])} mm går hele lemmet fritt og "
             f"åpningen er fortsatt under EN 747s egen 75 mm-grense — og "
             f"mellom båndene kiler fingeren seg. Bredden er derfor ikke en "
             f"skrue man vrir på: den lander i ett av tre vinduer, eller så "
             f"er den ulovlig.\n\n")
    L.append("| Klaringsbånd | Lovlig platebredde | |\n|---|---|---|\n")
    _rowsw = sorted(zip(G.PANEL_WIDTH_WINDOWS,
                        sorted(G.EN_LEGAL_GAP_BANDS, reverse=True)))
    for (wlo, whi), (glo, ghi) in _rowsw:
        if wlo <= G.PANEL_W <= whi:
            note = f"**valgt — {G.PANEL_W} mm, {G.PANEL_SIDE_GAP} mm klaring**"
        elif wlo <= 652 <= whi:
            note = "tidligere vindu (652 mm)"
        elif glo == 0:
            note = f"upraktisk — spiser opp de {G.PANEL_FIT} mm innsettingsklaring"
        else:
            note = ""
        L.append(f"| {_fmt(glo)}–{_fmt(ghi)} mm | "
                 f"{_fmt(wlo)}–{_fmt(whi)} mm | {note} |\n")
    for flo, fhi in G.PANEL_WIDTH_FORBIDDEN:
        L.append(f"| — | **{_fmt(flo)}–{_fmt(fhi)} mm** | **forbudt** — "
                 f"klaringer {_fmt((G.PANEL_OPENING - fhi) / 2)}–"
                 f"{_fmt((G.PANEL_OPENING - flo) / 2)} mm, midt i klembåndet |\n")
    L.append(f"\nBredden deltar **ikke** i begrensningene på stillingsbyttet — "
             f"det er høyden og dybden på plateenheten som møter "
             f"overføringssjakten ({G.TRANSFER_SLOT} mm fri høyde mot en "
             f"{G.PANEL_UNIT_H} mm høy enhet). Å smalne platen gir mer slingring "
             f"ved innsettingen og mindre bordflate, ingenting annet. "
             f"Modellen asserter vinduene: en «bare litt smalere»-endring "
             f"stopper byggeporten med akkurat denne tabellen.\n\n")

    slat_pitch = (G.SLAT_X_END - G.SLAT_X_START - G.BED_SLAT_W) / (G.SLAT_COUNT - 1)
    L.append(f"**Køyespiler:** {G.SLAT_COUNT} stk., første spile starter på "
             f"X {G.SLAT_X_START}, deling {_fmt(slat_pitch)} mm, siste spile "
             f"slutter på X {G.SLAT_X_END}. Åpning mellom spilene "
             f"{_fmt(slat_pitch - G.BED_SLAT_W)} mm.\n\n")
    L.append(f"**Benkespiler:** {G.BENCH_SLAT_COUNT} per benk, deling "
             f"{_fmt(G.BENCH_SLAT_PITCH)} mm, felt X {G.BENCH_SLAT_X_START}.."
             f"{G.BENCH_LEN} (speilvendt på den andre benken).\n\n")
    L.append(f"**Endespiler (V13):** 1 per benk, {G.END_SLAT_LEN} mm lang, X "
             f"{G.END_SLAT_X[0]}..{G.END_SLAT_X[0] + G.BENCH_SLAT_W} og "
             f"{G.END_SLAT_X[1]}..{G.WALL_SPAN}, Y {G.END_SLAT_Y0}.."
             f"{G.END_SLAT_Y1}. Den er kortere fordi den starter på den bakre "
             f"hjørnestolpens forside, og den lukker feltet helt ut til "
             f"veggen — spalten inn til første benkespile er "
             f"{G.END_SLAT_GAP} mm. Uten den stopper soveflaten nede "
             f"{G.BENCH_SLAT_W} mm fra veggen i hver ende. Endelisten under "
             f"den er {G.END_CLEAT_T}×{G.END_CLEAT_H} × {G.END_CLEAT_LEN} mm, "
             f"skrudd på stolpens forside (J17).\n\n")

    L.append("## Skruerader i rammeleddene\n\n")
    L.append(f"Ingen bolt går inn i en stolpe. Stolpen er {G.POST_T} mm tykk, "
             f"og på den tykkelsen har en M8 ikke nok kantavstand; en {SCREW_D} "
             f"mm treskrue har akkurat nok. To skruer i et ledd står alltid "
             f"symmetrisk om delens midtlinje. Skruetyper og antall står i "
             f"[beslaglista](beslagliste.md).\n\n")
    L.append("| Ledd | Skruer | Z | Kantavstand | Avstand mellom | I planet |\n")
    L.append("|---|---:|---|---|---:|---|\n")
    where = {"J1": "Y " + " og ".join(_fmt(v) for v in rows["J1"]["y"])
                   + " (midt i stolpedybden)",
             "J2": f"X {_fmt(rows['J2']['x'])} fra hver vegg",
             "J8": f"X {_fmt(rows['J8']['x'])} fra hver vegg"}
    for j in ("J1", "J2", "J8"):
        r = rows[j]
        L.append(f"| {j} — {r['member']} | {r['count']} per ledd | "
                 + " og ".join(f"**{_fmt(z)}**" for z in r["z"]) + " | "
                 + " / ".join(_fmt(e) for e in r["edge"]) + " | "
                 + (_fmt(r["spacing"]) if r["spacing"] else "—") + " | "
                 + where[j] + " |\n")
    L.append(f"\nMinstekrav for en forboret {SCREW_D} mm treskrue: "
             f"kantavstand {MIN_EDGE} mm (3d), avstand mellom to skruer langs "
             f"fiberretningen {MIN_SPACING_GRAIN} mm (5d). Alle radene over "
             f"holder kravet.\n\n")
    end_d = rows["_rail_end_distance"]
    if end_d < rows["_rail_end_required"]:
        L.append(f"**Ett avvik:** endeavstanden fra vangens ende inn til "
                 f"J2- og J8-skruen blir {_fmt(end_d)} mm, mot minstekravet "
                 f"{rows['_rail_end_required']} mm. Se avviksnotatet i "
                 f"ASSEMBLY.md.\n\n")
    else:
        L.append(f"Endeavstanden fra vangens ende inn til J2- og J8-skruen "
                 f"er {_fmt(end_d)} mm, godt over minstekravet "
                 f"{rows['_rail_end_required']} mm — den brede stolpen ga "
                 f"denne avstanden gratis.\n\n")
    L.append("**Ingen forsenkte boltehoder.** Ingen del av rammen festes "
             "lenger fra en flate som ender mot vegg, så det finnes ikke et "
             "eneste hode som må senkes ned under en monteringsflate. "
             "Skruehoder forsenkes som vanlig der de er i veien for hånda.\n\n")

    L.append("## Madrass og puter\n\n| | Mål |\n|---|---|\n")
    L.append(f"| Madrass, overkøye | **standard 80 × 200 cm.** Sengen er "
             f"dimensjonert rundt den; liggeflaten er {G.WALL_SPAN} × "
             f"{G.MATTRESS_W} mm, så madrassen presses de siste "
             f"{2000 - G.WALL_SPAN} mm inn mellom veggene og fyller bredden "
             f"nøyaktig |\n")
    L.append(f"| **Madrasstykkelse** | **{G.MATTRESS_H_MIN}–"
             f"{G.MATTRESS_H_MAX} mm — kjøp {G.MATTRESS_H} mm.** Åpningen fra "
             f"madrassens overside opp til nedre rekkverksbånd skal ligge i "
             f"EN 747-båndet {G.EN_LIMB_BAND[0]:.0f}–"
             f"{G.MAX_GUARD_OPENING} mm. Tynnere enn {G.MATTRESS_H_MIN} og "
             f"åpningen blir større enn {G.MAX_GUARD_OPENING}; **tykkere enn "
             f"{G.MATTRESS_H_MAX} og den faller ned i klemvinduet under "
             f"{G.EN_LIMB_BAND[0]:.0f} mm**. Hyllevarene over vinduet — "
             + ", ".join(f"{t}" for t in (140, 150, 160)
                         if t > G.MATTRESS_H_MAX)
             + f" mm — er altså ULOVLIGE her, og det er ikke en detalj: det er "
             f"den ene tingen ved denne sengen du må huske i butikken. "
             f"Modellen tegner {G.MATTRESS_H} mm, som gir "
             f"{G.GUARD_BAND_Z0[0] - G.MATTRESS_Z1} mm — midt i båndet |\n")
    L.append(f"| **Maks madrasstykkelse merkes på sengen** | "
             f"{G.MATTRESS_H_MAX} mm. EN 747 krever at maksmålet står "
             f"permanent på sengen. Merk linja "
             f"{G.SLAT_Z1 + G.MATTRESS_H_MAX} mm over gulvet — "
             f"{G.MATTRESS_H_MAX} mm over spilene — på innsiden av en fremre "
             f"stolpe (steg 11) |\n")
    wander = getattr(G, "MATTRESS_WANDER", 0)
    if wander:
        L.append(f"| Madrassens sideveis vandring | {wander} mm mellom "
                 f"veggen og de fremre stolpene |\n")
    else:
        L.append("| Madrassens sideveis vandring | ingen — madrassen fyller "
                 "hele bredden mellom veggen og de fremre stolpene |\n")
    L.append(f"| **Soveflate, underetasjen** | **{G.LOWER_SLEEP_LEN} × "
             f"{G.LOWER_SLEEP_DEPTH} mm** — samme lengde som overkøyen. De to "
             f"bakre hjørnestolpene står i flaten og tar et "
             f"{G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} mm hjørne i hver "
             f"ende; ellers er den hel |\n")
    L.append(f"| **Puter, tykkelse** | **{G.CUSHION_T} mm, alle fire.** Lik "
             f"tykkelse er hele poenget: fire like tykke puter er én seng. "
             f"Sittehøyden blir {G.BENCH_TOP} + {G.CUSHION_T} = "
             f"**{G.CUSHION_TOP_BENCH} mm** |\n")
    L.append(f"| Puter, dybde | {G.LOWER_SLEEP_DEPTH} mm — hele flatens dybde, "
             f"vegg til fremre stolpeplan |\n")
    L.append(f"| **Benkepute (2 stk.)** | **{G.SEAT_CUSHION_LEN} × "
             f"{G.LOWER_SLEEP_DEPTH} × {G.CUSHION_T} mm** — 1/3 av lengden. "
             f"Skjær et {G.CUSHION_NOTCH[0]} × {G.CUSHION_NOTCH[1]} mm hakk i "
             f"veggkanten, der stolpen står |\n")
    L.append(f"| **Ryggpute (2 stk.)** | **{G.BACK_CUSHION_LEN} × "
             f"{G.LOWER_SLEEP_DEPTH} × {G.CUSHION_T} mm** — 1/6 av lengden. "
             f"Rene rektangler |\n")
    L.append(f"| Regnestykket | {G.SEAT_CUSHION_LEN} + {G.BACK_CUSHION_LEN} + "
             f"{G.BACK_CUSHION_LEN} + {G.SEAT_CUSHION_LEN} = "
             f"**{G.LOWER_SLEEP_LEN} mm**. {G.LOWER_SLEEP_LEN} deler seg ikke "
             f"på 6, så tredelen er rundet ned og sjettedelen opp — summen er "
             f"eksakt, og det er summen som må stemme |\n")
    L.append(f"| Alle fire av én skumplate | 80 × 200 cm dekker dem: "
             f"{G.CUSHION_SHEET[0]} mm er nøyaktig dybden og "
             f"{G.CUSHION_SHEET[1]} mm er {G.CUSHION_SHEET_WASTE} mm mer enn "
             f"lengden. Fire tverrkapp |\n")
    L.append(f"| Midtsonen ligger | {G.PANEL_BENCH_DIP} mm lavere enn "
             f"benkene ({G.CUSHION_TOP_PANEL} mot {G.CUSHION_TOP_BENCH} mm). "
             f"Putene er like tykke likevel — skummet tar de "
             f"{G.PANEL_BENCH_DIP} millimeterne, og ingen puteskjøt ligger på "
             f"en sonegrense |\n")
    L.append(f"| Hodehøyde over nedre soveflate | {G.LOWER_HEADROOM} mm til "
             f"køyespilene ({G.LOWER_HEADROOM_RAIL} mm under sidevangene) "
             f"— men det er høyden i det ÅPNE feltet. Målt på kroppene over "
             f"hele soveflatens fotavtrykk er laveste faste del "
             f"«{G.LOWER_HEADROOM_WHO}» på {_fmt(G.LOWER_HEADROOM_MIN)} mm, "
             f"og over putestripa langs veggen er det "
             f"«{G.LOWER_HEADROOM_WALL_WHO}» på "
             f"{_fmt(G.LOWER_HEADROOM_WALL)} mm |\n")
    L.append(f"| Ryggpute i sofastilling | står på høykant ytterst på hver "
             f"benk: {G.CUSHION_T} mm tykk, {G.LOWER_SLEEP_DEPTH} mm dyp, "
             f"{G.BACK_CUSHION_LEN} mm høy, topp {G.BACKREST_Z1} mm. Ryggen "
             f"mot bordbærelekta |\n\n")

    # X8c - KASSEROMMET. Målt på solidene (STORAGE_BAYS i generate_loftbed.py),
    # ikke skrevet inn her: taket er benkevangens underkant, bredden er det de
    # tingene som faktisk står på gulvet lar stå igjen, dybden er benkespilens
    # egen lengde. Avsnittet finnes fordi et rom ingen har målt, er et rom
    # ingen kjøper kasser til.
    _bay_l, _bay_r = G.STORAGE_BAYS
    L.append(f"## Kasserommet under benkene\n\n"
             f"Under hver benk står det et rom som ikke er tegnet inn — det "
             f"er bare det stubbeføttene lar bli igjen — og her er målene på "
             f"det, målt på delene. **Kasser inntil "
             f"{_fmt(G.STORAGE_BAY_H)} × {_fmt(G.STORAGE_BAY_W)} × "
             f"{_fmt(G.STORAGE_BAY_D)} mm (H × B × D) går inn, én på hver "
             f"side.** De skyves rett inn forfra, under benkevangen.\n\n"
             f"| | Mål |\n|---|---:|\n")
    L.append(f"| **Fri høyde** | **{_fmt(G.STORAGE_BAY_H)} mm** — gulv til "
             f"benkevangens underkant |\n")
    L.append(f"| **Fri bredde** | **{_fmt(G.STORAGE_BAY_W)} mm** — fra bakre "
             f"hjørnestolpes innerside til stubbefotens ytterside "
             f"(X {_fmt(_bay_l[1])}–{_fmt(_bay_l[2])} og "
             f"{_fmt(_bay_r[1])}–{_fmt(_bay_r[2])}) |\n")
    L.append(f"| **Fri dybde** | **{_fmt(G.STORAGE_BAY_D)} mm** — veggen til "
             f"fremre benkevanges forside, altså hele benkens dybde. "
             f"Benkevangen henger over kassa, ikke foran den |\n")
    L.append(f"| Antall rom | {len(G.STORAGE_BAYS)} — ett under hver benk. "
             f"Mellom dem er gulvet åpent foran stigen ("
             f"X {_fmt(G.OPEN_FLOOR_X[0])}–{_fmt(G.OPEN_FLOOR_X[1])}), og "
             f"der skal det ikke stå noe |\n")
    L.append(f"| Hva som stjeler resten | de fire stubbeføttene "
             f"({_fmt(G.LEG_W)} mm hver i X, innerst på hver benk) og de to "
             f"bakre hjørnestolpene ({_fmt(G.POST_W)} mm hver, ytterst) |\n")
    L.append(f"| Høyden er et minstemål | gulvet er skjevt og rammen bygges i "
             f"vater fra høyderisset over gulvets HØYESTE punkt, så "
             f"{_fmt(G.STORAGE_BAY_H)} mm er høyden akkurat der — ellers er "
             f"det mer. Mål på stedet før du kapper en kasse i mannshøyde med "
             f"tallet |\n\n")

    # REFERANSEKROPPEN. Tallene under er de eneste i nøkkelmål som er målt på
    # noe annet enn tre: fire barnekropper i modellen, hver bygget av 14
    # primitiver etter AnthroKids og posert i den stillingen raden handler om.
    # Ingen av dem er skrevet inn her - alle kommer ut av modellens egen
    # måleblokk, akkurat som resten av tabellen.
    L.append(f"\n## Referansekroppen — hva sengen er til for\n\n"
             f"Modellen har fire *referansekropper*: et barn på "
             f"**{G.FIGURE_H:.0f} mm** (EN 747 åpner overkøya fra 6 år), "
             f"bygget som én solid av {14} kuler, sylindre og bokser med "
             f"segmentene som brøkdeler av ståhøyden etter **AnthroKids** "
             f"(de digitaliserte Snyder-studiene 1975/1977, "
             f"math.nist.gov/~SRessler/anthrokids/, fri bruk). To ligger i "
             f"sengestilling, to sitter i bordstilling. En kropp er ikke en "
             f"del: den kappes ikke, bærer ingenting, står i ingen liste og "
             f"er tatt ut av alle kontaktsjekker — men den er i parts.tsv og "
             f"i eksportene, og målene under er målt på den.\n\n"
             f"| | Mål |\n|---|---:|\n")
    L.append(f"| **Fri høyde over hodet, sittende** | **{G.SIT_HEADROOM:.0f} "
             f"mm** — kronen står i Z {G.SIT_CROWN_Z:.0f} og "
             f"«{G.SIT_HEAD_OVER}» er det første over. Man sitter helt "
             f"rett opp i sofaen |\n")
    L.append(f"| Sittehøyde | {G.FIG_SITTING_H:.0f} mm (0,545 × H) over "
             f"seteflaten på {G.SEAT_FACE:.0f} mm |\n")
    L.append(f"| **Bordplaten over setet** | **{G.TABLE_OVER_SEAT:.0f} mm**, "
             f"med {G.TABLE_UNDER_SEAT:.0f} mm under seg — et sittende kne "
             f"står {G.FIG_SIT_RISE + G.FIG_THIGH_R:.0f} mm over setet, så "
             f"KNÆRNE går inn under platen med "
             f"{G.TABLE_UNDER_SEAT - G.FIG_SIT_RISE - G.FIG_THIGH_R:.0f} mm "
             f"luft. Det er hele X9-runden: en PULT, ikke et sofabord. Fram "
             f"til v15 lå platen 140 mm over setet med 122 under seg, og 122 "
             f"slipper et lår inn men ikke et kne — derfor satt figurene i "
             f"skredderstilling helt til nå |\n")
    L.append(f"| Nærmeste kropp til platen, sittende | "
             f"{G.LEG_TO_TABLE:.0f} mm |\n")
    L.append(f"| Underarmen over platen | {G.WRIST_OVER_TABLE:.0f} mm — "
             f"barnet legger armene oppå og har albuene i været: "
             f"{G.TABLE_OVER_ELBOW:.0f} mm av platehøyden ligger over albuen "
             f"til et barn på {G.FIGURE_H:.0f} mm. Det er en pulthøyde regnet "
             f"for en stol, brukt fra en sofa — SMÅSTAD-pulten på 730 over "
             f"den 430 mm stolen som selges til den gjør det samme (300 mm) |\n")
    L.append(f"| **Sålene på fotbrettet** | "
             f"**{G.figure_seated_left.extents[2][0]:.0f} mm** over gulvet — "
             f"de HENGER ikke: leggen står i lodd, foten ligger flatt og "
             f"kneet på {G.FOOTREST_KNEE_ANGLE:.0f}°. Til og med X9 hang de "
             f"134 mm i lufta |\n")
    L.append(f"| Fotbrettets høyde | {G.FOOTREST_TOP} mm — utledet, ikke "
             f"valgt: setet bærer låret bare så lenge sålen står mellom "
             f"{G.FOOTREST_MIN:.0f} og {G.FOOTREST_MAX:.0f} mm, og av de "
             f"{len(G.footrest_stacks())} kurvene sengens egne fem "
             f"dimensjoner lager treffer én båndet "
             f"({G.FOOTREST_CHEEK_H} på høykant + {G.FOOTREST_DECK_T} "
             f"flatt) |\n")
    L.append(f"| Fotbrettets plass | X {G.FOOTREST_X0}..{G.FOOTREST_X1} × "
             f"Y {G.FOOTREST_Y0:.0f}.."
             f"{G.FOOTREST_Y0 + G.FOOTREST_DEPTH:.0f} × Z 0..{G.FOOTREST_TOP}"
             f" — bukta mellom de to gangpassasjene, løs, under platen i "
             f"begge stillinger ("
             + " / ".join(f"{g:.0f} mm" for g in G.FOOTREST_AIR.values())
             + " luft) |\n")
    L.append(f"| Låret på puta | barnet står {list(G.FOOTREST_THIGH.values())[0][0]:.1f} mm "
             f"ned i skummet — samme dybde som rumpa selv "
             f"({G.FIG_BUTTOCK_SINK:.1f} mm), og puta bærer låret helt ut "
             f"til sin egen kant på X {G.SEAT_EDGE_X} |\n")
    L.append(f"| **Fri høyde over ansiktet, nede** | "
             f"**{G.LIE_LOWER_FACE:.0f} mm** til køyespilene |\n")
    L.append(f"| Over den som ligger i køya | ingenting — køya er åpen "
             f"oppover. Rekkverket står {G.GUARD_OVER_BODY:.0f} mm over "
             f"kroppens høyeste punkt og {G.GUARD_OVER_FACE:.0f} mm over "
             f"ansiktet |\n")
    L.append(f"| Madrass igjen bak føttene | "
             f"{G.WALL_SPAN - G.figure_lying_upper.extents[0][1]:.0f} mm av "
             f"{G.WALL_SPAN} — plassen å vokse i |\n\n")

    L.append("## Sikkerhetsmål (EN 747)\n\n| | Mål | Krav |\n|---|---:|---:|\n")
    band = f"≤ 5 eller {G.EN_LIMB_BAND[0]:.0f}–{G.MAX_GUARD_OPENING}"
    L.append(f"| Madrassoverside → nedre rekkverksbånd | "
             f"{G.GUARD_BAND_Z0[0] - G.MATTRESS_Z1} | {band} |\n")
    L.append(f"| Mellom de to rekkverksbåndene | "
             f"{G.GUARD_BAND_Z0[1] - (G.GUARD_BAND_Z0[0] + G.GUARD_W)} | "
             f"{band} |\n")
    L.append(f"| Klatreåpningens bredde | {G.LADDER_CLEAR} | "
             f"{G.MIN_LADDER_CLEAR}–{G.MAX_LADDER_CLEAR} |\n")
    L.append(f"| Rekkverkets høyde over madrassen | "
             f"{G.GUARD_BAND_Z0[1] + G.GUARD_W - G.MATTRESS_Z1} | ≥ "
             f"{G.MIN_GUARD_OVER_MATTRESS} |\n")
    gap = getattr(G, "MAX_MATTRESS_GAP", None)
    if gap is not None:
        L.append(f"| Åpning mellom madrass og vegg (verste stilling) | "
                 f"{gap} | ≤ {G.MAX_GUARD_OPENING} |\n")
    L.append(f"| Fri klatreåpning i stigen | {G.LADDER_CLEAR} | ≥ "
             f"{G.MIN_LADDER_CLEAR} |\n")
    L.append(f"| Største klatretrinn | {_fmt(max(steps[1:]))} | ≤ "
             f"{G.MAX_CLIMB_STEP} |\n")
    L.append(f"| Hodehøyde over nedre soveflate | {G.LOWER_HEADROOM} | ≥ "
             f"{G.MIN_SIT_HEADROOM} (én sittehøyde) |\n")
    L.append(f"| — laveste faste del over soveflaten (målt) | "
             f"{_fmt(G.LOWER_HEADROOM_MIN)} ({G.LOWER_HEADROOM_WHO}) | "
             f"ingen grense — det er stigen |\n")
    L.append(f"| — over putestripa ved veggen (målt) | "
             f"{_fmt(G.LOWER_HEADROOM_WALL)} ({G.LOWER_HEADROOM_WALL_WHO}) | "
             f"ingen grense — lekta er permanent |\n")
    L.append(f"| Hodehøyde over øvre madrass | {G.UPPER_SIT_HEADROOM} | ≥ "
             f"{G.MIN_LIE_HEADROOM} (køya er sovesone) |\n")
    write(os.path.join(out_dir, "nokkelmal.md"), "".join(L))


# ---------------------------------------------------------------------------
# BEFORE STEP 0 - the room
# ---------------------------------------------------------------------------
# The bed is cut to a niche this model draws as three perfect planes. The
# house it is going into is being rebuilt, so those planes are about to be
# rebuilt too - and that makes the order of work a fact about the BUILD, not
# advice. This is that order, and every number in it is read off the model:
# the zones off WALL_ZONES, the niche width off WALL_SPAN, the allowances off
# ROOM_OVER_*. The text lives here, once, and is rendered into both
# byggesteg.md and MONTERING.md the way the numbered steps are.
ROOM_TITLE = "Før steg 0 — mål rommet"


NO_WALL_FIX = "— (bare anlegg)"


def _spikerslag_fix(zo):
    """What a nogging zone actually gets, read off the model's own fixings.

    X11: A ZONE IS A BEARING BAND, NOT A SCREW BAND. `WALL_ZONES` is derived
    from the parts that lie flat on the wall or stand in a corner - what the
    bed PRESSES on - and until X11 the table headed that column «del som skal
    ha feste», which promised a fixing in every one of the four. One of the
    four had one. Both facts are worth printing and they are two columns now;
    this one comes from `zo["fix"]`, which generate_loftbed.py fills by
    reading back the placed wall fasteners, so a joint added or removed in the
    model moves this cell and nothing has to be retyped.
    """
    if not zo["fix"]:
        return NO_WALL_FIX
    return " · ".join(f"{jid}, {n} stk." for jid, n in sorted(zo["fix"]))


def spikerslag_rows(G, idx):
    """[(nr, "fra–til", "fra risset", vegg, del, feste), ...] - the noggings
    the wall needs, in both notations: over the finished floor and from the
    height line. The second column is G.riss_span(), i.e. the first one minus
    MEASURE_DATUM_Z - see the X8b block in generate_loftbed.py for why a wall
    cannot be set off a floor nobody trusts. The last one is what the zone
    gets in the way of screws, which is not the same question - see
    `_spikerslag_fix`."""
    out = []
    for i, zo in enumerate(G.WALL_ZONES, 1):
        z0, z1 = zo["z"]
        name = idx[zo["labels"][0]][0]
        n = len(zo["labels"])
        out.append((i, f"{_fmt(z0)}–{_fmt(z1)}", zo["riss_txt"],
                    "Hjørnene, mot endeveggene" if zo["corner"]
                    else "Bakveggen",
                    f"{name}" + (f" ({n} stk.)" if n > 1 else ""),
                    _spikerslag_fix(zo)))
    return out


def spikerslag_table(G, idx):
    L = [f"| Sone | Fra ferdig gulv | Fra høyderisset ({G.MEASURE_DATUM_Z}) | "
         "Vegg | Del som ligger an her | Feste i veggen |\n",
         "|---:|---|---|---|---|---|\n"]
    for nr, z, r, wall, part, fix in spikerslag_rows(G, idx):
        L.append(f"| {nr} | **{z}** | **{r}** | {wall} | {part} | {fix} |\n")
    L.append(f"\nTo notasjoner, samme sone. **Målt fra ferdig gulv** er "
             f"modellens egen Z. **Målt fra høyderisset** er den samme "
             f"høyden minus {G.MEASURE_DATUM_Z} — minus er *under* "
             f"laserlinja, pluss er *over* den. Gulvet er skjevt og risset er "
             f"ikke: står du ved den åpne veggen med målebåndet på laserlinja, "
             f"er det den andre kolonnen du setter sonene etter.\n")
    L.append(f"\n**Spikerslaget skal ligge i alle {len(G.WALL_ZONES)} sonene, "
             f"også der det ikke kommer en skrue.** Kolonnen *Del som ligger "
             f"an her* sier hva sengen presser mot veggen i den høyden — det "
             f"er derfor sonen finnes. Kolonnen *Feste i veggen* sier hva som "
             f"faktisk skrus fast der, og «{NO_WALL_FIX}» betyr at sengen "
             f"bare hviler mot veggen i den sonen. En gipsplate uten tre bak "
             f"gir etter under anlegg også.\n")
    return "".join(L)


def room_first(G):
    """The pre-step, step-shaped: title, intro, do, check."""
    # W1/W7: delene som står BÅDE på gulvet og I veggplanet. De kan ikke
    # holdes ut fra veggen — der er det ingen klaring å ta en fotlist i — så
    # lista utledes her i stedet for å tastes, og kulepunktet under teller den.
    on_floor_and_wall = sorted(
        p.label for p in G.CUT_PARTS
        if abs(p.extents[1][0] - G.WALL_Y) < G.TOL
        and abs(p.extents[2][0]) < G.TOL)
    return dict(
        title=ROOM_TITLE,
        intro="Nisja er hverken i vinkel eller i vater, og senga skal stå i "
              "begge deler. **Senga er referansen, ikke rommet — bygg i "
              "vater og lodd, og ta skjevheten i delene som møter vegg og "
              "gulv.**",
        do=[
            "Vent til vegger og gulv er ferdige. **Mens veggen er åpen: legg "
            "spikerslag i sonene under.** Etterpå kommer du ikke til.",
            f"**Riv fotlist og alt annet listverk langs bakveggen i hele "
            f"nisjas bredde — alle {G.WALL_SPAN} mm — før rammen reises.** "
            f"{len(on_floor_and_wall)} deler står både PÅ gulvet og I "
            f"veggplanet Y {G.WALL_Y}: de to bakre hjørnestolpene og de to "
            f"bakre benkeføttene, og en list under dem skyver hele bakkanten "
            f"ut fra veggen.",
            f"Slå et vannrett høyderiss rundt hele nisja med linjelaser, "
            f"{G.MEASURE_DATUM_Z} mm over ferdig gulv. Alt måles fra risset, "
            "aldri fra gulvet — spikerslagsonene under står i begge "
            "notasjoner, og det er riss-kolonnen du setter dem etter.",
            f"Sett laseren som loddlinje midt i nisja. Mål ut til hver "
            f"endevegg i rutenett: {G.MEASURE_GRID[0]} høyder × "
            f"{G.MEASURE_GRID[1]} dybder på hver vegg. Legg sammen paret i "
            f"hvert punkt. **Minste sum er nisjas minste bredde.**",
            f"**Mål nisjedybden på BEGGE endevegger** — fra bakveggen og ut "
            f"til nisjas åpning, i de samme "
            f"{G.MEASURE_GRID[0]} høydene. Minste dybde må være minst "
            f"**{_fmt(back_frame(G)['need'])} mm**, og det er bakrammen som "
            f"setter kravet, ikke senga: senga er {G.OVERALL_DEPTH} mm dyp, "
            f"men bakrammen bygges liggende på gulvet inne i nisja og tippes "
            f"opp derfra (steg 1 og 2). Liggende tar den sin egen høyde, "
            f"{_fmt(back_frame(G)['h'])} mm, ut fra bakveggen. Er nisja "
            f"grunnere enn det, får rammen ikke ligge — og da lar den seg "
            f"ikke reise heller, for {G.WALL_SPAN} mm bredde går ikke å svinge "
            f"inn i en {G.WALL_SPAN} mm åpning.",
            f"Er minste bredde et annet tall enn {G.WALL_SPAN}: sett den inn "
            "som `WALL_SPAN` i `generate_loftbed.py` og kjør `mise run "
            "build`. Kapplista regner seg om.",
            "Gulv: mål ned fra risset i sengas fire hjørner og på midten. "
            "Merk det høyeste punktet på gulvet. Senga bygges ned fra det.",
            "Kapp verksteddelene nå. Romdelene tilpasses på stedet: stolper "
            f"og føtter kappes {G.ROOM_OVER_FLOOR} mm for lange og trimmes i "
            "bunn til rammen står i vater — strek opp med avstandskloss, "
            f"meddrag. Sidevangene kappes {G.ROOM_OVER_WALL} mm for lange i "
            "hver veggende og finkappes etter målt bredde. Ytterste "
            "endespile strekes opp etter veggen med fast avstand, så fugen "
            "blir jevn.",
            # Denne lista trykkes to steder med hver sin relative sti
            # (byggesteg.md i docs/generated, MONTERING.md i docs), så her
            # står det ingen lenke - bare hvor svaret er.
            f"**Romdelenes hull bores først når romdelen er finkappet.** "
            f"Hvert hull i dem er målt fra den enden som ennå har "
            f"{G.ROOM_OVER_WALL} mm overmål på seg, så rekkefølgen er kapp "
            f"først, drill etterpå. Kapplistas rombolk sier hvilke deler, og "
            f"siste punkt i steg 0 sier hvilke ledd.",
            "**De fire hjørnestolpene står helt inntil endeveggen — null "
            "klaring.** Derfor strekes veggsiden på hver av dem, hver gang: "
            "sett stolpen på plass, hold den i lodd, og strek opp veggsiden "
            "med avstandskloss der veggen buler. Høvle av til stolpen står i "
            "lodd inntil veggen. Ingen monn i bredden — det er tre som skal "
            "bort, ikke legges til. Buler veggen og du lar det stå, skyver "
            "bulen hele rammen ut av lodd.",
            "Kapp kanter som møter vegg eller gulv med lite bakfall. Da er "
            "det bare den synlige kanten som bestemmer fugen.",
        ],
        check=[
            "Høyderisset skal gå hele veien rundt nisja og møte seg selv. "
            "Gjør det ikke det, står laseren feil.",
            f"Er forskjellen mellom minste og største bredde større enn "
            f"{G.ROOM_OVER_WALL} mm, mål om. Kapp uansett etter den minste.",
            f"Nisjedybden skal være minst {_fmt(back_frame(G)['need'])} mm i "
            f"hvert eneste målepunkt på begge endevegger — ikke i snitt. Det "
            f"grunneste punktet er det rammen tar borti når den ligger. "
            f"Kommer du under, må rammen bygges på et annet gulv, og da må "
            f"den bæres inn ferdig reist gjennom en åpning som er nøyaktig "
            f"like bred som den selv. Det går ikke.",
            "Sjekk at spikerslagene ligger i sonene før veggen lukkes — "
            "målt ned eller opp fra høyderisset, ikke opp fra gulvet.",
            f"Bakveggen skal være bar helt ned til gulvet i alle "
            f"{G.WALL_SPAN} mm, ikke bare der de {len(on_floor_and_wall)} "
            f"delene i veggplanet lander. Hold en rett list mot veggen "
            f"nederst: den skal ligge an hele veien.",
            "Hver hjørnestolpe skal stå i lodd begge veier. Vipper den "
            "fordi veggen buler, høvles bulen av — lys i fugen der veggen "
            "viker er greit og skal stå.",
        ],
    )


ROOM_ZONE_NOTE = ("Gulv-kolonnen er fra **ferdig gulv**. Legges gulvet "
                  "etterpå, må påforingshøyden legges til — i begge "
                  "kolonner, for risset slås fra ferdig gulv det også.")


# THE ASSERT THAT READS THE INK. Every height band printed in the nogging
# table has to be the real Z extent of the part named in the same row - not a
# number that once was.
#
# X11: AND THE FIXING COLUMN IS READ THE SAME WAY. The column that used to say
# «del som skal ha feste» was the one thing on this sheet nobody could check,
# because it was a heading and not a measurement - it claimed a fixing for
# four zones and the model placed one in one of them. The claim is a cell now,
# and the cell is read back and counted against the wall fasteners the model
# actually placed in that height band. A joint added to or taken out of
# WALL_FIXINGS moves both, or stops the build.
SPIKERSLAG_COLS = 6


def assert_spikerslag_ink(G, idx, text):
    seen = 0
    for line in text.split("\n"):
        if not line.startswith("| ") or "**" not in line:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) != SPIKERSLAG_COLS:
            continue
        m = re.fullmatch(r"\*\*([\d,]+)–([\d,]+)\*\*", c[1])
        if not m:
            continue
        z0, z1 = (float(v.replace(",", ".")) for v in m.groups())
        # X8b - THE TWO COLUMNS ARE BOUND TOGETHER IN THE INK. The second
        # notation is only usable if it is the first one minus the height
        # line, and this reads both of them back off the printed row and
        # subtracts. A hand-typed riss column, or a datum that moved and took
        # one column with it, stops the build here.
        r = re.fullmatch(r"\*\*([-+]?[\d,]+)\.\.([-+]?[\d,]+) "
                         r"(?:under|over|krysser) risset\*\*", c[2])
        assert r, (f"spikerslagsone {c[0]}: «{c[2]}» er ikke et sonebånd "
                   "målt fra høyderisset")
        r0, r1 = (float(v.replace(",", ".")) for v in r.groups())
        assert z0 - r0 == z1 - r1 == G.MEASURE_DATUM_Z, (
            f"spikerslagsone {c[0]} står på trykk som {c[1]} over ferdig gulv "
            f"og {c[2]}: differansen er {z0 - r0} / {z1 - r1}, og den SKAL "
            f"være høyderisset selv, {G.MEASURE_DATUM_Z}")
        part = re.sub(r" \(\d+ stk\.\)$", "", c[4])
        hits = [p for p in G.CUT_PARTS
                if idx[p.label][0] == part
                and abs(p.extents[2][0] - z0) < 0.05
                and abs(p.extents[2][1] - z1) < 0.05]
        assert hits, (f"spikerslagsone {c[0]} sier {c[1]} for «{part}», men "
                      "ingen del med det navnet står i den høyden")
        # THE FIXING CELL, MEASURED. Every wall fastener the model placed
        # THROUGH one of the pieces this row names is counted, joint by joint,
        # and the cell has to name exactly those joints with exactly those
        # numbers - or say, in so many words, that the zone gets none. It is
        # the PIECE and not the height band that decides: zone 1 is the corner
        # post and runs 0..1402, so it contains every other zone's height, and
        # a band test would credit it with screws that go through somebody
        # else's wood.
        labels = {p.label for p in hits}
        placed = {}
        for f in G.FASTENER_SPECS:
            if not f.get("wall") or f["through"].label not in labels:
                continue
            placed[f["jid"]] = placed.get(f["jid"], 0) + 1
        want = (NO_WALL_FIX if not placed else
                " · ".join(f"{jid}, {n} stk."
                           for jid, n in sorted(placed.items())))
        assert c[5] == want, (
            f"spikerslagsone {c[0]} står på trykk med festet «{c[5]}», men "
            f"modellen har lagt «{want}» i Z {c[1]}")
        seen += 1
    assert seen == len(G.WALL_ZONES), \
        f"{seen} soner på trykk mot {len(G.WALL_ZONES)} i modellen"
    n_ink = sum(1 for line in text.split("\n")
                if line.startswith("| ") and NO_WALL_FIX in line)
    assert n_ink == sum(1 for zo in G.WALL_ZONES if not zo["fix"]), \
        f"{n_ink} soner på trykk uten veggfeste mot " \
        f"{sum(1 for zo in G.WALL_ZONES if not zo['fix'])} i modellen"


# ---------------------------------------------------------------------------
# WHERE THE HOLE GOES ON THE PIECE - the table a man at a trestle can use
# ---------------------------------------------------------------------------
# The model projects every fastener back into the piece it is marked on (see
# X6 in generate_loftbed.py); this puts the projection into Norwegian. Two
# numbers and a pitch per line, and not one of them typed: the words below
# are the only thing this file adds.
#
# The datum names are deliberately NOT «venstre» and «høyre». Along the wall
# a piece has an OUTER end - the one pointing at the nearest side wall - and
# an INNER one, and naming them that way is what lets one line serve a joint
# and its mirror image. The model asserts that the two halves of the bed
# really do project to the same numbers before this prints a word of it.
PLACE_END_NO = {
    (0, "ytre"): "ytterenden", (0, "indre"): "innerenden",
    (1, "bak"): "veggenden", (1, "fram"): "romenden",
    (2, "ned"): "nedre ende", (2, "opp"): "toppen",
}
PLACE_EDGE_NO = {
    (0, "ytre"): "ytterkanten", (0, "indre"): "innerkanten",
    (1, "bak"): "bakkanten", (1, "fram"): "forkanten",
    (2, "ned"): "underkanten", (2, "opp"): "overkanten",
}
PLACE_BOTH_NO = {
    (0, "ende"): "begge ender", (0, "kant"): "begge langkanter",
    (1, "ende"): "vegg- og romenden", (1, "kant"): "bak- og forkanten",
    (2, "ende"): "begge ender", (2, "kant"): "under- og overkanten",
}
PLACE_FACE_NO = {
    (0, "ytre"): "yttersiden (mot sideveggen)",
    (0, "indre"): "innersiden (mot sengas midte)",
    (1, "bak"): "baksiden (mot veggen)",
    (1, "fram"): "forsiden (mot rommet)",
    (2, "ned"): "undersiden", (2, "opp"): "oversiden",
}
# Deterministic order for the datums of one axis - and the order a builder
# reads them in: from the wall out, from the floor up, from the side wall in.
PLACE_AXIS_ORDER = {0: ("ytre", "midt", "indre"), 1: ("bak", "midt", "fram"),
                    2: ("ned", "midt", "opp")}


def _place_one_datum(a):
    """(datum, [mm, ...]) - a row that has a pitch is ONE row, so it is said
    from ONE end, not half from each. The datum is the nearest one; the far
    figures are turned round on the piece's own width."""
    best = min(r["at"][0] for r in a["refs"])
    target = next(n for n in PLACE_AXIS_ORDER[a["axis"]]
                  if any(r["ref"] == n and abs(r["at"][0] - best) < 1e-9
                         for r in a["refs"]))
    vals = set()
    for r in a["refs"]:
        for v in r["at"]:
            vals.add(round(v if r["ref"] == target
                           else (a["width"] / 2 if r["ref"] == "midt"
                                 else a["width"] - v), 1))
    return target, sorted(vals)


def _place_ref(axis, role, ref, at):
    where = (PLACE_END_NO if role == "ende" else PLACE_EDGE_NO)[(axis, ref)]
    if at == [0]:
        return f"i flukt med {where}"      # a bracket corner, not a hole
    return f"{' / '.join(_fmt(v) for v in at)} mm fra {where}"


def _place_cell(a):
    """One axis of one placement line, as a measurement and nothing else."""
    axis, role, refs = a["axis"], a["role"], a["refs"]
    if a["both"]:
        txt = (f"{' / '.join(_fmt(v) for v in refs[0]['at'])} mm fra "
               f"{PLACE_BOTH_NO[(axis, role)]}")
    elif len(refs) == 1 and refs[0]["ref"] == "midt":
        side = "ende" if role == "ende" else "side"
        txt = f"midt på ({_fmt(refs[0]['at'][0])} mm fra hver {side})"
    elif len(refs) > 1 and a["cc"] is not None:
        target, vals = _place_one_datum(a)
        txt = _place_ref(axis, role, target, vals)
    elif len(refs) > 1:
        order = PLACE_AXIS_ORDER[axis]
        txt = " · ".join(
            (f"midt på ({_fmt(r['at'][0])} mm fra hver side)"
             if r["ref"] == "midt" else _place_ref(axis, role, r["ref"],
                                                   r["at"]))
            for r in sorted(refs, key=lambda r: order.index(r["ref"])))
    else:
        txt = _place_ref(axis, role, refs[0]["ref"], refs[0]["at"])
    return txt


def wall_fix_placement_rows(G, st):
    """The wall fixings, in the same five columns as everything else.

    THEY ARE THE ONE ROW THAT CANNOT CARRY AN X MEASUREMENT. Every other
    fastener in the bed sits where the wood says; these sit where the STUDS
    say, and the studs are not in the model - they are in the room. So the
    line gives the height, the diameter and the RULE, and the pitch column
    carries the spacing the model reckons the strength on.
    """
    out = []
    for w in wall_fix_lines(G, jids=set(st["joints"])):
        piece = (f"{w['member']} {w['section']} × {_fmt(w['piece_len'])}, "
                 f"{PLACE_FACE_NO[w['face']]}")
        if abs(w["below"] - w["above"]) < 0.51:
            kant = (f"midt på ({_fmt(w['below'])} mm fra hver side) = "
                    f"{_fmt(w['z'])} mm over gulvet")
        else:
            near = "ned" if w["below"] <= w["above"] else "opp"
            kant = (f"{_fmt(min(w['below'], w['above']))} mm fra "
                    f"{PLACE_EDGE_NO[(2, near)]} = {_fmt(w['z'])} mm over "
                    f"gulvet")
        out.append((f"**{w['jid']}** {w['per']}× {_fast_short(w['name'])}",
                    piece,
                    "etter stender — minst i begge ender og på midten",
                    kant, f"≈ {_fmt(round(w['cc']))}"))
    return out


def wall_fix_note(G, st):
    """The paragraph under a step that fastens the bed to the wall."""
    ws = wall_fix_lines(G, jids=set(st["joints"]))
    if not ws:
        return ""
    n = sum(w["n"] for w in ws)
    return (
        f"**Veggfestene har ingen X-mål, og hullene kan ikke bores i steg 0.** "
        f"Stenderne finnes bare i rommet, og de står der de står — du finner "
        f"dem først når rammen er oppe. Regelen er derfor **et feste i hver "
        f"stender du treffer, og minst i begge ender og på midten** av delen. "
        f"**Tallet i c/c-kolonnen er veiledende.** Modellen har ingen vegg og "
        f"vet ikke hvor stenderne står; den regner styrken på en jevn deling, "
        f"og det er den verste fordelingen du kan treffe mens du følger "
        f"regelen over: "
        + " · ".join(f"{w['jid']} {w['n']} stk. på {_fmt(w['piece_len'])} mm, "
                     f"{_fmt(round(w['inset']))} mm inn fra hver ytterende"
                     for w in ws)
        + f". Tettere stendere gir sterkere feste, ikke svakere; færre enn "
        f"{n} fester i alt er for få. Boring: "
        + " · ".join(f"{w['jid']} {w['drill']}" for w in ws) + ".\n")


def placement_rows(G, st, idx):
    """[(ledd, merkes-opp-på, fra enden, fra kanten, c/c)] for one step."""
    out = []
    for pl in G.FASTENER_PLACEMENTS:
        if pl["jid"] not in st["joints"]:
            continue
        cells = {"ende": [], "kant": []}
        for a in pl["axes"]:
            cells[a["role"]].append(_place_cell(a))
        cc = [_fmt(a["cc"]) for a in pl["axes"] if a["cc"] is not None]
        piece = (f"{PART_NO[pl['member']]} "
                 f"{_no_section(G, pl['section'].replace('×', 'x'))} × "
                 f"{_fmt(pl['piece_len'])}")
        out.append((f"**{pl['jid']}** {pl['per']}× {_fast_short(pl['name'])}",
                    f"{piece}, {PLACE_FACE_NO[pl['face']]}",
                    " · ".join(cells["ende"]) or "—",
                    " · ".join(cells["kant"]) or "—",
                    " / ".join(cc) or "—"))
    # ...and the wall fixings, which the model places but cannot measure into
    # a piece: their X belongs to the studs. Same table, same columns.
    out += wall_fix_placement_rows(G, st)
    return out


# The rules are explained ONCE, at the top of the guide; a step page only
# gets the table. Repeating five lines of convention twelve times is how a
# manual stops being read.
PLACE_INTRO = "**Festeplassering — mål på delen:**\n"
PLACE_RULES = (
    "**Hvert steg har en «festeplassering»-tabell**, og den er svaret på "
    "hvor langt inn og hvor langt opp på materialet et feste skal stå. "
    "Hullet er oppgitt i DELENS egne mål — så mange mm inn fra en navngitt "
    "ende, så mange mm inn fra en navngitt kant, og senteravstand mellom "
    "hullene i samme rad. Ta tabellene med til steg 0: det er der du merker "
    "opp og borer, mens delene ennå ligger løse på bukken — med to unntak, "
    "og begge står i punktene under.\n\n"
    "* **Romdelene bores ikke på bukken.** De er kappet med overmål i den "
    "enden som møter vegg, og alle målene i raden er tatt fra nettopp den "
    "enden. De finkappes etter målt nisjebredde først, og bores så. Siste "
    "punkt i steg 0 sier hvilke.\n"
    "* **Veggfestene har ingen X-mål i det hele tatt.** Stenderne bestemmer, "
    "og de finnes bare i rommet. Raden gir høyden, diameteren og regelen — "
    "og hullene bores på stedet.\n"
    "* **Ytterenden** er den enden av delen som peker mot nærmeste "
    "endevegg, **innerenden** den som peker inn mot sengas midte. Derfor "
    "gjelder ett mål begge sider av senga — og modellen måler at de to "
    "halvdelene faktisk projiserer til samme tall før det skrives.\n"
    "* **Stående deler måles ovenfra.** Foten kappes i vater etter at rammen "
    "står, så den enden finnes ikke ennå når du borer.\n"
    "* **«midt på» er senterlinjen.** Riss den opp med senterlinjal eller "
    "med to diagonaler — ikke mål fra den ene siden.\n"
    "* Målene er senter av hullet. Retningen skruen drives, og hvorfor akkurat "
    "den veien, står i [skrueretninger](skrueretninger.md).\n\n")


def assert_placement_ink(G, bygg, retn):
    """Every fastener on the direction sheet has a line that says WHERE.

    Read off the two emitted fragments, not off the data that made them: the
    direction sheet and the placement tables are two readings of one set of
    solids, and a fastener that lost its placement line - a joint that fell
    out of a step, a drive nobody printed - is exactly the kind of silent
    hole this pair of tables exists to close.
    """
    def cells(text):
        for line in text.split("\n"):
            if line.startswith("| **J"):
                yield [x.strip() for x in line.strip().strip("|").split("|")]

    # The direction sheet: the joint is its own column, the fastener is
    # «2× Treskrue 6×80 forsenket Torx» in the next one.
    driven = set()
    for c in cells(retn):
        jid = re.fullmatch(r"\*\*(J[\w-]+)\*\*", c[0]).group(1)
        driven.add((jid, _fast_short(re.sub(r"^\d+× ", "", c[1]))))
    # The placement tables: joint and fastener share the first column.
    placed = {}
    for c in cells(bygg):
        m = re.fullmatch(r"\*\*(J[\w-]+)\*\* \d+× (.+)", c[0])
        if not m:
            continue
        key = (m.group(1), m.group(2))
        placed[key] = placed.get(key, 0) + 1
    # THE WALL FIXINGS ARE READ OUT FIRST, and against the model rather than
    # against the direction sheet: they go into a wall and not into a second
    # piece of wood, so they have no drive and no direction row - see the last
    # line of skrueretninger.md. What they DO have is a placement line each,
    # and this is where that is counted.
    wall_want = {(w["jid"], _fast_short(w["name"])): w
                 for w in wall_fix_lines(G)}
    wall_ink = {k: v for k, v in placed.items() if k in wall_want}
    placed = {k: v for k, v in placed.items() if k not in wall_want}
    assert set(wall_ink) == set(wall_want), (
        f"veggfeste: {sorted(set(wall_want) - set(wall_ink))} står i modellen "
        f"uten en plasseringslinje")
    assert all(v == 1 for v in wall_ink.values()), \
        "et veggfeste har fått mer enn én plasseringslinje"
    missing = driven - set(placed)
    extra = set(placed) - driven
    assert not missing and not extra, (
        f"festeplassering: {sorted(missing)} står i skrueretningene uten en "
        f"plasseringslinje, og {sorted(extra)} står plassert uten å være "
        f"drevet")
    # ...and the lines have to add up to the whole bed, not just to each
    # other: every fastener the model placed is inside one of them.
    n_lines = sum(placed.values())
    assert n_lines == len(G.FASTENER_PLACEMENTS), (
        f"{n_lines} plasseringslinjer på trykk mot "
        f"{len(G.FASTENER_PLACEMENTS)} i modellen")
    n_fast = sum(pl["n"] for pl in G.FASTENER_PLACEMENTS)
    driven_total = len([f for f in G.FASTENER_SPECS if f["drive"] is not None])
    assert n_fast == driven_total, \
        f"{n_fast} festemidler dekket av plasseringslinjene mot {driven_total}"
    n_wall = sum(w["n"] for w in wall_fix_lines(G))
    print(f"  festeplassering: {n_lines} linjer, {len(driven)} "
          f"skrueretninger, {n_fast} festemidler - én linje per rad, ingen "
          f"rad uten linje; + {len(wall_ink)} veggfestelinjer med {n_wall} "
          f"fester, plassert etter stender og ikke etter mål")


# ---------------------------------------------------------------------------
# X12 - A DATUM THAT IS STILL WASTE WHEN THE DRILL COMES OUT
# ---------------------------------------------------------------------------
# X6 rule 2 says an end that does not exist yet is not a datum, and the model
# keeps it by REFUSING to name such an end (`_end_is_datum`). That is the
# right place for the rule and the wrong place for the proof: the rule is
# about the meeting of three separate facts, and the model only holds one of
# them.
#
#   * the CUT LIST knows which ends leave the bench oversize - ROOM_OVER_WALL
#     on every end that meets a wall, ROOM_OVER_FLOOR under every foot;
#   * the PLACEMENT TABLE names the end each hole is measured from;
#   * the STEPS know when the drill comes out - step 0 for everything that is
#     cut to size in the shop, and a point of its own, after the fine cut, for
#     the pieces the room finishes.
#
# Any two of those three can agree while the third one drifts, and none of
# them can see the other two. So this reads all three OFF THE FINISHED INK -
# the placement rows in byggesteg.md and the sentence in step 0 that names
# the deferred joints - and demands they close:
#
#   a hole measured from an end that is still 10 mm of waste when it is
#   bored has to be in the deferred list, and every joint in that list has
#   to have such a hole.
#
# The foot is the other half of the same rule and it has no deferred list at
# all: a foot is trimmed in vater long after the frame is standing, so a hole
# measured up from one can never be bored. That is not "defer it", it is "you
# cannot say it" - and it is why the ladder's rung holes count DOWN from the
# top.
END_NO_AXIS = {"ytterenden": (0, "ytre"), "innerenden": (0, "indre"),
               "veggenden": (1, "bak"), "romenden": (1, "fram"),
               "nedre ende": (2, "ned"), "toppen": (2, "opp")}
# The two-in-one datum names, which have to be expanded before they are asked
# about: «fra begge ender» is a claim about both of them.
END_NO_PAIRS = {"vegg- og romenden": [(1, "bak"), (1, "fram")]}
END_NO_BOTH = "begge ender"          # the axis comes from the piece
DRILL_DEFER_MARK = "IKKE PÅ BUKKEN"


def oversize_ends(fit):
    """The ends of a piece that are still waste when it leaves the bench."""
    if fit is None:
        return set()
    if fit["kind"] == "vegg":
        return {(0, "ytre")}         # ROOM_OVER_WALL, fine-cut in the room
    if fit["kind"].startswith("gulv"):
        return {(2, "ned")}          # ROOM_OVER_FLOOR, trimmed in vater
    return set()                     # meddrag: the WIDTH is scribed, not the end


def assert_datum_ink(G, bygg):
    """No placement line measures from an end that is still oversize."""
    rows, defer_ink = [], None
    for line in bygg.split("\n"):
        if DRILL_DEFER_MARK in line:
            m = re.search(r"Det gjelder ((?:J[\w-]+, )*J[\w-]+)\.", line)
            assert m, (f"steg 0 har «{DRILL_DEFER_MARK}»-punktet, men det "
                       f"navngir ingen ledd - regelen har ingen eier på trykk")
            defer_ink = set(m.group(1).split(", "))
            m2 = re.search(r"har (\d+) mm overmål i hver ende", line)
            assert m2 and int(m2.group(1)) == G.ROOM_OVER_WALL, (
                f"steg 0 trykker et annet overmål enn modellens "
                f"{G.ROOM_OVER_WALL} mm")
        if line.startswith("| **J"):
            rows.append([x.strip() for x in line.strip().strip("|").split("|")])
    assert defer_ink is not None, \
        f"ingen «{DRILL_DEFER_MARK}»-setning på trykk i steg 0"

    # The piece is found by the string the emitter PRINTS for it, built here
    # out of the same two calls the placement row is built out of. A cell that
    # matches no cut-list line is a cell nobody can look up, and that is a
    # finding in itself - so it is an assert and not a `continue`.
    by_ink = {}
    for p in G.CUT_PARTS:
        ink = f"{_no_section(G, p.cut[1])} × {_fmt(p.cut[2])}"
        by_ink.setdefault(ink, []).append(p)

    earned, bench_hits, foot_hits = set(), [], []
    for c in rows:
        jid = re.fullmatch(r"\*\*(J[\w-]+)\*\*.*", c[0]).group(1)
        hits = [ink for ink in by_ink if ink in c[1]]
        assert len(hits) == 1, (
            f"{jid}: «{c[1]}» treffer {len(hits)} kapplinjer - "
            f"plasseringsraden navngir en del kapplista ikke har")
        ps = by_ink[hits[0]]
        if "Veggfeste" in c[0]:
            # No piece datum at all: the studs decide, and the row says so.
            assert "etter stender" in c[2], \
                f"{jid}: et veggfeste har fått et X-mål som fasit: «{c[2]}»"
            continue
        over = oversize_ends(G.ROOM_FIT.get(ps[0].label))
        if not over:
            continue
        # Which ends does the row name? The «fra enden» column is always the
        # piece's LENGTH axis, so «begge ender» resolves against that.
        axis = G._length_axis(ps[0])
        named = set()
        for word, ref in END_NO_AXIS.items():
            if f"fra {word}" in c[2]:
                named.add(ref)
        for word, refs in END_NO_PAIRS.items():
            if f"fra {word}" in c[2]:
                named |= set(refs)
        if f"fra {END_NO_BOTH}" in c[2]:
            named |= {(axis, w) for w in
                      (("ytre", "indre"), ("bak", "fram"), ("ned", "opp"))[axis]}
        hit = named & over
        if not hit:
            continue
        if any(a == 2 for a, _w in hit):
            foot_hits.append((jid, ps[0].label, c[2]))
        else:
            earned.add(jid)
            if jid not in defer_ink:
                bench_hits.append((jid, ps[0].label, c[2]))

    assert not foot_hits, (
        "X6/X12: disse plasseringslinjene måler fra en FOT som først kappes "
        "i vater når rammen står - det finnes ikke noe senere boretidspunkt "
        "å utsette dem til, så linjen må måles fra toppen i stedet: "
        + "; ".join(f"{j} på '{l}' ({t})" for j, l, t in foot_hits))
    assert not bench_hits, (
        f"X6/X12: disse måles fra en ende som ennå har {G.ROOM_OVER_WALL} mm "
        f"overmål når steg 0 borer, og steg 0 utsetter dem ikke: "
        + "; ".join(f"{j} på '{l}' ({t})" for j, l, t in bench_hits)
        + f". Enten skal leddet stå i «{DRILL_DEFER_MARK}»-punktet, eller så "
          f"skal hullet måles fra den andre enden")
    assert earned == defer_ink, (
        f"X6/X12: steg 0 utsetter {sorted(defer_ink)}, og det er "
        f"{sorted(earned)} som faktisk måler fra en ende med overmål. "
        f"For mye: {sorted(defer_ink - earned)}; for lite: "
        f"{sorted(earned - defer_ink)}")
    print(f"  X12 referanse-ende: {len(rows)} plasseringsrader lest av "
          f"blekket mot kapplistas overmål. {len(earned)} ledd "
          f"({', '.join(sorted(earned))}) måler fra en ende som ennå har "
          f"{G.ROOM_OVER_WALL} mm på seg, og steg 0 utsetter nøyaktig de "
          f"samme. Ingen linje måler fra en fot")


# ---------------------------------------------------------------------------
# X16 - THE ONE RUNG THAT IS NOT LIKE THE OTHERS HAS TO SAY SO ON PAPER
# ---------------------------------------------------------------------------
# X16 took two bordklosser off the ladder and gave their job to a rung. That
# is the right piece of wood in the right place, and it has one cost that no
# drawing can carry on its own: the seat rung LOOKS EXACTLY LIKE THE OTHER
# FOUR. Same section, same length, same two screws, same block underneath.
# Nothing about it on the bench says «this one is the table top's front edge,
# and if it is 3 mm out the plate rocks».
#
# So the sentence that says it is a load-bearing artefact, and it is checked
# like one. The step that builds the ladder has to NAME the seat rung by its
# number and PRINT the height it is set to, measured down from the upright top
# the way every other height on a standing part is - and both have to be the
# model's own numbers. A step guide that quietly stops saying which rung the
# plate lands on is exactly the failure this round invented, and it is not a
# thing a reader would notice: the ladder would still be right in every
# drawing and the builder would still have no reason to measure that one rung
# twice.
def assert_seat_rung_ink(G, bygg):
    """The step guide has to name the seat rung and print its own height."""
    seat_no = G.RUNG_TOPS.index(G.PANEL_UNDER_TABLE) + 1
    down = _upright_top(G) - G.PANEL_UNDER_TABLE
    body = bygg.split("## Steg 6")[-1].split("\n## ")[0]
    assert f"Trinn {seat_no}" in body, (
        f"X16: steg 6 navngir ikke støttetrinnet. Platen lander på trinn "
        f"{seat_no} i bordstilling, og det trinnet er ikke til å skille fra "
        f"de andre fire på benken - står det ikke på arket, finnes det ikke")
    assert f"{_fmt(down)} mm" in body, (
        f"X16: steg 6 skriver ikke ned støttetrinnets egen høyde "
        f"({_fmt(down)} mm ned fra stigevangens topp). Det er det ene målet "
        f"på stigen som bordplaten hviler på")
    print(f"  X16 støttetrinnet: steg 6 navngir trinn {seat_no} og setter det "
          f"{_fmt(down)} mm ned fra stigevangens topp - lest av blekket, mot "
          f"modellens egen {G.PANEL_UNDER_TABLE} mm")


# ---------------------------------------------------------------------------
# X15 - AND THE SAME REFERENCE RULE, ASKED OF THE DRAWINGS
# ---------------------------------------------------------------------------
# assert_datum_ink() above holds the PLACEMENT TABLE to X6 rule 2: no hole is
# measured from an end that is still waste. X15 put measurements on the step
# sheets as well, and they are measured off the same bed at the same moment -
# so they answer to the same rule. It is asked here, of the derived records,
# rather than in the drawing file: a measure that may not exist must not be
# drawn OR emitted, and the place to refuse it is where it is made.
def assert_step_dims(G, steps):
    import step_dims
    recs = step_dims.owed(G, steps)
    n_z = step_dims.assert_datums(G, recs)
    n_dim = sum(1 for r in sum(recs.values(), []) if r["kind"] == "mål")
    n_flush = sum(len(v) for v in recs.values()) - n_dim
    print(f"  X15 plasseringsmål: {n_dim} mål og {n_flush} flukt over "
          f"{len([n for n in recs if recs[n]])} steg, alle utledet av "
          f"kroppene og leddene. {n_z} av dem er høyder, og hver eneste en "
          f"måles NEDOVER fra noe som står - ingen fra en fot og ingen fra "
          f"gulvet")
    return recs


def emit_byggesteg(G, out_dir, steps, idx):
    L = [HEAD, "# Steg for steg\n\n",
         "Rekkefølgen er ikke fri. Sengen står inntil bakveggen og inntil "
         "begge sidevegger, og den bygges på plass. Alt som skal skrus eller "
         "boltes fra en flate som ender mot vegg, må gjøres før den flaten "
         "kommer inntil veggen. Derfor bygges den bakfra og utover.\n\n",
         "Bildeversjonen av de samme stegene, med samme nummer, ligger i "
         "[MONTERING.md](../MONTERING.md). Mål slår du opp i "
         "[nøkkelmål](nokkelmal.md) og [kappliste](kappliste.md); "
         "leddene står i J-oversikten i "
         "[ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene), med antall og forboring "
         "i [beslaglista](beslagliste.md).\n\n",
         PLACE_RULES]

    # Før steg 0: rommet. Steg 0 kapper, og halve kapplista kan ikke kappes
    # ferdig før nisja er målt - så dette står foran, ikke i en merknad.
    room = room_first(G)
    L.append(f"## {room['title']}\n\n")
    L.append(room["intro"] + "\n\n")
    L.append("**Slik gjør du:**\n\n")
    for d in room["do"]:
        L.append(f"1. {d}\n")
    L.append("\n**Spikerslag i veggen:**\n\n")
    L.append(spikerslag_table(G, idx) + "\n")
    L.append(ROOM_ZONE_NOTE + "\n\n")
    L.append("Hva som kappes nå og hva som kappes på stedet: "
             "[kapplista](kappliste.md).\n\n")
    L.append("**Sjekk før du går videre:**\n\n")
    for c in room["check"]:
        L.append(f"* {c}\n")
    L.append("\n")

    for st in steps:
        L.append(f"## Steg {st['n']} — {st['title']}\n\n")
        L.append(st["intro"] + "\n\n")
        parts = step_part_summary(G, st, idx)
        if parts:
            L.append("**Deler:** " + " · ".join(parts) + "\n\n")
        fast = step_fastener_summary(st)
        if fast:
            L.append("**Festemidler:** " + " · ".join(fast) + "\n\n")
        if st["joints"]:
            order = [j["id"] for j in JOINTS]
            L.append("**Ledd:** " + ", ".join(
                sorted(st["joints"], key=order.index))
                     + " — se J-oversikten i "
                       "[ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene) og "
                       "[beslagliste](beslagliste.md)\n\n")
        place = placement_rows(G, st, idx)
        if place:
            L.append(PLACE_INTRO + "\n")
            L.append("| Ledd | Merkes opp på | Fra enden | Fra kanten | "
                     "c/c |\n|---|---|---|---|---:|\n")
            for row in place:
                L.append("| " + " | ".join(row) + " |\n")
            L.append("\n")
            note = wall_fix_note(G, st)
            if note:
                L.append(note + "\n")
        L.append("**Slik gjør du:**\n\n")
        for d in st["do"]:
            L.append(f"1. {d}\n")
        L.append("\n**Sjekk før du går videre:**\n\n")
        for c in st["check"]:
            L.append(f"* {c}\n")
        L.append("\n")
    text = "".join(L)
    assert_spikerslag_ink(G, idx, text)
    write(os.path.join(out_dir, "byggesteg.md"), text)
    return text


MONTERING_HEAD = (
    "<!-- GENERERT AV tools/gen_doc_tables.py under `mise run build`.\n"
    "     IKKE REDIGER FOR HÅND. Strektegningene lages av\n"
    "     `mise run montering` (tools/render_lineart.py). -->\n\n")

# HOW MANY PAIRS OF HANDS, AND WHERE. The cover used to say «2 personer» and
# every step said «hvis du er alene» - one of the two was wrong, and it was
# the cover. The steps are written for ONE man with clamps and battens, and
# they name the places where that stops being true; those places carry
# `two_person=True` in build_steps(), and the badge, the cover line and the
# pictogram caption are all read off THAT. Move the flag and all three move.
def two_person_steps(steps):
    return sorted(st["n"] for st in steps if st.get("two_person"))


def _og(items):
    items = [str(i) for i in items]
    return items[0] if len(items) == 1 else \
        ", ".join(items[:-1]) + " og " + items[-1]


def crew_line(steps):
    ns = two_person_steps(steps)
    assert ns, "ingen steg er merket som tomannsjobb - da er badgen en løgn"
    return f"1 person — 2 ved reisning (steg {_og(ns)})"


# The pictogram page. (do-key, dont-key or None, the one line beside them).
# The drawings themselves come out of tools/gen_glyphs.py; the pairs use the
# manual convention of showing the wrong way beside the right one.
def prep_rows(steps):
    ns = two_person_steps(steps)
    return [
        ("to-personer", "en-person-nei",
         f"**Én person — men to ved reisningen, steg {_og(ns)}.** Bakrammen "
         f"tippes opp om underkanten, og den fremre sidevangen løftes opp på "
         f"endebjelkene. Begge deler krever fire hender. Resten av sengen er "
         f"skrevet for én mann med tvinger og lister."),
        ("underlag", "dra-nei",
         "**Mykt underlag.** Bygg rammene flatt på papp eller teppe. Ikke "
         "dra delene over gulvet."),
        ("sorter", None,
         "**Sorter delene** etter kapplista, og merk hver del på en flate "
         "som blir skjult."),
        # Denne raden avløste "Les steg 0 først" med bokikonet. Budskapet var
        # det samme - alt kappes og bores før noe reises - men det stod bare i
        # teksten; nå står det i bildet, og paret har fått den IKKE SLIK-en
        # boka aldri hadde.
        ("blyant-foerst", "skrutrekker-foerst-nei",
         "**Blyanten først.** Merk av hvert kapp og hvert hull før du skrur "
         "— all saging og all boring skjer før delen reises: "
         "verksteddelene i steg 0, romdelene så snart de er finkappet i "
         "rommet."),
        ("verktoy", None,
         "**Verktøy:** drill med bor, torxbits, tommestokk, vater og "
         "vinkelhake."),
        ("forbor", None,
         "**Forbor.** I bordene og i all endeved er forboring et krav."),
        ("veggfeste-ja", "fritt-staaende-nei",
         "**Sengen skal skrus fast i veggen.** Den er ikke beregnet på å stå "
         "fritt — veggen er sperren på baksiden."),
    ]


# Forsteg-sidens eget SLIK / IKKE SLIK-par, i samme oppsett som «Før du
# begynner». Det er én ting på den siden som ikke lar seg si med tall, og det
# er HVORDAN en strek mot vegg blir til: klossen følger veggen, tommestokken
# gjør det ikke. Bakfallet fra punkt 8 fikk ikke sitt eget par - siden bærer
# allerede lista, målefiguren og spikerslagstabellen, og et par til ville
# skyve tabellen over på neste side for å illustrere en setning som står
# tydelig i lista.
ROOM_PREP = [
    ("meddrag-ja", "punktmaal-nei",
     "**Avstandskloss, ikke tommestokk.** Klossen følger veggen hele veien, "
     "og blyanten mot klossens ytterkant gir emnet veggens form. Ett "
     "punktmål gir en rett strek mot en vegg som ikke er rett."),
]


# On a step page the size is what you need; the full trade name is on the
# hardware page. Nothing is dropped that you cannot look up two pages back.
def _fast_short(name):
    for tail in (" forsenket Torx", " varmforsinket"):
        name = name.replace(tail, "")
    name = name.replace(", bøyd av flattstål 30×4", "")
    if name.startswith("Veggfeste"):
        return "Veggfeste"
    if name.startswith("Senkhodeskrue"):
        return "Senkhodeskrue M6×30 + skive + mutter"
    if name.startswith("Filtknott"):
        return "Filtknott ⌀40"
    return name


def _img(src, height, alt=""):
    return f'<img src="{src}" alt="{alt}" height="{height}">'


# Målefiguren på forsteg-siden er tre visninger: nisja som rom til venstre,
# oppriss og plan under hverandre til høyre. Høyden er i piksler som alle
# andre bildehøyder her; build_pdf regner den om til millimeter på papiret.
# 406 px er ca. 107 mm høyt og fyller satsbredden 180 mm - så bredt som siden
# tillater, og det er den bredden figurens egen typestørrelse er regnet for.
# Tallet er ikke fritt: render_maalfigur.assert_fits_column() leser det herfra
# og stopper tegningen hvis figurens egne proporsjoner ikke gir 180 mm ved
# akkurat denne høyden - endrer du komposisjonen der, sier asserten hva tallet
# skal være (se tools/render_maalfigur.py).
# [v14/X1: 360 -> 406. Senga ble 150 mm høyere, så opprisset ble høyere i
#  forhold til bredden og figuren smalere ved samme pikselhøyde - asserten
#  fanget det og sa hvilket tall som gir 180 mm igjen.]
ROOM_FIG_PX = 406

# Måltegningen av senga selv - side 2, rett etter forsiden. Samme regnestykke
# og samme kontrakt som over: tallet er høyden i piksler som gir figuren
# satsbredden 180 mm, og render_maaltegning.assert_fits_column() leser det
# herfra og stopper tegningen hvis komposisjonen har endret proporsjonene.
# Den er nesten kvadratisk, så den er nesten dobbelt så høy som romfiguren.
MAAL_FIG_PX = 673


# The glyphs are all drawn to ONE scale, and each carries that scale in the
# height of its viewBox - a wood screw is 120 units tall, the big angle
# bracket 386. Rendering every glyph to the same pixel height would throw
# that away and make a 90 mm bracket look like a 5 mm screw, so the height in
# the page is taken from the drawing instead. SCREW_UNITS is the reference.
SCREW_UNITS = 120.0


def _glyph_height(path, screw_px, cap=None):
    with open(path, encoding="utf-8") as fh:
        head = fh.read(4000)
    m = re.search(r'viewBox="[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+([\d.]+)"', head)
    units = float(m.group(1)) if m else SCREW_UNITS
    h = round(screw_px * units / SCREW_UNITS)
    return min(h, cap) if cap else max(h, 12)


def emit_montering(G, root, steps, idx):
    """docs/MONTERING.md - the pictorial manual. Same steps, same numbers.

    Page 1 is the cover, page 2 the bed's own six dimensions, page 3 the
    room, page 4 the preparation pictograms, page 5 the hardware inventory,
    page 6 the part inventory, then one page per step.
    Everything on those pages is derived: the drawings from the model, the
    counts from JOINTS and the cut list, the step order from build_steps().
    """
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import gen_glyphs

    img_dir = os.path.join(root, "docs", "img")
    total_fast = hardware_total(steps)          # also asserts the step counts
    glyph = gen_glyphs.emit_fastener_glyphs(sorted(total_fast),
                                            os.path.join(img_dir, "beslag"))
    legend = gen_glyphs.emit_notation_legend(os.path.join(img_dir, "beslag"))
    # THE FILL CODE. A badge letter carries a fill pattern as well as a
    # letter, and the pattern follows it everywhere the letter goes - so the
    # glyph in a step's own fastener table is the coded one, drawn with the
    # same pattern the drawing above it puts in that screw. Which (fastener,
    # code) pairs exist is decided by the STEPS, because that is where the
    # letters are handed out; a pair no page shows is a file nobody reads.
    #
    # And a page only hands out fills where the SHAPES need them - see
    # step_fill_code(). A step whose screws tell themselves apart draws them
    # bare, and its table draws them bare too: the table is the key to the
    # picture above it, so a coded row over an uncoded screw would be a key to
    # a lock that is not there.
    coded_pairs = set()
    for st in steps:
        if not step_fill_code(st):
            continue
        for name, letter in step_badges(st).items():
            code = gen_glyphs.fill_code(letter)
            if code and code != "open":
                coded_pairs.add((name, code))
    coded = gen_glyphs.emit_coded_glyphs(coded_pairs,
                                         os.path.join(img_dir, "beslag"))
    fill_legend = gen_glyphs.emit_fill_code_legend(
        os.path.join(img_dir, "beslag"))
    # FIGURHODET er REGNET, ikke tegnet. Landemerketabellen i
    # tools/gen_figurhode.py er kilden, og den skriver hodet inn i de fire
    # figurikonene FØR piktogramsiden settes av dem - og den samme tabellen
    # skriver PRAKSIS §4. Ikonfilene er dermed artefakter som resten: en hånd
    # som retter et tall i en av dem blir overskrevet ved neste bygg, og
    # `mise run check` hasher dem.
    import gen_figurhode
    gen_figurhode.regenerate()
    pikto = gen_glyphs.emit_pictograms(os.path.join(img_dir, "ikon"))
    # As many letters as the busiest step needs, and no more.
    widest = max((len(step_badges(st)) for st in steps), default=0)
    merke = gen_glyphs.emit_badges(os.path.join(img_dir, "ikon"), widest)

    def gimg(name, screw_px, cap=None, code=None):
        f = coded.get((name, code), glyph[name])
        h = _glyph_height(os.path.join(img_dir, "beslag", f), screw_px, cap)
        return _img("img/beslag/" + f, h, name)

    # ----- page 1: cover ---------------------------------------------------
    parts_rows = cut_table(G)
    n_parts = sum(r[3] for r in parts_rows)
    # Every numbered page is a step, and step 0 - the cutting, drilling and
    # countersinking that happens before anything is raised - is one of them.
    # The cover counts what the reader will actually turn: 12 steg (0-11), the
    # same count byggerekkefolge.svg prints. Counting only 1..11 said 11 and
    # left the two documents contradicting each other.
    n_steps = len(steps)
    step_lo = min(st["n"] for st in steps)
    step_hi = max(st["n"] for st in steps)
    assert n_steps == step_hi - step_lo + 1, "stegnumrene har hull"
    L = [MONTERING_HEAD,
         "# HANNA\n\n",
         "## Loftseng med sofa, bord og ekstraseng under\n\n",
         "![HANNA](img/hanna-hero.png)\n\n",
         "| Bredde | Dybde | Høyde |\n|---:|---:|---:|\n",
         f"| **{G.WALL_SPAN} mm** | **{G.OVERALL_DEPTH} mm** | "
         f"**{G.POST_HEIGHT} mm** |\n\n",
         f"{n_parts} deler · {n_steps} steg ({step_lo}–{step_hi}) · "
         f"{crew_line(steps)} · passer standard madrass 80 × 200 cm\n\n",
         "Sengen står inntil bakveggen og inntil begge sidevegger, og skrus "
         "fast i bakveggen. **Bygg bakfra og utover.**\n\n",
         "Ord og begrunnelser: [ASSEMBLY.md](ASSEMBLY.md). "
         "Full steg-for-steg-tekst: [byggesteg](generated/byggesteg.md).\n\n"]

    # ----- page 2: the bed's own dimensions --------------------------------
    # Forsiden viser senga; denne siden svarer på hvor stor den er, og den
    # står FØR «Mål rommet først» med vilje: den som skal måle nisja må vite
    # hva den skal måle den mot. Seks mål, ikke flere - resten er nøkkelmål.
    # Tegningen lages av tools/render_maaltegning.py under `mise run
    # montering`; denne fila skriver bare taggen og teksten under den.
    L.append("---\n\n# Sengen i mål\n\n")
    L.append(_img("img/hanna-maal.png", MAAL_FIG_PX,
                  f"Senga i bordstilling, sett på skrå, med seks mål: "
                  f"{G.WALL_SPAN} mm bredde, {G.OVERALL_DEPTH} mm dybde, "
                  f"{G.POST_HEIGHT} mm høyde, {G.SLAT_Z0} mm fri høyde "
                  f"under, {G.PANEL_TOP_TABLE} mm pulthøyde og "
                  f"{G.SLAT_LEN} mm soveflate på tvers") + "\n\n")
    L.append(f"**{G.WALL_SPAN} × {G.OVERALL_DEPTH} × {G.POST_HEIGHT} mm.** "
             f"Bredden er rommets tall og ikke sengas: senga fyller nisja "
             f"vegg til vegg, og hver gjennomgående del kappes til "
             f"{G.THROUGH_LEN} mm for å komme inn i den.\n\n")
    L.append(f"Under senga står **{G.SLAT_Z0} mm** fritt. Platen er tegnet i "
             f"bordstilling, på **{G.PANEL_TOP_TABLE} mm** — den samme platen "
             f"ligger nede på {G.PANEL_TOP_BED} mm som sengebunn. Soveflaten "
             f"oppe er {G.WALL_SPAN} × **{G.SLAT_LEN} mm** — vegg til vegg, "
             f"ikke kappelengden: spilene er {G.THROUGH_LEN} mm og holdes "
             f"{G.THROUGH_X0} mm fra hver vegg for å komme inn, men madrassen "
             f"presses de siste millimeterne inn mellom veggene og fyller "
             f"hele nisjas bredde. En standard madrass på 80 × 200 cm.\n\n")
    L.append("Alle mål i mm, målt fra ferdig gulv. Resten av tallene står i "
             "[nøkkelmål](generated/nokkelmal.md).\n\n")

    # ----- page 3: the room ------------------------------------------------
    # Denne siden står før alt annet fordi arbeidet gjør det: nisja må være
    # ferdig og målt før halve kapplista kan kappes. Samme tekst som i
    # byggesteg.md - den står ett sted, i room_first().
    room = room_first(G)
    L.append("---\n\n# Mål rommet først\n\n")
    L.append(room["intro"] + "\n\n")
    for i, d in enumerate(room["do"], 1):
        L.append(f"{i}. {d}\n")
    # Figuren står ETTER lista og før spikerslagstabellen, fordi den er
    # bildet av punkt 2 og 3 og ikke av siden som helhet. Den tegnes av
    # tools/render_maalfigur.py under `mise run montering`, akkurat som
    # stegbildene lenger bak - denne fila skriver bare taggen.
    L.append("\n" + _img("img/maal-rommet.png", ROOM_FIG_PX,
                         f"Nisja som rom, med oppriss og plan ved siden av: "
                         f"høyderisset {G.MEASURE_DATUM_Z} mm over ferdig "
                         f"gulv går som en ring rundt alle tre veggene, "
                         f"loddplanet står midt i nisja, og hver endevegg "
                         f"måles i {G.MEASURE_GRID[0]} høyder × "
                         f"{G.MEASURE_GRID[1]} dybder")
             + "\n\n")
    L.append("\n**Slik strekes en del opp mot vegg og gulv:**\n\n")
    L.append("| Slik | Ikke slik | |\n|:---:|:---:|---|\n")
    for do, dont, line in ROOM_PREP:
        yes = (_img("img/ikon/" + pikto[do], 72, do) + " "
               + _img("img/ikon/" + pikto["hake"], 26, "ja"))
        no = (_img("img/ikon/" + pikto[dont], 72, dont) + " "
              + _img("img/ikon/" + pikto["kryss"], 26, "nei"))
        L.append(f"| {yes} | {no} | {line} |\n")
    L.append("\n**Spikerslag i veggen** — legg dem mens veggen er åpen:\n\n")
    L.append(spikerslag_table(G, idx) + "\n")
    L.append(ROOM_ZONE_NOTE + "\n\n")
    for c in room["check"][:1]:
        L.append(f"⚠️ {c}\n\n")

    # ----- page 4: before you start ---------------------------------------
    L.append("---\n\n# Før du begynner\n\n")
    L.append("**Svart strek** er delen du setter opp nå. "
             "**Grå strek** er det som allerede står.\n\n")
    # The drawings say four things with marks rather than words, and none of
    # them are obvious the first time you meet them. They are explained once,
    # here, and never repeated on a step page.
    L.append("**Festemidlene er tegnet, ikke antydet.** Hver skrue, bolt og "
             "hvert beslag på stegsidene er den samme kroppen som står i "
             "modellen, i sin egen lengde og langs sin egen akse — så en "
             "skrue som peker feil vei eller er for lang stopper byggingen "
             "av manualen, ikke først byggingen av sengen.\n\n")
    L.append("**Trukket ut av hullet:** på de fleste stegene er festemidlene "
             "tegnet et stykke ut langs sin egen akse, med en **prikket "
             "linje** ned i hullet de skal i og en **prikk** der hullet er. "
             "Den prikkede linjen betyr festemiddel og ingenting annet; "
             "**piler** brukes bare om tredeler som skal føres sammen. På de "
             "stegene som setter tjue-tretti like skruer — spilene — er de "
             "tegnet **der de havner** i stedet: hodet fylt, og den delen "
             "som ligger begravd i treet **stiplet**.\n\n")
    L.append("**Bokstaven i ringen** (Ⓐ, Ⓑ …) sier hvilken av stegets typer "
             "et festemiddel er, og går igjen i tabellen under bildet. Den "
             "sitter alltid **på** skruen den gjelder, eller har en tynn "
             "strek bort til den — den peker aldri i løse lufta. Der to "
             "skruer på samme side er nesten like lange, skilles de i tillegg "
             "med **fyll** i silhuetten — den samme bokstaven én gang til, så "
             "du ser hvilken av dem det er uten å lese: åpen, skravert, "
             "krysskravert, heldekt. Ellers står skruene i ren kontur, for da "
             "skiller lengden dem selv. Hele koden står på [beslagsiden]"
             "(#beslag).\n\n")
    # Erfaringsrunde 1: the corner box came off the step sheets - it printed
    # the same fastener rows the table under the picture already prints - so
    # the sentence that sent the reader to it comes off too. The table is the
    # one place the counts stand now, and this says so.
    L.append("**Antallet står ikke i bildet.** Festemidlene er tegnet ett for "
             "ett, der de går — bare to som havner nøyaktig oppå hverandre på "
             "papiret er tegnet én gang. Hvor mange det er i alt står i "
             "tabellen under bildet, og bare der. Hvilken vei hver enkelt "
             "drives, og hva som forbores, står i "
             "[beslaglista](generated/beslagliste.md) og "
             "[skrueretningene](generated/skrueretninger.md).\n\n")
    L.append("| Slik | Ikke slik | |\n|:---:|:---:|---|\n")
    for do, dont, line in prep_rows(steps):
        yes = (_img("img/ikon/" + pikto[do], 72, do) + " "
               + _img("img/ikon/" + pikto["hake"], 26, "ja"))
        no = ("" if dont is None else
              _img("img/ikon/" + pikto[dont], 72, dont) + " "
              + _img("img/ikon/" + pikto["kryss"], 26, "nei"))
        L.append(f"| {yes} | {no} | {line} |\n")
    L.append("\n")

    # ----- page 5: hardware -----------------------------------------------
    # The legend first: nothing on this page says what the two numbers in
    # "5×60" are, or what the "100x" counts. One measured exemplar does.
    L.append("---\n\n# Beslag\n\n")
    L.append(_img("img/beslag/" + legend, 104,
                  "5 = tykkelse i mm, 60 = lengde i mm, 100x = antall")
             + "\n\n")
    # And the fill code, in the one place it is worth learning: full size,
    # all four at once. On a step page it is a reminder; here it is the
    # definition.
    L.append(_img("img/beslag/" + fill_legend,
                  int(gen_glyphs.FILL_LEGEND_PX),
                  "Fyllkoden: A åpen, B skravert, C krysskravert, D heldekt")
             + "\n\n")
    L.append("**Fyllkode.** Der to skruer på samme side er nesten like lange, "
             "skilles de med fyll — ellers står festemidlene i ren "
             "kontur.\n\n")
    L.append("| | |\n|:---:|---|\n")
    for name, qty in sorted(total_fast.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {gimg(name, 44)} **{qty}x** | {name} |\n")
    L.append("\nHvor hver enkelt går, og hva som forbores: "
             "[beslagliste](generated/beslagliste.md). Hvilken vei hver "
             "enkelt drives, og hvorfor: "
             "[skrueretninger](generated/skrueretninger.md).\n\n")

    # ----- page 6: parts ---------------------------------------------------
    L.append("---\n\n# Delene\n\n")
    L.append("| Del | Dim. | Lengde | Ant. | Kapp |\n|---|---|---:|---:|---|\n")
    for no_name, section, length, qty, _sp, _en, fit in parts_rows:
        L.append(f"| {no_name} | {section} | {_fmt(length)} | **{qty}** | "
                 + ("på stedet" if fit else "nå") + " |\n")
    L.append(f"\n**{n_parts} deler.** **Ant.** er antallet — det samme tallet "
             "som står som `4×` på stegsidene. **Dim.** og **Lengde** er i "
             "millimeter.\n\n")
    n_room = sum(r[3] for r in parts_rows if r[6])
    L.append(f"**Kapp:** «nå» er delene verkstedet gjør ferdig. «på stedet» "
             f"er de {n_room} delene som møter en endevegg eller gulvet — de "
             "kappes med overmål og finkappes i rommet. Overmålet står i "
             "[kapplista](generated/kappliste.md).\n\n")
    L.append("Posisjoner: [kappliste](generated/kappliste.md). Hva du skal "
             "kjøpe: [innkjøpsliste](generated/innkjopsliste.md).\n\n")

    # ----- the step pages --------------------------------------------------
    order = [j["id"] for j in JOINTS]
    for st in steps:
        L.append("---\n\n")
        L.append(f"# {st['n']}\n\n")
        L.append(f"## {st['title']}\n\n")
        if st.get("image", True):
            L.append(f"![Steg {st['n']}](img/steg-{st['n']:02d}.png)\n\n")

        rows = step_part_rows(G, st, idx)
        if rows:
            L.append("| Ant. | Del | Dim. | Lengde |\n|---:|---|---|---:|\n")
            for qty, name, section, length in rows:
                L.append(f"| **{qty}×** | {name} | {section} | {length} |\n")
            L.append("\n")

        fast = step_fastener_rows(st)
        badges = step_badges(st)
        if fast and badges:
            # More than one kind in this step: the letter column is the key to
            # the same letters on the drawing's fastening arrows. Listed in
            # letter order, which is the order the drawing's inset lists them
            # in too - commonest first.
            fills_on = step_fill_code(st)
            L.append("| | | |\n|:---:|:---:|---|\n")
            for name, qty in sorted(fast, key=lambda r: badges[r[0]]):
                code = gen_glyphs.fill_code(badges[name]) if fills_on else None
                L.append(f"| {_img('img/ikon/' + merke[badges[name]], 20, badges[name])}"
                         f" | {gimg(name, gen_glyphs.GLYPH_MIN_PX, cap=72, code=code)} "
                         f"**{qty}x** | {_fast_short(name)} |\n")
            if fills_on:
                L.append("\nBokstavene viser hvor på tegningen hver type går. "
                         "To av dem er nesten like lange, så de bærer fyll "
                         "også — den samme bokstaven om igjen — "
                         "se [fyllkoden på beslagsiden](#beslag).\n\n")
            else:
                L.append("\nBokstavene viser hvor på tegningen hver type "
                         "går.\n\n")
        elif fast:
            L.append("| | |\n|:---:|---|\n")
            for name, qty in fast:
                L.append(f"| {gimg(name, gen_glyphs.GLYPH_MIN_PX, cap=72)} "
                         f"**{qty}x** | "
                         f"{_fast_short(name)} |\n")
            L.append("\n")

        if st["joints"]:
            L.append("Ledd " + ", ".join(
                f"**{j}**" for j in sorted(st["joints"], key=order.index))
                + " → [beslagliste](generated/beslagliste.md)\n\n")
        for c in st["check"][:1]:
            L.append(f"⚠️ {c}\n\n")
        L.append(f"[Steg {st['n']} i ord]"
                 f"(generated/byggesteg.md#steg-{st['n']}"
                 f"--{_anchor(st['title'])})\n\n")

    L.append("---\n\n")
    L.append("Tegningene i `docs/img/` er projisert ut av modellen og sjekket "
             "inn i git. De lages på nytt med `mise run montering`.\n")
    path = os.path.join(root, "docs", "MONTERING.md")
    write(path, "".join(L))


def _anchor(title):
    out = []
    for ch in title.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -":
            out.append("-")
    return "".join(out)


# ---------------------------------------------------------------------------
# WHICH WAY EVERY SCREW GOES - the sheet a human reviews
# ---------------------------------------------------------------------------
# The direction a screw is driven is what the arrows in docs/MONTERING.md
# assert on every page, and it is the one thing in this documentation that
# cannot be read off the model: the geometry says two boxes meet, not which
# side the drill was on. So it is derived where it CAN be derived - a screw
# has to pass through the member it is driven from and stop inside the one it
# grips, and for most of these joints only one direction does that - and it is
# reviewed where it cannot. This page is that review: one line per screw, with
# the basis stated, so a builder can check the drawings against the joint.
BASIS = {
    "utledet": "utledet av tykkelsene",
    "tvetydig": "fastsatt — begge veier holder målene",
    "unntak": "fastsatt",
    "gjelder ikke": "fastsatt",
}

# The drawing's part KINDS in Norwegian live with the joint table in
# generate_loftbed.py, because that is where the joint table now is.
KIND_NO = PART_NO

# The model's own axes, said out loud. X runs along the wall, Y out of it
# towards the room, Z up.
AXIS_NO = {(0, 1): "mot høyre vegg", (0, -1): "mot venstre vegg",
           (1, 1): "utover mot rommet", (1, -1): "innover mot veggen",
           (2, 1): "rett opp", (2, -1): "rett ned"}


def _dir_no(vec):
    """The drive vector as a phrase. Skew screws get both components."""
    parts_ = [(j, v) for j, v in enumerate(vec) if abs(v) > 1e-6]
    parts_.sort(key=lambda jv: -abs(jv[1]))
    words = [AXIS_NO[(j, 1 if v > 0 else -1)] for j, v in parts_]
    if len(words) == 1:
        return words[0]
    ang = math.degrees(math.atan2(abs(parts_[1][1]), abs(parts_[0][1])))
    return f"{words[0]}, {ang:.0f}° skrått {words[1]}"


def emit_skrueretninger(G, out_dir, idx):
    """One line per kind of fastener per joint, printed off the placed solids.

    Nothing here is prose that somebody keeps in step with the drawings: the
    direction is the unit vector the model drove the screw along, and the
    members are the ones it actually passes through. The old «Drives fra»
    sentence in the joint table has become this caption.
    """
    def dims(part):
        return _no_section(G, idx[part.label][1])

    def kind_of(crow, part, pa, pb):
        return crow["a"] if part is pa else crow["b"]

    L = [HEAD, "# Skrueretninger\n\n",
         "Hvilken vei hver skrue drives, og hvorfor akkurat den veien. "
         "Hvert festemiddel i denne sengen er modellert som en kropp med "
         "egen retningsvektor; tabellen under er skrevet ut av de kroppene, "
         "ikke av en setning noen holder ved like. Tegningene i "
         "[MONTERING.md](../MONTERING.md) tegner de samme kroppene.\n\n",
         "**Utledet** betyr at bare én retning er fysisk mulig: skruen må gå "
         "klar gjennom delen den drives fra og ende inne i den andre, altså "
         "`tykkelse(fra) < lengde < tykkelse(fra) + tykkelse(inn i)`. "
         "**Fastsatt** betyr at begge retninger ville holdt målene, eller at "
         "skruen ikke er en rett gjennomskrue i det hele tatt (skråskrue, "
         "gjennomgående bolt, beslagflik) — da er retningen den som står i "
         "leddtabellen, og den er satt for hånd og kontrollert mot "
         "geometrien.\n\n",
         "**Der begge veier holder målene, avgjør fronten.** Sengens front "
         "— alt fra vangenes ytterflate og fram til stolpeplanet — er den "
         "eneste flaten noen ser på, og det skal ikke stå et skruehode i "
         "den. Ledd som griper i en del i det laget skrus derfor innenfra og "
         "ut, og linjene under sier det. Modellen asserter det: ingen "
         "festemiddelhoder på en romvendt flate.\n\n",
         "**Hvor på delen hullet står** — så mange mm inn fra en navngitt "
         "ende og en navngitt kant, og senteravstanden mellom hullene — står "
         "i «festeplassering»-tabellen i det steget som eier leddet, i "
         "[byggesteg](byggesteg.md). Det er én plasseringslinje per rad i "
         "tabellen under, og den bijeksjonen er en assert på det ferdige "
         "blekket: en retning uten plassering, eller en plassering uten "
         "retning, feller bygget.\n\n",
         "| Ledd | Festemiddel | Retning | Grunnlag |\n",
         "|---|---|---|---|\n"]

    # One line per KIND of fastener per joint: a joint and its mirror image
    # at the far end of the bed are one line, with a note that the direction
    # turns round with it.
    order = {j["id"]: i for i, j in enumerate(JOINTS)}
    groups, seq = {}, []
    for f in G.FASTENER_SPECS:
        if f["drive"] is None:              # the wall fixing, see the note
            continue
        crow = f["crow"]
        key = (f["jid"], f["name"],
               crow["a"] if f["through"] is f["pa"] or f["into"] is f["pa"]
               else crow["b"], f["kind"], id(f["drive"]))
        if key not in groups:
            groups[key] = []
            seq.append(key)
        groups[key].append(f)
    seq.sort(key=lambda k: (order[k[0]], k[1]))

    n_derived = n_set = 0
    for key in seq:
        fs = groups[key]
        f = fs[0]
        dr = f["drive"]
        mirrored = len({q["direction"] for q in fs}) > 1
        crow, c = f["crow"], f["contact"]
        pa, pb = f["pa"], f["pb"]
        _guess, status = G.derived_entry(c, crow, pa, pb, dr)
        way = _dir_no(f["direction"])
        if f["kind"] == "plate":
            seat = f["through"] or f["into"]
            grips = pb if seat is pa else pa
            host, other = (KIND_NO[kind_of(crow, seat, pa, pb)],
                           KIND_NO[kind_of(crow, grips, pa, pb)])
            if f["through"] is not None:
                what = (f"**{f['name']}** ligger under {host}, bøyer ned "
                        f"forbi kanten og griper om {other}")
            else:
                what = (f"**{f['name']}** ligger på {host} og bøyer om "
                        f"hjørnet til {other}; skruene i fliken går {way}")
        elif f["through"] is None:
            t_no = KIND_NO[kind_of(crow, f["into"], pa, pb)]
            what = (f"**{f['name']}** gjennom beslagfliken og {way} inn i "
                    f"{t_no} ({dims(f['into'])})")
        else:
            e_no = KIND_NO[kind_of(crow, f["through"], pa, pb)]
            t_no = KIND_NO[kind_of(crow, f["into"], pa, pb)]
            what = (f"**{f['name']}** gjennom {e_no} ({dims(f['through'])}) "
                    f"→ inn i {t_no} ({dims(f['into'])}), {way}")
            if dr["counterbore"]:
                _ax = max(range(3), key=lambda j: abs(f["direction"][j]))
                _t = (f["through"].extents[_ax][1]
                      - f["through"].extents[_ax][0])
                _bite = f["length"] - (_t - dr["counterbore"])
                if getattr(f["through"], "tapered", None):
                    # The wedge: one rule, a different depth at every hole.
                    what += (f" — hodet står {_t - dr['counterbore']:g} mm "
                             f"under plata i alle tre hullene, så "
                             f"kontraboret grunner ut mot den skråkappede "
                             f"tuppen (dypest ved roten, null ved tuppen) og "
                             f"skruen tar {_bite:g} mm i {t_no} uansett")
                else:
                    what += (f" — hodet står {dr['counterbore']:g} mm inne i "
                             f"{e_no}, i bunnen av kontraboret, så skruen "
                             f"tar {_bite:g} mm i {t_no} og ingenting går "
                             f"gjennom den andre siden")
            if f.get("seat"):
                what += (f" — skruen står i et flatbunnet sete, "
                         f"⌀{f['seat_d']:g} forstner {f['seat']:g} mm ned "
                         f"langs skruens egen akse (vinkelklossen), så hodet "
                         f"ligger helt under flaten")
        if mirrored:
            what += " (speilvendt i den andre enden)"
        basis = BASIS[status]
        if dr["exempt"]:
            basis += f" — {dr['exempt']}"
        # V5: where the fit rule cannot decide, the visible front does. Read
        # off the same geometry the model asserts on, not off a list of joint
        # ids: the screw runs OUT of the room-front (+Y) into a member that
        # reaches the visible layer, so the other direction would have put
        # its head on a face the room looks at.
        elif (status == "tvetydig" and f["kind"] == "screw"
              and f["through"] is not None and f["direction"][1] > 1e-9
              and f["into"].extents[1][1] >= G.VISIBLE_FRONT_Y - 1e-6):
            basis += (" — skrudd innenfra og ut, så hodet ikke havner på "
                      "den romvendte forflaten")
        if status == "utledet":
            n_derived += 1
        else:
            n_set += 1
        L.append(f"| **{f['jid']}** | {dr['per']}× {f['name']} | {what} | "
                 f"{basis} |\n")

    L.append(f"\n**{n_derived}** av retningene er utledet av målene alene, "
             f"**{n_set}** er fastsatt for hånd. Alle sammen kontrolleres ved "
             f"hver bygging: skruekroppen må ha hodet i plan med flaten den "
             f"drives fra, spissen inne i delen den tar tak i, og ingenting "
             f"av seg selv i noen annen del.\n\n")
    L.append("Veggfestene (J14 og J12-V) står ikke her — de går rett gjennom "
             "den bakre sidevangen og gjennom bordbærelekta og inn i veggen, "
             "og har ingen andre del å gå inn i.\n")
    text = "".join(L)
    write(os.path.join(out_dir, "skrueretninger.md"), text)
    return text


def emit_beslagliste(out_dir, steps):
    total = hardware_total(steps)
    L = [HEAD, "# Beslag og festemidler\n\n",
         "Alt er elforsinket eller varmforsinket. Handelsnavn som i norsk "
         "byggevarehandel.\n\n",
         "## Handleliste\n\n",
         "| Post | Behov | Kjøp |\n|---|---:|---|\n"]
    for name, qty in sorted(total.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {name} | {qty} | {_buy_hint(name, qty)} |\n")
    L.append("\n**Behov** er antallet sengen bruker; **Kjøp** er den minste "
             "pakken som finnes i butikk og dekker behovet. Treskruer selges "
             "i pakker à "
             + " / ".join(str(n) for n in SCREW_PACK_SIZES)
             + " stk. Står det samme tall i begge kolonnene, har du ingen "
               "reserve — ta en pakke opp. En skrue du mangler koster en "
               "kveld.\n")
    L.append("\nI tillegg trengs **D3 trelim**, én liten flaske. Den er ikke "
             "en post i tabellen fordi den ikke telles i stykk, men den er "
             "ikke valgfri: J13a og J13b er limte fuger, og skruene der er "
             "tvinger som blir sittende.\n")
    L.append("\n## Hvor det går — ledd for ledd\n\n")
    L.append("| Ledd | Hva | Antall ledd | Per ledd | Forboring | "
             "Drives fra |\n|---|---|---:|---|---|---|\n")
    for j in JOINTS:
        per = " + ".join(f"{q}× {n}" for n, q in j["fast"])
        L.append(f"| **{j['id']}** | {j['title']} | {j['n']} | {per} | "
                 f"{j['drill']} | {j['side']} |\n")
    L.append("\nForklaringen til hvert ledd står i "
             "[ASSEMBLY.md](../ASSEMBLY.md#4-j--leddene).\n")
    # THE LINE THAT USED TO BE OPEN, AND IS NOT ANY MORE. The panel is a
    # drop-in unit and nothing holds it DOWN. Until this round that was the
    # one decision the manual left to the builder, and it sat here - in the
    # shopping list - as three costed options and a TBD. The decision is
    # taken now: NO LOCK, accepted deviation, and the reasoning is in
    # ASSEMBLY vedlegg B. So there is no unbought part left to list, and the
    # beslagliste says so instead of asking.
    L.append("\n## Lås i sengestilling — ingen, og det er et valg\n\n"
             "**Det står ingen lås i denne lista, og det er ikke en glipp.** "
             "Platen løftes rett opp i begge stillinger, og etter denne "
             "runden er det ingen ståldel igjen i platemekanismen i det hele "
             "tatt — verken beslag eller lås.\n\n"
             "Begrunnelsen står i sin helhet i "
             "[ASSEMBLY, vedlegg B, avvik 4](../ASSEMBLY.md#vedlegg-b--aksepterte-avvik). "
             "Kort: madrassen ligger *oppå* platen og må fjernes før platen "
             # Fallhøyden er nedre soveflate — puteoversiden over benken —
             # ned til gulvet, altså CUSHION_TOP_BENCH  [var ~26 cm].
             f"kan løftes, dette er underetasjen med ~"
             f"{_fmt(round(_MODEL.CUSHION_TOP_BENCH / 10))} cm fallhøyde, og "
             "plateenheten veier "
             f"{_fmt(round(_MODEL.PANEL_UNIT_MASS, 1))} kg.\n\n"
             "Trevirket for en ettermontert lås står likevel der det sto: "
             "**kilelektas endeved mot enden av den fremre benkevangen**, "
             f"tvers over de {_MODEL.LOCK_GAP} mm i sideklaringen, i samme "
             "høydebånd i sengestilling og "
             f"{_MODEL.PANEL_MODE_LIFT} mm fra hverandre i bordstilling. "
             "Geometrien er målt og asserted i modellen, så en lås kan "
             "ettermonteres senere uten at noe tre må endres.\n")
    write(os.path.join(out_dir, "beslagliste.md"), "".join(L))


def _buy_hint(name, qty):
    if "Låseskrue M8" in name:
        return f"{qty + 5} stk. (bolt, mutter og skive hver for seg)"
    if name.startswith("Treskrue"):
        # Treskruer selges i faste pakker, ikke i «behov + 10». Kjøp nærmeste
        # pakke opp.
        for size in SCREW_PACK_SIZES:
            if size >= qty:
                return f"1 pk. à {size} stk."
        n = -(-qty // SCREW_PACK_SIZES[-1])
        return f"{n} pk. à {SCREW_PACK_SIZES[-1]} stk."
    if "M6×30" in name:
        return f"{qty + 2} sett"
    if "Vinkelbeslag" in name:
        return f"{qty + 2} stk."
    if "flattstål" in name:
        return "kappes av flattstål 30×4 — én meter dekker alle stålbeslagene"
    if "Filtknott" in name:
        return "1 pk."
    return f"{qty} stk."


def emit_json(G, out_dir, steps, idx, rows):
    # The drawing flags travel with the step, so tools/render_lineart.py can
    # look up what kind of page this is instead of branching on its number.
    # They are written out even when false: a reader of byggesteg.json should
    # be able to see that a step is NOT a half view without knowing that the
    # key exists on other steps.
    #
    # `fill_code` is in the same list and is written the same way, but it is
    # not declared by hand in build_steps() - it is COMPUTED from the step's
    # own fastener set by step_fill_code(). That is the point: whether a page
    # needs the fill code is a fact about the screws it drives, so nobody has
    # to remember to switch it on the day a joint changes size.
    page_flags = ("half_view", "thumbnails", "crop_to_subject",
                  "no_fasteners", "info_panel", "avoid_top_left")
    data = dict(
        steps=[dict(n=st["n"], title=st["title"], image=st.get("image", True),
                    page=st.get("page", "step"),
                    labels=st["labels"], highlight=st["highlight_labels"],
                    camera=st["camera"], intro=st["intro"], do=st["do"],
                    check=st["check"],
                    fasteners=step_fastener_summary(st),
                    joints=st["joints"],
                    parts=step_part_summary(G, st, idx),
                    fill_code=step_fill_code(st),
                    **{k: bool(st.get(k, False)) for k in page_flags})
               for st in steps],
        bolt_rows={k: v for k, v in rows.items() if not k.startswith("_")},
    )
    path = os.path.join(out_dir, "byggesteg.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# STEP MESHES  (per-step .stl groups for tools/render_steps.py)
# ---------------------------------------------------------------------------
def emit_step_meshes(G, steps, group_dir):
    """Two Y-up STLs per step - everything placed before it, and this step's
    highlight - plus the `.groups` manifest tools/mesh_to_usda.swift eats."""
    from build123d import Compound, export_stl

    step_dir = os.path.join(group_dir, "steps")
    os.makedirs(step_dir, exist_ok=True)
    universe = {p.label: p for p in
                list(G.parts) + [G.panel_bed] + list(G.battens_bed)
                + list(G.FOOTREST_PARTS)
                + [G.mattress] + list(G.CUSHIONS_BED)}
    PRIOR = (0.82, 0.82, 0.80, 1.0)
    NEW = (0.94, 0.42, 0.10, 1.0)

    placed = []
    manifests = []
    for st in steps:
        if st.get("image", True) and st["camera"]:
            groups = []
            # Everything already standing, minus whatever this step paints,
            # goes in the pale group; the highlight group is exactly what the
            # step is about (new parts, or - for a step that only moves or
            # fixes what is already there - the parts it acts on).
            prior = [universe[l] for l in placed
                     if l not in st["highlight_labels"]]
            new = [universe[l] for l in st["highlight_labels"]]
            for name, members, rgba in (("prior", prior, PRIOR),
                                        ("new", new, NEW)):
                if not members:
                    continue
                path = os.path.join(step_dir, f"steg_{st['n']:02d}_{name}.stl")
                export_stl(Compound(children=[p.moved(G.Y_UP)
                                              for p in members]), path)
                groups.append(f"{name}={','.join(f'{c:.4g}' for c in rgba)}"
                              f"={path}")
            mpath = os.path.join(step_dir, f"steg_{st['n']:02d}.groups")
            with open(mpath, "w", encoding="utf-8") as fh:
                fh.write("\n".join(groups) + "\n")
            manifests.append(mpath)
        placed += st["labels"]
    print(f"  wrote {len(manifests)} per-step mesh manifests in {step_dir}")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
def emit(ns):
    import types
    G = types.SimpleNamespace(**ns)
    out_dir = os.path.join(G.OUT_DIR, "docs", "generated")
    os.makedirs(out_dir, exist_ok=True)

    print("\n=== DOC FRAGMENTS ===")
    rows = G.SCREW_ROWS
    steps = resolve_steps(G, build_steps(G))
    check_step_units(G, steps)
    idx = cut_index(G)

    emit_kappliste(G, out_dir)
    emit_innkjopsliste(G, out_dir)
    emit_nokkelmal(G, out_dir, rows)
    bygg = emit_byggesteg(G, out_dir, steps, idx)
    emit_beslagliste(out_dir, steps)
    retn = emit_skrueretninger(G, out_dir, idx)
    assert_placement_ink(G, bygg, retn)
    assert_datum_ink(G, bygg)
    assert_seat_rung_ink(G, bygg)
    assert_step_dims(G, steps)
    emit_montering(G, G.OUT_DIR, steps, idx)
    emit_json(G, out_dir, steps, idx, rows)
    emit_step_meshes(G, steps, G.GROUP_DIR)


def main():
    """`mise run build` runs this; importing the generator builds the model."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    import generate_loftbed
    emit(vars(generate_loftbed))


if __name__ == "__main__":
    main()
