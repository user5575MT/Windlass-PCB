# Connector pinout and wiring schedule

This schedule is revision 0.8 and describes the earlier `kicad/` schematic, including an ISO7721. The integrated connectors and GPIO assignments are the `kicad11/` schematic and `docs/integrated_bom.md`. The reed isolator on that board is ISO7720FDR.

Revision 0.8. Not a fabrication release. Pin 1 is the first pin of the schematic symbol. The relay contacts are routed. Most other nets are still open. Net names below are the ones in `docs/windlass.net` after the 19 November 2026 export.

Six housings replace the separate 2-pin headers. A shared housing does not join the nets. `UP_RET` is not `DN_RET`. `REED_RET` is not `GND`. `GND_CAN` is not `GND`. `NMEA_SHIELD` is not `GND`. `NET-S` has no PCB net.

## J_PWR — KF350-3.5-2P, screw, 10 A, 300 V, 18–24 AWG

| Pin | Net | Wire |
|---|---|---|
| 1 | VIN_12 | Battery positive, before the fuses |
| 2 | GND | Battery return. This is the only power ground on the board |

Silk beside the housing reads `+12` on pin 1 and `GND` on pin 2. The relays are marked `UP` and `DN`.

## J_CONTACT — KF350-3.5-4P, screw, 10 A, 300 V, 18–24 AWG

The relay contacts are dry. They are not tied to `GND` or to each other. The unmeasured Lofrans control current is still the installation block. 18 AWG is the heaviest wire this terminal accepts. If the measured current needs a heavier conductor, this housing changes.

| Pin | Net | Wire |
|---|---|---|
| 1 | UP_COM | Existing UP control feed |
| 2 | UP_NO | Existing UP control load |
| 3 | DN_COM | Existing DOWN control feed |
| 4 | DN_NO | Existing DOWN control load |

Silk in the gap beside the housing reads `U-C`, `U-N` and `D-C` for pins 1, 2 and 3. `D-N` for pin 4 is on the comment layer. Those four labels are up-common, up-normally-open, down-common and down-normally-open.

## J_PERM — KF350-3.5-4P, screw, 10 A rating, coil current only

The loop is `+12V_COIL` → pin 1 → panel relay-power switch → pin 2, then pin 2 is tied to pin 3 on the PCB, then pin 3 → ignition switch → pin 4 → the coil feed. Opening either switch drops both coils. The current is the Finder coil, about 42 mA, not the contact current.

| Pin | Net | Wire |
|---|---|---|
| 1 | SW_A | From +12V_COIL |
| 2 | SW_B | Return from the relay-power switch |
| 3 | IGN_A | Tied to pin 2 on the PCB. Ignition switch input |
| 4 | IGN_B | Ignition switch return, onward to the coils |

## J_REED — JST B4B-XH-A(LF)(SN), latched, 2.5 mm, 3 A, 250 V

Lofrans reed and the standalone dry contact. Pins 2 and 4 are the same isolated net, `REED_RET`. That shared return is not a signal path and it is not `GND`. Do not fit both sources at once. This plug is not sealed. XH accepts about 22–28 AWG.

| Pin | Net | Wire |
|---|---|---|
| 1 | REED_SIG | Lofrans reed signal |
| 2 | REED_RET | Lofrans reed return |
| 3 | DRY_A | Standalone contact |
| 4 | REED_RET | Standalone contact return. Same net as pin 2 |

### Reed mode header

`JP_REED` is a 2.54 mm 1×03 pin header, KiCad `PinHeader_1x03_P2.54mm_Vertical`. The three pins are not joined in copper. `SH_REED` is one loose 2.54 mm shunt. It is in the BOM and it is not a footprint on the board, so it cannot short the pins by itself. `JP1` only removes isolated 5 V from the CAN isolator.

| Header pin | Net | Shunt |
|---|---|---|
| 1 | LOFRANS_NODE | Default, with pin 2. Lofrans mode |
| 2 | REED_ISO | Common pin of the shunt |
| 3 | DRY_A | Alternative, with pin 2. Standalone dry-contact mode |

Fit one shunt only. Two shunts would connect pin 1 to pin 3. The silkscreen past pin 1 reads `1-2 LOFRANS` and `2-3 DRY`. `1 SHUNT` is on the comment layer, because the same words on silk crossed the down-relay outline.

### Startup and the chain counter

The existing firmware was read and not modified. It still samples GPIO27. This board's isolator output is GPIO6. A later image has to keep the same gate. Nothing here flashes or retargets the prototype.

`DebouncedInput::begin` stores the level present when the MCU starts. That sample is not an edge. `update` returns true only after the new level has been stable for 30 ms. The counter changes only when that new level is high and `direction` is already `U` or `D`. `direction` starts as `S` and is set from the sense inputs before the loop. A rising edge while the sense inputs say stopped prints `Pulse ignored: stopped or direction conflict` and does not increment `signedPulses`. A falling edge does not increment it either.

ISO7721 without the F suffix, with VCC1 valid: the output goes high if the input side is unpowered or the input is open. VCC1 is the same `+3V3` as the ESP32, so the MCU is not running while the output is in UVLO. The output is high-impedance only while VCC1 itself is below its UVLO.

- MCU startup. The first sample is the level already on the pin. It is not counted.
- Field-supply startup. The output is already at its default high. A low input, from R23 or from a closed contact, then drives the output low. That is a falling edge and is not counted. An input that is already high leaves the output high, so there is no edge.
- Field-supply shutdown. If the output was low, the default-high state produces one rising edge. It increments the counter only when a direction sense input is already active.
- Shunt removed. R23 pulls `REED_ISO` low. That is a falling edge and is not counted. The settled state is low, which is idle.
- Shunt inserted onto a high source. That is a rising edge. It increments the counter only when direction sense is already `U` or `D`. Change the shunt with the windlass stopped.

