# FreeRouting trial on the integrated board

The schematic and `kicad11/windlass.kicad_pcb` were not modified. No firmware was changed, nothing was flashed, and no Gerber, drill, or position file was written. The working copies and the session files stayed in `/tmp/windlass-fr/`.

The question was whether FreeRouting 2.5.0 can finish the copper that the custom router left in `kicad11/drc.rpt`. It can connect the ordinary nets. It does not yet produce a board that meets the isolation rule and the 0.20 mm minimum width together.

Times below are Australia/Sydney (UTC+11).

## What the 351 violations are

`kicad11/drc.rpt` was written at 10:58 on 22 November 2026. The file has three sections. The 351 are the first section. The 27 unconnected pads and the 140 footprint items are separate and are not part of that 351.

| Count | Check | Cause |
| ---: | --- | --- |
| 180 | `via_dangling` | Fanout vias with copper on one layer |
| 76 | `track_dangling` | Routes that stop short of the pad |
| 37 | `hole_clearance` | Vias and tracks dropped on the USB-C mounting holes. Four of these are the connector's own GND pads against its NPTH holes (0.194 mm, rule 0.25 mm) |
| 12 | `drill_out_of_range` | U3 pad 41 thermal holes are 0.20 mm; the board minimum is 0.30 mm. Footprint against the rule, independent of the router |
| 11 | `clearance` | Tracks and vias closer than 0.20 mm |
| 9 | `hole_to_hole` | Two vias of the same net placed on top of each other |
| 6 | `silk_edge_clearance` | U5, U6, U7 reference silk against the isolation slots |
| 4 | `tracks_crossing` | Tracks of different nets crossing on one layer |
| 4 | `shorting_items` | `USB_VBUS` to `CC2`, `GND` to `USB_SHIELD`, `+3V3` to `NQ`, `GND_CAN` to an unused pad of U10 |
| 4 | `items_not_allowed` | Vias inside the inner-layer isolation keepouts |
| 4 | `silk_overlap` | J_PWR and J_PERM labels over the connector silk |
| 3 | `solder_mask_bridge` | Mask openings on three of the shorts above |
| 1 | `silk_over_copper` | D61 silk over the mask opening |

The 27 unconnected items are unfinished nets (`+3V3`, `REED_ISO`, `DN_NO`, `DRY_A`, `USB_SHIELD`, and several others). One of them is the F.Cu GND zone reported against itself.

The 140 footprint items are 136 id mismatches (`C_0805_2012Metric` stored without the library prefix, same land pattern as the symbol) and 4 mounting holes that are on the board and absent from the schematic.

## What has to be gone before an autorouter runs

The tracks and vias are the defect. They were deleted on the copy. Footprints, zones, rule-area keepouts, slots, and the outline stayed.

These do not have to be fixed for a routing trial, and they remain after a successful route: the 12 U3 drills, the silk items, the footprint-id mismatches, the four mounting holes, and the four USB-C pad-to-NPTH hole clearances.

KiCad's Specctra export does not carry two rules the layout depends on:

- The 21 barrier nets (`REED_RET`, `REED_3V3`, `REED_ISO`, `REED_SIG`, `LOFRANS_NODE`, `DRY_A`, `UP_RET`, `UP_FIELD`, `UP_LED_A`, `DN_RET`, `DN_FIELD`, `DN_LED_A`, `GND_CAN`, `ISO_5V`, `CAN_H`, `CAN_L`, `NMEA_SHIELD`, `UP_COM`, `UP_NO`, `DN_COM`, `DN_NO`) are allowed on every layer. A through via on any of them drills the In1 GND pour and the In2 +3V3 pour.
- Every net is in one class of width 0.20 mm and clearance 0.20 mm. The 1.2 mm contact width and the 0.80 mm 12 V width exist only in the custom router, so FreeRouting was not told them.
- The exported board rule also says SMD-to-SMD clearance 0.05 mm. That number was changed to 0.20 mm in the copy so the trial used the board's clearance.

## Whether FreeRouting can run here

