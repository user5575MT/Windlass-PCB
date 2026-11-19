# Design review, revision 0.2

Date: 2026-11-18. Schematic regenerated from `scripts/build_schematic.py`. KiCad 10.0.8 ERC: 0 errors, 0 warnings (`docs/erc_report.txt`). ERC checks connectivity. It does not approve current, creepage, thermal margin, or behaviour on the boat.

No PCB routing has been started. No Gerbers. No order. `WindlassProject` was not edited, flashed, or deployed.

The working prototype still has no heartbeat output. GPIO1 on this board is the heartbeat input. With the firmware that is on the bench, that pin is not toggled, the monostable stays low, and the coil path stays off. That is the intended result until a separately reviewed image exists.

## 1. Hardware watchdog

`U11` is a Nexperia 74LVC1G123. Input A is tied to GND. CLR is tied to 3.3 V. The heartbeat is a rising edge on B (GPIO1, `WDI_FUTURE`), with a 100 kΩ pulldown so reset and high-Z are a low. Q is low until a valid rising edge. A level, high or low, does not retrigger. Nexperia states that a new edge during the pulse restarts it, so repeated edges hold Q high, and stopping the edges lets the current pulse finish and then stay low.

Timing, from the Nexperia formula for CEXT above 10 nF, `tW = K × REXT(kΩ) × CEXT(pF)` nanoseconds, K nominally 1:

```text
100 kΩ × 3.3 µF = 330 ms typical
Long case, K = 1.2 and capacitor +20%: about 475 ms
Short case, K = 1 and capacitor −20%: about 264 ms
```

A ceramic loses capacitance under DC bias, which shortens the pulse. Shortening fails safe. The long case is the one that matters, and it stays under half a second.

Why this window: the existing software command TTL is 300 ms and is unchanged. It drops a GPIO that the CPU can still write. It does nothing to a GPIO that is stuck high. The hardware window is what releases that stuck pin, and only if edges have stopped. A future image must produce a rising edge at least every 100 ms during a legal RUN, so the short case (264 ms) still covers two intervals, and must produce no edges at all otherwise. The contract is `docs/firmware_heartbeat_contract.md`. The prototype firmware is not modified, and it does not toggle GPIO1, so these coils stay off with that image.

Q is AND-ed with the XOR (`U12`, 74LVC1G08) and that result drives `Q_SERIES`. `R_COILFEED` only joins the ignition contact to the coil high side. It does not bypass `Q_SERIES`. The old fitted 0 Ω `R_BYPASS` is gone.

Startup: the function table triggers on CLR rising only when B is already high. B is held low, so power-up does not fire a pulse. Coils stay off until the first valid rising edge, and even then a direction request has to be high. One glitch on GPIO1 can open a single timeout window. The direction pins are pulled down, so that window does not run a coil by itself.

Loss of 3.3 V: the 74LVC output goes high-Z (IOFF), and the 100 kΩ pulldown on the series-FET gate turns `Q_SERIES` off. The direction gates have their own pulldowns.

## 2. Interlock fault table

The XOR, the cross-clamps, and the heartbeat are three separate mechanisms. A welded contact is a fourth case, and none of the three open it.

| Condition | What this PCB does | Prevented on this PCB? |
| --- | --- | --- |
| Both GPIOs asserted | XOR low, so the AND is low and `Q_SERIES` is off. Each coil gate is also clamped off by the other request | Yes, if either the XOR path or the clamps are intact |
| One GPIO stuck high, main loop still running, no valid RUN | Edges are not produced by the loop. Q falls after one pulse. Writing the stuck pin low does not clear it | The coil drops. A free-running kick would defeat this, and the future firmware is not allowed to do that |
| One GPIO stuck high while a valid RUN for that same direction is still refreshed | That coil runs | This is the commanded direction, not a fault. The opposite coil stays clamped |
| Both GPIOs stuck high | Same as both asserted | Yes, both coils off, same condition as the row above |
| ESP32 reset or boot | Direction requests and GPIO1 are pulled down. Q is low until a rising edge | Coils off. A single boot glitch on GPIO1 opens one window only, and the direction pulldowns still hold the coil FETs off |
| Loss of 3.3 V logic supply | Monostable and gates unpowered. Series-FET gate and both coil gates pulled down | Coil drivers off. Does not open a contact that is already welded |
| Heartbeat stuck high, or stuck low | The monostable runs at most one pulse after the last rising edge, then Q stays low | A static level cannot hold coil power. The current firmware never produces the edge, so the coils stay off |
| Relay contact welded | No auxiliary contact. The switched +12 V node is also high when the hand remote or the Lofrans controller commands that direction | No. A weld runs until the breaker or the existing feed is removed. Detection is not claimed |
| Hand remote or Lofrans controller commands the opposite direction | Those contacts are in parallel and do not pass through this board | No. Both contactors can be asked to run. This is hazard H11 |

