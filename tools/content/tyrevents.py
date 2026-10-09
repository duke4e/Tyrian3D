#!/usr/bin/env python3
"""Prints a Tyrian level's events with names and decoded fields, as JE_loadMap reads them and
JE_eventSystem runs them (src/tyrian2.c; reference: tools/content/EVENTS.md).

usage: tools/content/tyrevents.py <episode> <level> [--file N] [--data DIR] [--raw]

<level> is a level name from the episode script (levelsN.dat, e.g. TYRIAN, "SAVARA V"), a
section number, or f<N> for a level file entry number directly. A section can load one of
several level files (]h[ / ]H[ pick by difficulty): the first is shown, --file picks another.
--data reads another data directory (default data/tyrian2000). --raw adds the raw fields.
"""
import argparse
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import tyrdata  # noqa: E402
from tyrdata import Reader  # noqa: E402
import levels  # noqa: E402

# src/lvlmast.c shapeFile[]: event 5 and enemyDat.shapebank are 1-based indexes into it
# (the sheet is newsh<letter>.shp).
SHAPE_FILE = "2478ABCDEFGHIJKLMNOPQRSTU5#V0@3^59'%"
SPECIAL_BANKS = {21: "coins&gems", 26: "two-player"}  # JE_makeEnemy, always loaded

# Event 16: tyrian.hdt's event texts (helptext.c outputs[]) and their voices (sndmast.c).
MESSAGES = {1: "Enemy approaching from behind. (danger)", 2: "Large mass detected ahead! (boss)",
            3: "Intercepting enemy aircraft. (enemies)", 4: "Cleared enemy platforms. (cleared)",
            5: "Approaching enemy platforms... (danger)", 6: "WARNING: Spikes ahead!! (spikes)",
            7: "Afterburners activated! (accelerate)", 8: "** Danger! ** (danger)",
            9: ">>> Bonus Level <<< (enemies)"}

# Enemy slot ranges (JE_createNewEventEnemy enemyOffset).
LAYER = {0: "sky", 25: "ground", 50: "top", 75: "ground2"}
SPAWN_OFFSET = {6: 25, 7: 50, 10: 75, 15: 0, 17: 25, 18: 0, 23: 50, 32: 50, 56: 75,
                49: 25, 50: 0, 51: 50, 52: 75}
BOTTOM_Y = {17: "190", 18: "190", 23: "180", 32: "190!", 56: "190!"}  # '!' = eventdat5 ignored
MAP_ROWS = {1: 300, 2: 600, 3: 600}
MAP_W = {1: 14, 2: 14, 3: 15}
START_ROW = 292  # mapY = 300 - 8 (layer 1); layers 2 and 3 start at 592


def bank_name(b):
    if b in SPECIAL_BANKS:
        return f"{b}({SPECIAL_BANKS[b]})"
    if 1 <= b <= len(SHAPE_FILE):
        return f"{b}({SHAPE_FILE[b - 1]})"
    return str(b)


def link(v):
    return "all" if v == 0 else str(v)


def maptile(v, layer):
    """Events 71, 77 and 81 give map positions as 2 * a tile index (the original's 16-bit map).
    The map pointer of a layer at row mapY is mainmap[mapY][0] - 1, so tile 14 * mapY - 1
    (15 * mapY - 1 for layer 3): shown as mapY when it is one, else as row and column."""
    idx = v // 2 if v >= 0 else -((-v) // 2)  # C division truncates toward zero
    w = MAP_W[layer]
    if (idx + 1) % w == 0:
        return f"{v}(mapY {(idx + 1) // w})"
    return f"{v}(tile {idx}: row {idx // w} col {idx % w}, mapY {(idx + 1) / w:.2f})"


class Level:
    def __init__(self, data, offset):
        r = Reader(data, offset)
        self.offset = offset
        self.map_file = chr(r.u8())
        self.shape_file = chr(r.u8())
        self.mapX, self.mapX2, self.mapX3 = r.u16(3)
        n = r.u16()
        self.level_enemy = r.u16(n) if n else []
        self.events = []
        for _ in range(r.u16()):
            self.events.append(dict(t=r.u16(), type=r.u8(), d1=r.s16(), d2=r.s16(), d3=r.s8(), d5=r.s8(),
                                    d6=r.s8(), d4=r.u8()))
        self.events_end = r.o
        # The maps follow the events directly: 3 tables of 128 shape numbers (big-endian), then
        # the maps 14x300, 14x600 and 15x600 (one byte per tile: an index into the table).
        self.map_sh = []
        for _ in range(3):
            raw = data[r.o:r.o + 256]
            self.map_sh.append([raw[i] << 8 | raw[i + 1] for i in range(0, 256, 2)])
            r.o += 256
        self.maps = []
        for layer in (1, 2, 3):
            size = MAP_W[layer] * MAP_ROWS[layer]
            self.maps.append(data[r.o:r.o + size])
            r.o += size
        self.end = r.o


