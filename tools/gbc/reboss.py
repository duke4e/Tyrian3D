"""Episode 7's committed levels given the bosses episode.py's level specs now ask for, keeping everything else of theirs
(as retype.py does for the enemies): a spec with gbc_boss=False gets its PC boss (boss=, else the original level's)
whole, placed at the GBC boss's time, in place of the GBC boss's pieces (the level's events from the GBC boss's start on
go: its pieces, the script's records over it, its loop and end; tools/content/gbc/build.py makes the placed boss's
fight and the level's end when it is gone); a spec with no_boss=True loses its placed boss, and the level ends as
episode.py ends one without a boss (its last event 600 ticks on, or the map's end). The boss song (event 204) goes
with the boss; the difficulty skips (66) count what is left; the level's sheets get those the placed boss needs.

    python tools/gbc/reboss.py --levels 20,2 [--dry]
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import episode as E  # noqa: E402
import waves  # noqa: E402


def ev(t, type_, d1=0):
    return dict(t=t, type=type_, d1=d1, d2=0, d3=0, d5=0, d6=0, d4=0)


def keep_only(events, keep):
    """The events kept (keep: a predicate on an index), the difficulty skips (66) counting those left of theirs."""
    cover = [set() for _ in events]
    for i, e in enumerate(events):
        if e['type'] == 66:
            for j in range(i + 1, min(len(events), i + 1 + e['d2'])):
                cover[j].add(i)
    kept = [(i, e) for i, e in enumerate(events) if keep(i)]
    out = []
    for i, e in kept:
        if e['type'] == 66:
            n = sum(1 for j, _ in kept if i in cover[j])
            if n == 0:
                continue
            e = dict(e, d2=n)
        out.append(e)
    return out


def reboss(n, dry=False):
    spec = E.spec_of(n)
    path = glob.glob(os.path.join(E.OUT, 'levels', f'*_L{n:02d}.json'))[0]
    level = json.load(open(path))
    events = level['events']
    note = None
    if spec.get('no_boss'):
        if not any(p['kind'] == 'boss' for p in level['placements']):
            print(f"L{n:02d} {spec['name']}: no boss placed already")
            return
        level['placements'] = [p for p in level['placements'] if p['kind'] != 'boss']
        events = keep_only(events, lambda i: events[i]['type'] not in (11, 204))
        last = max(e['t'] for e in events)
        end = min(8100, max(28 * (level['pc_rows'] - 7) + 200, last + 600))
        events.append(ev(end, 11))
        note = f'its placed boss gone, the end at {end}'
    elif spec.get('gbc_boss', True) is False and level.get('gbc_boss'):
        start = level['gbc_boss']['start']
        src = waves.Source(*spec['boss']) if spec.get('boss') else waves.Source(*spec['pc'])
        boss = src.boss()
        if boss is None:
            raise SystemExit(f"L{n:02d}: {src.name} has no boss")
        gone = sum(1 for e in events if e['t'] >= start)
        events = keep_only(events, lambda i: events[i]['t'] < start and events[i]['type'] != 11)
        place = dict(kind='boss', episode=src.episode, name=src.name, start=start,
                     end=start + max([e['t'] for e in boss['events']] + [0]))
        level['placements'] = [p for p in level['placements'] if p['kind'] != 'boss'] + [place]
        level['gbc_boss'] = None
        events.append(ev(start, 204, 1))
        events.append(ev(max(8100, place['end'] + 600), 11))
        # (its sheets: those its pieces and what they launch need, as episode.enemies loads the boss's first)
        need = set()
        for e in boss['events']:
            if e['type'] in waves.SPAWNS and e['d1'] > 0:
                for k in range(4 if e['type'] == 12 else 1):
                    need |= waves.sheets_of(src.enemies, e['d1'] + k)
        banks = list(level['banks'])
        for b in sorted(need - {0, 99, 21, 26}):
            if b not in banks:
                banks.append(b)
        if len(banks) > E.BANKS:
            raise SystemExit(f"L{n:02d}: {len(banks)} sheets needed ({banks}), at most {E.BANKS}")
        if banks != level['banks']:
            level['banks'] = banks
            events = [e for e in events if not (e['t'] == 0 and e['type'] in (5, 210))]
            at = next((i for i, e in enumerate(events) if e['t'] == 0 and e['type'] == 13), 0)
            events[at:at] = E.sheet_events(banks)
        note = f'{gone} events of its GBC boss gone, {src.name} placed at {start}, sheets {level["banks"]}'
    else:
        print(f"L{n:02d} {spec['name']}: its boss as the spec has it already")
        return
    events.sort(key=lambda e: e['t'])  # (stable: the order within a tick stays)
    level['events'] = events
    print(f"L{n:02d} {spec['name']}: {note}")
    if not dry:
        json.dump(level, open(path, 'w'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', required=True, help='GBC level numbers')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    for n in (int(x) for x in a.levels.split(',')):
        reboss(n, a.dry)


if __name__ == '__main__':
    main()
