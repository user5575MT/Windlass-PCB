# Design simplification

19 November 2026 review of the revision 0.8 schematic and the routing record in `docs/progress_log.md`. No schematic was regenerated for that review. No copper was added then. No board was ordered. The prototype firmware was not modified.

The review below recommended a separate relay board. That recommendation stands as the record of the review. The build that followed it is the single integrated board in `kicad11/`, because the controller is required to carry both relays on the same PCB. See `docs/integrated_design.md`.

Routing of the 80 × 69 mm four-layer board should stop. The placement is the wrong shape for the circuit that was drawn, and the circuit is larger than the job requires before the boat measurements exist.

## Recommendation

Build a two-layer controller that counts chain, senses direction, serves Wi-Fi, and can publish isolated NMEA 2000. Do not put relay contacts on that board.

Add a second, optional board for the UP and DOWN contacts only after measurement B1 says what those contacts actually switch. Until that board exists, this controller cannot energise the windlass. That is the fail-safe state.

Discard the 80 × 69 mm placement and its tracks. Keep the net rules and the safety outcomes. Do not keep the part count.

## Why the current board is the wrong thing to finish

Revision 0.8 DRC, after the best kept route, was 208 unconnected items and no shorts. The board was still trying to carry all of the following at once:

- Five grounds that must not touch: `GND`, `REED_RET`, `UP_RET`, `DN_RET`, `GND_CAN`.
- Two isolated DC-DC modules (MEJ2S0503 and MEJ2S0505) and two isolators (ISO7721 and ISO1042).
- Two Finder 40.31 relays, hand-fitted, sized for an unmeasured load and drawn at 0.80 mm for a provisional 2 A.
- A heartbeat monostable, an XOR, an AND, three coil FETs, and two cross-clamp FETs.
- Two bucks, two ideal-diode FETs, two TVS diodes, and a mid-mount USB-C whose library footprint has already fought the outline.

The XOR and the AND repeat the cross-clamps. Both request pins high already clamps both coil gates off. The 5 V buck exists to feed the isolated modules and one LED. The reed’s isolated 3.3 V rail is what creates the false chain pulse: if that rail collapses while the reed is active and a direction sense is already on, the ISO7721 without the F suffix drives its output high, and the existing firmware can count the rising edge. Removing that rail removes the failure. Adding another isolator to detect it does not.

The only price this file is willing to repeat is the one already written down: DigiKey listed Murata MEJ2S0505SC at about $15.39, hand-fitted, functional isolation only. There is still no assembly quotation and no two-board total. A new total is not invented here.

## What is essential

| Function | Keep | Reason |
| --- | --- | --- |
| ESP32-S3-WROOM-1-N16, no PSRAM | Yes | Wi-Fi, native TWAI, 85 °C. Octal-PSRAM parts lose pins and temperature. |
| Chain input that does not load the Lofrans reed | Yes, but not on the first population | The PC817 input pulled idle from 3.22 V to 1.5 V. The first boards should count a dry contact on this board’s own 3.3 V. The Lofrans wire stays on the connector, unpopulated, until B4. |
| Two direction senses with separate returns | Yes | Joining IN2 and IN3 grounds already caused a fault. Two optocouplers are the smallest circuit that preserves that split. |
| Parallel normally-open UP and DOWN contacts | Yes, on a later board | Bench-tested in parallel. This board must not sit in series with the Lofrans remote or the hand remote. |
| Ignition and relay-power switch in the coil current | Yes, as wires through the relay board | Software cannot bypass a contact that is in series with the coil. |
| Hardware drop of coil power if the CPU stops | Yes, on the relay board | The 300 ms software TTL does not run if the CPU is halted. The monostable covers that. It is not redundant. |
| One direction at a time | Yes, the cross-clamps | Already drawn. The XOR and the AND are the redundant copy. |
| Isolated NMEA, no terminator, NET-S open, publish off by default | Yes | One isolated transceiver. Not a second DC-DC module, a preload resistor, and two extra FETs. |
| Antenna keep-out and a non-metal clearance around it | Yes | Espressif’s rule. Enclosure material is still B6. |

## What to drop from the first build

