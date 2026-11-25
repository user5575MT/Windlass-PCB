# DigiKey cart, DevKitC-1 kept

25 November 2026, Sydney time (AEDT, UTC+11). Nothing was ordered, nothing was flashed, and no copper was routed. The home-assembly board on the parent branch is the checkpoint and was not edited.

DigiKey Australia is the component supplier. The ESP32-S3-DevKitC-1 is the only part bought elsewhere. The SparkFun Thing Plus is not in this cart.

The opened lines add to **A$209.36** for one controller. That figure pays for every DigiKey line below, DigiKey delivery, one DevKit, and the five-board JLCPCB quote already on the checkpoint. One green 5 mm LED was not the page that came back, so it is not in the sum.

## Delivered cost

| Parcel | What | AUD |
|---|---|---|
| DigiKey Australia | Every line in the table below, GST included | 149.71 |
| DigiKey delivery | A$0. The goods are over the A$60 including-GST threshold. Under that, delivery is A$24. | 0.00 |
| Phipps Electronics | One ESP32-S3-DevKitC-1-N16R8. The published price is A$30.95. Standard post on an order under A$35 is A$0 and is untracked stamped mail. Tracked parcel post is quoted at checkout and is not in this sum. | 30.95 |
| JLCPCB | Five boards, the checkpoint quote, USD 19.02, A$28.70 at the rate already used on that quote. The quote shows no GST. It is the old 120 mm × 112 mm outline, used here only until this board has its own outline. | 28.70 |
| | **One controller** | **209.36** |

Minimum order quantity is 1 on every DigiKey line. Where a line buys more than it fits, that is the quantity break, not a minimum.

## DevKitC-1

DigiKey Australia still has no PCB-antenna DevKitC-1 in stock. Phipps Electronics, an Australian shop, lists ESP32-S3-DevKitC-1-N16R8 at A$30.95 with 3 in stock and all stock in Australia. The specifications on that page are ESP32-S3-WROOM-1, 16 MB flash, 8 MB PSRAM, dual USB-C, 44 pins. One bullet on the same page swaps the flash and PSRAM figures. The specifications section is the one used here. The brand field says unbranded, so this is not an Espressif carton. The listed body is 53 mm × 20 mm, shorter than Espressif's own DevKitC-1, so the row spacing of the two 22-pin headers is measured on the board that arrives before any socket is placed.

The module is N16R8. The existing image is built for 16 MB with PSRAM disabled. No source change and no build-option change. Nothing is flashed.

The PCB takes two 22-pin sockets, PPPC221LFBN-RC. A 40-pin breakaway covers the two jumpers and is a spare if the DevKit arrives without pins fitted. The controller 5 V pin feeds the DevKit through a series 1N5819, anode at the regulator, so a USB plug on the module cannot back-feed the board. The module 3.3 V pin is not fed.

## Coil rail

The 7812 sits after the ignition loop. An open ignition switch or an open panel switch removes the regulator input and both coils drop. The MCU regulator is on the other fuse.

ST L7812CV, the C version, from the February 2025 datasheet.

- At 25 °C the output is 11.5 V to 12.5 V.
- From 5 mA to 1 A, with the input from 14.5 V to 25 V, the output is 11.4 V to 12.6 V. That row is the one that covers the junction-temperature range of the C table, 0 °C to 125 °C.
- Dropout is 2 V typical at 1 A and 25 °C. No maximum is published at the coil current. Figure 28 shows the 20 mA and 200 mA curves below the 1 A curve. The 2 V figure is used below as a ceiling, and it overstates the drop at about 100 mA.
- The note under the table says the minimum load for regulation is 5 mA. A 1 kΩ bleeder draws 12 mA at 12 V and 0.16 W at 12.6 V, which is inside a 0.25 W resistor.
- Quiescent current is 8 mA maximum at 25 °C. Short-circuit current is 0.35 A typical at 35 V in, and the peak is 2.2 A typical. Neither is a published maximum.
- TO-220 junction-to-ambient is 50 °C/W. The input capacitor is 0.33 µF or larger and low impedance. The output capacitor is 0.1 µF. This cart uses the 1 µF film on the input and a 100 nF ceramic on the output.
- Absolute maximum input is 35 V. The P6KE18A clamps at 25.2 V maximum, so the input survives a clamp.

Omron G2R-1-DC12. Must-operate is 70 percent, 8.4 V maximum, at a coil temperature of 23 °C. Must-release is 15 percent, 1.8 V, at the same temperature. Coil resistance is 275 Ω ±10 percent. The 110 percent maximum is 13.2 V, and the datasheet says that figure is the top of a varying range, not a continuous voltage.

