# Home-assembly controller

24 November 2026, Sydney time. This is the finished through-hole design. It is not an order. Bench-test the first board before it is installed. A single-distributor replacement for the relays, the isolators and the watchdog was investigated and not fitted. The reasons are in `docs/home_purchase.md`.

`kicad11/windlass_install_v2.kicad_pcb` and the firmware were not edited. The new files are under `kicad_home/` and `scripts/build_home.py`. Open `kicad_home/windlass_home.kicad_pro`.

The board is **120.0 mm by 112.0 mm**, two layers, 1.6 mm. It is not 100 mm square. The DevKit sockets, the two Finder relays, the two 5×20 fuse holders, the two Murata modules and the field-side parts were placed with their real courtyards and with 0.6 mm between isolation domains. That set does not fit in 100 mm by 100 mm. The extra width is the isolation column. The extra height is the room under the DevKit that the logic and the timing network use.

Pictures: `docs/images/windlass_home_top.png` and `docs/images/windlass_home_3d.png`. The 3D view shows the parts that have models. The DevKit itself is a plug-in module on the two socket strips, so the render shows the sockets and not the module. The antenna end of the module sits over the empty copper area beside those sockets.

## Checks

ERC on `kicad_home/windlass_home.kicad_sch`: 0 errors. Report: `docs/home_erc.txt`.

DRC on `kicad_home/windlass_home.kicad_pcb`: 0 errors and 0 unconnected pads, with the isolation rules in `kicad_home/windlass_home.kicad_dru` loaded. Report: `docs/home_drc.txt`. Six silk warnings remain. They are the pin-1 arcs of the optocouplers crossing the milled isolation slots. The slots are supposed to be milled, so those arcs are cut with the slot.

Two M3 holes are fitted, both on the right edge. The left corners are occupied by the relays and the connectors. A box can clamp that edge, or a hole can be drilled later in a spot that is clear of copper.

## Watchdog

The 74HCT123 cannot hold the existing 80 ms heartbeat, and the firmware period was not changed.

Nexperia’s 74HC/HCT123 formula is tw = 0.45 × R × C at 5 V, for C above 10 nF. A retrigger is ignored until trtrig = 30 + 0.19 × R × C nanoseconds. That ratio is 0.42. A pulse long enough to cover a missed edge (more than 160 ms) also ignores the next edge, which arrives at 80 ms. A window that both retriggers at 80 ms and drops out after one missed edge does not survive the capacitor tolerance. The 74HCT123 is not fitted.

The watchdog is one CD74HCT14E, powered from the 5 V rail so its input threshold is a legal high for a 3.3 V GPIO. GPIO1 is pulled down by 100 kΩ and inverted. A 330 Ω / 220 nF edge into a 10 kΩ pull-up makes a pulse of about 1 ms on the rising edge of the heartbeat only. That pulse turns on a BC547B and dumps a 2.2 µF film capacitor. The capacitor then charges through 470 kΩ. While the capacitor is still below the Schmitt threshold, the series IRLZ44N stays on. A stuck-high or stuck-low GPIO produces one edge and then the rail turns off.

The calculated dropout, with a 1 percent resistor, a 10 percent film capacitor and the TI threshold span, is 231 ms to 705 ms. The long corner is over the original 475 ms limit, and over half a second. The earlier 660 ms figure is not that long corner. No resistor that fits the film footprint can hold the long corner under 475 ms and the short corner over two 100 ms intervals. R_TIME stays 470 kΩ. The working is in `docs/home_purchase.md`. Time the first board. The output is off if the heartbeat stops. It does not latch off.

## Coil switches and the fuse

The ESP32 pin does not drive the IRLZ44N. Its minimum high is about 2.6 V, and the IRLZ44N has no RDS(on) specification at 3.3 V. A CD74HCT125E on the 5 V rail does. Its minimum high output, with the 100 kΩ pulldown, is about 4.4 V. The IRLZ44N specifies 35 mΩ at 4.0 V and 25 mΩ at 5.0 V. The gate resistor is 470 Ω so a fault that drives both buffer outputs into each other stays under the 35 mA pin limit. Each request also clamps the other gate with a BC547B, so both requests on holds both gates off.

The three IRLZ44N devices are low-side. The series device is held on by the watchdog. The up and down devices each feed one relay coil. The tabs are drains. They are not bolted together and they are not bolted to ground.

The coil fuse is a SIBA 70-007-33/0.4A, a 400 mA fast ceramic 5×20 cartridge. It is the lowest current in the 179021 series with a published interrupting current of 1500 A at 250 VDC. No 250 mA 5×20 cartridge found for this buy has a DC interrupting current, and the Littelfuse 0235.250HXP is not the part to order. Pre-arcing I²t is 0.07 A²s. Total clearing I²t is not published; the check uses twice that, 0.14 A²s. The energy in each IRLZ44N is then 4.9 mJ at 35 mΩ, against an avalanche rating of 210 mJ, and the FET stays in the RDS(on) region at a few tenths of a volt. The working is in `docs/home_purchase.md`. The 2 A fuse in the controller branch is 0217002.HXP. It is not the coil protection. Normal coil current is 42 mA, and both coils at 18 V are 125 mA, which is under the 400 mA fuse. A fault between 250 mA and 400 mA will not open it.

