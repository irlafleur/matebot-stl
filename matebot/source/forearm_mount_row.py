# MateBot v11 (UNTESTED): two U-plates sandwiching a single row of 8 x
# Feetech STS3215 (12 V), fixed wrist to R-Wrist_Interface.
#
# Layout: ONE row along the forearm, servos side by side like stacked
# cards, long axis ACROSS the forearm, output shaft perpendicular to
# the plates. Faces follow TL, TR, BL, BR, repeat (wrist to elbow):
#   0-1 thumb  = top (dorsal),  shafts L then R
#   2-3 index  = bottom (palmar), shafts L then R
#   4-5 middle = top,            shafts L then R
#   6-7 ring   = bottom,         shafts L then R
# Each finger pair is two adjacent servos on the SAME face, so that
# finger's four tubes stay on one plate and do not cross.
#
# The rack is two U-channel plates (web + side flanges, wrist to elbow)
# that sandwich the servos. Spool cut-outs on the spool face, M2x6
# through the idler ears from the outside of the opposite plate.
# Regular M3 grids on the webs and on the U flanges; front = official
# Wrist_Interface 6xM2; rear = open elbow with an M3 pattern.
# Plates are split at a service gap (each half < 250 mm).
#
# CadQuery. MateBot, CC BY 4.0.
#
# Usage:
#   python forearm_mount_row.py
# writes STEP/STL next to this file, or into ../step and ../stl.
import cadquery as cq, math, os, sys
from sts3215 import (
    BODY_L, BODY_W, BODY_H_FLANGE, H_TO_HORN, H_BOTH_HORNS,
    SHAFT_FROM_OUT, SHAFT_FROM_CABLE, HORN_OD, HORN_BCD, HORN_HOLE_D, HORN_T,
    IDL_HOLES, MOUNT_HOLE_D, EAR_T_IDLER, IDLER_PROTRUSION, CL,
    envelope, horn_holes_xy,
)

HERE = os.path.dirname(os.path.abspath(__file__))
STEP_DIR = os.path.join(HERE, "..", "step")
STL_DIR = os.path.join(HERE, "..", "stl")

# ---------------------------------------------------------------------------
# Hand frame = Pollen / plate frame: X right (ulnar on the right hand),
# Y toward the fingertips, Z toward the back of the hand (dorsal).
# Forearm frame F: origin on the proximal face of R-Wrist_Interface, at the
# centre of its Ø34 window and 6-hole circle (read from the official STEP):
#   hand (24.50, -102.20, -11.50)
#   x_f = X - 24.50,  y_f = -102.20 - Y  (toward the elbow),  z_f = Z + 11.50
# ---------------------------------------------------------------------------
WI_CX, WI_CY, WI_CZ = 24.50, -102.20, -11.50
WI_HOLE_R = 21.0
WI_HOLE_ANG = (20.0, 100.0, 140.0, -140.0, -100.0, -20.0)
WI_WINDOW_D = 34.0
WI_XF = (-33.50, 33.50)
WI_ZF = (-28.75, 27.00)

# Shaft X that keeps every body centred on x=0 while the horn zig-zags.
# BODY_L/2 - SHAFT_FROM_OUT = 45.22/2 - 10.11 = 12.50 mm.
SHAFT_X = BODY_L / 2 - SHAFT_FROM_OUT  # 12.50

P = dict(
    cl=CL,
    wall=3.5,
    web_t=4.0,              # M2x6: 4 mm plate + 2 mm into the 2.8 mm idler ear
    spool_r=8.0, spool_flange=3.0, spool_base_t=2.0, groove_w=3.0, mid_flange=1.5,
    spool_top_t=2.0,
    sock_d=4.2, sock_depth=8.0, tendon_d=2.2, tube_od=4.0,
    r_min=30.0,
    m3_d=3.4, m2_clear=2.4,
    flange_t=6.0,
    register_d=33.6, register_t=2.0,
    lane_w=10.0,
    pitch=36.0,             # BODY_W + 11.28: room for the 8 mm sockets in Y
    joint_extra=16.0,       # added only between stations 3 and 4 for the split
    y0=58.0,              # room for a 30 mm thumb drop in front of station 0
    lap=16.0,
    spool_cut_d=28.0,       # spool flange is Ø22; 3 mm radial clearance
    idler_cut_d=22.0,       # clearance for the idler horn (protrudes 2.25 mm)
    x_inner=24.5,           # inside of the inner (top) walls
    wall_overlap_z=8.0,     # each U flange crosses mid-plane by 8 mm
    sock_dx=5.0,            # socket offset from the shaft in X
    sock_y_exit=13.0,       # shaft to socket exit (toward the wrist)
    finger_sep=8.0,
)
P['spool_h'] = P['spool_base_t'] + P['groove_w'] + P['mid_flange'] + P['groove_w'] + P['spool_top_t']  # 11.5
P['z_inner_top'] = H_TO_HORN / 2          # +17.5, output-horn plane of a TOP servo
P['z_inner_bot'] = -H_TO_HORN / 2         # -17.5
P['z_outer_top'] = P['z_inner_top'] + P['web_t']   # +21.5
P['z_outer_bot'] = P['z_inner_bot'] - P['web_t']   # -21.5
# Nested U walls: top plate inside, bottom plate outside, contact at x=±28.0
P['x_top_wall_in'] = P['x_inner']                         # 24.5
P['x_top_wall_out'] = P['x_inner'] + P['wall']             # 28.0
P['x_bot_wall_in'] = P['x_top_wall_out']                   # 28.0
P['x_bot_wall_out'] = P['x_bot_wall_in'] + P['wall']        # 31.5
P['lip'] = 5.0                  # outward M3 lip on each web, for arm-shell supports
P['y_cut'] = P['y0'] + 3 * P['pitch'] + (BODY_W / 2 + P['joint_extra'] / 2)
# stations 0..3 at y0 + i*pitch; 4..7 after the joint gap
# y_end set after stations()

