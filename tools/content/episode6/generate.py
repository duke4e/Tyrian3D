#!/usr/bin/env python3
"""Episode 6's levels: new maps (mapsynth.py) and events (compose.py) from the designs below,
written to tools/content/episode6/levels/<name>.json (our own data: maps of tile numbers, events,
and references to the original levels' waves and bosses; build.py turns them into the game's files
with the game's data).

usage: <python with numpy and PIL> tools/content/episode6/generate.py [--events] <level>...

Only the levels named are made again (a level once played stays as it is); --events keeps their
maps (and so their terrain) and makes only the events again. Pictures of the maps go
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
import minigames  # noqa: E402
import objects  # noqa: E402
import preview  # noqa: E402
import sources  # noqa: E402
import waves  # noqa: E402
from mapsynth import LAYER_TILES, Model, generate  # noqa: E402
from plan import Plan  # noqa: E402

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
    if design.get("side"):
        # Seen from the side (event 200): open space, the game's stars through blank tiles; the
        # rocks along the window's edges come from the 3D view.
        blank = design["blank"]
        return finish(design, [[[blank] * 14 for _ in range(300)], [[0] * 14 for _ in range(600)],
                               [[0] * 15 for _ in range(600)]])
    grids = maps_of(design["map"], 0)
    model = Model(grids, max_tiles=LAYER_TILES[0])
    slug = name.lower().replace(" ", "_")
    if design.get("keep_map") or EVENTS_ONLY:
        # The map as it is (a map liked as it was): only the events are made again.
        layers = json.load(open(os.path.join(OUT, f"{slug}.json")))["maps"]
        return finish(design, layers)
    plan = None
    if design.get("plan"):
        # The map from a plan: shapes of materials, and objects of the originals pasted in.
        levels = [originals()[n] for n in design["map"]]
        used = {t for l in levels for row in l["maps"][0] for t in row} | set(model.count)
        mats = preview.materials(letter, design["materials"], used)
        library = objects.library(levels, mats, design["base"], design.get("kinds", {}))
        plan = design["plan"](Plan(design["base"], seed=seed))
        bias = plan.bias(mats)
    else:
        bias = design["bias"](model, grids) if design.get("bias") else None
    layer1, stats = generate(model, 300, 14, seed, bias=bias)
    if plan:
        placed = plan.paste_objects(layer1, library)
        stats["objects"] = len(placed)
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
    return finish(design, layers)


def make_invaders(design):
    """The mini-game (minigames.py) on another level's maps (their terrain built already)."""
    layers = json.load(open(os.path.join(OUT, f"{design['maps_of']}.json")))["maps"]
    events = minigames.invaders(design.get("seed", 1))
    data = {5: waves.Source(5, "ASTEROIDS").enemies}
    banks = sorted({data[e["ep"]][e["d1"]]["shapebank"] for e in events if e["type"] in waves.SPAWNS} - {21, 26})
    assert len(banks) <= 4, banks
    sheets = (banks + [0] * 4)[:4]
    look = waves.Source(*design["look"])
    look_events = [dict(e) for e in look.events if e["t"] == 0 and e["type"] in LOOK_EVENTS and e["type"] not in (2, 3, 64)]
    head = [compose.event(0, 5, sheets[0], sheets[1], d3=sheets[2], d4=sheets[3]), compose.event(0, 13)]
    return dict(name=design["name"], song=design["song"], shapes=design["shapes"], maps=layers,
                events=look_events + head + events, placements=[], banks=banks, terrain=None,
                shared_maps=design["maps_of"])


# Seen from the side, the playfield reaches this far (game pixels) ahead of the screen's top, so it
# fills the window turned on its side (event 200's d3, tens of pixels; EVENTS.md).
SIDE_AHEAD = 250


def level_speeds(design):
    """The layers' scroll speeds the level runs at (its own, or its look's)."""
    if design.get("speeds"):
        return tuple(design["speeds"])
    look = waves.Source(*design.get("look", design["boss"]))
    start = [e for e in look.events if e["t"] == 0 and e["type"] == 2]
    return (start[0]["d1"], start[0]["d2"], start[0]["d3"]) if start else (1, 2, 3)


