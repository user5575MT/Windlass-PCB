"""Preliminary placement boards. No copper routing. Not for fabrication.

Writes two KiCad boards:

- kicad/placement_finder.kicad_pcb
  Selected Finder 40.31.7.012.0000 relays, smallest outline that
  clears the ESP32 antenna courtyard, the two isolation modules,
  the connectors and the mounting holes.

- kicad/placement_compact_study.kicad_pcb
  Same architecture on an 80 x 60 mm outline, using the Omron G5Q
  courtyard as a size study only. That relay is not selected.
  Its published DC rating is resistive (L/R = 0).
"""

from __future__ import annotations

import math
import re
import uuid
from pathlib import Path

ROOT = Path(r"C:\Users\thoma\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints")
OUT = Path(r"C:\Users\thoma\Windlass-PCB\kicad")
LOCAL = OUT / "footprints.pretty"

FP = {
    "finder": ("Relay_THT", "Relay_SPDT_Finder_40.31"),
    "g5q": ("Relay_THT", "Relay_SPDT_Omron-G5Q-1"),
    "esp": ("RF_Module", "ESP32-S3-WROOM-1"),
    "mej": ("Converter_DCDC", "Converter_DCDC_muRata_MEJ1SxxxxSC_THT"),
    "hdr2": ("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical"),
    "hdr5": ("Connector_PinHeader_2.54mm", "PinHeader_1x05_P2.54mm_Vertical"),
    "m3": ("MountingHole", "MountingHole_3.2mm_M3"),
    "so16": ("Package_SO", "SOIC-16W_7.5x10.3mm_P1.27mm"),
    "so8": ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"),
    "tsot": ("Package_TO_SOT_SMD", "TSOT-23-6"),
    "sot223": ("Package_TO_SOT_SMD", "SOT-223-3_TabPin2"),
    "sma": ("Diode_SMD", "D_SMA"),
    "fuse": ("Fuse", "Fuse_1206_3216Metric"),
    "ind": ("Inductor_SMD", "L_Bourns-SRN4018"),
    "led": ("LED_SMD", "LED_RGB_1210"),
    "tb35": ("TerminalBlock_4Ucon", "TerminalBlock_4Ucon_1x02_P3.50mm_Horizontal"),
    "tb35x4": ("TerminalBlock_4Ucon", "TerminalBlock_4Ucon_1x04_P3.50mm_Horizontal"),
    "tb35x5": ("TerminalBlock_4Ucon", "TerminalBlock_4Ucon_1x05_P3.50mm_Horizontal"),
    "xh4": ("Connector_JST", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"),
    "xh5": ("Connector_JST", "JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical"),
    "hdr3": ("Connector_PinHeader_2.54mm", "PinHeader_1x03_P2.54mm_Vertical"),
    "usb": ("Connector_USB", "USB_C_Receptacle_HRO_TYPE-C-31-M-12"),
    "r0402": ("Resistor_SMD", "R_0402_1005Metric"),
    "r2512": ("Resistor_SMD", "R_2512_6332Metric"),
    "c0402": ("Capacitor_SMD", "C_0402_1005Metric"),
    "c0805": ("Capacitor_SMD", "C_0805_2012Metric"),
    "sod": ("Diode_SMD", "D_SOD-123"),
    "sot23": ("Package_TO_SOT_SMD", "SOT-23"),
    "sot236": ("Package_TO_SOT_SMD", "SOT-23-6"),
    "sot23_5": ("Package_TO_SOT_SMD", "SOT-23-5"),
    "sot353": ("Package_TO_SOT_SMD", "SOT-353_SC-70-5"),
    "sop4": ("Package_SO", "SOIC-4_4.55x2.6mm_P1.27mm"),
    "tssop8": ("Package_SO", "TSSOP-8_3x3mm_P0.65mm"),
    "led0603": ("LED_SMD", "LED_0603_1608Metric"),
    "sw": ("Button_Switch_SMD", "SW_SPST_TL3342"),
    "tp": ("TestPoint", "TestPoint_Pad_D1.5mm"),
}


LOCAL_FP = {
    "mej2": LOCAL / "Murata_MEJ2SxxxxSC.kicad_mod",
    "m3w": LOCAL / "MountingHole_M3_Washer.kicad_mod",
    "kf2": LOCAL / "KF350-3.5-1x02.kicad_mod",
    "kf4": LOCAL / "KF350-3.5-1x04.kicad_mod",
}


def uid() -> str:
    return str(uuid.uuid4())


def load_text(key: str) -> str:
    if key in LOCAL_FP:
        return LOCAL_FP[key].read_text(encoding="utf-8")
    lib, name = FP[key]
    return (ROOT / f"{lib}.pretty" / f"{name}.kicad_mod").read_text(encoding="utf-8")


def courtyard_rects(text: str) -> list[tuple[float, float, float, float]]:
    """Axis-aligned courtyard pieces in the footprint's local frame.

    The ESP32 footprint is a body rectangle plus a wider antenna wing.
    Returning both keeps the collision test from treating the whole
    48 mm bounding box as occupied beside the module body.
    """
    rects = []
    blocks = []
    for match in re.finditer(r"\(fp_(?:line|rect|circle|poly|arc)\b", text):
        depth = 0
        for i in range(match.start(), len(text)):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    blocks.append(text[match.start() : i + 1])
                    break
    pts = []
    circles = []
    for block in blocks:
        if "F.CrtYd" not in block:
            continue
        if block.startswith("(fp_circle"):
            c = re.search(r"\(center ([-\d.]+) ([-\d.]+)\)", block)
            e = re.search(r"\(end ([-\d.]+) ([-\d.]+)\)", block)
            if c and e:
                cx, cy = float(c.group(1)), float(c.group(2))
                ex, ey = float(e.group(1)), float(e.group(2))
                r = math.hypot(ex - cx, ey - cy)
                circles.append((cx - r, cy - r, cx + r, cy + r))
            continue
        for m in re.finditer(r"\((?:start|end|xy|center) ([-\d.]+) ([-\d.]+)\)", block):
            pts.append((float(m.group(1)), float(m.group(2))))
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        # Split a T-shaped courtyard (ESP32) into the wide antenna wing
        # and the narrower body. A single bounding box would forbid
        # parts that sit beside the shielded body.
        y_break = None
        # The wing is the band that reaches the extreme x.
        xmin, xmax = min(xs), max(xs)
        wide = [p for p in pts if abs(p[0] - xmin) < 0.2 or abs(p[0] - xmax) < 0.2]
        narrow = [p for p in pts if abs(p[0] - xmin) >= 0.2 and abs(p[0] - xmax) >= 0.2]
        if wide and narrow and (xmax - xmin) > (max(p[0] for p in narrow) - min(p[0] for p in narrow) + 5):
            wx = [p[0] for p in wide]
            wy = [p[1] for p in wide]
            nx = [p[0] for p in narrow]
            ny = [p[1] for p in narrow]
            # Wing is only the part beyond the body, so the two
            # rectangles meet at the body edge instead of overlapping.
            body_edge = min(ny) if min(wy) < min(ny) else max(ny)
            if min(wy) < min(ny):
                rects.append((min(wx), min(wy), max(wx), body_edge))
                rects.append((min(nx), body_edge, max(nx), max(ny)))
            else:
                rects.append((min(wx), body_edge, max(wx), max(wy)))
                rects.append((min(nx), min(ny), max(nx), body_edge))
        else:
            rects.append((min(xs), min(ys), max(xs), max(ys)))
    rects.extend(circles)
    return rects


def rot_point(x: float, y: float, deg: float) -> tuple[float, float]:
    """KiCad rotates footprint geometry clockwise."""
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (x * c + y * s, -x * s + y * c)


def place_rects(rects, x, y, deg):
    out = []
    for x0, y0, x1, y1 in rects:
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        moved = []
        for lx, ly in corners:
            rx, ry = rot_point(lx, ly, deg)
            moved.append((x + rx, y + ry))
        xs = [p[0] for p in moved]
        ys = [p[1] for p in moved]
        out.append((min(xs), min(ys), max(xs), max(ys)))
    return out


def overlaps(a, b, gap=0.05) -> bool:
    return not (a[2] <= b[0] + gap or b[2] <= a[0] + gap or a[3] <= b[1] + gap or b[3] <= a[1] + gap)


def embed(key: str, ref: str, value: str, x: float, y: float, deg: float) -> str:
    if key in LOCAL_FP:
        lib_name = f"windlass:{LOCAL_FP[key].stem}"
    else:
        lib, name = FP[key]
        lib_name = f"{lib}:{name}"
    text = load_text(key)
    text = re.sub(r'^\(footprint "[^"]+"', f'(footprint "{lib_name}"', text, count=1)
    text = text.replace(
        '(layer "F.Cu")',
        f'(layer "F.Cu")\n\t(uuid "{uid()}")\n\t(at {x:.3f} {y:.3f} {deg:.1f})',
        1,
    )
    text = text.replace('"REF**"', f'"{ref}"', 1)
    text = re.sub(r'(\(property "Value" )"[^"]+"', rf'\1"{value}"', text, count=1)
    text = re.sub(
        r'\(uuid "[0-9a-fA-F-]{36}"\)',
        lambda _m: f'(uuid "{uid()}")',
        text,
    )
    # Assembly identity stays on F.Fab. F.SilkS is reserved for the functional labels.
    marker = '(property "Reference"'
    start = text.find(marker)
    if start >= 0:
        nxt = text.find('(property ', start + len(marker))
        silk = text.find('(layer "F.SilkS")', start)
        if silk >= 0 and (nxt < 0 or silk < nxt):
            text = text[:silk] + '(layer "F.Fab")' + text[silk + len('(layer "F.SilkS")') :]
    return text


def rect_graphic(x0, y0, x1, y1, layer, width=0.15) -> str:
    return (
        f'\t(gr_rect\n'
        f'\t\t(start {x0:.3f} {y0:.3f})\n'
        f'\t\t(end {x1:.3f} {y1:.3f})\n'
        f'\t\t(stroke (width {width}) (type default))\n'
        f'\t\t(fill none)\n'
        f'\t\t(layer "{layer}")\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t)'
    )


def text_graphic(s, x, y, layer="Cmts.User", size=1.0, angle=0.0) -> str:
    safe = s.replace('"', "'")
    return (
        f'\t(gr_text "{safe}"\n'
        f'\t\t(at {x:.3f} {y:.3f} {angle:.1f})\n'
        f'\t\t(layer "{layer}")\n'
        f'\t\t(uuid "{uid()}")\n'
        f'\t\t(effects (font (size {size} {size}) (thickness 0.12)))\n'
        f'\t)'
    )


def edge(w, h) -> str:
    lines = []
    pts = [(0, 0), (w, 0), (w, h), (0, h)]
    for i in range(4):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 4]
        lines.append(
            f'\t(gr_line (start {x0:.3f} {y0:.3f}) (end {x1:.3f} {y1:.3f}) '
            f'(stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (uuid "{uid()}"))'
        )
    return "\n".join(lines)


