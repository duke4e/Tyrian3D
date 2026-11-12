"""Episode 7's upper layers with their holes and notches closed: the synthesiser's pieces (episode.py upper_layers)
came out with pits enclosed by rock and narrow cuts in their walls, which the 3D view raises into straight-walled
holes (the user's playtest, 2026-11-12, TYRIAN: "gornji layer je i dalje pun neprirodnih rupa").

The layer's rock (its non-blank cells) with its enclosed pits of at most HOLE cells and its walls' cuts (blank runs of
at most SLOT cells across, rock at both ends) filled, then each cell whose rock neighbourhood changed given the tile
the layer's source draws most often with that neighbourhood (its 8 neighbours rock or not, else its 4), learnt from
the source's layer and the level's own, turn by turn among the most common few so that fills don't repeat one tile.

    python tools/gbc/fill_upper.py <level number> <layer> [--dry] [--out picture.png]
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'content'))
import episode as E  # noqa: E402

LEVELS = os.path.join(HERE, '..', '..', 'data', 'gbc', 'episode7', 'levels')
HOLE = 40
SLOT = 2   # (cells: the widest cut in a wall filled)
# (the tiles a fill may use, by level and layer: the rock's own, not its paths, plates or craters)
ALLOWED = {('TYRIAN', 3): {*range(121, 126), *range(131, 136), *range(141, 144), 151, 153}}
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
N4 = [(-1, 0), (0, -1), (0, 1), (1, 0)]


def pattern(rock, y, x, nb):
    h, w = rock.shape
    return tuple(bool(rock[y + dy, x + dx]) if 0 <= y + dy < h and 0 <= x + dx < w else True for dy, dx in nb)


def learn(grids, allowed=None):
    p8, p4 = defaultdict(Counter), defaultdict(Counter)
    for g in grids:
        rock = g > 0
        for y, x in zip(*np.nonzero(rock)):
            if allowed and g[y, x] not in allowed:
                continue
            p8[pattern(rock, y, x, N8)][g[y, x]] += 1
            p4[pattern(rock, y, x, N4)][g[y, x]] += 1
    return p8, p4


def closed(rock):
    out = rock.copy()
    h, w = rock.shape
    # (the slots: blank runs of at most SLOT cells in a row with rock at both their ends, filled where the run's cells
    # above or below are slot or rock too: the walls' narrow cuts)
    slot = np.zeros_like(rock)
    for y in range(h):
        x = 0
        while x < w:
            if rock[y, x]:
                x += 1
                continue
            x1 = x
            while x1 < w and not rock[y, x1]:
                x1 += 1
            if 0 < x and x1 < w and x1 - x <= SLOT:
                slot[y, x:x1] = True
            x = x1
    out |= slot
    lab, n = ndimage.label(~out)
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) <= HOLE and xs.min() > 0 and xs.max() < w - 1 and ys.min() > 0 and ys.max() < h - 1:
            out[ys, xs] = True
    return out


def fill(grid, source_grids, allowed=None):
    g = np.array(grid)
    rock = g > 0
    new = closed(rock)
    p8, p4 = learn([np.array(s) for s in source_grids] + [g], allowed)
    turn = Counter()
    out = g.copy()
    changed = 0
    h, w = g.shape
    for y in range(h):
        for x in range(w):
            if not new[y, x]:
                continue
            a8, b8 = pattern(rock, y, x, N8), pattern(new, y, x, N8)
            if rock[y, x] and a8 == b8:
                continue
            opts = p8.get(b8) or p4.get(pattern(new, y, x, N4)) or p8.get((True,) * 8)
            if not opts:
                continue
            top = [t for t, _ in opts.most_common(4)]
            out[y, x] = top[turn[b8] % len(top)]
            turn[b8] += 1
            changed += 1
    return out.tolist(), changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('level', type=int)
    ap.add_argument('layer', type=int)
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--out')
    a = ap.parse_args()
    path = glob.glob(os.path.join(LEVELS, f'{a.level:02d}_*.json'))[0]
    level = json.load(open(path, encoding='utf-8'))
    ep, name = level['upper']['source']
    src = [s for s in E.sources.original_levels() if (s['episode'], s['name']) == (ep, name)][0]
    k = a.layer - 1
    out, changed = fill(level['maps'][k], [src['maps'][k]], ALLOWED.get((level['name'], a.layer)))
    print(f"{level['name']}: layer {a.layer}, {changed} cells retiled")
    if a.out:
        E.preview.picture([out], level['shapes']).save(a.out)
    if not a.dry:
        level['maps'][k] = out
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(level, f)


if __name__ == '__main__':
    main()
