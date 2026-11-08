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
    # (spec `bottom_row`: the map's first row that tile all along: SAVARA II's starts in open water, not on the stray
    # dock edges its GBC map's frame made)
    if spec.get('bottom_row') is not None:
        out[E.ROWS - 1] = [spec['bottom_row']] * 14
    return out, gmap, img, letter


if __name__ == '__main__':
    n = int(sys.argv[1])
    spec = E.spec_of(n)
    out, gmap, img, letter = layer(spec)
    D.picture(out, gmap, img, letter).save(sys.argv[2] if len(sys.argv) > 2 else f'remake_L{n:02d}.png')
