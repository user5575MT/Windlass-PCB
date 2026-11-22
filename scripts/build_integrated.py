#!/usr/bin/env python3
"""Generate the integrated windlass controller schematic into kicad11/.

Does not write kicad/. That folder remains the revision 0.8 reference.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_schematic as bs  # noqa: E402

bs.LIBROOT = Path("/usr/share/kicad/symbols")
bs.LIBS = bs.Libraries()
bs.OUT = ROOT / "kicad11"
bs.PROJECT = "windlass"
OUT = bs.OUT

for _ref in ("R25", "R26", "R27", "R28", "R_PWR"):
    bs.REF_FP[_ref] = "Resistor_SMD:R_0402_1005Metric"
for _ref in ("C25", "C31", "C41"):
    bs.REF_FP[_ref] = "Capacitor_SMD:C_0402_1005Metric"

Sheet = bs.Sheet
two_pin = bs.two_pin
multi_pin = bs.multi_pin
pin = bs.pin
connect_named = bs.connect_named
local_rect_symbol = bs.local_rect_symbol
outward = bs.outward

bs.LOCAL_SYMBOLS["windlass:SMBJ_BI"] = local_rect_symbol(
    "windlass:SMBJ_BI",
    "D",
    "SMBJ18CA",
    "Bidirectional 18 V standoff TVS, SMB. No polarity. Fitted across each relay contact. It clamps the contact opening voltage. It does not join the contactor return to board GND. The Quick coil energy is unmeasured, so this is not a claim that the TVS absorbs that energy.",
    [("1", "A", "passive", "L"), ("2", "B", "passive", "R")],
    width=5.08,
)


def build_power(s: Sheet):
    s.note(
        20,
        250,
        "POWER. One 12 V input, two fuses. NOT FOR FABRICATION.\\n"
        "+12V_MCU feeds the 3.3 V buck only. +12V_COIL feeds the external switch, the ignition contact and the two Finder coils.\\n"
        "There is no 5 V logic rail. The CAN isolator makes its own 5 V from 3.3 V, and only when the publish jumper is fitted.\\n"
        "Contactor-coil current does not enter this 12 V input. It flows through the relay contacts from the boat's existing control feed.",
    )
    s.flag(25, 210, "VIN_12")
    two_pin(s, "Device:Fuse", "F_MCU", "2A_0466002", 55, 200, "VIN_12", "VIN_MCU", "Fuse:Fuse_1206_3216Metric")
    two_pin(s, "Diode:SMAJ18A", "D_TVS_MCU", "SMAJ18A", 90, 200, "VIN_MCU", "GND", "Diode_SMD:D_SMA")
    q = s.place(
        "windlass:DMP6023LE",
        "Q_MCU",
        "DMP6023LE-13",
        140,
        200,
        "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
    )
    connect_named(s, q, {"D": "VIN_MCU", "S": "+12V_MCU", "G": "QMCU_G"})
    two_pin(s, "Device:R", "R_MCU_G", "100k", 140, 175, "QMCU_G", "GND")
    two_pin(s, "windlass:DIODE_OPEN", "D_Z_MCU", "BZT52C12", 170, 200, "+12V_MCU", "QMCU_G", "Diode_SMD:D_SOD-123")
    s.flag(175, 215, "+12V_MCU")
    _buck(s, 40, 120)
    s.flag(40, 70, "+3V3")
    two_pin(s, "Device:Fuse", "F_COIL", "1A_0466001", 40, 40, "VIN_12", "VIN_COIL", "Fuse:Fuse_1206_3216Metric")
    two_pin(s, "Diode:SMAJ18A", "D_TVS_COIL", "SMAJ18A", 80, 40, "VIN_COIL", "GND", "Diode_SMD:D_SMA")
    qc = s.place(
        "windlass:DMP6023LE",
        "Q_COIL",
        "DMP6023LE-13",
        130,
        40,
        "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
    )
    connect_named(s, qc, {"D": "VIN_COIL", "S": "+12V_COIL", "G": "QCOIL_G"})
    two_pin(s, "Device:R", "R_COIL_G", "100k", 130, 18, "QCOIL_G", "GND")
    two_pin(s, "windlass:DIODE_OPEN", "D_Z_COIL", "BZT52C12", 165, 40, "+12V_COIL", "QCOIL_G", "Diode_SMD:D_SOD-123")
    s.flag(175, 55, "+12V_COIL")
    s.flag(20, 20, "GND")
    s.note(
        200,
        120,
        "SMAJ18A is a 400 W, 10/1000 us clamp, about 29.2 V at the rated pulse. It is not load-dump protection.\\n"
        "AP63203 absolute maximum is 35 V DC and 40 V for 400 ms. Recommended operating maximum is 32 V.\\n"
        "Reverse battery turns Q_MCU off. The unidirectional TVS then conducts and F_MCU is what opens.\\n"
        "F_COIL is sized for two Finder coils, 42 mA each, only one at a time. It is not the contactor-coil fuse.\\n"
        "The boat's recommended 2.5 A control fuse, if fitted, is in the existing control wiring, not on this board.",
    )


def _buck(s, x, y):
    u = s.place(
        "Regulator_Switching:AP63203WU",
        "U20",
        "AP63203WU-7",
        x,
        y,
        "Package_TO_SOT_SMD:TSOT-23-6",
    )
    connect_named(s, u, {"IN": "+12V_MCU", "EN": "+12V_MCU", "GND": "GND", "SW": "SW_3V3", "BST": "BST_3V3", "FB": "+3V3"})
    two_pin(s, "Device:L", "L20", "3.9uH", x + 40, y + 10, "SW_3V3", "+3V3", "Inductor_SMD:L_Bourns-SRN4018")
    two_pin(s, "Device:C", "C30B", "100nF", x + 20, y - 20, "BST_3V3", "SW_3V3")
    two_pin(s, "Device:C", "C30I", "10uF", x - 20, y - 20, "+12V_MCU", "GND", "Capacitor_SMD:C_0805_2012Metric")
    two_pin(s, "Device:C", "C30A", "22uF", x + 60, y - 16, "+3V3", "GND", "Capacitor_SMD:C_0805_2012Metric")
    two_pin(s, "Device:C", "C30C", "22uF", x + 80, y - 16, "+3V3", "GND", "Capacitor_SMD:C_0805_2012Metric")


def build_esp(s: Sheet):
    s.note(
        20,
        270,
        "ESP32-S3-WROOM-1-N16. NOT FOR FABRICATION. Prototype firmware is not modified and does not edge GPIO1.\\n"
        "EN: 10k to +3V3 and 1 uF to GND. GPIO0: 10k pull-up and a boot button. GPIO3: 10k to GND.\\n"
        "GPIO45 and GPIO46 stay open. Do not pull GPIO45 high. USB VBUS is not connected to +3V3.",
    )
    m = s.place("RF_Module:ESP32-S3-WROOM-1", "U3", "ESP32-S3-WROOM-1-N16", 170, 150, "RF_Module:ESP32-S3-WROOM-1")
    connect_named(
        s,
        m,
        {
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
            "IO18": "PUBLISH_EN",
            "USB_D-": "USB_DN",
            "USB_D+": "USB_DP",
            "TXD0": "UART_TX",
            "RXD0": "UART_RX",
        },
    )
    two_pin(s, "Device:R", "R10", "10k", 40, 220, "EN_NET", "+3V3")
    two_pin(s, "Device:C", "C10", "1uF", 40, 200, "EN_NET", "GND")
    sw = s.place("Switch:SW_Push", "SW_RST", "TL3342F160QG", 70, 180, "Button_Switch_SMD:SW_SPST_TL3342")
    connect_named(s, sw, {"1": "EN_NET", "2": "GND"})
    two_pin(s, "Device:R", "R11", "10k", 40, 150, "IO0_NET", "+3V3")
    swb = s.place("Switch:SW_Push", "SW_BOOT", "TL3342F160QG", 70, 140, "Button_Switch_SMD:SW_SPST_TL3342")
    connect_named(s, swb, {"1": "IO0_NET", "2": "GND"})
    two_pin(s, "Device:R", "R12", "10k", 40, 110, "IO3_NET", "GND")
    two_pin(s, "Device:C", "C11", "10uF", 100, 220, "+3V3", "GND", "Capacitor_SMD:C_0805_2012Metric")
    two_pin(s, "Device:C", "C12", "100nF", 120, 220, "+3V3", "GND")
    two_pin(s, "Device:R", "R13", "100k", 100, 180, "UP_REQ", "GND")
    two_pin(s, "Device:R", "R14", "100k", 120, 180, "DN_REQ", "GND")
    usb = s.place(
        "Connector:USB_C_Receptacle_USB2.0_16P",
        "J_USB",
        "USB4105",
        300,
        160,
        "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
    )
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
    two_pin(s, "Device:R", "R15", "5.1k", 250, 120, "CC1", "GND")
    two_pin(s, "Device:R", "R16", "5.1k", 270, 120, "CC2", "GND")
    two_pin(s, "Device:R", "R17", "22", 250, 140, "USB_DP", "USB_DP_C")
    two_pin(s, "Device:R", "R18", "22", 270, 140, "USB_DN", "USB_DN_C")
    esd = s.place(
        "Power_Protection:USBLC6-2SC6",
        "U_ESD",
        "USBLC6-2SC6",
        300,
        110,
        "Package_TO_SOT_SMD:SOT-23-6",
    )
    connect_named(s, esd, {"I/O1": "USB_DP_C", "I/O2": "USB_DN_C", "GND": "GND", "VBUS": "USB_VBUS"})
    two_pin(s, "Device:R", "R19", "1M", 330, 80, "USB_SHIELD", "GND")
    two_pin(s, "Device:C", "C13", "100nF", 350, 80, "USB_SHIELD", "GND")
    for ref, net, x in (
        ("TP_TX", "UART_TX", 40),
        ("TP_RX", "UART_RX", 55),
        ("TP_WDI", "WDI_FUTURE", 70),
        ("TP_3V3", "+3V3", 85),
        ("TP_GND", "GND", 100),
        ("TP_REED", "REED_GPIO", 115),
    ):
        tp = s.place("Connector_Generic:Conn_01x01", ref, "TP", x, 80, "TestPoint:TestPoint_Pad_D1.5mm")
        p = pin(tp, num="1")[0]
        if net in ("GND", "+3V3"):
            s.power(p, net)
        else:
            s.label(p, net)
    s.note(
        20,
        40,
        "J_USB is a GCT USB4105 top-mount receptacle. Every signal pad is on the board. The earlier mid-mount HRO part is not used.\\n"
        "CC resistors are 5.1k Rd. D+ and D- have 22 ohm series resistors, then USBLC6-2SC6. Its VBUS pin is USB_VBUS, not +3V3.\\n"
        "R13 and R14 hold the coil requests low while the GPIOs are high-Z, including reset.",
    )


def build_reed(s: Sheet):
    s.note(
        20,
        270,
        "REED. REED_RET is not GND, UP_RET, DN_RET or GND_CAN. NOT FOR FABRICATION.\\n"
        "ISO7720FDR is the fail-safe-low orderable part. The KiCad symbol is the shared SOIC-8 pinout.\\n"
        "Default shunt is pins 1-2, Lofrans. Dry contact is the same shunt on pins 2-3. Fit one shunt only.",
    )
    dcdc = s.place("windlass:MEJ2S", "U4", "MEJ2S0303SC", 40, 210, "windlass:Murata_MEJ2SxxxxSC")
    connect_named(s, dcdc, {"1": "+3V3", "2": "GND", "7": "REED_3V3", "5": "REED_RET"})
    two_pin(s, "Device:C", "C24", "100nF", 40, 180, "+3V3", "GND")
    two_pin(s, "Device:C", "C20", "100nF", 80, 180, "REED_3V3", "REED_RET")
    two_pin(s, "Device:R", "R24", "51_0.5W", 100, 180, "REED_3V3", "REED_RET", "Resistor_SMD:R_2512_6332Metric")
    two_pin(s, "Device:R", "R20", "10k", 140, 230, "REED_SIG", "LOFRANS_NODE")
    two_pin(s, "Device:D_Schottky", "D20", "BAT54W", 170, 230, "REED_3V3", "LOFRANS_NODE", "Diode_SMD:D_SOD-123")
    two_pin(s, "Device:D_Schottky", "D21", "BAT54W", 170, 210, "LOFRANS_NODE", "REED_RET", "Diode_SMD:D_SOD-123")
    jp = s.place(
        "Jumper:Jumper_3_Open",
        "JP_REED",
        "HDR_1x03",
        220,
        210,
        "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    )
    connect_named(s, jp, {"1": "LOFRANS_NODE", "2": "REED_ISO", "3": "DRY_A"})
    shunt = s.place("Connector_Generic:Conn_01x02", "SH_REED", "SHUNT_2.54", 250, 230, on_board="no")
    for p in shunt:
        s.nc(p)
    two_pin(s, "Device:R", "R22", "4.7k", 220, 180, "REED_3V3", "DRY_A")
    two_pin(s, "Device:R", "R23", "47k", 250, 180, "REED_ISO", "REED_RET")
    two_pin(s, "Device:C", "C22", "1nF", 270, 180, "REED_ISO", "REED_RET")
    iso = s.place("Isolator:ISO7720D", "U5", "ISO7720FDR", 320, 210, "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
    connect_named(
        s,
        iso,
        {
            "VCC1": "REED_3V3",
            "INA": "REED_ISO",
            "INB": "REED_3V3",
            "GND1": "REED_RET",
            "GND2": "GND",
            "OUTB": "PG",
            "OUTA": "REED_DATA",
            "VCC2": "+3V3",
        },
    )
    two_pin(s, "Device:C", "C21", "100nF", 360, 180, "+3V3", "GND")
    # Blanker. /S = PG. /R = REED_DATA OR NOT PG. Q high forces the GPIO low.
    nfet = s.place("Transistor_FET:2N7002", "Q_NPG", "2N7002BK", 40, 120, "Package_TO_SOT_SMD:SOT-23")
    connect_named(s, nfet, {"G": "PG", "D": "NOT_PG", "S": "GND"})
    two_pin(s, "Device:R", "R25", "10k", 70, 120, "NOT_PG", "+3V3")
    two_pin(s, "Device:D_Schottky", "D22", "BAT54W", 100, 130, "OR_R", "REED_DATA", "Diode_SMD:D_SOD-123")
    two_pin(s, "Device:D_Schottky", "D23", "BAT54W", 100, 110, "OR_R", "NOT_PG", "Diode_SMD:D_SOD-123")
    two_pin(s, "Device:R", "R26", "100k", 130, 110, "OR_R", "GND")
    n1 = s.place("74xGxx:74LVC1G00", "U13", "74LVC1G00GW", 180, 130, "Package_TO_SOT_SMD:SOT-353_SC-70-5")
    connect_named(s, n1, {"1": "PG", "2": "NQ", "GND": "GND", "4": "BLOCKED", "5": "+3V3"})
    n2 = s.place("74xGxx:74LVC1G00", "U14", "74LVC1G00GW", 230, 110, "Package_TO_SOT_SMD:SOT-353_SC-70-5")
    connect_named(s, n2, {"1": "OR_R", "2": "BLOCKED", "GND": "GND", "4": "NQ", "5": "+3V3"})
    two_pin(s, "Device:C", "C25", "100nF", 180, 90, "+3V3", "GND")
    two_pin(s, "Device:R", "R27", "10k", 280, 130, "REED_DATA", "REED_GPIO")
    qblk = s.place("Transistor_FET:2N7002", "Q_BLK", "2N7002BK", 310, 110, "Package_TO_SOT_SMD:SOT-23")
    connect_named(s, qblk, {"G": "BLOCKED", "D": "REED_GPIO", "S": "GND"})
    two_pin(s, "Device:R", "R28", "100k", 340, 110, "REED_GPIO", "GND")
    s.note(
        20,
        40,
        "Lofrans load is 3.3 V / 47k = 70 uA, and only while the shunt is on pins 1-2. The 4.7k pull-up is on DRY_A and cannot reach REED_SIG in that position.\\n"
        "R20 is 10k in series. D20 and D21 clamp LOFRANS_NODE to the field 3.3 V rail. The Lofrans wire is not connected to an ESP32 pin.\\n"
        "MEJ2S0303SC is 3.3 V to 3.3 V. R24 is 51 ohm, about 65 mA, just over 10 percent of the 606 mA rating, so the published load envelope applies.\\n"
        "Murata: hipot 5.2 kVDC for 1 s, continuous functional barrier 2.4 kVDC. Not a safety barrier. The LCSC YLPTEC listing is not this part.\\n"
        "Blanker: ISO7720F outputs go low when the field side is unpowered. Q_NPG makes NOT_PG. The diode-OR and the two NAND gates are an SR latch.\\n"
        "/S is PG, so a field-supply loss sets BLOCKED and Q_BLK holds REED_GPIO low. That is a falling edge, which the existing firmware does not count.\\n"
        "The latch clears only when PG is high and REED_DATA is low, which is the start of a real pulse. The following rise is the end of that pulse.\\n"
        "Supply loss and recovery while idle produce no counted rising edge. Recovery during a real pulse counts that pulse once or misses it.\\n"
        "Until the first real pulse after power-up, REED_GPIO is held low. The firmware samples that level and does not treat the sample as an edge.\\n"
        "INB is tied to the field rail, so OUTB is high only while the isolator considers that rail valid. This is not a separate precision supervisor.",
    )


def build_direction(s: Sheet):
    s.note(
        20,
        250,
        "DIRECTION SENSE. UP_RET and DN_RET are different nets. Neither joins GND. NOT FOR FABRICATION.\\n"
        "Assumption, not a measurement: each FIELD pin is a switched positive voltage, about 5 V to 24 V, and the matching RET pin is that circuit's return.\\n"
        "R30 and R40 are 4.7k on that assumption. At 12 V the LED current is about 2.3 mA. Confirm polarity and voltage before installation.\\n"
        "If the sense wire is not a low-impedance switched positive, change these two resistors. Do not join the two returns on this PCB.",
    )
    _sense(s, 180, "UP", "R30", "D30", "C31", "U6")
    _sense(s, 80, "DN", "R40", "D40", "C41", "U7")
    s.note(
        20,
        40,
        "TLP291(GB-TP,SE): pin 1 anode, pin 2 cathode, pin 3 emitter, pin 4 collector.\\n"
        "Emitter is board GND. Collector is the GPIO with a 10k pull-up to 3.3 V. LED on pulls the GPIO low, which is what the existing firmware treats as active.\\n"
        "1N4148 is anti-parallel across the LED. 100 nF is across the LED. There is no isolated supply on these channels.",
    )


def _sense(s, y, tag, rref, dref, cref, uref):
    field = f"{tag}_FIELD"
    ret = f"{tag}_RET"
    node = f"{tag}_LED_A"
    gpio = "UP_SENSE" if tag == "UP" else "DN_SENSE"
    two_pin(s, "Device:R", rref, "4.7k", 50, y, field, node)
    opt = s.place(
        "Isolator:TLP291",
        uref,
        "TLP291(GB-TP,SE",
        110,
        y,
        "Package_SO:SOIC-4_4.55x2.6mm_P1.27mm",
    )
    by = {p["num"]: p for p in opt}
    s.label(by["1"], node)
    s.label(by["2"], ret)
    s.power(by["3"], "GND")
    s.label(by["4"], gpio)
    two_pin(s, "Device:R", rref + "P", "10k", 160, y + 15, gpio, "+3V3")
    two_pin(s, "windlass:DIODE_OPEN", dref, "1N4148W", 80, y - 22, node, ret, "Diode_SMD:D_SOD-123")
    two_pin(s, "Device:C", cref, "100nF", 80, y + 18, node, ret)


def build_relay(s: Sheet):
    s.note(
        20,
        265,
        "RELAYS. Finder 40.31.7.012.0000. NOT FOR FABRICATION.\\n"
        "Coil table: 288 ohm, 42 mA at 12 V, pickup 8.8 V, max 18 V. Contact DC1 is 10 A resistive at 30 V DC.\\n"
        "DC13 life equals DC1 only when the load already has a diode. That is not assumed.\\n"
        "The XOR and AND gates are removed. The cross-clamps stop both coils being commanded together. The series FET drops the coil return unless the heartbeat is fresh.\\n"
        "A welded contact is not opened by any of this.",
    )
    two_pin(s, "Device:R", "R_COILFEED", "0", 30, 220, "IGN_B", "COIL_12")
    wdt = s.place("windlass:74LVC1G123", "U11", "74LVC1G123DP,125", 80, 190, "Package_SO:TSSOP-8_3x3mm_P0.65mm")
    connect_named(
        s,
        wdt,
        {"A": "GND", "B": "WDI_FUTURE", "CLR": "+3V3", "GND": "GND", "Q": "WDT_Q", "CEXT": "WDT_C", "REXT": "WDT_RC", "VCC": "+3V3"},
    )
    two_pin(s, "Device:R", "R52", "100k", 130, 220, "+3V3", "WDT_RC")
    two_pin(s, "Device:C", "C50", "3.3uF", 130, 200, "WDT_C", "WDT_RC", "Capacitor_SMD:C_0805_2012Metric")
    two_pin(s, "Device:R", "R53", "100k", 40, 160, "WDI_FUTURE", "GND")
    two_pin(s, "Device:C", "C51", "100nF", 40, 140, "+3V3", "GND")
    two_pin(s, "Device:R", "R50", "100", 180, 190, "WDT_Q", "QSERIES_G")
    two_pin(s, "Device:R", "R51", "100k", 180, 170, "QSERIES_G", "GND")
    qs = s.place("windlass:NX6008NBK", "Q_SERIES", "NX6008NBK", 230, 180, "Package_TO_SOT_SMD:SOT-23")
    connect_named(s, qs, {"G": "QSERIES_G", "S": "GND", "D": "SERIES_NODE"})
    _coil(s, 110, "UP", "Q_UP", "Q_CLAMP_UP", "K_UP", "R60", "R61", "D60", "D61")
    _coil(s, 40, "DN", "Q_DN", "Q_CLAMP_DN", "K_DN", "R70", "R71", "D70", "D71")
    two_pin(s, "Device:R", "R80", "100k", 300, 220, "COIL_12", "COIL_DIV")
    two_pin(s, "Device:R", "R81", "100k", 320, 220, "COIL_DIV", "GND")
    two_pin(s, "Device:D_Schottky", "D80", "BAT54W", 340, 220, "+3V3", "COIL_DIV", "Diode_SMD:D_SOD-123")
    two_pin(s, "Device:R", "R82", "1k", 360, 220, "COIL_DIV", "COIL_RAIL_OK")
    s.note(
        250,
        140,
        "Heartbeat: Nexperia tW = K * REXT(kOhm) * CEXT(pF) ns, K about 1 above 10 nF. 100k and 3.3 uF is 330 ms typical.\\n"
        "Long case, K=1.2 and capacitor +20 percent, is about 475 ms. A static level does not retrigger.\\n"
        "The prototype firmware does not edge GPIO1, so Q stays low and both coils stay off. Do not modify that firmware.\\n"
        "Each gate has a 100k pulldown. The other request turns on a 2N7002 that clamps that gate off.\\n"
        "Both requests high: both gates are clamped off. One request, fresh heartbeat: that coil pulls in.\\n"
        "SMBJ18CA is across each COM-NO pair only. It is bidirectional, so it does not require the contactor return to be board GND.\\n"
        "Contact copper is 1.2 mm for a 2.5 A upper bound from the Quick recommended control fuse, using IPC-2221 external 1 oz, 10 C, which is about 1.07 mm at 2.5 A.\\n"
        "That fuse rating is not a measured coil current. Do not install until the control current and its inductive energy are measured.",
    )


def _coil(s, y, tag, qref, cref, kref, rgate, rpull, dref, tvs):
    own = "UP_REQ" if tag == "UP" else "DN_REQ"
    other = "DN_REQ" if tag == "UP" else "UP_REQ"
    gate = f"{tag}_GATE"
    low = f"{tag}_LOW"
    com = f"{tag}_COM"
    no = f"{tag}_NO"
    two_pin(s, "Device:R", rgate, "10k", 40, y, own, gate)
    two_pin(s, "Device:R", rpull, "100k", 60, y, gate, "GND")
    clamp = s.place("Transistor_FET:2N7002", cref, "2N7002BK", 90, y, "Package_TO_SOT_SMD:SOT-23")
    connect_named(s, clamp, {"G": other, "D": gate, "S": "GND"})
    fet = s.place("windlass:NX6008NBK", qref, "NX6008NBK", 140, y, "Package_TO_SOT_SMD:SOT-23")
    connect_named(s, fet, {"G": gate, "D": low, "S": "SERIES_NODE"})
    k = s.place("Relay:Relay_SPDT", kref, "40.31.7.012.0000", 200, y, "Relay_THT:Relay_SPDT_Finder_40.31")
    connect_named(s, k, {"A1": "COIL_12", "A2": low, "11": com, "14": no, "12": None})
    two_pin(s, "windlass:DIODE_OPEN", dref, "SS14", 170, y + 18, "COIL_12", low, "Diode_SMD:D_SMA")
    two_pin(s, "windlass:SMBJ_BI", tvs, "SMBJ18CA", 240, y, com, no, "Diode_SMD:D_SMB")


def build_nmea(s: Sheet):
    s.note(
        20,
        250,
        "NMEA 2000. No 120 ohm resistor is placed across CANH and CANL. NOT FOR FABRICATION.\\n"
        "GND_CAN is not GND and not REED_RET. NET-S is a connector pin with no copper.\\n"
        "The publish jumper is open by default. Open, the isolated 5 V module is off and this board does not drive the bus.",
    )
    jp = s.place(
        "Jumper:Jumper_2_Open",
        "JP1",
        "Jumper_2_Open",
        40,
        200,
        "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
    )
    connect_named(s, jp, {"A": "+3V3", "B": "CAN_VIN"})
    two_pin(s, "Device:R", "R90", "100k", 70, 180, "CAN_VIN", "GND")
    two_pin(s, "Device:R", "R91", "10k", 70, 160, "CAN_VIN", "PUBLISH_EN")
    dcdc = s.place("windlass:MEJ2S", "U9", "MEJ2S0305SC", 140, 190, "windlass:Murata_MEJ2SxxxxSC")
    connect_named(s, dcdc, {"1": "CAN_VIN", "2": "GND", "7": "ISO_5V", "5": "GND_CAN"})
    vin = pin(dcdc, num="1")[0]
    dx, dy = outward(vin["ang"])
    s.flag(round(vin["ax"] + dx * 2.54, 4), round(vin["ay"] + dy * 2.54, 4))
    two_pin(s, "Device:R", "R94", "120_0.5W", 180, 160, "ISO_5V", "GND_CAN", "Resistor_SMD:R_2512_6332Metric")
    two_pin(s, "Device:C", "C93", "100nF", 110, 160, "CAN_VIN", "GND")
    two_pin(s, "Device:C", "C91", "100nF", 180, 140, "ISO_5V", "GND_CAN")
    u = s.place("windlass:ISO1042BDWR", "U10", "ISO1042BDWR", 260, 180)
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
    two_pin(s, "Device:R", "R92", "10k", 220, 220, "TXD_NODE", "+3V3")
    two_pin(s, "Device:R", "R93", "33", 200, 150, "TWAI_TX", "TXD_NODE")
    two_pin(s, "Device:C", "C90", "100nF", 220, 130, "+3V3", "GND")
    two_pin(s, "Device:C", "C92", "100nF", 320, 150, "NMEA_SHIELD", "GND_CAN")
    s.note(
        20,
        70,
        "ISO1042 primary is 3.3 V. VCC2 must be 4.5 V to 5.5 V, so U9 is a Murata MEJ2S0305SC, 3.3 V to 5 V, 400 mA rating.\\n"
        "R94 is 120 ohm, about 42 mA, just over 10 percent of that rating. 5 V plus the published 9 percent envelope is 5.45 V, inside the ISO1042 VCC2 range.\\n"
        "Hipot 5.2 kVDC for 1 s. Continuous functional barrier 2.4 kVDC. Not a safety barrier.\\n"
        "JP1 open: R90 holds CAN_VIN low, the module is off, and R91 lets GPIO18 read low. JP1 fitted: the module runs and GPIO18 reads high.\\n"
        "R91 limits a mistaken GPIO drive to about 0.3 mA. There is no 120 ohm between CAN_H and CAN_L. R94 is a preload, not a terminator.\\n"
        "C92 joins the shield to GND_CAN only. Do not land the NMEA NET-S wire.",
    )


def build_connectors(s: Sheet):
    s.note(
        20,
        260,
        "CONNECTORS. NOT FOR FABRICATION.\\n"
        "J_PWR, J_CONTACT and J_PERM are 3.5 mm screw terminals. J_REED, J_SENSE and J_NMEA are JST XH.\\n"
        "Pins inside one housing are not joined, except J_REED pins 2 and 4, which are both REED_RET so each cable has its own return wire.",
    )
    two_pin(s, "Connector_Generic:Conn_01x02", "J_PWR", "KF350-3.5-2P", 30, 210, "VIN_12", "GND", "windlass:KF350-3.5-1x02")
    multi_pin(
        s,
        "Connector_Generic:Conn_01x04",
        "J_CONTACT",
        "KF350-3.5-4P",
        80,
        210,
        ["UP_COM", "UP_NO", "DN_COM", "DN_NO"],
        "windlass:KF350-3.5-1x04",
    )
    multi_pin(
        s,
        "Connector_Generic:Conn_01x04",
        "J_PERM",
        "KF350-3.5-4P",
        140,
        210,
        ["SW_A", "SW_B", "IGN_A", "IGN_B"],
        "windlass:KF350-3.5-1x04",
    )
    two_pin(s, "Device:R", "R_SWLINK", "0", 180, 220, "+12V_COIL", "SW_A")
    two_pin(s, "Device:R", "R_IGNLINK", "0", 200, 220, "SW_B", "IGN_A")
    multi_pin(
        s,
        "Connector_Generic:Conn_01x04",
        "J_REED",
        "B4B-XH-A",
        30,
        150,
        ["REED_SIG", "REED_RET", "DRY_A", "REED_RET"],
        "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
    )
    multi_pin(
        s,
        "Connector_Generic:Conn_01x05",
        "J_SENSE",
        "B5B-XH-A",
        90,
        150,
        ["UP_FIELD", "UP_RET", None, "DN_FIELD", "DN_RET"],
        "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical",
    )
    multi_pin(
        s,
        "Connector_Generic:Conn_01x05",
        "J_NMEA",
        "B5B-XH-A",
        150,
        150,
        ["GND_CAN", "CAN_L", "NMEA_SHIELD", "CAN_H", None],
        "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical",
    )
    _led(s, 40, 80, "LED_R", "D_R", "R_R", "LTST-C190KRKT")
    _led(s, 100, 80, "LED_G", "D_G", "R_G", "LTST-C190KGKT")
    two_pin(s, "Device:R", "R_RPD", "100k", 40, 55, "LED_R", "GND")
    two_pin(s, "Device:R", "R_GPD", "100k", 100, 55, "LED_G", "GND")
    two_pin(s, "Device:R", "R_PWR", "1k", 170, 80, "+3V3", "LED_PWR_A")
    led = s.place("Device:LED", "D_PWR", "LTST-C190KRKT", 200, 80, "LED_SMD:LED_0603_1608Metric")
    by = {p["num"]: p for p in led}
    s.label(by["2"], "LED_PWR_A")
    s.power(by["1"], "GND")
    s.note(
        230,
        140,
        "J_NMEA is the PCB header, not a Micro-C. Pigtail:\\n"
        "1 GND_CAN to NET-C. 2 CAN_L to NET-L. 3 shield, capacitor to GND_CAN only.\\n"
        "4 CAN_H to NET-H. 5 NET-S is open. Do not land the red wire. This board does not take backbone power.\\n"
        "D_R and D_G are GPIO-driven, 680 ohm, from 3.3 V. D_PWR is on +3V3 and has no GPIO. The blue LED is removed.\\n"
        "R_SWLINK and R_IGNLINK are 0 ohm. Coil current still has to pass the external switch, the ignition contact and Q_SERIES.\\n"
        "Relay contacts are in parallel with the existing controls. Unplugging J_CONTACT leaves those controls in place.\\n"
        "J_SENSE pin 3 is unused so the two returns are not on adjacent pins.",
    )


def _led(s, x, y, net, dref, rref, value):
    two_pin(s, "Device:R", rref, "680", x, y, net, f"{net}_A")
    led = s.place("Device:LED", dref, value, x + 25, y, "LED_SMD:LED_0603_1608Metric")
    by = {p["num"]: p for p in led}
    s.label(by["2"], f"{net}_A")
    s.power(by["1"], "GND")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(ROOT / "kicad" / "footprints.pretty", OUT / "footprints.pretty")
    sheets = {name: Sheet(name) for name in bs.SHEET_IDS}
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
    for lib_id, sexpr in bs.LOCAL_SYMBOLS.items():
        leaf = lib_id.split(":")[-1]
        parts.append(sexpr.replace(f'(symbol "{lib_id}"', f'(symbol "{leaf}"', 1))
    lib = (
        '(kicad_symbol_lib\n'
        '  (version 20251024)\n'
        '  (generator "windlass_build_integrated")\n'
        '  (generator_version "1")\n'
        + "\n".join(parts)
        + "\n)\n"
    )
    (OUT / "windlass.kicad_sym").write_text(lib, encoding="utf-8")
    bs.build_root(OUT)
    text = (OUT / "windlass.kicad_sch").read_text(encoding="utf-8")
    text = text.replace("rev 0.7", "rev 1.0 integrated")
    text = text.replace(
        "WINDLASS CONTROLLER  rev 1.0 integrated   NOT FOR FABRICATION",
        "WINDLASS CONTROLLER  integrated rev 1.0   NOT FOR FABRICATION",
    )
    (OUT / "windlass.kicad_sch").write_text(text, encoding="utf-8")
    for sch in OUT.glob("*.kicad_sch"):
        body = sch.read_text(encoding="utf-8")
        body = body.replace('(rev "0.7-not-for-fabrication")', '(rev "1.0-not-for-fabrication")')
        body = body.replace('(date "2026-11-19")', '(date "2026-11-22")')
        sch.write_text(body, encoding="utf-8")
    (OUT / "sym-lib-table").write_text((ROOT / "kicad" / "sym-lib-table").read_text(encoding="utf-8"), encoding="utf-8")
    (OUT / "fp-lib-table").write_text((ROOT / "kicad" / "fp-lib-table").read_text(encoding="utf-8"), encoding="utf-8")
    (OUT / "windlass.kicad_pro").write_text(
        '{\n  "meta": {"filename": "windlass.kicad_pro", "version": 3},\n'
        '  "sheets": [],\n  "text_variables": {},\n'
        '  "schematic": {"legacy_lib_dir": "", "legacy_lib_names": []}\n}\n',
        encoding="utf-8",
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
