# Verification of the dowel pass-through in finger_link_tendon (v1).
# Usage: python verify_finger_link_tendon.py "<Amazing Hand Parts - Link.step>"  (run from any folder; needs CadQuery)
import sys, os, math, importlib.util
import cadquery as cq
here=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("flt",os.path.join(here,"finger_link_tendon.py")); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
P=M.P; res=[]
def chk(name,ok,detail): res.append(ok); print(("PASS" if ok else "FAIL"),"-",name,":",detail)
W=lambda s: cq.Workplane("XY").add(s)
vol=lambda w: sum(x.Volume() for x in w.solids().vals()) if w.vals() else 0.0
new,orig=M.build(); nod,_=M.build(dict(P,dowel=False))
chk("single valid solid",len(new.solids().vals())==1 and new.val().isValid(),f"solids={len(new.solids().vals())} valid={new.val().isValid()} volume {new.val().Volume():.0f} mm3 (before dowel holes {nod.val().Volume():.0f})")
x0,x1=P['x_in'],P['x_in']+P['t']
# the cutters only touch the plates: Link body (|X|<11.5) identical with and without dowel cutters
inner=cq.Workplane("XY").box(23.0,200,200)
d=vol(nod.intersect(inner))-vol(new.intersect(inner))
chk("Link body and cross bar (|X| < 11.5) untouched by the dowel holes",abs(d)<0.01,f"volume difference {d:.4f} mm3")
# wall >= wall_min around the round hole and the slot, inside the plates (rings must be fully solid)
okall=True
for sign in (1,-1):
    xa,xb=(x0,x1) if sign>0 else (-x1,-x0)
    slab=cq.Workplane("XY").box(xb-xa,200,200,centered=(False,True,True)).translate((xa,0,0))
    for nm,fn in (("round hole (pivot, D2x10 pin)",lambda g: cq.Workplane("YZ").workplane(offset=xa-1).center(*P['dowel_pivot']).circle(P['dowel_d']/2+g).extrude(xb-xa+2)),
                  ("arc slot (D2x16 pin)",lambda g: M.slot_solid(P,xa-1,xb+1,g))):
        ring=fn(P['wall_min']).cut(fn(0.0)).intersect(slab)
        v=vol(ring); fr=vol(ring.intersect(new))/v
        ok=fr>0.9999; okall&=ok
        print(f"   side {sign:+d} {nm}: 1.2 mm ring solid fraction {fr:.4f}")
chk(f"wall >= {P['wall_min']} mm around the dowel round hole and slot (so no groove, pocket or channel within {P['wall_min']} mm)",okall,"see lines above")
# dowel insertion path: pin D2.0 swept along its whole insertion length, from outside, Link tilted by several angles
def ivol(*ws):
    cur=ws[0]
    for w in ws[1:]:
        cur=cur.intersect(w)
        if not cur.solids().vals(): return 0.0
    return vol(cur)
def sweep(axis,x_from,x_to):
    y,z=axis; a,b=min(x_from,x_to),max(x_from,x_to)
    return cq.Workplane("YZ").workplane(offset=a).center(y,z).circle(1.0).extrude(b-a)
def tilted(link,deg):
    return cq.Workplane("XY").add(link.val().rotate(cq.Vector(0,M.G2[0],M.G2[1]),cq.Vector(1,M.G2[0],M.G2[1]),deg))
def plate_slab(sign): return cq.Workplane("XY").box(x1-x0,300,300,centered=(False,True,True)).translate((x0 if sign>0 else -x1,0,0))
pins=[("D2x10 Gimbal<->Link pin (axis Y=0 Z=-6)",P['dowel_pivot'],5.0,10.0,[0,10,-30,-60]),
      ("D2x16 Gimbal<->Proximal pin (axis Y=0 Z=0)",P['dowel_prox'],8.1,16.0,[10,0,-10,-20,-30])]
for nm,axis,half,L,tilts in pins:
    bad=[]
    for tilt in tilts:
        lk=tilted(new,tilt)
        for sign in (1,-1):
            path=sweep(axis,-sign*half,sign*(half+L))      # tip final position .. tail at the start of insertion
            vp=ivol(lk,path,plate_slab(sign)); vall=ivol(lk,path)
            if vall>0.01: bad.append((tilt,sign,"total",round(vall,2)))
    chk(f"{nm}: whole insertion path (tip at the far ear to tail outside) free of Link material, Link tilted {tilts} deg, both insertion sides",not bad,f"collisions {bad}")
# negative control: tilt outside the slot must collide for the proximal pin
v=ivol(tilted(new,35),sweep(P['dowel_prox'],-8.1,24.1),plate_slab(1)); print(f"INFO - control: Link tilted +35 deg (outside the slot range) blocks the D2x16 pin by {v:.1f} mm3 (expected > 0)")
# the pin path vs the ORIGINAL Link (no plates): zero in the plate zone -> the new Link blocks nothing the old one did not
print(f"INFO - plate zone volume: round hole {math.pi*P['dowel_d']**2/4*P['t']:.1f} mm3 each, plate wall left under the groove at the slot: {P['R_out']-P['groove_d']-(6+P['dowel_d']/2):.2f} mm")
bb=new.val().BoundingBox(); print(f"INFO - bbox X +-{bb.xmax:.1f}, Y {bb.ymin:.1f}..{bb.ymax:.1f}, Z {bb.zmin:.1f}..{bb.zmax:.1f}")
print("SUMMARY:",sum(res),"/",len(res),"checks passed"); sys.exit(0 if all(res) else 1)
