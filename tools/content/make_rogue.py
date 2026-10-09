#!/usr/bin/env python3
"""The rogue mode's data (src/rogue.h): its acts and their levels, the items its cards offer and
the unlocks bought between runs, written to assets/content/rogue.cfg.

usage: tools/content/make_rogue.py

Levels are the episodes' own (episode:section, as tools/levels.py lists them); a level with a boss
bar (event 79) can end an act. Items are those the episodes' shops sell (their ]I lists), plus the
new ones of assets/content/items.cfg behind unlocks; an item's tier (1-3, how rare and how late its
card comes) follows its price among the items of its kind.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import levels  # noqa: E402
import tyrdata  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "content", "rogue.cfg")

# The acts: their levels by name (the first section of an episode with that name), from the
# episodes' easier half to their harder one. Bonus, secret and mini-game levels are left out, and
# TORM (twice as long as the others).
ACTS = [
    dict(name="Act I: Deliani", difficulty=2, rows=3,
         levels=[(1, n) for n in ("TYRIAN", "ASTEROID1", "ASTEROID2", "SAVARA", "MINES", "BUBBLES", "DELIANI",
                                  "ASTEROID?", "MINEMAZE", "HOLES", "SOH JIN")],
         bosses=[(1, "ASSASSIN"), (1, "SAVARA V")]),
    dict(name="Act II: Gyges and Ixmucane", difficulty=3, rows=3,
         levels=[(2, n) for n in ("GYGES", "ASTCITY", "SOH JIN", "GEM WAR", "MARKERS", "MISTAKES", "BOTANY A",
                                  "BOTANY B")] +
                [(3, n) for n in ("GAUNTLET", "IXMUCANE", "STARGATE", "CAMANIS", "AST. CITY", "SAWBLADES",
                                  "SAVARA Y", "New Deli")],
         bosses=[(2, "GRYPHON"), (3, "FLEET"), (3, "TYRIAN X")]),
    dict(name="Act III: Into the Core", difficulty=4, rows=3,
         levels=[(4, n) for n in ("SURFACE", "LAVA RUN", "CORE", "?TUNNEL?", "ICE EXIT", "HARVEST", "UNDERDELI",
                                  "SAVARA IV", "EYESPY", "LAVA EXIT", "SIDE EXIT", "APPROACH")] +
                [(5, n) for n in ("ASTEROIDS", "AST ROCK", "MINERS", "SAVARA", "CORAL", "STATION")],
         bosses=[(4, "DREAD-NOT"), (4, "BRAINIAC"), (4, "NOSE DRIP"), (5, "FRUIT")]),
]

# The shops' item lists (]I): nine lines, these are the kinds of the ones used.
# Ports 44-47 are the Dragonwing's (the second player's) weapons.
SKIP = {("front", i) for i in range(44, 48)}

SHOP_KINDS = {0: "ship", 1: "front", 2: "rear", 3: "generator", 5: "left", 6: "right", 8: "shield"}

# Specials (the ship's special weapon) offered by cards: the ones that work on any ship.
SPECIALS = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 40, 41, 45, 47]

# The new items of assets/content/items.cfg and the unlocks that put them in the cards.
NEW_ITEMS = [("front", i, "arsenal") for i in (48, 49, 50, 51)] + [("rear", i, "arsenal") for i in (52, 53)] + \
            [(side, i, "pods") for i in (33, 34, 35, 36, 37) for side in ("left", "right")]

UNLOCKS = [
    ("arsenal", 3, "Sidekick Arsenal", "Weapons made from sidekicks join the cards"),
    ("pods", 3, "Weapon Pods", "Sidekicks made from weapons join the cards"),
    ("specials", 2, "Special Weapons", "Special weapons (Flare, Repulsor...) join the cards"),
    ("capital", 2, "Venture Capital", "Runs start with 5000 credits more"),
    ("hull", 5, "Spare Hull", "Runs start with an extra life"),
    ("warmup", 3, "Warm Guns", "Runs start with the front gun at power 2"),
    ("fourth", 6, "Fourth Card", "Card picks show four cards"),
    ("exotic", 4, "Exotic Hulls", "Ships no shop sells join the cards"),
]
EXOTIC_SHIPS = [8, 10, 11, 12, 15, 17, 18]  # Stalker, U-Ship, Silver Ship, Nort Ship, Red Dragon, PeteZoomer, Rum Bottle


def shops(episode):
    """The episode's shops' item lists (each ]I command's nine lines)."""
    strings = levels.read_strings(os.path.join(tyrdata.DATA, f"levels{episode}.dat"))
    return [strings[i + 1:i + 10] for i, s in enumerate(strings) if s.startswith("]I")]


