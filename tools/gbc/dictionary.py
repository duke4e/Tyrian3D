"""Episode 7's maps by a tile dictionary: each GBC block (a 16 x 16 metatile) one PC tile, and the PC map laid block for
block after the GBC map (a PC cell a GBC block: the GBC map's 11 columns in the PC's 2..12, a PC row a GBC row, the map
28/24 times as long as at 1.5x, the level's clock with it).

The proposal: the aligned autotile's choices at each block's cells (episode.autotile, spec 'aligned'), as votes, made one
tile per block where the blocks meet as the originals pair their tiles (over all the GBC map's neighbour pairs: ICM); the
user's picks (tools/gbc/dictionaries.json, {"<gbc level>": {"<block>": tile}}) stand, the rest around them.

    python tools/gbc/dictionary.py 23 [out.png]     the dictionary proposed for GBC level 23, the map laid and drawn
    python tools/gbc/dictionary.py apply 23,3 [--dry] the committed levels' maps laid from their dictionaries
    python tools/gbc/dictionary.py upper 21,1 [--dry] their backgrounds 2 and 3 laid from the originals' pieces (upper.py)
"""
import json
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import episode as E  # noqa: E402

DICTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionaries.json')
LEFT = 2      # the PC column of the GBC map's first
SMOOTH = 0.5  # votes' prior per candidate
SUGGEST = 40  # suggestions per block


def setting(spec):
    """The GBC map (block rows), its picture, the originals' layer-1 grids the PC tiles follow, the tile set's letter."""
    rows, img = E.gbc_level(spec['gbc'])
    source = tuple(spec.get('tiles', spec['pc']))
    letter = [l for l in E.sources.original_levels() if (l['episode'], l['name']) == source][0]['shapes']
    names = [tuple(m) for m in spec.get('maps', [source])]
    grids = [l['maps'][0] for l in E.sources.original_levels() if (l['episode'], l['name']) in names and l['shapes'] == letter]
    return rows['map'], img, grids, letter


def originals(grids):
    """The originals' tile pairs as autotile counts them: right[left][right], above[below][above]; and the tiles that
    stand beside or above themselves (ground, not pieces of something); and how often each is used."""
    right, above, selfish, use = {}, {}, Counter(), Counter()
    for g in grids:
        for y in range(len(g)):
            for x in range(len(g[0])):
                t = g[y][x]
                use[t] += 1
                if y + 1 < len(g):
                    above.setdefault(g[y + 1][x], Counter())[t] += 1
                if x > 0:
                    right.setdefault(g[y][x - 1], Counter())[t] += 1
                if (x > 0 and g[y][x - 1] == t) or (y > 0 and g[y - 1][x] == t):
                    selfish[t] += 1
    return right, above, selfish, use


def neighbours(gmap):
    """The GBC map's block pairs: beside[(left, right)], above[(upper, lower)], counted."""
    beside, above = Counter(), Counter()
    for y, row in enumerate(gmap):
        for x, b in enumerate(row):
            if x + 1 < len(row):
                beside[(b, row[x + 1])] += 1
            if y + 1 < len(gmap):
                above[(b, gmap[y + 1][x])] += 1
    return beside, above


