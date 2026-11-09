"""Episode 7's maps by corners: layer 1 1:1 after the GBC map (a PC cell a GBC block, as tools/gbc/dictionary.py lays it),
each cell's tile the one whose corners are the GBC map's materials at that block's corners.

The materials are the level's look's main colours (k-means of its originals' tiles' corner and centre patches, weighted
by use: spec `maps`, and `corner_maps` for more originals of the tile set, TYRIAN's dark pits GAUNTLET's; their number
`corner_materials`; tiles left out `corner_exclude`). A material
at a block's corner (the GBC map's colours there, their lightness range moved to the tiles') is shared by the four cells
round it, so every boundary between two materials runs through cells, never along their edges: each cell takes a tile
whose four corners (and centre) are its own, the originals' transition tiles, where the old per-quarter plan put plain
tiles side by side (the user: "rubovi trave nisu smooth", "naglo prekinuti"). The tiles are any of the tile set's
that the originals use and whose patches are all near the materials; the pairs as all originals of the tile set pair
them (episode.pair_costs), the map solved over the whole grid (episode.solve_grid), a little noise in the choice where
several tiles fit (the user: "vise varijacije"); a dictionary's picks (dictionaries.json) fixed where a block has one.

    python tools/gbc/corners.py 23 [out.png]     the corner map for GBC level 23 beside its GBC map
"""
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import episode as E  # noqa: E402
import dictionary as D  # noqa: E402

POOL_DIST = 10.0     # a tile the level's originals never use: its patches at most this far (Lab) from a material
POOL_DETAIL = 14.0   # ... and its 4 x 4 pixel cells at most this far (the level's originals' tiles: all of them)
CENTRE_WEIGHT = 0.5  # a cell's centre counts half a corner
SLACK = 1.0          # candidates up to this much worse than the best fit
VARY = 0.25          # noise in the choice among fitting tiles
OWN_WEIGHT = 4       # the level's own originals' use counts this much more in the prior
WINDOW = 4           # half the GBC window (px) round a corner or centre


def patches(lab_img):
    """A tile's (28 x 24 Lab) corner patches TL, TR, BL, BR and centre, their mean colours (5, 3)."""
    p = [lab_img[:7, :6], lab_img[:7, 18:], lab_img[21:, :6], lab_img[21:, 18:], lab_img[10:18, 8:16]]
    return np.array([q.reshape(-1, 3).mean(0) for q in p])


def mix_distance(v, centres):
    """Each colour's (n, 3) distance to the nearest mix of two materials (the segments between their centres)."""
    best = np.full(len(v), np.inf)
    for a in range(len(centres)):
        for b in range(len(centres)):
            d = centres[b] - centres[a]
            u = np.clip(((v - centres[a]) @ d) / max(d @ d, 1e-9), 0, 1) if a != b else np.zeros(len(v))
            best = np.minimum(best, np.linalg.norm(v - (centres[a] + u[:, None] * d), axis=1))
    return best


def counts(grids):
    right, above, selfish, use = D.originals(grids)
    return right, above, selfish, use


def setup(spec):
    gmap, img, grids, letter = D.setting(spec)
    names = {tuple(m) for m in spec.get('corner_maps', [])}
    extra = [l['maps'][0] for l in E.sources.original_levels() if (l['episode'], l['name']) in names and l['shapes'] == letter]
    every = [l['maps'][0] for l in E.sources.original_levels() if l['shapes'] == letter]
    tiles = E.preview.tiles(letter)
    pal = E.preview.palette()
    _, _, _, own = counts(grids + extra)
    right, above, selfish, use = counts(every)
    # (a blank tile, which shows what is under layer 1, as black: BUBBLES's, WARP's and FLEET's space)
    labs = {t: E.lab(np.zeros((28, 24, 3)) if tiles.get(t) is None else pal[tiles[t]].astype(np.float64))
            for t in set(use) | set(own) if use[t] or own[t]}
    P = {t: patches(v) for t, v in labs.items()}
    from scipy.cluster.vq import kmeans2
    total = sum(own[t] for t in P)
    sample = np.concatenate([P[t] for t in P for _ in range(round(3000 * own[t] / total)) if own[t]])
    centres, _ = kmeans2(sample, spec.get('corner_materials', 4), minit='++', seed=spec.get('seed', 1))
    objects = E.object_tiles(letter)
    pool = []
    for t, p in P.items():
        if t in objects or t in spec.get('corner_exclude', ()):
            continue
        if spec.get('corner_own_only') and not own[t]:
            continue  # (DELI CORE: UNDERDELI's tiles alone, not the rest of its set's)
        if spec.get('corner_no_blank') and tiles.get(t) is None:
            continue  # (DELIANI: its blank tiles were black holes in the floor)
        near = np.sqrt(((p[:, None] - centres[None]) ** 2).sum(-1)).min(1)
        # (and none of its 4 x 4 pixel cells far from every mix of two materials: GAUNTLET's black with red lamps, its
        # blue grids; a grass edge's speckled cells are a mix of grass and dirt)
        cells = labs[t].reshape(7, 4, 6, 4, 3).mean((1, 3)).reshape(-1, 3)
        detail = mix_distance(cells, centres).max()
        if own[t] >= 1 or (near.max() <= POOL_DIST and detail <= POOL_DETAIL):
            pool.append(t)
    pool.sort()
    sigs = np.array([((P[t][:, None] - centres[None]) ** 2).sum(-1).argmin(1) for t in pool])
    return dict(gmap=gmap, img=img, grids=grids, every=every, letter=letter, tiles=tiles, pal=pal, own=own, use=use,
                right=right, above=above, selfish=selfish, centres=centres, sample=sample, pool=pool, sigs=sigs)


