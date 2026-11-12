# Renders the French assembly drawings of ONE finger (index) on R-Hand_Plate_tendon:
#   docs/assemblage_doigt_eclate_FR.png   exploded view with numbered parts
#   docs/assemblage_coupes_vis_FR.png     3 sections: chosen solution, stock Gimbal + top screw, why an axial screw from below fails
# Usage: python render_assembly_fr.py <folder with the original 'Amazing Hand Parts - *.step'>   (MateBot STEP files are read from ../step)
import sys, os, math, tempfile, importlib.util
import numpy as np, cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d
from stl import mesh
here=os.path.dirname(os.path.abspath(__file__)); MS=os.path.join(here,"..","step"); DOCS=os.path.join(here,"..","docs")
AHD=sys.argv[1] if len(sys.argv)>1 else os.environ.get("MATEBOT_AH_STEP_DIR","/workspace/ah-enh/cad/step")
AH=lambda n: cq.importers.importStep(os.path.join(AHD,f"Amazing Hand Parts - {n}.step"))
MT=lambda n: cq.importers.importStep(os.path.join(MS,n+".step"))
spec=importlib.util.spec_from_file_location("rhp",os.path.join(here,"R-Hand_Plate_tendon.py")); sys.argv=[sys.argv[0],os.path.join(AHD,"Amazing Hand Parts - R-Hand_Plate.step")]
M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M); P=M.P
bu=MT("bushing_d6_flanged"); BP=importlib.util.spec_from_file_location("b",os.path.join(here,"bushing_d6.py")); BM=importlib.util.module_from_spec(BP); BP.loader.exec_module(BM)
plate=MT("R-Hand_Plate_tendon"); shell=MT("R-Palm_Shell_tendon"); gt=MT("Gimbal_tendon"); gstock=AH("Gimbal"); link=MT("finger_link_tendon"); prox=AH("Proximal")
low=bu.translate((0,0,P['blk_z'][0]-BM.P['flange_t'])); high=bu.rotate((0,0,0),(1,0,0),180).translate((0,0,P['blk_z'][1]+BM.P['flange_t']))
z0=P['post_z'][0]; py=P['post_y']
BWP=importlib.util.spec_from_file_location("bw",os.path.join(here,"bushing_washer_d6.py")); BW=importlib.util.module_from_spec(BWP); BWP.loader.exec_module(BW)
washer=BW.place_washer_under(BW.build_washer(),0,py,z0)       # flat printed washer D8 x 0.9 (option 2)
T1=BW.place_top(BW.build(),13.5)                              # printed top-hat bushing-washer (option 1)
head=cq.Workplane("XY").workplane(offset=z0-2.7).center(0,py).circle(2.25).extrude(1.8)
shank=cq.Workplane("XY").workplane(offset=z0-0.9).center(0,py).circle(1.25).extrude(8.0)
screw=head.union(shank)
th=cq.Workplane("XY").workplane(offset=14.4).circle(2.25).extrude(1.8); ts=cq.Workplane("XY").workplane(offset=14.4-8.0).circle(1.25).extrude(8.0); tscrew=th.union(ts)
pin16=cq.Workplane("YZ").workplane(offset=-8.1).circle(1.0).extrude(16.2); pin10=cq.Workplane("YZ").workplane(offset=-5.0).center(0,-6).circle(1.0).extrude(10.0)
tmp=tempfile.mkdtemp()
def crop(s,box):
    b=cq.Workplane("XY").box(*box[:3],centered=False).translate(box[3:]); return cq.Workplane("XY").add(s.val().intersect(b.val()))
plate_c=crop(plate,(34,34,18,-17,-22,-0.5)); shell_c=crop(shell,(48,74,60,-24,-56,-50))
def tri(w):
    f=os.path.join(tmp,"t%d.stl"%abs(hash(str(id(w))))); cq.exporters.export(w if isinstance(w,cq.Workplane) else cq.Workplane("XY").add(w),f,tolerance=0.05,angularTolerance=0.2); return mesh.Mesh.from_file(f).vectors
def light(v,d=np.array([0.4,-0.5,0.8])):
    n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12; d=d/np.linalg.norm(d); return 0.4+0.6*np.clip(n@d,0,1)
