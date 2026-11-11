# Renders docs/bushing_d6_preview.png: the printable bushing (3 views) and the Y=0 section of the abduction pivot with the pair fitted.
# Usage: python render_bushing_d6.py "<folder with the original 'Amazing Hand Parts - *.step'>"  (CadQuery, numpy-stl, matplotlib)
import sys, os, math, tempfile, importlib.util
import numpy as np, cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh
here = os.path.dirname(os.path.abspath(__file__)); docs = os.path.join(here, "..", "docs")
ah = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MATEBOT_AH_STEP_DIR", "/workspace/ah-enh/cad/step")
spec = importlib.util.spec_from_file_location("b", os.path.join(here, "bushing_d6.py")); B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
P = B.P; b = B.build()
f = os.path.join(tempfile.mkdtemp(), "b.stl"); cq.exporters.export(b, f, tolerance=0.01, angularTolerance=0.1); V = mesh.Mesh.from_file(f).vectors
def light(v, d=np.array([0.4, -0.5, 0.8])):
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12; d = d / np.linalg.norm(d); return 0.3 + 0.7 * np.clip(n @ d, 0, 1)
fig = plt.figure(figsize=(17, 5.8))
for i, (el, az, t) in enumerate([(30, -50, "3/4 view, body up"), (-30, -50, "3/4 view from below (flange face)")]):
    ax = fig.add_subplot(1, 3, i + 1, projection='3d')
    ax.add_collection3d(Poly3DCollection(V, facecolors=np.c_[np.array([0.12, 0.12, 0.14])[None, :] * 0 + np.array([0.29, 0.56, 0.85])[None, :] * light(V)[:, None], np.ones(len(V))], edgecolor='none'))
    mid = (V.reshape(-1, 3).max(0) + V.reshape(-1, 3).min(0)) / 2; r = 6.2
    ax.set_xlim(mid[0] - r, mid[0] + r); ax.set_ylim(mid[1] - r, mid[1] + r); ax.set_zlim(mid[2] - r, mid[2] + r); ax.set_box_aspect((1, 1, 1)); ax.view_init(el, az); ax.set_axis_off(); ax.set_title(t, fontsize=10)
# section through the pivot (plane Y = 0), X horizontal, Z vertical
def load(n): return cq.importers.importStep(os.path.join(ah, "Amazing Hand Parts - %s.step" % n))
F1 = load("Finger_Frame-1"); G = load("Gimbal"); fz0, fz1 = F1.val().BoundingBox().zmin, F1.val().BoundingBox().zmax
low = b.translate((0, 0, fz0 - P['flange_t'])); high = b.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, fz1 + P['flange_t']))
slab = cq.Workplane("XY").box(60, 0.02, 60).translate((0, 0, 5))
def tris(s):
    out = []
    for fc in s.intersect(slab).faces(">Y").vals():
        vs, ts = fc.tessellate(0.01)
        out += [[(vs[i].x, vs[i].z) for i in t] for t in ts]
    return out
ax = fig.add_subplot(1, 3, 3); ax.set_aspect('equal')
for shp, col in ((F1, '#b8b8b8'), (G, '#7fb2e5'), (low, '#ff9f43'), (high, '#ff9f43')):
    for t in tris(shp): ax.add_patch(Polygon(t, closed=True, fc=col, ec=col, lw=0.3))
ax.add_patch(Rectangle((-4, fz1 + P['flange_t']), 8, 0.8, fc='#dddddd', ec='k', lw=0.6, zorder=4)); ax.text(4.3, fz1 + P['flange_t'] + 0.4, "M2.5 large washer (D8)", fontsize=8, va='center')
ax.text(-10, fz0 - 1.1, "bottom flange (3.5..4.5)", fontsize=8); ax.text(-10, fz1 + 1.4, "top flange (12.5..13.5)", fontsize=8)
ax.text(8.3, 8.5, "Finger_Frame-1", fontsize=8, color='#666'); ax.text(-8.2, 7, "Gimbal boss D6", fontsize=8, color='#2b6cb0')
ax.set_xlim(-11, 12); ax.set_ylim(1.5, 16.5); ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")
ax.set_title("Section Y=0 of the abduction pivot, pair fitted\n(Frame-1 grey, Gimbal blue, bushings orange)", fontsize=10)
fig.suptitle("bushing_d6_flanged: PETG equivalent of Pollen's GFM-0608-04. bore D%.2f, OD D%.2f, length %.1f (flange D%.0f x %.1f). 2 per finger, UNTESTED" % (P['bore'], P['od'], P['length'], P['flange_d'], P['flange_t']), fontsize=11)
plt.tight_layout(rect=[0, 0, 1, 0.93]); plt.savefig(os.path.join(docs, "bushing_d6_preview.png"), dpi=100); plt.close()
print("ok")
