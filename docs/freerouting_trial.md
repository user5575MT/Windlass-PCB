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
