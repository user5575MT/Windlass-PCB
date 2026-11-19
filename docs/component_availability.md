# Component availability

## Revision 0.7 checks, 19 November 2026

No order was placed. Quantities below are the figures already read on this date. They were not reloaded for this revision.

| Reference | Part | Land | Stock already read |
| --- | --- | --- | --- |
| D_R | Lite-On LTST-C190KRKT, red, 0603, JLCPCB C94869. Datasheet Vf 1.6 to 2.4 V at 20 mA. Driven from GPIO15 through 680 Ω. Amber is this lamp and D_G together | `LED_0603_1608Metric` | The JLCPCB page listed the part and did not show a quantity |
| D_G | Lite-On LTST-C190KGKT, yellow-green, 567.5 to 576.5 nm, 0603, JLCPCB C125094. Datasheet Vf 1.9 to 2.4 V at 20 mA. This is the ready lamp. A 525 nm green was not selected | `LED_0603_1608Metric` | The JLCPCB page listed the part and did not show a quantity |
| D_B | Lite-On LTST-C190TBKT, blue, 465 to 475 nm, 0603, JLCPCB C125096. Datasheet Vf 2.8 to 3.8 V at 20 mA, so it is not on a 3.3 V GPIO. Anode is +5V through R_B, 1 kΩ. Cathode is the drain of Q_LED | `LED_0603_1608Metric` | The LCSC page showed 23960 |
| Q_LED | Nexperia 2N7002BK,215, the same SOT-23 reel as the clamp FETs. Pin 1 gate, pin 2 source, pin 3 drain. Gate is GPIO17 with R_BPD 100 kΩ to GND. Source is GND. There is no DC path from the drain or from +5V to the gate | `SOT-23` | JLCPCB C282405 showed 137246, extended, economic and standard |
| R_R, R_G | 680 Ω, 0402. About 1.9 mA at Vf 2.0 V and about 1.3 mA at Vf 2.4 V, from 3.3 V | `R_0402_1005Metric` | Commodity |
| R_B | 1 kΩ, 0402, from +5V. About 1.7 mA at Vf 3.3 V and about 1.2 mA at Vf 3.8 V | `R_0402_1005Metric` | Commodity |
| R_RPD, R_GPD, R_BPD | 100 kΩ pulldowns. The prototype firmware does not drive GPIO15, GPIO16 or GPIO17, so the lamps stay off | `R_0402_1005Metric` | Commodity |
| U_ESD | ST USBLC6-2SC6, SOT-23-6, JLCPCB C7519. Pins 1 and 6 are one data line, pins 3 and 4 the other, pin 2 GND, pin 5 USB_VBUS. Placed on the connector side of the 22 Ω resistors. USBLC6-2P6 is SOT-666 and is not this land | `SOT-23-6` | JLCPCB showed 40209, extended, economic and standard |

Factory-assembled SMD is the intent for these LEDs, the blue FET, the pulldowns and the ESD device. The hand-fitted list from revision 0.6 is unchanged: both Finder relays, both MEJ2 modules, and the loose reed shunt.

## Revision 0.6 checks, 19 November 2026

Pages read on this date that did not print a quantity are marked that way. No order was placed. A package name on a distributor page is not treated as the land.