def has_boss(episode, section_name):
    return section_name in BOSSES.get(episode, set())


def scan_bosses():
    """Level names (per episode) whose events show a boss bar."""
    result = {}
    for episode in range(1, 6):
        data, n, pos = tyrdata.lvl_positions(os.path.join(tyrdata.DATA, f"tyrian{episode}.lvl"))
        strings = levels.read_strings(os.path.join(tyrdata.DATA, f"levels{episode}.dat"))
        for s in strings:
            if not s.startswith("]L"):
                continue
            name, file_num = s[13:22].strip(), int(s[25:27])
            if not 0 < file_num * 2 <= n:
                continue  # sections the game never reaches name levels the file doesn't have
            r = tyrdata.Reader(data, pos[(file_num - 1) * 2])
            r.u8(2)
            r.u16(3)
            r.u16(r.u16())
            for _ in range(r.u16()):
                r.u16()
                kind = r.u8()
                dat, dat2 = r.s16(), r.s16()
                r.u8(4)
                if kind == 79 and (dat or dat2):
                    result.setdefault(episode, set()).add(name)
    return result


BOSSES = {}


def tiers(ids, cost):
    """Each id's tier, 1-3, by its price among the others (thirds)."""
    ranked = sorted(ids, key=cost)
    return {item: 1 + min(2, k * 3 // max(1, len(ranked))) for k, item in enumerate(ranked)}


def main():
    BOSSES.update(scan_bosses())
    items = tyrdata.load_items(1)
    lines = ["# Tyrian3D rogue mode, made by tools/content/make_rogue.py (do not edit by hand: change the rules).",
             "# Format: src/rogue.h.", ""]

    level_sections = {ep: {name: sec for sec, name in reversed(levels.level_sections(
        os.path.join(tyrdata.DATA, f"levels{ep}.dat")))} for ep in range(1, 6)}
    for number, act in enumerate(ACTS, 1):
        lines.append(f'act {number} name="{act["name"]}" difficulty={act["difficulty"]} rows={act["rows"]}')
        for kind, entries in (("level", act["levels"]), ("boss", act["bosses"])):
            for episode, name in entries:
                section = level_sections[episode][name]
                assert kind == "level" or has_boss(episode, name), name
                lines.append(f'{kind} {number} {episode}:{section} "{name}"')
        lines.append("")

    # Items the shops sell, by kind.
    sold = {kind: set() for kind in SHOP_KINDS.values()}
    for episode in range(1, 6):
        for shop in shops(episode):
            for index, kind in SHOP_KINDS.items():
                for word in shop[index][8:].split():
                    if word.isdigit() and int(word) > 0 and (kind, int(word)) not in SKIP:
                        sold[kind].add(int(word))
    costs = {"ship": lambda i: items["ships"][i]["cost"], "front": lambda i: items["ports"][i]["cost"],
             "rear": lambda i: items["ports"][i]["cost"], "generator": lambda i: items["gens"][i]["cost"],
             "left": lambda i: items["options"][i]["cost"], "right": lambda i: items["options"][i]["cost"],
             "shield": lambda i: items["shields"][i]["cost"], "special": lambda i: items["specials"][i]["pwr"]}
    names = {"ship": "ships", "front": "ports", "rear": "ports", "generator": "gens", "left": "options",
             "right": "options", "shield": "shields", "special": "specials"}
    lines.append("# Items: <kind> <id> tier=<1-3> [unlock=<name>]")
    for kind in ("front", "rear", "left", "right", "shield", "generator", "ship"):
        ids = sorted(sold[kind])
        for item, tier in sorted(tiers(ids, costs[kind]).items()):
            lines.append(f"item {kind} {item} tier={tier}  # {items[names[kind]][item]['name'].strip()}")
    for item, tier in sorted(tiers(SPECIALS, costs["special"]).items()):
        lines.append(f"item special {item} tier={tier} unlock=specials  # {items['specials'][item]['name'].strip()}")
    for item, tier in sorted(tiers(EXOTIC_SHIPS, costs["ship"]).items()):
        lines.append(f"item ship {item} tier={max(2, tier)} unlock=exotic  # {items['ships'][item]['name'].strip()}")
    for kind, item, unlock in NEW_ITEMS:
        lines.append(f"item {kind} {item} tier=2 unlock={unlock}")
    lines.append("")

    lines.append("# Unlocks: <name> cost=<cores> title= text=")
    for name, cost, title, text in UNLOCKS:
        lines.append(f'unlock {name} cost={cost} title="{title}" text="{text}"')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{OUT}: {len(ACTS)} acts, {sum(1 for l in lines if l.startswith('item '))} items, {len(UNLOCKS)} unlocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