This board can keep its own two coils from being driven together, can drop its own coils when the heartbeat stops, when 3.3 V dies, when the CPU resets, and when the switch or the ignition contact is open.

This board cannot open a welded contact, cannot see the other operator, and cannot enforce the 300 ms TTL when the CPU is halted. The hardware timeout covers that last case only after a future image actually toggles GPIO1.

## 3. Reed input

ISO7721D, field side at 3.3 V. From the TI datasheet at that supply: VIH is at least 0.7×VCCI (2.31 V at 3.3 V), VIL is at most 0.3×VCCI (0.99 V), input leakage is ±10 µA. A 10 MΩ pull-down is wrong: 10 µA × 10 MΩ = 100 V, so leakage can cross VIH. That resistor is removed.

The field supply is 3.3 V rather than 5 V because a 5 V rail would put VIH at 3.5 V, and the measured idle of 3.22–3.3 V would not be a reliable high.

`U4` is Murata MEJ2S0503SC, 5 V to 3.3 V, 606 mA. A 51 Ω preload draws about 65 mA, just over 10% of rated current, which is the region the load-regulation figure is specified for. Load regulation for this code is 10% typical and 15% maximum, so the rail can sit near 3.8 V. ISO7721 accepts 2.25 V to 5.5 V. At 3.8 V, VIH is 2.66 V. The idle, after 0.1 V of drop in the 10 kΩ series resistor at 10 µA, is still about 3.1 V if the Lofrans source is stiff.

| Mode | Path | Level at the isolator |
| --- | --- | --- |
| Lofrans, switch throw A | `J_REED` → 10 kΩ → switch → isolator, with one 47 kΩ from the isolator input to `REED_RET` | Idle high. Load is 3.3 V / 47 kΩ = 70 µA. An open wire sits near 0.47 V from 10 µA leakage, below VIL |
| Dry contact, switch throw C | `J_DRY` between `DRY_A` and `REED_RET`. 4.7 kΩ pull-up from `REED_3V3` only on `DRY_A` | Open contact about 3.0 V, above 2.66 V. Closed contact shorts the input to `REED_RET` |
| Switch open or between positions | 47 kΩ on the isolator input only | 10 µA × 47 kΩ = 0.47 V, below VIL. Reads inactive |

The dry-contact pull-up is on `DRY_A` only. In the Lofrans position the switch disconnects it from `J_REED`, so the onboard 3.3 V cannot backfeed the Lofrans signal. Do not fit a Lofrans wire and a dry contact at the same time. Assemble the switch in the Lofrans position unless `J_DRY` is the sensor in use.

The 140 µA figure was two 47 kΩ resistors in parallel. The second one did not improve the leakage fail-safe, so it is removed. The load cannot go below 70 µA on the published ±10 µA leakage: 10 µA in 100 kΩ is 1.0 V, which can sit above VIL when the isolated rail is low. The lighter DC load is offset by a 1 nF capacitor on the isolator input. With the 10 kΩ series resistor that is about 10 µs, against a 30 ms firmware debounce and a minimum isolator hysteresis of 0.1×VCC (0.33 V at 3.3 V).

Field current returns only to `REED_RET`. The MCU pin is powered from +3.3 V and `GND`. ISO7721 without the F suffix drives its output high if the field supply is off. High is idle. The existing firmware counts the rising edge while a direction is sensed, not a level held low, so an open wire sitting low does not run the counter.

Clamps are BAT54W, on the Lofrans node, to `REED_3V3` and to `REED_RET`. A 12 V fault through 10 kΩ is about 0.8 mA into the isolated rail. The 65 mA preload absorbs that. The Lofrans pulse width has not been measured; this filter would only hide a pulse of a few tens of microseconds.

The source impedance of the Lofrans pin is still unmeasured. The boat check remains: idle at `J_REED` must stay near the unloaded 3.22–3.3 V.

## 4. Power supply

`VIN_12` splits before either fuse.

MCU branch, sized for the electronics only:

