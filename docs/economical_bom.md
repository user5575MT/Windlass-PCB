# Economical single-distributor selection

25 November 2026, Sydney time (AEDT, UTC+11). Nothing was ordered, nothing was flashed, and no new copper was routed. The home-assembly board on the parent branch is the checkpoint and was not edited.

The distributor for this selection is DigiKey Australia. Every price below was read from a DigiKey Australia product page on this date. Where the page showed the ex-GST quantity price and the GST footer, both are quoted. Where the extract showed only the quantity price, the including-GST figure is that price plus 10 percent, which is the GST those other pages add, and the line is marked computed.

This is not yet a cart that can be imported. The lines that were opened add to A$131.93 including GST. The five-board JLCPCB quote already on the checkpoint is A$28.70 and is only a stand-in until this board has an outline. The 5 V regulator, the logic, the optocouplers, the small transistors, the diodes, the passives and the connectors are specified below and are not in that sum, because their pages were not the ones returned. Routing waits until those lines are opened on the same distributor.

## What changed, and what did not

The boat still sees two independent dry contacts, a hardware ignition loop, and a hardware panel switch. Neither switch is a GPIO. The MCU rail and the coil rail stay on separate fuses. A static level on the heartbeat pin cannot hold a coil. Both direction requests together still hold both coils off. The contacts do not switch the motor. Isolation between the controller, the reed side and the CAN side stays functional isolation, not a marine safety barrier.

The coil voltage is no longer the raw boat voltage. A 7812 sits after the ignition loop, so an open ignition switch or an open panel switch removes the regulator input and both coils drop. The MCU regulator is on the other fuse and stays up. That is what lets the relays be ordinary 12 V parts whose coils are not rated to 18 V.

## Relay and the regulated coil rail

Omron G2R-1-DC12, DigiKey 39-G2R-1DC12-ND, 4,468 in stock. A$8.92 ex GST, A$9.812 inc GST, so two are A$19.624. SPDT, 275 Ω, 43.6 mA, must-operate 8.4 V, must-release 1.8 V. The contact table in the G2R datasheet rates the one-pole part at 5 A, 30 VDC, L/R = 7 ms. That covers the boat's 2.5 A control fuse. The datasheet also says the 110 percent maximum coil voltage is the highest voltage that can be applied, and Omron's ratings page says that figure is not a continuous rating. The regulator's job is to hold the coil at its rated 12 V, not to sit at 13.2 V.

ST L7812CV, DigiKey 497-1452-5-ND, 14,098 in stock. A$1.99 ex GST, A$2.189 inc GST. Positive 12 V, 1.5 A, TO-220, 35 V maximum input, dropout 2 V at 1 A typical. The input maximum covers the P6KE18A clamp. The 2 V dropout figure is the 1 A typical, so it overstates the drop at 44 mA. Used as a bound anyway, the G2R is guaranteed to pick up only when the regulator input is at least 10.4 V. Engine-running voltage is above that. A resting battery near 12 V still has margin once the real drop at 44 mA is less than 2 V. Confirm that drop on the first board.

The 7812 needs a few milliamps of load to stay in regulation. With both coils off it has none, so a 1 kΩ, 0.5 W bleeder from the 12 V output to ground is part of the circuit. It draws 12 mA and dissipates 0.14 W. It is not priced yet.

At 14.8 V in and one coil, the 7812 dissipates about 0.12 W. At 18 V in with both coils on, about 0.5 W. A TO-220 does that in free air. A switching 12 V module was looked at and not used: the Recom R-7812-0.5 and R-78E12-0.5 both need 15 V in before they regulate, which a 12 V battery does not provide.

## Controller supply

The controller still needs its own regulator from the unswitched, fused, reverse-protected input, with enough input rating for the P6KE18A clamp. The Recom and Murata 5 V pages searched for this did not come back as those parts, so no 5 V regulator is in the sum. The requirement for that line is a through-hole 5 V output, at least 500 mA, input from about 7 V to at least 32 V. The Thing Plus 5 V pin is fed through a series Schottky so a USB plug on the module cannot back-feed the regulator. Do not also feed the module's 3.3 V pin.

## Isolated converters

The CAN rail has to stay inside the MCP2562 recommended range, 4.5 V to 5.5 V. The DigiKey page for that transceiver shows the same range.

Traco TMR 0511, DigiKey 1951-2740-ND, 674 in stock. The quantity table shows A$25.46, so A$28.01 including GST, computed. One output, 5 V, 400 mA, 4.5 V to 9 V in, 1.5 kV isolation, SIP. The October 2026 TMR 2 datasheet gives set accuracy ±1 percent maximum, line regulation 0.2 percent maximum, load regulation 0.5 percent maximum from 10 percent to 90 percent load, and no minimum load. Stacked with the temperature coefficient, the output stays near 5.1 V, inside 4.5 V to 5.5 V. This is functional isolation. It is not the 5.2 kV Murata hipot, and it is not a safety barrier.

