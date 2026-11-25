# Manufacturing and purchasing package

24 November 2026, Sydney time (AEDT, UTC+11). The copper on this board is the checkpoint. A single-distributor cart inside A$150 to A$180 was not closed, and the watchdog was not replaced on the copper. Nothing was ordered. The firmware was not edited.

## What was asked, and what is not being ordered

The ask was two orders only: JLCPCB for the bare boards, and one of DigiKey, Mouser or element14 for every component, all of it in stock, delivered to Australia, inside A$150 to A$180 with the boards. That cart does not exist without giving up a limit the design already requires.

DigiKey Australia does not list the ESP32-S3-DevKitC-1-N16R8. The DevKitC-1U-N8R8 listing is the wrong antenna and 8 MB of flash, and it was not in stock. Mouser Australia lists ESP32-S3-DevKitC-1-N32R16V at A$25.34. That is 32 MB of flash, not the 16 MB part this image is built for, and the page did not return a stock count. element14 was not shown to sell the board. None of the three can be the single supplier today.

Omron G2R-1-DC12 does have a published inductive rating, 5 A at 30 VDC with L/R = 7 ms, which would cover the boat's 2.5 A control fuse. Its maximum coil voltage is 110 percent, 13.2 V. These coils have to operate at up to 18 V. It is not a substitute. No cheaper relay was found with both a maximum coil voltage of at least 18 V and a published DC inductive rating. The two Finder 40.31.7.012.0000 stay, A$40.50 including GST.

Recom RFM-0505S is in stock at DigiKey, 19,505 pieces, A$3.542 including GST. It is 1 W, 200 mA, 1 kV, and the datasheet calls the insulation functional. Load regulation is ±15 percent from 10 percent to 100 percent load, so a 5 V output can be 5.75 V. The MCP2562 recommended maximum is 5.5 V. It is not fitted. The 3.3 V mate was not confirmed as its own in-stock line. The two Murata modules stay.

Those four parts are why the total is not inside A$150 to A$180. Cutting them to hit the number would drop either the 18 V coil limit or the transceiver's recommended supply.

The coil fuse stays the SIBA 70-007-33/0.4A. It is the 5×20 part with a published 1500 A interrupt at 250 VDC. element14 has one piece, in the UK, so it does not meet a rule of sufficient stock and no backorder. DigiKey's in-stock 5×20 parts at this current publish an AC interrupt only. IEC 60127's operating time is the pre-arcing time plus the arcing time. SIBA publishes the pre-arcing integral, 0.07 A²s, and does not publish a maximum operating time. A multiple of the pre-arcing integral is not that time, and avalanche energy is not the limit while the gate is held on. The forward safe operating area cannot be closed until a datasheet gives the operating time. The earlier twice-pre-arcing argument is withdrawn.

The HCT14 timer still fails the original limit. The long corner is 705 ms and the limit is 475 ms. A 74HCT123 cannot hold the 80 ms heartbeat, because its retrigger gap is about 0.42 of the pulse. The part that does both is the TI CD74HCT4538E, DIP-16, DigiKey 296-2125-5-ND, 267 in stock, A$1.947 including GST. The pulse is 0.7 × RX × CX. At 470 kΩ, 1 percent, and 1 µF, 5 percent, the nominal pulse is 329 ms. TI's −55 °C to 125 °C window at the 10 kΩ / 0.1 µF test point is 0.850 to 1.150 of that formula. Applied here, the short corner is 263 ms and the long corner is 401 ms. That covers two 100 ms intervals and stays under 475 ms. Retrigger is microseconds to a few tens of microseconds, not a blanked fraction of the pulse. Power-up reset holds Q low. It is not on the board. A fresh route of the whole board leaves power nets open. Patching the DIP-16 onto this copper shorted a timing pin to +5 V and left clearance and unconnected errors. The checkpoint DRC is two track-width notes and no unconnected pads. The copper was put back.

The priced list below is that checkpoint. It is A$220.63, it is more than one electronics distributor, and it is the list that matches the board.

24 November 2026, Sydney time (AEDT, UTC+11). The copper, the outline and the footprints are unchanged. The coil-fuse value on the schematic is SIBA 70-007-33/0.4A. Nothing was ordered. The firmware was not edited.

The priced lines add to **A$220.63 for one controller**. That figure pays for the five-board JLCPCB minimum, delivered, and for every component, including the lines that had no price last time. DigiKey delivery is A$0. Two sellers do not publish postage, and those two amounts are not in the A$220.63.

