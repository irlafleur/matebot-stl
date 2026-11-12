# v11 previews: top view + 3/4 view in the style of Ian-Remi's sketch,
# French labels, and a tube-routing / mounting-pattern drawing.
# Usage: python render_forearm_mount_row.py
import os, math, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Polygon, Arc, Wedge
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forearm_mount_row as F
from sts3215 import BODY_L, BODY_W, H_TO_HORN, SHAFT_FROM_OUT, SHAFT_FROM_CABLE

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.normpath(os.path.join(HERE, "..", "docs"))

# colours
C_TOP = "#4C7A9B"
C_BOT = "#C4A574"
C_SERVO_TOP = "#E07A3D"
C_SERVO_BOT = "#3D8B7A"
C_SPOOL = "#E2B04A"
C_IDLER = "#6B6B6B"
C_PLATE = "#D9D3C7"
C_PLATE2 = "#B7C4CE"
FINGER_COL = dict(thumb="#C0392B", index="#2980B9", middle="#27AE60", ring="#8E44AD")
FINGER_FR = dict(thumb="Pouce", index="Index", middle="Majeur", ring="Annulaire")

p = F.P
sts = F.stations()
paths = F.tube_paths()
pat = F.patterns()
ye = F.y_end()


def servo_rect(s):
    """Body rectangle in XY (long axis across the forearm)."""
    # body X: shaft + [-SHAFT_FROM_OUT, +SHAFT_FROM_CABLE] with side
    if s["side"] == "left":
        x0 = s["xf"] - SHAFT_FROM_OUT  # actually left: +X_s along +X, so x from xf-10.11 to xf+35.11
        x1 = s["xf"] + SHAFT_FROM_CABLE
    else:
        x0 = s["xf"] - SHAFT_FROM_CABLE
        x1 = s["xf"] + SHAFT_FROM_OUT
    y0 = s["y"] - BODY_W / 2
    y1 = s["y"] + BODY_W / 2
    return x0, x1, y0, y1


