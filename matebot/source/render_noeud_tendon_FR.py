# Renders docs/noeud_tendon_etapes_FR.png : step-by-step drawing (French) of how to attach the braided line to the
# capstan plates of finger_link_tendon.  The parts come from the CAD files in ../step (finger_link_tendon, R-Hand_Plate_tendon);
# the line routes (tangent, wrap, Ø1.2 channel, pocket) are computed with the SAME numbers as finger_link_tendon.py (P dict) and
# checked against the solid (no route point is inside the material).  The line is drawn thicker than a real braid (diameter not measured).
# Usage (needs CadQuery + VTK, offscreen):  xvfb-run -a python render_noeud_tendon_FR.py
import os, sys, math, tempfile, numpy as np
import cadquery as cq, vtk, vtk.util.numpy_support
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, Wedge
here=os.path.dirname(os.path.abspath(__file__)); STEP=os.path.join(here,"..","step"); DOCS=os.path.join(here,"..","docs")
OUT=os.path.join(DOCS,"noeud_tendon_etapes_FR.png")
# ---------------------------------------------------------------- numbers of finger_link_tendon.py (P) and R-Hand_Plate_tendon.py
G2=(0.0,-6.0)                 # Link pivot (Y,Z)
R_RIM=9.7; GROOVE_W=1.4; GROOVE_D=1.2; R_C=R_RIM-GROOVE_D+0.5      # tendon centre radius 9.0
X0=12.0; T=2.4; XM=X0+T/2; X1=X0+T                                   # plate X 12.0..14.4
POCKET_R=5.2; POCKET_D=3.2; POCKET_DEPTH=2.0; RHO=3.0; CHAN_D=1.2
PSI={'flex':-15.0,'ext':35.0}; SGN={'flex':-1,'ext':+1}
X_SOCK=10.5; Y_SOCK=-30.0; Y_CONE=-25.4; ZS={'flex':-12.8,'ext':2.3}  # sockets of R-Hand_Plate_tendon (finger frame)
CA=(0.91,0.35,0.05); CB=(0.11,0.44,0.81); COL={'flex':CA,'ext':CB}     # servo A orange, servo B blue
PLATE=(0.60,0.65,0.72); COLUMN=(0.80,0.82,0.86); LINKC=(0.72,0.75,0.80); TUBEC=(0.78,0.86,0.93); LR=0.30
def pol(r,psi): a=math.radians(psi); return (G2[0]+r*math.cos(a), G2[1]+r*math.sin(a))
def tangent(kind):
    ey,ez=Y_SOCK,ZS[kind]; dy,dz=ey-G2[0],ez-G2[1]; d=math.hypot(dy,dz); phi=math.degrees(math.atan2(dz,dy)); da=math.degrees(math.acos(R_C/d))
    c=[(a+180)%360-180 for a in (phi+da,phi-da)]; tgt=-90 if kind=='flex' else 90
    return min(c,key=lambda a:abs(((a-tgt)+180)%360-180))
def route(kind):
    psi=PSI[kind]; sgn=SGN[kind]; rp=POCKET_R; rcc=R_C-RHO
    dpsi=math.degrees(math.acos((rp**2+rcc**2-RHO**2)/(2*rp*rcc))); psiQ=psi+sgn*dpsi; psiT=tangent(kind)
    d=((psiQ-psiT+180)%360)-180
    wrap=[(XM,)+pol(R_C,psiT+d*i/60) for i in range(61)]; Tp=wrap[0]; Qp=wrap[-1]
    ys=np.linspace(Y_SOCK-8,Tp[1],50); lead=[]
    for y in ys:
        t=(y-Y_SOCK)/(Tp[1]-Y_SOCK); lead.append((X_SOCK+min(max(t,0),1)*(XM-X_SOCK), y, ZS[kind]+t*(Tp[2]-ZS[kind])))
    Py,Pz=pol(rp,psi); Cy,Cz=pol(rcc,psiQ)
    aQ=math.atan2(Qp[2]-Cz,Qp[1]-Cy); aP=math.atan2(Pz-Cz,Py-Cy); da=(aP-aQ+math.pi)%(2*math.pi)-math.pi
    chan=[(XM,Cy+RHO*math.cos(aQ+da*i/30),Cz+RHO*math.sin(aQ+da*i/30)) for i in range(31)]
    return dict(lead=lead,wrap=wrap,chan=chan,P=(XM,Py,Pz),Q=Qp,T=Tp,psiQ=psiQ,psiT=psiT,wrap_deg=abs(d))
