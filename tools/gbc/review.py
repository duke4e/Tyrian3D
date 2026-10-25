"""Sheets for checking the GBC enemy types' PC enemies by eye (tools/gbc/enemy_overrides.json).

For each level, data/gbc/enemies/Lnn_review.png: one row per look of the GBC types the level's script
spawns (types drawn alike share a row; most spawned first), with the GBC sprite, the PC enemy the level
uses now (episode.py's choice after the overrides, data/gbc/enemies/Lnn_chosen.json) and the six best
candidates, each with the sprite sheets it needs (green: loaded in the level; the composites' parts, to
copy into the overrides, in Lnn_review.txt); and Lnn_pool.png: every
enemy the original levels it condenses spawn (enemies.py: pool), labelled episode:enemy, to pick from.

    python tools/gbc/review.py [--levels 23,3,...]      (after episode.py)
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enemies as EN  # noqa: E402
import episode as E  # noqa: E402

D = EN.OUT
CELL = 56
COL = 92


def thumb(rgba, h=CELL):
    im = Image.fromarray(rgba) if isinstance(rgba, np.ndarray) else rgba
    k = min(h / im.height, (COL - 4) / im.width, 3)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)


def label(parts):
    """b: event 12's block; cN: a composite of N (its parts in Lnn_review.txt)."""
    return '' if parts == 1 else 'b' if parts == 4 else f'c{len(parts)}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', default=','.join(str(i) for i in range(1, 25)))
    a = ap.parse_args()
    cells = {}
    for c in EN.atlas():
        cells.setdefault((c[0], c[1], c[5]), c[4])
    data = {}

    def sheets(ep, n, parts):
        if ep not in data:
            data[ep] = E.sources.tyrdata.load_items(ep)['enemies']
        return set().union(*(E.waves.sheets_of(data[ep], m) for m in EN.part_numbers(n, parts)))
    spec_of = {s['gbc']: s for s in E.LEVELS}
    for level in [int(x) for x in a.levels.split(',')]:
        d = json.load(open(os.path.join(D, f'L{level:02d}.json')))
        chosen = json.load(open(os.path.join(D, f'L{level:02d}_chosen.json')))
        banks = set(chosen['banks'])
        use = Counter(r['rec'][1] for r in d['executed'] if r['rec'][0] in (3, 4, 0x21, 0x22, 0x23, 0x24) or r['rec'][0] >= 0x28)
        looks = {}
        for t in d['types']:
            p = os.path.join(D, f'L{level:02d}_type{int(t):02x}.png')
            if os.path.exists(p):
                im = np.array(Image.open(p).convert('RGBA'))
                looks.setdefault(im.tobytes() + bytes(im.shape[:2]), (im, []))[1].append(int(t))
        rows, text = [], []
        for im, ts in sorted(looks.values(), key=lambda v: -sum(use[t] for t in v[1])):
            row = Image.new('RGB', (COL * 8, CELL + 30), (24, 24, 24))
            dr = ImageDraw.Draw(row)
            g = thumb(im)
            row.paste(g, (0, 0), g)
            dr.text((2, CELL + 2), ' '.join(f'{t:02x}' for t in sorted(ts)), fill=(255, 255, 255))
            dr.text((2, CELL + 15), f'x{sum(use[t] for t in ts)}', fill=(160, 160, 160))
            now = [(v[0], v[1], EN.parts_key(v[2])) for v in (chosen['types'].get(f'{t:02x}') for t in ts) if v]
            cands = [(c['episode'], c['enemy'], EN.parts_key(c.get('parts', 1))) for c in d['types'][str(ts[0])].get('candidates', [])]
            cands = [c for c in cands if c in cells][:6]
            for k, c in enumerate(([Counter(now).most_common(1)[0][0]] if now else [None]) + cands):
                x = COL * (k + 1) + 4
                if c is None:
                    dr.text((x, 20), 'none', fill=(255, 80, 80))
                    continue
                if c in cells:
                    t_ = thumb(cells[c])
                    row.paste(t_, (x, 0), t_)
                b = sheets(*c) - {0}
                dr.text((x, CELL + 2), f"{'=' if k == 0 else ''}{c[0]}:{c[1]}{label(c[2])}",
                        fill=(255, 220, 0) if k == 0 else (220, 220, 220))
                dr.text((x, CELL + 15), ','.join(str(v) for v in sorted(b)),
                        fill=(110, 230, 110) if b <= banks else (230, 120, 120))
            rows.append(row)
            for c in ([Counter(now).most_common(1)[0][0]] if now else []) + cands:
                if not isinstance(c[2], int):
                    text.append(f"{' '.join(f'{t:02x}' for t in sorted(ts))}: [{c[0]}, {json.dumps([list(p) for p in c[2]])}]")
        open(os.path.join(D, f'L{level:02d}_review.txt'), 'w').write('\n'.join(dict.fromkeys(text)) + '\n')
        if rows:
            out = Image.new('RGB', (rows[0].width, 16 + len(rows) * (CELL + 32)), (0, 0, 0))
            ImageDraw.Draw(out).text((4, 2), f"L{level:02d} {spec_of[level]['name'] if 'name' in spec_of[level] else ''}"
                                             f"  sheets {chosen['banks']}", fill=(255, 255, 255))
            for i, r in enumerate(rows):
                out.paste(r, (0, 16 + i * (CELL + 32)))
            out.save(os.path.join(D, f'L{level:02d}_review.png'))
        # the pool: every enemy of the original levels it condenses
        spec = spec_of[level]
        pool = sorted(EN.pool([tuple(m) for m in spec.get('pool', spec.get('maps', [spec['pc']]))]))
        seen, items = set(), []
        for ep, n in pool:
            c = cells.get((ep, n, 1))
            if c is None or c.tobytes() in seen:
                continue
            seen.add(c.tobytes())
            items.append((f'{ep}:{n}', ','.join(str(v) for v in sorted(sheets(ep, n, 1) - {0})), c))
        cols = 12
        out = Image.new('RGB', (cols * 64, ((len(items) + cols - 1) // cols) * 84), (24, 24, 24))
        dr = ImageDraw.Draw(out)
        for i, (name, b, c) in enumerate(items):
            im = Image.fromarray(c).resize((48, 54), Image.NEAREST)
            x, y = (i % cols) * 64, (i // cols) * 84
            out.paste(im, (x + 8, y), im)
            dr.text((x + 4, y + 58), name, fill=(220, 220, 220))
            dr.text((x + 4, y + 70), b, fill=(150, 150, 150))
        out.save(os.path.join(D, f'L{level:02d}_pool.png'))
        print(f'L{level:02d}: {len(rows)} looks, pool {len(items)}, sheets {chosen["banks"]}')


if __name__ == '__main__':
    main()