| Reference | Part | Land now on the board | Stock shown this pass |
| --- | --- | --- | --- |
| U8 | Nexperia 74LVC1G86GW,125, LCSC C12513. Nexperia GW is SOT353-1, 0.65 mm pitch, pin 1 B, pin 2 A, pin 3 GND, pin 4 Y, pin 5 VCC. LCSC labels the same reel TSSOP-5 | `SOT-353_SC-70-5` | The LCSC page did not show a quantity. An earlier JLCPCB reading the same day was C12513, 3313, and was not reloaded |
| U12 | Nexperia 74LVC1G08GW,125, LCSC C12512. Same SOT353 pin numbers. AND and XOR are commutative, so the A/B names do not change the circuit | `SOT-353_SC-70-5` | Not reloaded. The earlier LCSC image page showed 30190 and a brand listing showed 27030. JLCPCB C12512 did not show a quantity |
| U11 | Nexperia 74LVC1G123DP,125, SOT505-2, TSSOP-8, 3.0 mm body, 0.65 mm. The DC reel is 0.5 mm VSSOP and is not this land | `TSSOP-8_3x3mm_P0.65mm` | Not reloaded. Earlier LCSC image page showed 427. JLCPCB showed no quantity. DigiKey showed 17524 |
| D_R | Lite-On LTST-C190KRKT, red, 0603. The JLCPCB page lists Vf 2 V at 20 mA | `LED_0603_1608Metric` | Quantity not shown |
| D_G | Lite-On LTST-C190KGKT, yellow-green, 567 to 576 nm, 0603. Same Vf listing, 2 V at 20 mA. This is not a 525 nm green | `LED_0603_1608Metric` | Quantity not shown |
| D_B | Historical. Revision 0.7 selects LTST-C190TBKT and drives it from +5V through Q_LED. This row was the open 3.3 V anode | `LED_0603_1608Metric` | See revision 0.7 |
| SW_RST, SW_BOOT | E-Switch TL3342F160QG, LCSC C2886898. The page says SMD 5.2 × 5.2 mm, 4 gull-wing pads, SPST, 160 gf, 50 mA, 12 V. The KiCad land `SW_SPST_TL3342` cites the TL3342 drawing and has the same four pads | `SW_SPST_TL3342` | The LCSC page did not show a quantity |
| JP_REED | Standard 2.54 mm 1×03 header. `SH_REED` is one loose shunt, not soldered | `PinHeader_1x03_P2.54mm_Vertical`. The shunt has no board footprint | Commodity header and shunt. No single-vendor count |
| F_COIL | Littelfuse 0466001.NR, LCSC C151134. The page confirms 1206, 1 A, 63 V, 50 A interrupt. The halogen-free 0466001.NRHF is not substituted | `Fuse_1206_3216Metric` | The LCSC page did not show a quantity |
| D_TVS_MCU, D_TVS_COIL | Littelfuse SMAJ18A, JLCPCB C148219. 18 V stand-off, 29.2 V clamp, 400 W at 10/1000 µs. A TECH PUBLIC reel is not the part | `D_SMA` | Not reloaded. The earlier JLCPCB page did not show a quantity |
| J_USB | Korean Hroparts TYPE-C-31-M-12, LCSC C165948, 16-pin USB 2.0 | `USB_C_Receptacle_HRO_TYPE-C-31-M-12` | Not reloaded. The earlier LCSC page showed 490560 |

Hand-fitted, not a JLCPCB assembly line for these reels: both Finder 40.31.7.012.0000 relays, Murata MEJ2S0505SC, Murata MEJ2S0503SC if the three LCSC pieces noted in revision 0.5 are gone, and the loose reed shunt.

The SOT-23-5 land is no longer used for U8 or U12. `R_R`, `R_G` and `R_B` are on the board.

## Revision 0.5 checks, 19 November 2026

The U8, U12, LED, SW_REED and MEJ2 rows below are the state before revision 0.6. The section above replaces them.

Pages below were read on this date. A page that did not show a quantity is marked that way. No order was placed. Prices on those pages are not a quotation, and there is still no fabrication total.

The placed land and the orderable package have to be the same part. Two logic lands are not.

