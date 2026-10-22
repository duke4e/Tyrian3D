"""The fruit and the two odd pick-ups of the coins sheet (enemies' drops and loose items of episodes 1-5), polished
(2026-10-22, round 32; they replace wave3_ai_items.py's strawberry, grapes_purple, grapes_green, fruit_round,
check_rainbow and orbiter). Items are drawn as models of their own centred in height on their layer (the ground
enemies' layer for drops of ground enemies, the sky's for the others; models.cfg: not origin), turned about the
sprite's centre: the fruit turns slowly (spin=1.5, as the other loose items), the tick keeps still (its symbol stays
readable), the asteroid killer turns with its frames (yaw=frames).

- strawberry (coins 75; enemy 503: 300 credits, 20 in BUBBLES, MINEMAZE, WINDY and FRUIT, on the ground, in the sky
  and dropped): as the sprite (12 x 14) and its upscale draw it, a red strawberry lying tip down the screen (rows 3-13,
  widest at rows 5-9, its tip at row 13), lit at its upper left (0x79, 0x7b), seeds in lighter reds (0x76-0x77), a
  crown of green leaves across its top (rows 0-3, 0x24-0x2b in a dark green outline), the pink shoulder under it
  (0x48). Built as a glossy strawberry: a body lofted along its length (half-width and depth per y: BERRY), some 40
  golden seeds set into its skin in a quincunx (where the camera sees the skin), a calyx of seven pointed sepals
  splayed out from the stem over the shoulder, curling at their tips, a short stem up the screen. The red in bands
  by how much the skin faces up (the game's sun shades the rest), glowing a little in itself (0.12-0.26) so that it
  reads red, not brown, from the slanted camera.
- fruit_round, fruit_orange (coins 37 and 113; enemies 502, 504: the lime of 150 credits, 8 in IXMUCANE, SAWBLADES,
  SAVARA and FRUIT, and the orange of 500, 4 in SAVARA and FRUIT): one picture in ramps 2 and 7 (the orange two shades
  darker, its outline 0x01 instead of 0x20): a round fruit 12 pixels across (rows 1-12), lit at its upper right, a
  small dark x at its lower left (the navel). Built as one round citrus fruit (a fine icosphere a little flattened,
  its peel pitted with dimples of noise), painted in bands by how much it faces up, the navel a nub in a little star of
  creases; two models, the lime's in ramp 2 and the orange's in ramp 7, each glowing a little in its own colours (the
  old model took the frame's ramp with color=sprite, which keeps emission in the model's own colour, so it could not
  glow: two models now).
- grapes_green, grapes_purple (coins 38 and 114 (enemies 506, 510: 1000 and 500 credits; 38 and 114 are the same
  pixels), coins 19 (505: 750 credits); 4, 13 and 4 of them in BONUS, MINEMAZE, MARKERS, IXMUCANE, SAWBLADES, SAVARA
  and FRUIT): a bunch of nine grapes (each a 2 x 2 ball lit at its upper left: 0x2c over 0x29, 0x27; purple 0x5c over
  0x59, 0x57) hanging from a curly brown vine (ramp 1: its left end hooked, across the top, curling down on the right;
  the purple bunch's vine a shade darker), the stalk into the bunch. The grapes are one picture in ramps 2 and 5 but the
  vine stays brown, so two models (color=sprite would turn the vine green or purple). Built as such a bunch: glossy
  grapes (polish_grape_wing.py's grapes: painted icospheres, their rims darker, a lit cap, glowing faintly in their
  own colours), nine in front where the sprite draws them, eight behind filling the bunch out; the vine and the stalk
  brown tubes along the sprite's curl, knotted where the stalk leaves it.
- check_rainbow (coins 245, 2x2; enemy 476: 800 credits, dropped in BUBBLES and AST. CITY): a tick in a black outline
  (0x01), its shadow (0xa0, 0xa1) cast to the lower right (left out: the game casts the model's own), coloured like a
  rainbow along its stroke: red and orange the short stroke (ramp 7), yellow round the bottom, then green (ramp 2),
  blue (ramps 3 and 8) and violet (ramp 5) up the long stroke. Built as an enamelled tick: the stroke a solid over its
  outline (polish_ring_machine.relief; the two strokes' edges straight, their ends cut level as the sprite's, their
  meeting cut level at the sprite's lowest row, every corner rounded; the strokes' middle lines and widths measured
  from the sprite's edges), its top a rounded cushion higher along the stroke's middle, cut along smooth contours
  into six bands of colour along the stroke (red 0x76, orange 0x79, yellow 0x7c, green 0xca, blue 0x9b, violet 0x5c:
  brighter than the sprite's ramps 2, 3 and 5, a rainbow; the sides a shade or two darker), each glowing in its own
  colour (0.3 on top, 0.18 on the sides); under it a black enamel plate a pixel wider all round (the sprite's
  outline). No spin (models.cfg yaw=0).
- orbiter (coins 153; enemy 535: the orbiting asteroid killer, value -3: the player who takes it gets a shot that
  orbits the ship; 4 dropped in ASTEROID1; its animation 153 x5, 155 x4, 157 x5, 155 x4 swings two blue points round
  a ball of fire, from upper right / lower left (153) through up / down (155) to upper left / lower right (157) and back):
  the fire ball (rows 8-19, its hot core at the upper left, 0x7d-0x7e, orange and red to its rim) and two blue
  crystal points (ramp 13, 0xd6-0xdb, outlined in ramp 9's dark blues), their broad ends out, their points at the ball.
  Built with the points up and down the screen (155's pose; models.cfg turns it with the frames, yaw=frames:36:45:ccw,
  so that the first frame shows 153's pose and the points orbit the ball counter-clockwise, half a turn a cycle: the
  model looks the same turned half round): the ball a glowing icosphere painted in bands of fire by its heat (hotter
  towards its top, swirled by noise), every band glowing in its own colour (0.3-0.62), the points flattened crystal
  arrowheads (rhombic pyramids, their edges bevelled), teal faces by the light they get, glowing a little (0.16), the
  broad base dark blue.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is the
sprite's centre: a 1x1 sprite's pixel (6, 7) (column c is x = c + 0.5 - 6, row r is y = 6.5 - r), a 2x2 sprite's
pixel (12, 14) (x = c + 0.5 - 12, y = 13.5 - r). Every mesh is triangulated before the export (polish_k_pod
.triangulate: the same output with and without --check); no random numbers, no booleans.

models.cfg: model strawberry, grapes_purple, grapes_green, fruit_round, check_rainbow, orbiter items/<name>.glb
(unchanged); new: model fruit_orange items/fruit_orange.glb; sprite coins 37 fruit_round spin=1.5 and sprite coins 113
fruit_orange spin=1.5 (both without color=sprite); the other sprite lines unchanged (coins 75 strawberry spin=1.5,
coins 19 grapes_purple spin=1.5, coins 38 and 114 grapes_green spin=1.5, coins 245 check_rainbow yaw=0 glow=14:0.2,
coins 153 orbiter yaw=frames:36:45:ccw glow=18:0.4).

Replaces wave3_ai_items.py's strawberry (STRAWBERRY, BERRY_PROFILE, berry_surface(), strawberry()), grapes (GRAPES,
grapes(), grapes_purple(), grapes_green()), fruit_round (ROUND, fruit_round()), check_rainbow (CHECK, check_rainbow(),
and SHADOW, which only it read) and orbiter (ORBITER, orbiter()), with their docstring paragraphs and registrations;
its red_keel_shell and hot_dog stay. In wave3_ai_art.py: STRAWBERRY, GRAPES_P, GRAPES_P95, GRAPES_G, GRAPES_G114, LIME,
ORANGE, CHECK, ORBITER and ORBITER_153 (read only by those models, or by nothing).

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (each model's silhouette against
coins.png: the tick without its shadow, the orbiter against 155 and, turned 45 degrees clockwise, 153), --preview
<prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "enemies"))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, resample, round_edge  # noqa: E402
from polish_torm_beetle import tube  # noqa: E402

LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun
FLAT = LIGHT.z


def lit(name, index, strength=0.0, metallic=0.0, roughness=0.3):
    pal = k.level_palette()
    extra = dict(emission=pal[index], emission_strength=strength) if strength > 0 else {}
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, **extra)


def light_value(n, base, a=3.2, b=1.2):
    return base + a * (n.dot(LIGHT) - FLAT) + b * (n.z - 1.0)


def paint_by_up(obj, bands, m):
    """band_split by how much each vertex faces up (its normal's z): the same from every side, as the item turns."""
    obj.data.update()
    values = [v.normal.z for v in obj.data.vertices]
    band_split(obj, values, [(lo, m[key]) for lo, key in bands])
    return obj


def finish(opts, name, parts, sprite, large, **kw):
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    obj = join(parts, name) if len(parts) > 1 else parts[0]
    obj.name = name
    obj.data.name = name
    bpy.context.view_layer.update()
    kit.finish(opts, name, [obj], sprite, large, **kw)
    return obj


# --- Coins 75: the strawberry ------------------------------------------------------------------------------------------
# Its body along the screen's y: (y, half-width, half-depth), from its tip up to its shoulder.
BERRY = [(-7.15, 0.12, 0.12), (-6.75, 1.6, 1.25), (-6.05, 3.0, 2.4), (-4.9, 4.35, 3.35), (-3.4, 5.4, 4.05),
         (-1.6, 6.0, 4.45), (0.3, 6.15, 4.6), (1.9, 5.95, 4.45), (3.0, 5.35, 4.0), (3.8, 4.2, 3.25), (4.3, 2.7, 2.3),
         (4.6, 1.2, 1.2), (4.7, 0.15, 0.3)]
BERRY_BANDS = [(-2.0, "skin_dark"), (-0.15, "skin_low"), (0.3, "skin"), (0.66, "skin_top"), (0.9, "skin_lit")]
SEED_ROWS = 6                     # rings of seeds along it, SEEDS a ring round it (staggered), where they show
SEEDS = 9
SEED_R = (0.27, 0.38, 0.15)       # a seed's half-sizes: across, along the berry, its height
CALYX_C = Vector((0.0, 4.15, 1.75))   # where the sepals and the stem leave the berry
# The sepals: (direction round the berry's axis, degrees from +X towards the camera; length; how far they lean up the
# screen out of the plane across the berry, degrees): the side ones long and low (the sprite's crown spans its whole
# width), the top ones leaning up the screen.
SEPALS = [(-16.0, 6.4, 6.0), (16.0, 5.9, 20.0), (52.0, 4.7, 38.0), (90.0, 4.2, 50.0), (128.0, 4.7, 38.0),
          (164.0, 5.9, 20.0), (196.0, 6.4, 6.0)]
SEPAL_W, SEPAL_H = 1.35, 0.28


def strawberry_materials():
    return {
        "skin_dark": lit("straw_dark", 0x72, 0.12, roughness=0.2),
        "skin_low": lit("straw_low", 0x74, 0.15, roughness=0.18),
        "skin": lit("straw_skin", 0x75, 0.19, roughness=0.16), "skin_top": lit("straw_top", 0x76, 0.22, roughness=0.15),
        "skin_lit": lit("straw_lit", 0x78, 0.26, roughness=0.14), "shoulder": lit("straw_shoulder", 0x48, 0.12),
        "seed": lit("straw_seed", 0x7c, 0.22, metallic=0.1, roughness=0.3),
        "leaf_dark": lit("straw_leaf_dark", 0x24, 0.06, roughness=0.45),
        "leaf": lit("straw_leaf", 0x27, 0.08, roughness=0.4),
        "leaf_lit": lit("straw_leaf_lit", 0x2a, 0.1, roughness=0.38),
    }


def berry_section(y):
    pts = k.profile([p for p in BERRY], step=0.05)
    best = min(pts, key=lambda p: abs(p[0] - y))
    return best[1], best[2]


def strawberry_body(m):
    pts = k.profile(BERRY, step=0.42)
    rings = [k.ring(y, max(w, 0.05), max(h, 0.05), 24) for y, w, h in pts]
    body = k.loft("straw_body", rings, m["skin"])
    k.smooth(body, 70)
    paint_by_up(body, BERRY_BANDS, m)
    # the shoulder under the calyx darker pink
    mk.paint(body, lambda c, n: m["shoulder"] if c.y > 3.9 and n.z > -0.2 else None)
    return body


def seeds(m):
    out = []
    for i in range(SEED_ROWS):
        y = -5.6 + i * (8.8 / (SEED_ROWS - 1))
        hw, hh = berry_section(y)
        for j in range(SEEDS):
            phi = math.pi * (j + (0.5 if i % 2 else 0.0)) / SEEDS * 2.0 - math.pi / 2
            x, z = hw * math.cos(phi), hh * math.sin(phi)
            if z < -0.25 * hh or y > 3.4:
                continue
            nrm = Vector((math.cos(phi) / max(hw, 0.1), 0.0, math.sin(phi) / max(hh, 0.1))).normalized()
            seed = k.ellipsoid(f"seed{i}_{j}", (0.0, 0.0, 0.0), SEED_R, m["seed"], 6, 4)
            rot = nrm.to_track_quat("Z", "Y").to_matrix().to_4x4()
            seed.data.transform(Matrix.Translation(Vector((x, y, z)) - nrm * 0.06) @ rot)
            k.recalc_normals(seed)
            k.smooth(seed, 80)
            out.append(seed)
    return out


def calyx(m):
    out = []
    for i, (angle, length, lean_deg) in enumerate(SEPALS):
        a = math.radians(angle)
        lean = math.radians(lean_deg)
        out_dir = Vector((math.cos(a) * math.cos(lean), math.sin(lean), math.sin(a) * math.cos(lean)))
        side = out_dir.cross(Vector((0.0, 1.0, 0.0)))
        mid = CALYX_C + out_dir * length * 0.5
        tip = CALYX_C + out_dir * length + Vector((0.0, 0.25, 0.0))
        # lying over the shoulder: the middle pressed onto the berry, the tip curling up off it
        hw, hh = berry_section(max(min(mid.y, 4.6), -7.0))
        r_mid = math.hypot(mid.x / max(hw, 0.3), mid.z / max(hh, 0.3))
        if r_mid < 1.05:
            scale = 1.05 / max(r_mid, 1e-3)
            mid = Vector((mid.x * scale, mid.y, mid.z * scale))
        st = [(CALYX_C.x, CALYX_C.y, CALYX_C.z, SEPAL_W * 0.55, SEPAL_H),
              (mid.x, mid.y, mid.z, SEPAL_W, SEPAL_H),
              (tip.x, tip.y, tip.z + 0.25, 0.08, 0.06)]
        leaf = tube(f"sepal{i}", [s + (1.4,) for s in st], m["leaf"], segments=10)
        leaf.data.update()
        values = [light_value(v.normal, 5.9) for v in leaf.data.vertices]
        band_split(leaf, values, [(-99, m["leaf_dark"]), (5.4, m["leaf"]), (6.4, m["leaf_lit"])])
        k.smooth(leaf, 70)
        out.append(leaf)
    stem = tube("stem", [(0.0, 4.0, 1.9, 0.55, 0.55, 2.0), (0.15, 5.6, 2.5, 0.48, 0.48, 2.0),
                         (0.45, 6.9, 2.6, 0.42, 0.42, 2.0)], m["leaf"], segments=10)
    stem.data.update()
    band_split(stem, [light_value(v.normal, 6.0) for v in stem.data.vertices],
               [(-99, m["leaf_dark"]), (5.4, m["leaf"]), (6.4, m["leaf_lit"])])
    k.smooth(stem, 70)
    out.append(stem)
    return out


def strawberry(opts):
    m = strawberry_materials()
    parts = [strawberry_body(m)] + seeds(m) + calyx(m)
    finish(opts, "strawberry", parts, 75, False, distance=0.32)


# --- Coins 37 and 113: the lime and the orange -------------------------------------------------------------------------
FRUIT_R = (6.0, 6.0, 5.4)
DIMPLE = (0.1, 1.05)              # the peel's dimples: depth, how many per pixel (noise scale)
NAVEL = (-2.3, -2.7)              # where the navel is, seen from above (the sprite's x at its lower left)
# (rim, body, top, cap, navel) palette indices and emission strengths
FRUITS = {
    "fruit_round": ((0x27, 0.08), (0x2a, 0.12), (0x2b, 0.14), (0x2c, 0.16), (0x25, 0.06)),
    "fruit_orange": ((0x76, 0.12), (0x78, 0.16), (0x79, 0.19), (0x7a, 0.22), (0x75, 0.1)),
}
FRUIT_BANDS = (0.12, 0.55, 0.86)  # borders by how much the peel faces up (rim | body | top | cap)


def citrus(opts, name):
    (rim, rg), (body, bg), (top, tg), (cap, cg), (navel, ng) = FRUITS[name]
    m = {"rim": lit(f"{name}_rim", rim, rg, roughness=0.42), "body": lit(f"{name}_body", body, bg, roughness=0.38),
         "top": lit(f"{name}_top", top, tg, roughness=0.34), "cap": lit(f"{name}_cap", cap, cg, roughness=0.3),
         "navel": lit(f"{name}_navel", navel, ng, roughness=0.6)}
    shape = Ellipsoid((0.0, 0.0, 0.0), FRUIT_R)

    def dimples(d, p, n):
        v = noise.noise(Vector((p.x * DIMPLE[1], p.y * DIMPLE[1], p.z * DIMPLE[1] + 7.3)))
        return -DIMPLE[0] * max(0.0, v) * 1.6

    paint = [(lambda p, n: n.z, FRUIT_BANDS, ("rim", "body", "top", "cap"))]
    ball = painted_ball("peel", shape, paint, m, subdivisions=5, displace=dimples, smooth_angle=80)
    # the navel: a nub in a little star of creases, where the sprite draws its x
    p, nrm = shape.point(Vector((NAVEL[0] / FRUIT_R[0], NAVEL[1] / FRUIT_R[1],
                                 math.sqrt(max(0.0, 1 - (NAVEL[0] / FRUIT_R[0]) ** 2 - (NAVEL[1] / FRUIT_R[1]) ** 2)))))
    marks = []
    rot = nrm.to_track_quat("Z", "Y").to_matrix().to_4x4()
    nub = k.ellipsoid("nub", (0.0, 0.0, 0.0), (0.42, 0.42, 0.22), m["navel"], 10, 6)
    nub.data.transform(Matrix.Translation(p - nrm * 0.02) @ rot)
    marks.append(nub)
    for j in range(5):
        a = 2 * math.pi * j / 5 + 0.3
        crease = k.ellipsoid(f"crease{j}", (0.0, 0.0, 0.0), (0.16, 0.62, 0.06), m["navel"], 6, 4)
        crease.data.transform(Matrix.Translation(p - nrm * 0.03) @ rot @ Matrix.Rotation(a, 4, "Z") @
                              Matrix.Translation((0.0, 0.7, 0.0)))
        marks.append(crease)
    for o in marks:
        k.recalc_normals(o)
        k.smooth(o, 80)
    sprite = 37 if name == "fruit_round" else 113
    finish(opts, name, [ball] + marks, sprite, False, distance=0.32)


# --- Coins 38 / 114 and 19: the grapes ---------------------------------------------------------------------------------
# The front grapes' middles (the sprite's 2 x 2 balls, lit at their upper left), the ones behind; their radii.
GRAPES_FRONT = [(0.0, 3.0), (-3.0, 2.0), (3.0, 2.0), (1.0, 0.0), (-2.0, -1.0), (4.0, -1.0), (2.0, -3.0), (-1.0, -4.0),
                (1.0, -6.0)]
GRAPES_BACK = [(-1.5, 1.4), (1.6, 1.8), (-0.6, -1.9), (2.9, 0.5), (-2.75, 0.3), (0.4, -4.6), (2.7, -2.4),
               (-0.9, 1.1)]
GRAPE_R = (1.52, 1.52, 1.4)
GRAPE_Z = (2.2, 1.3, 0.6)         # the front grapes' middles: base height, the dome over it; the back ones' lower
# The vine: its curl across the top (x, y, z, radius) and the stalk into the bunch.
VINE = [(-3.7, 4.0, 2.1, 0.46), (-3.55, 5.3, 2.6, 0.56), (-2.6, 6.25, 2.9, 0.6), (-1.0, 6.5, 3.0, 0.62),
        (0.5, 6.05, 3.05, 0.62), (1.8, 5.3, 3.0, 0.6), (3.2, 4.9, 2.9, 0.58), (4.5, 4.45, 2.75, 0.55),
        (5.35, 3.55, 2.55, 0.5), (5.55, 2.3, 2.3, 0.46)]
STALK = [(0.4, 5.7, 3.0, 0.5), (1.0, 4.6, 3.05, 0.46), (1.35, 3.4, 3.0, 0.42), (1.2, 2.4, 2.8, 0.36)]
GRAPES = {
    # grapes: (rim, body, lit) indices and emission strengths; the vine's (dark, body, lit) indices
    "grapes_green": (((0x26, 0.08), (0x29, 0.13), (0x2c, 0.18)), (0x13, 0x15, 0x18)),
    "grapes_purple": (((0x56, 0.09), (0x59, 0.14), (0x5c, 0.19)), (0x12, 0x14, 0x17)),
}


def grapes(opts, name):
    ((rim, rg), (body, bg), (cap, cg)), (vd, vb, vl) = GRAPES[name]
    m = {"grape_dark": lit(f"{name}_rim", rim, rg, roughness=0.34),
         "grape": lit(f"{name}_body", body, bg, roughness=0.28),
         "grape_lit": lit(f"{name}_lit", cap, cg, roughness=0.22),
         "vine_dark": lit(f"{name}_vine_dark", vd, 0.0, roughness=0.6),
         "vine": lit(f"{name}_vine", vb, 0.04, roughness=0.55),
         "vine_lit": lit(f"{name}_vine_lit", vl, 0.06, roughness=0.5)}
    paint = [(lambda p, n: n.z, (0.25, 0.78), ("grape_dark", "grape", "grape_lit"))]
    parts = []
    for i, (x, y) in enumerate(GRAPES_FRONT):
        q = (x / 5.5) ** 2 + ((y + 1.0) / 6.5) ** 2
        z = GRAPE_Z[0] + GRAPE_Z[1] * max(0.0, 1.0 - q)
        s = 1.0 - 0.03 * ((i * 7) % 3)
        parts.append(painted_ball(f"g{i}", Ellipsoid((x, y, z), tuple(r * s for r in GRAPE_R)), paint, m,
                                  subdivisions=2, smooth_angle=80))
    for i, (x, y) in enumerate(GRAPES_BACK):
        parts.append(painted_ball(f"b{i}", Ellipsoid((x, y, GRAPE_Z[2]), tuple(r * 0.95 for r in GRAPE_R)), paint, m,
                                  subdivisions=2, smooth_angle=80))
    for nm, pts in (("vine", VINE), ("stalk", STALK)):
        obj = mk.smooth_tube(nm, pts, m["vine"], 10, 2)
        obj.data.update()
        band_split(obj, [light_value(v.normal, 5.8) for v in obj.data.vertices],
                   [(-99, m["vine_dark"]), (5.3, m["vine"]), (6.3, m["vine_lit"])])
        k.smooth(obj, 60)
        parts.append(obj)
    knot = k.ellipsoid("knot", (0.45, 5.65, 3.05), (0.72, 0.62, 0.6), m["vine"], 12, 8)
    k.smooth(knot, 70)
    parts.append(knot)
    sprite = 38 if name == "grapes_green" else 19
    finish(opts, name, parts, sprite, False, distance=0.32)


# --- Coins 245: the rainbow tick ---------------------------------------------------------------------------------------
# The stroke's middle line: the short stroke's top, the bottom corner, the long stroke's top; their half-widths.
TICK = [(-6.35, 2.0), (-2.29, -6.12), (5.32, 8.0)]
TICK_W = (2.1, 2.55)
TICK_BOTTOM = -6.0                # the strokes' meeting cut level here (the sprite's lowest coloured row), rounded
TICK_H, TICK_CROWN, TICK_EDGE = 1.75, 0.65, 1.0   # the top's height at the edge's foot, over the middle, the rounding
TICK_BASE = 0.45                  # the stroke stands on the plate this high
PLATE = (0.9, 0.0, 1.05)          # the black plate: how much wider, its underside and top
SHADOW = (0xa0, 0xa1)             # the sprite's shadow (left out of the silhouette)
# The colours along the stroke (from the short stroke's top): (where the band starts, top index, side index).
RAINBOW = [(0.0, 0x76, 0x74), (0.15, 0x79, 0x77), (0.28, 0x7c, 0x7a), (0.42, 0xca, 0xc7), (0.6, 0x9b, 0x98),
           (0.8, 0x5c, 0x59)]


def line_point(p, q, y):
    """The point on the line through p and q at height y."""
    t = (y - p[1]) / (q[1] - p[1])
    return (p[0] + (q[0] - p[0]) * t, y)


def intersect(p1, d1, p2, d2):
    det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
    t = ((p2[0] - p1[0]) * (-d2[1]) - (p2[1] - p1[1]) * (-d2[0])) / det
    return (p1[0] + d1[0] * t, p1[1] + d1[1] * t)


def tick_outline(grow=0.0):
    """The tick's outline, counter-clockwise: the strokes' edges offset from their middle lines (grown by grow), their
    ends level, their meeting cut level at TICK_BOTTOM (less grow), the corners rounded."""
    (ax, ay), (bx, by), (cx, cy) = TICK
    w1, w2 = TICK_W[0] + grow, TICK_W[1] + grow
    u1 = Vector((bx - ax, by - ay)).normalized()
    u2 = Vector((cx - bx, cy - by)).normalized()
    o1 = Vector((-u1.y, u1.x))           # the short stroke's outer side (to the lower left)
    if o1.x > 0:
        o1 = -o1
    o2 = Vector((u2.y, -u2.x))           # the long stroke's outer side (to the lower right)
    if o2.x < 0:
        o2 = -o2
    a, b, c = Vector((ax, ay)), Vector((bx, by)), Vector((cx, cy))
    top1, top2 = ay + grow, cy + grow
    p1 = line_point(a + o1 * w1, b + o1 * w1, top1)
    corner = intersect(a + o1 * w1, u1, b + o2 * w2, u2)
    p3 = line_point(b + o2 * w2, c + o2 * w2, top2)
    p4 = line_point(b - o2 * w2, c - o2 * w2, top2)
    inner = intersect(a - o1 * w1, u1, b - o2 * w2, u2)
    p6 = line_point(a - o1 * w1, b - o1 * w1, top1)
    poly = ccw([p1, corner, p3, p4, inner, p6])
    # cut level at the bottom (Sutherland-Hodgman against y >= level)
    level = TICK_BOTTOM - grow
    cut = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        pin, qin = p[1] >= level, q[1] >= level
        if pin:
            cut.append(p)
        if pin != qin:
            t = (level - p[1]) / (q[1] - p[1])
            cut.append((p[0] + (q[0] - p[0]) * t, level))
    pts = resample(cut, 0.45)
    pts = chaikin(pts, 2)
    return ccw(pts)


def path_t(x, y):
    """How far along the stroke (0 at the short stroke's top, 1 at the long one's) the nearest point of its middle line
    is."""
    pts = [Vector(p) for p in TICK]
    lengths = [(b - a).length for a, b in zip(pts, pts[1:])]
    total = sum(lengths)
    q = Vector((x, y))
    best, best_t, run = None, 0.0, 0.0
    for (a, b), length in zip(zip(pts, pts[1:]), lengths):
        d = b - a
        u = max(0.0, min(1.0, (q - a).dot(d) / d.length_squared))
        dist = (a + d * u - q).length
        if best is None or dist < best:
            best, best_t = dist, (run + u * length) / total
        run += length
    return best_t


def check_rainbow(opts):
    m = {}
    for i, (_, top, side) in enumerate(RAINBOW):
        m[f"top{i}"] = lit(f"tick_top{i}", top, 0.3, metallic=0.1, roughness=0.18)
        m[f"side{i}"] = lit(f"tick_side{i}", side, 0.18, metallic=0.1, roughness=0.26)
    m["plate"] = lit("tick_plate", 0x01, 0.0, metallic=0.3, roughness=0.2)

    def band_of(x, y):
        t = path_t(x, y)
        i = 0
        for j, (start, _, _) in enumerate(RAINBOW):
            if t >= start:
                i = j
        return i

    def height(x, y, d):
        w = TICK_W[1] if path_t(x, y) > 0.33 else TICK_W[0]
        z = TICK_H + TICK_CROWN * min(1.0, d / w) ** 0.7
        return TICK_BASE + z * round_edge(d, TICK_EDGE)

    def paint(x, y, d):
        return ("side%d" if d < 0.55 else "top%d") % band_of(x, y)

    borders = [((lambda x, y, d: path_t(x, y)), start) for start, _, _ in RAINBOW[1:]]
    borders.append(((lambda x, y, d: d), 0.55))
    stroke = relief("tick", [tick_outline()], height, m, paint=paint, side="side0", bottom=TICK_BASE,
                    spacing=0.42, borders=borders, smooth_angle=55)
    # the sides below the top's rounding: each in its band's side colour
    mk.paint(stroke, lambda c, n: m["side%d" % band_of(c.x, c.y)] if abs(n.z) < 0.3 else None)
    grow, z0, z1 = PLATE

    def plate_h(x, y, d):
        return z0 + (z1 - z0) * round_edge(d, 0.5)
    plate = relief("plate", [tick_outline(grow)], plate_h, m, paint=lambda x, y, d: "plate", side="plate",
                   bottom=z0, spacing=0.6, band=1.5)
    finish(opts, "check_rainbow", [stroke, plate], 245, True, skip=SHADOW, distance=0.6)


# --- Coins 153 (155, 157): the orbiting asteroid killer ----------------------------------------------------------------
ORB_R = (6.05, 6.05, 5.75)
# Its fire: (lowest heat, palette index, emission strength), from the rim to the core.
FIRE = [(-9.0, 0x74, 0.3), (0.22, 0x76, 0.34), (0.4, 0x78, 0.4), (0.58, 0x7a, 0.46), (0.74, 0x7c, 0.52),
        (0.88, 0x7e, 0.6)]
SWIRL = (0.16, 0.55, 2.6)         # the fire's swirl: amount, scale (per pixel), twist (radians over the ball's height)
# The points: their broad ends' middle (|y|), half-width (x), half-thickness (z); their tips' |y|.
POINT_BASE, POINT_W, POINT_T, POINT_TIP = 10.35, 3.95, 1.45, 6.4
FRAME = (0.62, 0.45)              # the dark blue frame behind each point: how much bigger, how much lower
CRYSTAL_BANDS = [(-99, 0xd6), (5.2, 0xd8), (6.0, 0xd9), (6.6, 0xda), (7.1, 0xdb)]


def orbiter(opts):
    m = {f"fire{i}": lit(f"orb_fire{i}", index, glow, roughness=0.3) for i, (_, index, glow) in enumerate(FIRE)}
    for index in (0xd6, 0xd8, 0xd9, 0xda, 0xdb):
        m[index] = lit(f"orb_crystal_{index:02x}", index, 0.16, metallic=0.25, roughness=0.12)
    m["base"] = lit("orb_base", 0x95, 0.14, metallic=0.2, roughness=0.3)

    def heat(p, n):
        tw = SWIRL[2] * (p.z / ORB_R[2])
        x, y = p.x * math.cos(tw) - p.y * math.sin(tw), p.x * math.sin(tw) + p.y * math.cos(tw)
        v = noise.noise(Vector((x * SWIRL[1], y * SWIRL[1], p.z * SWIRL[1] * 0.6 + 3.1)))
        return n.z + SWIRL[0] * v

    keys = tuple(f"fire{i}" for i in range(len(FIRE)))
    ball = painted_ball("ball", Ellipsoid((0.0, 0.0, 0.0), ORB_R), [(heat, tuple(f[0] for f in FIRE[1:]), keys)], m,
                        subdivisions=4, smooth_angle=80)
    parts = [ball]
    for side in (1, -1):
        yb, yt = side * POINT_BASE, side * POINT_TIP
        verts = [(-POINT_W, yb, 0.0), (0.0, yb, POINT_T), (POINT_W, yb, 0.0), (0.0, yb, -POINT_T), (0.0, yt, 0.0)]
        faces = [(0, 1, 2, 3), (0, 4, 1), (1, 4, 2), (2, 4, 3), (3, 4, 0)]
        point = k.mesh_object(f"point{side:+d}", verts, faces, m[0xd9])
        k.recalc_normals(point)
        mk.bevel(point, 0.22, 2, 30)
        mk.paint(point, lambda c, n, yb=yb: m["base"] if abs(c.y) > abs(yb) - 0.05 and abs(n.y) > 0.8 else
                 m[kit_band(light_value(n, 6.2), CRYSTAL_BANDS)])
        parts.append(point)
        # its dark blue frame (the sprite's outline): the same point a little bigger, behind it
        g, dz = FRAME
        yb2, yt2 = side * (POINT_BASE + g), side * (POINT_TIP - g * 0.8)
        fverts = [(-POINT_W - g, yb2, -dz), (0.0, yb2, POINT_T - dz), (POINT_W + g, yb2, -dz),
                  (0.0, yb2, -POINT_T - g - dz), (0.0, yt2, -dz)]
        frame = k.mesh_object(f"frame{side:+d}", fverts, faces, m["base"])
        k.recalc_normals(frame)
        k.smooth(frame, 30)
        parts.append(frame)
    obj = finish(opts, "orbiter", parts, 155, True, distance=0.6)
    if "check" in opts:   # 153's pose: the points turned 45 degrees clockwise
        kit.check(opts, "orbiter turned 45 cw (coins 153)", [obj], 153, True, turn=-45.0)


def kit_band(value, bands):
    key = bands[0][1]
    for lowest, k_ in bands:
        if value >= lowest:
            key = k_
    return key


# --- Build -------------------------------------------------------------------------------------------------------------
MODELS = [
    ("strawberry", strawberry),
    ("fruit_round", lambda opts: citrus(opts, "fruit_round")),
    ("fruit_orange", lambda opts: citrus(opts, "fruit_orange")),
    ("grapes_green", lambda opts: grapes(opts, "grapes_green")),
    ("grapes_purple", lambda opts: grapes(opts, "grapes_purple")),
    ("check_rainbow", check_rainbow),
    ("orbiter", orbiter),
]


def build():
    opts = kit.options()
    for name, make in MODELS:
        if not kit.wanted(opts, name):
            continue
        k.reset()
        make(opts)


if __name__ == "__main__":
    build()
