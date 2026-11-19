"""Copper for the 80 x 69 mm board. Not a fabrication route.

The four relay-contact nets are drawn first, at 0.80 mm, on B.Cu in the gap
between the Finder pin rows. Other nets then follow on F.Cu and B.Cu.
Nothing is drawn on In1.Cu or In2.Cu. Tracks stop at the antenna keep-out,
the two isolation barriers, and the antenna notch. GND is left for the L2 plane.
"""

import math
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "kicad" / "placement_finder.kicad_pcb"
REPORT = ROOT / "docs" / "route_initial.txt"

CLEARANCE = 0.2
EDGE = 0.3
VIA_SIZE = 0.45
VIA_DRILL = 0.2
BOARD_W, BOARD_H = 80.0, 69.0

# Copper keep-outs. Footprints may sit in the antenna zone; tracks may not.
BLOCKED = [
    (18.0, 51.0, 62.0, 68.5),
    (16.2, 33.2, 21.2, 40.8),
    (57.0, 38.8, 62.2, 46.6),
    (28.0, 55.0, 52.0, 69.0),
]
WIDE = {"UP_COM": 0.80, "UP_NO": 0.80, "DN_COM": 0.80, "DN_NO": 0.80}
POWER = {"+5V", "+3V3", "+12V", "VIN_12", "+12V_MCU", "+12V_COIL", "COIL_12", "V5_RAW", "GND"}


def rot_point(x, y, deg):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (x * c + y * s, -x * s + y * c)


def blocks(text, keyword):
    token = f"({keyword}"
    i = 0
    found = []
    while True:
        start = text.find(token, i)
        if start < 0:
            break
        depth = 0
        for j in range(start, len(text)):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    found.append(text[start : j + 1])
                    i = j + 1
                    break
        else:
            break
    return found


def collect(text):
    """Return {net: [center, ...]} and obstacle rects (box, net)."""
    nets = {}
    obstacles = []
    tht = []
    for fp in blocks(text, "footprint"):
        at = re.search(r"\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?\)", fp)
        if not at:
            continue
        fx, fy = float(at.group(1)), float(at.group(2))
        frot = float(at.group(3) or 0)
        for pad in blocks(fp, "pad"):
            net = re.search(r'\(net "([^"]+)"\)', pad)
            loc = re.search(r"\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?\)", pad)
            size = re.search(r"\(size ([-0-9.]+) ([-0-9.]+)\)", pad)
            if not loc or not size:
                continue
            px, py = float(loc.group(1)), float(loc.group(2))
            prot = float(loc.group(3) or 0)
            sx, sy = float(size.group(1)), float(size.group(2))
            cx, cy = rot_point(px, py, frot)
            cx += fx
            cy += fy
            ang = frot + prot
            corners = []
            for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)):
                rx, ry = rot_point(dx, dy, ang)
                corners.append((cx + rx, cy + ry))
            xs = [p[0] for p in corners]
            ys = [p[1] for p in corners]
            name = net.group(1) if net else ""
            kind = re.match(r'\(pad "[^"]*" (\w+)', pad)
            # A through-hole pad is copper on every layer. An SMD pad is top only.
            layer = "*" if kind and kind.group(1) != "smd" else "F.Cu"
            obstacles.append(((min(xs), min(ys), max(xs), max(ys)), name, layer))
            if name:
                point = (round(cx, 3), round(cy, 3))
                nets.setdefault(name, []).append(point)
                if layer == "*":
                    tht.append(point)
    return nets, obstacles, tht


def unique(points):
    seen = []
    for p in points:
        if all(abs(p[0] - q[0]) > 0.05 or abs(p[1] - q[1]) > 0.05 for q in seen):
            seen.append(p)
    return seen


