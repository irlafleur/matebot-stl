# -*- coding: utf-8 -*-
# Previews of the v10 open-rack 3-3-2 forearm chassis (spools above and below) and a French tube-routing drawing.
# Usage: python render_forearm_mount_332.py
import os, sys, tempfile, math
import numpy as np, cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Polygon, FancyBboxPatch as FBP
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh
from sts3215 import envelope, HORN_OD, BODY_L, BODY_W, H_TO_HORN
import forearm_mount_332 as F

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs")
os.makedirs(DOCS, exist_ok=True)
parts = F.build_all(); p = F.P
tmp = tempfile.mkdtemp()

def tri(w, tol=0.35):
    f = os.path.join(tmp, "t%d.stl" % abs(hash(str(id(w))) % 10**8))
    cq.exporters.export(w, f, tolerance=tol, angularTolerance=0.2)
    return mesh.Mesh.from_file(f).vectors

def light(v, d=np.array([0.35, -0.55, 0.75])):
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    d = d / np.linalg.norm(d)
    return 0.28 + 0.72 * np.clip(n @ d, 0, 1)

def add3(ax, w, col, tol=0.35):
    V = tri(w, tol)
    rgba = np.c_[np.array(matplotlib.colors.to_rgb(col))[None, :] * light(V)[:, None], np.ones(len(V))]
    ax.add_collection3d(Poly3DCollection(V, facecolors=rgba, edgecolor="none"))
    return V

def frame3(ax, Vs, pad=6, equal_cube=False):
    pts = np.vstack([V.reshape(-1, 3) for V in Vs])
    lo, hi = pts.min(0) - pad, pts.max(0) + pad
    mid = (lo + hi) / 2
    span = hi - lo
    if equal_cube:
        r = span.max() / 2
        ax.set_xlim(mid[0] - r, mid[0] + r)
        ax.set_ylim(mid[1] - r, mid[1] + r)
        ax.set_zlim(mid[2] - r, mid[2] + r)
        ax.set_box_aspect((1, 1, 1))
    else:
        ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
        ax.set_box_aspect(tuple(np.maximum(span, 1.0)))
    ax.set_axis_off()

# ---------- 0. spool preview (holes now official 14 mm BCD, M3) ----------
fig = plt.figure(figsize=(8.2, 4.4))
fig.suptitle("MateBot  —  spool_r8  (v10, non testé)\nCercle de vis 14 mm (dessin Waveshare ST3215), 4 × M3 Ø3,4, vis M3×6",
             fontsize=12, fontweight="bold")
for i, (el, az, title) in enumerate(((28, -40, "trois quarts"), (90, -90, "dessus (trous M3)"))):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    V = add3(ax, parts["spool_r8"], "#e8590c", 0.08)
    frame3(ax, [V], 2, equal_cube=True)
    ax.view_init(el, az)
    ax.set_title(title, fontsize=10, pad=4)
fig.tight_layout(rect=(0, 0, 1, 0.86))
fig.savefig(os.path.join(DOCS, "spool_r8_preview.png"), dpi=130, bbox_inches="tight", facecolor="white")
plt.close()
print("wrote spool_r8_preview.png")

# ---------- 1. printed parts ----------
fig = plt.figure(figsize=(14.5, 10.2))
fig.subplots_adjust(left=0.03, right=0.98, top=0.88, bottom=0.04, wspace=0.08, hspace=0.22)
fig.suptitle("MateBot v10  —  pièces du châssis d'avant-bras  (non testé)", fontsize=15, fontweight="bold", y=0.97)
items = [
    (parts["yoke"], "forearm_wrist_yoke  (×1)\njoug au poignet, 4 sockets du pouce", "#4c6ef5", 22, -55, True),
    (parts["rail_L"], "forearm_rail_3x_L  (×1)\ncôté radial, index / majeur / annulaire A", "#20c997", 18, -40, False),
    (parts["rail_R"], "forearm_rail_3x_R  (×1)\ncôté cubital, index / majeur / annulaire B", "#20c997", 18, -140, False),
    (parts["brace"], "forearm_brace  (×3)\nentretoise palmaire, 4 × M3", "#fab005", 22, -50, False),
    (parts["spool_r8"], "spool_r8  (×8 + 2)\nBCD 14 mm, 4 × M3×6", "#e8590c", 22, -40, True),
]
for i, (w, title, col, el, az, cube) in enumerate(items):
    ax = fig.add_subplot(2, 3, i + 1, projection="3d")
    V = add3(ax, w, col, 0.35 if i < 3 else 0.1)
    frame3(ax, [V], 5 if i < 3 else 2, equal_cube=cube if i != 3 else False)
    ax.view_init(el, az)
    ax.set_title(title, fontsize=9.5, pad=8)
