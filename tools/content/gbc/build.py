#!/usr/bin/env python3
"""Episode 7, the GBC Tyrian levels (docs/plans/2026-10-25-gbc-epizoda.md), in the game's own formats,
written to assets/content/episode7: tyrian7.lvl (the levels and the episode's item data), levels7.dat
(the script: shops, levels, texts) and cubetxt7.dat. The game reads them as it reads episode 6
(src/file.c finds them in the content directory).

usage: tools/content/gbc/build.py

The levels are data/gbc/episode7 (in the repository; tools/gbc/episode.py makes them from the GBC ROM);
without them this writes nothing. Standard library only: it
runs at build time.
"""
import json
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "episode6"))
import tyrformat as tf  # noqa: E402
import tyrdata  # noqa: E402
import compose  # noqa: E402
import waves  # noqa: E402
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


# Episode 7's own enemies (the GBC levels' that no PC level has): their sprites are sheet W (shapeFile's 37th,
# src/lvlmast.c; newshw.shp, written by sheet.py from their models), or a PC sheet's sprite no PC enemy has ("sheet"),
# their records their base's with those sprites. Levels name them as episode "gbc", enemy n: the n-th as the file lists
# them.
NEW_ENEMIES = json.load(open(os.path.join(HERE, "new_enemies.json")))
NEW_SHEET = 37
SHAPE_FILE = "2478ABCDEFGHIJKLMNOPQRSTU5#V0@3^59'%W"  # (src/lvlmast.c shapeFile: a sheet's number is its place + 1)
SHEET_CHARS = {"x23": "#", "x25": "%", "x27": "'", "x40": "@", "x5e": "^"}  # (the sheets' names as models.cfg has them)


def own_sheet(name):
    """The sheet an own enemy is drawn from: W, or the PC sheet of its look."""
    sheet = NEW_ENEMIES[name].get("sheet")
    return NEW_SHEET if sheet is None else SHAPE_FILE.index(SHEET_CHARS.get(sheet.lower(), sheet.upper())) + 1


# The PC enemy shots the GBC guns' shots are drawn as (sprite numbers of the enemy shots' sheet): an aimed one the
# round two-frame shot most PC enemies aim with; fast straight ones (12 PC px a tick and more) the long one; slower
# ones the small ball.
GBC_SHOT_SPRITE = {"aimed": 112, "fast": 70, "slow": 146}


