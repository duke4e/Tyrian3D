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


def maps_of(names, layer, rows=None):
    """The originals' maps of a layer; rows: (first, last) of layer 1's rows to take (a layer of 600 rows twice
    those), as ASSASSIN's map without the brown ground its level starts on."""
    maps = [originals()[n]["maps"][layer] for n in names]
    if rows:
        k = len(maps[0]) // 300
        maps = [m[rows[0] * k:rows[1] * k] for m in maps]
    return maps


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


def channel(seed, half=3.0, swing=2.5, period=90.0):
    """A bias for an upper layer of walls (GYGES' hive): walls along both sides, a channel winding up
    between them (only the layer's empty tiles), about half tiles either side of its middle."""
    def make_bias(model, grids):
        base = {sources.EMPTY}

        def bias(t, x, y):
            middle = 6.5 + swing * math.sin(y / period * 2 * math.pi + seed)
            d = abs(x - middle) - half - math.sin(y / 17.0 + seed)
            if -1.5 <= d <= 1.0:
                return 1.0  # (the walls' edges: any tile, so the walls can close and open)
            if t in base:
                return 1.0 if d < 0 else 0.15
            return 0.02 if d < 0 else 1.0
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
    if design.get("original_maps"):
        return finish(design, original_maps(*design["original_maps"]))
    grids = maps_of(design["map"], 0, design.get("map_rows"))
    model = Model(grids, max_tiles=LAYER_TILES[0])
    slug = name.lower().replace(" ", "_")
    if design.get("keep_map") or EVENTS_ONLY:
        # The map as it is (a map liked as it was): only the events are made again, and the layers
        # in remake (DEEP ICE's walls on layer 2, IXMUCANE's brown rock out of place over the ice).
        layers = json.load(open(os.path.join(OUT, f"{slug}.json")))["maps"]
        for k in design.get("remake", []) if not EVENTS_ONLY else []:
            layers[k - 1] = upper_layer(design, k - 1)
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
    layers = [layer1] + [upper_layer(design, k) for k in (1, 2)]
    return finish(design, layers)


def original_maps(episode, name):
    """An original level's three maps as shape numbers (its own map: its terrain, vegetation and clean ground are
    found by the same hash, the tiles' shape numbers)."""
    lv = waves.Source(episode, name).level
    out = []
    for k, (rows, columns) in enumerate(((300, 14), (600, 14), (600, 15))):
        table, raw = lv.map_sh[k], lv.maps[k]
        out.append([[table[raw[r * columns + c]] if raw[r * columns + c] < 128 else 0 for c in range(columns)]
                    for r in range(rows)])
    return out


def upper_layer(design, k):
    """Layer k + 1 (1 or 2: the upper layers) of a design."""
    rows, columns = 600, (14, 15)[k - 1]
    names = design.get(f"layer{k + 1}")
    if not names:
        return [[0] * columns for _ in range(rows)]
    source = design.get(f"layer{k + 1}_from", k + 1) - 1
    sources_ = maps_of(names, source, design.get("map_rows"))
    m = Model(sources_, max_tiles=LAYER_TILES[k] - 1)
    upper_bias = design.get(f"bias{k + 1}")
    width = min(columns, len(sources_[0][0]))  # (layer 2's 14 columns as layer 3: one left empty)
    grid, stats = generate(m, rows, width, design.get("seed", 1) + k,
                           bias=upper_bias(m, sources_) if upper_bias else None)
    print(design["name"], f"layer {k + 1}", dict(stats))
    return [row + [0] * (columns - width) for row in grid]


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


# The waves' density (enemies per 1000 clock, from the level's start to its boss) by the level's place in the
# episode (the user, 2026-11-03: "premalo protivnika - gledati progresiju od ep 1 do ep 5, pa ekstrapolirati"):
# the originals' median enemies per 1000 clock, whole levels, bosses and ground enemies too, are 28, 38, 41, 34 and
# 44 for episodes 1-5 (episode 6 had 12-27); episode 6 goes on from there, 38 at its first level to 52 at its last.
ORDER = ["DIG SITE", "REEF", "GREY MOON", "DELI RUIN", "ROOST", "MIGRATION", "DEEP ICE", "GLACIER", "COLLECTOR",
         "CRUSTGATE", "GRAVITRON", "THE CORE", "STARFALL", "THE GAUNTLET"]
SECRET_TARGET = {"VAULT": ("GREY MOON", 0.8)}  # (a secret level: as its parent, a little calmer)


def waves_target(name):
    """The waves' density (from, to) through the level (see ORDER), or None (the old pace)."""
    scale = 1.0
    if name in SECRET_TARGET:
        name, scale = SECRET_TARGET[name]
    if name not in ORDER:
        return None
    n = ORDER.index(name)
    total = 38 + 14 * n / (len(ORDER) - 1)
    # (The waves' own: the measured whole falls short of the pace by the stretches without waves, round an
    # ambush, a siege or a mid-level boss, and the waves too big for the start.)
    return (1.0 * total * scale, 1.5 * total * scale)