OpenJDK 21 is installed. The published JAR is Java 25 bytecode. OpenJDK 25.0.5.1 (the Ubuntu 24.04 package `openjdk-25-jre-headless`) runs it. Egress is unrestricted, so the GitHub release downloaded.

The native binary `freerouting-cli` 2.5.0 for linux-x64 loads the design and then dies in the routing thread:

`com.oracle.svm.core.jdk.UnsupportedFeatureError: SerializationConstructorAccessor class not found for declaringClass: app.freerouting.board.model.items.ComponentOutline`

That is FreeRouting issue 957. The process stays up and never writes a session. A 2.6 build was not published on 22 November 2026. The JAR does not have this bug.

Command that completed, headless:

`java -Xmx6g -jar freerouting-2.5.0.jar --gui.enabled=false -de windlass.dsn -do windlass.ses -mp 40 -mt 3`

KiCad 10.0.8 has no `kicad-cli pcb export` path for Specctra. `pcbnew.ExportSpecctraDSN` wrote the design (88,487 bytes, four signal layers, four pours, 48 keepouts, no wires). `pcbnew.ImportSpecctraSES` read the session back onto the unrouted copy.

## Trial A — exported rules, every layer allowed

Started 5:03 pm, session saved 5:15 pm. Fanout escaped 317 of 338 SMD pins. Autoroute finished in five passes: score 999.87, 0 unrouted, 8 violations. Those 8 are pin-to-pin gaps on J_USB (`GND` against `USB_VBUS`) that FreeRouting calls unfixable because it does not move parts. KiCad's own DRC does not list those pad pairs.

KiCad DRC on the import, zones refilled, at 5:19 pm:

| Check | Trial A | Original board |
| --- | ---: | ---: |
| Shorts | 0 | 4 |
| Clearance | 0 | 11 |
| Crossing tracks | 0 | 4 |
| Open signal nets | 0 | 26, plus one zone artifact |
| Dangling vias | 0 | 180 |
| Dangling tracks | 0 | 76 |
| Router hole-to-hole | 0 | 9 |
| Keepout violations | 0 | 4 |
| Tracks at 0.15 mm | 101 | 0 (the rule is 0.20 mm) |
| U3 drill 0.20 mm | 12 | 12 |
| USB pad-to-NPTH | 4 | 4, inside the original 37 |
| Silk warnings | 11 | 11 |

The 4 unconnected lines in the new report are the F.Cu GND zone reported against itself.

Fourteen of the 21 barrier nets have through vias, including `REED_RET` (2), `CAN_H` (2), `CAN_L` (2), `UP_COM` (2), and `GND_CAN` (1). The pours are relieved, so KiCad reports no short, and the via barrel still passes through the ground plane. That is the isolation rule this board is built around. A per-net `(use_layer F.Cu)` in the session was ignored; FreeRouting applies `use_layer` on a net class.

## Trial B — barrier nets locked to F.Cu

The 21 nets were moved to a Specctra class with `(use_layer F.Cu)` and no via rule. Started 5:24 pm, session saved 5:29 pm. Autoroute used 23 passes and kept its best board: score 995.35, 1 unrouted, 9 violations. Fanout escaped 309 of 338 pins.

KiCad DRC on that import:

| Check | Trial B |
| --- | ---: |
| Shorts | 1 |
| Clearance | 1 |
| Copper-to-edge | 2 |
| Open signal nets | 1 |
| Barrier-net vias | 0 |
| Barrier copper off F.Cu | 0 |
| Tracks at 0.15 mm | 104 |

The open net is `REED_ISO`: U5 pin 2 is not joined to the track that reaches the rest of the net. The short is a `VIN_12` track on In1.Cu through an `IGN_B` via, and the clearance error is the same pair at 0.166 mm. The edge errors are two `ISO_5V` tracks 0.283 mm from an isolation slot; the rule is 0.30 mm. The four USB hole clearances, the twelve U3 drills, and the silk warnings are the same ones as trial A.

