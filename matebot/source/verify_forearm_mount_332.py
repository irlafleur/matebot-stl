# Verification of the v10 3-3-2 open-rack forearm chassis (alternating
# top/bottom pairs: TL, TR, BL, BR, repeat) and the official-BCD spool_r8.
# Usage: python verify_forearm_mount_332.py
# Optional: Amazing Hand STEP folder as argv[1] (for the Wrist_Interface check).
import os, sys, math
import cadquery as cq
from sts3215 import (
    BODY_L, BODY_W, BODY_H_FLANGE, H_TO_HORN, H_BOTH_HORNS, SHAFT_FROM_OUT,
    SHAFT_FROM_CABLE, HORN_OD, HORN_BCD, HORN_HOLE_D, HORN_T, IDL_HOLES,
    MOUNT_HOLE_D, envelope, horn_holes_xy,
)
import forearm_mount_332 as F

HERE = os.path.dirname(os.path.abspath(__file__))
AHD = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MATEBOT_AH_STEP_DIR", "/workspace/ah-enh/cad/step")
res = []
def chk(name, ok, detail):
    res.append(bool(ok))
    print(("PASS" if ok else "FAIL"), "-", name, ":", detail)

def ivol(a, b):
    try:
        r = a.intersect(b)
        vs = r.solids().vals() if r.vals() else []
        return sum(s.Volume() for s in vs) if vs else 0.0
    except Exception as e:
        return float("nan")

parts = F.build_all()
p = F.P
names = ("rail_L", "rail_R", "yoke", "brace", "spool_r8")

# 1. each printed part is a single valid solid, fits a 250 mm bed
for n in names:
    w = parts[n]
    sols = w.solids().vals()
    bb = w.val().BoundingBox()
    mx = max(bb.xlen, bb.ylen, bb.zlen)
    chk(f"{n}: one valid solid, max dim <= 250 mm",
        len(sols) == 1 and all(s.isValid() for s in sols) and mx <= 250,
        f"solids={len(sols)} max={mx:.1f}  {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm  vol={w.val().Volume():.0f} mm3")

# 2. walls / floor thick enough for PETG
chk("rack plate 4 mm, locating ribs 3.5 mm, flange 6 mm",
    p['floor_t'] >= 3.5 and p['wall'] >= 3.0 and p['flange_t'] >= 5.0,
    f"floor {p['floor_t']}, wall {p['wall']}, flange {p['flange_t']}, rib_h {p['rib_h']}")

# 3. official servo numbers used
chk("STS3215 body 45.22 x 24.72, height to horn 35, both horns 37.25, shaft 10.11 from output end",
    abs(BODY_L - 45.22) < 1e-6 and abs(BODY_W - 24.72) < 1e-6 and abs(H_TO_HORN - 35.0) < 1e-6
    and abs(H_BOTH_HORNS - 37.25) < 1e-6 and abs(SHAFT_FROM_OUT - 10.11) < 1e-6,
    f"{BODY_L} x {BODY_W}, H_TO_HORN {H_TO_HORN}, H_BOTH {H_BOTH_HORNS}, shaft {SHAFT_FROM_OUT}")

# 4. spool: 14 mm BCD, M3 clearance, centre hole, two grooves at r=8
sp = parts['spool_r8']
bb = sp.val().BoundingBox()
holes_ok = True
details = []
for x, y in horn_holes_xy():
    inside = sp.val().isInside(cq.Vector(x, y, 6.0), 0.2)
    details.append((round(x, 2), round(y, 2), inside))
    if inside:
        holes_ok = False
radii = [math.hypot(x, y) for x, y in horn_holes_xy()]
chk("spool_r8: official 14 mm horn BCD, M3 (Ø3.4) holes open, flanges Ø22, height 11.5, r=8 grooves",
    holes_ok and all(abs(r - 7.0) < 1e-9 for r in radii) and abs(bb.zlen - 11.5) < 0.05 and abs(bb.xlen - 22.0) < 0.05,
    f"hole-inside? {details}, bbox {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")