## What the A$220.63 is

| Piece | AUD | What it includes |
| --- | --- | --- |
| JLCPCB, five boards, delivered | 28.70 | USD 19.02 converted at the RBA rate. The quote does not show GST. |
| element14 Australia | 105.60 | GST included. Goods stay over the free-delivery line, so freight is A$0. |
| DigiKey Australia | 60.65 | GST included. At A$60 or more, delivery is A$0. |
| Zaitronics, the DevKit | 18.50 | GST included. Postage is calculated at checkout and is not in this sum. |
| Pedal Parts, the 220 nF disc | 0.10 | The part only. Postage is not on the page and is not in this sum. |
| LCSC catalog lines | 7.08 | USD prices converted at the same rate. No GST. Do not open a separate LCSC parcel for these. |
| **Sum** | **220.63** | |

The Reserve Bank rate used is the 4:00 pm rate on 24 November 2026, 0.6627 US dollars per Australian dollar. One US dollar is A$1.50898.

If all five boards are built, the board share is A$5.74 and one controller is A$197.67 on the same parts. The minimum order is five, so the first controller pays the whole A$28.70 unless the other four are used.

Not in the sum:

- Postage on the Zaitronics DevKit. The shipping page says the charge is calculated at checkout. No dollar figure is published, so none is added.
- Postage on the Pedal Parts 220 nF disc. The product page does not show it.
- Australian GST on the imported boards. The JLCPCB quote does not show it.
- An element14 extended-range surcharge. The basket could not be opened. The SIBA fuse is the one UK-stock line, one piece, 3 to 5 business days. If that piece has sold, the manufacturer lead time on the page is 33 weeks.
- Freight for a separate LCSC parcel. The A$7.08 is the catalog value of the lines that still have no Australian 1-piece price. Add them to the element14 or DigiKey cart when those order codes are in stock. Do not open a fourth parcel for A$7.08 of passives.

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
| IRF9540NPBF | 2 fitted, 3 bought | 0.3461 each | 13.398 | | DigiKey. The third piece clears free delivery |
| MCP2562-E/P | 1 | 2.3372 | 2.123 | | DigiKey |
| 6N137, DIP-8 | 2 | 0.7502 Broadcom | 6.798 Everlight | | DigiKey 1080-1485-ND |
| CD74HCT14E | 1 | 0.7993 | | 1.430 | element14 3120225 |
| CD74HCT125E | 1 | not listed | 1.749 | not listed | DigiKey |
| SN74HC00N | 1 | 0.6683 | | 1.287 | element14 3120419 |
| SN74HC08N | 1 | 0.6552 | page blocked | not listed | LCSC C2887, converted |
| PC817X1J000F | 4 | not this Sharp code | | 1.628 | element14 9707697 |
| DevKitC-1-N16R8 | 1 | not listed | not the DevKit | not listed | Zaitronics, 18.50 inc GST |
| 70-007-33/0.4A | 1 | not the 250 mA part | | 0.856 | element14 2523853 |
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

DigiKey Australia, delivery page retrieved the same day: free delivery on orders of A$60 or more, and A$24 under that. Most parcels arrive in about four days from their US warehouse, plus customs. The required DigiKey lines, including the six Phoenix blocks and the two housings, come to A$55.24. That is still under A$60, so the A$24 charge would still apply. Buying one extra IRF9540NPBF (A$4.47, the same part already fitted twice) and one extra Phoenix 1984617 (A$0.95, the same 2-position block) takes the cart to A$60.65. Delivery is then A$0. Those two spares cost A$5.41 and remove A$24.

element14 Australia terms: a delivery fee of A$24 plus GST may be charged under A$60 ex GST, and delivery is free over A$60 ex GST for under 20 kg. The element14 goods here are A$105.60 including GST, about A$96 ex GST. Freight is A$0 on that rule. The SIBA fuse is UK stock. element14 says an extra charge for extended-range stock is shown in the basket. The basket could not be opened, so that extra is not in the total.

The passives that element14 sells in tens are costed at the ten-piece price even where fewer are fitted. The 2.2 µF film is the same: the fitting part starts at ten, A$10.22 for the ten. The body is 13 mm by 5 mm on a 10 mm pitch, which fits the 13 mm by 6 mm footprint. The 1+ film in that search is 11.5 mm wide and does not fit.

## Assembly and polarity

