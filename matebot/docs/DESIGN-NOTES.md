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
1. **`finger_link_tendon`** (done in v0, untested): the original Link plus a cross bar and two capstan plates (groove on the rim, two Ø3.2 × 2 mm knot pockets, Ø1.2 mm channels with a 3 mm bend radius). See `finger_link_tendon_preview.png` and `finger_link_tendon_routing.png`. Generator: `source/finger_link_tendon.py`.
2. Flexor on the palm side (−Z, lower pocket and lower tangent), extensor on the back (+Z, upper pocket and upper tangent). The rim radius is 9.0 mm and the tendon centre radius 8.3 mm, so the tendon never bends tighter than about 3 mm (channel) and 8.3 mm (groove).
3. Moment arm at the base joint: **8.3 mm** (about the spool radius → about 1:1 angle mapping). Loop conservation was checked numerically (flexor stroke minus extensor stroke ≤ 0.2 mm over 0 to −70°, tube ends assumed 40 mm behind the pivot).
4. Proximal, Distal, Gimbal: **unchanged**. Nothing in the 4-bar needs to change.
4. Palm: remove servo pockets, add a **PTFE tube termination plate** (`ptfe_anchor_8x`) at the wrist side of the palm.
5. Keep TPU pads/shells from the original.

## 4. Forearm servo bay
- 2 rows × 4 STS3215, outputs facing up, part `servo_bay_8x_sts3215` (≈120 × 103 × 18 mm, fits the SV06 220 mm bed and the Kobra S1).
- STS3215 nominal body **45.2 × 24.7 × 35 mm** (Feetech datasheet nominal) — **measure a real servo before printing**; clearance parameter `CL=0.4 mm` in `parts.py`.
- Bay bolts to the forearm structure with 4 × M3. Daisy-chain servo cables run underneath through the cutouts.
- A full InMoov-size forearm (~250 mm long) has room for this bay plus the wrist.

## 5. Pulley / spool
- `spool_r8`: two grooves (flexor + extensor) at r = 8 mm, flanges r = 11 mm, cross-hole to anchor each tendon end.
- Bolts to the stock STS3215 round horn with 4 × M2.5. **Horn bolt-circle assumed 14 mm diameter — verify**; edit `parts.py`.
- Travel (CAD estimate with the tendon Link): full flexion (~70° of Link rotation) ≈ 10 mm of tendon, abduction ±20° ≈ ±4.5 mm, up to ~15 mm in total ≈ 105° of spool rotation. Large margin vs. servo 360° range.
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
- BOM: [`bom/hand-tendon.csv`](../bom/hand-tendon.csv)
