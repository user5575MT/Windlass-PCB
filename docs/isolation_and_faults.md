# Isolation boundaries, current paths, and fault cases

Rev 0.2, matching the schematic in `kicad/`. The Lofrans factory schematic was not in the files that were inspected, so terminal names and currents are still OPEN. This diagram is the board copper, not a claim about the boat's internal commons. The fault table in `design_review.md` is the one to use for the watchdog cases.

## Grounds and barriers

```text
GND -------- ESP32, both bucks, coil-FET sources, USB shield network
   |  (board 12 V return. This is the only ground the MCU may use.)
   |
   x  UP_RET ---- TLP291 U6 cathode, D30, C30, J_UP_S pin 2
   x  DN_RET ---- TLP291 U7 cathode, D40, C40, J_DN_S pin 2
   x  REED_RET -- ISO7721 side 2, MEJ2S0503 secondary, J_REED pin 2, J_DRY pin 2
   x  GND_CAN --- ISO1042 side 2, MEJ2S0505 secondary, J_NMEA pin 1 (NET-C), C92
   x  NET-S ----- J_NMEA pin 5 only. No copper net.

+12V_MCU and +12V_COIL split at the connector. They are not joined after the fuses.

UP_COM, UP_NO, DN_COM, DN_NO are dry contact pins. They do not touch any ground. Revision 0.8 routes those four nets on the bottom copper, in the gap between the Finder pin rows. The tracks do not cross the reed barrier or the CAN barrier, and they do not join `UP_RET`, `DN_RET`, `REED_RET` or `GND_CAN` to `GND`.

x = no copper connection on this PCB.
```

`UP_RET` and `DN_RET` are also not connected to each other. The previous prototype fault when the IN2 and IN3 grounds were joined is the reason. If the Lofrans diagram shows one legitimate field return, the join is made in the wiring, not in a pour.

## UP sense current, and the same path for DOWN

When the switched +12 V for that direction is present and `UP_RET` is wired to the real return of that circuit:

```text
J_UP_S pin 1 (UP_FIELD)
  -> R30 (OPEN)
  -> U6 pin 1 anode
  -> U6 LED
  -> U6 pin 2 cathode
  -> J_UP_S pin 2 (UP_RET)
  -> field return, off the board
```

Nothing in that loop enters `GND`. The phototransistor is a separate loop:

```text
+3V3 -> R30P 10k -> U6 pin 4 collector -> GPIO7 (UP_SENSE)
                 -> U6 pin 3 emitter -> GND
```

LED on (direction active) pulls GPIO7 low. That matches the existing firmware, which treats LOW as active. DOWN is the same with `R40`, `U7`, `DN_RET`, GPIO8.

D30 sits anti-parallel to the LED so a reverse pulse on the field pair goes through the diode instead of the LED. C30 is across the same pair. Both stay on `UP_RET`.

## Reed current

The reed wire does not supply the isolator. `U4` is Murata MEJ2S0503SC. Its secondary is the only source of `REED_3V3`.

```text
+5V / GND  ->  U4 primary
U4 secondary: REED_3V3 and REED_RET   (floating relative to GND)

Lofrans position, one shunt on JP_REED pins 1-2:
  J_REED pin 1 -> R20 10k -> LOFRANS_NODE -> header pin 1 -> pin 2 -> REED_ISO -> ISO7721 INA
  R23 47k and C22 1 nF from REED_ISO to REED_RET only
  D20, D21 clamp LOFRANS_NODE to the isolated rail

Dry position, the same shunt on JP_REED pins 2-3:
  J_REED pin 3 (DRY_A) -> header pin 3 -> pin 2 -> REED_ISO
  R22 4.7k from REED_3V3 to DRY_A only
  J_REED pin 4 = REED_RET

Shunt removed: R23 holds REED_ISO low. No rising edge, so the input is idle.

ISO7721 OUTA (side 1) -> GPIO6, powered from +3V3 / GND
```

In the Lofrans position, `R22` has no path to `REED_SIG`. Idle near 3.3 V becomes a high on GPIO6. Active near 0 V becomes a low. Leakage and threshold figures are in `design_review.md`. Fit one shunt only. `JP_REED` pins 1 and 3 are not tied in copper.

Startup edges are in `docs/connector_pinout.md`. The existing firmware counts a debounced rising edge only while direction sense is already UP or DOWN, and the level present at MCU start is not an edge. Field-supply startup and removing the shunt produce a falling edge or no edge with this no-F isolator. Field-supply shutdown, and inserting the shunt onto a high source, can each produce one rising edge, and that edge increments the counter only if the windlass sense is already active. The firmware file was not edited.

