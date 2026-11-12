# Renders docs/Gimbal_tendon_preview.png (stock Gimbal vs Gimbal_tendon + the plate post/washer) and docs/thumb_aperture_preview.png (new thumb aperture of R-Palm_Shell_tendon).
# Usage: python render_gimbal_thumb.py <folder with the original 'Amazing Hand Parts - *.step'>   (MateBot STEP files are read from ../step)
import sys, os, math, tempfile, importlib.util
import numpy as np, cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh
here=os.path.dirname(os.path.abspath(__file__)); MSTEP=os.path.join(here,"..","step"); DOCS=os.path.join(here,"..","docs")
AH=sys.argv[1] if len(sys.argv)>1 else os.environ.get("MATEBOT_AH_STEP_DIR","/workspace/ah-enh/cad/step")
spec=importlib.util.spec_from_file_location("rhp",os.path.join(here,"R-Hand_Plate_tendon.py")); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M); P=M.P
tmp=tempfile.mkdtemp()
def tri(shape):
    f=os.path.join(tmp,"t%d.stl"%abs(hash(str(id(shape))))); cq.exporters.export(cq.Workplane("XY").add(shape),f,tolerance=0.05,angularTolerance=0.2); return mesh.Mesh.from_file(f).vectors
def light(v,d=np.array([0.4,-0.5,0.8])):
    n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12; d=d/np.linalg.norm(d); return 0.35+0.65*np.clip(n@d,0,1)
def add(ax,V,rgb,alpha=1.0):
    c=np.array(matplotlib.colors.to_rgb(rgb))[None,:]*light(V)[:,None]; ax.add_collection3d(Poly3DCollection(V,facecolors=np.c_[c,np.full(len(V),alpha)],edgecolor='none'))
def frame(ax,V,el,az,title):
    a=V.reshape(-1,3); mid=(a.max(0)+a.min(0))/2; r=(a.max(0)-a.min(0)).max()/2
    ax.set_xlim(mid[0]-r,mid[0]+r); ax.set_ylim(mid[1]-r,mid[1]+r); ax.set_zlim(mid[2]-r,mid[2]+r); ax.set_box_aspect((1,1,1)); ax.view_init(el,az); ax.set_axis_off(); ax.set_title(title,fontsize=10)
G0=cq.importers.importStep(os.path.join(AH,"Amazing Hand Parts - Gimbal.step")).val(); GT=cq.importers.importStep(os.path.join(MSTEP,"Gimbal_tendon.step")).val()
# hardware under the post (Gimbal-frame coordinates): post, washer D8 x0.8, screw head D4.5 x 1.8
z0=P['post_z'][0]
post=cq.Workplane("XY").workplane(offset=z0).center(0,P['post_y']).circle(P['post_d']/2).extrude(P['post_z'][1]-z0).val()
washer=cq.Workplane("XY").workplane(offset=z0-0.8).center(0,P['post_y']).circle(4.0).circle(1.35).extrude(0.8).val()
head=cq.Workplane("XY").workplane(offset=z0-2.6).center(0,P['post_y']).circle(2.25).extrude(1.8).val()
fig=plt.figure(figsize=(15,5.2))
for i,(el,az,t) in enumerate([(25,-55,"stock Gimbal"),(25,-55,"Gimbal_tendon (rear tab + arc slot)"),(-60,-55,"from below: tab, post (green), washer (blue), screw head (dark)")]):
    ax=fig.add_subplot(1,3,i+1,projection='3d')
    if i==0: V=tri(G0); add(ax,V,'#9aa5b1')
    else:
        V=tri(GT); add(ax,V,'#9aa5b1')
        if i==2:
            for s,c in ((post,'#2b8a3e'),(washer,'#1c7ed6'),(head,'#343a40')): add(ax,tri(s),c)
    frame(ax,V,el,az,t)
fig.suptitle("Gimbal_tendon (printed, replaces the stock Gimbal on the 3 tendon fingers): the plate post slides in the arc slot, so the Gimbal turns +-25 deg but cannot lift out",fontsize=10)
plt.tight_layout(rect=[0,0,1,0.93]); plt.savefig(os.path.join(DOCS,"Gimbal_tendon_preview.png"),dpi=110); plt.close()
# thumb aperture: relieved shell (new) + thumb parts at rest, seen along the hand Y axis and from below
sh_new=cq.importers.importStep(os.path.join(MSTEP,"R-Palm_Shell_tendon.step")).val(); sh_old=cq.importers.importStep(os.path.join(AH,"Amazing Hand Parts - R-Palm_Shell.step")).val()
box=cq.Workplane("XY").box(90,70,90,centered=(True,False,False)).translate((-5,-100,-80)).val()
parts=[]
for nm in ("Gimbal","Proximal","Proximal_Shell"): parts.append(M.to_thumb(cq.importers.importStep(os.path.join(AH,f"Amazing Hand Parts - {nm}.step")).val()))
parts.append(M.to_thumb(cq.importers.importStep(os.path.join(AH,"Amazing Hand Parts - Finger_Frame-1.step")).val()))
parts.append(M.to_thumb(cq.importers.importStep(os.path.join(MSTEP,"finger_link_tendon.step")).val()))
Ps=[tri(p) for p in parts]; Vn=tri(sh_new.intersect(box)); Vo=tri(sh_old.intersect(box))
fig=plt.figure(figsize=(15,5.2))
for i,(el,az,t,Vs) in enumerate([(0,90,"original R-Palm_Shell (seen from the wrist end)",Vo),(0,90,"R-Palm_Shell_tendon: bigger thumb aperture",Vn),(-50,60,"R-Palm_Shell_tendon, from below",Vn)]):
    ax=fig.add_subplot(1,3,i+1,projection='3d'); add(ax,Vs,'#9aa5b1',0.9)
    for V in Ps: add(ax,V,'#e8590c')
    frame(ax,np.vstack([Vs,*Ps]),el,az,t)
fig.suptitle("Thumb aperture (view along the hand Y axis, orange = thumb Gimbal, Frame-1, Proximal, Link at rest (Distal omitted); thumb mounting pose is ESTIMATED from the Wrist_Interface screw pattern)",fontsize=10)
plt.tight_layout(rect=[0,0,1,0.93]); plt.savefig(os.path.join(DOCS,"thumb_aperture_preview.png"),dpi=110); plt.close(); print("ok")