def hits(x1, y1, x2, y2, rect, margin):
    a, b, c, d = rect
    a -= margin
    b -= margin
    c += margin
    d += margin
    if abs(y1 - y2) <= 1e-6:
        y = y1
        xa, xb = (x1, x2) if x1 <= x2 else (x2, x1)
        return not (xb < a or xa > c or y < b or y > d)
    x = x1
    ya, yb = (y1, y2) if y1 <= y2 else (y2, y1)
    return not (yb < b or ya > d or x < a or x > c)


def inside(x, y, width):
    inset = EDGE + width / 2
    if x < inset or y < inset or x > BOARD_W - inset or y > BOARD_H - inset:
        return False
    nx0, ny0, nx1, ny1 = BLOCKED[-1]
    return not (nx0 < x < nx1 and ny0 < y < ny1)


def blocks_layer(obstacle_layer, layer):
    return obstacle_layer == "*" or obstacle_layer == layer


def segment_ok(x1, y1, x2, y2, width, net, obstacles, tracks, layer="F.Cu", extra=0.0):
    if abs(x1 - x2) < 1e-6 and abs(y1 - y2) < 1e-6:
        return True
    if abs(x1 - x2) > 1e-6 and abs(y1 - y2) > 1e-6:
        return False
    margin = CLEARANCE + width / 2 + extra
    if not inside(x1, y1, width) or not inside(x2, y2, width):
        return False
    for box in BLOCKED:
        if hits(x1, y1, x2, y2, box, width / 2):
            return False
    for box, other, olayer in obstacles:
        if other == net or not blocks_layer(olayer, layer):
            continue
        if hits(x1, y1, x2, y2, box, margin):
            return False
    for (tx1, ty1, tx2, ty2, tw, tnet, tlayer) in tracks:
        if tnet == net or tlayer != layer:
            continue
        if hits(x1, y1, x2, y2, (min(tx1, tx2), min(ty1, ty2), max(tx1, tx2), max(ty1, ty2)), margin + tw / 2):
            return False
    return True


def via_ok(x, y, net, obstacles, tracks, extra=0.0, vias=()):
    # The extra margin covers the 0.25 mm hole-to-copper rule and the solder-mask
    # opening, which the plain 0.20 mm track clearance does not.
    r = VIA_SIZE / 2 + extra
    if not inside(x, y, VIA_SIZE):
        return False
    box = (x - r, y - r, x + r, y + r)
    for blocked in BLOCKED:
        if hits(x, y, x, y, blocked, r):
            return False
    for vx, vy in vias:
        if abs(vx - x) < 0.6 and abs(vy - y) < 0.6:
            return False
    for ob, other, _olayer in obstacles:
        if other == net:
            continue
        if hits(x, y, x, y, ob, r + CLEARANCE):
            return False
    for tx1, ty1, tx2, ty2, tw, tnet, _tlayer in tracks:
        if tnet == net:
            continue
        if hits(tx1, ty1, tx2, ty2, box, CLEARANCE + tw / 2):
            return False
    return True


def path_ok(path, width, net, obstacles, tracks, extra=0.0, vias=()):
    for item in path:
        kind = item[0]
        if kind == "via":
            if not via_ok(item[1], item[2], net, obstacles, tracks, extra, vias):
                return False
        elif not segment_ok(item[1][0], item[1][1], item[2][0], item[2][1], width, net, obstacles, tracks, item[3], extra):
            return False
    return True


def step(a, b, dist):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    if n <= dist + 0.4:
        return None
    return (a[0] + dx / n * dist, a[1] + dy / n * dist)


def on_tht(point, tht):
    return any(abs(point[0] - q[0]) < 0.05 and abs(point[1] - q[1]) < 0.05 for q in tht)