ax = fig.add_subplot(2, 3, 6)
ax.set_axis_off()
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.text(0.2, 9.5, "Impression  (PETG noir)", fontsize=12, fontweight="bold")
ax.text(0.2, 8.9,
        "• Rails : plaque médiane à plat, face dorsale\n"
        "  vers le haut.  4 à 6 parois, 40 %, 0,20 mm.\n"
        "  Supports sous les nervures et logements\n"
        "  de la face palmaire (index et annulaire).\n\n"
        "• Joug : bossage de centrage (Y = −2 mm)\n"
        "  sur le plateau, trous M2 verticaux.\n"
        "  Supports sous les nervures palmaires s'il\n"
        "  y en a ; le pouce est sur la face dorsale.\n\n"
        "• Entretoises : à plat, sans support (8 mm).\n"
        "• Spool : bride sur le plateau, 100 %\n"
        "  ou 6 parois, 0,12 à 0,20 mm.\n\n"
        "Lit max. 250 mm : rail 165 mm, joug 120 mm.\n"
        "Paquet ~241 mm de long, ~97 mm d'épaisseur\n"
        "servo+spool (rails 110 mm avec logements).",
        fontsize=8.5, va="top", family="DejaVu Sans")
fig.savefig(os.path.join(DOCS, "forearm_parts_preview.png"), dpi=130, bbox_inches="tight", facecolor="white")
plt.close()
print("wrote forearm_parts_preview.png")

# ---------- 2. assembly ----------
assy = [("yoke", parts["yoke"], "#4c6ef5"),
        ("rail_L", parts["rail_L"], "#20c997"),
        ("rail_R", parts["rail_R"], "#20c997")]
for yb in F._gap_ys(p):
    assy.append(("brace", parts["brace"].translate((0, yb, p["z_bot_face"] - 4.0)), "#fab005"))
for finger in ("thumb", "index", "middle", "ring"):
    for ab in ("A", "B"):
        xf, ysh = F.servo_xf(finger, ab), F._ys()[finger]
        face = F.servo_face(finger)
        env = F.place_S(envelope(cl=0, with_horns=True, with_cables=False), xf, ysh, F.z_shaft_of(finger), face)
        sp = F.place_S(parts["spool_r8"], xf, ysh, F.z_shaft_of(finger), face)
        assy.append((f"s_{finger}_{ab}", env, "#868e96"))
        assy.append((f"p_{finger}_{ab}", sp, "#e8590c"))

fig = plt.figure(figsize=(14.5, 8.2))
fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.02, wspace=0.02)
fig.suptitle("MateBot v10  —  châssis 3-3-2 ouvert, spools dessus et dessous + 8 × STS3215  (non testé)", fontsize=15, fontweight="bold", y=0.97)
for i, (el, az, title, cube) in enumerate((
        (18, -55, "vue de trois quarts : spools en haut (pouce, majeur) et en bas (index, annulaire)", False),
        (90, -90, "vue de dessus (face dorsale : pouce et majeur ; index et annulaire dessous)", False))):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    Vs = []
    for name, w, col in assy:
        tol = 0.6 if name in ("yoke", "rail_L", "rail_R") else 0.35
        Vs.append(add3(ax, w, col, tol))
    frame3(ax, Vs, 8, equal_cube=cube)
    ax.view_init(el, az)
    ax.set_title(title, fontsize=11, pad=6)
fig.savefig(os.path.join(DOCS, "forearm_chassis_preview.png"), dpi=130, bbox_inches="tight", facecolor="white")
plt.close()
print("wrote forearm_chassis_preview.png")

