# Fabrication readiness

23 November 2026, Sydney time. The board is `kicad11/windlass_install_v2.kicad_pcb`. The image is `firmware/s3`. No order was placed, nothing was flashed, and the prototype firmware and the Pi bridge were not modified.

## Checks

DRC on the v2 board: 0 violations, 0 unconnected pads, 0 footprint errors. ERC on `kicad11/windlass.kicad_sch`: 0 errors and 1 warning. The warning is U5 pin 4 `GND1` on `REED_RET`, which is the isolator's field ground and is intentional.

The schematic netlist and the board agree. 132 parts are on both. Values and footprint names match. Pad nets match, including U12 and U15: pad 2 is the request, pad 4 is the driver, pad 1 is the unconnected pin of the 74LVC1G34 and has no copper net. The four M3 holes are only on the board. KiCad prints an annotation warning while exporting; the placed reference designators in the netlist are the ones on the board.

Tracks are 0.2 mm and wider. Vias are 0.6 mm pads with 0.3 mm drills, so the annular ring is 0.15 mm. That is the absolute minimum JLCPCB publishes for a multilayer 1 oz via, and it is above the 0.127 mm track they publish as the standard minimum. It was not changed. Hole-to-copper on this board is checked at 0.25 mm, and that DRC is clean. The USB4105 locating holes are in the non-plated drill file at 0.65 mm.

The manufacturing files are `fab/jlcpcb`.

## Blockers

There is no fabrication blocker on this board. The files can be sent to JLCPCB as they are.

These are not fabrication blockers. They still have to be done before the windlass is asked to move:

- The Pi bridge has to be changed to `docs/pi_bridge_protocol.md`. This repository does not do that. The image built with the placeholder secrets will not open the radio.
- `WIFI_PASS` and `COMMAND_KEY` are chosen at compile time and are not in this repository.
- LCSC stock was not re-counted. The BOM leaves the LCSC column empty so an old C-number is not ordered by mistake. The Finder relays and both Murata modules are hand-fitted.
- The monostable pulse, the reed edge against the Lofrans magnet, and boat measurements B1, B2, B3, and B6 are still unmeasured. R30 and R40 stay 4.7 kΩ on the unmeasured sense voltage.
- NMEA certification is not claimed. The publish strap stays open while another 128777 source is on the backbone.

This package is not a marine installation approval.
