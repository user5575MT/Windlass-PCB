# Progress log

Status of this repository: design only. No board has been ordered. No firmware has been modified, flashed, or deployed. No vessel wiring has been changed. No Gerber, drill, or position file has been written.

## 2026-11-23 — Direction buffers

`kicad11/windlass_install.kicad_pcb` was not edited. It is the checkpoint from before this change and no longer matches the schematic. The buffered board is `kicad11/windlass_install_v2.kicad_pcb`.

`U12` and `U15` are Nexperia 74LVC1G34GW buffers on GPIO9 and GPIO10. `R60` and `R70` are 100 Ω, 1206, 250 mW. `Q_CLAMP_UP` and `Q_CLAMP_DN` are NX3008NBK. The Finder relays, the dry contacts, the series switch, the monostable, and the isolation barrier are unchanged. Firmware was not edited.

The ESP32-S3 high of 2.616 V is 0.616 V above the buffer’s 2.0 V VIH minimum. Through 100 Ω the switch input is about 3.12 V against the 3.0 V on-level, using the ZXMS 100 µA maximum published at 25 °C. With both requests high, each 100 Ω dissipates about 112 mW and the clamp holds the opposite input at about 0.05 V. An unpowered buffer leaks about 0.2 V into the 100 kΩ pulldown.

ERC at 4:19 pm Sydney time: 0 errors, 1 warning, the intentional U5 `GND1` on `REED_RET`. DRC at 4:18 pm Sydney time, after a zone refill: 0 violations, 0 unconnected pads. The title block says not for fabrication. No Gerber was written, no part was ordered, and nothing was flashed. The write-up is `docs/install_protection.md`.

## 2026-11-23 — Relay and contactor review

The schematic, `kicad11/windlass_install.kicad_pcb`, and the firmware were not edited. No Gerber was written, no part was ordered, and nothing was flashed.

The direction inputs fail the published on-level. ESP32-S3-WROOM-1 VOH minimum is 0.8 × VDD, measured at high impedance, which is 2.616 V on the AP63203 minimum of 3.27 V. The ZXMS6004FF on-level is 3.0 V. `R60` and `R70` at 1 kΩ drop about 0.10 V at the published 100 µA and would be adequate if the pin sat on the rail. They cannot close a gap that exists at 0 Ω. `Q_SERIES`, driven by the 74LVC1G123 through 100 Ω, does meet 3.0 V, at about 3.13 V. The correction, not drawn, is a 74LVC1G buffer on GPIO9 and GPIO10 and 100 Ω in place of the 1 kΩ.

The Finder 40.31 contact passes the Quick control circuit on the published bound. DC1 is 12 A at 24 V. With a freewheeling diode, DC13 life matches that. Without one, Finder’s approximation for a 40 ms L/R load is 6 A. Quick’s recommended fuse for the T6315-12 and T6415-12 coil is 2.5 A fast, and Quick does not publish the coil current. The Rev 002A manual does not describe a coil suppressor. One 1N5404 per coil, at the contactor, after confirming the housing has none, is the arrangement that uses the DC1 life. A shorted diode opens the control fuse and the contactor stays off.

The write-up is the review section of `docs/install_protection.md`.

## 2026-11-23 — Installation protection

The bench file `kicad11/windlass_bench.kicad_pcb` was not edited. The installation board is `kicad11/windlass_install.kicad_pcb`, copied from it and then reworked. The schematic is the shared one, so the bench file no longer matches it.

`Q_UP`, `Q_DN`, and `Q_SERIES` are Diodes ZXMS6004FFTA on the existing SOT-23 land. Pin 1 is drain, pin 2 is IN, pin 3 is source. `F_COIL` is Littelfuse 0466.250, 250 mA. `R60` and `R70` are 1 kΩ. `D61` and `D71` are gone. Nothing on the board joins COM to NO. The contactor diode is an installation part at the contactor. The series FET, the cross-clamps, the monostable, and the isolation barrier are unchanged. Firmware was not edited.

ERC at 3:32 pm Sydney time: 0 errors, 1 warning, the intentional U5 `GND1` on `REED_RET`. DRC at 3:41 pm Sydney time, after a zone refill: 0 violations, 0 unconnected pads. The title block says not for fabrication. No Gerber was written, no part was ordered, and nothing was flashed. The write-up is `docs/install_protection.md`.

