# v16 previews: top view + 3/4 view of the one flat plate, French labels.
# Usage: python render_forearm_mount_row.py
import os, math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, FancyArrow
from matplotlib.lines import Line2D
from forearm_mount_row import (
    P, stations, patterns, y_end, y_pack_start, y_pack_end, SHAFT_X, BODY_W, BODY_L,
)
from sts3215 import BODY_W as BW, SHAFT_FROM_OUT, SHAFT_FROM_CABLE, H_TO_HORN

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs")

p = P
sts = stations()
pat = patterns()
ye = y_end()
C_PLATE = "#9AAEB8"
C_WALL = "#6A7C88"
C_TOP = "#E08A3D"      # dorsal servo (spool through the plate)
C_BOT = "#3D8B6E"      # palmar servo (idler on the plate)
C_SPOOL = "#E4B84A"
FINGER_FR = dict(thumb="Pouce", index="Index", middle="Majeur", ring="Annulaire")
FINGER_COL = dict(thumb="#C0392B", index="#2471A3", middle="#1E8449", ring="#7D3C98")


def servo_rect(s):
    # body in XY: long axis across X, width along Y, centred on (0, y) in X
    x0, x1 = -BODY_L / 2, BODY_L / 2
    y0, y1 = s["y"] - BODY_W / 2, s["y"] + BODY_W / 2
    return x0, x1, y0, y1


