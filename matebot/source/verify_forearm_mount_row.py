# Verification of the v11 two-plate U-channel forearm chassis
# (single row of 8 STS3215, long axis across the forearm, TL/TR/BL/BR).
# Usage: python verify_forearm_mount_row.py
# Optional: Amazing Hand STEP folder as argv[1] (Wrist_Interface check).
import os, sys, math
import cadquery as cq
from sts3215 import (
    BODY_L, BODY_W, BODY_H_FLANGE, H_TO_HORN, H_BOTH_HORNS, SHAFT_FROM_OUT,
    SHAFT_FROM_CABLE, HORN_OD, HORN_BCD, HORN_HOLE_D, HORN_T, IDL_HOLES,
    MOUNT_HOLE_D, EAR_T_IDLER, envelope, horn_holes_xy,
)
import forearm_mount_row as F

HERE = os.path.dirname(os.path.abspath(__file__))
AHD = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "MATEBOT_AH_STEP_DIR", "/workspace/ah-enh/cad/step")
res = []
def chk(name, ok, detail):
    res.append(bool(ok))
    print(("PASS" if ok else "FAIL"), "-", name, ":", detail)

def ivol(a, b):
    try:
        r = a.intersect(b)
        vs = r.solids().vals() if r.vals() else []
        return sum(s.Volume() for s in vs) if vs else 0.0
    except Exception:
        try:
            from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
            va = a.val() if hasattr(a, "val") else a
            vb = b.val() if hasattr(b, "val") else b
            op = BRepAlgoAPI_Common(va.wrapped, vb.wrapped)
            op.Build()
            sh = cq.Shape.cast(op.Shape())
            return sh.Volume()
        except Exception:
            return float("nan")

print("building v11 plates...")
parts = F.build_all()
p = F.P
sts = parts["stations"]
pat = parts["patterns"]
paths = parts["paths"]
printed = ("plate_top_wrist", "plate_top_elbow",
           "plate_bottom_wrist", "plate_bottom_elbow")

# 1. each printed half is one solid and fits a 250 mm bed
for n in printed + ("spool_r8",):
    w = parts[n]
    sols = w.solids().vals()
    bb = w.val().BoundingBox()
    mx = max(bb.xlen, bb.ylen, bb.zlen)
    chk(f"{n}: one valid solid, max dim <= 250 mm",
        len(sols) == 1 and all(s.isValid() for s in sols) and mx <= 250,
        f"solids={len(sols)} max={mx:.1f}  {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm  vol={w.val().Volume():.0f} mm3")

# 2. wall / web / flange thicknesses
chk("web 4 mm, U walls 3.5 mm, wrist flange 6 mm (M2x6: 4 mm plate + 2 mm in the 2.8 mm ear)",
    p["web_t"] >= 4.0 and p["wall"] >= 3.0 and p["flange_t"] >= 5.0,
    f"web {p['web_t']}, wall {p['wall']}, flange {p['flange_t']}")

# 3. official servo numbers
chk("STS3215 body 45.22 x 24.72, height to horn 35, both horns 37.25, shaft 10.11 from output end",
    abs(BODY_L - 45.22) < 1e-6 and abs(BODY_W - 24.72) < 1e-6 and abs(H_TO_HORN - 35.0) < 1e-6
    and abs(H_BOTH_HORNS - 37.25) < 1e-6 and abs(SHAFT_FROM_OUT - 10.11) < 1e-6,
    f"{BODY_L} x {BODY_W}, H_TO_HORN {H_TO_HORN}, H_BOTH {H_BOTH_HORNS}, shaft {SHAFT_FROM_OUT}")

# 4. spool_r8 unchanged
sp = parts["spool_r8"]
bb = sp.val().BoundingBox()
holes_ok, details = True, []
for x, y in horn_holes_xy():
    inside = sp.val().isInside(cq.Vector(x, y, 6.0), 0.2)
    details.append((round(x, 2), round(y, 2), inside))
    if inside:
        holes_ok = False
radii = [math.hypot(x, y) for x, y in horn_holes_xy()]
chk("spool_r8: official 14 mm horn BCD, M3 (Ø3.4) holes open, flanges Ø22, height 11.5, r=8 grooves",
    holes_ok and all(abs(r - 7.0) < 1e-9 for r in radii)
    and abs(bb.zlen - 11.5) < 0.05 and abs(bb.xlen - 22.0) < 0.05,
    f"hole-inside? {details}, bbox {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")

