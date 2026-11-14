# MateBot v18 (UNTESTED): one minimal FLAT plate holding a single row of
# 8 x Feetech STS3215 (12 V). Bodies sit face-to-face (0.4 mm nominal gap,
# no glue). v17, v16, v15, v14 and v13 are superseded.
#
# Layout: the same packed row as v12/v13. Long axis ACROSS the forearm,
# output shaft perpendicular to the plate. Faces follow TL, TR, BL, BR,
# repeat (wrist / front -> elbow / back):
#   0-1 thumb  = top (dorsal),  shafts L then R
#   2-3 index  = bottom (palmar), shafts L then R
#   4-5 middle = top,            shafts L then R
#   6-7 ring   = bottom,         shafts L then R
# Each finger pair is two adjacent servos on the SAME face.
#
# The plate is a 4 mm flat rectangle, 56 mm wide, barely longer than the
# 8 packed bodies (8 x 24.72 + 7 x 0.4 = 200.56 mm) plus a low wall at
# each end. No U flanges, no second plate, no socket bosses, no wrist
# flange, no side-rail grid, no corner posts, no widening (v14's 78 mm
# plate is rejected). The two Ø10 cable holes of v13-v16 are gone.
#
# v17 additions, on top of that v13 plate (v16 is corrected: the end-wall
# holes are an ADDITION, not a replacement of the v15 web holes):
# - 8 x M3 clearance holes in the WEB, one over each servo body, on the
#   solid side opposite the spool / idler cut-out (the cable end).
#   x = -xf = ±12.50 mm, y = station y. Inside-to-outside along Z, with
#   an inner-face counterbore (Ø6.5 x 1.8 mm) so an ISO 7380 button head
#   sits flush and does not hit the servo. Fit these before the servos.
#   Restored from v15; v16 had dropped them by mistake.
# - BOTH end walls (front and back) have ONE semicircular arch cut-out,
#   centred at x = 0, radius 13 mm, open at the wall's free edge
#   (z = -16 mm, away from the web). The crown sits at z = -3 mm, leaving
#   a 3 mm lintel under the web. Opening at the free edge is 26 mm wide.
#   Cables and tubes pass through the arch. The back wall is no longer
#   closed; the remaining side legs and the lintel still stop the pack
#   in Y. A cylinder along Y, centred on the free edge, cuts the notch;
#   printed outer-face down the notch opens at the top of the wall, so
#   no supports are needed.
# - 8 x M3 clearance holes in the END WALLS, in addition to the web
#   holes: 4 per end (front and back), TWO on each side of the arc,
#   stacked in Z. Pattern: x = ±24 mm, z = -5.0 and -12.5 mm (rectangle
#   48 x 7.5 mm), same as v16. The 56 mm width is kept; the holes sit
#   in the side margins of the 16 mm walls, flanking the R13 arc with
#   about 8 mm of material (counterbore edge to arc). A shallow
#   counterbore on the inner face of each wall lets an M3 button head
#   sit flush so it does not hit the first/last servo (those faces are
#   flush with the wall). No inward posts: there is no gap between the
#   wall and the pack (the 3.5 mm wall is the meat around the hole).
#   Screws go from the inside of each end toward the outside, into the
#   later attachment; fit them before the servos.
# - Wall height is kept at 16 mm. The two stacked holes sit in the side
#   margins (x = ±24) and do not compete with the central arc for Z
#   space, so there is no need to raise the walls or place the pair
#   side by side horizontally.
# - The 16 M2 idler-ear holes (index, ring) each have a 3.5 mm-wall
#   post on the inside and a 90 deg countersink on the outer face for
#   a flat-head screw (M2x10 DIN 7991 / ISO 10642). A full 9.4 mm
#   cylinder does not fit between servos packed 0.4 mm apart (hole
#   centres across a gap are only 4.62 mm apart) and would also hit
#   the idler horn at the shaft-end holes, so each post is clipped
#   at the body side (staying out of the pack gap) and outside the
#   idler-horn keep-out. The posts stand 3.5 mm down from the web;
#   the four idler-facing servos sit on the ends of the posts
#   (3.5 mm further from the plate than in v13). Screw length is
#   4 mm web + 3.5 mm post + 2.5 mm into the 2.8 mm ear = 10 mm.
#   Do not use M2x12 (it would bottom on the housing).
# - v18: the M2 posts are also clipped on their inner side (toward
#   the centre of that servo's 4-hole pattern / the other 3 screws)
#   to clear a raised housing on the official STS3215 idler face.
#   Measured from the Waveshare ST3215.step: a rectangular step
#   (X 19.55 to 29.40 mm from the shaft toward the cable, Y ±8.94 mm)
#   standing 1.90 mm past the ear outer face, between the ears, on
#   the cable-end side of the horn. The 2D drawing shows this area
#   but does not dimension it. Keep-out = that outline + 0.4 mm.
#   It reaches only the two cable-end posts of each idler-facing
#   servo (closest official material 3.66 mm from those hole axes);
#   the shaft-end pair stays clear of it and is still clipped only
#   around the idler horn and the body/neighbour. Remaining wall
#   around the M2 hole (Ø2.4) at the housing cut is about 2.1 mm.
#
# Official 24.72 mm width already includes the ears (Waveshare 2D and
# STEP). 0.4 mm is the project's print allowance (CL).
#
# Frame F (local to this plate): origin at the front-centre of the plate,
# on the inner face (the face the servos sit against / the posts grow
# from). +X ulnar, +Y toward the back / elbow, +Z outward through the
# plate (servo bodies hang in -Z). M2 access is from the outside (+Z).
# M3 web-attachment access is from the inside (z = 0) toward the
# outside (z = +web_t). M3 end-attachment access is from the inside of
# each end wall (toward the pack), thread out at the front (y = 0) or
# the back (y = y_end).
#
# CadQuery. MateBot, CC BY 4.0.
#
# Usage:
#   python forearm_mount_row.py
# writes STEP/STL next to this file, or into ../step and ../stl.
# Does not overwrite spool_r8.
import cadquery as cq, math, os, sys
from sts3215 import (
    BODY_L, BODY_W, BODY_H_FLANGE, H_TO_HORN, H_BOTH_HORNS,
    SHAFT_FROM_OUT, SHAFT_FROM_CABLE, HORN_OD, HORN_BCD, HORN_HOLE_D, HORN_T,
    IDL_HOLES, MOUNT_HOLE_D, EAR_T_IDLER, IDLER_PROTRUSION, CL,
    IDL_HOUSING_X0, IDL_HOUSING_X1, IDL_HOUSING_HALF_W, IDL_HOUSING_H,
    idler_housing_rect, envelope, horn_holes_xy,
)

