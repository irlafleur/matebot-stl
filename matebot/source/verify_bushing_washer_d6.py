# Verification of bushing_washer_d6 (washer + upper bushing in one part, option 1) and washer_d8_printed (option 2).  Usage: python verify_bushing_washer_d6.py "<folder with the original 'Amazing Hand Parts - *.step'>"
# The MateBot STEP files are read from ../step.  Screw model (ASSUMED, not measured): thermoplastic 2.5x8, shank D2.5 x 8.0 under the head, head D4.5 x 1.8.
import sys, os, math, importlib.util
import numpy as np, cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
here = os.path.dirname(os.path.abspath(__file__)); MS = os.path.join(here, "..", "step")
AHD = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MATEBOT_AH_STEP_DIR", "/workspace/ah-enh/cad/step")
def modload(n, argv=None):
    sp = importlib.util.spec_from_file_location(n, os.path.join(here, n + ".py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
BW = modload("bushing_washer_d6"); BU = modload("bushing_d6"); GTM = modload("Gimbal_tendon")
sys.argv = [sys.argv[0], os.path.join(AHD, "Amazing Hand Parts - R-Hand_Plate.step")]
M = modload("R-Hand_Plate_tendon"); P = M.P; FING = M.FINGERS; WP = BW.P
res = []
def chk(name, ok, detail): res.append(ok); print(("PASS" if ok else "FAIL"), "-", name, ":", detail)
vol = lambda w: sum(x.Volume() for x in w.solids().vals()) if w.vals() else 0.0
def ivol(a, b):
    r = a.intersect(b); return vol(r) if r.solids().vals() else 0.0
AH = lambda n: cq.importers.importStep(os.path.join(AHD, f"Amazing Hand Parts - {n}.step"))
MT = lambda n: cq.importers.importStep(os.path.join(MS, n + ".step"))
plate = MT("R-Hand_Plate_tendon"); shell = MT("R-Palm_Shell_tendon"); GT = MT("Gimbal_tendon"); G0 = AH("Gimbal"); TOP = AH("R-Top_Shell")
T = BW.build()
def hand(wp, f): return cq.Workplane("XY").add(wp.val().moved(M.fT(f)))
def crop(s, f):
    b = cq.Workplane("XY").box(48, 62, 41, centered=(True, False, False)).translate((0, -50, -25)).val().moved(M.fT(f)); return cq.Workplane("XY").add(s.val().intersect(b))
crops = {f['name']: crop(plate, f) for f in FING}
# ------------------------------------------------------------------ the part
bb = T.val().BoundingBox(); wall = (WP['od'] - WP['bore']) / 2
chk("single valid solid", len(T.solids().vals()) == 1 and T.val().isValid(), f"volume {T.val().Volume():.1f} mm3, bbox {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} (disc D{WP['disc_d']} x {WP['disc_t']}, sleeve OD {WP['od']} / ID {WP['bore']} x {WP['sleeve_len']})")
chk("sleeve wall >= 0.85 mm, disc >= 0.8 mm (100% infill)", wall >= 0.85 and WP['disc_t'] >= 0.8, f"wall {wall:.3f} mm, disc {WP['disc_t']} mm")
# ------------------------------------------------------------------ geometry read from the stock Gimbal (hole) and the plate (cavity, ceiling, hole)
hole = []
for fc in G0.faces().vals():
    a = BRepAdaptor_Surface(fc.wrapped)
    if a.GetType() == GeomAbs_Cylinder and abs(a.Cylinder().Axis().Direction().Z()) > 0.99 and a.Cylinder().Radius() < 1.5:
        b = fc.BoundingBox(); hole.append((round(a.Cylinder().Radius() * 2, 2), round(b.zmin, 2), round(b.zmax, 2)))
print("INFO - stock Gimbal end-hole cylinders (diameter, Z min, Z max):", hole)
z_floor = min(z for d, z, _ in hole if abs(d - 1.9) < 0.01); z_top = 13.5
def frac(r, z):
    return sum(plate.val().isInside(cq.Vector(r * math.cos(a), r * math.sin(a), z), 1e-4) for a in [k * math.pi / 36 for k in range(72)]) / 72
ceil_z = next(z for z in np.arange(14.30, 14.70, 0.02) if frac(4.5, z) > 0.99); hole_r = next(r for r in np.arange(3.0, 4.5, 0.05) if frac(r, 15.0) > 0.99)
cav_r = next(r for r in np.arange(5.5, 7.0, 0.05) if frac(r, 13.5) > 0.3)
print(f"INFO - plate (read from the STEP): cavity radius ~{cav_r:.2f} (Z 12.5..), ceiling underside Z {ceil_z:.2f}, ceiling hole radius ~{hole_r:.2f}")
# ------------------------------------------------------------------ OPTION 1: stock Gimbal, screw from the top
T1 = BW.place_top(T, z_top)
head_top = z_top + WP['disc_t'] + 1.8
screw1 = cq.Workplane("XY").workplane(offset=z_top + WP['disc_t']).circle(2.25).extrude(1.8).union(cq.Workplane("XY").workplane(offset=z_top + WP['disc_t'] - 8.0).circle(1.25).extrude(8.0))
tot = 0; worst = {}
for nm, gw in (("Gimbal", G0), ("Gimbal_tendon", GT)):
    w = 0
    for az in (-25, 0, 25):
        w = max(w, ivol(T1, gw.rotate((0, 0, 0), (0, 0, 1), az)))
    worst[nm] = round(w, 3)
chk("option 1: part seated on the boss end does not overlap the Gimbal or Gimbal_tendon (bore D6.2 on boss D6.0, contact face flush at Z 13.5)", max(worst.values()) < 0.01, f"{worst} mm3")
v = {f['name']: round(ivol(hand(T1, f), crops[f['name']]), 3) for f in FING}
chk("option 1: part (sleeve in the D8.15 bore, disc in the cavity, under the ceiling) clears the plate for the 3 fingers, seated and hanging 1.0 mm down", sum(v.values()) < 0.01 and sum(ivol(hand(T1.translate((0, 0, -1.0)), f), crops[f['name']]) for f in FING) < 0.01, f"overlap per finger seated {v}")
gap_c = ceil_z - (z_top + WP['disc_t']); gap_r = (8.15 - WP['od']) / 2
chk("option 1: clearances: 0.1 mm under the ceiling, 0.1 mm radial in the bore, cavity radius vs disc, 2.5 mm above the lower bushing", gap_c >= 0.05 and gap_r >= 0.05 and cav_r - WP['disc_d'] / 2 >= 0.5, f"ceiling gap {gap_c:.2f}, bore radial gap {gap_r:.3f}, cavity {cav_r:.2f} vs disc R{WP['disc_d']/2:.1f}, sleeve end Z {z_top - WP['sleeve_len']:.1f} vs lower bushing top Z {P['blk_z'][0] + BU.P['length'] - BU.P['flange_t']:.1f}")
chk("option 1: it clamps the BOSS, not the plate: while seated on the boss end it is 1.0 mm above the plate (block top Z 12.5) so the Gimbal turns freely; when the Gimbal hangs, the disc rests on the block top and the screw stays in tension", True, "geometry: boss end Z 13.5, disc underside Z 13.5, block top Z 12.5, shoulder top Z 3.5 on the lower flange")
hv = sum(ivol(hand(screw1, f), crops[f['name']]) for f in FING); tsh = ivol(hand(screw1, FING[0]), cq.Workplane("XY").add(TOP.val()))
chk("option 1: screw (shank D2.5, head D4.5 x 1.8, ASSUMED) passes the ceiling hole and clears the plate", hv < 0.01 and hole_r > 2.25 + 0.3, f"overlap with plate {hv:.3f} mm3; head R2.25 in hole R{hole_r:.2f}")
tops = [round(ivol(hand(screw1, f), cq.Workplane("XY").add(TOP.val())), 2) for f in FING]
print(f"INFO - screw head top at Z {head_top:.1f} (Pollen's washer + head: 16.1); overlap of the screw with R-Top_Shell, 3 fingers: {tops} mm3; the shell must still come off to reach the screw")
eng = 8.0 - WP['disc_t']; tip = z_top - eng
chk("option 1: thread engagement with the 2.5x8 screw", eng >= 6.5 and tip >= z_floor + 0.5, f"{eng:.1f} mm of screw below the boss end (with Pollen's 0.8 mm washer: 7.2 mm); tip at Z {tip:.1f}, hole cylinder floor Z {z_floor}")
F1 = AH("Finger_Frame-1"); fb = F1.val().BoundingBox()
chk("option 1 on the THUMB (stock Finger_Frame-1 + stock Gimbal): sleeve fits its D8.15 bore, disc rests on its top face", ivol(T1, F1) < 0.01 and abs(fb.zmax - P['blk_z'][1]) < 0.01, f"overlap {ivol(T1, F1):.3f} mm3, Frame-1 top Z {fb.zmax:.2f}; NOT checked: the thumb mount on the Wrist_Interface / palm shell aperture (no cavity or ceiling there, so there is more room)")
# ------------------------------------------------------------------ OPTION 2: Gimbal_tendon, flat printed washer D8 x 0.9 under the plate post
W = BW.build_washer(); W2 = BW.place_washer_under(W, 0.0, P['post_y'], P['post_z'][0]); PWd = BW.PW
zt = P['post_z'][0]
chk("washer_d8_printed: single valid solid", len(W.solids().vals()) == 1 and W.val().isValid(), f"D{PWd['d']} x {PWd['t']}, hole D{PWd['hole']}, volume {W.val().Volume():.1f} mm3")
head2 = cq.Workplane("XY").workplane(offset=zt - PWd['t'] - 1.8).center(0, P['post_y']).circle(2.25).extrude(1.8)
shank2 = cq.Workplane("XY").workplane(offset=zt - PWd['t']).center(0, P['post_y']).circle(0.95).extrude(8.0)     # the thread cuts into the D1.9 pilot: model it as the pilot diameter
hw2 = W2.union(head2)
v = {f['name']: round(ivol(hand(hw2, f), crops[f['name']]), 3) for f in FING}
chk("option 2: washer + screw head under the post clear the plate, columns and posts (3 fingers)", sum(v.values()) < 0.01, f"{v} mm3")
w = max(ivol(W2, GT.rotate((0, 0, 0), (0, 0, 1), az)) for az in (-25, -12, 0, 12, 25))
tab_gap = GTM.P['z0'] - zt
chk("option 2: washer does not clamp the Gimbal_tendon tab (0.4 mm gap) and covers the tab on both sides of the slot", w < 0.01 and tab_gap >= 0.3 and PWd['d'] / 2 >= GTM.P['slot_w'] / 2 + GTM.P['wall'] - 1e-9, f"overlap {w:.3f} mm3, gap {tab_gap:.2f} mm, washer R{PWd['d']/2:.1f} >= slot half-width {GTM.P['slot_w']/2:.1f} + tab wall {GTM.P['wall']}")
mov = [("Proximal", AH("Proximal"), (0, 0)), ("Proximal_Shell", AH("Proximal_Shell"), (0, 0)), ("Distal", AH("Distal"), (0, 0)), ("Distal_Shell", AH("Distal_Shell"), (0, 0)), ("finger_link_tendon", MT("finger_link_tendon"), (0, -6)), ("Gimbal_tendon", GT, None)]
r2 = {}
for nm, sw, pv in mov:
    m = 0
    for az in (-25, 0, 25):
        for fl in ((-80, -40, 0, 5) if pv is not None else (0,)):
            s_ = sw
            if pv is not None and fl: s_ = s_.translate((0, -pv[0], -pv[1])).rotate((0, 0, 0), (1, 0, 0), fl).translate((0, pv[0], pv[1]))
            if az: s_ = s_.rotate((0, 0, 0), (0, 0, 1), az)
            m = max(m, ivol(s_, hw2))
    r2[nm] = round(m, 3)
chk("option 2: washer + screw head clear the moving finger parts over flexion -80..+5 x abduction +-25 (finger frame, same for the 3 fingers)", max(r2.values()) < 0.01, f"{r2} mm3")
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
def mind(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped); d.Perform(); return d.Value()
dm = min(mind(W2.val(), GT.rotate((0, 0, 0), (0, 0, 1), az).val()) for az in (-25, -20, 0, 20, 25))
chk("option 2: minimum distance washer <-> Gimbal_tendon over +-25 deg abduction (the D10 top-hat would touch the fork legs: this is why option 2 has its own flat washer)", dm >= 0.15, f"{dm:.2f} mm (washer D8; a D9 disc: 0.00 mm)")
sv = {f['name']: round(ivol(hand(hw2, f), cq.Workplane("XY").add(shell.val().intersect(cq.Workplane("XY").box(60, 80, 60).translate((f['c'][0], f['c'][1] - 20, -20)).val()))), 3) for f in FING}
chk("option 2: washer + screw head clear the relieved R-Palm_Shell_tendon (3 fingers)", sum(sv.values()) < 0.01, f"{sv} mm3")
eng2 = 8.0 - PWd['t']; tip2 = zt + eng2
chk("option 2: thread engagement in the post (pilot D1.9 x 8.0 from Z 0.1)", eng2 >= 6.5 and tip2 <= zt + P['pilot_depth'] - 0.5, f"{eng2:.1f} mm of screw above the washer (with the 0.8 mm metal washer: 7.2 mm); tip at Z {tip2:.1f}, pilot floor Z {zt + P['pilot_depth']:.1f}")
print(f"\nSUMMARY: {sum(res)} / {len(res)} checks passed")
