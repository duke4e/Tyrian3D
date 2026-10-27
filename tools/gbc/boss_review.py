"""The GBC bosses beside their PC versions, for review by eye (episode 7): data/gbc/bosses/Lnn_pieces.png.

Left the GBC boss as bosses.py saw it (Lnn_boss.png at 1.5x), right its pieces as the level has them (episode.py,
boss.py): each PC part's first frame at the GBC piece's place (1.5x), with the piece's GBC type and group; below the
PC boss's own body. Wrong looks go to tools/gbc/boss_overrides.json ({"Lnn": {"type": [enemy, layer event]}}).

    python tools/gbc/boss_review.py
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G  # noqa: E402
import enemies as EN  # noqa: E402

OUT = os.path.join(G.ROOT, 'data', 'gbc', 'bosses')


def main():
    cells = {}
    for c in EN.atlas():
        if c[5] == 1:
            cells.setdefault((c[0], c[1]), Image.fromarray(c[4][4:32, 4:28]))
    rom = json.load(open(os.path.join(OUT, 'rom.json')))
    for path in sorted(glob.glob(os.path.join(G.ROOT, 'data', 'gbc', 'episode7', 'levels', '*.json'))):
        level = json.load(open(path))
        gb = level.get('gbc_boss')
        if not gb:
            continue
        n = level['gbc']
        bd = rom[str(n)]
        import boss as B
        units = B.units_of(bd, [i - bd['first'] for i in bd['pieces']])
        x0 = min(u['x'] for u in units)
        y0 = min(u['y'] for u in units)
        w = (max(u['x'] for u in units) + 16 - x0) * 1.5 + 24
        h = (max(u['y'] for u in units) + 16 - y0) * 1.5 + 28
        sheet = Image.new('RGBA', (int(max(w, 100)) + 260, int(max(h, 150)) + 20), (24, 24, 24, 255))
        dr = ImageDraw.Draw(sheet)
        p = os.path.join(OUT, f'L{n:02d}_boss.png')
        if os.path.exists(p):
            g = Image.open(p).convert('RGBA')
            g = g.resize((int(g.width * 1.5), int(g.height * 1.5)), Image.NEAREST)
            sheet.paste(g, (0, 0), g)
        for (t, grp, look), u in zip(gb['looks'], units):
            x, y = 250 + (u['x'] - x0) * 1.5, (u['y'] - y0) * 1.5
            ep = level['gbc_boss']['records'][0]['base'][0] if level['gbc_boss']['records'] and level['gbc_boss']['records'][0]['base'] else 1
            im = cells.get((ep, look[0])) if look else None
            if im is not None:
                sheet.paste(im, (int(x), int(y)), im)
            dr.text((int(x) + 2, int(y) + 2), f'{t:02x}', fill=(255, 255, 0))
            dr.text((int(x) + 2, int(y) + 12), f'g{grp}', fill=(0, 255, 255))
        dr.text((4, sheet.height - 14), f"L{n:02d} {level['name']}: {len(units)} pieces", fill=(255, 255, 255))
        sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
        sheet.save(os.path.join(OUT, f'L{n:02d}_pieces.png'))
        print(n, level['name'], len(units))


if __name__ == '__main__':
    main()
