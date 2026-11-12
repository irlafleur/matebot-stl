# MateBot v10 (UNTESTED): printable open-rack forearm chassis for 8 x
# Feetech STS3215 (12 V), fixed wrist to R-Wrist_Interface.
# Layout: "3-3-2" as two side rails of 3 (index, middle, ring: A radial,
# B ulnar) plus a thumb pair of 2 at the wrist, with pairs alternating
# faces along the arm (TL, TR, BL, BR, repeat):
#   thumb  = top (dorsal), index = bottom (palmar),
#   middle = top,          ring  = bottom.
# The rack is a mid-plane plate, open on both faces so spools, sockets
# and tube lanes live above AND below, without crossings.
# CadQuery. MateBot, CC BY 4.0.
#
# Usage:
#   python forearm_mount_332.py
# writes STEP/STL next to this file, or into ../step and ../stl when those exist.
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

P = dict(
    cl=CL,                  # 0.4 mm around the body, not a datasheet figure
    wall=3.5, floor_t=4.0,  # printed walls / mid-plane plate of the rack
    gap_y=8.0,
    spool_r=8.0, spool_flange=3.0, spool_base_t=2.0, groove_w=3.0, mid_flange=1.5,
    spool_top_t=2.0,
    sock_d=4.2, sock_depth=8.0, tendon_d=2.2, tube_od=4.0,
    r_min=30.0,
    m3_d=3.4, m3_nut=6.6, m2_clear=2.4,
    flange_t=6.0,
    register_d=33.6, register_t=2.0,
    rib_h=12.0,             # short locating ribs on the ACTIVE face only
)

P['spool_h'] = P['spool_base_t'] + P['groove_w'] + P['mid_flange'] + P['groove_w'] + P['spool_top_t']  # 11.5
P['pitch'] = BODY_L + P['gap_y']  # 53.22
P['y_thumb'] = P['flange_t'] + 12.0 + 14.0          # 32.0
P['y_index'] = P['y_thumb'] + P['pitch'] + 4.0      # 89.22
P['y_middle'] = P['y_index'] + P['pitch']           # 142.44
P['y_ring'] = P['y_middle'] + P['pitch']            # 195.66
P['y_end'] = P['y_ring'] + SHAFT_FROM_CABLE + 8.0   # ~238.8

P['centre_gap'] = 16.0
P['rail_cx'] = P['centre_gap'] / 2 + P['wall'] + (BODY_W + P['cl']) / 2   # 24.06

# Mid-plane of the open rack at z=0. Plate spans z = -floor_t/2 .. +floor_t/2.
P['z_mid'] = 0.0
P['z_top_face'] = P['floor_t'] / 2          # +2.0, idler ears of TOP servos
P['z_bot_face'] = -P['floor_t'] / 2         # -2.0, idler ears of BOTTOM servos
P['z_shaft_top'] = P['z_top_face'] + H_TO_HORN   # +37.0
P['z_shaft_bot'] = P['z_bot_face'] - H_TO_HORN   # -37.0

# Thumb pair, closer together, shifted radial, on the TOP face (TL, TR).
P['thumb_cx'] = -12.0
P['thumb_half'] = (BODY_W + P['cl']) / 2 + 4.0     # 16.56
P['lane_w'] = 10.0

# TL, TR, BL, BR, repeat from the wrist to the elbow.
FACE = dict(thumb="top", index="bottom", middle="top", ring="bottom")


def f_to_hand(xf, yf, zf):
    return (xf + WI_CX, WI_CY - yf, zf - 11.50)

def hand_to_f(x, y, z):
    return (x - WI_CX, WI_CY - y, z + 11.50)

def servo_face(finger):
    return FACE[finger]

def z_shaft_of(finger, p=P):
    return p['z_shaft_top'] if servo_face(finger) == "top" else p['z_shaft_bot']

def z_face_of(finger, p=P):
    return p['z_top_face'] if servo_face(finger) == "top" else p['z_bot_face']

