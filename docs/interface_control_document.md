# Interface control document

Electrical values marked OPEN are not to be designed around until measured. Logic and protocol values below are copied from the working tree so this board can speak the same contract later. This document does not change that contract.

## P1 — Power input

| Item | Value | Status |
| --- | --- | --- |
| Nominal | 12 V marine DC | From brief |
| Connector | Locking / screw, pin 1 = +12 V, pin 2 = GND, silk polarity | Connector MPN OPEN |
| MCU load | ESP32-S3 TX current up to 355 mA at 3.3 V (module datasheet) plus logic and isolated DC-DC | Budget OPEN until DC-DC chosen |
| Relay coil load | Unknown | OPEN B1 |
| Source | House bank, windlass breaker, or other | OPEN B6 |
| Reverse polarity | MCU and coil branches each have a DMP6023LE and a fuse. Reverse connection turns the FET off and the unidirectional SMAJ18A is cleared by the fuse | Drawn. Not tested |
| Load dump | SMAJ18A is fitted on both branches and is not load-dump protection. Energy and source impedance are unmeasured | OPEN B6 |

MCU 3.3 V and relay coil 12 V split after the input protection. Opening the relay switch does not remove MCU power.

## P2 — Reed

| Item | Value | Status |
| --- | --- | --- |
| Idle | About 3.2–3.3 V (brief). README recorded 3.22 V before a PC817 load | Confirm on the boat, B4 |
| Active | Near 0 V while the magnet is passing | Confirm, B4 |
| Known bad load | PC817 input pulled idle to 1.5 V | Do not repeat |
| Edge | Working firmware counts a stable reed level after 30 ms debounce. README: count on the HIGH transition of the opto output after an LED bypass | Re-validate on this conditioner, B4 |
| Increment | Configurable. Working default `mmPerTurn = 360` (0.36 m) if NVS is empty | Firmware, not a hardware constant |
| Reference | Lofrans ground vs this board’s ground is not assumed common | OPEN B4 |

Test points: reed as it arrives, and the logic-level signal at the GPIO.

## P3 — UP and DOWN sense

| Item | Value | Status |
| --- | --- | --- |
| Nominal | 12 V direction signals (brief) | Topology OPEN B5 |
| Working firmware | Opto output, external 3.3 V pull-up, LOW = active. Input side of the opto isolated from the ESP32 | Confirm the boat still matches this |
| Code pins today | UP GPIO25, DOWN GPIO26, reed GPIO27 on the classic ESP32 | Do not copy onto the S3 module |
| README pins | UP GPIO26, DOWN GPIO25 | Disagrees with `main.cpp`. Wiring on the boat is OPEN |
| Conflict | Both active → direction `X`, reed edges ignored | Preserve in future firmware; hardware still reports both |

## P4 — UP and DOWN outputs

| Item | Value | Status |
| --- | --- | --- |
| Function | NO contacts in parallel with existing Lofrans / hand-remote controls | Wiring OPEN B1 |
| De-energised | Coils off. Contacts open if they are not welded | Contact form OPEN until relay is chosen |
| Backfeed | Must not power the hand remote or the Lofrans controller through our contacts | OPEN B1, B3 |
| Coil supply | Relay switch in series with ignition permissive | Ignition location OPEN B2 |
| Drive polarity on the old bench module | Active-LOW GPIO into a relay module | That module is not this PCB. New drivers are active such that reset/Hi-Z = coil off |

## P5 — Ignition / engine permissive

Hardwired series element in the coil supply. The MCU may only sense it, for the amber LED. No GPIO enables the coils if this contact is open. Voltage, current, and where it sits in the existing boat are OPEN (B2). Not present in the inspected firmware.

## P6 — Relay-power switch

Panel or enclosure switch in the coil supply only. MCU power bypasses it. The MCU may sense the switched rail for the amber LED. There is no GPIO enable in the current firmware (`main.cpp` comment: physical coil-power switch is the hardware enable).

## P7 — NMEA 2000 drop

| Signal | Connection | Status |
| --- | --- | --- |
| CAN_H, CAN_L | ISO1042 bus pins, common-mode range per that datasheet | Part candidate only |
| NET-C | Isolated-side ground reference | Required |
| NET-S | Not used as device power. No connection that can feed the backbone | Required |
| SHIELD | Capacitor to isolated ground at this drop | Value OPEN with the DC-DC choice |
| Termination | None fitted. Backbone ends stay the only terminators | Required unless a measured topology says this node is an end |
| Bit rate | 250 kbit/s NMEA 2000 | Firmware, later |
| PGNs in the existing design | 128777 operating status; 128778 monitoring. No 128776 motor command on NMEA | Do not add motor commands on NMEA in this hardware pass |
| Duplicate source | Publish-enable strap off ⇒ transceiver does not drive the bus | Waveshare must stay off the bus when the strap is on |

Certification is not claimed.

## P8 — USB service

USB-C, ESP32-S3 native USB (GPIO19 D−, GPIO20 D+). Service and recovery only. Not a power source for coils. CC resistors and ESD are part of the esp32 sheet. Exact connector MPN OPEN.

## P9 — Wireless (existing contract, unchanged)

Copied from `WindlassController` `main.cpp` so a later image can keep it. Not implemented by this hardware task, and not to be edited in the working tree.

| Item | Value |
| --- | --- |
| SoftAP SSID | `WindlassCounter` (password is a secret in the working source; not copied here) |
| Telemetry | UDP `WLC1` broadcast port 4210 |
| Command | UDP port 4212, `WLC1CMD` / `WLC1ACK`, only if `ENABLE_RELAY_CONTROL` is compiled in. Default compile is off |
| TTL | Default 300 ms, allowed 150–1000 ms |
| Session | New RFC4122 UUID required after boot, stop, or fault |
| Loss of link | Command path must drop coils. No resume without a new hold |

## P10 — LED

See architecture. Amber means “this board will not move the windlass” (switch or ignition). It does not mean the Lofrans remote is disabled. Red is a local fault, including contact-feedback disagreement. Green is not permission to stand in the chain path.
