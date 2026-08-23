"""Feilinjisering som port: gjør assertene om på en løgn og krev at de feller.

An assert that has never failed is not a proven assert, it is an untested
one. Every round in this project has ended the same way by hand - break the
thing on purpose, watch the gate go red, put it back - and it worked every
time it was remembered. This is that habit, written down and run by
`mise run check`.

WHICH ASSERTS. Not all of them, and the line is a real one. Most of the
asserts in the model are LOCAL: they compare two numbers that sit next to each
other, and a reader can see in one glance what would break them. The ones
worth this trouble are the GUARDS - the handful that measure the finished ink
or the placed solids ACROSS files, where the failure mode is not a wrong
number but a silence: a table that stopped being written, a joint that fell
out of a list, a body nobody measured. Those are the ones where «it passed» is
ambiguous, because passing and having nothing to say look identical.

HOW AN INJECTION WORKS. Nothing is written to disk and nothing is patched
permanently. Each case builds the input the check would have got - the model's
namespace, the resolved build steps, the emitted markdown, the README - makes
ONE change to a copy of it, and calls the check. The case passes when the
check raises AssertionError, and fails both when it passes quietly and when it
raises something else: a TypeError from a perturbation the check never even
reached is a broken injection, not a proof.

AND THE CONTROL. Before any of them run, every check is run on the unperturbed
inputs and has to pass. Otherwise «it failed» proves nothing at all.
"""

import contextlib
import io
import os
import re
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import check_tall                              # noqa: E402

# THE MODEL IS IMPORTED HERE AND NOWHERE ELSE, and the order matters: the
# model prints its whole proof as it builds, importing it twice prints
# nothing the second time, and `gen_doc_tables` imports it on its own way in.
# So the capture goes round the FIRST import - this one - and everything
# downstream gets the same module object and the same log.
_BUF = io.StringIO()
with contextlib.redirect_stdout(_BUF):
    import generate_loftbed as _MODEL          # noqa: E402
    import gen_doc_tables as T                 # noqa: E402
_LOG = _BUF.getvalue()


class Rig:
    """Everything the guards read, built once and copied per injection."""

    def __init__(self):
        self.M = _MODEL
        self.log = _LOG
        self.bygg = self._byggesteg()
        self.bygg_steps = T.resolve_steps(self.M, T.build_steps(self.M))
        self.pool = check_tall.achievable(self.M, self.log)
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            self.readme = fh.read()
        with open(os.path.join(ROOT, "docs", "generated", "kappliste.md"),
                  encoding="utf-8") as fh:
            self.kappliste = fh.read()
        self.prose = {}
        for rel in check_tall.PROSE_FILES:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                self.prose[os.path.basename(rel)] = fh.read()

    @staticmethod
    def _byggesteg():
        """The emitted step guide, read back off disk - it is the ink."""
        with open(os.path.join(ROOT, "docs", "generated", "byggesteg.md"),
                  encoding="utf-8") as fh:
            return fh.read()

    def G(self):
        """A fresh namespace over the model's globals - shallow on purpose.

        Rebinding a name on it (THROUGH_LEN, ROOM_H) leaves the model itself
        untouched, which is what lets an injection move a constant without
        rebuilding 12 seconds of solids.
        """
        return types.SimpleNamespace(**vars(self.M))

    def steps(self, G):
        return T.resolve_steps(G, T.build_steps(G))

    def step_dims(self):
        """A fresh copy of every placement measure the steps owe."""
        import copy
        import step_dims
        return copy.deepcopy(step_dims.owed(self.M, self.bygg_steps))

    def sheets(self):
        """The finished step drawings, read back off disk - they are the ink.

        X15's bijection is a question about FILES: what came out on the paper
        against what the model says the step owes. So the rig hands the guard
        the same thing `mise run montering` hands it, and an injection edits a
        copy of one sheet.
        """
        out = {}
        for st in self.bygg_steps:
            path = os.path.join(ROOT, "docs", "img", f"steg-{st['n']:02d}.svg")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as fh:
                    out[st["n"]] = fh.read()
        return out


# ---------------------------------------------------------------------------
# THE CHECKS, AS THE CONTROL RUNS THEM
# ---------------------------------------------------------------------------
def run_units(rig, G=None, steps=None):
    G = G or rig.G()
    with contextlib.redirect_stdout(io.StringIO()):
        T.check_step_units(G, steps if steps is not None else rig.steps(G))


def run_datum(rig, G=None, bygg=None):
    G = G or rig.G()
    with contextlib.redirect_stdout(io.StringIO()):
        T.assert_datum_ink(G, rig.bygg if bygg is None else bygg)


