"""Composing an episode 6 level's events: waves of the original levels placed anew along a
difficulty curve, stationary ground enemies on the tiles of the new map that suit them, the boss
block at the end (tools/content/EVENTS.md has the rules this follows).

Events are dicts as tyrevents reads them (t, type, d1..d6, d4); an event naming an enemy (its d1)
carries the episode it is from ("ep"), so the build can bring it into episode 6's item data.
"""
import random
from collections import Counter, defaultdict

import waves as W

LAYER1_ROWS = 300
CLOCK_END = 8148          # layer 1 runs out here (EVENTS.md 3)
ENEMY_D1 = W.SPAWNS | {33, 45, 59, 68}  # events whose d1 is an enemy
COURIER_LINK = 40         # the secret couriers' (waves get links 1-39)
DATA_CUBE = 512           # the item data's data cube (value 1; sheet 21, always there)
WARP_ORB = 593            # a warp orb (sheet 20); the build gives each secret level its own
WARP_SHEET = 20


def event(t, type_, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0, ep=None):
    e = dict(t=int(t), type=type_, d1=d1, d2=d2, d3=d3, d5=d5, d6=d6, d4=d4)
    if ep is not None:
        e["ep"] = ep
    return e


def row_at(t):
    """The layer 1 row at the top of the screen at clock t."""
    return 292 - (t + 27) // 28


def ground_time(row):
    """The clock at which a ground enemy spawned at the top edge sits on this row (the originals'
    convention, EVENTS.md 3)."""
    return 28 * (291 - row) - 8


class Links:
    """Link numbers for placed waves: a wave's links become free ones (the originals reuse 1-40
    for ordinary groups; above 40, links of a block of 20 die together, so those keep their place
    in a block)."""

    def __init__(self):
        self.busy = {}  # link -> clock until which it is in use

    def remap(self, links, start, end):
        mapping = {}
        for link in sorted(links):
            if link <= 40:
                for new in range(1, COURIER_LINK):
                    if self.busy.get(new, -1) < start and new not in mapping.values():
                        mapping[link] = new
                        break
            else:
                new = link
                while self.busy.get(new, -1) >= start and new + 20 < 254:
                    new += 20
                mapping[link] = new
        for new in mapping.values():
            self.busy[new] = end
        return mapping


def place(template, start, links, ep):
    """A wave or boss template's events at a new start, with new link numbers."""
    mapping = links.remap(set(template["links"]) | {e["d4"] for e in template["events"] if e["d4"]},
                          start, start + template.get("length", 0) + 600)
    out = []
    for e in template["events"]:
        e = dict(e)
        e["t"] = start + e["t"]
        jump = e.pop("jump", None)
        if jump == "exit":
            e["d1"] = start + template["loop"][1] + 2
        elif jump == "loop":
            e["d1"] = start + template["loop"][0]
        if e["d4"] in mapping and (e["type"] in W.SPAWNS or W.by_link(e) is not None):
            e["d4"] = mapping[e["d4"]]
        if e["type"] == 39:
            e["d1"] = mapping.get(e["d1"], e["d1"])
            e["d2"] = mapping.get(e["d2"], e["d2"])
        if e["type"] == 79:
            e["d1"] = mapping.get(e["d1"], e["d1"])
            e["d2"] = mapping.get(e["d2"], e["d2"])
        if e["type"] == 70 and e["d2"]:
            e["d2"] = mapping.get(e["d2"], e["d2"])
            e["d4"] = mapping.get(e["d4"], e["d4"])
        if e["type"] in ENEMY_D1:
            e["ep"] = ep
            if e["type"] in (33, 45) and e["d1"] in (512, 513):
                # An original's data cube: episode 6's cubes are its own (story.py).
                e["d1"], e["ep"] = 396, 5
        out.append(e)
    return out


