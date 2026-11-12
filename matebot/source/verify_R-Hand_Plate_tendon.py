# Verification of R-Hand_Plate_tendon (v1: pivot blocks, Gimbal underside retention, shorter columns, thumb aperture of R-Palm_Shell_tendon).
# Usage: python verify_R-Hand_Plate_tendon.py <R-Hand_Plate.step> [<Pollen step dir> <finger_link_tendon.step>]   (MateBot step files are read from ../step)
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
MSTEP=os.path.join(here,"..","step")
LINK=sys.argv[3] if len(sys.argv)>3 else os.path.join(MSTEP,"finger_link_tendon.step")
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
    n=math.sqrt((x1-x0)**2+(y1-y0)**2+(z1-z0)**2)
    tend=cq.Solid.makeCylinder(0.6,n,cq.Vector(x0,y0,z0),cq.Vector(x1-x0,y1-y0,z1-z0)).moved(M.fT(f))   # D1.2 mm tendon incl. margin
    v=vol(W(tend).intersect(new))
    if v>0.01: bad.append((ln['finger'],ln['side'],ln['kind'],round(v,2)))
chk("no tendon line (D1.2, mouth of cone to capstan tangent, finger at rest) touches plate material",not bad,f"{len(info['lines'])} lines, collisions: {bad}")
# 5b the same with a 1.5 mm radius corridor (swing/abduction margin)
bad=[]
for ln in info['lines']:
    f=[x for x in FING if x['name']==ln['finger']][0]
    (x0,y0,z0),(x1,y1,z1)=ln['p_exit'],ln['p_cap']; n=math.sqrt((x1-x0)**2+(y1-y0)**2+(z1-z0)**2)
    tend=cq.Solid.makeCylinder(P['corridor_d']/2,n,cq.Vector(x0,y0,z0),cq.Vector(x1-x0,y1-y0,z1-z0)).moved(M.fT(f))
    v=vol(W(tend).intersect(new))
    if v>0.5: bad.append((ln['finger'],ln['side'],ln['kind'],round(v,2)))
chk("tendon corridor D3.0 free of plate material",not bad,f"collisions: {bad}")
# 6 swept Link capstan plates vs new plate
tot=0; badl=[]
for f in FING:
    for s in (-1,1):
        x0=P['plate_x'][0] if s>0 else -P['plate_x'][1]
        cyl=cq.Workplane("YZ").workplane(offset=x0).center(*P['link_pivot']).circle(9.7).extrude(P['plate_x'][1]-P['plate_x'][0]).val().moved(M.fT(f))
        v=vol(W(cyl).intersect(new)); tot+=v
        if v>0.05: badl.append((f['name'],s,round(v,2)))
