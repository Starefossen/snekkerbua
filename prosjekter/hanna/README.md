# HANNA — a loft bed whose manual is compiled, not written

[![check](https://github.com/Starefossen/snekkerbua/actions/workflows/check.yml/badge.svg)](https://github.com/Starefossen/snekkerbua/actions/workflows/check.yml)

*The first project in [snekkerbua](../../README.md). Shared practices:
[PRAKSIS.md](../../PRAKSIS.md) · workshop inventory:
[UTSTYR.md](../../UTSTYR.md).*

![HANNA — loftseng med sofa, bord og ekstraseng under](docs/img/hanna-poster@2x.png)

<img src="docs/img/hanna-turntable.gif" alt="The finished bed, one revolution" width="440">

*48 frames off the solids, shot with `usdrecord` and assembled by
`tools/render_animasjon.py`. Deterministic: the frame index drives the camera,
so the same model gives the same bytes.*

A parametric loft bed in [build123d](https://github.com/gumyr/build123d) /
OpenCascade, built for one 199 cm alcove between two walls. The model is the
only source of truth: **every drawing, every table and all 68 pages of the
printed assembly manual are generated from the solids and machine-checked
before they are allowed to exist.** Nothing is hand-drawn and no number is
hand-transcribed.

<img src="docs/img/steg-05.png" alt="Step 5 of the generated assembly manual" width="560">

*Step 5, drawn by `tools/render_lineart.py`. The bed is a hidden-line
projection of the real B-rep solids. Every screw is a modelled body, exploded
along its own drive axis, in its true length. The letters, the fill code, the
counts in the inset panel and the sectioned corner are all derived — and a
build-failing assert measures the finished ink to prove each badge sits on the
fastener it names.*

---

## Key facts

| | |
|---|---|
| **Envelope** | 1990 × 836 × 1700 mm — a wall-to-wall fit in a 1990 mm alcove. Through-running parts are cut 1984 mm, because a 1990 mm board will not swing into a 1990 mm opening |
| **Timber** | **63 pieces** in **4 timber profiles** plus one 18 mm plywood sheet — 47.1 running metres. 32 of the 63 pieces come off a single profile (36×98) in four saw settings |
| **Steel** | **180 fasteners laid out across 17 joints**, **166 of them modelled as solid bodies** — head, countersink, shank and point, each with its own drive vector. **Not one head sits on a room-facing face**, and that is an assert |
| **Checks** | **385 asserts in the model** and 57 more in the tools, all build-failing. Screw directions are derived from physics (5 of 21 are forced by the thicknesses alone); screw counts must fit the face they stand on; every part must touch the assembly and clash with nothing |
| **Determinism** | `mise run check` runs the whole chain twice and demands **112 byte-identical artefacts** — the three films included, plus a hash stamp that fails the gate if they are older than the model they show. Determinism is an assert, not an expectation |
| **Output** | A **68-page print-ready PDF** in one command, plus a picture-only manual, a written build guide, six schematics, and STEP / STL / GLB / USDZ exports |
| **Standards** | Clearances, guard heights and the mattress thickness window come out of EN 747; edge distances and screw spacing out of Eurocode 5 |

The bed's *functional* design — a loft platform over a bench/table/spare-bed
that converts by moving one panel between two heights — is adapted from a
Hoppekids convertible loft bed. The structure, the dimensions, every joint and
all of the documentation here are original.

---

## How it works

```
generate_loftbed.py           the model: geometry, parts, fasteners, 385 asserts
  ├─ tools/gen_doc_tables.py  → docs/generated/*.md, docs/MONTERING.md, byggesteg.json
  ├─ tools/render_lineart.py  → docs/img/steg-NN.svg/.png   (+ check_coverage)
  │    ├─ tools/render_cutpage.py   step 0, the cutting plan
  │    └─ tools/render_panel.py     step 10, the loose panel
  ├─ tools/gen_glyphs.py      → fastener glyphs and pictograms
  ├─ tools/render_animasjon.py → docs/img/hanna-*.gif  (the three films)
  └─ tools/build_pdf.py       → docs/hanna.pdf
       └─ tools/render_pdf_matrix.py → docs/img/hanna-manual-sider.png
```

<img src="docs/img/hanna-bygg.gif" alt="The bed assembling itself, steps 1-11" width="560">

*The same eleven steps the manual is paginated from, read straight out of
`docs/generated/byggesteg.json`: each step's parts fly in along the direction
that step's text has you moving them, its screws appear once the wood has
landed, and the corner numeral is the number on the printed page. Nothing here
is a second description of the build — it is the build description, animated.*

**One source.** Any number that appears in the documentation *comes from* the
model — not "was copied from". The tools import `generate_loftbed.py`, read its
module globals and print. None of them defines geometry, and none of them
re-derives something the model already knows. The one hand-written document,
`docs/ASSEMBLY.md`, is allowed to name parts and cite joint numbers, but it may
never restate a dimension a generated fragment already carries; it links
instead. The rule behind it: **if two files have to agree about a number, the
number is in the wrong place.**

**The drawings are projections, not illustrations.** `render_lineart.py` puts
the actual solids through OpenCascade's hidden-line removal — no meshes — and
composes one page per build step: parts already standing in thin grey, the
parts you fit now in heavy black, the hidden run of a new part dashed. That is
the convention a picture-only assembly manual uses, the kind that comes in the
box with flat-pack furniture, and it is used here because the model can satisfy
it exactly.

**A rule/constraint layout engine, not tuned coordinates.** `tools/layout.py`
knows nothing about beds. It answers the two questions every annotation asks —
*how big* and *where is there room* — from rules rather than from numbers
somebody liked the look of. Every stroke width, radius, margin and point size
on a step page is a multiple of one length, `pen = bbox diagonal / 400`, so the
whole pen set follows what is being drawn. Badge placement is a scored search
over an occupancy field, with contact to the named body priced above any amount
of white paper.

**The manual cannot lie.** The asserts are almost never "this number is that
number" — they are relations, derived from something outside the drawing, and
they say where to fix it when they break. Four families:

* **Screw length.** A through screw must clear the part it is driven from and
  end inside the other: `t(from) < length < t(from) + t(into)`. Where only one
  direction satisfies that, the direction is *derived* and the joint table only
  gets to agree.
* **Fits the face.** A row of `n` screws needs `(n-1)·4d + 2·3d` mm of real
  contact face. Switching this on deleted four screw counts that had stood
  unchallenged.
* **Completeness.** Every part in exactly one step; every joint present as
  often as the table says; the shopping list equal to the fasteners actually
  placed; and every step page must *draw* at least one of each fastener type it
  lists, with the drawn count matching the printed count. That last one catches
  silent drawings — a part listed but never shown being fixed.
* **Orientation.** A bracket screwed into wood is not necessarily the right way
  up. A bracket that *bears* something must have its horizontal leg driven
  upward into the underside of what it carries.

And because the derived artefacts are committed — so that `git diff --stat`
after a build *is* the impact analysis — the chain itself has to be
reproducible. `mise run check` runs it twice and compares checksums. A failure
there is never a model change: it is an unsorted `dict`, a timestamp, an
`id()`-ordering or an order-dependent float sum.

That same gate runs on every push to `main` — the badge at the top is
[`.github/workflows/check.yml`](../../.github/workflows/check.yml), which is
`build`, `montering` and `check` on a machine that starts with nothing. To run
it yourself: **[Verify it yourself](../../README.md#verify-it-yourself)**.

---

## Quickstart

Needs [`mise`](https://mise.jdx.dev/). Everything else is
`pip install -r requirements.txt` (build123d, markdown) plus `rsvg-convert` for
the PNGs. The PDF additionally wants a headless Chrome to print with and
poppler to read the result back with — the page numbers in the table of
contents are looked up in the finished PDF, not guessed:
`brew install librsvg poppler` (or `apt install librsvg2-bin poppler-utils`).

The task file is `mise.toml` at the repo root and every task already runs in
this directory, so these work unchanged from anywhere in the tree:

```bash
mise run build      # model + all generated tables + docs/MONTERING.md
mise run montering  # re-draw the line art in docs/img/
mise run check      # run the whole chain twice, demand byte-identical output
mise run pdf        # docs/hanna.pdf, 68 pages, print-ready
```

| Task | What it does |
|---|---|
| `build` | Builds and validates the model, exports it, writes every fragment in `docs/generated/` and `docs/MONTERING.md` |
| `build-full` | Same plus the slow deliverables: `.glb` and the whole-model hidden-line `.svg` projections |
| `montering` | Draws the cover and one line-art page per build step into `docs/img/` |
| `check` | Determinism assert: two full runs, 112 artefacts, byte-identical or fail |
| `pdf` | Assembles `docs/hanna.pdf` from the checked-in documents (no build123d needed) |
| `schematics` | Renders `docs/schematics/*.svg` to PNG for proofreading |
| `usdz` | Converts the meshes to `.usdz` for Quick Look / Xcode / AR, one material per colour group |
| `render`, `render-validate` | Shaded previews and the five design-validation views (macOS `usdrecord`) |
| `montering-skyggelagt` | Shaded reference renders of the same build steps |
| `view`, `view-usdz` | Open the model in FreeCAD / Quick Look |

---

## Project map

Everything below lives in `prosjekter/hanna/` and every path is relative to it.

| Path | |
|---|---|
| `generate_loftbed.py` | The model. Geometry, the joint table, the fasteners as solids, and the asserts |
| `tools/` | Everything that reads the model: doc tables, line art, cut page, panel page, glyphs, PDF, USD helpers |
| `docs/generated/` | Machine-written, never edited by hand: cut list, buying list, key dimensions, hardware list, screw directions, step text, `byggesteg.json` |
| `docs/img/`, `docs/schematics/` | The committed drawings — so the manual is readable and printable on a machine with none of this toolchain |
| `docs/hanna.pdf` | The 68-page print manual. Deliberately untracked — the tooling is in git, the binary is one `mise run pdf` away |
| `parts.tsv` | Tracked regression snapshot: label, colour group and bounding box of every part, both panel modes. A diff on it is the diff on the model |
| `v1/` | The first alcove bunk-bed frame, kept for history |

---

## The build documents

These are **in Norwegian** — they are what someone standing at the saw actually
reads.

<img src="docs/img/hanna-manual-sider.png" alt="The first nine pages of the printed manual, three by three" width="760">

*The first nine of the 68 printed pages, read straight back out of
`docs/hanna.pdf` by `tools/render_pdf_matrix.py`: the cover, the contents, two
pages of conventions and safety, the fastener list, the parts list, the
landscape cutting plan, and the first two build steps. Every page on that sheet
was compiled — nothing on it was laid out by hand. The finished PDF hangs off
the [`hanna-v1.0`
release](https://github.com/Starefossen/snekkerbua/releases/tag/hanna-v1.0) if
you would rather read it than build it.*

* **[docs/MONTERING.md](docs/MONTERING.md)** — the picture manual. Twelve steps
  (0–11), one drawing per step, almost no words. Generated.
* **[docs/ASSEMBLY.md](docs/ASSEMBLY.md)** — the reasoning: tools, timber,
  every joint J1…J15, the build order and why it has to be that order,
  mattress and cushions, safety, and the load-path appendix. The one
  hand-written file.
* **[docs/generated/](docs/generated/)** — cut list, buying list with a
  board-by-board cutting plan, key dimensions, hardware list and screw
  directions.
* `docs/hanna.pdf` — all of the above, imposed for print. Not committed; run
  `mise run pdf` and it appears, identical, from the tracked documents.

## For whoever changes the model

Two files, both in Norwegian, neither part of the printed manual.

* **[../../PRAKSIS.md](../../PRAKSIS.md)** — the shared practices of the
  workshop: the single-source rule, what makes an assert worth writing, rules
  instead of cases, the drawing conventions that hold across projects, and why
  determinism is an assert.
* **[docs/PRAKSIS.md](docs/PRAKSIS.md)** — HANNA's own: the chain out of
  `generate_loftbed.py`, the four assert families and the standards they come
  from, the box invariant and its one wedge-shaped exception, where the
  boundary between steel and timber runs, and every convention in this
  manual's picture language — fill codes, badge rules, the bracket chain, the
  icon spec — with the reason behind each.

## Limits

This is one product, not a furniture framework. Everything is axis-aligned box
furniture: all cuts are 90°, there is no mitre and no curve in the bed, and the
drawing engine assumes rectangular solids in an orthographic projection. The
model is parametric in the sense that the dimensions are constants with asserts
holding them together — change the alcove width or the main board profile and
the chain will tell you loudly what no longer fits — but it is not a
configurator, and the bed is wall-side-specific and not reversible.
