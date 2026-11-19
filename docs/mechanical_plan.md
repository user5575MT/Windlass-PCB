# Preliminary placement

## Revision 0.4 — every field connection

The 80 × 60 mm outline holds the six field connectors, both Finder relays, the ESP32 module, both Murata MEJ2 modules and the isolators, with washer courtyards and an antenna notch. It does not hold the remaining passives and the three switches. One SOD-123 was still unplaced at 80 × 68 mm. At **80 × 69 mm** the courtyard check is clear for every schematic part. That is 9 mm over the preferred height and inside the 100 × 70 mm maximum. Width stays 80 mm. The extra strip is on the bottom edge. The antenna stays on the top edge.

The connectors are real footprints, not 2.54 mm headers:

- Left edge, screw, 3.5 mm: `J_PWR` (2-pin, 10 A), `J_CONTACT` (4-pin, 10 A), `J_PERM` (4-pin, coil loop).
- Right edge, latched JST XH: `J_REED` (4), `J_SENSE` (4), `J_NMEA` (5).
- Bottom edge: USB-C shell overhangs the edge between the relays.

`J_SENSE` has no empty pin between `UP_RET` and `DN_FIELD`. The nets are not joined. The pinout is `docs/connector_pinout.md`.

Mounting holes are 3.2 mm. The courtyard is 7.4 mm across, which covers an ISO 7380 M3 button head (5.7 mm) and a 7 mm washer with 0.2 mm to spare. Centres are 4.0 mm from the bottom corners and the same distance from the top corners of the 69 mm board.

The top edge is notched from x = 28 to 52, starting 14 mm down from the top, so the FR4 beside and beyond the module antenna is removed. The copper keep-out still covers the library antenna courtyard. Espressif’s 15 mm clearance is an enclosure rule in every direction around that notch. The twelve 0.2 mm heatsink vias are unchanged.

Small parts are packed into the free cells so the courtyard check covers them. Their coordinates are a fit proof, not a routed arrangement. Copper is not routed.

## Still unresolved

- Lofrans control current and its inductive energy. The 10 A / 18–24 AWG contact terminal is not a measured rating.
- `R30` and `R40`, the direction-sense LED resistors.
- KF350-3.5-4P stock, and the real drill drawing for both KF350 sizes. The placed courtyard is a 3.5 mm 4Ucon envelope.
- JST B5B-XH-A stock count was not on the page extract. The header is not sealed.
- MEJ2 pin-to-body offset and the 1.00 mm versus 1.15 mm drill.
- MEJ2S0505SC is not a JLCPCB Murata assembly part. MEJ2S0503SC stock was 3.
- AP63203 quantity, 74LVC1G123 / 86 / 08, NX6008NBK, fuses, USB-C and LED reels.
- Branded SMAJ18A quantity. A TECH PUBLIC listing was not accepted.
- USB-C DRC still reports eight errors. They are the footprint’s stacked GND and VBUS through-holes (A1 with B12, A4 with B9, and the matching pair). The placement file has no nets, so KiCad treats each pair as two nets. Recheck after the schematic is linked to the board. The shield-to-edge error cleared when the receptacle moved 0.2 mm onto the board.
- No fabrication quote. Nothing is released to be built.

# Earlier placement note


## Revision 0.3 — connectors, MEJ2 footprint, keep-outs

The outline stays **80 × 60 mm**. Copper is still not routed. Nothing in this revision is a fabrication release.

The Murata MEJ2 single-output footprint is `kicad/footprints.pretty/Murata_MEJ2SxxxxSC.kicad_mod`. It is no longer the MEJ1 library part. Pins are 1 (+Vin), 2 (−Vin), 5 (−Vout) and 7 (+Vout), on a 2.54 mm pitch, which is the single-output table in Murata KDC_MEJ2. Pin 6 is not fitted. The drill is 1.00 mm, one of the two hole diameters printed on the recommended-footprint drawing (the other is 1.15 mm). The courtyard is the 19.65 × 10.05 mm maximum body. The drawing’s pin-to-body offset was not fully legible, so that courtyard is centred on the pin span and must be checked against the dimensioned figure before the holes are released.

