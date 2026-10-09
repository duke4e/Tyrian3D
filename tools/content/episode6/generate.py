#!/usr/bin/env python3
"""Episode 6's levels: new maps (mapsynth.py) and events (compose.py) from the designs below,
written to tools/content/episode6/levels/<name>.json (our own data: maps of tile numbers and
events; build.py turns them into the game's files with the game's data).

usage: <python with numpy and PIL> tools/content/episode6/generate.py [level...]

Pictures of the maps go to export/episode6/.
"""
import json
import math
import os
import random
import sys

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


def maps_of(levels_, layer):
    return [l["maps"][layer] for l in levels_]


def pick(names):
    """Original levels by (episode, name)."""
    return [l for l in sources.original_levels() if (l["episode"], l["name"]) in names]


def noise(seed):
    """A smooth 2D field (sums of sines), -1..1."""
    rnd = random.Random(seed)
    waves_ = [(rnd.uniform(0.15, 0.6), rnd.uniform(0.04, 0.12), rnd.uniform(0, 6.3)) for _ in range(5)]
    return lambda x, y: sum(math.sin(a * x + b * y + p) for a, b, p in waves_) / len(waves_)


# --- DIG SITE: Savara. Open sea, an archipelago, the dig site's island, a field of rocks, the boss
# on open water. ----------------------------------------------------------------------------------

def dig_site():
    name, letter = "DIG SITE", "y"
    savara = [(1, "SAVARA"), (1, "SAVARA V"), (3, "SAVARA Y"), (5, "SAVARA")]
    src = pick(savara)
    m = Model(maps_of(src, 0), max_tiles=LAYER_TILES[0])
    mats = preview.materials(letter, {"water": (12, 38, 56), "sand": (110, 80, 40), "rock": (85, 85, 80),
                                      "jungle": (30, 80, 25)}, list(m.count))
    n = noise(11)
    boss_time = 6100

    def want(x, y):
        v = n(x, y)
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
        w = want(x, y)
        if y < 90 and mats[t]["water"] < 0.5:
            return 0  # the boss's open water: nothing else, where anything else can be avoided
        return (0.02 + mats[t][w]) ** 2

    layer1, stats = generate(m, 300, 14, 4, bias=bias)
    print(name, "layer 1", dict(stats))
    clouds = Model(maps_of(src, 1), max_tiles=LAYER_TILES[1] - 1)
    layer2, stats = generate(clouds, 600, 14, 5)
    print(name, "layer 2", dict(stats))
    layer3 = [[0] * 15 for _ in range(600)]

    wave_sources = [waves.Source(e, n_) for e, n_ in [(1, "SAVARA"), (3, "SAVARA Y"), (4, "SAVARA IV"), (1, "SAVARA V")]]
    boss = waves.Source(1, "SAVARA")
    ground = [waves.Source(e, n_) for e, n_ in [(1, "SAVARA"), (3, "SAVARA Y"), (5, "SAVARA")]]

    def density(row):
        return 0.5 if 140 <= row < 190 else 0.18

    events, placements, banks = compose.compose(layer1, wave_sources, boss, ground, boss_time, seed=7,
                                                density=density)
    return dict(name=name, song=33, shapes=letter, maps=[layer1, layer2, layer3], events=events,
                placements=placements, banks=banks)


DESIGNS = {"DIG SITE": dig_site}


def main(names):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PICTURES, exist_ok=True)
    for name in names or DESIGNS:
        level = DESIGNS[name]()
        slug = name.lower().replace(" ", "_")
        with open(os.path.join(OUT, f"{slug}.json"), "w") as f:
            json.dump(level, f, separators=(",", ":"))
        preview.strips(preview.picture([level["maps"][0]], level["shapes"]), os.path.join(PICTURES, f"{slug}.png"))
        events = compose.expand(level)
        spawns = sum(1 for e in events if e["type"] in waves.SPAWNS)
        print(f"{name}: {len(events)} events, {spawns} enemies, {len(level['placements'])} waves and bosses, "
              f"sheets {level['banks']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