HERE = os.path.dirname(os.path.abspath(__file__))
STEP_DIR = os.path.join(HERE, "..", "step")
STL_DIR = os.path.join(HERE, "..", "stl")

# Shaft X that keeps every body centred on x=0 while the horn zig-zags.
# BODY_L/2 - SHAFT_FROM_OUT = 45.22/2 - 10.11 = 12.50 mm.
SHAFT_X = BODY_L / 2 - SHAFT_FROM_OUT  # 12.50

P = dict(
    cl=CL,
    web_t=4.0,              # plate thickness
    wall_t=3.5,             # front and back wall thickness
    wall_h=16.0,            # low end walls; kept, holes sit beside the arc
    pack_gap=0.4,           # nominal body-to-body gap (0-0.5 mm, no glue)
    half_w=28.0,            # 56 mm: same as v13; Ø28 cut-out at x=±12.50 needs |x|>=26.5
    spool_r=8.0, spool_flange=3.0, spool_base_t=2.0, groove_w=3.0, mid_flange=1.5,
    spool_top_t=2.0,
    spool_cut_d=28.0,       # spool flange is Ø22; 3 mm radial clearance
    idler_cut_d=22.0,       # clearance for the idler horn (protrudes 2.25 mm)
    m2_clear=2.4,
    m2_boss_wall=3.5,       # target annular wall around each M2 (clipped, see below)
    m2_boss_h=3.5,          # post height, into the body side; servos sit on the ends
    m2_csk_d=4.8,           # 90 deg countersink on the outer face (DIN 7991 M2 dk=4.0)
    m2_csk_angle=90.0,
    m3_clear=3.4,           # M3 clearance (inside of the end -> outside)
    m3_cbore_d=6.5,         # inner-face counterbore for an ISO 7380 M3 button head (dk=5.7)
    m3_cbore_h=1.8,         # flush with the inner face of the end wall
    end_m3_x=24.0,          # one column on each side of the arc
    end_m3_z=(-5.0, -12.5), # TWO holes per side, stacked in Z (4 per end wall)
    arc_r=13.0,             # semicircular arch in both end walls, open at z=-wall_h
)
P['m2_boss_od'] = P['m2_clear'] + 2 * P['m2_boss_wall']   # 9.4 mm, before clipping
P['spool_h'] = P['spool_base_t'] + P['groove_w'] + P['mid_flange'] + P['groove_w'] + P['spool_top_t']  # 11.5
P['pitch'] = BODY_W + P['pack_gap']   # 25.12 mm
P['pack_len'] = 8 * BODY_W + 7 * P['pack_gap']  # 200.56 mm, 8 bodies + 7 gaps

