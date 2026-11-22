# Integrated windlass controller

22 November 2026. One new PCB replaces the revision 0.8 layout. The old design stays in `kicad/` and was not edited. The new schematic and board are in `kicad11/`. Nothing in this file is a fabrication release. No Gerber, drill, or position file was written. No part was ordered. The prototype was not flashed or deployed, and the 300 ms software watchdog, the authentication, and the CAN retransmission were not changed.

## What changed

The board is 200 × 160 mm and four layers. Inner 1 is a ground pour, inner 2 is 3.3 V, and the outer layers also get a ground pour. There is no fixed outline from revision 0.8.

Removed, because each one repeated something else or existed only to feed a rail that is gone:

- The 74LVC1G86 XOR and the 74LVC1G08 AND. The two 2N7002 cross-clamps already hold a coil gate off when the other request is on, and both requests on hold both gates off.
- The 5 V buck, its fuse, and the AP2112. The ESP32 and the logic run from one AP63203 3.3 V buck.
- The blue LED, its transistor, and GPIO17.
- The mid-mount HRO USB-C footprint. The connector is a GCT USB4105, top-mount, so the signal pads sit on the board.
- The second publish FET. A jumper in the MEJ2 primary turns the isolated CAN supply on. It is open unless someone fits the shunt.

Kept, because each one is the hardware interlock firmware cannot bypass:

- Two Finder 40.31 relays. The contacts are in parallel with the existing windlass controls. `UP_COM` is not tied to `DN_COM`. The NC pins are not connected. Unplugging or unpowering this board leaves the Lofrans controller in circuit.
- The external relay-power switch and the external ignition, both in series with the coil feed, ahead of the onboard FETs.
- A series FET, Q_SERIES, that the 74LVC1G123 holds on only while GPIO1 keeps producing edges. A static level does not retrigger it. Nexperia’s timing, with 100 kΩ and 3.3 µF, is about 330 ms typical and about 475 ms at the long case used here. The prototype image does not edge GPIO1, so a board loaded with that image keeps the coils off.
- Cross-clamps so both relays cannot be driven together.
- Flyback diodes across the Finder coils only. A bidirectional SMBJ18CA across each contact pair. That clamp has no polarity and it does not join the contactor return to board ground.

The coil high side is the fused, polarity-protected coil branch, then the external switch, then the external ignition, then Q_SERIES. The low side is Q_UP or Q_DN. If the controller stops, resets, or loses 3.3 V, the requests fall, the monostable times out, and both coils release. A welded contact is not opened by any of this. The boat breaker is the clearing action.

## Chain counting

The Lofrans reed is not connected to a GPIO. It is clamped to its own 3.3 V rail and its own return with two BAT54W diodes, then read through an ISO7720FDR. The F suffix forces the logic outputs low when the field side has no power. A 10 kΩ series resistor and the 47 kΩ input resistor are the load on the Lofrans signal, on the order of 70 µA at 3.3 V.

A shunt selects that input or a dry contact with its own 4.7 kΩ pull-up. The pull-up is not on the Lofrans node. With the shunt off, the 47 kΩ holds the isolator input low. That is a level, not a pulse.

The field rail is a Murata MEJ2S0303SC, preloaded at about 65 mA so the published regulation applies. Murata’s own data gives 5.2 kV DC hipot for one second and 2.4 kV DC continuous functional isolation. That is not a safety barrier.

A power loss must not look like a chain pulse. The blanker is an SR latch of two 74LVC1G00 gates, not a monostable. Field-supply loss forces the GPIO low. Existing firmware counts a rising edge, so that falling edge is not a count. The latch lets the next rising edge through only after a real low on the reed data while the field rail is up. Until the first real pulse after power-up, the GPIO is held low. Firmware was not changed. Recovery during a real pulse can count that pulse once or miss it.

## Direction

Two TLP291 optocouplers. `UP_RET` and `DN_RET` are separate and are not board ground. There is no isolated supply on these inputs. The phototransistor is active low into a GPIO with a 10 kΩ pull-up.

R30 and R40 are fitted as 4.7 kΩ on an assumption that has not been measured: each field wire is a switched positive of about 5 V to 24 V, and the matching return is that circuit’s return. At 12 V the LED current is about 2.3 mA. At 24 V it is about 4.9 mA. The LED absolute maximum used here is 50 mA. If the boat wire is not a low-impedance switched positive, these two resistors have to change before the board is installed.

## NMEA 2000

ISO1042 on the logic 3.3 V, with its bus side on 5 V from a Murata MEJ2S0305SC. The 120 Ω on that module is a preload, about 42 mA, just over 10% of the 400 mA rating. It is not across CANH and CANL. The shield capacitor goes to `GND_CAN` only. Connector pin 5, NET-S, is not connected. The publish jumper is open, so the isolated supply stays off until the shunt is fitted. GPIO18 only reads the jumper, through 10 kΩ.