Copper keep-outs, on all four copper layers, now cover the antenna zone and the gap between MEJ2 pins 2 and 5 on each module. That gap is 7.62 mm. Tracks, vias, pads and pours are forbidden there. The module’s own pins sit outside the polygon. `REED_RET`, `UP_RET`, `DN_RET` and `GND_CAN` are still separate nets. The keep-outs do not join them.

Espressif’s module layout note (Hardware Design Guidelines, PCB layout for modules) asks for the antenna outside the base board, or, if it cannot overhang, for the base board to be cut away beside and beyond the antenna. It separately asks for at least 15 mm of clearance inside the housing, in all directions, and says the module should not sit in the middle of a board with a hole cut on all four sides. The placed module is at the top edge. The copper keep-out is the area past the module body. The board is not notched, because a notch under the antenna was not required to meet 80 × 60 mm and has not been drawn. Mounting holes are outside that keep-out. The 15 mm housing clearance is an enclosure requirement, not extra PCB.

### Connectors, and what does not fit

The 2.54 mm headers are gone from the 80 × 60 mm placement. The parts selected for the field wiring are screw terminals:

- KF350-3.5-2P (Cixi Kefa, LCSC C474892): 3.5 mm pitch, 10 A, 300 V, 18–24 AWG, for 12 V input and the UP/DOWN contact outputs. Stock was not shown on the page read on 19 November 2026.
- XY350V-3.5-2P (Ningbo Xinlaiya, LCSC C784942): 3.5 mm pitch, 7 A, 300 V, 18–24 AWG, for the low-current loops. JLCPCB showed 1791 in stock on that date, extended, wave solder.

The placed board has four of these on the side edges: 12 V input, UP contact, DOWN contact, and the Lofrans reed. Each side column, between the M3 hole and the MEJ2 body, is only tall enough for two. The antenna keep-out takes the top edge and the two Finder courtyards take the bottom edge, so there is no third column.

These required connectors are still on the schematic and are **not on the placement**, because they do not fit:

- dry-contact reed
- UP field sense and its own return
- DOWN field sense and its own return
- ignition permissive
- relay-power switch loop
- NMEA drop

That is a mechanical limit of 80 × 60 mm with these relays and this antenna keep-out. The board was not enlarged. A multi-way housing or a verified connector shallower than 8 mm would be the next thing to try. The 4Ucon 3.50 mm courtyard used for the fit check is 8.7 × 8.0 mm. It is a pitch-matched envelope. The KF350 and XY350V body drawings were not in the pages that were read, and the 1.2 mm drill is the KiCad model’s drill, not a number copied from those drawings. Do not release the holes until those drawings are checked.

The relay-power switch remains an off-board switch in series with the coil feed, so it can be a sealed panel switch. The connector for that loop is one of the parts that does not fit.

### The twelve 0.2 mm drills

They are twelve plated holes on pad 41 of the KiCad `ESP32-S3-WROOM-1` footprint, each drilled 0.2 mm in a 0.6 mm pad, tagged as heatsink vias under the exposed pad. Espressif’s layout guide tells you to stitch that pad to ground with vias and to cover the gaps so solder does not wick. KiCad’s default minimum hole, used when the board has no tighter project rule, is 0.3 mm, which is why DRC reports them. JLCPCB’s capability page lists 0.2 mm as the preferred minimum via hole on a multilayer board, and a 0.6 mm pad gives a 0.2 mm annular ring, which is above the 0.15 mm multilayer minimum. The holes are not a footprint mistake and they were not deleted. `kicad/placement_finder.kicad_pro` sets the minimum through hole to 0.2 mm so the check matches that capability. KiCad 10.0.8 then reported **0 errors** on `kicad/placement_finder.kicad_pcb` (19 November 2026, 13:20). The twelve drills are no longer violations. They were not added to an exclusion list.

