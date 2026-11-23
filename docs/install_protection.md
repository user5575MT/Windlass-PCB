# Installation protection

23 November 2026, Sydney time. This is the permanent-installation revision of the two bench restrictions. It starts from `kicad11/windlass_bench.kicad_pcb`, which was not edited. The board that matches the schematic is `kicad11/windlass_install.kicad_pcb`. The parts list is `docs/integrated_bom.md`.

No firmware was edited. No Gerber was written. No part was ordered. Nothing was flashed. The title block says not for fabrication. A clean DRC is the connectivity check. It is not approval to install the board on the boat.

ERC at 3:32 pm Sydney time (`kicad11/erc_install.rpt`): 0 errors, 1 warning. The warning is U5 pin 4 `GND1` on `REED_RET`, and it is intentional. DRC at 3:41 pm Sydney time (`kicad11/drc_install.rpt`), after a zone refill: 0 violations, 0 unconnected pads. `REED_RET`, `UP_RET`, `DN_RET`, `GND_CAN`, `ISO_5V`, `CAN_H`, `CAN_L`, and the other isolated-side nets still have no vias and no inner-layer copper. `UP_COM` is not tied to `DN_COM`. Each contact net connects only its relay pin to its connector pin.

The series FET, the two cross-clamps, the 74LVC1G123 heartbeat, and the external switch and ignition in the coil feed are unchanged. The prototype image still does not edge GPIO1, so a board loaded with that image keeps both coils off.

This review did not edit the schematic, the PCB, or the firmware.

## Relay and contactor review

23 November 2026, Sydney time. Three checks against the published sheets. The board files were left as they are. The text block on the relay sheet still says the 1 kΩ holds the input above 3.0 V, and that DC1 is 10 A at 30 V. Those two sentences are superseded by this section.

### 1. Relay-driver voltage margin — fail

The direction inputs do not have a datasheet guarantee of the ZXMS on-level. `R60` and `R70` are not the cause, and changing their value does not repair it.

`UP_REQ` is GPIO9 and `DN_REQ` is GPIO10. Each pin drives its 1 kΩ resistor and the opposite 2N7002BK clamp gate. `R61` and `R71`, 100 kΩ, sit on the switch side of the 1 kΩ. `Q_SERIES` is a separate path: 74LVC1G123 Q through `R50`, 100 Ω.

Diodes ZXMS6004FF, DS33609 Rev. 8-2, November 2020. Recommended VIH for the MOSFET to be on is 3.0 V to 5.5 V. VIL for off is 0 V to 0.7 V. Input current at VIN = +3 V is 60 µA typical and 100 µA maximum, and at +5 V it is 120 µA typical and 200 µA maximum. Those electrical characteristics are at TA = +25 °C. The datasheet does not publish an input-current maximum over the −40 °C to +125 °C ambient range. The 220 µA figure is the input current while overtemperature protection is active, at VIN = +5 V, and it is not the normal on-state current. RDS(on) and the current limit are specified at VIN = 3 V and at 5 V. Between the 1.5 V threshold maximum and 3.0 V the part is not specified as fully on.

Espressif ESP32-S3-WROOM-1, Table 6-3, DC characteristics at 3.3 V and 25 °C. VOH minimum is 0.8 × VDD. Note 2 says VOH and VOL are measured using a high-impedance load. The 40 mA source current on the next line is typical, at VDD = 3.3 V, VOH still at least 2.64 V, and PAD_DRIVER = 3. It is not a guaranteed minimum current, and it does not raise the VOH floor. The table itself is 25 °C only.

Diodes AP63203. The fixed 3.3 V feedback in CCM is 3.27 V minimum, 3.30 V typical, 3.33 V maximum. The datasheet says those min and max limits apply from −40 °C to +85 °C and from 3.8 V to 32 V input. PFM at light load sits above that, so the minimum is the CCM figure.

At that 3.27 V rail the published GPIO floor is 0.8 × 3.27 = 2.616 V. That is 0.384 V below the 3.0 V on-level, with the series resistor at 0 Ω. No value of `R60` or `R70` can close a gap that is already there at the pin.

The resistor drop, taken on its own, is small. With the pin at the 3.27 V rail, IIN at its 100 µA maximum, and the 100 kΩ pulldown included:

Vin = (Vs − Rs × IIN) / (1 + Rs / Rp)

Rs at 1 kΩ +1% and +100 ppm/°C over 60 °C is 1016 Ω. Rp at −1% is 99 kΩ.

Vin = (3.27 − 0.1016) / (1 + 1016 / 99000) = 3.136 V.

That is 136 mV above 3.0 V. At ±5% the same sum is 3.131 V. Input current would have to reach about 235 µA, more than double the published 100 µA, before this 1 kΩ path fell to 3.0 V with the pin held at the rail. The 1 kΩ is adequate for the current the ZXMS datasheet publishes. It cannot make up for an output that the ESP32 datasheet only guarantees at 2.616 V.

