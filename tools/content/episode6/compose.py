"""Composing an episode 6 level's events: waves of the original levels placed anew along a
difficulty curve, stationary ground enemies on the tiles of the new map that suit them, the boss
block at the end (tools/content/EVENTS.md has the rules this follows).

Events are dicts as tyrevents reads them (t, type, d1..d6, d4); an event naming an enemy (its d1)
carries the episode it is from ("ep"), so the build can bring it into episode 6's item data.
"""
import random

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
        placed += place(template, p["start"], links, source.episode)
    head = [e for e in level["events"] if e["t"] == 0]
    rest = [e for e in level["events"] if e["t"] > 0]
    return head + sorted(rest + placed, key=lambda e: e["t"])


def compose(grid, wave_sources, boss_source, ground_sources, boss_time, seed, density=None,
            intensity=lambda f: 0.4 + 0.6 * f, start=150, ground_waves=False):
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
        spawn_span = max(e["t"] for e in w["events"] if e["type"] in W.SPAWNS)
        t += spawn_span + int(rnd.uniform(90, 260) * (1.3 - level))

    # Stationary ground enemies on tiles they stood on in the originals.
    affinity = {}
    ground_ep = {}
    for s in ground_sources:
        for enemy, shapes in s.ground_objects().items():
            if s.enemies[enemy]["shapebank"] not in banks and len(banks) >= 4:
                continue
            for shape, n in shapes.items():
                affinity.setdefault(shape, []).append((enemy, n))
            ground_ep[enemy] = s.episode
            banks.add(s.enemies[enemy]["shapebank"])
    last_row = row_at(boss_time - 200)
    taken = set()
    for r in range(row_at(start + 100), last_row, -1):
        for c in range(2, 13):
            options = affinity.get(grid[r][c])
            if not options or (density and rnd.random() > density(r)):
                continue
            if any((rr, cc) in taken for rr in range(r - 2, r + 3) for cc in range(c - 2, c + 3)):
                continue
            enemies, weights = zip(*options)
            enemy = rnd.choices(enemies, weights)[0]
            taken.add((r, c))
            events.append(event(ground_time(r), 6, d1=enemy, d2=24 * c - 30, ep=ground_ep[enemy]))

    # The level's settings at its start (EVENTS.md 8: one sheet event for every enemy, no random
    # enemies), and the end if the boss is never found.
    banks = sorted(b for b in banks if b not in (21, 26))[:4]
    sheets = (banks + [0] * 4)[:4]
    head = [event(0, 2, d1=1, d2=2, d3=3), event(0, 5, sheets[0], sheets[1], d3=sheets[2], d4=sheets[3]),
            event(0, 8), event(0, 13)]
    events = head + sorted(events, key=lambda e: e["t"]) + [event(CLOCK_END - 50, 11)]
    return events, placements, banks
