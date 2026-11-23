# Assumptions and open questions

Rev 0.1 of the schematic uses the confirmed prototype findings. These are no longer open:

- UP and DOWN commands are switched +12 V. The new contacts are normally open and sit in parallel with the Lofrans wireless controller and the hand remote. Parallel operation has been bench-tested. The contacts on the schematic are dry and the two commons are not tied, so a shared or a split feed can both be wired.
- Direction sensing is two optical channels. Their returns are not connected to ESP32 ground and not connected to each other. That is the correction for the IN2/IN3 ground fault.
- The reed is not a PC817 input. It is a high-impedance isolator. Idle about 3.22–3.3 V, active about 0 V, still has to be confirmed on the boat with this input connected.
- NMEA side-2 ground is not the ESP32 ground. NET-S is not used. No terminator is fitted.

Still open, and still able to cause a wrong relay, a fire, or a second chain count:

## Blocking measurements

### B1 — Output contact circuit

Measure at the existing Lofrans / hand-remote terminals, windlass breaker open or actuator disconnected:

- Is each direction a dry NO contact, a switched +12 V, or a switched ground?
- What is the common (shared +12 V feed, shared ground, or neither)?
- Voltage across the load and current while a contactor is pulled in, and inrush if it is visible on a scope.
- Inductive or lamp/resistive? Is there already a freewheel diode, and across which two terminals?
- With this board’s future contacts imagined in parallel: can that path put 12 V back onto the hand remote or the Lofrans wireless box?

Do not finalise relay type, contact rating, or suppression without this.

### B2 — Ignition / engine permissive

The brief requires a hardwired permissive. The inspected firmware has no ignition pin. Record:

- Where the existing permissive is (series in the Lofrans coil feed, a key switch, an engine-running contact, or absent).
- Open-circuit voltage and closed current.
- Confirm it must stay in series with this board’s coil supply, and that the Lofrans path is unchanged if this board is removed.

### B3 — Weld and stuck-contact behaviour of the real load

From B1 current, state the contact current against the candidate relay’s welded-contact guidance. Also decide the system rule when feedback says a contact is stuck closed: operator action, pull the windlass breaker, or both. This board cannot open a welded contact.

### B4 — Reed source

With the existing controller disconnected from the reed:

- Idle voltage, active voltage, and rise/fall time of one chain pulse.
- Source impedance, or the voltage sag when a known resistor (100 kΩ, then 10 kΩ) is applied from the reed line to the Lofrans reference.
- Which conductor is the reference, and is it galvanically the same as battery negative?

The new input must leave idle at the unloaded value within a limit set from this measurement. The old PC817 result (3.22 V → 1.5 V) is the failure to avoid.

### B5 — Direction sense

- Idle and active voltage of UP and of DOWN, relative to which ground.
- Are these the same nodes as the output command lines in B1, or separate taps?
- Confirm LOW = active on the present opto outputs matches the boat, and which physical wire is UP. README and `main.cpp` disagree (GPIO26 vs GPIO25).

### B6 — 12 V source and enclosure

- Which battery and which breaker feed this board.
- Whether the feed can see alternator load dump (engine running, same battery).
- Maximum board outline, cable direction, metal or plastic enclosure, and whether the ESP32 antenna can sit with 15 mm clearance to metal.

Fuse, TVS, and the buck thermal calculation wait on this and on B1.

### B7 — Watchdog semantics

Inspected contract (`main.cpp`): while a valid hold is refreshed, firmware drives the relay GPIO to the ON level and holds it. If no refresh arrives for `RUN_TTL_DEFAULT_MS` (300 ms), firmware writes both GPIOs OFF. Range allowed in firmware is 150–1000 ms. That file has no heartbeat output. It was not modified.

Rev 0.2 draws the hardware timer anyway: 74LVC1G123, about 330 ms typical, 475 ms long case. GPIO1 must rise at least every 100 ms or the coils drop. The current image does not do that, so this board’s coils stay off until a separately reviewed image exists. The 300 ms TTL is unchanged and is a different mechanism. See `design_review.md`.

### B8 — NMEA drop and the existing receiver

- Can a real NMEA 2000 drop reach this mounting place?
- Are both backbone ends already terminated?
- When this board is allowed to transmit, is the Waveshare receiver removed or its transmitter disabled?
- Is wireless-RX-only an acceptable build option if the backbone cannot be reached? The publish strap supports that, but only one publisher may be active.

## Assumptions (not yet allowed to size parts)

| ID | Assumption | If wrong |
| --- | --- | --- |
| A1 | Module `ESP32-S3-WROOM-1-N16`, no PSRAM, is enough flash and temperature margin. | Change module before layout. Octal PSRAM parts lose GPIO35–37 and drop to 65 °C. |
| A2 | Isolated CAN is `ISO1042BDWR`. On the integrated board the supply is Murata MEJ2S0305SC, 3.3 V to 5 V, fed from `+3V3` through JP1. The earlier line that the DC-DC was not chosen is closed for this board. | A different isolator package changes the barrier layout. |
| A3 | Coil drivers will be powered only from the switched 12 V rail, and GPIO reset/Hi-Z leaves coils off. | Revisit if B1 shows the “relay” is actually a logic line into the Lofrans box rather than a contact in parallel. |
| A4 | Chain calibration stays in firmware NVS. Hardware only conditions edges. | None expected. |
| A5 | Four-layer stackup will be JLCPCB’s standard 4-layer (impedance profile to be copied from their current stackup page when layout starts). | Controlled-impedance notes change if they publish a different stack. |
| A6 | Through-hole screw terminals and any relay will be hand-fitted if JLCPCB will not assemble that exact part at quantity 2. | Assembly drawing must say so. |
| A7 | KiCad 10.0.8 produced the integrated netlist, the ERC, and the DRC. The earlier line that it was not installed is closed. | A different KiCad version can move a file format. |

## Explicitly not assumed

- That the Lofrans ground is this board’s ground.
- That a 120 Ω resistor belongs on this drop.
- That NET-S may power the CAN transceiver.
- That GPIO32/33 from the classic ESP32 bench code exist on this module.
- That the LED, or a green indication, means the windlass is safe to approach.
- That an interlock on this PCB stops the existing remote.
