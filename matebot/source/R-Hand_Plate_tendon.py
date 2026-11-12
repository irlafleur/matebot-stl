# Usage: python R-Hand_Plate_tendon.py "/path/to/Amazing Hand Parts - R-Hand_Plate.step"   (needs CadQuery)
# MateBot v1 (UNTESTED): Amazing Hand R-Hand_Plate with PTFE (Bowden) tube anchors for the tendon-driven fingers, and the finger pivot blocks of Finger_Frame-1 merged in.
# Original plate: Pollen Robotics, CC BY 4.0.  Added geometry: MateBot, CC BY 4.0.
#
# What is added (all values in mm, see P below):
#   * 3 fingers on the plate (index, middle, ring) x 2 sides x 2 tendons (extensor + flexor) = 12 sockets.
#     The thumb is NOT on this plate (it screws into the Wrist_Interface), see DESIGN-NOTES.
#   * one "anchor column" per finger side (6 columns). Each column holds 2 sockets: extensor (back, Z=+2.3) over flexor (palm side, Z=-14.3).
#   * socket = D4.2 x 8 deep bore for a 4 mm OD PTFE tube, stop shoulder with a D2.2 through-hole for the tendon,
#     then a conical exit (D2.2 -> D5.0 over 3 mm) that faces the finger so the tendon can swing without rubbing.
#   * tube clearance holes (D5.0) through the cross beam behind the columns, along each tube line.
#   * tendon corridors (D3.0) and relief cuts so the Link capstan plates (swept R=9.7 + margin 0.6) and the tendons clear the plate walls.
#   * v1: Finger_Frame-1 and Finger_Frame-2 are no longer printed.  Their only remaining job (hold the Gimbal's D6 abduction boss in two bushings) is done by a
#     PIVOT BLOCK per finger (the Frame-1 outline, Z 4.5..12.5, D8.15 bore) fused under the plate slab where the Frame-1 used to be screwed.  Frame-2 only carried servos.
#   * v1: Gimbal retention from UNDERNEATH: a D4.4 post (pilot D1.9) hangs from each pivot block down to Z=0.5; with Gimbal_tendon (arc slot) and the large M2.5 washer
#     + 2.5x8 thermoplastic screw from below the Gimbal is held and still turns +-25 degrees.  The thumb keeps a stock Gimbal and a printed Finger_Frame-1 (it is mounted on the Wrist_Interface).
#   * v1: the extensor/flexor sockets of each column are 1.5 mm closer (flexor Z -14.3 -> -12.8) and the columns 1.5 mm shorter.
#   * v1: R-Palm_Shell_tendon also gets a bigger thumb aperture (swept Link capstan plates of the thumb + 1.5 mm).
# Frames: plate frame = Pollen assembly frame (X right, Y toward fingertips, Z toward the back of the hand).
# Finger frame = plate frame rotated about Z and moved to the finger gimbal (index 0 deg, middle -5.76, ring -13.46).
import cadquery as cq, numpy as np, math, os, sys, json
SRC=sys.argv[1] if len(sys.argv)>1 else os.environ.get("MATEBOT_PLATE_STEP","Amazing Hand Parts - R-Hand_Plate.step")
# The original R-Palm_Shell (same folder as the plate, or MATEBOT_PALM_SHELL_STEP): the two outermost flexor columns touch its skin, so a relieved copy is exported too.
SHELL=os.environ.get("MATEBOT_PALM_SHELL_STEP",os.path.join(os.path.dirname(os.path.abspath(SRC)),"Amazing Hand Parts - R-Palm_Shell.step"))
# Finger_Frame-1 (its outline is the pivot block outline), same folder as the plate or MATEBOT_FRAME1_STEP
FRAME1=os.environ.get("MATEBOT_FRAME1_STEP",os.path.join(os.path.dirname(os.path.abspath(SRC)),"Amazing Hand Parts - Finger_Frame-1.step"))
FINGERS=[dict(name="index", c=(0.0,0.0), th=0.0),
         dict(name="middle",c=(32.8,-6.0),th=-5.76),
         dict(name="ring",  c=(65.0,-17.1),th=-13.46)]   # fitted to the plate's M2.8 finger-frame holes (+-6,-7 in finger frame)
