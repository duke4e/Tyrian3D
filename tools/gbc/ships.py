"""Episode 7's FLEET: layer 1 space with the original's ships copied whole where the GBC map has its ships (the user:
"brodove baš trebamo uzeti iz pc fleeta, bez ikakve prilagodbe": the PC level's ships look right only as they are).

The GBC ships are the GBC map's groups of blocks that aren't space (mostly black blocks); the PC ships the original's
groups of tiles that aren't blank. Each GBC ship takes the PC ship nearest it in size and shape (its blocks' outline
against the ship's tiles', the boxes' centres on each other), pasted whole with its centre on the GBC ship's (a PC
cell a GBC block, as tools/gbc/dictionary.py lays the map), the rest blank.

    python tools/gbc/ships.py 21 [out.png]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import episode as E  # noqa: E402
import dictionary as D  # noqa: E402

SPACE_DARK = 0.85   # a GBC block this much near black is space


def groups(mask):
    """Connected groups (8 neighbours) of True cells: lists of (row, column)."""
    seen = np.zeros_like(mask, bool)
    out = []
    h, w = mask.shape
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                stack, cells = [(y, x)], []
                seen[y, x] = True
                while stack:
                    a, b = stack.pop()
                    cells.append((a, b))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            c, d = a + dy, b + dx
                            if 0 <= c < h and 0 <= d < w and mask[c, d] and not seen[c, d]:
                                seen[c, d] = True
                                stack.append((c, d))
                out.append(cells)
    return out


def pc_ships(grids, tiles):
    """The originals' ships: (rows, columns, {(dy, dx): tile}) for each group of non-blank tiles."""
    out = []
    for g in grids:
        a = np.array(g)
        mask = np.vectorize(lambda t: tiles.get(int(t)) is not None)(a)
        for cells in groups(mask):
            ys, xs = [c[0] for c in cells], [c[1] for c in cells]
            y0, x0 = min(ys), min(xs)
            if len(cells) < 2:
                continue
            out.append((max(ys) - y0 + 1, max(xs) - x0 + 1, {(y - y0, x - x0): int(a[y, x]) for y, x in cells}))
    return out


def layer(spec):
    gmap, img, grids, letter = D.setting(spec)
    tiles = E.preview.tiles(letter)
    blank = next(t for t, _ in D.originals(grids)[3].most_common() if tiles.get(t) is None)
    h, w = len(gmap), len(gmap[0])
    dark = np.array([[(img[16 * y:16 * y + 16, 16 * x:16 * x + 16].max(-1) < 40).mean() for x in range(w)] for y in range(h)])
    ships = pc_ships(grids, tiles)
    out = [[blank] * 14 for _ in range(E.ROWS)]
    top = E.ROWS - h
    taken = np.zeros((E.ROWS, 14), bool)
    placed = []
    for cells in sorted(groups(dark < SPACE_DARK), key=len, reverse=True):
        ys, xs = [c[0] for c in cells], [c[1] for c in cells]
        gh, gw = max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
        gmask = {(y - min(ys), x - min(xs)) for y, x in cells}
        cy, cx = (min(ys) + max(ys)) / 2, (min(xs) + max(xs)) / 2

        def miss(s):
            sh, sw, st = s
            oy, ox = round((gh - sh) / 2), round((gw - sw) / 2)
            mine = {(y + oy, x + ox) for y, x in st}
            return len(mine ^ gmask) + 2 * (abs(sh - gh) + abs(sw - gw))
        sh, sw, st = min(ships, key=miss)
        y0 = top + round(cy - (sh - 1) / 2)
        x0 = D.LEFT + round(cx - (sw - 1) / 2)
        x0 = min(max(x0, 0), 14 - sw)
        spots = [(y0 + dy, x0 + dx) for dy, dx in st]
        if any(not (0 <= r < E.ROWS) or taken[r, c] for r, c in spots):
            continue
        for (dy, dx), t in st.items():
            out[y0 + dy][x0 + dx] = t
            taken[y0 + dy, x0 + dx] = True
        placed.append((gh, gw, sh, sw))
    print(f"  {spec['name']}: {len(placed)} ships placed of {len(groups(dark < SPACE_DARK))} on the GBC map, "
          f"{len(ships)} in the originals")
    return out, (gmap, img, grids, letter)


if __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    out, (gmap, img, grids, letter) = layer(spec)
    D.picture(out, gmap, img, letter).save(sys.argv[2] if len(sys.argv) > 2 else f'ships_L{n:02d}.png')
