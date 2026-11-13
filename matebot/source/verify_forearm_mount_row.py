# Verification of the v15 one-piece flat forearm plate
# (packed single row of 8 STS3215, body-to-body, TL/TR/BL/BR,
#  8 web M3 attachments over the bodies, clipped M2 posts
#  with a countersink on the outer face).
# Usage: python verify_forearm_mount_row.py
import os, sys, math
import cadquery as cq
from sts3215 import (
    BODY_L, BODY_W, BODY_H_FLANGE, H_TO_HORN, H_BOTH_HORNS, SHAFT_FROM_OUT,
    SHAFT_FROM_CABLE, HORN_OD, HORN_BCD, HORN_HOLE_D, HORN_T, IDL_HOLES,
    MOUNT_HOLE_D, EAR_T_IDLER, envelope, horn_holes_xy,
)
import forearm_mount_row as F

HERE = os.path.dirname(os.path.abspath(__file__))
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

print("building v15 plate...")
parts = F.build_all()
p = F.P
sts = parts["stations"]
pat = parts["patterns"]
pl = parts["plate"]

# 1. one solid, fits a 250 mm bed
w = pl
sols = w.solids().vals()
bb = w.val().BoundingBox()
mx = max(bb.xlen, bb.ylen, bb.zlen)
chk("plate: one valid solid, max dim <= 250 mm",
    len(sols) == 1 and all(s.isValid() for s in sols) and mx <= 250,
    f"solids={len(sols)} max={mx:.1f}  {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm  vol={w.val().Volume():.0f} mm3")

sp = parts["spool_r8"]
bb_s = sp.val().BoundingBox()
sols_s = sp.solids().vals()
chk("spool_r8: one valid solid, max dim <= 250 mm",
    len(sols_s) == 1 and all(s.isValid() for s in sols_s) and max(bb_s.xlen, bb_s.ylen, bb_s.zlen) <= 250,
    f"solids={len(sols_s)}  {bb_s.xlen:.1f} x {bb_s.ylen:.1f} x {bb_s.zlen:.1f} mm")

# 2. thicknesses and v15 features, still the v13 envelope (56 mm, no rails)
chk("web 4 mm, low end walls 3.5 x 16 mm, plate 56 mm wide, M2 posts 3.5 mm wall / 3.5 mm tall, no U flanges",
    p["web_t"] >= 4.0 and p["wall_t"] >= 3.0 and p["wall_h"] >= 8.0
    and abs(p["half_w"] - 28.0) < 1e-9
    and abs(p["m2_boss_wall"] - 3.5) < 1e-9 and abs(p["m2_boss_h"] - 3.5) < 1e-9,
    f"web {p['web_t']}, wall_t {p['wall_t']}, wall_h {p['wall_h']}, half_w {p['half_w']}, "
    f"m2_boss_wall {p['m2_boss_wall']}, m2_boss_h {p['m2_boss_h']}")

# 3. official servo numbers
chk("STS3215 body 45.22 x 24.72, height to horn 35, both horns 37.25, shaft 10.11 from output end",
    abs(BODY_L - 45.22) < 1e-6 and abs(BODY_W - 24.72) < 1e-6 and abs(H_TO_HORN - 35.0) < 1e-6
    and abs(H_BOTH_HORNS - 37.25) < 1e-6 and abs(SHAFT_FROM_OUT - 10.11) < 1e-6,
    f"{BODY_L} x {BODY_W}, H_TO_HORN {H_TO_HORN}, H_BOTH {H_BOTH_HORNS}, shaft {SHAFT_FROM_OUT}")

# 4. spool_r8 unchanged
holes_ok, details = True, []
for x, y in horn_holes_xy():
    inside = sp.val().isInside(cq.Vector(x, y, 6.0), 0.2)
    details.append((round(x, 2), round(y, 2), inside))
    if inside:
        holes_ok = False
