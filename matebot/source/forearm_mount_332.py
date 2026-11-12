# MateBot v9 (UNTESTED): printable forearm chassis for 8 x Feetech STS3215 (12 V)
# and the servo-end PTFE anchors, with a fixed wrist to R-Wrist_Interface.
# Layout: "3-3-2" as two side rails of 3 servos (index, middle, ring: A on the
# radial rail, B on the ulnar rail) plus a thumb pair of 2 at the wrist.
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
# 6 x D2.4 / D3.2 counterbore holes on that circle, at ±20°, ±100°, ±140°
# (from the Wrist_Interface STEP). 3 extra D2.5 at 0°, ±120° are not used.
WI_HOLE_ANG = (20.0, 100.0, 140.0, -140.0, -100.0, -20.0)
WI_WINDOW_D = 34.0
# Outline of the Wrist_Interface in F (from its bbox):
#   X -9..58  -> x_f -33.5..33.5 ;  Z -40.25..15.50 -> z_f -28.75..27.00
WI_XF = (-33.50, 33.50)
WI_ZF = (-28.75, 27.00)

P = dict(
    # servo pocket
    cl=CL,                  # 0.4 mm around the body, not a datasheet figure
    wall=3.5, floor_t=4.0,  # printed walls / floor of a rail
    gap_y=8.0,              # free space between two servo bodies along the arm
    # spool (same grooves as the v0 spool, horn pattern now from the drawing)
    spool_r=8.0, spool_flange=3.0, spool_base_t=2.0, groove_w=3.0, mid_flange=1.5,
    spool_top_t=2.0,
    # tube sockets (same as R-Hand_Plate_tendon)
    sock_d=4.2, sock_depth=8.0, tendon_d=2.2, tube_od=4.0,
    # bends
    r_min=30.0,
    # joints
    m3_d=3.4, m3_nut=6.6, m2_clear=2.4,
    # flange
    flange_t=6.0,
    register_d=33.6, register_t=2.0,   # loose fit in the Ø34 window
    # rail / pair pitch
)

P['spool_h'] = P['spool_base_t'] + P['groove_w'] + P['mid_flange'] + P['groove_w'] + P['spool_top_t']  # 11.5
P['pitch'] = BODY_L + P['gap_y']  # 53.22
# Shaft of the thumb pair, just behind the flange + a socket block + spool radius
P['y_thumb'] = P['flange_t'] + 12.0 + 14.0          # 32.0
P['y_index'] = P['y_thumb'] + P['pitch'] + 4.0      # 89.22, extra 4 mm so the index sockets clear the thumb bed
P['y_middle'] = P['y_index'] + P['pitch']           # 138.44
P['y_ring'] = P['y_middle'] + P['pitch']            # 191.66
P['y_end'] = P['y_ring'] + SHAFT_FROM_CABLE + 8.0   # ~234.8  (whole pack, split in two prints)

# Two rails: pocket centres in x. Centre gap 16 mm (cable spine + middle tube lane).
P['centre_gap'] = 16.0
P['rail_cx'] = P['centre_gap'] / 2 + P['wall'] + (BODY_W + P['cl']) / 2   # 24.06
# Floor top at z=0: idler ears sit here, output horn / spool above at z=H_TO_HORN=35
P['z_floor'] = 0.0
P['z_shaft'] = P['z_floor'] + H_TO_HORN          # 35.0
P['wall_top'] = BODY_H_FLANGE - 4.0              # walls stop below the output ears, 28 mm

# Thumb pair: same orientation (spool dorsal) but in front, closer together,
# shifted radial (thumb is at x_f ≈ -24.5, z_f ≈ -28). We keep them on the
# same (dorsal) face so the chassis stays ~55 mm deep, not 100 mm.
P['thumb_cx'] = -12.0
P['thumb_half'] = (BODY_W + P['cl']) / 2 + 4.0     # 16.56, 8 mm between the two bodies

# Side corridors for tubes that cannot go through the Ø34 window
# (index −X at hand X=-10.5 is 18 mm left of the window; ring sockets are
#  to the right of it). Grooves run along the radial and ulnar edges of the flange.
P['lane_w'] = 10.0


def f_to_hand(xf, yf, zf):
    return (xf + WI_CX, WI_CY - yf, zf - 11.50)