P=dict(
  tube_od=4.0, tube_id=2.0,
  sock_d=4.2, sock_depth=8.0,       # bore for the tube
  tendon_hole_d=2.2, straight=1.6,  # stop shoulder with tendon hole (straight part length)
  cone_len=3.0, cone_d=5.0,         # conical exit toward the finger
  y_tube_end=-30.0,                 # finger-frame Y of the tube stop face (>= 30 mm behind the finger pivot)
  x_in=10.5,                        # |X| of the socket axis in the finger frame (capstan lines are at 13.2, tendon leans 6 deg inward)
  z_ext=2.3, z_flex=-12.8,          # socket axes. v1: flexor 1.5 mm closer to the extensor (was -14.3). Capstan tangents are at Z=3.0 / -15.0 (pivot Z=-6, radius 9.0)
  col_hw=4.1,                       # half width of a column (>= cone mouth radius 2.5 + 1.6 wall)
  col_top=15.5, col_bot_margin=4.1, # column goes up to the top face of the slab (Z=15.5): the plate still prints slab-down with no new supports. 4.1 below the flexor axis
  pass_d=4.5,                       # clearance hole for the tube through the cross beam
  corridor_d=3.0,                   # tendon corridor
  relief_r=10.3,                    # swept radius of the Link capstan plates (rim R=9.7 since finger_link_tendon v1) + 0.6
  link_pivot=(0.0,-6.0), plate_x=(12.0,14.4),
  capstan_x=13.2, capstan_r=9.0,    # tendon centre radius on the Link plate (v1: 9.0, was 8.3)
  # v1 pivot block (Finger_Frame-1 function) and Gimbal underside retention
  bore_d=8.15, bore_ch=0.3,         # D8.15 bore of Finger_Frame-1 (CAD), 0.3 chamfers
  blk_z=(4.5,12.5),                 # Frame-1 Z range = under the slab
  post_d=4.4, post_y=-8.6, post_z=(0.1,4.5), pilot_d=1.9, pilot_depth=8.0,   # Gimbal_tendon slot centre radius is 8.6; screw 2.5x8 + washer from below; post bottom 0.4 below the tab so the washer does not clamp it
  abd=25.0,                         # abduction travel the slot / swept checks are designed for (+- degrees)
  # v1 thumb: finger frame -> hand frame (derived from the Wrist_Interface's 3 screw holes, see DESIGN-NOTES): finger Y' = 20 deg off -Z toward -X, finger Z' = -Y(hand)
  thumb_tilt=20.0, thumb_origin=(0.0,-72.5,-39.58), thumb_clear=1.5,
)
def fT(f): return cq.Location(cq.Vector(f['c'][0],f['c'][1],0), cq.Vector(0,0,1), f['th'])
def cylY(x,z,y_hi,y_lo,d):
    """solid cylinder along finger Y from y_lo to y_hi (finger frame, before placing)"""
    return cq.Workplane("XZ").workplane(offset=-y_hi).center(x,z).circle(d/2).extrude(y_hi-y_lo).val()
def coneY(x,z,y_small,y_big,d_small,d_big):
    return cq.Solid.makeCone(d_small/2,d_big/2,y_big-y_small,cq.Vector(x,y_small,z),cq.Vector(0,1,0))
def sock_geometry(p=P):
    """y positions (finger frame) of one socket, from the stop face going toward the finger"""
    y0=p['y_tube_end']
    return dict(y_back=y0-p['sock_depth'], y_stop=y0, y_cone0=y0+p['straight'], y_front=y0+p['straight']+p['cone_len'])
def tangent_pt(E,C,r,upper):
    """tangent point (y,z) on the capstan circle (centre C, radius r) of the straight line coming from E=(y,z) (cone mouth); upper side or lower side"""
    dy,dz=E[0]-C[0],E[1]-C[1]; d=math.hypot(dy,dz); phi=math.atan2(dz,dy); al=math.acos(r/d)
    pts=[(C[0]+r*math.cos(phi+k*al),C[1]+r*math.sin(phi+k*al)) for k in (1,-1)]
    return max(pts,key=lambda q:q[1]) if upper else min(pts,key=lambda q:q[1])
def thumb_trsf(p=P):
    """finger frame -> hand frame for the thumb, as an OCP gp_Trsf"""
    from OCP.gp import gp_Trsf
    a=math.radians(p['thumb_tilt']); u=(-math.sin(a),0.0,-math.cos(a)); zp=(0.0,-1.0,0.0)
    xp=(u[1]*zp[2]-u[2]*zp[1],u[2]*zp[0]-u[0]*zp[2],u[0]*zp[1]-u[1]*zp[0])
    o=p['thumb_origin']; t=gp_Trsf()
    t.SetValues(xp[0],u[0],zp[0],o[0], xp[1],u[1],zp[1],o[1], xp[2],u[2],zp[2],o[2])
    return t
