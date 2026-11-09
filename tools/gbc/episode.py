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
from collections import Counter
from fractions import Fraction

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
BANKS = 8  # sprite sheets a level loads at most (tyrian2.c: event 5 the first four, event 210 the others)
# Levels whose enemies fire less often than the GBC's (their guns' pace times this): with the GBC's hit points, fire
# and Easy rules (script.py event 203) these still cost the ship well over their PC originals on Easy (the autopilot
# in Arcade, TYR3D_LOG_BALANCE, damage a 1000 ticks: SAVARA 438 to SAVARA IV's 140, its boss's two pieces aiming
# 6-point shots every 2 ticks; JUNGLE 345 to TORM's 133, its boss's; DESERT 87 to DESERTRUN's 34; AST.BONUS 71 to
# ASTEROID?'s 33; SPACE ATK 154 to SQUADRON's 112). The factor brings their shots' damage down to what the original
# leaves after the collisions, at most 4 times (2026-10-29, the user: Easy is quite hard; take the ratios of the PC
# originals the GBC levels were made from).
FIRE_PACE = {'SAVARA': 4, 'JUNGLE': 3.5, 'DESERT': 2.8, 'AST.BONUS': 2, 'SPACE ATK': 1.8}
# Episode 7's own enemies (the GBC levels' that no PC level has; overrides name them ["gbc", name], or a composite of
# them ["gbc", [[name, dx, dy], ...]]): sheet W, shapeFile's 37th, or a look of a PC sheet no PC enemy has ("sheet":
# its sprite there; tools/content/gbc/build.py makes their records). Levels number them as the file lists them (from 1):
# new ones go at its end.
NEW_ENEMIES = json.load(open(os.path.join(ROOT, 'tools', 'content', 'gbc', 'new_enemies.json')))
NEW_SHEET = 37
SHAPE_FILE = "2478ABCDEFGHIJKLMNOPQRSTU5#V0@3^59'%W"  # (src/lvlmast.c shapeFile: a sheet's number is its place + 1)
SHEET_CHARS = {'x23': '#', 'x25': '%', 'x27': "'", 'x40': '@', 'x5e': '^'}  # (the sheets' names as models.cfg has them)


def own_index(name):
    """An own enemy's number in the levels (episode "gbc")."""
    return list(NEW_ENEMIES).index(name) + 1


def own_sheet(name):
    """The sheet an own enemy is drawn from: W, or the PC sheet of its look."""
    sheet = NEW_ENEMIES[name].get("sheet")
    return NEW_SHEET if sheet is None else SHAPE_FILE.index(SHEET_CHARS.get(sheet.lower(), sheet.upper())) + 1


def own_type(v):
    """An override ["gbc", name] or ["gbc", [[name, dx, dy], ...]] as a candidate (episode, enemy, parts)."""
    if isinstance(v[1], list):
        parts = [[own_index(nm), dx, dy] for nm, dx, dy in v[1]]
        return dict(episode="gbc", enemy=parts[0][0], parts=parts)
    return dict(episode="gbc", enemy=own_index(v[1]), parts=4 if len(NEW_ENEMIES[v[1]]["parts"]) == 4 else 1)
# autotile:
CAND_SLACK, CAND_MAX = 4, 72  # a cell's candidates: the tiles at most this many quarters further off its plan than its nearest
PRIOR_WEIGHT = 0.12   # a tile's cost per -log of its use against the most used one's (the originals' common tiles first)
EDGE_TILES = 2        # the tiles used at least this often that never stand beside themselves (shores' corners and edges)
PAIR_COST = 4.0       # a pair of tiles side by side or above each other that no original has, in quarters off the plan, ...
EDGE_NORM = 20.0      # ... times its edge's mismatch (Lab) over this, at most 1
RARE_COUNT = 0        # a pair the originals have fewer times than this costs PAIR_COST * RARE_COST for each it lacks ...
RARE_COST = 0.0       # ... of it (over RARE_COUNT): a platform cut straight off at a void (spec 'rare': (count, cost))
# (the levels the review of 2026-11-04 found odd joins in: docs/plans/2026-11-04-epizoda7-pregled.md; ASTEROID2's
# platforms cut off straight, LAVA II's river in pieces, TUNNEL's walls in ribs, ICE EXIT's river cut by panels)
RARE = (12, 0.6)
# (the levels the user found blocky, cut off or with stray tiles, 2026-11-05: edges, whole, and the joins as RARE or stricter)
REMADE = dict(edges=True, whole=True)
WHOLE_COST = 3.0      # (spec 'whole') an unseen pair with a piece of something in it, in PAIR_COSTs
BP_ITERATIONS = 60    # belief propagation over the map before it is bettered row by row
SIGMA = 0.15          # material mismatch (0-2, the quarters' shares) beyond a cell's nearest tile: weight 1/e
FORBID = 0.6          # ... and from where a tile is not taken
# backgrounds 2 and 3 (the GBC has one map; the PC originals' upper layers, made anew: upper_layers):
UPPER_SHAPE = ((600, 14), (600, 15))  # their rows and columns
UPPER_ROOM = (600 - 8 - 1) * 28  # pixels one scrolls from its start (row 592 at the screen's top) until it stops at row 1
UPPER_BLANK = 12      # rows left empty at the top: one that runs out repeats its top rows
UPPER_TRIES = 5       # attempts at an upper layer as full as its original

# The original levels whose enemies the GBC ones are first sought among (enemies.py: pool)
SAVARAS = [(1, 'SAVARA'), (1, 'SAVARA V'), (4, 'SAVARA IV'), (3, 'SAVARA Y')]
DESERTS = [(4, 'SURFACE'), (4, 'DESERTRUN'), (4, 'TIME WAR')]
JUNGLES = [(2, 'TORM'), (2, 'GYGES'), (2, 'BOTANY A'), (2, 'BOTANY B')]
ICES = [(3, 'CAMANIS'), (4, 'ICE EXIT'), (4, 'ICESECRET')]
DELIS = [(1, 'DELIANI'), (3, 'New Deli'), (4, 'UNDERDELI'), (4, 'CORE')]
LAVAS = [(4, 'LAVA EXIT'), (4, 'LAVA RUN'), (4, 'SIDE EXIT')]