def hand_to_f(x, y, z):
    return (x - WI_CX, WI_CY - y, z + 11.50)

def place_S(shape, xf, yf, zf):
    """Map a solid in servo frame S into F: shaft at (xf,yf,zf),
    +X_s along +y_f (cable to the elbow), +Z_s along +z_f (spool dorsal).
    A +90 deg rotation about Z sends (x,y,z)_S to (-y, x, z), i.e.
    X_s -> +Y_f, Y_s -> -X_f, Z_s -> +Z_f, then we translate."""
    return shape.rotate((0, 0, 0), (0, 0, 1), 90).translate((xf, yf, zf))

def loc_S_on_rail(xf, yf, zf):
    """Location equivalent to place_S: rotate +90 deg about Z, then translate."""
    from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
    tr, tt = gp_Trsf(), gp_Trsf()
    tr.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(90))
    tt.SetTranslation(gp_Vec(xf, yf, zf))
    return cq.Location(tt.Multiplied(tr))


# Stations
FINGERS_RAIL = ("index", "middle", "ring")
Y_SHAFT = dict(thumb=None, index=None, middle=None, ring=None)  # filled after P is final
def _ys():
    return dict(thumb=P['y_thumb'], index=P['y_index'], middle=P['y_middle'], ring=P['y_ring'])


def servo_xf(finger, ab):
    """ab: 'A' = radial (left, -x), 'B' = ulnar (right, +x)."""
    if finger == "thumb":
        return P['thumb_cx'] + (-P['thumb_half'] if ab == "A" else P['thumb_half'])
    return (-P['rail_cx'] if ab == "A" else P['rail_cx'])

def servo_loc(finger, ab):
    ys = _ys()
    return loc_S_on_rail(servo_xf(finger, ab), ys[finger], P['z_shaft'])


# ---------------------------------------------------------------------------
# Spool, official horn pattern (BCD 14 mm from the Waveshare 2D drawing,
# M3 clearance 3.4 mm: the horn holes are Ø2.5 / M3 tapped in the STEP).
# ---------------------------------------------------------------------------
def spool_r8(p=P):
    r, fl = p['spool_r'], p['spool_flange']
    h = cq.Workplane("XY").circle(r + fl).extrude(p['spool_base_t'])
    h = h.faces(">Z").workplane().circle(r).extrude(p['groove_w'])
    h = h.faces(">Z").workplane().circle(r + 2.0).extrude(p['mid_flange'])
    h = h.faces(">Z").workplane().circle(r).extrude(p['groove_w'])
    h = h.faces(">Z").workplane().circle(r + fl).extrude(p['spool_top_t'])
    # centre clearance over the stock M3x6 horn screw head
    h = h.faces(">Z").workplane().hole(6.5)
    h = h.faces(">Z").workplane().pushPoints(horn_holes_xy()).hole(3.4)  # M3 clearance, official 14 mm BCD
    # tendon anchor cross-holes in each groove (same as the v0 spool)
    z1 = p['spool_base_t'] + p['groove_w'] / 2
    z2 = p['spool_base_t'] + p['groove_w'] + p['mid_flange'] + p['groove_w'] / 2
    for z in (z1, z2):
        h = h.cut(cq.Workplane("YZ").workplane(offset=-20).center(r - 1.0, z).circle(0.8).extrude(40))
    return h


