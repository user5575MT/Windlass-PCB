# JLCPCB order

23 November 2026, Sydney time (AEDT, UTC+11). Catalogue prices and stock were read at 7:08 pm. No order was placed. The board file `kicad11/windlass_install_v2.kicad_pcb` and the firmware were not changed.

Upload `fab/jlcpcb/windlass_install_v2_gerbers.zip`, `fab/jlcpcb/bom_smt.csv`, and `fab/jlcpcb/cpl.csv`. The assembly build is 5 boards, top side only, Standard PCBA. The through-hole parts and the two switches are on `fab/jlcpcb/purchase_hand.csv` and are soldered by hand.

This is a catalogue snapshot, not a quotation and not a reservation. Stock and the price ladder move. The live JLCPCB quote can differ, and it is the price that gets paid.

## What has to be accepted with this upload

These are purchasing facts. They are already applied in the files.

- C30A and C30C are Samsung CL21A226MAQNNNE, C45783: 22 µF, 25 V, X5R, ±20%, 0805, basic library. The design asks for 22 µF, 16 V or higher, X7R. The assembly library has no 0805 22 µF X7R reel at 16 V or higher. X5R is specified to 85 °C, which is the board's ambient limit. The 25 V rating is the one used, because of DC bias at 3.3 V.
- F_COIL is Littelfuse 0466.250NRHF, C83557: 250 mA, 125 V, I²t 0.0022, 1206. F_MCU is Littelfuse 0466002.NRHF, C3105: 2 A, 63 V, 1206. The NR reels (C206986 and C187595) have stock 0. NRHF is the halogen-free reel of the same series and the same ratings. The 63 V MCU fuse is above the SMAJ18A clamp, about 29.2 V, on the 12 V branch.
- C50 is TDK C3216X7R1H335KT000E, C342695: 3.3 µF, 50 V, X7R, ±10%, 1206. The named Murata GRM31CR71H335KA88L is not in the catalogue.
- Every 0402 100 nF, including C92, is Samsung CL05B104KB54PNC, C307331: 100 nF, 50 V, X7R, ±10%, basic. One reel covers the 50 V requirement on C92 and the "16 V or higher" parts.
- The Schottky diodes are Yangjie BAT54W, C699107: SOD-123, 30 V, 200 mA, 600 mA surge, Vf about 1 V at 100 mA. Pad centers match the SOD-123 land at rotation 0 within 0.05 mm. Nexperia BAT54W,115 is an SC-70 part and the listing has five pieces, so it is not the reel.
- 1N4148W is the basic reel C81598: 75 V, 150 mA, 4 ns. The catalogue calls the package SOD-123. The library land is the SOD-123F outline, and its pad centers sit within 0.09 mm of this board's SOD-123 land.
- J_CONTACT and J_PERM are XY350V-3.5-4P, C557656: 7 A, 300 V, 3.5 mm. The four holes match the drawn KF350 land (the library origin sits 5.25 mm from the KiCad centre, and the pitch error is 0). The drawn KF350-3.5-4P listing has no stock. The contact path is the boat's 2.5 A fuse, so 7 A is above the circuit current and below the 10 A rating of the part that was drawn.
- SW_BOOT and SW_RST stay the exact E-Switch TL3342F160QG and are hand soldered. JLCPCB C2886898 has one piece in stock. The library land for that listing misses this custom footprint by about 3 mm, so it is not a machine placement.
- U20 AP63203WU-7, C780769, has 17 pieces in stock and a minimum purchase of 7. Five boards need 7 pieces. That covers this run and leaves little spare.
- The order is Standard PCBA. C2913199, the ESP32-S3-WROOM-1-N16, is `componentProductType` 2. An Economic assembly search does not return it.

## SMT parts

Each row was matched on value, package, and the electrical rating in `docs/integrated_bom.md`, then checked against the JLCPCB assembly catalogue. Stock below is the 7:08 pm reading. "Buy" is the larger of five boards times the quantity on one board, the assembly minimum (`leastPatchNumber`), and the shop minimum. The unit price is the ladder step for that buy quantity.

Library footprints used for the pad check are from the JLCEDA/EasyEDA official library, https://lceda.cn/ and https://easyeda.com. Pad positions were compared. The footprint drawings were not copied into this repository.

