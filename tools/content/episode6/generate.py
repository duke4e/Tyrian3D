#!/usr/bin/env python3
"""Episode 6's levels: new maps (mapsynth.py) and events (compose.py) from the designs below,
written to tools/content/episode6/levels/<name>.json (our own data: maps of tile numbers, events,
and references to the original levels' waves and bosses; build.py turns them into the game's files
with the game's data).

usage: <python with numpy and PIL> tools/content/episode6/generate.py <level>...

Only the levels named are made again (a level once played stays as it is). Pictures of the maps go
to export/episode6/.
"""
import json
import math
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose  # noqa: E402
import preview  # noqa: E402
import sources  # noqa: E402
import waves  # noqa: E402
from mapsynth import LAYER_TILES, Model, generate  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "levels")
PICTURES = os.path.join(ROOT, "export", "episode6")

# Events at a level's start that set its look (taken from a "look" level): the star field, scroll
# speeds, layer order and opacity, effects (lava, water), filters.
LOOK_EVENTS = {1, 2, 3, 8, 9, 21, 28, 29, 42, 43, 44, 48, 64, 65, 72, 73}

_originals = None


def originals():
    global _originals
    if _originals is None:
        _originals = {(l["episode"], l["name"]): l for l in sources.original_levels()}
    return _originals


def maps_of(names, layer):
    return [originals()[n]["maps"][layer] for n in names]


def noise(seed, scale=1.0):
    """A smooth 2D field (sums of sines), about -1.6..1.6; scale > 1 makes larger blobs."""
    rnd = random.Random(seed)
    parts = [(rnd.uniform(0.15, 0.6) / scale, rnd.uniform(0.04, 0.12) / scale, rnd.uniform(0, 6.3)) for _ in range(5)]
    return lambda x, y: sum(math.sin(a * x + b * y + p) for a, b, p in parts) / len(parts) * 1.6


def base_tiles(grids, share=0.6):
    """The most common tiles, covering share of the sources' cells: the "ground" the features
    stand on (open space, sea, sand...)."""
    count = Counter(t for g in grids for row in g for t in row)
    total = sum(count.values())
    out, covered = set(), 0
    for t, n in count.most_common():
        if covered >= share * total:
            break
        out.add(t)
        covered += n
    return out


def zones(zone_list, seed, scale=1.0, clear=None, share=0.6):
    """A plan of features by zones, for a design's bias: zone_list is (first row, last row,
    amount 0-1) from the map's top (row 0 is the level's end), amount how much of the zone is
    features (tiles other than the base). clear(row) -> True: only base tiles there (where the
    map can do without others: the boss's open space)."""
    def make_bias(model, grids):
        base = base_tiles(grids, share)
        n = noise(seed, scale)

        def amount(y):
            for a, b, v in zone_list:
                if a <= y <= b:
                    return v
            return 0.0

        def bias(t, x, y):
            if clear and clear(y):
                return 1.0 if t in base else 0
            want_feature = n(x, y) > 1.6 - 3.2 * amount(y)
            if t in base:
                return 0.12 if want_feature else 1.0
            return 1.0 if want_feature else 0.03
        return bias
    return make_bias