FL=route('flex'); EX=route('ext')
# ---------------------------------------------------------------- CAD crops -> STL
tmp=tempfile.mkdtemp()
def crop(s,x0,x1,y0,y1,z0,z1): return s.intersect(cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)))
def exp(s,n): f=os.path.join(tmp,n); cq.exporters.export(s,f,tolerance=0.01,angularTolerance=0.1); return f
link=cq.importers.importStep(os.path.join(STEP,"finger_link_tendon.step")); plate=cq.importers.importStep(os.path.join(STEP,"R-Hand_Plate_tendon.step"))
F_PLATE=exp(crop(link,11.95,14.5,-14,14,-20,8),"plateP.stl"); F_LINK=exp(crop(link,-15,15,-14,14,-20,8),"linkc.stl")
F_COL=exp(crop(plate,4.5,16,-42,-20,-18,6),"col.stl")
# check: no route point lies inside the Link solid (groove, channel and pocket are real voids)
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
_sol=link.val().wrapped
def inside(p): return BRepClass3d_SolidClassifier(_sol,gp_Pnt(*p),1e-6).State()==TopAbs_IN
for k,r in (('flex',FL),('ext',EX)):
    nin=sum(inside(p) for p in r['wrap']+r['chan']+[r['P']]); print("route",k,": points inside the material:",nin,"| wrap %.0f deg"%r['wrap_deg']); assert nin==0
# ---------------------------------------------------------------- VTK helpers
def stl_actor(path,color,opacity=1.0):
    r=vtk.vtkSTLReader(); r.SetFileName(path); r.Update(); n=vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(35); n.SplittingOn(); n.Update()
    m=vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort()); m.ScalarVisibilityOff(); a=vtk.vtkActor(); a.SetMapper(m); p=a.GetProperty()
    p.SetColor(*color); p.SetOpacity(opacity); p.SetSpecular(0.25); p.SetSpecularPower(25); p.SetAmbient(0.25); p.SetDiffuse(0.8); return a
def tube_actor(pts,radius,color,sides=14,opacity=1.0):
    vp=vtk.vtkPoints(); [vp.InsertNextPoint(*p) for p in pts]; pl=vtk.vtkPolyLine(); pl.GetPointIds().SetNumberOfIds(len(pts)); [pl.GetPointIds().SetId(i,i) for i in range(len(pts))]
    ca=vtk.vtkCellArray(); ca.InsertNextCell(pl); pd=vtk.vtkPolyData(); pd.SetPoints(vp); pd.SetLines(ca)
    t=vtk.vtkTubeFilter(); t.SetInputData(pd); t.SetRadius(radius); t.SetNumberOfSides(sides); t.CappingOn(); t.Update()
    m=vtk.vtkPolyDataMapper(); m.SetInputConnection(t.GetOutputPort()); m.ScalarVisibilityOff(); a=vtk.vtkActor(); a.SetMapper(m); p=a.GetProperty()
    p.SetColor(*color); p.SetSpecular(0.4); p.SetSpecularPower(30); p.SetAmbient(0.35); p.SetOpacity(opacity); return a
def sphere_actor(c,r,color,opacity=1.0):
    s=vtk.vtkSphereSource(); s.SetCenter(*c); s.SetRadius(r); s.SetThetaResolution(40); s.SetPhiResolution(40); m=vtk.vtkPolyDataMapper(); m.SetInputConnection(s.GetOutputPort())
    a=vtk.vtkActor(); a.SetMapper(m); p=a.GetProperty(); p.SetColor(*color); p.SetOpacity(opacity); p.SetSpecular(0.9); p.SetSpecularPower(90); return a