## 2026-11-23 — Bench revision from the electrical review

`kicad11/windlass_cleared.kicad_pcb` was not overwritten. The corrections are on `kicad11/windlass_bench.kicad_pcb`.

U10 pin 10 is GND2 on `GND_CAN`. Pins 9 and 15 stay on `GND_CAN`. Pins 11 and 16 stay on `ISO_5V`. The join is on F.Cu, with no via. L20 is Bourns SRN6045-3R3Y. SRN4018-3R3M was not fitted: its 2.3 A saturation rating is below the AP63203 3.1 A peak-limit maximum. C30I is a 22 µF 25 V X7R 1210, C50 is a 3.3 µF 50 V X7R 1206, and C92 is a 100 nF 50 V X7R 0402. The 1 A coil fuse and the SMBJ18CA clamps were left in place and written down as bench-only restrictions.

ERC at 2:53 pm Sydney time: 0 errors, 1 warning, the intentional U5 `GND1` on `REED_RET`. DRC at 2:56 pm Sydney time: 0 violations, 0 unconnected pads. The title block still says not for fabrication and not for marine installation. B1–B8 are open. No Gerber was written, no part was ordered, and the prototype firmware was not edited. The write-up is `docs/electrical_review.md`.

## 2026-11-23 — Electrical review, nothing changed

The schematic, `kicad11/windlass_cleared.kicad_pcb`, and the integrated BOM were checked against the datasheets. No schematic, PCB, firmware, or part value was edited.

U10 pin 10 is GND2 on the ISO1042 and is tied to `ISO_5V`. Pins 9 and 15 are the same ground, on `GND_CAN`, so the isolated 5 V rail is shorted inside the package. That has to move before fabrication. A clean DRC does not see it. The power input, the coil interlock, the reed input, and the ESP32 straps otherwise match their datasheets. The 3.9 µH SRN4018 is not a Bourns ordering code, capacitor voltages are not specified, and B1–B8 are still measurements. The write-up is `docs/electrical_review.md`. The board is not for fabrication.

## 2026-11-23 — USB4105 ground-pad corners relieved

`kicad11/windlass_cleared.kicad_pcb` continues from the complete board. That file was not overwritten. The schematic was not edited. The connector stays the GCT USB4105.

A larger corner radius cannot make 0.25 mm. The corner of each ground pad that faces a locating hole was cut back so the copper is 0.28 mm from the hole. KiCad measures 0.280 mm. The cut is 0.0184 mm², about 2.7 percent of the pad. The tail width on the drawing is 0.45 mm inside a 0.60 mm pad. The shell stakes and the peg holes were not moved. Paste and mask use the same outline.

DRC at 12:33 pm Sydney time is `kicad11/drc_cleared.rpt`: 0 violations and 0 unconnected items. ERC is `kicad11/erc_cleared.rpt`: 0 errors and 1 warning. The hole rule stays 0.25 mm. JLCPCB has not reviewed the board. A hole shifted by their published ±0.075 mm still leaves about 0.205 mm. Adding the through-hole oversize as well is arithmetic on a separate row and can leave about 0.140 mm. This board is not for fabrication. B1–B8 are open. The write-up is the “Decision” section of `docs/usb4105_jlcpcb.md`.

## 2026-11-23 — JLCPCB has not accepted the USB4105 land

The PCB and the schematic were not edited. JLCPCB’s capability table, retrieved the same day, lists NPTH-to-track clearance as 0.2 mm, hole position as ±0.075 mm, and through-hole size as +0.13 / −0.08 mm. A 1.6 mm FR-4 thickness is on that list, and the Ø0.65 mm holes are above the 0.50 mm NPTH minimum. The GCT recommended land is 0.1944 mm from pad to hole, which is under the published 0.2 mm row before those tolerances. The table has no USB4105 exception. Lowering the KiCad rule from 0.25 mm to 0.20 mm would not clear the four errors. No horizontal 16-pin replacement in the KiCad library keeps 0.20 mm after a 0.075 mm hole shift on a 1.6 mm board. The write-up is `docs/usb4105_jlcpcb.md`. The next action is to ask JLCPCB whether they will build this land. The board is not for fabrication.

## 2026-11-23 — Complete copy, reed nets joined on F.Cu

