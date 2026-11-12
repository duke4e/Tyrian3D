"""Episode 7's flying rocks in more than one look: the committed levels' spawns of one PC rock turned in turn to the
rocks of its family (episode 1's sky rocks of sheet D), at the same speed.

The user's playtest (2026-11-12): "ep 7, asteroid 1, svi leteći kameni su istog izgleda, trebali bi napravit varijacije,
pošto ih orginal pc igra i ima". GBC ASTEROID has one rock; the PC game's rocks of that family are D 43 (260-262), D 85
(263-265), D 123 (266-268) and the lumpy D 5 (135-137), each a model of its own (models.cfg "Asteroids in the sky").

    python tools/gbc/rocks.py [--dry]
"""
import argparse
import glob
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = os.path.join(HERE, '..', '..', 'data', 'gbc', 'episode7', 'levels')

# level: (episode, rock, [(rock, its ymove less the first's: added to the event's d3), ...] taken in turn)
ROCKS = {
    'ASTEROID': (1, 260, [(260, 0), (263, 0), (266, 0), (135, 3)]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    for path in sorted(glob.glob(os.path.join(LEVELS, '*.json'))):
        level = json.load(open(path, encoding='utf-8'))
        if level['name'] not in ROCKS:
            continue
        ep, rock, turns = ROCKS[level['name']]
        done, k = Counter(), 0
        for e in level['events']:
            if e.get('ep') == ep and e['d1'] == rock and e['type'] in (6, 7, 10, 15, 17, 18):
                new, slower = turns[k % len(turns)]
                k += 1
                e['d1'], e['d3'] = new, e['d3'] + slower
                done[new] += 1
        print(f"{level['name']}: {dict(done)}")
        if done and not a.dry:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(level, f)


if __name__ == '__main__':
    main()