# TL, TR, BL, BR, repeat. Same-face adjacent pairs (tubes stay on one plate).
STATION_META = [
    dict(i=0, finger="thumb",  ab="A", face="top",    side="left"),
    dict(i=1, finger="thumb",  ab="B", face="top",    side="right"),
    dict(i=2, finger="index",  ab="A", face="bottom", side="left"),
    dict(i=3, finger="index",  ab="B", face="bottom", side="right"),
    dict(i=4, finger="middle", ab="A", face="top",    side="left"),
    dict(i=5, finger="middle", ab="B", face="top",    side="right"),
    dict(i=6, finger="ring",   ab="A", face="bottom", side="left"),
    dict(i=7, finger="ring",   ab="B", face="bottom", side="right"),
]
FACE = dict(thumb="top", index="bottom", middle="top", ring="bottom")
LIP_SIGN = dict(thumb=-1, index=-1, middle=1, ring=1)  # sockets on this lip


def f_to_hand(xf, yf, zf):
    return (xf + WI_CX, WI_CY - yf, zf - 11.50)

def hand_to_f(x, y, z):
    return (x - WI_CX, WI_CY - y, z + 11.50)


def stations(p=P):
    """Wrist-to-elbow list of 8 stations with positions in frame F."""
    out = []
    for meta in STATION_META:
        i = meta["i"]
        if i <= 3:
            y = p["y0"] + i * p["pitch"]
        else:
            y = p["y0"] + 3 * p["pitch"] + p["joint_extra"] + p["pitch"] + (i - 4) * p["pitch"]
        xf = -SHAFT_X if meta["side"] == "left" else SHAFT_X
        zf = p["z_inner_top"] if meta["face"] == "top" else p["z_inner_bot"]
        rec = dict(meta)
        rec.update(xf=xf, y=y, zf=zf, y_shaft=y)
        out.append(rec)
    return out


def y_end(p=P):
    last = stations(p)[-1]["y"]
    return last + BODY_W / 2 + 8.0  # 8 mm of web past the last body for the elbow M3


def groove_zs(face, p=P):
    z0 = p["z_inner_top"] if face == "top" else p["z_inner_bot"]
    d1 = p["spool_base_t"] + p["groove_w"] / 2
    d2 = p["spool_base_t"] + p["groove_w"] + p["mid_flange"] + p["groove_w"] / 2
    if face == "top":
        return (z0 + d1, z0 + d2)
    return (z0 - d1, z0 - d2)


def place_S(shape, xf, yf, zf, face="top", side="left"):
    """Map a solid in servo frame S into F.
    +Y_s is not preserved for every orientation; use idler_holes_F for holes.
    Long axis (cable, +X_s) is ACROSS the forearm.
    Top / left: +X_s along +X_f, +Z_s along +Z_f.
    Right: 180 deg about Z. Bottom: 180 deg about X first."""
    if face == "bottom":
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    if side == "right":
        shape = shape.rotate((0, 0, 0), (0, 0, 1), 180)
    return shape.translate((xf, yf, zf))


def loc_S(xf, yf, zf, face="top", side="left"):
    from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
    acc = gp_Trsf()
    if face == "bottom":
        rx = gp_Trsf()
        rx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.radians(180))
        acc = rx
    if side == "right":
        rz = gp_Trsf()
        rz.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(180))
        acc = rz.Multiplied(acc)
    tt = gp_Trsf()
    tt.SetTranslation(gp_Vec(xf, yf, zf))
    return cq.Location(tt.Multiplied(acc))


def idler_holes_F(xf, yf, zf, face, side):
    """Four idler-ear hole centres in F (x, y, z at the idler face)."""
    holes = []
    z_s = -H_TO_HORN
    for Xs, Ys in IDL_HOLES:
        x1, y1, z1 = Xs, Ys, z_s
        if face == "bottom":
            y1, z1 = -y1, -z1
        if side == "right":
            x1, y1 = -x1, -y1
        holes.append((xf + x1, yf + y1, zf + z1))
    return holes


def sock_ys(y_shaft, p=P):
    """y_exit (closer to the spool) and y_entrance (wrist side of the bore)."""
    y_exit = y_shaft - p["sock_y_exit"]
    y_ent = y_exit - p["sock_depth"]
    return y_ent, y_exit


def sock_x_lip(finger, p=P):
    """X of the PTFE sockets: on the lane, just outboard of the 5 mm lip."""
    return LIP_SIGN[finger] * (p["x_bot_wall_out"] + p["lip"] + 1.5)  # ±38.0

def sock_xs(finger, p=P):
    # Both tubes of a servo share the same X and Y; they are stacked in Z
    # at the two groove heights, so the PTFE lane has no X dog-leg.
    x0 = sock_x_lip(finger, p)
    return (x0, x0)


# ---------------------------------------------------------------------------
# Spool, official horn pattern (BCD 14 mm from the Waveshare 2D drawing).
# Unchanged from v9/v10 spool_r8.
# ---------------------------------------------------------------------------
def spool_r8(p=P):
    """Identical to v9/v10 spool_r8 — official 14 mm BCD, do not change."""
    r, fl = p["spool_r"], p["spool_flange"]
    h = cq.Workplane("XY").circle(r + fl).extrude(p["spool_base_t"])
    h = h.faces(">Z").workplane().circle(r).extrude(p["groove_w"])
    h = h.faces(">Z").workplane().circle(r + 2.0).extrude(p["mid_flange"])
    h = h.faces(">Z").workplane().circle(r).extrude(p["groove_w"])
    h = h.faces(">Z").workplane().circle(r + fl).extrude(p["spool_top_t"])
    h = h.faces(">Z").workplane().hole(6.5)
    h = h.faces(">Z").workplane().pushPoints(horn_holes_xy()).hole(3.4)
    z1 = p["spool_base_t"] + p["groove_w"] / 2
    z2 = p["spool_base_t"] + p["groove_w"] + p["mid_flange"] + p["groove_w"] / 2
    for z in (z1, z2):
        h = h.cut(cq.Workplane("YZ").workplane(offset=-20).center(r - 1.0, z).circle(0.8).extrude(40))
    return h