The F-suffix part was not fitted. It would swap which of these events is the rising edge. No clamp was added on the isolator output, because a clamp would fight the default-high state while the field supply is down.

### Proposed gate for a later image

Direction sense is not enough. A field-supply collapse while the windlass is already moving produces the rising edge above, and `direction` is already `U` or `D`, so the counter moves. The same is true of a shunt inserted, or a mode change, while a direction input is active. The 30 ms debounce removes chatter. It does not remove a step, because a step stays at the new level.

A hardware valid signal is required. The spare ISO7721 channel cannot carry it. On the KiCad `ISO7721D` symbol, `INB` is pin 3 on the MCU side and `OUTB` is pin 6 on the field side, so that channel points from the MCU toward the field. The reed channel is the only field-to-MCU channel, and it is already the pulse.

The proposed part, not fitted on this revision, is a second one-channel isolator with a default-low output. Its input ties to `REED_3V3`. Its output is `REED_VALID` into a free GPIO, with a pulldown. The GPIO is not chosen. U11 stays the coil heartbeat and is not reused. Changing the existing ISO7721 to the F suffix is not a substitute: power coming back onto an idle-high input is still a rising edge, and a shunt insertion is still a rising edge.

A later image, not this prototype, should count a rising edge only when both of these are true:

- `REED_VALID` has been high for longer than the longest chain pulse that installation will produce. That blank covers MCU start, reset, and the field rail coming back.
- The low interval that just ended was at least 30 ms and no longer than that same maximum. A jumper removal holds the input low. A jumper insertion or a mode change is a step, not a pulse of that width.

The 30 ms figure is the prototype debounce. The chain calibration default is 0.36 m per pulse, stored in NVS, and it is not a hardware constant. The Lofrans magnet duty and the maximum gypsy speed have not been measured. At 0.36 m per pulse, a pulse period of 0.72 s is 0.5 m/s of chain. The low portion would have to be under about 4 percent of one pitch before a 30 ms debounce swallowed a real pulse. That is a bound. It is not a measured clearance. The duty stays open.

The 4.7 kΩ pull-up, `R22`, exists only between `REED_3V3` and `DRY_A`.

- Pins 1–2. `DRY_A` stays open. A closed dry contact on J_REED pins 3 and 4 only returns the pull-up current into `REED_RET`. There is no copper path from that contact to `REED_ISO`, `LOFRANS_NODE` or `REED_SIG`.
- Pins 2–3. `LOFRANS_NODE` stays open. The pull-up reaches the isolator and does not reach `REED_SIG`. `R20` (10 kΩ) and the clamps `D20`/`D21` stay on the Lofrans node, so a cable left on J_REED pins 1 and 2 is still loaded. That load is not the dry-contact pull-up feeding the Lofrans signal.
- Shunt removed. `R23`, 47 kΩ, holds `REED_ISO` at `REED_RET`. With the field supply on, the isolator output stays low. The firmware counts rising edges, so that state produces no pulses. If the field supply is off, the ISO7721 without an F suffix defaults its output high, and high is also idle. Either state is inactive.

An open header is not a safety barrier. The exported netlist has no pin on both `LOFRANS_NODE` and `DRY_A`.

## J_SENSE — JST B5B-XH-A(LF)(SN)

Two direction-sense loops. `UP_RET` and `DN_RET` are not connected. Pin 3 is unused and is the separation between the two returns. A two-pin pair for each loop also fits on this edge and was not used. The unused pin is there so a strand between the return pins has to cross an open position.

| Pin | Net | Wire |
|---|---|---|
| 1 | UP_FIELD | UP sense, into R30 |
| 2 | UP_RET | UP sense return only |
| 3 | no connect | Unused separator. Do not land a wire |
| 4 | DN_FIELD | DOWN sense, into R40 |
| 5 | DN_RET | DOWN sense return only |

## J_NMEA — JST B5B-XH-A(LF)(SN)

This header is not a Micro-C. A pigtail has to map it. The board makes its own isolated 5 V and does not draw backbone power, so NET-S is open. `GND_CAN` connects only to NET-C. Shield goes to the cable shield and, on the PCB, through C92 to `GND_CAN`. It is not connected to MCU ground.

| Pin | PCB net | Drop wire | Micro-C |
|---|---|---|---|
| 1 | GND_CAN | Black, NET-C | Pin 3 |
| 2 | CAN_L | Blue, NET-L | Pin 5 |
| 3 | NMEA_SHIELD | Bare shield | Pin 1 |
| 4 | CAN_H | White, NET-H | Pin 4 |
| 5 | no connect | Red, NET-S. Do not land it | Pin 2 |

## Power and return paths

- `VIN_12` and `GND` feed the MCU fuse and the coil fuse. They do not feed the isolated secondaries.
- `+12V_MCU` feeds only the two bucks. `+12V_COIL` feeds only J_PERM and the relay coils.
- Reed power is `REED_3V3` from U4, returned on `REED_RET`.
- CAN power is `ISO_5V` from U9, returned on `GND_CAN`.
- Direction-sense LED current returns only on that channel’s RET pin. The optocoupler emitter is MCU `GND`.

## What was rejected

Smaller isolated modules that are in stock at JLCPCB are 1 kV or 1.5 kV clones, or they were out of stock. They were not exchanged for the Murata MEJ2. See `docs/component_availability.md`.