class Scene:
    def __init__(s,W=1000,H=750):
        s.W,s.H=W,H; s.ren=vtk.vtkRenderer(); s.ren.SetBackground(1,1,1); s.win=vtk.vtkRenderWindow(); s.win.SetOffScreenRendering(1); s.win.AddRenderer(s.ren); s.win.SetSize(W,H); s.win.SetMultiSamples(8)
    def add(s,a): s.ren.AddActor(a)
    def camera(s,focal,direction,up,scale):
        d=np.asarray(direction,float); d/=np.linalg.norm(d); f=np.asarray(focal,float); c=s.ren.GetActiveCamera(); c.ParallelProjectionOn()
        c.SetFocalPoint(*f); c.SetPosition(*(f+d*300)); c.SetViewUp(*up); c.SetParallelScale(scale); c.SetClippingRange(1,700); s.ren.RemoveAllLights()
        for dv,i in (((0.5,0.35,0.8),0.9),((-0.6,-0.2,0.5),0.35)):
            l=vtk.vtkLight(); l.SetLightTypeToCameraLight(); l.SetPosition(*dv); l.SetFocalPoint(0,0,0); l.SetIntensity(i); s.ren.AddLight(l)
    def render(s):
        s.win.Render(); w=vtk.vtkWindowToImageFilter(); w.SetInput(s.win); w.ReadFrontBufferOff(); w.Update()
        return vtk.util.numpy_support.vtk_to_numpy(w.GetOutput().GetPointData().GetScalars()).reshape(s.H,s.W,-1)[::-1,:,:3].copy()
    def proj(s,p):
        c=vtk.vtkCoordinate(); c.SetCoordinateSystemToWorld(); c.SetValue(*p); v=c.GetComputedDoubleDisplayValue(s.ren); return (v[0],s.H-v[1])
def knot3d(center,toward,scale=0.40):
    th=np.linspace(0.35,4*math.pi-0.35,400); R=2+np.cos(2.5*th); loc=np.c_[R*np.cos(th),R*np.sin(th),0.9*np.sin(2.5*th)]*scale
    ang=math.atan2(toward[1],toward[0]); ca,sa=math.cos(ang),math.sin(ang)
    return [(center[0]+w,center[1]+ca*u-sa*v,center[2]+sa*u+ca*v) for u,v,w in loc]
def tail_pts(r,kind,L=10.0):
    P=r['P']; a=math.radians(PSI[kind]); ur=(math.cos(a),math.sin(a)); pts=[P]+[(P[0]+i*0.4,P[1],P[2]) for i in range(1,8)]; x=P[0]+2.8; rem=L-2.8
    pts+=[(x+0.3*(1-math.exp(-i/2.0)),P[1]+ur[0]*rem*i/12,P[2]+ur[1]*rem*i/12) for i in range(1,13)]; return pts
def mirror(pts): return [(-x,y,z) for x,y,z in pts]
DIR=(1,0.40,0.20); FOC=(13.2,-3.5,-6); SC=12.2
imgs={}; proj={}
def plate_scene(xray,column=False,tubes=False,focal=FOC,direction=DIR,scale=SC):
    sc=Scene(); sc.add(stl_actor(F_PLATE,PLATE,0.40 if xray else 1.0))
    if column: sc.add(stl_actor(F_COL,COLUMN))
    sc.camera(focal,direction,(0,0,1),scale); return sc
# 1 : the line leaves the socket
sc=plate_scene(False,column=True,focal=(10,-8,-5),direction=(1.0,1.0,0.25),scale=21)
for k,r in (('flex',FL),('ext',EX)): sc.add(tube_actor([(X_SOCK,-36,ZS[k])]+r['lead'],LR,COL[k]))
imgs[1]=sc.render(); proj[1]=sc.proj
# 2 : wrap in the groove (plate seen through)
sc=plate_scene(True)
for k,r in (('flex',FL),('ext',EX)): sc.add(tube_actor(r['lead'][-26:]+r['wrap'],LR+0.04,COL[k]))
imgs[2]=sc.render(); proj[2]=sc.proj
# 3 : Ø1.2 channel, out of the pocket
sc=plate_scene(True)
for k,r in (('flex',FL),('ext',EX)):
    P=r['P']; a=math.radians(PSI[k]); ur=(math.cos(a),math.sin(a)); end=[(P[0]+0.9*i,P[1]+0.07*i*i*ur[0]*0.25,P[2]+0.07*i*i*ur[1]*0.25) for i in range(1,17)]
    sc.add(tube_actor(r['lead'][-26:]+r['wrap']+r['chan']+end,LR+0.04,COL[k]))
