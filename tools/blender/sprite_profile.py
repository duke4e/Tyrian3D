#!/usr/bin/env python3
"""Measures a sprite for modelling: its silhouette per pixel row, a brightness map and its main
colours, read from a sheet exported by TYR3D_EXTRACT (19 columns of 12x14 cells).

usage: tools/blender/sprite_profile.py <sheet.png> <sprite index> [--small] [--png out.png]

For each row: the row, its left and right edges relative to the sprite's centre column (12 for a
2x2 sprite, 6 for a 1x1 one), the half-width (as tyrkit model scripts take it), and the row's
pixels as brightness digits (0-9, '.' for transparent). --png writes the sprite enlarged 16 times.
"""
import collections
import struct
import sys
import zlib


def read_png(path):
    data = open(path, "rb").read()
    i, idat = 8, b""
    while i < len(data):
        length = struct.unpack(">I", data[i:i + 4])[0]
        kind, chunk = data[i + 4:i + 8], data[i + 8:i + 8 + length]
        i += 12 + length
        if kind == b"IHDR":
            width, height, _, colour_type = struct.unpack(">IIBB", chunk[:10])
        elif kind == b"IDAT":
            idat += chunk
    bpp = 4 if colour_type == 6 else 3
    raw = zlib.decompress(idat)
    stride = width * bpp
    rows, previous = [], bytearray(stride)
    for y in range(height):
        kind = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = previous[x]
            c = previous[x - bpp] if x >= bpp else 0
            if kind == 1:
                line[x] = (line[x] + a) & 255
            elif kind == 2:
                line[x] = (line[x] + b) & 255
            elif kind == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif kind == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line))
        previous = line
    return width, height, bpp, rows


def sprite_pixels(sheet, index, large=True):
    """The sprite's pixels as rows of (r, g, b) or None for transparent."""
    width, height, bpp, rows = read_png(sheet)
    w, h = (24, 28) if large else (12, 14)
    x0, y0 = (index - 1) % 19 * 12, (index - 1) // 19 * 14
    out = []
    for y in range(h):
        line = []
        for x in range(w):
            p = rows[y0 + y][(x0 + x) * bpp:(x0 + x) * bpp + bpp]
            line.append(None if bpp == 4 and p[3] == 0 else tuple(p[:3]))
        out.append(line)
    return out


def write_png(path, rows, scale=16):
    h, w = len(rows), len(rows[0])
    raw = b""
    for y in range(h * scale):
        line = bytearray(b"\x00")
        for x in range(w * scale):
            p = rows[y // scale][x // scale] or (48, 0, 48)
            line += bytes(p)
        raw += bytes(line)

    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w * scale, h * scale, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)


def main():
    args = sys.argv[1:]
    sheet, index = args[0], int(args[1])
    large = "--small" not in args
    pixels = sprite_pixels(sheet, index, large)
    centre = 12 if large else 6
    colours = collections.Counter()
    print("row  left right half  pixels")
    for y, line in enumerate(pixels):
        covered = [x for x, p in enumerate(line) if p is not None]
        digits = "".join("." if p is None else str(min(9, int((0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]) / 26)))
                         for p in line)
        colours.update(p for p in line if p is not None)
        if covered:
            left, right = covered[0] - centre, covered[-1] + 1 - centre
            print(f"{y:3}  {left:4} {right:5} {max(-left, right) / 1:5.1f}  {digits}")
        else:
            print(f"{y:3}                   {digits}")
    print("colours:", ", ".join(f"{c}x{n}" for c, n in colours.most_common(12)))
    if "--png" in args:
        write_png(args[args.index("--png") + 1], pixels)


if __name__ == "__main__":
    main()