# TL, TR, BL, BR, repeat. Same-face adjacent pairs.
STATION_META = [
    dict(i=0, finger="thumb",  ab="A", face="top",    side="left"),
    dict(i=1, finger="thumb",  ab="B", face="top",    side="right"),
    dict(i=2, finger="index",  ab="A", face="bottom", side="left"),
    dict(i=3, finger="index",  ab="B", face="bottom", side="right"),
    dict(i=4, finger="middle", ab="A", face="top",    side="left"),
    dict(i=5, finger="middle", ab="B", face="top",    side="right"),
    dict(i=6, finger="ring",   ab="A", face="bottom", side="left"),
    dict(i=7, finger="ring",   ab="B", face="bottom", side="right"),
]


def stations(p=P):
    """Front-to-back list of 8 stations with positions in frame F.
    Bottom-face (idler) servos sit on the 3.5 mm M2 posts, so their
    shaft frame is 3.5 mm further from the plate than in v13."""
    y0 = p["wall_t"] + BODY_W / 2.0
    out = []
    for meta in STATION_META:
        i = meta["i"]
        y = y0 + i * p["pitch"]
        xf = -SHAFT_X if meta["side"] == "left" else SHAFT_X
        # Top-face: output horn (spool) on the plate, zf = 0.
        # Bottom-face: idler ear on the post ends, zf = -H_TO_HORN - m2_boss_h.
        zf = 0.0 if meta["face"] == "top" else -H_TO_HORN - p["m2_boss_h"]
        rec = dict(meta)
        rec.update(xf=xf, y=y, zf=zf, y_shaft=y)
        out.append(rec)
    return out


def y_end(p=P):
    """Overall plate length: front wall + packed bodies + back wall."""
    return p["wall_t"] + p["pack_len"] + p["wall_t"]


def y_pack_start(p=P):
    return p["wall_t"]


def y_pack_end(p=P):
    return p["wall_t"] + p["pack_len"]


def groove_zs(face, p=P):
    """Groove centre Z in F. Top-face spools go through the plate (+Z);
    bottom-face spools stand on the far side of the body (-Z)."""
    d1 = p["spool_base_t"] + p["groove_w"] / 2
    d2 = p["spool_base_t"] + p["groove_w"] + p["mid_flange"] + p["groove_w"] / 2
    if face == "top":
        return (d1, d2)
    return (-H_TO_HORN - p["m2_boss_h"] - d1, -H_TO_HORN - p["m2_boss_h"] - d2)


def place_S(shape, xf, yf, zf, face="top", side="left"):
    """Map a solid in servo frame S into F.
    Long axis (cable, +X_s) is ACROSS the forearm.
    Top / left: +X_s along +X_f, +Z_s along +Z_f.
    Right: 180 deg about Z. Bottom: 180 deg about X first."""
    if face == "bottom":
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    if side == "right":
        shape = shape.rotate((0, 0, 0), (0, 0, 1), 180)
    return shape.translate((xf, yf, zf))


def loc_S(xf, yf, zf, face="top", side="left"):
    from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
    acc = gp_Trsf()
    if face == "bottom":
        rx = gp_Trsf()
        rx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.radians(180))
        acc = rx
    if side == "right":
        rz = gp_Trsf()
        rz.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(180))
        acc = rz.Multiplied(acc)
    tt = gp_Trsf()
    tt.SetTranslation(gp_Vec(xf, yf, zf))
    return cq.Location(tt.Multiplied(acc))


