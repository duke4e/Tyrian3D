"""A GBC level's boss as PC level events (episode 7): its behaviour the GBC game's own, its looks the PC boss's.

boss_rom.py found it in the ROM (data/gbc/bosses/rom.json): the script's last stretch, from the boss's spawns to its
loop (command 06), with the level's enemy types and guns. The stretch becomes PC events as the rest of the script
does (script.Translator), and what only the boss does as the PC engine has it:

- its groups' speeds: the GBC's own (gbc_speeds: as its mover changes them each frame), every change an event 19 at
  its time, the rest of the difference (whole ticks, the GBC's half pixels) made up by a nudge (corrections: to the
  GBC flight's way, boss_rom.py), so that its loops go as the GBC's; a group steered towards the ship, or whose
  steps go on through the loops, as the main script translates them (19, 20, 27, 55), unless the loop runs again
  from before its spawn (JUNGLE II's whole level): carried on through the replay, cut where the GBC's level ended;
- the other enemies of the stretch (its waves) as the main script's (script.Translator: at their types' start speeds,
  with the map only when 03 or an even block command makes them);

- its pieces (each GBC enemy of the groups spawned with the one its end waits for: a block's 16-px pieces each):
  one PC enemy each (episode 7's own record, build.py), at the GBC piece's place, drawn as the PC boss's part at
  the same place in its body (parts(): both bodies' boxes 0-1; the GBC's are the PC's made small; checked by eye,
  boss_review.py, corrections in tools/gbc/boss_overrides.json),
  with the GBC piece's hit points as its armour (255: can't be hurt; 0: dies at the first hit), its start speed, its
  guns, what it launches, the PC part's worth;
- its guns: each GBC gun with the ones that fire with it one PC weapon: the shots' speeds 4x (a GBC pixel a frame
  is 1.5 PC pixels in 0.375 ticks: script.py), at most MAX_SPEED (faster ones would pass by the ship between two
  ticks), aimed ones at the GBC's 3 pixels a frame, the same damage, from where the GBC's come;
- 0e (a group's gun, how often it fires) -> 31 (the link's three guns' frequencies), 1d's interval too;
- 0a (a group's hit points) -> 25;
- 13 with 99 (towards the ship, a step every 10 frames) -> 55 (the PC's homing: HOMING);
- 02 with its third byte (the map stands, the clock runs on) -> the map stopped (2), forced events (53), every
  enemy's drift with the map stopped (19). The pieces are sky enemies (the PC parts that stand on the ground in
  their originals too): a GBC enemy moves on the screen by its own speed, and with the map only when command 03
  or an even block command made it ($2ca8's flag, $20b8): those drift with it (fixedmovey) till it stops;
- the loop (06: the clock back) -> 54 back to its first event; when it starts before the map stops (the GBC
  runs that stretch again over the stopped map), its records again after the first time, timed as the stopped map's;
  the jump after whatever else falls on its tick;
- 05 (once group g is gone, every enemy taken off and the level over) -> 70 every CHECK ticks (a jump to the end
  once the group's link has none left; 255, none at all: the boss's links), where every enemy is taken off (41)
  and the level ends (11); pieces of that group that can't be hurt (CAMANIS's middle one: the GBC level never ends)
  on a link of their own, the group's events given to it too.

The clock: as the main script's (1.5 a position) while the map moves, (b + 1) x 0.375 a position while it stands
(02's b: a step every b + 1 frames; forced events: a tick a tick).
"""
import json
import os

import script as S

ROM_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        'data', 'gbc', 'bosses', 'rom.json')
OVERRIDES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'boss_overrides.json')
CHECK = 6           # ticks between the end checks
MAX_SPEED = 18      # PC pixels a tick: the ship's hit box is 19 high
AIM = 3             # the GBC's aimed shots: 3 pixels a frame (x and y together)
HOMING = 97         # 55's xaccel / yaccel: towards the ship, at most 8 px a tick, a step most ticks
BOSS_LINKS = range(101, 121)  # (the engine lets a piece on these die alone in episode 7: tyrian2.c gbc_piece_link)
END_GAP = 40        # ticks after the boss's last event: the end's
CUT_GAP = 100       # ticks after where the GBC's level ended in a replay its boss flies off in: the end's
SPAWNS = {3, 4, 0x21, 0x22, 0x23, 0x24}


def s8(v):
    return v - 256 if v > 127 else v


def is_spawn(r):
    return r[0] in SPAWNS or r[0] >= 0x28


def block_of(cmd):
    if cmd < 0x28:
        return 1, 1
    k = cmd - 0x28
    return ((k >> 1) & 3) + 1, (k >> 3) + 1


def load(level):
    """The level's boss as boss_rom.py found it, or None."""
    if not os.path.exists(ROM_JSON):
        return None
    return json.load(open(ROM_JSON)).get(str(level))


