# Manufacturing and purchasing package

24 November 2026, Sydney time (AEDT, UTC+11). The board was not changed. Nothing was ordered. The firmware was not edited.

The priced lines add to **A$248.22 for one controller**. That figure is the five-board JLCPCB minimum delivered to Australia, every component line that returned a price, and the DigiKey delivery charge. Four small lines had no price and are named below. They are not in the A$248.22.

## What the A$248.22 is

| Piece | AUD | What it includes |
| --- | --- | --- |
| JLCPCB, five boards, delivered | 28.70 | USD 19.02 converted at the RBA rate. The quote does not show GST. |
| element14 Australia | 107.15 | GST included. Goods are over the published free-delivery line, so freight is A$0. |
| DigiKey Australia | 50.16 | GST included. |
| DigiKey delivery | 24.00 | The published charge, because the DigiKey goods are under A$60. |
| Phipps Electronics, the DevKit | 30.95 | The listed unit price. The page does not say whether GST is included, and it does not show postage. |
| LCSC catalog lines | 7.26 | USD prices converted at the same rate. No GST and no freight. |
| **Sum** | **248.22** | |

The Reserve Bank rate used is the 4:00 pm rate on 24 November 2026, 0.6627 US dollars per Australian dollar. One US dollar is A$1.50898.

If all five boards are built, the board share is A$5.74 and one controller is A$225.26 on the same parts. The minimum order is five, so the first controller pays the whole A$28.70 unless the other four are used.

Not in the sum:

- One 220 nF, 50 V, 5 mm disc for C_EDGE. No distributor page returned a price for a body that fits.
- Two KF350 3.50 mm 4-pin terminals, and the mating housings for the 2-pin and the two 4-pin terminals. The LCSC search returned the 2-pin and the 3-pin only.
- Two JST XHP-5 housings. The 4-pin housing is in the sum. The 5-pin housing was not in the first LCSC results.
- Postage on the DevKit.
- Australian GST on the imported boards. The JLCPCB quote does not show it, so it is not added here.
- Freight on a separate LCSC parcel. The A$7.26 is the catalog value only. Those lines are cheap enough to move onto the DigiKey or element14 cart; if that cart then reaches the free-delivery line, the A$24 DigiKey charge drops off. That was not assumed.

The full line list, with order codes, is `docs/home_assembly_bom.csv`. The Gerbers are `fab/home/windlass_home_gerbers.zip`. The placement drawing is `docs/images/windlass_home_placement.svg`.

## Bare boards

Both quotes were taken on 24 November 2026 for 120 mm by 112 mm, two layers, 1.6 mm, 1 oz, green mask, white silk, lead-free HASL, quantity 5. Neither quote shows Australian GST. The eight isolation slots are part of the outline. Neither calculator added a separate slot charge, and none is invented here. The quotes are before Gerber review.

JLCPCB, Australia selected:

| | USD |
| --- | --- |
| Five boards, 3-day build | 10.50 |
| Global Standard Direct Line, 10–14 days | 8.52 |
| **Delivered** | **19.02** |

A$28.70 at the rate above. UPS Worldwide Express Saver was USD 9.98, DHL USD 21.27, FedEx Express USD 28.21. The 24-hour line was not a bare-board option on this quote.

PCBWay, country Australia:

| | USD |
| --- | --- |
| Five boards, 24-hour build | 40.25 |
| Global Direct, 5–10 days | 6.65 |
| **Delivered** | **46.90** |

A$70.77. The 12-hour build was USD 125.66 for the boards before freight. A 100 mm square sanity check on the same calculator returned the published USD 5.00.

JLCPCB is the cheaper fab. The zip matches that quote.

## PCBWay will not sell this as an unassembled kit

PCBWay's own March 2026 answer is that parts are sourced for each SMT order and are not sold separately. Leftover parts can be stored or returned with assembled boards. A customer can buy the parts and ship them in. That is assembly kitting, not a bag of loose parts with bare boards.

