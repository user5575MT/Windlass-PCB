#!/usr/bin/env python3
"""Through-hole home-assembly schematic. Does not touch the v2 board.

One CD74HCT14E is the watchdog. A 74HCT123 is not fitted: with CEXT above
10 nF the Nexperia retrigger interval is about 0.42 of the pulse, so an
80 ms heartbeat cannot keep a 330 ms 74HCT123 alive.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_schematic as bs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "kicad_home"
bs.LIBROOT = Path("/usr/share/kicad/symbols")
bs.PROJECT = "windlass_home"
bs.ROOT_UUID = "b1e0a001-0000-4000-8000-000000000001"
bs.SHEET_IDS["home"] = bs.ROOT_UUID

FP = {
    "r": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical",
    "r1w": "Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal",
    "c": "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
    "cfilm": "Capacitor_THT:C_Rect_L13.0mm_W6.0mm_P10.00mm_FKS3_FKP3_MKS4",
    "cp": "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm",
    "cp10": "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
    "d": "Diode_THT:D_DO-41_SOD81_P5.08mm_Vertical_CathodeUp",
    "dz": "Diode_THT:D_DO-35_SOD27_P5.08mm_Vertical_CathodeUp",
    "q": "Package_TO_SOT_THT:TO-92_Inline",
    "fet": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "dip14": "Package_DIP:DIP-14_W7.62mm",
    "dip8": "Package_DIP:DIP-8_W7.62mm",
    "dip4": "Package_DIP:DIP-4_W7.62mm",
    "led": "LED_THT:LED_D5.0mm",
    "fuse": "Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open",
    "oki": "Converter_DCDC:Converter_DCDC_Murata_OKI-78SR_Horizontal",
    "mej": "windlass:Murata_MEJ2SxxxxSC",
    "relay": "Relay_THT:Relay_SPDT_Finder_40.31",
    "sock": "Connector_PinSocket_2.54mm:PinSocket_1x22_P2.54mm_Vertical",
    "kf2": "windlass:KF350-3.5-1x02",
    "kf4": "windlass:KF350-3.5-1x04",
    "xh4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
    "xh5": "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical",
    "jp2": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
    "jp3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
}


def add_symbol(lib_id, ref, value, description, pins, width):
    bs.LOCAL_SYMBOLS[lib_id] = bs.local_rect_symbol(
        lib_id, ref, value, description, pins, width
    )


add_symbol(
    "windlass:CD74HCT14E",
    "U",
    "CD74HCT14E",
    "TI CD74HCT14E, hex Schmitt inverter, DIP-14. TTL thresholds so an ESP32 high is a legal input.",
    [
        ("1", "1A", "input", "L"),
        ("3", "2A", "input", "L"),
        ("5", "3A", "input", "L"),
        ("9", "4A", "input", "L"),
        ("11", "5A", "input", "L"),
        ("13", "6A", "input", "L"),
        ("2", "1Y", "output", "R"),
        ("4", "2Y", "output", "R"),
        ("6", "3Y", "output", "R"),
        ("8", "4Y", "output", "R"),
        ("10", "5Y", "output", "R"),
        ("12", "6Y", "output", "R"),
        ("14", "VCC", "power_in", "T"),
        ("7", "GND", "power_in", "B"),
    ],
    17.78,
)
add_symbol(
    "windlass:CD74HCT125E",
    "U",
    "CD74HCT125E",
    "TI CD74HCT125E, quad 3-state buffer, DIP-14. OE is active low. Output high is about 4.4 V, which is a legal IRLZ44N gate drive.",
    [
        ("1", "1OE", "input", "L"),
        ("2", "1A", "input", "L"),
        ("4", "2OE", "input", "L"),
        ("5", "2A", "input", "L"),
        ("10", "3OE", "input", "L"),
        ("9", "3A", "input", "L"),
        ("13", "4OE", "input", "L"),
        ("12", "4A", "input", "L"),
        ("3", "1Y", "output", "R"),
        ("6", "2Y", "output", "R"),
        ("8", "3Y", "output", "R"),
        ("11", "4Y", "output", "R"),
        ("14", "VCC", "power_in", "T"),
        ("7", "GND", "power_in", "B"),
    ],
    20.32,
)
add_symbol(
    "windlass:SN74HC00N",
    "U",
    "SN74HC00N",
    "TI SN74HC00N, quad NAND, DIP-14. Runs from the DevKit 3.3 V pin. Not an HCT part.",
    [
        ("1", "1A", "input", "L"),
        ("2", "1B", "input", "L"),
        ("4", "2A", "input", "L"),
        ("5", "2B", "input", "L"),
        ("10", "3B", "input", "L"),
        ("9", "3A", "input", "L"),
        ("13", "4B", "input", "L"),
        ("12", "4A", "input", "L"),
        ("3", "1Y", "output", "R"),
        ("6", "2Y", "output", "R"),
        ("8", "3Y", "output", "R"),
        ("11", "4Y", "output", "R"),
        ("14", "VCC", "power_in", "T"),
        ("7", "GND", "power_in", "B"),
    ],
    20.32,
)
add_symbol(
    "windlass:SN74HC08N",
    "U",
    "SN74HC08N",
    "TI SN74HC08N, quad AND, DIP-14. Runs from the DevKit 3.3 V pin. One gate is the reed blanker output.",
    [
        ("1", "1A", "input", "L"),
        ("2", "1B", "input", "L"),
        ("4", "2A", "input", "L"),
        ("5", "2B", "input", "L"),
        ("10", "3B", "input", "L"),
        ("9", "3A", "input", "L"),
        ("13", "4B", "input", "L"),
        ("12", "4A", "input", "L"),
        ("3", "1Y", "output", "R"),
        ("6", "2Y", "output", "R"),
        ("8", "3Y", "output", "R"),
        ("11", "4Y", "output", "R"),
        ("14", "VCC", "power_in", "T"),
        ("7", "GND", "power_in", "B"),
    ],
    20.32,
)
add_symbol(
    "windlass:MCP2562-E-P",
    "U",
    "MCP2562-E/P",
    "Microchip MCP2562-E/P DIP-8. Pin 5 is SPLIT, not VIO. SPLIT is left open. STBY is held low. Logic is the isolated 5 V rail.",
    [
        ("1", "TXD", "input", "L"),
        ("2", "VSS", "power_in", "L"),
        ("3", "VDD", "power_in", "L"),
        ("8", "STBY", "input", "L"),
        ("4", "RXD", "output", "R"),
        ("5", "SPLIT", "passive", "R"),
        ("6", "CANL", "bidirectional", "R"),
        ("7", "CANH", "bidirectional", "R"),
    ],
    12.7,
)
add_symbol(
    "windlass:MEJ2S",
    "U",
    "MEJ2",
    "Murata MEJ2 single-output SIP. Pins 1 +Vin, 2 -Vin, 5 -Vout, 7 +Vout. Pin 6 is not fitted.",
    [
        ("1", "+Vin", "power_in", "L"),
        ("2", "-Vin", "power_in", "L"),
        ("7", "+Vout", "power_out", "R"),
        ("5", "-Vout", "power_in", "R"),
    ],
    10.16,
)


def cell(c, r):
    return bs.on_grid(30 + c * 55), bs.on_grid(30 + r * 38)


def build() -> bs.Sheet:
    s = bs.Sheet("home")
    s.path = "/"
    s.note(
        20,
        20,
        "WINDLASS HOME ASSEMBLY. Through-hole and plug-in modules only. 100 x 100 mm, two layers.\\n"
        "The v2 board and the firmware are unchanged. GPIO numbers are the existing map.\\n"
        "Watchdog is one CD74HCT14E. A 74HCT123 is not used: once CEXT is above 10 nF the retrigger\\n"
        "gap is about 0.42 of the pulse, so an 80 ms heartbeat cannot hold a 330 ms HCT123 high.\\n"
        "Isolation is functional. REED_RET, UP_RET, DN_RET and GND_CAN do not join GND or each other.\\n"
        "Relay contacts are dry and independent. Commons are not tied. Do not order from this sheet\\n"
        "until the first board has been measured.",
    )

    # Flags for rails that have no power_out pin of their own.
    # Flags sit on an empty corner. A flag on top of a pin stub joins those nets.
    s.flag(20, 560, "GND")
    s.flag(40, 560, "+3V3")
    s.flag(60, 560, "+12V_MCU")
    s.flag(80, 560, "REED_RET")
    s.flag(100, 560, "GND_CAN")
    # CAN_VIN is power_in on the far side of the open publish jumper. The flag
    # marks the net as driven when that jumper is fitted. Open, R90 holds it low.
    s.flag(120, 560, "CAN_VIN")

    # --- 12 V input, two branches ---
    bs.multi_pin(s, "Connector_Generic:Conn_01x02", "J_PWR", "KF350-3.5-2P", *cell(0, 0), ["VIN_12", "GND"], FP["kf2"])
    bs.two_pin(s, "Device:Fuse", "F_MCU", "0217002.HXP", *cell(0, 1), "VIN_12", "VIN_MCU", FP["fuse"])
    bs.two_pin(s, "Device:D", "D_TVS_MCU", "P6KE18A", *cell(0, 2), "VIN_MCU", "GND", FP["d"])
    q = s.place("Transistor_FET:IRF9540N", "Q_MCU", "IRF9540NPBF", *cell(1, 0), FP["fet"])
    bs.connect_named(s, q, {"D": "VIN_MCU", "S": "+12V_MCU", "G": "QMCU_G"})
    bs.two_pin(s, "Device:R", "R_MCU_G", "100k", *cell(1, 1), "QMCU_G", "GND", FP["r"])
    bs.two_pin(s, "Device:D", "D_Z_MCU", "BZX55C12", *cell(1, 2), "+12V_MCU", "QMCU_G", FP["dz"])
    bs.two_pin(s, "Device:C_Polarized", "C_IN", "10uF_50V", *cell(1, 3), "+12V_MCU", "GND", FP["cp10"])

    bs.two_pin(s, "Device:Fuse", "F_COIL", "0235.250HXP", *cell(0, 3), "VIN_12", "VIN_COIL", FP["fuse"])
    bs.two_pin(s, "Device:D", "D_TVS_COIL", "P6KE18A", *cell(0, 4), "VIN_COIL", "GND", FP["d"])
    q = s.place("Transistor_FET:IRF9540N", "Q_COIL", "IRF9540NPBF", *cell(1, 4), FP["fet"])
    bs.connect_named(s, q, {"D": "VIN_COIL", "S": "+12V_COIL", "G": "QCOIL_G"})
    bs.two_pin(s, "Device:R", "R_COIL_G", "100k", *cell(2, 0), "QCOIL_G", "GND", FP["r"])
    bs.two_pin(s, "Device:D", "D_Z_COIL", "BZX55C12", *cell(2, 1), "+12V_COIL", "QCOIL_G", FP["dz"])

    u = s.place("Converter_DCDC:OKI-78SR-5_1.5-W36H-C", "U20", "OKI-78SR-5/1.5-W36H-C", *cell(2, 2), FP["oki"])
    bs.connect_named(s, u, {"IN": "+12V_MCU", "GND": "GND", "OUT": "+5V"})
    bs.two_pin(s, "Device:C_Polarized", "C_5V", "10uF_25V", *cell(2, 3), "+5V", "GND", FP["cp"])
    bs.two_pin(s, "Device:C", "C_5VHF", "100nF", *cell(2, 4), "+5V", "GND", FP["c"])
    # Anode is pin 2, cathode is pin 1. Current flows from +5V into the DevKit only.
    bs.two_pin(s, "Diode:1N5817", "D_DEV", "1N5817", *cell(3, 0), "DEV_5V", "+5V", FP["d"])
    bs.two_pin(s, "Device:C_Polarized", "C_DEV", "10uF_25V", *cell(3, 1), "DEV_5V", "GND", FP["cp"])

    # --- DevKit sockets. Pin 1 of both headers is the USB end, opposite the antenna. ---
    j1 = {
        "1": "+3V3", "2": "+3V3", "4": "GPIO4", "5": "GPIO5", "6": "GPIO6",
        "7": "GPIO7", "8": "GPIO15", "9": "GPIO16", "11": "GPIO18", "12": "GPIO8",
        "15": "GPIO9", "16": "GPIO10", "20": "GPIO14", "21": "DEV_5V", "22": "GND",
    }
    j3 = {"1": "GND", "4": "GPIO1", "21": "GND", "22": "GND"}
    bs.connect_named(
        s,
        s.place("Connector_Generic:Conn_01x22", "J1", "DevKitC_J1", *cell(0, 6), FP["sock"]),
        j1,
    )
    bs.connect_named(
        s,
        s.place("Connector_Generic:Conn_01x22", "J3", "DevKitC_J3", *cell(1, 6), FP["sock"]),
        j3,
    )
    bs.two_pin(s, "Device:C", "C_3V3", "100nF", *cell(3, 2), "+3V3", "GND", FP["c"])
    bs.two_pin(s, "Device:C_Polarized", "C_3V3B", "10uF_16V", *cell(3, 3), "+3V3", "GND", FP["cp"])

    # --- Watchdog: missing-pulse detector, one HCT14 ---
    u = s.place("windlass:CD74HCT14E", "U12", "CD74HCT14E", *cell(4, 0), FP["dip14"])
    bs.connect_named(
        s,
        u,
        {
            "1A": "GPIO1",
            "1Y": "HB_N",
            "2A": "EDGE",
            "2Y": "DISCH",
            "3A": "TIME",
            "3Y": "WDI_Q",
            "4A": "GND",
            "5A": "GND",
            "6A": "GND",
            "VCC": "+5V",
            "GND": "GND",
        },
    )
    bs.two_pin(s, "Device:R", "R_HB", "100k", *cell(4, 2), "GPIO1", "GND", FP["r"])
    bs.two_pin(s, "Device:R", "R_EDGE", "330", *cell(4, 3), "HB_N", "EDGE_R", FP["r"])
    bs.two_pin(s, "Device:C", "C_EDGE", "220nF", *cell(5, 0), "EDGE_R", "EDGE", FP["c"])
    bs.two_pin(s, "Device:R", "R_EDGE_PU", "10k", *cell(5, 1), "EDGE", "+5V", FP["r"])
    bs.two_pin(s, "Device:R", "R_BASE", "1k", *cell(5, 2), "DISCH", "DISCH_B", FP["r"])
    q = s.place("Transistor_BJT:BC547", "Q_DIS", "BC547B", *cell(5, 3), FP["q"])
    bs.connect_named(s, q, {"B": "DISCH_B", "C": "TIME", "E": "GND"})
    bs.two_pin(s, "Device:R", "R_TIME", "470k", *cell(5, 4), "+5V", "TIME", FP["r"])
    bs.two_pin(s, "Device:C", "C_TIME", "2.2uF", *cell(6, 0), "TIME", "GND", FP["cfilm"])
    bs.two_pin(s, "Device:C", "C_U12", "100nF", *cell(6, 1), "+5V", "GND", FP["c"])
    bs.two_pin(s, "Device:R", "R50", "470", *cell(6, 2), "WDI_Q", "WDI_GATE", FP["r"])
    bs.two_pin(s, "Device:R", "R_SER_PD", "100k", *cell(6, 3), "WDI_GATE", "GND", FP["r"])

    # --- Request buffers and coil FETs ---
    u = s.place("windlass:CD74HCT125E", "U15", "CD74HCT125E", *cell(7, 0), FP["dip14"])
    bs.connect_named(
        s,
        u,
        {
            "1OE": "GND",
            "1A": "GPIO9",
            "1Y": "UP_DRV",
            "2OE": "GND",
            "2A": "GPIO10",
            "2Y": "DN_DRV",
            "3OE": "+5V",
            "3A": "GND",
            "4OE": "+5V",
            "4A": "GND",
            "VCC": "+5V",
            "GND": "GND",
        },
    )
    bs.two_pin(s, "Device:C", "C_U15", "100nF", *cell(7, 2), "+5V", "GND", FP["c"])
    bs.two_pin(s, "Device:R", "R13", "100k", *cell(7, 3), "GPIO9", "GND", FP["r"])
    bs.two_pin(s, "Device:R", "R14", "100k", *cell(7, 4), "GPIO10", "GND", FP["r"])
    bs.two_pin(s, "Device:R", "R60", "470", *cell(8, 0), "UP_DRV", "UP_GATE", FP["r"])
    bs.two_pin(s, "Device:R", "R61", "100k", *cell(8, 1), "UP_GATE", "GND", FP["r"])
    bs.two_pin(s, "Device:R", "R70", "470", *cell(8, 2), "DN_DRV", "DN_GATE", FP["r"])
    bs.two_pin(s, "Device:R", "R71", "100k", *cell(8, 3), "DN_GATE", "GND", FP["r"])
    # Opposite request clamps the other gate. Both high holds both gates off.
    bs.two_pin(s, "Device:R", "R_CL_UP", "4.7k", *cell(8, 4), "DN_DRV", "CLUP_B", FP["r"])
    bs.two_pin(s, "Device:R", "R_CL_DN", "4.7k", *cell(9, 0), "UP_DRV", "CLDN_B", FP["r"])
    q = s.place("Transistor_BJT:BC547", "Q_CL_UP", "BC547B", *cell(9, 1), FP["q"])
    bs.connect_named(s, q, {"B": "CLUP_B", "C": "UP_GATE", "E": "GND"})
    q = s.place("Transistor_BJT:BC547", "Q_CL_DN", "BC547B", *cell(9, 2), FP["q"])
    bs.connect_named(s, q, {"B": "CLDN_B", "C": "DN_GATE", "E": "GND"})

    for ref, gate, drain in (
        ("Q_UP", "UP_GATE", "UP_LOW"),
        ("Q_DN", "DN_GATE", "DN_LOW"),
    ):
        q = s.place("Transistor_FET:IRLZ44N", ref, "IRLZ44NPBF", *cell(9, 3 if ref == "Q_UP" else 4), FP["fet"])
        bs.connect_named(s, q, {"G": gate, "D": drain, "S": "SERIES_DRAIN"})
    q = s.place("Transistor_FET:IRLZ44N", "Q_SERIES", "IRLZ44NPBF", *cell(10, 0), FP["fet"])
    bs.connect_named(s, q, {"G": "WDI_GATE", "D": "SERIES_DRAIN", "S": "GND"})
    bs.two_pin(s, "Diode:1N5819", "D60", "1N5819", *cell(10, 1), "COIL_12", "UP_LOW", FP["d"])
    bs.two_pin(s, "Diode:1N5819", "D70", "1N5819", *cell(10, 2), "COIL_12", "DN_LOW", FP["d"])

    k = s.place("Relay:Relay_SPDT", "K_UP", "40.31.7.012.0000", *cell(10, 3), FP["relay"])
    bs.connect_named(s, k, {"A1": "COIL_12", "A2": "UP_LOW", "11": "UP_COM", "14": "UP_NO"})
    k = s.place("Relay:Relay_SPDT", "K_DN", "40.31.7.012.0000", *cell(10, 4), FP["relay"])
    bs.connect_named(s, k, {"A1": "COIL_12", "A2": "DN_LOW", "11": "DN_COM", "14": "DN_NO"})

    bs.multi_pin(
        s, "Connector_Generic:Conn_01x04", "J_PERM", "KF350-3.5-4P", *cell(11, 0),
        ["+12V_COIL", "SW_LINK", "SW_LINK", "COIL_12"], FP["kf4"],
    )
    bs.multi_pin(
        s, "Connector_Generic:Conn_01x04", "J_CONTACT", "KF350-3.5-4P", *cell(11, 1),
        ["UP_COM", "UP_NO", "DN_COM", "DN_NO"], FP["kf4"],
    )
    bs.two_pin(s, "Device:R", "R80", "100k", *cell(11, 2), "COIL_12", "COIL_DIV", FP["r"])
    bs.two_pin(s, "Device:R", "R81", "100k", *cell(11, 3), "COIL_DIV", "GND", FP["r"])
    bs.two_pin(s, "Diode:BAT46", "D80", "BAT46", *cell(11, 4), "+3V3", "COIL_DIV", FP["dz"])
    bs.two_pin(s, "Device:R", "R82", "1k", *cell(12, 0), "COIL_DIV", "GPIO14", FP["r"])

    # LEDs, sourced by the GPIO. High lights the lamp.
    bs.two_pin(s, "Device:R", "R_R", "680", *cell(12, 1), "GPIO15", "LED_R", FP["r"])
    bs.two_pin(s, "Device:LED", "D_R", "RED", *cell(12, 2), "GND", "LED_R", FP["led"])
    bs.two_pin(s, "Device:R", "R_G", "680", *cell(12, 3), "GPIO16", "LED_G", FP["r"])
    bs.two_pin(s, "Device:LED", "D_G", "GREEN", *cell(12, 4), "GND", "LED_G", FP["led"])

    # --- Reed, isolated side ---
    u = s.place("windlass:MEJ2S", "U4", "MEJ2S0503SC", *cell(0, 8), FP["mej"])
    bs.connect_named(s, u, {"+Vin": "+5V", "-Vin": "GND", "+Vout": "REED_3V3", "-Vout": "REED_RET"})
    bs.two_pin(s, "Device:R", "R24", "51", *cell(1, 8), "REED_3V3", "REED_RET", FP["r1w"])
    bs.two_pin(s, "Device:C_Polarized", "C_REED", "10uF_16V", *cell(2, 8), "REED_3V3", "REED_RET", FP["cp"])
    bs.multi_pin(
        s, "Connector_Generic:Conn_01x04", "J_REED", "B4B-XH-A", *cell(3, 8),
        ["REED_SIG", "REED_RET", "DRY_A", "REED_RET"], FP["xh4"],
    )
    jp = s.place("Jumper:Jumper_3_Bridged12", "JP_REED", "1x03", *cell(4, 8), FP["jp3"])
    bs.connect_named(s, jp, {"A": "LOFRANS_NODE", "C": "REED_ISO", "B": "DRY_A"})
    bs.two_pin(s, "Device:R", "R20", "10k", *cell(5, 8), "REED_SIG", "LOFRANS_NODE", FP["r"])
    bs.two_pin(s, "Device:R", "R23", "47k", *cell(6, 8), "REED_ISO", "REED_RET", FP["r"])
    bs.two_pin(s, "Device:R", "R22", "4.7k", *cell(7, 8), "REED_3V3", "DRY_A", FP["r"])
    bs.two_pin(s, "Diode:BAT46", "D20", "BAT46", *cell(8, 8), "REED_3V3", "LOFRANS_NODE", FP["dz"])
    bs.two_pin(s, "Diode:BAT46", "D21", "BAT46", *cell(9, 8), "LOFRANS_NODE", "REED_RET", FP["dz"])
    q = s.place("Transistor_BJT:BC557", "Q_REED", "BC557B", *cell(10, 8), FP["q"])
    bs.connect_named(s, q, {"E": "REED_3V3", "B": "REED_B", "C": "REED_C"})
    bs.two_pin(s, "Device:R", "R_REED_B", "47k", *cell(11, 8), "REED_ISO", "REED_B", FP["r"])
    bs.two_pin(s, "Device:R", "R_REED_C", "1k", *cell(12, 8), "REED_C", "RD_A", FP["r"])
    u = s.place("Isolator:PC817", "U_RD", "PC817", *cell(13, 6), FP["dip4"])
    bs.connect_named(s, u, {"1": "RD_A", "2": "REED_RET", "3": "GND", "4": "REED_DATA"})
    bs.two_pin(s, "Device:R", "R_DATA", "10k", *cell(13, 7), "+3V3", "REED_DATA", FP["r"])
    bs.two_pin(s, "Device:R", "R_PG", "1k", *cell(13, 8), "REED_3V3", "PG_A", FP["r"])
    u = s.place("Isolator:PC817", "U_PG", "PC817", *cell(14, 6), FP["dip4"])
    bs.connect_named(s, u, {"1": "PG_A", "2": "REED_RET", "3": "GND", "4": "PG_N"})
    bs.two_pin(s, "Device:R", "R_PGPU", "10k", *cell(14, 7), "+3V3", "PG_N", FP["r"])

    # Blanker. BLOCKED sets while the field rail is down and clears only on a real low.
    u = s.place("windlass:SN74HC00N", "U16", "SN74HC00N", *cell(4, 6), FP["dip14"])
    bs.connect_named(
        s,
        u,
        {
            "1A": "PG_N",
            "1B": "PG_N",
            "1Y": "PG",
            "2A": "PG",
            "2B": "NOT_DATA",
            "2Y": "NR",
            "3A": "PG",
            "3B": "NQ",
            "3Y": "BLOCKED",
            "4A": "NR",
            "4B": "BLOCKED",
            "4Y": "NQ",
            "VCC": "+3V3",
            "GND": "GND",
        },
    )
    q = s.place("Transistor_BJT:BC547", "Q_INV", "BC547B", *cell(5, 6), FP["q"])
    bs.connect_named(s, q, {"B": "INV_B", "C": "NOT_DATA", "E": "GND"})
    bs.two_pin(s, "Device:R", "R_INV_B", "100k", *cell(5, 7), "REED_DATA", "INV_B", FP["r"])
    bs.two_pin(s, "Device:R", "R_INV_C", "10k", *cell(6, 6), "+3V3", "NOT_DATA", FP["r"])
    u = s.place("windlass:SN74HC08N", "U17", "SN74HC08N", *cell(6, 7), FP["dip14"])
    bs.connect_named(
        s,
        u,
        {
            "1A": "REED_DATA",
            "1B": "NQ",
            "1Y": "GPIO6",
            "2A": "GND",
            "2B": "GND",
            "3A": "GND",
            "3B": "GND",
            "4A": "GND",
            "4B": "GND",
            "VCC": "+3V3",
            "GND": "GND",
        },
    )
    bs.two_pin(s, "Device:C", "C_U16", "100nF", *cell(3, 6), "+3V3", "GND", FP["c"])
    bs.two_pin(s, "Device:C", "C_U17", "100nF", *cell(3, 7), "+3V3", "GND", FP["c"])

    # --- Direction sense. Returns stay separate. Active low into the MCU. ---
    bs.multi_pin(
        s, "Connector_Generic:Conn_01x05", "J_SENSE", "B5B-XH-A", *cell(8, 6),
        ["UP_FIELD", "UP_RET", None, "DN_FIELD", "DN_RET"], FP["xh5"],
    )
    bs.two_pin(s, "Device:R", "R30", "4.7k", *cell(9, 6), "UP_FIELD", "UP_LED", FP["r"])
    u = s.place("Isolator:PC817", "U6", "PC817", *cell(9, 7), FP["dip4"])
    bs.connect_named(s, u, {"1": "UP_LED", "2": "UP_RET", "3": "GND", "4": "GPIO7"})
    bs.two_pin(s, "Diode:1N4148", "D30", "1N4148", *cell(10, 6), "UP_LED", "UP_RET", FP["d"])
    bs.two_pin(s, "Device:R", "R31", "10k", *cell(10, 7), "+3V3", "GPIO7", FP["r"])
    bs.two_pin(s, "Device:R", "R40", "4.7k", *cell(11, 6), "DN_FIELD", "DN_LED", FP["r"])
    u = s.place("Isolator:PC817", "U7", "PC817", *cell(11, 7), FP["dip4"])
    bs.connect_named(s, u, {"1": "DN_LED", "2": "DN_RET", "3": "GND", "4": "GPIO8"})
    bs.two_pin(s, "Diode:1N4148", "D40", "1N4148", *cell(12, 6), "DN_LED", "DN_RET", FP["d"])
    bs.two_pin(s, "Device:R", "R41", "10k", *cell(12, 7), "+3V3", "GPIO8", FP["r"])

    # --- CAN. No terminator. Publish jumper open. NET-S has no copper. ---
    jp = s.place("Jumper:Jumper_2_Open", "JP1", "1x02_open", *cell(0, 10), FP["jp2"])
    bs.connect_named(s, jp, {"A": "+5V", "B": "CAN_VIN"})
    bs.two_pin(s, "Device:R", "R90", "100k", *cell(1, 10), "CAN_VIN", "GND", FP["r"])
    bs.two_pin(s, "Device:R", "R91", "10k", *cell(2, 10), "GPIO18", "CAN_VIN", FP["r"])
    u = s.place("windlass:MEJ2S", "U9", "MEJ2S0505SC", *cell(3, 10), FP["mej"])
    bs.connect_named(s, u, {"+Vin": "CAN_VIN", "-Vin": "GND", "+Vout": "ISO_5V", "-Vout": "GND_CAN"})
    bs.two_pin(s, "Device:R", "R94", "120", *cell(4, 10), "ISO_5V", "GND_CAN", FP["r1w"])
    bs.two_pin(s, "Device:C_Polarized", "C_ISO", "10uF_16V", *cell(5, 10), "ISO_5V", "GND_CAN", FP["cp"])
    bs.two_pin(s, "Device:C", "C_ISO_HF", "100nF", *cell(6, 10), "ISO_5V", "GND_CAN", FP["c"])
    u = s.place("windlass:MCP2562-E-P", "U_CAN", "MCP2562-E/P", *cell(7, 10), FP["dip8"])
    bs.connect_named(
        s, u,
        {"TXD": "CAN_TXD", "VSS": "GND_CAN", "VDD": "ISO_5V", "RXD": "CAN_RXD",
         "CANL": "CAN_L", "CANH": "CAN_H", "STBY": "GND_CAN"},
    )
    # TX: GPIO high = LED off = isolated TXD high = recessive.
    bs.two_pin(s, "Device:R", "R_TX", "270", *cell(8, 10), "+3V3", "TX_A", FP["r"])
    u = s.place("Isolator:6N137", "U_TX", "6N137", *cell(9, 10), FP["dip8"])
    bs.connect_named(
        s, u,
        {"A": "TX_A", "C": "GPIO4", "GND": "GND_CAN", "VO": "CAN_TXD", "EN": "ISO_5V", "VCC": "ISO_5V"},
    )
    bs.two_pin(s, "Device:R", "R_TXPU", "10k", *cell(10, 10), "ISO_5V", "CAN_TXD", FP["r"])
    bs.two_pin(s, "Device:C", "C_UTX", "100nF", *cell(11, 10), "ISO_5V", "GND_CAN", FP["c"])
    # RX: dominant (RXD low) lights the LED and pulls GPIO5 low.
    bs.two_pin(s, "Device:R", "R_RX", "270", *cell(12, 10), "ISO_5V", "RX_A", FP["r"])
    u = s.place("Isolator:6N137", "U_RX", "6N137", *cell(13, 10), FP["dip8"])
    bs.connect_named(
        s, u,
        {"A": "RX_A", "C": "CAN_RXD", "GND": "GND", "VO": "GPIO5", "EN": "+5V", "VCC": "+5V"},
    )
    bs.two_pin(s, "Device:R", "R_RXPU", "10k", *cell(14, 9), "+3V3", "GPIO5", FP["r"])
    bs.two_pin(s, "Device:C", "C_URX", "100nF", *cell(14, 8), "+5V", "GND", FP["c"])
    bs.multi_pin(
        s, "Connector_Generic:Conn_01x05", "J_NMEA", "B5B-XH-A", *cell(13, 9),
        ["GND_CAN", "CAN_L", "NMEA_SHIELD", "CAN_H", None], FP["xh5"],
    )
    bs.two_pin(s, "Device:C", "C92", "100nF", *cell(12, 9), "NMEA_SHIELD", "GND_CAN", FP["c"])
    return s


def write_project_libs():
    """Local symbols and the four project footprints the global table does not have."""
    import shutil

    symbols = []
    for lib_id, sexpr in bs.LOCAL_SYMBOLS.items():
        leaf = lib_id.split(":")[-1]
        symbols.append(sexpr.replace(f'"{lib_id}"', f'"{leaf}"', 1))
    (OUT / "windlass.kicad_sym").write_text(
        "(kicad_symbol_lib (version 20260306) (generator windlass_build_home)\n"
        + "\n".join(symbols)
        + "\n)\n",
        encoding="utf-8",
    )
    pretty = OUT / "footprints.pretty"
    pretty.mkdir(exist_ok=True)
    src = ROOT / "kicad11" / "footprints.pretty"
    for name in (
        "KF350-3.5-1x02.kicad_mod",
        "KF350-3.5-1x04.kicad_mod",
        "Murata_MEJ2SxxxxSC.kicad_mod",
        "MountingHole_M3_Washer.kicad_mod",
    ):
        shutil.copy(src / name, pretty / name)
    (OUT / "sym-lib-table").write_text(
        '(sym_lib_table\n'
        '  (version 7)\n'
        '  (lib (name "windlass")(type "KiCad")(uri "${KIPRJMOD}/windlass.kicad_sym")(options "")(descr ""))\n'
        ')\n',
        encoding="utf-8",
    )
    (OUT / "fp-lib-table").write_text(
        '(fp_lib_table\n'
        '  (version 7)\n'
        '  (lib (name "windlass")(type "KiCad")(uri "${KIPRJMOD}/footprints.pretty")(options "")(descr ""))\n'
        ')\n',
        encoding="utf-8",
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write_project_libs()
    sheet = build()
    sheet.save(OUT)
    src = OUT / "home.kicad_sch"
    text = src.read_text(encoding="utf-8")
    text = text.replace('(paper "A3")', '(paper "A1")')
    text = text.replace(
        '(title_block (title "home") (date "2026-11-19") (rev "0.7-not-for-fabrication") '
        '(company "Windlass PCB") (comment 1 "NOT FOR FABRICATION"))',
        '(title_block (title "Windlass home assembly") (date "2026-11-24") (rev "1.0") '
        '(company "Windlass PCB") (comment 1 "Bench-validate before installation. Do not order until then."))',
    )
    dst = OUT / "windlass_home.kicad_sch"
    dst.write_text(text, encoding="utf-8")
    src.unlink()
    project = OUT / "windlass_home.kicad_pro"
    if not project.exists():
        project.write_text(
            '{\n  "meta": {"filename": "windlass_home.kicad_pro", "version": 3},\n'
            '  "board": {"design_settings": {"rules": {"min_clearance": 0.2, "min_track_width": 0.15, "min_copper_edge_clearance": 0.5}}}\n}\n',
            encoding="utf-8",
        )
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
