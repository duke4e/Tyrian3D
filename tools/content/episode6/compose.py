"""Composing an episode 6 level's events: waves of the original levels placed anew along a
difficulty curve, stationary ground enemies on the tiles of the new map that suit them, the boss
block at the end (tools/content/EVENTS.md has the rules this follows).

Events are dicts as tyrevents reads them (t, type, d1..d6, d4); an event naming an enemy (its d1)
carries the episode it is from ("ep"), so the build can bring it into episode 6's item data.
"""
import random
from collections import Counter, defaultdict

import tyrevents
import waves as W

LAYER1_ROWS = 300
CLOCK_END = 8148          # layer 1 runs out here (EVENTS.md 3)
ENEMY_D1 = W.SPAWNS | {33, 45, 59, 68}  # events whose d1 is an enemy
COURIER_LINK = 40         # the secret couriers' (waves get links 1-39)
DATA_CUBE = 512           # the item data's data cube (value 1; sheet 21, always there)
WARP_ORB = 593            # a warp orb (sheet 20); the build gives each secret level its own
WARP_SHEET = 20
SPECIAL_PICKUP = 1296     # a special weapon's pickup (sheet 26, always there); the build sets which special


def event(t, type_, d1=0, d2=0, d3=0, d5=0, d6=0, d4=0, ep=None):
    e = dict(t=int(t), type=type_, d1=d1, d2=d2, d3=d3, d5=d5, d6=d6, d4=d4)
    if ep is not None:
        e["ep"] = ep
    return e


def row_at(t):
    """The layer 1 row at the top of the screen at clock t."""
    return 292 - (t + 27) // 28


def ground_time(row):
    """The clock at which a ground enemy spawned at the top edge sits on this row (the originals'
    convention, EVENTS.md 3)."""
    return 28 * (291 - row) - 8


class Links:
    """Link numbers for placed waves: a wave's links become free ones (the originals reuse 1-40
    for ordinary groups; above 40, links of a block of 20 die together, so those keep their place
    in a block)."""

    def __init__(self):
        self.busy = {}  # link -> clock until which it is in use

    def remap(self, links, start, end):
        mapping = {}
        for link in sorted(links):
            if link <= 40:
                for new in range(1, COURIER_LINK):
                    if self.busy.get(new, -1) < start and new not in mapping.values():
                        mapping[link] = new
                        break
            else:
                new = link
                while self.busy.get(new, -1) >= start and new + 20 < 254:
                    new += 20
                mapping[link] = new
        for new in mapping.values():
            self.busy[new] = end
        return mapping


def place(template, start, links, ep):
    """A wave or boss template's events at a new start, with new link numbers."""
    mapping = links.remap(set(template["links"]) | {e["d4"] for e in template["events"] if e["d4"]},
                          start, start + template.get("length", 0) + 600)
    out = []
    for e in template["events"]:
        e = dict(e)
        e["t"] = start + e["t"]
        jump = e.pop("jump", None)
        if jump == "exit":
            e["d1"] = start + template["loop"][1] + 2
        elif jump == "loop":
            e["d1"] = start + template["loop"][0]
        elif isinstance(jump, int):
            e["d1"] = start + jump  # (the boss's own jumps: when it dies, boss_jumps; its stages, waves.Source.boss)
        elif jump == "gone":
            e["gone"] = True  # (its target, past the level's end, set by expand)
        if "jump2" in e:
            e["d2"] = start + e.pop("jump2")  # (a level timer's: fight_template)
        if e["d4"] in mapping and (e["type"] in W.SPAWNS | W.CUSTOM_SPAWNS | {TOUGH} or W.by_link(e) is not None):
            e["d4"] = mapping[e["d4"]]
        if e["type"] == 39:
            e["d1"] = mapping.get(e["d1"], e["d1"])
            e["d2"] = mapping.get(e["d2"], e["d2"])
        if e["type"] == 79:
            e["d1"] = mapping.get(e["d1"], e["d1"])
            e["d2"] = mapping.get(e["d2"], e["d2"])
        if e["type"] == 70 and e["d2"]:
            e["d2"] = mapping.get(e["d2"], e["d2"])
            e["d4"] = mapping.get(e["d4"], e["d4"])
            if e["d3"]:  # (a third link, a signed byte in the file: DREAD-NOT's 141 is -115)
                d3 = mapping.get(e["d3"] & 0xFF, e["d3"] & 0xFF)
                e["d3"] = d3 - 256 if d3 > 127 else d3
        if e["type"] in ENEMY_D1:
            e["ep"] = ep
            if e["type"] in (33, 45) and e["d1"] in (512, 513):
                # An original's data cube: episode 6's cubes are its own (story.py).
                e["d1"], e["ep"] = 396, 5
            elif e["type"] in W.SPAWNS and W.tyrdata.load_items(ep)["enemies"].get(e["d1"], {}).get("value") == 1:
                # (an original's cube made as an enemy: TYRIAN X's boss's 53; a coin instead)
                e["d1"], e["ep"] = 396, 5
        out.append(e)
    return out


def expand(level):
    """A level's events: its own (ground enemies, settings) and its placements (waves and the boss
    of the original levels, by reference: they are the game's data, read at build time), with new
    link numbers, in time order."""
    links = Links()
    sources = {}
    placed = []
    end = None
    boss_block = None
    for p in sorted(level["placements"], key=lambda p: p["start"]):
        key = (p["episode"], p["name"])
        if key not in sources:
            sources[key] = W.Source(*key)
        source = sources[key]
        if p["kind"] == "boss":
            template = dict(source.boss(stages=True), length=CLOCK_END - p["start"])
            if level.get("banks"):
                # (Its parts on a sheet the level doesn't load would be there unseen, shot at blind:
                # DREAD-NOT's four guns in GRAVITRON. Left out, their stage's jump finds them gone.)
                loaded = set(level["banks"]) | {21, 26}
                template["events"] = [e for e in template["events"] if e["type"] not in W.SPAWNS or
                                      source.enemies[e["d1"]]["shapebank"] in loaded]
            template["events"] = template["events"] + boss_speeds(source, template, speed_at(level["events"], p["start"])) + \
                boss_jumps(source, template)
            if not any(e["type"] in (36, 57) for e in template["events"]):
                # (A boss whose original ends otherwise, ASTEROID2's by its map's restart: the level
                # ends once it is gone.)
                first = min(e["t"] for e in template["events"] if e["type"] in W.SPAWNS | W.CUSTOM_SPAWNS)
                template["events"].append(event(first + 1, 36))
            template["events"] = shorter_invulnerable(template["events"], source)
            template["events"] = sorted(template["events"] + boss_gone(template, p.get("flip")), key=lambda e: e["t"])
            end = boss_end(source, template, p["start"])
            boss_block = (source, template, p["start"])
        elif p["kind"] == "midboss":
            template = midboss_template(source, p)
        elif p["kind"] == "fight":
            template = fight_template(source, p)
        else:
            template = source.waves(ground=p.get("ground", False))[p["index"]]
            template = dict(template, events=without_still_tops(source, template["events"],
                                                                 speed_at(level["events"], p["start"])[2]))
        events = place(template, p["start"], links, source.episode)
        if p.get("drop"):
            events = with_drops(events, p["drop"])
        placed += events
    if boss_block:
        placed += escorts(level, *boss_block, links)
    own = [dict(e, t=max(e["t"], end)) if end is not None and e["type"] == 11 else e for e in level["events"]]
    # What a boss's end does (boss_gone) lies well past the level's end, reached only by its jumps.
    if any("gone" in e for e in placed):
        past = max(e["t"] for e in own + placed if "gone" not in e) + 1000
        for e in placed:
            mark = e.pop("gone", None)
            if mark is False:
                e["t"] = past   # (what it does)
            elif mark:
                e["d1"] = past  # (a look for the boss that jumps there)
    head = [e for e in own if e["t"] == 0]
    rest = [e for e in own if e["t"] > 0]
    return counted_skips(with_small_adjust(head + sorted(rest + placed, key=lambda e: e["t"])))


