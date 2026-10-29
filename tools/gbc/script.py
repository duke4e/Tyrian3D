"""A GBC level's enemy script as PC level events (episode 7; tools/content/EVENTS.md).

The GBC game's script is a port of the PC event system with its own numbers: a list of trigger
positions (scrolled pixels) and records of five bytes (command, a, b, c, group). Its enemies are the
PC enemies (enemies.py found which); here each record becomes the PC events that do the same:

    03/04 a x y g      enemy of type a at (x, y) in group g     -> 15 (sky) / 6 (ground), link of g
    21-24              the same on Hard / Normal and up          -> 66 (skip on easier) + the enemy
    28+                a block: the pieces of one big enemy (columns, rows by the command's bits, 16 px
                       apart): one PC enemy, centred on them (a composite's parts after an event 201: one
                       enemy, which dies alone; the GBC's all do, the PC's die with their link)
    13/1d vx vy . g    group's speed (99: towards the ship)     -> 19 (+ 55)
    14 cx cy rx g      group zig-zag: every |c| frames the speed  -> 20 (+ 27 for the turn speed)
                       steps by 1, turning at rx
    15 rx ry . g       turn speeds                               -> 27
    16 cx cy . g       acceleration (the same steps, no turning)  -> 20
    0b n . . g         group g becomes group n                   -> 39
    02 . s .           scroll: a pixel every s+1 frames          -> 2
    00 d n             skip the next n records below difficulty d -> 66
    0e a b c g         group's gun a every b frames (a ff: gun c's -> 31 (d6 1: its launches as they are)
                       every b; b 0: none)
    (each enemy made)  its type's hit points and gun's pace   -> 203 before it (tyrian2.c gbc_fight; the
                       (the type table's bytes 1, 5, 6)          PC enemy drawn for it is often far tougher,
                                                                 or fires where it never does)

Scale: a GBC pixel is 1.5 PC pixels; a trigger at scrolled position p is the PC clock 1.5 p; with the
GBC scroll of a pixel every 4 frames as the PC's 1 px a tick, a GBC frame is 0.375 ticks, so a speed
unit (half a pixel a frame) is 2 PC px a tick.

How a GBC enemy moves (the spawn $2ca8, the mover $20b8): from its type's start speed (the type table's
bytes 3 and 4, half pixels a frame; 99: steered towards the ship), and with the map (a pixel each time it
scrolls) only when command 03 or an even block command made it (the flag $2ca8 sets: not 21-24, the
Hard and Normal ones); 13 and the rest
change its speed, not that. Here: its start speed its own (y: the spawn event's own speed, which makes up
for the PC enemy's; x, the PC enemy's steps and steering undone or the steering towards the ship: by its
link, as it is made); the map's drift, in the PC's sky slots (their height in the 3D view), as fixedmovey,
for those only; the PC enemies that stand on the ground in their originals go to the ground slots, which
scroll by themselves: those the GBC doesn't carry get the scroll taken off their speeds.
"""
SPEED_UNIT = 2          # PC px per tick for a GBC speed unit
FRAME = 0.375           # PC ticks per GBC frame
SCALE = 1.5
SKY, GROUND = 15, 6
LINKS = range(1, 31)    # links for the GBC groups (above 40, links of a block of 20 die together)
KEEP = 0x63
OBJECT = 201            # (Tyrian3D's event: the next d1 events make one enemy)
FIGHT = 203             # (Tyrian3D's event: the next enemy's hit points and fire, the GBC's)
HOMING = 97             # 55's xaccel / yaccel: towards the ship (13 with 99: a step every 10 frames)


def s8(v):
    return v - 256 if v > 127 else v


def ticks(frames):
    return max(1, round(frames * FRAME))


def ev(t, type_, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0, ep=None):
    e = dict(t=int(t), type=type_, d1=int(d1), d2=int(d2), d3=int(d3), d5=int(d5), d6=int(d6), d4=int(d4))
    if ep is not None:
        e['ep'] = ep
    return e


