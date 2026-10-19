"""Episode 6's item data with enemies brought in from any episode.

Enemy and weapon numbers mean different things in episodes 1-3 (tyrian.hdt) and 4-5 (their level
files' last entry). Episode 6's item data starts as episode 5's; an enemy of another episode is
copied into a free slot of it, with the weapons it fires and the enemies it launches or leaves,
and the events that name it get the new number (`Importer.enemy`).
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import tyrdata  # noqa: E402

ENEMY_SIZE = 77    # one enemyDat record (episodes.c)
WEAPON_SIZE = 80   # one weapons record
WEAPON_BANKS = ((0, tyrdata.WEAP_END1), (tyrdata.WEAP_START2, tyrdata.WEAP_NUM))
ENEMY_BANKS = ((0, tyrdata.ENEMY_END1), (tyrdata.ENEMY_START2, tyrdata.ENEMY_NUM))

# Where brought-in enemies go: slots episode 6's levels don't otherwise use (episode 5's second
# bank's last ones). Enemies fire weapons named by a byte (1-251), so brought-in weapons go in the
# low weapons nothing of episode 5 uses (players' guns, sidekicks, specials, enemies, the chains
# they fire); chain targets (a hit firing weapon n is attack 100+n) below 150.
IMPORT_ENEMIES = range(1500, tyrdata.ENEMY_NUM + 1)
ATTACK = 10  # the attack[8] bytes in a weapon record


def item_data(episode):
    """The episode's item data (bytes) as JE_loadItemDat reads it."""
    if episode <= 3:
        data = open(os.path.join(tyrdata.DATA, "tyrian.hdt"), "rb").read()
        start = struct.unpack_from("<i", data, 0)[0]
        return data[start:]
    data, n, pos = tyrdata.lvl_positions(os.path.join(tyrdata.DATA, f"tyrian{episode}.lvl"))
    return data[pos[n - 1]:pos[n]]


def layout(data):
    """Offsets of every weapon and enemy record in item data."""
    r = tyrdata.Reader(data, 0)
    r.u16(7)
    weapons = {}
    for lo, hi in WEAPON_BANKS:
        for i in range(lo, hi + 1):
            weapons[i] = r.o
            r.o += WEAPON_SIZE
    r.o += (tyrdata.PORT_NUM + 1) * (1 + 30 + 1 + 44 + 6)
    r.o += (tyrdata.SPECIAL_NUM + 1) * (1 + 30 + 2 + 1 + 1 + 2)
    r.o += (tyrdata.POWER_NUM + 1) * (1 + 30 + 2 + 1 + 1 + 2)
    r.o += (tyrdata.SHIP_NUM + 1) * (1 + 30 + 2 + 2 + 1 + 1 + 1 + 2 + 1)
    r.o += (tyrdata.OPTION_NUM + 1) * (1 + 30 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 40 + 1 + 2 + 1 + 1 + 1)
    r.o += (tyrdata.SHIELD_NUM + 1) * (1 + 30 + 1 + 1 + 2 + 2)
    enemies = {}
    for lo, hi in ENEMY_BANKS:
        for i in range(lo, hi + 1):
            enemies[i] = r.o
            r.o += ENEMY_SIZE
    return weapons, enemies, r.o


def chains(record):
    """The weapons a weapon's hits fire (attack 100-249)."""
    return [a - 100 for a in record[ATTACK:ATTACK + 8] if 100 <= a < 250]


