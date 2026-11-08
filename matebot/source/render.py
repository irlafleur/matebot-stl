import glob,matplotlib;matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh
for f in glob.glob("*.stl"):
    m=mesh.Mesh.from_file(f);fig=plt.figure(figsize=(5,5));ax=fig.add_subplot(projection='3d')
    ax.add_collection3d(Poly3DCollection(m.vectors,facecolor='#4a90d9',edgecolor='k',linewidth=0.05))
    s=m.points.flatten();ax.auto_scale_xyz(s,s,s);ax.set_title(f+" (v0 UNTESTED)");plt.savefig(f[:-4]+"_preview.png",dpi=90)
