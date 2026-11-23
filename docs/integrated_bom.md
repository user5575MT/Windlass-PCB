# Integrated controller BOM

Parts as drawn in `kicad11/windlass.net`. 128 fitted parts, plus four M3 mounting holes that are on the PCB and not in the schematic. No price is stated. Stock was not re-checked for this list. A JLCPCB line is not a claim that the part is basic-library or in stock. The coil-driver and contact-protection calculations are in `docs/install_protection.md`.

Hand-fitted parts: both Finder relays, both genuine Murata modules, and the USB-C receptacle if the assembler does not place it. Do not substitute the LCSC listing that uses the MEJ2S part number and is made by YLPTEC.

## Power

| Ref | Value | Footprint | Role |
| --- | --- | --- | --- |
| J_PWR | KF350-3.5-2P | windlass:KF350-3.5-1x02 | 12 V input |
| F_MCU | 0466002, 2 A | Fuse_1206 | MCU branch fuse |
| F_COIL | 0466.250, 250 mA | Fuse_1206 | Finder coil branch fuse. Cold resistance 0.691 Ω. It is not the contactor fuse |
| D_TVS_MCU, D_TVS_COIL | SMAJ18A | SMA | 18 V unidirectional TVS, not load-dump protection |
| Q_MCU, Q_COIL | DMP6023LE-13 | SOT-223 | reverse-polarity P-FETs |
| D_Z_MCU, D_Z_COIL | BZT52C12 | SOD-123 | gate clamps |
| R_MCU_G, R_COIL_G | 100 kΩ | 0402 | gate pull-downs |
| U20 | AP63203WU-7 | TSOT-23-6 | 12 V to 3.3 V buck |
| L20 | SRN6045-3R3Y, 3.3 µH | windlass:L_Bourns_SRN6045 | buck inductor. Isat 5.0 A, Irms 3.2 A. SRN4018-3R3M was rejected: Isat 2.3 A is below the AP63203 3.1 A peak-limit maximum |
| C30I | 22 µF, 25 V, X7R, GRM32ER71E226KE15 or equivalent | 1210 | buck input. Effective capacitance at 12 V is measured on the first article |
| C30A, C30C | 22 µF, 16 V or higher, X7R | 0805 | buck output |
| C30B | 100 nF | 0402 | bootstrap |

There is no 5 V logic rail and no second buck.

## Controller, USB, indicators

| Ref | Value | Footprint |
| --- | --- | --- |
| U3 | ESP32-S3-WROOM-1-N16 | module, no PSRAM |
| J_USB | USB4105 | USB-C 16-pin, top-mount horizontal |
| U_ESD | USBLC6-2SC6 | SOT-23-6, VBUS pin on USB_VBUS |
| R15, R16 | 5.1 kΩ | CC pull-downs |
| R17, R18 | 22 Ω | D+ / D− series |
| R19 | 1 MΩ | shield to GND, with C13 100 nF |
| C10 | 1 µF, 16 V or higher | EN delay, with R10 10 kΩ. Not module bulk |
| C11 | 10 µF, 16 V or higher | 3.3 V rail |
| C12 | 100 nF, 16 V or higher | 3.3 V rail. The USB shield capacitor is C13 |
| R10, R11, R12 | 10 kΩ | EN, GPIO0, GPIO3 straps |
| R13, R14 | 100 kΩ | request pulldowns |
| SW_BOOT, SW_RST | TL3342F160QG | boot and reset |
| D_PWR | LTST-C190KRKT | 3.3 V power LED, R_PWR 1 kΩ |
| D_R | LTST-C190KRKT | GPIO15, R_R 680 Ω |
| D_G | LTST-C190KGKT | GPIO16, R_G 680 Ω |

GPIO17 is not connected. The blue LED and its transistor are gone. Test points: TP_3V3, TP_GND, TP_TX, TP_RX, TP_REED, TP_WDI.

## Reed input