| Reference | What was read | Stock shown | Land on the board |
| --- | --- | --- | --- |
| U20 | Diodes AP63203WU-7, JLCPCB C780769, TSOT-23-6, 3.3 V fixed, 2 A | JLCPCB search showed 5163, extended. The LCSC image page for the same number showed 0 | TSOT-23-6. Matches |
| U8, U12 | Nexperia 74LVC1G08GW,125 is LCSC C12512, SOT-353. The earlier JLCPCB number C284803 was the wrong page. JLCPCB C12512 did not show a quantity. MDD 74LVC1G08GW, C52140431, showed 5044 and is not this part | LCSC image page showed 30190. A brand listing the same day showed 27030 | Placed land is KiCad SOT-23-5. Its pads are on a 0.95 mm pitch. SOT-353 is 0.65 mm. Do not assemble the GW reel onto this land |
| U11 | The placed footprint is TSSOP-8, 3.0 mm body, 0.65 mm pitch. That is Nexperia 74LVC1G123DP,125, LCSC C513291. 74LVC1G123DC,125 is VSSOP-8 at 0.5 mm (JLCPCB C77273 showed 5075) and does not fit | LCSC image page for the DP part showed 427. The JLCPCB page did not show a quantity. DigiKey showed 17524 | TSSOP-8 matches the DP part only |
| Q_UP, Q_DN, Q_SERIES | Nexperia NX6008NBK is SOT-23, pin 1 gate, pin 2 source, pin 3 drain. The orderable reel found is NX6008NBKR, LCSC C3280960. NX6008NBKWX is SOT-323 and is the wrong package. No JLCPCB C-number for the Nexperia SOT-23 part came back | LCSC image page showed 2680 | SOT-23. Matches NX6008NBKR, not the SOT-323 reel |
| Q90 and the clamps | Nexperia 2N7002BK,215, JLCPCB C282405, SOT-23 | JLCPCB showed 137246, extended, economic and standard | SOT-23 |
| Q91 | Diodes DMP3099L-7, LCSC C155244, SOT-23, 30 V, 3.8 A. The ElecSuper and VBsemi listings are not this part | LCSC showed 90380. The JLCPCB page did not show a quantity | SOT-23 |
| F_MCU | Littelfuse 0466002.NR is the 2 A, 63 V, 1206 fuse. DigiKey showed 14304 of that exact number. The halogen-free 0466002.NRHF, LCSC C3105, is the same series and land and showed 56380 | Exact reel is in stock at DigiKey. The HF suffix was not substituted | Fuse_1206 |
| F_COIL | Littelfuse 0466001.NR, LCSC C151134, 1 A, 63 V, 1206, 50 A interrupt. That page did not show a quantity. The halogen-free 0466001.NRHF, LCSC C151135, showed 24410 | Exact 1 A count is still open. HF stock is not a silent MPN change | Fuse_1206 |
| D_TVS_MCU, D_TVS_COIL | Littelfuse SMAJ18A, JLCPCB C148219, SMA, 18 V stand-off, 29.2 V clamp, 400 W at 10/1000 µs | The JLCPCB page did not show a quantity. A TECH PUBLIC reel is not the accepted part | D_SMA |
| J_USB | Korean Hroparts TYPE-C-31-M-12, LCSC C165948, 16-pin USB 2.0, SMD | LCSC showed 490560 | USB_C_Receptacle_HRO_TYPE-C-31-M-12. Matches |
| D_R, D_G, D_B | No LED MPN is frozen. The resistors still assume 2 mA and a forward drop of 2.0 V red/green and 3.0 V blue | Not counted | LED_0603. R_R, R_G and R_B are in the schematic and are not on the board |
| SW_RST, SW_BOOT | The land is KiCad SW_SPST_TL3342. No E-Switch orderable was given a stock count | Not counted | SPST tactile. Acceptable for reset and boot only |
| SW_REED | The schematic is an ON-ON switch. The placed land is the same two-pad tactile switch | Not a candidate | OPEN. Nets were not stamped onto it |

74LVC1G86GW,125 was not reloaded in this pass. The earlier reading the same day was JLCPCB C12513, 3313 in stock, SOT-353. It has the same land mismatch as U12: the board has SOT-23-5.

KF350 and the Murata module are still not released as lands. The KF350 project footprint uses a 1.0 mm drill because the Cixi Kefa drawing states pin diameter 0.80 mm, pitch 3.50 mm and a 1.0 mm PCB hole. The pad and the courtyard are still the 4Ucon envelope. The MEJ2 drill is 1.00 mm, the tighter of the 1.00 mm and 1.15 mm figures on the Murata recommended footprint. The courtyard is the 19.65 × 10.05 mm maximum, centred on the pin span, because the pin-to-body offset was not fully legible. Do not route around either footprint.

## Revision 0.4 additions, 19 November 2026

TLP291 is no longer an open package. The orderable part is Toshiba `TLP291(GB-TP,SE`, LCSC C4153770. The JLCPCB page for that number showed 1101 in stock, extended, SMT, economic and standard, SOP-4. Pins are 1 anode, 2 cathode, 3 emitter, 4 collector. GB rank CTR is 100% minimum at 5 mA. Isolation is 3750 Vrms, creepage 5.0 mm. The earlier zero-stock lines were a JLCPCB-Assembly placeholder and a SOP-16 listing, not this reel. `R30` and `R40` stay OPEN. At the GB saturated-CTR minimum of 30% at 1 mA, about 2 mA of LED current saturates the 10 kΩ output. The resistor is still not chosen, because the field voltage is unmeasured.

