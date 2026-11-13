# Verification of the v16 one-piece flat forearm plate
# (packed single row of 8 STS3215, body-to-body, TL/TR/BL/BR,
#  8 end-wall M3 attachments, 4 per end / 2 per side, clipped M2 posts
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

print("building v16 plate...")
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

# 2. thicknesses and v16 features, still the v13 envelope (56 mm, no rails)
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

# 8. still no wrist flange, U flanges, sockets, second plate or v14 rails
extra = [k for k in pat if k in ("front_wi_m2", "side_flange_m3", "web_shell_top_m3",
                                   "web_shell_bot_m3", "elbow_m3", "joint_m3",
                                   "attach_m3", "web_m3")]
chk("no wrist flange, no U flanges, no joint, no socket bosses, no second plate, no v14 rails or v15 web M3",
    extra == [] and "plate_bottom" not in parts and "plate_top" not in parts
    and "plate" in parts and "end_m3" in pat,
    f"extra patterns={extra}, keys={sorted(parts)}, pat={sorted(pat)}")

# 9. 8 end-wall M3: 4 per end, TWO on each side, not 1 per side
end = pat["end_m3"]["holes"]
end_xs = sorted(set(h["x"] for h in end))
end_zs = sorted(set(h["z"] for h in end))
n_front = sum(1 for h in end if h["end"] == "front")
n_back = sum(1 for h in end if h["end"] == "back")
# two columns (sides), two rows (stacked in Z)
per_side_front = {}
for h in end:
    if h["end"] == "front":
        per_side_front.setdefault(h["x"], 0)
        per_side_front[h["x"]] += 1
two_per_side = per_side_front == {-p["end_m3_x"]: 2, p["end_m3_x"]: 2}
# holes are open through the mid-wall
open_ok, cbore_ok, edge_ok = True, True, True
ye = parts["y_end"]
wt = p["wall_t"]
for h in end:
    y_mid = (h["y_out"] + h["y_in"]) / 2
    if pl.val().isInside(cq.Vector(h["x"], y_mid, h["z"]), 0.2):
        open_ok = False
    # counterbore on the inner face
    y_in = h["y_in"]
    # a point 0.5 mm into the pack from the inner face should be empty of plate
    # and a point 0.5 mm into the wall from the inner face, on axis, is the cbore (empty)
    if h["end"] == "front":
        if pl.val().isInside(cq.Vector(h["x"], wt - 0.5, h["z"]), 0.15):
            cbore_ok = False
    else:
        if pl.val().isInside(cq.Vector(h["x"], ye - wt + 0.5, h["z"]), 0.15):
            cbore_ok = False
    # stay inside the plate width and the wall height
    if abs(h["x"]) + p["m3_clear"] / 2 > p["half_w"] - 1.0:
        edge_ok = False
    if not (0.0 > h["z"] > -p["wall_h"] + p["m3_clear"] / 2 + 0.8):
        edge_ok = False
chk("end walls have 4 M3 each (2 per side of the centre, stacked in Z), clearance 3.4, inner counterbore, 56 mm plate",
    len(end) == 8 and n_front == 4 and n_back == 4 and two_per_side
    and end_xs == [-p["end_m3_x"], p["end_m3_x"]]
    and list(end_zs) == sorted(p["end_m3_z"])
    and abs(p["end_m3_x"] - 24.0) < 1e-9
    and abs(p["m3_clear"] - 3.4) < 1e-9
    and open_ok and cbore_ok and edge_ok,
    f"n={len(end)} front={n_front} back={n_back} xs={end_xs} zs={end_zs} "
    f"two_per_side={two_per_side} open={open_ok} cbore={cbore_ok} edge={edge_ok}")

# 10. end M3 miss the front cable holes and stay off the pack mid-plane
cable_ok, cable_min = True, 1e9
need = p["cable_hole_d"] / 2 + p["m3_clear"] / 2 + 0.6  # ~7.3
for h in end:
    if h["end"] != "front":
        continue
    for cx, cz in pat["cable_front"]["holes"]:
        d = math.hypot(h["x"] - cx, h["z"] - cz)
        cable_min = min(cable_min, d)
        if d < need:
            cable_ok = False
chk("front end M3 stay clear of the two Ø10 cable holes; all 8 stay in the end walls",
    cable_ok and cable_min >= need
    and all(h["dir"] == "Y" for h in end),
    f"min M3-cable = {cable_min:.2f} mm (need >= {need:.2f})")

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