- Fuse `F_MCU`, Littelfuse 0466002 class, 2 A, 1206. Operating current is about 0.3 A (see below). 2 A is there so the 10 µF input capacitors do not open a smaller fuse. Confirm the tape-and-reel suffix at purchase.
- `D_TVS_MCU`, Littelfuse SMAJ18A, 18 V stand-off, 400 W for a 10/1000 µs pulse, clamp about 29.2 V. This is the short-pulse clamp. It is not load-dump protection.
- `Q_MCU`, Diodes DMP6023LE-13, −60 V, −7 A, SOT-223. Pin 1 gate, pin 2 drain and tab, pin 3 source. Drain is the fused input, source is `+12V_MCU`. `BZT52C12` holds Vgs near −12 V, inside the ±20 V gate rating. At a few hundred milliamps and 28 mΩ, dissipation is a few milliwatts.
- `U20` AP63203WU-7, fixed 3.3 V, and `U21` AP63205WU-7, fixed 5 V. Diodes, 2 A synchronous, VIN 3.8–32 V, TSOT-26. Passives are the datasheet table: 3.9 µH and 4.7 µH, 10 µF input, two 22 µF outputs, 100 nF bootstrap. Inductor saturation must be above the 3.1 A maximum high-side peak current limit. The exact reel is a purchasing choice against that spec, not an electrical unknown.

AP2112K-3.3 is removed. At the module TX peak of 355 mA it would have dropped `(5.0 − 3.3) × 0.355 = 0.60 W` in SOT-23-5.

Buck thermal check, AP63203, θJA = 89 °C/W from the Diodes datasheet. The design load is 500 mA continuous, above the 355 mA TX peak, so the enclosure case is covered with the radio on. Efficiency is taken as 85%. The datasheet quotes up to 88% at 5 mA; the 500 mA point is on the EVM curve and was not read as a single number here, so 85% is the conservative figure used.

```text
Pout = 3.3 V × 0.50 A = 1.65 W
Loss at 85% = 1.65 × (1/0.85 − 1) = 0.29 W
Rise if the entire 0.29 W is in the IC = 0.29 × 89 = 26 °C
Junction at 85 °C ambient ≈ 111 °C, limit 125 °C
```

The inductor takes part of that loss, so the junction is cooler than this. The old linear regulator had no such margin. This is a calculation, not a measurement inside the enclosure. Enclosure air temperature is still open (B6).

Electronics current from 12 V, same 85% assumption: about 160 mA for the 3.3 V rail at 500 mA, plus about 110 mA for the 5 V rail at the isolated-module load below. Together about 0.3 A. `F_MCU` is 2 A. `F_5V` is a separate 2 A anti-surge fuse on the buck side of the MEJ2 primaries, which is the fuse Murata asks for on a 5 V input. The coil fuse is not either of these.

Absolute maximum on the AP6320x input is −0.3 V to 35 V DC, and −0.3 V to 40 V for 400 ms. Recommended operation stops at 32 V. The internal UVLO rises at 3.5 V typical with 440 mV hysteresis. EN is tied to the MCU 12 V rail, so that internal comparator is the lockout. It is not programmed higher: a shared windlass battery can sag, and that sag is unmeasured. Reverse connection turns `Q_MCU` off. The unidirectional SMAJ18A then conducts like a diode and `F_MCU` is what opens.

Coil branch, now sized from the relay coil rather than from the unknown contactor: `F_COIL` 1 A, `Q_COIL` DMP6023LE-13, and another SMAJ18A. One Finder coil is 42 mA. The 7 A FET and the 1 A fuse are the coil-supply parts. `+12V_COIL` then goes through the external switch and the ignition contact. `+12V_MCU` does not.

USB VBUS is a test pad. It does not feed +5 V and does not power the board.

SMAJ18A is not load-dump protection on either branch. Its rating is 400 W for a 10/1000 µs pulse, clamp about 29.2 V. A load-dump pulse is longer and, into a low source impedance, far more energy. The buck's 40 V / 400 ms absolute maximum is a stress rating, not a promise that this TVS will hold a load dump inside it. The source impedance is still B6.

## 5. Isolation

Grounds with no copper between them on this PCB:

```text
GND        battery return, ESP32, bucks, coil-FET sources, USB shield network
+12V_MCU   bucks only
+12V_COIL  switch, ignition, coils only
UP_RET     UP opto only
DN_RET     DOWN opto only
REED_RET   reed isolator, MEJ2S0503 secondary, J_REED and J_DRY
GND_CAN    ISO1042 side 2, MEJ2S0505 secondary, J_NMEA NET-C
NET-S      connector pin 5, no copper net
```

`UP_RET` and `DN_RET` are not tied to each other. `REED_RET` and `GND_CAN` are not tied to each other. Dry contacts `UP_COM`/`UP_NO` and `DN_COM`/`DN_NO` touch no ground.

