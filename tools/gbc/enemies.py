"""The GBC levels' enemies: their scripts and each enemy type's PC enemy (tools/gbc, episode 7).

Each level is flown in the emulator on Hard (every type shows; the ship kept alive, never firing, so
every enemy lives out its path) while its script runs; for every spawn the new enemy's sprites (the OAM cluster at its place)
are drawn, and each GBC enemy type gets the PC enemy whose sprite looks most like it (the PC sprites,
made small, are what the GBC game shows: silhouette and shading against the PC atlases in
upscale/in, at the 1.5x scale; the original level's episode first). Writes data/gbc/enemies/Lnn.json
(the script as executed at Normal: positions and records; the types and their PC enemies; where the level's
type and gun tables are, types_at and guns_at: tools/gbc/boss_rom.py reads them) and a sheet of the matches
for review.

    python tools/gbc/enemies.py [--levels 23,3,...] [--tables]
(--tables: only the tables' places, into the Lnn.json there are, without flying)
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

OUT = os.path.join(G.ROOT, 'data', 'gbc', 'enemies')
ATLAS = os.path.join(G.ROOT, 'upscale', 'in')
ENEMIES, STRUCT = 0xc192, 29          # the enemy table ($c47d enemies of 29 bytes)
SPAWNS = {3, 4, 0x21, 0x22, 0x23, 0x24}


def rom_word(rom, bank, a):
    return rom[X.rom_off(bank, a)] | (rom[X.rom_off(bank, a + 1)] << 8)


def enemy_structs(g):
    w = g.wram()  # ($c000-$cfff: WRAM bank 0)
    n = int(w[0x47d])
    base = ENEMIES - 0xc000
    return [[int(v) for v in w[base + i * STRUCT:base + (i + 1) * STRUCT]] for i in range(n)]


def cluster_at(g, x, y):
    """The OAM sprites around an enemy at (x, y) (struct coordinates: screen x = x - SCX - 8 + 8,
    OAM y = y - 1; found by comparing structs with the OAM), drawn from VRAM: RGBA or None."""
    vram, obpal = g.vram(), G.cgb_rgb(g.obpal())
    scx = int(g.io()[0x43])
    ox, oy = (x - scx) & 255, (y - 1) & 255
    imgs = X.oam_clusters(g, vram, obpal)
    oam = g.oam().reshape(40, 4)
    best, bd = None, 1e9
    # the clusters in the order oam_clusters makes them: find the one whose sprites are nearest
    spr = [(int(sx) - 8, int(sy) - 16) for sy, sx, t, a in oam if 0 < sy < 160 and 0 < sx < 168]
    if not spr:
        return None
    # oam_clusters gives images only; recompute the clusters' boxes the same way
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
    for k, grp in enumerate(groups.values()):
        cx = int(min(s[0] for s in grp)) + 8
        cy = int(min(s[1] for s in grp)) + 16
        d = abs(cx - ox) + abs(cy - oy)
        if d < bd and k < len(imgs):
            best, bd = imgs[k], d
    return best if bd < 24 else None


def fly(level, frames):
    """Flies a level; returns its script as executed (frame, position, record bytes) and, for each
    GBC enemy type, the images of the enemies spawned with it."""
    rom = open(G.ROM, 'rb').read()
    g, bank, init, c = X.start_level(level)
    types_at, guns_at = tables(g)
    g.write(0xd92a, 2)  # on Hard: its spawns are Normal's and the Hard-only ones (records 21/22, skips 00)
    pos_list, rec_list = c['events_pos'], c['events']
    executed, types, pending = [], {}, []
    ptr = g.read(0xc457) | (g.read(0xc458) << 8)
    idle = 0
    for f in range(frames):
        g.write(0xd8da, 8)  # the ship's armour kept full
        before = enemy_structs(g)
        g.run(1, 0)
        new = g.read(0xc457) | (g.read(0xc458) << 8)
        if new == ptr:
            idle += 1
            if idle > 3000:
                break
        else:
            idle = 0
        pos = (g.read(0xc439) << 8) | g.read(0xc43a)
        recs = []
        p = ptr
        while p != new and len(recs) < 64:
            r = list(rom[X.rom_off(bank, p):X.rom_off(bank, p) + 5])
            recs.append(r)
            executed.append(dict(frame=f, pos=pos, at=(p - rec_list) // 5, rec=r))
            p += 5
        ptr = new
        spawned = [r for r in recs if r[0] in SPAWNS or r[0] >= 0x28]
        if spawned:
            after = enemy_structs(g)
            fresh = after[len(before):] if len(after) > len(before) else []
            for r, st in zip(spawned, fresh):
                pending.append(dict(type=r[1], group=st[0x0d], x=st[0], y=st[1], left=60))
                t = types.setdefault(r[1], dict(images=[], groups=set()))
                t['groups'].add(r[4])
        # the new enemies' sprites, once they show (followed by group and nearest place)
        if pending:
            structs = enemy_structs(g)
            for pd in pending:
                same = [st for st in structs if st[0x0d] == pd['group']]
                if same:
                    st = min(same, key=lambda st: abs(st[0] - pd['x']) + abs(st[1] - pd['y']))
                    pd['x'], pd['y'] = st[0], st[1]
                    img = cluster_at(g, st[0], st[1])
                    t = types[pd['type']]
                    if img is not None:
                        if len(t['images']) < 12:
                            t['images'].append(img)
                        pd['left'] = 0
                pd['left'] -= 1
            pending[:] = [pd for pd in pending if pd['left'] > 0]
    return dict(bank=bank, events_pos=pos_list, events=rec_list, executed=executed, types=types,
                types_at=types_at, guns_at=guns_at)


def tables(g):
    """Where the level's enemy types ($c453: 10 bytes each) and guns ($c451) are, its init having set them."""
    w = lambda a: g.read(a) | g.read(a + 1) << 8
    return w(0xc453), w(0xc451)


