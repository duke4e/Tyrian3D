"""The GBC levels' own bosses (episode 7): what they look like and which PC boss is the nearest.

A GBC level's script ends with command 06 (the boss: its code, the level dispatcher with level + 100, runs it from
then on; the script's pointer only follows the map's loop) and 01. Each level is flown in the emulator (Hard, the
ship kept alive and never firing) from there for BOSS_FRAMES frames: the screens (data/gbc/bosses/Lnn_screens.png)
and the boss's look: the largest cluster of sprites on screen, by frame (Lnn_boss.png, the most common large one).
The PC bosses (every original level's of episodes 1-5: waves.Source.boss's body, its pieces at their offsets in
the atlases' first frames) are matched against it as the enemies are (enemies.Matcher's features: silhouette,
shading, size at 1.5x, colour), into data/gbc/bosses/bosses.json and Lnn_match.png.

    python tools/gbc/bosses.py [--levels 23,3,...]
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G  # noqa: E402
import extract as X  # noqa: E402
import enemies as EN  # noqa: E402

OUT = os.path.join(G.ROOT, 'data', 'gbc', 'bosses')
BOSS_FRAMES = 2400
LAYERS = {6: 'ground', 10: 'ground', 17: 'ground', 15: 'sky', 18: 'sky', 7: 'top', 23: 'top', 32: 'top', 12: None}


def script_end(level):
    """The frame the level's main script ends at (its records stop running forwards), or None."""
    d = json.load(open(os.path.join(EN.OUT, f'L{level:02d}.json')))
    pa = pp = -1
    for e in d['executed']:
        if e['at'] < pa or e['pos'] < pp:
            return e['frame']
        pa, pp = e['at'], e['pos']
    return d['executed'][-1]['frame'] if d['executed'] else None  # (the flight ended with the script)


def fly_boss(level):
    """(screens, the boss's sprite clusters by sample) from the script's end on."""
    end = script_end(level)
    if end is None:
        return None
    g, bank, init, c = X.start_level(level)
    g.write(0xd92a, 2)
    for _ in range(end):
        g.write(0xd8da, 8)
        g.run(1, 0)
    screens, clusters = [], []
    for f in range(BOSS_FRAMES):
        g.write(0xd8da, 8)
        g.run(1, 0)
        if f % 30 == 0:
            vram, obpal = g.vram(), G.cgb_rgb(g.obpal())
            cl = [im for im in X.oam_clusters(g, vram, obpal) if im.shape[0] * im.shape[1] >= 24 * 24]
            if cl:
                clusters.append(max(cl, key=lambda im: (im[:, :, 3] > 0).sum()))
        if f % 300 == 0:
            screens.append(Image.fromarray(np.array(g.frame())))
    return screens, clusters


def pc_bosses():
    """[(episode, level name, RGBA composite of the boss's body)] for every original level with a boss."""
    sys.path.insert(0, os.path.join(G.ROOT, 'tools', 'content', 'episode6'))
    import waves
    import levels as lv
    cells = {}
    for c in EN.atlas():
        if c[5] == 1:
            cells.setdefault((c[0], c[1]), c[4][4:32, 4:28])
    out, seen = [], set()
    for ep in range(1, 6):
        for s in lv.read_strings(os.path.join(G.ROOT, 'data', 'tyrian2000', f'levels{ep}.dat')):
            if not s.startswith(']L'):
                continue
            name = s[13:22].strip()
            try:
                src = waves.Source(ep, name)
                b = src.boss()
            except Exception:
                continue
            if not b:
                continue
            sp = [e for e in b['events'] if e['type'] in LAYERS and e['d1'] > 0 and e['d4'] in b['links']]
            if not sp:
                continue
            t0 = min(e['t'] for e in sp)
            parts = []
            for e in sp:
                if e['t'] > t0 + 60:
                    continue
                if e['type'] == 12:
                    for k, (dx, dy) in enumerate([(0, 28), (24, 28), (0, 0), (24, 0)]):
                        parts.append((e['d1'] + k, e['d2'] + dx, e['d5'] - 28 + dy))
                else:
                    parts.append((e['d1'], e['d2'], e['d5']))
            parts = list(dict.fromkeys(parts))
            key = tuple(sorted(parts))
            if key in seen or not parts:
                continue
            seen.add(key)
            x0, y0 = min(x for _, x, _ in parts), min(y for _, _, y in parts)
            w, h = max(x for _, x, _ in parts) - x0 + 24, max(y for _, _, y in parts) - y0 + 28
            if w > 400 or h > 400:
                continue
            comp = Image.new('RGBA', (w, h))
            for n, x, y in parts:
                c = cells.get((ep, n))
                if c is not None:
                    comp.alpha_composite(Image.fromarray(c), (x - x0, y - y0))
            out.append((ep, name, np.array(comp), [list(p) for p in parts]))
    return out


