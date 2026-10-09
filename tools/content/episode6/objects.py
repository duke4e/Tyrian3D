"""Objects of the original maps (buildings, fortresses, rocks with docks, pillars): the groups of
tiles that stand apart from the map's base (the sea, the plain floor), each with the ring of base
tiles around it, so it fits wherever the new map has that base. Episode 6's plans place them; the
map around them is generated (mapsynth.py takes them as fixed cells).
"""
from collections import Counter

COLUMNS, ROWS = 14, 300


class MapObject:
    def __init__(self, cells, source):
        self.cells = cells  # {(row, col): tile}, rows and columns from the object's top left
        self.source = source
        self.rows = 1 + max(r for r, _ in cells)
        self.cols = 1 + max(c for _, c in cells)
        self.core = 0  # tiles that aren't base
        self.core_cells = set()

    def is_core(self, r, c):
        return (r, c) in self.core_cells

    def __repr__(self):
        return f"<object {self.rows}x{self.cols} core {self.core} from {self.source}>"


def base_tiles(grids, share=0.6):
    count = Counter(t for g in grids for row in g for t in row)
    total = sum(count.values())
    out, covered = set(), 0
    for t, n in count.most_common():
        if covered >= share * total:
            break
        out.add(t)
        covered += n
    return out


def library(levels, mats, base_material, kinds):
    """The objects of these levels, each with a kind: the material most of its core is of
    (kinds: material -> kind name), deduplicated; objects as wide as the map are left out (they are
    stretches of a level, not objects)."""
    used = {t for l in levels for row in l["maps"][0] for t in row}
    base = {t for t in used if mats[t].get(base_material, 0) >= 0.6}
    out, seen = [], set()
    for o in extract(levels, base):
        if all(o.touches):
            continue
        key = tuple(sorted(o.cells.items()))
        if key in seen:
            continue
        seen.add(key)
        share = Counter()
        for t in o.cells.values():
            if t not in base:
                for m, v in mats[t].items():
                    share[m] += v
        o.kind = kinds.get(share.most_common(1)[0][0], "other")
        out.append(o)
    return out


def extract(levels, base, min_core=4, max_rows=70, ring=1):
    """The objects of these original levels (dicts as sources.original_levels gives): groups of
    non-base tiles (8-connected) on layer 1 with their ring of tiles around them."""
    out = []
    for level in levels:
        g = level["maps"][0]
        seen = set()
        for r in range(ROWS):
            for c in range(COLUMNS):
                if (r, c) in seen or g[r][c] in base:
                    continue
                stack, group = [(r, c)], []
                seen.add((r, c))
                while stack:
                    y, x = stack.pop()
                    group.append((y, x))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < ROWS and 0 <= xx < COLUMNS and (yy, xx) not in seen and g[yy][xx] not in base:
                                seen.add((yy, xx))
                                stack.append((yy, xx))
                r0 = min(y for y, _ in group) - ring
                r1 = max(y for y, _ in group) + ring
                c0 = max(0, min(x for _, x in group) - ring)
                c1 = min(COLUMNS - 1, max(x for _, x in group) + ring)
                if len(group) < min_core or r1 - r0 + 1 > max_rows or r0 < 0 or r1 >= ROWS:
                    continue
                core = set(group)
                cells = {}
                for y in range(r0, r1 + 1):
                    for x in range(c0, c1 + 1):
                        near = any((y + dy, x + dx) in core for dy in range(-ring, ring + 1) for dx in range(-ring, ring + 1))
                        if near:
                            cells[(y - r0, x - c0)] = g[y][x]
                obj = MapObject(cells, (level["episode"], level["name"], r0, c0))
                obj.core = len(group)
                obj.core_cells = {(y - r0, x - c0) for y, x in group}
                obj.touches = (c0 == 0, c1 == COLUMNS - 1)  # it reaches the map's left / right edge
                out.append(obj)
    return out