## Dry contacts

```text
J_UP_K pin 1 UP_COM -> K_UP contact -> J_UP_K pin 2 UP_NO
J_DN_K pin 1 DN_COM -> K_DN contact -> J_DN_K pin 2 DN_NO
```

Coil current, separate from the contact:

```text
+12V_COIL -> J_SW -> J_IGN -> R_COILFEED 0R -> COIL_12
COIL_12 -> relay coil -> coil NMOS -> Q_SERIES -> GND
Q_SERIES gate = XOR(UP_REQ, DN_REQ) AND heartbeat Q
```

`R_COILFEED` is not a bypass of the heartbeat. `+12V_MCU` does not enter this path.

The hand remote and the Lofrans wireless controller stay in parallel with `UP_COM`/`UP_NO` and `DN_COM`/`DN_NO`. This board is not in series with them. Unplugging the contact connectors leaves their path untouched. Unplugging the board's power leaves the coils open.

## Fault cases

| Case | What the copper does |
| --- | --- |
| UP_RET joined to DN_RET on this PCB | Not possible. There is no such track. The earlier fault mode is not redrawn. |
| Installer joins the two returns in the loom when the Lofrans diagram says not to | Off-board wiring error. The PCB cannot prevent it. The connectors are separate so the diagram can be followed either way. |
| UP_RET left open | That opto LED has no return. The channel reads inactive. It does not take a path through GND or through the other channel. |
| Field wire shorted to the other channel's return | Current can flow only if the installer has created that path. The PCB does not. |
| 12 V applied to the reed pin | 10 kΩ and the field clamps, about 0.8 mA into the isolated rail. It does not enter the ESP32 pin except through the isolator. |
| ESP32 ground tied to a sense return by a later "cleanup" | Re-creates the prototype fault. Silk and this note are the control. There is no single ground pour across those nets. |
| Both GPIO requests high, or both stuck high | 74LVC1G86 output is low, so the AND is low and `Q_SERIES` is off. Each gate is also clamped by the other request. Both coils stay off if either mechanism is intact. |
| One GPIO stuck high, the other low, heartbeat still running | That one coil can energise. The 300 ms TTL stops it only while firmware is running. A stopped heartbeat drops `Q_SERIES` within one timeout. The relay-power switch and the ignition contact still remove coil power. |
| Heartbeat stuck high or stuck low | `Q_SERIES` drops after at most one monostable pulse. A level does not refresh it. The current firmware produces no edges, so the coils stay off. |
| 3.3 V logic supply lost | Series-FET gate pulldown wins because the 74LVC output is high-Z. Coil drivers off. A welded contact is unchanged. |
| One clamp FET fails open and the XOR fails stuck high, both requests high | The unclamped channel can run. The other channel is still clamped, so this is one direction, not both. Both directions need both clamps to fail as well as the XOR. |
| Contact welded | Coil-off does not open it. The paralleled +12 V line is high whenever the hand remote or the Lofrans remote commands that direction, so sensing that node cannot tell a welded contact from a legitimate operator. No auxiliary contact is fitted, because no relay MPN is chosen. Detection of a weld is therefore not claimed. |
| Our contact closed while the other operator commands the opposite direction | This PCB cannot see or stop the other operator. Both contactors can be asked to run. Residual hazard H11. |
| NET-S tied to +12 V or to GND by a later edit | Would bridge or backfeed the backbone. Pin 5 of `J_NMEA` is no-connect. |
| Publish jumper fitted while the Waveshare still transmits | Two 128777 sources. The jumper is open by default and is the hardware lock. Fitting it is a deliberate act. |
| Publish jumper open | CAN DC-DC primary is off. ISO1042 datasheet: bus pins are high-impedance when unpowered. This board does not drive or bias the bus. |
| Lofrans or hand remote operated with this board removed | Their contacts never went through this PCB. They still work. |

## What is still blocked on the Lofrans drawing

- Which terminal is the shared +12 V feed, if there is one. `UP_COM` and `DN_COM` are separate so either answer can be wired.
- Inrush and hold current. Relay, flyback diode, coil FET and fuse stay OPEN.
- Where the ignition contact sits today, and its current.
- Whether UP and DOWN already share a field return. This PCB does not assume either answer.
