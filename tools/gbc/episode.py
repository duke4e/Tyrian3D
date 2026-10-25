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
    dict(gbc=11, name='SPACE', pc=(2, 'SOH JIN'), space=True, pool=[(1, 'SOH JIN'), (2, 'SOH JIN'), (2, 'GEM WAR'), (2, 'MARKERS'), (2, 'MISTAKES')]),
    dict(gbc=19, name='SAVARA', pc=(4, 'SAVARA IV'), pool=SAVARAS),
    dict(gbc=20, name='SAVARA II', pc=(1, 'SAVARA V'), pool=SAVARAS),
    dict(gbc=14, name='OASIS', pc=(4, 'SURFACE'), arcade=True, pool=DESERTS),
    dict(gbc=2, name='DESERT', pc=(4, 'DESERTRUN'), arcade=True, pool=DESERTS),
    dict(gbc=4, name='JUNGLE', pc=(2, 'TORM'), pool=JUNGLES),
    dict(gbc=8, name='JUNGLE II', pc=(2, 'TORM'), seed=2, pool=JUNGLES),
    dict(gbc=9, name='ASTEROID2', pc=(1, 'ASTEROID2'), pool=[(1, 'ASTEROID2'), (1, 'ASTEROID1'), (2, 'ASTCITY'), (3, 'AST. CITY')]),
    dict(gbc=13, name='WARP', pc=(3, 'STARGATE'), pool=[(3, 'STARGATE'), (1, 'BUBBLES')]),
    dict(gbc=12, name='BUBBLES', pc=(1, 'BUBBLES'), arcade=True, pool=[(1, 'BUBBLES'), (3, 'STARGATE')]),
    dict(gbc=15, name='CAMANIS', pc=(3, 'CAMANIS'), pool=ICES),
    dict(gbc=18, name='ICE EXIT', pc=(4, 'ICE EXIT'), maps=[(4, 'ICE EXIT'), (3, 'CAMANIS')], arcade=True, pool=ICES),
    dict(gbc=5, name='AST.BONUS', pc=(1, 'ASTEROID?'), pool=[(1, 'ASTEROID?'), (1, 'BONUS'), (2, 'BONUS')]),
    dict(gbc=10, name='SPACE ATK', pc=(4, 'SQUADRON'), space=True, pool=[(4, 'SQUADRON'), (1, 'ASSASSIN'), (4, 'DREAD-NOT')]),
    dict(gbc=21, name='FLEET', pc=(3, 'FLEET'), pool=[(3, 'FLEET')]),
    dict(gbc=17, name='DELIANI', pc=(4, 'BRAINIAC'), pool=[(4, 'BRAINIAC'), (1, 'DELIANI'), (3, 'New Deli')]),
    dict(gbc=22, name='TUNNEL', pc=(4, 'NOSE DRIP'), pool=[(4, '?TUNNEL?'), (4, 'NOSE DRIP'), (3, 'IXMUCANE')]),
    dict(gbc=1, name='DELICORE', pc=(1, 'DELIANI'), match=True, arcade=True, pool=DELIS),
    dict(gbc=16, name='DELI CORE', pc=(3, 'New Deli'), match=True, pool=DELIS),
    dict(gbc=6, name='LAVA I', pc=(4, 'LAVA EXIT'), pool=LAVAS),
    dict(gbc=7, name='LAVA II', pc=(4, 'LAVA RUN'), pool=LAVAS),
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
    regions off it: the originals' common tiles (ground rather than the objects on it), and where the
    originals have them, tiles that stand above the tile below and right of the one to the left."""
    from collections import Counter
    from scipy.cluster.vq import kmeans2
    import random
    rnd = random.Random(spec.get('seed', 1))
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
    layer1 = [[0] * 14 for _ in range(ROWS)]
    off = 0
    for r in range(ROWS - 1, -1, -1):
        for c in range(14):
            want = grid[n * r:n * r + n, n * c:n * c + n].ravel()
            miss = (sigs != want).sum(1)
            best = miss.min()
            off += best > 0
            cand = np.nonzero(miss <= best)[0]
            below = layer1[r + 1][c] if r + 1 < ROWS else None
            left = layer1[r][c - 1] if c > 0 else None
            w = []
            for i in cand:
                t = ids[i]
                w.append(weight[i] * (8.0 if below is not None and above.get(below, {}).get(t) else 1.0)
                         * (8.0 if left is not None and right.get(left, {}).get(t) else 1.0))
            layer1[r][c] = ids[cand[rnd.choices(range(len(cand)), w)[0]]]
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


def enemies(spec, look):
    """The GBC script (data/gbc/enemies, tools/gbc/enemies.py) as PC events (script.py), its enemies
    the PC ones found for its types; the boss the original level's (a placement); the sprite sheets
    they need (at most 4: the less used types take a candidate on the loaded ones)."""
    import script
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
    data = {}

    def enemies_of(e_):
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
    boss = look.boss()
    boss_banks = Counter()
    if boss:
        for e in boss['events']:
            if e['type'] in waves.SPAWNS and e['d1'] > 0:
                for k in range(4 if e['type'] == 12 else 1):
                    boss_banks.update(waves.sheets_of(look.enemies, e['d1'] + k))
    def sheet(c):
        """The sheets a candidate needs ({99}: none it can be drawn with, e.g. sheet 0)."""
        b = set().union(*(waves.sheets_of(enemies_of(c['episode']), c['enemy'] + k) for k in range(c.get('parts', 1))))
        return {99} if (0 in b or not b) else b
    need = Counter()
    for t, cs in cands.items():
        need.update({b: use[t] for b in sheet(cs[0])})
    banks = [b for b, _ in boss_banks.most_common()][:2]
    for b, _ in need.most_common():
        if len(banks) < 4 and b not in banks and b != 99:
            banks.append(b)
    for t, cs in cands.items():
        ok = [c for c in cs if sheet(c) <= set(banks)]
        if ok:
            types[t] = (ok[0]['episode'], ok[0]['enemy'], ok[0].get('parts', 1))
    # by-eye corrections (tools/gbc/enemy_overrides.json: "L23:29" -> [episode, enemy], or null to
    # leave a type out); their sheets join the loaded ones while there is room
    over = json.load(open(OVERRIDES)) if os.path.exists(OVERRIDES) else {}
    for key, v in over.items():
        lv, t = key.split(':')
        if int(lv[1:]) != spec['gbc']:
            continue
        t = int(t, 16)
        if v is None:
            types.pop(t, None)
            continue
        need_b = waves.sheets_of(enemies_of(v[0]), v[1])
        if need_b <= set(banks) or len(set(banks) | need_b) <= 4:
            banks += sorted(need_b - set(banks))
            types[t] = (v[0], v[1], v[2] if len(v) > 2 else 1)
    ground = ground_enemies()
    events = script.translate(records, positions, types, enemies_of, lambda k: ground.get(k[:2], False))
    placements = []
    if boss:
        start = round(1.5 * positions[-1]) if positions else 4000
        placements.append(dict(kind='boss', episode=look.episode, name=look.name, start=min(start, 7000)))
    review_enemies(spec['gbc'], types, use)
    print(f"  {len(records)} GBC records -> {len(events)} events, {len(types)}/{len(d['types'])} types as PC enemies, "
          f"sheets {banks}, boss {look.name if boss else None}")
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
    events = [dict(e) for e in look.events if e['t'] == 0 and e['type'] in LOOK_EVENTS
              and not (e['type'] in (2, 3) and any(x['t'] == 0 and x['type'] == 2 for x in enemy_events))]
    for e in events:
        e.pop('adjust', None)
    events.append(dict(t=0, type=5, d1=(banks + [0] * 4)[0], d2=(banks + [0] * 4)[1], d3=(banks + [0] * 4)[2],
                       d5=0, d6=0, d4=(banks + [0] * 4)[3]))
    events.append(dict(t=0, type=13, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    events += enemy_events
    if not placements:
        last = max([e['t'] for e in enemy_events] + [0])
        end = min(8100, max(28 * (n_rows - 7) + 200, last + 600))
        events.append(dict(t=end, type=11, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
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