| Present part | Verdict |
| --- | --- |
| 74LVC1G86 and 74LVC1G08 | Drop. The 2N7002 cross-clamps already block both-on. |
| MEJ2S0503 and ISO7721 as fitted parts | Do not fit until B4. A dry-contact pull-up on the same 3.3 V as the ESP32 cannot outlive the CPU, so a supply collapse cannot create a stored edge. |
| MEJ2S0505, R94 preload, Q90, Q91 | Replace with one isolated CAN transceiver that includes its power, chosen from a datasheet at order time. Publish enable becomes a jumper, open by default, read by a pulldown. |
| AP63205 5 V buck and F_5V | Drop if the CAN device and the LEDs run from 3.3 V. |
| Second ideal-diode FET and second TVS on the coil branch | Drop from the controller. The relay board gets a fuse in the coil feed. The SMAJ18A remains a short-pulse clamp, not load-dump protection, and only if B6 says the feed can see a load dump. |
| Finder 40.31 and 0.80 mm contact copper | Do not place until B1. If B1 shows a logic-level input into the Lofrans box, these relays are the wrong part. |
| Mid-mount USB-C `TYPE-C-31-M-12` | Do not reuse this footprint. Its pads and the board edge have already conflicted. A service header, or a USB-C whose drawing puts every pad on the board, is enough for bring-up. |
| Four-layer 80 × 69 mm outline and every track on it | Discard. R14’s four-layer requirement was a layout choice, not a safety requirement. |
| Reed power-good isolator | Do not add. The failure mode belongs to the isolated reed supply. Leave that supply off the first build. |

## Three architectures

### 1. Finish the current board

One 80 × 69 mm, four-layer board, five grounds, two isolated modules, two relays, the full interlock.

Routing has already failed with hundreds of unconnected items and, on a discarded pass, with shorts between domains. The safety circuit is more complicated than the measurements support. Assembly needs hand-fitted relays and at least one Murata module. This is the largest board to test, because a coil fault and a radio fault live on the same card.

Do not continue it.

### 2. One larger two-layer board, reduced circuit

Same connectors and the same safety outcomes, on a board big enough to route by hand. One 3.3 V buck. Dry-contact reed fitted, Lofrans isolator as a footprint only. Two optocouplers. One isolated CAN device at the edge, with its own ground island and no terminator. Relays, monostable, and cross-clamps on the same board only if B1 is already in hand; otherwise the relay footprints stay off the sheet.

One assembly, one enclosure, easier than the current board. The contact copper is still next to the antenna and the isolator if the relays are included before their current is known. That is the remaining reason not to choose this as the first article.

### 3. Controller now, relay board after B1

Board 1, two-layer, no relays: ESP32-S3, one protected 12 V to 3.3 V buck, dry-contact reed, two optocouplers with separate returns, Wi-Fi at the edge, service connector, one isolated CAN transceiver, publish jumper open. Board 1 has one ground, plus the two opto returns and the CAN ground island.

Board 2, only after B1, B2, and B3: two contacts rated for the measured load, coil feed through the existing ignition and relay-power switch, 74LVC1G123, two cross-clamp FETs, one series FET, two low-side FETs, flyback across each coil and not across the Lofrans load. Unplugging board 2 leaves the Lofrans controller and the hand remote as they are.

Board 1 can be bench-tested and taken to the boat with the windlass breaker open. It cannot run the motor. Board 2 is small, replaceable, and is the only place a contact weld can occur.

This is the architecture to draw next.

## Reed, direction, interlock, CAN

**Reed.** First population is a dry contact, 3.3 V pull-up on the contact side of the jumper only, input to the ESP32. Power loss and power return happen on the same rail as the CPU, and the existing firmware already ignores the sample it takes at start. The Lofrans pair of wires is a separate connector position with no fitted resistor to that node. After B4, if the Lofrans reference is not battery negative, fit the ISO7721 and its supply as a stuffing option. If B4 shows the reference is battery negative and a stated resistor does not sag the idle voltage, a divider may replace the isolator. Neither of those is drawn until the numbers exist.

**Direction.** Keep two TLP291 channels and two returns. A resistor divider is simpler and is not allowed until B5 shows that each sense line is a battery-referenced voltage rather than a floating loop. `R30` and `R40` stay unchosen until that voltage and the Lofrans driver rating are known.

**Interlock.** On the relay board, keep the series FET, the monostable, the gate pulldowns, and the cross-clamps. Delete the XOR and the AND. Both high still clamps both gates. Heartbeat expiry still opens the series FET. Reset still pulls the gates down. The ignition switch and the relay-power switch stay in the coil wire. A welded contact is still not opened; B3 decides the operator rule, which is to pull the windlass breaker. No extra sensor is added for that.

**CAN.** One isolated transceiver, side-2 ground not joined to `GND` or to either opto return, no 120 Ω on CANH/CANL, NET-S not connected, shield capacitor to the CAN ground only. The publish jumper is open in the default build so the bus-side supply is off. The Waveshare transmitter stays the only publisher until B8 says otherwise.

## Availability, cost, assembly, area

Stock figures below are the ones already recorded on 19 November 2026. They are not a new lookup and not a quotation.

