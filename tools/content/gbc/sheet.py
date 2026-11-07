#!/usr/bin/env python3
"""Episode 7's own sprite sheet, W (newshw.shp): the sprites of the enemies the GBC levels have and the PC game has not
(tools/content/gbc/new_enemies.json), drawn from their models' top views (the model scripts' --sprite renders) in the
levels' palette. Writes tools/content/gbc/newshw.shp (the game's compressed sprite format: a table of the 12 x 14
sprites' offsets, each sprite's rows as runs of skipped and drawn pixels) and sheet_w.png (the sheet as the game draws
it, 4x, to look at); build.py copies the sheet into assets/content/episode7, where the game finds it (src/file.c).

usage: <python with PIL> tools/content/gbc/sheet.py [<render dir>]
       (the render dir holds <enemy>.png, each model's --sprite render; without one, or without an enemy's render, its
       sprites stay as newshw.shp has them; an enemy with "recolor" is a PC sheet's sprite in other colours, from the
       extracted sheets: SPACE ATK's yellow crystal, 2:794's lilac moved to the yellows, as its model's,
       tools/glb_palette_remap.py)
"""
import json
import os
import struct
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PALETTE = os.path.join(ROOT, "tools", "blender", "palette_levels.txt")
COLS = 19      # sprites a row of a sheet (a 2x2 sprite n is n, n + 1, n + 19, n + 20)
TW, TH = 12, 14


def palette():
    return [tuple(int(v) for v in line.split()) for line in open(PALETTE) if line.strip()]


def quantize(img, ramps, pal):
    """An RGBA picture as palette indices (None: transparent), each pixel the nearest shade of the given ramps."""
    shades = [16 * r + s for r in ramps for s in range(1, 16)]
    out = []
    for y in range(img.height):
        row = []
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a < 128:
                row.append(None)
                continue
            r, g, b = (int(round(c * 255 / max(a, 1))) for c in (r, g, b))  # (premultiplied when shrunk)
            row.append(min(shades, key=lambda i: (pal[i][0] - r) ** 2 * 3 + (pal[i][1] - g) ** 2 * 4 +
                           (pal[i][2] - b) ** 2 * 2))
        out.append(row)
    return out


def shrink(path, w, h):
    """The render brought down to the sprites' pixels (its alpha premultiplied, so edges don't take the background)."""
    return Image.open(path).convert("RGBa").resize((w, h), Image.BOX)


def encode(tile):
    """One 12 x 14 sprite (rows of indices or None) in the game's format (sprite.c blit_sprite2)."""
    out = bytearray()
    last = max([y for y, row in enumerate(tile) if any(v is not None for v in row)], default=-1)
    for y in range(last + 1):
        row, x = tile[y], 0
        while x < TW:
            skip = 0
            while x + skip < TW and row[x + skip] is None:
                skip += 1
            run = 0
            while x + skip + run < TW and row[x + skip + run] is not None:
                run += 1
            if run == 0:
                break
            out.append((run << 4) | skip)
            out += bytes(row[x + skip:x + skip + run])
            x += skip + run
        out.append(TW - x)  # (the row's end: skip to its end, nothing drawn)
    out.append(0x0F)
    return bytes(out)


def write_sheet(tiles, path):
    """tiles: index -> 12 x 14 sprite; the table covers 1 .. the largest index (the others empty)."""
    n = max(tiles)
    empty = bytes([0x0F])
    blobs = [encode(tiles[i]) if i in tiles else empty for i in range(1, n + 1)]
    offset = 2 * n
    table, data = b"", b""
    for blob in blobs:
        table += struct.pack("<H", offset + len(data))
        data += blob
    open(path, "wb").write(table + data)
    return n


