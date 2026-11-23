# Electrical review of the cleared board

23 November 2026, afternoon Sydney time. The schematic in `kicad11/`, the netlist `kicad11/windlass.net`, `kicad11/windlass_cleared.kicad_pcb`, and `docs/integrated_bom.md` were checked against the datasheets named below. No schematic, PCB, firmware, or BOM value was changed. No Gerber was written and no part was ordered.

The cleared board’s DRC is clean (0 violations, 0 unconnected items, 12:33 pm Sydney time, `kicad11/drc_cleared.rpt`). That report does not include schematic parity. A clean DRC is not an electrical release and is not permission to fabricate.

## Verdict

The board is not ready to fabricate. One connection is wrong and shorts the isolated CAN supply.

After that net is moved, the power input, the coil interlock, the reed input, and the ESP32 straps agree with the datasheets and can be built as a bench prototype. Capacitor voltages and a real inductor ordering code still have to be locked before parts are bought. B1–B8 are measurements. They block connecting the board to the windlass. They do not, by themselves, block etching a bench board once the short is removed.

## Critical — fix before fabrication

### U10 pin 10 shorts ISO_5V to GND_CAN

TI ISO1042, SLLSF09F, revised August 2026, Figure 4-1 (DW, 16-pin SOIC, top view):

| Pin | Datasheet | This board |
| --- | --- | --- |
| 9 | GND2 | `GND_CAN` |
| 10 | GND2 | `ISO_5V` |
| 11 | VCC2, tie to pin 16 | `ISO_5V` |
| 15 | GND2 | `GND_CAN` |
| 16 | VCC2, tie to pin 11 | `ISO_5V` |

Pins 9, 10, and 15 are the same transceiver-side ground. Pad 10 of U10 on `windlass_cleared.kicad_pcb` is at the physical pin-10 position (right-hand row, second pad up from pin 9) and its net is `ISO_5V`. The package therefore joins `ISO_5V` to `GND_CAN`. The MEJ2S0305SC output is shorted. The CAN transceiver cannot run. The short is on the isolated side only.

The symbol in `isolated_nmea2000.kicad_sch` names pin 10 `VCC2`. That name is the error. Pins 1–3, 5, 8, 11–13, and 16 match the datasheet, and pins 4, 6, 7, and 14 are correctly unconnected. `J_NMEA` pin 5 (NET-S) is unconnected. `R94` is from `ISO_5V` to `GND_CAN`, not across CANH and CANL. `C92` joins the shield to `GND_CAN` only.

Proposed correction, not applied: rename symbol pin 10 to GND2 and connect it to `GND_CAN`. Leave pins 11 and 16 on `ISO_5V`. Update the cleared PCB pad with the schematic, then refill and run ERC and DRC. Do not add a 120 Ω terminator while doing that.

## Important — settle before parts are ordered

### The 3.9 µH SRN4018 is not a Bourns ordering code

Diodes’ AP63203 table recommends 3.9 µH, 10 µF in, two 22 µF out, and 100 nF bootstrap. The board has those values, and the pinout matches: FB (pin 1) on `+3V3`, EN (pin 2) tied to VIN, VIN (pin 3), GND (pin 4), SW (pin 5), BST (pin 6). Diodes allows EN to be tied to VIN. EN absolute maximum is 35 V. Recommended VIN is 32 V. Absolute maximum is 35 V DC and 40 V for 400 ms. The valley current limit is 2.5 A minimum, 3.2 A typical, 3.9 A maximum.

Bourns SRN4018 (datasheet table retrieved 23 November 2026) lists SRN4018-3R3M at 3.3 µH, Isat 2.3 A, Irms 2.2 A, and SRN4018-4R7M at 4.7 µH, Isat 2.0 A. It does not list 3.9 µH. `docs/circuit_calculations.md` asks for Isat above 3.1 A. Both neighbouring parts are under that floor and under the 3.9 A limit maximum. At a normal load under 1 A, 2.3 A Isat is enough. The inductor saturates if the buck hits current limit.

Proposed correction: put a real ordering code on L20. SRN4018-3R3M fits the existing land and sits inside Diodes’ 2.2–10 µH range. If the 3.1 A floor is kept, the footprint has to change to a part that actually has that Isat.

### Capacitor voltage is not on the BOM

`C30I` is 10 µF, 0805, on the 12 V rail after the P-FET. A 6.3 V part would be over its rating. An 0805 10 µF at 25 V also loses most of its capacitance at 12 V DC bias, and Diodes asks for more than 10 µF. `C50` is 3.3 µF, 0805, on the monostable. Nexperia’s formula for Cext above 10 nF is tW = K × Rext × Cext with K about 1, so 100 kΩ and 3.3 µF is about 330 ms only if the capacitor is actually 3.3 µF. An X7R part under DC bias will be shorter. `C92` is 100 nF from the NMEA shield to `GND_CAN` with no voltage written down.

