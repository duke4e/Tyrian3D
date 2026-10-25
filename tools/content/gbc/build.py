#!/usr/bin/env python3
"""Episode 7, the GBC Tyrian levels (docs/plans/2026-10-25-gbc-epizoda.md), in the game's own formats,
written to assets/content/episode7: tyrian7.lvl (the levels and the episode's item data), levels7.dat
(the script: shops, levels, texts) and cubetxt7.dat. The game reads them as it reads episode 6
(src/file.c finds them in the content directory).

usage: tools/content/gbc/build.py

The levels are data/gbc/episode7 (tools/gbc/episode.py: made from the user's GBC ROM, so neither they
nor this episode are in the repository); without them this writes nothing. Standard library only: it
runs at build time.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "episode6"))
import tyrformat as tf  # noqa: E402
import compose  # noqa: E402
import enemydata  # noqa: E402
from build import ENEMY_D1, level_entries  # noqa: E402  (episode 6's: a level's two entries)

sys.path.insert(0, os.path.join(ROOT, "tools"))
import levels as lv  # noqa: E402

SRC = os.path.join(ROOT, "data", "gbc", "episode7")
OUT = os.path.join(ROOT, "assets", "content", "episode7")
DATA = os.path.join(ROOT, "data", "tyrian2000")

ENDING = [
    "Ixmucane's core is gone, and with it the last",
    "of Microsol's hold on the system.",
]
# The GBC speakers' PC portraits (cube faces: 8 Transon, 6 Reid, 7 Vykromod, 11 Dougan, 14 News, 10 the
# captain, 4 Mondus, 1 data (Javi's in the originals), 2 archive data, 13 alerts) and their cubes' titles
SPEAKERS = {
    "NEWS": (14, "HOLO NEWS", "News"), "VYKROMOD": (7, "INCOMING TRANSMISSION", "Vykromod"),
    "TRANSON": (8, "MESSAGE FROM GENCORE", "Transon"), "DOUGAN": (11, "INCOMING TRANSMISSION", "Dougan"),
    "SAVARA": (13, "DISTRESS CALL FROM SAVARA", "Savara"), "JAVI": (1, "GENCORE SECURITY", "Javi"),
    "CAPTAIN": (10, "INCOMING TRANSMISSION", "Captain"), "REID": (6, "INCOMING TRANSMISSION", "Reid"),
    "TECH": (2, "CODED MESSAGE", "Data"), "STATIC": (13, "SHIP'S COMPUTER", "Alert"),
    "MONDUS": (4, "INCOMING TRANSMISSION", "Mondus"), None: (17, "PERSONAL LOG", "Trent"),
}
# Names in the GBC texts (all capitals there): written with their capitals and marked (~)
NAMES = ["Transon", "Lohk", "Gencore", "Microsol", "Trent", "Hawkins", "Savara", "Javi", "Onukala", "Reid",
         "Mendivian", "Deliani", "Ixmucane", "Harble", "Wom", "Torm", "Camanis", "Dougan", "Vykromod",
         "Mondus", "Hazudra", "Tyrian", "Gyges", "Midway", "Terraform", "Zinglon", "Ixmucane", "Asteroid"]
WIDTH = 62
HINTS = [
    ["Did you know?", "These levels come from Tyrian 2000 for the", "Game Boy Color (World Tree Games, 2000)."],
    ["Did you know?", "The Game Boy Color version was finished", "but never sold; it became freeware in 2007."],
    ["Did you know?", "Here every GBC level is flown with the", "PC game's ships, weapons and enemies."],
]


def sentences(text, width=None, marks=True):
    """A GBC text ('/' a new line, '|' a new page, all capitals) as lines of the cubes: in sentences'
    capitals, names marked, wrapped to WIDTH, pages apart."""
    import re
    names = {n.upper(): n for n in NAMES}
    out = []
    # a page that ends mid-sentence goes on into the next one
    pages = []
    for page in text.split("|"):
        if pages and not pages[-1].rstrip().endswith((".", "!", "?", "..")):
            pages[-1] += "/" + page
        else:
            pages.append(page)
    for page in pages:
        flat = " ".join(w for w in page.replace("/", " ").split(" ") if w)
        flat = flat.lower()
        flat = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), flat)
        flat = re.sub(r"\bi\b", "I", flat)
        flat = re.sub(r"\bi'", "I'", flat)

        def name(m):
            w = m.group(0)
            n = names.get(w.upper())
            return (f"~{n}~" if marks else n) if n else w
        flat = re.sub(r"[A-Za-z]+", name, flat)
        line = ""
        for w in flat.split(" "):
            if len(line.replace("~", "")) + 1 + len(w.replace("~", "")) > (width or WIDTH) and line:
                out.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        if line:
            out.append(line)
        out.append("")
    return out[:-1]


def planets():
    """{(episode, level name): planet} from the original scripts' ]G lines (the planet map's
    destinations: planet, section pairs) and their sections' ]L lines."""
    out = {}
    for ep in range(1, 6):
        strings = lv.read_strings(os.path.join(DATA, f"levels{ep}.dat"))
        section, names, dests = 0, {}, []
        for s in strings:
            if s.startswith("*"):
                section += 1
            elif s.startswith("]L"):
                names.setdefault(section, s[13:22].strip())
            elif s.startswith("]G"):
                nums = s[3:].split()
                pairs = nums[2:]
                dests += [(int(pairs[i]), int(pairs[i + 1])) for i in range(0, len(pairs) - 1, 2)]
            elif s.startswith("]J"):
                pass
        for planet, sec in dests:
            # the destination section, or the first level after it (a shop before the level)
            for k in range(sec, sec + 4):
                if k in names:
                    out.setdefault((ep, names[k]), planet)
                    break
    return out


