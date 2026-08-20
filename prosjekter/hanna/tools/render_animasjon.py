#!/usr/bin/env python3
"""The three films: a turntable, the panel mechanism, and the build-up.

Same chain as every other shaded picture in this repo - the solids out of
generate_loftbed.py, meshed per colour group, handed to tools/mesh_to_usda.swift
and shot with usdrecord - with one addition: a film needs the SAME asset in
every frame with a few of its prims MOVED, so the geometry is exported once and
each frame is a four-line USD layer that references it and authors an `over`:

    def "Asset" (references = @film.usda@)
    {
        over "w03_rails" { xformOp:translate = ... }   # this step, flying in
        over "Materials" { over "f03" { ... opacity = 0.6 } }   # its screws
    }

Nothing in the model is touched. The displacement is an ILLUSTRATION TRANSFORM
authored in the frame's own layer, and it is derived from the model's own
numbers, so a film cannot drift away from the bed it shows.

    hanna-turntable.gif   the finished bed, 360 degrees, ladder side first
    hanna-mekanisme.gif   the loose panel from the bed seat to the table seat
    hanna-bygg.gif        steps 1-11 of docs/generated/byggesteg.json, in order

DETERMINISM. Nothing here reads a clock or a random number: the frame index
drives the camera, the displacement and the fade, and the palette is computed
from the frames themselves. Two runs on the same model give byte-identical
GIFs, which is what makes `git diff` on them a consequence analysis - see
docs/PRAKSIS.md section 5. The frames themselves are scratch and are written
outside the repo ($TMPDIR/loftbed_film, override with LOFTBED_FILM_DIR).

STALENESS. The films are expensive and are NOT rebuilt by `mise run build`, so
each one records the sha256 of the sources it was rendered from in
docs/img/hanna-filmer.stamp. `--check` (mise run film-check, wired into
`mise run check`) re-hashes those sources in a couple of milliseconds and fails
if a film is older than the model it claims to show.

FRAME SIZE. Everything is shot at --render-width and delivered at --width:
the frames are cropped to the one box the whole film uses and then scaled down
to the delivered size, so the downscale is the antialiasing. Rendering at the
delivered size instead gives visibly harder edges on the slat ends.

Usage:
    python tools/render_animasjon.py [turntable|mekanisme|bygg|all]
                                     [--width N] [--render-width N] [--no-mp4]
    python tools/render_animasjon.py --check
"""

import argparse
import hashlib
import math
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
IMG_DIR = os.path.join(ROOT, "docs", "img")
STEP_JSON = os.path.join(ROOT, "docs", "generated", "byggesteg.json")
PARTS_TSV = os.path.join(ROOT, "parts.tsv")
STAMP = os.path.join(IMG_DIR, "hanna-filmer.stamp")
FILM_DIR = os.environ.get(
    "LOFTBED_FILM_DIR", os.path.join(tempfile.gettempdir(), "loftbed_film"))

# The manual's highlight colour - the same (0.94, 0.42, 0.10) the per-step
# renders paint "the parts this step is about" in. A film uses it for the same
# thing: whatever is moving is orange, and it goes back to its own timber
# colour the moment it is seated.
HIGHLIGHT = (0.94, 0.42, 0.10)

# Every film and the sources it is a function of. `--check` re-hashes exactly
# these: a change to a step's text must not force a re-render of the turntable,
# which never reads byggesteg.json.
FILM_SOURCES = {
    "turntable": {"parts": PARTS_TSV},
    "mekanisme": {"parts": PARTS_TSV},
    "bygg": {"parts": PARTS_TSV, "steg": STEP_JSON},
}
FILM_ORDER = ["turntable", "mekanisme", "bygg"]
GIF_NAME = {name: f"hanna-{name}.gif" for name in FILM_ORDER}

# Fallbacks in order; the first one that exists wins. macOS only, like the rest
# of the shaded chain (usdrecord + swift).
NUMERAL_FONTS = [
    ("/System/Library/Fonts/Helvetica.ttc", 1),
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
    ("/System/Library/Fonts/HelveticaNeue.ttc", 2),
]


# ---------------------------------------------------------------------------
# PLUMBING
# ---------------------------------------------------------------------------
def run(cmd, **kw):
    res = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if res.returncode != 0:
        sys.exit(f"FAILED: {' '.join(str(c) for c in cmd)}\n"
                 f"{res.stdout}\n{res.stderr}")
    return res.stdout


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


_MODEL = None


def model():
    """generate_loftbed as a module. Importing it builds and validates the bed
    and writes its exports - the same thing tools/gen_doc_tables.py does."""
    global _MODEL
    if _MODEL is None:
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        import generate_loftbed
        _MODEL = generate_loftbed
    return _MODEL


def stage_module():
    if TOOLS not in sys.path:
        sys.path.insert(0, TOOLS)
    import make_render_stage
    return make_render_stage


# ---------------------------------------------------------------------------
# THE MODEL'S FRAME AND THE ASSET'S FRAME
# ---------------------------------------------------------------------------
# generate_loftbed works in mm, Z-up, X along the wall. The meshes are exported
# through G.Y_UP, which is Ry(180) * Rx(-90), so a model point (x, y, z) lands
# at (-x, z, y) before mesh_to_usda.swift centres the footprint and scales to
# metres. Only the ROTATION matters for a displacement vector - the centring is
# a translation and cancels - so this is the whole conversion:
def to_asset(vec_mm):
    """A model-space displacement (dx, dy, dz) in mm as an asset-space
    displacement in metres."""
    dx, dy, dz = vec_mm
    return (-dx * 0.001, dz * 0.001, dy * 0.001)


def model_bbox(group_solids):
    """The model-space box mesh_to_usda.swift centres its output on: the union
    of everything handed to it in one call."""
    lo = [1e18, 1e18, 1e18]
    hi = [-1e18, -1e18, -1e18]
    for solids in group_solids:
        for p in solids:
            for i, (a, b) in enumerate(p.extents):
                lo[i] = min(lo[i], a)
                hi[i] = max(hi[i], b)
    return tuple((lo[i], hi[i]) for i in range(3))


def point_to_asset(p, bbox):
    """A model-space POINT in asset coordinates - the same turn as to_asset()
    plus the centring the swift tool applies (footprint centred, floor at 0)."""
    (x0, x1), (y0, y1), (z0, _) = bbox
    return (((x0 + x1) / 2 - p[0]) * 0.001, (p[2] - z0) * 0.001,
            (p[1] - (y0 + y1) / 2) * 0.001)