class Importer(enemydata.Importer):
    """Episode 6's importer, but when the item data has no free weapon slot left, a brought-in
    enemy's gun is episode 5's of that number (the episodes' guns of a number are mostly alike); and
    episode 7's own enemies."""

    full = 0

    def enemy_block(self, episode, first, count=4):
        if episode == "gbc":
            return self.new_enemy(first)
        return super().enemy_block(episode, first, count)

    def enemy(self, episode, number):
        if episode == "gbc":
            return self.new_enemy(number)
        if episode == "boss":
            return self.boss_enemy(number)
        return super().enemy(episode, number)

    # The GBC bosses' pieces (tools/gbc/boss.py: the level's gbc_boss): a record each, the PC boss part's whose looks
    # it takes (its sprites, explosion, worth, what it leaves) with the GBC piece's armour, start speed, guns and
    # launches (the level's events move it on: the GBC script's); level_boss is the level being written.
    level_boss = None
    level_slug = None
    overridden = frozenset()  # (episode, enemy) whose guns an event 31 (fire override) may turn on: all brought in

    def boss_enemy(self, index):
        key = ("boss", self.level_slug, index)
        if key in self.enemy_map:
            return self.enemy_map[key]
        spec = self.level_boss["records"][index - 1]
        new = self.free_enemies.pop(0)
        self.enemy_map[key] = new
        base_ep, base = spec["base"] or (5, 1)
        # (the part's record without its own guns, which it doesn't fire: they'd take weapon numbers; what it leaves
        # when shot down comes with it)
        record = bytearray(self._enemy_record(base_ep, base))
        die = struct.unpack_from("<H", record, 75)[0]
        if 0 < die <= tyrdata.ENEMY_NUM:
            struct.pack_into("<H", record, 75, self.enemy(base_ep, die))
        at = self.enemies[new]
        self.data[at:at + enemydata.ENEMY_SIZE] = record
        for k in range(3):
            gun = spec["tur"][k]
            self.data[at + 1 + k] = self.gbc_weapon(gun) if gun else 0
            self.data[at + 4 + k] = min(255, spec["freq"][k])
        # xmove, ymove (its start speed), xaccel, yaccel (towards the ship), xcaccel, ycaccel
        struct.pack_into("<bbbb", self.data, at + 7, *spec.get("move", [0, 0]), *spec.get("accel", [0, 0]))
        self.data[at + 11:at + 13] = bytes(2)
        self.data[at + 17:at + 19] = bytes(2)          # startxc, startyc
        self.data[at + 19] = spec["armor"]
        self.data[at + 64:at + 66] = bytes(2)          # xrev, yrev: no turning till the events give it
        # (a part drawn damaged from the start, dani < 0, never fires: ASTEROID2's tank, ASTEROID's and OASIS's
        # boss, kept silent; its look stays, the damaged flag goes)
        if struct.unpack_from("<b", self.data, at + 69)[0] < 0:
            self.data[at + 69] = 0
        launch = spec.get("launch")
        self.data[at + 70] = min(255, spec.get("launchfreq", 0)) if launch else 0
        struct.pack_into("<H", self.data, at + 71, self.enemy(*launch) if launch else 0)
        return new

    def gbc_weapon(self, key, spec=None):
        """A GBC gun (boss.py gun_weapon) as a weapon of the episode: its shots at their speeds, from their places, the
        PC's enemy shots that look most like the GBC's (aimed: the round one); the same gun of another level the same
        weapon. (main() makes them all first: the free weapon numbers are few.)"""
        if key in self.weapon_map:
            return self.weapon_map[key]
        spec = spec or self.level_boss["guns"][key]
        content = json.dumps(spec, sort_keys=True)
        if content in self.weapon_content:
            self.weapon_map[key] = self.weapon_content[content]
            return self.weapon_map[key]
        assert self.free_weapons, "no free weapon slot for a GBC gun"
        new = self.free_weapons.pop()  # (the highest: chain targets must be below 150)
        self.weapon_map[key] = self.weapon_content[content] = new
        shots = spec["shots"]
        rec = bytearray(enemydata.WEAPON_SIZE)
        rec[3] = spec["multi"]
        rec[6] = spec["max"]
        rec[9] = spec["aim"]
        aimed = spec["aim"] > 0
        for k, sh in enumerate(shots[:8]):
            rec[10 + k] = min(255, sh["attack"])
            rec[18 + k] = 255                                  # del: till it leaves the screen
            struct.pack_into("<b", rec, 26 + k, max(-128, min(127, sh["sx"])))
            struct.pack_into("<b", rec, 34 + k, max(-128, min(127, sh["sy"])))
            struct.pack_into("<b", rec, 42 + k, max(-128, min(127, sh["bx"])))
            struct.pack_into("<b", rec, 50 + k, max(-128, min(127, sh["by"])))
            struct.pack_into("<H", rec, 58 + 2 * k, GBC_SHOT_SPRITE["aimed" if aimed else
                                                                     "fast" if abs(sh["sy"]) >= 12 or abs(sh["sx"]) >= 12 else "slow"])
        if aimed:
            struct.pack_into("<H", rec, 4, 2)                  # weapani: the round shot's two frames
        rec[77] = 13 if aimed else 6                           # sound
        rec[78] = 255                                          # trail: none
        self.data[self.weapons[new]:self.weapons[new] + enemydata.WEAPON_SIZE] = rec
        return new

    def new_enemy(self, index):
        """One of episode 7's own enemies (its parts in consecutive slots, as event 12 takes them): its base's
        records (with their guns) on sheet W, one frame each, its armour and value; or a look of a PC sheet that no PC
        enemy has ("sheet": its sprite there, "big" a 2x2 one), its base's record standing still (the level's events
        move it: the translation undoes no own enemy's steps), its armour and worth the base's unless given."""
        name = list(NEW_ENEMIES)[index - 1]
        if ("gbc", name) in self.enemy_map:
            return self.enemy_map[("gbc", name)]
        spec = NEW_ENEMIES[name]
        parts = spec["parts"]
        look = "sheet" in spec
        block = self.free_enemies[:len(parts)]
        assert block == list(range(block[0], block[0] + len(parts))), "no consecutive free enemy slots"
        base_ep, base = spec["base"]
        for k, part in enumerate(parts):
            self.free_enemies.remove(block[k])
            self._fill(base_ep, base + k % 4, block[k])
            at = self.enemies[block[k]]
            self.data[at] = 1                     # ani: one frame
            if "armor" in spec:
                self.data[at + 19] = spec["armor"]
            self.data[at + 20] = int(spec.get("big", True))  # esize: 2x2 (0: one 12 x 14 sprite)
            struct.pack_into("<20H", self.data, at + 21, part["sprite"], *[0] * 19)
            self.data[at + 62] = 0                # animate
            self.data[at + 63] = own_sheet(name)  # shapebank
            struct.pack_into("<HBb", self.data, at + 66, 0, 0, 0)  # dgr, dlevel, dani: no wreck sprite
            if "value" in spec:
                struct.pack_into("<h", self.data, at + 73, spec["value"])
            if look:
                self.data[at + 7:at + 13] = bytes(6)   # xmove, ymove, xaccel, yaccel, xcaccel, ycaccel
                self.data[at + 17:at + 19] = bytes(2)  # startxc, startyc
                self.data[at + 64:at + 66] = bytes(2)  # xrev, yrev
        self.enemy_map[("gbc", name)] = block[0]
        return block[0]

    def _fill(self, episode, number, new):
        """As episode 6's, but a gun the enemy never fires (its frequency 0: only an event 31 would make it) stays episode
        5's gun of its number: the free weapon numbers are few (the GBC bosses' guns take some)."""
        record = self._enemy_record(episode, number)
        if (episode, number) in self.overridden:
            return super()._fill(episode, number, new)
        fired = {record[1 + k] for k in range(3) if record[4 + k]}
        idle = {record[1 + k] for k in range(3) if not record[4 + k] and 0 < record[1 + k] < 252} - fired
        self._idle = getattr(self, "_idle", []) + [idle]
        try:
            super()._fill(episode, number, new)
        finally:
            self._idle.pop()

    def weapon(self, episode, number, chain=False):
        if not chain and getattr(self, "_idle", None) and number in self._idle[-1]:
            return number
        try:
            return super().weapon(episode, number, chain)
        except AssertionError:
            Importer.full += 1
            return number


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


