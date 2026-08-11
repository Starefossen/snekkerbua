import os

from build123d import *

# Create individual parts
part_a = Box(1990, 48, 98)
# Position A: flush against back wall (Y=0 -> back face). Top at Z=98.
# Box center starts at 0,0,0.
part_a = part_a.moved(Location((0, 24, 49)))
part_a.label = "Back Wall Ledger"

part_b_left = Box(48, 754, 98)
# Position B left: flush against left wall (X = -995). Butts against A (Y=48). Top at 98.
part_b_left = part_b_left.moved(Location((-971, 425, 49)))
part_b_left.label = "Left Side Ledger"

part_b_right = Box(48, 754, 98)
# Position B right: flush against right wall (X = 995).
part_b_right = part_b_right.moved(Location((971, 425, 49)))
part_b_right.label = "Right Side Ledger"

part_c = Box(1990, 48, 148)
# Position C: Front face at Y=850. Top edge flush with A and B (Z=98).
part_c = part_c.moved(Location((0, 826, 24)))
part_c.label = "Front Load-Bearing Beam"

part_d = Box(1990, 48, 48)
# Position D: Attached to back side of C (so ends at Y=802, starts at 754).
# Top aligned with top of A (Z=98).
part_d = part_d.moved(Location((0, 778, 74)))
part_d.label = "Slat Cleat"

# Slats
slats = []
# 12 slats, 100mm wide, 70mm gap. Total width 1970mm.
for i in range(12):
    # EXPLICITLY set height (Z) to 20mm so they lie flat on the X/Y plane
    slat = Box(length=100, width=754, height=20)
    # Slats span from Y=24 to Y=778 (resting on A and D). Center Y = 401.
    # Bottom at Z=98, so center Z = 108.
    x_pos = -935 + i * 170
    slat = slat.moved(Location((x_pos, 401, 108)))
    slat.label = f"Slat_{i+1}"
    slats.append(slat)

# Skirting tool (height: 70, depth: 15)
skirting_back = Box(1990, 15, 70).moved(Location((0, 7.5, 35)))
skirting_left = Box(15, 850, 70).moved(Location((-995 + 7.5, 425, 35)))
skirting_right = Box(15, 850, 70).moved(Location((995 - 7.5, 425, 35)))
skirting_tool = skirting_back + skirting_left + skirting_right

# Subtract the skirting boards from each part to create a flush notch
part_a = part_a - skirting_tool
part_a.label = "Back Wall Ledger"

part_b_left = part_b_left - skirting_tool
part_b_left.label = "Left Side Ledger"

part_b_right = part_b_right - skirting_tool
part_b_right.label = "Right Side Ledger"

part_c = part_c - skirting_tool
part_c.label = "Front Load-Bearing Beam"

part_d = part_d - skirting_tool
part_d.label = "Slat Cleat"

# Combine into an assembly
bed_frame = Compound(children=[
    part_a, part_b_left, part_b_right, part_c, part_d, *slats
])

# Ut ved siden av skriptet selv - ingen absolutte stier i repoet.
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Export to STEP (Standard Z-up CAD format)
export_step(bed_frame, os.path.join(OUT_DIR, "bed_frame.step"))

# Export to SVG for a clear visual preview without coordinate system issues
try:
    export_svg(bed_frame, os.path.join(OUT_DIR, "bed_frame.svg"), direction=(1, -1, 1))
except Exception as e:
    print("SVG export failed:", e)

print("Files exported successfully.")
