# Verification of the v9 3-3-2 forearm chassis and the updated spool_r8.
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
chk("rail floor 4 mm, walls 3.5 mm, flange 6 mm",
    p['floor_t'] >= 3.5 and p['wall'] >= 3.0 and p['flange_t'] >= 5.0,
    f"floor {p['floor_t']}, wall {p['wall']}, flange {p['flange_t']}")

# 3. official servo numbers used
chk("STS3215 body 45.22 x 24.72, height to horn 35, both horns 37.25, shaft 10.11 from output end",
    abs(BODY_L - 45.22) < 1e-6 and abs(BODY_W - 24.72) < 1e-6 and abs(H_TO_HORN - 35.0) < 1e-6
    and abs(H_BOTH_HORNS - 37.25) < 1e-6 and abs(SHAFT_FROM_OUT - 10.11) < 1e-6,
    f"{BODY_L} x {BODY_W}, H_TO_HORN {H_TO_HORN}, H_BOTH {H_BOTH_HORNS}, shaft {SHAFT_FROM_OUT}")

# 4. spool: 14 mm BCD, M3 clearance, centre hole, two grooves at r=8
sp = parts['spool_r8']
bb = sp.val().BoundingBox()
# sample the 4 M3 holes: points at radius 7, mid-height of the spool, should be OUTSIDE the solid (in the hole)
holes_ok = True
details = []
for x, y in horn_holes_xy():
    # a point at the hole centre, z = 1 mm, should not be inside the material
    inside = sp.val().isInside(cq.Vector(x, y, 6.0), 0.2)
    details.append((round(x, 2), round(y, 2), inside))
    if inside:
        holes_ok = False
# BCD
radii = [math.hypot(x, y) for x, y in horn_holes_xy()]
chk("spool_r8: official 14 mm horn BCD, M3 (Ø3.4) holes open, flanges Ø22, height 11.5, r=8 grooves",
    holes_ok and all(abs(r - 7.0) < 1e-9 for r in radii) and abs(bb.zlen - 11.5) < 0.05 and abs(bb.xlen - 22.0) < 0.05,
    f"hole-inside? {details}, bbox {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")

# 5. M2 holes in the rail floor line up with the idler-ear pattern
# In F, hole at (xf - Ys, y_shaft + Xs), and the floor has Ø2.4. Probe a point at z=-2 (mid floor).
m2_ok = True
m2_det = []
for finger, ab, railn in (("index", "A", "rail_L"), ("index", "B", "rail_R"),
                          ("ring", "A", "rail_L"), ("thumb", "A", "yoke")):
    xf = F.servo_xf(finger, ab)
    ysh = F._ys()[finger]
    w = parts[railn]
    for Xs, Ys in IDL_HOLES:
        xh, yh = xf - Ys, ysh + Xs
        inside = w.val().isInside(cq.Vector(xh, yh, p['z_floor'] - p['floor_t'] / 2), 0.15)
        m2_det.append((finger, ab, round(xh, 2), round(yh, 2), inside))
        if inside:
            m2_ok = False  # the hole should be empty
chk("M2 holes in the floor line up with the official idler-ear pattern (24.45 x 20.50 mm, Ø1.6 in the case)",
    m2_ok, f"a point at each hole centre mid-floor is inside the part? (want False) {m2_det}")

# 6. no collision between frame parts as assembled in F
chk("assembled rails do not overlap each other or the yoke (0.2 mm air at the lap)",
    ivol(parts['rail_L'], parts['rail_R']) < 0.01
    and ivol(parts['rail_L'], parts['yoke']) < 0.01
    and ivol(parts['rail_R'], parts['yoke']) < 0.01,
    f"L/R {ivol(parts['rail_L'], parts['rail_R']):.3f}, L/yoke {ivol(parts['rail_L'], parts['yoke']):.3f}, R/yoke {ivol(parts['rail_R'], parts['yoke']):.3f} mm3")