def make(design):
    """A level from a design dict (see the levels below)."""
    name = design["name"]
    letter = design["shapes"]
    seed = design.get("seed", 1)
    grids = maps_of(design["map"], 0)
    model = Model(grids, max_tiles=LAYER_TILES[0])
    bias = design["bias"](model, grids) if design.get("bias") else None
    layer1, stats = generate(model, 300, 14, seed, bias=bias)
    print(name, "layer 1", dict(stats))
    layers = [layer1]
    for k, rows, columns in ((1, 600, 14), (2, 600, 15)):
        names = design.get(f"layer{k + 1}")
        if not names:
            layers.append([[0] * columns for _ in range(rows)])
            continue
        m = Model(maps_of(names, k), max_tiles=LAYER_TILES[k] - 1)
        upper_bias = design.get(f"bias{k + 1}")
        grid, stats = generate(m, rows, columns, seed + k,
                               bias=upper_bias(m, maps_of(names, k)) if upper_bias else None)
        print(name, f"layer {k + 1}", dict(stats))
        layers.append(grid)

    wave_sources = [waves.Source(*s) for s in design["waves"]]
    boss = waves.Source(*design["boss"])
    ground = [waves.Source(*s) for s in design.get("ground", [])]
    events, placements, banks = compose.compose(layer1, wave_sources, boss, ground, design["boss_time"],
                                                seed=design.get("events_seed", seed + 7),
                                                density=design.get("density"),
                                                intensity=design.get("intensity", lambda f: 0.4 + 0.6 * f),
                                                ground_waves=design.get("ground_waves", False))
    # The look of a chosen original level replaces the default settings at the start.
    look = waves.Source(*design.get("look", design["boss"]))
    # (Of the effects, lava, water and the spotlight: the blurs and the upside-down screen show as
    # flat slabs in the 3D view.)
    look_events = [dict(e) for e in look.events if e["t"] == 0 and e["type"] in LOOK_EVENTS and
                   not (e["type"] == 64 and e["d1"] not in (1, 2, 6))]
    if design.get("speeds"):
        look_events = [e for e in look_events if e["type"] not in (2, 3)]
        b1, b2, b3 = design["speeds"]
        look_events.insert(0, compose.event(0, 2, d1=b1, d2=b2, d3=b3))
    head = [e for e in events if e["t"] == 0 and e["type"] in (5, 13)]
    rest = [e for e in events if not (e["t"] == 0 and e["type"] in (2, 5, 8, 13))]
    return dict(name=name, song=design["song"], shapes=letter, maps=layers, events=look_events + head + rest,
                placements=placements, banks=banks)


# --- The levels ---------------------------------------------------------------------------------
# map: the originals whose layer 1 the new map's tiles follow; layer2/layer3: those of the upper
# layers (none: empty); bias: the plan; waves, boss, ground: the originals whose waves, boss and
# ground enemies are used (episode, name); look: the original whose start settings it takes;
# speeds: the layers' scroll speeds (layer 3 at most 2 when it has things on it: at 3 it runs out
# before the boss).

SAVARA = [(1, "SAVARA"), (1, "SAVARA V"), (3, "SAVARA Y"), (5, "SAVARA")]


def dig_site_bias(model, grids):
    mats = preview.materials("y", {"water": (12, 38, 56), "sand": (110, 80, 40), "rock": (85, 85, 80),
                                   "jungle": (30, 80, 25)}, list(model.count))
    n = noise(11)

    def want(x, y):
        v = n(x, y) / 1.6
        if y >= 250:              # the start: open sea, a few islets
            return "sand" if v > 0.62 else "water"
        if y >= 190:              # the archipelago
            return "sand" if v > 0.25 else ("rock" if v < -0.75 else "water")
        if y >= 140:              # the dig site: a big island, jungle on its high ground
            edge = abs(x - 6.5) / 6.5 + 0.35 * v
            return "water" if edge > 0.85 else ("jungle" if v > 0.35 else "sand")
        if y >= 95:               # a field of rocks
            return "rock" if v > 0.3 else "water"
        return "water"            # open water for the boss

    def bias(t, x, y):
        if y < 90 and mats[t]["water"] < 0.5:
            return 0  # the boss's open water: nothing else, where anything else can be avoided
        return (0.02 + mats[t][want(x, y)]) ** 2
    return bias