def draw_top_view(ax, with_notes=True):
    ax.set_aspect("equal")
    w = p["half_w"]
    # plate
    ax.add_patch(Rectangle((-w, 0), 2 * w, ye,
                            facecolor="#D5DEE6", edgecolor="#3D4A55", lw=0.9, zorder=2))
    # front and back walls (shown as darker bands)
    ax.add_patch(Rectangle((-w, 0), 2 * w, p["wall_t"],
                            facecolor=C_WALL, edgecolor="#3D4A55", lw=0.6, zorder=3))
    ax.add_patch(Rectangle((-w, ye - p["wall_t"]), 2 * w, p["wall_t"],
                            facecolor=C_WALL, edgecolor="#3D4A55", lw=0.6, zorder=3))
    # cable holes in the front wall
    for x, z in pat["cable_front"]["holes"]:
        ax.add_patch(Circle((x, p["wall_t"] / 2), p["cable_hole_d"] / 2,
                            facecolor="white", edgecolor="#1F4E79", lw=0.8, zorder=4))
    # 8 x M3 in the end walls (4 per end, 2 per side, stacked in Z).
    # In top view the two Z-stacked holes of a column coincide; draw
    # one circle per column and label it 2x.
    if "end_m3" in pat:
        seen = set()
        for h in pat["end_m3"]["holes"]:
            y = p["wall_t"] / 2 if h["end"] == "front" else ye - p["wall_t"] / 2
            key = (h["end"], h["x"])
            if key in seen:
                continue
            seen.add(key)
            ax.add_patch(Circle((h["x"], y), 1.7, facecolor="white",
                                edgecolor="#1F4E79", lw=0.8, zorder=5))
            ax.text(h["x"], y, "2×", ha="center", va="center",
                    fontsize=4.5, color="#1F4E79", zorder=6, fontweight="bold")
    # M2 post footprints (clipped in CAD; drawn as target OD here)
    if "servo_idler_m2" in pat:
        r = p.get("m2_boss_od", 9.4) / 2
        for h in pat["servo_idler_m2"]["holes"]:
            ax.add_patch(Circle((h["x"], h["y"]), r, facecolor="#c8b89a",
                                edgecolor="#5a4a2a", lw=0.35, alpha=0.45, zorder=4))

    for s in sts:
        x0, x1, y0, y1 = servo_rect(s)
        col = C_TOP if s["face"] == "top" else C_BOT
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0,
                               facecolor=col, edgecolor="#222", lw=0.7,
                               alpha=0.95, zorder=7))
        if s["face"] == "top":
            ax.add_patch(Circle((s["xf"], s["y"]), 14.0, facecolor="none",
                                edgecolor="#333", lw=0.5, ls=":", zorder=8))
            ax.add_patch(Circle((s["xf"], s["y"]), 11.0, facecolor=C_SPOOL,
                                edgecolor="#6A4A10", lw=0.7, zorder=8, alpha=0.95))
            ax.add_patch(Circle((s["xf"], s["y"]), 8.0, facecolor="none",
                                edgecolor="#6A4A10", lw=0.5, zorder=8))
        else:
            ax.add_patch(Circle((s["xf"], s["y"]), 11.0, facecolor="none",
                                edgecolor="#555", lw=0.5, ls="--", zorder=8))
            ax.add_patch(Circle((s["xf"], s["y"]), 3.2, facecolor="#222",
                                edgecolor="#222", zorder=8))
            # M2 holes
            for h in pat["servo_idler_m2"]["holes"]:
                if h["i"] == s["i"]:
                    ax.add_patch(Circle((h["x"], h["y"]), 1.2, facecolor="none",
                                        edgecolor="#222", lw=0.5, zorder=9))
        label = f"{s['i']+1}  {FINGER_FR[s['finger']]} {s['ab']}"
        side = "G" if s["side"] == "left" else "D"
        face = "dessus" if s["face"] == "top" else "dessous"
        ax.text(0, s["y"], f"{label}\n{face}, arbre {side}",
                ha="center", va="center", fontsize=5.5, color="#111", zorder=10,
                fontweight="bold")

    if with_notes:
        ax.annotate("AVANT\n2 trous Ø10\npour les câbles bus",
                    xy=(16, p["wall_t"] / 2), xytext=(36, -18),
                    fontsize=6.5, ha="left", color="#1F4E79",
                    arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=0.6))
        ax.annotate("ARRIÈRE FERMÉ\nmur bas 3,5 × 16 mm",
                    xy=(0, ye - p["wall_t"] / 2), xytext=(36, ye - 8),
                    fontsize=6.5, ha="left", color="#7A1F1F",
                    arrowprops=dict(arrowstyle="->", color="#7A1F1F", lw=0.6))
        ax.annotate("Servos collés\njeu 0,4 mm, sans colle",
                    xy=(0, (sts[3]["y"] + sts[4]["y"]) / 2), xytext=(46, 110),
                    fontsize=6.5, ha="left", color="#7A3E00",
                    arrowprops=dict(arrowstyle="->", color="#7A3E00", lw=0.6))
        ax.annotate("4 × M3 par bout\n(2 de chaque côté)\nintérieur → extérieur",
                    xy=(24.0, p["wall_t"] / 2), xytext=(36, 86),
                    fontsize=6.5, ha="left", color="#1F4E79",
                    arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=0.6))
        ax.annotate("Poteaux M2\nparoi 3,5 mm\nvis fraisée M2×10",
                    xy=(20.25, 66.1 + 10.25), xytext=(36, 40),
                    fontsize=6.5, ha="left", color="#5a4a2a",
                    arrowprops=dict(arrowstyle="->", color="#5a4a2a", lw=0.6))
    ax.set_xlim(-40, 80)
    ax.set_ylim(-28, ye + 24)
    ax.set_xlabel("X (mm)  —  radial ←    → ulnaire")
    ax.set_ylabel("Y (mm)  —  avant → arrière")
    ax.grid(True, color="#ddd", lw=0.4)
    ax.set_axisbelow(True)