def candidates(a, b, tht):
    ax, ay = a
    bx, by = b
    elbows = [(bx, ay), (ax, by)]
    both = on_tht(a, tht) and on_tht(b, tht)
    out = []
    if abs(ax - bx) < 0.05 or abs(ay - by) < 0.05:
        out.append([("seg", a, b, "F.Cu")])
        if both:
            out.append([("seg", a, b, "B.Cu")])
    for elbow in elbows:
        out.append([("seg", a, elbow, "F.Cu"), ("seg", elbow, b, "F.Cu")])
        if both:
            out.append([("seg", a, elbow, "B.Cu"), ("seg", elbow, b, "B.Cu")])
    # Drop the middle onto B.Cu. The vias sit 1 mm off each pad, not on the pad.
    for elbow in elbows:
        p = step(a, elbow, 1.0)
        q = step(b, elbow, 1.0)
        if p is None or q is None:
            continue
        out.append(
            [
                ("seg", a, p, "F.Cu"),
                ("via", p[0], p[1]),
                ("seg", p, elbow, "B.Cu"),
                ("seg", elbow, q, "B.Cu"),
                ("via", q[0], q[1]),
                ("seg", q, b, "F.Cu"),
            ]
        )
    return out


def termini(point, net, width, obstacles, tracks, tht, extra, vias):
    """Where a track may change to the bottom layer.

    A through-hole pad is already on B.Cu. An SMD pad needs a short top stub
    and a via, leaving the pad across its short side rather than along the row.
    """
    if on_tht(point, tht):
        return [point]
    px, py = point
    found = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for dist in (1.0, 1.6, 2.4):
            q = (px + dx * dist, py + dy * dist)
            if not segment_ok(px, py, q[0], q[1], width, net, obstacles, tracks, "F.Cu", extra):
                continue
            if not via_ok(q[0], q[1], net, obstacles, tracks, extra, vias):
                continue
            found.append(q)
            break
    return found


def bottom_paths(p, q):
    px, py = p
    qx, qy = q
    paths = []
    if abs(px - qx) < 0.05 or abs(py - qy) < 0.05:
        paths.append([("seg", p, q, "B.Cu")])
    paths.append([("seg", p, (qx, py), "B.Cu"), ("seg", (qx, py), q, "B.Cu")])
    paths.append([("seg", p, (px, qy), "B.Cu"), ("seg", (px, qy), q, "B.Cu")])
    for delta in (2.2, -2.2, 4.4, -4.4):
        paths.append(
            [
                ("seg", p, (px, py + delta), "B.Cu"),
                ("seg", (px, py + delta), (qx, py + delta), "B.Cu"),
                ("seg", (qx, py + delta), q, "B.Cu"),
            ]
        )
        paths.append(
            [
                ("seg", p, (px + delta, py), "B.Cu"),
                ("seg", (px + delta, py), (px + delta, qy), "B.Cu"),
                ("seg", (px + delta, qy), q, "B.Cu"),
            ]
        )
    return paths


def with_stubs(a, p, b, q, middle):
    path = []
    if abs(p[0] - a[0]) > 0.05 or abs(p[1] - a[1]) > 0.05:
        path.extend([("seg", a, p, "F.Cu"), ("via", p[0], p[1])])
    path.extend(middle)
    if abs(q[0] - b[0]) > 0.05 or abs(q[1] - b[1]) > 0.05:
        path.extend([("via", q[0], q[1]), ("seg", q, b, "F.Cu")])
    return path


def route_pair(a, b, net, width, obstacles, tracks, tht, vias):
    extra = 0.12
    for path in candidates(a, b, tht):
        if path_ok(path, width, net, obstacles, tracks, extra, vias):
            return path
    ends_a = termini(a, net, width, obstacles, tracks, tht, extra, vias)
    ends_b = termini(b, net, width, obstacles, tracks, tht, extra, vias)
    for p in ends_a:
        for q in ends_b:
            for middle in bottom_paths(p, q):
                path = with_stubs(a, p, b, q, middle)
                if path_ok(path, width, net, obstacles, tracks, extra, vias):
                    return path
    return None