# ---------------------------------------------------------------------------
# One 3-servo rail (side +1 ulnar / -1 radial). Built in F, already placed in x.
# ---------------------------------------------------------------------------
def _pocket_cut(xf, y_shaft, p):
    """Pocket for the body + idler-horn clearance + M2 holes + cable cutout,
    as a solid to be subtracted from the rail blank."""
    cl = p['cl']
    # body pocket, open at the top: slightly taller than the walls so the cut is through
    x0 = xf - (BODY_W + cl) / 2
    x1 = xf + (BODY_W + cl) / 2
    y0 = y_shaft - SHAFT_FROM_OUT - cl
    y1 = y_shaft + SHAFT_FROM_CABLE + cl
    body = cq.Workplane("XY").box(x1 - x0, y1 - y0, 50, centered=False).translate((x0, y0, p['z_floor'] + 0.2))
    # idler horn through the floor (protrudes 2.25 mm into the 4 mm floor)
    horn = cq.Workplane("XY").workplane(offset=p['z_floor'] - p['floor_t'] - 1).center(xf, y_shaft).circle((HORN_OD + 1.6) / 2).extrude(p['floor_t'] + 4)
    cuts = body.union(horn)
    # 4 x M2 through the floor, aligned with the idler-ear holes.
    # In S, idler holes are at (X_s, Y_s). Map: x_f = xf - Y_s, y_f = y_shaft + X_s
    for Xs, Ys in IDL_HOLES:
        xh, yh = xf - Ys, y_shaft + Xs
        cuts = cuts.union(cq.Workplane("XY").workplane(offset=p['z_floor'] - p['floor_t'] - 1).center(xh, yh).circle(p['m2_clear'] / 2).extrude(p['floor_t'] + 6))
    # cable / screwdriver cutout at the cable end (open toward the elbow and down a bit)
    cy0 = y_shaft + SHAFT_FROM_CABLE - 6
    cable = cq.Workplane("XY").box(x1 - x0 - 4, 24, 18, centered=False).translate((x0 + 2, cy0, p['z_floor'] + 4))
    cuts = cuts.union(cable)
    return cuts


def fuse_fuzzy(shapes, tol=0.08):
    """Union a list of cq objects / shapes, with a fuzzy tolerance so coplanar faces fuse."""
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

def _socket_block(xf, y_shaft, inner_sign, p):
    """Two Ø4.2 x 8 sockets on the INNER side of the spool (not in front),
    so they do not eat the 8 mm gap between two stations. The PTFE arrives
    from the wrist; the bare tendon leaves toward the groove (~10 mm)."""
    z_g1 = p['z_shaft'] + p['spool_base_t'] + p['groove_w'] / 2
    z_g2 = p['z_shaft'] + p['spool_base_t'] + p['groove_w'] + p['mid_flange'] + p['groove_w'] / 2
    y_stop = y_shaft - 2.0
    y_back = y_stop - p['sock_depth']
    x_axis = xf + inner_sign * (BODY_W / 2 + 5.0)
    hw, hz = 5.0, 8.0
    z_mid = 0.5 * (z_g1 + z_g2)
    y_mid = 0.5 * (y_back - 1 + y_shaft + 4)
    blk = (cq.Workplane("XY").workplane(offset=z_mid - hz)
           .center(x_axis, y_mid)
           .box(2 * hw, (y_shaft + 4) - (y_back - 1), 2 * hz, centered=True))
    for z in (z_g1, z_g2):
        bore = cq.Workplane("XZ").workplane(offset=y_back).center(x_axis, z).circle(p['sock_d'] / 2).extrude(p['sock_depth'])
        hole = cq.Workplane("XZ").workplane(offset=y_back - 1).center(x_axis, z).circle(p['tendon_d'] / 2).extrude((y_stop + 10) - (y_back - 1))
        blk = blk.cut(bore).cut(hole)
    return blk, (x_axis, y_back, y_stop, z_g1, z_g2)

def _thumb_bed_end(p):
    return p['y_thumb'] + SHAFT_FROM_CABLE + 6.0

def _lap_xs(side, p):
    """x of the 2 M3 lap holes on the inner shelf of a rail (and of the yoke tab)."""
    xf = servo_xf("index", "A" if side < 0 else "B")
    inner = -side
    half = (BODY_W + p['cl']) / 2
    # two holes side by side on the inner shelf
    return xf + inner * (half + 3.0), xf + inner * (half + 7.0)

def _lap_ys(p):
    """Y of the 3 M3 lap holes: on the inner shelf, beside the front of the index servo,
    starting just after the thumb bed so the rail body does not invade the thumb bed."""
    y0 = _thumb_bed_end(p) + 1.0
    return [y0 + 8.0, y0 + 22.0, y0 + 36.0]