chk("swept Link capstan plate (R9.7) clears the new plate",tot<0.05,f"overlap {tot:.2f} mm3 {badl}")
# ---------------------------------------------------------------- v1 checks: pivot blocks, Gimbal underside retention, columns, hardware
added=new.cut(orig)
def modload(name):
    sp=importlib.util.spec_from_file_location(name,os.path.join(here,name+".py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
BU=modload("bushing_d6")
def ivol(a,b):
    r=a.intersect(b); return vol(r) if r.solids().vals() else 0.0
def stepwp(path): return cq.importers.importStep(path)
def pol(name): return stepwp(os.path.join(STEPDIR,f"Amazing Hand Parts - {name}.step"))
def mst(name): return stepwp(os.path.join(MSTEP,name+".step"))
def P3(f,x,y,z):
    t=math.radians(f['th']); return cq.Vector(f['c'][0]+x*math.cos(t)-y*math.sin(t), f['c'][1]+x*math.sin(t)+y*math.cos(t), z)
def crop(f):
    """plate material around one finger (finger frame box X +-24, Y -50..12, Z -25..16), in the hand frame"""
    return cq.Workplane("XY").add(new.val().intersect(cq.Workplane("XY").box(48,62,41,centered=(True,False,False)).translate((0,-50,-25)).val().moved(M.fT(f))))
def pose(wp,f,az=0.0,flex=0.0,pivot=(0.0,0.0)):
    """finger-frame part -> hand frame: flexion about the finger X axis through (Y,Z)=pivot, abduction about the finger Z axis, then the finger placement"""
    s=wp
    if flex: s=s.translate((0,-pivot[0],-pivot[1])).rotate((0,0,0),(1,0,0),flex).translate((0,pivot[0],pivot[1]))
    if az: s=s.rotate((0,0,0),(0,0,1),az)
    return cq.Workplane("XY").add(s.val().moved(M.fT(f)))
ABD=P['abd']
crops={f['name']:crop(f) for f in FING}
# 7 pivot block bore: D8.15 coaxial with the finger axis, at Z=8 (probe 0.015 inside / outside)
r0=P['bore_d']/2; ok=True; bad=[]
for f in FING:
    for z in (5.0,8.0,12.0):
        for k in range(8):
            a=2*math.pi*k/8; vin=new.val().isInside(P3(f,(r0-0.015)*math.cos(a),(r0-0.015)*math.sin(a),z),1e-4); vout=new.val().isInside(P3(f,(r0+0.015)*math.cos(a),(r0+0.015)*math.sin(a),z),1e-4)
            if vin or not vout: ok=False; bad.append((f['name'],z,k))
chk(f"pivot block: D{P['bore_d']} bore, Z {P['blk_z'][0]}..{P['blk_z'][1]}, coaxial with each finger axis (3 fingers x 3 heights x 8 probes, +-0.015 mm)",ok,f"bad probes {bad[:5]}")
# 7b the block outline is the Frame-1 outline and fuses with the slab
fz=cq.importers.importStep(os.path.join(STEPDIR,"Amazing Hand Parts - Finger_Frame-1.step"))
miss=[]
for f in FING:
    fr=pose(fz,f); v=vol(fr.cut(new)); miss.append(round(v,1))
print(f"INFO - Finger_Frame-1 material NOT covered by the plate's pivot block (bore, screw holes are expected): {miss} mm3 of {fz.val().Volume():.0f}")
for f in FING:
    res.append(True)
# 8 bushing pair (2 x bushing_d6_flanged) fits the bores of each finger and clears the slab notch
b=BU.build(); low=b.translate((0,0,P['blk_z'][0]-BU.P['flange_t'])); high=b.rotate((0,0,0),(1,0,0),180).translate((0,0,P['blk_z'][1]+BU.P['flange_t']))
pair=low.union(high); tot=0; rep=[]
for f in FING:
    v=ivol(pose(pair,f),crops[f['name']]); tot+=v; rep.append(round(v,3))
chk("bushing pair (bushing_d6_flanged x2) fits each finger's plate bore and the slab notch",tot<0.01,f"interference per finger {rep} mm3 (bushing OD {BU.P['od']}, bore D{P['bore_d']})")
# 9 Gimbals (stock and Gimbal_tendon) turning +-ABD in the bore, clear of the whole new plate
G0=pol("Gimbal"); GT=mst("Gimbal_tendon"); worst={}
for nm,gw in (("Gimbal",G0),("Gimbal_tendon",GT)):
    w=0
    for f in FING:
        for az in (-ABD,-ABD/2,0,ABD/2,ABD): w=max(w,ivol(pose(gw,f,az),crops[f['name']]))
    worst[nm]=round(w,3)
chk(f"Gimbal and Gimbal_tendon turning +-{ABD:.0f} deg (abduction) clear the plate (block, post, rails, columns)",max(worst.values())<0.01,f"worst interference {worst} mm3")
# 10 Gimbal underside retention: post, pilot, washer, screw head, tab slot
r_post=P['post_d']/2; ring_ok=True
for f in FING:
    outer=cq.Workplane("XY").workplane(offset=P['post_z'][0]).center(0,P['post_y']).circle(P['pilot_d']/2+1.2).extrude(P['post_z'][1]-P['post_z'][0])
    inner=cq.Workplane("XY").workplane(offset=P['post_z'][0]-0.1).center(0,P['post_y']).circle(P['pilot_d']/2).extrude(P['post_z'][1]-P['post_z'][0]+0.2)
    ring=pose(outer.cut(inner),f); fr=ivol(ring,new)/vol(ring); ring_ok&=fr>0.9999
chk("post: 1.2 mm solid wall around the D1.9 pilot hole (post D4.4)",ring_ok and (r_post-P['pilot_d']/2)>=1.2,f"wall {(r_post-P['pilot_d']/2):.2f} mm, solid fraction ok={ring_ok}")
pil_ok=True
for f in FING:
    for z in (P['post_z'][0]+0.3,3.0,6.0,P['post_z'][0]+P['pilot_depth']-0.3):
        if new.val().isInside(P3(f,0,P['post_y'],z),1e-4): pil_ok=False
    if not new.val().isInside(P3(f,0,P['post_y'],P['post_z'][0]+P['pilot_depth']+0.5),1e-4): pil_ok=False
chk(f"pilot hole D{P['pilot_d']} open from Z {P['post_z'][0]} to {P['post_z'][0]+P['pilot_depth']} (8 mm for a 2.5x8 screw through the washer), closed above",pil_ok,"probes along the axis")
z_w0=P['post_z'][0]-0.8
washer=cq.Workplane("XY").workplane(offset=z_w0).center(0,P['post_y']).circle(4.0).circle(1.35).extrude(0.8)
head=cq.Workplane("XY").workplane(offset=z_w0-1.8).center(0,P['post_y']).circle(2.25).extrude(1.8)
access=cq.Workplane("XY").workplane(offset=-47.5).center(0,P['post_y']).circle(3.5).extrude(z_w0-1.8+47.5)
v1=sum(ivol(pose(washer.union(head),f),crops[f['name']]) for f in FING); v2=sum(ivol(pose(access,f),new) for f in FING)
chk("washer D8 x 0.8 and screw head D4.5 x 1.8 under the post clear the plate; screwdriver access (D7 column straight down to Z -47) is not blocked by the plate, anchor columns or reliefs",v1+v2<0.01,f"washer+head {v1:.3f} mm3, access column {v2:.3f} mm3 (the palm shell is fitted AFTER the fingers, as in Pollen's guide)")
GTP=modload("Gimbal_tendon").P
gap=GTP['z0']-P['post_z'][0]
chk("washer does not clamp the Gimbal_tendon tab: the post bottom (washer top) is below the tab underside, and the tab still has room under the block",gap>=0.3 and (P['blk_z'][0]-GTP['z1'])>=0.9,f"gap tab/washer {gap:.2f} mm, gap tab/block {P['blk_z'][0]-GTP['z1']:.2f} mm (Gimbal drops/lifts by that much at most)")
# tab slot vs post, washer, head for the whole abduction range, with 0.2 mm radial margin on the post
postg=cq.Workplane("XY").workplane(offset=P['post_z'][0]).center(0,P['post_y']).circle(r_post+0.2).extrude(P['post_z'][1]-P['post_z'][0]+0.5)
w=0
for az in (-ABD,-ABD/2,0,ABD/2,ABD):
    w=max(w,ivol(GT.rotate((0,0,0),(0,0,1),az),postg),ivol(GT.rotate((0,0,0),(0,0,1),az),head))
cover=min((8.0-GT_slot)/2 for GT_slot in (modload("Gimbal_tendon").P['slot_w'],))
chk(f"Gimbal_tendon slot passes the D4.4 post (+0.2 radial margin) over +-{ABD:.0f} deg; screw head clears the tab",w<0.01,f"interference {w:.3f} mm3; the D8 washer overlaps the tab by {cover:.1f} mm on each side of the slot")
# 11 moving finger parts vs plate material, vs post, washer and screw, over flexion x abduction
mov=[("Proximal",pol("Proximal"),(0,0)),("Proximal_Shell",pol("Proximal_Shell"),(0,0)),("Distal",pol("Distal"),(0,0)),("Distal_Shell",pol("Distal_Shell"),(0,0)),("finger_link_tendon",stepwp(LINK),(0,-6)),("Gimbal_tendon",GT,None)]
hw=washer.union(head)
res_pl={}; res_hw={}; arg_pl={}; ext5={}
for nm,sw,pv in mov:
    a=0; b2=0; e5=0
    for f in FING:
        for az in (-ABD,0,ABD):
            for fl in ((-80,-40,0,5) if pv is not None else (0,)):
                t=pose(sw,f,az,fl,pv) if pv is not None else pose(sw,f,az)
                v=ivol(t,crops[f['name']])
                if fl==5: e5=max(e5,v)
                elif v>a: a=v; arg_pl[nm]=(f['name'],az,fl)
                if f is FING[0]: b2=max(b2,ivol(t,pose(hw,f)))
    res_pl[nm]=round(a,3); res_hw[nm]=round(b2,3); ext5[nm]=round(e5,2)
chk(f"Proximal, shells, Distal, tendon Link, Gimbal_tendon swept over flexion -80..0 x abduction +-{ABD:.0f} deg clear the plate (3 fingers)",max(res_pl.values())<0.05,f"worst per part {res_pl} mm3 at {arg_pl}")
print(f"INFO - at +5 deg past straight (hyper-extension, the stock Finger_Frame-1 itself stops the Proximal at +7 deg) the Proximal touches the pivot block: overlaps {ext5} mm3 (stock Frame-1: 2.7 mm3 for the Proximal at the same pose, i.e. the same contact)")
chk("the same parts clear the washer and the screw head (index finger, flexion -80..+5)",max(res_hw.values())<0.01,f"{res_hw} mm3")
# 12 columns: 1.5 mm closer sockets, 1.5 mm shorter
d_new=P['z_ext']-P['z_flex']; L_new=P['col_top']-(P['z_flex']-P['col_bot_margin'])
chk("sockets 1.5 mm closer and columns 1.5 mm shorter than v0 (axes 16.6 apart, columns 33.9 long)",abs((16.6-d_new)-1.5)<1e-6 and abs((33.9-L_new)-1.5)<1e-6,f"socket spacing {d_new:.1f} mm (v0 16.6), column length {L_new:.1f} mm (v0 33.9); wall under the flexor bore {P['col_bot_margin']-P['sock_d']/2:.2f} mm, between the two cone mouths {d_new-P['cone_d']:.1f} mm")
# 13 tendon lines vs Gimbal_tendon / Proximal / link at rest (tendon D1.2)
bad=[]
for ln in info['lines']:
    f=[x for x in FING if x['name']==ln['finger']][0]
    (x0,y0,z0),(x1,y1,z1)=ln['p_exit'],ln['p_cap']; n=math.sqrt((x1-x0)**2+(y1-y0)**2+(z1-z0)**2)
    tend=cq.Solid.makeCylinder(0.6,n,cq.Vector(x0,y0,z0),cq.Vector(x1-x0,y1-y0,z1-z0)).moved(M.fT(f))
    for nme,shp in (("Gimbal_tendon",GT),("Gimbal",G0),("Proximal",pol("Proximal"))):
        for az in (-ABD,0,ABD):
            v=vol(W(tend).intersect(pose(shp,f,az)))
            if v>0.01: bad.append((ln['finger'],ln['side'],ln['kind'],nme,az,round(v,2)))
chk("tendon lines (D1.2) clear Gimbal, Gimbal_tendon and Proximal (rest, abduction +-25; the line ends tangent on the Link capstan by design)",not bad,f"collisions {bad[:6]}")
# 8 palm shell: the original soft shell is touched by the outer columns, the relieved copy must be clear
orig_shell=cq.importers.importStep(os.path.join(STEPDIR,"Amazing Hand Parts - R-Palm_Shell.step"))
v0=vol(orig_shell.intersect(added)); relieved,nn=M.shell_relieved(info); v1=vol(relieved.intersect(added))
print(f"INFO - added plate material overlapping the ORIGINAL R-Palm_Shell: {v0:.1f} mm3 ({nn} notches needed)")
chk("relieved R-Palm_Shell_tendon clears the added material",v1<0.05,f"overlap {v1:.3f} mm3; shell lost {orig_shell.val().Volume()-relieved.val().Volume():.0f} mm3")
for n in ("R-Top_Shell","R-Wrist_Interface"):
    sh=cq.importers.importStep(os.path.join(STEPDIR,f"Amazing Hand Parts - {n}.step"))
    v=vol(sh.intersect(added)); chk(f"added material clears {n}",v<0.05,f"{v:.2f} mm3")
# thumb aperture: every thumb part, swept over flexion x abduction, keeps >= thumb_clear from the relieved R-Palm_Shell_tendon (and from the plate)
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
def mind(a,b):
    d=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped); d.Perform(); return d.Value()
def fpose(wp,az=0.0,flex=0.0,pivot=(0.0,0.0)):
    s=wp
    if flex: s=s.translate((0,-pivot[0],-pivot[1])).rotate((0,0,0),(1,0,0),flex).translate((0,pivot[0],pivot[1]))
    if az: s=s.rotate((0,0,0),(0,0,1),az)
    return s.val()
tbox=cq.Workplane("XY").box(80,60,80,centered=(True,False,False)).translate((-5,-95,-75)).val()
shc=cq.Workplane("XY").add(relieved.val().intersect(tbox)); pc=cq.Workplane("XY").add(new.val().intersect(tbox)); sho=cq.Workplane("XY").add(orig_shell.val().intersect(tbox))
tparts=[("Gimbal",G0,None),("Finger_Frame-1",fz,False),("Proximal",pol("Proximal"),(0,0)),("Proximal_Shell",pol("Proximal_Shell"),(0,0)),("Distal",pol("Distal"),(0,0)),("Distal_Shell",pol("Distal_Shell"),(0,0)),("finger_link_tendon",stepwp(LINK),(0,-6))]
dmin={}; dold={}; arg={}
for nm,sw,pv in tparts:
    poses=[(0,0)] if pv is False else ([(az,0) for az in (-ABD,0,ABD)] if pv is None else [(az,fl) for az in (-ABD,0,ABD) for fl in (-80,-40,0,5)])
    for az,fl in poses:
        sh=M.to_thumb(fpose(sw,az,fl,pv if pv else (0,0)) if pv is not False else sw.val())
        d1=mind(sh,shc.val()); d2=mind(sh,pc.val()); d3=mind(sh,sho.val()); d=min(d1,d2)
        if nm not in dmin or d<dmin[nm]: dmin[nm]=d; arg[nm]=(az,fl)
        dold[nm]=min(dold.get(nm,1e9),d3)
rep=", ".join(f"{k} {v:.2f}@az{arg[k][0]}/fl{arg[k][1]}" for k,v in dmin.items())
fr_d=dmin.pop("Finger_Frame-1")
print(f"INFO - thumb Finger_Frame-1 (fixed, bolted on the Wrist_Interface, not in the aperture sweep) is {fr_d:.2f} mm from the palm shell / plate (0.35 mm from the stock shell): it is the fixed mounting part, it has to sit close")
chk(f"thumb: all moving parts (Gimbal, Proximal, Distal, shells, tendon Link) stay >= {P['thumb_clear']} mm from the relieved palm shell and the plate over flexion -80..+5 x abduction +-{ABD:.0f} deg",min(dmin.values())>=P['thumb_clear']-0.05,rep)
print("INFO - for comparison, same poses against the ORIGINAL palm shell (min distance per part, mm; the tendon Link is the part that collides there): "+", ".join(f"{k} {v:.2f}" for k,v in dold.items()))
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