# The bosses (boss=): the PC boss the GBC level's own looks like (tools/gbc/bosses.py: its sprites beside the PC bosses'
# bodies, picked by eye: the GBC game's are mostly the PC's made small, often another level's), else the original
# level's. gbc_boss=False: that PC boss whole, as its original has it (placed at the GBC boss's time), rather than the
# GBC boss's pieces drawn as its parts (the user's hand check, 2026-11-07: SAVARA II, DESERT, JUNGLE, CAMANIS, FLEET,
# DELIANI and TUNNEL looked wrong in pieces; SPACE ATK's too, in round 4). no_boss=True: none, where the GBC level has none (BUBBLES, AST.BONUS,
# DELICORE, LAVA I, FINALE: until 2026-11-07 they got an original's; JUNGLE II's GBC boss is its whole script).
# The episode in the GBC game's Full Game order (found by playing it through in the emulator), with the
# levels only its Arcade mode has (arcade) after one of their look. gbc: the GBC level (data/gbc/levels/Lnn_*); pc: the original level it
# is a version of (its tiles, look, song); layers: the original whose backgrounds 2 and 3 its own follow (else pc's:
# upper_layers); as_they_are: those of them taken as the original has them (the DELIs' pipes came out flat strips; FLEET's ships of many tiles came out of
# the synthesiser one in 150 rows, of seven); fills: how full those made are, where not as the original's (TYRIAN's
# clouds as full as its, 0.38, hid half the playfield in 3D, and over the boss fight, where the map stands).
LEVELS = [
    dict(gbc=23, name='TYRIAN', remake='corners', corner_maps=[(3, 'GAUNTLET')], corner_materials=5, corner_pair=8, corner_slack=2.0, mend=True, relay=dict(replace=(1, 29, 59, 81, 82, 83, 84, 85, 91, 92, 93, 94, 95, 104, 105, 117, 141, 142, 143), family=(96, 97, 98, 99, 100, 106, 107, 108, 109, 110, 118, 119, 120), source=[(4, 'NOSE DRIP'), (1, 'TYRIAN')]), pc=(1, 'TYRIAN'), fills={2: 0.15}, maps=[(1, 'TYRIAN'), (3, 'TYRIAN X'), (4, 'NOSE DRIP')], pool=[(1, 'TYRIAN'), (3, 'TYRIAN X')],
         boss=(1, 'ASSASSIN')),
    dict(gbc=3, name='ASTEROID', remake='autotile', replace={339: 372}, sides_keep=2.0, paths=dict(blocks=tuple(range(1, 15)), plain=372), pins={30: 339}, mend=True, mend_lock=(339, 340, 341, 342, 343, 347, 348, 351, 352, 353, 357, 359, 360, 366, 367, 368, 369, 370, 376, 377, 378, 379, 380, 386, 387, 388, 389, 390, 421, 424, 425, 426, 429), pc=(1, 'ASTEROID1'), pool=[(1, 'ASTEROID1'), (1, 'ASTEROID2'), (1, 'ASTEROID?')], boss=(1, 'ASTEROID2')),
    dict(gbc=11, name='SPACE', pc=(2, 'SOH JIN'), space=True, pool=[(1, 'SOH JIN'), (2, 'SOH JIN'), (2, 'GEM WAR'), (2, 'MARKERS'), (2, 'MISTAKES')], boss=(4, 'ICE EXIT')),
    dict(gbc=19, name='SAVARA', remake='autotile', maps=[(4, 'SAVARA IV'), (1, 'SAVARA'), (5, 'SAVARA')], materials=5, exclude=[17, 9, 19, 20, 10, 7, 27, 16, 18], pc=(4, 'SAVARA IV'), layers=(1, 'SAVARA V'), pool=SAVARAS, boss=(1, 'SAVARA V'), rare=RARE),
    dict(gbc=20, name='SAVARA II', remake='autotile', exclude=[17, 9, 19, 20, 10, 7, 27, 16, 18, 6, 8, 26, 28], blur=1.5, bottom_row=25, pc=(1, 'SAVARA V'), pool=SAVARAS, boss=(1, 'SAVARA'), gbc_boss=False, **REMADE),
    dict(gbc=14, name='OASIS', remake='corners', decor=[dict(tile=27, below=37, ids=(212, 222), tag='arch', **{'from': (4, 'DESERTRUN')})], corner_exclude=(11, 25, 26), templates=[([[35, 36, 37, 38, 39, 40], [33, 34, None, None, 41, 42]], [[27, 28, 29, 30, 1, 9, 10], [37, 38, 39, 40, 1, 19, 20]])], pc=(4, 'SURFACE'), arcade=True, pool=DESERTS, boss=(1, 'ASTEROID2')),
    dict(gbc=2, name='DESERT', remake='corners', decor=[dict(tile=27, below=37, ids=(212, 222), tag='arch', **{'from': (4, 'DESERTRUN')})], corner_exclude=(11, 25, 26), templates=[([[26, 27], [24, 25]], [[7, 8], [17, 18]]), ([[30, 31], [28, 29]], [[7, 8], [17, 18]]), ([[35, 36, 37, 38, 39, 40], [33, 34, None, None, 41, 42]], [[27, 28, 29, 30, None, 9, 10], [37, 38, 39, 40, None, 19, 20]])], pc=(4, 'DESERTRUN'), arcade=True, pool=DESERTS, boss=(4, 'SURFACE'), rare=RARE, gbc_boss=False, **REMADE),
    dict(gbc=4, name='JUNGLE', remake='jungle', jungle=dict(water=(1,), walls=tuple(range(30, 41)), turret=41, roads=tuple(range(15, 30))), pc=(2, 'TORM'), pool=JUNGLES, rare=RARE, gbc_boss=False, **REMADE),
    dict(gbc=8, name='JUNGLE II', remake='jungle', jungle=dict(water=(1,), walls=tuple(range(30, 41)), turret=41, roads=tuple(range(15, 30))), pc=(2, 'TORM'), seed=2, pool=JUNGLES, rare=RARE, **REMADE),
    dict(gbc=9, name='ASTEROID2', remake='corners', corner_pair=8, corner_slack=2.0, corner_exclude=(384, 380, 388, 390, 416, 417, 418, 339, 419, 400, 59, 378), pc=(1, 'ASTEROID2'), pool=[(1, 'ASTEROID2'), (1, 'ASTEROID1'), (2, 'ASTCITY'), (3, 'AST. CITY')],
         boss=(1, 'ASTEROID1'), rare=(12, 1.0), **REMADE),
    dict(gbc=13, name='WARP', remake='fitted', maps=[(1, 'BUBBLES')], pc=(3, 'STARGATE'), space=True, stars=True, pool=[(3, 'STARGATE'), (1, 'BUBBLES')],
         boss=(1, 'ASSASSIN')),
    dict(gbc=12, name='BUBBLES', remake='fitted', pc=(1, 'BUBBLES'), arcade=True, pool=[(1, 'BUBBLES'), (3, 'STARGATE')], no_boss=True),
    dict(gbc=15, name='CAMANIS', remake='autotile', pc=(3, 'CAMANIS'), pool=ICES, gbc_boss=False),
    dict(gbc=18, name='ICE EXIT', remake='autotile', pc=(4, 'ICE EXIT'), maps=[(4, 'ICE EXIT'), (3, 'CAMANIS')], arcade=True, pool=ICES, boss=(4, 'DREAD-NOT'),
         rare=(5, 0.25), **REMADE),
    dict(gbc=5, name='AST.BONUS', pc=(1, 'ASTEROID?'), pool=[(1, 'ASTEROID?'), (1, 'BONUS'), (2, 'BONUS')], no_boss=True,
         gbc_boss=False),
    dict(gbc=10, name='SPACE ATK', pc=(4, 'SQUADRON'), space=True, pool=[(4, 'SQUADRON'), (1, 'ASSASSIN'), (4, 'DREAD-NOT')], boss=(4, 'APPROACH'), gbc_boss=False),
    dict(gbc=21, name='FLEET', remake='ships', pc=(3, 'FLEET'), as_they_are=(3,), pool=[(3, 'FLEET')], gbc_boss=False),
    dict(gbc=17, name='DELIANI', remake='corners', block_like={b: 537 for b in (0, 1, *range(3, 23))}, block_like_inner=True, corner_repair=True, corner_repair_finish=True, upper_stamps=dict(layer=3, source=(1, 'DELIANI'), blocks=tuple(range(14, 23))), upper_pace=[None, 1], upper_clear=[2], corner_materials=2, replace={592: 500}, corner_exclude=(497, 287, 288, 289), corner_no_blank=True, pc=(4, 'BRAINIAC'), tiles=(1, 'DELIANI'), layers=(1, 'DELIANI'), pool=[(4, 'BRAINIAC'), (1, 'DELIANI'), (3, 'New Deli')], boss=(1, 'DELIANI'), rare=RARE, gbc_boss=False),
    dict(gbc=22, name='TUNNEL', pc=(4, 'NOSE DRIP'), pool=[(4, '?TUNNEL?'), (4, 'NOSE DRIP'), (3, 'IXMUCANE')], boss=(3, 'IXMUCANE'), rare=RARE, gbc_boss=False),
    dict(gbc=1, name='DELICORE', remake='corners', corner_exclude=tuple(t for t in range(1, 100) if t != 21), corner_pair=8, corner_slack=2.0, corner_repair=True, corner_repair_miss=4, corner_repair_finish=True, tiles=(4, 'BRAINIAC'), layers=(4, 'BRAINIAC'), pc=(1, 'DELIANI'), match=True, arcade=True, pool=DELIS, rare=RARE, as_they_are=(2, 3), no_boss=True),
    dict(gbc=16, name='DELI CORE', remake='exact', exact=dict(blocks=tuple(b for b in range(24) if b != 10), family=(71, 72, 73, 74, 81, 83, 84, 85, 91, 92, 93, 94, 95), sides={95: 'NW', 94: 'NE', 85: 'SW', 84: 'SE', 92: 'N', 72: 'S', 83: 'W', 81: 'E', 74: '', 71: '', 73: '', 91: '', 93: ''}, inner={0: 93, 2: 91, 5: 73, 7: 71}, edges={'N': 92, 'S': 72, 'W': 83, 'E': 81, 'NW': 95, 'NE': 94, 'SW': 85, 'SE': 84}, rare=6, fill=82, objects={15: 75, 16: 76, 17: 77, 18: 86, 19: 87, 20: 82, 21: 82, 22: 82, 23: 82}, runs={(20, 21, 22, 23): ((82, 78, 79, 80), (78, 79, 80, 82))}), ninepatch=dict(blocks=tuple(b for b in range(24) if b != 10), patch=(95, 92, 94, 83, 74, 81, 85, 72, 84), fill=82), corner_materials=3, block_like={10: 82, 0: 74, 1: 74}, corner_fill=(74,), corner_own_only=True, corner_repair=True, tiles=(4, 'UNDERDELI'), layers=(4, 'UNDERDELI'), pc=(3, 'New Deli'), match=True, pool=DELIS, boss=(4, 'DREAD-NOT'), rare=RARE, as_they_are=(2, 3)),
    dict(gbc=6, name='LAVA I', pc=(4, 'LAVA EXIT'), pool=LAVAS, no_boss=True),
    dict(gbc=7, name='LAVA II', pc=(4, 'LAVA RUN'), pool=LAVAS, boss=(4, 'CORE'), rare=RARE),
    dict(gbc=24, name='FINALE', pc=(4, 'DREAD-NOT'), space=True, pool=[(4, 'DREAD-NOT'), (4, 'APPROACH')], no_boss=True),
]