The reverse-polarity devices are IRF9540N, one per branch, source toward the load, gate pulled to ground and clamped near −12 V by a BZX55C12. The TVS on each fused rail is a P6KE18A. It is an 18 V part and it is not load-dump protection. The OKI absolute maximum of 36 V is why this clamp is acceptable.

## DevKit power

The OKI-78SR-5/1.5-W36H-C makes 5.0 V from 7 V to 36 V. The HCT logic, the MEJ2 modules and the OKI stay on that rail. Only the DevKit 5 V pin is fed through a 1N5817, anode at the OKI, cathode at the DevKit. A genuine DevKitC-1 v1.1 already has a 1N5819 from each USB socket onto its 5 V rail, so USB does not back-feed the OKI. Some clone boards replace that diode with a 0 Ω link. The series 1N5817 still stops a clone from back-feeding the OKI. Do not also feed the DevKit 3V3 pin. The 3.3 V parts draw from the DevKit regulator. Program from the DevKit USB socket with the 12 V plug out.

Buy an ESP32-S3-DevKitC-1-N16R8. The current image is built for 16 MB of flash with PSRAM left disabled. GPIO0, GPIO3, GPIO19, GPIO20, GPIO35–37, GPIO43, GPIO44, GPIO45 and GPIO46 are not connected. GPIO38 is the on-board LED and is left open.

## Isolation

This is functional isolation, the same boundary as v2. It is not a marine safety barrier. The Murata MEJ2 hipot is 5.2 kVDC for one second and 2.4 kVDC continuous. The UL recognition on the module is basic or supplementary at 200 Vrms and is not cited as a safety barrier.

REED_RET, UP_RET, DN_RET and GND_CAN do not join GND or each other. The two dry contacts are independent: the commons are not tied, and the normally-closed pins are open. On the two-layer board the field nets stay in the right-hand column. A milled slot under each optocoupler and each MEJ2 is a real cut, and the router keepout around each slot is larger than the cut so copper stays 0.5 mm off the mill. Domain-to-domain clearance is 0.6 mm. Clearance inside one domain is 0.2 mm, because a TO-92 has its three pins 2.54 mm apart and a 0.6 mm rule does not fit on the transistor itself.

The reed blanker is the same rule as v2. Loss of the field supply forces GPIO6 low and holds it there. The latch clears only when the field supply is up and the reed has been low. The next rising edge is the one the firmware counts. The CAN path is the MCP2562 on the isolated 5 V rail, with a 6N137 in each direction. There is no 120 Ω terminator across CANH and CANL. The publish jumper ships open, and a GPIO high cannot power the converter.

## Assembly

Every part is through-hole, or it is a finished module with through-hole pins. The labelled drawing is `docs/images/windlass_home_placement.svg`. A red square is pad 1.

The diode band goes in the red square. The LED flat is the cathode and goes in the red square. The electrolytic stripe is the other hole. TO-220 leads, marking toward you, are gate, drain, source, and the tab is the drain. Do not bolt the tabs together.

The square pad of a TO-92 is the collector. The parts in the buy list are onsemi, which are emitter, base, collector with the flat toward you, so the right-hand lead is the one that goes in the square. A Nexperia C-B-E part faces the other way. Match the bag, not a single flat-direction rule.

DIP pin 1 is the red square. The DevKit USB end is pin 1 of each socket, which is the end nearer the connector edge. Fit the shunt on JP_REED pins 1-2 and leave the CAN publish jumper open. The coil holder gets the SIBA 400 mA fast cartridge. The controller holder gets 0217002.HXP, which is the fast-acting 217 series. J_PWR is one Phoenix 1984617. Each 4-pin terminal is two of those blocks snapped together.

## Cost for one controller

The manufacturing package, the quotes, and the line-by-line buy list are in `docs/home_purchase.md` and `docs/home_assembly_bom.csv`. Gerbers are in `fab/home/windlass_home_gerbers.zip`.

The priced lines, including the five-board JLCPCB minimum delivered to Australia, add to **A$220.63**. DigiKey delivery is A$0. Postage on the DevKit and on the 220 nF disc is not published and is not in that sum. Nothing was ordered.

## Before installation

Time the watchdog dropout on the first board. The calculated long corner is 705 ms, which is over the original 475 ms limit, and the resistor was not changed. Confirm the 400 mA fuse opens on a dead short without damaging the IRLZ44N. Confirm the OKI starts on the fast 2 A fuse. Confirm a clone DevKit does not back-feed the OKI through the 1N5817. The firmware and the v2 board stay as they are.