def run_readme(rig, text=None):
    with contextlib.redirect_stdout(io.StringIO()):
        check_tall.check_readme(rig.M, rig.log,
                                rig.readme if text is None else text)


def run_prose(rig, texts=None):
    with contextlib.redirect_stdout(io.StringIO()):
        check_tall.check_prose(rig.pool, texts or rig.prose)


def run_kappliste(rig, text=None):
    """X14: the cut list's own ink. Every row is checked against the POSITION
    printed in the same row - a piece under «kapp nå» may not show an X that
    reaches a wall or a Z that starts on the floor - and X14 added the one
    exception the rule has: a LOOSE piece stands on the floor and is still the
    workshop's, so its row has to say «(løs del)» out loud."""
    with contextlib.redirect_stdout(io.StringIO()):
        T._assert_kappliste_ink(rig.M, rig.kappliste if text is None else text)


def run_seat_rung(rig, bygg=None):
    """X16: the step guide names the seat rung and prints its own height.

    The rung the table plate lands on is the same section, the same length and
    the same two screws as the other four - the paper is the only place it is
    told apart, so the paper is checked."""
    G = rig.G()
    with contextlib.redirect_stdout(io.StringIO()):
        T.assert_seat_rung_ink(G, rig.bygg if bygg is None else bygg)


def run_step_dim_datum(rig, recs=None):
    """X15: no placement measure on a step sheet is taken off a foot or off
    the floor, and every height is measured downwards."""
    import step_dims
    with contextlib.redirect_stdout(io.StringIO()):
        step_dims.assert_datums(
            rig.M, rig.step_dims() if recs is None else recs)


def run_step_dim_ink(rig, sheets=None):
    """X15's bijection: what the sheets drew against what the steps owe."""
    import step_dims
    with contextlib.redirect_stdout(io.StringIO()):
        step_dims.assert_ink(rig.M, rig.bygg_steps,
                             rig.sheets() if sheets is None else sheets)


def run_brace_ink(rig, G=None, text=None):
    """X17's bijection: a step whose body is still a hinge has to carry a
    brace point on paper, and a step whose bodies are all held may not."""
    G = G or rig.G()
    with contextlib.redirect_stdout(io.StringIO()):
        T.assert_brace_ink(G, rig.steps(G), T.cut_index(G),
                           rig.bygg if text is None else text)


def run_brace_report(rig, G=None):
    """X17's fasit: the two bodies the builder wrote down after building the
    bed have to be among the ones the derived rule still catches."""
    G = G or rig.G()
    with contextlib.redirect_stdout(io.StringIO()):
        T.apply_braces(G, rig.steps(G), T.cut_index(G))


# ---------------------------------------------------------------------------
# BORESJABLONGENE
# ---------------------------------------------------------------------------
# Arkene er 1:1, og et 1:1-ark har ingen synlig feilmodus: en sjablong som er
# én millimeter feil ser nøyaktig ut som en som er riktig. Så vokterne her er
# de eneste som kan se det, og de må vises å bite.
def jig_sheets(rig):
    """Begge arkene, tegnet ferdig i minnet, med sine EGNE kopier av
    plasseringstabellen.

    Kopiene er poenget: injeksjonene under flytter et mål ETTER at arket er
    tegnet - som er nøyaktig det som skjer når modellen endrer seg og arkene
    ikke er tegnet på nytt - og det skal ikke røre modellen selv.
    """
    import copy
    import render_boresjablong as RB
    G = rig.G()
    G.FASTENER_PLACEMENTS = copy.deepcopy(rig.M.FASTENER_PLACEMENTS)
    with contextlib.redirect_stdout(io.StringIO()):
        out = [RB.build_ramme(G), RB.build_skraaskrue(G)]
    return RB, out


def run_jig(rig, sheets=None):
    """Sjablongenes egne asserter, kjørt på det som ble tegnet."""
    RB, out = sheets if sheets is not None else jig_sheets(rig)
    with contextlib.redirect_stdout(io.StringIO()):
        for _sh, _ink, rulers, drawn, _boxes, _hy, _fy in out:
            RB.assert_rulers(rulers)
            RB.assert_resolution(rulers)
            RB.assert_holes(drawn)
            RB.assert_mirrors(drawn)
            RB.assert_edge_distance(drawn)


def minimal_pdf():
    """En liten, gyldig PDF med flat xref - den samme formen Skia skriver.

    Fikstur og ikke pynt: /PrintScaling-vokteren tar BYTES, og en sak som
    bare kunne kjøres på en maskin der `mise run pdf` allerede hadde vært
    innom ville vært en sak som stille lot være å kjøre.
    """
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] >>"]
    out = bytearray(b"%PDF-1.4\n")
    offs = []
    for i, body in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj".encode() + body + b"endobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for o in offs:
        out += f"{o:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    return bytes(out)