def speed_at(events, t):
    """The layers' speeds (event 2) in force at t."""
    speeds = (1, 2, 3)
    for e in sorted(events, key=lambda e: e["t"]):
        if e["t"] > t:
            break
        if e["type"] == 2:
            speeds = (e["d1"], e["d2"], e["d3"])
    return speeds


def boss_speeds(source, boss, level_speeds):
    """Speed events (2) for an original's boss placed in a new level whose layers go at
    level_speeds there: the layers that carry its enemies (1 its ground and ground 2 ones, 3 its
    top ones; sky ones ride none) as the original had them when its boss came and changed them
    after, and the whole map stopped where the original stops it once its boss is in place (the
    clock running on: 53). Without them a top or ground boss rose off the screen or drifted down
    with a map that went another speed (TORM's in GREY MOON never came into view). The layers that
    carry none of its enemies keep the new level's speeds."""
    carried = {tyrevents.SPAWN_OFFSET[e["type"]] for e in boss["events"] if e["type"] in tyrevents.SPAWN_OFFSET}
    ground, top = bool(carried & {25, 75}), 50 in carried
    end = boss["start"] + max(e["t"] for e in boss["events"])
    changes = [(0, speed_at(source.events, boss["start"]))] + \
        [(e["t"] - boss["start"], (e["d1"], e["d2"], e["d3"])) for e in source.events
         if e["type"] == 2 and boss["start"] <= e["t"] <= end]
    forced = {e["t"] for e in boss["events"] if e["type"] == 53 and e["d1"] != 99}
    out, now = [], tuple(level_speeds)
    for t, speeds in changes:
        if t > 0 and speeds == (0, 0, 0):
            new = speeds
        else:
            new = (speeds[0] if ground else level_speeds[0], level_speeds[1], speeds[2] if top else level_speeds[2])
        if new != now:
            out.append(event(t, 2, *new))
            if new[0] == 0 and t not in forced:
                out.append(event(t, 53))
            now = new
    return out


def boss_jumps(source, boss):
    """The original's jumps when its boss dies (57: the clock jumps to d1 when a link-254 enemy
    dies), from just before its block to its end, their targets as far into the block (place()
    makes them absolute): how BRAINIAC, FLEET and GEM WAR go on (GEM WAR to its second wave, then
    to the level's end)."""
    end = boss["start"] + max(e["t"] for e in boss["events"])
    out = []
    for e in source.events:
        if e["type"] == 57 and boss["start"] - 100 <= e["t"] <= end:
            jump = dict(event(e["t"] - boss["start"], 57, d1=e["d1"]))
            if e["d1"]:
                jump["jump"] = e["d1"] - boss["start"]
            out.append(jump)
    return out


def without_still_tops(source, events, top_speed):
    """A wave's events without its top enemies that would never come into view: where the new
    level's layer 3 stands (top_speed 0) the ones that ride it with no move of their own (no y speed
    in their data or their spawn, no event on their link) stay where they are made, above the
    screen, and fill the top enemies' 25 slots (SURFACE's pyramids in COLLECTOR: its boss could
    never be made)."""
    if top_speed:
        return events
    linked = {W.by_link(e) for e in events if e["type"] not in W.SPAWNS} - {None}

    def still(e):
        if e["type"] not in W.TOP_SPAWNS or e["d1"] not in source.enemies:
            return False
        en = source.enemies[e["d1"]]
        return (not e["d3"] and not e["d6"] and e["d4"] not in linked and
                not en["ymove"] and not en["ycaccel"] and not en["yaccel"])
    return [e for e in events if not still(e)]


def boss_end(source, boss, start):
    """Where a level whose boss (placed at start) stops the map ends at the latest: where the
    original ends after its boss came, if that is later (with the map standing, layer 1 no longer
    runs out at CLOCK_END; the boss's end-when-clear, 36, ends it once the boss is gone). None when
    the boss doesn't stop the map."""
    if not any(e["type"] == 2 and e["d1"] == 0 for e in boss["events"]):
        return None
    ends = [e["t"] - boss["start"] for e in source.events if e["type"] == 11 and boss["start"] <= e["t"] < 60000]
    if not ends:
        return None
    # A jump when the boss dies leads to what the original does after it (BRAINIAC's 600 ticks of
    # stars speeding up, not in the block): the level ends soon after its target instead.
    targets = [e["jump"] for e in boss["events"] if e["type"] == 57 and "jump" in e]
    return start + (min(ends[0], max(targets) + 150) if targets else ends[0])


FLIP_LONGEST = 900  # clock the screen stays turned over at most while a boss is fought (EYESPY's: 930)


def boss_gone(boss, flip=False):
    """What an original's boss (a block at the level's end) does once it is gone: its wrecks sent
    down off the screen (pieces its pattern holds in place stayed as wrecks, holding up its end
    when clear, 36, until the level's last event: REEF's IXMUCANE, DEEP ICE's ASSASSIN, 20 s and
    more of nothing), its bar taken down. flip: the screen upside down while it is fought, as
    EYESPY's boss turns it (the user, 2026-11-03, of ROOST's turn by the clock: "totalno bezveze"):
    a danger message, the turn once it is in place (100 after its last enemy is made), back once
    it is gone, or after FLIP_LONGEST; none if it is gone before. It is looked for every 25 from
    its last enemy on (70: its links dead) with a jump to those events, past the level's end,
    which return (54 -1), so none of the boss's own events is passed over (its pattern moving the
    wrecks again in between: sent down again at the next look). None for a boss of more than
    three links (70 looks for three: DREAD-NOT's stages end the level their own way)."""
    links = sorted(boss["links"])
    if len(links) > 3:
        return []
    a, b, c = (links + [0, 0])[:3]
    made = max(e["t"] for e in boss["events"] if e["type"] in W.SPAWNS | W.CUSTOM_SPAWNS)
    end = max(e["t"] for e in boss["events"])
    at = made + 100
    looks = {t: dict(event(t, 70, d1=-1, d2=a, d3=c - 256 if c > 127 else c, d4=b), jump="gone")
             for t in range(at - 75, end + 600, 25)}
    out = list(looks.values())
    done = [event(0, 20, d4=link) for link in links] + [event(0, 19, d2=3, d4=link) for link in links] + [event(0, 79)]
    if flip:
        # (the turn after the look at its time, which passes it by when the boss is gone)
        out = [e for e in out if e["t"] <= at] + [event(at - 40, 16, d1=MESSAGE_DANGER, d2=30),
                                                   event(at, 64, d1=9, d2=1, d3=1),
                                                   event(at + FLIP_LONGEST, 64, d1=9, d2=0)] + \
            [e for e in out if e["t"] > at]
        done.insert(0, event(0, 64, d1=9, d2=0))
    return out + [dict(e, gone=False) for e in done + [event(0, 54, d1=-1)]]


MAX_INVULNERABLE = 350  # clock a boss's part may stand unshootable unless a stage before it holds it there


def shorter_invulnerable(events, source):
    """A boss block's events with its parts shootable sooner: a part made unshootable (armour 255 in its data or
    its spawn, or set so by 25) and made shootable later by 25 waits at most MAX_INVULNERABLE, unless a jump of its
    pattern lies between (a stage that must be cleared first: ASSASSIN's second, DREAD-NOT's stages): the 25 and the
    bar that comes with it (79 on its link) come sooner (the user, 2026-11-03: "skratiti vrijeme glavnih kad su
    besmrtni, osim ako nemaju neki event koji to opravdava"; BRAINIAC's brain stood unshootable 1000 clock)."""
    jumps = [e["t"] for e in events if e["type"] in (54, 70, 71)]
    since, moves = {}, {}
    for e in sorted(events, key=lambda e: e["t"]):
        link = e["d4"]
        if not link:
            continue
        if e["type"] in W.SPAWNS:
            en = source.enemies.get(e["d1"])
            if en and en["armor"] == 255:
                since.setdefault(link, e["t"])
        elif e["type"] in W.CUSTOM_SPAWNS and e["d6"] == 255:
            since.setdefault(link, e["t"])
        elif e["type"] == 25:
            if e["d1"] >= 255:
                since.setdefault(link, e["t"])
                continue
            t0 = since.pop(link, None)
            if t0 is not None and e["t"] - t0 > MAX_INVULNERABLE and not any(t0 < j <= e["t"] for j in jumps):
                moves[(e["t"], link)] = t0 + MAX_INVULNERABLE
    out = []
    for e in events:
        to = moves.get((e["t"], e["d4"])) if e["type"] == 25 else None
        if e["type"] == 79:
            to = next((v for (t, link), v in moves.items() if t == e["t"] and link in (e["d1"], e["d2"])), None)
        out.append(dict(e, t=to) if to is not None else e)
    return sorted(out, key=lambda e: e["t"])