The drawing `docs/images/windlass_home_placement.svg` is the component side, connectors along the bottom. Every reference is labelled. A red square is pad 1.

- Diode band, and the LED flat, go in the red square. That pad is the cathode. On D_DEV the cathode is the DevKit end and the anode is the +5 V end.
- Electrolytic stripe is the hole that is not red. The positive lead is the red square. The five 5 mm capacitors are 25 V parts, including the three positions marked 16 V.
- TO-220, marking toward you: gate, drain, source. The red square is the gate. The tab is the drain. Do not bolt the tabs together and do not bolt them to ground.
- The square pad of a TO-92 is the collector. The onsemi BC547B and BC557B bought here are E-B-C: with the flat toward you, the leads are emitter, base, collector, so the collector is the right-hand lead and that lead goes in the red square. A Nexperia BC547B,112 is C-B-E and would face the other way. Nexperia was not in the element14 or LCSC results. Do not use "flat toward you, C-B-E" unless the bag is a C-B-E part.
- DIP pin 1 is the red square, at the notch. Socket pin 1 is the end of each socket nearer the connector edge. The DevKit USB end is pin 1. Do not reverse the module.
- Fit the shunt on JP_REED pins 1-2. Leave JP1, the CAN publish jumper, open.
- The coil holder gets SIBA 70-007-33/0.4A, 400 mA fast, 5×20. The controller holder gets 0217002.HXP. Littelfuse lists the 217 series as fast-acting, IEC mark F, not time-lag.
- J_PWR is one Phoenix 1984617. J_PERM and J_CONTACT are two of the same block snapped together on each footprint. The screw takes the wire. There is no plug housing to buy.
- P6KE18A is a DO-15 body. The leads fit the 1.1 mm holes. 1N4148 and BAT46 are DO-35 bodies in the same style of hole. Form the leads. Do not redesign the footprint for that.
- The 1 W resistors are a 9 mm body. Form the leads to the 15.24 mm pitch.

Solder the sockets, the connectors and the short parts first. Fit the relays, the Murata modules and the TO-220 devices last. Power the OKI from the 12 V plug with the DevKit out, and check 5.0 V, before the module is inserted. Program from the DevKit USB socket with the 12 V plug out.

## Watchdog against the original limit

The circuit is unchanged. R_TIME stays 470 kΩ and C_TIME stays the 2.2 µF film. CD74HCT14E is on the OKI 5 V rail. GPIO1 is pulled down by 100 kΩ and inverted. A 330 Ω resistor and the 220 nF capacitor into a 10 kΩ pull-up make a short low pulse on the rising edge of the heartbeat only. That pulse turns on the BC547B and dumps the film. The film then charges through 470 kΩ. The series IRLZ44N stays on until the film crosses the Schmitt threshold. A stuck GPIO produces one edge and then the rail turns off. It does not latch off.

The original limit is in `docs/design_review.md`. The long case is the one that matters, and it was required to stay under half a second. The firmware contract records that long case as 475 ms (`kMonostableLongMs`) and the short case as 264 ms (`kMonostableShortMs`). The heartbeat is an edge every 80 ms, and the contract also requires an edge at least every 100 ms so the short case covers two intervals. Those constants were not edited.

TI CD74HCT14, positive-going threshold, at 25 °C and from −55 °C to 125 °C: at 4.5 V, 1.2 V to 1.9 V; at 5.5 V, 1.4 V to 2.1 V. There is no guaranteed 5.0 V column. Input leakage is ±0.1 µA at 25 °C and ±1 µA from −40 °C to 125 °C. The charge equation is t = −RC ln((Vinf − Vth) / (Vinf − V0)), with Vinf = Vcc − Ileak·R and V0 = 0.1 V after the dump. A positive leak is the input sinking, which lengthens the timeout. This equation reproduces the 393 ms nominal line and the 445 ms line at 5.0 V with 1 µA sinking.

With a 1 percent resistor and a 10 percent film capacitor:

| Case | Dropout | Against the requirement |
| --- | --- | --- |
| Short: R and C low, 5.5 V, threshold 1.4 V, 1 µA sourcing | 231 ms | Covers two 100 ms intervals. The earlier 239 ms used a different starting voltage. |
| 5.0 V, threshold 1.65 V, no leakage | 393 ms | The nominal line. |
| Same, 1 µA sinking | 445 ms | Leakage lengthens it. |
| Long: R and C high, 4.5 V, threshold 1.9 V, 1 µA sinking | 705 ms | Over 475 ms, and over half a second. |