def draw_34(ax):
    ax.set_axis_off()
    a, b = 0.45, 0.38
    def proj(x, y, z):
        return x + a * y, z + b * y

    def poly(pts, fc, ec="#333", alpha=0.9, lw=0.5, zorder=2):
        xs, ys = zip(*[proj(*q) for q in pts])
        ax.fill(xs, ys, facecolor=fc, edgecolor=ec, lw=lw, alpha=alpha, zorder=zorder)

    w, ye_, t, h, wt = p["half_w"], ye, p["web_t"], p["wall_h"], p["wall_t"]
    # plate top (outer +Z) and a side edge
    poly([(-w, 0, t), (w, 0, t), (w, ye_, t), (-w, ye_, t)], "#C5D0D8", zorder=3)
    poly([(w, 0, 0), (w, ye_, 0), (w, ye_, t), (w, 0, t)], "#9AAEB8", zorder=4)
    # front wall (down in -Z)
    poly([(-w, 0, 0), (w, 0, 0), (w, 0, -h), (-w, 0, -h)], C_WALL, zorder=6)
    poly([(-w, 0, 0), (-w, wt, 0), (-w, wt, -h), (-w, 0, -h)], C_WALL, zorder=6)
    # back wall
    poly([(-w, ye_, 0), (w, ye_, 0), (w, ye_, -h), (-w, ye_, -h)], C_WALL, zorder=5)
    poly([(w, ye_ - wt, 0), (w, ye_, 0), (w, ye_, -h), (w, ye_ - wt, -h)], C_WALL, zorder=5)

    for s in sts:
        col = C_TOP if s["face"] == "top" else C_BOT
        x0, x1 = -BODY_L / 2, BODY_L / 2
        y0, y1 = s["y"] - BODY_W / 2, s["y"] + BODY_W / 2
        z0 = -H_TO_HORN - (p['m2_boss_h'] if s['face'] == 'bottom' else 0.0)
        z1 = -p['m2_boss_h'] if s['face'] == 'bottom' else 0.0
        # frontish face and top (against the plate)
        poly([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], col, alpha=0.85, zorder=8)
        poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], col, alpha=0.55, zorder=7)
        # spool mark
        cx, cy = proj(s["xf"], s["y"], 6.0 if s["face"] == "top" else -H_TO_HORN - 6)
        ax.plot(cx, cy, "o", color=C_SPOOL if s["face"] == "top" else "#222",
                ms=5 if s["face"] == "top" else 3, zorder=9,
                markeredgecolor="#6A4A10" if s["face"] == "top" else "#222")

    ax.set_aspect("equal")
    # labels
    def T(x, y, z, text, **k):
        px, py = proj(x, y, z)
        ax.text(px, py, text, fontsize=7, **k)
    T(0, -8, 10, "Plaque plate (4 mm)", color="#1F4E79", fontweight="bold", ha="center")
    T(0, ye_ + 8, -4, "Mur arrière", color="#7A1F1F", ha="left")
    T(0, -12, -h - 2, "Mur avant, 2 trous câbles", color="#1F4E79", ha="center")
    ax.set_title("Vue de 3/4  —  une seule plaque plate, servos dessous", fontsize=9)


def fig_chassis():
    fig = plt.figure(figsize=(13.2, 8.6), facecolor="white")
    fig.suptitle("MateBot v16 — plaque plate 56 mm, 4 × M3 par extrémité et poteaux M2  (non testé)",
                 fontsize=13, fontweight="bold")
    ax = fig.add_axes([0.05, 0.08, 0.48, 0.82])
    draw_top_view(ax)
    ax.set_title("Vue de dessus  —  gros rond = bobine à travers la plaque, point = poulie folle contre la plaque",
                 fontsize=8)
    ax2 = fig.add_axes([0.55, 0.18, 0.42, 0.62])
    draw_34(ax2)
    fig.text(0.75, 0.10,
             "Séquence avant → arrière : TL, TR, BL, BR, répétée.\n"
             "Axe long du servo en travers. Jeu 0,4 mm, sans colle.\n"
             "v15 (8 trous dans la toile) est remplacé.",
             ha="center", fontsize=7.5, color="#333")
    # legend
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_SPOOL, markeredgecolor="#6A4A10",
               markersize=8, label="Bobine à travers la plaque (Ø28)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#222",
               markersize=5, label="Poulie folle sur poteaux (M2×10 fraisée)"),
        Rectangle((0, 0), 1, 1, facecolor=C_TOP, edgecolor="#222", label="Servo face dorsale (TL / TR)"),
        Rectangle((0, 0), 1, 1, facecolor=C_BOT, edgecolor="#222", label="Servo face palmaire (BL / BR)"),
    ]
    ax2.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.08),
               frameon=False, fontsize=7)
    out = os.path.join(DOCS, "forearm_chassis_preview.png")
    fig.savefig(out, dpi=140)
    plt.close()
    print("wrote", out)
    return out


