# Electrical review, bench revision

23 November 2026, Sydney time. The installation revision supersedes the two bench restrictions in the section below. The current schematic and `kicad11/windlass_install.kicad_pcb` are the design to read. The calculations, the parts, and what is still a boat measurement are in `docs/install_protection.md`. `kicad11/windlass_bench.kicad_pcb` was not edited and no longer matches the schematic. It remains the copper checkpoint of the bench article.

The cleared board `kicad11/windlass_cleared.kicad_pcb` is unchanged. The corrections below are the bench revision. No firmware was edited. No Gerber was written and no part was ordered.

ERC at 2:53 pm Sydney time (`kicad11/erc_bench.rpt`): 0 errors, 1 warning. The warning is U5 pin 4 `GND1` on `REED_RET`, and it is intentional. DRC at 2:56 pm Sydney time (`kicad11/drc_bench.rpt`), after a zone refill: 0 violations, 0 unconnected pads. Schematic pad nets match the board. `GND_CAN`, `ISO_5V`, `CAN_H`, `CAN_L`, `REED_RET`, `UP_RET`, `DN_RET`, and the other isolated-side nets have no vias and no inner-layer copper.

A clean DRC is the connectivity check. The title block says not for fabrication and not for marine installation. That stands.

## Verdict

There is no remaining critical copper defect on the bench revision. U10 pin 10 is `GND_CAN`. L20 is a Bourns SRN6045-3R3Y, because the SRN4018-3R3M saturation rating is below the converter’s peak current limit. C30I, C50, and C92 have voltage ratings and dielectrics. The 1 A coil fuse and the contact clamps are written down as bench-only restrictions.

This is a bench-prototype design. It is not approval to install the board on the boat. B1–B8 are still the installation measurements, and they are listed separately from the items that are still unverified on the bench article.

## Corrections applied

### U10 pin 10 is GND2 on GND_CAN

TI ISO1042, SLLSF09F, revised August 2026, Figure 4-1 (DW-16, top view):

| Pin | Datasheet | Bench schematic and PCB |
| --- | --- | --- |
| 9 | GND2 | `GND_CAN` |
| 10 | GND2 | `GND_CAN` |
| 11 | VCC2, tie to pin 16 | `ISO_5V` |
| 15 | GND2 | `GND_CAN` |
| 16 | VCC2, tie to pin 11 | `ISO_5V` |

The symbol in `kicad11/windlass.kicad_sym` and the copy embedded in `isolated_nmea2000.kicad_sch` now name pin 10 GND2. Pins 11 and 16 stay VCC2. Pins 4, 6, 7, and 14 stay unconnected. The PCB pad is the physical pin 10, on F.Cu, joined to pin 9. Pin 11 stays on `ISO_5V` and still feeds U9 pin 7. No via was added. No 120 Ω terminator was added. `R94` remains the preload from `ISO_5V` to `GND_CAN`.

On the cleared checkpoint, pad 10 is still `ISO_5V`. That file is the record of the short. The bench file is the one to build from.

### L20 is SRN6045-3R3Y

Bourns does not list a 3.9 µH SRN4018. SRN4018-3R3M is a real part: 3.3 µH, Isat 2.3 A at 30% drop, Irms 2.2 A. It was not fitted.

The AP63203 high-side peak current limit is 2.5 A minimum, 2.8 A typical, and 3.1 A maximum. Cycle-by-cycle protection turns the high-side FET off at that current. The inductor has to remain out of saturation until that limit can act. The current to design for is the 3.1 A maximum of the peak limit, plus whatever the limiter lets through during its delay. The normal board load, which is under 1 A, does not set this number. The 3.9 A valley-limit maximum is a different threshold and was not used as the saturation floor.

SRN4018-3R3M Isat of 2.3 A is below the 2.5 A minimum peak limit, so the core is already at its saturation definition before the limiter is guaranteed to trip. Its 2.2 A Irms is also below 2.7 A, which is Diodes’ rule of a DC rating at least 35% above a 2 A load. Both checks fail. The part was rejected for that reason.