def rigid_matrix(roll_deg, t_asset, pivot_asset):
    """USD matrix4d for `roll about the model Y axis through pivot, then
    translate`. A model roll about Y is an asset roll about Z, because the
    export turns model +Y into asset +Z. USD uses row vectors, so the linear
    block is the transpose."""
    a = math.radians(roll_deg)
    c, s = math.cos(a), math.sin(a)
    px, py, pz = pivot_asset
    rp = (c * px - s * py, s * px + c * py, pz)
    d = (px + t_asset[0] - rp[0], py + t_asset[1] - rp[1],
         pz + t_asset[2] - rp[2])
    rows = [(c, s, 0.0, 0.0), (-s, c, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0),
            (d[0], d[1], d[2], 1.0)]
    return "( " + ", ".join(
        "(" + ", ".join(f"{v:.9g}" for v in row) + ")" for row in rows) + " )"


# ---------------------------------------------------------------------------
# ASSET: one .usda holding every group a film can move, in one shared frame
# ---------------------------------------------------------------------------
def build_asset(work, groups, name="film"):
    """groups: [(prim name, (r, g, b, a), [solids])] -> path to the .usda.

    ONE call to mesh_to_usda.swift for all of them, on purpose: the tool
    centres its output on the bounding box of everything it is given, so
    groups written in separate calls would not share an origin and could not
    be moved relative to each other.
    """
    from build123d import Compound, export_stl
    G = model()
    args = []
    for prim, rgba, solids in groups:
        if not solids:
            continue
        path = os.path.join(work, f"{prim}.stl")
        members = [p.moved(G.Y_UP) for p in solids]
        if all(getattr(p, "group", None) == "fasteners" for p in solids):
            export_stl(Compound(children=members), path,
                       tolerance=G.FASTENER_MESH_TOL,
                       angular_tolerance=G.FASTENER_MESH_ANG)
        else:
            export_stl(Compound(children=members), path)
        args.append(f"{prim}={','.join(f'{c:.4g}' for c in rgba)}={path}")
    asset = os.path.join(work, f"{name}.usda")
    run(["swift", os.path.join(TOOLS, "mesh_to_usda.swift"), asset] + args,
        cwd=ROOT)
    return asset


# ---------------------------------------------------------------------------
# FRAME: a tiny layer that references the asset and overrides a few prims
# ---------------------------------------------------------------------------
def _over(indent, name, body):
    pad = " " * indent
    inner = "".join(f"{pad}    {line}\n" for line in body)
    return f'{pad}over "{name}"\n{pad}{{\n{inner}{pad}}}\n\n'


def _mesh_overs(mesh_ov):
    out = ""
    for prim in sorted(mesh_ov):
        o = mesh_ov[prim]
        body = []
        if not o.get("visible", True):
            body.append('token visibility = "invisible"')
        t = o.get("translate")
        if t and any(abs(c) > 1e-9 for c in t):
            body.append("double3 xformOp:translate = "
                        f"({t[0]:.6g}, {t[1]:.6g}, {t[2]:.6g})")
            body.append('uniform token[] xformOpOrder = ["xformOp:translate"]')
        if o.get("matrix"):
            body.append(f"matrix4d xformOp:transform = {o['matrix']}")
            body.append('uniform token[] xformOpOrder = ["xformOp:transform"]')
        if body:
            out += _over(8, prim, body)
    return out


def _material_overs(mat_ov):
    if not mat_ov:
        return ""
    inner = ""
    for prim in sorted(mat_ov):
        o = mat_ov[prim]
        body = []
        if "color" in o:
            c = o["color"]
            body.append("color3f inputs:diffuseColor = "
                        f"({c[0]:.6g}, {c[1]:.6g}, {c[2]:.6g})")
        if "opacity" in o:
            body.append(f"float inputs:opacity = {o['opacity']:.6g}")
        surface = _over(12, "Surface", body)
        inner += f'        over "{prim}"\n        {{\n{surface}        }}\n\n'
    return f'        over "Materials"\n        {{\n{inner}        }}\n\n'


