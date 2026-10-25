"""What is left of CAMANIS' grey and blue bunker once it is destroyed (stage 4 of the clean ground: the wreck models
that stand in for the map's painting of it; sheet 7 sprites 1, 3 above 39, 41), built on polish_ice_bunker.py
(2026-10-25). models.cfg: model ice_bunker_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck
enemies/ice_bunker_*_wreck.glb origin; wreck 7 1 ice_bunker_tl_wreck, wreck 7 3 ice_bunker_tr_wreck, wreck 7 39
ice_bunker_bl_wreck, wreck 7 41 ice_bunker_br_wreck (drawn with the live sprite lines' options, yaw=0 height=-4, at the
live pieces' places: CAMANIS' two bunkers, t 3520 and 4192).

The painting (the same at both places, CAMANIS 89e6d1810ded7622 at 552, 3949 and 672, 4621; it lies a row higher up
the screen than the sprites; columns and rows of the 48 x 56 picture below are the sprites'): the bunker burnt out from
inside, its outline, deck rim, back corner panels, the gun's blue housing in the hatch, the skylight with its two lamps
and the head's top plates still standing; black where it burnt through (the map's 0x20): the deck all round the
hatch (columns 9-36 of rows 1-19, the rails and the beam's lower half gone, the left side panels below row 15, the right
ones at rows 11-15), a strip down the deck's left side by the head (columns 3-8 of rows 19-27), the head's left shoulder
(columns 4-15 of rows 25-35) and its right front corner (columns 30-37 of rows 28-37), a gash in the left slope (columns
9-12 of rows 38-41); the head's front blown away (columns 14-29 of rows 36-51: the windows, the lens and its socket
gone, the ice showing through at its foot, rows 47-51); red-hot metal (ramp 7, 0x70-0x74) in three places: a twisted
streak where the left rail was (column 14 of rows 6-15, a cluster at columns 11-16 of rows 9-14) and in the two pits of
the head (columns 7-12 of rows 28-34, columns 31-36 of rows 30-35); the greys round the holes up to four shades darker,
the right slope by the pit nearly black, the side slots and the vents at the front's foot kept.

The model: polish_ice_bunker.py's bunker (its build_whole(), its materials), the window band, the lens and its socket
taken away, then broken: the holes cut with exact booleans (prisms over jagged outlines, polish_jaw_gun_wreck.jagged;
polish_pyramid_wreck.break_with keeps each result in canonical order), their walls and floors charred black (palette
0x00, the painting's black; the live 0x01 was the lens socket's only): the deck's (floor at 0.8, the housing's foot: the
housing stands on it, uncut) through the deck, beam, rails and side panels; the strips beside the head through the deck
and the head (floors 1.0, 0.8); the two pits in the head (floors 2.6 and 3.0, over the deck slab under the head) and
the gash in its left slope; the front's hole a wedge whose floor is a plane sloping from 3.4 at its back (row 36) to
-0.6 at row 46.4 and on down, through the head's foot (the terrain's ice shows there, as in the painting). Then the
soot: SOOT (below), the painting's pixels against the sprites' as how many shades darker the painting is, blurred a
little, sampled at each face's plan point (the deck's and the head's faces split along a 1.5-pixel grid first), each
grey made as much darker (snapped to the live model's greys, 0x02 at most), the blue-grey panels and the housing a step
or two down their ramps. In the holes: the left rail's twisted end lying red-hot (a bent bar), red-hot plates lying in
the deck's hole by it and in the head's pits where the painting's red patches are (thin buckled plates over jagged
outlines, 0x73 at 0.4, a hotter core in each, 0x75 at 0.42, and a few glowing lumps: under the bloom's white), broken
lumps of the deck and the head on the holes' floors (polish_pyramid_wreck.chunk). The head keeps its height (12.12 at
the skylight, as the live model). Cut along the sprites' edges as the live bunker (polish_savara_boss.cut, the caps in
the live's dark), each piece moved so that its sprite's centre is its origin.

Coordinates as polish_ice_bunker.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ice; the
whole's origin is the corner where the four sprites meet; column c's left edge is x = c - 24, row r's top edge
y = 28 - r.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>, --whole
<file.glb> (the uncut wreck too).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (join, drop_unused)
from polish_savara_boss import cut  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_ice_bunker as live  # noqa: E402
from polish_jaw_gun_wreck import ccw, inside, jagged, lump  # noqa: E402
from polish_pyramid_wreck import break_with, chunk, emissive, refine  # noqa: E402

XE, YE = live.XE, live.YE
SEED = 739
PIECES = [(name + "_wreck", sprite, box) for name, sprite, box in live.PIECES]

# --- The painting -----------------------------------------------------------------------------------------------------
# SOOT: one character a pixel of the 48 x 56 picture (rows top to bottom): how many shades darker the painting is than
# the live sprites there (9: burnt through to black or red-hot where the sprite was not dark; '.' none; ' ' not the
# bunker's own pixels: the ice round it).
SOOT = """
............................................
...........................13992............
.................111........999991..........
................29931111111.2393231.........
............19.99999999999992911991.........
..........19991999999292199929199999........
.........199999................991..........
.........144439...............5991..........
.........149999.9999......99.939939.........
..........39999.9999......1...399399........
..........2999999999.......999399399........
.........15999999911.......19939939999.11...
.......19299999991.........19929999999992...
.......2949999999...........9999449999993...
.......994999999919........1999933999999....
...129..999991.999.........999993999........
..1239..99999..99..........991339949........
..13999999999...9.........9991.2221.........
..93999999999.............191...1...........
..139993.9............................21....
..199999..443111.....................9991...
...49999.3331111.....................142....
...3999...111........................121....
...299.21.............................1.....
...23.52...........21.21....................
...12.32.................1..................
...19.33299421........2.....................
....3.949999951.......1.....................
....3.9999999941..22.....1.......1..........
....9.99999999942...............332.........
...13.99999999992..3...........999991.......
...13.99999999321............2.999999.......
...13.99999962.21.........1.99.999999.......
...19.9999992.11...........249.999999.......
...19.999943.1................3999999.......
......932.1542................6999999.......
......11112451....99.99999999.249991........
.........33692....99199999999..149..........
    ...1399996.19199.99993999......292..
    ..12999996199.991994..999......192..
    ...1399795.99.9999999.999......2..1.
    ....149992.99.99....9.999...........
    .....2339...........   99...........
    ......11..... 99999999   ...........
    .............99999.9999 ............
    .............9999999999 9...........
    ............. 99999999999...........
    .............  9......999...........
    .............  ......... ...........
    ....................................
    ....................................
    ....................................