The reed side has no 5 V logic IC. It drives optocoupler LEDs. Recom RFM-0505S, DigiKey 945-3159-ND, 19,505 in stock, quantity price A$3.22, so A$3.54 including GST, computed. It is the unregulated 1 W part, and its load-regulation envelope is the reason it is not on the CAN rail. Size the LED resistors for the high end of that envelope. No bleeder is required on the TMR. The RFM still needs enough load that it is inside the region its datasheet actually specifies.

A regulated through-hole module at this price is the economical regulated choice that is in stock. The Murata NXE1S0505MC is about A$4.87 and has tens of thousands in stock, and it is an iLGA surface-mount part, so it is not in this home-assembly list. Two TMR 0511 modules would cost more than the two Murata modules on the checkpoint, so the second domain stays on the RFM.

## Watchdog

TI CD74HCT4538E, DigiKey 296-2125-5-ND, 267 in stock. A$1.77 ex GST, A$1.947 inc GST. DIP-16, 4.5 V to 5.5 V, so it runs on the controller 5 V rail and a 3.3 V GPIO high is a legal input.

The pulse is 0.7 × RX × CX. RX is 470 kΩ, 1 percent. CX is 1 µF, 5 percent, film. Nominal pulse 329 ms. TI's −55 °C to 125 °C window at the 10 kΩ / 0.1 µF test point is 0.850 to 1.150 of the formula. Applied here, the short corner is 263 ms and the long corner is 401 ms. The firmware short bound is 264 ms and the original long bound is 475 ms. The long corner is inside 475 ms. The short corner is 1 ms under the firmware constant and is above 200 ms, which is two 100 ms intervals, and above the 160 ms assert in the header. That 1 ms is inside the extrapolation: the K window is specified at 10 kΩ and 0.1 µF, not at 470 kΩ and 1 µF. Time the first board.

Retrigger is microseconds to a few tens of microseconds, so the existing 80 ms heartbeat is not blanked. Power-up reset holds Q low, so the coils stay off until a real rising edge. GPIO1 stays the heartbeat pin, with the 100 kΩ pulldown. The unused half is tied so it cannot time out into a coil. The firmware file is not edited.

This part is not on the checkpoint copper. The fresh layout is where it gets placed. The earlier attempt to patch it onto the existing tracks shorted a pin to 5 V and was reverted.

## Fuse

There is no 5×20 holder in this selection. Both fuses are Littelfuse PICO II 251, axial, fast, 125 VAC and 125 VDC, interrupting 50 A AC and 300 A DC.

Coil fuse: 0251.630MXL, DigiKey F2312-ND, 990 in stock. A$2.18 ex GST, A$2.398 inc GST. 630 mA. Nominal melting I²t 0.08 A²s. One G2R coil is 44 mA and both are 87 mA, so the fuse is not asked to carry a normal load near its rating. A fault between roughly 200 mA and 630 mA can sit there without opening. A lower-current 251 was not the page that came back.

Controller fuse: 0251002.MXL, DigiKey F2314-ND, 19,677 in stock. A$1.83 ex GST, A$2.013 inc GST. 2 A. Nominal melting I²t 0.405 A²s. This fuse is the converter branch, not the coil protection.

The melting integral is not the total clearing time. The forward safe operating area of the coil FETs is not closed until a datasheet gives a maximum opening time or a total clearing integral. The 300 A DC interrupt is real and is the right voltage class for this rail. It is not a guarantee against a short, heavy cable that can deliver more than 300 A. The boat's battery fuse remains the high-energy interrupt.

## ESP32-S3

DigiKey Australia does not have an Espressif DevKitC-1 in stock. The DevKitC-1U-N8R8 listing is the U.FL module, 8 MB flash, and it showed zero stock. The DFRobot DevKitC-1 listing showed zero stock.

The board that is in stock, and that breaks out every GPIO this firmware uses, is the SparkFun Thing Plus ESP32-S3, DEV-24408, DigiKey 1568-24408-ND, 577 in stock. A$41.44 ex GST, A$45.584 inc GST. The module is ESP32-S3-MINI-1-N4R2: 4 MB flash, 2 MB PSRAM, PCB antenna, ambient rating −40 °C to 85 °C. The page contents are a board and a cable. It does not say the pin headers are fitted, so the socket order has to include male headers for the module as well as female sockets on the PCB. Those headers are not priced yet.

The headers carry GPIO 1, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16 and 18, which is the whole firmware map apart from the UART pins the checkpoint left unconnected. GPIO35–37 are not used. GPIO0 is the onboard status LED and GPIO46 is the RGB LED; neither is in the coil path.