def plan(spec, S):
    """The materials at the GBC blocks' corners (H + 1, W + 1) and centres (H, W)."""
    img, centres, sample = S['img'], S['centres'], S['sample']
    g = E.lab(img.astype(np.float64))
    if spec.get('match'):
        gm, gs = g.reshape(-1, 3).mean(0), g.reshape(-1, 3).std(0) + 1e-6
        g = (g - gm) / gs * sample.std(0) + sample.mean(0)
    from scipy.ndimage import gaussian_filter
    blur = spec.get('corner_blur', 1.0)
    if blur:
        g = np.stack([gaussian_filter(g[..., i], blur, mode='nearest') for i in range(3)], -1)
    # (the lightness range by spec `corner_range`, percentiles: 1 to 99 takes the GBC's darkest to the tiles' darkest, so
    # TYRIAN's black pits stay black, where 5 to 95 lifted them into the rock)
    q = list(spec.get('corner_range', (1, 99)))
    lo, hi = np.percentile(g[..., 0], q)
    plo, phi = np.percentile(sample[:, 0], q)
    g[..., 0] = plo + (g[..., 0] - lo) * (phi - plo) / max(hi - lo, 1e-6)
    # (spec `corner_dark_as`: [lightness, tile]: the GBC map's pixels darker than that, before the range is moved, that
    # tile's centre colour: TYRIAN's black pits NOSE DRIP's raised ridges, which join their ground as the originals do)
    if spec.get('corner_dark_as'):
        level, t = spec['corner_dark_as']
        im = S['tiles'][t]
        col = patches(E.lab(S['pal'][im].astype(np.float64)))[4]
        dark = E.lab(img.astype(np.float64))[..., 0] < level
        if blur:
            dark = gaussian_filter(dark.astype(float), blur, mode='nearest') > 0.5
        g[dark] = col
    h, w = len(S['gmap']), len(S['gmap'][0])

    def at(y, x):
        win = g[max(0, y - WINDOW):min(g.shape[0], y + WINDOW), max(0, x - WINDOW):min(g.shape[1], x + WINDOW)]
        return int(((win.reshape(-1, 3).mean(0) - centres) ** 2).sum(-1).argmin())
    V = np.array([[at(16 * j, 16 * i) for i in range(w + 1)] for j in range(h + 1)])
    C = np.array([[at(16 * j + 8, 16 * i + 8) for i in range(w)] for j in range(h)])
    # (spec `block_like`: {block: tile}, those blocks wholly that tile's material, corners and centre: DESERT's drawn
    # arches the concrete's, so the walls round them are the originals')
    for b, t in spec.get('block_like', {}).items():
        m = material_of(S, t)
        for j, row in enumerate(S['gmap']):
            for i, x in enumerate(row):
                if x == int(b):
                    C[j][i] = m
                    V[j][i] = V[j][i + 1] = V[j + 1][i] = V[j + 1][i + 1] = m
    return V, C


def material_of(S, t):
    """The material of a tile's centre patch."""
    im = S['tiles'].get(t)
    lab_img = E.lab(np.zeros((28, 24, 3)) if im is None else S['pal'][im].astype(np.float64))
    return int(((patches(lab_img)[4] - S['centres']) ** 2).sum(-1).argmin())