The earlier 660 ms figure does not come out of this equation. At a 0.2 V start and with the resistor at its low tolerance it is 660 ms, which is not the long corner. Both 660 ms and 705 ms fail the original long limit. The short corner does not. The deficiency is the long side only.

The OKI-78SR output is 4.8 V to 5.2 V nominal, with setting accuracy ±4 percent at half load and a total regulation band of ±3 percent. Stacked, that is about 4.66 V to 5.36 V. Using 4.66 V in place of 4.5 V, with the same 1.9 V threshold, the long corner is 668 ms. The regulator does not bring it under 475 ms.

No resistor that fits the existing film footprint meets both limits at once. The HCT14 threshold window sets the ratio. At the same ±1 percent and ±10 percent:

| R_TIME | Short corner | Long corner |
| --- | --- | --- |
| 324 kΩ | 164 ms | 462 ms |
| 330 kΩ | 167 ms | 472 ms |
| 332 kΩ | 168 ms | 475 ms |
| 470 kΩ, as built | 231 ms | 705 ms |

A 330 kΩ change would put the long corner under 475 ms and would leave 7 ms over two 80 ms firmware edges. The firmware edges when the elapsed time reaches 80 ms, so loop stretch eats that 7 ms and the rail can drop on a healthy heartbeat. That is a new deficiency. A value that keeps the short corner above 200 ms, two 100 ms intervals, pushes the long corner to about 589 ms. Even a ±1 percent capacitor cannot hold both bounds. R_TIME stays 470 kΩ. A different timer would be a new through-hole IC and a layout change, and that change is not being made. Time the first board. The window above is the calculation, not a measurement.

One microamp in 470 kΩ is 0.47 V. At 4.5 V the capacitor still aims at 4.03 V, above 1.9 V, so the specified leakage lengthens the timeout and does not stop the trip. Film leakage is nanoamps. The KEMET part is metallised PET. That term does not move the window next to the 1 µA input specification.

## Fuse clearing and the MOSFET safe operating area

The coil holder is still the Schurter 0031.8201, a 5×20 mm cartridge. The Littelfuse 0235.250HXP is not the part to buy. Its interrupt rating is 35 A at 250 VAC and 10 kA at 125 VAC, and the datasheet gives no DC interrupting current. The same is true of the Littelfuse 235, 216 and 215 series, the Eaton S500, S501 and S506, the Schurter FSF and FST, and the Bel 5SF: the published interrupting current is AC only. Eaton's C308F 250 mA part is rated 4000 A at 250 VDC, and it is a 3×8.4 mm body that does not fit this holder. Bel 0ADBC0250-BE is rated for 1000 VDC, and it is 6.3×32 mm.

No 250 mA, 5×20 cartridge found for this buy has an explicit DC interrupting current. SIBA 179021 is a fast ceramic 5×20 series. The datasheet gives 1500 A at 250 VDC for the members from 400 mA to 4 A. The 250 mA member, 179021.0,25, is outside that range and is rated 1500 A at 250 VAC only. The lowest current with the DC rating is 70-007-33/0.4A, which is 179021.0,4, 400 mA. Pre-arcing I²t is 0.07 A²s. The voltage drop is 650 mV at 0.4 A, so the hot resistance is about 1.6 Ω. It fits the existing holder. The schematic value is that part. The pads did not move.

Both coils at 18 V are about 125 mA, which is 31 percent of 400 mA. A fault that sits between 250 mA and 400 mA will not open this fuse. That is the cost of having a DC interrupt rating in this body. A 500 mA time-lag part in the 477 series has a DC rating and a much larger I²t, and it was not selected.

A dead short of a coil output is the fuse, the IRF9540N (0.117 Ω maximum) and the two IRLZ44Ns (35 mΩ at Vgs = 4 V). SIBA publishes the pre-arcing integral and does not publish total clearing I²t. The bound used here is twice the pre-arcing integral, 0.14 A²s. The body is sand-filled ceramic and the coil rail is 12 V to 18 V against a 250 VDC interrupting rating, so the arc is a small fraction of the rating. The factor of two is a bound, not a number from the datasheet.