def write_frame(path, asset, cam, mesh_ov=None, mat_ov=None):
    """cam is (azimuth, elevation, distance, target)."""
    mrs = stage_module()
    az, elev, dist, target = cam
    a, e = math.radians(az), math.radians(elev)
    direction = (math.sin(a) * math.cos(e), math.sin(e),
                 math.cos(a) * math.cos(e))
    eye = tuple(t + dist * d for t, d in zip(target, direction))
    overs = _mesh_overs(mesh_ov or {}) + _material_overs(mat_ov or {})
    text = f"""#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "World"
{{
    def "Asset" (
        prepend references = @{os.path.abspath(asset)}@
    )
    {{
{overs}    }}

    def Camera "Cam"
    {{
        float2 clippingRange = (0.05, 100)
        float focalLength = {mrs.FOCAL_LENGTH}
        float horizontalAperture = {mrs.H_APERTURE}
        float verticalAperture = {mrs.V_APERTURE}
        matrix4d xformOp:transform = {mrs.look_at_matrix(eye, target)}
        uniform token[] xformOpOrder = ["xformOp:transform"]
    }}
}}
"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def shoot(stage, png, width):
    run(["usdrecord", "--camera", "Cam", "--imageWidth", str(width),
         "--complexity", "high", "--colorCorrectionMode", "sRGB", stage, png])


# ---------------------------------------------------------------------------
# EASING - frame index in, displacement out. No clock, no state.
# ---------------------------------------------------------------------------
def ease_out(t):
    """Fast away, gentle into the seat - a part being placed by hand."""
    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t):
    """Smoothstep. Used on every leg of the mechanism path."""
    return t * t * (3.0 - 2.0 * t)


# ---------------------------------------------------------------------------
# ASSEMBLY: frames -> GIF (+ .mp4)
# ---------------------------------------------------------------------------
def _pil():
    try:
        from PIL import Image, ImageChops, ImageDraw, ImageFont
    except ImportError:
        sys.exit("Pillow is missing - `pip install pillow` (it is in "
                 "requirements.txt; run `mise run install`)")
    return Image, ImageChops, ImageDraw, ImageFont


def load_frames(paths):
    """usdrecord writes RGBA with a transparent ground; the manual is printed
    on white, so the films are too."""
    Image, _, _, _ = _pil()
    out = []
    for p in paths:
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        out.append(Image.alpha_composite(bg, im).convert("RGB"))
    return out


def union_box(frames, margin=12):
    """One crop box for the whole film - the union of what every frame draws.

    Per-frame crops would make the bed swim; the union is fixed for the film
    and only throws away margin no frame ever uses.
    """
    Image, ImageChops, _, _ = _pil()
    w, h = frames[0].size
    white = Image.new("RGB", (w, h), (255, 255, 255))
    box = None
    for im in frames:
        b = ImageChops.difference(im, white).convert("L") \
            .point(lambda v: 255 if v > 6 else 0).getbbox()
        if b is None:
            continue
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                     max(box[2], b[2]), max(box[3], b[3]))
    if box is None:
        return (0, 0, w, h)
    x0 = max(0, box[0] - margin)
    y0 = max(0, box[1] - margin)
    x1 = min(w, box[2] + margin)
    y1 = min(h, box[3] + margin)
    # .mp4 wants even dimensions (yuv420p subsamples by two).
    if (x1 - x0) % 2:
        x1 = x1 - 1 if x1 == w else x1 + 1
    if (y1 - y0) % 2:
        y1 = y1 - 1 if y1 == h else y1 + 1
    return (x0, y0, x1, y1)


def numeral_font(size):
    _, _, _, ImageFont = _pil()
    for path, index in NUMERAL_FONTS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size, index=index)
    sys.exit("no numeral font found - the step overlay needs one of: "
             + ", ".join(p for p, _ in NUMERAL_FONTS))


def draw_numeral(im, number, title):
    """The big corner numeral of the printed page, on the film frame.

    Same idea as .step-num in tools/build_pdf.py: the number is the biggest
    thing on the page and the title sits under it in text size.
    """
    _, _, ImageDraw, _ = _pil()
    d = ImageDraw.Draw(im)
    big = numeral_font(max(34, im.height // 7))
    small = numeral_font(max(11, im.height // 34))
    x, y = max(10, im.width // 40), max(8, im.height // 40)
    d.text((x, y), str(number), font=big, fill=(26, 26, 26))
    bb = d.textbbox((x, y), str(number), font=big)
    d.text((x + 2, bb[3] + im.height // 90), title, font=small,
           fill=(90, 90, 90))
    return im


def write_gif(frames, path, duration_ms, colors=96):
    """One palette for the whole film - a per-frame palette flickers, and a
    shared one is what lets GIF's inter-frame optimisation do any work.

    A hold is the same image object repeated in `frames`; GIF says that with
    ONE frame and a longer delay, so the repeats are collapsed here instead of
    being written out as identical frames Pillow would drop anyway.
    """
    Image, _, _, _ = _pil()
    step = max(1, len(frames) // 10)
    sample = frames[::step]
    w, h = frames[0].size
    strip = Image.new("RGB", (w, h * len(sample)))
    for i, im in enumerate(sample):
        strip.paste(im, (0, i * h))
    pal = strip.quantize(colors=colors, method=Image.MEDIANCUT)
    # dither=NONE: these renders are flat-shaded facets, so dithering only
    # sprays noise into every frame and doubles the file.
    uniq, delay = [], []
    for im in frames:
        if uniq and im is uniq[-1]:
            delay[-1] += duration_ms
            continue
        uniq.append(im)
        delay.append(duration_ms)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in uniq]
    q[0].save(path, save_all=True, append_images=q[1:], loop=0,
              duration=delay, optimize=True, disposal=1)
    return path


def write_mp4(frames, path, fps, work):
    if shutil.which("ffmpeg") is None:
        return None
    seq = os.path.join(work, "seq")
    os.makedirs(seq, exist_ok=True)
    for i, im in enumerate(frames):
        im.save(os.path.join(seq, f"f{i:05d}.png"))
    if os.path.exists(path):
        os.remove(path)
    run(["ffmpeg", "-nostdin", "-loglevel", "error",
         "-fflags", "+bitexact", "-flags", "+bitexact",
         "-framerate", f"{fps:.6g}", "-i", os.path.join(seq, "f%05d.png"),
         "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", path])
    return path


def scale_to(frames, width):
    """Downscale the cropped frames to the delivered width - this is where the
    antialiasing comes from, so it is a real step and not a convenience."""
    Image, _, _, _ = _pil()
    w, h = frames[0].size
    if w <= width:
        return frames
    new = (width, max(2, int(round(h * width / w))))
    new = (new[0] - new[0] % 2, new[1] - new[1] % 2)
    return [im.resize(new, Image.LANCZOS) for im in frames]


def finish(name, frames, duration_ms, work, want_mp4, colors=96):
    """Crop, assemble, report. `frames` is the play order, holds included."""
    out_gif = os.path.join(IMG_DIR, GIF_NAME[name])
    write_gif(frames, out_gif, duration_ms, colors=colors)
    made = [out_gif]
    if want_mp4:
        mp4 = write_mp4(frames, os.path.join(IMG_DIR, f"hanna-{name}.mp4"),
                        1000.0 / duration_ms, work)
        if mp4:
            made.append(mp4)
    for p in made:
        print(f"  {os.path.relpath(p, ROOT)}  {len(frames)} frames  "
              f"{frames[0].width}x{frames[0].height}  "
              f"{os.path.getsize(p) / 1e6:.2f} MB")
    return made


# ---------------------------------------------------------------------------
# FILM 1 - TURNTABLE
# ---------------------------------------------------------------------------
TURNTABLE_FRAMES = 48
TURNTABLE_ELEV = 21.0
TURNTABLE_DIST = 3.6


def film_turntable(work, width, render_width, want_mp4):
    """The finished bed, one revolution, starting ladder-side-on.

    Azimuth 0 looks the ladder in the face (the export turns the front towards
    +Z - see tools/make_render_stage.py), so frame 0 is the picture the README
    hero is, and the loop closes on it.
    """
    G = model()
    groups = [(g, tuple(G.GROUP_COLORS[g]),
               [p for p in G.display_parts(G.panel_bed) if p.group == g])
              for g in G.GROUP_ORDER]
    asset = build_asset(work, groups, "turntable")

    pngs = []
    for i in range(TURNTABLE_FRAMES):
        az = 360.0 * i / TURNTABLE_FRAMES
        stage = os.path.join(work, f"tt_{i:03d}.usda")
        png = os.path.join(work, f"tt_{i:03d}.png")
        write_frame(stage, asset, (az, TURNTABLE_ELEV, TURNTABLE_DIST,
                                   (0.0, 0.80, 0.0)))
        shoot(stage, png, render_width)
        pngs.append(png)
    print(f"  {len(pngs)} frames, azimuth 0..360 in "
          f"{360.0 / TURNTABLE_FRAMES:g} degree steps")

    frames = load_frames(pngs)
    box = union_box(frames, margin=10)
    frames = scale_to([im.crop(box) for im in frames], width)
    return finish("turntable", frames, 80, work, want_mp4, colors=64)

# ---------------------------------------------------------------------------
# FILM 2 - THE MECHANISM, AND THE PROOF THAT THE PATH EXISTS
# ---------------------------------------------------------------------------
# THE FIRST CUT OF THIS FILM WAS A LIE and it is worth writing down why. It
# lifted the panel straight out of the bed seat, carried it forward out of the
# bed and lowered it into the table seat - and it drove the sheet 166 mm
# through both ladder uprights on the way, because the panel cannot pass a
# 320 mm ladder opening and the wall is behind it. Nothing checked it.
#
# THE SECOND CUT WAS TRUE AND UNCOMFORTABLE. It found a path, and the path was
# nine handgrips long and went through a slot with no clearance in it at all:
# the unit is 91 mm tall and the corridor it had to cross was 91 mm high, so
# the only way through was a 3 degree ROLL, held for two legs, over a bench,
# above a child's head. The film proved the mode change was POSSIBLE. It also
# proved, to anyone who watched it twice, that nobody would do it twice.
#
# WHAT CHANGED IN THE WOOD (v13, and both of these are asserted in the model,
# not assumed here):
#   * K1 cut the rung blocks from 73 to 36 mm - the length of the upright face
#     they are screwed to. The 37 mm that came off never touched anything;
#     what it DID do was hang into this corridor and pull its ceiling down by
#     the blocks' full 48 mm of height. The ceiling is now the back table
#     ledger's underside at 409, and the slot is TRANSFER_SLOT = 114 mm from
#     the bench slat tops at 295 - 23 mm of daylight round a 91 mm unit.
#     Those four are the v13 numbers and they are kept because they are what
#     the story is about; X1/X9 have since lifted the ledger and re-cut the
#     unit, so TRANSFER_SLOT, the slat tops and PANEL_UNIT_H all read
#     differently now. The live ones are the model's - see the X9 note below.
#   * K2 narrowed the panel 652 -> 574, which does not touch this corridor at
#     all (it is a height and a depth question) but does make the unit lighter
#     and the sideways move 39 mm shorter at each end.
#
# SO THE PATH IS RE-SEARCHED, AND IT IS FLAT. No roll, seven handgrips:
#
#   1  up        150 mm          into the middle of the slot, flat
#   2  slide      599 mm left     out over the bench, level, 59 mm off the
#                                 slat tops and 59 mm under the ledger
#   3  out         50 mm +Y       the rear edge off the table ledger's line
#   4  up        319 mm           past the ledger and rung 2, in the open bay
#   5  back        50 mm -Y       over the seat line again
#   6  slide      599 mm right    back across, now ABOVE the bordkloss band
#   7  down        84 mm          within the asserted 100, into the table seat
#
# X9 re-measured every one of those legs off the model - the numbers above are
# the v16 ones. What CHANGED is leg 6: the band it crosses in used to have
# rung 2's top as its floor, because rung 2 carried the plate; the desk's front
# seat is the two bordklosser at 682, so the floor went up with them and the
# band is 118 mm for an 86 mm unit. Legs 1-3 are the same move over the same
# bench; the ceiling over that bench went UP 140 mm with the ledger, so the
# flat carry has 59 mm of daylight where it had 34.
#
# Legs 3 and 5 are the two that look like fussing and are not: the back table
# ledger runs the whole width of the bed at Y -48..0, so the panel's rear edge
# has to step off its line before it can rise past it, wherever in X you are
# standing. Everything else is one lift, one carry, one carry back, one lower.
#
# EVERY FRAME IS CHECKED. mech_probe() puts the five moving boxes through a
# separating-axis test against every fixed part in the bed and against the
# wall plane, and the film REFUSES TO RENDER if any frame interpenetrates. The
# tightest number on the whole path is +2.0 mm, and that is not a coincidence:
# it is PANEL_FIT, the clearance the design was drawn with. So the film is not
# an illustration of the mode change - it is the feasibility proof for it.
#
# THAT SENTENCE WAS TRUE OF THE DESIGN AND FALSE OF THE PROBE until this round.
# What the probe actually reported was 0,00 mm on the back bench rail, because
# the guide batten's rear face lies ON that rail's front face in the seat and
# stays there for the first few millimetres of the lift. It was reading the
# SEAT and calling it a near miss. mech_probe() now measures which pairs touch
# in the two seats and leaves those out of the reported minimum - they are
# still collision-checked like everything else - and with that fixed the
# number the note has claimed all along is the number it prints.
MECH_ROLL = 0.0             # deg. It was 3.0, found by search, and it was the
                            # only thing that got a 91 mm unit through a 91 mm
                            # slot. K1 made the slot 114, so the search comes
                            # back with zero and the probe below is what says
                            # so - the oriented-box machinery is kept exactly
                            # because it is what can tell a flat path from a
                            # lucky one.
MECH_CLEAR = 11.0           # mm of daylight the film keeps off every measured
                            # limit it does not have to touch
MECH_CAM = (330.0, 26.0, 4.3, (0.0, 0.50, 0.05))
# frames per leg, leg 1..7
MECH_LEG_FRAMES = [7, 14, 4, 9, 4, 14, 7]


def _part(G, label):
    return next(p for p in G.parts if p.label == label)


def mech_keys(G):
    """[(roll deg, (dx, dy, dz) mm)] - the eight poses the path runs through.

    Everything here is read off the model. Nothing in it is a choice any more
    except which side of the bed the panel comes out on; the roll that used to
    be the one free parameter is zero, and the two cruise heights are simply
    the middles of the two free bands the model measures."""
    unit_h = G.PANEL_UNIT_H                                 # 86  [X3: was 91]
    # LEG 1 - up into the middle of the transfer slot. The slot's two walls
    # are measured in the model (K1): bench slat tops to the ledger underside.
    lift = (G.TRANSFER_FLOOR + G.TRANSFER_CLEAR / 2) - G.BATTEN_Z0_BED   # 150
                                                            # [was 120.5]
    assert lift <= G.INSERT_CLEAR["bed_mode"], (
        f"the first lift is {lift:.0f} mm and the asserted free run out of "
        f"the bed seat is only {G.INSERT_CLEAR['bed_mode']}")
    assert G.TRANSFER_CLEAR / 2 >= MECH_CLEAR - 1, (
        f"the flat carry has {G.TRANSFER_CLEAR / 2:.0f} mm above and below - "
        f"under the {MECH_CLEAR:g} mm of daylight this film insists on, and "
        f"the path would have to go back to a roll")
    # LEG 2 - left until the panel's own left edge is MECH_CLEAR off the back
    # corner post's inner face. That also takes its right edge well clear of
    # the rung ends at 835 - which is the point of the move.
    side = -(G.PANEL_X0 - G.POST_W - MECH_CLEAR)            # -599
    assert G.PANEL_X1 + side < _part(G, "Ladder Rung_1").extents[0][0], \
        "the sideways move does not take the panel clear of the rung ends"
    # LEG 3 - far enough forward that the panel's rear edge is off the table
    # ledger's front face on the way up: the ledger is RAIL_T deep, plus fit.
    out = G.RAIL_T + G.PANEL_FIT                            # 50
    # LEG 4/6 - the free band the panel crosses the ladder in on the way back,
    # with the unit centred in it. Before K1 the ceiling here was a rung BLOCK;
    # the blocks are out of the panel's depth band now, so it is rung 3 itself.
    # X9 MOVED THE FLOOR OF THIS BAND, and this is the one place in the film
    # that had to be told: it used to be rung 2's top, because rung 2 was what
    # carried the plate at table height. The plate is a desk now and its front
    # seat is the two BORDKLOSSER at PANEL_UNDER_TABLE - higher than rung 2 and
    # standing in exactly this corridor - so the floor is the bordkloss top.
    # The band is 118 mm for an 86 mm unit; the model asserts it (X9).
    band = (G.PANEL_UNDER_TABLE, _part(G, "Ladder Rung_3").extents[2][0])
    cruise = (band[0] + (band[1] - band[0] - unit_h) / 2) - G.BATTEN_Z0_BED
    # LEG 7 - and down.
    drop = cruise - G.PANEL_MODE_LIFT
    assert drop <= G.INSERT_CLEAR["table_mode"], (
        f"the final descent is {drop:.0f} mm and the asserted free run into "
        f"the table seat is only {G.INSERT_CLEAR['table_mode']}")
    return [
        (MECH_ROLL, (0.0, 0.0, 0.0)),              # seated, bed mode
        (MECH_ROLL, (0.0, 0.0, lift)),             # 1 up, into the slot
        (MECH_ROLL, (side, 0.0, lift)),            # 2 across, flat, over the bench
        (MECH_ROLL, (side, out, lift)),            # 3 rear edge off the ledger
        (MECH_ROLL, (side, out, cruise)),          # 4 up past ledger and rung 2
        (MECH_ROLL, (side, 0.0, cruise)),          # 5 back over the seat line
        (MECH_ROLL, (0.0, 0.0, cruise)),           # 6 across, above rung 2
        (MECH_ROLL, (0.0, 0.0, G.PANEL_MODE_LIFT)),   # 7 down into the table seat
    ]


def mech_path(G):
    """One (roll, translation) per frame, eased leg by leg."""
    keys = mech_keys(G)
    out = [keys[0]]
    for (r0, t0), (r1, t1), n in zip(keys, keys[1:], MECH_LEG_FRAMES):
        for i in range(1, n + 1):
            u = ease_in_out(i / n)
            out.append((r0 + (r1 - r0) * u,
                        tuple(a + (b - a) * u for a, b in zip(t0, t1))))
    return out


# --- the probe -------------------------------------------------------------
# Every wooden part in this bed is an axis-aligned box and the panel unit is
# five boxes, so the exact test for "do these two solids interpenetrate" is a
# separating-axis test between one rotated box and one axis-aligned one. The
# screws are left out on purpose: they live inside the wood they join, so their
# boxes add nothing the wood does not already say.
def _sat_gap(A, B):
    """Signed separation of two oriented boxes, (centre, half, axes) each:
    the largest gap over the 15 candidate separating axes. > 0 is daylight."""
    ca, ha, aa = A
    cb, hb, ab = B
    d = tuple(cb[i] - ca[i] for i in range(3))
    axes = list(aa) + list(ab)
    for u in aa:
        for v in ab:
            c = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
                 u[0] * v[1] - u[1] * v[0])
            n = math.sqrt(sum(x * x for x in c))
            if n > 1e-6:
                axes.append(tuple(x / n for x in c))
    best = -1e18
    for ax in axes:
        ra = sum(ha[i] * abs(sum(aa[i][k] * ax[k] for k in range(3)))
                 for i in range(3))
        rb = sum(hb[i] * abs(sum(ab[i][k] * ax[k] for k in range(3)))
                 for i in range(3))
        best = max(best, abs(sum(d[k] * ax[k] for k in range(3))) - ra - rb)
    return best


def _box(extents):
    return (tuple(sum(e) / 2 for e in extents),
            tuple((e[1] - e[0]) / 2 for e in extents),
            ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)))


def _moved_box(extents, pivot, roll, t):
    """The AABB `extents` rolled `roll` degrees about the model Y axis through
    `pivot` and then translated by `t`."""
    a = math.radians(roll)
    ca, sa = math.cos(a), math.sin(a)
    c, h, _ = _box(extents)
    d = tuple(ci - pi for ci, pi in zip(c, pivot))
    d = (d[0] * ca + d[2] * sa, d[1], -d[0] * sa + d[2] * ca)
    c = tuple(p + q + r for p, q, r in zip(pivot, d, t))
    axes = ((ca, 0.0, -sa), (0.0, 1.0, 0.0), (sa, 0.0, ca))
    return (c, h, axes)


def mech_probe(G, path, tol=1e-6):
    """(worst gap, what, frame) over the whole path. Negative = the film would
    show wood through wood, and that is a build failure.

    WHAT "WORST" MEANS, and this was wrong in the file for a whole round. The
    number the film used to report as "the tightest pass, +2.0 mm = PANEL_FIT"
    was not that at all: it measured 0,00 mm on the back bench rail, at frame
    1, and it did so on the old path too. The zero is real and it is not a
    near miss - the guide batten's rear face IS the back bench rail's front
    face (M4: the battens stop ON that plane), so those two pieces of wood are
    in contact in the seat and stay in contact for the first few millimetres
    of the lift. Reporting that as the clearance of the manoeuvre says nothing
    about the manoeuvre.

    So the pairs that TOUCH IN EITHER SEAT are identified first and excluded
    from the reported minimum - they are the seats, and a seat is supposed to
    touch. They are still collision-checked on every frame like everything
    else; what changes is only which number gets called "the tightest pass".
    """
    unit = [G.panel_bed] + list(G.battens_bed)
    moving = {id(p) for p in unit}
    fixed = [(p.label, p.extents) for p in G.parts if id(p) not in moving]
    pivot = (G.WALL_SPAN / 2, 0.0, G.BATTEN_Z0_BED)

    # The seat pairs: (moving part, fixed part) in contact in the bed seat or
    # in the table seat, i.e. the wood the unit is designed to land on and lie
    # against. Measured, not listed.
    seat_pairs = set()
    for k in (0, len(path) - 1):
        roll, t = path[k]
        for i, p in enumerate(unit):
            A = _moved_box(p.extents, pivot, roll, t)
            for j, (_label, ex) in enumerate(fixed):
                if _sat_gap(A, _box(ex)) <= tol:
                    seat_pairs.add((i, j))

    worst = (1e18, None, -1)
    wall = 1e18
    for k, (roll, t) in enumerate(path):
        for i, p in enumerate(unit):
            A = _moved_box(p.extents, pivot, roll, t)
            ca, ha, aa = A
            ymin = ca[1] - sum(ha[i2] * abs(aa[i2][1]) for i2 in range(3))
            wall = min(wall, ymin - G.WALL_Y)
            for j, (label, ex) in enumerate(fixed):
                g = _sat_gap(A, _box(ex))
                if g < -tol:
                    sys.exit(
                        f"MEKANISMEFILMEN GÅR GJENNOM TRE: frame {k} puts the "
                        f"panel unit {-g:.1f} mm inside '{label}'.\nThe path "
                        f"in mech_keys() is not a path the panel can take. Fix "
                        f"the path - or, if the model changed, this is a "
                        f"design finding and the mode change no longer works.")
                if g < worst[0] and (i, j) not in seat_pairs:
                    worst = (g, label, k)
    # The rear edge of the panel IS the wall plane - it lies on it in both
    # seats - so touching is the design and only going THROUGH it is a fault.
    if wall < -tol:
        sys.exit(f"MEKANISMEFILMEN GÅR INN I VEGGEN: {-wall:.1f} mm behind "
                 f"Y = {G.WALL_Y}. The room is not a place to put a panel.")
    return worst


def film_mekanisme(work, width, render_width, want_mp4):
    G = model()
    path = mech_path(G)
    gap, who, frame = mech_probe(G, path)
    assert MECH_ROLL == 0.0, \
        "the path is not flat any more - if a roll came back, say so in the " \
        "note above and in ASSEMBLY J13, because it is a two-person move"
    print(f"  probe: {len(path)} frames over {len(MECH_LEG_FRAMES)} legs, "
          f"roll {MECH_ROLL:g} deg - a FLAT carry.\n"
          f"         no part of the panel unit inside any part of the bed; "
          f"tightest pass {gap:+.2f} mm on '{who}' (frame {frame}) - the "
          f"drawn fit is {G.PANEL_FIT} mm.\n"
          f"         the carry itself has {G.TRANSFER_CLEAR / 2:.1f} mm of "
          f"daylight over and under it in a {G.TRANSFER_SLOT:g} mm slot "
          f"({G.TRANSFER_FLOOR_WHO} → {G.TRANSFER_CEILING_WHO})")

    panel_unit = [G.panel_bed] + list(G.battens_bed) \
        + list(G.panel_fasteners(G.panel_bed))
    moving = {id(p) for p in panel_unit}
    fixed = [p for p in G.display_parts(G.panel_bed) if id(p) not in moving]

    groups = [(g, tuple(G.GROUP_COLORS[g]),
               [p for p in fixed if p.group == g]) for g in G.GROUP_ORDER]
    # The travelling unit in the manual's highlight colour, its own screws in
    # steel - one prim each, so one `over` moves the whole sub-assembly.
    groups += [("unit", HIGHLIGHT + (1.0,),
                [G.panel_bed] + list(G.battens_bed)),
               ("unitfast", tuple(G.GROUP_COLORS["fasteners"]),
                list(G.panel_fasteners(G.panel_bed)))]
    asset = build_asset(work, groups, "mekanisme")
    bbox = model_bbox(g[2] for g in groups)
    pivot = point_to_asset((G.WALL_SPAN / 2, 0.0, G.BATTEN_Z0_BED), bbox)

    pngs = []
    for i, (roll, t) in enumerate(path):
        xform = rigid_matrix(roll, to_asset(t), pivot)
        stage = os.path.join(work, f"mk_{i:03d}.usda")
        png = os.path.join(work, f"mk_{i:03d}.png")
        write_frame(stage, asset, MECH_CAM,
                    mesh_ov={"unit": {"matrix": xform},
                             "unitfast": {"matrix": xform}})
        shoot(stage, png, render_width)
        pngs.append(png)
    print(f"  {len(pngs)} frames over {len(MECH_LEG_FRAMES)} legs")

    frames = load_frames(pngs)
    box = union_box(frames, margin=10)
    frames = scale_to([im.crop(box) for im in frames], width)
    # A GIF loops, so the film runs the path out and back: the panel goes to
    # the table seat, waits, and comes home the way it came. No extra renders
    # - the return leg is the same frames read backwards, which is also the
    # honest thing to show, because the way back IS the way out reversed.
    play = ([frames[0]] * 5 + frames + [frames[-1]] * 8 + frames[-2:0:-1])
    return finish("mekanisme", play, 85, work, want_mp4, colors=64)


# FILM 3 - THE BUILD-UP
# ---------------------------------------------------------------------------
# WHERE EACH STEP COMES IN FROM. One direction per step, in model space, and
# it is the direction the step's own text has you moving the wood: the back
# frame is built flat and pushed back against the wall, the end beams and posts
# come in from their own ends of the room, the rails and the ladder go on from
# the front, and everything that lands on a rail top - slats, panel, mattress -
# comes down from above. `mirror` means the sign is per part, taken from which
# side of the bed's centre line the part is on, so the two end beams close in
# on the frame instead of both sliding the same way.
#
#   axis   0 = X (along the wall), 1 = Y (wall -> ladder), 2 = Z (up)
STEP_ENTRY = {
    1:  (1, "+", "bakrammen legges inn mot veggen"),
    2:  (1, "+", "reises og skrus fast - ingen ny del"),
    3:  (0, "mirror", "endebjelker og stolper inn fra hver sin ende"),
    4:  (1, "+", "sidevangen legges på forfra"),
    5:  (1, "+", "benkevanger og føtter forfra"),
    6:  (1, "+", "stigen settes på forfra"),
    7:  (2, "+", "benkespilene og endespilene legges ned"),
    8:  (2, "+", "køyespilene legges ned på vangene"),
    9:  (1, "+", "rekkverksbordene forfra"),
    10: (2, "+", "platen går rett ned i setet"),
    11: (2, "+", "madrassen og de fire putene legges på"),
}
ENTRY_OFFSET = 300.0        # mm, the brief's 250-350 band
BYGG_FLY = 10               # frames of travel
BYGG_POP = 3                # frames the step's screws fade in over
BYGG_HOLD = 1               # one frame of the finished step
BYGG_BEAT = 6               # a step that places no wood (step 2)
BYGG_TAIL = 8               # frames of the finished bed at the end
BYGG_AZ = (336.0, 312.0)    # 24 degrees of orbit over the whole film
BYGG_ELEV = 24.0
BYGG_DIST = 4.6


def step_solids(G, steps):
    """{n: ([wood], [fasteners])} off byggesteg.json, on the model's solids."""
    universe = {p.label: p for p in
                list(G.parts) + [G.panel_bed] + list(G.battens_bed)
                + [G.mattress] + list(G.CUSHIONS_BED)}
    out = {}
    for st in steps:
        wood = [universe[l] for l in st["labels"]]
        fast = [s for s in G.FASTENERS if s.spec["jid"] in st["joints"]]
        out[st["n"]] = (wood, fast)
    return out