def draw_top_view(ax, with_tubes=False, with_patterns=True):
    ax.set_aspect("equal")
    # plates (top web outline)
    x_lip = p["x_bot_wall_out"] + p["lip"]
    # bottom plate slightly larger (flange)
    ax.add_patch(Rectangle((-44, -2), 88, p["flange_t"] + 2,
                            facecolor="#C9B89A", edgecolor="#5A4A32", lw=0.8, zorder=1))
    ax.add_patch(Rectangle((-x_lip, p["flange_t"]), 2 * x_lip, ye - p["flange_t"],
                            facecolor="#D5DEE6", edgecolor="#3D4A55", lw=0.9, zorder=2))
    # U walls (nested)
    for sign in (-1, 1):
        ax.add_patch(Rectangle((sign * p["x_top_wall_in"] if sign > 0 else -p["x_top_wall_out"],
                                p["flange_t"]),
                               p["wall"], ye - p["flange_t"],
                               facecolor="#9AAEB8", edgecolor="none", zorder=3, alpha=0.7))
    # joint
    ax.axhline(p["y_cut"], color="#7A3E00", ls="--", lw=0.9, zorder=4)
    ax.axhspan(p["y_cut"] - p["lap"] / 2, p["y_cut"] + p["lap"] / 2,
               color="#7A3E00", alpha=0.08, zorder=3)

    # M3 lip grid
    if with_patterns:
        for h in pat["web_shell_top_m3"]["holes"]:
            ax.add_patch(Circle((h["x"], h["y"]), 1.7, facecolor="none",
                                edgecolor="#1F4E79", lw=0.5, zorder=5))
        for x, y, z in pat["elbow_m3"]["top"]:
            ax.add_patch(Circle((x, y), 1.7, facecolor="none",
                                edgecolor="#7A1F1F", lw=0.7, zorder=5))
        for x, y, z in pat["joint_m3"]["top"]:
            ax.add_patch(Circle((x, y), 1.7, facecolor="none",
                                edgecolor="#7A3E00", lw=0.7, zorder=5))
        # WI holes at y=0
        for x, y, z in pat["front_wi_m2"]["positions"]:
            ax.add_patch(Circle((x, 3.0), 1.2, facecolor="none",
                                edgecolor="#222", lw=0.7, zorder=6))
        ax.add_patch(Circle((0, 3.0), 17.0, facecolor="none",
                            edgecolor="#222", lw=0.6, ls=":", zorder=6))

    for s in sts:
        x0, x1, y0, y1 = servo_rect(s)
        col = C_SERVO_TOP if s["face"] == "top" else C_SERVO_BOT
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0,
                               facecolor=col, edgecolor="#222", lw=0.7,
                               alpha=0.95, zorder=7))
        # spool or idler mark
        if s["face"] == "top":
            ax.add_patch(Circle((s["xf"], s["y"]), 11.0, facecolor=C_SPOOL,
                                edgecolor="#6A4A10", lw=0.7, zorder=8, alpha=0.95))
            ax.add_patch(Circle((s["xf"], s["y"]), 8.0, facecolor="none",
                                edgecolor="#6A4A10", lw=0.5, zorder=8))
        else:
            ax.add_patch(Circle((s["xf"], s["y"]), 3.2, facecolor="#222",
                                edgecolor="#222", zorder=8))
            ax.add_patch(Circle((s["xf"], s["y"]), 11.0, facecolor="none",
                                edgecolor="#555", lw=0.5, ls="--", zorder=8))
        # cut-out ring on the plate of the spool face
        ax.add_patch(Circle((s["xf"], s["y"]), 14.0, facecolor="none",
                            edgecolor="#333", lw=0.4, ls=":", zorder=8))
        label = f"{s['i']+1}  {FINGER_FR[s['finger']]} {s['ab']}"
        side = "G" if s["side"] == "left" else "D"
        face = "dessus" if s["face"] == "top" else "dessous"
        ax.text(0, s["y"], f"{label}\n{face}, arbre {side}",
                ha="center", va="center", fontsize=5.5, color="#111", zorder=9,
                fontweight="bold")

    if with_tubes:
        for path in paths:
            pts = path["pts_ptfe"]
            xs, ys = [q[0] for q in pts], [q[1] for q in pts]
            col = FINGER_COL[path["finger"]]
            ls = "-" if path["face"] == "top" else (0, (2.2, 1.4))
            ax.plot(xs, ys, color=col, lw=1.15, ls=ls, zorder=10, solid_capstyle="round")
            ax.plot(xs[-1], ys[-1], "o", color=col, ms=2.4, zorder=11)

    # annotations
    ax.annotate("POIGNET\n6 vis M2, cercle R=21 mm\n+ enregistrement Ø33,6",
                xy=(0, 0), xytext=(58, -8),
                fontsize=6.5, ha="left", color="#222",
                arrowprops=dict(arrowstyle="->", color="#222", lw=0.6))
    ax.annotate("COUDE OUVERT\n4 vis M3 par plaque",
                xy=(12, ye - 5), xytext=(50, ye - 20),
                fontsize=6.5, ha="left", color="#7A1F1F",
                arrowprops=dict(arrowstyle="->", color="#7A1F1F", lw=0.6))
    ax.annotate("Joint des deux demis\nY=186 mm, 4 vis M3",
                xy=(20, p["y_cut"]), xytext=(52, p["y_cut"] + 18),
                fontsize=6.5, ha="left", color="#7A3E00",
                arrowprops=dict(arrowstyle="->", color="#7A3E00", lw=0.6))
    ax.text(-x_lip - 2, (ye + p["flange_t"]) / 2, "Grille M3\nlèvres / coque\npas 20 mm",
            ha="right", va="center", fontsize=6.5, color="#1F4E79")
    ax.set_xlim(-78, 92)
    ax.set_ylim(-28, ye + 28)
    ax.set_xlabel("X (mm)  —  radial ←    → ulnaire")
    ax.set_ylabel("Y (mm)  —  poignet → coude")
    ax.grid(True, color="#ddd", lw=0.4)
    ax.set_axisbelow(True)


