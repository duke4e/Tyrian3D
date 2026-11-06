#!/usr/bin/env python3
"""The GBC game's screen where each enemy type of a level first shows whole, for telling what a type is by its
surroundings (the user, 2026-11-05: "za neke spriteove bi trebali screenshote iz gba igre/levela, jer ovako im se baš
ne može odrediti kontekst"): the level flown in the emulator as enemies.py flies it, and for each type the first frames
its spawned enemy's own sprites stand inside the screen (the struct's two OAM slots, a block's pieces together:
not the neighbours touching it, which the first version boxed too), a box round them. Written to data/gbc/context/Lnn_typeXX.png
(the screen 3x, the box yellow) and Lnn_typeXX_b.png (a second look a second later, where there is one), and Lnn_typeXX_frames.png: the type's own looks as they showed,
most often seen first (2026-11-06). --types=21,2b: only those types.

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
    im = Image.fromarray(g if isinstance(g, np.ndarray) else g.frame()).resize((160 * SCALE, 144 * SCALE), Image.NEAREST)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = (v * SCALE for v in box)
    for k in range(3):
        d.rectangle([x0 - 3 - k, y0 - 3 - k, x1 + 2 + k, y1 + 2 + k], outline=(255, 214, 0) if k != 1 else (0, 0, 0))
    im.save(path)


def own(g, sts):
    """An enemy's own sprites (each struct's two OAM slots, bytes 0x12 and 0x13; a block's pieces together, not its
    neighbours'): (screen box, RGBA picture) or None when none shows."""
    oam = g.oam().reshape(40, 4)
    scx = int(g.io()[0x43])
    spr = []
    for st in sts:
        for s_ in (st[0x12], st[0x13]):
            if s_ < 40:
                y, x, t, a = (int(v) for v in oam[s_])
                # (a slot the enemy holds draws it there: OAM x = its x - SCX, y = its y; a stale slot, before it
                # is drawn, may hold another's sprite: the ship's)
                near = abs(((x - st[0] + scx + 128) & 255) - 128) <= 8 and abs(((y - st[1] + 128) & 255) - 128) <= 8
                if near and 0 < y < 160 and 0 < x < 168:
                    spr.append((x - 8, y - 16, t & 0xfe, a))
    if not spr:
        return None
    x0, y0 = min(s_[0] for s_ in spr), min(s_[1] for s_ in spr)
    x1, y1 = max(s_[0] for s_ in spr) + 8, max(s_[1] for s_ in spr) + 16
    vram, obpal = g.vram(), G.cgb_rgb(g.obpal())
    img = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    for x, y, t, a in reversed(spr):
        for half in range(2):
            px = X.tile_px(vram, ((t + half) * 16) + (0x2000 if a & 8 else 0))
            if a & 0x20:
                px = px[:, ::-1]
            rgb = obpal[a & 7][px]
            blk = np.dstack([rgb, np.where(px > 0, 255, 0).astype(np.uint8)])
            yy = y - y0 + ((1 - half) * 8 if a & 0x40 else half * 8)
            if a & 0x40:
                blk = blk[::-1]
            sub = img[yy:yy + 8, x - x0:x - x0 + 8]
            m = blk[:, :, 3] > 0
            sub[m] = blk[m]
    return (x0, y0, x1, y1), img


def frames_strip(found, path):
    """A type's own looks, most often seen first (at most 10, 6x), each with how many times it was seen."""
    items = sorted(found.values(), key=lambda e: -e[1])[:10]
    S = 6
    W = sum(e[0].shape[1] * S + 12 for e in items) + 12
    H = max(e[0].shape[0] * S for e in items) + 28
    out = Image.new('RGBA', (max(W, 120), H), (36, 40, 46, 255))
    d = ImageDraw.Draw(out)
    x = 12
    for im, n in items:
        pim = Image.fromarray(im, 'RGBA').resize((im.shape[1] * S, im.shape[0] * S), Image.NEAREST)
        out.alpha_composite(pim, (x, 22))
        d.text((x, 5), f'x{n}', fill=(255, 214, 0, 255))
        x += pim.width + 12
    out.save(path)