SRN6045-3R3Y, Bourns rev 01/20, is the part on the schematic and the board: 3.3 µH ±30%, Isat 5.0 A, Irms 3.2 A, DCR 30.2 mΩ maximum, body 6.0 × 6.0 × 4.5 mm. Isat is 1.9 A above the 3.1 A peak-limit maximum. Irms is above 2.7 A. At 12 V to 3.3 V and 1.1 MHz, 3.3 µH gives about 0.66 A of ripple, 33% of 2 A, inside Diodes’ 30–50% window. At the −30% inductance the ripple is about 0.94 A, still inside 50%. At 32 V and 2.31 µH the current rises about 14 A/µs, so the 1.9 A gap is about 140 ns. The datasheet does not publish the limiter delay. That 140 ns figure is the budget, and a short-circuit check on the first article is the measurement.

The land is the recommended layout on that drawing: each pad 2.3 mm by 6.0 mm, 2.0 mm between the facing edges. L20 moved 0.70 mm in +X so the larger pad clears the bootstrap via. The footprint is `windlass:L_Bourns_SRN6045`. It is not the SRN6045TA land in the KiCad library.

### Capacitor ratings

`C30I` is Murata GRM32ER71E226KE15 or an equivalent 22 µF, 25 V, X7R, 1210, on `+12V_MCU`. Diodes asks for more than 10 µF at the buck input. An 0805 10 µF Class II part at 12 V does not remain 10 µF, so that case was removed. The Murata reference sheet confirms the marked rating and the 1210 body. It does not include this part’s DC-bias curve, and none was invented. Effective capacitance at 12 V is a first-article measurement. If it is under 10 µF, fit a second capacitor. That measurement is separate from B1–B8.

`C50` is Murata GRM31CR71H335KA88L or an equivalent 3.3 µF, ±10%, 50 V, X7R, 1206. `R52` stays 100 kΩ. Nexperia’s formula for Cext above 10 nF is tW = K × Rext × Cext with K about 1, so the nominal pulse is still about 330 ms. The voltage across the timing capacitor during the pulse is on the order of the 3.3 V rail, which is 6.6% of a 50 V rating. The ±10% tolerance alone puts the pulse between about 300 ms and 360 ms. A further 20% loss, which is a pessimistic allowance and not this part’s curve, still leaves about 240 ms, above the 100 ms edge interval and near the 300 ms firmware TTL. The resistor and the nominal capacitance were not increased. The pulse is still measured on the first board (B7).

`C92` is Murata GRM155R71H104KE14 or an equivalent 100 nF, 50 V, X7R, 0402. It joins `NMEA_SHIELD` to `GND_CAN`. Both nets are on the isolated side of the barrier, so the capacitor is not a barrier component. The footprint stays 0402.

`C30A` and `C30C` stay 22 µF, 0805, and are purchased as 16 V or higher, X7R. Ceramics on the 3.3 V rail are 16 V or higher. `C10` is the EN delay capacitor, 1 µF. `C11` is 10 µF on 3.3 V. `C12` is 100 nF on 3.3 V. The USB shield capacitor is `C13`.

### The 1 A coil fuse and the contact clamps are bench restrictions

These two circuits were not changed. They are accepted only for a bench article that is not wired to a windlass contactor.

`F_COIL` is 1 A (0466001). The Finder coil is 42 mA. The NX6008NBK continuous rating is 270 mA at VGS = 4.5 V and 25 °C. A shorted coil lead can take the FET past 270 mA before the fuse opens. One FET failing short does not energise a coil, because `Q_SERIES` and the low-side FET are in series. Both failing short, with the ignition and the relay-power switch closed, does. This fuse is not approved as the protection for an installed windlass.

`D61` and `D71` are SMBJ18CA across each COM–NO pair. They are not connected to board ground, and `UP_COM` is not tied to `DN_COM`. A TVS that is overloaded fails short. A short from COM to NO holds that contactor on. Nothing on this board then opens that path. `F_COIL` and `F_MCU` do not carry contactor current. `J_CONTACT` stays off the boat until B1 is measured and the contact protection is redesigned for that current. The 1.2 mm trace is the IPC-2221 external 1 oz, 10 °C figure for 2.5 A. It is not a measured contactor current.

### Documents brought back to the schematic

The schematic and `docs/integrated_bom.md` are the parts list. `docs/circuit_calculations.md`, `docs/pin_allocation.md`, `docs/architecture.md`, `docs/component_availability.md`, `docs/connector_pinout.md`, and `docs/design_review.md` now say so at the top. Those pages still describe the earlier revision, including the XOR, the AP63205, `NMOS_COIL_OPEN`, a blue LED on GPIO17, an ISO7721, and MEJ2S0505SC. The integrated board has none of those. GPIO17 is open. The reed isolator is ISO7720FDR. U9 is MEJ2S0305SC, fed from 3.3 V through JP1. A2 and A7 in `docs/assumptions_and_open_questions.md` now say the converter is chosen and that KiCad 10.0.8 produced the netlist. The NMEA sheet no longer says that 5 V plus 9% is 5.45 V. Murata’s load-regulation columns for MEJ2S0305SC print 13 and 15. `ISO_5V` is measured at the preload.