def run_print_scaling(rig, data=None):
    """«Faktisk størrelse»-nøkkelen i katalogen til den trykte fila."""
    import build_pdf as BP
    if data is None:
        pdf = os.path.join(ROOT, "docs", "hanna.pdf")
        if os.path.exists(pdf):
            with open(pdf, "rb") as fh:
                data = fh.read()
        else:
            data = BP.set_print_scaling(minimal_pdf())
    with contextlib.redirect_stdout(io.StringIO()):
        check_tall.assert_print_scaling(data)


def run_value_comments(rig, source=None):
    src = rig.M.VALUE_COMMENT_SOURCE if source is None else source
    stale, checked, _skip = rig.M.stale_value_comments(src, vars(rig.M))
    assert checked > 100, "verdikommentar-verifikatoren leste nesten ingenting"
    assert not stale, f"foreldede verdikommentarer: {stale[:3]}"


CONTROLS = [
    ("X12 manøvrerbarhet per byggesteg", run_units),
    ("X12 referanse-ende mot overmål", run_datum),
    ("X15 plasseringsmålenes utgangspunkt", run_step_dim_datum),
    ("X15 stegarkenes plasseringsmål mot modellen", run_step_dim_ink),
    ("README-tallene", run_readme),
    ("tallsveipet over håndprosaen", run_prose),
    ("X10 verdikommentarene", run_value_comments),
    ("X14 kapplistas løse deler", run_kappliste),
    ("X16 støttetrinnet i stegveiledningen", run_seat_rung),
    ("X17 avstivingspunktene mot de ubundne kroppene", run_brace_ink),
    ("X17 byggherrens to kropper mot regelen", run_brace_report),
    ("boresjablongenes egne mål", run_jig),
    ("«Faktisk størrelse» i den trykte fila", run_print_scaling),
]


# ---------------------------------------------------------------------------
# THE INJECTIONS
# ---------------------------------------------------------------------------
def _sub(text, old, new):
    """Replace exactly once, and fail loudly if the target has moved.

    RuntimeError and not AssertionError, deliberately: the harness reads an
    AssertionError as «the gate bit». An injection that changed nothing would
    then be recorded as a proof, which is the one failure mode a falsification
    harness must not have.
    """
    if old not in text:
        raise RuntimeError(f"injeksjonen fant ikke «{old}» i teksten - "
                           f"målet har flyttet seg og saken beviser ingenting")
    return text.replace(old, new, 1)


def inj_frame_is_carried(rig):
    """Say a 1990 mm body fits through a 1990 mm opening after all."""
    G = rig.G()
    G.THROUGH_LEN = G.WALL_SPAN            # 1984 -> 1990
    run_units(rig, G)


def inj_nobody_raises_it(rig):
    """Let the step that tips the back frame stop saying which body it is."""
    G = rig.G()
    steps = rig.steps(G)
    for st in steps:
        if not st["labels"]:
            st["highlight_labels"] = []
    run_units(rig, G, steps)


def inj_ceiling_drops(rig):
    """Put the ceiling below the diagonal the frame sweeps on its way up."""
    G = rig.G()
    G.ROOM_H = 1200
    run_units(rig, G)


def inj_bench_bores_a_wall_end(rig):
    """Take one joint out of step 0's «bores senere» list and leave the row.

    This is the review's finding in miniature: the holes are measured from an
    end the room has not cut yet, and the instruction sends the builder to the
    bench with a drill anyway.
    """
    run_datum(rig, bygg=_sub(rig.bygg, "J2, J2-B, J3, J7, J8, J17",
                             "J2, J2-B, J3, J7, J17"))


def inj_measured_from_the_foot(rig):
    """Re-datum a ladder hole to the foot - the end that is still 15 mm long.

    X16: the victim used to be NAMED as J5-B's «1377 / 1401 mm fra toppen»,
    and J5-B was struck with the bordklosser it held. The row is derived now -
    the ladder stile's own J4 line, whichever heights it carries this round -
    so the case keeps aiming at the RULE and not at two numbers.
    """
    row = next(l for l in rig.bygg.split("\n")
               if l.startswith("| **J4**") and "mm fra toppen" in l)
    run_datum(rig, bygg=_sub(rig.bygg, row,
                             row.replace("mm fra toppen", "mm fra nedre ende")))


