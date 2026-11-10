"""Episode 7's backgrounds 2 and 3 laid from whole pieces of an original's (spec `upper_pieces`), where the synthesiser's
pieces came out of no shape (ICE EXIT's ice), too few (CAMANIS's), too many over layer 1 (FLEET's ships), or not where
layer 1's walls are (DELICORE's rooms and pipes, BRAINIAC's).

A piece is a group of the original layer's tiles touching (also at the corners), laid whole. spec upper_pieces:
{layer (2 or 3): dict(source=[(episode, level), ...] (that layer of each), fill=share of the cells, max_rows=n (taller
pieces left out), min_tiles=n (smaller ones too), join=n (tiles so many cells apart one piece), avoid=True (none where, as the map scrolls, it would pass over what layer 1 has there: FLEET's
ships), follow=0.0-1.0 (only where layer 1's walls under and round it are as they were under it in its original,
at least that share of the cells: the layer at layer 1's pace, BRAINIAC's rooms against its walls), seed)}.

    python tools/gbc/dictionary.py upper 21,1 [--dry]     the committed levels' upper layers laid so
"""
import os
import random
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content', 'episode6'))
import episode as E  # noqa: E402

SCREEN = 200      # the playfield's height (pixels) a piece passes through
OPEN_DARK = 0.85  # a layer-1 tile is open (space, a corridor's floor) when so much of it is colour 0 or near black


def original(ep, name):
    return [l for l in E.sources.original_levels() if (l['episode'], l['name']) == (ep, name)][0]


def pieces(grid, max_rows, min_tiles=1, join=0):
    """The layer's pieces: (rows, columns, {(dy, dx): tile}, top row, left column), those of at most max_rows rows and
    at least min_tiles tiles; join: tiles so many cells apart are of one piece (BRAINIAC's pipes, gaps in their runs)."""
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
        cells = {(y - sl[0].start, x - sl[1].start): int(a[y, x])
                 for y in range(sl[0].start, sl[0].stop) for x in range(sl[1].start, sl[1].stop) if lab[y, x] == i}
        out.append((h, w, cells, sl[0].start, sl[1].start))
    return out


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
    walls = solid_mask(layer1, letter)
    padded = np.pad(walls, ((0, 0), (1, 2)), constant_values=True)  # (beyond the sides: wall)
    pool = []
    for source in st['source']:
        ep, name, layer = (*source, k)[:3]  # ((episode, level) or (episode, level, its layer): another layer's pieces)
        src = original(ep, name)
        # (tiles that show nothing, all colour 0, are empty: FLEET's background 3 joins its ships with them)
        seen = {t for t, px in E.preview.tiles(src["shapes"]).items() if px is not None and px.any()}
        grid = [[t if t in seen else 0 for t in row] for row in src['maps'][layer - 1]]
        found = pieces(grid, st.get('max_rows', 20), st.get('min_tiles', 1), st.get('join', 0))
        if st.get('follow'):
            # (what layer 1 had under and round each piece in its original: the layers' bottoms together, one pace)
            w0 = solid_mask(src['maps'][0], src['shapes'])
            off = len(src['maps'][0]) - len(grid)
            keep = []
            for h, w, cells, top, left in found:
                y0, x0 = top + off - 1, left - 1
                if y0 < 0 or y0 + h + 2 > len(w0):
                    continue
                w0p = np.pad(w0, ((0, 0), (1, 2)), constant_values=True)
                keep.append((h, w, cells, w0p[y0:y0 + h + 2, left:left + w + 2]))
            pool += keep
        else:
            pool += [(h, w, cells, None) for h, w, cells, _, _ in found]
    if not pool:
        raise SystemExit(f"{level['name']}: no pieces for background {k}")
    taken = np.zeros((rows, columns), bool)
    out = [[0] * columns for _ in range(rows)]
    over = None
    if st.get('avoid'):
        px = timeline(level)
        over = passes(px[0], px[k - 1], rows)
    off = n1 - rows  # (layer 1's row under an upper row at one pace)
    want = st['fill'] * rows * columns
    cands = []
    for i, (h, w, cells, ctx) in enumerate(pool):
        for y in range(E.UPPER_BLANK, rows - h + 1):
            for x in range(0, columns - w + 1):
                score = rng.random()
                if ctx is not None:
                    y1 = y + off - 1
                    if y1 < 0 or y1 + h + 2 > n1:
                        continue
                    match = float((padded[y1:y1 + h + 2, x:x + w + 2] == ctx).mean())
                    if match < st['follow']:
                        continue
                    score = match + 0.05 * score
                cands.append((score, i, y, x))
    cands.sort(reverse=True)
    if not st.get('follow'):
        rng.shuffle(cands)
    placed = 0
    for score, i, y, x in cands:
        if placed >= want:
            break
        h, w, cells, _ = pool[i]
        # (room round it: a piece doesn't touch another)
        if taken[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1].any():
            continue
        if over is not None:
            hit = False
            for dy in range(h):
                span = over[y + dy]
                if span is None:
                    continue
                lo, hi = span
                for (cy, cx) in cells:
                    if cy != dy:
                        continue
                    # (layer 3 is a column wider: its column c over layer 1's c - 1 and c)
                    xs = range(max(0, x + cx - (k == 3) - 1), min(walls.shape[1], x + cx + 1))
                    a, b = max(0, n1 - 1 - int(hi)), min(n1, n1 - int(lo))
                    if a < b and walls[a:b, xs.start:xs.stop].any():
                        hit = True
                        break
                if hit:
                    break
            if hit:
                continue
        for (cy, cx), t in cells.items():
            out[y + cy][x + cx] = t
        taken[y:y + h, x:x + w] = True
        placed += len(cells)
    print(f"  background {k}: {placed} tiles in pieces ({placed / (rows * columns):.3f} full, wanted {st['fill']}), "
          f"{len(pool)} pieces to lay, {len(cands)} places")
    return out