## What matches the datasheets

### 12 V input

`J_PWR` splits after the connector into `F_MCU` (2 A, 0466002) and `F_COIL` (1 A, 0466001). Each branch has an SMAJ18A with the cathode on the fused rail and the anode on GND, then a DMP6023LE-13. Diodes DS37199: pin 1 gate, pin 2 drain (the tab is drain), pin 3 source. The body diode points from drain to source. The board puts the drain on the fused input and the source on the load, with BZT52C12 from source to gate and 100 kΩ from gate to GND. Correct polarity turns the FET on. Reverse polarity leaves it off, and the TVS then conducts so the fuse opens. VGS is clamped near 12 V. The datasheet limit is ±20 V. RDSon is 35 mΩ maximum at VGS = −4.5 V, against a load of a few hundred milliamps.

The buck is a 2 A part. The steady 12 V draw is the coil at 42 mA on its own fuse, plus the 3.3 V rail. That rail supplies the module, about 100 mA into the reed converter at its 65 mA preload, and on the order of 200 mA into the CAN converter when the transceiver is dominant. The 2 A fuse and the 2 A buck are not the limiting ratings. This is an estimate from the Murata full-load input currents scaled by output current, not a measurement. SMAJ18A clamping is about 29.2 V, under the buck’s 32 V recommended maximum. It is not load-dump protection. Load-dump energy is B6.

USB VBUS does not feed the buck. Programming needs the 12 V input. That is the intended service arrangement, not a missing diode.

### Windlass control

Coil current is `+12V_COIL`, through `R_SWLINK`, the external relay-power switch, `R_IGNLINK`, the ignition contact, and `R_COILFEED`, to both coil high sides. Either connector left open leaves the coils off. The three links are 0 Ω, 0402, at 42 mA.

`Q_UP` and `Q_DN` are low-side. Their sources meet at `Q_SERIES`, whose source is GND. `Q_SERIES` is on only while the 74LVC1G123 output is high. Nexperia 74LVC1G123 (SOT505-2): pin 1 is A, the falling-edge input, tied to GND; pin 2 is B, the rising-edge input, on GPIO1 with a 100 kΩ pulldown; pin 3 is CLR, tied to 3.3 V; pin 5 is Q, through 100 Ω to the gate, with 100 kΩ to GND. A static level does not retrigger. Q is low until an edge. The coils fail off when the heartbeat stops, the MCU resets, or 3.3 V is absent.

A DOWN request turns on `Q_CLAMP_UP` and holds the UP gate off, and the reverse. Both requests hold both gates off through the 10 kΩ series resistors. The XOR and the AND are not on this sheet, and they are not required for that case. A single stuck request still runs that one coil for as long as GPIO1 keeps rising. That limit is the firmware contract, not a second timer.

`D60` and `D70` are SS14 with the cathode on `COIL_12` and the anode on the coil low side. They are across the Finder coils only.

### Lofrans reed

U4 is MEJ2S0303SC. Murata’s single-output pins are 1 +Vin, 2 −Vin, 5 −Vout, 7 +Vout. The footprint uses those four holes at 2.54 mm and omits pin 6, which Murata does not fit on the single-output part. Pin 1 is `+3V3`. The secondary is `REED_3V3` and `REED_RET`. Murata’s production test is 5.2 kV DC for one second. The continuous functional rating is 2.4 kV DC. Murata states that this is not a safety barrier, and the series disclaimer excludes life-critical use without written approval. The windlass safety case cannot rest on these modules. The same figures apply to U9.

`R24` is 51 Ω, 0.5 W. At 3.3 V it draws about 65 mA and dissipates about 0.21 W, just over 10% of the 606 mA rating.

ISO7720FDR pins match the symbol: VCC1 and INB on `REED_3V3`, INA on `REED_ISO`, GND1 on `REED_RET`, OUTA to the blanker, OUTB used as field-supply present. The F suffix holds the logic outputs low when the field side has no supply. `R23`, 47 kΩ, holds INA low with the shunt off. `R22`, 4.7 kΩ, pulls `DRY_A` up and reaches the isolator only when the shunt joins pins 2 and 3. The Lofrans position (pins 1–2) leaves that pull-up off the boat wire. BAT54W clamps sit from the Lofrans node to `REED_3V3` and to `REED_RET`, after 10 kΩ. A 12 V source into that 10 kΩ is under 1 mA, against a 65 mA preload.