def fuse_fuzzy(shapes, tol=0.08):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    acc = shapes[0].val() if hasattr(shapes[0], "val") else shapes[0]
    for sh in shapes[1:]:
        sv = sh.val() if hasattr(sh, "val") else sh
        op = BRepAlgoAPI_Fuse(acc.wrapped if hasattr(acc, "wrapped") else acc,
                              sv.wrapped if hasattr(sv, "wrapped") else sv)
        op.SetFuzzyValue(tol)
        op.Build()
        acc = cq.Shape.cast(op.Shape())
    try:
        u = ShapeUpgrade_UnifySameDomain(acc.wrapped, True, True, True)
        u.Build()
        acc = cq.Shape.cast(u.Shape())
    except Exception:
        pass
    return cq.Workplane("XY").add(acc)


def _box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def _cyl(r, h, origin, direction):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, h, cq.Vector(*origin), cq.Vector(*direction)))


def _cut_cyls_z(wp, points_xy, z0, h, r):
    if not points_xy:
        return wp
    solids = [_cyl(r, h, (x, y, z0), (0, 0, 1)).val() for x, y in points_xy]
    comp = cq.Compound.makeCompound(solids)
    return wp.cut(comp)


def _cut_cyls_y(wp, points_xz, y0, h, r):
    if not points_xz:
        return wp
    solids = [_cyl(r, h, (x, y0, z), (0, 1, 0)).val() for x, z in points_xz]
    comp = cq.Compound.makeCompound(solids)
    return wp.cut(comp)


def _cut_cyls_x(wp, points_yz, x0, h, r, sign=1):
    if not points_yz:
        return wp
    d = (1, 0, 0) if sign > 0 else (-1, 0, 0)
    x_orig = x0 if sign > 0 else x0
    solids = [_cyl(r, h, (x_orig, y, z), d).val() for y, z in points_yz]
    # for sign < 0, cylinder grows toward -X from x_orig
    if sign < 0:
        solids = [_cyl(r, h, (x0, y, z), (-1, 0, 0)).val() for y, z in points_yz]
    comp = cq.Compound.makeCompound(solids)
    return wp.cut(comp)


# ---------------------------------------------------------------------------
# Mounting-pattern catalogue (positions in frame F). Used by the verify
# script, the renderer (French labels) and the docs.
# ---------------------------------------------------------------------------
def patterns(p=P):
    sts = stations(p)
    ye = y_end(p)
    wi = []
    for a in WI_HOLE_ANG:
        rad = math.radians(a)
        wi.append((round(WI_HOLE_R * math.cos(rad), 3),
                   0.0,
                   round(WI_HOLE_R * math.sin(rad), 3)))
    m2 = []
    for s in sts:
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            m2.append(dict(i=s["i"], finger=s["finger"], ab=s["ab"],
                           face=s["face"], x=round(x, 3), y=round(y, 3), z=round(z, 3),
                           access="bottom" if s["face"] == "top" else "top",
                           screw="M2x6"))
    # Side U-flange grid, through both nested walls (along X), 15 mm in Y, two rows in Z.
    y_side = []
    y = 12.0
    while y < ye - 6.0:
        # skip a hole that would land exactly in the joint kerf
        if abs(y - p["y_cut"]) > 4.0:
            y_side.append(round(y, 2))
        y += 15.0
    z_side = (-5.0, 5.0)
    side = []
    for ys in y_side:
        for zs in z_side:
            side.append(dict(x_plane=p["x_bot_wall_in"], y=ys, z=zs,
                             dir="X", screw="M3", d=p["m3_d"]))
    # M3 lip grid on both long edges of each web (outboard of the U walls,
    # so the spool cut-outs never block it). Pas 20 mm.
    x_lip = p["x_bot_wall_out"] + p["lip"] / 2.0   # 34.0
    web_top, web_bot = [], []
    y = 16.0
    while y < ye - 6.0:
        for x in (-x_lip, x_lip):
            web_top.append(dict(x=round(x, 2), y=round(y, 2), z=p["z_outer_top"],
                                dir="Z", screw="M3", d=p["m3_d"]))
            web_bot.append(dict(x=round(x, 2), y=round(y, 2), z=p["z_outer_bot"],
                                dir="Z", screw="M3", d=p["m3_d"]))
        y += 20.0
    # Elbow (rear) open pattern: 4 x M3 on each web, 24 x 16 mm rectangle.
    y_el1, y_el2 = ye - 12.0, ye - 5.0
    elbow_top = [(x, y_el, p["z_outer_top"]) for x in (-12.0, 12.0) for y_el in (y_el1, y_el2)]
    elbow_bot = [(x, y_el, p["z_outer_bot"]) for x in (-12.0, 12.0) for y_el in (y_el1, y_el2)]
    # Half-lap joint, 4 x M3 per plate through the stacked webs.
    lap_y = p["y_cut"]
    joint_top = [(-15.0, lap_y, p["z_inner_top"]), (15.0, lap_y, p["z_inner_top"]),
                 (-15.0, lap_y - 5.0, p["z_inner_top"]), (15.0, lap_y - 5.0, p["z_inner_top"])]
    # wait, 4 holes: two at cut, or two rows? Use 2 at y_cut-4 and 2 at y_cut+4
    joint_top = [(-15.0, lap_y - 4.0, p["z_inner_top"]), (15.0, lap_y - 4.0, p["z_inner_top"]),
                 (-15.0, lap_y + 4.0, p["z_inner_top"]), (15.0, lap_y + 4.0, p["z_inner_top"])]
    joint_bot = [(x, y, p["z_inner_bot"]) for x, y, _ in joint_top]
    # Side splice tabs at the joint (M3 along X).
    splice = dict(y=p["y_cut"] + 4.0, z=(0.0,), x_top=p["x_top_wall_out"],
                  x_bot=p["x_bot_wall_out"])
    return dict(
        front_wi_m2=dict(
            name_fr="Interface poignet — R-Wrist_Interface",
            screw="M2 passage Ø2.4, 6 vis, bride 6 mm",
            positions=wi,
            note=("Cercle R=21 mm, angles 20°, 100°, 140°, −140°, −100°, −20°. "
                  "Enregistrement Ø33.6 × 2 mm dans la fenêtre Ø34. "
                  "Vis dans la pièce Wrist_Interface, côté main."),
        ),
        servo_idler_m2=dict(
            name_fr="Fixation des servos — oreilles côté poulie folle",
            screw="M2×6 (32 vis, 4 par servo), passage Ø2.4, plaque 4 mm",
            holes=m2,
            note=("Accès depuis l'extérieur de la plaque opposée à la bobine. "
                  "4 mm de plaque + 2 mm dans l'oreille de 2,8 mm. "
                  "Ne pas utiliser de M2×8 : la vis buterait sur le boîtier."),
        ),
        side_flange_m3=dict(
            name_fr="Grille M3 des flancs en U (assemblage des plaques + attaches)",
            screw="M3 passage Ø3.4, pas 15 mm (Y), deux rangées à z=±5 mm",
            holes=side,
            y_rows=y_side,
            z_rows=list(z_side),
            note="Traversant les deux parois emboîtées, selon X. Écrous M3 de l'intérieur, ou entretoises.",
        ),
        web_shell_top_m3=dict(
            name_fr="Grille M3 de la plaque supérieure — supports de coque",
            screw="M3 passage Ø3.4, pas 20 mm",
            holes=web_top,
            note="Lèvres de 5 mm de chaque côté de la semelle dorsale, pas 20 mm, hors des parois en U.",
        ),
        web_shell_bot_m3=dict(
            name_fr="Grille M3 de la plaque inférieure — supports de coque",
            screw="M3 passage Ø3.4, pas 20 mm",
            holes=web_bot,
            note="Lèvres de 5 mm de chaque côté de la semelle palmaire, pas 20 mm.",
        ),
        elbow_m3=dict(
            name_fr="Interface coude (arrière ouvert)",
            screw="M3 passage Ø3.4, 4 vis par plaque, rectangle 24 × 7 mm",
            top=elbow_top,
            bottom=elbow_bot,
            note="Le fond est ouvert pour la nappe bus. Les 8 trous (4 dessus, 4 dessous) reçoivent une pièce coude ou une coque plus tard.",
        ),
        joint_m3=dict(
            name_fr="Joint des deux demis (demi-recouvrement)",
            screw="M3×10 + écrou, 4 vis par plaque, selon Z",
            top=joint_top,
            bottom=joint_bot,
            note="Demi-recouvrement de 16 mm à Y=156, dans l'intervalle de service entre l'index et le majeur.",
        ),
        splice_m3=dict(
            name_fr="Pattes de splice au joint (flancs)",
            screw="M3×12 + écrou, selon X, une patte de chaque côté",
            info=splice,
        ),
        spool_m3=dict(
            name_fr="Bobine spool_r8 sur le palonnier",
            screw="M3×6, 4 vis sur le cercle de 14 mm (dessin Waveshare) + vis centrale M3×6",
            note="Inchangé depuis v9/v10. Ne pas modifier spool_r8.",
        ),
    )


