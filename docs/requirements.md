# Requirements

IDs are stable. Verification is OPEN until a schematic sheet, an ERC log, or a hardware test exists. “Sheet” names the hierarchical sheet that will carry the requirement. None of those sheets exist yet.

Source of the requirement list: `Windlass_PCB_Cursor_Brief.md` (Downloads, 2026-11-18) plus constraints read from the working WindlassProject tree.

| ID | Requirement | Sheet | Verification |
| --- | --- | --- | --- |
| R1 | ESP32-S3-WROOM family module, exact orderable part, antenna keepout, flash/PSRAM called out, reset/boot straps, decoupling, USB programming, recovery pads. | esp32 | OPEN. Candidate recorded in architecture. ERC not run. |
| R2 | Native TWAI confirmed for that module; GPIO restrictions applied. | esp32 | OPEN. Datasheet states TWAI / ISO 11898-1. Pin map is preliminary. |
| R3 | Protected nominal 12 V input: fuse, reverse polarity, surge/load-dump basis, filter, brownout behaviour, 5 V and 3.3 V, thermal budget, protection coordination. No generic buck module. | power | OPEN. Blocked on B1, B6. |
| R4 | High-impedance reed input. Must not load the Lofrans reed. Hysteresis, test points, pulse polarity checked on the bench. | reed | OPEN. Blocked on B4. Prior failure: 3.22 V idle pulled to 1.5 V. |
| R5 | Two protected UP/DOWN sense inputs. Direction counting still works for the existing operators. | direction_sense | OPEN. Blocked on B5. |
| R6 | Two NO outputs in parallel with the existing 12 V controls. Pinout, de-energised state, and no-backfeed written down from real wiring. | relay_control_and_interlock | OPEN. Blocked on B1–B3. |
| R7 | Hardware interlock so both directions cannot be driven together by GPIO, stuck pin, or firmware crash. Welded-contact case analysed. Coil interlock alone is not enough. | relay_control_and_interlock | OPEN. Blocked on B1, B3. |
| R8 | Physical relay-power switch, separate from MCU power, hardwired. Ignition/engine permissive hardwired. Software cannot bypass either. Coils default off on boot, reset, brownout, watchdog expiry, and disabled state. | relay_control_and_interlock, connectors | OPEN. Ignition wiring not found in firmware (B2). |
| R9 | 300 ms control watchdog contract preserved. Do not change the existing timing. | relay_control_and_interlock | OPEN. See B7. Present contract is a software TTL, not a hardware timer. |
| R10 | Isolated NMEA 2000: isolated transceiver, isolated DC-DC, CAN_H/CAN_L, NET-S/NET-C, shield, creepage, ESD. No always-on 120 Ω terminator. Do not power the backbone or bridge the barrier. | isolated_nmea2000 | OPEN. Transceiver candidate recorded. DC-DC part not chosen. |
| R11 | Wi-Fi pairing compatible with the existing interface. No silent change to firmware auth or retransmission. Direct NMEA and wireless RX must not both publish. | esp32, connectors_status_service | OPEN. Strap defined in architecture. Firmware not modified. |
| R12 | Multicolour LED: solid green = link and controls enabled; flashing blue = pairing; solid red = fault; amber = relay switch off or ignition open. Priority defined. LED is not a safety function. | connectors_status_service | OPEN. |
| R13 | Locking or screw connectors for 12 V, reed, sense, contacts, ignition, NMEA. USB-C for service. Pin 1, polarity, and names on silk. Mounting, strain relief, coating notes, test pads. | connectors_status_service | OPEN. |
| R14 | Four-layer board, stated stackup, return paths, isolation keepout, antenna clearance. SMD on one side where practical. | PCB | OPEN. No layout. |
| R15 | Parts chosen so two boards can be assembled at JLCPCB, with stock, minimums, and through-hole limits checked per part. | BOM | OPEN. Two parts snapshotted. Rest not checked. |
| R16 | Datasheets cited for safety-critical parts. No invented part numbers. | all | OPEN. Two candidates have URLs. Relay and power parts do not. |
| R17 | Exports marked NOT FOR FABRICATION until sign-off. No order placed. | manufacturing | Holding. No exports yet. |
| R18 | Existing prototype firmware and wiring are not modified by this design. | process | Holding. This repo is new; WindlassProject was read only. |
| R19 | Prototype bring-up starts with the windlass actuator disconnected and a simulated load. | test plan | OPEN. Test plan not written (Phase C). |
| R20 | Chain increment defaults to 0.36 m per pulse and stays configurable. Not hard-coded as a resistor or a fixed firmware constant on this board. | reed / firmware note | OPEN. Hardware only counts edges. The 0.36 m figure stays a firmware calibration, as it is today (`mmPerTurn`). |