The 29 March 2024 question "Can you quote pcb fab and kitting of parts only?" is on their site. The answer text was not in the page retrieved today.

JLCPCB's parts library is marked for PCBA only. It will not sell these parts loose either.

Buy the bare boards from JLCPCB and the parts from the distributors below.

## Where the parts are cheaper

Prices below are the 1-piece (or the stated minimum) retrieved on 24 November 2026. LCSC figures are US dollars from the JLCPCB parts library, which is the LCSC catalog. DigiKey and element14 figures are Australian dollars, GST included, from digikey.com.au and au.element14.com. A blank means that seller had no exact listing, or the page did not return a price.

| Part | Qty fitted | LCSC USD | DigiKey AUD inc | element14 AUD inc | Bought from |
| --- | --- | --- | --- | --- | --- |
| OKI-78SR-5/1.5-W36H-C | 1 | not the horizontal part | | 10.252 | element14 2812636 |
| MEJ2S0505SC | 1 | not listed | 16.929 | | DigiKey 811-2397-ND |
| MEJ2S0503SC | 1 | 13.8934 | | 18.887 | element14 2429477 |
| Finder 40.31.7.012.0000 | 2 | not listed | | 40.502 | element14 1169158 |
| IRLZ44NPBF | 3 | 0.8943 each | 8.778 | | DigiKey |
| IRF9540NPBF | 2 | 0.3461 each | 8.932 | | DigiKey |
| MCP2562-E/P | 1 | 2.3372 | 2.123 | | DigiKey |
| 6N137, DIP-8 | 2 | 0.7502 Broadcom | 6.798 Everlight | | DigiKey 1080-1485-ND |
| CD74HCT14E | 1 | 0.7993 | | 1.430 | element14 3120225 |
| CD74HCT125E | 1 | not listed | 1.749 | not listed | DigiKey |
| SN74HC00N | 1 | 0.6683 | | 1.287 | element14 3120419 |
| SN74HC08N | 1 | 0.6552 | page blocked | not listed | LCSC C2887, converted |
| PC817X1J000F | 4 | not this Sharp code | | 1.628 | element14 9707697 |
| DevKitC-1-N16R8 | 1 | not listed | not listed | not listed | Phipps, 30.95 listed |
| 0235.250HXP | 1 | 1.1989 | | 2.409 | element14 1192542 |
| 0217002.HXP | 1 | 0.3168 | | 0.9416 | element14 2762005 |
| Schurter 0031.8201 | 2 | not listed | | 3.608 | element14 1162740 |
| BC547B, onsemi, E-B-C | 4 | 0.1692 | | 1.866 | element14 1504818 |
| BC557BTA, onsemi, E-B-C | 1 | 0.0954 | | | LCSC C512874 |
| 1N5817, Vishay | 1 | 0.0719 | | 1.232 | element14 1836088 |
| 1N5819, ST, DO-41 | 2 | 0.0416 | | | LCSC C84618 |
| 1N4148-TAP | 2 | 0.0318 | | | LCSC C917479 |
| BAT46, ST, DO-35 | 3 | 0.0721 | | | LCSC C2969783 |
| P6KE18A, Yageo | 2 | 0.2187 Littelfuse | | 1.406 | element14 4078418 |
| BZX55C12-TAP | 2 fitted, 5 bought | 0.0757 | | 4.796 for five | element14 1779204 |
| PPPC221LFBN-RC | 2 | not listed | 4.576 | not the 22-pin | DigiKey S7055-ND |
| B4B-XH-A | 1 | 0.0523 | 0.275 | 100-piece minimum | DigiKey 455-B4B-XH-A-ND |
| B5B-XH-A(LF)(SN) | 2 | 0.0903 | | | LCSC C157991 |
| ECEA1EKS100I, 10 µF 25 V | 5 | | | 2.898 | element14 3346715 |
| R60DF4220506AK, 2.2 µF | 1 fitted, 10 bought | no fitting box | | 10.219 for ten | element14 4559288 |

