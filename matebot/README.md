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
| `finger_link_tendon.stl` | 4 (+2 spares) | **Replaces Pollen's `Link`** (do not also print the original Link). Same pivot holes, plus a cross bar and two tendon plates. Print 1 first. Needs supports. |

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
| Socket axes | X = ±10.5 mm, extensor at Z = +2.3 mm, flexor at Z = −14.3 mm (tangents of the 8.3 mm capstan around the Link pivot at Z = −6) |
| Column | 8.2 mm wide, 12.6 mm long (Y −38.0 to −25.4), from the slab top (Z = 15.5) down to Z = −18.4 mm |
| Wall around every socket | 2.0 mm (bore), 1.6 mm (cone mouth) |

The sockets sit at X = ±10.5, not at the capstan lines X = ±13.2: this keeps the sockets of neighbouring fingers at least 7.9 mm apart (the fingers fan out by 5.8° and 13.5°), and the tendon leans about 6° inward between the socket and the capstan.

Other changes to the original plate: a Ø4.5 mm clearance hole behind each extensor socket where the tube crosses the plate's cross beam (the flexor tubes pass under the plate), a Ø3 mm tendon corridor, and a cylindrical relief (R9.6) around each Link capstan plate (about 830 mm³ removed in total). All original screw holes are kept.

What was **checked in CAD** (script `source/verify_R-Hand_Plate_tendon.py`, 20 checks): single valid solid; finger positions fitted to the plate's own screw holes (worst error 0.19 mm); no original hole plugged; wall ≥ 1.6 mm around all 12 sockets; no tendon line (finger at rest) touches the plate, Finger_Frame-1/-2, Gimbal or Proximal; the swept Link capstan plates clear the plate; the new material clears the Finger_Frame, Gimbal, Proximal, Top_Shell and Wrist_Interface.

What is **not** verified: nothing has been printed. The tendon lines were checked with the finger at rest only (not over the full flexion and abduction range). The thin walls left beside the extensor clearance holes where they cut through the original pockets can be as thin as 0.2 mm (they will not print, the hole simply opens into the pocket). The tubes were only checked straight from the sockets back to Y = −85 mm; they will overlap the Wrist_Interface walls a little, which is to be solved with the wrist adapter.

Printing: PETG, plate slab-down exactly like the original (no supports needed: the columns reach the slab top face), 0.2 mm layers, 5+ walls and 40% or more infill (the columns carry the tube reaction, not the tendon tension). The bores are horizontal; they bridge over 4.2 mm, so check them with the tube before gluing and ream with a Ø4.2 drill if tight. Glue the tubes in with a drop of CA glue.

Check with calipers: the PTFE tube OD (the sockets assume 4.0 mm: if yours is 4.1 or more, change `sock_d`), and that the tubes seat fully (8 mm).

## The finger part: `finger_link_tendon` (v0, untested)

In Pollen's Amazing Hand, the two ball-joint rods are screwed onto the ends of the cross bar of the **Link**, not onto the Proximal or Distal. The Link is the input crank of the finger: it drives the Proximal and the Distal through the 4-bar linkage. So the Link is the only finger part that has to change. **Proximal, Distal, Gimbal and the shells are printed unchanged.**

`finger_link_tendon` keeps the original Link (all pivot holes untouched) and adds:
- a Ø6 cross bar (same place and size as the original barrel, now 24 mm long);
- two identical plates at the ends of the bar, **X = ±12.0 to ±14.4 mm** from the finger axis (just outside the 11.9 mm half-width of the Proximal_Shell);
- on each plate: a U groove (1.4 mm wide) around the rim, centred 8.3 mm from the Link pivot, so the tendon wraps the plate like a capstan with a constant lever arm of about 8.3 mm (the same as the 8 mm spool);
- two knot/crimp pockets per plate (Ø3.2 × 2.0 mm, open on the outer face) with a Ø1.2 mm channel that leaves the groove on a 3 mm radius bend. The **lower pocket is the flexor** (palm side, −Z), the **upper pocket is the extensor** (back, +Z).

**Which tendon goes where.** Each servo has one loop with a flexor and an extensor. The two legs of a loop go to **opposite plates**: servo A's flexor to the +X plate and its extensor to the −X plate; servo B's flexor to the −X plate and its extensor to the +X plate. Crossing is required: if both legs of a loop went to the same plate, the finger could not abduct, because side motion shortens both legs of that plate by the same amount and a closed loop cannot absorb that. With the crossed layout, A and B turning the same way flex the finger and opposite ways abduct, as in Pollen's code (the sign of abduction depends on which servo you call A).

Design numbers (CAD estimates from the original STL files, not measurements on a print):
- Link rotation for full flexion: about 70°; the Proximal turns about 65° and the Distal about 128°.
- Tendon stroke per leg: about 10 mm for 70° of flexion, plus or minus about 4.5 mm for ±20° of abduction. Total up to about 15 mm, which is about 105° of rotation of the 8 mm spool.
- Clearance over the flexion range (−80° to +15°) between the new material and the Gimbal, Proximal, Proximal_Shell and Finger_Frame-1: at least 0.38 mm to the Gimbal, 0.86 mm to the shell, 2.1 mm to the Proximal (sampled check against the original STL files, one finger only; the Distal, neighbouring fingers and the palm were not checked).
- The plates reach X = ±14.4 mm. The Hand_Plate windows suggest a finger pitch of about 30 mm, so neighbouring plates would be about 1.2 mm apart. **Not verified on a real palm.**
- Printing: the original Link also needs supports in every orientation. Print `finger_link_tendon` with the plate lying flat (X up) and tree supports under the cross bar and the Link strip, 4+ walls, 100% infill on the plates.
- Strength (hand estimate, not FEA): the cross bar and plates should hold roughly 50 to 80 N of tendon tension in PETG. The STS3215 can pull much more. **Start with the servo torque limit at 10% (about 35 N at the 8 mm spool)** and raise it only after testing.

## Known issues

- The spool's horn screw pattern is not yet matched to the real Feetech horn.
- The servo pocket clearance is tight (about 0.2 mm per side).
- The 4 servo-pair mounts and the wrist adapter (with the thumb's 4 tube ends) have not been designed yet.
- `R-Hand_Plate_tendon` is a v0 and is not printed yet. `Finger_Frame-2` only held the servos in the original hand and has no job in the tendon hand; it is still compatible with the new plate.
- The cross bar fills the original M2 rod hole of the barrel. Nothing else of the original Link is removed.

## License

[CC BY 4.0](LICENSE.md): free to use, including commercially, with credit.