| Barrier | Part | Rating used for this review | Limit |
| --- | --- | --- | --- |
| CAN transceiver | TI ISO1042BDWR, DW-16 | 5000 Vrms for 1 minute, basic isolation | One-minute hipot, not a continuous working voltage |
| CAN supply | Murata MEJ2S0505SC | Production hipot 5.2 kVDC for 1 second. Murata states a continuous barrier withstand of 2.4 kVDC, and that this is functional isolation, not a safety barrier | Continuous claim stops at 2.4 kVDC |
| Reed supply | Murata MEJ2S0503SC | Same family, same hipot and the same 2.4 kVDC continuous statement | Same limit. Secondary is `REED_RET`, not `GND_CAN` |
| PCB creepage | Isolation rectangles are drawn on the 80 × 60 mm placement. Copper is not routed, so the distance is not yet a board measurement | Murata's certified creepage and clearance for the 200 Vrms working voltage is 2 mm, at up to 4000 m. Isolation capacitance is 4 pF typical. Isolation resistance is 1 GΩ typical at 500 VDC | The 2 mm figure is not a 2.4 kV board design. The drawn keep-out is the full 7.62 mm pin gap |

Application check, both modules, input from AP63205 at 4.95–5.05 V. The 5 V-input absolute maximum is 7 V, so normal regulation is inside it. A buck that fails short and puts 12 V on this rail is not inside it, and nothing on the board clamps that fault. MEJ2S0505SC is 400 mA; the CAN load with its 120 Ω preload is about 115 mA. MEJ2S0503SC is 606 mA; the 51 Ω preload is about 65 mA, just over 10 percent. The two secondaries are not joined.

The complete barrier is the weaker of those numbers and the copper that is not yet laid out. It is not 5 kVrms. Murata’s sales policy also lists ships among the uses that need prior written approval, and the datasheet says the series is functional isolation when it is not used as a safety barrier. This prototype does not claim that approval and does not claim marine certification. Repeated hipot testing is discouraged by Murata and is not part of this design.

A 120 Ω resistor on the CAN secondary is a preload so the module stays inside its regulation window (about 42 mA, just over 10% of 400 mA). It is not a bus terminator. No 120 Ω is fitted on CANH/CANL. Load regulation of MEJ2S0505SC is 10% maximum, so the secondary can sit on 5.5 V, which is the top of the ISO1042 VCC2 range (4.5–5.5 V). Measure `ISO_5V` on the first board before trusting the transceiver.

Publish remains the open jumper. Open jumper removes primary power from `U9`. ISO1042 bus pins are high-impedance when unpowered. NET-S stays no-connect. `Q91` is DMP3099L (−30 V, −3.8 A) used at 5 V. The MEJ2S0505 primary at full rated load is 503 mA typical.

JLCPCB stock of the genuine Murata modules was not confirmed. A reseller listing with a similar name is not accepted as this part.

## 6. What is selected, and what is still blocked

Selected from manufacturer datasheets, without a Lofrans current measurement:

| Function | Part |
| --- | --- |
| Module | ESP32-S3-WROOM-1-N16 (LCSC C2913199, stock snapshot 2026-11-18) |
| 3.3 V and 5 V | AP63203WU-7, AP63205WU-7, with the datasheet L and C values |
| MCU reverse protection | DMP6023LE-13, BZT52C12, SMAJ18A, 2 A 1206 fuse |
| Heartbeat and interlock | 74LVC1G123, 74LVC1G08, 74LVC1G86, 2N7002 gate clamps |
| Relay and coil drive | Finder 40.31.7.012.0000, NX6008NBK, SS14, 1 A coil fuse, DMP6023LE, SMAJ18A. Through-hole relay, hand-fitted |
| Reed | ISO7721DR (8-pin D package), MEJ2S0503SC, BAT54W clamps, SPDT mode switch |
| Direction sense | TLP291, one channel each, returns not joined. Series resistor still open |
| CAN | ISO1042BDWR (LCSC C2671499 snapshot), MEJ2S0505SC, DMP3099L publish switch |

### Relay contact and coil

The board switches +12 V into the existing Lofrans UP and DOWN control circuits. It does not switch the windlass motor. Each onboard contact is the normally-open throw of a Finder 40.31, in parallel with the existing Lofrans and wired hand controls. The normally-closed pin is open. Unplugging this board leaves those original controls connected to each other.

Finder series datasheet (Farnell 2790229, the 40.31 column and the coil-code table):

| Figure | Value used |
| --- | --- |
| Order code | 40.31.7.012.0000, coil code 7.012 |
| Coil | 12 V, code 7.012. Table: 288 Ω, 42 mA at UN (12 × 42 mA = 0.50 W). The table heading calls this the 0.65 W standard coil |
| Pickup / maximum | 8.8 V / 18 V |
| Operate / release | 7 ms / 3 ms |
| Contact, DC1 | 10 A at 30 V DC, resistive breaking capacity in that table |
| Contact, AC15 | 500 VA at 230 V AC. This is an AC inductive figure. It is not a 12 V DC inductive rating |
| DC13 | Finder says a diode across the load gives electrical life similar to DC1, and that the load then releases more slowly |

