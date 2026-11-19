# Routing feasibility — revision 0.8

Not a fabrication release. The four relay-contact nets are routed at 0.80 mm. A partial signal route follows them. Most nets are still open. No Gerber, drill, or position file has been written. The working prototype was not opened, flashed, or changed. The schematic was not regenerated.

The outline stays 80 × 69 mm. Nothing found in this pass is a reason to grow it. The original 9 mm was not reopened.

## Stackup

The board file uses JLCPCB JLC04161H-7628, from the JLCPCB impedance page read on 19 November 2026.

| Layer | Material | Thickness | εr |
| --- | --- | --- | --- |
| L1, F.Cu | copper | 0.035 mm | |
| dielectric 1 | 7628 prepreg | 0.2104 mm | 4.4 |
| L2, In1.Cu | copper | 0.0152 mm | |
| core | FR4 | 1.065 mm | 4.6 |
| L3, In2.Cu | copper | 0.0152 mm | |
| dielectric 3 | 7628 prepreg | 0.2104 mm | 4.4 |
| L4, B.Cu | copper | 0.035 mm | |

JLCPCB says to use 7.1 mil as the dielectric height for an outer controlled-impedance track on this stack, and 8.1 mil for an inner track. The USB 90 Ω width has to come from JLCPCB’s calculator when a board is ordered. No third-party width is adopted here.

Finished thickness is the 1.6 mm general setting. Loss tangent 0.02 is the value written into the board file, not a JLCPCB specification.

## Design rules

These are the rules in `kicad/placement_finder.kicad_pro`. They are the design minimums, not a claim that the fabricator cannot go tighter.

| Rule | Value |
| --- | --- |
| Clearance | 0.20 mm |
| Copper to board edge | 0.30 mm |
| Hole clearance | 0.25 mm |
| Hole to hole | 0.25 mm |
| Minimum through hole | 0.20 mm |
| Minimum track | 0.20 mm |
| Via annular ring | 0.10 mm |
| Minimum via diameter | 0.45 mm |

## Where each net is allowed to go

L1 carries signals. L2 is the battery-return ground plane and nothing else: `GND` only. The pour must stop at the keep-outs below and must not pick up `REED_RET`, `UP_RET`, `DN_RET` or `GND_CAN`. L3 is split power: `+3V3`, `+5V`, `+12V_MCU` and `+12V_COIL`, each staying in its own domain. L4 is the spare signal layer for the crossings L1 cannot make.

The netlist already keeps those five returns on separate pins. An isolator or a module that has one pin on `GND` and another pin on an isolated return is the barrier, not a short.

Keep-outs, every copper layer, tracks, vias, pads and pours forbidden, footprints allowed:

- Antenna. x 18 to 62 mm, y 51 to 68.5 mm. The board notch is x 28 to 52 mm, from y 55 mm up to the top edge. Espressif’s module keep-out is no copper on any layer. The 3.3 V feed to the module is at least 25 mil on the main rail and 20 mil at the VDD3P3 pins, from the Espressif layout example.
- Reed barrier. x 16.2 to 21.2 mm, y 33.2 to 40.8 mm. This is the MEJ2 primary-to-secondary gap for U4. Do not route across it and do not pour across it.
- CAN barrier. x 57.0 to 62.2 mm, y 38.8 to 46.6 mm. Same rule for U9. `GND_CAN` stays on the secondary side. No 120 Ω between CANH and CANL. NET-S has a connector pin and no PCB net.

Relay coils stay on `+12V_COIL` and the low-side FET nets. One Finder coil is 42 mA. The coil path and the contact path are different currents. `F_MCU` and `F_COIL` are on the supply branches and do not protect `UP_COM`, `UP_NO`, `DN_COM` or `DN_NO`. Those four nets have no fuse and no suppressor on this board. The SS14 diodes are across the Finder coils only.

The Finder DC1 rating, 10 A resistive at 30 V, is not the Lofrans contactor load and is not the track size. Contact copper is sized for a provisional 12 V, 2 A control load. IPC-2221 external, 1 oz, 10 °C, gives about 0.78 mm for 2 A, so the 0.20 mm minimum track is not enough for that load. The 0.20 mm clearance rule is the spacing used with that 12 V assumption. It is not a spacing for a circuit above 30 V. The real Lofrans current, voltage and inductive energy are installation measurements. No new measurement was made in this pass, so the tracks stay at 0.80 mm.

Direction-sense tracks stay with their own return. The optocoupler LED current comes back on `UP_RET` or `DN_RET`. The phototransistor emitter is `GND`. Those two domains meet only inside the optocoupler. J_SENSE pin 3 is the unused pin between the two returns.

USB is the ESP32-S3 native device port. The exported netlist has:

