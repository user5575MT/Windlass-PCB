"""Historical builder for the pre-buffer checkpoint.

Do not run this against the current design. It overwrites
kicad11/windlass_install.kicad_pcb from the bench board and sets R60 and
R70 back to 1k. The schematic now matches kicad11/windlass_install_v2.kicad_pcb.

Build kicad11/windlass_install.kicad_pcb from the bench board.

ZXMS6004FF is pin 1 drain, pin 2 IN, pin 3 source. The NX6008 land was
pin 1 gate, pin 2 source, pin 3 drain. Straight endpoint moves cross the
neighbouring pad, so each front-copper connection is replaced with a
clearance-checked polyline. Inner copper is left where it is. The two
contact clamps and the spurs that existed only to reach them are removed.
"""
import math
import shutil

import pcbnew

ROOT = "/agent/repos/Windlass-PCB/kicad11"
SRC_BOARD = ROOT + "/windlass_bench.kicad_pcb"
BOARD = ROOT + "/windlass_install.kicad_pcb"

# This pad receives the net that currently sits on the named pad.
SRC = {"1": "3", "2": "1", "3": "2"}
CONTACT = ("UP_COM", "UP_NO", "DN_COM", "DN_NO")
TOL = 10000  # nm

# Intermediate points, millimetres. The surviving far end and the new pad
# centre are added at the ends.
ROUTES = {
    ("Q_UP", "UP_GATE"): [(8.4, 101.3326), (8.4, 105.0285)],
    ("Q_UP", "UP_LOW"): [(14.3667, 103.1285)],
    ("Q_UP", "SERIES_NODE"): [(7.3703, 106.9), (14.0, 106.9), (14.0, 104.0785)],
    ("Q_DN", "DN_LOW"): [(18.6625, 90.5646)],
    ("Q_DN", "SERIES_NODE"): [(22.0, 93.259), (22.0, 90.5646)],
    ("Q_SERIES", "QSERIES_G"): [(24.9, 92.6071), (24.9, 97.2), (18.2, 97.2), (18.2, 96.1416)],
    ("Q_SERIES", "SERIES_NODE"): [(20.7855, 94.2416)],
}


def mm(value):
    return value / 1e6


def nm(value):
    return int(round(value * 1e6))


def near(a, b, tol=TOL):
    return abs(a.x - b.x) <= tol and abs(a.y - b.y) <= tol


def touches(pad, pt):
    if pad.HitTest(pt):
        return True
    centre = pad.GetPosition()
    return abs(centre.x - pt.x) <= 20000 and abs(centre.y - pt.y) <= 20000


def on_segment(pt, a, b, tol=TOL):
    dx = b.x - a.x
    dy = b.y - a.y
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return near(pt, a, tol)
    scale = ((pt.x - a.x) * dx + (pt.y - a.y) * dy) / length_sq
    if scale < 0 or scale > 1:
        return False
    return abs(a.x + scale * dx - pt.x) <= tol and abs(a.y + scale * dy - pt.y) <= tol


def point(x, y):
    return pcbnew.VECTOR2I(nm(x), nm(y))


def add_track(board, start, end, width, net):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(width)
    track.SetLayer(pcbnew.F_Cu)
    track.SetNet(net)
    board.Add(track)
    return track


def segments_of(points):
    pairs = []
    for start, end in zip(points, points[1:]):
        if start.x == end.x and start.y == end.y:
            continue
        pairs.append((start, end))
    return pairs


