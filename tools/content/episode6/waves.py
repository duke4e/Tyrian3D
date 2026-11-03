"""Wave templates from the original levels, for episode 6's new levels (tools/content/EVENTS.md).

A wave is a group of enemies that come together, with the events that steer them later by their
link numbers (moves, accelerations, fire, drops); placed in a new level at another time with new
link numbers, it plays as it did. A level's boss is the same kind of block: the enemies of its
boss bar's links and the events around it (the warning, the bar, the end when it is gone).
Ground enemies are not moved in waves (they stand on the map); stationary ones are placed anew by
the tiles they stood on (`ground_objects`).
"""
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import levels  # noqa: E402
import tyrdata  # noqa: E402
import tyrevents  # noqa: E402

SKY_SPAWNS = {15, 18}             # sky enemies (at the top; 18 from the bottom)
TOP_SPAWNS = {7, 23, 32}          # top layer
GROUND_SPAWNS = {6, 10, 12, 17, 56}
SPAWNS = SKY_SPAWNS | TOP_SPAWNS | GROUND_SPAWNS
# Enemy 0 drawn as a sprite (d1) of a sheet (d3), with its armour (d6), on a link (d4): parts of
# bosses (FLEET's walker, TORM's and BOTANY A's shells). Kept with a boss only: a wave never takes
# them (their sheets may not be loaded where it goes).
CUSTOM_SPAWNS = {49, 50, 51, 52}
# Events that act on the enemies of one link (d4), when their selection is by link.
LINK_EVENTS = {19, 20, 24, 25, 27, 31, 33, 45, 47, 55, 58, 59, 60, 68, 74}
# Events a level's script uses around its boss (kept with the boss block).
BOSS_SCRIPT = {2, 4, 16, 30, 34, 35, 36, 46, 53, 62, 79, 83}
JUMPS = {38, 54, 61, 66, 67, 70, 71, 75, 76, 80}


def by_link(e):
    """The link an event acts on, or None (it acts on all, a layer, or no enemy)."""
    t, d3, d4 = e["type"], e["d3"], e["d4"]
    if t in SPAWNS:
        return d4 or None
    if t not in LINK_EVENTS or d4 == 0:
        return None
    if t == 19 and d3 != 0:
        return None
    if t in (20, 27, 55) and 80 <= d3 <= 89:
        return None
    if t in (31, 58) and d4 == 99:
        return None
    return d4


def sheets_of(enemies, number, seen=None):
    """The sheets an enemy needs: its own, and those of the enemies it launches or leaves."""
    seen = set() if seen is None else seen
    if number in seen or number not in enemies:
        return set()
    seen.add(number)
    e = enemies[number]
    out = {e["shapebank"]}
    for other in (e["elaunchtype"] % 1000 if e["elaunchfreq"] else 0, e["eenemydie"]):
        if 0 < other:
            out |= sheets_of(enemies, other, seen)
    return out - {21, 26}  # (always there)