# ---------- 3. French routing + layout comparison ----------
# Reuse the verified waypoints (same geometry as verify_forearm_mount_332.py).
PLATE = {
    ("index",  "+X", "ext"):  (10.50, -30.00,  2.30),
    ("index",  "+X", "flex"): (10.50, -30.00,-12.80),
    ("index",  "-X", "ext"):  (-10.50,-30.00,  2.30),
    ("index",  "-X", "flex"): (-10.50,-30.00,-12.80),
    ("middle", "+X", "ext"):  (40.24, -36.90,  2.30),
    ("middle", "+X", "flex"): (40.24, -36.90,-12.80),
    ("middle", "-X", "ext"):  (19.34, -34.79,  2.30),
    ("middle", "-X", "flex"): (19.34, -34.79,-12.80),
    ("ring",   "+X", "ext"):  (68.23, -48.72,  2.30),
    ("ring",   "+X", "flex"): (68.23, -48.72,-12.80),
    ("ring",   "-X", "ext"):  (47.81, -43.83,  2.30),
    ("ring",   "-X", "flex"): (47.81, -43.83,-12.80),
}

def lane_x(finger, ab):
    if finger == "thumb":
        return -20.0
    if finger == "index":
        return F.WI_XF[0] - p["lane_w"] / 2 - 0.5
    if finger == "ring":
        return F.WI_XF[1] + p["lane_w"] / 2 + 0.5
    return 0.0

def lane_z(finger):
    if finger == "thumb":
        return F.WI_ZF[0] - p["lane_w"] / 2 - 0.5
    if F.servo_face(finger) == "top":
        return 12.0
    return -16.0

def path_for(rec, which_z):
    x, yb, ys, zg1, zg2 = rec["sock"]
    z = zg1 if which_z == 0 else zg2
    finger, ab = rec["finger"], rec["ab"]
    lx = lane_x(finger, ab)
    zc = lane_z(finger)
    if finger == "thumb":
        x_out = x - 40.0
        return [(x, yb, z), (x_out, yb, z), (x_out, yb, zc), (x_out, -25.0, zc), (lx, -25.0, zc)]
    y_run = yb - 40.0
    if abs(lx - x) >= 40.0:
        pts = [(x, yb, z), (x, y_run, z), (lx, y_run, zc)]
    else:
        pts = [(x, yb, z), (lx, y_run, zc)]
    key_side = "-X" if ab == "A" else "+X"
    key_kind = "ext" if which_z == 0 else "flex"
    hx, hy, hz = PLATE[(finger, key_side, key_kind)]
    xf, yf, zf = F.hand_to_f(hx, hy, hz)
    y_pre = yf + 40.0
    pts += [(lx, y_pre, zc), (xf, yf, zf)]
    return pts

colors_f = {"thumb": "#9c36b5", "index": "#1c7ed6", "middle": "#2f9e44", "ring": "#e8590c"}
names_f = {"thumb": "pouce", "index": "index", "middle": "majeur", "ring": "annulaire"}

fig = plt.figure(figsize=(17.2, 12.4), facecolor="white")
gs = fig.add_gridspec(2, 2, height_ratios=[1.55, 1.0], hspace=0.22, wspace=0.16,
                      left=0.05, right=0.98, top=0.90, bottom=0.05)
ax = fig.add_subplot(gs[0, :])
ax.set_aspect("equal")
ax.set_title("Tracé des 16 gaines PTFE  —  vue de dessus.  Traits pleins = face dorsale (haut), pointillés = face palmaire (bas).  R ≥ 30 mm, sans croisement 3D.",
             fontsize=12.5, pad=10)

# Wrist interface (top view)
ax.add_patch(Rectangle((F.WI_XF[0], -17.2), F.WI_XF[1] - F.WI_XF[0], 17.2,
                       facecolor="#dee2e6", edgecolor="#343a40", lw=1.0, zorder=1))
ax.add_patch(Circle((0, 0), 17.0, facecolor="white", edgecolor="#343a40", lw=1.0, ls="--", zorder=2))
# corridors as pale bands (top-view footprints)
ax.add_patch(Rectangle((F.WI_XF[0] - 11, -4), 11, 16,
                       facecolor="#fff3bf", edgecolor="#e67700", lw=0.7, ls="--", zorder=1, alpha=0.85))
ax.add_patch(Rectangle((F.WI_XF[1], -4), 11, 16,
                       facecolor="#fff3bf", edgecolor="#e67700", lw=0.7, ls="--", zorder=1, alpha=0.85))

