# MateBot v15 (UNTESTED): one minimal FLAT plate holding a single row of
# 8 x Feetech STS3215 (12 V). Bodies sit face-to-face (0.4 mm nominal gap,
# no glue). v14 and v13 are superseded.
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
# each end. Closed at the back with a low stop. At the front, a low wall
# with two cable holes only. No U flanges, no second plate, no socket
# bosses, no wrist flange, no side-rail grid, no corner posts, no
# widening (v14's 78 mm plate is rejected).
#
# v15 additions, on top of that v13 plate:
# - 8 x M3 clearance holes in the web, one over each servo body, on the
#   solid side opposite the spool / idler cut-out (the cable end).
#   Screws go from the inside to the outside. A shallow counterbore on
#   the inner face lets an M3 button head sit flush so it does not hit
#   the servo. These 8 holes are the attachment provision (Ian-Remi:
#   "8 trous par plaque c'est bon"); there are no holes in the end
#   walls.
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
#
# Official 24.72 mm width already includes the ears (Waveshare 2D and
# STEP). 0.4 mm is the project's print allowance (CL).
#
# Frame F (local to this plate): origin at the front-centre of the plate,
# on the inner face (the face the servos sit against / the posts grow
# from). +X ulnar, +Y toward the back / elbow, +Z outward through the
# plate (servo bodies hang in -Z). M2 access is from the outside (+Z).
# M3 attachment access is from the inside (z = 0), thread out at z = +4.
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
    envelope, horn_holes_xy,
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
    wall_h=16.0,            # low end walls, into the body side
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
    m3_clear=3.4,           # M3 clearance (inside -> outside)
    m3_cbore_d=6.5,         # inner-face counterbore for an ISO 7380 M3 button head (dk=5.7)
    m3_cbore_h=1.8,         # flush / slightly sub-flush with z=0
    cable_hole_d=10.0,
    cable_hole_x=16.0,      # two holes in the front wall, left and right
    cable_hole_z=-8.0,      # idler-side bus stub sits ~8 mm below the inner face
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
    (flush at z = 0), thread out at z = +web_t."""
    holes = []
    for s in stations(p):
        holes.append(dict(
            i=s["i"], finger=s["finger"], ab=s["ab"], face=s["face"],
            x=round(-s["xf"], 3), y=round(s["y"], 3), z=0.0,
            dir="Z", screw="M3", d=p["m3_clear"],
            access="inside -> outside",
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
    servos, 8 web M3 attachments, spool and idler cut-outs, two front
    cable holes. No end-wall M3, no side-rail grid, no wrist."""
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
    cables = [(-p["cable_hole_x"], p["cable_hole_z"]),
              (p["cable_hole_x"], p["cable_hole_z"])]
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
            screw="M3 passage Ø3.4, tête fraisée/bouton affleurante à l'intérieur, vis de l'intérieur vers l'extérieur",
            holes=attach_m3_holes(p),
            note=("Un trou par servo, sur le côté plein opposé à la découpe "
                  "bobine / fouet (côté câble), à x = −xf = ±12,50 mm, y = axe "
                  "du servo. Lamage Ø6,5 × 1,8 mm sur la face intérieure pour "
                  "une tête bouton ISO 7380 (ou équivalent) affleurante, afin "
                  "de ne pas toucher le servo. La tige ressort à l'extérieur "
                  "(z = +4). Pas de trous dans les murs avant / arrière : ces "
                  "8 trous les remplacent. Les vis doivent être mises en place "
                  "avant les servos (la tête est sous le corps)."),
        ),
        spool_cuts=dict(
            name_fr="Découpes bobine Ø28 (pouce, majeur)",
            holes=spool_cuts,
        ),
        idler_cuts=dict(
            name_fr="Jeu Ø22 pour le palonnier fouet (index, annulaire)",
            holes=idler_cuts,
        ),
        cable_front=dict(
            name_fr="Trous de câbles en façade (2 × Ø10)",
            holes=cables,
            note=("Mur avant bas, deux trous Ø10 à x = ±16 mm, z = −8 mm. "
                  "Les câbles bus des servos sortent sur les côtés (±X) ; "
                  "ces trous laissent ramener la nappe vers l'avant."),
        ),
        spool_m3=dict(
            name_fr="Bobine spool_r8 sur le palonnier",
            screw="4 x M3x6 sur le cercle de 14 mm + vis centrale M3x6",
            note="Inchangé depuis v9. Pas dans cette plaque.",
        ),
    )


def _m2_posts(p, sts):
    """Inside posts around each M2 hole: 3.5 mm target wall, 3.5 mm tall,
    clipped so they stay inside their own servo's body outline (out of
    the 0.4 mm pack gap and out of the neighbour) and out of the
    idler-horn keep-out. Printable, growing down from the web."""
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
        ]
        comp = cq.Compound.makeCompound([c.val() for c in clips])
        groups.append(posts.cut(comp))
    return groups


def plate(p=P):
    """One flat 4 mm plate, low back stop, low front wall with two cable
    holes, clipped M2 posts, countersunk M2, 8 flush M3 in the web."""
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

    # Two cable holes through the front wall, along Y.
    body = _cut_cyls_y(body, [(-p["cable_hole_x"], p["cable_hole_z"]),
                              (p["cable_hole_x"], p["cable_hole_z"])],
                       -1.0, wt + 2.0, p["cable_hole_d"] / 2)

    # 8 x M3 through the web, inside -> outside, plus an inner counterbore
    # so the button head sits flush at z = 0 and does not hit the servo.
    m3_pts = [(h["x"], h["y"]) for h in attach_m3_holes(p)]
    body = _cut_cyls_z(body, m3_pts, -1.0, t + 2.0, p["m3_clear"] / 2)
    body = _cut_cyls_z(body, m3_pts, -0.2, p["m3_cbore_h"] + 0.2, p["m3_cbore_d"] / 2)
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
    print("v15 stations (front -> back), pack_gap =", P["pack_gap"],
          "pitch =", P["pitch"], "pack_len =", P["pack_len"])
    for s in stations():
        print(f"  {s['i']}: {s['finger']:6s} {s['ab']}  face={s['face']:6s}  "
              f"side={s['side']:5s}  shaft=({s['xf']:+.2f}, {s['y']:.2f}, {s['zf']:+.1f})")
    print(f"y_end = {y_end():.2f} mm  (one flat plate, {2*P['half_w']:.0f} mm wide, "
          f"attach M3={len(attach_m3_holes())}, M2={len(m2_hole_xy())})")
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
            if k == "attach_m3":
                for h in v["holes"]:
                    print(f"        {h['i']}: ({h['x']:+.2f}, {h['y']:.2f}) {h['finger']} {h['ab']}")
