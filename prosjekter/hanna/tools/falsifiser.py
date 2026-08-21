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
        self.pool = check_tall.achievable(self.M, self.log)
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            self.readme = fh.read()
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


def run_value_comments(rig, source=None):
    src = rig.M.VALUE_COMMENT_SOURCE if source is None else source
    stale, checked, _skip = rig.M.stale_value_comments(src, vars(rig.M))
    assert checked > 100, "verdikommentar-verifikatoren leste nesten ingenting"
    assert not stale, f"foreldede verdikommentarer: {stale[:3]}"


CONTROLS = [
    ("X12 manøvrerbarhet per byggesteg", run_units),
    ("X12 referanse-ende mot overmål", run_datum),
    ("README-tallene", run_readme),
    ("tallsveipet over håndprosaen", run_prose),
    ("X10 verdikommentarene", run_value_comments),
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
    """Re-datum a ladder hole to the foot - the end that is still 15 mm long."""
    run_datum(rig, bygg=_sub(rig.bygg,
                             "1377 / 1401 mm fra toppen",
                             "1377 / 1401 mm fra nedre ende"))


def inj_wall_fixing_gets_an_x(rig):
    """Give a wall fixing an X measurement, as if the studs were known."""
    run_datum(rig, bygg=_sub(
        rig.bygg,
        "| **J14** 6× Veggfeste | bakre sidevange 48×98 × 1984, forsiden "
        "(mot rommet) | etter stender — minst i begge ender og på midten |",
        "| **J14** 6× Veggfeste | bakre sidevange 48×98 × 1984, forsiden "
        "(mot rommet) | 165 mm fra ytterenden |"))


def inj_readme_retells_a_count(rig):
    """Let the README go on saying an artefact count that has moved."""
    m = re.search(r"krever \*\*(\d+) byte-identiske artefakter\*\*",
                  check_tall._flat(rig.readme))
    n = int(m.group(1))
    run_readme(rig, _sub(rig.readme, f"**{n} byte-identiske",
                         f"**{n + 1} byte-identiske"))


def inj_readme_quotes_a_line_the_model_lost(rig):
    """Keep quoting a printed line the model no longer prints."""
    run_readme(rig, _sub(rig.readme, "181 festemidler plassert i 22 ledd",
                         "181 festemidler plassert i 23 ledd"))


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
    """
    texts = dict(rig.prose)
    texts["ASSEMBLY.md"] = _sub(texts["ASSEMBLY.md"], "σ ≈ 12,1 MPa",
                                "σ ≈ 12,4 MPa")
    run_prose(rig, texts)


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
    ("README gjenforteller et artefakttall som har flyttet seg",
     "README-tall", inj_readme_retells_a_count),
    ("README siterer en linje modellen ikke lenger skriver",
     "README-tall", inj_readme_quotes_a_line_the_model_lost),
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
