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
                for new in range(1, 41):
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
        if e["d4"] in mapping and (e["type"] in W.SPAWNS or W.by_link(e) is not None):
            e["d4"] = mapping[e["d4"]]
        if e["type"] == 39:
            e["d1"] = mapping.get(e["d1"], e["d1"])
            e["d2"] = mapping.get(e["d2"], e["d2"])
        if e["type"] == 79:
            e["d1"] = mapping.get(e["d1"], e["d1"])
            e["d2"] = mapping.get(e["d2"], e["d2"])
        if e["type"] in ENEMY_D1:
            e["ep"] = ep
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
        else:
            template = source.waves(ground=p.get("ground", False))[p["index"]]
        events = place(template, p["start"], links, source.episode)
        if p.get("drop"):
            events = with_drops(events, p["drop"])
        placed += events
    head = [e for e in level["events"] if e["t"] == 0]
    rest = [e for e in level["events"] if e["t"] > 0]
    return head + sorted(rest + placed, key=lambda e: e["t"])


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
        objects = [o for o in s.ground_objects()
                   if s.enemies[o[2]]["shapebank"] in banks or len(banks) < 4]
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


def compose(grid, wave_sources, boss_source, ground_sources, boss_time, seed, density=None,
            intensity=lambda f: 0.4 + 0.6 * f, start=150, ground_waves=False, wealth=10000):
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

    # The ground enemies' sheets next (they go with the map), at most two; the waves get the rest.
    for b in ground_banks(ground_sources, 2):
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

    t = start
    end = boss_time - 350
    while t < end:
        f = (t - start) / max(1, end - start)
        level = intensity(f)
        # Bigger waves as it gets harder; a pause after each, shorter as it gets harder.
        fitting = [x for x in templates if x[2]["count"] <= 3 + level * 10 and x[2]["length"] < end - t + 400]
        if not fitting:
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
    events += place_ground(grid, ground_sources, banks, start, boss_time, rnd, density)

    # The level's settings at its start (EVENTS.md 8: one sheet event for every enemy, no random
    # enemies), and the end if the boss is never found.
    banks = sorted(b for b in banks if b not in (21, 26))[:4]
    sheets = (banks + [0] * 4)[:4]
    head = [event(0, 2, d1=1, d2=2, d3=3), event(0, 5, sheets[0], sheets[1], d3=sheets[2], d4=sheets[3]),
            event(0, 8), event(0, 13)]
    events = head + sorted(events, key=lambda e: e["t"]) + [event(CLOCK_END - 50, 11)]
    return events, placements, banks
