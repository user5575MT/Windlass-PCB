# JLCPCB package for windlass_install_v2

Generated 23 November 2026 from `kicad11/windlass_install_v2.kicad_pcb`. Nothing in this directory has been ordered.

| File | Contents |
| --- | --- |
| `windlass_install_v2_gerbers.zip` | 4-layer Gerbers and Excellon drills |
| `bom.csv` | One row per value and footprint. `LCSC` is blank on purpose |
| `cpl.csv` | Centroid file, millimetres, KiCad rotation, absolute coordinates shared with the Gerbers |

The zip names:

| Layer | File |
| --- | --- |
| Top copper | `windlass-F_Cu.gtl` |
| Inner 1 | `windlass-In1_Cu.g1` |
| Inner 2 | `windlass-In2_Cu.g2` |
| Bottom copper | `windlass-B_Cu.gbl` |
| Top mask / paste / silk | `.gts`, `.gtp`, `.gto` |
| Bottom mask / paste / silk | `.gbs`, `.gbp`, `.gbo` |
| Outline | `windlass-Edge_Cuts.gm1` |
| Plated drills | `windlass-PTH.drl` |
| Non-plated drills | `windlass-NPTH.drl` |

Board stack: 1.6 mm, 4 layers. Every placed part in the centroid file is on the top. Bottom paste is empty.

`bom.csv` column `Assembly` is `smt` or `through-hole`. The through-hole parts are the two Finder relays, the two Murata modules, the KF350 terminals, the JST headers, and the two jumpers. JLCPCB's SMT line places the `smt` rows. The through-hole rows are hand-fitted, or wave-soldered if the order says so. The six test points and the four M3 holes are on the board and are not in the centroid file.

The `LCSC` column is empty. A C-number from an older note is not copied here, because those counts were not re-read and several of those notes describe parts that are no longer on this board. At order time, match each comment and footprint to a current JLCPCB reel. Do not substitute the Murata modules or the Finder relays.

Coordinates are KiCad's absolute origin, the same origin as the Gerbers and the drills. Rotation is KiCad's footprint rotation.
