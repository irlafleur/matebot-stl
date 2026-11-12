# Renders docs/bushing_washer_d6_preview.png: the two printed parts (top-hat bushing-washer, flat washer) and the sections of option 1 (stock Gimbal, screw from the top)
# and option 2 (Gimbal_tendon, screw from below).  Usage: python render_bushing_washer_d6.py "<folder with the original 'Amazing Hand Parts - *.step'>"
import sys, os, tempfile, importlib.util
import numpy as np, cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh
here = os.path.dirname(os.path.abspath(__file__)); MS = os.path.join(here, "..", "step"); DOCS = os.path.join(here, "..", "docs")
AHD = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MATEBOT_AH_STEP_DIR", "/workspace/ah-enh/cad/step")
def ml(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(here, n + ".py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
BW = ml("bushing_washer_d6"); BU = ml("bushing_d6"); GTM = ml("Gimbal_tendon"); sys.argv = [sys.argv[0], os.path.join(AHD, "Amazing Hand Parts - R-Hand_Plate.step")]; M = ml("R-Hand_Plate_tendon"); P = M.P
MT = lambda n: cq.importers.importStep(os.path.join(MS, n + ".step")); AH = lambda n: cq.importers.importStep(os.path.join(AHD, f"Amazing Hand Parts - {n}.step"))
plate = MT("R-Hand_Plate_tendon"); bu = MT("bushing_d6_flanged"); G0 = AH("Gimbal"); GT = MT("Gimbal_tendon")
T = BW.build(); W = BW.build_washer(); WP = BW.P
low = bu.translate((0, 0, P['blk_z'][0] - BU.P['flange_t'])); high = bu.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, P['blk_z'][1] + BU.P['flange_t']))
T1 = BW.place_top(T, 13.5); z0 = P['post_z'][0]
screw1 = cq.Workplane("XY").workplane(offset=13.5 + WP['disc_t']).circle(2.25).extrude(1.8).union(cq.Workplane("XY").workplane(offset=13.5 + WP['disc_t'] - 8.0).circle(1.25).extrude(8.0))
W2 = BW.place_washer_under(W, 0, P['post_y'], z0)
screw2 = cq.Workplane("XY").workplane(offset=z0 - 0.9 - 1.8).center(0, P['post_y']).circle(2.25).extrude(1.8).union(cq.Workplane("XY").workplane(offset=z0 - 0.9).center(0, P['post_y']).circle(1.25).extrude(8.0))
tmp = tempfile.mkdtemp()
def tri(w):
    f = os.path.join(tmp, "t%d.stl" % abs(hash(str(id(w))))); cq.exporters.export(w, f, tolerance=0.02, angularTolerance=0.15); return mesh.Mesh.from_file(f).vectors
def light(v, d=np.array([0.4, -0.5, 0.8])):
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12; d = d / np.linalg.norm(d); return 0.3 + 0.7 * np.clip(n @ d, 0, 1)
def tris(s, val):
    sl = cq.Workplane("XY").box(0.02, 400, 400).translate((val, 0, 0)); r = s.intersect(sl); out = []
    for fc in r.faces().vals():
        if abs(fc.normalAt().x) < 0.9: continue
        vs, ts = fc.tessellate(0.03); out += [[(vs[i].y, vs[i].z) for i in t] for t in ts]
    return out
fig = plt.figure(figsize=(21, 14.5)); gs = fig.add_gridspec(2, 3, height_ratios=[1, 2.1])
for k, (w, name, col, el, az, txt) in enumerate([(T, "bushing_washer_d6 (option 1)", '#228be6', 28, -50, "vue de dessus, manchon en haut (orientation d'impression)"), (T, "", '#228be6', -35, -50, "vue de dessous (face du disque)"), (W, "washer_d8_printed (option 2)", '#868e96', 28, -50, "rondelle plate D8 x 0,9")]):
    ax = fig.add_subplot(gs[0, k], projection='3d'); V = tri(w)
    ax.add_collection3d(Poly3DCollection(V, facecolors=np.c_[np.array(matplotlib.colors.to_rgb(col))[None, :] * light(V)[:, None], np.ones(len(V))], edgecolor='none'))
    mid = (V.reshape(-1, 3).max(0) + V.reshape(-1, 3).min(0)) / 2; r = 6
    ax.set_xlim(mid[0] - r, mid[0] + r); ax.set_ylim(mid[1] - r, mid[1] + r); ax.set_zlim(mid[2] - r, mid[2] + r); ax.set_box_aspect((1, 1, 1)); ax.view_init(el, az); ax.set_axis_off()
    ax.set_title((name + "\n" if name else "") + txt, fontsize=12)