def atlas():
    """The PC enemies' frames from the atlases (cells of 32x36 with the 24x28 sprite at 4,4):
    (episode, enemy, sheet, sprite, RGBA, parts), and the 4-part enemies (event 12: enemies d1..d1+3
    as a 2x2 block, part 1 right of part 0, 2 above it, 3 above 1) of the original levels as 48x56
    composites, with parts 4, and the enemies made of several (composites(): parts their list)."""
    sys.path.insert(0, os.path.join(G.ROOT, 'tools', 'content', 'episode6'))
    import waves
    idx = json.load(open(os.path.join(ATLAS, 'atlases.json')))
    cw, ch = idx['cell']
    sheets, out, cells = {}, [], {}
    for c in idx['cells']:
        # (episodes 1-5: the game's data; episode 6's enemies are its own)
        if not c['sheet'].startswith('enemy') or c['episode'] > 5:
            continue
        if c['atlas'] not in sheets:
            sheets[c['atlas']] = np.array(Image.open(os.path.join(ATLAS, c['atlas'])).convert('RGBA'))
        a = sheets[c['atlas']][c['row'] * ch:(c['row'] + 1) * ch, c['column'] * cw:(c['column'] + 1) * cw]
        if c.get('frame') == 0:
            cells[(c['episode'], c['enemy'])] = a[4:32, 4:28]
        out.append((c['episode'], c['enemy'], c['sheet'], c['sprite'], a, 1))
    import levels as lv
    blocks = set()
    for ep in range(1, 6):
        for s in lv.read_strings(os.path.join(G.ROOT, 'data', 'tyrian2000', f'levels{ep}.dat')):
            if s.startswith(']L'):
                try:
                    src = waves.Source(ep, s[13:22].strip())
                except Exception:
                    continue
                blocks |= {(ep, e['d1']) for e in src.events if e['type'] == 12 and e['d1'] > 0}
    for ep, d1 in sorted(blocks):
        parts = [cells.get((ep, d1 + k)) for k in range(4)]
        if any(p is None for p in parts):
            continue
        comp = np.zeros((56, 48, 4), np.uint8)
        for k, (x, y) in enumerate([(0, 28), (24, 28), (0, 0), (24, 0)]):
            comp[y:y + 28, x:x + 24] = parts[k]
        out.append((ep, d1, 'block', d1, comp, 4))
    for ep, parts in composites():
        if any((ep, n) not in cells for n, _, _ in parts):
            continue
        w, h = max(dx for _, dx, _ in parts) + 24, max(dy for _, _, dy in parts) + 28
        comp = Image.new('RGBA', (w, h))
        for n, dx, dy in parts:
            part = Image.fromarray(cells[(ep, n)])
            comp.alpha_composite(part, (dx, dy))
        out.append((ep, parts[0][0], 'comp', parts[0][0], np.array(comp), parts))
    return out


