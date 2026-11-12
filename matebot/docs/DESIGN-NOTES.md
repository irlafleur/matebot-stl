# MateBot Hand v0: tendon-driven Amazing Hand variant

> Status: **v0 design, untested**. Nothing here has been printed or measured yet. All force numbers are **estimates**.
>
> Based on [Pollen Robotics Amazing Hand](https://github.com/pollen-robotics/AmazingHand), licensed **CC BY 4.0**. Changes: in-hand servos removed, fingers re-driven by Bowden tendons from forearm servos. Credit to Pollen Robotics for the original finger design.

## 1. Architecture
- 4 Amazing Hand fingers, 2 DoF each (8 DoF total), kept as close to the original as possible.
- The 8 in-hand STS3032 servos are removed. The palm becomes a thin printed shell with tendon guides.
- 8 × Feetech STS3215 12V (30 kg·cm) in a forearm servo bay, each with an ~8 mm radius double-groove spool.
- Tendons: braided PE (UHMWPE) fishing line, ~100 lb class, running inside 2×4 mm PTFE tubes (Bowden) from the forearm to the palm.
- Same Feetech serial bus as the arm (Waveshare Bus Servo Adapter, 12 V supply). Control via LeRobot / ROS 2.

## 2. Mapping the Amazing Hand mechanism to tendons
In the Amazing Hand, each finger is driven by **two servos working as a parallel/differential pair**: both turning the same way = flexion/extension; turning in opposite directions = sideways (abduction/adduction) motion. Each servo horn pushes the finger through an M2 rod with ball joints.

Tendon mapping (keeps the same control logic):
- Each servo becomes **one closed antagonist loop**: one groove of the spool pulls a flexor tendon, the other groove pulls an extensor tendon. Turning the spool pulls one and releases the other by the same length, so no slack and no return spring is needed.
- In Pollen's finger the two ball-joint rods attach to the two ends of the cross bar of the **Link** (left rod and right rod). The Link is the crank that drives Proximal and Distal through a 4-bar linkage, so the tendons attach to the Link, not to Proximal or Distal.
- **Crossed loops.** A tendon pulling at lateral offset ±L shortens by L·θ when the finger abducts by θ. If both legs of one loop sat on the same side they would both shorten, which a closed loop cannot allow (the abduction would be locked). So each servo's flexor goes to one side and its extensor to the **opposite** side: leg lengths then change by +Lθ and −Lθ and the loop is conserved. Servo A: flexor on +X, extensor on −X. Servo B: flexor on −X, extensor on +X. Then A+B same direction = flexion, opposite = abduction, as in Pollen's code (sign of abduction to be set at first test).
- The distal joint keeps the original coupling of the Amazing Hand finger (it is not separately actuated).

Option considered: flexor-only tendons + return springs/elastic. Cheaper (4 fewer tube runs) but weaker extension and the springs eat grip force. **Default is antagonist loops**; springs are the fallback.

## 3. Finger modifications (CAD work still to do on the STEP files)
1. **`finger_link_tendon`** (v1, untested): the original Link plus a cross bar and two capstan plates (groove on the rim, two Ø3.2 × 2 mm knot pockets, Ø1.2 mm channels with a 3 mm bend radius). v1 adds the dowel pass-through (see 3a). See `finger_link_tendon_preview.png` and `finger_link_tendon_routing.png`. Generator: `source/finger_link_tendon.py`.
2. Flexor on the palm side (−Z, lower pocket and lower tangent), extensor on the back (+Z, upper pocket and upper tangent). The rim radius is 9.7 mm (v1; was 9.0) and the tendon centre radius 9.0 mm (v1; was 8.3), so the tendon never bends tighter than about 3 mm (channel) and 9.0 mm (groove).
3. Moment arm at the base joint: **9.0 mm** (v1; the spool is 8 mm, so the spool turns about 12% more than the Link). Loop conservation (flexor stroke minus extensor stroke): ≤ 0.2 mm over 0 to −70° in v0 with tube ends 40 mm behind the pivot, and ≤ 0.13 mm from +10° to −70° in v1 with the tube ends of `R-Hand_Plate_tendon` (25.4 mm behind the pivot, 2D model).
4. Proximal, Distal, Gimbal: **unchanged**. Nothing in the 4-bar needs to change.
4. Palm: **`R-Hand_Plate_tendon`** (v0, untested) replaces the Hand_Plate: 6 anchor columns with 12 PTFE sockets for the index, middle and ring (the thumb sits on the Wrist_Interface and still needs its 4 anchors). See section 3b. `ptfe_anchor_8x` is now only for the servo side of the tubes.
5. Keep TPU pads/shells from the original.

## 3a. Dowel pass-through in the Link plates (v1)
The two capstan plates sit at X = 12 to 14.4 mm, on the axes of the assembly pins of the Amazing Hand, so the pins could not be pushed in from outside:
- **D2×10 Gimbal ↔ Link pin:** axis X through the Link pivot (Y = 0, Z = −6), length 10 (Gimbal ±5). The plate disc is centred on this axis, so the plate is solid on it.
- **D2×16 Gimbal ↔ Proximal pin:** axis X at (Y = 0, Z = 0), length 16.2 (Proximal ears at X = ±8.1, holes Ø2.0). The plate disc (R 9.7 around the pivot) covers (0, 0) at 6 mm from the pivot, so it blocked the pin. (The other D2×16 pin, Proximal ↔ Distal at Y = 52, and the D2×10 pin Distal ↔ Link at Y = 49.2, are far from the plates.)
- **Fix:** Ø2.5 round hole on the pivot axis (D2×10) and Ø2.5 arc slot at 6 mm radius, 80° to 120° around the pivot (D2×16). The slot is an arc because the Link turns: a round hole at (0, 0) lines up only at one exact Link angle, a Ø2.5 hole allows about ±2° around that angle for a Ø2.0 pin.
- **Conflicts and what moved:** the top of the slot is at r = 7.25 mm from the pivot, but the groove floor was at 7.8 mm (wall 0.55 mm, below the 1.2 mm wanted). The rim radius was raised from 9.0 to 9.7 mm, keeping the groove 1.2 mm deep: groove floor 8.5 mm, wall 1.25 mm, tendon centre radius 9.0 mm instead of 8.3 mm. The knot pockets and channels did **not** move (nearest wall at the slot: 2.4 mm to the extensor pocket at the nominal angle; the slot range stops at 80° where it is 1.5 mm from the pocket). The wedge removed from the lower back of each plate started at the pivot and would have opened the round hole, so its apex now starts 4.2 mm from the pivot.
- **Side effects:** lever arm +8% (tendon stroke for 70° of flexion 10.1 → 11.0 mm, torque on the Link +8% for the same tendon tension); `R-Hand_Plate_tendon` relief radius R9.6 → R10.3 and its tendon corridors aim at the new tangent heights Z = +3.0 / −15.0 (sockets unchanged at +2.3 / −14.3, so the tendon leans 0.7 mm over 25 mm).
- **Using the hole as the tendon anchor was evaluated and rejected** (the dowel does not stay in it, so it is free after assembly): an extensor tied in the slot has a 6 mm lever arm against 9 mm for the flexor, which breaks loop conservation (mismatch 1.7 mm at −30°, 4.7 mm at −70°, 2D model); entry from the groove would be a 90° turn at the exit tangent; the pivot hole has no lever arm at all. Knots stay in the pockets.
- Checks: `source/verify_finger_link_tendon.py` (wall ≥ 1.2 mm around both holes, pin paths clear for the whole insertion length with the Link tilted +10° to −30°).

## 3c. Finger bushing (printed equivalent of Pollen's GFM-0608-04)
- **Upstream:** the Amazing Hand BOM and assembly guide list "Bushing D interior 6 mm / D exterior 8 mm" (igus iglidur GFM-0608-04, flanged, bore 6, OD 8, length 4 including the flange, flange D12 × 1), 2 per finger, pressed into both sides of `Finger_Frame-1` as the abduction / adduction pivot. The guide's last step tightens the M2.5 large washer + 2.5×8 screw "until the washer is in contact with the bushing". All other pivots (D2×10, D2×16 axes) run directly in printed holes.
- **CAD facts read from the STEP files:** `Finger_Frame-1` has a D8.15 through bore, Z 4.5 to 12.5; the Gimbal boss is D6.0, Z 3.5 to 13.5, i.e. it protrudes exactly 1.0 mm on each side, the flange thickness; the Gimbal shoulder (D11.9) and the frame's R6.0 outer arc both match the D12 flange.
- **Printed bushing** `bushing_d6.py`: bore D6.20 (+0.20 over the boss, as printed bores run small), OD D8.10 (+0.05 under the CAD bore: light press once printed), flange D12.0 × 1.0, length 4.0, 0.95 mm wall, 0.25 lead-in chamfer. Quantity 8 + 2 spares.
- **Checks** (`verify_bushing_d6.py`, 12 of 12): no interference with Frame-1, Gimbal (turned ±30°), Frame-2, Proximal, shells, Distal, hand plate, tendon Link, tendon plate and palm shell (rest pose and swept −80° to 0° flexion). Hyper-extension: the flange first touches the Proximal at +5° past straight, the TPU Proximal_Shell at +9°, and the original frame stops the Proximal at +7°, so the flange does not shorten the real range. The new Link plates (|X| ≥ 12) and the dowel slot are nowhere near the flanges (R6).
- **Friction:** PETG on PETG is rough. Grease the boss, or print the bushings in a harder or slicker filament if you have one (PA, PETG-CF). This is untested.
- **Open:** real printed bore and boss sizes (measure), thumb frame (assumed identical).

## 3b. Palm plate with tube anchors, pivot blocks and Gimbal retention (`R-Hand_Plate_tendon`, v1 untested)
Source: `source/R-Hand_Plate_tendon.py`; checks: `source/verify_R-Hand_Plate_tendon.py`; images `R-Hand_Plate_tendon_preview.png` and `R-Hand_Plate_tendon_routing.png`.

- **Count.** The plate carries 3 fingers. Each finger has 4 tendon ends (2 servos × flexor + extensor), so 12 sockets, not 8. The thumb is mounted on the Wrist_Interface, its 4 ends are still open.
- **Finger poses on the plate** (fitted to the plate's own M2.8 holes at (±6, −7) in the finger frame, worst error 0.19 mm): index at (0, 0) rotated 0°, middle at (32.8, −6.0) rotated −5.76°, ring at (65.0, −17.1) rotated −13.46°. All Pollen parts share one assembly frame, so the finger frame of the index is the plate frame.
- **Tendon lines.** At rest the tendons leave the capstan (radius 9.0 since Link v1, around the Link pivot at Y = 0, Z = −6) along −Y at Z = +3.0 (extensor) and Z = −15.0 (flexor), X = ±13.2. v1: sockets at Z = +2.3 / −12.8 (flexor moved up 1.5 mm), so the extensor leans 0.7 mm and the flexor 2.2 mm over 25 mm; the Ø3 corridors are aimed at the real tangent points (computed from the cone mouth).
- **Socket positions.** Sockets at |X| = 10.5 (not 13.2) in the finger frame, tube stop at Y = −30. Reason: the fingers fan out, so lines of neighbouring fingers converge toward the wrist (6.4 mm apart at the capstans, 3.5 mm at Y = −30). At |X| = 10.5 the sockets of neighbours are at least 7.9 mm apart (3.7 mm of wall). Cost: the tendon leans atan(2.7 / 25.4) = 6° inward; the cone exit (22° half angle) absorbs the swing. The change in tendon length is small but not included in the earlier loop-conservation check (that assumed straight tendons 40 mm behind the pivot).
- **Columns.** 8.2 × 12.6 mm, from the slab top face (Z = 15.5) down to Z = −16.9 mm (v0 −18.4: **1.5 mm shorter, sockets 15.1 mm apart instead of 16.6**), so they print slab-down without supports. Why only the flexor moved: shifting both sockets 0.75 mm would leave 1.25 mm of wall under the flexor bore (< 1.6 mm); moving only the flexor up keeps the bottom margin at 4.1 mm (2.0 mm wall under the bore). Each fuses with the original plate over 265 to 555 mm³.
- **Relief cuts in the original plate:** R10.3 cylinder around each Link capstan plate (swept R9.7 + 0.6; v1: 2.6 mm longer on the outer side for ±25° abduction) (the plates of the middle and ring fingers touched the plate walls, up to 32 mm³), Ø3.0 tendon corridors, Ø4.5 tube clearance holes through the cross beam behind the extensor sockets. About 730 mm³ removed in total.
- **Palm shell.** The two outermost flexor columns (index left, ring right) touch the soft palm shell skin (about 270 mm³ in total), so `R-Palm_Shell_tendon` has notches there (0.6 mm margin), plus clearance for the Gimbal posts, washers and screw heads, plus the bigger thumb aperture (see below): about 1030 mm³ removed in total in v1.
- **Frame-1 / Frame-2 folded into the plate (v1).** Frame-1 was only a bearing block for the Gimbal boss: X ±10, Y −15 to +6, Z 4.5 to 12.5 with the D8.15 bore (the Gimbal boss D6.0 runs in the 2 bushings). The plate now has that block under the slab, built from the outline of Frame-1's bottom face, with the same bore and 0.3 mm chamfers. Only about 10 mm³ of Frame-1 (its screw holes and bore) is not covered. Frame-2 only carried the servos of the original hand. Check: bushing pair fits all three bores (0 mm³), the stock Gimbal and `Gimbal_tendon` turn ±25° without touching anything, and Proximal/shells/Distal/Link sweeps clear the block (only the +5° to +7° hyper-extension stop touches, exactly as with the stock Frame-1). The thumb is on the Wrist_Interface, so it still needs one printed Frame-1 and a stock Gimbal.
- **Gimbal retained from below (v1).** Pollen's retention is a screw and washer on top of the boss (blind Ø1.9 hole, Z 5.5 to 13.5). Rejected options: (a) screw in the boss axis from below: the Gimbal is solid at Z = 0 and the D2×16 pin crosses the axis; (b) a retainer bar under the shoulder: the Proximal ears sweep radius 5.2 to 8.75 mm over Z ±3.3 during abduction; (c) a clip groove in the boss: only 1.0 mm of boss shows on each side; (d) a through-bolt: no room next to the pin. Chosen: `Gimbal_tendon` gets a rear tab (Z 0.5 to 3.5, 8.0 mm wide at radius 8.6, clipped at Y ≤ −3.7) with a Ø5.0 arc slot (±25°, wall 1.5 mm); the plate has a Ø4.4 post at (0, −8.6), Z 0.1 to 4.5, with a Ø1.9 × 8 mm pilot (wall 1.25 mm). Large M2.5 washer (Ø8 × 0.8) + the existing 2.5×8 screw from below, 7.2 mm of thread. The post bottom is 0.4 mm below the tab so the washer does not clamp it; the tab has 1.0 mm of room under the block. The abduction range assumed is ±25°.
- **Thumb aperture (v1).** The thumb sits on the Wrist_Interface with 3 screws; its pose was ESTIMATED from the 3-hole pattern ((8.04, −35.1), (−3.24, −30.9), (15.22, 2.2) in hand X, Z): finger axis 20° off −Z toward −X, origin (0, −72.5, −39.58). Check: the stock thumb parts do not touch the stock shell at rest; only the tendon Link plates collide. The aperture is cut as ONE boolean of convex prisms: two for the Link plates (disc R9.7 + 1.5 swept ±25°, hull per side, extruded along Y) and one at the wrist end for the Proximal and Proximal_Shell (swept ±25° × flexion −80° to +5°, grown 1.5 mm). The shell skin boolean breaks with many near-coincident cylinders, hence the few convex prisms and a final cleanup of zero-volume slivers. Result: the shell loses about 1030 mm³ in total; every moving thumb part stays at least 1.5 mm from the new shell and the plate over abduction ±25° × flexion −80° to +5° (min distances in `verify_R-Hand_Plate_tendon.py` output; the printed Finger_Frame-1 of the thumb, bolted on the interface, is 0.54 mm from the new shell, 0.35 mm from the stock shell: it is the fixed mounting part, it sits close by design).
- **Strength.** The columns are only tube stops: the tendon tension is carried by the tube from the servo to the socket, not by the plate. Pull-out of a glued 4 mm tube from an 8 mm socket is not measured.
- **Open points.** The thumb pose (estimated), the real abduction range, printed bore and pilot tolerances. Tendon lines are checked at rest and ±25° abduction. Tubes passing the Wrist_Interface overlap its walls by 1 to 145 mm³ per tube (straight-line check, 10 of 12 tubes touch): to be solved by the wrist adapter, which must also take the thumb's tubes. The tendon-length effect of the 6° inward lean over the full flexion and abduction range is not recomputed.

## 4. Forearm servo bay
- 2 rows × 4 STS3215, outputs facing up, part `servo_bay_8x_sts3215` (≈120 × 103 × 18 mm, fits the SV06 220 mm bed and the Kobra S1).
- STS3215 nominal body **45.2 × 24.7 × 35 mm** (Feetech datasheet nominal) — **measure a real servo before printing**; clearance parameter `CL=0.4 mm` in `parts.py`.
- Bay bolts to the forearm structure with 4 × M3. Daisy-chain servo cables run underneath through the cutouts.
- A full InMoov-size forearm (~250 mm long) has room for this bay plus the wrist.

## 5. Pulley / spool
- `spool_r8`: two grooves (flexor + extensor) at r = 8 mm, flanges r = 11 mm, cross-hole to anchor each tendon end.
- Bolts to the stock STS3215 round horn with 4 × M2.5. **Horn bolt-circle assumed 14 mm diameter — verify**; edit `parts.py`.
- Travel (CAD estimate with the tendon Link v1, 9.0 mm lever arm): full flexion (~70° of Link rotation) ≈ 11 mm of tendon, abduction ±20° ≈ ±4.5 mm, up to ~15.5 mm in total ≈ 111° of spool rotation. Large margin vs. servo 360° range.
- Print in PETG, 100% infill or 6 walls; wrap tendons ≥1.5 turns before the anchor.

## 6. Tendon routing through the wrist
- 16 tendons (8 loops × 2) in 16 PTFE tubes, about 30–40 cm each.
- Tubes are fixed at both ends (servo-side anchor block and palm anchor block). Because the tube length is fixed (Bowden), **wrist motion barely changes tendon length**; keep tube bend radius ≥ 30 mm.
- Route the bundle through the wrist center to minimize length change from wrist pitch/yaw.
- Pre-tension each loop with the servo (set mid-position, then tie off).

## 7. Scaling 1.2×
- The Amazing Hand is smaller than an adult hand. Scaling 1.2× in the slicer works for the shells, but **do not scale pin holes and tendon channels**: re-export from STEP with 2 mm pins / 1.2 mm channels restored.
- Scaling raises the fingertip lever by 1.2×, so fingertip force drops ~17% unless the base moment arm grows to ~9.6 mm (scale the spool to r ≈ 9.6 mm too to keep 1:1).

## 8. Force estimate (ESTIMATE, not tested)
- STS3215 12V stall ≈ 30 kg·cm ≈ 2.94 N·m. Use ~35% for continuous holding ≈ 1.0 N·m (thermal limit).
- Tendon tension at r = 8 mm: 1.0 / 0.008 ≈ **125 N** continuous (≈ 370 N at stall — the 100 lb ≈ 445 N line is enough, but don't hold stall).
- Bowden + channel friction loss: assume 40% → ~75 N effective.
- Base joint moment arm 8 mm, fingertip lever ~80 mm → ~7.5 N per servo at the fingertip; 2 servos per finger in flexion → **~15 N per finger**.
- 4 fingers wrapping an object against the palm with friction μ ≈ 0.5 (TPU) → hold ≈ 4 × 15 × 0.5 ≈ 30 N ≈ **~3 kg power grasp**; pinch much less. Realistic target: **2–3 kg held, about 3× the Enhanced Amazing Hand estimate**.
- Comparison: Enhanced Amazing Hand STS3032 is 4.5 kg·cm peak in the hand with short levers; STS3215 has ~6.7× the torque but loses some to friction and routing.

## 9. Control
- Bus: Feetech SCS/STS serial at 1 Mbps via Waveshare Bus Servo Adapter, shared or separate from the arm bus (recommend a **separate bus/adapter for the hand** at first for debugging). IDs 21–28 for hand servos.
- Software: Feetech SDK / LeRobot `feetech` motor bus; ROS 2 later. Port Pollen's finger mixing (A+B = flex, A−B = abduction).
- Safety: torque limit in servo EEPROM (start at 10% for the finger tests (tendon Link is the weak part), 30% at most later), temperature monitoring, e-stop in 12 V line.

## 10. Assembly and test plan
1. Measure STS3215 and horn; adjust `parts.py`; print spool + anchor + 1 finger with `finger_link_tendon`.
2. **Single-finger bench test**: 1 finger, 2 servos, 40 cm PTFE runs. Check range, backlash, friction (measure servo load reading).
3. Luggage-scale test: hook the fingertip, ramp torque limit, record N at fingertip. Film it for the channel.
4. Build all 4 fingers + palm, full bay.
5. **Grip test**: grasp a bottle filled progressively with water, hung from a luggage scale; record max hold before slipping. Update this doc with measured numbers.
6. Endurance: 30 min cycling, check tendon creep and re-tension.

## 11. Risks
- Friction/hysteresis in PTFE runs reduces force and precision (mitigate: short runs, large bend radius, PTFE lube).
- Tendon creep/stretch of PE line → re-tension; try Dyneema with low creep.
- Line cutting into PETG channels → add PTFE sleeve or metal eyelets at sharp turns.
- Servo overheating if holding near stall → torque limits.
- Finger mechanism coupling may not map cleanly to tendons; may need finger redesign.
- The Link plate and the Ø6 cross bar carry the full tendon tension. They are the weakest part of the finger: start at a 10% servo torque limit.
- The tendon plates reach X = ±14.4 mm; with a finger pitch of about 30 mm neighbours would be only about 1.2 mm apart (not verified on a real palm).
- Unverified dimensions (servo body, horn bolt circle).

## 12. Open questions
- Antagonist loops vs. flexor + springs?
- Scale 1.2× now or after the 1× prototype?
- Separate hand bus or shared with arm?
- Thumb-like opposition: rotate one finger base 60–90°?

## Files
- Starter parts (v0, untested, STL+STEP+PNG): `matebot-hand-tendon.zip` (not in git; no Git LFS yet). Source script `parts.py`.
- Palm plate and palm shell: `../stl/R-Hand_Plate_tendon.stl`, `../stl/R-Palm_Shell_tendon.stl`, `../stl/Gimbal_tendon.stl` (STEP in `../step/`).
- BOM: [`bom/hand-tendon.csv`](../bom/hand-tendon.csv)
