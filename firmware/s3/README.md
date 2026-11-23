# Integrated ESP32-S3 image

This tree is the controller for `kicad11/windlass_install_v2.kicad_pcb`. The prototype `WindlassController` sources are not in this repository and are not built here.

Host checks, from this directory:

```text
make test
```

That builds the decision core with the system compiler and runs the watchdog, STOP, link-loss, conflict, heartbeat, chain, remote-gap, and NMEA tests. It does not flash a board.

The sketch is `platform/esp32s3_main.cpp`, for the Arduino-ESP32 core on an ESP32-S3. `setup()` drives GPIO1, GPIO9, and GPIO10 low before Wi-Fi or TWAI start. There is no timer interrupt on GPIO1. Set `WIFI_PASS` at compile time. The placeholder `CHANGE_ME` is not a boat password.

## GPIO

| Function | GPIO | Net | Level |
| --- | --- | --- | --- |
| Heartbeat | 1 | WDI_FUTURE | Rising edge only while one direction is authorised |
| TWAI TX / RX | 4 / 5 | TWAI_TX / TWAI_RX | 250 kbit/s. Silent until GPIO18 is high and an address claim has succeeded |
| Reed | 6 | REED_GPIO | Rising edge after 30 ms, and only for one direction |
| UP / DOWN sense | 7 / 8 | UP_SENSE / DN_SENSE | Low means 12 V is present |
| UP / DOWN request | 9 / 10 | UP_REQ / DN_REQ | High asks. Reset and high-Z stay off |
| Coil rail | 14 | COIL_RAIL_OK | High means the switched rail is present |
| Red / green | 15 / 16 | LED_R / LED_G | Both together is the amber indication. No blue LED |
| Publish strap | 18 | PUBLISH_EN | Input with pulldown. Open strap, and the hardware jumper, keep the bus silent |

GPIO0, GPIO3, GPIO45, and GPIO46 are not driven. USB is GPIO19 and GPIO20. UART test pads are GPIO43 and GPIO44.

## Commands

The byte layout is `docs/pi_bridge_protocol.md`. It is WLC2, HMAC-SHA256, UDP port 4212 for commands and 4210 for signed telemetry. The unrecovered prototype layout is not accepted. The Pi bridge in the boat is not modified by this tree; it has to be changed to this specification before a radio test.

Build with both secrets set, each at least 16 bytes and neither equal to `CHANGE_ME`:

```text
-DWIFI_PASS=\"the-softap-password\" -DCOMMAND_KEY=\"the-command-key\"
```

`WIFI_PASS` only starts the SoftAP and the chain page. `COMMAND_KEY` is the HMAC key. SoftAP presence is not authentication. With either secret left as `CHANGE_ME`, the command socket stays closed and a hold cannot start.

The chain page is HTTP port 80 and has no UP, DOWN, or STOP control.

A hold lasts for the command TTL. That TTL is clamped to 150–1000 ms and defaults to 300 ms. STOP, expiry, a conflict, coil-rail loss, and loss of the command link clear both requests and GPIO1 immediately, retire the session, and ignore a later RUN until STOP has been accepted on the new session. A repeated sequence does not refresh the hold. UP hauls chain in. DOWN pays chain out. The default is 360 mm per pulse, stored with the pulse count.

## Build

From this directory, `./build_image.sh` compiles the ESP32-S3 image with arduino-cli. The default image uses the placeholder secrets, so it boots with the coils off and does not open the access point. Pass the two secrets as arguments to build the image the Pi will talk to. The script does not flash.

## NMEA 2000

TWAI is 250 kbit/s on GPIO4 and GPIO5. Publishing stays off until GPIO18 reads high. The node then waits 0–255 ms, sends ISO address claim PGN 60928, and waits 250 ms before any other PGN. A lower NAME takes the next address, through 251, and then the null address 254, which sends no windlass status. The NAME uses industry group 4, device class 100, function 0, and manufacturer code 0. The public function list for class 100 has Scale (Catch) at function 130 and no windlass entry, and no manufacturer code is assigned to this project. The unique number is the low 21 bits of the MAC.

Once claimed, the node sends PGN 128777 and PGN 128778 once a second, and PGN 126993 every 60 s. Product information PGN 126996 is the 132-byte form, sent only in reply to an ISO request, so the certification-level field is omitted. PGN 128776 is ignored on reception and is never transmitted. Rode is 0.1 m per count. A negative count is sent as unavailable. Line speed, controller voltage, motor current, and motor time are unavailable. Docking is unavailable. Windlass ID is 0. This is not an NMEA certification.