def dist_point_seg(px, py, ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    scale = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(px - (ax + scale * dx), py - (ay + scale * dy))


def dist_seg_seg(a, b, c, d):
    # Sample the shorter check at 0.02 mm. These runs are a few millimetres.
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    steps = max(1, int(length / 0.02))
    best = None
    for step in range(steps + 1):
        scale = step / steps
        px = a[0] + (b[0] - a[0]) * scale
        py = a[1] + (b[1] - a[1]) * scale
        got = dist_point_seg(px, py, c[0], c[1], d[0], d[1])
        best = got if best is None else min(best, got)
    return best


def pad_box(pad):
    box = pad.GetBoundingBox()
    return (mm(box.GetLeft()), mm(box.GetTop()), mm(box.GetRight()), mm(box.GetBottom()))


def dist_seg_box(a, b, box):
    x0, y0, x1, y1 = box
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    steps = max(1, int(length / 0.02))
    best = None
    for step in range(steps + 1):
        scale = step / steps
        px = a[0] + (b[0] - a[0]) * scale
        py = a[1] + (b[1] - a[1]) * scale
        cx = min(max(px, x0), x1)
        cy = min(max(py, y0), y1)
        got = math.hypot(px - cx, py - cy)
        best = got if best is None else min(best, got)
    return best


def same_net_items(board, netname):
    tracks = []
    vias = []
    for item in board.GetTracks():
        if item.GetNetname() != netname:
            continue
        if item.GetClass() == "PCB_VIA":
            vias.append(item)
        else:
            tracks.append(item)
    pads = []
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetNetname() == netname:
                pads.append(pad)
    return tracks, vias, pads


def via_changes_layer(via, tracks):
    layers = set()
    for track in tracks:
        if near(via.GetPosition(), track.GetStart()) or near(via.GetPosition(), track.GetEnd()):
            layers.add(track.GetLayer())
    return len(layers) >= 2


def end_anchored(pt, track, tracks, vias, pads):
    for pad in pads:
        if touches(pad, pt):
            return True
    for via in vias:
        if near(pt, via.GetPosition()) and via_changes_layer(via, tracks):
            return True
    for other in tracks:
        if other is track:
            continue
        if (
            near(pt, other.GetStart())
            or near(pt, other.GetEnd())
            or on_segment(pt, other.GetStart(), other.GetEnd())
        ):
            return True
    return False


def trim_contact_spurs(board):
    removed = 0
    for _ in range(50):
        progress = False
        for netname in CONTACT:
            tracks, vias, pads = same_net_items(board, netname)
            for track in tracks:
                start_ok = end_anchored(track.GetStart(), track, tracks, vias, pads)
                end_ok = end_anchored(track.GetEnd(), track, tracks, vias, pads)
                if start_ok == end_ok:
                    continue
                print(
                    "trim",
                    netname,
                    "track",
                    mm(track.GetStart().x),
                    mm(track.GetStart().y),
                    "->",
                    mm(track.GetEnd().x),
                    mm(track.GetEnd().y),
                )
                board.Remove(track)
                removed += 1
                progress = True
                break
            if progress:
                break
            for via in vias:
                if via_changes_layer(via, tracks):
                    continue
                print("trim", netname, "via", mm(via.GetPosition().x), mm(via.GetPosition().y))
                board.Remove(via)
                removed += 1
                progress = True
                break
            if progress:
                break
        if not progress:
            break
    else:
        raise SystemExit("contact spur trim did not finish")
    print("trimmed", removed)
    for netname in CONTACT:
        assert_contact_connected(board, netname)


def assert_contact_connected(board, netname):
    tracks, vias, pads = same_net_items(board, netname)
    parent = {}

    def find(key):
        parent.setdefault(key, key)
        if parent[key] != key:
            parent[key] = find(parent[key])
        return parent[key]

    def union(left, right):
        left, right = find(left), find(right)
        parent[right] = left

    for index, pad in enumerate(pads):
        find(("pad", index))
    for index, via in enumerate(vias):
        find(("via", index))
    for index, track in enumerate(tracks):
        find(("start", index))
        find(("end", index))
        union(("start", index), ("end", index))
        for pad_index, pad in enumerate(pads):
            if touches(pad, track.GetStart()):
                union(("pad", pad_index), ("start", index))
            if touches(pad, track.GetEnd()):
                union(("pad", pad_index), ("end", index))
        for via_index, via in enumerate(vias):
            if near(track.GetStart(), via.GetPosition()):
                union(("via", via_index), ("start", index))
            if near(track.GetEnd(), via.GetPosition()):
                union(("via", via_index), ("end", index))
        for other_index, other in enumerate(tracks):
            if other_index <= index:
                continue
            pairs = (
                (("start", index), track.GetStart(), other.GetStart(), ("start", other_index)),
                (("start", index), track.GetStart(), other.GetEnd(), ("end", other_index)),
                (("end", index), track.GetEnd(), other.GetStart(), ("start", other_index)),
                (("end", index), track.GetEnd(), other.GetEnd(), ("end", other_index)),
            )
            for left_key, left_pt, right_pt, right_key in pairs:
                if near(left_pt, right_pt) or on_segment(left_pt, other.GetStart(), other.GetEnd()):
                    union(left_key, right_key)
    groups = {find(("pad", index)) for index in range(len(pads))}
    if len(pads) < 2 or len(groups) != 1:
        raise SystemExit(f"{netname} pads are not one connected net ({len(groups)} groups, {len(pads)} pads)")
    print(netname, "pads connected", len(pads))


def check_clearance(board, added):
    worst = 0.2
    problems = 0
    pads = []
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            pads.append((footprint.GetReference(), pad))
    existing = [track for track in board.GetTracks() if track.GetClass() != "PCB_VIA" and track not in added]
    for track in added:
        start = (mm(track.GetStart().x), mm(track.GetStart().y))
        end = (mm(track.GetEnd().x), mm(track.GetEnd().y))
        half = mm(track.GetWidth()) / 2
        for ref, pad in pads:
            if pad.GetNetname() == track.GetNetname() or not pad.IsOnLayer(track.GetLayer()):
                continue
            gap = dist_seg_box(start, end, pad_box(pad)) - half
            if gap < worst - 1e-6:
                problems += 1
                print(
                    f"clearance {gap:.3f} {track.GetNetname()} vs {ref} pad {pad.GetNumber()} {pad.GetNetname()}"
                )
                worst = min(worst, gap)
        for other in existing:
            if other.GetNetname() == track.GetNetname() or other.GetLayer() != track.GetLayer():
                continue
            other_seg = (
                (mm(other.GetStart().x), mm(other.GetStart().y)),
                (mm(other.GetEnd().x), mm(other.GetEnd().y)),
            )
            gap = dist_seg_seg(start, end, other_seg[0], other_seg[1]) - half - mm(other.GetWidth()) / 2
            if gap < 0.2 - 1e-6:
                problems += 1
                print(
                    f"clearance {gap:.3f} {track.GetNetname()} vs track {other.GetNetname()} "
                    f"{other_seg[0]} {other_seg[1]}"
                )
    # New tracks against each other.
    for index, track in enumerate(added):
        start = (mm(track.GetStart().x), mm(track.GetStart().y))
        end = (mm(track.GetEnd().x), mm(track.GetEnd().y))
        half = mm(track.GetWidth()) / 2
        for other in added[index + 1 :]:
            if other.GetNetname() == track.GetNetname() or other.GetLayer() != track.GetLayer():
                continue
            other_seg = (
                (mm(other.GetStart().x), mm(other.GetStart().y)),
                (mm(other.GetEnd().x), mm(other.GetEnd().y)),
            )
            gap = dist_seg_seg(start, end, other_seg[0], other_seg[1]) - half - mm(other.GetWidth()) / 2
            if gap < 0.2 - 1e-6:
                problems += 1
                print(f"clearance {gap:.3f} {track.GetNetname()} vs {other.GetNetname()}")
    print("clearance problems", problems)
    if problems:
        raise SystemExit("new copper is inside 0.2 mm")


def delete_dn_gate_stub(board):
    """The front-copper run from the DN_GATE via to the old gate pad is only
    a spur once the pad track has been removed. The via still carries the
    net on In2.Cu."""
    for track in list(board.GetTracks()):
        if track.GetClass() == "PCB_VIA" or track.GetLayer() != pcbnew.F_Cu:
            continue
        if track.GetNetname() != "DN_GATE":
            continue
        xs = sorted((mm(track.GetStart().x), mm(track.GetEnd().x)))
        ys = (mm(track.GetStart().y), mm(track.GetEnd().y))
        if 20.5 <= xs[0] and xs[1] <= 22.6 and all(87.0 < y < 87.8 for y in ys):
            print("delete DN_GATE stub")
            board.Remove(track)


def add_dn_gate(board, pad, added):
    """Pad 2 cannot be reached from the existing DN_GATE via without crossing
    DN_LOW or the down-coil diode. A through via beside the pad joins In2.Cu,
    which is clear back to the existing via."""
    net = pad.GetNet()
    old = None
    for item in board.GetTracks():
        if item.GetClass() != "PCB_VIA" or item.GetNetname() != "DN_GATE":
            continue
        if abs(mm(item.GetPosition().x) - 22.311) < 0.05 and abs(mm(item.GetPosition().y) - 87.416) < 0.05:
            old = item
    if old is None:
        raise SystemExit("DN_GATE via not found")
    # x=17.1 clears the In1 UP_LOW track at x=16.21. The old via only changed
    # layer for the spur that was removed, so the In2 track takes its place.
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(17.1, 92.3))
    via.SetWidth(nm(0.6))
    via.SetDrill(nm(0.3))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)
    front = [
        point(17.1, 92.3),
        point(17.1, 91.5146),
        pad.GetPosition(),
    ]
    inner = [
        point(17.1, 92.3),
        point(17.1, 86.5),
        point(22.311, 86.5),
        old.GetPosition(),
    ]
    for start, end in segments_of(front):
        added.append(add_track(board, start, end, nm(0.25), net))
    for start, end in segments_of(inner):
        track = add_track(board, start, end, nm(0.25), net)
        track.SetLayer(pcbnew.In2_Cu)
        added.append(track)
    board.Remove(old)
    print(" routed DN_GATE via 17.1,92.3 and removed the old layer-change via")


