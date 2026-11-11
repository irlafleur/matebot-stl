# MateBot parts (tendon-driven hand)

MateBot moves the Amazing Hand's 8 servos out of the palm and into the forearm. Each finger is driven by a pair of Feetech STS3215 (12 V) servos pulling tendons through PTFE tubes.

**Status: v0, untested.** Nothing here has been validated on a real build. Measure your own servo and servo horn before printing.

## Folders

- `stl/`: ready-to-print files
- `step/`: editable CAD files
- `source/`: Python (CadQuery) scripts that generate the parts: `parts.py` (spool, PTFE anchor, servo bay) `finger_link_tendon.py` (the modified finger Link) and `R-Hand_Plate_tendon.py` (the modified hand plate and palm shell), with `verify_R-Hand_Plate_tendon.py` and `render_plate_tendon.py`
- `docs/`: design notes, assembly guide (French), preview images (`finger_link_tendon_preview.png`, `finger_link_tendon_routing.png`, `R-Hand_Plate_tendon_preview.png`, `R-Hand_Plate_tendon_routing.png`) and an explainer animation

## Parts to print

| File | Quantity | Notes |
|---|---|---|
| `spool_r8.stl` | 8 (+2 spare) | One per servo. Two grooves: flexor and extensor. 100% infill or 6 walls. |
| `ptfe_anchor_8x.stl` | 2 (servo side only) | Holds the 16 PTFE tube ends in the forearm. The palm ends now sit in `R-Hand_Plate_tendon`. |
| `servo_bay_8x_sts3215.stl` | 1 | **Bench testing only.** It does not fit inside the forearm; it will be replaced by 4 pair mounts. |
| `finger_link_tendon.stl` | 4 (+2 spares) | **Replaces Pollen's `Link`** (do not also print the original Link). Same pivot holes, plus a cross bar and two tendon plates, now with **dowel pass-through holes** (v1). Print 1 first. Needs supports. |

| `R-Hand_Plate_tendon.stl` | 1 | **Replaces Pollen's `R-Hand_Plate`.** Same outline and screw holes, plus 12 PTFE tube sockets for the index, middle and ring fingers. Needs no support (same as the original). |
| `R-Palm_Shell_tendon.stl` | 1 | **Replaces Pollen's `R-Palm_Shell`.** Same shell with 3 small notches where the new sockets reach it. Print in the same material as the original. |

## The palm plate: `R-Hand_Plate_tendon` (v0, untested)

Pollen's plate holds 3 fingers (index, middle, ring) in 3 windows. The **thumb is not on this plate**: it screws into the Wrist_Interface. So the plate takes 3 fingers × 4 tendons = **12 tube ends** (not 8). The thumb's 4 tube ends still need a home on the wrist adapter (not designed yet).

Each finger side gets one **anchor column** that hangs under the plate and holds two sockets, the extensor above the flexor (6 columns, 12 sockets):

| Item | Value (finger frame: X sideways, Y along the finger, Z toward the back of the hand) |
|---|---|
| Tube socket | Ø4.2 mm bore, 8.0 mm deep, for 4 mm OD PTFE tube |
| Stop shoulder | 1.6 mm thick, Ø2.2 mm through-hole for the tendon |
| Tendon exit | cone from Ø2.2 to Ø5.0 mm over 3.0 mm, facing the finger (lets the tendon swing without rubbing) |
| Tube end (stop face) | Y = −30.0 mm, i.e. 30 mm behind the finger pivot |
| Socket axes | X = ±10.5 mm, extensor at Z = +2.3 mm, flexor at Z = −14.3 mm (the tendons leave the 9.0 mm capstan tangents at Z = +3.0 and −15.0, so they lean 0.7 mm over the 25 mm to the socket; Link pivot at Z = −6) |
| Column | 8.2 mm wide, 12.6 mm long (Y −38.0 to −25.4), from the slab top (Z = 15.5) down to Z = −18.4 mm |
| Wall around every socket | 2.0 mm (bore), 1.6 mm (cone mouth) |