"""

# --- The holes (pixel edges (column, row), before roughening) ---------------------------------------------------------
# The deck's: round the hatch (the housing inside it, uncut), the left rail's end kept (rows 6.6-8.6), out to the side
# panels at the left (rows 15-19) and the right (rows 11-15). Cuts the deck and what lies on it.
DECK_HOLE = [(28.6, 0.9), (31.4, 0.9), (33.6, 2.6), (34.2, 3.8), (36.2, 4.6), (35.8, 6.4), (35.2, 8.2), (36.4, 8.8),
             (36.8, 10.6), (40.2, 11.0), (40.6, 13.0), (40.2, 14.6), (36.2, 15.0), (36.4, 17.2), (33.0, 17.4),
             (28.6, 18.4), (25.4, 19.0), (17.0, 19.0), (12.6, 19.4), (8.8, 19.2), (2.4, 19.0), (1.8, 16.6),
             (2.2, 15.4), (4.2, 14.6), (7.0, 13.6), (7.6, 11.0), (9.6, 9.8), (9.8, 8.6), (13.7, 8.6), (13.7, 6.2),
             (11.2, 5.6), (10.8, 4.6), (12.8, 3.8), (16.6, 2.8), (19.0, 3.7), (28.2, 3.6)]
DECK_FLOOR = live.HATCH_FLOOR - 0.2          # (the housing's foot)
# In and beside the head: (outline, floor, the parts it cuts: name prefixes).
HEAD_HOLES = [
    # the strip down the deck's left side by the head
    ([(2.4, 18.8), (8.8, 19.2), (8.8, 22.0), (9.0, 25.4), (7.0, 28.0), (6.0, 31.2), (4.2, 31.4), (3.4, 27.0),
      (3.0, 24.0)], 1.0,
     ("deck", "side_panel", "stud", "head")),
    # the head's left shoulder
    ([(4.4, 25.6), (9.0, 25.2), (13.2, 25.8), (14.8, 27.6), (15.4, 30.2), (14.4, 32.6), (12.6, 34.6), (9.6, 35.4),
      (6.2, 35.0), (5.0, 32.4), (4.0, 28.6)], 2.6, ("head",)),
    # the head's right front corner
    ([(29.8, 28.6), (33.8, 28.2), (36.8, 29.4), (37.6, 32.4), (37.2, 35.2), (35.2, 37.0), (32.2, 37.2), (30.6, 35.6),
      (29.6, 32.0)], 3.0, ("head",)),
    # the deck's small hole right of the head's back corner
    ([(36.6, 19.4), (40.0, 19.6), (40.2, 21.0), (38.4, 21.8), (36.8, 21.0)], DECK_FLOOR, ("deck", "head")),
    # the gash in the left slope
    ([(8.6, 37.6), (12.8, 37.8), (13.4, 40.0), (12.6, 41.8), (9.4, 41.6), (8.2, 39.6)], 1.0, ("head",)),
]
# The front blown away: its outline; its floor a plane sloping down the screen, FRONT_Z[0] high at row FRONT_ROWS[0],
# FRONT_Z[1] at row FRONT_ROWS[1] (under the ice from row 45: it breaks through the head's foot there).
FRONT_HOLE = [(13.8, 35.8), (17.4, 35.4), (21.6, 36.0), (26.2, 35.6), (29.4, 36.0), (29.6, 40.8), (29.2, 45.4),
              (29.8, 52.6), (14.4, 52.6), (14.6, 46.2), (13.4, 41.2)]
FRONT_ROWS, FRONT_Z = (36.0, 46.4), (3.4, -0.6)
GONE = ("lens", "window_frame", "pane", "sill", "divider")   # (the window band and the lens: in the front's hole)

# --- What lies in the holes ------------------------------------------------------------------------------------------
# The left rail's end, twisted and red-hot (column, row, height over the deck hole's floor; its radius).
RAIL_GLOW = ([(14.3, 5.2, 0.75), (14.0, 7.6, 0.6), (14.6, 10.2, 0.7), (13.9, 12.8, 0.6), (14.8, 15.6, 0.65)], 0.7)
# The red-hot metal lying in the holes (the painting's red patches): outlines, the floor they lie on, how much they
# buckle; a hotter core in each (its outline shrunk to CORE of the plate's about its middle).
GLOWS = [([(11.0, 9.2), (12.8, 9.6), (13.4, 11.4), (15.8, 11.2), (16.4, 13.0), (15.8, 15.2), (13.6, 15.0),
           (12.2, 13.4), (10.8, 12.0)], DECK_FLOOR, 0.25),
         ([(8.8, 27.8), (11.2, 27.6), (13.0, 28.8), (12.8, 31.0), (11.8, 32.2), (9.6, 32.4), (9.0, 34.2), (6.8, 34.0),
           (6.8, 31.0), (8.6, 30.2)], 2.6, 0.35),
         ([(32.8, 29.8), (35.2, 30.0), (36.4, 32.6), (36.6, 35.0), (35.6, 36.2), (33.4, 35.6), (31.6, 35.2),
           (30.8, 32.4), (31.2, 30.8)], 3.0, 0.35)]
CORE = 0.55
# A few glowing lumps on them (column, row, radius, floor).
EMBERS = [(12.2, 12.2, 0.7, DECK_FLOOR), (10.4, 30.6, 0.8, 2.6), (8.2, 32.8, 0.6, 2.6), (34.4, 32.4, 0.8, 3.0),
          (33.0, 34.6, 0.6, 3.0)]
# Broken lumps on the holes' floors: how many in the deck's hole, in the front's.
DECK_LUMPS, FRONT_LUMPS = 12, 7
# The housing and the embers' clusters: no lumps there (columns, rows: x0, x1, y0, y1).
CLEAR = [(18.6, 27.4, 5.6, 19.4), (10.6, 16.6, 5.4, 15.6)]


def P(c, r):
    return (XE(c), YE(r))


def hole_outline(points, seed, amount=0.4):
    return ccw(jagged([P(c, r) for c, r in points], seed, amount, 0.8))


def materials():
    """The live bunker's (its black, 0x01, was the lens socket's only: gone), the char of the holes (the painting's
    black: 0x00) and the embers'."""
    m = live.materials()
    del m["black"], m["lens"], m["lens_hot"]
    m["char"] = k.material("ibwreck_char", palette=0x00, metallic=0.0, roughness=1.0)
    m["ember"] = emissive("ibwreck_ember", 0x73, 0.4, 0.0, 1.0)
    m["hot"] = emissive("ibwreck_hot", 0x75, 0.42, 0.0, 0.8)
    return m