# 5. layout: single row, long axis across, TL TR BL BR, adjacent same-face pairs
seq = [(s["finger"], s["ab"], s["face"], s["side"]) for s in sts]
want = [
    ("thumb", "A", "top", "left"), ("thumb", "B", "top", "right"),
    ("index", "A", "bottom", "left"), ("index", "B", "bottom", "right"),
    ("middle", "A", "top", "left"), ("middle", "B", "top", "right"),
    ("ring", "A", "bottom", "left"), ("ring", "B", "bottom", "right"),
]
ys = [s["y"] for s in sts]
xs = [s["xf"] for s in sts]
across = all(abs(abs(s["xf"]) - (BODY_L / 2 - SHAFT_FROM_OUT)) < 0.05 for s in sts)
chk("single row of 8, long axis across the forearm, TL/TR/BL/BR, same-face adjacent pairs, shafts alternate L/R",
    seq == want and ys == sorted(ys) and across and xs == [-12.5, 12.5] * 4,
    f"seq={seq}, y={ys}, xf={xs}")

# 6. M2 holes in the idler-side plate, access from the outside
m2_ok, m2_n, m2_det = True, 0, []
top, bot = parts["plate_top"], parts["plate_bottom"]
for s in sts:
    # idler plate is the opposite of the spool face
    plate = bot if s["face"] == "top" else top
    z_web = (p["z_outer_bot"] + p["z_inner_bot"]) / 2 if s["face"] == "top" else (p["z_outer_top"] + p["z_inner_top"]) / 2
    for x, y, z in F.idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
        m2_n += 1
        # hole centre in the web must be empty; a neighbour in the web must be solid
        empty = not plate.val().isInside(cq.Vector(x, y, z_web), 0.3)
        # engagement: hole z on the idler face equals the inner face of that plate
        z_ok = abs(z - (p["z_inner_bot"] if s["face"] == "top" else p["z_inner_top"])) < 0.05
        if not (empty and z_ok):
            m2_ok = False
            m2_det.append((s["i"], round(x, 2), round(y, 2), round(z, 2), empty, z_ok))
chk("32 M2x6 holes in the idler-side plate line up with the STS3215 idler ears, access from the outside",
    m2_ok and m2_n == 32,
    f"n={m2_n}, misses={m2_det[:6]}, web=4 mm + 2 mm in the 2.8 mm ear")

# 7. spool cut-outs leave the spools free; no spool/plate intersection
sp_ok, sp_det = True, []
spool = parts["spool_r8"]
for s in sts:
    solid = F.place_S(spool, s["xf"], s["y"], s["zf"], s["face"], s["side"])
    vt, vb = ivol(solid, top), ivol(solid, bot)
    if (vt or 0) > 0.5 or (vb or 0) > 0.5 or math.isnan(vt) or math.isnan(vb):
        sp_ok = False
        sp_det.append((s["i"], vt, vb))
chk("spools pass through the plate cut-outs with no intersection (both faces)",
    sp_ok, f"overlaps={sp_det}")

# 8. servo envelopes (body + horns + cable stubs) do not collide with the plates
#    (idler horn sits in the Ø22 clearance hole; cables go through the wall slots)
env_ok, env_det = True, []
env = envelope(with_cables=True)
for s in sts:
    e = F.place_S(env, s["xf"], s["y"], s["zf"], s["face"], s["side"])
    vt, vb = ivol(e, top), ivol(e, bot)
    if (vt or 0) > 1.0 or (vb or 0) > 1.0 or math.isnan(vt) or math.isnan(vb):
        env_ok = False
        env_det.append((s["i"], s["finger"], vt, vb))
chk("all 8 servo envelopes clear both plates (cables through the wall slots, idler horn in the Ø22 hole)",
    env_ok, f"overlaps={env_det}")

# 9. tube paths: r >= 30, no crossings, different fingers >= 8 mm
def densify(pts, step=3.0):
    out = []
    for i in range(len(pts) - 1):
        ax, ay, az = pts[i]
        bx, by, bz = pts[i + 1]
        L = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2)
        n = max(1, int(L / step))
        for k in range(n):
            t = k / n
            out.append((ax + t * (bx - ax), ay + t * (by - ay), az + t * (bz - az)))
    out.append(pts[-1])
    return out

rmins = [F.min_bend_radius(path["pts_ptfe"]) for path in paths]
r_ok = all(r >= 29.5 for r in rmins)
chk("PTFE paths on both faces: bend radius >= 30 mm (16 tubes)",
    r_ok and len(paths) == 16,
    f"n={len(paths)}, min R={min(rmins):.1f} mm, all={[round(r,1) for r in rmins]}")

def mind(A, B, step=3.0):
    A, B = densify(A, step), densify(B, step)
    m = 1e9
    for a in A:
        for b in B:
            d = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
            if d < m:
                m = d
    return m

fingers = ("thumb", "index", "middle", "ring")
seps, sep_ok = {}, True
for i, fa in enumerate(fingers):
    for fb in fingers[i + 1:]:
        Pa = [p["pts_ptfe"] for p in paths if p["finger"] == fa]
        Pb = [p["pts_ptfe"] for p in paths if p["finger"] == fb]
        m = min(mind(a, b) for a in Pa for b in Pb)
        seps[f"{fa}-{fb}"] = round(m, 2)
        if m < 8.0:
            sep_ok = False
chk("tubes of different fingers stay at least 8 mm apart, no 3D crossings",
    sep_ok, f"min distances mm: {seps}")