def level(n, want=None):
    import glob
    for old in glob.glob(os.path.join(OUT, f'L{n:02d}_type*.png')):  # (the level's earlier looks: made anew)
        if want is None or int(os.path.basename(old)[8:10], 16) in want:
            os.remove(old)
    rom = open(G.ROM, 'rb').read()
    g, bank, init, c = X.start_level(n)
    g.write(0xd92a, 2)  # (Hard: Normal's spawns and the Hard-only ones, as enemies.py)
    ptr = g.read(0xc457) | (g.read(0xc458) << 8)
    idle, pending, done, waiting = 0, [], {}, []
    looks = {}  # type -> picture hash -> [picture, times seen]
    for f in range(FRAMES):
        g.write(0xd8da, 8)  # (the ship's armour kept full)
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
        for r in spawned:
            if (want is None or r[1] in want) and len([pd for pd in pending if pd['type'] == r[1]]) < 3:
                # (a block record makes its pieces' structs, columns x rows)
                b = r[0] - 0x28
                count = (((b >> 1) & 3) + 1) * ((b >> 3) + 1) if r[0] >= 0x28 else 1
                waiting.append(dict(type=r[1], group=r[4], x=r[2], y=r[3], count=count, age=0))
        if waiting:
            # (the record's enemy: of its group the structs nearest where it spawns, once they are there: the table is
            # compacted and a struct can come a few frames after its record)
            after = EN.enemy_structs(g)
            taken = {p_ for pd in pending for p_ in pd['pos']}
            for w in waiting:
                near = sorted((abs(st[0] - w['x']) + abs(((st[1] - w['y'] + 128) & 255) - 128), i) for i, st in enumerate(after)
                              if st[0x0d] == w['group'] and (st[0], st[1]) not in taken)
                near = [(d_, i) for d_, i in near if d_ <= 40][:w['count']]
                w['age'] += 1
                if len(near) == w['count']:
                    sts = [after[i] for _, i in near]
                    taken |= {(st[0], st[1]) for st in sts}
                    pending.append(dict(type=w['type'], group=w['group'], pos=[(st[0], st[1]) for st in sts], left=900, at=-1,
                                        best=None))
                    w['age'] = 999
            waiting[:] = [w for w in waiting if w['age'] < 90]
        if not pending or f % 2:
            continue
        structs = EN.enemy_structs(g)
        for pd in pending:
            same = [st for st in structs if st[0x0d] == pd['group']]
            if not same:
                pd['left'] = 0
                continue
            mine = []
            for i, (x, y) in enumerate(pd['pos']):
                st = min(same, key=lambda st: abs(st[0] - x) + abs(st[1] - y))
                pd['pos'][i] = (st[0], st[1])
                mine.append(st)
            got = own(g, mine)
            pd['left'] -= 2
            if got is None:
                continue
            box, img = got
            t = pd['type']
            whole = box[0] >= 1 and box[1] >= 1 and box[2] <= 159 and box[3] <= 143
            if whole:
                h = hash(img.tobytes()) ^ hash(img.shape)
                e = looks.setdefault(t, {}).setdefault(h, [img, 0])
                e[1] += 1
            if not whole and done.get(t, 0) == 0:
                # (one never whole on the screen, at its edge: its most shown look, kept for the end)
                area = img.shape[0] * img.shape[1]
                if pd['best'] is None or area > pd['best'][0]:
                    pd['best'] = (area, g.frame().copy(), box, img)
            if whole and done.get(t, 0) == 0 and pd['at'] < 0:
                shot(g, box, os.path.join(OUT, f'L{n:02d}_type{t:02x}.png'))
                done[t] = 1
                pd['at'] = f
            elif whole and done.get(t, 0) == 1 and pd['at'] >= 0 and f - pd['at'] >= SECOND:
                shot(g, box, os.path.join(OUT, f'L{n:02d}_type{t:02x}_b.png'))
                done[t] = 2
        for pd in pending:
            if pd['left'] <= 0 and pd['best'] and done.get(pd['type'], 0) == 0:
                _, frame, box, img = pd['best']
                shot(frame, box, os.path.join(OUT, f"L{n:02d}_type{pd['type']:02x}.png"))
                looks.setdefault(pd['type'], {})[0] = [img, 1]
                done[pd['type']] = 1
        pending[:] = [pd for pd in pending if pd['left'] > 0]
    for t, found in looks.items():
        frames_strip(found, os.path.join(OUT, f'L{n:02d}_type{t:02x}_frames.png'))
    return done


def main():
    os.makedirs(OUT, exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith('--types=')]
    want = next((set(int(t, 16) for t in a[8:].split(',')) for a in sys.argv[1:] if a.startswith('--types=')), None)
    levels = [int(a) for a in args] or list(range(1, 25))
    for n in levels:
        done = level(n, want)
        print(f'L{n:02d}: {len(done)} types, {sum(1 for v in done.values() if v == 2)} with a second look', flush=True)


if __name__ == '__main__':
    main()
