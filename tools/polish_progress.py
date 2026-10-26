#!/usr/bin/env python3
"""How far the models' polish is: the share of the game's enemy appearances (TYR3D_EXTRACT's catalog.json, each look
weighted by its count) whose model's GLB was last written by a commit with a tools/blender polish_*.py script, for the
enemies, the launched enemies and the drops apart. Looks whose sprite is blank (invisible markers: FLEET's and
BRAINIAC's ground blockers) need no model and are left out. The catalogue's sheets are named as models.cfg names them
(letters small, the symbols x5e x23 x27 x25 x40, twoplayer as powerups).

usage: <python with PIL> tools/polish_progress.py [--extract export/extract] [--missing 25]
"""
import argparse
import collections
import json
import os
import re
import subprocess

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYMBOLS = {"^": "x5e", "#": "x23", "'": "x27", "%": "x25", "@": "x40"}


def cfg_name(sheet):
    return "powerups" if sheet == "twoplayer" else SYMBOLS.get(sheet, sheet.lower())


def blank(extract, sheet, sprite, large, cell, columns, cache={}):
    """Whether the look's sprite has no pixel (its cells: n, n+1, n+columns, n+columns+1 for a large one)."""
    name = "enemy_" + SYMBOLS.get(sheet, sheet) if sheet not in ("coins", "twoplayer") else \
        ("coins" if sheet == "coins" else "powerups")
    path = os.path.join(extract, "sheets", name + ".png")
    if not os.path.exists(path):
        return False
    if path not in cache:
        cache[path] = np.array(Image.open(path).convert("RGBA"))[..., 3] > 0
    alpha = cache[path]
    cw, ch = cell
    cells = [sprite - 1] + ([sprite, sprite - 1 + columns, sprite + columns] if large else [])
    for i in cells:
        r, c = divmod(i, columns)
        if alpha[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw].any():
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", default=os.path.join(ROOT, "export", "extract"))
    ap.add_argument("--missing", type=int, default=25)
    a = ap.parse_args()
    cat = json.load(open(os.path.join(a.extract, "catalog.json")))
    models, sprites = {}, {}
    for line in open(os.path.join(ROOT, "assets", "models", "models.cfg")):
        t = line.split()
        if len(t) >= 3 and t[0] == "model":
            models[t[1]] = "assets/models/" + t[2]
        elif len(t) >= 4 and t[0] == "sprite":
            sprites[(t[1], int(t[2]))] = t[3]
    # The last commit that wrote each file, and whether each commit has a polish script.
    log = subprocess.run(["git", "-C", ROOT, "log", "--format=commit %H", "--name-only"], capture_output=True,
                         text=True).stdout
    last, polish, commit = {}, {}, None
    for line in log.splitlines():
        if line.startswith("commit "):
            commit = line[7:]
            polish[commit] = False
        elif line.strip():
            if re.search(r"/polish_[^/]*\.py$", line.strip()):
                polish[commit] = True
            last.setdefault(line.strip(), commit)
    total, done, missing, invisible = collections.Counter(), collections.Counter(), collections.Counter(), 0
    for e in cat["enemies"]:
        frames = e.get("frames") or []
        if not frames:
            continue
        layers = e.get("layers", [])
        kind = "drops" if "drop" in layers else "launched" if "launched" in layers else "enemies"
        count = e.get("count", 1) or 1
        if blank(a.extract, e["sheet"], frames[0], e.get("large", False), cat["cell"], cat["columns"]):
            invisible += count
            continue
        key = (cfg_name(e["sheet"]), frames[0])
        total[kind] += count
        model = sprites.get(key)
        commit = last.get(models.get(model)) if model else None
        if commit and polish.get(commit):
            done[kind] += count
        else:
            missing[(kind, key, model)] += count
    for kind in ("enemies", "launched", "drops"):
        if total[kind]:
            print(f"{kind}: {100.0 * done[kind] / total[kind]:.2f} % ({done[kind]} of {total[kind]})")
    print(f"all: {100.0 * sum(done.values()) / max(sum(total.values()), 1):.2f} % "
          f"(blank looks left out: {invisible} appearances)")
    for (kind, key, model), count in missing.most_common(a.missing):
        print(f"  {count:5d} {kind:8} {key[0]} {key[1]}: {model or 'no model'}")


if __name__ == "__main__":
    main()