HEADER_LAYERS = """\t(layers
\t\t(0 "F.Cu" signal "top_copper")
\t\t(4 "In1.Cu" signal)
\t\t(6 "In2.Cu" signal)
\t\t(2 "B.Cu" signal "bottom_copper")
\t\t(9 "F.Adhes" user "F.Adhesive")
\t\t(11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(17 "Dwgs.User" user "User.Drawings")
\t\t(19 "Cmts.User" user "User.Comments")
\t\t(21 "Eco1.User" user "User.Eco1")
\t\t(23 "Eco2.User" user "User.Eco2")
\t\t(25 "Edge.Cuts" user)
\t\t(27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user)
\t\t(33 "B.Fab" user)
\t)"""


def setup_4layer() -> str:
    return """\t(setup
\t\t(stackup
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "prepreg") (thickness 0.2104) (material "7628") (epsilon_r 4.4) (loss_tangent 0.02))
\t\t\t(layer "In1.Cu" (type "copper") (thickness 0.0152))
\t\t\t(layer "dielectric 2" (type "core") (thickness 1.065) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
\t\t\t(layer "In2.Cu" (type "copper") (thickness 0.0152))
\t\t\t(layer "dielectric 3" (type "prepreg") (thickness 0.2104) (material "7628") (epsilon_r 4.4) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(copper_finish "None")
\t\t\t(dielectric_constraints no)
\t\t)
\t\t(pad_to_mask_clearance 0.05)
\t\t(solder_mask_min_width 0.05)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(tenting front back)
\t)"""


