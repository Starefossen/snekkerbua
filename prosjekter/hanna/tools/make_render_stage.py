"""Write a throwaway USD stage that references a .usdz and adds a camera.

`usdrecord` needs a camera prim to shoot from; the delivered .usdz files
deliberately contain nothing but the bed. This builds a tiny wrapper stage:

    <root>/Asset   -> references the .usdz
    <root>/Cam     -> a 3/4 view camera looking at the middle of the bed

Usage:
    python tools/make_render_stage.py <asset.usdz> <out.usda>
                                      [azimuth] [elevation] [distance]

Angles in degrees. Azimuth is measured from +Z towards +X; the bed's front
face (the ladder side) looks towards +Z, so an azimuth of 0 looks the bed in
the face and 330 gives a 3/4 view of the front and one open end. Everything is
in metres, Y-up, which is what the .usdz uses.

(Before the export flip that turned the ladder side towards +Z the same frames
were shot from azimuth a - 180: 180 for the front elevation, 150 for the front
3/4.  The flip is a proper 180 deg rotation about the vertical axis, not a
mirror, so handedness is unchanged and every azimuth simply gains 180 deg
while the elevation and distance stay put.)

No lights are authored: usdrecord's Storm/Metal delegate lights the frame with
its own camera headlight and ignores lights in the stage (verified - adding a
DomeLight + DistantLight rig changed the output by <=2/255 per channel). The
elevation is therefore what controls how bright the horizontal surfaces are,
and 26 degrees is high enough to read the slats, the mattress and the seats.
"""

import math
import os
import sys

DEFAULT_AZIMUTH = 330.0
DEFAULT_ELEVATION = 26.0
DEFAULT_DISTANCE = 3.7
TARGET = (0.0, 0.80, 0.0)          # roughly the middle of the loft bed

FOCAL_LENGTH = 35.0
H_APERTURE = 36.0
V_APERTURE = 24.0


def normalize(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def look_at_matrix(eye, target, up=(0.0, 1.0, 0.0)):
    """Camera-to-world matrix in USD's row-vector layout (translation last row).

    A USD camera looks down its own -Z, so the third row is -forward.
    """
    forward = normalize(tuple(t - e for t, e in zip(target, eye)))
    right = normalize(cross(forward, up))
    cam_up = cross(right, forward)
    back = tuple(-c for c in forward)
    rows = [right + (0.0,), cam_up + (0.0,), back + (0.0,), tuple(eye) + (1.0,)]
    return "( " + ", ".join(
        "(" + ", ".join(f"{v:.8g}" for v in row) + ")" for row in rows) + " )"


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    asset = os.path.abspath(argv[1])
    out_path = argv[2]
    azimuth = float(argv[3]) if len(argv) > 3 else DEFAULT_AZIMUTH
    elevation = float(argv[4]) if len(argv) > 4 else DEFAULT_ELEVATION
    distance = float(argv[5]) if len(argv) > 5 else DEFAULT_DISTANCE

    a, e = math.radians(azimuth), math.radians(elevation)
    direction = (math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e))
    eye = tuple(t + distance * d for t, d in zip(TARGET, direction))

    stage = f"""#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "World"
{{
    def "Asset" (
        prepend references = @{asset}@
    )
    {{
    }}

    def Camera "Cam"
    {{
        float2 clippingRange = (0.05, 100)
        float focalLength = {FOCAL_LENGTH}
        float horizontalAperture = {H_APERTURE}
        float verticalAperture = {V_APERTURE}
        matrix4d xformOp:transform = {look_at_matrix(eye, TARGET)}
        uniform token[] xformOpOrder = ["xformOp:transform"]
    }}
}}
"""
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(stage)
    print(f"  camera at ({eye[0]:.2f}, {eye[1]:.2f}, {eye[2]:.2f}) -> {out_path}")


if __name__ == "__main__":
    main(sys.argv)
