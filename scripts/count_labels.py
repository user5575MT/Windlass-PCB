import collections
import re
from pathlib import Path

c = collections.Counter()
for p in Path(r"C:\Users\thoma\Windlass-PCB\kicad").glob("*.kicad_sch"):
    for m in re.finditer(r'global_label "([^"]+)"', p.read_text(encoding="utf-8")):
        c[m.group(1)] += 1
print("SINGLE")
for k, v in sorted(c.items()):
    if v == 1:
        print(f"  {k}")
print("ALL")
for k, v in sorted(c.items()):
    print(f"{v:3} {k}")
