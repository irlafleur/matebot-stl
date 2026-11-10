# Verification of R-Hand_Plate_tendon.  Usage: python verify_R-Hand_Plate_tendon.py <R-Hand_Plate.step> [<Pollen step dir> <finger_link_tendon.step>]
# Every check prints PASS/FAIL with the number behind it.  Nothing here replaces a real print + caliper check.
import sys, os, math, importlib.util
import cadquery as cq, numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
here=os.path.dirname(os.path.abspath(__file__))
sys.argv=[sys.argv[0]]+sys.argv[1:]
spec=importlib.util.spec_from_file_location("rhp",os.path.join(here,"R-Hand_Plate_tendon.py")); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
P=M.P; FING=M.FINGERS
STEPDIR=sys.argv[2] if len(sys.argv)>2 else os.path.dirname(M.SRC)
LINK=sys.argv[3] if len(sys.argv)>3 else os.path.join(here,"..","step","finger_link_tendon.step")
new,orig,info=M.build(); g=info['g']
res=[]
def chk(name,ok,detail): res.append(ok); print(("PASS" if ok else "FAIL"),"-",name,":",detail)
vol=lambda w: sum(s.Volume() for s in w.solids().vals()) if w.vals() else 0.0
def W(shape): return cq.Workplane("XY").add(shape)
# 1 validity
chk("single valid solid",len(new.solids().vals())==1 and new.val().isValid(),f"solids={len(new.solids().vals())} valid={new.val().isValid()}")
# 1b finger placement: the Finger_Frame screw holes of each finger (finger frame (+-6,-7) and (0,-44.5)) must land on the plate's own D2.8 screw holes
holes28=[]
for face in orig.faces().vals():
    ad=BRepAdaptor_Surface(face.wrapped)
    if ad.GetType()==GeomAbs_Cylinder and abs(ad.Cylinder().Radius()*2-2.8)<0.02 and abs(ad.Cylinder().Axis().Direction().Z())>0.99:
        o=ad.Cylinder().Axis().Location(); holes28.append((o.X(),o.Y()))
worst=0
for f in FING:
    t=math.radians(f['th'])
    for (x,y) in ((-6,-7),(6,-7),(0,-44.5)):
        px=f['c'][0]+x*math.cos(t)-y*math.sin(t); py=f['c'][1]+x*math.sin(t)+y*math.cos(t)
        d=min(math.hypot(px-hx,py-hy) for hx,hy in holes28); worst=max(worst,d)
chk("finger frames (3 fingers x 3 screw holes) land on the plate's D2.8 screw holes",worst<0.4,f"worst distance {worst:.2f} mm (fitted finger poses: "+", ".join(f"{f['name']} c={f['c']} rot={f['th']} deg" for f in FING)+")")
# 2 original holes still open: sample the original hole walls (cylinder faces whose normal points to the axis), move 0.1 mm into the void
plugged=0; tested=0; bad=[]
for face in orig.faces().vals():
    a=BRepAdaptor_Surface(face.wrapped)
    if a.GetType()!=GeomAbs_Cylinder: continue
    cyl=a.Cylinder(); ax=cyl.Axis(); o=ax.Location(); d=ax.Direction(); r=cyl.Radius()
    if r>12: continue                                  # outline / big arcs, not holes
    u0,u1,v0,v1=a.FirstUParameter(),a.LastUParameter(),a.FirstVParameter(),a.LastVParameter()
    for i in range(6):
        for j in range(3):
            u=u0+(u1-u0)*(i+0.5)/6; v=v0+(v1-v0)*(j+0.5)/3
            pt=a.Value(u,v); n=face.normalAt(cq.Vector(pt.X(),pt.Y(),pt.Z()))
            # inward normal toward the axis means it is a hole wall
            rad=cq.Vector(pt.X()-o.X(),pt.Y()-o.Y(),pt.Z()-o.Z()); rad=rad-cq.Vector(d.X(),d.Y(),d.Z())*rad.dot(cq.Vector(d.X(),d.Y(),d.Z()))
            if rad.Length<1e-6 or n.dot(rad)>=0: continue
            q=cq.Vector(pt.X(),pt.Y(),pt.Z())-rad.normalized()*0.1
            # only if that point really is a void in the original
            if orig.val().isInside(q,1e-4): continue
            tested+=1
            if new.val().isInside(q,1e-4): plugged+=1; bad.append((round(q.x,1),round(q.y,1),round(q.z,1),round(r*2,1)))