def rail(side, p=P):
    """side = -1 radial (A), +1 ulnar (B). Returns (solid, socket records, meta)."""
    xf = servo_xf("index", "A" if side < 0 else "B")
    inner = -side
    half = (BODY_W + p['cl']) / 2
    y_body0 = _thumb_bed_end(p) + 1.0          # main rail starts after the thumb bed
    y0 = y_body0
    y1 = p['y_end']
    x_out = xf + side * (half + p['wall'])
    x_in  = xf + inner * (half + p['wall'] + 8.0)
    x_lo, x_hi = (x_in, x_out) if x_in < x_out else (x_out, x_in)
    floor = cq.Workplane("XY").box(x_hi - x_lo, y1 - y0, p['floor_t'], centered=False).translate((x_lo, y0, p['z_floor'] - p['floor_t']))
    def wall(xa, xb):
        lo, hi = (xa, xb) if xa < xb else (xb, xa)
        return cq.Workplane("XY").box(hi - lo, y1 - y0, p['wall_top'], centered=False).translate((lo, y0, p['z_floor']))
    outer_w = wall(xf + side * half, x_out)
    inner_w = wall(xf + inner * half, xf + inner * (half + p['wall']))
    front = cq.Workplane("XY").box(x_hi - x_lo, p['wall'], p['wall_top'], centered=False).translate((x_lo, y0, p['z_floor']))
    rear  = cq.Workplane("XY").box(x_hi - x_lo, p['wall'], p['wall_top'], centered=False).translate((x_lo, y1 - p['wall'], p['z_floor']))
    rail = floor.union(outer_w).union(inner_w).union(front).union(rear)
    recs = []
    for f, ysh in zip(FINGERS_RAIL, (p['y_index'], p['y_middle'], p['y_ring'])):
        rail = rail.cut(_pocket_cut(xf, ysh, p))
        blk, rec = _socket_block(xf, ysh, inner, p)
        rail = rail.union(blk)
        recs.append(dict(finger=f, ab=("A" if side < 0 else "B"), side=side, xf=xf, y_shaft=ysh, sock=rec))
    # Inner-shelf lap tab: a 4 mm floor-only finger that extends 8 mm back under
    # the yoke tab (they stack: yoke tab at z=-8..-4, this floor at z=-4..0).
    # The 3 M3 holes are in the body of the rail, on the inner shelf, so they
    # sit beside the index servo, not under it.
    tab_y0 = y0 - 0.4   # barely laps backward; the 3 M3 sit beside the index, after the thumb bed
    tab_w = 10.0
    # tab on the inner side, 10 mm wide
    t_in = xf + inner * (half + 1.0)
    t_out = xf + inner * (half + 1.0 + tab_w)
    tlo, thi = (t_in, t_out) if t_in < t_out else (t_out, t_in)
    tab = cq.Workplane("XY").box(thi - tlo, y0 + 42.0 - tab_y0, p['floor_t'], centered=False).translate((tlo, tab_y0, p['z_floor'] - p['floor_t']))
    rail = rail.union(tab)
    lap_x = _lap_xs(side, p)
    lap_ys = _lap_ys(p)
    for y in lap_ys:
        for x in lap_x:
            hole = cq.Workplane("XY").workplane(offset=p['z_floor'] - p['floor_t'] - 1).center(x, y).circle(p['m3_d'] / 2).extrude(p['floor_t'] + 8)
            rail = rail.cut(hole)
    # brace holes in the floor, mid and rear stations (and a third near the end)
    for yb in (0.5 * (p['y_index'] + p['y_middle']), 0.5 * (p['y_middle'] + p['y_ring']), p['y_end'] - 10):
        for dx in (inner * (half + 2.0), side * (half - 2.0)):
            hole = cq.Workplane("XY").workplane(offset=p['z_floor'] - p['floor_t'] - 1).center(xf + dx, yb).circle(p['m3_d'] / 2).extrude(p['floor_t'] + 8)
            rail = rail.cut(hole)
    rail = rail.combine()
    return rail, recs, dict(y0=y0, y1=y1, x_lo=x_lo, x_hi=x_hi, lap_x=lap_x, lap_ys=lap_ys, xf=xf)


def rail_L(p=P):
    return rail(-1, p)

def rail_R(p=P):
    return rail(+1, p)


