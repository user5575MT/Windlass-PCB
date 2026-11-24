#!/usr/bin/env python3
"""Place and route the 100 x 100 mm through-hole home board.

The v2 board is not read or written. Isolation nets stay on their own side of
a milled slot under each optocoupler and each MEJ2.
"""
from __future__ import annotations

import heapq
import math
import os
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_board import parse_netlist

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "kicad_home"
FP = Path("/usr/share/kicad/footprints")
BOARD_W = 120.0
BOARD_H = 112.0
GRID = 0.254
EDGE = 0.8
CLR = 0.20
ISO = 0.60

REED = {
    "REED_RET", "REED_3V3", "REED_SIG", "LOFRANS_NODE", "DRY_A", "REED_ISO",
    "REED_B", "REED_C", "RD_A", "PG_A",
}
CAN = {"GND_CAN", "ISO_5V", "CAN_H", "CAN_L", "CAN_TXD", "CAN_RXD", "NMEA_SHIELD", "RX_A"}
UP = {"UP_RET", "UP_FIELD", "UP_LED"}
DN = {"DN_RET", "DN_FIELD", "DN_LED"}
POWER = {
    "GND", "+5V", "+3V3", "+12V_MCU", "+12V_COIL", "VIN_12", "VIN_MCU", "VIN_COIL",
    "COIL_12", "DEV_5V", "SERIES_DRAIN", "UP_LOW", "DN_LOW", "SW_LINK",
}


def domain(net: str) -> str:
    if net in REED:
        return "reed"
    if net in CAN:
        return "can"
    if net in UP:
        return "up"
    if net in DN:
        return "dn"
    return "mcu"


WIDE = {"+12V_MCU", "+12V_COIL", "VIN_12", "VIN_MCU", "VIN_COIL", "COIL_12", "SERIES_DRAIN", "UP_LOW", "DN_LOW", "SW_LINK"}


def width_of(net: str) -> float:
    if net in WIDE:
        return 0.80
    if net in POWER:
        return 0.50
    return 0.35


def mm(v: float) -> int:
    return int(round(v * 1_000_000))


def fp_file(footprint: str):
    lib, name = footprint.split(":")
    if lib == "windlass":
        return str(OUT / "footprints.pretty"), name
    return str(FP / f"{lib}.pretty"), name


def add_line(board, x1, y1, x2, y2, layer="Edge.Cuts", width=0.1):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    seg.SetLayer(board.GetLayerID(layer))
    seg.SetWidth(mm(width))
    board.Add(seg)


def xform(fp, x, y):
    ang = math.radians(fp.GetOrientation().AsDegrees())
    xr = x * math.cos(ang) - y * math.sin(ang)
    yr = x * math.sin(ang) + y * math.cos(ang)
    pos = fp.GetPosition()
    return pos.x / 1e6 + xr, pos.y / 1e6 + yr


# Pin 1 position and rotation. Positive rotation is counterclockwise.
ANCHORS = {
    # Courtyards packed along the bottom edge, left to right.
    "J_PWR": (5.1, 7, 0),
    "J_PERM": (15.3, 7, 0),
    "J_CONTACT": (32.5, 7, 0),
    "J_REED": (51.4, 7, 0),
    "J_SENSE": (66.4, 7, 0),
    "J_NMEA": (83.9, 7, 0),
    # Pin 1 is the USB end. Rotation 90 points pin 22, and the antenna, to +X.
    "J1": (8, 71, 90),
    "J3": (8, 93.86, 90),
    "K_UP": (4.5, 16, 0),
    "K_DN": (4.5, 31.5, 0),
    # These four DIPs sit in the 8 mm gap under the DevKit. A TO-220 does not.
    "U12": (8, 74.9, 0),
    "U15": (20, 74.9, 0),
    "U16": (32, 74.9, 0),
    "U17": (44, 74.9, 0),
    "U20": (16, 52, 0),
    "F_COIL": (38, 15, -90),
    "F_MCU": (50, 15, -90),
    # Right-hand column. Primary or MCU side faces left. Secondary faces the right edge.
    "U6": (80, 16, 180),
    "U7": (80, 24, 180),
    "U4": (78, 40, 0),
    "U_PG": (90, 52, 180),
    "U_RD": (90, 60, 180),
    "U9": (78, 68, 0),
    "U_TX": (78, 82, 0),
    "U_RX": (112, 80, 180),
    "U_CAN": (100, 90, 0),
    "JP1": (70, 78, 0),
    "JP_REED": (70, 34, 0),
}

