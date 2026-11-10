# Renders the previews of R-Hand_Plate_tendon.  Usage: python render_plate_tendon.py <R-Hand_Plate.step>  (needs CadQuery, numpy-stl, matplotlib)
import sys, os, math, importlib.util, tempfile
import numpy as np, cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh
here=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("rhp",os.path.join(here,"R-Hand_Plate_tendon.py")); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
P=M.P
new,orig,info=M.build(); added=new.cut(orig)
tmp=tempfile.mkdtemp()
def tri(shape,name):
    f=os.path.join(tmp,name+".stl"); cq.exporters.export(cq.Workplane("XY").add(shape),f,tolerance=0.05,angularTolerance=0.2); return mesh.Mesh.from_file(f).vectors
Vn=tri(new.val(),"new"); Va=tri(added.val(),"added")
def light(v,d=np.array([0.4,-0.5,0.8])):
    n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12; d=d/np.linalg.norm(d); return 0.35+0.65*np.clip(n@d,0,1)
def added_mask(V):
    """True for triangles whose centroid lies inside one of the (slightly grown) anchor columns"""
    g=info['g']; cen=V.mean(1); m=np.zeros(len(V),bool)
    for f in M.FINGERS:
        t=math.radians(f['th']); c,s_=math.cos(t),math.sin(t)
        d=cen[:,:2]-np.array(f['c']); xf=d[:,0]*c+d[:,1]*s_; yf=-d[:,0]*s_+d[:,1]*c
        for sd in (-1,1):
            xs=sd*P['x_in']; hw=P['col_hw']+0.3
            m|=(abs(xf-xs)<hw)&(yf>g['y_back']-0.3)&(yf<g['y_front']+0.3)&(cen[:,2]<P['col_top']+0.1)&(cen[:,2]>P['z_flex']-P['col_bot_margin']-0.5)
    return m
def draw3d(ax,V,base='#9aa5b1',hi='#d9480f'):
    m=added_mask(V); print("added triangles",int(m.sum()),"of",len(V)); sh=light(V)[:,None]
    c=np.where(m[:,None],np.array(matplotlib.colors.to_rgb(hi))[None,:],np.array(matplotlib.colors.to_rgb(base))[None,:])*sh
    order=None
    ax.add_collection3d(Poly3DCollection(V,facecolors=np.c_[c,np.ones(len(V))],edgecolor='none'))
def tube_lines():
    out=[]
    g=info['g']
    for f in M.FINGERS:
        t=math.radians(f['th'])
        def P3(x,y,z): return (f['c'][0]+x*math.cos(t)-y*math.sin(t), f['c'][1]+x*math.sin(t)+y*math.cos(t), z)
        for s in (-1,1):
            for nm,z in (("ext",P['z_ext']),("flex",P['z_flex'])):
                xs=s*P['x_in']; xc=s*P['capstan_x']
                out.append(dict(kind=nm,tendon=[P3(xs,g['y_front'],z),P3(xc,0,z)],tube=[P3(xs,g['y_back'],z),P3(xs,-85,z)],cap=P3(xc,0,z)))
    return out
L=tube_lines()
col={'ext':'#e8590c','flex':'#1c7ed6'}
# 1 overview (3 views)
fig=plt.figure(figsize=(15,5.2))
for i,(el,az,t) in enumerate([(35,-60,"3/4 view from the palm side"),(-35,-120,"under (palm) side"),(90,-90,"from the back (top)")]):
    ax=fig.add_subplot(1,3,i+1,projection='3d'); draw3d(ax,Vn)
    allv=Vn.reshape(-1,3); mid=(allv.max(0)+allv.min(0))/2; r=(allv.max(0)-allv.min(0)).max()/2
    ax.set_xlim(mid[0]-r,mid[0]+r); ax.set_ylim(mid[1]-r,mid[1]+r); ax.set_zlim(mid[2]-r,mid[2]+r); ax.set_box_aspect((1,1,1)); ax.view_init(el,az); ax.set_axis_off(); ax.set_title(t,fontsize=10)
