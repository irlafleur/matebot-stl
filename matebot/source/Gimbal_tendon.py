# Usage: python Gimbal_tendon.py "/path/to/Amazing Hand Parts - Gimbal.step"   (needs CadQuery; writes Gimbal_tendon.step/.stl in the current folder)
# MateBot v1 (UNTESTED): Amazing Hand Gimbal + a rear TAB with an arc slot, so the finger can be held from UNDERNEATH the hand plate.
# Original Gimbal: Pollen Robotics, CC BY 4.0.  Added geometry: MateBot, CC BY 4.0.
#
# Why: with Finger_Frame-1 merged into R-Hand_Plate_tendon, the Gimbal boss (D6, Z 3.5..13.5) turns in the plate's D8.15 bore (two bushing_d6_flanged).
# Pollen holds the Gimbal in with a 2.5x8 screw + large M2.5 washer on TOP of the boss (back of the hand).  A screw coaxial from underneath is impossible: the
# Gimbal is solid at Z=0 around the axis and the D2x16 Proximal pin crosses it.  So the screw + washer move to the underside:
#   * the plate has a D4.4 post at (X=0, Y=-8.6) hanging down to Z=0.1 (0.4 mm below the tab, so the washer never clamps the tab) with a D1.9 pilot hole (R-Hand_Plate_tendon.py);
#   * this Gimbal has a tab (Z 0.5..3.5, behind the shoulder) with a D5.0 ARC slot of 50 degrees around the boss axis; the post passes through the slot;
#   * the large M2.5 washer (D8) + 2.5x8 thermoplastic screw go up from below through the washer into the post: the washer overlaps the tab around the slot,
#     so the Gimbal cannot drop out, and it can still turn +-25 degrees (abduction) because the post slides in the slot.
# Frame: Pollen assembly frame, finger frame (X lateral, Y toward the fingertip, Z toward the back of the hand); boss axis = Z through (0,0).
import cadquery as cq, math, os, sys
SRC=sys.argv[1] if len(sys.argv)>1 else os.environ.get("MATEBOT_GIMBAL_STEP","Amazing Hand Parts - Gimbal.step")
P=dict(
  R_s=8.6,            # slot centre radius from the boss axis
  slot_w=5.0,         # slot width (post D4.4 + 0.6)
  wall=1.5,           # tab wall around the slot
  abd=25.0,           # post travel, +- degrees of abduction
  z0=0.5, z1=3.5,     # tab Z range = the shoulder (underside 0.5, top 3.5, touches the lower bushing flange for r < 6 and leaves 1.0 mm to the block outside it)
  y_clip=-3.7,        # the tab stays behind this Y (the Proximal rear lip reaches Y=-3.3)
)
def sector(r0,r1,z0,z1,half_deg):
    """annular sector r0..r1, Z z0..z1, centred on the -Y axis, +-half_deg"""
    s=cq.Workplane("XZ").center((r0+r1)/2,(z0+z1)/2).rect(r1-r0,z1-z0).revolve(2*half_deg,(-(r0+r1)/2,-(z0+z1)/2,0),(-(r0+r1)/2,1-(z0+z1)/2,0))
    return s.rotate((0,0,0),(0,0,1),-90-half_deg)
def cap(R,deg,r,z0,z1):
    a=math.radians(-90+deg); return cq.Workplane("XY").workplane(offset=z0).center(R*math.cos(a),R*math.sin(a)).circle(r).extrude(z1-z0)
def tab_solid(p=P,grow=0.0):
    h=p['slot_w']/2+p['wall']+grow
    t=sector(p['R_s']-h,p['R_s']+h,p['z0'],p['z1'],p['abd']).union(cap(p['R_s'],p['abd'],h,p['z0'],p['z1'])).union(cap(p['R_s'],-p['abd'],h,p['z0'],p['z1']))
    clip=cq.Workplane("XY").box(60,60,10,centered=(True,False,False)).translate((0,-60+p['y_clip'],p['z0']-1))   # Y <= y_clip
    return t.intersect(clip)
def slot_solid(p=P,grow=0.0):
    h=p['slot_w']/2+grow
    return sector(p['R_s']-h,p['R_s']+h,p['z0']-1,p['z1']+1,p['abd']).union(cap(p['R_s'],p['abd'],h,p['z0']-1,p['z1']+1)).union(cap(p['R_s'],-p['abd'],h,p['z0']-1,p['z1']+1))
def build(p=P):
    g=cq.importers.importStep(SRC)
    new=g.union(tab_solid(p)).cut(slot_solid(p))
    return new,g
if __name__=="__main__":
    new,orig=build(); bb=new.val().BoundingBox()
    print("bbox",*(round(v,2) for v in (bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax)),"solids",len(new.solids().vals()),"valid",new.val().isValid(),"vol",round(new.val().Volume(),1),"orig",round(orig.val().Volume(),1))
    cq.exporters.export(new,"Gimbal_tendon.step"); cq.exporters.export(new,"Gimbal_tendon.stl",tolerance=0.01,angularTolerance=0.1)