| Item | Recorded state | First build |
| --- | --- | --- |
| ESP32-S3-WROOM-1-N16 | LCSC snapshot, extended assembly | Fit |
| AP63203 3.3 V buck | Extended, stock was thin on one page | Fit. Recheck at order |
| TLP291 | A real Toshiba reel was found after an empty listing | Fit both channels |
| ISO1042 plus MEJ2S0505 | ISO1042 stock was a snapshot. MEJ2 about $15.39 at DigiKey, hand-fit, not a safety barrier | Do not fit this pair. Choose one integrated isolated CAN part when the schematic is redrawn |
| MEJ2S0503 | LCSC showed 3 pieces | Do not fit |
| Finder 40.31 | Hand-fit. Contact rating is not the Lofrans load | Do not fit |
| USB-C HRO mid-mount | In stock. Footprint and outline already conflicted | Do not reuse the footprint |
| 74LVC1G123 | In distribution | Relay board only |
| 74LVC1G86, 74LVC1G08 | In distribution | Do not fit |

Board 1 should be a two-layer prototype, one side of SMD, through-hole connectors, no hand-fitted module if the CAN part is a single SOIC. Area is whatever the antenna keep-out, the CAN island, and the connectors need. A 100 mm board is acceptable. The old 80 × 69 mm limit was a packing target, not a requirement.

Board 2 is a few relays and a handful of SOT-23 parts. Its size follows the relay chosen from B1. If that current is only the Finder coil’s 42 mA into a remote input, board 2 can be two small signal relays. If B1 shows a contactor current, board 2 uses a relay whose DC inductive rating covers the measurement, and the track width is calculated from that current rather than from 2 A or from 10 A.

Verification of board 1, actuator disconnected: ERC, then a boat check that the Lofrans idle voltage does not move with our reed wires disconnected, that each opto follows the existing remote, and that CANH/CANL are silent with the jumper open. Verification of board 2 is a separate bench with a resistive or measured load, then a parallel wiring check against B1 before it is allowed near the contactor.

## Measurements still required

These are unchanged from `docs/assumptions_and_open_questions.md`. None of them is answered by another PCB revision.

| ID | Needed before | What it decides |
| --- | --- | --- |
| B1 | Any relay copper | Contact type, current, inrush, freewheel, backfeed into the hand remote |
| B2 | Relay-board wiring | Where the ignition permissive actually is |
| B3 | Installing contacts | Weld behaviour. This hardware still cannot open a welded contact |
| B4 | Fitting the Lofrans reed input | Source impedance, reference conductor, whether it is battery negative |
| B5 | Replacing the optocouplers, and the series resistors | Sense voltage, which ground, whether the sense wires are the command wires |
| B6 | Fuse, TVS, enclosure | Which battery, load dump, metal near the antenna |
| B7 | The relay-board firmware image | GPIO1 must be edged by a new image. The 300 ms TTL stays. The prototype image is not edited |
| B8 | Fitting the publish jumper | Whether a backbone exists, whether it is already terminated, and whether the Waveshare transmitter is removed |

## What the next drawing should contain

Retain from the present schematic, as requirements rather than as a copy of the sheet:

- ESP32-S3-WROOM-1-N16 pin map, straps, and antenna keep-out.
- Parallel NO contacts, commons not tied on the PCB, absent from board 1.
- `UP_RET` not joined to `DN_RET` or to `GND`.
- Coil current through an external switch and an ignition contact, then a series FET that needs a fresh heartbeat and exactly one request.
- No 120 Ω between CANH and CANL. NET-S unconnected. Publish off unless the jumper is fitted.
- Chain length left in firmware calibration, default 0.36 m per pulse.
- The prototype image, the 300 ms TTL, authentication, and CAN retransmission left untouched.

Redraw as a new, smaller schematic. Do not route the old board while that schematic is open.

## Implementation order

1. Take B1, B4, and B5 on the boat with the windlass breaker open. B1 is a current measurement. B4 is a voltage and a sag measurement. B5 is which wire moves, relative to which conductor.
2. Draw board 1 only. Dry-contact reed, two optocouplers, one buck, one isolated CAN device, publish jumper open, no relays, no monostable.
3. Review that schematic against this note and against H8, H9, H10, and H11. H11 stays a residual: this PCB still cannot stop the existing remote.
4. Lay out board 1 on two layers, by hand, with the CAN ground confined to one edge. Run ERC and DRC before any relay work.
5. Bench-test board 1 with the actuator disconnected. Confirm the Lofrans reed is not connected to a fitted pull-up.
6. When B1, B2, and B3 are written down, draw board 2 from those numbers. Choose the relay then. Do not reuse the Finder footprint unless the measured current fits its DC rating and the inductive case is stated.
7. Do not generate fabrication files for either board until that board’s ERC and DRC are clean and the measurements it depends on are filled in.
