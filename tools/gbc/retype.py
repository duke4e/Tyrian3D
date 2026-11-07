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

--respawn (2026-11-07): the records the script now makes from the screen's bottom (script.py gbc_y: low on the GBC
screen or below it) get their committed enemies' spawns made there, each keeping its PC enemy (read from the committed
level) and its other events; a record not found at its time is looked for a tick or two off on its link.
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
        c = E.own_type(v)
        return ('gbc', c['enemy'], EN.parts_key(c['parts']))
    if isinstance(v[1], list):
        return (v[0], v[1][0][0], EN.parts_key(v[1]))
    return (v[0], v[1], EN.parts_key(v[2] if len(v) > 2 else 1))


def sheets_of_type(tp):
    ep, n, parts = tp
    if ep == 'gbc':
        names = list(E.NEW_ENEMIES)
        return {E.own_sheet(names[m - 1]) for m in ([p[0] for p in parts] if isinstance(parts, tuple) else [n])}
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
    init = script.Translator.__init__

    def kept(self, *a, **k):  # (its notes: what it couldn't place as the GBC does)
        init(self, *a, **k)
        NOTES.append(self.notes)
    script.Translator.__init__ = kept
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            events, _, _, _ = E.enemies(spec, waves.Source(*spec['pc']), banks_given=banks, types_given=types_given)
    finally:
        script.Translator.one = one
        script.Translator.__init__ = init
    return [e for e in events if '_rid' in e]  # (the boss's pieces, boss.py's own, have none: never replaced)


NOTES = []


def records(run):
    """A translation's events by record ({rid: events}), and the records made at each time on each link, in order."""
    recs = defaultdict(list)
    for e in run:
        recs[e['_rid']].append(e)
    order = defaultdict(list)
    for rid in sorted(recs):
        sp = [e for e in recs[rid] if e['type'] in waves.SPAWNS]
        if sp:
            order[(sp[0]['t'], sp[0]['d4'])].append(rid)
    return recs, order


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


def carry(events, recs, order, want, put_of):
    """Each wanted record's events in place of the committed enemy made for it: the enemies made at the record's time
    on its link (in a GBC boss's stretch, numbered otherwise when the committed level was made: on links none of the
    records there have), paired with the records there by their hit points (a record the committed level left out, as a
    piece of another's enemy, has none). put_of(rid, the unit's events) -> its new events ([]: left out; None: keep
    it). The new events (the difficulty skips that counted over a replaced enemy count its new events), how many were
    made anew, left out, and the places not matched."""
    cover = [set() for _ in events]
    for i, e in enumerate(events):
        if e['type'] == 66:
            for j in range(i + 1, min(len(events), i + 1 + e['d2'])):
                cover[j].add(id(e))
    tagged = [[e, c] for e, c in zip(events, cover)]
    done, gone, missed = 0, 0, []

    def hp(rid=None, unit=None):
        # (an enemy's hit points, its fight event's: the GBC type's, whatever the PC enemy; None without one)
        e = next((e for e in recs[rid] if e['type'] == script.FIGHT), None) if rid else             (plain[unit[0]] if plain[unit[0]]['type'] == script.FIGHT else None)
        return e['d1'] if e else None
    for (t, link), rids in sorted(order.items()):
        mine = [k for k, rid in enumerate(rids) if want(rid)]
        if not mine:
            continue
        plain = [x[0] for x in tagged]
        units = units_at(plain, t, link)
        if not units:
            busy = {l for (tt, l) in order if tt == t}
            units = [u for u in units_at(plain, t, None)
                     if next(plain[i]['d4'] for i in range(u[0], u[1] + 1) if plain[i]['type'] in waves.SPAWNS) not in busy]
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
            put = put_of(rid, plain[first:last + 1])
            if put is None:
                continue
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
    return events, done, gone, missed


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
    recs, order = records(translated(spec, banks, given))

    def put_of(rid, unit):
        return [] if new[recs[rid][0]['_type']] is None else \
            [{f: v for f, v in e.items() if not f.startswith('_')} for e in recs[rid] if e['type'] != 66]
    events, done, gone, missed = carry(level['events'], recs, order, lambda rid: recs[rid][0]['_type'] in changed,
                                       put_of)
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