def groove_zs(finger, p=P):
    """Z of the two spool grooves in F, on the spool's outward side."""
    z0 = z_shaft_of(finger, p)
    d1 = p['spool_base_t'] + p['groove_w'] / 2
    d2 = p['spool_base_t'] + p['groove_w'] + p['mid_flange'] + p['groove_w'] / 2
    if servo_face(finger) == "top":
        return (z0 + d1, z0 + d2)
    return (z0 - d1, z0 - d2)

def place_S(shape, xf, yf, zf, face="top"):
    """Map a solid in servo frame S into F.
    +X_s along +y_f (cable to the elbow).
    Top:    +Z_s along +z_f (spool dorsal).
    Bottom: +Z_s along -z_f (spool palmar), after a 180 deg rotation about X_s."""
    if face == "bottom":
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    return shape.rotate((0, 0, 0), (0, 0, 1), 90).translate((xf, yf, zf))

def loc_S(xf, yf, zf, face="top"):
    from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
    acc = gp_Trsf()
    if face == "bottom":
        rx = gp_Trsf()
        rx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.radians(180))
        acc = rx
    rz = gp_Trsf()
    rz.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(90))
    acc = rz.Multiplied(acc)
    tt = gp_Trsf()
    tt.SetTranslation(gp_Vec(xf, yf, zf))
    return cq.Location(tt.Multiplied(acc))

def loc_S_on_rail(xf, yf, zf, face="top"):
    return loc_S(xf, yf, zf, face)

FINGERS_RAIL = ("index", "middle", "ring")

def _ys():
    return dict(thumb=P['y_thumb'], index=P['y_index'], middle=P['y_middle'], ring=P['y_ring'])

def servo_xf(finger, ab):
    """ab: 'A' = radial (left, -x), 'B' = ulnar (right, +x)."""
    if finger == "thumb":
        return P['thumb_cx'] + (-P['thumb_half'] if ab == "A" else P['thumb_half'])
    return (-P['rail_cx'] if ab == "A" else P['rail_cx'])

def servo_loc(finger, ab):
    return loc_S(servo_xf(finger, ab), _ys()[finger], z_shaft_of(finger), servo_face(finger))

def m2_xy(xf, y_shaft, Xs, Ys, face):
    """Idler-ear hole in F. Top: x = xf - Ys (Y_s -> -X_f). Bottom: x = xf + Ys."""
    if face == "top":
        return xf - Ys, y_shaft + Xs
    return xf + Ys, y_shaft + Xs


# ---------------------------------------------------------------------------
# Spool, official horn pattern (BCD 14 mm from the Waveshare 2D drawing).
# ---------------------------------------------------------------------------
def spool_r8(p=P):
    r, fl = p['spool_r'], p['spool_flange']
    h = cq.Workplane("XY").circle(r + fl).extrude(p['spool_base_t'])
    h = h.faces(">Z").workplane().circle(r).extrude(p['groove_w'])
    h = h.faces(">Z").workplane().circle(r + 2.0).extrude(p['mid_flange'])
    h = h.faces(">Z").workplane().circle(r).extrude(p['groove_w'])
    h = h.faces(">Z").workplane().circle(r + fl).extrude(p['spool_top_t'])
    h = h.faces(">Z").workplane().hole(6.5)
    h = h.faces(">Z").workplane().pushPoints(horn_holes_xy()).hole(3.4)
    z1 = p['spool_base_t'] + p['groove_w'] / 2
    z2 = p['spool_base_t'] + p['groove_w'] + p['mid_flange'] + p['groove_w'] / 2
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