def inj_wall_fixing_gets_an_x(rig):
    """Give a wall fixing an X measurement, as if the studs were known."""
    run_datum(rig, bygg=_sub(
        rig.bygg,
        "| **J14** 6× Veggfeste | bakre sidevange 48×98 × 1984, forsiden "
        "(mot rommet) | etter stender — minst i begge ender og på midten |",
        "| **J14** 6× Veggfeste | bakre sidevange 48×98 × 1984, forsiden "
        "(mot rommet) | 165 mm fra ytterenden |"))


def _a_measure(recs, kind="mål", axis=None):
    """The first placement record of a kind, in step order - so an injection
    aims at a RULE and not at a number that may move next round."""
    for n in sorted(recs):
        for i, r in enumerate(recs[n]):
            if r["kind"] == kind and (axis is None or r["axis"] == axis):
                return n, i, r
    raise RuntimeError("modellen skylder ingen slike plasseringsmål lenger - "
                       "injeksjonen har mistet målet sitt")


def inj_step_sheet_prints_a_wrong_figure(rig):
    """Type a different number on an arrow the model measured itself."""
    sheets = dict(rig.sheets())
    n, _i, rec = _a_measure(rig.step_dims())
    old = f">{rec['figure']}</text>"
    new = f">{int(rec['mm']) + 45} mm</text>"
    sheets[n] = _sub(sheets[n], old, new)
    run_step_dim_ink(rig, sheets)


def inj_step_sheet_drops_a_measure(rig):
    """Rub one measure off a sheet and leave everything else standing.

    This is the SILENCE case, and it is the reason the bijection exists: a
    sheet that has stopped drawing a dimension looks exactly like a step that
    never owed one.
    """
    sheets = dict(rig.sheets())
    n, _i, rec = _a_measure(rig.step_dims())
    sheets[n] = _sub(sheets[n], f">{rec['figure']}</text>", ">.</text>")
    run_step_dim_ink(rig, sheets)


def inj_step_dim_measured_upward(rig):
    """Turn one height round so it is measured UP from the piece below.

    X6 rule 2 on the drawings: the lower end of a standing part is still
    ROOM_OVER_FLOOR of waste when the frame goes up, so a height taken from
    underneath is a height taken off wood that is not there yet.
    """
    recs = rig.step_dims()
    n, i, _r = _a_measure(recs, axis=2)
    recs[n][i]["alts"] = [(b, a) for a, b in recs[n][i]["alts"]]
    run_step_dim_datum(rig, recs)


def inj_step_dim_measured_from_the_floor(rig):
    """Put the datum end of a height on the floor - which is not in vater."""
    recs = rig.step_dims()
    n, i, _r = _a_measure(recs, axis=2)
    recs[n][i]["alts"] = [((a[0], a[1], 0.0), b)
                          for a, b in recs[n][i]["alts"]]
    run_step_dim_datum(rig, recs)


def inj_readme_retells_a_count(rig):
    """Let the README go on saying an artefact count that has moved."""
    m = re.search(r"krever \*\*(\d+) byte-identiske artefakter\*\*",
                  check_tall._flat(rig.readme))
    n = int(m.group(1))
    run_readme(rig, _sub(rig.readme, f"**{n} byte-identiske",
                         f"**{n + 1} byte-identiske"))


def inj_readme_quotes_a_line_the_model_lost(rig):
    """Keep quoting a printed line the model no longer prints.

    X16: the two counts were TYPED here, and X16 struck a joint and four
    screws - so the injection stopped finding its own victim and the case
    proved nothing instead of going red. Read off the README's own quote now:
    whatever it says the model prints, bump the joint count by one and demand
    the port notice that the model prints something else.
    """
    m = re.search(r"`(\d+) festemidler plassert i (\d+) ledd`", rig.readme)
    assert m, ("README siterer ikke lenger «N festemidler plassert i M ledd» - "
               "injeksjonen har mistet målet sitt og må skrives om")
    n, joints = int(m.group(1)), int(m.group(2))
    run_readme(rig, _sub(rig.readme,
                         f"{n} festemidler plassert i {joints} ledd",
                         f"{n} festemidler plassert i {joints + 1} ledd"))