def spec_of(gbc):
    """The LEVELS entry of a GBC level."""
    return next(s for s in LEVELS if s['gbc'] == gbc)


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


def object_tiles(letter):
    """The tile set's object tiles as make_cleanground.py learns them from the originals' logged objects (cached
    in data/gbc/cache/object_tiles.json while the ground log and cleanground.json stay as they were)."""
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'terrain'))
    import make_cleanground as mc
    path = os.path.join(GBC, 'cache', 'object_tiles.json')
    stamp = [os.path.getmtime(f) if os.path.exists(f) else 0 for f in (mc.mt.GROUND, mc.OVERRIDES)]
    cache = json.load(open(path)) if os.path.exists(path) else {}
    if cache.get('stamp') != stamp:
        cache = dict(stamp=stamp, tiles={})
    if letter not in cache['tiles']:
        cache['tiles'][letter] = sorted(mc.tileset_object_tiles(letter))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(cache, open(path, 'w'))
    return set(cache['tiles'][letter])


def pair_costs(spec, ids, right, above, selfish, tiles, pal):
    """What each pair of tiles costs side by side ([left, right]) and one above the other ([below, above]): nothing (or a
    little if rare) where the originals pair them, else how badly their edges join; and the seen and mismatch tables."""
    T = len(ids)
    idx = {t: i for i, t in enumerate(ids)}
    seen_h = np.zeros((T, T), bool)  # [left, right]
    seen_v = np.zeros((T, T), bool)  # [below, above]
    count_h = np.zeros((T, T))
    count_v = np.zeros((T, T))
    for a_, cnt in right.items():
        for b_, c_ in cnt.items():
            if a_ in idx and b_ in idx:
                seen_h[idx[a_], idx[b_]] = True
                count_h[idx[a_], idx[b_]] = c_
    for a_, cnt in above.items():
        for b_, c_ in cnt.items():
            if a_ in idx and b_ in idx:
                seen_v[idx[a_], idx[b_]] = True
                count_v[idx[a_], idx[b_]] = c_
    # (how badly an unseen pair's edge joins: the step in colour across it beyond the steps just inside either tile,
    # per pixel along it; two grasses join, grass beside the sea doesn't)
    tl = np.stack([lab(pal[tiles[t]].astype(np.float64)) if tiles.get(t) is not None else lab(np.zeros((28, 24, 3)))
                   for t in ids])

    def mismatch(a_edge, a_in, b_edge, b_in):
        d = np.linalg.norm(a_edge[:, None] - b_edge[None, :], axis=-1)
        g = (np.linalg.norm(a_edge - a_in, axis=-1)[:, None] + np.linalg.norm(b_edge - b_in, axis=-1)[None, :]) / 2
        return np.maximum(0, d - g).mean(-1)
    mis_h = mismatch(tl[:, :, -1], tl[:, :, -2], tl[:, :, 0], tl[:, :, 1])   # [left, right]
    mis_v = mismatch(tl[:, 0], tl[:, 1], tl[:, -1], tl[:, -2])               # [below, above]
    # (a pair the originals have only a few times costs a little too, as much more as it is rarer: ASTEROID2's
    # platforms cut straight off at the void, a join its originals have at a few edges, where they have rocky rims)
    rare_count, rare_cost = spec.get('rare', (RARE_COUNT, RARE_COST))
    rare_h = rare_cost * np.clip(1 - count_h / max(rare_count, 1), 0, 1) if rare_count else 0.0
    rare_v = rare_cost * np.clip(1 - count_v / max(rare_count, 1), 0, 1) if rare_count else 0.0
    # (and a pair they never have at least as much as the rarest they have)
    unseen_least = rare_cost if rare_count else 0.0
    cost_h = np.where(seen_h, rare_h, np.maximum(unseen_least, np.minimum(1.0, mis_h / EDGE_NORM)))
    cost_v = np.where(seen_v, rare_v, np.maximum(unseen_least, np.minimum(1.0, mis_v / EDGE_NORM)))
    # (spec 'whole': a tile that never stands beside itself, a piece of something, beside one the originals never put it
    # beside costs WHOLE_COST: DESERT's stumps came out of the halves of two, JUNGLE's cliffs of pieces of others)
    if spec.get('whole'):
        piece = np.array([selfish[t] == 0 for t in ids])
        either = piece[:, None] | piece[None, :]
        cost_h = np.where(~seen_h & either, WHOLE_COST, cost_h)
        cost_v = np.where(~seen_v & either, WHOLE_COST, cost_v)
    return cost_h, cost_v, seen_h, seen_v, mis_h, mis_v


