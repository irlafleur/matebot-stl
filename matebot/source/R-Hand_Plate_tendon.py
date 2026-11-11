# Usage: python R-Hand_Plate_tendon.py "/path/to/Amazing Hand Parts - R-Hand_Plate.step"   (needs CadQuery)
# MateBot v0 (UNTESTED): Amazing Hand R-Hand_Plate with PTFE (Bowden) tube anchors for the tendon-driven fingers.
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
# Frames: plate frame = Pollen assembly frame (X right, Y toward fingertips, Z toward the back of the hand).
# Finger frame = plate frame rotated about Z and moved to the finger gimbal (index 0 deg, middle -5.76, ring -13.46).
import cadquery as cq, math, os, sys, json
SRC=sys.argv[1] if len(sys.argv)>1 else os.environ.get("MATEBOT_PLATE_STEP","Amazing Hand Parts - R-Hand_Plate.step")
# The original R-Palm_Shell (same folder as the plate, or MATEBOT_PALM_SHELL_STEP): the two outermost flexor columns touch its skin, so a relieved copy is exported too.
SHELL=os.environ.get("MATEBOT_PALM_SHELL_STEP",os.path.join(os.path.dirname(os.path.abspath(SRC)),"Amazing Hand Parts - R-Palm_Shell.step"))
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
  z_ext=2.3, z_flex=-14.3,          # tendon lines leaving the capstan tangents (pivot Z=-6, radius 8.3)
  col_hw=4.1,                       # half width of a column (>= cone mouth radius 2.5 + 1.6 wall)
  col_top=15.5, col_bot_margin=4.1, # column goes up to the top face of the slab (Z=15.5): the plate still prints slab-down with no new supports. 4.1 below the flexor axis
  pass_d=4.5,                       # clearance hole for the tube through the cross beam
  corridor_d=3.0,                   # tendon corridor
  relief_r=10.3,                    # swept radius of the Link capstan plates (rim R=9.7 since finger_link_tendon v1) + 0.6
  link_pivot=(0.0,-6.0), plate_x=(12.0,14.4),
  capstan_x=13.2, capstan_r=9.0,    # tendon centre radius on the Link plate (v1: 9.0, was 8.3)
  z_cap_ext=3.0, z_cap_flex=-15.0,  # capstan tangent heights = pivot Z (-6) +- capstan_r. The sockets stay at +2.3 / -14.3 (v0 plate geometry unchanged): the tendon only leans 0.7 mm over 25 mm
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
def shell_relieved(info,p=P,grow=0.6):
    """R-Palm_Shell with a notch wherever an anchor column would touch it (columns grown by 0.6 mm)."""
    shell=cq.importers.importStep(SHELL); g=info['g']; n=0
    for i,c in enumerate(info['columns']):
        f=FINGERS[i//2]; s=(-1,1)[i%2]; xs=s*p['x_in']; hw=p['col_hw']+grow
        zb=p['z_flex']-p['col_bot_margin']-grow; zt=p['col_top']
        box=cq.Workplane("XY").box(2*hw,g['y_front']-g['y_back']+2*grow,zt-zb,centered=False).translate((xs-hw,g['y_back']-grow,zb)).val().moved(fT(f))
        before=shell.val().Volume(); shell=shell.cut(cq.Workplane("XY").add(box))
        if before-shell.val().Volume()>0.5: n+=1
    return shell,n
def build(p=P):
    plate=cq.importers.importStep(SRC)
    g=sock_geometry(p); parts_add=[]; cuts=[]; lines=[]; relief=[]
    for f in FINGERS:
        L=fT(f)
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
                # tube clearance through whatever is behind the column (cross beam etc.)
                thru=cylY(xs,z,g['y_back'],-90.0,p['pass_d'])
                # tendon corridor from the cone mouth to the capstan (leaning toward X=+-13.2)
                xc=s*p['capstan_x']; ang_y=g['y_front']
                zc=p['z_cap_ext'] if nm=="ext" else p['z_cap_flex']
                dx,dy,dz=xc-xs,0.0-ang_y,zc-z; n=math.sqrt(dx*dx+dy*dy+dz*dz)
                cor=cq.Solid.makeCylinder(p['corridor_d']/2,n+3.0,cq.Vector(xs,ang_y,z),cq.Vector(dx,dy,dz))
                cuts += [x.moved(L) for x in (sock,hole,cone,thru,cor)]
                lines.append(dict(finger=f['name'],side=s,kind=nm,
                                  p_exit=(xs,g['y_front'],z), p_cap=(xc,0.0,zc), axis=(xs,z)))
            # relief for the swept Link capstan plate on this side
            x0=p['plate_x'][0] if s>0 else -p['plate_x'][1]
            rel=cq.Workplane("YZ").workplane(offset=x0-0.6).center(*p['link_pivot']).circle(p['relief_r']).extrude(p['plate_x'][1]-p['plate_x'][0]+1.2).val()
            relief.append(rel.moved(L))
    body=plate
    for a in parts_add: body=body.union(cq.Workplane("XY").add(a))
    for c in cuts+relief: body=body.cut(cq.Workplane("XY").add(c))
    return body,plate,dict(g=g,lines=lines,cuts=cuts,columns=parts_add,relief=relief)
if __name__=="__main__":
    new,orig,info=build()
    bb=new.val().BoundingBox()
    print("bbox",*(round(v,2) for v in (bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax)))
    print("solids",len(new.solids().vals()),"vol",round(new.val().Volume(),1),"orig vol",round(orig.val().Volume(),1))
    if os.path.exists(SHELL):
        sh,n=shell_relieved(info); print("palm shell notches:",n,"vol removed",round(cq.importers.importStep(SHELL).val().Volume()-sh.val().Volume(),1))
        cq.exporters.export(sh,"R-Palm_Shell_tendon.step"); cq.exporters.export(sh,"R-Palm_Shell_tendon.stl",tolerance=0.01,angularTolerance=0.1)
    cq.exporters.export(new,"R-Hand_Plate_tendon.step"); cq.exporters.export(new,"R-Hand_Plate_tendon.stl",tolerance=0.01,angularTolerance=0.1)
