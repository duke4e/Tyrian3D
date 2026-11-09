"""Episode 7's layer 1, 1:1 after the GBC map (a PC cell a GBC block), by the method the level's spec names (`remake`),
as the user's map reviews chose per level (2026-11-07/08):

    autotile    episode.autotile aligned (the committed maps' way: CAMANIS, ICE EXIT, the SAVARAs looked best so)
    corners     corners.py (materials at the blocks' corners, the originals' transition tiles; templates, block_like)
    ships       ships.py (FLEET: the original's ships whole where the GBC map has ships)
    fitted      dictionary.fitted (BUBBLES, WARP: the dictionary's tiles, given up where they wouldn't join)
    dictionary  dictionary.lay (the dictionary as it is: AST.BONUS, LAVA II)
    ninepatch   framed rectangles (DELI CORE's earlier variant)
    exact       the tile set's pad tiles as its original lays them, by each cell's 8 neighbours (DELI CORE)
    jungle      jungle.py: river, cliffs and walkways in layers, each from its PC original (the jungles)

    python tools/gbc/remake.py 23 [out.png]
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import episode as E  # noqa: E402
import dictionary as D  # noqa: E402


def layer(spec):
    """(layer 1: ROWS x 14 tiles, GBC map, its picture, the tile set's letter)."""
    how = spec.get('remake', 'dictionary')
    gmap, img, grids, letter = D.setting(spec)
    if how == 'autotile':
        out, h = E.autotile(dict(spec, aligned=True), img, grids, letter)
        # (spec `own_sides`, with `edges`: the side columns the autotile's own, its plan the nearest column's: ASTEROID's
        # plates go on to the sides, where the side solver left them space, the user: "s lijeve strane nam nedostaju
        # tileovi")
        if not spec.get('own_sides'):
            inside = Counter(t for row in out[E.ROWS - h:] for t in row[D.LEFT:D.LEFT + len(gmap[0])])
            every = [l['maps'][0] for l in E.sources.original_levels() if l['shapes'] == letter]
            out = D.sides(spec, out, letter, grids + every, allowed=inside)
    elif how == 'corners':
        import corners
        out = corners.layer(spec)
    elif how == 'ninepatch':
        out = ninepatch(spec, gmap)
    elif how == 'exact':
        out = exact(spec, gmap)
    elif how == 'jungle':
        import jungle
        out = jungle.layer(spec)
    elif how == 'ships':
        import ships
        out, _ = ships.layer(spec)
    elif how in ('fitted', 'dictionary'):
        dic = {int(b): t for b, t in D.picks()[str(spec['gbc'])].items()}
        out = D.fitted(spec, dic, gmap, grids, letter) if how == 'fitted' else D.layer(spec, dic, gmap, grids, letter)
    else:
        raise SystemExit(f"{spec['name']}: no remake method {how!r}")
    # (spec `ornaments`: [(tile, [(variant, weight), ...], share)]: that share of the tile's cells on the GBC map's columns
    # one of its variants, tiles of the same edges with something on them, as its original has them: DELIANI's plates
    # their hatches and turrets, its floor its lights; the user: "mapa izgleda jako golo"; never two side by side)
    if spec.get('ornaments'):
        import random
        rnd = random.Random(spec.get('seed', 1))
        h, w = len(gmap), len(gmap[0])
        orn = set()
        for r in range(E.ROWS - h, E.ROWS):
            for c in range(D.LEFT, D.LEFT + w):
                for tile, variants, share in spec['ornaments']:
                    if out[r][c] != tile or rnd.random() >= share:
                        continue
                    if any((r + dr, c + dc) in orn for dr in (-1, 0, 1) for dc in (-1, 0, 1)):
                        continue
                    out[r][c] = rnd.choices([v for v, _ in variants], [k for _, k in variants])[0]
                    orn.add((r, c))
        # (the loop rows above the map follow its top rows)
        for r in range(E.ROWS - h):
            b = E.ROWS - 1 - r
            out[r] = list(out[E.ROWS - h + 7 - (b - h) % 8])  # (dictionary.lay's loop: the map's top 8 rows)
    # (spec `stamps`: dict(source=(episode, level), floor=[tiles], share=..., max=(rows, columns)): the source's small
    # pieces standing alone on its floor (its tiles' groups, none of the floor, that fit the size, floor all round),
    # put on the map's own floor where it has room for one and its margin, about as many per floor cell as the source
    # has: DELIANI's small plates with their turrets and hatches on its bare floor)
    if spec.get('stamps'):
        import random
        st = spec['stamps']
        rnd = random.Random(spec.get('seed', 1) + 7)
        src = [l for l in E.sources.original_levels() if (l['episode'], l['name']) == tuple(st['source'])][0]['maps'][0]
        floor = set(st['floor'])
        mh, mw = st.get('max', (3, 3))
        sh_, sw_ = len(src), len(src[0])
        seen, pieces = set(), []
        for y in range(sh_):
            for x in range(sw_):
                if src[y][x] in floor or (y, x) in seen:
                    continue
                stack, cells = [(y, x)], []
                seen.add((y, x))
                while stack:
                    a, b = stack.pop()
                    cells.append((a, b))
                    for c2, d2 in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= c2 < sh_ and 0 <= d2 < sw_ and (c2, d2) not in seen and src[c2][d2] not in floor:
                            seen.add((c2, d2))
                            stack.append((c2, d2))
                ys, xs = [c_[0] for c_ in cells], [c_[1] for c_ in cells]
                y0, x0, ph, pw = min(ys), min(xs), max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
                if ph > mh or pw > mw or y0 == 0 or x0 == 0 or y0 + ph >= sh_ or x0 + pw >= sw_:
                    continue
                pieces.append([[src[y0 + j][x0 + i] for i in range(pw)] for j in range(ph)])
        floor_cells = sum(t in floor for row in src for t in row)
        per_cell = len(pieces) / max(1, floor_cells) * st.get('share', 1.0)
        h, w = len(gmap), len(gmap[0])
        spots = [(r, c) for r in range(E.ROWS - h + 1, E.ROWS - 1) for c in range(D.LEFT, D.LEFT + w)]
        rnd.shuffle(spots)
        want = round(per_cell * sum(out[r][c] in floor for r, c in spots))
        placed = 0
        for r, c in spots:
            if placed >= want or not pieces:
                break
            pc_ = rnd.choice(pieces)
            ph, pw = len(pc_), len(pc_[0])
            if r - 1 < E.ROWS - h or r + ph >= E.ROWS or c - 1 < D.LEFT or c + pw > D.LEFT + w:
                continue
            if all(out[r + j][c + i] in floor for j in range(-1, ph + 1) for i in range(-1, pw + 1)):
                for j in range(ph):
                    for i in range(pw):
                        out[r + j][c + i] = pc_[j][i]
                placed += 1
        print(f"  {spec['name']}: {placed} of {len(pieces)} kinds of small pieces from {st['source'][1]} put on its floor")
        for r in range(E.ROWS - h):
            b = E.ROWS - 1 - r
            out[r] = list(out[E.ROWS - h + 7 - (b - h) % 8])
    if spec.get('paths'):
        out = paths(spec, out, gmap, img, letter)
    # (spec `replace`: {tile: tile} after the making: ASTEROID's red bars, the turrets the GBC map draws (leaving them out of
    # the autotile changed its materials and lost the paths))
    for a, b in spec.get('replace', {}).items():
        out = [[b if t == a else t for t in row] for row in out]
    # (spec `pins`: {block: tile}: those GBC blocks that tile where they are, last: ASTEROID's red turret blocks its red
    # turret tile, which elsewhere stood in rows as red bars)
    if spec.get('pins'):
        h, w = len(gmap), len(gmap[0])
        for i, row in enumerate(gmap):
            for g, b in enumerate(row):
                if b in spec['pins']:
                    out[E.ROWS - h + i][g + D.LEFT] = spec['pins'][b]
        for r in range(E.ROWS - h):
            b_ = E.ROWS - 1 - r
            out[r] = list(out[E.ROWS - h + 7 - (b_ - h) % 8])
    if spec.get('mend'):
        out = mend(spec, out, gmap, letter)
    # (spec `relay`: dict(replace=[tiles], family=[tiles], source=[(episode, level), ...]): the cells of those tiles laid
    # again with the family's tiles as the sources lay them by each cell's 8 neighbours (exact()'s way): TYRIAN's black
    # pits (GAUNTLET's holes) NOSE DRIP's raised ridges in the dark rubble round them, the user: "ove crne rupe trebamo
    # pretvoriti u nešto zanimljivije", whatever joins its neighbours)
    if spec.get('relay'):
        out = relay(spec, out)
    # (spec `bottom_row`: the map's first row that tile all along: SAVARA II's starts in open water, not on the stray
    # dock edges its GBC map's frame made)
    if spec.get('bottom_row') is not None:
        out[E.ROWS - 1] = [spec['bottom_row']] * 14
    return out, gmap, img, letter


def ninepatch(spec, gmap):
    """Spec `ninepatch`: dict(blocks=[...], patch=(tl, t, tr, l, c, r, bl, b, br), fill=tile): the GBC map's cells of
    those blocks covered by rectangles of at least 2 x 2 (the largest first), each drawn as the tile set's framed pad
    (its corners, edges and middle), the rest the fill: UNDERDELI draws its blue mesh only as such framed rectangles,
    which the corner tiling put together in shapes it has no tiles for (the user on DELI CORE: "mnogo nelogičnosti");
    thinner strips of those blocks become fill."""
    st = spec['ninepatch']
    tl, t_, tr, l_, c_, r_, bl, b_, br = st['patch']
    blocks = set(st['blocks'])
    h, w = len(gmap), len(gmap[0])
    mask = [[gmap[i][min(max(c - D.LEFT, 0), w - 1)] in blocks for c in range(14)] for i in range(h)]
    free = [row[:] for row in mask]
    grid = [[st['fill']] * 14 for _ in range(h)]
    rects = 0
    while True:
        best = None
        heights = [0] * 14
        for i in range(h):
            heights = [heights[c] + 1 if free[i][c] else 0 for c in range(14)]
            for c0 in range(14):
                mh = 10 ** 9
                for c1 in range(c0, 14):
                    mh = min(mh, heights[c1])
                    if mh < 2:
                        break
                    if c1 - c0 + 1 >= 2 and (best is None or mh * (c1 - c0 + 1) > best[0]):
                        best = (mh * (c1 - c0 + 1), i - mh + 1, i, c0, c1)
        if best is None:
            break
        _, i0, i1, c0, c1 = best
        for i in range(i0, i1 + 1):
            for c in range(c0, c1 + 1):
                free[i][c] = False
                top, bot, lef, rig = i == i0, i == i1, c == c0, c == c1
                grid[i][c] = (tl if lef else tr if rig else t_) if top else (bl if lef else br if rig else b_) if bot else                     (l_ if lef else r_ if rig else c_)
        rects += 1
    print(f"  {spec['name']}: {rects} framed rectangles, {sum(map(sum, free))} cells too thin for one left as fill")
    out = []
    for r in range(E.ROWS):
        b = E.ROWS - 1 - r
        if b >= h:
            b = h - 8 + (b - h) % 8
        out.append(list(grid[h - 1 - b]))
    return out


def _around(mask, r, c):
    """The 8 neighbours of a cell (row by row, the cell left out): 1 where the mask is set; outside the columns 1 (the
    pads go on past the map's side), outside the rows 0."""
    h, w = len(mask), len(mask[0])
    return tuple(1 if not 0 <= c + dc < w or (0 <= r + dr < h and mask[r + dr][c + dc]) else 0
                 for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0))