def _pocket_cut(xf, y_shaft, face, p):
    """Subtract from the rack: body pocket on the ACTIVE face, idler-horn
    counterbore from that face, M2 through the plate, cable notch toward the elbow."""
    cl = p['cl']
    x0 = xf - (BODY_W + cl) / 2
    x1 = xf + (BODY_W + cl) / 2
    y0 = y_shaft - SHAFT_FROM_OUT - cl
    y1 = y_shaft + SHAFT_FROM_CABLE + cl
    sign = 1.0 if face == "top" else -1.0
    z_face = p['z_top_face'] if face == "top" else p['z_bot_face']
    # Body pocket, open outward, starts 0.2 mm off the plate so the plate stays.
    body = (cq.Workplane("XY").box(x1 - x0, y1 - y0, 50, centered=False)
            .translate((x0, y0, z_face + sign * 0.2 if face == "top" else z_face - 50)))
    if face == "top":
        body = (cq.Workplane("XY").box(x1 - x0, y1 - y0, 50, centered=False)
                .translate((x0, y0, z_face + 0.2)))
    else:
        body = (cq.Workplane("XY").box(x1 - x0, y1 - y0, 50, centered=False)
                .translate((x0, y0, z_face - 50)))
    # Idler horn counterbore from the servo face, 3.0 mm into the 4 mm plate
    # (horn protrudes 2.25 mm), not through, so the opposite face stays mostly closed
    # except for the M2 through-holes (screwdriver access from the clear face).
    if face == "top":
        horn = (cq.Workplane("XY").workplane(offset=z_face - 3.0)
                .center(xf, y_shaft).circle((HORN_OD + 1.6) / 2).extrude(3.5))
    else:
        horn = (cq.Workplane("XY").workplane(offset=z_face - 0.5)
                .center(xf, y_shaft).circle((HORN_OD + 1.6) / 2).extrude(3.5))
    cuts = body.union(horn)
    z_plate0 = p['z_bot_face'] - 1
    for Xs, Ys in IDL_HOLES:
        xh, yh = m2_xy(xf, y_shaft, Xs, Ys, face)
        cuts = cuts.union(cq.Workplane("XY").workplane(offset=z_plate0)
                          .center(xh, yh).circle(p['m2_clear'] / 2).extrude(p['floor_t'] + 2))
    # Cable notch at the cable end, on the active face, open toward the elbow
    # and toward the centre gap, so the daisy-chain can drop into the spine.
    cy0 = y_shaft + SHAFT_FROM_CABLE - 6
    if face == "top":
        cable = cq.Workplane("XY").box(x1 - x0 - 4, 24, 16, centered=False).translate((x0 + 2, cy0, z_face + 2))
    else:
        cable = cq.Workplane("XY").box(x1 - x0 - 4, 24, 16, centered=False).translate((x0 + 2, cy0, z_face - 18))
    return cuts.union(cable)


def _face_ribs(xf, y_shaft, face, side, p):
    """Short locating ribs on the ACTIVE face only, at the two X sides of the body.
    The opposite face at this Y stays open (spool / screwdriver / tube clearance)."""
    cl = p['cl']
    half = (BODY_W + cl) / 2
    y0 = y_shaft - SHAFT_FROM_OUT - cl
    y1 = y_shaft + SHAFT_FROM_CABLE + cl
    z_face = p['z_top_face'] if face == "top" else p['z_bot_face']
    z0 = z_face if face == "top" else z_face - p['rib_h']
    ribs = []
    for xa, xb in ((xf - half - p['wall'], xf - half),
                   (xf + half, xf + half + p['wall'])):
        lo, hi = (xa, xb) if xa < xb else (xb, xa)
        ribs.append(cq.Workplane("XY").box(hi - lo, y1 - y0, p['rib_h'], centered=False)
                    .translate((lo, y0, z0)))
    return fuse_fuzzy(ribs) if len(ribs) > 1 else ribs[0]


