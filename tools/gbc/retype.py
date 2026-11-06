"""Episode 7's committed levels given new PC enemies for some GBC types, keeping everything else of theirs.

The committed levels (data/gbc/episode7/levels) are episode.py's output worked over since (boss.py, edits by hand),
and episode.py no longer makes their events exactly again (the matcher's candidates changed since); so a change to
enemy_overrides.json is carried into them enemy by enemy: the level's script is translated again (episode.enemies,
with the level's sheets and the types' new PC enemies), and each GBC record of a changed type has its events (its
fight, object, spawns and its link's speeds made with it) put in place of the committed level's for that record:
those at the record's time on its link, the k-th there as the record is the k-th there (the links are the GBC
groups', numbered alike). A type now left out (null) loses its records' events. The difficulty skips (event 66) that
count over a replaced enemy count its new events. The level's sheets: its own, with those the new PC enemies need
added (up to episode.BANKS; event 5 the first four, event 210 the others). The GBC boss's pieces (boss.py's own
events) are left alone; the script's other records in its stretch are carried as the others.

    python tools/gbc/retype.py --levels 1,2 [--rev HEAD] [--dry]
"""
import argparse
import contextlib
import difflib
import glob
import io
import json
import os
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import episode as E  # noqa: E402
import enemies as EN  # noqa: E402
import script  # noqa: E402
import waves  # noqa: E402

LINK_EVENTS = (19, 20, 55)  # (a link's speeds, made with its enemy: script.py spawn_events)


def overrides_at(rev):
    return json.loads(subprocess.run(['git', 'show', f'{rev}:tools/gbc/enemy_overrides.json'], cwd=ROOT,
                                     capture_output=True, text=True, encoding='utf-8', check=True).stdout)


def as_type(v):
    """An override's value as episode.enemies' type (episode, enemy, parts key)."""
    if v[0] == 'gbc':
        return ('gbc', sorted(E.NEW_ENEMIES).index(v[1]) + 1, 4 if len(E.NEW_ENEMIES[v[1]]['parts']) == 4 else 1)
    if isinstance(v[1], list):
        return (v[0], v[1][0][0], EN.parts_key(v[1]))
    return (v[0], v[1], EN.parts_key(v[2] if len(v) > 2 else 1))


def sheets_of_type(tp):
    ep, n, parts = tp
    if ep == 'gbc':
        return {E.NEW_SHEET}
    E.enemy_data(ep, n)
    data = E._enemy_data[ep]
    nums = [p[0] for p in parts] if isinstance(parts, tuple) else range(n, n + (4 if parts == 4 else 1))
    return set().union(*(waves.sheets_of(data, m) for m in nums)) - {0, 99}


def translated(spec, banks, types_given):
    """The level's script translated with these sheets and types, each event tagged with its record (_rid, _type)."""
    one = script.Translator.one
    count = [0]

    def tagged(self, rec, t):
        count[0] += 1
        evs = one(self, rec, t)
        for e in evs:
            e['_rid'], e['_type'] = count[0], rec[1]
        return evs
    script.Translator.one = tagged
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            events, _, _, _ = E.enemies(spec, waves.Source(*spec['pc']), banks_given=banks, types_given=types_given)
    finally:
        script.Translator.one = one
    return [e for e in events if '_rid' in e]  # (the boss's pieces, boss.py's own, have none: never replaced)


def units_at(events, t, link):
    """The committed level's enemies made at clock t on this link, in order: (first, last) indices of each one's
    events (its fight 203, object 201, spawns, and the link's speeds right after); link None: on any link."""
    out = []
    i = 0
    while i < len(events):
        e = events[i]
        if e['t'] > t:
            break
        if e['t'] == t and e['type'] in waves.SPAWNS and (link is None or e['d4'] == link):
            link_ = e['d4']
            first, last = i, i
            if i > 0 and events[i - 1]['t'] == t and events[i - 1]['type'] == script.OBJECT:
                first = i - 1
                n, last = events[i - 1]['d1'], i - 1
                while n and last + 1 < len(events):
                    last += 1
                    if events[last]['type'] in waves.SPAWNS:
                        n -= 1
            if first > 0 and events[first - 1]['t'] == t and events[first - 1]['type'] == script.FIGHT:
                first -= 1
            while last + 1 < len(events) and events[last + 1]['t'] == t and events[last + 1]['type'] in LINK_EVENTS \
                    and events[last + 1]['d4'] == link_:
                last += 1
            out.append((first, last))
            i = last + 1
            continue
        i += 1
    return out


def unloaded_spawns(level):
    """The PC enemies the level spawns on sheets it doesn't load ({(episode, enemy): sheets})."""
    banks = set(level['banks'])
    out = defaultdict(set)
    for e in level['events']:
        if e['type'] in waves.SPAWNS and e['d1'] > 0 and isinstance(e.get('ep'), int):
            if E.enemy_data(e['ep'], e['d1']) is None:
                continue
            for k in range(4 if e['type'] == 12 else 1):
                sheets = waves.sheets_of(E._enemy_data[e['ep']], e['d1'] + k) - {0, 99}
                if not sheets <= banks:
                    out[(e['ep'], e['d1'] + k)] |= sheets - banks
    return dict(out)