# --- Soot -------------------------------------------------------------------------------------------------------------

class Soot:
    """SOOT as a field over the plan: blurred a little (sigma in pixels), bilinear between the pixels' middles."""

    def __init__(self, text, sigma=0.75):
        rows = [line.ljust(48) for line in text.strip("\n").split("\n")]
        raw = [[(int(ch) if ch.isdigit() else 0) for ch in row[:48]] for row in rows]
        rad = 2
        kern = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-rad, rad + 1)]
        s = sum(kern)
        kern = [v / s for v in kern]
        h, w = len(raw), 48

        def blur(a, axis):
            out = [[0.0] * w for _ in range(h)]
            for r in range(h):
                for c in range(w):
                    t = 0.0
                    for i, kv in enumerate(kern):
                        rr, cc = (r + i - rad, c) if axis == 0 else (r, c + i - rad)
                        rr, cc = min(max(rr, 0), h - 1), min(max(cc, 0), w - 1)
                        t += kv * a[rr][cc]
                    out[r][c] = t
            return out
        self.h, self.w = h, w
        self.a = blur(blur(raw, 0), 1)

    def __call__(self, x, y):
        u, v = x + 24.0 - 0.5, 28.0 - y - 0.5
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def px(r, c):
            return self.a[r][c] if 0 <= r < self.h and 0 <= c < self.w else 0.0
        return ((1 - fu) * (1 - fv) * px(r0, c0) + fu * (1 - fv) * px(r0, c0 + 1) + (1 - fu) * fv * px(r0 + 1, c0) +
                fu * fv * px(r0 + 1, c0 + 1))