Copper raises the must-operate voltage by about 0.393 percent per degree. That scaling is not an Omron limit. It is the estimate used here.

- A 70 °C coil needs about 9.95 V.
- A 100 °C coil needs about 10.9 V.
- Must-release at a 100 °C coil is about 2.3 V.

While the input is inside the 14.5 V to 25 V window, the output stays between 11.4 V and 12.6 V. 11.4 V is above the 23 °C must-operate and above the 100 °C estimate, so the relay picks up. 12.6 V is 105 percent of rated. That is under 13.2 V. Coil power is about 10 percent above the power at 12.0 V. Omron does not publish a continuous voltage above the rated voltage, and 70 °C is already the top of the ambient range, so a hot coil at 12.6 V is at the edge of what the datasheet describes.

Below 14.5 V the part is outside that window and the output is the input minus the dropout. Using the 2 V typical as a ceiling:

- 12.6 V in leaves at least about 10.6 V, which covers 23 °C and a 70 °C coil, and is short of the 100 °C estimate.
- 12.0 V in leaves at least about 10.0 V, which still covers the 8.4 V guarantee and is about even with a 70 °C coil.
- The real drop at 100 mA is less than the 1 A figure, so the output is higher than these bounds. The datasheet does not give that drop as a maximum.

Holding is not the close call. The output does not approach 2 V while the input is present.

Dissipation, both coils at the low coil resistance and the output at 12.6 V, is 114 mA out of the regulator. Quiescent current is extra and is drawn from the input.

- 14.8 V in: 0.37 W. At 70 °C ambient the junction is about 89 °C.
- 18 V in: 0.76 W. Junction about 108 °C, under the 125 °C limit, in free air.
- A continuous 25.2 V clamp: 1.64 W. Junction about 152 °C at 70 °C ambient, which is over 125 °C. The clamp is a transient. The standoff is 15.3 V and the breakdown starts at 17.1 V, so a charging voltage near 14.8 V does not sit the TVS in conduction. Continuous operation is the battery and alternator range.

One coil at 14.8 V is about 0.26 W.

## Fuses and the MOSFETs

Both fuses are Littelfuse 251, axial, fast, 125 V AC and 125 V DC, interrupting 50 A AC and 300 A DC. The coil fuse is now 0251.500NRT1L, 500 mA, because that rating is one of the rows with published maximum opening times. The 630 mA part only publishes a maximum at 200 percent.

For the 500 mA rating the datasheet says:

- At 100 percent it does not open for at least 4 hours.
- At 200 percent, 1.0 A, it opens within 1 second.
- At 275 percent, 1.375 A, within 300 ms.
- At 400 percent, 2.0 A, within 30 ms.
- At 1000 percent, 5.0 A, within 4 ms.

Nominal melting I²t is 0.0598 A²s. That is not the clearing energy and it is not used as one.

Normal coil-branch current is about 64 mA with one coil and about 107 mA with both, including the bleeder and the regulator quiescent current. That is about a fifth of the fuse rating, inside the 4 hour minimum at 100 percent.

A short on the regulated coil output is limited by the 7812, not by the battery. The published currents are typical: 0.35 A, and a 2.2 A peak. At 2.2 A and the IRLZ44N's 35 mΩ at 4 V, the FET dissipates 0.17 W and sits at about 0.08 V. It is fully on. This does not depend on fuse I²t, and it is not an avalanche event. The maximum short-circuit current is not published, so the claim stops at the typical peak.

The published 4 ms at 5 A, if it were the clearing time with the FET fully on, puts 3.5 mJ in an IRLZ44N at 35 mΩ and 12 mJ in the IRF9540N at 117 mΩ. Above 5 A the datasheet does not publish a shorter maximum time. Up to 300 A the fuse is rated to interrupt, and the let-through time in that band is not published, so the FET energy there is not a closed number. Above 300 A the interrupt rating does not cover the fault. A short heavy battery cable can exceed 300 A, and the boat battery fuse is the interrupt for that fault. Avalanche energy is not used.

The controller fuse stays the 2 A 251. It is on the converter branch. The 2 A rating does have the 4 ms maximum at 1000 percent, which is 20 A. The same limit applies: above that current the opening time is not published, and 300 A is the interrupt rating.

## What stayed

The watchdog is the CD74HCT4538E. Pulse is 0.7 × 470 kΩ × 1 µF, nominally 329 ms. With the resistor at 1 percent, the film at 5 percent, and TI's 0.850 to 1.150 window from the 10 kΩ / 0.1 µF test point, the corners are 263 ms and 401 ms. The long corner is inside 475 ms. The short corner is 1 ms under the firmware constant of 264 ms and is above the 160 ms assert. That window is specified at 10 kΩ and 0.1 µF, so using it here is an extrapolation. Time the first board. GPIO1 stays the heartbeat. The firmware file is not edited.