def templates(spec, gmap):
    """{(GBC row, GBC column): tile} where the GBC map has one of spec `templates`' block patterns ([pattern, tiles], 2D
    lists, None anywhere: any block, no tile): DESERT's pyramids the PC's stone ruin, OASIS's arches its rocks. A pattern
    cut off by the map's side matches on what shows of it (two columns at least: the GBC arches half off the map, which
    became stray tiles, the user: "desno od 6. i 10. luka je jedan sivi tile"), and tiles wider than the pattern or past
    the side move in no further than the PC playfield needs: columns -2 .. 11 (the PC's side columns 0, 1 and 13)."""
    out = {}
    h, w = len(gmap), len(gmap[0])
    for pattern, tiles in spec.get('templates', ()):
        ph, pw = len(pattern), len(pattern[0])
        th, tw = len(tiles), len(tiles[0])
        for j in range(h - ph + 1):
            for i in range(-(pw - 2), w - 1):
                seen = [(y, x) for y in range(ph) for x in range(pw) if 0 <= i + x < w and pattern[y][x] is not None]
                if len({x for _, x in seen}) < 2 or not all(gmap[j + y][i + x] == pattern[y][x] for y, x in seen):
                    continue
                x0 = max(-D.LEFT, min(i, 14 - D.LEFT - tw))
                for y in range(min(th, h - j)):
                    for x in range(tw):
                        if tiles[y][x] is not None:
                            out[(j + y, x0 + x)] = tiles[y][x]
    return out


def gbc_row(r, h):
    """The GBC row a PC row shows (dictionary.lay's: the map at the bottom, its top 8 rows looped above)."""
    b = E.ROWS - 1 - r
    if b >= h:
        b = h - 8 + (b - h) % 8
    return h - 1 - b


REPAIR_PAIR = 100.0  # repair: a pair the originals never make against a region off the plan
REPAIR_MISS = 1.0    # ... a changed cell at most this many regions further off its plan (the layout kept)


def repair(choice, misses, seen_h, seen_v, prior, h, sweeps=6, pairs=True, slack=REPAIR_MISS):
    """After the solve, each free cell in a pair the originals never make takes the tile (any of the pool) with the
    fewest such pairs round it, then the fewest regions off its plan: the last odd joins (the user on DELICORE: "ajmo
    još tih 42 popraviti") without moving the rest of the map. Returns how many cells changed."""
    changed = 0
    top = E.ROWS - h
    # (each cell's miss as the solve left it: a repair may go at most REPAIR_MISS past that, not drift step by step)
    base = {k: m[choice[k[0]][k[1]]] + slack for k, m in misses.items()}

    def bad_round(r, c, t):
        n = np.zeros(len(t), int) if hasattr(t, '__len__') else 0
        if c > 0:
            n = n + ~seen_h[choice[r][c - 1], t]
        if c < 13:
            n = n + ~seen_h[t, choice[r][c + 1]]
        if r + 1 < E.ROWS:
            n = n + ~seen_v[choice[r + 1][c], t]
        if r > top:
            n = n + ~seen_v[t, choice[r - 1][c]]
        return n
    every = np.arange(seen_h.shape[0])
    for _ in range(sweeps):
        moved = 0
        for r in range(top, E.ROWS):
            for c in range(14):
                if (r, c) not in misses or bad_round(r, c, choice[r][c]) == 0:
                    continue
                cost = REPAIR_PAIR * bad_round(r, c, every) + misses[(r, c)] + E.PRIOR_WEIGHT * prior
                cost = np.where(misses[(r, c)] > base[(r, c)], np.inf, cost)
                best = int(cost.argmin())
                if best != choice[r][c] and cost[best] < cost[choice[r][c]]:
                    choice[r][c] = best
                    moved += 1
        changed += moved
        if not moved:
            break
    # (then two cells at once, where one alone can't join both ways: each odd pair's two cells every two tiles)
    T = seen_h.shape[0]
    for _ in range(sweeps if pairs else 0):
        moved = 0
        for r in range(top, E.ROWS):
            for c in range(14):
                for r2, c2 in ((r, c + 1), (r + 1, c)):
                    if r2 >= E.ROWS or c2 > 13 or (r, c) not in misses or (r2, c2) not in misses:
                        continue
                    a, b = choice[r][c], choice[r2][c2]
                    odd = (not seen_h[a, b]) if r2 == r else (not seen_v[b, a])
                    if not odd:
                        continue
                    best, best_cost = None, (REPAIR_PAIR * (bad_round(r, c, a) + bad_round(r2, c2, b)) +
                                             misses[(r, c)][a] + misses[(r2, c2)][b])
                    for ta in range(T):
                        if misses[(r, c)][ta] > base[(r, c)]:
                            continue
                        choice[r][c] = ta
                        tb_cost = REPAIR_PAIR * bad_round(r2, c2, every) + misses[(r2, c2)]
                        choice[r2][c2] = b
                        tb_cost = np.where(misses[(r2, c2)] > base[(r2, c2)], np.inf, tb_cost)
                        for tb in np.argsort(tb_cost)[:4]:
                            if not np.isfinite(tb_cost[tb]):
                                continue
                            choice[r2][c2] = int(tb)
                            cost = REPAIR_PAIR * (bad_round(r, c, ta) + bad_round(r2, c2, int(tb))) + misses[(r, c)][ta] + misses[(r2, c2)][tb]
                            if cost < best_cost:
                                best, best_cost = (ta, int(tb)), cost
                        choice[r2][c2] = b
                    choice[r][c] = a
                    if best is not None:
                        choice[r][c], choice[r2][c2] = best
                        moved += 1
        changed += moved
        if not moved:
            break
    return changed


