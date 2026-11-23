# JLCPCB and the GCT USB4105 land

Read on 23 November 2026. The board file was not edited. No Gerber was generated, and nothing was sent to JLCPCB. This is not a JLCPCB approval.

The four remaining DRC errors are on `kicad11/windlass_complete.kicad_pcb`. Each is the GCT USB4105 ground pad against one of its two Ø0.65 mm non-plated holes. KiCad measures 0.1944 mm. The board rule is 0.25 mm.

## The land

GCT drawing USB4105, 4 October 2019, revision note B4 dated 18 December 2023: https://gct.co/files/drawings/usb4105.pdf

The recommended PCB layout is drawn from the component side, with a tolerance of ±0.05 mm. It calls for two Ø0.65 mm holes, twelve pads 1.15 mm long, four pads 0.60 mm wide, and eight pads 0.30 mm wide. The KiCad footprint `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` cites that drawing. It places the holes at (±2.89 mm, −2.605 mm) as non-plated, and the ground pads A1/B12 and A12/B1 at (±3.20 mm, −3.68 mm), each 0.60 × 1.15 mm with a 0.15 mm corner radius. The gap from the rounded corner to the hole is 0.1944 mm. The drawing text does not print the words “non-plated”. The component view shows two Ø0.50 mm pegs, and the product page lists locating pegs separately from the shell stakes. The footprint treats the Ø0.65 mm holes as the peg holes and the oval drills as the stakes.

The ±0.05 mm figure is GCT’s tolerance on the recommended layout. The footprint uses the nominal dimensions. It is not a JLCPCB process tolerance, and it is not added again on top of JLCPCB’s drill tolerances below.

The drawing does not state a PCB thickness. The shell-stake options are 0.60 mm, 0.95 mm, and 1.20 mm, each ±0.15 mm. The longest option is shorter than 1.6 mm, so the stake can sit in a 1.6 mm board. That is not a GCT statement that 1.6 mm is an approved thickness.

The shell-stake drills in the footprint are oval, 0.60 × 1.70 mm and 0.60 × 1.40 mm, in 1.00 × 2.10 mm and 1.00 × 1.80 mm pads. The design annular ring is 0.20 mm. Those four DRC errors are the peg holes, not the stakes.

## What JLCPCB publishes

Source: the rigid-PCB capability table at https://jlcpcb.com/capabilities/pcb-capabilities, retrieved 23 November 2026. The rows below are quoted from that table.

| Published row | Value |
| --- | --- |
| FR-4 thickness, including 1.6 mm | 0.4 / 0.6 / 0.8 / 1.0 / 1.2 / 1.6 / 2.0 mm |
| Minimum non-plated hole | 0.50 mm |
| Hole size tolerance, through-holes | +0.13 / −0.08 mm |
| Hole position tolerance | ±0.075 mm |
| Non-plated slot size tolerance | ±0.2 mm, made by CNC |
| NPTH to track | 0.2 mm |
| PTH to track | 0.28 mm minimum, 0.35 mm recommended |
| Inner-layer via hole to copper | 0.2 mm |
| PTH annular ring, multilayer, 1 oz | 0.20 mm recommended, 0.15 mm absolute minimum |
| NPTH pad annular ring | ≥ 0.45 mm, so that 0.2 mm of copper can be removed around the hole for the sealing film |
| Plated slot, multilayer | width ≥ 0.35 mm, and length at least twice the width |

The Ø0.65 mm holes are above the 0.50 mm minimum. A 1.6 mm 4-layer FR-4 board is a thickness the table lists. The stake slots, as drawn, meet the plated-slot width and the twice-width length rule, and the 0.20 mm annular ring meets the multilayer recommendation. The inner pours are not the four DRC errors: those errors are the ground pads, and the same DRC run reports no other hole-clearance item, so the pours are at least the board’s 0.25 mm from these holes.

The table does not have a row named “NPTH to SMD pad” or “copper to NPTH”. The row that names a non-plated hole and neighbouring copper is “NPTH to Track, 0.2 mm”. The ground features are pads. Applying that 0.2 mm to a pad is a reading of the table, not a second published number.

The NPTH annular-ring note is about a pad that surrounds the hole. These ground pads do not surround the holes. The note is not a measurement of this land.

Two other JLCPCB pages do not settle it:

- The ordering guide, last updated 10 November 2026, says an order that exceeds their capabilities is cancelled and they email the reason. https://jlcpcb.com/help/article/instructions-for-ordering
- A design-issues article, updated 9 September 2026, says to leave at least 2 mm between an NPTH and a copper trace, and also says JLCPCB does not verify design errors in Gerber files. https://jlcpcb.com/blog/common-pcb-design-issues-recommendations

The 2 mm sentence is not on the capability table. It is not reconciled there with the 0.2 mm NPTH-to-track row, and it would reject ordinary USB-C shell holes. It is not used here as the pass or fail number. The capability table is the manufacturing minimum they publish. The 2 mm article and the ordering guide disagree in tone about whether a file below that minimum is caught. Neither page mentions the USB4105, and neither is a review of this board.

## Comparison