# 5. M2 holes in the mid-plane plate line up with the idler-ear pattern on BOTH faces
m2_ok = True
m2_det = []
for finger, ab, railn in (("index", "A", "rail_L"), ("index", "B", "rail_R"),
                          ("middle", "A", "rail_L"), ("ring", "A", "rail_L"),
                          ("thumb", "A", "yoke")):
    xf = F.servo_xf(finger, ab)
    ysh = F._ys()[finger]
    face = F.servo_face(finger)
    w = parts[railn]
    for Xs, Ys in IDL_HOLES:
        xh, yh = F.m2_xy(xf, ysh, Xs, Ys, face)
        inside = w.val().isInside(cq.Vector(xh, yh, p['z_mid']), 0.15)
        m2_det.append((finger, ab, face, round(xh, 2), round(yh, 2), inside))
        if inside:
            m2_ok = False
chk("M2 holes in the mid-plane line up with the official idler-ear pattern on both faces (24.45 x 20.50 mm, Ø1.6 in the case)",
    m2_ok, f"a point at each hole centre mid-plate is inside the part? (want False) {m2_det}")

# 6. no collision between frame parts as assembled in F
chk("assembled rails do not overlap each other or the yoke (half-lap air at the joint)",
    ivol(parts['rail_L'], parts['rail_R']) < 0.01
    and ivol(parts['rail_L'], parts['yoke']) < 0.01
    and ivol(parts['rail_R'], parts['yoke']) < 0.01,
    f"L/R {ivol(parts['rail_L'], parts['rail_R']):.3f}, L/yoke {ivol(parts['rail_L'], parts['yoke']):.3f}, R/yoke {ivol(parts['rail_R'], parts['yoke']):.3f} mm3")

# 7. official servo envelope (body + horns, no invented cable) clears the frame, BOTH faces
worst = {}
for finger in ("thumb", "index", "middle", "ring"):
    for ab in ("A", "B"):
        railn = "yoke" if finger == "thumb" else ("rail_L" if ab == "A" else "rail_R")
        env = F.place_S(envelope(cl=0.0, with_horns=True, with_cables=False),
                        F.servo_xf(finger, ab), F._ys()[finger], F.z_shaft_of(finger),
                        F.servo_face(finger))
        v = ivol(parts[railn], env)
        worst[f"{finger}_{ab}_{F.servo_face(finger)}"] = round(v, 3)
chk("servo body + both official horns (cl=0) do not overlap the frame for all 8 stations (top and bottom)",
    all(v < 0.05 for v in worst.values()), f"overlap mm3: {worst}")

# 8. spool sits on the horn outer face and does not overlap the body, both faces
sp_iv = {}
for finger, ab in (("index", "A"), ("thumb", "B"), ("middle", "A"), ("ring", "A")):
    xf, ysh = F.servo_xf(finger, ab), F._ys()[finger]
    face = F.servo_face(finger)
    sp_f = F.place_S(parts['spool_r8'], xf, ysh, F.z_shaft_of(finger), face)
    env = F.place_S(envelope(cl=0.0, with_horns=True, with_cables=False), xf, ysh, F.z_shaft_of(finger), face)
    sp_iv[f"{finger}_{ab}_{face}"] = round(ivol(sp_f, env), 3)
chk("spool on the horn outer face does not overlap the official servo envelope on either face (contact only)",
    all(v < 0.05 for v in sp_iv.values()), f"{sp_iv}")

# 9. pair integrity, 3-3-2, and TL/TR/BL/BR alternating faces
ys = F._ys()
faces = {f: F.servo_face(f) for f in ("thumb", "index", "middle", "ring")}
chk("3-3-2 + TL,TR,BL,BR: thumb pair TOP at the wrist, then index BOTTOM, middle TOP, ring BOTTOM (A radial, B ulnar)",
    ys['thumb'] < ys['index'] < ys['middle'] < ys['ring']
    and faces == dict(thumb="top", index="bottom", middle="top", ring="bottom")
    and F.servo_xf("index", "A") < 0 < F.servo_xf("index", "B")
    and abs(F.servo_xf("index", "A") + F.servo_xf("index", "B")) < 0.01
    and F.servo_xf("thumb", "A") < F.servo_xf("thumb", "B"),
    f"shaft y {ys}, faces {faces}, x A/B index {F.servo_xf('index','A'):.2f}/{F.servo_xf('index','B'):.2f}, thumb {F.servo_xf('thumb','A'):.2f}/{F.servo_xf('thumb','B'):.2f}")