# rails
for side, name in ((-1, "rail A  (radial)"), (1, "rail B  (cubital)")):
    xf = F.servo_xf("index", "A" if side < 0 else "B")
    half = (BODY_W + 0.4) / 2 + p["wall"]
    y0, y1 = p["y_index"] - 16, p["y_end"]
    ax.add_patch(Rectangle((xf - half, y0), 2 * half, y1 - y0,
                           facecolor="#e6fcf5", edgecolor="#0b7285", lw=1.0, zorder=2))
    ax.text(xf, y1 + 8, name, ha="center", fontsize=8, color="#0b7285")

# thumb bed
ax.add_patch(Rectangle((F.servo_xf("thumb", "A") - 14, 6),
                       F.servo_xf("thumb", "B") - F.servo_xf("thumb", "A") + 28,
                       F._thumb_bed_end(p) - 6, facecolor="#dbe4ff", edgecolor="#364fc7", lw=1, zorder=2))

# servos + spools
for finger in ("thumb", "index", "middle", "ring"):
    for ab in ("A", "B"):
        xf, ysh = F.servo_xf(finger, ab), F._ys()[finger]
        ax.add_patch(Rectangle((xf - BODY_W / 2, ysh - 10.11), BODY_W, BODY_L,
                               facecolor=colors_f[finger], edgecolor="k", lw=0.4, alpha=0.45, zorder=3))
        face = F.servo_face(finger)
        ax.add_patch(Circle((xf, ysh), 11, facecolor="#fd7e14" if face=="top" else "#ffd8a8",
                            edgecolor="#d9480f", lw=0.5, alpha=0.95, zorder=4, linestyle="-" if face=="top" else "--"))
        tag = "HAUT" if face == "top" else "BAS"
        ax.text(xf, ysh + 22, f"{names_f[finger]} {ab}  {tag}", ha="center", fontsize=6.5, color="#212529", zorder=5)

# lane bands
for f, lab in (("index", "voie index (bas)"), ("middle", "voie majeur (haut)"), ("ring", "voie annulaire (bas)")):
    lx = lane_x(f, "A")
    ax.plot([lx, lx], [-22, F._ys()[f] - 12], color=colors_f[f], lw=7, alpha=0.22,
            solid_capstyle="round", zorder=1)
    ax.text(lx + (8 if f == "ring" else -8 if f == "index" else 8),
            F._ys()[f] - 18, lab, ha="left" if f != "index" else "right",
            fontsize=7.5, color=colors_f[f], fontweight="bold", zorder=6)

# all 16 verified paths (xy): solid = top face, dashed = bottom face
for rec in parts["recs"]:
    c = colors_f[rec["finger"]]
    ls = "-" if rec["face"] == "top" else "--"
    for k in (0, 1):
        pts = path_for(rec, k)
        xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
        ax.plot(xs, ys, color=c, lw=1.2, alpha=0.9, zorder=6, linestyle=ls)
        ax.plot(xs[0], ys[0], "o", color=c, ms=3.2, zorder=7)
        ax.plot(xs[-1], ys[-1], "s", color=c, ms=3.4, zorder=7)

# annotations well outside the wrist clutter
ax.annotate("12 sockets de la plaque\n(index, majeur, annulaire)",
            xy=(16, -72), xytext=(58, -78),
            fontsize=8, color="#1c7ed6", ha="left",
            arrowprops=dict(arrowstyle="->", color="#1c7ed6", lw=0.9))
ax.annotate("4 sockets du pouce\nsur le joug, face HAUT",
            xy=(-21, 8.5), xytext=(-78, 40),
            fontsize=8, color="#9c36b5", ha="center",
            arrowprops=dict(arrowstyle="->", color="#9c36b5", lw=0.9))
ax.annotate("coude R ≥ 30 mm\navant chaque voie",
            xy=(F.servo_xf("index", "A"), F._ys()["index"] - 40),
            xytext=(-78, 130),
            fontsize=8, color="#495057", ha="center",
            arrowprops=dict(arrowstyle="->", color="#495057", lw=0.9))
ax.annotate("couloir cubital\n(annulaire)",
            xy=(F.WI_XF[1] + 5.5, 4), xytext=(70, 18),
            fontsize=8, color="#e67700",
            arrowprops=dict(arrowstyle="->", color="#e67700", lw=0.8))