The blanker is two 74LVC1G00 gates. Field-supply loss forces GPIO6 low, so a falling supply is not a rising edge. The latch stays blocking until the reed data has been low while the field rail is up, so a supply that returns during a pulse misses that pulse instead of counting it twice. `REED_RET`, `UP_RET`, `DN_RET`, `GND_CAN`, and `GND` are separate nets. On `windlass_bench.kicad_pcb` those nets, and the other isolated-side nets, have no vias and no inner-layer copper.

### Direction sense

TLP291 pin 1 is the LED anode, pin 2 the cathode, pin 3 the emitter, pin 4 the collector. `R30` and `R40` feed the anodes. The cathodes return on `UP_RET` and `DN_RET`, which are separate and are not board ground. The collectors are active low into GPIO7 and GPIO8 with 10 kΩ to 3.3 V. The 1N4148W diodes are anti-parallel. At 12 V the LED current is about (12 − 1.2) / 4.7 kΩ ≈ 2.3 mA. At 24 V it is about 4.9 mA. Both are far under the LED absolute maximum used in the design notes. The 4.7 kΩ values assume a low-impedance switched positive. If B5 shows something else, the resistors change before installation. There is no copper path from these inputs to the contact nets.

### ESP32-S3

GPIO0 has 10 kΩ to 3.3 V and a button to GND. GPIO3 has 10 kΩ to GND. GPIO45 and GPIO46 are open, which is what the 3.3 V-flash module requires. EN has the 10 kΩ and 1 µF above. USB D+ and D− leave GPIO19 and GPIO20 through 22 Ω. CC1 and CC2 have 5.1 kΩ to GND. USBLC6 pin 5 is `USB_VBUS`, not 3.3 V. SBU pins are open.

### NMEA

JP1 is fitted open. `R90`, 100 kΩ, holds the module input off. GPIO18 only senses that node through 10 kΩ. A GPIO driven high can source about 0.3 mA, which cannot run the converter, so a firmware mistake does not publish. TXD is pulled up by 10 kΩ and in series with 33 Ω, so an undriven pin is recessive. No 120 Ω sits on CANH/CANL.

## B1–B8

| Item | Answered from the design and the datasheets | Still a measurement |
| --- | --- | --- |
| B1 | The contacts are dry NO. The commons are separate. Suppression is an SMBJ18CA across each pair, with no onboard fuse. The trace is drawn for 2.5 A. The relay’s resistive DC rating is 10 A at 30 V. None of that is the boat’s current, inrush, or energy, and none of it says whether the boat wire is dry, switched 12 V, or switched ground. | Voltage, current, inrush, inductance, existing diode, and whether a parallel contact feeds 12 V back into the hand remote. |
| B2 | The sheet puts the ignition loop in series with the coil feed, after the relay-power switch. An open connector is off. The firmware image has no ignition input, and this hardware does not give it one. | Where the boat’s permissive is, its open voltage and closed current, and whether it must stay in series. |
| B3 | This PCB cannot open a welded contact or a shorted SMBJ. The clearing action is the boat breaker. | The real current, set against Finder’s welded-contact guidance, and the operator rule. |
| B4 | The Lofrans load is 10 kΩ in series and 47 kΩ to the isolated return, with BAT54 clamps. Idle current is on the order of 70 µA only if the source is near 3.3 V. The pull-up cannot reach the Lofrans pin in the default shunt position. The reference is `REED_RET`, not board ground. | Idle and active voltage, rise and fall, source impedance, and whether that reference is battery negative. The old 3.22 V to 1.5 V sag is the result to avoid. |
| B5 | Two optocouplers, separate returns, active low on GPIO7 (UP) and GPIO8 (DOWN). Those are not the DevKit pins in the README or in `main.cpp`. | Idle and active voltage, which ground, whether the wires are the contactor coils, and which physical wire is UP. |
| B6 | The input is designed for 12 V. The coil is specified to 18 V. SMAJ18A is not a load-dump clamp. The buck rise used in the calculations is 89 °C/W from Diodes’ single-layer test board, not this enclosure. | Which battery and breaker, whether the engine can load-dump that feed, the enclosure, and 15 mm from the antenna to metal. |
| B7 | The monostable pinout matches Nexperia. `C50` is now 3.3 µF, 50 V, X7R, 1206, with `R52` still 100 kΩ, so the nominal pulse is still about 330 ms. GPIO1 must rise at least every 100 ms. The prototype image does not. The 300 ms TTL is a different timer and was not changed. | The actual Q pulse with the fitted `C50`, and a reviewed image that edges GPIO1, before any coil test. |
| B8 | No terminator, NET-S open, publish jumper open, shield to `GND_CAN` only. One publisher is the rule already written down. | Whether a drop can reach the mount, whether both backbone ends are already terminated, and whether the other transmitter is removed. |