Contact tracks (`UP_COM`, `UP_NO`, `DN_COM`, `DN_NO`) are 0.20 mm, which is the only width the KiCad netclass contains. They are on F.Cu and have no vias.

## Conclusion

FreeRouting is usable in this environment through the JAR. The native CLI 2.5.0 is not.

On this placement it will connect the board when barrier nets may change layer, and the import then has no short, no clearance error, and no open signal. That route puts through vias on the isolated returns, the CAN pair, and the relay contacts.

When those nets are held on F.Cu, FreeRouting obeys the layer lock and still misses `REED_ISO`, shorts `VIN_12` to `IGN_B`, and runs `ISO_5V` too close to a slot. Both routes neck about a hundred tracks to 0.15 mm. Neither route knows about the 1.2 mm contact width.

It is a credible autorouter for a later pass, after the net classes carry the layer lock and the real widths, and after the USB-C pad gaps and the U3 drill rule are decided. It did not, on this placement, produce a DRC-clean board that also keeps the isolation rule. The schematic and the existing PCB were left as they are.

## Routed copy

The follow-up is `kicad11/windlass_routed.kicad_pcb`. `kicad11/windlass.kicad_pcb` was not overwritten. The schematic was not edited. No firmware was changed, and no Gerber, drill, or position file was written.

### Net classes

KiCad net classes are in the project file. Assigning a class on the net object is what the Specctra export uses. A pattern alone does not move the net on the next load, so each net is also stored as an explicit assignment. The board minimum track width stays 0.20 mm. Clearance stays 0.20 mm. The via stays 0.60 mm with a 0.30 mm drill.

| Class | Width | Nets |
| --- | ---: | --- |
| Contact | 1.20 mm | `UP_COM`, `UP_NO`, `DN_COM`, `DN_NO` |
| Power12 | 0.80 mm | `VIN_12`, `VIN_MCU`, `+12V_MCU`, `VIN_COIL`, `+12V_COIL`, `COIL_12` |
| Coil | 0.50 mm | `SERIES_NODE`, `UP_LOW`, `DN_LOW`, `SW_A`, `SW_B`, `IGN_A`, `IGN_B` |
| Isolated | 0.40 mm | `GND_CAN`, `ISO_5V`, `CAN_H`, `CAN_L`, `REED_3V3`, `REED_RET` |
| Isolated_sig | 0.25 mm | `REED_ISO`, `REED_SIG`, `LOFRANS_NODE`, `DRY_A`, `UP_RET`, `UP_FIELD`, `UP_LED_A`, `DN_RET`, `DN_FIELD`, `DN_LED_A`, `NMEA_SHIELD` |
| USB | 0.20 mm | `USB_DN`, `USB_DP`, `USB_DN_C`, `USB_DP_C`, `USB_VBUS`, `USB_SHIELD`, `CC1`, `CC2` |
| Default | 0.25 mm | everything else |

The 1.20 mm contact width is the same IPC-2221 estimate as before: external 1 oz copper, 10 °C rise, about 1.07 mm for 2.5 A. That 2.5 A is Quick’s recommended control fuse, not a measured coil current (B1). The other widths are the ones `scripts/build_board.py` already used. Isolation is not expressed as a 1.60 mm net-class clearance. The isolator pads are closer than that to each other, so that clearance would fail on the package.

### What the DSN actually contained

KiCad’s export was read back before the route. The class widths in the file were Contact 1200, Power12 800, Coil 500, Isolated 400, Isolated_sig 250, USB 200, and the default class 250, in the file’s micrometre units. Every class had clearance 200. The structure rule also said `(clearance 50 (type smd_smd))`. That token was changed to 200. KiCad does not export a layer lock. The two isolated classes were then given `(circuit (use_layer F.Cu))` and their `(use_via ...)` line was removed. The other classes kept the 0.60 / 0.30 via. The classes sit inside `(network ...)`, before `(wiring)`.

### Which of the 21 nets may use a via