chk("original holes not plugged",plugged==0,f"{tested} wall samples tested, {plugged} inside new material {bad[:6]}")
# 3 wall thickness around every socket (ring of 1.6 mm around the bore, bore length) -- must be fully solid
minwall=1.6; allok=True; worst=1.0
for f in FING:
    L=M.fT(f)
    for s in (-1,1):
        for z in (P['z_ext'],P['z_flex']):
            xs=s*P['x_in']
            for nm,(ya,yb,rin) in dict(bore=(g['y_back'],g['y_stop'],P['sock_d']/2),
                                       tendon_hole=(g['y_stop'],g['y_cone0'],P['tendon_hole_d']/2)).items():
                outer=M.cylY(xs,z,yb,ya,2*(rin+minwall)).moved(L); inner=M.cylY(xs,z,yb,ya,2*rin).moved(L)
                ring=W(outer).cut(W(inner)); v=vol(ring); vi=vol(ring.intersect(new))
                fr=vi/v; worst=min(worst,fr)
                if fr<0.9999: allok=False; print("   ring not solid",f['name'],s,z,nm,round(fr,4))
            # cone: wall measured perpendicular to the cone surface is ~ (outer cylinder of cone_d/2+1.6)
            outer=M.cylY(xs,z,g['y_front'],g['y_cone0'],P['cone_d']+2*minwall).moved(L); inner=M.coneY(xs,z,g['y_cone0'],g['y_front'],P['tendon_hole_d'],P['cone_d']).moved(L)
            ring=W(outer).cut(W(inner)); fr=vol(ring.intersect(new))/vol(ring); worst=min(worst,fr)
            if fr<0.9999: allok=False; print("   ring not solid (cone)",f['name'],s,z,round(fr,4))
chk(f"wall >= {minwall} mm around all 12 sockets (bore, tendon hole, cone)",allok,f"worst solid fraction of the 1.6 mm ring = {worst:.4f}")
# 4 sockets don't touch each other / geometry: min axis distance
axes=[]
for f in FING:
    for s in (-1,1):
        for z in (P['z_ext'],P['z_flex']):
            for y in np.linspace(g['y_back'],g['y_front'],25):
                x,yy=M.fT(f).toTuple()[0][0:2] if False else (None,None)
import itertools
pts={}
for f in FING:
    t=math.radians(f['th'])
    for s in (-1,1):
        for z in (P['z_ext'],P['z_flex']):
            arr=[]
            for y in np.linspace(g['y_back'],g['y_front'],25):
                xf=s*P['x_in']; arr.append((f['c'][0]+xf*math.cos(t)-y*math.sin(t), f['c'][1]+xf*math.sin(t)+y*math.cos(t), z))
            pts[(f['name'],s,z)]=np.array(arr)
mind=1e9; keys=list(pts)
for a,b in itertools.combinations(keys,2):
    d=np.min(np.linalg.norm(pts[a][:,None,:]-pts[b][None,:,:],axis=2)); mind=min(mind,d)