## Contacts and the Quick contactor

The likely contactor is a Quick T6315-12. The model, the coil resistance, and the inductive energy are not confirmed. Quick’s user manual states a 12 V coil and a recommended 2.5 A fast control fuse. It does not state the coil current. The motor ratings in that manual are the motor contact, which this board does not switch.

Finder’s DC1 rating used here is 10 A at 30 V DC, resistive. The DC13 inductive life equals that figure only when the load already has a diode. That diode is not assumed. The SMBJ18CA may absorb less energy than the contactor coil stores. Installation stays blocked until the measured current and the turn-off energy sit inside the Finder DC1 figure.

Contact tracks are 1.2 mm. IPC-2221 for an external 1 oz trace at a 10 °C rise gives about 1.07 mm for 2.5 A. The 1.2 mm width is that fuse as an upper bound, not a measured current. The 1 A coil fuse is sized for two Finder coils at 42 mA, only one of them on.

## Isolation

`REED_RET`, `UP_RET`, `DN_RET`, and `GND_CAN` are not joined to `GND` or to each other. Barrier nets have no through vias, so a via barrel cannot land on the ground plane. Slots are drawn between the isolator pin rows. Inner-layer keepouts cover each cluster of barrier pads so a through-hole ring is not poured against the ground plane. A slot by itself does not split a zone. The keepout does.

A clean clearance check would not make this a safety-isolated board. The Murata modules are functional isolation. The ISO7720 in this narrow package is the 3000 Vrms part, not the wide-body 5000 Vrms part. Creepage here is a layout gap, not an agency rating.

## Power input

One 12 V connector, split after the connector into an MCU fuse and a coil fuse. Each branch has an SMAJ18A and a P-FET. Reverse battery turns the FET off; the unidirectional TVS then conducts and the fuse opens. The AP63203 absolute maximum used here is 35 V DC, 40 V for 400 ms, with 32 V as the recommended maximum. The SMAJ18A clamp is about 29 V. This is not load-dump protection. Contactor current does not enter this connector. It flows through the dry contacts from the boat’s existing control feed.

## Validation

KiCad 10.0.8.

ERC, `kicad11/erc.rpt`, 10:08 Sydney time on 22 November 2026: 0 errors, 1 warning. The warning is intentional. U5 `GND1` sits on `REED_RET`.

DRC, `kicad11/drc.rpt`, after a zone refill at 10:58 Sydney time the same morning: 351 violations and 27 unconnected items. Four of the violations are shorts: `USB_VBUS` to `CC2`, `GND` to `USB_SHIELD`, `+3V3` to `NQ`, and `GND_CAN` to an unconnected pad of U10. There are also 11 clearance errors, 4 crossing tracks, and 180 dangling vias from escape vias the maze did not finish. The four extra footprints are the M3 mounting holes, which are not in the schematic.

The layout is placed and partly routed. It is not a finished board. The router in `scripts/build_board.py` does not yet keep fine-pitch escapes clear, and several isolated nets still have no complete path that stays on the top layer. Do not send this file to a manufacturer.

## Manufacturing readiness

Not ready. A clean DRC would still not be enough, and this DRC is not clean.

Still unmeasured, and still able to change a part or forbid installation:

- B1. The installed contactor, its coil current, the inrush, and the turn-off energy. The 2.5 A figure is a fuse recommendation.
- B2. Where the ignition permissive actually sits in the boat wiring.
- B3. A welded contact. This PCB cannot open one.
- B4. Lofrans reed source impedance, and whether its reference is battery negative.
- B5. The sense voltage and which conductor is the return. R30 and R40 depend on this.
- B6. Battery type, whether a load dump exists, and whether the enclosure is metal over the antenna.
- B7. The heartbeat edge on GPIO1 is not in the prototype image.
- B8. The NMEA drop, whether the bus is already terminated, and which device is allowed to publish.

Also unresolved: the SMBJ18CA energy against the real coil, the Finder contact life on an inductive load with no diode, and the MEJ2 pin-1 to body-end dimension against a Murata drawing. The KF350 courtyard is still the 4Ucon envelope.

The antenna keepout is on every copper layer over the module’s antenna end. Espressif’s 15 mm clearance to metal is not satisfied by that keepout if the case is metal. That remains B6.

## Files

- `kicad11/windlass.kicad_sch` and the seven sheets. Regenerated by `scripts/build_integrated.py`.
- `kicad11/windlass.kicad_pcb`. Placed and partly routed by `scripts/build_board.py`. Not for fabrication.
- `kicad11/erc.rpt`, `kicad11/drc.rpt`.
- `docs/integrated_bom.md`.