`kicad11/windlass_complete.kicad_pcb` continues from the validated board. The validated file, the finished file, the routed file, and the original `kicad11/windlass.kicad_pcb` were not overwritten. The schematic was not edited, and the board was not autorouted again.

JP_REED moved to (104.00 mm, 137.58 mm) and turned 180°, so the dry contact is the north pin, and C22 moved 2 mm north. `LOFRANS_NODE`, `REED_ISO`, and `DRY_A` now each join their pads on F.Cu: JP_REED pin 1 to D20 pin 2, JP_REED pin 2 to R23 pin 1, and JP_REED pin 3 to J_REED pin 3. The `REED_RET` wall is split and rejoined east of the header so it stays clear of those new tracks. `REED_3V3` keeps its original link. No barrier net has a via, and barrier copper stays on F.Cu. The slots and the inner keepouts are unchanged.

The connector stays the GCT USB4105. No horizontal top-mount USB 2.0 footprint in the KiCad library both matches a manufacturer drawing and clears the 0.25 mm hole rule on a 1.6 mm board. The lands that do clear it are mid-mount, vertical, power-only, or made for a thinner board. The four 0.1944 mm hole-clearance errors remain, and the hole rule stays 0.25 mm.

DRC at 8:51 am Sydney time is `kicad11/drc_complete.rpt`: 0 shorts, 0 clearance errors, 0 under-width tracks, 0 unconnected items, and 4 hole-clearance errors. ERC is the validated run on the unchanged schematic: 0 errors and 1 warning. This board is not for fabrication. B1–B8 are still open. The write-up is the “Complete copy” section of `docs/freerouting_trial.md`.

## 2026-11-23 — Validated copy, DRY_A left on F.Cu

`kicad11/windlass_validated.kicad_pcb` continues from the finished board. The finished file, the routed file, and the original `kicad11/windlass.kicad_pcb` were not overwritten. The schematic was not edited.

A two-via jump of the `DRY_A` segment that blocks `LOFRANS_NODE` and `REED_ISO` was measured and rejected. The segment sits inside the reed inner keepout. The only exits that stay outside that keepout and outside the isolation slots cross onto the logic side, where a barrel would sit 0.20 mm from the inner ground pour and the inner 3.3 V pour. `DRY_A` is the standalone dry contact and shares `REED_3V3` and `REED_RET` with the Lofrans input, so that via was not added. Both nets stay unconnected, on F.Cu.

The four dangling vias were removed. The `+12V  GND` and `SW  SW  IGN  IGN` labels were moved clear of the connector silk and of D61 pad 2. The GCT USB4105 land is unchanged: the drawing’s own gap is 0.1944 mm, the layout tolerance is ±0.05 mm, and the 0.25 mm hole rule still reports all four gaps.

DRC at 7:23 am Sydney time is `kicad11/drc_validated.rpt`: 0 shorts, 0 clearance errors, 0 under-width tracks, 2 unconnected items, and 4 hole-clearance errors. ERC on the unchanged schematic is 0 errors and 1 warning (U5 `GND1` on `REED_RET`). This board is not for fabrication. B1–B8 are still open. The write-up is the “Validated copy” section of `docs/freerouting_trial.md`.

## 2026-11-22 — Finished copy of the routed board

`kicad11/windlass_finished.kicad_pcb` continues from the FreeRouting copy. The routed file and the original `kicad11/windlass.kicad_pcb` were not overwritten. The schematic was not edited. The board was not autorouted again.

`GND_CAN` now reaches U10 pin 15 on F.Cu at 0.40 mm, around the pin row and the isolation slot, with no via. The seventy under-width segments were widened to their class widths. One `PG` segment between U13 pins 2 and 4 was centered so both gaps are 0.200 mm. The four `GND` zone-to-itself reports were four real pour fragments, each holding a ground pad (the two USB ground pairs, R15 pin 2, and U14 pin 3) that had no connection to the main plane. A via on each joins them to the ground pours. `LOFRANS_NODE` and `REED_ISO` are still open: the only F.Cu gap between those pads and the rest of their nets is a `DRY_A` track, and all three nets are barred from vias.