imgs[3]=sc.render(); proj[3]=sc.proj
# 5 : knot at the bottom of the pocket, 10 mm tail, glue drop
sc=plate_scene(False,focal=(13.2,1.0,-5.2),scale=8.6)
for k,r in (('flex',FL),('ext',EX)):
    P=r['P']; a=math.radians(PSI[k]); sc.add(tube_actor(knot3d((X0+1.55,P[1],P[2]),(math.cos(a+math.pi),math.sin(a+math.pi))),0.2,COL[k],12)); sc.add(tube_actor(tail_pts(r,k),0.2,COL[k],12))
    sc.add(sphere_actor((X1-0.25,P[1],P[2]),1.35,(1.0,0.93,0.55),0.45))
imgs[5]=sc.render(); proj[5]=sc.proj
# 6 : overview from behind, both plates, 4 line ends (+X: flexor A, extensor B ; -X: flexor B, extensor A)
sc=Scene(); sc.add(stl_actor(F_LINK,LINKC))
for k in ('flex','ext'):
    for sx in (X_SOCK,-X_SOCK): sc.add(tube_actor([(sx,-38,ZS[k]),(sx,Y_SOCK,ZS[k])],2.0,TUBEC,40))
for k,r in (('flex',FL),('ext',EX)):
    o='ext' if k=='flex' else 'flex'; full=[(X_SOCK,-36,ZS[k])]+r['lead']+r['wrap']+r['chan']
    sc.add(tube_actor(full,LR*1.2,COL[k])); sc.add(tube_actor(mirror(full),LR*1.2,COL[o]))
sc.camera((0,-10,-5),(0.55,-1.0,0.75),(0,0,1),26); imgs[6]=sc.render(); proj[6]=sc.proj
# 7 : finger straight, side view, tight lines
sc=Scene(); sc.add(stl_actor(F_PLATE,PLATE))
for k in ('flex','ext'): sc.add(tube_actor([(X_SOCK,-38,ZS[k]),(X_SOCK,Y_SOCK,ZS[k])],2.0,TUBEC,40))
for k,r in (('flex',FL),('ext',EX)): sc.add(tube_actor([(X_SOCK,-36,ZS[k])]+r['lead']+r['wrap'][:2],LR+0.04,COL[k]))
sc.camera((8,-9,-6),(1,0.0,0.0),(0,0,1),20); imgs[7]=sc.render(); proj[7]=sc.proj
# ---------------------------------------------------------------- figure
import textwrap
imgs[7]=imgs[7][135:585]; _p7=proj[7]; proj[7]=lambda q:(_p7(q)[0],_p7(q)[1]-135)      # crop the side view to a wide strip
BG='#ffffff'; INK='#1f2933'; GREY='#667788'
FW,FH=24.0,26.0; ML=0.35; GAP=0.30; CW=(FW-2*ML-2*GAP)/3; HEAD=1.75; ROWH=7.85; TITLE=0.55; IMGH=CW*0.75
fig=plt.figure(figsize=(FW,FH),dpi=100); fig.patch.set_facecolor(BG)
def wrap(t,w): return "\n".join(textwrap.fill(p,w) for p in t.split("\n"))
def panel(c,r,num,title,cap,img=None,span=1,capw=62):
    left=ML+c*(CW+GAP); wdt=span*CW+(span-1)*GAP; bottom=FH-HEAD-r*ROWH-TITLE-IMGH
    ax=fig.add_axes([left/FW,bottom/FH,wdt/FW,IMGH/FH]); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_edgecolor('#9aa5b1'); sp.set_linewidth(1.5)
    if img is not None: ax.imshow(img,aspect='auto'); ax.set_xlim(0,img.shape[1]); ax.set_ylim(img.shape[0],0)
    ytitle=(bottom+IMGH+TITLE/2)/FH
    fig.text((left+0.58)/FW,ytitle,title,fontsize=19,fontweight='bold',color=INK,va='center')
    fig.text((left+0.17)/FW,ytitle,str(num),fontsize=22,fontweight='bold',color='white',ha='center',va='center',bbox=dict(boxstyle='circle,pad=0.28',fc='#1c7ed6',ec='none'))
    if cap: fig.text(left/FW,(bottom-0.12)/FH,wrap(cap,capw*span),fontsize=14,va='top',ha='left',color=INK,linespacing=1.35)
    return ax