chk("socket axes keep >= bore+1.6 mm walls between them",mind-P['sock_d']>=1.6,f"min axis distance {mind:.2f} mm -> wall {mind-P['sock_d']:.2f} mm")
# 5 tendon lines (rest) vs plate+columns material
bad=[]; 
for ln in info['lines']:
    f=[x for x in FING if x['name']==ln['finger']][0]
    (x0,y0,z0),(x1,y1,z1)=ln['p_exit'],ln['p_cap']
    n=math.hypot(x1-x0,y1-y0)
    tend=cq.Solid.makeCylinder(0.6,n+0.0,cq.Vector(x0,y0,z0),cq.Vector(x1-x0,y1-y0,0)).moved(M.fT(f))   # D1.2 mm tendon incl. margin
    v=vol(W(tend).intersect(new))
    if v>0.01: bad.append((ln['finger'],ln['side'],ln['kind'],round(v,2)))
chk("no tendon line (D1.2, mouth of cone to capstan tangent, finger at rest) touches plate material",not bad,f"{len(info['lines'])} lines, collisions: {bad}")
# 5b the same with a 1.5 mm radius corridor (swing/abduction margin)
bad=[]
for ln in info['lines']:
    f=[x for x in FING if x['name']==ln['finger']][0]
    (x0,y0,z0),(x1,y1,z1)=ln['p_exit'],ln['p_cap']; n=math.hypot(x1-x0,y1-y0)
    tend=cq.Solid.makeCylinder(P['corridor_d']/2,n,cq.Vector(x0,y0,z0),cq.Vector(x1-x0,y1-y0,0)).moved(M.fT(f))
    v=vol(W(tend).intersect(new))
    if v>0.5: bad.append((ln['finger'],ln['side'],ln['kind'],round(v,2)))
chk("tendon corridor D3.0 free of plate material",not bad,f"collisions: {bad}")
# 6 swept Link capstan plates vs new plate
tot=0; badl=[]
for f in FING:
    for s in (-1,1):
        x0=P['plate_x'][0] if s>0 else -P['plate_x'][1]
        cyl=cq.Workplane("YZ").workplane(offset=x0).center(*P['link_pivot']).circle(9.0).extrude(P['plate_x'][1]-P['plate_x'][0]).val().moved(M.fT(f))
        v=vol(W(cyl).intersect(new)); tot+=v
        if v>0.05: badl.append((f['name'],s,round(v,2)))
chk("swept Link capstan plate (R9.0) clears the new plate",tot<0.05,f"overlap {tot:.2f} mm3 {badl}")
# 7 assembly interference: finger parts at rest vs ADDED material only (new - orig)
added=new.cut(orig)
def placed(path,f):
    return cq.importers.importStep(path).val().moved(M.fT(f))
names=["Finger_Frame-1","Finger_Frame-2","Gimbal","Proximal"]
worst=0; report=[]
for f in FING:
    for n in names:
        sh=placed(os.path.join(STEPDIR,f"Amazing Hand Parts - {n}.step"),f)
        v=vol(W(sh).intersect(added)); worst=max(worst,v)
        if v>0.05: report.append((f['name'],n,round(v,2)))
    if os.path.exists(LINK):
        sh=placed(LINK,f); v=vol(W(sh).intersect(new)); worst=max(worst,v)
        if v>0.05: report.append((f['name'],"finger_link_tendon vs plate",round(v,2)))
chk("finger parts (Frame-1, Frame-2, Gimbal, Proximal, tendon Link) clear the added material",not report,f"overlaps: {report}")
# 7b tendon lines (D1.2) vs the finger parts at rest (the tendon runs close to Frame-1/Frame-2/Gimbal)
bad=[]
for ln in info['lines']:
    f=[x for x in FING if x['name']==ln['finger']][0]
    (x0,y0,z0),(x1,y1,z1)=ln['p_exit'],ln['p_cap']; n=math.hypot(x1-x0,y1-y0)
    tend=cq.Solid.makeCylinder(0.6,n,cq.Vector(x0,y0,z0),cq.Vector(x1-x0,y1-y0,0)).moved(M.fT(f))
    for nme in ("Finger_Frame-1","Finger_Frame-2","Gimbal","Proximal"):
        sh=placed(os.path.join(STEPDIR,f"Amazing Hand Parts - {nme}.step"),f)
        v=vol(W(tend).intersect(W(sh)))
        if v>0.01: bad.append((ln['finger'],ln['side'],ln['kind'],nme,round(v,2)))
