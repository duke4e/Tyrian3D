#!/usr/bin/env python3
"""The GBC game's screen where each enemy type of a level first shows whole, for telling what a type is by its
surroundings (the user, 2026-11-05: "za neke spriteove bi trebali screenshote iz gba igre/levela, jer ovako im se baš
ne može odrediti kontekst"): the level flown in the emulator as enemies.py flies it, and for each type the first frames
its spawned enemy's sprites stand inside the screen, a box round them. Written to data/gbc/context/Lnn_typeXX.png
(the screen 3x, the box yellow) and Lnn_typeXX_b.png (a second look a second later, where there is one).

    python tools/gbc/context.py [level...]      (GBC level numbers, default all)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gb as G  # noqa: E402
import extract as X  # noqa: E402
import enemies as EN  # noqa: E402

OUT = os.path.join(G.ROOT, 'data', 'gbc', 'context')
FRAMES = 40000     # at most (a level ends sooner: its script idle for 3000 frames)
SCALE = 3
SECOND = 60        # frames between a type's first look and its second


def clusters(g):
    """The OAM sprites grouped as oam_clusters groups them: [(x0, y0, x1, y1)] screen boxes."""
    oam = g.oam().reshape(40, 4)
    spr = [(int(sx) - 8, int(sy) - 16) for sy, sx, t, a in oam if 0 < sy < 160 and 0 < sx < 168]
    n = len(spr)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if abs(spr[i][0] - spr[j][0]) <= 8 and abs(spr[i][1] - spr[j][1]) <= 16:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(spr[i])
    return [(min(s[0] for s in grp), min(s[1] for s in grp), max(s[0] for s in grp) + 8, max(s[1] for s in grp) + 16)
            for grp in groups.values()]


def shot(g, box, path):
    im = Image.fromarray(g.frame()).resize((160 * SCALE, 144 * SCALE), Image.NEAREST)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = (v * SCALE for v in box)
    for k in range(3):
        d.rectangle([x0 - 3 - k, y0 - 3 - k, x1 + 2 + k, y1 + 2 + k], outline=(255, 214, 0) if k != 1 else (0, 0, 0))
    im.save(path)


def level(n):
    rom = open(G.ROM, 'rb').read()
    g, bank, init, c = X.start_level(n)
    g.write(0xd92a, 2)  # (Hard: Normal's spawns and the Hard-only ones, as enemies.py)
    ptr = g.read(0xc457) | (g.read(0xc458) << 8)
    idle, pending, done = 0, [], {}
    for f in range(FRAMES):
        g.write(0xd8da, 8)  # (the ship's armour kept full)
        before = EN.enemy_structs(g)
        g.run(1, 0)
        new = g.read(0xc457) | (g.read(0xc458) << 8)
        idle = idle + 1 if new == ptr else 0
        if idle > 3000:
            break
        recs, p = [], ptr
        while p != new and len(recs) < 64:
            recs.append(list(rom[X.rom_off(bank, p):X.rom_off(bank, p) + 5]))
            p += 5
        ptr = new
        spawned = [r for r in recs if r[0] in EN.SPAWNS or r[0] >= 0x28]
        if spawned:
            after = EN.enemy_structs(g)
            fresh = after[len(before):] if len(after) > len(before) else []
            for r, st in zip(spawned, fresh):
                if done.get(r[1], 0) < 2:
                    pending.append(dict(type=r[1], group=st[0x0d], x=st[0], y=st[1], left=600, at=-1))
        if not pending:
            continue
        structs = EN.enemy_structs(g)
        scx = int(g.io()[0x43])
        boxes = None
        for pd in pending:
            same = [st for st in structs if st[0x0d] == pd['group']]
            if not same:
                pd['left'] = 0
                continue
            st = min(same, key=lambda st: abs(st[0] - pd['x']) + abs(st[1] - pd['y']))
            pd['x'], pd['y'] = st[0], st[1]
            if boxes is None:
                boxes = clusters(g)
            ox, oy = (st[0] - scx) & 255, (st[1] - 1) & 255
            near = [b for b in boxes if abs(b[0] + 8 - ox) + abs(b[1] + 16 - oy) < 24]
            if near:
                b = min(near, key=lambda b: abs(b[0] + 8 - ox) + abs(b[1] + 16 - oy))
                whole = b[0] >= 2 and b[1] >= 2 and b[2] <= 158 and b[3] <= 142
                t = pd['type']
                if whole and done.get(t, 0) == 0 and pd['at'] < 0:
                    shot(g, b, os.path.join(OUT, f'L{n:02d}_type{t:02x}.png'))
                    done[t] = 1
                    pd['at'] = f
                elif whole and done.get(t, 0) == 1 and pd['at'] >= 0 and f - pd['at'] >= SECOND:
                    shot(g, b, os.path.join(OUT, f'L{n:02d}_type{t:02x}_b.png'))
                    done[t] = 2
                    pd['left'] = 0
            pd['left'] -= 1
        pending[:] = [pd for pd in pending if pd['left'] > 0]
    return done


def main():
    os.makedirs(OUT, exist_ok=True)
    levels = [int(a) for a in sys.argv[1:]] or list(range(1, 25))
    for n in levels:
        done = level(n)
        print(f'L{n:02d}: {len(done)} types, {sum(1 for v in done.values() if v == 2)} with a second look', flush=True)


if __name__ == '__main__':
    main()