LEVELS = [
    # Played and approved as it is (2026-10-09): not to be made again (its map would come out
    # different: the plan's numbers changed form since).
    dict(name="DIG SITE", frozen=True, shapes="y", song=33, seed=4, events_seed=7, map=SAVARA, layer2=SAVARA, bias=dig_site_bias,
         waves=[(1, "SAVARA"), (3, "SAVARA Y"), (4, "SAVARA IV"), (1, "SAVARA V")], boss=(1, "SAVARA"),
         ground=[(1, "SAVARA"), (3, "SAVARA Y"), (5, "SAVARA")], boss_time=6100,
         density=lambda row: 0.5 if 140 <= row < 190 else 0.18, look=(1, "SAVARA"), speeds=(1, 2, 3)),
]


def boss_clear(boss_time, margin=6):
    """Rows of the boss's open space: from where the boss comes to the map's end."""
    first = compose.row_at(boss_time) + margin
    return lambda y: y <= first


def reef_bias(model, grids):
    """A coast along the left, reefs and rocks off it, open water for the boss."""
    mats = preview.materials("y", {"water": (12, 38, 56), "sand": (110, 80, 40), "rock": (85, 85, 80),
                                   "jungle": (30, 80, 25)}, list(model.count))
    n = noise(23)
    clear = boss_clear(5600)

    def want(x, y):
        coast = 3.0 + 2.2 * math.sin(y / 27.0) + 1.2 * math.sin(y / 9.0 + 2) + (2.5 if 150 < y < 200 else 0)
        if y < 70:
            coast -= 4
        if x < coast:
            return "jungle" if x < coast - 2.5 and n(x, y) > -0.3 else "sand"
        v = n(x, y)
        if x > coast + 2 and v > 0.9 and y >= 70:
            return "rock"
        return "water"

    def bias(t, x, y):
        if clear(y) and x > 4 and mats[t]["water"] < 0.5:
            return 0
        return (0.02 + mats[t][want(x, y)]) ** 2
    return bias


def roost_bias(model, grids):
    """Jungle: a river winding up the level, a lake in the middle, cliffs, open ground for the
    boss."""
    mats = preview.materials("x", {"grass": (0, 70, 5), "water": (25, 60, 85), "rock": (90, 90, 90),
                                   "dark": (10, 20, 10)}, list(model.count))

    def want(x, y):
        rx = 7 + 4.2 * math.sin(y / 23.0) + 1.5 * math.sin(y / 7.3 + 1)
        width = 1.4 + 0.8 * math.sin(y / 31.0) + (3.5 if 150 < y < 180 else 0)
        if y < 60:
            width = 0.6
        return "water" if abs(x - rx) < width else "grass"

    def bias(t, x, y):
        return (0.05 + mats[t][want(x, y)]) ** 2
    return bias


ASTEROIDS = [(1, "ASTEROID1"), (1, "ASTEROID2"), (5, "AST ROCK")]
ICE = [(3, "IXMUCANE"), (3, "CAMANIS")]
SNOW = [(4, "ICE EXIT")]
LAVA = [(4, "LAVA RUN"), (4, "LAVA EXIT")]

