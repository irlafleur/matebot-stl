# Amazing Hand (Pollen Robotics)

A 4-finger robotic hand by [Pollen Robotics](https://github.com/pollen-robotics/AmazingHand). The files are unchanged. Official assembly guide and printing tips: [AmazingHand docs](https://github.com/pollen-robotics/AmazingHand/tree/main/docs).

- `original/`: the original parts
- `enhanced/`: Pollen's enhanced versions of some parts (frame, shells, wrist interface)

## How many to print (one hand)

| Part | Quantity |
|---|---|
| Finger_Frame-1, Finger_Frame-2, Proximal, Distal, Gimbal | 4 each (one per finger). **Link: not printed with MateBot's tendon drive** (see below) |
| Proximal_Shell, Distal_Shell | 4 each |
| BallJoint_Rod - Spacer | 8 (2 per finger), **not needed with MateBot's tendon drive** |
| Palm_Shell, Hand_Plate, Top_Shell, Wrist_Interface | 1 each, L or R for the hand you build |
| Spares worth printing | 2 Gimbal, 2 Distal (and 2 Link if you build the original servo-in-palm hand) |

Pollen recommends rigid parts in PLA with at least 80% infill, and shells in flexible filament (Filaflex 82A). MateBot prints them in PETG.

With MateBot's tendon drive, the servo horn, the BallJoint_Rod Spacers and the in-palm servo mounts are not needed, and the original **Link is replaced** by [`matebot/stl/finger_link_tendon.stl`](../matebot/stl/finger_link_tendon.stl). Proximal, Distal and Gimbal are used unchanged.

## License

[CC BY 4.0 for the mechanical design, Apache 2.0 for code](LICENSE.md). Credit Pollen Robotics.