ax.annotate("couloir radial\n(index)",
            xy=(F.WI_XF[0] - 5.5, 4), xytext=(-78, -8),
            fontsize=8, color="#e67700",
            arrowprops=dict(arrowstyle="->", color="#e67700", lw=0.8))
ax.text(0, -10, "fenêtre Ø34\n(voie du majeur)", ha="center", va="center", fontsize=7.5, color="#495057")
ax.text(F.P["thumb_cx"], 68, "joug + paire du pouce", ha="center", va="bottom", fontsize=8, color="#364fc7")
ax.annotate("couloir palmaire-radial\ndu pouce (sous le joug,\nvu ici en projection)",
            xy=(-20, -25), xytext=(-78, -50),
            fontsize=8, color="#9c36b5", ha="center",
            arrowprops=dict(arrowstyle="->", color="#9c36b5", lw=0.8))

ax.set_xlim(-100, 95)
ax.set_ylim(-95, 260)
ax.set_xlabel("x_f  (mm)     radial  ←        →  cubital", fontsize=9)
ax.set_ylabel("y_f  (mm)", fontsize=9)
ax.grid(True, ls=":", alpha=0.35)
ax.invert_yaxis()  # wrist at the top of the page
ax.text(0.5, -0.10, "Poignet (main) en haut de la page, coude en bas.   16 tubes = 8 boucles × 2.   Traits = plan de routage vérifié (R ≥ 30 mm).",
        transform=ax.transAxes, fontsize=8, color="#495057", ha="center", va="top")
ax.legend(handles=[
    Line2D([0], [0], color=colors_f[k], lw=2, label=names_f[k])
    for k in ("thumb", "index", "middle", "ring")
] + [
    Line2D([0], [0], marker="o", color="k", lw=0, label="socket servo", ms=5),
    Line2D([0], [0], marker="s", color="k", lw=0, label="socket plaque / pouce", ms=5),
], loc="lower right", fontsize=8, framealpha=0.92, ncol=3)

# ---------- layout sketches ----------
ax1 = fig.add_subplot(gs[1, 0])
ax1.set_xlim(0, 12)
ax1.set_ylim(0, 10)
ax1.set_axis_off()
ax1.set_title("Pourquoi ce 3-3-2  (et pas 3 servos de front, ni 4 paires en file)",
              fontsize=11, loc="left", pad=8)

def mini(ax, x0, y0, rows, title, note, chosen=False, shifts=None):
    w, h, gap = 0.42, 0.36, 0.08
    nmax = max(len(r) for r in rows)
    height = len(rows) * (h + gap) + 0.15
    width = nmax * (w + 0.04) + 0.2
    col = "#2f9e44" if chosen else "#adb5bd"
    if chosen:
        ax.add_patch(FancyBboxPatch((x0 - width / 2 - 0.55, y0 - 0.25),
                                    width + 0.85, height + 1.55,
                                    boxstyle="round,pad=0.08", facecolor="#ebfbee",
                                    edgecolor="#2b8a3e", lw=1.6, zorder=0))
    # wrist is at the TOP of the sketch (same as the plan)
    y = y0 + (len(rows) - 1) * (h + gap)
    shifts = shifts or [0] * len(rows)
    for row, sh in zip(rows, shifts):
        n = len(row)
        x = x0 - n * (w + 0.04) / 2 + sh
        for _ in row:
            ax.add_patch(Rectangle((x, y), w, h, facecolor=col, edgecolor="#212529", lw=0.45, zorder=2))
            x += w + 0.04
        y -= (h + gap)
    ax.text(x0, y0 + height + 1.05, title, ha="center", va="top", fontsize=8,
            fontweight="bold", color="#2b8a3e" if chosen else "#212529")
    ax.text(x0, y0 - 0.45, note, ha="center", va="top", fontsize=6.8, color="#495057")

# rows listed wrist → elbow
mini(ax1, 1.7, 3.3, ["AB", "AB", "AB", "AB"], "4 paires en file",
     "paires intactes\n~250+ mm, largeur constante\naccès arrière un peu moins bon", False)
mini(ax1, 5.15, 3.3, ["ABC", "ABC", "AB"], "3 + 3 + 2 de front",
     "une paire est coupée (3 impair)\n~90 mm de large au poignet\nplus court (~180 mm)", False)