def draw_34(ax):
    """Schematic 3/4 (isometric) view of the sandwich."""
    ax.set_axis_off()
    # simple cabinet projection
    a, b = 0.5, 0.4
    def proj(x, y, z):
        return x + a * y, z + b * y

    def box(x0, x1, y0, y1, z0, z1, fc, ec="#333", alpha=0.9, lw=0.5, zorder=2):
        # 3 visible faces
        faces = [
            [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],  # front-ish
            [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],  # top
            [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],  # right
        ]
        for fcs in faces:
            pts = [proj(*q) for q in fcs]
            ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=ec,
                                 lw=lw, alpha=alpha, zorder=zorder + 0.001 * fcs[0][1]))

    # bottom plate web + walls + flange
    x_lip = p["x_bot_wall_out"] + p["lip"]
    box(-x_lip, x_lip, p["flange_t"], ye, p["z_outer_bot"], p["z_inner_bot"], C_BOT, zorder=2)
    box(-p["x_bot_wall_out"], -p["x_bot_wall_in"], p["flange_t"], ye, p["z_outer_bot"], p["wall_overlap_z"],
        "#A88A58", zorder=3)
    box(p["x_bot_wall_in"], p["x_bot_wall_out"], p["flange_t"], ye, p["z_outer_bot"], p["wall_overlap_z"],
        "#A88A58", zorder=3)
    box(-44, 44, 0, p["flange_t"], -40, 42, "#BFA67A", zorder=4)

    # servos + spools (draw before top plate so the top plate sits on them)
    for s in sts:
        x0, x1, y0, y1 = servo_rect(s)
        if s["face"] == "top":
            z0, z1 = p["z_inner_bot"], p["z_inner_bot"] + 32
            box(x0, x1, y0, y1, z0, z1, C_SERVO_TOP, zorder=5)
            # spool above top inner
            sx, sy = s["xf"], s["y"]
            # cylinder as a circle in projection is messy; use a short box
            box(sx - 8, sx + 8, sy - 8, sy + 8, p["z_inner_top"], p["z_inner_top"] + p["spool_h"],
                C_SPOOL, zorder=8)
        else:
            z0, z1 = p["z_inner_top"] - 32, p["z_inner_top"]
            box(x0, x1, y0, y1, z0, z1, C_SERVO_BOT, zorder=5)
            sx, sy = s["xf"], s["y"]
            box(sx - 8, sx + 8, sy - 8, sy + 8, p["z_inner_bot"] - p["spool_h"], p["z_inner_bot"],
                C_SPOOL, zorder=1)

    # top plate (slightly transparent)
    box(-x_lip, x_lip, p["flange_t"], ye, p["z_inner_top"], p["z_outer_top"], C_TOP, alpha=0.55, zorder=7)
    box(-p["x_top_wall_out"], -p["x_top_wall_in"], p["flange_t"], ye, -p["wall_overlap_z"], p["z_outer_top"],
        "#3E6580", alpha=0.45, zorder=6)
    box(p["x_top_wall_in"], p["x_top_wall_out"], p["flange_t"], ye, -p["wall_overlap_z"], p["z_outer_top"],
        "#3E6580", alpha=0.45, zorder=6)

    # labels in projected space
    def T(x, y, z, txt, **k):
        px, py = proj(x, y, z)
        ax.text(px, py, txt, fontsize=6.2, **k)

    T(0, -8, 50, "Plaque supérieure (U)", color=C_TOP, fontweight="bold", ha="center")
    T(0, -8, -52, "Plaque inférieure (U) + bride poignet", color="#7A5A20", fontweight="bold", ha="center")
    T(0, ye + 8, 40, "Coude ouvert", color="#7A1F1F", ha="center")
    T(50, 80, 8, "Flancs en U\ngrille M3 pas 15 mm", color="#333", ha="left")
    ax.set_aspect("equal")
    # bounds
    corners = [proj(x, y, z) for x in (-50, 50) for y in (-10, ye + 10) for z in (-55, 55)]
    ax.set_xlim(min(c[0] for c in corners) - 5, max(c[0] for c in corners) + 20)
    ax.set_ylim(min(c[1] for c in corners) - 5, max(c[1] for c in corners) + 10)