LEVELS += [
    dict(name="REEF", shapes="y", song=21, seed=31, map=SAVARA, layer2=SAVARA, bias=reef_bias,
         waves=[(4, "SAVARA IV"), (5, "SAVARA")], boss=(4, "SAVARA IV"), ground=[(1, "SAVARA"), (5, "SAVARA")],
         boss_time=5600, density=lambda row: 0.25, look=(4, "SAVARA IV"), speeds=(1, 2, 3)),
    dict(name="GREY MOON", shapes="z", song=1, seed=41, map=[(1, "ASTEROID1"), (1, "ASTEROID2")],
         waves=[(5, "ASTEROIDS"), (1, "ASTEROID1"), (1, "ASTEROID2"), (5, "AST ROCK")], ground_waves=True,
         boss=(5, "AST ROCK"), boss_time=6200, look=(1, "ASTEROID1")),
    dict(name="ROOST", shapes="x", song=28, seed=51, map=[(2, "TORM")], bias=roost_bias,
         waves=[(2, "GRYPHON")], boss=(2, "TORM"), ground=[(2, "TORM")], boss_time=6300,
         density=lambda row: 0.2, look=(2, "TORM")),
    dict(name="DEEP ICE", shapes="w", song=14, seed=61, map=ICE, layer2=[(3, "IXMUCANE")], layer3=[(3, "IXMUCANE")],
         bias=zones([(0, 300, 0.3)], 61),
         waves=[(3, "CAMANIS"), (3, "IXMUCANE"), (3, "SAWBLADES")], boss=(3, "IXMUCANE"),
         ground=[(3, "IXMUCANE"), (3, "CAMANIS")], boss_time=4600, look=(3, "IXMUCANE"), speeds=(1, 2, 2)),
    dict(name="GLACIER", shapes="w", song=4, seed=71, map=SNOW + [(3, "CAMANIS")], layer2=SNOW,
         bias=zones([(0, 300, 0.4)], 71, scale=1.4), waves=[(4, "ICE EXIT"), (3, "FLEET")], boss=(4, "ICE EXIT"),
         ground=[(4, "ICE EXIT")], boss_time=5200, look=(4, "ICE EXIT"), speeds=(1, 2, 2)),
    dict(name="CRUSTGATE", shapes=")", song=17, seed=81, map=LAVA, layer2=LAVA,
         bias=zones([(0, 300, 0.35)], 81, scale=1.5), waves=[(4, "SURFACE"), (4, "LAVA RUN")], boss=(4, "BRAINIAC"),
         ground=[(4, "LAVA RUN"), (4, "LAVA EXIT")], boss_time=6000, look=(4, "LAVA RUN")),
]


DELI = [(1, "DELIANI"), (3, "New Deli")]

LEVELS += [
    dict(name="DELI RUIN", shapes="z", song=14, seed=91, map=DELI, layer2=DELI, layer3=DELI,
         waves=[(1, "DELIANI"), (3, "New Deli")],
         boss=(1, "ASSASSIN"), ground=DELI, boss_time=5800, density=lambda row: 0.3, look=(1, "DELIANI"),
         speeds=(1, 2, 2)),
    dict(name="COLLECTOR", shapes="w", song=29, seed=101, map=[(3, "FLEET")], layer2=[(3, "FLEET")],
         layer3=[(3, "FLEET")], waves=[(3, "FLEET"), (5, "STATION")], ground_waves=True, boss=(3, "FLEET"),
         boss_time=5600, look=(3, "FLEET"), intensity=lambda f: 0.55 + 0.45 * f),
    dict(name="THE CORE", shapes=")", song=23, seed=111, map=[(4, "CORE")], layer2=[(4, "CORE")],
         bias=zones([(0, 300, 0.3)], 111, scale=1.4), waves=[(4, "CORE"), (4, "LAVA EXIT"), (4, "SURFACE")],
         boss=(5, "FRUIT"), ground=[(4, "CORE")], boss_time=5600, density=lambda row: 0.3, look=(4, "CORE"),
         intensity=lambda f: 0.6 + 0.4 * f),
]


def main(names):
    if not names:
        print(__doc__)
        print("levels:", ", ".join(d["name"] for d in LEVELS))
        return 1
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PICTURES, exist_ok=True)
    for design in LEVELS:
        if design["name"] not in names:
            continue
        if design.get("frozen") and "--force" not in names:
            print(f"{design['name']}: frozen (played and approved); --force makes it again")
            continue
        level = make(design)
        slug = design["name"].lower().replace(" ", "_")
        with open(os.path.join(OUT, f"{slug}.json"), "w") as f:
            json.dump(level, f, separators=(",", ":"))
        preview.strips(preview.picture([level["maps"][0]], level["shapes"]), os.path.join(PICTURES, f"{slug}.png"))
        events = compose.expand(level)
        spawns = sum(1 for e in events if e["type"] in waves.SPAWNS)
        print(f"{design['name']}: {len(events)} events, {spawns} enemies, {len(level['placements'])} waves and bosses, "
              f"sheets {level['banks']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