Seventeen nets are the field or bus side of a functional isolator. A through via on those nets puts a plated barrel in the In1 ground pour and the In2 3.3 V pour. A 0.20 mm antipad is ordinary low-voltage spacing, and a 1.60 mm antipad does not fit at the isolator pins. The inner keepouts cover the pad clusters and not the path between them. These seventeen stay on F.Cu with no via: `REED_RET`, `REED_3V3`, `REED_ISO`, `REED_SIG`, `LOFRANS_NODE`, `DRY_A`, `UP_RET`, `UP_FIELD`, `UP_LED_A`, `DN_RET`, `DN_FIELD`, `DN_LED_A`, `GND_CAN`, `ISO_5V`, `CAN_H`, `CAN_L`, `NMEA_SHIELD`.

The four relay contacts are dry contacts in parallel with the boat controls, clamped by SMBJ18CA, not the secondary of the isolator. IPC-2221 internal spacing under 50 V is about 0.1 mm, and 0.20 mm meets it. A via at that clearance does not join the contact to ground. `UP_COM` is not tied to `DN_COM`. Those four nets may use vias. They still cannot enter an isolator keepout.

### The route

FreeRouting 2.5.0, the JAR, on OpenJDK 25.0.5.1. The native CLI was not used. Started 7:03 pm, session saved 7:06 pm, Sydney time, 22 November 2026. The command set hole clearance to 250 µm (the log says `Applied drill-hole clearance override: 250.0 um`), copper-to-edge clearance to 300 µm, neck width to 0, and automatic neckdown off. Fanout escaped 312 of 338 SMD pins. The autorouter stopped after 18 passes on its best board: score 986.31, 3 unrouted, 8 violations. Those 8 are the same unfixable J_USB pin gaps as trial A. The optimizer did not run, because the board was not complete.

An earlier start the same evening was stopped. With neck width set to 200 µm it logged `Necked retry routed net '+12V_COIL' at 200.0 um` and was discarded. The kept session has no “Necked retry” line.

### Import and DRC

The session was imported onto the copy, zones were refilled, and DRC was run at 7:12 pm. The report is `kicad11/drc_routed.rpt`. Custom rules in `kicad11/windlass_routed.kicad_dru` check the class widths, because the board minimum alone is 0.20 mm and would accept a 0.30 mm track on a 0.40 mm net.

| Check | Routed copy |
| --- | ---: |
| Shorts | 0 |
| Clearance | 0 |
| Copper-to-edge | 0 |
| Tracks crossing | 0 |
| Hole clearance | 0 |
| Drill out of range | 0 |
| Keepout | 0 |
| Open signal nets | 3 |
| GND zone reported against itself | 4 |
| Tracks under the class width | 70 |
| Dangling vias | 4, warnings |
| Silk warnings | 5 |
| Barrier-net vias | 0 |
| Barrier copper off F.Cu | 0 |

The three open connections are all on F.Cu-only nets. `LOFRANS_NODE` does not reach D20 pin 2 from JP_REED pin 1. `REED_ISO` has a track that does not reach R23 pin 1. `GND_CAN` has a track that does not reach U10 pin 15. The four dangling vias are `QMCU_G`, `IO3_NET`, `DN_REQ`, and `VIN_COIL`.

Track widths on the import:

| Width | Tracks | Where it is wrong |
| --- | ---: | --- |
| 1.20 mm | 32 | Contact nets. All of their tracks are this width. |
| 0.80 mm | 69 | Power12, except four segments at 0.60 mm on `+12V_MCU` and `+12V_COIL` |
| 0.50 mm | 37 | Coil path. All of those tracks are this width. |
| 0.40 mm | 75 | Isolated supply, except seven segments at 0.30 mm on `ISO_5V` and `REED_3V3` |
| 0.25 mm | 502 | Default and isolated signals, except 54 segments at 0.1874 mm |
| 0.20 mm | 74 | USB nets, which is the class width, except five segments at 0.15 mm on `USB_DN` and `USB_VBUS` |