`Q_SERIES` does meet the on-level. Nexperia 74LVC1G123, Rev. 8, 14 August 2023: VOH minimum is VCC − 0.1 V at IO = −100 µA, for −40 °C to +125 °C. On the 3.27 V rail that is 3.17 V at the pin while it sources 100 µA. The 100 kΩ on the switch input takes about 32 µA at 3.15 V, so the pin current is about 132 µA. The 0.1 V specification allows up to 1 kΩ of output resistance, and the extra 32 µA on that resistance is another 32 mV, so the pin is about 3.14 V before `R50`. Through 100 Ω +1% the switch input is about 3.13 V. Margin against 3.0 V is about 130 mV at the published input current.

The cross-clamp has the same GPIO limit. Nexperia 2N7002BK specifies RDS(on) at 2 Ω maximum for VGS = 5 V and 1.6 Ω maximum for VGS = 10 V, both at 25 °C. It does not specify RDS(on) at 3.3 V. VGS(th) maximum is 2.1 V. With the GPIO at the 3.27 V rail, the clamp voltage stays under the 0.7 V off-level for a clamp resistance up to about 260 Ω, because 3.27 × 260 / (260 + 990) is 0.68 V. The 5 V maximum of 2 Ω is far under that. With only the published 2.616 V high, the gate is 0.52 V above the 2.1 V threshold maximum, and no RDS figure covers that. The off-state of the opposite direction is therefore not guaranteed from the two datasheets either.

Correction, required before a coil is energised from this board, and not drawn in this review: buffer GPIO9 and GPIO10 with a 74LVC1G gate powered from +3V3, so the buffered net is what `R60`, `R70`, and the two clamp gates already share, and change `R60` and `R70` from 1 kΩ to 100 Ω. Keeping 1 kΩ behind that buffer does not pass. The buffer drop, scaled from VCC − 0.1 V at 100 µA to about 140 µA, is 0.14 V, so the source is 3.13 V. Through 1 kΩ +1% the pin is (3.13 − 0.102) / 1.010 = 3.00 V, with nothing left. Through 100 Ω +1% it is (3.13 − 0.010) / 1.001 = 3.12 V, about 120 mV above 3.0 V. A ±5% 100 Ω resistor changes that by about a millivolt.

### 2. Finder contact against the Quick coil — pass, on the published bound

The contact can carry the control current Quick’s own fuse is specified for, both with a freewheeling diode and on Finder’s no-diode approximation. Quick does not publish the coil current, so that fuse is the bound.

Finder 40 series, S40EN, contact specification for the 40.31 column. Breaking capacity DC1 is 12 A at 24 V, 0.6 A at 110 V, and 0.25 A at 220 V. Rated current is 12 A. Minimum switching load is 300 mW (5 V / 5 mA). Contact material is AgNi. Ambient is −40 °C to +85 °C. Open-contact dielectric strength is 1000 V AC. Curve H 40.1 says a resistive load under the curve can be expected to give at least 100 × 10³ operations, and that a diode in parallel with a DC13 load permits a similar electrical life to a DC1 load. The same note says the release time of the load increases.

Finder general technical information, TecEN. DC13 is an inductive DC load: contactor coils, valves, electromagnets. It assumes no inrush current, and the switch-off voltage can be up to 15 times the rated voltage. A DC inductive load with a 40 ms L/R time constant is approximated as 50% of the DC1 rating. A freewheeling diode in parallel with the load is taken as the same value as DC1.

At 12 V the DC1 current is the 12 A contact rating: the 24 V breaking capacity is already 12 A, and the rated current does not go higher at a lower voltage. Half of that, for the no-diode approximation, is 6 A. A charging 12 V system stays under the 24 V point on that table.

Quick contactor units, manual Rev 002A. T6315-12 and T6415-12 have a 12 Vdc coil and a recommended control fuse of 2.5 A fast. The 24 V models use 1.6 A fast. The 800 A interruption capacity, with the 5 ms time constant in note (1), is the motor contact at 48 Vdc. This PCB does not switch that contact and does not feed the coils. The manual does not publish coil current, coil resistance, inductance, inrush, or an economizer. A plain DC coil current rises to V/R and does not overshoot it, so the “no inrush” assumption in the DC13 paragraph holds for a coil of that kind. The current that a 2.5 A fast fuse is the recommended protection for sits under 2.5 A in normal use. 2.5 A is under 6 A and under 12 A.

The minimum load is not a separate miss. 300 mW at 12 V is 25 mA. The control circuit that Quick protects with a 2.5 A fuse is not a 25 mA dry circuit. The milliamp value itself is still unpublished.

The older “10 A at 30 V” figure in the earlier notes is not the breaking-capacity row on the current S40EN sheet. The comparison above uses 12 A at 24 V.

### 3. Contactor suppression — pass, after one inspection