def idler_holes_F(xf, yf, zf, face, side):
    """Four idler-ear hole centres in F (x, y, z at the idler face)."""
    holes = []
    z_s = -H_TO_HORN
    for Xs, Ys in IDL_HOLES:
        x1, y1, z1 = Xs, Ys, z_s
        if face == "bottom":
            y1, z1 = -y1, -z1
        if side == "right":
            x1, y1 = -x1, -y1
        holes.append((xf + x1, yf + y1, zf + z1))
    return holes


# ---------------------------------------------------------------------------
# Spool, official horn pattern (BCD 14 mm from the Waveshare 2D drawing).
# Unchanged from v9/v10/v11/v12/v13/v14 spool_r8.
# ---------------------------------------------------------------------------
def spool_r8(p=P):
    """Identical to v9/v10 spool_r8 — official 14 mm BCD, do not change."""
    r, fl = p["spool_r"], p["spool_flange"]
    h = cq.Workplane("XY").circle(r + fl).extrude(p["spool_base_t"])
    h = h.faces(">Z").workplane().circle(r).extrude(p["groove_w"])
    h = h.faces(">Z").workplane().circle(r + 2.0).extrude(p["mid_flange"])
    h = h.faces(">Z").workplane().circle(r).extrude(p["groove_w"])
    h = h.faces(">Z").workplane().circle(r + fl).extrude(p["spool_top_t"])
    h = h.faces(">Z").workplane().hole(6.5)
    h = h.faces(">Z").workplane().pushPoints(horn_holes_xy()).hole(3.4)
    z1 = p["spool_base_t"] + p["groove_w"] / 2
    z2 = p["spool_base_t"] + p["groove_w"] + p["mid_flange"] + p["groove_w"] / 2
    for z in (z1, z2):
        h = h.cut(cq.Workplane("YZ").workplane(offset=-20).center(r - 1.0, z).circle(0.8).extrude(40))
    return h


def fuse_fuzzy(shapes, tol=0.08):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    acc = shapes[0].val() if hasattr(shapes[0], "val") else shapes[0]
    for sh in shapes[1:]:
        sv = sh.val() if hasattr(sh, "val") else sh
        op = BRepAlgoAPI_Fuse(acc.wrapped if hasattr(acc, "wrapped") else acc,
                              sv.wrapped if hasattr(sv, "wrapped") else sv)
        op.SetFuzzyValue(tol)
        op.Build()
        acc = cq.Shape.cast(op.Shape())
    try:
        u = ShapeUpgrade_UnifySameDomain(acc.wrapped, True, True, True)
        u.Build()
        acc = cq.Shape.cast(u.Shape())
    except Exception:
        pass
    return cq.Workplane("XY").add(acc)


def _box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def _cyl(r, h, origin, direction):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, h, cq.Vector(*origin), cq.Vector(*direction)))


def _cone(r1, r2, h, origin, direction):
    return cq.Workplane("XY").add(cq.Solid.makeCone(r1, r2, h, cq.Vector(*origin), cq.Vector(*direction)))


def _cut_cyls_z(wp, points_xy, z0, h, r):
    if not points_xy:
        return wp
    solids = [_cyl(r, h, (x, y, z0), (0, 0, 1)).val() for x, y in points_xy]
    comp = cq.Compound.makeCompound(solids)
    return wp.cut(comp)


def _cut_cyls_y(wp, points_xz, y0, h, r):
    if not points_xz:
        return wp
    solids = [_cyl(r, h, (x, y0, z), (0, 1, 0)).val() for x, z in points_xz]
    comp = cq.Compound.makeCompound(solids)
    return wp.cut(comp)


def attach_m3_holes(p=P):
    """Eight M3 clearance holes in the web, one over each servo body,
    on the solid side opposite the spool / idler cut-out (cable end).
    x = -xf (the mirrored shaft column), y = station y.
    Screws go inside -> outside: head in the inner-face counterbore
    (flush at z = 0), thread out at z = +web_t. Restored from v15."""
    holes = []
    for s in stations(p):
        holes.append(dict(
            i=s["i"], finger=s["finger"], ab=s["ab"], face=s["face"],
            x=round(-s["xf"], 3), y=round(s["y"], 3), z=0.0,
            dir="Z", screw="M3", d=p["m3_clear"],
            access="inside -> outside",
        ))
    return holes


