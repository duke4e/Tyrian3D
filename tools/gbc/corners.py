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
    """{(GBC row, column): tile} where the GBC map has one of spec `templates`' block patterns ([pattern, tiles], 2D
    lists, None anywhere: any block, no tile): DESERT's pyramids the PC's stone ruin, OASIS's arches its rocks."""
    out = {}
    h, w = len(gmap), len(gmap[0])
    for pattern, tiles in spec.get('templates', ()):
        ph, pw = len(pattern), len(pattern[0])
        for j in range(h - ph + 1):
            for i in range(w - pw + 1):
                if all(pattern[y][x] is None or gmap[j + y][i + x] == pattern[y][x] for y in range(ph) for x in range(pw)):
                    for y in range(ph):
                        for x in range(pw):
                            if tiles[y][x] is not None:
                                out[(j + y, i + x)] = tiles[y][x]
    return out


def gbc_row(r, h):
    """The GBC row a PC row shows (dictionary.lay's: the map at the bottom, its top 8 rows looped above)."""
    b = E.ROWS - 1 - r
    if b >= h:
        b = h - 8 + (b - h) % 8
    return h - 1 - b


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
    for r in range(E.ROWS):
        i = gbc_row(r, h)
        row_c, row_u = [], []
        for c in range(14):
            g = min(max(c - D.LEFT, 0), w - 1)
            b = gmap[i][g]
            if (i, g) in cells and D.LEFT <= c < D.LEFT + w:
                ci = np.array([idx[cells[(i, g)]]])
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
            miss[sig[:, 0] < 0] = 99
            best = miss.min()
            ci = np.nonzero(miss <= best + SLACK)[0]
            if len(ci) > E.CAND_MAX:
                ci = ci[np.argsort(miss[ci] * 10 + prior[ci])[:E.CAND_MAX]]
            row_c.append(ci)
            row_u.append(miss[ci] + E.PRIOR_WEIGHT * prior[ci] + VARY * rng.random(len(ci)))
        cands.append(row_c)
        unary.append(row_u)
    cost_h, cost_v, seen_h, seen_v, mis_h, mis_v = E.pair_costs(spec, ids, S['right'], S['above'], S['selfish'],
                                                                S['tiles'], S['pal'])
    choice = E.solve_grid(cands, unary, cost_h, cost_v, T)
    out = [[ids[choice[r][c]] for c in range(14)] for r in range(E.ROWS)]
    pairs = [(seen_h, mis_h, choice[r][c - 1], choice[r][c]) for r in range(E.ROWS - h, E.ROWS) for c in range(2, 13)] + \
        [(seen_v, mis_v, choice[r + 1][c], choice[r][c]) for r in range(E.ROWS - h, E.ROWS - 1) for c in range(2, 13)]
    bad = sum(not seen[a, b] for seen, _, a, b in pairs)
    print(f"  {spec['name']} {S['letter']}: {len(ids)} tiles, {len(set(map(tuple, sigs)))} signatures; on the GBC map "
          f"{bad} of {len(pairs)} neighbour pairs the originals never have")
    inside = Counter(t for row in out[E.ROWS - h:] for t in row[D.LEFT:D.LEFT + w])
    return D.sides(spec, out, S['letter'], S['grids'] + S['every'], allowed=inside)


if __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    S = setup(spec)
    out = layer(spec, S)
    D.picture(out, S['gmap'], S['img'], S['letter']).save(sys.argv[2] if len(sys.argv) > 2 else f'corners_L{n:02d}.png')
