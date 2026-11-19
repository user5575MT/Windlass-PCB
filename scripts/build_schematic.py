#!/usr/bin/env python3
"""Generate the Windlass hierarchical KiCad schematic.

Values marked OPEN are not fabrication values. They are drawn so the
topology can be reviewed and so ERC can run. See docs/circuit_calculations.md.
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path

LIBROOT = Path(r"C:\Users\thoma\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols")
OUT = Path(r"C:\Users\thoma\Windlass-PCB\kicad")
PROJECT = "windlass"
VERSION = "20260306"
ROOT_UUID = "4c1a6e2e-7b0d-4f4a-9a11-0c5d8e2a11a0"

# sheet name -> uuid (also the hierarchical sheet uuid on the root)
SHEET_IDS = {
    "power": "a11aaaaa-1111-4111-8111-111111111101",
    "esp32": "a11aaaaa-1111-4111-8111-111111111102",
    "reed": "a11aaaaa-1111-4111-8111-111111111103",
    "direction_sense": "a11aaaaa-1111-4111-8111-111111111104",
    "relay_control_and_interlock": "a11aaaaa-1111-4111-8111-111111111105",
    "isolated_nmea2000": "a11aaaaa-1111-4111-8111-111111111106",
    "connectors_status_service": "a11aaaaa-1111-4111-8111-111111111107",
}


def uid() -> str:
    return str(uuid.uuid4())


class Quoted(str):
    """A string that was quoted in the library file and must stay quoted."""


def parse(text: str):
    tokens = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c in "()":
            tokens.append(c)
            i += 1
            continue
        if c == '"':
            i += 1
            buf = []
            while i < n:
                if text[i] == "\\":
                    buf.append(text[i + 1])
                    i += 2
                    continue
                if text[i] == '"':
                    i += 1
                    break
                buf.append(text[i])
                i += 1
            tokens.append(Quoted("".join(buf)))
            continue
        j = i
        while i < n and not text[i].isspace() and text[i] not in "()":
            i += 1
        tokens.append(text[j:i])

    def read(k):
        if tokens[k] != "(":
            return tokens[k], k + 1
        k += 1
        items = []
        while tokens[k] != ")":
            item, k = read(k)
            items.append(item)
        return items, k + 1

    tree, _ = read(0)
    return tree


UNQUOTED = {
    "yes", "no", "passive", "input", "output", "bidirectional", "tri_state",
    "power_in", "power_out", "free", "unspecified", "no_connect",
    "open_collector", "open_emitter", "unconnected",
    "line", "default", "none", "background", "outline", "solid", "dash", "dot",
    "hide", "inverted", "clock", "low", "edge", "non_logic",
    "left", "right", "top", "bottom", "center", "mirror",
    "global", "local", "private",
}


def dump(node, head=False) -> str:
    if isinstance(node, str):
        if isinstance(node, Quoted) or not (
            re.match(r"^-?\d+(?:\.\d+)?$", node)
            or node in UNQUOTED
            or (head and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", node))
        ):
            escaped = node.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return node
    return "(" + " ".join(dump(x, head=(i == 0)) for i, x in enumerate(node)) + ")"


class Libraries:
    def __init__(self):
        self._files = {}

    def _file(self, lib):
        if lib not in self._files:
            tree = parse((LIBROOT / f"{lib}.kicad_sym").read_text(encoding="utf-8"))
            self._files[lib] = {
                item[1]: item
                for item in tree
                if isinstance(item, list) and item and item[0] == "symbol"
            }
        return self._files[lib]

    def symbol(self, lib: str, name: str):
        table = self._file(lib)
        sym = table[name]
        parent_name = None
        for item in sym[1:]:
            if isinstance(item, list) and item and item[0] == "extends":
                parent_name = item[1]
        if not parent_name:
            return sym
        parent = self.symbol(lib, parent_name)
        child_props = {
            item[1]: item
            for item in sym[1:]
            if isinstance(item, list) and item and item[0] == "property"
        }
        merged = ["symbol", name]
        for item in parent[2:]:
            if isinstance(item, list) and item and item[0] == "property":
                merged.append(child_props.pop(item[1], item))
            elif isinstance(item, list) and item and item[0] == "symbol":
                renamed = list(item)
                if isinstance(renamed[1], str) and renamed[1].startswith(parent_name + "_"):
                    renamed[1] = name + renamed[1][len(parent_name) :]
                merged.append(renamed)
            elif not (isinstance(item, list) and item and item[0] == "extends"):
                merged.append(item)
        merged.extend(child_props.values())
        return merged


LIBS = Libraries()


def pins_of(sym):
    found = []

    def walk(node):
        if not isinstance(node, list) or not node:
            return
        if node[0] == "pin":
            at = next(x for x in node if isinstance(x, list) and x[0] == "at")
            num = next(x for x in node if isinstance(x, list) and x[0] == "number")
            name = next(x for x in node if isinstance(x, list) and x[0] == "name")
            hidden = any(isinstance(x, list) and x and x[0] == "hide" for x in node)
            found.append(
                {
                    "num": num[1],
                    "name": name[1],
                    "type": node[1],
                    "x": float(at[1]),
                    "y": float(at[2]),
                    "ang": float(at[3]),
                    "hidden": hidden,
                }
            )
        for child in node:
            if isinstance(child, list):
                walk(child)

    walk(sym)
    return found


def outward(angle: float):
    a = int(round(angle)) % 360
    # Library coordinates are Y-up. The schematic file is Y-down, so the
    # wire leaves the pin tip in the opposite direction and the Y sign flips.
    dx, dy = {0: (-1, 0), 90: (0, -1), 180: (1, 0), 270: (0, 1)}[a]
    return dx, -dy


def on_grid(mm: float) -> float:
    """KiCad's electrical grid is 50 mil. Integer millimetres are not on that grid."""
    mils = mm / 0.0254
    snapped = round(mils / 50.0) * 50.0
    return round(snapped * 0.0254, 4)


def _libfp(lib: str, name: str) -> str:
    return f"{lib}:{name}"