SIDES = ((1, 'N'), (6, 'S'), (3, 'W'), (4, 'E'))  # (_around's index of each side)


def exact(spec, gmap):
    """Spec `exact`: dict(blocks=[...], family=[...], sides={tile: 'NSWE'}, fill=tile, objects={block: tile},
    runs={blocks: (tiles on the left half, on the right half)}): the GBC map's cells of those
    blocks drawn with the tile set's pad tiles (the family) exactly as its original uses them: each cell the tile the
    original has most often where its own 8 neighbours are pad and floor alike (the nearest such neighbourhood when the
    original has none), the rest the fill. The user on DELI CORE chose this over the framed rectangles and the solver
    (2026-11-09: "ovaj sa 175 loših izgleda najbolje"), but: where the most common tile breaks a seam (one tile of a pair
    ends the pad at their seam, the other goes on: the bottom-left corners that stood as spikes in bottom edges) another
    tile the original has there (spec `keep`: at least that share of the most common one's count); and the GBC's turrets (spec `objects`, blocks out of the pads) are the
    tile set's own turrets on the floor (UNDERDELI's dome, its crab machine three wide for a run of four, floor on its
    outer side (the user: no dome beside the crab), its 2 x 2 machine), not the small islands they made."""
    st = spec['exact']
    fam, fill = set(st['family']), st['fill']
    objects = st.get('objects', {})
    blocks = set(st['blocks']) - set(objects)
    src = [l for l in E.sources.original_levels() if (l['episode'], l['name']) == tuple(spec['tiles'])][0]['maps'][0]
    smask = [[t in fam for t in row] for row in src]
    table = {}
    for y, row in enumerate(src):
        for x, t in enumerate(row):
            if smask[y][x]:
                table.setdefault(_around(smask, y, x), Counter())[t] += 1
    h, w = len(gmap), len(gmap[0])
    col = [min(max(c - D.LEFT, 0), w - 1) for c in range(14)]
    mask = [[gmap[i][col[c]] in blocks for c in range(14)] for i in range(h)]
    weight = [2 if i in (1, 3, 4, 6) else 1 for i in range(8)]
    grid = [[fill] * 14 for _ in range(h)]
    cands = {}
    near = 0
    for i in range(h):
        for c in range(14):
            if not mask[i][c]:
                continue
            k = _around(mask, i, c)
            # (spec `edges`: {floor sides: tile}: a neighbourhood the original has under `rare` times (or never), its floor
            # sides' edge or corner, the pit round a turret's sides: the original's one or two odd cells put corners
            # there)
            sides = ''.join(n for j, n in SIDES if not k[j])
            rare = sum(table.get(k, {}).values()) < st.get('rare', 3)
            if rare and sides in st.get('edges', {}):
                cands[i, c] = [(st['edges'][sides], 1)]
                grid[i][c] = st['edges'][sides]
                continue
            if k not in table:
                near += 1
                k = min(table, key=lambda q: (sum(wt for a, b, wt in zip(k, q, weight) if a != b), -sum(table[q].values())))
            top = table[k].most_common(1)[0][1]
            cands[i, c] = [(t, n) for t, n in table[k].most_common() if n >= top * st.get('keep', .25)]
            # (spec `inner`: {diagonal (_around's index): tile}: a cell of pad all round but for that one diagonal, the
            # pad's inner corner, that junction tile, where the original as often puts an edge's bar: the bar stood in
            # the pad as a spike beside the corner tiles that close the step)
            floor = [j for j in range(8) if not k[j]]
            if len(floor) == 1 and floor[0] in st.get('inner', {}):
                cands[i, c] = [(st['inner'][floor[0]], top)]
            grid[i][c] = cands[i, c][0][0]
    # (seams: two pad tiles side by side either both go on across their seam or both end there (the pad's sides, st
    # `sides`: {tile: 'NSWE' sides it ends at}); where the most common tile breaks that, the cell's other likely tiles:
    # the user's "šiljci" right of the corners, a bottom-left corner in a bottom edge where the pad on the left went
    # lower)
    ends = {int(t): set(v) for t, v in st['sides'].items()}

    def seams(i, c, t):
        bad = 0
        for di, dc, mine, theirs in ((0, -1, 'W', 'E'), (0, 1, 'E', 'W'), (-1, 0, 'N', 'S'), (1, 0, 'S', 'N')):
            j, d = i + di, c + dc
            if not (0 <= j < h and 0 <= d < 14 and mask[j][d]):
                continue
            o = grid[j][d]
            if t in ends and o in ends and (mine in ends[t]) != (theirs in ends[o]):
                bad += 1
        return bad
    fixed = set()
    for _ in range(6):
        changed = 0
        for (i, c), cs in cands.items():
            best = min(cs, key=lambda tn: (seams(i, c, tn[0]), -tn[1]))[0]
            if best != grid[i][c]:
                grid[i][c] = best
                fixed.add((i, c))
                changed += 1
        if not changed:
            break
    broken = sum(seams(i, c, grid[i][c]) for i, c in cands) // 2
    fixed = len(fixed)
    # (the turrets: on the GBC map's columns; a run of the 4-wide one the crab and floor, the floor on the side nearer
    # the map's edge)
    placed = 0
    for i in range(h):
        for g in range(w):
            b = gmap[i][g]
            if b not in objects:
                continue
            grid[i][g + D.LEFT] = objects[b]
            placed += 1
    for run, (left, right) in st.get('runs', {}).items():
        n = len(run)
        for i in range(h):
            for g in range(w - n + 1):
                if tuple(gmap[i][g:g + n]) == tuple(run):
                    tiles = left if g + n / 2 <= w / 2 else right
                    for j, t in enumerate(tiles):
                        grid[i][g + D.LEFT + j] = t
    print(f"  {spec['name']}: {near} cells laid as the nearest neighbourhood the original has, {fixed} turned to their "
          f"seams' tile, {broken} seams left broken, {placed} turret cells")
    out = []
    for r in range(E.ROWS):
        b = E.ROWS - 1 - r
        if b >= h:
            b = h - 8 + (b - h) % 8
        out.append(list(grid[h - 1 - b]))
    return out