def inj_readme_swaps_the_two_booklets(rig):
    """Let a sentence about the build booklet quote the reference's length.

    The two PDFs are paginated separately, and on a machine that has never
    printed them the page claims are only held to EACH OTHER - so the one way
    that check can go slack is by holding all of them to ONE number. It does
    not: there is a group per booklet. This proves it, and it proves it
    without depending on either PDF existing, because the injection makes the
    two groups disagree with each other rather than with a measurement.
    """
    flat = check_tall._flat(rig.readme)
    m = re.search(r"alle (\d+) sidene i byggeheftet og alle (\d+) i "
                  r"referanseheftet", flat)
    assert m, ("README sier ikke lenger «alle N sidene i byggeheftet og alle "
               "M i referanseheftet» - injeksjonen har mistet målet sitt og "
               "må skrives om")
    bygg, ref = m.group(1), m.group(2)
    assert bygg != ref, ("de to heftene er blitt like lange, og da kan ikke "
                         "denne injeksjonen skille gruppene fra hverandre - "
                         "bytt ut den ene setningen den perturberer")
    run_readme(rig, _sub(rig.readme, f"Byggeheftet på {bygg} sider",
                         f"Byggeheftet på {ref} sider"))


def inj_prose_keeps_an_old_number(rig):
    """Put a superseded stress back in the load-path appendix."""
    texts = dict(rig.prose)
    texts["ASSEMBLY.md"] = _sub(texts["ASSEMBLY.md"],
                                "σ = 2,17 MPa", "σ = 9,44 MPa")
    run_prose(rig, texts)


def inj_prose_invents_a_millimetre(rig):
    """Quote a length in the prose that no part and no fragment has."""
    texts = dict(rig.prose)
    texts["ASSEMBLY.md"] = _sub(texts["ASSEMBLY.md"], "1296 mm²",
                                "1297,3 mm av oversiden")
    run_prose(rig, texts)


def inj_prose_restores_a_hand_worked_capacity(rig):
    """Put the bearing capacity back the way vedlegg A worked it by hand.

    THIS IS THE ONE THE X13 ROUND EXISTS FOR. Until this round every bearing
    capacity in the load-path appendix was arithmetic done once by a person and
    then whitelisted, and «3,2 kN» sat in `PROSE_ALLOW` with «lagerkapasitet
    regnet av flate x f_c,90 i tillegget» beside it - which is to say the sweep
    was told not to look. The model divides 1296 mm2 by the same design value
    every other bearing row uses now (2,31, not the characteristic 2,5) and
    gets 3,0. Type the old number back in and the sweep has to bite; if it does
    not, the whitelist line was deleted without anything taking its place.
    """
    texts = dict(rig.prose)
    texts["ASSEMBLY.md"] = _sub(texts["ASSEMBLY.md"], "1296 mm² → 3,0 kN",
                                "1296 mm² → 3,2 kN")
    run_prose(rig, texts)


def inj_prose_moves_a_computed_stress(rig):
    """Nudge a bending stress the model now works off the C24 sheet.

    The bearing case above is a capacity; this is the other family - sigma =
    M/W on a member the model measures - and it was whitelisted for the same
    reason. 12,1 MPa is the ledger with somebody leaning hard on the table,
    vedlegg A's own governing bending row.

    [X14: the nudge was 12,4 and had to move to 12,6. 12,4 stopped being a
     miss the moment the cut list grew - 36x98 went from 11,88 to 12,42
     running metres, and the sweep's tolerance at one decimal is 0,05. That
     is the coarseness this file admits to, and it was the FALSIFIER that
     caught it drifting, not a reader.]
    """
    texts = dict(rig.prose)
    texts["ASSEMBLY.md"] = _sub(texts["ASSEMBLY.md"], "σ ≈ 12,1 MPa",
                                "σ ≈ 12,6 MPa")
    run_prose(rig, texts)


def inj_kappliste_hides_the_loose_mark(rig):
    """Let a loose piece that stands on the floor pass as an ordinary one.

    THIS IS THE X14 GUARD. The cut list is split by a rule - the room finishes
    what reaches a wall or stands on the floor - and the footrest is the first
    piece in this bed that stands on the floor and is NOT the room's, because
    nobody screws it down. That exception is written into the row itself, so
    the ink can be read back and held to it. Rub the mark out and the row says
    «kapp nå» while its own Z column says 0: the check has to bite, or the
    exception is a thing the code knows and the paper does not.
    """
    run_kappliste(rig, _sub(rig.kappliste, f" {T.LOOSE_MARK} |", " |"))


def inj_kappliste_moves_a_loose_piece_off_the_floor(rig):
    """Mark an ordinary workshop piece as loose.

    The other half of the same rule: the mark is not a licence. A row that
    carries it has to BE a piece standing on the floor and nowhere near a
    wall, and a piece that hangs in the air with the mark on it is a lie the
    other way round.

    X16: the victim used to be NAMED - «Bordkloss» - and X16 struck the
    bordkloss off the cut list with the seat rung that replaced it. A named
    injection whose target has left the building does not go red, it goes
    away, which is the one thing this harness must never do quietly. So the
    row is DERIVED: the first workshop row that is not already marked loose
    and whose own Z column does not start on the floor.
    """
    rows = [l for l in rig.kappliste.split("\n")
            if l.startswith("| ") and "**" in l and T.LOOSE_MARK not in l]
    row = next(l for l in rows
               if not l.rsplit("|", 2)[1].strip().startswith("0.."))
    cells = row.split("|")
    marked = "|".join([cells[0], f"{cells[1].rstrip()} {T.LOOSE_MARK} "]
                      + cells[2:])
    run_kappliste(rig, _sub(rig.kappliste, row, marked))