The 0.1874 mm width is three quarters of 0.25 mm after FreeRouting’s integer half-width arithmetic (`2 * ((1250 * 3) / 4) = 1874` file units). The same ratio produces the 0.60, 0.30, and 0.15 mm segments. A direct merge of FreeRouting’s default settings and the CLI flag leaves automatic neckdown false, and the kept log has no necked-retry line. The session file still contains these widths. The router did not honor the class width on those 70 segments.

Contact vias: `UP_COM` one, `DN_COM` one, `DN_NO` one, `UP_NO` none. `UP_NO` reaches both outer layers through the relay pins. DRC reports no via inside an isolation keepout.

Schematic parity did not run on this copy. The schematic stores its sheet instances under the project name `windlass`, and this board’s project file is `windlass_routed`. Parity on `kicad11/windlass.kicad_pcb`, which uses the original project name, reports 0 schematic parity issues. The schematic was not given a second instance table.

### U3 thermal vias

The library footprint has twelve 0.20 mm drills on a 0.70 mm pitch under the 3.9 mm ground pad. The board minimum hole is 0.30 mm, so those twelve were drill errors. Espressif’s ESP32-S3-WROOM-1 datasheet v1.8, Figure 11-1, labels the thermal-pad via and the only via diameter in that figure is 0.5 mm. The ESP32-S3 hardware design guidelines say the ground pad should connect through at least nine vias placed in the gaps of the paste grid, and they do not state a drill or a pitch.

On the copy only, the twelve holes were removed and nine were added: drill 0.50 mm, pad 0.80 mm, pitch 1.40 mm, centered on the existing pad. The annular ring is 0.15 mm. The hole-edge gap is 0.90 mm. The via copper stays inside the 3.9 mm pad. They are on `GND` and use a solid zone connection, so the pour does not have to grow a spoke between them. DRC no longer reports a drill error or a starved thermal on these pads.

### USB-C pad to NPTH

The GCT USB4105 drawing (4 October 2019, recommended layout tolerance ±0.05 mm) specifies two 0.65 mm non-plated holes and the pad sizes the KiCad footprint already uses. The copper-to-hole gap on that land is 0.1944 mm. The pads were not moved or resized.

KiCad will not let a custom rule loosen the board minimum, so the copy’s minimum hole clearance is 0.19 mm, and `windlass_routed.kicad_dru` puts 0.25 mm back on every pair that is not both members of `J_USB`. The original project file still has 0.25 mm as its board minimum. The routed DRC has no hole-clearance violation. A fabricator that requires 0.20 mm from a non-plated hole to copper will still reject this land, and the ±0.05 mm drawing tolerance can make the finished gap smaller than 0.19 mm.

### Silk

Nine silkscreen segments on U5, U6, and U7 that crossed an isolation slot were deleted. DRC no longer reports a silk-to-edge error on those slots. Four silk overlaps remain, on the J_PWR and J_PERM labels, and one silk-over-copper warning where the J_PERM text crosses a pad of D61. Those were already on the unrouted board.

### What is still in the way of fabrication

This board is not for fabrication. Measurements B1–B8 in `docs/assumptions_and_open_questions.md` are still open. A clean clearance report is not an isolation rating. The three open nets are on the isolator side of the reed and CAN barriers. Seventy tracks are narrower than the class that was sent to the router. The USB-C land is the manufacturer’s land and is still under a common 0.20 mm hole-to-copper rule once the drawing tolerance is included. No production file was written.

## Finished copy

`kicad11/windlass_finished.kicad_pcb` starts from the routed copy and does not replace it. `kicad11/windlass_routed.kicad_pcb` and `kicad11/windlass.kicad_pcb` are unchanged. The schematic was not edited. No track was moved except the seventy under-width segments, one `PG` segment that the widening put against U13, the new `GND_CAN` track, and four ground vias. The board was not sent back through FreeRouting.

DRC after a zone refill, at 8:57 pm Sydney time on 22 November 2026, is `kicad11/drc_finished.rpt`. The project file puts the board hole clearance back to 0.25 mm. `windlass_finished.kicad_dru` keeps the six width rules and does not exempt `J_USB`.