def fig_chassis():
    fig = plt.figure(figsize=(13.5, 10.2), facecolor="white")
    fig.suptitle("MateBot v11 — châssis avant-bras, deux plaques en U  (non testé)",
                 fontsize=13, fontweight="bold", y=0.98)
    ax1 = fig.add_axes([0.05, 0.07, 0.40, 0.86])
    ax2 = fig.add_axes([0.48, 0.10, 0.50, 0.80])
    draw_top_view(ax1, with_tubes=False, with_patterns=True)
    ax1.set_title("Vue de dessus  —  gros rond = bobine dessus, point = bobine dessous", fontsize=9)
    draw_34(ax2)
    ax2.set_title("Vue de 3/4  —  les deux plaques en U enserrent la rangée de 8 servos", fontsize=9)
    # legend
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=C_SPOOL, markeredgecolor="#6A4A10",
               markersize=9, label="Bobine sur le dessus (gros rond)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#222",
               markersize=5, label="Bobine en dessous (petit point)"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=C_SERVO_TOP,
               markersize=8, label="Servo face dorsale (TL / TR)"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=C_SERVO_BOT,
               markersize=8, label="Servo face palmaire (BL / BR)"),
        Line2D([0], [0], color="#1F4E79", marker="o", markerfacecolor="none",
               markersize=6, lw=0, markeredgecolor="#1F4E79", label="Grille M3 supports de coque"),
    ]
    fig.legend(handles=handles, loc="lower right", fontsize=7.5, frameon=False,
               bbox_to_anchor=(0.98, 0.01))
    fig.text(0.48, 0.02,
             "Séquence poignet → coude : TL, TR, BL, BR, répétée.  Axe long du servo en travers de l'avant-bras.  "
             "Vis M2×6 dans les oreilles, accès depuis l'extérieur.",
             fontsize=7, color="#333")
    out = os.path.join(DOCS, "forearm_chassis_preview.png")
    fig.savefig(out, dpi=140)
    plt.close()
    print("wrote", out)
    return out


def fig_parts():
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.6), facecolor="white")
    fig.suptitle("MateBot v11 — pièces à imprimer  (chaque demi < 250 mm)", fontsize=12, fontweight="bold")
    info = [
        ("Plaque sup. poignet", "forearm_plate_top_wrist", "79 × 188 × 38 mm", C_TOP),
        ("Plaque sup. coude", "forearm_plate_top_elbow", "79 × 168 × 38 mm", C_TOP),
        ("Plaque inf. poignet\n(+ bride 6 vis M2)", "forearm_plate_bottom_wrist", "88 × 196 × 82 mm", C_BOT),
        ("Plaque inf. coude", "forearm_plate_bottom_elbow", "79 × 168 × 38 mm", C_BOT),
    ]
    # schematic plan of each half
    x_lip = p["x_bot_wall_out"] + p["lip"]
    for ax, (title, fn, dim, col) in zip(axes, info):
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=9)
        if "wrist" in fn:
            y0, y1 = (0 if "bottom" in fn else p["flange_t"]), p["y_cut"] + p["lap"] / 2
        else:
            y0, y1 = p["y_cut"] - p["lap"] / 2, ye
        x0 = -44 if "bottom" in fn and "wrist" in fn else -x_lip
        x1 = 44 if "bottom" in fn and "wrist" in fn else x_lip
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=col,
                               edgecolor="#222", lw=0.8, alpha=0.85))
        # show stations that live on this half
        for s in sts:
            if not (y0 - 5 <= s["y"] <= y1 + 5):
                continue
            sx0, sx1, sy0, sy1 = servo_rect(s)
            ax.add_patch(Circle((s["xf"], s["y"]), 8, facecolor=C_SPOOL if s["face"]==("top" if "top" in fn else "bottom") else "#eee",
                                edgecolor="#444", lw=0.5))
        ax.set_xlim(x0 - 8, x1 + 8)
        ax.set_ylim(y0 - 10, y1 + 10)
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(0.5, -0.08, dim, transform=ax.transAxes, ha="center", fontsize=7.5, color="#333")
    fig.text(0.5, 0.02,
             "Plus 8× spool_r8 (inchangé, Ø22 × 11,5 mm, cercle de 14 mm, vis M3×6).  "
             "Impression : PETG, 5 parois, 30 % gyroid, 0,2 mm.  Plaques : semelle vers le plateau.",
             ha="center", fontsize=7.5, color="#333")
    fig.tight_layout(rect=(0, 0.06, 1, 0.92))
    out = os.path.join(DOCS, "forearm_parts_preview.png")
    fig.savefig(out, dpi=140)
    plt.close()
    print("wrote", out)
    return out


