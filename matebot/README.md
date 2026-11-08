# MateBot parts (tendon-driven hand)

MateBot moves the Amazing Hand's 8 servos out of the palm and into the forearm. Each finger is driven by a pair of Feetech STS3215 (12 V) servos pulling tendons through PTFE tubes.

**Status: v0, untested.** Nothing here has been validated on a real build. Measure your own servo and servo horn before printing.

## Folders

- `stl/`: ready-to-print files
- `step/`: editable CAD files
- `source/`: Python scripts that generate the parts (`parts.py`)
- `docs/`: design notes, assembly guide (French), preview images and an explainer animation

## Parts to print

| File | Quantity | Notes |
|---|---|---|
| `spool_r8.stl` | 8 (+2 spare) | One per servo. Two grooves: flexor and extensor. 100% infill or 6 walls. |
| `ptfe_anchor_8x.stl` | 1 per tube end, still to be confirmed | Holds the PTFE tube ends. |
| `servo_bay_8x_sts3215.stl` | 1 | **Bench testing only.** It does not fit inside the forearm; it will be replaced by 4 pair mounts. |
| `finger_tendon_adapter_test.stl` | 1 | Test part. Print one before making four. |

## Known issues

- The spool's horn screw pattern is not yet matched to the real Feetech horn.
- The servo pocket clearance is tight (about 0.2 mm per side).
- The 4 servo-pair mounts and the wrist adapter have not been designed yet.

## License

[CC BY 4.0](LICENSE.md): free to use, including commercially, with credit.