def expand(level):
    """A level's events: its own (ground enemies, settings) and its placements (waves and the boss
    of the original levels, by reference: they are the game's data, read at build time), with new
    link numbers, in time order."""
    links = Links()
    sources = {}
    placed = []
    for p in sorted(level["placements"], key=lambda p: p["start"]):
        key = (p["episode"], p["name"])
        if key not in sources:
            sources[key] = W.Source(*key)
        source = sources[key]
        if p["kind"] == "boss":
            template = dict(source.boss(), length=CLOCK_END - p["start"])
        elif p["kind"] == "midboss":
            template = midboss_template(source, p)
        else:
            template = source.waves(ground=p.get("ground", False))[p["index"]]
        events = place(template, p["start"], links, source.episode)
        if p.get("drop"):
            events = with_drops(events, p["drop"])
        placed += events
    head = [e for e in level["events"] if e["t"] == 0]
    rest = [e for e in level["events"] if e["t"] > 0]
    return head + sorted(rest + placed, key=lambda e: e["t"])


# --- Gimmicks (docs/plans/2026-10-09-epizoda-6.md, 7) --------------------------------------------

HOLD_LOOP = 600  # clock of a siege's round of waves
MIDBOSS_DROP = {36, 11, 4, 83, 2, 30, 53, 34, 35, 46}  # a boss block's level-ending and speed events
MESSAGE_BEHIND, MESSAGE_BOSS, MESSAGE_AFTERBURNER, MESSAGE_DANGER, MESSAGE_BONUS = 1, 2, 7, 8, 9


def midboss_span(source):
    """A mid-level boss's timing (relative to its block): where the map stops (where the original
    stops it, or once the boss is in view), and its loop: from after its last spawn and the stop to
    the end of its pattern (at most 900 on)."""
    boss = source.boss()
    events = [e for e in boss["events"] if e["type"] not in MIDBOSS_DROP]
    spawns = [e for e in events if e["type"] in W.SPAWNS]
    last_spawn = max(e["t"] for e in spawns)
    stops = sorted(e["t"] - boss["start"] for e in source.events
                   if e["type"] in (2, 30) and e["d1"] == 0 and 0 <= e["t"] - boss["start"] <= 1500)
    if stops:
        stop = stops[0]
    else:
        # Ground bosses come with the map: it runs until they are well in view.
        ground = any(e["type"] in W.GROUND_SPAWNS for e in spawns)
        stop = last_spawn + (190 if ground else 0)
    loop_from = max(stop, last_spawn) + 10
    pattern = max([e["t"] for e in events] + [loop_from + 200])
    return stop, loop_from, min(pattern, loop_from + 900)


def midboss_template(source, p):
    """A boss of an original level in the middle of a new one: the map stops (the clock running on,
    53), its pattern loops (54) until its enemies are gone (70), then the map goes on at the level's
    speeds; its level-ending events left out."""
    boss = source.boss()
    stop, loop_from, loop_to = p["loop"]
    events = [dict(e) for e in boss["events"] if e["type"] not in MIDBOSS_DROP and e["t"] <= loop_to
              and not (e["type"] == 79 and not e["d1"] and not e["d2"])]  # (its bar stays up)
    links = sorted(boss["links"])
    a, b = links[0], (links[1] if len(links) > 1 else 0)
    b1, b2, b3 = p["speeds"]
    if not any(e["type"] == 16 for e in events):
        events.insert(0, event(0, 16, d1=MESSAGE_BOSS))
    events += [event(stop, 2), event(stop, 53)]
    # Out as soon as the boss is gone (looked for every 50), else round again. The jumps' targets
    # are set by place() (it makes the times absolute).
    events += [dict(event(t, 70, d1=-1, d2=a, d4=b), jump="exit") for t in range(loop_from + 50, loop_to + 1, 50)]
    events += [dict(event(loop_to, 70, d1=-1, d2=a, d4=b), jump="exit"),
               dict(event(loop_to, 54, d1=-1), jump="loop"),
               event(loop_to + 2, 2, d1=b1, d2=b2, d3=b3), event(loop_to + 2, 53, d1=99)]
    events.sort(key=lambda e: e["t"])
    return dict(events=events, links=links, length=loop_to + 2, loop=(loop_from, loop_to))