SKIP_IT = 21  # the planet map's "Skip It" (pName 21): a way past a level, not a place (the user: "skip it je opcija za level, ne ime levela")


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
            if planet == SKIP_IT:
                continue
            # the destination section, or the first level after it (a shop before the level)
            for k in range(sec, sec + 4):
                if k in names:
                    out.setdefault((ep, names[k]), planet)
                    break
    return out


def shops():
    """The original shops' item lists (]I[ blocks with an item of every kind), episodes 1-4 in order."""
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
                # (only full lists: every kind with an item; a few originals' sections hold empty ones)
                if len(block) >= 8 and all(len(line.split()) > 1 for line in block):
                    out.append(block)
                continue
            i += 1
    return out


# The GBC shop's items as the PC's (tools/gbc/shop.py reads what the GBC shop offers before each level into
# data/gbc/shop.json): its one weapon slot is the front's (the nearest front gun by name and look), its engines the
# generators, its sidekicks both sides' (the PC has no shield, repair, magnet or cold sidekick: the nearest in use).
# The rear guns and armour stay the originals' shops' (the GBC has none).
GBC_SHIPS = {"Talon": 1, "Micros": 5, "Phoenx": 3, "Storm": 14, "Dragon": 15, "Carrot": 2, "UShip": 10}
GBC_WEAPONS = {"Pulse": 1, "Multi": 2, "Scatter": 19, "Sonic": 41, "Vulcan": 7, "Mega": 3, "Proton": 13, "Thunder": 8,
               "Fireball": 18, "Rail": 40, "Chip": 5, "Hotdog": 25, "L.Ball": 42, "Laser": 4, "Hyper": 27, "Arrow": 17,
               "Plasma": 20}
GBC_ENGINES = {"Std": 1, "Light": 2, "Heavy": 3, "MFusion": 4, "Micro": 5, "Graviton": 6}
GBC_SHIELDS = {"Low": 3, "Hard": 4, "Diammd": 5, "LHX Sld": 6, "HTX Sld": 9, "Iron": 10, "Gold": 8}
GBC_SIDES = {"None": 0, "Single": 1, "Dual": 2, "Charge": 3, "Bomb": 13, "Heat": 17, "Shield": 30, "Repair": 16,
             "Magnet": 18, "Cold": 4}


