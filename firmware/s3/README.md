# Integrated ESP32-S3 image

This tree is the controller for `kicad11/windlass_install_v2.kicad_pcb`. The prototype `WindlassController` sources are not in this repository and are not built here.

Host checks, from this directory:

```text
make test
```

That builds the decision core with the system compiler and runs the watchdog, STOP, conflict, heartbeat, chain, and protocol tests. It does not flash a board.

The sketch is `platform/esp32s3_main.cpp`, for the Arduino-ESP32 core on an ESP32-S3. `setup()` drives GPIO1, GPIO9, and GPIO10 low before Wi-Fi or TWAI start. There is no timer interrupt on GPIO1. Set `WIFI_PASS` at compile time. The placeholder `CHANGE_ME` is not a boat password.

## GPIO

| Function | GPIO | Net | Level |
| --- | --- | --- | --- |
| Heartbeat | 1 | WDI_FUTURE | Rising edge only while one direction is authorised |
| TWAI TX / RX | 4 / 5 | TWAI_TX / TWAI_RX | 250 kbit/s. Frames only if the publish strap is high |
| Reed | 6 | REED_GPIO | Rising edge after 30 ms, and only for one direction |
| UP / DOWN sense | 7 / 8 | UP_SENSE / DN_SENSE | Low means 12 V is present |
| UP / DOWN request | 9 / 10 | UP_REQ / DN_REQ | High asks. Reset and high-Z stay off |
| Coil rail | 14 | COIL_RAIL_OK | High means the switched rail is present |
| Red / green | 15 / 16 | LED_R / LED_G | Both together is the amber indication. No blue LED |
| Publish strap | 18 | PUBLISH_EN | Read only. Open strap sends no status frames |

GPIO0, GPIO3, GPIO45, and GPIO46 are not driven. USB is GPIO19 and GPIO20. UART test pads are GPIO43 and GPIO44.

## Commands

SoftAP SSID `WindlassCounter`. Telemetry is UDP broadcast port 4210. Commands are UDP port 4212. The chain page is HTTP port 80 and has no UP, DOWN, or STOP control.

```text
WLC1CMD <session> <sequence> <UP|DOWN|STOP|BOTH> <ttl_ms>
WLC1ACK <session> <sequence> <OK|REJECT>
WLC1 <session> <pulses> <mm> <mm_per> <U|D|X|S> <running> <fault> <locked>
```

The TTL is clamped to 150–1000 ms and defaults to 300 ms. After STOP, expiry, a conflict, or coil-rail loss, the session changes and a RUN is ignored until STOP has been accepted on the new session. A repeated sequence does not refresh the hold. UP hauls chain in. DOWN pays chain out. The default is 360 mm per pulse, stored with the pulse count.

The prototype datagram bytes were not in this repository. This text is the contract for this image.
