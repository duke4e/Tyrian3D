"""Episode 7's jungles (JUNGLE, JUNGLE II): layer 1 1:1 after the GBC map in layers, each from the PC original that draws
that kind of thing, as the user asked after the dictionary, the corners and the quilt failed on this tile set ("očito ne
postoji 1:1 mapiranje", "trebali bi neki pristup koji do sad nismo imali"):

    water   the GBC's water blocks (and its roads over water) TORM's river: each cell the shore or water tile TORM has
            most where its own 8 neighbours are water and land alike (remake.exact()'s way), the rest TORM's grass
    walls   the GBC's grey walls TORM's cliffs the same way (cliff cells by TORM's), its turrets TORM's gun in the cliff
    roads   the GBC's road blocks BOTANY's walkway: each cell the walkway piece for the sides it joins other road cells
            on, a bridge over water

    python tools/gbc/jungle.py 4 [out.png]
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import episode as E  # noqa: E402
import dictionary as D  # noqa: E402
from remake import _around  # noqa: E402

GRASS = 502
SHORE = (544, 545, 546, 547, 548, 554, 555, 556, 557, 558, 564, 565, 566)
FALLS = (541, 542, 543, 551, 552, 553, 561, 562, 563)
# (BOTANY's walkway on land by the sides it joins on; a lone end its cap)
ROAD = {'NS': 575, 'N': 574, 'S': 575, 'WE': 585, 'E': 584, 'W': 585, 'SE': 571, 'SW': 573, 'NE': 591, 'NW': 593,
        'SWE': 572, 'NSE': 581, 'NSW': 583, 'NWE': 592, 'NSWE': 582, '': 582}
BRIDGE_NS, BRIDGE_TOP, BRIDGE_BOTTOM, BRIDGE_WE = 595, 596, 597, 594
GUN_TOP, GUN = 576, 586
NOT_CLIFF = {504, 527, 528, 537, 538, 539, 540, 549, 550, 559, 560, 567, 568, 569, 570, 576, 586}


def _source(name):
    return [l for l in E.sources.original_levels() if (l['episode'], l['name']) == name][0]['maps'][0]


def _table(srcs, member, count):
    """{8-neighbour pattern: Counter of tiles} over the sources, the mask `member`, only tiles `count` counted."""
    table = {}
    for src in srcs:
        m = [[member(t) for t in row] for row in src]
        for y, row in enumerate(src):
            for x, t in enumerate(row):
                if m[y][x] and count(t):
                    table.setdefault(_around(m, y, x), Counter())[t] += 1
    return table


WEIGHT = [2 if i in (1, 3, 4, 6) else 1 for i in range(8)]


def _lay(table, mask, grid):
    near = 0
    for i, row in enumerate(mask):
        for c, on in enumerate(row):
            if not on:
                continue
            k = _around(mask, i, c)
            if k not in table:
                near += 1
                k = min(table, key=lambda q: (sum(wt for a, b, wt in zip(k, q, WEIGHT) if a != b), -sum(table[q].values())))
            grid[i][c] = table[k].most_common(1)[0][0]
    return near


def layer(spec):
    st = spec['jungle']
    gmap, img, grids, letter = D.setting(spec)
    h, w = len(gmap), len(gmap[0])
    col = [min(max(c - D.LEFT, 0), w - 1) for c in range(14)]
    G = [[gmap[i][col[c]] for c in range(14)] for i in range(h)]
    water, walls, roads = set(st['water']), set(st['walls']) | {st['turret']}, set(st['roads'])
    torm = [_source(tuple(m)) for m in st.get('river', [(2, 'TORM')])]

    def wet(i, c):
        """A road cell over water: more water than land among its sides that aren't road."""
        n = [G[j][d] for j, d in ((i - 1, c), (i + 1, c), (i, c - 1), (i, c + 1)) if 0 <= j < h and 0 <= d < 14]
        n = [b for b in n if b not in roads]
        return sum(b in water for b in n) > len(n) / 2
    def sides(i, c):
        return ''.join(n for n, (j, d) in zip('NSWE', ((i - 1, c), (i + 1, c), (i, c - 1), (i, c + 1)))
                       if not (0 <= j < h and 0 <= d < 14) or G[j][d] in roads)
    # (BOTANY bridges only straight: a road's turn or junction over water stands on a small island of its own)
    wmask = [[G[i][c] in water or (G[i][c] in roads and wet(i, c) and sides(i, c) in ('NS', 'N', 'S', 'WE', 'W', 'E'))
              for c in range(14)] for i in range(h)]
    grid = [[GRASS] * 14 for _ in range(h)]
    shore = set(SHORE)
    near = _lay(_table(torm, lambda t: t in shore or t in FALLS, lambda t: t in shore), wmask, grid)
    # the walls
    cliff = {t for src in torm for row in src for t in row if t not in shore and t not in FALLS and t != GRASS
             and t not in NOT_CLIFF and t in st.get('cliff_tiles', range(501, 537))}
    cmask = [[G[i][c] in walls for c in range(14)] for i in range(h)]
    # (TORM's cliffs are three rows, lip, face and foot, the GBC's walls two, top and face: the grass under a wall the
    # foot, where the lip stood straight on the foot)
    for i in range(h - 2, -1, -1):
        for c in range(14):
            if G[i][c] in walls and G[i + 1][c] not in walls | water | roads and not wmask[i + 1][c]:
                cmask[i + 1][c] = True
    near += _lay(_table(torm, lambda t: t in cliff, lambda t: True), cmask, grid)
    guns = 0
    for i in range(h):
        for c in range(14):
            if G[i][c] == st['turret']:
                grid[i][c] = GUN
                if i > 0 and cmask[i - 1][c]:
                    grid[i - 1][c] = GUN_TOP
                guns += 1
    # the roads
    rmask = [[G[i][c] in roads for c in range(14)] for i in range(h)]
    for i in range(h):
        for c in range(14):
            if not rmask[i][c]:
                continue
            k = ''.join(n for n, (j, d) in zip('NSWE', ((i - 1, c), (i + 1, c), (i, c - 1), (i, c + 1)))
                        if not (0 <= j < h and 0 <= d < 14) or rmask[j][d])
            if wmask[i][c]:
                t = BRIDGE_WE if k in ('WE', 'W', 'E') else BRIDGE_NS
                if t == BRIDGE_NS:
                    if i > 0 and rmask[i - 1][c] and not wmask[i - 1][c]:
                        t = BRIDGE_TOP
                    elif i + 1 < h and rmask[i + 1][c] and not wmask[i + 1][c]:
                        t = BRIDGE_BOTTOM
            else:
                t = ROAD[k]
            grid[i][c] = t
    print(f"  {spec['name']}: river, cliffs and walkways in layers; {near} cells laid as the nearest neighbourhood "
          f"TORM has, {guns} guns")
    out = []
    for r in range(E.ROWS):
        b = E.ROWS - 1 - r
        if b >= h:
            b = h - 8 + (b - h) % 8
        out.append(list(grid[h - 1 - b]))
    return out


if __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    out = layer(spec)
    gmap, img, grids, letter = D.setting(spec)
    D.picture(out, gmap, img, letter).save(sys.argv[2] if len(sys.argv) > 2 else f'jungle_L{n:02d}.png')