_PACK = {
    "r0402": _libfp("Resistor_SMD", "R_0402_1005Metric"),
    "r2512": _libfp("Resistor_SMD", "R_2512_6332Metric"),
    "c0402": _libfp("Capacitor_SMD", "C_0402_1005Metric"),
    "c0805": _libfp("Capacitor_SMD", "C_0805_2012Metric"),
    "sod": _libfp("Diode_SMD", "D_SOD-123"),
    "sma": _libfp("Diode_SMD", "D_SMA"),
    "sot23": _libfp("Package_TO_SOT_SMD", "SOT-23"),
    "sot236": _libfp("Package_TO_SOT_SMD", "SOT-23-6"),
    "sot223": _libfp("Package_TO_SOT_SMD", "SOT-223-3_TabPin2"),
    "sot353": _libfp("Package_TO_SOT_SMD", "SOT-353_SC-70-5"),
    "tsot": _libfp("Package_TO_SOT_SMD", "TSOT-23-6"),
    "so8": _libfp("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"),
    "so16": _libfp("Package_SO", "SOIC-16W_7.5x10.3mm_P1.27mm"),
    "sop4": _libfp("Package_SO", "SOIC-4_4.55x2.6mm_P1.27mm"),
    "tssop8": _libfp("Package_SO", "TSSOP-8_3x3mm_P0.65mm"),
    "fuse": _libfp("Fuse", "Fuse_1206_3216Metric"),
    "ind": _libfp("Inductor_SMD", "L_Bourns-SRN4018"),
    "led0603": _libfp("LED_SMD", "LED_0603_1608Metric"),
    "sw": _libfp("Button_Switch_SMD", "SW_SPST_TL3342"),
    "tp": _libfp("TestPoint", "TestPoint_Pad_D1.5mm"),
    "usb": _libfp("Connector_USB", "USB_C_Receptacle_HRO_TYPE-C-31-M-12"),
    "esp": _libfp("RF_Module", "ESP32-S3-WROOM-1"),
    "finder": _libfp("Relay_THT", "Relay_SPDT_Finder_40.31"),
    "hdr2": _libfp("Connector_PinHeader_2.54mm", "PinHeader_1x02_P2.54mm_Vertical"),
    "hdr3": _libfp("Connector_PinHeader_2.54mm", "PinHeader_1x03_P2.54mm_Vertical"),
    "mej2": "windlass:Murata_MEJ2SxxxxSC",
    "kf2": "windlass:KF350-3.5-1x02",
    "kf4": "windlass:KF350-3.5-1x04",
    "xh4": _libfp("Connector_JST", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"),
    "xh5": _libfp("Connector_JST", "JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical"),
}


def _bind(pack: str, refs) -> None:
    for ref in refs:
        REF_FP[ref] = _PACK[pack]


REF_FP = {}
_bind("esp", ["U3"])
_bind("mej2", ["U4", "U9"])
_bind("so8", ["U5"])
_bind("so16", ["U10"])
_bind("tssop8", ["U11"])
_bind("sot353", ["U8", "U12"])
_bind("sop4", ["U6", "U7"])
_bind("tsot", ["U20", "U21"])
_bind("sot223", ["Q_MCU", "Q_COIL"])
_bind("sot23", ["Q_UP", "Q_DN", "Q_SERIES", "Q_CLAMP_UP", "Q_CLAMP_DN", "Q90", "Q91", "Q_LED"])
_bind("sot236", ["U_ESD"])
_bind("finder", ["K_UP", "K_DN"])
_bind("usb", ["J_USB"])
_bind("hdr2", ["JP1"])
_bind("hdr3", ["JP_REED"])
_bind("sw", ["SW_RST", "SW_BOOT"])
_bind("led0603", ["D_R", "D_G", "D_B"])
_bind("tp", ["TP_TX", "TP_RX", "TP_WDI", "TP_VBUS"])
_bind("fuse", ["F_MCU", "F_5V", "F_COIL"])
_bind("sma", ["D_TVS_MCU", "D_TVS_COIL", "D60", "D70"])
_bind("sod", ["D20", "D21", "D30", "D40", "D80", "D_Z_MCU", "D_Z_COIL"])
_bind("ind", ["L20", "L21"])
_bind("r2512", ["R24", "R94"])
_bind("c0805", ["C10", "C11", "C50", "C30I", "C30A", "C30C", "C40I", "C40A", "C40C"])
_bind("kf2", ["J_PWR"])
_bind("kf4", ["J_CONTACT", "J_PERM"])
_bind("xh4", ["J_REED"])
_bind("xh5", ["J_SENSE", "J_NMEA"])
_bind(
    "r0402",
    [
        "R_MCU_G", "R_COIL_G", "R10", "R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19",
        "R20", "R22", "R23", "R30", "R30P", "R40", "R40P", "R50", "R51", "R52", "R53",
        "R60", "R61", "R70", "R71", "R80", "R81", "R82", "R90", "R91", "R92", "R93",
        "R_R", "R_G", "R_B", "R_RPD", "R_GPD", "R_BPD", "R_SWLINK", "R_IGNLINK", "R_COILFEED",
    ],
)
_bind(
    "c0402",
    ["C12", "C13", "C20", "C21", "C22", "C24", "C30", "C40", "C51", "C90", "C91", "C92", "C93", "C30B", "C40B"],
)


LOCAL_PINS = {}


def local_rect_symbol(lib_id, ref, value, description, pin_defs, width=10.16):
    """pin_defs: list of (num, name, type, side) side in L/R/T/B."""
    left = [p for p in pin_defs if p[3] == "L"]
    right = [p for p in pin_defs if p[3] == "R"]
    top = [p for p in pin_defs if p[3] == "T"]
    bottom = [p for p in pin_defs if p[3] == "B"]
    pins = []
    coords = {}
    y = 2.54 * (len(left) - 1)
    for num, name, ptype, _side in left:
        coords[num] = (-width, y, 0)
        pins.append((num, name, ptype, -width, y, 0))
        y -= 2.54
    y = 2.54 * (len(right) - 1)
    for num, name, ptype, _side in right:
        coords[num] = (width, y, 180)
        pins.append((num, name, ptype, width, y, 180))
        y -= 2.54
    for num, name, ptype, _side in top:
        coords[num] = (0, width, 270)
        pins.append((num, name, ptype, 0, width, 270))
    for num, name, ptype, _side in bottom:
        coords[num] = (0, -width, 90)
        pins.append((num, name, ptype, 0, -width, 90))
    leaf = lib_id.split(":")[-1]
    LOCAL_PINS[lib_id] = [
        {"num": n, "name": nm, "type": t, "x": x, "y": y, "ang": a, "hidden": False}
        for n, nm, t, x, y, a in pins
    ]
    pin_sexpr = []
    for n, nm, t, x, y, a in pins:
        pin_sexpr.append(
            f'(pin {t} line (at {x} {y} {int(a)}) (length 2.54) (name "{nm}" (effects (font (size 1.27 1.27)))) (number "{n}" (effects (font (size 1.27 1.27)))))'
        )
    body = " ".join(pin_sexpr)
    return f'''(symbol "{lib_id}"
  (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes)
  (property "Reference" "{ref}" (at 0 {width + 2.54} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Value" "{value}" (at 0 {width + 5.08} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Datasheet" "" (at 0 0 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Description" "{description}" (at 0 0 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (symbol "{leaf}_0_1"
    (rectangle (start {-width + 2.54} {width - 1.27}) (end {width - 2.54} {-width + 1.27})
      (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol "{leaf}_1_1" {body})
)'''


LOCAL_SYMBOLS = {
    "windlass:ISO1042BDWR": local_rect_symbol(
        "windlass:ISO1042BDWR",
        "U",
        "ISO1042BDWR",
        "TI ISO1042 DW-16 isolated CAN. Pinout from datasheet Rev F, Figure 4-1. Project-local symbol; not in the KiCad library.",
        [
            ("1", "VCC1", "power_in", "L"),
            ("2", "GND1", "power_in", "L"),
            ("3", "TXD", "input", "L"),
            ("5", "RXD", "output", "L"),
            ("8", "GND1", "power_in", "L"),
            ("16", "VCC2", "power_in", "R"),
            ("15", "GND2", "power_in", "R"),
            ("13", "CANH", "passive", "R"),
            ("12", "CANL", "passive", "R"),
            ("11", "VCC2", "power_in", "R"),
            ("10", "VCC2", "power_in", "R"),
            ("9", "GND2", "power_in", "R"),
        ],
        width=12.7,
    ),
    "windlass:ISO_DCDC_OPEN": local_rect_symbol(
        "windlass:ISO_DCDC_OPEN",
        "U",
        "ISO_DCDC_OPEN",
        "Isolated DC-DC placeholder. MPN, isolation rating and current are OPEN. Do not treat as a selected part.",
        [
            ("1", "+VIN", "passive", "L"),
            ("2", "-VIN", "passive", "L"),
            ("4", "+VOUT", "power_out", "R"),
            ("3", "-VOUT", "power_out", "R"),
        ],
    ),
    "windlass:BUCK_12_5_OPEN": local_rect_symbol(
        "windlass:BUCK_12_5_OPEN",
        "U",
        "BUCK_12_5_OPEN",
        "12 V to 5 V buck placeholder. Inductor, compensation and MPN are OPEN.",
        [
            ("1", "VIN", "power_in", "L"),
            ("2", "GND", "power_in", "B"),
            ("3", "VOUT", "power_out", "R"),
        ],
    ),
    "windlass:DIODE_OPEN": local_rect_symbol(
        "windlass:DIODE_OPEN",
        "D",
        "DIODE_OPEN",
        "Diode whose MPN is not yet chosen.",
        [("1", "K", "passive", "L"), ("2", "A", "passive", "R")],
        width=5.08,
    ),
    "windlass:MEJ2S": local_rect_symbol(
        "windlass:MEJ2S",
        "U",
        "MEJ2S",
        "Murata MEJ2 single-output SIP. Pins 1 +Vin, 2 -Vin, 5 -Vout, 7 +Vout. Pin 6 is not fitted. Functional isolation, 5.2 kVDC hipot for 1 s, 2.4 kVDC continuous. Not a safety-barrier approval.",
        [
            ("1", "+VIN", "power_in", "L"),
            ("2", "-VIN", "power_in", "L"),
            ("7", "+VOUT", "power_out", "R"),
            ("5", "-VOUT", "power_out", "R"),
        ],
    ),
    "windlass:DMP6023LE": local_rect_symbol(
        "windlass:DMP6023LE",
        "Q",
        "DMP6023LE-13",
        "Diodes DMP6023LE, SOT-223, -60 V, -7 A. Pin 1 gate, pin 2 drain (tab), pin 3 source, from the Diodes pin-out drawing.",
        [
            ("1", "G", "input", "L"),
            ("2", "D", "passive", "R"),
            ("3", "S", "passive", "B"),
        ],
        width=7.62,
    ),
    "windlass:NX6008NBK": local_rect_symbol(
        "windlass:NX6008NBK",
        "Q",
        "NX6008NBK",
        "Nexperia NX6008NBK, SOT-23, 60 V. Pin 1 gate, pin 2 source, pin 3 drain. RDS max 3 ohm at Vgs 2.5 V. Vgs absolute maximum is +/-8 V, so the gate stays on the 3.3 V logic rail.",
        [
            ("1", "G", "input", "L"),
            ("3", "D", "passive", "R"),
            ("2", "S", "passive", "B"),
        ],
        width=7.62,
    ),
    "windlass:74LVC1G123": local_rect_symbol(
        "windlass:74LVC1G123",
        "U",
        "74LVC1G123",
        "Nexperia 74LVC1G123 retriggerable monostable. Pin numbers from the Nexperia datasheet. Single-unit project symbol so both units of the KiCad multi-unit symbol are not required.",
        [
            ("1", "A", "input", "L"),
            ("2", "B", "input", "L"),
            ("3", "CLR", "input", "L"),
            ("4", "GND", "power_in", "L"),
            ("5", "Q", "output", "R"),
            ("6", "CEXT", "passive", "R"),
            ("7", "REXT", "passive", "R"),
            ("8", "VCC", "power_in", "R"),
        ],
        width=12.7,
    ),
}


class Sheet:
    def __init__(self, name: str):
        self.name = name
        self.uuid = SHEET_IDS[name]
        self.path = f"/{ROOT_UUID}/{self.uuid}"
        self.items = []
        self.symbols_used = {}
        self.pin_cache = {}
        self._seq = 0

    def _sym(self, lib_id):
        if lib_id in self.pin_cache:
            return self.pin_cache[lib_id]
        if lib_id in LOCAL_SYMBOLS:
            self.symbols_used[lib_id] = LOCAL_SYMBOLS[lib_id]
            self.pin_cache[lib_id] = LOCAL_PINS[lib_id]
            return LOCAL_PINS[lib_id]
        lib, name = lib_id.split(":")
        sym = LIBS.symbol(lib, name)
        embedded = ["symbol", lib_id] + sym[2:]
        self.symbols_used[lib_id] = dump(embedded)
        found = pins_of(sym)
        self.pin_cache[lib_id] = found
        return found

    def place(self, lib_id, ref, value, x, y, footprint="", unit=1, body=1, on_board="yes"):
        x, y = on_grid(x), on_grid(y)
        footprint = footprint or REF_FP.get(ref, "")
        pins = self._sym(lib_id)
        su = uid()
        pin_xml = []
        abs_pins = []
        for p in pins:
            pin_xml.append(f'(pin "{p["num"]}" (uuid "{uid()}"))')
            abs_pins.append({**p, "ax": round(x + p["x"], 4), "ay": round(y - p["y"], 4)})
        fp = footprint or ""
        inst = f'''(symbol
  (lib_id "{lib_id}")
  (at {x} {y} 0)
  (unit {unit})
  (body_style {body})
  (exclude_from_sim no) (in_bom yes) (on_board {on_board}) (in_pos_files {on_board}) (dnp no)
  (uuid "{su}")
  (property "Reference" "{ref}" (at {x} {y + 5.08} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Value" "{value}" (at {x} {y - 5.08} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Footprint" "{fp}" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Datasheet" "" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  {" ".join(pin_xml)}
  (instances (project "{PROJECT}" (path "{self.path}" (reference "{ref}") (unit {unit}))))
)'''
        self.items.append(inst)
        return abs_pins

    def _wire(self, x1, y1, x2, y2):
        if (x1, y1) == (x2, y2):
            return
        self.items.append(
            f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{uid()}"))'
        )

    def _stub(self, pin):
        dx, dy = outward(pin["ang"])
        x2 = round(pin["ax"] + dx * 2.54, 4)
        y2 = round(pin["ay"] + dy * 2.54, 4)
        self._wire(pin["ax"], pin["ay"], x2, y2)
        return x2, y2

    def label(self, pin, name):
        x, y = self._stub(pin)
        dx, _dy = outward(pin["ang"])
        justify = "right bottom" if dx < 0 else "left bottom"
        self.items.append(
            f'(global_label "{name}" (shape passive) (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{uid()}"))'
        )

    def power(self, pin, name):
        x, y = self._stub(pin)
        lib = f"power:{name}"
        self._sym(lib)
        ref = "#PWR" + uuid.uuid4().hex[:6]
        # GND and +3V3/+5V/+12V pins sit at the symbol origin, unit 1 style 1.
        self.items.append(
            f'''(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (body_style 1)
  (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)
  (uuid "{uid()}")
  (property "Reference" "{ref}" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Value" "{name}" (at {x} {y - 2.54} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Datasheet" "" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (pin "1" (uuid "{uid()}"))
  (instances (project "{PROJECT}" (path "{self.path}" (reference "{ref}") (unit 1))))
)'''
        )

    def flag(self, x, y, net_label=None):
        """PWR_FLAG. Pin is in the library unit PWR_FLAG_0_0, so unit 0 style 0."""
        x, y = on_grid(x), on_grid(y)
        self._sym("power:PWR_FLAG")
        ref = "#FLG" + uuid.uuid4().hex[:4]
        self.items.append(
            f'''(symbol (lib_id "power:PWR_FLAG") (at {x} {y} 0) (unit 0) (body_style 0)
  (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)
  (uuid "{uid()}")
  (property "Reference" "{ref}" (at {x} {y + 3.81} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Value" "PWR_FLAG" (at {x} {y + 5.08} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Datasheet" "" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (pin "1" (uuid "{uid()}"))
  (instances (project "{PROJECT}" (path "{self.path}" (reference "{ref}") (unit 0))))
)'''
        )
        if net_label:
            if net_label in ("GND", "+3V3", "+5V", "+12V"):
                self._sym(f"power:{net_label}")
                pref = "#PWR" + uuid.uuid4().hex[:6]
                self.items.append(
                    f'''(symbol (lib_id "power:{net_label}") (at {x} {y} 0) (unit 1) (body_style 1)
  (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)
  (uuid "{uid()}")
  (property "Reference" "{pref}" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Value" "{net_label}" (at {x} {y - 2.54} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (property "Datasheet" "" (at {x} {y} 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))
  (pin "1" (uuid "{uid()}"))
  (instances (project "{PROJECT}" (path "{self.path}" (reference "{pref}") (unit 1))))
)'''
                )
            else:
                self.items.append(
                    f'(global_label "{net_label}" (shape passive) (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid()}"))'
                )

    def nc(self, pin):
        self.items.append(f'(no_connect (at {pin["ax"]} {pin["ay"]}) (uuid "{uid()}"))')

    def note(self, x, y, text):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        self.items.append(
            f'(text "{escaped}" (at {x} {y} 0) (effects (font (size 1.27 1.27))) (uuid "{uid()}"))'
        )

    def save(self, folder: Path):
        libs = "\n".join(self.symbols_used.values())
        body = "\n".join(self.items)
        title = self.name.replace("_", " ")
        text = f'''(kicad_sch
  (version {VERSION})
  (generator "windlass_build_schematic")
  (generator_version "1")
  (uuid "{self.uuid}")
  (paper "A3")
  (title_block (title "{title}") (date "2026-11-19") (rev "0.7-not-for-fabrication") (company "Windlass PCB") (comment 1 "NOT FOR FABRICATION"))
  (lib_symbols
{libs}
  )
{body}
  (embedded_fonts no)
)
'''
        (folder / f"{self.name}.kicad_sch").write_text(text, encoding="utf-8")


def pin(pins, num=None, name=None):
    hits = []
    for p in pins:
        if num is not None and p["num"] != num:
            continue
        if name is not None and p["name"] != name:
            continue
        hits.append(p)
    if not hits:
        raise KeyError(f"pin num={num} name={name}")
    return hits


def connect_named(sheet, pins, mapping):
    """mapping: pin name -> 'GND'/'+3V3'/... or a global label, or None to NC."""
    used = set()
    for p in pins:
        if p["hidden"] and p["type"] == "no_connect":
            continue
        key = (p["ax"], p["ay"])
        if key in used:
            continue
        if p["name"] not in mapping and p["num"] not in mapping:
            sheet.nc(p)
            used.add(key)
            continue
        dest = mapping.get(p["name"], mapping.get(p["num"]))
        if dest is None:
            sheet.nc(p)
        elif dest in ("GND", "+3V3", "+5V", "+12V"):
            sheet.power(p, dest)
        else:
            sheet.label(p, dest)
        used.add(key)


def two_pin(sheet, lib, ref, value, x, y, a, b, footprint=""):
    pins = sheet.place(lib, ref, value, x, y, footprint)
    # passive two-pin parts use numbers 1 and 2
    p1 = pin(pins, num="1")[0]
    p2 = pin(pins, num="2")[0]
    for p, dest in ((p1, a), (p2, b)):
        if dest in ("GND", "+3V3", "+5V", "+12V"):
            sheet.power(p, dest)
        else:
            sheet.label(p, dest)


def multi_pin(sheet, lib, ref, value, x, y, nets, footprint=""):
    """nets is pin 1..n. None marks a no-connect. Repeated names are the same net, not a join of domains."""
    pins = sheet.place(lib, ref, value, x, y, footprint)
    by = {p["num"]: p for p in pins}
    for i, dest in enumerate(nets, start=1):
        p = by[str(i)]
        if dest is None:
            sheet.nc(p)
        elif dest in ("GND", "+3V3", "+5V", "+12V"):
            sheet.power(p, dest)
        else:
            sheet.label(p, dest)


def build_power(s: Sheet):
    s.note(
        20,
        250,
        "POWER rev 0.2. NOT FOR FABRICATION.\\n"
        "VIN_12 splits into two protected branches. +12V_MCU feeds only the bucks. +12V_COIL feeds only the switch, ignition and coils.\\n"
        "The MCU branch stays up when the relay switch is open. Coil current does not flow through Q_MCU or the bucks.\\n"
        "AP2112K is removed. 3.3 V is an AP63203 buck straight from +12V_MCU, so the Wi-Fi current is not dropped across a 1.7 V linear regulator.",
    )
    s.flag(25, 210, "VIN_12")
    two_pin(s, "Device:Fuse", "F_MCU", "2A_0466002", 55, 200, "VIN_12", "VIN_MCU")
    # SMAJ18A extends SM6T: pin 1 is the cathode end of the symbol, pin 2 the anode.
    two_pin(s, "Diode:SMAJ18A", "D_TVS_MCU", "SMAJ18A", 90, 200, "VIN_MCU", "GND", "Diode_SMD:D_SMA")
    q = s.place("windlass:DMP6023LE", "Q_MCU", "DMP6023LE-13", 140, 200)
    connect_named(s, q, {"D": "VIN_MCU", "S": "+12V_MCU", "G": "QMCU_G"})
    two_pin(s, "Device:R", "R_MCU_G", "100k", 140, 175, "QMCU_G", "GND")
    two_pin(s, "windlass:DIODE_OPEN", "D_Z_MCU", "BZT52C12", 170, 200, "+12V_MCU", "QMCU_G")
    s.flag(175, 215, "+12V_MCU")
    _buck(s, 40, 130, "U20", "AP63203WU", "L20", "3.9uH", "SW_3V3", "BST_3V3", "+3V3", "C30")
    # FB and the output capacitors stay on the buck side of F_5V. The fuse is the Murata input fuse.
    _buck(s, 200, 130, "U21", "AP63205WU", "L21", "4.7uH", "SW_5V", "BST_5V", "V5_RAW", "C40")
    two_pin(s, "Device:Fuse", "F_5V", "2A_antisurge", 310, 130, "V5_RAW", "+5V")
    s.flag(40, 80, "+3V3")
    s.flag(330, 130, "+5V")
    # Coil branch sized for the Finder coil current. The Lofrans contact current is still unmeasured.
    two_pin(s, "Device:Fuse", "F_COIL", "1A_0466001", 40, 50, "VIN_12", "VIN_COIL")
    two_pin(s, "Diode:SMAJ18A", "D_TVS_COIL", "SMAJ18A", 80, 50, "VIN_COIL", "GND", "Diode_SMD:D_SMA")
    qc = s.place("windlass:DMP6023LE", "Q_COIL", "DMP6023LE-13", 130, 50)
    for p in pin(qc, name="D"):
        s.label(p, "VIN_COIL")
    for p in pin(qc, name="S"):
        s.label(p, "+12V_COIL")
    for p in pin(qc, name="G"):
        s.label(p, "QCOIL_G")
    two_pin(s, "Device:R", "R_COIL_G", "100k", 130, 28, "QCOIL_G", "GND")
    two_pin(s, "windlass:DIODE_OPEN", "D_Z_COIL", "BZT52C12", 165, 50, "+12V_COIL", "QCOIL_G")
    s.flag(170, 65, "+12V_COIL")
    s.flag(20, 20, "GND")
    s.note(
        20,
        100,
        "SMAJ18A is a 400 W, 10/1000 us clamp, about 29.2 V. It is not load-dump protection. A load-dump pulse is a different, much larger stress, and its source impedance is unmeasured.\\n"
        "AP6320x absolute maximum is 35 V DC and 40 V for 400 ms. Recommended operating maximum is 32 V. The TVS keeps a short pulse inside that range only while the TVS itself survives.\\n"
        "EN is tied to +12V_MCU. Internal VIN UVLO is about 3.5 V rising, 440 mV hysteresis. It is not raised, because a shared windlass battery sag is unmeasured.\\n"
        "Reverse battery: Q_MCU turns off. The unidirectional TVS then conducts and F_MCU is what opens. F_5V is the 2 A anti-surge fuse Murata requires on a 5 V MEJ2 input.\\n"
        "Coil branch is now sized for two Finder 40.31 coils, 42 mA each, only one at a time. F_COIL is 1 A. Q_COIL is the same DMP6023LE. SMAJ18A on this branch is the same short-pulse clamp, not load-dump protection.",
    )


def _buck(s, x, y, uref, value, lref, lval, sw, bst, vout, cref):
    u = s.place(
        "Regulator_Switching:" + value,
        uref,
        value,
        x,
        y,
        "Package_TO_SOT_SMD:TSOT-23-6",
    )
    connect_named(s, u, {"IN": "+12V_MCU", "EN": "+12V_MCU", "GND": "GND", "SW": sw, "BST": bst, "FB": vout})
    two_pin(s, "Device:L", lref, lval, x + 35, y + 8, sw, vout)
    two_pin(s, "Device:C", cref + "B", "100nF", x + 20, y - 18, bst, sw)
    two_pin(s, "Device:C", cref + "I", "10uF", x - 15, y - 18, "+12V_MCU", "GND")
    two_pin(s, "Device:C", cref + "A", "22uF", x + 55, y - 12, vout, "GND")
    two_pin(s, "Device:C", cref + "C", "22uF", x + 70, y - 12, vout, "GND")


def build_esp(s: Sheet):
    s.note(
        20,
        270,
        "ESP32-S3-WROOM-1-N16. NOT FOR FABRICATION.\\n"
        "EN: 10k to +3V3 and 1 uF to GND, from the module datasheet RC-delay recommendation.\\n"
        "GPIO0: 10k pull-up, button to GND, normal SPI boot. GPIO46 and GPIO45 are left open (internal pull-down). Do not pull GPIO45 high.\\n"
        "GPIO3: 10k to GND. Datasheet: no internal pull, level must be defined. Default eFuse ignores GPIO3 for JTAG source.\\n"
        "USB VBUS is not connected to +5V or +3V3. A cable that also carries 12 V battery power does not backfeed the onboard 5 V rail, and the onboard 5 V rail does not drive VBUS.\\n"
        "CC1 and CC2 each have 5.1k to GND, the device-side Rd. D+ and D- each have 22 ohm series resistors on the module side of U_ESD. There is no VBUS-detect GPIO.",
    )
    m = s.place("RF_Module:ESP32-S3-WROOM-1", "U3", "ESP32-S3-WROOM-1-N16", 160, 150)
    gpio = {
        "3V3": "+3V3",
        "GND": "GND",
        "EN": "EN_NET",
        "IO0": "IO0_NET",
        "IO1": "WDI_FUTURE",
        "IO3": "IO3_NET",
        "IO4": "TWAI_TX",
        "IO5": "TWAI_RX",
        "IO6": "REED_GPIO",
        "IO7": "UP_SENSE",
        "IO8": "DN_SENSE",
        "IO9": "UP_REQ",
        "IO10": "DN_REQ",
        "IO14": "COIL_RAIL_OK",
        "IO15": "LED_R",
        "IO16": "LED_G",
        "IO17": "LED_B",
        "IO18": "PUBLISH_EN",
        "USB_D-": "USB_DN",
        "USB_D+": "USB_DP",
        "TXD0": "UART_TX",
        "RXD0": "UART_RX",
    }
    connect_named(s, m, gpio)
    two_pin(s, "Device:R", "R10", "10k", 90, 210, "EN_NET", "+3V3")
    two_pin(s, "Device:C", "C10", "1uF", 90, 190, "EN_NET", "GND")
    sw = s.place(
        "Switch:SW_Push",
        "SW_RST",
        "TL3342F160QG",
        60,
        175,
        "Button_Switch_SMD:SW_SPST_TL3342",
    )
    connect_named(s, sw, {"1": "EN_NET", "2": "GND"})
    two_pin(s, "Device:R", "R11", "10k", 90, 150, "IO0_NET", "+3V3")
    swb = s.place(
        "Switch:SW_Push",
        "SW_BOOT",
        "TL3342F160QG",
        60,
        140,
        "Button_Switch_SMD:SW_SPST_TL3342",
    )
    connect_named(s, swb, {"1": "IO0_NET", "2": "GND"})
    two_pin(s, "Device:R", "R12", "10k", 90, 120, "IO3_NET", "GND")
    two_pin(s, "Device:C", "C11", "10uF", 200, 210, "+3V3", "GND")
    two_pin(s, "Device:C", "C12", "100nF", 220, 210, "+3V3", "GND")
    # Request pins idle low if the GPIO is high-Z. These pulldowns are the default-OFF for the coil requests.
    two_pin(s, "Device:R", "R13", "100k", 230, 160, "UP_REQ", "GND")
    two_pin(s, "Device:R", "R14", "100k", 230, 145, "DN_REQ", "GND")
    for ref, net, x in (
        ("TP_TX", "UART_TX", 40),
        ("TP_RX", "UART_RX", 55),
        ("TP_WDI", "WDI_FUTURE", 70),
        ("TP_VBUS", "USB_VBUS", 85),
    ):
        tp = s.place("Connector_Generic:Conn_01x01", ref, "TESTPAD", x, 100)
        s.label(pin(tp, num="1")[0], net)
    usb = s.place("Connector:USB_C_Receptacle_USB2.0_16P", "J_USB", "TYPE-C-31-M-12", 300, 150)
    connect_named(
        s,
        usb,
        {
            "GND": "GND",
            "VBUS": "USB_VBUS",
            "CC1": "CC1",
            "CC2": "CC2",
            "D+": "USB_DP_C",
            "D-": "USB_DN_C",
            "SBU1": None,
            "SBU2": None,
            "SHIELD": "USB_SHIELD",
        },
    )
    two_pin(s, "Device:R", "R15", "5.1k", 270, 120, "CC1", "GND")
    two_pin(s, "Device:R", "R16", "5.1k", 270, 105, "CC2", "GND")
    two_pin(s, "Device:R", "R17", "22", 250, 130, "USB_DP", "USB_DP_C")
    two_pin(s, "Device:R", "R18", "22", 250, 115, "USB_DN", "USB_DN_C")
    # ST pinout, SOT-23-6: 1 and 6 are I/O1, 3 and 4 are I/O2, 2 is GND, 5 is VBUS.
    # The I/O pins sit on the connector side of the 22 ohm resistors. Pin 5 is USB_VBUS, not +5V.
    esd = s.place("Power_Protection:USBLC6-2SC6", "U_ESD", "USBLC6-2SC6", 280, 155)
    connect_named(
        s,
        esd,
        {"I/O1": "USB_DP_C", "I/O2": "USB_DN_C", "GND": "GND", "VBUS": "USB_VBUS"},
    )
    two_pin(s, "Device:R", "R19", "1M", 320, 100, "USB_SHIELD", "GND")
    two_pin(s, "Device:C", "C13", "100nF", 340, 100, "USB_SHIELD", "GND")
    s.note(
        20,
        80,
        "CC 5.1k is USB Type-C Rd for a device port. 22 ohm series resistors are preliminary full-speed series values, not a safety rating.\\n"
        "U_ESD is USBLC6-2SC6, SOT-23-6. Both I/O1 pins are USB_DP_C and both I/O2 pins are USB_DN_C, on the connector side of R17 and R18.\\n"
        "Its VBUS pin is USB_VBUS. That net is not +5V and not +3V3. The device does not source VBUS and does not present Rp.\\n"
        "Shield is 1M || 100nF to board GND, not a hard chassis bond. Chassis bond is OPEN.\\n"
        "10 uF + 100 nF at the module 3V3 pin follows the Espressif guidance to put bulk capacitance at the module power pin.\\n"
        "GPIO1 is WDI_FUTURE. The relay sheet uses it as the heartbeat. This sheet does not toggle it, and the prototype firmware is not modified.",
    )


def build_reed(s: Sheet):
    s.note(
        20,
        250,
        "REED rev 0.7. Two modes, one isolator, one isolated 3.3 V rail. REED_RET is not GND, UP_RET, DN_RET or GND_CAN.\\n"
        "JP_REED is a 2.54 mm 1x03 header. Copper does not join the pins. SH_REED is the loose shunt, default on pins 1-2.\\n"
        "Pin 2 is REED_ISO. Pin 1 is LOFRANS_NODE. Pin 3 is DRY_A. The 4.7k pull-up is on DRY_A only.\\n"
        "MEJ2S0503SC is 5 V to 3.3 V. A 51 ohm preload is about 65 mA, above 10 percent of the 606 mA rating, so the published load envelope applies.\\n"
        "ISO7721 field supply is 3.3 V on purpose. At 5 V, VIH would be 3.5 V and the measured 3.22 V idle would not be a reliable high.",
    )
    dcdc = s.place("windlass:MEJ2S", "U4", "MEJ2S0503SC", 40, 180)
    connect_named(s, dcdc, {"1": "+5V", "2": "GND", "7": "REED_3V3", "5": "REED_RET"})
    two_pin(s, "Device:C", "C24", "100nF", 40, 150, "+5V", "GND")
    two_pin(s, "Device:C", "C20", "100nF", 80, 150, "REED_3V3", "REED_RET")
    two_pin(s, "Device:R", "R24", "51_0.5W", 100, 150, "REED_3V3", "REED_RET")
    # Lofrans conditioner. 10k series, 47k pull-down, clamps on the switch throw.
    two_pin(s, "Device:R", "R20", "10k", 140, 200, "REED_SIG", "LOFRANS_NODE")
    two_pin(s, "Device:D_Schottky", "D20", "BAT54W", 170, 200, "REED_3V3", "LOFRANS_NODE", "Diode_SMD:D_SOD-123")
    two_pin(s, "Device:D_Schottky", "D21", "BAT54W", 170, 180, "LOFRANS_NODE", "REED_RET", "Diode_SMD:D_SOD-123")
    jp = s.place(
        "Jumper:Jumper_3_Open",
        "JP_REED",
        "HDR_1x03_2.54",
        210,
        175,
        "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    )
    connect_named(s, jp, {"1": "LOFRANS_NODE", "2": "REED_ISO", "3": "DRY_A"})
    # Loose shunt. It is not soldered and it does not join the pins in copper.
    shunt = s.place("Connector_Generic:Conn_01x02", "SH_REED", "SHUNT_2.54", 250, 175, on_board="no")
    for p in shunt:
        s.nc(p)
    # Dry contact. Pull-up exists only on DRY_A, which is J_REED pin 3.
    two_pin(s, "Device:R", "R22", "4.7k", 210, 145, "REED_3V3", "DRY_A")
    # One pull-down, on the isolator side, so Lofrans mode is not two resistors in parallel.
    two_pin(s, "Device:R", "R23", "47k", 240, 155, "REED_ISO", "REED_RET")
    two_pin(s, "Device:C", "C22", "1nF", 240, 135, "REED_ISO", "REED_RET")
    iso = s.place("Isolator:ISO7721D", "U5", "ISO7721DR", 290, 175)
    connect_named(
        s,
        iso,
        {
            "VCC1": "+3V3",
            "GND1": "GND",
            "OUTA": "REED_GPIO",
            "INB": "GND",
            "VCC2": "REED_3V3",
            "GND2": "REED_RET",
            "INA": "REED_ISO",
            "OUTB": None,
        },
    )
    two_pin(s, "Device:C", "C21", "100nF", 320, 145, "+3V3", "GND")
    s.note(
        20,
        110,
        "One 47k pull-down sits on the isolator input. Lofrans load is 3.3 V / 47k = 70 uA. A second 47k would double that and is not fitted.\\n"
        "10 uA leakage in 47k is 0.47 V, below VIL. 100k would be 1.0 V and can cross VIL, so the load cannot be reduced further on this leakage spec.\\n"
        "1 nF at the isolator input with the 10k series resistor is about 10 us, still far under the 30 ms debounce, and it replaces the noise margin the lighter DC load gives up.\\n"
        "ISO7721 (no F suffix) defaults high if the field supply is off. High is idle. The existing firmware counts a rising edge, not a held low.\\n"
        "Lofrans position is one shunt on pins 1-2. DRY_A stays open, so the pull-up cannot reach REED_ISO, LOFRANS_NODE or REED_SIG.\\n"
        "Dry position is the same shunt on pins 2-3. LOFRANS_NODE stays open, so the pull-up reaches the isolator and does not reach REED_SIG.\\n"
        "Default assembly is pins 1-2. Fit one shunt only. Two shunts would short pin 1 to pin 3.\\n"
        "With the shunt removed, R23 holds REED_ISO low. A held level is not a pulse.\\n"
        "ISO7721 without the F suffix holds its output high when VCC2 is below its UVLO and VCC1 is valid, and the output is high-impedance when VCC1 is below UVLO.\\n"
        "VCC1 is the same +3V3 as the ESP32, so the MCU is not running while the output side is unpowered.\\n"
        "The existing firmware samples the pin at start and does not treat that sample as an edge. It counts a change only after 30 ms, and only when the new level is high and a direction sense input is already active.\\n"
        "Field-supply startup and jumper removal produce a falling edge or no edge. A rising edge from supply shutdown or from inserting the shunt is ignored while the windlass sense is stopped.\\n"
        "R20 and the clamps stay on the Lofrans node in both positions. JP1 only removes the CAN isolator supply. Do not fit both sources at once.\\n"
        "Chain length stays the NVS calibration, default 0.36 m per pulse.",
    )


def build_direction(s: Sheet):
    s.note(
        20,
        250,
        "DIRECTION SENSE. Two separate 12 V opto channels. NOT FOR FABRICATION.\\n"
        "UP_RET and DN_RET are different nets. Neither is connected to GND or to each other on this PCB.\\n"
        "Joining IN2/IN3 grounds on the previous prototype caused a fault. This sheet does not join them.\\n"
        "Whether the boat wiring may tie the two returns together is OPEN. Do that only from the Lofrans diagram, off this PCB.\\n"
        "R30 and R40 are OPEN. LED current is (Vfield - Vf) / R. It must stay far below contactor pull-in and inside the Lofrans driver rating.\\n"
        "TLP291 pins, KiCad symbol and Toshiba convention: 1 anode, 2 cathode, 3 emitter, 4 collector.\\n"
        "LED on pulls the GPIO low, matching the existing firmware (LOW = active).",
    )
    _sense_channel(s, 40, "UP", "R30", "D30", "C30", "U6")
    _sense_channel(s, 140, "DN", "R40", "D40", "C40", "U7")
    s.note(
        20,
        90,
        "Current path, each channel, and only that channel:\\n"
        "FIELD pin -> R_OPEN -> TLP291 anode, cathode -> that channel RET pin.\\n"
        "1N4148 is anti-parallel across the LED (cathode at anode, anode at cathode) so a reverse transient does not break the LED.\\n"
        "100 nF is across the LED. Time constant is R_OPEN * 100 nF and is therefore OPEN. Firmware already debounces 30 ms.\\n"
        "No copper path exists from these field pins to GND, to the other channel, or back out as a voltage source.\\n"
        "The opto output cannot push 12 V into the ESP32. The ESP32 cannot push 3.3 V into the Lofrans wire.",
    )


def _sense_channel(s, y, tag, rref, dref, cref, uref):
    field = f"{tag}_FIELD"
    ret = f"{tag}_RET"
    node = f"{tag}_LED_A"
    gpio = "UP_SENSE" if tag == "UP" else "DN_SENSE"
    two_pin(s, "Device:R", rref, "R_IN_OPEN", 50, y, field, node)
    opt = s.place(
        "Isolator:TLP291",
        uref,
        "TLP291(GB-TP,SE",
        100,
        y,
        "Package_SO:SOIC-4_4.55x2.6mm_P1.27mm",
    )
    # pins by number
    by = {p["num"]: p for p in opt}
    s.label(by["1"], node)       # anode
    s.label(by["2"], ret)        # cathode
    s.label(by["3"], "GND") if False else     s.power(by["3"], "GND")  # emitter
    s.label(by["4"], gpio)
    two_pin(s, "Device:R", rref + "P", "10k", 150, y + 15, gpio, "+3V3")
    # anti-parallel diode: K at anode node, A at return. DIODE_OPEN pin1=K pin2=A.
    two_pin(s, "windlass:DIODE_OPEN", dref, "1N4148W_ANTIPARALLEL", 70, y - 20, node, ret)
    two_pin(s, "Device:C", cref, "100nF", 70, y + 18, node, ret)


def build_relay(s: Sheet):
    s.note(
        20,
        265,
        "RELAY CONTROL. NOT FOR FABRICATION. Finder 40.31.7.012.0000, hand-fitted through-hole.\\n"
        "Coil code 7.012: 288 ohm and 42 mA at 12 V from the coil table. Pickup 8.8 V, max 18 V, operate/release 7/3 ms. The family is called 0.65 W; 12 V times 42 mA is 0.50 W.\\n"
        "SPDT used as NO. The NC pin is open. UP_COM is not tied to DN_COM. Neither contact pin touches GND.\\n"
        "The Finder DC1 rating is 10 A resistive at 30 V. That rating is not the Lofrans contactor load and is not the track size.\\n"
        "Contact copper is calculated for a provisional 2 A. There is no fuse and no suppressor on the four contact nets. Measure the contactor current and its kick before installation.\\n"
        "Coil high side is +12V_COIL, then the external relay-power switch, then the external ignition contact, then R_COILFEED.\\n"
        "R_COILFEED is only that series connection. It is not a watchdog bypass. Coil current still has to pass Q_SERIES, and Q_SERIES is on only while the heartbeat is fresh and exactly one direction is requested.\\n"
        "Both GPIOs high: XOR is low, so the AND is low, and each gate is clamped off by the other request.\\n"
        "A welded contact is not opened by any of this. There is no auxiliary contact, so the paralleled +12 V node cannot prove which operator closed it.",
    )
    two_pin(s, "Device:R", "R_COILFEED", "0", 30, 200, "IGN_B", "COIL_12")
    s.note(20, 230, "Heartbeat: rising edge only. A high or low level does not hold Q. The future image may edge GPIO1 only during a valid RUN. A running loop is not a heartbeat.")
    wdt = s.place("windlass:74LVC1G123", "U11", "74LVC1G123DP,125", 70, 175)
    connect_named(
        s,
        wdt,
        {
            "A": "GND",
            "B": "WDI_FUTURE",
            "CLR": "+3V3",
            "GND": "GND",
            "Q": "WDT_Q",
            "CEXT": "WDT_C",
            "REXT": "WDT_RC",
            "VCC": "+3V3",
        },
    )
    two_pin(s, "Device:R", "R52", "100k", 110, 200, "+3V3", "WDT_RC")
    two_pin(s, "Device:C", "C50", "3.3uF", 110, 180, "WDT_C", "WDT_RC")
    two_pin(s, "Device:R", "R53", "100k", 40, 145, "WDI_FUTURE", "GND")
    two_pin(s, "Device:C", "C51", "100nF", 40, 130, "+3V3", "GND")
    xor = s.place(
        "74xGxx:74LVC1G86",
        "U8",
        "74LVC1G86GW,125",
        160,
        180,
        "Package_TO_SOT_SMD:SOT-353_SC-70-5",
    )
    connect_named(s, xor, {"1": "UP_REQ", "2": "DN_REQ", "GND": "GND", "4": "XOR_Y", "5": "+3V3"})
    andg = s.place(
        "74xGxx:74LVC1G08",
        "U12",
        "74LVC1G08GW,125",
        200,
        160,
        "Package_TO_SOT_SMD:SOT-353_SC-70-5",
    )
    connect_named(s, andg, {"1": "XOR_Y", "2": "WDT_Q", "GND": "GND", "4": "AND_Y", "5": "+3V3"})
    two_pin(s, "Device:R", "R50", "100", 240, 160, "AND_Y", "QSERIES_G")
    two_pin(s, "Device:R", "R51", "100k", 240, 140, "QSERIES_G", "GND")
    qs = s.place("windlass:NX6008NBK", "Q_SERIES", "NX6008NBK", 180, 160)
    for p in pin(qs, name="G"):
        s.label(p, "QSERIES_G")
    for p in pin(qs, name="S"):
        s.power(p, "GND")
    for p in pin(qs, name="D"):
        s.label(p, "SERIES_NODE")
    _coil(s, 80, "UP", "Q_UP", "Q_CLAMP_UP", "K_UP", "R60", "R61", "D60")
    _coil(s, 20, "DN", "Q_DN", "Q_CLAMP_DN", "K_DN", "R70", "R71", "D70")
    # Presence detector on COIL_12
    two_pin(s, "Device:R", "R80", "100k", 250, 200, "COIL_12", "COIL_DIV")
    two_pin(s, "Device:R", "R81", "100k", 270, 200, "COIL_DIV", "GND")
    # Schottky clamp: cathode to +3V3 (pin 1 = K), anode to divider (pin 2 = A)
    two_pin(s, "Device:D_Schottky", "D80", "SCHOTTKY_CLAMP", 290, 200, "+3V3", "COIL_DIV")
    two_pin(s, "Device:R", "R82", "1k", 310, 200, "COIL_DIV", "COIL_RAIL_OK")
    s.note(
        20,
        100,
        "Presence detector: 100k/100k would sit at half the coil rail, so a Schottky to +3V3 clamps the GPIO.\\n"
        "At 12 V the clamp current is about (12-3.6)/100k = 84 uA. At 40 V it is about 0.36 mA. This detects 'rail present', it is not a voltmeter.\\n"
        "Timeout: Nexperia tW = K * REXT(kOhm) * CEXT(pF) nanoseconds, K nominal 1 for CEXT above 10 nF. 100k * 3.3 uF = 330 ms typical.\\n"
        "Long case, K=1.2 and capacitor +20 percent: about 475 ms. A static level cannot refresh it. Future firmware must edge GPIO1 at least every 100 ms.\\n"
        "The existing prototype firmware does not toggle GPIO1. With that image Q stays low and the coils stay off. Do not modify that firmware.\\n"
        "A future image must stop edges and drive both request pins low on STOP, comms loss, an invalid command, or TTL expiry. Those are two separate actions.\\n"
        "A stuck-high request with the main loop still running does not hold the coil, because a level on GPIO1 does not retrigger. Edges are allowed only while the RUN is valid.\\n"
        "The run-on after the last legal edge is one pulse: 330 ms typical, about 475 ms long case. Both request pins stuck is still blocked by the XOR.\\n"
        "Coil FETs are NX6008NBK: 60 V, RDS max 3 ohm at 2.5 V. Two in series drop about 0.25 V at 42 mA. Flyback is SS14, 1 A, 40 V, across each coil only.\\n"
        "The NO contact is in parallel with the Lofrans and hand controls. The SPDT NC pin is open. Unplugging these contacts leaves the original controls in place.\\n"
        "Do not install until the Lofrans control current and its inductive energy are measured and shown to be inside the Finder DC1 figure. DC13 life equals DC1 only if the load already has a diode, which is not assumed.",
    )


def _coil(s, y, tag, qref, cref, kref, rgate, rpull, dref):
    own = "UP_REQ" if tag == "UP" else "DN_REQ"
    other = "DN_REQ" if tag == "UP" else "UP_REQ"
    gate = f"{tag}_GATE"
    low = f"{tag}_LOW"
    com = f"{tag}_COM"
    no = f"{tag}_NO"
    two_pin(s, "Device:R", rgate, "10k", 40, y, own, gate)
    two_pin(s, "Device:R", rpull, "100k", 60, y, gate, "GND")
    clamp = s.place("Transistor_FET:2N7002", cref, "2N7002", 90, y, "Package_TO_SOT_SMD:SOT-23")
    for p in pin(clamp, name="G"):
        s.label(p, other)
    for p in pin(clamp, name="D"):
        s.label(p, gate)
    for p in pin(clamp, name="S"):
        s.power(p, "GND")
    fet = s.place("windlass:NX6008NBK", qref, "NX6008NBK", 130, y)
    connect_named(s, fet, {"G": gate, "D": low, "S": "SERIES_NODE"})
    k = s.place("Relay:Relay_SPDT", kref, "40.31.7.012.0000", 190, y)
    connect_named(s, k, {"A1": "COIL_12", "A2": low, "11": com, "14": no, "12": None})
    # Flyback across the coil only. Cathode at COIL_12, anode at the low side. Not a diode across the Lofrans load.
    two_pin(s, "windlass:DIODE_OPEN", dref, "SS14", 160, y + 18, "COIL_12", low)


def build_nmea(s: Sheet):
    s.note(
        20,
        250,
        "ISOLATED NMEA 2000. NOT FOR FABRICATION. No 120 ohm resistor is fitted or even placed.\\n"
        "GND_CAN is the ISO1042 side-2 ground and the DC-DC secondary return. It is not connected to GND.\\n"
        "NET-S has a connector pin and no PCB net. It is not a power source and not a return.\\n"
        "ISO1042 datasheet: bus pins are high-impedance when unpowered. The publish jumper defaults open, so VCC2 stays off\\n"
        "and this board does not bias or drive the bus. Fit the jumper only after the Waveshare transmitter is removed.\\n"
        "TXD has an external pull-up to +3V3 because the datasheet says the internal pull-up is too weak to guarantee recessive.",
    )
    # Publish switch
    jp = s.place("Jumper:Jumper_2_Open", "JP1", "Jumper_2_Open", 40, 190)
    connect_named(s, jp, {"A": "+3V3", "B": "PUBLISH_EN"})
    two_pin(s, "Device:R", "R90", "100k", 40, 165, "PUBLISH_EN", "GND")
    qn = s.place("Transistor_FET:2N7002", "Q90", "2N7002", 80, 170, "Package_TO_SOT_SMD:SOT-23")
    for p in pin(qn, name="G"):
        s.label(p, "PUBLISH_EN")
    for p in pin(qn, name="S"):
        s.power(p, "GND")
    for p in pin(qn, name="D"):
        s.label(p, "PUB_GATE")
    qp = s.place("Transistor_FET:DMP3099L", "Q91", "DMP3099L", 120, 180, "Package_TO_SOT_SMD:SOT-23")
    for p in pin(qp, name="S"):
        s.power(p, "+5V")
    for p in pin(qp, name="G"):
        s.label(p, "PUB_GATE")
    for p in pin(qp, name="D"):
        s.label(p, "CAN_VIN")
    two_pin(s, "Device:R", "R91", "100k", 120, 155, "PUB_GATE", "+5V")
    dcdc = s.place("windlass:MEJ2S", "U9", "MEJ2S0505SC", 180, 180)
    connect_named(s, dcdc, {"1": "CAN_VIN", "2": "GND", "7": "ISO_5V", "5": "GND_CAN"})
    # Q91 is a passive MOSFET. ERC cannot see it as a power source, so CAN_VIN
    # needs an explicit power flag. The flag sits on the stub already drawn to pin 1.
    vin = pin(dcdc, num="1")[0]
    dx, dy = outward(vin["ang"])
    s.flag(round(vin["ax"] + dx * 2.54, 4), round(vin["ay"] + dy * 2.54, 4))
    two_pin(s, "Device:R", "R94", "120_0.5W", 180, 145, "ISO_5V", "GND_CAN")
    two_pin(s, "Device:C", "C93", "100nF", 150, 145, "CAN_VIN", "GND")
    u = s.place("windlass:ISO1042BDWR", "U10", "ISO1042BDWR", 260, 160)
    connect_named(
        s,
        u,
        {
            "1": "+3V3",
            "2": "GND",
            "3": "TXD_NODE",
            "5": "TWAI_RX",
            "8": "GND",
            "16": "ISO_5V",
            "15": "GND_CAN",
            "13": "CAN_H",
            "12": "CAN_L",
            "11": "ISO_5V",
            "10": "ISO_5V",
            "9": "GND_CAN",
        },
    )
    two_pin(s, "Device:R", "R92", "10k", 220, 200, "TXD_NODE", "+3V3")
    two_pin(s, "Device:R", "R93", "33", 200, 140, "TWAI_TX", "TXD_NODE")
    two_pin(s, "Device:C", "C90", "100nF", 230, 130, "+3V3", "GND")
    two_pin(s, "Device:C", "C91", "100nF", 300, 180, "ISO_5V", "GND_CAN")
    # Shield cap to GND_CAN only. NET-S is intentionally absent here.
    # ISO_5V and GND_CAN are driven by the DC-DC power_out pins. No second PWR_FLAG.
    two_pin(s, "Device:C", "C92", "100nF", 320, 150, "NMEA_SHIELD", "GND_CAN")
    s.note(
        20,
        90,
        "ISO1042BDWR pin numbers are the DW-16 datasheet (VCC1=1, GND1=2, TXD=3, RXD=5, GND1=8, GND2=9,\\n"
        "VCC2=10 and 11 and 16 tied, CANL=12, CANH=13, GND2=15). NC pins 4, 6, 7, 14 are omitted from the symbol on purpose.\\n"
        "100 nF bypass on VCC1 and VCC2 matches the TI isolated-CAN reference (slla298). A bulk capacitor on VCC2 is OPEN.\\n"
        "U9 is Murata MEJ2S0505SC. Hipot 5.2 kVDC for 1 second. Murata says continuous barrier withstand is 2.4 kVDC and the part is functional isolation, not a safety barrier.\\n"
        "120 ohm preload is about 42 mA, just over 10 percent of the 400 mA rating, so the published tolerance envelope applies. 5 V plus 9 percent is 5.45 V, inside the ISO1042 4.5-5.5 V VCC2 range.\\n"
        "GND_CAN is not joined to REED_RET. C92, shield to GND_CAN, is 100 nF. Its working voltage must survive the barrier test and is a layout/part rating, not yet a placed voltage.\\n"
        "Q91 is DMP3099L, -30 V, -3.8 A. This circuit applies 5 V. Full-load primary current of the MEJ2S0505 is about 0.5 A.\\n"
        "33 ohm on TXD is a short series resistor for the logic edge. It is not a bus termination. No 120 ohm bus terminator is fitted.",
    )


def build_connectors(s: Sheet):
    s.note(
        20,
        260,
        "CONNECTORS rev 0.7. NOT FOR FABRICATION.\\n"
        "Six housings. Pins inside one housing are not joined. UP_RET is not DN_RET. REED_RET is not GND. GND_CAN is not GND.\\n"
        "J_PWR, J_CONTACT and J_PERM are 3.5 mm screw terminals. J_REED, J_SENSE and J_NMEA are latched JST XH, 3 A, not a sealed marine plug.\\n"
        "J_REED pin 2 and pin 4 are both REED_RET, so each cable has its own return wire. That is one net, not a second ground.\\n"
        "J_SENSE is a 5-pin XH. Pin 3 is unused so UP_RET and DN_FIELD are not adjacent. UP_RET is not DN_RET.\\n"
        "NET-S is pin 5 of J_NMEA and is a no-connect. Shield is not MCU ground.",
    )
    tb2 = "windlass:KF350-3.5-1x02"
    tb4 = "windlass:KF350-3.5-1x04"
    xh4 = "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
    xh5 = "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical"
    two_pin(s, "Connector_Generic:Conn_01x02", "J_PWR", "KF350-3.5-2P", 25, 210, "VIN_12", "GND", tb2)
    multi_pin(
        s, "Connector_Generic:Conn_01x04", "J_CONTACT", "KF350-3.5-4P", 70, 210,
        ["UP_COM", "UP_NO", "DN_COM", "DN_NO"], tb4,
    )
    multi_pin(
        s, "Connector_Generic:Conn_01x04", "J_PERM", "KF350-3.5-4P", 120, 210,
        ["SW_A", "SW_B", "IGN_A", "IGN_B"], tb4,
    )
    # +12V_COIL -> SW_A, SW_B -> IGN_A. IGN_B is consumed by R_COILFEED on the relay sheet.
    two_pin(s, "Device:R", "R_SWLINK", "0", 150, 210, "+12V_COIL", "SW_A")
    two_pin(s, "Device:R", "R_IGNLINK", "0", 175, 210, "SW_B", "IGN_A")
    multi_pin(
        s, "Connector_Generic:Conn_01x04", "J_REED", "B4B-XH-A(LF)(SN)", 25, 150,
        ["REED_SIG", "REED_RET", "DRY_A", "REED_RET"], xh4,
    )
    multi_pin(
        s, "Connector_Generic:Conn_01x05", "J_SENSE", "B5B-XH-A(LF)(SN)", 80, 150,
        ["UP_FIELD", "UP_RET", None, "DN_FIELD", "DN_RET"], xh5,
    )
    multi_pin(
        s, "Connector_Generic:Conn_01x05", "J_NMEA", "B5B-XH-A(LF)(SN)", 140, 150,
        ["GND_CAN", "CAN_L", "NMEA_SHIELD", "CAN_H", None], xh5,
    )
    s.note(
        200,
        145,
        "J_NMEA pin order is the PCB header, not a Micro-C. Pigtail to a drop plug:\\n"
        "1 GND_CAN -> NET-C (black). 2 CAN_L -> NET-L (blue). 3 SHIELD -> shield, capacitor to GND_CAN only.\\n"
        "4 CAN_H -> NET-H (white). 5 NET-S is open on this PCB. Do not land the red wire. This board does not draw backbone power.",
    )
    # Red and yellow-green: GPIO high, 680 ohm, cathode to GND. Device:LED pin 1 = K, pin 2 = A.
    _led(s, 40, 80, "LED_R", "D_R", "R_R", "680", "LTST-C190KRKT")
    _led(s, 90, 80, "LED_G", "D_G", "R_G", "680", "LTST-C190KGKT")
    two_pin(s, "Device:R", "R_RPD", "100k", 40, 60, "LED_R", "GND")
    two_pin(s, "Device:R", "R_GPD", "100k", 90, 60, "LED_G", "GND")
    # Blue: +5V, 1k, LED, 2N7002BK drain. Gate is LED_B. Source is GND. No DC path from +5V to the GPIO.
    two_pin(s, "Device:R", "R_B", "1k", 140, 80, "+5V", "LED_B_A")
    bled = s.place("Device:LED", "D_B", "LTST-C190TBKT", 165, 80, "LED_SMD:LED_0603_1608Metric")
    bb = {p["num"]: p for p in bled}
    s.label(bb["2"], "LED_B_A")
    s.label(bb["1"], "LED_B_K")
    qled = s.place("Transistor_FET:2N7002", "Q_LED", "2N7002BK,215", 190, 80, "Package_TO_SOT_SMD:SOT-23")
    for p in pin(qled, name="G"):
        s.label(p, "LED_B")
    for p in pin(qled, name="D"):
        s.label(p, "LED_B_K")
    for p in pin(qled, name="S"):
        s.power(p, "GND")
    two_pin(s, "Device:R", "R_BPD", "100k", 165, 60, "LED_B", "GND")
    s.note(
        20,
        40,
        "Three discrete 0603 LEDs. Amber is D_R and D_G both on. This is not a single RGB package.\\n"
        "D_R is Lite-On LTST-C190KRKT, red. D_G is Lite-On LTST-C190KGKT, yellow-green, 567 to 576 nm. Both list Vf 2.4 V max at 20 mA, so 3.3 V lights them.\\n"
        "680 ohm from 3.3 V is about 1.9 mA at Vf 2.0 V and about 1.3 mA at Vf 2.4 V. R_RPD and R_GPD hold the GPIO side low until firmware drives it.\\n"
        "D_B is Lite-On LTST-C190TBKT, 465 to 475 nm, Vf 2.8 to 3.8 V at 20 mA. It is not on a GPIO.\\n"
        "R_B is 1k from +5V to the anode. The cathode is the drain of Q_LED, a 2N7002BK. The source is GND. The gate is LED_B, GPIO17, with R_BPD 100k to GND.\\n"
        "The drain can sit near 5 V while the FET is off. The gate has no DC connection to the drain or to +5V, so the GPIO cannot be pulled to 5 V.\\n"
        "1k from 5 V is about 1.7 mA at Vf 3.3 V and about 1.2 mA at the 3.8 V maximum, so the lamp still lights at the top of the Vf range.\\n"
        "Indication, highest first: solid red fault, flashing blue pairing, amber when controls are disabled, solid green when ready.\\n"
        "The prototype firmware does not drive GPIO15, GPIO16 or GPIO17. The pulldowns hold the lamps off. That firmware is not modified.\\n"
        "R_SWLINK and R_IGNLINK are 0 ohm records of the coil-only series loop. They are fed from +12V_COIL, not from +12V_MCU. Delete neither.\\n"
        "J_REED pin 1 is the Lofrans signal and pin 3 is the standalone contact. Do not fit both sources at once.\\n"
        "Existing Lofrans and hand-remote contacts stay in parallel at UP_COM/UP_NO and DN_COM/DN_NO. This board does not sit in series with them.",
    )


def _led(s, x, y, net, dref, rref, rval, value):
    two_pin(s, "Device:R", rref, rval, x, y, net, f"{net}_A")
    led = s.place("Device:LED", dref, value, x + 25, y, "LED_SMD:LED_0603_1608Metric")
    by = {p["num"]: p for p in led}
    s.label(by["2"], f"{net}_A")  # anode
    s.power(by["1"], "GND")       # cathode


def build_root(folder: Path):
    sheets = []
    x = 30
    for i, name in enumerate(SHEET_IDS, start=2):
        y = 250 - (i - 2) * 28
        sheets.append(
            f'''(sheet (at {x} {y}) (size 120 18)
  (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
  (stroke (width 0.254) (type solid)) (fill (color 0 0 0 0.0))
  (uuid "{SHEET_IDS[name]}")
  (property "Sheetname" "{name}" (at {x} {y + 16} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.524 1.524)) (justify left bottom)))
  (property "Sheetfile" "{name}.kicad_sch" (at {x} {y + 1} 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)) (justify left top)))
  (instances (project "{PROJECT}" (path "/{ROOT_UUID}" (page "{i}"))))
)'''
        )
    note = (
        "WINDLASS CONTROLLER  rev 0.7   NOT FOR FABRICATION\\n"
        "Grounds that are NOT joined on this PCB:\\n"
        "  GND      board 12 V return, ESP32, coil drivers, USB shield network\\n"
        "  UP_RET   UP sense opto return only\\n"
        "  DN_RET   DOWN sense opto return only\\n"
        "  REED_RET reed isolator field ground only\\n"
        "  GND_CAN  NMEA side-2 / NET-C only\\n"
        "  NET-S    connector pin, no copper net\\n"
        "Dry contacts UP_COM/UP_NO and DN_COM/DN_NO are not grounded.\\n"
        "KiCad ERC is not a substitute for the Lofrans wiring check or for thermal sign-off."
    )
    text = f'''(kicad_sch
  (version {VERSION})
  (generator "windlass_build_schematic")
  (generator_version "1")
  (uuid "{ROOT_UUID}")
  (paper "A3")
  (title_block (title "Windlass controller") (date "2026-11-19") (rev "0.7-not-for-fabrication") (comment 1 "NOT FOR FABRICATION"))
  (lib_symbols)
  {''.join(sheets)}
  (text "{note}" (at 160 240 0) (effects (font (size 1.27 1.27))) (uuid "{uid()}"))
  (sheet_instances (path "/" (page "1")))
  (embedded_fonts no)
)
'''
    (folder / "windlass.kicad_sch").write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheets = {name: Sheet(name) for name in SHEET_IDS}
    build_power(sheets["power"])
    build_esp(sheets["esp32"])
    build_reed(sheets["reed"])
    build_direction(sheets["direction_sense"])
    build_relay(sheets["relay_control_and_interlock"])
    build_nmea(sheets["isolated_nmea2000"])
    build_connectors(sheets["connectors_status_service"])
    for sh in sheets.values():
        sh.save(OUT)
    parts = []
    for lib_id, sexpr in LOCAL_SYMBOLS.items():
        leaf = lib_id.split(":")[-1]
        parts.append(sexpr.replace(f'(symbol "{lib_id}"', f'(symbol "{leaf}"', 1))
    lib = (
        '(kicad_symbol_lib\n'
        '  (version 20251024)\n'
        '  (generator "windlass_build_schematic")\n'
        '  (generator_version "1")\n'
        + "\n".join(parts)
        + "\n)\n"
    )
    (OUT / "windlass.kicad_sym").write_text(lib, encoding="utf-8")
    build_root(OUT)
    pro = OUT / "windlass.kicad_pro"
    if not pro.exists():
        pro.write_text(
            '{\n  "meta": {"filename": "windlass.kicad_pro", "version": 3},\n'
            '  "sheets": [],\n  "text_variables": {},\n'
            '  "schematic": {"legacy_lib_dir": "", "legacy_lib_names": []}\n}\n',
            encoding="utf-8",
        )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
