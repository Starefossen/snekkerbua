![snekkerbua — der Hans gjør ting han (ennå) ikke kan](prosjekter/hanna/docs/img/hanna-poster@2x.png)

# snekkerbua

[![check](https://github.com/Starefossen/snekkerbua/actions/workflows/check.yml/badge.svg)](https://github.com/Starefossen/snekkerbua/actions/workflows/check.yml)

A workshop repo, one directory per project. Every project here is built the same
way: the model is parametric and is the only source of truth, the manual is
generated out of the solids rather than written beside them, and nothing is
allowed to exist until the machine has checked it.

## Prosjekter

| | | |
|---|---|---|
| <a href="prosjekter/hanna/"><img src="prosjekter/hanna/docs/img/hanna-hero.png" alt="HANNA" width="300"></a> | **[HANNA](prosjekter/hanna/)** — a convertible loft bed for one 199 cm alcove. 63 pieces of timber, 180 fasteners modelled as solids, and a print-ready assembly manual compiled from the model. | <img src="prosjekter/hanna/docs/img/hanna-turntable.gif" alt="One revolution" width="150"> |

## Felles

* **[PRAKSIS.md](PRAKSIS.md)** — the practices that hold across projects.
* **[UTSTYR.md](UTSTYR.md)** — the tool park and the buying plan. One workshop,
  one inventory, however many projects stand in it.

The short version of PRAKSIS:

* **One source.** Every number in the documentation *comes from* the model — not
  "was copied from". If two files have to agree about a number, the number is in
  the wrong place.
* **An assert is a relation**, derived from physics or a standard, never a
  restatement of a constant — and it says where to fix it when it breaks.
* **Rules, not cases.** How a thing is treated is a property of the thing,
  declared once. No `if` on a name, no switch somebody has to remember to flip.
* **A drawn choice is measured, not argued.** The proof is cut out of the
  finished page, and a tripwire assert measures the ink afterwards.
* **The derived artefacts are committed**, so `git diff --stat` after a build
  *is* the impact analysis.
* **Determinism is an assert, not an expectation.** `mise run check` runs the
  whole chain twice and demands byte-identical output.

## Quickstart

Needs [`mise`](https://mise.jdx.dev/). There is one task file, `mise.toml`, here
at the root, and each task runs with its own project as the working directory —
so a command is the same command wherever in the tree you type it:

```bash
mise run build      # model + every generated table and document
mise run montering  # re-draw the line art
mise run check      # run the whole chain twice, demand byte-identical output
mise run pdf        # the print-ready manual
```

The full round for HANNA is `mise run build && montering && check && pdf &&
usdz && film-check`. Per-project prerequisites and the rest of the tasks are in
the project's own README.

## Verify it yourself

Don't take the badge's word for it — three commands, from nothing:

```bash
git clone https://github.com/Starefossen/snekkerbua.git && cd snekkerbua
mise trust && mise run install   # python 3.11 + requirements.txt
mise run build && mise run montering && mise run check
```

`check` builds the whole chain twice and compares SHA-256 of every committed
derived file — the tables, `docs/MONTERING.md`, every drawing, `parts.tsv`.
*Byte-identical* here means exactly that: not "looks the same", not "same
numbers", the same bytes. If a run can produce two answers to the same
question, then a diff on the drawings is not evidence of anything, and the rest
of this repo is a story rather than a proof. The same gate runs on every push
— [`.github/workflows/check.yml`](.github/workflows/check.yml). Pushing a
`<prosjekt>-v*` tag runs a second one,
[`release.yml`](.github/workflows/release.yml), which builds the manual and the
3D models on macOS (the `.usdz` chain is Xcode-only) and hangs them off the
release.

You also need `rsvg-convert` for the PNGs (`brew install librsvg`, or
`apt install librsvg2-bin`); the workflow file is the exact list. `mise run
pdf` wants two more: a Chrome to print with and poppler to read the result back
with.

`git log --oneline` is the design journal — each commit is one decision, with
the reasoning in the body.