def _socket_block(xf, y_shaft, inner_sign, face, finger, p):
    """Two Ø4.2 x 8 sockets on the INNER side of the spool, on the SAME face
    as the spool (top or bottom). Not in front of the spool, so they do not
    eat the gap between stations. PTFE arrives from the wrist."""
    z_g1, z_g2 = groove_zs(finger, p)
    y_stop = y_shaft - 2.0
    y_back = y_stop - p['sock_depth']
    x_axis = xf + inner_sign * (BODY_W / 2 + 5.0)
    hw, hz = 5.0, 8.0
    z_mid = 0.5 * (z_g1 + z_g2)
    y_mid = 0.5 * (y_back - 1 + y_shaft + 4)
    blk = (cq.Workplane("XY").workplane(offset=z_mid - hz)
           .center(x_axis, y_mid)
           .box(2 * hw, (y_shaft + 4) - (y_back - 1), 2 * hz, centered=True))
    # Pillar from the mid-plane plate out to the socket block, same X, this face only.
    z_face = p['z_top_face'] if face == "top" else p['z_bot_face']
    z_lo, z_hi = (min(z_face, z_mid - hz), max(z_face, z_mid + hz))
    pillar = (cq.Workplane("XY").box(2 * hw, 8.0, z_hi - z_lo, centered=False)
              .translate((x_axis - hw, y_back - 1, z_lo)))
    blk = fuse_fuzzy([blk, pillar])
    for z in (z_g1, z_g2):
        bore = cq.Workplane("XZ").workplane(offset=y_back).center(x_axis, z).circle(p['sock_d'] / 2).extrude(p['sock_depth'])
        hole = cq.Workplane("XZ").workplane(offset=y_back - 1).center(x_axis, z).circle(p['tendon_d'] / 2).extrude((y_stop + 10) - (y_back - 1))
        blk = blk.cut(bore).cut(hole)
    return blk, (x_axis, y_back, y_stop, z_g1, z_g2)


def _thumb_bed_end(p):
    return p['y_thumb'] + SHAFT_FROM_CABLE + 6.0

def _lap_xs(side, p):
    xf = servo_xf("index", "A" if side < 0 else "B")
    inner = -side
    half = (BODY_W + p['cl']) / 2
    return xf + inner * (half + 3.0), xf + inner * (half + 7.0)

def _lap_ys(p):
    y0 = _thumb_bed_end(p) + 1.0
    return [y0 + 8.0, y0 + 22.0, y0 + 36.0]

def _gap_ys(p):
    """Y midpoints of the 8 mm body gaps, for mid-plane-adjacent braces
    that must not sit under a servo."""
    def body_end(ysh):
        return ysh + SHAFT_FROM_CABLE
    def body_start(ysh):
        return ysh - SHAFT_FROM_OUT
    return [
        0.5 * (body_end(p['y_index']) + body_start(p['y_middle'])),
        0.5 * (body_end(p['y_middle']) + body_start(p['y_ring'])),
        p['y_end'] - 6.0,
    ]


def rail(side, p=P):
    """side = -1 radial (A), +1 ulnar (B). Open mid-plane rack, pockets on
    both faces according to FACE (index bottom, middle top, ring bottom)."""
    xf = servo_xf("index", "A" if side < 0 else "B")
    inner = -side
    half = (BODY_W + p['cl']) / 2
    y_body0 = _thumb_bed_end(p) + 1.0
    y0, y1 = y_body0, p['y_end']
    x_out = xf + side * (half + p['wall'])
    x_in  = xf + inner * (half + p['wall'] + 8.0)
    x_lo, x_hi = (x_in, x_out) if x_in < x_out else (x_out, x_in)
    z0 = p['z_bot_face']
    plate = (cq.Workplane("XY").box(x_hi - x_lo, y1 - y0, p['floor_t'], centered=False)
             .translate((x_lo, y0, z0)))
    # Half-lap on the inner shelf: from y0 back a little, only the UPPER half
    # (z = 0.1 .. +2), so the yoke tab (z = -2 .. -0.1) can sit under it.
    tab_y0 = y0 - 0.4
    tab_w = 10.0
    t_in = xf + inner * (half + 1.0)
    t_out = xf + inner * (half + 1.0 + tab_w)
    tlo, thi = (t_in, t_out) if t_in < t_out else (t_out, t_in)
    # Cut the lower half of the plate away in the lap Y band, on the inner 10 mm.
    y_lap1 = max(_lap_ys(p)) + 8.0
    lower_cut = (cq.Workplane("XY").box(thi - tlo + 0.4, y_lap1 - tab_y0 + 1.0, p['floor_t'] / 2 + 0.1, centered=False)
                 .translate((min(tlo, t_in) - 0.2, tab_y0 - 0.5, z0 - 0.05)))
    plate = plate.cut(lower_cut)
    # Add the upper-half tab that extends slightly back toward the yoke.
    tab = (cq.Workplane("XY").box(thi - tlo, y0 + 2.0 - tab_y0, p['floor_t'] / 2 - 0.1, centered=False)
           .translate((tlo, tab_y0, 0.1)))
    rail = plate.union(tab)

    recs = []
    for f, ysh in zip(FINGERS_RAIL, (p['y_index'], p['y_middle'], p['y_ring'])):
        face = servo_face(f)
        rail = rail.union(_face_ribs(xf, ysh, face, side, p))
        rail = rail.cut(_pocket_cut(xf, ysh, face, p))
        blk, rec = _socket_block(xf, ysh, inner, face, f, p)
        rail = rail.union(blk)
        recs.append(dict(finger=f, ab=("A" if side < 0 else "B"), side=side,
                         face=face, xf=xf, y_shaft=ysh, sock=rec))

    rail = fuse_fuzzy([rail])
    lap_x = _lap_xs(side, p)
    lap_ys = _lap_ys(p)
    for y in lap_ys:
        for x in lap_x:
            hole = (cq.Workplane("XY").workplane(offset=p['z_bot_face'] - 1)
                    .center(x, y).circle(p['m3_d'] / 2).extrude(p['floor_t'] + 2))
            rail = rail.cut(hole)
    # Brace holes through the inner (and a little of the outer) shelf, in the body gaps.
    for yb in _gap_ys(p):
        for dx in (inner * (half + 2.0), side * (half - 2.0)):
            hole = (cq.Workplane("XY").workplane(offset=p['z_bot_face'] - 1)
                    .center(xf + dx, yb).circle(p['m3_d'] / 2).extrude(p['floor_t'] + 2))
            rail = rail.cut(hole)
    rail = rail.combine()
    return rail, recs, dict(y0=y0, y1=y1, x_lo=x_lo, x_hi=x_hi, lap_x=lap_x, lap_ys=lap_ys, xf=xf)