The Murata MEJ2 modules stay. These smaller parts were looked up and not used:

| Candidate | Why it was not used |
|---|---|
| Murata NXJ2S0505MC-R13, C7250507 | JLCPCB stock 0. 400 mA and 5.2 kV, but the body is 16 × 14.5 mm |
| Murata NXE2S0505MC-R13, C5817084 | LCSC page showed no stock count. Isolation listed as 3 kV, below the MEJ2 5.2 kVDC hipot |
| TI UCC12050DVER | TI listed it out of stock. 500 mW is below the CAN load once the preload is included |
| B0505S-1WR3 sold as rlt C512048, YLPTEC C2992394, ZOEYGO C5154856 | In stock, and smaller (11.6 × 6 mm), but the listings are not Mornsun and the isolation on those pages is 1 kV, 3 kV or 1.5 kV. Unregulated |
| YLPTEC B0503S-1WR3, C5369462 | 9342 in stock. Isolation on the page is 1.5 kV. Not a MEJ2 replacement |

Newly confirmed stock on the same date: Diodes AP63205WU-7, C2071056, LCSC page showed 59342, extended SMT. Diodes DMP6023LE-13, C154901, LCSC page showed 2390. AP63203WU-7 is C780769 and the page did not show a quantity. A TECH PUBLIC SMAJ18A, C41425641, showed 2220. That is not the accepted TVS. The branded SMAJ18A quantity was not reconfirmed.

JST B4B-XH-A(LF)(SN), C144395, appeared on an LCSC brand listing as 518040 in stock, extended. JST B5B-XH-A(LF)(SN), C157991, is the 5-pin, 3 A, 250 V, latched header. The JLCPCB extract confirmed the ratings and did not include a stock count. KF350-3.5-2P, C474892, LCSC page showed 22465. KF350-3.5-4P, C42400616, is the contact and permissive terminal. Its JLCPCB page did not show a stock count. The 4Ucon courtyard is still an envelope, not that manufacturer’s drawing.

74LVC1G123, 74LVC1G86, 74LVC1G08, NX6008NBK, the fuses, the USB-C receptacle and the LEDs were not given a fresh stock count in this pass. They stay OPEN.

No fabrication or assembly quotation was fetched. There is still no two-board total.

## Earlier check


Checked 19 November 2026 from JLCPCB and LCSC product pages, plus DigiKey where a Murata module was not listed as Murata stock at LCSC. Pages that did not show a stock count are marked that way. Figures that match the 18 November snapshot are not treated as a new count. No order was placed. No total is a quotation: JLCPCB’s fabrication and assembly fee schedule was not re-read, so a two-board total is not stated.

Assembly priority used here: in-stock basic, then in-stock extended, then a verified alternative, then hand-fit. Nothing was swapped on package size or a nominal current alone.