def patch(choice, misses, seen_h, seen_v, h, size=(3, 4), budget=200000):
    """The odd pairs no one or two cells can mend: a window of free cells round each solved whole (depth first, every
    pair inside it and across its border one the originals make, the fewest regions off the plan). Returns how many
    windows were mended."""
    top = E.ROWS - h
    T = seen_h.shape[0]

    def odd_cells():
        out = []
        for r in range(top, E.ROWS):
            for c in range(14):
                if c < 13 and not seen_h[choice[r][c], choice[r][c + 1]]:
                    out.append((r, c))
                if r + 1 < E.ROWS and not seen_v[choice[r + 1][c], choice[r][c]]:
                    out.append((r, c))
        return out
    mended = 0
    for r0, c0 in odd_cells():
        if seen_h[choice[r0][c0], choice[r0][min(c0 + 1, 13)]] and (r0 + 1 >= E.ROWS or seen_v[choice[r0 + 1][c0], choice[r0][c0]]):
            continue  # (mended by an earlier window)
        best = None
        for wr, wc in ((size[0], size[1]), (size[1], size[0])):
            rs = range(max(top, r0 - wr // 2), min(E.ROWS, r0 - wr // 2 + wr))
            cs = range(max(0, c0 - wc // 2 + 1), min(14, c0 - wc // 2 + 1 + wc))
            cells = [(r, c) for r in rs for c in cs if (r, c) in misses]
            inside = set(cells)
            if not cells:
                continue
            grid = {k: choice[k[0]][k[1]] for k in cells}
            nodes = [0]
            found = [None]

            def ok(r, c, t):
                # the neighbours already set: left and above inside, any outside the window
                for (rr, cc, horiz, first) in ((r, c - 1, True, True), (r, c + 1, True, False), (r - 1, c, False, False),
                                               (r + 1, c, False, True)):
                    if not (top <= rr < E.ROWS and 0 <= cc < 14):
                        continue
                    if (rr, cc) in inside and cells.index((rr, cc)) > cells.index((r, c)):
                        continue
                    n = grid[(rr, cc)] if (rr, cc) in inside else choice[rr][cc]
                    if horiz and not (seen_h[n, t] if first else seen_h[t, n]):
                        return False
                    # (seen_v[below, above]: the row below is r + 1)
                    if not horiz and not (seen_v[n, t] if first else seen_v[t, n]):
                        return False
                return True

            def dfs(k, cost):
                nodes[0] += 1
                if nodes[0] > budget or (found[0] is not None and cost >= found[0][0]):
                    return
                if k == len(cells):
                    found[0] = (cost, dict(grid))
                    return
                r, c = cells[k]
                m = misses[(r, c)]
                for t in np.argsort(m):
                    t = int(t)
                    if ok(r, c, t):
                        grid[(r, c)] = t
                        dfs(k + 1, cost + m[t])
                grid[(r, c)] = choice[r][c]
            dfs(0, 0.0)
            if found[0] is not None and (best is None or found[0][0] < best[0]):
                best = found[0]
        if best is not None:
            for (r, c), t in best[1].items():
                choice[r][c] = t
            mended += 1
    return mended


def layer(spec, S=None, fixed=None):
    S = S or setup(spec)
    gmap, pool, sigs = S['gmap'], S['pool'], S['sigs']
    V, C = plan(spec, S)
    h, w = len(gmap), len(gmap[0])
    fixed = {int(b): t for b, t in (fixed if fixed is not None else D.picks().get(str(spec['gbc']), {})).items()}
    cells = templates(spec, gmap)
    ids = sorted(set(pool) | set(fixed.values()) | set(cells.values()))
    idx = {t: i for i, t in enumerate(ids)}
    T = len(ids)
    sig = np.full((T, 5), -1)
    for t, s in zip(pool, sigs):
        sig[idx[t]] = s
    weights = np.array([1, 1, 1, 1, CENTRE_WEIGHT])
    pri = np.array([S['use'][t] + OWN_WEIGHT * S['own'][t] for t in ids], np.float64) + 1
    prior = -np.log(pri / pri.max())
    rng = np.random.default_rng(spec.get('seed', 1))
    cands, unary = [], []
    misses = {}  # (row, column) -> each tile's miss off the plan (free cells only)
    for r in range(E.ROWS):
        i = gbc_row(r, h)
        row_c, row_u = [], []
        for c in range(14):
            g = min(max(c - D.LEFT, 0), w - 1)
            b = gmap[i][g]
            if (i, c - D.LEFT) in cells:
                ci = np.array([idx[cells[(i, c - D.LEFT)]]])
                row_c.append(ci)
                row_u.append(np.zeros(1))
                continue
            if b in fixed:
                ci = np.array([idx[fixed[b]]])
                row_c.append(ci)
                row_u.append(np.zeros(1))
                continue
            want = np.array([V[i][g], V[i][g + 1], V[i + 1][g], V[i + 1][g + 1], C[i][g]])
            miss = ((sig != want) * weights).sum(1)
            misses[(r, c)] = miss
            miss[sig[:, 0] < 0] = 99
            best = miss.min()
            ci = np.nonzero(miss <= best + spec.get('corner_slack', SLACK))[0]
            if len(ci) > E.CAND_MAX:
                ci = ci[np.argsort(miss[ci] * 10 + prior[ci])[:E.CAND_MAX]]
            row_c.append(ci)
            row_u.append(miss[ci] + E.PRIOR_WEIGHT * prior[ci] + VARY * rng.random(len(ci)))
        cands.append(row_c)
        unary.append(row_u)
    cost_h, cost_v, seen_h, seen_v, mis_h, mis_v = E.pair_costs(spec, ids, S['right'], S['above'], S['selfish'],
                                                                S['tiles'], S['pal'])
    choice = E.solve_grid(cands, unary, cost_h, cost_v, T, pair=spec.get('corner_pair'))  # (more: joins before the plan)
    if spec.get('corner_repair'):
        repaired = repair(choice, misses, seen_h, seen_v, prior, h, pairs=spec['corner_repair'] != 'single',
                          slack=spec.get('corner_repair_miss', REPAIR_MISS))
        if spec.get('corner_repair_finish'):
            # (and the last odd pairs with no bound, those cells alone: DELICORE's last 4, the user: "popravimo još tih 4")
            repaired += repair(choice, misses, seen_h, seen_v, prior, h, slack=np.inf)
            print(f"  {spec['name']}: {patch(choice, misses, seen_h, seen_v, h)} windows of odd pairs solved whole")
        print(f"  {spec['name']}: {repaired} cells changed so that their pairs are the originals'")
    out = [[ids[choice[r][c]] for c in range(14)] for r in range(E.ROWS)]
    pairs = [(seen_h, mis_h, choice[r][c - 1], choice[r][c]) for r in range(E.ROWS - h, E.ROWS) for c in range(2, 13)] + \
        [(seen_v, mis_v, choice[r + 1][c], choice[r][c]) for r in range(E.ROWS - h, E.ROWS - 1) for c in range(2, 13)]
    bad = sum(not seen[a, b] for seen, _, a, b in pairs)
    print(f"  {spec['name']} {S['letter']}: {len(ids)} tiles, {len(set(map(tuple, sigs)))} signatures; on the GBC map "
          f"{bad} of {len(pairs)} neighbour pairs the originals never have")
    inside = Counter(t for row in out[E.ROWS - h:] for t in row[D.LEFT:D.LEFT + w])
    out = D.sides(spec, out, S['letter'], S['grids'] + S['every'], allowed=inside)
    # (the templates' tiles in the side columns stay: an arch at the map's side reaches into them)
    for (i, g), t in cells.items():
        if not 0 <= g < w:
            r = E.ROWS - h + i
            out[r][g + D.LEFT] = t
            for r2 in range(E.ROWS - h):  # (and in the loop above the map, as dictionary.lay repeats its top rows)
                b = E.ROWS - 1 - r2
                if E.ROWS - h + 7 - (b - h) % 8 == r:
                    out[r2][g + D.LEFT] = t
    return out


if __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    S = setup(spec)
    out = layer(spec, S)
    D.picture(out, S['gmap'], S['img'], S['letter']).save(sys.argv[2] if len(sys.argv) > 2 else f'corners_L{n:02d}.png')
