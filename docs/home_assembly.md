# Home-assembly controller

24 November 2026, Sydney time. This is the finished through-hole design. It is not an order. Bench-test the first board before it is installed.

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

The bounds, using the HCT threshold at 4.5 V to 5.5 V and a 10 percent capacitor, are roughly 250 ms to 540 ms with no allowance yet for the input leakage. Leakage of 1 µA in 470 kΩ is about half a volt, so the first board has to be timed. Three missed edges are the short-case dropout. The output is off if the heartbeat stops. It does not latch off.

## Coil switches and the fuse

The ESP32 pin does not drive the IRLZ44N. Its minimum high is about 2.6 V, and the IRLZ44N has no RDS(on) specification at 3.3 V. A CD74HCT125E on the 5 V rail does. Its minimum high output, with the 100 kΩ pulldown, is about 4.4 V. The IRLZ44N specifies 35 mΩ at 4.0 V and 25 mΩ at 5.0 V. The gate resistor is 470 Ω so a fault that drives both buffer outputs into each other stays under the 35 mA pin limit. Each request also clamps the other gate with a BC547B, so both requests on holds both gates off.

The three IRLZ44N devices are low-side. The series device is held on by the watchdog. The up and down devices each feed one relay coil. The tabs are drains. They are not bolted together and they are not bolted to ground.

The coil fuse is a Littelfuse 0235 series 250 mA fast-acting 5×20 cartridge, ordered as 0235.250HXP for the holder. The series cold resistance is 2.25 Ω and the nominal melting I²t is 0.0166 A²s. A dead short from 12 V is about 5 A, so the melt time is about 0.7 ms. The FET energy in that interval, at the 4 V RDS, is under a millijoule. That is why the gate has to be at the 4 V specification and not at 3.3 V. The 0.0022 A²s figure belongs to the v2 1206 fuse and does not apply here. Opening time is a first-board measurement. The 2 A fuse in the controller branch is a Littelfuse 217 series time-lag cartridge, 0217002.HXP, sized for the converter inrush rather than for the coils. Normal coil current is 42 mA, and both coils at 18 V are 125 mA, under the 250 mA fuse.

The reverse-polarity devices are IRF9540N, one per branch, source toward the load, gate pulled to ground and clamped near −12 V by a BZX55C12. The TVS on each fused rail is a P6KE18A. It is an 18 V part and it is not load-dump protection. The OKI absolute maximum of 36 V is why this clamp is acceptable.

## DevKit power

The OKI-78SR-5/1.5-W36H-C makes 5.0 V from 7 V to 36 V. The HCT logic, the MEJ2 modules and the OKI stay on that rail. Only the DevKit 5 V pin is fed through a 1N5817, anode at the OKI, cathode at the DevKit. A genuine DevKitC-1 v1.1 already has a 1N5819 from each USB socket onto its 5 V rail, so USB does not back-feed the OKI. Some clone boards replace that diode with a 0 Ω link. The series 1N5817 still stops a clone from back-feeding the OKI. Do not also feed the DevKit 3V3 pin. The 3.3 V parts draw from the DevKit regulator. Program from the DevKit USB socket with the 12 V plug out.

Buy an ESP32-S3-DevKitC-1-N16R8. The current image is built for 16 MB of flash with PSRAM left disabled. GPIO0, GPIO3, GPIO19, GPIO20, GPIO35–37, GPIO43, GPIO44, GPIO45 and GPIO46 are not connected. GPIO38 is the on-board LED and is left open.

## Isolation

This is functional isolation, the same boundary as v2. It is not a marine safety barrier. The Murata MEJ2 hipot is 5.2 kVDC for one second and 2.4 kVDC continuous. The UL recognition on the module is basic or supplementary at 200 Vrms and is not cited as a safety barrier.

REED_RET, UP_RET, DN_RET and GND_CAN do not join GND or each other. The two dry contacts are independent: the commons are not tied, and the normally-closed pins are open. On the two-layer board the field nets stay in the right-hand column. A milled slot under each optocoupler and each MEJ2 is a real cut, and the router keepout around each slot is larger than the cut so copper stays 0.5 mm off the mill. Domain-to-domain clearance is 0.6 mm. Clearance inside one domain is 0.2 mm, because a TO-92 has its three pins 2.54 mm apart and a 0.6 mm rule does not fit on the transistor itself.