def emit(path, width, net):
    lines = []
    for item in path:
        if item[0] == "via":
            lines.append(
                f'\t(via (at {item[1]:.3f} {item[2]:.3f}) (size {VIA_SIZE}) (drill {VIA_DRILL}) '
                f'(layers "F.Cu" "B.Cu") (net "{net}") (uuid "{uuid.uuid4()}"))'
            )
        else:
            x1, y1 = item[1]
            x2, y2 = item[2]
            if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
                continue
            lines.append(
                f'\t(segment (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) '
                f'(width {width:.3f}) (layer "{item[3]}") (net "{net}") (uuid "{uuid.uuid4()}"))'
            )
    return lines


def route_contacts(obstacles, tracks, vias):
    """0.80 mm contact tracks on the bottom, in the gap between the Finder pin rows.

    The connector is on the left edge and the contact pins face the other way.
    Moving the connector into the reed supply, or turning the relays around into
    the connector courtyard, was checked and does not open a wider channel.
    The pin-row gap is clear of through-hole copper, so the four tracks use B.Cu.
    A top-side stub leaves each lower connector pin, because a bottom stub would
    cross the vertical track of the pin above it. Vias are 0.45 mm with a 0.20 mm drill.
    """
    width = 0.80
    # (net, exit layer, lane x, lane y, connector, relay pin)
    # Leftmost lane is the lowest, so a drop into a common pin does not cross the
    # track above it. DN_NO's via stays left of R94 (ISO_5V) at x 9.12.
    # Centres are more than 1.0 mm apart: 0.40 + 0.20 + 0.40. The top lane stays
    # below the lower Finder row and DN_NO's via stays left of R94.
    jobs = [
        ("UP_COM", "B.Cu", 6.25, 18.15, (4.30, 39.20), (32.25, 16.10)),
        ("DN_COM", "F.Cu", 7.40, 19.20, (4.30, 32.20), (63.75, 16.10)),
        ("DN_NO", "F.Cu", 8.50, 20.25, (4.30, 28.70), (67.25, 23.60)),
        ("UP_NO", "F.Cu", 9.70, 21.45, (4.30, 35.70), (35.75, 23.60)),
    ]
    graphics = []
    failed = []
    for name, exit_layer, lane_x, lane_y, src, dst in jobs:
        path = [("seg", src, (lane_x, src[1]), exit_layer)]
        if exit_layer == "F.Cu":
            path.append(("via", lane_x, src[1]))
        path.append(("seg", (lane_x, src[1]), (lane_x, lane_y), "B.Cu"))
        path.append(("seg", (lane_x, lane_y), (dst[0], lane_y), "B.Cu"))
        path.append(("seg", (dst[0], lane_y), dst, "B.Cu"))
        if not path_ok(path, width, name, obstacles, tracks):
            failed.append(name)
            continue
        for item in path:
            if item[0] == "seg":
                tracks.append((item[1][0], item[1][1], item[2][0], item[2][1], width, name, item[3]))
            elif item[0] == "via":
                vias.append((item[1], item[2]))
        graphics.extend(emit(path, width, name))
    return graphics, failed


def stage_of(name):
    if name in WIDE:
        return "contacts"
    if name in {"REED_RET", "REED_3V3", "UP_RET", "DN_RET", "GND_CAN", "ISO_5V", "NMEA_SHIELD"}:
        return "isolation"
    if name in POWER or name.startswith("+12V") or name.startswith("VIN"):
        return "power"
    if name.startswith(("UP_GATE", "DN_GATE", "UP_LOW", "DN_LOW", "UP_REQ", "DN_REQ", "QCOIL", "QMCU", "QSERIES", "COIL", "IGN_", "AND_", "PUB")):
        return "coils"
    if name.startswith(("REED", "LOFRANS", "DRY", "UP_SENSE", "DN_SENSE", "UP_FIELD", "DN_FIELD", "UP_LED", "DN_LED")):
        return "reed"
    if name.startswith(("CAN", "TWAI", "TXD", "SERIES", "UART")):
        return "can"
    if name.startswith(("USB", "CC1", "CC2")):
        return "usb"
    return "gpio"