GPIO8 and GPIO9 are also the fuel-gauge I²C pins. The Thing Plus schematic shows 2.2 kΩ pull-ups on those nets to the peripheral 3.3 V rail, which is on by default. GPIO9 is the up request and the pull-up holds it high until the firmware drives it. The series FET is off until the watchdog sees rising edges, so a high request during that window does not energise a coil. GPIO8 is the down sense, active low meaning voltage present, so the pull-up idles as "not present" and the optocoupler has to sink about 1.5 mA. Do not clock the fuel gauge. Leave the peripheral-power jumper in its default closed state.

Mouser's US catalog showed ESP32-S3-DevKitC-1-N8R8 with 459 pieces that can ship immediately, and the European catalog showed ESP32-S3-DevKitC-1-N32R16V with 1,102 pieces that can dispatch immediately. The Australian site lists the N32R16V at A$25.34. That Australian page would not open from here, so those counts are not this cart. An N32 module can keep the existing 16 MB partition table because the image only uses the bottom of the flash. An N8 or the 4 MB Thing Plus cannot.

The current build line is `FlashSize=16M,PartitionScheme=app3M_fat9M_16MB`. The tree does not mount a FAT, SPIFFS or LittleFS volume. Preferences uses NVS. The built image is 458,361 bytes. The Arduino-ESP32 default 4 MB scheme gives an app slot of 1.25 MB and still has an NVS partition. The only change for this module is the board option:

`FlashSize=4M,PartitionScheme=default,CDCOnBoot=cdc,PSRAM=disabled`

That is a build configuration change. The source is not edited here, and nothing is flashed. PSRAM stays disabled, so the 2 MB PSRAM and its GPIO26 connection are left alone. GPIO26 is not in the firmware map.

## Lines opened on 25 November 2026

| Buy | Part | DigiKey | Stock | Each inc GST | Line inc GST |
|---|---|---|---|---|---|
| 1 | SparkFun Thing Plus ESP32-S3, DEV-24408 | 1568-24408-ND | 577 | 45.584 | 45.584 |
| 2 | Omron G2R-1-DC12 | 39-G2R-1DC12-ND | 4,468 | 9.812 | 19.624 |
| 1 | Traco TMR 0511 | 1951-2740-ND | 674 | 28.006 computed | 28.006 |
| 1 | Recom RFM-0505S | 945-3159-ND | 19,505 | 3.542 computed | 3.542 |
| 3 | Infineon IRLZ44NPBF | IRLZ44NPBF-ND | 40,342 | 2.926 | 8.778 |
| 2 | Infineon IRF9540NPBF | IRF9540NPBF-ND | 7,268 | 4.466 | 8.932 |
| 1 | Microchip MCP2562-E/P | MCP2562-E/P-ND | 759 | 2.123 | 2.123 |
| 2 | Everlight 6N137, DIP-8 | 1080-1485-ND | 389 | 3.399 computed | 6.798 |
| 1 | ST L7812CV | 497-1452-5-ND | 14,098 | 2.189 | 2.189 |
| 1 | TI CD74HCT4538E | 296-2125-5-ND | 267 | 1.947 | 1.947 |
| 1 | Littelfuse 0251.630MXL, coil | F2312-ND | 990 | 2.398 | 2.398 |
| 1 | Littelfuse 0251002.MXL, controller | F2314-ND | 19,677 | 2.013 | 2.013 |

Opened lines: **A$131.93** including GST. DigiKey Australia delivery is A$0 at A$60 including GST or more, and A$24 under that. These goods are over A$60, so the published delivery on this parcel is A$0. The minimum purchase on every line above is 1.

The checkpoint JLCPCB quote for five 120 mm × 112 mm boards, delivered, is USD 19.02, A$28.70 at the rate already used on that quote, and that quote shows no GST. It is not an order for this new outline. Added only as a ceiling for the bare boards, the opened parts plus that quote are **A$160.63**. The unpriced lines below sit on top of that.

## Still to open before routing

Same distributor, through-hole, in stock. Not in the sum.

- The 5 V controller regulator, input to at least 32 V, 500 mA or more.
- CD74HCT125E, SN74HC00N, SN74HC08N.
- Four PC817 optocouplers in DIP-4.
- Three BC547B, emitter-base-collector, for the cross-clamps.
- 1N5817 for the module feed, two coil flyback diodes, the small signal diodes and clamps, two P6KE18A, two BZX55C12.
- 470 kΩ 1 percent, 1 µF 5 percent film, the 1 kΩ 0.5 W bleeder, the other resistors, and the bypass and bulk capacitors.
- Screw terminals for power, the two dry contacts, and the ignition loop, so the boat wiring does not change. Female sockets and male headers for the Thing Plus.
- The 5 V regulator's input capacitor and the 7812's recommended input and output capacitors.

The ignition connector is still four positions: coil positive, panel-switch return tied to ignition input, and ignition return into the 7812. The dry contacts stay independent, commons not tied, normally-closed pins open.
