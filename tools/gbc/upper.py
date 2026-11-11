"""Episode 7's backgrounds 2 and 3 laid from whole pieces of an original's (spec `upper_pieces`), where the synthesiser's
pieces came out of no shape (ICE EXIT's ice, LAVA I and II's), too few (CAMANIS's), too many over layer 1 (FLEET's
ships), or not where layer 1's walls are (DELICORE's rooms and pipes, BRAINIAC's).

A piece is a group of the original layer's tiles touching (also at the corners), laid whole; none that touches the
original map's edge or is cut off within it (a tile drawn up to a side nothing is beyond: ice ending straight, half a
ship, LAVA EXIT's block of one tile). spec upper_pieces:
{layer (2 or 3): dict(source=[(episode, level), ...] (that layer of each, or (episode, level, layer)), fill=share of the
cells, max_rows=n (taller pieces left out), min_tiles=n (smaller ones too), join=n (tiles so many cells apart one
piece), mend=dict(body=tile, broken={tile, ...}) (a joined piece's gaps in a row and its broken tiles made body: BRAINIAC's
pipes whole; one with a row ending in a broken tile is left out), closed=False (cut pieces too: pipes drawn at the
tile's edge), as_tiles=[(episode, level), ...] (the pieces' tiles made the most alike of those levels' layer's: CAMANIS's
ice as LAVA EXIT's rock), gap=n (rows between pieces, 1), avoid=True or 'raised' (none where, as the map scrolls, it
would pass over layer 1's walls, FLEET's ships, or over its raised ground, LAVA I's rocks against background 2's
solid), over=0.0-1.0 (at least that share of its cells over layer 1's walls), off=True (none of them: DELICORE's rooms
in its pits, apart from its floors), anchor=True or {tile, ...} (its ends, cells with one neighbour or none, and those
tiles over layer 1's walls or, under background 3, background 2's pieces: pipes standing on them), room=n (over and anchor: that
much round them too: DELICORE's flat rooms clear of its floors' raised rims, its pipes' feet on them however the 3D
view's height between the layers shifts them), seed)}. over, off and anchor: a layer that scrolls with
layer 1 (DELICORE's).

    python tools/gbc/dictionary.py upper 21,1 [--dry]     the committed levels' upper layers laid so
"""
import json
import os
import random
import struct
import sys
import zlib
from collections import Counter

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content', 'episode6'))
import episode as E  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SCREEN = 200      # the playfield's height (pixels) a piece passes through
OPEN_DARK = 0.85  # a layer-1 tile is open (space, a corridor's floor) when so much of it is colour 0 or near black
CUT = 0.5         # a piece is cut off where a tile's drawn pixels cover more than this of a side nothing is beyond
BAND = 40         # rows of an upper layer given their share of the pieces
RAISED = 3        # terrain samples so far above the ground's most common height are raised ground (LAVA I's rocks stand
                  # at 12 over its lava at -6; LAVA II has none, its lava at 0 over channels at -16)


placed_log = []  # (row, column, source level, its row, its column) of each piece lay() placed last, for checking


def original(ep, name):
    return [l for l in E.sources.original_levels() if (l['episode'], l['name']) == (ep, name)][0]


def pieces(grid, max_rows, min_tiles=1, join=0):
    """The layer's pieces: (rows, columns, {(dy, dx): tile}, top row, left column), those of at most max_rows rows and
    at least min_tiles tiles that don't touch the map's edge; join: tiles so many cells apart are of one piece
    (BRAINIAC's pipes, gaps in their runs)."""
    a = np.array(grid)
    near = ndimage.binary_dilation(a > 0, np.ones((2 * join + 1, 2 * join + 1), bool)) if join else a > 0
    lab, n = ndimage.label(near, np.ones((3, 3), bool))
    lab[a == 0] = 0
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h > max_rows or int((lab[sl] == i).sum()) < min_tiles:
            continue
        if sl[0].start == 0 or sl[1].start == 0 or sl[0].stop == a.shape[0] or sl[1].stop == a.shape[1]:
            continue
        cells = {(y - sl[0].start, x - sl[1].start): int(a[y, x])
                 for y in range(sl[0].start, sl[0].stop) for x in range(sl[1].start, sl[1].stop) if lab[y, x] == i}
        out.append((h, w, cells, sl[0].start, sl[1].start))
    return out