# 10. 16 sockets, 8 on top and 8 on the bottom, Ø4.2 x 8, facing the wrist
socks = parts['recs']
n_top = sum(1 for r in socks if r['face'] == "top")
n_bot = sum(1 for r in socks if r['face'] == "bottom")
# each record is one servo with 2 groove zs, so 4 top servos + 4 bottom servos
chk("16 PTFE sockets (2 per servo): 8 on the top face (thumb+middle) and 8 on the bottom (index+ring)",
    len(socks) == 8 and n_top == 4 and n_bot == 4
    and all(abs(r['sock'][2] - r['sock'][1] - p['sock_depth']) < 1e-6 for r in socks)
    and all(r['sock'][3] > 0 and r['sock'][4] > 0 for r in socks if r['face'] == "top")
    and all(r['sock'][3] < 0 and r['sock'][4] < 0 for r in socks if r['face'] == "bottom"),
    f"{len(socks)} records, top servos {n_top}, bottom servos {n_bot}, zs {[(r['finger'], r['ab'], r['face'], round(r['sock'][3],1), round(r['sock'][4],1)) for r in socks]}")

# 11. tube paths on BOTH faces: min bend 30 mm, no 3D crossings between fingers
PLATE = {
    ("index",  "+X", "ext"):  (10.50, -30.00,  2.30),
    ("index",  "+X", "flex"): (10.50, -30.00,-12.80),
    ("index",  "-X", "ext"):  (-10.50,-30.00,  2.30),
    ("index",  "-X", "flex"): (-10.50,-30.00,-12.80),
    ("middle", "+X", "ext"):  (40.24, -36.90,  2.30),
    ("middle", "+X", "flex"): (40.24, -36.90,-12.80),
    ("middle", "-X", "ext"):  (19.34, -34.79,  2.30),
    ("middle", "-X", "flex"): (19.34, -34.79,-12.80),
    ("ring",   "+X", "ext"):  (68.23, -48.72,  2.30),
    ("ring",   "+X", "flex"): (68.23, -48.72,-12.80),
    ("ring",   "-X", "ext"):  (47.81, -43.83,  2.30),
    ("ring",   "-X", "flex"): (47.81, -43.83,-12.80),
}

def lane_x(finger, ab):
    if finger == "thumb":
        return -20.0
    if finger == "index":
        return F.WI_XF[0] - p['lane_w'] / 2 - 0.5
    if finger == "ring":
        return F.WI_XF[1] + p['lane_w'] / 2 + 0.5
    return 0.0

def lane_z(finger):
    """Lane height: top-face fingers stay dorsal, bottom-face fingers stay palmar,
    until the wrist corridors / plate."""
    if finger == "thumb":
        return F.WI_ZF[0] - p['lane_w'] / 2 - 0.5
    if F.servo_face(finger) == "top":
        return 12.0
    return -16.0

def path_for(rec, which_z):
    """Each finger's 4 tubes gather into that finger's lane at this station
    and on this face, then run to the wrist in that lane. 90 deg turns get
    40 mm legs so a 30 mm fillet fits; a short jog is a single diagonal."""
    x, yb, ys, zg1, zg2 = rec['sock']
    z = zg1 if which_z == 0 else zg2
    finger, ab = rec['finger'], rec['ab']
    face = rec['face']
    lx = lane_x(finger, ab)
    zc = lane_z(finger)
    if finger == "thumb":
        # dorsal sockets: go radial 40 mm, drop to the palmar corridor, then forward
        x_out = x - 40.0
        return [(x, yb, z), (x_out, yb, z), (x_out, yb, zc), (x_out, -25.0, zc), (lx, -25.0, zc)]
    y_run = yb - 40.0
    if abs(lx - x) >= 40.0:
        pts = [(x, yb, z), (x, y_run, z), (lx, y_run, zc)]
    else:
        pts = [(x, yb, z), (lx, y_run, zc)]
    key_side = "-X" if ab == "A" else "+X"
    key_kind = "ext" if which_z == 0 else "flex"
    hx, hy, hz = PLATE[(finger, key_side, key_kind)]
    xf, yf, zf = F.hand_to_f(hx, hy, hz)
    y_pre = yf + 40.0
    pts += [(lx, y_pre, zc), (xf, yf, zf)]
    return pts