Proposed correction: specify voltage and dielectric before purchase. `C30I` at least 25 V, checked on the manufacturer’s bias curve, or a larger case. `C50` measured on the first board (see Verification). `C92` at least 50 V.

### The coil fuse is larger than the coil FET

Finder 40.31.7.012.0000, sensitive 12 V coil: 288 Ω, 42 mA, operate 8.8–18 V. Nexperia NX6008NBK: VGS maximum ±8 V, continuous drain 270 mA at VGS = 4.5 V and 25 °C, RDSon maximum 3 Ω at VGS = 2.5 V. The gates are 3.3 V, so they are inside the 8 V limit. Two FETs in series drop under about 0.26 V at 42 mA. The coil still sees more than the 8.8 V pickup at 12 V.

`F_COIL` is 1 A. A shorted coil lead can push the NX6008 past 270 mA before that fuse opens. One FET failing short does not energise a coil: the series FET and the low-side FET both have to conduct. Both failing short, with the ignition and the relay-power switch closed, does.

Proposed correction: a coil fuse above 42 mA and below 270 mA, or a low-side FET rated above the fuse. For a bench board that never leaves the bench, the present 1 A fuse only fails this fault case.

### A shorted contact clamp holds the contactor on

`D61` and `D71` are SMBJ18CA across each COM–NO pair. They are not connected to board ground, and `UP_COM` is not tied to `DN_COM`. The NC pins are open. A TVS that is overloaded fails short. A short from COM to NO is the same stuck-run as a welded contact (B3). Nothing on this board then opens that path. `F_COIL` and `F_MCU` do not carry contactor current.

Proposed correction, after B1 gives the current: a fuse in each contact lead, above the measured coil current and below the 1.2 mm trace. Until that measurement, do not land `J_CONTACT` on the boat. The 1.2 mm width is the IPC-2221 external 1 oz, 10 °C figure for 2.5 A. It is not a measured contactor current. Finder’s DC1 figure used here is 10 A at 30 V DC resistive. Finder’s own note is that a DC13 inductive load is about half of that unless the load already has a diode. The SMBJ is across the contact, not a diode across the contactor coil.

### The isolated 5 V tolerance is not the 9% written on the sheet

The NMEA sheet says 5 V plus a 9% envelope is 5.45 V, inside the ISO1042 VCC2 range of 4.5–5.5 V. Absolute maximum on VCC2 is 6 V. The Murata MEJ2 selection guide prints 13 and 15 in the load-regulation columns for MEJ2S0305SC. That is not 9%, and the tolerance-envelope drawing was not readable as a number in the text extract. The 42 mA preload is 10.5% of the 400 mA rating, which is the region where Murata’s regulation figure starts to apply. `R94` dissipates about 0.21 W at 5 V and about 0.25 W at 5.45 V, inside the 0.5 W part.

Proposed correction: measure `ISO_5V` with JP1 fitted and only the preload, after pin 10 is fixed. If it is outside 4.5–5.5 V, add a post-regulator. Do not treat 5.45 V as shown.

### Older documents will buy the wrong parts

The schematic and `docs/integrated_bom.md` are the parts list. These older statements are not:

- `docs/circuit_calculations.md` still describes the XOR, a second buck (AP63205), and coil FETs called `NMOS_COIL_OPEN`. The sheet has neither gate. The coil FETs are NX6008NBK.
- `docs/pin_allocation.md` still puts a blue LED on GPIO17 and an ISO7721 on the reed. GPIO17 is open. The reed part is ISO7720FDR.
- `docs/architecture.md` still names MEJ2S0505SC, a 5 V input. U9 pin 1 is fed from 3.3 V through JP1. The part on the sheet is MEJ2S0305SC. A 5 V-input module will not start.
- `docs/assumptions_and_open_questions.md` A2 still says the DC-DC is not chosen, and A7 says KiCad 10 is not installed. KiCad 10.0.8 produced the netlist.

`C10` is the EN capacitor (10 kΩ to 3.3 V, 1 µF to GND, button to GND). The BOM calls it module bulk. `C11` is the 10 µF on 3.3 V. `C12` is 100 nF on 3.3 V, not the USB shield capacitor. That capacitor is `C13`.

Proposed correction: mark those older pages as superseded by `docs/integrated_design.md` and `docs/integrated_bom.md`, and correct the three BOM role labels. Do not change the nets.

### USB4105 residual, already recorded

The ground-pad relief meets the board’s 0.25 mm hole rule. JLCPCB has not reviewed the board. A hole moved by their published ±0.075 mm still leaves about 0.205 mm. Adding the through-hole oversize as well can leave about 0.140 mm. That arithmetic is in `docs/usb4105_jlcpcb.md`. It is not a new electrical defect, and it is not a fabrication approval.

### The existing firmware cannot run this board

