"""Render one isometric image per build step for docs/MONTERING.md.

Reads docs/generated/byggesteg.json - the step description emitted by
tools/gen_doc_tables.py during `mise run build` - and, for every step that
asks for an image, runs the same mesh chain the .usdz deliverables use:

    per-step .stl groups   (written by generate_loftbed.py)
      -> tools/mesh_to_usda.swift   two named UsdPreviewSurface materials
      -> tools/make_render_stage.py adds the camera from the step's hint
      -> usdrecord                  shaded PNG

The two materials are the point: everything already standing is painted a
pale grey, and the parts this step is about are painted in the highlight
colour, so a builder can see at a glance what changes.

The stage is centred on the bounding box of the meshes it is given. Every
step from 1 onwards already contains the four corner posts, so that box is
the same to within a couple of centimetres in depth all the way through and
the bed does not jump between images.

Usage:
    python tools/render_steps.py [--width 1400] [--out docs/img]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP_JSON = os.path.join(ROOT, "docs", "generated", "byggesteg.json")
GROUP_DIR = os.environ.get(
    "LOFTBED_GROUP_DIR", os.path.join(tempfile.gettempdir(), "loftbed_groups"))
STEP_DIR = os.path.join(GROUP_DIR, "steps")


def run(cmd, **kw):
    res = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if res.returncode != 0:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{res.stdout}\n{res.stderr}")
    return res.stdout


def main(argv):
    width = "1400"
    out_dir = os.path.join(ROOT, "docs", "img")
    only = None
    i = 1
    while i < len(argv):
        if argv[i] == "--width":
            width = argv[i + 1]; i += 2
        elif argv[i] == "--out":
            out_dir = argv[i + 1]; i += 2
        elif argv[i] == "--step":
            only = int(argv[i + 1]); i += 2
        else:
            sys.exit(__doc__)
    for tool in ("swift", "usdrecord"):
        if shutil.which(tool) is None:
            sys.exit(f"{tool} not found - the step images need the macOS USD "
                     f"tools and a Swift toolchain. Run `mise run build` "
                     f"first, then `mise run montering` on a Mac.")

    with open(STEP_JSON, encoding="utf-8") as fh:
        data = json.load(fh)
    os.makedirs(out_dir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="loftbed_steps_")
    made = []
    try:
        for st in data["steps"]:
            n = st["n"]
            if not st["image"] or not st["camera"]:
                continue
            if only is not None and n != only:
                continue
            manifest = os.path.join(STEP_DIR, f"steg_{n:02d}.groups")
            if not os.path.exists(manifest):
                sys.exit(f"missing {manifest} - run `mise run build` first")
            with open(manifest, encoding="utf-8") as fh:
                groups = [ln for ln in fh.read().split("\n") if ln.strip()]

            asset = os.path.join(work, f"steg_{n:02d}.usda")
            stage = os.path.join(work, f"steg_{n:02d}_stage.usda")
            png = os.path.join(out_dir, f"steg-{n:02d}.png")
            az, elev, dist = st["camera"]

            run(["swift", os.path.join(ROOT, "tools", "mesh_to_usda.swift"),
                 asset] + groups, cwd=ROOT)
            run([sys.executable,
                 os.path.join(ROOT, "tools", "make_render_stage.py"),
                 asset, stage, str(az), str(elev), str(dist)])
            run(["usdrecord", "--camera", "Cam", "--imageWidth", width,
                 "--complexity", "high", "--colorCorrectionMode", "sRGB",
                 stage, png])
            made.append(png)
            print(f"  steg {n:2d}  az {az:>3} elev {elev:>2} d {dist}  -> {png}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"\n{len(made)} step images in {out_dir}")


if __name__ == "__main__":
    main(sys.argv)
