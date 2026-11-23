# Prototype remote and the Pi bridge

23 November 2026, Sydney time. The hardware is unchanged. The prototype tree and the Pi bridge were not edited, because neither source is in this repository.

`docs/interface_control_document.md` section P9 is the copy of what `WindlassController` `src/main.cpp` exposes by name. That file is recorded at `C:\Users\thoma\OneDrive\Desktop\WindlassProject\WindlassController\src\main.cpp`, with the project README beside it. A separate publisher lives at `WaveshareReceiver\src\main.cpp` and uses TWAI on GPIO15 and GPIO16, which are not the pins on this board. None of those trees are present here. A search of `user5575MT` on GitHub, a search of the public code for these datagram names, and the Origin namespace available to this run did not contain them.

## What P9 already records

| Item | Recorded value |
| --- | --- |
| SoftAP SSID | `WindlassCounter` |
| Telemetry | UDP broadcast port 4210, magic name `WLC1` |
| Command | UDP port 4212, magic names `WLC1CMD` and `WLC1ACK`, and only when `ENABLE_RELAY_CONTROL` is compiled in. The prototype default is off |
| TTL | 300 ms default, clamped to 150–1000 ms |
| Session | A new RFC4122 UUID after boot, stop, or fault |
| Link loss | The command path drops the coils. The old hold does not resume |

SoftAP presence is not authentication. The decision core in `firmware/s3` keeps that TTL, the session retirement, and the immediate STOP clear. Those rules are tested without a datagram.

## What is missing

A parser cannot be written from the names alone. These items are absent, and `firmware/s3` does not invent substitutes for them:

- The SoftAP password. It is a secret in the prototype `main.cpp` and was not copied.
- The `WLC1` telemetry layout: field order, widths, and encoding.
- The `WLC1CMD` and `WLC1ACK` layouts: field order, widths, encoding, and where the UUID sits.
- The check that decides a UUID is the current session.
- The authentication algorithm, token, and key.
- The Pi windlass bridge: no source file, port, or message definition was found.

Until those exist, the image opens no command socket and transmits no telemetry broadcast. `consider_remote()` rejects every buffer, including the text line this tree used in an earlier draft. `Controller::command()` is not called from the platform. With `WIFI_PASS` left as `CHANGE_ME`, the SoftAP does not start. A real password, supplied at compile time, starts the access point for the chain page only. That page cannot command motion.

The internal session label is the string the missing parser would pass into `Controller::command()`. It is not placed on the air, and it is not presented as an RFC4122 UUID.