GREYS = (0x02, 0x06, 0x08, 0x0a, 0x0c)
GREY_KEY = {0x02: "dark", 0x06: "deck", 0x08: "steel", 0x0a: "lit", 0x0c: "hi"}
# The blue-grey parts' steps down (a step for 1.5-3.5 shades darker, two for 3.5-6.5, black beyond).
BLUE_STEPS = {"glass_teal": ("panel", "panel_dark"), "panel": ("panel_dark", "housing_dark"),
              "panel_dark": ("housing_dark", "dark"), "housing": ("housing_dark", "dark"),
              "housing_dark": ("dark", "dark")}
UNTOUCHED = ("glass", "light", "ember", "hot", "char")


def burnt(m, key, d):
    """The material a face of m[key] takes where the painting is d shades darker (None: as it is)."""
    if d < 1.5 or key in UNTOUCHED:
        return None
    if d >= 6.5:
        return m["dark"] if key != "dark" else None
    index = next((i for i, kk in GREY_KEY.items() if kk == key), None)
    if index is not None:
        target = max(1.0, index - d)
        new = min(GREYS, key=lambda s: (abs(s - target), s))
        return m[GREY_KEY[new]] if new != index else None
    steps = BLUE_STEPS.get(key)
    if steps is None:
        return None
    return m[steps[0] if d < 3.5 else steps[1]]


