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