radii = [math.hypot(x, y) for x, y in horn_holes_xy()]
chk("spool_r8: official 14 mm horn BCD, M3 (Ø3.4) holes open, flanges Ø22, height 11.5, r=8 grooves",
    holes_ok and all(abs(r - 7.0) < 1e-9 for r in radii)
    and abs(bb_s.zlen - 11.5) < 0.05 and abs(bb_s.xlen - 22.0) < 0.05,
    f"hole-inside? {details}, bbox {bb_s.xlen:.2f} x {bb_s.ylen:.2f} x {bb_s.zlen:.2f}")

# 5. layout
seq = [(s["finger"], s["ab"], s["face"], s["side"]) for s in sts]
want = [
    ("thumb", "A", "top", "left"), ("thumb", "B", "top", "right"),
    ("index", "A", "bottom", "left"), ("index", "B", "bottom", "right"),
    ("middle", "A", "top", "left"), ("middle", "B", "top", "right"),
    ("ring", "A", "bottom", "left"), ("ring", "B", "bottom", "right"),
]
ys = [s["y"] for s in sts]
xs = [s["xf"] for s in sts]
across = all(abs(abs(s["xf"]) - F.SHAFT_X) < 1e-9 for s in sts)
bot_zf = [-H_TO_HORN - p["m2_boss_h"] for s in sts if s["face"] == "bottom"]
top_zf = [s["zf"] for s in sts if s["face"] == "top"]
chk("single row of 8, long axis across the forearm, TL/TR/BL/BR, same-face adjacent pairs, shafts alternate L/R",
    seq == want and ys == sorted(ys) and across and xs == [-12.5, 12.5] * 4
    and all(abs(s["zf"]) < 1e-9 for s in sts if s["face"] == "top")
    and all(abs(s["zf"] - (-H_TO_HORN - p["m2_boss_h"])) < 1e-9 for s in sts if s["face"] == "bottom"),
    f"seq={seq}, y={[round(y,2) for y in ys]}, xf={xs}, bottom zf shifted by {p['m2_boss_h']} mm posts")

gaps = [round(ys[i+1] - ys[i] - BODY_W, 3) for i in range(7)]
chk("bodies packed face-to-face: nominal gap 0-0.5 mm (0.4 mm), pitch = BODY_W + gap, no service gap",
    0.0 <= p["pack_gap"] <= 0.5 and abs(p["pitch"] - (BODY_W + p["pack_gap"])) < 1e-9
    and all(abs(g - p["pack_gap"]) < 1e-9 for g in gaps)
    and abs(p["pack_len"] - (8 * BODY_W + 7 * p["pack_gap"])) < 1e-9,
    f"pack_gap={p['pack_gap']}, pitch={p['pitch']:.2f}, pack_len={p['pack_len']:.2f}, gaps={gaps}")

# 6. length is barely more than the packed row
ye = parts["y_end"]
expect = p["pack_len"] + 2 * p["wall_t"]
chk("plate length = packed 8 bodies + a small front wall + a small back wall, still well under 250 mm",
    abs(ye - expect) < 1e-9 and ye <= 250 and (ye - p["pack_len"]) <= 10.0,
    f"y_end={ye:.2f} mm, pack={p['pack_len']:.2f} mm, extra={ye-p['pack_len']:.2f} mm")

# 7. M2 only on the four idler-facing servos (index, ring), 16 holes, open through web+post, countersunk
m2 = pat["servo_idler_m2"]["holes"]
m2_fingers = sorted({h["finger"] for h in m2})
misses = []
csk_open = []
csk_side_solid = []
for s in sts:
    if s["face"] != "bottom":
        continue
    for x, y, z in F.idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
        mid = cq.Vector(x, y, p["web_t"] / 2)
        if pl.val().isInside(mid, 0.2):
            misses.append((round(x, 2), round(y, 2)))
        # countersink should be open just below the outer face, on axis
        if pl.val().isInside(cq.Vector(x, y, p["web_t"] - 0.4), 0.15):
            csk_open.append((round(x, 2), round(y, 2)))
        # plastic remains beside the countersink (r = 3.0 mm from axis, at the outer face)
        if pl.val().isInside(cq.Vector(x + 3.0, y, p["web_t"] - 0.2), 0.15):
            csk_side_solid.append(True)
        else:
            csk_side_solid.append(False)