DRC at 8:57 pm Sydney time is `kicad11/drc_finished.rpt`: 0 shorts, 0 clearance errors, 0 under-width tracks, 2 unconnected items, and 4 hole-clearance errors. The hole errors are the GCT USB-C land, 0.1944 mm against a 0.25 mm rule. That gap is not waived on this copy. U3’s nine 0.50 mm thermal vias are unchanged. This board is not for fabrication. B1–B8 are still open. The write-up is the “Finished copy” section of `docs/freerouting_trial.md`.

## 2026-11-22 — FreeRouting on a separate copy

`kicad11/windlass_routed.kicad_pcb` is a copy of the integrated board, routed with FreeRouting 2.5.0 (the JAR on OpenJDK 25) after the net classes were set to the widths the layout already required. The original `kicad11/windlass.kicad_pcb` was not overwritten. The schematic was not edited.

The route ran from 7:03 pm to 7:06 pm Sydney time. DRC after zone refill, at 7:12 pm, is in `kicad11/drc_routed.rpt`: 0 shorts, 0 clearance errors, 0 hole-clearance errors, and 0 drill errors. Three signal connections are still open (`LOFRANS_NODE`, `REED_ISO`, `GND_CAN`), all on nets that are held on F.Cu with no vias. Seventy tracks are narrower than their class. The seventeen isolator-side nets have no vias. The four relay-contact nets are 1.20 mm and may use vias. U3’s twelve 0.20 mm thermal drills were replaced, on the copy, with nine 0.50 mm drills inside the existing ground pad. The USB-C land was not redrawn. This board is not for fabrication. B1–B8 are still open. The write-up is the “Routed copy” section of `docs/freerouting_trial.md`.

## 2026-11-22 — FreeRouting trial, board unchanged

FreeRouting 2.5.0 was run on a copy of `kicad11/windlass.kicad_pcb` with the custom-router copper removed. The schematic and `kicad11/windlass.kicad_pcb` were not modified. The native Linux CLI hangs on a GraalVM serialization error (`ComponentOutline`). The JAR, on OpenJDK 25.0.5.1, completed both trials.

With every net free to use all four layers, KiCad DRC after import showed 0 shorts, 0 clearance errors, and 0 open signal nets. Fourteen isolated nets still received through vias. With those 21 nets locked to F.Cu in the Specctra file, the vias disappeared and one signal stayed open (`REED_ISO` at U5 pin 2). That import also has one short (`VIN_12` on In1.Cu against an `IGN_B` via) and one 0.166 mm clearance on the same pair. Both runs left about 100 tracks at 0.15 mm, under the 0.20 mm rule. The report is `docs/freerouting_trial.md`.

## 2026-11-22 — Integrated redesign, not for fabrication

The revision 0.8 placement in `kicad/` is unchanged and is kept as the reference. A new schematic and a new four-layer board are in `kicad11/`. The outline is 200 × 160 mm. The relays stay on this board. The XOR, the AND, the second buck, the 5 V rail, and the mid-mount USB-C footprint are gone.

ERC on `kicad11/windlass.kicad_sch` is 0 errors and 1 warning. The warning is U5 pin 4, `GND1`, on `REED_RET`. That net is not joined to `GND`.

DRC on `kicad11/windlass.kicad_pcb`, after a zone refill at 10:58 Sydney time on 22 November 2026, is not clean. The report is `kicad11/drc.rpt`: 351 violations, 27 unconnected items, 4 shorts, 11 clearance errors, 4 crossing tracks, and 180 dangling vias. The shorts join `USB_VBUS` to `CC2`, `GND` to `USB_SHIELD`, `+3V3` to `NQ`, and `GND_CAN` to an unconnected pad of U10. This board is not for fabrication. Measurements B1–B8 are still open. No production file was written.

## 2026-11-22 — Architecture review, routing stopped

The 80 × 69 mm four-layer placement is not to be routed further. The recommendation is a two-layer controller with a dry-contact reed, two optocouplers, and one isolated CAN transceiver, and a separate relay board only after measurement B1. The XOR, the AND, the fitted reed isolator supply, the second buck, the Finder relays, and the mid-mount USB-C footprint come off the first article. No schematic was regenerated and no copper was added. See `docs/design_simplification.md`.

## 2026-11-19 — Revision 0.8

Relay-contact routing, the reed-valid proposal, and the USB enumeration note. The outline stays 80 × 69 mm. No fabrication output was written. No order was placed. The prototype firmware was not modified, flashed, or deployed. The schematic was not regenerated.

