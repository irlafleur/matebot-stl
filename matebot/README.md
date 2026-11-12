# MateBot parts (tendon-driven hand)

MateBot moves the Amazing Hand's 8 servos out of the palm and into the forearm. Each finger is driven by a pair of Feetech STS3215 (12 V) servos pulling tendons through PTFE tubes.

**Status: v0/v1, untested.** Nothing here has been validated on a real build. Measure your own servo and servo horn before printing.

## Folders

- `stl/`: ready-to-print files
- `step/`: editable CAD files
- `source/`: Python (CadQuery) scripts that generate the parts: `parts.py` (spool, PTFE anchor, servo bay) `finger_link_tendon.py` (the modified finger Link), `bushing_d6.py` (the printable finger bushing, with `verify_bushing_d6.py` and `render_bushing_d6.py`) and `R-Hand_Plate_tendon.py` (the modified hand plate and palm shell, now with the Gimbal pivot blocks), `Gimbal_tendon.py` (the Gimbal with a retention tab), with `verify_R-Hand_Plate_tendon.py`, `render_plate_tendon.py` and `render_gimbal_thumb.py`, `render_assembly_fr.py` (the French assembly drawings)
- `docs/`: design notes, assembly guide (French), preview images (`finger_link_tendon_preview.png`, `finger_link_tendon_routing.png`, `R-Hand_Plate_tendon_preview.png`, `R-Hand_Plate_tendon_routing.png`, `Gimbal_tendon_preview.png`, `thumb_aperture_preview.png`, `assemblage_doigt_eclate_FR.png`, `assemblage_coupes_vis_FR.png`, `bushing_d6_preview.png`) and an explainer animation

## Parts to print

| File | Quantity | Notes |
|---|---|---|
| `spool_r8.stl` | 8 (+2 spare) | One per servo. Two grooves: flexor and extensor. 100% infill or 6 walls. |
| `ptfe_anchor_8x.stl` | 2 (servo side only) | Holds the 16 PTFE tube ends in the forearm. The palm ends now sit in `R-Hand_Plate_tendon`. |
| `servo_bay_8x_sts3215.stl` | 1 | **Bench testing only.** It does not fit inside the forearm; it will be replaced by 4 pair mounts. |
| `finger_link_tendon.stl` | 4 (+2 spares) | **Replaces Pollen's `Link`** (do not also print the original Link). Same pivot holes, plus a cross bar and two tendon plates, now with **dowel pass-through holes** (v1). Print 1 first. Needs supports. |
| `Gimbal_tendon.stl` | 3 (+1 spare) | **Replaces Pollen's `Gimbal` on the index, middle and ring fingers** (do not also print the original Gimbal for those 3). Identical, plus a rear tab with an arc slot so the Gimbal can be **screwed from underneath the plate** (see [the Gimbal section](#the-gimbal-screwed-from-underneath-gimbal_tendon-v0-untested)). |
| `bushing_d6_flanged.stl` | 8 (+2 spares) | **Printable version of Pollen's "Bushing D interior 6 mm"** (GFM-0608-04): 2 per finger, pressed into the pivot bores of `R-Hand_Plate_tendon`. Small part: print all 10 at once. See [the bushing section](#the-finger-bushing-bushing_d6_flanged-v0-untested). |
| `R-Hand_Plate_tendon.stl` | 1 | **Replaces Pollen's `R-Hand_Plate` and, for the 3 fingers, Finger_Frame-1 and Finger_Frame-2.** Same outline and screw holes, plus a Gimbal pivot block with the D8.15 bore under each finger window, a Gimbal retention post, and 12 PTFE tube sockets. Needs no support (same as the original). |
| `R-Palm_Shell_tendon.stl` | 1 | **Replaces Pollen's `R-Palm_Shell`.** Same shell with notches where the new sockets, posts and screw heads reach it, and a **bigger thumb aperture**. Print in the same material as the original. |

**No longer printed for the index, middle and ring fingers: `Finger_Frame-1` and `Finger_Frame-2`.** Frame-1's function (the D8.15 Gimbal bore with its bushings) is now part of `R-Hand_Plate_tendon`; Frame-2 only carried the servos of the original hand and has no job in the tendon hand. **The thumb is the exception:** it is not on the plate but on the Wrist_Interface, so it still needs **1 printed `Finger_Frame-1`** (Pollen's file, unchanged) and **1 stock `Gimbal`**, plus its own 2 bushings (already in the 10). Print the thumb's Proximal, Distal, shells and `finger_link_tendon` as for the other fingers (4 each).