# One domain can have several boxes. The packer tries them in order.
REGIONS = {
    "mcu": [(2.0, 13.0, 73.0, 110.0)],
    "reed": [(74.0, 30.0, 118.0, 62.0), (74.0, 100.0, 118.0, 110.0)],
    "up": [(74.0, 12.0, 118.0, 32.0), (74.0, 100.0, 118.0, 110.0)],
    "dn": [(74.0, 12.0, 118.0, 32.0), (74.0, 100.0, 118.0, 110.0)],
    "can": [(74.0, 60.0, 118.0, 110.0)],
}
ISLANDS = [box for name, boxes in REGIONS.items() if name != "mcu" for box in boxes]
# Taller than the gap under a mated DevKit. They stay outside that shadow.
TALL = {
    "C_IN", "C_5V", "C_DEV", "C_3V3B", "C_REED", "C_ISO", "C_TIME",
    "F_COIL", "F_MCU", "U20", "U4", "U9", "K_UP", "K_DN",
    "Q_COIL", "Q_MCU", "Q_UP", "Q_DN", "Q_SERIES", "R24", "R94",
}


def rect_of(fp, margin=0.4):
    bb = fp.GetBoundingBox(False, False)
    return (
        bb.GetLeft() / 1e6 - margin,
        bb.GetTop() / 1e6 - margin,
        bb.GetRight() / 1e6 + margin,
        bb.GetBottom() / 1e6 + margin,
    )