`UP_COM`, `UP_NO`, `DN_COM` and `DN_NO` are routed at 0.80 mm on the bottom, in the gap between the Finder pin rows. J_CONTACT and the relays were not moved. Three vias, 0.45 mm with a 0.20 mm drill, take the lower connector pins onto that layer. The tracks do not cross either isolation barrier.

DRC after the contacts, `docs/drc_rev08_contacts.txt`: 18 warnings, 274 unconnected items, no short and no clearance error. DRC after the following signal pass, `docs/drc_rev08_routed.txt`: 18 warnings, 208 unconnected items, no short, no clearance error and no isolation short. The 18 warnings are the same silk and library-copy items as revision 0.7. Fully linked nets are the four contacts, `AND_Y`, `COIL_RAIL_OK`, `TWAI_RX` and `LED_B_K`. `GND` is still the unfilled L2 plane.

A valid reed-power signal is required. Direction sense does not reject a rising edge caused by the field supply falling while the windlass is moving. The spare ISO7721 channel points the wrong way, so it cannot carry that signal. The proposed second isolator is documented and not fitted. The 30 ms debounce is a chatter filter. The magnet duty is still unmeasured. Enumeration from the 12 V rail, with `USB_VBUS` isolated, is documented in `docs/routing_feasibility.md`. There is still no VBUS-detect GPIO.

## 2026-11-19 — Revision 0.7

Status LEDs, USB ESD, the reed startup note, silkscreen, and a first route. The outline stays 80 × 69 mm. No fabrication output was written. No order was placed. The prototype firmware was read and not modified, flashed, or deployed.

D_R and D_G stay on GPIO15 and GPIO16 through 680 Ω. D_B is LTST-C190TBKT from the onboard 5 V rail through 1 kΩ and a 2N7002BK. The gate is GPIO17 and has no DC path to 5 V. U_ESD is USBLC6-2SC6 on the connector side of the 22 Ω resistors. Its VBUS pin is `USB_VBUS`, which is still separate from `+5V`.

ERC is 0 errors and 1 warning, the same U5 `GND2` warning on `REED_RET`. DRC is 18 warnings, 261 unconnected items, and 0 footprint errors. There is no short and no clearance error. The route drew 23 segments. `LED_R` is the only fully linked net. Contact nets were left open because 0.80 mm did not find a clear path.

## 2026-11-19 — Revision 0.6

Electrical and footprint synchronisation of the 80 × 69 mm board. No copper was routed. No order was placed. The prototype was not touched.

`SW_REED` is gone. `JP_REED` is a 2.54 mm 1×03 header: pin 1 `LOFRANS_NODE`, pin 2 `REED_ISO`, pin 3 `DRY_A`. `SH_REED` is one loose shunt, default on pins 1–2, and it is not a footprint. U8 and U12 are on the SOT-353 land. `R_R`, `R_G` and `R_B` are on the board. The MEJ2 hole is 0.6 mm. The pin-1 to body-end offset is still not on the drawing extract.

ERC is 0 errors and 1 warning. The warning is U5 pin 5, `GND2`, on `REED_RET`. It is not joined to `GND`. The 570 off-grid warnings from revision 0.5 are gone. DRC is 0 errors, 312 warnings and 264 unconnected items. The unconnected items are unrouted nets. Details are in `docs/routing_feasibility.md`, `docs/connector_pinout.md` and `docs/component_availability.md`.

## 2026-11-19 — Revision 0.5

Electrical check of the instantiated schematic, then a net stamp onto the 80 × 69 mm placement. No copper was routed. No order was placed. The prototype was not touched.

The outline stays 80 × 69 mm. J_SENSE is the 5-pin JST XH with pin 3 unused, so `UP_RET` and `DN_RET` are not adjacent. The reed switch graph, the stackup, the DRC and the stock readings are in `docs/connector_pinout.md`, `docs/routing_feasibility.md` and `docs/component_availability.md`.

ERC is 0 errors and 571 warnings. The warnings are the millimetre grid plus the intentional `REED_RET` connection on the isolator’s side-2 ground. PCB DRC after the net stamp has no clearance and no solder-mask errors. The eight USB-C pad errors were un-netted stacked pads and they cleared once A1/B12 were both `GND` and A4/B9 were both `USB_VBUS`. Two hundred and fifty-five unconnected items remain because there are no tracks.

