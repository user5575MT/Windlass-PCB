#!/usr/bin/env python3
"""Place and route the integrated controller. Does not touch kicad/."""
from __future__ import annotations

import heapq
import math
import os
import re
from collections import deque
from pathlib import Path

os.environ.setdefault("KICAD10_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
os.environ.setdefault("KICAD10_SYMBOL_DIR", "/usr/share/kicad/symbols")

import pcbnew

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "kicad11"
FP = Path("/usr/share/kicad/footprints")

BOARD_W = 200.0
BOARD_H = 160.0
GRID = 0.125
CLR = 0.20
EDGE = 0.50
ISO_GAP = 1.60  # surface gap between a barrier net and any other net
PLANE_MARGIN = 2.20  # inner-plane keepout beyond barrier pads

# Nets that must not share a plane with GND, and must keep ISO_GAP on the surface.
BARRIER = {
    "REED_RET", "REED_3V3", "REED_ISO", "REED_SIG", "LOFRANS_NODE", "DRY_A",
    "UP_RET", "UP_FIELD", "UP_LED_A",
    "DN_RET", "DN_FIELD", "DN_LED_A",
    "GND_CAN", "ISO_5V", "CAN_H", "CAN_L", "NMEA_SHIELD",
    "UP_COM", "UP_NO", "DN_COM", "DN_NO",
}
# These stay on the top layer. A through via would put a ring on the ground plane.
NO_VIA = set(BARRIER)


def width_of(net: str) -> float:
    if net in ("UP_COM", "UP_NO", "DN_COM", "DN_NO"):
        return 1.20
    if net in ("VIN_12", "VIN_MCU", "+12V_MCU", "VIN_COIL", "+12V_COIL", "COIL_12"):
        return 0.80
    if net in ("SERIES_NODE", "UP_LOW", "DN_LOW", "SW_A", "SW_B", "IGN_A", "IGN_B"):
        return 0.50
    if net in ("GND_CAN", "ISO_5V", "CAN_H", "CAN_L", "REED_3V3", "REED_RET"):
        return 0.40
    if net.startswith("USB_"):
        return 0.20
    return 0.25


ANCHORS = {
    # ref: x, y, rotation. Y increases downward.
    # USB and the 12 V buck sit along the top-left. Relays occupy the left edge.
    # The ESP32 antenna points at the top edge. Reed, sense and CAN each have
    # their own strip so an isolated net does not cross the logic area.
    "U3": (148, 46, 0),
    "J_USB": (20, 16, 0),
    "U20": (56, 28, 0),
    "Q_MCU": (88, 16, 0),
    "Q_COIL": (88, 36, 0),
    "K_UP": (18, 64, 0),
    "K_DN": (18, 102, 0),
    "U11": (96, 68, 0),
    "U4": (76, 120, 0),
    "U5": (110, 118, 0),
    "U6": (132, 118, 0),
    "U7": (154, 118, 0),
    "U10": (174, 76, 0),
    "U9": (170, 104, 0),
    "J_PWR": (16, 144, 0),
    "J_PERM": (46, 144, 0),
    "J_CONTACT": (32, 130, 0),
    "J_REED": (94, 148, 0),
    "J_SENSE": (144, 148, 0),
    "J_NMEA": (186, 144, 0),
}

USB_BOX = (8.0, 8.0, 48.0, 42.0)
POWER_BOX = (36.0, 8.0, 122.0, 50.0)
RELAY_BOX = (8.0, 48.0, 64.0, 154.0)
LOGIC_BOX = (60.0, 48.0, 142.0, 102.0)
ESP_BOX = (116.0, 48.0, 142.0, 100.0)
REED_BOX = (58.0, 104.0, 124.0, 156.0)
SENSE_BOX = (118.0, 104.0, 164.0, 156.0)
CAN_BOX = (160.0, 68.0, 196.0, 156.0)
FALLBACK_BOX = (8.0, 8.0, 192.0, 152.0)

REGION_OF = {}
for _refs, _box in (
    (("R15", "R16", "R17", "R18", "R19", "C13", "U_ESD"), USB_BOX),
    (("C12", "C30A", "C30B", "C30C", "C30I", "C90", "L20", "F_MCU", "F_COIL",
      "D_TVS_MCU", "D_TVS_COIL", "D_Z_MCU", "D_Z_COIL", "R_MCU_G", "R_COIL_G"), POWER_BOX),
    (("D60", "D70", "D61", "D71", "R80", "R_COILFEED", "R_SWLINK", "R_IGNLINK",
      "Q_UP", "Q_DN", "Q_SERIES", "Q_CLAMP_UP", "Q_CLAMP_DN",
      "R50", "R51", "R60", "R61", "R70", "R71"), RELAY_BOX),
    (("C10", "C11", "C51", "R10", "R11", "R12", "R13", "R14", "R92", "R93",
      "SW_BOOT", "SW_RST", "TP_TX", "TP_RX"), ESP_BOX),
    (("C20", "C21", "C22", "C24", "R20", "R22", "R23", "R24", "D20", "D21", "JP_REED"), REED_BOX),
    (("C31", "C41", "D30", "D40", "R30", "R30P", "R40", "R40P"), SENSE_BOX),
    (("C91", "C92", "C93", "JP1", "R90", "R91", "R94"), CAN_BOX),
):
    for _ref in _refs:
        REGION_OF[_ref] = _box


def parse_netlist(path: Path):
    text = path.read_text(encoding="utf-8")
    comp_block = text.split("(components")[1].split("(groups)")[0]
    comps = []
    for chunk in comp_block.split("(comp")[1:]:
        ref = re.search(r'\(ref "([^"]+)"\)', chunk).group(1)
        value = re.search(r'\(value "([^"]*)"\)', chunk).group(1)
        fp = re.search(r'\(footprint "([^"]+)"\)', chunk).group(1)
        comps.append((ref, value, fp))
    net_block = text.split("(nets")[1]
    nets = []
    for chunk in net_block.split("(net")[1:]:
        name = re.search(r'\(name "([^"]*)"\)', chunk).group(1)
        nodes = re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', chunk)
        if name and nodes:
            nets.append((name, nodes))
    return comps, nets


def fp_file(footprint: str):
    lib, name = footprint.split(":")
    if lib == "windlass":
        return str(OUT / "footprints.pretty"), name
    return str(FP / f"{lib}.pretty"), name


def mm(v) -> int:
    return int(round(v * 1_000_000))


def add_line(board, x1, y1, x2, y2, layer="Edge.Cuts", width=0.1):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    seg.SetLayer(getattr(pcbnew, layer) if hasattr(pcbnew, layer) else board.GetLayerID(layer))
    seg.SetWidth(mm(width))
    board.Add(seg)


def add_text(board, x, y, text, layer="F.SilkS", size=0.9):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetLayer(pcbnew.F_SilkS if layer == "F.SilkS" else board.GetLayerID(layer))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(0.15))
    board.Add(t)