| Check | Finished copy |
| --- | ---: |
| Shorts | 0 |
| Clearance | 0 |
| Tracks crossing | 0 |
| Copper-to-edge | 0 |
| Tracks under the class width | 0 |
| Drill out of range | 0 |
| Keepout | 0 |
| Hole clearance | 4, all on J_USB |
| Open connections | 2 |
| GND zone reported against itself | 0 |
| Dangling vias | 4, warnings, same as the routed copy |
| Silk warnings | 5, same as the routed copy |
| Barrier-net vias | 0 |
| Barrier copper off F.Cu | 0 |

### The three open connections

`GND_CAN` is connected. U10 pin 15 and pin 9 share x = 178.65 mm, and pins 10 to 14 sit between them, so a straight track would short `ISO_5V`, `CAN_L`, and `CAN_H`. The new track is 0.40 mm on F.Cu. It leaves pin 15 to the east, crosses above the package at y = 70.20 mm (the isolation slot starts at y = 70.80 mm), comes down the west side of that slot at x = 171.60 mm, and meets the existing `GND_CAN` track near C91. It has no via.

`LOFRANS_NODE` and `REED_ISO` are still open. JP_REED pin 1 (`LOFRANS_NODE`) does not reach D20 pin 2. R23 pin 1 (`REED_ISO`) does not reach the track that already ends on JP_REED pin 2. Both missing pads are on the opposite side of one `DRY_A` track from the copper already on their nets. That track runs from (94.73 mm, 122.40 mm) to (97.92 mm, 119.21 mm) and continues through (99.51 mm, 119.21 mm) to JP_REED pin 3. With it in place, the free cells on the two sides come no closer than 0.99 mm, and the copper in that gap is the `DRY_A` track plus its 0.20 mm clearance. `DRY_A`, `LOFRANS_NODE`, and `REED_ISO` are all F.Cu-only barrier nets, so a via is not available: the barrel would sit in the inner ground pour and the inner 3.3 V pour. Removing that `DRY_A` segment does open a 0.25 mm path for both nets, at x = 95.2 mm for `LOFRANS_NODE` and along y = 118.6 mm for `REED_ISO`. Putting the segment back anywhere between its two ends closes those paths again, and no other route between those ends stays on F.Cu at 0.25 mm and 0.20 mm clearance. The two pads were left unconnected. A track was not forced through `DRY_A`.

### The seventy narrow tracks

Every segment below its class width was set to the class width: 0.1874 mm and 0.15 mm necks to 0.25 mm or 0.20 mm, the 0.30 mm isolated segments to 0.40 mm, and the 0.60 mm `+12V_MCU` and `+12V_COIL` segments to 0.80 mm. DRC after that change reports no short, no clearance error, and no under-width track. One `PG` segment, between U13 pin 2 and U13 pin 4, sits in a 0.650 mm pad gap. Its center is x = 105.5185 mm, which leaves 0.200 mm to each pad. The USB escapes stay at 0.20 mm and leave the connector pads outward. None of them runs between the 0.50 mm-pitch pins.

### The four GND zone reports

These were real pieces of disconnected copper, reported in a confusing way. The F.Cu `GND` zone had island removal set to never. Its fill had five islands: the main pour, and four fragments of 8.08 mm², 0.93 mm², 0.95 mm², and 1.95 mm². KiCad’s ratsnest draws an edge between islands of the same zone, and both ends of that edge are the zone, so the report says the zone is unconnected from itself at (0.40 mm, 0.40 mm), which is the zone’s origin. The connectivity count included those four edges. They are not a duplicate-marker bug.

Each fragment touches a ground pad that had no track and no via into the main pour:

| Island | Pad |
| --- | --- |
| 8.08 mm² around (96–100, 74–78) | U14 pin 3 |
| 0.93 mm² at the left of J_USB | J_USB A1 and B12 |
| 0.95 mm² at the right of J_USB | J_USB A12 and B1 |
| 1.95 mm² above the connector | R15 pin 2 |