chk("16 M2 holes line up with the idler ears of index and ring only, countersunk on the outer face, access from the outside",
    len(m2) == 16 and m2_fingers == ["index", "ring"] and misses == []
    and csk_open == [] and all(csk_side_solid)
    and abs(p["m2_csk_d"] - 4.8) < 1e-9 and abs(p["m2_csk_angle"] - 90.0) < 1e-9,
    f"n={len(m2)}, fingers={m2_fingers}, misses={misses}, csk_still_solid={csk_open}, "
    f"csk_side_solid={sum(csk_side_solid)}/{len(csk_side_solid)}, "
    f"web={p['web_t']} + post={p['m2_boss_h']} + 2.5 mm in the 2.8 mm ear = M2x10")

# 8. still no wrist flange, U flanges, sockets, second plate, rails or end posts
extra = [k for k in pat if k in ("front_wi_m2", "side_flange_m3", "web_shell_top_m3",
                                   "web_shell_bot_m3", "elbow_m3", "joint_m3",
                                   "end_m3", "web_m3")]
chk("no wrist flange, no U flanges, no joint, no socket bosses, no second plate, no v14 rails or end posts",
    extra == [] and "plate_bottom" not in parts and "plate_top" not in parts
    and "plate" in parts and "attach_m3" in pat,
    f"extra patterns={extra}, keys={sorted(parts)}, pat={sorted(pat)}")

# 9. 8 web M3 over the solid body, opposite the cut-outs
att = pat["attach_m3"]["holes"]
att_ok = True
att_detail = []
for h, s in zip(att, sts):
    want_x = -s["xf"]
    good = (h["i"] == s["i"] and abs(h["x"] - want_x) < 1e-9 and abs(h["y"] - s["y"]) < 1e-9)
    # hole is in the web (open at mid-thickness) and not in a cut-out
    mid = cq.Vector(h["x"], h["y"], p["web_t"] / 2)
    open_ = not pl.val().isInside(mid, 0.2)
    # counterbore is open on the inner face
    inner = not pl.val().isInside(cq.Vector(h["x"], h["y"], 0.5), 0.15)
    # enough meat from the cut-out at (xf, y): cut r is 14 (spool) or 11 (idler)
    cut_r = p["spool_cut_d"] / 2 if s["face"] == "top" else p["idler_cut_d"] / 2
    dist_cut = abs(h["x"] - s["xf"]) - cut_r
    # over the body: |x| <= BODY_L/2
    over_body = abs(h["x"]) <= BODY_L / 2 + 0.01
    att_detail.append((h["i"], round(h["x"], 2), round(h["y"], 2), open_, inner,
                       round(dist_cut, 2), over_body))
    if not (good and open_ and inner and dist_cut >= 3.0 and over_body):
        att_ok = False
chk("8 M3 clearance holes, one over each servo body, opposite the cut-out, inside-to-outside with an inner counterbore",
    att_ok and len(att) == 8 and abs(p["m3_clear"] - 3.4) < 1e-9
    and abs(p["m3_cbore_d"] - 6.5) < 1e-9 and p["m3_cbore_h"] >= 1.6,
    f"n={len(att)}, items={att_detail}")

# 10. M3 heads / holes miss the M2 posts and the cut-outs; M3 centre-to-M2 >= 8 mm
m3_m2_ok, m3_m2_min = True, 1e9
for h in att:
    for m in m2:
        d = math.hypot(h["x"] - m["x"], h["y"] - m["y"])
        m3_m2_min = min(m3_m2_min, d)
        if d < (p["m3_cbore_d"] / 2 + p["m2_boss_od"] / 2):
            # may still be ok if the M2 boss is on a different servo and clipped;
            # require a hard 8 mm centre distance
            pass
        if d < 8.0:
            m3_m2_ok = False
chk("web M3 stay clear of the M2 holes/posts (centre distance >= 8 mm) and of the cut-outs",
    m3_m2_ok and m3_m2_min >= 8.0,
    f"min M3-M2 = {m3_m2_min:.2f} mm")