The nominal gap is 0.1944 mm. The published NPTH-to-track minimum is 0.20 mm. The land is 0.0056 mm under that number before any process tolerance.

The hole-position tolerance is ±0.075 mm. A hole moved that far toward the pad leaves 0.119 mm. The through-hole size tolerance is +0.13 / −0.08 mm and is not labelled “plated only”; non-plated slots have their own row. If the +0.13 mm applies to the diameter of these holes, the radius grows by 0.065 mm and the gap falls to about 0.054 mm. That sum is arithmetic on two separate rows. JLCPCB does not publish it as a guaranteed remaining clearance, and the 0.2 mm row does not say that it already includes those tolerances.

The board’s own 0.25 mm rule is stricter than 0.20 mm. Lowering the KiCad rule to 0.20 mm would not clear the four errors, because 0.1944 mm is still under 0.20 mm.

A manufacturer land can be kept despite a KiCad error when the fabricator’s published capability covers the real gap, or when the fabricator confirms the exception. The capability table does not cover 0.1944 mm, and JLCPCB has not confirmed this land.

## No replacement is confirmed

The connector stays the USB4105 until a replacement is both a horizontal top-mount USB 2.0 16-pin part and clear of the published hole rule on a 1.6 mm board. The KiCad USB-C receptacle footprints were measured again for the 0.20 mm number. None of the horizontal 16-pin lands does that with the published position tolerance included.

| Footprint | Closest copper to a foreign hole | Why it is not the replacement |
| --- | --- | --- |
| GCT USB4105 | 0.194 mm, NPTH to the ground pad | This land. Under 0.20 mm as drawn. |
| GCT USB4110 | 0.194 mm, same geometry | Same class of part, same gap. |
| JAE DX07S016JA1 | 0.266 mm, oval NPTH to a shell pad | Drawing SJ121836 rev 3, mounting view marked reference, prints t1.2. A 0.075 mm hole shift leaves 0.191 mm. Not a confirmed 1.6 mm part. |
| Amphenol 12401610E4-2A | 0.298 mm, NPTH to a shell pad | USB 3.2 Gen 2, two pad rows. The KiCad gap was not checked back to an Amphenol drawing. The schematic would change. |
| GCT USB4085 | 0.300 mm between plated signal holes | The PTH-to-track minimum is 0.28 mm. A 0.075 mm shift leaves about 0.225 mm. Pad gap is 0.15 mm. |
| GCT USB4115-03-C | 0.47 mm | Vertical USB 3.2 receptacle. The enclosure is still unknown. |
| GCT USB4125 / USB4135 | holes clear | Power only. No D+ or D−. |

## Decision

The connector stays the GCT USB4105. A different connector was not fitted. No horizontal 16-pin land in the KiCad library is a cleaner fix than relieving the one corner that fails the hole rule.

Raising the corner radius of the 0.60 mm pad cannot reach 0.25 mm. At the largest radius the pad allows, 0.30 mm, the gap is 0.233 mm. The copper that fails the rule is one corner of each ground pad, the corner facing the locating hole. That corner was cut back so the copper stays 0.28 mm from the hole edge. KiCad measures 0.280 mm. The board rule stays 0.25 mm, and there is no exemption.

The cut removes 0.0184 mm² from a 0.670 mm² pad, about 2.7 percent. It is deepest at the corner, about 0.10 mm, and it is about 0.02 mm at the pad centre line. The other three corners, the pad centre, and the toe stay on the drawing. The drawing’s four power tails are 0.45 mm wide, centred in the 0.60 mm pad, so the tail has 0.075 mm of pad on each side before this cut. The shell-stake slots and the Ø0.65 mm peg holes were not moved. Paste and mask follow the same outline, so paste is not printed on the copper that was removed. A1 and B12 are one pad, and A12 and B1 are the other. All four pad numbers carry the same outline. The nets are still GND.

The new board is `kicad11/windlass_cleared.kicad_pcb`. `kicad11/windlass_complete.kicad_pcb` was not overwritten. The schematic was not edited, because the connector and the pin assignment did not change. Routing, the isolation slots, the inner keepouts, and the relay circuit are the same.

DRC after a zone refill, at 12:33 pm Sydney time on 23 November 2026, is `kicad11/drc_cleared.rpt`: 0 violations, 0 unconnected items, and 0 footprint errors. ERC on the unchanged schematic is `kicad11/erc_cleared.rpt`: 0 errors and 1 warning, U5 pin 4 `GND1` on `REED_RET`.

What remains: JLCPCB has not reviewed this board. Their published hole-position tolerance is ±0.075 mm. A hole moved that far toward the pad leaves about 0.205 mm, which is still above their 0.20 mm NPTH-to-track row. Their through-hole size tolerance is +0.13 / −0.08 mm and is not labelled plated-only. If that oversize also applies, the radius grows by 0.065 mm and the two effects together leave about 0.140 mm. That sum is arithmetic on two separate rows, not a limit they publish. The design meets the 0.25 mm board rule and the 0.20 mm published design minimum. It does not absorb both tolerances at once. This board is still not for fabrication. B1–B8 are open. A clean DRC is not an isolation rating.