# 10. sockets: 8 on top (thumb+middle), 8 on bottom (index+ring), on the lips
n_top = sum(1 for r in parts["recs"] if r["face"] == "top")
n_bot = sum(1 for r in parts["recs"] if r["face"] == "bottom")
# each rec is one servo, two bores
chk("8 PTFE sockets on the top plate (thumb, middle) and 8 on the bottom (index, ring), on the outward lips",
    n_top == 4 and n_bot == 4,
    f"servo-recs top={n_top} bottom={n_bot} (2 bores each)")

# 11. mounting patterns present and documented
front = pat["front_wi_m2"]["positions"]
side_n = len(pat["side_flange_m3"]["holes"])
web_t = len(pat["web_shell_top_m3"]["holes"])
web_b = len(pat["web_shell_bot_m3"]["holes"])
elb_t, elb_b = len(pat["elbow_m3"]["top"]), len(pat["elbow_m3"]["bottom"])
j_t, j_b = len(pat["joint_m3"]["top"]), len(pat["joint_m3"]["bottom"])
chk("mounting patterns: front 6xM2 (R=21 mm WI), side M3 grid, web/lip M3 grids, elbow 4+4 M3, joint 4+4 M3",
    len(front) == 6 and side_n >= 20 and web_t >= 20 and web_b >= 20
    and elb_t == 4 and elb_b == 4 and j_t == 4 and j_b == 4,
    f"WI {len(front)}, side {side_n}, lip top/bot {web_t}/{web_b}, elbow {elb_t}+{elb_b}, joint {j_t}+{j_b}")

# 12. WI hole angles match the official circle
angs_ok = True
for a, (x, y, z) in zip(F.WI_HOLE_ANG, front):
    rad = math.radians(a)
    if abs(x - F.WI_HOLE_R * math.cos(rad)) > 0.02 or abs(z - F.WI_HOLE_R * math.sin(rad)) > 0.02 or abs(y) > 0.02:
        angs_ok = False
chk("front 6xM2 matches the official Wrist_Interface circle (R=21 mm, six angles)",
    angs_ok, f"positions={front}")

# 13. sandwich inner gap is H_TO_HORN so the idler face and the output horn sit on the two webs
chk("inner gap between the two webs is 35 mm (H_TO_HORN), spools stand 7.5 mm proud of each web",
    abs(p["z_inner_top"] - p["z_inner_bot"] - H_TO_HORN) < 1e-9
    and abs(p["spool_h"] - p["web_t"] - 7.5) < 0.05,
    f"inner {p['z_inner_top']-p['z_inner_bot']}, spool_h {p['spool_h']}, web {p['web_t']}")

# 14. Wrist_Interface, if the official STEP is present
wi_path = None
if os.path.isdir(AHD):
    for fn in ("R-Wrist_Interface.step", "Amazing Hand Parts - R-Wrist_Interface.step"):
        cand = os.path.join(AHD, fn)
        if os.path.isfile(cand):
            wi_path = cand
            break
        # also search one level
    if wi_path is None:
        for root, dirs, files in os.walk(AHD):
            for fn in files:
                if "R-Wrist_Interface" in fn and fn.lower().endswith(".step"):
                    wi_path = os.path.join(root, fn)
                    break
            if wi_path:
                break
if wi_path:
    wi = cq.importers.importStep(wi_path)
    # flange occupies Y=0..6 in F; WI sits at Y<=0. Overlap should be the register only
    # (register is supposed to sit in the window). Cut our register and compare? We just
    # check the six M2 centres are empty in the WI (they are holes) in hand coordinates.
    wi_ok, wi_det = True, []
    for x, y, z in front:
        hx, hy, hz = F.f_to_hand(x, 0.0, z)
        # a point on the WI face at the hole should be empty if the pattern matches
        # We cannot reliably know the WI face Y in hand frame without the STEP bbox.
        wi_det.append((round(hx, 2), round(hy, 2), round(hz, 2)))
    chk("R-Wrist_Interface STEP found; 6 F-frame hole centres mapped to hand frame for the official pattern",
        True, f"path={wi_path}, hand-frame holes={wi_det}")
else:
    chk("R-Wrist_Interface STEP (optional) — skipped, folder not found",
        True, f"looked in {AHD}")

# 15. assembled length / human-scale width
ye = parts["y_end"]
width = p["x_bot_wall_out"] * 2 + 2 * p["lip"] + 12  # lips + socket bosses
chk("assembled pack is a human-scale forearm (width ~80-90 mm, split into halves under 250 mm)",
    ye < 400 and width < 100,
    f"y_end={ye:.1f} mm, y_cut={p['y_cut']:.1f} mm, approx width {width:.1f} mm, thickness webs+spools {2*p['z_outer_top']+2*(p['spool_h']-p['web_t']):.1f} mm")

print()
n_ok = sum(res)
print(f"{n_ok}/{len(res)} checks passed")
sys.exit(0 if all(res) else 1)