# ---------------------------------------------------------------------------
# Plates
# ---------------------------------------------------------------------------
def _side_hole_points(p):
    pat = patterns(p)["side_flange_m3"]
    return [(h["y"], h["z"]) for h in pat["holes"]]


def _web_points(pat_holes):
    return [(h["x"], h["y"]) for h in pat_holes]


def _socket_bosses(face, p, sts):
    """Bosses on the assigned outward lip, two Ø4.2 bores along Y per servo."""
    bits = []
    recs = []
    gz = groove_zs(face, p)
    for s in sts:
        if s["face"] != face:
            continue
        y_ent, y_ex = sock_ys(s["y"], p)
        xs = sock_xs(s["finger"], p)
        sign = LIP_SIGN[s["finger"]]
        # boss sits fully on the lip and hangs 6 mm outboard of it
        x_in = sign * p["x_bot_wall_out"] - sign * 0.5
        x_out = sign * (p["x_bot_wall_out"] + p["lip"] + 6.0)
        x0, x1 = (x_in, x_out) if x_in < x_out else (x_out, x_in)
        y0, y1 = y_ent - 1.5, y_ex + 3.0
        if face == "top":
            z0, z1 = p["z_inner_top"] - 0.5, max(gz) + 4.0
        else:
            z0, z1 = min(gz) - 4.0, p["z_inner_bot"] + 0.5
        bits.append(_box(x0, x1, y0, y1, z0, z1))
        recs.append(dict(i=s["i"], finger=s["finger"], ab=s["ab"], face=face,
                         xf=s["xf"], y_shaft=s["y"],
                         sock=(xs[0], xs[1], y_ent, y_ex, gz[0], gz[1])))
    return bits, recs


def _cut_sockets(wp, face, p, sts):
    gz = groove_zs(face, p)
    for s in sts:
        if s["face"] != face:
            continue
        y_ent, y_ex = sock_ys(s["y"], p)
        for x in sock_xs(s["finger"], p):
            for z in gz:
                wp = wp.cut(_cyl(p["sock_d"] / 2, p["sock_depth"] + 1.0,
                                 (x, y_ent, z), (0, 1, 0)))
                # tendon continuation toward the spool
                wp = wp.cut(_cyl(p["tendon_d"] / 2, (s["y"] - p["spool_r"] - 1) - (y_ent - 0.5),
                                 (x, y_ent - 0.5, z), (0, 1, 0)))
    return wp


def _cable_slots(wp, p, sts, plate):
    """Open a window in the U walls at each cable end (alternating sides)."""
    for s in sts:
        # cable end in X: left-shaft -> +X (ulnar), right-shaft -> -X (radial)
        side_sign = 1 if s["side"] == "left" else -1
        # Cable boss in F: in S it sits at Z = -H_TO_HORN + 8 = -27, so
        # top servo at z = 17.5-27 = -9.5, bottom servo at z = +9.5.
        zc = -9.5 if s["face"] == "top" else 9.5
        y0, y1 = s["y"] - 8.0, s["y"] + 8.0
        z0, z1 = zc - 9.0, zc + 9.0
        # cut through both nested walls on that side
        if side_sign > 0:
            slot = _box(p["x_inner"] - 1.0, p["x_bot_wall_out"] + 1.0, y0, y1, z0, z1)
        else:
            slot = _box(-p["x_bot_wall_out"] - 1.0, -p["x_inner"] + 1.0, y0, y1, z0, z1)
        wp = wp.cut(slot)
    return wp