STEP = 1.5                      # the grid the soot's faces are split along


def scorch(obj, soot, m, split=True):
    """obj's faces (but its undersides) painted by the soot under their plan points; split along a 1-pixel grid first
    (its faces turned up), so that the soot follows the painting."""
    if split:
        lo, hi = mk.bounds([obj])
        refine(obj, (lo.x - 0.01, hi.x + 0.01, lo.y - 0.01, hi.y + 0.01), STEP, lambda f: f.normal.z > 0.2)
    keys = {mat.name: key for key, mat in m.items()}
    mats = list(obj.data.materials)
    slots = {}
    for poly in obj.data.polygons:
        if poly.normal.z < -0.3:
            continue
        src = mats[poly.material_index] if poly.material_index < len(mats) else None
        key = keys.get(src.name) if src is not None else None
        if key is None:
            continue
        new = burnt(m, key, soot(poly.center.x, poly.center.y))
        if new is None or new is src:
            continue
        if new.name not in slots:
            slots[new.name] = mk.slot_of(obj, new)
        poly.material_index = slots[new.name]
    obj.data.update()
    return obj


# --- The break --------------------------------------------------------------------------------------------------------

def overlaps(obj, outline):
    xs, ys = [p[0] for p in outline], [p[1] for p in outline]
    lo, hi = mk.bounds([obj])
    return not (hi.x < min(xs) or lo.x > max(xs) or hi.y < min(ys) or lo.y > max(ys))


def cut_holes(whole, m):
    """The holes cut out of the parts they reach; returns the parts left."""
    parts = []
    for obj in whole:
        if obj.name.startswith(GONE):
            data = obj.data
            bpy.data.objects.remove(obj)
            if data.users == 0:
                bpy.data.meshes.remove(data)
        else:
            parts.append(obj)
    jobs = [(hole_outline(DECK_HOLE, 3.1), lambda o: mk.prism("deck_hole", o, DECK_FLOOR, 40.0, m["char"]),
             ("deck", "beam", "rail", "side_panel", "stud"))]
    for i, (points, floor, which) in enumerate(HEAD_HOLES):
        jobs.append((hole_outline(points, 5.3 + 2.1 * i, 0.35),
                     lambda o, f=floor, i=i: mk.prism(f"head_hole{i}", o, f, 40.0, m["char"]), which))
    (r0, r1), (z0, z1) = FRONT_ROWS, FRONT_Z

    def front_floor(x, y):
        return z0 + (z1 - z0) * ((28.0 - y) - r0) / (r1 - r0)
    jobs.append((hole_outline(FRONT_HOLE, 9.7, 0.45),
                 lambda o: mk.wedge("front_hole", o, 0.0, lambda x, y: 40.0, m["char"], bottom=front_floor),
                 ("head", "rail", "sky")))
    for outline, make, which in jobs:
        hit = [o for o in parts if o.name.startswith(which) and not o.name.startswith("housing") and
               overlaps(o, outline)]
        if not hit:
            continue
        cutter = make(outline)
        kept = break_with(hit, cutter)
        parts = [o for o in parts if o not in hit] + kept
    parts.sort(key=lambda o: o.name)
    return parts, front_floor


def reshade(obj):
    if obj.name.startswith(("head_rail", "rail")):
        return k.smooth(obj, 40)
    return mk.shade(obj, 35.0)


