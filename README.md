# MateBot – 3D-printable parts

MateBot is a human-size household robot built in Quebec by Ian-Remi Lafleur and documented on YouTube ([@MyMateBot](https://www.youtube.com/@MyMateBot)). Build progress: [MateBot build tracker](https://irlafleur.github.io/matebot-site/).

This repository holds every printable file used in the build. It mixes three projects, and **each folder has its own license**. Read the license of the folder you use.

| Folder | What it is | Author | License | Commercial use |
|---|---|---|---|---|
| [`matebot/`](matebot/) | MateBot's own parts: tendon-driven hand drive (spools, PTFE anchor, servo bay, tendon Link for the fingers) | Ian-Remi Lafleur | [CC BY 4.0](matebot/LICENSE.md) | Yes, with credit |
| [`matebot/code/`](matebot/code/) | Test code: Arduino Yún + 6 STS3215 servos | MateBot | [MIT](matebot/code/LICENSE) | Yes |
| [`amazing-hand/`](amazing-hand/) | Amazing Hand robotic hand (original and enhanced) | Pollen Robotics | [CC BY 4.0 for the mechanical design, Apache 2.0 for code](amazing-hand/LICENSE.md) | Yes, with credit |
| [`inmoov/`](inmoov/) | InMoov forearm, right hand, wrist and servo bed | Gael Langevin | [CC BY-NC](inmoov/LICENSE.md) | **No** |

## Where do I start?

**Read the [Build Manual](MANUAL.md)** for clear step-by-step instructions (printing, servo IDs, assembly, wiring, first test).

1. **Hand:** print the fingers and palm from `amazing-hand/` (see its README for how many of each).
2. **Hand drive (tendons):** print the parts in `matebot/stl/`. The assembly guide is in `matebot/docs/`.
3. **Forearm:** print the shells listed in `inmoov/README.md`.

## Status

MateBot's own parts are a **v0 design that has not been tested yet**. Measure your servos before printing, and expect changes.

## Print settings used

PETG, 0.2 mm layers, printed on an Anycubic Kobra S1 and a Sovol SV06 ACE. Load-bearing parts: 4 to 6 walls.
