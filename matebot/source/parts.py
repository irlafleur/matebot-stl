# MateBot tendon hand - v0 UNTESTED parametric starter parts (CadQuery)
# STS3215 dims: 45.2 x 24.7 x 35 mm body (Feetech datasheet nominal) - VERIFY WITH CALIPERS
import cadquery as cq
S_L,S_W,S_H=45.2,24.7,35.0
CL=0.4  # print clearance
def spool(r=8.0):
    # double-groove spool: one groove flexion, one extension (antagonist), bolts to stock round horn
    hub=cq.Workplane("XY").circle(r+3).extrude(2)
    hub=hub.faces(">Z").workplane().circle(r).extrude(3).faces(">Z").workplane().circle(r+2).extrude(1.5)
    hub=hub.faces(">Z").workplane().circle(r).extrude(3).faces(">Z").workplane().circle(r+3).extrude(2)
    hub=hub.faces(">Z").workplane().hole(6.5)  # clearance over horn centre screw
    for a in (0,90,180,270):  # 4x M2.5 to horn - horn bolt circle 14 mm assumed, VERIFY
        import math
        x,y=7*math.cos(math.radians(a)),7*math.sin(math.radians(a))
        hub=hub.faces(">Z").workplane(origin=(0,0,0)).center(x,y).hole(2.7)
    # tendon anchor cross-holes in each groove
    for z in (3.5,8.0):
        hub=hub.cut(cq.Workplane("YZ").workplane(offset=-20).center(r-1.0,z).circle(0.8).extrude(40))
    return hub
def ptfe_anchor(n=8,pitch=7.0):
    # block holding 4 mm OD PTFE tube ends; 1.2 mm line passes through
    L=n*pitch+6
    b=cq.Workplane("XY").box(L,12,10)
    for i in range(n):
        x=-L/2+3+pitch/2+i*pitch
        b=b.cut(cq.Workplane("XZ").workplane(offset=-6).center(x,0).circle(2.1).extrude(8))   # tube socket 8 mm deep
        b=b.cut(cq.Workplane("XZ").workplane(offset=-6).center(x,0).circle(0.9).extrude(12))  # line exit
    b=b.faces(">Z").workplane().pushPoints([(-L/2+2.5,0),(L/2-2.5,0)]).hole(3.4)
    return b
def servo_bay():
    # 2 rows x 4 STS3215 lying flat, outputs facing up; fits 220 mm bed (SV06)
    gap=4; wall=3
    cw,cl=S_W+CL,S_L+CL
    nx,ny=4,2
    W=nx*cw+(nx+1)*gap; Lg=ny*cl+(ny+1)*gap
    tray=cq.Workplane("XY").box(W,Lg,3).translate((0,0,1.5))
    frame=cq.Workplane("XY").box(W,Lg,18).translate((0,0,9))
    for i in range(nx):
        for j in range(ny):
            x=-W/2+gap+cw/2+i*(cw+gap); y=-Lg/2+gap+cl/2+j*(cl+gap)
            frame=frame.cut(cq.Workplane("XY").box(cw,cl,20).translate((x,y,11)))
            frame=frame.cut(cq.Workplane("XY").box(cw-8,cl-8,10).translate((x,y,0)))  # cable/vent cutout
    frame=frame.faces("<Z").workplane().pushPoints([(-W/2+2,-Lg/2+2),(W/2-2,-Lg/2+2),(-W/2+2,Lg/2-2),(W/2-2,Lg/2-2)]).hole(3.4)
    return frame
def finger_adapter():
    # test block: 2 tendon channels (1.2 mm) + knot pocket, slots onto a finger phalanx test print
    b=cq.Workplane("XY").box(16,12,10)
    for x in (-4,4):
        b=b.cut(cq.Workplane("XY").center(x,0).circle(0.7).extrude(20).translate((0,0,-10)))
        b=b.cut(cq.Workplane("XY").center(x,0).circle(1.6).extrude(3).translate((0,0,2)))  # knot/crimp pocket
    b=b.faces("<Y").workplane().hole(2.1)  # 2 mm pin hinge (Amazing Hand pin size)
    return b
parts={"spool_r8":spool(),"ptfe_anchor_8x":ptfe_anchor(),"servo_bay_8x_sts3215":servo_bay(),"finger_tendon_adapter_test":finger_adapter()}
for k,v in parts.items():
    cq.exporters.export(v,f"{k}.stl"); cq.exporters.export(v,f"{k}.step")
    bb=v.val().BoundingBox(); print(k,round(bb.xlen,1),round(bb.ylen,1),round(bb.zlen,1))