class Source:
    """An original level: its events, enemy data episode, waves, boss, ground objects."""

    def __init__(self, episode, name, number=None):
        data_dir = tyrdata.DATA
        self.episode = episode
        self.name = name
        self.items = tyrdata.load_items(episode)
        data, n, pos = tyrdata.lvl_positions(os.path.join(data_dir, f"tyrian{episode}.lvl"))
        if number is None:
            for s in levels.read_strings(os.path.join(data_dir, f"levels{episode}.dat")):
                if s.startswith("]L") and s[13:22].strip() == name:
                    number = int(s[25:27])
                    break
        self.number = number
        self.level = tyrevents.Level(data, pos[(number - 1) * 2])
        self.events = self.level.events
        self.enemies = self.items["enemies"]
        # The small enemies' adjustment each spawn is made under (event 26: DELIANI, DELI and New Deli
        # turn it on for their first part, BONUS for all of it: their 1x1 enemies 10 px left and 7
        # up, as the multi-sprite cannons' muzzle pieces need), so that a new level makes them so too
        # (compose.with_small_adjust).
        adjust = 0
        for e in self.events:
            if e["type"] == 26:
                adjust = e["d1"]
            elif adjust and e["type"] in SPAWNS:
                e["adjust"] = adjust

    def boss_links(self):
        """The links of the last boss bar (the level's boss; earlier bars are mid-bosses)."""
        bars = [e for e in self.events if e["type"] == 79 and e["t"] < 60000 and (e["d1"] or e["d2"])]
        if not bars:
            return set()
        last = max(bars, key=lambda e: e["t"])
        return {v for v in (last["d1"], last["d2"]) if v}

    def boss(self, stages=False):
        """The boss block: its time (the first event of it) and events (times relative to it), or
        None. It starts at the boss enemies' first spawn, or the warning before it.

        stages: a boss fought in stages taken whole (DREAD-NOT's five parts, ASSASSIN's two; the
        user, 2026-11-03, of GRAVITRON: "ne mogu ubiti glavnoga"): the bars before its last one, from
        its block on, and the links its jumps look for (70) are the boss's too, and its jumps from one
        stage to the next and round a stage (70, 54; 71, where the map stops for it) are kept, their
        targets as far into the block ("jump", for compose.place). Without them only its last part
        came, shot at only when its stages' time had run out."""
        links = self.boss_links()
        if not links:
            return None

        def first(links):
            spawn_times = [e["t"] for e in self.events if e["type"] in SPAWNS and e["d4"] in links and e["t"] < 60000]
            if not spawn_times:
                return None
            start = min(spawn_times)
            warning = [e["t"] for e in self.events if e["type"] == 16 and start - 400 <= e["t"] <= start]
            return min(warning + [start])

        def linked(e):
            return e["d4"] if e["type"] in CUSTOM_SPAWNS else by_link(e)

        start = first(links)
        if start is None:
            return None
        staged = False
        while stages:
            end = max(e["t"] for e in self.events if e["t"] < 60000 and linked(e) in links)
            more = set()
            for e in self.events:
                if start <= e["t"] <= end and e["type"] == 79:
                    more |= {v for v in (e["d1"], e["d2"]) if v}
                elif start <= e["t"] <= end and e["type"] == 70 and e["d2"]:
                    more |= {v for v in (e["d2"], e["d3"] & 0xFF, e["d4"]) if v}
            if more <= links:
                break
            links, staged = links | more, True
            start = first(links)
        end = max(e["t"] for e in self.events if e["t"] < 60000 and linked(e) in links)
        block = []
        for e in self.events:
            if e["t"] < start or e["t"] >= 60000:
                continue
            if linked(e) in links or e["type"] in BOSS_SCRIPT and e["type"] != 2 or e["type"] == 39 and e["d1"] in links:
                block.append(dict(e, t=e["t"] - start))
            elif staged and e["type"] in (54, 70, 71) and e["t"] <= end and (e["type"] != 70 or e["d2"]):
                if e["type"] == 54 and e["d1"] == -1:
                    block.append(dict(e, t=e["t"] - start))  # (a return)
                elif start <= e["d1"] <= end:
                    block.append(dict(e, t=e["t"] - start, jump=e["d1"] - start))
        return dict(start=start, events=block, links=links)

    def waves(self, max_gap=40, max_count=16, span=1500, ground=False):
        """Sky and top waves: spawns in a row (no gap over max_gap, the same kind of enemy, at
        most max_count), with the events on their links up to span after the wave's start.
        ground: ground enemies too (levels over open space, where nothing under them matters:
        asteroids)."""
        boss = self.boss_links()
        events = [e for e in self.events if e["t"] < 60000]
        ground_links = set() if ground else {e["d4"] for e in events if e["type"] in GROUND_SPAWNS and e["d4"]}
        kinds = SKY_SPAWNS | TOP_SPAWNS | (GROUND_SPAWNS if ground else set())
        spawns = [e for e in events if e["type"] in kinds and e["d4"] not in boss and e["d4"] not in ground_links]
        waves = []
        for e in spawns:
            w = waves[-1] if waves else None
            if (w is None or e["t"] - w["last_spawn"] > max_gap or len(w["spawns"]) >= max_count or
                    (e["d1"] != w["spawns"][-1]["d1"] and e["t"] - w["last_spawn"] > 10)):
                waves.append(dict(start=e["t"], spawns=[e], last_spawn=e["t"]))
            else:
                w["spawns"].append(e)
                w["last_spawn"] = e["t"]
        # A link's events belong to the latest wave before them that spawned it (levels reuse
        # link numbers).
        spawned = [{e["d4"] for e in w["spawns"] if e["d4"]} for w in waves]
        attached = [[] for _ in waves]
        for e in events:
            link = by_link(e) if e["type"] not in SPAWNS else None
            if e["type"] == 39:
                link = e["d1"]
            if not link:
                continue
            for i in range(len(waves) - 1, -1, -1):
                if waves[i]["start"] <= e["t"] and link in spawned[i]:
                    if e["t"] <= waves[i]["start"] + span:
                        attached[i].append(e)
                    break
        out = []
        for i, w in enumerate(waves):
            links = spawned[i]
            evs = sorted(w["spawns"] + attached[i] + self.arch_parts(w["spawns"]), key=lambda e: e["t"])
            evs = [dict(e, t=e["t"] - w["start"]) for e in evs]
            enemies = [e["d1"] for e in w["spawns"]]
            # (Sheets: of the enemies, what they launch or leave, and what the wave's events put in.)
            made = enemies + [e["d1"] for e in evs if e["type"] in (33, 59, 68) and e["d1"] > 0]
            sheets = set().union(*(sheets_of(self.enemies, x) for x in made)) if made else set()
            out.append(dict(source=(self.episode, self.name), start=w["start"], events=evs, links=sorted(links),
                            enemies=enemies, count=len(enemies), length=max(e["t"] for e in evs),
                            armor=sum(min(self.enemies[x]["armor"], 100) for x in enemies if x in self.enemies),
                            banks=sorted(sheets)))
        return out

    # The tan rock arch of SURFACE and DESERTRUN (assets/models/models.cfg): its top row (162, 164, the span's 166, 168,
    # 170, the right leg's 241) over its bottom row (the left foot 198, 200, 202, the span's 204, 206, 208, 279, the
    # right feet 281, 282), 24 pixels a column, the span's bottom piece 38 sprites on from its top one.
    ARCH_TOP = (162, 164, 166, 168, 170)
    ARCH_SPAN = (166, 168, 170)

    def arch_parts(self, spawns):
        """What a wave's rock arches lack of themselves, as top enemies made with them: the originals make an arch's
        feet now and then on the ground (layer 1: a wave leaves them out) and stand something else in its middle
        (SURFACE's gun hut, on a link its ground enemies use too: a wave leaves it out), so in a new level an arch
        stood in two halves (ROOST, COLLECTOR). The feet are made at the top layer with the rest, the middle bridged
        with the span's columns."""
        def graphic(e):
            en = self.enemies.get(e["d1"])
            return (en["shapebank"], en["egraphic"][0]) if en and e["type"] in TOP_SPAWNS else (None, None)

        legs = [e for e in spawns if graphic(e)[1] == 241]
        out = []
        for leg in legs:
            bank = graphic(leg)[0]
            ids = {}
            for number, en in sorted(self.enemies.items()):
                if en["shapebank"] == bank and not en["xmove"] and not en["ymove"]:
                    ids.setdefault(en["egraphic"][0], number)
            same = [e for e in spawns if e["t"] == leg["t"] and graphic(e)[0] == bank]
            have = {(graphic(e)[1], e["d2"]) for e in same}
            top = [e["d2"] for e in same if graphic(e)[1] in self.ARCH_TOP and e["d2"] < leg["d2"]]
            if not top:
                continue
            row, low = leg["d5"], leg["d5"] + 28

            def part(number, x, y):
                if number in ids and (number, x) not in have:
                    out.append(dict(leg, d1=ids[number], d2=x, d5=y))

            for k, x in enumerate(range(max(top) + 24, leg["d2"], 24)):
                span = self.ARCH_SPAN[min(k, 2)]
                part(span, x, row)
                part(span + 38, x, low)
            for number, x in ((198, min(top) - 24), (281, leg["d2"] + 24), (282, leg["d2"] + 36)):
                if not any(graphic(e)[1] == number for e in same):
                    part(number, x, low)
        return out

    def map_grid(self):
        """Layer 1 as rows of shape numbers."""
        table = self.level.map_sh[0]
        raw = self.level.maps[0]
        return [[table[raw[r * 14 + c]] if raw[r * 14 + c] < 128 else 0 for c in range(14)] for r in range(300)]

    def ground_objects(self):
        """Stationary ground enemies and the tiles under them: a list of (key, kind, enemy), key
        the shape under a 1-tile enemy (events 6, 10) or the 2x2 shapes under a 4-part one (12,
        its first part's enemy number), kind the event type."""
        moving = {by_link(e) for e in self.events if e["type"] in (19, 20, 55, 74) and by_link(e)}
        grid = self.map_grid()
        out = []
        for e in self.events:
            if e["type"] not in (6, 10, 12) or e["t"] >= 60000 or e["d4"] in moving or e["d2"] in (-99, -200):
                continue
            if e["type"] == 12 and e["d6"] not in (0, 1):
                continue  # 4-part enemies on other layers
            enemy = self.enemies.get(e["d1"])
            if not enemy or enemy["xmove"] or enemy["ymove"] or enemy["xaccel"] or enemy["yaccel"]:
                continue
            col = (e["d2"] + 30) / 24
            row = 291 - (e["t"] + 8 - e["d5"]) / 28
            c, r = round(col), round(row)
            if abs(col - c) > 0.1 or abs(row - r) > 0.1:
                continue
            if e["type"] == 12:
                # Parts: +1 x+24, +2 y-28 (the row above), +3 both.
                if not (0 <= c < 13 and 1 <= r < 300):
                    continue
                key = (grid[r - 1][c], grid[r - 1][c + 1], grid[r][c], grid[r][c + 1])
            else:
                if not (0 <= c < 14 and 0 <= r < 300):
                    continue
                key = grid[r][c]
            out.append((key, e["type"], e["d1"]))
        return out


_originals = {}


def originals(episodes=(1, 2, 3, 4, 5)):
    """Every original level of these episodes (once each; those the decoder reads)."""
    out = []
    for ep in episodes:
        if ep not in _originals:
            _originals[ep] = []
            names = [s[13:22].strip() for s in levels.read_strings(os.path.join(tyrdata.DATA, f"levels{ep}.dat"))
                     if s.startswith("]L")]
            for name in dict.fromkeys(names):
                try:
                    _originals[ep].append(Source(ep, name))
                except (IndexError, TypeError, ValueError):
                    pass  # (names the script has twice or not as a level of its own)
        out += _originals[ep]
    return out