def units_of(bd, pieces):
    """The pieces one by one: (record index, type, x, y, group) in GBC pixels (a block's top row first, as the GBC
    spawns them: its types one after another)."""
    out = []
    for i in pieces:
        cmd, a, b, c, g = bd['records'][i]
        if cmd in (0x21, 0x22, 0x23, 0x24):
            cmd = 3
        cols, rows = block_of(cmd)
        k = 0
        for row in range(rows):
            for col in range(cols):
                out.append(dict(rec=i, type=a + k, x=b + 16 * col, y=s8(c) - 16 * (rows - 1 - row), group=g))
                k += 1
    return out


def pc_parts(src):
    """The PC boss's body: [(enemy, x, y, layer event type)] (its first spawns, event 12's four parts), or []."""
    b = src.boss()
    if not b:
        return []
    kinds = (6, 7, 10, 15, 17, 18, 23, 12, 56, 32)
    sp = [e for e in b['events'] if e['type'] in kinds and e['d1'] > 0 and e['d4'] in b['links']]
    if not sp:
        return []
    t0 = min(e['t'] for e in sp)
    out = []
    for e in sp:
        if e['t'] > t0 + 60:
            continue
        if e['type'] == 12:
            layer = {0: 6, 1: 6, 2: 15, 3: 7, 4: 6}.get(e['d6'], 6)
            for k, (dx, dy) in enumerate([(0, 28), (24, 28), (0, 0), (24, 0)]):
                out.append((e['d1'] + k, e['d2'] + dx, e['d5'] - 28 + dy, layer))
        else:
            out.append((e['d1'], e['d2'], e['d5'], e['type']))
    return list(dict.fromkeys(out))