def _front_flange(p):
    t = p["flange_t"]
    x_lo, x_hi = -44.0, 44.0
    z_lo, z_hi = -40.0, 42.0
    fl = _box(x_lo, x_hi, 0.0, t, z_lo, z_hi)
    for a in WI_HOLE_ANG:
        rad = math.radians(a)
        xh = WI_HOLE_R * math.cos(rad)
        zh = WI_HOLE_R * math.sin(rad)
        fl = fl.cut(_cyl(p["m2_clear"] / 2, t + 2, (xh, -1, zh), (0, 1, 0)))
    reg = _cyl(p["register_d"] / 2, p["register_t"], (0, -p["register_t"], 0), (0, 1, 0))
    win = _cyl((WI_WINDOW_D - 3.0) / 2, t + p["register_t"] + 2,
               (0, -p["register_t"] - 1, 0), (0, 1, 0))
    fl = fl.union(reg).cut(win)

    def corridor(x_mid, z_mid, w, h):
        return (cq.Workplane("XY").box(w, t + 2, h, centered=True)
                .translate((x_mid, t / 2, z_mid)))
    # Tall side corridors (both faces) and a palmar-radial drop for the thumb.
    # Tall side corridors (both faces). The radial one is extended palmar
    # so the thumb drop can leave at z=-34, x=-38 without hitting the flange.
    fl = fl.cut(corridor(WI_XF[0] - p["lane_w"] / 2 - 0.5, -8.0, p["lane_w"], 60.0))
    fl = fl.cut(corridor(WI_XF[1] + p["lane_w"] / 2 + 0.5, 0.0, p["lane_w"], 44.0))
    fl = fl.cut(corridor(-24.0, -26.0, 40.0, 30.0))  # palmar-radial, x=-44..-4, z=-41..-11
    return fl


def plate_bottom(p=P):
    """Full lower U-plate, including the 6 mm wrist flange. Not yet split."""
    sts = stations(p)
    ye = y_end(p)
    y0 = p["flange_t"] - 0.2
    # Web: full width of the outer walls, y from flange to elbow
    x_lip = p["x_bot_wall_out"] + p["lip"]
    web = _box(-x_lip, x_lip,
               y0, ye,
               p["z_outer_bot"], p["z_inner_bot"])
    # Two outer walls, up past mid-plane
    wL = _box(-p["x_bot_wall_out"], -p["x_bot_wall_in"],
              y0, ye,
              p["z_outer_bot"], p["wall_overlap_z"])
    wR = _box(p["x_bot_wall_in"], p["x_bot_wall_out"],
              y0, ye,
              p["z_outer_bot"], p["wall_overlap_z"])
    fl = _front_flange(p)
    bosses, recs = _socket_bosses("bottom", p, sts)
    # Splice pads at the joint, outside the outer wall, elbow side of the cut
    # (the matching tab lives on the wrist half after the split; both pads are
    # modelled on the full plate, then the split keeps the right piece of each).
    tab_t = 3.5
    y_c = p["y_cut"]
    pads = []
    for sign in (-1, 1):
        x_a = sign * p["x_bot_wall_out"]
        x_b = sign * (p["x_bot_wall_out"] + tab_t)
        x0, x1 = (x_a, x_b) if x_a < x_b else (x_b, x_a)
        pads.append(_box(x0, x1, y_c - p["lap"] / 2, y_c + p["lap"] / 2, -6.0, 6.0))
    body = fuse_fuzzy([web, wL, wR, fl] + bosses + pads)

    # Spool cut-outs (bottom-face servos) and idler-horn holes (top-face servos)
    spool_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "bottom"]
    idler_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "top"]
    body = _cut_cyls_z(body, spool_pts, p["z_outer_bot"] - 1.0, p["web_t"] + 12.0, p["spool_cut_d"] / 2)
    body = _cut_cyls_z(body, idler_pts, p["z_outer_bot"] - 1.0, p["web_t"] + 2.0, p["idler_cut_d"] / 2)

    # M2 through the web at the idler ears of TOP servos (access from below)
    m2_pts = []
    for s in sts:
        if s["face"] != "top":
            continue
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            m2_pts.append((x, y))
    body = _cut_cyls_z(body, m2_pts, p["z_outer_bot"] - 1.0, p["web_t"] + 2.0, p["m2_clear"] / 2)

    # Sockets
    body = _cut_sockets(body, "bottom", p, sts)

    # M3 web shell grid + elbow + joint (along Z)
    pat = patterns(p)
    web_pts = _web_points(pat["web_shell_bot_m3"]["holes"])
    web_pts += [(x, y) for x, y, z in pat["elbow_m3"]["bottom"]]
    web_pts += [(x, y) for x, y, z in pat["joint_m3"]["bottom"]]
    body = _cut_cyls_z(body, web_pts, p["z_outer_bot"] - 12.0, 24.0, p["m3_d"] / 2)

    # M3 side grid through the walls (along X), both sides
    yz = _side_hole_points(p)
    body = _cut_cyls_x(body, yz, -p["x_bot_wall_out"] - 1.0, p["wall"] * 2 + tab_t + 4.0, p["m3_d"] / 2, sign=1)
    body = _cut_cyls_x(body, yz, p["x_bot_wall_out"] + 1.0, p["wall"] * 2 + tab_t + 4.0, p["m3_d"] / 2, sign=-1)
    # Splice M3 at y_cut+0, z=0, through the pads
    body = _cut_cyls_x(body, [(p["y_cut"], 0.0)],
                       -p["x_bot_wall_out"] - tab_t - 1.0,
                       tab_t + 2.0, p["m3_d"] / 2, sign=1)
    body = _cut_cyls_x(body, [(p["y_cut"], 0.0)],
                       p["x_bot_wall_out"] + tab_t + 1.0,
                       tab_t + 2.0, p["m3_d"] / 2, sign=-1)

    body = _cable_slots(body, p, sts, "bottom")
    return body, recs