# Credits: the coins and gems enemies can leave (the item data's enemies 390-399: 10, 25, 50, 75,
# 100, 250, 500, 1000, 2500 and 5000 credits; always loaded).
COINS = {390: 10, 391: 25, 392: 50, 393: 75, 394: 100, 395: 250, 396: 500, 397: 1000, 398: 2500, 399: 5000}


def with_drops(events, coin):
    """A placed wave's events with each linked enemy leaving a coin (event 33 after its spawn),
    unless the wave already gives its link a drop of its own."""
    own = {e["d4"] for e in events if e["type"] == 33}
    out = []
    for e in events:
        out.append(e)
        if e["type"] in W.SPAWNS and e["d4"] and e["d4"] not in own:
            out.append(event(e["t"], 33, d1=coin, d4=e["d4"], ep=5))
    return out


def pick_coin(rnd, value):
    """A coin worth about value (a little either way)."""
    target = value * rnd.uniform(0.6, 1.5)
    return min(COINS, key=lambda c: abs(COINS[c] - target))


def ground_banks(ground_sources, room):
    """The sheets of the ground enemies most used, up to room of them."""
    count = Counter()
    for s in ground_sources:
        for _, _, enemy in s.ground_objects():
            count[s.enemies[enemy]["shapebank"]] += 1
    return [b for b, _ in count.most_common(room)]


def place_ground(grid, ground_sources, banks, start, boss_time, rnd, density=None, min_rate=0.45):
    """Ground enemy events for a new map (see compose)."""
    found = Counter()       # key -> enemies found on it in the originals
    seen = Counter()        # key -> times it occurs in the originals' maps
    options = defaultdict(Counter)  # key -> (kind, episode, enemy) -> count
    for s in ground_sources:
        objects = [o for o in s.ground_objects() if W.sheets_of(s.enemies, o[2]) <= banks]
        if not objects:
            continue
        for key, kind, enemy in objects:
            found[key] += 1
            options[key][(kind, s.episode, enemy)] += 1
            banks.add(s.enemies[enemy]["shapebank"])
        g = s.map_grid()
        for r in range(300):
            for c in range(14):
                seen[g[r][c]] += 1
                if r >= 1 and c < 13:
                    seen[(g[r - 1][c], g[r - 1][c + 1], g[r][c], g[r][c + 1])] += 1
    rate = {k: found[k] / max(seen[k], found[k]) for k in found}
    events = []
    taken = set()
    for r in range(row_at(start + 100), row_at(boss_time - 200), -1):
        for c in range(1, 13):
            for key, size in (((grid[r - 1][c], grid[r - 1][c + 1], grid[r][c], grid[r][c + 1]), 2), (grid[r][c], 1)):
                if rate.get(key, 0) < min_rate:
                    continue
                if density and rnd.random() > density(r):
                    continue
                cells = {(r - dy, c + dx) for dy in range(size) for dx in range(size)}
                if any((rr, cc) in taken for rr, cc in cells):
                    continue
                if rnd.random() > rate[key]:
                    continue
                (kind, ep, enemy), = rnd.choices(list(options[key]), list(options[key].values()))
                taken |= cells
                events.append(event(ground_time(r), kind, d1=enemy, d2=24 * c - 30, ep=ep))
                break
    return events


def courier_events(t, prize, kinds, rnd):
    """A secret: a lone enemy crossing the top of the screen fast, leaving a data cube or a warp
    orb to a secret level (prize "cube" or "warp:<level>") when shot down in time. kinds: sky enemies
    (episode, number, enemy) the level's sheets show."""
    ep, number, _ = rnd.choice(kinds)
    left = rnd.random() < 0.5
    out = [event(t, 15, d1=number, d2=-24 if left else 268, d4=COURIER_LINK, d5=44, ep=ep),
           event(t, 20, d1=0, d2=0, d4=COURIER_LINK), event(t, 19, d1=3 if left else -3, d2=0, d4=COURIER_LINK)]
    if prize == "cube":
        out.append(event(t, 33, d1=DATA_CUBE, d4=COURIER_LINK, ep=5))
    else:
        out.append(dict(event(t, 33, d1=WARP_ORB, d4=COURIER_LINK, ep=5), warp=prize.split(":", 1)[1]))
    return out