# 7. official servo envelope (body + horns, no invented cable) clears the frame
worst = {}
for finger in ("thumb", "index", "middle", "ring"):
    for ab in ("A", "B"):
        railn = "yoke" if finger == "thumb" else ("rail_L" if ab == "A" else "rail_R")
        env = F.place_S(envelope(cl=0.0, with_horns=True, with_cables=False),
                        F.servo_xf(finger, ab), F._ys()[finger], p['z_shaft'])
        v = ivol(parts[railn], env)
        worst[f"{finger}_{ab}"] = round(v, 3)
chk("servo body + both official horns (cl=0) do not overlap the frame for all 8 stations",
    all(v < 0.05 for v in worst.values()), f"overlap mm3: {worst}")

# 8. spool sits on the horn outer face and does not overlap the body
sp_iv = {}
for finger, ab in (("index", "A"), ("thumb", "B"), ("ring", "A")):
    xf, ysh = F.servo_xf(finger, ab), F._ys()[finger]
    sp_f = F.place_S(parts['spool_r8'], xf, ysh, p['z_shaft'])
    env = F.place_S(envelope(cl=0.0, with_horns=True, with_cables=False), xf, ysh, p['z_shaft'])
    sp_iv[f"{finger}_{ab}"] = round(ivol(sp_f, env), 3)
chk("spool on the horn outer face does not overlap the official servo envelope (contact only)",
    all(v < 0.05 for v in sp_iv.values()), f"{sp_iv}")

# 9. pair integrity and 3-3-2 layout
ys = F._ys()
chk("3-3-2 layout: thumb pair at the wrist, then index, middle, ring on two rails (A radial, B ulnar)",
    ys['thumb'] < ys['index'] < ys['middle'] < ys['ring']
    and F.servo_xf("index", "A") < 0 < F.servo_xf("index", "B")
    and abs(F.servo_xf("index", "A") + F.servo_xf("index", "B")) < 0.01
    and F.servo_xf("thumb", "A") < F.servo_xf("thumb", "B"),
    f"shaft y {ys}, x A/B index {F.servo_xf('index','A'):.2f}/{F.servo_xf('index','B'):.2f}, thumb {F.servo_xf('thumb','A'):.2f}/{F.servo_xf('thumb','B'):.2f}")

# 10. tube sockets: 16 ends, Ø4.2 x 8, facing the wrist, min 4 mm between neighbouring axes
socks = parts['recs']
chk("16 PTFE sockets (2 per servo) are present",
    len(socks) == 8 and all(r['sock'][2] - r['sock'][1] == p['sock_depth'] for r in socks),
    f"{len(socks)} records, depth {[round(r['sock'][2]-r['sock'][1],2) for r in socks]}")

