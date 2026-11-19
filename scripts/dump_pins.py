"""Print KiCad symbol pin numbers, names, and coordinates."""
import sys
from pathlib import Path

LIB = Path(r"C:\Users\thoma\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols")


def parse(text):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c == "(":
            tokens.append("(")
            i += 1
            continue
        if c == ")":
            tokens.append(")")
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
            tokens.append("".join(buf))
            continue
        j = i
        while i < n and not text[i].isspace() and text[i] not in "()":
            i += 1
        tokens.append(text[j:i])

    def read(k):
        tok = tokens[k]
        if tok != "(":
            return tok, k + 1
        k += 1
        items = []
        while tokens[k] != ")":
            item, k = read(k)
            items.append(item)
        return items, k + 1

    tree, _ = read(0)
    return tree


def top_symbols(tree):
    # (kicad_symbol_lib (version ...) (symbol "NAME" ...))
    out = {}
    for item in tree:
        if isinstance(item, list) and item and item[0] == "symbol":
            out[item[1]] = item
    return out


def pins_of(sym):
    pins = []
    def walk(node, unit):
        if not isinstance(node, list):
            return
        if node and node[0] == "symbol" and isinstance(node[1], str) and "_" in node[1]:
            # NAME_U_S
            tail = node[1].rsplit("_", 2)
            if len(tail) == 3 and tail[1].isdigit():
                unit = int(tail[1])
        if node and node[0] == "pin":
            at = next(x for x in node if isinstance(x, list) and x[0] == "at")
            num = next(x for x in node if isinstance(x, list) and x[0] == "number")
            name = next(x for x in node if isinstance(x, list) and x[0] == "name")
            pins.append((unit, num[1], name[1], node[1], float(at[1]), float(at[2]), float(at[3])))
        for child in node:
            if isinstance(child, list):
                walk(child, unit)
    walk(sym, 0)
    return pins


def main():
    queries = sys.argv[1:]
    files = {}
    for q in queries:
        lib, name = q.split(":")
        if lib not in files:
            files[lib] = top_symbols(parse((LIB / f"{lib}.kicad_sym").read_text(encoding="utf-8")))
        sym = files[lib][name]
        print(f"\n== {q} ==")
        for unit, num, name_, ptype, x, y, ang in pins_of(sym):
            print(f"  u{unit} {num:6} {name_:16} {ptype:12} ({x:7.2f},{y:7.2f}) {ang}")


if __name__ == "__main__":
    main()