Energy in the FET while it is ohmic is RDS × I²t. At 35 mΩ and 0.14 A²s that is 4.9 mJ in each IRLZ44N. At 25 mΩ, the 5 V figure, it is 3.5 mJ. The Infineon single-pulse avalanche energy is 210 mJ. The IRF9540N takes 0.117 × 0.14 = 16 mJ. At the hot fuse resistance the stack is about 1.8 Ω, so 12 V gives about 6.6 A and 18 V gives about 9.9 A. Pre-arcing is then about 1.6 ms at 12 V and 0.7 ms at 18 V, and the clearing bound is about 3.2 ms and 1.4 ms. Vds during that pulse is I × RDS, about 0.23 V at 12 V and 0.35 V at 18 V. That is the RDS(on) region of the safe operating area, not a linear-region pulse at the rail voltage. The HCT125 high output that drives these gates is about 4.4 V minimum, and the IRLZ44N RDS is specified at 4 V and at 5 V.

The 0235.250HXP melting integral is smaller, and it is not usable here because the part has no DC interrupting current. Confirm the opening on the first board.

The controller fuse is a different part. Littelfuse lists 0217002.HXP as the 217 series, fast-acting, IEC mark F2AL, cold resistance 0.042 Ω, melting I²t 5.726 A²s. It protects the converter branch. It is not the coil protection. Confirm on the first board that the OKI starts without opening it.

## DevKit prices

The module is the ESP32-S3-DevKitC-1-N16R8 with the PCB antenna. The DevKitC-1U and the bare WROOM module do not fit the sockets. Prices retrieved the same day:

| Seller | Price | What the page says |
| --- | --- | --- |
| Zaitronics, Melbourne | A$18.50 inc GST | Names DevKitC-1-N16R8. Also marked unavailable, 5 to 10 days before dispatch. Postage is calculated at checkout. This is the price in the total. |
| Maker Store, Carrum Downs | A$23.95 inc GST | Coming soon. |
| DigiKey Australia | A$24.37 inc GST | That listing is DevKitC-1U-N8R8. Wrong antenna, 8 MB flash. Not bought. DigiKey does not list the PCB-antenna N16R8 DevKit. |
| Tempero Systems | A$29.95 | Out of stock. |
| Phipps Electronics | A$30.95 listed | GST and postage not shown. Use this if Zaitronics will not dispatch. The total then rises by A$12.45, plus whatever postage Phipps adds. |
| Lazy Automation | A$10.00 | Nine listed, headers unsoldered, and the text says onboard and external antenna support. It does not confirm the Espressif PCB-antenna board. Not used. |

## Shopping lists

Nothing below has been ordered.

element14 Australia, order 2523853 and the codes in `docs/home_assembly_bom.csv`. Goods A$105.60 inc GST. Freight A$0. The coil fuse on that cart is one SIBA 70-007-33/0.4A. The old 0235.250HXP, order 1192542, comes off the cart.

DigiKey Australia. Goods A$60.65 inc GST. Freight A$0.

| Order code | Part | Buy |
| --- | --- | --- |
| 811-2397-ND | MEJ2S0505SC | 1 |
| IRLZ44NPBF-ND | IRLZ44N | 3 |
| IRF9540NPBF-ND | IRF9540N | 3, fit 2 |
| MCP2562-E/P-ND | MCP2562-E/P | 1 |
| 1080-1485-ND | Everlight 6N137, DIP-8 | 2 |
| CD74HCT125E | CD74HCT125E | 1 |
| S7055-ND | PPPC221LFBN-RC | 2 |
| 455-B4B-XH-A-ND | B4B-XH-A | 1 |
| 277-1721-ND | Phoenix 1984617, 3.50 mm | 6, fit 5 |
| 2057-25CH-B-05-ND | 25CH-B-05, 5-pin housing | 2 |

JLCPCB, the zip `fab/home/windlass_home_gerbers.zip`. Five boards, the quote above, A$28.70 delivered. No GST in the quote.

Zaitronics, one ESP32-S3-DevKitC-1-N16R8, A$18.50 inc GST. Confirm it will dispatch, and confirm the PCB antenna and the N16R8 mark. Postage is extra and unpublished.

Pedal Parts Australia, CAPN0178, one 220 nF 50 V disc, 5 mm pitch, A$0.10. Postage is extra and unpublished.

The remaining LCSC catalog lines in the CSV sum to A$7.08 converted. They are the 100 nF discs, the small resistors, the signal diodes, the BC557B, the two B5B-XH-A headers, the XHP-4 housing, the crimp contacts, the shunts, the two LEDs and the 10 µF 50 V input capacitor. Add them to the element14 or DigiKey cart. Do not pay a separate LCSC freight charge for that list.