def min_radius(pts):
    rmin = 1e9
    for i in range(1, len(pts) - 1):
        ax, ay, az = [pts[i][k] - pts[i-1][k] for k in range(3)]
        bx, by, bz = [pts[i+1][k] - pts[i][k] for k in range(3)]
        la = math.sqrt(ax*ax+ay*ay+az*az); lb = math.sqrt(bx*bx+by*by+bz*bz)
        if la < 1e-6 or lb < 1e-6:
            continue
        dot = max(-1.0, min(1.0, (ax*bx+ay*by+az*bz) / (la*lb)))
        ang = math.acos(dot)
        if ang < math.radians(2):
            continue
        need = 30.0 * math.tan(ang / 2.0)
        if min(la, lb) + 1e-6 >= need:
            r = 30.0
        else:
            r = min(la, lb) / math.tan(ang / 2.0)
        rmin = min(rmin, r)
    return rmin

def seg_dist(a1, a2, b1, b2):
    # closest approach of two 3D segments
    ax, ay, az = [a2[k]-a1[k] for k in range(3)]
    bx, by, bz = [b2[k]-b1[k] for k in range(3)]
    rx, ry, rz = [a1[k]-b1[k] for k in range(3)]
    aa = ax*ax+ay*ay+az*az; bb = bx*bx+by*by+bz*bz; ab = ax*bx+ay*by+az*bz
    ar = ax*rx+ay*ry+az*rz; br = bx*rx+by*ry+bz*rz
    den = aa*bb - ab*ab
    if den < 1e-12:
        s = 0.0
        t = min(1.0, max(0.0, br / bb if bb > 1e-12 else 0.0))
    else:
        s = min(1.0, max(0.0, (ab*br - bb*ar) / den))
        t = min(1.0, max(0.0, (aa*br - ab*ar) / den))
    dx = a1[0]+s*ax - (b1[0]+t*bx)
    dy = a1[1]+s*ay - (b1[1]+t*by)
    dz = a1[2]+s*az - (b1[2]+t*bz)
    return math.sqrt(dx*dx+dy*dy+dz*dz)

paths = {}
rmins = {}
for rec in socks:
    for k in (0, 1):
        key = (rec['finger'], rec['ab'], k)
        pts = path_for(rec, k)
        paths[key] = pts
        rmins[key] = min_radius(pts)

chk("tube paths on both faces have r >= 30 mm (30 mm fillet fits every corner)",
    all(r >= p['r_min'] - 0.05 for r in rmins.values()),
    f"min r per path { {str(k): round(v,1) for k,v in rmins.items()} }")

# closest distance between tubes of different fingers (3D)
min_d, min_pair = 1e9, None
keys = list(paths)
for i, a in enumerate(keys):
    for b in keys[i+1:]:
        if a[0] == b[0]:
            continue
        pa, pb = paths[a], paths[b]
        for i1 in range(len(pa)-1):
            for i2 in range(len(pb)-1):
                d = seg_dist(pa[i1], pa[i1+1], pb[i2], pb[i2+1])
                if d < min_d:
                    min_d, min_pair = d, (a, b, d)
chk("no 3D crossings between different fingers (closest tubes >= 8 mm, both faces)",
    min_d >= 8.0,
    f"closest {min_d:.1f} mm between {min_pair}")

# 12. yoke vs Wrist_Interface
wi_path = os.path.join(AHD, "R-Wrist_Interface.step")
if not os.path.isfile(wi_path):
    wi_path = os.path.join(AHD, "Amazing Hand Parts - R-Wrist_Interface.step")
if os.path.isfile(wi_path):
    wi = cq.importers.importStep(wi_path)
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf, gp_Vec
    T = gp_Trsf()
    # F -> hand: xh=xf+WI_CX, yh=WI_CY-yf, zh=zf-11.50
    T.SetValues(1,0,0,F.WI_CX,  0,-1,0,F.WI_CY,  0,0,1,-11.50)
    yk_h = cq.Workplane("XY").add(cq.Shape.cast(BRepBuilderAPI_Transform(parts['yoke'].val().wrapped, T, True).Shape()))
    v_wi = ivol(yk_h, wi)
    chk("yoke (in the hand frame) does not overlap R-Wrist_Interface (register sits in the Ø34 window, 6 x M2 line up with the D2.4 circle of radius 21 mm)",
        v_wi < 0.05, f"overlap {v_wi:.3f} mm3")