class Links:
    """GBC groups -> PC links 1-30, a link given again once its group has had no record for a while."""

    def __init__(self):
        self.of, self.last = {}, {}

    def get(self, group, t):
        if group == 0:
            return 0
        if group in self.of:
            self.last[self.of[group]] = t
            return self.of[group]
        free = [l for l in LINKS if self.last.get(l, -10 ** 9) < t - 900]
        link = free[0] if free else min(LINKS, key=lambda l: self.last.get(l, -10 ** 9))
        for g, l in list(self.of.items()):
            if l == link:
                del self.of[g]
        self.of[group], self.last[link] = link, t
        return link

    def known(self, group):
        return self.of.get(group)


class Translator:
    """The records' translation, record by record (translate(); the boss's stretch, boss.py): its links and the
    scroll speed new enemies drift with carried from one to the next. Arguments as translate()'s."""

    def __init__(self, types, enemies_of, ground_of, start_speed=1, sizes=None, links=None, starts=None, stats=None):
        self.types, self.enemies_of, self.ground_of = types, enemies_of, ground_of
        self.sizes = sizes or {}
        self.links = links or Links()
        self.speed = start_speed
        self.starts = starts or {}  # GBC type -> its start speed, the type table's bytes (vx, vy)
        self.stats = stats or {}    # GBC type -> (hit points, gun, every how many frames it fires): bytes 1, 5, 6
        self.guns = {}              # link -> the guns of the types made on it
        self.pace = 1               # the level's enemies fire this many times less often (episode.py FIRE_PACE)
        self.uncarried = set()      # links of ground slots' enemies the GBC map doesn't carry (their 19s less the scroll)
        self.steered = {}           # link -> (x, y) steered towards the ship
        self.carried = {}           # link -> when the sky enemies the GBC map carries were last made on it

    def spawn_events(self, t, rec, carried=None):
        types, sizes, links, speed = self.types, self.sizes, self.links, self.speed
        enemies_of, ground_of = self.enemies_of, self.ground_of
        cmd, a, b, c, g = rec
        pc = types.get(a)
        if pc is None:
            return []
        ep, n, parts = pc
        # (with the map: made by 03 or an even block command, not 21-24 ($26f3 works the flag out from the command
        # 4 - cmd, 1 only for 03); its start speed, a block's its first piece's)
        if carried is None:
            carried = cmd == 3 or (cmd >= 0x28 and cmd % 2 == 0)
        vx, vy = self.starts.get(a, (0, 0))
        sx = 0 if vx == KEEP else SPEED_UNIT * s8(vx)
        sy = 0 if vy == KEEP else SPEED_UNIT * s8(vy)
        drift = speed if carried else 0
        k = cmd - 0x28
        block = (((k >> 1) & 3) + 1, (k >> 3) + 1) if cmd >= 0x28 else (1, 1)
        w, h = sizes.get(a, (16, 16))
        # a block is the pieces of one big GBC enemy (two columns one robot, a bunker, an airship of
        # eight, three rows one stalactite; seen in the GBC game, never a formation): one PC enemy for
        # it, centred on its pieces
        whole = True
        cols = rows = 1
        link = links.get(g, t)
        ground = ground_of(pc)
        datas = [enemies_of(ep).get(m, {}) for m in ([p[0] for p in parts] if isinstance(parts, tuple) else [n])]
        # (its hit points, a block's pieces' together, and how often it fires: the GBC's; tyrian2.c gbc_fight)
        fight = []
        if a in self.stats:
            hp, gun, every = self.stats[a]
            hp *= block[0] * block[1]
            fight = [ev(t, FIGHT, hp if 0 < hp < 255 else 0, 0, min(127, ticks(every * self.pace)) if gun and every else 0)]
            if link:
                self.guns.setdefault(link, set()).add(gun)

        def start_y(m):
            # (the spawn event's own speed: the GBC start speed's y for the PC enemy's; on the ground, which the map
            # carries, less the scroll for one the GBC's doesn't)
            own = enemies_of(ep).get(m, {}).get('ymove', 0)
            return max(-128, min(127, sy - own - (0 if not ground or carried else speed)))
        evs = fight
        for j in range(rows):
            for i in range(cols):
                x = SCALE * (b + 16 * i) - 12
                y = max(-128, min(127, round(SCALE * (s8(c) - 16 * j))))
                top = round(SCALE * (s8(c) - 16 * (block[1] - 1)))  # (the block's top row: its rows go up)
                if parts == 4:
                    # a 4-part enemy (event 12: the parts d1..d1+3, the layer in d6, part 0 the lower
                    # left one) with its top left corner where the GBC one's is; in the sky it gets
                    # the scroll by its link (event 12 leaves fixedmovey 0)
                    evs.append(ev(t, 12, n, round(x) + (27 if ground else 0), start_y(n), min(127, y + 28), 0 if ground else 2, link, ep=ep))
                    if not ground and link and drift:
                        evs.append(ev(t, 19, -99, -99, 0, 0, drift, link))
                elif isinstance(parts, tuple):
                    # a composite: its parts with their offsets from its top left, in one link, centred
                    # on the GBC enemy (its sprite, or the block's pieces)
                    bw, bh = max(w, 16 * block[0]), max(h, 16 * block[1])
                    cx = (SCALE * bw - (max(p[1] for p in parts) + 24)) / 2
                    cy = round((SCALE * bh - (max(p[2] for p in parts) + 28)) / 2)
                    # (one enemy: the engine lets the next events' pieces die together, and alone of the rest of
                    # their link, the GBC group, whose enemies die alone: tyrian2.c gbc_takes_along)
                    evs.append(ev(t, OBJECT, len(parts)))
                    for m, dx, dy in parts:
                        dx += cx
                        yy = max(-128, min(127, top + cy + dy))
                        if ground:
                            evs.append(ev(t, GROUND, m, round(x + dx) + 27, start_y(m), yy, 0, link, ep=ep))
                        else:
                            evs.append(ev(t, SKY, m, round(x + dx), start_y(m), yy, drift, link, ep=ep))
                else:
                    if whole and block != (1, 1):  # (one PC enemy for a block's pieces: centred on them)
                        x += (SCALE * 16 * block[0] - 24) / 2
                        y = max(-128, min(127, top + round((SCALE * 16 * block[1] - 28) / 2)))
                    if ground:
                        evs.append(ev(t, GROUND, n, round(x) + 27, start_y(n), y, 0, link, ep=ep))
                    else:
                        evs.append(ev(t, SKY, n, round(x), start_y(n), y, drift, link, ep=ep))
        # the rest of its start speed by its link, as it is made (alone, with none: the PC enemy's x stays): x, the PC
        # enemy's steps undone, steering towards the ship for 99 (or the PC's undone)
        if link:
            if ground and not carried:
                self.uncarried.add(link)
            else:
                self.uncarried.discard(link)
            if carried and not ground:
                self.carried[link] = t
            else:
                self.carried.pop(link, None)
            # (and when the PC enemy steps sideways by itself: made ahead of its time on a playfield reaching above the
            # screen, tyrian2.c prespawn_events, it has stepped by then)
            if sx or any(d.get('xmove') or d.get('xcaccel') for d in datas):
                evs.append(ev(t, 19, sx, -99, 0, 0, 0, link))
            if any(d.get('xcaccel') or d.get('ycaccel') for d in datas):
                evs.append(ev(t, 20, 0, 0, 0, 0, 0, link))
            steer = (vx == KEEP, vy == KEEP)
            if any(steer) or any(self.steered.get(link, ())) or any(d.get('xaccel') or d.get('yaccel') for d in datas):
                evs.append(ev(t, 55, HOMING if steer[0] else 0, HOMING if steer[1] else 0, 0, 0, 0, link))
            self.steered[link] = steer
        return evs

    def one(self, rec, t):
        """One record's events at clock t."""
        links = self.links
        cmd, a, b, c, g = rec
        if cmd in (3, 4) or cmd >= 0x28:
            return self.spawn_events(t, rec)
        if cmd in (0x21, 0x22, 0x23, 0x24):
            evs = self.spawn_events(t, [cmd - (0x1e if cmd < 0x23 else 0x20), a, b, c, g], carried=False)
            return [ev(t, 66, 2 if cmd < 0x23 else 1, len(evs))] + evs if evs else []
        link = links.known(g) if g else None
        if cmd in (0x13, 0x1d):
            if not link:
                return []
            # (99: that way steered towards the ship from its speed then; the other way's steering off, $289c)
            less = self.speed if link in self.uncarried else 0
            evs = [ev(t, 19, -99 if a == KEEP else SPEED_UNIT * s8(a), -99 if b == KEEP else SPEED_UNIT * s8(b) - less, 0, 0, 0, link)]
            steer = (a == KEEP, b == KEEP)
            if any(steer) or any(self.steered.get(link, ())):
                evs.append(ev(t, 55, HOMING if steer[0] else 0, HOMING if steer[1] else 0, 0, 0, 0, link))
            self.steered[link] = steer
            return evs
        if cmd in (0x14, 0x16):
            if not link:
                return []

            def cc(v):
                v = s8(v)
                return 0 if v == 0 else (1 if v > 0 else -1) * max(1, round(abs(v) * FRAME / SPEED_UNIT))
            evs = [ev(t, 20, cc(a), cc(b), 0, 0, 0, link)]
            if c and cmd == 0x14:
                evs.append(ev(t, 27, SPEED_UNIT * s8(c), -99, 0, 0, 0, link))
            return evs
        if cmd == 0x15:
            if not link or not (a or b):
                return []
            return [ev(t, 27, SPEED_UNIT * s8(a) if a else -99, SPEED_UNIT * s8(b) if b else -99, 0, 0, 0, link)]
        if cmd == 0x0e:
            # (a group's gun: a, or with a ff the group's gun c, every b frames; its PC guns at that pace)
            if not link or (a == 0xff and c not in self.guns.get(link, ())):
                return []
            if a != 0xff:
                self.guns[link] = {a}
            f = min(255, ticks(b * self.pace)) if b and (c if a == 0xff else a) else 0
            return [ev(t, 31, f, f, f, 0, 1, link)]
        if cmd == 0x0b:
            if not link:
                return []
            new = links.get(a, t)
            for known in (self.steered, self.carried, self.guns):
                if link in known:
                    known[new] = known[link]
            if link in self.uncarried:
                self.uncarried.add(new)
            return [ev(t, 39, link, new)]
        if cmd == 0x02:
            s = 0 if b == 0xff else max(1, round(4 / (b + 1)))
            # (the sky enemies the map carries at its new speed: those of links made so lately that they may still fly)
            drift = [ev(t, 19, -99, -99, 0, 0, s or -99, l) for l, when in sorted(self.carried.items())
                     if s != self.speed and t - when < 900]
            self.speed = s
            # (backgrounds 2 and 3 are empty: at layer 1's speed they last its length; at the usual
            # 2x and 3x they run out of map at clock 8274 and 5516, which the GBC levels pass)
            return [ev(t, 2, s, s, s)] + drift
        return []