def to_thumb(shape,p=P):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped,thumb_trsf(p),True).Shape())
def _hull2d(pts):
    pts=sorted(set(pts))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[]; 
    for q in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],q)<=0: lo.pop()
        lo.append(q)
    up=[]
    for q in reversed(pts):
        while len(up)>=2 and cross(up[-2],up[-1],q)<=0: up.pop()
        up.append(q)
    return lo[:-1]+up[:-1]
def thumb_envelope(p=P):
    """(side -> 2D hull polygon in the hand XZ plane, y0, y1): the thumb's Link capstan plates (disc R9.7 about the Link pivot, finger X' 12..14.4 on each side) swept over +-abd of
    abduction (rotation about the finger Z' axis = the hand -Y direction, so it is a rotation in the hand XZ plane), grown by thumb_clear.  The disc plane contains the hand Y direction,
    so each plate is a thin rectangle in XZ extruded along Y over the disc diameter."""
    cl=p['thumb_clear']; R=9.7+cl; a_=math.radians(p['thumb_tilt'])
    xp=(-math.cos(a_),math.sin(a_)); u=(-math.sin(a_),-math.cos(a_)); o=(p['thumb_origin'][0],p['thumb_origin'][2])
    zc=-p['link_pivot'][1]*-1  # finger Z' of the pivot (-6) -> hand Y = origin_y - Z'
    ypiv=p['thumb_origin'][1]-p['link_pivot'][1]
    out={}
    for s in (-1,1):
        xa=(p['plate_x'][0]-cl) if s>0 else -(p['plate_x'][1]+cl); xb=(p['plate_x'][1]+cl) if s>0 else -(p['plate_x'][0]-cl)
        pts=[]
        n=int(round(2*p['abd']/2.5))
        for k in range(n+1):
            az=math.radians(-p['abd']+k*(2*p['abd']/n)); ca,sa=math.cos(az),math.sin(az)
            for X in (xa,xb):
                for Y in (-R,R):
                    X2,Y2=X*ca-Y*sa, X*sa+Y*ca            # rotate about finger Z'
                    pts.append((o[0]+X2*xp[0]+Y2*u[0], o[1]+X2*xp[1]+Y2*u[1]))
        out[s]=(_hull2d(pts),ypiv-R,ypiv+R)
    return out
def thumb_extra(p=P,y_from=-77.0):
    """(polygon, y0, y1): the thumb's Proximal and Proximal_Shell swept over abduction +-abd x flexion -80..+5 (5 deg = the hard stop on the stock Frame-1), only the part of the sweep that lies
    wrist-ward of the Link-plate prisms (hand Y < y_from), projected on the hand XZ plane, grown by thumb_clear, hulled.  Needed because the stock shell edge at the wrist end is only ~0.9 mm
    from the Proximal_Shell at +-25 deg abduction.  Uses the original Pollen Proximal / Proximal_Shell STEP files (same folder as the plate)."""
    cl=p['thumb_clear']; pts=[]; d=os.path.dirname(os.path.abspath(SRC))
    for nm in ("Proximal","Proximal_Shell"):
        sh=cq.importers.importStep(os.path.join(d,f"Amazing Hand Parts - {nm}.step")).val()
        verts,_=sh.tessellate(0.4)
        base=np.array([(v.x,v.y,v.z) for v in verts])
        for fl in (-80,-40,0,5):
            a=math.radians(fl); c,s_=math.cos(a),math.sin(a)
            fy=base[:,1]*c-base[:,2]*s_; fz=base[:,1]*s_+base[:,2]*c; fx=base[:,0]
            for az in np.linspace(-p['abd'],p['abd'],9):
                b=math.radians(az); cb,sb=math.cos(b),math.sin(b)
                X=fx*cb-fy*sb; Y=fx*sb+fy*cb; Z=fz
                pts.extend(zip(X.tolist(),Y.tolist(),Z.tolist()))
    # transform all points with the thumb trsf at once
    t=thumb_trsf(p); m=[[t.Value(i,j) for j in range(1,5)] for i in range(1,4)]
    A=np.array(pts); H=A@np.array([r[:3] for r in m]).T+np.array([r[3] for r in m])
    H=H[H[:,1]<y_from]
    ring=[(cl/math.cos(math.pi/8)*math.cos(k*math.pi/4+math.pi/8),cl/math.cos(math.pi/8)*math.sin(k*math.pi/4+math.pi/8)) for k in range(8)]
    q=[(float(h[0])+rx,float(h[2])+rz) for h in H[::7] for rx,rz in ring]
    poly=_hull2d(q); ymin=float(H[:,1].min())-cl
    return poly,ymin,y_from+1.0
