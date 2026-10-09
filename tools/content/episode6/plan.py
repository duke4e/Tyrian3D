"""Plans of episode 6's maps: the shapes a level's map is designed from (a fortress, a continent,
a river, a bridge across the screen, a field of pillars, the boss's open space), in tile
coordinates (row 0 is the map's top, the level's end; 300 rows of 14 columns), each of a
material. mapsynth.py then fills the map tile by tile, weighing each tile by how much of the
material the plan wants there it shows (the tiles' materials come from their colours,
preview.materials), so the map has the plan's shapes with the originals' tiles and edges.

Shapes are drawn in order, later ones over earlier ones; edges are roughened by noise.
"""
import math
import random

COLUMNS, ROWS = 14, 300


class Plan:
    def __init__(self, base, seed=1, roughness=0.9):
        self.base = base
        self.fixed = {}  # (row, column) -> tile: placed objects
        self.requests = []  # objects to paste after the map is made
        self.cells = [[base] * COLUMNS for _ in range(ROWS)]
        self.strict = [[False] * COLUMNS for _ in range(ROWS)]
        self.rnd = random.Random(seed)
        parts = [(self.rnd.uniform(0.5, 1.2), self.rnd.uniform(0.3, 0.9), self.rnd.uniform(0, 6.3)) for _ in range(4)]
        self.noise = lambda x, y: roughness * sum(math.sin(a * x + b * y + p) for a, b, p in parts) / len(parts)

    def _set(self, r, c, material, strict):
        if 0 <= r < ROWS and 0 <= c < COLUMNS:
            self.cells[r][c] = material
            self.strict[r][c] = strict

    def blob(self, row, col, rows, cols, material, strict=False):
        """An irregular round mass (an island, a continent): centre and radii in tiles."""
        for r in range(int(row - rows - 2), int(row + rows + 3)):
            for c in range(COLUMNS):
                d = ((r - row) / rows) ** 2 + ((c - col) / cols) ** 2
                if d < 1 + 0.6 * self.noise(c, r):
                    self._set(r, c, material, strict)
        return self

    def rect(self, r0, r1, c0, c1, material, rough=True, strict=False):
        """A rectangular mass (a fortress, a city block), edges a little rough unless rough=False."""
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                edge = min(r - r0, r1 - r, c - c0, c1 - c)
                if not rough or edge >= 1 or self.noise(c, r) > -0.3:
                    self._set(r, c, material, strict)
        return self

    def band(self, row, height, material, c0=0, c1=COLUMNS - 1, strict=True):
        """A straight band across (a bridge, a wall, a dam)."""
        for r in range(row, row + height):
            for c in range(c0, c1 + 1):
                self._set(r, c, material, strict)
        return self

    def river(self, r0, r1, width, material, centre=7.0, swing=4.0, period=24.0, strict=False):
        """A winding river (or road, canyon) from r0 to r1."""
        for r in range(r0, r1 + 1):
            x = centre + swing * math.sin(r / period * 2 * math.pi) + 1.2 * math.sin(r / 7.0)
            w = width * (1 + 0.25 * math.sin(r / 13.0))
            for c in range(COLUMNS):
                if abs(c - x) < w / 2:
                    self._set(r, c, material, strict)
        return self

    def scatter(self, r0, r1, count, size, material, cols=(1, 12), strict=False):
        """Small masses scattered (pillars, rocks, islets), size in tiles."""
        for _ in range(count):
            r = self.rnd.randint(r0, r1)
            c = self.rnd.randint(*cols)
            for dr in range(size):
                for dc in range(max(1, size - 1)):
                    self._set(r + dr, c + dc, material, strict)
        return self

    def coast(self, r0, r1, side, depth, material, strict=False):
        """Land along one side (side -1 left, 1 right), depth tiles in, wavering."""
        for r in range(r0, r1 + 1):
            d = depth + 1.5 * math.sin(r / 17.0) + self.noise(0, r) * 1.5
            for c in range(COLUMNS):
                inside = c < d if side < 0 else c >= COLUMNS - d
                if inside:
                    self._set(r, c, material, strict)
        return self

    def fill(self, r0, r1, material, strict=True):
        """Whole rows of one material (the boss's open space)."""
        for r in range(r0, r1 + 1):
            for c in range(COLUMNS):
                self._set(r, c, material, strict)
        return self

    def interior(self, margin=1):
        """Cells at least margin cells inside their shape (all neighbours that far the same)."""
        out = [[False] * COLUMNS for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLUMNS):
                m = self.cells[r][c]
                out[r][c] = all(self.cells[rr][cc] == m
                                for rr in range(max(0, r - margin), min(ROWS, r + margin + 1))
                                for cc in range(max(0, c - margin), min(COLUMNS, c + margin + 1)))
        return out

    def calm(self, r0, r1, tile, c0=0, c1=COLUMNS - 1):
        """Calm water (or plain floor): one tile only, for objects to go in (paste_objects)."""
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                self._set(r, c, f"tile:{tile}", True)
        return self

    def want_objects(self, kinds, r0, r1, count, cols=None, min_core=0):
        """Objects of these kinds to paste in rows r0-r1 (after the map is made: paste_objects);
        min_core: only big ones (landmarks), with at least that many tiles."""
        self.requests.append((set(kinds), r0, r1, count, cols, min_core))
        return self

    def paste_objects(self, grid, library, gap=1):
        """The wanted objects pasted into the made map, each where its own surroundings (the ring
        of plain tiles it had in the original) match the map's, so no seam shows: its box and a
        margin of gap all the plain tile its ring has most."""
        from collections import Counter
        placed = []
        taken = set()
        for kinds, r0, r1, count, cols, min_core in self.requests:
            pool = [o for o in library if o.kind in kinds and o.core >= min_core]
            n = 0
            for _ in range(count * 200):
                if n >= count or not pool:
                    break
                o = self.rnd.choice(pool)
                ring = Counter(t for (r, c), t in o.cells.items() if not o.is_core(r, c))
                if not ring:
                    continue
                plain = ring.most_common(1)[0][0]
                left, right = o.touches
                if left:
                    col = 0
                elif right:
                    col = COLUMNS - o.cols
                else:
                    lo, hi = cols or (0, COLUMNS - o.cols)
                    hi = min(hi, COLUMNS - o.cols)
                    if hi < lo:
                        continue
                    col = self.rnd.randint(lo, hi)
                if r1 - r0 + 1 < o.rows:
                    continue
                row = self.rnd.randint(r0, r1 - o.rows + 1)
                box = [(row + r, col + c) for r in range(-gap, o.rows + gap) for c in range(-gap, o.cols + gap)
                       if 0 <= col + c < COLUMNS]
                if any(not (0 <= r < ROWS) or grid[r][c] != plain or (r, c) in taken for r, c in box):
                    continue
                for (r, c), t in o.cells.items():
                    grid[row + r][col + c] = t
                taken.update(box)
                placed.append((o, row, col))
                n += 1
        return placed

    def bias(self, mats, floor=0.02, must=0.6):
        """mapsynth's bias for this plan: tiles weighed by their share of the wanted material.
        Inside strict shapes (not at their edges, where the originals' transition tiles go) tiles
        with less than must of the material are out; at the edges any tile may stand."""
        inside = self.interior()

        def weigh(t, x, y):
            want = self.cells[y][x]
            if want.startswith("tile:"):
                exact = t == int(want[5:])
                if inside[y][x]:
                    return 1.0 if exact else 0
                return 1.0 if exact else 0.05 + mats[t].get("water", 0.0)
            share = mats[t].get(want, 0.0)
            if self.strict[y][x] and inside[y][x] and share < must:
                return 0
            if not inside[y][x]:
                return 0.05 + share  # an edge: the transition tiles count too
            return (floor + share) ** 2
        return weigh

    def picture(self, colours):
        """The plan as an image (for checking), a colour per material."""
        from PIL import Image
        im = Image.new("RGB", (COLUMNS, ROWS))
        for r in range(ROWS):
            for c in range(COLUMNS):
                im.putpixel((c, r), colours.get(self.cells[r][c], (255, 0, 255)))
        return im.resize((COLUMNS * 6, ROWS * 6), Image.NEAREST)
