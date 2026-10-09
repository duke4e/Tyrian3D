#!/usr/bin/env python3
"""New items for Tyrian3D's content layer (src/content.h): weapons made from sidekicks and
sidekicks made from weapons, built from the original item data by rules, written to
assets/content/items.cfg.

usage: tools/content/make_items.py

Weapons go in the free weapon slots from 819, ports in 48-60, sidekicks in 33-37. The rules start
from the episode 1-3 data (tyrian.hdt); a port's 11 power levels grow its weapon step by step (more
shots, faster fire, more damage), as the original ports do.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tyrdata  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets", "content", "items.cfg")

FIELDS = ["shotrepeat", "multi", "weapani", "max", "tx", "ty", "aim", "acceleration", "accelerationx", "circlesize",
          "sound", "trail", "shipblastfilter"]
ARRAYS = [("attack", "attack"), ("del", "del_"), ("sx", "sx"), ("sy", "sy"), ("bx", "bx"), ("by", "by"), ("sg", "sg")]


class Out:
    def __init__(self, data):
        self.data = data
        self.lines = []
        self.next_weapon = 819

    def weapon(self, w, comment=""):
        """A weapon line from a dict like tyrdata's; its new id."""
        wid = self.next_weapon
        self.next_weapon += 1
        assert wid <= 999, "out of free weapon slots"
        parts = [f"weapon {wid}"]
        for f in FIELDS:
            parts.append(f"{f}={int(w[f])}")
        n = max(1, min(8, int(w["max"]) or 1))
        for key, src in ARRAYS:
            parts.append(f"{key}=" + ",".join(str(int(v)) for v in w[src][:n]))
        self.lines.append(" ".join(parts) + (f"  # {comment}" if comment else ""))
        return wid

    def port(self, pid, name, levels, cost, graphic, poweruse, comment):
        self.lines.append(f"# {comment}")
        self.lines.append(f'port {pid} name="{name}" opnum=1 op1={",".join(map(str, levels))} op2={",".join(map(str, levels))} '
                          f"cost={cost} graphic={graphic} poweruse={poweruse}")

    def sidekick(self, sid, copy, name, wpnum, wport, cost, comment, **extra):
        self.lines.append(f"# {comment}")
        rest = " ".join(f"{k}={v}" for k, v in extra.items())
        self.lines.append(f'sidekick {sid} copy={copy} name="{name}" wpnum={wpnum} wport={wport} cost={cost} {rest}'.rstrip())


def blank(**kw):
    w = dict(shotrepeat=10, multi=1, weapani=0, max=1, tx=0, ty=0, aim=0, acceleration=0, accelerationx=0, circlesize=0,
             sound=0, trail=255, shipblastfilter=0, attack=[1] * 8, del_=[255] * 8, sx=[0] * 8, sy=[0] * 8, bx=[0] * 8,
             by=[0] * 8, sg=[0] * 8)
    w.update(kw)
    return w


def shots(w, spec):
    """Sub-shots from (sx, sy, bx, by, sg, attack) tuples."""
    w = dict(w)
    for key in ("sx", "sy", "bx", "by", "sg", "attack"):
        w[key] = [0] * 8
    src = {"sx": 0, "sy": 1, "bx": 2, "by": 3, "sg": 4, "attack": 5}
    for i, s in enumerate(spec[:8]):
        for key, k in src.items():
            w[key][i] = s[k]
    w["multi"] = w["max"] = len(spec[:8])
    return w


def level(i, lo, hi):
    """A value growing from lo (power 1) to hi (power 11)."""
    return round(lo + (hi - lo) * i / 10)