Reports that said ERC found 0 violations, including the revision 0.4 line below, were written before KiCad instantiated the symbols. They are not the electrical result.

## 2026-11-19 — Revision 0.4

Six production connector footprints replace the headers. 80 × 60 mm holds those connectors and the large parts. The passives and switches need the outline to be 80 × 69 mm. Courtyard check is clear at that size. The ERC line recorded here was later found not to have instantiated the symbols. See revision 0.5. Copper is not routed. No order was placed.

## 2026-11-19 — Revision 0.3 placement check

MEJ2 footprint drawn from the Murata pin table. Copper keep-outs added for the antenna zone and both isolation gaps. Four 3.5 mm screw terminals fit on the 80 × 60 mm edges. The dry-contact, both direction-sense pairs, the ignition loop, the relay-power switch loop and the NMEA connector do not fit that edge. The board was not enlarged. Availability notes are in `docs/component_availability.md`. KiCad DRC on the revised 80 × 60 mm board reported 0 errors after the minimum hole was set to 0.2 mm. Twenty-six silkscreen and library-copy warnings remain in `docs/drc_placement_80x60_warnings.txt`. Schematic ERC is 0 violations. No order was placed.

## 2026-11-19 — Placement, not routing

Selected outline is 80 × 60 mm, four-layer, with the Finder 40.31 relays. A 90 × 60 mm arrangement of the same parts also clears and is not adopted. An Omron G5Q courtyard was placed on the 80 × 60 mm outline as a size study and was not substituted. KiCad PCB DRC reported no courtyard overlaps. The twelve reported errors are 0.2 mm drills in the ESP32-S3-WROOM-1 footprint. No copper was routed. See `docs/mechanical_plan.md`.

## 2026-11-18 — Phase A inspection

### Commands

```text
kicad-cli version
```

Result: `kicad-cli` is not on PATH. `where.exe kicad-cli` and `where.exe kicad` found nothing. No KiCad directory under `C:\Program Files` or `%LOCALAPPDATA%\Programs`. Winget lists `KiCad.KiCad` 10.0.8 as available and not installed. ERC/DRC cannot be run until KiCad is installed. No schematic files were invented to stand in for a KiCad project.

Workspace `C:\Users\thoma\Windlass-PCB` was empty at inspection.

### Read-only sources (not modified)

| Source | What it established |
| --- | --- |
| `C:\Users\thoma\OneDrive\Desktop\WindlassProject\WindlassController\src\main.cpp` | Working controller firmware. Reed GPIO27, UP sense GPIO25, DOWN sense GPIO26. Opto outputs need 3.3 V pull-ups. `ENABLE_RELAY_CONTROL` defaults to 0. Bench relay pins GPIO32/33, active-LOW. Command TTL default 300 ms (`RUN_TTL_DEFAULT_MS`), clamp 150–1000 ms. |
| `C:\Users\thoma\OneDrive\Desktop\WindlassProject\README.md` | PC817 input loading previously pulled the Lofrans reed idle from 3.22 V to 1.5 V. README pin text (UP GPIO26, DOWN GPIO25) disagrees with `main.cpp`. Relays must stay disconnected in that project. |
| `C:\Users\thoma\OneDrive\Desktop\WindlassProject\WaveshareReceiver\src\main.cpp` | Separate ESP32-S3 publishes toward NMEA. TWAI pins in that tree are GPIO15/16. Not this PCB. |
| Espressif ESP32-S3-WROOM-1/1U datasheet (documentation.espressif.com module datasheet) | N16 = 16 MB quad flash, no PSRAM, −40 to 85 °C. TWAI controller present (ISO 11898-1). GPIO35–37 unavailable only on octal-PSRAM variants. Strapping: GPIO0, GPIO3, GPIO45, GPIO46. EN must not float. USB on GPIO19/20. |
| Espressif ESP32-S3 hardware design guidelines, PCB layout | PCB-antenna clearance at least 15 mm inside the housing. No copper in the module keepout on any layer. Power traces to the module 3.3 V pins at least 20–25 mil on the cited 4-layer example. |
| LCSC / JLCPCB product pages retrieved 2026-11-18 | `ESP32-S3-WROOM-1-N16` is LCSC C2913199. Page showed about 1201 in stock, minimum 1, JLCPCB assembly type extended / standard PCBA only. `ISO1042BDWR` is LCSC C2671499, SOIC-16, page showed about 217 in stock. Stock is a snapshot, not a reservation. |

