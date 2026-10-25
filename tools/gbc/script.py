"""A GBC level's enemy script as PC level events (episode 7; tools/content/EVENTS.md).

The GBC game's script is a port of the PC event system with its own numbers: a list of trigger
positions (scrolled pixels) and records of five bytes (command, a, b, c, group). Its enemies are the
PC enemies (enemies.py found which); here each record becomes the PC events that do the same:

    03/04 a x y g      enemy of type a at (x, y) in group g     -> 15 (sky) / 6 (ground), link of g
    21-24              the same on Hard / Normal and up          -> 66 (skip on easier) + the enemy
    28+                a block of enemies (columns, rows by the command's bits, 16 px apart; the
                       pieces of one big enemy: one PC enemy of several parts if its type has one)
    13/1d vx vy . g    group's speed (99: keep)                 -> 19
    14 cx cy rx g      group zig-zag: every |c| frames the speed  -> 20 (+ 27 for the turn speed)
                       steps by 1, turning at rx
    15 rx ry . g       turn speeds                               -> 27
    16 cx cy . g       acceleration (the same steps, no turning)  -> 20
    0b n . . g         group g becomes group n                   -> 39
    02 . s .           scroll: a pixel every s+1 frames          -> 2
    00 d n             skip the next n records below difficulty d -> 66

Scale: a GBC pixel is 1.5 PC pixels; a trigger at scrolled position p is the PC clock 1.5 p; with the
GBC scroll of a pixel every 4 frames as the PC's 1 px a tick, a GBC frame is 0.375 ticks, so a speed
unit (half a pixel a frame) is 2 PC px a tick. GBC enemies move with the map: in the PC's sky slots
(their height in the 3D view) they get the scroll as fixedmovey; the PC enemies that stand on the
ground in their originals go to the ground slots, which scroll by themselves.
"""
SPEED_UNIT = 2          # PC px per tick for a GBC speed unit
FRAME = 0.375           # PC ticks per GBC frame
SCALE = 1.5
SKY, GROUND = 15, 6
LINKS = range(1, 31)    # links for the GBC groups (above 40, links of a block of 20 die together)
KEEP = 0x63


def s8(v):
    return v - 256 if v > 127 else v


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


def translate(records, positions, types, enemies_of, ground_of, start_speed=1, clock=None):
    """records: the GBC records (lists of 5 bytes) in order, positions their trigger positions;
    types: GBC type -> (episode, enemy, parts: 1, 4 for a 4-part enemy (event 12) or a composite's
    ((enemy, dx, dy), ...), its parts spawned each at its offset) or None (left out); enemies_of(ep) -> that episode's enemy
    data; ground_of((ep, n)) -> True if the PC enemy stands on the ground; clock(position) -> the PC
    clock (default 1.5 x the position). Returns the events."""
    clock = clock or (lambda p: round(SCALE * p))
    links = Links()
    speed = start_speed
    out = []

    def spawn_events(t, rec):
        cmd, a, b, c, g = rec
        pc = types.get(a)
        if pc is None:
            return []
        ep, n, parts = pc
        if cmd >= 0x28 and parts == 1:
            k = cmd - 0x28
            cols, rows = ((k >> 1) & 3) + 1, (k >> 3) + 1
        else:
            # (a block of pieces is one big GBC enemy, e.g. two columns one robot: the type's PC enemy
            # of several parts was found for the whole of it, so it is made once)
            cols = rows = 1
        link = links.get(g, t)
        ground = ground_of(pc)
        datas = [enemies_of(ep).get(m, {}) for m in ([p[0] for p in parts] if isinstance(parts, tuple) else [n])]
        evs = []
        for j in range(rows):
            for i in range(cols):
                x = SCALE * (b + 16 * i) - 12
                y = max(-128, min(127, round(SCALE * (s8(c) - 16 * j))))
                if parts == 4:
                    # a 4-part enemy (event 12: the parts d1..d1+3, the layer in d6, part 0 the lower
                    # left one) with its top left corner where the GBC one's is; in the sky it gets
                    # the scroll by its link (event 12 leaves fixedmovey 0)
                    evs.append(ev(t, 12, n, round(x) + (27 if ground else 0), 0, min(127, y + 28), 0 if ground else 2, link, ep=ep))
                    if not ground and link:
                        evs.append(ev(t, 19, -99, -99, 0, 0, speed, link))
                elif isinstance(parts, tuple):
                    # a composite: its parts with their offsets from its top left, in one link
                    for m, dx, dy in parts:
                        yy = max(-128, min(127, y + dy))
                        if ground:
                            evs.append(ev(t, GROUND, m, round(x + dx) + 27, 0, yy, 0, link, ep=ep))
                        else:
                            evs.append(ev(t, SKY, m, round(x + dx), 0, yy, speed, link, ep=ep))
                elif ground:
                    evs.append(ev(t, GROUND, n, round(x) + 27, 0, y, 0, link, ep=ep))
                else:
                    evs.append(ev(t, SKY, n, round(x), 0, y, speed, link, ep=ep))
        # GBC enemies start still: the PC enemy's own moves undone (by its link; alone: none to undo)
        if link and not ground:
            if any(d.get('xmove') or d.get('ymove') for d in datas):
                evs.append(ev(t, 19, 0, 0, 0, 0, 0, link))
            if any(d.get('xcaccel') or d.get('ycaccel') for d in datas):
                evs.append(ev(t, 20, 0, 0, 0, 0, 0, link))
            if any(d.get('xaccel') or d.get('yaccel') for d in datas):
                evs.append(ev(t, 55, 0, 0, 0, 0, 0, link))
        return evs

    def one(i):
        nonlocal speed
        rec = records[i]
        t = clock(positions[i])
        cmd, a, b, c, g = rec
        if cmd in (3, 4) or cmd >= 0x28:
            return spawn_events(t, rec)
        if cmd in (0x21, 0x22, 0x23, 0x24):
            evs = spawn_events(t, [cmd - (0x1e if cmd < 0x23 else 0x20), a, b, c, g])
            return [ev(t, 66, 2 if cmd < 0x23 else 1, len(evs))] + evs if evs else []
        link = links.known(g) if g else None
        if cmd in (0x13, 0x1d):
            if not link:
                return []
            return [ev(t, 19, -99 if a == KEEP else SPEED_UNIT * s8(a), -99 if b == KEEP else SPEED_UNIT * s8(b), 0, 0, 0, link)]
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
        if cmd == 0x0b:
            if not link:
                return []
            return [ev(t, 39, link, links.get(a, t))]
        if cmd == 0x02:
            s = 0 if b == 0xff else max(1, round(4 / (b + 1)))
            speed = s
            # (backgrounds 2 and 3 are empty: at layer 1's speed they last its length; at the usual
            # 2x and 3x they run out of map at clock 8274 and 5516, which the GBC levels pass)
            return [ev(t, 2, s, s, s)]
        return []

    i = 0
    while i < len(records):
        rec = records[i]
        if rec[0] == 0x00:
            n = rec[2]
            t = clock(positions[i])
            sub = []
            for k in range(i + 1, min(len(records), i + 1 + n)):
                sub += one(k)
            if sub:
                out += [ev(t, 66, rec[1], len(sub))] + sub
            i += 1 + n
            continue
        out += one(i)
        i += 1
    return out