def fig_parts():
    fig, ax = plt.subplots(1, 1, figsize=(8.2, 5.6), facecolor="white")
    fig.suptitle("MateBot v16 — pièce à imprimer  (une plaque plate, ≤ 250 mm)",
                 fontsize=12, fontweight="bold")
    w, ye_ = p["half_w"], ye
    ax.set_aspect("equal")
    ax.set_title("Plaque avant-bras (une pièce)", fontsize=9)
    ax.add_patch(Rectangle((-w, 0), 2 * w, ye_, facecolor="#9AAEB8",
                           edgecolor="#222", lw=0.8, alpha=0.9))
    ax.add_patch(Rectangle((-w, 0), 2 * w, p["wall_t"], facecolor=C_WALL,
                           edgecolor="#222", lw=0.5))
    ax.add_patch(Rectangle((-w, ye_ - p["wall_t"]), 2 * w, p["wall_t"],
                           facecolor=C_WALL, edgecolor="#222", lw=0.5))
    for x, z in pat["cable_front"]["holes"]:
        ax.add_patch(Circle((x, p["wall_t"] / 2), p["cable_hole_d"] / 2,
                            facecolor="white", edgecolor="#1F4E79", lw=0.8))
    if "end_m3" in pat:
        seen = set()
        for h in pat["end_m3"]["holes"]:
            y = p["wall_t"] / 2 if h["end"] == "front" else ye_ - p["wall_t"] / 2
            key = (h["end"], h["x"])
            if key in seen:
                continue
            seen.add(key)
            ax.add_patch(Circle((h["x"], y), 1.7, facecolor="white",
                                edgecolor="#1F4E79", lw=0.8))
            ax.text(h["x"], y, "2×", ha="center", va="center",
                    fontsize=4.5, color="#1F4E79", fontweight="bold")
    r_post = p.get("m2_boss_od", 9.4) / 2
    for h in pat.get("servo_idler_m2", {}).get("holes", []):
        ax.add_patch(Circle((h["x"], h["y"]), r_post, facecolor="#c8b89a",
                            edgecolor="#5a4a2a", lw=0.35, alpha=0.4))
    for s in sts:
        if s["face"] == "top":
            ax.add_patch(Circle((s["xf"], s["y"]), 14, facecolor="#eee",
                                edgecolor="#333", lw=0.6, ls=":"))
            ax.text(s["xf"], s["y"], "Ø28", ha="center", va="center", fontsize=5.5, color="#333")
        else:
            ax.add_patch(Circle((s["xf"], s["y"]), 11, facecolor="#eee",
                                edgecolor="#555", lw=0.5, ls="--"))
            for h in pat["servo_idler_m2"]["holes"]:
                if h["i"] == s["i"]:
                    ax.add_patch(Circle((h["x"], h["y"]), 1.2, facecolor="none",
                                        edgecolor="#222", lw=0.5))
    ax.set_xlim(-w - 10, w + 10)
    ax.set_ylim(-16, ye_ + 16)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, -0.06,
            f"56,0 × {ye_:.2f}".replace(".", ",") + " × 20,0 mm  (plaque 4 mm + murs 16 mm)",
            transform=ax.transAxes, ha="center", fontsize=8, color="#333")
    fig.text(0.5, 0.03,
             "Plus 8× spool_r8 (inchangé, Ø22 × 11,5 mm, cercle de 14 mm, vis M3×6).\n"
             "Impression : PETG, 5 parois, 30 % gyroid, 0,2 mm.  Face extérieure sur le plateau, murs vers le haut, sans support.",
             ha="center", fontsize=7.2, color="#333")
    fig.tight_layout(rect=(0, 0.08, 1, 0.92))
    out = os.path.join(DOCS, "forearm_parts_preview.png")
    fig.savefig(out, dpi=140)
    plt.close()
    print("wrote", out)
    return out