The same run recorded 26 warnings in `docs/drc_placement_80x60_warnings.txt`. Nine are silkscreen crossing the board edge or another courtyard, mostly reference text on the edge terminals and the corner holes. Eleven are the embedded footprints no longer matching the library copy, because the value field was rewritten and the MEJ2 footprint lives in the project library rather than the global table. None of those warnings is a courtyard overlap or a drill error.

The CAN module was moved inboard to x = 74.5 mm so its 10.05 mm body stays inside the 80 mm edge. The reed isolator was moved to (18.6, 34.8) so its courtyard clears that module.

# Earlier placement note


Revision 0.2. This is a component placement, not a routed board and not a fabrication release. No copper is poured. No tracks are drawn. No Gerbers are issued. The working prototype is unchanged.

The preferred outline is met. The board that clears the footprint courtyards is **80 × 60 mm**, four-layer. That is inside the 80 × 60 mm target and inside the 100 × 70 mm cap. A second Finder arrangement at 90 × 60 mm also clears, and is the roomier of the two. It is not required.

## What was placed

Both Finder boards use the selected parts. The third file is a size study of a smaller relay that is not selected.

| File | Outline | What it is |
| --- | --- | --- |
| `kicad/placement_finder.kicad_pcb` | 80 × 60 mm | Selected placement. Finder 40.31.7.012.0000 |
| `kicad/placement_finder_90x60.kicad_pcb` | 90 × 60 mm | Same parts, wider connector margins |
| `kicad/placement_compact_study.kicad_pcb` | 80 × 60 mm | Omron G5Q courtyard only, marked not selected |
| `kicad/placement/placement_80x60.svg` | 80 × 60 mm | Drawing of the selected placement |

The drawing shows the board outline, the antenna edge, both relay courtyards, the power cluster (two bucks, two inductors, the input TVS, the MCU fuse, the coil P-FET), the reed isolator and the CAN isolator, both isolated DC-DC modules, the connectors, the status LED, four M3 holes, and the isolation rectangles.

## Why 80 × 60 mm is the size

The ESP32-S3-WROOM-1 footprint courtyard is not the 18 × 25.5 mm module body. KiCad draws the body at about 19.5 × 20 mm and adds the antenna keep-out as a wing 48 mm wide and 21 mm deep. That wing is the copper-free region on every layer. It sits on the top edge, centred. The 15 mm metal clearance beyond the antenna remains an enclosure rule. It is not extra PCB.

Under that wing the two Finder courtyards are 29.5 × 12.9 mm each (body 29 × 12.4 × 25 mm). Side by side, with a gap, they occupy about 61 mm. The left and right connector columns and the M3 holes take the rest of the 80 mm. The depth is the antenna wing plus the module body (about 41 mm from the top edge), the relay row (12.9 mm) and a connector strip along the bottom. That stack fills 60 mm.

A 90 × 60 mm board of the same parts also clears. The extra 10 mm is unused connector margin. It does not fix an electrical or isolation problem, so it is not the board to build.

The outline was not grown to make routing easier. Copper has not been routed, so routing difficulty is not a reason for any dimension here.

## Relay size

The Finder 40.31.7.012.0000 stays. It is through-hole and hand-fitted. It is not a JLCPCB-assembled SMT part.

Two smaller relays were checked and not substituted. Both publish a DC current that is a resistive rating.

- Omron G5Q-1A4, about 20.3 × 10.3 × 15.8 mm. The DC contact rating used in the check is 5 A at 30 V DC with L/R = 0. That is a resistive figure. The KiCad G5Q courtyard was placed on the same 80 × 60 mm outline (`placement_compact_study.kicad_pcb`) so the space can be compared. The part is not on the schematic.
- Hongfa HF46F/12-HS1T, about 20.5 × 7 × 15.3 mm, through-hole. The 5 A at 30 V DC figure is resistive. The UL R300 pilot-duty listing is a 250 V DC rating of about 0.22 A, not a multi-amp 12 V inductive rating.

