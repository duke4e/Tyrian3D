"""New maps from the tiles of original ones (episode 6): a tile's choice depends on its neighbours
to the left and below (and below-left and below-right), as the original maps have them, so the
new maps hold together as the originals do without copying any stretch of them.

A map is made row by row from the bottom (the end a level starts at). Each row is solved exactly
as a chain: from the right, which tiles still let the row be finished; then from the left, a
weighted choice among those. A row that leaves no valid row above it is made again (and the one
below it, if that keeps failing). A plan (bias) weighs tiles by what the level's design wants
where: e.g. water along a river's curve, land elsewhere.

Maps are lists of rows (row 0 is the top, the level's end) of shape numbers (shapesX.dat).
"""
import random
from collections import Counter, defaultdict

# A layer can use this many different tiles (JE_loadMap: the shape tables' entries it reads).
LAYER_TILES = (72, 71, 70)


class Model:
    def __init__(self, grids, max_tiles=None, keep=()):
        """Learned from source maps (one layer each); max_tiles keeps the most used tiles (and
        keep) so a map stays within a layer's limit."""
        count = Counter(t for g in grids for row in g for t in row)
        allowed = None
        if max_tiles is not None and len(count) > max_tiles:
            allowed = set(keep) | {t for t, _ in count.most_common(max_tiles - len(keep))}
        self.ctx4 = defaultdict(Counter)  # (lower-left, lower, lower-right, left) -> tile
        self.ctx3 = defaultdict(Counter)  # (lower-left, lower, left)
        self.ctx2 = defaultdict(Counter)  # (lower, left)
        self.run = Counter()              # each tile's longest vertical run in the sources
        self.count = Counter()
        self.bottom_rows = []
        for g in grids:
            h, w = len(g), len(g[0])
            ok = (lambda t: True) if allowed is None else (lambda t: t in allowed or t == -1)
            for y in range(h - 1):
                for x in range(w):
                    t, below = g[y][x], g[y + 1][x]
                    left = g[y][x - 1] if x > 0 else -1
                    ll = g[y + 1][x - 1] if x > 0 else -1
                    lr = g[y + 1][x + 1] if x + 1 < w else -1
                    if not all(ok(v) for v in (t, below, left, ll, lr)):
                        continue
                    self.ctx4[(ll, below, lr, left)][t] += 1
                    self.ctx3[(ll, below, left)][t] += 1
                    self.ctx2[(below, left)][t] += 1
                    self.count[t] += 1
            for x in range(w):
                n = 1
                for y in range(h - 2, -1, -1):
                    n = n + 1 if g[y][x] == g[y + 1][x] else 1
                    self.run[g[y][x]] = max(self.run[g[y][x]], n)
            if all(ok(t) for t in g[-1]):
                self.bottom_rows.append(list(g[-1]))

    def contexts(self, level, ll, below, lr, left):
        if level == 0:
            return self.ctx4.get((ll, below, lr, left))
        if level == 1:
            return self.ctx3.get((ll, below, left))
        return self.ctx2.get((below, left))


def _solve_row(model, rnd, below_row, runs, level, universe, bias):
    n = len(below_row)

    def candidates(x, left):
        ll = below_row[x - 1] if x > 0 else -1
        lr = below_row[x + 1] if x + 1 < n else -1
        c = model.contexts(level, ll, below_row[x], lr, left)
        if not c:
            return {}
        # No vertical runs longer than the sources have (a pillar doesn't grow into a wall).
        return {t: w for t, w in c.items() if t != below_row[x] or runs[x] < model.run[t]}

    finishable = [None] * n  # the tiles at x after which the row can be finished (None: any)
    for x in range(n - 2, -1, -1):
        finishable[x] = {t for t in universe
                         if any(finishable[x + 1] is None or u in finishable[x + 1] for u in candidates(x + 1, t))}
    row = []
    for x in range(n):
        c = candidates(x, row[x - 1] if x > 0 else -1)
        if finishable[x] is not None:
            c = {t: w for t, w in c.items() if t in finishable[x]}
        if not c:
            return None
        if bias is not None:
            c = {t: w * bias(t, x) for t, w in c.items()}
        tiles, weights = zip(*c.items())
        row.append(rnd.choices(tiles, weights)[0])
    return row


def generate(model, rows, columns, seed, bias=None, bottom=None, attempts=12):
    """A map rows x columns; bias(tile, x, y) weighs a tile's choice; bottom: the first row (else
    a source's)."""
    rnd = random.Random(seed)
    universe = list(model.count)
    grid = [None] * rows
    grid[rows - 1] = list(bottom) if bottom is not None else list(rnd.choice(model.bottom_rows))[:columns]
    runs_at = {rows - 1: [1] * columns}
    tries = Counter()
    stats = Counter()
    y = rows - 2
    steps = 0
    while y >= 0:
        steps += 1
        if steps > rows * 80:
            stats["gave up"] += 1
            for yy in range(y, -1, -1):
                grid[yy] = list(grid[yy + 1])
            break
        runs = runs_at[y + 1]
        row = None
        for level in range(2):
            row = _solve_row(model, rnd, grid[y + 1], runs, level, universe,
                             None if bias is None else (lambda t, x, y=y: bias(t, x, y)))
            if row is not None:
                break
        if row is None:
            tries[y] += 1
            stats["redone"] += 1
            y = min(rows - 2, y + 1 + tries[y] // attempts)
            continue
        stats[f"level {level}"] += 1
        grid[y] = row
        runs_at[y] = [runs[x] + 1 if row[x] == grid[y + 1][x] else 1 for x in range(columns)]
        y -= 1
    return grid, stats