def end_m3_holes(p=P):
    """Eight M3 clearance holes in the end walls: 4 per end (front and
    back), TWO on each side of the arch. x = ±end_m3_x, z in end_m3_z.
    Axis along Y. Head in a counterbore on the inner face of the wall,
    thread out to the later attachment on the outside of each end.
    These are in ADDITION to the 8 web M3 holes."""
    ye = y_end(p)
    holes = []
    for end, y_out, y_in in (
        ("front", 0.0, p["wall_t"]),
        ("back", ye, ye - p["wall_t"]),
    ):
        for x in (-p["end_m3_x"], p["end_m3_x"]):
            for z in p["end_m3_z"]:
                holes.append(dict(
                    end=end, x=round(x, 3),
                    y_out=round(y_out, 3), y_in=round(y_in, 3),
                    z=round(z, 3),
                    dir="Y", screw="M3", d=p["m3_clear"],
                    access="inside of the end -> outside",
                ))
    return holes


def m2_hole_xy(p=P):
    """(x, y) of the 16 M2 idler-ear holes."""
    pts = []
    for s in stations(p):
        if s["face"] != "bottom":
            continue
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            pts.append((x, y))
    return pts


def patterns(p=P):
    """Catalogue: countersunk M2 idler screws of the four plate-facing
    servos, 8 web M3 attachments (v15, restored), 8 end-wall M3
    attachments (4 per end, 2 per side of the arc), spool and idler
    cut-outs, one arch in each end wall. No side-rail grid, no
    inward end posts, no wrist, no Ø10 cable holes."""
    sts = stations(p)
    m2 = []
    for s in sts:
        if s["face"] != "bottom":
            continue
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            m2.append(dict(i=s["i"], finger=s["finger"], ab=s["ab"],
                           face=s["face"], x=round(x, 3), y=round(y, 3), z=round(z, 3),
                           access="outside / +Z, countersunk",
                           screw="M2x10 DIN 7991 / ISO 10642 flat head"))
    spool_cuts = [(s["xf"], s["y"]) for s in sts if s["face"] == "top"]
    idler_cuts = [(s["xf"], s["y"]) for s in sts if s["face"] == "bottom"]
    return dict(
        servo_idler_m2=dict(
            name_fr="Fixation des servos — oreilles côté poulie folle (index, annulaire)",
            screw="M2x10 fraisée 90° (DIN 7991 / ISO 10642), passage Ø2.4, 16 vis",
            holes=m2,
            note=("4 trous par servo dont les oreilles du fouet sont contre les "
                  "poteaux (index et annulaire). Accès depuis l'extérieur (+Z), "
                  "fraisage 90° Ø4,8 mm sur la face extérieure. Poteau intérieur "
                  "paroi 3,5 mm (Ø 9,4 mm, rogné côté voisin et côté palonnier), "
                  "haut 3,5 mm. 4 mm de plaque + 3,5 mm de poteau + 2,5 mm dans "
                  "l'oreille (2,8 mm). Ne pas utiliser de M2×12. Pouce et majeur : "
                  "pas de vis M2 sur cette plaque (bobine en travers, Ø28)."),
        ),
        attach_m3=dict(
            name_fr="Attaches diverses — 8 × M3 dans la plaque, au-dessus des servos",
            screw="M3 passage Ø3.4, tête bouton affleurante à l'intérieur, vis de l'intérieur vers l'extérieur",
            holes=attach_m3_holes(p),
            note=("Un trou par servo, sur le côté plein opposé à la découpe "
                  "bobine / fouet (côté câble), à x = −xf = ±12,50 mm, y = axe "
                  "du servo. Lamage Ø6,5 × 1,8 mm sur la face intérieure pour "
                  "une tête bouton ISO 7380 affleurante, afin de ne pas toucher "
                  "le servo. La tige ressort à l'extérieur (z = +4). Ces 8 "
                  "trous de v15 sont rétablis ; les 8 trous d'extrémité s'y "
                  "ajoutent. Mettre les vis avant les servos (la tête est sous "
                  "le corps)."),
        ),
        end_m3=dict(
            name_fr="Attaches avant et arrière — 4 × M3 par extrémité (2 de chaque côté de l'arc)",
            screw="M3 passage Ø3.4, tête bouton affleurante à l'intérieur du mur, vis de l'intérieur vers l'extérieur",
            holes=end_m3_holes(p),
            note=("4 trous par mur d'extrémité, deux de chaque côté de l'arc : "
                  "x = ±24 mm, z = −5,0 et −12,5 mm (rectangle 48 × 7,5 mm). "
                  "Axe selon Y. Lamage Ø6,5 × 1,8 mm sur la face intérieure "
                  "du mur pour une tête bouton ISO 7380 affleurante (le premier "
                  "/ dernier servo est contre cette face). La tige ressort à "
                  "l'extérieur pour une attache à dessiner plus tard. Pas de "
                  "poteaux vers l'intérieur : il n'y a pas de jeu entre le mur "
                  "et les servos (le mur de 3,5 mm fait office de paroi). "
                  "Mettre les vis avant les servos. S'ajoutent aux 8 trous "
                  "dans la toile, ils ne les remplacent pas."),
        ),
        spool_cuts=dict(
            name_fr="Découpes bobine Ø28 (pouce, majeur)",
            holes=spool_cuts,
        ),
        idler_cuts=dict(
            name_fr="Jeu Ø22 pour le palonnier fouet (index, annulaire)",
            holes=idler_cuts,
        ),
        end_arcs=dict(
            name_fr="Arc semi-circulaire dans chaque mur d'extrémité (R13, ouvert au bord libre)",
            holes=[(0.0, -p["wall_h"])] * 2,
            note=("Un arc de rayon 13 mm, centré en x = 0 sur le bord libre "
                  "(z = −16 mm) de chaque mur (avant et arrière). Ouverture "
                  "de 26 mm au bord libre, clé de voûte à z = −3 mm (linteau "
                  "de 3 mm sous la toile). Les deux trous Ø10 de v13–v16 sont "
                  "retirés. Les câbles bus et les gaines passent par l'arc. "
                  "Le mur arrière n'est plus fermé ; les jambages et le "
                  "linteau arrêtent toujours la rangée en Y. Hauteur des murs "
                  "inchangée (16 mm) : les vis empilées sont dans les marges "
                  "latérales et ne disputent pas l'espace de l'arc."),
        ),
        spool_m3=dict(
            name_fr="Bobine spool_r8 sur le palonnier",
            screw="4 x M3x6 sur le cercle de 14 mm + vis centrale M3x6",
            note="Inchangé depuis v9. Pas dans cette plaque.",
        ),
    )