def parts(units, body, overrides):
    """Each piece's PC part: the part of the PC boss's body nearest the piece's place in the GBC boss's (both boxes
    0-1), each part for as few pieces as can be; overrides {"type": [enemy, layer]} by eye."""
    if not body:
        return [None] * len(units)
    gx0 = min(u['x'] for u in units)
    gy0 = min(u['y'] for u in units)
    gw = max(u['x'] for u in units) + 16 - gx0
    gh = max(u['y'] for u in units) + 16 - gy0
    px0 = min(p[1] for p in body)
    py0 = min(p[2] for p in body)
    pw = max(p[1] for p in body) + 24 - px0
    ph = max(p[2] for p in body) + 28 - py0
    gu = [((u['x'] + 8 - gx0) / gw, (u['y'] + 8 - gy0) / gh) for u in units]
    pp = [((p[1] + 12 - px0) / pw, (p[2] + 14 - py0) / ph) for p in body]
    pairs = sorted((abs(a[0] - b[0]) + abs(a[1] - b[1]), i, k) for i, a in enumerate(gu) for k, b in enumerate(pp))
    cap = -(-len(units) // len(body))
    used, out = {}, [None] * len(units)
    for d, i, k in pairs:
        if out[i] is None and used.get(k, 0) < cap:
            out[i] = k
            used[k] = used.get(k, 0) + 1
    res = []
    for u, k in zip(units, out):
        o = overrides.get(f"{u['type']:02x}")
        res.append(tuple(o) if o else (body[k][0], body[k][3]))
    return res


def gun_weapon(chain):
    """A GBC gun (and the ones chained to it) as a PC enemy weapon (build.py writes it: tools/content/gbc)."""
    shots = []
    aim = 0
    for g in chain:
        if g['aimed']:
            aim = AIM
            sx = sy = 0
        else:
            sx, sy = 4 * g['vx'], 4 * g['vy']
            m = max(abs(sx), abs(sy))
            if m > MAX_SPEED:
                sx, sy = round(sx * MAX_SPEED / m), round(sy * MAX_SPEED / m)
        # (from where the GBC's come, the GBC enemy's top left + (6 + dx, dy): its middle, the PC shot's 12 px wide)
        shots.append(dict(sx=sx, sy=sy, bx=round(1.5 * g['dx']) + 6, by=round(1.5 * g['dy']) + 8,
                          attack=max(1, g['damage'])))
    # (an aimed shot at the GBC's speed: 3 pixels a frame along x and y together, the PC's aim along the
    # longer one: 4 x 3 x 0.75 for the usual angles)
    return dict(multi=len(shots), max=len(shots), aim=round(4 * aim * 0.75) if aim else 0, shots=shots)


def ticks(frames):
    return max(1, round(frames * S.FRAME))


def gbc_speeds(recs, frames, lo, hi, group, start):
    """A group's speeds as the GBC changes them, records lo..hi-1 (their frames) from state start (vx, vy, cx, cy, wx,
    wy, bx, by: speeds in half pixels a frame, steps every |c| frames, counters, where they turn): the speed set (13,
    1d), the steps (14, 16: every |c| frames the speed steps by 1, the counter starting at |c|, a negative c's at
    |c| - 1; 14 turning at its third byte), where they turn (15), as the GBC's mover does it each frame after the move
    ($2109: a step, then the turn when the speed is at a bound that isn't 0: the bound and the step change sign).
    [(frame, vx, vy)] for each change and the state after, or None for a group steered towards the ship."""
    vx, vy, cx, cy, wx, wy, bx, by = start
    out = [(frames[lo] if lo < len(frames) else 0, vx, vy)]
    by_frame = {}
    for i in range(lo, hi):
        r = recs[i]
        if r[4] == group and r[0] in (0x13, 0x1d, 0x14, 0x15, 0x16, 0x0b):
            by_frame.setdefault(frames[i], []).append(r)
    if not by_frame:
        return out, start
    f0, f1 = frames[lo], frames[hi] if hi < len(frames) else max(by_frame) + 1
    for f in range(f0, f1):
        for r in by_frame.get(f, []):
            cmd, a, b, c, g = r
            if cmd == 0x0b or (cmd in (0x13, 0x1d) and 0x63 in (a, b)):
                return None, start
            if cmd in (0x13, 0x1d):
                vx, vy = s8(a), s8(b)
            elif cmd in (0x14, 0x16):
                cx, cy = s8(a), s8(b)
                wx = a if a < 0x80 else (~a & 0xff)
                wy = b if b < 0x80 else (~b & 0xff)
                if cmd == 0x14:
                    bx = s8(c)
            else:
                bx, by = s8(a), s8(b)
        pv = (vx, vy)
        # (the move with these speeds this frame, then the steps)
        if cx:
            wx = (wx - 1) & 0xff
            if wx == 0:
                wx = abs(cx)
                vx = s8((vx + (1 if cx > 0 else -1)) & 0xff)  # (a byte: it wraps)
                if vx == bx and bx:
                    bx, cx = -bx, -cx
        if cy:
            wy = (wy - 1) & 0xff
            if wy == 0:
                wy = abs(cy)
                vy = s8((vy + (1 if cy > 0 else -1)) & 0xff)
                if vy == by and by:
                    by, cy = -by, -cy
        if (vx, vy) != pv or by_frame.get(f):
            out.append((f + 1 if (vx, vy) != pv else f, vx, vy))
    return out, (vx, vy, cx, cy, wx, wy, bx, by)


def gbc_way(changes, lo, hi):
    """How far speeds [(frame, vx, vy)] carry a group from GBC frame lo to hi, in PC pixels (a unit is half a GBC pixel a
    frame, 0.75 PC px), or None."""
    changes = sorted(changes, key=lambda c: c[0])  # (stable: same-frame changes keep their order)
    if not changes or changes[0][0] > lo:
        return None
    x = y = 0.0
    for (f, vx, vy), nxt in zip(changes, changes[1:] + [(hi, 0, 0)]):
        a, b = max(f, lo), min(nxt[0], hi)
        if b > a:
            x += 0.75 * vx * (b - a)
            y += 0.75 * vy * (b - a)
    return x, y


def simulate(events, link, t0, t1, st):
    """A link's enemies' way from clock t0 to t1 as the engine moves them (tyrian2.c JE_main, JE_drawEnemy): each tick
    the events due, the clock on (by the map's speed, event 2, or a tick when it stands and events are forced, 53),
    then the move (19 sets the speeds and drift, 20 the speed steps, 27 where they turn); none till the link's
    first spawn. [(clock, x, y, steady: no events, no steps, the map stopped; speeds)] and the state after (back:
    the map's speed, forced)."""
    st = dict(st)
    evs = sorted((e for e in events if t0 <= e['t'] < t1 and (
        e['type'] in (2, 53) or (e['type'] == 19 and (e['d4'] == link or e['d3'] == 99)) or
        (e['type'] in (20, 27) and e['d4'] in (link, 0)) or (e.get('ep') == 'boss' and e['d4'] == link))),
        key=lambda e: e['t'])
    traj, k, clock = [], 0, t0
    while clock < t1:
        due = False
        while k < len(evs) and evs[k]['t'] <= clock:
            e = evs[k]
            k += 1
            if e['type'] == 2:
                st['back'] = e['d1']
            elif e['type'] == 53:
                st['forced'] = e['d1'] != 99
            elif e.get('ep') == 'boss':
                st['here'] = True
            elif e['type'] == 19:
                due = True
                if e['d1'] != -99:
                    st['exc'] = e['d1']
                if e['d2'] != -99:
                    st['eyc'] = e['d2']
                if e['d6'] != 0:
                    st['fy'] = 0 if e['d6'] == -99 else e['d6']
            elif e['type'] == 20:
                due = True
                if e['d1'] != -99:
                    st['excc'], st['wx'] = e['d1'], abs(e['d1'])
                if e['d2'] != -99:
                    st['eycc'], st['wy'] = e['d2'], abs(e['d2'])
            else:
                due = True
                if e['d1'] != -99:
                    st['exrev'] = e['d1']
                if e['d2'] != -99:
                    st['eyrev'] = e['d2']
        step = st['back'] if st['back'] > 0 else (1 if st['forced'] else 0)
        if step <= 0:
            break  # (the clock stands: nothing comes)
        if st.get('here'):
            for v, c, w, r in (('exc', 'excc', 'wx', 'exrev'), ('eyc', 'eycc', 'wy', 'eyrev')):
                if st[c]:
                    st[w] -= 1
                    if st[w] <= 0:
                        if st[v] == st[r]:
                            st[c], st[r] = -st[c], -st[r]
                        else:
                            st[v] += 1 if st[c] > 0 else -1
                            st[w] = abs(st[c])
                            if st[v] == st[r]:
                                st[c], st[r] = -st[c], -st[r]
            steady = st['excc'] == 0 and st['eycc'] == 0 and st['fy'] == 0 and st['back'] == 0 and not due
            traj.append((clock, st['x'], st['y'], steady, st['exc'], st['eyc']))
            st['y'] += st['fy'] + st['eyc']
            st['x'] += st['exc']
        clock += step
    return traj, st


def nudge(traj, want, link):
    """Events that make up the difference between where traj ends and want (PC px from its start): a link's speed
    changed by 1-4 px a tick for a few ticks while it goes steadily (its last long enough stretch of one speed),
    then back; or none."""
    if not traj:
        return []
    dx = round(want[0] - (traj[-1][1] - traj[0][1]))
    dy = round(want[1] - (traj[-1][2] - traj[0][2]))
    if dx == 0 and dy == 0:
        return []
    runs, start = [], None
    for i, p in enumerate(traj + [(None, 0, 0, False, None, None)]):
        same = start is not None and p[3] and (p[4], p[5]) == (traj[start][4], traj[start][5])
        if start is not None and not same:
            runs.append((start, i))
            start = None
        if start is None and p[3]:
            start = i
    for speed in (1, 2, 3, 4):
        n = -(-max(abs(dx), abs(dy)) // speed)
        ok = [r for r in runs if r[1] - r[0] >= n + 2]
        if ok:
            r = ok[-1]
            t, ex, ey = traj[r[0] + 1][0], traj[r[0]][4], traj[r[0]][5]
            vx = (1 if dx > 0 else -1) * min(speed, abs(dx)) if dx else 0
            vy = (1 if dy > 0 else -1) * min(speed, abs(dy)) if dy else 0
            evs, x, y = [], 0, 0
            # (whole ticks: the last one makes up the rest)
            for k in range(n):
                sx = max(-abs(vx), min(abs(vx), dx - x))
                sy = max(-abs(vy), min(abs(vy), dy - y))
                if not evs or (evs[-1]['d1'], evs[-1]['d2']) != (ex + sx, ey + sy):
                    evs.append(S.ev(t + k, 19, ex + sx, ey + sy, 0, 0, 0, link))
                x, y = x + sx, y + sy
            evs.append(S.ev(t + n, 19, ex, ey, 0, 0, 0, link))
            return evs
    return []


class Boss:
    """The boss's events and its pieces' records, from the level's boss (load()), the main script's translator (its
    links, the types' PC enemies) and clock, and the PC boss (waves.Source) whose looks it takes."""

    def __init__(self, level, bd, tr, clock, src, launchable):
        self.level, self.bd, self.tr, self.clock = level, bd, tr, clock
        self.recs, self.pos = bd['records'], bd['positions']
        self.first = bd['first']
        self.launchable = launchable    # GBC type -> (episode, enemy) a piece may launch, or missing
        self.pieces = [i - self.first for i in bd['pieces']]
        self.groups = set(bd['groups'])
        self.units = units_of(bd, self.pieces)
        overrides = {}
        if os.path.exists(OVERRIDES):
            overrides = json.load(open(OVERRIDES)).get(f"L{level:02d}", {})
        self.src_ep = src.episode
        self.body = pc_parts(src)
        self.looks = parts(self.units, self.body, overrides)
        self.made = {}
        self.speed0 = tr.speed  # (the map's speed as the boss's stretch starts: the main script's last)
        self.events, self.records, self.guns = [], [], {}
        self.notes = []

    # the clock: positions -> PC ticks (the main script's while the map moves; (b + 1) x 0.375 a position after a
    # 02 that stops it)
    def times(self):
        stop = self.bd['stop'] - self.first if self.bd['stop'] is not None else None
        out = []
        t_stop = p_stop = rate = None
        # (each record's clock unrounded and the stopped map's rate after it: where a position between records is)
        self.t_exact, self.rates = [], []
        for i, (r, p) in enumerate(zip(self.recs, self.pos)):
            if stop is not None and i >= stop:
                if r[0] == 2 and r[3]:
                    if t_stop is None:
                        t_stop, p_stop = self.clock(p), p
                    else:
                        t_stop, p_stop = t_stop + (p - p_stop) * rate, p
                    rate = (r[2] + 1) * S.FRAME
                out.append(round(t_stop + (p - p_stop) * rate))
                self.t_exact.append(t_stop + (p - p_stop) * rate)
            else:
                out.append(self.clock(p))
                self.t_exact.append(out[-1])
            self.rates.append(rate)
        return out, (rate or S.FRAME * 2)

    def gun_slots(self):
        """Each group's guns (the pieces' own and the ones 0e and 1d give it): slots 0-2 of its pieces' records, at most
        three (the most used: a piece's own firing gun, then by how often the script turns it on); and the one it
        launches enemies with (guns 20 and up: the PC enemy's launch, apart from its guns)."""
        use, launch = {}, {}
        for u in self.units:
            t = self.bd['types'].get(f"{u['type']:02x}", {})
            n = t.get('gun')
            if n:
                d = launch if n >= 20 else use
                d.setdefault(u['group'], {})
                d[u['group']][n] = d[u['group']].get(n, 0) + (1000 if t.get('every') else 1)
        for r in self.recs:
            if r[0] == 0x0e and r[4] in self.groups:
                n = r[1] if r[1] != 0xff else r[3]
                if n:
                    d = launch if n >= 20 else use
                    d.setdefault(r[4], {})
                    d[r[4]][n] = d[r[4]].get(n, 0) + (1 if r[2] else 0)
        slots, launches = {}, {}
        for g, w in use.items():
            order = sorted(w, key=lambda n: -w[n])
            if len(order) > 3:
                self.notes.append(f"group {g}: guns {order}, the three most used kept")
            slots[g] = order[:3]
        for g, w in launch.items():
            order = sorted(w, key=lambda n: -w[n])
            if len(order) > 1:
                self.notes.append(f"group {g}: launches with guns {order}, the most used kept")
            launches[g] = order[0]
        self.launches = launches
        return slots

    def translate(self):
        bd, tr = self.bd, self.tr
        t, rate = self.times()
        k = bd['loop'][0] - self.first
        j = bd['loop'][1] - self.first
        stop = bd['stop'] - self.first if bd['stop'] is not None else None
        end = bd['end'] - self.first if bd['end'] is not None else None
        target = bd['target']
        slots = self.gun_slots()
        # the pieces' links: the boss's own (BOSS_LINKS: a piece on them goes alone when shot down)
        free = iter(BOSS_LINKS)
        for g in sorted(self.groups):
            link = next(free)
            for grp, l in list(tr.links.of.items()):
                if l == link:
                    del tr.links.of[grp]
            tr.links.of[g] = link
            tr.links.last[link] = 10 ** 9   # (never given away again)
        self.link = {g: tr.links.of[g] for g in self.groups}
        # (pieces that can't be hurt in the group the end waits for: CAMANIS's middle one, which keeps the GBC level
        # from ever ending: on a link of their own that does what the group's does, the end not waiting for them)
        g_end = self.recs[end][4] if end is not None else None
        self.inv_link = {}
        if any(u['group'] == g_end and bd['types'].get(f"{u['type']:02x}", {}).get('hp') == 255 for u in self.units):
            self.inv_link[g_end] = next(free)
            tr.links.last[self.inv_link[g_end]] = 10 ** 9
            self.notes.append(f"group {g_end}'s pieces that can't be hurt: the end doesn't wait for them (the GBC's never "
                              f"comes)")
        # the pieces' records
        piece_of = {}
        for u, look in zip(self.units, self.looks):
            piece_of.setdefault(u['rec'], []).append((u, look))
        # each group's guns' state: {gun: frames} (the pieces' own from their types)
        state = {}
        for u in self.units:
            ty = bd['types'].get(f"{u['type']:02x}", {})
            if ty.get('gun'):
                state.setdefault(u['group'], {})[ty['gun']] = ty.get('every', 0)

        # each record's frame (from the stretch's start: b + 1 frames a position, 02 changing it)
        frames, delay = [0], bd.get('delay0', 4)
        for i in range(1, len(self.recs)):
            if self.recs[i - 1][0] == 2 and self.recs[i - 1][2] != 0xff:
                delay = self.recs[i - 1][2] + 1
            frames.append(frames[-1] + (self.pos[i] - self.pos[i - 1]) * delay)
        self.frames = frames

        def clock_of(f, fr=frames, tt=t):
            # (a frame's clock: as its records', between them in proportion)
            for i in range(len(fr) - 1):
                if fr[i] <= f < fr[i + 1]:
                    return tt[i] + (f - fr[i]) * (tt[i + 1] - tt[i]) / (fr[i + 1] - fr[i])
            return tt[-1] + (f - fr[-1]) * S.FRAME
        # the groups whose speeds the GBC's way is worked out for (gbc_speeds): every speed change an event 19 at its
        # time (the PC's steps are half a GBC speed unit, at whole ticks: a zig-zag's speeds came out off); not one
        # steered towards the ship
        exact, start_state, carry = set(), {}, set()
        for g in self.groups:
            ps = [i for i in self.pieces if self.recs[i][4] == g]
            ty = bd['types'].get(f"{self.recs[ps[0]][1]:02x}", {}) if ps else {}
            vx, vy = ty.get('vx', 0), ty.get('vy', 0)
            if not ps or 0x63 in (vx, vy):
                continue
            first = (s8(vx), s8(vy), 0, 0, 0, 0, 0, 0)
            res, end_st = gbc_speeds(self.recs, frames, ps[0], j, g, first)
            if res is None:
                continue
            # (not one whose speed still steps at the loop's end: the steps go on through the loops, which the
            # events of a pass can't follow; the PC's own steps do it, 20 and 27. But when the loop runs again from
            # before its spawn, over the stopped map (JUNGLE II's: the whole level), the copy carries it on from
            # there, the replayed records steering it as the GBC's do (the boss flies off and the level ends);
            # the PC's steps, without the GBC's bounds, took it off the screen in a few seconds)
            if end_st[2] or end_st[3]:
                if not (stop is not None and k < stop and ps[0] >= k):
                    continue
                carry.add(g)
            exact.add(g)
            start_state[g] = (ps[0], res, end_st, first)
        self.exact = exact
        self.exact_speeds, self.exact_frames = {}, {}

        def fire(time, g):
            s = slots.get(g, [])
            st = state.get(g, {})
            freq = [ticks(st[n]) if st.get(n) else 0 for n in s] + [0] * (3 - len(s))
            n = self.launches.get(g)
            launch = ticks(st[n]) if n and st.get(n) else 0
            return S.ev(time, 31, freq[0], freq[1], freq[2], min(127, launch), 0, self.link[g])

        def one(i, time, replay=False):
            r = self.recs[i]
            cmd, a, b, c, g = r
            if i in piece_of:
                return self.spawn(time, piece_of[i], slots)
            if cmd == 2 and c:
                tr.speed = 0
                return [S.ev(time, 2, 0, 0, 0), S.ev(time, 53, 0), S.ev(time, 19, -99, -99, 99, 0, -99)]
            if cmd == 2 and replay:
                return []  # (the map stays stopped when the GBC's moves again in its loop)
            if g in self.exact and cmd in (0x13, 0x14, 0x15, 0x16):
                return []  # (its speeds: gbc_speeds)
            if g in self.groups:
                if cmd == 0x0e:
                    st = state.setdefault(g, {})
                    if a != 0xff:
                        st.clear()
                        st[a] = b
                    elif c in st:
                        st[c] = b
                    return [fire(time, g)]
                if cmd == 0x1d:
                    st = state.setdefault(g, {})
                    for n in st:
                        st[n] = c
                    evs = [] if g in self.exact else tr.one([0x13, a, b, 0, g], time)
                    return evs + [fire(time, g)]
                if cmd == 0x0a:
                    return [S.ev(time, 25, min(255, a), 0, 0, 0, 0, self.link[g])]
            return tr.one(r, time)

        def run(lo, hi, at, replay=False):
            """Records lo..hi-1 at at(i) (a skip on easier difficulties as the main script's)."""
            evs, i = [], lo
            while i < hi:
                r = self.recs[i]
                if r[0] == 0 and r[1]:
                    sub = []
                    for q in range(i + 1, min(hi, i + 1 + r[2])):
                        sub += one(q, at(q), replay)
                    evs += [S.ev(at(i), 66, r[1], len(sub))] + sub if sub else []
                    i += 1 + r[2]
                    continue
                evs += one(i, at(i), replay)
                i += 1
            return evs

        self.t0 = t[0]
        out = run(0, j, lambda i: t[i])
        # the loop: back to its first record (a copy of it timed as the stopped map's when it starts before)
        t_j = t[j] if j < len(t) else t[-1] + 1
        cut = None
        if stop is not None and k < stop:
            p_k = target
            base = t_j + 2
            copy = run(k, j, lambda i: base + round((self.pos[i] - p_k) * rate), replay=True)
            t_end_loop = base + max(1, round((self.pos[j] - p_k) * rate))
            loop_from = base
            self.notes.append("its loop starts before the map stops: run again over the stopped map")
            # (groups carried on through the replay fly off in it: where the GBC's flight then ended, the group its
            # end waits for gone from the screen, the level ends, the replay cut there (JUNGLE II: 71 frames after
            # going back). Not a flight that ended otherwise: its ship rammed)
            fl = bd.get('flight') or {}
            if carry and fl.get('ended') and fl.get('loops') and fl['ended'] > fl['loops'][-1] and fl.get('track'):
                last = fl['track'][-1][2].get(str(g_end))
                if last is None or last[1] >= 160:  # (below the screen's 144 rows, or above it)
                    cut = base + round((fl['ended'] - fl['loops'][-1]) * S.FRAME) + CUT_GAP
                    copy = [e for e in copy if e['t'] < cut]
                    t_end_loop = cut
                    self.notes.append(f"its boss flies off in the replay: the level ends {cut - base} ticks into it")
            out += [S.ev(t_j, 54, base)] + copy
        else:
            # (the clock at the target: from the last record before it, at the rate then; a stopped map's rate can
            # change after the stop: DELIANI's went from 3 frames a position to 2, and its loop, started from the stop
            # at the last rate, ran its speed's record again each time round: it drifted off the screen)
            if stop is not None and target >= self.pos[stop]:
                q = max(i for i in range(stop, len(self.recs)) if self.pos[i] <= target)
                t_k = round(self.t_exact[q] + (target - self.pos[q]) * self.rates[q])
            else:
                t_k = t[k] if k < j else t_j
            loop_from = min(t_k, t_j - 1)
            t_end_loop = t_j
        if cut is None:
            out.append(S.ev(t_end_loop, 54, loop_from))
        self.segments = dict(first_end=t_j if (stop is not None and k < stop) else loop_from, loop=(loop_from, t_end_loop),
                             copy=stop is not None and k < stop, target=target)
        # the exact groups' speeds: the first pass, and the copy of the loop (from where the first leaves them)
        for g in sorted(self.exact):
            i0, res, end_st, first = start_state[g]
            # (a speed's clock rounded onto its pass's jump back would come after it: the next pass started at the
            # old speed, ICE EXIT's 8 px a tick to the right each time round; the tick before)
            end1 = t_j if self.segments['copy'] else t_end_loop
            speeds = [(min(round(clock_of(f)), end1 - 1), vx, vy) for f, vx, vy in res]
            exact_f = list(res)
            if self.segments['copy']:
                fr2 = [0] * len(self.recs)
                for i in range(k, len(self.recs)):
                    fr2[i] = round((self.pos[i] - target) * (rate / S.FRAME))
                t2 = [base + round((self.pos[i] - target) * rate) for i in range(len(self.recs))]
                # (from where the first pass leaves it; when its spawn comes again in the loop, from there anew, unless
                # it is carried on through the replay: see carry above)
                lo2, st2 = (i0, first) if i0 >= k and g not in carry else (k, end_st)
                res2, _ = gbc_speeds(self.recs, fr2, lo2, j, g, st2)
                for f, vx, vy in res2 or []:
                    tm = round(clock_of(f, fr2[k:j + 1], t2[k:j + 1]))
                    if cut is None or tm < cut:
                        speeds.append((min(tm, t_end_loop - 1), vx, vy))
                exact_f = list(res2 or [])
                self.loop_frames = (fr2[k], fr2[j])
            else:
                self.loop_frames = (frames[k], frames[j])
            self.exact_frames[g] = exact_f
            last = {}
            for tm, vx, vy in speeds:
                last[tm] = (vx, vy)
            # (the PC's speeds are bytes too: at most 127, a GBC speed of 63; faster ones leave the screen in a tick)
            out += [S.ev(tm, 19, max(-127, min(127, S.SPEED_UNIT * vx)), max(-127, min(127, S.SPEED_UNIT * vy)), 0, 0,
                         0, self.link[g]) for tm, (vx, vy) in sorted(last.items()) if cut is None or tm < cut]
            self.exact_speeds[g] = speeds
        # the end: checks every CHECK ticks from its 05 on, in the loop too
        if end is not None:
            g = self.recs[end][4]
            links = [self.link[g]] if g in self.link else sorted(self.link.values())[:3]
            if g in (0, 255):
                self.notes.append("its end waits for every enemy to be gone: here for the boss's links")
            t_end = cut if cut is not None else max(e['t'] for e in out) + END_GAP
            # (the two runs a CHECK apart where they overlap: one check in each CHECK ticks)
            checks = []
            for c in sorted(set(range(t[end], t_end_loop, CHECK)) | set(range(loop_from, t_end_loop, CHECK))):
                if not checks or c - checks[-1] >= CHECK:
                    checks.append(c)
            for c in checks:
                out.append(S.ev(c, 70, t_end, links[0], links[1] if len(links) > 1 else 0, 0, 0,
                                links[2] if len(links) > 2 else 0))
            out += [S.ev(t_end, 41, 0), S.ev(t_end, 11, 0)]
        out.sort(key=lambda e: (e['t'], e['type'] == 54))  # (a jump after what else comes at its tick)
        out += self.corrections(out)
        for g, inv in self.inv_link.items():
            link = self.link[g]
            out += [dict(e, d4=inv) for e in out if e['type'] in (19, 20, 25, 27, 31, 55) and e['d4'] == link and
                    not (e['type'] == 19 and e['d3'])]
        out.sort(key=lambda e: (e['t'], e['type'] == 54))  # (a jump after what else comes at its tick)
        self.events = out
        return out

    def corrections(self, events):
        """The PC's whole ticks (speed changes at whole ticks) and the GBC's half pixels (odd speeds move a pixel on
        alternate frames) part a group's way a little from the GBC's, and a loop repeats that each time round
        (TYRIAN's boss rose 18 px a loop, out of the screen): each group whose speeds are the GBC's (gbc_speeds) is
        made to go the GBC's way (boss_rom.py's flight, frame by frame: from its spawn to the first loop's end, and
        each loop) over its first pass and over a loop (simulate(): as the engine moves enemies), the difference
        made up while it stands (a nudge of 1-4 px a tick; the loop's inside the loop, the first pass's before it).
        Groups steered towards the ship, or whose steps go on through the loops, are left as they are."""
        fl = self.bd.get('flight') or {}
        ways = fl.get('ways', {})
        seg = self.segments
        lo, hi = seg['loop']
        out = []
        for g in sorted(self.exact):
            w = ways.get(str(g))
            if not w:
                continue
            link = self.link[g]
            spawns = [e for e in events if e.get('ep') == 'boss' and e['d4'] == link]
            ref = self.records[spawns[0]['d1'] - 1]
            start = dict(x=0.0, y=0.0, exc=ref.get('move', [0, 0])[0], eyc=ref.get('move', [0, 0])[1], excc=0, eycc=0,
                         wx=0, wy=0, exrev=100, eyrev=100, fy=spawns[0]['d6'], back=self.speed0, forced=False,
                         here=False)
            t_j = seg['first_end'] if seg['copy'] else hi
            # a loop: the GBC's loops after the first (their mean)
            if len(w) > 1:
                want = (1.5 * sum(v[0] for v in w[1:]) / (len(w) - 1), 1.5 * sum(v[1] for v in w[1:]) / (len(w) - 1))
                _, st = simulate(events + out, link, self.t0, t_j, start)
                traj, _ = simulate(events + out, link, lo, hi, st)
                out += nudge(traj, want, link)
            # the first pass: from its spawn to the first loop's end
            want = (1.5 * w[0][0], 1.5 * w[0][1])
            traj, _ = simulate(events + out, link, self.t0, t_j, start)
            before = traj if seg['copy'] else [p for p in traj if p[0] < lo]
            if traj and before:
                # (where the whole pass ends; the nudge in its part that doesn't come again)
                shift = (traj[-1][1] - before[-1][1], traj[-1][2] - before[-1][2])
                out += nudge(before, (want[0] - shift[0], want[1] - shift[1]), link)
        return out

    def spawn(self, time, pieces, slots):
        """A spawn record's pieces: one PC enemy each (ep 'boss': self.records[d1 - 1]; the same piece the same record
        when its spawn runs again)."""
        evs = []
        for u, look in pieces:
            key = (u['rec'], u['type'], u['x'], u['y'])
            if key not in self.made:
                self.records.append(self.record(u, look, slots))
                self.made[key] = len(self.records)
            n = self.made[key]
            x = S.SCALE * u['x'] - 12
            y = max(-128, min(127, round(S.SCALE * u['y'])))
            link = self.link[u['group']]
            if self.records[n - 1]['armor'] == 255 and u['group'] in self.inv_link:
                link = self.inv_link[u['group']]
            # (in the sky, the PC parts that stand on the ground in their originals too; drifting with the map as the
            # GBC's do: those its command 03 or an even block command makes, $2ca8's flag, $20b8; not 21-24)
            cmd = self.recs[u['rec']][0]
            with_map = cmd == 3 or (cmd >= 0x28 and cmd % 2 == 0)  # (not 21-24: script.py)
            ty = self.bd['types'].get(f"{u['type']:02x}", {})
            self.tr.steered[link] = (ty.get('vx') == 0x63, ty.get('vy') == 0x63)  # (its record steers it: a 13 stops it)
            evs.append(S.ev(time, S.SKY, n, round(x), 0, y, self.tr.speed if with_map else 0, link, ep='boss'))
        return evs

    def record(self, u, look, slots):
        """A piece's PC enemy: its looks (base: [episode, enemy] whose record it copies), armour, guns (keys of
        self.guns, by slot), how often they fire (ticks), what it launches."""
        ty = self.bd['types'].get(f"{u['type']:02x}", {})
        g = u['group']
        guns = slots.get(g, [])
        own = ty.get('gun')
        every = ty.get('every', 0)
        tur, freq = [], []
        for n in guns:
            if n == own or self.gun_given(g, n):
                key = f"L{self.level:02d}:{n}"
                self.guns.setdefault(key, gun_weapon(self.bd['guns'][str(n)]))
                tur.append(key)
            else:
                tur.append(None)
            freq.append(ticks(every) if n == own and every else 0)
        tur += [None] * (3 - len(tur))
        freq += [0] * (3 - len(freq))
        launch, lf = None, 0
        n = self.launches.get(g)
        if n and (n == own or self.gun_given(g, n)):
            launch = self.launchable.get(n - 20)
            active = (n == own and every) or any(r[0] == 0x0e and r[4] == g and n in (r[1], r[3]) and r[2]
                                                 for r in self.recs)
            if launch is None and active:
                self.notes.append(f"group {g} launches GBC type {n - 20:02x}, which has no PC enemy: left out")
            elif n == own and every:
                lf = ticks(every)
        hp = ty.get('hp', 1)
        armor = 255 if hp == 255 else max(1, min(254, hp))
        if hp > 254 and hp != 255:
            self.notes.append(f"type {u['type']:02x}: {hp} hit points, 254 here")
        if look:
            base, layer = [self.src_ep, look[0]], look[1]
        else:
            pc = self.tr.types.get(u['type'])
            base, layer = ([pc[0], pc[1]] if pc and pc[2] == 1 else None), S.SKY
        # (its start speed, the type's (half pixels a frame: SPEED_UNIT); 99 towards the ship)
        vx, vy = ty.get('vx', 0), ty.get('vy', 0)
        move = [0 if v == 0x63 else S.SPEED_UNIT * s8(v) for v in (vx, vy)]
        accel = [HOMING if v == 0x63 else 0 for v in (vx, vy)]
        return dict(base=base, layer=layer, armor=armor, tur=tur, freq=freq, move=move, accel=accel,
                    launch=list(launch) if launch else None, launchfreq=lf, gbc_type=u['type'], group=g)

    def gun_given(self, g, n):
        return any(r[0] == 0x0e and r[4] == g and r[1] == n for r in self.recs)