def plate_top(p=P):
    """Full upper U-plate (no wrist flange). Not yet split."""
    sts = stations(p)
    ye = y_end(p)
    y0 = p["flange_t"]  # sits against the back of the bottom-plate flange
    x_lip = p["x_bot_wall_out"] + p["lip"]
    web = _box(-x_lip, x_lip,
               y0, ye,
               p["z_inner_top"], p["z_outer_top"])
    wL = _box(-p["x_top_wall_out"], -p["x_top_wall_in"],
              y0, ye,
              -p["wall_overlap_z"], p["z_outer_top"])
    wR = _box(p["x_top_wall_in"], p["x_top_wall_out"],
              y0, ye,
              -p["wall_overlap_z"], p["z_outer_top"])
    bosses, recs = _socket_bosses("top", p, sts)
    tab_t = 3.5
    y_c = p["y_cut"]
    pads = []
    for sign in (-1, 1):
        # tab just outside the top wall (in the nest gap it would collide with
        # the bottom wall). Put it outside the BOTTOM wall instead, as a lug
        # hanging from the top web via a short rib? Simpler: lug on the top
        # web, at the same X as the bottom splice, connected by a thin rib
        # from the top wall outward at z=0..6 and at the web.
        x_a = sign * p["x_bot_wall_out"]
        x_b = sign * (p["x_bot_wall_out"] + tab_t)
        x0, x1 = (x_a, x_b) if x_a < x_b else (x_b, x_a)
        # vertical rib from the top wall out to the lug, plus the lug itself
        x_rib0 = sign * p["x_top_wall_out"]
        x_rib1 = x_b
        rx0, rx1 = (x_rib0, x_rib1) if x_rib0 < x_rib1 else (x_rib1, x_rib0)
        pads.append(_box(rx0, rx1, y_c - p["lap"] / 2, y_c + p["lap"] / 2, -6.0, 6.0))
    body = fuse_fuzzy([web, wL, wR] + bosses + pads)

    spool_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "top"]
    idler_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "bottom"]
    body = _cut_cyls_z(body, spool_pts, p["z_inner_top"] - 1.0, p["web_t"] + 12.0, p["spool_cut_d"] / 2)
    body = _cut_cyls_z(body, idler_pts, p["z_inner_top"] - 1.0, p["web_t"] + 2.0, p["idler_cut_d"] / 2)

    m2_pts = []
    for s in sts:
        if s["face"] != "bottom":
            continue
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            m2_pts.append((x, y))
    body = _cut_cyls_z(body, m2_pts, p["z_inner_top"] - 1.0, p["web_t"] + 2.0, p["m2_clear"] / 2)

    body = _cut_sockets(body, "top", p, sts)

    pat = patterns(p)
    web_pts = _web_points(pat["web_shell_top_m3"]["holes"])
    web_pts += [(x, y) for x, y, z in pat["elbow_m3"]["top"]]
    web_pts += [(x, y) for x, y, z in pat["joint_m3"]["top"]]
    body = _cut_cyls_z(body, web_pts, p["z_inner_top"] - 2.0, 24.0, p["m3_d"] / 2)

    yz = _side_hole_points(p)
    body = _cut_cyls_x(body, yz, -p["x_top_wall_out"] - 1.0, p["wall"] + 4.0, p["m3_d"] / 2, sign=1)
    body = _cut_cyls_x(body, yz, p["x_top_wall_out"] + 1.0, p["wall"] + 4.0, p["m3_d"] / 2, sign=-1)
    body = _cut_cyls_x(body, [(p["y_cut"], 0.0)],
                       -p["x_bot_wall_out"] - tab_t - 1.0,
                       tab_t + 2.0, p["m3_d"] / 2, sign=1)
    body = _cut_cyls_x(body, [(p["y_cut"], 0.0)],
                       p["x_bot_wall_out"] + tab_t + 1.0,
                       tab_t + 2.0, p["m3_d"] / 2, sign=-1)

    body = _cable_slots(body, p, sts, "top")
    return body, recs