# The boss's escorts (the user, 2026-11-03: "glavnima dodat neke začine tipa razni protivnici koji ponavljaju neku
# patternu, štite glavne, gnjave igrača"): waves round it while it is fought, the same few in turn, from ESCORT_FIRST
# after its last part is made, every ESCORT_EVERY, ESCORT_COUNT of them; each skipped once it is gone (its last
# links set ESCORT_FLAG as they die, 60; each wave's events behind a 61 that skips them when it is set).
ESCORT_FLAG = 10  # (GYGES's script uses 1 and 2)
ESCORT_FIRST, ESCORT_EVERY, ESCORT_COUNT = 120, 420, 6
ESCORT_COIN = 393  # 75 credits an escort


def escort_waves(level, source, boss):
    """The waves that escort a boss: its own level's from round its fight (its escorts there), else the new level's
    own small ones; those the level's sheets show, two at most."""
    banks = set(level.get("banks") or []) | {21, 26}

    def fits(w, most):
        return set(w["banks"]) <= banks and 2 <= w["count"] <= most and w["length"] <= 600 and             not set(w["links"]) & set(boss["links"])
    own = [w for w in source.waves() if -600 <= w["start"] - boss["start"] <= 2500 and fits(w, 10)]
    if len(own) < 2:
        seen = set()
        for p in level["placements"]:
            if p["kind"] != "wave" or (p["episode"], p["name"], p["index"]) in seen:
                continue
            seen.add((p["episode"], p["name"], p["index"]))
            w = W.Source(p["episode"], p["name"]).waves(ground=p.get("ground", False))[p["index"]]
            if fits(w, 8):
                own.append(w)
    rnd = random.Random(level["name"])
    return rnd.sample(own, min(2, len(own))) if own else []


def escorts(level, source, boss, start, links):
    """The escorts' events (see escort_waves), placed; and the boss's last links marked (60) as it is made."""
    waves = escort_waves(level, source, boss)
    if not waves:
        return []
    made = max(e["t"] for e in boss["events"] if e["type"] in W.SPAWNS | W.CUSTOM_SPAWNS)
    out = [event(start + made + 2, 60, d1=ESCORT_FLAG, d2=1, d4=link) for link in sorted(source.boss_links())]
    for k in range(ESCORT_COUNT):
        t = start + made + ESCORT_FIRST + k * ESCORT_EVERY
        placed = with_drops(place(waves[k % len(waves)], t, links, source.episode), ESCORT_COIN)
        # (Only what makes its enemies is skipped: those already made keep their moves.)
        by_tick = defaultdict(list)
        for e in placed:
            by_tick[e["t"]].append(e)
        for tick in sorted(by_tick):
            making = [e for e in by_tick[tick] if e["type"] in W.SPAWNS | {33, 45}]
            if any(e["type"] in W.SPAWNS for e in making):
                group = f"escort{k}@{tick}"
                out.append(dict(event(tick, 61, d1=ESCORT_FLAG, d2=1), _skip=group))
                out += [dict(e, _group=group) for e in making]
            out += [e for e in by_tick[tick] if not any(e is m for m in making) or
                    not any(m["type"] in W.SPAWNS for m in making)]
    return out


def counted_skips(events):
    """The escorts' skips (61) counted as the events finally stand (with_small_adjust may have set an adjustment
    among them), their marks taken off."""
    out = [dict(e) for e in events]
    for i, e in enumerate(out):
        group = e.pop("_skip", None)
        if group is None:
            continue
        last = max(j for j in range(i + 1, len(out)) if out[j].get("_group") == group)
        e["d3"] = last - i
    for e in out:
        e.pop("_group", None)
    return out


def with_small_adjust(events):
    """The events with the small enemies' adjustment (26) set before every 1x1 enemy as its
    original made it ("adjust", waves.Source: on; off for the rest), and set again at every
    jump's target as it stands there, so a loop finds it as the level first came there. A level
    whose 1x1 enemies were all made without it is left as it is."""
    if not any(e.get("adjust") for e in events):
        return events
    enemies = {}

    def small(e):
        if "ep" not in e:
            return False
        data = enemies.setdefault(e["ep"], W.tyrdata.load_items(e["ep"])["enemies"])
        parts = [e["d1"] + k for k in range(4 if e["type"] == 12 else 1)]
        return any(data.get(n, {}).get("esize") == 0 for n in parts)

    out, state = [], 0
    for e in events:
        if e["type"] == 26:
            state = e["d1"]
        elif e["type"] in W.SPAWNS and small(e) and e.get("adjust", 0) != state:
            state = e.get("adjust", 0)
            out.append(event(e["t"], 26, d1=state))
        out.append(e)
    if len(out) == len(events):
        return events
    targets = sorted({e["d1"] for e in out if e["type"] in W.JUMPS and e["d1"] > 0})
    for target in reversed(targets):
        at = next((i for i, e in enumerate(out) if e["t"] >= target), None)
        if at is None or out[at]["type"] == 26:
            continue
        state = next((e["d1"] for e in reversed(out[:at]) if e["type"] == 26), 0)
        out.insert(at, event(out[at]["t"], 26, d1=state))
    return out


# --- Gimmicks (docs/plans/2026-10-09-epizoda-6.md, 7) --------------------------------------------

HOLD_LOOP = 600  # clock of a siege's round of waves
SIDE_AHEAD = 340  # seen from the side, how far the playfield reaches ahead (event 200's d3 x 10; tyrian2.c SIDE_AHEAD)
MIDBOSS_DROP = {36, 11, 4, 83, 2, 30, 53, 34, 35, 46}  # a boss block's level-ending and speed events
MESSAGE_BEHIND, MESSAGE_BOSS, MESSAGE_AFTERBURNER, MESSAGE_DANGER, MESSAGE_BONUS = 1, 2, 7, 8, 9


def midboss_span(source):
    """A mid-level boss's timing (relative to its block): where the map stops (where the original
    stops it, or once the boss is in view), and its loop: from after its last spawn and the stop to
    the end of its pattern (at most 900 on)."""
    boss = source.boss()
    events = [e for e in boss["events"] if e["type"] not in MIDBOSS_DROP]
    spawns = [e for e in events if e["type"] in W.SPAWNS]
    last_spawn = max(e["t"] for e in spawns)
    stops = sorted(e["t"] - boss["start"] for e in source.events
                   if e["type"] in (2, 30) and e["d1"] == 0 and 0 <= e["t"] - boss["start"] <= 1500)
    if stops:
        stop = stops[0]
    else:
        # Ground bosses come with the map: it runs until they are well in view.
        ground = any(e["type"] in W.GROUND_SPAWNS for e in spawns)
        stop = last_spawn + (190 if ground else 0)
    loop_from = max(stop, last_spawn) + 10
    pattern = max([e["t"] for e in events] + [loop_from + 200])
    return stop, loop_from, min(pattern, loop_from + 900)


