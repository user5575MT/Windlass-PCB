# Pin allocation

This page is the revision 0.2 map in `kicad/esp32.kicad_sch`. The integrated board’s map is in `docs/electrical_review.md`: heartbeat GPIO1, TWAI GPIO4 and GPIO5, reed GPIO6, UP sense GPIO7, DOWN sense GPIO8, requests GPIO9 and GPIO10, coil-rail GPIO14, red GPIO15, green GPIO16, publish GPIO18, USB GPIO19 and GPIO20, UART GPIO43 and GPIO44. GPIO17, GPIO45, and GPIO46 are open. There is no blue LED and no ISO7721. The reed isolator is ISO7720FDR.

Implemented on `kicad/esp32.kicad_sch` for `ESP32-S3-WROOM-1-N16`. Classic ESP32 GPIO25/26/27/32/33 are not on this module and are not reused. This map is for a future image on this board. The running DevKit firmware is not edited.

## Not on this module

| Working DevKit (`main.cpp`) | On this module |
| --- | --- |
| Reed GPIO27 | GPIO27 is not a module pin (internal flash) |
| UP sense GPIO25 | GPIO25 is not a module pin |
| DOWN sense GPIO26 | GPIO26 is not a module pin |
| Bench relays GPIO32, GPIO33 | GPIO32 and GPIO33 are not module pins |

## Straps and fixed pins

| Pin | Use | Constraint |
| --- | --- | --- |
| EN (pin 3) | Reset RC and test pad | Must not float. High = run |
| GPIO0 (pin 27) | BOOT button to GND | Weak pull-up at reset selects normal boot. External pull-up plus a button |
| GPIO3 (pin 15) | Not a function | Datasheet: no internal pull; level must be defined at reset for JTAG-source strap. Hold with a resistor. Do not use as a signal that is high-Z at boot |
| GPIO45 (pin 26) | Do not connect | Weak pull-down. VDD_SPI strap. Do not pull high at boot on this 3.3 V flash module |
| GPIO46 (pin 16) | Do not connect | Weak pull-down. Boot-mode and ROM-print strap. Do not pull high at boot |
| GPIO19 (pin 13) | USB D− | Service USB only |
| GPIO20 (pin 14) | USB D+ | Service USB only |
| GPIO43 (pin 37, TXD0) | UART log test pad | Keep away from the antenna |
| GPIO44 (pin 36, RXD0) | UART log test pad | Same |

GPIO35, GPIO36, and GPIO37 are available on N16 because it has no octal PSRAM. They would be unavailable on N16R8.

## Assigned on the rev 0.2 schematic

| Function | GPIO | Net | Note |
| --- | --- | --- | --- |
| TWAI TX | GPIO4 | TWAI_TX | Series 33 Ω then ISO1042 TXD. TXD also has 10 kΩ to +3.3 V so a floating pin is recessive |
| TWAI RX | GPIO5 | TWAI_RX | ISO1042 RXD |
| Reed, isolated | GPIO6 | REED_GPIO | ISO7721 OUTA. High = idle, low = active |
| UP sense | GPIO7 | UP_SENSE | Opto output. Low = +12 V present on that channel |
| DOWN sense | GPIO8 | DN_SENSE | Same |
| UP coil request | GPIO9 | UP_REQ | 100 kΩ pulldown. High asks for UP. Reset or Hi-Z = off |
| DOWN coil request | GPIO10 | DN_REQ | Same |
| Coil rail present | GPIO14 | COIL_RAIL_OK | Read-only detector after the switch and the ignition contact. Amber when low |
| LED red | GPIO15 | LED_R | Indicator only |
| LED green | GPIO16 | LED_G | |
| LED blue | GPIO17 | LED_B | |
| Publish strap read | GPIO18 | PUBLISH_EN | Same net as the hardware jumper. Firmware cannot power the CAN driver if the jumper is open |
| Heartbeat | GPIO1 | WDI_FUTURE | Rising edge into the 74LVC1G123. 100 kΩ pulldown. The prototype firmware does not toggle this pin, so the coils stay off with that image |
| UART log | GPIO43 / GPIO44 | UART_TX / UART_RX | Test pads |
| Spare, no-connect | GPIO2, GPIO11, GPIO12, GPIO13, GPIO21, GPIO35–42, GPIO47, GPIO48 | — | GPIO11 and GPIO12 are not weld-feedback inputs. The shared +12 V contact node cannot tell a welded contact from the hand remote |
| Do not use at boot | GPIO45, GPIO46 | no-connect | Internal pull-downs. Do not pull GPIO45 high |
| GPIO3 | 10 kΩ to GND | IO3_NET | No internal pull. Default eFuse ignores the level |

GPIO8 is DOWN sense. It is not a spare.

## LED priority

1. Solid red if firmware has latched a fault.
2. Else flashing blue while pairing.
3. Else amber when `COIL_RAIL_OK` (GPIO14) is low: relay switch open or ignition open.
4. Else solid green when the selected link is up and the coil rail is present.

There is no contact-feedback input on this revision, so red is not driven by a weld detector. Green is withheld when amber applies. The LED circuit is not in series with a coil.

## Decoupling and layout constraints already fixed by the vendor guide

- Antenna keepout: no copper on any layer in the module keepout; module at the board edge; 15 mm clearance inside the housing.
- 3.3 V to the module: wide traces (Espressif 4-layer example: at least 25 mil on the main 3.3 V, at least 20 mil at the module power pins), ground under the power pour.
- At the module 3V3 pin the schematic has 10 µF and 100 nF to GND. EN is 10 kΩ to 3.3 V and 1 µF to GND, from the module datasheet.