The sockets sit at X = ±10.5, not at the capstan lines X = ±13.2: this keeps the sockets of neighbouring fingers at least 7.9 mm apart (the fingers fan out by 5.8° and 13.5°), and the tendon leans about 6° inward between the socket and the capstan.

Other changes to the original plate: a Ø4.5 mm clearance hole behind each extensor socket where the tube crosses the plate's cross beam (the flexor tubes pass under the plate), a Ø3 mm tendon corridor, and a cylindrical relief (R10.3) around each Link capstan plate (about 730 mm³ removed in total). All original screw holes are kept.

What was **checked in CAD** (script `source/verify_R-Hand_Plate_tendon.py`, 20 checks): single valid solid; finger positions fitted to the plate's own screw holes (worst error 0.19 mm); no original hole plugged; wall ≥ 1.6 mm around all 12 sockets; no tendon line (finger at rest) touches the plate, Finger_Frame-1/-2, Gimbal or Proximal; the swept Link capstan plates clear the plate; the new material clears the Finger_Frame, Gimbal, Proximal, Top_Shell and Wrist_Interface.

What is **not** verified: nothing has been printed. The tendon lines were checked with the finger at rest only (not over the full flexion and abduction range). The thin walls left beside the extensor clearance holes where they cut through the original pockets can be as thin as 0.2 mm (they will not print, the hole simply opens into the pocket). The tubes were only checked straight from the sockets back to Y = −85 mm; they will overlap the Wrist_Interface walls a little, which is to be solved with the wrist adapter.

Printing: PETG, plate slab-down exactly like the original (no supports needed: the columns reach the slab top face), 0.2 mm layers, 5+ walls and 40% or more infill (the columns carry the tube reaction, not the tendon tension). The bores are horizontal; they bridge over 4.2 mm, so check them with the tube before gluing and ream with a Ø4.2 drill if tight. Glue the tubes in with a drop of CA glue.

Check with calipers: the PTFE tube OD (the sockets assume 4.0 mm: if yours is 4.1 or more, change `sock_d`), and that the tubes seat fully (8 mm).

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
- `R-Hand_Plate_tendon` is a v0 and is not printed yet. `Finger_Frame-2` only held the servos in the original hand and has no job in the tendon hand; it is still compatible with the new plate.
- The cross bar fills the original M2 rod hole of the barrel. Nothing else of the original Link is removed.
- The rim radius grew from 9.0 to 9.7 mm in v1, so the tendon lever arm is 9.0 mm instead of 8.3 mm and the plate relief in `R-Hand_Plate_tendon` grew from R9.6 to R10.3. A v0 Link on a v1 plate works; a v1 Link on a v0 plate scrapes the plate walls of the middle and ring fingers.

### How to tie the tendon (v1)

1. Thread the tendon from the groove through the Ø1.2 channel into the pocket on the outer face (the channel leaves the groove 3 mm from the rim edge, on the side facing the fingertip).
2. In the pocket (Ø3.2 × 2.0 mm) tie a **double overhand (stopper) knot**, leave a 10 mm tail, add one drop of CA glue, and pull the tendon back so the knot sits at the bottom of the pocket. A crimp sleeve of about 1 mm works too. The knot must be larger than the 1.2 mm channel.
3. Lay the tendon in the groove and send it back to the tube along the tangent (flexor from the bottom of the plate, extensor from the top). Tension it with the servo at its centre position.
4. **Do not use the dowel hole or slot as the anchor.** They were evaluated for this: the slot is at a 6 mm radius and the round hole at the pivot, so a tendon tied there would have a 6 mm (or 0 mm) lever arm while the other leg of the loop has 9 mm. A 2D model gives a loop length mismatch of 1.7 mm at −30° and 4.7 mm at −70° (the loop would go slack or overtight). The slot also sits right under the tendon's exit tangent, so the tendon would have to turn 90° into it, and a knot in the hole would sit between the plate and the shell (gap 0.1 mm). Keep the pockets for the knots.

## License

[CC BY 4.0](LICENSE.md): free to use, including commercially, with credit.