def translate(records, positions, types, enemies_of, ground_of, start_speed=1, clock=None, sizes=None, translator=None):
    """records: the GBC records (lists of 5 bytes) in order, positions their trigger positions;
    types: GBC type -> (episode, enemy, parts: 1, 4 for a 4-part enemy (event 12) or a composite's
    ((enemy, dx, dy), ...), its parts spawned each at its offset) or None (left out); enemies_of(ep) -> that episode's enemy
    data; ground_of((ep, n)) -> True if the PC enemy stands on the ground; clock(position) -> the PC
    clock (default 1.5 x the position); sizes: GBC type -> (width, height) of its sprite in GBC pixels,
    a composite is centred on it (on the block's pieces for a block); translator: a Translator to go on with (its
    links and speed; else a new one). Returns the events."""
    clock = clock or (lambda p: round(SCALE * p))
    tr = translator or Translator(types, enemies_of, ground_of, start_speed, sizes)
    out = []
    i = 0
    while i < len(records):
        rec = records[i]
        if rec[0] == 0x00:
            n = rec[2]
            t = clock(positions[i])
            sub = []
            for k in range(i + 1, min(len(records), i + 1 + n)):
                sub += tr.one(records[k], clock(positions[k]))
            if sub:
                out += [ev(t, 66, rec[1], len(sub))] + sub
            i += 1 + n
            continue
        out += tr.one(rec, clock(positions[i]))
        i += 1
    return out
