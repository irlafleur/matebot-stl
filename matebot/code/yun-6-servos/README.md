# Arduino Yún + Waveshare Bus Servo Adapter (A) + 6 × Feetech STS3215

Drives 6 STS3215 serial-bus servos daisy-chained, from an Arduino Yún, through the Waveshare Bus Servo Adapter (A). No library needed: the Feetech STS protocol is implemented in the sketch.

## 1. Give each servo its own ID (once, before chaining)
Every servo ships with ID 1, so six on one bus won't work.
1. Adapter jumper on **B** (USB mode), adapter on the PC by USB-C, 12 V plugged into the adapter's barrel jack.
2. Connect **one** servo. Open Feetech **FD** (download on the [Waveshare wiki](https://www.waveshare.com/wiki/Bus_Servo_Adapter_(A))), pick the COM port, 1000000 baud, Open, Search.
3. Programming tab, ID row (address 5), type the new ID (1 to 6), Save. Power-cycle, Search again to confirm, label the servo.

## 2. Wiring to the Yún (jumper on **A**)
- Adapter RX to Yún pin 0 (RX), adapter TX to Yún pin 1 (TX). RX-RX / TX-TX is what Waveshare specifies for this board.
- Adapter GND to Yún GND (common ground required).
- 12 V **only** on the adapter's barrel jack, never on the Yún. The adapter's USB-C stays unplugged; the Yún is powered by its own micro-USB.
- Servos chained: adapter, servo 1, servo 2, … servo 6. Use a 12 V supply of at least 5 A.

## 3. Yún gotcha
On the Yún, pins 0/1 (Serial1) are also wired to the Linux processor, which uses them as a console. To avoid conflicts:
- don't use `Bridge` in this sketch;
- disable the Linux console on that port: over SSH, comment out the `ttyATH0` line in `/etc/inittab`, then `reboot`;
- if nothing answers, wait about a minute after boot and type `scan`.

## 4. Use
Upload `yun_6_servos/yun_6_servos.ino` with the Arduino IDE 2 (board "Arduino Yún", included in Arduino AVR Boards). Serial monitor at 115200, line ending "Newline".
- `scan`: ping the 6 servos and read their positions
- `sweep`: move all 6 together, then back to center (2048)
- `m 3 2500`: servo 3 to position 2500 (0 to 4095)
- `r 3`: read servo 3's position
- `off` / `on`: torque off / on

Test without load first (no tendons attached). Not yet tested on hardware.