The relays stay the G2R-1-DC12. The contact rating used here is 5 A at 30 VDC, L/R = 7 ms.

The CAN rail stays the Traco TMR 0511. The October 2026 datasheet gives set accuracy ±1 percent, line 0.2 percent, load 0.5 percent from 10 to 90 percent, and no minimum load. The output stays near 5.1 V, inside the MCP2562 range of 4.5 V to 5.5 V. This is functional isolation, not a safety barrier.

The reed side stays the Recom RFM-0505S. It is unregulated and is not used on the CAN rail. A 220 Ω load keeps it near the 10 percent load its regulation figure is written from. At 5.75 V that resistor dissipates about 0.15 W, inside a 0.25 W part.

The boat still sees two independent dry contacts, a hardware ignition loop, and a hardware panel switch. Neither switch is a GPIO. The contacts do not switch the motor.

## Cart

Prices are Australian dollars, GST included, from DigiKey Australia on 25 November 2026. "Computed" means the page showed the ex-GST quantity price and the including-GST figure is that price plus 10 percent. The footer on those pages shows the 1-piece GST price, so a quantity-break line is marked computed.

| Buy | Fit | Part | DigiKey | Stock | Line inc GST | GST |
|---|---|---|---|---|---|---|
| 2 | 2 | Omron G2R-1-DC12 | 39-G2R-1DC12-ND | 4,468 | 19.624 | page |
| 1 | 1 | Traco TMR 0511 | 1951-2740-ND | 674 | 28.006 | computed |
| 1 | 1 | Recom RFM-0505S | 945-3159-ND | 19,505 | 3.542 | computed |
| 3 | 3 | Infineon IRLZ44NPBF | IRLZ44NPBF-ND | 40,342 | 8.778 | page |
| 2 | 2 | Infineon IRF9540NPBF | IRF9540NPBF-ND | 7,268 | 8.932 | page |
| 1 | 1 | Microchip MCP2562-E/P | MCP2562-E/P-ND | 759 | 2.123 | page |
| 2 | 2 | Everlight 6N137, DIP-8 | 1080-1485-ND | 389 | 6.798 | computed |
| 1 | 1 | ST L7812CV | 497-1452-5-ND | 14,098 | 2.189 | page |
| 1 | 1 | Murata OKI-78SR-5/1.5-W36-C | 811-2196-5-ND | 46,903 | 9.746 | page |
| 1 | 1 | TI CD74HCT4538E | 296-2125-5-ND | 267 | 1.947 | page |
| 1 | 1 | TI SN74HCT125N | 296-8386-5-ND | 686 | 1.496 | page |
| 1 | 1 | TI SN74HC00N | 296-1563-5-ND | 292 | 1.265 | page |
| 1 | 1 | TI SN74HC08N | 296-1570-5-ND | 25,799 | 1.287 | page |
| 4 | 4 | Lite-On LTV-817M, DIP-4 | LTV-817M-ND | 2,413 | 2.684 | page |
| 3 | 3 | Diotec BC547B | 4878-BC547BCT-ND | 20,056 | 0.693 | page |
| 1 | 1 | Diotec BC557B | 4878-BC557BCT-ND | 5,889 | 0.242 | page |
| 10 | 6 | Diodes Inc 1N5819-T | 1N5819DICT-ND | 24,540 | 5.819 | computed |
| 2 | 2 | Vishay 1N4148-TAP | 1N4148-TAPCT-ND | 17,619 | 0.836 | page |
| 2 | 2 | ST P6KE18A | 497-11385-1-ND | 764 | 3.124 | page |
| 2 | 2 | Good-Ark 1N4742A, 12 V 1 W | 4786-1N4742ACT-ND | 5,233 | 0.770 | page |
| 1 | 1 | Littelfuse 0251.500NRT1L, coil | F5998CT-ND | 9,333 | 2.585 | page |
| 1 | 1 | Littelfuse 0251002.MXL, controller | F2314-ND | 19,677 | 2.013 | page |
| 2 | 2 | Kemet R82DC4100DQ60J, 1 µF 5% | 399-5447-1-ND | 185,714 | 2.134 | computed |
| 20 | 12 | Murata RDER71H104K0K1H03B, 100 nF 50 V | 490-8814-ND | 110,259 | 10.340 | computed |
| 6 | 5 | Würth 860010472002, 10 µF 25 V | 732-8625-1-ND | 8,317 | 0.990 | page |
| 1 | 1 | Würth 860040674004, 100 µF 50 V | 732-9187-1-ND | 33,044 | 0.572 | page |
| 2 | 2 | Sullins PPPC221LFBN-RC | S7055-ND | 1,583 | 4.576 | page |
| 5 | 5 | Phoenix 1984617 | 277-1721-ND | 42,142 | 4.730 | page |
| 1 | 1 | JST B4B-XH-A | 455-B4B-XH-A-ND | 58,887 | 0.275 | page |
| 2 | 2 | JST B5B-XH-A | 455-B5B-XH-A-ND | 72,246 | 0.660 | page |
| 1 | 1 | Sullins PRPC040SAAN-RC | S1011EC-40-ND | 65,124 | 2.002 | page |
| 10 | 2 | Sullins QPC02SXGN-RC | S9337-ND | 1,737,435 | 0.462 | computed |
| 1 | 1 | Lite-On LTL-307EE, red 5 mm | 160-1701-ND | 16,944 | 0.308 | page |
| 25 | 12 | Yageo MFR-25FBF52-100K | same series | see note | 1.397 | series |
| 25 | 11 | Yageo MFR-25FBF52-10K | same series | see note | 1.397 | series |
| 10 | 5 | Yageo MFR-25FBF52-4K7 | same series | see note | 0.671 | series |
| 10 | 4 | Yageo MFR-25FBF52-1K | same series | see note | 0.671 | series |
| 10 | 3 | Yageo MFR-25FBF52-470R | same series | see note | 0.671 | series |
| 10 | 2 | Yageo MFR-25FBF52-270R | same series | see note | 0.671 | series |
| 10 | 1 | Yageo MFR-25FBF52-220R | same series | see note | 0.671 | series |
| 10 | 2 | Yageo MFR-25FBF52-47K | same series | see note | 0.671 | series |
| 10 | 2 | Yageo MFR-25FBF52-680R | same series | see note | 0.671 | series |
| 10 | 1 | Yageo MFR-25FBF52-470K | same series | see note | 0.671 | series |

