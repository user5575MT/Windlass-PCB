# JLCPCB package for windlass_install_v2

Prepared 23 November 2026, Sydney time (AEDT, UTC+11). The board file was not changed. Nothing in this directory has been ordered.

Upload these three files together:

| Upload | File |
| --- | --- |
| Gerbers and drills | `windlass_install_v2_gerbers.zip` |
| SMT bill of materials | `bom_smt.csv` |
| SMT pick and place | `cpl.csv` |

`bom.csv` is the full list, including the hand-fitted parts, and it is not the upload file. `purchase_hand.csv` is the separate buy list for those parts. The part match, the rotation check, and the cost are in `docs/jlcpcb_order.md`.

Order options that match this package: 5 boards, 4 layers, 1.6 mm, single-sided Standard assembly, parts on the top only. Standard assembly is required because `ESP32-S3-WROOM-1-N16` (C2913199) is a Standard-only part. Leave the through-hole parts and the two switches off the machine build. They are soldered by hand from `purchase_hand.csv`.

## Zip contents

| Layer | File |
| --- | --- |
| Top copper | `windlass-F_Cu.gtl` |
| Inner 1 | `windlass-In1_Cu.g1` |
| Inner 2 | `windlass-In2_Cu.g2` |
| Bottom copper | `windlass-B_Cu.gbl` |
| Top paste | `windlass-F_Paste.gtp` |
| Bottom paste | `windlass-B_Paste.gbp` |
| Top silkscreen | `windlass-F_Silkscreen.gto` |
| Bottom silkscreen | `windlass-B_Silkscreen.gbo` |
| Top mask | `windlass-F_Mask.gts` |
| Bottom mask | `windlass-B_Mask.gbs` |
| Outline | `windlass-Edge_Cuts.gm1` |
| Plated drills | `windlass-PTH.drl` |
| Non-plated drills | `windlass-NPTH.drl` |

The board is 200 mm by 160 mm. Bottom paste is empty. Bottom silk has no legend. The four M3 holes and the two USB locating holes are in the non-plated drill file.

## Centroid file

`cpl.csv` is millimetres, top side, and the same origin as the Gerbers. Y in the file is the Gerber Y. Two placements are shifted off the KiCad footprint origin so the JLCPCB library footprint lands on the copper:

| Designator | Mid X | Mid Y | Rotation |
| --- | --- | --- | --- |
| J_USB | 20.0000 | −14.6923 | 0 |
| U3 | 148.0000 | −49.6267 | 0 |

The KiCad origins were (20, −16) and (148, −46). The rest of the coordinates are the KiCad centroids. Rotations in this file are the JLCPCB placement angle, which for the SOT-23, SOT-223, SOT-353, TSSOP-8, TSOT-23-6, SOT-23-6, SOIC-8, and SOP-4 parts differs from the KiCad angle. The table is in `docs/jlcpcb_order.md`.