LAYERS = {6: 'ground', 10: 'ground', 17: 'ground at bottom', 15: 'sky', 18: 'sky at bottom', 7: 'top',
          23: 'top at bottom'}


def composites():
    """The PC enemies made of several (the original levels spawn their parts together, each at its
    offset: a long rocket, a face with arms, a robot of four): (episode, parts), parts ((enemy, dx, dy),
    ...) with the offsets from the top left part in PC pixels (y down), in the order they're drawn.
    Groups of the same enemy (a row of fighters) aren't; a chain with a run of the same part (a rocket's
    body) also comes with the run of one and of two."""
    sys.path.insert(0, os.path.join(G.ROOT, 'tools', 'content', 'episode6'))
    import waves
    import levels as lv
    found = {}
    for ep in range(1, 6):
        for s in lv.read_strings(os.path.join(G.ROOT, 'data', 'tyrian2000', f'levels{ep}.dat')):
            if not s.startswith(']L'):
                continue
            try:
                src = waves.Source(ep, s[13:22].strip())
            except Exception:
                continue
            at = {}
            for e in src.events:
                if e['type'] in LAYERS and e['d1'] > 0:
                    at.setdefault((e['t'], LAYERS[e['type']]), []).append((e['d1'], e['d2'], e['d5']))
            for spawns in at.values():
                spawns = list(dict.fromkeys(spawns))
                left = set(range(len(spawns)))
                while left:
                    group, todo = set(), [left.pop()]
                    while todo:
                        i = todo.pop()
                        group.add(i)
                        near = {j for j in left if abs(spawns[j][1] - spawns[i][1]) <= 24 and abs(spawns[j][2] - spawns[i][2]) <= 28}
                        left -= near
                        todo += near
                    parts = [spawns[i] for i in sorted(group)]
                    if not 2 <= len(parts) <= 9 or len({n for n, _, _ in parts}) < 2:
                        continue
                    x0, y0 = min(x for _, x, _ in parts), min(y for _, _, y in parts)
                    parts = tuple((n, x - x0, y - y0) for n, x, y in parts)
                    if max(dx for _, dx, _ in parts) > 6 * 24 or max(dy for _, _, dy in parts) > 4 * 28:
                        continue
                    for v in shortened(parts):
                        found.setdefault((ep, tuple(sorted(v))), v)  # (one drawing order for each)
    return sorted((ep, v) for (ep, _), v in found.items())


def shortened(parts):
    """A composite and, if its parts lie in a line (a step of 24 or 28 apart) with a run of the same
    part, the same with the run of one and of two."""
    out = [parts]
    for axis, step in ((1, 24), (2, 28)):
        other = 3 - axis
        if len({p[other] for p in parts}) != 1:
            continue
        line = sorted(parts, key=lambda p: p[axis])
        runs = []
        for p in line:
            if runs and runs[-1][0][0] == p[0]:
                runs[-1].append(p)
            else:
                runs.append([p])
        if all(len(r) <= 2 for r in runs):
            continue
        for keep in (1, 2):
            seq = [p[0] for r in runs for p in r[:keep]]
            gap = line[1][axis] - line[0][axis] if len(line) > 1 else step
            v = tuple((n, gap * k if axis == 1 else 0, gap * k if axis == 2 else 0) for k, n in enumerate(seq))
            if len(v) >= 2:
                out.append(v)
    return out


def parts_key(parts):
    """A candidate's parts as a key: 1, 4 (event 12's block) or the composite's ((enemy, dx, dy), ...)."""
    return parts if isinstance(parts, int) else tuple(tuple(p) for p in parts)


def part_numbers(n, parts):
    """The enemy numbers a candidate is made of."""
    return [n + k for k in range(parts)] if isinstance(parts, int) else [p[0] for p in parts]


