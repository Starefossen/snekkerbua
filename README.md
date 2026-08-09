# Alcove-Style Bunk Bed Frame

This project contains Python scripts using the `build123d` library to
programmatically generate 3D models of bed frames and export them as STEP,
STL, GLB, USDZ and SVG. The loft bed it builds is called **HANNA**.

* `v1/generate_bed_frame.py` — an alcove-style bunk bed frame.
* `generate_loftbed.py` — HANNA, the loft bed, with a convertible sofa / table
  / bed underneath. It is built for a niche: fitted between two walls and
  standing against the back wall, screwed fast to it. There are no guard rails
  at the back, because the wall is the barrier there. Boards and posts are
  unified on **36×98**, the single dimension most of the bed is cut from, so
  the saw takes four settings for the whole main board. Four corner posts
  carry the mattress platform, with the slats lying **flush on top** of the
  side rails, so the mattress lands exactly on the slat ends at both edges.
  Each end has a single 48×98 end beam under the side rails and is otherwise
  **fully open above the mattress**. The ladder sits flat against the front
  rail, in the same plane as the front posts: 36×48 uprights, four 48×73
  treads on cleat blocks, and a climb-through gap in both front guard bands,
  as wide as the ladder itself. The front bench rail stops at the sofa ends,
  so the whole floor between the benches is open. Between the benches an 18 mm
  panel, stiffened by two 48×73 battens on edge underneath, rests on wood at
  bench height (bed mode) or table height (table mode). Every part is
  validated to touch the rest of the assembly and to clash with nothing (see
  the checks in the build output). Widths, depths, heights and every part
  length live in [docs/generated/nokkelmal.md](docs/generated/nokkelmal.md)
  and [docs/generated/kappliste.md](docs/generated/kappliste.md).

`parts.tsv` is the tracked regression snapshot: label, colour group and
bounding box for every part, both panel modes included. It is rewritten by
`mise run build`, so a diff on it is the diff on the model. Every other
generated *model* file is gitignored.

## Building it — read this first

* **[docs/ASSEMBLY.md](docs/ASSEMBLY.md)** — the build guide. Tools, hardware,
  every joint (J1…J15), the build order and why it has to be that order,
  mattress and cushions, safety, and the load-path appendix. In Norwegian.
* **[docs/MONTERING.md](docs/MONTERING.md)** — the same build, one picture per
  step, drawn as black-and-white line art with almost no words. Same step
  numbers as the text guide.
* **[docs/PRAKSIS.md](docs/PRAKSIS.md)** — for whoever changes the model or
  the drawings, not for whoever builds the bed: the single-source rule, what
  makes an assert worth writing here, how the fasteners are modelled and where
  the boundary between steel and timber runs, the drawing conventions, and how
  to regenerate everything. Deliberately not in the printed manual.

Both are driven by the model. `mise run build` regenerates the tables in
`docs/generated/` (cut list, buying list, key dimensions, hardware list, the
step-by-step text and the machine-readable step data) straight from
`generate_loftbed.py`, and `docs/ASSEMBLY.md` links to them rather than
restating any dimension. `mise run montering` re-draws the line art in
`docs/img/` — the cover drawing and one drawing per build step, projected out
of the model itself by `tools/render_lineart.py`. Those files **are**
committed, because the guide has to be readable and printable on a machine
with none of this toolchain installed.

## Setup & Usage

This project uses `mise` for environment management and task running. 

1. Ensure you have `mise` installed.
2. In your terminal, navigate to this directory.
3. You can now use the built-in mise tasks to run the project.

To see available tasks:
```bash
mise run
```

### Available Tasks:

* **Install dependencies** (run automatically when building):
  ```bash
  mise run install
  ```
* **Generate the 3D models** (`.step`, `.stl`, `.glb`, `.svg`):
  ```bash
  mise run build
  ```
* **Convert the models to `.usdz`** (runs `build` first):
  ```bash
  mise run usdz
  ```
* **Render shaded PNG previews** of both modes (runs `usdz` first):
  ```bash
  mise run render      # -> loftbed_bed_mode.png, loftbed_table_mode.png
  ```