The prototype image uses reed GPIO27, sense GPIO25 and GPIO26, and relay GPIO32 and GPIO33, and it does not edge GPIO1. Those GPIO numbers are not the pins of ESP32-S3-WROOM-1-N16. This board’s map, taken from the netlist and the module pad names, is TWAI GPIO4 and GPIO5, reed GPIO6, UP sense GPIO7, DOWN sense GPIO8, UP request GPIO9, DOWN request GPIO10, coil-rail GPIO14, red GPIO15, green GPIO16, publish GPIO18, USB GPIO19 and GPIO20, UART GPIO43 and GPIO44, heartbeat GPIO1. GPIO17, GPIO45, and GPIO46 are open. A board loaded with the prototype image keeps the coils off. That image was not edited. A reviewed image is required before a coil test. The 300 ms command TTL is a different mechanism and was not changed.

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

The blanker is two 74LVC1G00 gates. Field-supply loss forces GPIO6 low, so a falling supply is not a rising edge. The latch stays blocking until the reed data has been low while the field rail is up, so a supply that returns during a pulse misses that pulse instead of counting it twice. `REED_RET` is not joined to `GND`, `UP_RET`, `DN_RET`, or `GND_CAN` in the netlist. On the cleared board those nets have no vias and their copper is on F.Cu.

### Direction sense

TLP291 pin 1 is the LED anode, pin 2 the cathode, pin 3 the emitter, pin 4 the collector. `R30` and `R40` feed the anodes. The cathodes return on `UP_RET` and `DN_RET`, which are separate and are not board ground. The collectors are active low into GPIO7 and GPIO8 with 10 kΩ to 3.3 V. The 1N4148W diodes are anti-parallel. At 12 V the LED current is about (12 − 1.2) / 4.7 kΩ ≈ 2.3 mA. At 24 V it is about 4.9 mA. Both are far under the LED absolute maximum used in the design notes. The 4.7 kΩ values assume a low-impedance switched positive. If B5 shows something else, the resistors change before installation. There is no copper path from these inputs to the contact nets.

### ESP32-S3

GPIO0 has 10 kΩ to 3.3 V and a button to GND. GPIO3 has 10 kΩ to GND. GPIO45 and GPIO46 are open, which is what the 3.3 V-flash module requires. EN has the 10 kΩ and 1 µF above. USB D+ and D− leave GPIO19 and GPIO20 through 22 Ω. CC1 and CC2 have 5.1 kΩ to GND. USBLC6 pin 5 is `USB_VBUS`, not 3.3 V. SBU pins are open.

### NMEA, apart from pin 10

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
| B7 | The monostable pinout and the 330 ms formula match Nexperia. GPIO1 must rise at least every 100 ms. The prototype image does not. The 300 ms TTL is a different timer and was not changed. | The actual Q pulse with the fitted `C50`, and a reviewed image that edges GPIO1, before any coil test. |
| B8 | No terminator, NET-S open, publish jumper open, shield to `GND_CAN` only. One publisher is the rule already written down. | Whether a drop can reach the mount, whether both backbone ends are already terminated, and whether the other transmitter is removed. |

A2 and A7 in the assumptions table are stale, as noted above. A1, A3, A4, A5, and A6 are unchanged by this review. The explicit non-assumptions still hold: Lofrans ground is not this board’s ground, no 120 Ω belongs here until B8 says this drop is an end, NET-S does not power the transceiver, and an LED is not a safety indication.

## Before a first prototype is manufactured

1. Move U10 pin 10 to `GND_CAN`.
2. Replace “3.9 µH SRN4018” with an ordering code that exists, and write capacitor voltages on the BOM.
3. Decide, in writing, that the 1 A coil fuse and the contact clamps are accepted for a bench article that is not wired to a contactor. If the first article might be wired to one, change those two items first.
4. Leave B1–B8 open. Do not install the board to answer them.
5. Do not program the prototype image and expect the relays to move.
6. Leave the title block as not for fabrication until the pin-10 board has its own ERC and DRC, and until the USB land risk in `docs/usb4105_jlcpcb.md` is accepted or removed.

## Datasheets used

- Texas Instruments ISO1042, SLLSF09F, revised August 2026. Figure 4-1 and the pin table.
- Diodes AP63200/AP63201/AP63203/AP63205. Pin table, absolute maximums, recommended operating conditions, and the AP63203 component table.
- Diodes DMP6023LE, DS37199 Rev. 3-2, January 2015. Pin diagram and RDS(on).
- Nexperia 74LVC1G123, Rev. 8, 14 August 2023. Pin table and the pulse-width formula.
- Nexperia NX6008NBK, 19 August 2021. Limiting values and RDSon.
- Murata MEJ2 series datasheet. Pin table, 5.2 kV DC hipot, 2.4 kV DC continuous functional isolation, selection-guide columns for MEJ2S0303SC and MEJ2S0305SC.
- Bourns SRN4018 series table, retrieved 23 November 2026. No 3.9 µH row. 3.3 µH and 4.7 µH rows as cited.
- Finder 40 series coil table for the 7.012 sensitive coil: 288 Ω, 42 mA, 8.8–18 V. DC1 and the DC13 note as cited in the design documents and the Finder general technical information.
