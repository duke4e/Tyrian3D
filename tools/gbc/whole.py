"""Episode 7's enemies drawn from part of a PC object made whole: the committed levels' spawns of some of an object's
parts (alone, or an event 201 object of some of them) get the missing parts, at the places the PC levels put them, and
are one object (event 201: they die together).

The user's playtest (2026-11-11): DESERT's turrets without their body and its stepped blocks without their turret
("polomljene piramide"), OASIS's "krivo spojeni" enemies and its boss's missing part, JUNGLE's and JUNGLE II's
turrets missing part of their body or their front, ASTEROID2's towers whose base went and left the top flying. The
parts and their offsets are those the PC levels always spawn together (tools/gbc/static_ground.py's sources).
tools/gbc/retype.py can't do it: the levels' clocks were stretched since (dictionary.py apply).

Spawns of one tick on one link that are parts of the same object at its offsets are taken together first (JUNGLE makes
its turret's two halves as two GBC types). The difficulty skips (event 66) count the events they did.

    python tools/gbc/whole.py [--levels 2,4] [--dry]
"""
import argparse
import glob
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = os.path.join(HERE, '..', '..', 'data', 'gbc', 'episode7', 'levels')
SPAWNS = {6, 7, 10, 15, 17, 18, 23, 32, 56}
OBJECT = 201
NEAR = 6  # (pixels a part may lie off its place and still be the object's: ASTEROID2's tower top 24 above, not 28)

# (episode, [(enemy, dx, dy), ...]): offsets from the object's top left, as the PC levels place them (d2, d5)
WHOLE = {
    'lamp block, turret': (4, [(206, 0, 3), (207, 24, 3), (205, 16, 0)]),
    'lamp block 2, turret': (4, [(203, 0, 3), (204, 24, 3), (205, 12, 0)]),
    'OASIS block': (4, [(312, 0, 0), (313, 24, 0), (314, 48, 0), (309, 0, 28), (310, 24, 28), (311, 48, 28)]),
    'JUNGLE turret': (2, [(758, 0, 0), (759, 0, 28)]),
    'JUNGLE pod': (2, [(756, 0, 0), (757, 24, 0)]),
    'JUNGLE pair': (2, [(753, 0, 0), (754, 24, 0)]),
    'ASTEROID2 tower': (1, [(287, 0, 0), (288, 0, 28)]),
    'DELIANI pair': (1, [(241, 0, 0), (242, 24, 0)]),
}
# (a part of more than one: the object its lone spawns become)
LONE = {(4, 205): 'lamp block, turret'}


def objects_of(ep, enemy):
    if (ep, enemy) in LONE:
        return [LONE[(ep, enemy)]]
    return [name for name, (e, parts) in WHOLE.items() if e == ep and enemy in [p[0] for p in parts]]


def units(events):
    """The tick's enemies: (indices of their events, head index or None) — an event 201 and its next d1 events, or a
    spawn of its own."""
    out, i = [], 0
    while i < len(events):
        e = events[i]
        if e['type'] == OBJECT:
            out.append((list(range(i + 1, min(len(events), i + 1 + e['d1']))), i))
            i += 1 + e['d1']
        elif e['type'] in SPAWNS and e['d1'] > 0:
            out.append(([i], None))
            i += 1
        else:
            i += 1
    return out


def fix(level):
    """The level's events with its partial objects whole; how many made whole."""
    ev = level['events']
    new_of = {}            # old index -> list of new events in its place (empty: removed)
    made = Counter()
    ticks = {}
    for i, e in enumerate(ev):
        ticks.setdefault(e['t'], []).append(i)
    for t, idx in ticks.items():
        tick = [ev[i] for i in idx]
        cands = []
        for parts, head in units(tick):
            spawns = [tick[p] for p in parts if tick[p]['type'] in SPAWNS]
            if not spawns or not all(isinstance(s.get('ep'), int) for s in spawns):
                continue
            eps = {s['ep'] for s in spawns}
            names = set.intersection(*[set(objects_of(s['ep'], s['d1'])) for s in spawns]) if len(eps) == 1 else set()
            if len(names) != 1:
                continue
            name = names.pop()
            cands.append(dict(name=name, parts=parts, head=head, spawns=spawns))
        # (lone spawns of one object on one link at its offsets taken together)
        groups = []
        for c in cands:
            ep, layout = WHOLE[c['name']]
            off = {m: (dx, dy) for m, dx, dy in layout}
            a = c['spawns'][0]
            origin = (a['d2'] - off[a['d1']][0], a['d5'] - off[a['d1']][1])
            for g in groups:
                near = max(abs(g['origin'][0] - origin[0]), abs(g['origin'][1] - origin[1])) <= NEAR
                if g['name'] == c['name'] and near and g['link'] == a['d4'] and \
                        not {s['d1'] for s in g['spawns']} & {s['d1'] for s in c['spawns']}:
                    g['spawns'] += c['spawns']
                    g['units'].append(c)
                    break
            else:
                groups.append(dict(name=c['name'], origin=origin, link=a['d4'], spawns=list(c['spawns']), units=[c]))
        for g in groups:
            ep, layout = WHOLE[g['name']]
            have = {s['d1'] for s in g['spawns']}
            if have >= {m for m, _, _ in layout} and len(g['units']) == 1 and g['units'][0]['head'] is not None:
                continue  # (whole already, one object; whole but its parts apart, ASTEROID2's tower: made one)
            first = g['units'][0]
            a = g['spawns'][0]
            # its events: an event 201 for all its parts, the parts it had, then the missing ones (copies of the first)
            evs = [dict(t=t, type=OBJECT, d1=len(layout), d2=0, d3=0, d5=0, d6=0, d4=0)]
            evs += g['spawns']
            for m, dx, dy in layout:
                if m not in have:
                    evs.append(dict(a, d1=m, d2=g['origin'][0] + dx, d5=g['origin'][1] + dy))
            anchor = idx[first['head'] if first['head'] is not None else first['parts'][0]]
            new_of[anchor] = evs
            for u in g['units']:
                for p in ([u['head']] if u['head'] is not None else []) + u['parts']:
                    if idx[p] != anchor:
                        new_of[idx[p]] = []
            made[g['name']] += 1
    if not made:
        return ev, made
    out, where = [], []    # where: the new index each old one starts at
    for i, e in enumerate(ev):
        where.append(len(out))
        out.extend(new_of.get(i, [e]))
    where.append(len(out))
    for i, e in enumerate(ev):  # (a difficulty skip counts the events its old ones are now)
        if e['type'] == 66 and i not in new_of:
            j = where[i]
            out[j] = dict(out[j], d2=where[min(len(ev), i + 1 + e['d2'])] - where[i + 1])
    return out, made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', help='GBC level numbers (default: all)')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    want = None if not a.levels else {int(x) for x in a.levels.split(',')}
    for path in sorted(glob.glob(os.path.join(LEVELS, '*.json'))):
        n = int(os.path.basename(path)[4:6])
        if want and n not in want:
            continue
        level = json.load(open(path, encoding='utf-8'))
        events, made = fix(level)
        if made:
            print(f"L{n:02d} {level['name']}: {dict(made)}, events {len(level['events'])} -> {len(events)}")
            if not a.dry:
                level['events'] = events
                with open(path, 'w', encoding='utf-8', newline='\n') as f:
                    json.dump(level, f)


if __name__ == '__main__':
    main()