def _entry_vector(G, part, axis, sign):
    v = [0.0, 0.0, 0.0]
    if sign == "mirror":
        mid = sum(part.extents[axis]) / 2
        centre = G.WALL_SPAN / 2 if axis == 0 else 0.0
        v[axis] = ENTRY_OFFSET * (1.0 if mid >= centre else -1.0)
    else:
        v[axis] = ENTRY_OFFSET * (1.0 if sign == "+" else -1.0)
    return tuple(v)


def film_bygg(work, width, render_width, want_mp4):
    import json
    G = model()
    with open(STEP_JSON, encoding="utf-8") as fh:
        steps = [st for st in json.load(fh)["steps"] if 1 <= st["n"] <= 11]
    solids = step_solids(G, steps)

    # One prim per (step, colour group) plus one per step's fasteners. Landed
    # wood keeps its own timber colour - the film has to end on the real bed,
    # not on a grey one - and the step in progress is painted over in the
    # highlight colour by the frame layer.
    groups, wood_prims, fast_prim, prim_entry = [], {}, {}, {}
    # label -> the prim that part ended up in. A step with no wood of its own
    # still gets a beat and highlights what it ACTS on (step 2 raises the back
    # frame), and that highlight has to find the prim step 1 put it in.
    label_prim = {}
    for st in steps:
        n = st["n"]
        wood, fast = solids[n]
        axis, sign, _ = STEP_ENTRY[n]
        # One prim per (colour group, entry vector). A `mirror` step splits in
        # two - the two end beams come in from opposite ends and one prim can
        # only carry one translate - and every other step is one prim per
        # colour group.
        bins = {}
        for p in wood:
            v = _entry_vector(G, p, axis, sign)
            bins.setdefault((p.group, v), []).append(p)
        prims = []
        for g in G.GROUP_ORDER:
            for (grp, v), members in sorted(
                    ((k, m) for k, m in bins.items() if k[0] == g),
                    key=lambda kv: kv[0][1]):
                side = "" if len(bins) == 1 else f"_{len(prims)}"
                prim = f"w{n:02d}_{g}{side}"
                groups.append((prim, tuple(G.GROUP_COLORS[g]), members))
                prims.append(prim)
                prim_entry[prim] = v
                for p in members:
                    label_prim[p.label] = prim
        wood_prims[n] = prims
        if fast:
            prim = f"f{n:02d}"
            groups.append((prim, tuple(G.GROUP_COLORS["fasteners"]), fast))
            fast_prim[n] = prim
    asset = build_asset(work, groups, "bygg")

    # Which prims exist at all, so a frame can hide everything not yet placed.
    all_prims = [g[0] for g in groups]

    plan = []           # (step, phase, i_in_phase, n_in_phase)
    for st in steps:
        n = st["n"]
        wood, fast = solids[n]
        if wood:
            plan += [(n, "fly", i, BYGG_FLY) for i in range(BYGG_FLY)]
            if n in fast_prim:
                plan += [(n, "pop", i, BYGG_POP) for i in range(BYGG_POP)]
            plan += [(n, "hold", i, BYGG_HOLD) for i in range(BYGG_HOLD)]
        else:
            plan += [(n, "beat", i, BYGG_BEAT) for i in range(BYGG_BEAT)]

    pngs, numerals = [], []
    for k, (n, phase, i, tot) in enumerate(plan):
        az = BYGG_AZ[0] + (BYGG_AZ[1] - BYGG_AZ[0]) * k / max(1, len(plan) - 1)
        st = next(s for s in steps if s["n"] == n)
        mesh_ov, mat_ov = {}, {}

        placed = set()
        for s in steps:
            if s["n"] < n:
                placed.update(wood_prims[s["n"]])
                if s["n"] in fast_prim:
                    placed.add(fast_prim[s["n"]])
        for prim in all_prims:
            if prim in placed:
                continue
            if prim in wood_prims[n] and phase != "beat":
                continue
            if prim == fast_prim.get(n) and phase in ("pop", "hold"):
                continue
            mesh_ov[prim] = {"visible": False}

        if phase == "fly":
            t = ease_out(i / BYGG_FLY)          # i = 0 is the full offset
            for prim in wood_prims[n]:
                v = prim_entry[prim]
                mesh_ov[prim] = {"translate": to_asset(
                    tuple(c * (1.0 - t) for c in v))}
        if phase == "pop":
            mat_ov[fast_prim[n]] = {"opacity": (i + 1) / BYGG_POP}
        # The step in progress wears the manual's highlight colour.
        highlight = set(wood_prims[n]) if phase != "beat" else {
            label_prim[l] for l in st["highlight"] if l in label_prim}
        for prim in sorted(highlight):
            mat_ov.setdefault(prim, {})["color"] = HIGHLIGHT

        stage = os.path.join(work, f"by_{k:04d}.usda")
        png = os.path.join(work, f"by_{k:04d}.png")
        write_frame(stage, asset, (az, BYGG_ELEV, BYGG_DIST, (0.0, 0.80, 0.0)),
                    mesh_ov=mesh_ov, mat_ov=mat_ov)
        shoot(stage, png, render_width)
        pngs.append(png)
        numerals.append((n, st["title"]))

    # One last frame with nothing highlighted and no numeral: the film has to
    # END on the bed, not on an orange mattress.
    stage = os.path.join(work, "by_done.usda")
    png = os.path.join(work, "by_done.png")
    write_frame(stage, asset, (BYGG_AZ[1], BYGG_ELEV, BYGG_DIST,
                               (0.0, 0.80, 0.0)))
    shoot(stage, png, render_width)
    pngs.append(png)
    numerals.append(None)
    print(f"  {len(pngs)} frames over {len(steps)} steps, azimuth "
          f"{BYGG_AZ[0]:g}..{BYGG_AZ[1]:g}")

    frames = load_frames(pngs)
    box = union_box(frames, margin=10)
    frames = scale_to([im.crop(box) for im in frames], width)
    for im, tag in zip(frames, numerals):
        if tag is not None:
            draw_numeral(im, tag[0], tag[1])
    play = frames + [frames[-1]] * BYGG_TAIL
    return finish("bygg", play, 95, work, want_mp4, colors=96)