def picks():
    try:
        with open(DICTS, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def votes(spec, gmap, img, grids, letter):
    """The aligned autotile's tile at each block's cells, counted per block."""
    layer1, n_rows = E.autotile(dict(spec, aligned=True), img, grids, letter)
    h = len(gmap)
    assert n_rows == h, (n_rows, h)
    v = defaultdict(Counter)
    for i, row in enumerate(gmap):
        for x, b in enumerate(row):
            v[b][layer1[E.ROWS - h + i][x + LEFT]] += 1
    return v


def propose(spec, fixed=None, sweeps=8):
    """{block: tile} for the spec's GBC level, and per block its candidates best first ([(tile, cost)])."""
    gmap, img, grids, letter = setting(spec)
    fixed = {int(b): t for b, t in (fixed if fixed is not None else picks().get(str(spec['gbc']), {})).items()}
    v = votes(spec, gmap, img, grids, letter)
    right, above, selfish, use = originals(grids)
    tiles = E.preview.tiles(letter)
    pal = E.preview.palette()
    ground = [t for t, _ in use.most_common() if tiles.get(t) is not None][:E.mapsynth.LAYER_TILES[0]]
    ids = sorted(set(ground) | {t for c in v.values() for t in c} | set(fixed.values()))
    idx = {t: i for i, t in enumerate(ids)}
    cost_h, cost_v, *_ = E.pair_costs(spec, ids, right, above, selfish, tiles, pal)
    blocks = sorted(v)
    count = Counter(b for row in gmap for b in row)
    unary = {}
    for b in blocks:
        n_b = sum(v[b].values())
        p = np.array([(v[b][t] + SMOOTH) / (n_b + SMOOTH * len(ids)) for t in ids])
        unary[b] = -count[b] * np.log(p)
    beside, below = neighbours(gmap)
    links = defaultdict(list)  # block -> (other, count, cost row given the other's tile)
    for (a, b), n in beside.items():
        links[a].append((b, n, lambda tb, a_=None: cost_h[:, tb]))   # a left of b: cost_h[a's, b's]
        links[b].append((a, n, lambda ta, b_=None: cost_h[ta, :]))   # b right of a
    for (a, b), n in below.items():
        links[a].append((b, n, lambda tb: cost_v[tb, :]))   # a above b: cost_v[b's (below), a's (above)]
        links[b].append((a, n, lambda ta: cost_v[:, ta]))   # b below a
    choice = {b: idx[fixed[b]] if b in fixed else int(unary[b].argmin()) for b in blocks}
    for _ in range(sweeps):
        changed = 0
        for b in blocks:
            if b in fixed:
                continue
            tot = unary[b].copy()
            for o, n, row in links[b]:
                if o == b:  # (beside or above itself: both ends its own tile)
                    tot += n * E.PAIR_COST * np.array([0.5 * (row(t)[t]) for t in range(len(ids))])
                else:
                    tot += n * E.PAIR_COST * row(choice[o])
            best = int(tot.argmin())
            changed += best != choice[b]
            choice[b] = best
        if not changed:
            break
    # suggestions per block: the tiles voted for (most first), then the tile set's nearest in colour
    near = likeness(gmap, img, grids, letter, tiles, pal)
    ranked = {}
    for b in blocks:
        voted = [t for t, _ in v[b].most_common()]
        ranked[b] = (voted + [t for t in near[b] if t not in voted])[:SUGGEST]
    return {b: ids[choice[b]] for b in blocks}, ranked, (gmap, img, grids, letter)


def likeness(gmap, img, grids, letter, tiles, pal, n=4):
    """Each block's tiles of the whole tile set, nearest first: the GBC lightness range (5th to 95th percentile, the
    blocks weighted by use) moved to the originals' tiles' (by their use), the hues kept (moved channel by channel, the
    GBC browns came out green beside TYRIAN's fields), the pictures compared as n x n region means in Lab."""
    from PIL import Image
    count = Counter(b for row in gmap for b in row)
    pos = {}
    for y, row in enumerate(gmap):
        for x, b in enumerate(row):
            pos.setdefault(b, (y, x))
    _, _, _, use = originals(grids)
    tids = [t for t in sorted(tiles) if tiles[t] is not None]
    blab = {b: E.lab(np.array(Image.fromarray(img[16 * y:16 * y + 16, 16 * x:16 * x + 16]).resize((24, 28), Image.BILINEAR))
                     .astype(np.float64)) for b, (y, x) in pos.items()}
    tlab = {t: E.lab(pal[tiles[t]].astype(np.float64)) for t in tids}

    def wpct(v, w, q):
        o = np.argsort(v)
        c = np.cumsum(w[o])
        return np.interp(np.array(q) / 100 * c[-1], c, v[o])
    src = np.concatenate([blab[b][..., 0].ravel() for b in blab])
    sw = np.concatenate([np.full(24 * 28, count[b]) for b in blab]).astype(float)
    used = [t for t in tids if use[t]] or tids
    ref = np.concatenate([tlab[t][..., 0].ravel() for t in used])
    rw = np.concatenate([np.full(24 * 28, use[t] or 1) for t in used]).astype(float)
    lo, hi = wpct(src, sw, [5, 95])
    plo, phi = wpct(ref, rw, [5, 95])
    bd = {}
    for b, v in blab.items():
        v = v.copy()
        v[..., 0] = plo + (v[..., 0] - lo) * (phi - plo) / max(hi - lo, 1e-6)
        bd[b] = E.regions(v, n)
    td = np.stack([E.regions(tlab[t], n) for t in tids])
    out = {}
    for b in blab:
        d = np.sqrt(((td - bd[b][None]) ** 2).sum(-1)).mean((1, 2))
        out[b] = [tids[i] for i in np.argsort(d)]
    return out


def lay(gmap, dic):
    """Layer 1 (ROWS x 14) from the GBC map by the dictionary: the map at the bottom, its top 8 rows looped above it, the
    columns past its sides its edge column's tiles."""
    h, w = len(gmap), len(gmap[0])
    out = []
    for r in range(E.ROWS):
        b = E.ROWS - 1 - r
        if b >= h:
            b = h - 8 + (b - h) % 8
        row = gmap[h - 1 - b]
        out.append([dic[row[min(max(c - LEFT, 0), w - 1)]] for c in range(14)])
    return out


def sides(spec, layer1, letter, grids, allowed=None):
    """The columns past the GBC map's sides (the PC's 0, 1 and 13) made again: down each, the ground tiles (those that
    stand beside themselves) that join the column inside it and each other as the originals have them (Viterbi)."""
    right, above, selfish, use = originals(grids)
    tiles = E.preview.tiles(letter)
    pal = E.preview.palette()
    # (allowed: only those, the tiles of the map's own columns, so the sides go on with what it shows; how often the map
    # shows each its prior, so FLEET's sides are space, not the hull wall its original has along its sides)
    if allowed is not None:
        use = Counter(allowed)
    # (a blank tile too, where the map shows one: FLEET's space)
    ground = [t for t, _ in use.most_common() if (tiles.get(t) is not None or allowed is not None) and selfish[t] and
              (allowed is None or t in allowed)]
    ground = ground[:E.mapsynth.LAYER_TILES[0]]
    ids = sorted(set(ground) | {t for row in layer1 for t in row})
    idx = {t: i for i, t in enumerate(ids)}
    cost_h, cost_v, *_ = E.pair_costs(spec, ids, right, above, selfish, tiles, pal)
    cand = np.array([idx[t] for t in ground])
    ids_c = cand
    prior = -np.log(np.array([use[ids[i]] for i in cand], np.float64) / max(use[ids[i]] for i in cand))
    out = [list(row) for row in layer1]
    for c, inside in ((1, 2), (0, 1), (13, 12)):
        rows = len(out)
        unary = np.stack([E.PAIR_COST * (cost_h[cand, idx[out[r][inside]]] if c < inside else cost_h[idx[out[r][inside]], cand])
                          + E.PRIOR_WEIGHT * prior for r in range(rows)])
        # (spec sides_keep: a tile other than the one inside it costs that much: ASTEROID's plates go on to the edge,
        # where the cheap space beside them left black notches, and its rims don't repeat there, none being ground)
        if spec.get('sides_keep'):
            unary += spec['sides_keep'] * np.stack([ids_c != idx[out[r][inside]] for r in range(rows)])
        vert = E.PAIR_COST * cost_v[np.ix_(cand, cand)]  # [below, above]
        acc, back = unary[rows - 1], []
        for r in range(rows - 2, -1, -1):  # up from the bottom: row r above row r + 1
            tot = acc[:, None] + vert           # (below, above)
            back.append(tot.argmin(0))
            acc = tot.min(0) + unary[r]
        k = int(acc.argmin())
        out[0][c] = ids[cand[k]]
        for i, r in enumerate(range(1, rows)):
            k = int(back[rows - 2 - i][k])
            out[r][c] = ids[cand[k]]
    return out


def layer(spec, dic, gmap, grids, letter):
    """The PC map's layer 1 from the dictionary, its side columns made again (from the tiles it shows)."""
    out = lay(gmap, dic)
    h, w = len(gmap), len(gmap[0])
    inside = Counter(t for row in out[E.ROWS - h:] for t in row[LEFT:LEFT + w])
    return sides(spec, out, letter, grids, allowed=inside)


FIT_PAIR = 8.0    # fitted: how much a pair the originals never make costs against a tile unlike the dictionary's
FIT_MATCH = 1.0


def fitted(spec, dic, gmap, grids, letter):
    """Layer 1 near the dictionary but joined as the originals join their tiles (the user on BUBBLES: the shape may give
    a little so that every tile fits its neighbours): each cell any tile of the level's originals, costing as unlike
    the dictionary's tile it is (4 x 4 region means in Lab) and its pairs as the originals pair tiles (one they never
    make at least spec `rare`'s cost), solved over the whole grid (episode.solve_grid)."""
    right, above, selfish, use = originals(grids)
    tiles = E.preview.tiles(letter)
    pal = E.preview.palette()
    ids = sorted(set(use) | set(dic.values()))
    idx = {t: i for i, t in enumerate(ids)}

    def look(t):
        im = tiles.get(t)
        return E.regions(E.lab(np.zeros((28, 24, 3)) if im is None else pal[im].astype(np.float64)), 4)
    R = np.stack([look(t) for t in ids])
    diff = {b: FIT_MATCH * np.sqrt(((R - R[idx[t]][None]) ** 2).sum(-1)).mean((1, 2)) / 10 for b, t in dic.items()}
    cost_h, cost_v, *_ = E.pair_costs(dict(spec, rare=spec.get('rare') or (2, 1.0)), ids, right, above, selfish, tiles, pal)
    h, w = len(gmap), len(gmap[0])
    every = np.arange(len(ids))
    cands, unary = [], []
    for r in range(E.ROWS):
        b_ = E.ROWS - 1 - r
        if b_ >= h:
            b_ = h - 8 + (b_ - h) % 8
        row = gmap[h - 1 - b_]
        cands.append([every] * 14)
        unary.append([diff[row[min(max(c - LEFT, 0), w - 1)]] for c in range(14)])
    choice = E.solve_grid(cands, unary, cost_h, cost_v, len(ids), pair=FIT_PAIR)
    return [[ids[choice[r][c]] for c in range(14)] for r in range(E.ROWS)]


def picture(layer1, gmap, img, letter):
    """The GBC map (a block 24 x 28) beside the PC map (layer 1), their columns lined up."""
    from PIL import Image
    h = len(gmap)
    pc = E.preview.picture([layer1[E.ROWS - h:]], letter)
    g = Image.fromarray(img).resize((len(gmap[0]) * 24, h * 28), Image.NEAREST)
    out = Image.new('RGB', (LEFT * 24 + g.width + 12 + pc.width, max(g.height, pc.height)), (40, 0, 40))
    out.paste(g, (LEFT * 24, out.height - g.height))
    out.paste(pc, (LEFT * 24 + g.width + 12, out.height - pc.height))
    return out


SHIFT = -9                 # the ground enemies' x: the map's columns now from GBC x 16c - 32, not 16c - 38 (6 x 1.5 PC px)
GROUND_SPAWNS = (6, 17)    # (and event 12 with d6 0: a 4-part one on the ground)
JUMPS = (54, 70)           # events whose d1 is a time


def clock_at(events, px):
    """The first clock at which layer 1 has scrolled px pixels (event 2's speeds), or None if it never does."""
    speed, at, done = 1, 0, 0
    for e in sorted((e for e in events if e['type'] == 2), key=lambda e: e['t']):
        if speed > 0 and done + speed * (e['t'] - at) >= px:
            break
        done += speed * (e['t'] - at)
        speed, at = e['d1'], e['t']
    return at + (px - done) / speed if speed > 0 else None


def stretch(level):
    """The level's clock for its map made 28/24 times as long (a PC row a GBC row, not 1.5 x 16 px of one): up to the
    pivot (the GBC map's top reached, or a placed boss's start if earlier) 7/6 as long, which keeps each event where it was on
    the map (event 2's speeds go with it), and from there on the same, shifted (the boss's own pace, and the clock stays
    below layer 1's end); the jumps' times with it; the boss's placement and start; the ground enemies 9 px left with
    the map's columns; backgrounds 2 and 3 no faster than their maps last."""
    events = level['events']
    top = clock_at(events, 28 * level['pc_rows'])
    # (a placed PC boss's start; a GBC boss's pieces are the script's, on its map: JUNGLE II's beetle from clock 96 on)
    boss = min((p['start'] for p in level['placements'] if p['kind'] == 'boss'), default=None)
    pivot = min([x for x in (top, boss) if x is not None] or [max(e['t'] for e in events)])
    extra = round(pivot / 6)

    def f(t):
        return round(t * 7 / 6) if t <= pivot else t + extra
    for e in events:
        e['t'] = f(e['t'])
        if e['type'] in JUMPS and e['d1'] != 65535:
            e['d1'] = f(e['d1'])
        if e['type'] in GROUND_SPAWNS or (e['type'] == 12 and e['d6'] == 0):
            e['d2'] += SHIFT
    for p in level['placements']:
        p['start'], p['end'] = f(p['start']), f(p['start']) + p['end'] - p['start']
    if level.get('gbc_boss'):
        level['gbc_boss']['start'] = f(level['gbc_boss']['start'])
    return pivot, extra


def paces(level, ratios=None, fixed=None):
    """Backgrounds 2 and 3 at their pace (or the originals' ratios), no faster than their maps last until the boss or
    the end (episode.make_level's)."""
    events = level['events']
    bosses = [p['start'] for p in level['placements'] if p['kind'] == 'boss']
    ends = [e['t'] for e in events if e['type'] == 11]
    last = max(e['t'] for e in events)
    until = bosses[0] if bosses else ends[0] if ends else min(8100, max(28 * (level['pc_rows'] - 7) + 200, last + 600))
    px = E.layer1_pixels(events, until)
    room = Fraction(E.UPPER_ROOM, max(1, px))
    old = ratios or level['upper']['pace']
    pace = [float(min(Fraction(p).limit_denominator(1000), room)) if any(any(r) for r in grid) else 1
            for p, grid in zip(old, level['maps'][1:3])]
    # (spec upper_pace: [pace or None, ...]: a layer that must keep to layer 1, DELIANI's structures over its plates)
    for k, p in enumerate(fixed or ()):
        if p is not None:
            pace[k] = float(p)
    for e in events:
        if e['type'] == 2 and e['d1'] > 0:
            e['d2'], e['d3'] = (max(1, int(e['d1'] * p)) for p in pace)
    level['upper']['pace'] = pace
    return pace, px


ROW_TIME = 288   # a ground spawn's clock against the map row it stands on: t = 28 (300 - row) - 288 (DESERTRUN's and
                 # SURFACE's arch tops over their legs, every one of them: the clock is layer 1's place)


def decor(level, spec, layer1):
    """Spec `decor`: [{tile, below, from: (episode, level), ids: (first, last)}]: where layer 1 has the tile over `below`
    (the PC stone arch's left leg, 27 over 37), the original's ground enemies of those ids that stand over its first such
    tile (the arch's top: DESERTRUN's 212-222, the user: "lukovima nedostaje gornji dio, ovo su samo noge"), at the same
    places against it; the decor of an earlier apply goes first. Each goes after the events of its tick and outside any
    difficulty skip's (66) events."""
    import waves
    events = [e for e in level['events'] if 'decor' not in e]
    added = 0
    for d in spec.get('decor', ()):
        src = waves.Source(*d['from'])
        grid = [l for l in E.sources.original_levels() if (l['episode'], l['name']) == tuple(d['from'])][0]['maps'][0]
        lo, hi = d['ids']
        group_t = min(e['t'] for e in src.events if e['type'] in (6, 7, 10) and lo <= e['d1'] <= hi)
        r0 = E.ROWS - (group_t + ROW_TIME) // 28
        c0 = grid[r0].index(d['tile'])
        group = [e for e in src.events if e['t'] == group_t and e['type'] in (6, 7, 10) and lo <= e['d1'] <= hi]
        for r in range(E.ROWS - 1):
            for c in range(14):
                if layer1[r][c] == d['tile'] and layer1[r + 1][c] == d['below']:
                    t = 28 * (E.ROWS - r) - ROW_TIME
                    if t < 0:
                        continue
                    for e in group:
                        events.append(dict(t=t, type=e['type'], d1=e['d1'], d2=e['d2'] + 24 * (c - c0), d3=e['d3'],
                                           d5=e['d5'], d6=e['d6'], d4=0, ep=src.episode, decor=d.get('tag', 'decor')))
                        added += 1
    # (in clock order, the new ones after the old of their tick; none inside a difficulty skip's run)
    events.sort(key=lambda e: (e['t'], 'decor' in e))
    covered = set()
    for i, e in enumerate(events):
        if e['type'] == 66:
            covered.update(range(i + 1, i + 1 + e['d2']))
    bad = [i for i in covered if i < len(events) and 'decor' in events[i]]
    if bad:
        raise SystemExit(f"{spec['name']}: {len(bad)} decor events inside difficulty skips")
    level['events'] = events
    return added


def apply(n, dry=False):
    """The committed level's layer 1 made again by its spec's method (remake.py; by default laid from its dictionary,
    tools/gbc/dictionaries.json, every block); the first time
    (the level not 'aligned' yet) its clock stretched to the longer map (stretch); a level whose spec takes its tiles
    from another original (spec 'tiles') gets that one's tile set and backgrounds 2 and 3."""
    import glob
    import remake
    spec = E.spec_of(n)
    gmap, img, grids, letter = setting(spec)
    if spec.get('remake', 'dictionary') in ('dictionary', 'fitted'):
        missing = sorted({b for row in gmap for b in row} - {int(b) for b in picks().get(str(n), {})})
        if missing:
            raise SystemExit(f"L{n:02d}: blocks without a tile in {DICTS}: {missing}")
    path = glob.glob(os.path.join(E.OUT, 'levels', f'*_L{n:02d}.json'))[0]
    with open(path, encoding='utf-8') as f:
        level = json.load(f)
    notes = []
    ratios = None
    if level['shapes'] != letter:
        upper, ratios = E.upper_layers(spec, letter)
        level['maps'][1:3] = [grid or [[0] * columns for _ in range(rows)] for grid, (rows, columns) in zip(upper, E.UPPER_SHAPE)]
        level['upper']['source'] = list(spec.get('layers', spec['pc']))
        notes.append(f"tile set {level['shapes']} -> {letter}, backgrounds 2 and 3 from {level['upper']['source']}")
        level['shapes'] = letter
    level['maps'][0] = remake.layer(spec)[0]
    k, cells = remake.upper(spec, gmap)
    if cells:
        # (that upper layer the GBC map's structures alone, at layer 1's pace: spec upper_pace)
        rows, columns = E.UPPER_SHAPE[k - 1]
        level['maps'][k] = [[0] * columns for _ in range(rows)]
        for (r, c), t in cells.items():
            level['maps'][k][r][c] = t
        for j in spec.get('upper_clear', ()):  # (the other upper layer empty: DELIANI's synthesised pieces gone)
            r_, c_ = E.UPPER_SHAPE[j - 2]
            level['maps'][j - 1] = [[0] * c_ for _ in range(r_)]
        notes.append(f"{len(cells)} tiles of the GBC map's structures in background {k + 1}")
    ur = spec.get('upper_remake')
    if ur:
        # (spec upper_remake: dict(layer=2, remake=..., tiles=...): the GBC map made again by another remake, in that
        # upper layer over layer 1 (its row R over layer 1's R - 300; spec upper_pace keeps it at layer 1's pace):
        # DELICORE's BRAINIAC platforms over its UNDERDELI floor, the user: "layer 1 prebaciti na layer 2")
        sub = {key: spec[key] for key in ('gbc', 'name', 'pc', 'match', 'arcade', 'pool', 'rare', 'seed') if key in spec}
        sub.update((key, v) for key, v in ur.items() if key not in ('layer', 'blank'))
        blank = set(ur.get('blank', ()))  # (its black void none: BRAINIAC's 21, layer 1's black under nothing)
        grid = [[0 if t in blank else t for t in row] for row in remake.layer(sub)[0]]
        rows, columns = E.UPPER_SHAPE[ur['layer'] - 2]
        up = [[0] * columns for _ in range(rows)]
        for r in range(E.ROWS):
            up[rows - E.ROWS + r][:len(grid[r])] = grid[r]
        level['maps'][ur['layer'] - 1] = up
        notes.append(f"background {ur['layer']} the GBC map as {sub['remake']} with {sub['tiles'][1]}'s tiles")
        for j in spec.get('upper_clear', ()):
            r_, c_ = E.UPPER_SHAPE[j - 2]
            level['maps'][j - 1] = [[0] * c_ for _ in range(r_)]
    if spec.get('bg2_under'):
        # (spec bg2_under: background 2 drawn under the ground enemies from the start (event 43), so they stand on it)
        if not any(e['type'] == 43 and e['t'] == 0 for e in level['events']):
            level['events'].insert(0, dict(t=0, type=43, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    if not level.get('aligned'):
        pivot, extra = stretch(level)
        notes.append(f"clock x 7/6 up to {pivot:.0f}, then +{extra}; pc_rows {level['pc_rows']} -> {len(gmap)}")
        level['pc_rows'] = len(gmap)
        level['aligned'] = True
    if ratios is not None or 'clock' in ' '.join(notes) or spec.get('upper_pace'):
        pace, px = paces(level, ratios, spec.get('upper_pace'))
        notes.append(f'backgrounds 2, 3 at {pace} x layer 1 ({px} px before the boss or the end)')
    level['events'].sort(key=lambda e: e['t'])  # (stable)
    if spec.get('decor') or any('decor' in e for e in level['events']):
        notes.append(f"{decor(level, spec, level['maps'][0])} decor events")
    print(f"L{n:02d} {spec['name']}: " + '; '.join(notes or ['layer 1 laid again']))
    if not dry:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(level, f)
    return level


def upper_apply(n, dry=False):
    """The committed level's backgrounds 2 and 3 laid from whole pieces of the originals' (spec upper_pieces: upper.py),
    at their originals' pace (no faster than their maps last)."""
    import glob
    import upper
    import waves
    spec = E.spec_of(n)
    path = glob.glob(os.path.join(E.OUT, 'levels', f'*_L{n:02d}.json'))[0]
    with open(path, encoding='utf-8') as f:
        level = json.load(f)
    print(f"L{n:02d} {spec['name']}:")
    for k, st in sorted(spec.get('upper_pieces', {}).items()):
        level['maps'][k - 1] = upper.lay(level, spec, k, st, level['shapes'])
    ratios = E.layer_ratios(waves.Source(*spec.get('layers', spec['pc'])))
    pace, px = paces(level, ratios, spec.get('upper_pace'))
    print(f'  backgrounds 2, 3 at {pace} x layer 1 ({px} px before the boss or the end)')
    if not dry:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(level, f)
    return level


if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[1] == 'upper':
    for n in (int(x) for x in sys.argv[2].split(',')):
        upper_apply(n, dry='--dry' in sys.argv)
elif __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[1] == 'apply':
    for n in (int(x) for x in sys.argv[2].split(',')):
        apply(n, dry='--dry' in sys.argv)
elif __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    dic, ranked, (gmap, img, grids, letter) = propose(spec)
    picture(layer(spec, dic, gmap, grids, letter), gmap, img, letter).save(sys.argv[2] if len(sys.argv) > 2 else f'dict_L{n:02d}.png')
    print(spec['name'], letter, len(dic), 'blocks:', dic)