def apply_title(board):
    block = board.GetTitleBlock()
    block.SetRevision("install")
    block.SetComment(0, "NOT FOR FABRICATION. No Gerbers in this revision.")
    block.SetComment(1, "Coil drivers are ZXMS6004FF. F_COIL is 250 mA.")
    block.SetComment(2, "No component across COM-NO. Contactor diode is off this board.")
    board.SetTitleBlock(block)


def main():
    shutil.copyfile(SRC_BOARD, BOARD)
    board = pcbnew.LoadBoard(BOARD)
    by_ref = {footprint.GetReference(): footprint for footprint in list(board.GetFootprints())}
    added = []

    for ref in ("Q_UP", "Q_DN", "Q_SERIES"):
        footprint = by_ref[ref]
        pads = {pad.GetNumber(): pad for pad in footprint.Pads()}
        old_net = {number: pad.GetNet() for number, pad in pads.items()}
        jobs = []
        for number, pad in pads.items():
            for track in list(board.GetTracks()):
                if track.GetClass() == "PCB_VIA" or track.GetLayer() != pcbnew.F_Cu:
                    continue
                if track.GetNetname() != pad.GetNetname():
                    continue
                start_on = touches(pad, track.GetStart())
                end_on = touches(pad, track.GetEnd())
                if not start_on and not end_on:
                    continue
                far = None
                if start_on and not end_on:
                    far = track.GetEnd()
                elif end_on and not start_on:
                    far = track.GetStart()
                jobs.append((pad.GetNetname(), far, track.GetWidth(), track))
        for _netname, _far, _width, track in jobs:
            board.Remove(track)
        for number, pad in pads.items():
            pad.SetNet(old_net[SRC[number]])
        footprint.SetValue("ZXMS6004FF")
        print(ref, {number: pads[number].GetNetname() for number in ("1", "2", "3")})

        seen = set()
        for netname, far, width, _track in jobs:
            if far is None or netname in seen:
                continue
            seen.add(netname)
            if (ref, netname) == ("Q_DN", "DN_GATE"):
                continue
            pad = next(item for item in pads.values() if item.GetNetname() == netname)
            points = [far]
            for x, y in ROUTES[(ref, netname)]:
                points.append(point(x, y))
            points.append(pad.GetPosition())
            for start, end in segments_of(points):
                added.append(add_track(board, start, end, width, pad.GetNet()))
            print(" routed", netname, "width", mm(width))
        expected = {key[1] for key in ROUTES if key[0] == ref}
        if ref == "Q_DN":
            expected.add("DN_GATE")
        missing = expected - seen
        if missing:
            raise SystemExit(f"{ref} missing routes {sorted(missing)}")

    delete_dn_gate_stub(board)
    dn_pad = next(pad for pad in by_ref["Q_DN"].Pads() if pad.GetNetname() == "DN_GATE")
    add_dn_gate(board, dn_pad, added)

    for ref in ("D61", "D71"):
        board.Remove(by_ref[ref])
        print("removed", ref)

    trim_contact_spurs(board)

    for ref, value in (("F_COIL", "250mA_0466.250"), ("R60", "1k"), ("R70", "1k")):
        by_ref[ref].SetValue(value)
        print(ref, value)

    apply_title(board)
    check_clearance(board, added)
    board.Save(BOARD)
    print("saved", len(added), "tracks")


if __name__ == "__main__":
    main()