def finish(design, layers):
    """The level's events for its maps, and the level."""
    name, letter, seed = design["name"], design["shapes"], design.get("seed", 1)
    layer1 = layers[0]
    wave_sources = [waves.Source(*s) for s in design["waves"]]
    boss = waves.Source(*design["boss"])
    ground = [waves.Source(*s) for s in design.get("ground", [])]
    events, placements, banks = compose.compose(layer1, wave_sources, boss, ground, design["boss_time"],
                                                seed=design.get("events_seed", seed + 7),
                                                density=design.get("density"),
                                                intensity=design.get("intensity", lambda f: 0.4 + 0.6 * f),
                                                ground_waves=design.get("ground_waves", False),
                                                wealth=design.get("wealth", 10000),
                                                gimmicks=design.get("gimmicks"), speeds=level_speeds(design),
                                                ground_sheets=design.get("ground_sheets", 2))
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
    level = dict(name=name, song=design["song"], shapes=letter, maps=layers, events=look_events + head + rest,
                 placements=placements, banks=banks, terrain=design.get("terrain", {}))
    if design.get("side"):
        # Stars on (the game's and the 3D view's deep ones), the view from the side with its rocks.
        level["events"] = [e for e in level["events"] if not (e["t"] == 0 and e["type"] in (1, 8, 9, 64))]
        level["events"][1:1] = [compose.event(0, 9), compose.event(0, 1, d1=0),
                                compose.event(0, 200, d1=1, d2=design["side"], d3=SIDE_AHEAD // 10)]
        level["terrain"] = None
        level["sideways"] = True
    return level


# --- The levels ---------------------------------------------------------------------------------
# map: the originals whose layer 1 the new map's tiles follow; layer2/layer3: those of the upper
# layers (none: empty); bias: the plan; waves, boss, ground: the originals whose waves, boss and
# ground enemies are used (episode, name); look: the original whose start settings it takes;
# speeds: the layers' scroll speeds (layer 3 at most 2 when it has things on it: at 3 it runs out
# before the boss).



# Materials by tileset (reference colours; "space" is the blank tiles), the base material objects
# stand on, and the kinds of objects by their main material.
SAVARA_MATS = dict(materials={"water": (12, 38, 56), "sand": (110, 80, 40), "rock": (85, 85, 80), "jungle": (30, 80, 25)},
                   base="water", kinds={"rock": "building", "sand": "island", "jungle": "island"})
ASTEROID_MATS = dict(materials={"space": (0, 0, 0), "rock": (90, 90, 90), "dark": (35, 35, 35), "rust": (82, 44, 42)},
                     base="space", kinds={"rock": "station", "dark": "station", "rust": "station"})
DELI_MATS = dict(materials={"floor": (12, 25, 38), "plate": (28, 41, 53), "lamp": (90, 40, 40)},
                 base="floor", kinds={"plate": "building", "lamp": "building"})
TORM_MATS = dict(materials={"grass": (0, 69, 2), "water": (23, 58, 81), "rock": (90, 90, 90), "dark": (10, 20, 10)},
                 base="grass", kinds={"rock": "cliff", "water": "pond", "dark": "cliff"})
ICE_MATS = dict(materials={"cliff": (48, 29, 6), "ice": (105, 160, 171), "deep": (73, 112, 138), "dark": (31, 63, 85)},
                base="cliff", kinds={"ice": "ice", "deep": "ice", "dark": "ice"})
SNOW_MATS = dict(materials={"snow": (105, 160, 171), "rock": (80, 80, 80), "deep": (73, 112, 138)},
                 base="snow", kinds={"rock": "rock", "deep": "rock"})
SPACE_MATS = dict(materials={"space": (0, 0, 0), "hull": (50, 48, 45), "light": (90, 85, 80)},
                  base="space", kinds={"hull": "ship", "light": "ship"})
LAVA_MATS = dict(materials={"lava": (64, 2, 0), "crust": (150, 62, 50), "ember": (80, 15, 8)},
                 base="crust", kinds={"lava": "pool", "ember": "pool"})
CORE_MATS = dict(materials={"floor": (74, 34, 22), "hot": (130, 22, 8), "dark": (40, 15, 10)},
                 base="floor", kinds={"hot": "vent", "dark": "vent"})

# The 3D terrain of the new maps (tools/terrain/levels.json settings; "materials": heights by the
# surfaces' colours, tools/terrain/make_terrain.py), by tileset.
SAVARA_TERRAIN = {"classes": 6, "heights": {}, "forest": "palm",
                  "materials": {"#0c2638": 0, "#09202e": 0, "#6e5028": 8, "#555550": 14, "#1e5019": 12}}
ASTEROID_TERRAIN = {"classes": 6, "heights": {}, "void": "hole"}
DELI_TERRAIN = {"classes": 6, "heights": {}, "materials": {"#0c1926": 0, "#1c2935": 10, "#162330": "~"}}
TORM_TERRAIN = {"classes": 6, "heights": {}, "materials": {"#004502": 0, "#173a51": -14, "#5a5a5a": "~", "#0a140a": "~"}}
ICE_TERRAIN = {"classes": 6, "heights": {}, "rolling": 6, "solid_upper": True}
SNOW_TERRAIN = {"classes": 6, "heights": {}, "rolling": 10}
SPACE_TERRAIN = {"classes": 6, "heights": {}, "void": "hole"}
LAVA_TERRAIN = {"classes": 6, "heights": {}, "materials": {"#400200": -6, "#963e32": 12, "#500f08": "~"},
                "solid_upper": True}
CORE_TERRAIN = {"classes": 6, "heights": {}, "rolling": 10, "solid_upper": True}

SAVARA = [(1, "SAVARA"), (1, "SAVARA V"), (3, "SAVARA Y"), (5, "SAVARA"), (4, "SAVARA IV")]
ASTEROIDS = [(1, "ASTEROID1"), (1, "ASTEROID2"), (5, "AST ROCK")]
DELI = [(1, "DELIANI"), (3, "New Deli")]
ICE = [(3, "IXMUCANE"), (3, "CAMANIS")]
SNOW = [(4, "ICE EXIT"), (3, "CAMANIS")]
LAVA = [(4, "LAVA RUN"), (4, "LAVA EXIT")]


def dig_site(p):
    """Open sea and islets, a jungle continent on the left with buildings off it, the dig site: a
    great island (a landmark of the originals), a field of pillars and bunkers, open water for the
    boss."""
    p.calm(256, 296, 25, 6, 13).want_objects({"island", "building"}, 256, 296, 3, cols=(6, 13))
    p.coast(196, 252, -1, 6, "sand").coast(200, 248, -1, 4, "jungle")
    p.calm(196, 250, 25, 8, 13).want_objects({"building"}, 196, 250, 3, cols=(8, 13))
    p.calm(136, 192, 25).want_objects({"island"}, 136, 192, 1, min_core=150)
    p.calm(95, 132, 25).want_objects({"building"}, 95, 132, 6)
    return p.fill(0, 88, "water")


def reef(p):
    """A long coast on the right with jungle, reefs of rock and bunkers off it, a sea fort (a
    landmark of the originals) between, open water for the boss."""
    p.coast(110, 292, 1, 5, "sand").coast(120, 285, 1, 3, "jungle")
    p.calm(220, 292, 25, 0, 8).want_objects({"building"}, 220, 292, 4, cols=(0, 7))
    p.calm(168, 214, 25).want_objects({"building"}, 168, 214, 1, min_core=60)
    p.calm(110, 165, 25, 0, 8).want_objects({"building"}, 110, 165, 4, cols=(0, 7))
    return p.fill(0, 92, "water")


def grey_moon(p):
    """Asteroid fields thickening, stations and wrecks between them, open space for the boss."""
    p.scatter(200, 295, 10, 3, "rock").scatter(120, 200, 18, 3, "rock")
    p.blob(160, 7, 18, 4, "rock")
    p.calm(230, 296, 1).want_objects({"station"}, 230, 296, 4)
    p.calm(90, 140, 1).want_objects({"station"}, 90, 140, 4)
    return p.fill(0, 80, "space")


def vault(p):
    """The grey moon's vault: strongrooms of plating either side of corridors, lamps along them,
    a hall at the end."""
    for k, r0 in enumerate(range(50, 290, 46)):
        if k % 2:
            p.rect(r0, r0 + 28, 0, 5, "plate").rect(r0 + 8, r0 + 36, 9, 13, "plate")
        else:
            p.rect(r0, r0 + 30, 0, 3, "plate").rect(r0 + 4, r0 + 26, 6, 13, "plate")
        p.scatter(r0, r0 + 36, 4, 1, "lamp", cols=(1, 12))
    return p.fill(0, 40, "floor")


def roost_bias(model, grids):
    """Jungle: a river winding up the level, a lake in the middle, open ground for the boss."""
    mats = preview.materials("x", TORM_MATS["materials"], list(model.count))

    def want(x, y):
        rx = 7 + 4.2 * math.sin(y / 23.0) + 1.5 * math.sin(y / 7.3 + 1)
        width = 1.4 + 0.8 * math.sin(y / 31.0) + (3.5 if 150 < y < 180 else 0)
        if y < 60:
            width = 0.6
        return "water" if abs(x - rx) < width else "grass"

    def bias(t, x, y):
        return (0.05 + mats[t][want(x, y)]) ** 2
    return bias


def glacier(p):
    """A snow plain broken by rock ridges and crevasses."""
    p.scatter(120, 296, 14, 3, "rock").band(210, 2, "deep", strict=False).band(150, 2, "deep", strict=False)
    return p


def collector(p):
    """The Hazudra fleet: hulls of ships in open space, the Collector's ship at the end."""
    p.rect(150, 296, 0, 3, "hull").rect(100, 230, 10, 13, "hull")
    p.calm(100, 296, 20, 4, 9).want_objects({"ship"}, 100, 296, 6, cols=(4, 9))
    return p.fill(0, 80, "space")


def crustgate(p):
    """Crust over lava: lava rivers, the gate's opening at the end."""
    p.river(120, 296, 3, "lava", centre=4, swing=2.5, period=50).river(100, 260, 2.5, "lava", centre=10, swing=2, period=40)
    return p.fill(0, 80, "lava", strict=False)


def the_core(p):
    """The gravitron core: vents and hot seams, the heart for the boss."""
    p.scatter(100, 296, 16, 2, "hot").river(90, 296, 1.6, "hot", centre=7, swing=5, period=70)
    return p


# map: the originals whose layer 1 the new map's tiles follow; layer2/layer3: those of the upper
# layers (none: empty); plan (with materials, base, kinds) or bias; waves, boss, ground: the
# originals whose waves, boss and ground enemies are used (episode, name): the ground enemies go
# with the map's own tileset, the waves come from another theme and the boss from a third (the
# user, 2026-10-09: "malo da začinimo igru"); look: the original whose start settings it takes;
# speeds: the layers' scroll speeds; wealth: about the credits its coins and gems are worth;
# gimmicks (compose.py, docs/plans/2026-10-09-epizoda-6.md 7): midboss ((episode, name), clock),
# ambush [(clock, (episode, name))], bursts [(from, to, factor)], dark and flip [(from, to)],
# couriers [(clock, "cube" or "warp:<level>")] (a secret data cube, or the warp orb to a secret level),
# hold (clock, seconds): a siege, the map stopped, waves round and round until the level timer ends.
LEVELS = [
    dict(name="DIG SITE", terrain=SAVARA_TERRAIN, shapes="y", song=33, seed=4, map=SAVARA, layer2=SAVARA[:4], plan=dig_site, **SAVARA_MATS,
         waves=[(3, "CAMANIS"), (3, "SAWBLADES")], boss=(3, "TYRIAN X"), ground=SAVARA[:4], boss_time=6100,
         look=(1, "SAVARA"), speeds=(1, 2, 3), wealth=12000,
         gimmicks=dict(ambush=[(2900, (3, "CAMANIS"))], bursts=[(4300, 4900, 2)], couriers=[(3600, "cube")])),
    dict(name="REEF", terrain=SAVARA_TERRAIN, shapes="y", song=21, seed=31, map=SAVARA, layer2=SAVARA[:4], plan=reef, **SAVARA_MATS,
         waves=[(2, "GYGES"), (2, "GRYPHON")], boss=(3, "IXMUCANE"), ground=SAVARA[:4], boss_time=5600,
         look=(4, "SAVARA IV"), speeds=(1, 2, 3), wealth=15000,
         gimmicks=dict(midboss=((2, "GYGES"), 2600), ambush=[(4400, (2, "GRYPHON"))], couriers=[(1800, "cube")])),
    dict(name="GREY MOON", terrain=ASTEROID_TERRAIN, shapes="z", song=1, seed=41, map=ASTEROIDS, layer2=ASTEROIDS[:2], layer3=ASTEROIDS[:2],
         plan=grey_moon, **ASTEROID_MATS, waves=[(4, "SAVARA IV"), (5, "SAVARA")], boss=(2, "TORM"),
         ground=ASTEROIDS, boss_time=6200, look=(1, "ASTEROID1"), wealth=18000,
         gimmicks=dict(bursts=[(1500, 2200, 2), (4700, 5300, 2)], midboss=((1, "ASTEROID2"), 3000),
                       couriers=[(4100, "warp:vault")]), ground_sheets=0),
    dict(name="DELI RUIN", terrain=DELI_TERRAIN, shapes="z", song=14, seed=91, map=DELI, layer2=DELI, layer3=DELI,
         waves=[(4, "ICE EXIT"), (4, "EYESPY")], boss=(3, "FLEET"), ground=DELI, boss_time=5800,
         look=(1, "DELIANI"), speeds=(1, 2, 2), wealth=21000,
         gimmicks=dict(dark=[(2000, 3400)], ambush=[(4300, (3, "New Deli"))], couriers=[(2900, "cube")],
                       hold=(1100, 40))),
    dict(name="ROOST", terrain=TORM_TERRAIN, shapes="x", song=28, seed=51, map=[(2, "TORM")], bias=roost_bias,
         waves=[(4, "LAVA RUN"), (4, "SURFACE")], boss=(1, "SAVARA"), ground=[(2, "TORM")], boss_time=6300,
         look=(2, "TORM"), wealth=24000,
         gimmicks=dict(ambush=[(2200, (4, "LAVA RUN"))], flip=[(3300, 4300)], couriers=[(2800, "cube")])),
    dict(name="DEEP ICE", terrain=ICE_TERRAIN, keep_map=True, shapes="w", song=14, seed=61, map=ICE, layer2=[(3, "IXMUCANE")], layer3=[(3, "IXMUCANE")],
         bias=zones([(0, 300, 0.3)], 61), waves=[(1, "DELIANI"), (3, "New Deli")], boss=(1, "ASSASSIN"),
         ground=ICE, boss_time=4600, look=(3, "IXMUCANE"), speeds=(1, 2, 2), wealth=27000,
         gimmicks=dict(dark=[(900, 2100)], ambush=[(3000, (3, "New Deli"))], couriers=[(1500, "cube")])),
    dict(name="GLACIER", terrain=SNOW_TERRAIN, shapes="w", song=4, seed=71, map=SNOW, layer2=[(4, "ICE EXIT")], plan=glacier, **SNOW_MATS,
         waves=[(5, "STATION"), (4, "EYESPY")], boss=(2, "BOTANY A"), ground=[(4, "ICE EXIT")], boss_time=5200,
         look=(4, "ICE EXIT"), speeds=(1, 2, 2), wealth=30000,
         gimmicks=dict(midboss=((4, "ICESECRET"), 2400), bursts=[(3700, 4300, 2)], couriers=[(3300, "cube")])),
    dict(name="COLLECTOR", terrain=SPACE_TERRAIN, shapes="w", song=29, seed=101, map=[(3, "FLEET")], layer2=[(3, "FLEET")],
         layer3=[(3, "FLEET")], plan=collector, **SPACE_MATS, waves=[(4, "SURFACE"), (4, "LAVA EXIT")],
         boss=(4, "BRAINIAC"), boss_time=5600, look=(3, "FLEET"), intensity=lambda f: 0.55 + 0.45 * f,
         wealth=34000, gimmicks=dict(bursts=[(1400, 2200, 2)], ambush=[(3200, (4, "LAVA EXIT"))],
                                     couriers=[(2600, "cube")])),
    dict(name="CRUSTGATE", terrain=LAVA_TERRAIN, shapes=")", song=17, seed=81, map=LAVA, layer2=LAVA, plan=crustgate, **LAVA_MATS,
         waves=[(2, "MARKERS"), (2, "MISTAKES")], boss=(4, "ICE EXIT"), ground=LAVA, boss_time=6000,
         look=(4, "LAVA RUN"), wealth=38000,
         gimmicks=dict(midboss=((5, "MINERS"), 1800), flip=[(3200, 4200)], bursts=[(4700, 5200, 2)],
                       couriers=[(2800, "cube")])),
    dict(name="THE CORE", terrain=CORE_TERRAIN, shapes=")", song=23, seed=111, map=[(4, "CORE")], layer2=[(4, "CORE")], plan=the_core,
         **CORE_MATS, waves=[(3, "FLEET"), (3, "GAUNTLET")], boss=(5, "FRUIT"), ground=[(4, "CORE")], boss_time=5600,
         look=(4, "CORE"), intensity=lambda f: 0.6 + 0.4 * f, wealth=45000,
         gimmicks=dict(dark=[(900, 2300)], midboss=((4, "CORE"), 3000), ambush=[(4700, (3, "CAMANIS"))])),
    # Seen from the side (side: the rocks along the edges, 1 asteroids, 2 crags; blank: a blank tile
    # of the tile set, open space for the stars). Their upper layers' maps are empty, but layer 3 still
    # carries the top layer's enemies: its speed is the one their waves' originals give it (GRYPHON's 3,
    # BRAINIAC's 1); at 0 most of them would stand above the screen and never come.
    dict(name="MIGRATION", side=1, blank=27, shapes="x", song=6, seed=131, waves=[(2, "GRYPHON"), (1, "SOH JIN")],
         boss=(2, "GEM WAR"), boss_time=6000, look=(2, "GRYPHON"), speeds=(1, 0, 3), wealth=26000,
         gimmicks=dict(couriers=[(3000, "cube")], ambush=[(4200, (2, "GRYPHON"))])),
    dict(name="GRAVITRON", side=2, blank=21, shapes=")", song=24, seed=141, waves=[(4, "BRAINIAC"), (3, "GAUNTLET")],
         boss=(4, "DREAD-NOT"), boss_time=6000, look=(4, "LAVA EXIT"), speeds=(1, 0, 1), wealth=40000,
         intensity=lambda f: 0.55 + 0.45 * f, gimmicks=dict(couriers=[(2500, "cube")], bursts=[(3400, 4200, 2)])),
    # Secret and bonus levels (story.py places them: VAULT behind GREY MOON's warp orb, INVADERS after
    # THE CORE).
    dict(name="VAULT", terrain=DELI_TERRAIN, shapes="z", song=18, seed=121, map=DELI, layer2=DELI, plan=vault, **DELI_MATS,
         waves=[(3, "BONUS"), (3, "New Deli")], boss=(1, "ASTEROID2"), ground=DELI, boss_time=6200,
         look=(1, "DELIANI"), speeds=(1, 2, 2), intensity=lambda f: 0.3 + 0.4 * f, wealth=60000,
         gimmicks=dict(couriers=[(2000, "cube"), (4400, "cube")], bursts=[(3000, 3600, 2)])),
    dict(name="INVADERS", kind="invaders", maps_of="collector", shapes="w", song=41, seed=3, look=(3, "FLEET")),
]


EVENTS_ONLY = False


def main(names):
    global EVENTS_ONLY
    if "--events" in names:
        # The maps as they are (their terrain built): only the events made again.
        EVENTS_ONLY = True
        names = [n for n in names if n != "--events"]
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
        level = make_invaders(design) if design.get("kind") == "invaders" else make(design)
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
