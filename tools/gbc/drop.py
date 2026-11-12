"""Spawns taken out of an episode 7 level: every spawn of the PC enemies named, the difficulty skips (event 66) counting
the events left.

SAVARA II's dark red front piece (GBC type 0x12, mapped to the beak of SAVARA's red jet, episode 1's 308) lies over the
grey jet it comes with (type 0x05, the red jet 742-744 that has its own nose): the user's playtest (2026-11-12), "neki
avioni imaju krivi nos". Its overrides are null (tools/gbc/enemy_overrides.json) so that retype.py leaves it out too.

    python tools/gbc/drop.py <level number> <episode>:<enemy>[,...] [--dry]
"""
import argparse
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = os.path.join(HERE, '..', '..', 'data', 'gbc', 'episode7', 'levels')
SPAWNS = {6, 7, 10, 12, 15, 17, 18, 23, 32, 56}


def drop(events, enemies):
    """The events without those spawns (an event 201 naming one counts one fewer)."""
    gone = {i for i, e in enumerate(events) if e['type'] in SPAWNS and (e.get('ep'), e['d1']) in enemies}
    out, where = [], []
    for i, e in enumerate(events):
        where.append(len(out))
        if i in gone:
            continue
        if e['type'] == 201:
            e = dict(e, d1=e['d1'] - len(gone & set(range(i + 1, i + 1 + e['d1']))))
            if e['d1'] <= 0:
                continue
        out.append(e)
    where.append(len(out))
    for i, e in enumerate(events):
        if e['type'] == 66 and i not in gone:
            j = where[i]
            out[j] = dict(out[j], d2=where[min(len(events), i + 1 + e['d2'])] - where[i + 1])
    return out, len(gone)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('level', type=int)
    ap.add_argument('enemies')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    enemies = {tuple(int(x) for x in s.split(':')) for s in a.enemies.split(',')}
    path = glob.glob(os.path.join(LEVELS, f'{a.level:02d}_*.json'))[0]
    level = json.load(open(path, encoding='utf-8'))
    events, n = drop(level['events'], enemies)
    print(f"{level['name']}: {n} spawns out, events {len(level['events'])} -> {len(events)}")
    if n and not a.dry:
        level['events'] = events
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(level, f)


if __name__ == '__main__':
    main()
