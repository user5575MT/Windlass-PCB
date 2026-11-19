# Traceability matrix

Rev 0.2 sheets exist under `kicad/` and KiCad 10.0.8 ERC reported 0 violations (`docs/erc_report.txt`). That is a connectivity check. It is not a current rating, a creepage measurement, or a boat test. The review of what changed, and what is still blocked, is `design_review.md`. Rows below stay OPEN wherever a value on the sheet is marked OPEN or a measurement is still missing.

| Req | Statement (short) | Schematic sheet | Test | Result |
| --- | --- | --- | --- | --- |
| R1 | ESP32-S3-WROOM-1-N16, straps, USB, pads, keepout | esp32 | ERC + layout keepout review + USB enumerate | OPEN |
| R2 | TWAI and GPIO limits | esp32, pin_allocation.md | Datasheet check + ERC | Datasheet check done. ERC 0 violations. Not a layout review |
| R3 | Protected 12 V, 5 V, 3.3 V, thermal | power | Brownout and reverse-polarity bench, actuator disconnected | MCU and coil branches calculated. Coil fuse is 1 A for a 42 mA coil. Load-dump energy OPEN. B6 |
| R4 | High-Z reed, hysteresis, test points | reed | Idle sag vs B4; pulse timing | Thresholds calculated for ±10 µA. Boat idle check OPEN. B4 |
| R5 | UP/DOWN sense | direction_sense | Thresholds vs B5; existing remote still counts | OPEN. Blocked B5 |
| R6 | NO outputs, no backfeed | relay_control_and_interlock | Simulated load only; backfeed measurement | Relay selected, DC1 10 A at 30 V. Installation held until the Lofrans current and inductive energy are measured. B1 |
| R7 | Hardware interlock, weld case | relay_control_and_interlock | Both GPIOs asserted; stuck GPIO; feedback fault | OPEN. Blocked B1, B3 |
| R8 | Relay switch and ignition, not bypassable | relay_control_and_interlock, connectors | Switch off, ignition open, MCU still running, coils off | OPEN. Blocked B2 |
| R9 | 300 ms watchdog contract | relay_control_and_interlock | TTL expiry on a future image; hardware timeout is drawn and is not a firmware edit | Software TTL unchanged. Hardware timer drawn. Not tested. Current image does not kick GPIO1 |
| R10 | Isolated NMEA, no terminator, no NET-S power | isolated_nmea2000 | Barrier hipot or insulation-resistance at the datasheet rating; bus traffic with one publisher | OPEN |
| R11 | Pairing unchanged; one publisher | esp32, connectors | Strap off ⇒ no CAN dominant; pairing fail ⇒ coils off | OPEN. Firmware not in this task |
| R12 | LED states and priority | connectors_status_service | Each state forced; confirm LED not in coil path | OPEN |
| R13 | Connectors, silk, test pads, coating note | connectors | Visual vs ICD | OPEN |
| R14 | 4-layer, returns, isolation, antenna | PCB | DRC + stackup note | OPEN |
| R15 | JLCPCB qty 2 | BOM report | Stock recheck at order time | OPEN. Two snapshots only |
| R16 | Datasheets, no invented MPNs | docs | Review | MCU, reed, CAN, and heartbeat parts cited. Coil chain and R_IN still open |
| R17 | No fab release | — | Exports absent | Holding. No Gerbers |
| R18 | Working prototype untouched | — | WindlassProject not edited | Holding for this session |
| R19 | Actuator disconnected for first power | test plan | Procedure not written | OPEN |
| R20 | 0.36 m configurable, not a hardware constant | reed | NVS calibration still the source | OPEN |

## Independent review vs tools

| Check | Meaning | State |
| --- | --- | --- |
| ERC | KiCad 10.0.8 electrical rules on `kicad/windlass.kicad_sch` | 0 violations, 2026-11-18. See `docs/erc_report.txt` |
| DRC | KiCad layout rules | Not run. No board |
| This matrix and `hazard_analysis.md` | Design review | Written. Not a second person’s sign-off |
| Boat measurement | B1–B8 | Not done |