A smaller body would leave spare room beside the relays. It would not, by itself, authorise a board below 80 × 60 mm, and it would not meet the rule that a relay is not swapped on a resistive current rating. The Lofrans control current and its inductive energy are still unmeasured. Installation stays blocked on that measurement, against the Finder DC1 ceiling of 10 A at 30 V DC resistive.

## Where the groups sit on the 80 × 60 mm board

Origin is the bottom-left corner. Dimensions are millimetres.

- Antenna. Top edge, x = 16 to 64, y = 39 to 60. Copper-free on all layers. The module is centred at (40, 32.25), rotated so the antenna legend points at that edge.
- Relays. K_UP and K_DN along the bottom, courtyards roughly x = 9.5 to 39 and x = 41 to 70.5, y = 4.9 to 17.8. Normally-closed pins are not connected. The two contact commons are not tied.
- Power. Left of the module body: AP63203, AP63205, the two inductors, SMAJ18A, the 2 A fuse. The coil P-FET sits on the right of the module, still on the coil side of the CAN barrier.
- Reed isolation. MEJ2S0503SC in the top-left margin, with ISO7721D on the logic side of that module. The rectangle on Eco1 is the barrier. `REED_RET` is not joined to battery ground.
- CAN isolation. MEJ2S0505SC in the top-right margin, ISO1042 below it on the logic side. The rectangle on Eco1 is the barrier. `GND_CAN` is not joined to battery ground, and this region does not share copper with the relay contacts.
- Connectors. 12 V input, UP contact and DOWN contact on the left edge. Reed, dry-contact and the relay-power switch along the bottom. Ignition and the NMEA header on the right edge, outside the CAN barrier. These headers are placement stand-ins at 2.54 mm pitch. The connector family is not frozen.
- Status LED. Bottom edge, between the two relays, so it remains visible when the board is installed.
- Mounting. Four M3 holes, 3.2 mm, at (3.8, 3.8), (76.2, 3.8), (3.8, 56.2) and (76.2, 56.2).

The MEJ2 modules are drawn with the KiCad MEJ1 SIP footprint. Both are 19.5 × 9.8 mm SIPs with the same 2.54 mm pitch. The footprint is a size proxy for placement. It is not a claim that the MEJ1 pinout has been substituted, and it is not a routed footprint. The isolation rectangles are drawings. They become all-layer copper keep-outs when routing starts. The minimum keep-out under each barrier is the module's 2 mm certified spacing, and the preferred keep-out is the full 7.62 mm pin gap.

The four-layer stack in the file is a placeholder (1 oz copper, prepreg / core / prepreg). A JLCPCB stackup has not been chosen. The layer count is four, as required.

## Clearance check

KiCad 10.0.8 DRC, errors only, 19 November 2026:

| Board | Report | Courtyard overlaps | Other errors |
| --- | --- | --- | --- |
| 80 × 60 mm Finder | `docs/drc_placement_80x60.txt` | 0 | 12 |
| 90 × 60 mm Finder | `docs/drc_placement_90x60.txt` | 0 | 12 |
| 80 × 60 mm G5Q study | `docs/drc_placement_study.txt` | 0 | 12 |

The 12 errors on every board are the same pads: the ESP32-S3-WROOM-1 footprint's own 0.2 mm drills on pad 41, against KiCad's default minimum hole of 0.3 mm. They are not collisions between parts. JLCPCB's usual minimum drill is 0.2 mm, so these are a rule-default mismatch to confirm at order time, not a reason to grow the board.

Unconnected-pad count is zero because this placement has no nets. That is not a routed-board check. Pads of neighbouring parts do not violate the default clearance, because no clearance error was reported.

## Still open

Creepage across the isolation barriers is not a measured copper distance until the keep-outs are routed. Enclosure air temperature, the 15 mm antenna-to-metal gap, and which battery feed the board sees remain B6. The Lofrans control current remains the installation hold.