def hit(pad, x, y) -> bool:
    return bool(pad.HitTest(pcbnew.VECTOR2I(mm(x), mm(y))))


class Router:
    def __init__(self, board, pads_by_net):
        self.board = board
        self.pads_by_net = pads_by_net
        self.nx = int(BOARD_W / GRID) + 1
        self.ny = int(BOARD_H / GRID) + 1
        self.tracks = []  # (x1,y1,x2,y2,width,net,layer)
        self.vias = []  # (x,y,net)
        self.walls = []  # (x1,y1,x2,y2) copper is not allowed here
        self.holes = []  # (x,y,drill)
        for pads in pads_by_net.values():
            for p in pads:
                d = p.GetDrillSize().x / 1e6
                if d > 0:
                    pos = p.GetPosition()
                    self.holes.append((pos.x / 1e6, pos.y / 1e6, d))

    def cell(self, v):
        return int(round(v / GRID))

    def _blocked_point(self, x, y, layer, net, half):
        if x < EDGE or y < EDGE or x > BOARD_W - EDGE or y > BOARD_H - EDGE:
            return True
        gap_need = ISO_GAP if net in BARRIER else CLR
        for onet, pads in self.pads_by_net.items():
            if onet == net:
                continue
            need = ISO_GAP if (net in BARRIER) != (onet in BARRIER) else CLR
            need = max(need, gap_need if net in BARRIER or onet in BARRIER else CLR)
            if (net in BARRIER) == (onet in BARRIER) and net not in BARRIER:
                need = CLR
            elif (net in BARRIER) != (onet in BARRIER):
                need = ISO_GAP
            else:
                need = CLR
            for p in pads:
                pos = p.GetPosition()
                px, py = pos.x / 1e6, pos.y / 1e6
                # cheap reject
                if abs(px - x) > 8 and abs(py - y) > 8:
                    continue
                bb = p.GetBoundingBox()
                # expand bbox by need + half
                extra = (need + half) * 1e6
                if bb.GetLeft() - extra <= mm(x) <= bb.GetRight() + extra and bb.GetTop() - extra <= mm(y) <= bb.GetBottom() + extra:
                    # refine with hit test on a slightly padded basis: distance from pad copper
                    if p.HitTest(pcbnew.VECTOR2I(mm(x), mm(y))):
                        return True
                    # sample clearance: if the point is within need+half of copper, block.
                    # Approximate with bbox of the pad expanded, then reject if a nearby
                    # point on the pad is closer than need+half.
                    cx = min(max(x, bb.GetLeft() / 1e6), bb.GetRight() / 1e6)
                    cy = min(max(y, bb.GetTop() / 1e6), bb.GetBottom() / 1e6)
                    if (x - cx) ** 2 + (y - cy) ** 2 < (need + half) ** 2:
                        # bbox corner can be outside a round pad; accept if the
                        # nearest bbox point is not actually near copper.
                        if p.HitTest(pcbnew.VECTOR2I(mm(cx), mm(cy))) or min(abs(x - px), abs(y - py)) < need + half:
                            return True
        for x1, y1, x2, y2, w, onet, olayer in self.tracks:
            if onet == net:
                continue
            need = ISO_GAP if (net in BARRIER) != (onet in BARRIER) else CLR
            if self._seg_dist(x, y, x1, y1, x2, y2) < need + half + w / 2:
                return True
        for vx, vy, onet in self.vias:
            if onet == net:
                continue
            need = ISO_GAP if (net in BARRIER) != (onet in BARRIER) else CLR
            if (x - vx) ** 2 + (y - vy) ** 2 < (need + half + 0.30) ** 2:
                return True
        return False

    @staticmethod
    def _seg_dist(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return ((px - (x1 + t * dx)) ** 2 + (py - (y1 + t * dy)) ** 2) ** 0.5

    def _mask(self, net, half):
        """1 = blocked for this net's centerline. Own pads are cleared."""
        masks = [bytearray(self.nx * self.ny), bytearray(self.nx * self.ny)]
        def mark_rect(x0, y0, x1, y1, layers=(0, 1)):
            gx0 = max(0, int(min(x0, x1) / GRID))
            gx1 = min(self.nx - 1, int(max(x0, x1) / GRID))
            gy0 = max(0, int(min(y0, y1) / GRID))
            gy1 = min(self.ny - 1, int(max(y0, y1) / GRID))
            for layer in layers:
                for gy in range(gy0, gy1 + 1):
                    row = gy * self.nx
                    for gx in range(gx0, gx1 + 1):
                        masks[layer][row + gx] = 1

        def mark_near(x0, y0, x1, y1, rad, layers=(0, 1)):
            """Block cells whose centre is within rad of the copper rectangle."""
            gx0 = max(0, int((x0 - rad) / GRID) - 1)
            gx1 = min(self.nx - 1, int((x1 + rad) / GRID) + 1)
            gy0 = max(0, int((y0 - rad) / GRID) - 1)
            gy1 = min(self.ny - 1, int((y1 + rad) / GRID) + 1)
            r2 = rad * rad
            for gy in range(gy0, gy1 + 1):
                cy = gy * GRID
                row = gy * self.nx
                for gx in range(gx0, gx1 + 1):
                    cx = gx * GRID
                    qx = min(max(cx, x0), x1)
                    qy = min(max(cy, y0), y1)
                    if (cx - qx) * (cx - qx) + (cy - qy) * (cy - qy) <= r2:
                        for layer in layers:
                            masks[layer][row + gx] = 1

        barrier = net in BARRIER
        for onet, pads in self.pads_by_net.items():
            if onet == net:
                continue
            need = ISO_GAP if barrier != (onet in BARRIER) else CLR
            for p in pads:
                bb = p.GetBoundingBox()
                layers = (0, 1) if p.GetDrillSize().x > 0 else (0,)
                mark_near(bb.GetLeft() / 1e6, bb.GetTop() / 1e6,
                          bb.GetRight() / 1e6, bb.GetBottom() / 1e6, need + half, layers)
        for x1, y1, x2, y2, w, onet, olayer in self.tracks:
            if onet == net:
                continue
            need = ISO_GAP if barrier != (onet in BARRIER) else CLR
            rad = need + half + w / 2
            steps = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / GRID) + 1
            for i in range(steps + 1):
                t = i / max(steps, 1)
                cx = x1 + (x2 - x1) * t
                cy = y1 + (y2 - y1) * t
                mark_rect(cx - rad, cy - rad, cx + rad, cy + rad, (olayer,))
        for vx, vy, onet in self.vias:
            if onet == net:
                continue
            need = ISO_GAP if barrier != (onet in BARRIER) else CLR
            rad = need + half + 0.30
            mark_rect(vx - rad, vy - rad, vx + rad, vy + rad)
        for p in self.pads_by_net.get(net, []):
            bb = p.GetBoundingBox()
            gx0 = max(0, int((bb.GetLeft() / 1e6) / GRID))
            gx1 = min(self.nx - 1, int((bb.GetRight() / 1e6) / GRID))
            gy0 = max(0, int((bb.GetTop() / 1e6) / GRID))
            gy1 = min(self.ny - 1, int((bb.GetBottom() / 1e6) / GRID))
            for gy in range(gy0, gy1 + 1):
                for gx in range(gx0, gx1 + 1):
                    if hit(p, gx * GRID, gy * GRID):
                        for layer in (0, 1):
                            if p.GetDrillSize().x == 0 and layer == 1:
                                continue
                            masks[layer][gy * self.nx + gx] = 0
        for x1, y1, x2, y2 in self.walls:
            mark_rect(min(x1, x2) - EDGE, min(y1, y2) - EDGE, max(x1, x2) + EDGE, max(y1, y2) + EDGE)
        # Isolated nets stay out of the USB connector and the module. A long
        # detour across either one seals fine-pitch pads that cannot use a via.
        if barrier:
            for rect in ((6, 4, 48, 34), (118, 28, 166, 72)):
                mark_rect(*rect)
        return masks

    def via_fanout(self, net, pads):
        """Drop each surface pad to the back layer before the maze runs."""
        if net in NO_VIA:
            return
        w = width_of(net)
        half = w / 2
        self._mask_cache = self._mask(net, half)
        for p in pads:
            if p.GetDrillSize().x > 0:
                continue
            pos = p.GetPosition()
            cx, cy = pos.x / 1e6, pos.y / 1e6
            gx, gy = self.cell(cx), self.cell(cy)
            placed = False
            for dist in (1.05, 1.45, 1.9, 2.4):
                for dx, dy in ((dist, 0), (-dist, 0), (0, dist), (0, -dist)):
                    x, y = cx + dx, cy + dy
                    point = pcbnew.VECTOR2I(mm(x), mm(y))
                    if any(pad.HitTest(point) for group in self.pads_by_net.values() for pad in group):
                        continue
                    if not self._via_ok(x, y, net):
                        continue
                    vx, vy = self.cell(x), self.cell(y)
                    steps = max(abs(vx - gx), abs(vy - gy), 1)
                    ray = []
                    blocked = False
                    for i in range(1, steps + 1):
                        sx = gx + (vx - gx) * i // steps
                        sy = gy + (vy - gy) * i // steps
                        if self._mask_cache[0][sy * self.nx + sx]:
                            blocked = True
                            break
                        ray.append((sx, sy, 0))
                    if blocked or not ray:
                        continue
                    self._commit([(gx, gy, 0)] + ray + [(vx, vy, 1)], net, w)
                    rad = w / 2 + CLR + half
                    for sx, sy, _layer in ray:
                        self._paint(sx * GRID - rad, sy * GRID - rad, sx * GRID + rad, sy * GRID + rad)
                    placed = True
                    break
                if placed:
                    break

    def fanout(self, net, pads):
        """Give each surface pad a short stub into open copper so the maze
        does not have to escape a fine-pitch pad while other tracks exist."""
        w = width_of(net)
        half = w / 2
        self._mask_cache = self._mask(net, half)
        own = [p for p in pads if p.GetDrillSize().x == 0]
        own.sort(key=lambda p: p.GetBoundingBox().GetWidth() * p.GetBoundingBox().GetHeight())
        for p in own:
            pos = p.GetPosition()
            cx, cy = self.cell(pos.x / 1e6), self.cell(pos.y / 1e6)
            best = []
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                ray = []
                for i in range(1, 20):
                    gx, gy = cx + dx * i, cy + dy * i
                    if not (0 <= gx < self.nx and 0 <= gy < self.ny):
                        break
                    if self._mask_cache[0][gy * self.nx + gx]:
                        break
                    ray.append((gx, gy, 0))
                if len(ray) > len(best):
                    best = ray
            if len(best) < 8:
                continue
            self._commit([(cx, cy, 0)] + best, net, w)
            # Keep the next pad of this net off the stub we just laid.
            rad = w / 2 + CLR + half
            for gx, gy, _layer in best:
                x, y = gx * GRID, gy * GRID
                self._paint(x - rad, y - rad, x + rad, y + rad)

    def _paint(self, x0, y0, x1, y1):
        gx0 = max(0, int(min(x0, x1) / GRID))
        gx1 = min(self.nx - 1, int(max(x0, x1) / GRID))
        gy0 = max(0, int(min(y0, y1) / GRID))
        gy1 = min(self.ny - 1, int(max(y0, y1) / GRID))
        for gy in range(gy0, gy1 + 1):
            row = gy * self.nx
            for gx in range(gx0, gx1 + 1):
                self._mask_cache[0][row + gx] = 1

    def route(self, net, pads):
        if len(pads) < 2:
            return True
        w = width_of(net)
        half = w / 2
        self._mask_cache = self._mask(net, half)
        groups = []
        for p in pads:
            cells = []
            bb = p.GetBoundingBox()
            x0, x1 = bb.GetLeft() / 1e6, bb.GetRight() / 1e6
            y0, y1 = bb.GetTop() / 1e6, bb.GetBottom() / 1e6
            gx0, gx1 = self.cell(x0), self.cell(x1)
            gy0, gy1 = self.cell(y0), self.cell(y1)
            for gy in range(min(gy0, gy1), max(gy0, gy1) + 1):
                for gx in range(min(gx0, gx1), max(gx0, gx1) + 1):
                    x, y = gx * GRID, gy * GRID
                    if hit(p, x, y):
                        cells.append((gx, gy))
            if not cells:
                pos = p.GetPosition()
                cells.append((self.cell(pos.x / 1e6), self.cell(pos.y / 1e6)))
            groups.append(cells)
        connected = set(groups[0])
        ok = True
        for target in groups[1:]:
            path = self._astar(connected, set(target), net, half, limit=8000)
            if not path:
                path = self._coarse_path(connected, set(target), net, half)
                if path:
                    print(f"  coarse {net}")
            if not path:
                ok = False
                print(f"  FAILED segment of {net}")
                continue
            self._commit(path, net, w)
            connected.update((x, y) for x, y, _layer in path)
        return ok

    def _astar(self, starts, goals, net, half, limit=20000):
        allow_via = net not in NO_VIA
        # starts/goals are (gx,gy) on F.Cu
        start_states = [(0, gx, gy) for gx, gy in starts]
        goal = goals
        heap = []
        seen = set()
        parent = {}
        for gx, gy in starts:
            if self._blocked_point(gx * GRID, gy * GRID, 0, net, half):
                # still allow the cell if it sits on our own pad
                pass
            heap.append((0, 0, gx, gy, 0))
        best = {}
        goal_list = list(goals)
        while heap:
            f, g, x, y, layer = heapq.heappop(heap)
            key = (x, y, layer)
            if key in seen:
                continue
            seen.add(key)
            if layer == 0 and g > 0 and (x, y) in goals:
                return self._reconstruct(parent, key)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.nx and 0 <= ny < self.ny):
                    continue
                if nx * GRID < EDGE or ny * GRID < EDGE or nx * GRID > BOARD_W - EDGE or ny * GRID > BOARD_H - EDGE:
                    continue
                if self._mask_cache[layer][ny * self.nx + nx]:
                    continue
                ng = g + 1
                nk = (nx, ny, layer)
                if nk in seen or ng >= best.get(nk, 1e18):
                    continue
                best[nk] = ng
                parent[nk] = key
                # heuristic
                hx = min(abs(nx - gx) + abs(ny - gy) for gx, gy in goal_list)
                heapq.heappush(heap, (ng + hx, ng, nx, ny, layer))
            if allow_via and (x, y, 1 - layer) not in seen:
                if self._via_ok(x * GRID, y * GRID, net):
                    nk = (x, y, 1 - layer)
                    ng = g + 6
                    if ng < best.get(nk, 1e18):
                        best[nk] = ng
                        parent[nk] = key
                        heapq.heappush(heap, (ng, ng, x, y, 1 - layer))
            if len(seen) > limit:
                if os.environ.get("ROUTE_DEBUG"):
                    xs = [s[0] for s in seen]
                    ys = [s[1] for s in seen]
                    print(f"  fine limit {len(seen)} x {min(xs)*GRID:.0f}-{max(xs)*GRID:.0f} "
                          f"y {min(ys)*GRID:.0f}-{max(ys)*GRID:.0f} goals {len(goal_list)}")
                return None
        if os.environ.get("ROUTE_DEBUG"):
            print(f"  fine exhausted {len(seen)}")
        return None

    def _coarse_path(self, starts, goals, net, half):
        """0.5 mm maze between a free cell beside each pad. Used when the
        fine search runs out of budget on a long net."""
        step = 4

        def free(gx, gy, layer):
            if not (0 <= gx < self.nx and 0 <= gy < self.ny):
                return False
            return not self._mask_cache[layer][gy * self.nx + gx]

        def portal(cells):
            for gx, gy in cells:
                if free(gx, gy, 0):
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if free(gx + dx, gy + dy, 0):
                            return (gx, gy)
            for gx, gy in cells:
                for rad in range(2, 20):
                    for dx, dy in ((rad, 0), (-rad, 0), (0, rad), (0, -rad)):
                        if free(gx + dx, gy + dy, 0):
                            return (gx + dx, gy + dy)
            return None

        a = portal(starts)
        b = portal(goals)
        if a is None or b is None:
            print(f"  no escape beside {'start' if a is None else 'goal'}")
            return None
        allow_via = net not in NO_VIA
        sx, sy = a[0] // step, a[1] // step
        gx, gy = b[0] // step, b[1] // step
        maxx, maxy = self.nx // step, self.ny // step

        def cfree(cx, cy, layer):
            # The center of the coarse cell must clear the fine mask and the edge.
            fx, fy = cx * step + step // 2, cy * step + step // 2
            x, y = fx * GRID, fy * GRID
            if x < EDGE or y < EDGE or x > BOARD_W - EDGE or y > BOARD_H - EDGE:
                return False
            return free(fx, fy, layer)

        heap = [(0, 0, sx, sy, 0)]
        seen = set()
        parent = {}
        best = {}
        found = None
        while heap:
            f, g, x, y, layer = heapq.heappop(heap)
            key = (x, y, layer)
            if key in seen:
                continue
            seen.add(key)
            if layer == 0 and (x, y) == (gx, gy) and g > 0:
                found = key
                break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < maxx and 0 <= ny < maxy):
                    continue
                # The goal cell may sit on the pad, whose centre the mask cleared
                # only in part. Step onto it anyway; the fine link checks the spur.
                if (nx, ny, layer) != (gx, gy, 0):
                    # Every fine cell along the step has to be clear, or the
                    # coarse path jumps a wall the fine router cannot cross.
                    blocked = False
                    for i in range(step + 1):
                        fx = x * step + step // 2 + (nx - x) * i
                        fy = y * step + step // 2 + (ny - y) * i
                        if not free(fx, fy, layer):
                            blocked = True
                            break
                    if blocked:
                        continue
                nk = (nx, ny, layer)
                ng = g + 1
                if nk in seen or ng >= best.get(nk, 1e18):
                    continue
                best[nk] = ng
                parent[nk] = key
                heapq.heappush(heap, (ng + abs(nx - gx) + abs(ny - gy), ng, nx, ny, layer))
            if allow_via and cfree(x, y, 1 - layer):
                px, py = (x * step + step // 2) * GRID, (y * step + step // 2) * GRID
                if self._via_ok(px, py, net):
                    nk = (x, y, 1 - layer)
                    ng = g + 3
                    if nk not in seen and ng < best.get(nk, 1e18):
                        best[nk] = ng
                        parent[nk] = key
                        heapq.heappush(heap, (ng + abs(x - gx) + abs(y - gy), ng, x, y, 1 - layer))
            if len(seen) > 60000:
                print(f"  coarse gave up ({len(seen)})")
                return None
        if found is None:
            print(f"  coarse exhausted {len(seen)}")
            return None
        coarse = self._reconstruct(parent, found)
        usable = [c for c in coarse if cfree(c[0], c[1], c[2])]
        if not usable:
            print("  coarse path has no clear cell")
            return None
        fine = [(x * step + step // 2, y * step + step // 2, layer) for x, y, layer in usable]
        def stitch(origins, chain, layer):
            origin_set = set(origins)
            target_set = set(chain)
            both = origin_set & target_set
            if both:
                hit = next(iter(both))
                return [(hit[0], hit[1], layer)]
            prev = {}
            dq = deque(origin_set)
            seen = set(origin_set)
            found = None
            while dq:
                x, y = dq.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in seen or not (0 <= nx < self.nx and 0 <= ny < self.ny):
                        continue
                    if not free(nx, ny, layer):
                        continue
                    seen.add((nx, ny))
                    prev[(nx, ny)] = (x, y)
                    if (nx, ny) in target_set:
                        found = (nx, ny)
                        dq.clear()
                        break
                    dq.append((nx, ny))
                if len(seen) > 40000:
                    break
            if found is None:
                return None
            path = [found]
            while path[-1] not in origin_set:
                path.append(prev[path[-1]])
            path.reverse()
            return [(x, y, layer) for x, y in path]

        chain0 = [(x, y) for x, y, layer in fine if layer == 0]
        head = stitch(starts, chain0, 0)
        tail = stitch(goals, chain0, 0)
        if not head or not tail:
            print("  coarse link failed")
            return None
        index = {(x, y): i for i, (x, y, _layer) in enumerate(fine)}
        hi = index[(head[-1][0], head[-1][1])]
        ti = index[(tail[-1][0], tail[-1][1])]
        mid = fine[hi:ti + 1] if hi <= ti else list(reversed(fine[ti:hi + 1]))
        return head + mid + list(reversed(tail))

    def _via_ok(self, x, y, net):
        if net in NO_VIA:
            return False
        if x < 1.2 or y < 1.2 or x > BOARD_W - 1.2 or y > BOARD_H - 1.2:
            return False
        for hx, hy, d in self.holes:
            need = 0.30 / 2 + 0.25 + d / 2
            if (x - hx) ** 2 + (y - hy) ** 2 < need ** 2:
                return False
        for vx, vy, onet in self.vias:
            if onet == net:
                continue
            if (x - vx) ** 2 + (y - vy) ** 2 < 0.90 ** 2:
                return False
        gx, gy = self.cell(x), self.cell(y)
        # The mask is the track centerline. A via is wider, so require the
        # neighbouring cells to be clear as well.
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                cx, cy = gx + dx, gy + dy
                if not (0 <= cx < self.nx and 0 <= cy < self.ny):
                    return False
                if self._mask_cache[0][cy * self.nx + cx] or self._mask_cache[1][cy * self.nx + cx]:
                    return False
        return True

    def _reconstruct(self, parent, key):
        path = [key]
        while key in parent:
            key = parent[key]
            path.append(key)
        path.reverse()
        return path

    def _commit(self, path, net, w):
        layer_id = {0: pcbnew.F_Cu, 1: pcbnew.B_Cu}
        run = [path[0]]
        for prev, cur in zip(path, path[1:]):
            if cur[2] != prev[2]:
                self._flush(run, net, w)
                vx, vy = cur[0] * GRID, cur[1] * GRID
                if not any(abs(px - vx) < 0.2 and abs(py - vy) < 0.2 and onet == net for px, py, onet in self.vias):
                    via = pcbnew.PCB_VIA(self.board)
                    via.SetPosition(pcbnew.VECTOR2I(mm(vx), mm(vy)))
                    via.SetWidth(mm(0.60))
                    via.SetDrill(mm(0.30))
                    via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    via.SetNet(self.board.FindNet(net))
                    via.SetIsFree(False)
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
        # merge colinear
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


def overlaps(x, y, forbidden):
    for x1, y1, x2, y2 in forbidden:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    return False


def pack(region, items, forbidden):
    """Place non-anchor parts on a grid, clear of anchor copper."""
    x0, y0, w, h = region
    spots = []
    y = y0
    while y < y0 + h - 1:
        x = x0
        while x < x0 + w - 1:
            if not overlaps(x, y, forbidden):
                spots.append((x, y))
            x += 4.6
        y += 3.8
    si = 0
    for ref, fp in items:
        if ref in ANCHORS:
            continue
        while si < len(spots):
            x, y = spots[si]
            si += 1
            fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            forbidden.append((x - 1.8, y - 1.4, x + 1.8, y + 1.4))
            break
        else:
            raise RuntimeError(f"no spot for {ref}")


def main():
    comps, nets = parse_netlist(OUT / "windlass.net")
    board = pcbnew.NewBoard(str(OUT / "windlass.kicad_pcb"))
    board.SetCopperLayerCount(4)
    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(CLR)
    ds.m_TrackMinWidth = mm(0.20)
    ds.m_ViasMinSize = mm(0.60)
    ds.m_ViasMinDrill = mm(0.30)
    ds.m_CopperEdgeClearance = mm(0.30)
    ds.m_HoleClearance = mm(0.25)
    ds.m_HoleToHoleMin = mm(0.25)
    ds.SetCopperLayerCount(4)

    # outline
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

    for ref, (x, y, rot) in ANCHORS.items():
        fp = footprints[ref]
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))

    pin_net = {}
    nets_of = {}
    for name, nodes in nets:
        for ref, pin in nodes:
            pin_net[(ref, pin)] = name
            nets_of.setdefault(ref, set()).add(name)

    def rect_of(fp, margin=0.4):
        bb = fp.GetBoundingBox(False, False)
        return (bb.GetLeft() / 1e6 - margin, bb.GetTop() / 1e6 - margin,
                bb.GetRight() / 1e6 + margin, bb.GetBottom() / 1e6 + margin)

    def overlaps_rect(a, b):
        return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]

    occupied = [rect_of(footprints[ref], 0.6) for ref in ANCHORS]
    for x, y in ((6, 6), (194, 6), (6, 154), (194, 154)):
        occupied.append((x - 4, y - 4, x + 4, y + 4))
    ux, uy, _rot = ANCHORS["U3"]
    u3_pads = [p for p in footprints["U3"].Pads() if p.GetNumber()]
    pad_ys = [p.GetPosition().y / 1e6 for p in u3_pads]
    pad_xs = [p.GetPosition().x / 1e6 for p in u3_pads]
    antenna = (ux - 18, 1.0, ux + 18, min(pad_ys) - 1.2)
    occupied.append(antenna)
    # The module courtyard graphic does not cover the pad field. Reserve it
    # explicitly so passives cannot land on the ESP32.
    occupied.append((min(pad_xs) - 2.5, min(pad_ys) - 2.5, max(pad_xs) + 2.5, max(pad_ys) + 3.0))

    def pads_on(ref, net):
        pts = []
        for p in footprints[ref].Pads():
            if pin_net.get((ref, p.GetNumber())) == net:
                pos = p.GetPosition()
                pts.append((pos.x / 1e6, pos.y / 1e6))
        return pts

    def fits(fp, x, y):
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        rect = rect_of(fp, 0.35)
        if rect[0] < 1.2 or rect[1] < 1.2 or rect[2] > BOARD_W - 1.2 or rect[3] > BOARD_H - 1.2:
            return None
        if any(overlaps_rect(rect, o) for o in occupied):
            return None
        return rect

    def pack_grid(fp, box, step):
        x0, y0, x1, y1 = box
        y = y0
        while y < y1:
            x = x0
            while x < x1:
                rect = fits(fp, x, y)
                if rect is not None:
                    return rect
                x += step
            y += step
        return None

    def seeds_for(ref, box):
        sig = [n for n in nets_of.get(ref, ()) if n not in ("GND", "+3V3")]
        pts = []
        for net in sig:
            for other in sorted(placed):
                if other == "U3" and REGION_OF.get(ref) is not ESP_BOX:
                    continue
                pts.extend(pads_on(other, net))
        if not pts and REGION_OF.get(ref) is ESP_BOX:
            pts = pads_on("U3", "+3V3") or pads_on("U3", "GND")
        x0, y0, x1, y1 = box
        inside = [p for p in pts if x0 - 8 <= p[0] <= x1 + 8 and y0 - 8 <= p[1] <= y1 + 8]
        return (inside or pts)[:6]

    def spiral(fp, box, seeds):
        x0, y0, x1, y1 = box
        if not seeds:
            seeds = [((x0 + x1) / 2, (y0 + y1) / 2)]
        for tx, ty in seeds:
            for radius in (3.6, 5.2, 7.2, 9.6, 13, 17, 23, 30):
                steps = max(8, int(radius * 1.3))
                for k in range(steps):
                    ang = 2 * math.pi * k / steps
                    x = tx + radius * math.cos(ang)
                    y = ty + radius * math.sin(ang)
                    if not (x0 <= x <= x1 and y0 <= y <= y1):
                        continue
                    rect = fits(fp, x, y)
                    if rect is not None:
                        return rect
        return None

    placed = set(ANCHORS)
    areas = []
    for ref in footprints:
        if ref in ANCHORS:
            continue
        bb = footprints[ref].GetBoundingBox(False, False)
        areas.append((-(bb.GetWidth() * bb.GetHeight()), ref))
    for _area, ref in sorted(areas):
        fp = footprints[ref]
        home = REGION_OF.get(ref, LOGIC_BOX)
        rect = spiral(fp, home, seeds_for(ref, home))
        if rect is None:
            rect = pack_grid(fp, home, 2.0)
        if rect is None and home is not LOGIC_BOX:
            rect = spiral(fp, LOGIC_BOX, seeds_for(ref, LOGIC_BOX)) or pack_grid(fp, LOGIC_BOX, 2.2)
            if rect is not None:
                print(f"  {ref} overflowed into logic")
        if rect is None:
            rect = pack_grid(fp, FALLBACK_BOX, 2.4)
            if rect is not None:
                print(f"  {ref} overflowed into fallback")
        if rect is None:
            raise RuntimeError(f"no place for {ref}")
        occupied.append(rect)
        placed.add(ref)

    pads_by_net = {name: [] for name, _ in nets}
    pad_lookup = {}
    for ref, fp in footprints.items():
        board.Add(fp)
        for pad in fp.Pads():
            pad_lookup.setdefault((ref, pad.GetNumber()), []).append(pad)
    for name, nodes in nets:
        for ref, pin in nodes:
            for pad in pad_lookup.get((ref, pin), []):
                pad.SetNet(net_by_name[name])
                pads_by_net[name].append(pad)

    # mounting holes, not in the schematic
    for i, (x, y) in enumerate(((6, 6), (194, 6), (6, 154), (194, 154)), start=1):
        fp = pcbnew.FootprintLoad(str(FP / "MountingHole.pretty"), "MountingHole_3.2mm_M3")
        fp.SetReference(f"H{i}")
        fp.SetValue("M3")
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        board.Add(fp)

    # slots between isolator pin rows. Coordinates are footprint-local, rotation 0.
    slots = []
    def slot_for(ref, x1, y1, x2, y2):
        if ref not in footprints:
            return
        pos = footprints[ref].GetPosition()
        ox, oy = pos.x / 1e6, pos.y / 1e6
        slots.append((ox + x1, oy + y1, ox + x2, oy + y2))

    slot_for("U5", -0.7, -2.6, 0.7, 2.6)       # between SOIC-8 rows
    slot_for("U10", -1.0, -5.2, 1.0, 5.2)      # between SOIC-16W rows
    slot_for("U6", -0.8, -1.6, 0.8, 1.6)       # TLP291
    slot_for("U7", -0.8, -1.6, 0.8, 1.6)
    slot_for("U4", 5.2, -2.2, 7.4, 2.2)        # between MEJ2 primary and secondary
    slot_for("U9", 5.2, -2.2, 7.4, 2.2)
    for x1, y1, x2, y2 in slots:
        add_line(board, x1, y1, x2, y1)
        add_line(board, x2, y1, x2, y2)
        add_line(board, x2, y2, x1, y2)
        add_line(board, x1, y2, x1, y1)

    # antenna keepout, local to U3: the module graphic extends well above the pads.
    # antenna was reserved during placement, from the module origin to just above its pads.

    def make_keepout(rect, name):
        x1, y1, x2, y2 = rect
        k = pcbnew.ZONE(board)
        k.SetIsRuleArea(True)
        lset = pcbnew.LSET()
        lset.AddLayer(pcbnew.In1_Cu)
        lset.AddLayer(pcbnew.In2_Cu)
        k.SetLayerSet(lset)
        k.SetDoNotAllowZoneFills(True)
        k.SetDoNotAllowVias(True)
        k.SetDoNotAllowTracks(True)
        k.SetDoNotAllowPads(False)
        ol = k.Outline()
        ol.NewOutline()
        for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            ol.Append(mm(x), mm(y))
        board.Add(k)
        return (x1, y1, x2, y2)

    def cluster_boxes(names, margin, join=14.0):
        rects = []
        for name in names:
            for p in pads_by_net.get(name, []):
                bb = p.GetBoundingBox()
                rects.append((bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6))
        used = [False] * len(rects)
        boxes = []
        for i, seed in enumerate(rects):
            if used[i]:
                continue
            used[i] = True
            group = [seed]
            grew = True
            while grew:
                grew = False
                for j, other in enumerate(rects):
                    if used[j]:
                        continue
                    ocx, ocy = (other[0] + other[2]) / 2, (other[1] + other[3]) / 2
                    if any(abs(ocx - (g[0] + g[2]) / 2) < join and abs(ocy - (g[1] + g[3]) / 2) < join for g in group):
                        used[j] = True
                        group.append(other)
                        grew = True
            xs = [v for g in group for v in (g[0], g[2])]
            ys = [v for g in group for v in (g[1], g[3])]
            boxes.append((min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin))
        return boxes

    keepouts = []
    groups = {
        "reed": ["REED_RET", "REED_3V3", "REED_ISO", "REED_SIG", "LOFRANS_NODE", "DRY_A"],
        "up": ["UP_RET", "UP_FIELD", "UP_LED_A"],
        "dn": ["DN_RET", "DN_FIELD", "DN_LED_A"],
        "can": ["GND_CAN", "ISO_5V", "CAN_H", "CAN_L", "NMEA_SHIELD"],
        "contacts": ["UP_COM", "UP_NO", "DN_COM", "DN_NO"],
    }
    for gname, nlist in groups.items():
        for box in cluster_boxes(nlist, PLANE_MARGIN):
            keepouts.append(make_keepout(box, gname))
            print(f"keepout {gname}: {tuple(round(v, 1) for v in box)}")

    # antenna keepout on every copper layer, including tracks
    ak = pcbnew.ZONE(board)
    ak.SetIsRuleArea(True)
    ak.SetLayerSet(pcbnew.LSET.AllCuMask())
    ak.SetDoNotAllowZoneFills(True)
    ak.SetDoNotAllowVias(True)
    ak.SetDoNotAllowTracks(True)
    ak.SetDoNotAllowPads(False)
    ol = ak.Outline()
    ol.NewOutline()
    x1, y1, x2, y2 = antenna
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        ol.Append(mm(x), mm(y))
    board.Add(ak)
    print(f"antenna keepout {tuple(round(v,1) for v in antenna)}")

    pos_lines = []
    for ref, fp in sorted(footprints.items()):
        p = fp.GetPosition()
        pos_lines.append(f"{ref:12} {p.x/1e6:7.2f} {p.y/1e6:7.2f}")
    (OUT / "placement.txt").write_text("\n".join(pos_lines), encoding="utf-8")
    if os.environ.get("SKIP_ROUTE"):
        board.Save(str(OUT / "windlass.kicad_pcb"))
        print("placement only")
        return
    router = Router(board, pads_by_net)
    router.walls = list(slots)
    router.walls.append(antenna)
    # route barrier nets first so later nets keep the gap
    # Short nets first, so a later long run cannot pave over the only exit
    # from a fine-pitch pad. Isolated nets still go before logic nets.
    def span_of(n):
        pads = pads_by_net[n]
        xs = [p.GetPosition().x for p in pads]
        ys = [p.GetPosition().y for p in pads]
        return (max(xs) - min(xs)) + (max(ys) - min(ys))

    # Long isolated nets claim their corridor first. Logic nets are via-fanned
    # to the back layer before they are routed, so a track on the top cannot
    # close the only exit from a fine-pitch pad.
    barrier_order = sorted((n for n in pads_by_net if n in BARRIER), key=lambda n: (-span_of(n), n))
    early_logic = {"USB_DP_C", "USB_DN_C", "USB_VBUS", "USB_DP", "USB_DN", "IO0_NET", "TXD_NODE", "UP_REQ"}
    logic_order = sorted(
        (n for n in pads_by_net if n not in BARRIER),
        key=lambda n: (n not in early_logic, span_of(n), n),
    )
    failed = []
    only = {n for n in os.environ.get("ROUTE_ONLY", "").split(",") if n}

    def route_one(name):
        if only and name not in only:
            return
        if name in ("GND", "+3V3"):
            return
        pads = pads_by_net[name]
        if len(pads) < 2:
            return
        print(f"route {name} ({len(pads)})", flush=True)
        if not router.route(name, pads):
            failed.append(name)
            print(f"  FAILED {name}")

    for name in barrier_order:
        if not only or name in only:
            router.fanout(name, pads_by_net[name])
    for name in barrier_order:
        route_one(name)
    if not only:
        for name in logic_order:
            if name.startswith("USB_"):
                router.fanout(name, pads_by_net[name])
        for name in logic_order:
            if name in ("GND", "+3V3"):
                continue
            router.via_fanout(name, pads_by_net[name])
    for name in logic_order:
        route_one(name)

    # GND fanout vias for SMD pads, outside keepouts and the antenna
    def inside(rect, x, y, pad=0):
        x1, y1, x2, y2 = rect
        return x1 - pad <= x <= x2 + pad and y1 - pad <= y <= y2 + pad

    router._mask_cache = router._mask("GND", 0.15)
    gnd = net_by_name["GND"]
    for p in pads_by_net.get("GND", []):
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            continue
        pos = p.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6
        if any(inside(r, px, py) for r in keepouts) or inside(antenna, px, py):
            continue
        # through-hole already hits In1
        if p.GetDrillSize().x > 0:
            continue
        # search a via site just outside the pad
        placed = False
        for dist in (1.1, 1.6, 2.2):
            for dx, dy in ((dist, 0), (-dist, 0), (0, dist), (0, -dist), (dist, dist), (-dist, dist)):
                x, y = px + dx, py + dy
                if any(inside(r, x, y) for r in keepouts) or inside(antenna, x, y, 0.5):
                    continue
                if router._via_ok(x, y, "GND"):
                    via = pcbnew.PCB_VIA(board)
                    via.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                    via.SetWidth(mm(0.60))
                    via.SetDrill(mm(0.30))
                    via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    via.SetNet(gnd)
                    board.Add(via)
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(pcbnew.VECTOR2I(mm(px), mm(py)))
                    t.SetEnd(pcbnew.VECTOR2I(mm(x), mm(y)))
                    t.SetWidth(mm(0.30))
                    t.SetLayer(pcbnew.F_Cu)
                    t.SetNet(gnd)
                    board.Add(t)
                    router.vias.append((x, y, "GND"))
                    router.holes.append((x, y, 0.30))
                    placed = True
                    break
            if placed:
                break

    # planes
    def add_zone(net_name, layer, rect):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(net_by_name[net_name])
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetLocalClearance(mm(CLR))
        ol = z.Outline()
        ol.NewOutline()
        x1, y1, x2, y2 = rect
        for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            ol.Append(mm(x), mm(y))
        board.Add(z)

    full = (0.4, 0.4, BOARD_W - 0.4, BOARD_H - 0.4)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In1_Cu):
        add_zone("GND", layer, full)
    # 3V3 plane only over the logic area, inner layer, keepouts still apply
    add_zone("+3V3", pcbnew.In2_Cu, full)
    # Fan the 3V3 pads out the same way as GND, onto the inner plane.
    p3 = net_by_name["+3V3"]
    router._mask_cache = router._mask("+3V3", 0.15)
    for p in pads_by_net.get("+3V3", []):
        if p.GetDrillSize().x > 0:
            continue
        pos = p.GetPosition()
        px, py = pos.x / 1e6, pos.y / 1e6
        if any(inside(r, px, py) for r in keepouts) or inside(antenna, px, py):
            continue
        for dist in (1.1, 1.6, 2.2):
            done = False
            for dx, dy in ((dist, 0), (-dist, 0), (0, dist), (0, -dist)):
                x, y = px + dx, py + dy
                if any(inside(r, x, y) for r in keepouts) or inside(antenna, x, y, 0.5):
                    continue
                if router._via_ok(x, y, "+3V3"):
                    via = pcbnew.PCB_VIA(board)
                    via.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                    via.SetWidth(mm(0.60))
                    via.SetDrill(mm(0.30))
                    via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    via.SetNet(p3)
                    board.Add(via)
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(pcbnew.VECTOR2I(mm(px), mm(py)))
                    t.SetEnd(pcbnew.VECTOR2I(mm(x), mm(y)))
                    t.SetWidth(mm(0.30))
                    t.SetLayer(pcbnew.F_Cu)
                    t.SetNet(p3)
                    board.Add(t)
                    router.vias.append((x, y, "+3V3"))
                    router.holes.append((x, y, 0.30))
                    done = True
                    break
            if done:
                break

    # connector labels
    labels = [
        (12, 140, "+12V  GND"),
        (42, 140, "SW  SW  IGN  IGN"),
        (28, 122, "UP COM  UP NO  DN COM  DN NO"),
        (100, 140, "REED SIG  RET  DRY  RET"),
        (145, 140, "UP  UPRET  -  DN  DNRET"),
        (178, 140, "C  L  SHD  H  S-open"),
        (112, 6, "USB"),
        (150, 8, "ANTENNA KEEPOUT"),
        (18, 56, "UP RELAY"),
        (18, 78, "DN RELAY"),
    ]
    for x, y, text in labels:
        add_text(board, x, y, text)

    board.GetTitleBlock().SetTitle("Windlass integrated controller")
    board.GetTitleBlock().SetDate("2026-11-22")
    board.GetTitleBlock().SetRevision("1.0-not-for-fabrication")
    board.GetTitleBlock().SetComment(0, "NOT FOR FABRICATION. No Gerbers.")

    pcbnew.SaveBoard(str(OUT / "windlass.kicad_pcb"), board)
    print("failed", failed)
    print("wrote", OUT / "windlass.kicad_pcb")


if __name__ == "__main__":
    main()