DigiKey goods **A$149.71**. Delivery A$0.

The Yageo lines use the quantity table that is the same on the two pages that were opened in full, MFR-25FBF52-47R (8,336 in stock) and MFR-25FBF52-402K (10,130 in stock): A$0.150 at one piece, A$0.061 at ten, A$0.0508 at 25, minimum 1. MFR-25FBF52-18K, 51K, 56K and 2M were also opened and sit on that same table, at A$0.150 or A$0.160 for one piece. The exact values in the table were not each opened, so their stock counts are not copied here. The dollars are the opened table. Nothing is being ordered on that basis.

## Notes on the parts

SN74HCT125N is the HCT125 in DIP-14, 4.5 V to 5.5 V. The CD74HCT125E page was not the one returned. SN74HC08N's page says it ships from Rochester. Both are DigiKey Australia lines, GST included, minimum 1.

LTV-817M is a 4-pin DIP phototransistor, PC817 pinout, CTR 50 percent minimum. The page gives the package as 0.400 inch. The fresh layout uses the Lite-On drawing.

Diotec BC547B and BC557B are TO-92, hFE group B. The square pad stays the collector. Confirm emitter-base-collector on the Diotec drawing before the layout.

1N5819-T covers the two coil flyback diodes, the DevKit series diode, and the three small Schottky positions that were BAT46. It is 40 V and 1 A. Those nodes are 5 V or 12 V.

P6KE18A on the ST page is 15.3 V standoff, 17.1 V breakdown minimum, 25.2 V clamp maximum. Stock is 764 and the page says it will not be restocked once that is gone. It is in stock now, not a backorder. The OKI input maximum is 36 V, so the clamp is inside it. The 100 µF input capacitor is 50 V for the same reason. The 10 µF parts are on the 5 V side and are 25 V.

The 1 µF film price and the 185,714 stock count were read from the substitute table on the R82DC4100AA60J page, which is out of stock until April 2027. The DQ60J row on that table is the part. GST on that row is computed.

The coil fuse is cut tape of the 251 series, the same body and the same electrical table as the bulk part. Cut tape has no reel fee on that page.

JST B4B-XH-A is the reed header. Two B5B-XH-A are the sense and NMEA headers. They mate with the XH plugs already used on the boat. New housings and crimps are not in this cart. Five Phoenix 1984617 blocks make the power pair and the two 4-position screw connectors. The ignition connector is still four positions, and the dry contacts stay independent.

The 40-pin header is cut down for the reed jumper and the publish jumper. Ten shunts, fit two.

## Not in the sum

One green 5 mm LED. The red is LTL-307EE. The green page that was requested came back as another red part, so no green price is included.

Routing waits on the electrical points above, which are closed as far as the datasheets go, and on measuring the DevKit that Phipps actually ships. The schematic on this branch is still the checkpoint. No new copper has been drawn.