LCSC is cheaper on the FETs, the logic, the diodes and the resistors. It does not stock the horizontal OKI, the MEJ2S0505SC, the Finder relay, the CD74HCT125E, or the Sharp PC817X1J000F. A parts-only LCSC order still needs a parcel to Australia. LCSC lists DHL, UPS, FedEx, Global Direct Standard Line and registered mail, and the price is calculated in the cart. The cart was blocked from this network, so no LCSC freight number is used.

DigiKey Australia, delivery page retrieved the same day: free delivery on orders of A$60 or more, and A$24 under that. Most parcels arrive in about four days from their US warehouse, plus customs. This DigiKey list is A$50.16, so the A$24 applies.

element14 Australia terms: a delivery fee of A$24 plus GST may be charged under A$60 ex GST, and delivery is free over A$60 ex GST for under 20 kg. The element14 goods here are about A$97 ex GST. Freight is A$0 on that rule. Several of those lines are UK stock, and element14 says an extra charge for extended-range stock is shown in the basket. The basket could not be opened, so that extra is not in the total.

The passives that element14 sells in tens are costed at the ten-piece price even where fewer are fitted. The 2.2 µF film is the same: the fitting part starts at ten, A$10.22 for the ten. The body is 13 mm by 5 mm on a 10 mm pitch, which fits the 13 mm by 6 mm footprint. The 1+ film in that search is 11.5 mm wide and does not fit.

## Assembly and polarity

The drawing `docs/images/windlass_home_placement.svg` is the component side, connectors along the bottom. Every reference is labelled. A red square is pad 1.

- Diode band, and the LED flat, go in the red square. That pad is the cathode. On D_DEV the cathode is the DevKit end and the anode is the +5 V end.
- Electrolytic stripe is the hole that is not red. The positive lead is the red square. The five 5 mm capacitors are 25 V parts, including the three positions marked 16 V.
- TO-220, marking toward you: gate, drain, source. The red square is the gate. The tab is the drain. Do not bolt the tabs together and do not bolt them to ground.
- The square pad of a TO-92 is the collector. The onsemi BC547B and BC557B bought here are E-B-C: with the flat toward you, the leads are emitter, base, collector, so the collector is the right-hand lead and that lead goes in the red square. A Nexperia BC547B,112 is C-B-E and would face the other way. Nexperia was not in the element14 or LCSC results. Do not use "flat toward you, C-B-E" unless the bag is a C-B-E part.
- DIP pin 1 is the red square, at the notch. Socket pin 1 is the end of each socket nearer the connector edge. The DevKit USB end is pin 1. Do not reverse the module.
- Fit the shunt on JP_REED pins 1-2. Leave JP1, the CAN publish jumper, open.
- The coil holder gets 0235.250HXP, 250 mA fast. The controller holder gets 0217002.HXP. Littelfuse lists the 217 series as fast-acting, IEC mark F, not time-lag.
- P6KE18A is a DO-15 body. The leads fit the 1.1 mm holes. 1N4148 and BAT46 are DO-35 bodies in the same style of hole. Form the leads. Do not redesign the footprint for that.
- The 1 W resistors are a 9 mm body. Form the leads to the 15.24 mm pitch.

Solder the sockets, the connectors and the short parts first. Fit the relays, the Murata modules and the TO-220 devices last. Power the OKI from the 12 V plug with the DevKit out, and check 5.0 V, before the module is inserted. Program from the DevKit USB socket with the 12 V plug out.

## Watchdog, including leakage

The circuit is unchanged. CD74HCT14E on the 5 V rail. GPIO1 is pulled down by 100 kΩ and inverted. A 330 Ω resistor and a 220 nF capacitor into a 10 kΩ pull-up make a short low pulse on the rising edge of the heartbeat only. That pulse turns on the BC547B and dumps the 2.2 µF film. The film then charges through 470 kΩ. The series IRLZ44N stays on until the film crosses the Schmitt threshold. A stuck GPIO produces one edge and then the rail turns off. It does not latch off.