def midboss_template(source, p):
    """A boss of an original level in the middle of a new one: the map stops (the clock running on,
    53), its pattern loops (54) until its enemies are gone (70), then the map goes on at the level's
    speeds; its level-ending events left out."""
    boss = source.boss()
    stop, loop_from, loop_to = p["loop"]
    events = [dict(e) for e in shorter_invulnerable(boss["events"], source) if e["type"] not in MIDBOSS_DROP and e["t"] <= loop_to
              and not (e["type"] == 79 and not e["d1"] and not e["d2"])]  # (its bar stays up)
    trim = p.get("trim", 0)
    if trim:
        # (Only the last of its approach (THE HOARD's fights, generate.make_hoard: p's loop is reckoned from there): what
        # it makes before that left out but the boss's own (its links'), its other events at its start, in their order.)
        events = [dict(e, t=max(0, e["t"] - trim)) for e in events
                  if e["t"] >= trim or e["type"] not in W.SPAWNS or e.get("d4") in boss["links"]]
    links = sorted(boss["links"])
    a, b = links[0], (links[1] if len(links) > 1 else 0)
    b1, b2, b3 = p["speeds"]
    if not any(e["type"] == 16 for e in events):
        events.insert(0, event(0, 16, d1=MESSAGE_BOSS))
    if p.get("dark"):
        # Lights out while it is fought (only the ship's spotlight), from where the map stops until it is gone.
        events.append(event(stop, 64, d1=6, d2=1, d3=1))
    if p.get("side"):
        # Seen from the side while it is fought (event 200: asteroids along the edges), from before it is made.
        events.insert(0, event(0, 200, d1=1, d2=1, d3=SIDE_AHEAD // 10))
    if p.get("chase"):
        # Seen from behind the ship while it is fought (Tyrian3D event 205: the chase camera).
        events.insert(0, event(0, 205, d1=1))
    if p.get("flip"):
        # The screen upside down while it is fought (as EYESPY's boss turns it), from where the map
        # stops (unless it is gone by then, all of it made: out at once) until it is gone.
        made = max(e["t"] for e in events if e["type"] in W.SPAWNS | W.CUSTOM_SPAWNS)
        events += [event(stop - 40, 16, d1=MESSAGE_DANGER, d2=30)] + \
            ([dict(event(stop, 70, d1=-1, d2=a, d4=b), jump="exit")] if stop > made else []) + \
            [event(stop, 64, d1=9, d2=1, d3=1)]
    events += [event(stop, 2), event(stop, 53)]
    # Out as soon as the boss is gone (looked for every 50), else round again. The jumps' targets
    # are set by place() (it makes the times absolute).
    events += [dict(event(t, 70, d1=-1, d2=a, d4=b), jump="exit") for t in range(loop_from + 50, loop_to + 1, 50)]
    events += [dict(event(loop_to, 70, d1=-1, d2=a, d4=b), jump="exit"),
               dict(event(loop_to, 54, d1=-1), jump="loop"),
               event(loop_to + 2, 2, d1=b1, d2=b2, d3=b3), event(loop_to + 2, 53, d1=99)]
    # Its wrecks go: pieces stopped in place (GYGES's sky ones, eyc 0) stayed on the screen as
    # wrecks for the rest of the level, holding up its end when clear (36) until its last event.
    # Every slot of its links (wrecks too) sent down off the screen, and its bar taken down.
    for link in (a, b) if b else (a,):
        events += [event(loop_to + 2, 20, d4=link), event(loop_to + 2, 19, d2=3, d4=link)]
    events.append(event(loop_to + 2, 79))
    if p.get("flip"):
        events.append(event(loop_to + 2, 64, d1=9, d2=0))
    if p.get("dark"):
        events.append(event(loop_to + 2, 64, d1=6, d2=0))
    if p.get("side"):
        events.append(event(loop_to + 2, 200, d1=0))
    if p.get("chase"):
        events.append(event(loop_to + 2, 205, d1=0))
    events.sort(key=lambda e: e["t"])
    return dict(events=events, links=links, length=loop_to + 2, loop=(loop_from, loop_to))


# THE HOARD's fights (the user, 2026-11-04: "iskopirati kompletne scenarije boss encountera iz svih levela. najčešće se
# radilo o nekom skriptiranom eventu gdje je bilo više toga za napraviti, dal se radilo o nekakvom štitu od protivnika
# (npr brainiac), ili nekim specifičnim protivnicima"; "dignuti health za x5"): each boss's whole encounter as its
# level has it, from a little before its warning to its level's end, what comes with it too (its shields, escorts,
# the enemies its script makes, its stages, its own map stops and jumps), but the map's own (ground) enemies, the
# level's settings and its end; the boss's links FIGHT_TOUGH times as tough (Tyrian3D event 206).
FIGHT_APPROACH = 200  # clock of a boss's approach a fight takes with it, before its warning or first part
FIGHT_TOUGH = 5
FIGHT_LOOK = 25       # clock between the looks for a fight's boss gone, once its level has run out
FIGHT_GONE = 120      # clock after its boss is gone to its end (its wrecks sent away; the next fight's sheets)
TOUGH, CLEAR_JUMP, CHECKPOINT, MARK = 206, 207, 208, 209  # Tyrian3D events: links made tougher; a jump once the
                                                          # screen is clear; a checkpoint (debugmode.c); nothing
# Events a fight leaves out: the level's settings (stars, sheets, random enemies, layers' order, palette, difficulty,
# the map's position and wraps), its end (11 and 36, made the fight's), and the skips by difficulty, flag or players
# (all of it comes: their counts would no longer hold). (Not the map's stops until the screen is clear, 4 and 83:
# ASTEROID1's boss holds the map so, and its clock with it.)
FIGHT_KEEP_OUT = {1, 3, 5, 8, 9, 11, 13, 14, 21, 22, 26, 28, 29, 34, 35, 37, 42, 43, 44, 46, 48, 61, 63, 65, 66,
                  72, 73, 77, 78, 80, 81, 82, 84, 85}
FIGHT_JUMPS = {38, 54, 67, 70, 71}  # (their target: d1; 67's d2)


def encounter(source):
    """An original's boss encounter: from FIGHT_APPROACH before its boss's warning (or first part, by the bars of its
    stages and the parts made from 1100 before the first of them, as BRAINIAC's and TORM's come down to their places: levels make enemies of those links early on too) to
    its level's end (its first 11 after the boss's last part is made; its last event if none). start, end (clock in
    its level), links (its stages'), final (its last bar's)."""
    boss = source.boss(stages=True)
    links = set(boss["links"])
    bars = [e["t"] for e in source.events if e["type"] == 79 and e["t"] < 60000 and {e["d1"], e["d2"]} & links]
    first_bar = min(bars)
    made = [e["t"] for e in source.events if e["type"] in W.SPAWNS | W.CUSTOM_SPAWNS and e["d4"] in links and
            first_bar - 1100 <= e["t"] < 60000]
    start = min(made + [first_bar])
    start = min([e["t"] for e in source.events if e["type"] == 16 and start - 400 <= e["t"] <= start] + [start])
    start = max(0, start - FIGHT_APPROACH)
    last_made = max(made + [first_bar])
    ends = [e["t"] for e in source.events if e["type"] == 11 and last_made <= e["t"] < 60000]
    end = min(ends) if ends else max(e["t"] for e in source.events if e["t"] < 60000)
    return dict(start=start, end=end, links=links, final=source.boss_links())


def fight_sheets_of(enemies, number, seen=None):
    """W.sheets_of, with what an enemy launches though its data never has it launch: the script makes it (31's
    launch rate: CAMANIS's 216 and 218 launch 596, of sheet 8, its fourth). (Without a rate, a launch type up to 20 is
    the speed it is aimed at the ship with when it is launched itself: 596's 4.)"""
    seen = set() if seen is None else seen
    if number in seen or number not in enemies:
        return set()
    seen.add(number)
    e = enemies[number]
    out = {e["shapebank"]}
    launched = e["elaunchtype"] % 1000 if number <= 1000 else e["elaunchtype"]
    for other in (launched if e["elaunchfreq"] or launched > 20 else 0, e["eenemydie"]):
        if 0 < other:
            out |= fight_sheets_of(enemies, other, seen)
    return out - {21, 26}


def encounter_sheets(source, enc):
    """The sheets an encounter's enemies need, the boss's first, then the others' by how many of them need each."""
    boss = Counter()
    others = Counter()
    for e in source.events:
        if enc["start"] <= e["t"] <= enc["end"] and e["type"] in W.SPAWNS | W.CUSTOM_SPAWNS | {33, 59, 68}:
            if e["type"] in W.CUSTOM_SPAWNS:
                need = {e["d3"]} - {21, 26}
            elif e["d1"] > 0:
                need = set().union(*(fight_sheets_of(source.enemies, e["d1"] + k) for k in range(4 if e["type"] == 12 else 1)))
            else:
                continue
            (boss if e["d4"] in enc["links"] else others).update(need)
    return [b for b, _ in boss.most_common()], [b for b, _ in others.most_common() if b not in boss]


def fight_template(source, p):
    """A boss's encounter (see encounter) as a block of a level whose map is open space (THE HOARD): its events but
    FIGHT_KEEP_OUT, the ground enemies not of its boss and the enemies whose sheets the fight hasn't loaded (p["banks"]),
    its jumps' targets as far into it (those before it its start, past it its hold), its parts' unshootable stretches
    shortened (shorter_invulnerable); its level's end (11) and what
    comes after the encounter a hold until the boss's last bar's links are gone (the clock running), then the fight's
    end; its end when clear (36) a jump to the fight's end once the screen is clear (or the boss long gone, 207). At its
    end its wrecks are sent away, its bars, toughness, effects, death jump and timer taken off, and the map goes on at
    the level's speeds (p["speeds"]). p's mechanics as midboss_template's (flip, dark, side, chase)."""
    enc = encounter(source)
    s, e_ = enc["start"], enc["end"]
    links, final = enc["links"], enc["final"]
    loaded = set(p["banks"]) | {21, 26, 0}
    window = [e for e in source.events if s <= e["t"] <= e_]

    def fits(e):
        if e["type"] in W.CUSTOM_SPAWNS:
            return e["d3"] in loaded
        parts = range(4 if e["type"] == 12 else 1)
        return all(fight_sheets_of(source.enemies, e["d1"] + k) <= loaded for k in parts)

    def taken(e):
        # (sky and top enemies; ground ones only the boss's: the others stood on its level's map)
        if e["type"] in W.CUSTOM_SPAWNS:
            return fits(e)
        sky = e["type"] not in W.GROUND_SPAWNS or e["type"] == 12 and e["d6"] in (2, 3)
        return fits(e) and (sky or e["d4"] in links)

    kept_links = set(links) | {e["d4"] for e in window if e["type"] in W.SPAWNS and taken(e)}

    def kept(ev):
        kind = ev["type"]
        if kind in (11, 36):
            return True
        if kind in FIGHT_KEEP_OUT or kind in W.SPAWNS | W.CUSTOM_SPAWNS and not taken(ev):
            return False
        if kind in (33, 45, 59, 68) and ev["d1"] > 0 and not fight_sheets_of(source.enemies, ev["d1"]) <= loaded:
            return False
        return kind in W.SPAWNS or W.by_link(ev) is None or W.by_link(ev) in kept_links

    window = [ev for ev in window if kept(ev)]
    # (Past its last event but its level's end, its hold: a level's end long after its boss, when the screen is
    # clear (New Deli's, 4000 clock on), is no fight's.)
    hold = max([ev["t"] for ev in window if ev["type"] != 11] + [s]) - s + 10
    end = hold + 60

    def target(t):
        return 0 if t < s else t - s if t - s < hold else hold

    events, effects = [], set()
    starting = [ev for ev in source.events if ev["t"] < s and ev["type"] in (2, 53, 57)]
    for kind in (2, 53, 57):
        last = [ev for ev in starting if ev["type"] == kind]
        if last and (kind != 57 or last[-1]["d1"] and s - last[-1]["t"] <= 600):
            events.append(dict(last[-1], t=0, **({"jump": target(last[-1]["d1"])} if kind == 57 else {})))
    for ev in window:
        t, kind = ev["t"] - s, ev["type"]
        if kind == 11:
            events.append(dict(event(min(t, hold - 5), 54), jump=hold))
            continue
        if kind == 36:
            events.append(dict(event(t, CLEAR_JUMP), jump=end))
            continue
        out = dict(ev, t=t)
        if kind == 67:
            out["jump2"] = target(ev["d2"])
        elif kind in FIGHT_JUMPS | {57} and ev["d1"] not in (-1, 65535) and not (kind == 57 and not ev["d1"]):
            out["jump"] = target(ev["d1"])
        if kind == 64 and ev["d2"]:
            effects.add(ev["d1"])
        events.append(out)
    events = shorter_invulnerable(events, source)
    # (A boss's death's jump and the level timer's are made outside the events, so the game runs the event before their
    # target again: nothing there, the last at its tick (BRAINIAC's pattern's loop came round again after its brain's
    # death, for ever).)
    events += [event(e["jump"] - 1, MARK) for e in events if e["type"] == 57 and "jump" in e]
    # (and the clock running where a boss's death leads: its parts shootable sooner, shorter_invulnerable, BRAINIAC's brain
    # went before its level stopped the map with the clock running, and its end, the map standing, stood still)
    events += [event(e["jump"], 53) for e in events if e["type"] == 57 and "jump" in e]
    events += [event(e["jump2"] - 1, MARK) for e in events if e["type"] == 67 and "jump2" in e]

    a, b, c = (sorted(final) + [0, 0])[:3]
    # The hold: the clock running, the boss's last stage looked for until it is gone.
    events += [event(hold, 2, d1=0, d2=0, d3=0), event(hold, 53)]
    events += [dict(event(t, 70, d1=-1, d2=a, d3=c, d4=b), jump=end) for t in range(hold + 1, end - 9, FIGHT_LOOK)]
    events.append(dict(event(end - 10, 54), jump=hold + 1))
    # Its toughness from its start; its mechanics.
    events += [event(0, TOUGH, d1=FIGHT_TOUGH, d4=link) for link in sorted(links)]
    made = [ev["t"] - s for ev in window if ev["type"] in W.SPAWNS | W.CUSTOM_SPAWNS and ev["d4"] in final]
    there = min(made) + 100 if made else 0
    if p.get("side"):
        events.append(event(0, 200, d1=1, d2=1, d3=SIDE_AHEAD // 10))
    if p.get("chase"):
        events.append(event(0, 205, d1=1))
    if p.get("dark"):
        events.append(event(there, 64, d1=6, d2=1, d3=1))
        effects.add(6)
    if p.get("flip"):
        events += [event(there - 40, 16, d1=MESSAGE_DANGER, d2=30), event(there, 64, d1=9, d2=1, d3=1)]
        if there + FLIP_LONGEST < hold:
            events.append(event(there + FLIP_LONGEST, 64, d1=9, d2=0))
        effects.add(9)
    # Its end.
    b1, b2, b3 = p["speeds"]
    done = [event(end, CLEAR_JUMP), event(end, 57), event(end, 67, d1=0), event(end, 79), event(end, 99, d1=0)]
    for link in sorted(links):
        done += [event(end, 20, d4=link), event(end, 19, d2=3, d4=link), event(end, TOUGH, d4=link)]
    done += [event(end, 64, d1=fx, d2=0) for fx in sorted(effects)]
    if p.get("side"):
        done.append(event(end, 200, d1=0))
    if p.get("chase"):
        done.append(event(end, 205, d1=0))
    # (on its tick: a jump there by 207 may find the clock standing)
    done += [event(end, 2, d1=b1, d2=b2, d3=b3), event(end, 53, d1=99)]
    events = sorted(events + done, key=lambda e: e["t"])
    return dict(events=events, links=sorted(kept_links - {0}), length=end + FIGHT_GONE)


# Credits: the coins and gems enemies can leave (the item data's enemies 390-399: 10, 25, 50, 75,
# 100, 250, 500, 1000, 2500 and 5000 credits; always loaded).
COINS = {390: 10, 391: 25, 392: 50, 393: 75, 394: 100, 395: 250, 396: 500, 397: 1000, 398: 2500, 399: 5000}


def with_drops(events, coin):
    """A placed wave's events with each linked enemy leaving a coin (event 33 after its spawn),
    unless the wave already gives its link a drop of its own."""
    own = {e["d4"] for e in events if e["type"] == 33}
    out = []
    for e in events:
        out.append(e)
        if e["type"] in W.SPAWNS and e["d4"] and e["d4"] not in own:
            out.append(event(e["t"], 33, d1=coin, d4=e["d4"], ep=5))
    return out


def pick_coin(rnd, value):
    """A coin worth about value (a little either way)."""
    target = value * rnd.uniform(0.6, 1.5)
    return min(COINS, key=lambda c: abs(COINS[c] - target))


def ground_banks(ground_sources, room):
    """The sheets of the ground enemies most used, up to room of them."""
    count = Counter()
    for s in ground_sources:
        for _, _, enemy in s.ground_objects():
            count[s.enemies[enemy]["shapebank"]] += 1
    return [b for b, _ in count.most_common(room)]


def place_ground(grid, ground_sources, banks, start, boss_time, rnd, density=None, min_rate=0.45):
    """Ground enemy events for a new map (see compose)."""
    found = Counter()       # key -> enemies found on it in the originals
    seen = Counter()        # key -> times it occurs in the originals' maps
    options = defaultdict(Counter)  # key -> (kind, episode, enemy) -> count
    for s in ground_sources:
        objects = [o for o in s.ground_objects() if W.sheets_of(s.enemies, o[2]) <= banks]
        if not objects:
            continue
        for key, kind, enemy in objects:
            found[key] += 1
            options[key][(kind, s.episode, enemy)] += 1
            banks.add(s.enemies[enemy]["shapebank"])
        g = s.map_grid()
        for r in range(300):
            for c in range(14):
                seen[g[r][c]] += 1
                if r >= 1 and c < 13:
                    seen[(g[r - 1][c], g[r - 1][c + 1], g[r][c], g[r][c + 1])] += 1
    rate = {k: found[k] / max(seen[k], found[k]) for k in found}
    events = []
    taken = set()
    for r in range(row_at(start + 100), row_at(boss_time - 200), -1):
        for c in range(1, 13):
            for key, size in (((grid[r - 1][c], grid[r - 1][c + 1], grid[r][c], grid[r][c + 1]), 2), (grid[r][c], 1)):
                if rate.get(key, 0) < min_rate:
                    continue
                if density and rnd.random() > density(r):
                    continue
                cells = {(r - dy, c + dx) for dy in range(size) for dx in range(size)}
                if any((rr, cc) in taken for rr, cc in cells):
                    continue
                if rnd.random() > rate[key]:
                    continue
                (kind, ep, enemy), = rnd.choices(list(options[key]), list(options[key].values()))
                taken |= cells
                events.append(event(ground_time(r), kind, d1=enemy, d2=24 * c - 30, ep=ep))
                break
    return events


def courier_events(t, prize, kinds, rnd):
    """A secret: a lone enemy crossing the top of the screen fast, leaving a data cube or a warp
    orb to a secret level (prize "cube" or "warp:<level>") when shot down in time. kinds: sky enemies
    (episode, number, enemy) the level's sheets show."""
    ep, number, _ = rnd.choice(kinds)
    left = rnd.random() < 0.5
    speed = 2 if prize.startswith("special") else 3  # (a special's courier slower: it is meant to be found)
    out = [event(t, 15, d1=number, d2=-24 if left else 268, d4=COURIER_LINK, d5=44, ep=ep),
           event(t, 20, d1=0, d2=0, d4=COURIER_LINK), event(t, 19, d1=speed if left else -speed, d2=0, d4=COURIER_LINK)]
    if prize == "cube":
        out.append(event(t, 33, d1=DATA_CUBE, d4=COURIER_LINK, ep=5))
    elif prize.startswith("special"):
        # A special weapon to pick up (its value 32100 + the special: mainint.c), made by the build from the item
        # data's own (episode 5's 1296, the two-player sheet's pickup) as SPECIAL_PICKUP's copy.
        out.append(dict(event(t, 33, d1=SPECIAL_PICKUP, d4=COURIER_LINK, ep=5), value=32100 + int(prize.split(":", 1)[1])))
    else:
        out.append(dict(event(t, 33, d1=WARP_ORB, d4=COURIER_LINK, ep=5), warp=prize.split(":", 1)[1]))
    return out


def courier_kinds(wave_sources, banks):
    """Sky enemies for couriers: shootable in a pass (armor 5-40), not too big, flying straight;
    the waves' own, or else any episode 4 and 5 levels fly on the level's sheets."""
    def suits(en):
        return (en["shapebank"] in banks and 5 <= en["armor"] <= 40 and en["esize"] <= 1 and
                0 < en["value"] < 10000 and not en["xaccel"] and not en["yaccel"] and not en["elaunchfreq"])

    kinds = {}
    for s in wave_sources:
        for w in s.waves():
            for e in w["events"]:
                if e["type"] == 15 and suits(s.enemies[e["d1"]]):
                    kinds[(s.episode, e["d1"])] = s.enemies[e["d1"]]
    if not kinds:
        for s in W.originals(episodes=(4, 5)):
            for e in s.events:
                if e["type"] == 15 and e["t"] < 60000 and suits(s.enemies[e["d1"]]):
                    kinds[(s.episode, e["d1"])] = s.enemies[e["d1"]]
    return [(ep, n, en) for (ep, n), en in sorted(kinds.items())]


def screen_top(row):
    """The clock at which a layer 1 row comes to the screen's top (the clock follows layer 1: curLoc)."""
    return 28 * (291 - row)


def map_rows(grid, letter):
    """Each layer 1 row's mean brightness and how much it varies (0-255), from its tiles' pixels."""
    import numpy as np
    import preview
    pal = preview.palette().astype(float)
    lum = pal @ np.array([0.299, 0.587, 0.114])
    tiles, cache = preview.tiles(letter), {}

    def tile(s):
        if s not in cache:
            img = tiles.get(s)
            cache[s] = (0.0, 0.0) if img is None else (float(lum[img].mean()), float(lum[img].std()))
        return cache[s]
    mean = [float(np.mean([tile(s)[0] for s in row])) for row in grid]
    vary = [float(np.std([tile(s)[0] for s in row]) + np.mean([tile(s)[1] for s in row])) for row in grid]
    return mean, vary


BURST_ROWS = 22   # a rush's stretch of map (616 pixels: at twice the speed, about 300 clock of real time)
DARK_ROWS = 30    # a dark stretch's


def best_stretch(score, rows, lo, hi, taken):
    """The stretch of `rows` rows (top row, bottom row) between rows lo and hi with the lowest mean score, clear of
    the taken clock windows, or None."""
    best = None
    for top in range(lo, hi - rows):
        bottom = top + rows
        t0, t1 = screen_top(bottom), screen_top(top)
        if any(t0 < b and a < t1 for a, b in taken):
            continue
        value = float(sum(score[top:bottom])) / rows
        if best is None or value < best[0]:
            best = (value, top, bottom)
    return best and best[1:]


def map_gimmicks(g, grid, letter, ground, start, boss_time, windows):
    """The gimmicks that follow the map (the user, 2026-11-03: "eventi (ubrzanje, torch svijetlo) nek započinju i
    staju kad ima smisla a ne ovak na random, tj. nek prate nešto što se događa na mapi"), as clock windows: bursts
    "map" (bursts_map of them): rushes along the map's most open stretches (even, the fewest ground enemies), from as
    the stretch comes in at the top until before it ends; dark "map": lights out over its darkest stretch, from as it
    reaches the middle of the screen until it has passed it. (dark "midboss" or "hold": while the mid-level boss or
    the siege is fought: compose, midboss_template.)"""
    g = dict(g)
    if g.get("bursts") != "map" and g.get("dark") != "map":
        return g
    mean, vary = map_rows(grid, letter)
    busy = [0.0] * len(grid)
    for e in ground:
        r = 291 - (e["t"] + 8) // 28
        for k in range(max(0, r - 1), min(len(grid), r + 2)):
            busy[k] += 1
    lo, hi = max(2, 292 - (boss_time - 500) // 28), 292 - (start + 300) // 28  # (rows: hi comes first)
    taken = [(a, b) for a, b, *_ in windows]
    if g.get("dark") == "map":
        stretch = best_stretch(mean, DARK_ROWS, lo, hi, taken)
        g["dark"] = []
        if stretch:
            top, bottom = stretch
            g["dark"] = [(screen_top(bottom) + 92, screen_top(top) + 92)]
            taken += g["dark"]
    if g.get("bursts") == "map":
        score = [v + 8 * b for v, b in zip(vary, busy)]
        g["bursts"] = []
        for _ in range(g.get("bursts_map", 1)):
            stretch = best_stretch(score, BURST_ROWS, lo, hi, taken)
            if not stretch:
                break
            top, bottom = stretch
            window = (screen_top(bottom) + 40, screen_top(top) - 120, 2)
            g["bursts"].append(window)
            taken.append((window[0] - 200, window[1] + 200))
    return g


def timed_list(value):
    """A gimmick's clock windows ([] when it is given another way: "map", "midboss", "hold")."""
    return value if isinstance(value, list) else []


def timed_flips(g):
    """The level's stretches upside down by the clock (flip [(from, to)]; flip "boss" or "midboss":
    while that boss is fought, as EYESPY's boss turns the screen: the user, 2026-11-03, ROOST's
    turn by the clock came "for no reason")."""
    flip = g.get("flip", [])
    return flip if isinstance(flip, list) else []


def gimmick_events(g, speeds, wave_sources, banks, rnd, placements):
    """The level's gimmicks as events (and an ambush's waves as placements)."""
    out = []
    if g.get("couriers"):
        kinds = courier_kinds(wave_sources, banks)
        assert kinds, "no enemy for the couriers"
        for t, prize in g["couriers"]:
            out += courier_events(t, prize, kinds, rnd)
    b1, b2, b3 = speeds
    for t0, t1, factor in timed_list(g.get("bursts")):
        # Afterburners: the level rushes, every layer faster by factor (their ratios kept, so the
        # upper layers last as long; events keep to the map).
        out += [event(t0 - 80, 16, d1=MESSAGE_AFTERBURNER, d2=30),
                event(t0, 2, d1=b1 * factor, d2=b2 * factor, d3=b3 * factor), event(t1, 2, d1=b1, d2=b2, d3=b3)]
    for t0, t1 in timed_list(g.get("dark")):
        # Lights out: only a spotlight round the ship (BRAINIAC, ASSASSIN).
        out += [event(t0, 64, d1=6, d2=1, d3=1), event(t1, 64, d1=6, d2=0)]
    for t0, t1 in timed_flips(g):
        # The screen upside down (LAVA RUN, EYESPY), a warning first. (Turned by a boss: its block's,
        # boss_gone and midboss_template.)
        out += [event(t0 - 80, 16, d1=MESSAGE_DANGER, d2=30), event(t0, 64, d1=9, d2=1, d3=1), event(t1, 64, d1=9, d2=0)]
    for t, (ep, name) in g.get("ambush", []):
        # Enemies from behind (a wave of an original that has them come up from the bottom).
        source = W.Source(ep, name)
        behind = [(i, w) for i, w in enumerate(source.waves())
                  if any(e["type"] in (18, 23, 32) for e in w["events"]) and set(w["banks"]) <= banks
                  and w["count"] >= 2]
        assert behind, f"{name} has no wave from behind on the sheets {sorted(banks)}"
        index, w = rnd.choice(behind)
        out.append(event(t - 70, 16, d1=MESSAGE_BEHIND, d2=30))
        placements.append(dict(kind="wave", episode=ep, name=name, index=index, start=t, drop=pick_coin(rnd, 100)))
    return out


SCENERY_WAVES = 3  # waves of nothing to shoot (SURFACE's rock arches) a level at most, with its density's pace
DISTINCT_WAVES = 9  # kinds of waves a level at most, with its density's pace (they come round again)


def shootable(source, index, w):
    """How many of a wave's enemies can be shot (not its scenery: SURFACE's rock arches)."""
    return sum(1 for e in w["events"] if e["type"] in W.SPAWNS and 0 < source.enemies.get(e["d1"], {}).get("armor", 0) < 255)


def compose(grid, wave_sources, boss_source, ground_sources, boss_time, seed, density=None,
            intensity=lambda f: 0.4 + 0.6 * f, start=150, ground_waves=False, wealth=10000, gimmicks=None,
            speeds=(1, 2, 3), ground_sheets=2, letter=None, target=None, keep_ground=None, need_sheets=()):
    """The level's own events and its placements (see expand). grid: the new layer 1 map (rows of
    shapes), letter its tile set. density(row) -> chance of a ground enemy on a suitable tile there.
    intensity(fraction of the level) -> how big the waves come (0-1). target: (from, to) the waves'
    enemies per 1000 clock as the level goes on (the episodes' density: generate.py waves_target), else
    the waves' old pace. keep_ground: the ground enemies' events kept from the level as it was (its
    terrain is levelled under them) instead of placed anew. need_sheets: sheets the boss's parts launch
    or leave from that its own enemies don't come from (FLEET's covers' hunters in DELI RUIN, 15;
    ASSASSIN's middle piece's launches in DEEP ICE, 10), kept for them."""
    rnd = random.Random(seed)
    events = []
    placements = []

    # The boss, and the enemy sheets everything must share.
    boss = boss_source.boss(stages=True)
    banks = set()
    for e in boss["events"]:
        if e["type"] in W.SPAWNS:
            banks.add(boss_source.enemies[e["d1"]]["shapebank"])
    banks |= set(need_sheets)
    for e in keep_ground or []:
        # (the kept ground enemies' sheets, first: they stand where the terrain is levelled for them)
        for part in range(4 if e["type"] == 12 else 1):
            banks |= W.sheets_of(W.tyrdata.load_items(e["ep"])["enemies"], e["d1"] + part)
    placements.append(dict(kind="boss", episode=boss_source.episode, name=boss_source.name, start=boss_time))
    if (gimmicks or {}).get("flip") == "boss":
        placements[-1]["flip"] = True

    # A boss in the middle of the level (its sheets before the waves'): the map stops while it is
    # fought, so the clock runs ahead of the map by the fight's length from then on (shift).
    gimmicks = gimmicks or {}
    calm = list(gimmicks.get("calm", []))  # no enemies at all
    # No waves from t0 to t1, their events over before the third (around an ambush: its own).
    windows = [(t0, t1, t0) for t0, t1 in calm] + [(t - 100, t + 500, t + 300) for t, _ in gimmicks.get("ambush", [])]
    shift_from, shift = CLOCK_END, 0
    if gimmicks.get("midboss"):
        (ep, name), at = gimmicks["midboss"]
        mid = W.Source(ep, name)
        stop, loop_from, loop_to = midboss_span(mid)
        mid_banks = {mid.enemies[e["d1"]]["shapebank"] for e in mid.boss()["events"] if e["type"] in W.SPAWNS}
        for b in sorted(mid_banks):
            if len(banks) < 4:
                banks.add(b)
        placements.append(dict(kind="midboss", episode=ep, name=name, start=at, loop=[stop, loop_from, loop_to],
                               speeds=list(speeds)))
        if gimmicks.get("flip") == "midboss":
            placements[-1]["flip"] = True
        if gimmicks.get("dark") == "midboss":
            placements[-1]["dark"] = True
        assert all(b in banks for b in mid_banks), f"{name}'s sheets {mid_banks} do not fit with {banks}"
        # (Waves' events never in its loop: they would come round again with it.)
        windows.append((at - 200, at + loop_to + 2 + 150, at + loop_from))
        # The map stands from at + stop until the fight is over (the clock at at + loop_to + 2).
        shift_from, shift = at + stop, loop_to + 2 - stop
        for t0, t1, *_ in timed_list(gimmicks.get("bursts")) + timed_list(gimmicks.get("dark")) + timed_flips(gimmicks) + \
                [(t, t + 600) for t, _ in gimmicks.get("ambush", [])] + \
                [(t, t + 200) for t, _ in gimmicks.get("couriers", [])]:
            assert t1 < at - 200 or t0 > at + loop_to + 2, "a gimmick during the mid-level boss"

    # A warp orb's sheet, when the level hides one.
    if any(prize.startswith("warp") for _, prize in gimmicks.get("couriers", [])):
        banks.add(WARP_SHEET)

    # Sheets an ambush's waves need.
    for _, (ep, name) in gimmicks.get("ambush", []):
        need = Counter(b for w in W.Source(ep, name).waves() if any(e["type"] in (18, 23, 32) for e in w["events"])
                       for b in w["banks"])
        if need and not set(need) & banks and len(banks) < 4:
            banks.add(need.most_common(1)[0][0])

    # The ground enemies' sheets next (they go with the map), at most two (ground_sheets); the
    # waves get the rest.
    for b in ground_banks(ground_sources, 2)[:ground_sheets]:
        if len(banks) < 4:
            banks.add(b)

    # Waves the sheets allow (four sheets in all: the boss's and the waves' most common).
    templates = [(s, i, w) for s in wave_sources for i, w in enumerate(s.waves(ground=ground_waves))
                 if 0 < w["count"] <= 12 and w["length"] <= 1600]
    common = {}
    for _, _, w in templates:
        for b in w["banks"]:
            common[b] = common.get(b, 0) + w["count"]
    for b in sorted(common, key=lambda b: -common[b]):
        if len(banks) >= 4:
            break
        banks.add(b)
    templates = [x for x in templates if set(x[2]["banks"]) <= banks]

    # A siege: the map stops and the level's waves come round and round until the level timer
    # (67) runs out (its countdown on the screen), then the map goes on.
    hold = []
    if gimmicks.get("hold"):
        at, seconds = gimmicks["hold"]
        assert not gimmicks.get("midboss"), "a siege and a mid-level boss in one level"
        loop_from, loop_to = at + 20, at + HOLD_LOOP
        exit_ = loop_to + 10
        short = [x for x in templates if x[2]["length"] <= HOLD_LOOP // 3 and x[2]["count"] >= 3] or             [x for x in templates if x[2]["length"] <= HOLD_LOOP // 2 and x[2]["count"] >= 2]
        for k in range(3):
            source, index, w = rnd.choice(short)
            placements.append(dict(kind="wave", episode=source.episode, name=source.name, index=index,
                                   start=loop_from + k * (HOLD_LOOP // 3), _count=w["count"]))
        # (The timer's jump runs the event before its target again: the message there, not the loop.)
        hold = [event(at - 80, 16, d1=MESSAGE_DANGER, d2=30), event(at, 2), event(at, 53),
                event(at, 67, d1=1, d2=exit_, d3=seconds * 35 // 100), event(loop_to, 54, d1=loop_from),
                event(exit_ - 2, 16, d1=4, d2=30), event(exit_, 2, d1=speeds[0], d2=speeds[1], d3=speeds[2]),
                event(exit_, 53, d1=99)]
        if gimmicks.get("dark") == "hold":
            # (the power cut while it lasts: only the ship's spotlight)
            hold[1:1] = [event(at, 64, d1=6, d2=1, d3=1)]
            hold.append(event(exit_, 64, d1=6, d2=0))
        windows.append((at - 200, exit_ + 150, loop_from))
        shift_from, shift = at, exit_ - at

    # The ground enemies (placed now: the gimmicks that follow the map keep clear of them).
    if keep_ground is None:
        ground = place_ground(grid, ground_sources, banks, start, boss_time - shift, rnd, density)
        for e in ground:
            if e["t"] >= shift_from:
                e["t"] += shift  # the map stood still for the mid-level boss
    else:
        ground = [dict(e) for e in keep_ground]
    if letter:
        gimmicks = map_gimmicks(gimmicks, grid, letter, ground, start, boss_time, windows)

    t = start
    end = boss_time - 350
    scenery_left = SCENERY_WAVES
    distinct = set()
    while t < end:
        inside = [w for w in windows if w[0] <= t < w[1]]
        if inside:
            t = inside[0][1]
            continue
        f = (t - start) / max(1, end - start)
        level = intensity(f)
        # Bigger waves as it gets harder; a pause after each, shorter as it gets harder.
        bound = min([w[2] for w in windows if w[0] > t] + [end + 400])
        fitting = [x for x in templates if x[2]["count"] <= (4 if target else 3) + level * 10 and
                   x[2]["length"] < bound - t and (not target or shootable(*x) or scenery_left > 0)]
        if not fitting:
            later = [w[1] for w in windows if w[0] > t]
            if later:
                t = min(later)
                continue
            break
        if target and len(distinct) >= DISTINCT_WAVES:
            # (the waves seen so far again, once there are DISTINCT_WAVES kinds: more kinds of enemies would bring in
            # more of other episodes' weapons than the episode's item data has room for)
            again = [x for x in fitting if (x[0].episode, x[0].name, x[1]) in distinct]
            fitting = again or fitting
        source, index, w = rnd.choice(fitting)
        distinct.add((source.episode, source.name, index))
        placement = dict(kind="wave", episode=source.episode, name=source.name, index=index, start=t)
        if ground_waves:
            placement["ground"] = True
        placements.append(placement)
        placement["_count"] = w["count"]
        spawn_span = max(e["t"] for e in w["events"] if e["type"] in W.SPAWNS)
        if target:
            # As many enemies a stretch as the episodes before have by this point (waves may overlap): the wave's
            # enemies that can be shot (not its scenery: SURFACE's rock arches).
            real = shootable(source, index, w)
            if not real:
                scenery_left -= 1
            want = target[0] + (target[1] - target[0]) * f
            t += max(int(max(real, 1) * 1000 / want * rnd.uniform(0.8, 1.2)), spawn_span // 2 + 40)
        else:
            t += spawn_span + int(rnd.uniform(90, 260) * (1.3 - level))

    # Credits: most waves' enemies leave coins, worth what makes the level's wealth in all.
    wave_enemies = sum(p.get("_count", 0) for p in placements)
    for p in placements:
        n = p.pop("_count", 0)
        if p["kind"] == "wave" and rnd.random() < 0.65:
            p["drop"] = pick_coin(rnd, wealth / max(1, 0.65 * wave_enemies))

    # Stationary ground enemies where the map has a place for them: on tiles (or 2x2 blocks of
    # tiles) that carry an enemy in most of the places the originals have them (turret pads,
    # emplacements, bunkers painted into the tileset), not on any tile one once stood on.
    events += [e for e in ground if not any(w0 <= e["t"] < w1 for w0, w1 in calm)]
    events += gimmick_events(gimmicks, speeds, wave_sources, banks, rnd, placements) + hold

    # The level's settings at its start (EVENTS.md 8: one sheet event for every enemy, no random
    # enemies), and the end if the boss is never found.
    banks = sorted(b for b in banks if b not in (21, 26))[:4]
    sheets = (banks + [0] * 4)[:4]
    head = [event(0, 2, d1=1, d2=2, d3=3), event(0, 5, sheets[0], sheets[1], d3=sheets[2], d4=sheets[3]),
            event(0, 8), event(0, 13)]
    events = head + sorted(events, key=lambda e: e["t"]) + [event(CLOCK_END - 50, 11)]
    return events, placements, banks