def main():
    data = tyrdata.load_items(1)
    W, O, P = data["weapons"], data["options"], data["ports"]
    out = Out(data)
    out.lines += ["# Tyrian3D new items, made by tools/content/make_items.py (do not edit by hand: change the rules).",
                  "# Format: src/content.h.", ""]

    # --- Front weapons from sidekicks ---------------------------------------------------------
    # Phoenix Cannon: the Phoenix Device's fireballs, forward in a widening fan. A fireball does no
    # damage itself: it bursts into a chain weapon on a hit (attack 100+n fires weapon n), which grows
    # from a small blast (w12) to an eight-way burst (w28) to the Phoenix's own fireworks (w36).
    fire = W[O[8]["wpnum"]]
    levels = []
    for i in range(11):
        count = [1, 1, 2, 2, 3, 3, 2, 3, 3, 2, 3][i]
        chain = 112 if i < 4 else 128 if i < 9 else 136
        spread = [0, -1, 1][:count] if count != 2 else [-1, 1]
        spec = [(s, 6, s * 4, 0, fire["sg"][0], chain) for s in spread]
        w = shots(blank(sound=fire["sound"], trail=fire["trail"], shipblastfilter=fire["shipblastfilter"]), spec)
        w["shotrepeat"] = level(i, 14, 8) if i < 9 else 16
        levels.append(out.weapon(w, f"Phoenix Cannon {i + 1}"))
    out.port(48, "Phoenix Cannon", levels, 1000, O[8]["itemgraphic"], 50,
             "Phoenix Cannon: the Phoenix Device's fireballs, bursting into ever bigger explosions")
    out.lines.append("")

    # Wobble Cannon: the Wobbley's blue blobs in pairs, weaving side to side (circlesize 20+x: an x
    # wide sway, little forward wobble), more pairs and more damage each level.
    wob = W[O[5]["wpnum"]]
    levels = []
    for i in range(11):
        pairs = [(-4, 4), (-12, 12), (-20, 20)][: 1 + i // 4]
        damage = 1 + i // 3
        spec = []
        for a, b in pairs:
            spec += [(0, 6, a, 0, wob["sg"][0], damage), (0, 6, b, 0, wob["sg"][0], damage)]
        w = shots(blank(sound=wob["sound"], weapani=wob["weapani"], circlesize=20 + 3 + i // 3,
                        shipblastfilter=wob["shipblastfilter"]), spec)
        w["shotrepeat"] = level(i, 6, 4)
        levels.append(out.weapon(w, f"Wobble Cannon {i + 1}"))
    out.port(49, "Wobble Cannon", levels, 700, O[5]["itemgraphic"], 30,
             "Wobble Cannon: the Wobbley's blobs in pairs, weaving as they fly")
    out.lines.append("")

    # Micro-Missile Swarm: the Mini-Missile's missiles (they drift back, then accelerate forward and
    # burst), from more tubes and more of them per trigger each level.
    mis = W[O[10]["wpnum"]]
    levels = []
    for i in range(11):
        tubes = [0, -2, 2, -1, 1][: 1 + i * 4 // 10]
        spec = [(dx, mis["sy"][0], dx * 3, 0, mis["sg"][0], mis["attack"][0]) for dx in tubes]
        w = shots(blank(sound=mis["sound"], trail=mis["trail"], acceleration=mis["acceleration"],
                        shipblastfilter=mis["shipblastfilter"]), spec)
        w["multi"] = 1 + i // 5  # per trigger, cycling the tubes, as the Mini-Missile
        w["shotrepeat"] = level(i, 8, 4)
        levels.append(out.weapon(w, f"Micro-Missile Swarm {i + 1}"))
    out.port(50, "Micro-Missile Swarm", levels, 1100, O[10]["itemgraphic"], 50,
             "Micro-Missile Swarm: the Mini-Missile's missiles, faster and from more tubes each level")
    out.lines.append("")

    # Zica Flamer: the Zica Flamethrower's flames (they pass through enemies: attack 250+n is n damage
    # without stopping), reaching further (speed and life together, as they slow to a stop) and
    # burning harder each level.
    flame = W[O[17]["wpnum"]]
    levels = []
    for i in range(11):
        w = dict(flame)
        reach = level(i, 8, 14)
        w["del_"] = [reach] * 8
        w["sy"] = [reach] * 8
        w["attack"] = [250 + (1 if i >= 3 else 0) + (1 if i >= 8 else 0) + (k in (2, 3)) for k in range(8)]
        w["multi"] = 2 + i * 2 // 10
        w["shotrepeat"] = level(i, 4, 3)
        levels.append(out.weapon(w, f"Zica Flamer {i + 1}"))
    out.port(51, "Zica Flamer", levels, 1000, O[17]["itemgraphic"], 30,
             "Zica Flamer: the Zica Flamethrower as a main gun, its flames reaching further each level")
    out.lines.append("")

    # --- Rear weapons from sidekicks ----------------------------------------------------------
    # Rear guns use little power (the original ones 20-40): the front gun draws from the generator
    # first, and a rear gun short of power doesn't fire.
    # 8-Way Burst: the 8-Way MicroBomb's bombs (bursting on a hit), in more directions each level.
    bomb = W[O[14]["wpnum"]]
    dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, -1), (0, 1)]  # sy > 0 is forward
    levels = []
    for i in range(11):
        spec = [(dx, dy, 0, 0, bomb["sg"][0], bomb["attack"][0]) for dx, dy in dirs[: 2 + i * 6 // 10]]
        w = shots(blank(sound=bomb["sound"], weapani=bomb["weapani"], shipblastfilter=bomb["shipblastfilter"]), spec)
        w["shotrepeat"] = level(i, 24, 14)
        levels.append(out.weapon(w, f"8-Way Burst {i + 1}"))
    out.port(52, "8-Way Burst", levels, 800, O[14]["itemgraphic"], 40,
             "8-Way Burst: the 8-Way MicroBomb's bombs as a rear gun, in more directions each level")
    out.lines.append("")

    # Mine Layer: the Post-It Mine's sticky mines (a hit bursts into two more), drifting slowly ahead
    # of the ship as a curtain for a few seconds (del is a shot's life in frames; 98-121 mean other
    # things), more often and in pairs each level.
    mine = W[O[15]["wpnum"]]
    levels = []
    for i in range(11):
        spec = [(0, 1, dx, 0, mine["sg"][0], mine["attack"][0]) for dx in ([0] if i < 6 else [-8, 8])]
        w = shots(blank(sound=mine["sound"], shipblastfilter=mine["shipblastfilter"]), spec)
        w["del_"] = [96] * 8
        w["shotrepeat"] = level(i, 26, 12)
        levels.append(out.weapon(w, f"Mine Layer {i + 1}"))
    out.port(53, "Mine Layer", levels, 700, O[15]["itemgraphic"], 20,
             "Mine Layer: the Post-It Mine's mines drifting slowly ahead, more often each level")
    out.lines.append("")

    # --- Sidekicks from weapons ---------------------------------------------------------------
    # A sidekick fires one weapon entry: here one power level of a front gun, through the sidekicks'
    # port (16), from the body of an existing sidekick (copy=).
    sk_port = O[1]["wport"]
    out.sidekick(33, 1, "Laser Option", P[4]["op"][0][5], sk_port, 9000,
                 "Laser Option: the Laser's beams (power 6) from a gun pod")
    out.sidekick(34, 2, "Sonic Option", P[11]["op"][0][4], sk_port, 11000,
                 "Sonic Option: the Sonic Wave (power 5) from twin pods")
    out.sidekick(35, 4, "Lightning Option", P[8]["op"][0][4], sk_port, 14000,
                 "Lightning Option: the Lightning Cannon (power 5) from a rotary pod")
    out.sidekick(36, 1, "Banana Option", P[23]["op"][0][4], sk_port, 8000,
                 "Banana Option: the Banana Blast (power 5) from a gun pod")
    out.sidekick(37, 30, "Guided Option", P[31]["op"][0][3], sk_port, 12000,
                 "Guided Option: the Guided Bombs (power 4) from an orbiting satellite")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(out.lines) + "\n")
    print(f"{OUT}: {out.next_weapon - 819} weapons, 6 ports, 5 sidekicks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