# ---------------------------------------------------------------------------
# Wrist yoke: flange to the Wrist_Interface + thumb pair + rail laps +
# tube corridors (radial, centre window, ulnar) and 4 thumb sockets.
# ---------------------------------------------------------------------------
def _thumb_sockets(p):
    """One shared 4-socket block in front of the thumb pair, slightly radial,
    tubes leaving toward the palmar-radial corridor of the flange."""
    z_g1 = p['z_shaft'] + p['spool_base_t'] + p['groove_w'] / 2
    z_g2 = p['z_shaft'] + p['spool_base_t'] + p['groove_w'] + p['mid_flange'] + p['groove_w'] / 2
    y_shaft = p['y_thumb']
    y_stop = min(y_shaft - (p['spool_r'] + 6.0), 16.5)
    y_back = y_stop - p['sock_depth']
    # four sockets in a 2 x 2 at the midline of the thumb pair, a bit radial
    x_mid = p['thumb_cx'] - 4.0
    xs = (x_mid - 5.0, x_mid + 5.0)
    zs = (z_g1, z_g2)
    hw, hl, hz = 12.0, (y_stop + 4) - (y_back - 2), 8.0
    z_mid = 0.5 * (z_g1 + z_g2)
    y_mid = 0.5 * (y_back - 2 + y_stop + 4)
    blk = (cq.Workplane("XY").workplane(offset=z_mid - hz)
           .center(x_mid, y_mid)
           .box(2 * hw, hl, 2 * hz, centered=True))
    recs = []
    for ab, x in (("A", xs[0]), ("B", xs[1])):
        for z in zs:
            bore = cq.Workplane("XZ").workplane(offset=y_back).center(x, z).circle(p['sock_d'] / 2).extrude(p['sock_depth'])
            hole = cq.Workplane("XZ").workplane(offset=y_back - 1).center(x, z).circle(p['tendon_d'] / 2).extrude((y_stop + 8) - (y_back - 1))
            blk = blk.cut(bore).cut(hole)
        recs.append(dict(finger="thumb", ab=ab, xf=servo_xf("thumb", ab), y_shaft=y_shaft,
                         sock=(x, y_back, y_stop, zs[0], zs[1])))
    return blk, recs


