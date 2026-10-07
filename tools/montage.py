#!/usr/bin/env python3
"""Arrange BMP frame dumps into a single PNG grid (stdlib only).

usage: tools/montage.py out.png columns scale in1.bmp in2.bmp ...

scale may be fractional (0.25 shrinks each image to a quarter of its size). On macOS, sips does
the shrinking, which is much faster than reading full-size dumps here.
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib


def read_bmp(path):
    with open(path, "rb") as f:
        data = f.read()
    offset = struct.unpack_from("<I", data, 10)[0]
    width, height = struct.unpack_from("<ii", data, 18)
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    masks = None
    if compression == 3 or compression == 6:  # BI_BITFIELDS / BI_ALPHABITFIELDS
        masks = struct.unpack_from("<IIII", data, 54)
    bottom_up = height > 0
    height = abs(height)
    stride = ((width * bpp + 31) // 32) * 4
    pixels = []
    for row in range(height):
        src_row = (height - 1 - row) if bottom_up else row
        base = offset + src_row * stride
        line = []
        for x in range(width):
            if bpp == 32:
                (value,) = struct.unpack_from("<I", data, base + x * 4)
                if masks:
                    def channel(mask):
                        if mask == 0:
                            return 255
                        shift = (mask & -mask).bit_length() - 1
                        return (value & mask) >> shift
                    line.append((channel(masks[0]), channel(masks[1]), channel(masks[2])))
                else:
                    line.append(((value >> 16) & 255, (value >> 8) & 255, value & 255))
            elif bpp == 24:
                b, g, r = data[base + x * 3: base + x * 3 + 3]
                line.append((r, g, b))
            else:
                raise ValueError(f"unsupported bpp {bpp} in {path}")
        pixels.append(line)
    return width, height, pixels


def write_png(path, width, height, rows):
    raw = b"".join(b"\x00" + bytes(c for px in row for c in px) for row in rows)

    def chunk(tag, payload):
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def load(path, scale):
    """Returns the image and the scale still to apply to it."""
    if scale < 1 and shutil.which("sips"):
        with open(path, "rb") as f:
            width, height = struct.unpack_from("<ii", f.read(26), 18)
        size = [str(max(1, int(abs(height) * scale))), str(max(1, int(width * scale)))]
        with tempfile.TemporaryDirectory() as tmp:
            small = os.path.join(tmp, "small.bmp")
            subprocess.run(["sips", "-s", "format", "bmp", "-z", *size, path, "--out", small],
                           check=True, capture_output=True)
            return read_bmp(small), 1.0
    return read_bmp(path), scale


def main():
    out, columns, scale = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    loaded = [load(p, scale) for p in sys.argv[4:]]
    images = [image for image, _ in loaded]
    scale = loaded[0][1]
    cell_w = int(max(w for w, _, _ in images) * scale)
    cell_h = int(max(h for _, h, _ in images) * scale)
    gap = 4
    rows_n = (len(images) + columns - 1) // columns
    width = columns * cell_w + (columns - 1) * gap
    height = rows_n * cell_h + (rows_n - 1) * gap
    canvas = [[(40, 40, 40)] * width for _ in range(height)]
    for i, (w, h, px) in enumerate(images):
        ox = (i % columns) * (cell_w + gap)
        oy = (i // columns) * (cell_h + gap)
        for y in range(int(h * scale)):
            row = canvas[oy + y]
            src = px[min(h - 1, int(y / scale))]
            for x in range(int(w * scale)):
                row[ox + x] = src[min(w - 1, int(x / scale))]
    write_png(out, width, height, canvas)


if __name__ == "__main__":
    main()
