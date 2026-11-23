# ESP32-S3 image and the continuous both-request check

Nothing in this pass was flashed. The prototype firmware was not in this repository and was not edited. No Gerber was written and no part was ordered. The board is not approved for fabrication or for installation.

## Continuous both-request check

`U12` and `U15` are 74LVC1G34 buffers. `R60` and `R70` are 100 Ω, 1206. `Q_CLAMP_UP` and `Q_CLAMP_DN` are NX3008NBK. With both requests held high, each buffer sources about 34 mA into its 100 Ω and the opposite clamp. That is under the buffer’s ±50 mA limiting value and under its 100 mA supply-current limit. The resistor is about 112 mW, inside the 1206’s derated rating at 85 °C (about 206 mW). The clamp dissipation is under 4 mW. Package dissipation in the buffer at the published 24 mA point is about 24 mW, inside the SOT353 rating at 85 °C. No part and no copper changed. The arithmetic is in `docs/install_protection.md`. It is not a measurement on a board. At 125 °C ambient the same 1206 would be under the 112 mW, and that ambient is outside the ESP32-S3-WROOM-1-N16 rating used for this board.

## GPIO review

The firmware constants were checked against a netlist exported from `kicad11/windlass.kicad_sch` and against the pad nets of `U3` on `kicad11/windlass_install_v2.kicad_pcb`.

| Net | Schematic pin | Module GPIO | Firmware |
| --- | --- | --- | --- |
| WDI_FUTURE | U3 pin 39, IO1 | GPIO1 | Heartbeat |
| TWAI_TX / TWAI_RX | pins 4 / 5 | GPIO4 / GPIO5 | NMEA 2000, silent until claimed |
| REED_GPIO | pin 6, IO6 | GPIO6 | Chain count |
| UP_SENSE / DN_SENSE | pins 7 / 12 | GPIO7 / GPIO8 | Direction |
| UP_REQ / DN_REQ | pins 17 / 18 | GPIO9 / GPIO10 | Requests, active high |
| COIL_RAIL_OK | pin 22, IO14 | GPIO14 | Permissive |
| LED_R / LED_G | pins 8 / 9 | GPIO15 / GPIO16 | Indicators |
| PUBLISH_EN | pin 11, IO18 | GPIO18 | Strap read, pulldown, default unpublished |
| EN_NET | pin 3 | EN | Not driven by the image |
| IO0_NET / IO3_NET | pins 27 / 15 | GPIO0 / GPIO3 | Not driven |

GPIO17, GPIO45, and GPIO46 are unconnected on the board. The image does not drive them.

## What the image does

`firmware/s3` keeps the chain counter and the safety rules that are specified without a datagram, and it leaves the prototype untouched:

- Chain count is a debounced rising edge, 30 ms, and only while exactly one sense input is active. The level present at startup is not a pulse. UP decreases the count. DOWN increases it. The default is 360 mm per pulse. The count and the calibration are saved in NVS under the `chain` namespace (`pulses` and `mm`) on the device, and in the host memory store in tests.
- The web page sets that calibration and the saved count. It has no run control. The page is served only when `WIFI_PASS` is compiled to a value other than `CHANGE_ME`. The placeholder does not start the SoftAP.
- The prototype command bytes, password, UUID placement, authentication check, and Pi bridge are missing. The image opens no UDP command socket and sends no telemetry broadcast. Every buffer presented to `consider_remote()` is rejected. The platform does not call `Controller::command()`. The missing list is `docs/protocol_gap.md`.
- NMEA 2000 uses the ESP32-S3 TWAI peripheral at 250 kbit/s on GPIO4 and GPIO5. GPIO18 is an input with a pulldown, and the hardware jumper also holds the ISO1042 off when open. Frames start only after that pin reads high, a 0–255 ms claim delay, ISO address claim PGN 60928, and 250 ms of quiet. Status is then PGN 128777 and PGN 128778 once a second. PGN 126993 follows every 60 s and is the network heartbeat, separate from GPIO1. PGN 126996 is the 132-byte product-information form, on ISO request only, so no certification level is sent. A received PGN 128776 is ignored and is never transmitted. The NAME is industry 4, class 100, function 0, manufacturer 0, arbitrary-address capable, unique number from the low 21 bits of the MAC, preferred address 128. A lower NAME moves the address up to 251 and then to the null address 254, which stops the status PGNs.
- GPIO1 edges exist only while one request is authorised. The edge is every 80 ms, high for 40 ms. That period is inside the 100 ms contract, and two edges fit in the 264 ms short pulse of the 74LVC1G123 (100 kΩ and 3.3 µF; typical 330 ms; long case about 475 ms). STOP, a 300 ms expiry, both directions, command-link loss, and loss of the coil rail clear the requests and hold GPIO1 low in the same step. A RUN on a retired session does not start the windlass. After a stop, a RUN is ignored until STOP has been accepted on the new session. The platform reports the command link down, so this image does not start a hold.
- Outputs are written low at the start of `setup()`, before the radio. A stalled `loop()` produces no further edges. The pulldowns and the monostable are what hold the coils off if the CPU stops.

## Tests

`make test` in `firmware/s3` passed at 4:49 pm Sydney time on 23 November 2026. The compiler was g++, `-Wall -Wextra -Werror`. The cases cover boot outputs off, the 300 ms expiry, the 150 ms and 1000 ms clamps, a repeated sequence, STOP ahead of a later RUN, both-direction fail-off, heartbeat edges only during a hold, the 80 ms edge against the 264 ms short pulse, rail loss, command-link loss, chain edges, saved position, the web form, rejection of the earlier text line and of a binary buffer, the published address-claim NAME sample, the 250 ms claim quiet time, PGN 128777 and 128778 field coding, a received PGN 128776, the 132-byte product information, the 60 s NMEA heartbeat, and address-claim loss through to the null address. The platform file is checked for a low write on GPIO1 before Wi-Fi, for the absence of a timer interrupt, and for the absence of a command call.

## Remaining before a bench flash

- The prototype packet layout, its SoftAP password, and the Pi bridge are still absent. A radio test of the existing remote has to wait for those sources. Pointing the remote at a made-up line would not be that remote.
- The NMEA field coding follows the public canboat layouts, including address claim. It is not an NMEA certification. The publish strap must stay open while any other 128777 source is on the backbone. The monostable pulse has not been measured on a board.
- The chain sense of UP and DOWN, and the reed edge against the Lofrans magnet, still need a boat measurement. The blanker can drop one pulse when the field supply returns during that pulse.
- The 34 mA both-request figure and the clamp off-level are datasheet calculations. They have not been measured.
- B1, B2, B3, and B6 in `docs/assumptions_and_open_questions.md` are still open. This image does not close them.