def mended(cells, mend):
    """A joined piece's rows whole: the gaps between its tiles filled with mend['body'], the broken tiles
    (mend['broken']) made into it; None where a row ends in a broken one (a pipe cut off)."""
    out = dict(cells)
    for y in {cy for cy, _ in cells}:
        xs = sorted(cx for cy, cx in cells if cy == y)
        if out[(y, xs[0])] in mend['broken'] or out[(y, xs[-1])] in mend['broken']:
            return None
        for x in range(xs[0], xs[-1] + 1):
            if out.get((y, x), mend['body']) in mend['broken'] or (y, x) not in out:
                out[(y, x)] = mend['body']
    return out


def cut(cells, tiles):
    """How much the piece is cut off: the most of a tile's side drawn (its outermost pixels) where nothing of the piece
    is beyond (CAMANIS's ice cut straight, FLEET's ship without its wing, LAVA EXIT's block of one tile)."""
    worst = 0.0
    for (cy, cx), t in cells.items():
        p = tiles[t] != 0
        for (dy, dx), line in (((0, -1), p[:, 0]), ((0, 1), p[:, -1]), ((-1, 0), p[0, :]), ((1, 0), p[-1, :])):
            if (cy + dy, cx + dx) not in cells:
                worst = max(worst, float(line.mean()))
    return worst


def alike(letter, used, target, wanted):
    """Each of a tile set's tiles (used) as the most alike of another set's (wanted, the tiles an original's layer
    uses): the same drawn shape, at one offset between the sets where that keeps it (the interiors' kinds kept apart),
    else the best overlap (CAMANIS's ice as LAVA EXIT's rock)."""
    a, b = E.preview.tiles(letter), E.preview.tiles(target)

    def overlap(s, t):
        if a.get(s) is None or b.get(t) is None:
            return 0.0
        x, y = a[s] != 0, b[t] != 0
        return float((x & y).sum() / max(1, (x | y).sum()))
    best_off = max(range(-512, 513), key=lambda o: sum(overlap(s, s + o) >= 0.95 for s in used if s + o in wanted))
    return {s: s + best_off if s + best_off in wanted and overlap(s, s + best_off) >= 0.95
            else max(wanted, key=lambda t: overlap(s, t)) for s in used}


def open_tiles(letter):
    """The tile set's open tiles (mostly black): {shape: True}."""
    pal = E.preview.palette()
    lum = pal.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    # (a shape the tile set doesn't draw, None: the black the game clears to, FLEET's space, BRAINIAC's floor)
    return {s: px is None or float((lum[px] < 24).mean()) >= OPEN_DARK for s, px in E.preview.tiles(letter).items()}


def solid_mask(layer1, letter):
    """Layer 1's walls: True where its tile isn't open."""
    op = open_tiles(letter)
    return np.array([[not (t == 0 or op.get(t, True)) for t in row] for row in layer1], bool)


def raised_mask(level):
    """Layer 1's raised ground: True where any of a cell's terrain samples stands RAISED above its most common height (the level's terrain,
    tools/terrain/levels.json's entry for its background 1, as built)."""
    with open(os.path.join(ROOT, 'tools', 'terrain', 'levels.json'), encoding='utf-8') as f:
        entries = json.load(f)
    found = [h for h, e in entries.items() if e.get('episode') == 7 and e.get('level') == f"{level['name']} (gbc)"
             and e.get('background', 1) == 1]
    if len(found) != 1:
        raise SystemExit(f"{level['name']}: no one terrain for background 1 ({found})")
    with open(os.path.join(ROOT, 'assets', 'terrain', f'{found[0]}.ter'), 'rb') as f:
        data = f.read()
    _, width, height, sample, sides = struct.unpack('<5I', data[4:24])
    h = np.frombuffer(zlib.decompress(data[24:]), np.int8).reshape(height, width)
    rows, columns = len(level['maps'][0]), len(level['maps'][0][0])
    th, tw = 28 // sample, 24 // sample
    x0 = sides * tw  # (the generated columns on each side)
    cells = h[:rows * th, x0:x0 + columns * tw].reshape(rows, th, columns, tw)
    values, counts = np.unique(cells, return_counts=True)
    return (cells > values[counts.argmax()] + RAISED).any(axis=(1, 3))