def rail_L(p=P):
    return rail(-1, p)

def rail_R(p=P):
    return rail(+1, p)


def _thumb_sockets(p):
    """Shared 4-socket block in front of the thumb pair, on the TOP (dorsal)
    face, slightly radial, tubes leaving toward a palmar-radial drop."""
    z_g1, z_g2 = groove_zs("thumb", p)
    y_shaft = p['y_thumb']
    y_stop = min(y_shaft - (p['spool_r'] + 6.0), 16.5)
    y_back = y_stop - p['sock_depth']
    x_mid = p['thumb_cx'] - 4.0
    xs = (x_mid - 5.0, x_mid + 5.0)
    zs = (z_g1, z_g2)
    hw, hl, hz = 12.0, (y_stop + 4) - (y_back - 2), 8.0
    z_mid = 0.5 * (z_g1 + z_g2)
    y_mid = 0.5 * (y_back - 2 + y_stop + 4)
    blk = (cq.Workplane("XY").workplane(offset=z_mid - hz)
           .center(x_mid, y_mid)
           .box(2 * hw, hl, 2 * hz, centered=True))
    # Pillar UP from the mid-plane only — the palmar side under the thumb
    # stays open so index/ring tubes can run underneath.
    z_lo, z_hi = p['z_top_face'], z_mid + hz
    pillar = (cq.Workplane("XY").box(2 * hw, 12.0, z_hi - z_lo, centered=False)
              .translate((x_mid - hw, 7.0, z_lo)))
    blk = fuse_fuzzy([blk, pillar])
    recs = []
    for ab, x in (("A", xs[0]), ("B", xs[1])):
        for z in zs:
            bore = cq.Workplane("XZ").workplane(offset=y_back).center(x, z).circle(p['sock_d'] / 2).extrude(p['sock_depth'])
            hole = cq.Workplane("XZ").workplane(offset=y_back - 1).center(x, z).circle(p['tendon_d'] / 2).extrude((y_stop + 8) - (y_back - 1))
            blk = blk.cut(bore).cut(hole)
        recs.append(dict(finger="thumb", ab=ab, face="top",
                         xf=servo_xf("thumb", ab), y_shaft=y_shaft,
                         sock=(x, y_back, y_stop, zs[0], zs[1])))
    return blk, recs