# ------------------------------------------------------------ 1. exploded view
# (name, shape, dz explosion, dx, colour, label text)
items=[
 (1,plate_c,0,0,'#9aa5b1',"Plaque R-Hand_Plate_tendon (extrait autour du doigt)\nbloc de pivot Ø8,15 + poteau Ø4,4 + trou pilote Ø1,9",None),
 (2,high,28,0,'#f59f00',"Bague du haut (collerette dans l'encoche de la dalle)\nbushing_d6_flanged",None),
 (3,low,-18,0,'#f59f00',"Bague du bas, collerette vers le bas\nbushing_d6_flanged",None),
 (4,gt,-40,0,'#228be6',"Gimbal_tendon (languette + fente en arc Ø5)\n(ou Gimbal d'origine, voir la coupe B)",None),
 (5,washer,-70,0,'#868e96',"Rondelle plate imprimée Ø8 x 0,9 (washer_d8_printed)\nremplace la rondelle M2.5 ; option 2 seulement",None),
 (6,screw,-84,0,'#343a40',"Vis thermoplastique 2.5 x 8, par en dessous,\ndans le trou pilote du poteau",None),
 (7,link,-52,0,'#be4bdb',"finger_link_tendon",None),
 (9,shell_c,-118,0,'#c8d0d8',"Coque de paume R-Palm_Shell_tendon\n(posée en dernier)",None),
]
pins=[(8,pin16,-40,22,'#e03131',""),(8,pin10,-52,22,'#e03131',"")]
fig=plt.figure(figsize=(17,11.5)); ax=fig.add_axes([0.0,0.0,0.62,1.0],projection='3d')
allv=[]; anchors={}
for n,s,dz,dx,c,txt,pos in items:
    w=s if isinstance(s,cq.Workplane) else cq.Workplane("XY").add(s)
    V=tri(w); V=V+np.array([dx,0,dz]); allv.append(V)
    cc=np.array(matplotlib.colors.to_rgb(c))[None,:]*light(V)[:,None]
    ax.add_collection3d(Poly3DCollection(V,facecolors=np.c_[cc,np.full(len(V),0.97 if n!=9 else 0.35)],edgecolor='none'))
    anchors[n]=V.reshape(-1,3).mean(0)
for n,s,dz,dx,c,txt in pins:
    V=tri(cq.Workplane("XY").add(s.val() if isinstance(s,cq.Workplane) else s))+np.array([dx,0,dz]); allv.append(V)
    cc=np.array(matplotlib.colors.to_rgb(c))[None,:]*light(V)[:,None]; ax.add_collection3d(Poly3DCollection(V,facecolors=np.c_[cc,np.ones(len(V))],edgecolor='none'))
    anchors[(n,dz)]=V.reshape(-1,3).mean(0); anchors[8]=anchors[(n,dz)]
A=np.vstack(allv).reshape(-1,3); lo=A.min(0); hi=A.max(0); mid=(lo+hi)/2; r=(hi-lo).max()/2*0.72
ax.set_xlim(mid[0]-r,mid[0]+r); ax.set_ylim(mid[1]-r,mid[1]+r); ax.set_zlim(mid[2]-r,mid[2]+r); ax.set_box_aspect((1,1,1)); ax.view_init(14,-62); ax.set_axis_off()
ax.plot([0,0],[0,0],[-80,40],'k--',lw=0.8)
fig.canvas.draw()
def to2d(p):
    x,y,_=proj3d.proj_transform(p[0],p[1],p[2],ax.get_proj()); return ax.transData.transform((x,y))
inv=fig.transFigure.inverted()
labels=[(n,txt) for n,_,_,_,_,txt,_ in items]
rows=[(1,items[0][5]),(2,items[1][5]),(3,items[2][5]),(4,items[3][5]),(7,items[6][5]),(8,"Axes (dowels) D2x10 et D2x16\n(à glisser après avoir monté le Link)"),(5,items[4][5]),(6,items[5][5]),(9,items[7][5])]
ys=np.linspace(0.93,0.07,len(rows))
for (n,txt),y in zip(rows,ys):
    a=anchors[n]
    p=inv.transform(to2d(a)); fig.add_artist(plt.Line2D([p[0],0.64],[p[1],y],color='#555',lw=0.9))
    fig.text(0.64,y,f" {n} ",fontsize=15,fontweight='bold',color='white',va='center',bbox=dict(boxstyle='circle,pad=0.25',fc='#1c7ed6',ec='none'))
    fig.text(0.67,y,txt,fontsize=12.5,va='center')
fig.text(0.02,0.975,"MateBot - un doigt sur la plaque R-Hand_Plate_tendon v6 - vue éclatée (non à l'échelle, éclatement le long de l'axe Z du pivot)",fontsize=14,fontweight='bold',va='top')
fig.text(0.02,0.015,"Proximal, Distal et leurs coques ne sont pas représentés. Gimbal_tendon : Gimbal avec languette (vissage par en dessous). Le poteau (Ø4,4) de la plaque traverse la fente de la languette ;\nla rondelle imprimée (Ø8) recouvre la languette de 1,5 mm de chaque côté de la fente. Vue générée par la CAO ; non testé à l'impression.",fontsize=10.5,va='bottom')
fig.savefig(os.path.join(DOCS,"assemblage_doigt_eclate_FR.png"),dpi=110); plt.close(fig)
# ------------------------------------------------------------ 2. sections
def tris(s,axis,val,th_=0.02):
    sl={'x':lambda:cq.Workplane("XY").box(th_,400,400).translate((val,0,0)),'y':lambda:cq.Workplane("XY").box(400,th_,400).translate((0,val,0))}[axis]()
    proj=(lambda v:(v.y,v.z)) if axis=='x' else (lambda v:(v.x,v.z))
    r=cq.Workplane("XY").add(s.val() if isinstance(s,cq.Workplane) else s).intersect(sl); out=[]
    for fc in r.faces().vals():
        n=fc.normalAt()
        if abs(n.x if axis=='x' else n.y)<0.9: continue
        vs,ts_=fc.tessellate(0.05); out+=[[proj(vs[i]) for i in t] for t in ts_]
    return out
