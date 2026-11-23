# Circuit calculations

The integrated board in `kicad11/` has superseded this page. The schematic and `docs/integrated_bom.md` are the parts list. This page still describes the XOR, a second buck (AP63205), and coil FETs called `NMOS_COIL_OPEN`. None of those are on the integrated schematic. The coil FETs are NX6008NBK. L20 is Bourns SRN6045-3R3Y. U9 is MEJ2S0305SC from 3.3 V. The text below is the revision 0.2 record.

Rev 0.2. Figures below are the ones used on the schematic of that revision. Anything marked OPEN is not a fabrication value. KiCad ERC does not check these numbers. The watchdog, reed thresholds, buck thermal check, and isolation ratings are written out in `design_review.md`.

## Direction-sense LED current — OPEN

For each TLP291 channel:

```text
I_F = (V_field - V_F) / R_IN
```

`R_IN` is `R_IN_OPEN` on the schematic (`R30`, `R40`). `V_F` for TLP291 is about 1.2 V at a few milliamps (Toshiba datasheet; confirm at the chosen current). `V_field` is the switched +12 V, which sags under contactor load and is not yet measured.

Rule before a value is filled in: `I_F` must be well below the contactor pull-in current and inside the Lofrans source rating. A sense current that can pull in the contactor is a backfeed fault. No number is assigned until that rating is known.

Filter: `C30` / `C40` are 100 nF across the LED. Time constant `R_IN * 100 nF` is OPEN with `R_IN`. The existing firmware debounce is 30 ms, so the analog delay only has to stay well under that.

Anti-parallel diode: 1N4148-class, across the LED only. It does not carry contactor current.

## Reed loading

ISO7721 leakage is ±10 µA. A pull-down must keep that current below VIL (0.3×VCCI, 0.99 V at 3.3 V).

```text
10 µA × 47 kΩ = 0.47 V     below VIL
10 µA × 10 MΩ = 100 V      the rev 0.1 value, removed
```

Lofrans position uses one 47 kΩ, on the isolator input only. A second 47 kΩ in parallel would raise the load to 140 µA without improving the leakage fail-safe, so it is not fitted.

```text
I_idle ≈ 3.3 V / 47 kΩ = 70 µA
10 µA × 47 kΩ = 0.47 V     below VIL
10 µA × 100 kΩ = 1.0 V     can cross VIL, so 47 kΩ is the highest safe pull-down
```

The previous PC817 input pulled the idle from 3.22 V to 1.5 V. 70 µA is still orders of magnitude below that LED current. Source resistance was not measured, so idle at `J_REED` must still be checked on the boat.

Fault current if 12 V is forced onto the reed pin and the clamp holds the node near 3.6 V:

```text
I_fault ≈ (12 - 3.6) / 10e3 = 0.84 mA
```

The 10 kΩ is the fault limiter. The isolated rail’s 51 Ω preload is about 65 mA, so it absorbs this. Dry-contact pull-up is 4.7 kΩ and is disconnected from `J_REED` in the Lofrans position.

Filter: 1 nF on the isolator input. With the 10 kΩ series resistor, τ ≈ 10 µs, against a 30 ms firmware debounce. The larger capacitor offsets the higher impedance of the single 47 kΩ. Chain length is not a resistor. The firmware default remains `mmPerTurn = 360` (0.36 m) when NVS is empty.

## Coil-rail presence detector

`R80` and `R81` are 100 kΩ from `COIL_12` to GND. The midpoint is clamped to +3.3 V by `D80`.

```text
I_clamp(12 V) ≈ (12 - 3.6) / 100e3 = 84 µA
I_clamp(40 V) ≈ (40 - 3.6) / 100e3 = 0.36 mA
```

`R82` is 1 kΩ between the clamp node and GPIO14. This detects "coil rail present". It is not a calibrated voltmeter. Threshold in firmware is a normal 3.3 V CMOS high/low.

## GPIO mutual exclusion

Not a power calculation. For the record of the logic:

| UP_REQ | DN_REQ | XOR (74LVC1G86) | Q_SERIES | UP gate | DN gate | Coils |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | off | pulled down | pulled down | both off |
| 1 | 0 | 1 | on | driven | clamped off by UP_REQ | UP only |
| 0 | 1 | 1 | on | clamped off by DN_REQ | driven | DOWN only |
| 1 | 1 | 0 | off | clamped off | clamped off | both off |