def inj_stale_value_comment(rig):
    """Move one digit in a value comment and ask the verifier to find it.

    The line is picked, not written down: the first `NAME = expr  # <number>`
    whose NAME really is a scalar at module level, so the case keeps working
    when the file is edited and never quietly perturbs a line the checker
    would have skipped anyway.
    """
    src = rig.M.VALUE_COMMENT_SOURCE
    # Anchored inside ONE line: `\s` would happily walk over a newline into
    # the next comment and perturb a number that is not on the name's line.
    for m in re.finditer(
            r"^([A-Z_][A-Z0-9_]*)([ \t]*=[ \t]*(?!=)[^\n]+?[ \t]+#[ \t]*)"
            r"(\d+)(?![\dxX×])", src, flags=re.M):
        val = vars(rig.M).get(m.group(1))
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            continue
        moved = m.group(1) + m.group(2) + str(int(m.group(3)) + 7)
        return run_value_comments(rig, _sub(src, m.group(0), moved))
    # NOT an AssertionError: the harness reads that as «the gate bit», and
    # «I could not find anything to break» is the opposite of a proof.
    raise RuntimeError("fant ingen verdikommentar å perturbere")


def inj_step_guide_forgets_the_seat_rung(rig):
    """Let step 6 stop saying WHICH rung the table plate lands on.

    The silence case, and X16 is what made it possible: before this round the
    plate's front seat was two blocks with their own part, their own joint and
    their own line in every list. Now it is a rung among rungs, and if the
    sentence goes, nothing else in the manual says which one.
    """
    seat = f"Trinn {rig.M.CLIMB_LANDING + 1} er STØTTETRINNET"
    run_seat_rung(rig, _sub(rig.bygg, seat, "Ett av trinnene er STØTTETRINNET"))


def inj_step_guide_misprints_the_seat_height(rig):
    """Type a different height for the one rung the table top rests on."""
    down = T._upright_top(rig.M) - rig.M.PANEL_UNDER_TABLE
    run_seat_rung(rig, _sub(rig.bygg, f"{T._fmt(down)} mm i begge ender",
                            f"{T._fmt(down + 12)} mm i begge ender"))


def _first_brace(rig, G):
    """The brace point the builder's own report names first, derived.

    Not «step 3» and not a label: the first of BRACE_REPORTED, matched against
    the bodies the rule fires on. If the rule ever stops firing on it the
    control has already gone red, so this cannot fail quietly.
    """
    braces = T.brace_points(G, rig.steps(G), T.cut_index(G))
    for n in sorted(braces):
        for rec in braces[n]:
            if any(T._match(T.BRACE_REPORTED[0], l) for l in rec["labels"]):
                return n, rec
    raise RuntimeError("X17 fyrer ikke lenger på den første av kroppene "
                       "byggherren skrev ned - injeksjonen har mistet målet")


def inj_brace_point_rubbed_out(rig):
    """Rub one brace point off the step guide and leave the body a hinge.

    THE SILENCE CASE, and it is the one this bijection exists for: a step that
    has stopped printing the paragraph looks exactly like a step that never
    owed one. The bed is unchanged, the body still turns on two screws 44 mm
    apart, and the only thing that moved is the paper.
    """
    _n, rec = _first_brace(rig, rig.G())
    run_brace_ink(rig, text=_sub(rig.bygg, "1. " + rec["text"] + "\n", ""))


def inj_brace_point_invented(rig):
    """...and the other way round: a step that holds everything it makes gets
    a brace point anyway. A licence to print the paragraph is not the same
    thing as the rule that decides where it goes."""
    n, rec = _first_brace(rig, rig.G())
    other = next(st["n"] for st in rig.bygg_steps
                 if st["n"] > n and st["do"]
                 and not any(T.BRACE_MARK in d for d in st["do"]))
    head = f"\n## Steg {other} — "
    before, after = rig.bygg.split(head, 1)
    mark = "**Slik gjør du:**\n\n"
    if mark not in after:
        raise RuntimeError(f"steg {other} har ingen «{mark.strip()}» - "
                           f"injeksjonen har mistet målet sitt")
    cut = after.index(mark) + len(mark)
    run_brace_ink(rig, text=(before + head + after[:cut]
                             + "1. " + rec["text"] + "\n" + after[cut:]))


