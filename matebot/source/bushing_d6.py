# MateBot bushing_d6: printable flanged bushing for the abduction pivot of an Amazing Hand finger.
#
# Pollen Robotics' bill of materials calls it "Bushing D interior 6 mm / D exterior 8 mm, GFM 0608-04"
# (an igus iglidur GFM-0608-04 flanged plastic bush: 6 bore, 8 OD, 4 long including the flange, flange 12 x 1).
# 2 per finger are pressed into the two sides of Finger_Frame-1; the Gimbal's D6 boss turns in them
# (finger abduction / adduction).  This is a PETG equivalent to print.
#
# Frame: axis = +Z, flange from Z = 0 to flange_t (its top face, Z = flange_t, is the one that touches Finger_Frame-1), body Z = flange_t .. length.  Origin on the axis.
# Usage:  python bushing_d6.py [out_dir]       writes bushing_d6_flanged.step/.stl (CadQuery)
import sys, os, cadquery as cq

P = dict(
    bore      = 6.20,   # Gimbal boss is D6.0 (CAD).  igus bore is 6.02..6.07; printed PETG bore comes out ~0.1 smaller than drawn -> 6.2 drawn
    od        = 8.10,   # body OD.  Finger_Frame-1 bore is D8.14 (CAD, with 0.3 chamfers).  Printed holes run small -> light press fit.  igus: D8.0
    length    = 4.00,   # total length including the flange (igus b1)
    flange_d  = 12.0,   # igus d3.  Equal to the R6.0 outer arc of the Frame-1 and the D11.9 Gimbal shoulder
    flange_t  = 1.00,   # igus b2.  The Gimbal boss sticks out of the frame by exactly 1.0 on both sides (Z 3.5 / 13.5 vs frame 4.5..12.5)
    lead_in   = 0.25,   # outer chamfer at the body tip (press-in lead)
    bore_ch   = 0.20,   # bore chamfer, flange side (hides elephant foot on the bed side) and tip side
)

def build(p=P):
    L, ft = p['length'], p['flange_t']
    # revolve profile in (r, z)
    r_b, r_o, r_f = p['bore']/2, p['od']/2, p['flange_d']/2
    li, bc = p['lead_in'], p['bore_ch']
    pts = [(r_b+bc, 0), (r_f, 0), (r_f, ft), (r_o, ft), (r_o, L-li), (r_o-li, L), (r_b+bc, L), (r_b, L-bc), (r_b, bc)]
    s = cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
    return s

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    s = build(); b = s.val().BoundingBox()
    print("volume %.1f mm3  bbox %.2f x %.2f x %.2f  valid=%s solids=%d" % (s.val().Volume(), b.xlen, b.ylen, b.zlen, s.val().isValid(), s.solids().size()))
    cq.exporters.export(s, os.path.join(out, "step", "bushing_d6_flanged.step"))
    cq.exporters.export(s, os.path.join(out, "stl", "bushing_d6_flanged.stl"), tolerance=0.01, angularTolerance=0.1)
