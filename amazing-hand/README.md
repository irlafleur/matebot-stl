# Amazing Hand (Pollen Robotics)

A 4-finger robotic hand by [Pollen Robotics](https://github.com/pollen-robotics/AmazingHand). The files are unchanged. Official assembly guide and printing tips: [AmazingHand docs](https://github.com/pollen-robotics/AmazingHand/tree/main/docs).

- `original/`: the original parts
- `enhanced/`: Pollen's enhanced versions of some parts (frame, shells, wrist interface)

## How many to print (one hand)

| Part | Quantity |
|---|---|
| Finger_Frame-1, Finger_Frame-2, Proximal, Distal, Gimbal | 4 each (one per finger). **With MateBot's tendon drive:** Finger_Frame-2 is not printed, Finger_Frame-1 and Gimbal only for the **thumb** (1 each); the plate replaces Finger_Frame-1 for the other 3 fingers and `Gimbal_tendon` replaces their Gimbal (see below). **Link: not printed** |
| Proximal_Shell, Distal_Shell | 4 each |
| BallJoint_Rod - Spacer | 8 (2 per finger), **not needed with MateBot's tendon drive** |
| Bushing D interior 6 (igus GFM-0608-04) | 8 (2 per finger), a **bought** part in Pollen's BOM, not in these files. MateBot prints it: [`matebot/stl/bushing_d6_flanged.stl`](../matebot/stl/bushing_d6_flanged.stl) |
| Palm_Shell, Hand_Plate, Top_Shell, Wrist_Interface | 1 each, L or R for the hand you build |
| Spares worth printing | 2 Gimbal, 2 Distal (and 2 Link if you build the original servo-in-palm hand) |

Pollen recommends rigid parts in PLA with at least 80% infill, and shells in flexible filament (Filaflex 82A). MateBot prints them in PETG.

With MateBot's tendon drive, the servo horn, the BallJoint_Rod Spacers and the in-palm servo mounts are not needed, the original **Link is replaced** by [`matebot/stl/finger_link_tendon.stl`](../matebot/stl/finger_link_tendon.stl), the **R-Hand_Plate** by [`matebot/stl/R-Hand_Plate_tendon.stl`](../matebot/stl/R-Hand_Plate_tendon.stl) and the **R-Palm_Shell** by [`matebot/stl/R-Palm_Shell_tendon.stl`](../matebot/stl/R-Palm_Shell_tendon.stl). Proximal and Distal are used unchanged; the **Gimbal** of the 3 plate fingers is replaced by [`matebot/stl/Gimbal_tendon.stl`](../matebot/stl/Gimbal_tendon.stl) (so it can be screwed from underneath the plate), and **Finger_Frame-1 / -2 are folded into the plate** (the thumb keeps one Frame-1 and a stock Gimbal).

## License

[CC BY 4.0 for the mechanical design, Apache 2.0 for code](LICENSE.md). Credit Pollen Robotics.