def decode(data, index):
    """A sprite back from the sheet (rows of indices or None), as blit_sprite2 draws it."""
    at = struct.unpack_from("<H", data, 2 * (index - 1))[0]
    tile = [[None] * TW for _ in range(TH)]
    x = y = 0
    while data[at] != 0x0F:
        b = data[at]
        x += b & 0x0F
        count = b >> 4
        if count == 0:
            y, x = y + 1, x - TW
        else:
            for _ in range(count):
                at += 1
                tile[y][x] = data[at]
                x += 1
        at += 1
    return tile


def recolored(e, pal):
    """A PC sheet's sprite (the extracted sheets' pictures, export/extract/sheets: TYR3D_EXTRACT) as palette indices, its
    colours moved ("map": index -> index, as tools/glb_palette_remap.py moves a model's): the picture of a recolour."""
    rc = e["recolor"]
    big = rc.get("big", True)
    src = Image.open(os.path.join(ROOT, "export", "extract", "sheets", f"enemy_{rc['sheet']}.png")).convert("RGBA")
    col, row = (rc["sprite"] - 1) % COLS, (rc["sprite"] - 1) // COLS
    w, h = (2 * TW, 2 * TH) if big else (TW, TH)
    crop = src.crop((col * TW, row * TH, col * TW + w, row * TH + h))
    moved = {int(a, 0): int(b, 0) for a, b in rc["map"].items()}
    out = []
    for y in range(h):
        line = []
        for x in range(w):
            r, g, b, a = crop.getpixel((x, y))
            if a < 128:
                line.append(None)
                continue
            i = min(range(256), key=lambda i: (pal[i][0] - r) ** 2 + (pal[i][1] - g) ** 2 + (pal[i][2] - b) ** 2)
            line.append(moved.get(i, i))
        out.append(line)
    return out


def main():
    # (without a render dir, or a render, an enemy drawn from its model keeps the sprites it has in newshw.shp)
    renders = sys.argv[1] if len(sys.argv) > 1 else None
    pal = palette()
    spec = json.load(open(os.path.join(HERE, "new_enemies.json")))
    old = open(os.path.join(HERE, "newshw.shp"), "rb").read() if os.path.exists(os.path.join(HERE, "newshw.shp")) else None
    tiles = {}
    for name, e in spec.items():
        if "sheet" in e:
            continue  # (a look of a PC sheet: nothing of its own to draw)
        w, h = 24 * e["columns"], 28 * e["rows"]
        if "recolor" in e:
            picture = recolored(e, pal)
        elif renders and os.path.exists(os.path.join(renders, name + ".png")):
            picture = quantize(shrink(os.path.join(renders, name + ".png"), w, h), e["ramps"], pal)
        else:
            assert old, f"{name}: no render and no sheet to keep its sprites from"
            for part in e["parts"]:
                for ty in range(2):
                    for tx in range(2):
                        k = part["sprite"] + tx + COLS * ty
                        tiles[k] = decode(old, k)
            continue
        for part in e["parts"]:
            # the part's 2x2 sprite: its column and row in the picture (row 0 the top), its first sprite
            c, r, first = part["column"], part["row"], part["sprite"]
            for ty in range(2):
                for tx in range(2):
                    tiles[first + tx + COLS * ty] = [picture[28 * r + TH * ty + yy][24 * c + TW * tx:24 * c + TW * tx + TW]
                                                     for yy in range(TH)]
    path = os.path.join(HERE, "newshw.shp")
    n = write_sheet(tiles, path)
    data = open(path, "rb").read()
    for i, t in tiles.items():
        assert decode(data, i) == t, i
    rows = (n + COLS - 1) // COLS
    sheet = Image.new("RGBA", (COLS * TW, rows * TH))
    for i in range(1, n + 1):
        t = decode(data, i)
        for y in range(TH):
            for x in range(TW):
                if t[y][x] is not None:
                    sheet.putpixel(((i - 1) % COLS * TW + x, (i - 1) // COLS * TH + y), pal[t[y][x]] + (255,))
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(os.path.join(HERE, "sheet_w.png"))
    print(f"{path}: {n} sprites, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
