"""The GBC levels' bosses as the ROM has them (episode 7): the script's last stretch, its loop, its enemies' and guns' data.

A GBC boss is no code of its own: it is enemies of the level's type table, spawned by the level's script and steered by
it as the other enemies are, the script's last stretch run as a loop (the GBC script interpreter, bank 0 $2741-$2828;
the per-enemy update $1160-$12e3):

    02 a b c .      scroll: the clock (the script's position) a step every b+1 frames; c != 0: the map stands, the
                    clock runs on (from the boss on)
    06 lo hi . .    the clock back to position hi:lo (the records from there run again): the boss's loop
    05 e . . g      once no enemy of group g is left (255: none at all) every enemy is taken off and (e = 1) the
                    level ends ($2b79, $0a9d)
    0e gun n f g    group g's gun (ff: those whose gun is f) fires every n frames (0: not at all)
    13 vx vy . g    group g's speed (half pixels a frame; 99: steered towards the ship, a step every 10 frames)
    14/16 cx cy r g its speed a step every |c| frames (14: turning at r)
    28+             a block of pieces of one enemy (columns, rows from the command's bits, 16 px apart, rows upwards)

The level's tables (their pointers set by its init): enemy types at $c453, 10 bytes each: [0] 0 for an 8-px wide
sprite, [1] hit points (Normal; Easy half, Hard 1.5x), [3]/[4] start speed (99: towards the ship), [5] gun, [6] how
often it fires (frames), [8] sprite tile. Guns at $c451, 7 bytes from gun 1 ($054d): [0] sprite, [1] damage (+ the
difficulty - 1), [2] 99: the next gun fires with it, [3]/[4] speed in pixels a frame (99: aimed at the ship), [5]/[6]
where from (the enemy's top left + (6, 0)). Guns 20 and up launch an enemy of type gun - 20 ($054d hands $2ca8 gun - 21, which takes the type after). At most 9 enemy
shots fly at once.

Each level with a loop is flown (Normal, the ship kept alive in a corner where nothing rams it, never firing) from a
while before its boss: where each boss group is, frame by frame, and the shots fired (where from, how fast), as a
reference for the PC version (tools/gbc/episode.py boss).

    python tools/gbc/boss_rom.py [--levels 23,3,...] [--frames 3000]
Writes data/gbc/bosses/rom.json.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G  # noqa: E402
import extract as X  # noqa: E402
import enemies as EN  # noqa: E402
import episode as E  # noqa: E402
from PIL import Image  # noqa: E402

OUT = os.path.join(G.ROOT, 'data', 'gbc', 'bosses', 'rom.json')
SPAWNS = {3, 4, 0x21, 0x22, 0x23, 0x24}
SHOTS, SHOT_SIZE, SHOT_MAX = 0xc37f, 7, 9
LAUNCH = 20                # guns from this one launch an enemy (type gun - 20)
NORMAL = 1                 # $d92a: the difficulty


def s8(v):
    return v - 256 if v > 127 else v


def script(rom, bank, events, events_pos):
    """The level's records and their positions, up to its loop (06) or end (01) past the map's start."""
    ro = lambda a: X.rom_off(bank, a)
    recs, pos = [], []
    for i in range(1500):
        r = list(rom[ro(events + 5 * i):ro(events + 5 * i) + 5])
        p = rom[ro(events_pos + 2 * i)] | rom[ro(events_pos + 2 * i + 1)] << 8
        if i and p < pos[-1]:
            break
        recs.append(r)
        pos.append(p)
        if r[0] in (1, 6) and p > 1000:
            break
    return recs, pos


def is_spawn(r):
    return r[0] in SPAWNS or r[0] >= 0x28


def block_of(cmd):
    """A spawn's columns and rows (a block for commands 28 and up)."""
    if cmd < 0x28:
        return 1, 1
    k = cmd - 0x28
    return ((k >> 1) & 3) + 1, (k >> 3) + 1