- CC1 is J_USB A5 and R15, 5.1 kΩ to `GND`. CC2 is J_USB B5 and R16, 5.1 kΩ to `GND`. That is Rd. The board does not present Rp and does not source VBUS.
- D+ is U3 pin 14, R17 22 Ω, then `USB_DP_C`. D− is U3 pin 13, R18 22 Ω, then `USB_DN_C`. `USB_DP_C` is J_USB A6/B6 and U_ESD pins 1 and 6. `USB_DN_C` is J_USB A7/B7 and U_ESD pins 3 and 4. The 22 Ω resistors stay between the ESD device and the module. The module’s internal pull-up is the full-speed pull-up. There is no external 1.5 kΩ.
- U_ESD is ST USBLC6-2SC6 in SOT-23-6. ST DS4260 lists 3.5 pF maximum from an I/O pin to ground and 1.7 pF maximum between the I/O pins, and it is specified for USB 2.0. The ESP32-S3 port is full speed. Pin 2 is `GND`. Pin 5 is `USB_VBUS`, not `+5V`.
- `USB_VBUS` is J_USB A4, A9, B4, B9, `TP_VBUS` and U_ESD pin 5. It has no pin on `+5V` or `+3V3`. There is no VBUS-detect GPIO. No power-path switch was added.
- `USB_SHIELD` is the shell pad, R19 1 MΩ and C13 100 nF to `GND`. It is not a hard chassis bond.
- SBU1 and SBU2 are no-connects.

A cable that brings 12 V and USB at the same time has no copper path from `USB_VBUS` onto the onboard 5 V rail, and the 5 V rail has no path onto VBUS. That is the netlist as exported. It is not a test with both supplies plugged in.

The ESP32-S3-WROOM-1 has no VBUS pin. USB D− is module pin 13 and USB D+ is module pin 14. The PHY runs from the module 3.3 V rail, and that rail is produced from the 12 V input by the buck. The board can enumerate as a self-powered device while `USB_VBUS` stays off `+5V` and `+3V3`. It does not source VBUS. The CC pins present Rd, not Rp.

There is still no VBUS-detect GPIO. `TP_VBUS` is the only place `USB_VBUS` can be probed. Firmware cannot tell that a host is attached, and it cannot hold the internal D+ pull-up off until VBUS is present. A self-powered device is supposed to enable that pull-up only while VBUS is present. That limit stays. No power path was added.

## Trace width

IPC-2221 external, k = 0.048, 1 oz taken as 1.378 mil, 10 °C rise. This is a sizing estimate, not a temperature-rise test.

| Current | External width | What it covers |
| --- | --- | --- |
| 42 mA | about 0.004 mm, so the 0.20 mm rule governs | One Finder coil |
| 0.5 A | about 0.12 mm, so the 0.20 mm rule governs | MEJ2S0505 primary at full load |
| 2 A | about 0.78 mm | Provisional contact load. Drawn at 0.80 mm. Also the MCU fuse branch as a fault rating |
| 10 A | about 7.2 mm | The Finder resistive contact rating. Not used as the track size |

## What the checks found

Schematic ERC, KiCad 10.0.8, 19 November 2026, `docs/erc_report.txt`: 1 message, 0 errors, 1 warning. Symbol origins and wire ends are on the 1.27 mm electrical grid, so the previous 570 `endpoint_off_grid` warnings are gone. The remaining warning is U5 pin 5, `GND2`, on `REED_RET` instead of `GND`. That is the isolation. It is not connected to MCU ground.

Earlier ERC reports of zero violations, including revision 0.4, were produced before the schematic symbols were actually instantiated. Revision 0.5 then reported 571 warnings, of which 570 were the millimetre grid.

PCB DRC of the revision 0.7 route, kept as `docs/drc_placement_80x60.txt`, KiCad 10.0.8: 18 warnings, 261 unconnected items, 0 footprint errors. The revision 0.8 result is below. The warning list has no short, no clearance error and no solder-mask bridge. USB A1, A12, B1 and B12 are `GND`. A4, A9, B4 and B9 are `USB_VBUS`. The shield pad is `USB_SHIELD`. No exclusion was added.

The 18 warnings are 2 silkscreen-to-edge on the USB shell, 4 silkscreen-over-copper on the library artwork of Q_MCU, Q_COIL and SW_BOOT, and 12 library-copy mismatches. Reference designators were moved from F.SilkS to F.Fab. A compare of the placed pads with the library files, after ignoring position, uuid, reference text and value, matched the pad geometry. KiCad still reports a local override on U3, both SOT-223 FETs, the three KF350 terminals, the three JST headers, SW_BOOT, D40 and D80. No pad size or drill on those footprints was changed.

## Contact route

`UP_COM`, `UP_NO`, `DN_COM` and `DN_NO` are routed at 0.80 mm. J_CONTACT was not moved. The relays were not turned. The connector already sits against J_PWR and U4, and turning a Finder 40.31 so the contact pins face the connector puts those pins into the connector courtyard. The open copper is the gap between the two Finder pin rows.

