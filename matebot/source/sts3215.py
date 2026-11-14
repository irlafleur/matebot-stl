# Feetech STS3215 / Waveshare ST3215 envelope and official dimensions.
# MateBot, CC BY 4.0.
#
# Sources (do not invent values; every number below is from one of these):
#   1. Waveshare official 2D drawing (ST3215.pdf inside
#      https://files.waveshare.com/upload/0/08/ST3215-2D.zip ), title block
#      "SCS215", drawn by WL Zhang, 2022/6/8. Also the matching DXF in that zip.
#   2. Waveshare official STEP (ST3215.step inside
#      https://files.waveshare.com/upload/5/59/ST3215-3D.zip ), measured in
#      CadQuery. Used for hole positions that the 2D drawing does not dimension.
#   3. Waveshare wiki https://www.waveshare.com/wiki/ST3215_Servo
#      (overall 45.22 x 35 x 24.72 mm) and FAQ (included screws: self-tapping
#      3x5, round-head self-tapping 2x6, round-head M3x6; a screw that bottoms
#      on the housing can stall and burn the servo).
#   4. Feetech product page https://www.feetechrc.com/525603.html
#      (model ST-3215-C018, size A 45.2 / B 24.7 / C 35 mm, spline 25T / OD 5.9 mm,
#      horn type plastic POM, cable 15 cm, two 5264-3P bus ports).
#
# Local servo frame S used by the envelope:
#   origin = output-shaft axis at the OUTER face of the output horn
#            (the face the spool sits on)
#   +Z through the shaft, outward (spool in +Z, body in -Z)
#   +X from the shaft toward the CABLE end (the long way of the body)
#   +Y across the body width
import cadquery as cq, math

# --- overall, from the 2D drawing (1) and Feetech (4) ---
BODY_L = 45.22          # drawing: 45.22; Feetech rounds to 45.2
BODY_W = 24.72          # drawing: 24.72; Feetech rounds to 24.7
BODY_H_FLANGE = 32.0    # drawing: 32, body including both mounting flanges, no horns
H_TO_HORN = 35.0        # drawing: 35 and Feetech C; output-horn outer to idler flange outer
                        # STEP measures 35.20 (9.600 - (-25.60)); we still place the
                        # idler ear face at Z = -35.0 from the drawing, and the idler
                        # horn tip at Z = -37.25
H_BOTH_HORNS = 37.25    # drawing: 37.25, output-horn outer to idler-horn outer
SHAFT_FROM_OUT = 10.11  # drawing: 10.11, shaft axis to the output end of the body
SHAFT_FROM_CABLE = BODY_L - SHAFT_FROM_OUT  # 35.11

# --- horns, from the 2D drawing (1) and STEP (2) ---
HORN_OD = 19.2          # drawing: Ø19.2 (output and idler)
HORN_BCD = 14.0         # drawing: 14, four holes on the output horn
HORN_HOLE_D = 2.5       # STEP: four Ø2.5 cylinders on the 14 mm circle (M3 minor)
HORN_HOLE_DEPTH = 2.5   # STEP: the Ø2.5 bores run 2.5 mm in from the outer face
HORN_T = 4.5            # STEP solid: output horn 4.50 thick (Y 5.100 to 9.600)
IDLER_HORN_T = 3.35     # STEP solid: 3.35 (Y -27.650 to -24.300)
SPLINE_TEETH = 25
SPLINE_OD = 5.9         # Feetech (4)
HORN_CENTRE_SCREW = "M3x6"  # Feetech "rocker screw M3X6"; Waveshare includes M3x6

# --- mounting ears, from STEP (2); 2D drawing gives 20.7 / 24.45 / 20.5 / 6.11 ---
# Output-side (around the horn) four Ø1.6 holes, 20.70 x 20.50 mm rectangle.
# Idler-side four Ø1.6 holes, 24.45 x 20.50 mm rectangle (the cable-end pair is
# shifted). Do not use the same pattern on both faces.
MOUNT_HOLE_D = 1.6      # STEP: Ø1.6; Waveshare 2x6 self-tapping (M2) go here
EAR_T_OUTPUT = 1.60     # STEP: top-ear faces Y 4.80 to 6.40
EAR_T_IDLER = 2.80      # STEP: bottom-ear hole span Y -25.40 to -22.60
# Hole centres in S: (X toward cable, Y across). Shaft is at X=0, Y=0.
# Output-side: X = 8.30 and 29.00 (= 8.30+20.70), Y = ±10.25
# Idler-side:  X = 8.30 and 32.75 (= 8.30+24.45), Y = ±10.25
# 8.30 = 18.41 - 10.11: the 18.41 dimension on the drawing is the output-end
# of the body to this hole, and 10.11 is the shaft.
OUT_HOLES = ((8.30, 10.25), (8.30, -10.25), (29.00, 10.25), (29.00, -10.25))
IDL_HOLES = ((8.30, 10.25), (8.30, -10.25), (32.75, 10.25), (32.75, -10.25))
# Idler-horn protrusion past the idler ear outer face: 37.25 - 35.00 = 2.25
IDLER_PROTRUSION = H_BOTH_HORNS - H_TO_HORN

