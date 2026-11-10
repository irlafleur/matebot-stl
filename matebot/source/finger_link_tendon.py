# Usage: python finger_link_tendon.py "/path/to/Amazing Hand Parts - Link.step"   (needs CadQuery)
# MateBot v0 (UNTESTED): tendon-driven Amazing Hand Link ("finger_link_tendon")
# Original Link (Pollen Robotics, CC BY 4.0) + two capstan plates joined by a cross bar.
# Frame = Pollen finger frame: X lateral, Y along finger (palm -> tip), Z up (back of finger). Flexion = tip towards -Z.
import cadquery as cq, math, json, sys
from OCP.BRepAdaptor import BRepAdaptor_Surface
import os
# Pollen original: AmazingHand/cad/step/"Amazing Hand Parts - Link.step" (CC BY 4.0). Pass a path or set MATEBOT_LINK_STEP.
SRC=sys.argv[1] if len(sys.argv)>1 else os.environ.get("MATEBOT_LINK_STEP","Amazing Hand Parts - Link.step")
G2=(0.0,-6.0)             # Link pivot (Y,Z)
BAR_C=(3.6,-11.1)         # original cross barrel centre (Y,Z)
P=dict(
  x_in=12.0, t=2.4,       # plate x range: 12.0 .. 14.4 (Proximal_Shell is +-11.9 wide)
  R_out=9.0,              # rim radius
  groove_w=1.4, groove_d=1.2,   # U groove, tendon centre radius ~8.3
  bar_r=3.0,
  pocket_d=3.2, pocket_depth=2.0, pocket_r=5.2,  # knot / crimp pocket
  psi_flex=-15.0, psi_ext=35.0,      # pocket angles on plate (deg, 0 = +Y, 90 = +Z)
  cut_from=175.0, cut_to=250.0,      # removed wedge (lower back) - tendons never wrap there
  chan_d=1.2, bend_r=3.0,
)
def pol(r,psi): a=math.radians(psi); return (G2[0]+r*math.cos(a), G2[1]+r*math.sin(a))  # (Y,Z)
def build(p=P, bar_r=None):
    bar_r=bar_r or p['bar_r']
    link=cq.importers.importStep(SRC)
    x0=p['x_in']; x1=x0+p['t']; xm=(x0+x1)/2
    def plate_side(sign):
        disc=cq.Workplane("YZ").workplane(offset=x0).center(*G2).circle(p['R_out']).extrude(p['t'])
        # remove wedge
        pts=[G2]+[pol(30,a) for a in (p['cut_from'],212,p['cut_to'])]
        wedge=cq.Workplane("YZ").workplane(offset=x0-1).polyline(pts).close().extrude(p['t']+2)
        disc=disc.cut(wedge)
        # groove
        ring=(cq.Workplane("YZ").workplane(offset=xm-p['groove_w']/2).center(*G2)
              .circle(p['R_out']+1).circle(p['R_out']-p['groove_d']).extrude(p['groove_w']))
        disc=disc.cut(ring)
        rb=p['R_out']-p['groove_d']  # groove bottom radius
        rb=p['R_out']-p['groove_d']; rc=rb+0.5      # tendon centre radius in groove (~8.3)
        info={}
        for psi,sgn in ((p['psi_flex'],-1),(p['psi_ext'],+1)):
            py,pz=pol(p['pocket_r'],psi)
            pocket=(cq.Workplane("YZ").workplane(offset=x1-p['pocket_depth']).center(py,pz)
                    .circle(p['pocket_d']/2).extrude(p['pocket_depth']+1))
            disc=disc.cut(pocket)
            # curved tendon channel: arc of radius rho tangent (inside) to the groove circle at Q, ending at pocket centre P.
            rho=p['bend_r']
            # centre of bend circle C = rc-rho from G2 at angle psiQ ; need |P-C|=rho
            rp=p['pocket_r']; rcc=rc-rho
            cosd=(rp**2+rcc**2-rho**2)/(2*rp*rcc); dpsi=math.degrees(math.acos(cosd))
            psiQ=psi+sgn*(-dpsi) if False else psi-sgn*dpsi*(-1)  # placeholder, fixed below
            psiQ=psi+sgn*dpsi
            Q=pol(rc,psiQ); C=pol(rcc,psiQ)
            # arc from Q to P around C (short way)
            aQ=math.atan2(Q[1]-C[1],Q[0]-C[0]); aP=math.atan2(pz-C[1],py-C[0])
            da=(aP-aQ+math.pi)%(2*math.pi)-math.pi
            aM=aQ+da/2; M=(C[0]+rho*math.cos(aM),C[1]+rho*math.sin(aM))
            V=lambda y,z: cq.Vector(xm,y,z)
            edge=cq.Edge.makeThreePointArc(V(*Q),V(*M),V(py,pz))
            # tangent at Q is perpendicular to (Q-C); direction of travel along the arc
            tv=(-(Q[1]-C[1]),(Q[0]-C[0])); 
            if da<0: tv=(-tv[0],-tv[1])
            n=math.hypot(*tv); tv=cq.Vector(0,tv[0]/n,tv[1]/n)
            plane=cq.Plane(origin=V(*Q),xDir=cq.Vector(1,0,0),normal=tv)
            tube=cq.Workplane(plane).circle(p['chan_d']/2).sweep(cq.Workplane("XY").add(cq.Wire.assembleEdges([edge])))
            disc=disc.cut(tube)
            # short straight lead-in so the tube opens cleanly into the groove (extend back 1.5 mm along -tangent)
            lead=cq.Solid.makeCylinder(p['chan_d']/2,1.5,V(*Q),-tv)
            disc=disc.cut(cq.Workplane("XY").add(lead))
            info[str(psi)]=dict(Q_psi=round(psiQ,1),bend_r=rho,arc_deg=round(math.degrees(abs(da)),1))
        p['_info']=info
        if sign<0: disc=disc.mirror("YZ")
        return disc
    bar=cq.Workplane("YZ").workplane(offset=-(x0+0.3)).center(*BAR_C).circle(bar_r).extrude(2*(x0+0.3))
    out=link.union(bar).union(plate_side(+1)).union(plate_side(-1))
    return out,link
if __name__=="__main__":
    new,orig=build()
    bb=new.val().BoundingBox()
    print("bbox",round(bb.xmin,2),round(bb.xmax,2),round(bb.ymin,2),round(bb.ymax,2),round(bb.zmin,2),round(bb.zmax,2))
    print("solids",len(new.solids().vals()),"vol",round(new.val().Volume(),1),"orig vol",round(orig.val().Volume(),1))
    print(P.get('_info'))
    cq.exporters.export(new,"finger_link_tendon.step"); cq.exporters.export(new,"finger_link_tendon.stl",tolerance=0.01,angularTolerance=0.1)
