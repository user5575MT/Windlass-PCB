# Installation protection

23 November 2026, Sydney time. This is the permanent-installation revision of the two bench restrictions. It starts from `kicad11/windlass_bench.kicad_pcb`, which was not edited. The board that matches the schematic is `kicad11/windlass_install.kicad_pcb`. The parts list is `docs/integrated_bom.md`.

No firmware was edited. No Gerber was written. No part was ordered. Nothing was flashed. The title block says not for fabrication. A clean DRC is the connectivity check. It is not approval to install the board on the boat.

ERC at 3:32 pm Sydney time (`kicad11/erc_install.rpt`): 0 errors, 1 warning. The warning is U5 pin 4 `GND1` on `REED_RET`, and it is intentional. DRC at 3:41 pm Sydney time (`kicad11/drc_install.rpt`), after a zone refill: 0 violations, 0 unconnected pads. `REED_RET`, `UP_RET`, `DN_RET`, `GND_CAN`, `ISO_5V`, `CAN_H`, `CAN_L`, and the other isolated-side nets still have no vias and no inner-layer copper. `UP_COM` is not tied to `DN_COM`. Each contact net connects only its relay pin to its connector pin.

The series FET, the two cross-clamps, the 74LVC1G123 heartbeat, and the external switch and ignition in the coil feed are unchanged. The prototype image still does not edge GPIO1, so a board loaded with that image keeps both coils off.

## Coil drivers

The NX6008NBK could not survive the fault it was supposed to clear. Its continuous rating is 270 mA at 4.5 V and 25 °C, and its 1 A pulsed rating is only for 10 µs. A shorted coil lead at 12 V, through the roughly 5.6 Ω of two of those FETs, is about 2 A. That exceeds the pulse rating long before a 1 A fuse opens. A larger plain MOSFET was not a fix: the parts with a multi-amp pulse rating do not guarantee RDS(on) at 3.3 V, and a FET sitting in its linear region is not protected by a fuse that takes seconds to open. No drain-source TVS was added. A TVS that fails short would hold the coil on.

`Q_UP`, `Q_DN`, and `Q_SERIES` are Diodes ZXMS6004FFTA, DS33609 Rev. 8-2, November 2020. The package is SOT23F, marking 1K6. Pin 1 is drain, pin 2 is IN, pin 3 is source. The pitch matches SOT-23, and the coil current is 42 mA, so the existing SOT-23 land was kept. The SOT-223 ZXMS6004DG was not used.

From that datasheet, at the 3 V input used here:

| Item | Figure |
| --- | --- |
| On threshold, VIH | 3.0 V minimum |
| Off threshold, VIL | 0.7 V maximum |
| Input current at 3 V | 100 µA maximum |
| RDS(on) at 3 V, 0.5 A | 600 mΩ maximum |
| Current limit at 3 V | 0.7 A minimum, 1.7 A typical |
| Short-circuit drain voltage, VDS(SC) | 36 V |
| Drain clamp, VDS(AZ), at 10 mA | 60 V minimum, 65 V typical, 70 V maximum |
| Single-pulse energy, EAS | 90 mJ at 0.5 A, 24 V, 25 °C |
| Thermal trip | 150 °C minimum, 175 °C typical, about 10 °C hysteresis, then auto-restart |

The current limit applies only in saturation. At the 42 mA coil current the switch stays fully on. Note 8 in the datasheet says the part is not designed to sit in thermal shutdown for a long time. The fuse is what ends that condition.

`R60` and `R70` are 1 kΩ, with the existing 100 kΩ pulldown on the switch input. At the 3.0 V threshold the pulldown takes 30 µA, so the resistor carries 130 µA and drops 0.13 V. The GPIO has to be at least 3.13 V. The AP63203 output in CCM is 3.27 V minimum and 3.33 V maximum, which leaves 0.14 V for the pin. The ESP32-S3 VOH minimum of 0.8×VDD is the high-current test and was not used as the voltage at 130 µA. The series-FET gate resistor stays 100 Ω, a 10 mV drop at 100 µA. The opposite request still clamps the input off: 3.3 V across 1 kΩ is 3.3 mA, and even 100 Ω in the 2N7002 leaves about 0.30 V, under the 0.7 V off threshold.

## Coil fuse

`F_COIL` is Littelfuse 0466.250, a 250 mA, 125 V, very-fast 1206 fuse. The current product table gives a cold resistance of 0.691 Ω, measured at 10% of rated current, and a nominal melting I²t of 0.0022 A²s. Orderable reels are 0466.250NR and the halogen-free 0466.250NRHF. The series is specified as secondary protection of portable equipment. It is not a marine safety fuse, and it is not the contactor fuse.

The 466 series characteristic table, at 25 °C, holds 100% for 4 hours minimum, opens 200% within 5 seconds, and opens 300% within 0.2 seconds. The temperature-rerating note is in addition to the usual 25% continuous derating. Littelfuse’s own 70 °C example is I = 0.75 × 0.80 × Irated, so 150 mA. The curve is described as nominal.

