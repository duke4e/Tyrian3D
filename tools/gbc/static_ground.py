"""The PC enemies that never move on the ground: tools/content/gbc/static_ground.json, [[episode, enemy], ...].

An enemy is static when every ground spawn of it in the PC levels (events 6, 10 and event 12's ground parts) leaves it
where the map puts it: no speed of its own (the enemy's ymove and xmove, and the event's d3 and fixed move, together
0) and no acceleration or to and fro. Turrets, bunkers and pyramids are; walkers and tanks are not. Episode 7 anchors
them to the ground where a GBC enemy drawn as one moves (tools/content/gbc/build.py anchor, tyrian2.c GBC_ANCHOR):
the user, 2026-11-11: "ovaj protivnik s piramidom bi trebao biti fiksni na podu", "imamo turreta koji se pomiču po
levelu".

usage: python tools/gbc/static_ground.py
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'content'))
import episode as E  # noqa: E402
import tyrdata  # noqa: E402
import waves  # noqa: E402

OUT = os.path.join(HERE, '..', 'content', 'gbc', 'static_ground.json')


def main():
    moves, data = defaultdict(set), {}
    for level in E.sources.original_levels():
        ep = level['episode']
        try:
            src = waves.Source(ep, level['name'])
        except Exception:  # (a level without its events)
            continue
        enemies = data.setdefault(ep, tyrdata.load_items(ep)['enemies'])
        for e in src.events:
            if e['type'] in (6, 10) and e['d1'] > 0:
                parts, fixed = [e['d1']], e['d6']
            elif e['type'] == 12 and e['d6'] in (0, 1, 4) and e['d1'] > 0:
                parts, fixed = [e['d1'] + k for k in range(4)], 0
            else:
                continue
            for p in parts:
                d = enemies.get(p, {})
                wanders = any(d.get(k) for k in ('xcaccel', 'ycaccel', 'xaccel', 'yaccel', 'xrev', 'yrev'))
                moves[(ep, p)].add((e['d3'] + d.get('ymove', 0) + fixed, d.get('xmove', 0), wanders))
    static = sorted([ep, n] for (ep, n), v in moves.items() if v == {(0, 0, False)})
    with open(OUT, 'w', newline='\n') as f:
        json.dump(static, f)
        f.write('\n')
    print(f"{OUT}: {len(static)} of {len(moves)} ground enemies static")


if __name__ == '__main__':
    main()
