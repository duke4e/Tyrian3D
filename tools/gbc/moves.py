"""The GBC levels' enemies' paths against episode 7's (a check of script.py's translation of how they move).

The GBC level is flown (Normal, the ship kept in the bottom left corner, never firing, as boss_rom.py flies it) and
each enemy followed from its spawn (its group, and where it should be from its speed); the PC level's are read from
a log of the game (TYR3D_LOG_MOVES: every enemy each tick). Each GBC spawn's enemy gets the PC enemy its event
made (the level's spawn at the same clock, 1.5 a position, nearest its place: by its link), and both their speeds
over their first ticks (PC px a tick; the GBC's a pixel a frame is 4) are set side by side, with the share of spawns
whose speeds agree.

    TYR3D_LOG_MOVES=1 TYR3D_START=7:<section> TYR3D_AUTOPILOT=park TYR3D_GODMODE=1 ... ./tyrian3d > moves.log
    python tools/gbc/moves.py <GBC level> moves.log [--from P] [--to P] [--ticks 15]
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G  # noqa: E402
import extract as X  # noqa: E402
import enemies as EN  # noqa: E402
import script as S  # noqa: E402

MOVE = re.compile(r'move: clock (\d+) slot (\d+) enemy (\d+) at (-?\d+),(-?\d+) moving .* link (\d+)')
LEVELS = os.path.join(G.ROOT, 'data', 'gbc', 'episode7', 'levels')
SPAWNS = {6, 12, 15}


def wrap(v):
    return (v + 128) % 256 - 128


def gbc_paths(level, p_from, p_to):
    """Each enemy spawned from position p_from to p_to: (position at its spawn, its record, [(x, y) each frame])."""
    rom = open(G.ROM, 'rb').read()
    g, bank, init, c = X.start_level(level)
    g.write(0xd92a, 1)
    ptr = g.read(0xc457) | (g.read(0xc458) << 8)
    live, done, pending = [], [], []

    for f in range(60000):
        g.write(0xd8da, 8)
        g.write(0xd8dd, 4)
        g.write(0xd8de, 128)
        g.run(1, 0)
        pos = g.read(0xc439) << 8 | g.read(0xc43a)
        new = g.read(0xc457) | (g.read(0xc458) << 8)
        recs = []
        p = ptr
        while p != new and len(recs) < 64:
            recs.append(list(rom[X.rom_off(bank, p):X.rom_off(bank, p) + 5]))
            p += 5
        ptr = new
        sts = EN.enemy_structs(g)
        taken = set()
        for e in live:
            # (where it should be: its last step again)
            px, py = e['path'][-1]
            dx, dy = (wrap(px - e['path'][-2][0]), wrap(py - e['path'][-2][1])) if len(e['path']) > 1 else (0, 0)
            near = [(abs(wrap(s[0] - px - dx)) + abs(wrap(s[1] - py - dy)), k) for k, s in enumerate(sts)
                    if k not in taken and s[13] == e['group']]
            near = [n for n in near if n[0] <= 6]
            if near:
                k = min(near)[1]
                taken.add(k)
                e['path'].append((sts[k][0], sts[k][1]))
            else:
                e['gone'] = True
        done += [e for e in live if e.get('gone')]
        live = [e for e in live if not e.get('gone')]
        # (the new ones: each the spawn record's of its group nearest its place, made this frame or a few before (a
        # block's pieces come after); others, launched or there from the start, followed too but no spawn's)
        if p_from <= pos <= p_to:
            pending += [dict(rec=r, pos=pos, frame=f) for r in recs if r[0] in (3, 4, 0x21, 0x22, 0x23, 0x24) or r[0] >= 0x28]
        pending = [q for q in pending if f - q['frame'] <= 8]
        for k in range(len(sts)):
            if k in taken:
                continue
            near = [(abs(wrap(sts[k][0] - q['rec'][2])), n) for n, q in enumerate(pending) if q['rec'][4] == sts[k][13]]
            near = [n for n in near if n[0] <= 20]
            q = pending.pop(min(near)[1]) if near else None
            live.append(dict(pos=q['pos'] if q else pos, rec=q['rec'] if q else None, group=sts[k][13],
                             path=[(sts[k][0], sts[k][1])]))
        if pos > p_to + 200 or g.read(0xc42d):
            break
    return [e for e in done + live if e['rec']]


def pc_paths(log):
    """Each PC enemy: (clock at its spawn, slot, enemy, [(x, y) each tick])."""
    out, cur = [], {}
    last_clock = None
    seen = set()
    for line in open(log, errors='replace'):
        m = MOVE.match(line)
        if not m:
            continue
        clock, slot, en, x, y, link = (int(v) for v in m.groups())
        if clock != last_clock:
            # (a tick: slots not seen in the last one are free again)
            for s in list(cur):
                if s not in seen:
                    out.append(cur.pop(s))
            seen = set()
            last_clock = clock
        seen.add(slot)
        e = cur.get(slot)
        if e is None or e['enemy'] != en or abs(x - e['path'][-1][0]) > 40 or abs(y - e['path'][-1][1]) > 40:
            if e is not None:
                out.append(e)
            e = cur[slot] = dict(clock=clock, slot=slot, enemy=en, link=link, path=[], clocks=[])
        e['path'].append((x, y))
        e['clocks'].append(clock)
    return out + list(cur.values())


def speed(path, n, per, at=1):
    """The mean speed over n steps from its place at (the second: the first is where it was made)."""
    if len(path) < at + n + 1:
        return None
    return ((path[at + n][0] - path[at][0]) / n * per, (path[at + n][1] - path[at][1]) / n * per)


def unwrapped(path):
    """A GBC path's places (bytes, round at 256) as steps added up."""
    out = [path[0]]
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        out.append((out[-1][0] + wrap(x1 - x0), out[-1][1] + wrap(y1 - y0)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('level', type=int)
    ap.add_argument('log')
    ap.add_argument('--from', dest='p_from', type=int, default=0)
    ap.add_argument('--to', dest='p_to', type=int, default=1500)
    ap.add_argument('--ticks', type=int, default=15)
    a = ap.parse_args()
    frames = round(a.ticks / S.FRAME)
    gbc = gbc_paths(a.level, a.p_from, a.p_to)
    pcs = pc_paths(a.log)
    level = json.load(open(os.path.join(LEVELS, next(n for n in os.listdir(LEVELS) if n.endswith(f'_L{a.level:02d}.json')))))
    events = [q for q in level['events'] if q['type'] in SPAWNS and q.get('ep') not in (None, 'boss')]
    rows, agree = [], 0
    for e in sorted(gbc, key=lambda e: e['pos']):
        v = speed(unwrapped(e['path']), frames, 1)
        if v is None:
            continue
        # (GBC pixels a frame: 1.5 PC px in 0.375 ticks)
        v = (v[0] * S.SCALE / S.FRAME, v[1] * S.SCALE / S.FRAME)
        # (its PC spawn: the level's event at its clock nearest its place; a composite's part)
        t0, x0 = S.SCALE * e['pos'], S.SCALE * e['rec'][2] - 12
        evs = [q for q in events if abs(q['t'] - t0) <= 3 and abs(q['d2'] - (27 if q['type'] == 6 else 0) - x0) <= 60]
        if not evs:
            rows.append((e, v, None, None))
            continue
        q = min(evs, key=lambda q: abs(q['d2'] - (27 if q['type'] == 6 else 0) - x0))
        t, x = q['t'], q['d2'] - (12 if q['type'] == 6 or (q['type'] == 12 and q['d6'] != 2) else 0)
        # (the PC enemies of its link there at that clock, made then or, on a playfield reaching above the screen, a
        # while before: tyrian2.c prespawn_events; from that clock on)
        cands = []
        for p in pcs:
            if p['link'] != q['d4']:
                continue
            if t - 130 <= p['clock'] <= t and t in p['clocks']:
                k = p['clocks'].index(t)
                if len(p['path']) > k + a.ticks + 1:
                    cands.append((abs(p['path'][k][0] - x), k, p))
            elif t < p['clock'] <= t + 3 and len(p['path']) > a.ticks + 1:
                cands.append((abs(p['path'][0][0] - x), 0, p))
        if not cands:
            rows.append((e, v, None, None))
            continue
        _, k, p = min(cands, key=lambda c: c[0])
        w = speed(p['path'], a.ticks, 1, k + 1)
        ok = abs(w[0] - v[0]) <= 1.0 and abs(w[1] - v[1]) <= 1.0
        agree += ok
        rows.append((e, v, p, w, ok))
    for row in rows:
        e, v = row[0], row[1]
        r = e['rec']
        head = f"p{e['pos']:5d} rec {r[0]:02x} type {r[1]:02x} g{r[4]:3d}  GBC {v[0]:5.1f},{v[1]:5.1f}"
        if row[2] is None:
            print(head + '  PC: none made then')
        else:
            p, w, ok = row[2], row[3], row[4]
            print(head + f"  PC {w[0]:5.1f},{w[1]:5.1f} (enemy {p['enemy']}, clock {p['clock']}){'' if ok else '  <-- differs'}")
    matched = sum(1 for r in rows if r[2] is not None)
    print(f"{matched} of {len(rows)} GBC spawns matched; {agree} of them move alike (within 1 px a tick over {a.ticks} ticks)")


if __name__ == '__main__':
    main()
