"""Episode 7's background 3 pieces taken from an original (remake.py upper_stamps) with the guns the original sets on
them: at each socket tile of the level's background 3, the enemies the original puts there (top layer, event 7), made
when that row comes to the screen's top as the original makes them.

DELIANI's purple tubes are PC DELIANI's, whose tube ends hold a gun of four pieces in each of their socket rows (228-231
at a left tube's socket, tile 583; 232-235 at a right tube's, 584); the stamps brought the sockets and no guns, the
user's playtest (2026-11-12): "na ljubičastim letećim otocima nedostaju turreti". PC DELIANI makes a socket row's gun at
the tick its layer 3 has scrolled so far that the row lies one row and the layer's step (pixels a tick) below the
screen's top edge (28 + step pixels: the enemy is made 28 above the top and moved one step); the pieces' x the
socket's column times 24 and the offsets below.

    python tools/gbc/sockets.py [--dry]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upper  # noqa: E402

LEVELS = os.path.join(HERE, '..', '..', 'data', 'gbc', 'episode7', 'levels')
TOP = 7  # (event 7: an enemy of the top layer, background 3)

# level: {socket tile: (episode, [(enemy, x less 24 times the socket's column), ...])}
SOCKETS = {
    'DELIANI': {583: (1, [(228, -24), (229, 0), (230, 24), (231, 52)]),
                584: (1, [(232, -32), (233, -24), (234, 0), (235, 24)])},
}


def guns(level, table):
    """The events of the guns for the level's sockets, and how many sockets."""
    grid = level['maps'][2]
    rows = len(grid)
    px = upper.timeline(level)
    scroll = sorted((e for e in level['events'] if e['type'] == 2 and e['t'] < 60000), key=lambda e: e['t'])
    out, n = [], 0
    for r, row in enumerate(grid):
        for c, tile in enumerate(row):
            if tile not in table:
                continue
            ep, pieces = table[tile]
            # (the layer's step where the row comes in: the one by its own reach, then again with that tick's)
            step = 1
            for _ in range(2):
                target = (rows - 2 - r - step / 28) * 28 - 200
                if not (px[2] >= target).any():
                    break
                t = int(np.argmax(px[2] >= target))
                step = max([e['d3'] for e in scroll if e['t'] <= t] + [1])
            else:
                n += 1
                out += [dict(t=t, type=TOP, d1=enemy, d2=24 * c + dx, d3=0, d5=0, d6=0, d4=0, ep=ep) for enemy, dx in pieces]
    return out, n


def insert(events, new):
    """The events with the new ones at their ticks (after that tick's others); the difficulty skips (event 66) counting
    the events they did."""
    out, where = [], []
    new = sorted(new, key=lambda e: e['t'])
    k = 0
    for i, e in enumerate(events):
        while k < len(new) and new[k]['t'] < e['t']:
            out.append(new[k])
            k += 1
        where.append(len(out))
        out.append(e)
    out += new[k:]
    where.append(len(out) - (len(new) - k))
    for i, e in enumerate(events):
        if e['type'] == 66:
            j = where[i]
            out[j] = dict(out[j], d2=where[min(len(events), i + 1 + e['d2'])] - where[i + 1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    for path in sorted(glob.glob(os.path.join(LEVELS, '*.json'))):
        level = json.load(open(path, encoding='utf-8'))
        if level['name'] not in SOCKETS:
            continue
        table = SOCKETS[level['name']]
        have = [e for e in level['events'] if e['type'] == TOP and (e.get('ep'), e['d1']) in
                {(ep, m) for ep, ps in table.values() for m, _ in ps}]
        if have:
            print(f"{level['name']}: has its guns already")
            continue
        new, n = guns(level, table)
        print(f"{level['name']}: {n} socket rows, {len(new)} enemies at ticks {sorted({e['t'] for e in new})}")
        if new and not a.dry:
            level['events'] = insert(level['events'], new)
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(level, f)


if __name__ == '__main__':
    main()