def boss_of(recs, pos):
    """The boss's stretch of the script: dict(start, stop, loop [start, end], target, end record, pieces, groups) or None.
    The loop is the records from the 06's position to it; the map stands from the last 02 that stops it (none after
    that starts it again); the boss is the groups spawned with the one the last 05 waits for (their last spawns, within
    60 positions of each other: TYRIAN's claws, DESERT's turrets), or (it waits for none at all) what is spawned last
    before its loop; the stretch starts with its first spawn (or the map's stop, the 05, the loop)."""
    j = len(recs) - 1
    if recs[j][0] != 6:
        return None
    target = recs[j][1] | recs[j][2] << 8
    k = next((i for i in range(j) if pos[i] >= target), j)
    ends = [i for i in range(j) if recs[i][0] == 5 and recs[i][1] == 1]
    end = ends[-1] if ends else None
    stop = None
    for i in range(j):
        if recs[i][0] == 2:
            stop = (i if stop is None else stop) if recs[i][3] else None
    g_end = recs[end][4] if end is not None else None
    spawns = [i for i in range(j) if is_spawn(recs[i])]
    if g_end not in (None, 0, 255):
        mine = [i for i in spawns if recs[i][4] == g_end]
    else:
        mine = [i for i in spawns if i < k][-1:]
    pieces, groups = [], set()
    if mine:
        keep = [mine[-1]]
        for i in reversed(mine[:-1]):
            if pos[keep[0]] - pos[i] > 60:
                break
            keep.insert(0, i)
        # with it: the groups spawned at its spawns' places (TYRIAN's claws, DESERT's turrets) and right after them
        # (spawn after spawn: JUNGLE II's body after its head)
        times = {pos[i] for i in keep}
        groups = {recs[i][4] for i in spawns if any(abs(pos[i] - t) <= 1 for t in times)} | {recs[i][4] for i in keep}
        i = keep[-1] + 1
        while i < j and is_spawn(recs[i]) and pos[i] - pos[keep[-1]] <= 32:
            groups.add(recs[i][4])
            i += 1
        groups.discard(0)
        lo, hi = pos[keep[0]] - 4, pos[i - 1] + 4
        pieces = [x for x in spawns if lo <= pos[x] <= hi and recs[x][4] in groups]
    start = min([x for x in [stop, end, k] if x is not None] + pieces)
    return dict(start=start, stop=stop, loop=[k, j], target=target, end=end, pieces=pieces, groups=sorted(groups))


def tables(g):
    w = lambda a: g.read(a) | g.read(a + 1) << 8
    return w(0xc453), w(0xc451)


def type_entry(rom, bank, t0, t):
    raw = [rom[X.rom_off(bank, t0 + 10 * t + k)] for k in range(10)]
    return dict(raw=raw, narrow=raw[0] == 0, hp=raw[1], vx=raw[3], vy=raw[4], gun=raw[5], every=raw[6], tile=raw[8])


def gun_entry(rom, bank, s0, n):
    raw = [rom[X.rom_off(bank, s0 + 7 * (n - 1) + k)] for k in range(7)]
    aimed = raw[3] == 0x63
    return dict(raw=raw, sprite=raw[0], damage=raw[1], chain=raw[2] == 0x63, aimed=aimed,
                vx=None if aimed else s8(raw[3]), vy=None if aimed else s8(raw[4]), dx=s8(raw[5]), dy=s8(raw[6]))


def guns_of(rom, bank, s0, first):
    """A gun and the ones that fire with it (chained)."""
    out, n = [], first
    while 0 < n < LAUNCH and len(out) < 8:
        e = gun_entry(rom, bank, s0, n)
        out.append(dict(e, n=n))
        if not e['chain']:
            break
        n += 1
    return out