fig.suptitle("R-Hand_Plate_tendon (v0 UNTESTED) - grey: original Pollen plate, orange: MateBot anchor columns, PTFE sockets and reliefs",fontsize=11)
plt.tight_layout(rect=[0,0,1,0.92]); plt.savefig(os.path.join(here,"..","docs","R-Hand_Plate_tendon_preview.png"),dpi=110); plt.close()
# 2 tube / tendon lines: top view + two side sections
fig,axs=plt.subplots(1,2,figsize=(16,7.5),gridspec_kw=dict(width_ratios=[1.35,1]))
ax=axs[0]
ord_=np.argsort(Vn[:,:,2].mean(1)); 
ax.add_collection(PolyCollection(Vn[ord_][:,:,:2],facecolors=[(*(np.array((0.6,0.65,0.7))*l),1) for l in light(Vn[ord_])],edgecolor='none'))
oa=np.argsort(Va[:,:,2].mean(1)); ax.add_collection(PolyCollection(Va[oa][:,:,:2],facecolors=[(*(np.array((0.85,0.28,0.06))*l),0.9) for l in light(Va[oa])],edgecolor='none'))
for l in L:
    c=col[l['kind']]; t=np.array(l['tendon']); u=np.array(l['tube'])
    ax.plot(t[:,0],t[:,1],'-',color=c,lw=1.6); ax.plot(u[:,0],u[:,1],'--',color=c,lw=1.6)
for f in M.FINGERS:
    ax.plot(*f['c'],'k+',ms=12); ax.annotate(f['name'],f['c'],xytext=(4,6),textcoords='offset points',fontsize=9)
ax.plot([],[],'-',color=col['ext'],label='extensor tendon (Z=+2.3)'); ax.plot([],[],'-',color=col['flex'],label='flexor tendon (Z=-14.3)'); ax.plot([],[],'k--',label='PTFE tube path (D4)')
ax.legend(loc='lower left',fontsize=9); ax.set_xlim(-20,82); ax.set_ylim(-92,12); ax.set_aspect('equal'); ax.grid(True,alpha=.3); ax.set_title("Top view (X right, Y toward fingertips): tendons from the capstans back to the PTFE sockets")
# side view of index finger lines in the index frame
ax=axs[1]
sl=lambda x: None
shapeY=[]
f=M.FINGERS[0]
for sgn,cc in ((1,'#555'),):
    pass
# section of the new plate at X = +10.5 (index +, finger frame = plate frame)
for shp,cl in ((new,'k'),):
    sec=new.intersect(cq.Workplane("XY").box(0.02,300,300).translate((P['x_in'],-50,0)))
    for e in sec.edges().vals():
        if e.BoundingBox().xlen<0.02:
            pts=e.positions(list(np.linspace(0,1,30))); a=np.array([(p.y,p.z) for p in pts]); ax.plot(a[:,0],a[:,1],cl,lw=1)
g=info['g']
for z,c,nm in ((P['z_ext'],col['ext'],'extensor'),(P['z_flex'],col['flex'],'flexor')):
    ax.plot([g['y_front'],0],[z,z],'-',color=c,lw=1.8); ax.plot([g['y_back']-1,-85],[z,z],'--',color=c,lw=1.8)
    ax.text(-78,z+1.2,nm,color=c,fontsize=9)
ax.add_patch(plt.Circle((0,-6),P['capstan_r'],fill=False,color='g',lw=1)); ax.annotate("capstan R8.3",(0,-6),xytext=(8,-6),fontsize=8,color='g')
ax.axvline(g['y_stop'],color='gray',lw=0.6,ls=':'); ax.text(g['y_stop']-0.5,16.5,"tube end\n(Y=-30)",fontsize=8,ha='right')
ax.set_xlim(-90,12); ax.set_ylim(-24,20); ax.set_aspect('equal'); ax.grid(True,alpha=.3); ax.set_title("Index finger, side section at X=+10.5 (Y toward tips, Z up = back of hand)")
plt.tight_layout(); plt.savefig(os.path.join(here,"..","docs","R-Hand_Plate_tendon_routing.png"),dpi=100); plt.close()
print("ok")