def relay(spec, out):
    st = spec['relay']
    fam, rep = set(st['family']), set(st['replace'])
    table = {}
    for l in E.sources.original_levels():
        if (l['episode'], l['name']) not in {tuple(m) for m in st['source']}:
            continue
        src = l['maps'][0]
        smask = [[t in fam for t in row] for row in src]
        for y, row in enumerate(src):
            for x, t in enumerate(row):
                if smask[y][x]:
                    table.setdefault(_around(smask, y, x), Counter())[t] += 1
    mask = [[t in rep for t in row] for row in out]
    weight = [2 if i in (1, 3, 4, 6) else 1 for i in range(8)]
    new = [row[:] for row in out]
    near = 0
    for i, row in enumerate(out):
        for c, t in enumerate(row):
            if not mask[i][c]:
                continue
            k = _around(mask, i, c)
            if k not in table:
                near += 1
                k = min(table, key=lambda q: (sum(wt for a, b, wt in zip(k, q, weight) if a != b), -sum(table[q].values())))
            new[i][c] = table[k].most_common(1)[0][0]
    print(f"  {spec['name']}: {sum(map(sum, mask))} cells laid again as {st['source'][0][1]}'s, {near} as the nearest "
          f"neighbourhood it has")
    return new


def mend(spec, out, gmap, letter, sweeps=6):
    """Spec `mend`: the last pairs no original of the tile set makes (beside or above), each of their cells, but those
    of spec mend_lock's tiles (paths, turrets), the tile with the fewest such pairs round it, then the most like the one
    it had (4 x 4 region means): ASTEROID's rock caps under plain plate, a dark notch in it (the user's screenshots)."""
    import numpy as np
    every = [l['maps'][0] for l in E.sources.original_levels() if l['shapes'] == letter]
    right, above, _, use = D.originals(every)
    tiles = E.preview.tiles(letter)
    pal = E.preview.palette()
    lock = set(spec.get('mend_lock', ()))
    # (the tiles the map has already, none locked and none of the tile set's objects: a turret pair stood in for a rim)
    ids = sorted({t for row in out for t in row} - lock - set(E.object_tiles(letter)))
    # (spec `mend_pool`: [(episode, level)], their tiles too, but spec `mend_skip`'s: the jungles' cliffs may take any of
    # TORM's cliff and shore pieces, the map's own being too few to close a cliff's end)
    if spec.get('mend_pool'):
        names = {tuple(m) for m in spec['mend_pool']}
        more = {t for l in E.sources.original_levels() if (l['episode'], l['name']) in names for row in l['maps'][0] for t in row}
        ids = sorted(set(ids) | (more - lock - set(spec.get('mend_skip', ())) - set(E.object_tiles(letter))))
    look = {t: E.regions(E.lab(np.zeros((28, 24, 3)) if tiles.get(t) is None else pal[tiles[t]].astype(np.float64)), 4)
            for t in set(ids) | {t for row in out for t in row}}
    h = len(gmap)
    top = E.ROWS - h
    seen_h = lambda a, b: b in right.get(a, ())
    seen_v = lambda below, abv: abv in above.get(below, ())

    def bad(r, c, t):
        n = 0
        if c > 0 and not seen_h(out[r][c - 1], t):
            n += 1
        if c < 13 and not seen_h(t, out[r][c + 1]):
            n += 1
        if r + 1 < E.ROWS and not seen_v(out[r + 1][c], t):
            n += 1
        if r > top and not seen_v(t, out[r - 1][c]):
            n += 1
        return n
    changed = 0
    for _ in range(sweeps):
        moved = 0
        for r in range(top, E.ROWS):
            for c in range(14):
                cur = out[r][c]
                if cur in lock or bad(r, c, cur) == 0:
                    continue
                base = look[cur]
                best = min(ids, key=lambda t: (bad(r, c, t), float(np.sqrt(((look[t] - base) ** 2).sum(-1)).mean())))
                if bad(r, c, best) < bad(r, c, cur):
                    out[r][c] = best
                    moved += 1
        changed += moved
        if not moved:
            break
    # (then a 3 x 3 window of free cells round each pair left, solved whole: depth first, each cell among the 30 tiles
    # most like its own, every pair inside and across the border one the originals make)
    for r0 in range(top, E.ROWS):
        for c0 in range(14):
            if out[r0][c0] in lock or bad(r0, c0, out[r0][c0]) == 0:
                continue
            cells = [(r, c) for r in range(max(top, r0 - 1), min(E.ROWS, r0 + 2)) for c in range(max(0, c0 - 1), min(14, c0 + 2))
                     if out[r][c] not in lock]
            keep = {k: out[k[0]][k[1]] for k in cells}
            cand = {k: sorted(ids, key=lambda t: float(np.sqrt(((look[t] - look[keep[k]]) ** 2).sum(-1)).mean()))[:spec.get('mend_cands', 30)]
                    for k in cells}
            best, nodes = [None, None], [0]

            def ok(r, c):
                t = out[r][c]
                for rr, cc in ((r, c - 1), (r - 1, c)):
                    if (rr, cc) in keep and cells.index((rr, cc)) > cells.index((r, c)):
                        continue
                    if cc == c - 1 and cc >= 0 and not seen_h(out[rr][cc], t):
                        return False
                    if rr == r - 1 and rr >= top and not seen_v(t, out[rr][cc]):
                        return False
                for rr, cc in ((r, c + 1), (r + 1, c)):
                    if (rr, cc) in keep:
                        continue
                    if cc == c + 1 and cc < 14 and not seen_h(t, out[rr][cc]):
                        return False
                    if rr == r + 1 and rr < E.ROWS and not seen_v(out[rr][cc], t):
                        return False
                return True

            def dfs(i, cost):
                nodes[0] += 1
                if nodes[0] > 60000 or (best[0] is not None and cost >= best[0]):
                    return
                if i == len(cells):
                    best[0], best[1] = cost, {k: out[k[0]][k[1]] for k in cells}
                    return
                r, c = cells[i]
                for j, t in enumerate(cand[(r, c)]):
                    out[r][c] = t
                    if ok(r, c):
                        dfs(i + 1, cost + j)
                out[r][c] = keep[(r, c)]
            dfs(0, 0)
            for k, t in (best[1] or keep).items():
                out[k[0]][k[1]] = t
            if best[1]:
                changed += sum(best[1][k] != keep[k] for k in cells)
    left = sum(bad(r, c, out[r][c]) for r in range(top, E.ROWS) for c in range(14)) // 2
    print(f"  {spec['name']}: {changed} cells mended, {left} odd pairs left (at locked tiles: paths meeting rims)")
    for r in range(top):
        b_ = E.ROWS - 1 - r
        out[r] = list(out[top + 7 - (b_ - h) % 8])
    return out