def fly(level, boss, recs, pos, frames, launched=None):
    """From a while before the boss: the boss groups' places (each group's sprites' box, every 4 frames), the shots
    fired (frame, place, speed), the frames the clock goes back (the loop), the frame the level ends, and the looks
    of the enemies its pieces launch (launched: {sprite tile: type}; {type: [RGBA images]})."""
    launched = launched or {}
    looks, pending = {}, []
    # (each group's way, frame by frame by its first piece while none of it comes or goes: from its spawn to the
    # first time the clock goes back, then each loop; the GBC's half pixels in it, which odd speeds move on
    # alternate frames)
    ways, way_now, last_pos = {}, {}, {}
    g, bank, init, c = X.start_level(level)
    g.write(0xd92a, NORMAL)
    at = min([pos[i] for i in boss['pieces']] or [pos[boss['start']]])  # (from its pieces' spawns: JUNGLE II's loop is the whole level)
    track, shots, loops, ended = [], [], [], None
    seen = set()
    prev_clock = None
    started = None
    for f in range(40000):
        g.write(0xd8da, 8)
        g.write(0xd8dd, 4)
        g.write(0xd8de, 128)   # (the ship in the bottom left corner: nothing of the boss rams it)
        g.run(1, 0)
        clock = g.read(0xc439) << 8 | g.read(0xc43a)
        if started is None:
            if clock >= at - 20:
                started = f
            prev_clock = clock
            continue
        n = f - started
        if n >= frames or g.read(0xc42d):
            ended = n if g.read(0xc42d) else None
            break
        if prev_clock is not None and clock < prev_clock:
            loops.append(n)
            for grp, w in way_now.items():
                ways.setdefault(grp, []).append(list(w))
            way_now = {grp: [0, 0] for grp in way_now}
        prev_clock = clock
        sts = EN.enemy_structs(g)
        for grp in boss['groups']:
            mine = [(s[0], s[1]) for s in sts if s[13] == grp]
            if mine and len(mine) == len(last_pos.get(grp, [])):
                w = way_now.setdefault(grp, [0, 0])
                w[0] += (mine[0][0] - last_pos[grp][0][0] + 128) % 256 - 128
                w[1] += (mine[0][1] - last_pos[grp][0][1] + 128) % 256 - 128
            elif mine:
                way_now.setdefault(grp, [0, 0])
            last_pos[grp] = mine
        # (a launched enemy: its type's sprite tile; drawn a few frames later, where it is then)
        for s in sts:
            if s[27] in launched and len(looks.get(launched[s[27]], [])) < 6 and not any(
                    abs(p[1] - s[0]) < 12 and abs(p[2] - s[1]) < 12 for p in pending):
                pending.append([launched[s[27]], s[0], s[1], 6])
        for p in pending:
            p[3] -= 1
            if p[3] == 0:
                near = [s for s in sts if s[27] in launched and launched[s[27]] == p[0]]
                if near:
                    s = min(near, key=lambda s: abs(s[0] - p[1]) + abs(s[1] - p[2]))
                    img = EN.cluster_at(g, s[0], s[1])
                    if img is not None and img.shape[0] * img.shape[1] <= 32 * 32:
                        looks.setdefault(p[0], []).append(img)
        pending[:] = [p for p in pending if p[3] > 0]
        if n % 4 == 0:
            by = {}
            for s in sts:
                if s[13] in boss['groups']:
                    by.setdefault(s[13], []).append((s[0], s[1], s[14]))
            track.append([n, clock, {str(k): [min(x for x, _, _ in v), min(y for _, y, _ in v), max(x for x, _, _ in v),
                                              max(y for _, y, _ in v), sum(h for _, _, h in v), len(v)]
                                     for k, v in by.items()}])
        k = g.read(0xc47b)
        for i in range(0 if k == 0xff else k + 1):
            s = [g.read(SHOTS + SHOT_SIZE * i + j) for j in range(SHOT_SIZE)]
            key = (s[5], s[2], s[3])
            # (a new shot: its slot's first frame; slots are reused, so by slot and its first place)
            if (s[5], s[0] - s8(s[2]), s[1] - s8(s[3])) not in seen:
                shots.append([n, s[0], s[1], s8(s[2]), s8(s[3]), s[4]])
            seen.add((s[5], s[0], s[1]))
        if len(seen) > 4000:
            seen.clear()
    return dict(track=track, shots=shots, loops=loops, ended=ended, ways={str(k): v for k, v in ways.items()}), looks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', default=','.join(str(i) for i in range(1, 25)))
    ap.add_argument('--frames', type=int, default=3000)
    ap.add_argument('--no-fly', action='store_true')
    a = ap.parse_args()
    rom = open(G.ROM, 'rb').read()
    found = json.load(open(OUT)) if os.path.exists(OUT) else {}
    matcher = None
    for level in [int(x) for x in a.levels.split(',')]:
        g, bank, init, c = X.start_level(level)
        t0, s0 = tables(g)
        recs, pos = script(rom, bank, c['events'], c['events_pos'])
        boss = boss_of(recs, pos)
        if boss is None:
            found[str(level)] = None
            print(f'L{level:02d}: no boss loop (ends with {recs[-1]})')
            continue
        lo = boss['start']
        types, guns = {}, {}
        for i in range(lo, len(recs)):
            r = recs[i]
            if is_spawn(r):
                cols, rows = block_of(r[0])
                for t in range(r[1], r[1] + cols * rows):  # (a block's pieces: its types one after another)
                    types[t] = type_entry(rom, bank, t0, t)
        for t, e in list(types.items()):
            if 0 < e['gun'] < LAUNCH:
                guns[e['gun']] = guns_of(rom, bank, s0, e['gun'])
            elif e['gun'] >= LAUNCH:
                types.setdefault(e['gun'] - 20, type_entry(rom, bank, t0, e['gun'] - 20))
        for i in range(lo, len(recs)):
            r = recs[i]
            if r[0] == 0x0e:
                n = r[1] if r[1] != 0xff else r[3]
                if 0 < n < LAUNCH:
                    guns[n] = guns_of(rom, bank, s0, n)
                elif n >= LAUNCH:
                    types.setdefault(n - 20, type_entry(rom, bank, t0, n - 20))
        launches = sorted({e['gun'] - 20 for e in types.values() if e['gun'] >= LAUNCH} |
                          {(r[1] if r[1] != 0xff else r[3]) - 20 for r in recs[lo:] if r[0] == 0x0e and
                           (r[1] if r[1] != 0xff else r[3]) >= LAUNCH})
        for t in launches:
            types.setdefault(t, type_entry(rom, bank, t0, t))
        # (frames a position as the stretch starts: the last 02 before it, b + 1)
        delay0 = next(((r[2] + 1) for r in reversed(recs[:lo]) if r[0] == 2 and r[2] != 0xff), 4)
        out = dict(boss, bank=bank, types_at=t0, guns_at=s0, records=recs[lo:], positions=pos[lo:], first=lo, delay0=delay0,
                   types={f'{t:02x}': e for t, e in sorted(types.items())}, guns={str(n): v for n, v in sorted(guns.items())},
                   launches=launches)
        old = found.get(str(level)) or {}
        if not a.no_fly:
            out['flight'], looks = fly(level, boss, recs, pos, a.frames, {types[t]['tile']: t for t in launches})
            for t in launches:  # (types drawn with the same sprite tile: the same looks)
                same = [u for u in launches if types[u]['tile'] == types[t]['tile'] and u in looks]
                if t not in looks and same:
                    looks[t] = looks[same[0]]
            # the launched enemies' PC ones: as enemies.py finds the script's (their looks against the PC enemies')
            out['launched'] = {}
            for t, imgs in looks.items():
                for k, im in enumerate(imgs[:3]):
                    Image.fromarray(im).save(os.path.join(os.path.dirname(OUT), f'L{level:02d}_launch{t:02x}_{k}.png'))
                if matcher is None:
                    matcher = EN.Matcher()
                cands = matcher.best(imgs, E.spec_of(level)['pc'][0], n=30,
                                     prefer=EN.pool([tuple(m) for m in E.spec_of(level).get('pool', [E.spec_of(level)['pc']])]))
                out['launched'][f'{t:02x}'] = dict(pc=cands[0], candidates=cands, size=list(imgs[0].shape[:2]))
        else:
            for k in ('flight', 'launched'):
                if old.get(k):
                    out[k] = old[k]
        found[str(level)] = out
        fl = out.get('flight', {})
        print(f"L{level:02d}: boss from record {lo} (position {pos[lo]}), stop {boss['stop']}, loop {boss['loop']} "
              f"({pos[boss['loop'][1]] - pos[boss['loop'][0]] if boss['loop'][0] < boss['loop'][1] else 0} steps), "
              f"end {recs[boss['end']] if boss['end'] is not None else None}, groups {boss['groups']}, "
              f"types {sorted(types)}, guns {sorted(guns)}"
              + (f"; flown: loops at {fl['loops'][:3]}, {len(fl['shots'])} shots, ended {fl['ended']}" if fl else ''), flush=True)
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(found, open(OUT, 'w'))


if __name__ == '__main__':
    main()