else:
    chk("yoke vs R-Wrist_Interface (STEP not found, skipped)", False, wi_path)

# 13. 4 thumb sockets live on the yoke, on the TOP face
thumb_recs = [r for r in socks if r['finger'] == "thumb"]
chk("four thumb sockets are on the yoke, on the TOP (dorsal) face (two records A/B, each with 2 groove zs)",
    len(thumb_recs) == 2 and all(r['face'] == "top" for r in thumb_recs),
    f"{[(r['ab'], r['face'], r['sock']) for r in thumb_recs]}")

# 14-15. screw engagement, both faces: plate 4 mm + ear 2.80, M2x6; spool M3x6
chk("M2x6 through the 4 mm mid-plane engages 2.0 mm in the 2.80 mm idler ear on BOTH faces and does not come out into the case (Waveshare: a screw that bottoms on the housing can burn the servo)",
    (6.0 - p['floor_t']) <= 2.80 - 0.4 and (6.0 - p['floor_t']) >= 1.5,
    f"engagement {6.0 - p['floor_t']:.2f} mm in {2.80} mm ear; heads sit on the opposite (clear) face")
chk("M3x6 through the 2 mm spool pad engages 4.0 mm in the 4.5 mm horn and stays 0.5 mm short of the inner face, on both faces",
    (6.0 - 2.0) <= 4.5 - 0.4,
    f"engagement {6.0-2.0:.1f} mm in 4.5 mm horn")

# 16. opposite face at each station is open (no frame in the opposite spool/body volume)
opp = {}
for finger in ("thumb", "index", "middle", "ring"):
    for ab in ("A", "B"):
        # a phantom servo on the OPPOSITE face at the same XY should not hit the frame
        # (except the mid-plane plate, which we subtract by only testing the body+spool outward of the other face)
        other = "bottom" if F.servo_face(finger) == "top" else "top"
        z_other = p['z_shaft_bot'] if other == "bottom" else p['z_shaft_top']
        railn = "yoke" if finger == "thumb" else ("rail_L" if ab == "A" else "rail_R")
        env = F.place_S(envelope(cl=0.0, with_horns=True, with_cables=False),
                        F.servo_xf(finger, ab), F._ys()[finger], z_other, other)
        # The mid-plane plate will overlap the phantom idler horn / ears. Cut the
        # test to the outward body: use the envelope and accept plate overlap at
        # the ears only if volume is just the horn-in-plate. Better: check a
        # box on the opposite side starting 1 mm off the plate, the size of body+spool.
        xf, ysh = F.servo_xf(finger, ab), F._ys()[finger]
        sign = 1 if other == "top" else -1
        z_face = p['z_top_face'] if other == "top" else p['z_bot_face']
        # clearance volume: body + horn + spool, starting 1 mm off the plate
        z0 = z_face + sign * 1.0
        z1 = z_other + sign * (p['spool_h'] + 1.0)
        zlo, zhi = (z0, z1) if z0 < z1 else (z1, z0)
        box = (cq.Workplane("XY").box(BODY_W + 8, BODY_L + 8, zhi - zlo, centered=True)
               .translate((xf, ysh, 0.5 * (zlo + zhi))))
        # but the body is offset along Y (shaft not at mid-body). Use the actual envelope minus a slab of the plate.
        plate_slab = (cq.Workplane("XY").box(200, 400, p['floor_t'] + 2, centered=True)
                      .translate((0, 100, 0)))
        try:
            env_out = env.cut(plate_slab)
            v = ivol(parts[railn], env_out)
        except Exception:
            v = ivol(parts[railn], env)
        opp[f"{finger}_{ab}"] = round(v, 3)
chk("opposite face at each station is open: a phantom body+horn+spool on the other side (outside the 4 mm plate) does not hit the rack",
    all(v < 1.0 for v in opp.values()),
    f"overlap mm3 (want ~0, plate/horn contact excluded): {opp}")

print()
n_ok = sum(res)
print(f"{n_ok}/{len(res)} checks passed.")
sys.exit(0 if n_ok == len(res) else 1)