def note(ax,txt,xy,xyt,color=INK,fs=14,ha='left',bold=False):
    ax.annotate(txt,xy,xyt,fontsize=fs,color=color,ha=ha,va='center',fontweight='bold' if bold else 'normal',annotation_clip=False,
        arrowprops=dict(arrowstyle='-|>',color=color,lw=1.6,shrinkA=2,shrinkB=3),bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='none',alpha=0.88))
def cross(ax,xy,s=22):
    ax.plot([xy[0]-s,xy[0]+s],[xy[1]-s,xy[1]+s],color='#e03131',lw=4); ax.plot([xy[0]-s,xy[0]+s],[xy[1]+s,xy[1]-s],color='#e03131',lw=4)
face=lambda y,z: (X1,y,z)
# --- 1
ax=panel(0,0,1,"La ligne sort du logement","Passe la tresse dans le trou Ø2,2 du logement de la plaque (côté doigt : cône Ø2,2 → Ø5,0) et tire-la vers la plaque du Link. Fléchisseur = logement du bas (orange), extenseur = logement du haut (bleu). La gaine PTFE est butée à Y = −30 dans le logement.",imgs[1]); p=proj[1]
note(ax,"trou Ø2,2 + cône\nfléchisseur (bas)",p((X_SOCK,Y_CONE,ZS['flex'])),(40,640),CA,bold=True)
note(ax,"logement de la gaine PTFE\n(colonne d'ancrage de la plaque)",p((X_SOCK,-31,-4)),(40,60),INK)
note(ax,"tangente haute (Z +3,0)\nextenseur (haut)",p((13.2,-0.2,3.0)),(590,60),CB,bold=True)
note(ax,"tangente basse (Z −15,0)",p((13.2,-0.7,-15.0)),(560,710),CA,bold=True)
# --- 2
ax=panel(1,0,2,"Enroule dans la gorge","Pose la ligne dans la gorge en U (largeur 1,4 mm, fond à R8,5, jante R9,7) : elle tourne sur R9,0 comme sur un cabestan. Fléchisseur : environ %.0f° (du bas vers le bout du doigt), extenseur : environ %.0f° (du haut vers le bout du doigt). Arrête-toi à l'entrée du canal Ø1,2 (point jaune)."%(FL['wrap_deg'],EX['wrap_deg']),imgs[2]); p=proj[2]
note(ax,"gorge en U\n(1,4 mm de large)",p((XM,)+pol(R_C,200)),(40,560),INK)
note(ax,"jante R9,7",p((X1,)+pol(R_RIM,120)),(470,40),INK)
for r in (FL,EX): ax.plot(*p(r['Q']),'o',ms=15,mfc='#ffd43b',mec='k',mew=2,zorder=5)
cross(ax,p(face(*G2))); cross(ax,p(face(*pol(6.0,100))))
note(ax,"NE PAS utiliser :\ntrou et fente Ø2,5 (axes)",p(face(*pol(6.0,100))),(40,200),'#e03131',bold=True)
# --- 3
ax=panel(2,0,3,"Passe dans le canal Ø1,2, sors par la poche","Au point jaune la ligne entre dans le canal Ø1,2 (courbe de rayon 3 mm) et débouche dans la poche Ø3,2 × 2,0 mm, ouverte sur la face extérieure. Sors le bout par la poche : prévois de quoi faire le nœud + 10 mm de queue. Fléchisseur : poche du bas ; extenseur : poche du haut.",imgs[3]); p=proj[3]
for r in (FL,EX): ax.plot(*p(r['Q']),'o',ms=13,mfc='#ffd43b',mec='k',mew=2,zorder=5)
note(ax,"canal Ø1,2",p(tuple(FL['chan'][14])),(500,500),CA,bold=True)
note(ax,"canal Ø1,2",p(tuple(EX['chan'][14])),(40,330),CB,bold=True)
note(ax,"poche du bas\n(fléchisseur)",p(face(FL['P'][1],FL['P'][2])),(760,690),CA,bold=True)
note(ax,"poche du haut\n(extenseur)",p(face(EX['P'][1],EX['P'][2])),(760,70),CB,bold=True)
# --- 4  knot drawing
ax=panel(0,1,4,"Fais un nœud d'arrêt double","Double nœud d'arrêt (« double overhand ») : fais 2 tours de la queue dans la boucle, puis serre. Laisse 10 mm de queue. Le nœud doit être plus gros que le canal Ø1,2 et tenir dans la poche Ø3,2 (alternative : un manchon à sertir d'environ 1 mm).")
ax.set_xlim(-9,13); ax.set_ylim(-8.25,8.25)
d=0.40; th=np.linspace(d,4*math.pi-d,1400); Rk=2+np.cos(2.5*th); kx=Rk*np.cos(th); ky=Rk*np.sin(th); kz=np.sin(2.5*th); LW=11
def stroke(x,y,lw,c,z=2): ax.plot(x,y,color=c,lw=lw,solid_capstyle='round',solid_joinstyle='round',zorder=z)
t=np.linspace(0,1,40); stand=np.c_[kx[0]+t*6.0,ky[0]+(t**1.7)*4.2]; tail=np.c_[kx[-1]+t*6.0,ky[-1]-(t**1.7)*4.2]
stroke(kx,ky,LW,CA)
cr=[np.argmin(abs(th-(math.pi/2+k*math.pi)/2.5)) for k in range(0,10)]; cr=[i for i in cr if 60<i<1340]
for i in cr:
    if kz[i]>0: a,b=i-60,i+60; stroke(kx[a:b],ky[a:b],LW+9,'white',3); stroke(kx[a:b],ky[a:b],LW,CA,4)
