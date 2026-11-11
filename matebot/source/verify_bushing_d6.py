# Verification of bushing_d6 (printable flanged D6 bushing of the finger abduction pivot).
# Usage: python verify_bushing_d6.py "<folder with the original 'Amazing Hand Parts - *.step'>"   (or set $MATEBOT_AH_STEP_DIR)
# Needs CadQuery.  The MateBot STEP files (finger_link_tendon, R-Hand_Plate_tendon, R-Palm_Shell_tendon) are read from ../step.
import sys, os, math, importlib.util
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
here = os.path.dirname(os.path.abspath(__file__)); mstep = os.path.join(here, "..", "step")
ah = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MATEBOT_AH_STEP_DIR", "/workspace/ah-enh/cad/step")
spec = importlib.util.spec_from_file_location("b", os.path.join(here, "bushing_d6.py")); B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
P = B.P; res = []
def chk(name, ok, detail): res.append(ok); print(("PASS" if ok else "FAIL"), "-", name, ":", detail)
vol = lambda w: sum(x.Volume() for x in w.solids().vals()) if w.vals() else 0.0
def ivol(a, b):
    r = a.intersect(b); return vol(r) if r.solids().vals() else 0.0
def load(n, own=False): return cq.importers.importStep(os.path.join(mstep, n + ".step") if own else os.path.join(ah, "Amazing Hand Parts - %s.step" % n))
def cyl(shape, axis, rmax=7.0):
    out = []
    for f in shape.faces().vals():
        a = BRepAdaptor_Surface(f.wrapped)
        if a.GetType() != GeomAbs_Cylinder: continue
        c = a.Cylinder(); d = c.Axis().Direction()
        if abs(abs((d.X(), d.Y(), d.Z())[axis]) - 1) > 1e-6 or c.Radius() > rmax: continue
        fb = f.BoundingBox(); out.append((c.Radius(), fb.zmin, fb.zmax, fb.xmin, fb.xmax, fb.ymin, fb.ymax))
    return out

b = B.build(); bb = b.val().BoundingBox()
chk("single valid solid, bbox", len(b.solids().vals()) == 1 and b.val().isValid() and abs(bb.zlen - P['length']) < 1e-6 and abs(bb.xlen - P['flange_d']) < 1e-6,
    "solids=%d valid=%s bbox %.2f x %.2f x %.2f, volume %.1f mm3" % (len(b.solids().vals()), b.val().isValid(), bb.xlen, bb.ylen, bb.zlen, b.val().Volume()))

# -- geometry facts read from the original CAD
F1 = load("Finger_Frame-1"); G = load("Gimbal")
bore = [c for c in cyl(F1, 2) if c[0] > 3.5 and c[0] < 4.5 and abs(c[3] + c[0]) < 0.1]
frame_r = max(c[0] for c in bore); fz0 = F1.val().BoundingBox().zmin; fz1 = F1.val().BoundingBox().zmax
boss = [c for c in cyl(G, 2) if abs(c[0] - 3.0) < 0.05 and c[2] - c[1] > 5]
boss_r = boss[0][0]; bz0 = boss[0][1]; bz1 = boss[0][2]
print("   Finger_Frame-1: bore R%.3f (D%.2f), Z %.2f..%.2f (%.2f long);  Gimbal boss R%.2f (D%.1f), Z %.1f..%.1f" % (frame_r, 2 * frame_r, fz0, fz1, fz1 - fz0, boss_r, 2 * boss_r, bz0, bz1))
flange_out = (fz0 - bz0, bz1 - fz1)
chk("Gimbal boss sticks out of the frame by the flange thickness on both sides", all(abs(x - P['flange_t']) < 0.01 for x in flange_out), "protrusion %.2f / %.2f mm, flange_t %.2f" % (flange_out + (P['flange_t'],)))
body_len = P['length'] - P['flange_t']
chk("two bodies fit in the bore length without touching each other", 2 * body_len <= fz1 - fz0, "2 x %.1f = %.1f of %.1f mm (gap %.1f)" % (body_len, 2 * body_len, fz1 - fz0, fz1 - fz0 - 2 * body_len))
chk("OD clearance in the Frame-1 bore (CAD) and bore clearance on the Gimbal boss", P['od'] / 2 <= frame_r + 1e-6 and P['bore'] / 2 > boss_r,
    "OD D%.2f in D%.2f bore (diametral %+.2f); bore D%.2f on D%.1f boss (diametral %+.2f)" % (P['od'], 2 * frame_r, 2 * frame_r - P['od'], P['bore'], 2 * boss_r, P['bore'] - 2 * boss_r))