## The finger bushing: `bushing_d6_flanged` (v0, untested)

**What Pollen calls it.** In the Amazing Hand bill of materials and assembly guide (Step 2, "Bushings") it is **"Bushing D interior 6 mm / D exterior 8 mm", part number GFM-0608-04**: an igus iglidur GFM flanged plastic bush, 6 mm bore, 8 mm OD, 4 mm long including the flange, flange D12 × 1 mm. It is a *bought* part, 2 per finger (8 per hand with the thumb), so it was never in the STL set. It is the only bushing in the hand: the D2×10 and D2×16 axes turn directly in the printed holes of the Gimbal, Proximal, Distal and Link, and the BallJoint_Rod Spacers (not needed with tendons) are not bushings.

**Where it goes.** The finger's abduction / adduction pivot. The Gimbal has a D6.0 boss (Z 3.5 to 13.5 in the finger frame); the plate's pivot block (`R-Hand_Plate_tendon`, which replaces Finger_Frame-1) has the same D8.15 through bore (8.0 mm long, Z 4.5 to 12.5). One bushing is pushed in from each side, flange outside, until the flange touches the frame. The boss sticks out of the frame by exactly 1.0 mm on each side, which is the flange thickness, so the M2.5 large washer and the 2.5×8 screw end up resting on the outer flange.

| | Printed `bushing_d6_flanged` | Pollen / igus GFM-0608-04 |
|---|---|---|
| Bore | **D6.20** (the Gimbal boss is D6.0) | D6.0 (+0.02 to +0.07) |
| Body OD | **D8.10** (frame bore D8.15 in the CAD) | D8.0 |
| Flange | D12.0 × 1.0 | D12 × 1 |
| Total length | 4.0 (body 3.0 under the flange) | 4.0 |
| Wall | 0.95 mm (body), 1.0 mm (flange) | |
| Chamfers | 0.25 on the outer body tip (lead-in), 0.2 on the bore both ends | 0.5 |
| Quantity | **8 (+2 spares = 10)** | 8 |