def overlaps(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def apply_rules(board, net_names):
    """Clearances the autorouter and DRC both see. Isolation classes stay 0.6 mm from everything."""
    design = board.GetDesignSettings()
    design.m_CopperEdgeClearance = pcbnew.FromMM(0.50)
    design.m_MinClearance = pcbnew.FromMM(0.20)
    # The router leaves a 0.175 mm neck on one gate net. That is above a
    # two-layer fab minimum of 0.127 mm.
    design.m_TrackMinWidth = pcbnew.FromMM(0.15)
    settings = design.m_NetSettings
    default = settings.GetDefaultNetclass()
    default.SetClearance(pcbnew.FromMM(0.20))
    default.SetTrackWidth(pcbnew.FromMM(0.35))
    default.SetViaDiameter(pcbnew.FromMM(0.80))
    default.SetViaDrill(pcbnew.FromMM(0.40))

    def add(name, clearance, width):
        netclass = pcbnew.NETCLASS(name)
        netclass.SetClearance(pcbnew.FromMM(clearance))
        netclass.SetTrackWidth(pcbnew.FromMM(width))
        netclass.SetViaDiameter(pcbnew.FromMM(0.80))
        netclass.SetViaDrill(pcbnew.FromMM(0.40))
        settings.SetNetclass(name, netclass)

    add("supply", 0.20, 0.50)
    add("coil", 0.20, 0.80)
    # 0.2 mm inside a domain. A TO-92 has its pins 2.54 mm apart, so a 0.6 mm
    # class clearance does not fit on the transistor itself. The 0.6 mm
    # isolation is a class-to-class rule written into the Specctra file.
    add("reed", 0.20, 0.35)
    add("can", 0.20, 0.35)
    add("up", 0.20, 0.35)
    add("dn", 0.20, 0.35)
    supply = {"GND", "+5V", "+3V3", "DEV_5V"}
    for name in net_names:
        if name.startswith("unconnected"):
            continue
        kind = domain(name)
        if kind == "mcu" and name in WIDE:
            kind = "coil"
        elif kind == "mcu" and name in supply:
            kind = "supply"
        elif kind == "mcu":
            continue
        settings.SetNetclassPatternAssignment(name, kind)


def patch_dsn(path):
    """Freerouting reads isolation as a class_class scope, and it will run a track
    up to a keepout. The keepouts are the milled slots, so they grow by the
    copper-to-edge gap before the router sees them."""
    import re

    text = path.read_text()
    grown = []

    def grow(match):
        nums = [int(v) for v in match.group(1).split()]
        xs, ys = nums[0::2], nums[1::2]
        margin = 500
        x0, x1 = min(xs) - margin, max(xs) + margin
        y0, y1 = min(ys) - margin, max(ys) + margin
        grown.append(1)
        coords = f"{x0} {y0}  {x1} {y0}  {x1} {y1}  {x0} {y1}  {x0} {y0}"
        return f'(keepout "" (polygon signal 0  {coords}))'

    text = re.sub(r'\(keepout "" \(polygon signal 0\s+([0-9\-\s]+)\)\)', grow, text)
    pairs = []
    islands = ["reed", "can", "up", "dn"]
    others = ["kicad_default", "supply", "coil"]
    for i, left in enumerate(islands):
        for right in others:
            pairs.append((left, right))
        for right in islands[i + 1 :]:
            pairs.append((left, right))
    blocks = []
    for left, right in pairs:
        blocks.append(
            "    (class_class\n"
            f"      (classes {left} {right})\n"
            "      (rule\n"
            "        (clearance 600)\n"
            "      )\n"
            "    )"
        )
    # The class pairs belong inside the network scope, immediately before it closes.
    closing = "  )\n  (wiring"
    if closing not in text:
        raise SystemExit("dsn network close not found")
    text = text.replace(closing, "\n".join(blocks) + "\n" + closing, 1)
    # Pull the routing boundary in so copper stays off the outer edge.
    text = text.replace(
        "(boundary\n      (path pcb 0  120000 -112000  0 -112000  0 0  120000 0  120000 -112000)",
        "(boundary\n      (path pcb 0  119500 -111500  500 -111500  500 -500  119500 -500  119500 -111500)",
    )
    path.write_text(text)
    print(f"  dsn keepouts grown: {len(grown)}, class pairs: {len(pairs)}")


def region_for(nets):
    hits = [domain(n) for n in nets if domain(n) != "mcu"]
    if not hits:
        return "mcu"
    return hits[0]


class Router:
    def __init__(self, board, pads_by_net, holes, walls):
        self.board = board
        self.pads_by_net = pads_by_net
        self.holes = holes
        self.walls = walls
        self.nx = int(BOARD_W / GRID) + 2
        self.ny = int(BOARD_H / GRID) + 2
        self.tracks = []
        self.vias = []

    def cell(self, v):
        return int(round(v / GRID))

    def _mask(self, net, half):
        masks = [bytearray(self.nx * self.ny), bytearray(self.nx * self.ny)]
        mine = domain(net)

        def mark(x0, y0, x1, y1, rad, layers=(0, 1)):
            gx0 = max(0, int((min(x0, x1) - rad) / GRID) - 1)
            gx1 = min(self.nx - 1, int((max(x0, x1) + rad) / GRID) + 1)
            gy0 = max(0, int((min(y0, y1) - rad) / GRID) - 1)
            gy1 = min(self.ny - 1, int((max(y0, y1) + rad) / GRID) + 1)
            r2 = rad * rad
            for gy in range(gy0, gy1 + 1):
                cy = gy * GRID
                row = gy * self.nx
                for gx in range(gx0, gx1 + 1):
                    cx = gx * GRID
                    qx = min(max(cx, min(x0, x1)), max(x0, x1))
                    qy = min(max(cy, min(y0, y1)), max(y0, y1))
                    if (cx - qx) ** 2 + (cy - qy) ** 2 <= r2:
                        for layer in layers:
                            masks[layer][row + gx] = 1

        for onet, pads in self.pads_by_net.items():
            if onet == net:
                continue
            need = ISO if domain(onet) != mine else CLR
            for p in pads:
                bb = p.GetBoundingBox()
                layers = (0, 1) if p.GetDrillSize().x else (0,)
                mark(bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6, need + half, layers)
        for x1, y1, x2, y2, w, onet, olayer in self.tracks:
            if onet == net:
                continue
            need = ISO if domain(onet) != mine else CLR
            mark(x1, y1, x2, y2, need + half + w / 2, (olayer,))
        for vx, vy, onet in self.vias:
            if onet == net:
                continue
            need = ISO if domain(onet) != mine else CLR
            mark(vx, vy, vx, vy, need + half + 0.45)
        for x1, y1, x2, y2 in self.walls:
            mark(x1, y1, x2, y2, half + 0.15)
        # Antenna end: no copper.
        mark(50, 69, 72, 98, half)
        for p in self.pads_by_net.get(net, []):
            bb = p.GetBoundingBox()
            gx0 = max(0, self.cell(bb.GetLeft() / 1e6))
            gx1 = min(self.nx - 1, self.cell(bb.GetRight() / 1e6))
            gy0 = max(0, self.cell(bb.GetTop() / 1e6))
            gy1 = min(self.ny - 1, self.cell(bb.GetBottom() / 1e6))
            for gy in range(min(gy0, gy1), max(gy0, gy1) + 1):
                for gx in range(min(gx0, gx1), max(gx0, gx1) + 1):
                    if p.HitTest(pcbnew.VECTOR2I(mm(gx * GRID), mm(gy * GRID))):
                        masks[0][gy * self.nx + gx] = 0
                        if p.GetDrillSize().x:
                            masks[1][gy * self.nx + gx] = 0
        return masks

    def _via_ok(self, x, y):
        if x < 1.3 or y < 1.3 or x > BOARD_W - 1.3 or y > BOARD_H - 1.3:
            return False
        if 50 < x < 72 and 69 < y < 98:
            return False
        for hx, hy, d in self.holes:
            if (x - hx) ** 2 + (y - hy) ** 2 < (0.45 + 0.25 + d / 2) ** 2:
                return False
        for vx, vy, _onet in self.vias:
            if (x - vx) ** 2 + (y - vy) ** 2 < 0.85 ** 2:
                return False
        return True

    def _pad_cells(self, pads):
        groups = []
        for p in pads:
            bb = p.GetBoundingBox()
            cells = []
            gx0, gx1 = self.cell(bb.GetLeft() / 1e6), self.cell(bb.GetRight() / 1e6)
            gy0, gy1 = self.cell(bb.GetTop() / 1e6), self.cell(bb.GetBottom() / 1e6)
            for gy in range(min(gy0, gy1), max(gy0, gy1) + 1):
                for gx in range(min(gx0, gx1), max(gx0, gx1) + 1):
                    if p.HitTest(pcbnew.VECTOR2I(mm(gx * GRID), mm(gy * GRID))):
                        cells.append((gx, gy))
            if not cells:
                pos = p.GetPosition()
                cells.append((self.cell(pos.x / 1e6), self.cell(pos.y / 1e6)))
            groups.append(cells)
        return groups

    def route(self, net, pads):
        if len(pads) < 2:
            return True
        w = width_of(net)
        mask = self._mask(net, w / 2)
        groups = self._pad_cells(pads)
        connected = set(groups[0])
        ok = True
        for target in groups[1:]:
            path = self._astar(connected, set(target), mask, net)
            if not path:
                ok = False
                print(f"  open  {net}  ({len(connected)} cells already joined)")
                continue
            self._commit(path, net, w)
            connected.update((x, y) for x, y, _layer in path)
        return ok

    def _astar(self, starts, goals, mask, net):
        heap = []
        best = {}
        parent = {}
        goal_list = list(goals)
        for gx, gy in starts:
            for layer in (0, 1):
                heap.append((0, 0, gx, gy, layer))
                best[(gx, gy, layer)] = 0
        seen = 0
        while heap:
            _f, g, x, y, layer = heapq.heappop(heap)
            if best.get((x, y, layer), 1e18) != g:
                continue
            seen += 1
            if g > 0 and (x, y) in goals:
                return self._rebuild(parent, (x, y, layer))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.nx and 0 <= ny < self.ny):
                    continue
                px, py = nx * GRID, ny * GRID
                if px < EDGE or py < EDGE or px > BOARD_W - EDGE or py > BOARD_H - EDGE:
                    continue
                if mask[layer][ny * self.nx + nx]:
                    continue
                ng = g + 1
                key = (nx, ny, layer)
                if ng >= best.get(key, 1e18):
                    continue
                best[key] = ng
                parent[key] = (x, y, layer)
                hx = min(abs(nx - gx) + abs(ny - gy) for gx, gy in goal_list)
                # Prefer the back layer for the ground net so the front stays free.
                bias = 0.4 if net == "GND" and layer == 0 else 0
                heapq.heappush(heap, (ng + hx + bias, ng, nx, ny, layer))
            if self._via_ok(x * GRID, y * GRID):
                other = 1 - layer
                if not mask[other][y * self.nx + x]:
                    ng = g + 4
                    key = (x, y, other)
                    if ng < best.get(key, 1e18):
                        best[key] = ng
                        parent[key] = (x, y, layer)
                        heapq.heappush(heap, (ng, ng, x, y, other))
            if seen > 250000:
                return None
        return None

    @staticmethod
    def _rebuild(parent, key):
        path = [key]
        while key in parent:
            key = parent[key]
            path.append(key)
        path.reverse()
        return path

    def _commit(self, path, net, w):
        run = [path[0]]
        for prev, cur in zip(path, path[1:]):
            if cur[2] != prev[2]:
                self._flush(run, net, w)
                vx, vy = cur[0] * GRID, cur[1] * GRID
                via = pcbnew.PCB_VIA(self.board)
                via.SetPosition(pcbnew.VECTOR2I(mm(vx), mm(vy)))
                via.SetWidth(mm(0.80))
                via.SetDrill(mm(0.40))
                via.SetViaType(pcbnew.VIATYPE_THROUGH)
                via.SetNet(self.board.FindNet(net))
                self.board.Add(via)
                self.vias.append((vx, vy, net))
                run = [cur]
            else:
                run.append(cur)
        self._flush(run, net, w)

    def _flush(self, run, net, w):
        if len(run) < 2:
            return
        layer = pcbnew.F_Cu if run[0][2] == 0 else pcbnew.B_Cu
        pts = [(p[0] * GRID, p[1] * GRID) for p in run]
        merged = [pts[0]]
        for i in range(1, len(pts) - 1):
            ax, ay = merged[-1]
            bx, by = pts[i]
            cx, cy = pts[i + 1]
            if (bx - ax) * (cy - by) == (by - ay) * (cx - bx):
                continue
            merged.append(pts[i])
        merged.append(pts[-1])
        netinfo = self.board.FindNet(net)
        for (x1, y1), (x2, y2) in zip(merged, merged[1:]):
            if (x1, y1) == (x2, y2):
                continue
            t = pcbnew.PCB_TRACK(self.board)
            t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
            t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
            t.SetWidth(mm(w))
            t.SetLayer(layer)
            t.SetNet(netinfo)
            self.board.Add(t)
            self.tracks.append((x1, y1, x2, y2, w, net, 0 if layer == pcbnew.F_Cu else 1))