def inj_body_is_held_after_all(rig):
    """Give a hinged body a second fixing out at its own free corner.

    This is the graph half of X17, and it is the injection that keeps the
    CRITERION honest rather than the ink: move one of the two screws that hold
    the body out to the corner that swings, and the anchors stop being a short
    line with a long lever - the rule says «held» and stops firing. Nothing on
    paper changes. What has to bite is the assert that holds the derived rule
    to the two bodies the builder wrote down after he had built the bed: if it
    does not, the rule has quietly stopped covering his report and the manual
    would go to the next builder without the point.
    """
    G = rig.G()
    _n, rec = _first_brace(rig, G)
    # BOTH ends, because the bed is mirrored: the sentence is one instruction
    # and the hinges are two, and fixing one of them proves nothing while the
    # other still fires.
    want = {}
    for hold in rec["mirrors"]:
        jid, _grips, _mine, anchor = hold["cloud"][0]
        want[(jid, anchor)] = hold["far"]
    specs, moved = [], set()
    for f in G.FASTENER_SPECS:
        key = (f["jid"], tuple(f["anchor"]))
        if key in want and key not in moved:
            f = dict(f, anchor=want[key])
            moved.add(key)
        specs.append(f)
    if moved != set(want):
        raise RuntimeError(f"fant ikke {sorted(set(want) - moved)} blant de "
                           f"plasserte festene - injeksjonen har mistet målet")
    G.FASTENER_SPECS = specs
    run_brace_report(rig, G)


def inj_jig_hole_moves(rig):
    """Flytt et hull 1 mm i modellen ETTER at arket er tegnet.

    Det er den ekte feilen: modellen endrer seg, arket blir liggende, og en
    sjablong som er én millimeter feil ser ut som en som er riktig.
    """
    RB, out = jig_sheets(rig)
    for _sh, _ink, _rulers, drawn, _boxes, _hy, _fy in out:
        for p, g in drawn:
            if p["jid"] != "J1":
                continue
            ref = g["fold"]["raw"]["refs"][0]
            ref["at"] = [v + 1.0 for v in ref["at"]]
            run_jig(rig, (RB, out))
            return
    raise RuntimeError("fant ikke J1 blant de tegnede mønstrene")


def inj_jig_ruler_short(rig):
    """Trykk en kontrollinjal 1 mm for kort - tallet ved enden står igjen."""
    RB, out = jig_sheets(rig)
    rulers = out[0][2]
    r = rulers[0]
    spec = r["spec"]
    r["last"] = ((r["last"][0] - 1.0, r["last"][1]) if not spec["vertical"]
                 else (r["last"][0], r["last"][1] - 1.0))
    run_jig(rig, (RB, out))


def inj_print_scaling_rubbed_out(rig):
    """Ta /PrintScaling ut av katalogen igjen - like mange bytes, så ingen
    offset i fila flytter seg og PDF-en er fortsatt lesbar. Da er den bare en
    PDF som åpner på «Tilpass til side», og sjablongene er ikke lenger 1:1."""
    import build_pdf as BP
    pdf = os.path.join(ROOT, "docs", "hanna.pdf")
    if os.path.exists(pdf):
        with open(pdf, "rb") as fh:
            data = fh.read()
    else:
        data = BP.set_print_scaling(minimal_pdf())
    hurt = data.replace(b"/PrintScaling /None", b"/PrintScalinX /None", 1)
    if hurt == data:
        raise RuntimeError("fant ingen /PrintScaling å fjerne - patchen har "
                           "byttet form og saken beviser ingenting")
    run_print_scaling(rig, hurt)