The pads themselves were not listed as open, because each one is connected to its own fragment. The fragment is not connected to the rest of `GND`. A 0.60 mm via with a 0.30 mm drill was added on the two USB ground pads and on R15 pin 2. U14 pin 3 is only 0.35 mm tall, so its via sits just below the pad, at (99.225 mm, 75.45 mm), and a 0.25 mm track joins them. The vias meet the B.Cu and In1 `GND` pours. After the refill the four zone-to-itself reports are gone, and those pads are on the same ground as the rest of the board. `GND` is not a barrier net. No isolated return was joined to it.

### U3 and the USB-C land

The nine U3 vias are the ones already on the routed copy: drill 0.50 mm, pad 0.80 mm, pitch 1.40 mm, inside the 3.9 mm pad, solid connection to `GND`. The datasheet figure shows a 0.5 mm via. The hardware design guidelines ask for at least nine and do not give a pitch. The 1.40 mm pitch is the spacing that fits this pad and the board’s 0.30 mm hole, 0.10 mm annular ring, and 0.25 mm hole-to-hole rules. DRC reports no drill error on them. They were not moved.

The USB-C pads are still the GCT USB4105 land. The copper-to-NPTH gap is 0.1944 mm. The pads were not moved or resized. The finished board does not repeat the routed copy’s 0.19 mm hole-clearance floor, so DRC reports all four gaps against the 0.25 mm rule. The drawing tolerance is ±0.05 mm, which can make a finished board worse than 0.1944 mm. This is a fabrication blocker. It is not waived.

### What is still in the way

This board is not for fabrication. B1–B8 are still open. A DRC with no short and no clearance error is not an isolation rating. Two barrier connections are still open, for the reason above. The USB-C land misses the 0.25 mm hole clearance by 0.0556 mm. Four dangling vias and five silk warnings are unchanged from the routed copy. No Gerber, drill, or position file was written.

## Validated copy

`kicad11/windlass_validated.kicad_pcb` continues from the finished board and leaves that file as the checkpoint. The schematic, the relay circuit, and the firmware are unchanged. The project file keeps the 0.25 mm hole clearance. `windlass_validated.kicad_dru` keeps the six width rules and does not exempt `J_USB`.

### The DRY_A via check

`LOFRANS_NODE` and `REED_ISO` are still open. JP_REED pin 1 does not reach the `LOFRANS_NODE` track at D20 pin 2. R23 pin 1 does not reach JP_REED pin 2. The copper between them is the `DRY_A` segment from (94.73 mm, 122.40 mm) to (97.92 mm, 119.21 mm).

`DRY_A` is the standalone dry-contact node. It sits on the field side of the reed isolator, on `REED_3V3` and `REED_RET`. The Lofrans input uses that same isolated supply. R22 pulls `DRY_A` up to `REED_3V3`. With the shunt on JP_REED pins 1–2, that pull-up stays off `REED_ISO` and `LOFRANS_NODE`. With the shunt on pins 2–3, the pull-up reaches the isolator through `DRY_A`.

A two-via jump onto another layer was measured before any via was placed. The field pocket is the inner keepout from (83.06 mm, 113.59 mm) to (110.70 mm, 151.18 mm) on In1 and In2. That keepout forbids tracks, vias, and pours. The isolation slots are (81.20 mm, 117.80 mm)–(83.40 mm, 122.20 mm) at the MEJ2 and (109.30 mm, 115.40 mm)–(110.70 mm, 120.60 mm) at the ISO7720. The blocking segment is inside the keepout.

`REED_3V3` runs without a break from U4 pin 7 (91.24 mm, 120.00 mm) along y = 116.06 mm to U5 pin 1. The south edge of that 0.40 mm track is y = 116.26 mm. JP_REED pin 1’s pad reaches y = 116.515 mm. The gap is 0.255 mm. A 0.25 mm track with 0.20 mm clearance on both sides needs 0.65 mm, so `DRY_A` has no F.Cu exit north of the header. West and east of the pocket, the exits are the two slots. Past either slot is the logic side of the isolator.