def slot_wall(fp, x1, y1, x2, y2):
    corners = [xform(fp, x, y) for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2))]
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    return min(xs), min(ys), max(xs), max(ys)


def main():
    subprocess.check_call(
        ["kicad-cli", "sch", "export", "netlist", "-o", str(OUT / "windlass_home.net"), str(OUT / "windlass_home.kicad_sch")],
        stdout=subprocess.DEVNULL,
    )
    comps, nets = parse_netlist(OUT / "windlass_home.net")
    board = pcbnew.NewBoard(str(OUT / "windlass_home.kicad_pcb"))
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(CLR)
    ds.m_TrackMinWidth = mm(0.20)
    ds.m_ViasMinSize = mm(0.70)
    ds.m_ViasMinDrill = mm(0.35)
    ds.m_CopperEdgeClearance = mm(0.30)
    ds.m_HoleClearance = mm(0.25)
    ds.m_HoleToHoleMin = mm(0.25)
    ds.SetCopperLayerCount(2)
    for a, b in (
        ((0, 0), (BOARD_W, 0)),
        ((BOARD_W, 0), (BOARD_W, BOARD_H)),
        ((BOARD_W, BOARD_H), (0, BOARD_H)),
        ((0, BOARD_H), (0, 0)),
    ):
        add_line(board, a[0], a[1], b[0], b[1])

    net_by_name = {}
    for i, (name, _nodes) in enumerate(nets, start=1):
        item = pcbnew.NETINFO_ITEM(board, name, i)
        board.Add(item)
        net_by_name[name] = item

    footprints = {}
    for ref, value, fpname in comps:
        folder, name = fp_file(fpname)
        fp = pcbnew.FootprintLoad(folder, name)
        if fp is None:
            raise SystemExit(f"missing footprint {fpname}")
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Value().SetVisible(False)
        footprints[ref] = fp

    nets_of = {}
    pin_net = {}
    for name, nodes in nets:
        for ref, pin in nodes:
            pin_net[(ref, pin)] = name
            nets_of.setdefault(ref, set()).add(name)

    occupied = []
    missing = [ref for ref in ANCHORS if ref not in footprints]
    if missing:
        raise SystemExit(f"anchors not in the netlist: {missing}")
    for ref, (x, y, rot) in ANCHORS.items():
        fp = footprints[ref]
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        occupied.append(rect_of(fp, 0.45))
    # Antenna keepout. The rest of the DevKit shadow can hold parts shorter than the socket.
    occupied.append((50.0, 69.0, 72.0, 98.0))
    UNDER_DEVKIT = (8.0, 73.2, 62.0, 92.2)

    def fits(fp, x, y, rot, dom, ref):
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        rect = rect_of(fp, 0.30)
        if rect[0] < 1.0 or rect[1] < 1.0 or rect[2] > BOARD_W - 1.0 or rect[3] > BOARD_H - 1.0:
            return None
        if any(overlaps(rect, o) for o in occupied):
            return None
        if dom == "mcu" and any(overlaps(rect, isl) for isl in ISLANDS):
            return None
        if overlaps(rect, UNDER_DEVKIT) and ref in TALL:
            return None
        return rect

    def pack(ref):
        fp = footprints[ref]
        dom = region_for(nets_of.get(ref, ()))
        boxes = REGIONS[dom]
        seeds = []
        for net in nets_of.get(ref, ()):
            if net in ("GND", "+3V3", "+5V"):
                continue
            for other, ofp in footprints.items():
                if other == ref or other not in placed:
                    continue
                for pad in ofp.Pads():
                    if pin_net.get((other, pad.GetNumber())) == net:
                        pos = pad.GetPosition()
                        seeds.append((pos.x / 1e6, pos.y / 1e6))
        seeds.sort()

        def inside(x, y):
            return any(b[0] <= x <= b[2] and b[1] <= y <= b[3] for b in boxes)

        if not seeds:
            home = boxes[0]
            seeds = [((home[0] + home[2]) / 2, (home[1] + home[3]) / 2)]
        for tx, ty in seeds[:6]:
            for radius in (0, 3, 6, 9, 13, 18, 24, 32, 44):
                steps = 1 if radius == 0 else 16
                for k in range(steps):
                    ang = 2 * math.pi * k / steps
                    x = tx + radius * math.cos(ang)
                    y = ty + radius * math.sin(ang)
                    if not inside(x, y):
                        continue
                    for rot in (0, 90, 180, 270):
                        rect = fits(fp, x, y, rot, dom, ref)
                        if rect is not None:
                            return rect
        for home in boxes:
            y = home[1] + 1.5
            while y < home[3]:
                x = home[0] + 1.5
                while x < home[2]:
                    for rot in (0, 90):
                        rect = fits(fp, x, y, rot, dom, ref)
                        if rect is not None:
                            return rect
                    x += 1.27
                y += 1.27
        return None

    anchor_rects = [(ref, rect_of(footprints[ref], 0.0)) for ref in ANCHORS]
    for i, (ra, a) in enumerate(anchor_rects):
        for rb, b in anchor_rects[i + 1 :]:
            if overlaps(a, b):
                print(f"  ANCHOR OVERLAP {ra} {rb} {a} {b}")

    placed = set(ANCHORS)
    order = sorted(
        (ref for ref in footprints if ref not in ANCHORS),
        key=lambda r: (
            -footprints[r].GetBoundingBox(False, False).GetWidth()
            * footprints[r].GetBoundingBox(False, False).GetHeight(),
            r,
        ),
    )
    for ref in order:
        rect = pack(ref)
        if rect is None:
            raise RuntimeError(f"no place for {ref} in {region_for(nets_of.get(ref, ()))}")
        occupied.append(rect)
        placed.add(ref)
        print(f"  placed {ref:8} {region_for(nets_of.get(ref, ())):4}")

    # Anchors must not cover each other.
    anchor_rects = [(ref, rect_of(footprints[ref], 0.0)) for ref in ANCHORS]
    for i, (ra, a) in enumerate(anchor_rects):
        for rb, b in anchor_rects[i + 1 :]:
            if overlaps(a, b):
                print(f"  ANCHOR OVERLAP {ra} {rb}")

    pads_by_net = {name: [] for name, _ in nets}
    holes = []
    for ref, fp in footprints.items():
        board.Add(fp)
        for pad in fp.Pads():
            pos = pad.GetPosition()
            drill = pad.GetDrillSize().x / 1e6
            if drill:
                holes.append((pos.x / 1e6, pos.y / 1e6, drill))
            name = pin_net.get((ref, pad.GetNumber()))
            if name:
                pad.SetNet(net_by_name[name])
                pads_by_net[name].append(pad)

    walls = []
    slots = {
        "U4": (4.3, -3.6, 8.6, 3.6),
        "U9": (4.3, -3.6, 8.6, 3.6),
        "U_RD": (2.2, -1.2, 5.4, 3.8),
        "U_PG": (2.2, -1.2, 5.4, 3.8),
        "U6": (2.2, -1.2, 5.4, 3.8),
        "U7": (2.2, -1.2, 5.4, 3.8),
        "U_TX": (2.2, -1.0, 5.4, 8.6),
        "U_RX": (2.2, -1.0, 5.4, 8.6),
    }
    for ref, local in slots.items():
        box = slot_wall(footprints[ref], *local)
        walls.append(box)
        x1, y1, x2, y2 = box
        add_line(board, x1, y1, x2, y1)
        add_line(board, x2, y1, x2, y2)
        add_line(board, x2, y2, x1, y2)
        add_line(board, x1, y2, x1, y1)

    corners = ((4.0, 4.0), (BOARD_W - 4.0, 4.0), (4.0, BOARD_H - 4.0), (BOARD_W - 4.0, BOARD_H - 4.0))
    placed_holes = []
    bodies = [rect_of(fp, 0.0) for fp in footprints.values()]
    for i, (cx, cy) in enumerate(corners, start=1):
        hole = pcbnew.FootprintLoad(str(FP / "MountingHole.pretty"), "MountingHole_3.2mm_M3")
        hole.SetReference(f"H{i}")
        hole.SetValue("M3")
        hole.Reference().SetVisible(False)
        hole.Value().SetVisible(False)
        found = None
        for step in range(0, 48):
            for dx, dy in ((0, 0), (step, 0), (-step, 0), (0, step), (0, -step), (step, step), (-step, step), (step, -step), (-step, -step)):
                x, y = cx + dx * (1 if cx < BOARD_W / 2 else -1), cy + dy * (1 if cy < BOARD_H / 2 else -1)
                if not (3 < x < BOARD_W - 3 and 3 < y < BOARD_H - 3):
                    continue
                hole.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                hrect = rect_of(hole, 0.8)
                if any(overlaps(hrect, body) for body in bodies):
                    continue
                found = (x, y)
                break
            if found:
                break
        if found is None:
            print(f"  hole H{i} has no clear corner")
            continue
        board.Add(hole)
        placed_holes.append(hole)
        bodies.append(rect_of(hole, 0.0))
        print(f"  hole H{i} at {found[0]:.0f},{found[1]:.0f}")
    for fitted in placed_holes:
        for pad in fitted.Pads():
            pos = pad.GetPosition()
            holes.append((pos.x / 1e6, pos.y / 1e6, pad.GetDrillSize().x / 1e6))

    apply_rules(board, [name for name, _nodes in nets])

    if os.environ.get("PLACE_ONLY") or os.environ.get("FREEROUTE"):
        board.Save(str(OUT / "windlass_home.kicad_pcb"))
        if os.environ.get("FREEROUTE"):
            dsn = OUT / "windlass_home.dsn"
            pcbnew.ExportSpecctraDSN(board, str(dsn))
            patch_dsn(dsn)
            print(f"dsn {dsn}")
        else:
            print("placement only")
        return

    router = Router(board, pads_by_net, holes, walls)

    def span(name):
        pts = [(p.GetPosition().x, p.GetPosition().y) for p in pads_by_net[name]]
        if len(pts) < 2:
            return 0
        return math.hypot(max(p[0] for p in pts) - min(p[0] for p in pts), max(p[1] for p in pts) - min(p[1] for p in pts))

    failed = []
    ordered = sorted(nets, key=lambda item: span(item[0]))
    for index, (name, _nodes) in enumerate(ordered, start=1):
        if index % 20 == 0:
            print(f"  routing {index}/{len(ordered)} {name}", flush=True)
        if not router.route(name, pads_by_net[name]):
            failed.append(name)
    print(f"unrouted {len(failed)}: {failed}")
    # Back-side ground pour for the controller side only. It stops at the isolation column.
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(board.FindNet("GND"))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    zone.SetLocalClearance(pcbnew.FromMM(0.30))
    zone.SetMinThickness(pcbnew.FromMM(0.25))
    zone.SetThermalReliefGap(pcbnew.FromMM(0.30))
    zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.40))
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((1.5, 12.0), (72.0, 12.0), (72.0, 110.0), (1.5, 110.0)):
        outline.Append(int(x * 1e6), int(y * 1e6))
    outline.NewHole()
    for x, y in ((50.0, 69.0), (50.0, 98.0), (72.0, 98.0), (72.0, 69.0)):
        outline.Append(int(x * 1e6), int(y * 1e6))
    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(str(OUT / "windlass_home.kicad_pcb"))
    print(f"wrote {OUT / 'windlass_home.kicad_pcb'}")


if __name__ == "__main__":
    main()