# -- walls
rb, ro, rf = P['bore'] / 2, P['od'] / 2, P['flange_d'] / 2
cyls = cyl(b, 2, 7.0); radii = sorted(set(round(c[0], 3) for c in cyls))
wall_body = ro - rb
chk("wall >= 0.8 mm (body), flange thickness >= 0.8 mm", wall_body >= 0.8 and P['flange_t'] >= 0.8 and rf - ro >= 0.8,
    "body wall %.2f, flange thickness %.2f, flange overhang %.2f; cylinder radii in the CAD: %s (tip flat after chamfers: %.2f)" % (wall_body, P['flange_t'], rf - ro, radii, wall_body - P['lead_in'] - P['bore_ch']))

# -- place the pair as assembled: low bushing flange Z 3.5..4.5 body inside the frame, high bushing flipped
low = b.translate((0, 0, fz0 - P['flange_t']))
high = b.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, fz1 + P['flange_t']))
pair = low.union(high)
chk("pair placed in the frame: no overlap between the two bushings", ivol(low, high) < 1e-6, "overlap %.4f mm3" % ivol(low, high))
# Press fit is real at the printed size; interference with the CAD bore only if OD > bore:
chk("pair vs Finger_Frame-1 (CAD bore)", ivol(pair, F1) < 0.01, "interference %.4f mm3" % ivol(pair, F1))
chk("pair vs Gimbal at abduction -30, 0, +30 deg (rotation about the boss axis)", all(ivol(pair, G.rotate((0, 0, 0), (0, 0, 1), a)) < 0.01 for a in (-30, 0, 30)),
    "interference " + ", ".join("%.4f" % ivol(pair, G.rotate((0, 0, 0), (0, 0, 1), a)) for a in (-30, 0, 30)) + " mm3")

# washer contact: M2.5 large washer (D8) sits on the outer flange face, centred on the screw axis
washer = cq.Workplane("XY").workplane(offset=fz1 + P['flange_t']).circle(4.0).circle(1.4).extrude(0.8)
chk("M2.5 large washer (D8) rests on the outer flange face, not on the Gimbal boss alone", abs(bz1 - (fz1 + P['flange_t'])) < 0.01 and ivol(washer, pair) < 1e-6,
    "boss end Z %.2f = flange face Z %.2f" % (bz1, fz1 + P['flange_t']))

# -- neighbours: static (index finger position) and swept
static = ["Finger_Frame-2", "Proximal", "Proximal_Shell", "Distal", "Distal_Shell", "R-Hand_Plate"]
worst = 0.0; lines = []
for n in static:
    v = ivol(pair, load(n)); worst = max(worst, v); lines.append("%s %.3f" % (n, v))
for n in ("R-Hand_Plate_tendon", "R-Palm_Shell_tendon", "finger_link_tendon"):
    v = ivol(pair, load(n, True)); worst = max(worst, v); lines.append("%s %.3f" % (n, v))
chk("pair vs every neighbouring part, rest pose (index finger position)", worst < 0.01, "; ".join(lines) + " mm3")
sw = {}
angles = list(range(-80, 1, 5))
mov = {"Proximal": (load("Proximal"), (0, 0)), "Proximal_Shell": (load("Proximal_Shell"), (0, 0)), "Distal": (load("Distal"), (0, 0)), "Distal_Shell": (load("Distal_Shell"), (0, 0)),
       "finger_link_tendon": (load("finger_link_tendon", True), (0, -6))}
def rot(s, y, z, a): return s.translate((0, -y, -z)).rotate((0, 0, 0), (1, 0, 0), a).translate((0, y, z))   # rotation about the X axis through (Y,Z) = (y,z)
for n, (s, (y, z)) in mov.items():
    sw[n] = max(ivol(pair, rot(s, y, z, a)) for a in angles)
chk("pair vs the moving finger parts swept over the flexion range -80..0 deg (straight finger), about the Gimbal/Link pivots", max(sw.values()) < 0.01, ", ".join("%s %.3f" % kv for kv in sw.items()) + " mm3")
# hyper-extension: where does the pair first touch, compared with the hard stop of the original frame
def first(a_shape, y, z, others, hi=15):
    for a in range(1, hi + 1):
        if any(ivol(o, rot(a_shape, y, z, a)) > 0.001 for o in others): return a
    return None
f_b = first(load("Proximal"), 0, 0, [pair]); f_s = first(load("Proximal_Shell"), 0, 0, [pair]); f_f = first(load("Proximal"), 0, 0, [F1])
print("   INFO hyper-extension (Proximal turned past the straight pose, about X at the Gimbal pivot): first contact with the flanges: Proximal +%s deg, Proximal_Shell +%s deg; the original Finger_Frame-1 itself stops the Proximal at +%s deg (no bushing involved)" % (f_b, f_s, f_f))
chk("bushing flanges do not reduce the free extension below +3 deg beyond straight", (f_b is None or f_b >= 3) and (f_s is None or f_s >= 3), "first contact +%s / +%s deg" % (f_b, f_s))
print("SUMMARY: %d / %d checks passed" % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