# 11. spool / idler cut-outs
spool_pts = pat["spool_cuts"]["holes"]
idler_pts = pat["idler_cuts"]["holes"]
want_spool = [(s["xf"], s["y"]) for s in sts if s["face"] == "top"]
want_idler = [(s["xf"], s["y"]) for s in sts if s["face"] == "bottom"]
chk("Ø28 spool cut-outs only where a spool faces the plate (thumb, middle); Ø22 idler clearance on index, ring",
    spool_pts == want_spool and idler_pts == want_idler
    and len(spool_pts) == 4 and len(idler_pts) == 4,
    f"spool={spool_pts}, idler={idler_pts}")

# 12. two front cable holes
cables = pat["cable_front"]["holes"]
chk("front wall still has exactly two cable holes (Ø10)",
    len(cables) == 2 and p["cable_hole_d"] == 10.0,
    f"cables={cables}, d={p['cable_hole_d']}")

# 13. spools through the cut-outs, no intersection with the plate
spool_hits = []
for s in sts:
    placed = F.place_S(sp, s["xf"], s["y"], s["zf"], s["face"], s["side"])
    vol = ivol(placed, pl)
    if not (vol == 0 or (isinstance(vol, float) and vol < 1.0)):
        spool_hits.append((s["i"], s["finger"], s["ab"], vol))
chk("spools pass through the Ø28 cut-outs (top face) or clear the plate (bottom face)",
    spool_hits == [],
    f"overlaps={spool_hits}")

# 14. servo envelopes clear the plate and the (clipped) M2 posts
env_hits = []
for s in sts:
    env = F.place_S(envelope(cl=0.0, with_horns=True, with_cables=True),
                    s["xf"], s["y"], s["zf"], s["face"], s["side"])
    vol = ivol(env, pl)
    if not (vol == 0 or (isinstance(vol, float) and vol < 1.0)):
        env_hits.append((s["i"], s["finger"], s["ab"], s["face"], vol))
chk("all 8 servo envelopes clear the plate and the clipped M2 posts",
    env_hits == [],
    f"overlaps={env_hits}")

# 15. front/back walls flush with the pack
first_start = sts[0]["y"] - BODY_W / 2
last_end = sts[-1]["y"] + BODY_W / 2
chk("end walls sit flush with the first and last body faces (pack is 200.56 mm)",
    abs(first_start - p["wall_t"]) < 1e-9 and abs(last_end - (p["wall_t"] + p["pack_len"])) < 1e-9,
    f"first_start={first_start:.2f}, last_end={last_end:.2f}, wall_t={p['wall_t']}, pack={p['pack_len']:.2f}")

# 16. bbox is the v13 56 x 207.6 mm plate, height is web + walls (posts are shorter than the walls)
chk("assembled pack is one flat 56 mm plate, max dim <= 250 mm, height is web + end walls",
    abs(bb.xlen - 2 * p["half_w"]) < 0.2 and abs(bb.xlen - 56.0) < 0.2 and bb.ylen < 220
    and bb.zlen <= p["web_t"] + p["wall_h"] + 0.2,
    f"bbox {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, half_w={p['half_w']}")

# 17. features are only on the body side of the web (printable flat, no supports)
chk("all added material is on the body side of the web (printable outer-face down, no supports)",
    bb.zmax <= p["web_t"] + 0.05 and bb.zmin >= -p["wall_h"] - 0.05,
    f"zmin={bb.zmin:.2f}, zmax={bb.zmax:.2f}")

# 18. posts do not enter the pack gaps (a point in the mid-gap, at post height, is empty of plate)
gap_hits = []
for i in range(7):
    y_mid = p["wall_t"] + (i + 1) * BODY_W + i * p["pack_gap"] + p["pack_gap"] / 2
    # sample a few X along the mid-gap at z = -1.5 (inside the post height)
    for x in (-20, -12.5, 0, 12.5, 20):
        if pl.val().isInside(cq.Vector(x, y_mid, -1.5), 0.15):
            gap_hits.append((round(x, 2), round(y_mid, 2)))
chk("M2 posts are clipped out of the 0.4 mm pack gaps",
    gap_hits == [],
    f"gap_hits={gap_hits}")

print()
n_ok = sum(res)
print(f"{n_ok}/{len(res)} checks passed")
sys.exit(0 if all(res) else 1)
