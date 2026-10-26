"""The GBC Tyrian levels as an episode of the PC game (episode 7; docs/plans/2026-10-25-gbc-epizoda.md).

Each GBC level becomes a PC level of the original level it is a version of: its map is made anew from
that level's tiles by episode 6's synthesiser (tools/content/episode6/mapsynth.py), with the GBC map as
the plan (each map cell weighs the tiles by how near their colours, quarter by quarter, are to the GBC
map's there, after the GBC colours are matched to the tile set's). The GBC map is scaled 1.5x (GBC 176 px
= the 264 px the PC playfield shows). Written as level JSON (as episode 6's levels) to
data/gbc/episode7 with a preview of each map beside the GBC one; tools/content/gbc/build.py turns them
into the game's files. Needs data/gbc/levels (tools/gbc/extract.py), the game data, numpy and PIL.

    python tools/gbc/episode.py [--levels 23,3,...]
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'content', 'episode6'))
import mapsynth  # noqa: E402
import preview  # noqa: E402
import sources  # noqa: E402
import waves  # noqa: E402

GBC = os.path.join(ROOT, 'data', 'gbc')
OUT = os.path.join(GBC, 'episode7')
SCALE = 1.5           # PC pixels per GBC pixel
ROWS = 300            # layer 1 rows
LOOK_EVENTS = {1, 2, 3, 8, 9, 21, 28, 29, 42, 43, 44, 48, 64, 65, 72, 73}  # as episode 6's generate.py
OVERRIDES = os.path.join(HERE, 'enemy_overrides.json')
# Episode 7's own enemies (the GBC levels' that no PC level has; overrides name them ["gbc", name]): sheet W, shapeFile's
# 37th (tools/content/gbc/build.py makes their records)
NEW_ENEMIES = json.load(open(os.path.join(ROOT, 'tools', 'content', 'gbc', 'new_enemies.json')))
NEW_SHEET = 37
PAIR_COST = 4.0       # autotile: a pair of tiles side by side or above each other that no original has, in quarters off the plan
SIGMA = 0.15          # material mismatch (0-2, the quarters' shares) beyond a cell's nearest tile: weight 1/e
FORBID = 0.6          # ... and from where a tile is not taken

# The original levels whose enemies the GBC ones are first sought among (enemies.py: pool)
SAVARAS = [(1, 'SAVARA'), (1, 'SAVARA V'), (4, 'SAVARA IV'), (3, 'SAVARA Y')]
DESERTS = [(4, 'SURFACE'), (4, 'DESERTRUN'), (4, 'TIME WAR')]
JUNGLES = [(2, 'TORM'), (2, 'GYGES'), (2, 'BOTANY A'), (2, 'BOTANY B')]
ICES = [(3, 'CAMANIS'), (4, 'ICE EXIT'), (4, 'ICESECRET')]
DELIS = [(1, 'DELIANI'), (3, 'New Deli'), (4, 'UNDERDELI'), (4, 'CORE')]
LAVAS = [(4, 'LAVA EXIT'), (4, 'LAVA RUN'), (4, 'SIDE EXIT')]

# The episode in the GBC game's Full Game order (found by playing it through in the emulator), with the
# levels only its Arcade mode has (arcade) after one of their look. gbc: the GBC level (data/gbc/levels/Lnn_*); pc: the original level it
# is a version of (its tiles, look, song).
LEVELS = [
    dict(gbc=23, name='TYRIAN', pc=(1, 'TYRIAN'), maps=[(1, 'TYRIAN'), (3, 'TYRIAN X'), (4, 'NOSE DRIP')], pool=[(1, 'TYRIAN'), (3, 'TYRIAN X')]),
    dict(gbc=3, name='ASTEROID', pc=(1, 'ASTEROID1'), pool=[(1, 'ASTEROID1'), (1, 'ASTEROID2'), (1, 'ASTEROID?')]),
    dict(gbc=11, name='SPACE', pc=(2, 'SOH JIN'), space=True, pool=[(1, 'SOH JIN'), (2, 'SOH JIN'), (2, 'GEM WAR'), (2, 'MARKERS'), (2, 'MISTAKES')], boss=(2, 'GEM WAR')),
    dict(gbc=19, name='SAVARA', pc=(4, 'SAVARA IV'), pool=SAVARAS),
    dict(gbc=20, name='SAVARA II', pc=(1, 'SAVARA V'), pool=SAVARAS),
    dict(gbc=14, name='OASIS', pc=(4, 'SURFACE'), arcade=True, pool=DESERTS),
    dict(gbc=2, name='DESERT', pc=(4, 'DESERTRUN'), arcade=True, pool=DESERTS, boss=(4, 'SURFACE')),
    dict(gbc=4, name='JUNGLE', pc=(2, 'TORM'), pool=JUNGLES),
    dict(gbc=8, name='JUNGLE II', pc=(2, 'TORM'), seed=2, pool=JUNGLES),
    dict(gbc=9, name='ASTEROID2', pc=(1, 'ASTEROID2'), pool=[(1, 'ASTEROID2'), (1, 'ASTEROID1'), (2, 'ASTCITY'), (3, 'AST. CITY')]),
    dict(gbc=13, name='WARP', pc=(3, 'STARGATE'), pool=[(3, 'STARGATE'), (1, 'BUBBLES')], boss=(1, 'ASSASSIN')),
    dict(gbc=12, name='BUBBLES', pc=(1, 'BUBBLES'), arcade=True, pool=[(1, 'BUBBLES'), (3, 'STARGATE')], boss=(2, 'GEM WAR')),
    dict(gbc=15, name='CAMANIS', pc=(3, 'CAMANIS'), pool=ICES),
    dict(gbc=18, name='ICE EXIT', pc=(4, 'ICE EXIT'), maps=[(4, 'ICE EXIT'), (3, 'CAMANIS')], arcade=True, pool=ICES),
    dict(gbc=5, name='AST.BONUS', pc=(1, 'ASTEROID?'), pool=[(1, 'ASTEROID?'), (1, 'BONUS'), (2, 'BONUS')], boss=(1, 'ASTEROID2')),
    dict(gbc=10, name='SPACE ATK', pc=(4, 'SQUADRON'), space=True, pool=[(4, 'SQUADRON'), (1, 'ASSASSIN'), (4, 'DREAD-NOT')], boss=(4, 'APPROACH')),
    dict(gbc=21, name='FLEET', pc=(3, 'FLEET'), pool=[(3, 'FLEET')]),
    dict(gbc=17, name='DELIANI', pc=(4, 'BRAINIAC'), pool=[(4, 'BRAINIAC'), (1, 'DELIANI'), (3, 'New Deli')]),
    dict(gbc=22, name='TUNNEL', pc=(4, 'NOSE DRIP'), pool=[(4, '?TUNNEL?'), (4, 'NOSE DRIP'), (3, 'IXMUCANE')], boss=(3, 'IXMUCANE')),
    dict(gbc=1, name='DELICORE', pc=(1, 'DELIANI'), match=True, arcade=True, pool=DELIS),
    dict(gbc=16, name='DELI CORE', pc=(3, 'New Deli'), match=True, pool=DELIS),
    dict(gbc=6, name='LAVA I', pc=(4, 'LAVA EXIT'), pool=LAVAS),
    dict(gbc=7, name='LAVA II', pc=(4, 'LAVA RUN'), pool=LAVAS, boss=(4, 'CORE')),
    dict(gbc=24, name='FINALE', pc=(4, 'DREAD-NOT'), space=True, pool=[(4, 'DREAD-NOT'), (4, 'APPROACH')]),
]


def lab(rgb):
    """sRGB (0-255, ...x3) -> CIE Lab."""
    c = rgb.astype(np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = np.einsum("...i,ij->...j", c, np.array([[0.4124, 0.2126, 0.0193], [0.3576, 0.7152, 0.1192], [0.1805, 0.0722, 0.9505]]))
    xyz /= np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def quarter_shares(labels, k):
    """Each quarter's share of each material: labels (h, w) of material numbers -> (2, 2, k)."""
    h, w = labels.shape
    return np.array([[np.bincount(labels[y * h // 2:(y + 1) * h // 2, x * w // 2:(x + 1) * w // 2].ravel(),
                                  minlength=k) / ((h // 2) * (w // 2)) for x in range(2)] for y in range(2)])


def quarters(img):
    """Mean colour of each quarter (2x2) of an image (h, w, 3) -> (2, 2, 3)."""
    h, w = img.shape[:2]
    return np.array([[img[y * h // 2:(y + 1) * h // 2, x * w // 2:(x + 1) * w // 2].reshape(-1, 3).mean(0)
                      for x in range(2)] for y in range(2)])


def match_channels(src, ref, src_w=None, ref_w=None):
    """A function mapping src's colours (Lab) so each channel's distribution is ref's (quantiles)."""
    qs = np.linspace(0, 1, 101)

    def wq(v, w, q):
        o = np.argsort(v)
        cw = np.cumsum(w[o] if w is not None else np.ones(len(v)))
        return np.interp(q * cw[-1], cw, v[o])
    maps = []
    for k in range(3):
        a = wq(src[:, k], src_w, qs)
        b = wq(ref[:, k], ref_w, qs)
        maps.append((a, b))
    return lambda x: np.stack([np.interp(x[..., k], *maps[k]) for k in range(3)], -1)


def gbc_level(n):
    d = [p for p in os.listdir(os.path.join(GBC, 'levels')) if p.startswith(f'L{n:02d}_')][0]
    d = os.path.join(GBC, 'levels', d)
    return json.load(open(os.path.join(d, 'map.json'))), np.array(Image.open(os.path.join(d, 'map.png')).convert('RGB'))


def level_song(ep, name):
    import levels as lv
    for s in lv.read_strings(os.path.join(sources.tyrdata.DATA, f'levels{ep}.dat')):
        if s.startswith(']L') and s[13:22].strip() == name:
            return int(s[22:24])
    return 1


def plan_targets(labels, n_rows, k):
    """Each PC cell's (layer 1, rows ROWS-n_rows.. ROWS-1 and the loop above) target: its quarters' shares
    of the k materials in the GBC map (labels: the GBC map's pixels as material numbers).
    PC column c spans GBC x 16c-38 .. 16c-22 (the ship centred: x = 24c - 33 in game x, 24 the
    playfield's left edge); a row is 28/1.5 GBC px; rows above the map repeat its top 8 rows."""
    h = labels.shape[0]
    ph = 28 / SCALE
    tgt = np.zeros((ROWS, 14, 2, 2, k))
    for r in range(ROWS):
        b = ROWS - 1 - r                      # PC rows from the bottom
        if b >= n_rows:
            b = n_rows - 8 + (b - n_rows) % 8  # the loop at the top
        y1 = h - b * ph
        y0 = y1 - ph
        for c in range(14):
            x0 = 16 * c - 38
            ys = np.clip(np.arange(int(round(y0)), int(round(y1))), 0, h - 1)
            xs = np.clip(np.arange(x0, x0 + 16), 0, labels.shape[1] - 1)
            tgt[r, c] = quarter_shares(labels[ys][:, xs], k)
    return tgt


def regions(img, n):
    """Mean colour of each of n x n regions of an image (h, w, 3) -> (n, n, 3)."""
    h, w = img.shape[:2]
    return np.array([[img[y * h // n:(y + 1) * h // n, x * w // n:(x + 1) * w // n].reshape(-1, 3).mean(0)
                      for x in range(n)] for y in range(n)])


def space(spec, img, grids, letter):
    """Open space: layer 1 all the original's most used blank tile, the stars the game's (its look)."""
    from collections import Counter
    tiles = preview.tiles(letter)
    blank = [t for t, _ in Counter(t for g in grids for row in g for t in row).most_common() if tiles.get(t) is None][0]
    n_rows = int(round(img.shape[0] * SCALE / 28))
    print(spec['name'], f'{n_rows} rows from GBC, open space (tile {blank})')
    return [[blank] * 14 for _ in range(ROWS)], n_rows


def autotile(spec, img, grids, letter):
    """Layer 1 from the GBC map by materials. The materials are the tile set's main colours (k-means of
    the used tiles' region means, weighted by use); a tile's signature is the materials of its n x n
    regions; the GBC map (spec 'match': its colours moved to the tile set's first), cut into the PC
    tiles' regions, gives each cell the signature it wants, and the cell takes a tile with the fewest
    regions off it: the originals' common tiles (ground rather than the objects on it), paired with their
    neighbours as the originals pair them (row by row, Viterbi, over a few passes: edges that join up)."""
    from collections import Counter
    from scipy.cluster.vq import kmeans2
    n = spec.get('regions', 2)
    tiles = preview.tiles(letter)
    pal = preview.palette()
    use = Counter(t for g in grids for row in g for t in row)
    above, right = {}, {}
    for g in grids:
        for y in range(len(g)):
            for x in range(len(g[0])):
                if y + 1 < len(g):
                    above.setdefault(g[y + 1][x], Counter())[g[y][x]] += 1
                if x > 0:
                    right.setdefault(g[y][x - 1], Counter())[g[y][x]] += 1
    # ground, not the objects standing on it: a ground tile (a texture, a straight edge) stands beside
    # or above itself somewhere in the originals; an object's tiles (a bunker's four) never do
    selfish = Counter()
    for g in grids:
        for y in range(len(g)):
            for x in range(len(g[0])):
                if (x > 0 and g[y][x - 1] == g[y][x]) or (y > 0 and g[y - 1][x] == g[y][x]):
                    selfish[g[y][x]] += 1
    ground = [t for t, _ in use.most_common() if selfish[t] >= 1 or use[t] >= 100]
    ids = ground[:mapsynth.LAYER_TILES[0]]  # (a layer's limit)
    rmean = {}
    for t in ids:
        im = tiles.get(t)
        rmean[t] = lab(regions(np.zeros((28, 24, 3)) if im is None else pal[im].astype(np.float64), n))
    k = spec.get('materials', 4)
    sample = np.concatenate([rmean[t].reshape(-1, 3) for t in ids for _ in range(min(30, 1 + use[t] // 20))])
    centres, _ = kmeans2(sample, k, minit='++', seed=spec.get('seed', 1))

    def material(v):
        return ((v[..., None, :] - centres) ** 2).sum(-1).argmin(-1)
    sigs = np.array([material(rmean[t]).ravel() for t in ids])  # (T, n*n)
    weight = np.array([use[t] for t in ids], np.float64) ** 2
    n_rows = int(round(img.shape[0] * SCALE / 28))
    g = lab(img.astype(np.float64))
    if spec.get('match'):
        # GBC colours far from the tile set's (the DeliCores' purple): its mean and spread per channel
        # moved to the used tiles'
        gm, gs = g.reshape(-1, 3).mean(0), g.reshape(-1, 3).std(0) + 1e-6
        g = (g - gm) / gs * sample.std(0) + sample.mean(0)
    # blurred, so the GBC textures' grain (pebbles, cobbles) doesn't read as edges
    from scipy.ndimage import gaussian_filter
    g = np.stack([gaussian_filter(g[..., i], spec.get('blur', 3.0), mode='nearest') for i in range(3)], -1)
    # its lightness range moved to the tile set's (5th to 95th percentile), the hues kept: the GBC
    # greys and browns are drawn lighter and with more contrast
    lo, hi = np.percentile(g[..., 0], [5, 95])
    plo, phi = np.percentile(sample[:, 0], [5, 95])
    g[..., 0] = plo + (g[..., 0] - lo) * (phi - plo) / max(hi - lo, 1e-6)
    h = g.shape[0]
    rh, rw = 28 / n / SCALE, 24 / n / SCALE
    grid = np.zeros((ROWS * n, 14 * n), int)
    loop = 8 * n  # the loop at the top: the map's top 8 rows
    for r in range(ROWS * n):
        b = ROWS * n - 1 - r
        if b >= n_rows * n:
            b = n_rows * n - loop + (b - n_rows * n) % loop
        y1 = h - b * rh
        ys = np.clip(np.arange(int(round(y1 - rh)), max(int(round(y1)), int(round(y1 - rh)) + 1)), 0, h - 1)
        for c in range(14 * n):
            x0 = rw * c - 38
            xs = np.clip(np.arange(int(round(x0)), max(int(round(x0 + rw)), int(round(x0)) + 1)), 0, g.shape[1] - 1)
            grid[r, c] = material(g[ys][:, xs].reshape(-1, 3).mean(0))
    # each cell's candidates: the tiles nearest its plan (and one quarter further); the map is then the
    # choice that misses the plan least and pairs its tiles as the originals pair them (beside and above
    # each other: an edge that joins up, a texture that goes on), found row by row (the best row for the
    # rows below and above it, Viterbi) over a few passes from a first pass that looks only below
    T = len(ids)
    idx = {t: i for i, t in enumerate(ids)}
    seen_h = np.zeros((T, T), bool)  # [left, right]
    seen_v = np.zeros((T, T), bool)  # [below, above]
    for a_, cnt in right.items():
        for b_ in cnt:
            if a_ in idx and b_ in idx:
                seen_h[idx[a_], idx[b_]] = True
    for a_, cnt in above.items():
        for b_ in cnt:
            if a_ in idx and b_ in idx:
                seen_v[idx[a_], idx[b_]] = True
    prior = -np.log(np.array([use[t] for t in ids], np.float64) / max(use[t] for t in ids))
    MISS, PAIR, PRIOR = 1.0, PAIR_COST, 0.12
    cands, unary = [], []
    off = 0
    for r in range(ROWS):
        row_c, row_u = [], []
        for c in range(14):
            want = grid[n * r:n * r + n, n * c:n * c + n].ravel()
            miss = (sigs != want).sum(1)
            best = miss.min()
            off += best > 0
            ci = np.nonzero(miss <= best + 2)[0]
            if len(ci) > 48:
                ci = ci[np.argsort(miss[ci] * 10 + prior[ci])[:48]]
            row_c.append(ci)
            row_u.append(MISS * miss[ci] + PRIOR * prior[ci])
        cands.append(row_c)
        unary.append(row_u)
    choice = [[None] * 14 for _ in range(ROWS)]

    def solve_row(r, use_above):
        """The best row r for its neighbours below (and above): Viterbi along the row."""
        costs = []
        for c in range(14):
            u = unary[r][c].copy()
            ci = cands[r][c]
            if r + 1 < ROWS and choice[r + 1][c] is not None:
                u += PAIR * ~seen_v[choice[r + 1][c], ci]
            if use_above and r > 0 and choice[r - 1][c] is not None:
                u += PAIR * ~seen_v[ci, choice[r - 1][c]]
            costs.append(u)
        acc, back = costs[0], []
        for c in range(1, 14):
            pair = PAIR * ~seen_h[np.ix_(cands[r][c - 1], cands[r][c])]  # (prev, cur)
            tot = acc[:, None] + pair
            back.append(tot.argmin(0))
            acc = tot.min(0) + costs[c]
        k_ = int(acc.argmin())
        picks = [k_]
        for c in range(13, 0, -1):
            k_ = int(back[c - 1][k_])
            picks.append(k_)
        picks.reverse()
        for c in range(14):
            choice[r][c] = int(cands[r][c][picks[c]])
    for r in range(ROWS - 1, -1, -1):
        solve_row(r, False)
    for _ in range(3):
        for r in list(range(ROWS)) + list(range(ROWS - 1, -1, -1)):
            solve_row(r, True)
    layer1 = [[ids[choice[r][c]] for c in range(14)] for r in range(ROWS)]
    bad = sum(not seen_h[choice[r][c - 1], choice[r][c]] for r in range(ROWS) for c in range(1, 14)) + \
        sum(not seen_v[choice[r + 1][c], choice[r][c]] for r in range(ROWS - 1) for c in range(14))
    print(f'  {bad} pairs of tiles the originals never put together')
    print(spec['name'], letter, f'{n_rows} rows from GBC, {len(set(map(tuple, sigs)))} signatures, {off} cells off theirs')
    return layer1, n_rows


_ground = None


def ground_enemies():
    """{(episode, enemy): True} for the PC enemies the original levels make on the ground more often
    than in the air (spawn events 6, 10, 17, 56, and 12 on a ground layer)."""
    global _ground
    if _ground is None:
        import levels as lv
        from collections import Counter
        votes = Counter()
        for e_ in range(1, 6):
            for s in lv.read_strings(os.path.join(sources.tyrdata.DATA, f'levels{e_}.dat')):
                if not s.startswith(']L'):
                    continue
                try:
                    src = waves.Source(e_, s[13:22].strip())
                except Exception:
                    continue
                for e in src.events:
                    if e['type'] not in waves.SPAWNS or e['d1'] <= 0:
                        continue
                    ground = e['type'] in (6, 10, 17, 56) or (e['type'] == 12 and e['d6'] in (0, 1, 4))
                    for k in range(4 if e['type'] == 12 else 1):
                        votes[(e_, e['d1'] + k)] += 1 if ground else -1
        _ground = {k: v > 0 for k, v in votes.items()}
    return _ground


_cells = None


def review_enemies(level, types, use):
    """data/gbc/episode7/preview/Lnn_enemies.png: each GBC type (as used, most used first) beside the PC
    enemy it became."""
    global _cells
    import enemies as EN
    from PIL import ImageDraw
    if _cells is None:
        _cells = {(c[0], c[1], c[5]): c[4] for c in EN.atlas()}
    rows = []
    for t, n in use.most_common():
        p = os.path.join(GBC, 'enemies', f'L{level:02d}_type{t:02x}.png')
        row = Image.new('RGB', (230, 64), (24, 24, 24))
        d = ImageDraw.Draw(row)
        if os.path.exists(p):
            g = Image.open(p).convert('RGBA')
            k = max(1, min(3, 56 // max(g.size)))
            g = g.resize((g.size[0] * k, g.size[1] * k), Image.NEAREST)
            row.paste(g, (0, 0), g)
        pc = types.get(t)
        if pc and (pc[0], pc[1], pc[2]) in _cells:
            c = Image.fromarray(_cells[(pc[0], pc[1], pc[2])])
            c = c.resize((int(c.width * 56 / c.height), 56), Image.NEAREST)
            row.paste(c, (110, 0), c)
        d.text((60, 4), f'{t:02x} x{n}', fill=(255, 255, 255))
        d.text((60, 20), f'{pc[0]}:{pc[1]}' if pc else 'left out', fill=(255, 255, 0))
        rows.append(row)
    if rows:
        out = Image.new('RGB', (230 * 2, 66 * ((len(rows) + 1) // 2)))
        for i, r in enumerate(rows):
            out.paste(r, ((i % 2) * 230, (i // 2) * 66))
        out.save(os.path.join(OUT, 'preview', f'L{level:02d}_enemies.png'))


def pieces(records, positions, sizes):
    """The spawn records that are pieces of a big GBC enemy another record of the same moment makes: the GBC game
    builds a big ship of several types side by side (in one group), and each type's look was found for the whole
    of it (enemies.py draws the sprites round an enemy), so each made it again, on top of the other. A record
    whose place lies inside the sprite of one before it (the leftmost first), in its group, is left out (its
    type replaced by PIECE); the first is centred on the whole (script.py sizes)."""
    out = [list(r) for r in records]
    moment = {}
    for i, (r, p) in enumerate(zip(records, positions)):
        cmd = r[0]
        if cmd in (3, 4, 0x21, 0x22, 0x23, 0x24) or cmd >= 0x28:
            moment.setdefault(p, []).append(i)
    dropped = 0
    for idx in moment.values():
        idx.sort(key=lambda i: (records[i][2], (records[i][3] + 128) % 256))
        gone = set()
        for n, i in enumerate(idx):
            if i in gone:
                continue
            a = records[i]
            k = a[0] - 0x28
            cols, rows = ((((k >> 1) & 3) + 1, (k >> 3) + 1) if a[0] >= 0x28 else (1, 1))
            w, h = sizes.get(a[1], (16, 16))
            w, h = max(w, 16 * cols), max(h, 16 * rows)
            for j in idx[n + 1:]:
                b = records[j]
                if j in gone or b[4] != a[4]:
                    continue
                if 0 <= b[2] - a[2] < w and abs(((b[3] + 128) % 256) - ((a[3] + 128) % 256)) < h:
                    gone.add(j)
                    out[j][1] = PIECE
                    dropped += 1
    return out, dropped


PIECE = 0xFE              # (no GBC type: a record left out as a piece of another's enemy)


def enemies(spec, look):
    """The GBC script (data/gbc/enemies, tools/gbc/enemies.py) as PC events (script.py), its enemies
    the PC ones found for its types; the boss the original level's (a placement); the sprite sheets
    they need (at most 4: the less used types take a candidate on the loaded ones)."""
    import script
    import enemies as EN
    path = os.path.join(GBC, 'enemies', f"L{spec['gbc']:02d}.json")
    if not os.path.exists(path):
        return [], [], []
    d = json.load(open(path))
    rom = open(os.path.join(GBC, 'Tyrian.gb'), 'rb').read()

    def ro(a):
        return a if a < 0x4000 else d['bank'] * 0x4000 + a - 0x4000
    # the main script: the records run in order until the boss takes the script elsewhere
    last, prev_at, prev_pos = -1, -1, -1
    for e in d['executed']:
        if e['at'] < prev_at or e['pos'] < prev_pos:
            break
        last, prev_at, prev_pos = e['at'], e['at'], e['pos']
    records = [list(rom[ro(d['events'] + 5 * i):ro(d['events'] + 5 * i) + 5]) for i in range(last + 1)]
    positions = [rom[ro(d['events_pos'] + 2 * i)] | (rom[ro(d['events_pos'] + 2 * i + 1)] << 8) for i in range(last + 1)]
    # ... and no further than the positions run forwards (past its end the lists hold other data)
    for i in range(1, len(positions)):
        if positions[i] < positions[i - 1] or positions[i] > 6000:
            records, positions = records[:i], positions[:i]
            break
    data = {}

    def enemies_of(e_):
        if e_ == "gbc":
            return {}  # (episode 7's own enemies stand still: nothing of theirs to undo)
        if e_ not in data:
            data[e_] = sources.tyrdata.load_items(e_)['enemies']
        return data[e_]
    # types: their PC enemies (every GBC enemy is a PC one: the best candidate on the loaded sheets)
    from collections import Counter
    use = Counter(r[1] for r in records if r[0] in (3, 4, 0x21, 0x22, 0x23, 0x24) or r[0] >= 0x28)
    types, cands = {}, {}
    for t, info in d['types'].items():
        if info.get('pc'):
            cands[int(t)] = info['candidates']
    # the boss: the original level's, or (spec 'boss') another's where it has none
    boss_source = waves.Source(*spec['boss']) if spec.get('boss') else look
    boss = boss_source.boss()
    boss_banks = Counter()
    if boss:
        for e in boss['events']:
            if e['type'] in waves.SPAWNS and e['d1'] > 0:
                for k in range(4 if e['type'] == 12 else 1):
                    boss_banks.update(waves.sheets_of(boss_source.enemies, e['d1'] + k))
    def sheet(c):
        """The sheets a candidate needs ({99}: none it can be drawn with, e.g. sheet 0)."""
        if c['episode'] == "gbc":
            return {NEW_SHEET}
        b = set().union(*(waves.sheets_of(enemies_of(c['episode']), n) for n in EN.part_numbers(c['enemy'], c.get('parts', 1))))
        return {99} if (0 in b or not b) else b
    # by-eye corrections (tools/gbc/enemy_overrides.json: "L23:29" -> [episode, enemy], [episode, enemy, 4]
    # (event 12's block), [episode, [[enemy, dx, dy], ...]] (a composite) or null to leave a type out):
    # their sheets are loaded before the candidates' (after the boss's)
    over = {}
    for key, v in (json.load(open(OVERRIDES)) if os.path.exists(OVERRIDES) else {}).items():
        lv, t = key.split(':')
        if int(lv[1:]) != spec['gbc']:
            continue
        if v is None:
            over[int(t, 16)] = None
        elif v[0] == "gbc":  # episode 7's own enemy (tools/content/gbc/new_enemies.json), by name
            over[int(t, 16)] = dict(episode="gbc", enemy=sorted(NEW_ENEMIES).index(v[1]) + 1,
                                    parts=4 if len(NEW_ENEMIES[v[1]]["parts"]) == 4 else 1)
        elif isinstance(v[1], list):
            over[int(t, 16)] = dict(episode=v[0], enemy=v[1][0][0], parts=v[1])
        else:
            over[int(t, 16)] = dict(episode=v[0], enemy=v[1], parts=v[2] if len(v) > 2 else 1)
    need, need_over = Counter(), Counter()
    for t, cs in cands.items():
        if over.get(t):
            need_over.update({b: use[t] for b in sheet(over[t])})
        elif t not in over:
            need.update({b: use[t] for b in sheet(cs[0])})
    banks = [b for b, _ in boss_banks.most_common()][:4]  # (the boss's all: its parts and launches show)
    for b, _ in need_over.most_common() + need.most_common():
        if len(banks) < 4 and b not in banks and b != 99:
            banks.append(b)
    for t, cs in cands.items():
        if t in over and over[t] is None:
            continue
        ok = ([over[t]] if over.get(t) and sheet(over[t]) <= set(banks) else []) + [c for c in cs if sheet(c) <= set(banks)]
        if ok:
            types[t] = (ok[0]['episode'], ok[0]['enemy'], EN.parts_key(ok[0].get('parts', 1)))
    json.dump(dict(banks=banks, types={f'{t:02x}': list(v) for t, v in types.items()}),  # (for review.py)
              open(os.path.join(GBC, 'enemies', f"L{spec['gbc']:02d}_chosen.json"), 'w'))
    ground = ground_enemies()
    # the clock: 1.5 x the GBC position along its map; what the GBC script does past the map's top
    # (while its boss's arena loops) is pressed into the time before the boss (at most clock 7000:
    # layer 1 runs out at 8148)
    p_map = d.get('map_px') or 16 * json.load(open(os.path.join(GBC, 'levels', [x for x in os.listdir(os.path.join(GBC, 'levels'))
                                                                          if x.startswith(f"L{spec['gbc']:02d}_")][0], 'map.json')))['rows']
    p_last = positions[-1] if positions else 0
    room = 7000 - 1.5 * p_map
    k = 1.5 if p_last <= p_map else max(0.0, min(1.5, room / max(1, p_last - p_map)))

    def clock(p):
        return round(1.5 * p) if p <= p_map else round(1.5 * p_map + (p - p_map) * k)
    sizes = {int(t): (info['size'][1], info['size'][0]) for t, info in d['types'].items() if info.get('size')}
    for name in NEW_ENEMIES:
        ground[("gbc", sorted(NEW_ENEMIES).index(name) + 1)] = NEW_ENEMIES[name]["layer"] == "ground"
    records, merged = pieces(records, positions, sizes)
    events = script.translate(records, positions, types, enemies_of, lambda k_: ground.get(k_[:2], False), clock=clock,
                              sizes=sizes)
    placements = []
    if boss:
        start = min(clock(p_last) if positions else 4000, 7000)
        placements.append(dict(kind='boss', episode=boss_source.episode, name=boss_source.name, start=start,
                               end=start + max([e['t'] for e in boss['events']] + [0])))
    review_enemies(spec['gbc'], types, use)
    print(f"  {len(records)} GBC records -> {len(events)} events, {len(types)}/{len(d['types'])} types as PC enemies, "
          f"sheets {banks}, boss {boss_source.name if boss else None}, {merged} pieces of others' enemies"
          + (f", spawns left out (type: count) {dict((f'{t:02x}', n) for t, n in use.items() if t not in types)}"
             if any(t not in types for t in use) else ''))
    return events, placements, banks


def make_level(spec):
    rows_gbc, img = gbc_level(spec['gbc'])
    gbc_map = rows_gbc['map']
    ep, pcname = spec['pc']
    src = [l for l in sources.original_levels() if l['episode'] == ep and l['name'] == pcname][0]
    letter = src['shapes']
    # the tiles follow their neighbours as these originals have them (the level's, and others of its look)
    names = [tuple(m) for m in spec.get('maps', [spec['pc']])]
    grids = [l['maps'][0] for l in sources.original_levels() if (l['episode'], l['name']) in names and l['shapes'] == letter]
    model = mapsynth.Model(grids, max_tiles=mapsynth.LAYER_TILES[0])
    tiles = preview.tiles(letter)
    pal = preview.palette()
    ids = sorted(model.count)
    layer1, n_rows = space(spec, img, grids, letter) if spec.get('space') else autotile(spec, img, grids, letter)
    maps = [layer1, [[0] * 14 for _ in range(600)], [[0] * 15 for _ in range(600)]]
    # events: the original's look at the start, no random enemies, the GBC script's enemies (with the
    # original's boss in place of the GBC one), the end
    look = waves.Source(ep, pcname)
    enemy_events, placements, banks = enemies(spec, look)
    # (its scroll speeds the GBC script's: event 2 at the start, backgrounds 2 and 3 with layer 1)
    events = [dict(e) for e in look.events if e['t'] == 0 and e['type'] in LOOK_EVENTS and e['type'] not in (2, 3)]
    if not any(x['t'] == 0 and x['type'] == 2 for x in enemy_events):
        events.insert(0, dict(t=0, type=2, d1=1, d2=1, d3=1, d5=0, d6=0, d4=0))
    for e in events:
        e.pop('adjust', None)
    events.append(dict(t=0, type=5, d1=(banks + [0] * 4)[0], d2=(banks + [0] * 4)[1], d3=(banks + [0] * 4)[2],
                       d5=0, d6=0, d4=(banks + [0] * 4)[3]))
    events.append(dict(t=0, type=13, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    events += enemy_events
    last = max([e['t'] for e in enemy_events] + [0])
    if not placements:
        end = min(8100, max(28 * (n_rows - 7) + 200, last + 600))
    else:
        # (with a boss, the end when it is gone is its block's; this one, as the originals have one
        # near 8100, ends the level if it never is, after the block's last event)
        end = max(8100, placements[0]['end'] + 600)
    events.append(dict(t=min(end, 65000), type=11, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    level = dict(name=spec['name'], song=level_song(ep, pcname), shapes=letter, maps=maps, events=events,
                 placements=placements, banks=banks, terrain=None, gbc=spec['gbc'], pc=[ep, pcname],
                 gbc_rows=len(gbc_map), pc_rows=n_rows, arcade=spec.get('arcade', False))
    # preview: the GBC map at 1.5x beside the PC map's playfield columns (2..12)
    pcimg = preview.picture([layer1[ROWS - n_rows:]], letter)
    g = Image.fromarray(img).resize((264, int(img.shape[0] * SCALE)), Image.NEAREST)
    pv = Image.new('RGB', (264 + 12 + pcimg.width, max(g.height, pcimg.height)))
    pv.paste(g, (0, pv.height - g.height))
    pv.paste(pcimg, (276, pv.height - pcimg.height))
    return level, pv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', help='GBC level numbers (default: all)')
    a = ap.parse_args()
    want = None if not a.levels else {int(x) for x in a.levels.split(',')}
    os.makedirs(os.path.join(OUT, 'levels'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'preview'), exist_ok=True)
    for i, spec in enumerate(LEVELS, 1):
        if want and spec['gbc'] not in want:
            continue
        level, pv = make_level(spec)
        slug = f"{i:02d}_L{spec['gbc']:02d}"
        json.dump(level, open(os.path.join(OUT, 'levels', slug + '.json'), 'w'))
        pv.save(os.path.join(OUT, 'preview', slug + '.png'))
    # the story (tools/gbc/story.py): a shop shows what the GBC game tells after the level before it
    # (the opening in the first shop); the ending is the GBC one
    story = json.load(open(os.path.join(GBC, 'story.json'))) if os.path.exists(os.path.join(GBC, 'story.json')) else None
    stages, pending = [], story['opening'] if story else []
    for i, s in enumerate(LEVELS, 1):
        st = dict(s, slug=f"{i:02d}_L{s['gbc']:02d}")
        st['cubes'], pending = pending, []
        if story and not s.get('arcade'):
            pending = story['after'].get(str(s['gbc']), [])
        stages.append(st)
    json.dump(dict(stages=stages, ending=story['ending'] if story else []),
              open(os.path.join(OUT, 'episode.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