def yoke(p=P):
    # Flange plate in Y=0..t (toward the elbow). Only the register boss sits at
    # Y=-register_t..0, inside the Ø34 window of the Wrist_Interface.
    x_lo, x_hi = -44.0, 44.0
    z_lo, z_hi = -40.0, 42.0
    t = p['flange_t']
    fl = cq.Workplane("XY").box(x_hi - x_lo, t, z_hi - z_lo, centered=False).translate((x_lo, 0, z_lo))
    for a in WI_HOLE_ANG:
        rad = math.radians(a)
        xh = WI_HOLE_R * math.cos(rad)
        zh = WI_HOLE_R * math.sin(rad)
        fl = fl.cut(cq.Solid.makeCylinder(p['m2_clear'] / 2, t + 2, cq.Vector(xh, -1, zh), cq.Vector(0, 1, 0)))
    reg = cq.Workplane("XY").add(cq.Solid.makeCylinder(p['register_d'] / 2, p['register_t'], cq.Vector(0, -p['register_t'], 0), cq.Vector(0, 1, 0)))
    win = cq.Workplane("XY").add(cq.Solid.makeCylinder((WI_WINDOW_D - 3.0) / 2, t + p['register_t'] + 2, cq.Vector(0, -p['register_t'] - 1, 0), cq.Vector(0, 1, 0)))
    fl = fl.union(reg).cut(win)

    def corridor_cut(x_mid, z_mid, w, h):
        return cq.Workplane("XY").box(w, t + 2, h, centered=True).translate((x_mid, t / 2, z_mid))
    # Tall side corridors so BOTH faces (dorsal and palmar lanes) can pass the flange.
    fl = fl.cut(corridor_cut(WI_XF[0] - p['lane_w'] / 2 - 0.5, 0.0, p['lane_w'], 44.0))
    fl = fl.cut(corridor_cut(WI_XF[1] + p['lane_w'] / 2 + 0.5, 0.0, p['lane_w'], 44.0))
    # Palmar-radial drop for the thumb (sockets are dorsal, thumb is palmar-radial).
    fl = fl.cut(corridor_cut(-20.0, WI_ZF[0] - p['lane_w'] / 2 - 0.5, 28.0, p['lane_w']))

    # Thumb pair: mid-plane plate + TOP-face ribs only. Palmar side stays open.
    y0 = t - 0.5
    y1 = _thumb_bed_end(p)
    x_a = servo_xf("thumb", "A")
    x_b = servo_xf("thumb", "B")
    half = (BODY_W + p['cl']) / 2
    x_lo_t = x_a - half - p['wall']
    x_hi_t = x_b + half + p['wall']
    floor = (cq.Workplane("XY").box(x_hi_t - x_lo_t, y1 - y0, p['floor_t'], centered=False)
             .translate((x_lo_t, y0, p['z_bot_face'])))
    bed = floor
    for ab, xf in (("A", x_a), ("B", x_b)):
        bed = bed.union(_face_ribs(xf, p['y_thumb'], "top", -1, p))
        bed = bed.cut(_pocket_cut(xf, p['y_thumb'], "top", p))
    sock_blk, recs = _thumb_sockets(p)
    bed = fuse_fuzzy([bed, sock_blk])
    key = (cq.Workplane("XY").box(x_hi_t - x_lo_t, 4.0, p['floor_t'] + 6.0, centered=False)
           .translate((x_lo_t, 3.0, p['z_bot_face'])))
    bed = bed.union(key)

    # Half-lap tabs: LOWER half of the mid-plane (z = -2 .. -0.1), long enough
    # for the 3 M3 holes beside the index (which is on the BOTTOM, so the lower
    # tab stays on the inner shelf, not in the body pocket).
    tabs = []
    y_tab0 = y1 - 4.0
    y_tab1 = max(_lap_ys(p)) + 8.0
    for side in (-1, 1):
        xf = servo_xf("index", "A" if side < 0 else "B")
        inner = -side
        halfp = (BODY_W + p['cl']) / 2
        t_in = xf + inner * (halfp + 1.0)
        t_out = xf + inner * (halfp + 1.0 + 10.0)
        tlo, thi = (t_in, t_out) if t_in < t_out else (t_out, t_in)
        shelf = (cq.Workplane("XY").box(thi - tlo, y_tab1 - y_tab0, p['floor_t'] / 2 - 0.1, centered=False)
                 .translate((tlo, y_tab0, p['z_bot_face'])))
        # Short rib at the thumb-bed end, AFTER the thumb body (cable end at
        # y_thumb + SHAFT_FROM_CABLE = 67.11), to fuse the half-lap tab to the bed.
        y_rib0 = p['y_thumb'] + SHAFT_FROM_CABLE + 1.0  # 68.11
        rib = (cq.Workplane("XY").box(thi - tlo, y1 - y_rib0, p['floor_t'] + 0.5, centered=False)
               .translate((tlo, y_rib0, p['z_bot_face'])))
        shelf = shelf.union(rib)
        for y in _lap_ys(p):
            for x in _lap_xs(side, p):
                shelf = shelf.cut(cq.Workplane("XY").workplane(offset=p['z_bot_face'] - 1)
                                  .center(x, y).circle(p['m3_d'] / 2).extrude(p['floor_t'] + 2))
        tabs.append(shelf)
    yk = fuse_fuzzy([fl, bed, tabs[0], tabs[1]])
    return yk, recs