def xy_S_to_F(Xs, Ys, s):
    """Map a point in the servo's idler-face XY (frame S) into plate frame F."""
    x, y = Xs, Ys
    if s["face"] == "bottom":
        y = -y
    if s["side"] == "right":
        x, y = -x, -y
    return s["xf"] + x, s["y"] + y


def housing_keepout_F(s, p, clear=CL):
    """Official idler-face housing, mapped into F, expanded by clear and
    extruded through the post height. Minkowski offset of the sharp
    rectangle (side slabs + r=clear corner cylinders)."""
    x0, x1, y0, y1 = idler_housing_rect(0.0)
    corners = [xy_S_to_F(x, y, s) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs, ys = zip(*corners)
    xa, xb, ya, yb = min(xs), max(xs), min(ys), max(ys)
    h = p["m2_boss_h"]
    parts = [
        _box(xa, xb, ya, yb, -h - 1, 1),
        _box(xa - clear, xa, ya, yb, -h - 1, 1),
        _box(xb, xb + clear, ya, yb, -h - 1, 1),
        _box(xa, xb, ya - clear, ya, -h - 1, 1),
        _box(xa, xb, yb, yb + clear, -h - 1, 1),
        _cyl(clear, h + 2, (xa, ya, 1.0), (0, 0, -1)),
        _cyl(clear, h + 2, (xb, ya, 1.0), (0, 0, -1)),
        _cyl(clear, h + 2, (xb, yb, 1.0), (0, 0, -1)),
        _cyl(clear, h + 2, (xa, yb, 1.0), (0, 0, -1)),
    ]
    return fuse_fuzzy(parts)


def _m2_posts(p, sts):
    """Inside posts around each M2 hole: 3.5 mm target wall, 3.5 mm tall,
    clipped so they stay inside their own servo's body outline (out of
    the 0.4 mm pack gap and out of the neighbour), out of the
    idler-horn keep-out, and out of the official idler-face housing
    step (plus 0.4 mm) on the inner side of the 4-hole pattern.
    Printable, growing down from the web."""
    r = p["m2_clear"] / 2.0 + p["m2_boss_wall"]
    h = p["m2_boss_h"]
    keep_r = HORN_OD / 2.0 + 0.4
    groups = []
    for s in sts:
        if s["face"] != "bottom":
            continue
        raw = []
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            raw.append(_cyl(r, h, (x, y, 0.0), (0, 0, -1)))
        posts = fuse_fuzzy(raw)
        # Stay 0.1 mm inside this servo's body in Y, so nothing enters
        # the pack gap or the neighbour. A thin gap slab is not enough:
        # the unclipped Ø9.4 boss reaches 2.2 mm into the next body.
        y0 = s["y"] - BODY_W / 2.0 + 0.1
        y1 = s["y"] + BODY_W / 2.0 - 0.1
        clips = [
            _box(-p["half_w"] - 5, p["half_w"] + 5, -20.0, y0, -h - 1, 1),
            _box(-p["half_w"] - 5, p["half_w"] + 5, y1, y_end(p) + 20.0, -h - 1, 1),
            _cyl(keep_r, h + 2, (s["xf"], s["y"], 1.0), (0, 0, -1)),
            housing_keepout_F(s, p, CL),
        ]
        comp = cq.Compound.makeCompound([c.val() for c in clips])
        groups.append(posts.cut(comp))
    return groups


def plate(p=P):
    """One flat 4 mm plate, a low wall at each end with a central arch
    and 4 M3 beside it, clipped M2 posts, countersunk M2, 8 M3 in the
    web over the bodies."""
    sts = stations(p)
    ye = y_end(p)
    w = p["half_w"]
    t, h, wt = p["web_t"], p["wall_h"], p["wall_t"]
    web = _box(-w, w, 0.0, ye, 0.0, t)
    front = _box(-w, w, 0.0, wt, -h, 0.0)
    back = _box(-w, w, ye - wt, ye, -h, 0.0)
    body = fuse_fuzzy([web, front, back] + _m2_posts(p, sts))

    spool_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "top"]
    idler_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "bottom"]
    # Through the web (and a little past) so the spool / idler horn is free.
    body = _cut_cyls_z(body, spool_pts, -1.0, t + 2.0, p["spool_cut_d"] / 2)
    body = _cut_cyls_z(body, idler_pts, -1.0, t + 2.0, p["idler_cut_d"] / 2)

    m2_pts = m2_hole_xy(p)
    # M2 through the web and the post (z = -boss_h .. +web_t).
    body = _cut_cyls_z(body, m2_pts, -p["m2_boss_h"] - 1.0,
                       t + p["m2_boss_h"] + 2.0, p["m2_clear"] / 2)
    # 90 deg countersink on the outer face (z = web_t), opening outward.
    # Cone: diameter m2_csk_d at z=web_t, point  m2_csk_d/2  mm into the web
    # (90 deg => height = radius). Meets the Ø2.4 bore at depth 1.2 mm,
    # which matches a DIN 7991 M2 head (k = 1.2, dk = 4.0) with print
    # clearance on the head diameter (4.8 mm).
    csk_r = p["m2_csk_d"] / 2.0
    cones = [_cone(csk_r, 0.0, csk_r, (x, y, t), (0, 0, -1)).val() for x, y in m2_pts]
    if cones:
        body = body.cut(cq.Compound.makeCompound(cones))

    # Semicircular arch in BOTH end walls, open at the free edge
    # (z = -wall_h). A cylinder along Y, centred on that edge, cuts a
    # half-disk into the wall. Printed outer-face down, the notch opens
    # at the top of the wall (no supports).
    body = body.cut(_cyl(p["arc_r"], wt + 2.0, (0.0, -1.0, -h), (0, 1, 0)))
    body = body.cut(_cyl(p["arc_r"], wt + 2.0, (0.0, ye - wt - 1.0, -h), (0, 1, 0)))

    # 8 x M3 through the web, inside -> outside, plus an inner
    # counterbore so the button head sits flush at z = 0.
    m3_pts = [(h["x"], h["y"]) for h in attach_m3_holes(p)]
    body = _cut_cyls_z(body, m3_pts, -1.0, t + 2.0, p["m3_clear"] / 2)
    body = _cut_cyls_z(body, m3_pts, -0.2, p["m3_cbore_h"] + 0.2, p["m3_cbore_d"] / 2)

    # 8 x M3 through the end walls, along Y, plus an inner-face
    # counterbore so a button head sits flush and does not hit the pack.
    end_len = wt + 2.0
    front_xz = [(h["x"], h["z"]) for h in end_m3_holes(p) if h["end"] == "front"]
    back_xz = [(h["x"], h["z"]) for h in end_m3_holes(p) if h["end"] == "back"]
    body = _cut_cyls_y(body, front_xz, -1.0, end_len, p["m3_clear"] / 2)
    body = _cut_cyls_y(body, back_xz, ye - wt - 1.0, end_len, p["m3_clear"] / 2)
    cb_h = p["m3_cbore_h"] + 0.2
    cb_r = p["m3_cbore_d"] / 2.0
    # Front: inner face at y = wt, counterbore cuts into the wall (-Y).
    front_cb = [_cyl(cb_r, cb_h, (x, wt + 0.2, z), (0, -1, 0)).val() for x, z in front_xz]
    # Back: inner face at y = ye - wt, counterbore cuts into the wall (+Y).
    back_cb = [_cyl(cb_r, cb_h, (x, ye - wt - 0.2, z), (0, 1, 0)).val() for x, z in back_xz]
    body = body.cut(cq.Compound.makeCompound(front_cb + back_cb))
    return body