| LCSC | MPN | On one board | Buy | Stock | Library | Unit USD | Line USD |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| C28323 | CL21B105KBFNNNE | 1 | 20 | 3,857,124 | basic | 0.0279 | 0.56 |
| C3039694 | CL21B106KAYQNNE | 1 | 5 | 115,645 | extended | 0.0932 | 0.47 |
| C307331 | CL05B104KB54PNC | 16 | 80 | 20,098,240 | basic | 0.0086 | 0.69 |
| C1523 | 0402B102K500NT | 1 | 20 | 3,839,248 | basic | 0.0017 | 0.03 |
| C45783 | CL21A226MAQNNNE | 2 | 10 | 4,727,862 | basic | 0.1084 | 1.08 |
| C21397 | GRM32ER71E226KE15L | 1 | 5 | 61,174 | extended | 0.3502 | 1.75 |
| C342695 | C3216X7R1H335KT000E | 1 | 5 | 6,076 | extended | 0.4209 | 2.10 |
| C699107 | BAT54W | 5 | 25 | 18,951 | extended | 0.0272 | 0.68 |
| C81598 | 1N4148W | 2 | 15 | 4,428,544 | basic | 0.0123 | 0.18 |
| C2480 | SS14 | 2 | 10 | 1,161,569 | basic | 0.0192 | 0.19 |
| C125094 | LTST-C190KGKT | 1 | 20 | 424,811 | extended | 0.0185 | 0.37 |
| C94869 | LTST-C190KRKT | 2 | 20 | 100,068 | extended | 0.0216 | 0.43 |
| C148219 | SMAJ18A | 2 | 10 | 8,797 | extended | 0.1141 | 1.14 |
| C43491 | BZT52C12 | 2 | 15 | 196,103 | extended | 0.0212 | 0.32 |
| C83557 | 0466.250NRHF | 1 | 5 | 46,220 | extended | 0.0894 | 0.45 |
| C3105 | 0466002.NRHF | 1 | 5 | 48,275 | extended | 0.0727 | 0.36 |
| C3020560 | USB4105-GF-A | 1 | 5 | 5,043 | extended | 1.0211 | 5.11 |
| C2045238 | SRN6045-3R3Y | 1 | 5 | 473 | extended | 0.5269 | 2.63 |
| C282405 | 2N7002BK,215 | 2 | 10 | 33,862 | extended | 0.0310 | 0.31 |
| C179399 | NX3008NBK,215 | 2 | 10 | 33,201 | extended | 0.0382 | 0.38 |
| C154901 | DMP6023LE-13 | 2 | 10 | 2,460 | extended | 0.7855 | 7.86 |
| C95063 | ZXMS6004FFTA | 3 | 15 | 6,257 | extended | 0.4926 | 7.39 |
| C25744 | 0402WGF1002TCE | 10 | 50 | 34,426,704 | basic | 0.0010 | 0.05 |
| C25741 | 0402WGF1003TCE | 16 | 80 | 11,825,794 | basic | 0.0009 | 0.07 |
| C25905 | 0402WGF5101TCE | 2 | 20 | 4,095,561 | basic | 0.0014 | 0.03 |
| C25092 | 0402WGF220JTCE | 2 | 20 | 7,077,622 | basic | 0.0011 | 0.02 |
| C26083 | 0402WGF1004TCE | 1 | 20 | 3,436,786 | basic | 0.0010 | 0.02 |
| C25900 | 0402WGF4701TCE | 3 | 20 | 12,297,801 | basic | 0.0017 | 0.03 |
| C25792 | 0402WGF4702TCE | 1 | 20 | 5,274,167 | basic | 0.0019 | 0.04 |
| C137021 | RC2512FK-0751RL | 1 | 5 | 13,495 | extended | 0.0727 | 0.36 |
| C25076 | 0402WGF1000TCE | 1 | 20 | 9,794,142 | basic | 0.0011 | 0.02 |
| C17901 | 1206W4F1000T5E | 2 | 15 | 1,743,685 | basic | 0.0050 | 0.08 |
| C11702 | 0402WGF1001TCE | 2 | 20 | 29,150,345 | basic | 0.0011 | 0.02 |
| C25105 | 0402WGF330JTCE | 1 | 20 | 4,400,944 | basic | 0.0010 | 0.02 |
| C421657 | 25121WF1200T4E | 1 | 5 | 10,654 | extended | 0.0377 | 0.19 |
| C17168 | 0402WGF0000TCE | 3 | 20 | 13,841,933 | basic | 0.0012 | 0.02 |
| C137948 | RC0402FR-07680RL | 2 | 20 | 468,151 | extended | 0.0034 | 0.07 |
| C2671499 | ISO1042BDWR | 1 | 5 | 189 | extended | 6.0168 | 30.08 |
| C513291 | 74LVC1G123DP,125 | 1 | 5 | 3,352 | extended | 0.5580 | 2.79 |
| C455045 | 74LVC1G34GW,125 | 2 | 10 | 3,309 | extended | 0.0896 | 0.90 |
| C12508 | 74LVC1G00GW,125 | 2 | 10 | 1,530 | extended | 0.1769 | 1.77 |
| C780769 | AP63203WU-7 | 1 | 7 | 17 | extended | 1.3451 | 9.42 |
| C2913199 | ESP32-S3-WROOM-1-N16 | 1 | 5 | 1,355 | extended | 4.9106 | 24.55 |
| C2878308 | ISO7720FDR | 1 | 5 | 322 | extended | 2.5429 | 12.71 |
| C55144 | TLP291(GB-TP,SE | 2 | 10 | 331,236 | extended | 0.1126 | 1.13 |
| C7519 | USBLC6-2SC6 | 1 | 5 | 38,866 | extended | 0.1544 | 0.77 |

SMT parts for the purchased quantities: **119.66 USD**. The table is rounded to the cent per line, so the displayed lines add to 119.64 USD. The total is the sum of the unrounded extensions.

Ratings checked against the catalogue text, beyond the package match:

- C10, C28323: 1 µF, 50 V, X7R, ±10%, 0805. The design asks for 1 µF at 16 V or higher.
- C11, C3039694: 10 µF, 25 V, X7R, ±10%, 0805. No basic 16 V reel. The design does not mandate the dielectric.
- C22, C1523: 1 nF, 50 V, X7R, ±10%. The filter value has no voltage callout.
- C30I, C21397: Murata GRM32ER71E226KE15L, 22 µF, 25 V, X7R, ±10%, 1210. This is the specified reel.
- R60 and R70, C17901: 100 Ω, 1%, 250 mW, 200 V, 1206.
- R24, C137021: 51 Ω, 1%, 1 W, 2512. Dissipation at 3.3 V is about 0.21 W, inside the 0.5 W the design asks for.
- R94, C421657: 120 Ω, 1%, 1 W, 2512. The 5 V preload is about 0.21 W.
- R_G and R_R, C137948: 680 Ω, 1%, 62.5 mW. There is no basic 1% reel.
- Other 0402 resistors are UNI-ROYAL 1% thick film, 62.5 mW, 50 V, basic library.
- SS14, C2480: MDD, 40 V, 1 A, SMA.
- SMAJ18A, C148219: Littelfuse, unidirectional, 18 V standoff, 29.2 V clamp at 10/1000 µs, 400 W.
- BZT52C12, C43491: 11.4 V to 12.7 V, 500 mW. The Diodes 370 mW reel was not used.
- LEDs are Lite-On LTST-C190KGKT and LTST-C190KRKT. Pin 1 matches at rotation 0.
- L20, C2045238: Bourns SRN6045-3R3Y, 3.3 µH, Isat 5 A, Irms 3.2 A, ±30%. The library footprint request returned no drawing. The land is two terminals, so 0° and 180° are the same circuit. The centroid keeps the KiCad angle, 0°.
- USB4105-GF-A, C3020560: GCT top-mount USB 2.0 receptacle, the part the KiCad footprint `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` is drawn for. Stake option blank is 0.95 mm and uses the same land and the same two 0.65 mm locating holes. The catalogue short text says 12P; the GCT drawing is 16 positions.
- ESP32-S3-WROOM-1-N16 is the 16 MB part with no PSRAM. It is not the N16R8.
- ISO7720FDR, C2878308, is the narrow SOIC-8, 3000 Vrms. The wide-body 5000 Vrms part was not substituted.
- ISO1042BDWR is the SOIC-16 wide body, 7.5 mm.
- TLP291(GB-TP,SE is the Toshiba GB CTR reel. Pins are 1 anode, 2 cathode, 3 emitter, 4 collector.
- NX3008NBK: pin 1 gate, pin 2 source, pin 3 drain.
- DMP6023LE-13: pin 1 gate, pin 2 drain, pin 3 source, tab drain. The library calls the tab pin 4. At 180° the tab lands on the KiCad tab.
- ZXMS6004FFTA: pin 1 drain, pin 2 IN, pin 3 source. The part is SOT-23F on the SOT-23 land already used by this board. Pad centers are about 0.3 mm further out along the lead.
- 74LVC1G34GW and 74LVC1G00GW are the Nexperia GW reels. The catalogue short text says TSSOP-5. The library land is SOT-353 at 0.65 mm pitch, which is this board's land.
- 2N7002BK,215 is the Nexperia SOT-23 reel.

## Pick and place

`cpl.csv` has the 112 machine-placed parts, all on the top. The six test points and the four M3 holes are not in it. Hand-fitted designators are not in it: JP1, JP_REED, J_CONTACT, J_PERM, J_NMEA, J_SENSE, J_PWR, J_REED, K_DN, K_UP, U4, U9, SW_BOOT, SW_RST.

Chip resistors, chip capacitors, SOD-123, SOD-123F, SMA, the LEDs, and the 1206 fuses match the library land at the KiCad rotation. The worst passive residual is the SMAJ18A pads, 0.19 mm along the land, at rotation 0.

These parts need a JLCPCB rotation other than the KiCad angle. Both tools take counterclockwise as positive. The angle below is what `cpl.csv` contains. On this board each of these footprints is placed at KiCad rotation 0, so the file angle is the correction itself.

| Footprints | Designators | CPL rotation |
| --- | --- | ---: |
| SOT-23 | Q_BLK, Q_NPG, Q_CLAMP_DN, Q_CLAMP_UP, Q_DN, Q_SERIES, Q_UP | 180 |
| SOT-223, tab is pin 2 | Q_COIL, Q_MCU | 180 |
| SOT-353 | U12, U15, U13, U14 | 180 |
| SOP-4, TLP291 | U6, U7 | 180 |
| TSSOP-8, 74LVC1G123 | U11 | 90 |
| TSOT-23-6, AP63203 | U20 | 90 |
| SOT-23-6, USBLC6-2SC6 | U_ESD | 90 |
| SOIC-8, ISO7720FDR | U5 | 90 |
| SOIC-16W, ISO1042BDWR | U10 | 0 |

Where a residual remains after that rotation, it is along the long axis of the pad and the pitch matches. Measured residuals: 74LVC1G34 0.01 mm, 74LVC1G00 0.21 mm, 74LVC1G123 0.25 mm, AP63203 0.06 mm, USBLC6 0.01 mm, ISO7720 0.23 mm, TLP291 0.25 mm, DMP6023 0.32 mm, ISO1042 0.54 mm (the library pad centers sit further out, symmetric, and a 2 mm pad still covers them). The 0° and 180° alternatives for the parts that needed 90° are several millimetres off, so those are not pad-length effects.

J_USB and U3 stay at rotation 0, and their centroids move so the library origin sits on the copper rather than on the KiCad origin.

- J_USB is 20.0000, −14.6923. The KiCad origin is 20, −16. After the 1.3077 mm shift, the 16 signal pins (A1, A4–A9, A12, B1, B4–B9, B12) land within 0.15 mm. The remaining error is across the pad, not along the connector.
- U3 is 148.0000, −49.6267. The KiCad origin is 148, −46. After the 3.6267 mm shift, pads 1 through 40 land within 0.03 mm. The module ground pad is the same part and moves with them.

L20 stays at its KiCad centroid and rotation 0, as noted above.

## Hand-fitted parts

Solder these by hand. They are listed in `fab/jlcpcb/purchase_hand.csv` and they are omitted from `bom_smt.csv` and `cpl.csv`. JLCPCB connector prices are the same 7:08 pm catalogue. Distributor prices are public listings read the same evening and are not quotations. Distributor shipping is not included. TME's displayed price includes the duties and tariffs they state on the page.

| Parts | Buy for 5 boards | Source | Line USD |
| --- | ---: | --- | ---: |
| JP1, 1×2 header, C32713268 | 5 | JLCPCB | 0.08 |
| JP_REED, 1×3 header, C49257 | 5 | JLCPCB | 0.15 |
| J_CONTACT, J_PERM, XY350V-3.5-4P, C557656 | 10 | JLCPCB | 3.00 |
| J_NMEA, J_SENSE, B5B-XH-A(LF)(SN), C157991 | 10 | JLCPCB | 0.90 |
| J_PWR, KF350-3.5-2P, C474892 | 5 | JLCPCB | 0.60 |
| J_REED, B4B-XH-A(LF)(SN), C144395 | 5 | JLCPCB | 0.26 |
| K_DN, K_UP, Finder 40.31.7.012.0000 | 10 | TME, 931 listed, 3.99 USD at 10 | 39.90 |
| U4, Murata MEJ2S0303SC | 5 | DigiKey 811-2400-ND, 53 listed, 9.83 USD | 49.15 |
| U9, Murata MEJ2S0305SC | 5 | DigiKey 811-2399-ND, 164 listed, 9.83 USD | 49.15 |
| SW_BOOT, SW_RST, TL3342F160QG | 10 | TME, 1,416 listed, 0.48 USD at 10 | 4.80 |
| One 2.54 mm shunt on JP_REED pins 1–2 | 5 | no order code selected | unavailable |

JLCPCB hand-fit parts: **4.99 USD**. Distributor listings that have a price: **143.00 USD**. The shunt price is unavailable.

Fit JP1 open. Fit the shunt on JP_REED pins 1 and 2 for a Lofrans chain counter, and do not solder the shunt. Hand-solder JST pin 1 to the silkscreen. The header and JST hole pitches match the library parts with a pitch error of 0; the library origin is the pin-1 end, and the KiCad origin is the centre of the connector.

Buy the Finder part and both Murata modules as those exact MPNs. U4 does not appear in the JLCPCB catalogue. U9's listing C5457212 has stock 0. The Finder listing C6389061 has stock 0. TTI lists both Murata modules lower (7.97 USD and 7.86 USD, 25 pieces each). Newark lists the Finder relay at 8.46 USD. The totals above use DigiKey for the modules and TME for the relay and the switches.

## Gerbers and drills

A fresh KiCad 10.0.8 plot of `kicad11/windlass_install_v2.kicad_pcb` was compared with this zip. After removing comment and attribute lines, top copper, inner 1, inner 2, bottom copper, both paste layers, both mask layers, and the outline are the same file. The plated drill has the same hits as the plot made at 6:14 pm AEDT; the new header differs only by the KiCad timestamp, 6:59 pm AEDT. The same is true of the non-plated drill. Tools in the plated file are 0.30, 0.50, 0.60, 0.95, 1.00, and 1.50 mm. Non-plated tools are 0.65 mm (the USB locating holes) and 3.20 mm (the four M3 holes).

The silkscreen in the earlier zip added pad-shaped flashes on top of the legend: 409 on the top, 57 on the bottom. A normal silk plot of this board has the same 1,842 legend strokes on the top and an empty bottom. This zip uses that plot. Copper, paste, mask, outline, and drills are unchanged by that.

The outline is a 200 mm by 160 mm rectangle. The Gerber origin is the KiCad absolute origin, and `cpl.csv` uses that origin.

## Cost for 5 boards

Assembly fees are the published JLCPCB Standard, single-sided schedule from the help page "PCB Assembly Cost", last updated 22 October 2026 and read on 23 November 2026. They move slightly with exchange rates. Coupons are not applied.

| Line | USD | Basis |
| --- | ---: | --- |
| SMT parts, purchased quantities | 119.66 | catalogue ladder at 7:08 pm AEDT |
| Setup, single sided | 25.56 | published Standard fee |
| Stencil | 8.21 | published Standard fee |
| Feeder loading, 46 part numbers | 70.38 | 1.53 USD each, basic and extended, on Standard |
| SMT joints, 348 per board | 2.78 | 0.0016 USD × 348 × 5 |
| Assembly process | 106.93 | setup, stencil, loading, joints |
| **Parts plus assembly process** | **226.59** | |
| Fixture, if charged | 16.42 | published as 8.21 USD × 2 fixtures for 1–29 rigid boards. Confirm on the quote. |
| Parts plus process, if the fixture is charged | 243.01 | |

The joint count is the number of distinct copper-pad centres on the 112 machine-placed parts. The per-board joint charge is 0.5568 USD, which is above the 0.48 USD single-board minimum, so that surcharge is not added. The board is 320 cm², under the 650 cm² large-board fee. No hand-soldering labour is included, because the through-hole parts are not being sent to JLCPCB for soldering.

| Also required, outside the assembly line | USD |
| --- | ---: |
| Connectors and headers from JLCPCB, not assembled | 4.99 |
| Relays, Murata modules, and switches, from the listings above | 143.00 |
| Five 2.54 mm shunts | unavailable |
| PCB fabrication, 200 × 160 mm, 4 layer, 1.6 mm | unavailable |
| Shipping | unavailable |
| Tax | unavailable |

The fabrication price was not returned. JLCPCB's quote interface needs an account and an uploaded Gerber key, and this session did not place that request. No fabrication number is estimated here.

Adding the priced lines, and leaving the fixture, the shunts, fabrication, shipping, and tax out: **374.58 USD**. Adding the fixture line if the quote charges it: **391.00 USD**. Either figure is short of a finished delivered cost by the unavailable lines.
