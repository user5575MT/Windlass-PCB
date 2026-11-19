"""Stamp schematic netlist names onto the placement board.

Matches reference designator and pad number. A footprint is left untouched
when the netlist asks for a pin that the footprint does not have, so a
two-pad stand-in cannot be presented as the three-pin reed switch.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NETLIST = ROOT / "docs" / "windlass.net"
BOARD = ROOT / "kicad" / "placement_finder.kicad_pcb"
REPORT = ROOT / "docs" / "net_assignment.txt"


def parse_netlist(text: str) -> dict[str, dict[str, str]]:
    """KiCad sexpr netlist, pretty-printed with one token per line."""
    nets: dict[str, dict[str, str]] = {}
    for block in text.split("(net")[1:]:
        name = re.search(r'\(name "([^"]+)"\)', block)
        if not name:
            continue
        for ref, pin in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', block):
            nets.setdefault(ref, {})[pin] = name.group(1)
    return nets


def sexpr_blocks(text: str, keyword: str) -> list[tuple[int, int]]:
    spans = []
    token = f"({keyword}"
    i = 0
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
                    spans.append((start, j + 1))
                    i = j + 1
                    break
        else:
            break
    return spans


def reference_of(block: str) -> str | None:
    match = re.search(r'\(property "Reference" "([^"]+)"', block)
    return match.group(1) if match else None


def pad_numbers(block: str) -> set[str]:
    return set(re.findall(r'\(pad "([^"]*)"', block))


def stamp_pad(block: str, number: str, net_id: int, net_name: str) -> str:
    token = f'(pad "{number}"'
    out = []
    i = 0
    while True:
        start = block.find(token, i)
        if start < 0:
            out.append(block[i:])
            break
        depth = 0
        end = None
        for j in range(start, len(block)):
            if block[j] == "(":
                depth += 1
            elif block[j] == ")":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        pad = block[start:end]
        pad = re.sub(r'\(net (?:\d+ )?"[^"]*"\)\s*', "", pad, count=1)
        net = f'(net "{net_name}")'
        updated, count = re.subn(
            r'^(\(pad "[^"]*" (?:smd|thru_hole|np_thru_hole|connect) \S+)',
            rf"\1 {net}",
            pad,
            count=1,
        )
        if count != 1:
            raise SystemExit(f"could not stamp pad {number}")
        pad = updated
        out.append(block[i:start])
        out.append(pad)
        i = end
    return "".join(out)


def main() -> None:
    pins = parse_netlist(NETLIST.read_text(encoding="utf-8"))
    if not pins:
        sys.exit("netlist parser found no nets")
    names = sorted({net for pads in pins.values() for net in pads.values()})
    ids = {name: i + 1 for i, name in enumerate(names)}
    text = BOARD.read_text(encoding="utf-8")
    spans = sexpr_blocks(text, "footprint")
    skipped = []
    missing_fp = []
    assigned = 0
    pieces = []
    cursor = 0
    seen = set()
    for start, end in spans:
        block = text[start:end]
        ref = reference_of(block)
        pieces.append(text[cursor:start])
        cursor = end
        if ref is None or ref not in pins:
            pieces.append(block)
            if ref:
                missing_fp.append(ref)
            continue
        seen.add(ref)
        wanted = pins[ref]
        have = pad_numbers(block)
        absent = [pin for pin in wanted if pin not in have]
        if absent:
            skipped.append(f"{ref}: footprint has no pad {', '.join(absent)}")
            pieces.append(block)
            continue
        for number, name in wanted.items():
            if name.startswith("unconnected-"):
                continue
            block = stamp_pad(block, number, ids[name], name)
            assigned += 1
        pieces.append(block)
    pieces.append(text[cursor:])
    BOARD.write_text("".join(pieces), encoding="utf-8")
    unused = sorted(set(pins) - seen)
    lines = [
        f"nets {len(names)}",
        f"pads stamped {assigned}",
        f"footprints skipped {len(skipped)}",
        *skipped,
        f"schematic refs with no footprint {len(unused)}",
        *unused,
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:20]))
    if len(lines) > 20:
        print(f"... {len(lines) - 20} more lines in {REPORT.name}")


if __name__ == "__main__":
    main()