The design contact rating is that DC1 number: **10 A at 30 V DC, resistive**. Nominal 12 V is below 30 V, so the published current is the ceiling used here. The control circuit is not assumed to be resistive, and it is not assumed to already have a flyback diode. **Installation is not allowed until the actual control-circuit current and inductive energy are measured and shown to be inside this rating.** No Lofrans current was invented to fill that gap.

The relay is through-hole and is hand-fitted. It is not treated as a JLCPCB-assembled SMT part. A smaller Omron G5Q and a Hongfa HF46F were checked for the 80 × 60 mm outline. Both were left off the schematic: their published DC current figures are resistive, and the HF46F R300 listing is a 250 V DC pilot-duty rating of about 0.22 A, not a 12 V inductive rating. See `docs/mechanical_plan.md`.

Coil-path parts that were open are now:

| Part | Selection | Why |
| --- | --- | --- |
| Q_UP, Q_DN, Q_SERIES | Nexperia NX6008NBK | 60 V. RDS(on) maximum 3 Ω at VGS = 2.5 V. Two FETs drop about 0.25 V at 42 mA, so the coil still sees about 11.7 V, above 8.8 V. Gate absolute maximum is ±8 V, and the gate is driven from 3.3 V. Drain rating sits above the SMAJ18A clamp of about 29.2 V |
| D60, D70 | SS14 | 1 A, 40 V, across each coil. This protects the driver. It is not a diode across the Lofrans load |
| F_COIL | Littelfuse 0466001, 1 A | One coil is 42 mA. Both together, if the interlock failed, are 84 mA |
| Q_COIL | DMP6023LE-13 | −60 V, −7 A, same part as the MCU branch, at 42 mA |
| D_TVS_COIL | SMAJ18A | Stand-off 18 V matches the coil maximum operating voltage. Same short-pulse clamp as the MCU branch. Not load-dump protection |

Still blocked. These are not given invented values:

- Measured Lofrans control current and inductive energy, against the 10 A / 30 V DC1 rating above. The coil parts are no longer open. The contact application is.
- Direction-sense resistor `R_IN`. LED current must stay far below contactor pull-in. That rating is not measured.
- Lofrans reed source impedance, and the reed pulse width. The DC load is now 70 µA with a 1 nF filter. The boat idle check is not done.
- Load-dump source impedance. SMAJ18A’s 400 W pulse is cited. Coordination with the alternator is not.
- PCB creepage as a routed copper distance. Placement is drawn at 80 × 60 mm (`docs/mechanical_plan.md`). The isolation rectangles are not yet copper keep-outs.
- JLCPCB stock of MEJ2S0505SC, MEJ2S0503SC, DMP6023LE-13, and AP63205WU-7 at order time. The earlier AP63203 snapshot (C780769) is a snapshot, not a reservation.
- Enclosure air temperature, antenna clearance, and which battery feed this board sees (B6).
- Ignition contact location and current (B2).
- Direction-wire identity: the prototype README and `main.cpp` still disagree. This sheet follows the code’s active-low sense into new GPIO numbers. It does not change the DevKit image.

## 7. Verification record

```text
python scripts\build_schematic.py
python scripts\count_labels.py
kicad-cli sch erc --severity-all --exit-code-violations -o docs\erc_report.txt kicad\windlass.kicad_sch
```

ERC on 2026-11-19: `Found 0 violations` (0 errors, 0 warnings) in `docs/erc_report.txt`. Every global label is used at least twice. KiCad’s default profile still ignores “global label only once”, “four connection points joined”, SPICE, and footprint-filter mismatch. That result is a connectivity check. It is not approval to install or to fabricate.

Revision on the sheets is `0.2-not-for-fabrication`.

## 8. Compact placement

The preferred 80 × 60 mm outline is met with the selected Finder relays. A 90 × 60 mm arrangement of the same parts also clears its courtyards and is not used, because the extra width is spare connector margin. KiCad DRC on 19 November 2026 reported no courtyard overlaps on either board. The only errors are twelve 0.2 mm drills inside the ESP32-S3-WROOM-1 footprint, against the default 0.3 mm minimum hole. Details, the antenna keep-out, the isolation rectangles and the connector positions are in `docs/mechanical_plan.md`.

No copper was routed. This section is not a fabrication release.