def fig_tubes():
    fig = plt.figure(figsize=(13.2, 10.4), facecolor="white")
    fig.suptitle("MateBot v11 — chemin des tubes PTFE et motifs de fixation  (légendes en français)",
                 fontsize=12.5, fontweight="bold", y=0.98)
    ax = fig.add_axes([0.05, 0.08, 0.58, 0.86])
    draw_top_view(ax, with_tubes=True, with_patterns=True)
    ax.set_title("Vue de dessus  —  trait plein = face dorsale, pointillé = face palmaire", fontsize=9)

    # side panel: patterns + routing notes
    axp = fig.add_axes([0.66, 0.08, 0.32, 0.86])
    axp.set_axis_off()
    axp.set_xlim(0, 1)
    axp.set_ylim(0, 1)
    lines = [
        ("Chemins des tubes", None),
        ("Pouce  —  plaque supérieure, lèvre radiale,", FINGER_COL["thumb"]),
        ("puis descente palmaire-radiale vers le poignet.", FINGER_COL["thumb"]),
        ("Index  —  plaque inférieure, voie palmaire", FINGER_COL["index"]),
        ("un peu en retrait (x = −20) pour laisser 18 mm", FINGER_COL["index"]),
        ("avec la descente du pouce.", FINGER_COL["index"]),
        ("Majeur  —  plaque supérieure, lèvre ulnaire,", FINGER_COL["middle"]),
        ("sortie par la fenêtre Ø34.", FINGER_COL["middle"]),
        ("Annulaire  —  plaque inférieure, lèvre ulnaire,", FINGER_COL["ring"]),
        ("couloir latéral palmaire.", FINGER_COL["ring"]),
        ("Rayon de courbure ≥ 30 mm, doigts ≥ 8 mm.", "#222"),
        ("", None),
        ("Motifs de fixation (repère F, mm)", None),
        ("Poignet : 6 × M2, passage Ø2,4, bride 6 mm", "#222"),
        ("  cercle R = 21 mm, angles 20°, 100°, 140°,", "#222"),
        ("  −140°, −100°, −20°.  Enregistrement", "#222"),
        ("  Ø33,6 × 2 mm dans la fenêtre Ø34.", "#222"),
        ("Servos : 32 × M2×6, passage Ø2,4, dans les", "#222"),
        ("  4 oreilles côté poulie folle.  Accès depuis", "#222"),
        ("  l'extérieur de la plaque opposée à la bobine.", "#222"),
        ("  4 mm de plaque + 2 mm dans l'oreille (2,8 mm).", "#222"),
        ("  Ne pas utiliser de M2×8 (butée sur le boîtier).", "#222"),
        ("Flancs en U : grille M3, pas 15 mm, 2 rangées", "#222"),
        ("  à z = ±5 mm, vis selon X (assemblage des", "#222"),
        ("  deux plaques + attaches futures).", "#222"),
        ("Lèvres des semelles : grille M3, pas 20 mm,", "#1F4E79"),
        ("  supports de coque, dessus et dessous.", "#1F4E79"),
        ("Coude (arrière ouvert) : 4 × M3 par plaque,", "#7A1F1F"),
        ("  rectangle 24 × 7 mm, pour une pièce coude.", "#7A1F1F"),
        ("Joint des demis : 4 × M3×10 + écrou par plaque,", "#7A3E00"),
        ("  demi-recouvrement 16 mm à Y = 186 mm, plus", "#7A3E00"),
        ("  une patte M3 de chaque côté.", "#7A3E00"),
        ("Bobine spool_r8 : 4 × M3×6 sur le cercle de", "#222"),
        ("  14 mm + vis centrale M3×6.  Inchangé.", "#222"),
    ]
    y = 0.98
    for text, col in lines:
        if text == "":
            y -= 0.012
            continue
        weight = "bold" if col is None else "normal"
        color = "#111" if col is None else col
        size = 8.2 if col is None else 7.2
        axp.text(0.0, y, text, va="top", ha="left", fontsize=size,
                 color=color, fontweight=weight, transform=axp.transAxes)
        y -= 0.026 if col is None else 0.023

    out = os.path.join(DOCS, "forearm_tubes_FR.png")
    fig.savefig(out, dpi=140)
    plt.close()
    print("wrote", out)
    return out


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    fig_chassis()
    fig_parts()
    fig_tubes()
    print("done")