def solve_grid(cands, unary, cost_h, cost_v, T, pair=None):
    """The map's tiles (indices) from each cell's candidates and their costs (cands, unary: ROWS x 14 lists of arrays) and
    the pair costs ([left, right], [below, above]): min-sum belief propagation over the whole grid, its best tiles then
    bettered row by row (Viterbi along each row given the rows below and above it)."""
    PAIR = PAIR_COST if pair is None else pair
    choice = None

    def solve_row(r):
        """The best row r for its neighbours below and above: Viterbi along the row."""
        costs = []
        for c in range(14):
            u = unary[r][c].copy()
            ci = cands[r][c]
            if r + 1 < ROWS:
                u += PAIR * cost_v[choice[r + 1][c], ci]
            if r > 0:
                u += PAIR * cost_v[ci, choice[r - 1][c]]
            costs.append(u)
        acc, back = costs[0], []
        for c in range(1, 14):
            pair = PAIR * cost_h[np.ix_(cands[r][c - 1], cands[r][c])]  # (prev, cur)
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
    # the whole map at once: min-sum belief propagation over the grid, its best tiles then bettered row by row (row by
    # row alone can't change two rows together, which a shore needs, and gave the plan up for strips)
    U = np.full((ROWS, 14, T), 1e6, np.float32)
    for r in range(ROWS):
        for c in range(14):
            U[r, c, cands[r][c]] = unary[r][c]
    H = (PAIR * cost_h).astype(np.float32)   # [left, right]
    V = (PAIR * cost_v).astype(np.float32)   # [below, above]
    fl, fr, fb, fa = (np.zeros((ROWS, 14, T), np.float32) for _ in range(4))  # into a cell from its left, right, below, above
    for _ in range(BP_ITERATIONS):
        b = U + fl + fr + fb + fa
        nl, nr, nb, na = (np.zeros_like(fl) for _ in range(4))
        nl[:, 1:] = ((b - fr)[:, :-1, :, None] + H).min(2)
        nr[:, :-1] = ((b - fl)[:, 1:, None, :] + H).min(3)
        nb[:-1] = ((b - fa)[1:, :, :, None] + V).min(2)
        na[1:] = ((b - fb)[:-1, :, None, :] + V).min(3)
        for m, new in ((fl, nl), (fr, nr), (fb, nb), (fa, na)):
            new -= new.min(-1, keepdims=True)
            m *= 0.5
            m += 0.5 * new
    best = (U + fl + fr + fb + fa).argmin(-1)
    choice = [[int(best[r, c]) for c in range(14)] for r in range(ROWS)]
    for _ in range(3):
        for r in list(range(ROWS)) + list(range(ROWS - 1, -1, -1)):
            solve_row(r)
    return choice