# ---- event names and decoders -------------------------------------------------------------

def simulate(events):
    """Annotates each event with the curLoc it fires at ('loc') and the layer 1 scroll then ('s1'),
    following the events in file order (JE_main's level loop: an event fires at the start of the
    first tick with curLoc >= eventtime; curLoc and the layer 1 map advance backMove per move).
    Jumps and skips are conditional and ignored. A map stopped without forced events (event 2
    with bg1=0) restarts on its own when the screen is clear (event 4): assumed at speed 1, and the
    following events are marked 'approx'."""
    loc = s1 = 0
    back_move, forced, approx = 1, False, False
    for e in events:
        t = e["t"]
        if t > loc:
            if back_move > 0:
                steps = -(-(t - loc) // back_move)
                loc += steps * back_move
                s1 += steps * back_move
            elif forced:
                loc = t  # curLoc+1 a tick, the map does not move
            else:
                approx = True
                back_move = 1
                s1 += t - loc
                loc = t
        e["loc"], e["s1"], e["approx"] = loc, s1, approx
        k = e["type"]
        if k in (2, 30):
            back_move = max(e["d1"], 0)
        elif k == 3:
            back_move = 1  # one pixel every 3 ticks
        elif k == 53:
            forced = e["d1"] != 99
        elif k == 77:
            # the map pointer moves (in tiles), backPos stays: s1 follows the new mapY
            map_y = (e["d1"] // 2 + 1) / 14
            s1 = 28 * (START_ROW - map_y) + s1 % 28


def spawn(e, enemies, mapX, mapX3):
    t = e["type"]
    off = SPAWN_OFFSET.get(t)
    if t == 12:
        off = {0: 25, 1: 25, 2: 0, 3: 50, 4: 75}.get(e["d6"], 25)
    s = [f"[{LAYER[off]}]"]
    if 49 <= t <= 52:
        s.append(f"graphic={e['d1']} bank={bank_name(e['d3'])} armor={e['d6']}")
    elif t == 12:
        s.append(f"enemy={e['d1']}..{e['d1'] + 3}(2x2 of parts: +1 x+24, +2 y-28, +3 both)")
    else:
        s.append(f"enemy={e['d1']}")
    x = e["d2"]
    if x == -99:
        s.append("x=enemyDat start")
    elif x == -200:
        s.append("x=random 24..231")
    else:
        s.append(f"x={x}")
    if t in BOTTOM_Y:
        s.append(f"y={BOTTOM_Y[t]}" + (f"+{e['d5']}" if not BOTTOM_Y[t].endswith("!") and e["d5"] else ""))
    elif e["d5"]:
        s.append(f"y=-28{e['d5']:+d}")
    if not (49 <= t <= 52) and e["d3"]:
        s.append(f"vy{e['d3']:+d}")
    if e["d4"]:
        s.append(f"link={e['d4']}")
    if t != 12 and not (49 <= t <= 52) and e["d6"]:
        s.append(f"fixedmovey={e['d6']}")
    # Where a ground enemy lands on the layer 1 map: the tile column and row of a 2x2 sprite's
    # top-left corner (of part 0 for event 12), with the layer 1 scroll the event fires at
    # (simulate(); exact without jumps and stops). Integers: on the tile grid.
    if off in (25, 75) and x not in (-99, -200) and t not in BOTTOM_Y:
        col = (x - (mapX - 1) * 24 + 30) / 24
        row = START_ROW + (-28 + e["d5"] - 7 - e.get("s1", e["t"])) / 28
        where = f"row {row:.2f}" if row > -1 else "beyond the map's top"
        s.append(f"@L1 col {col:.2f} {where}" + (" ~" if e.get("approx") else ""))
    elif off == 50 and x not in (-99, -200):
        col = (x - mapX3 * 24 + 24) / 24
        s.append(f"@L3 col {col:.2f}")
    return " ".join(s)


def d_global_select(e):
    d3 = e["d3"]
    if 80 <= d3 <= 89:
        return f"link=newPL[{d3 - 80}](event 75)"
    return None


def d19(e):
    sel = d_global_select(e)
    if sel is None:
        sel = {0: f"link={e['d4']}", 1: "all ground(25-49)", 2: "all sky(0-24)", 3: "all top(50-74)",
               99: "all"}.get(e["d3"], f"none(d3={e['d3']})")
    s = [sel]
    if e["d1"] != -99:
        s.append(f"exc={e['d1']}")
    if e["d2"] != -99:
        s.append(f"eyc={e['d2']}")
    if e["d6"] == -99:
        s.append("fixedmovey=0")
    elif e["d6"]:
        s.append(f"fixedmovey={e['d6']}")
    if e["d5"] > 0:
        s.append(f"cycle={e['d5']}")
    return " ".join(s)


def d20(e):
    s = [d_global_select(e) or f"link={link(e['d4'])}"]
    if e["d1"] != -99:
        s.append(f"excc={e['d1']}")
    if e["d2"] != -99:
        s.append(f"eycc={e['d2']}")
    if e["d5"] > 0:
        s.append(f"cycle={e['d5']}")
    if e["d6"] > 0:
        s.append(f"ani={e['d6']}(animin={e['d5']})")
    return " ".join(s)


def d27(e):
    s = [d_global_select(e) or f"link={link(e['d4'])}"]
    if e["d1"] != -99:
        s.append(f"exrev={e['d1']}")
    if e["d2"] != -99:
        s.append(f"eyrev={e['d2']}")
    if 0 < e["d3"] < 17:
        s.append(f"filter={e['d3']}")
    return " ".join(s)


def d55(e):
    s = [d_global_select(e) or f"link={link(e['d4'])}"]
    if e["d1"] != -99:
        s.append(f"xaccel={e['d1']}")
    if e["d2"] != -99:
        s.append(f"yaccel={e['d2']}")
    return " ".join(s)


def d74(e):
    s = [f"link={link(e['d4'])}"]
    for k, n in (("d1", "xmax"), ("d2", "ymax"), ("d5", "xmin"), ("d6", "ymin")):
        if e[k] != -99:
            s.append(f"{n}={e[k]}")
    return " ".join(s)


def d4(e):
    mode = {0: "ground clear", 1: "ground clear", 2: "sky clear", 3: "screen clear"}.get(e["d1"], f"? {e['d1']}")
    return f"restart 1/2/3 when {mode} (or whole screen clear)"


def d5(e):
    return "sheets " + " ".join(bank_name(e[k]) if e[k] > 0 else "-" for k in ("d1", "d2", "d3", "d4"))


def d38(e):
    return f"curLoc={e['d1'] & 0xffff} (resume at the last event with time <= it)"


def d54(e):
    return "return (curLoc=returnLoc)" if e["d1"] == -1 else f"jump curLoc={e['d1'] & 0xffff} (returnLoc=curLoc+1)"


def d70(e):
    if e["d2"] == 0:
        return f"jump {e['d1'] & 0xffff} if no enemy with link 1..19"
    links = [str(e["d2"])] + [str(e[k]) for k in ("d3", "d4") if e[k]]
    return f"jump {e['d1'] & 0xffff} if no enemy with link {'/'.join(links)}"


def d75(e):
    s = f"newPL[{e['d3'] - 80}] = random live link in {e['d1']}..{e['d2']} with eyc==0"
    if e["d4"]:
        s += f"; none: skip {e['d4']} events"
    return s


def d77(e):
    s = f"map1={maptile(e['d1'], 1)} map2={maptile(e['d2'] if e['d2'] > 0 else e['d1'], 2)}"
    return s


EVENTS = {
    1: ("starfield speed", lambda e: f"speed={e['d1']}"),
    2: ("scroll speed", lambda e: f"bg1={e['d1']} bg2={e['d2']} bg3={e['d3']} (delays 1)"),
    3: ("slow scroll", lambda e: "bg1 1px/3 ticks, bg2 1px/2 ticks, bg3 1px/tick"),
    4: ("map stop resume", d4),
    5: ("enemy shape banks", d5),
    6: ("ground enemy", None),
    7: ("top enemy", None),
    8: ("stars off", None),
    9: ("stars on", None),
    10: ("ground2 enemy", None),
    11: ("END LEVEL", lambda e: "immediately" if e["d1"] == 1 else "fly out (40 ticks)"),
    12: ("4-part enemy", None),
    13: ("random enemies off", None),
    14: ("random enemies on", None),
    15: ("sky enemy", None),
    16: ("text window", lambda e: f"message {e['d1']}: {MESSAGES.get(e['d1'], '?')}"),
    17: ("ground enemy bottom", None),
    18: ("sky enemy bottom", None),
    19: ("global move", d19),
    20: ("global accel", d20),
    21: ("bg3 over player", None),
    22: ("bg3 normal", None),
    23: ("top enemy bottom", None),
    24: ("global animate", lambda e: f"link={e['d4']} ani={e['d1']} cycle={e['d2']} mode={e['d3']}"),
    25: ("global set armor", lambda e: f"link={link(e['d4'])} armor={e['d1']}"),
    26: ("small enemy adjust", lambda e: f"on={e['d1']}"),
    27: ("global rev/filter", d27),
    28: ("top enemies under", None),
    29: ("top enemies over", None),
    30: ("scroll speed b", lambda e: f"bg1={e['d1']} bg2={e['d2']} bg3={e['d3']} (delays 1, stop kept)"),
    31: ("fire override", lambda e: f"link={'all' if e['d4'] == 99 else e['d4']} freq={e['d1']},{e['d2']},{e['d3']}"
                                    f" launchfreq={e['d5']}"),
    32: ("top enemy bottom b", None),
    33: ("enemy drops enemy", lambda e: f"link={e['d4']} enemydie={e['d1']}"),
    34: ("music fade", None),
    35: ("play song", lambda e: f"song={e['d1']}"),
    36: ("end when clear", lambda e: "end level when no enemy is on screen"),
    37: ("random enemy freq", lambda e: f"spawn if rand%100 > {e['d1']}"),
    38: ("set curLoc", d38),
    39: ("change link", lambda e: f"link {e['d1']} -> {e['d2']}"),
    40: ("continual damage", None),
    41: ("clear enemies", lambda e: "all" if e["d1"] == 0 else "sky (0-24)"),
    42: ("bg3 under sky", None),
    43: ("bg2 order", lambda e: f"background2over={e['d1']}"),
    44: ("filter", lambda e: f"active={e['d1']} filter={e['d2']} bright={e['d3']} new={e['d4']} "
                             f"chg={e['d5']} fadestart={int(e['d6'] == 0)}"),
    45: ("arcade drops enemy", lambda e: f"link={e['d4']} enemydie={e['d1']} (arcade/2P only)"),
    46: ("difficulty change", lambda e: f"{e['d1']:+d}" + (" (arcade/2P only)" if e["d2"] else "")
                                         + (f" damageRate={e['d3']}" if e["d3"] else "")),
    47: ("global set armor b", lambda e: f"link={link(e['d4'])} armor={e['d1']}"),
    48: ("bg2 opaque", None),
    49: ("custom ground enemy", None),
    50: ("custom sky enemy", None),
    51: ("custom top enemy", None),
    52: ("custom ground2 enemy", None),
    53: ("force events", lambda e: "off" if e["d1"] == 99 else "on"),
    54: ("jump", d54),
    55: ("global homing", d55),
    56: ("ground2 enemy bottom", None),
    57: ("254-death jump", lambda e: f"jump {e['d1'] & 0xffff} when a link-254 enemy dies"),
    58: ("set launch type", lambda e: f"link={'all' if e['d4'] == 99 else e['d4']} launchtype={e['d1']}"),
    59: ("replace enemy", lambda e: f"link={link(e['d4'])} -> enemy {e['d1']}"),
    60: ("special flag", lambda e: f"link={e['d4']} on death flag[{e['d1']}]={int(e['d2'] == 1)}"),
    61: ("skip if flag", lambda e: f"if flag[{e['d1']}]=={e['d2']} skip {e['d3']}"),
    62: ("sound", lambda e: f"sample={e['d1']}"),
    63: ("skip unless 2P", lambda e: f"skip {e['d1']} unless 2P/arcade"),
    64: ("smoothie", lambda e: f"effect={e['d1']} on={e['d2']} data={e['d3']}"),
    65: ("bg3 x parallax", lambda e: "like bg1" if e["d1"] == 0 else "own"),
    66: ("skip by difficulty", lambda e: f"skip {e['d2']} if difficulty <= {e['d1']}"),
    67: ("level timer", lambda e: f"on={int(e['d1'] == 1)} {e['d3']}s then jump {e['d2'] & 0xffff}"),
    68: ("replace enemy b", lambda e: f"link={link(e['d4'])} -> enemy {e['d1']}"),
    69: ("invulnerable", lambda e: f"ticks={e['d1']}"),
    70: ("jump if links dead", d70),
    71: ("jump if map passed", lambda e: f"jump {e['d1'] & 0xffff} if map1 pos*2 <= {maptile(e['d2'], 1)}"),
    72: ("bg3 x1b", lambda e: f"on={int(e['d1'] == 1)}"),
    73: ("sky enemies over all", lambda e: f"on={int(e['d1'] == 1)}"),
    74: ("bounce box", d74),
    75: ("pick random link", d75),
    76: ("return when clear", None),
    77: ("set map position", d77),
    78: ("galaga shot freq+1", None),
    79: ("boss bar", lambda e: f"links {e['d1']} {e['d2']}"),
    80: ("skip if 2P", lambda e: f"skip {e['d1']} if 2P"),
    81: ("bg2 wrap", lambda e: f"at {maptile(e['d1'], 2)} to {maptile(e['d2'], 2)}"),
    82: ("give special", lambda e: f"special={e['d1']}"),
    83: ("map stop resume b", d4),
    84: ("timed battle timer", lambda e: f"on={int(e['d1'] == 1)} {e['d3']}s then jump {e['d2'] & 0xffff}"),
    85: ("timed drops enemy", lambda e: f"link={e['d4']} enemydie={e['d1']}"),
    99: ("random explosions", lambda e: f"on={int(e['d1'] == 1)}"),
}
SPAWNS = set(SPAWN_OFFSET) | {12}


def raw(e):
    return f"({e['d1']},{e['d2']},{e['d3']},{e['d4']},{e['d5']},{e['d6']})"


# ---- the script --------------------------------------------------------------------------

def script_levels(path):
    """[(section, name, song, file number, next section, timed battle)] for every ]L line of the
    script (JE_loadMap's ]L: next section at 9, name at 13, song at 22, file number at 25)."""
    out = []
    section = 0
    timed = False
    for s in levels.read_strings(path):
        if s.startswith("*"):
            section += 1
            timed = "timed battle" in s.lower()
        elif s.startswith("]L"):
            out.append((section, s[13:22].strip(), int(s[22:24] or 0), int(s[25:27]), int(s[9:12] or 0), timed))
    return out


def pick_level(ep, which, data_dir, file_override):
    path = os.path.join(data_dir, f"levels{ep}.dat")
    lines = script_levels(path) if os.path.exists(path) else []
    if which.lower().startswith("f") and which[1:].isdigit():
        n = int(which[1:])
        named = [ln for ln in lines if ln[3] == n]
        return n, (named[0] if named else None), []
    if which.isdigit():
        matches = [ln for ln in lines if ln[0] == int(which)]
    else:
        key = which.strip().upper()
        matches = [ln for ln in lines if ln[1].upper() == key]
        if not matches:
            matches = [ln for ln in lines if ln[1].upper().startswith(key)]
    if not matches:
        sys.exit(f"no level {which!r} in {path}; levels: " + ", ".join(sorted({ln[1] for ln in lines})))
    matches.sort(key=lambda ln: ln[5])  # timed battle sections last
    first = matches[0]
    if file_override is not None:
        chosen = next((ln for ln in matches if ln[3] == file_override), None)
        return file_override, (chosen or first), matches
    return first[3], first, matches


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("episode", type=int)
    ap.add_argument("level")
    ap.add_argument("--file", type=int, default=None, help="level file entry number (of the matched ones)")
    ap.add_argument("--data", default=tyrdata.DATA, help="data directory")
    ap.add_argument("--raw", action="store_true", help="also print the raw fields")
    a = ap.parse_args()

    file_num, line, matches = pick_level(a.episode, a.level, a.data, a.file)
    data, n, pos = tyrdata.lvl_positions(os.path.join(a.data, f"tyrian{a.episode}.lvl"))
    if not 0 < file_num * 2 <= n:
        sys.exit(f"level file entry {file_num} not in tyrian{a.episode}.lvl ({n} entries)")
    lv = Level(data, pos[(file_num - 1) * 2])
    try:
        enemies = tyrdata.load_items(a.episode, a.data)["enemies"]
    except (OSError, IndexError, Exception):  # noqa: BLE001 (episode without item data)
        enemies = {}

    if line:
        sec, name, song, fnum, nxt, timed = line
        print(f"episode {a.episode} section {sec}: {name}  song {song}  file {fnum}  next section {nxt}"
              + ("  (timed battle section)" if timed else ""))
    others = [f"section {m[0]} file {m[3]}" + (" (timed battle)" if m[5] else "") for m in matches if m is not line]
    if others:
        print("  also: " + ", ".join(others) + "  (]h[/]H[ choose by difficulty; --file N)")
    print(f"entry offset {lv.offset}, events end {lv.events_end}"
          f" (next entry {pos[(file_num - 1) * 2 + 1]}), maps end {lv.end}")
    print(f"mapFile '{lv.map_file}'  shapeFile '{lv.shape_file}' (shapes{lv.shape_file.lower()}.dat)"
          f"  mapX {lv.mapX}  mapX2 {lv.mapX2}  mapX3 {lv.mapX3}")
    for layer in (1, 2, 3):
        m = lv.maps[layer - 1]
        used = sorted(set(m))
        shapes = sum(1 for v in lv.map_sh[layer - 1] if v)
        print(f"map {layer}: {MAP_W[layer]}x{MAP_ROWS[layer]}, {len(used)} tile indexes used (max {used[-1]}),"
              f" {shapes} non-zero shape numbers in its table")
    print(f"random enemies ({len(lv.level_enemy)}): {lv.level_enemy}  (sky slots; event 13 off, 14 on,"
          f" 37 frequency; default on at rand%100 > 96)")
    print()

    simulate(lv.events)
    banks = set()
    counts = Counter()
    spawned = Counter()
    drops = Counter()
    warn = 0
    for e in lv.events:
        t = e["type"]
        counts[t] += 1
        name, fn = EVENTS.get(t, (f"UNKNOWN {t}", None))
        if t in SPAWNS:
            fields = spawn(e, enemies, lv.mapX, lv.mapX3)
            ids = [e["d1"] + k for k in range(4)] if t == 12 else ([] if 49 <= t <= 52 else [e["d1"]])
            for i in ids:
                spawned[i] += 1
                b = enemies.get(i, {}).get("shapebank")
                if b is not None and b not in banks and b not in SPECIAL_BANKS:
                    fields += f" !bank {bank_name(b)} not loaded"
                    warn += 1
            if 49 <= t <= 52 and e["d3"] > 0 and e["d3"] not in banks and e["d3"] not in SPECIAL_BANKS:
                fields += " !bank not loaded"
                warn += 1
        elif fn is not None:
            fields = fn(e)
        else:
            fields = "" if t in EVENTS else raw(e)
        if t == 5:
            banks = {e[k] for k in ("d1", "d2", "d3", "d4") if e[k] > 0}
        if t in (33, 45, 85):
            drops[e["d1"]] += 1
        if e["loc"] != e["t"]:
            fields += f"  (fires at curLoc {e['loc']}{'~' if e['approx'] else ''})"
        line_out = f"{e['t']:5d} {t:3d} {name:<20} {fields}"
        if a.raw:
            line_out += f"   raw {raw(e)}"
        print(line_out.rstrip())

    print()
    print(f"{len(lv.events)} events, last time {max((e['t'] for e in lv.events), default=0)}"
          + (f", {warn} spawns with an unloaded shape bank" if warn else ""))
    print("per type: " + ", ".join(f"{t} {EVENTS.get(t, ('?',))[0]} x{c}" for t, c in sorted(counts.items())))

    def show(title, ids):
        if not ids:
            return
        print(title)
        for i in sorted(ids):
            d = enemies.get(i)
            if d is None:
                print(f"  {i:5d}  (no enemy data)")
                continue
            print(f"  {i:5d} x{ids[i]:<3d} armor {d['armor']:3d}  size {'2x2' if d['esize'] == 1 else '1x1'}"
                  f"  bank {bank_name(d['shapebank']):<7} graphic {d['egraphic'][0]:4d}  value {d['value']:5d}"
                  f"  move {d['xmove']},{d['ymove']}  start {d['startx']},{d['starty']}"
                  f"  expl {d['explosiontype']}"
                  + (f"  launch {d['elaunchtype']}/{d['elaunchfreq']}" if d["elaunchfreq"] else "")
                  + (f"  dies->{d['eenemydie']}" if d["eenemydie"] else ""))

    show("enemies spawned by events (enemyDat):", spawned)
    show("random enemies:", Counter(lv.level_enemy))
    show("enemies made when linked enemies die (33/45/85):", drops)


if __name__ == "__main__":
    main()