| Reference | Manufacturer part | LCSC | Stock | Assembly | Alternative | Status |
| --- | --- | --- | --- | --- | --- | --- |
| U1 | Espressif ESP32-S3-WROOM-1-N16 | C2913199 | Not reconfirmed. The 1201 figure is the 18 November snapshot | Extended, SMT, standard PCBA only | None | Use. Stock must be read again at order time |
| U10 | TI ISO1042BDWR | C2671499 | Not reconfirmed. 217 is the old snapshot | Extended, SMT | None accepted | Use. Stock open |
| U5 | TI ISO7721DR, SOIC-8 | C366164 | LCSC page showed 7328 | Extended, SMT | ISO7721DWR is SOIC-16 and is the wrong footprint | Use the 8-pin part. D-package isolation is 3000 Vrms, not the 5000 Vrms wide-body rating |
| U_OPTO (both) | Toshiba TLP291 | — | JLCPCB C9900014135 (SOP-4) showed 0. C9900196983 is SOP-16 and is the wrong package | Extended listings empty | A real Toshiba SOP-4 reel is still required | OPEN. Do not treat the empty listing as the part |
| U4 | Murata MEJ2S0503SC | C38477250 | LCSC page showed 3 | Extended, wave | A non-Murata module is not accepted | Low stock. Two boards need two. Hand-fit if the count is gone |
| U9 | Murata MEJ2S0505SC | Not a Murata LCSC listing | DigiKey 811-2397-ND showed 5517, active, about $15.39 each, 20 week factory lead | Not a JLCPCB Murata assembly part | YLPTEC C5382398 is out of stock and is not Murata. JLCPCB C9900052435 is labelled JLCPCB Assembly, not Murata | Hand-fit the Murata part. Do not assemble the clone |
| K_UP, K_DN | Finder 40.31.7.012.0000 | Not checked this pass | — | Hand-fit | Smaller relays were rejected. Their DC ratings are resistive | Hand-fit. Installation still waits on the measured control current |
| U20 | Diodes AP63203WU-7 | Not rechecked | — | Expected extended SMT | None | OPEN stock |
| U21 | Diodes AP63205WU-7 | Not rechecked | — | Expected extended SMT | None | OPEN stock |
| U11 | Nexperia 74LVC1G123 | Not rechecked | — | Expected extended or basic SMT | None | OPEN stock |
| U8, U12 | 74LVC1G86, 74LVC1G08 | Not rechecked | — | Expected SMT | None | OPEN stock |
| Q_UP, Q_DN, Q_SERIES | Nexperia NX6008NBK | Not rechecked | — | Expected SMT | None | OPEN stock |
| Q_MCU, Q_COIL | Diodes DMP6023LE-13 | Not rechecked | — | Expected SMT | None | OPEN stock |
| Q91 | Diodes DMP3099L | Not rechecked | — | Expected SMT | None | OPEN stock |
| Q clamps | 2N7002 | Not rechecked | — | Often basic | None | OPEN stock |
| D_TVS_MCU, D_TVS_COIL | SMAJ18A | Not rechecked | — | Expected SMT | None | OPEN stock |
| D60, D70 | SS14 | Not rechecked | — | Often basic | None | OPEN stock |
| D20, D21 | BAT54W | Not rechecked | — | Expected SMT | None | OPEN stock |
| F_MCU | Littelfuse 0466002 | Not rechecked | — | Expected SMT | None | OPEN stock |
| F_COIL | Littelfuse 0466001 | Not rechecked | — | Expected SMT | None | OPEN stock |
| J_PWR, J_UP_K, J_DN_K | Cixi Kefa KF350-3.5-2P | C474892 | Not displayed on the page read | Extended, wave, economic and standard | KF127S-5.08-2P is 10 A and 14–26 AWG but its courtyard does not fit this edge | Selected. 10 A, 300 V, 18–24 AWG. Drawing and stock still open. J_PWR and J_UP_K are placed. J_DN_K is placed |
| J_REED, J_DRY, J_UP_S, J_DN_S, J_IGN, J_SW | Ningbo Xinlaiya XY350V-3.5-2P | C784942 | JLCPCB page showed 1791 | Extended, wave | KF350 if a 10 A signal terminal is preferred. These loops are milliamps | In stock. Only J_REED is placed. The other five do not fit the edge |
| J_NMEA | 5-pin terminal, MPN not chosen | — | — | — | A Micro-C is not claimed | OPEN. The 19 mm 5-pin courtyard does not fit beside the CAN module |
| J_USB, LED, SW_RST, SW_BOOT, SW_REED | Not rechecked | — | — | — | — | OPEN. Exact MPNs are not frozen |
| R, C, L | Datasheet values are set. Reels are not | — | — | Prefer basic 0402/0603 | — | OPEN MPN |

## What JLCPCB can assemble, and what is hand-fitted

Factory assembly is the SMT set once each reel’s stock is confirmed, plus wave-soldered terminals that are actually in the JLCPCB library. Hand-fitted for this two-board run:

- Both Finder relays.
- Murata MEJ2S0505SC, bought from an authorised distributor, not from the YLPTEC or “JLCPCB Assembly” listings.
- MEJ2S0503SC as well, if the three pieces at LCSC are not still there at order time.

## Cost

Unit prices actually shown on 19 November 2026: MEJ2S0503SC about $13.84 at qty 1, MEJ2S0505SC about $15.39 at DigiKey qty 1, XY350V about $0.15, ISO7721DR from about $0.50. That is not a board cost. Fabrication, stencil, extended-part setup and shipping were not quoted. Do not treat any earlier estimate as a quotation.

## Before manufacturing files

Read every row marked OPEN or “not reconfirmed” again. The KiCad footprint, the MPN and the JLCPCB line have to be the same part. The MEJ2 drill and the terminal drills are not released until the manufacturer drawings are checked. Do not order.