def autotile(spec, img, grids, letter):
    """Layer 1 from the GBC map by materials. The materials are the tile set's main colours (k-means of
    the used tiles' region means, weighted by use); a tile's signature is the materials of its n x n
    regions; the GBC map (spec 'match': its colours moved to the tile set's first), cut into the PC
    tiles' regions, gives each cell the signature it wants, and the cell takes a tile with the fewest
    regions off it: the originals' common tiles (ground and its shores rather than the objects on it), paired
    with their neighbours as the originals pair them or as their edges join (over the whole map: belief
    propagation, then row by row)."""
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
    # (and not the tiles of objects: tools/terrain/make_cleanground.py erases every copy of those, a stand-in
    # on it; GBC DELIANI's pod tile as fill made strips of 2364)
    objects = object_tiles(letter)
    # (and the shores' corners and edges, which never stand beside themselves either: without them an island
    # was cut off square, the sea straight beside the grass)
    # (and not those the level's spec leaves out: DESERT's stumps came out of halves of two, the user: "mali otok s odrezanim
    # tileovima")
    ground = [t for t, _ in use.most_common() if (use[t] >= EDGE_TILES or selfish[t] >= 1) and t not in objects and
              t not in spec.get('exclude', ())]
    ids = ground[:mapsynth.LAYER_TILES[0]]  # (a layer's limit)
    rmean = {}
    for t in ids:
        im = tiles.get(t)
        rmean[t] = lab(regions(np.zeros((28, 24, 3)) if im is None else pal[im].astype(np.float64), n))
    k = spec.get('materials', 4)
    # (each tile as often as the originals have it, a few thousand in all: a rare one can't make a material of its own,
    # CAMANIS's dashed plate taking its plateaus from the cobbles)
    total = sum(use[t] for t in ids)
    sample = np.concatenate([rmean[t].reshape(-1, 3) for t in ids for _ in range(max(1, round(3000 * use[t] / total)))])
    centres, _ = kmeans2(sample, k, minit='++', seed=spec.get('seed', 1))

    def material(v):
        return ((v[..., None, :] - centres) ** 2).sum(-1).argmin(-1)
    sigs = np.array([material(rmean[t]).ravel() for t in ids])  # (T, n*n)
    weight = np.array([use[t] for t in ids], np.float64) ** 2
    # (aligned: each PC cell one GBC metatile, the GBC map's columns in the PC's 2..12, a PC row a GBC row: the layout
    # 1:1, the map 28/24 times as long as at 1.5x; else the GBC map 1.5x, a cell 16 x 18.67 GBC pixels from x -38)
    aligned = spec.get('aligned', False)
    x_off = 32 if aligned else 38
    n_rows = img.shape[0] // 16 if aligned else int(round(img.shape[0] * SCALE / 28))
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
    rh, rw = (16 / n if aligned else 28 / n / SCALE), 24 / n / SCALE
    grid = np.zeros((ROWS * n, 14 * n), int)
    loop = 8 * n  # the loop at the top: the map's top 8 rows
    for r in range(ROWS * n):
        b = ROWS * n - 1 - r
        if b >= n_rows * n:
            b = n_rows * n - loop + (b - n_rows * n) % loop
        y1 = h - b * rh
        ys = np.clip(np.arange(int(round(y1 - rh)), max(int(round(y1)), int(round(y1 - rh)) + 1)), 0, h - 1)
        for c in range(14 * n):
            x0 = rw * c - x_off
            xs = np.clip(np.arange(int(round(x0)), max(int(round(x0 + rw)), int(round(x0)) + 1)), 0, g.shape[1] - 1)
            grid[r, c] = material(g[ys][:, xs].reshape(-1, 3).mean(0))
    # (the columns beyond the GBC map's sides, the wide playfield's: as its nearest one inside it, not its edge's pixels
    # repeated: SAVARA II's right edge, a frame's grey there, got a column of grey wall, the user: "tileovi koji nebi
    # trebali biti tu")
    if spec.get('edges'):
        inside = [c for c in range(14 * n) if rw * c - x_off >= 0 and rw * (c + 1) - x_off <= g.shape[1]]
        for c in range(14 * n):
            if c not in inside:
                grid[:, c] = grid[:, min(inside, key=lambda i: abs(i - c))]
    # each cell's candidates: the tiles nearest its plan (and a few quarters further); the map is then the
    # choice that misses the plan least and pairs its tiles as the originals pair them (beside and above
    # each other: an edge that joins up, a texture that goes on) or else as their edges join
    T = len(ids)
    cost_h, cost_v, seen_h, seen_v, mis_h, mis_v = pair_costs(spec, ids, right, above, selfish, tiles, pal)
    prior = -np.log(np.array([use[t] for t in ids], np.float64) / max(use[t] for t in ids))
    MISS, PAIR, PRIOR = 1.0, PAIR_COST, PRIOR_WEIGHT
    cands, unary = [], []
    off = 0
    for r in range(ROWS):
        row_c, row_u = [], []
        for c in range(14):
            want = grid[n * r:n * r + n, n * c:n * c + n].ravel()
            miss = (sigs != want).sum(1)
            best = miss.min()
            off += best > 0
            ci = np.nonzero(miss <= best + CAND_SLACK)[0]
            if len(ci) > CAND_MAX:
                ci = ci[np.argsort(miss[ci] * 10 + prior[ci])[:CAND_MAX]]
            row_c.append(ci)
            row_u.append(MISS * miss[ci] + PRIOR * prior[ci])
        cands.append(row_c)
        unary.append(row_u)
    choice = solve_grid(cands, unary, cost_h, cost_v, T)
    layer1 = [[ids[choice[r][c]] for c in range(14)] for r in range(ROWS)]
    pairs = [(seen_h, mis_h, choice[r][c - 1], choice[r][c]) for r in range(ROWS) for c in range(1, 14)] + \
        [(seen_v, mis_v, choice[r + 1][c], choice[r][c]) for r in range(ROWS - 1) for c in range(14)]
    bad = sum(not seen[a_, b_] for seen, _, a_, b_ in pairs)
    badly = sum(not seen[a_, b_] and mis[a_, b_] > 12 for seen, mis, a_, b_ in pairs)
    missed = sum(int((sigs[choice[r][c]] != grid[n * r:n * r + n, n * c:n * c + n].ravel()).sum())
                 for r in range(ROWS) for c in range(14))
    print(f'  {bad} pairs of tiles the originals never put together, {badly} of them badly joined; {missed} regions off '
          f'the plan')
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