def fig_tubes():
    # Kept as the third annotated drawing (cables + mounting), French labels.
    fig = plt.figure(figsize=(13.2, 9.6), facecolor="white")
    fig.suptitle("MateBot v16 — trous, vis et câbles  (légendes en français)",
                 fontsize=12.5, fontweight="bold", y=0.98)
    ax = fig.add_axes([0.05, 0.08, 0.55, 0.84])
    draw_top_view(ax, with_notes=True)
    ax.set_title("Vue de dessus", fontsize=9)

    axp = fig.add_axes([0.64, 0.08, 0.34, 0.84])
    axp.set_axis_off()
    axp.set_xlim(0, 1)
    axp.set_ylim(0, 1)
    lines = [
        ("La plaque", None),
        ("Une seule plaque plate de 4 mm, à peine plus", "#222"),
        ("longue que les 8 servos collés (200,56 mm", "#222"),
        ("+ deux murs de 3,5 mm). Largeur 56 mm", "#222"),
        ("(comme v13 ; la plaque v14 de 78 mm est", "#222"),
        ("abandonnée).", "#222"),
        ("Mur arrière bas (3,5 × 16 mm), fermé.", "#7A1F1F"),
        ("Mur avant bas, deux trous Ø10 pour les", "#1F4E79"),
        ("câbles bus (x = ±16 mm).", "#1F4E79"),
        ("", None),
        ("Servos", None),
        ("Rangée unique, axe long en travers,", "#222"),
        ("TL / TR / BL / BR. Jeu 0,4 mm, sans colle.", "#7A3E00"),
        ("Pouce et majeur (dessus) : bobine à travers", C_TOP),
        ("une découpe Ø28. Pas de vis M2 sur cette", C_TOP),
        ("plaque : les oreilles du fouet sont 35 mm", C_TOP),
        ("plus loin, de l'autre côté.", C_TOP),
        ("Index et annulaire (dessous) : 4 × M2×10", C_BOT),
        ("fraisée 90° (DIN 7991) dans les oreilles", C_BOT),
        ("du fouet, depuis l'extérieur. Poteau", C_BOT),
        ("intérieur paroi 3,5 mm, haut 3,5 mm", C_BOT),
        ("(rogné côté voisin et palonnier : une paroi", C_BOT),
        ("circulaire Ø9,4 ne passe pas entre des", C_BOT),
        ("servos au jeu 0,4 mm). 4 mm de plaque +", C_BOT),
        ("3,5 mm de poteau + 2,5 mm dans l'oreille.", C_BOT),
        ("Pas de M2×12 (elle buterait dans le boîtier).", C_BOT),
        ("", None),
        ("Limite d'une seule plaque", None),
        ("Une plaque ne peut pas visser les 4 servos", "#7A3E00"),
        ("dont la bobine la traverse. Ils sont tenus", "#7A3E00"),
        ("par les voisins et le mur arrière seulement.", "#7A3E00"),
        ("Correctif le plus simple plus tard : une", "#7A3E00"),
        ("deuxième plaque plate identique sur l'autre", "#7A3E00"),
        ("face (toujours sans flancs en U). Ne pas", "#7A3E00"),
        ("utiliser les oreilles côté palonnier.", "#7A3E00"),
        ("", None),
        ("Attaches : 8 × M3 dans les murs", None),
        ("4 trous par extrémité, DEUX de chaque", "#1F4E79"),
        ("côté du centre (et des trous de câbles) :", "#1F4E79"),
        ("x = ±24 mm, z = −5,0 et −12,5 mm", "#1F4E79"),
        ("(rectangle 48 × 7,5 mm). Axe selon Y.", "#1F4E79"),
        ("Lamage Ø6,5 × 1,8 mm à l'intérieur du", "#1F4E79"),
        ("mur (tête bouton ISO 7380 affleurante).", "#1F4E79"),
        ("Vis de l'intérieur vers l'extérieur, à", "#1F4E79"),
        ("poser avant les servos. Pas de poteaux", "#1F4E79"),
        ("vers l'intérieur : le mur (3,5 mm) est", "#1F4E79"),
        ("contre le premier / dernier servo.", "#1F4E79"),
        ("Les 8 trous dans la toile (v15) sont retirés.", "#1F4E79"),
        ("", None),
        ("Câbles", None),
        ("Les sorties bus sont sur les côtés (±X).", "#1F4E79"),
        ("On les ramène vers l'avant par les 2 trous.", "#1F4E79"),
        ("Pas de logements de tubes sur cette plaque ;", "#222"),
        ("les gaines PTFE passent autour.", "#222"),
        ("", None),
        ("Bobine spool_r8 : 4 × M3×6 sur le cercle de", "#222"),
        ("14 mm + vis centrale M3×6. Inchangée.", "#222"),
        ("v15 (8 trous dans la toile) est remplacé.", "#7A3E00"),
    ]

    y = 0.995
    for text, col in lines:
        if text == "":
            y -= 0.007
            continue
        weight = "bold" if col is None else "normal"
        color = "#111" if col is None else col
        size = 7.4 if col is None else 6.2
        axp.text(0.0, y, text, va="top", ha="left", fontsize=size,
                 color=color, fontweight=weight, transform=axp.transAxes)
        y -= 0.018 if col is None else 0.016

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