ORDER = ["contacts", "isolation", "power", "coils", "reed", "can", "usb", "gpio"]


def main():
    requested = sys.argv[1] if len(sys.argv) > 1 else "all"
    if requested != "all" and requested not in ORDER:
        raise SystemExit("stage must be one of: " + ", ".join(ORDER) + ", all")
    keep = set(ORDER) if requested == "all" else set(ORDER[: ORDER.index(requested) + 1])
    text = BOARD.read_text(encoding="utf-8")
    text = re.sub(r"\n\t\(segment \(start .*?\)\)", "", text)
    text = re.sub(r"\n\t\(via \(at .*?\)\)", "", text)
    nets, obstacles, tht = collect(text)
    tracks = []
    vias = []
    routed = []
    partial = []
    skipped = []
    graphics = []
    contact_graphics, contact_failed = route_contacts(obstacles, tracks, vias)
    graphics.extend(contact_graphics)
    if contact_failed:
        partial.append("CONTACT FAILED " + ", ".join(contact_failed))
    else:
        routed.append("UP_COM, UP_NO, DN_COM, DN_NO (2 pads each at 0.80 mm, B.Cu)")
    done = set(WIDE)
    for name in sorted(nets, key=lambda n: (ORDER.index(stage_of(n)), n)):
        if name in done:
            continue
        stage = stage_of(name)
        if stage not in keep:
            continue
        points = unique(nets[name])
        if len(points) < 2:
            continue
        # GND is the L2 plane and is not drawn as tracks. A net with many pads
        # is only given its short links; the rest stays for a pour.
        if name == "GND" or name.startswith("unconnected"):
            skipped.append(f"{name} ({len(points)} pads, plane or no-connect)")
            continue
        width = 0.40 if stage == "power" else WIDE.get(name, 0.20)
        cap = 22.0 if stage == "power" else 45.0
        parent = list(range(len(points)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        pairs = sorted(
            ((abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1]), i, j)
             for i in range(len(points)) for j in range(i + 1, len(points))),
        )
        linked = 0
        for dist, i, j in pairs:
            if dist > cap or find(i) == find(j):
                continue
            path = route_pair(points[i], points[j], name, width, obstacles, tracks, tht, vias)
            if path is None:
                continue
            parent[find(i)] = find(j)
            linked += 1
            for item in path:
                if item[0] == "seg":
                    tracks.append((item[1][0], item[1][1], item[2][0], item[2][1], width, name, item[3]))
                elif item[0] == "via":
                    vias.append((item[1], item[2]))
            graphics.extend(emit(path, width, name))
        groups = len({find(i) for i in range(len(points))})
        if groups == 1:
            routed.append(f"{name} ({len(points)} at {width:.2f} mm)")
        elif linked:
            partial.append(f"{name} ({linked} links, {groups} groups left, {width:.2f} mm)")
        else:
            partial.append(f"{name} (no clear link, {width:.2f} mm)")
    if not text.rstrip().endswith(")"):
        raise SystemExit("board file does not end with a closing parenthesis")
    body = text.rstrip()[:-1]
    BOARD.write_text(body + "\n" + "\n".join(graphics) + "\n)\n", encoding="utf-8")
    lines = [
        f"Route through stage {requested}. Not for fabrication.",
        f"segments and vias written: {len(graphics)}",
        f"nets fully linked: {len(routed)}",
        f"nets partly linked: {len(partial)}",
        f"nets left for a pour or a later pass: {len(skipped)}",
        "",
        "Fully linked:",
        *routed,
        "",
        "Partly linked:",
        *partial,
        "",
        "Not attempted:",
        *skipped,
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:8]))


if __name__ == "__main__":
    main()