def keepout_block(pts, flags) -> str:
    """One keep-out on every copper layer. pts is a list of (x, y)."""
    xy = " ".join(f"(xy {x:.3f} {y:.3f})" for x, y in pts)
    blocks = []
    for layer in ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu"):
        blocks.append(
            "\t(zone\n"
            "\t\t(net 0)\n"
            '\t\t(net_name "")\n'
            f'\t\t(layer "{layer}")\n'
            f'\t\t(uuid "{uid()}")\n'
            "\t\t(hatch full 0.508)\n"
            "\t\t(priority 1)\n"
            "\t\t(connect_pads (clearance 0))\n"
            "\t\t(min_thickness 0.2)\n"
            "\t\t(filled_areas_thickness no)\n"
            "\t\t(keepout\n"
            f"\t\t\t(tracks {flags[0]})\n"
            f"\t\t\t(vias {flags[1]})\n"
            f"\t\t\t(pads {flags[2]})\n"
            f"\t\t\t(copperpour {flags[3]})\n"
            f"\t\t\t(footprints {flags[4]})\n"
            "\t\t)\n"
            "\t\t(fill (thermal_gap 0.5) (thermal_bridge_width 0.5))\n"
            f"\t\t(polygon (pts {xy}))\n"
            "\t)"
        )
    return "\n".join(blocks)


