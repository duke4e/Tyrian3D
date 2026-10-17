#!/usr/bin/env python3
"""Contact sheets of the enemy models beside their sprites, for reviewing the models.

usage: <python with PIL> tools/model_sheet.py <renders dir> <out prefix> [--catalog <catalog.json>]
           [--episodes 1,2] [--per-page 48]

<renders dir>: PNGs from tools/blender/render_models.py, named after the models' .glb files.
Each cell shows the sprite (the 4x upscale from upscale/out/sheets, or the original sheet from
the catalog's export) and the model's render, labelled with the models.cfg rule. With a catalog
(TYR3D_EXTRACT), cells are ordered by how often the enemy appears and limited to the episodes
given. Pages are written as <out prefix>_<n>.png.
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CELL = 160
COLUMNS = 6


def model_files():
    """models.cfg model name -> .glb path (relative to assets/models)."""
    files = {}
    for line in open(os.path.join(ROOT, "assets", "models", "models.cfg")):
        t = line.split("#", 1)[0].split()
        if len(t) >= 3 and t[0] == "model":
            files[t[1]] = t[2]
    return files


def sprite_rules():
    """(sheet, first sprite, model name) for every sprite line of models.cfg."""
    rules = []
    for line in open(os.path.join(ROOT, "assets", "models", "models.cfg")):
        t = line.split("#", 1)[0].split()
        if len(t) >= 4 and t[0] == "sprite":
            rules.append((t[1], int(t[2]), t[3]))
    return rules


def sheet_file(sheet):
    s = sheet.lower()
    if s in ("coins", "powerups"):
        return s
    if re.fullmatch(r"x[0-9a-f]{2}", s):
        return "enemy_" + s
    return "enemy_" + (sheet.upper() if sheet.isalpha() else sheet)


_sheets = {}


def sprite_image(sheet, index, large):
    name = sheet_file(sheet)
    if name not in _sheets:
        path = os.path.join(ROOT, "upscale", "out", "sheets", name + ".png")
        if not os.path.exists(path):
            path = os.path.join(ROOT, "upscale", "out", "sheets", name.replace("enemy_", "enemy_").lower() + ".png")
        _sheets[name] = Image.open(path).convert("RGBA") if os.path.exists(path) else None
    sheet_image = _sheets[name]
    if sheet_image is None:
        return None
    scale = sheet_image.size[0] // (19 * 12)
    c, r = (index - 1) % 19, (index - 1) // 19
    w, h = (24, 28) if large else (12, 14)
    return sheet_image.crop((c * 12 * scale, r * 14 * scale, (c * 12 + w) * scale, (r * 14 + h) * scale))


def fit(image, size):
    image = image.copy()
    image.thumbnail((size, size), Image.LANCZOS if image.size[0] > size else Image.NEAREST)
    if image.size[0] < size // 2:
        f = max(1, (size // 2) // max(image.size[0], 1))
        image = image.resize((image.size[0] * f, image.size[1] * f), Image.NEAREST)
    return image


def main():
    args = sys.argv[1:]
    renders, prefix = args[0], args[1]
    options = {}
    i = 2
    while i < len(args):
        options[args[i][2:]] = args[i + 1]
        i += 2
    per_page = int(options.get("per-page", 48))
    files = model_files()

    order = []
    seen = set()
    info = {}
    if "catalog" in options:
        catalog = json.load(open(options["catalog"]))
        episodes = {int(e) for e in options.get("episodes", "1,2,3,4,5,6").split(",")}
        for e in sorted(catalog["enemies"], key=lambda e: -e.get("count", 0)):
            if e["episode"] in episodes and e.get("frames"):
                info[(e["sheet"].lower(), e["frames"][0])] = e
    for sheet, index, model in sprite_rules():
        key = (sheet.lower(), index)
        if info and key not in info:
            continue
        if model in seen:
            continue
        seen.add(model)
        order.append((sheet, index, model))
    if info:
        rank = {k: n for n, k in enumerate(info)}
        order.sort(key=lambda r: rank.get((r[0].lower(), r[1]), 1 << 30))

    pages = [order[i:i + per_page] for i in range(0, len(order), per_page)]
    for p, page in enumerate(pages):
        rows = (len(page) + COLUMNS - 1) // COLUMNS
        sheet_image = Image.new("RGB", (COLUMNS * CELL * 2, rows * (CELL + 16)), (52, 54, 62))
        draw = ImageDraw.Draw(sheet_image)
        for n, (sheet, index, model) in enumerate(page):
            x, y = (n % COLUMNS) * CELL * 2, (n // COLUMNS) * (CELL + 16)
            e = info.get((sheet.lower(), index))
            large = e["large"] if e else True
            sprite = sprite_image(sheet, index, large)
            if sprite is not None:
                s = fit(sprite, CELL - 8)
                sheet_image.paste(s, (x + (CELL - s.size[0]) // 2, y + (CELL - s.size[1]) // 2), s)
            glb = files.get(model, "")
            render = os.path.join(renders, os.path.splitext(os.path.basename(glb))[0] + ".png")
            if os.path.exists(render):
                r = fit(Image.open(render).convert("RGBA"), CELL - 8)
                sheet_image.paste(r, (x + CELL + (CELL - r.size[0]) // 2, y + (CELL - r.size[1]) // 2), r)
            label = f"{sheet}:{index} {model}" + (f" x{e['count']}" if e else "")
            draw.text((x + 4, y + CELL), label[:40], fill=(220, 220, 220))
        out = f"{prefix}_{p + 1}.png"
        sheet_image.save(out)
        print(out, len(page))


if __name__ == "__main__":
    main()