def gbc_offers():
    """{GBC level: the GBC shop's offer before it} (data/gbc/shop.json), or {}."""
    path = os.path.join(ROOT, "data", "gbc", "shop.json")
    if not os.path.exists(path):
        return {}
    return {s["before"]: s["offer"] for s in json.load(open(path))["shops"]}


SHOP_MAX = 6  # items a list at most (the game holds 10: itemAvail)


def gbc_shop(offer, block):
    """An original's shop block with the GBC shop's ships, front guns, generators, shields and sidekicks, and that
    block's own after them (the GBC's lists are as short as the PC's, 3 to 5, but draw from the same few each time:
    the user, 2026-10-29, found the offer thin and much the same; the original's at this point of the episode brings
    the PC's progression), at most SHOP_MAX a list."""
    lines = {line.split()[0]: line for line in block}

    def ids(kind, table, names, first=()):
        out = list(first)
        for i in [table[n] for n in names if n in table] + [int(v) for v in lines[kind].split()[1:]]:
            if i not in out and len(out) < SHOP_MAX:
                out.append(i)
        return f" {kind:<6} " + " ".join(str(i) for i in out)
    lines["Ship"] = ids("Ship", GBC_SHIPS, offer["ship"])
    lines["WeapF"] = ids("WeapF", GBC_WEAPONS, offer["weapon"])
    lines["Power"] = ids("Power", GBC_ENGINES, offer["engine"])
    lines["Shield"] = ids("Shield", GBC_SHIELDS, offer["shield"])
    lines["Opt1"] = ids("Opt1", GBC_SIDES, offer["sideA"], (0,))
    lines["Opt2"] = ids("Opt2", GBC_SIDES, offer["sideB"], (0,))
    return [lines[line.split()[0]] for line in block]