def shops():
    """The original shops' item lists (]I[ blocks), episodes 1-4 in order."""
    out = []
    for ep in range(1, 5):
        strings = lv.read_strings(os.path.join(DATA, f"levels{ep}.dat"))
        i = 0
        while i < len(strings):
            if strings[i].startswith("]I"):
                block = []
                i += 1
                while i < len(strings) and strings[i].startswith(" "):
                    block.append(strings[i])
                    i += 1
                if len(block) >= 8:
                    out.append(block)
                continue
            i += 1
    return out


def script(stages, levels, planet_of, cube_numbers, ending_text):
    """levels7.dat: each stage a shop section (the planet map's one destination, the items: the
    originals' shops, from episode 1's first to episode 4's, spread over the episode) and its level's
    section; then the ending."""
    lines = []
    all_shops = shops()
    origin = 1
    n = len(stages)
    ending = 2 * n + 1
    for i, (stage, level) in enumerate(zip(stages, levels)):
        shop_section, level_section = 2 * i + 1, 2 * i + 2
        planet = planet_of.get(tuple(stage["pc"]), 1)
        shop = all_shops[min(len(all_shops) - 1, i * len(all_shops) // n)]
        cubes = cube_numbers[i]
        lines += [f"*{shop_section} SECTION - Tyrian GBC Stage {i + 1} - {level['name']}"]
        if cubes:
            lines += [f"]+[ {len(cubes):02d}"]
        lines += [f"]?[ {len(cubes):02d} {' '.join(f'{c:03d}' for c in cubes)}".rstrip(),
                  f"]G[ {origin:02d} 1 {planet:02d} {level_section:03d}", "]I["] + shop + [""]
        origin = planet
        lines += [f"*{level_section} SECTION - Tyrian GBC {level['name']}",
                  tf.level_line(level_section + 1 if i + 1 < n else ending, level["name"], level["song"], i + 1), ""]
    lines += [f"*{ending} SECTION - Tyrian GBC Ending", "]M 008[", "]P 005[", "]Wn 03["] + (ending_text or ENDING) + \
             ["#", "]F[", "]Q[", "#"]
    for k in range(9):
        lines += HINTS[k % len(HINTS)] + ["#"]
    return lines + [""]


def main():
    index = os.path.join(SRC, "episode.json")
    if not os.path.exists(index):
        print(f"{SRC}: no GBC levels (tools/gbc/extract.py, tools/gbc/episode.py), episode 7 not written")
        return 0
    episode = json.load(open(index))
    stages = episode["stages"]
    levels = [json.load(open(os.path.join(SRC, "levels", st["slug"] + ".json"))) for st in stages]
    os.makedirs(OUT, exist_ok=True)
    for level in levels:
        level["events"] = compose.expand(level)  # the placed bosses of the originals
    # (as episode 6: episode 5's enemies used as they are keep their weapons)
    probe = enemydata.Importer()
    kept = set()
    for level in levels:
        for e in level["events"]:
            if e["type"] in ENEMY_D1 and "ep" in e and e["d1"] > 0:
                for k in range(4 if e["type"] == 12 else 1):
                    if e["ep"] == 5 or probe._same_enemy(e["ep"], e["d1"] + k):
                        kept.add(e["d1"] + k)
    importer = enemydata.Importer(kept)
    entries = []
    for level in levels:
        entries += level_entries(level, importer)
    entries.append(bytes(importer.data))
    tf.write_level_file(os.path.join(OUT, "tyrian7.lvl"), entries)
    # the story as data cubes, numbered in order; the ending's text
    cubes, numbers, n = [], [], 0
    for st in stages:
        numbers.append([])
        for c in st.get("cubes", []):
            n += 1
            face, title, header = SPEAKERS.get(c["speaker"], SPEAKERS[None])
            cubes += [f"*{n:02d} {face:02d}", title, header] + sentences(c["text"])
            numbers[-1].append(n)
    ending = []
    for c in episode.get("ending", []):
        ending += sentences(c["text"], 58, marks=False) + [""]  # (a text window: 60 characters, no marks)
    tf.write_strings(os.path.join(OUT, "levels7.dat"), script(stages, levels, planets(), numbers, ending[:-1]))
    tf.write_strings(os.path.join(OUT, "cubetxt7.dat"), cubes + ["*"])
    print(f"{OUT}: {len(levels)} levels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