The table above is the XOR alone. `Q_SERIES` is that XOR AND the 74LVC1G123 output, so a row that says “on” is on only while the heartbeat is fresh. A single stuck request can still energise that one coil while edges continue. A static high or low on GPIO1 cannot. Typical timeout is 330 ms. See `design_review.md`. The 300 ms firmware TTL is unchanged and is a different mechanism.

Gate clamps are 2N7002. The current they switch is the 10 kΩ pull-up from a 3.3 V GPIO, about 0.33 mA. That is inside a 2N7002. The coil FETs are `NMOS_COIL_OPEN` because the coil current is not known.

## 3.3 V and 5 V bucks

AP2112K-3.3 is not fitted. At 355 mA it would have dissipated `(5.0 − 3.3) × 0.355 = 0.60 W` in SOT-23-5.

`U20` is AP63203WU-7 and `U21` is AP63205WU-7, both from the 12 V MCU branch. Datasheet: `https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf`. θJA for TSOT-26 is 89 °C/W. Passives are the datasheet table (3.9 µH / 4.7 µH, 10 µF, 2×22 µF, 100 nF bootstrap).

At a continuous 500 mA on 3.3 V, taking efficiency as 85% and assigning every watt of loss to the IC:

```text
Loss = 1.65 W × (1/0.85 − 1) = 0.29 W
Rise = 0.29 × 89 = 26 °C
Junction at 85 °C ambient ≈ 111 °C, limit 125 °C
```

The inductor shares that loss. This is a calculation, not an enclosure measurement. USB VBUS is not diode-ORed into either rail.

## ESP32 reset and USB

From the ESP32-S3-WROOM-1 datasheet text: EN delay is usually 10 kΩ and 1 µF. Those are `R10` and `C10`. GPIO0 pull-up is 10 kΩ (`R11`). GPIO3 pull-down is 10 kΩ (`R12`) because that pin has no internal resistor.

USB-C CC1 and CC2 are 5.1 kΩ to GND (`R15`, `R16`), the Type-C Rd value for a device port. Series 22 Ω on D+ and D− (`R17`, `R18`) are preliminary full-speed series resistors, not a safety rating.

## Isolated CAN supply

`U9` is Murata MEJ2S0505SC, 5 V to 5 V, 400 mA, efficiency 75% typical. Production hipot is 5.2 kVDC for 1 second. Murata’s continuous functional rating is 2.4 kVDC, which is the number this review uses, not the ISO1042 5000 Vrms one-minute test. PCB creepage is not drawn.

ISO1042 dominant bus current is about 43–73 mA at `RL = 60 Ω`. A 120 Ω preload on the secondary draws about 42 mA so the module stays above 10% load. That resistor is not on CANH/CANL. No bus terminator is fitted.

100 nF on VCC1 and on VCC2 follows TI isolated-CAN reference slla298. Shield capacitor `C92` is 100 nF to `GND_CAN`. Its working voltage has to survive the barrier test and is still a purchasing rating, not a laid-out creepage.

## Relay coil path

Finder 40.31, coil code 7.012, from the series coil table: 288 Ω, 42 mA at 12 V, operating range 8.8 V to 18 V, operate/release 7 ms / 3 ms.

```text
I_coil = 12 V / 288 Ω = 42 mA
Two FETs at 3 Ω max each: drop = 2 × 0.042 × 3 = 0.25 V
Coil voltage at 12 V ≈ 11.7 V, above the 8.8 V pickup
```

`F_COIL` is 1 A, about 20 times one coil and about 12 times both coils. The interlock allows only one coil. `NX6008NBK` is 60 V and 270 mA at 25 °C on the stated pad, against 42 mA. `SS14` is 1 A / 40 V across each coil. `Q_COIL` is DMP6023LE, 60 V / 7 A, at 42 mA. `SMAJ18A` on this branch matches the coil's 18 V maximum operating voltage as a stand-off. Its 29.2 V clamp is inside the 60 V FETs. It is not load-dump protection, and it does not make 10 A a safe inductive contact current.

## Parts still not closed

| Item | Why |
| --- | --- |
| Load-dump energy | SMAJ18A is 400 W, 10/1000 µs. Source impedance is unknown. |
| Lofrans control current and inductive energy | Contact design limit is DC1, 10 A at 30 V. DC13 is not that number unless the load has its own diode. |
| Inductor reel | Value and Isat floor are set (above 3.1 A). The exact MPN is a purchase against that spec. |
| C92 voltage rating | Has to survive the barrier. Creepage is a layout item. |
| R30, R40 | See the LED-current rule above. |