def edge_poly(pts) -> str:
    lines = []
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        lines.append(
            f'\t(gr_line (start {x0:.3f} {y0:.3f}) (end {x1:.3f} {y1:.3f}) '
            f'(stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (uuid "{uid()}"))'
        )
    return "\n".join(lines)


def build(title, rev, comment, w, h, parts, zones, labels, keepouts=(), outline=None, allow_outside=None) -> tuple[str, list[str]]:
    cache = {k: courtyard_rects(load_text(k)) for k in {p[0] for p in parts}}
    placed = []
    problems = []
    bodies = []
    for key, ref, value, x, y, deg in parts:
        rects = place_rects(cache[key], x, y, deg)
        extra = (allow_outside or {}).get(ref, (0.0, 0.0, 0.0, 0.0))
        for rect in rects:
            if (
                rect[0] < -0.05 - extra[0]
                or rect[1] < -0.05 - extra[1]
                or rect[2] > w + 0.05 + extra[2]
                or rect[3] > h + 0.05 + extra[3]
            ):
                problems.append(
                    f"OFF BOARD {ref} {rect[0]:.2f},{rect[1]:.2f} .. {rect[2]:.2f},{rect[3]:.2f}"
                )
            for pref, prect in placed:
                if overlaps(rect, prect):
                    problems.append(
                        f"OVERLAP {ref} vs {pref}  "
                        f"({rect[0]:.1f},{rect[1]:.1f})-({rect[2]:.1f},{rect[3]:.1f}) vs "
                        f"({prect[0]:.1f},{prect[1]:.1f})-({prect[2]:.1f},{prect[3]:.1f})"
                    )
            placed.append((ref, rect))
        bodies.append(embed(key, ref, value, x, y, deg))
    graphics = [edge_poly(outline) if outline else edge(w, h)]
    for z in zones:
        graphics.append(rect_graphic(*z))
    for lab in labels:
        graphics.append(text_graphic(*lab))
    for pts, flags in keepouts:
        graphics.append(keepout_block(pts, flags))
    pcb = "\n".join(
        [
            "(kicad_pcb",
            "\t(version 20241229)",
            '\t(generator "windlass_place_preview")',
            "\t(generator_version \"0.2\")",
            "\t(general (thickness 1.6) (legacy_teardrops no))",
            '\t(paper "A4")',
            "\t(title_block",
            f'\t\t(title "{title}")',
            '\t\t(date "2026-11-19")',
            f'\t\t(rev "{rev}")',
            '\t\t(company "Windlass PCB — NOT FOR FABRICATION")',
            f'\t\t(comment 1 "{comment}")',
			'\t\t(comment 2 "No copper pours. GND plane is not filled. Do not manufacture.")',
            "\t)",
            HEADER_LAYERS,
            setup_4layer(),
            *graphics,
            *bodies,
            ")",
            "",
        ]
    )
    return pcb, problems