stroke(stand[:,0],stand[:,1],LW,CA); stroke(tail[:,0],tail[:,1],LW,CA)
note(ax,"ligne qui vient de la gorge\n(par le canal Ø1,2)",(stand[-1,0]-0.2,stand[-1,1]-0.1),(5.2,7.0),INK)
note(ax,"queue : 10 mm",(tail[-1,0]-0.2,tail[-1,1]),(7.4,-6.3),INK)
note(ax,"nœud serré\n(5 croisements)",(-1.6,-1.2),(-8.4,-6.6),INK)
ax.text(-8.7,7.5,"schéma agrandi, pas à l'échelle",fontsize=12,color=GREY,style='italic')
# --- 5
ax=panel(1,1,5,"Rentre le nœud, puis une goutte de colle","Tire la ligne du côté du tube : le nœud descend au fond de la poche (il ne peut pas passer dans le canal Ø1,2). Puis 1 goutte de colle cyano sur le nœud. La queue de 10 mm reste couchée sur la plaque. Même geste pour l'extenseur (poche du haut).",imgs[5]); p=proj[5]
note(ax,"goutte de colle cyano",p((X1-0.2,FL['P'][1],FL['P'][2])),(560,700),'#b08900',bold=True)
note(ax,"nœud au fond de la poche",p((X0+1.4,FL['P'][1],FL['P'][2])),(40,590),CA,bold=True)
note(ax,"queue 10 mm",p(tuple(tail_pts(FL,'flex')[-1])),(740,610),CA,bold=True)
note(ax,"poche Ø3,2 × 2,0",p(face(EX['P'][1],EX['P'][2])),(40,110),INK,bold=True)
# --- key
left=ML+2*(CW+GAP); bottom=FH-HEAD-1*ROWH-TITLE-IMGH
ax=fig.add_axes([left/FW,bottom/FH,CW/FW,IMGH/FH]); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_facecolor('#f1f5f9')
for sp in ax.spines.values(): sp.set_edgecolor('#9aa5b1'); sp.set_linewidth(1.5)
ax.text(0.04,0.955,"À retenir",fontsize=21,fontweight='bold',va='top',color=INK)
items=["Orange = servo A, bleu = servo B (plaque +X vue de l'extérieur).",
 "Fléchisseur = poche du bas (côté paume), extenseur = poche du haut (dos).",
 "Gorge : ligne à R9,0 du pivot (bras de levier 9,0 mm) ; canal Ø1,2 ; poche Ø3,2 × 2,0 mm ; jante R9,7.",
 "Le trou Ø2,5 et la fente Ø2,5 ne servent QU'AU PASSAGE DES AXES (D2×10 et D2×16) : n'y attache jamais la ligne. Bras de levier de 0 ou 6 mm au lieu de 9 mm : la boucle serait trop lâche ou trop tendue (écart de 1,7 mm à −30°, 4,7 mm à −70°, modèle 2D).",
 "Par doigt : 4 bouts de ligne, donc 4 nœuds.",
 "La tresse est dessinée plus épaisse que la vraie ; son diamètre n'est pas mesuré. Rien n'a été testé à l'impression ni sur le robot."]