# --- idler-face housing step, from the official STEP (2) ---
# The 2D drawing (1) shows a rectangular area on the idler face, between
# the four mounting ears on the cable-end side of the horn, but does not
# dimension it. Measured in CadQuery from ST3215.step: shaft at X=-25.500,
# ear outer face at Y=-25.600, this housing's outer face at Y=-27.500
# (1.90 mm past the ears, toward the idler horn). Outline in servo frame S
# (X toward the cable, Y across the width), taken from the proud silhouette
# (material at least 0.3 mm past the ear, outside the horn):
#   X = 19.551 to 29.397  (= STEP X -5.949 to 3.897, plus 25.500)
#   Y = ±8.936            (= STEP Z)
# An inner pad (X 21.50 to 27.50, Y ±6.00) sits 1.75 mm past the ears
# (STEP Y=-27.350); the outer rim is 1.90 mm past. This housing is
# separate from the idler horn (Ø19.2, tip 2.05 mm past the ears in the
# STEP, 2.25 mm on the drawing). It reaches the two cable-end idler
# holes (X=32.75, Y=±10.25): closest proud material is 3.66 mm from
# those hole axes (the shaft-end pair is clear of it; they only see
# the horn).
IDL_HOUSING_X0 = 19.551
IDL_HOUSING_X1 = 29.397
IDL_HOUSING_HALF_W = 8.936
IDL_HOUSING_H = 1.90

def idler_housing_rect(clear=0.0):
    """Axis-aligned rectangle of the idler-face housing in S (X toward
    cable, Y across), optionally expanded by clear."""
    return (IDL_HOUSING_X0 - clear, IDL_HOUSING_X1 + clear,
            -IDL_HOUSING_HALF_W - clear, IDL_HOUSING_HALF_W + clear)

# Print clearance around the body in a pocket (not from a drawing; a print allowance)
CL = 0.4

def horn_holes_xy():
    """Four horn-hole centres in the XY plane of S (Z=0 is the outer face)."""
    r = HORN_BCD / 2.0
    return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (0, 90, 180, 270)]

def body_box():
    """Axis-aligned body including flanges, no horns. X from -SHAFT_FROM_OUT to +SHAFT_FROM_CABLE."""
    x0, x1 = -SHAFT_FROM_OUT, SHAFT_FROM_CABLE
    y0, y1 = -BODY_W / 2, BODY_W / 2
    # Idler ear outer at Z=-H_TO_HORN; output ear outer at Z=-H_TO_HORN+BODY_H_FLANGE
    z0, z1 = -H_TO_HORN, -H_TO_HORN + BODY_H_FLANGE
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def envelope(cl=0.0, with_horns=True, with_cables=True):
    """Collision envelope of one STS3215, optional clearance around the body only.
    Horns stay at nominal size (they are already a known OD)."""
    x0, x1 = -SHAFT_FROM_OUT - cl, SHAFT_FROM_CABLE + cl
    y0, y1 = -BODY_W / 2 - cl, BODY_W / 2 + cl
    z0, z1 = -H_TO_HORN - cl, -H_TO_HORN + BODY_H_FLANGE + cl
    body = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    if with_horns:
        # output horn, from Z=-HORN_T to 0, Ø19.2
        body = body.union(cq.Workplane("XY").circle(HORN_OD / 2).extrude(-HORN_T))
        # idler horn, tip at Z=-H_BOTH_HORNS
        body = body.union(cq.Workplane("XY").workplane(offset=-H_BOTH_HORNS).circle(HORN_OD / 2).extrude(IDLER_HORN_T))
    if with_cables:
        # cable stubs at the cable end (both bus ports), 8 mm long, 6 mm boss — not
        # dimensioned on the drawing; a clearance envelope only, so we do not claim mm.
        stub = cq.Workplane("YZ").workplane(offset=SHAFT_FROM_CABLE).center(0, -H_TO_HORN + 8).circle(3.5).extrude(8 + cl)
        body = body.union(stub)
    return body

def output_horn():
    """Stock output horn disc with 4 x Ø2.5 holes on the 14 mm circle and a centre clearance."""
    h = cq.Workplane("XY").circle(HORN_OD / 2).extrude(-HORN_T)
    h = h.faces(">Z").workplane().hole(6.2)  # over the M3x6 centre screw head
    for x, y in horn_holes_xy():
        h = h.faces(">Z").workplane().center(x, y).hole(HORN_HOLE_D)
    return h