def retype(n, rev='HEAD', dry=False):
    spec = E.spec_of(n)
    path = glob.glob(os.path.join(E.OUT, 'levels', f'*_L{n:02d}.json'))[0]
    level = json.load(open(path))
    old = {int(k[4:], 16): v for k, v in overrides_at(rev).items() if int(k[1:3]) == n}
    new = {int(k[4:], 16): v for k, v in json.load(open(E.OVERRIDES)).items() if int(k[1:3]) == n}
    changed = {t for t in set(old) | set(new) if old.get(t, 'none') != new.get(t, 'none') and t in new}
    if not changed:
        print(f"L{n:02d} {spec['name']}: no type changed")
        return
    # the sheets: the level's, and those its new PC enemies need
    banks = list(level['banks'])
    for t in sorted(changed):
        if new[t] is not None:
            for b in sorted(sheets_of_type(as_type(new[t]))):
                if b not in banks:
                    banks.append(b)
    if len(banks) > E.BANKS:
        raise SystemExit(f"L{n:02d}: {len(banks)} sheets needed ({banks}), at most {E.BANKS}")
    # (a type left out now is translated as before, so that the links come as the committed level's; its events go)
    d = json.load(open(os.path.join(E.GBC, 'enemies', f'L{n:02d}.json')))
    given = {}
    for t in changed:
        if new[t] is not None:
            given[t] = as_type(new[t])
        else:
            cands = d['types'].get(str(t), {}).get('candidates') or []
            if cands:
                c = cands[0]
                given[t] = (c['episode'], c['enemy'], EN.parts_key(c.get('parts', 1)))
    run = translated(spec, banks, given)
    # each record's events, and its place among the records made at its time on its link
    recs = defaultdict(list)
    for e in run:
        recs[e['_rid']].append(e)
    order = defaultdict(list)
    for rid in sorted(recs):
        sp = [e for e in recs[rid] if e['type'] in waves.SPAWNS]
        if sp:
            order[(sp[0]['t'], sp[0]['d4'])].append(rid)
    events = level['events']
    cover = [set() for _ in events]
    for i, e in enumerate(events):
        if e['type'] == 66:
            for j in range(i + 1, min(len(events), i + 1 + e['d2'])):
                cover[j].add(id(e))
    tagged = [[e, c] for e, c in zip(events, cover)]
    done, gone, missed = 0, 0, []

    def hp(rid=None, unit=None):
        # (an enemy's hit points, its fight event's: the GBC type's, whatever the PC enemy; None without one)
        e = next((e for e in recs[rid] if e['type'] == script.FIGHT), None) if rid else \
            (plain[unit[0]] if plain[unit[0]]['type'] == script.FIGHT else None)
        return e['d1'] if e else None
    for (t, link), rids in sorted(order.items()):
        mine = [k for k, rid in enumerate(rids) if recs[rid][0]['_type'] in changed]
        if not mine:
            continue
        plain = [x[0] for x in tagged]
        units = units_at(plain, t, link)
        if not units:
            # (the GBC boss's stretch, its links numbered otherwise when the committed level was made: the enemies
            # at that time on links none of the records there have)
            busy = {l for (tt, l) in order if tt == t}
            units = [u for u in units_at(plain, t, None)
                     if next(plain[i]['d4'] for i in range(u[0], u[1] + 1) if plain[i]['type'] in waves.SPAWNS) not in busy]
        # (the records there as the committed enemies there, by their hit points: a record the committed level
        # left out, as a piece of another's enemy, has none)
        pair = {}
        sm = difflib.SequenceMatcher(a=[hp(rid=r) for r in rids], b=[hp(unit=u) for u in units], autojunk=False)
        for a0, b0, size in sm.get_matching_blocks():
            for j in range(size):
                pair[a0 + j] = b0 + j
        lost = [k for k in mine if k not in pair]
        if lost:
            missed.append(f"{t} link {link}: {len(lost)} of type {recs[rids[lost[0]]][0]['_type']:02x} "
                          f"({len(units)} enemies there, {len(rids)} records)")
        for k in sorted((k for k in mine if k in pair), key=lambda k: -pair[k]):
            rid = rids[k]
            first, last = units[pair[k]]
            put = [] if new[recs[rid][0]['_type']] is None else \
                [{f: v for f, v in e.items() if not f.startswith('_')} for e in recs[rid] if e['type'] != 66]
            # (on the committed enemy's link)
            was = next(plain[i]['d4'] for i in range(first, last + 1) if plain[i]['type'] in waves.SPAWNS)
            for e in put:
                if e['d4'] == link and (e['type'] in waves.SPAWNS or e['type'] in LINK_EVENTS):
                    e['d4'] = was
            c = set.intersection(*(tagged[i][1] for i in range(first, last + 1)))
            tagged[first:last + 1] = [[e, set(c)] for e in put]
            done += bool(put)
            gone += not put
    events = [x[0] for x in tagged]
    for e in events:
        if e['type'] == 66:
            e['d2'] = sum(1 for x in tagged if id(e) in x[1])
    note = ''
    if banks != level['banks']:
        note = f", sheets {level['banks']} -> {banks}"
        level['banks'] = banks
        events = [e for e in events if not (e['t'] == 0 and e['type'] in (5, 210))]
        at = next((i for i, e in enumerate(events) if e['t'] == 0 and e['type'] == 13), 0)
        events[at:at] = E.sheet_events(banks)
    level['events'] = events
    print(f"L{n:02d} {spec['name']}: types {' '.join(f'{t:02x}' for t in sorted(changed))}: {done} enemies made anew, "
          f"{gone} left out, {len(missed)} places not matched{note}")
    for m in missed:
        print('   not matched:', m)
    unloaded = unloaded_spawns(level)
    if unloaded:
        print(f"   spawns whose sheets aren't loaded ({level['banks']}): {unloaded}")
    if not dry:
        json.dump(level, open(path, 'w'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', required=True, help='GBC level numbers')
    ap.add_argument('--rev', default='HEAD', help="the overrides as they were (a git revision)")
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    for n in (int(x) for x in a.levels.split(',')):
        retype(n, a.rev, a.dry)


if __name__ == '__main__':
    main()
