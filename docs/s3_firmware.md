# ESP32-S3 image and the continuous both-request check

Nothing in this pass was flashed. The prototype firmware was not in this repository and was not edited. No Gerber was written and no part was ordered. The board is not approved for fabrication or for installation.

## Continuous both-request check

`U12` and `U15` are 74LVC1G34 buffers. `R60` and `R70` are 100 Ω, 1206. `Q_CLAMP_UP` and `Q_CLAMP_DN` are NX3008NBK. With both requests held high, each buffer sources about 34 mA into its 100 Ω and the opposite clamp. That is under the buffer’s ±50 mA limiting value and under its 100 mA supply-current limit. The resistor is about 112 mW, inside the 1206’s derated rating at 85 °C (about 206 mW). The clamp dissipation is under 4 mW. Package dissipation in the buffer at the published 24 mA point is about 24 mW, inside the SOT353 rating at 85 °C. No part and no copper changed. The arithmetic is in `docs/install_protection.md`. It is not a measurement on a board. At 125 °C ambient the same 1206 would be under the 112 mW, and that ambient is outside the ESP32-S3-WROOM-1-N16 rating used for this board.

## GPIO review

The firmware constants were checked against a netlist exported from `kicad11/windlass.kicad_sch` and against the pad nets of `U3` on `kicad11/windlass_install_v2.kicad_pcb`.

| Net | Schematic pin | Module GPIO | Firmware |
| --- | --- | --- | --- |
| WDI_FUTURE | U3 pin 39, IO1 | GPIO1 | Heartbeat |
| TWAI_TX / TWAI_RX | pins 4 / 5 | GPIO4 / GPIO5 | Status frames only |
| REED_GPIO | pin 6, IO6 | GPIO6 | Chain count |
| UP_SENSE / DN_SENSE | pins 7 / 12 | GPIO7 / GPIO8 | Direction |
| UP_REQ / DN_REQ | pins 17 / 18 | GPIO9 / GPIO10 | Requests, active high |
| COIL_RAIL_OK | pin 22, IO14 | GPIO14 | Permissive |
| LED_R / LED_G | pins 8 / 9 | GPIO15 / GPIO16 | Indicators |
| PUBLISH_EN | pin 11, IO18 | GPIO18 | Strap read |
| EN_NET | pin 3 | EN | Not driven by the image |
| IO0_NET / IO3_NET | pins 27 / 15 | GPIO0 / GPIO3 | Not driven |

GPIO17, GPIO45, and GPIO46 are unconnected on the board. The image does not drive them.

## What the image does

`firmware/s3` keeps the documented behaviour of the prototype and adds the GPIO1 heartbeat:

- Chain count is a debounced rising edge, 30 ms, and only while exactly one sense input is active. The level present at startup is not a pulse. UP decreases the count. DOWN increases it. The default is 360 mm per pulse. The count and the calibration are saved.
- The web page sets that calibration and the saved count. It has no run control.
- Remote UP, DOWN, and STOP use the session and sequence rules in `firmware/s3/README.md`.
- Status frames are PGN 128777 and 128778, and only while the publish strap is high. PGN 128776 is not sent.
- GPIO1 edges exist only while one request is authorised. STOP, a 300 ms expiry, both directions, and loss of the coil rail clear the requests and hold GPIO1 low in the same step. A RUN on a retired session does not start the windlass. After a stop, a RUN is ignored until STOP has been accepted on the new session.
- Outputs are written low at the start of `setup()`, before the radio. A stalled `loop()` produces no further edges. The pulldowns and the monostable are what hold the coils off if the CPU stops.

## Tests

`make test` in `firmware/s3` passed at 4:34 pm Sydney time on 23 November 2026. The compiler was g++, `-Wall -Wextra -Werror`. The cases cover boot outputs off, the 300 ms expiry, the 150 ms and 1000 ms clamps, a repeated sequence, STOP ahead of a later RUN, both-direction fail-off, heartbeat edges only during a hold, rail loss, chain edges, saved position, the web form, and the two status frames. The platform file is checked for a low write on GPIO1 before Wi-Fi and for the absence of a timer interrupt.

## Remaining before a bench flash

- The prototype packet layout and its SoftAP password were not in this repository. This image uses the text protocol in the firmware README. The existing remote has to be pointed at that protocol, and `WIFI_PASS` has to be set, before a radio test.
- The NMEA frames are a bench encoding of the two status PGNs. There is no address claim and no fast-packet transport. Certification is not claimed. The publish strap must stay open while any other 128777 source is on the backbone.
- The chain sense of UP and DOWN, and the reed edge against the Lofrans magnet, still need a boat measurement. The blanker can drop one pulse when the field supply returns during that pulse.
- The 34 mA both-request figure and the clamp off-level are datasheet calculations. They have not been measured.
- B1, B2, B3, and B6 in `docs/assumptions_and_open_questions.md` are still open. This image does not close them.