def timeline(level):
    """How far layers 1, 2 and 3 have scrolled (pixels) at each tick of the clock, by event 2's speeds."""
    scroll = sorted((e for e in level['events'] if e['type'] == 2 and e['t'] < 60000), key=lambda e: e['t'])
    last = max(e['t'] for e in level['events'] if e['t'] < 60000)
    px = np.zeros((3, last + 1))
    sp, at, pos = (1, 1, 1), 0, np.zeros(3)
    for e in scroll + [dict(t=last + 1, d1=0, d2=0, d3=0)]:
        for t in range(at, min(e['t'], last + 1)):
            px[:, t] = pos
            pos = pos + sp
        sp, at = (e['d1'], e['d2'], e['d3']), e['t']
    return px


def passes(px1, pxk, rows):
    """For each row of an upper layer (rows long, its bottom the level's start), the span of layer 1's rows (from layer 1's
    bottom) it is over on the screen while the map scrolls: [first, last] or None for one never on the screen."""
    out = []
    for r in range(rows):
        d = (rows - 1 - r) * 28  # (its distance from the layer's bottom, pixels)
        on = (pxk >= d - SCREEN) & (pxk <= d + 28)
        if not on.any():
            out.append(None)
            continue
        lag = pxk[on] - px1[on]  # layer 1's pixel under it: d - lag
        out.append(((d - lag.max()) // 28, (d + 28 - lag.min()) // 28))
    return out


def lay(level, spec, k, st, letter):
    """Background k (2 or 3) laid from pieces, as spec upper_pieces[k] says."""
    rows, columns = E.UPPER_SHAPE[k - 2]
    rng = random.Random(st.get('seed', 1) + k)
    layer1 = level['maps'][0]
    n1 = len(layer1)
    walls = raised_mask(level) if st.get('avoid') == 'raised' else solid_mask(layer1, letter)
    # (layer 3 is a column wider and 16 pixels further left: its column c mostly over layer 1's c - 1; beyond the
    # sides: wall)
    under = np.pad(walls, ((0, 0), (1, 1)), constant_values=True)
    under = under[:, :-1] if k == 3 else under[:, 1:-1]
    # (what a piece's ends stand on, room round them: layer 1's walls and, under background 3, background 2's
    # pieces, both at layer 1's pace)
    m = st.get('room', 0)
    stand = walls.copy()
    if k == 3:
        stand |= np.array(level['maps'][1][len(level['maps'][1]) - n1:], bool)
    stand = np.pad(stand, ((m, m), (m + 1, m + 1)), constant_values=True)
    stand = ndimage.binary_erosion(stand, np.ones((2 * m + 1, 2 * m + 1), bool), border_value=1)[m:-m or None, m:-m or None]
    stand = stand[:, :-1] if k == 3 else stand[:, 1:-1]
    pool, origin = [], []
    for source in st['source']:
        ep, name, layer = (*source, k)[:3]  # ((episode, level) or (episode, level, its layer): another layer's pieces)
        src = original(ep, name)
        tiles = E.preview.tiles(src['shapes'])
        recolour = None
        if st.get('as_tiles'):
            wanted = {t for e, n in st['as_tiles'] for row in original(e, n)['maps'][k - 1] for t in row if t}
            used = {t for row in src['maps'][layer - 1] for t in row if t and tiles.get(t) is not None}
            recolour = alike(src['shapes'], used, letter, wanted)
        # (tiles that show nothing, all colour 0, are empty: FLEET's background 3 joins its ships with them)
        seen = {t for t, px in E.preview.tiles(src["shapes"]).items() if px is not None and px.any()}
        grid = [[t if t in seen else 0 for t in row] for row in src['maps'][layer - 1]]
        for h, w, cells, top, left in pieces(grid, st.get('max_rows', 20), st.get('min_tiles', 1), st.get('join', 0)):
            if st.get('mend'):
                cells = mended(cells, st['mend'])
                if cells is None:
                    continue
            if st.get('closed', True) and cut(cells, tiles) > CUT:
                continue
            if recolour:
                cells = {c: recolour[t] for c, t in cells.items()}
            pool.append((h, w, cells))
            origin.append((name, top, left))
    if not pool:
        raise SystemExit(f"{level['name']}: no pieces for background {k}")
    if (st.get('over') or st.get('off') or st.get('anchor')) and not np.array_equal(*timeline(level)[[0, k - 1]]):
        raise SystemExit(f"{level['name']}: background {k} doesn't scroll with layer 1 (over, anchor)")
    props = st.get('anchor') if isinstance(st.get('anchor'), (set, frozenset, tuple, list)) else ()
    ends = [[c for c, t in cells.items() if t in props or
             sum((c[0] + dy, c[1] + dx) in cells for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0))) <= 1]
            for _, _, cells in pool]
    placed_log.clear()
    taken = np.zeros((rows, columns), bool)
    out = [[0] * columns for _ in range(rows)]
    over = None
    if st.get('avoid'):
        px = timeline(level)
        over = passes(px[0], px[k - 1], rows)
    off = n1 - rows  # (layer 1's row under an upper row at one pace)
    # (of the rows that come on the screen, the others left empty: with avoid, as they scroll; with over or anchor,
    # layer 1's)
    fixed = bool(st.get('over') or st.get('off') or st.get('anchor'))
    on = [(over is None or over[y] is not None) and (not fixed or y + off >= 0) for y in range(rows)]
    shown = sum(on)
    want = st['fill'] * shown * columns
    cands = []
    for i, (h, w, cells) in enumerate(pool):
        for y in range(E.UPPER_BLANK, rows - h + 1):
            if not (on[y] and on[y + h - 1]):
                continue
            for x in range(0, columns - w + 1):
                if st.get('over') and np.mean([stand[y + off + cy, x + cx] for cy, cx in cells]) < st['over']:
                    continue
                if st.get('off') and any(under[y + off + cy, x + cx] for cy, cx in cells):
                    continue
                if st.get('anchor') and not all(stand[y + off + cy, x + cx] for cy, cx in ends[i]):
                    continue
                cands.append((i, y, x))
    # (each piece in turn, none laid much more often than another: the small ones fit most places)
    by_piece = {}
    for c in cands:
        by_piece.setdefault(c[0], []).append(c)
    for v in by_piece.values():
        rng.shuffle(v)
    turns = list(by_piece.values())
    cands = []
    for r in range(max((len(v) for v in turns), default=0)):
        rng.shuffle(turns)
        cands += [v[r] for v in turns if r < len(v)]
    gap = st.get('gap', 1)
    placed = 0
    # (spread along the level: each stretch of BAND rows its share)
    shown_in = Counter(y // BAND for y in range(rows) if on[y])
    quota = {band: want * n / shown for band, n in shown_in.items()}
    in_band = Counter()
    for i, y, x in cands:
        if placed >= want:
            break
        h, w, cells = pool[i]
        if in_band[y // BAND] >= quota.get(y // BAND, 0):
            continue
        # (room round it: a piece doesn't touch another)
        if taken[max(0, y - gap):y + h + gap, max(0, x - 1):x + w + 1].any():
            continue
        if over is not None:
            hit = False
            for (cy, cx) in cells:
                span = over[y + cy]
                if span is None:
                    continue
                lo, hi = span
                # (and the columns either side: the layers' parallax)
                xs = slice(max(0, x + cx - (k == 3) - 1), min(walls.shape[1], x + cx + 2))
                a, b = max(0, n1 - 1 - int(hi)), min(n1, n1 - int(lo))
                if a < b and walls[a:b, xs].any():
                    hit = True
                    break
            if hit:
                continue
        for (cy, cx), t in cells.items():
            out[y + cy][x + cx] = t
        taken[y:y + h, x:x + w] = True
        placed += len(cells)
        in_band[y // BAND] += len(cells)
        placed_log.append((y, x, *origin[i]))
    print(f"  background {k}: {placed} tiles in pieces ({placed / (shown * columns):.3f} full, wanted {st['fill']}), "
          f"{len(pool)} pieces to lay, {len(cands)} places")
    return out
