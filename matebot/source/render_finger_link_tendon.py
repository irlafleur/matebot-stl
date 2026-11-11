# Renders the previews of finger_link_tendon (v1).  Usage: python render_finger_link_tendon.py <Link.step>  (CadQuery, numpy-stl, matplotlib)
import sys, os, math, importlib.util, tempfile
import numpy as np, cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh
here=os.path.dirname(os.path.abspath(__file__)); docs=os.path.join(here,"..","docs")
spec=importlib.util.spec_from_file_location("flt",os.path.join(here,"finger_link_tendon.py")); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
P=M.P; new,orig=M.build(); G=M.G2
f=os.path.join(tempfile.mkdtemp(),"l.stl"); cq.exporters.export(new,f,tolerance=0.02,angularTolerance=0.2); V=mesh.Mesh.from_file(f).vectors
def light(v,d=np.array([0.4,-0.5,0.8])):
    n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12; d=d/np.linalg.norm(d); return 0.3+0.7*np.clip(n@d,0,1)
# ---- preview: 3 views + close-up of the outer face of the +X plate
fig=plt.figure(figsize=(16,5.5))
for i,(el,az,t) in enumerate([(25,-55,"3/4 view"),(0,0,"from +X (outer face of the plate: dowel hole, slot, pockets)"),(90,-90,"from above (+Z)")]):
    ax=fig.add_subplot(1,3,i+1,projection='3d')
    ax.add_collection3d(Poly3DCollection(V,facecolors=np.c_[np.array([0.29,0.56,0.85])[None,:]*light(V)[:,None],np.ones(len(V))],edgecolor='none'))
    mid=(V.reshape(-1,3).max(0)+V.reshape(-1,3).min(0))/2; r=(V.reshape(-1,3).max(0)-V.reshape(-1,3).min(0)).max()/2
    ax.set_xlim(mid[0]-r,mid[0]+r); ax.set_ylim(mid[1]-r,mid[1]+r); ax.set_zlim(mid[2]-r,mid[2]+r); ax.set_box_aspect((1,1,1)); ax.view_init(el,az); ax.set_axis_off(); ax.set_title(t,fontsize=10)