def finder_layout():
    """90 x 60 mm. Finder 40.31 courtyards, antenna wing on the top edge."""
    w, h = 90.0, 60.0
    parts = [
        ("esp", "U1", "ESP32-S3-WROOM-1-N16", 45.0, 32.25, 180),
        ("finder", "K_UP", "40.31.7.012.0000", 17.25, 7.6, 0),
        ("finder", "K_DN", "40.31.7.012.0000", 48.75, 7.6, 0),
        ("m3", "H1", "M3", 4.0, 4.0, 0),
        ("m3", "H2", "M3", 86.0, 4.0, 0),
        ("m3", "H3", "M3", 4.0, 56.0, 0),
        ("m3", "H4", "M3", 86.0, 56.0, 0),
        # MEJ1 footprint is the placement proxy for MEJ2 (same 19.5 x 9.8 mm SIP).
        ("mej", "U_REED", "MEJ2S0503SC", 8.4, 34.0, 270),
        ("mej", "U_CAN", "MEJ2S0505SC", 81.6, 34.0, 270),
        ("so8", "U_ISO", "ISO7721D", 16.2, 44.5, 0),
        ("so16", "U_CANISO", "ISO1042BDWR", 63.0, 25.5, 0),
        ("tsot", "U20", "AP63203WU-7", 22.0, 22.5, 0),
        ("tsot", "U21", "AP63205WU-7", 29.5, 22.5, 0),
        ("ind", "L20", "3.9uH", 21.0, 29.0, 0),
        ("ind", "L21", "4.7uH", 29.0, 29.0, 0),
        ("sma", "D_TVS", "SMAJ18A", 14.5, 22.5, 0),
        ("fuse", "F_MCU", "2A", 14.5, 28.5, 0),
        ("sot223", "Q_COIL", "DMP6023LE", 25.5, 35.2, 0),
        ("hdr2", "J_VIN", "12V_IN", 6.2, 10.2, 0),
        ("hdr2", "J_UP", "UP_CONTACT", 6.2, 17.4, 0),
        ("hdr2", "J_DN", "DN_CONTACT", 6.2, 24.6, 0),
        ("hdr2", "J_REED", "REED", 12.9, 2.5, 90),
        ("hdr2", "J_DRY", "DRY", 20.5, 2.5, 90),
        ("hdr2", "J_SW", "RELAY_POWER", 28.1, 2.5, 90),
        ("hdr2", "J_IGN", "IGNITION", 83.8, 26.5, 0),
        ("hdr5", "J_NMEA", "NMEA", 83.8, 10.2, 0),
        ("led", "D_LED", "RGB_STATUS", 36.0, 2.4, 0),
    ]
    zones = [
        # Antenna keep-out, all layers, copper-free. Drawn, not a pour.
        (21.0, 39.0, 69.0, 60.0, "Dwgs.User", 0.2),
        # Reed barrier. Primary side is toward the module.
        (1.2, 33.5, 20.5, 54.5, "Eco1.User", 0.2),
        # CAN barrier. Kept off the relay and coil area.
        (74.0, 33.5, 88.8, 54.5, "Eco1.User", 0.2),
    ]
    labels = [
        ("ANTENNA EDGE  —  copper-free keep-out, all layers", 45, 57.5, "Cmts.User", 0.9),
        ("REED ISOLATION", 8, 53.5, "Cmts.User", 0.7),
        ("CAN ISOLATION", 82, 53.5, "Cmts.User", 0.7),
        ("POWER", 26, 37.5, "Cmts.User", 0.8),
        ("90 x 60 mm  four-layer  NOT FOR FABRICATION", 45, 1.2, "Cmts.User", 0.9),
        ("Finder 40.31  hand-fitted", 45, 16.5, "Cmts.User", 0.7),
    ]
    return build(
        "Windlass placement A — Finder 40.31",
        "0.2-placement-not-for-fabrication",
        "90 x 60 mm. Selected relays. Placement study, not a routed board.",
        w, h, parts, zones, labels,
    )


def pack_parts(fixed, small, w, h, blocked):
    """Place small parts in the first free cell. Returns parts and any refs that did not fit."""
    keys = {p[0] for p in fixed} | {p[0] for p in small}
    cache = {k: courtyard_rects(load_text(k)) for k in keys}
    occupied = [tuple(b) for b in blocked]
    for key, _ref, _value, x, y, deg in fixed:
        occupied.extend(place_rects(cache[key], x, y, deg))
    placed = list(fixed)
    missed = []
    def search(key, step):
        for deg in (0, 90):
            y = 0.8
            while y < h:
                x = 0.8
                while x < w:
                    rects = place_rects(cache[key], x, y, deg)
                    if rects and all(
                        r[0] >= 0.35 and r[1] >= 0.35 and r[2] <= w - 0.35 and r[3] <= h - 0.35
                        and all(not overlaps(r, occ, -0.2) for occ in occupied)
                        for r in rects
                    ):
                        return (x, y, deg, rects)
                    x += step
                y += step
        return None

    for key, ref, value in small:
        found = search(key, 0.7)
        if found is None:
            found = search(key, 0.35)
        if found is None:
            missed.append(ref)
        else:
            placed.append((key, ref, value, found[0], found[1], found[2]))
            occupied.extend(found[3])
    return placed, missed