def enemies(spec, look, banks_given=None, types_given=None):
    """The GBC script (data/gbc/enemies, tools/gbc/enemies.py) as PC events (script.py), its enemies
    the PC ones found for its types; the boss the original level's (a placement); the sprite sheets
    they need (at most BANKS: the less used types take a candidate on the loaded ones). banks_given, types_given:
    these sheets and (some) types' PC enemies instead of those found (retype.py)."""
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
    # the GBC boss (boss_rom.py, boss.py): the script from its first spawn on is its, translated apart
    import boss as BOSS
    bd = BOSS.load(spec['gbc']) if spec.get('gbc_boss', True) else None
    if bd:
        records, positions = records[:bd['first']], positions[:bd['first']]
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
    boss = None if spec.get('no_boss') else boss_source.boss()  # (no_boss: none where the GBC level has none)
    boss_banks = Counter()
    if boss:
        for e in boss['events']:
            if e['type'] in waves.SPAWNS and e['d1'] > 0:
                for k in range(4 if e['type'] == 12 else 1):
                    boss_banks.update(waves.sheets_of(boss_source.enemies, e['d1'] + k))
    def sheet(c):
        """The sheets a candidate needs ({99}: none it can be drawn with, e.g. sheet 0)."""
        if c['episode'] == "gbc":
            # (a 4-part one is one of them: its parts are its own; a composite's parts are each one)
            parts = c.get('parts', 1)
            names = list(NEW_ENEMIES)
            return {own_sheet(names[n - 1]) for n in ([c['enemy']] if isinstance(parts, int) else [p[0] for p in parts])}
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
        elif v[0] == "gbc":  # episode 7's own enemy (tools/content/gbc/new_enemies.json), by name, or a composite
            over[int(t, 16)] = own_type(v)
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
    banks = [b for b, _ in boss_banks.most_common()][:BANKS]  # (the boss's all: its parts and launches show)
    for b, _ in need_over.most_common() + need.most_common():
        if len(banks) < BANKS and b not in banks and b != 99:
            banks.append(b)
    if banks_given is not None:
        banks = list(banks_given)
    for t, cs in cands.items():
        if t in over and over[t] is None:
            continue
        ok = ([over[t]] if over.get(t) and sheet(over[t]) <= set(banks) else []) + [c for c in cs if sheet(c) <= set(banks)]
        if ok:
            types[t] = (ok[0]['episode'], ok[0]['enemy'], EN.parts_key(ok[0].get('parts', 1)))
    types.update(types_given or {})
    json.dump(dict(banks=banks, types={f'{t:02x}': list(v) for t, v in types.items()}),  # (for review.py)
              open(os.path.join(GBC, 'enemies', f"L{spec['gbc']:02d}_chosen.json"), 'w'))
    ground = ground_enemies()
    # the clock: 1.5 x the GBC position along its map; what the GBC script does past the map's top
    # (while its boss's arena loops) is pressed into the time before the boss (at most clock 7000:
    # layer 1 runs out at 8148)
    p_map = d.get('map_px') or 16 * json.load(open(os.path.join(GBC, 'levels', [x for x in os.listdir(os.path.join(GBC, 'levels'))
                                                                          if x.startswith(f"L{spec['gbc']:02d}_")][0], 'map.json')))['rows']
    p_last = positions[-1] if positions else 0
    if bd:
        # (the boss's stretch while the map still moves: up to its stop)
        p_last = max(p_last, bd['positions'][(bd['stop'] if bd['stop'] is not None else bd['loop'][1]) - bd['first']])
    room = 7000 - 1.5 * p_map
    k = 1.5 if p_last <= p_map else max(0.0, min(1.5, room / max(1, p_last - p_map)))

    def clock(p):
        return round(1.5 * p) if p <= p_map else round(1.5 * p_map + (p - p_map) * k)
    sizes = {int(t): (info['size'][1], info['size'][0]) for t, info in d['types'].items() if info.get('size')}
    for name in NEW_ENEMIES:
        ground[("gbc", own_index(name))] = NEW_ENEMIES[name]["layer"] == "ground"
    records, merged = pieces(records, positions, sizes)
    # the types' start speeds (the type table's bytes 3 and 4: script.py; its place from enemies.py --tables)
    if 'types_at' not in d:
        raise SystemExit(f"L{spec['gbc']:02d}.json: no types_at (tools/gbc/enemies.py --tables)")
    starts = {t: (rom[ro(d['types_at'] + 10 * t + 3)], rom[ro(d['types_at'] + 10 * t + 4)]) for t in range(100)}
    stats = {t: tuple(rom[ro(d['types_at'] + 10 * t + k)] for k in (1, 5, 6)) for t in range(100)}
    tr = script.Translator(types, enemies_of, lambda k_: ground.get(k_[:2], False), sizes=sizes, starts=starts,
                           stats=stats)
    tr.pace = FIRE_PACE.get(spec['name'], 1)
    events = script.translate(records, positions, types, enemies_of, None, clock=clock, translator=tr)
    placements = []
    gbc_boss = None
    if bd:
        # (what its pieces launch: the type's PC enemy, a composite's first part; one only launched, never spawned by
        # the script: boss_rom.py found it by its looks)
        launchable = {t: (v[0], v[1]) for t, v in types.items() if v[0] != 'gbc'}
        # (of the candidates those on the level's sheets: a launched enemy whose sheet isn't loaded has no sprite)
        for t, v in bd.get('launched', {}).items():
            ok = [c for c in v['candidates'] if sheet(c) <= set(banks)]
            if ok:
                launchable.setdefault(int(t, 16), (ok[0]['episode'], ok[0]['enemy']))
        for t, info in d['types'].items():  # (a type left out of the script's: its best candidate)
            ok = [c for c in info.get('candidates', []) if sheet(c) <= set(banks)]
            if ok:
                launchable.setdefault(int(t), (ok[0]['episode'], ok[0]['enemy']))
        b = BOSS.Boss(spec['gbc'], bd, tr, clock, boss_source, launchable)
        events += b.translate()
        events.sort(key=lambda e: e['t'])
        gbc_boss = dict(start=min((e['t'] for e in b.events), default=0), records=b.records, guns=b.guns, notes=b.notes,
                        looks=[[u['type'], u['group'], list(lk) if lk else None] for u, lk in zip(b.units, b.looks)])
        print(f"  GBC boss: {len(b.units)} pieces in groups {sorted(b.groups)} as {boss_source.name}'s parts, "
              f"{len(b.guns)} guns, {len(b.events)} events" + (f"; {'; '.join(dict.fromkeys(b.notes))}" if b.notes else ''))
    elif boss:
        start = min(clock(p_last) if positions else 4000, 7000)
        placements.append(dict(kind='boss', episode=boss_source.episode, name=boss_source.name, start=start,
                               end=start + max([e['t'] for e in boss['events']] + [0])))
    review_enemies(spec['gbc'], types, use)
    print(f"  {len(records)} GBC records -> {len(events)} events, {len(types)}/{len(d['types'])} types as PC enemies, "
          f"sheets {banks}, boss {boss_source.name if boss else None}, {merged} pieces of others' enemies"
          + (f", spawns left out (type: count) {dict((f'{t:02x}', n) for t, n in use.items() if t not in types)}"
             if any(t not in types for t in use) else ''))
    return events, placements, banks, gbc_boss


DROP_REACH = 120  # an original's drop reaches the enemies of its link that came this many ticks before it
GROUP_GAP = 90    # a GBC group: its link's enemies, each come at most this many ticks after the one before
_enemy_data = {}


def enemy_data(ep, n):
    """A PC enemy's record (None for the episode's own)."""
    if not isinstance(ep, int):
        return None
    if ep not in _enemy_data:
        _enemy_data[ep] = sources.tyrdata.load_items(ep)['enemies']
    return _enemy_data[ep].get(n)