def script(stages, levels, planet_of, cube_numbers, ending_text):
    """levels7.dat: each stage a shop section (the planet map's one destination, the items: the GBC shop's
    offer before the level, in an original's shop block: the originals' shops, from episode 1's first to episode
    4's, spread over the episode, for what the GBC shop has not) and its level's section; then the ending."""
    lines = []
    all_shops = shops()
    offers = gbc_offers()
    offer = None
    origin = 1
    n = len(stages)
    ending = 2 * n + 1
    for i, (stage, level) in enumerate(zip(stages, levels)):
        shop_section, level_section = 2 * i + 1, 2 * i + 2
        planet = planet_of.get(tuple(stage["pc"]), origin)  # (one the map hasn't: where the last was)
        shop = all_shops[min(len(all_shops) - 1, i * len(all_shops) // n)]
        # the GBC shop's offer before this level (the Arcade-only levels and the last: the one before)
        offer = offers.get(stage.get("gbc"), offer)
        if offer:
            shop = gbc_shop(offer, shop)
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


# The boss fight. The boss is the original level's (or a related one's): its block from the spawns of its last boss
# bar's links (BOSS_LEAD before the bar: those links also make ordinary enemies all through some levels, DELIANI's,
# LAVA EXIT's), its links ones of its own (31-40 where the original's are low: the GBC script's are 1-30), and the
# original's scroll over it (the blocks leave scroll events out): where the original stops its map there, so does
# the level. Where it doesn't (the originals' bosses come at their maps' ends and many drift down with the scroll;
# in a GBC level they flew through the screen and their "end when clear", 36, ended the level), once the boss's body
# is on screen the map stops, its drifting pieces stop (19 by link). Forced events (53) keep the clock running for
# its script; the level ends when it is gone (36, added where its block has none), or at its event 11, at least
# BOSS_TIME ticks of fight later (an unkillable boss); the block's map restarts (4, 83) are left out.
BOSS_TOP = 24            # the boss's highest piece's y when it stops (its top edge a few pixels into the screen)
BOSS_TIME = 2400         # ticks of fight at least before the level's 11 ends it anyway (an unkillable boss)
BOSS_MAX = 6000          # ... and at most (a boss block that runs on: the final one's phases)
BOSS_IN = 300            # the added end-when-clear this long after the boss is made or stops
BOSS_CHECK = 12          # ... and from then on whether it is gone (event 70) every this many ticks
BOSS_LEAD = 400          # the block's spawns from this long before its last boss bar
LAYER_OF = {15: "sky", 18: None, 6: "ground", 10: "ground", 17: None, 56: None, 7: "top", 23: None, 32: None}


def boss_template(src):
    """The original's boss block (waves.Source.boss) from its last bar's spawns, and its scroll events."""
    b = src.boss()
    if b is None:
        return None
    links = b["links"]
    events = [e for e in src.events if e["t"] < 60000]
    bars = [e["t"] for e in events if e["type"] == 79 and (e["d1"] in links or e["d2"] in links)]
    spawns = sorted(e["t"] for e in events if e["type"] in waves.SPAWNS and e["d4"] in links
                    and e["t"] >= max(bars + [0]) - BOSS_LEAD)
    start = spawns[0] if spawns else b["start"]
    start = min([e["t"] for e in events if e["type"] == 16 and start - 400 <= e["t"] <= start] + [start])
    block = []
    for e in events:
        if e["t"] < start:
            continue
        link = waves.by_link(e)
        if (link in links or e["type"] in waves.BOSS_SCRIPT and e["type"] != 2 or e["type"] == 39 and e["d1"] in links):
            block.append(dict(e, t=e["t"] - start))
    length = max([e["t"] for e in block] + [0])
    # (and the moves of every enemy of a layer, or all, over it: BRAINIAC's hold its brain against the scroll)
    block += [dict(e, t=e["t"] - start) for e in events
              if e["type"] == 19 and e["d3"] in (1, 2, 3, 99) and start <= e["t"] <= start + length]
    block.sort(key=lambda e: e["t"])
    scroll = [dict(e, t=e["t"] - start) for e in events if e["type"] in (2, 30) and start <= e["t"] <= start + length]
    before = [e for e in events if e["type"] in (2, 30) and e["t"] < start]
    return dict(start=start, events=block, links=links, length=length, scroll=scroll,
                speed=(before[-1]["d1"], before[-1]["d2"], before[-1]["d3"]) if before else (1, 2, 3))


class BossLinks:
    """The boss's links: its own (31-40 for the originals' low ones; the GBC script's are 1-30)."""

    def remap(self, links, start, end):
        low = iter(range(31, 41))
        return {link: (next(low, link) if link <= 40 else link) for link in sorted(links)}


def boss_fight(level, events):
    bosses = [p for p in level["placements"] if p["kind"] == "boss"]
    if not bosses:
        return events
    p = bosses[0]
    src = waves.Source(p["episode"], p["name"])
    tpl = boss_template(src)
    if tpl is None:
        return events
    start = p["start"]
    placed = compose.place(tpl, start, BossLinks(), src.episode)
    links = {v for e in placed if e["type"] == 79 for v in (e["d1"], e["d2"]) if v}
    s1, s2, s3 = tpl["speed"]
    scroll = [dict(t=start, type=2, d1=s1, d2=s2, d3=s3, d5=0, d6=0, d4=0)]
    scroll += [dict(t=start + e["t"], type=e["type"], d1=e["d1"], d2=e["d2"], d3=e["d3"], d5=0, d6=0, d4=0)
               for e in tpl["scroll"]]
    stops = [e["t"] for e in scroll if e["d1"] == 0]
    data = {}
    spawns = [e for e in placed if e["d4"] in links and e["type"] in tuple(LAYER_OF) + (12,)]
    first = min(e["t"] for e in spawns) if spawns else start
    arrive = None
    drifting = set()  # the links whose pieces drift down with no motion of their own (stopped when it is in)
    for e in spawns:
        if e["t"] > first + 300:
            continue  # (the body only: later spawns are what it launches, adds, brings back)
        if e["type"] == 12:
            layer = {0: "ground", 1: "ground", 2: "sky", 3: "top", 4: "ground"}.get(e["d6"])
            top = -28 + e["d5"] - 28
        else:
            layer = LAYER_OF[e["type"]]
            top = -28 + e["d5"]
        if layer is None:
            continue  # (from the bottom: on screen at once)
        dat = data.setdefault(e["ep"], tyrdata.load_items(e["ep"])["enemies"]).get(e["d1"], {}) if "ep" in e else {}
        if dat.get("ycaccel") or dat.get("yaccel") or dat.get("yrev"):
            continue  # (it moves to a place of its own, or to and fro)
        own = e["d3"] + dat.get("ymove", 0) + (e["d6"] if e["type"] != 12 else 0)
        moving = not stops or e["t"] < stops[0]  # (the map: still moving when it is made)
        vy = own + ({"sky": 0, "ground": s1, "top": s3}[layer] if moving else 0)
        if own > 0:
            drifting.add(e["d4"])
        if vy <= 0 or top >= BOSS_TOP:
            continue
        # (the clock: the map's scroll while it moves, a tick at a time once it stops, forced)
        arrive = max(arrive or 0, e["t"] + int((BOSS_TOP - top) / vy * (s1 if moving and s1 > 0 else 1) + 0.999))
    if arrive is None:
        arrive = first + 100  # (pieces that move to their places themselves: they are in a while after)
    # Where the original stops its map over the boss, the level does the same (its boss is made for it: TORM's
    # holds its place against the scroll till then; pieces drifting down over a map already stopped stop once they
    # are in); where not, the map stops and its drifting pieces stop once it is in (for one the map brings in row
    # by row, its last row)
    # (a boss that holds its place against the scroll itself, its own speed up the screen while the map runs:
    # IXMUCANE's; the map runs on as the original's)
    holds = any(e["type"] in (19, 20) and e["d4"] in links and -99 < e["d2"] < 0 and e["t"] < (stops[0] if stops else 65000)
                for e in placed)
    if stops:
        halt = stops[0]
        if halt > arrive:
            drifting = set()  # (drifting with the scroll till the original's stop: that is its design)
    elif holds:
        halt, drifting = None, set()
    else:
        if not all(e["t"] <= first + 300 for e in spawns):
            arrive, drifting = max(e["t"] for e in spawns) + 28 * 8, set()
        halt = arrive
    added = []
    if halt is None:
        halt = arrive
    else:
        scroll = [e for e in scroll if e["t"] < halt or (e["t"] == halt and e["d1"] == 0)]
        if not any(e["t"] == halt and e["d1"] == 0 for e in scroll):
            added.append(dict(t=halt, type=2, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
        if not any(e["type"] == 53 and e["d1"] != 99 and e["t"] <= halt for e in placed):
            added.append(dict(t=halt, type=53, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    added += [dict(t=arrive, type=19, d1=-99, d2=0, d3=0, d5=0, d6=-99, d4=link) for link in sorted(drifting)]
    # (a boss that passes by in the original, its map going on once it is gone: ASTEROID2's tank, which drives
    # down past the ship: here it stops once it is in, and fights)
    if not any(e["type"] == 36 for e in placed) and any(e["type"] in (4, 83) for e in placed):
        rovers = sorted({e["d4"] for e in spawns if e["d4"]})
        added += [dict(t=arrive, type=20, d1=0, d2=0, d3=0, d5=0, d6=0, d4=link) for link in rovers]
        added += [dict(t=arrive, type=19, d1=0, d2=0, d3=0, d5=0, d6=0, d4=link) for link in rovers]
    freeze = max(halt, arrive)
    # (pieces drawn damaged from the start, dani < 0, don't count as on screen: ASTEROID2's tank; with only such
    # a boss, an end when clear ends the level at once: it ends at its 11)
    counted = any(data.setdefault(e["ep"], tyrdata.load_items(e["ep"])["enemies"]).get(e["d1"], {}).get("dani", 0) >= 0
                  for e in spawns if "ep" in e)
    end = freeze + min(BOSS_MAX, max(BOSS_TIME, start + tpl["length"] - freeze + 300))
    if counted and not any(e["type"] == 36 and e["t"] >= freeze for e in placed):
        # (a while after it is made: one that comes in on its own, ASTEROID2's tank, must be in first)
        added.append(dict(t=max(freeze, first) + BOSS_IN, type=36, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    bars = sorted(links)[:3]
    if bars:
        # (and once its bars' links are empty, the level ends with every enemy taken off, as the GBC's end once their
        # boss is gone, boss.py's 70s: an end when clear waited for the rest too, and BUBBLES's bubble machines,
        # standing on the stopped map, never stopped blowing: the user, 2026-10-29, killed its boss at once and the
        # level never ended; a boss that doesn't count as on screen too: AST.BONUS's tank, shot down at once, left
        # the stopped map empty till its 11, the user, 2026-11-04: "zaglavio sam nakon što sam ubio glavnog")
        added += [dict(t=c, type=70, d1=end, d2=bars[0], d3=bars[1] if len(bars) > 1 else 0, d5=0, d6=0,
                       d4=bars[2] if len(bars) > 2 else 0)
                  for c in range(max(freeze, first) + BOSS_IN, end, BOSS_CHECK)]
        added.append(dict(t=end, type=41, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0))
    out = []
    for e in placed:
        if e["t"] > freeze and e["type"] == 53 and e["d1"] == 99:
            continue  # (nothing after it stops the clock again)
        if e["type"] in (4, 83):
            continue  # (nor the map's restart once the screen is clear: the boss would scroll away)
        out.append(e)
    rest = [dict(e, t=min(65000, end)) if e["type"] == 11 else e for e in events]
    merged = rest + out + scroll + added
    merged.sort(key=lambda e: e["t"])  # (stable: same-time events keep their order)
    return compose.with_small_adjust(merged)


def music(stages):
    """The GBC songs (tools/gbc/music.py: each cut at its loop, in data/gbc/music/loops) into music/ beside the episode's
    files, and music.txt: a line a level, by its number in the level file (its ]L line's), its song and the sample its
    loop starts at, its boss song and its loop's (- where it has none); the game plays them in place of the PC songs
    (src/loudness.c play_recorded_song, tyrian2.c gbc_music), as MIDI through the SoundFont where the music plays as
    MIDI (each song's .mid beside it)."""
    loops = os.path.join(ROOT, "data", "gbc", "music", "loops")
    if not os.path.exists(os.path.join(loops, "loops.json")):
        return
    info = json.load(open(os.path.join(loops, "loops.json")))
    os.makedirs(os.path.join(OUT, "music"), exist_ok=True)
    lines, used = [], set()
    for i, st in enumerate(stages, 1):
        song, boss = info["levels"].get(str(st["gbc"]), [None, None])
        if not song:
            continue
        used |= {song, boss} - {None}
        lines.append(f"{i:02d} {song} {info['loops'][song]} " + (f"{boss} {info['loops'][boss]}" if boss else "- 0"))
    for f in sorted(used):
        shutil.copyfile(os.path.join(loops, f), os.path.join(OUT, "music", f))
        midi = f[:-4] + ".mid"  # (its MIDI, tools/gbc/midi.py: played while the music plays as MIDI)
        if os.path.exists(os.path.join(loops, midi)):
            shutil.copyfile(os.path.join(loops, midi), os.path.join(OUT, "music", midi))
    with open(os.path.join(OUT, "music.txt"), "w") as out:
        out.write("\n".join(lines) + "\n")


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
        # (the boss is placed here, boss_fight; the rest as episode 6 places them)
        bosses = [p for p in level["placements"] if p["kind"] == "boss"]
        level["placements"] = [p for p in level["placements"] if p["kind"] != "boss"]
        expanded = compose.expand(level)
        level["placements"] += bosses
        level["events"] = boss_fight(level, expanded)
    # (as episode 6: episode 5's enemies used as they are keep their weapons)
    probe = Importer()
    kept = set()
    for level in levels:
        for e in level["events"]:
            if e["type"] in ENEMY_D1 and "ep" in e and e["d1"] > 0:
                for k in range(4 if e["type"] == 12 else 1):
                    if e["ep"] not in ("gbc", "boss") and (e["ep"] == 5 or probe._same_enemy(e["ep"], e["d1"] + k)):
                        kept.add(e["d1"] + k)
    importer = Importer(kept)
    overridden = set()
    for level in levels:
        links = {e["d4"] for e in level["events"] if e["type"] == 31}
        overridden |= {(e["ep"], e["d1"] + k) for e in level["events"]
                       if e["type"] in ENEMY_D1 and "ep" in e and e["d1"] > 0 and (99 in links or e["d4"] in links)
                       for k in range(4 if e["type"] == 12 else 1)}
    importer.overridden = frozenset(overridden)
    # (the GBC bosses' guns first: the free weapon numbers are few)
    for level in levels:
        for key, spec in (level.get("gbc_boss") or {}).get("guns", {}).items():
            importer.gbc_weapon(key, spec)
    entries = []
    for level in levels:
        importer.level_boss, importer.level_slug = level.get("gbc_boss"), level["name"]
        entries += level_entries(level, importer)
    entries.append(bytes(importer.data))
    tf.write_level_file(os.path.join(OUT, "tyrian7.lvl"), entries)
    shutil.copyfile(os.path.join(HERE, "newshw.shp"), os.path.join(OUT, "newshw.shp"))
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
    music(stages)
    print(f"{OUT}: {len(levels)} levels, {len(importer.enemy_map)} enemies and {len(importer.weapon_map)} guns brought in"
          + (f", {Importer.full} guns as episode 5's (no slot left)" if Importer.full else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