mini(ax1, 9.0, 3.3, ["AB", "AB", "AB", "AB"], "Choisi : 2 rails de 3 + pouce,\nfaces alternées (haut/bas)",
     "paires intactes, faces alternées\nTL TR / BL BR, voies haut et bas\n~241 mm, épaisseur ~97–110 mm", True,
     shifts=[-0.45, 0, 0, 0])
ax1.text(8.55, 6.55, "pouce", ha="center", fontsize=6.5, color="#2b8a3e")
ax1.text(0.2, 1.15,
         "Chaque carré = un servo, vu depuis le dos, poignet en haut.  Un rang de 3 casse une paire (A et B\n"
         "doivent rester au même Y, face à face) et dépasse la largeur d'un poignet humain.  Une 4e station\n"
         "en file allonge l'avant-bras d'un pas (~53 mm) sans gain de routage.  Faces opposées (4+4) : trop épais.",
         fontsize=7.6, va="top", color="#343a40")

# ---------- comparison table ----------
ax2 = fig.add_subplot(gs[1, 1])
ax2.set_axis_off()
ax2.set_title("Tableau comparé  (avant-bras droit, poignet fixe)", fontsize=11, loc="left", pad=8)
col_labels = ["Disposition", "Long.", "Largeur", "Épais.", "Paires", "Tubes / accès"]
cell = [
    ["4 paires en file, 2 de front", "~250+ mm", "80 mm", "53 mm", "intactes", "OK / arrière un peu moins bon"],
    ["3+3+2 de front (3, 3 et 2)", "~180 mm", "90 puis 60", "53 mm", "1 coupée", "risque de croisement / bon"],
    ["4+4 faces opposées (palmaire + dorsal)", "~150 mm", "70 mm", "~100 mm", "intactes", "OK / bon, trop épais"],
    ["Colonne unique de 8", "~400 mm", "40 mm", "53 mm", "séparées", "OK / mauvais accès"],
    ["Choisi : 2 rails de 3 + 2, faces alternées", "~241 mm", "65 puis 80", "~97–110 mm", "intactes", "voies haut et bas / vis face libre"],
]
tbl = ax2.table(cellText=cell, colLabels=col_labels, loc="upper center", cellLoc="left")
tbl.auto_set_font_size(False)
tbl.set_fontsize(7.4)
tbl.scale(1.15, 1.85)
for (r, c), cell_obj in tbl.get_celld().items():
    cell_obj.set_edgecolor("#dee2e6")
    cell_obj.PAD = 0.04
    if r == 0:
        cell_obj.set_facecolor("#f1f3f5")
        cell_obj.set_text_props(weight="bold", color="#212529")
    elif r == 5:
        cell_obj.set_facecolor("#d3f9d8")
        cell_obj.set_text_props(color="#2b8a3e", weight="bold")
    else:
        cell_obj.set_facecolor("white")
tbl.auto_set_column_width(list(range(len(col_labels))))
ax2.text(0.0, 0.12,
         "Sources des cotes servo : dessin 2D Waveshare ST3215-2D.zip (intitulé SCS215, 8 juin 2022)\n"
         "et STEP ST3215-3D.zip.  Le tracé est un plan de routage, pas un solide balayé dans le châssis.\n"
         "Rayon min. PTFE 30 mm : déjà une limite de frottement du MANUEL.  OD du tube supposé 4,0 mm.\n"
         "Les paires alternent de face (pouce et majeur en haut, index et annulaire en bas) : le rack est ouvert des deux côtés.\n"
         "L'épaisseur d'ensemble (~97 mm servo+spool, 110 mm avec les logements) est celle d'un montage deux faces, demandé explicitement.",
         fontsize=7.2, color="#495057", style="italic", va="bottom", transform=ax2.transAxes)

fig.suptitle("MateBot  —  Support des 8 servos STS3215 et tracé des gaines  (v10, non testé)",
             fontsize=15, fontweight="bold", y=0.985)
fig.savefig(os.path.join(DOCS, "forearm_tubes_FR.png"), dpi=140, bbox_inches="tight", facecolor="white")
plt.close()
print("wrote forearm_tubes_FR.png")
print("done")
