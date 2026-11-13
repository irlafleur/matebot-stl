# MateBot v13 (UNTESTED): one minimal FLAT plate holding a single row of
# 8 x Feetech STS3215 (12 V). Bodies sit face-to-face (0.4 mm nominal gap,
# no glue). v12 is superseded.
#
# Layout: the same packed row as v12. Long axis ACROSS the forearm, output
# shaft perpendicular to the plate. Faces follow TL, TR, BL, BR, repeat
# (wrist / front -> elbow / back):
#   0-1 thumb  = top (dorsal),  shafts L then R
#   2-3 index  = bottom (palmar), shafts L then R
#   4-5 middle = top,            shafts L then R
#   6-7 ring   = bottom,         shafts L then R
# Each finger pair is two adjacent servos on the SAME face.
#
# The plate is a 4 mm flat rectangle, barely longer than the 8 packed
# bodies (8 x 24.72 + 7 x 0.4 = 200.56 mm) plus a low wall at each end.
# Closed at the back with a low stop. At the front, a low wall with two
# cable holes only (bus leads can be dressed toward the wrist). No U
# flanges, no second plate, no socket bosses, no wrist flange, no M3
# grids. M2x6 through the plate into the idler ears of the four servos
# whose idlers face it (index, ring). The four servos whose spools face
# the plate (thumb, middle) get a Ø28 cut-out so the spool can pass
# through; this plate cannot reach their idler ears (35 mm away on the
# far side). They are located by the packed neighbours and the back
# wall only. If those four later need a clamped mount, the simplest fix
# is a second identical flat plate on the other face (still no U
# flanges). Do not use the output-side ears (different hole pattern).
#
# Official 24.72 mm width already includes the ears (Waveshare 2D and
# STEP). 0.4 mm is the project's print allowance (CL).
#
# Frame F (local to this plate): origin at the front-centre of the plate,
# on the inner face (the face the servos sit against). +X ulnar, +Y
# toward the back / elbow, +Z outward through the plate (servo bodies
# hang in -Z). M2 access is from the outside (+Z).
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
    web_t=4.0,              # M2x6: 4 mm plate + 2 mm into the 2.8 mm idler ear
    wall_t=3.5,             # front and back wall thickness
    wall_h=16.0,            # low end walls, into the body side
    pack_gap=0.4,           # nominal body-to-body gap (0-0.5 mm, no glue)
    half_w=28.0,            # plate half-width: Ø28 cut-out at x=±12.50 needs |x|>=26.5
    spool_r=8.0, spool_flange=3.0, spool_base_t=2.0, groove_w=3.0, mid_flange=1.5,
    spool_top_t=2.0,
    spool_cut_d=28.0,       # spool flange is Ø22; 3 mm radial clearance
    idler_cut_d=22.0,       # clearance for the idler horn (protrudes 2.25 mm)
    m2_clear=2.4,
    cable_hole_d=10.0,
    cable_hole_x=16.0,      # two holes in the front wall, left and right
    cable_hole_z=-8.0,      # idler-side bus stub sits ~8 mm below the inner face
)
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
    """Front-to-back list of 8 stations with positions in frame F."""
    y0 = p["wall_t"] + BODY_W / 2.0
    out = []
    for meta in STATION_META:
        i = meta["i"]
        y = y0 + i * p["pitch"]
        xf = -SHAFT_X if meta["side"] == "left" else SHAFT_X
        # Top-face: output horn (spool) on the plate, zf = 0.
        # Bottom-face: idler on the plate, output at zf = -H_TO_HORN.
        zf = 0.0 if meta["face"] == "top" else -H_TO_HORN
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
    return (-H_TO_HORN - d1, -H_TO_HORN - d2)


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
# Unchanged from v9/v10/v11/v12 spool_r8.
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


def patterns(p=P):
    """Minimal catalogue: M2 idler screws of the four plate-facing servos,
    spool and idler cut-outs, two front cable holes. No M3 grids, no wrist."""
    sts = stations(p)
    m2 = []
    for s in sts:
        if s["face"] != "bottom":
            continue
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            m2.append(dict(i=s["i"], finger=s["finger"], ab=s["ab"],
                           face=s["face"], x=round(x, 3), y=round(y, 3), z=round(z, 3),
                           access="outside / +Z", screw="M2x6"))
    spool_cuts = [(s["xf"], s["y"]) for s in sts if s["face"] == "top"]
    idler_cuts = [(s["xf"], s["y"]) for s in sts if s["face"] == "bottom"]
    cables = [(-p["cable_hole_x"], p["cable_hole_z"]),
              (p["cable_hole_x"], p["cable_hole_z"])]
    return dict(
        servo_idler_m2=dict(
            name_fr="Fixation des servos — oreilles côté poulie folle (index, annulaire)",
            screw="M2x6, passage Ø2.4, 16 vis (4 servos)",
            holes=m2,
            note=("4 trous par servo dont les oreilles du fouet sont contre la "
                  "plaque (index et annulaire). Accès depuis l'extérieur (+Z). "
                  "4 mm de plaque + 2 mm dans l'oreille (2,8 mm). "
                  "Ne pas utiliser de M2×8. Pouce et majeur : pas de vis M2 "
                  "sur cette plaque (bobine en travers, Ø28)."),
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


def plate(p=P):
    """One flat 4 mm plate, low back stop, low front wall with two cable holes."""
    sts = stations(p)
    ye = y_end(p)
    w = p["half_w"]
    t, h, wt = p["web_t"], p["wall_h"], p["wall_t"]
    web = _box(-w, w, 0.0, ye, 0.0, t)
    front = _box(-w, w, 0.0, wt, -h, 0.0)
    back = _box(-w, w, ye - wt, ye, -h, 0.0)
    body = fuse_fuzzy([web, front, back])

    spool_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "top"]
    idler_pts = [(s["xf"], s["y"]) for s in sts if s["face"] == "bottom"]
    # Through the web (and a little past) so the spool / idler horn is free.
    body = _cut_cyls_z(body, spool_pts, -1.0, t + 2.0, p["spool_cut_d"] / 2)
    body = _cut_cyls_z(body, idler_pts, -1.0, t + 2.0, p["idler_cut_d"] / 2)

    m2_pts = []
    for s in sts:
        if s["face"] != "bottom":
            continue
        for x, y, z in idler_holes_F(s["xf"], s["y"], s["zf"], s["face"], s["side"]):
            m2_pts.append((x, y))
    body = _cut_cyls_z(body, m2_pts, -1.0, t + 2.0, p["m2_clear"] / 2)

    # Two cable holes through the front wall, along Y.
    body = _cut_cyls_y(body, [(-p["cable_hole_x"], p["cable_hole_z"]),
                              (p["cable_hole_x"], p["cable_hole_z"])],
                       -1.0, wt + 2.0, p["cable_hole_d"] / 2)
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
    print("v13 stations (front -> back), pack_gap =", P["pack_gap"],
          "pitch =", P["pitch"], "pack_len =", P["pack_len"])
    for s in stations():
        print(f"  {s['i']}: {s['finger']:6s} {s['ab']}  face={s['face']:6s}  "
              f"side={s['side']:5s}  shaft=({s['xf']:+.2f}, {s['y']:.2f}, {s['zf']:+.1f})")
    print(f"y_end = {y_end():.2f} mm  (one flat plate, front+back walls {P['wall_t']} mm)")
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