# ---------------------------------------------------------------------------
# THE STAMP - what each committed film was rendered from
# ---------------------------------------------------------------------------
STAMP_HEADER = [
    "# Hvilken modell filmene i docs/img/ faktisk viser.",
    "# Skrevet av tools/render_animasjon.py, lest av `mise run film-check`.",
    "# En linje per film: <film> <kilde>=<sha256> ...  Endres en kilde uten at",
    "# filmen kjøres på nytt, feiler film-check - se docs/PRAKSIS.md punkt 5.",
]


def read_stamp():
    if not os.path.exists(STAMP):
        return {}
    out = {}
    with open(STAMP, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, *rest = line.split()
            out[name] = dict(f.split("=", 1) for f in rest)
    return out


def write_stamp(films):
    """Rewrites the whole file but only touches the lines for `films`, so
    rendering one film alone does not claim the other two are fresh."""
    stamped = read_stamp()
    for name in films:
        stamped[name] = {k: sha256(p) for k, p in FILM_SOURCES[name].items()}
    lines = list(STAMP_HEADER)
    for name in FILM_ORDER:
        if name in stamped:
            lines.append(name + "  " + "  ".join(
                f"{k}={stamped[name][k]}" for k in sorted(stamped[name])))
    with open(STAMP, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"  stamped {', '.join(films)} in {os.path.relpath(STAMP, ROOT)}")


def check_stamp():
    """Fast: hashes two small files and compares. No model, no render."""
    stamped = read_stamp()
    bad = []
    for name in FILM_ORDER:
        gif = os.path.join(IMG_DIR, GIF_NAME[name])
        if not os.path.exists(gif):
            bad.append(f"{name}: {os.path.relpath(gif, ROOT)} finnes ikke")
            continue
        if name not in stamped:
            bad.append(f"{name}: ingen linje i "
                       f"{os.path.relpath(STAMP, ROOT)}")
            continue
        for key, path in FILM_SOURCES[name].items():
            now = sha256(path)
            was = stamped[name].get(key)
            if was != now:
                bad.append(f"{name}: {os.path.relpath(path, ROOT)} er endret "
                           f"({(was or '-')[:12]} -> {now[:12]})")
    if bad:
        print("FILMENE ER BYGGET FRA EN ELDRE MODELL - kjør `mise run film`:")
        for b in bad:
            print("  " + b)
        print("  (eller bare den filmen det gjelder: mise run film-turntable "
              "/ film-mekanisme / film-bygg)")
        return 1
    print(f"OK  filmer: {', '.join(GIF_NAME[n] for n in FILM_ORDER)} er "
          f"bygget fra denne modellen (parts.tsv + byggesteg.json)")
    return 0


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
FILMS = {"turntable": film_turntable, "mekanisme": film_mekanisme,
         "bygg": film_bygg}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__.split("\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("film", nargs="?", default="all",
                    choices=["all"] + FILM_ORDER)
    ap.add_argument("--width", type=int, default=700,
                    help="delivered frame width in px (default 700)")
    ap.add_argument("--render-width", type=int, default=1400,
                    help="width the frames are shot at before the crop and "
                         "the downscale (default 1400)")
    ap.add_argument("--no-mp4", action="store_true",
                    help="skip the .mp4 even if ffmpeg is installed")
    ap.add_argument("--check", action="store_true",
                    help="only verify the stamp against the current sources")
    ns = ap.parse_args(argv)

    if ns.check:
        return check_stamp()

    for tool in ("swift", "usdrecord"):
        if shutil.which(tool) is None:
            sys.exit(f"{tool} not found - the films need the macOS USD tools "
                     f"and a Swift toolchain, same as `mise run render`.")
    wanted = FILM_ORDER if ns.film == "all" else [ns.film]
    os.makedirs(IMG_DIR, exist_ok=True)
    for name in wanted:
        work = os.path.join(FILM_DIR, name)
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work, exist_ok=True)
        print(f"\n=== {name} ===")
        FILMS[name](work, ns.width, ns.render_width,
                    not ns.no_mp4)
    write_stamp(wanted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
