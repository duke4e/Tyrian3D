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

    def boss_links(self):
        """The links of the last boss bar (the level's boss; earlier bars are mid-bosses)."""
        bars = [e for e in self.events if e["type"] == 79 and e["t"] < 60000 and (e["d1"] or e["d2"])]
        if not bars:
            return set()
        last = max(bars, key=lambda e: e["t"])
        return {v for v in (last["d1"], last["d2"]) if v}

    def boss(self):
        """The boss block: its time (the first event of it) and events (times relative to it), or
        None. It starts at the boss enemies' first spawn, or the warning before it."""
        links = self.boss_links()
        if not links:
            return None
        spawn_times = [e["t"] for e in self.events if e["type"] in SPAWNS and e["d4"] in links and e["t"] < 60000]
        if not spawn_times:
            return None
        start = min(spawn_times)
        warning = [e["t"] for e in self.events if e["type"] == 16 and start - 400 <= e["t"] <= start]
        start = min(warning + [start])
        block = []
        for e in self.events:
            if e["t"] < start or e["t"] >= 60000:
                continue
            link = by_link(e)
            if link in links or e["type"] in BOSS_SCRIPT and e["type"] != 2 or e["type"] == 39 and e["d1"] in links:
                block.append(dict(e, t=e["t"] - start))
        return dict(start=start, events=block, links=links)

    def waves(self, max_gap=40, max_count=16, span=1500):
        """Sky and top waves: spawns in a row (no gap over max_gap, the same kind of enemy, at
        most max_count), with the events on their links up to span after the wave's start."""
        boss = self.boss_links()
        events = [e for e in self.events if e["t"] < 60000]
        ground_links = {e["d4"] for e in events if e["type"] in GROUND_SPAWNS and e["d4"]}
        spawns = [e for e in events if e["type"] in SKY_SPAWNS | TOP_SPAWNS and e["d4"] not in boss
                  and e["d4"] not in ground_links]
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
            evs = sorted(w["spawns"] + attached[i], key=lambda e: e["t"])
            evs = [dict(e, t=e["t"] - w["start"]) for e in evs]
            enemies = [e["d1"] for e in w["spawns"]]
            out.append(dict(source=(self.episode, self.name), start=w["start"], events=evs, links=sorted(links),
                            enemies=enemies, count=len(enemies), length=max(e["t"] for e in evs),
                            armor=sum(min(self.enemies[x]["armor"], 100) for x in enemies if x in self.enemies),
                            banks=sorted({self.enemies[x]["shapebank"] for x in enemies if x in self.enemies})))
        return out

    def ground_objects(self):
        """Stationary ground enemies: enemy type -> Counter of the layer 1 shapes they stood on."""
        moving = {by_link(e) for e in self.events if e["type"] in (19, 20, 55, 74) and by_link(e)}
        table = self.level.map_sh[0]
        rows = [self.level.maps[0][r * 14:(r + 1) * 14] for r in range(300)]
        out = defaultdict(Counter)
        for e in self.events:
            if e["type"] not in (6, 10) or e["t"] >= 60000 or e["d4"] in moving or e["d2"] in (-99, -200):
                continue
            enemy = self.enemies.get(e["d1"])
            if not enemy or enemy["xmove"] or enemy["ymove"] or enemy["xaccel"] or enemy["yaccel"]:
                continue
            col = (e["d2"] + 30) / 24
            row = 291 - (e["t"] + 8 - e["d5"]) / 28
            c, r = round(col), round(row)
            if abs(col - c) > 0.1 or abs(row - r) > 0.1 or not (0 <= c < 14 and 0 <= r < 300):
                continue
            out[e["d1"]][table[rows[r][c]]] += 1
        return out