The four tracks run on B.Cu in that gap. Centres are y = 18.15, 19.20, 20.25 and 21.45 mm, at x = 6.25, 7.40, 8.50 and 9.70 mm. `UP_COM` stays on B.Cu from the connector pin to the relay pin. The other three leave the connector on F.Cu and change layer on a 0.45 mm via with a 0.20 mm drill, because a bottom stub would cross the vertical track of the pin above it. The `DN_NO` via is at x = 8.50 mm, clear of R94. The tracks do not enter the reed barrier, the CAN barrier, or the antenna keep-out.

DRC after that stage alone, `docs/drc_rev08_contacts.txt`: 18 warnings, 274 unconnected items, no short, no clearance error, no hole error. The four contact nets are absent from the unconnected list. The unconnected count is higher than revision 0.7 because that pass's partial tracks were removed before the contacts were drawn.

## Signal route after the contacts

`scripts/route_initial.py` then walked isolation returns, power, coil and interlock nets, reed and direction, CAN, USB, and the remaining GPIO. Tracks stay on F.Cu and B.Cu. Nothing was drawn on In1.Cu or In2.Cu. `GND` was not drawn: it is the L2 plane, and kicad-cli does not fill a zone. The antenna keep-out, both barriers and the notch still reject tracks.

Fully linked: the four contact nets, `AND_Y`, `COIL_RAIL_OK`, `TWAI_RX` and `LED_B_K`. Seventy-seven other nets have a partial link or no link. Detail is in `docs/route_initial.txt`. The coil low sides `UP_LOW` and `DN_LOW` have no link. Their pads sit on the same pin rows the 0.80 mm contact tracks now occupy. `REED_GPIO` has no link: the ESP32 pad column only allows a short escape, and the reed barrier sits between that escape and the isolator. `CAN_H` and `CAN_L` have no link. `VIN_12` has no link.

An earlier signal pass in this revision placed `GND_CAN` and `ISO_5V` vias against the Q_MCU tab. That pass was not kept. The board on disk is the pass below.

PCB DRC of the kept route, `docs/drc_rev08_routed.txt`, KiCad 10.0.8, 19 November 2026: 18 warnings, 208 unconnected items, 0 footprint errors. The warnings are the same 2 silk-to-edge, 4 silk-over-copper and 12 library-copy items as revision 0.7. There is no short, no clearance error, no hole error and no isolation-boundary short. `GND`, `UP_RET`, `DN_RET`, `REED_RET` and `GND_CAN` still share no pad.

The outline stays 80 × 69 mm. The contact copper fits without growing it. The open nets are a density and escape problem, not a reason found here to change the outline.

`scripts/assign_nets.py` stamped 344 pads from the 109-net export and skipped nothing. Every schematic reference that is on the board has the same footprint field as the placed footprint. `SH_REED` is the loose shunt and has no footprint. `H1` to `H4` are mounting holes and are not schematic symbols.

The five returns `GND`, `UP_RET`, `DN_RET`, `REED_RET` and `GND_CAN` still share no pin.

## Footprints checked against the drawings

- KF350. The Cixi Kefa drawing states 3.50 mm pitch, 0.80 mm pin and a 1.0 mm PCB hole. The project footprint drill is 1.0 mm. The courtyard is still the 4Ucon envelope, not a traced body.
- MEJ2. The Murata recommended-footprint extract pairs 0.6 ± 0.15 mm with 0.024 ± 0.006 inch, and that pair is the hole. The drill is now 0.6 mm. The pad is 1.8 mm because the extract does not label a pad diameter. Pin 6 is not fitted and has no hole. The courtyard is still the 19.65 × 10.05 mm body centred on the pin span. The extract does not give a pin-1 to body-end dimension, so that offset is not resolved.
- USB-C. The placed land is the KiCad footprint for Hroparts TYPE-C-31-M-12, which is the selected connector. The pads were not remeasured against a fresh drawing in this pass.
- Relays. Finder 40.31, KiCad `Relay_SPDT_Finder_40.31`. Hand-fitted. The contact rating used for track width is the provisional 2 A above, not the 10 A resistive DC1 figure.
- Switches. Reset and boot are TL3342F160QG on the KiCad TL3342 land. The reed mode part is the 2.54 mm header, not a slide switch.
- LEDs. Three 0603 lamps, not one RGB package. D_B is LTST-C190TBKT, driven from +5V through 1 kΩ and a 2N7002BK. The gate is GPIO17.

## Not released for routing

- KF350 body outline is still the 4Ucon envelope.
- MEJ2 pin-1 to body-end offset is still not on the drawing extract used here.
- Littelfuse 0466001.NR and branded SMAJ18A still have no quantity on the pages that were read.
- Contact tracks are drawn at the provisional 0.80 mm. The measured Lofrans current, voltage and inductive energy are still open, so the width was not changed.
- USB differential width waits on the JLCPCB calculator for this stack.