- **Print:** upright (flange on the bed, body up, no support), PETG, 0.12 mm layers, 3 or more walls (the 0.95 mm wall is all perimeters), 100% infill, about 40 mm/s. Put all 10 on one plate with 3 mm spacing.
- **Fit:** the printed plate bore usually comes out slightly under the drawn D8.15, so the body is a light press fit. Push the bushing in against a flat surface. If it will not go, sand the body; if it is loose, a drop of CA glue on the body. Pass a D6.2 drill or reamer by hand through the bore if the Gimbal boss does not turn freely (D6.3 if it is still tight). One drop of PTFE or silicone grease on the boss; PETG running on PETG can squeak.
- **Measure before printing all 10:** the real bore of your printed plate and the real boss of your printed Gimbal (caliper). Print 2 test bushings first. To re-size, edit `od` and `bore` in `source/bushing_d6.py` and run it.
- **Verified in CAD** (`source/verify_bushing_d6.py`, 12 of 12 pass): the pair fits the stock Frame-1 bore (identical to the plate bore) and the Gimbal boss with no interference, with the Gimbal turned ±30°; no contact with Finger_Frame-2, Proximal, shells, Distal, the hand plate, `finger_link_tendon`, `R-Hand_Plate_tendon` or `R-Palm_Shell_tendon` (they sit at |X| ≥ 12 mm, far from the D12 flanges), and none while Proximal, shells, Distal and Link are swept through −80° to 0° of flexion. The flange only touches the Proximal if the finger is pushed more than +5° past straight; the frame itself stops the Proximal at +7°.
- **Not verified:** real printed tolerances, wear and friction of PETG on PETG, and the thumb (its Finger_Frame-1 is the original Pollen file; the bushings were checked on the fingers' bore, which is the same D8.15). v1 adds: the pair fits the new plate bore of all 3 fingers, and the upper flange sits in the slab notch (0 mm³ interference, `verify_R-Hand_Plate_tendon.py`).
- Original part, if you ever prefer to buy it: igus iglidur GFM-0608-04 (Pollen's BOM lists 8 per hand at about 1.60 EUR each). Nothing was bought.

## The palm plate: `R-Hand_Plate_tendon` (v1, untested)

Pollen's plate holds 3 fingers (index, middle, ring) in 3 windows. The **thumb is not on this plate**: it screws into the Wrist_Interface. So the plate takes 3 fingers × 4 tendons = **12 tube ends** (not 8). The thumb's 4 tube ends still need a home on the wrist adapter (not designed yet).

**v1 changes (all three fingers):**

1. **Finger_Frame-1 and Finger_Frame-2 are no longer printed.** Under each finger window the plate now has a **Gimbal pivot block**: the exact outline of Frame-1's bottom face (X ±10, Y −15 to +6) from the slab underside down to Z = 4.5, i.e. the 8 mm long block of Frame-1, with the same **Ø8.15 through bore** (0.3 mm lead-in chamfer on both ends) for the 2 bushings and the Gimbal boss. The Gimbal therefore mounts directly on the plate. The original M2 screw holes stay; Frame-2 only carried the servos and is not needed.
2. **The Gimbal is screwed from underneath** (see [the Gimbal section](#the-gimbal-screwed-from-underneath-gimbal_tendon-v0-untested)): a **Ø4.4 post** hangs under each block at X = 0, Y = −8.6 (finger frame), down to Z = 0.1, with a **Ø1.9 pilot hole 8 mm deep** opening at its bottom face.
3. **Anchor columns 1.5 mm shorter, sockets 1.5 mm closer.**
4. The palm shell (`R-Palm_Shell_tendon`) has a bigger thumb aperture.

Each finger side gets one **anchor column** that hangs under the plate and holds two sockets, the extensor above the flexor (6 columns, 12 sockets):

| Item | Value (finger frame: X sideways, Y along the finger, Z toward the back of the hand) |
|---|---|
| Tube socket | Ø4.2 mm bore, 8.0 mm deep, for 4 mm OD PTFE tube |
| Stop shoulder | 1.6 mm thick, Ø2.2 mm through-hole for the tendon |
| Tendon exit | cone from Ø2.2 to Ø5.0 mm over 3.0 mm, facing the finger (lets the tendon swing without rubbing) |
| Tube end (stop face) | Y = −30.0 mm, i.e. 30 mm behind the finger pivot |
| Socket axes | X = ±10.5 mm, extensor at Z = +2.3 mm, **flexor at Z = −12.8 mm (v0: −14.3)**: the two sockets are **15.1 mm apart (v0 16.6)**. The tendons leave the 9.0 mm capstan tangents at Z = +3.0 and −15.0, so the extensor leans 0.7 mm and the **flexor 2.2 mm** over the 25 mm to the socket (Link pivot at Z = −6); the tendon corridors (Ø3.0) are re-aimed at the real tangent points |
| Column | 8.2 mm wide, 12.6 mm long (Y −38.0 to −25.4), from the slab top (Z = 15.5) down to **Z = −16.9 mm: 32.4 mm tall (v0: 33.9)** |
| Wall around every socket | 2.0 mm (bore, also under the flexor bore), 1.6 mm (cone mouth) |

The 1.5 mm came entirely out of the flexor side (flexor moved up, extensor and column top unchanged): moving both sockets 0.75 mm each would have left only 1.25 mm of wall under the flexor bore, below the 1.6 mm minimum.

The sockets sit at X = ±10.5, not at the capstan lines X = ±13.2: this keeps the sockets of neighbouring fingers at least 7.9 mm apart (the fingers fan out by 5.8° and 13.5°), and the tendon leans about 6° inward between the socket and the capstan.

Other changes to the original plate: a Ø4.5 mm clearance hole behind each extensor socket where the tube crosses the plate's cross beam (the flexor tubes pass under the plate), a Ø3 mm tendon corridor, and a cylindrical relief (R10.3) around each Link capstan plate, **v1: 2.6 mm wider on the outer side of each plate** so the Link plates can abduct ±25° without touching the plate rails (the ring finger's plate touched by 1.5 mm³ at +25°). All original screw holes are kept.

**Palm shell (`R-Palm_Shell_tendon`).** Notches where the columns (grown by 0.6 mm), the Gimbal post, washer and screw head reach the shell, and a **bigger thumb aperture**: the shell loses about 1030 mm³ in total (v0: 764 mm³), most of it the thumb aperture. The aperture is the envelope of the thumb's parts swept through the full range (abduction ±25°, flexion −80° to +5°) plus **1.5 mm of clearance all round**: the tendon Link's capstan plates (the part that collided with the stock hole) and the Proximal / Proximal_Shell at the wrist end of the aperture (the stock shell edge is only 0.9 mm from the Proximal_Shell at +25° abduction). See `docs/thumb_aperture_preview.png`. **The thumb's position and angle are ESTIMATED**: they come from the 3-hole screw pattern of the Wrist_Interface (the hand's thumb mount), not from Pollen's assembly file.

What was **checked in CAD** (script `source/verify_R-Hand_Plate_tendon.py`, 34 checks, see the numbers in the output): single valid solid; finger positions fitted to the plate's own screw holes (worst error 0.19 mm); no original hole plugged; wall ≥ 1.6 mm around all 12 sockets; Ø8.15 bores coaxial with the finger axes; the 2 bushings fit each bore and the slab notch; stock Gimbal and `Gimbal_tendon` turning ±25° clear the plate; post wall around the pilot ≥ 1.2 mm; washer, screw head and a Ø7 screwdriver column clear the plate and columns; the post slides in the `Gimbal_tendon` slot over ±25°; Proximal, shells, Distal, tendon Link and `Gimbal_tendon` swept over flexion × abduction clear the plate, washer and head; column 32.4 mm and socket spacing 15.1 mm; tendon lines clear the Gimbal parts; relieved shell clear of all added material; thumb parts keep ≥ 1.5 mm from the new shell.

What is **not** verified: nothing has been printed. The thumb pose is estimated (see above). The extension stop: the Proximal touches the block at +5° to +7° past straight, exactly like the stock Frame-1 (the check range stops at +5°). The tendon lines were checked at rest and at ±25° abduction against the Gimbal parts, not over the full flexion range. The thin walls left beside the extensor clearance holes where they cut through the original pockets can be as thin as 0.2 mm (they will not print, the hole simply opens into the pocket). The tubes were only checked straight from the sockets back to Y = −85 mm; they will overlap the Wrist_Interface walls a little, which is to be solved with the wrist adapter.

Printing: PETG, plate slab-down exactly like the original. No supports are needed: the columns, the pivot blocks and the posts all grow straight up from the slab, and the bores and pilot holes are vertical in that orientation (they print round). 0.2 mm layers, 5+ walls and 40% or more infill. The tube bores are horizontal; they bridge over 4.2 mm, so check them with the tube before gluing and ream with a Ø4.2 drill if tight. Glue the tubes in with a drop of CA glue.

Check with calipers: the PTFE tube OD (the sockets assume 4.0 mm: if yours is 4.1 or more, change `sock_d`), the printed Ø8.15 bores (they must accept the bushings, see above), and that the tubes seat fully (8 mm).

## The Gimbal screwed from underneath: `Gimbal_tendon` (v0, untested)

**The problem.** Pollen keeps the Gimbal in with one 2.5×8 screw and a large M2.5 washer on top of its boss (blind Ø1.9 hole, Z 5.5 to 13.5). With the Frame gone and the palm shell on top, the fingers were not held. The request was to screw the Gimbal in from underneath.

**Why not a screw in the boss axis from below.** The boss axis is also the abduction axis. Below the boss the Gimbal is solid at Z = 0 and the D2×16 Gimbal ↔ Proximal pin crosses that axis, so no screw can enter the boss from below on its axis. A retainer bar under the shoulder would be hit by the Proximal's ears (they sweep radius 5.2 to 8.75 mm around the pivot during abduction), and a clip in a groove of the boss is only 1.0 mm tall. So the screw does not hold the boss; it holds a **tab behind it**.

**What it is.** `Gimbal_tendon.stl` is Pollen's Gimbal plus a **rear tab** (Z 0.5 to 3.5, at radius 8.6 from the boss axis, 8.0 mm wide) with a **Ø5.0 arc slot (±25°)**. The plate's **post (Ø4.4)** stands in the slot. A **large M2.5 washer (Ø8 × 0.8) and a 2.5×8 thermoplastic screw (the one Pollen lists for the top of the boss)** are screwed **from below into the post's Ø1.9 pilot hole**. The washer overlaps the tab by 1.5 mm each side of the slot, so the Gimbal cannot drop or pull out; the post can slide in the slot, so the Gimbal still turns ±25° (abduction). It does not clamp: the washer sits 0.4 mm below the tab and the tab has 1.0 mm of room under the block.

| | |
|---|---|
| Screw | **2.5 × 8 mm thermoplastic screw (the same as Pollen's top screw, 1 per finger: no new hardware)**, into a Ø1.9 pilot hole, **7.2 mm of thread in the post** (8.0 mm screw minus the 0.8 mm washer) |
| Washer | the large M2.5 washer Pollen already lists (Ø8) |
| Counterbore | none needed: the head (about Ø4.5 × 1.8) sits free below the post, and the palm shell is notched around it |
| Access | Ø7 mm straight down from the post, not blocked by the plate, anchor columns or reliefs; **the palm shell is fitted after the fingers** (as in Pollen's order), so install the screw before fitting the shell |
| Original top hole | the Gimbal's top blind hole and the boss end are untouched; the top screw is not needed any more (optional) |

**Install (per finger):**
1. Press one bushing into the **lower** end of the bore (flange down) of the plate's pivot block.
2. Offer the `Gimbal_tendon` from below: boss up through that bushing, the post passing through the arc slot of the tab.
3. Press the second bushing into the upper end of the bore from above (flange in the slab notch).
4. From below: washer, then the 2.5×8 screw into the post, tighten until the head sits on the post bottom face (then the washer is held 0.4 mm from the tab). Check that the Gimbal turns by hand ±25°.
5. Fit the Proximal, Distal and `finger_link_tendon` as before. **Dowel pins D2×10 / D2×16** as in the previous version.

**Verified in CAD** (`verify_R-Hand_Plate_tendon.py`): `Gimbal_tendon` is one valid solid (volume 1029 mm³ vs 902 for the stock Gimbal); the post (+0.2 mm margin) passes the slot over ±25°; washer and head clear all moving finger parts (Proximal, shells, Distal, tendon Link, tab) over flexion × abduction; wall ≥ 1.5 mm around the slot. **Not verified:** the real force the 2.5×8 screw holds in a printed Ø1.9 pilot (the post wall is 1.25 mm), or the real abduction range (if your fingers abduct more than ±25°, enlarge `abd` in `source/Gimbal_tendon.py` and `source/R-Hand_Plate_tendon.py`).

Printing: like the original Gimbal (boss up, fork on the bed) with **tree supports under the new tab** (3 mm thick, it overhangs the shoulder by about 6 mm); print 1 first and check that the post slides in the slot with a little play (ream the slot with a Ø5 drill if tight). PETG, 4+ walls, 100% infill on the tab.

See the drawings `docs/assemblage_doigt_eclate_FR.png` (exploded view, French) and `docs/assemblage_coupes_vis_FR.png` (sections of the screw paths).

Run `python source/Gimbal_tendon.py "<Amazing Hand Parts - Gimbal.step>"` to regenerate it. Preview: `docs/Gimbal_tendon_preview.png`.

## Gimbal retention: alternatives checked (v7 review)

### Option without any reprint: stock Gimbal + Pollen's top screw (checked)
The stock Gimbal has one end hole, and it is on the **top** of the boss (the back of the hand side, Z = 13.5), not at the bottom: **Ø1.9 mm, about 8.5 mm deep from the top (Ø1.9 from Z 12.9 to 5.5, then a drill-point cone to about Z 4.9), with a Ø2.8 countersink 0.6 mm deep, blind** (measured in the STEP file). Pollen's 2.5×8 screw and large washer go in there from above. This works with the v6 plate unchanged: the washer (Ø8) and head sit in the slab notch with 0 mm³ overlap with the plate and the palm shell. The cost: **R-Top_Shell covers the screw** (70 mm³ of overlap with a Ø7 access column), so it has to come off to tighten it. If you can live with that, **no `Gimbal_tendon` is needed**; the stock Gimbals you already printed (6 in zip v5) work. `Gimbal_tendon` also keeps this hole, so it can use the top screw too.

### Why a screw "through the lower bushing, along the Gimbal axis" does not work (checked in CAD)
`source/render_assembly_fr.py` (panel C of `docs/assemblage_coupes_vis_FR.png`). Along the boss axis the stock Gimbal is solid only from Z 1.1 to 4.9 (above the pin bore) and from Z −2.3 to −1.05; between them the **D2×16 Gimbal-Proximal pin crosses the axis** (Ø2.2 bore, pin Ø2.0 over X ±8.1): a Ø2.0 or Ø2.5 shank would cut it over 5.3 or 7.2 mm³. The existing hole is blind (floor at Z ≈ 4.9, 3.9 mm of material and the pin bore below it), so the screw would first have to be drilled through, and from the bottom the Gimbal body (Z ≤ −2.3) lies inside the fork where the Link turns: a screw head of Ø4.5 or a washer of Ø8 just below it collides with the Link by 11 to 32 mm³ at every flexion angle. Also, the lower bushing sits around the boss (Z 3.5 to 4.5): the screw would never pass through it, and a fixed bushing cannot hold the Gimbal from dropping (the Gimbal falls toward −Z and only something above the boss, or a part of the Gimbal caught by a fixed part, stops it). That is why the retention is either on top (stock) or by the tab and post (`Gimbal_tendon`).

## The finger part: `finger_link_tendon` (v1, untested)

In Pollen's Amazing Hand, the two ball-joint rods are screwed onto the ends of the cross bar of the **Link**, not onto the Proximal or Distal. The Link is the input crank of the finger: it drives the Proximal and the Distal through the 4-bar linkage. So the Link is the only finger part that has to change. **Proximal, Distal, Gimbal and the shells are printed unchanged.**

`finger_link_tendon` keeps the original Link (all pivot holes untouched) and adds:
- a Ø6 cross bar (same place and size as the original barrel, now 24 mm long);
- two identical plates at the ends of the bar, **X = ±12.0 to ±14.4 mm** from the finger axis (just outside the 11.9 mm half-width of the Proximal_Shell);
- on each plate: a U groove (1.4 mm wide) around the rim (rim radius 9.7 mm), centred **9.0 mm** from the Link pivot, so the tendon wraps the plate like a capstan with a constant lever arm of about 9.0 mm (the 8 mm spool turns about 12% more than the Link);
- **v1: dowel pass-through** in both plates. The plates sit right on the axes of two assembly pins, so they blocked them: the **D2×10 pin** (Gimbal ↔ Link, axis = the Link pivot, Y = 0, Z = −6) and the **D2×16 pin** (Gimbal ↔ Proximal, axis Y = 0, Z = 0, 16.2 mm long, ears at X = ±8.1). Each plate now has a **Ø2.5 round hole at the pivot** and a **Ø2.5 arc slot** 6 mm above it (80° to 120° around the pivot). The slot is an arc, not a round hole, because the Link turns on its pivot: the round hole would only line up with the pin axis at one exact Link angle; the slot lets you tilt the Link by +10° (extension) to −30° (flexed) while you push the D2×16 pin through. The pins only pass through these holes while you assemble; once in place they stop at X = ±8.1 and the holes are free;
- the lower back wedge of each plate now starts 4.2 mm from the pivot (was at the pivot) so the pivot hole keeps a closed wall;
- two knot/crimp pockets per plate (Ø3.2 × 2.0 mm, open on the outer face) with a Ø1.2 mm channel that leaves the groove on a 3 mm radius bend. The **lower pocket is the flexor** (palm side, −Z), the **upper pocket is the extensor** (back, +Z).

**Which tendon goes where.** Each servo has one loop with a flexor and an extensor. The two legs of a loop go to **opposite plates**: servo A's flexor to the +X plate and its extensor to the −X plate; servo B's flexor to the −X plate and its extensor to the +X plate. Crossing is required: if both legs of a loop went to the same plate, the finger could not abduct, because side motion shortens both legs of that plate by the same amount and a closed loop cannot absorb that. With the crossed layout, A and B turning the same way flex the finger and opposite ways abduct, as in Pollen's code (the sign of abduction depends on which servo you call A).

Design numbers (CAD estimates from the original STL files, not measurements on a print):
- Link rotation for full flexion: about 70°; the Proximal turns about 65° and the Distal about 128°.
- Tendon stroke per leg: about 11 mm for 70° of flexion (9.0 mm lever arm), plus or minus about 4.5 mm for ±20° of abduction. Total up to about 15.5 mm, which is about 111° of rotation of the 8 mm spool. A quick 2D model gives a flexor + extensor length mismatch of at most 0.13 mm from +10° to −70° of Link rotation (tube ends 25 mm behind the pivot): the loop stays closed.
- Clearance over the flexion range (−80° to +15°) between the new material and the Gimbal, Proximal, Proximal_Shell and Finger_Frame-1: at least 0.38 mm to the Gimbal, 0.86 mm to the shell, 2.1 mm to the Proximal (sampled check of the v0 geometry against the original STL files, one finger only; **not repeated for v1**: the only v1 changes are on the plates, at X ≥ 12 mm, which is outside every one of those parts, plus a larger rim radius 9.0 → 9.7 mm).
- v1 dowel checks (`source/verify_finger_link_tendon.py`, 5 of 5 pass): single valid solid; the Link body and bar are untouched by the new holes; at least 1.2 mm of solid wall (so no groove, pocket or channel) around the round hole and around the slot; the D2×10 and D2×16 pins (modelled as Ø2.0 cylinders) pass through both plates along their **whole insertion length** (from 10 or 16 mm outside the ear to the far ear), from either side, with the Link at 0°, +10°, −30° and −60° (D2×10) or +10° to −30° (D2×16). Control: at +35° the slot no longer lines up and the D2×16 pin is blocked, as expected. The pin path was checked against the Link only, not against the Gimbal, Proximal and Distal.
- The plates reach X = ±14.4 mm. The Hand_Plate windows suggest a finger pitch of about 30 mm, so neighbouring plates would be about 1.2 mm apart. **Not verified on a real palm.**
- Printing: the original Link also needs supports in every orientation. Print `finger_link_tendon` with the plate lying flat (X up) and tree supports under the cross bar and the Link strip, 4+ walls, 100% infill on the plates.
- Strength (hand estimate, not FEA): the cross bar and plates should hold roughly 50 to 80 N of tendon tension in PETG. The STS3215 can pull much more. **Start with the servo torque limit at 10% (about 35 N at the 8 mm spool)** and raise it only after testing.

## Known issues

- The spool's horn screw pattern is not yet matched to the real Feetech horn.
- The servo pocket clearance is tight (about 0.2 mm per side).
- The 4 servo-pair mounts and the wrist adapter (with the thumb's 4 tube ends) have not been designed yet.
- `R-Hand_Plate_tendon` v1 and `Gimbal_tendon` are not printed yet. `Finger_Frame-1` and `-2` are no longer printed for the 3 fingers (the thumb still needs one Frame-1).
- The cross bar fills the original M2 rod hole of the barrel. Nothing else of the original Link is removed.
- The rim radius grew from 9.0 to 9.7 mm in v1, so the tendon lever arm is 9.0 mm instead of 8.3 mm and the plate relief in `R-Hand_Plate_tendon` grew from R9.6 to R10.3. A v0 Link on a v1 plate works; a v1 Link on a v0 plate scrapes the plate walls of the middle and ring fingers.

### How to tie the tendon (v1)

1. Thread the tendon from the groove through the Ø1.2 channel into the pocket on the outer face (the channel leaves the groove 3 mm from the rim edge, on the side facing the fingertip).
2. In the pocket (Ø3.2 × 2.0 mm) tie a **double overhand (stopper) knot**, leave a 10 mm tail, add one drop of CA glue, and pull the tendon back so the knot sits at the bottom of the pocket. A crimp sleeve of about 1 mm works too. The knot must be larger than the 1.2 mm channel.
3. Lay the tendon in the groove and send it back to the tube along the tangent (flexor from the bottom of the plate, extensor from the top). Tension it with the servo at its centre position.
4. **Do not use the dowel hole or slot as the anchor.** They were evaluated for this: the slot is at a 6 mm radius and the round hole at the pivot, so a tendon tied there would have a 6 mm (or 0 mm) lever arm while the other leg of the loop has 9 mm. A 2D model gives a loop length mismatch of 1.7 mm at −30° and 4.7 mm at −70° (the loop would go slack or overtight). The slot also sits right under the tendon's exit tangent, so the tendon would have to turn 90° into it, and a knot in the hole would sit between the plate and the shell (gap 0.1 mm). Keep the pockets for the knots.

## License

[CC BY 4.0](LICENSE.md): free to use, including commercially, with credit.