INJECTIONS = [
    ("bakrammen bæres inn gjennom en åpning like bred som seg selv",
     "X12 manøvrerbarhet", inj_frame_is_carried),
    ("ingen steg reiser den enheten som ikke kan bæres inn",
     "X12 manøvrerbarhet", inj_nobody_raises_it),
    ("taket senkes under diagonalen rammen sveiper",
     "X12 manøvrerbarhet", inj_ceiling_drops),
    ("steg 0 borer et hull i en ende som ennå har overmål",
     "X12 referanse-ende", inj_bench_bores_a_wall_end),
    ("et hull måles fra en fot som kappes etterpå",
     "X12 referanse-ende", inj_measured_from_the_foot),
    ("et veggfeste oppgir X-mål som fasit",
     "X12 stenderne", inj_wall_fixing_gets_an_x),
    ("et stegark trykker et annet tall enn det modellen målte",
     "X15 plasseringsmål", inj_step_sheet_prints_a_wrong_figure),
    ("et stegark slutter stille å tegne et mål steget skylder",
     "X15 plasseringsmål", inj_step_sheet_drops_a_measure),
    ("en høyde på et stegark måles oppover fra delen under",
     "X15 utgangspunkt", inj_step_dim_measured_upward),
    ("en høyde på et stegark tas fra gulvet",
     "X15 utgangspunkt", inj_step_dim_measured_from_the_floor),
    ("kapplista skjuler at en løs del står på gulvet",
     "X14 løse deler", inj_kappliste_hides_the_loose_mark),
    ("kapplista merker en verksteddel som løs",
     "X14 løse deler", inj_kappliste_moves_a_loose_piece_off_the_floor),
    ("README gjenforteller et artefakttall som har flyttet seg",
     "README-tall", inj_readme_retells_a_count),
    ("README siterer en linje modellen ikke lenger skriver",
     "README-tall", inj_readme_quotes_a_line_the_model_lost),
    ("README gir byggeheftet referanseheftets sidetall",
     "README-tall", inj_readme_swaps_the_two_booklets),
    ("håndprosaen beholder en spenning modellen har regnet om",
     "tallsveip", inj_prose_keeps_an_old_number),
    ("håndprosaen finner opp en millimeter",
     "tallsveip", inj_prose_invents_a_millimetre),
    ("lastveis-tillegget får tilbake sin håndregnede lagerkapasitet",
     "tallsveip", inj_prose_restores_a_hand_worked_capacity),
    ("en av vedlegg As bøyespenninger flyttes en tidel",
     "tallsveip", inj_prose_moves_a_computed_stress),
    ("en verdikommentar står igjen fra en gammel runde",
     "X10 verdikommentarer", inj_stale_value_comment),
    ("stegveiledningen slutter å si HVILKET trinn platen lander på",
     "X16 støttetrinnet", inj_step_guide_forgets_the_seat_rung),
    ("stegveiledningen setter støttetrinnet i feil høyde",
     "X16 støttetrinnet", inj_step_guide_misprints_the_seat_height),
    ("et avstivingspunkt viskes ut av et steg som fortsatt har en løs kropp",
     "X17 avstiving", inj_brace_point_rubbed_out),
    ("et steg som holder alt det bygger får et avstivingspunkt likevel",
     "X17 avstiving", inj_brace_point_invented),
    ("en løs kropp får et feste ute i det frie hjørnet og blir «stabil»",
     "X17 avstiving", inj_body_is_held_after_all),
    ("et hull flytter seg 1 mm i modellen etter at sjablongen er tegnet",
     "boresjablong", inj_jig_hole_moves),
    ("en kontrollinjal trykkes 1 mm kortere enn tallet ved enden",
     "boresjablong", inj_jig_ruler_short),
    ("«Faktisk størrelse» viskes ut av den trykte fila",
     "boresjablong", inj_print_scaling_rubbed_out),
]


def main():
    rig = Rig()
    for what, run in CONTROLS:
        try:
            run(rig)
        except AssertionError as exc:
            raise AssertionError(
                f"KONTROLLEN RYKER: «{what}» feller på uendret innhold, og da "
                f"beviser ingen feilinjisering noe som helst.\n{exc}") from exc
    bad = []
    for name, guard, inject in INJECTIONS:
        try:
            inject(rig)
        except AssertionError:
            continue                            # the gate bit - as it must
        except Exception as exc:                # noqa: BLE001
            bad.append(f"«{name}» ({guard}): injeksjonen kom aldri fram til "
                       f"asserten - {type(exc).__name__}: {exc}")
            continue
        bad.append(f"«{name}»: {guard} slapp den igjennom. Enten er regelen "
                   f"for løs, eller så måler den ikke det den sier")
    assert not bad, ("FALSIFISERING: "
                     + str(len(bad)) + " av " + str(len(INJECTIONS))
                     + " feilinjiseringer bet ikke:\n  " + "\n  ".join(bad))
    by_guard = {}
    for _n, guard, _f in INJECTIONS:
        by_guard[guard] = by_guard.get(guard, 0) + 1
    print(f"OK  FALSIFISERING: {len(CONTROLS)} vokterasserter kjørt rene på "
          f"dagens innhold, og {len(INJECTIONS)} navngitte feilinjiseringer "
          f"felte hver sin - "
          + " · ".join(f"{g} {n}" for g, n in sorted(by_guard.items()))
          + ". Ingen av dem rørte en fil på disk")


if __name__ == "__main__":
    main()