chk("tendon lines (D1.2) clear Finger_Frame-1/-2, Gimbal and Proximal",not bad,f"collisions {bad}")
# 8 palm shell: the original soft shell is touched by the outer columns, the relieved copy must be clear
orig_shell=cq.importers.importStep(os.path.join(STEPDIR,"Amazing Hand Parts - R-Palm_Shell.step"))
v0=vol(orig_shell.intersect(added)); relieved,nn=M.shell_relieved(info); v1=vol(relieved.intersect(added))
print(f"INFO - added plate material overlapping the ORIGINAL R-Palm_Shell: {v0:.1f} mm3 ({nn} notches needed)")
chk("relieved R-Palm_Shell_tendon clears the added material",v1<0.05,f"overlap {v1:.3f} mm3; shell lost {orig_shell.val().Volume()-relieved.val().Volume():.0f} mm3")
for n in ("R-Top_Shell","R-Wrist_Interface"):
    sh=cq.importers.importStep(os.path.join(STEPDIR,f"Amazing Hand Parts - {n}.step"))
    v=vol(sh.intersect(added)); chk(f"added material clears {n}",v<0.05,f"{v:.2f} mm3")
# 9 does each column fuse with the original plate (volume of overlap)
for i,c in enumerate(info['columns']):
    v=vol(W(c).intersect(orig)); 
    f=FING[i//2]; print("INFO - column",f['name'],"side","-+"[i%2],"overlap with original plate",round(v,1),"mm3")
    res.append(v>50)
# 10 tube lines (D4.0) from the tube end back to the wrist plane: report where they touch the plate/wrist
bad=[]
for f in FING:
    for s in (-1,1):
        for z in (P['z_ext'],P['z_flex']):
            t=M.cylY(s*P['x_in'],z,g['y_back'],-86.0,P['tube_od']).moved(M.fT(f))
            v=vol(W(t).intersect(new))
            if v>0.05: bad.append((f['name'],s,z,round(v,1)))
chk("straight D4.0 tube paths from the sockets back to Y=-86 are free of plate material",not bad,f"collisions {bad}")
# 11 INFO only: thin slivers left beside the tube clearance holes where they cut through the original pockets (coarse sampling)
S=orig.val(); worst=9; loc=None
for f in FING:
    t=math.radians(f['th'])
    P3=lambda x,y,z: cq.Vector(f['c'][0]+x*math.cos(t)-y*math.sin(t), f['c'][1]+x*math.sin(t)+y*math.cos(t), z)
    for s_ in (-1,1):
        xs=s_*P['x_in']; z=P['z_ext']
        for y in np.arange(g['y_back']-1,-86,-3.0):
            for a_ in np.linspace(0,2*math.pi,12,endpoint=False):
                pt=lambda r: P3(xs+math.cos(a_)*r,y,z+math.sin(a_)*r)
                if not S.isInside(pt(P['pass_d']/2+0.05),1e-4): continue
                for r in np.arange(P['pass_d']/2,P['pass_d']/2+1.61,0.2):
                    if not S.isInside(pt(r+0.05),1e-4):
                        if r-P['pass_d']/2<worst: worst=r-P['pass_d']/2; loc=(f['name'],s_,round(y,1))
                        break
print(f"INFO - thinnest wall left beside an extensor tube clearance hole (through the original pockets/cross beam): {worst:.1f} mm at {loc}  (walls < ~0.4 mm will not print; they just open into the pocket)")
print("\nSUMMARY:",sum(res),"/",len(res),"checks passed")
sys.exit(0 if all(res) else 1)
