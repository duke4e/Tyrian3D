#!/usr/bin/env python3
"""A sprite's reference pictures for modelling: every animation frame of an enemy type from the
4x upscaled atlases (upscale/out, see upscale/README.md), side by side, with the first frame at
its original size enlarged beside them.

usage: <python with PIL> tools/sprite_reference.py <sheet> <first sprite> <out.png> [--extract <dir>]

<sheet> as models.cfg names it: an enemy shape file's letter or digit (e.g. 4, e, x27), coins or
powerups. --extract: a TYR3D_EXTRACT directory, for the original sprite (default: none).
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPSCALE = os.path.join(ROOT, "upscale")
SCALE = 4


def sheet_names(sheet):
    """The names the atlases use for a models.cfg sheet."""
    sheet = sheet.lower()
    if sheet == "powerups":
        return {"powerups", "twoplayer"}
    if sheet == "coins":
        return {"coins"}
    return {"enemy_" + sheet, "enemy_" + sheet.upper()}


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    sheet, first, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    extract = sys.argv[sys.argv.index("--extract") + 1] if "--extract" in sys.argv else None
    index = json.load(open(os.path.join(UPSCALE, "in", "atlases.json")))
    cw, ch = index["cell"]
    names = sheet_names(sheet)

    # The enemy types whose first frame is this sprite, and all their frames' cells.
    cells = [c for c in index["cells"] if c["sheet"] in names]
    enemies = {(c.get("episode"), c.get("enemy")) for c in cells if c["sprite"] == first and c.get("frame", 0) == 0}
    frames = [c for c in cells if (c.get("episode"), c.get("enemy")) in enemies] if enemies else \
        [c for c in cells if c["sprite"] == first]
    seen, pictures = set(), []
    for c in sorted(frames, key=lambda c: (c.get("enemy", 0), c.get("frame", 0))):
        if (c["atlas"], c["column"], c["row"]) in seen or c["sprite"] in {p[0] for p in pictures}:
            continue
        seen.add((c["atlas"], c["column"], c["row"]))
        path = os.path.join(UPSCALE, "out", c["atlas"])
        if not os.path.exists(path):
            continue
        atlas = Image.open(path).convert("RGBA")
        box = (c["column"] * cw * SCALE, c["row"] * ch * SCALE, (c["column"] + 1) * cw * SCALE, (c["row"] + 1) * ch * SCALE)
        pictures.append((c["sprite"], atlas.crop(box)))
    if not pictures:
        # A whole sheet (powerups, coins): 19 columns of 12 x 14 cells.
        for name in names:
            path = os.path.join(UPSCALE, "out", name + ".png")
            if os.path.exists(path):
                atlas = Image.open(path).convert("RGBA")
                col, row = (first - 1) % 19, (first - 1) // 19
                pictures.append((first, atlas.crop((col * 12 * SCALE, row * 14 * SCALE, (col + 2) * 12 * SCALE,
                                                    (row + 2) * 14 * SCALE))))
                break
    if not pictures:
        print(f"no upscaled pictures of {sheet} {first}")
        return 1

    original = None
    if extract:
        for name in names:
            path = os.path.join(extract, "sheets", name + ".png")
            if os.path.exists(path):
                big = any(c.get("size") == "2x2" for c in frames)
                col, row = (first - 1) % 19, (first - 1) // 19
                n = 2 if big else 1
                original = Image.open(path).convert("RGBA").crop((col * 12, row * 14, (col + n) * 12, (row + n) * 14))
                original = original.resize((original.width * SCALE * 2 // n, original.height * SCALE * 2 // n), Image.NEAREST)
                break

    pw, ph = pictures[0][1].size
    width = pw * len(pictures) + (original.width + 8 if original else 0)
    sheet_image = Image.new("RGBA", (width, max(ph, original.height if original else 0) + 14), (40, 40, 48, 255))
    draw = ImageDraw.Draw(sheet_image)
    x = 0
    if original:
        sheet_image.paste(original, (0, 14), original)
        draw.text((2, 1), "original", fill=(255, 230, 80, 255))
        x = original.width + 8
    for sprite, picture in pictures:
        sheet_image.paste(picture, (x, 14), picture)
        draw.text((x + 2, 1), str(sprite), fill=(255, 230, 80, 255))
        x += pw
    sheet_image.save(out)
    print(f"{out}: {len(pictures)} frames")
    return 0


if __name__ == "__main__":
    sys.exit(main())