def with_drops(events, look, placements, pool=(), gbc_boss=None):
    """The pickups (the purple balls that power up the guns in Arcade, the guns of the arcade modes, coins): the
    original level's drops (events 33 and 45: what the enemies of a link leave when shot down) in its order and
    at its pace, and as many: each reaches as many enemies as it did in the original (its link's, DROP_REACH),
    given to the GBC groups that come nearest the same share of the way to the boss (after a group's last enemy,
    by its link, so that the whole group carries it), as many as it takes. (The GBC game has none of its own: its
    script has no such command. A drop given to one GBC enemy each left the arcade with a third of the
    originals' purple balls: SAVARA V's waves of 17 planes, each leaving one.) Not the originals' data cubes (the
    GBC story's are the episode's own) nor their warp orbs (secret levels); not to a group that can't be shot
    down. An original with none (DESERTRUN): the first level of its pool with some."""
    def drops_of(src):
        # (and not the secret levels' warp orbs, value 10000 + the section they jump to: not this episode's)
        en = src.enemies
        return [e for e in src.events if e['type'] in (33, 45) and e['t'] < 60000 and e['d1'] not in (512, 513)
                and not 10000 <= en.get(e['d1'], {}).get('value', 0) < 20000]
    orig = drops_of(look)
    for m in pool:
        if orig:
            break
        look = waves.Source(*m)
        orig = drops_of(look)
    # (a GBC boss's loop that is the whole level, JUNGLE II's: over its groups, not its pieces, on links 101 and up)
    whole = gbc_boss is not None and gbc_boss['start'] < 600
    spawns = [i for i, e in enumerate(events) if e['type'] in (6, 7, 10, 12, 15) and e.get('d4') and 'ep' in e
              and e['ep'] != 'boss' and e['d4'] < 101 and (gbc_boss is None or whole or e['t'] < gbc_boss['start'])]
    if not orig or not spawns:
        return events

    def pieces(e):
        return 4 if e['type'] == 12 else 1

    def reach(d):
        return max(1, sum(pieces(e) for e in look.events if e['type'] in waves.SPAWNS and e['d4'] == d['d4']
                          and d['t'] - DROP_REACH <= e['t'] <= d['t']))

    def can_die(e):
        data = [enemy_data(e['ep'], e['d1'] + k) for k in range(pieces(e))]
        return any(d is None or d['armor'] < 254 for d in data)
    # the GBC groups: [the indices of a link's spawns], each GROUP_GAP at most after the one before
    groups, last = [], {}
    for i in spawns:
        g = last.get(events[i]['d4'])
        if g is None or events[i]['t'] - events[g[-1]]['t'] > GROUP_GAP:
            g = last[events[i]['d4']] = []
            groups.append(g)
        g.append(i)
    groups = [g for g in groups if any(can_die(events[i]) for i in g)]
    b = look.boss()
    end_o = max(e['t'] for e in look.events if e['t'] < 60000)
    # (a boss block found at the start, as CAMANIS's and LAVA EXIT's, isn't where the level ends: every drop after
    # it went to the GBC level's last groups, and most found none free)
    span_o = b['start'] if b and b['start'] > end_o / 2 else end_o
    span_g = (placements[0]['start'] if placements else gbc_boss['start'] if gbc_boss and not whole
              else max(events[i]['t'] for i in spawns))
    size = [sum(pieces(events[i]) for i in g) for g in groups]
    used, after = set(), {}
    for e in orig:
        want = min(1.0, e['t'] / max(1, span_o)) * span_g
        need = reach(e)
        while need > 0:
            free = [k for k in range(len(groups)) if k not in used]
            if not free:
                break
            # (the nearest, a group bigger than the drop needs as if a little further for each enemy too many; in it,
            # after the enemy that makes up the number, so that those before carry it and not the rest: a gun given
            # to all of a group of 17 gave 17)
            k = min(free, key=lambda k: (abs(events[groups[k][-1]]['t'] - want) + GROUP_GAP / 3 * max(0, size[k] - need), k))
            used.add(k)
            n = 0
            for i in groups[k]:
                n += pieces(events[i])
                if n >= need:
                    break
            need -= n
            # (533 and 534 are the game's own codes, a random special weapon: as they are, episode 5's numbers)
            after.setdefault(i, []).append(dict(e, t=events[i]['t'], d4=events[i]['d4'],
                                                ep=5 if e['d1'] in (533, 534) else look.episode))
    out = []
    for i, e in enumerate(events):
        out.append(e)
        out += after.get(i, [])
    return out


def fill(grid):
    """The share of a map's cells that aren't empty (tile 0)."""
    return sum(1 for row in grid for t in row if t) / max(1, len(grid) * len(grid[0]))


def as_it_is(m, rows, columns):
    """An original's upper layer as it is, rows x columns, its top rows left empty (UPPER_BLANK)."""
    grid = [list(row[:columns]) + [0] * (columns - len(row)) for row in m[-rows:]]
    return [[0] * columns for _ in range(UPPER_BLANK)] + grid[UPPER_BLANK:]


def layer_ratios(src):
    """How fast an original's backgrounds 2 and 3 scroll against layer 1: for each the ratio it keeps longest while
    both move (1 where it never moves with layer 1: BRAINIAC's background 2 stands while the level runs)."""
    scroll = sorted((e for e in src.events if e['type'] in (2, 30) and e['t'] < 60000), key=lambda e: e['t'])
    out = []
    for k in ('d2', 'd3'):
        held = Counter()
        for a, b in zip(scroll, scroll[1:] + [None]):
            if a['d1'] > 0 and a[k] > 0:
                held[Fraction(a[k], a['d1'])] += (b['t'] if b else a['t'] + 1000) - a['t']
        out.append(held.most_common(1)[0][0] if held else Fraction(1))
    return out


def upper_layers(spec, letter):
    """Backgrounds 2 and 3 made anew from the original's (spec's layers, else its pc; the GBC has one map): each that
    is more than one tile's filler or a sign at the start (3 tiles or more, 100 placed, over 30 rows) by the
    synthesiser from the stretch it fills (SAVARA V's clouds only round its start: here all along), its top rows left
    empty; None for one that isn't. With how fast each scrolls against layer 1 (layer_ratios)."""
    ep, name = spec.get('layers', spec['pc'])
    src = [l for l in sources.original_levels() if l['episode'] == ep and l['name'] == name and l['shapes'] == letter][0]
    out = []
    for k, (rows, columns) in ((1, UPPER_SHAPE[0]), (2, UPPER_SHAPE[1])):
        m = src['maps'][k]
        filled = [y for y, row in enumerate(m) if any(row)]
        tiles = Counter(t for row in m for t in row if t)
        if len(tiles) < 3 or sum(tiles.values()) < 100 or filled[-1] - filled[0] < 30:
            out.append(None)
            continue
        if k + 1 in spec.get('as_they_are', ()):
            print(f"  background {k + 1} from {name}'s as it is")
            out.append(as_it_is(m, rows, columns))
            continue
        stretch = m[filled[0]:filled[-1] + 1]
        want = spec.get('fills', {}).get(k + 1, fill(stretch))
        model = mapsynth.Model([stretch], max_tiles=mapsynth.LAYER_TILES[k] - 1)
        # (as full as the original's stretch: the synthesiser left to itself grows TYRIAN's clouds to half the sky,
        # so the empty tile weighs more or less until it is within a sixth of it; one that runs into a dead end, the
        # rest a row copied up, is made again from another seed)
        weight, seed, best = 1.0, spec.get('seed', 1) + k, None
        for _ in range(UPPER_TRIES):
            grid, stats = mapsynth.generate(model, rows, columns, seed, bias=lambda t, x, y, w=weight: w if t == 0 else 1.0)
            if stats.get('gave up'):
                seed += 1000
                continue
            got = fill(grid)
            if best is None or abs(got - want) < abs(fill(best[0]) - want):
                best = grid, stats
            if abs(got - want) <= want / 6:
                break
            weight *= (got / want) ** 2
        if best is None:
            # (what the synthesiser can't continue, BRAINIAC's background 3: the original's as it is)
            grid, stats = as_it_is(m, rows, columns), {'the original': 1}
        else:
            grid, stats = best
            for y in range(UPPER_BLANK):
                grid[y] = [0] * columns
        print(f"  background {k + 1} from {name}'s: {fill(grid):.2f} full (wanted {want:.2f}), {dict(stats)}")
        out.append(grid)
    return out, layer_ratios(waves.Source(ep, name))