### Not found in the inspected firmware

- A hardware watchdog that removes coil power.
- An ignition or engine-permissive input pin.
- A measured UP/DOWN contact current, common, or freewheel arrangement.
- A KiCad symbol, footprint, or stackup.

Those items stay OPEN. See `assumptions_and_open_questions.md`.

### Files written this session

- `docs/architecture.md`
- `docs/requirements.md`
- `docs/interface_control_document.md`
- `docs/assumptions_and_open_questions.md`
- `docs/hazard_analysis.md`
- `docs/pin_allocation.md`
- `docs/traceability_matrix.md`
- `docs/progress_log.md`

## 2026-11-18 — Rev 0.1 schematic

KiCad 10.0.8 installed at `%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe`.

```text
python scripts\build_schematic.py
kicad-cli sch erc --severity-all --exit-code-violations -o docs\erc_report.txt kicad\windlass.kicad_sch
```

Result: `Found 0 violations` after the test-pad rebuild. Report: `docs/erc_report.txt`. Every global label is used at least twice (`scripts/count_labels.py`). KiCad's default profile still ignores a few checks (SPICE, footprint-filter mismatch, four points joined); none of those fired as errors.

Sheets: `kicad/power.kicad_sch`, `esp32`, `reed`, `direction_sense`, `relay_control_and_interlock`, `isolated_nmea2000`, `connectors_status_service`, root `windlass.kicad_sch`.

Confirmed from the prototype and drawn: switched +12 V NO contacts in parallel; direction sense is two opto channels whose returns are not joined to each other or to ESP32 ground; reed is a high-Z digital isolator, not a PC817 LED; NMEA side-2 ground is not the ESP32 ground; NET-S is no-connect; no terminator.

Still OPEN at the end of rev 0.1, and marked that way on the sheet: fuse, TVS, ideal-diode FET, buck, coil FET, relay MPN and current, flyback diode, direction resistor, both isolated DC-DC modules, AP2112 thermal sign-off. No Lofrans schematic was found to close those.

## 2026-11-18 — Rev 0.2 schematic

Same commands as rev 0.1. ERC again `Found 0 violations`. Label check: no global label used only once. Review: `docs/design_review.md`.

Drawn since 0.1: 74LVC1G123 heartbeat (about 330 ms typical) AND-ed into the series coil FET, replacing the fitted 0 Ω bypass; ISO7721 bias resized for ±10 µA leakage; SPDT reed mode so the dry-contact pull-up cannot reach the Lofrans pin; MCU and coil 12 V branches split; AP2112 removed in favour of AP63203 and AP63205; both isolated supplies are Murata MEJ2 parts with the 5.2 kVDC / 2.4 kVDC figures cited. Prototype firmware was not modified. Layout was not started.

Still OPEN at that point: contactor current and the coil-branch fuse, FET, TVS, and flyback; direction-sense resistor; reed source impedance; load-dump energy; PCB creepage; JLCPCB stock of the Murata modules at order time.

## 2026-11-19 — Rev 0.2 coil parts and the remaining checks

Same generate, label, and ERC commands. ERC report dated 2026-11-19: 0 errors, 0 warnings. No global label is used only once.

Relay is Finder 40.31.7.012.0000, hand-fitted through-hole. Coil figures from the series table: 288 Ω, 42 mA, 8.8 V to 18 V, 7 ms / 3 ms. Contact figure used: DC1, 10 A at 30 V. AC15 at 230 V AC is not used as a 12 V DC inductive rating. Installation stays blocked until the Lofrans control current and inductive energy are measured.

Coil path completed from that coil current: NX6008NBK drivers and series FET, SS14 flyback, 1 A fuse 0466001, DMP6023LE, SMAJ18A. SMAJ18A is still not load-dump protection. Reed load is the single 47 kΩ, about 70 µA, with 1 nF. Heartbeat contract is `docs/firmware_heartbeat_contract.md`. Placement intent is `docs/mechanical_plan.md`. Prototype firmware was not modified. No layout and no fabrication files.