base = [(plate, '#9aa5b1', 0.9), (low, '#f59f00', 1)]
for k, (parts, lim, title, notes) in enumerate([
    (base + [(high, '#f59f00', 0) , (G0, '#4dabf7', 1), (T1, '#e64980', 1), (screw1, '#343a40', 1)], (-9, 9, -1, 19), "Option 1 : Gimbal d'origine, vis du dessus, bague-rondelle (rose)\n(coupe X=0, mm)", [((0, 14.2), (9.5, 17), "1 disque D10 x 0,9 : serre le bout du pivot,\n   tourne avec le Gimbal"), ((3.9, 11.5), (9.5, 12.5), "2 manchon OD 7,95 / ID 6,2 dans l'alésage D8,15\n   (remplace la bague du haut)"), ((0, 9), (9.5, 8), "3 vis 2.5x8 : 7,1 mm dans le trou D1,9"), ((4.5, 14.9), (9.5, 3), "4 plafond de la plaque Z 14,5 :\n   jeu 0,1 mm au-dessus du disque")]),
    (base + [(high, '#f59f00', 1), (GT, '#228be6', 1), (W2, '#e64980', 1), (screw2, '#343a40', 1)], (-16, 9, -4, 17), "Option 2 : Gimbal_tendon, vis par en dessous, rondelle plate imprimée (rose)\n(coupe X=0, mm)", [((-8.6, -0.4), (0,0), "1 rondelle D8 x 0,9 sous la languette\n   (jeu 0,4 mm ; 0,29 mm au Gimbal à ±25°)"), ((-8.6, 5), (7.5, 14), "2 vis 2.5x8 : 7,1 mm dans le poteau (pilote D1,9)"), ((-8.6, 2), (7.5, 9), "3 languette du Gimbal_tendon")])]):
    ax = fig.add_subplot(gs[1, k])
    for s, c, a in parts:
        if a == 0: continue
        for t in tris(s, 0): ax.add_patch(Polygon(t, closed=True, fc=c, ec=c, lw=0.25, alpha=a))
    ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(title, fontsize=12)
    for n, (xy, xyt, t) in enumerate(notes, 1): ax.text(xy[0], xy[1], str(n), fontsize=12, fontweight='bold', color='k', ha='center', va='center', bbox=dict(boxstyle='circle,pad=0.15', fc='yellow', ec='k'))
    ax.set_xlabel("\n".join(t.replace("\n   ", " ") for xy, xyt, t in notes), fontsize=10, loc='left')
ax = fig.add_subplot(gs[1, 2]); ax.axis('off')
ax.text(0, 0.97, "Quantités (pièces à imprimer, PETG, 0,12 mm, 100 %)", fontsize=13, fontweight='bold', va='top')
ax.text(0, 0.88, "Option 1 (recommandée) : 4 x bushing_washer_d6 (+2) + 4 x bushing_d6_flanged (bague du bas, +2)\n   -> plus de rondelle M2.5 achetée, plus de bague du haut.\n\nOption 2 (vis par en dessous) : 3 x washer_d8_printed (+1)\n   + bague du haut ET du bas standard (bushing_d6_flanged) par doigt.\n\nOrientation d'impression : bushing_washer_d6 disque sur le plateau, manchon\nvers le haut, sans support ; washer_d8_printed à plat.\n\nVis 2.5 x 8 suffisante : 7,1 mm de filet engagé\n(rondelle Pollen 0,8 mm : 7,2 mm).\nLe pivot reste libre : la vis serre le disque sur le bout du pivot,\nl'ensemble tourne avec le Gimbal ; le disque ne touche pas la plaque\n(1,0 mm de jeu) tant que le Gimbal repose sur sa bague du bas.", fontsize=10.5, va='top', linespacing=1.4)
fig.suptitle("MateBot v8 - bague-rondelle imprimée (remplace la rondelle M2.5 et la bague du haut) - CAO, non testé à l'impression", fontsize=15, y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.97]); plt.savefig(os.path.join(DOCS, "bushing_washer_d6_preview.png"), dpi=75); print("ok")