def free_low_weapons(enemies=None):
    """Weapons 1-251 nothing of episode 5 uses: its players' guns, sidekicks and specials, and
    the weapons of its enemies (enemies: only these, the ones episode 6 keeps; None: all)."""
    items = tyrdata.load_items(5)
    used = set()
    for p in items["ports"]:
        for mode in p["op"]:
            used.update(v for v in mode if v)
    for o in items["options"]:
        used.update(range(o["wpnum"], o["wpnum"] + o["pwr"] + 1))
    for sp in items["specials"]:
        used.add(sp["wpn"])
    for number, e in items["enemies"].items():
        if enemies is None or number in enemies:
            used.update(t for t in e["tur"] if 0 < t < 252)
    weapons = items["weapons"]
    todo = list(used)
    while todo:
        w = todo.pop()
        for a in weapons.get(w, {}).get("attack", []):
            if 100 <= a < 250 and a - 100 not in used:
                used.add(a - 100)
                todo.append(a - 100)
    # The game's own tables of weapons (link and charge guns, mainint.c / varz.c) are up high.
    return [i for i in range(1, 252) if i not in used]


class Importer:
    """Episode 6's item data (episode 5's), enemies of other episodes brought into it."""

    def __init__(self, kept_enemies=None):
        """kept_enemies: episode 5's enemies episode 6 uses as they are (their weapons stay);
        None keeps every enemy's weapons."""
        self.data = bytearray(item_data(5))
        self.weapons, self.enemies, end = layout(self.data)
        assert end <= len(self.data)
        self.sources = {}
        self.enemy_map = {}   # (episode, enemy) -> number in episode 6
        self.weapon_map = {}  # (episode, weapon) -> number in episode 6
        self.free_enemies = list(IMPORT_ENEMIES)
        self.free_weapons = free_low_weapons(kept_enemies)
        self.weapon_content = {}  # a brought-in weapon's record (as written) -> its number

    def scale_values(self, factor, skip=range(390, 400)):
        """Every enemy worth factor times its credits (values 2-9999: credits on a kill; 1 is a
        data cube, above and below are other things), but the coins and gems themselves."""
        for number, at in self.enemies.items():
            if number in skip:
                continue
            value = struct.unpack_from("<h", self.data, at + 73)[0]
            if 1 < value < 10000:
                struct.pack_into("<h", self.data, at + 73, min(9999, int(round(value * factor))))

    def custom(self, episode, number, value):
        """A copy of an enemy (brought in as enemy() does) worth value (a warp orb's 10000 + n),
        in a slot of its own; the same copy again for the same value."""
        key = (episode, number, "value", value)
        if key not in self.enemy_map:
            new = self.free_enemies.pop(0)
            self.enemy_map[key] = new
            self._fill(episode, number, new)
            struct.pack_into("<h", self.data, self.enemies[new] + 73, value)
        return self.enemy_map[key]

    def _source(self, episode):
        if episode not in self.sources:
            data = item_data(episode)
            self.sources[episode] = (data,) + layout(data)[:2]
        return self.sources[episode]

    def _weapon_record(self, episode, number):
        data, weapons, _ = self._source(episode)
        return bytes(data[weapons[number]:weapons[number] + WEAPON_SIZE])

    def _same_weapon(self, episode, number, seen=None):
        """The weapon (and the weapons its hits fire) the same in episode 5."""
        seen = set() if seen is None else seen
        if number in seen:
            return True
        seen.add(number)
        record = self._weapon_record(episode, number)
        if record != bytes(self.data[self.weapons[number]:self.weapons[number] + WEAPON_SIZE]):
            return False
        return all(self._same_weapon(episode, c, seen) for c in chains(record))

    def weapon(self, episode, number, chain=False):
        """A weapon of an episode as one of episode 6 (a chain target below 150)."""
        if number <= 0 or episode == 5 or self._same_weapon(episode, number):
            return number
        key = (episode, number)
        if key not in self.weapon_map:
            free = [w for w in self.free_weapons if not chain or w < 150]
            assert free, f"no free weapon slot ({len(set(self.weapon_map.values()))} brought in)"
            new = free[0]
            self.free_weapons.remove(new)
            self.weapon_map[key] = new  # first, for chains that come back to it
            record = bytearray(self._weapon_record(episode, number))
            for k in range(8):
                a = record[ATTACK + k]
                if 100 <= a < 250:
                    record[ATTACK + k] = 100 + self.weapon(episode, a - 100, chain=True)
            record = bytes(record)
            # The same weapon from another episode (or another number) shares a slot, unless
            # something already points at this one (a chain coming back to it).
            known = self.weapon_content.get(record)
            others = [k for k, v in self.weapon_map.items() if v == new and k != key]
            if known is not None and (not chain or known < 150) and not others and 100 + new not in record[ATTACK:ATTACK + 8]:
                self.weapon_map[key] = known
                self.free_weapons.insert(0, new)
                self.free_weapons.sort()
                return known
            self.weapon_content[record] = new
            self.data[self.weapons[new]:self.weapons[new] + WEAPON_SIZE] = record
        return self.weapon_map[key]

    def _enemy_record(self, episode, number):
        data, _, enemies = self._source(episode)
        return bytes(data[enemies[number]:enemies[number] + ENEMY_SIZE])

    def _same_enemy(self, episode, number, seen=None):
        """The enemy (its weapons, what it launches and leaves) the same in episode 5."""
        seen = set() if seen is None else seen
        if number in seen:
            return True
        seen.add(number)
        record = self._enemy_record(episode, number)
        if record != bytes(self.data[self.enemies[number]:self.enemies[number] + ENEMY_SIZE]):
            return False
        if not all(self._same_weapon(episode, t) for t in record[1:4] if 0 < t < 252):
            return False
        launched, dying = (struct.unpack_from("<H", record, at)[0] for at in (71, 75))
        if number <= 1000:
            launched %= 1000  # (the thousands are its launch special: _fill)
        return all(self._same_enemy(episode, o, seen) for o in (launched, dying) if 0 < o <= tyrdata.ENEMY_NUM)

    def enemy_block(self, episode, first, count=4):
        """count consecutive enemies (a 4-part enemy's, event 12) as consecutive numbers of
        episode 6."""
        if episode == 5 or all(self._same_enemy(episode, first + k) for k in range(count)):
            return first
        if (episode, first) in self.enemy_map:
            return self.enemy_map[(episode, first)]
        block = self.free_enemies[:count]
        assert block == list(range(block[0], block[0] + count)), "no consecutive free enemy slots"
        # Taken in place: the parts' own references (launches, drops) come after.
        for k in range(count):
            self.free_enemies.remove(block[k])
            self.enemy_map[(episode, first + k)] = block[k]
        for k in range(count):
            self._fill(episode, first + k, block[k])
        return block[0]

    def _fill(self, episode, number, new):
        record = bytearray(self._enemy_record(episode, number))
        for k in range(3):
            tur = record[1 + k]
            if 0 < tur < 252:
                record[1 + k] = self.weapon(episode, tur)
        for at in (71, 75):  # elaunchtype, eenemydie
            other = struct.unpack_from("<H", record, at)[0]
            if at == 71 and number <= 1000:
                # An enemy of the first bank launches elaunchtype % 1000, the thousands its launch
                # special (JE_makeEnemy; 1: only in line with the player, the launched one on its
                # link). Brought in, it is of the second bank (IMPORT_ENEMIES), which launches the
                # whole number: the enemy it launches, without the special.
                other %= 1000
            if 0 < other <= tyrdata.ENEMY_NUM:
                struct.pack_into("<H", record, at, self.enemy(episode, other))
        self.data[self.enemies[new]:self.enemies[new] + ENEMY_SIZE] = record

    def enemy(self, episode, number):
        """An enemy of an episode as an enemy number of episode 6 (the same number when it is
        the same there)."""
        if number <= 0 or episode == 5 or self._same_enemy(episode, number):
            return number
        key = (episode, number)
        if key in self.enemy_map:
            return self.enemy_map[key]
        new = self.free_enemies.pop(0)
        self.enemy_map[key] = new
        self._fill(episode, number, new)
        return new