The Quick manual does not describe built-in coil suppression. An external 1N5404 across each coil is the arrangement Finder uses for DC13 life equal to DC1. It is not required to stay inside the 6 A no-diode approximation. It does not, by its failure modes, start the windlass.

Rev 002A was read in full, in the Italian, English, French, German, and Spanish text. The coil section gives rated voltage and the recommended fuse. The connection diagrams show the push buttons, the control fuse, and the battery. No sentence and no diagram label describes a diode, a varistor, or a suppressor across the coil. That silence does not prove a particular installed unit has an empty coil housing.

Vishay 1N5404, document 88516. Average forward current 3.0 A at a lead temperature of 105 °C, repetitive peak reverse voltage 400 V, forward voltage 1.2 V maximum at 3 A. Freewheeling is one of the listed uses. Three amps is above the 2.5 A fuse. The 400 V rating is the reverse voltage while the coil is energised, and a 12 V coil is far under it. Standard recovery is the right speed for a contactor.

Fit one diode per coil, at the contactor, only after looking at that contactor. Cathode to the coil terminal that is positive while the coil is energised, anode to the coil return. The manual diagrams do not print which terminal is positive, so that polarity comes from the installed wiring. If a suppressor is already fitted, leave it and do not add a second diode: an external diode opposed to a hidden internal diode shorts the coil. The 2.5 A fuse then opens and the contactor does not pull in.

Failure of a correctly placed diode stays off the windlass. A shorted diode collapses the coil voltage, the control fuse opens, and the contactor cannot pull in. An open diode leaves the contact unsuppressed. Finder’s unsuppressed switch-off voltage can reach 15 times the coil voltage, about 180 V on a 12 V coil, against the 1000 V AC open-contact dielectric. The Finder contact wears faster. COM and NO are not bridged by either failure. A diode across the Finder contact, rather than across the coil, is the wrong place and is not used.

The cost is release time. Finder states that the parallel diode increases the release time of the load. Quick does not publish coil inductance or dropout time, so the added delay cannot be calculated. It delays a stop. It does not energise a coil. Measure the dropout on the boat after the diode is fitted. An RC snubber was not chosen: Quick does not publish pull-in current, so a shorted capacitor in series with a resistor cannot be shown to stay below pull-in. A TVS would release faster and would put the contact back on the 50% approximation, because Finder’s written equivalence with DC1 is the freewheeling diode.

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

`R60` and `R70` are still 1 kΩ on the schematic. The margin calculation is in the review section above. The series-FET gate resistor stays 100 Ω. That path meets the 3.0 V on-level. The two direction inputs do not, on the published ESP32-S3 VOH, and the correction is a 74LVC1G buffer plus 100 Ω. It is not drawn yet.

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

The suppression decision is in the review section above. One 1N5404 per coil, at the contactor, after confirming that coil has no suppressor of its own. Cathode to the coil terminal that is positive while the coil is energised, anode to the coil return. The boat’s existing 2.5 A fast control fuse stays in the control wiring and is not a PCB part. Finder’s current DC1 row is 12 A at 24 V. With the diode, DC13 life is that DC1 life. Without it, the published approximation is 6 A. Both sit above 2.5 A. The contact copper stays 1.2 mm. IPC-2221 for an external 1 oz trace at a 10 °C rise is about 1.07 mm at 2.5 A. This PCB does not supply the contactor coils.

## Still a measurement

These are not closed by a datasheet:

- The direction-driver correction: a 74LVC1G buffer on GPIO9 and GPIO10, and `R60` and `R70` at 100 Ω. It is specified above and is not on the schematic. Firmware can be written against the existing pin names. A coil-on test waits until that buffer is on the board.
- The installed contactor has to be confirmed as a Quick T6315-12 or T6415-12. If it is not, the 2.5 A comparison above does not apply. Quick does not publish coil current, resistance, inductance, or inrush, so the 2.5 A fuse is the bound that was used.
- Whether that contactor already has a coil suppressor, and which coil terminal is positive. Fit the 1N5404 only when the housing has none, then measure the release time.
- Whether a parallel contact feeds the hand remote or the Lofrans box. That is the boat wiring, and it is not in the Quick sheet.
- Where the ignition permissive sits, and whether it must stay in series (B2).
- The Lofrans reed, on the boat, with this input connected (B4).
- The sense-wire voltage, return, and which conductor is UP (B5).
- Whether this 12 V feed can be load-dumped, and the enclosure and antenna clearance (B6). The SMAJ18A and the 36 V short-circuit rating do not close that.
- The Q pulse with the fitted `C50`, and a reviewed image that edges GPIO1, before any coil is tested (B7).
- The NMEA drop, the backbone terminations, and which device publishes (B8).

Separate from the boat, and unchanged by this revision: `C30I` effective capacitance at 12 V, `ISO_5V` at the preload, the USB4105 note, and the MEJ2 pin-1 dimension.
