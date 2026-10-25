#!/usr/bin/env python3
"""A model in other palette colours: copies a GLB with its palette materials ("name@index", as models.cfg's
models take their colours) moved to other indices, the geometry as it is.
usage: python3 tools/glb_palette_remap.py <in.glb> <out.glb> <old>=<new>...   (indices in decimal or 0x hex)
e.g.   python3 tools/glb_palette_remap.py assets/models/enemies/block_rubble.glb \\
           assets/models/enemies/block_rubble_brown.glb 71=0xa3 74=0xa4 65=0x12 68=0xa2
"""
import json
import re
import struct
import sys


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    remap = {int(a, 0): int(b, 0) for a, b in (p.split("=") for p in sys.argv[3:])}
    data = open(src, "rb").read()
    magic, version, _ = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF", "not a binary glTF"
    length, kind = struct.unpack_from("<I4s", data, 12)
    assert kind == b"JSON"
    doc = json.loads(data[20:20 + length])
    rest = data[20 + length:]
    for m in doc.get("materials", []):
        name = m.get("name", "")
        match = re.fullmatch(r"(.*)@(\d+)", name)
        if match and int(match.group(2)) in remap:
            m["name"] = f"{match.group(1)}@{remap[int(match.group(2))]}"
    text = json.dumps(doc, separators=(",", ":")).encode()
    text += b" " * (-len(text) % 4)
    out = struct.pack("<4sII", b"glTF", version, 12 + 8 + len(text) + len(rest)) + struct.pack("<I4s", len(text), b"JSON")
    open(dst, "wb").write(out + text + rest)
    print(dst, [m.get("name") for m in doc.get("materials", [])])


if __name__ == "__main__":
    main()