def build_all(p=P):
    pl = plate(p)
    sp = spool_r8(p)
    return dict(
        plate=pl,
        spool_r8=sp,
        p=p,
        stations=stations(p),
        patterns=patterns(p),
        y_end=y_end(p),
        pack_len=p["pack_len"],
    )


def _export(name, wp, dest_step, dest_stl):
    cq.exporters.export(wp, dest_step)
    cq.exporters.export(wp, dest_stl)
    bb = wp.val().BoundingBox()
    solids = wp.solids().vals() if hasattr(wp, "solids") else [wp.val()]
    n = len(solids)
    print(f"{name:28s}  {bb.xlen:7.1f} x {bb.ylen:7.1f} x {bb.zlen:6.1f} mm   "
          f"vol {wp.val().Volume():.0f} mm3  solids={n}")
    return bb


if __name__ == "__main__":
    out_step = STEP_DIR if os.path.isdir(STEP_DIR) else HERE
    out_stl = STL_DIR if os.path.isdir(STL_DIR) else HERE
    print("v18 stations (front -> back), pack_gap =", P["pack_gap"],
          "pitch =", P["pitch"], "pack_len =", P["pack_len"])
    for s in stations():
        print(f"  {s['i']}: {s['finger']:6s} {s['ab']}  face={s['face']:6s}  "
              f"side={s['side']:5s}  shaft=({s['xf']:+.2f}, {s['y']:.2f}, {s['zf']:+.1f})")
    print(f"y_end = {y_end():.2f} mm  (one flat plate, {2*P['half_w']:.0f} mm wide, "
          f"web M3={len(attach_m3_holes())}, end M3={len(end_m3_holes())}, "
          f"M2={len(m2_hole_xy())}, arc R={P['arc_r']})")
    parts = build_all()
    _export("forearm_plate", parts["plate"],
            os.path.join(out_step, "forearm_plate.step"),
            os.path.join(out_stl, "forearm_plate.stl"))
    pat = parts["patterns"]
    print("\n--- mounting patterns ---")
    for k, v in pat.items():
        print(f"  {k}: {v.get('name_fr','')}")
        if "holes" in v:
            print(f"      {len(v['holes'])} items")
            if k == "end_m3":
                for h in v["holes"]:
                    print(f"        {h['end']:5s}  ({h['x']:+.2f}, z={h['z']:+.1f})")
            if k == "attach_m3":
                for h in v["holes"]:
                    print(f"        i={h['i']}  ({h['x']:+.2f}, {h['y']:.2f})")