y=0.865
for it in items:
    lines=textwrap.wrap(it,56); ax.text(0.04,y,"●",fontsize=13,va='top',color='#1c7ed6'); ax.text(0.085,y,"\n".join(lines),fontsize=14,va='top',color=INK,linespacing=1.35); y-=0.043*len(lines)+0.022
# --- 6 overview (render + crossing scheme)
axb=panel(0,2,6,"Vue d'ensemble : les 4 bouts d'un doigt et le croisement","Chaque plaque reçoit un fléchisseur (poche du bas) d'un servo et un extenseur (poche du haut) de l'autre servo. Si les deux bouts d'une boucle allaient sur la même plaque, le doigt ne pourrait plus faire l'abduction. Chaque bout se fixe comme aux étapes 1 à 5 (4 nœuds par doigt).",None,span=2)
axb.axis('off')
axi=fig.add_axes([ML/FW,(FH-HEAD-2*ROWH-TITLE-IMGH)/FH,CW/FW,IMGH/FH]); axi.imshow(imgs[6],aspect='auto'); axi.set_xticks([]); axi.set_yticks([]); axi.set_xlim(0,1000); axi.set_ylim(750,0)
for sp in axi.spines.values(): sp.set_edgecolor('#9aa5b1'); sp.set_linewidth(1.5)
p=proj[6]
note(axi,"plaque −X",p((-13.2,0,2)),(70,70),INK,bold=True); note(axi,"plaque +X",p((13.2,0,2)),(800,70),INK,bold=True)
note(axi,"gaines PTFE (vers les servos)",p((X_SOCK,-36,ZS['flex'])),(330,700),INK)
axi.text(10,742,"vue de derrière, au-dessus (CAO)",fontsize=12,color=GREY,style='italic',va='bottom')
axs=fig.add_axes([(ML+CW+GAP)/FW,(FH-HEAD-2*ROWH-TITLE-IMGH)/FH,CW/FW,IMGH/FH]); axs.set_xlim(-5.2,15.2); axs.set_ylim(-3.1,12.2); axs.set_xticks([]); axs.set_yticks([])
for sp in axs.spines.values(): sp.set_edgecolor('#9aa5b1'); sp.set_linewidth(1.5)
def plate_icon(cx,cy,title,sgn):
    axs.add_patch(Circle((cx,cy),1.9,fc='#cbd5e1',ec='#64748b',lw=2)); axs.add_patch(Circle((cx,cy-0.25),0.28,fc='white',ec='#64748b'))
    px=cx+sgn*1.05; axs.add_patch(Circle((px,cy+0.9),0.38,fc='white',ec='#64748b',lw=2)); axs.add_patch(Circle((px,cy-0.95),0.38,fc='white',ec='#64748b',lw=2))
    ha='right' if sgn>0 else 'left'; axs.text(px-sgn*0.55,cy+0.9,"extenseur",fontsize=10,ha=ha,va="center",color=INK); axs.text(px-sgn*0.55,cy-1.2,"fléchisseur",fontsize=10,ha=ha,va='center',color=INK)
    axs.text(cx,cy+2.35,title,fontsize=15,fontweight='bold',ha='center',color=INK); return (px,cy+0.9),(px,cy-0.95)
pm_ext,pm_flex=plate_icon(1.6,8.4,"plaque −X",+1); pp_ext,pp_flex=plate_icon(8.4,8.4,"plaque +X",-1)
axs.text(5,11.7,"croisement : chaque boucle va aux deux plaques opposées",fontsize=14,ha='center',color=INK,fontweight='bold')
for cx,name,c in ((2.8,"A",CA),(7.2,"B",CB)):
    axs.add_patch(Circle((cx,0.7),0.85,fc='white',ec=c,lw=3,zorder=5)); axs.text(cx,0.7,name,fontsize=22,fontweight='bold',ha='center',va='center',color=c,zorder=6)