TI CD74HCT14, positive-going threshold: at 4.5 V, 1.2 V to 1.9 V; at 5.5 V, 1.4 V to 2.1 V, across the full temperature range. Input leakage is ±0.1 µA at 25 °C and ±1 µA from −40 °C to 125 °C. The absolute maximum clamp current is ±20 mA. The 330 Ω resistor holds the edge-clamp current to about (5.5 − 0.7) / 330 = 15 mA, inside that rating. The discharge pulse, from a kick near 0.3 V back up to the threshold, is 0.5 ms to 1.1 ms. The BC547B discharges 2.2 µF in a small part of that.

Dropout is the charge of 2.2 µF through 470 kΩ from a saturated collector. With a 1 percent resistor, a 10 percent film capacitor, the threshold span above, and ±1 µA of input current:

| Case | Dropout | Missed 80 ms edges |
| --- | --- | --- |
| Short corner: low R and C, 5.5 V, threshold 1.4 V, 1 µA sourcing | 239 ms | 3.0 |
| 5.0 V, threshold 1.65 V, no leakage | 393 ms | 4.9 |
| Same, 1 µA sinking | 445 ms | 5.6 |
| Long corner: high R and C, 4.5 V, threshold 1.9 V, 1 µA sinking | 660 ms | 8.3 |

One microamp in 470 kΩ is 0.47 V. At 5.0 V the capacitor still aims at 4.53 V, and at 4.5 V it aims at 4.03 V. Both are above the highest threshold in the table, so the leakage lengthens the timeout and does not stop the trip. Five microamps, well beyond the HCT specification, still trips, at about 1.4 s. The trip fails only around 8 µA, where the aim falls below the threshold.

Film leakage is not that current. A polyester box at 5 V leaks nanoamps. The KEMET part bought for C_TIME is metallised PET. That term does not move the window next to the 1 µA input specification. The BC547 collector cutoff is tens of nanoamps at room temperature beside the same 1 µA. Time the first board. The window above is the calculation, not a measurement.

## Fuse clearing and the IRLZ44N

The coil fuse is the Littelfuse 235 series, 0235.250HXP. Cold resistance 2.25 Ω. Nominal melting I²t 0.0166 A²s. The interrupt rating is 35 A at 250 VAC. There is no published DC rating.

A dead short of a coil output is the fuse, the IRF9540N (0.117 Ω maximum), and the two IRLZ44Ns. At the 4 V RDS maximum of 35 mΩ each, the stack is 2.44 Ω before wiring, and 12 V gives about 4.9 A. Melt time at that current is 0.0166 / 4.9² = 0.69 ms. Wiring only makes it slower.

While the FET is ohmic, the energy to reach the melting I²t is RDS × I²t. At 35 mΩ that is 0.58 mJ in each IRLZ44N. At 25 mΩ, the 5 V figure, it is 0.42 mJ. The Infineon single-pulse avalanche energy is 210 mJ. The pulse is under a millisecond, so the die rise is a fraction of a degree: 5 A in 35 mΩ is under a watt. Opening on 12 V DC can add an arc after the melt. The datasheet does not give that time. Ten times the melt energy is still about 6 mJ, a few percent of the avalanche rating. The fuse is inside the safe operating region of the IRLZ44N. This is not a board defect. Confirm the opening on the first board.

The controller fuse is a different part. Littelfuse lists 0217002.HXP as the 217 series, fast-acting, IEC mark F2AL, cold resistance 0.042 Ω, melting I²t 5.726 A²s. Earlier notes called this series time-lag. That was wrong, and the copper does not depend on it. This fuse is there for the converter branch. It is not the coil protection. Its let-through is large next to the coil fuse. Confirm on the first board that the OKI starts without opening it. A time-lag 5×20 cartridge would fit the same holder without a board change, if that test says the fast part is too quick.

Normal coil current is about 42 mA. Both coils at 18 V are about 125 mA, under the 250 mA fuse.