def draw(ax,parts,axis,val):
    for s,c,a in parts:
        for t in tris(s,axis,val): ax.add_patch(Polygon(t,closed=True,fc=c,ec=c,lw=0.25,alpha=a))
fig,axs=plt.subplots(1,3,figsize=(24,11))
base=[(plate,'#9aa5b1',0.9),(high,'#f59f00',1),(low,'#f59f00',1)]
# A chosen: Gimbal_tendon + screw from below (plane X=0: Y horizontal, Z vertical)
ax=axs[0]; draw(ax,base+[(gt,'#228be6',1),(washer,'#868e96',1),(screw,'#343a40',1)],'x',0)
ax.set_xlim(-24,12); ax.set_ylim(-13,31); ax.set_title("A. Retenue : Gimbal_tendon, vis par en dessous\n(coupe X=0 ; Y horizontal, Z vertical, mm)",fontsize=14)
def note(ax,xy,xyt,t,c='k'): ax.annotate(t,xy,xyt,fontsize=11,color=c,arrowprops=dict(arrowstyle='->',color=c))
note(ax,(-8.6,6),(-23.5,29),"poteau Ø4,4 de la plaque")
note(ax,(-8.6,2),(-23.5,25.5),"languette du Gimbal_tendon (fente en arc Ø5, ±25°)")
note(ax,(-8.6,4.5),(-23.5,22),"vis 2.5x8 : 7,1 mm de filet dans le poteau (pilote Ø1,9)")
note(ax,(0,16),(-4,29),"pivot du Gimbal Ø6\n+ 2 bagues")
note(ax,(-8.6,-0.3),(-23.5,-9),"rondelle imprimée Ø8 x 0,9 : retient la languette\n(0,4 mm sous la languette, ne la serre pas)")
note(ax,(-8.6,-2.4),(-23.5,-12),"tête de vis (Ø4,5), accessible par en dessous")
ax=axs[1]; draw(ax,[(plate,'#9aa5b1',0.9),(low,'#f59f00',1),(gstock,'#4dabf7',1),(T1,'#e64980',1),(tscrew,'#343a40',1)],'x',0)
ax.set_xlim(-14,14); ax.set_ylim(-3,31); ax.set_title("B. Sans réimpression : Gimbal d'origine + vis par le dessus + bague-rondelle\n(trou existant du bout Ø1,9, coupe X=0)",fontsize=14)
note(ax,(0,15.5),(-13.5,28),"bague-rondelle imprimée (rose, bushing_washer_d6) :\ndisque Ø10 x 0,9 serré par la vis 2.5x8 sur le bout du pivot,\nmanchon dans l'alésage (remplace la bague du haut)\nvis dans le trou du bout (Ø1,9, ~8,5 mm, borgne) : 7,1 mm de filet")
ax.text(-13.5,-1.8,"il faut retirer R-Top_Shell (dos de la main) pour serrer la vis",fontsize=11,color='#c92a2a')
ax=axs[2]; draw(ax,[(plate,'#9aa5b1',0.9),(high,'#f59f00',1),(low,'#f59f00',1),(gstock,'#4dabf7',1),(prox,'#8ce99a',0.9),(link,'#be4bdb',0.9),(pin16,'#e03131',1),(pin10,'#e03131',1)],'y',0)
ax.add_patch(Rectangle((-1.25,-2.3),2.5,7.2,fc='none',ec='#c92a2a',lw=2,ls='--'))
ax.add_patch(Circle((0,-4.5),2.25,fc='none',ec='#c92a2a',lw=2,ls='--'))
ax.set_xlim(-16,16); ax.set_ylim(-18,31); ax.set_title("C. Idée « vis dans l'axe par en dessous » : impossible\n(coupe Y=0 ; X horizontal, Z vertical)",fontsize=14)
note(ax,(0,0),(-15.5,28),"l'axe D2x16 (rouge) traverse l'axe du pivot : la vis\n(pointillés) devrait le couper sur 2 mm",'#c92a2a')
note(ax,(0,-4.5),(-15.5,-14),"sous le Gimbal, la tête de vis est sur le passage du Link\n(11 à 32 mm³ de collision selon l'angle)",'#c92a2a')
note(ax,(0,5.2),(-15.5,22),"le trou d'origine est borgne : ouvert en haut seulement,\nfond à Z≈4,9 ; du bas il faudrait percer 3,9 mm de plus (Z 1,1 à 4,9)")
for ax in axs: ax.set_aspect('equal'); ax.grid(alpha=.3); ax.tick_params(labelsize=9)
fig.suptitle("MateBot v8 - chemin de la vis (finger frame = repère de la plaque ; gris : plaque, orange : bagues, bleu : Gimbal, violet : Link, vert : Proximal, rouge : axes)",fontsize=14,y=0.995)
plt.tight_layout(rect=[0,0,1,0.97]); fig.savefig(os.path.join(DOCS,"assemblage_coupes_vis_FR.png"),dpi=80); plt.close(fig); print("ok")
