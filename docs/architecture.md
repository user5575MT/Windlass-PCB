# Architecture

This page is the preliminary architecture. The integrated board does not use the AP63205 or the MEJ2S0505SC named below. U9 is a Murata MEJ2S0305SC fed from 3.3 V through JP1. The parts list is `docs/integrated_bom.md`.

Preliminary. Relay contact circuit, coil current, ignition wiring, and input thresholds are not frozen. They stay open until the measurements in `assumptions_and_open_questions.md` are answered. Nothing here authorises fabrication, a firmware flash, or a wiring change on the working prototype.

## Role

One new board mounted beside the existing Lofrans controller. It is an additional parallel operator.

- Existing Lofrans wireless controller and the wired hand remote keep working if this board is unplugged or unpowered.
- This board must not backfeed those controls and must not load the Lofrans reed the way the earlier PC817 input did (idle fell from 3.22 V to 1.5 V; see WindlassProject README).
- Chain length may be published on isolated NMEA 2000 **or** the existing wireless receiver path may be kept. Both must not publish at once.
- Motor run authority, if later enabled, is hold-to-run with the existing 300 ms command TTL. That TTL is a software timer in `WindlassController` (`RUN_TTL_DEFAULT_MS`). It is not a hardware watchdog on the present prototype.

```text
House / windlass 12 V
        │
        ├─ fuse, reverse polarity, transient clamp ── MCU buck/LDO ── ESP32-S3 always (sense, radio, NMEA)
        │
        └─ physical relay-power switch ── ignition/engine contact ── relay coil supply
                    (both hardwired; MCU cannot bypass)

Lofrans reed ── high-Z conditioner ── ESP32          (no DC load that sags the 3.2 V idle)
Lofrans UP/DOWN sense ── protected inputs ── ESP32   (count direction from any operator)
ESP32 requests ── hardware interlock ── two NO contacts in parallel with existing UP/DOWN controls

ESP32 TWAI ── ISO1042 ── isolated 5 V ── NMEA drop (CAN_H, CAN_L, NET-C reference, shield)
                         NET-S is not a power source and is not backfed
```

## Power

Two supplies from the same nominal 12 V connector, split after protection:

1. **MCU rail.** Its own fuse, reverse-polarity FET, and TVS, then two bucks: AP63205 to 5 V and AP63203 to 3.3 V. The linear 3.3 V regulator is not used. The MCU stays up when the relay switch is off.
2. **Relay coil rail.** A separate fuse and reverse-polarity FET, then the physical switch and the ignition contact, then a series FET that is on only while a hardware heartbeat is fresh and exactly one direction is requested. Coil current is unmeasured, so that fuse, that FET, and that TVS stay open. Software cannot jumper the switch or the ignition contact.

The heartbeat is a 74LVC1G123. A static high or low on GPIO1 does not hold the coils. Detail and the fault table are in `design_review.md`.

## Logic

**Module.** `ESP32-S3-WROOM-1-N16` (LCSC C2913199 snapshot 2026-11-18). 16 MB quad flash, no PSRAM, PCB antenna, −40 to 85 °C, native TWAI. No-PSRAM is deliberate: octal-PSRAM variants (`N16R8` and similar) take GPIO35–37 and are rated only to 65 °C unless PSRAM ECC is enabled. This firmware does not need PSRAM. Classic ESP32 GPIO25/26/27/32/33 are not the pinout of this module; GPIO32 is not brought out. The new pin map is in `pin_allocation.md`. It applies to a future image for this board only. The running DevKit firmware is not edited to match it.

**Antenna.** Module at the board edge, copper-free keepout on every layer under the antenna, at least 15 mm clearance inside the enclosure (Espressif layout guide). A metal box makes this fail; enclosure material is OPEN.

**USB.** Native USB on GPIO19/20 to a service USB-C connector. Boot and EN buttons, plus test pads, for recovery. USB does not power the relays.

**NMEA 2000.** `ISO1042BDWR` (LCSC C2671499 snapshot) on the TWAI pins. Bus side power is a Murata MEJ2S0505SC, a separate module from the reed supply, secondary ground not joined to the reed return or to ESP32 ground. Murata rates the family at 5.2 kVDC hipot for 1 second and 2.4 kVDC continuous, as functional isolation, not a safety barrier. Termination is not fitted. NET-S is not connected. No certification is claimed. PCB creepage is not drawn yet.

**Duplicate publishers.** A hardware publish-enable strap gates the transceiver enable (or equivalent) so this board cannot drive CAN_H/CAN_L unless that strap is set. Wireless-RX operation is the other position: NMEA driver held off, existing receiver remains the only 128777 source. The strap is read by firmware; the electrical off state does not depend on firmware. Leaving the existing Waveshare transmitter connected while this strap is on is a residual hazard (H10).

**Status LED.** Three discrete LEDs or one common-cathode RGB, driven by GPIO. Priority, highest first: solid red fault; flashing blue pairing; amber when the relay-power switch is off or the ignition permissive is open; solid green only when a link is up and both permissives are closed. The LED is an indicator. It is not in the coil path and is not a safety interlock.

**Wireless pairing.** Keep the existing SoftAP contract (WPA2, local `WLC1` telemetry, command path only if a future approved image enables it). This hardware design does not change secrets, ports, or retransmission. Pairing indication is the blue flash. Fail-safe if pairing is lost: coil requests off. Exact state machine stays the one already in the controller tree; it is not redefined here.

## Outputs and interlock (topology only)

Not designed at component level until questions B1–B4 are measured.

Intent, so the later sheet has a target:

- Two normally-open contacts, one UP and one DOWN, electrically in parallel with the existing control contacts.
- Coil power only from the switched, ignition-gated rail.
- A hardware path that cannot energise both coils when both GPIOs are asserted, stuck, or the MCU is reset. A static heartbeat level cannot hold coil power either. A welded contact still conducts with the coil off, and this board does not claim to detect that weld: the paralleled +12 V node is high whenever the other operator commands that direction.
- Safe state with coil power removed, MCU reset, heartbeat expired, or GPIO high-impedance: both of this board’s coils de-energised. Contact state then depends on the contact itself.
- This PCB cannot stop the Lofrans remote or the hand remote from commanding the opposite direction. That conflict is residual (H11) and needs a system rule, not a trace on this board.

## What is intentionally absent

- Always-on 120 Ω CAN terminator.
- A path from NET-S into the 12 V or 5 V rails.
- A GPIO that can override the relay switch or the ignition contact.
- Any change to `WindlassProject`, the Venus gateway, or the flashed prototype.