def courier_kinds(wave_sources, banks):
    """Sky enemies for couriers: shootable in a pass (armor 5-40), not too big, flying straight;
    the waves' own, or else any episode 4 and 5 levels fly on the level's sheets."""
    def suits(en):
        return (en["shapebank"] in banks and 5 <= en["armor"] <= 40 and en["esize"] <= 1 and
                0 < en["value"] < 10000 and not en["xaccel"] and not en["yaccel"] and not en["elaunchfreq"])

    kinds = {}
    for s in wave_sources:
        for w in s.waves():
            for e in w["events"]:
                if e["type"] == 15 and suits(s.enemies[e["d1"]]):
                    kinds[(s.episode, e["d1"])] = s.enemies[e["d1"]]
    if not kinds:
        for s in W.originals(episodes=(4, 5)):
            for e in s.events:
                if e["type"] == 15 and e["t"] < 60000 and suits(s.enemies[e["d1"]]):
                    kinds[(s.episode, e["d1"])] = s.enemies[e["d1"]]
    return [(ep, n, en) for (ep, n), en in sorted(kinds.items())]


def gimmick_events(g, speeds, wave_sources, banks, rnd, placements):
    """The level's gimmicks as events (and an ambush's waves as placements)."""
    out = []
    if g.get("couriers"):
        kinds = courier_kinds(wave_sources, banks)
        assert kinds, "no enemy for the couriers"
        for t, prize in g["couriers"]:
            out += courier_events(t, prize, kinds, rnd)
    b1, b2, b3 = speeds
    for t0, t1, factor in g.get("bursts", []):
        # Afterburners: the level rushes, every layer faster by factor (their ratios kept, so the
        # upper layers last as long; events keep to the map).
        out += [event(t0 - 80, 16, d1=MESSAGE_AFTERBURNER, d2=30),
                event(t0, 2, d1=b1 * factor, d2=b2 * factor, d3=b3 * factor), event(t1, 2, d1=b1, d2=b2, d3=b3)]
    for t0, t1 in g.get("dark", []):
        # Lights out: only a spotlight round the ship (BRAINIAC, ASSASSIN).
        out += [event(t0, 64, d1=6, d2=1, d3=1), event(t1, 64, d1=6, d2=0)]
    for t0, t1 in g.get("flip", []):
        # The screen upside down (LAVA RUN, EYESPY), a warning first.
        out += [event(t0 - 80, 16, d1=MESSAGE_DANGER, d2=30), event(t0, 64, d1=9, d2=1, d3=1), event(t1, 64, d1=9, d2=0)]
    for t, (ep, name) in g.get("ambush", []):
        # Enemies from behind (a wave of an original that has them come up from the bottom).
        source = W.Source(ep, name)
        behind = [(i, w) for i, w in enumerate(source.waves())
                  if any(e["type"] in (18, 23, 32) for e in w["events"]) and set(w["banks"]) <= banks
                  and w["count"] >= 2]
        assert behind, f"{name} has no wave from behind on the sheets {sorted(banks)}"
        index, w = rnd.choice(behind)
        out.append(event(t - 70, 16, d1=MESSAGE_BEHIND, d2=30))
        placements.append(dict(kind="wave", episode=ep, name=name, index=index, start=t, drop=pick_coin(rnd, 100)))
    return out


