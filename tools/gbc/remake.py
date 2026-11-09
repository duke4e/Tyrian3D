"""Episode 7's layer 1, 1:1 after the GBC map (a PC cell a GBC block), by the method the level's spec names (`remake`),
as the user's map reviews chose per level (2026-11-07/08):

    autotile    episode.autotile aligned (the committed maps' way: CAMANIS, ICE EXIT, the SAVARAs looked best so)
    corners     corners.py (materials at the blocks' corners, the originals' transition tiles; templates, block_like)
    ships       ships.py (FLEET: the original's ships whole where the GBC map has ships)
    fitted      dictionary.fitted (BUBBLES, WARP: the dictionary's tiles, given up where they wouldn't join)
    dictionary  dictionary.lay (the dictionary as it is: AST.BONUS, LAVA II)

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
    # (spec `bottom_row`: the map's first row that tile all along: SAVARA II's starts in open water, not on the stray
    # dock edges its GBC map's frame made)
    if spec.get('bottom_row') is not None:
        out[E.ROWS - 1] = [spec['bottom_row']] * 14
    return out, gmap, img, letter


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


def upper(spec, gmap):
    """Spec `upper_stamps`: dict(layer=2, source=(episode, level), source_layer=3, pieces=[(row, column, rows, columns)],
    blocks=[...]): where the GBC map has a structure of those blocks (DELIANI's pink-windowed machines), the source
    layer's piece nearest it in size, centred on it, in that upper layer, its rows 300 above layer 1's (the layers start
    at rows 292 and 592, so at layer 1's pace a row of the upper layer stands over its layer-1 row; the wide playfield
    has the second layer 2 px off the first, tyrian2.c WIDE_OFS1/2: its columns over layer 1's). The user on DELIANI: the
    PC level is two layers, the plates and islands below and "ostalo napravimo s drugim layerom". Returns (layer index,
    {(row, column): tile})."""
    st = spec.get('upper_stamps')
    if not st:
        return None, {}
    src = [l for l in E.sources.original_levels() if (l['episode'], l['name']) == tuple(st['source'])][0]
    grid = src['maps'][st.get('source_layer', st['layer']) - 1]
    pieces = [[row[x:x + w] for row in grid[y:y + h]] for y, x, h, w in st['pieces']]
    blocks = set(st['blocks'])
    h, w = len(gmap), len(gmap[0])
    seen, out = set(), {}
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
            gh, gw = max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
            piece = min(pieces, key=lambda p: abs(len(p) - gh) + abs(len(p[0]) - gw))
            ph, pw = len(piece), len(piece[0])
            r0 = E.ROWS - h + min(ys) + (gh - ph) // 2 + E.ROWS  # (the upper layer's row over layer 1's)
            c0 = min(max(D.LEFT + min(xs) + (gw - pw) // 2, 0), 14 - pw)
            for y in range(ph):
                for x in range(pw):
                    if piece[y][x] and 0 <= r0 + y < 2 * E.ROWS:
                        out[(r0 + y, c0 + x)] = piece[y][x]
    return st['layer'] - 1, out


if __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    out, gmap, img, letter = layer(spec)
    D.picture(out, gmap, img, letter).save(sys.argv[2] if len(sys.argv) > 2 else f'remake_L{n:02d}.png')
