"""Episode 7's layer 1 made so that the 3D view can go on from its edge columns (src/background3d.c make_sides: the
side columns are solved from the map's own tile pairs, bound to its first and last columns; wfc.c wfc_fit_edge leaves
a row unbound where no column can stand beside the edge's run, and the solver then leaves void there, a straight cut).
The user, 2026-11-11, WARP's and BUBBLES's first platform "naglo odrezana": its lower left corner tile was there
alone in the map. Edge cells of the rows round an unbound one are turned to another of the map's tiles whose pairs
with its neighbours the map has, the change that leaves the fewest unbound rows, until none or no change helps.

    python tools/gbc/edges.py [--levels 13,12] [--dry]
"""
import argparse
import glob
import json
import os
from collections import defaultdict

LEVELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'gbc', 'episode7', 'levels')
WINDOW = 4  # (rows above and below an unbound one whose edge cells may change)


def rules(m):
    left, right, down, up = (defaultdict(set) for _ in range(4))
    for r in range(len(m)):
        for c in range(len(m[0])):
            k = m[r][c]
            if c + 1 < len(m[0]):
                right[k].add(m[r][c + 1])
                left[m[r][c + 1]].add(k)
            if r + 1 < len(m):
                down[k].add(m[r + 1][c])
                up[m[r + 1][c]].add(k)
    return left, right, down, up


def unbound(m, right_side, rl=None):
    """The rows wfc_fit_edge leaves unbound on that side."""
    left, right, down, _ = rl or rules(m)
    may, out = {k for row in m for k in row}, []
    for r, row in enumerate(m):
        e = row[-1] if right_side else row[0]
        beside = may & (right[e] if right_side else left[e])
        if beside:
            may = beside
        else:
            out.append(r)
        may = set().union(*(down[k] for k in may)) if may else set()
    return out


def fits(m, r, c, inner, side, t, rl):
    """Tile t at the edge cell (r, c): its pairs with the cell beside it and those above and below the map's."""
    left, right, down, up = rl
    if (m[r][inner] not in right[t]) if not side else (m[r][inner] not in left[t]):
        return False
    return (r == 0 or t in down[m[r - 1][c]]) and (r + 1 == len(m) or m[r + 1][c] in down[t])


def pair(m, c, inner, side, bad, rl):
    """Two edge cells of the rows round the first unbound one changed together (one alone never helps)."""
    b = bad[0]
    rows = range(max(0, b - WINDOW), min(len(m), b + WINDOW + 1))
    tiles = {k for row in m for k in row}
    best = None
    for r1 in rows:
        for t1 in tiles:
            if t1 == m[r1][c]:
                continue
            o1, m[r1][c] = m[r1][c], t1
            # (the first may break its neighbours' pairs only where the second mends them: checked once both are in)
            for r2 in rows:
                if r2 <= r1:
                    continue
                for t2 in tiles:
                    if t2 == m[r2][c]:
                        continue
                    o2, m[r2][c] = m[r2][c], t2
                    if fits(m, r1, c, inner, side, t1, rl) and fits(m, r2, c, inner, side, t2, rl):
                        n = len(unbound(m, side))
                        if n < len(bad) and (best is None or n < best[0]):
                            best = (n, (r1, t1), (r2, t2))
                    m[r2][c] = o2
            m[r1][c] = o1
    return best


def fix(m):
    changed = 0
    for side in (False, True):
        c = len(m[0]) - 1 if side else 0
        inner = c - 1 if side else 1
        for _ in range(40):
            rl = rules(m)
            bad = unbound(m, side, rl)
            if not bad:
                break
            left, right, down, up = rl
            best = None
            for r in sorted({x for b in bad for x in range(max(0, b - WINDOW), min(len(m), b + WINDOW + 1))}):
                for t in {k for row in m for k in row}:
                    if t == m[r][c]:
                        continue
                    if (m[r][inner] not in right[t]) if not side else (m[r][inner] not in left[t]):
                        continue
                    if r > 0 and t not in down[m[r - 1][c]]:
                        continue
                    if r + 1 < len(m) and m[r + 1][c] not in down[t]:
                        continue
                    old, m[r][c] = m[r][c], t
                    n = len(unbound(m, side))
                    m[r][c] = old
                    if n < len(bad) and (best is None or n < best[0]):
                        best = (n, (r, t))
            if best is None:
                best = pair(m, c, inner, side, bad, rl)
            if best is None:
                break
            for r, t in best[1:]:
                m[r][c] = t
                changed += 1
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    want = None if not a.levels else {int(x) for x in a.levels.split(',')}
    for path in sorted(glob.glob(os.path.join(LEVELS, '*.json'))):
        n = int(os.path.basename(path)[4:6])
        if want and n not in want:
            continue
        level = json.load(open(path, encoding='utf-8'))
        m = level['maps'][0]
        before = (unbound(m, False), unbound(m, True))
        if not before[0] and not before[1]:
            continue
        k = fix(m)
        after = (unbound(m, False), unbound(m, True))
        print(f"L{n:02d} {level['name']}: unbound {before} -> {after}, {k} cells changed")
        if k and not a.dry:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(level, f)


if __name__ == '__main__':
    main()