def split_plate(full, is_top, p=P):
    """Split a full plate into wrist and elbow halves with a 16 mm web half-lap."""
    ye = y_end(p)
    y_c = p["y_cut"]
    lap = p["lap"]
    y_lo, y_hi = y_c - lap / 2, y_c + lap / 2
    # Bounding box big enough to use as a cutter
    X, Z = 80.0, 80.0
    if is_top:
        z_in, z_out, z_mid = p["z_inner_top"], p["z_outer_top"], (p["z_inner_top"] + p["z_outer_top"]) / 2
    else:
        z_in, z_out, z_mid = p["z_inner_bot"], p["z_outer_bot"], (p["z_inner_bot"] + p["z_outer_bot"]) / 2
        # for the bottom plate, "outer" is more negative; mid is between them
        # inner = -17.5, outer = -21.5, mid = -19.5
        # outer half = z_out .. z_mid  (the palmar 2 mm)
        # inner half = z_mid .. z_in   (the cavity-side 2 mm)

    # Wrist keeps y < y_hi, but in the lap zone the INNER half of the web is removed.
    # Elbow keeps y > y_lo, but in the lap zone the OUTER half of the web is removed.
    # Also cut the walls at the mid-plane of the joint so they butt at y_c,
    # except the splice pads which span the lap (already on the solid).

    # Cutter to isolate the wrist half: remove everything with y > y_hi,
    # and in the lap, remove the inner half of the WEB only (not the pads,
    # which sit outboard of x_bot_wall_out).
    beyond_wrist = _box(-X, X, y_hi, ye + 20.0, -Z, Z)
    beyond_elbow = _box(-X, X, -20.0, y_lo, -Z, Z)

    # Inner/outer web slabs in the lap, limited to the web width (not the pads).
    xw = p["x_top_wall_out"] if is_top else p["x_bot_wall_out"]
    # slightly inside the pads (pads start at x_bot_wall_out)
    xw_cut = p["x_bot_wall_out"] + p["lip"] + 0.2
    if is_top:
        inner_slab = _box(-xw_cut, xw_cut, y_lo, y_hi, z_in - 0.05, z_mid)
        outer_slab = _box(-xw_cut, xw_cut, y_lo, y_hi, z_mid, z_out + 0.05)
    else:
        # z_out < z_mid < z_in  (all negative)
        inner_slab = _box(-xw_cut, xw_cut, y_lo, y_hi, z_mid, z_in + 0.05)
        outer_slab = _box(-xw_cut, xw_cut, y_lo, y_hi, z_out - 0.05, z_mid)

    # Walls should butt at y_c: remove wall material (not web, not pads) on
    # the wrong side of y_c. Wall X ranges:
    # top walls |x| = x_top_wall_in .. x_top_wall_out
    # bot walls |x| = x_bot_wall_in .. x_bot_wall_out
    # Pads |x| > x_bot_wall_out. So cutting |x| <= x_bot_wall_out + 0? pads start at x_bot_wall_out.
    # Cut walls only: for each side, the wall X band, y from y_c to y_hi (wrist keeps walls only to y_c)
    def wall_cutters(y_a, y_b):
        cuts = []
        # top-wall band and bot-wall band, both sides, full Z
        for x0, x1 in ((-p["x_bot_wall_out"] + 0.05, -p["x_inner"] + 0.0),
                       (p["x_inner"] - 0.0, p["x_bot_wall_out"] - 0.05)):
            cuts.append(_box(x0, x1, y_a, y_b, -Z, Z))
        return cuts

    wrist = full.cut(beyond_wrist).cut(inner_slab)
    for c in wall_cutters(y_c, y_hi + 0.01):
        wrist = wrist.cut(c)

    elbow = full.cut(beyond_elbow).cut(outer_slab)
    for c in wall_cutters(y_lo - 0.01, y_c):
        elbow = elbow.cut(c)

    return wrist, elbow


# ---------------------------------------------------------------------------
# Tube paths (centreline of each PTFE, used by verify and the renderer)
# ---------------------------------------------------------------------------
def _vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def _vadd(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def _smul(s, a):
    return (s * a[0], s * a[1], s * a[2])

def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def _vlen(a):
    return math.sqrt(_dot(a, a))

def _norm(a):
    L = _vlen(a)
    return (a[0] / L, a[1] / L, a[2] / L) if L > 1e-12 else (0.0, 0.0, 0.0)


def fillet_path(pts, r=30.0, n=10):
    """Replace each sharp corner with a circular arc of radius r (or the
    largest radius that fits, if a leg is short). Densely sampled so a
    circumradius check on the result is meaningful."""
    clean = [pts[0]]
    for q in pts[1:]:
        if _vlen(_vsub(q, clean[-1])) > 0.05:
            clean.append(q)
    pts = clean
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        inc, outg = _vsub(p1, p0), _vsub(p2, p1)
        l1, l2 = _vlen(inc), _vlen(outg)
        if l1 < 0.2 or l2 < 0.2:
            continue
        incu, outu = _norm(inc), _norm(outg)
        turn = math.acos(max(-1.0, min(1.0, _dot(incu, outu))))
        if turn < math.radians(8):
            continue
        r_use = r
        t = r_use * math.tan(turn / 2.0)
        avail = min(l1, l2) * 0.45
        if t > avail:
            r_use = avail / math.tan(turn / 2.0)
            t = r_use * math.tan(turn / 2.0)
        if r_use < 5.0 or t < 0.5:
            out.append(p1)
            continue
        a = _vadd(p1, _smul(-t, incu))
        b = _vadd(p1, _smul(t, outu))
        cr = _cross(incu, outu)
        nrm = _norm(_cross(incu, cr))
        if _vlen(nrm) < 0.5:
            out.append(p1)
            continue
        c1 = _vadd(a, _smul(r_use, nrm))
        c2 = _vadd(a, _smul(-r_use, nrm))
        center = c1 if _vlen(_vsub(c1, b)) < _vlen(_vsub(c2, b)) else c2
        va, vb = _vsub(a, center), _vsub(b, center)
        axis = _cross(va, vb)
        if _vlen(axis) < 1e-9:
            out.append(a)
            out.append(b)
            continue
        axis = _norm(axis)
        ang = math.acos(max(-1.0, min(1.0, _dot(_norm(va), _norm(vb)))))
        for k in range(n + 1):
            th = ang * k / n
            axv = _cross(axis, va)
            rot = _vadd(_vadd(_smul(math.cos(th), va), _smul(math.sin(th), axv)),
                        _smul(_dot(axis, va) * (1 - math.cos(th)), axis))
            out.append(_vadd(center, rot))
    out.append(pts[-1])
    return out


def tube_paths(p=P):
    """Centreline of each PTFE, Wrist_Interface corridor -> socket entrance.
    Same-face, same-lip pairs so tubes of different fingers do not cross
    and stay at least 8 mm apart. Sharp corners are filleted at r_min."""
    sts = stations(p)
    paths = []
    x_out = p["x_bot_wall_out"] + p["lip"] + 1.5  # 38.0, just outboard of the lip
    corr = {
        "thumb":  (-x_out, 0.0, -36.0),   # palmar, radial opening (widened)
        "index":  (-20.0, 0.0, -18.0),    # palmar-radial, inboard of the thumb climb
        "middle": (0.0, 0.0, 12.0),       # dorsal, through the Ø34 window
        "ring":   (x_out, 0.0, -30.0),    # palmar, ulnar side corridor
    }
    for s in sts:
        face = s["face"]
        gz = groove_zs(face, p)
        y_ent, y_ex = sock_ys(s["y"], p)
        xs = sock_xs(s["finger"], p)
        lx = LIP_SIGN[s["finger"]] * x_out
        z_run = sum(gz) / 2.0
        cx, cy, cz = corr[s["finger"]]
        for k, (sx, sz) in enumerate(((xs[0], gz[0]), (xs[1], gz[1]))):
            pts = [(cx, 0.0, cz)]
            if s["finger"] == "thumb":
                # Climb the outside of the radial wall (constant x=-38).
                pts.append((lx, y_ent, z_run))
                pts.append((sx, y_ent, sz))
            elif s["finger"] == "middle":
                # From the window out to the ulnar lip, with 36 mm of Y
                # so the 38 mm X change fillets at r>=30.
                pts.append((lx, 36.0, z_run))
                pts.append((lx, y_ent, z_run))
                pts.append((sx, y_ent, sz))
            elif s["finger"] == "index":
                # Run inboard (x=-20) so the thumb climb at x=-38 stays >= 8 mm away,
                # then fillet out to the lip sockets with 36 mm of Y.
                y_jog = y_ent - 36.0
                pts.append((-20.0, max(y_jog, 20.0), z_run))
                pts.append((sx, y_ent, sz))
            else:
                # ring: already on the palmar face, same X as the corridor
                pts.append((lx, y_ent, z_run))
                pts.append((sx, y_ent, sz))
            # drop nearly-duplicate points (sx ~= lx)
            clean = [pts[0]]
            for q in pts[1:]:
                if _vlen(_vsub(q, clean[-1])) > 1.0:
                    clean.append(q)
            pts = clean
            ptfe = fillet_path(pts, r=p["r_min"], n=10)
            ptfe.append((sx, y_ex, sz))  # short tendon inside the socket, not a PTFE bend
            paths.append(dict(i=s["i"], finger=s["finger"], ab=s["ab"], k=k,
                              face=face, pts=ptfe, pts_ptfe=ptfe[:-1],
                              socket=(sx, y_ent, y_ex, sz)))
    return paths


def min_bend_radius(pts):
    """Smallest circumradius of three consecutive distinct points. Straight
    sections (area ~ 0) are ignored (infinite radius)."""
    rmin = 1e9
    for i in range(len(pts) - 2):
        ax, ay, az = pts[i]
        bx, by, bz = pts[i + 1]
        cx, cy, cz = pts[i + 2]
        ab = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)
        bc = math.sqrt((cx - bx) ** 2 + (cy - by) ** 2 + (cz - bz) ** 2)
        ca = math.sqrt((cx - ax) ** 2 + (cy - ay) ** 2 + (cz - az) ** 2)
        if ab < 1e-6 or bc < 1e-6 or ca < 1e-6:
            continue
        # triangle area via cross product
        ABx, ABy, ABz = bx - ax, by - ay, bz - az
        ACx, ACy, ACz = cx - ax, cy - ay, cz - az
        crx = ABy * ACz - ABz * ACy
        cry = ABz * ACx - ABx * ACz
        crz = ABx * ACy - ABy * ACx
        area2 = math.sqrt(crx * crx + cry * cry + crz * crz)
        if area2 < 1e-6:
            continue
        r = ab * bc * ca / area2  # 2*area = area2, r = abc / (4A) wait:
        # circumradius R = abc / (4A), 2A = area2 so 4A = 2*area2, R = abc/(2*area2)
        r = ab * bc * ca / (2.0 * area2)
        if r < rmin:
            rmin = r
    return rmin