The reed blanker is the same rule as v2. Loss of the field supply forces GPIO6 low and holds it there. The latch clears only when the field supply is up and the reed has been low. The next rising edge is the one the firmware counts. The CAN path is the MCP2562 on the isolated 5 V rail, with a 6N137 in each direction. There is no 120 Ω terminator across CANH and CANL. The publish jumper ships open, and a GPIO high cannot power the converter.

## Assembly

Every part is through-hole, or it is a finished module with through-hole pins. A conventional iron can solder all of it. Match each TO-92 flat to the silk. The BC547 and BC557 leads, flat toward you, are collector, base, emitter. The IRLZ44N and IRF9540N leads, marking toward you, are gate, drain, source. The diode silk marks the cathode.

## Cost for one controller

Prices were read on 24 November 2026. element14 Australia shows an ex-GST price and a GST-inclusive price in brackets. DigiKey Australia shows both. No currency was converted. Shipping is not included. Nothing was ordered.

| Part | Qty | GST-inclusive | Source |
| --- | --- | --- | --- |
| ESP32-S3-DevKitC-1-N16R8 | 1 | $30.95 listed | Phipps Electronics, in stock in Australia. The page does not say whether GST is included, and one bullet swaps the flash and PSRAM sizes. The body text says 16 MB flash and 8 MB PSRAM. Confirm the module is marked N16R8. The seller is a generic board, not an Espressif box. |
| OKI-78SR-5/1.5-W36H-C | 1 | $10.252 | element14 Australia 2812636 |
| MEJ2S0505SC | 1 | $16.929 | DigiKey Australia 811-2397-ND |
| MEJ2S0503SC | 1 | $18.887 | element14 Australia 2429477 |
| Finder 40.31.7.012.0000 | 2 | $40.502 | element14 Australia 1169158 |
| IRLZ44NPBF | 3 | $8.778 | DigiKey Australia IRLZ44NPBF-ND |
| IRF9540NPBF | 2 | $8.932 | DigiKey Australia IRF9540NPBF-ND |
| MCP2562-E/P | 1 | $2.123 | DigiKey Australia MCP2562-E/P-ND |
| 6N137, DIP-8, Everlight | 2 | $6.798 | DigiKey Australia 1080-1485-ND. Same JEDEC part: 5000 Vrms, 75 ns. |
| CD74HCT14E | 1 | $1.430 | element14 Australia 3120225 |
| SN74HC00N | 1 | $1.287 | element14 Australia 3120419 |
| PC817X1J000F | 4 | $1.628 | element14 Australia 9707697 at $0.370 ex GST. The page rounded the GST bracket, so 10 percent was applied here. |
| 0235.250HXP, 250 mA fast 5×20 | 1 | $2.409 | element14 Australia 1192542. Cartridge form of the 0235 series for the fuse holder. |

Those lines add to **A$150.91** if the DevKit’s $30.95 already includes GST, or **A$119.96** without the DevKit. The full list, including the lines with no retrieved price, is `docs/home_assembly_bom.csv`.

These parts are on the board and did not have an Australian price on the pages retrieved today. They are not free.

- CD74HCT125E in DIP-14. element14 Australia has no listing for that exact part. Any 74HCT125 in DIP-14, run from 5 V, is the same function.
- SN74HC08N in DIP-14. element14 Australia has no listing. Any 74HC08 in DIP-14 is the same function. It runs from the DevKit 3.3 V rail.
- The 2 A time-lag 5×20 cartridge, Littelfuse 217 series, ordering code 0217002.HXP. The axial-lead twin is 0217002.MXP. The holder takes the cartridge.
- Two 5×20 fuse holders, Schurter 0031.8201 or the same open horizontal holder.
- BC547B (four) and BC557B (one).
- 1N5817 (two), 1N5819 (three), 1N4148 (three), BAT46 (four), P6KE18A (two), BZX55C12 (two).
- The axial resistors, the two 1 W resistors (51 Ω and 120 Ω), the disc capacitors, the radial electrolytics and the 2.2 µF film capacitor. Values are in the CSV.
- One red and one green 5 mm LED.
- Two 22-pin female socket strips at 2.54 mm.
- The KF350 and JST XH headers on the board, and the mating housings used by the existing wiring schedule.
- The bare board. Five two-layer boards of 100 mm by 100 mm or smaller have a published JLCPCB price that does not apply here, because both sides are over 100 mm. No quote was taken.

## Before installation

Time the watchdog dropout on the first board. Confirm the 250 mA fuse opens on a dead short without damaging the IRLZ44N. Confirm a clone DevKit does not back-feed the OKI through the 1N5817. The firmware and the v2 board stay as they are.
