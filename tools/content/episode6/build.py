#!/usr/bin/env python3
"""Episode 6 in the game's own formats (docs/plans/2026-10-09-epizoda-6.md), written to
assets/content/episode6: tyrian6.lvl (the levels and the episode's item data), levels6.dat (the
script: shops, levels, texts) and cubetxt6.dat (the data cubes). The game reads them as it reads
episodes 1-5 (src/file.c finds them in the content directory).

usage: tools/content/episode6/build.py

For now one level, a copy of episode 5's SAVARA, stands for DIG SITE: the path from the episode
menu through the shop and the level to the ending works before the level compiler makes real
levels.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import tyrdata  # noqa: E402
import tyrformat as tf  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "assets", "content", "episode6")

# The episode's levels: (name, its source: episode and level file number, song).
LEVELS = [
    ("DIG SITE", (5, 4), 33),
]

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


def script():
    lines = []
    # 1: the shop. ]G: the planet map's origin, one destination (planet 4, section 2).
    lines += ["*1 SECTION - Episode 6 start", "]![ 00", "]G[ 04 1 04 002", "]I["] + FIRST_SHOP + [""]
    section = 2
    for i, (name, _, song) in enumerate(LEVELS):
        lines += [f"*{section} SECTION - {name}", tf.level_line(section + 1, name, song, i + 1), ""]
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


def main():
    os.makedirs(OUT, exist_ok=True)
    sources = {}
    entries = []
    for name, (episode, number), _ in LEVELS:
        if episode not in sources:
            sources[episode] = tf.read_level_file(os.path.join(tyrdata.DATA, f"tyrian{episode}.lvl"))
        source = sources[episode]
        entries += [source[(number - 1) * 2], source[(number - 1) * 2 + 1]]
    # The item data: episode 5's (new items come from assets/content/items.cfg on top).
    if 5 not in sources:
        sources[5] = tf.read_level_file(os.path.join(tyrdata.DATA, "tyrian5.lvl"))
    entries.append(sources[5][-1])
    tf.write_level_file(os.path.join(OUT, "tyrian6.lvl"), entries)
    tf.write_strings(os.path.join(OUT, "levels6.dat"), script())
    tf.write_strings(os.path.join(OUT, "cubetxt6.dat"), cubes())
    print(f"{OUT}: {len(LEVELS)} levels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