Finder 40.31.7.012.0000 coil: 288 Ω, 42 mA at 12 V, pickup 8.8 V, maximum operating voltage 18 V. At 18 V one coil is 62.5 mA. Both coils, if the interlock has already failed, are 125 mA, which is still under the 150 mA 70 °C hold. One coil at 42 mA is 28% of that hold. The fuse drop at 42 mA is 29 mV. Two switches at 600 mΩ drop another 50 mV. The coil still sees about 11.92 V against an 8.8 V pickup.

A shorted coil lead puts the switches into current limit at 0.7 A minimum. That is 280% of the fuse rating, above the 200% point and below the 300% point. The opening time is not interpolated between 5 seconds and 0.2 seconds. The fuse is carrying more than the current whose maximum opening time is 5 seconds, and it stays open, so the thermal restart ends. While the coil is shorted it has no voltage across it and cannot pull in.

A 200 mA fuse was not used. Its 70 °C hold, on the same example, is 120 mA, which is below both coils at 18 V.

## What a coil-lead fault does not cover

A copper short from `UP_LOW` or `DN_LOW` to GND bypasses both low-side switches. The coil then draws its normal 42 mA whenever the external switch and the ignition are closed. The fuse cannot tell that from a commanded coil. Moving the heartbeat to a high-side switch was not done: the level shifter that would drive it can fail in the on direction and defeat the watchdog.

Two switches failing short, with the external switch and the ignition closed, still energises that coil at 42 mA. The fuse does not open on coil current. During a commanded direction, a shorted opposite low-side switch can still run the other coil, because `Q_SERIES` is on. That is the existing interlock, and it was left as it is. A welded Finder contact is still not opened by this board. The boat breaker is that clearing action.

`D60` and `D70` stay the SS14 flyback diodes. If one fails short, that coil is shorted, the 250 mA fuse opens, and the coil cannot pull in. If one fails open, the ZXMS clamp is the backup. Finder does not publish the coil inductance. A 50 ms time constant on 288 Ω is 14.4 H and about 13 mJ at 42 mA, against the 90 mJ single-pulse rating. A more typical relay time constant of 5 to 15 ms is about 1 to 4 mJ. The 50 ms figure is a bound, not a measured inductance. The SMAJ18A clamp on the coil rail is still about 29.2 V. That is under the 36 V short-circuit rating and under the 60 V clamp, and it is still not load-dump protection.

## Dry contacts

`D61` and `D71` are removed. No PCB component sits across COM and NO, so no PCB component can fail in a way that bridges that pair and energises the windlass. The two contacts stay independent.

A fuse in series with the contact does not fix a shorted suppressor. The fault current is the contactor coil current, which any control fuse has to carry, and the contactor is energised until the fuse opens. An RC snubber was not fitted. Quick does not publish the pull-in current, so a shorted capacitor plus the resistor cannot be shown to stay below pull-in.

The diode belongs at each contactor, cathode to the switched positive and anode to the coil return. Specify a 3 A, 400 V diode such as a 1N5404. Three amps is above Quick’s 2.5 A fast control fuse, which stays in the boat’s existing control wiring and is not a PCB part. A shorted diode shorts the coil, that fuse opens, and the contactor drops out. A diode that fails open loses the suppression and wears the contact. It does not bridge COM to NO.

Finder’s DC13 life equals the DC1 rating, 10 A at 30 V DC resistive, when a diode is fitted across the load. Quick does not publish the T6315-12 or T6415-12 coil current. It does specify the 2.5 A fuse as the control fuse for that coil, so the coil current is a current that fuse is meant to carry. That is inside 10 A. The contact copper stays 1.2 mm. IPC-2221 for an external 1 oz trace at a 10 °C rise is about 1.07 mm at 2.5 A. This PCB does not supply the contactor coils.

## Still a measurement

These are not closed by a datasheet:

- The installed contactor has to be confirmed as a Quick T6315-12 or T6415-12. If it is not, the coil current is unknown and the 10 A comparison above does not apply.
- Whether a parallel contact feeds the hand remote or the Lofrans box. That is the boat wiring, and it is not in the Quick sheet.
- Where the ignition permissive sits, and whether it must stay in series (B2).
- The Lofrans reed, on the boat, with this input connected (B4).
- The sense-wire voltage, return, and which conductor is UP (B5).
- Whether this 12 V feed can be load-dumped, and the enclosure and antenna clearance (B6). The SMAJ18A and the 36 V short-circuit rating do not close that.
- The Q pulse with the fitted `C50`, and a reviewed image that edges GPIO1, before any coil is tested (B7).
- The NMEA drop, the backbone terminations, and which device publishes (B8).

Separate from the boat, and unchanged by this revision: `C30I` effective capacitance at 12 V, `ISO_5V` at the preload, the USB4105 note, and the MEJ2 pin-1 dimension.