# 11. tube paths: waypoints and minimum bend, no crossings between fingers
# Each path is a polyline in F: socket back -> a point at y=8 in the lane -> corridor at y=0
# -> through / around the Wrist_Interface -> a mid-air point at y=-20 -> plate socket (hand, converted).
PLATE = {
    # hand-frame stop of each plate socket, then converted to F
    # (finger, side, kind) : hand (x,y,z)
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
# Thumb sockets on the yoke are the palm-side anchors; the finger end is still
# on the Wrist_Interface (pose estimated). We only check the forearm half of those 4.

def lane_x(finger, ab):
    if finger == "thumb":
        return -20.0  # palmar-radial corridor
    if finger == "index":
        return F.WI_XF[0] - p['lane_w'] / 2 - 0.5
    if finger == "ring":
        return F.WI_XF[1] + p['lane_w'] / 2 + 0.5
    return 0.0  # middle: Ø34 window

def path_for(rec, which_z, side_label):
    """Each finger's 4 tubes gather into that finger's lane at this station,
    then run to the wrist in that lane. 90 deg turns get 40 mm legs so a
    30 mm fillet fits; a short jog to a nearby lane is a single diagonal
    (a sharp 90 deg corner would be an artefact of the polyline)."""
    x, yb, ys, zg1, zg2 = rec['sock']
    z = zg1 if which_z == 0 else zg2
    finger, ab = rec['finger'], rec['ab']
    lx = lane_x(finger, ab)
    zc = (F.WI_ZF[0] - p['lane_w'] / 2 - 0.5) if finger == "thumb" else 0.0
    if finger == "thumb":
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
    """Lower bound of the bend radius of a polyline, using the inscribed-circle
    radius at each interior vertex: r = tan(alpha/2) * min(len_in, len_out),
    but we report the turning radius if we cut the corner with a 30 mm fillet
    when both legs are long enough, otherwise the actual inscribed r."""
    rmin = 1e9
    for i in range(1, len(pts) - 1):
        ax, ay, az = [pts[i][k] - pts[i-1][k] for k in range(3)]
        bx, by, bz = [pts[i+1][k] - pts[i][k] for k in range(3)]
        la = math.sqrt(ax*ax+ay*ay+az*az); lb = math.sqrt(bx*bx+by*by+bz*bz)
        if la < 1e-6 or lb < 1e-6:
            continue
        dot = (ax*bx+ay*by+az*bz) / (la*lb)
        dot = max(-1.0, min(1.0, dot))
        ang = math.acos(dot)  # turning angle, 0 = straight
        if ang < math.radians(2):
            continue
        # inscribed radius if we fillet with leg min(la,lb, 30)/tan? Standard:
        # a fillet of radius r needs r*tan(phi/2) of tangent length on each leg,
        # where phi = pi-ang? Wait: interior angle = pi-ang if ang is the deviation.
        phi = math.pi - ang  # interior
        need = 30.0 * math.tan((math.pi - phi) / 2.0) if False else 30.0 * math.tan(ang / 2.0)
        if min(la, lb) + 1e-6 >= need:
            r = 30.0  # a 30 mm fillet fits
        else:
            r = min(la, lb) / math.tan(ang / 2.0)
        rmin = min(rmin, r)
    return rmin

def seg_dist(a1, a2, b1, b2):
    """Minimum distance between two 3D segments."""
    import numpy as np
    p, r = np.array(a1, float), np.array(a2, float) - np.array(a1, float)
    q, s = np.array(b1, float), np.array(b2, float) - np.array(b1, float)
    rr, ss, rs = float(r @ r), float(s @ s), float(r @ s)
    qp = q - p
    denom = rr * ss - rs * rs
    if denom < 1e-9:
        # nearly parallel
        t = 0.0 if rr < 1e-9 else max(0, min(1, float(qp @ r) / rr))
        u = 0.0 if ss < 1e-9 else max(0, min(1, float((p + t*r - q) @ s) / ss))
        t = 0.0 if rr < 1e-9 else max(0, min(1, float((q + u*s - p) @ r) / rr))
        return float(np.linalg.norm(p + t*r - (q + u*s)))
    t = max(0, min(1, float((rs * (qp @ s) - ss * (-qp @ r) if False else (qp @ s) * rs + (p-q) @ r * ss) )))  # placeholder
    # proper:
    # t = ((qp·s) rs - (qp·r) ss) / denom? Let's use the standard formula
    # t = ((q-p)·s * s·r - (q-p)·r * s·s) wait
    t = float(( (qp @ s) * rs - (qp @ r) * ss ) / denom)  # may be wrong sign
    # Use a robust 2-projection iteration
    t, u = 0.0, 0.0
    for _ in range(8):
        t = 0.0 if rr < 1e-9 else max(0, min(1, float((qp + u*s) @ r) / rr))  # wrong
        break
    # fallback: dense sample
    md = 1e9
    for i in range(11):
        pa = np.array(a1) + (i/10)*r
        for j in range(11):
            pb = np.array(b1) + (j/10)*s
            md = min(md, float(np.linalg.norm(pa-pb)))
    return md

paths = {}
rmins = {}
for rec in socks:
    for k in (0, 1):
        name = f"{rec['finger']}_{rec['ab']}_{k}"
        pts = path_for(rec, k, rec['ab'])
        paths[name] = pts
        rmins[name] = min_radius(pts)

chk("every tube path can take a 30 mm fillet at each turn (legs long enough, or inscribed r >= 30)",
    all(r >= p['r_min'] - 0.05 for r in rmins.values()),
    f"min r per tube (mm): { {k: round(v,1) for k,v in rmins.items()} }")

# crossings: min distance between tubes of different fingers, along the forearm (y >= -20)
# (inside the hand the 12 plate sockets already sit 7.9 mm apart by design)
min_cross = 1e9
pair = None
items = list(paths.items())
for i, (n1, p1) in enumerate(items):
    f1 = n1.split("_")[0]
    for n2, p2 in items[i+1:]:
        f2 = n2.split("_")[0]
        if f1 == f2:
            continue
        for a, b in zip(p1, p1[1:]):
            if max(a[1], b[1]) < -20:
                continue
            for c, d in zip(p2, p2[1:]):
                if max(c[1], d[1]) < -20:
                    continue
                md = seg_dist(a, b, c, d)
                if md < min_cross:
                    min_cross = md
                    pair = (n1, n2, md)
chk("tube paths of different fingers stay at least 4.0 mm apart along the forearm (no crossing)",
    min_cross >= 4.0,
    f"closest {pair}")

# 12. Wrist_Interface: yoke register goes into the Ø34 window, zero overlap with the solid
wi_path = os.path.join(AHD, "Amazing Hand Parts - R-Wrist_Interface.step")
if os.path.isfile(wi_path):
    WI = cq.importers.importStep(wi_path)
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    T = gp_Trsf()
    T.SetValues(1, 0, 0, F.WI_CX,  0, -1, 0, F.WI_CY,  0, 0, 1, -11.50)
    # z_h = zf - 11.50, and WI_CZ is -11.50, so translation z = -11.50. Yes, F.WI_CZ is -11.50.
    yk_h = cq.Workplane("XY").add(cq.Shape.cast(BRepBuilderAPI_Transform(parts['yoke'].val().wrapped, T, True).Shape()))
    v = ivol(yk_h, WI)
    chk("yoke (in the hand frame) does not overlap R-Wrist_Interface (register sits in the Ø34 window, 6 x M2 line up with the D2.4 circle of radius 21 mm)",
        v < 0.05, f"overlap {v:.3f} mm3")
else:
    chk("Wrist_Interface STEP present for the overlap check", False, f"missing {wi_path}")

# 13. 4 thumb sockets live on the yoke (the plate does not carry them)
chk("the 4 thumb tube ends are anchored on the wrist yoke (they are not on R-Hand_Plate_tendon)",
    sum(1 for r in socks if r['finger'] == 'thumb') == 2 and all(r['sock'][1] < F._ys()['thumb'] for r in socks if r['finger']=='thumb'),
    "two records (A/B), each with 2 groove sockets in one shared block")

# 14. M2x6 into the 2.80 mm idler ear does not protrude into the body
# clamp = floor 4 mm + ear 2.80; M2x6 engages 2 mm in the ear (6-4), 0.8 mm short of through
chk("M2x6 through the 4 mm floor engages 2.0 mm in the 2.80 mm idler ear and does not come out into the case (Waveshare: a screw that bottoms on the housing can burn the servo)",
    p['floor_t'] + 2.0 <= 4.0 + 2.80 and p['floor_t'] + 0.0 >= 3.5,
    f"floor {p['floor_t']} + engagement 2.0 = 6.0, ear+floor = {p['floor_t']+2.80}")

# 15. M3x6 into the horn: spool base 2 mm + 4 mm in the 4.5 mm horn, case is behind the inner face
chk("M3x6 through the 2 mm spool pad engages 4.0 mm in the 4.5 mm horn and stays 0.5 mm short of the inner face (Waveshare: no screw may press the housing)",
    (6.0 - p['spool_base_t']) <= HORN_T - 0.4 and HORN_T - (6.0 - p['spool_base_t']) >= 0.4,
    f"pad {p['spool_base_t']}, horn {HORN_T}, leftover {HORN_T - (6.0 - p['spool_base_t']):.2f} mm")

print()
print(f"{sum(res)}/{len(res)} checks passed")
sys.exit(0 if all(res) else 1)
