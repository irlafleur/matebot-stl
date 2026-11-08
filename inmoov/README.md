# InMoov parts (Gael Langevin)

MateBot uses the InMoov right forearm as a temporary base. The files are unchanged, from [inmoov.fr](https://inmoov.fr/hand-and-forarm/).

**Non-commercial license.** See [LICENSE.md](LICENSE.md).

## What MateBot prints from here

| File | Qty | Notes |
|---|---|---|
| `Right-Hand/robpart2V4.stl` | 1 | Forearm lower shell, glued to robpart5 |
| `Right-Hand/robpart5V4.stl` | 1 | |
| `Right-Hand/robpart3V4.stl` | 1 | Forearm top cover, glued to robpart4 |
| `Right-Hand/robpart4V4.stl` | 1 | |
| `Right-Hand/robcap3V2.stl` | 1 | Only if you keep the InMoov elbow |

The shells carry 8 servos in MateBot, so print them in PETG with 4 to 6 walls.

## Not used by MateBot

- `Forearm-and-Servo-Bed/`: servo bed, pulleys, cable holders and tensioners. MateBot replaces them with its tendon drive (`../matebot/`). They are kept here for anyone building the original InMoov.
- The InMoov fingers, palm and wrist parts in `Right-Hand/`: MateBot uses the Amazing Hand instead.
- The InMoov rotating wrist is not in this repository yet. Get it from the [InMoov gallery](https://inmoov.fr/inmoov-stl-parts-viewer/?bodyparts=Rotation-Wrist).