def finder_80():
    """Connectors fit in 80 x 60. Passives need one added strip."""
    dy = 9.0
    w, h = 80.0, 60.0 + dy
    fixed = [
        ("esp", "U3", "ESP32-S3-WROOM-1-N16", 40.0, 32.25, 180),
        ("finder", "K_UP", "40.31.7.012.0000", 12.25, 7.1, 0),
        ("finder", "K_DN", "40.31.7.012.0000", 43.75, 7.1, 0),
        ("m3w", "H1", "M3+washer", 4.0, 4.0, 0),
        ("m3w", "H2", "M3+washer", 76.0, 4.0, 0),
        ("m3w", "H3", "M3+washer", 4.0, 56.0, 0),
        ("m3w", "H4", "M3+washer", 76.0, 56.0, 0),
        ("mej2", "U4", "MEJ2S0503SC", 12.2, 28.0, 0),
        ("mej2", "U9", "MEJ2S0505SC", 53.2, 33.7, 0),
        ("so8", "U5", "ISO7721DR", 16.5, 36.0, 0),
        ("so16", "U10", "ISO1042BDWR", 62.0, 22.9, 0),
        ("sot223", "Q_MCU", "DMP6023LE-13", 12.2, 45.0, 90),
        ("sot223", "Q_COIL", "DMP6023LE-13", 68.4, 45.0, 90),
        ("kf2", "J_PWR", "KF350-3.5-2P", 4.3, 14.1, 90),
        ("kf4", "J_CONTACT", "KF350-3.5-4P", 4.3, 30.2, 90),
        ("kf4", "J_PERM", "KF350-3.5-4P", 4.3, 46.3, 90),
        ("xh4", "J_REED", "B4B-XH-A", 76.75, 8.45, 270),
        ("xh5", "J_SENSE", "B5B-XH-A", 76.75, 22.25, 270),
        ("xh5", "J_NMEA", "B5B-XH-A", 76.75, 38.55, 270),
        ("usb", "J_USB", "USB-C", 40.0, 0.2, 0),
        ("sot236", "U_ESD", "USBLC6-2SC6", 40.0, 7.6, 0),
        ("led0603", "D_R", "LTST-C190KRKT", 21.4, 6.8, 0),
        ("led0603", "D_G", "LTST-C190KGKT", 24.8, 6.8, 0),
        ("led0603", "D_B", "LTST-C190TBKT", 28.2, 6.8, 0),
        ("sod", "D_Z_MCU", "BZT52C12", 11.2, 6.8, 0),
        ("sod", "D_Z_COIL", "BZT52C12", 33.8, 6.8, 0),
    ]
    small = [
        ("tsot", "U20", "AP63203WU-7"),
        ("tsot", "U21", "AP63205WU-7"),
        ("ind", "L20", "3.9uH"),
        ("ind", "L21", "4.7uH"),
        ("sma", "D_TVS_MCU", "SMAJ18A"),
        ("sma", "D_TVS_COIL", "SMAJ18A"),
        ("sma", "D60", "SS14"),
        ("sma", "D70", "SS14"),
        ("fuse", "F_MCU", "0466002"),
        ("fuse", "F_5V", "2A"),
        ("fuse", "F_COIL", "0466001"),
        ("sop4", "U6", "TLP291-GB"),
        ("sop4", "U7", "TLP291-GB"),
        ("sot353", "U8", "74LVC1G86GW"),
        ("tssop8", "U11", "74LVC1G123DP"),
        ("sot353", "U12", "74LVC1G08GW"),
        ("sot23", "Q_UP", "NX6008NBK"),
        ("sot23", "Q_DN", "NX6008NBK"),
        ("sot23", "Q_SERIES", "NX6008NBK"),
        ("sot23", "Q_CLAMP_UP", "2N7002"),
        ("sot23", "Q_CLAMP_DN", "2N7002"),
        ("sot23", "Q90", "2N7002"),
        ("sot23", "Q91", "DMP3099L"),
        ("sot23", "Q_LED", "2N7002BK"),
        ("sw", "SW_RST", "TL3342"),
        ("sw", "SW_BOOT", "TL3342"),
        ("hdr3", "JP_REED", "REED_MODE"),
        ("hdr2", "JP1", "PUBLISH"),
        ("tp", "TP_TX", "TX"),
        ("tp", "TP_RX", "RX"),
        ("tp", "TP_WDI", "WDI"),
        ("tp", "TP_VBUS", "VBUS"),
        ("r2512", "R24", "51R"),
        ("r2512", "R94", "120R"),
        ("c0805", "C10", "1uF"),
        ("c0805", "C11", "10uF"),
        ("c0805", "C50", "3.3uF"),
        ("c0805", "C30I", "10uF"),
        ("c0805", "C30A", "22uF"),
        ("c0805", "C30C", "22uF"),
        ("c0805", "C40I", "10uF"),
        ("c0805", "C40A", "22uF"),
        ("c0805", "C40C", "22uF"),
    ]
    for ref in (
        "R_MCU_G", "R_COIL_G", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19",
        "R20", "R22", "R23", "R30", "R30P", "R40", "R40P", "R50", "R51", "R52", "R53",
        "R60", "R61", "R70", "R71", "R80", "R81", "R82", "R90", "R91", "R92", "R93",
        "R_R", "R_G", "R_B", "R_RPD", "R_GPD", "R_BPD",
        "R_SWLINK", "R_IGNLINK", "R_COILFEED",
        "C12", "C13", "C20", "C21", "C22", "C24", "C30", "C40", "C51", "C90", "C91", "C92", "C93",
        "C30B", "C40B",
    ):
        small.append(("r0402" if ref.startswith("R") else "c0402", ref, ref))
    for ref in ("D20", "D21", "D30", "D40", "D80"):
        small.append(("sod", ref, ref))
    # Keep the USB shell on the bottom edge and the two bottom holes
    # in the corners. Everything else moves up with the extra strip.
    stay = {"J_USB", "H1", "H2", "U_ESD", "D_R", "D_G", "D_B", "D_Z_MCU", "D_Z_COIL"}
    fixed = [
        (key, ref, value, x, y if ref in stay else y + dy, deg)
        for key, ref, value, x, y, deg in fixed
    ]
    blocked = [
        (18.0, 40.0 + dy, 62.0, h),
        (28.0, 46.0 + dy, 52.0, h),
    ]
    parts, missed = pack_parts(fixed, small, w, h, blocked)
    if missed:
        print("  UNPLACED", ", ".join(missed))
    by_ref = {ref: (x, y, deg) for _key, ref, _value, x, y, deg in parts}
    labels_extra = []

    def silk_at(ref, lx, ly, text, layer="F.SilkS", angle=0.0):
        x, y, deg = by_ref[ref]
        rx, ry = rot_point(lx, ly, deg)
        labels_extra.append((text, x + rx, y + ry, layer, 0.8, angle))

    # Pin 1 is local y=0. The two mode lines sit past pin 1. ONE SHUNT sits past pin 3,
    # away from the K_DN body silk that the old pin-1-end line crossed.
    silk_at("JP_REED", 0.0, -4.0, "1-2 LOFRANS")
    silk_at("JP_REED", 0.0, -5.1, "2-3 DRY")
    silk_at("JP_REED", -10.2, -4.0, "1 SHUNT", layer="Cmts.User")
    # Short vertical text. The 3.5 mm pin pitch does not fit a longer word,
    # and local +Y is board +X at rotation 90.
    silk_at("J_PWR", -1.8, 4.5, "+12", angle=90)
    silk_at("J_PWR", 3.5, 4.5, "GND", angle=90)
    silk_at("J_CONTACT", 0.0, 4.9, "U-C", angle=90)
    silk_at("J_CONTACT", 3.5, 4.9, "U-N", angle=90)
    silk_at("J_CONTACT", 7.0, 4.9, "D-C", angle=90)
    silk_at("J_CONTACT", 8.8, 4.9, "D-N", layer="Cmts.User", angle=90)
    silk_at("K_UP", 12.0, 4.0, "UP")
    silk_at("K_DN", 12.0, 4.0, "DN")
    silk_at("D_R", 0.0, -2.2, "FAULT", layer="Cmts.User")
    silk_at("D_G", 0.0, -2.2, "READY", layer="Cmts.User")
    silk_at("D_B", 0.0, -2.2, "PAIR", layer="Cmts.User")
    zones = [
        (18.0, 42.0 + dy, 62.0, 46.0 + dy, "Dwgs.User", 0.15),
        (16.2, 24.2 + dy, 21.2, 31.8 + dy, "Eco1.User", 0.12),
        (57.0, 29.8 + dy, 62.2, 37.6 + dy, "Eco1.User", 0.12),
    ]
    # Pads and pours stay out of the antenna zone and out of each MEJ2 pin gap.
    # The module footprint is allowed because its courtyard includes the antenna.
    no_cu = ("not_allowed", "not_allowed", "not_allowed", "not_allowed", "allowed")
    barrier = ("not_allowed", "not_allowed", "not_allowed", "not_allowed", "allowed")
    keepouts = [
        ([(18.0, 42.0 + dy), (62.0, 42.0 + dy), (62.0, h - 0.5), (18.0, h - 0.5)], no_cu),
        ([(16.2, 24.2 + dy), (21.2, 24.2 + dy), (21.2, 31.8 + dy), (16.2, 31.8 + dy)], barrier),
        ([(57.0, 29.8 + dy), (62.2, 29.8 + dy), (62.2, 37.6 + dy), (57.0, 37.6 + dy)], barrier),
    ]
    labels = [
        ("ANTENNA NOTCH", 40, 52.0 + dy, "Cmts.User", 0.7),
        ("REED BARRIER", 18.5, 28.4 + dy, "Cmts.User", 0.45),
        ("CAN BARRIER", 59.5, 34.2 + dy, "Cmts.User", 0.45),
        (f"{w:.0f} x {h:.0f}  NOT FOR FABRICATION", 40, 2.2, "Cmts.User", 0.6),
        *labels_extra,
    ]
    outline = [
        (0, 0), (w, 0), (w, h), (52, h), (52, 46 + dy), (28, 46 + dy), (28, h), (0, h),
    ]
    return build(
        f"Windlass placement — {w:.0f} x {h:.0f} rev 0.8",
        "0.8-placement-not-for-fabrication",
        "JLC04161H-7628 stackup. Contact route plus a partial signal route. No fabrication outputs.",
        w, h, parts, zones, labels, keepouts, outline, {"J_USB": (0.0, 6.0, 0.0, 0.0)},
    )