def kept_ground(design):
    """The ground enemies of the level as it was, when its map is kept (its terrain is levelled under them)."""
    path = os.path.join(OUT, f"{design['name'].lower().replace(' ', '_')}.json")
    if not (EVENTS_ONLY or design.get("keep_map")) or not os.path.exists(path):
        return None
    return [e for e in json.load(open(path))["events"] if e["type"] in (6, 10, 12)]


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
                                                ground_sheets=design.get("ground_sheets", 2), letter=letter,
                                                target=waves_target(name), keep_ground=kept_ground(design),
                                                need_sheets=design.get("need_sheets", ()))
    # The look of a chosen original level replaces the default settings at the start.
    look = waves.Source(*design.get("look", design["boss"]))
    # (Of the effects, lava, water and the spotlight: the blurs and the upside-down screen show as
    # flat slabs in the 3D view.)
    look_events = [dict(e) for e in look.events if e["t"] == 0 and e["type"] in LOOK_EVENTS and
                   not (e["type"] == 64 and e["d1"] not in (1, 2, 6)) and
                   not (e["type"] == 64 and e["d1"] in design.get("look_without_effects", ()))]
    if design.get("speeds"):
        look_events = [e for e in look_events if e["type"] not in (2, 3)]
        b1, b2, b3 = design["speeds"]
        look_events.insert(0, compose.event(0, 2, d1=b1, d2=b2, d3=b3))
    head = [e for e in events if e["t"] == 0 and e["type"] in (5, 13)]
    rest = [e for e in events if not (e["t"] == 0 and e["type"] in (2, 5, 8, 13))]
    level = dict(name=name, song=design["song"], shapes=letter, maps=layers, events=look_events + head + rest,
                 placements=placements, banks=banks, terrain=design.get("terrain", {}))
    if design.get("chase"):
        # Seen from behind the ship, the whole level (Tyrian3D event 205: the chase camera; no 2D look of its own).
        level["events"][1:1] = [compose.event(0, 205, d1=1)]
    if design.get("original_maps"):
        level["shared_maps"] = "%d:%s" % design["original_maps"]  # (its 3D assets: the original's)
        level["terrain"] = None
    if design.get("side"):
        # Stars on (the game's and the 3D view's deep ones), the view from the side with its rocks.
        level["events"] = [e for e in level["events"] if not (e["t"] == 0 and e["type"] in (1, 8, 9, 64))]
        level["events"][1:1] = [compose.event(0, 9), compose.event(0, 1, d1=0),
                                compose.event(0, 200, d1=1, d2=design["side"], d3=SIDE_AHEAD // 10)]
        level["terrain"] = None
        level["sideways"] = True
    return level


def boss_sheets(source):
    """The sheets an original's boss needs (its parts', and what they launch or leave)."""
    boss = source.boss()
    out = set()
    for e in boss["events"]:
        if e["type"] in waves.SPAWNS:
            out |= waves.sheets_of(source.enemies, e["d1"])
    return out - {21, 26}


def episode_enemies(but):
    """The enemies (episode, number) the episode's other levels make (as they stand in levels/): in the episode's
    item data already, with their weapons (whose slots, for other episodes' enemies, are full)."""
    out = set()
    for f in sorted(os.listdir(OUT)):
        level = json.load(open(os.path.join(OUT, f)))
        if level["name"] == but or not level.get("placements"):
            continue
        out |= {(e["ep"], e["d1"]) for e in compose.expand(level) if e["type"] in waves.SPAWNS and "ep" in e}
    return out


HOARD_LEAD = 400  # clock from a fight's sheets to its boss (two of its own level's waves in between)
HOARD_GAP = 150   # clock from a boss gone to the next fight's sheets
HOARD_APPROACH = 500  # clock of a boss's approach kept before the map stops (some bring the whole stretch of their level
                       # before it: HARVEST's 9580, UNDERDELI's, CAMANIS', CORAL's: the level's clock runs out at 65535)


def make_hoard(design):
    """THE HOARD, the episode's last level (the user, 2026-11-03: "level samo sa svim bossevima, jedan za drugim + na
    kojemu idemo all in - da uguramo sve što igra nudi kao one off mehanike"): over open space, the Collector's
    hoard, its bosses one after another, each fought as a mid-level boss (the map stops, its pattern loops until it
    is gone), two waves of its own level before it, and with each a mechanic of the game's (fights: flip, dark, side,
    chase; bursts before; a siege before the last), the sheets changed for each (event 5: four at a time), the last
    one the level's boss."""
    rnd = random.Random(design["seed"])
    speeds = tuple(design["speeds"])
    events, placements = [], []
    t, first, banks = 150, None, None
    known = episode_enemies(design["name"])
    for fight in design["fights"]:
        source = waves.Source(*fight["boss"])
        sheets = boss_sheets(source)
        # (its waves those of the level of the episode it is fought in: their enemies, and their weapons, are in
        # the episode already; none of their scenery, SURFACE's rock arches: they floated in its open space)
        own = [(s, i, w) for s in (waves.Source(*k) for k in fight["waves"])
               for i, w in enumerate(s.waves()) if 3 <= w["count"] <= 10 and w["length"] <= 400 and
               all((s.episode, e["d1"]) in known and s.enemies.get(e["d1"], {}).get("armor", 0) > 0
                   for e in w["events"] if e["type"] in waves.SPAWNS)]
        for b, _ in Counter(b for _, _, w in own for b in w["banks"]).most_common():
            if len(sheets) < 4:
                sheets.add(b)
        fitting = [(s, i, w) for s, i, w in own if set(w["banks"]) <= sheets | {21, 26}]
        banks = sorted(sheets)[:4]
        load = compose.event(t, 5, *(banks + [0] * 4)[:2], d3=(banks + [0] * 4)[2], d4=(banks + [0] * 4)[3])
        if first is None:
            first = dict(load, t=0)
        else:
            events.append(load)
        if fight.get("burst"):
            events += [compose.event(t + 10, 16, d1=compose.MESSAGE_AFTERBURNER, d2=30),
                       compose.event(t + 90, 2, d1=speeds[0] * 2, d2=speeds[1] * 2, d3=speeds[2] * 2),
                       compose.event(t + HOARD_LEAD - 60, 2, d1=speeds[0], d2=speeds[1], d3=speeds[2])]
        for k in range(2 if fitting else 0):
            s, index, w = rnd.choice(fitting)
            placements.append(dict(kind="wave", episode=s.episode, name=s.name, index=index,
                                   start=t + 40 + k * 200, drop=compose.pick_coin(rnd, 250)))
        at = t + HOARD_LEAD
        if fight.get("siege"):
            # A siege first: the map stops, the waves come round until the level timer runs out.
            loop_from, loop_to = at + 20, at + compose.HOLD_LOOP
            exit_ = loop_to + 10
            for k in range(3):
                s, index, w = rnd.choice(fitting)
                placements.append(dict(kind="wave", episode=s.episode, name=s.name, index=index,
                                       start=loop_from + k * (compose.HOLD_LOOP // 3)))
            events += [compose.event(at - 80, 16, d1=compose.MESSAGE_DANGER, d2=30), compose.event(at, 2),
                       compose.event(at, 53), compose.event(at, 67, d1=1, d2=exit_, d3=fight["siege"] * 35 // 100),
                       compose.event(loop_to, 54, d1=loop_from), compose.event(exit_ - 2, 16, d1=4, d2=30),
                       compose.event(exit_, 2, d1=speeds[0], d2=speeds[1], d3=speeds[2]), compose.event(exit_, 53, d1=99)]
            at = exit_ + 250
        if fight.get("last"):
            placements.append(dict(kind="boss", episode=source.episode, name=source.name, start=at))
            break
        stop, loop_from, loop_to = compose.midboss_span(source)
        trim = max(0, stop - HOARD_APPROACH)
        stop, loop_from, loop_to = stop - trim, loop_from - trim, loop_to - trim
        placements.append(dict(kind="midboss", episode=source.episode, name=source.name, start=at, trim=trim,
                               loop=[stop, loop_from, loop_to], speeds=list(speeds),
                               **{k: True for k in ("flip", "dark", "side", "chase") if fight.get(k)}))
        t = at + loop_to + 2 + HOARD_GAP
    look = waves.Source(*design["look"])
    look_events = [dict(e) for e in look.events if e["t"] == 0 and e["type"] in LOOK_EVENTS and
                   e["type"] not in (1, 2, 3, 8, 9, 64)]
    head = [compose.event(0, 2, d1=speeds[0], d2=speeds[1], d3=speeds[2]), first, compose.event(0, 13),
            compose.event(0, 9), compose.event(0, 1, d1=0)]
    blank = design["blank"]
    return dict(name=design["name"], song=design["song"], shapes=design["shapes"],
                maps=[[[blank] * 14 for _ in range(300)], [[0] * 14 for _ in range(600)], [[0] * 15 for _ in range(600)]],
                events=look_events + head + sorted(events, key=lambda e: e["t"]) + [compose.event(compose.CLOCK_END - 50, 11)],
                placements=placements, banks=banks, terrain=None, open_space=True)


# --- The levels ---------------------------------------------------------------------------------
# map: the originals whose layer 1 the new map's tiles follow; layer2/layer3: those of the upper
# layers (none: empty); bias: the plan; waves, boss, ground: the originals whose waves, boss and
# ground enemies are used (episode, name); look: the original whose start settings it takes;
# speeds: the layers' scroll speeds (layer 3 at most 2 when it has things on it: at 3 it runs out
# before the boss).



# Materials by tileset (reference colours; "space" is the blank tiles), the base material objects
# stand on, and the kinds of objects by their main material. (The looks the episode's levels take are
# the originals' least used ones, the user, 2026-11-03: "dosadni tilesetovi - ... koristiti one koji se
# najmanje put koriste", "ne moraju biti nužno kompletni tilesetovi, ima lookova koji rade neku
# distinkciju": of the originals' maps grouped by the tiles they show, SAVARA's look has five levels,
# the asteroids' nine, DELIANI's three; SURFACE's desert, CORAL's reef, ASSASSIN's grey rock,
# BRAINIAC's halls, GYGES' hive and SIDE EXIT's crags one to three.)
DESERT_MATS = dict(materials={"sand": (140, 117, 94), "rock": (67, 68, 62), "shade": (45, 36, 15)},
                   base="sand", kinds={"rock": "rock", "shade": "rock"})
REEF_MATS = dict(materials={"space": (0, 0, 1), "reef": (60, 108, 130), "coral": (142, 59, 47)},
                 base="space", kinds={"reef": "reef", "coral": "reef"})
MOON_MATS = dict(materials={"space": (0, 0, 0), "rock": (98, 96, 90), "pale": (159, 148, 139), "dust": (77, 66, 52)},
                 base="space", kinds={"rock": "rock", "pale": "rock", "dust": "rock"})
HALL_MATS = dict(materials={"space": (0, 0, 0), "wall": (78, 62, 88), "slate": (48, 59, 68)},
                 base="space", kinds={"wall": "building", "slate": "building"})
ICE_MATS = dict(materials={"cliff": (48, 29, 6), "ice": (105, 160, 171), "deep": (73, 112, 138), "dark": (31, 63, 85)},
                base="cliff", kinds={"ice": "ice", "deep": "ice", "dark": "ice"})
SNOW_MATS = dict(materials={"snow": (105, 160, 171), "rock": (80, 80, 80), "deep": (73, 112, 138)},
                 base="snow", kinds={"rock": "rock", "deep": "rock"})
SPACE_MATS = dict(materials={"space": (0, 0, 0), "hull": (50, 48, 45), "light": (90, 85, 80)},
                  base="space", kinds={"hull": "ship", "light": "ship"})
CORE_MATS = dict(materials={"floor": (74, 34, 22), "hot": (130, 22, 8), "dark": (40, 15, 10)},
                 base="floor", kinds={"hot": "vent", "dark": "vent"})

# The 3D terrain of the new maps (tools/terrain/levels.json settings; "materials": heights by the
# surfaces' colours, tools/terrain/make_terrain.py), by tileset.
DESERT_TERRAIN = {"classes": 6, "heights": {}, "palms": True, "materials": {"#8c755e": 0, "#43443e": 16, "#2d240f": 12}}
REEF_TERRAIN = {"classes": 6, "heights": {}, "void": "hole", "detail": 6, "softness": 4, "roads": False,
                "materials": {"#3c6c82": 10, "#8e3b2f": "~"}}
ASTEROID_TERRAIN = {"classes": 6, "heights": {}, "void": "hole"}
DELI_TERRAIN = {"classes": 6, "heights": {}, "materials": {"#0c1926": 0, "#1c2935": 10, "#162330": "~"}}
HALL_TERRAIN = {"classes": 6, "heights": {}, "void": "hole", "solid_upper": [2]}
HIVE_TERRAIN = {"classes": 6, "heights": {}, "void": -36, "solid_upper": True}
ICE_TERRAIN = {"classes": 6, "heights": {}, "rolling": 6, "solid_upper": True}
SNOW_TERRAIN = {"classes": 6, "heights": {}, "rolling": 10}
SPACE_TERRAIN = {"classes": 6, "heights": {}, "void": "hole"}
CRAG_TERRAIN = {"classes": 6, "heights": {}, "rolling": 12, "solid_upper": True}
CORE_TERRAIN = {"classes": 6, "heights": {}, "rolling": 10, "solid_upper": True}

DESERT = [(4, "SURFACE"), (4, "DESERTRUN")]
DELI = [(1, "DELIANI"), (3, "New Deli")]
HALLS = [(4, "BRAINIAC")]
ICE = [(3, "IXMUCANE"), (3, "CAMANIS")]
SNOW = [(4, "ICE EXIT"), (3, "CAMANIS")]


def dig_site(p):
    """Desert (SURFACE's): outcrops of rock thickening up the level, the excavation's walls across the
    sand, the dig site: a field of outcrops in a walled pit, open sand for the boss."""
    p.scatter(210, 296, 16, 2, "rock").scatter(140, 210, 22, 2, "rock").scatter(150, 296, 24, 1, "shade")
    p.band(250, 2, "rock", 0, 6, strict=False).band(226, 2, "rock", 7, 13, strict=False)
    p.band(178, 2, "rock", 0, 13, strict=False).band(128, 2, "rock", 0, 13, strict=False)
    p.scatter(132, 176, 14, 2, "shade", cols=(1, 12))
    p.calm(95, 124, 1).want_objects({"rock"}, 95, 124, 5)
    return p.fill(0, 88, "sand")


def reef(p):
    """A reef (CORAL's): walls of reef along both sides, coral on them, islets of reef in the deep
    water between, open water for the boss."""
    p.coast(100, 296, -1, 4, "reef").coast(100, 296, 1, 4, "reef")
    p.blob(250, 7, 10, 2.5, "reef").blob(170, 6, 8, 3, "reef")
    p.scatter(110, 296, 14, 2, "coral", cols=(0, 13))
    p.calm(200, 226, 497, 4, 9).want_objects({"reef"}, 200, 226, 2, cols=(4, 9))
    p.calm(120, 150, 497, 4, 9).want_objects({"reef"}, 120, 150, 2, cols=(4, 9))
    return p.fill(0, 92, "space")


def grey_moon(p):
    """The grey moon (ASSASSIN's rock): fields of rock thickening, a great mass in the middle, open
    space for the boss."""
    p.scatter(200, 295, 10, 3, "rock").scatter(120, 200, 18, 3, "rock")
    p.blob(160, 7, 18, 4, "rock")
    p.calm(230, 296, 1).want_objects({"rock"}, 230, 296, 4)
    p.calm(90, 140, 1).want_objects({"rock"}, 90, 140, 4)
    return p.fill(0, 80, "space")


def vault(p):
    """The grey moon's vault (BRAINIAC's halls): strongrooms of walls either side of shafts, blocks
    of slate along them, a hall at the end."""
    for k, r0 in enumerate(range(50, 290, 46)):
        if k % 2:
            p.rect(r0, r0 + 28, 0, 5, "wall").rect(r0 + 8, r0 + 36, 9, 13, "wall")
        else:
            p.rect(r0, r0 + 30, 0, 3, "wall").rect(r0 + 4, r0 + 26, 6, 13, "wall")
        p.scatter(r0, r0 + 36, 4, 1, "slate", cols=(1, 12))
    return p.fill(0, 40, "space")


def glacier(p):
    """A snow plain broken by rock ridges and crevasses."""
    p.scatter(120, 296, 14, 3, "rock").band(210, 2, "deep", strict=False).band(150, 2, "deep", strict=False)
    return p


def collector(p):
    """The Hazudra fleet: hulls of ships in open space, the Collector's ship at the end."""
    p.rect(150, 296, 0, 3, "hull").rect(100, 230, 10, 13, "hull")
    p.calm(100, 296, 20, 4, 9).want_objects({"ship"}, 100, 296, 6, cols=(4, 9))
    return p.fill(0, 80, "space")


def the_core(p):
    """The gravitron core: vents and hot seams, the heart for the boss."""
    p.scatter(100, 296, 16, 2, "hot").river(90, 296, 1.6, "hot", centre=7, swing=5, period=70)
    return p


# map: the originals whose layer 1 the new map's tiles follow; layer2/layer3: those of the upper
# layers (none: empty; layerN_from: the originals' layer they follow, if not the same); plan (with
# materials, base, kinds) or bias; waves, boss, ground: the
# originals whose waves, boss and ground enemies are used (episode, name): the ground enemies go
# with the map's own tileset, the waves come from another theme and the boss from a third (the
# user, 2026-10-09: "malo da začinimo igru"); look: the original whose start settings it takes;
# speeds: the layers' scroll speeds; wealth: about the credits its coins and gems are worth;
# gimmicks (compose.py, docs/plans/2026-10-09-epizoda-6.md 7): midboss ((episode, name), clock),
# ambush [(clock, (episode, name))], bursts [(from, to, factor)] or "map" (bursts_map of them, along the
# map's most open stretches), dark [(from, to)] or "map" (over its darkest stretch), "midboss" or "hold"
# (while the mid-level boss or the siege is fought), flip [(from, to)] or "boss"/"midboss" (upside down
# while that boss is fought),
# couriers [(clock, "cube" or "warp:<level>")] (a secret data cube, or the warp orb to a secret level),
# hold (clock, seconds): a siege, the map stopped, waves round and round until the level timer ends.
# THE HOARD's and HOARD II's fights (the user, 2026-11-04: "zadnji level, nek je sa baš svim bossevima iz igre
# (uključujući i njihove obrane i konfiguracije)"; two levels: an event's clock it jumps to (54, 70) is a signed
# 16-bit number, so a level's events end by 32767): every boss of episodes 1-5 (the originals' levels with one, those of the same
# boss once: TYRIAN's and TYRIAN X's, SAVARA's and SAVARA Y's, TORM's and the BOTANYs', ICE EXIT's and ICESECRET's,
# episode 5's two SAVARAs'), each with its own stage's defences and pattern (compose.midboss_span), in the episodes'
# order, BRAINIAC's last after a siege; a mechanic of the game's with every other one (lights out, upside down, from
# behind the ship, from the side, a rush before it); their waves those of the episode's levels the episode has.
HOARD_BOSSES = [(1, "TYRIAN"), (1, "ASTEROID1"), (1, "ASTEROID2"), (1, "SAVARA"), (1, "DELIANI"), (1, "ASSASSIN"),
                (1, "SAVARA V"), (2, "TORM"), (2, "GYGES"), (2, "GEM WAR"), (3, "IXMUCANE"), (3, "CAMANIS"),
                (3, "FLEET"), (3, "New Deli"), (4, "SURFACE"), (4, "CORE"), (4, "ICE EXIT"), (4, "HARVEST"),
                (4, "UNDERDELI"), (4, "SAVARA IV"), (4, "DREAD-NOT"), (4, "LAVA EXIT"), (4, "APPROACH"),
                (5, "ASTEROIDS"), (5, "SAVARA"), (5, "AST ROCK"), (5, "MINERS"), (5, "CORAL"), (5, "FRUIT")]
HOARD_MECHANICS = [{}, dict(dark=True), {}, dict(flip=True), {}, dict(chase=True), {}, dict(side=True), {},
                   dict(burst=True)]
HOARD_WAVES = [(3, "CAMANIS"), (2, "GYGES"), (4, "SAVARA IV"), (4, "SURFACE"), (3, "BONUS"), (4, "LAVA EXIT")]


HOARD_SPLIT = 14  # THE HOARD: episodes 1-3's bosses, New Deli's its last; HOARD II: episodes 4-5's, then BRAINIAC's


def hoard_fights(part):
    fights = [dict(boss=b, waves=[HOARD_WAVES[k % len(HOARD_WAVES)]], **HOARD_MECHANICS[k % len(HOARD_MECHANICS)])
              for k, b in enumerate(HOARD_BOSSES)]
    if part == 1:
        return fights[:HOARD_SPLIT - 1] + [dict(fights[HOARD_SPLIT - 1], last=True)]
    return fights[HOARD_SPLIT:] + [dict(boss=(4, "BRAINIAC"), waves=[(4, "SURFACE"), (4, "LAVA EXIT")], siege=30, last=True)]


LEVELS = [
    dict(name="DIG SITE", terrain=DESERT_TERRAIN, shapes=")", song=33, seed=4, map=DESERT, plan=dig_site, **DESERT_MATS,
         waves=[(3, "CAMANIS"), (3, "SAWBLADES")], boss=(3, "TYRIAN X"), ground=DESERT, boss_time=6100,
         look=(4, "SURFACE"), speeds=(1, 2, 3), wealth=12000,
         gimmicks=dict(ambush=[(2900, (3, "CAMANIS"))], bursts="map", couriers=[(3600, "cube")])),
    dict(name="REEF", terrain=REEF_TERRAIN, shapes="z", song=21, seed=31, map=[(5, "CORAL")], plan=reef, **REEF_MATS,
         waves=[(2, "GYGES"), (2, "GRYPHON")], boss=(3, "IXMUCANE"), ground=[(5, "CORAL")], boss_time=5600,
         look=(5, "CORAL"), speeds=(1, 2, 3), wealth=15000,
         gimmicks=dict(midboss=((2, "GYGES"), 2600), ambush=[(4400, (2, "GRYPHON"))], couriers=[(1800, "cube")])),
    # (ASSASSIN's rock; not its ice, layer 2, which the 3D view shows as clouds over most of the screen; the look,
    # its star field, ASTEROID1's: ASSASSIN's has its spotlight.)
    dict(name="GREY MOON", terrain=ASTEROID_TERRAIN, shapes="z", song=1, seed=41, map=[(1, "ASSASSIN")], map_rows=(0, 272),
         plan=grey_moon, **MOON_MATS, waves=[(4, "SAVARA IV"), (5, "SAVARA")], boss=(2, "TORM"),
         ground=[(1, "ASSASSIN")], boss_time=6200, look=(1, "ASTEROID1"), wealth=18000,
         gimmicks=dict(bursts="map", bursts_map=2, midboss=((1, "ASTEROID2"), 3000),
                       couriers=[(4100, "warp:vault")]), ground_sheets=0),
    dict(name="DELI RUIN", terrain=DELI_TERRAIN, shapes="z", song=14, seed=91, map=DELI, layer2=DELI, layer3=DELI,
         waves=[(4, "ICE EXIT"), (4, "EYESPY"), (3, "FLEET")], boss=(3, "FLEET"), ground=DELI, boss_time=5800,
         look=(1, "DELIANI"), speeds=(1, 2, 2), wealth=21000, need_sheets=[15],
         gimmicks=dict(dark="hold", ambush=[(4300, (3, "New Deli"))], couriers=[(2900, "cube")],
                       hold=(1100, 40))),
    # (GYGES' hive: its floor, the islands of hive over it on layer 2 and its walls on layer 3.)
    dict(name="ROOST", terrain=HIVE_TERRAIN, shapes="x", song=28, seed=51, map=[(2, "GYGES")], layer2=[(2, "GYGES")],
         layer3=[(2, "GYGES")], bias2=zones([(0, 600, 0.25)], 52, scale=1.5), bias3=channel(53),
         waves=[(4, "LAVA RUN"), (4, "SURFACE")], boss=(1, "SAVARA"), ground=[(2, "GYGES")],
         boss_time=6300, look=(2, "GYGES"), speeds=(1, 2, 2), wealth=24000,
         gimmicks=dict(ambush=[(2200, (4, "LAVA RUN"))], flip="boss", couriers=[(1400, "special:49"), (2800, "cube")])),
    # (Its walls on layer 2 of ICE EXIT's ice, along the sides as IXMUCANE's brown rock was: the user, 2026-11-02,
    # "zamjeniti top layer (s ixmucane) na nešto što bolje paše ledenoj pozadini"; its floes on layer 3 kept.)
    dict(name="DEEP ICE", terrain=dict(ICE_TERRAIN, solid_upper=[2]), keep_map=True, remake=[2], shapes="w", song=14, seed=61,
         map=ICE, layer2=[(4, "ICE EXIT")], bias2=channel(62, half=4.5), layer3=[(4, "ICE EXIT")], layer3_from=2,
         bias=zones([(0, 300, 0.3)], 61), waves=[(1, "DELIANI"), (3, "New Deli")], boss=(1, "ASSASSIN"),
         ground=ICE, boss_time=4600, look=(3, "IXMUCANE"), speeds=(1, 2, 2), wealth=27000, need_sheets=[10],
         gimmicks=dict(dark="map", ambush=[(3000, (3, "New Deli"))], couriers=[(1500, "cube")])),
    dict(name="GLACIER", terrain=SNOW_TERRAIN, shapes="w", song=4, seed=71, map=SNOW, layer2=[(4, "ICE EXIT")], plan=glacier, **SNOW_MATS,
         waves=[(5, "STATION"), (4, "EYESPY")], boss=(2, "BOTANY A"), ground=[(4, "ICE EXIT")], boss_time=5200,
         look=(4, "ICE EXIT"), speeds=(1, 2, 2), wealth=30000,
         gimmicks=dict(midboss=((4, "ICESECRET"), 2400), bursts="map", couriers=[(3300, "cube")])),
    dict(name="COLLECTOR", terrain=SPACE_TERRAIN, shapes="w", song=29, seed=101, map=[(3, "FLEET")], layer2=[(3, "FLEET")],
         layer3=[(3, "FLEET")], plan=collector, **SPACE_MATS, waves=[(4, "SURFACE"), (4, "LAVA EXIT")],
         boss=(4, "BRAINIAC"), boss_time=5600, look=(3, "FLEET"), intensity=lambda f: 0.55 + 0.45 * f,
         wealth=34000, gimmicks=dict(bursts="map", ambush=[(3200, (4, "LAVA EXIT"))],
                                     couriers=[(2600, "cube")])),
    # (SIDE EXIT's crust: its glowing veins, the crags over them on layer 2; without its lava effect: with it the
    # game at the default detail, processorType 3, leaves layer 2 out, tyrian2.c's "smoothies[1-1]".)
    dict(name="CRUSTGATE", terrain=CRAG_TERRAIN, shapes=")", song=17, seed=81, map=[(4, "SIDE EXIT")], layer2=[(4, "SIDE EXIT")],
         bias2=zones([(0, 600, 0.4)], 82, scale=1.5), look_without_effects=(1,),
         waves=[(2, "MARKERS"), (2, "MISTAKES")], boss=(4, "ICE EXIT"), ground=[(4, "SIDE EXIT")], boss_time=6000,
         look=(4, "SIDE EXIT"), wealth=38000,
         gimmicks=dict(midboss=((5, "MINERS"), 1800), flip="midboss", bursts="map",
                       couriers=[(2800, "cube")])),
    dict(name="THE CORE", terrain=CORE_TERRAIN, shapes=")", song=23, seed=111, map=[(4, "CORE")], layer2=[(4, "CORE")], plan=the_core,
         **CORE_MATS, waves=[(3, "FLEET"), (3, "GAUNTLET")], boss=(5, "FRUIT"), ground=[(4, "CORE")], boss_time=5600,
         look=(4, "CORE"), intensity=lambda f: 0.6 + 0.4 * f, wealth=45000,
         gimmicks=dict(dark="midboss", midboss=((4, "CORE"), 3000), ambush=[(4700, (3, "CAMANIS"))])),
    # Seen from the side (side: the rocks along the edges, 1 asteroids, 2 crags; blank: a blank tile
    # of the tile set, open space for the stars). Their upper layers' maps are empty, but layer 3 still
    # carries the top layer's enemies: its speed is the one their waves' originals give it (GRYPHON's 3,
    # BRAINIAC's 1); at 0 most of them would stand above the screen and never come.
    dict(name="MIGRATION", side=1, blank=27, shapes="x", song=6, seed=131, waves=[(2, "GRYPHON"), (1, "SOH JIN")],
         boss=(2, "GEM WAR"), boss_time=6000, look=(2, "GRYPHON"), speeds=(1, 0, 3), wealth=26000,
         gimmicks=dict(couriers=[(3000, "cube")], ambush=[(4200, (2, "GRYPHON"))])),
    dict(name="GRAVITRON", side=2, blank=21, shapes=")", song=24, seed=141, waves=[(4, "BRAINIAC"), (3, "GAUNTLET")],
         boss=(4, "DREAD-NOT"), boss_time=6000, look=(4, "LAVA EXIT"), speeds=(1, 0, 1), wealth=40000,
         intensity=lambda f: 0.55 + 0.45 * f, gimmicks=dict(couriers=[(2500, "cube")], bursts="map")),
    # Secret and bonus levels (story.py places them: VAULT behind GREY MOON's warp orb, INVADERS after
    # THE CORE).
    dict(name="VAULT", terrain=HALL_TERRAIN, shapes=")", song=18, seed=121, map=HALLS, layer2=HALLS, layer3=HALLS, plan=vault,
         **HALL_MATS, waves=[(3, "BONUS"), (3, "New Deli")], boss=(1, "ASTEROID2"), ground=HALLS, boss_time=6200,
         look=(4, "BRAINIAC"), speeds=(1, 2, 2), intensity=lambda f: 0.3 + 0.4 * f, wealth=60000,
         gimmicks=dict(couriers=[(2000, "cube"), (4400, "cube")], bursts="map")),
    dict(name="INVADERS", kind="invaders", maps_of="collector", shapes="w", song=41, seed=3, look=(3, "FLEET")),
    # The episode's last two (the user, 2026-11-03: "ovo bi mogla biti zadnja 2 levela ep 6: starfox like level - ne
    # treba nužno imati 2d varijantu; level samo sa svim bossevima, jedan za drugim + ... all in"). STARFALL: the
    # Collector's fleet chased low over Tyrian's farmland (HARVEST's own maps and 3D assets), seen from behind the
    # ship the whole way (event 205): squadrons from ahead, rushes along the open fields, the dragons at the end
    # (GEM WAR's, as in MIGRATION; waves of episode 5's levels: the episode's slots for other episodes' enemies'
    # weapons are full, those that fire others most of all, below 150).
    dict(name="STARFALL", original_maps=(4, "HARVEST"), chase=True, shapes="z", song=12, seed=151,
         waves=[(5, "STATION"), (5, "SAVARA")], boss=(2, "GEM WAR"), boss_time=6000, look=(4, "HARVEST"),
         speeds=(1, 2, 3), wealth=50000, intensity=lambda f: 0.6 + 0.4 * f,
         gimmicks=dict(bursts="map", bursts_map=2, ambush=[(3900, (5, "STATION"))])),
    # THE HOARD: see make_hoard.
    dict(name="THE HOARD", kind="hoard", shapes=")", blank=21, song=35, seed=161, look=(4, "LAVA EXIT"),
         speeds=(1, 2, 1), fights=hoard_fights(1)),
    dict(name="HOARD II", kind="hoard", shapes=")", blank=21, song=35, seed=171, look=(4, "LAVA EXIT"),
         speeds=(1, 2, 1), fights=hoard_fights(2)),
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
        level = make_invaders(design) if design.get("kind") == "invaders" else \
            make_hoard(design) if design.get("kind") == "hoard" else make(design)
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