def compose(grid, wave_sources, boss_source, ground_sources, boss_time, seed, density=None,
            intensity=lambda f: 0.4 + 0.6 * f, start=150, ground_waves=False, wealth=10000, gimmicks=None,
            speeds=(1, 2, 3), ground_sheets=2):
    """The level's own events and its placements (see expand). grid: the new layer 1 map (rows of
    shapes). density(row) -> chance of a ground enemy on a suitable tile there. intensity(fraction
    of the level) -> how dense the waves come (0-1)."""
    rnd = random.Random(seed)
    events = []
    placements = []

    # The boss, and the enemy sheets everything must share.
    boss = boss_source.boss()
    banks = set()
    for e in boss["events"]:
        if e["type"] in W.SPAWNS:
            banks.add(boss_source.enemies[e["d1"]]["shapebank"])
    placements.append(dict(kind="boss", episode=boss_source.episode, name=boss_source.name, start=boss_time))

    # A boss in the middle of the level (its sheets before the waves'): the map stops while it is
    # fought, so the clock runs ahead of the map by the fight's length from then on (shift).
    gimmicks = gimmicks or {}
    calm = list(gimmicks.get("calm", []))  # no enemies at all
    # No waves from t0 to t1, their events over before the third (around an ambush: its own).
    windows = [(t0, t1, t0) for t0, t1 in calm] + [(t - 100, t + 500, t + 300) for t, _ in gimmicks.get("ambush", [])]
    shift_from, shift = CLOCK_END, 0
    if gimmicks.get("midboss"):
        (ep, name), at = gimmicks["midboss"]
        mid = W.Source(ep, name)
        stop, loop_from, loop_to = midboss_span(mid)
        mid_banks = {mid.enemies[e["d1"]]["shapebank"] for e in mid.boss()["events"] if e["type"] in W.SPAWNS}
        for b in sorted(mid_banks):
            if len(banks) < 4:
                banks.add(b)
        placements.append(dict(kind="midboss", episode=ep, name=name, start=at, loop=[stop, loop_from, loop_to],
                               speeds=list(speeds)))
        assert all(b in banks for b in mid_banks), f"{name}'s sheets {mid_banks} do not fit with {banks}"
        # (Waves' events never in its loop: they would come round again with it.)
        windows.append((at - 200, at + loop_to + 2 + 150, at + loop_from))
        # The map stands from at + stop until the fight is over (the clock at at + loop_to + 2).
        shift_from, shift = at + stop, loop_to + 2 - stop
        for t0, t1, *_ in gimmicks.get("bursts", []) + gimmicks.get("dark", []) + gimmicks.get("flip", []) + \
                [(t, t + 600) for t, _ in gimmicks.get("ambush", [])] + \
                [(t, t + 200) for t, _ in gimmicks.get("couriers", [])]:
            assert t1 < at - 200 or t0 > at + loop_to + 2, "a gimmick during the mid-level boss"

    # A warp orb's sheet, when the level hides one.
    if any(prize.startswith("warp") for _, prize in gimmicks.get("couriers", [])):
        banks.add(WARP_SHEET)

    # Sheets an ambush's waves need.
    for _, (ep, name) in gimmicks.get("ambush", []):
        need = Counter(b for w in W.Source(ep, name).waves() if any(e["type"] in (18, 23, 32) for e in w["events"])
                       for b in w["banks"])
        if need and not set(need) & banks and len(banks) < 4:
            banks.add(need.most_common(1)[0][0])

    # The ground enemies' sheets next (they go with the map), at most two (ground_sheets); the
    # waves get the rest.
    for b in ground_banks(ground_sources, 2)[:ground_sheets]:
        if len(banks) < 4:
            banks.add(b)

    # Waves the sheets allow (four sheets in all: the boss's and the waves' most common).
    templates = [(s, i, w) for s in wave_sources for i, w in enumerate(s.waves(ground=ground_waves))
                 if 0 < w["count"] <= 12 and w["length"] <= 1600]
    common = {}
    for _, _, w in templates:
        for b in w["banks"]:
            common[b] = common.get(b, 0) + w["count"]
    for b in sorted(common, key=lambda b: -common[b]):
        if len(banks) >= 4:
            break
        banks.add(b)
    templates = [x for x in templates if set(x[2]["banks"]) <= banks]

    # A siege: the map stops and the level's waves come round and round until the level timer
    # (67) runs out (its countdown on the screen), then the map goes on.
    hold = []
    if gimmicks.get("hold"):
        at, seconds = gimmicks["hold"]
        assert not gimmicks.get("midboss"), "a siege and a mid-level boss in one level"
        loop_from, loop_to = at + 20, at + HOLD_LOOP
        exit_ = loop_to + 10
        short = [x for x in templates if x[2]["length"] <= HOLD_LOOP // 3 and x[2]["count"] >= 3]
        for k in range(3):
            source, index, w = rnd.choice(short)
            placements.append(dict(kind="wave", episode=source.episode, name=source.name, index=index,
                                   start=loop_from + k * (HOLD_LOOP // 3), _count=w["count"]))
        # (The timer's jump runs the event before its target again: the message there, not the loop.)
        hold = [event(at - 80, 16, d1=MESSAGE_DANGER, d2=30), event(at, 2), event(at, 53),
                event(at, 67, d1=1, d2=exit_, d3=seconds * 35 // 100), event(loop_to, 54, d1=loop_from),
                event(exit_ - 2, 16, d1=4, d2=30), event(exit_, 2, d1=speeds[0], d2=speeds[1], d3=speeds[2]),
                event(exit_, 53, d1=99)]
        windows.append((at - 200, exit_ + 150, loop_from))
        shift_from, shift = at, exit_ - at

    t = start
    end = boss_time - 350
    while t < end:
        inside = [w for w in windows if w[0] <= t < w[1]]
        if inside:
            t = inside[0][1]
            continue
        f = (t - start) / max(1, end - start)
        level = intensity(f)
        # Bigger waves as it gets harder; a pause after each, shorter as it gets harder.
        bound = min([w[2] for w in windows if w[0] > t] + [end + 400])
        fitting = [x for x in templates if x[2]["count"] <= 3 + level * 10 and x[2]["length"] < bound - t]
        if not fitting:
            later = [w[1] for w in windows if w[0] > t]
            if later:
                t = min(later)
                continue
            break
        source, index, w = rnd.choice(fitting)
        placement = dict(kind="wave", episode=source.episode, name=source.name, index=index, start=t)
        if ground_waves:
            placement["ground"] = True
        placements.append(placement)
        placement["_count"] = w["count"]
        spawn_span = max(e["t"] for e in w["events"] if e["type"] in W.SPAWNS)
        t += spawn_span + int(rnd.uniform(90, 260) * (1.3 - level))

    # Credits: most waves' enemies leave coins, worth what makes the level's wealth in all.
    wave_enemies = sum(p.get("_count", 0) for p in placements)
    for p in placements:
        n = p.pop("_count", 0)
        if p["kind"] == "wave" and rnd.random() < 0.65:
            p["drop"] = pick_coin(rnd, wealth / max(1, 0.65 * wave_enemies))

    # Stationary ground enemies where the map has a place for them: on tiles (or 2x2 blocks of
    # tiles) that carry an enemy in most of the places the originals have them (turret pads,
    # emplacements, bunkers painted into the tileset), not on any tile one once stood on.
    ground = place_ground(grid, ground_sources, banks, start, boss_time - shift, rnd, density)
    for e in ground:
        if e["t"] >= shift_from:
            e["t"] += shift  # the map stood still for the mid-level boss
    events += [e for e in ground if not any(w0 <= e["t"] < w1 for w0, w1 in calm)]
    events += gimmick_events(gimmicks, speeds, wave_sources, banks, rnd, placements) + hold

    # The level's settings at its start (EVENTS.md 8: one sheet event for every enemy, no random
    # enemies), and the end if the boss is never found.
    banks = sorted(b for b in banks if b not in (21, 26))[:4]
    sheets = (banks + [0] * 4)[:4]
    head = [event(0, 2, d1=1, d2=2, d3=3), event(0, 5, sheets[0], sheets[1], d3=sheets[2], d4=sheets[3]),
            event(0, 8), event(0, 13)]
    events = head + sorted(events, key=lambda e: e["t"]) + [event(CLOCK_END - 50, 11)]
    return events, placements, banks