def glow_plate(name, outline, z, buckle, mat, seed, thickness=0.22):
    """A plate of red-hot metal lying on a floor: a thin prism over a jagged outline, its points pushed up and down a
    little by noise (buckled)."""
    from mathutils import noise
    obj = mk.prism(name, outline, z, z + thickness, mat)
    for v in obj.data.vertices:
        v.co.z += buckle * (0.5 + 0.5 * noise.noise(Vector((v.co.x * 0.6 + seed, v.co.y * 0.6 - seed, 0.3 * seed))))
    obj.data.update()
    mk.shade(obj, 40.0)
    return obj


def debris(parts, m, front_floor):
    """The rail's red-hot end, the red-hot plates and embers, the broken lumps on the holes' floors."""
    rng = random.Random(SEED)
    made = []
    pts, radius = RAIL_GLOW
    bar = mk.smooth_tube("rail_glow", [(XE(c), YE(r), DECK_FLOOR + z, radius) for c, r, z in pts], m["hot"], 10)
    made.append(k.smooth(bar, 60))
    for i, (points, floor, buckle) in enumerate(GLOWS):
        outline = hole_outline(points, 13.0 + 1.9 * i, 0.3)
        made.append(glow_plate(f"glow{i}", outline, floor + 0.02, buckle, m["ember"], 4.0 + i))
        cx = sum(p[0] for p in outline) / len(outline)
        cy = sum(p[1] for p in outline) / len(outline)
        core = [(cx + (x - cx) * CORE, cy + (y - cy) * CORE) for x, y in outline]
        made.append(glow_plate(f"glow{i}_core", core, floor + 0.16, buckle, m["hot"], 4.0 + i, 0.2))
    for i, (c, r, rad, floor) in enumerate(EMBERS):
        x, y = P(c, r)
        made.append(k.smooth(lump(f"ember{i}", (x, y, floor + 0.3 + 0.2 * rad), (rad, rad * 0.8, rad * 0.45),
                                  m["hot"], 2.3 + 1.37 * i, 0.3, 1), 70))

    def clear(x, y):
        return not any(XE(c0) <= x <= XE(c1) and YE(r1) <= y <= YE(r0) for c0, c1, r0, r1 in CLEAR)
    deck_outline = hole_outline(DECK_HOLE, 3.1)
    front_outline = hole_outline(FRONT_HOLE, 9.7, 0.45)
    for name, outline, count, floor, mats in (
            ("deck_lump", deck_outline, DECK_LUMPS, lambda x, y: DECK_FLOOR, ("deck", "dark", "steel", "dark")),
            ("front_lump", front_outline, FRONT_LUMPS, front_floor, ("steel", "dark", "deck", "dark"))):
        xs, ys = [p[0] for p in outline], [p[1] for p in outline]
        n = tries = 0
        while n < count and tries < 500:
            tries += 1
            x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
            size = rng.uniform(0.9, 1.9)
            if not inside((x, y), outline) or not clear(x, y):
                continue
            if any(not inside((x + dx, y + dy), outline) for dx, dy in ((size, 0), (-size, 0), (0, size), (0, -size))):
                continue
            z = floor(x, y)
            if z < 0.0:
                continue
            made.append(chunk(f"{name}{n}", (x, y, z - 0.15), size, rng, m[mats[n % len(mats)]],
                              rng.uniform(0.4, 0.75)))
            mk.shade(made[-1], 30.0)
            n += 1
    return made


def build_whole():
    m = materials()
    whole, _ = live.build_whole()
    # (build_whole made its own materials: the same names, so the same materials as m's)
    parts, front_floor = cut_holes(whole, m)
    soot = Soot(SOOT)
    for obj in parts:
        mk.apply(obj)
        if obj.name.startswith(("lamp", "sky_pane")):
            continue
        scorch(obj, soot, m, split=obj.name in ("deck", "head"))
        reshade(obj)
    parts += debris(parts, m, front_floor)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole bunker wreck: %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "ice_bunker_wreck_whole", whole, size=(48, 56), scale=10, distance=1.9)
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [db.join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            data = obj.data
            bpy.data.objects.remove(obj)
            if data.users == 0:
                bpy.data.meshes.remove(data)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