def score(gbc, cands):
    """Each candidate's likeness to the GBC boss (enemies.py's features: silhouette, shading, size, colour)."""
    f = EN.features(gbc)
    if f is None:
        return [-9.0] * len(cands)
    m, l, size, colour = f
    out = []
    for c in cands:
        g = EN.features(c[2])
        if g is None:
            out.append(-9.0)
            continue
        sim = float(EN.unit(g[0]) @ EN.unit(m)) * 0.6 + float(EN.unit(g[1]) @ EN.unit(l)) * 0.4
        pen = float(np.abs(np.log((g[2] + 1) / (size * 1.5 + 1))).sum())
        dc = float(np.sqrt(((g[3][1:] - colour[1:]) ** 2).sum()) + 0.3 * abs(g[3][0] - colour[0]))
        out.append(sim - 0.3 * pen - 0.015 * dc)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', default=','.join(str(i) for i in range(1, 25)))
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cands = pc_bosses()
    print(f'{len(cands)} PC bosses')
    path = os.path.join(OUT, 'bosses.json')
    found = json.load(open(path)) if os.path.exists(path) else {}
    for level in [int(x) for x in a.levels.split(',')]:
        r = fly_boss(level)
        if r is None:
            print(f'L{level:02d}: no script end')
            continue
        screens, clusters = r
        sheet = Image.new('RGB', (166 * len(screens), 146))
        for i, s in enumerate(screens):
            sheet.paste(s, (i * 166, 0))
        sheet.save(os.path.join(OUT, f'L{level:02d}_screens.png'))
        big = [c for c in clusters if (c[:, :, 3] > 0).sum() >= 600]
        if not big:
            found[str(level)] = None
            print(f'L{level:02d}: no boss sprites')
            continue
        # the boss's look: its largest frequent cluster (by size)
        keys = {}
        for c in big:
            keys.setdefault(c.shape[:2], []).append(c)
        look = max(keys.values(), key=lambda v: len(v) * (v[0][:, :, 3] > 0).sum())[0]
        Image.fromarray(look).save(os.path.join(OUT, f'L{level:02d}_boss.png'))
        s = score(look, cands)
        order = np.argsort(s)[::-1][:6]
        found[str(level)] = dict(size=list(look.shape[:2]), candidates=[dict(episode=cands[i][0], name=cands[i][1],
                                                                             score=round(s[i], 3)) for i in order])
        row = Image.new('RGB', (130 + 6 * 140, 150), (24, 24, 24))
        dr = ImageDraw.Draw(row)
        g_ = Image.fromarray(look)
        g_ = g_.resize((g_.width * 2, g_.height * 2), Image.NEAREST)
        row.paste(g_, (0, 0), g_)
        for k, i in enumerate(order):
            im = Image.fromarray(cands[i][2])
            sc = min(130 / im.width, 130 / im.height, 1.0)
            im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))))
            row.paste(im, (130 + k * 140, 0), im)
            dr.text((130 + k * 140, 136), f'{cands[i][0]}:{cands[i][1][:9]} {s[i]:.2f}', fill=(255, 255, 0))
        row.save(os.path.join(OUT, f'L{level:02d}_match.png'))
        print(f'L{level:02d}: boss {look.shape[1]}x{look.shape[0]}, best', [(cands[i][0], cands[i][1], round(s[i], 2)) for i in order[:3]])
    json.dump(found, open(path, 'w'), indent=1)


if __name__ == '__main__':
    main()