def link(a,b,c,ls): axs.add_patch(FancyArrowPatch(a,b,arrowstyle='-',color=c,lw=3.6,ls=ls))
A=(2.8,1.55); B=(7.2,1.55)
link(A,pp_flex,CA,'-'); link(A,pm_ext,CA,'--'); link(B,pm_flex,CB,'-'); link(B,pp_ext,CB,'--')
for (x,y,t,c) in ((-4.9,-1.0,"A fléchisseur → plaque +X (trait plein)",CA),(-4.9,-1.9,"A extenseur → plaque −X (tirets)",CA),(5.3,-1.0,"B fléchisseur → plaque −X (trait plein)",CB),(5.3,-1.9,"B extenseur → plaque +X (tirets)",CB)):
    axs.text(x,y,t,fontsize=12.5,color=c,fontweight='bold',va='center')
# --- 7 tensioning
panel(2,2,7,"Mise en tension (servos au centre)","1. Mets les deux servos du doigt à 2048 (centre).\n2. Garde le doigt droit.\n3. Tends chaque boucle à la main : pas de mou, mais sans forcer.\n4. La tension se règle avec le servo, pas en serrant davantage le nœud.\n5. Premiers essais avec la limite de couple à 10 % (environ 35 N).",None)
left=ML+2*(CW+GAP); bottom=FH-HEAD-2*ROWH-TITLE-IMGH; ax=fig.axes[-1]; ax.axis('off')
axi=fig.add_axes([left/FW,(bottom+IMGH*0.40)/FH,CW/FW,IMGH*0.60/FH]); axi.imshow(imgs[7],aspect='auto'); axi.set_xticks([]); axi.set_yticks([]); axi.set_xlim(0,1000); axi.set_ylim(450,0)
for sp in axi.spines.values(): sp.set_edgecolor('#9aa5b1'); sp.set_linewidth(1.5)
p=proj[7]; note(axi,"doigt droit (Link au repos de la CAO)",p((13.2,6,-6)),(430,60),INK,bold=True); note(axi,"ligne tendue, sans mou",p((6,-12,-14.3)),(60,420),INK)
axd=fig.add_axes([left/FW,bottom/FH,CW/FW,IMGH*0.38/FH]); axd.set_xlim(-3.75,13.75); axd.set_ylim(0,5); axd.set_xticks([]); axd.set_yticks([])
for sp in axd.spines.values(): sp.set_edgecolor('#9aa5b1'); sp.set_linewidth(1.5)
for cx,name,c in ((1.6,"A",CA),(5.4,"B",CB)):
    axd.add_patch(Circle((cx,2.75),1.15,fc='white',ec=c,lw=3.5)); axd.plot([cx,cx],[2.75,3.75],color=c,lw=5,solid_capstyle='round'); axd.plot(cx,2.75,'o',color=c,ms=9)
    axd.text(cx,0.95,"servo "+name+"\n2048",fontsize=15,ha='center',va='center',color=c,fontweight='bold',linespacing=1.2)
axd.text(7.9,2.6,"2048 = centre\n(plage 0 à 4095)\naiguille en haut",fontsize=14,va='center',color=INK,linespacing=1.4)
fig.text(0.0145,0.9915,"MateBot : fixer la ligne (tresse) sur les plaques de finger_link_tendon, pas à pas",fontsize=29,fontweight='bold',va='top',color=INK)
fig.text(0.0145,0.9585,"Pièces tirées de la CAO (finger_link_tendon v1, R-Hand_Plate_tendon). Orange = servo A, bleu = servo B. Vues de la plaque +X ; la plaque −X est symétrique. Dessin non testé à l'impression ni sur le robot.",fontsize=15,va='top',color='#475569')
fig.text(0.0145,0.9395,"CAO : canal Ø1,2 · poche Ø3,2 × 2,0 · gorge 1,4 mm · jante R9,7 · bras de levier 9,0 mm · plaque à X = ±12,0 à ±14,4 mm (repère du doigt : X latéral, Y vers le bout, Z vers le dos).",fontsize=13,va='top',color='#475569')
fig.savefig(OUT,dpi=100); print("saved",OUT)