def _brown(a):
    return (a[..., 0] - a[..., 2] > 25) & (a[..., 0] >= a[..., 1])


def exits(a, band=0.2):
    """A picture's path exits (N, E, S, W): brown in the middle half of each edge's band."""
    h, w = a.shape[:2]
    br = _brown(a.astype(int))
    k = max(1, int(round(h * band)))
    mid, midr = slice(w // 4, w - w // 4), slice(h // 4, h - h // 4)
    return (bool(br[:k, mid].mean() > 0.15), bool(br[midr, -k:].mean() > 0.15), bool(br[-k:, mid].mean() > 0.15),
            bool(br[midr, :k].mean() > 0.15))


def paths(spec, out, gmap, img, letter):
    """Spec `paths`: dict(blocks=[...], plain=tile, tiles=(first, last)): each GBC path block the PC path tile with the
    same exits (the brown path's ends on its edges, read off both pictures; of several the one the originals use most),
    any path tile elsewhere the plain plate, and a path that leaves the GBC map's side going on to the playfield's edge:
    ASTEROID's paths joined as the GBC map draws them (the user: "ima ih koji si ne pašu, rubnih koji naglo
    završavaju")."""
    import numpy as np
    from collections import Counter
    st = spec['paths']
    tiles = E.preview.tiles(letter)
    pal = E.preview.palette()
    use = Counter(t for l in E.sources.original_levels() if l['shapes'] == letter for row in l['maps'][0] for t in row)
    lo, hi = st.get('tiles', (340, 430))
    by = {}
    for t in range(lo, hi):
        if tiles.get(t) is None or not use[t]:
            continue
        a = pal[tiles[t]]
        share = _brown(a.astype(int)).mean()
        e = exits(a)
        if any(e) and 0.12 <= share <= 0.36 and (e not in by or use[t] > use[by[e]]):
            by[e] = t
    path_tiles = set(by.values())
    blocks = set(st['blocks'])
    h, w = len(gmap), len(gmap[0])
    pos = {}
    for y, row in enumerate(gmap):
        for x, b in enumerate(row):
            pos.setdefault(b, (y, x))
    block_exits = {b: exits(img[16 * y:16 * y + 16, 16 * x:16 * x + 16]) for b, (y, x) in pos.items() if b in blocks}
    out = [list(r) for r in out]
    for i, row in enumerate(gmap):
        r = E.ROWS - h + i
        for g, b in enumerate(row):
            c = g + D.LEFT
            if b in blocks:
                e = block_exits[b]
                out[r][c] = by.get(e, st['plain']) if any(e) else st['plain']
            elif out[r][c] in path_tiles:
                out[r][c] = st['plain']
        for c in list(range(D.LEFT)) + list(range(D.LEFT + w, 14)):
            if out[r][c] in path_tiles:
                out[r][c] = st['plain']  # (none in the side columns but those going on from the map)
        # (beyond the sides: a path leaving the map's edge goes on, straight, to the playfield's)
        we, ew = by.get((False, True, False, True)), out[r]
        if row[w - 1] in blocks and block_exits[row[w - 1]][1]:
            for c in range(D.LEFT + w, 14):
                out[r][c] = we
        if row[0] in blocks and block_exits[row[0]][3]:
            for c in range(0, D.LEFT):
                out[r][c] = we
    for r in range(E.ROWS - h):
        b_ = E.ROWS - 1 - r
        out[r] = list(out[E.ROWS - h + 7 - (b_ - h) % 8])
    return out


def components(grid):
    """A layer's groups of non-blank tiles (4 neighbours): (row, column, rows, columns, {(dy, dx): tile})."""
    hh, ww = len(grid), len(grid[0])
    seen, out = set(), []
    for y in range(hh):
        for x in range(ww):
            if not grid[y][x] or (y, x) in seen:
                continue
            stack, cells = [(y, x)], []
            seen.add((y, x))
            while stack:
                a, b = stack.pop()
                cells.append((a, b))
                for c, d in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if 0 <= c < hh and 0 <= d < ww and grid[c][d] and (c, d) not in seen:
                        seen.add((c, d))
                        stack.append((c, d))
            ys, xs = [c[0] for c in cells], [c[1] for c in cells]
            y0, x0 = min(ys), min(xs)
            out.append((y0, x0, max(ys) - y0 + 1, max(xs) - x0 + 1, {(a - y0, b - x0): grid[a][b] for a, b in cells}))
    return out


def upper(spec, gmap):
    """Spec `upper_stamps`: dict(layer=3, source=(episode, level), blocks=[...], max_rows=8): where the GBC map has a
    structure of those blocks (DELIANI's pink-windowed machines), one of the source's own compositions of that layer
    whole (its groups of tiles, as the original draws them), at the column it has there: they reach in from the
    playfield's side, open towards it (the user: "ni jedan od overlay otoka nije pravilno zatvoren ... uzeti gotove
    kompozicije s pc deliani overlay layera"); the side nearer the GBC structure's middle, the nearest in rows of those;
    two GBC structures side by side at the same rows a pair the source has side by side (its rows apart kept: "znaju
    dolaziti 2 otoka istovremeno s lijeve i desne strane"). The layer's row R over layer 1's row R - 300 (the layers
    start at rows 592 and 292; spec upper_pace keeps it at layer 1's pace). Returns (map index, {(row, column): tile})."""
    st = spec.get('upper_stamps')
    if not st:
        return None, {}
    k = st['layer'] - 1
    src = [l for l in E.sources.original_levels() if (l['episode'], l['name']) == tuple(st['source'])][0]
    grid = src['maps'][st.get('source_layer', st['layer']) - 1]
    cols = len(grid[0])
    comps = [c for c in components(grid) if c[2] <= st.get('max_rows', 8)]
    # (a composition's column at the side it reaches in from made whole, as the column next to it: its step there, off the
    # PC's screen, shows in the wide 3D playfield, the user: "pripaziti na ovaj rubni gore lijevo")
    closed = []
    for (y0, x0, ph, pw, cells) in comps:
        cells = dict(cells)
        for edge, nxt in ((0, 1), (pw - 1, pw - 2)):
            at_side = (x0 + edge == 0) or (x0 + edge == cols - 1)
            if at_side and pw > 1 and any((yy, edge) not in cells for yy in range(ph)):
                for yy in range(ph):
                    if (yy, nxt) in cells:
                        cells[(yy, edge)] = cells[(yy, nxt)]
        closed.append((y0, x0, ph, pw, cells))
    comps = closed
    side = lambda c: 'L' if c[1] == 0 and c[1] + c[3] < cols else 'R' if c[1] + c[3] == cols and c[1] > 0 else 'F'
    blocks = set(st['blocks'])
    h, w = len(gmap), len(gmap[0])
    machines = []
    seen = set()
    for j in range(h):
        for i in range(w):
            if gmap[j][i] not in blocks or (j, i) in seen:
                continue
            stack, cells = [(j, i)], []
            seen.add((j, i))
            while stack:
                a, b = stack.pop()
                cells.append((a, b))
                for c, d in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if 0 <= c < h and 0 <= d < w and (c, d) not in seen and gmap[c][d] in blocks:
                        seen.add((c, d))
                        stack.append((c, d))
            ys, xs = [c[0] for c in cells], [c[1] for c in cells]
            machines.append(dict(top=min(ys), rows=max(ys) - min(ys) + 1, side='L' if (min(xs) + max(xs)) / 2 < (w - 1) / 2 else 'R'))
    out = {}
    used = set()

    def place(m, c, dy=0):
        r0 = E.ROWS - h + m['top'] + (m['rows'] - c[2]) // 2 + dy + E.ROWS
        for (yy, xx), t in c[4].items():
            if 0 <= r0 + yy < 2 * E.ROWS:
                out[(r0 + yy, c[1] + xx)] = t
    done = set()
    for n, m in enumerate(machines):
        if n in done:
            continue
        mate = next((q for q, o in enumerate(machines) if q != n and q not in done and o['side'] != m['side'] and
                     abs(o['top'] - m['top']) <= 2), None)
        if mate is not None:
            left, right = (m, machines[mate]) if m['side'] == 'L' else (machines[mate], m)
            pairs = [(a, b) for a in comps if side(a) == 'L' for b in comps if side(b) == 'R' and abs(a[0] - b[0]) <= 6]
            if pairs:
                a, b = min(pairs, key=lambda p: (abs(p[0][2] - left['rows']) + abs(p[1][2] - right['rows']),
                                                 (id(p[0]) in used) + (id(p[1]) in used)))
                used.update((id(a), id(b)))
                place(left, a)
                place(left, b, b[0] - a[0] + (a[2] - left['rows']) // 2 - (b[2] - left['rows']) // 2)
                done.update((n, mate))
                continue
        cands = [c for c in comps if side(c) == m['side']] or comps
        c = min(cands, key=lambda c: (abs(c[2] - m['rows']), id(c) in used))
        used.add(id(c))
        place(m, c)
        done.add(n)
    return k, out


if __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    out, gmap, img, letter = layer(spec)
    D.picture(out, gmap, img, letter).save(sys.argv[2] if len(sys.argv) > 2 else f'remake_L{n:02d}.png')