fig.suptitle("finger_link_tendon v1 (UNTESTED): dowel pass-through added (round hole at the pivot + arc slot above it), rim R9.7",fontsize=11)
plt.tight_layout(rect=[0,0,1,0.93]); plt.savefig(os.path.join(docs,"finger_link_tendon_preview.png"),dpi=100); plt.close()
# ---- routing: side view of the +X plate in 3 poses, with dowel holes and the 3 pin axes
def pol(r,a): a=math.radians(a); return (G[0]+r*math.cos(a),G[1]+r*math.sin(a))
rb=P['R_out']-P['groove_d']; rc=rb+0.5
fig,axs=plt.subplots(1,3,figsize=(18,6.2))
strip_end=np.array([49.2,5.3]); Aext=(-25.4,2.3); Aflex=(-25.4,-14.3)
for ax,(phi,t) in zip(axs,[(10,"extension +10 deg"),(0,"rest 0 deg"),(-70,"flexion -70 deg")]):
    R=lambda y,z,d=phi: (G[0]+(y-G[0])*math.cos(math.radians(d))-(z-G[1])*math.sin(math.radians(d)), G[1]+(y-G[0])*math.sin(math.radians(d))+(z-G[1])*math.cos(math.radians(d)))
    # plate polygon (disc minus wedge) rotated
    a=np.radians(np.linspace(-175,175,200)); a=[x for x in np.degrees(a) if not (P['cut_from']-360<=x<=P['cut_to']-360 or P['cut_from']<=x<=P['cut_to'])]
    ang=np.linspace(P['cut_to']-360,P['cut_from'],220)
    pts=[pol(P['wedge_apex_r'],0.5*(P['cut_from']+P['cut_to']))]
    # wedge edge lines to the rim then arc
    e1=pol(P['R_out'],P['cut_to']-360); 
    poly=[pol(P['R_out'],x) for x in ang]
    outline=[R(*p) for p in poly]+[R(*pol(P['wedge_apex_r'],0.5*(P['cut_from']+P['cut_to'])))]
    ax.add_patch(Polygon(outline,closed=True,fc='#e8c9b5',ec='k',lw=1))
    ax.add_patch(Circle(R(*G),rb,fill=False,ec='#888',ls=':',lw=0.8)); ax.add_patch(Circle(R(*G),rc,fill=False,ec='g',ls='--',lw=0.6))
    # dowel round hole + slot
    ax.add_patch(Circle(R(*G),P['dowel_d']/2,fc='w',ec='#c00',lw=1.2))
    r=6.0; w=P['dowel_d']/2; a0,a1=P['dowel_slot_deg']
    for rr in (r-w,r+w): ax.plot(*zip(*[R(*pol(rr,x)) for x in np.linspace(a0,a1,30)]),color='#c00',lw=1.2)
    for x in (a0,a1): ax.add_patch(Circle(R(*pol(r,x)),w,fill=False,ec='#c00',lw=1.2))
    # pockets
    for psi,c in ((P['psi_flex'],'#1c7ed6'),(P['psi_ext'],'#e8590c')): ax.add_patch(Circle(R(*pol(P['pocket_r'],psi)),P['pocket_d']/2,fc='w',ec=c,lw=1.5))
    # dowel pin axes (fixed in the finger frame)
    ax.plot(*G,'k+',ms=9); ax.plot(0,0,'r+',ms=9)
    ax.annotate("D2x16 pin axis",(0,0),xytext=(-24,6),fontsize=8,color='#c00',arrowprops=dict(arrowstyle='-',color='#c00',lw=.5)); ax.annotate("D2x10 pin axis = pivot",G,xytext=(-24,-24),fontsize=8,color='k',arrowprops=dict(arrowstyle='-',lw=.5))
    # strip
    ax.plot(*zip(R(*G),R(*strip_end)),color='#777',lw=5,alpha=.7,solid_capstyle='round')
    # tendons (schematic: straight from the tube end to the tangent point, wrapped part not drawn)
    def tang(A,side):
        c=np.array(R(*G)); A=np.array(A); d=A-c; D=np.linalg.norm(d); base=math.atan2(d[1],d[0]); aa=math.acos(rc/D)
        cand=[c+rc*np.array([math.cos(base+s*aa),math.sin(base+s*aa)]) for s in (1,-1)]
        return max(cand,key=lambda p:side*p[1])
    for A,side,c in ((Aext,+1,'#e8590c'),(Aflex,-1,'#1c7ed6')):
        T=tang(A,side); ax.plot([A[0],T[0]],[A[1],T[1]],color=c,lw=1.3)
    ax.set_xlim(-30,30); ax.set_ylim(-26,18); ax.set_aspect('equal'); ax.grid(True,alpha=.3); ax.set_title(t); ax.set_xlabel("Y (mm), toward fingertip ->"); ax.set_ylabel("Z (mm), back of finger ^")
axs[0].plot([],[],color='#c00',label='dowel round hole + arc slot (D2.5)'); axs[0].plot([],[],color='#1c7ed6',label='flexor tendon'); axs[0].plot([],[],color='#e8590c',label='extensor tendon'); axs[0].legend(loc='upper right',fontsize=7)
fig.suptitle("finger_link_tendon v1 (UNTESTED) - side view of the +X plate. Pin axes (+) stay fixed while the plate turns: in extension/rest the slot is on the D2x16 axis, the round hole is on the pivot at every angle",fontsize=10)
plt.tight_layout(rect=[0,0,1,0.93]); plt.savefig(os.path.join(docs,"finger_link_tendon_routing.png"),dpi=95); plt.close(); print("ok")