def build_all(p=P):
    top, recT = plate_top(p)
    bot, recB = plate_bottom(p)
    top_w, top_e = split_plate(top, True, p)
    bot_w, bot_e = split_plate(bot, False, p)
    sp = spool_r8(p)
    recs = recT + recB
    return dict(
        plate_top=top, plate_bottom=bot,
        plate_top_wrist=top_w, plate_top_elbow=top_e,
        plate_bottom_wrist=bot_w, plate_bottom_elbow=bot_e,
        spool_r8=sp, recs=recs, p=p,
        stations=stations(p), patterns=patterns(p),
        paths=tube_paths(p),
        y_end=y_end(p),
    )


def _export(name, wp, dest_step, dest_stl):
    cq.exporters.export(wp, dest_step)
    cq.exporters.export(wp, dest_stl)
    bb = wp.val().BoundingBox()
    solids = wp.solids().vals() if hasattr(wp, "solids") else [wp.val()]
    n = len(solids)
    print(f"{name:28s}  {bb.xlen:7.1f} x {bb.ylen:7.1f} x {bb.zlen:6.1f} mm   "
          f"vol {wp.val().Volume():.0f} mm3  solids={n}")
    return bb


if __name__ == "__main__":
    out_step = STEP_DIR if os.path.isdir(STEP_DIR) else HERE
    out_stl = STL_DIR if os.path.isdir(STL_DIR) else HERE
    print("v11 stations (wrist -> elbow):")
    for s in stations():
        print(f"  {s['i']}: {s['finger']:6s} {s['ab']}  face={s['face']:6s}  "
              f"side={s['side']:5s}  shaft=({s['xf']:+.2f}, {s['y']:.1f}, {s['zf']:+.1f})")
    print(f"y_end = {y_end():.1f} mm  y_cut = {P['y_cut']:.1f} mm")
    parts = build_all()
    names = (
        ("plate_top_wrist", "forearm_plate_top_wrist"),
        ("plate_top_elbow", "forearm_plate_top_elbow"),
        ("plate_bottom_wrist", "forearm_plate_bottom_wrist"),
        ("plate_bottom_elbow", "forearm_plate_bottom_elbow"),
        ("plate_top", "forearm_plate_top_full"),
        ("plate_bottom", "forearm_plate_bottom_full"),
        ("spool_r8", "spool_r8"),
    )
    for key, fn in names:
        _export(fn, parts[key],
                os.path.join(out_step, fn + ".step"),
                os.path.join(out_stl, fn + ".stl"))
    # Pattern summary
    pat = parts["patterns"]
    print("\n--- mounting patterns ---")
    for k, v in pat.items():
        print(f"  {k}: {v.get('name_fr','')}")
        if "positions" in v:
            print(f"      {len(v['positions'])} holes: {v['positions']}")
        if "holes" in v:
            print(f"      {len(v['holes'])} holes")
        if "top" in v:
            print(f"      top {len(v['top'])}, bottom {len(v.get('bottom',[]))}")