def pool(levels):
    """The enemies (episode, number) the original levels (episode, name) spawn, 4-part ones by their
    first part."""
    sys.path.insert(0, os.path.join(G.ROOT, 'tools', 'content', 'episode6'))
    import waves
    out = set()
    for ep, name in levels:
        src = waves.Source(ep, name)
        out |= {(ep, e['d1']) for e in src.events if e['type'] in waves.SPAWNS and e['d1'] > 0}
    return out


def features(rgba, size=16):
    """Silhouette and shading (16x16), size, and the mean colour (Lab) of the opaque pixels."""
    ys, xs = np.nonzero(rgba[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    crop = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    a = np.array(Image.fromarray(crop).resize((size, size), Image.BOX)).astype(np.float64)
    m = a[:, :, 3] / 255
    lum = a[:, :, :3].mean(2) * m
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from episode import lab
    colour = lab(crop[crop[:, :, 3] > 0][:, :3].astype(np.float64)).mean(0)
    return m.ravel(), lum.ravel(), np.array(crop.shape[:2], np.float64), colour


def unit(x):
    x = x - x.mean(-1, keepdims=True)
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-6)


class Matcher:
    def __init__(self):
        self.cells = [c for c in atlas() if features(c[4]) is not None]
        f = [features(c[4]) for c in self.cells]
        self.m = unit(np.stack([x[0] for x in f]))
        self.l = unit(np.stack([x[1] for x in f]))
        self.size = np.stack([x[2] for x in f])
        self.colour = np.stack([x[3] for x in f])
        self.ep = np.array([c[0] for c in self.cells])
        self.keys = [(c[0], c[1]) for c in self.cells]

    def best(self, imgs, episode, n=3, prefer=()):
        """The best PC enemies for a GBC enemy seen in imgs (its frames): each enemy's best frame
        against the best image."""
        if not isinstance(imgs, list):
            imgs = [imgs]
        scores = np.max([self.score(im, episode, prefer) for im in imgs], axis=0)
        order = np.argsort(-scores)
        out, seen = [], set()
        for i in order:
            c = self.cells[i]
            key = (c[0], c[1], c[5])  # one per enemy (its frames are rows of their own)
            if key in seen:
                continue
            seen.add(key)
            out.append(dict(episode=int(c[0]), enemy=int(c[1]), sheet=c[2], sprite=int(c[3]),
                            parts=c[5] if isinstance(c[5], int) else [list(p) for p in c[5]],
                            score=float(scores[i])))
            if len(out) == n:
                break
        return out

    def score(self, img, episode, prefer=()):
        m, l, size, colour = features(img)
        sim = self.m @ unit(m) * 0.6 + self.l @ unit(l) * 0.4
        pen = np.abs(np.log((self.size + 1) / (size * 1.5 + 1))).sum(1)
        # the GBC palettes are near the PC's: hue and chroma (a, b) count, lightness a little
        dc = np.sqrt(((self.colour[:, 1:] - colour[1:]) ** 2).sum(1)) + 0.3 * np.abs(self.colour[:, 0] - colour[0])
        inpool = np.array([k in prefer for k in self.keys])
        return sim - 0.3 * pen - 0.015 * dc + 0.05 * (self.ep == episode) + 0.25 * inpool


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', default=','.join(str(i) for i in range(1, 25)))
    ap.add_argument('--frames', type=int, default=30000)
    ap.add_argument('--match', action='store_true', help='match the types again from the last flight')
    ap.add_argument('--tables', action='store_true', help="only the type and gun tables' places, no flight")
    a = ap.parse_args()
    if a.tables:
        for level in [int(x) for x in a.levels.split(',')]:
            path = os.path.join(OUT, f'L{level:02d}.json')
            d = json.load(open(path))
            d['types_at'], d['guns_at'] = tables(X.start_level(level)[0])
            json.dump(d, open(path, 'w'))
            print(f"L{level:02d}: types at {d['types_at']:04x}, guns at {d['guns_at']:04x}")
        return
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import episode as E
    spec_of = {s['gbc']: s for s in E.LEVELS}
    matcher = Matcher()
    os.makedirs(OUT, exist_ok=True)
    for level in [int(x) for x in a.levels.split(',')]:
        if a.match:
            old = json.load(open(os.path.join(OUT, f'L{level:02d}.json')))
            run = dict(old, types={})
            for t, info in old['types'].items():
                p = os.path.join(OUT, f'L{level:02d}_type{int(t):02x}.png')
                imgs = [np.array(Image.open(q).convert('RGBA')) for q in [p] + [p[:-4] + f'_{k}.png' for k in range(1, 6)]
                        if os.path.exists(q)]
                run['types'][int(t)] = dict(images=imgs, groups=set(info['groups']))
        else:
            run = fly(level, a.frames)
        ep = spec_of[level]['pc'][0]
        prefer = pool([tuple(m) for m in spec_of[level].get('pool', spec_of[level].get('maps', [spec_of[level]['pc']]))])
        types = {}
        sheet = []
        for t, d in sorted(run['types'].items()):
            if not d['images']:
                types[str(t)] = dict(pc=None, groups=sorted(d['groups']))
                continue
            # the type's look: its most frequent image (by size and pixels)
            keys = {}
            for im in d['images']:
                keys.setdefault(im.tobytes() + bytes(im.shape[:2]), [im, 0])[1] += 1
            img = max(keys.values(), key=lambda v: v[1])[0]
            frames = [v[0] for v in sorted(keys.values(), key=lambda v: -v[1])[:6]]
            # (the matched ones: its frames of about the main one's size and shape; a neighbour can be caught)
            m0 = unit(features(frames[0])[0])
            near = frames[:1] + [f for f in frames[1:] if all(0.75 <= f.shape[k] / frames[0].shape[k] <= 1.34 for k in (0, 1))
                                 and unit(features(f)[0]) @ m0 > 0.6]
            cands = matcher.best(near, ep, n=30, prefer=prefer)
            types[str(t)] = dict(pc=cands[0], candidates=cands, size=list(img.shape[:2]), groups=sorted(d['groups']))
            sheet.append((t, img, cands))
            Image.fromarray(img).save(os.path.join(OUT, f'L{level:02d}_type{t:02x}.png'))
            for k, fr in enumerate(frames[1:], 1):
                Image.fromarray(fr).save(os.path.join(OUT, f'L{level:02d}_type{t:02x}_{k}.png'))
        json.dump(dict(level=level, bank=run['bank'], events_pos=run['events_pos'], events=run['events'],
                       executed=run['executed'], types=types, types_at=run.get('types_at', old.get('types_at') if a.match else None),
                       guns_at=run.get('guns_at', old.get('guns_at') if a.match else None)), open(os.path.join(OUT, f'L{level:02d}.json'), 'w'))
        review(level, sheet, matcher)
        print(f'L{level:02d}: {len(run["executed"])} records run, {len(types)} enemy types')


def review(level, sheet, matcher):
    """GBC type | its three PC candidates, for checking by eye."""
    cell = {}
    for c in matcher.cells:
        cell.setdefault((c[2], c[3], c[5]), c[4])
    rows = []
    for t, img, cands in sheet:
        row = Image.new('RGB', (64 + 3 * 80, 80), (24, 24, 24))
        g = Image.fromarray(img).resize((img.shape[1] * 3, img.shape[0] * 3), Image.NEAREST)
        row.paste(g, (0, 0), g)
        d = ImageDraw.Draw(row)
        d.text((0, 68), f'{t:02x}', fill=(255, 255, 255))
        for k, c in enumerate(cands):
            pc = Image.fromarray(cell[(c['sheet'], c['sprite'], parts_key(c['parts']))])
            pc = pc.resize((64, min(72, int(64 * pc.height / pc.width))), Image.NEAREST)
            row.paste(pc, (64 + k * 80, 0), pc)
            d.text((64 + k * 80, 70), f"{c['episode']}:{c['enemy']} {c['score']:.2f}", fill=(255, 255, 0))
        rows.append(row)
    if rows:
        out = Image.new('RGB', (rows[0].width, 82 * len(rows)))
        for i, r in enumerate(rows):
            out.paste(r, (0, 82 * i))
        out.save(os.path.join(OUT, f'L{level:02d}_matches.png'))


if __name__ == '__main__':
    main()