A2 and A7 now name the MEJ2S0305SC and KiCad 10.0.8. A1, A3, A4, A5, and A6 are unchanged by this review. The explicit non-assumptions still hold: Lofrans ground is not this board’s ground, no 120 Ω belongs here until B8 says this drop is an end, NET-S does not power the transceiver, and an LED is not a safety indication.

## What remains before this board can be built or installed

The title block on `windlass_bench` still says not for fabrication and not for marine installation. ERC at 2:53 pm Sydney time is 0 errors and the same one intentional warning (U5 pin 4 `GND1` on `REED_RET`). DRC at 2:56 pm Sydney time is 0 violations and 0 unconnected pads (`kicad11/drc_bench.rpt`). A clean DRC is the connectivity check. It is not a fabrication release and it is not permission to wire the board to a windlass.

Still open, and separate from B1–B8:

- `C30I` effective capacitance at 12 V. The part is specified. Its own DC-bias curve was not in the sheet used here. Measure it on the first article. If the result is under 10 µF, add a second capacitor.
- `ISO_5V` at the 42 mA preload, after pin 10 is on `GND_CAN`. It has to sit inside 4.5–5.5 V.
- The Q pulse with the fitted `C50` (B7 is that measurement).
- The USB4105 residual in `docs/usb4105_jlcpcb.md`. JLCPCB has not reviewed the board.
- The MEJ2 pin-1 to body-end dimension against the courtyard.

B1–B8 stay open. They are the installation measurements. The 1 A coil fuse and the SMBJ fail-short behaviour stay bench-only restrictions. The prototype image was not edited and does not edge GPIO1, so a board loaded with that image keeps the coils off.

## Datasheets used

- Texas Instruments ISO1042, SLLSF09F, revised August 2026. Figure 4-1. Pins 9, 10, and 15 are GND2. Pins 11 and 16 are VCC2 and are tied together.
- Diodes AP63200/AP63201/AP63203/AP63205. Pin table, absolute maximums, the high-side peak current limit (2.5 / 2.8 / 3.1 A), and the AP63203 component table.
- Diodes DMP6023LE, DS37199 Rev. 3-2, January 2015. Pin diagram and RDS(on).
- Nexperia 74LVC1G123, Rev. 8, 14 August 2023. Pin table and the pulse-width formula for Cext above 10 nF.
- Nexperia NX6008NBK, 19 August 2021. Limiting values and RDSon. Continuous drain 270 mA at VGS = 4.5 V, 25 °C.
- Murata MEJ2 series datasheet. Pin table, 5.2 kV DC hipot, 2.4 kV DC continuous functional isolation, selection-guide columns for MEJ2S0303SC and MEJ2S0305SC.
- Murata reference sheet for GRM32ER71E226KE15 (22 µF, 25 V, X7R, 1210) and the published ratings for GRM31CR71H335KA88L (3.3 µF, 50 V, X7R, 1206) and GRM155R71H104KE14 (100 nF, 50 V, X7R, 0402). No DC-bias curve for those three parts was read for this revision.
- Bourns SRN4018 series table, retrieved 23 November 2026. SRN4018-3R3M is 3.3 µH, Isat 2.3 A, Irms 2.2 A. No 3.9 µH row.
- Bourns SRN6045 series, rev 01/20. SRN6045-3R3Y is 3.3 µH ±30%, Isat 5.0 A, Irms 3.2 A, DCR 30.2 mΩ maximum. Recommended layout: pad 2.3 mm by 6.0 mm, 2.0 mm between the facing edges.
- Finder 40 series coil table for the 7.012 sensitive coil: 288 Ω, 42 mA, 8.8–18 V. DC1 and the DC13 note as cited in the design documents and the Finder general technical information.