* **Draw the assembly manual's line art** (runs `build` first, needs
  `rsvg-convert` for the PNGs):
  ```bash
  mise run montering   # -> docs/img/hanna-hero.*, docs/img/steg-NN.*
  ```
* **Shaded reference renders of the same steps** (macOS: `usdrecord` + Swift):
  ```bash
  mise run montering-skyggelagt   # -> docs/img/skyggelagt/, not committed
  ```
* **Preview the model natively on macOS**:
  ```bash
  mise run view        # STEP in FreeCAD
  mise run view-usdz   # USDZ in Quick Look
  ```

## Viewing the `.usdz` Files

`mise run usdz` produces `loftbed_bed_mode.usdz` and `loftbed_table_mode.usdz`.
These open directly in Xcode and in macOS Quick Look — no extra software needed:

```bash
open loftbed_bed_mode.usdz     # Quick Look / Preview
open -a Xcode loftbed_bed_mode.usdz
```

They are also what you want for AR on an iPhone or iPad: AirDrop the file, or
put it on a web page, and AR Quick Look will place the bed in the room at 1:1
scale. The conversion re-orients the model to the USD conventions (metres,
origin centred on the floor) and passes `usdchecker --arkit`.

The pipeline is `generate_loftbed.py` → one `.stl` per colour group →
`tools/mesh_to_usda.swift` → `usdcat` → `usdzip`. All the converter tools ship
with macOS, so there is nothing extra to install. The `.usdz` carries **five
named meshes with five `UsdPreviewSurface` materials** (posts, rails, boards,
panel, mattress — the mattress is translucent). The per-group `.stl`
intermediates are written to a scratch directory (`$TMPDIR/loftbed_groups`,
override with `LOFTBED_GROUP_DIR`), never into the repo. The per-part names
and the cut list live in the `.step` and `.glb` files.

## Orientation of the exported files

* `.step` keeps the CAD convention: millimetres, **Z-up**, floor at Z = 0.
* `.stl`, `.glb` and `.usdz` are **Y-up**, so the bed stands upright by
  default in Quick Look, Preview and Xcode. For the STL the rotation is baked
  into the vertex data; `export_gltf` writes it onto the root node itself.

## Shaded previews

`mise run render` uses `usdrecord` (part of the USD tools that ship with
macOS) plus `tools/make_render_stage.py`, which wraps the `.usdz` in a
throwaway stage with a 3/4-view camera. The result is `loftbed_bed_mode.png`
and `loftbed_table_mode.png` in the repo root.

## Line drawings

`tools/render_lineart.py` (`mise run montering`) is what draws the assembly
manual. It projects the solids themselves — no meshes — through OpenCascade's
hidden-line removal, and writes one SVG per build step in which the parts
already standing are thin grey and the parts you fit in that step are heavy
black, plus `docs/img/hanna-hero.svg`, the all-black cover drawing of the
finished bed. `rsvg-convert` turns each one into the PNG the manual embeds.
Whole-model hidden-line `.svg` projections of both modes are a separate,
slower deliverable from `mise run build-full`.

## Viewing the `.step` File

A STEP (`.step` or `.stp`) file is a standard 3D CAD file format. To view it on your Mac, you can use any of the following options:

1. **FreeCAD** (Recommended for Engineering): 
   A free, powerful, open-source 3D CAD modeler. You can download it at [freecad.org](https://www.freecad.org/) or install it via Homebrew (`brew install --cask freecad`). Once installed, open FreeCAD and simply go to `File > Open` and select the `bed_frame.step` file.

2. **Visual Studio Code**:
   If you use VS Code, you can install the **OCP CAD Viewer** extension. This allows you to view STEP files right inside your code editor.

3. **Online Viewers** (No installation required):
   You can drag and drop your `.step` file into a free online viewer, such as:
   - [3DViewerOnline](https://www.3dvieweronline.com/)
   - [CAD Exchanger](https://cadexchanger.com/view/)

4. **eDrawings Viewer for Mac**:
   A free dedicated desktop application from Dassault Systèmes for viewing 3D CAD files.