A via outside the keepout is north of y = 113.59 mm, or outside x = 83.06–110.70 mm. The field-side ends of the segment cannot reach that via without crossing `REED_3V3` or a slot. On the logic side the In1 ground pour and the In2 3.3 V pour come within the ordinary 0.20 mm zone clearance of a barrel. The reed barrier is the 1.60 mm surface gap and the 2.20 mm inner-plane margin, not that 0.20 mm clearance. A barrel there would place the dry-contact node, and the isolated reed supply it shares, at ordinary low-voltage spacing from board ground and logic 3.3 V.

No via was added. Both open nets stay on F.Cu. The segment stays, so `DRY_A` still reaches JP_REED pin 3. The two F.Cu paths that open only when that segment is removed are the ones already measured on the finished board: `LOFRANS_NODE` at x = 95.2 mm, and `REED_ISO` along y = 118.6 mm between the header pins.

### USB-C land against the hole rule

The connector uses KiCad’s `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`. The footprint cites the GCT drawing (USB4105, 4 October 2019, recommended PCB layout, tolerance ±0.05 mm): https://gct.co/files/drawings/usb4105.pdf

That land, as drawn in the footprint, has two Ø0.65 mm non-plated holes at (±2.89 mm, −2.605 mm) and the ground pads A1/B12 and A12/B1 at (±3.20 mm, −3.68 mm), each 0.60 × 1.15 mm with a 0.15 mm corner radius. The gap from the rounded pad corner to the hole is 0.1944 mm. DRC measures the same 0.1944 mm on J_USB.

The board hole clearance stays 0.25 mm. The land is 0.0556 mm inside that rule. A fabricator that requires 0.20 mm from a non-plated hole to copper also rejects the nominal gap. The ±0.05 mm layout tolerance can make a finished board smaller than 0.1944 mm. The pads were left at the drawing sizes. The four hole-clearance errors remain. This is a fabrication blocker.

### Dangling vias and silk

Four vias that connected on one layer only were removed: `QMCU_G` at (82.07 mm, 16.22 mm), `IO3_NET` at (138.84 mm, 60.72 mm), `DN_REQ` at (143.55 mm, 61.01 mm), and `VIN_COIL` at (88.05 mm, 36.98 mm). Each net still joins its pads on the copper that remains.

The `+12V  GND` label moved from (12.00 mm, 140.00 mm) to (12.00 mm, 139.40 mm), above the J_PWR silk at y = 140.48 mm. The `SW  SW  IGN  IGN` label moved from (42.00 mm, 140.00 mm) to (45.50 mm, 139.40 mm). Its box is (39.15 mm, 138.61 mm)–(51.85 mm, 140.19 mm). D61 pad 2 ends at x = 38.90 mm, and the J_PERM silk starts at y = 140.48 mm. DRC reports no silk warning.

### DRC and ERC

DRC after a zone refill, at 7:23 am Sydney time on 23 November 2026, is `kicad11/drc_validated.rpt`. It reports 0 shorts, 0 clearance errors, 0 under-width tracks, 2 unconnected items, and 4 hole-clearance errors. No barrier net has a via. Barrier copper is on F.Cu only. The nine U3 vias stay at 0.50 mm drill and 0.80 mm pad.

ERC on the unchanged schematic, the same morning, is `kicad11/erc_validated.rpt`: 0 errors and 1 warning. The warning is U5 pin 4, `GND1`, on `REED_RET`. That net is the isolated field return.

### What is still in the way

This board is not for fabrication. B1–B8 in `docs/assumptions_and_open_questions.md` are still open. A DRC with no short and no clearance error is not an isolation rating. The two barrier connections stay open because the via that would free them puts `DRY_A` through the logic-side planes. The USB-C land cannot meet the 0.25 mm hole rule, or a 0.20 mm non-plated-hole rule, at the drawing’s own dimensions and tolerance. No Gerber, drill, or position file was written.
