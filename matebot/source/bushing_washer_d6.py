# MateBot bushing_washer_d6: printable "top-hat" part = washer + bushing sleeve in one piece.  It replaces BOTH the large M2.5 washer and the upper
# bushing_d6_flanged of a finger, so no bought washer is needed (v8).
#
# OPTION 1 (stock Gimbal, Pollen's screw from the top into the Gimbal's end hole, D1.9 blind): the part sits on the Gimbal's boss end.  The 2.5x8 screw clamps
#   it onto the boss end, so it TURNS WITH THE GIMBAL; its sleeve (OD 7.95, slip fit) turns in the plate's D8.15 bore like the bushing it replaces, and its disc
#   (D10) sits in the plate cavity (Z 12.5..14.5) under the ceiling hole.  The lower bushing (bushing_d6_flanged) stays.
# OPTION 2 (Gimbal_tendon, screw from below into the plate post): this top-hat does NOT fit there, the washer under the post has to stay <= D8.4
#   (at +-25 deg abduction the Gimbal's fork legs sweep to 4.3 mm from the post axis at Z 0.1) while the top-hat disc must be >= D9 to stop the Gimbal in the D8.15 bore.
#   So option 2 uses the flat printed washer D8 x 0.9 defined below (washer_d8_printed), together with the standard upper bushing_d6_flanged.
#
# Frame of bushing_washer_d6 (print orientation): axis +Z, disc from Z = 0 (bed) to disc_t, sleeve from disc_t up to disc_t+sleeve_len.  The face at Z = disc_t inside the sleeve
# (between the screw hole and the bore) is the contact face on the Gimbal boss end.  Usage:  python bushing_washer_d6.py [out_dir]
import sys, os, cadquery as cq

P = dict(
    hole      = 2.70,   # screw clearance for a 2.5 mm thermoplastic screw (printed holes run ~0.1 small)
    bore      = 6.20,   # Gimbal boss is D6.0 (CAD); same as bushing_d6
    od        = 7.95,   # sleeve OD: SLIP fit in the plate's D8.15 bore (the part turns with the Gimbal), bushing_d6 is D8.10 press fit
    disc_d    = 10.0,   # disc: bigger than the D8.15 bore (it stops the Gimbal falling out), smaller than the R6.25 cavity (Z 12.5..14.5); the ceiling hole is ~D6.9
    disc_t    = 0.90,   # the cavity above the boss end (Z 13.5) is 1.0 mm high (ceiling underside Z 14.5): 0.1 mm left
    sleeve_len= 3.50,   # 2.5 mm of it enters the bore (bore top Z 12.5), the end stays 2.5 mm above the lower bushing
    lead_in   = 0.25,   # chamfer at the sleeve tip
    bore_ch   = 0.20,   # chamfer inside the bore at the tip
    hole_ch   = 0.30,   # chamfer on the screw hole, bed side (elephant foot) -> hides in the countersink-free side
)

def build(p=P):
    t, L = p['disc_t'], p['sleeve_len']
    r_h, r_b, r_o, r_d = p['hole']/2, p['bore']/2, p['od']/2, p['disc_d']/2
    li, bc, hc = p['lead_in'], p['bore_ch'], p['hole_ch']
    pts = [(r_h+hc, 0), (r_d-0.2, 0), (r_d, 0.2), (r_d, t), (r_o, t), (r_o, t+L-li), (r_o-li, t+L), (r_b+bc, t+L), (r_b, t+L-bc), (r_b, t), (r_h, t), (r_h, hc)]
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))

PW = dict(d=8.0, t=0.9, hole=2.7, hole_ch=0.3)       # option 2: flat printed washer (replaces the large M2.5 washer under the post)
def build_washer(p=PW):
    r_h, r_o, t, hc = p['hole']/2, p['d']/2, p['t'], p['hole_ch']
    pts = [(r_h+hc, 0), (r_o-0.2, 0), (r_o, 0.2), (r_o, t), (r_h, t), (r_h, hc)]
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
def place_washer_under(w, x=0.0, y=-8.6, z_post_bottom=0.1):
    """option 2: washer top face against the post bottom (Z = z_post_bottom), washer below it"""
    return w.translate((x, y, z_post_bottom - PW['t']))

def place_top(w, z_boss_top=13.5, p=P):
    """option 1: finger frame, sleeve pointing down (toward -Z), the contact face on the boss end Z = z_boss_top"""
    return w.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, z_boss_top + p['disc_t']))
if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    s = build(); b = s.val().BoundingBox()
    print("volume %.1f mm3  bbox %.2f x %.2f x %.2f  valid=%s solids=%d" % (s.val().Volume(), b.xlen, b.ylen, b.zlen, s.val().isValid(), s.solids().size()))
    cq.exporters.export(s, os.path.join(out, "step", "bushing_washer_d6.step"))
    cq.exporters.export(s, os.path.join(out, "stl", "bushing_washer_d6.stl"), tolerance=0.01, angularTolerance=0.1)
    w = build_washer(); print("washer volume %.1f mm3 valid=%s" % (w.val().Volume(), w.val().isValid()))
    cq.exporters.export(w, os.path.join(out, "step", "washer_d8_printed.step"))
    cq.exporters.export(w, os.path.join(out, "stl", "washer_d8_printed.stl"), tolerance=0.01, angularTolerance=0.1)