def committed_type(unit, cands):
    """A committed enemy's PC enemy as a type (episode, enemy, parts key): a spawn's, event 12's four parts, or the
    candidate composite whose parts its spawns are; None for a GBC boss's piece or one none fits."""
    sp = [e for e in unit if e['type'] in waves.SPAWNS]
    if not sp or sp[0].get('ep') in (None, 'boss'):
        return None
    ep = sp[0]['ep']
    if sp[0]['type'] == 12:
        return ep, sp[0]['d1'], 4
    if len(sp) == 1 and not any(e['type'] == script.OBJECT for e in unit):
        return ep, sp[0]['d1'], 1
    nums = [e['d1'] for e in sp]
    return next((c for c in cands if c[0] == ep and isinstance(c[2], tuple) and [p[0] for p in c[2]] == nums), None)


def respawn(n, dry=False):
    """The committed level's enemies the GBC makes low on its screen or below it (rising into view: script.py
    gbc_y) made there, from the screen's bottom (events 18 and 17), where they were made above the screen or at the top
    spawn's lowest: each such record's committed enemy keeps its PC enemy and all its events but its spawns' type and
    y, which the script translated again with that PC enemy gives."""
    spec = E.spec_of(n)
    path = glob.glob(os.path.join(E.OUT, 'levels', f'*_L{n:02d}.json'))[0]
    level = json.load(open(path))
    d = json.load(open(os.path.join(E.GBC, 'enemies', f'L{n:02d}.json')))
    over = {int(k[4:], 16): v for k, v in json.load(open(E.OVERRIDES)).items() if int(k[1:3]) == n}

    def cands(t):
        return ([as_type(over[t])] if over.get(t) else []) + \
            [(c['episode'], c['enemy'], EN.parts_key(c.get('parts', 1))) for c in d['types'].get(str(t), {}).get('candidates') or []]

    def low(evs):
        return any(e['type'] in (script.BOTTOM_SKY, script.BOTTOM_GROUND) for e in evs)
    # the committed enemies' PC enemies, by type (the translation's may differ: the matcher's candidates changed since)
    found = defaultdict(lambda: defaultdict(int))
    recs, order = records(translated(spec, level['banks'], {}))

    def look(rid, unit):
        tp = committed_type(unit, cands(recs[rid][0]['_type']))
        if tp:
            found[recs[rid][0]['_type']][tp] += 1
    carry(level['events'], recs, order, lambda rid: low(recs[rid]), look)
    given = {t: max(c, key=c.get) for t, c in found.items()}
    del NOTES[:]
    recs, order = records(translated(spec, level['banks'], given))
    kept = []

    def span(evs):
        # (an enemy's object event and spawns: first and last index)
        at = [i for i, e in enumerate(evs) if e['type'] in waves.SPAWNS]
        first = at[0] - 1 if at[0] > 0 and evs[at[0] - 1]['type'] == script.OBJECT else at[0]
        return first, at[-1]

    def put_of(rid, unit):
        t = recs[rid][0]['_type']
        new = [e for e in recs[rid] if e['type'] in waves.SPAWNS]
        old = [e for e in unit if e['type'] in waves.SPAWNS]
        nums = [e['d1'] for e in old]
        if old and old[0]['type'] == 12:
            nums = [old[0]['d1'] + k for k in range(4)]  # (event 12's four parts: made apart from the bottom)
        seen.add(rid)
        # (one made where the old placement put such a record: above the screen, or at the top spawn's lowest; one
        # made on the screen is another record's, paired by its hit points in a GBC boss's stretch)
        if not any(e['d5'] >= 127 or e['d5'] <= -60 or e['type'] in (script.BOTTOM_SKY, script.BOTTOM_GROUND)
                   for e in old):
            kept.append(f"{unit[0]['t']} type {t:02x}: made on the screen there (paired wrongly?)")
            return None
        single =len(old) == 1 and len(new) == 1 and old[0]['type'] != 12 and \
            not any(e['type'] == script.OBJECT for e in unit + recs[rid])
        # (one spawn is placed alike whatever the PC enemy: one swapped by hand keeps its own)
        if not single and (committed_type(unit, cands(t)) != given.get(t) or [e['d1'] for e in new] != nums):
            kept.append(f"{unit[0]['t']} type {t:02x}: another PC enemy than the type's there")
            return None
        # (paired on another link, in a GBC boss's stretch: only one made at the same x; on its own link its x may
        # differ a little, the type's size as the matcher has it now)
        if old[0]['d4'] != new[0]['d4'] and [e['d2'] for e in new] != [e['d2'] for e in old]:
            kept.append(f"{unit[0]['t']} type {t:02x}: made elsewhere (paired wrongly?)")
            return None
        if old[0]['type'] == 12:
            # (its object and spawns the translation's, its other events the committed ones)
            a, b = span(unit)
            na, nb = span(recs[rid])
            return [dict(e) for e in unit[:a]] + \
                [{f: v for f, v in e.items() if not f.startswith('_')} for e in recs[rid][na:nb + 1]] + \
                [dict(e) for e in unit[b + 1:] if not (e['type'] == 19 and e['d1'] == -99 and e['d2'] == -99)]
        out, k = [], 0
        for e in unit:
            e = dict(e)
            if e['type'] in waves.SPAWNS:
                # (on the committed one's layer: a PC enemy swapped by hand may stand on the ground or not)
                bottom = new[k]['type'] in (script.BOTTOM_SKY, script.BOTTOM_GROUND)
                ground = e['type'] in (script.GROUND, script.BOTTOM_GROUND)
                e['type'] = (script.BOTTOM_GROUND if ground else script.BOTTOM_SKY) if bottom else \
                    (script.GROUND if ground else script.SKY)
                e['d5'] = new[k]['d5']
                k += 1
            out.append(e)
        return out
    seen = set()
    events, done, _, missed = carry(level['events'], recs, order, lambda rid: low(recs[rid]), put_of)
    # (a record not found at its time: in a GBC boss's stretch the committed level may make it a tick or two off, on the
    # same link: its one spawn, the same PC enemy at the same x made at the top)
    taken = set()
    for rid in sorted(r for r in recs if low(recs[r]) and r not in seen):
        new = [e for e in recs[rid] if e['type'] in waves.SPAWNS]
        if len(new) != 1 or any(e['type'] == script.OBJECT for e in recs[rid]):
            continue
        s = new[0]
        hit = [i for i, e in enumerate(events) if i not in taken and e['type'] in (script.SKY, script.GROUND,
                                                                              script.BOTTOM_SKY, script.BOTTOM_GROUND)
               and abs(e['t'] - s['t']) <= 2 and e['d4'] == s['d4'] and e['d1'] == s['d1'] and e['d2'] == s['d2']
               and e.get('ep') == s.get('ep')]
        if len(hit) == 1:
            taken.add(hit[0])
            ground = events[hit[0]]['type'] in (script.GROUND, script.BOTTOM_GROUND)
            events[hit[0]] = dict(events[hit[0]], type=script.BOTTOM_GROUND if ground else script.BOTTOM_SKY, d5=s['d5'])
            done += 1
            missed = [m for m in missed if not m.startswith(f"{s['t']} link {s['d4']}:")]
    level['events'] = events
    notes = sorted({x for ns in NOTES for x in ns})
    print(f"L{n:02d} {spec['name']}: {done} enemies made from the screen's bottom (types "
          f"{' '.join(f'{t:02x}' for t in sorted({recs[r][0]['_type'] for r in recs if low(recs[r])}))}), "
          f"{len(missed)} places not matched, {len(kept)} kept as they were")
    for m in missed:
        print('   not matched:', m)
    for m in kept:
        print('   kept as it was:', m)
    for m in notes:
        print('   note:', m)
    if not dry and done:
        json.dump(level, open(path, 'w'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', required=True, help='GBC level numbers')
    ap.add_argument('--rev', default='HEAD', help="the overrides as they were (a git revision)")
    ap.add_argument('--respawn', action='store_true', help="make the enemies low on the GBC screen or below it there")
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    for n in (int(x) for x in a.levels.split(',')):
        if a.respawn:
            respawn(n, a.dry)
        else:
            retype(n, a.rev, a.dry)


if __name__ == '__main__':
    main()