def compact_study():
    """80 x 60 mm geometric study. G5Q courtyard is not a selected part."""
    w, h = 80.0, 60.0
    parts = [
        ("esp", "U1", "ESP32-S3-WROOM-1-N16", 40.0, 32.25, 180),
        ("g5q", "K_UP", "G5Q-SIZE-STUDY-NOT-SELECTED", 13.95, 15.85, 0),
        ("g5q", "K_DN", "G5Q-SIZE-STUDY-NOT-SELECTED", 41.95, 15.85, 0),
        ("m3", "H1", "M3", 3.8, 3.8, 0),
        ("m3", "H2", "M3", 76.2, 3.8, 0),
        ("m3", "H3", "M3", 3.8, 56.2, 0),
        ("m3", "H4", "M3", 76.2, 56.2, 0),
        ("mej", "U_REED", "MEJ2S0503SC", 8.2, 34.2, 270),
        ("mej", "U_CAN", "MEJ2S0505SC", 76.1, 34.2, 270),
        ("so8", "U_ISO", "ISO7721D", 15.5, 34.5, 0),
        ("so16", "U_CANISO", "ISO1042BDWR", 58.5, 25.5, 0),
        ("tsot", "U20", "AP63203WU-7", 20.0, 21.5, 0),
        ("tsot", "U21", "AP63205WU-7", 26.5, 21.5, 0),
        ("ind", "L20", "3.9uH", 19.0, 27.5, 0),
        ("ind", "L21", "4.7uH", 26.0, 27.5, 0),
        ("sma", "D_TVS", "SMAJ18A", 13.0, 21.8, 0),
        ("fuse", "F_MCU", "2A", 13.0, 27.0, 0),
        ("sot223", "Q_COIL", "DMP6023LE", 58.0, 35.2, 0),
        ("hdr2", "J_VIN", "12V_IN", 5.6, 11.0, 0),
        ("hdr2", "J_UP", "UP_CONTACT", 5.6, 18.2, 0),
        ("hdr2", "J_DN", "DN_CONTACT", 5.6, 25.4, 0),
        ("hdr2", "J_REED", "REED", 14.0, 2.4, 90),
        ("hdr2", "J_DRY", "DRY", 22.0, 2.4, 90),
        ("hdr2", "J_SW", "RELAY_POWER", 30.0, 2.4, 90),
        ("hdr2", "J_IGN", "IGNITION", 74.2, 26.2, 0),
        ("hdr5", "J_NMEA", "NMEA", 74.2, 10.5, 0),
        ("led", "D_LED", "RGB_STATUS", 40.0, 2.5, 0),
    ]
    zones = [
        (16.0, 39.0, 64.0, 60.0, "Dwgs.User", 0.2),
        (1.2, 32.5, 14.0, 55.5, "Eco1.User", 0.2),
        (66.0, 32.5, 78.8, 55.5, "Eco1.User", 0.2),
    ]
    labels = [
        ("ANTENNA EDGE  —  copper-free keep-out", 40, 57.5, "Cmts.User", 0.8),
        ("SIZE STUDY ONLY", 40, 10.5, "Cmts.User", 1.0),
        ("G5Q courtyard is not the selected relay", 40, 8.8, "Cmts.User", 0.7),
        ("80 x 60 mm  NOT FOR FABRICATION", 40, 1.2, "Cmts.User", 0.8),
        ("REED", 8, 54.2, "Cmts.User", 0.6),
        ("CAN", 72, 54.2, "Cmts.User", 0.6),
    ]
    return build(
        "Windlass placement B — 80x60 size study",
        "0.2-size-study-not-selected",
        "80 x 60 mm geometric study. G5Q DC rating is resistive. Not selected.",
        w, h, parts, zones, labels,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (
        ("placement_finder.kicad_pcb", finder_80),
        ("placement_finder_90x60.kicad_pcb", finder_layout),
        ("placement_compact_study.kicad_pcb", compact_study),
    ):
        pcb, problems = fn()
        path = OUT / name
        path.write_text(pcb, encoding="utf-8")
        print(f"\n== {name}  {path.stat().st_size} bytes")
        if problems:
            print(f"  {len(problems)} placement problems")
            for p in problems:
                print("  ", p)
        else:
            print("  courtyard rectangles clear and on the board")


if __name__ == "__main__":
    main()