def yoke(p=P):
    # Flange plate in Y=0..t (toward the elbow). Only the register boss sits at
    # Y=-register_t..0, inside the Ø34 window of the Wrist_Interface.
    # Built with boxes / cylinders along Y so the sign of an XZ-workplane cannot flip it.
    x_lo, x_hi = -44.0, 44.0
    z_lo, z_hi = -40.0, 30.0
    t = p['flange_t']
    fl = cq.Workplane("XY").box(x_hi - x_lo, t, z_hi - z_lo, centered=False).translate((x_lo, 0, z_lo))
    def cyl_y(x, z, y0, h, d):
        return cq.Workplane("XZ").workplane(offset=y0).center(x, z).circle(d / 2).extrude(h)
    # Holes through the flange (M2 clearance). We go slightly past both faces.
    for a in WI_HOLE_ANG:
        rad = math.radians(a)
        xh = WI_HOLE_R * math.cos(rad)
        zh = WI_HOLE_R * math.sin(rad)
        # If XZ normal is -Y, extrude(h) from offset=y0 goes toward -Y; use a solid cylinder along +Y via box-cut of a 3D cylinder.
        fl = fl.cut(cq.Solid.makeCylinder(p['m2_clear'] / 2, t + 2, cq.Vector(xh, -1, zh), cq.Vector(0, 1, 0)))
    reg = cq.Workplane("XY").add(cq.Solid.makeCylinder(p['register_d'] / 2, p['register_t'], cq.Vector(0, -p['register_t'], 0), cq.Vector(0, 1, 0)))
    win = cq.Workplane("XY").add(cq.Solid.makeCylinder((WI_WINDOW_D - 3.0) / 2, t + p['register_t'] + 2, cq.Vector(0, -p['register_t'] - 1, 0), cq.Vector(0, 1, 0)))
    fl = fl.union(reg).cut(win)
    def corridor_cut(x_mid, z_mid, w, h):
        return cq.Workplane("XY").box(w, t + 2, h, centered=True).translate((x_mid, t / 2, z_mid))
    fl = fl.cut(corridor_cut(WI_XF[0] - p['lane_w'] / 2 - 0.5, 0.0, p['lane_w'], 16.0))
    fl = fl.cut(corridor_cut(WI_XF[1] + p['lane_w'] / 2 + 0.5, 0.0, p['lane_w'], 16.0))
    fl = fl.cut(corridor_cut(-20.0, WI_ZF[0] - p['lane_w'] / 2 - 0.5, 28.0, p['lane_w']))

    # Thumb pair bed, overlaps the flange by 0.5 mm in Y
    y0 = t - 0.5
    y1 = _thumb_bed_end(p)
    x_a = servo_xf("thumb", "A")
    x_b = servo_xf("thumb", "B")
    half = (BODY_W + p['cl']) / 2
    x_lo_t = x_a - half - p['wall']
    x_hi_t = x_b + half + p['wall']
    floor = cq.Workplane("XY").box(x_hi_t - x_lo_t, y1 - y0, p['floor_t'], centered=False).translate((x_lo_t, y0, p['z_floor'] - p['floor_t']))
    def twall(xa, xb):
        lo, hi = (xa, xb) if xa < xb else (xb, xa)
        return cq.Workplane("XY").box(hi - lo, y1 - y0, p['wall_top'], centered=False).translate((lo, y0, p['z_floor']))
    walls = twall(x_lo_t, x_a - half).union(twall(x_b + half, x_hi_t))
    endw = cq.Workplane("XY").box(x_hi_t - x_lo_t, p['wall'], p['wall_top'], centered=False).translate((x_lo_t, y1 - p['wall'], p['z_floor']))
    bed = floor.union(walls).union(endw)
    for ab, xf in (("A", x_a), ("B", x_b)):
        bed = bed.cut(_pocket_cut(xf, p['y_thumb'], p))
    sock_blk, recs = _thumb_sockets(p)
    # pillar from the floor up to the floating socket block, in front / between the two servos
    pillar = (cq.Workplane("XY").box(24.0, 12.0, 42.0, centered=False)
              .translate((p['thumb_cx'] - 4.0 - 12.0, 7.0, p['z_floor'])))
    bed = bed.union(pillar).union(sock_blk)
    # explicit flange-bed key, 4 mm in Y, overlaps both
    key = (cq.Workplane("XY").box(x_hi_t - x_lo_t, 4.0, p['floor_t'] + 6.0, centered=False)
           .translate((x_lo_t, 3.0, p['z_floor'] - p['floor_t'])))
    bed = bed.union(key)

    # Inner-shelf yoke tabs under the rail floors (z = -8 .. -4), long enough
    # to take the 3 M3 holes beside the index servo.
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
        shelf = cq.Workplane("XY").box(thi - tlo, y_tab1 - y_tab0, p['floor_t'] - 0.2, centered=False).translate((tlo, y_tab0, p['z_floor'] - 2 * p['floor_t']))
        # a short vertical rib to fuse the shelf to the thumb-bed floor (z=-4)
        rib = cq.Workplane("XY").box(thi - tlo, 6.0, p['floor_t'] + 1.0, centered=False).translate((tlo, y1 - 7.0, p['z_floor'] - 2 * p['floor_t']))
        shelf = shelf.union(rib)
        for y in _lap_ys(p):
            for x in _lap_xs(side, p):
                shelf = shelf.cut(cq.Workplane("XY").workplane(offset=p['z_floor'] - 2 * p['floor_t'] - 1).center(x, y).circle(p['m3_d'] / 2).extrude(2 * p['floor_t'] + 4))
        tabs.append(shelf)
    yk = fuse_fuzzy([fl, bed, tabs[0], tabs[1]])
    return yk, recs


def brace(p=P):
    """Cross-brace that bolts under the two rail floors (M3 x 4). One length for all stations."""
    # spans from left inner to right inner, 12 mm wide, 4 mm thick, with 4 holes
    # Hole x positions: we punch a slot-ish pattern so one brace fits mid and rear.
    # Exact hole x: for each rail, xf ± (half - 2) and xf + inner*(half+2)
    # That's 4 holes per station; we put 4 holes at the nominal mid-station x,
    # which is the same at every y because the rails are straight.
    half = (BODY_W + p['cl']) / 2
    xs = []
    for side in (-1, 1):
        xf = servo_xf("index", "A" if side < 0 else "B")
        inner = -side
        xs += [xf + inner * (half + 2.0), xf + side * (half - 2.0)]
    xs = sorted(xs)
    pad = 6.0
    xlo, xhi = xs[0] - pad, xs[-1] + pad
    w, t, L = 14.0, 4.0, xhi - xlo
    b = cq.Workplane("XY").box(L, w, t, centered=False).translate((xlo, -w / 2, 0))
    for x in xs:
        b = b.cut(cq.Workplane("XY").workplane(offset=-1).center(x, 0).circle(p['m3_d'] / 2).extrude(t + 2))
    return b


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