def layer1_pixels(events, until):
    """How far layer 1 scrolls (pixels) before the clock until, by the events' speeds (event 2)."""
    speed, at, px = 1, 0, 0
    for e in sorted((e for e in events if e['type'] == 2 and e['t'] < until), key=lambda e: e['t']):
        px += speed * (e['t'] - at)
        speed, at = e['d1'], e['t']
    return px + speed * max(0, until - at)


def sheet_events(banks):
    """The events loading a level's sprite sheets at its start: event 5 the first four, Tyrian3D's 210 the others."""
    b = list(banks) + [0] * (BANKS - len(banks))
    out = [dict(t=0, type=5, d1=b[0], d2=b[1], d3=b[2], d5=0, d6=0, d4=b[3])]
    if len(banks) > 4:
        out.append(dict(t=0, type=210, d1=b[4], d2=b[5], d3=b[6], d5=0, d6=0, d4=b[7]))
    return out


def make_level(spec):
    rows_gbc, img = gbc_level(spec['gbc'])
    gbc_map = rows_gbc['map']
    ep, pcname = spec['pc']
    # (spec 'tiles': the map's tile set another original's, with its layers: GBC DELIANI's PC DELIANI's, the user's pick)
    src = [l for l in sources.original_levels() if (l['episode'], l['name']) == tuple(spec.get('tiles', spec['pc']))][0]
    letter = src['shapes']
    # the tiles follow their neighbours as these originals have them (the level's, and others of its look)
    names = [tuple(m) for m in spec.get('maps', [spec.get('tiles', spec['pc'])])]
    grids = [l['maps'][0] for l in sources.original_levels() if (l['episode'], l['name']) in names and l['shapes'] == letter]
    model = mapsynth.Model(grids, max_tiles=mapsynth.LAYER_TILES[0])
    tiles = preview.tiles(letter)
    pal = preview.palette()
    ids = sorted(model.count)
    layer1, n_rows = space(spec, img, grids, letter) if spec.get('space') else autotile(spec, img, grids, letter)
    upper, ratios = upper_layers(spec, letter)
    maps = [layer1] + [grid or [[0] * columns for _ in range(rows)] for grid, (rows, columns) in zip(upper, UPPER_SHAPE)]
    # events: the original's look at the start, no random enemies, the GBC script's enemies (with the
    # original's boss in place of the GBC one), the end
    look = waves.Source(ep, pcname)
    enemy_events, placements, banks, gbc_boss = enemies(spec, look)
    # (its scroll speeds the GBC script's: event 2 at the start, backgrounds 2 and 3 with layer 1)
    events = [dict(e) for e in look.events if e['t'] == 0 and e['type'] in LOOK_EVENTS and e['type'] not in (2, 3)]
    if spec.get('stars'):
        # (the stars on where the original has them off: STARGATE's black, the GBC WARP's a starfield)
        events = [e for e in events if e['type'] not in (8, 9)] + [dict(t=0, type=9, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0)]
    if not any(x['t'] == 0 and x['type'] == 2 for x in enemy_events):
        events.insert(0, dict(t=0, type=2, d1=1, d2=1, d3=1, d5=0, d6=0, d4=0))
    for e in events:
        e.pop('adjust', None)
    events += sheet_events(banks)
    events.append(dict(t=0, type=13, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    enemy_events = with_drops(enemy_events, look, placements, spec.get('pool', []), gbc_boss)
    events += enemy_events
    last = max([e['t'] for e in enemy_events] + [0])
    if not placements:
        end = min(8100, max(28 * (n_rows - 7) + 200, last + 600))
    else:
        # (with a boss, the end when it is gone is its block's; this one, as the originals have one
        # near 8100, ends the level if it never is, after the block's last event)
        end = max(8100, placements[0]['end'] + 600)
    if not gbc_boss:
        events.append(dict(t=min(end, 65000), type=11, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    # the GBC boss song once the boss comes (tyrian2.c event 204: tools/gbc/music.py)
    boss_at = gbc_boss['start'] if gbc_boss else placements[0]['start'] if placements else None
    if boss_at is not None:
        # (before the first event of its time: a difficulty's skip, 66, counts the events after it at its own)
        at = next((k for k, e in enumerate(events) if e['t'] >= boss_at), len(events))
        events.insert(at, dict(t=boss_at, type=204, d1=1, d2=0, d3=0, d5=0, d6=0, d4=0))
    # backgrounds 2 and 3 at their original's pace against layer 1 (as fast as their map lasts until the boss: a
    # PC boss's block brings its original's speeds; an empty one at layer 1's)
    px = layer1_pixels(events, placements[0]['start'] if placements else end)
    pace = [min(r, Fraction(UPPER_ROOM, max(1, px))) if grid else 1 for r, grid in zip(ratios, upper)]
    for e in events:
        if e['type'] == 2 and e['d1'] > 0:
            e['d2'], e['d3'] = (max(1, int(e['d1'] * p)) for p in pace)
    if any(upper):
        print(f"  backgrounds 2, 3 at {[float(p) for p in pace]} x layer 1 (originals' {[float(r) for r in ratios]}; "
              f"layer 1 {px} px before the boss)")
    # (a GBC boss ends the level itself: boss.py)
    level = dict(name=spec['name'], song=level_song(ep, pcname), shapes=letter, maps=maps, events=events,
                 placements=placements, banks=banks, terrain=None, gbc=spec['gbc'], pc=[ep, pcname],
                 gbc_rows=len(gbc_map), pc_rows=n_rows, arcade=spec.get('arcade', False), gbc_boss=gbc_boss,
                 upper=dict(source=list(spec.get('layers', spec['pc'])), pace=[float(p) for p in pace]))
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