def thumb_cutter(p=P):
    """prisms (hand frame): two for the Link capstan plates (thumb_envelope) + one wrist-end prism (thumb_extra)"""
    out=[]
    poly,y0,y1=thumb_extra(p); out.append(cq.Workplane("XZ").workplane(offset=-y1).polyline(poly).close().extrude(y1-y0).val())
    for s,(poly,y0,y1) in thumb_envelope(p).items():
        out.append(cq.Workplane("XZ").workplane(offset=-y1).polyline(poly).close().extrude(y1-y0).val())   # XZ plane normal is -Y: offset=-y1 puts it at Y=y1, extrude toward -Y
    return out
def shell_relieved(info,p=P,grow=0.6):
    """R-Palm_Shell with (1) a notch wherever an anchor column would touch it (columns grown by 0.6 mm), (2) the Gimbal post / washer / screw-head region, (3) a bigger thumb aperture.
    All tools go into ONE boolean (many near-coincident swept cylinders break sequential cuts)."""
    shell0=cq.importers.importStep(SHELL); g=info['g']; tools=[]
    for i,c in enumerate(info['columns']):
        f=FINGERS[i//2]; s=(-1,1)[i%2]; xs=s*p['x_in']; hw=p['col_hw']+grow
        zb=p['z_flex']-p['col_bot_margin']-grow; zt=p['col_top']
        tools.append(cq.Workplane("XY").box(2*hw,g['y_front']-g['y_back']+2*grow,zt-zb,centered=False).translate((xs-hw,g['y_back']-grow,zb)).val().moved(fT(f)))
    for f in FINGERS:
        for pc in info['post_clear']: tools.append(pc.moved(fT(f)))
    tools+=info['thumb_cut']
    cut=shell0.val().cut(*tools)
    big=[x for x in cut.Solids() if x.Volume()>1.0]          # drop the zero-volume sliver solids that the skin boolean can leave
    res=cq.Workplane("XY").add(big[0] if len(big)==1 else cq.Compound.makeCompound(big))
    n=0
    for i,c in enumerate(info['columns']):    # number of column notches that really removed material
        t=tools[i]; 
        if shell0.val().intersect(t).Volume()>0.5: n+=1
    return res,n
def pivot_block(p=P):
    """Finger_Frame-1 outline (bottom face outer wire) extruded over Z 4.5..12.5, minus the D8.15 bore with 0.3 chamfers"""
    f1=cq.importers.importStep(FRAME1); fb=f1.faces("<Z").vals()[0]
    z0,z1=p['blk_z']
    blk=cq.Workplane("XY").add(cq.Solid.extrudeLinear(cq.Face.makeFromWires(fb.outerWire()),cq.Vector(0,0,z1-z0)).moved(cq.Location(cq.Vector(0,0,z0-fb.Center().z))))
    r=p['bore_d']/2; ch=p['bore_ch']
    bore=cq.Workplane("XY").workplane(offset=z0-0.01).circle(r).extrude(z1-z0+0.02)
    c0=cq.Workplane("XY").add(cq.Solid.makeCone(r+ch,r,ch+0.01,cq.Vector(0,0,z0-0.01),cq.Vector(0,0,1)))
    c1=cq.Workplane("XY").add(cq.Solid.makeCone(r,r+ch,ch+0.01,cq.Vector(0,0,z1-ch),cq.Vector(0,0,1)))
    return blk,[bore,c0,c1]
def post_solids(p=P):
    """(post to add, pilot hole to cut, [clearance volumes for the shell]) in the finger frame"""
    z0,z1=p['post_z']
    post=cq.Workplane("XY").workplane(offset=z0).center(0,p['post_y']).circle(p['post_d']/2).extrude(z1-z0+0.5)
    pilot=cq.Workplane("XY").workplane(offset=z0-0.01).center(0,p['post_y']).circle(p['pilot_d']/2).extrude(p['pilot_depth']+0.01)
    clear=cq.Workplane("XY").workplane(offset=z0-3.0).center(0,p['post_y']).circle(p['post_d']/2+3.0).extrude(3.0+z1-z0).val()   # washer D8 + head + 1.0 margin, under the post
    return post,pilot,[clear]
def build(p=P):
    plate=cq.importers.importStep(SRC)
    g=sock_geometry(p); parts_add=[]; cuts=[]; lines=[]; relief=[]
    blk0,bore_cuts0=pivot_block(p); post0,pilot0,post_clear=post_solids(p)
    C=p['link_pivot']
    for f in FINGERS:
        L=fT(f)
        parts_add.append(blk0.val().moved(L)); parts_add.append(post0.val().moved(L))
        cuts += [x.val().moved(L) for x in bore_cuts0+[pilot0]]
        for s in (-1,1):
            xs=s*p['x_in']; hw=p['col_hw']
            zb=p['z_flex']-p['col_bot_margin']; zt=p['col_top']
            col=cq.Workplane("XY").box(2*hw,g['y_front']-g['y_back'],zt-zb,centered=False).translate((xs-hw,g['y_back'],zb))
            colw=col.val().moved(L)
            parts_add.append(colw)
            for nm,z in (("ext",p['z_ext']),("flex",p['z_flex'])):
                sock=cylY(xs,z,g['y_stop'],g['y_back']-0.01,p['sock_d'])
                hole=cylY(xs,z,g['y_cone0']+0.01,g['y_stop']-0.01,p['tendon_hole_d'])
                cone=coneY(xs,z,g['y_cone0'],g['y_front']+0.01,p['tendon_hole_d'],p['cone_d']+0.0)
                thru=cylY(xs,z,g['y_back'],-90.0,p['pass_d'])
                # tendon corridor: straight line from the cone mouth to its tangent point on the capstan (circle R=capstan_r about the Link pivot), leaning to X=+-capstan_x
                xc=s*p['capstan_x']; ang_y=g['y_front']
                yT,zT=tangent_pt((ang_y,z),C,p['capstan_r'],nm=="ext")
                dx,dy,dz=xc-xs,yT-ang_y,zT-z; n=math.sqrt(dx*dx+dy*dy+dz*dz)
                cor=cq.Solid.makeCylinder(p['corridor_d']/2,n+3.0,cq.Vector(xs,ang_y,z),cq.Vector(dx,dy,dz))
                cuts += [x.moved(L) for x in (sock,hole,cone,thru,cor)]
                lines.append(dict(finger=f['name'],side=s,kind=nm,p_exit=(xs,g['y_front'],z), p_cap=(xc,yT,zT), axis=(xs,z)))
            x0=p['plate_x'][0] if s>0 else -p['plate_x'][1]
            ext_o=p.get('relief_out',2.6)      # v1: extra relief on the OUTER side so the Link plates can abduct +-25 deg (the rim sweeps out to X = 17.2)
            xa=x0-0.6-(ext_o if s<0 else 0.0)
            rel=cq.Workplane("YZ").workplane(offset=xa).center(*p['link_pivot']).circle(p['relief_r']).extrude(p['plate_x'][1]-p['plate_x'][0]+1.2+ext_o).val()
            relief.append(rel.moved(L))
    body=plate
    for a in parts_add: body=body.union(cq.Workplane("XY").add(a))
    for c in cuts+relief: body=body.cut(cq.Workplane("XY").add(c))
    return body,plate,dict(g=g,lines=lines,cuts=cuts,columns=[a for a in parts_add if a.BoundingBox().zlen>25],relief=relief,post_clear=post_clear,thumb_cut=thumb_cutter(p))
if __name__=="__main__":
    new,orig,info=build()
    bb=new.val().BoundingBox()
    print("bbox",*(round(v,2) for v in (bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax)))
    print("solids",len(new.solids().vals()),"vol",round(new.val().Volume(),1),"orig vol",round(orig.val().Volume(),1))
    if os.path.exists(SHELL):
        sh,n=shell_relieved(info); print("palm shell notches:",n,"vol removed",round(cq.importers.importStep(SHELL).val().Volume()-sh.val().Volume(),1))
        cq.exporters.export(sh,"R-Palm_Shell_tendon.step"); cq.exporters.export(sh,"R-Palm_Shell_tendon.stl",tolerance=0.01,angularTolerance=0.1)
    cq.exporters.export(new,"R-Hand_Plate_tendon.step"); cq.exporters.export(new,"R-Hand_Plate_tendon.stl",tolerance=0.01,angularTolerance=0.1)