| Ref | Value | Role |
| --- | --- | --- |
| U4 | MEJ2S0303SC | genuine Murata 3.3 V to 3.3 V, functional isolation only |
| R24 | 51 Ω, 0.5 W, 2512 | preload, about 65 mA |
| U5 | ISO7720FDR | fail-safe low isolator, SOIC-8 narrow body |
| U13, U14 | 74LVC1G00GW | blanker latch |
| Q_BLK, Q_NPG | 2N7002BK | blank and power-good invert |
| D20, D21 | BAT54W | Lofrans clamp to the field rail and return |
| D22, D23 | BAT54W | reset diode-OR |
| R20 | 10 kΩ | series into the Lofrans node |
| R22 | 4.7 kΩ | dry-contact pull-up only |
| R23 | 47 kΩ | holds the isolator input low with the shunt off |
| C22 | 1 nF | input filter |
| JP_REED | 1×03 2.54 mm | default shunt on pins 1–2, Lofrans |

The shunt itself is not a fitted part.

## Direction sense

| Ref | Value | Role |
| --- | --- | --- |
| U6, U7 | TLP291(GB-TP,SE) | UP and DOWN optocouplers |
| R30, R40 | 4.7 kΩ | LED series, an assumption, see the design note |
| D30, D40 | 1N4148W | anti-parallel |
| C31, C41 | 100 nF | across each LED |
| R30P, R40P | 10 kΩ | collector pull-ups, active low |

No isolated supply on these channels. `UP_RET` and `DN_RET` are not joined.

## Relay control

| Ref | Value | Role |
| --- | --- | --- |
| K_UP, K_DN | Finder 40.31.7.012.0000 | 12 V coil, 288 Ω, 42 mA. Contact DC1 is 10 A at 30 V DC resistive |
| Q_UP, Q_DN, Q_SERIES | ZXMS6004FFTA | protected low-side switches. SOT23F on the existing SOT-23 land. Pin 1 drain, pin 2 IN, pin 3 source |
| R60, R70 | 1 kΩ | series into the up and down inputs, so 100 µA of input current stays above the 3.0 V on-threshold |
| Q_CLAMP_UP, Q_CLAMP_DN | 2N7002BK | cross-clamp, no XOR and no AND |
| U11 | 74LVC1G123DP,125 | heartbeat, about 330 ms typical |
| C50 | 3.3 µF, 50 V, X7R, GRM31CR71H335KA88L or equivalent, 1206 | timing capacitor. Nominal pulse stays about 330 ms with R52 at 100 kΩ. Measure the Q pulse |
| R52 | 100 kΩ | timing resistor |
| D60, D70 | SS14 | Finder coil flyback only. Nothing on this board joins COM to NO |
| J_PERM | KF350 4-pin | external relay-power switch and ignition, both in series |
| J_CONTACT | KF350 4-pin | UP_COM, UP_NO, DN_COM, DN_NO. Two independent dry contacts |
| R_SWLINK, R_IGNLINK, R_COILFEED | 0 Ω | the series links in that external path |

Not on this PCB, fitted at each Quick contactor: one 3 A, 400 V diode such as a 1N5404, cathode to the switched positive and anode to the coil return, and the boat’s existing 2.5 A fast control fuse. F_COIL does not carry contactor current. The contact copper is 1.2 mm, the IPC-2221 external 1 oz, 10 °C figure for that 2.5 A fuse.

## NMEA 2000

| Ref | Value | Role |
| --- | --- | --- |
| U10 | ISO1042BDWR | isolated CAN transceiver |
| U9 | MEJ2S0305SC | genuine Murata 3.3 V to 5 V, functional isolation only |
| R94 | 120 Ω, 0.5 W, 2512 | preload on the isolated 5 V, not a bus terminator |
| JP1 | 1×02, fitted open | publish enable, default off |
| R90 | 100 kΩ | holds the module input off |
| R91 | 10 kΩ | jumper sense to GPIO18 |
| R92 | 10 kΩ | TXD pull-up |
| R93 | 33 Ω | TXD series |
| C92 | 100 nF, 50 V, X7R, GRM155R71H104KE14 or equivalent, 0402 | shield to GND_CAN only. Both nets are on the isolated side |
| J_NMEA | B5B-XH-A | drop connector, pin 5 NET-S is not connected |

No 120 Ω resistor is fitted across CANH and CANL.
