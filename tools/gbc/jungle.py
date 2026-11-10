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
FALL_AS = {541: 512, 542: 512, 543: 512, 551: 522, 552: 522, 553: 522, 561: 532, 562: 532, 563: 532}  # (cliff without it)
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


def _pieces(st, torm, cliff, cmask, wmask, grid, h):
    """Spec jungle cliffs='pieces': each band of the map's rows with walls (3-row cliffs, the bands of walls whose rows
    meet merged, a row of margin above and below) TORM's rows that match it best, copied whole: per cell a cliff
    where the GBC has none or none where it has one costs 2, water where it has land or land where water 1 (TORM's
    waterfalls either), the same TORM rows once only where another does nearly as well. Returns the cells copied as
    cliff or water (no walkway on them)."""
    shore = set(SHORE)
    falls = set(FALLS)

    def kind(t):
        return 'f' if t in falls else 'w' if t in shore else 'c' if t in cliff else 'g'
    srcs = [[[kind(t) for t in row] for row in src] for src in torm]
    # the bands
    rows = sorted({i for i in range(h) for c in range(14) if cmask[i][c]})
    bands = []
    for i in rows:
        if bands and i <= bands[-1][1] + st.get('band_gap', 1):
            bands[-1][1] = i
        else:
            bands.append([i, i])
    used = set()
    out, band_rows = set(), set()
    for r0, r1 in bands:
        a, b = max(0, r0 - 1), min(h - 1, r1 + 1)
        H = b - a + 1
        want = [['c' if cmask[i][c] else 'w' if wmask[i][c] else 'g' for c in range(14)] for i in range(a, b + 1)]
        best = None
        for s_i, (src, kinds) in enumerate(zip(torm, srcs)):
            for y in range(len(src) - H + 1):
                cost = 0
                for j in range(H):
                    kr, wr = kinds[y + j], want[j]
                    edge = 3 if j in (0, H - 1) else 1  # (the band's first and last rows join the map round it)
                    for c in range(14):
                        k, w = kr[c], wr[c]
                        if k == w or (k == 'f' and w in 'cw'):
                            continue
                        # (a GBC wall with no cliff costs most: the walls must stay)
                        cost += (st.get('miss_cliff', 4) if w == 'c' else 1) * edge
                if not any(kinds[y + j][c] in 'cf' for j in range(H) for c in range(14)):
                    continue
                key = (s_i, y)
                score = cost + (H * 2 if key in used else 0)
                if best is None or score < best[0]:
                    best = (score, s_i, y)
        _, s_i, y = best
        used.add((s_i, y))
        for j in range(H):
            for c in range(14):
                t = torm[s_i][y + j][c]
                if t not in cliff and t not in shore and t not in falls:
                    t = GRASS  # (TORM's huts, guns and creatures left out: the level has its own)
                # (TORM's river where the GBC has land: its waterfall plain cliff, its stream grass; the river round the
                # cliffs is laid again after)
                if want[j][c] != 'w':
                    if t in falls:
                        t = FALL_AS[t]
                    elif t in shore:
                        t = GRASS
                grid[a + j][c] = t
                band_rows.add(a + j)
                if kind(t) != 'g':
                    out.add((a + j, c))
                wmask[a + j][c] = kind(t) in 'wf'
    print(f"  {len(bands)} bands of cliffs copied from TORM")
    return out, band_rows


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
    # (a road over water on land of its own, a causeway: BOTANY's level bridge is drawn over its dark floor and its
    # upright one met TORM's shores badly, the user's screenshots; spec `bridges` keeps the upright one)
    wmask = [[G[i][c] in water or (st.get('bridges') and G[i][c] in roads and wet(i, c) and sides(i, c) in ('NS', 'N', 'S'))
              for c in range(14)] for i in range(h)]
    # (water one cell wide (land on both sides) a cell wider, to the right or below: TORM's shore needs two cells for any
    # water to show, the GBC's narrow channels were lost)
    if st.get('widen', True):
        add = []
        for i in range(h):
            for c in range(14):
                if not wmask[i][c]:
                    continue
                if 0 < c < 13 and not wmask[i][c - 1] and not wmask[i][c + 1] and G[i][c + 1] not in roads:
                    add.append((i, c + 1))
                if 0 < i < h - 1 and not wmask[i - 1][c] and not wmask[i + 1][c] and G[i + 1][c] not in roads:
                    add.append((i + 1, c))
        for i, c in add:
            wmask[i][c] = True
    # (a pond of fewer than spec `pond_min` cells grass: TORM's shore round one cell is a hole in the grass)
    seen = set()
    for i in range(h):
        for c in range(14):
            if not wmask[i][c] or (i, c) in seen:
                continue
            stack, cells = [(i, c)], []
            seen.add((i, c))
            while stack:
                a, b = stack.pop()
                cells.append((a, b))
                for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if 0 <= x < h and 0 <= y < 14 and wmask[x][y] and (x, y) not in seen:
                        seen.add((x, y))
                        stack.append((x, y))
            if len(cells) < st.get('pond_min', 6):
                for a, b in cells:
                    wmask[a][b] = False
    grid = [[GRASS] * 14 for _ in range(h)]
    shore = set(SHORE)
    near = _lay(_table(torm, lambda t: t in shore or t in FALLS, lambda t: t in shore), wmask, grid)
    # the walls
    cliff = {t for src in torm for row in src for t in row if t not in shore and t not in FALLS and t != GRASS
             and t not in NOT_CLIFF and t in st.get('cliff_tiles', range(501, 537))}
    cmask = [[G[i][c] in walls for c in range(14)] for i in range(h)]
    # (TORM's cliffs are three rows, lip, face and foot, everywhere: each column's run of wall cells is made three rows
    # from its top (into the grass under it, not into water or a road), so the cliff's steps and ends are the ones TORM
    # draws; a GBC wall running down a column, which TORM has no cliff for, keeps its top three)
    rows = st.get('cliff_rows', 3)
    for c in range(14):
        i = 0
        while i < h:
            if not cmask[i][c]:
                i += 1
                continue
            j = i
            while j < h and cmask[j][c]:
                j += 1
            for k in range(i, j):
                cmask[k][c] = False
            got = []
            for k in range(i, min(h, i + rows)):
                if k >= j and (G[k][c] in water | roads or wmask[k][c]):
                    break
                got.append(k)
            # (blocked below by water or a road: the missing rows above, into grass)
            k = i - 1
            while len(got) < rows and k >= 0 and not (G[k][c] in water | roads or wmask[k][c] or cmask[k][c]):
                got.append(k)
                k -= 1
            for k in got:
                cmask[k][c] = True
            i = max(j, i + rows)
    # (spec jungle `cliffs`: 'pieces', the user's choice after the terrace edges still broke (2026-11-10): whole bands of
    # TORM's rows with their cliffs, river and waterfalls copied as they are, each where it matches the GBC's walls and
    # water best; else 'terraces', the cliffs laid by their neighbours and carried on to the map's side, kept)
    pasted = set()
    if st.get('cliffs') == 'none':
        small = 0  # (the user: no cliffs at all, they broke every way tried; the walls grass, the map else 1:1)
    elif st.get('cliffs') == 'pieces':
        small = 0
        pasted, band_rows = _pieces(st, torm, cliff, cmask, wmask, grid, h)
        # (the river outside the bands laid again round the bands' own water, so it runs on into their waterfalls)
        again = [[GRASS] * 14 for _ in range(h)]
        _lay(_table(torm, lambda t: t in shore or t in FALLS, lambda t: t in shore), wmask, again)
        for i in range(h):
            for c in range(14):
                if i not in band_rows or not (grid[i][c] in cliff or grid[i][c] in FALLS):
                    grid[i][c] = again[i][c]
    else:
        # (a wall's piece of fewer than spec `cliff_min` cells grass: TORM has no cliff that short, the user's stubs)
        seen, small = set(), 0
        for i in range(h):
            for c in range(14):
                if not cmask[i][c] or (i, c) in seen:
                    continue
                stack, cells = [(i, c)], []
                seen.add((i, c))
                while stack:
                    a, b = stack.pop()
                    cells.append((a, b))
                    for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= x < h and 0 <= y < 14 and cmask[x][y] and (x, y) not in seen:
                            seen.add((x, y))
                            stack.append((x, y))
                if len(cells) < st.get('cliff_min', 8):
                    for a, b in cells:
                        cmask[a][b] = False
                    small += len(cells)
        # (TORM's cliffs are a terrace's edge: none stops in the grass, each runs to the map's side or into the river. So
        # each cliff's ends go on sideways, its three rows at that end, to the side, water, a road or another cliff: the
        # user's cliff ends that stopped in the grass)
        if st.get('cliff_extend', True):
            def blocked(i, c):
                return G[i][c] in water | roads or wmask[i][c]
            seen = set()
            comps = []
            for i in range(h):
                for c in range(14):
                    if not cmask[i][c] or (i, c) in seen:
                        continue
                    stack, cells = [(i, c)], []
                    seen.add((i, c))
                    while stack:
                        a, b = stack.pop()
                        cells.append((a, b))
                        for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                            if 0 <= x < h and 0 <= y < 14 and cmask[x][y] and (x, y) not in seen:
                                seen.add((x, y))
                                stack.append((x, y))
                    comps.append(cells)
            for cells in comps:
                for end, step in ((min(b for _, b in cells), -1), (max(b for _, b in cells), 1)):
                    band = sorted(a for a, b in cells if b == end)
                    c = end + step
                    while 0 <= c < 14:
                        if any(cmask[a][c] for a in band):
                            break
                        if any(blocked(a, c) for a in band):
                            break
                        for a in band:
                            cmask[a][c] = True
                        c += step
            # (a cliff whose end still stops in the grass (a road in its way) grass: it can't be a terrace's edge)
            seen = set()
            for i in range(h):
                for c in range(14):
                    if not cmask[i][c] or (i, c) in seen:
                        continue
                    stack, cells = [(i, c)], []
                    seen.add((i, c))
                    while stack:
                        a, b = stack.pop()
                        cells.append((a, b))
                        for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                            if 0 <= x < h and 0 <= y < 14 and cmask[x][y] and (x, y) not in seen:
                                seen.add((x, y))
                                stack.append((x, y))
                    good = True
                    for end, step in ((min(b for _, b in cells), -1), (max(b for _, b in cells), 1)):
                        c2 = end + step
                        if 0 <= c2 < 14 and not any(G[a][c2] in water or wmask[a][c2] for a, b in cells if b == end):
                            good = False
                    if not good:
                        for a, b in cells:
                            cmask[a][b] = False
                        small += len(cells)
        near += _lay(_table(torm, lambda t: t in cliff, lambda t: True), cmask, grid)
    # (the GBC's wall turrets TORM's gun in the cliff only with spec `guns`: in the cliff it broke the cliff round it, the
    # user's screenshots; the turrets are the level's enemies anyway)
    guns = 0
    for i in range(h):
        for c in range(14):
            if st.get('guns') and G[i][c] == st['turret']:
                grid[i][c] = GUN
                if i > 0 and cmask[i - 1][c]:
                    grid[i - 1][c] = GUN_TOP
                guns += 1
    # the roads
    rmask = [[G[i][c] in roads for c in range(14)] for i in range(h)]
    caps = set()
    for i in range(h):
        for c in range(14):
            if not rmask[i][c] or (i, c) in pasted:
                continue
            # (past the map's side no road: the wide 3D view shows the side columns, a road cut off there showed)
            k = ''.join(n for n, (j, d) in zip('NSWE', ((i - 1, c), (i + 1, c), (i, c - 1), (i, c + 1)))
                        if (not 0 <= j < h and 0 <= d < 14) or (0 <= j < h and 0 <= d < 14 and rmask[j][d]))
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
            # (BOTANY caps a road's left end (584) and its lower end (574) only: a road ending going right turns down
            # into the lower cap, one ending going up turns left into the left cap, as BOTANY's own ends turn; the user:
            # the walkways going right were cut off)
            if k == 'W' and i + 1 < h and not rmask[i + 1][c] and not wmask[i + 1][c] and grid[i + 1][c] == GRASS:
                grid[i][c], grid[i + 1][c] = ROAD['SW'], ROAD['N']
                caps.add((i + 1, c))
            elif k == 'S' and c > 0 and not rmask[i][c - 1] and not wmask[i][c - 1] and grid[i][c - 1] == GRASS:
                grid[i][c], grid[i][c - 1] = ROAD['SW'], ROAD['E']
                caps.add((i, c - 1))
    print(f"  {spec['name']}: river, cliffs and walkways in layers; {near} cells laid as the nearest neighbourhood "
          f"TORM has, {small} cells of short walls grass, {guns} guns")
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