def brace(p=P):
    """Cross-brace that bolts under the mid-plane plate in a body-gap (M3 x 4).
    The 8 mm gaps have no servo on either face, so a palmar-side brace is clear."""
    half = (BODY_W + p['cl']) / 2
    xs = []
    for side in (-1, 1):
        xf = servo_xf("index", "A" if side < 0 else "B")
        inner = -side
        xs += [xf + inner * (half + 2.0), xf + side * (half - 2.0)]
    xs = sorted(xs)
    pad = 6.0
    xlo, xhi = xs[0] - pad, xs[-1] + pad
    w, t, L = 8.0, 4.0, xhi - xlo
    b = cq.Workplane("XY").box(L, w, t, centered=False).translate((xlo, -w / 2, 0))
    for x in xs:
        b = b.cut(cq.Workplane("XY").workplane(offset=-1).center(x, 0).circle(p['m3_d'] / 2).extrude(t + 2))
    return b


def brace_placed(p=P):
    """The three braces translated to their gap Y, on the palmar side of the plate."""
    out = []
    for yb in _gap_ys(p):
        out.append(brace(p).translate((0, yb, p['z_bot_face'] - 4.0)))
    return out


def build_all(p=P):
    rL, recL, metaL = rail_L(p)
    rR, recR, metaR = rail_R(p)
    yk, recT = yoke(p)
    br = brace(p)
    sp = spool_r8(p)
    recs = recL + recR + recT
    return dict(rail_L=rL, rail_R=rR, yoke=yk, brace=br, spool_r8=sp,
                recs=recs, metaL=metaL, metaR=metaR, p=p)


def _export(name, wp, dest_step, dest_stl):
    cq.exporters.export(wp, dest_step)
    cq.exporters.export(wp, dest_stl)
    bb = wp.val().BoundingBox()
    print(f"{name:24s}  {bb.xlen:7.1f} x {bb.ylen:7.1f} x {bb.zlen:6.1f} mm   vol {wp.val().Volume():.0f} mm3")
    return bb


if __name__ == "__main__":
    out_step = STEP_DIR if os.path.isdir(STEP_DIR) else HERE
    out_stl = STL_DIR if os.path.isdir(STL_DIR) else HERE
    parts = build_all()
    for name in ("rail_L", "rail_R", "yoke", "brace", "spool_r8"):
        fn = {"rail_L": "forearm_rail_3x_L", "rail_R": "forearm_rail_3x_R",
              "yoke": "forearm_wrist_yoke", "brace": "forearm_brace",
              "spool_r8": "spool_r8"}[name]
        _export(fn, parts[name],
                os.path.join(out_step, fn + ".step"),
                os.path.join(out_stl, fn + ".stl"))
    print("y_thumb/index/middle/ring/end", P['y_thumb'], P['y_index'], P['y_middle'], P['y_ring'], P['y_end'])
    print("faces", FACE)
    print("z_shaft top/bot", P['z_shaft_top'], P['z_shaft_bot'])
