#!/usr/bin/env python3
"""Episode 6 in the game's own formats (docs/plans/2026-10-09-epizoda-6.md), written to
assets/content/episode6: tyrian6.lvl (the levels and the episode's item data), levels6.dat (the
script: shops, levels, texts) and cubetxt6.dat (the data cubes). The game reads them as it reads
episodes 1-5 (src/file.c finds them in the content directory).

usage: tools/content/episode6/build.py

The levels are tools/content/episode6/levels/*.json (made by generate.py: new maps of tile
numbers and events naming enemies by the episode they are from); this brings those enemies into
the episode's item data (enemydata.py: episode 5's, with what other episodes' enemies need) and
writes the binary files. Standard library only: it runs at build time.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import compose  # noqa: E402
import enemydata  # noqa: E402
import tyrformat as tf  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "content", "episode6")
LEVELS_DIR = os.path.join(HERE, "levels")

# The episode's levels in order (their json files in levels/).
LEVELS = ["dig_site"]
ENEMY_D1 = {6, 7, 10, 12, 15, 17, 18, 23, 32, 56, 33, 45, 59, 68}

# The shop before the first level: lines of ]I (ships, front and rear guns, generators, engine,
# left and right sidekicks, armor, shields), as the episodes write them.
FIRST_SHOP = [
    " Ship   3 14 16",
    " WeapF  1 3 13 48 49",
    " WeapR  0 9 10 52 53",
    " Power  3 4",
    " Engine 1",
    " Opt1   0 6 29 33",
    " Opt2   0 6 29 34",
    " Armor  1 2 3",
    " Shield 3 5 8",
]

ENDING = [
    "The grey books are safe in Graphim Arugo's vault, and the",
    "dig site on Savara is quiet again.",
    "",
    "The proximity bomb on your ship has fallen silent too. For now.",
    "",
    "To be continued...",
]

HINTS = [
    ["Did you know?", "Tyrian purple, the dye, took thousands of sea snails", "for a single gram."],
    ["Did you know?", "Purple orbs are experience in a rogue run."],
    ["Did you know?", "Repulsors push you away; magnets pull you in."],
]


def script(levels):
    lines = []
    # 1: the shop. ]G: the planet map's origin, one destination (planet 4, section 2).
    lines += ["*1 SECTION - Episode 6 start", "]![ 00", "]G[ 04 1 04 002", "]I["] + FIRST_SHOP + [""]
    section = 2
    for i, level in enumerate(levels):
        lines += [f"*{section} SECTION - {level['name']}", tf.level_line(section + 1, level["name"], level["song"], i + 1), ""]
        section += 1
    # The ending, then the end of the episode (]Q reads hints after it, as many as E5 has).
    lines += [f"*{section} SECTION - Episode 6 Ending", "]M 008[", "]P 005[", "]Wn 03["] + ENDING + ["#", "]F[",
                                                                                                     "]Q[", "#"]
    for k in range(9):
        lines += HINTS[k % len(HINTS)] + ["#"]
    lines += [""]
    return lines


def cubes():
    return ["*01 14", "HOLO NEWS - GD3 v123-07-11", "News",
            "~Grey~ ~Books~ ~Dig~ ~Attacked~",
            "The archaeological site of ~Graphim~ ~Arugo~ on Savara, where the grey books from",
            "the folklore planet ~Earth~ surfaced, was attacked last night by unmarked ships.",
            "*"]


def tables(maps):
    """Each layer's shape table (128 shape numbers) and its map bytes. Layer 1 has 72 tiles,
    layer 2 71 and an empty one (71), layer 3 70 and empty ones (70, 71)."""
    out = []
    for k, grid in enumerate(maps):
        empty = {0: None, 1: 71, 2: 70}[k]
        shapes = sorted({s for row in grid for s in row if s})
        limit = (72, 71, 70)[k]
        assert len(shapes) <= limit, f"layer {k + 1}: {len(shapes)} tiles (at most {limit})"
        index = {s: i for i, s in enumerate(shapes)}
        # Every entry a real shape number (JE_loadMap sets a tile only for those).
        table = shapes + [shapes[0] if shapes else 1] * (128 - len(shapes))
        raw = bytearray()
        for row in grid:
            for s in row:
                raw.append(index[s] if s else (empty if empty is not None else 0))
        out.append((table, bytes(raw)))
    return out


def level_entries(level, importer):
    """The level's two entries: its header and events, and its maps."""
    letter = level["shapes"].upper().encode("latin1")
    head = letter + letter + struct.pack("<3H", 1, 1, 1) + struct.pack("<H", 0)
    events = level["events"]
    body = struct.pack("<H", len(events))
    for e in events:
        d1 = e["d1"]
        if e["type"] in ENEMY_D1 and "ep" in e:
            d1 = importer.enemy(e["ep"], d1)
        body += struct.pack("<HBhhbbbB", e["t"], e["type"], d1, e["d2"], e["d3"], e["d5"], e["d6"], e["d4"])
    maps = b""
    raws = b""
    for table, raw in tables(level["maps"]):
        maps += struct.pack(">128H", *table)
        raws += raw
    return [head + body, maps + raws]


def main():
    os.makedirs(OUT, exist_ok=True)
    levels = [json.load(open(os.path.join(LEVELS_DIR, f"{name}.json"))) for name in LEVELS]
    for level in levels:
        level["events"] = compose.expand(level)
    # Episode 5's enemies the levels use as they are keep their weapons; the others' weapons may go
    # to enemies brought in from other episodes.
    probe = enemydata.Importer()
    kept = set()
    for level in levels:
        for e in level["events"]:
            if e["type"] in ENEMY_D1 and "ep" in e and e["d1"] > 0:
                if e["ep"] == 5 or probe._same_enemy(e["ep"], e["d1"]):
                    kept.add(e["d1"])
    importer = enemydata.Importer(kept)
    entries = []
    for level in levels:
        entries += level_entries(level, importer)
    entries.append(bytes(importer.data))
    tf.write_level_file(os.path.join(OUT, "tyrian6.lvl"), entries)
    tf.write_strings(os.path.join(OUT, "levels6.dat"), script(levels))
    tf.write_strings(os.path.join(OUT, "cubetxt6.dat"), cubes())
    print(f"{OUT}: {len(levels)} levels, {len(importer.enemy_map)} enemies and {len(importer.weapon_map)} weapons "
          f"brought in")
    return 0


if __name__ == "__main__":
    sys.exit(main())
